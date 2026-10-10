# A2 — Bản đồ yêu cầu → PoC → kiểm thử (QA BA)

- Ngày: 2026-10-10 · Vai trò: Business analyst cho QA (ánh xạ yêu cầu) · Trạng thái: bản 1, **chỉ đọc** mã sản phẩm, không chạy stack Docker.
- Đầu vào đã đọc: [infra/README.md](../../../infra/README.md) (toàn bộ), [04 Yêu cầu](../../research/ems/04-business-requirements.md) §0–§2, §5.3, §5.4, §5.7, §5.9, §5.10, §5.13, §5.14, §6; [07 Tích hợp](../../research/ems/07-device-integration.md) §5.1.5, §6.5–§6.12, §7.1–§7.4, §8.2–§8.7, §11.3; [10 An toàn](../../research/ems/10-security-and-reliability.md) §9.3, §11.4, §11.6–§11.9; [12 Truy vết](../../research/ems/12-traceability-matrix.md) §2, các dòng FR/NFR liên quan. Mã: `edge/bridge/bridge/*.py`, `ingest/ingest.py`, `simulators/vsite/vsite/{model,server,__main__}.py`, `simulators/vsite/maps/regmap.py` + map BESS/công tơ, `simulators/evse/csms/csms.py`, `tools/ems_cli.py`, `infra/{mosquitto,db,config}`, `tests/smoke.sh`.
- Không đọc: 05/06 (HTML), 15/16, 17 (agent khác đang viết). Wireframe không liên quan vì chưa có UI.

## Mục lục

