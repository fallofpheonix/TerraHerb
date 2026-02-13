package auth

import (
	"crypto/rand"
	"encoding/hex"
	"errors"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

type Claims struct {
	Role  string `json:"role"`
	Scope string `json:"scope"`
	jwt.RegisteredClaims
}

func GenerateToken(userID, role, scope, key string) (string, error) {
	return GenerateTokenWithTTL(userID, role, scope, key, 15*time.Minute)
}

func GenerateTokenWithTTL(userID, role, scope, key string, ttl time.Duration) (string, error) {
	now := time.Now()
	jti, err := generateTokenID()
	if err != nil {
		return "", err
	}
	claims := Claims{
		Role:  role,
		Scope: scope,
		RegisteredClaims: jwt.RegisteredClaims{
			Subject:   userID,
			ID:        jti,
			IssuedAt:  jwt.NewNumericDate(now),
			ExpiresAt: jwt.NewNumericDate(now.Add(ttl)),
		},
	}
	t := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return t.SignedString([]byte(key))
}

func ParseToken(tokenString, key string) (*Claims, error) {
	token, err := jwt.ParseWithClaims(tokenString, &Claims{}, func(t *jwt.Token) (any, error) {
		if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, errors.New("unexpected signing method")
		}
		return []byte(key), nil
	})
	if err != nil {
		return nil, err
	}
	claims, ok := token.Claims.(*Claims)
	if !ok || !token.Valid {
		return nil, errors.New("invalid token")
	}
	return claims, nil
}

func generateTokenID() (string, error) {
	raw := make([]byte, 16)
	if _, err := rand.Read(raw); err != nil {
		return "", err
	}
	return hex.EncodeToString(raw), nil
}
