package repository

import (
	"context"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"terraherbarium/backend/internal/models"
)

type AuthRepository struct {
	pool *pgxpool.Pool
}

func NewAuthRepository(pool *pgxpool.Pool) *AuthRepository {
	return &AuthRepository{pool: pool}
}

func (r *AuthRepository) UpsertDevUser(ctx context.Context, identifier string) (*models.AuthUser, error) {
	const q = `
		INSERT INTO users (identifier, role)
		VALUES ($1, 'farmer')
		ON CONFLICT (identifier)
		DO UPDATE SET updated_at = now()
		RETURNING id, identifier, role
	`
	var user models.AuthUser
	if err := r.pool.QueryRow(ctx, q, identifier).Scan(&user.ID, &user.Identifier, &user.Role); err != nil {
		return nil, err
	}
	return &user, nil
}

func (r *AuthRepository) CreateRefreshToken(ctx context.Context, userID int64, tokenHash, deviceID string, expiresAt time.Time) error {
	const q = `
		INSERT INTO refresh_tokens (user_id, token_hash, device_id, expires_at)
		VALUES ($1, $2, NULLIF($3, ''), $4)
	`
	_, err := r.pool.Exec(ctx, q, userID, tokenHash, deviceID, expiresAt)
	return err
}

func (r *AuthRepository) GetValidRefreshToken(ctx context.Context, tokenHash string) (*models.RefreshTokenRecord, error) {
	const q = `
		SELECT rt.id, rt.user_id, rt.token_hash, rt.device_id, rt.expires_at, rt.revoked_at, u.role
		FROM refresh_tokens rt
		JOIN users u ON u.id = rt.user_id
		WHERE rt.token_hash = $1
		  AND rt.revoked_at IS NULL
		  AND rt.expires_at > now()
	`
	var row models.RefreshTokenRecord
	if err := r.pool.QueryRow(ctx, q, tokenHash).Scan(
		&row.ID, &row.UserID, &row.TokenHash, &row.DeviceID, &row.ExpiresAt, &row.RevokedAt, &row.UserRole,
	); err != nil {
		return nil, err
	}
	return &row, nil
}

func (r *AuthRepository) RevokeRefreshTokenByHash(ctx context.Context, tokenHash string) error {
	const q = `
		UPDATE refresh_tokens
		SET revoked_at = now()
		WHERE token_hash = $1
		  AND revoked_at IS NULL
	`
	_, err := r.pool.Exec(ctx, q, tokenHash)
	return err
}
