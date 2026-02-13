package config

import (
	"fmt"
	"os"
)

type Config struct {
	HTTPAddr       string
	DatabaseURL    string
	RedisAddr      string
	RedisPassword  string
	JWTSigningKey  string
	RateLimitPerMin int
}

func Load() Config {
	return Config{
		HTTPAddr:        getenv("HTTP_ADDR", ":8080"),
		DatabaseURL:     getenv("DATABASE_URL", "postgres://postgres:postgres@localhost:5432/terraherb?sslmode=disable"),
		RedisAddr:       getenv("REDIS_ADDR", "localhost:6379"),
		RedisPassword:   os.Getenv("REDIS_PASSWORD"),
		JWTSigningKey:   getenv("JWT_SIGNING_KEY", "change-me-in-prod"),
		RateLimitPerMin: getenvInt("RATE_LIMIT_PER_MIN", 120),
	}
}

func getenv(key, fallback string) string {
	if value, ok := os.LookupEnv(key); ok && value != "" {
		return value
	}
	return fallback
}

func getenvInt(key string, fallback int) int {
	v := os.Getenv(key)
	if v == "" {
		return fallback
	}
	var out int
	_, err := fmt.Sscanf(v, "%d", &out)
	if err != nil {
		return fallback
	}
	return out
}
