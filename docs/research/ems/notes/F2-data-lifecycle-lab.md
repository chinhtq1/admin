# F2 — Nhật ký lab vòng đời dữ liệu: đo dung lượng, nén, truy vấn, WAL, Parquet

[← Mục lục](../index.html) · [17 Vòng đời dữ liệu](../17-data-lifecycle.md) · [F Dữ liệu](F-data-analytics.md) · [05 Domain](../05-domain-model.html) · [06 Kiến trúc](../06-system-architecture.html) · [15 Mô phỏng](../15-simulators-and-messaging.md)

- Phiên bản 1 · Ngày 2026-10-10 · Người ghi: Data & Analytics Architect (agent F2) · Trạng thái: lab đã chạy xong, container đã xóa.
- Mục đích: thay các số **giả định** về byte/hàng, tỷ lệ nén, chi phí truy vấn trong F §3.1.3 và 05 §19 bằng số **đo được** trên một site tham chiếu tổng hợp. Mọi số ở đây là `[FACT – đo trong lab]` cho dữ liệu tổng hợp; áp cho dữ liệu thật là `[INFERENCE]` cho tới khi có PoC-01 với dữ liệu site thật (Q-F02, Q-E-13).

## 1. Môi trường

| Hạng mục | Giá trị |
|---|---|
| Máy | VM Linux 6.18, 4 vCPU, 15 GiB RAM, đĩa ảo chung (252 GB, lúc chạy còn ~18 GB trống) |
| Image | `timescale/timescaledb:2.17.2-pg16` (đã có sẵn cục bộ, cùng image với PoC `infra/`) |
| PostgreSQL | 16.6 (musl, Alpine) |
| TimescaleDB | 2.17.2, chạy với `timescaledb.license=timescale` **chỉ trong container lab riêng** `f2lab-tsdb` để đo nén/CAGG. PoC `infra/` vẫn chạy `license=apache` (không đụng tới). Việc dùng TSL trong lab tự host không thay đổi câu hỏi giấy phép cho SaaS (Q-14) |
| Tham số | `shared_buffers=2GB`, `work_mem=64MB`, `maintenance_work_mem=1GB`, `max_wal_size` 8 GB rồi hạ xuống 1 GB (xem §6 sự cố đĩa) |
| DuckDB | 1.1.3 (pip trong `python:3.12-slim`, chạy `python -I`) để ghi Parquet |
| Script | `scratchpad/f2lab/01_schema_gen.sql`, `02a_build_ht.sql`, `02b_registers.sql`, `02c_variants.sql`, `02_measure.sql`, `03_cagg_query.sql`, `05_wal.sql`, `04_parquet.py`, `cap.py` (không commit; nội dung chính chép dưới đây) |

## 2. Dữ liệu tổng hợp

- 1 site tham chiếu, 1.000 chuỗi (05 §19): chuỗi 1–100 cửa sổ 5 s (C1), 101–950 cửa sổ 60 s (C2), 951–1.000 là thanh ghi int8 Wh mỗi 60 s (C4). 7 ngày (2026-10-01 → 2026-10-08 UTC).
- Gauge: 20.664.000 hàng (100 × 17.280 × 7 + 850 × 1.440 × 7). Thanh ghi: 504.000 hàng.
- Hình dạng: chuỗi lẻ theo đường cong PV ngày (sin), chuỗi chẵn theo tải; nhiễu ±1–2% **ngẫu nhiên độc lập** cho `v_avg`, `v_min`, `v_max`, `v_last` (làm tròn 0,1–0,01). Đây là trường hợp **bi quan** cho nén (dữ liệu thật thường mượt hơn và lượng tử theo thang thanh ghi).
- Thanh ghi: tổng tích lũy đơn điệu (int8), tăng theo công suất.
- Lưu ý thứ tự nạp: dữ liệu nạp **theo chuỗi rồi theo thời gian** (series-major), khác ingest thật (theo thời gian). Ảnh hưởng tới phép thử BRIN (§4.3).

