# 17 — Vòng đời dữ liệu: hiểu dữ liệu, kiểm soát tăng trưởng, giảm tải truy vấn, sao lưu và khôi phục

[← Mục lục](index.html) · [05 Domain](05-domain-model.html) · [06 Kiến trúc](06-system-architecture.html) · [10 An toàn](10-security-and-reliability.md) · [04 Yêu cầu](04-business-requirements.md) · [07 Tích hợp](07-device-integration.md) · [09 UX/UI](09-ux-ui-specification.html) · [12 Truy vết](12-traceability-matrix.md) · [13 Rủi ro](13-open-questions-and-risks.md) · [15 Mô phỏng](15-simulators-and-messaging.md)

| Thuộc tính | Giá trị |
|---|---|
| Tài liệu | 17 · Vòng đời dữ liệu (data lifecycle): dung lượng, phân tầng, retention, job, giảm tải truy vấn, backup/DR, quan sát chất lượng dữ liệu |
| Người viết | Data & Analytics Architect (agent F2) |
| Phiên bản | 1.0 · Ngày 2026-10-10 |
| Trạng thái | Đề xuất sẵn sàng triển khai cho Phase 1. Phụ thuộc cổng **NFR-DATA-013** (giấy phép TimescaleDB TSL, Q-14) nên mọi chính sách có **hai đường**: TimescaleDB TSL (đường A, ADR-06) và PostgreSQL thuần + `pg_partman` (đường E, dự phòng). |
| Đầu vào | [05 §7, §17, §19](05-domain-model.html#s19), [06 ADR-06, §11](06-system-architecture.html#adr-06), [07 §6.5–§6.12, §7](07-device-integration.md), [10 §7, §16](10-security-and-reliability.md), [15 §8.2](15-simulators-and-messaging.md), [04 §6.3](04-business-requirements.md), [F](notes/F-data-analytics.md), PoC `infra/db/init.sql`, `ingest/ingest.py` (đọc, không sửa) |
| Bằng chứng mới | Lab đo trên TimescaleDB 2.17.2 / PostgreSQL 16.6 với 1 site tham chiếu × 7 ngày (20,7 M hàng): [notes/F2-data-lifecycle-lab.md](notes/F2-data-lifecycle-lab.md). Số đo gắn `[FACT – đo trong lab]` và chỉ đúng cho dữ liệu tổng hợp đó |

Câu hỏi người dùng: *"Dữ liệu vào DB sẽ rất lớn nên có kế hoạch hay job gì để backup dữ liệu, giảm lượng query… nói chung phải hiểu dữ liệu."* Tài liệu này trả lời bằng: (1) bản đồ dữ liệu, (2) con số dung lượng có công thức và số đo, (3) chính sách tầng/retention kèm SQL, (4) quy tắc truy vấn, (5) kế hoạch backup/DR, (6) quan sát chất lượng dữ liệu, (7) danh sách job vận hành.

---

## Mục lục

1. [Tóm tắt quyết định](#s1)
2. [Bản đồ dữ liệu](#s2)
3. [Ước tính dung lượng](#s3)
4. [Giảm dữ liệu tại nguồn](#s4)
5. [Phân tầng lưu trữ và retention](#s5)
6. [Dữ liệu trễ, sai thứ tự, tính lại](#s6)
7. [Giảm tải truy vấn](#s7)
8. [Backup và DR](#s8)
9. [Hiểu dữ liệu: quan sát và chất lượng](#s9)
10. [Danh sách job vận hành](#s10)
11. [Chi phí ước tính](#s11)
12. [Áp dụng cho PoC hiện tại](#s12)
13. [Rủi ro và câu hỏi mở](#s13)
14. [Nguồn](#s14)

---

<a id="s1"></a>
## 1. Tóm tắt quyết định

### 1.1 Năm con số cần nhớ (1.000 site tham chiếu, 3,02 M mẫu/site/ngày, ≈ 35.000 mẫu/s)

| Đại lượng | Giá trị | Nhãn |
|---|---|---|
| Raw chưa nén | ≈ 435 GB/ngày · ≈ 159 TB/năm (144 B/hàng) | [FACT – đo trong lab] byte/hàng; [INFERENCE] phép nhân |
| Raw nén (TimescaleDB) | ≈ 11 TB/năm ở 10 B/hàng kế hoạch; dải đo 2,1–16,9 B/hàng → 2,3–18,6 TB/năm | như trên |
| Raw Parquet ZSTD (lưu trữ lạnh) | ≈ 5,6 TB/năm (5,1 B/hàng) | như trên |
| Tổng hợp | `agg_5m` nén ≈ 2,6 TB/năm (24,5 B/hàng); `agg_1h` ≈ 0,22 TB/năm; ngày/tháng không đáng kể | như trên |
| WAL sinh ra | ≈ 834 GB/ngày (276 B/hàng) trước nén → **yếu tố chi phối dung lượng backup PITR** | như trên |
| Trạng thái ổn định trong DB (đường A, sau 5 năm) | ≈ 29 TB = raw nóng 7 ngày 3 TB + raw nén 13 tháng 11,7 TB + `agg_5m` 5 năm 12,9 TB + giờ/ngày ~1 TB (chưa nhân bản HA) | [INFERENCE] |

### 1.2 Quyết định

| Mã | Quyết định | Lý do chính | Nhãn | Liên kết |
|---|---|---|---|---|
| D-17-01 | Mọi bảng chuỗi thời gian khóa `(series_id int4, ts)`; không lặp `site/device/point` dạng text mỗi hàng. `series` là sổ đăng ký duy nhất (05 §7) | Đo: 291 → 133 B/hàng (−54%) | [PROPOSAL], [FACT – đo trong lab] | NFR-DATA-014, FR-HIST-001 |
| D-17-02 | Raw: **0–7 ngày chưa nén** (chunk 1 ngày), **7 ngày–13 tháng nén** trong DB (đường A), **Parquet ZSTD** trên object storage từ tháng thứ 2 (bản thứ hai, độc lập) theo hợp đồng | Đáp ứng NFR-DATA-008; giữ backfill 7 ngày rơi vào chunk chưa nén (DML trên chunk nén chậm ~100×, đo) | [PROPOSAL] | NFR-DATA-008, NFR-DATA-016 |
| D-17-03 | Đường E (không TSL): raw trong DB **35 ngày** (MVP ≤ 200 site có thể 90 ngày), sau đó chỉ ở Parquet, truy vấn bằng job DuckDB bất đồng bộ | 13 tháng raw không nén ở 1.000 site ≈ 159 TB, không khả thi | [PROPOSAL], cần PO chốt (Q-63) | ADR-06 E |
| D-17-04 | Tổng hợp: CAGG `agg_5m` (real-time **bật**) và `agg_1h` (phân cấp, real-time **tắt**); ngày/tháng địa phương do job ghi sau watermark; **không nén CAGG trong cửa sổ refresh** | Đo: refresh CAGG đã nén sau dữ liệu trễ lỗi giới hạn giải nén | [PROPOSAL], [FACT – đo trong lab] | FR-HIST-005, F-P09 |
| D-17-05 | Dashboard **không bao giờ** đọc raw: `latest_value` (cache) + aggregate; độ phân giải tự chọn theo ngân sách điểm (≤ 2.000 điểm/chuỗi/biểu đồ), LTTB cho gauge, min/max envelope từ aggregate | Đo: tổng ngày 950 chuỗi raw 310 ms vs `agg_1h` 7 ms; `DISTINCT ON` latest 8,4 s vs bảng 0,13 ms | [PROPOSAL], [FACT – đo trong lab] | NFR-DATA-015, NFR-PERF-001/002 |
| D-17-06 | Backup vật lý bằng **pgBackRest** (dự phòng: WAL-G), 2 repo: repo1 cùng vùng, repo2 khác vùng có **object lock**; full tuần + differential ngày + WAL liên tục; PITR theo cụm (ctl-db 35 ngày, mon-db 14 ngày) | RPO/RTO 10 §16.2; WAL của cụm chuỗi thời gian rất lớn | [PROPOSAL] | NFR-REL-005, NFR-DATA-017/018 |
| D-17-07 | Diễn tập khôi phục **tự động hằng tháng** (restore → truy vấn kiểm tra → hủy) cộng diễn tập PITR đầy đủ hằng quý (10 §16.3) | "Backup chưa restore thử thì chưa có" | [PROPOSAL] | NFR-DATA-019 |
| D-17-08 | Job: policy trong DB cho nén/CAGG/retention (đường A) hoặc `pg_partman` + `pg_cron` (đường E); job nghiệp vụ (watermark, KPI ngày, báo cáo, export, DQ) trong **app scheduler có khóa phân tán** (JobRunr hoặc Quartz cluster); backup/verify/drill là **k8s CronJob** | Tách theo nơi chạy và quyền | [PROPOSAL] | §10 |
| D-17-09 | Quan sát dữ liệu: completeness/freshness theo site tính từ `agg_5m.n` (không quét raw), SLO dữ liệu, kiểm tra hợp đồng dữ liệu trong CI | "Hiểu dữ liệu" phải đo được | [PROPOSAL] | NFR-DATA-020/021, NFR-OBS-007 |

### 1.3 Yêu cầu phi chức năng mới (đánh số tiếp NFR-DATA-013 của 04 §6.3)

| Mã | Tên | Tiêu chí | Ưu tiên | Kiểm chứng |
|---|---|---|---|---|
| NFR-DATA-014 | Khóa gọn cho chuỗi | Bảng chuỗi thời gian chỉ chứa `series_id int4` + `ts`; không cột text định danh; không index `ts` riêng trên hypertable (`create_default_indexes => false`) | P0 | Review schema; test kích thước ≤ 150 B/hàng chưa nén |
| NFR-DATA-015 | Ngân sách truy vấn | API chuỗi trả ≤ 2.000 điểm/chuỗi/yêu cầu; ≤ 8 chuỗi/panel; dashboard L1/L2 không truy vấn bảng raw (kiểm bằng `pg_stat_statements` theo role); `statement_timeout` 5 s cho API tương tác, 30 s cho báo cáo trên replica | P0 | Test tải + truy vấn `pg_stat_statements` |
| NFR-DATA-016 | Lưu trữ lạnh có kiểm | Raw và `agg_5m` xuất Parquet theo tháng; **không drop chunk/partition nào** trước khi manifest (đếm hàng + checksum theo chuỗi-ngày) khớp DB | P0 (đường E), P1 (đường A) | Test job + kiểm manifest |
| NFR-DATA-017 | Backup bất biến, mã hóa | Bản backup và WAL mã hóa (AES-256, khóa KMS riêng); ít nhất một bản ở vùng khác có object lock ≥ thời gian PITR; credential production không xóa được backup (10 §16.3) | P0 (mã hóa, tách tài khoản), P1 (object lock, chờ Q-44) | Kiểm cấu hình + thử xóa bằng credential prod |
| NFR-DATA-018 | Tuổi backup | Cảnh báo khi: WAL archive trễ > 5 phút; full > 8 ngày; diff > 26 h; repo2 trễ > 24 h | P0 | Metric + alert |
| NFR-DATA-019 | Diễn tập khôi phục | Restore tự động hằng tháng vào môi trường tách, chạy bộ truy vấn kiểm (§8.7), ghi RTO đo được; lỗi → sự cố mức Cao | P0 (sau site pilot đầu tiên) | Biên bản job |
| NFR-DATA-020 | Completeness và freshness | Completeness ngày D của site ≥ 99,5% khi edge online (tính D+1 sau watermark); p99 `ts_ingest − ts` ≤ 120 s cho C2 (bổ sung NFR-PERF-003 p95 ≤ 60 s) | P1 (SLO chính thức), P0 (đo) | Bảng `dq_site_day` |
| NFR-DATA-021 | Hợp đồng dữ liệu trong CI | Mọi thay đổi payload, point registry, hàm tổng hợp chạy bộ test hợp đồng (schema, golden dataset, bẫy avg-of-avg, rollover) trên đúng phiên bản PostgreSQL/TimescaleDB của production | P0 | Pipeline CI |
| NFR-DATA-022 | Xóa theo hợp đồng và legal hold | Xóa dữ liệu tenant theo hợp đồng trong ≤ 30 ngày sau offboarding ở DB và archive; bản trong backup hết hạn theo vòng backup; `legal_hold` chặn mọi job xóa của phạm vi bị giữ | P1 | Test offboarding |
| NFR-DATA-023 | Đo dung lượng theo tenant | Hằng tháng tính GB theo tenant/tầng (raw, aggregate, archive, export) để showback và phát hiện tăng bất thường (> 30%/tháng) | P1 | Báo cáo job |

### 1.4 Xung đột và chỗ khác với tài liệu khác

| # | Chỗ | Nội dung | Cách xử lý trong 17 |
|---|---|---|---|
| C-17-01 | Đề bài nêu "hot raw 30–90 ngày" ↔ NFR-DATA-008/FR-HIST-011 "raw 13 tháng" | Hai con số không cùng nghĩa | Đường A: 7 ngày chưa nén + 13 tháng nén trong DB (đủ NFR-DATA-008). Đường E: 35–90 ngày trong DB + phần còn lại ở Parquet — **cần PO xác nhận "raw 13 tháng" được phép nằm ở archive truy vấn chậm** (Q-63) |
| C-17-02 | F §3.1.3, 05 §19, 06 bảng định cỡ giả định nén **5 B/hàng** | Đo: đủ cột 16,9; gọn 6,5; mượt 2,1 | Dùng **10 B/hàng** làm kế hoạch, bỏ cột không cần (§4.4). 05/06 nên cập nhật khi tổng hợp (X-F2-03) |
| C-17-03 | 05 §19 giả định `agg_5m` ~20 B/hàng nén | Đo 24,5 B/hàng | 5 năm `agg_5m` ở 1.000 site ≈ 12,9 TB (không phải 10,5) |
| C-17-04 | 10 §16.3: base backup **hằng ngày**, PITR 35 ngày, bản tháng giữ 13 tháng, diễn tập quý | WAL cụm chuỗi thời gian ≈ 29 TB/35 ngày ở 1.000 site (thô) | Giữ 35 ngày cho ctl-db và dữ liệu cấu hình; mon-db 14 ngày + Parquet làm bản dài hạn; full tuần + diff ngày; diễn tập tháng (tự động) **và** quý (đầy đủ). Cần 10 xác nhận (Q-64) |
| C-17-05 | 06 §14: `statement_timeout` API ví dụ 30 s | Dashboard cần nhanh, truy vấn 30 s là lỗi thiết kế | 5 s cho API tương tác; 30 s cho báo cáo/export trên replica |
| C-17-06 | FR-HIST-010: raw ≤ 7 ngày, 5 phút ≤ 93 ngày, ngày cho dài hơn | Là **giới hạn tối đa**; 17 thêm quy tắc chọn **mặc định** theo ngân sách điểm | Tương thích; mặc định thô hơn, người dùng "phóng to" tới giới hạn FR-HIST-010 |
| C-17-07 | PoC `infra/db/init.sql`: khóa text, view `latest_value` dùng `DISTINCT ON`, Timescale `license=apache` | Không phải lỗi PoC, nhưng không mở rộng được | Danh sách sửa ở §12 (không sửa ở đây) |

---

<a id="s2"></a>
## 2. Bản đồ dữ liệu (data inventory)

Quy ước cột: **SoT** = nguồn sự thật (source of truth). **Ghi** = tốc độ ghi ở site tham chiếu (05 §19). **Biến đổi** = append-only hay cập nhật được, có dữ liệu trễ không. **Đọc** = ai đọc, tần suất, khoảng thời gian, độ phân giải. **Pháp lý** ghi `[UNKNOWN]` khi chưa kiểm chứng. Tất cả là `[PROPOSAL]` trừ chỗ ghi khác.

### 2.1 Raw telemetry theo lớp thiết bị

Tần suất theo lớp C1–C5 của [07 §6.5](07-device-integration.md). Số điểm theo site tham chiếu F §3.1.1 (≈ 1.000 điểm). "Edge" = đọc và giữ cục bộ (vòng 1 s, 7 ngày); "Cloud" = gửi lên (tổng hợp tại nguồn avg/min/max/n).

| Lớp thiết bị | SL × điểm | Lớp điểm chính | Edge | Cloud | Hàng cloud/ngày (ước) | Ghi chú |
|---|---|---|---|---|---|---|
| Công tơ POC (`MTR_POC`) | 1 × 40 | C1: P/Q tổng + pha (~10); C4: A+/A−/R+/R− (4–8); C2 còn lại | 1 s | 5 s (C1), 60 s (C2, C4) | ≈ 0,22 M | C1 là đầu vào zero-export và Pmax; thanh ghi là nguồn tính tiền |
| Inverter PV | 10 × 60 | C2: P/Q/U/I AC, MPPT; C3: nhiệt độ, string ít biến động; C4: `e_total`; C5: alarm word, trạng thái | 1–5 s | 60 s / 300 s | ≈ 0,75 M | String-level chiếm phần lớn điểm |
| PCS | 1 × 40 | C1: P, setpoint, giới hạn; C2 còn lại; C4: E sạc/xả | 1 s | 5 s / 60 s | ≈ 0,2 M | |
| BMS (hệ + rack) | 1 × 70 | C1: SOC, CCL/DCL; C2: U/I/T min-max; C3: SOH | 1 s; cell-level chỉ ở edge | 5 s / 60 s / 300 s | ≈ 0,25 M | `retention_class = EDGE_ONLY` cho cell (05 §7) |
| Trạm khí tượng | 1 × 8 | C2: G_POA, GHI, T | 1–5 s | 60 s | ≈ 0,01 M | Bắt buộc cho PR |
| Submeter | 5 × 20 | C2 + C4 | 1–5 s | 60 s | ≈ 0,14 M | |
| Trụ sạc EV (OCPP) | 2 × 15 | C2: P, trạng thái; C4: E phiên (không đơn điệu giữa phiên) | theo MeterValues | 60 s | ≈ 0,04 M | Phiên EV có `id_tag_hash` → PII gián tiếp |
| Edge controller | 1 × 30 | C1: setpoint gửi, P cho phép; C2: sức khỏe (`clock_offset_ms`, `buffer_fill_pct`) | 1 s | 5 s / 60 s | ≈ 0,15 M | Bằng chứng audit điều khiển |
| **Tổng site tham chiếu** | ≈ 1.000 điểm | 10% C1, ~70% C2, ~15% C3, ~5% C4 | 86,4 M mẫu/ngày (chỉ edge) | — | **≈ 2,85–3,02 M** | 3,02 M là con số chuẩn của F/05; 2,85 M là phân lớp chi tiết §3.2 |

| Thuộc tính | Raw telemetry (`ts_gauge`, `ts_register`, `ts_state`) |
|---|---|
| SoT | Thiết bị → edge (giá trị, `ts`, quality điểm). Cloud là bản sao có `ts_ingest`. Dữ liệu 1 s chỉ có ở edge 7 ngày |
| Ghi | 35 mẫu/s/site; ≈ 35.000/s ở 1.000 site; đỉnh backfill 5–10× (NFR-PERF-004) |
| Biến đổi | Append-only theo `(series_id, ts)`; **có dữ liệu trễ** (backfill ≤ 7 ngày là bình thường, 07 §6.10); trùng khác giá trị → giữ `rev` cao hơn + audit (FR-HIST-002). Thanh ghi không bao giờ sửa, chỉ thêm `DataCorrection` lớp riêng |
| Đọc | UI-12 chẩn đoán (kỹ sư, hiếm, ≤ 1 ngày, raw); UI-13 trend explorer (≤ 7 ngày raw theo FR-HIST-010); job tổng hợp (mỗi 5 phút, cửa sổ refresh); job interval energy (mỗi 5 phút); forensic bundle (10 §18.4, hiếm) |
| Retention | 13 tháng (NFR-DATA-008); archive Parquet theo hợp đồng |
| Pháp lý | Bằng chứng tranh chấp hóa đơn/bảo hành; thời hạn pháp định cho dữ liệu đo đếm C&I `[UNKNOWN]` (Q-08, Q-F09) |
| PII | Không trực tiếp. Gián tiếp: profile tải có thể suy ra hoạt động của doanh nghiệp/hộ (INFERENCE); coi là dữ liệu mật của khách |

### 2.2 Các lớp dữ liệu khác

| Lớp dữ liệu | SoT | Ghi (site tham chiếu) | Biến đổi | Người đọc và mẫu truy cập | Retention | Pháp lý / hợp đồng | PII |
|---|---|---|---|---|---|---|---|
| `IntervalEnergy` (Δ 5 phút từ thanh ghi) | Cloud calc từ `ts_register` (máy trạng thái FR-HIST-004) | ~50 chuỗi × 288 = 14,4 k hàng/ngày | Cập nhật được khi tính lại (`calc_version`, cờ `REVISED`) | Hóa đơn bóng, Pmax, báo cáo R1–R3, UI-03/UI-10 cột kWh; đọc theo ngày/tháng | 5 năm (LONG_5M); bản trong báo cáo phát hành theo snapshot | Căn cứ tính tiền ESCO/PPA: nếu khách dùng làm chứng từ kế toán thì ≥ 10 năm theo Luật Kế toán (INFERENCE từ nguồn thứ cấp, §14 W17) | Không |
| `agg_5m`, `agg_1h` | Dẫn xuất từ raw (CAGG hoặc job) | 288 k + 24 k hàng/ngày | Tính lại khi dữ liệu trễ (trong cửa sổ refresh tự động; ngoài cửa sổ qua `dirty_bucket`) | UI-03, UI-05, UI-07/09/10, UI-13 (> 6 h), UI-01 (qua KPI), API đọc; 5 phút: tuần–3 tháng; 1 h: tháng–năm | 5 phút 5 năm (D-06 a); 1 h vòng đời | — | Không |
| `agg_15m/30m` (demand), `DemandWindow` | Job từ `IntervalEnergy` | 48–96 hàng/ngày | Tính lại | Pmax, hóa đơn bóng | 5 năm | Như IntervalEnergy | Không |
| `agg_day_local`, `agg_month_local`, `KpiValue` | Job sau watermark (FR-HIST-005) | ~1 k hàng/ngày | Cập nhật khi dirty; khi đã phát hành báo cáo → restatement | UI-01, UI-03, R1–R8, so sánh năm | Vòng đời dự án | Số đã phát hành bất biến (NFR-DATA-007) | Không |
| `latest_value` | Ingest (chỉ tiến theo `ts`) | 1 lần ghi/chuỗi/chu kỳ | Ghi đè | UI-01..UI-07 live, SSE, planner snapshot; đọc rất nhiều | Không lưu lịch sử; snapshot vào DB 60 s (06 §11) | — | Không |
| Event, Alarm, AlarmTransition, Ticket | Edge (event) / cloud alarm-worker | ~500 event + ~20 alarm/ngày | Event append-only; alarm có vòng đời trạng thái | UI-14/15/16, thông báo, báo cáo O&M; lọc 7–90 ngày | ≥ 5 năm (F §3.10) | Bằng chứng bảo hành/SLA O&M | Người ack (actor_id) |
| DispatchCommand + transition + ack, CommandApproval | ctl-db (control plane) | ~100 lệnh × 5 chuyển/ngày | Append-only (transition); `last_state` là bản chiếu | UI-21/22/23, điều tra INC; đọc theo lệnh, 30 ngày | Online ≥ 13 tháng + WORM ≥ 5 năm (NFR-DATA-009) | Bằng chứng điều khiển, tranh chấp; hợp đồng tới 10 năm (K R-25) | `actor_id`, IP |
| AuditEvent | ctl-db/audit, hash chain theo tenant | ~300 sự kiện/ngày | **Append-only tuyệt đối** (10 §7.3) | UI-33, điều tra, kiểm toán | Như trên | Hash chain + neo WORM (P1) | Có (actor, IP, user agent) |
| DispatchPlan, PlanSlot, PlanSlotResult, input snapshot | ctl-db | 60 KB/ngày (tầng 2) – 2,8 MB/ngày (MPC) | Phiên bản, bất biến sau phát hành | UI-19/20, đánh giá tối ưu | Bản đã chạy như audit; bản bị thay: tóm tắt + hash 30 ngày | Tái lập (NFR-DATA-006) | Không |
| Forecast (`issue_time × valid_time`) | opt-worker / nhà cung cấp | ~9,2 k hàng/ngày | Append-only theo `issue_time` | UI-37, planner, đánh giá dự báo | 2 năm đầy đủ, sau đó chỉ day-ahead | Điều khoản phân phối lại của nhà cung cấp dự báo `[UNKNOWN]` (Q-F05) | Không |
| Tariff, TOU, SOE, SiteGridConfig, EdgeConfigVersion, point mapping, `series` | mon-db core / ctl-db, **có phiên bản** | Thấp | Không sửa phiên bản cũ; thêm phiên bản `valid_from` | Mọi phép tính, UI-25/28/29 | Vòng đời site; mọi phiên bản giữ | Cấu hình edge ≥ 5 năm (10 §16.3) | Không |
| ReportSnapshot (PDF/XLSX), restatement | Object storage | ~0,12 GB/site/năm | Bất biến; restatement là bản mới | UI-30, email | ≥ 5 năm (F §3.14) | Có thể là chứng từ thanh toán → xem 10 năm (Q-66) | Tên người nhận |
| ExportJob + file | Object storage | Theo yêu cầu | File tạm | UI-30 | File 7 ngày; bản ghi job như audit | Xuất là hành động có audit | Người yêu cầu |
| Archive Parquet (raw + 5 phút) | Object storage | ≈ 15 MB/site/ngày raw | Ghi một lần mỗi tháng; viết lại khi restatement ngoài cửa sổ DB | Job DuckDB, xuất toàn tenant (NFR-DATA-012), DR | Theo hợp đồng (mặc định vòng đời) | Bản thứ hai độc lập với backup | Không |
| Log/metric/trace của nền tảng | Loki/Prometheus/OTel (06) | Phụ thuộc lưu lượng | Append-only | SRE, điều tra | Log 30–90 ngày; metric 13 tháng downsample (PROPOSAL); log edge ≥ 30 ngày (NFR-OBS-009) | NĐ 53/2022 có điều khoản nhật ký hệ thống; áp cho ta không `[UNKNOWN]` | Có thể (IP, user id) → không ghi PII thô (NFR-OBS-003) |
| Trạng thái broker (session, retained, queue) | Broker | — | Thay đổi liên tục | Broker | Không backup dữ liệu; backup **cấu hình** broker (ACL, listener) như mã | Mất session → edge kết nối lại, buffer + ack-sau-commit giữ dữ liệu (07 §6.12) | Không |
| Bí mật, khóa | Vault/KMS (10 §8) | — | Xoay vòng | Dịch vụ | Theo KMS | **Không** nằm trong backup DB; backup của vault theo quy trình riêng | — |

[INFERENCE] Nhóm chiếm dung lượng là raw telemetry và `agg_5m`; mọi lớp khác cộng lại < 1 TB/năm ở 1.000 site (05 §19). Vì vậy kế hoạch tập trung vào hai lớp đó, còn các lớp nhỏ được giữ lâu với chi phí không đáng kể.

---

<a id="s3"></a>
## 3. Ước tính dung lượng

### 3.1 Công thức

```
rows_site_day = Σ_class  N_points(class) × 86 400 / period_s(class) × (1 − r_rbe(class))
bytes_tier    = rows × B_row(tier)                       (B_row đo ở §3.3)
WAL_day       ≈ rows_day × B_wal                          (B_wal = 276 B/hàng, đo)
DB_steady     = hot_days × rows_day × B_unc  +  (raw_days − hot_days) × rows_day × B_comp
              + agg5_days × rows5_day × B_agg5_comp + Σ(agg ≥ 1 h)
```

- `N_points(class)`: theo phối trộn tài sản (§2.1). `period_s`: C1 5, C2 60, C3 300, C4 60. `r_rbe`: tỷ lệ bỏ nhờ deadband/report-by-exception (§4); mặc định 0 khi tính dung lượng (thận trọng).
- Index đã nằm trong `B_row` (PK `(series_id, ts)`; hypertable còn index `ts` mặc định trong số 144 B).
- Không gồm: bản sao HA (×2 cho primary + standby, ×3 nếu có replica đọc), WAL archive, backup.

### 3.2 Điểm theo phối trộn tài sản

| Hồ sơ site | Điểm | C1 (5 s) | C2 (60 s) | C3 (300 s) | C4 (60 s) | Hàng cloud/ngày | Tỷ trọng C1 |
|---|---|---|---|---|---|---|---|
| Nhỏ: chỉ PV + công tơ | 200 | 10 | 160 | 20 | 10 | 0,42 M | 41% |
| Tham chiếu (F §3.1.1) | 1.000 | 100 | 700 | 150 | 50 | **2,85 M** | **61%** |
| Tham chiếu theo giả định F/05 (10% @5 s, 90% @60 s) | 1.000 | 100 | 900 | — | — | **3,02 M** | 57% |
| Lớn: nhiều BESS, nhiều inverter | 5.000 | 400 | 3.600 | 800 | 200 | 12,6 M | 55% |

[INFERENCE — tính toán] **Thứ chi phối dung lượng là số điểm C1 ở 5 s**: 10% số điểm sinh ~60% số hàng. Đưa P/Q từng pha của công tơ POC và các điểm BMS ít dùng từ C1 xuống C2 là đòn bẩy lớn nhất (§4). Đội bảng dưới dùng 3,02 M (để khớp 05/06/15); hồ sơ hỗn hợp 60% nhỏ / 35% tham chiếu / 5% lớn cho trung bình ≈ 1,9 M hàng/site/ngày (≈ 0,63×).

### 3.3 Byte/hàng đo được `[FACT – đo trong lab]` (chi tiết: [F2 §4](notes/F2-data-lifecycle-lab.md))

| Tầng | B/hàng | Ghi chú |
|---|---|---|
| Raw, layout PoC khóa text | 291 | Heap 189 + index 102 |
| Raw, `series_id`, bảng thường + PK | 133 | Đường E (partition thuần) |
| Raw, hypertable chưa nén (PK + index `ts` mặc định) | 144 | Đường A, 7 ngày đầu |
| Raw nén, đủ cột 05 §7 (nhiễu độc lập) | 16,9 | Trường hợp xấu |
| Raw nén, `v_avg/v_min/v_max/n/quality` | 11,3 | |
| Raw nén, chỉ `v_avg/quality` | 6,5 | |
| Raw nén, tín hiệu mượt/lượng tử thô | 2,1 | Trường hợp tốt |
| **Raw nén — số kế hoạch** | **10** | [PROPOSAL] sau khi bỏ `ts_ingest`/`v_last` theo hàng (§4.4) |
| Thanh ghi int8 nén | 2,0 | Chưa nén 110 |
| `agg_5m` chưa nén / nén | 150 / 24,5 | Partial ghép được 10 cột |
| `agg_1h` chưa nén / nén (ước như 5m) | 148 / ~25 | |
| Parquet ZSTD-3 (raw, sắp `series_id, ts`) | 5,1 | ZSTD-9: 4,55; Snappy: 13,9 |
| WAL khi ingest | 276 | Gồm full-page write sau checkpoint |

### 3.4 Bảng dung lượng theo quy mô (3,02 M hàng/site/ngày; tháng = 30,4 ngày)

| Tầng | 100 site · ngày | 100 · tháng | 100 · năm | 1.000 · ngày | 1.000 · tháng | 1.000 · năm | 10.000 · ngày | 10.000 · tháng | 10.000 · năm |
|---|---|---|---|---|---|---|---|---|---|
| Raw chưa nén (hypertable, 144 B) | 43,5 GB | 1,3 TB | 15,9 TB | 435 GB | 13,2 TB | 158,7 TB | 4,3 TB | 132 TB | 1,6 PB |
| Raw heap PG thuần (133 B) | 40,2 GB | 1,2 TB | 14,7 TB | 402 GB | 12,2 TB | 146,6 TB | 4,0 TB | 122 TB | 1,5 PB |
| Raw layout PoC khóa text (291 B) | 87,9 GB | 2,7 TB | 32,1 TB | 879 GB | 26,7 TB | 320,8 TB | 8,8 TB | 267 TB | 3,2 PB |
| **Raw nén – kế hoạch (10 B)** | 3,0 GB | 92 GB | **1,1 TB** | 30,2 GB | 918 GB | **11,0 TB** | 302 GB | 9,2 TB | **110 TB** |
| Raw nén – dải đo (2,1–16,9 B) | 0,6–5,1 GB | 19–155 GB | 0,23–1,9 TB | 6,3–51 GB | 0,19–1,6 TB | 2,3–18,6 TB | 63–510 GB | 1,9–15,5 TB | 23–186 TB |
| Raw Parquet ZSTD (5,1 B) | 1,5 GB | 47 GB | 0,56 TB | 15,4 GB | 468 GB | 5,6 TB | 154 GB | 4,7 TB | 56 TB |
| `agg_5m` chưa nén (150 B) | 4,3 GB | 131 GB | 1,6 TB | 43,2 GB | 1,3 TB | 15,8 TB | 432 GB | 13,1 TB | 158 TB |
| `agg_5m` nén (24,5 B) | 0,7 GB | 21,5 GB | 258 GB | 7,1 GB | 215 GB | 2,6 TB | 70,6 GB | 2,1 TB | 25,8 TB |
| `agg_1h` nén (~25 B) | 60 MB | 1,8 GB | 22 GB | 0,6 GB | 18 GB | 219 GB | 6 GB | 182 GB | 2,2 TB |
| WAL sinh ra (276 B, trước nén) | 83 GB | 2,5 TB | 30 TB | 834 GB | 25,3 TB | 304 TB | 8,3 TB | 253 TB | 3,0 PB |
| Ngày/tháng, KPI, event, lệnh, audit, plan (05 §19) | — | — | < 0,1 TB | — | — | < 1 TB | — | — | < 10 TB |

Nhãn: byte/hàng `[FACT – đo trong lab]`; phép nhân và áp vào dữ liệu thật `[INFERENCE]`.

**Trạng thái ổn định trong DB (đường A, 1.000 site, chưa nhân HA)**: raw chưa nén 7 ngày ≈ 3,0 TB + raw nén 7 ngày–13 tháng ≈ 11,7 TB + `agg_5m` nén 5 năm ≈ 12,9 TB + `agg_1h` ≈ 0,22 TB/năm + phần nhỏ ≈ 1 TB → **≈ 29 TB sau 5 năm** (05 §19 ước 18–20 TB với giả định 5 B và 20 B). Nếu D-06 đổi sang (b) "sau 13 tháng chỉ giữ LONG_5M" (5% chuỗi), `agg_5m` (13 tháng mọi chuỗi + LONG_5M tới 5 năm) giảm còn ≈ 3,3 TB → tổng ≈ 20 TB.

**Đường E (PostgreSQL thuần, không nén)**: 13 tháng raw ≈ 159 TB ở 1.000 site → không khả thi; 35 ngày ≈ 14,1 TB, 90 ngày ≈ 36,1 TB; ở 100 site 90 ngày ≈ 3,6 TB (khả thi cho MVP). `agg_5m` 5 năm không nén ≈ 79 TB → phải giữ 5 phút cho LONG_5M hoặc chuyển sang Parquet.

### 3.5 Độ nhạy theo tần suất cloud (1.000 site × 1.000 điểm, mọi điểm cùng tần suất)

| Tần suất cloud | Hàng/site/ngày | Mẫu/s toàn hệ | Raw chưa nén/ngày | Raw nén/năm (10 B) | WAL/ngày |
|---|---|---|---|---|---|
| 1 s | 86,4 M | 1.000.000 | 12,4 TB | 315 TB | 23,8 TB |
| 5 s | 17,3 M | 200.000 | 2,5 TB | 63 TB | 4,8 TB |
| 60 s | 1,44 M | 16.667 | 207 GB | 5,3 TB | 397 GB |
| Hỗn hợp chuẩn (10% 5 s, 90% 60 s) | 3,02 M | 34.954 | 435 GB | 11,0 TB | 834 GB |
| Hỗn hợp chi tiết §3.2 | 2,85 M | 33.000 | 410 GB | 10,4 TB | 787 GB |

Deadband/report-by-exception (RBE) cho C2/C3: giảm số hàng 30% hoặc 60% trên phần C2+C3 → hàng/site/ngày từ 2,85 M còn ≈ 2,53 M (−11%) hoặc ≈ 2,22 M (−22%) vì C1 không áp RBE. [INFERENCE] Mức giảm **byte sau nén** nhỏ hơn mức giảm hàng: giá trị không đổi vốn đã nén rất tốt (đo: tín hiệu mượt 2,1 B/hàng). RBE chủ yếu tiết kiệm CPU ingest, WAL, băng thông 4G và chỗ trong buffer edge. Tỷ lệ thật trên dữ liệu site: `[UNKNOWN]` (Q-E-13).

### 3.6 Edge (nhắc lại 07 §6.7, không đổi)

Vòng 1 s 7 ngày: 1,8–4,8 GB/site tham chiếu; buffer tần suất cloud ≈ 45 MB/ngày → 7 ngày ≈ 0,32 GB, 30 ngày ≈ 1,36 GB. Ổ edge ≥ 32 GB (site tham chiếu). Buffer này là **một phần của câu chuyện RPO** (§8.2).

---

<a id="s4"></a>
## 4. Giảm dữ liệu tại nguồn

### 4.1 Nguyên tắc

1. **Tổng hợp tại nguồn, không lấy mẫu thưa** (F §3.1.2): edge gửi avg/min/max/n của cửa sổ; không gửi giá trị tức thời mỗi 60 s (mất gai).
2. **Điểm không cần lên cloud thì không lên**: cell-level BMS, thanh ghi chẩn đoán → `EDGE_ONLY`, tải lên theo yêu cầu (burst/forensic).
3. **Deadband chỉ cho gauge chậm và trạng thái**, luôn có **heartbeat** (gửi lại dù không đổi) để phân biệt "không đổi" với "mất dữ liệu".
4. **Không bao giờ giảm**: thanh ghi điện năng C4 (đọc ở mọi biên 5 phút), sự kiện/alarm C5, lệnh và ack, `edge.*` sức khỏe khi ở trạng thái lỗi, điểm của `MTR_POC` dùng cho zero-export/Pmax, setpoint đọc lại.

### 4.2 Chính sách theo lớp điểm `[PROPOSAL]`

| Lớp điểm | Ví dụ | Cửa sổ gửi | Deadband / RBE | Heartbeat (gửi tối thiểu) | Không được giảm khi |
|---|---|---|---|---|---|
| C1 điều khiển | `meter.p` (POC), `ess.p`, `ess.soc`, CCL/DCL | 5 s | Không | — | Luôn |
| C2 công suất/dòng/áp | `pv_inverter.p`, `meter.u_l1` | 60 s | Bỏ cửa sổ nếu \|avg − avg_gửi_cuối\| < 0,5% định mức **và** min/max cùng nằm trong dải | 15 phút | Thiết bị đang có alarm; burst mode |
| C2 nhiệt độ, khí tượng chậm | `t_cabinet`, `t_ambient` | 60 s | 0,5 °C | 15 phút | — |
| C3 chậm | SOH, cấu hình, string ít biến động | 300 s | 1 LSB / 0,5% | 60 phút | — |
| Trạng thái/enum/bitset | `pv_inverter.state`, `ess.mode` | Khi đổi (change-of-value) | Bất kỳ thay đổi | 15 phút (gửi lại trạng thái hiện tại) | Luôn gửi mọi lần đổi, kể cả lật nhanh |
| Thanh ghi C4 | `meter.e_import`, `e_total` | 60 s + ngay sau biên 5 phút | **Không** | — | Luôn |
| Sự kiện C5 | alarm, ack, `run_mode` | Tức thời | **Không** | — | Luôn; QoS 1 |
| Setpoint/giới hạn hiện hành | `p_limit_pct` | Khi đổi + 60 s | Không | 60 s | Luôn (bằng chứng điều khiển) |

Hệ quả cho tổng hợp: chuỗi có RBE phải tính trung bình **theo thời gian** (LOCF, `time_weight`), không trung bình mẫu (F §3.4). `max_age_s` của chuỗi = heartbeat × 1,5; quá hạn → `UNCERTAIN_STALE`, UI hiển thị khoảng trống.

### 4.3 Lớp tần suất và burst

- Mặc định mỗi điểm thuộc **một** lớp do driver khai báo (`sampling_class` trong point mapping, PoC `infra/config/site.yaml` đã có). Đổi lớp là đổi cấu hình có phiên bản.
- **Burst mode** (F-MON-12, P1): khi người vận hành mở UI live hoặc có sự cố, cloud yêu cầu C1/C2 ở 1 s trong N phút (mặc định 15). Dữ liệu burst ghi vào bảng riêng `ts_burst` retention 30 ngày, không vào `ts_gauge`, để không làm "bẩn" thống kê completeness và không phình raw 13 tháng.

### 4.4 Gọn bảng (giảm byte/hàng) `[PROPOSAL]`, căn cứ đo F2 §4.2

| Thay đổi | Lợi ích đo/ước | Đánh đổi |
|---|---|---|
| Bỏ `ts_ingest` mỗi hàng; giữ ở `telemetry_batch` (khóa `(edge_id, stream, seq)`) kèm `batch_id` | Bớt một cột timestamp gần như ngẫu nhiên; một phần chênh 16,9 → 11,3 B/hàng | Độ trễ ingest đo theo lô (đủ cho NFR-PERF-003) |
| C2: bỏ `v_last` (giữ cho C1 và trạng thái) | Bớt một cột float8 nhiễu | `last` của bucket lấy từ `v_avg` của cửa sổ cuối |
| `v_min/v_max` dạng `float4` (đã có) | — | Đủ cho min/max hiển thị |
| `window_s`, `covered_ms`: chỉ ghi khi khác mặc định của chuỗi (NULL = mặc định) | Nén gần 0 | Logic đọc phải thay NULL bằng mặc định |
| Không tạo index `ts` mặc định trên hypertable | −11 B/hàng chưa nén | Truy vấn "mọi chuỗi trong khoảng thời gian" dựa vào chunk exclusion (đủ) |
| Khóa `series_id int4` | −54% chưa nén | Cần bảng `series` + cache ánh xạ ở ingest |

### 4.5 Gộp lô trên đường truyền

Lô MQTT 1–5 nghìn điểm, mã hóa nhị phân + zstd (≤ 15 B/mẫu, F-P04); ingest ghi một transaction/lô bằng `COPY` vào bảng tạm rồi `INSERT … ON CONFLICT` (06 §9 bước 6). Ack sau commit (07 §7.1, PoC đã làm).

---

<a id="s5"></a>
## 5. Phân tầng lưu trữ và retention

### 5.1 Các tầng

| Tầng | Nội dung | Nơi | Định dạng | Thời gian | Truy cập |
|---|---|---|---|---|---|
| T0 Edge | 1 s vòng tròn; buffer cloud-rate | SSD edge | Nhị phân nén | 7 ngày / ≥ 30 ngày mục tiêu | Burst, forensic, backfill |
| T1a Raw nóng | Raw 0–7 ngày | mon-db | Hypertable chưa nén, chunk 1 ngày | 7 ngày | Mọi truy vấn chi tiết; nhận backfill |
| T1b Raw ấm | Raw 7 ngày–13 tháng | mon-db | Chunk nén (segmentby `series_id`) | đến 13 tháng | Trend explorer, chẩn đoán, tính lại |
| T2 Tổng hợp ấm | `agg_5m`, `IntervalEnergy`, demand | mon-db | CAGG/hypertable, nén sau 45 ngày | 5 năm | Dashboard, báo cáo |
| T3 Tổng hợp dài hạn | `agg_1h`, ngày, tháng, KPI | mon-db | CAGG/bảng thường | Vòng đời | Mọi màn hình dài hạn |
| T4 Lưu trữ lạnh | Raw + `agg_5m` + interval energy | Object storage S3-compatible | Parquet ZSTD, partition `tenant/site/năm/tháng` | Theo hợp đồng (mặc định vòng đời) | Job DuckDB, xuất tenant, DR |
| T5 Bằng chứng | Audit, lệnh, plan đã chạy | ctl-db + WORM | Bảng partition tháng + neo Merkle | Online 13 tháng, WORM ≥ 5 năm | Kiểm toán |

### 5.2 Bảng chính sách retention `[PROPOSAL]`

| Dữ liệu | Đường A (TSL) | Đường E (PG thuần) | Archive Parquet | Legal hold | Xóa khi offboarding |
|---|---|---|---|---|---|
| Raw gauge/register/state | Chưa nén 7 ngày; nén tới 13 tháng; drop chunk khi > 13 tháng **và** manifest tháng đã verify | Partition ngày; giữ 35 ngày (≤ 200 site: 90 ngày); detach → export → verify → drop | Từ D+35 sau cuối tháng; giữ theo hợp đồng | Chặn drop chunk chứa dữ liệu tenant bị giữ: xuất riêng phạm vi bị giữ sang prefix `hold/` có object lock trước khi drop | DELETE theo `series_id` (lô nhỏ, giờ thấp điểm) + xóa prefix archive |
| `ts_burst` | 30 ngày | 30 ngày | Không (trừ khi ghim forensic) | Ghim theo NFR-OBS-009 | Như trên |
| `agg_5m` | 5 năm; nén sau 45 ngày | Bảng partition tháng; 13 tháng mọi chuỗi, 5 năm cho `LONG_5M` | Theo tháng | Như raw | Như raw |
| `IntervalEnergy`, demand | 5 năm (LONG_5M) | 5 năm | Theo tháng | Bắt buộc khi có tranh chấp hóa đơn | Sau thời hạn hợp đồng/kế toán |
| `agg_1h`, ngày, tháng, KPI | Vòng đời | Vòng đời | Hằng năm (bản sao) | — | Theo hợp đồng |
| Event/alarm/ticket | ≥ 5 năm, partition tháng | như A | Hằng năm | Có | Ẩn danh actor |
| Lệnh, audit, plan đã chạy | Online 13 tháng + WORM ≥ 5 năm (hợp đồng tới 10 năm) | như A | WORM | Có | **Không xóa audit**; ẩn danh hóa `User` (10 §7.2) |
| Report snapshot | ≥ 5 năm (10 năm nếu là chứng từ thanh toán, Q-66) | như A | Đã ở object storage | Có | Theo hợp đồng |
| Export file | 7 ngày | 7 ngày | — | — | — |
| Forecast | 2 năm đầy đủ, sau đó day-ahead | như A | Hằng năm | — | Theo hợp đồng |
| Log nền tảng | 30 ngày nóng, 90 ngày lạnh (PROPOSAL; pháp lý `[UNKNOWN]`) | — | — | Có (điều tra) | — |

Quy tắc xóa: (1) không job nào xóa dữ liệu nếu phạm vi có `legal_hold` hiệu lực; (2) xóa raw không xóa bằng chứng đã chụp trong `ReportSnapshot` (05 §19); (3) mọi lần drop/delete ghi `AuditEvent` (role riêng `retention_job`, 10 §7.3).

### 5.3 SQL — đường A (TimescaleDB 2.17, cú pháp `compress_*`)

```sql
-- 1. Raw gauge (05 §7, rút gọn theo §4.4)
CREATE TABLE ts.ts_gauge (
  series_id  int4        NOT NULL,
  ts         timestamptz NOT NULL,            -- đầu cửa sổ nguồn [ts, ts+window)
  v_avg      float8, v_min float4, v_max float4,
  n          int2, window_s int2, covered_ms int4,   -- NULL = mặc định của series
  quality    int4        NOT NULL,
  batch_id   bigint      NOT NULL,            -- → ingest.telemetry_batch (ts_ingest ở đó)
  PRIMARY KEY (series_id, ts)
);
SELECT create_hypertable('ts.ts_gauge', by_range('ts', INTERVAL '1 day'), create_default_indexes => false);
ALTER TABLE ts.ts_gauge SET (timescaledb.compress,
  timescaledb.compress_segmentby = 'series_id', timescaledb.compress_orderby = 'ts');
SELECT add_compression_policy('ts.ts_gauge', compress_after => INTERVAL '7 days');
-- KHÔNG dùng add_retention_policy cho raw: drop phải chờ manifest Parquet (job ops.drop_archived_chunks, §5.5)

-- 2. CAGG 5 phút: partial ghép được (F §3.4); real-time bật (đuôi ≤ vài phút đọc từ raw)
CREATE MATERIALIZED VIEW agg.agg_5m WITH (timescaledb.continuous, timescaledb.materialized_only = false) AS
SELECT series_id, time_bucket(INTERVAL '5 minutes', ts) AS bucket_start,
       sum(v_avg * coalesce(window_s, 60)) AS integral, sum(coalesce(window_s, 60)) AS covered_s,
       min(v_min) AS v_min, max(v_max) AS v_max,
       first(v_avg, ts) AS v_first, last(v_avg, ts) AS v_last,
       count(*) AS n, bit_or(quality) AS quality_or
FROM ts.ts_gauge GROUP BY series_id, bucket_start WITH NO DATA;
SELECT add_continuous_aggregate_policy('agg.agg_5m',
  start_offset => INTERVAL '8 days', end_offset => INTERVAL '5 minutes', schedule_interval => INTERVAL '5 minutes');
ALTER MATERIALIZED VIEW agg.agg_5m SET (timescaledb.compress = true);
SELECT add_compression_policy('agg.agg_5m', compress_after => INTERVAL '45 days');   -- > start_offset (bẫy đo ở F2 §4.4)
SELECT add_retention_policy('agg.agg_5m', drop_after => INTERVAL '5 years');          -- sau khi archive tháng đã verify (job kiểm trước)

-- 3. CAGG 1 giờ phân cấp, chỉ đọc phần đã vật chất hóa
CREATE MATERIALIZED VIEW agg.agg_1h WITH (timescaledb.continuous, timescaledb.materialized_only = true) AS
SELECT series_id, time_bucket(INTERVAL '1 hour', bucket_start) AS bucket_start,
       sum(integral) AS integral, sum(covered_s) AS covered_s, min(v_min) AS v_min, max(v_max) AS v_max,
       first(v_first, bucket_start) AS v_first, last(v_last, bucket_start) AS v_last,
       sum(n) AS n, bit_or(quality_or) AS quality_or
FROM agg.agg_5m GROUP BY series_id, 2 WITH NO DATA;
SELECT add_continuous_aggregate_policy('agg.agg_1h',
  start_offset => INTERVAL '9 days', end_offset => INTERVAL '1 hour', schedule_interval => INTERVAL '30 minutes');

-- 4. Thanh ghi: không CAGG; IntervalEnergy do job máy trạng thái ghi (FR-HIST-004)
CREATE TABLE ts.ts_register (series_id int4 NOT NULL, ts timestamptz NOT NULL, raw int8 NOT NULL,
  quality int4 NOT NULL, batch_id bigint NOT NULL, PRIMARY KEY (series_id, ts));
SELECT create_hypertable('ts.ts_register', by_range('ts', INTERVAL '1 day'), create_default_indexes => false);
ALTER TABLE ts.ts_register SET (timescaledb.compress, timescaledb.compress_segmentby = 'series_id', timescaledb.compress_orderby = 'ts');
SELECT add_compression_policy('ts.ts_register', compress_after => INTERVAL '7 days');

-- 5. Theo dõi job nền của TimescaleDB
SELECT job_id, application_name, last_run_status, last_run_duration, next_start, total_failures
FROM timescaledb_information.job_stats ORDER BY last_run_status, job_id;
```

Lưu ý `[FACT]`: từ 2.13 CAGG mới mặc định **tắt** real-time aggregation; đặt `materialized_only` tường minh để không phụ thuộc phiên bản (§14 W10). `start_offset` của refresh phải nhỏ hơn retention raw (W10). Cú pháp `enable_columnstore`/`add_columnstore_policy` chỉ có từ 2.18 (W11); PoC đang 2.17.2.

Lựa chọn real-time [PROPOSAL]: `agg_5m` bật vì UI-03 hiển thị "hôm nay" tới phút hiện tại; phần real-time chỉ là raw sau bucket vật chất hóa cuối (≤ 10 phút khi refresh đúng hạn). `agg_1h` tắt; UI hiển thị watermark "đã tổng hợp đến …". Nếu job refresh trễ, phần real-time phình ra → alert khi `now − watermark_cagg > 15 phút`.

### 5.4 SQL — đường E (PostgreSQL thuần + `pg_partman` + `pg_cron`)

```sql
CREATE TABLE ts.ts_gauge ( ...cùng cột... , PRIMARY KEY (series_id, ts) ) PARTITION BY RANGE (ts);
SELECT partman.create_parent(p_parent_table => 'ts.ts_gauge', p_control => 'ts', p_interval => '1 day', p_premake => 7);
UPDATE partman.part_config
   SET retention = '35 days', retention_keep_table = true, retention_schema = 'ts_detached', infinite_time_partitions = true
 WHERE parent_table = 'ts.ts_gauge';
-- BRIN tùy chọn cho quét theo thời gian trên partition (ingest theo thời gian → correlation cao)
CREATE INDEX ON ts.ts_gauge USING brin (ts) WITH (pages_per_range = 32);

-- Bảng tổng hợp do job ghi (không CAGG)
CREATE TABLE agg.agg_5m (series_id int4, bucket_start timestamptz, integral float8, covered_s int4,
  v_min float4, v_max float4, v_first float8, v_last float8, n int4, quality_or int4,
  PRIMARY KEY (series_id, bucket_start)) PARTITION BY RANGE (bucket_start);
SELECT partman.create_parent(p_parent_table => 'agg.agg_5m', p_control => 'bucket_start', p_interval => '1 month', p_premake => 2);

CREATE TABLE agg.refresh_state (name text PRIMARY KEY, done_until timestamptz NOT NULL);

CREATE OR REPLACE PROCEDURE agg.refresh_5m() LANGUAGE plpgsql AS $$
DECLARE v_from timestamptz; v_to timestamptz := date_bin('5 minutes', now() - interval '5 minutes', timestamptz '2000-01-01');
BEGIN
  SELECT done_until INTO v_from FROM agg.refresh_state WHERE name = 'agg_5m' FOR UPDATE;
  -- (a) dải mới + (b) các dirty bucket đang chờ (gộp theo giờ), cùng một câu upsert
  WITH ranges AS (
      SELECT v_from AS f, v_to AS t
      UNION ALL
      SELECT bucket_start, bucket_end FROM calc.dirty_bucket WHERE status = 'PENDING' AND reason = 'LATE_DATA'
  )
  INSERT INTO agg.agg_5m
  SELECT g.series_id, date_bin('5 minutes', g.ts, timestamptz '2000-01-01'),
         sum(g.v_avg * coalesce(g.window_s, 60)), sum(coalesce(g.window_s, 60)), min(g.v_min), max(g.v_max),
         (array_agg(g.v_avg ORDER BY g.ts))[1], (array_agg(g.v_avg ORDER BY g.ts DESC))[1], count(*), bit_or(g.quality)
  FROM ts.ts_gauge g JOIN ranges r ON g.ts >= r.f AND g.ts < r.t
  GROUP BY 1, 2
  ON CONFLICT (series_id, bucket_start) DO UPDATE SET integral = excluded.integral, covered_s = excluded.covered_s,
     v_min = excluded.v_min, v_max = excluded.v_max, v_first = excluded.v_first, v_last = excluded.v_last,
     n = excluded.n, quality_or = excluded.quality_or;
  UPDATE calc.dirty_bucket SET status = 'DONE', processed_at = now() WHERE status = 'PENDING' AND reason = 'LATE_DATA';
  UPDATE agg.refresh_state SET done_until = v_to WHERE name = 'agg_5m';
END $$;

SELECT cron.schedule('agg_5m_refresh', '*/5 * * * *', 'CALL agg.refresh_5m()');
SELECT cron.schedule('partman_maint', '7 * * * *', 'CALL partman.run_maintenance_proc()');
SELECT cron.schedule('cron_history_purge', '15 3 * * *', $$DELETE FROM cron.job_run_details WHERE end_time < now() - interval '14 days'$$);
```

Lưu ý `[FACT]`: `pg_partman` chuyển bảng hết hạn sang `retention_schema` (ghi đè `retention_keep_table`) và detach không `CONCURRENTLY` trong `run_maintenance_proc()`; drop lỗi khi có FK phụ thuộc → bảng chuỗi không có FK (§14 W9). `cron.job_run_details` không tự dọn (W15). Câu `dirty_bucket` trên là phác thảo: production phải khóa hàng (`FOR UPDATE SKIP LOCKED`) và giới hạn số bucket mỗi lần.

Vòng đời partition đường E: `run_maintenance_proc` tạo trước 7 ngày → hết 35 ngày chuyển sang `ts_detached` → job `archive_export` xuất Parquet partition đó → job `archive_verify` so manifest → job `detached_drop` `DROP TABLE ts_detached.ts_gauge_pYYYYMMDD` chỉ khi verify `OK`.

### 5.5 Job drop có điều kiện (đường A)

```sql
CREATE OR REPLACE PROCEDURE ops.drop_archived_chunks(job_id int, config jsonb) LANGUAGE plpgsql AS $$
DECLARE c regclass; r record;
BEGIN
  FOR r IN SELECT chunk_schema, chunk_name, range_end FROM timescaledb_information.chunks
           WHERE hypertable_schema = 'ts' AND hypertable_name = config->>'table'
             AND range_end < now() - (config->>'keep')::interval LOOP
    -- tháng của chunk phải có manifest VERIFIED và không có legal hold chưa xuất
    IF EXISTS (SELECT 1 FROM ops.archive_manifest m
               WHERE m.table_name = config->>'table' AND m.day = (r.range_end - interval '1 day')::date AND m.status = 'VERIFIED')
       AND NOT EXISTS (SELECT 1 FROM ops.legal_hold h WHERE h.active AND h.export_status <> 'EXPORTED'
                       AND tstzrange(h.from_ts, h.to_ts) && tstzrange(r.range_end - interval '1 day', r.range_end)) THEN
      EXECUTE format('DROP TABLE %I.%I', r.chunk_schema, r.chunk_name);   -- drop_chunks theo khoảng cũng được
      INSERT INTO ops.retention_log(table_name, chunk, dropped_at) VALUES (config->>'table', r.chunk_name, now());
    END IF;
  END LOOP;
END $$;
SELECT add_job('ops.drop_archived_chunks', '1 day', config => '{"table":"ts_gauge","keep":"13 months"}');
```

[INFERENCE] `DROP TABLE` trực tiếp trên chunk là cách tối giản; production nên dùng `drop_chunks(older_than, newer_than)` cho đúng catalog. Kiểm trên PoC trước (§12).

### 5.6 Archive Parquet

- Đường dẫn: `s3://ems-archive-<vùng>/v1/<loại>/tenant_id=<t>/site_id=<s>/year=YYYY/month=MM/part-<seq>.parquet` (Hive partitioning, đọc được bằng DuckDB/Spark/Trino).
- Một file/site/tháng/loại; site tham chiếu ≈ 470 MB/tháng raw (5,1 B × 3,02 M × 30,4) — kích thước file tốt cho truy vấn. Site nhỏ ≈ 65 MB/tháng.
- Sắp `(series_id, ts)`, row group 1 M hàng, ZSTD level 3 (đo: 5,09 B/hàng; level 9 chỉ tốt hơn 11%). Kèm `series` snapshot (đơn vị, `agg_rule`, `point_code`) trong cùng prefix để file tự mô tả.
- `manifest.json` mỗi file: số hàng theo `(series_id, ngày)`, `sum(v_avg)` / `sum(raw)` theo chuỗi-ngày, `min/max ts`, `sha256`, phiên bản schema, phiên bản PostgreSQL/TimescaleDB nguồn.
- Mã hóa: SSE với khóa KMS **theo tenant** (crypto-shredding khi offboarding: hủy khóa = xóa mọi bản, kể cả bản sao vùng khác) `[PROPOSAL]`.
- Đây là **bản sao thứ hai, độc lập với backup PostgreSQL**: lỗi logic làm hỏng backup (ví dụ phiên bản TimescaleDB không khớp) không làm mất raw lịch sử.

---

<a id="s6"></a>
## 6. Dữ liệu trễ, sai thứ tự và tính lại

### 6.1 Watermark `complete_until`

- Theo stream: ingest đã có `contig[(edge, stream)]` = seq cao nhất không lỗ (PoC `ingest.py`). `complete_until(stream)` = `batch_ts` lớn nhất của lô ≤ seq liên tục đó.
- Theo site: `complete_until(site) = min` trên mọi stream của mọi edge của site; edge OFFLINE giữ watermark đứng yên (không tiến khi không biết).
- Lưu `calc.watermark(site_id, stream, complete_until, updated_at)` (05 §7); cập nhật mỗi lần ack.
- Dùng: UI hiển thị "dữ liệu đầy đủ đến …"; job ngày/KPI/báo cáo chỉ chạy cho ngày địa phương D khi `complete_until(site) ≥ cuối ngày D` hoặc quá hạn chờ (06:00 hôm sau, F §3.14) — khi đó đánh dấu `PARTIAL`.

### 6.2 Phân loại dữ liệu đến

| Trường hợp | Nhận biết | Đường A | Đường E |
|---|---|---|---|
| Đúng hạn (`ts ≥ complete_until − 10 phút`) | Bình thường | Upsert vào chunk chưa nén; CAGG refresh kế tiếp | Upsert; `refresh_5m` lần sau |
| Trễ ≤ 7 ngày (backfill sau mất mạng) | `via_backfill` hoặc `ts < complete_until` | Upsert vào chunk **chưa nén** (vì `compress_after = 7 ngày`); CAGG tự ghi invalidation, refresh trong `start_offset = 8 ngày` | Upsert; ghi `dirty_bucket(site, giờ)` |
| Trễ > 7 ngày hoặc rơi vào chunk đã nén | `ts < now − 7 ngày` | Ghi `calc.late_landing`; job `late_merge` gộp theo chunk ngoài giờ cao điểm (đặt `max_tuples_decompressed_per_dml_transaction` cho phiên job), rồi `refresh_continuous_aggregate` cho khoảng đó | Ghi thẳng vào partition nếu còn trong DB; nếu partition đã detach/archive → `late_landing` + viết lại file Parquet tháng (restatement archive) |
| Trùng khác giá trị | Khóa tồn tại, giá trị khác | Giữ `rev` cao hơn + audit (FR-HIST-002) | như A |

Số đo hỗ trợ (F2 §4.6): ghi vào chunk nén ~1,6 k hàng/s, vào chunk chưa nén ≥ 170 k hàng/s. Một site mất mạng 7 ngày backfill ≈ 21 M hàng: vào chunk chưa nén ≈ 2 phút thời gian DB; vào chunk nén ≈ 3,6 giờ. Đó là lý do giữ 7 ngày chưa nén bằng đúng buffer cứng NFR-DATA-001.

### 6.3 Tính lại phía sau

1. `dirty_bucket` gộp theo `(site, giờ)`; reason ∈ `LATE_DATA | ASSET_EVENT | MANUAL_EDIT | TARIFF_CHANGE | EF_CHANGE | CALC_VERSION` (05 §7).
2. Job `recompute` (mỗi 5 phút, app scheduler): IntervalEnergy (máy trạng thái từ `r_start` trước khoảng) → `agg_15m/30m` demand → ngày/tháng địa phương → KPI → kiểm ngưỡng restatement (> 0,5% kWh hoặc mọi thay đổi Pmax, NFR-DATA-007) → thông báo.
3. Mục tiêu ≤ 1 h từ khi dữ liệu tới (NFR-PERF-009). Đo refresh CAGG 1 h cửa sổ trên vùng đã nén: 4,4 s (F2 §4.4).
4. **Giới hạn tầm tính lại**: chỉ tính lại từ raw trong DB (13 tháng đường A; 35 ngày đường E). Xa hơn → job DuckDB đọc Parquet, ghi kết quả vào bảng tạm, rồi upsert tổng hợp; luôn có audit và restatement.

### 6.4 Bộ đếm reset/rollover

- Ingest phát hiện giảm giá trị (PoC đã sinh `COUNTER_RESET`), nhưng **phân loại** ROLLOVER/RESET/thay công tơ thuộc máy trạng thái IntervalEnergy (FR-HIST-004): dùng `R_wrap` của driver, chống rung ±2 LSB, `AssetEvent` thay công tơ.
- `IntervalEnergy` tính lại cho khoảng bị ảnh hưởng khi `AssetEvent` được nhập muộn (reason `ASSET_EVENT`).
- Không dùng `counter_agg` của Toolkit làm nguồn tính tiền (F Phát hiện #5).

### 6.5 Backfill sau mất mạng diện rộng

- Edge xả theo giới hạn tốc độ (30% băng thông, jitter, 07 §6.7); broker giảm ưu tiên `backfill` trước (NFR-REL-016).
- Ingest dùng pool kết nối riêng cho backfill; job CAGG vẫn chạy (refresh chỉ phần invalidated).
- Ví dụ 1.000 site mất 1 ngày: 3 tỷ hàng; ở 100 k hàng/s dư địa → ≈ 8,4 h để đuổi kịp; NFR-PERF-004 yêu cầu 5–10× tải thường (175–350 k/s) → 2,4–4,8 h. `[INFERENCE]`, đo ở PoC-01.

---

<a id="s7"></a>
## 7. Giảm tải truy vấn

### 7.1 Nguyên tắc

1. **Đọc đúng tầng**: live → `latest_value` (Valkey + bảng snapshot); biểu đồ → aggregate theo ngân sách điểm; số liệu kỳ → bảng KPI tính sẵn; raw chỉ cho UI-12/UI-13 phóng to và job.
2. **Một luồng đẩy, nhiều người xem**: ingest ghi `latest_value` và publish thay đổi theo site; mỗi instance mon-app giữ **một** subscription/site đang có người xem và fan-out SSE (06 ADR-03). Không có polling DB theo người dùng.
3. **Ngân sách điểm**: ≤ 2.000 điểm/chuỗi/biểu đồ (≈ số pixel ngang của biểu đồ rộng), ≤ 8 chuỗi/panel (NFR-PERF-002).
4. **Kết quả kỳ đã đóng là bất biến** → cache dài, vô hiệu hóa bằng sự kiện (dirty bucket / restatement), không theo TTL ngắn.

### 7.2 Chọn độ phân giải theo khoảng (mặc định; người dùng phóng to tới giới hạn FR-HIST-010)

| Khoảng hiển thị | Nguồn mặc định | Hàng đọc/chuỗi (tối đa) | Xử lý trước khi trả |
|---|---|---|---|
| ≤ 6 h | Raw (C1 5 s, C2 60 s) | 4.320 | LTTB → ≤ 2.000 điểm (gauge); trạng thái: giữ mọi lần đổi |
| 6 h – 3 ngày | `agg_5m` (C1); raw 60 s nếu ≤ 33 h cho C2 | 864 | Trả avg + dải min/max (envelope) |
| 3 ngày – 93 ngày | `agg_1h` | 2.232 | avg + min/max |
| > 93 ngày | `agg_day_local` | 3.650 (10 năm) | Cột ngày/tháng |
| Năng lượng (kWh) mọi khoảng | `IntervalEnergy` → 15 phút / giờ / ngày / tháng theo khoảng | ≤ 2.000 cột | **Không LTTB**; cộng tổng theo bucket |
| Pmax / demand | `DemandWindow` | — | max + thời điểm |

LTTB (Largest-Triangle-Three-Buckets, Steinarsson 2013, §14 W8) giữ hình dạng nhưng có thể bỏ cực trị hẹp; vì vậy với tầng aggregate trả **envelope min/max** thay cho LTTB, và LTTB chỉ áp cho raw. Đo: 8 chuỗi × 7 ngày raw 80.640 hàng đọc trong 8,3 ms (F2 §4.5), nên LTTB phía server từ raw ≤ 7 ngày là khả thi; chi phí chính là mạng và trình duyệt.

### 7.3 Ngân sách truy vấn theo màn hình (UI theo [09](09-ux-ui-specification.html))

| Màn hình | Truy vấn khi mở | Nguồn | Mục tiêu p95 | Ghi chú |
|---|---|---|---|---|
| UI-01 Tổng quan danh mục | 1 truy vấn KPI hôm nay/tháng cho ≤ 500 site + 1 đọc trạng thái | `kpi_site_day` + Valkey `site_status` | ≤ 3 s (NFR-PERF-001), mục tiêu DB ≤ 200 ms | Không sparkline từ raw; sparkline 24 h từ `agg_1h` (24 điểm/site) |
| UI-03 Dashboard site | ≤ 6 truy vấn: latest (cache), hôm nay `agg_5m` real-time (≤ 6 chuỗi), kWh hôm nay `IntervalEnergy`, KPI tháng | Cache + aggregate | ≤ 2 s | Live qua SSE mỗi 5 s |
| UI-04/05/07/09/10 Chi tiết tài sản | latest + 24 h `agg_5m` cho ≤ 8 chuỗi | Cache + `agg_5m` | ≤ 2 s | |
| UI-12 Chẩn đoán | raw ≤ 1 h–1 ngày, 1 thiết bị | Raw | ≤ 3 s | Role kỹ sư; giới hạn 1 ngày |
| UI-13 Trend explorer | ≤ 8 chuỗi × khoảng tùy chọn | Theo §7.2 | ≤ 3 s (NFR-PERF-002) | Hiển thị "Độ phân giải: …" (09) |
| UI-14 Console cảnh báo | Lọc alarm 10.000 dòng | Bảng alarm (index theo `site, state, raised_at`) | ≤ 2 s | Phân trang keyset, không `OFFSET` lớn, không `count(*)` chính xác |
| UI-20 Thực tế so với kế hoạch | PlanSlotResult + `agg_15m` | Aggregate | ≤ 2 s | |
| UI-30 Báo cáo/xuất | Snapshot có sẵn; xuất > 100 k hàng → job | Object storage / replica | Link ≤ 30 s (NFR-PERF-011) | Job async |
| API đọc công khai (P1) | ≤ 10.000 điểm/yêu cầu | Theo §7.2 | ≤ 1 s (NFR-PERF-012) | Rate limit theo tenant |

### 7.4 Loại truy vấn → tầng → độ trễ → TTL cache

| Loại truy vấn | Tầng nguồn | Độ trễ kỳ vọng (DB) | TTL cache | Khóa cache |
|---|---|---|---|---|
| Giá trị hiện tại | Valkey `latest_value` | < 5 ms (đo bảng PG: 0,13 ms cho 950 chuỗi) | Đẩy (SSE), không TTL | — |
| Biểu đồ hôm nay (5 phút) | `agg_5m` real-time | 3–10 ms/8 chuỗi (đo 2,9 ms cho 7 ngày) | 60 s | `tenant:series_hash:5m:from:to:wm` |
| Biểu đồ quá khứ đã đóng | `agg_5m` / `agg_1h` | 2–10 ms | 24 h, xóa khi dirty | thêm `calc_version` |
| KPI ngày/tháng | `kpi_site_day/month` | < 10 ms | Tới khi `KPI_RECOMPUTED` | `tenant:site:kpi:period:calc_version` |
| Tổng ngày nhiều chuỗi | `agg_1h` (không raw) | 7 ms (raw: 310 ms, đo) | 5 phút | |
| Raw chi tiết ≤ 1 ngày | Raw | 1–20 ms | 30 s (hôm nay), 24 h (đã đóng) | |
| Báo cáo định kỳ | Snapshot object storage | — | Bất biến | `report_id:version` |
| Xuất lớn, phân tích ad hoc | Replica đọc / Parquet (DuckDB) | phút | — | Job |

Khóa cache luôn chứa `tenant_id` (chống rò chéo tenant) và `wm` = watermark hoặc phiên bản tổng hợp, để dữ liệu trễ tự làm khóa cũ hết hiệu lực. Cache ở tầng ứng dụng (Valkey), không cache kết quả trong trình duyệt quá 60 s.

### 7.5 Rào chắn (guardrails)

- `statement_timeout`: 5 s role `app_api`; 30 s `app_report` (replica); 0 cho job có giới hạn riêng. `idle_in_transaction_session_timeout` 60 s. `lock_timeout` 5 s cho job DDL.
- Giới hạn khoảng theo tầng (FR-HIST-010); số chuỗi ≤ 8/panel, ≤ 50/yêu cầu API; xuất đồng bộ ≤ 100.000 hàng (NFR-PERF-011), lớn hơn → job ghi object storage, link ký 7 ngày, có audit.
- Hạn mức đồng thời theo tenant (ví dụ ≤ 4 truy vấn trend nặng/tenant) và rate limit API.
- Replica đọc cho báo cáo, planner (`planner_ro`), xuất và phân tích; primary chỉ phục vụ ingest + UI tương tác.
- `pg_stat_statements` + review tuần top-20 theo tổng thời gian; cảnh báo khi một role `app_api` đọc bảng `ts.*` (vi phạm NFR-DATA-015).
- Không `count(*)` chính xác trên hypertable cho UI; dùng `approximate_row_count()` hoặc số đếm duy trì sẵn. (Đo: 15 ms trên 20,7 M hàng đã nén nhờ metadata, nhưng trên chunk chưa nén là quét toàn bộ.)

### 7.6 Index và phân vùng

| Bảng | Index | Lý do |
|---|---|---|
| Raw (chunk chưa nén) | PK B-tree `(series_id, ts)` | Truy vấn luôn theo chuỗi + khoảng; đo PK 31,5 B/hàng |
| Raw (chunk nén) | Metadata segment theo `series_id` + min/max `ts` | Tự có khi `segmentby series_id, orderby ts` |
| Raw đường E | PK + BRIN `(ts)` `pages_per_range=32` | BRIN 287 KB vs B-tree 149 MB trên 20,7 M hàng (đo), chỉ hiệu quả khi thứ tự vật lý theo `ts` (correlation > 0,9, W13); lab nạp theo chuỗi nên correlation −0,01 → không tỉa được |
| `agg_*` | PK `(series_id, bucket_start)` | |
| `series` | `(site_id)`, `(asset_id)`, `(tenant_id)` | Dịch `site → series_id[]` một lần, cache ở app |
| Alarm/event | `(site_id, raised_at DESC)`, partial `WHERE state <> 'CLOSED'` | Console cảnh báo |

Phân vùng theo thời gian (chunk/partition 1 ngày) → truy vấn có điều kiện `ts` chỉ chạm chunk liên quan (chunk exclusion / partition pruning). Luôn truyền khoảng thời gian **hằng** vào truy vấn (không `now() − x` trong view lồng) để planner tỉa lúc lập kế hoạch `[INFERENCE]`.

### 7.7 Bảng KPI tính sẵn

`kpi_site_day(site_id, local_date, e_pv_kwh, e_imp_kwh, e_exp_kwh, e_chg_kwh, e_dis_kwh, self_consumption_pct, pmax_kw, pmax_at, availability_pct, coverage_pct, quality, calc_version)` và `kpi_site_month`, `kpi_portfolio_day(tenant_id, local_date, …)`. Ghi bởi job KPI ngày (D+1 sau watermark), cập nhật bởi `recompute`. UI-01 và báo cáo chỉ đọc các bảng này.

---

<a id="s8"></a>
## 8. Backup và DR

### 8.1 Cái gì được backup

| Thành phần | Cách | Ghi chú |
|---|---|---|
| ctl-db (lệnh, audit, plan, SOE, cấu hình) | pgBackRest vật lý + WAL liên tục; replica đồng bộ | RPO ≈ 0 (10 §16.2) |
| mon-db (metadata core + chuỗi thời gian + aggregate) | pgBackRest vật lý + WAL liên tục | Gồm chunk nén và CAGG (CAGG không tái tạo được từ raw đã xóa, W4) |
| Logical dump schema `core`, `ops`, tariff | `pg_dump -Fc` hằng ngày, giữ 13 tháng | Nhỏ; khôi phục chọn lọc cấu hình mà không restore cả cụm |
| Object storage (report, archive Parquet, export) | Sao chép sang vùng khác (replication) + versioning; archive có object lock | Archive Parquet là bản thứ hai cho raw |
| Cấu hình broker, ACL, Grafana, IaC, point registry đã phát hành | Git (hạ tầng như mã) | Không backup trạng thái phiên broker |
| Trạng thái broker (session, queue) | **Không** | Edge buffer + ack-sau-commit bù (07 §6.12) |
| Secrets/KMS | **Không trong backup DB**; quy trình riêng của Vault/KMS (10 §8) | Khóa giải mã backup ở KMS tách tài khoản |
| Edge | Cấu hình đã ký ở cloud; dữ liệu edge = buffer | Edge thay thế được bằng cấu hình |

### 8.2 RPO/RTO (giữ đúng 10 §16.2)

| Dữ liệu | RPO | RTO | Cơ chế trong 17 |
|---|---|---|---|
| Cấu hình, SOE, quyền | ≤ 5 phút | ≤ 4 h | WAL async `archive_timeout = 60 s` + replica; PITR |
| Lệnh + audit | ≤ 1 phút (≈ 0) | ≤ 4 h | Replica đồng bộ + WAL; edge giữ bản sao audit cục bộ ≥ 30 ngày |
| Timeseries nóng | ≤ 15 phút (thực tế ≈ 0 trong cửa sổ buffer edge) | ≤ 8 h, **dữ liệu mới trước** | WAL + **backfill từ buffer edge 7 ngày** |
| Timeseries lạnh (Parquet) | ≤ 24 h | ≤ 72 h | Sao chép vùng khác |

Câu chuyện RPO của chuỗi thời gian: dữ liệu chưa được ack vẫn nằm trong buffer edge; dữ liệu đã ack nhưng mất do sự cố DB được **gửi lại** nếu cloud hạ `ack_seq` (quy trình `RESEND_REQUEST`, 07 §6.10) trong vòng 7 ngày. Vì vậy sau restore PITR về thời điểm T, job `post_restore_resync` yêu cầu mọi edge gửi lại từ `seq` tương ứng `T − 15 phút`. `[PROPOSAL]`

### 8.3 So sánh công cụ

| Tiêu chí | pgBackRest | WAL-G | Barman | Snapshot đĩa/managed |
|---|---|---|---|---|
| Kiểu | Vật lý, full/diff/incr, block-level incremental (theo nguồn thứ cấp) | Vật lý, delta backup, Go, hướng object storage | Vật lý, quản lý tập trung nhiều server, incremental dựa rsync | Snapshot khối |
| Nén/mã hóa | lz4/zstd/gzip; AES-256 phía client | Nén có; mã hóa `[UNKNOWN]` trong nguồn đã thấy | `[UNKNOWN]` trong nguồn đã thấy | Theo nhà cung cấp |
| Nhiều repo | Có (repo1, repo2), WAL archive vào mọi repo | Một đích/lần (INFERENCE) | Có server backup trung tâm | — |
| Restore song song | Có (`process-max`) | Có | Có | Nhanh nhưng cùng hệ lưu trữ |
| Hợp với ta | **Chọn**: 2 repo khác vùng, mã hóa tích hợp, retention full/diff rõ | Dự phòng nếu R-62 xảy ra | Khi có nhiều cụm DB tự quản | Chỉ bổ sung; không thay backup có WAL; nhà cung cấp VN chưa rõ (Q-44) |
| Nguồn | §14 W5, W7 | W5 | W5 | — |

Rủi ro: một nguồn 2026 nói người duy trì pgBackRest từng tuyên bố ngừng duy trì rồi được tài trợ lại (W6, chưa kiểm chứng) → R-62.

### 8.4 Lịch và lưu giữ backup `[PROPOSAL]`

| Cụm | Full | Differential | Incremental | WAL | PITR | Bản dài hạn |
|---|---|---|---|---|---|---|
| ctl-db | CN 02:00 (giờ VN) | Hằng ngày 02:00 | 6 h/lần | Liên tục, `archive-async`, `archive_timeout=60s` | 35 ngày (10 §16.3) | Full đầu tháng giữ 13 tháng; audit WORM ≥ 5 năm (riêng) |
| mon-db | CN 01:00 | Hằng ngày 01:00 | — | Liên tục, `archive-async` | **14 ngày** (C-17-04) | Full đầu tháng giữ 3 tháng; dài hạn dựa Parquet + logical dump core 13 tháng |

Cấu hình mẫu (`/etc/pgbackrest/pgbackrest.conf`, rút gọn):

```ini
[global]
repo1-type=s3
repo1-s3-bucket=ems-pgbackrest-hn
repo1-path=/mon-db
repo1-retention-full=2
repo1-retention-diff=7
repo1-cipher-type=aes-256-cbc
repo1-bundle=y
repo1-block=y
repo2-type=s3
repo2-s3-bucket=ems-pgbackrest-hcm-lock      # vùng khác, bucket bật object lock
repo2-path=/mon-db
repo2-retention-full=3
repo2-cipher-type=aes-256-cbc
compress-type=zst
compress-level=3
process-max=8
archive-async=y
spool-path=/var/spool/pgbackrest
start-fast=y

[mon-db]
pg1-path=/var/lib/postgresql/16/main
```

Tham số PostgreSQL liên quan: `archive_mode=on`, `archive_command='pgbackrest --stanza=mon-db archive-push %p'`, `archive_timeout=60`, `wal_compression=zstd` (PG 15+, giảm full-page write) `[INFERENCE: hiệu quả trên WAL của ta chưa đo]`. Tên tùy chọn phải đối chiếu đúng phiên bản pgBackRest dùng (W7).

**Khối lượng backup ước tính (mon-db, 1.000 site)** `[INFERENCE]`: full ≈ 15–29 TB (theo năm vận hành); diff hằng ngày nhỏ vì chunk nén cũ **không đổi** — chủ yếu là 1 ngày raw chưa nén (≈ 435 GB) + chunk mới nén + aggregate; WAL thô 834 GB/ngày, sau nén zstd giả định 3–5× → ≈ 170–280 GB/ngày → 14 ngày ≈ 2,3–3,9 TB, 35 ngày ≈ 5,8–9,7 TB. Tỷ lệ nén WAL `[UNKNOWN]` (chưa đo).

### 8.5 Mã hóa, ngoài vùng, bất biến

- Mã hóa phía client của pgBackRest (khóa trong KMS/Vault, xoay năm), cộng SSE của object storage.
- repo2 ở vùng khác (NFR-REL-006 P1); bucket **object lock chế độ compliance** với thời hạn ≥ PITR + 7 ngày; không gỡ được kể cả tài khoản quản trị (W12). Thử chế độ governance trước vì compliance không đảo ngược được (W12).
- Tài khoản/credential ghi backup tách khỏi production; credential production chỉ có quyền `PutObject`, không `DeleteObject` (10 §16.3, ABU-15).
- Nhà cung cấp tại VN có object lock không: `[UNKNOWN]` (Q-44). Phương án tạm: repo2 trên máy chủ backup tách mạng, chỉ kéo (pull) từ primary.

### 8.6 Lưu ý riêng TimescaleDB

- **Backup vật lý (pgBackRest/WAL-G) là đường chính**: sao chép nguyên catalog TimescaleDB, chunk nén, CAGG. Khôi phục vào máy có **cùng phiên bản** PostgreSQL major và cùng phiên bản extension TimescaleDB (INFERENCE từ cách backup vật lý hoạt động; quy tắc chi tiết `[UNKNOWN]`, W1).
- Logical (`pg_dump`) chỉ cho di trú/xuất: phải `CREATE EXTENSION timescaledb` cùng phiên bản, gọi `timescaledb_pre_restore()`, `pg_restore` **không dùng `-j`**, rồi `timescaledb_post_restore()`; ghi lại phiên bản PostgreSQL và TimescaleDB với mỗi dump (W1, W2). Dump hypertable nén không cần giải nén trước (W1). Có báo cáo lỗi restore liên quan trigger/catalog (W3).
- Nâng cấp TimescaleDB: chạy restore drill với bản backup **trước** nâng cấp và sau nâng cấp; giữ image cũ trong registry ≥ thời hạn PITR.
- Job nền TimescaleDB (nén, CAGG) sau restore: kiểm `timescaledb_information.jobs` và bật lại nếu cần; tránh hai cụm cùng chạy job ghi archive (chặn bằng cờ `ops.cluster_role`).

### 8.7 Runbook khôi phục (rút gọn) `[PROPOSAL]`

1. Tuyên bố sự cố; nếu là ctl-db hoặc failover DR → **kích hoạt kill switch nền tảng trước** (NFR-REL-018, 10 §16.4).
2. Chọn mục tiêu: `--type=time --target="<T>"` (lỗi logic) hoặc latest (mất máy).
3. Dựng máy cùng image (PostgreSQL + TimescaleDB đúng phiên bản ghi trong `backup.info`/manifest).
4. `pgbackrest --stanza=mon-db --delta --process-max=16 restore [--type=time --target=…]`.
5. Khởi động ở chế độ không nhận ghi ứng dụng (`default_transaction_read_only` cho role app) → chạy **bộ truy vấn kiểm** (dưới).
6. Mở ingest; chạy `post_restore_resync` (yêu cầu edge gửi lại từ `seq` ứng với `T − 15 phút`); theo dõi watermark tiến.
7. Kiểm audit hash chain (ctl-db), `seq` sàn Signer, rồi mở control plane theo C3 (10 §16.4).
8. Ghi RTO thực tế, viết biên bản.

**Khôi phục theo bậc khi cụm lớn** `[INFERENCE]`: restore toàn bộ 15–29 TB ở ~0,5–1 GB/s mất 4–16 h, có thể vượt RTO 8 h. Phương án: dựng mon-db mới chỉ với `core` (từ logical dump/PITR cụm nhỏ) + hypertable rỗng, mở ingest và backfill 7 ngày từ edge (monitoring hoạt động lại sớm), song song restore bản vật lý vào máy khác rồi chép chunk lịch sử sang, trong lúc đó lịch sử > 7 ngày đọc từ Parquet (chậm). Cần PoC đo tốc độ restore (Q-65, R-60).

**Bộ truy vấn kiểm sau restore** (cũng dùng cho drill hằng tháng):

```sql
-- 1. Phiên bản
SELECT version(), extversion FROM pg_extension WHERE extname = 'timescaledb';
-- 2. Đếm hàng theo ngày cho 7 ngày đầy đủ gần nhất trước T, so với ops.daily_manifest (ghi mỗi đêm bởi job daily_close)
SELECT d.day, d.row_count AS expected, x.actual, d.row_count = x.actual AS ok
FROM ops.daily_manifest d
JOIN LATERAL (SELECT count(*) AS actual FROM ts.ts_gauge WHERE ts >= d.day AND ts < d.day + 1) x ON true
WHERE d.table_name = 'ts_gauge' AND d.day BETWEEN :t::date - 8 AND :t::date - 1 ORDER BY d.day;
-- 3. Checksum KPI năng lượng ngày (bất biến sau khi đóng kỳ) so với manifest
SELECT k.local_date, md5(string_agg(k.site_id::text || ':' || round(k.e_imp_kwh, 3) || ':' || round(k.e_pv_kwh, 3), ',' ORDER BY k.site_id)) = m.kpi_hash AS ok
FROM agg.kpi_site_day k JOIN ops.daily_manifest m ON m.table_name = 'kpi_site_day' AND m.day = k.local_date
WHERE k.local_date BETWEEN :t::date - 31 AND :t::date - 2 GROUP BY k.local_date, m.kpi_hash;
-- 4. Job TimescaleDB và CAGG
SELECT count(*) FILTER (WHERE last_run_status = 'Failed') AS failed_jobs FROM timescaledb_information.job_stats;
SELECT view_name, materialized_only FROM timescaledb_information.continuous_aggregates;
-- 5. Mẫu truy vấn nghiệp vụ: biểu đồ 8 chuỗi 7 ngày < 3 s
-- 6. ctl-db: kiểm hash chain audit (job có sẵn của 10 §7.3) cho khoảng restore
```

`ops.daily_manifest(table_name, day, row_count, kpi_hash, written_at)` được ghi hằng đêm và **cũng sao chép ra object storage** để drill so với nguồn ngoài DB được khôi phục.

---

<a id="s9"></a>
## 9. Hiểu dữ liệu: quan sát và chất lượng (data observability)

### 9.1 Catalog

- **Point registry là nguồn sự thật**: `PointDefinition` (toàn cục, phiên bản) + `series` (theo tài sản: `kind`, `agg_rule`, `unit`, `sampling_class`, `expected_period_s`, `deadband`, `max_age_s`, `retention_class`) (05 §7). Không chuỗi nào được ingest nếu chưa có `agg_rule` (FR-HIST-001).
- Catalog phát sinh trang tra cứu cho người vận hành (mã điểm, mô tả vi/en, đơn vị, lớp, nguồn, retention, người sở hữu) và xuất kèm mỗi file Parquet.
- Lineage tối thiểu: `series → ts_* → agg_5m → agg_1h → day_local → kpi_* → report_snapshot`, mỗi bước có `calc_version`.

### 9.2 Chỉ số chất lượng theo site

| Chỉ số | Định nghĩa | Nguồn tính (rẻ) | Ngưỡng cảnh báo `[PROPOSAL]` |
|---|---|---|---|
| Freshness | `now − max(ts)` theo site/stream | `latest_value`, `watermark` | > 3 × chu kỳ (C2: 3 phút) khi edge ONLINE |
| Ingest lag | `ts_ingest(batch) − ts` p50/p95/p99 | `telemetry_batch` | p95 > 60 s (NFR-PERF-003) |
| Completeness | Σ `n` nhận / Σ mẫu kỳ vọng (`86 400 / expected_period_s`, trừ chuỗi RBE: tính theo heartbeat) | `agg_5m.n` + `series` | Ngày < 99,5% (NFR-DATA-020) |
| Phân bố quality | % hàng theo origin + bitmask (`SUSPECT`, `OUT_OF_RANGE`, `CLOCK_SUSPECT`, `FROZEN`) | `agg_5m.quality_or` + đếm theo job | SUSPECT > 1%/thiết bị/ngày |
| Lỗ `seq` / `DATA_LOSS` | Số lô thiếu, khoảng mất | `telemetry_batch`, event | Bất kỳ `DATA_LOSS` |
| Đơn điệu bộ đếm | Số ROLLOVER/RESET/RESET_UNEXPLAINED | IntervalEnergy flags | Bất kỳ `RESET_UNEXPLAINED` |
| Cân bằng năng lượng | Residual `P_grid + P_pv + P_bess − P_load` (khi tải đo được) hoặc E_cons âm | `EnergyBalance` 5 phút (FR-HIST-013) | \|residual\| > 3% năng lượng ngày |
| Phép thử dấu | PV P < 0 ban ngày; nhập/xuất đồng thời > 0 cùng 5 phút trên cùng công tơ | `agg_5m` | Bất kỳ, sau commissioning |
| Σ inverter vs công tơ PV | Lệch ngày | `kpi_site_day` | > 3% (F §3.5) |
| Giá trị đóng băng | `v_min = v_max` suốt N giờ ban ngày | `agg_1h` | G_POA đóng băng 2 h giữa trưa |
| Đồng hồ | `edge.clock_offset_ms`, `clock_state` | `latest_value` | `DEGRADED`/`UNSYNCED` |

Phác thảo completeness (đọc `agg_5m`, không quét raw):

```sql
INSERT INTO dq.dq_site_day (site_id, local_date, expected, received, completeness_pct, computed_at)
SELECT s.site_id, :d, sum(86400.0 / s.expected_period_s), sum(a.n_day),
       round(100 * sum(a.n_day) / nullif(sum(86400.0 / s.expected_period_s), 0), 2), now()
FROM core.series s
JOIN LATERAL (SELECT coalesce(sum(n), 0) AS n_day FROM agg.agg_5m
              WHERE series_id = s.series_id AND bucket_start >= :day_start_utc AND bucket_start < :day_end_utc) a ON true
WHERE s.status = 'ACTIVE' AND s.kind = 'gauge' AND s.deadband IS NULL
GROUP BY s.site_id
ON CONFLICT (site_id, local_date) DO UPDATE SET received = excluded.received, completeness_pct = excluded.completeness_pct, computed_at = now();
```

### 9.3 SLO dữ liệu `[PROPOSAL]`

| SLO | Mục tiêu | Cửa sổ | Liên kết |
|---|---|---|---|
| Ingest kịp thời | 99% mẫu C2 truy vấn được ≤ 120 s; 95% ≤ 60 s | 30 ngày | NFR-PERF-003, NFR-DATA-020 |
| Bảo toàn | ≥ 99,9% mẫu tới cloud ≤ 24 h | 30 ngày | NFR-REL-004 |
| Completeness | ≥ 99,5%/site/ngày khi edge online | Ngày | NFR-DATA-020 |
| Tổng hợp kịp | `agg_5m` trễ ≤ 15 phút so với now; KPI ngày xong ≤ 02:00 giờ site | Ngày | NFR-PERF-008 |
| Tính lại | Dirty bucket xử lý ≤ 1 h | Ngày | NFR-PERF-009 |
| Backup | WAL archive trễ ≤ 5 phút; restore drill tháng đạt | Tháng | NFR-DATA-018/019 |

### 9.4 Dashboard cho chính nền tảng dữ liệu (Grafana, PoC đã có)

Ingest: mẫu/s, lô/s, dup rate, lag p95, backfill backlog theo edge. Lưu trữ: kích thước theo tầng và theo tenant, tỷ lệ nén thực tế theo hypertable (`hypertable_compression_stats`), số chunk chưa nén quá hạn. Job: `timescaledb_information.job_stats` / `cron.job_run_details` / JobRunr (thời lượng, lỗi). WAL: byte/giờ, độ trễ archive. Backup: tuổi full/diff, kết quả drill. DQ: completeness, SUSPECT, DATA_LOSS theo site. Truy vấn: top `pg_stat_statements`, vi phạm NFR-DATA-015.

### 9.5 Hợp đồng dữ liệu trong CI (NFR-DATA-021)

1. JSON Schema/Protobuf cho payload `up/telemetry`, `up/backfill`, `up/event` (07 §7.3); test tương thích ngược.
2. Lint point registry: mỗi điểm có `kind`, `unit`, `agg_rule`, `sampling_class`; C4 không có `deadband`; `R_wrap` cho thanh ghi.
3. Golden dataset: chuỗi RBE (bẫy avg-of-avg: 0 kW tại 0 s, 100 kW tại 280 s → 6,7 kW), rollover uint16/uint32, reset, thay công tơ, ngày VN `[D−1 17:00Z, D 17:00Z)`.
4. Test migration trên đúng image PostgreSQL/TimescaleDB production; test restore logical (pre/post restore).
5. Test hiệu năng nhỏ: truy vấn UI-03/UI-13 trên dữ liệu lab 1 site × 7 ngày phải < ngưỡng (phát hiện mất index/đọc nhầm raw).

### 9.6 Sở hữu

| Phạm vi | Chủ sở hữu |
|---|---|
| PointDefinition, `series`, `agg_rule`, job tổng hợp/KPI | Nhóm DATA |
| Point mapping site, commissioning, phép thử dấu | Installer/kỹ sư triển khai (P4) + DATA duyệt |
| Ingest, watermark, late path | Nhóm nền tảng (MON) |
| Backup, restore drill, object lock | SRE |
| Retention, legal hold, offboarding | DATA + PO + Pháp chế |
| Ticket DQ theo site | O&M của tenant (FR-HIST-015) |

---

<a id="s10"></a>
## 10. Danh sách job vận hành

Nơi chạy: **DB-A** = policy/job nền TimescaleDB; **pg_cron** = đường E; **App** = scheduler ứng dụng có khóa phân tán (JobRunr hoặc Quartz cluster trên Spring Boot; `@Scheduled` chỉ khi kèm ShedLock) — `[INFERENCE]` các thư viện là kiến thức nền; **K8s** = CronJob Kubernetes. "Idempotent" nghĩa là chạy lại cùng tham số cho cùng kết quả.

| Job | Mục đích | Lịch (giờ VN) | Nơi chạy | Idempotent | Cảnh báo khi lỗi | Runbook |
|---|---|---|---|---|---|---|
| `compress_raw` | Nén chunk raw > 7 ngày | 1 h/lần | DB-A (`add_compression_policy`) | Có | Chunk chưa nén > 9 ngày | [RB-D01](#rb-d01) |
| `compress_agg5m` | Nén `agg_5m` > 45 ngày | Ngày | DB-A | Có | Như trên | RB-D01 |
| `cagg_refresh_5m` | Refresh `agg_5m` (start 8 ngày, end 5 phút) | 5 phút | DB-A / pg_cron `agg.refresh_5m()` | Có | Watermark CAGG trễ > 15 phút | [RB-D02](#rb-d02) |
| `cagg_refresh_1h` | Refresh `agg_1h` | 30 phút | DB-A / pg_cron | Có | Trễ > 2 h | RB-D02 |
| `interval_energy` | Máy trạng thái thanh ghi → IntervalEnergy 5 phút | 5 phút | App | Có (`calc_version`) | Trễ > 15 phút; `RESET_UNEXPLAINED` | RB-D02 |
| `watermark_update` | `complete_until` theo stream/site | Theo ack + 1 phút | Ingest/App | Có | Watermark đứng yên khi edge ONLINE > 10 phút | RB-D02 |
| `late_merge` | Gộp `late_landing` vào chunk nén theo lô; refresh CAGG khoảng đó | 15 phút; lô lớn 01:00–05:00 | App (gọi SQL) | Có (upsert) | Hàng chờ > 1 h | [RB-D03](#rb-d03) |
| `recompute_dirty` | Dirty bucket → demand → ngày → KPI → restatement | 5 phút | App | Có | Dirty > 1 h (NFR-PERF-009) | RB-D03 |
| `kpi_daily_close` | Ngày địa phương D: `agg_day_local`, `kpi_site_day`, `daily_manifest` | 00:30–02:00 giờ site, chờ watermark ≥ cuối D (tối đa 06:00) | App | Có | Chưa xong 02:00 (NFR-PERF-008) | [RB-D04](#rb-d04) |
| `kpi_monthly_close` | Tháng địa phương + billing period | Ngày 1–2 | App | Có | | RB-D04 |
| `report_generate` | R1–R8 snapshot, gửi | Theo lịch tenant, sau `kpi_daily_close` | App (worker) | Có (`report_version`) | R1 chưa sẵn 06:00 | RB-D04 |
| `retention_raw` | Drop chunk > 13 tháng có manifest VERIFIED, không legal hold | Ngày 03:00 | DB-A (`ops.drop_archived_chunks`) | Có | Chunk quá hạn chưa drop > 7 ngày (thường do archive chưa verify) | [RB-D05](#rb-d05) |
| `retention_agg5m` | Drop `agg_5m` > 5 năm (sau verify) | Tuần | DB-A | Có | | RB-D05 |
| `partition_maintain` | Tạo trước 7 partition, detach hết hạn sang `ts_detached` | Giờ | pg_cron `partman.run_maintenance_proc()` | Có | Thiếu partition tương lai | RB-D05 |
| `archive_export` | Xuất Parquet tháng (A) / partition đã detach (E) | Ngày 5 hằng tháng (A); hằng ngày (E) | K8s (DuckDB/Java Parquet writer, đọc replica) | Có (ghi đè cùng khóa object, version) | Lỗi hoặc > 6 h | [RB-D06](#rb-d06) |
| `archive_verify` | Đọc lại Parquet, so manifest (đếm + checksum chuỗi-ngày) → `VERIFIED` | Sau export | K8s | Có | Lệch bất kỳ | RB-D06 |
| `detached_drop` | Drop bảng trong `ts_detached` khi VERIFIED | Ngày | pg_cron | Có | | RB-D06 |
| `legal_hold_export` | Xuất phạm vi bị giữ sang prefix `hold/` có object lock | Khi tạo hold | App | Có | | RB-D05 |
| `backup_full` | pgBackRest full | CN 01:00 (mon) / 02:00 (ctl) | K8s | Có | Full > 8 ngày | [RB-D07](#rb-d07) |
| `backup_diff` | pgBackRest differential | Hằng ngày | K8s | Có | Diff > 26 h | RB-D07 |
| `backup_incr_ctl` | Incremental ctl-db | 6 h | K8s | Có | | RB-D07 |
| `wal_archive_check` | `pgbackrest check`, tuổi WAL cuối ở repo1/repo2 | 5 phút | K8s / exporter | Có | Trễ > 5 phút (repo1), > 24 h (repo2) | RB-D07 |
| `backup_expire` | `pgbackrest expire` theo retention | Sau full | K8s | Có | | RB-D07 |
| `logical_dump_core` | `pg_dump -Fc` schema core/ops/tariff | Hằng ngày 03:30 | K8s | Có | | RB-D07 |
| `restore_drill` | Restore bản mới nhất vào môi trường tách, chạy bộ kiểm §8.7, ghi RTO, hủy | Tháng (Chủ nhật thứ 2); PITR đầy đủ hằng quý | K8s | Có | Bất kỳ kiểm lệch | [RB-D08](#rb-d08) |
| `vacuum_analyze_hot` | `VACUUM (ANALYZE)` chunk nóng, bảng metadata, outbox | Autovacuum + tối ưu tham số; job đêm cho bảng lớn | DB | Có | `n_dead_tup` cao; nguy cơ wraparound (`age(datfrozenxid)` > 1,0 tỷ) | [RB-D09](#rb-d09) |
| `index_bloat_check` | Ước lượng bloat index/bảng (pgstattuple hoặc truy vấn ước lượng) | Tuần | App / K8s | Có | Bloat > 30% trên bảng > 10 GB | RB-D09 |
| `export_cleanup` | Xóa file export > 7 ngày (lifecycle rule) + bản ghi job | Ngày | Object storage lifecycle + App | Có | | RB-D06 |
| `dq_hourly` | Freshness, lag, `DATA_LOSS`, đóng băng | Giờ | App | Có | Theo §9.2 | [RB-D10](#rb-d10) |
| `dq_daily` | Completeness, cân bằng, phép thử dấu, Σ inverter vs công tơ → ticket DQ | Sau `kpi_daily_close` | App | Có | Theo §9.2 | RB-D10 |
| `audit_chain_verify` | Kiểm hash chain audit | Ngày | App (10 §7.3) | Có | Đứt chuỗi = Khẩn cấp | 10 §7.3 |
| `storage_showback` | GB theo tenant/tầng (NFR-DATA-023) | Tháng | App | Có | Tăng > 30%/tháng | RB-D10 |
| `cron_history_purge` | Dọn `cron.job_run_details`, `job_stats` lịch sử, outbox đã xử lý > 7 ngày | Ngày | pg_cron / App | Có | | — |

### 10.1 Runbook rút gọn

<a id="rb-d01"></a>**RB-D01 Nén trễ.** Kiểm `job_stats` của policy nén; xem khóa (`pg_locks`) với truy vấn dài; chạy `compress_chunk(c)` thủ công cho chunk quá hạn ngoài giờ cao điểm; kiểm đĩa (chunk chưa nén ở 1.000 site ≈ 435 GB/ngày).

<a id="rb-d02"></a>**RB-D02 Tổng hợp/watermark trễ.** Kiểm job refresh lỗi; kiểm `max_tuples_decompressed_per_dml_transaction` nếu lỗi giải nén (CAGG nén trong cửa sổ refresh là cấu hình sai, D-17-04); kiểm ingest lag; UI tự hiển thị watermark nên không sửa tay số liệu.

<a id="rb-d03"></a>**RB-D03 Late/dirty tồn.** Xem phân bố theo site (thường một site backfill lớn); tăng song song job trong giờ thấp điểm; nếu chunk nén nhận nhiều hàng trễ: `decompress_chunk` → upsert → `compress_chunk` theo chunk.

<a id="rb-d04"></a>**RB-D04 Đóng ngày/báo cáo trễ.** Nếu watermark chưa tới: chờ tới 06:00 rồi phát hành `PARTIAL`; nếu job lỗi: chạy lại cho `(site, ngày)` (idempotent); kiểm restatement.

<a id="rb-d05"></a>**RB-D05 Retention không chạy.** Thường do archive chưa VERIFIED hoặc legal hold; không bao giờ bỏ qua kiểm manifest; nếu đĩa sắp đầy, mở rộng đĩa trước, không xóa tay.

<a id="rb-d06"></a>**RB-D06 Archive lệch.** So manifest theo `(series_id, ngày)`; xuất lại tháng đó (versioning giữ bản cũ); nếu DB đã mất phần dữ liệu (đường E) → sự cố dữ liệu, khôi phục từ backup còn PITR hoặc từ edge nếu < 7 ngày.

<a id="rb-d07"></a>**RB-D07 Backup/WAL lỗi.** `pgbackrest info`, `pgbackrest check`; kiểm `pg_stat_archiver` (`failed_count`, `last_failed_wal`); đĩa `pg_wal` đầy là nguy cơ dừng DB → ưu tiên khôi phục archive, không xóa WAL tay.

<a id="rb-d08"></a>**RB-D08 Drill thất bại.** Coi như backup không dùng được cho tới khi có drill đạt; xác định lỗi (phiên bản extension, thiếu WAL, lệch manifest); chạy full mới; báo cáo sự cố mức Cao.

<a id="rb-d09"></a>**RB-D09 Vacuum/bloat.** Bảng chuỗi append-only ít bloat; bloat thường ở `latest_value` snapshot, outbox, `dirty_bucket`, `command` → tăng autovacuum cho các bảng này; `REINDEX CONCURRENTLY` index bloat.

<a id="rb-d10"></a>**RB-D10 DQ/showback.** Mở ticket DQ cho site; không tự sửa dữ liệu đo; sửa qua `DataCorrection` có audit (FR-HIST-014).

---

<a id="s11"></a>
## 11. Chi phí ước tính

Không có bảng giá đã kiểm chứng cho nhà cung cấp tại Việt Nam (tìm kiếm không ra bảng giá Viettel IDC/FPT; một bài nêu 900 đ/GB/tháng chỉ là ví dụ minh họa, §14 W18). Vì vậy mục này cho **khối lượng GB-tháng** theo loại lưu trữ; chi phí = khối lượng × đơn giá **cần báo giá**.

### 11.1 Khối lượng 1.000 site (đường A) `[INFERENCE]`

| Loại lưu trữ | Năm 1 (cuối năm) | Năm 5 | Hệ số nhân bản | Tổng dung lượng thuê năm 5 |
|---|---|---|---|---|
| SSD/NVMe cho DB (primary) | raw 7 ngày 3,0 TB + raw nén ~11 TB + `agg_5m` 2,6 TB + khác ~0,5 TB ≈ **17 TB** | ≈ 29 TB | ×2 (standby) +1 replica đọc = ×3 | ≈ 87 TB (+ 30% dự phòng) |
| Object storage – backup (repo1 + repo2) | 2 full (~17–29 TB) + diff + WAL 14 ngày (2,3–3,9 TB) ≈ 40–60 TB mỗi repo | tăng theo DB | ×2 repo | 80–120 TB |
| Object storage – archive Parquet | raw 5,6 TB + `agg_5m` ~0,6 TB/năm | ≈ 31 TB (5 năm) | ×2 (vùng khác) | ≈ 62 TB |
| Object storage – report, export | ~0,12 TB/năm | ~0,6 TB | ×2 | ~1,2 TB |
| Edge SSD | ≥ 32 GB/site | — | — | Chi phí phần cứng (07 §6.15) |

### 11.2 Đòn bẩy chi phí, xếp theo tác động `[INFERENCE]`

1. Bật nén (đường A): raw 13 tháng 159 TB → 11,7 TB (×13).
2. Giảm số điểm C1 (§3.2): mỗi 10% số điểm chuyển C1 → C2 giảm ~50% hàng của nhóm đó.
3. D-06 (b) `LONG_5M`: `agg_5m` 5 năm 12,9 → ≈ 3,3 TB.
4. PITR 14 thay vì 35 ngày cho mon-db: WAL lưu giảm ~60%.
5. Parquet thay vì giữ raw trong DB khi không có TSL (đường E): 5,1 vs 133 B/hàng.

Công thức báo giá: `Chi phí/tháng ≈ GB_SSD × P_ssd × hệ số HA + GB_obj × P_obj + GB_obj_lock × P_obj_lock + egress_restore × P_egress` — các `P_*` là đơn giá cần báo giá (Q-44); phí egress khi restore/DR có thể đáng kể (W18 nêu egress thường chiếm phần lớn chi phí, nguồn thứ cấp).

---

<a id="s12"></a>
## 12. Áp dụng cho PoC hiện tại (`infra/`) — checklist, chưa triển khai

PoC hiện tại (đọc 2026-10-10): `infra/db/init.sql` tạo `telemetry` khóa `(site_id, device_id, point_code, ts)` dạng text, hypertable chunk 1 ngày, TimescaleDB chạy `license=apache` (không nén/CAGG), view `latest_value` bằng `DISTINCT ON`; `ingest.py` dedupe lô theo `(edge_id, stream, seq)` và ack sau commit; Grafana có sẵn. Đề xuất cho vòng PoC kế tiếp (agent PoC quyết định, F2 không sửa file):

- [ ] **Schema**: thêm `series(series_id serial, site_id, device_id, point_code, kind, agg_rule, unit, sampling_class, expected_period_s, deadband, max_age_s, retention_class)` sinh từ `infra/config/site.yaml`; đổi `telemetry` → `ts_gauge`/`ts_register`/`ts_state` khóa `(series_id, ts)`; `create_hypertable(..., create_default_indexes => false)`; bỏ `ts_ingest`, `edge_id`, `stream`, `seq` khỏi hàng (đã có trong `telemetry_batch`, thêm `batch_id`). Kỳ vọng: 291 → ~133 B/hàng (đo).
- [ ] **latest_value**: thay view `DISTINCT ON` bằng bảng `latest_value(series_id PK, ts, value, quality)` cập nhật trong transaction ingest với `WHERE excluded.ts > latest_value.ts` (đo: 8,4 s → 0,13 ms ở 20 M hàng).
- [ ] **Hai profile DB** trong compose: `db` (`license=apache`, mô phỏng đường E: `pg_partman` + `pg_cron` cần image có hai extension — image hiện tại `[UNKNOWN]` có sẵn hay không) và `db-tsl` (profile tùy chọn, `license=timescale`, **chỉ cho đo lường nội bộ** tới khi Q-14 có kết luận).
- [ ] **Job SQL đường A** (profile `db-tsl`): policy nén 7 ngày, CAGG `agg_5m` + `agg_1h` như §5.3, `job_stats` lên Grafana.
- [ ] **Job đường E**: `agg.refresh_5m()` + `pg_cron` mỗi 5 phút; `pg_partman` partition ngày, retention 35 ngày sang `ts_detached`.
- [ ] **Watermark**: ingest ghi `calc.watermark` từ `contig` sẵn có; panel Grafana "dữ liệu đầy đủ đến".
- [ ] **dirty_bucket**: ingest ghi khi lô `via_backfill` hoặc `ts < complete_until`; test bằng kịch bản ngắt broker của PoC.
- [ ] **Archive**: service `tools` thêm lệnh `archive-export --day` (DuckDB → Parquet ZSTD vào MinIO trong compose) và `archive-verify` (manifest); MinIO bật versioning (object lock nếu image hỗ trợ).
- [ ] **Backup**: thêm container `pgbackrest` (repo MinIO), `archive_mode=on`, chạy full + diff, và lệnh `tools restore-drill` restore vào container tạm + chạy bộ kiểm §8.7. Đo tốc độ restore và tỷ lệ nén WAL (đóng Q-65).
- [ ] **Guardrails**: role `app_api` với `statement_timeout=5s`; bật `pg_stat_statements`; panel Grafana "truy vấn đọc ts.* từ app_api".
- [ ] **DQ**: bảng `dq_site_day` + truy vấn completeness §9.2 trên `agg_5m`; panel Grafana completeness/freshness/lag.
- [ ] **Dữ liệu lớn**: tái dùng script lab F2 (`01_schema_gen.sql`) để nạp 1 site × 7 ngày rồi chạy bộ đo F2 cho cả hai profile — làm baseline hồi quy hiệu năng.
- [ ] **Dọn dẹp lab**: dùng `docker rm -v`/`docker compose down -v` có chủ đích; không `volume prune` toàn máy (xem F2 §6).

---

<a id="s13"></a>
## 13. Rủi ro và câu hỏi mở

Mã tiếp nối 13 (R-58, Q-62 là mã cuối hiện có). **Chưa đưa vào 13** — người tổng hợp chép sang.

### 13.1 Rủi ro

| Mã | Rủi ro | Khả năng | Tác động | Giảm thiểu | Owner |
|---|---|---|---|---|---|
| R-59 | Tỷ lệ nén thật kém hơn kế hoạch (đo đủ cột 16,9 B/hàng vs 10 B kế hoạch) → dung lượng raw 13 tháng ×1,7 | TB | TB | Gọn bảng §4.4; PoC-01 với dữ liệu site thật; theo dõi `hypertable_compression_stats` hằng tuần | DATA |
| R-60 | Restore toàn cụm mon-db ở 1.000 site vượt RTO 8 h (15–29 TB) | TB | Cao | Khôi phục theo bậc (§8.7), edge backfill, Parquet cho lịch sử; đo tốc độ restore trong drill | SRE |
| R-61 | Đường E (không TSL) buộc raw > 35–90 ngày chỉ ở Parquet → trend explorer > 35 ngày chậm/không tương tác, có thể không đạt cách hiểu NFR-DATA-008 | TB (phụ thuộc Q-14) | TB | Q-63; DuckDB job + `agg_5m` thay raw cho khoảng dài | PO + DATA |
| R-62 | Công cụ backup chính (pgBackRest) có rủi ro duy trì (một nguồn 2026, chưa kiểm chứng) | Thấp | TB | Giữ cấu hình WAL-G song song ở PoC; kiểm pgbackrest.org trước khi chốt | SRE |
| R-63 | CAGG nén trong cửa sổ refresh → refresh lỗi khi có dữ liệu trễ (đã tái hiện trong lab) | TB nếu cấu hình sai | TB | `compress_after(CAGG) > start_offset`; alert job lỗi; test hồi quy | DATA |
| R-64 | Backfill lớn rơi vào chunk đã nén (mất mạng > 7 ngày hoặc đổi `compress_after`) → ingest chậm ~100×, backlog | Thấp | TB | `late_landing` + gộp theo chunk; giữ `compress_after = 7 ngày` bằng buffer cứng | MON |
| R-65 | Volume WAL lớn (≈ 834 GB/ngày thô ở 1.000 site) gây đầy `pg_wal` khi archive chậm → DB dừng ghi | TB | Cao | `archive-async`, cảnh báo trễ 5 phút, đĩa `pg_wal` riêng có dư địa ≥ 24 h, `wal_compression` | SRE |
| R-66 | Xóa dữ liệu tenant trong chunk nén dùng chung đắt và chậm; bản trong backup còn tới hết vòng | Cao | TB (pháp lý) | Hợp đồng ghi rõ "xóa khỏi backup khi hết vòng backup"; crypto-shredding cho archive; DELETE theo lô | DATA + Pháp chế |
| R-67 | Dashboard hoặc API lỡ đọc raw (ORM, truy vấn ad hoc) làm tải primary tăng đột biến | TB | TB | Role không có quyền SELECT `ts.*` (06 §11), `pg_stat_statements` alert, test hiệu năng CI | MON |

### 13.2 Câu hỏi mở

| Mã | Câu hỏi | Owner | Vì sao quan trọng | Cách giải | Chặn |
|---|---|---|---|---|---|
| Q-63 | NFR-DATA-008 "raw 13 tháng" có cho phép phần sau 35–90 ngày nằm ở archive Parquet truy vấn bất đồng bộ (đường E) không? | PO | Quyết định khả thi đường E và chi phí | PO quyết, cập nhật FR-HIST-011 | G0 (cùng Q-14) |
| Q-64 | 10 §16.3 có chấp nhận PITR khác nhau theo cụm (ctl-db 35 ngày, mon-db 14 ngày + Parquet) và full tuần + diff ngày thay cho base backup hằng ngày? | SEC + SRE | Dung lượng WAL/backup | Agent 10 xác nhận | G1 |
| Q-65 | Tốc độ restore thực tế (pgBackRest, `process-max`) và tỷ lệ nén WAL trên hạ tầng mục tiêu tại VN | SRE | RTO 8 h và chi phí lưu WAL | Drill trên PoC + hạ tầng thật | G1 |
| Q-66 | Báo cáo/hóa đơn bóng và IntervalEnergy có thành **chứng từ kế toán** của khách (ESCO/PPA) không? Nếu có, giữ ≥ 10 năm (Luật Kế toán, nguồn thứ cấp) | LEGAL + BIZ | Retention 5 vs 10 năm | Pháp chế + hợp đồng mẫu | G1 |
| Q-67 | NĐ 53/2022 (lưu dữ liệu tại VN ≥ 24 tháng theo yêu cầu, nhật ký hệ thống) có áp cho SaaS EMS B2B không? | LEGAL | Retention log và vị trí lưu | Gộp với Q-08 | G0 |
| Q-68 | Tỷ lệ giảm hàng thật của deadband/RBE trên dữ liệu PV/BESS và tác động lên completeness | DATA + EDGE | Băng thông 4G, CPU ingest | Đo trên site pilot (cùng Q-E-13) | G1 |
| Q-69 | Image PostgreSQL/TimescaleDB production có kèm `pg_partman`, `pg_cron`, `pg_stat_statements`, Toolkit không, và chính sách nâng cấp phiên bản (ảnh hưởng restore) | ARC + SRE | Đường E và backup | Chọn image/đóng gói riêng | G0 |
| Q-70 | Mức real-time aggregation cho `agg_5m` có đạt NFR-PERF-001/002 ở 1.000 site khi refresh trễ? | DATA | Độ trễ dashboard | PoC-01 | G1 |

### 13.3 Vấn đề gửi agent khác

| Mã | Gửi | Vấn đề |
|---|---|---|
| X-17-01 | 04, 12 | Thêm NFR-DATA-014…023 (§1.3) vào 04 §6.3 và ma trận 12 |
| X-17-02 | 05 §19, 06 bảng định cỡ | Thay 5 B/hàng bằng 10 B/hàng kế hoạch (dải 2–17), `agg_5m` 24,5 B/hàng; thêm WAL vào định cỡ |
| X-17-03 | 10 §16.3 | Lịch backup theo cụm, drill tháng tự động + quý đầy đủ, PITR mon-db 14 ngày (Q-64) |
| X-17-04 | 06 §14 | `statement_timeout` 5 s cho API tương tác; quyền role không đọc `ts.*` |
| X-17-05 | 09 | Hiển thị "Độ phân giải" theo §7.2, envelope min/max, watermark |
| X-17-06 | 13 | Chép R-59…R-67, Q-63…Q-70 |
| X-17-07 | Agent PoC | Checklist §12; F2 §8 X-F2-01/02 |

---

<a id="s14"></a>
## 14. Nguồn

Số đo của tài liệu này: [notes/F2-data-lifecycle-lab.md](notes/F2-data-lifecycle-lab.md) §4 (`[FACT – đo trong lab]`, TimescaleDB 2.17.2, PostgreSQL 16.6, DuckDB 1.1.3, dữ liệu tổng hợp). Nguồn web dưới đây đều **qua kết quả tìm kiếm** (WebFetch bị chặn); mã W khớp sổ bằng chứng F2 §7. Nguồn đã có mã `S-xxx` trong 14 dùng lại qua các tài liệu 05/06/10/F.

| Mã | Nội dung | URL |
|---|---|---|
| W1 | Backup/restore logic TimescaleDB, pre/post restore, không `-j`, ghi phiên bản | https://www.tigerdata.com/docs/deploy/self-hosted/backup-and-restore/logical-backup ; https://docs.timescale.com/self-hosted/latest/backup-and-restore/logical-backup |
| W2 | `timescaledb_post_restore()` không tồn tại khi thiếu extension | https://support.zabbix.com/browse/ZBX-26790 |
| W3 | Lỗi restore hypertable/catalog | https://www.timescale.com/forum/t/timescaledb-backup-and-restore-issue/2527 ; https://timescale.com/forum/t/errors-during-restore-using-pg-restore/443 ; https://github.com/timescale/timescaledb/issues/1581 |
| W4 | CAGG khi di trú được tạo lại, không gồm raw đã xóa | https://docs.timescale.com/self-hosted/latest/migration/schema-then-data |
| W5 | So sánh pgBackRest / WAL-G / Barman | https://tessl.io/registry/alonso-skills/postgres/files/references/85-backup-tools.md ; https://ramnode.com/guides/series/postgres-superstack/pgbackrest ; https://chat2db.ai/resources/blog/pgbackrest-vs-barman-vs-wal-g ; https://severalnines.com/blog/automating-backups-and-disaster-recovery-in-postgresql-at-scale-pgbackrest-vs-barman/ ; https://dev.to/piteradyson/postgresql-backup-tools-comparison-databasus-wal-g-pgbackrest-and-barman-2kg ; https://www.kunalganglani.com/blog/postgresql-backup-tools-compared.md |
| W6 | Tình trạng duy trì pgBackRest 2026 (chưa kiểm chứng) | https://thebuild.com/blog/after-pgbackrest/ |
| W7 | Retention, multi-repo, archive-async của pgBackRest | https://docs.pgedge.com/pgbackrest/v2-57-0/user-guide/retention/ ; https://www.percona.com/blog/what-if-the-backup-server-is-down-and-a-backup-is-needed-multi-repo-functionality-of-pgbackrest/ ; https://pgbackrest.org/1/configuration.html ; https://enterprisedb.com/docs/supported-open-source/pgbackrest/05-retention_policy |
| W8 | LTTB (Steinarsson 2013) | https://github.com/vim-zz/highcharts-downsample ; https://pypi.org/project/lttb/0.2.2 ; https://metacpan.org/pod/Data::DownSample::LargestTriangleThreeBuckets |
| W9 | pg_partman retention, detach | https://api.pgxn.org/src/pg_partman/pg_partman-5.5.0/updates/pg_partman--4.7.0--4.7.1.sql ; https://api.pgxn.org/src/pg_partman/pg_partman-1.4.5/updates/pg_partman--1.2.0--1.3.0.sql ; https://www.crunchydata.com/blog/auto-archiving-and-data-retention-management-in-postgres-with-pg_partman ; https://cloud.google.com/blog/products/databases/dynamically-drop-partitions-within-cloud-databases ; https://www.postgrespro.com/list/thread-id/2705959 ; https://oneuptime.com/blog/post/2026-08-13-postgresql-partition-retention-drop-detach-archive/markdown |
| W10 | CAGG real-time mặc định, refresh offset | https://www.tigerdata.com/docs/reference/timescaledb/continuous-aggregates ; https://oneuptime.com/blog/post/2026-01-27-timescaledb-continuous-aggregates/markdown ; https://www.tigerdata.com/blog/continuous-aggregate-refresh-policies-solar-wind-scada ; https://stackharbor.com/en/knowledge-base/timescaledb-continuous-aggregates-strategy/ |
| W11 | Thiết lập nén, segmentby/orderby, columnstore 2.18 | https://docs.timescale.com/api/latest/compression/alter_table_compression ; https://docs.timescale.com/tutorials/latest/energy-data/compress-energy/ ; https://stellio.readthedocs.io/en/latest/admin/enabling_timescale_compression.html |
| W12 | S3 Object Lock compliance/governance | https://cloudian.com/blog/s3-object-lock-protecting-data-for-ransomware-threats-and-compliance/ ; https://www.vinchin.com/vm-backup/what-is-immutable-backup.html ; https://avepoint.com/blog/backup/immutable-backup ; https://www.solved.scality.com/s3-object-lock/ |
| W13 | BRIN vs B-tree | https://crunchydata.com/blog/postgres-indexing-when-does-brin-win ; https://crunchydata.com/blog/avoiding-the-pitfalls-of-brin-indexes-in-postgres ; https://hakibenita.com/postgresql-correlation-brin-multi-minmax ; https://www.depesz.com/?p=2915 |
| W14 | DuckDB Parquet (row group, ZSTD, Hive) | https://duckdb.org/docs/current/data/parquet/overview ; https://duckdb.org/docs/lts/data/parquet/tips |
| W15 | pg_cron | https://access.crunchydata.com/documentation/pg_cron/latest/ ; https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/PostgreSQL_pg_cron.md |
| W16 | NĐ 53/2022 lưu dữ liệu ≥ 24 tháng (phạm vi doanh nghiệp được nêu) | https://gvlawyers.com.vn/wp-content/uploads/2022/11/VN_Legal-alert-for-Decree-53-on-Cybersecurity.pdf ; https://lsvn.vn/tu-01102022-du-lieu-nguoi-dung-internet-tai-viet-nam-se-duoc-luu-tru1661052929.html ; https://ey.com/content/dam/ey-unified-site/ey-com/vi-vn/technical/tax/documents/ey-vietnam-legal-update-sep-2022-vn.pdf |
| W17 | Luật Kế toán: chứng từ 10 năm / 5 năm | https://ketoanthuanthien.vn/hoi-dap/quy-dinh-ve-thoi-han-luu-tru-hoa-don-dien-tu-la-bao-lau/ ; https://acman.vn/thoi-han-luu-tru-hoa-don-chung-tu-ma-ke-toan-can-biet.html ; https://einvoice.vn/tin-tuc/luu-tru-hoa-don-theo-nghi-dinh-123-2020-nd-cp |
| W18 | Giá object storage VN (không có bảng giá kiểm chứng) | https://cloudfly.vn/en/object-storage ; https://greennode.ai/blog/object-storage-viet-nam-gia-do-tre |
| Nội bộ | Quyết định và số liệu kế thừa | [05 §7, §19](05-domain-model.html#s19); [06 ADR-06, §11](06-system-architecture.html#adr-06); [07 §6.5–§6.12](07-device-integration.md); [10 §7, §16](10-security-and-reliability.md); [15 §8.2](15-simulators-and-messaging.md); [04 §6.3](04-business-requirements.md); [F](notes/F-data-analytics.md) (TimescaleDB TSL, CAGG, FusionSolar retention) |
