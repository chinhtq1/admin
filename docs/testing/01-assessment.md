# 01 — Đánh giá hiện trạng kiểm thử EMS PoC

- Ngày: 2026-10-10 (cập nhật 2026-10-12) · Vai trò: QA Architect · Trạng thái: **bản 1**
- Đầu vào: [A1 audit mã](notes/A1-code-audit.md), [A2 bản đồ yêu cầu](notes/A2-requirements-map.md), [A3 công cụ](notes/A3-tooling.md), [infra/README.md](../../infra/README.md), [04 Yêu cầu](../research/ems/04-business-requirements.md), [07 Tích hợp thiết bị](../research/ems/07-device-integration.md), [12 Truy vết](../research/ems/12-traceability-matrix.md).
- Tài liệu tiếp theo: [02 Chiến lược](02-strategy.md) · [README chạy test](README.md).
- Nhãn bằng chứng: **FACT** (có `file:line` hoặc đầu ra lệnh), **REPRODUCED** (A1 tái hiện bằng script gọi lớp sản phẩm với fake I/O, ở mức đơn vị), **SUSPECTED** / **INFERENCE** (suy từ đọc mã), **UNKNOWN**.

## Mục lục

1. [Tóm tắt](#1-tóm-tắt)
2. [Hiện trạng kiểm thử (trước khung mới)](#2-hiện-trạng-kiểm-thử-trước-khung-mới)
3. [Khoảng trống](#3-khoảng-trống)
4. [Chức năng quan trọng chưa được test](#4-chức-năng-quan-trọng-chưa-được-test)
5. [Rủi ro production xếp hạng](#5-rủi-ro-production-xếp-hạng)
6. [Danh sách bug nghi ngờ và trạng thái](#6-danh-sách-bug-nghi-ngờ-và-trạng-thái)
7. [Vấn đề testability](#7-vấn-đề-testability)
8. [Điều đã làm hôm nay và điều chưa kiểm](#8-điều-đã-làm-hôm-nay-và-điều-chưa-kiểm)

---

## 1. Tóm tắt

| # | Kết luận | Nhãn |
|---|---|---|
| 1 | Trước khung mới, test tự động duy nhất là `tests/smoke.sh` (35 dòng bash), kịch bản e2e D1–D6 qua CLI trong container, cần stack Docker `emspoc`. Không có unit, contract, DB, security, perf test; không có báo cáo máy đọc (JUnit). | FACT (`ls tests/` → `smoke.sh`; `wc -l tests/smoke.sh` = 35) |
| 2 | Smoke chạm **8/68** dòng kiểm thử của phạm vi đã hiện thực (11,8 %); thêm 8 dòng chỉ có bằng chứng chạy tay trong README §9 → **16/68** (23,5 %) có bất kỳ bằng chứng nào; **52/68** (76,5 %) chưa có. 34/68 dòng là rủi ro H. | INFERENCE của A2 §6 (đối chiếu `smoke.sh` với bảng §3, A2 không chạy smoke) |
| 3 | Phạm vi sản phẩm đích đã có gì đó để test: **52/353** mã yêu cầu (31 FR + 21 NFR = 14,7 %). Đây là mẫu số của chỉ số "độ phủ yêu cầu trên phạm vi đã hiện thực". | FACT (A2 §6; danh sách ở `tests/framework/data/implemented_scope.txt`, cả 52 mã tồn tại trong 04 — đã kiểm bằng `grep`) |
| 4 | Rủi ro lớn nhất nằm ở **logic thuần** (CommandHandler, Store/ack, Ingest, Aggregator, regmap, mô hình BESS) và **test được ở mức đơn vị không cần Docker**: A1 tái hiện 15 hành vi lỗi/đáng ngờ chỉ bằng fake I/O. | FACT (A1 §9: 19 thí nghiệm, 15 tái hiện) |
| 5 | 3 bug an toàn lệnh làm **setpoint BESS ở lại thiết bị sau `expires_at`** (A1-BUG-01/02/03) và 1 đường tương tự khi bridge khởi động lại < 15 s (B-03). Watchdog thiết bị không cứu được vì heartbeat vẫn chạy. | REPRODUCED (R6–R8) / INFERENCE (B-03) |
| 6 | 3 bug toàn vẹn dữ liệu ở hợp đồng ack tích lũy (A1-BUG-04/05/10) có thể làm edge **xóa telemetry chưa vào DB**. | REPRODUCED (R10–R12) |
| 7 | Khung kiểm thử mới (pytest) đã dựng và chạy: `make ci-pr` → 17 passed (4 test sản phẩm ví dụ + 13 self-test khung), báo cáo truy vết + metrics sinh ra. Đây là **baseline**, chưa phải độ phủ. | FACT (§8) |

## 2. Hiện trạng kiểm thử (trước khung mới)

### 2.1 `tests/smoke.sh` bao phủ gì

FACT (`tests/smoke.sh`, đọc toàn bộ):

| Bước | Lệnh | Kiểm gì | Hạn chế |
|---|---|---|---|
| 2a | `retry 18 coverage --minutes 10` | Có hàng telemetry cho `pv_inverter.p`, `ess.p`, `ess.soc`, `meter.p`, `evse.p` | Chỉ "có dữ liệu", không kiểm giá trị, quality, schema |
| 2b | `retry 24 balance --minutes 5 --max-err-pct 3` | Cân bằng POC mỗi phút trọn | Oracle cùng mô hình sinh dữ liệu → chứng minh dấu/scale/word order/pid, **không** chứng minh độ chính xác (README §9; `balance_check_w` luôn 0 theo cấu trúc, `model.py:253`) |
| 3 | `send-ess-p --p-kw -100 --minutes 10 --expect APPLIED`, `sleep 35`, `check-ess` | Chuỗi ack tới `APPLIED`, `ess.p` ≈ −100 kW | `sleep 35` cố định; không kiểm thứ tự đầy đủ, không kiểm hết hạn |
| 4a | `send-ess-p --expired --expect REJECTED_STALE` | Lệnh quá hạn bị từ chối | Ca vui duy nhất của nhánh C.7 |
| 4b | `send-ess-p --repeat 2 --expect APPLIED` | Trùng `command_id` chỉ chạy 1 lần | — |
| Dọn | `send-ess-p --p-kw 0` | Đường an toàn hóa | — |

Đặc điểm kỹ thuật (FACT): cần `infra/.env` + stack đang chạy; ~2,5 phút (README §8); `retry` ghi `/tmp/smoke.out` cố định (chạy song song sẽ đè nhau); `sleep 10` giữa lần thử, `sleep 35` trước assert; chỉ trả exit code, không JUnit; không bao D7–D12 (kẹp BMS, mất broker, watchdog, EV, tiêm lỗi, state).

**Tôi không chạy smoke**: không sở hữu stack Docker, và Docker daemon không truy cập được trong phiên này (FACT: `docker images` → `Cannot connect to the Docker daemon at unix:///var/run/docker.sock`). Kết quả `SMOKE: PASS` trong README §9 là của tác giả PoC, chưa được kiểm lại.

### 2.2 Bằng chứng khác

- Chạy tay có ghi đầu ra trong README §9: D7 (kẹp BMS), D8 (mất broker 30 s, `gaps 0`), D9 (watchdog), D10 (EV), D11 (tiêm lỗi), kiểm chéo SunSpec bằng pysunspec2. FACT về việc có đầu ra; không tái lập tự động.
- Script tái hiện của A1 (`docs/testing/notes/A1-repro/a1_repro.py`, `a1_repro2.py`): in ra, không assert — là bằng chứng một lần, chưa phải test hồi quy (A1 §9).
- Công cụ tĩnh (A3 §3.7, FACT): `ruff` 20 phát hiện với cấu hình mặc định; `bandit` 11 (0 High); `pip-audit` 0 lỗ hổng × 5 file; `gitleaks` 1 phát hiện (`docs/research/ems/notes/E3-simulator-handson.md:182`, mật khẩu mặc định công khai của OpenEMS); `trivy`: `eclipse-mosquitto:2.0.20` 2 CRITICAL có bản sửa (Alpine 3.20.6 EOSL).

## 3. Khoảng trống

| Khoảng trống | Hệ quả | Bằng chứng |
|---|---|---|
| Không có test đơn vị cho bất kỳ module nào | Logic an toàn lệnh, store-and-forward, codec, quality, cửa sổ không có lưới hồi quy; mọi sửa bug đều "mù" | FACT (`tests/` chỉ có `smoke.sh`) |
| Không có contract test cho payload/topic/thuộc tính MQTT 5 | Khi edge Java/Protobuf thay PoC không có tiêu chí "tương thích" khách quan | FACT; 07 §7.3 có schema nhưng không ai validate |
| Không test ca âm ACL / danh tính | A1-BUG-04 (ingest tin `edge_id` trong payload) không bị phát hiện bởi smoke | REPRODUCED R10 |
| Không test các đường lỗi của vòng đời lệnh | 3 bug "setpoint ở lại" lọt qua smoke (smoke chỉ đi ca vui) | REPRODUCED R6–R8 |
| Không test phục hồi tự động (D8, D9, mất ingest, mất DB) | NFR-REL-* chỉ có bằng chứng tay một lần, 30 s | FACT README §9 |
| Không đo hiệu năng | NFR-PERF-003/005 chưa có số | FACT; A3 có prototype tải 1.000 edge (~32k mẫu/s) nhưng chưa đo PoC |
| Không có truy vết tự động test → yêu cầu | Không trả lời được "FR nào đã được chứng minh" | FACT (12 có mã `T-` nhưng không có liên kết tới test chạy được) |
| Healthcheck nông | "healthy" không có nghĩa là hệ chạy đúng → test e2e không được tin trạng thái container | FACT `ingest.py:175-179`, bridge `__main__.py:91` (A1 §4.10, §4.14) |
| Python host 3.13 ≠ container 3.12 | Khác biệt hành vi (thấp) chưa được kiểm | UNKNOWN |

## 4. Chức năng quan trọng chưa được test

Xếp theo A1 §8 (rủi ro × khả năng hỏng) và số dòng H của A2. "Tầng tốt nhất" = tầng rẻ nhất bắt được lỗi.

| Hạng | Chức năng (file) | Vì sao quan trọng | Tầng tốt nhất | Yêu cầu |
|---|---|---|---|---|
| 1 | Vòng đời và an toàn lệnh `CommandHandler` (`edge/bridge/bridge/commands.py`) | Ghi thiết bị điện; 4 bug tái hiện; DI sẵn | unit (+ e2e D3–D7, CMD-19) | FR-INT-007, FR-INT-018, FR-BESS-005/007/008/009, FR-SEC-008/009, NFR-SEC-004/011, NFR-REL-012 |
| 2 | Store-and-forward + `TELEMETRY_ACK` (`store.py`, `uplink.py`, `ingest.py:86-106`) | Mất dữ liệu im lặng | unit + integration (Mosquitto thật) + resilience (D8) | FR-INT-008/009, NFR-DATA-001, NFR-REL-016 |
| 3 | Ingest: dedupe, danh tính, bộ đếm (`ingest/ingest.py`) | Bảo mật + dữ liệu | unit (fake DB) + db + integration | FR-HIST-002/004, FR-SEC-004, NFR-DATA-002 |
| 4 | Codec `regmap` + lint map/`site.yaml` | Lỗi map = số sai toàn hệ thống; dùng chung hai phía nên e2e không bắt được lỗi đối xứng (R-15-01) | unit (vector vàng độc lập) + property | FR-INT-003/004, NFR-DATA-003/004 |
| 5 | Máy trạng thái quality của poller (`poller.py:108-131`) | Quality sai → hiển thị sai/che dữ liệu | unit (fake client) + integration (pymodbus server cục bộ) | FR-MON-002, NFR-DATA-005 |
| 6 | Aggregator C1–C4 (`aggregate.py`) | Đầu vào mọi báo cáo | unit + property | FR-MON-001, FR-HIST-003 |
| 7 | Mô hình BESS/site (`vsite/model.py`) — oracle của e2e | Oracle sai → mọi e2e vô nghĩa | unit + property | FR-INT-014, FR-BESS-001 |
| 8 | Watchdog/fail-safe | Lưới an toàn cuối | unit (mô hình) + resilience (D9) | FR-INT-018, NFR-REL-002/003 |
| 9 | ACL Mosquitto | Ranh giới bảo mật | security/integration | FR-SEC-004, NFR-SEC-003 |
| 10 | Schema DB (`infra/db/init.sql`) | Tính duy nhất, view `latest_value` | db | FR-HIST-002, NFR-DATA-002 |
| 11 | CSMS stub `SET_EV_LIMIT` | EV P1, nhiều lỗ | unit (fake `cp`) | FR-EV-005 |
| 12 | REST tiêm lỗi vsite | Độ tin cậy của harness | unit (aiohttp test client) | FR-INT-014 |

## 5. Rủi ro production xếp hạng

Mã là PoC; production đích là Java/Spring Boot + React (ADR-20). Các rủi ro dưới đây là rủi ro **hợp đồng/thiết kế sẽ được mang sang** nếu không có test hồi quy bám hợp đồng (INFERENCE, theo A1 §7). Điểm = tác động (1–5) × khả năng (1–5).

| Hạng | Rủi ro | Tác động | Khả năng | Điểm | Bằng chứng chính | Biện pháp test (02) |
|---|---|---|---|---|---|---|
| R1 | **Lệnh làm thiết bị ở trạng thái không an toàn/không đúng sự thật**: setpoint ở lại sau hạn (supersede trước khi ghi; readback lỗi; hoàn nguyên lỗi vẫn `COMPLETED`; restart < 15 s quên lệnh), envelope hỏng không có ack kết thúc, hàng đợi lệnh bị chặn | 5 | 4 | 20 | A1-BUG-01/02/03/07/19, B-03, B-05 | Ma trận unit "mọi đường lỗi kết thúc an toàn" + e2e CMD-19 + resilience D9 |
| R2 | **Mất dữ liệu im lặng** ở hợp đồng ack tích lũy (ack giả từ edge khác, khởi tạo `contig` sai, lỗ seq vĩnh viễn, ack xóa hàng chưa gửi) | 5 | 3 | 15 | A1-BUG-04/05/10, B-07 | Unit Store/Ingest + integration Mosquitto + resilience D8, mất ingest/DB |
| R3 | **Vượt ranh giới edge/tenant**: ứng dụng tin `edge_id` trong payload; ingest được publish `down/config` cho mọi edge | 5 | 3 | 15 | A1-BUG-04, `acl.conf` | Security: ca âm ACL + "danh tính lấy từ topic"; contract test bắt buộc cho ingest Java |
| R4 | **Thời gian sai**: `ts_src = 0`, cửa sổ mất khi đồng hồ lùi, `clock_state` cứng `SYNCED`, IL-06 chưa có | 4 | 3 | 12 | A1-BUG-09/11 | Unit với `FakeClock.step_wall`, property cửa sổ |
| R5 | **Lệch hợp đồng tài liệu ↔ mã** (mã interlock `IL-04` thay `IL-03`; quality khi giữ giá trị; replay trả gì) | 3 | 4 | 12 | B-01 (FACT), A1-BUG-21, A2 Q1/Q2 | Contract test lấy giá trị từ 07/10; câu hỏi mở gửi chủ tài liệu |
| R6 | **Không quan sát được hỏng hóc**: healthcheck nông, luồng MQTT chết im lặng sau exception trong callback | 4 | 2 | 8 | A1-BUG-08, A1 §4.10 | Resilience: payload `down/config` hỏng → kỳ vọng bridge vẫn kết nối; e2e không tin "healthy" |
| R7 | **Hiệu năng ở quy mô chưa đo** (outbox không index, ingest 1 transaction/tin, `latest_value` quét toàn bảng, `client_id` ingest cứng) | 3 | 3 | 9 | A1 §7.6 | Perf nightly: NFR-PERF-003/005 trên PoC, tải aiomqtt |
| R8 | **Oracle mô phỏng yếu** (cân bằng tautological, SOC vượt `soc_max` khi tăng tốc, map dùng chung hai phía) | 3 | 3 | 9 | A1-BUG-14, R-15-01 | Vector vàng độc lập, property physics, không dùng `SIM_SPEED>1` khi kiểm năng lượng |
| R9 | **Chuỗi cung ứng/vệ sinh bảo mật**: image Mosquitto EOSL có CRITICAL sửa được; DSN mặc định có mật khẩu cứng (`ingest.py:42`, `ems_cli.py:34`) | 3 | 2 | 6 | A3 §4 | Security gate: trivy CRITICAL fixable = 0 (release), gitleaks, rule semgrep nội bộ |

## 6. Danh sách bug nghi ngờ và trạng thái

Nguồn: A1 §5 (A1-BUG-xx) và A2 §4 (B-xx). Trạng thái tại 2026-10-12: **chưa bug nào được sửa**; chưa có test đỏ nào trong repo (khung mới chỉ có test ví dụ). Cột "Test xác nhận" là nơi test đỏ phải được viết, đánh dấu `@pytest.mark.bug(...)` + `xfail(strict=True)` cho tới khi chủ thư mục sửa.

| ID | Trùng | Mức | Trạng thái bằng chứng | Mô tả ngắn | Vị trí | Test xác nhận (tầng) |
|---|---|---|---|---|---|---|
| A1-BUG-01 | B-04 | Cao | REPRODUCED (R6) | Supersede trước khi ghi lệnh mới; ghi lỗi → setpoint lệnh cũ ở lại vô hạn | `commands.py:151-159` | unit `tests/unit/bridge` (CMD-17 ca âm) |
| A1-BUG-02 | — | Cao | REPRODUCED (R7) | Readback lỗi → `FAILED_*` mà không tạo `lifetime` → không hoàn nguyên | `commands.py:156-172` | unit |
| A1-BUG-03 | — | Cao | REPRODUCED (R8) | Ghi hoàn nguyên lỗi vẫn `EXPIRED → COMPLETED` | `commands.py:196-198` | unit |
| B-03 | — | Cao | INFERENCE | Lệnh hiệu lực chỉ trong RAM; restart bridge < 15 s → setpoint cũ vô hạn | `commands.py:32,180` | e2e/resilience (CMD-19, cần chủ Docker) |
| A1-BUG-04 | B-02 | Cao | REPRODUCED (R10) | Ingest tin `edge_id` trong payload → ghi dữ liệu và `TELEMETRY_ACK` thay edge khác | `ingest.py:57,105,124,134,138` | unit + security/integration (ACL-03) |
| A1-BUG-05 | — | Cao | REPRODUCED logic (R11); kích hoạt INFERENCE | Ack lần đầu khởi tạo từ seq nhỏ nhất đã thấy → xóa seq chưa vào DB | `ingest.py:90-98` | unit (fake DB) + db |
| A1-BUG-10 | — | TB–Cao | REPRODUCED hệ quả (R12); kích hoạt SUSPECTED | Lỗ seq vĩnh viễn → ack đứng yên, gửi lại mãi | `__main__.py:94-97`, `store.py:42-60`, `ingest.py:156-157` | unit |
| B-07 | — | TB | INFERENCE | `TELEMETRY_ACK` xóa cả hàng chưa gửi (không kiểm `ack_seq ≤ seq đã gửi`) | `uplink.py:99-100`, `store.py:84-88` | unit (ACL-04) |
| A1-BUG-06 | — | TB | REPRODUCED (R13) | `COUNTER_RESET` giả khi backfill đến sau live | `ingest.py:76-77,108-116` | unit + db |
| A1-BUG-07 | B-06 | TB | REPRODUCED (R9) | Envelope sai định dạng → không ack kết thúc (07 yêu cầu `REJECTED_INVALID`) | `commands.py:61-65,87,111,116,119` | unit (CMD-20) |
| A1-BUG-08 | — | TB | REPRODUCED một phần (R14) + FACT nguồn paho | Exception trong callback `down/config` giết luồng MQTT; health vẫn xanh | `uplink.py:94-100` | unit + resilience |
| A1-BUG-09 | — | TB | REPRODUCED (R1) | `ess.clock` không được model cấp → `ts_src = 0` (1970) | `model.py:126-134`, `poller.py:98-99` | unit (lint map↔model) |
| A1-BUG-11 | — | TB | REPRODUCED (R17) | Đồng hồ tường lùi → mất cửa sổ đang mở | `aggregate.py:49-53` | unit + property |
| B-01 | — | TB (H theo A2) | FACT (lệch hợp đồng) | BMS cũ trả `REJECTED_INTERLOCK:IL-04`, tài liệu 10 §11.4 / 04 AC-BESS-04 là `IL-03` | `commands.py:137` | unit (CMD-12) |
| B-05 | — | TB | INFERENCE | `lifetime()` ngủ cứng 8 s → lệnh ngắn hoàn nguyên trễ tới 8 s | `commands.py:185,193-196` | unit (CMD-16) |
| A1-BUG-17 | B-08 | TB | SUSPECTED | CSMS: lệnh cũ hết hạn xóa profile của lệnh mới; không idempotency/trần dòng | `csms.py:203-231` | unit |
| A1-BUG-12 | — | Thấp–TB | REPRODUCED (R4) | REST tiêm lỗi không kiểm kiểu → vòng `physics` chết | `vsite/__main__.py:68-82` | unit (aiohttp) |
| A1-BUG-18 | — | Thấp–TB | SUSPECTED | HTTP đồng bộ trong event loop CSMS | `csms.py:97-103` | unit |
| A1-BUG-19 | — | Thấp–TB | SUSPECTED | Readback chờ theo envelope, không trần → lệnh `p_w=0` có thể bị trễ | `commands.py:58-66,160-172` | unit |
| A1-BUG-13 | — | Thấp | REPRODUCED (R5) | Sau watchdog revert, ghi setpoint vẫn thực thi khi `state=3` | `model.py:145-148,171` | unit (cần chốt hành vi — UNKNOWN 07) |
| A1-BUG-14 | — | Thấp | REPRODUCED (R3) | SOC vượt `soc_max` khi `SIM_SPEED` lớn | `model.py:120,159-170` | unit/property |
| A1-BUG-15 | — | Thấp (latent) | REPRODUCED (R2) | `encode` không kiểm phạm vi (quấn số) | `regmap.py:70,94-96` | unit + property |
| A1-BUG-16 | — | Thấp (latent) | SUSPECTED | `write/read_point` bỏ SF | `poller.py:142,156` | unit |
| A1-BUG-20 | B-10 | Thấp | SUSPECTED | `command_ack` không dedupe, `last_state` lùi | `ingest.py:118-127` | db/integration |
| A1-BUG-21 | — | Thấp | SUSPECTED / spec-gap | Giá trị giữ khi exc 04/06 gắn `GOOD` | `poller.py:124-131` | unit sau khi chốt (A2 Q2) |
| A1-BUG-22 | — | Thấp | FACT | `DELETE /faults/{lạ}` trả 200 | `vsite/__main__.py:86-99` | unit |
| B-09 | — | Thấp | INFERENCE | `p_w=true` lọt kiểm kiểu (bool là int) | `commands.py:109` | unit (CMD-03) |
| B-11 | — | Thấp | FACT (thiếu) | Response Topic lạ chỉ log, không sự kiện bảo mật | `commands.py:77-78` | unit |
| B-12 | — | Thấp | INFERENCE | Trạng thái bộ đếm chỉ trong RAM ở ingest | `ingest.py:39,108-111` | unit |

Ngoài mã: schema gauge của 07 không hợp lệ theo Draft 2020-12 (`$id` có fragment) — FACT A3 §3.3; test dùng `Draft7Validator`. Báo cho chủ 07.

## 7. Vấn đề testability

| Vấn đề | Vị trí (FACT) | Cách khung xử lý **không sửa mã sản phẩm** | Refactor đề xuất cho chủ thư mục |
|---|---|---|---|
| Đồng hồ gọi trực tiếp (`time.time/monotonic`) | `model.py:114-151,188,224,237`; `poller.py:73`; `store.py:16`; `commands.py` | `framework.clock.patch_module_time(monkeypatch, module, FakeClock)` chỉ thay thuộc tính `module.time` (không vá module `time` toàn cục — bài học R5: vá toàn cục làm hỏng asyncio) | Tiêm `clock: Callable[[], float]` |
| `asyncio.sleep(8)` cứng | `commands.py:185` | `patch_module_asyncio_sleep` (sleep tua đồng hồ giả, không chờ thật) | Tham số `tracking_delay_s` |
| Cấu hình đọc lúc import | `aggregate.py:12-14`, `csms.py:30-32`, bridge `__main__.py:24-25` | `monkeypatch.setenv` + `importlib.reload` trong test | Đọc trong constructor |
| Constructor làm I/O | `Bridge.__init__` (file, `/data`, SQLite, `ess-01` cứng), `Ingest.__init__`, `Mqtt()` của CSMS kết nối ngay | `Cls.__new__` + gán thuộc tính (cách A1 R10–R13) | Factory/`from_env()` |
| Random không seed | `model.py:71,185-187` | So sánh có dung sai; `pytest-randomly` reseed `random` mỗi test → tái lập theo seed in ra | Tiêm `rng` |
| Logic xen I/O | `ingest.telemetry()`; `csms.handle_command` | Fake DB/client | Tách hàm thuần `decide_ack(...)`, `counter_check(...)` |
| Nhiều import root (`bridge`, `regmap`, `vsite`, `ingest`) | Dockerfile `PYTHONPATH=/app/maps:/app` | `pythonpath` trong `pyproject.toml`, `--import-mode=importlib`; mutmut dùng workspace riêng (`tests/framework/mutation_ws.py`) | Không bắt buộc |
| Healthcheck nông | bridge/ingest | Test e2e kiểm hành vi, không kiểm `healthy` | Health phản ánh MQTT/DB/poller |
| ID cứng | `ess-01` trong bridge, `edge-vsite01`/`site-bd-01` trong CLI | Dùng đúng `site.yaml`; cô lập dữ liệu bằng `command_id` duy nhất + cửa sổ thời gian | Đọc từ `site.yaml` |
| Thread paho + drain | `uplink.py` | Test với Mosquitto thật (integration), `timeout_method=thread` | — |

## 8. Điều đã làm hôm nay và điều chưa kiểm

FACT (lệnh và đầu ra rút gọn, 2026-10-12, Python 3.13.16, `.venv`):

```text
make venv            -> pip check: No broken requirements found.
make lint            -> ruff check tests: All checks passed! ; 37 files already formatted
                        (product code, chỉ báo cáo: 101 phát hiện với cấu hình mới)
make ci-pr           -> unit: 17 passed in 2.44 s ; property/contract/docs: no tests collected (ALLOW_EMPTY=1)
                        report: Req coverage implemented scope 3/52 (5.8 %) ; core coverage line 8.8 % / branch 5.1 %
                        gates: rc=0
MUT_MODULES=regmap make mutation
                     -> regmap.py: 234 mutant, killed 100, survived 76, no_tests 58 -> score 56.8 % (100/176)
```

Chưa kiểm (UNKNOWN cho tới khi có người chạy): tầng `db`, `integration`, `e2e`, `resilience`, `perf` (cần Docker; daemon không truy cập được trong phiên này và tôi không sở hữu stack `emspoc`); fixture testcontainers Mosquitto/TimescaleDB trong khung **chưa được chạy** (A3 đã chạy được mẫu tương tự — A3 §7 dòng 17–18); `tests/smoke.sh` chưa chạy lại.