Cột của bảng gauge đầy đủ (theo 05 §7 `ts_gauge`): `series_id int4, ts timestamptz, window_s int2, v_avg float8, v_min float4, v_max float4, v_last float8, n int2, covered_ms int4, quality int4, ts_ingest timestamptz`, PK `(series_id, ts)`.

Bảng "layout PoC" chép đúng cột của `infra/db/init.sql` (`site_id, device_id, point_code` kiểu text lặp mỗi hàng, `quality text`, `edge_id`, `stream`, `seq`, …), PK `(site_id, device_id, point_code, ts)`.

## 3. Lệnh chính

```bash
docker run -d --name f2lab-tsdb -e POSTGRES_PASSWORD=lab -e POSTGRES_DB=lab --shm-size=1g \
  timescale/timescaledb:2.17.2-pg16 postgres -c timescaledb.license=timescale -c timescaledb.telemetry_level=off \
  -c shared_buffers=2GB -c max_wal_size=8GB -c maintenance_work_mem=1GB -c work_mem=64MB
docker exec f2lab-tsdb psql -U postgres -d lab -v ON_ERROR_STOP=1 -f /tmp/01_schema_gen.sql   # sinh g_heap, g_text
docker exec f2lab-tsdb psql -U postgres -d lab -f /tmp/02a_build_ht.sql   # hypertable chunk 1 ngày, nén từng ngày
docker exec f2lab-tsdb psql -U postgres -d lab -f /tmp/02c_variants.sql   # 4 biến thể cột, 1 ngày
docker exec f2lab-tsdb psql -U postgres -d lab -f /tmp/02_measure.sql     # BRIN, thống kê nén, thanh ghi
docker exec f2lab-tsdb psql -U postgres -d lab -f /tmp/03_cagg_query.sql  # CAGG + chi phí truy vấn + DML trên chunk nén
docker exec f2lab-tsdb psql -U postgres -d lab -f /tmp/05_wal.sql         # WAL/hàng
# Parquet: \copy 1 ngày ra CSV → DuckDB COPY ... (FORMAT parquet, COMPRESSION zstd, ROW_GROUP_SIZE 1000000), sắp theo (series_id, ts)
docker rm -f f2lab-tsdb
```

Thiết lập nén (cú pháp 2.17): `ALTER TABLE g_ht SET (timescaledb.compress, timescaledb.compress_segmentby='series_id', timescaledb.compress_orderby='ts')` rồi `compress_chunk()`.

CAGG (partial ghép được, theo F §3.4):

```sql
CREATE MATERIALIZED VIEW agg_5m WITH (timescaledb.continuous, timescaledb.materialized_only = true) AS
SELECT series_id, time_bucket('5 minutes', ts) AS bucket,
       sum(v_avg * window_s) AS integral, sum(window_s) AS covered_s, min(v_min) AS v_min, max(v_max) AS v_max,
       first(v_avg, ts) AS v_first, last(v_avg, ts) AS v_last, count(*) AS n, bit_or(quality) AS q_or
FROM g_ht GROUP BY series_id, bucket WITH NO DATA;
-- agg_1h: CAGG phân cấp trên agg_5m (sum integral/covered_s, min/max, first/last, sum n)
```

## 4. Kết quả `[FACT – đo trong lab]`

### 4.1 Byte/hàng chưa nén

| Bảng | Hàng | Heap | Index | Tổng | B/hàng (tổng) |
|---|---|---|---|---|---|
| Layout PoC, khóa text (`g_text`) | 20.664.000 | 3.901.399.040 | 2.115.829.760 | 6.018.285.568 | **291,2** (heap 188,8 + index 102,4) |
| Layout 05 §7, `series_id int4`, bảng thường (`g_heap`) | 20.664.000 | 2.089.877.504 | 651.812.864 | 2.742.288.384 | **132,7** (heap 101,1 + PK 31,5) |
| Như trên, hypertable (PK + index `ts` mặc định của `create_hypertable`) | 20.664.000 | 2.090.549.248 | 879.943.680 | 2.970.492.928 | **143,8** |
| Thanh ghi `r_ht` (int8) hypertable | 504.000 | — | — | 55.410.688 | **109,9** |
| PoC đang chạy (`infra/`, đọc-only): `avg(pg_column_size(row))` 230 hàng | — | — | — | — | ~160,6 B dữ liệu hàng (chưa tính header trang, index) |