1. [Quy ước](#1-quy-ước)
2. [Tóm tắt](#2-tóm-tắt)
3. [Bảng ánh xạ yêu cầu đã hiện thực (yes/partial)](#3-bảng-ánh-xạ-yêu-cầu-đã-hiện-thực-yespartial)
4. [Lỗi và lệch tài liệu phát hiện khi ánh xạ](#4-lỗi-và-lệch-tài-liệu-phát-hiện-khi-ánh-xạ)
5. [Yêu cầu CHƯA hiện thực (ngoài phạm vi test hiện tại)](#5-yêu-cầu-chưa-hiện-thực-ngoài-phạm-vi-test-hiện-tại)
6. [Tính độ phủ](#6-tính-độ-phủ)
7. [Điểm nối (seam) cần cho test và gợi ý cho framework](#7-điểm-nối-seam-cần-cho-test-và-gợi-ý-cho-framework)
8. [UNKNOWN và câu hỏi mở](#8-unknown-và-câu-hỏi-mở)

---

## 1. Quy ước

**Cột "Hiện thực?"**: `yes` = hành vi yêu cầu có trong mã PoC (có thể ở mức PoC: JSON thay Protobuf, user/pass thay mTLS); `partial` = có một phần, phần thiếu ghi rõ; `no` = không có (liệt kê ở §5, không tính vào mẫu số độ phủ).

**Nhãn bằng chứng**: `FACT` = trích `file:line` (dòng đếm bằng `grep -n`/`cat -n` ngày 2026-10-10) hoặc đầu ra lệnh; `INFERENCE` = suy ra từ đọc mã, **chưa chạy**; `UNKNOWN` = không xác định được. Kết quả chạy trong README §9 là FACT **của tác giả PoC**, không phải do A2 chạy lại.

**Rủi ro nếu hỏng**: `H` = mất an toàn vật lý, mất dữ liệu, lệnh sai/thi hành lại, rò dữ liệu giữa edge/tenant; `M` = sai số liệu/hợp đồng mà người vận hành vẫn phát hiện được; `L` = khó chịu, chẩn đoán.

**Cấp test đề xuất** (khớp 12 §2.1, thêm `C`):

| Mã | Cấp | Chạy với | Ghi chú |
|---|---|---|---|
| U | Unit | Python thuần, pytest, không Docker | Hàm thuần/lớp có seam (§7) |
| C | Contract | JSON Schema 07 §7.3 + thuộc tính MQTT 5, trên tin thu được từ broker thật hoặc tin ghi lại | Dùng lại được khi edge Java/Protobuf thay PoC |
| I | Integration | 1–2 thành phần + Mosquitto/PostgreSQL thật (container) | Không cần vsite |
| S | System/Simulation | Toàn stack `emspoc` + tiêm lỗi vsite REST | Chỉ agent sở hữu Docker được chạy |
| E | E2E UI | Angular → Spring → DB | **Chưa có**, để chỗ cắm sau |

Mã dòng (`TEL-01`, `CMD-07`…) là mã cục bộ của A2 để các agent khác trỏ tới; cột ReqID ghi mã chính thức của 04/07/10 và mã `T-` của 12/07 nếu có.

---

## 2. Tóm tắt

- **Phạm vi hiện thực thật nhỏ**: 31/268 FR và 21/85 NFR có hiện thực `yes`/`partial` trong PoC = **52/353 mã (14,7 %)** [FACT: đếm ở §6, tổng 268/85 theo 12 dòng "Phạm vi"]. Mọi FR về UI, PDP, MFA, RLS, JWS, audit, biểu giá, tối ưu, báo cáo là `no`.
- 68 dòng kiểm thử ở §3 bao phủ phạm vi đó. Test tự động hiện có (`tests/smoke.sh`) chạm **8/68 dòng (11,8 %)**, thêm 8 dòng chỉ có bằng chứng chạy tay trong README §9 → **16/68 (23,5 %)** có bất kỳ bằng chứng chạy nào [INFERENCE: đối chiếu `tests/smoke.sh` với §3; A2 **không** chạy smoke].
- 34/68 dòng rủi ro `H`, tập trung ở: vòng đời lệnh/hết hạn, idempotency/replay, store-and-forward, watchdog, ACL.
- **Phát hiện khi ánh xạ** (§4): 1 lệch hợp đồng là FACT (mã interlock `IL-04` thay vì `IL-03` cho BMS cũ); 3 lỗi rủi ro H suy ra từ mã (B-02 ingest tin `edge_id` trong payload; B-03 bridge khởi động lại làm mất lệnh đang hiệu lực → setpoint không bao giờ hoàn nguyên nếu restart < 15 s; B-04 supersede trước khi ghi thành công) và 8 lỗi M/L (B-05…B-12). Tất cả cần test đỏ xác nhận trước khi sửa.

---

## 3. Bảng ánh xạ yêu cầu đã hiện thực (yes/partial)

### 3.1 Hợp đồng telemetry MQTT (TEL)

| ReqID | Yêu cầu / tiêu chí (tóm tắt) | Hiện thực? · bằng chứng | Rủi ro | Cấp | Ý tưởng test và assertion cụ thể |
|---|---|---|---|---|---|
| **TEL-01** · FR-INT-008, 07 §7.1, T-FR-INT-008 | Không gian topic `ems/v1/{edge_id}/up/{telemetry/{c1..c4}, backfill, event, cmd-ack, state}`, `down/{cmd, config}` | yes · FACT `edge/bridge/bridge/__main__.py:97-100`, `commands.py:40,50`, `uplink.py:57,83-84,107`, `csms.py:62` | H | C, S | Thu mọi tin trên `ems/v1/+/up/#` trong 3 phút (user `ingest`); assert mỗi topic khớp `^ems/v1/(edge-vsite01\|edge-ev01)/up/(telemetry/c[1-4]\|backfill\|event\|cmd-ack\|state)$`; 0 topic lạ; `edge_id` trong payload == đoạn topic (xem ACL-03). |
| **TEL-02** · 07 §7.1 (thuộc tính MQTT 5) | QoS 1, không retain (trừ `up/state`); Content Type `application/json`, Payload Format Indicator 1; User Property `schema`, `edge_seq` | yes · FACT `uplink.py:26-38,115`, `__main__.py:97-99`; CSMS `csms.py:56-62` | M | C | Với paho v5: `msg.qos==1`, `msg.retain==False` cho telemetry/event/cmd-ack; `props.ContentType=="application/json"`, `PayloadFormatIndicator==1`; `("schema","ems.telemetry.v1")` ∈ UserProperty và `edge_seq` == `str(payload.seq)`. |
| **TEL-03** · 07 §7.3 | Lô `{schema, edge_id, stream, seq, batch_ts, config_version, points[]}`; gauge `{pid, ts, w, avg, min, max, last, n, q[, cov_ms]}`; counter `{pid, ts, raw, q, boundary[, ts_src]}` | yes (JSON logic, không Protobuf) · FACT `__main__.py:95-96`, `aggregate.py:63-69,93-98` | H | U, C | U: `Aggregator.flush()` với đọc tổng hợp → validate bằng JSON Schema rút gọn 07 §7.3 (tách schema gauge/counter vì counter không có `w`). C: mọi lô thật pass schema; `w ∈ {5,60,300}`; `ts % (w*1000) == 0`; `min ≤ avg ≤ max`; `n ≤ w / poll_period`. |
| **TEL-04** · 07 §7.3, NFR-DATA-005, 04 §1.3 #10 | Điểm `BAD_*` **không mang giá trị**, không gửi 0; DB lưu NULL | yes · FACT `aggregate.py:63-64`, `ingest.py:73`, README §9 (`meter.e_import NULL BAD_COMM`) | H | U, S | U: cửa sổ chỉ có đọc `BAD_COMM` → mẫu không có khóa `avg/min/max/last`, `q=="BAD_COMM"`. S: `fault meter-load --comm-loss` 10 s → `SELECT count(*) FROM telemetry WHERE device_id='meter-load' AND quality LIKE 'BAD_%' AND value IS NOT NULL` == 0. |
| **TEL-05** · FR-MON-001, 07 §6.5, T-FR-MON-001 | Lớp C1 5 s, C2 60 s, C3 300 s, C4 mỗi 60 s, C5 sự kiện khi đổi | partial (C3 chỉ theo chu kỳ, không "khi đổi"; C4 chưa đọc chủ động tại biên 5 phút — README §14) · FACT `aggregate.py:12-14,47,85,88-99`; `__main__.py:54-66` | M | U, S | U: đẩy 61 đọc 1 s cho 1 điểm C1 → `flush` trả đúng 12 cửa sổ có `w=5`, mỗi `n==5`. S: trong 1 phút trọn, `meter-poc meter.p` có 12 hàng C1, mỗi `pv_inverter.p` 1 hàng C2 (đúng điều kiện `HAVING` của truy vấn cân bằng README §7). |
| **TEL-06** · 04 FR-HIST-005 (quy ước), K R-05 | Cửa sổ nửa mở `[ts, ts+w)`; `ts` = đầu cửa sổ UTC ms | yes (ở edge) · FACT `aggregate.py:47` | M | U | Đọc tại `ts = k·5000` vào cửa sổ mới `k`, đọc tại `k·5000−1` vào cửa sổ `k−1`; cửa sổ đóng chỉ khi `now ≥ start + w + 500 ms` (`aggregate.py:85`). |
| **TEL-07** · 07 §6.10, FR-INT-008 (`seq`) | `seq` đơn điệu theo `(edge_id, stream)`, bền, không reset khi khởi động lại | yes (bridge); **no** cho CSMS stub (seq theo thời gian, không bền — README §14) · FACT `store.py:42-46`, `csms.py:65` | H | U, S | U: `Store(tmp)` gọi `next_seq("c1")` 3 lần → 1,2,3; mở lại cùng file → 4. S: `docker compose restart bridge` → `ems seq-check` gaps 0, `min_seq` không về 1. |
| **TEL-08** · 07 §7.1 (`max_batch_bytes`) | Lô ≤ 256 KB, edge tự chia | yes · FACT `__main__.py:25,103-113` | L | U | Patch `MAX_BATCH_BYTES=2048`, 200 mẫu → mỗi payload JSON hoàn chỉnh (cả header) `len(json.dumps(...)) ≤ 2048`; tổng số điểm bảo toàn; `seq` liên tiếp. |
| **TEL-09** · FR-MON-002, 07 §7.4 | `ts` (edge), `ts_src` (đồng hồ thiết bị, tùy chọn), `ts_ingest` (cloud gán) | partial (`ts_src` chỉ trên counter C4 và sự kiện; `src_clock_state="UNKNOWN"` cứng) · FACT `poller.py:97-102`, `aggregate.py:97-98`, `__main__.py:62`, `infra/db/init.sql:19` | M | S | `fault meter-poc --clock-offset -3600` → hàng C4 của `meter-poc`: `ts_src ≈ ts − 3600 s` (±2 s), `ts` không đổi; mọi hàng `ts_ingest ≥ ts`. |
| **TEL-10** · 07 §6.5 C5, FR-ALM (nguồn sự kiện) | Alarm word → sự kiện `DEVICE_ALARM` RAISED/CLEARED khi đổi, không phải telemetry | yes · FACT `__main__.py:54-66` | M | U, S | U: chuỗi giá trị 0, 0x2104, 0x2104, 0 → đúng 2 sự kiện: RAISED `code_raw=0x2104`, rồi CLEARED `code_raw=0x2104`; `event_id` tăng. S: `fault pv-inv-03 --alarm 0x2104` → 1 hàng `event` type DEVICE_ALARM. |

### 3.2 Quality tầng điểm (QUAL)

| ReqID | Yêu cầu / tiêu chí | Hiện thực? · bằng chứng | Rủi ro | Cấp | Ý tưởng test và assertion |
|---|---|---|---|---|---|
| **QUAL-01** · 07 §5.1.5, §6.9 | Exception 01/02/03 → `BAD_CONFIG` | partial (không ngừng poll block, không sinh sự kiện cấu hình) · FACT `poller.py:66-68,120-121` | M | U, S | U: client giả trả exception 2 → mọi điểm của thiết bị `q=="BAD_CONFIG"`, `value is None`. S: `fault pv-inv-03 --exception 2` → DB quality BAD_CONFIG, value NULL. |
| **QUAL-02** · 07 §5.1.5, 04 §2 `point.max_age_s` | Exception 04/06 → giữ giá trị cũ tới `max_age` (3 × chu kỳ poll) rồi `UNCERTAIN_STALE` | partial (không backoff có jitter; giá trị giữ được gắn `GOOD`) · FACT `poller.py:42,122-129` | M | U | Đọc tốt lúc t0; exc 6 lúc t0+2 s → `value==last`, `q=="GOOD"`; lúc t0+4 s → `value is None`, `q=="UNCERTAIN_STALE"`. Cửa sổ chỉ gồm đọc stale → mẫu không giá trị, `q=="UNCERTAIN_STALE"`. |
| **QUAL-03** · 07 §5.1.5, AC-INT (WF-09) | Timeout 3 lần liên tiếp → `BAD_COMM` + sự kiện `DEVICE_COMM LOST`; phục hồi → `RESTORED` | yes · FACT `poller.py:16,84-86,111-119` | H | U, S | U: 2 lỗi → không phát đọc nào; lỗi thứ 3 → mọi điểm `BAD_COMM` và **đúng 1** sự kiện LOST; lỗi thứ 4 → không LOST thứ 2; đọc tốt → đúng 1 RESTORED. S: `fault meter-load --comm-loss`/`--clear` (D11). |
| **QUAL-04** · 07 §5.1.5, FR-MON (sentinel) | Giá trị sentinel `na_values` → `BAD_DEVICE` | yes · FACT `regmap.py:98-102`, `poller.py:96`; map `generic_bess_pcs.yaml:16-17` | M | U, S | U: `Register(ess.soc).decode([0xFFFF]) == (None, True)`. S: `fault ess-01 --sentinel` → `ess.soc` quality BAD_DEVICE, value NULL. |
| **QUAL-05** · 07 §7.3 (`cov_ms`) | Cửa sổ thiếu mẫu mang `cov_ms` | yes · FACT `aggregate.py:66-69` | L | U | 3 đọc GOOD trong cửa sổ 5 s → `n==3`, `cov_ms==3000`; đủ 5 → không có `cov_ms`. |

### 3.3 Store-and-forward và ingest (SF)

| ReqID | Yêu cầu / tiêu chí | Hiện thực? · bằng chứng | Rủi ro | Cấp | Ý tưởng test và assertion |
|---|---|---|---|---|---|
| **SF-01** · FR-INT-009, NFR-DATA-001, 07 §6.7, T-FR-INT-009 | Mọi tin up qua outbox bền; mất broker không mất dữ liệu | partial (đã chứng minh 30 s, chưa 7 ngày) · FACT `store.py:53-60`, `uplink.py:130-140`; README §9 bước 5 (`gaps 0`) | H | I, S | S (D8): dừng mosquitto 30 s → `ems seq-check` `gaps 0` cho mọi stream của `edge-vsite01`. I: chạy `Uplink`+`Store` với broker container dừng/khởi động → số lô gửi == số `seq` cấp. Kéo dài: dừng 30 phút (tăng tốc bằng `W_C1_S`). |
| **SF-02** · 07 §7.1, ADR-16 | Telemetry chỉ xóa khi nhận `TELEMETRY_ACK` gửi **sau commit DB**; PUBACK không đủ | yes · FACT `uplink.py:99-100,123-126`, `store.py:84-88`, `ingest.py:59-84` | H | U, I | U: `mark_sent` rồi `ack_telemetry("c1", 5)` → chỉ xóa hàng `kind='telemetry' AND stream='c1' AND seq≤5`; hàng `c2` và `event` còn. I: làm DB lỗi (dừng `db`) → ingest không gửi ACK → sau 20 s bridge gửi lại; DB lên lại → `telemetry_batch` đủ seq, không trùng. |
| **SF-03** · 07 §7.1 (ack tích lũy) | `ack_seq` = seq cao nhất không có lỗ phía dưới | yes · FACT `ingest.py:86-106` | H | U (cần seam §7) | Nhận 1,2,4 → ACK lần lượt 1,2,2; nhận 3 → ACK 4. Khởi động lại ingest với DB có 1,2,4 → `contig==2`. |
| **SF-04** · 07 §6.12 | Gửi lại lô chưa ack sau `TELEMETRY_RESEND_S` (20 s) và khi kết nối lại | yes · FACT `store.py:62-68,78-82`, `uplink.py:51,78` | H | U | `pending(resend_ms=20000)`: hàng `sent_ms = now−19 s` không trả; `now−21 s` trả; `reset_unacked()` đặt mọi `sent_ms=NULL`. |
| **SF-05** · FR-INT-009, 07 §6.7, §6.12 bước 5 | Tồn đọng đi `up/backfill`, cũ trước, giới hạn tốc độ; realtime ưu tiên | yes (giới hạn 20 tin/s, mặc định 07 là 30 % băng thông) · FACT `uplink.py:135-151` | M | S | Sau D8: các lô có `arrival` trong lúc phục hồi và `topic LIKE '%/up/backfill'` có `seq` tăng dần theo `arrival` ("out of seq order: 0"); số lô backfill/giây ≤ 20; lô live đầu tiên sau reconnect tới **trước** lô backfill cuối. |
| **SF-06** · FR-HIST-002, NFR-DATA-002, AC-HIST-08, T-FR-HIST-002 | Ingest idempotent: bỏ trùng theo `(edge_id, stream, seq)`, upsert `(series, ts)`; trùng vẫn được ack | partial (khác giá trị → "giữ `rev` cao hơn + audit" chưa có: giữ bản đầu) · FACT `ingest.py:60-66,78-81`; `init.sql:22,31` | H | I | Publish cùng lô 2 lần → `telemetry_batch` 1 hàng; `telemetry` không đổi số hàng; 2 TELEMETRY_ACK cùng `ack_seq`. Lô khác `seq`, cùng `(device, point, ts)`, khác value → hiện giữ bản đầu (ghi lại hành vi; kỳ vọng doc khác). |
| **SF-07** · AC-MON-04, NFR-DATA-002 | "Giá trị hiện tại" chỉ tiến theo `ts` | yes · FACT `init.sql:74-78` (view `DISTINCT ON … ORDER BY ts DESC`) | M | I | Ghi `ts=10:00:10` rồi lô trễ `ts=10:00:05` (seq mới) → `latest_value.ts == 10:00:10`. |
| **SF-08** · NFR-REL-016, 07 §6.7 | `event`, `cmd-ack`, `state` không bao giờ bị bỏ | partial (xóa khỏi outbox khi PUBACK — README §14; dựa vào phiên ingest `clean_start=false`) · FACT `uplink.py:125-126`, `ingest.py:169-172` | M | S | Dừng **ingest** (không phải broker) 30 s, tiêm alarm + gửi 1 lệnh → bật ingest → `event` và đủ chuỗi `command_ack` có trong DB. |
| **SF-09** · FR-INT-009 (7 ngày, ưu tiên bỏ C3→C2) | Buffer 7/30 ngày, khi đầy bỏ C3 trước, không bao giờ bỏ C4/C5 | partial (outbox không giới hạn, không ưu tiên bỏ) · FACT `store.py:53-60` (không có giới hạn) | M | S (tăng tốc) | Chỉ đo được dung lượng/lô theo giờ để ngoại suy 7 ngày; không test được hành vi "đầy" — ghi `no` cho phần bỏ có ưu tiên. |

### 3.4 Lệnh: kiểm tra, vòng đời, hết hạn, idempotency (CMD)

Chung: `CommandHandler` (`edge/bridge/bridge/commands.py`) là điểm test U tốt nhất (fake `ess` + `Store(tmp)` + patch `bridge.commands.now_ms`), xem §7.

| ReqID | Yêu cầu / tiêu chí | Hiện thực? · bằng chứng | Rủi ro | Cấp | Ý tưởng test và assertion |
|---|---|---|---|---|---|
| **CMD-01** · FR-SEC-008, 07 §8.2, §8.7 A.3, BR-SEC-09, T-NFR-SEC-004d | Envelope đủ trường bắt buộc; thiếu `expires_at` → từ chối | partial (không JWS; `idempotency_key` đúng là không xuống edge) · FACT `commands.py:102-106` | H | U | Tham số hóa 12 trường: bỏ từng trường → ack cuối `REJECTED_INVALID`, `reason=="MISSING_FIELDS:<field>"`, `ess.write` không được gọi. |
| **CMD-02** · 07 §8.7 A.2, T-NFR-SEC-004 | `target.edge_id` ≠ chính nó → `REJECTED_INVALID` | yes · FACT `commands.py:99-100` | H | U, S | `target.edge_id="edge-x"` → `REJECTED_INVALID/TARGET_MISMATCH`, không write. |
| **CMD-03** · 07 §8.7 A.3, §8.4 | Type không hỗ trợ → `REJECTED_UNSUPPORTED`; `params` chặt `{p_w: number}` | yes (lưu ý `p_w=true` lọt — §4 B-09) · FACT `commands.py:107-110` | M | U | `SET_PV_LIMIT` → `REJECTED_UNSUPPORTED`; `{p_w:1,x:2}` → `REJECTED_INVALID/PARAMS`; `p_w:"100"` → PARAMS; `p_w:true` → kỳ vọng PARAMS (hiện **lọt**). |
| **CMD-04** · 07 §8.2, FR-BESS-005, 04 §2 | Thời hạn setpoint ≤ 1 h | yes · FACT `commands.py:20,111-113` | H | U | `expires−valid_from = 3 600 000 ms` → qua; `+1 ms` → `REJECTED_INVALID/DURATION_GT_1H`. |
| **CMD-05** · 07 §8.7 A.3, AC-BESS-02 (phần edge), T-NFR-SEC-004b | Setpoint > 80 % SOE cần hạng ≥ C2 **và** `reason` | yes · FACT `commands.py:114-117`; `rated_w` = SOE xả `__main__.py:48-49` | H | U | SOE 250 kW: `p_w=200000` C1 → qua; `200001` C1 → `REJECTED_INVALID/DANGER_CLASS_MIN_C2`; C2 không `reason` → từ chối; C2 + reason → qua; `p_w=-200001` C1 → từ chối (áp cả chiều sạc). |
| **CMD-06** · 07 §8.7 A.4, 10 §11.7, BR-SEC-09, T-NFR-SEC-004 | `seq` theo signer phải tăng → `REJECTED_REPLAY`; bền qua khởi động lại | yes (fsync: INFERENCE — SQLite WAL mặc định) · FACT `commands.py:119-120`, `store.py:109-117` | H | U, S | `seq=100` qua; lệnh mới `seq=100` → `REJECTED_REPLAY/SEQ_NOT_INCREASING`; `99` → REPLAY; `101` qua; mở lại `Store` → `100` vẫn REPLAY. |
| **CMD-07** · 07 §8.2 (`command_id` là khóa idempotency), 10 §11.7, D6 | Trùng `command_id` → trả trạng thái cũ, `duplicate:true`, **không** thực thi lại; bền qua restart | yes · FACT `commands.py:79-86`, `store.py:97-100`; README §9 bước 4 | H | U, S | U: gửi cùng envelope 2 lần → `ess.write("ess.p_setpoint",…)` gọi đúng 1 lần; ack thứ 2 có `duplicate:true`, `reason=="DUPLICATE_COMMAND_ID"`, `state` == trạng thái cuối của lần 1. S: smoke 4b (`DISPATCHED x1`, duplicate acks x1). Restart bridge rồi gửi lại → vẫn duplicate. |
| **CMD-08** · AC-SEC-05, 07 §8.7 C.7, NFR-SEC-011, T-NFR-SEC-011, D5 | Ngoài `[valid_from, expires_at]` hoặc trễ > `max_latency_ms` → `REJECTED_STALE`, không ghi | yes · FACT `commands.py:126-130`; README §9 bước 4 | H | U, S | U (đồng hồ giả): `now=expires+1 s` → `REJECTED_STALE/EXPIRED_BEFORE_EXECUTION`, không có ack DISPATCHED; `now<valid_from` → `OUTSIDE_VALIDITY_WINDOW`; `rx−sent_at=10001` (max 10000) → `MAX_LATENCY_EXCEEDED`; `=10000` → qua. S: smoke 4a. |
| **CMD-09** · 07 §8.2a, 10 §9.3, T-E2-01, T-E2-02 | Lệnh QoS 1 không retained; Message Expiry = `expires_at − sent_at`; Correlation Data = `command_id` echo trên mọi ack; Response Topic lạ bị bỏ qua + cảnh báo | partial (Response Topic lạ chỉ ghi log, không sinh sự kiện bảo mật) · FACT `tools/ems_cli.py:61-77,118-119`, `commands.py:40-42,74-78,88-89` | H | C, S | C: mọi ack có `CorrelationData == command_id.encode()`. S: lệnh với Response Topic `ems/v1/edge-ev01/up/cmd-ack` → ack vẫn chỉ trên `ems/v1/edge-vsite01/up/cmd-ack`. T-E2-01: dừng bridge, gửi lệnh Message Expiry 5 s, chờ 10 s, bật bridge → không có `RECEIVED` cho lệnh đó. Lệnh không retained: subscriber mới trên `down/cmd` không nhận tin cũ. |
| **CMD-10** · 07 §8.7 B, 04 §2 "Hạ rủi ro", T-FR-INT-018d, T-NFR-SEC-004e | `SET_ESS_P p_w=0` đi đường an toàn hóa: bỏ qua phần C nhưng **không** bỏ phần A | partial (không có audit `safe_path` + danh sách bước bỏ qua) · FACT `commands.py:121-124,145,151` | H | U, S | `p_w=0` với `expires_at` đã qua và trễ 42 s → `ACCEPTED` có `safe_path:true`, `effective_setpoint.p_w==0`, rồi APPLIED; `p_w=0` với `seq` cũ → `REJECTED_REPLAY`; sai target → `REJECTED_INVALID`. S: bước dọn của smoke. |
| **CMD-11** · AC-BESS-06, FR-BESS-007 (phần SOE tĩnh), 07 §8.7 C.11 | Ngoài SOE tĩnh → `REJECTED_OUT_OF_LIMIT`, không ghi | partial (chỉ P sạc/xả max, không ramp/ΔP/SOC) · FACT `commands.py:132-133`; `infra/config/site.yaml:140` | H | U | Phải dùng C2 + reason (vì > 80 %): `p_w=250001` → `REJECTED_OUT_OF_LIMIT/OUTSIDE_SOE`; `-250001` → như trên; không `ess.write`. |
| **CMD-12** · FR-BESS-009, AC-BESS-04 (phần từ chối), NFR-REL-007, 10 §11.4 IL-03 | Dữ liệu BMS cũ > `T_stale_bms` (5 s) → `REJECTED_INTERLOCK` | partial · FACT `commands.py:21,134-137`. **Mã sai: trả `IL-04`, tài liệu là `IL-03`** (§4 B-01). Không có P=0 tự động ở edge khi BMS cũ | H | U, S | U: `image["ess.p_discharge_max"].ts_ms = now−5001` → kỳ vọng `REJECTED_INTERLOCK:IL-03` (hiện trả IL-04 → test **đỏ** tới khi sửa); `now−5000` → qua. S: `fault ess-01 --comm-loss` 6 s rồi gửi lệnh → từ chối, không write. |
| **CMD-13** · FR-BESS-008, BR-BESS-03, 07 §8.5, §8.7 C.11, D7 | Giới hạn động CCL/DCL → kẹp, `APPLIED_CLAMPED` + `CLAMPED_BY_BMS`, ghi giá trị thực và nguồn | yes · FACT `commands.py:143-150,174-176`; README §9 (D7) | H | U, S | U: `pdis=50000`, xin 120000 → ACCEPTED `effective_setpoint.p_w==50000`; ack cuối `APPLIED_CLAMPED`, `clamp=={code:"CLAMPED_BY_BMS", limit_w:50000, source_point:"ess.p_discharge_max"}`; sạc −120000 với `pch=50000` → −50000, `source_point:"ess.p_charge_max"`. S: D7. |
| **CMD-14** · FR-INT-007, FR-BESS-005, FR-SEC-009, 07 §8.4, §8.5-1, T-FR-INT-007, D3 | Thứ tự `RECEIVED→ACCEPTED→DISPATCHED→APPLIED`; `APPLIED` chỉ sau readback ±1 LSB trong `readback_timeout_s`; lỗi → `FAILED_{DEVICE_EXCEPTION,NO_EFFECT,TIMEOUT}` | yes · FACT `commands.py:150-178` | H | U, S | U (fake ess): readback khớp → chuỗi trạng thái đúng thứ tự trên; `write` trả lỗi → `FAILED_DEVICE_EXCEPTION`, **không** có DISPATCHED; readback luôn lệch 2 W (`readback_timeout_s=1`) → `FAILED_NO_EFFECT`; readback `None` → `FAILED_TIMEOUT`. S: smoke bước 3 (readback −100000). |
| **CMD-15** · 07 §8.5-2 | Theo dõi đáp ứng `ess.p` so setpoint, dung sai max(2 % Pđm, 1 kW) → `CTRL.TRACKING_OK/DEVIATION` | partial (một lần ở giây 8, không theo dõi suốt lệnh, không DEVIATING > 60 s) · FACT `commands.py:182-192` | M | U, S | U (patch sleep): `measured=-99191`, setpoint −100000, Pđm 250 kW → TRACKING_OK `tolerance_w==5000`; `measured=-90000` → TRACKING_DEVIATION. S: sự kiện có trong `event` sau 8–10 s. |
| **CMD-16** · AC-BESS-03, BR-BESS-06, 07 §8.6, FR-BESS-005 | Hết hạn → `on_expiry=REVERT_DEFAULT` (P=0), `EXPIRED` → `COMPLETED`, đúng giờ (±1 chu kỳ) | partial (trễ tới 8 s với lệnh ngắn — §4 B-05) · FACT `commands.py:193-200`; README §9 (11:17:58 → 0) | H | U, S | S: lệnh 2 phút → `vsite /state ess.p_setpoint_w == 0` trong ≤ 2 s sau `expires_at`; ack `EXPIRED` có `ts − expires_at ≤ 1000 ms`, rồi `COMPLETED`. U: lệnh còn 3 s khi APPLIED → kỳ vọng revert ở ~3 s (hiện ~8 s → **đỏ**). |
| **CMD-17** · 07 §8.4 (`SUPERSEDED`) | Lệnh mới thay lệnh đang hiệu lực: cũ `SUPERSEDED`, chỉ hạn của lệnh mới còn hiệu lực | partial (bug khi lệnh mới ghi lỗi — §4 B-04) · FACT `commands.py:152-155` | H | U | A APPLIED; B APPLIED → A có ack `SUPERSEDED`, `superseded_by==B`; tới hạn A không ghi 0; tới hạn B ghi 0. Ca âm: B `write` lỗi → kỳ vọng thiết bị vẫn về 0 ở hạn của A (hiện **không** → đỏ). |
| **CMD-18** · FR-INT-011 (phần reported), 07 §6.12 bước 2 | `up/state` retained báo `active_commands[]` (id, `expires_at`), `config_version_reported`, `last_seq_by_stream`, buffer | partial (`clock_state` cứng `SYNCED`, không có đối soát cloud) · FACT `__main__.py:80-84`, `commands.py:204-209` | M | C, S | Khi có lệnh hiệu lực: tin state retained có `active_commands[0].command_id == cid`, `expires_at` đúng; sau hạn → `active_commands == []`; `last_seq_by_stream.c1 ≥` `max(seq)` trong `telemetry_batch`. |
| **CMD-19** · NFR-REL-012, NFR-REL-003, AC-INT-09 | Sau khi edge khởi động lại không thi hành lệnh cũ và không để setpoint cũ vô hạn | partial (không áp lại lệnh cũ — FACT README §9 bước 6; nhưng lệnh đang hiệu lực bị quên — §4 B-03) · FACT `commands.py:32,180` (chỉ trong RAM) | H | S | Lệnh 2 phút −80 kW; `docker compose restart bridge` (< 15 s) → sau `expires_at` + 5 s: kỳ vọng `ess.p_setpoint_w == 0` (INFERENCE: hiện giữ −80000 → **đỏ**). Restart > 15 s → watchdog đưa về 0 (đã thấy README §9). |
| **CMD-20** · 07 §8.7 A.3 | Envelope hỏng (JSON lỗi, timestamp sai định dạng, `seq` không phải số) → `REJECTED_INVALID` + cảnh báo bảo mật, không treo | partial (JSON lỗi: log, không ack; timestamp/seq sai: exception bị nuốt, lệnh kẹt ở `RECEIVED` hoặc không có ack — §4 B-06) · FACT `commands.py:63-73,87,111,119,129` | M | U | `expires_at="abc"` → kỳ vọng 1 ack `REJECTED_INVALID`; `seq="x"` → `RECEIVED` rồi `REJECTED_INVALID` (hiện không có trạng thái kết thúc → đỏ). |

### 3.5 Watchdog và fail-safe (WD)

| ReqID | Yêu cầu / tiêu chí | Hiện thực? · bằng chứng | Rủi ro | Cấp | Ý tưởng test và assertion |
|---|---|---|---|---|---|
| **WD-01** · NFR-REL-002, FR-INT-018 (phần watchdog), 07 §8.6, 04 §2 "Watchdog thiết bị", D9 | Edge ghi heartbeat; thiết bị không thấy heartbeat đổi trong `revert_timeout_s` (15 s ∈ [10, 60], > 3 chu kỳ ghi 2 s) → setpoint 0, alarm, phục hồi khi heartbeat lại | yes (ở mô hình vsite) · FACT `__main__.py:115-124`; `model.py:105,117,136-144,150-157,171`; `generic_bess_pcs.yaml:12`; README §9 bước 6 | H | U, S | U (patch `time.monotonic`): không heartbeat 15,1 s → `p_setpoint==0`, `alarm_word & 0x0100`, `state==3`; heartbeat đổi → bit 0x0100 tắt; ghi setpoint cũng reset bộ đếm. S: `docker compose stop bridge` → trong 15 s + 3τ: `ess.p_setpoint_w==0`, `abs(p_w) < 1000`. |
| **WD-02** · NFR-REL-003 (tinh thần `SAFE_START`) | Khởi động lại edge không tự áp lại lệnh cũ | yes · FACT README §9 bước 6 ("setpoint vẫn là 0"); không có mã reload (`commands.py:32`) | M | S | Sau WD-01, `start bridge` → 60 s sau `ess.p_setpoint_w` vẫn 0, không có ack mới. |
| **WD-03** · NFR-REL-001, 07 §6.11 | Mất cloud: lệnh tay chạy tới `expires_at` rồi `on_expiry`; ack được đệm | partial · FACT `commands.py:182-200` (task không phụ thuộc MQTT), `commands.py:40` (ack qua outbox) | H | S | Lệnh 2 phút; dừng mosquitto 3 phút → setpoint giữ tới hạn rồi về 0 khi broker vẫn tắt; bật broker → DB có `EXPIRED`, `COMPLETED` đúng thứ tự `id`. |

### 3.6 ACL và cô lập (ACL)

| ReqID | Yêu cầu / tiêu chí | Hiện thực? · bằng chứng | Rủi ro | Cấp | Ý tưởng test và assertion |
|---|---|---|---|---|---|
| **ACL-01** · FR-INT-008, 10 §9.3, AC-INT-01 (phần ACL), FR-SEC-004 (phần MQTT) | Không anonymous; edge X chỉ publish `ems/v1/X/up/#`, chỉ nhận `ems/v1/X/down/#`; cấm đọc topic edge khác | yes (user/pass thay mTLS) · FACT `infra/mosquitto/mosquitto.conf:6`, `infra/mosquitto/acl.conf:2-3` | H | I | Kết nối không user → CONNACK thất bại. `edge-ev01` publish QoS 1 lên `ems/v1/edge-vsite01/up/telemetry/c1` → subscriber `ingest` **không** nhận (PUBACK reason ≥ 0x80 nếu broker trả — UNKNOWN với Mosquitto 2.0.20, assert theo việc không giao). `edge-ev01` subscribe `ems/v1/+/down/#` → chỉ nhận tin của `edge-ev01`. |
| **ACL-02** · 10 §9.3, README §13.3 | Chỉ `dispatcher` publish `down/cmd`; `ingest` chỉ `down/config`; edge không publish `down/*` | yes · FACT `acl.conf:8-14` | H | I, S | `ingest` publish lệnh hợp lệ lên `ems/v1/edge-vsite01/down/cmd` → 5 s không có `RECEIVED` trong `command_ack`; `edge-vsite01` tự publish `down/cmd` của mình → không RECEIVED; `dispatcher` → có RECEIVED (đối chứng). |
| **ACL-03** · FR-SEC-004, 10 §9.3 (ánh xạ edge → site ở registry cloud) | Cloud gán dữ liệu theo **danh tính kết nối/topic**, không theo `edge_id` tự khai trong payload | **partial/lỗi** · FACT `ingest.py:57,69,124,134,138` dùng `msg["edge_id"]`; không đối chiếu topic (§4 B-02) | H | I | Đăng nhập `edge-ev01`, publish trên `ems/v1/edge-ev01/up/telemetry/c1` payload `edge_id:"edge-vsite01"`, `pid:3001` → kỳ vọng bị bỏ + log bảo mật; INFERENCE hiện tại: ghi thành `meter-poc meter.p` → test **đỏ**. Tương tự cho `cmd-ack` giả `APPLIED` của lệnh edge khác. |
| **ACL-04** · 10 §9.3 (giảm rủi ro ack giả) | `TELEMETRY_ACK` không được xóa dữ liệu chưa gửi (`ack_seq ≤ seq đã gửi`) | **no** · FACT `uplink.py:99-100`, `store.py:84-88` không kiểm `sent_ms` (§4 B-07) | M | U | Outbox có seq 1–10, mới gửi 1–3; `ack_telemetry("c1", 10)` → kỳ vọng chỉ xóa 1–3 (hiện xóa 1–10 → đỏ). |

### 3.7 Cân bằng năng lượng, dấu, đơn vị, bộ đếm (BAL)

| ReqID | Yêu cầu / tiêu chí | Hiện thực? · bằng chứng | Rủi ro | Cấp | Ý tưởng test và assertion |
|---|---|---|---|---|---|
| **BAL-01** · NFR-DATA-003, 04 §0.4, 07 §7.2, AC-INT-05 (tinh thần phép thử dấu) | `meter.p` POC + = nhập; `ess.p` + = xả; PV, tải, EV ≥ 0 | yes · FACT `model.py:3,240`; README §9 bước 3 | H | U, S | S: lệnh −100 kW (sạc) → `ess.p` C1 ≈ −100 kW ± 5 kW, `ess.soc` tăng, `meter.p` POC tăng ≈ +100 kW so với trước lệnh; `min(value)` của `pv_inverter.p` và `evse.p` ≥ 0. U: `Site.step` với BESS xả → `meter_poc.p` giảm đúng P xả. |
| **BAL-02** · FR-HIST-009 (phần cân bằng), FR-HIST-013 (P1), FR-EV-001 | Mỗi phút trọn: `residual = grid − (load + ev − pv − ess) ≈ 0` (< 3 % tải; đo được ≤ 0,05 %) | partial (chỉ kiểm cân bằng, không thuật toán phân bổ có `attribution_version`) · FACT `model.py:240,253`, `tools/ems_cli.py` lệnh `balance`; README §9 bước 2 | H | U, S | U: sau `Site.step` bất kỳ, `snapshot()["balance_check_w"] == 0` (±1 W làm tròn). S: smoke 2b; thêm biến thể khi BESS xả 150 kW và khi EV sạc. Ghi nhãn: chứng minh dấu/scale/word order/pid, **không** chứng minh độ chính xác đo. |
| **BAL-03** · FR-HIST-003, FR-INT-003, NFR-DATA-004, T-FR-INT-003 | Raw W/Wh; bộ đếm int64 Wh; codec map: word order CDAB, SF âm, sentinel, I32 | yes · FACT `regmap.py:65-106` | H | U | Vector vàng: I32 −100000 BIG ↔ words; CDAB đảo word; SF −2; counter trả `int`; property-based (hypothesis) `decode(encode(x)) ≈ x` cho mọi thanh ghi của 3 map. Lưu ý R-15-01: cùng codec hai phía → cần vector độc lập (pysunspec2 cho SunSpec). |
| **BAL-04** · FR-BESS-001 (số liệu), mô hình vsite | SOC tích phân có η; CCL/DCL giảm tuyến tính gần SOC min/max; kẹp setpoint | yes (mô phỏng) · FACT `model.py:119-124,158-170` | M | U | Sạc 100 kW trong 36 s mô phỏng, E=500 kWh, η=0,95 → ΔSOC = +0,19 % ± 0,005; SOC=12,5 % → `pdis == 250000·(12,5−10)/5 = 125000`. Đây là oracle cho test S nên phải đúng. |
| **BAL-05** · FR-HIST-004 (một phần), AC-HIST-03 (một phần) | Bộ đếm giảm bất thường → sự kiện; bộ đếm phiên EV không sinh reset giả | partial (chỉ `COUNTER_RESET`; không ROLLOVER/`R_wrap`, không chống rung ±2 LSB, không `ESTIMATED`; trạng thái bộ đếm trong RAM) · FACT `ingest.py:37-39,76-77,108-116`; `site.yaml` `monotonic: false` cho `evse.e_session` | M | I, S | I: lô C4 `raw` 9259 rồi 1138 → 1 hàng `event` COUNTER_RESET `payload.prev_raw==9259`; `evse.e_session` giảm → 0 sự kiện; giảm 1 Wh (trong ±2 LSB) → kỳ vọng doc: không reset (hiện có → đỏ). S: `fault meter-poc --counter-reset` (D11). |

### 3.8 EV / OCPP (EV) — FR-EV là P1, PoC đã có một phần

| ReqID | Yêu cầu / tiêu chí | Hiện thực? · bằng chứng | Rủi ro | Cấp | Ý tưởng test và assertion |
|---|---|---|---|---|---|
| **EV-01** · FR-EV-005, AC-EV-03, T-FR-EV-005, 10 §11.6, D10 | `SET_EV_LIMIT` qua SetChargingProfile có `validTo`; I ≥ 6 A hoặc 0; hết hạn → TxDefaultProfile an toàn; `EXPIRED→COMPLETED` | partial (không idempotency/`seq`/`max_latency`; lệnh chồng nhau hỏng — §4 B-08) · FACT `csms.py:148-157,203-231` | M | U, S | S: `send-ev-limit --amps 10 --minutes 2` → `APPLIED` có `readback.value=="Accepted"`, `evse.p` C1 < 11 kW trong 30 s; `--amps 5` → `REJECTED_OUT_OF_LIMIT/BELOW_I_MIN_6A`; hết hạn → `EXPIRED`, `COMPLETED`, `evse.i_limit_active` về 32. U: `handle_command` với `cp` giả. |
| **EV-02** · FR-EV-001 | EV tách khỏi tải trong cân bằng; `evse.p` C1 từ MeterValues | yes · FACT `csms.py:93-103,113-124,188-200`; `model.py:223-224,237-238` | M | S | `coverage` có `evse.p`; cân bằng BAL-02 đúng khi EV sạc ~22 kW; vsite `p_ev_w` về 0 sau 30 s không cập nhật (dừng `csms`). |
| **EV-03** · FR-EV-002 (P1) | Giám sát trạng thái connector và năng lượng phiên | partial · FACT `csms.py:125-128,163-169` | L | S | `event` có `EVSE_STATUS` cho Preparing/Charging/Finishing; `evse.e_session` C4 tăng trong phiên. |
| **EV-04** · NFR-SEC-021 (phần TxDefaultProfile), 07 §5.9 | TxDefaultProfile an toàn sau boot | partial (Security Profile ≥ 2 **không** có) · FACT `csms.py:141-146` | M | S | Sau `BootNotification`, log `SetChargingProfile TxDefaultProfile 32 A … Accepted`; `evse.i_limit_active == 32`. |

### 3.9 Trạng thái edge, phiên MQTT, simulator, driver, đo hiệu năng

| ReqID | Yêu cầu / tiêu chí | Hiện thực? · bằng chứng | Rủi ro | Cấp | Ý tưởng test và assertion |
|---|---|---|---|---|---|
| **ST-01** · 07 §7.1 (LWT), NFR-REL-008 (phần edge), FR-MON-008 (dữ liệu) | Will `{"online":false}` retained, Will Delay 2 s; state retained khi kết nối và mỗi 30 s | partial (cloud chưa tính OFFLINE sau 90 s) · FACT `uplink.py:54-58,85,102-107`, `__main__.py:128` | M | I, S | `docker kill bridge` → trong `1,5×30 s + 2 s` `edge_state.payload.online == false`; subscriber mới nhận ngay tin retained. |
| **ST-02** · 07 §8.2a (phiên) | `clean_start=false`, Session Expiry 3600 s → lệnh còn hạn vẫn tới sau rớt mạng ngắn | yes · FACT `uplink.py:67-69` | M | S | Dừng bridge 10 s (< watchdog), gửi lệnh hạn 5 phút, bật bridge → có `RECEIVED` và `APPLIED`. |
| **SIM-01** · FR-INT-014 | Bộ mô phỏng nội bộ có tiêm lỗi (comm_loss, exception, frozen, sentinel, alarm, counter_reset, clock_offset, bms_derate) | partial (chưa có "thiết bị không watchdog", chưa Toxiproxy) · FACT `simulators/vsite/vsite/server.py:25-28,111-130`, `vsite/__main__.py:57-101` | M | I | Mỗi lỗi qua REST → client Modbus thấy: timeout; exception đúng mã; thanh ghi không đổi 3 s (`frozen`); words = `na_values`; `DELETE /faults/{id}` khôi phục. Đây là test **của hạ tầng test**. |
| **SIM-02** · FR-INT-005 (chỉ phía thiết bị ảo) | Ảnh SunSpec 1/701/704 sinh bằng pysunspec2, khám phá được | partial (bridge không có khám phá SunSpec) · FACT README §6, §9 | L | I | Client pysunspec2 độc lập quét `[1,701,704]`; ghi `704.WMaxLimPct=50` → `701.W ≤ 50 kW`. |
| **INT-01** · FR-INT-004, T-FR-INT-004 | Gom block ≤ 125 thanh ghi/lần đọc, không vắt qua lỗ địa chỉ | yes · FACT `regmap.py:126-138` | M | U | Với 3 map: mọi block `end−start ≤ 125`; khoảng cách giữa thanh ghi trong block ≤ `max_gap`. |
| **INT-02** · FR-INT-003 (`access`), 07 §6.2 | Chỉ ghi thanh ghi có quyền W; ghi nửa giá trị 32 bit → exception 02 | yes · FACT `poller.py:133-145`; README §6 | M | U, I | `write("ess.p", …)` → `"NOT_WRITABLE"` không gửi PDU; I: FC16 1 word vào I32 setpoint → exception 02. |
| **PERF-01** · NFR-PERF-005 | p95 CREATED/SENT→RECEIVED ≤ 5 s; RECEIVED→APPLIED ≤ 15 s | partial (đo được ở edge PoC, chưa có Command API) · FACT `command_ack.ts`, `command.envelope.sent_at` (`init.sql:33-53`) | M | S | 20 lệnh: `RECEIVED.ts − sent_at` p95 ≤ 5 s; `APPLIED.ts − RECEIVED.ts` p95 ≤ 15 s. Nhãn "Mô phỏng". |
| **PERF-02** · NFR-PERF-003 | p95 `ts_ingest − ts` ≤ 10 s cho C1, ≤ 60 s cho C2 | partial (đo được; `ts` là đầu cửa sổ nên độ trễ gồm `w + 0,5 s`) · FACT `init.sql:19`, `aggregate.py:85` | M | S | 10 phút: p95(`ts_ingest − ts`) C1 ≤ 10 s, C2 ≤ 60 s + `w` (ghi rõ cách hiểu `ts`, xem §8 Q3). |

---

## 4. Lỗi và lệch tài liệu phát hiện khi ánh xạ

A2 chỉ đọc, **không sửa**. "INFERENCE" = suy ra từ đường mã, chưa chạy; cần test đỏ trước khi sửa. Chủ sở hữu thư mục quyết định sửa.

| # | Mô tả | Bằng chứng | Nhãn | Rủi ro | Test xác nhận |
|---|---|---|---|---|---|
| B-01 | BMS cũ trả `REJECTED_INTERLOCK:IL-04`; 10 §11.4 định nghĩa **IL-03** = BMS cũ, **IL-04** = mất `MTR_POC`; 04 AC-BESS-04 cũng ghi IL-03. README §5 lặp lại IL-04. | `edge/bridge/bridge/commands.py:137`; `10-security-and-reliability.md:731-732`; 04 AC-BESS-04 | FACT (lệch hợp đồng) | H (mã interlock sai làm sai cảnh báo/runbook) | CMD-12 |
| B-02 | Ingest lấy `edge_id` từ payload, không đối chiếu với topic/danh tính → edge A ghi telemetry/ack/event/state dưới tên edge B (ACL chỉ chặn topic, không chặn nội dung). | `ingest/ingest.py:57,69,124,134,138`; `acl.conf:2` | INFERENCE | H (cô lập edge/tenant, giả "APPLIED") | ACL-03 |
| B-03 | Lệnh đang hiệu lực chỉ nằm trong RAM; bridge khởi động lại < 15 s (watchdog chưa kịp) → không còn task hết hạn → setpoint cũ giữ **vô hạn** (vi phạm BR-BESS-06). Bảng `command.expires_ms` có nhưng không được đọc lại lúc khởi động. | `commands.py:32,180`; `store.py:31-33,101-107`; `model.py:147,151-157` | INFERENCE | H | CMD-19 |
| B-04 | Supersede xảy ra **trước** khi ghi lệnh mới: task hết hạn của lệnh cũ bị hủy và ack `SUPERSEDED`; nếu lệnh mới `FAILED_*` thì `active` vẫn trỏ lệnh cũ đã hủy → setpoint cũ không bao giờ hoàn nguyên. | `commands.py:152-160,171-172` | INFERENCE | H | CMD-17 (ca âm) |
| B-05 | `lifetime()` luôn ngủ 8 s trước khi xét hạn → lệnh còn < 8 s khi APPLIED hoàn nguyên trễ tới 8 s (AC-BESS-03 yêu cầu ±1 chu kỳ). | `commands.py:185,193-196` | INFERENCE | M | CMD-16 (U) |
| B-06 | `parse_ts(expires_at)` chạy trước `RECEIVED`; timestamp/`seq` sai định dạng ném exception bị `run()` nuốt → không có ack kết thúc (lệnh kẹt `RECEIVED` hoặc không ack nào). | `commands.py:63-65,87,111,119,129` | INFERENCE | M | CMD-20 |
| B-07 | `TELEMETRY_ACK` xóa mọi hàng `seq ≤ ack_seq` kể cả chưa gửi; 10 §9.3 yêu cầu kiểm `ack_seq ≤ seq đã gửi`. | `uplink.py:99-100`; `store.py:84-88` | INFERENCE | M (mất dữ liệu khi ack giả/lỗi) | ACL-04 |
| B-08 | CSMS: (a) không idempotency — trùng `command_id` thực thi lại; (b) hai `SET_EV_LIMIT` chồng nhau dùng chung `profile_id=2`: hết hạn lệnh cũ gọi `ClearChargingProfile(id=2)` xóa luôn profile của lệnh mới và đặt `i_limit=32`. | `simulators/evse/csms/csms.py:203-231` (đặc biệt 222, 227-229) | INFERENCE | M (P1) | EV-01 mở rộng |
| B-09 | `p_w=true` qua kiểm `isinstance(..., (int, float))` (bool là int) → setpoint 1 W. | `commands.py:109` | INFERENCE | L | CMD-03 |
| B-10 | `command_ack` không khử trùng; ack được xóa khỏi outbox khi PUBACK nên QoS 1 giao lại → hàng trùng; `command.last_state` = tin đến sau cùng. | `ingest.py:118-127`; `init.sql:45-53` | INFERENCE | L | I: publish cùng ack 2 lần → hiện 2 hàng |
| B-11 | Response Topic lạ chỉ ghi log, không sinh sự kiện bảo mật (07 §8.2a). | `commands.py:77-78` | FACT (thiếu) | L | CMD-09 |
| B-12 | Trạng thái bộ đếm cho `COUNTER_RESET` chỉ trong RAM → reset xảy ra quanh lúc ingest khởi động lại bị bỏ sót. | `ingest.py:39,108-111` | INFERENCE | L | BAL-05 |

**Lệch giữa các tài liệu (không phải lỗi mã):**

- AC-SEC-04 (04): phát lại **cùng** envelope → `REJECTED_REPLAY`. 07 §8.7 A.4 và 10 §11.7: trùng `command_id` → trả trạng thái cũ, không thực thi lại. PoC theo 07 (FACT `commands.py:79-86`). Test nên assert điều chung của cả hai: **không thực thi lại** + có cảnh báo; trạng thái trả về cần chốt (Q1 §8).
- AC-BESS-04: BMS cũ → setpoint = 0 trong ≤ 2 chu kỳ **và** từ chối lệnh mới. PoC chỉ từ chối lệnh mới; không có vòng an toàn cục bộ ở edge (README §14). Tính là `partial`.
- 10 §9.3: ingest chỉ subscribe `up/{state,telemetry,event,backfill}`; PoC cho đọc `up/#` (gồm `cmd-ack`) và publish `down/config` (README §13.3 đã ghi).

---

## 5. Yêu cầu CHƯA hiện thực (ngoài phạm vi test hiện tại)

Không tính vào mẫu số độ phủ. Khi backend Java/Angular xuất hiện, các mục này chuyển vào bảng §3 (cấp I/E).

| Nhóm | Mã (04) | Lý do không test bây giờ |
|---|---|---|
| Toàn bộ UI | Mọi FR có hiển thị: FR-MON-004…008 (phần UI), 010, 011; FR-HIST-010; FR-DASH-*, FR-REP-* | Chưa có Angular. Grafana chỉ là dashboard PoC (README §14). |
| Độ tươi | FR-MON-005, AC-MON-01…03, BR-MON-01 | Không có tính `freshness`; chỉ có dữ liệu thô (`ts`, `ts_ingest`) để làm sau. |
| Giám sát khác | FR-MON-003 (connector cloud hãng), 006, 007, 009 (FROZEN), 011–013 | Không có connector, không có phát hiện FROZEN (vsite có lỗi `frozen` nhưng cloud không phát hiện). |
| Lịch sử/DQ | FR-HIST-005, 006, 008, 010–012, 014–017; NFR-DATA-006…013 | Không có aggregate 5 phút/1 h, dữ liệu trễ, lấp khoảng, retention, Parquet. |
| Tổ chức/biểu giá/tối ưu/cảnh báo/nâng cao | FR-ORG-*, FR-TAR-*, FR-OPT-*, FR-ALM-*, FR-ADV-*, FR-PV-* | Không có mã. |
| BESS ngoài `SET_ESS_P` | FR-BESS-002, 003, 004, 006, 010, 012–020 (FR-BESS-011 "cấm" chỉ kiểm được bằng quét API khi có API) | PoC chỉ có `SET_ESS_P`; lệnh khác → `REJECTED_UNSUPPORTED` (CMD-03). |
| Lưới | FR-GRID-001…019, NFR-REL-009, AC-GRID-* | Không có vòng zero-export/trần nhập, không cấu hình lưới. `metering_point: MTR_POC` chỉ là nhãn trong `site.yaml`. |
| EV nâng cao | FR-EV-003 (Security Profile ≥ 2), 004, 006–010 | OCPP 1.6J không bảo mật (README §14). |
| Tích hợp | FR-INT-001, 002 (claim, mTLS), 005 (khám phá ở edge), 006, 010 (đồng bộ giờ, IL-06), 012, 013, 015–017, 019–031 | Không có. `clock_state` cứng `SYNCED` (`__main__.py:82`). |
| Bảo mật/điều khiển | FR-SEC-001, 002, 003, 005, 007, 011–014, 016–022 | Không PDP, MFA, RLS, phê duyệt C3, kill switch, Governor, audit append-only, Vault, giới hạn tốc độ (`min_write_interval_ms` có trong map nhưng không được thực thi). JWS: envelope `signature: "UNSIGNED-POC"` (`tools/ems_cli.py:89`). |
| NFR hiệu năng | NFR-PERF-001, 002, 004, 006–012 | Cần UI, tải 1.000 site, vòng điều khiển. |
| NFR tin cậy | NFR-REL-004…006, 009–011, 013, 015, 017, 018 | Không có SLO, DR, `run_mode`, kill switch, chứng chỉ. |
| NFR quan sát | NFR-OBS-001, 003…009 | Log không JSON có `trace_id`; không metric. |
| NFR bảo mật | NFR-SEC-001, 002, 005–009, 012–020, 022–033 | Như FR-SEC. |

---

## 6. Tính độ phủ

**Mẫu số theo mã yêu cầu** [FACT: đếm từ §3; tổng theo 12 "Phạm vi": 268 FR, 85 NFR]:

| Loại | Mã có hiện thực `yes`/`partial` trong PoC | Số |
|---|---|---|
| FR | FR-MON-001, 002 · FR-HIST-001, 002, 003, 004, 007, 009, 013 · FR-BESS-001, 005, 007, 008, 009 · FR-EV-001, 002, 005 · FR-INT-003, 004, 007, 008, 009, 011, 014, 018 · FR-SEC-004, 006, 008, 009, 010, 015 | 31 / 268 |
| NFR | NFR-PERF-003, 005 · NFR-REL-001, 002, 003, 007, 008, 012, 014, 016 · NFR-DATA-001, 002, 003, 004, 005 · NFR-OBS-002 · NFR-SEC-003, 004, 010, 011, 021 | 21 / 85 |
| Tổng | | **52 / 353 = 14,7 %** sản phẩm đích có gì đó để test |

Ghi chú: FR-HIST-001 (catalog = registry pid trong `site.yaml`, pid lạ bị bỏ `ingest.py:69-72`), FR-HIST-007 (chỉ tầng điểm), FR-SEC-015 (chỉ bảng `command_ack`, không UI) là `partial` mức thấp.

**Độ phủ test trên phạm vi đã hiện thực (68 dòng ở §3)** — INFERENCE từ đọc `tests/smoke.sh`, A2 **không chạy**:

| Trạng thái bằng chứng | Dòng | Số | % trên 68 |
|---|---|---|---|
| Có assertion tự động (`tests/smoke.sh`) | TEL-05 (chỉ "có dữ liệu"), CMD-07, CMD-08, CMD-10 (chỉ ca vui), CMD-14 (chỉ APPLIED), BAL-01, BAL-02, EV-02 | 8 | 11,8 % |
| Chỉ có chạy tay trong README §9 (D7–D11) | SF-01, SF-05, WD-01, WD-02, CMD-13, CMD-16, EV-01, QUAL-03 | 8 | 11,8 % |
| Chưa có bằng chứng chạy nào | 52 dòng còn lại | 52 | 76,5 % |

Phân bố rủi ro 68 dòng: H = 34, M = 30, L = 4. Đề xuất ưu tiên: (1) U cho `CommandHandler`, `Store`, `Aggregator`, `regmap`, `Bess` — chạy < 10 s, không Docker, phủ ~30 dòng; (2) I cho ACL và ingest (Mosquitto + Postgres) — gồm 3 test đỏ B-02, B-07, B-10; (3) S tự động hóa D7–D11 + CMD-19 + WD-03.

Độ phủ mục tiêu đề xuất cho vòng này: 100 % dòng `H` có ít nhất 1 test U/I/S tự động; test cho B-01…B-07 được đánh dấu `xfail(strict=True)` với mã lỗi tới khi chủ thư mục sửa.

---

## 7. Điểm nối (seam) cần cho test và gợi ý cho framework

| Thành phần | Seam đã có | Thiếu / đề xuất (không đổi hành vi) |
|---|---|---|
| `edge/bridge/bridge/commands.py` | `CommandHandler(edge_id, store, uplink, ess_poller, soe, rated_w)` nhận phụ thuộc qua constructor; `ess` chỉ cần `image`, `write`, `read_point` | `now_ms` import trực tiếp → patch `bridge.commands.now_ms`; `asyncio.sleep(8)` cứng (`commands.py:185`) → nên thành tham số `tracking_delay_s` để test nhanh. |
| `edge/bridge/bridge/store.py` | Đường dẫn SQLite tự chọn → `tmp_path` | — |
| `edge/bridge/bridge/aggregate.py` | Thuần; `WINDOW_S` đọc env lúc import | Đặt env trước import hoặc patch `WINDOW_S`. |
| `edge/bridge/bridge/poller.py` | `self.client` thay được bằng client giả | `_handle_error` dùng được trực tiếp. |
| `ingest/ingest.py` | Lớp `Ingest`, cần DB thật | Logic `ack_seq` tích lũy (`ingest.py:86-102`) nên tách hàm thuần; `self.client` cần giả để bắt TELEMETRY_ACK. |
| `simulators/vsite/vsite/model.py` | Thuần (dataclass) | `time.monotonic` cần patch cho watchdog/EV timeout. |
| Import path | Container dùng `PYTHONPATH=/app/maps:/app` (FACT `edge/bridge/Dockerfile:12`) | Test host: `PYTHONPATH=edge/bridge:simulators/vsite/maps:simulators/vsite`. Python host 3.13, container 3.12 — chạy U ở cả hai nếu được. |
| Hợp đồng (C) | JSON Schema rút gọn ở 07 §7.3 | Đặt schema thành file dùng chung (vd. `tests/contract/schemas/ems.telemetry.v1.json`) để edge Java sau này cũng chạy được; thêm schema cho `ems.cmd-ack.v1`, `ems.event.v1`, `ems.state.v1`, `ems.command.v1` (chưa có trong 07 — UNKNOWN chính thức). |
| Thông tin đăng nhập test | `infra/.env.example` | Chỉ lấy từ env; ACL-01/02 cần đăng nhập bằng từng user (`edge-vsite01`, `edge-ev01`, `ingest`, `dispatcher`). |
| Chỗ cắm Java/Angular | — | Giữ test C/S ở mức hợp đồng MQTT/DB/REST (không import Python của PoC) để dùng lại khi Spring Boot thay `ingest`/`ems_cli`. |

---

## 8. UNKNOWN và câu hỏi mở

1. **Q1** Phát lại cùng envelope: trả trạng thái cũ (07/10, PoC) hay `REJECTED_REPLAY` (04 AC-SEC-04)? Cần chủ 04/07 chốt; test hiện assert "không thực thi lại".
2. **Q2** Exception 04/06 trong `max_age`: giá trị giữ lại gắn `GOOD` (PoC `poller.py:127`) hay mã khác? 07 §5.1.5 không nói. UNKNOWN.
3. **Q3** NFR-PERF-003 đo `ts_ingest − ts` với `ts` = **đầu** cửa sổ: C1 luôn mang sẵn ≥ 5,5 s độ trễ. Cần chốt đo từ đầu hay cuối cửa sổ.
4. **Q4** Mosquitto 2.0.20 có trả PUBACK reason code `0x87` cho publish bị ACL từ chối với client MQTT 5 hay im lặng? UNKNOWN — test ACL-01 nên assert "không giao tới subscriber", không dựa vào reason code.
5. **Q5** `sqlite3` của Python với `journal_mode=WAL` và `synchronous` mặc định có fsync trước khi chấp nhận lệnh (NFR-REL-014)? INFERENCE là có (FULL), cần kiểm `PRAGMA synchronous` trong container.
6. **Q6** Schema chính thức cho `ems.cmd-ack.v1`, `ems.event.v1`, `ems.state.v1` chưa có trong 07 (chỉ có ví dụ). Test C cho các tin này dựa trên hình dạng PoC, cần đánh dấu "PoC schema".
