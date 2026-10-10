# 15 — Bộ mô phỏng thiết bị và lựa chọn messaging (MQTT hay gì khác)

[← Mục lục](index.html) · [06 Kiến trúc](06-system-architecture.html) · [07 Tích hợp](07-device-integration.md) · [10 An toàn](10-security-and-reliability.md) · [11 Lộ trình](11-mvp-and-roadmap.html) · [13 Rủi ro](13-open-questions-and-risks.md) · [14 Nguồn](14-source-register.md)

- Phiên bản 1 · Ngày 2026-10-10 · Trạng thái: đề xuất, chờ PoC-02 và ý kiến pháp lý về giấy phép broker.
- Trả lời câu hỏi: *"Nghiên cứu các source các thiết bị simulator và dùng MQTT hoặc message nào không"*.
- Ghi chú nghiên cứu gốc, bảng bằng chứng đầy đủ (E2-01…E2-50) và câu hỏi mở: [notes/E2-simulators-messaging.md](notes/E2-simulators-messaging.md). Mọi FACT lấy qua kết quả tìm kiếm (không mở trang, không clone repo). Nhãn: `[FACT]`, `[INFERENCE]`, `[PROPOSAL]`, `[UNKNOWN]`.
- Tài liệu này **mở rộng** 06 (ADR-03/04/05, PoC-02) và 07 (§7, §8, §11), tuân theo K §6 (R-01 dấu P, R-12 topic, #20 uplink, #33 nhãn "Mô phỏng").

## Mục lục

1. [Tóm tắt khuyến nghị](#1-tóm-tắt-khuyến-nghị)
2. [Bộ simulator theo môi trường](#2-bộ-simulator-theo-môi-trường)
3. [Thiết kế "virtual site"](#3-thiết-kế-virtual-site)
4. [Kế hoạch kiểm thử dùng simulator và giới hạn](#4-kế-hoạch-kiểm-thử-dùng-simulator-và-giới-hạn)
5. [Quyết định messaging edge↔cloud](#5-quyết-định-messaging-edgecloud)
6. [Topic, QoS, payload và ví dụ JSON](#6-topic-qos-payload-và-ví-dụ-json)
7. [Lựa chọn broker](#7-lựa-chọn-broker)
8. [Messaging nội bộ cloud](#8-messaging-nội-bộ-cloud)
9. [Live update cho frontend](#9-live-update-cho-frontend)
10. [Rủi ro và câu hỏi mở](#10-rủi-ro-và-câu-hỏi-mở)
11. [Nguồn](#11-nguồn)

---

## 1. Tóm tắt khuyến nghị

| # | Câu hỏi | Khuyến nghị | Nhãn | Căn cứ chính |
|---|---|---|---|---|
| D-15-01 | Có simulator sẵn cho thiết bị của ta không? | **Không có emulator Huawei/Sungrow/tủ BESS Trung Quốc mã mở.** Có thư viện tốt để tự dựng: pymodbus (BSD-3), thư viện `ocpp` (MIT), simulator OCPP của SAP (Apache-2.0), c104/j60870 cho IEC 104 (GPLv3, chỉ dùng làm công cụ test) | [FACT] + [INFERENCE] | E2-01, E2-12, E2-15, E2-16, E2-25, E2-26 |
| D-15-02 | Làm simulator thế nào? | **"Virtual site"** tự xây: sinh thanh ghi từ **cùng register map YAML** của driver + mô hình PV (pvlib/PVGIS), tải, BESS (SOC có hiệu suất, CCL/DCL), công tơ POC cân bằng; REST tiêm lỗi; Toxiproxy cho lỗi mạng | [PROPOSAL] | §3 |
| D-15-03 | Simulator có thay được thiết bị thật? | **Không.** Kết quả mô phỏng không nâng driver lên `VERIFIED_*`; cần vector vàng từ thiết bị thật, HIL lab, pilot | [PROPOSAL] (D-07-13) | §4.3 |
| D-15-04 | Dùng MQTT không? | **Có — MQTT 5** (không phải 3.1.1) qua TLS/mTLS, outbound-only, hợp đồng riêng (Protobuf + zstd). Sparkplug B chỉ là đầu ra phụ P2. Không Kafka/gRPC/AMQP từ edge | [PROPOSAL], giữ K §6 #20 | §5 |
| D-15-05 | Lệnh xuống edge? | MQTT 5 QoS 1, **không retained**, Message Expiry = `expires_at − now`, Correlation Data = `command_id`, Response Topic cố định `…/up/cmd-ack`; state machine và idempotency ở tầng ứng dụng (07 §8) | [PROPOSAL] | E2-46 |
| D-15-06 | File lớn (firmware, gói driver, backfill rất dài)? | HTTPS pre-signed URL; MQTT chỉ mang con trỏ + hash + chữ ký | [PROPOSAL] | §5.3 |
| D-15-07 | Broker nào? | Hợp đồng **không phụ thuộc broker**. PoC-02 so **EMQX Enterprise** (license) — **HiveMQ Enterprise** (license, Java) — **RabbitMQ 4.x** (mở). **Bỏ VerneMQ.** Dev/CI: Mosquitto 2.1. Pilot ≤ ~100–200 edge: có thể Mosquitto 2.1 một node + standby, có tiêu chí thoát | [PROPOSAL] dựa trên [FACT] giấy phép | E2-34…E2-40 |
| D-15-08 | Giấy phép broker có vấn đề gì? | **EMQX từ 5.9 là BSL 1.1**: cluster cần license thương mại; grant một node **không** áp khi tích hợp vào sản phẩm bán cho bên thứ ba → SaaS của ta nhiều khả năng phải mua license. HiveMQ CE không có cluster. VerneMQ: gói nhị phân thương mại trả phí | [FACT] + [INFERENCE] pháp lý | E2-34, E2-36, E2-37 |
| D-15-09 | Kafka ở MVP? | **Không.** Broker → ingest trực tiếp, ack sau commit DB (edge buffer là log bền); sự kiện nghiệp vụ qua transactional outbox PostgreSQL. Nâng cấp khi chạm ngưỡng §8.3 | [PROPOSAL], đồng ý 06 ADR-05 | §8 |
| D-15-10 | Live update cho UI? | **SSE** (giữ 06 ADR-03). **Không** MQTT-over-WebSocket tới trình duyệt | [PROPOSAL] | E2-50 |

---

## 2. Bộ simulator theo môi trường

### 2.1 Bốn môi trường

| Môi trường | Thành phần [PROPOSAL] | Mục tiêu | Không dùng cho |
|---|---|---|---|
| **(a) Laptop dev** | `docker compose`: 1–3 virtual site · edge (build local) · Mosquitto 2.1 · cloud stack · 1 charger ảo (Monta web emulator hoặc script `ocpp`) · diagslave/ModbusPal để thử tay | Viết driver, controller, UI với dữ liệu "sống" | Đo hiệu năng |
| **(b) CI** | Testcontainers (kiến thức nền, chưa có nguồn) khởi broker + virtual site + Toxiproxy · kịch bản tất định (seed, đồng hồ tăng tốc) · test hợp đồng JSON Schema/Protobuf · đêm: ma trận lỗi §3.4 · tuần: "edge ảo" phát payload tới 1.000–10.000 kết nối · master 104 giả (c104/j60870, P1) · SAP simulator nhiều charger (P1) | Hồi quy logic edge, arbiter, buffer, ingest, lệnh | Kiểm map thiết bị thật |
| **(c) HIL lab** | **Edge phần cứng thật** + thiết bị thật tối thiểu (07 §11.4) + virtual site cho phần thiếu trên OT LAN · RS-485 thật · WAN giả 4G (Toxiproxy/netem) · master 104 giả · đo vòng giới hạn xuất end-to-end | Cấp `VERIFIED_LAB`; đo thời gian thật | — |
| **(d) Demo bán hàng** | Tenant riêng **"Demo – Mô phỏng"** · virtual site + **edge ảo trong cloud** · phát lại ngày điển hình (nắng, mây, vượt trần nhập, mất mạng) · tài khoản chỉ đọc + kịch bản lệnh sandbox · reset hằng đêm | Trình diễn | Không có route tới edge thật; dữ liệu không vào KPI/benchmark; mọi màn hình/báo cáo/export ghi "Mô phỏng" |

### 2.2 So sánh công cụ (rút gọn)

Trung thực: **R** = register map, **B** = có hành vi, **P** = vật lý. Bảng đầy đủ (URL, phiên bản, rủi ro) ở [E2 §3.1](notes/E2-simulators-messaging.md#31-bảng-so-sánh-công-cụ-mô-phỏng).

| Nhóm | Công cụ | Giấy phép | Ngôn ngữ | Trung thực | Dùng ở | Ghi chú |
|---|---|---|---|---|---|---|
| Modbus | **pymodbus** (server API; simulator REST) | BSD-3 | Python | R → B (tự viết logic) | a, b, c, d | 3.14.0 (07/2026). App simulator sẽ bị thay bởi "simulator3" trước v4 → dùng server API, khóa phiên bản [FACT] |
| Modbus | modbus-tk | LGPL-2.1 | Python | R | — | Không cần khi đã có pymodbus |
| Modbus | diagslave / ModbusPal | Freeware / GPL | Binary / Java | R / R-B | a, c | Thử tay; không nhúng |
| Modbus | Modbus Slave (Witte) | Thương mại | Windows | R | c | Không có nguồn trong phiên [UNKNOWN] |
| Modbus Java | j2mod / digitalpetri modbus | Apache 2.0 / EPL-2.0 (thứ cấp) | Java | R | b (phương án B) | OpenEMS dùng fork `io.openems:j2mod` [FACT] |
| Modbus | Node-RED modbus | [UNKNOWN] | Node.js | R/B | — | Không có nguồn trong phiên |
| SunSpec | pysunspec2 + model JSON | Apache 2.0 (nixpkgs) | Python | — | b | Nguồn định nghĩa model để sinh chuỗi "SunS" |
| SunSpec | emdem/sunspec-sim | MIT | Python | R | a | Simulator SunSpec mã mở duy nhất tìm thấy; dự án cá nhân |
| Inverter/BESS | OpenEMS `Simulator.*` | EPL-2.0/AGPL theo module | Java | B | b (nếu ADR-07 chọn OpenEMS) | Channel ảo **trong** Edge: kiểm controller, **không** kiểm driver [INFERENCE] |
| Inverter | Huawei/Sungrow emulator | — | — | — | — | **Không tìm thấy**; chỉ có client (`huawei-solar-lib`) và proxy cache một kết nối |
| Victron | velib `dbusdummyservice`, emulator cộng đồng | [UNKNOWN] | Python | R/B | — | Chỉ khi làm driver Victron |
| Công tơ | SDM630 emulator | — | — | — | — | Chỉ có cấu hình ESPHome (forum); tự dựng công tơ ảo |
| OCPP CP | **SAP e-mobility-charging-stations-simulator** | Apache-2.0 | Node.js | B | b | Scale nhiều trạm; hỗ trợ 2.0.1 chưa xác minh |
| OCPP CP | Monta ocpp-emulator / MicroOcpp Simulator / Solidstudio VCP | Mở (license cần kiểm) / ? / Apache-2.0 | — | B | a, c | Chặn/sửa message để tái hiện charger không chuẩn |
| OCPP lib | **`ocpp` (Mobility House)** | MIT | Python | — | b | 1.6 + 2.0.1; viết CP ảo có quirk (ví dụ Easee) |
| CSMS | SteVe / CitrineOS | GPL / [UNKNOWN] | Java / TS | — | c | SteVe chưa hỗ trợ Security Whitepaper → chỉ lab |
| Charger SIL | EVerest | Apache-2.0 [INFERENCE] | C++ | B/P | c | Trung thực nhất, nặng |
| DR | OpenLEADR (py 2.0b không duy trì; `openleadr-rs` 3.1) | [UNKNOWN] | Python/Rust | B | P2 | Reference OpenADR 3 của Alliance chỉ cho thành viên |
| DR | EPRI IEEE 2030.5 client | BSD-3 | C | — | P2 | Test tool chuẩn là thương mại (QualityLogic) |
| IEC 104 | **c104** / **j60870** / QTester104 | GPLv3 / GPLv3 + độc quyền / [UNKNOWN] | Python / Java / Qt | B | b, c (P1) | GPL **chỉ trong công cụ test**; nhúng vào edge → mua license |
| IEC 61850 | libIEC61850 | GPLv3 hoặc thương mại | C | — | P2 | Như trên |
| Lưới | pandapower / PyPSA / GridLAB-D / OpenDSS | BSD / MIT / BSD-style / [UNKNOWN] | — | P | — | Quá mức cần cho C&I sau một POC |
| Đồng mô phỏng | HELICS / mosaik | BSD-3 / LGPL-2.1 | — | — | P2 | HIL lớn, nghiên cứu |
| Pin | PyBaMM / **BLAST-Lite** / mô hình bucket | BSD-3 / BSD-3 / của ta | Python | P | BLAST-Lite cho backtest 08 | PyBaMM quá chi tiết cho EMS |
| PV | **pvlib + PVGIS TMY** | BSD-3 [INFERENCE] / điều khoản JRC [UNKNOWN] | Python | P | a, b, d | PVGIS 5.3 (SARAH-3) phủ phần lớn châu Á |
| Lỗi mạng | **Toxiproxy** | MIT | Go | — | b, c | Chỉ TCP; Modbus RTU kiểm ở HIL |

**Dữ liệu mẫu.** Profile PV: PVGIS qua pvlib (sinh sẵn, commit CSV vào repo test). Hình dạng tải: NREL ComStock (15 phút, **của Mỹ**, giấy phép mâu thuẫn "ComStock License" vs CC BY 4.0 — kiểm trước khi đưa vào demo). **Không dùng Pecan Street** (miễn phí chỉ cho đại học phi thương mại). Ưu tiên dữ liệu pilot VN đã ẩn danh khi có.

**Ngôn ngữ của virtual site.** Đề xuất Python (pymodbus + pvlib) vì đây là **công cụ test** cô lập trong container, nói chuyện qua Modbus/OCPP/REST, không vào sản phẩm. Phương án B thuần Java (digitalpetri/j2mod server + profile CSV sinh trước) nếu đội muốn một stack. Không mâu thuẫn K R-22 (R-22 về runtime sản phẩm) nhưng cần ghi vào 06/11.

---

## 3. Thiết kế "virtual site"

### 3.1 Sơ đồ

```
                       REST điều khiển (chỉ mạng test): kịch bản, tốc độ, tiêm lỗi
                                        │
┌───────────────────────────── VIRTUAL SITE (container) ─────────────────────────────┐
│ Đồng hồ kịch bản (seed, 1×/10×/60×, Asia/Ho_Chi_Minh)                                │
│                                                                                      │
│  PV model ──(p_pv)──┐                                                                │
│  (pvlib/PVGIS,      │                                                                │
│   kẹp p_limit_pct)  ├──► Cân bằng POC: P_grid = P_load − P_pv − P_bess ──► Công tơ   │
│  Load model ─(p_load)┤      (P_bess > 0 = xả, K R-01)                       POC ảo   │
│  BESS model ─(p_bess)┘      bộ đếm e_import / e_export (int64 Wh, R_wrap)            │
│  (SOC, η, CCL/DCL,                                                                   │
│   τ, ramp, watchdog)                                                                 │
│                                                                                      │
│  Lớp mã hóa: nạp register map YAML của driver (scale, word order, sentinel)          │
│  Modbus TCP server :1502.. (mỗi thiết bị một unit/port) │ OCPP CP (P1) │ IEC104 (P1) │
└──────────────────────────────────────────┬──────────────────────────────────────────┘
                         Toxiproxy (latency, timeout, reset, down)
                                           │
                                   EDGE (thật hoặc ảo) ── MQTT 5 ──► broker ──► cloud
```

### 3.2 Mô hình

| Khối | Mô hình [PROPOSAL] | Tham số |
|---|---|---|
| PV | Công suất AC từ TMY PVGIS (pvlib) theo tọa độ site VN, scale theo kWp; nhiễu mây (Markov hoặc phát lại ngày thật); kẹp theo `p_limit_pct`/`p_limit_w` ghi xuống; ramp | `kwp`, `tilt`, `azimuth`, `dc_ac_ratio`, `cloud_model` |
| Tải | Profile 15 phút theo loại ngày + nhiễu + bước tải theo kịch bản | `p_base_w`, `shape_id`, `steps[]` |
| BESS | `p_cmd` kẹp vào `[−p_charge_max, p_discharge_max]`; trễ bậc 1 `τ` + ramp; sạc: `soc += (−p)·η_c·Δt/E_nom`; xả: `soc −= p·Δt/(η_d·E_nom)`; CCL/DCL giảm tuyến tính trong dải `taper_band` gần SOC biên và theo nhiệt độ; watchdog: hết `watchdog_s` không ghi → `p_cmd = 0` (hoặc giữ setpoint cũ nếu tắt, để kiểm `requires_native_fallback`) | `e_nom_wh`, `p_rated_w`, `eta_c`, `eta_d`, `soc_min/max`, `taper_band`, `tau_s`, `ramp_w_per_s`, `watchdog_s` |
| Công tơ POC | `P_grid = P_load − P_pv − P_bess`; Q đơn giản theo PF tải; bộ đếm nhập/xuất tách, int64 Wh | `sign_convention`, `ct_ratio`, `ct_reversed`, `R_wrap` |
| BMS công bố | `soc`, `soh`, `p_charge_max`, `p_discharge_max`, `cell_v_min/max`, `cell_t_min/max`, alarm word | Theo map của tủ |
| EVSE (P1) | Phiên sạc theo kịch bản; tôn trọng/không tôn trọng charging profile | `quirk_profile`, `min_a` |

Suy giảm pin (BLAST-Lite) **không** chạy trong virtual site; chỉ trong backtest tối ưu (08).

### 3.3 Điều khiển được

Lệnh của edge làm **đổi hành vi**: ghi setpoint P → BESS chạy theo (sau kẹp); ghi `p_limit_pct` → PV giảm; ghi mode → đổi luật nội bộ; ghi export limit vào "controller native ảo" → controller ảo tự giữ P_grid ≥ −limit. Có chế độ **"ghi chấp nhận nhưng không tác dụng"** để kiểm `FAILED_NO_EFFECT`.

### 3.4 Tiêm lỗi

| Lỗi | Cách tạo | Kỳ vọng ở edge/cloud |
|---|---|---|
| Mất liên lạc | Dừng trả lời; đóng TCP; Toxiproxy `timeout`/`down` | `BAD_COMM`; fallback trong `revert_timeout_s` |
| Exception Modbus 01/02/03/04/06 | Theo thanh ghi | `BAD_CONFIG`/retry có backoff |
| Một client duy nhất | Từ chối kết nối thứ hai | Edge là master duy nhất |
| Dữ liệu cũ/trễ | Toxiproxy `latency` + jitter | `UNCERTAIN_STALE`; ngân sách vòng ≤ 5 s |
| Giá trị đóng băng | Giữ nguyên giá trị | Cờ `FROZEN` |
| Alarm | Bật/tắt bit | Ánh xạ alarm, SOE |
| Timestamp sai thứ tự / đồng hồ thiết bị lệch | `ts_src` đảo; giờ địa phương thay UTC | Chuẩn hóa UTC; `UNCERTAIN_CLOCK` |
| Reset/quay vòng bộ đếm | Đặt về 0 hoặc qua `R_wrap` | `COUNTER_RESET`; không kWh âm |
| CT lắp ngược | Đảo dấu P công tơ | Phép thử dấu báo lỗi |
| Kẹp bởi BMS | Giảm DCL đột ngột | `APPLIED_CLAMPED` |
| Mất WAN/broker | Toxiproxy giữa edge và broker; dừng broker | Store-and-forward, backfill, `seq` liên tục |
| Map lệch cố ý | Word order/scale sai | Kiểm range/plausibility bắt được |

---

## 4. Kế hoạch kiểm thử dùng simulator và giới hạn

### 4.1 Ánh xạ vào các tầng test của 07 §11.1

| Tầng 07 | Simulator dùng | Thêm từ tài liệu này |
|---|---|---|
| L1 Giải mã driver | Không (vector vàng thật) | Vector vàng là **điều kiện** để map được dùng trong virtual site |
| L2 Hợp đồng | Edge ảo phát payload | Kiểm thuộc tính MQTT 5 (Content Type, Correlation Data, Message Expiry) |
| L3 Mô phỏng thiết bị | Virtual site, SAP/`ocpp` CP, c104 | Kịch bản tất định, đồng hồ tăng tốc |
| L4 Tiêm lỗi | Virtual site + Toxiproxy | Ma trận §3.4 chạy hằng đêm |
| L5 HIL | Thiết bị thật + virtual site bổ sung | Đo thời gian thật; RS-485 thật |
| L6 Pilot | Không | `VERIFIED_FIELD` |
| L7 Tải | Edge ảo 1.000–10.000 kết nối | Ba kịch bản lưu lượng §8.2; đỉnh backfill ×10 |

### 4.2 Ca kiểm thử bổ sung [PROPOSAL]

| Mã tạm | Ca | Tiêu chí đạt |
|---|---|---|
| T-E2-01 | Lệnh tới edge offline, edge nối lại sau `expires_at` | Broker đã loại tin (Message Expiry); cloud `UNDELIVERED`; edge không thực thi |
| T-E2-02 | Lệnh có Response Topic khác `…/up/cmd-ack` | Edge bỏ qua Response Topic lạ, vẫn ack đúng topic; ghi cảnh báo bảo mật |
| T-E2-03 | Lô telemetry > `max_batch_bytes` | Edge tự chia lô; không bị broker từ chối (Mosquitto 2.1 mặc định 2 MB) |
| T-E2-04 | Đổi broker (Mosquitto ↔ ứng viên PoC-02) cùng bộ test | 100% test hợp đồng đạt — chứng minh broker-agnostic |
| T-E2-05 | 10.000 edge ảo, 2.600 tin/s thường, 26.000 tin/s đỉnh, rớt một node broker | Không mất lô đã ack; ingest đuổi kịp trong thời gian mục tiêu (PoC-02) |
| T-E2-06 | Tenant demo gửi lệnh | Lệnh chỉ tới edge ảo; test mạng chứng minh không có route tới edge thật |

### 4.3 Mô phỏng không chứng minh được

| Không chứng minh | Lý do | Bù bằng |
|---|---|---|
| Register map đúng với thiết bị thật | Virtual site sinh từ cùng YAML: cùng lỗi hai phía cho kết quả "xanh" giả | Vector vàng, tài liệu hãng, lab |
| Quirk firmware, "ghi không tác dụng", lỗi SunSpec ở thiết bị đã chứng nhận | Chưa biết thì không mô phỏng được | Ma trận model × firmware, `VERIFIED_LAB/FIELD` |
| Thời gian đáp ứng thật (ramp PCS, trễ logger, chu kỳ công tơ, RTU) | Tham số mô phỏng là giả định | Đo HIL |
| Giới hạn tài nguyên thiết bị, watchdog, mòn NVM | Hành vi chưa có tài liệu | Hỏi hãng, thử dài ngày |
| Lỗi lắp đặt điện | Chỉ mô phỏng được lỗi đã biết | Phép thử dấu khi commissioning |
| Bảo vệ BMS/PCS/rơ-le | Nằm ngoài phần mềm | Không kiểm bằng mô phỏng |
| 4G thật, NAT timeout, churn | Toxiproxy chỉ xấp xỉ | Pilot |
| Giá trị kinh tế | Profile tải không phải của VN | Dữ liệu pilot; nhãn "Mô phỏng" |

---

## 5. Quyết định messaging edge↔cloud

### 5.1 ADR đề xuất: "Giao thức edge↔cloud" (bổ sung cho K §6 #20; người viết 06 cấp số ADR)

**Bối cảnh.** Edge sau NAT/4G, outbound-only; telemetry theo lô có `seq`; lệnh có hạn, phải ack, idempotent, ký số; config mong muốn; backfill sau mất mạng tới 7–30 ngày; hosting tại VN; đội Java.

**Phương án**

| Phương án | Trade-off chính | Kết luận |
|---|---|---|
| **MQTT 5 + hợp đồng riêng** | (+) Session/Message Expiry, Response Topic + Correlation Data (business ACK), Content Type, Reason Codes, shared subscription, topic alias; mọi broker lớn và AWS/Azure Event Grid hỗ trợ [FACT E2-43, E2-44, E2-46]. (−) Tự định nghĩa và duy trì hợp đồng | **Chọn** |
| MQTT 3.1.1 | (+) Hỗ trợ rộng nhất. (−) Không expiry, reason code, correlation → nhồi vào payload | Không |
| Sparkplug B 3.0 | (+) Tiêu chuẩn ISO/IEC, birth/death, SCADA [FACT E2-47]. (−) QoS 0 dữ liệu, không ngữ nghĩa ack/expiry lệnh, 2.2/3.0 không tương thích STATE | Đầu ra phụ P2 |
| JSON-RPC/WebSocket (kiểu OpenEMS) | (+) Đã chạy ở OpenEMS [FACT E2-09]. (−) Kết nối có trạng thái tới backend, tự làm QoS, fan-out, cân bằng tải | Không; nếu dùng OpenEMS Edge thì viết bundle uplink MQTT |
| gRPC streaming | (+) Protobuf, hai chiều. (−) HTTP/2 dài hạn qua 4G/NAT, không broker | Không |
| AMQP 1.0 | (+) Ngữ nghĩa giao nhận mạnh. (−) Client edge nặng hơn, ít dùng trong IoT năng lượng | Không |
| HTTPS batch | (+) Đơn giản, hợp file lớn. (−) Không đẩy lệnh | **Bổ sung** cho OTA, gói driver, backfill rất lớn, enroll |
| CoAP / DDS / OPC UA PubSub | Thiết bị hạn chế / LAN realtime / không có companion spec PV-BESS | Không |
| Kafka từ edge | Lộ broker, client nặng, cần TCP ổn định, kém với nhiều topic [FACT E2-48] | Không |

**Quyết định [PROPOSAL].** MQTT 5 qua TLS (mTLS, chứng chỉ riêng mỗi edge), port 8883 (443 dự phòng theo 06). Payload Protobuf + zstd (JSON chỉ để debug/test). HTTPS pre-signed URL cho tệp lớn. Sparkplug B P2.

**Hệ quả.** Hợp đồng chạy được trên mọi broker MQTT 5 và trên AWS IoT Core/Azure Event Grid nếu sau này cần (lối thoát). Bài học: Google Cloud IoT Core đóng 16/08/2023 [FACT E2-45]; Azure IoT Hub chỉ cho topic cố định và đã bỏ MQTT 5 [FACT E2-44] → **không gắn hợp đồng vào topic/SDK riêng của nhà cung cấp**.

### 5.2 Tham chiếu ngành

| Hệ | Cách làm | Bài học |
|---|---|---|
| OpenEMS | Edge↔Backend: JSON-RPC qua WebSocket, cổng 8081, `edgeRpc` [FACT] | Mô hình process image tốt, nhưng giao thức backend không phải MQTT |
| Victron Venus OS / VRM | Broker FlashMQ trên GX, cầu D-Bus→MQTT, keepalive theo yêu cầu, nối máy chủ MQTT của VRM [FACT] | MQTT là kênh cloud thực tế cho thiết bị năng lượng |
| Huawei SmartLogger | Dữ liệu lên FusionSolar; bên thứ ba dùng FTP CSV (≈ 300 s) hoặc Modbus TCP; không thấy MQTT công khai [FACT] | Edge của ta đọc Modbus, không phụ thuộc kênh cloud của hãng |
| EVerest | Module trong trạm sạc nói chuyện qua MQTT [FACT] | MQTT cũng hợp làm bus nội bộ edge (tùy chọn) |
| AWS IoT Core | MQTT 3.1.1/5, shared subscription GA 04/2023, expiry, request/response [FACT] | Đích di chuyển khả thi |
| Azure | IoT Hub: topic cố định, MQTT 5 deprecated; Event Grid MQTT: MQTT 5, topic tùy ý [FACT] | Chọn đúng sản phẩm nếu dùng Azure |

### 5.3 Theo loại tin

| Loại | Kênh | Ack | Hết hạn | Idempotency |
|---|---|---|---|---|
| Telemetry uplink | MQTT `up/telemetry/{stream}` | Cloud gửi `TELEMETRY_ACK` **sau commit DB**; edge xóa `seq ≤ ack_seq` | — | `(edge_id, stream, seq)` và `(point, ts)` |
| Lệnh downlink | MQTT `down/cmd` | `up/cmd-ack` theo state machine 07 §8.4 | Message Expiry + `expires_at` + `max_latency_ms` | `command_id`; `seq` + JWS chống replay |
| Config | MQTT `down/config` retained | `reported_config_version` trong `up/state` | — | `config_version` |
| Firmware/gói driver | HTTPS pre-signed URL; MQTT mang con trỏ | Trạng thái OTA trong `up/event` | URL hết hạn ngắn | Hash + chữ ký |
| Backfill | MQTT `up/backfill` có giới hạn tốc độ; > 24 h dữ liệu → HTTPS upload file + tin báo (P1) | Như telemetry | — | Như telemetry |

**Phiên MQTT.** Edge dùng Session Expiry hữu hạn (đề xuất 1–24 h) để lệnh **còn hạn** được giao sau rớt mạng ngắn; lệnh quá hạn bị broker loại. Keepalive 30–60 s; tinh chỉnh theo NAT timeout của nhà mạng VN ở pilot (Q-E2-09). Will message: `up/state` = offline, retained; Will Delay vài giây để tránh nhấp nháy.

---

## 6. Topic, QoS, payload và ví dụ JSON

### 6.1 Không gian tên topic

Theo **K R-12** (đã áp ở 07 §7.1): `ems/v1/{edge_id}/up/…` và `ems/v1/{edge_id}/down/…`. **Không đặt tenant/site trong topic** — ánh xạ `edge_id → site_id → tenant_id` nằm ở registry cloud. Lý do: ACL đơn giản theo `client_id`, edge chuyển site không đổi topic, không lộ tenant, và **không tồn tại wildcard xuyên tenant ở tầng topic**. Cô lập tenant thực hiện ở ingest (registry) và PostgreSQL RLS (K §6 #29).

| Topic | Hướng | QoS | Retained | Thuộc tính MQTT 5 |
|---|---|---|---|---|
| `ems/v1/{edge_id}/up/state` | edge→cloud | 1 | Có (Will = offline) | — |
| `ems/v1/{edge_id}/up/telemetry/{c1..c4}` | edge→cloud | 1 | Không | Content Type, User Property `schema`, topic alias |
| `ems/v1/{edge_id}/up/event` | edge→cloud | 1 | Không | Content Type |
| `ems/v1/{edge_id}/up/backfill` | edge→cloud | 1 | Không | Như telemetry |
| `ems/v1/{edge_id}/up/cmd-ack` | edge→cloud | 1 | Không | Correlation Data (echo) |
| `ems/v1/{edge_id}/down/cmd` | cloud→edge | 1 | **Không** | Message Expiry, Correlation Data, Response Topic |
| `ems/v1/{edge_id}/down/config` | cloud→edge | 1 | Có | — |
| `int/v1/…` (06 §12) | nội bộ cloud | 0–1 | — | Listener nội bộ, không mở ra Internet |

**ACL [PROPOSAL].** Edge: publish chỉ `ems/v1/${client_id}/up/#`, subscribe chỉ `ems/v1/${client_id}/down/#`, cấm wildcard ở cấp `edge_id`. Dịch vụ ingest: `$share/ingest/ems/v1/+/up/#` (chỉ subscribe, không có quyền publish `down/cmd`). Dispatcher lệnh: chỉ publish `ems/v1/+/down/cmd`. Opt-worker: không có credential broker (06).

### 6.2 Payload

| Định dạng | Ưu | Nhược | Dùng |
|---|---|---|---|
| **Protobuf + zstd** | Có schema, tiến hóa trường an toàn, nhỏ (mục tiêu ≤ 15 B/mẫu, 07 §7.3) | Không đọc được bằng mắt | **Trên dây** |
| CBOR | Nhị phân, không cần schema | Không có hợp đồng kiểu, tiến hóa khó kiểm | Không |
| JSON | Dễ debug, JSON Schema | Lớn | Tài liệu, debug, test hợp đồng (ánh xạ 1-1 với Protobuf) |

Lô ≤ `max_batch_bytes` (đề xuất 256 KB sau nén; Mosquitto 2.1 mặc định từ chối gói > 2 MB [FACT E2-38]). Content Type dùng **thuộc tính chuẩn MQTT 5** (`application/x-protobuf+zstd` hoặc `application/json`), Payload Format Indicator = 0 (binary) / 1 (UTF-8); `schema` và `edge_seq` là User Property.

### 6.3 Ví dụ (JSON logic; trên dây là Protobuf)

Ví dụ dưới chỉ minh họa **thuộc tính MQTT 5 đi kèm**; thân payload đầy đủ theo 07 §7.3 và §8.3, không lặp lại hết.

**Telemetry C1 (5 s)**

```json
{
  "mqtt": {
    "topic": "ems/v1/edge-0f3e9c2a/up/telemetry/c1",
    "qos": 1, "retain": false,
    "properties": {
      "content_type": "application/json",
      "payload_format_indicator": 1,
      "user_properties": {"schema": "ems.telemetry.v1", "edge_seq": "552301"}
    }
  },
  "payload": {
    "schema": "ems.telemetry.v1",
    "edge_id": "edge-0f3e9c2a",
    "stream": "c1",
    "seq": 552301,
    "batch_ts": 1791612065012,
    "config_version": 42,
    "points": [
      {"pid": 2001, "ts": 1791612060000, "w": 5, "avg": -35120.0, "last": -36000.0, "n": 5, "q": "GOOD"},
      {"pid": 3001, "ts": 1791612060000, "w": 5, "avg": 61.4, "last": 61.4, "n": 5, "q": "GOOD"},
      {"pid": 3002, "ts": 1791612060000, "w": 5, "q": "BAD_COMM"}
    ]
  }
}
```

`pid 2001` = `meter.p` tại `MTR_POC` (âm = xuất, K R-01); `pid 3001` = `ess.soc` (%). Điểm `BAD_*` không có giá trị.

**Lệnh (rút gọn; envelope đầy đủ ở 07 §8.3)**

```json
{
  "mqtt": {
    "topic": "ems/v1/edge-0f3e9c2a/down/cmd",
    "qos": 1, "retain": false,
    "properties": {
      "message_expiry_interval_s": 898,
      "correlation_data": "0192f3a4-6c1e-7b8a-9d10-3f2a1b4c5d6e",
      "response_topic": "ems/v1/edge-0f3e9c2a/up/cmd-ack",
      "content_type": "application/json",
      "user_properties": {"schema": "ems.command.v1"}
    }
  },
  "payload": {
    "schema": "ems.command.v1",
    "command_id": "0192f3a4-6c1e-7b8a-9d10-3f2a1b4c5d6e",
    "seq": 30411,
    "type": "SET_ESS_P",
    "target": {"edge_id": "edge-0f3e9c2a", "asset_id": "ess-01"},
    "params": {"p_w": 150000},
    "source": "OPERATOR",
    "danger_class": "C1",
    "valid_from": "2026-10-10T09:00:00.000Z",
    "expires_at": "2026-10-10T09:15:00.000Z",
    "sent_at": "2026-10-10T09:00:01.120Z",
    "max_latency_ms": 10000,
    "on_expiry": "REVERT_DEFAULT",
    "kid": "cmd-signer-2026-03",
    "signature": "eyJhbGciOiJFUzI1NiIsImtpZCI6…"
  }
}
```

`message_expiry_interval_s` = `expires_at − sent_at` làm tròn xuống. Message Expiry chỉ là lớp bảo vệ thứ nhất; edge **vẫn** tự kiểm `expires_at`, `max_latency_ms`, `seq`, chữ ký (07 §8.7), vì broker có thể bị chiếm (K R-11).

**Ack**

```json
{
  "mqtt": {
    "topic": "ems/v1/edge-0f3e9c2a/up/cmd-ack",
    "qos": 1, "retain": false,
    "properties": {
      "correlation_data": "0192f3a4-6c1e-7b8a-9d10-3f2a1b4c5d6e",
      "content_type": "application/json",
      "user_properties": {"schema": "ems.cmd-ack.v1"}
    }
  },
  "payload": {
    "schema": "ems.cmd-ack.v1",
    "edge_id": "edge-0f3e9c2a",
    "command_id": "0192f3a4-6c1e-7b8a-9d10-3f2a1b4c5d6e",
    "state": "APPLIED_CLAMPED",
    "ts": 1791622806250,
    "requested": {"p_w": 150000},
    "effective_setpoint": {"p_w": 120000},
    "clamp": {"code": "CLAMPED_BY_BMS", "limit_w": 120000},
    "edge_sig": {"kid": "edge-0f3e9c2a-2026-08", "jws": "…"}
  }
}
```

Mỗi chuyển trạng thái (`RECEIVED`, `ACCEPTED`, `DISPATCHED`, `APPLIED*`/`FAILED_*`, `EXPIRED`…) là một tin ack riêng, cùng Correlation Data.

---

## 7. Lựa chọn broker

### 7.1 Giấy phép và năng lực (2026)

| Broker | Cluster | MQTT 5 | Giấy phép | Auth/ACL | Tích hợp | Vận hành | Kết luận |
|---|---|---|---|---|---|---|---|
| **EMQX ≥ 5.9** | Có, **cần license thương mại** | Có | **BSL 1.1**; một node miễn phí **trừ** khi tích hợp vào sản phẩm/giải pháp bán cho bên thứ ba; chuyển Apache 2.0 sau 4 năm mỗi bản [FACT E2-34] | X.509, JWT, HTTP, SQL/NoSQL | Rule engine SQL, Kafka built-in, benchmark vendor 100k QoS1/s một node [FACT E2-35] | Erlang | **Ứng viên thương mại #1** |
| EMQX ≤ 5.8 | Có | Có | Apache 2.0 | — | WebHook, MQTT bridge | Erlang | Không: nhánh sẽ hết hỗ trợ [INFERENCE] |
| **HiveMQ Enterprise** | Có | Có | Thương mại | Extension SDK Java | Extension Kafka (kiến thức nền) | JVM — hợp đội | **Ứng viên thương mại #2** |
| HiveMQ CE | **Không** [FACT E2-36] | Có | Apache 2.0 | Extension Java | — | JVM | Dev/CI |
| **Mosquitto 2.1** | Không (kiến thức nền) | Có | EPL/EDL [INFERENCE] | Plugin; `acl_file`/`password_file` bị deprecate [FACT E2-38] | Bridge | Rất nhẹ | **Dev/CI/lab**; pilot nhỏ có điều kiện |
| VerneMQ | Có | Có | Mã Apache 2.0; **gói nhị phân/Docker trả phí khi dùng thương mại** [FACT E2-37] | Plugin | Webhooks | Erlang; tự build | **Bỏ khỏi shortlist** |
| **RabbitMQ 4.x** | Có | Có (không QoS 2; shared subscription có thể không) [FACT E2-40] | MPL-2.0 [INFERENCE] | HTTP/LDAP/cert | Consumer AMQP đọc thẳng queue | Erlang | **Ứng viên mở #3** |
| NanoMQ | Không | Có | MIT [FACT E2-39] | Cơ bản | Bridge MQTT/QUIC | Rất nhẹ | Broker **tại edge** nếu cần |
| NATS | Có | **Không** (3.1.1) [FACT E2-41] | Apache 2.0 [INFERENCE] | — | JetStream | Go | Không cho biên |
| AWS IoT Core / Azure Event Grid | Managed | Có | Dịch vụ | X.509 | Rule → dịch vụ cloud | Không vận hành | Loại ở MVP (hosting VN, 06); giữ làm lối thoát |
| Azure IoT Hub | Managed | Deprecated | Dịch vụ | — | — | — | Không |
| Google Cloud IoT Core | — | — | **Đã đóng 16/08/2023** [FACT E2-45] | — | — | — | Bài học |

### 7.2 Khuyến nghị [PROPOSAL]

1. **Hợp đồng broker-agnostic** (giữ 06 ADR-04): logic nghiệp vụ không dùng tính năng riêng của broker; chỉ dùng plugin cho xác thực, ACL, quan sát.
2. **PoC-02** chạy cùng bộ test (T-E2-04, T-E2-05) trên: EMQX Enterprise (license dùng thử), HiveMQ Enterprise (license dùng thử), RabbitMQ 4.x (mở; ingest đọc queue qua AMQP thay shared subscription).
3. **Chọn theo:** tổng chi phí 3 năm (license + vận hành), đạt PoC-02, ý kiến pháp lý (Q-E2-01), khả năng đội vận hành (HiveMQ có lợi thế Java; EMQX có lợi thế tính năng/tài liệu MQTT 5; RabbitMQ có lợi thế không phí license).
4. **Dev/CI:** Mosquitto 2.1 (hoặc EMQX một node — BSL cho phép môi trường không production).
5. **Pilot (≤ ~100–200 edge), tùy chọn:** Mosquitto 2.1 một node + standby nóng (VM failover), vì edge giữ buffer 7–30 ngày nên vài phút gián đoạn không mất dữ liệu [INFERENCE]. Tiêu chí thoát: > 200 edge, hoặc cần HA không gián đoạn, hoặc PoC-02 xong. Đây là **thay đổi** so với 06 ADR-04 ("Mosquitto chỉ dev/lab") — người viết 06 quyết.
6. **Dự trù ngân sách license broker** trong kế hoạch MVP; tiền lệ EMQX 5.9 cho thấy broker "mở" có thể đổi giấy phép (R-15-02).

---

## 8. Messaging nội bộ cloud

### 8.1 Phương án

| Phương án | Hợp khi | Không hợp | MVP |
|---|---|---|---|
| **Broker → ingest trực tiếp** (shared subscription / queue AMQP) + ack sau commit | Một consumer telemetry; buffer edge làm log bền | ≥ 3 consumer cần phát lại | **Chọn** |
| **Transactional outbox PostgreSQL + relay polling** | Sự kiện nghiệp vụ (lệnh, alarm, plan) vài tin/s | Telemetry | **Chọn**; `LISTEN/NOTIFY` chỉ để **đánh thức** relay (payload < 8.000 B, không bền) [FACT E2-49] |
| Kafka | Nhiều consumer, phát lại, phân vùng theo khóa | Thêm cụm stateful | Nâng cấp |
| Redpanda | API Kafka, vận hành gọn | BSL: cấm cung cấp như dịch vụ streaming [FACT E2-42] — ta không bán streaming, vẫn cần pháp lý | Ứng viên nâng cấp |
| NATS JetStream | Bus nhẹ | Không làm biên MQTT 5 | Không |
| RabbitMQ streams | Nếu RabbitMQ đã là broker biên | — | Có lý trong trường hợp đó |
| Redis/Valkey Streams | Hàng đợi tạm | Cache trong 06 không bền | Không cho sự kiện nghiệp vụ |

### 8.2 Lưu lượng ước tính

Giả định: site 200–500 điểm; tổng hợp tại nguồn (K §6 #19). Mẫu/s/site: **thấp** 200 × 1/60 s = 3,3; **trung bình** 50 điểm 5 s + 450 điểm 60 s = 17,5; **cao** 500 × 1/5 s = 100. Số tin MQTT đã gộp lô ≈ 0,23–0,26 tin/s/site. Mục tiêu ≤ 15 B/mẫu.

| Quy mô | Mẫu/s (thấp / TB / cao) | Tin MQTT/s thường | Đỉnh backfill (×10) | Ingest (TB / cao) |
|---|---|---|---|---|
| 100 site | 333 / 1.750 / 10.000 | ≈ 25 | ≈ 250 | 26 KB/s / 150 KB/s |
| 1.000 site | 3.333 / 17.500 / 100.000 | ≈ 250 | ≈ 2.500 | 263 KB/s / 1,5 MB/s |
| 10.000 site | 33.333 / 175.000 / 1.000.000 | ≈ 2.500 | ≈ 25.000 | 2,6 MB/s / 15 MB/s |

Khớp với 06 (≈ 260 tin/s và ≈ 35.000 mẫu/s ở 1.000 site; PoC-02 2.600/26.000 tin/s ở 10.000 edge). Dữ liệu 4G mỗi site (TB) ≈ 0,7 GB/tháng chưa tính overhead TLS/MQTT; kịch bản cao ≈ 3,9 GB/tháng. **Nút thắt là ghi TSDB (mẫu/s), không phải messaging.**

### 8.3 Quyết định và ngưỡng nâng cấp

**Không Kafka ở MVP** [PROPOSAL, đồng ý 06 ADR-05]. Chuyển sang Kafka/Redpanda khi **bất kỳ** điều kiện sau kéo dài ≥ 1 tuần:

1. ≥ 3 consumer độc lập cần đọc lại telemetry (kho cột, ML, xuất cho khách).
2. > 200.000 mẫu/s duy trì (≈ kịch bản TB ở ~10.000 site) **và** ingest cần tách khỏi tốc độ ghi DB.
3. Đỉnh backfill làm backpressure giữ edge chờ > 1 h.
4. Khách yêu cầu luồng xuất thời gian thực có phát lại.
5. Relay outbox trễ p95 > 5 s.

Khi nâng cấp: đặt log giữa broker và ingest (bridge của broker hoặc connector); **hợp đồng edge không đổi**.

---

## 9. Live update cho frontend

| Phương án | Kết luận |
|---|---|
| **SSE** | **Chọn** (giữ 06 ADR-03): một chiều, HTTP thường, vé ngắn hạn ≤ 60 s; mọi thao tác ghi qua REST có PDP/audit |
| WebSocket | Chỉ khi có nhu cầu hai chiều thật đã chứng minh; không dùng cho lệnh |
| MQTT-over-WebSocket tới trình duyệt | **Loại.** Trình duyệt chỉ có TLS một chiều, không trình chứng chỉ client [FACT E2-50] → phải mở xác thực token trên broker đang phục vụ edge và lệnh; ACL theo người dùng phức tạp; tăng bề mặt tấn công; phá tách mặt phẳng (K §6 #26). Nếu sau này khách cần subscribe trực tiếp: broker/listener **riêng**, chỉ đọc, dữ liệu đã chuẩn hóa, token ngắn hạn (Q-06-04) |

---

## 10. Rủi ro và câu hỏi mở

### 10.1 Rủi ro (mã tạm; người viết 13 cấp R-NN)

| Mã tạm | Rủi ro | Khả năng / Tác động | Giảm thiểu |
|---|---|---|---|
| R-15-01 | Virtual site sinh từ cùng register map → test "xanh" giả | Cao / Cao | Vector vàng thật, chế độ map lệch, HIL bắt buộc trước `VERIFIED_*` |
| R-15-02 | Broker "mở" đổi giấy phép (tiền lệ EMQX 5.9) | Trung bình / Trung bình | Hợp đồng broker-agnostic; T-E2-04 chạy trên ≥ 2 broker |
| R-15-03 | Chi phí license broker chưa có trong kế hoạch | Cao / Trung bình | Báo giá sớm; phương án RabbitMQ mở |
| R-15-04 | Dịch vụ managed bị khai tử (Google IoT Core 2023) | Thấp / Cao | Không dùng managed ở MVP; hợp đồng chạy được trên nhiều nơi |
| R-15-05 | Thư viện GPL (lib60870, j60870, libIEC61850, c104, SteVe) lọt vào image edge | Trung bình / Cao | SBOM + kiểm giấy phép trong CI; mua license thương mại nếu nhúng |
| R-15-06 | Tenant demo bị nhầm là dữ liệu thật hoặc chạm edge thật | Thấp / Cao | Nhãn bắt buộc, cô lập mạng, T-E2-06 |
| R-15-07 | pymodbus đổi API simulator trước v4 | Cao / Thấp | Dùng server API, khóa phiên bản, test nâng cấp |
| R-15-08 | Keepalive/NAT 4G làm rớt kết nối, tốn dữ liệu | Trung bình / Trung bình | Đo ở pilot (Q-E2-09) |

### 10.2 Câu hỏi mở

| ID | Câu hỏi | Chặn quyết định |
|---|---|---|
| Q-E2-01 | SaaS của ta có thuộc ngoại lệ "tích hợp vào sản phẩm bán cho bên thứ ba" của EMQX BSL không? Giá Enterprise? | ADR-04 |
| Q-E2-02 | Giá và điều khoản HiveMQ Enterprise tự host tại VN | ADR-04 |
| Q-E2-03 | RabbitMQ 4.x: danh sách giới hạn MQTT 5 đầy đủ (shared subscription, message expiry, will delay) | ADR-04 |
| Q-E2-04 | OpenEMS Edge có component uplink MQTT sẵn hay phải viết bundle theo hợp đồng 07? | ADR-07 |
| Q-E2-05 | SAP simulator có OCPP 2.0.1 chưa? Giấy phép Monta emulator, CitrineOS, EVerest, OpenLEADR | Công cụ EV/DR (P1/P2) |
| Q-E2-06 | Giấy phép pvlib và điều khoản dữ liệu PVGIS cho demo thương mại | Tenant demo |
| Q-E2-07 | Mosquitto 2.1 cho pilot: shared subscription, giới hạn, cert-as-username | Pilot |
| Q-E2-08 | Có profile tải C&I Việt Nam công khai, giấy phép dùng được? | Demo, backtest |
| Q-E2-09 | Keepalive/Session Expiry tối ưu trên 4G VN | Ổn định, chi phí |

### 10.3 Đề xuất sửa tài liệu khác

- **06 ADR-04:** thêm dữ kiện giấy phép (EMQX BSL, HiveMQ CE không cluster, VerneMQ nhị phân trả phí); thêm RabbitMQ 4.x; bỏ VerneMQ; cân nhắc Mosquitto ở pilot; dự trù chi phí license.
- **06 ADR-05:** NOTIFY chỉ đánh thức; ngưỡng định lượng §8.3; bảng ba kịch bản lưu lượng.
- **06 ADR-07:** chi phí bundle uplink MQTT nếu chọn OpenEMS; simulator OpenEMS chỉ test controller.
- **07 §7.1:** dùng thuộc tính chuẩn Content Type/Payload Format Indicator thay User Property `content-type`; thêm `max_batch_bytes`.
- **07 §8:** Correlation Data = `command_id`; Response Topic cố định; edge bỏ qua Response Topic lạ.
- **07 §11.2:** thay "[UNKNOWN]" bằng công cụ cụ thể ở §2.2.
- **11:** mốc "Virtual site v1" trước Gate M1; HIL trước Gate M2; tenant demo P1.

---

## 11. Nguồn

Tất cả **(qua kết quả tìm kiếm)**, không mở trang trực tiếp. Bảng claim ↔ nguồn ↔ độ tin cậy đầy đủ ở [E2 §5](notes/E2-simulators-messaging.md#5-evidence-ledger). Người viết 14 cấp mã S-xxx.

**Mô phỏng Modbus/SunSpec/thiết bị**
- https://pymodbus.readthedocs.io/en/dev/source/library/simulator/config.html
- https://pymodbus.readthedocs.io/en/v3.8.6/source/simulator.html
- https://pymodbus.readthedocs.io/en/v3.14.0/_sources/source/simulator3.rst.txt
- https://pymodbus.readthedocs.io/en/dev/source/simulator/datamodel.html
- https://www.piwheels.org/project/pymodbus/
- https://pepy.tech/projects/pymodbus
- https://github.com/bbarcklay/modbus-tk
- https://www.modbusdriver.com/index.php/diagslave.html
- https://modbuspal.sourceforge.net/
- https://sourceforge.net/p/j2mod
- https://central.sonatype.com/artifact/io.openems/j2mod
- https://jitpack.io/p/digitalpetri/modbus
- https://github.com/emdem/sunspec-sim
- https://github.com/nielsbasjes/sunspec-device
- https://github.com/otfabric/go-sunspec
- https://mynixos.com/nixpkgs/package/python313Packages.pysunspec2
- https://openems.github.io/openems.io/openems/latest/simulation/realtime.html
- https://openems.github.io/openems.io/openems/latest/gettingstarted.html
- https://zenodo.org/records/7145189
- https://github.com/OpenEMS/openems/issues/1507
- https://github.com/wlcrs/huawei-solar-lib
- https://github.com/norbim1/sun2000-modbus-cache
- https://support.spacewell.com/hc/en-001/articles/28356570657436
- https://knowledge.ampere.cloud/en/huawei-smartlogger-1000-3000-per-passthrough-an-den-amperecloud-log-anbinden
- https://github.com/victronenergy/dbus-flashmq
- https://communityarchive.victronenergy.com/questions/197508/simulate-multi-rs.html
- https://akkudoktor.net/t/sdm630-emulator-fuer-deye-sun-xxk-sg04-mqtt-deye-gateway/24950
- https://docs.evcc.io/en/meters/demo-meter

**EV, DR, IEC 104/61850**
- https://redirect.github.com/SAP/e-mobility-charging-stations-simulator
- https://oosmetrics.com/repo/SAP/e-mobility-charging-stations-simulator
- https://monta.com/en/?p=30014
- https://github.com/matth-x/MicroOcpp
- https://solidstudio.io/products/virtual-charge-point/
- https://pypi.org/project/ocpp/
- https://github.com/rwth-i5-idsg/steve
- https://lfenergy.org/projects/citrineos/
- https://www.mintlify.com/EVerest/everest-core
- https://lfenergy.org/projects/openleadr/
- https://www.openadr.org/openadr-3-0
- https://www.opensourceforu.com/2019/02/epri-open-source-software-accelerates-implementation-of-intelligent-distributed-energy-resources/
- https://github.com/mz-automation/lib60870
- https://github.com/mz-automation/libiec61850
- https://openmuc.org/iec-60870-5-104
- https://pypi.org/project/c104
- https://qtester104.sourceforge.net

**Lưới, pin, PV, dữ liệu, lỗi mạng**
- https://arxiv.org/pdf/1709.06743
- https://docs.helics.org/en/latest/developer-guide/tests.html
- https://wiki.openmod-initiative.org/wiki/Mosaik
- https://docs.pypsa.org/latest/home/license/
- https://www.nrel.gov/research/software/blast-lite--battery-lifetime-analysis-and-simulation-tool---lite
- https://pvlib-python.readthedocs.io/en/latest/reference/generated/pvlib.iotools.get_pvgis_tmy.html
- https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/getting-started-pvgis/pvgis-user-manual_en
- https://www.pecanstreet.org/dataport/licenses
- https://registry.opendata.aws/nrel-pds-building-stock/
- https://dev.co/testing/open-source/toxiproxy

**Messaging và broker**
- https://www.emqx.com/en/content/license-faq
- https://docs.emqx.com/en/emqx/latest/deploy/license.md
- https://scancode-licensedb.aboutcode.org/emq-use-grant-for-bsl-1.1.LICENSE
- https://docs.emqx.com/en/emqx/latest/data-integration/data-bridge-kafka.md
- https://community.hivemq.com/t/cluster-support-in-community-edition-ce/737
- https://vernemq.com/vernemq-licenses.html
- https://newreleases.io/project/github/vernemq/vernemq/release/2.0.1
- https://mosquitto.org/blog/2026/01/version-2-1-0-released/
- https://lf-edge.atlassian.net/wiki/spaces/LE/pages/15865096/Project+NanoMQ
- https://www.rabbitmq.com/docs/4.2/mqtt
- https://www.rabbitmq.com/docs/3.13/mqtt
- https://docs.nats.io/nats-server/configuration/mqtt
- https://docs.redpanda.com/streaming/24.2/get-started/licenses/
- https://aws.amazon.com/about-aws/whats-new/2023/04/aws-iot-core-mqtt5-shared-subscriptions-cloudwatch-metrics
- https://learn.microsoft.com/en-my/azure/iot/iot-mqtt-5-preview
- https://www.techzine.eu/news/infrastructure/86481/google-cloud-discontinues-iot-core/
- https://www.emqx.com/en/blog/mqtt5-request-response
- https://newsroom.eclipse.org/node/39823
- https://flowfuse.com/blog/2026/06/mqtt-vs-sparkplug-b
- https://www.hivemq.com/blog/streaming-iot-data-and-mqtt-messages-to-apache-kafka/
- https://openems.github.io/openems.io/javadoc/io/openems/backend/edgewebsocket/EdgeWebsocketImpl.html
- https://access.crunchydata.com/documentation/postgresql16/16.0/sql-notify.html
- https://thingsboard.io/docs/mqtt-broker/user-guide/mqtt-over-ws/
