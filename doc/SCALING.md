# SCALING

## Horizontal scaling
- API: stateless replicas.
- DB: read replicas for query-heavy endpoints.
- Redis: HA mode for durability.

## Complexity notes
- Read throughput scales near-linearly with API replicas until DB bottleneck.
- Migration and schema changes remain O(number_of_migrations).
- Cache invalidation complexity increases with node count and key cardinality.
