"""Local SQLite store: uplink outbox (store-and-forward), per-stream seq, seen-command table.

07 §6.7/§6.10: seq is monotonic per (edge_id, stream) and survives restarts; the outbox never drops
events/acks. Telemetry rows are deleted only on the cloud's TELEMETRY_ACK (sent by ingest after DB commit,
07 §7.1 / 15 §5.3) and re-sent if unacknowledged; events and acks are deleted on broker PUBACK (PoC).
"""
from __future__ import annotations

import json
import sqlite3
import threading
import time


def now_ms() -> int:
    return int(time.time() * 1000)


class Store:
    def __init__(self, path: str):
        self.db = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
        self.lock = threading.Lock()
        with self.lock:
            self.db.execute("PRAGMA journal_mode=WAL")
            self.db.executescript("""
            CREATE TABLE IF NOT EXISTS outbox(
              id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, stream TEXT, seq INTEGER,
              topic TEXT NOT NULL, backfill_topic TEXT, payload BLOB NOT NULL, props TEXT NOT NULL,
              created_ms INTEGER NOT NULL, sent_ms INTEGER);
            CREATE TABLE IF NOT EXISTS seq(stream TEXT PRIMARY KEY, seq INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS command(
              command_id TEXT PRIMARY KEY, state TEXT NOT NULL, envelope TEXT NOT NULL,
              last_ack TEXT, expires_ms INTEGER, updated_ms INTEGER);
            CREATE TABLE IF NOT EXISTS signer_seq(kid TEXT PRIMARY KEY, seq INTEGER NOT NULL);
            """)
            try:                                  # upgrade a PoC v0 outbox in place
                self.db.execute("ALTER TABLE outbox ADD COLUMN sent_ms INTEGER")
            except sqlite3.OperationalError:
                pass

    # ---- seq ------------------------------------------------------------------------
    def next_seq(self, stream: str) -> int:
        with self.lock:
            self.db.execute("INSERT INTO seq(stream, seq) VALUES(?, 1) "
                            "ON CONFLICT(stream) DO UPDATE SET seq = seq + 1", (stream,))
            return self.db.execute("SELECT seq FROM seq WHERE stream=?", (stream,)).fetchone()[0]

    def last_seqs(self) -> dict:
        with self.lock:
            return dict(self.db.execute("SELECT stream, seq FROM seq").fetchall())

    # ---- outbox ---------------------------------------------------------------------
    def enqueue(self, kind: str, topic: str, payload: dict, props: dict, stream: str | None = None,
                seq: int | None = None, backfill_topic: str | None = None) -> None:
        with self.lock:
            self.db.execute(
                "INSERT INTO outbox(kind, stream, seq, topic, backfill_topic, payload, props, created_ms) "
                "VALUES(?,?,?,?,?,?,?,?)",
                (kind, stream, seq, topic, backfill_topic, json.dumps(payload, separators=(",", ":")).encode(),
                 json.dumps(props), now_ms()))

    def pending(self, since_ms: int, live: bool, limit: int, resend_ms: int) -> list[tuple]:
        """Rows never sent, or sent but not acknowledged for resend_ms (telemetry awaiting TELEMETRY_ACK)."""
        op = ">=" if live else "<"
        with self.lock:
            return self.db.execute(
                f"SELECT id, kind, topic, backfill_topic, payload, props FROM outbox WHERE created_ms {op} ? "
                "AND (sent_ms IS NULL OR sent_ms < ?) ORDER BY id LIMIT ?", (since_ms, now_ms() - resend_ms, limit)).fetchall()

    def delete(self, row_id: int) -> None:
        with self.lock:
            self.db.execute("DELETE FROM outbox WHERE id=?", (row_id,))

    def mark_sent(self, row_id: int) -> None:
        with self.lock:
            self.db.execute("UPDATE outbox SET sent_ms=? WHERE id=?", (now_ms(), row_id))

    def reset_unacked(self) -> int:
        """On (re)connect: anything sent on the previous connection but never acknowledged is sent again,
        in seq order with the rest of the backlog (its PUBACK/TELEMETRY_ACK may have been lost)."""
        with self.lock:
            return self.db.execute("UPDATE outbox SET sent_ms=NULL WHERE sent_ms IS NOT NULL").rowcount

    def ack_telemetry(self, stream: str, ack_seq: int) -> int:
        """TELEMETRY_ACK: drop every telemetry row of this stream with seq <= ack_seq."""
        with self.lock:
            return self.db.execute("DELETE FROM outbox WHERE kind='telemetry' AND stream=? AND seq<=?",
                                   (stream, ack_seq)).rowcount

    def outbox_stats(self) -> dict:
        with self.lock:
            n, oldest, unacked = self.db.execute(
                "SELECT count(*), min(created_ms), count(sent_ms) FROM outbox").fetchone()
        return {"buffered": n - unacked, "awaiting_ack": unacked, "buffer_oldest_ts": oldest}

    # ---- commands -------------------------------------------------------------------
    def get_command(self, command_id: str):
        with self.lock:
            return self.db.execute("SELECT state, last_ack FROM command WHERE command_id=?", (command_id,)).fetchone()

    def put_command(self, command_id: str, state: str, envelope: dict, last_ack: dict | None, expires_ms: int | None):
        with self.lock:
            self.db.execute(
                "INSERT INTO command(command_id, state, envelope, last_ack, expires_ms, updated_ms) VALUES(?,?,?,?,?,?) "
                "ON CONFLICT(command_id) DO UPDATE SET state=excluded.state, last_ack=excluded.last_ack, "
                "updated_ms=excluded.updated_ms",
                (command_id, state, json.dumps(envelope), json.dumps(last_ack) if last_ack else None, expires_ms, now_ms()))

    def check_and_set_signer_seq(self, kid: str, seq: int) -> bool:
        """True if seq is newer than the last accepted seq of this signer (anti-replay, 07 §8.7 A.4)."""
        with self.lock:
            row = self.db.execute("SELECT seq FROM signer_seq WHERE kid=?", (kid,)).fetchone()
            if row and seq <= row[0]:
                return False
            self.db.execute("INSERT INTO signer_seq(kid, seq) VALUES(?,?) ON CONFLICT(kid) DO UPDATE SET seq=excluded.seq",
                            (kid, seq))
            return True
