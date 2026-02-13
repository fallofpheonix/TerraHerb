package http

import (
	"net/http/httptest"
	"testing"
)

func TestParseBearerToken(t *testing.T) {
	tests := []struct {
		name        string
		header      string
		wantToken   string
		wantPresent bool
		wantOK      bool
	}{
		{name: "missing", header: "", wantToken: "", wantPresent: false, wantOK: false},
		{name: "valid", header: "Bearer abc123", wantToken: "abc123", wantPresent: true, wantOK: true},
		{name: "lowercase scheme", header: "bearer zyx", wantToken: "zyx", wantPresent: true, wantOK: true},
		{name: "invalid scheme", header: "Token abc", wantToken: "", wantPresent: true, wantOK: false},
		{name: "missing token", header: "Bearer", wantToken: "", wantPresent: true, wantOK: false},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			token, present, ok := parseBearerToken(tc.header)
			if token != tc.wantToken || present != tc.wantPresent || ok != tc.wantOK {
				t.Fatalf("got token=%q present=%v ok=%v", token, present, ok)
			}
		})
	}
}

func TestClientIP(t *testing.T) {
	req := httptest.NewRequest("GET", "/health", nil)
	req.RemoteAddr = "10.0.0.8:12345"
	if got := clientIP(req); got != "10.0.0.8" {
		t.Fatalf("expected parsed remote addr host, got %q", got)
	}

	req = httptest.NewRequest("GET", "/health", nil)
	req.RemoteAddr = "10.0.0.8:12345"
	req.Header.Set("X-Real-IP", "203.0.113.10")
	if got := clientIP(req); got != "203.0.113.10" {
		t.Fatalf("expected x-real-ip, got %q", got)
	}

	req = httptest.NewRequest("GET", "/health", nil)
	req.RemoteAddr = "10.0.0.8:12345"
	req.Header.Set("X-Forwarded-For", "198.51.100.5, 10.0.0.8")
	if got := clientIP(req); got != "198.51.100.5" {
		t.Fatalf("expected first x-forwarded-for value, got %q", got)
	}
}