Kết luận: khóa `series_id int4` thay cho 3 cột text **giảm 54%** dung lượng chưa nén (291 → 133 B/hàng). Index `ts` mặc định của hypertable tốn thêm ~11 B/hàng mà truy vấn theo `(series_id, ts)` không cần.

### 4.2 Nén cột TimescaleDB (segmentby `series_id`, orderby `ts`, chunk 1 ngày)

| Biến thể (1 ngày, 2.952.000 hàng) | Cột | Chưa nén B/hàng | Nén B/hàng | Tỷ lệ |
|---|---|---|---|---|
| `v_full` | đủ cột 05 §7 (gồm `v_last`, `covered_ms`, `ts_ingest`) | 143,8 | **16,85** | 8,5× |
| `v_mid` | `series_id, ts, v_avg, v_min, v_max, n, quality` | 110,9 | **11,32** | 9,8× |
| `v_lean` | `series_id, ts, v_avg, quality` | 102,8 | **6,51** | 15,8× |
| `v_quant` | như `v_mid`, giá trị làm tròn về số nguyên (tín hiệu "mượt", lượng tử thô) | 110,9 | **2,14** | 51,8× |
| Cả 7 ngày `g_ht` (đủ cột) | | 143,8 | **16,71** (345.202.688 B) | 8,5× |
| Thanh ghi `r_ht` 7 ngày (int8 đơn điệu) | | 109,9 | **1,97** | 56× |

Thời gian: nén một chunk 1 ngày (2,95 M hàng) ≈ 3,0–3,5 s; nạp + nén 6 ngày (17,7 M hàng) bằng `INSERT … SELECT` theo ngày = 102,8 s → ≥ 170 k hàng/s gồm cả nén (1 phiên, 4 vCPU).

Đọc kết quả: giả định cũ **5 B/hàng** (F §3.1.3, 05 §19) chỉ đạt khi bảng gọn (≤ 4 cột giá trị) hoặc tín hiệu mượt. Với đủ cột và nhiễu độc lập trên avg/min/max/last, con số là **~17 B/hàng**. Mỗi cột giá trị nhiễu tốn ~2–5 B sau nén. Đề xuất: **10 B/hàng** làm số kế hoạch (dải 2–17), bỏ `ts_ingest` theo hàng (giữ ở `telemetry_batch`) và cân nhắc bỏ `v_last` cho C2 (17 §3, §4).

### 4.3 Index

| Index trên `g_heap` (20,66 M hàng) | Kích thước |
|---|---|
| PK B-tree `(series_id, ts)` | 651.812.864 B (31,5 B/hàng) |
| B-tree `(ts)` | 149.250.048 B (7,2 B/hàng) |
| BRIN `(ts)`, `pages_per_range=32` | 286.720 B |

`pg_stats.correlation`: `series_id` = 1, `ts` = −0,014 (do nạp series-major). BRIN chỉ có ích khi thứ tự vật lý khớp `ts` (ingest thật theo thời gian → correlation gần 1, `[INFERENCE]`). BRIN nhỏ hơn B-tree ~520 lần nhưng không thay được PK `(series_id, ts)` cho truy vấn theo chuỗi.

### 4.4 Continuous aggregate

| Hạng mục | Kết quả |
|---|---|
| Refresh lần đầu `agg_5m` 7 ngày (20,66 M hàng nguồn, đã nén) | 51,0 s → ~2,5 µs/hàng nguồn |
| Refresh `agg_1h` phân cấp từ `agg_5m` | 5,5 s |
| `agg_5m` | 1.915.200 hàng; 287.424.512 B chưa nén (**150 B/hàng**); nén 46.899.200 B (**24,5 B/hàng**) |
| `agg_1h` | 159.600 hàng; 23.601.152 B chưa nén (**148 B/hàng**) |
| Bẫy: refresh CAGG đã nén sau dữ liệu trễ | `ERROR: tuple decompression limit exceeded by operation … current limit: 100000, tuples decompressed: 820800` (refresh cửa sổ 1 h trên `agg_5m` đã nén). Đặt `timescaledb.max_tuples_decompressed_per_dml_transaction=0` thì refresh xong trong **4,37 s**; `agg_1h` 0,05 s |

