package http

import (
	"net/http/httptest"
	"testing"
)

func TestParseSearchParamsDefaults(t *testing.T) {
	req := httptest.NewRequest("GET", "/api/v1/plants", nil)

	params, err := parseSearchParams(req)
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}
	if params.Page != 1 {
		t.Fatalf("expected page=1, got %d", params.Page)
	}
	if params.Limit != 20 {
		t.Fatalf("expected limit=20, got %d", params.Limit)
	}
	if params.Month != 0 {
		t.Fatalf("expected month=0, got %d", params.Month)
	}
}

func TestParseSearchParamsValidation(t *testing.T) {
	tests := []struct {
		name string
		url  string
	}{
		{name: "invalid month", url: "/api/v1/plants?month=13"},
		{name: "invalid page", url: "/api/v1/plants?page=0"},
		{name: "invalid limit", url: "/api/v1/plants?limit=101"},
		{name: "invalid season enum", url: "/api/v1/plants?season=rainy"},
		{name: "invalid plant type enum", url: "/api/v1/plants?plant_type=flower"},
		{name: "invalid lifecycle enum", url: "/api/v1/plants?lifecycle=monthly"},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			req := httptest.NewRequest("GET", tc.url, nil)
			if _, err := parseSearchParams(req); err == nil {
				t.Fatalf("expected validation error for %s", tc.url)
			}
		})
	}
}
