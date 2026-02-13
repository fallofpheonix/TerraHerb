package http

import (
	"encoding/json"
	"errors"
	"net/http"
	"strconv"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"terraherbarium/backend/internal/config"
	"terraherbarium/backend/internal/models"
	"terraherbarium/backend/internal/observability"
	"terraherbarium/backend/internal/service"
)

type Handler struct {
	cfg          config.Config
	plantService *service.PlantService
	authService  *service.AuthService
}

func NewRouter(cfg config.Config, plantService *service.PlantService, authService *service.AuthService) http.Handler {
	h := &Handler{
		cfg:          cfg,
		plantService: plantService,
		authService:  authService,
	}
	logger := observability.NewLogger()
	metrics := observability.NewMetrics()

	r := chi.NewRouter()
	r.Use(middleware.RequestID)
	r.Use(middleware.RealIP)
	r.Use(middleware.Recoverer)
	r.Use(observability.RequestIDPropagationMiddleware)
	r.Use(observability.RequestLoggingMiddleware(logger))
	r.Use(metrics.Middleware)
	r.Use(rateLimitMiddleware(plantService.Cache(), cfg.RateLimitPerMin))

	r.Get("/health", h.health)
	r.Get("/metrics", metrics.Handler)

	r.Route("/api/v1", func(api chi.Router) {
		api.Post("/auth/login", h.login)
		api.Post("/auth/refresh", h.refresh)
		api.Post("/auth/logout", h.logout)

		api.With(authMiddleware(cfg.JWTSigningKey, false)).Get("/plants", h.searchPlants)
		api.With(authMiddleware(cfg.JWTSigningKey, false)).Get("/plants/by-season", h.searchBySeason)
		api.With(authMiddleware(cfg.JWTSigningKey, false)).Get("/plants/by-climate-zone", h.searchByClimate)
		api.With(authMiddleware(cfg.JWTSigningKey, false)).Get("/plants/{id}", h.getPlantByID)
	})

	return r
}

func (h *Handler) health(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, map[string]string{"status": "ok"})
}

func (h *Handler) login(w http.ResponseWriter, r *http.Request) {
	var req models.AuthLoginRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(r, w, http.StatusBadRequest, "VALIDATION_ERROR", "invalid JSON payload")
		return
	}

	resp, err := h.authService.LoginDevOTP(r.Context(), req)
	if err != nil {
		if errors.Is(err, service.ErrInvalidCredentials) {
			writeError(r, w, http.StatusUnauthorized, "UNAUTHORIZED", "invalid credentials")
			return
		}
		writeError(r, w, http.StatusInternalServerError, "INTERNAL_ERROR", "failed to issue token")
		return
	}
	writeJSON(w, http.StatusOK, resp)
}

func (h *Handler) refresh(w http.ResponseWriter, r *http.Request) {
	var req models.AuthRefreshRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(r, w, http.StatusBadRequest, "VALIDATION_ERROR", "invalid JSON payload")
		return
	}
	if req.RefreshToken == "" {
		writeError(r, w, http.StatusBadRequest, "VALIDATION_ERROR", "refresh_token is required")
		return
	}

	resp, err := h.authService.Refresh(r.Context(), req)
	if err != nil {
		switch {
		case errors.Is(err, service.ErrInvalidToken), errors.Is(err, service.ErrInvalidDevice):
			writeError(r, w, http.StatusUnauthorized, "UNAUTHORIZED", "invalid refresh token")
		default:
			writeError(r, w, http.StatusInternalServerError, "INTERNAL_ERROR", "failed to refresh token")
		}
		return
	}
	writeJSON(w, http.StatusOK, resp)
}

func (h *Handler) logout(w http.ResponseWriter, r *http.Request) {
	var req models.AuthLogoutRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(r, w, http.StatusBadRequest, "VALIDATION_ERROR", "invalid JSON payload")
		return
	}
	if req.RefreshToken == "" {
		writeError(r, w, http.StatusBadRequest, "VALIDATION_ERROR", "refresh_token is required")
		return
	}
	if err := h.authService.Logout(r.Context(), req.RefreshToken); err != nil {
		if errors.Is(err, service.ErrInvalidToken) {
			writeError(r, w, http.StatusUnauthorized, "UNAUTHORIZED", "invalid refresh token")
			return
		}
		writeError(r, w, http.StatusInternalServerError, "INTERNAL_ERROR", "logout failed")
		return
	}
	writeJSON(w, http.StatusOK, map[string]string{"status": "logged_out"})
}

func (h *Handler) searchPlants(w http.ResponseWriter, r *http.Request) {
	params, err := parseSearchParams(r)
	if err != nil {
		writeError(r, w, http.StatusBadRequest, "VALIDATION_ERROR", err.Error())
		return
	}
	resp, err := h.plantService.SearchPlants(r.Context(), params)
	if err != nil {
		writeError(r, w, http.StatusInternalServerError, "INTERNAL_ERROR", err.Error())
		return
	}
	writeJSON(w, http.StatusOK, resp)
}

