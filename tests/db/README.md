# tests/db — database (marker `db`)

Ephemeral TimescaleDB (`timescale/timescaledb:2.17.2-pg16`) via testcontainers, schema from `infra/db/init.sql`
(fixture `pg_dsn`, `db`). Constraints, upsert/dedupe SQL, `latest_value` view, hypertable creation, init.sql idempotency,
later Flyway/Liquibase migrations (expand/contract). Never uses the emspoc stack's DB.
