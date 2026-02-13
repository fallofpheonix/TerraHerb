package service

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"strconv"
	"strings"
	"time"

	"github.com/jackc/pgx/v5"
	"terraherbarium/backend/internal/auth"
	"terraherbarium/backend/internal/config"
	"terraherbarium/backend/internal/models"
	"terraherbarium/backend/internal/repository"
)

var (
	ErrInvalidCredentials = errors.New("invalid credentials")
	ErrInvalidToken       = errors.New("invalid token")
	ErrInvalidDevice      = errors.New("invalid device")
)

type AuthService struct {
	cfg  config.Config
	repo *repository.AuthRepository
}

func NewAuthService(cfg config.Config, repo *repository.AuthRepository) *AuthService {
	return &AuthService{cfg: cfg, repo: repo}
}

func (s *AuthService) LoginDevOTP(ctx context.Context, req models.AuthLoginRequest) (*models.AuthResponse, error) {
	if strings.TrimSpace(req.Identifier) == "" || strings.TrimSpace(req.OTP) == "" {
		return nil, ErrInvalidCredentials
	}
	if req.OTP != s.cfg.AuthDevOTP {
		return nil, ErrInvalidCredentials
	}

	user, err := s.repo.UpsertDevUser(ctx, req.Identifier)
	if err != nil {
		return nil, err
	}
	return s.issueTokenPair(ctx, user, req.DeviceID)
}

func (s *AuthService) Refresh(ctx context.Context, req models.AuthRefreshRequest) (*models.AuthResponse, error) {
	claims, err := auth.ParseToken(req.RefreshToken, s.cfg.JWTSigningKey)
	if err != nil || claims.Scope != "refresh" || claims.Subject == "" {
		return nil, ErrInvalidToken
	}
	hash := hashToken(req.RefreshToken)
	row, err := s.repo.GetValidRefreshToken(ctx, hash)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			return nil, ErrInvalidToken
		}
		return nil, err
	}
	if row.DeviceID != nil && req.DeviceID != "" && *row.DeviceID != req.DeviceID {
		return nil, ErrInvalidDevice
	}
	if err := s.repo.RevokeRefreshTokenByHash(ctx, hash); err != nil {
		return nil, err
	}

	user := &models.AuthUser{
		ID:         row.UserID,
		Identifier: claims.Subject,
		Role:       row.UserRole,
	}
	return s.issueTokenPair(ctx, user, req.DeviceID)
}

func (s *AuthService) Logout(ctx context.Context, refreshToken string) error {
	if strings.TrimSpace(refreshToken) == "" {
		return ErrInvalidToken
	}
	if _, err := auth.ParseToken(refreshToken, s.cfg.JWTSigningKey); err != nil {
		return ErrInvalidToken
	}
	return s.repo.RevokeRefreshTokenByHash(ctx, hashToken(refreshToken))
}

func (s *AuthService) issueTokenPair(ctx context.Context, user *models.AuthUser, deviceID string) (*models.AuthResponse, error) {
	accessTTL := time.Duration(s.cfg.AccessTokenMins) * time.Minute
	refreshTTL := time.Duration(s.cfg.RefreshTokenHrs) * time.Hour
	subject := user.Identifier
	if subject == "" {
		subject = strconv.FormatInt(user.ID, 10)
	}

	accessToken, err := auth.GenerateTokenWithTTL(subject, user.Role, "access", s.cfg.JWTSigningKey, accessTTL)
	if err != nil {
		return nil, err
	}
	refreshToken, err := auth.GenerateTokenWithTTL(subject, user.Role, "refresh", s.cfg.JWTSigningKey, refreshTTL)
	if err != nil {
		return nil, err
	}
	if err := s.repo.CreateRefreshToken(ctx, user.ID, hashToken(refreshToken), deviceID, time.Now().Add(refreshTTL)); err != nil {
		return nil, err
	}

	return &models.AuthResponse{
		AccessToken:      accessToken,
		RefreshToken:     refreshToken,
		TokenType:        "Bearer",
		AccessExpiresIn:  int64(accessTTL.Seconds()),
		RefreshExpiresIn: int64(refreshTTL.Seconds()),
	}, nil
}

func hashToken(raw string) string {
	sum := sha256.Sum256([]byte(raw))
	return hex.EncodeToString(sum[:])
}
