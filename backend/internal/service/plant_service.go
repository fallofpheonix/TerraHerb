package service

import (
	"context"
	"crypto/sha1"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"time"

	"terraherbarium/backend/internal/cache"
	"terraherbarium/backend/internal/models"
	"terraherbarium/backend/internal/repository"
)

type PlantService struct {
	repo  *repository.PlantRepository
	cache *cache.RedisClient
}

type PlantListResponse struct {
	Meta struct {
		Page    int  `json:"page"`
		Limit   int  `json:"limit"`
		Total   int  `json:"total"`
		HasNext bool `json:"has_next"`
	} `json:"meta"`
	Data []models.Plant `json:"data"`
}

func NewPlantService(repo *repository.PlantRepository, cache *cache.RedisClient) *PlantService {
	return &PlantService{repo: repo, cache: cache}
}

func (s *PlantService) SearchPlants(ctx context.Context, params models.PlantSearchParams) (*PlantListResponse, error) {
	cacheKey := s.listCacheKey(params)
	if payload, err := s.cache.Get(ctx, cacheKey); err == nil {
		var cached PlantListResponse
		if unmarshalErr := json.Unmarshal([]byte(payload), &cached); unmarshalErr == nil {
			return &cached, nil
		}
	}

	plants, total, err := s.repo.SearchPlants(ctx, params)
	if err != nil {
		return nil, err
	}

	resp := &PlantListResponse{Data: plants}
	if params.Page <= 0 {
		params.Page = 1
	}
	if params.Limit <= 0 {
		params.Limit = 20
	}
	resp.Meta.Page = params.Page
	resp.Meta.Limit = params.Limit
	resp.Meta.Total = total
	resp.Meta.HasNext = params.Page*params.Limit < total

	if b, err := json.Marshal(resp); err == nil {
		_ = s.cache.Set(ctx, cacheKey, string(b), 10*time.Minute)
	}

	return resp, nil
}

func (s *PlantService) GetPlantByID(ctx context.Context, id int64) (*models.PlantDetail, error) {
	cacheKey := fmt.Sprintf("plant:v1:profile:%d", id)
	if payload, err := s.cache.Get(ctx, cacheKey); err == nil {
		var cached models.PlantDetail
		if unmarshalErr := json.Unmarshal([]byte(payload), &cached); unmarshalErr == nil {
			return &cached, nil
		}
	}

	plant, err := s.repo.GetPlantByID(ctx, id)
	if err != nil {
		return nil, err
	}
	if b, err := json.Marshal(plant); err == nil {
		_ = s.cache.Set(ctx, cacheKey, string(b), 24*time.Hour)
	}
	return plant, nil
}

func (s *PlantService) listCacheKey(params models.PlantSearchParams) string {
	raw := fmt.Sprintf("q=%s|season=%s|climate=%s|region=%s|month=%d|type=%s|life=%s|page=%d|limit=%d",
		params.Query, params.Season, params.ClimateZone, params.RegionCode, params.Month, params.PlantType, params.Lifecycle, params.Page, params.Limit)
	sum := sha1.Sum([]byte(raw))
	return "plant:v1:list:" + hex.EncodeToString(sum[:])
}
