package http

import (
	"encoding/json"
	"log"
	"net/http"
	"strconv"
	"sync"
	"sync/atomic"
	"time"

	"github.com/go-chi/chi/v5/middleware"
)

type Observability struct {
	totalRequests atomic.Uint64
	totalErrors   atomic.Uint64
	mu            sync.Mutex
	byRoute       map[string]uint64
}

func NewObservability() *Observability {
	return &Observability{
		byRoute: make(map[string]uint64),
	}
}

func (o *Observability) Middleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		o.totalRequests.Add(1)

		rw := &statusRecorder{ResponseWriter: w, status: http.StatusOK}
		next.ServeHTTP(rw, r)

		duration := time.Since(start)
		if rw.status >= 500 {
			o.totalErrors.Add(1)
		}
		routeKey := r.Method + " " + r.URL.Path + " " + strconv.Itoa(rw.status)
		o.mu.Lock()
		o.byRoute[routeKey]++
		o.mu.Unlock()

		entry := map[string]any{
			"ts":          time.Now().UTC().Format(time.RFC3339Nano),
			"request_id":  middleware.GetReqID(r.Context()),
			"method":      r.Method,
			"path":        r.URL.Path,
			"status":      rw.status,
			"duration_ms": duration.Milliseconds(),
			"remote_ip":   r.RemoteAddr,
		}
		b, _ := json.Marshal(entry)
		log.Printf("%s", b)
	})
}

func (o *Observability) MetricsHandler(w http.ResponseWriter, _ *http.Request) {
	o.mu.Lock()
	byRoute := make(map[string]uint64, len(o.byRoute))
	for k, v := range o.byRoute {
		byRoute[k] = v
	}
	o.mu.Unlock()

	payload := map[string]any{
		"requests_total": o.totalRequests.Load(),
		"errors_total":   o.totalErrors.Load(),
		"by_route":       byRoute,
	}
	writeJSON(w, http.StatusOK, payload)
}

type statusRecorder struct {
	http.ResponseWriter
	status int
}

func (r *statusRecorder) WriteHeader(statusCode int) {
	r.status = statusCode
	r.ResponseWriter.WriteHeader(statusCode)
}
