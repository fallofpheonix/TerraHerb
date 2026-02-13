package service

import "terraherbarium/backend/internal/cache"

func (s *PlantService) Cache() *cache.RedisClient {
	return s.cache
}
