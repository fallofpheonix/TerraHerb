# SATURATION

## Saturation signals
- Rising p95 latency under moderate concurrency.
- DB connection pool exhaustion.
- Redis command latency spikes.

## Immediate responses
- Increase pool limits carefully.
- Add/adjust indexes for hot queries.
- Shift high-read paths to cache with bounded TTL.