func (h *Handler) searchBySeason(w http.ResponseWriter, r *http.Request) {
	params, err := parseSearchParams(r)
	if err != nil {
		writeError(r, w, http.StatusBadRequest, "VALIDATION_ERROR", err.Error())
		return
	}
	params.Season = r.URL.Query().Get("season")
	if params.Season == "" {
		writeError(r, w, http.StatusBadRequest, "VALIDATION_ERROR", "season is required")
		return
	}
	resp, err := h.plantService.SearchPlants(r.Context(), params)
	if err != nil {
		writeError(r, w, http.StatusInternalServerError, "INTERNAL_ERROR", err.Error())
		return
	}
	writeJSON(w, http.StatusOK, resp)
}

func (h *Handler) searchByClimate(w http.ResponseWriter, r *http.Request) {
	params, err := parseSearchParams(r)
	if err != nil {
		writeError(r, w, http.StatusBadRequest, "VALIDATION_ERROR", err.Error())
		return
	}
	params.ClimateZone = r.URL.Query().Get("climate_zone")
	if params.ClimateZone == "" {
		writeError(r, w, http.StatusBadRequest, "VALIDATION_ERROR", "climate_zone is required")
		return
	}
	resp, err := h.plantService.SearchPlants(r.Context(), params)
	if err != nil {
		writeError(r, w, http.StatusInternalServerError, "INTERNAL_ERROR", err.Error())
		return
	}
	writeJSON(w, http.StatusOK, resp)
}

func (h *Handler) getPlantByID(w http.ResponseWriter, r *http.Request) {
	id, err := strconv.ParseInt(chi.URLParam(r, "id"), 10, 64)
	if err != nil {
		writeError(r, w, http.StatusBadRequest, "VALIDATION_ERROR", "id must be an integer")
		return
	}
	plant, err := h.plantService.GetPlantByID(r.Context(), id)
	if err != nil {
		writeError(r, w, http.StatusNotFound, "NOT_FOUND", "plant not found")
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"data": plant})
}

func parseSearchParams(r *http.Request) (models.PlantSearchParams, error) {
	q := r.URL.Query()
	params := models.PlantSearchParams{
		Query:       q.Get("q"),
		Season:      q.Get("season"),
		ClimateZone: q.Get("climate_zone"),
		RegionCode:  q.Get("region_code"),
		Month:       0,
		PlantType:   q.Get("plant_type"),
		Lifecycle:   q.Get("lifecycle"),
		Page:        1,
		Limit:       20,
	}
	if params.Season != "" && !isAllowed(params.Season, "spring", "summer", "monsoon", "autumn", "winter", "year_round", "kharif", "rabi", "zaid") {
		return models.PlantSearchParams{}, errors.New("season has unsupported value")
	}
	if params.PlantType != "" && !isAllowed(params.PlantType, "herb", "crop", "tree", "weed", "shrub", "climber") {
		return models.PlantSearchParams{}, errors.New("plant_type has unsupported value")
	}
	if params.Lifecycle != "" && !isAllowed(params.Lifecycle, "annual", "biennial", "perennial") {
		return models.PlantSearchParams{}, errors.New("lifecycle has unsupported value")
	}
	month, err := parseIntInRange(q.Get("month"), "month", 1, 12, true)
	if err != nil {
		return models.PlantSearchParams{}, err
	}
	params.Month = month
	page, err := parseIntInRange(q.Get("page"), "page", 1, 1000000, true)
	if err != nil {
		return models.PlantSearchParams{}, err
	}
	params.Page = page
	limit, err := parseIntInRange(q.Get("limit"), "limit", 1, 100, true)
	if err != nil {
		return models.PlantSearchParams{}, err
	}
	params.Limit = limit
	return params, nil
}

func parseIntInRange(v, field string, min, max int, optional bool) (int, error) {
	if v == "" {
		if optional {
			switch field {
			case "page":
				return 1, nil
			case "limit":
				return 20, nil
			default:
				return 0, nil
			}
		}
		return 0, errors.New(field + " is required")
	}
	i, err := strconv.Atoi(v)
	if err != nil {
		return 0, errors.New(field + " must be an integer")
	}
	if i < min || i > max {
		return 0, errors.New(field + " must be between " + strconv.Itoa(min) + " and " + strconv.Itoa(max))
	}
	return i, nil
}

func isAllowed(value string, allowed ...string) bool {
	for _, candidate := range allowed {
		if value == candidate {
			return true
		}
	}
	return false
}

func writeJSON(w http.ResponseWriter, status int, payload any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(payload)
}

func writeError(r *http.Request, w http.ResponseWriter, status int, code, message string) {
	writeJSON(w, status, map[string]any{
		"error": map[string]string{
			"code":       code,
			"message":    message,
			"request_id": middleware.GetReqID(r.Context()),
		},
	})
}