Bài học: **không nén CAGG trong vùng còn refresh** (`compress_after` của CAGG phải lớn hơn `start_offset` của refresh policy), nếu không mỗi lần dữ liệu trễ sẽ giải nén cả segment và có thể lỗi giới hạn.

### 4.5 Chi phí truy vấn (cache ấm, 1 phiên, `EXPLAIN ANALYZE`)

| Truy vấn | Nguồn | Hàng trả | Thời gian thực thi |
|---|---|---|---|
| 8 chuỗi C2 × 7 ngày | raw nén `g_ht` | 80.640 | 8,3 ms |
| như trên | raw heap `g_heap` | 80.640 | 16,9 ms |
| như trên | `agg_5m` | 16.128 | 2,9 ms |
| như trên | `agg_1h` | 1.344 | 1,9 ms |
| 1 chuỗi C1 (5 s) × 1 ngày | raw nén | 17.280 | 1,2 ms |
| như trên | `agg_5m` | 288 | 0,2 ms |
| Tổng ngày của 950 chuỗi (dashboard site) | raw nén | 950 | **309,5 ms** |
| như trên | `agg_1h` | 950 | **7,4 ms** (42× nhanh hơn) |
| Giá trị mới nhất 950 chuỗi bằng `DISTINCT ON … ORDER BY ts DESC` trên raw (giống view `latest_value` của PoC) | `g_heap` | 950 | **8.374 ms** |
| như trên | bảng `latest_value` (PK `series_id`) | 950 | **0,13 ms** |
| `count(*)` toàn hypertable 20,66 M hàng (đã nén) | `g_ht` | 1 | 15,4 ms (dùng metadata segment); `approximate_row_count` 7 ms |

Lưu ý: cache ấm, một người dùng; với hàng trăm người dùng đồng thời và dữ liệu 1.000 site, chênh lệch raw vs aggregate tăng theo số hàng phải quét (INFERENCE).

### 4.6 Ghi dữ liệu trễ vào chunk đã nén

| Thao tác | Hàng | Thời gian |
|---|---|---|
| `INSERT … ON CONFLICT DO NOTHING` 100 chuỗi × 1 h vào chunk đã nén (ts lệch 1 s, hàng mới) | 6.000 | 3.670 ms (~1,6 k hàng/s) |
| `INSERT … ON CONFLICT (series_id, ts) DO UPDATE` cùng khoảng (hàng trùng khóa) | 6.000 | 800 ms |
| So sánh: nạp vào chunk chưa nén + nén | 17,7 M | 102,8 s (≥ 170 k hàng/s) |

Kết luận: DML trên chunk nén chậm hơn ~100 lần so với ghi vào chunk chưa nén. Backfill 7 ngày của một site (~21 M hàng) đi vào chunk đã nén sẽ mất hàng giờ → giữ `compress_after = 7 ngày` (bằng buffer cứng NFR-DATA-001) để backfill thường rơi vào chunk chưa nén; dữ liệu trễ hơn đi `late_landing` và gộp theo lô (17 §6).

### 4.7 WAL

| Hạng mục | Kết quả |
|---|---|
| Nạp 1 ngày (2.952.000 hàng) vào hypertable mới ngay sau `CHECKPOINT` | WAL 816.222.144 B → **276,5 B/hàng**; kích thước bảng 424.370.176 B |
| Nén chunk đó | WAL 48.822.632 B (≈ kích thước sau nén 49.733.632 B) |

WAL ≈ 1,9× kích thước dữ liệu chưa nén (gồm full-page write sau checkpoint, 2 index). `wal_compression` mặc định (off) trong lab. Hệ quả cho dung lượng lưu WAL archive và PITR (17 §8).

