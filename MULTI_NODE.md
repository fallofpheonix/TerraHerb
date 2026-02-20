# MULTI_NODE

## Single-node today
- One API instance, one PostgreSQL primary, one Redis node.

## Multi-node target
- Stateless API replicas behind load balancer.
- Managed Postgres with read replicas.
- Redis HA setup for cache/rate-limit durability.

## Consistency notes
- Keep auth token verification stateless.
- Ensure cache keys are versioned for rolling deploy safety.
