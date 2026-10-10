# A1 — Audit mã nguồn PoC EMS dưới góc nhìn kiểm thử

- Ngày: 2026-10-10 · Vai trò: QA Architect (assessment, code) · Trạng thái: **xong vòng 1**
- Phạm vi: toàn bộ mã sản phẩm hiện có: `simulators/vsite` (model, server, `__main__`, maps + `regmap.py`), `edge/bridge/bridge/*`, `ingest/ingest.py`, `simulators/evse/csms/csms.py`, `tools/ems_cli.py`, `infra/` (compose, mosquitto conf/ACL/entrypoint, `db/init.sql`, `config/site.yaml`, Grafana provisioning), `tests/smoke.sh`.
- Đầu vào hợp đồng: [infra/README.md](../../../infra/README.md), [07 Tích hợp thiết bị](../../research/ems/07-device-integration.md) (§5.1.5, §6.9–§6.12, §7, §8.4–§8.7, §11.3), [04 Yêu cầu](../../research/ems/04-business-requirements.md) (FR-INT-*).
- **Read-only với mã sản phẩm.** Không sửa file nào ngoài `docs/testing/notes/`. Không chạy Docker (không sở hữu stack).

## Mục lục

1. [Phương pháp và nhãn bằng chứng](#1-phương-pháp-và-nhãn-bằng-chứng)
2. [Tóm tắt điều hành](#2-tóm-tắt-điều-hành)
3. [Bản đồ thành phần](#3-bản-đồ-thành-phần)
4. [Audit theo thành phần](#4-audit-theo-thành-phần)
5. [Danh sách bug nghi ngờ / đã tái hiện](#5-danh-sách-bug)
6. [Vấn đề testability (tổng hợp) và seam đề xuất](#6-testability)
7. [Rủi ro production](#7-rủi-ro-production)
8. [Xếp hạng: cái gì cần test nhất](#8-xếp-hạng-cần-test)
9. [Lệnh đã chạy và kết quả](#9-lệnh-đã-chạy)

---

## 1. Phương pháp và nhãn bằng chứng

- Đọc toàn bộ mã (3 167 dòng Python/YAML/SQL/shell — `wc -l`), đối chiếu với README và 07.
- Với mỗi nghi ngờ rẻ để kiểm, viết script Python gọi **trực tiếp lớp sản phẩm** (không sửa chúng) với fake I/O: `docs/testing/notes/A1-repro/a1_repro.py` (R1–R15) và `a1_repro2.py` (R16–R19). Chạy bằng `.venv` (Python 3.13.16, cùng phiên bản thư viện ghim trong `requirements.txt`).
- Nhãn:
  - **FACT** — có `file:line` hoặc đầu ra lệnh.
  - **REPRODUCED** — bug đã tái hiện bằng script ở trên (đầu ra ghi ở §5).
  - **SUSPECTED** — suy từ đọc mã, chưa tái hiện.
  - **INFERENCE** — suy luận về hệ quả/kịch bản kích hoạt.
  - **UNKNOWN** — chưa đủ dữ liệu.
- Giới hạn: tái hiện ở mức đơn vị (fake DB, fake Modbus, fake MQTT). Chưa tái hiện trên stack Docker thật; Python host 3.13 trong khi image dùng 3.12 (UNKNOWN: khác biệt hành vi, khả năng thấp với mã này).

## 2. Tóm tắt điều hành

| # | Phát hiện | Mức | Nhãn |
|---|---|---|---|
| 1 | Ba đường lỗi của lệnh BESS để setpoint **ở lại thiết bị sau `expires_at`** (supersede rồi ghi lỗi; readback lỗi; ghi hoàn nguyên lỗi nhưng vẫn báo `COMPLETED`) | Cao (an toàn) | REPRODUCED (R6, R7, R8) |
| 2 | Ingest tin `edge_id` **trong payload**, không đối chiếu topic → edge này ghi dữ liệu và gửi `TELEMETRY_ACK` thay edge khác (có thể làm edge kia xóa buffer chưa commit) | Cao (bảo mật + mất dữ liệu) | REPRODUCED (R10) |
| 3 | Ack tích lũy của ingest khởi tạo từ seq nhỏ nhất **đã thấy** → lô đầu tiên đến là seq 6 thì ack 6, edge xóa seq 1..5 chưa vào DB | Cao (mất dữ liệu, kịch bản khởi động) | REPRODUCED logic (R11), kích hoạt INFERENCE |
| 4 | Một lỗ seq vĩnh viễn (poison batch ở ingest hoặc crash giữa `next_seq` và `enqueue`) làm ack đứng yên mãi → outbox edge phình, gửi lại mọi lô mỗi 20 s | Trung bình–Cao | REPRODUCED (R12) + SUSPECTED kích hoạt |
| 5 | `COUNTER_RESET` giả khi backfill (cũ, nhỏ hơn) đến sau dữ liệu live | Trung bình | REPRODUCED (R13) |
| 6 | Envelope lệnh sai định dạng (thời gian, `danger_class`, `seq`) → exception bị nuốt, **không có ack kết thúc** (07 §8.7-A.3 yêu cầu `REJECTED_INVALID`) | Trung bình | REPRODUCED (R9) |
| 7 | `down/config` sai định dạng làm exception trong callback paho (`suppress_exceptions=False`) → luồng mạng MQTT chết, bridge vẫn "healthy" | Trung bình | REPRODUCED (R14) + nguồn paho |
| 8 | `ess.clock` có trong map nhưng model không cấp → `ts_src = 0` → sự kiện alarm BESS có `ts_src` 1970-01-01; fault `clock_offset_s` trên `ess-01` không có tác dụng | Trung bình | REPRODUCED (R1) |
| 9 | Aggregator mất trọn cửa sổ khi đồng hồ tường lùi | Trung bình | REPRODUCED (R17) |
| 10 | Chỉ có **một** test (smoke e2e cần Docker); toàn bộ logic an toàn lệnh, store-and-forward, codec không có test đơn vị | — | FACT (`tests/` chỉ có `smoke.sh`) |

Kết luận cho thiết kế framework (INFERENCE): phần lớn rủi ro nằm ở **logic thuần** (CommandHandler, Store, Aggregator, Ingest, regmap, Bess) và **đã có thể test đơn vị không cần Docker** với fake — R6–R13 chứng minh điều đó. Tầng Docker (L3/L4) nên dành cho hợp đồng dây (Modbus, MQTT 5, ACL, PG) và kịch bản e2e D1–D12.

## 3. Bản đồ thành phần

```
vsite.model (vật lý) ──values()/on_write()──► vsite.server.DeviceServer.action ──Modbus TCP──► bridge.poller.EndpointPoller
      ▲ REST /faults /ev /clock (vsite.__main__)                                                     │ Reading(value,q,ts,ts_src)
csms.py ──POST /ev──┘                                                                                ▼
                                                     bridge.aggregate.Aggregator (C1–C4) ; C5 → event (bridge.__main__.on_reading)
                                                                                                     ▼ next_seq + enqueue
                                                                                bridge.store.Store (SQLite outbox, seq, command, signer_seq)
                                                                                                     ▼ drain thread
                                                    bridge.uplink.Uplink (paho MQTT5) ◄── down/cmd ── tools/ems_cli.py (dispatcher)
                                                                       │  ▲ down/config TELEMETRY_ACK            ▲
                                                                       ▼  │                                        │
                                                         mosquitto (ACL) ──$share──► ingest.Ingest ──► PostgreSQL/Timescale ◄── CLI/Grafana
bridge.commands.CommandHandler ── write/read_point ──► EndpointPoller(ess-01) ; heartbeat_loop ─► _ess.heartbeat (watchdog vsite)
```

Mã dùng chung quan trọng: `simulators/vsite/maps/regmap.py` được **cả vsite (encode) và bridge (decode)** dùng (FACT: `edge/bridge/Dockerfile` `COPY --from=maps`). Hệ quả (INFERENCE, README cũng nêu R-15-01): test e2e vsite↔bridge không bắt được lỗi map đối xứng; cần **vector vàng độc lập** cho codec.

## 4. Audit theo thành phần

### 4.1 `simulators/vsite/vsite/model.py` — vật lý site

**Trách nhiệm** (FACT): đồng hồ kịch bản (`Clock`, :22-38), profile PV/tải nội suy (`Profile`, :41-54), `Inverter` (:57-89), `Bess` (:92-171), `Meter` (:174-199), `Site.step` cân bằng tại POC (:202-242), `snapshot` (:244-256).

**Logic và bất biến cần test**

| Bất biến | Vị trí | Ghi chú |
|---|---|---|
| Cân bằng `P_grid = P_load + P_ev − P_pv − P_ess` | model.py:240 | `balance_check_w` (:253) tính lại từ **cùng biến** → luôn 0 theo cấu trúc (FACT); không phải oracle độc lập. Oracle thật là `ems balance` qua dây (README D2). |
| Dấu: `ess.p` + = xả → SOC giảm; − = sạc → SOC tăng | :164-169 | |
| Hiệu suất: sạc `+|P|·η_c·Δt/E`, xả `−P·Δt/(η_d·E)` | :165, :168 | Test: chu trình sạc rồi xả cùng năng lượng AC → SOC cuối < SOC đầu (tổn hao). |
| CCL/DCL giảm tuyến tính trong dải `taper_pct` gần `soc_min/soc_max`; `bms_derate_w` lấy min | :119-124 | |
| Lệnh bị kẹp `[-pch, pdis]`; trễ bậc 1 theo **giờ tường**; |p|<1 W → 0 | :159-162 | |
| SOC chỉ kẹp cứng `[0, 100]`; `soc_min/max` chỉ giữ nhờ taper | :170 | Vượt `soc_max` khi `SIM_SPEED` lớn (A1-BUG-14). |
| Watchdog: heartbeat không đổi > `watchdog_s` → setpoint 0, alarm `0x0100`, state 3; heartbeat đổi → xóa | :137-157 | Ghi `ess.p_setpoint` cũng làm mới bộ đếm (:147) — thiết kế có chủ ý. |
| Năng lượng tích phân theo **giờ mô phỏng**, động học theo giờ tường | :4, :88, :163, :197-199 | `SIM_SPEED>1` làm Wh ≠ ∫P dt tường (README §14). |
| PV ≥ 0, kẹp theo `p_limit_pct` chỉ khi `p_limit_ena` | :85-86 | |
| Bộ đếm công tơ: `p ≥ 0` → `e_import`, ngược lại `e_export` | :196-199 | |
| EV về 0 nếu 30 s (giờ tường) không cập nhật | :221, :237-238 | |

**Testability**
- Tốt: lớp thuần, không I/O ngoài `Profile(path)`; `Site(scenario_dict, profile, ids)` dễ dựng (FACT: R3, R5 dựng trực tiếp).
- Kém: gọi trực tiếp `time.monotonic()` (:114, :140, :147, :151, :224, :237) và `time.time()` (:188) → phải monkeypatch module `time` (R5 làm vậy; cần cẩn thận vì patch toàn cục — xem §6). `random` toàn cục không seed cho nhiễu (:71, :185-187) → giá trị không tái lập; `shares` thì seed 42 (:211).
- `Clock(start_local)` chỉ nhận `HH:MM` (:27); `/clock` không kiểm tốc độ âm.

### 4.2 `simulators/vsite/vsite/server.py` — Modbus SimDevice

**Trách nhiệm** (FACT): ảnh SunSpec 1/701/704 sinh bằng pysunspec2 và **kiểm chéo địa chỉ YAML lúc khởi động** (:34-64); SimData chỉ cho ghi thanh ghi RW (:84-93); hook `action` trước mọi request: tiêm lỗi → xử lý ghi (từ chối ghi một phần thanh ghi 32 bit/vùng RO bằng exception 02) → làm mới thanh ghi từ model (:111-130).

**Bất biến**: ghi phải phủ trọn các thanh ghi RW chạm tới (:119-123); `sentinel` thay giá trị bằng `na_values[0]` (:107-108); `frozen` ngừng refresh (:128-129); `comm_loss` ngủ 30 s rồi trả `GATEWAY_NO_RESPONSE` (:113-115).

**Testability**: `refresh()` và `action()` gọi được không cần mạng (R1 gọi `refresh` với `regs` giả — FACT). API `SimDevice` "experimental" ở pymodbus 3.15 (README §11) → ghim phiên bản là bắt buộc; test hợp đồng nên chạy client pymodbus thật vào server thật (L3, không cần Docker: server bind cổng cục bộ).

**Bug**: thanh ghi có trong map nhưng model không cấp giá trị bị bỏ qua lặng lẽ (`r.point not in vals` → `continue`, :104) → `ess.clock` = 0 mãi (A1-BUG-09). Đề xuất test lint: mọi điểm `R` của map phải có trong `model.values()` (trừ `_sf.*`).

### 4.3 `simulators/vsite/maps/*.yaml` + `regmap.py` — codec dùng chung

**Trách nhiệm**: `Register.to_words/from_words` (word order BIG/LITTLE_WORD, có dấu, F32), `encode/decode` (scale, `scale_ref` SF, offset, `sign_transform`, `na_values`, counter → int), `RegisterMap.blocks()` gom khối ≤ 125 thanh ghi với `max_gap`.

**Bất biến cần test (vector vàng, T-FR-INT-003)**: I32 CDAB, SF âm, sentinel 0xFFFF / −32768, U64 counter, gom khối không vắt qua lỗ khi `max_gap: 0`, khối ≤ 125.

**Testability**: thuần, rất dễ test (FACT: R2). `by_point` là `@property` dựng lại dict mỗi lần gọi (regmap.py:118) — gọi trong vòng poll (poller.py:93) → chi phí thừa (hiệu năng, thấp).

**Bug**: `to_words` mask không kiểm phạm vi (regmap.py:70) → `encode(2**31)` I32 giải mã thành `−2147483648`; U16 `encode(−5.0)` → `6548.6` (REPRODUCED R2). Hiện ESS setpoint đã được kẹp nên chưa kích hoạt (INFERENCE) nhưng là bẫy cho lệnh mới (A1-BUG-15).

**Map**: `generic_bess_pcs.yaml` khai `ess.clock` (dòng `address: 23`) nhưng model không cấp (A1-BUG-09). `min_write_interval_ms`, `persist`, `readback_ref`, `register_wrap` được khai báo nhưng **không mã nào dùng** (FACT: grep chỉ thấy trong `regmap.py` dataclass) → không có hành vi để test; ghi chú để không viết test giả.

### 4.4 `simulators/vsite/vsite/__main__.py` — REST tiêm lỗi + vòng vật lý

**Trách nhiệm**: `build()` đọc scenario + env + site.yaml (:23-47); REST `/health`, `/state`, `PUT/DELETE /faults/{id}`, `/ev`, `/clock` (:50-120); `physics()` bước 0,2 s (:123-136).

**Testability**: `api(site, servers, faults)` trả `web.Application` → test được bằng aiohttp test client không cần Modbus (INFERENCE). `build()` trộn I/O file + env + chọn model.

**Bug/rủi ro**:
- Không kiểm kiểu/giá trị body: `bms_derate_w` gán thẳng (:81-82) → chuỗi làm `Bess.limits()` ném `TypeError` (REPRODUCED R4) trong `physics()` không có try/except → `asyncio.gather` (:156) kết thúc → tiến trình vsite thoát (INFERENCE; container `restart: unless-stopped` sẽ khởi động lại, mất trạng thái SOC). `exception: 99` → `ExcCodes(99)` ném `ValueError` trong `action` (SUSPECTED).
- `DELETE /faults/{unknown}` trả 200 (:86-99), `PUT` trả 404 — không nhất quán (thấp).
- `clock_offset_s` chỉ áp nếu model có thuộc tính → im lặng không làm gì với `ess-01` (:79; R1).
- Chọn model: mọi công tơ không phải `MTR_POC` dùng **chung** `site.meter_load` (:40-43) → site có 2 công tơ tải sẽ trùng số (thấp, hiện chỉ 1).

### 4.5 `edge/bridge/bridge/poller.py` — đọc Modbus + quality

**Trách nhiệm**: một kết nối/endpoint, khóa chung cho poll/ghi (:33); đọc theo khối (:57-70); giải mã với SF cùng chu kỳ (:88-96); `ts_src` từ thanh ghi đồng hồ (:97-99); máy trạng thái quality (:108-131); `write()` FC16 (:133-145), `read_point()` (:147-156).

**Bất biến (07 §5.1.5, §6.9)**:

| Tình huống | Hành vi mã | Khớp 07? |
|---|---|---|
| Timeout/OSError | `fail_count++`; <3 lần: không phát reading; ≥3: `BAD_COMM` + sự kiện `DEVICE_COMM LOST` một lần; đọc lại được → `RESTORED` | Có |
| Exception 01/02/03 | `BAD_CONFIG` cho mọi điểm | Có (nhưng không "ngừng poll block", không sự kiện cấu hình) |
| Exception khác (04/06/…) | giữ giá trị cũ ≤ `max_age_ms`=3000 với **q = `GOOD`**, quá hạn → `UNCERTAIN_STALE` không giá trị | Một phần: giá trị giữ được gắn `GOOD` và ts mới (:126-127) → được tính vào `n`/`avg` như mẫu thật, không có `cov_ms` (INFERENCE). Mọi mã khác 1/2/3 kể cả 0x0A/0x0B gateway đều vào nhánh này. |
| Sentinel | `BAD_DEVICE`, không giá trị | Có |
| Lỗi 1 khối | bỏ cả lần đọc (mọi khối) | Chặt hơn 07 |

**Testability**: client pymodbus tạo trong `__init__` (:32) nhưng là thuộc tính công khai → thay bằng fake được. `poll_once` dùng `time.time()` (:73). Callback `on_reading/on_device_event` tiêm được → tốt.

**Bug**:
- `ts_src`: `image.get(...)` trả `Reading` (luôn truthy) và giá trị 0 hợp lệ → `ts_src_ms = 0` (:98-99) khi thanh ghi đồng hồ = 0 (REPRODUCED R1, A1-BUG-09). Nên coi 0/ngoài khoảng hợp lý là không có `ts_src`.
- `write()`/`read_point()` không truyền SF (`r.encode(value)` :142, `r.decode(rr.registers)` :156) → sai với thanh ghi `scale_ref` có SF ≠ 0 (SUSPECTED, latent cho `SET_PV_LIMIT`; hiện `WMaxLimPct_SF = 0`) (A1-BUG-16).
- `read_point()` không kiểm `connected` trước khi đọc (khác `write`) — lỗi bị bắt và trả `None` → readback thành `FAILED_TIMEOUT` (chấp nhận được).

### 4.6 `edge/bridge/bridge/aggregate.py` — cửa sổ C1–C4

**Bất biến**: `ts` = đầu cửa sổ căn theo UTC ms (:47); cửa sổ đóng khi reading mới thuộc cửa sổ sau (:49-53) hoặc `now ≥ start + w + 0,5 s` (:85-87); cửa sổ không có mẫu GOOD → **không có giá trị** và q = `last_q` (≠ GOOD) (:63-64, REPRODUCED R18: `{'q': 'BAD_COMM'}` không có `avg`); thiếu mẫu → `cov_ms` (:67-69, R19); C4 mỗi `C4_PERIOD_S`, `boundary` khi `ts % 300 000 < 5 000` (:89-99).

**Testability**: `Aggregator` thuần, nhận `now_ms` làm tham số cho `flush` (tốt). Nhưng `WINDOW_S`/`C4_PERIOD_S` đọc env **lúc import** (:12-14) → đổi cấu hình trong test phải reload module.

**Bug**: đồng hồ tường lùi (NTP step) → `win.start_ms > start` nên cửa sổ cũ bị **ghi đè** không qua `closed` (:49-53) → mất mẫu (REPRODUCED R17: 3 mẫu ở cửa sổ 10 000 biến mất, chỉ còn cửa sổ 0) (A1-BUG-11). Trạng thái thiết bị (`ess.state`, enum) được lấy trung bình (README §13.7, FACT `site.yaml` C1/C2).

### 4.7 `edge/bridge/bridge/store.py` — outbox SQLite

**Bất biến**: `seq` theo stream tăng đơn điệu, bền qua khởi động lại (:42-46); outbox xả theo `id` (= thứ tự seq, vì `flush_loop` cấp seq rồi enqueue tuần tự); telemetry chỉ xóa khi `TELEMETRY_ACK` (`seq ≤ ack_seq`, :84-88); event/ack xóa khi PUBACK (uplink.py:125-126); kết nối lại → mọi hàng đã gửi chưa ack được gửi lại (:78-82); chống replay theo `kid` (:109-117).

**Testability**: rất tốt — chỉ cần đường dẫn file tạm (R6–R11 dùng `Store` thật). Đồng hồ: `now_ms()` tường cho `created_ms/sent_ms` → phân loại live/backfill (uplink.py:135-145) và resend phụ thuộc đồng hồ tường.

**Bug/rủi ro**:
- `next_seq` và `enqueue` là hai câu lệnh autocommit riêng (`isolation_level=None`, :21; dùng ở `__main__.py:94-97`) → crash/lỗi đĩa giữa hai lệnh để lại **lỗ seq vĩnh viễn** → ack của ingest đứng yên (A1-BUG-10; SUSPECTED kích hoạt, hệ quả REPRODUCED R12).
- Không index trên `(kind, stream, seq)`, `created_ms`, `sent_ms` → quét toàn bảng mỗi 0,2 s khi backlog lớn (INFERENCE, hiệu năng; FR-INT-009 yêu cầu buffer 7–30 ngày).
- Không giới hạn kích thước outbox / không có chính sách tràn và sự kiện `DATA_LOSS` (07 §6.10) (FACT: không có mã).

### 4.8 `edge/bridge/bridge/uplink.py` — MQTT 5 + drain

**Bất biến**: Will retained `{"online": false}` + Will Delay 2 s (:54-58); `clean_start=False`, Session Expiry 3600 (:67-69); hàng tạo sau khi kết nối → topic live, trước đó → `up/backfill`, giới hạn `backfill_rate`/s, cũ trước (:130-153); live được ưu tiên trước backfill (07 §6.12-5).

**Testability**: paho `Client` tạo trong `__init__`, thread drain tự khởi động trong `start()`; `_on_message` và `_publish_row` gọi được trực tiếp (R14 gọi `_on_message`). Test hợp đồng MQTT 5 thật cần broker (L3).

**Bug**: `_on_message` không bắt exception (:94-100); `body["stream"]` thiếu → `KeyError` lan ra paho; paho 2.1.0 `suppress_exceptions=False` mặc định nên **re-raise** (client.py:4495-4506) và `_thread_main` kết thúc luồng (client.py:4521-4525) → không còn reconnect (REPRODUCED phần exception R14; phần luồng chết là đọc nguồn paho — FACT nguồn, chưa chạy với broker) (A1-BUG-08). Topic `down/config` chỉ `ingest` được ghi (ACL) nên kích hoạt cần ingest lỗi hoặc tài khoản ingest bị lộ.

Hệ quả thứ tự: sau kết nối lại, live (seq cao) đi **trước** backfill (seq thấp) — đúng 07, nhưng là nguyên nhân A1-BUG-06 ở ingest.

### 4.9 `edge/bridge/bridge/commands.py` — lệnh `SET_ESS_P`

**Bất biến (07 §8.4–§8.7)**:
- Idempotency: `command_id` đã thấy → ack lại trạng thái cũ `duplicate: true`, không thực thi (:80-86).
- Thứ tự kiểm: A.2 target (:99) → A.3 cấu trúc/type/params/thời hạn ≤ 1 h/hạng nguy hiểm (:102-117) → A.4 replay theo `kid` (:119) → B. `p_w == 0` bỏ qua C (:122-124) → C.7 cửa sổ hiệu lực + `max_latency_ms` (:126-130) → C.11 SOE tĩnh → `REJECTED_OUT_OF_LIMIT` (:132-133) → BMS cũ > 5 s → `REJECTED_INTERLOCK:IL-04` (:134-137).
- Thực thi: kẹp động theo CCL/DCL → `APPLIED_CLAMPED` (:145-149); supersede lệnh cũ (:152-155); ghi → `DISPATCHED`; readback ± 1 → `APPLIED*`, nếu không `FAILED_NO_EFFECT/TIMEOUT` (:156-178); `lifetime`: sau 8 s sự kiện tracking (tol = max(2 % P đm, 1 kW)), tới `expires_at` ghi 0 → `EXPIRED` → `COMPLETED` (:182-202).

**Testability**: tốt nhất trong repo — DI qua constructor (`store`, `uplink`, `ess_poller`, `soe`, `rated_w`); `handle()` gọi trực tiếp được (R6–R9 FACT). Điểm kém: `asyncio.sleep(8)` cứng (:185), `now_ms()`/`time.monotonic()` trực tiếp; `device_id: "ess-01"` cứng trong `event()` (:49).

**Bug** (chi tiết §5): A1-BUG-01/02/03 (setpoint ở lại sau hạn), A1-BUG-07 (envelope sai → không ack kết thúc), A1-BUG-19 (hàng đợi lệnh bị chặn trong lúc readback, timeout do envelope quyết định, không trần).

Khoảng trống so với 07 (FACT, đã ghi ở README §14): không JWS (A.1), không kiểm `site_id/asset_id` (A.2 chỉ `edge_id`), không IL-06, không arbiter, `danger_class` so sánh **chuỗi** (`"C10" < "C2"`) (:116).

### 4.10 `edge/bridge/bridge/__main__.py` — ghép nối

**Trách nhiệm**: đọc env/site.yaml/maps; dựng pollers, aggregator, uplink, command handler; vòng `flush` (1 s), `heartbeat` (2 s), `state` (30 s); C5 → sự kiện khi đổi.

**Testability**: `Bridge.__init__` làm mọi thứ (đọc file theo env, `os.makedirs("/data")`, mở SQLite, tạo client) và **cứng `ess-01`** (`next(...)` → `StopIteration` nếu site không có) — muốn test `flush_loop`/`on_reading` phải dựng qua `__new__` hoặc tách factory (đề xuất §6).

**Rủi ro**: `HEALTH_FILE` chỉ được `flush_loop` chạm (:91) → healthcheck không phản ánh MQTT, pollers hay command loop (INFERENCE). `heartbeat_loop` chứng minh tiến trình còn sống, không chứng minh vòng điều khiển khỏe. `alarm_state` trong RAM → khởi động lại phát lại `RAISED` cho alarm đang bật (thấp). `state()` báo `clock_state: "SYNCED"` cứng.

### 4.11 `ingest/ingest.py`

**Trách nhiệm**: shared subscription `$share/ingest/ems/v1/+/up/#`; telemetry: dedupe lô `(edge_id, stream, seq)` → upsert hàng hẹp `ON CONFLICT (series, ts) DO NOTHING` → commit → `TELEMETRY_ACK` tích lũy; cmd-ack → `command_ack` + `command.last_state`; event → `event` (unique `event_id`); state → `edge_state`; `COUNTER_RESET` khi C4 giảm.

**Bất biến**: ack chỉ sau commit (:84); `ack_seq` = seq cao nhất không có lỗ phía dưới (:86-102); dedupe → vẫn ack (:63-66); counter `monotonic: false` bị bỏ qua (:37-38).

**Testability**: `Ingest.__init__` đọc file + env; `run()` vòng vô hạn; logic xử lý tách khỏi transport khá tốt — R10–R13 dựng qua `__new__` với fake DB/client (FACT). Mặc định DSN chứa `ems:ems` (:42) và CLI cũng vậy (`tools/ems_cli.py:34`) — mặc định thông tin đăng nhập cứng (thấp, chỉ là fallback).

**Bug**: A1-BUG-04 (tin `edge_id` payload — :57, :105, :124, :134), A1-BUG-05 (khởi tạo `contig` — :90-98), A1-BUG-06 (COUNTER_RESET giả — :76-77, :108-116), A1-BUG-10 (exception không phải DB bị nuốt mà không ack → lỗ vĩnh viễn — :156-157), A1-BUG-20 (cmd-ack không dedupe, `last_state` lùi theo thứ tự đến — :118-127). `last_counter` cập nhật trong RAM trước khi transaction commit (:109-110) → lệch nếu rollback (thấp). `client_id="ingest-1"` cứng (:161) → hai bản ingest đá nhau khỏi broker (rủi ro scale).

Khác 07 §6.10 (FACT): trùng `(series, ts)` khác giá trị bị bỏ lặng lẽ (không `rev`, không audit); không `RESEND_REQUEST`/`DATA_LOSS` cho lỗ seq.

### 4.12 `simulators/evse/csms/csms.py` — CSMS stub OCPP 1.6J

**Trách nhiệm**: nhận Boot/Status/Start/Stop/MeterValues, cài TxDefaultProfile 32 A an toàn, tổng hợp `evse.p` C1/C2/C4 → MQTT, POST `/ev` sang vsite mỗi giây, xử lý `SET_EV_LIMIT`.

**Testability**: biến toàn cục `EDGE_ID`, `PID` lúc import (:30-31); `Mqtt()` kết nối ngay trong constructor (:44-54); `handle_command(site, raw)` dùng được với fake `site.cp` (INFERENCE).

**Bug/rủi ro**:
- Lệnh cũ hết hạn **xóa profile id 2 của lệnh mới hơn** (cùng `profile_id=2`, task cũ không bị hủy, :222-231); không `SUPERSEDED`, không idempotency `command_id`, không anti-replay, không trần trên `i_max_a` (chỉ chặn 0<I<6, :217) (SUSPECTED, A1-BUG-17).
- `urllib.request.urlopen(..., timeout=1)` **đồng bộ trong event loop** (:97-103) → vsite chậm làm OCPP đứng ≤ 1 s mỗi giây (SUSPECTED, A1-BUG-18).
- Exception trong `handle_command` (ví dụ thiếu `params.i_max_a`) mất trong future của `run_coroutine_threadsafe` (:240) → chỉ có `RECEIVED` (SUSPECTED).
- Không store-and-forward, seq gieo theo thời gian không bền (FACT, README §14 thừa nhận).

### 4.13 `tools/ems_cli.py`

Vai trò kép: dispatcher (publish `down/cmd` với Message Expiry, Correlation Data, Response Topic) + công cụ kiểm (balance, seq-check, coverage, check-ess). `uuid7()` đúng version 7 / variant RFC 4122 (REPRODUCED đúng — R16: 0/2000 sai). `seq = time ms` (:84) → hai CLI cùng ms → `REJECTED_REPLAY` (thấp). `send-ev-limit` luôn trả 0, không `--expect` (:141-150) → smoke không thể dùng để kiểm EV. `balance` là kiểm tra hợp lệ cho dấu/scale/word order nhưng **không** cho độ chính xác (cùng mô hình sinh mọi giá trị — README §9).

Khuyến nghị (INFERENCE): các hàm kiểm (`BALANCE_SQL`, `cmd_seq_check`…) là tài sản tái dùng cho framework — nên tách thành thư viện truy vấn có thể gọi từ pytest thay vì parse stdout.

### 4.14 `infra/`

| Mục | Quan sát | Nhãn |
|---|---|---|
| `mosquitto/acl.conf` | Edge: write `up/#`, read `down/#` của chính nó (`%u`); ingest: read `+/up/#`, **write `+/down/config`**; dispatcher: write `+/down/cmd` | FACT. Rủi ro: ingest gửi được `TELEMETRY_ACK` cho mọi edge → kết hợp A1-BUG-04 thành đường mất dữ liệu. Cần test ACL âm (edge không publish được topic edge khác / `down/#`; dispatcher không đọc được `up/#`; ingest không publish `down/cmd`). |
| `mosquitto.conf` | `allow_anonymous false`, persistence, `max_queued_messages 10000`, `max_inflight 20` | FACT. Queue 10 000 cho session ingest khi ingest chết lâu → tràn, broker bỏ tin (INFERENCE) → telemetry được edge gửi lại (ổn), event/ack mất (đã xóa khi PUBACK). |
| `entrypoint.sh` | Sinh password file từ env, fail nếu thiếu | FACT, tốt. |
| `docker-compose.yml` | Cổng bind `127.0.0.1`; `:?set in .env` cho mật khẩu; healthcheck vsite/ingest/bridge dựa file/HTTP nội bộ | FACT. Healthcheck ingest = file được chạm trong vòng `sleep(30)` (ingest.py:175-179) → "healthy" kể cả khi MQTT/DB chết. `DB_PASSWORD` nhúng trong URL → ký tự `@:/` làm hỏng DSN (thấp). |
| `db/init.sql` | PK `telemetry(site, device, point, ts)`; `telemetry_batch` PK `(edge, stream, seq)` + `arrival`; `event.event_id` UNIQUE toàn cục; hypertable có điều kiện | FACT. `latest_value` = `DISTINCT ON` toàn bảng (hiệu năng). `event_id = "{edge}-ev-{seq}"`: nếu volume bridge bị xóa (seq về 1) → sự kiện mới trùng id cũ bị `DO NOTHING` **lặng lẽ** (INFERENCE). Tương tự telemetry seq reset → lô mới bị coi là trùng và vẫn được ack (INFERENCE, rủi ro thay edge/reflash). |
| `config/site.yaml` | Nguồn sự thật chung cho bridge/ingest/vsite/CSMS; pid duy nhất | FACT. Cần test lint: pid duy nhất toàn cục, mọi `code` tồn tại trong map của driver, `sampling_class` hợp lệ, `ts_src_point` tồn tại và được model cấp. |
| `grafana/` | Mật khẩu qua `$EMS_DB_PASSWORD` | FACT, không có bí mật cứng. |
| `.env.example` | Chỉ `change-me-*` | FACT. |

### 4.15 `tests/smoke.sh`

Chỉ test hiện có: e2e D1–D6 qua CLI trong container, cần stack Docker, ~2,5 phút (README). Kiểm `exit code` từng bước; `retry` dùng `/tmp/smoke.out` cố định (chạy song song sẽ đè nhau); không có JUnit/báo cáo máy đọc; không bao D7–D12. **Tôi không chạy smoke** (không sở hữu Docker) — kết quả PASS trong README là của người viết README, chưa được kiểm lại trong audit này.

## 5. Danh sách bug

Mức: Cao = có thể gây vận hành sai thiết bị hoặc mất dữ liệu im lặng; Trung bình = sai hợp đồng/khả năng phục hồi; Thấp = latent/ít hệ quả. Script: `docs/testing/notes/A1-repro/`.

| ID | Mức | Nhãn | Vị trí | Mô tả và bằng chứng |
|---|---|---|---|---|
| A1-BUG-01 | Cao | REPRODUCED (R6) | `edge/bridge/bridge/commands.py:151-159` | Lệnh B supersede A: A bị hủy task và ack `SUPERSEDED` **trước** khi ghi B; ghi B lỗi → B `FAILED_DEVICE_EXCEPTION`, `self.active` vẫn trỏ A đã hủy. Thiết bị giữ setpoint của A vô thời hạn (heartbeat vẫn chạy nên watchdog thiết bị không cứu). Đầu ra: `A acks: [... 'APPLIED', 'SUPERSEDED']`, `B acks: ['RECEIVED','ACCEPTED','FAILED_DEVICE_EXCEPTION']`, `device setpoint after A expired: -100000.0`. |
| A1-BUG-02 | Cao | REPRODUCED (R7) | `commands.py:156-172` | Ghi thành công nhưng readback không khớp/không đọc được → `FAILED_NO_EFFECT`/`FAILED_TIMEOUT` và `return` **không tạo `lifetime`** → không hoàn nguyên khi hết hạn dù giá trị có thể đã vào thiết bị. Đầu ra: `acks: [... 'DISPATCHED', 'FAILED_NO_EFFECT'] | device setpoint after expiry: -80000.0`. |
| A1-BUG-03 | Cao | REPRODUCED (R8) | `commands.py:196-198` | Ghi hoàn nguyên lúc hết hạn bỏ qua mã lỗi, vẫn ack `EXPIRED` → `COMPLETED` (07 §8.4: `COMPLETED` "khi hoàn nguyên xong"). Đầu ra: `acks: [..., 'EXPIRED', 'COMPLETED'] | device setpoint: -70000.0`. Không retry. |
| A1-BUG-04 | Cao | REPRODUCED (R10) | `ingest/ingest.py:57, 105, 124, 134, 138` | Ingest lấy `edge_id` từ **payload**, không so với topic. Publish bằng tài khoản `edge-ev01` lên `ems/v1/edge-ev01/up/telemetry/c1` với `edge_id: edge-vsite01` → hàng được ghi cho `meter-poc`, và `TELEMETRY_ACK {'ack_seq': 999}` gửi tới `ems/v1/edge-vsite01/down/config` → edge-vsite01 xóa mọi telemetry seq ≤ 999 chưa commit. ACL topic theo `%u` bị vô hiệu ở tầng ứng dụng. |
| A1-BUG-05 | Cao | REPRODUCED logic (R11); kích hoạt INFERENCE | `ingest.py:90-98` | Lần đầu thấy `(edge, stream)`, `contig = min(seq đã lưu) − 1`. Nếu lô đến đầu tiên là seq 6 (seq 1–5 đang bay/được gửi lại), ack = 6 → edge xóa 1–5 (đầu ra: `ack_seq: 6`, `edge outbox rows deleted by that ack: 6`). Kịch bản kích hoạt (INFERENCE): stack mới, bridge publish trước khi session shared-subscription của ingest tồn tại → lô đầu mất ở broker; sau 20 s gửi lại nhưng lô live seq cao hơn đã tới trước. |
| A1-BUG-06 | Trung bình | REPRODUCED (R13) | `ingest.py:76-77, 108-116`; thứ tự gửi `uplink.py:136-148` | Kiểm bộ đếm theo **thứ tự đến**, không theo `ts`. Sau mất mạng > 60 s, C4 live (raw 1300) tới trước C4 backfill (raw 1200) → `COUNTER_RESET meter-poc meter.e_import: 1300 -> 1200` giả. |
| A1-BUG-07 | Trung bình | REPRODUCED (R9) | `commands.py:61-65, 87, 111, 116, 119` | Exception trong `handle` bị `run()` nuốt. `expires_at` sai định dạng → **không ack nào** (kể cả `RECEIVED`); `valid_from` sai, `danger_class` kiểu số, `seq` không phải số → chỉ `RECEIVED`. 07 §8.7-A.3 yêu cầu `REJECTED_INVALID` + cảnh báo bảo mật. |
| A1-BUG-08 | Trung bình | REPRODUCED một phần (R14) + FACT nguồn paho | `edge/bridge/bridge/uplink.py:94-100`; paho `client.py:4495-4506, 4521-4525` | `TELEMETRY_ACK` thiếu `stream`/`ack_seq` không phải số → exception trong callback; paho re-raise → luồng `loop_start` kết thúc → bridge không bao giờ reconnect, chỉ đệm SQLite; healthcheck vẫn xanh. Chưa chạy với broker thật. |
| A1-BUG-09 | Trung bình | REPRODUCED (R1) | `simulators/vsite/vsite/model.py:126-134`; `server.py:104`; `poller.py:98-99`; `ingest.py:28, 135`; `vsite/__main__.py:79` | Map BESS có `ess.clock` (`ts_src_point` của `ess-01` trong site.yaml) nhưng `Bess.values()` không cấp → thanh ghi = 0 → `ts_src_ms = 0` → sự kiện `DEVICE_ALARM` của ess-01 lưu `ts_src = 1970-01-01`. Fault `clock_offset_s` trên ess-01 im lặng không tác dụng. Lỗi nằm ở simulator nhưng lộ ra lỗ ở edge: không kiểm hợp lý `ts_src`. |
| A1-BUG-10 | Trung bình | REPRODUCED hệ quả (R12); SUSPECTED kích hoạt | `edge/bridge/bridge/__main__.py:94-97`; `store.py:42-60`; `ingest.py:156-157` | Lỗ seq vĩnh viễn → `ack_seq` đứng ở 2 (`[1, 2, 2, 2, 2]`) → mọi lô sau giữ trong outbox và được gửi lại mỗi `TELEMETRY_RESEND_S` mãi mãi. Nguồn lỗ: crash giữa `next_seq` và `enqueue` (hai autocommit), hoặc lô "độc" làm ingest ném exception không phải DB (bị log rồi bỏ, không ack). Không có `RESEND_REQUEST`/`DATA_LOSS` (07 §6.10). |
| A1-BUG-11 | Trung bình | REPRODUCED (R17) | `edge/bridge/bridge/aggregate.py:49-53` | Đồng hồ tường lùi → cửa sổ đang mở bị thay mà không chuyển sang `closed` → mất mẫu. Đầu ra: 3 mẫu cửa sổ `ts=10000` biến mất, chỉ còn cửa sổ `ts=0` với 1 mẫu. |
| A1-BUG-12 | Thấp–TB | REPRODUCED (R4) | `simulators/vsite/vsite/__main__.py:68-82, 123-136, 156` | REST tiêm lỗi không kiểm kiểu: `bms_derate_w: "50000"` → `TypeError` trong `Bess.step`; vòng `physics` không bắt → vsite thoát (INFERENCE). Ảnh hưởng độ ổn định của harness test, không phải sản phẩm. |
| A1-BUG-13 | Thấp | REPRODUCED (R5) | `model.py:145-148, 171` | Sau watchdog revert, ghi `ess.p_setpoint` (không đổi heartbeat) được **thực thi** (p ≈ −99 887 W) trong khi `state` vẫn 3 và alarm `0x100` vẫn bật → trạng thái mâu thuẫn với công suất. Cần chốt hành vi mong muốn (UNKNOWN: 07 không quy định cách thiết bị thoát revert). |
| A1-BUG-14 | Thấp | REPRODUCED (R3) | `model.py:120, 159-170` | SOC vượt `soc_max` khi `SIM_SPEED` lớn: x1 và x60 → 95,000 %, x600 → 96,614 % (trễ PCS theo giờ tường, tích phân theo giờ mô phỏng). Test tăng tốc thời gian (T-FR-INT-009 "tăng tốc") phải biết giới hạn này. |
| A1-BUG-15 | Thấp (latent) | REPRODUCED (R2) | `simulators/vsite/maps/regmap.py:70, 94-96` | `encode` không kiểm phạm vi → `I32 encode(2**31)` → `−2147483648`; `U16 encode(−5.0)` → `6548.6`. Ghi ra thiết bị một giá trị bị quấn sẽ không ai phát hiện. |
| A1-BUG-16 | Thấp (latent) | SUSPECTED | `edge/bridge/bridge/poller.py:142, 156` | `write()`/`read_point()` bỏ SF của `scale_ref` → sai khi SF ≠ 0 (sẽ gặp khi nối `SET_PV_LIMIT`). |
| A1-BUG-17 | Trung bình | SUSPECTED | `simulators/evse/csms/csms.py:203-231` | `SET_EV_LIMIT`: task của lệnh cũ không bị hủy; khi hết hạn gọi `ClearChargingProfile(id=2)` xóa profile của lệnh mới; không `SUPERSEDED`, không idempotency, không trần dòng. |
| A1-BUG-18 | Thấp–TB | SUSPECTED | `csms.py:97-103` | HTTP đồng bộ trong event loop asyncio (timeout 1 s) → chặn OCPP khi vsite chậm. |
| A1-BUG-19 | Thấp–TB | SUSPECTED | `commands.py:58-66, 160-172` | Lệnh xử lý tuần tự; readback chờ tới `tolerance.readback_timeout_s` do **envelope** đặt, không trần → lệnh an toàn hóa `p_w=0` có thể bị trễ tùy ý sau một lệnh có readback treo. |
| A1-BUG-20 | Thấp | SUSPECTED | `ingest.py:118-127` | `command_ack` không dedupe; `command.last_state` ghi đè theo thứ tự đến (QoS 1 gửi lại có thể làm trạng thái lùi). |
| A1-BUG-21 | Thấp | SUSPECTED / spec-gap | `poller.py:124-131` | Nhánh exception 04/06: giá trị giữ lại được gắn `GOOD` với `ts` mới → được tính như mẫu đo thật trong `avg`/`n`, không `cov_ms`. 07 §5.1.5 nói "giữ giá trị cũ" nhưng không nói quality trong lúc giữ — cần chốt (UNKNOWN). |
| A1-BUG-22 | Thấp | FACT (đọc mã) | `vsite/__main__.py:86-99` | `DELETE /faults/{id}` trả 200 với id không tồn tại (PUT trả 404). |

Không phải bug nhưng cần biết khi viết oracle: `balance_check_w` luôn 0 theo cấu trúc (model.py:253); cân bằng e2e đúng tới 0,05 % chỉ chứng minh dấu/scale/word order/ánh xạ pid, không chứng minh độ chính xác đo (README §9).

## 6. Testability

| Vấn đề | Vị trí (FACT) | Cách test được ngay, **không sửa mã** | Refactor đề xuất (cho chủ thư mục, không bắt buộc) |
|---|---|---|---|
| Đồng hồ tường/monotonic gọi trực tiếp | model.py:114-151, 188, 224, 237; poller.py:73; store.py:16; commands.py (now_ms, monotonic); aggregate (tham số `now_ms` — tốt) | `monkeypatch.setattr(module.time, "monotonic", fake)` — **chú ý**: `vsite.model.time` là module `time` toàn cục, patch sẽ ảnh hưởng event loop asyncio (bài học từ R5: phải lưu và khôi phục hàm gốc). Dùng `freezegun`/`time-machine` cẩn thận với asyncio. | Tiêm `clock: Callable[[], float]` qua constructor. |
| Sleep cứng | commands.py:185 (`sleep(8)`), :169 (`0.5`) | Patch `bridge.commands.asyncio.sleep` (R8 làm vậy) | Tham số hóa `tracking_delay_s`. |
| Cấu hình đọc lúc import | aggregate.py:12-14; csms.py:30-32; bridge `__main__.py:24-25` (`MAX_BATCH_BYTES`) | `monkeypatch.setenv` + `importlib.reload` | Đọc trong constructor. |
| Constructor làm I/O | `Bridge.__init__` (file, `/data`, SQLite, client, `ess-01` cứng); `Ingest.__init__` (file); `Mqtt()` trong csms kết nối ngay | Dựng qua `Cls.__new__` + gán thuộc tính (R10–R13) | Factory/DI; tách `from_env()`. |
| Ngẫu nhiên không seed | model.py:71, 185-187 | So sánh với dung sai; hoặc `random.seed` trong fixture | Tiêm `rng`. |
| Logic xen I/O | ingest `telemetry()` (SQL + logic contig + publish); csms `handle_command` | Fake DB/client (R10–R13) | Tách hàm thuần `decide_ack(seqs, seq)`, `counter_check(prev, raw, ts)`. |
| Host/ID cứng | mặc định `mosquitto`, `db`, `vsite:8080` (env ghi đè được — chấp nhận); `edge-vsite01`, `edge-ev01`, `site-bd-01` cứng trong CLI (ems_cli.py:85, 114, 142); `ess-01` cứng trong bridge | Dùng đúng site.yaml hiện có | Đọc từ site.yaml. |
| Thread + paho | uplink drain thread, paho loop thread | Test hợp đồng với Mosquitto thật (L3) | — |
| Healthcheck nông | bridge (file chạm bởi flush), ingest (file chạm bởi sleep loop) | Test e2e phải kiểm hành vi, không tin `healthy` | Health phản ánh MQTT/DB/poller. |

## 7. Rủi ro production

Mã là **PoC**; production đích là Java/Spring Boot + Angular (và edge theo ADR-07). Các rủi ro dưới đây là **rủi ro hợp đồng/thiết kế sẽ được mang sang** nếu không có test hồi quy bám theo hợp đồng (INFERENCE):

1. **An toàn lệnh** — mọi đường lỗi phải kết thúc bằng trạng thái thiết bị an toàn và trạng thái lệnh đúng sự thật (A1-BUG-01/02/03/07/19). Watchdog thiết bị chỉ cứu khi **tiến trình** chết; khi tiến trình sống nhưng logic hỏng, heartbeat vẫn chạy (bridge `__main__.py:115-124`) nên không có lưới an toàn. Đây là rủi ro số 1 cho FR-INT-007, FR-INT-018, NFR-SEC (PDP-15).
2. **Toàn vẹn dữ liệu (store-and-forward ↔ ack)** — hợp đồng ack tích lũy rất nhạy: khởi tạo sai (BUG-05), lỗ vĩnh viễn (BUG-10), ack giả (BUG-04), seq reset khi thay/flash edge (INFERENCE, §4.14). FR-INT-009 "không mất dữ liệu khi mất mạng ≤ 7 ngày" chưa có test nào ngoài D8 30 s.
3. **Bảo mật ranh giới tenant/edge** — ACL topic đúng nhưng ứng dụng tin payload (BUG-04). Production Java ingest phải lấy danh tính từ topic/chứng chỉ mTLS, không từ payload — cần test hợp đồng bắt buộc điều này.
4. **Thời gian** — phụ thuộc đồng hồ tường ở aggregator (BUG-11), store (live/backfill), kiểm `max_latency_ms` (so `sent_at` của cloud với đồng hồ edge), `ts_src` không kiểm hợp lý (BUG-09); `clock_state` cứng `SYNCED`. FR-INT-010/IL-06 chưa hiện thực.
5. **Khả năng quan sát/vận hành** — healthcheck nông; luồng MQTT có thể chết im lặng (BUG-08); ingest một `client_id` cứng không scale ngang.
6. **Hiệu năng ở quy mô** — outbox không index; `latest_value` `DISTINCT ON` toàn bảng; ingest đồng bộ mỗi tin một transaction; `by_point` dựng lại mỗi lần. Chưa có số đo (UNKNOWN) → cần test tải sau.
7. **Độ trung thực mô phỏng** — map dùng chung hai phía (không bắt được lỗi map đối xứng), cân bằng tautological, `SIM_SPEED` làm sai lệch năng lượng và SOC (BUG-14). Oracle test phải độc lập với mô hình khi có thể (vector vàng, giá trị tính tay).

## 8. Xếp hạng: cái gì cần test nhất

Tầng: L1 = unit thuần (không mạng), L2 = component với fake/thật cục bộ (SQLite, aiohttp test client, pymodbus server cục bộ), L3 = tích hợp với hạ tầng thật (Mosquitto, PostgreSQL — container riêng của test), L4 = e2e stack `emspoc`.

| Hạng | Đối tượng | Lý do (rủi ro × khả năng hỏng) | Tầng | Ca chính | Truy vết |
|---|---|---|---|---|---|
| 1 | `CommandHandler` (vòng đời + an toàn) | Ghi thiết bị thật; 4 bug đã tái hiện; DI sẵn → rẻ | L1/L2 | Ma trận A→B→C (mỗi bước một vector từ chối, đúng mã lý do); idempotency; replay; safe-path `p_w=0` (kể cả hết hạn/độ trễ, nhưng replay vẫn bị chặn — T-NFR-SEC-004e); kẹp CCL/DCL; supersede; **mọi đường lỗi kết thúc an toàn** (BUG-01/02/03); envelope sai → `REJECTED_INVALID` (BUG-07); hết hạn → ghi 0 → `EXPIRED→COMPLETED` | FR-INT-007, FR-INT-018, T-FR-INT-007, T-NFR-SEC-004/004b/004e, 07 §8.4–8.7 |
| 2 | Hợp đồng store-and-forward + `TELEMETRY_ACK` (Store + Uplink drain + Ingest contig) | Mất dữ liệu im lặng; 3 bug | L1 (Store, logic contig) + L3 (Mosquitto thật: mất broker, mất ingest, gửi lại, thứ tự backfill) | seq bền qua restart; xóa chỉ khi ack; ack không vượt lỗ; ack lần đầu không nhảy (BUG-05); lỗ vĩnh viễn (BUG-10); live trước backfill, backfill tăng dần, rate limit; PUBACK ≠ đã lưu | FR-INT-008, FR-INT-009, T-FR-INT-008/009, 07 §6.7/§6.10/§6.12 |
| 3 | Ingest (dedupe, quy danh tính, counter) | Bảo mật + dữ liệu | L1 (fake DB) + L3 (PostgreSQL thật với `init.sql`) | topic≠payload edge_id → từ chối (BUG-04); dedupe lô; upsert `(series, ts)`; BAD không giá trị → `value NULL`; COUNTER_RESET theo `ts` không theo thứ tự đến (BUG-06); `monotonic:false`; cmd-ack dedupe/không lùi trạng thái | FR-INT-008, FR-HIST-002 (máy trạng thái bộ đếm), NFR-SEC |
| 4 | Codec `regmap` + lint map/site.yaml | Lỗi map = số sai toàn hệ thống; dùng chung hai phía | L1 | Vector vàng độc lập (I32 CDAB, SF âm, sentinel, U64, F32, STRING); tràn phạm vi (BUG-15); `blocks()` ≤125, không vắt lỗ; lint: pid duy nhất, code ∈ map, `ts_src_point` được model cấp (BUG-09), SunSpec cross-check | FR-INT-003, FR-INT-004, T-FR-INT-003/004 |
| 5 | Poller (quality state machine) | Quality sai = UI hiển thị sai/che mất dữ liệu | L2 (fake client) + L2 (pymodbus server cục bộ + Faults của vsite) | 1–2 timeout không phát; 3 → `BAD_COMM` + LOST một lần; RESTORED; exc 01/02/03 → `BAD_CONFIG`; 04/06 giữ ≤ max_age rồi `UNCERTAIN_STALE` (chốt quality khi giữ — BUG-21); sentinel → `BAD_DEVICE`; `ts_src` hợp lý | 07 §5.1.5, §6.9 |
| 6 | Aggregator | Số liệu C1–C4 là đầu vào mọi báo cáo | L1 (+ property-based) | Biên cửa sổ; `cov_ms`; cửa sổ BAD không giá trị (không bao giờ 0); C4 chu kỳ/`boundary`; đồng hồ lùi (BUG-11) | 07 §6.5, §7.3; K §6 #9 |
| 7 | Vật lý BESS/site (oracle của e2e) | Oracle sai → mọi test e2e vô nghĩa | L1 (property-based) | Dấu; SOC đi đúng chiều; tổn hao η; taper; kẹp; watchdog 15 s và thoát revert (BUG-13); vượt `soc_max` theo `SIM_SPEED` (BUG-14); cân bằng | FR-INT-014, FR-INT-016 |
| 8 | E2E cân bằng + phép thử dấu + lệnh (D1–D7) | Hồi quy toàn chuỗi | L4 (chủ Docker) | Port `smoke.sh` sang pytest, xuất JUnit; thêm D7, D10, D11 | FR-INT-016, T-FR-INT-007 |
| 9 | Watchdog/fail-safe e2e (D9) + mất broker (D8) | Gate M2 | L4 | Dừng bridge → P = 0 ≤ `revert_timeout_s`; dừng broker N phút → 0 lỗ seq | FR-INT-018, T-FR-INT-018 |
| 10 | ACL Mosquitto + schema DB | Ranh giới bảo mật/tính duy nhất | L3 | Ca âm ACL cho từng user; PK/unique; hypertable có điều kiện; view `latest_value` | FR-INT-008, NFR-SEC |
| 11 | CSMS stub | EV P1, nhiều lỗ | L2 (fake `cp`) | Idempotency, supersede/expiry (BUG-17), trần dòng, không chặn loop (BUG-18) | FR-EV-*, T-FR-EV-005 |
| 12 | REST tiêm lỗi vsite | Độ tin cậy của harness | L2 (aiohttp test client) | Kiểm kiểu → 400 thay vì crash (BUG-12); DELETE id lạ (BUG-22) | FR-INT-014 |
| 13 | CLI (`uuid7`, envelope, SQL kiểm) | Công cụ dùng trong test | L1 | `uuid7` (đã đúng, R16); envelope đủ trường 07 §8.3; `expiry = expires_at − sent_at` | — |

Gợi ý kiến trúc framework (INFERENCE, để A-khác quyết): đặt các ca theo **hợp đồng** (topic/payload/ack/quality/vòng đời lệnh) ở dạng dữ liệu (YAML/JSON vector) để cùng bộ vector chạy được với bridge Python hôm nay và edge/backend Java sau này; adapter theo ngôn ngữ chỉ làm phần "gửi vector, đọc kết quả".

## 9. Lệnh đã chạy

```bash
# đọc mã / tài liệu
wc -l <mọi file .py/.yaml/.sql/.sh/conf trong simulators edge ingest tools infra tests>   # 3167 total
cat -n <từng file>; grep -n ... docs/research/ems/07-device-integration.md

# môi trường (venv dùng chung, .venv đã có trong .gitignore)
python3 -m venv /home/user/admin/.venv
/home/user/admin/.venv/bin/pip install pymodbus==3.15.0 pysunspec2==1.3.6 PyYAML==6.0.3 paho-mqtt==2.1.0 aiohttp==3.14.4 "psycopg[binary]==3.2.10"
#   -> Python 3.13.16; aiohttp 3.14.4, paho-mqtt 2.1.0, pymodbus 3.15.0, pysunspec2 1.3.6, PyYAML 6.0.3 (+ psycopg 3.2.10)

# tái hiện (từ gốc repo)
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python docs/testing/notes/A1-repro/a1_repro.py    # exit 0; R1–R15
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python docs/testing/notes/A1-repro/a1_repro2.py   # exit 0; R16–R19
```

Tóm tắt kết quả: 19 thí nghiệm. **Tái hiện được 15 hành vi lỗi/đáng ngờ** (R1–R14, R17); R15 chỉ là trích dẫn mã; R16 (uuid7), R18, R19 xác nhận hành vi **đúng**. Không chạy Docker, không chạy `tests/smoke.sh`.

Lưu ý khi chuyển script thành test: script là bằng chứng một lần (in ra, không assert); chuyển sang pytest cần assert **hành vi đúng mong muốn** (ví dụ "setpoint về 0 hoặc lệnh không bị SUPERSEDED khi ghi lệnh mới lỗi") và đánh dấu `xfail(strict=True)` cho bug chưa sửa, để test tự đỏ khi bug được sửa mà chưa bỏ đánh dấu.
