package http

import (
	"net"
	"net/http"
	"strings"
	"time"

	"terraherbarium/backend/internal/auth"
	"terraherbarium/backend/internal/cache"
)

func authMiddleware(jwtKey string, required bool) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			token, hasHeader, ok := parseBearerToken(r.Header.Get("Authorization"))
			if !hasHeader {
				if required {
					writeError(r, w, http.StatusUnauthorized, "UNAUTHORIZED", "missing authorization header")
					return
				}
				next.ServeHTTP(w, r)
				return
			}
			if !ok {
				writeError(r, w, http.StatusUnauthorized, "UNAUTHORIZED", "invalid bearer token")
				return
			}
			if _, err := auth.ParseToken(token, jwtKey); err != nil {
				writeError(r, w, http.StatusUnauthorized, "UNAUTHORIZED", "invalid token")
				return
			}
			next.ServeHTTP(w, r)
		})
	}
}

func rateLimitMiddleware(c *cache.RedisClient, perMinute int) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			ip := clientIP(r)
			key := "rl:v1:" + ip + ":" + r.URL.Path
			count, err := c.IncrWithTTL(r.Context(), key, time.Minute)
			if err == nil && count > int64(perMinute) {
				w.Header().Set("Retry-After", "60")
				writeError(r, w, http.StatusTooManyRequests, "RATE_LIMITED", "too many requests")
				return
			}
			next.ServeHTTP(w, r)
		})
	}
}

func parseBearerToken(header string) (string, bool, bool) {
	header = strings.TrimSpace(header)
	if header == "" {
		return "", false, false
	}
	parts := strings.Fields(header)
	if len(parts) != 2 || !strings.EqualFold(parts[0], "Bearer") || strings.TrimSpace(parts[1]) == "" {
		return "", true, false
	}
	return parts[1], true, true
}

func clientIP(r *http.Request) string {
	xff := strings.TrimSpace(r.Header.Get("X-Forwarded-For"))
	if xff != "" {
		if idx := strings.IndexByte(xff, ','); idx >= 0 {
			return strings.TrimSpace(xff[:idx])
		}
		return xff
	}
	if xrip := strings.TrimSpace(r.Header.Get("X-Real-IP")); xrip != "" {
		return xrip
	}
	host, _, err := net.SplitHostPort(r.RemoteAddr)
	if err == nil && host != "" {
		return host
	}
	return r.RemoteAddr
}
