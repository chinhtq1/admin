-- EMS PoC schema. Works on plain PostgreSQL 16; if the TimescaleDB extension is available the
-- telemetry table becomes a hypertable (Apache-2.0 part only: the compose file starts Timescale
-- with timescaledb.license=apache, so no TSL feature — compression, continuous aggregates — is used).

CREATE TABLE IF NOT EXISTS telemetry (
  site_id      text        NOT NULL,
  device_id    text        NOT NULL,
  point_code   text        NOT NULL,              -- 07 §7.2, ví dụ meter.p, ess.soc
  ts           timestamptz NOT NULL,              -- đầu cửa sổ (gauge) hoặc thời điểm đọc (counter), UTC
  value        double precision,                  -- avg (gauge, unit_raw) | raw int64 (counter); NULL nếu BAD_*
  quality      text        NOT NULL,              -- 07 §6.9
  w_s          integer,                           -- độ dài cửa sổ (5/60/300); NULL với counter C4
  v_min double precision, v_max double precision, v_last double precision,
  n            integer,
  cov_ms       integer,
  ts_src       timestamptz,                       -- thời gian thiết bị (nếu có)
  ts_ingest    timestamptz NOT NULL DEFAULT now(),-- cloud gán (07 §7.4)
  edge_id      text        NOT NULL,
  stream       text        NOT NULL,
  seq          bigint      NOT NULL,
  via_backfill boolean     NOT NULL DEFAULT false,
  PRIMARY KEY (site_id, device_id, point_code, ts)
);

-- dedupe lô theo (edge_id, stream, seq) — 07 §6.10; cũng dùng để chứng minh "không lỗ seq"
CREATE TABLE IF NOT EXISTS telemetry_batch (
  arrival bigserial,                               -- thứ tự cloud nhận được (để kiểm backfill đúng thứ tự)
  edge_id text NOT NULL, stream text NOT NULL, seq bigint NOT NULL,
  topic text NOT NULL, n_points integer NOT NULL, batch_ts timestamptz,
  ts_ingest timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (edge_id, stream, seq)
);

CREATE TABLE IF NOT EXISTS command (
  command_id    text PRIMARY KEY,
  edge_id       text NOT NULL,
  type          text,
  params        jsonb,
  envelope      jsonb,                             -- do dispatcher (tools/ems_cli.py) ghi khi gửi
  created_at    timestamptz DEFAULT now(),
  last_state    text,
  last_state_at timestamptz
);

CREATE TABLE IF NOT EXISTS command_ack (
  id         bigserial PRIMARY KEY,
  command_id text NOT NULL,
  edge_id    text NOT NULL,
  state      text NOT NULL,                       -- 07 §8.4: RECEIVED, ACCEPTED, DISPATCHED, APPLIED, ...
  ts         timestamptz NOT NULL,
  payload    jsonb NOT NULL,
  ts_ingest  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS command_ack_cid ON command_ack(command_id, id);

CREATE TABLE IF NOT EXISTS event (
  id        bigserial PRIMARY KEY,
  edge_id   text NOT NULL,
  event_id  text NOT NULL UNIQUE,
  type      text NOT NULL,
  device_id text,
  ts        timestamptz NOT NULL,
  ts_src    timestamptz,
  state     text,
  code_raw  text,
  payload   jsonb,
  ts_ingest timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS edge_state (
  edge_id text PRIMARY KEY, payload jsonb NOT NULL, updated_at timestamptz NOT NULL
);

CREATE OR REPLACE VIEW latest_value AS
  SELECT DISTINCT ON (site_id, device_id, point_code)
         site_id, device_id, point_code, ts, value, quality, w_s, stream, ts_ingest
  FROM telemetry
  ORDER BY site_id, device_id, point_code, ts DESC;

DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_available_extensions WHERE name = 'timescaledb') THEN
    CREATE EXTENSION IF NOT EXISTS timescaledb;
    PERFORM create_hypertable('telemetry', 'ts', chunk_time_interval => interval '1 day', if_not_exists => true);
    RAISE NOTICE 'telemetry is a TimescaleDB hypertable';
  ELSE
    RAISE NOTICE 'TimescaleDB not available: plain PostgreSQL table';
  END IF;
END $$;