### 4.8 Parquet (DuckDB 1.1.3, 1 ngày, 2.952.000 hàng, sắp theo `(series_id, ts)`, row group 1 M)

| Codec | Byte | B/hàng | Ghi |
|---|---|---|---|
| CSV (nguồn, có header) | 166.142.897 | 56,28 | — |
| Parquet ZSTD level 3 | 15.020.174 | **5,09** | 1,6 s |
| Parquet ZSTD level 9 | 13.441.598 | 4,55 | 1,3 s |
| Parquet Snappy | 41.068.344 | 13,91 | 0,7 s |
| Đọc lại 8 chuỗi từ file ZSTD | 11.520 hàng | — | 0,034 s |

Cột Parquet: `series_id, ts, window_s, v_avg, v_min, v_max, v_last, n, covered_ms, quality` (không có `ts_ingest`). Parquet ZSTD nhỏ hơn bản nén TimescaleDB đủ cột ~3 lần trong phép thử này.

### 4.9 Không đo được

- Kích thước/tốc độ `pgBackRest`/`WAL-G` (không cài trong lab), tỷ lệ nén WAL archive → `[UNKNOWN]`, 17 §8 dùng dải giả định.
- `pg_dump` hypertable nén: không chạy vì thiếu đĩa.
- Tải đồng thời nhiều người dùng, 1.000 site thật: thuộc PoC-01.

## 5. Mô hình dung lượng (cap.py)

Đầu vào: 3,02 M hàng/site/ngày (F §3.1.3), agg_5m 288 k hàng/site/ngày, agg_1h 24 k; byte/hàng ở §4. Kết quả in vào 17 §3. Một vài dòng kiểm tra:

```
baseline rows/site/day=3,020,000 samples/s 1000 sites= 34,954 unc/day 434.9 GB comp/yr 11.0 TB wal/day 833.5 GB
steady 1000: hot7d 3.0 TB warm13mo 11.7 TB a5 5y 12.9 TB a1/yr 219.0 GB sum 28.7 TB
fallback raw heap 90 d 1000 sites 36.1 TB ; 395 d 158.7 TB
WAL 35d 1000 sites raw 29.2 TB ; 14d 11.7 TB
```

## 6. Sự cố trong lab và dọn dẹp

- Lần nạp đầu đặt `max_wal_size=8GB` và giữ cả bảng `g_text` (6,0 GB) + `g_heap` (2,7 GB): đĩa VM xuống còn 1,9 GB trống, lệnh `INSERT INTO g_ht` lỗi `No space left on device`. Ghi nhận kích thước `g_text`, xóa `g_text`, hạ `max_wal_size` = 1 GB, `CHECKPOINT`; nạp lại hypertable theo từng ngày rồi nén ngay. Không ảnh hưởng dữ liệu đo (số ở §4.1 đọc trước khi xóa). Container PoC `emspoc-*` lúc đó vẫn healthy.
- Dọn dẹp: `docker rm -f f2lab-tsdb`; rồi `docker volume prune -f --filter "label!=com.docker.compose.project"` → giải phóng 11,79 GB **volume ẩn danh không gắn container** (gồm volume dữ liệu của container lab). Volume có nhãn compose `emspoc_db-data`, `emspoc_bridge-data`, `emspoc_mosquitto-data` còn nguyên (đã kiểm `docker volume ls`). Lưu ý cho agent PoC: tại thời điểm dọn, các container `emspoc-*` đã không còn (không phải do F2 xóa); nếu agent khác có volume ẩn danh cần giữ thì có thể đã bị prune — lần sau nên dùng `docker rm -v <container>` thay cho prune. File Parquet/CSV tạm đã xóa.

## 7. Sổ bằng chứng tìm kiếm (WebSearch; WebFetch bị chặn — mọi URL "qua kết quả tìm kiếm")

