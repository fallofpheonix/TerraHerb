package observability

import (
	"fmt"
	"net/http"
	"sort"
	"strings"
	"sync"
	"time"
)

type Metrics struct {
	mu             sync.Mutex
	requestTotal   map[string]uint64
	latencyCount   map[string]uint64
	latencyMsTotal map[string]float64
}

func NewMetrics() *Metrics {
	return &Metrics{
		requestTotal:   make(map[string]uint64),
		latencyCount:   make(map[string]uint64),
		latencyMsTotal: make(map[string]float64),
	}
}

func (m *Metrics) Middleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		rw := &statusRecorder{ResponseWriter: w, status: http.StatusOK}
		next.ServeHTTP(rw, r)

		key := labelKey(r.Method, r.URL.Path, rw.status)
		latencyKey := fmt.Sprintf("%s|%s", r.Method, r.URL.Path)
		latencyMs := float64(time.Since(start).Milliseconds())

		m.mu.Lock()
		m.requestTotal[key]++
		m.latencyCount[latencyKey]++
		m.latencyMsTotal[latencyKey] += latencyMs
		m.mu.Unlock()
	})
}

func (m *Metrics) Handler(w http.ResponseWriter, _ *http.Request) {
	m.mu.Lock()
	defer m.mu.Unlock()

	w.Header().Set("Content-Type", "text/plain; version=0.0.4")

	lines := make([]string, 0, len(m.requestTotal)+len(m.latencyCount)+4)
	lines = append(lines,
		"# HELP terraherb_http_requests_total Total HTTP requests.",
		"# TYPE terraherb_http_requests_total counter",
	)

	requestKeys := sortedKeys(m.requestTotal)
	for _, k := range requestKeys {
		method, path, status := splitRequestKey(k)
		lines = append(lines, fmt.Sprintf("terraherb_http_requests_total{method=%q,path=%q,status=%q} %d",
			method, path, status, m.requestTotal[k]))
	}

	lines = append(lines,
		"# HELP terraherb_http_request_duration_ms_sum Sum of request latencies in milliseconds.",
		"# TYPE terraherb_http_request_duration_ms_sum counter",
	)
	latencyKeys := sortedKeysFloat(m.latencyMsTotal)
	for _, k := range latencyKeys {
		method, path := splitLatencyKey(k)
		lines = append(lines, fmt.Sprintf("terraherb_http_request_duration_ms_sum{method=%q,path=%q} %.3f",
			method, path, m.latencyMsTotal[k]))
	}

	lines = append(lines,
		"# HELP terraherb_http_request_duration_ms_count Count of requests observed for latency.",
		"# TYPE terraherb_http_request_duration_ms_count counter",
	)
	countKeys := sortedKeys(m.latencyCount)
	for _, k := range countKeys {
		method, path := splitLatencyKey(k)
		lines = append(lines, fmt.Sprintf("terraherb_http_request_duration_ms_count{method=%q,path=%q} %d",
			method, path, m.latencyCount[k]))
	}

	_, _ = w.Write([]byte(strings.Join(lines, "\n") + "\n"))
}

func labelKey(method, path string, status int) string {
	return fmt.Sprintf("%s|%s|%d", method, path, status)
}

func splitRequestKey(key string) (string, string, string) {
	parts := strings.SplitN(key, "|", 3)
	if len(parts) != 3 {
		return "UNKNOWN", "UNKNOWN", "0"
	}
	return parts[0], parts[1], parts[2]
}

func splitLatencyKey(key string) (string, string) {
	parts := strings.SplitN(key, "|", 2)
	if len(parts) != 2 {
		return "UNKNOWN", "UNKNOWN"
	}
	return parts[0], parts[1]
}

func sortedKeys(m map[string]uint64) []string {
	keys := make([]string, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	return keys
}

func sortedKeysFloat(m map[string]float64) []string {
	keys := make([]string, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	return keys
}
