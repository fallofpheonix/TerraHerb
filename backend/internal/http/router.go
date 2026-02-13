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
	"terraherbarium/backend/internal/service"
)

type Handler struct {
	plantService *service.PlantService
}

func NewRouter(cfg config.Config, plantService *service.PlantService) http.Handler {
	h := &Handler{plantService: plantService}
	r := chi.NewRouter()
	r.Use(middleware.RequestID)
	r.Use(middleware.RealIP)
	r.Use(middleware.Recoverer)
	r.Use(middleware.Logger)
	r.Use(rateLimitMiddleware(plantService.Cache(), cfg.RateLimitPerMin))

	r.Get("/health", h.health)

	r.Route("/api/v1", func(api chi.Router) {
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

func (h *Handler) searchPlants(w http.ResponseWriter, r *http.Request) {
	params, err := parseSearchParams(r)
	if err != nil {
		writeError(w, http.StatusBadRequest, "VALIDATION_ERROR", err.Error())
		return
	}
	resp, err := h.plantService.SearchPlants(r.Context(), params)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "INTERNAL_ERROR", err.Error())
		return
	}
	writeJSON(w, http.StatusOK, resp)
}

func (h *Handler) searchBySeason(w http.ResponseWriter, r *http.Request) {
	params, err := parseSearchParams(r)
	if err != nil {
		writeError(w, http.StatusBadRequest, "VALIDATION_ERROR", err.Error())
		return
	}
	params.Season = r.URL.Query().Get("season")
	if params.Season == "" {
		writeError(w, http.StatusBadRequest, "VALIDATION_ERROR", "season is required")
		return
	}
	resp, err := h.plantService.SearchPlants(r.Context(), params)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "INTERNAL_ERROR", err.Error())
		return
	}
	writeJSON(w, http.StatusOK, resp)
}

func (h *Handler) searchByClimate(w http.ResponseWriter, r *http.Request) {
	params, err := parseSearchParams(r)
	if err != nil {
		writeError(w, http.StatusBadRequest, "VALIDATION_ERROR", err.Error())
		return
	}
	params.ClimateZone = r.URL.Query().Get("climate_zone")
	if params.ClimateZone == "" {
		writeError(w, http.StatusBadRequest, "VALIDATION_ERROR", "climate_zone is required")
		return
	}
	resp, err := h.plantService.SearchPlants(r.Context(), params)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "INTERNAL_ERROR", err.Error())
		return
	}
	writeJSON(w, http.StatusOK, resp)
}

func (h *Handler) getPlantByID(w http.ResponseWriter, r *http.Request) {
	id, err := strconv.ParseInt(chi.URLParam(r, "id"), 10, 64)
	if err != nil {
		writeError(w, http.StatusBadRequest, "VALIDATION_ERROR", "id must be an integer")
		return
	}
	plant, err := h.plantService.GetPlantByID(r.Context(), id)
	if err != nil {
		writeError(w, http.StatusNotFound, "NOT_FOUND", "plant not found")
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

func writeError(w http.ResponseWriter, status int, code, message string) {
	writeJSON(w, status, map[string]any{
		"error": map[string]string{
			"code":    code,
			"message": message,
		},
	})
}