| # | Claim | URL | Loại nguồn | Độ tin | Ghi chú |
|---|---|---|---|---|---|
| W1 | Restore logic TimescaleDB: tạo extension, `timescaledb_pre_restore()`, `pg_restore`, `timescaledb_post_restore()`; nên ghi lại phiên bản PostgreSQL và TimescaleDB khi dump; không dùng `pg_restore -j`; dump được hypertable nén không cần giải nén | https://www.tigerdata.com/docs/deploy/self-hosted/backup-and-restore/logical-backup ; https://docs.timescale.com/self-hosted/latest/backup-and-restore/logical-backup | Tài liệu vendor | High | Trang "Versions are mismatched…" không đọc được → quy tắc khớp phiên bản cụ thể `[UNKNOWN]` |
| W2 | `timescaledb_post_restore()` lỗi "does not exist" khi chưa tạo extension | https://support.zabbix.com/browse/ZBX-26790 | Bug tracker bên thứ ba | Med | Runbook phải tạo extension đúng phiên bản trước |
| W3 | Lỗi restore liên quan trigger/catalog hypertable | https://www.timescale.com/forum/t/timescaledb-backup-and-restore-issue/2527 ; https://timescale.com/forum/t/errors-during-restore-using-pg-restore/443 ; https://github.com/timescale/timescaledb/issues/1581 | Forum/issue | Med | Ưu tiên backup vật lý; logical chỉ cho xuất/di trú |
| W4 | CAGG khi di trú được tạo lại và tính lại; tính lại không gồm raw đã xóa | https://docs.timescale.com/self-hosted/latest/migration/schema-then-data | Tài liệu vendor | Med | Không được dựa vào "tính lại CAGG" sau khi raw đã hết hạn → CAGG phải nằm trong backup |
| W5 | pgBackRest: incremental/differential theo block, nén lz4/zstd/gzip, mã hóa AES-256 phía client, kho S3/MinIO/GCS; WAL-G delta backup, viết bằng Go; Barman quản lý tập trung nhiều server, incremental dựa rsync | https://tessl.io/registry/alonso-skills/postgres/files/references/85-backup-tools.md ; https://ramnode.com/guides/series/postgres-superstack/pgbackrest ; https://chat2db.ai/resources/blog/pgbackrest-vs-barman-vs-wal-g ; https://severalnines.com/blog/automating-backups-and-disaster-recovery-in-postgresql-at-scale-pgbackrest-vs-barman/ ; https://dev.to/piteradyson/postgresql-backup-tools-comparison-databasus-wal-g-pgbackrest-and-barman-2kg ; https://www.kunalganglani.com/blog/postgresql-backup-tools-compared.md | Blog thứ cấp | Med | Chi tiết mã hóa của WAL-G/Barman chưa thấy → `[UNKNOWN]` |
| W6 | Một nguồn 2026 nói người duy trì pgBackRest tuyên bố ngừng (4/2026) rồi được nhóm tài trợ cứu sau ~3 tuần | https://thebuild.com/blog/after-pgbackrest/ ; https://www.kunalganglani.com/blog/postgresql-backup-tools-compared.md | Blog | Low (chưa kiểm chứng) | Rủi ro R-62; kiểm pgbackrest.org trước khi chốt |
| W7 | pgBackRest: `repo1-retention-full`, `repo1-retention-diff` (hết hạn diff kéo theo incr phụ thuộc); WAL hết hạn theo full cũ nhất còn giữ; nhiều repo (repo1/repo2) archive WAL vào mọi repo; `archive-async` + `spool-path` | https://docs.pgedge.com/pgbackrest/v2-57-0/user-guide/retention/ ; https://www.percona.com/blog/what-if-the-backup-server-is-down-and-a-backup-is-needed-multi-repo-functionality-of-pgbackrest/ ; https://pgbackrest.org/1/configuration.html ; https://enterprisedb.com/docs/supported-open-source/pgbackrest/05-retention_policy | Tài liệu (bản phân phối) + blog | Med–High | Cấu hình 17 §8 |
| W8 | LTTB: luận văn MSc Sveinn Steinarsson 2013, Đại học Iceland, "Downsampling Time Series for Visual Representation"; có bản port Python/JS | https://github.com/vim-zz/highcharts-downsample ; https://pypi.org/project/lttb/0.2.2 ; https://metacpan.org/pod/Data::DownSample::LargestTriangleThreeBuckets | Repo/registry | High | PDF skemman chỉ thấy qua snippet |
| W9 | pg_partman: `retention_keep_table`, `retention_schema` (ghi đè keep_table); detach không `CONCURRENTLY` trong `run_maintenance_proc()`; drop lỗi khi có FK phụ thuộc | https://api.pgxn.org/src/pg_partman/pg_partman-5.5.0/updates/pg_partman--4.7.0--4.7.1.sql ; https://api.pgxn.org/src/pg_partman/pg_partman-1.4.5/updates/pg_partman--1.2.0--1.3.0.sql ; https://www.crunchydata.com/blog/auto-archiving-and-data-retention-management-in-postgres-with-pg_partman ; https://cloud.google.com/blog/products/databases/dynamically-drop-partitions-within-cloud-databases ; https://www.postgrespro.com/list/thread-id/2705959 ; https://www.postgresql.org/message-id/CAB%2B%3D1TXEHjX4Rb5vqqN%2B9TVcBNU%3D981_Mh5T4bnZmPpzXzNMpw%40mail.gmail.com ; https://oneuptime.com/blog/post/2026-08-13-postgresql-partition-retention-drop-detach-archive/markdown | Changelog chính thức + blog | Med | Fallback detach → export → drop |
| W10 | CAGG: real-time aggregation tắt mặc định cho CAGG tạo từ 2.13 (một nguồn nói 2.11); `materialized_only`; `start_offset` refresh phải nhỏ hơn retention raw | https://oneuptime.com/blog/post/2026-01-27-timescaledb-continuous-aggregates/markdown ; https://www.tigerdata.com/docs/reference/timescaledb/continuous-aggregates ; https://www.tigerdata.com/blog/continuous-aggregate-refresh-policies-solar-wind-scada ; https://stackharbor.com/en/knowledge-base/timescaledb-continuous-aggregates-strategy/ | Tài liệu vendor + blog | Med–High | Phiên bản đổi mặc định: dùng `materialized_only` tường minh |
| W11 | Nén: `ALTER TABLE … SET (timescaledb.compress, compress_segmentby, compress_orderby)` chỉ bật, cần policy hoặc `compress_chunk`; segmentby = id nguồn dữ liệu; ví dụ energy 180 MB → 16 MB; cú pháp columnstore mới từ 2.18 | https://docs.timescale.com/api/latest/compression/alter_table_compression ; https://docs.timescale.com/tutorials/latest/energy-data/compress-energy/ ; https://stellio.readthedocs.io/en/latest/admin/enabling_timescale_compression.html | Tài liệu vendor/dự án | High | PoC dùng 2.17.2: cú pháp `compress_*` |
| W12 | S3 Object Lock: chế độ compliance không rút ngắn/không gỡ được kể cả root; governance cho phép người có quyền bypass; lock bảo vệ sự tồn tại, không bảo vệ nội dung sạch | https://cloudian.com/blog/s3-object-lock-protecting-data-for-ransomware-threats-and-compliance/ ; https://www.vinchin.com/vm-backup/what-is-immutable-backup.html ; https://avepoint.com/blog/backup/immutable-backup ; https://www.solved.scality.com/s3-object-lock/ | Blog vendor | Med | Cần tài liệu nhà cung cấp VN (Q-44) |
| W13 | BRIN nhỏ hơn B-tree hàng nghìn lần trên dữ liệu thời gian; cần correlation cao (> 0,9); B-tree thắng khi tập kết quả nhỏ | https://crunchydata.com/blog/postgres-indexing-when-does-brin-win ; https://crunchydata.com/blog/avoiding-the-pitfalls-of-brin-indexes-in-postgres ; https://hakibenita.com/postgresql-correlation-brin-multi-minmax ; https://www.depesz.com/?p=2915 | Blog chuyên môn | Med–High | Khớp đo §4.3 |
| W14 | DuckDB Parquet: `ROW_GROUP_SIZE` mặc định 122.880, `COMPRESSION zstd`, `COMPRESSION_LEVEL`; Hive partitioning | https://duckdb.org/docs/current/data/parquet/overview ; https://duckdb.org/docs/lts/data/parquet/tips | Tài liệu dự án | High | Dùng cho job export/verify |
| W15 | pg_cron: `cron.schedule`, `cron.unschedule`, `cron.job_run_details` (không tự dọn), chạy trong DB `postgres` mặc định, cần background worker | https://access.crunchydata.com/documentation/pg_cron/latest/ ; https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/PostgreSQL_pg_cron.md | Tài liệu | High | Fallback rollup |
| W16 | NĐ 53/2022/NĐ-CP: lưu trữ dữ liệu tại VN tối thiểu 24 tháng cho một số loại dữ liệu và doanh nghiệp (viễn thông, internet, TMĐT, mạng xã hội…), tính từ khi có yêu cầu; hiệu lực 01/10/2022 | https://gvlawyers.com.vn/wp-content/uploads/2022/11/VN_Legal-alert-for-Decree-53-on-Cybersecurity.pdf ; https://lsvn.vn/tu-01102022-du-lieu-nguoi-dung-internet-tai-viet-nam-se-duoc-luu-tru1661052929.html ; https://ey.com/content/dam/ey-unified-site/ey-com/vi-vn/technical/tax/documents/ey-vietnam-legal-update-sep-2022-vn.pdf | Bản tin luật sư/kiểm toán | Med | Có áp cho SaaS EMS không: `[UNKNOWN]` (Q-08) |
| W17 | Luật Kế toán 2015: chứng từ dùng trực tiếp ghi sổ lưu ≥ 10 năm; chứng từ quản lý ≥ 5 năm; lưu điện tử phải tra cứu được suốt thời hạn | https://ketoanthuanthien.vn/hoi-dap/quy-dinh-ve-thoi-han-luu-tru-hoa-don-dien-tu-la-bao-lau/ ; https://acman.vn/thoi-han-luu-tru-hoa-don-chung-tu-ma-ke-toan-can-biet.html ; https://einvoice.vn/tin-tuc/luu-tru-hoa-don-theo-nghi-dinh-123-2020-nd-cp | Trang tư vấn thứ cấp | Med | Áp cho dữ liệu tính tiền ESCO/PPA nếu khách dùng số của ta lập hóa đơn: `[INFERENCE]` |
| W18 | Giá object storage tại VN: không tìm thấy bảng giá Viettel IDC/FPT; CloudFly nêu phí băng thông 90–180 đ/GB; GreenNode nêu 900 đ/GB/tháng chỉ là ví dụ minh họa | https://cloudfly.vn/en/object-storage ; https://greennode.ai/blog/object-storage-viet-nam-gia-do-tre | Trang nhà cung cấp/blog | Low | Không dùng làm giá; 17 §11 để biến giá |

