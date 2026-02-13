package models

import "time"

type AuthLoginRequest struct {
	Identifier string `json:"identifier"`
	OTP        string `json:"otp"`
	DeviceID   string `json:"device_id"`
}

type AuthRefreshRequest struct {
	RefreshToken string `json:"refresh_token"`
	DeviceID     string `json:"device_id"`
}

type AuthLogoutRequest struct {
	RefreshToken string `json:"refresh_token"`
}

type AuthResponse struct {
	AccessToken      string `json:"access_token"`
	RefreshToken     string `json:"refresh_token"`
	TokenType        string `json:"token_type"`
	AccessExpiresIn  int64  `json:"access_expires_in"`
	RefreshExpiresIn int64  `json:"refresh_expires_in"`
}

type AuthUser struct {
	ID         int64
	Identifier string
	Role       string
}

type RefreshTokenRecord struct {
	ID        int64
	UserID    int64
	TokenHash string
	DeviceID  *string
	ExpiresAt time.Time
	RevokedAt *time.Time
	UserRole  string
}