## 8. Vấn đề gửi agent khác

| Mã | Gửi | Vấn đề | Đề xuất |
|---|---|---|---|
| X-F2-01 | Agent PoC (`infra/`, `ingest/`) | Bảng `telemetry` dùng 3 khóa text mỗi hàng: 291 B/hàng so với 133 B/hàng khi dùng `series_id int4` (đo §4.1) | Thêm bảng `series` và đổi khóa sang `(series_id, ts)` khi qua giai đoạn PoC tiếp theo (17 §12) |
| X-F2-02 | Agent PoC | View `latest_value` dùng `DISTINCT ON` trên toàn bảng: 8,4 s ở 20,7 M hàng (đo §4.5) | Bảng/cache `latest_value` cập nhật lúc ingest, chỉ tiến theo `ts` (05 §7) |
| X-F2-03 | 05, 06, F | Giả định 5 B/hàng nén lạc quan cho đủ cột (đo 16,9 B; gọn 6,5 B; mượt 2,1 B) | Dùng 10 B/hàng kế hoạch, cập nhật 05 §19 và 06 bảng định cỡ khi tổng hợp |
| X-F2-04 | 10 §16.3 | WAL ~276 B/hàng → 35 ngày PITR cho cụm chuỗi thời gian ở 1.000 site ≈ 29 TB WAL thô | Tách chính sách PITR theo cụm (17 §8) |
