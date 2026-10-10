# 16 — Đánh giá simulator mã mở bằng chạy thử (hands-on)

[← Mục lục](index.html) · [15 Mô phỏng](15-simulators-and-messaging.md) · [07 Tích hợp](07-device-integration.md)

- Phiên bản 1 · Ngày 2026-10-10 · Trạng thái: kết quả lab, đầu vào cho bước dựng hạ tầng (docker-compose: broker, DB, simulator, edge bridge).
- Câu hỏi: *"Có dựng được thiết bị mô phỏng từ mã nguồn mở không, và dùng những mảnh nào?"*
- Khác [15](15-simulators-and-messaging.md)/[E2](notes/E2-simulators-messaging.md) (chỉ đọc snippet tìm kiếm): lần này **clone repo, đọc file LICENSE, `git log -1`, chạy và nói chuyện bằng giao thức thật**. Lệnh, đầu ra và lỗi đầy đủ: [notes/E3-simulator-handson.md](notes/E3-simulator-handson.md).
- Nhãn: `[FACT]` = quan sát khi chạy hoặc đọc code/LICENSE trong phiên này; `[INFERENCE]` = suy luận; `[PROPOSAL]` = đề xuất; `[UNKNOWN]` = chưa kiểm được.
- Quy ước dấu và đơn vị theo [05](05-domain-model.html) / [07 §7.2](07-device-integration.md#72-mã-điểm-đơn-vị-dấu): lưới + = nhập, ESS + = xả, PV ≥ 0; raw W, Wh.

## Mục lục

1. [Tóm tắt](#1-tóm-tắt)
2. [Bảng đánh giá](#2-bảng-đánh-giá)
3. [Ghi chú theo công cụ](#3-ghi-chú-theo-công-cụ)
4. [Khoảng trống: register map theo hãng](#4-khoảng-trống-register-map-theo-hãng)
5. [Stack simulator đề xuất](#5-stack-simulator-đề-xuất)
6. [Phần phải tự viết cho "virtual site"](#6-phần-phải-tự-viết-cho-virtual-site)
7. [Hệ quả giấy phép](#7-hệ-quả-giấy-phép)
8. [Mô phỏng không chứng minh được gì](#8-mô-phỏng-không-chứng-minh-được-gì)
9. [Sửa so với 15/E2 và câu hỏi mở](#9-sửa-so-với-15e2-và-câu-hỏi-mở)

---

## 1. Tóm tắt

**Trả lời: dựng được một phần — khung giao thức có sẵn và chạy tốt, nhưng "thiết bị" (register map của hãng + hành vi) phải tự viết.**

| Mảng | Có sẵn và đã chạy được | Phải tự làm |
|---|---|---|
| Modbus TCP server | **pymodbus 3.15 API `SimDevice`/`SimData`** với hook `action` — PoC 127 dòng đã chạy PV + BESS + công tơ POC, ghi setpoint làm đổi SOC và P lưới, tiêm exception 06 và giá trị đóng băng `[FACT]` | Lớp mã hóa từ register map YAML của ta (word order CDAB, scale, dấu, sentinel), REST tiêm lỗi, mô hình vật lý |
| SunSpec | **pysunspec2 + model JSON (Apache-2.0)** sinh ảnh thanh ghi; pymodbus phục vụ; pysunspec2 scan lại thấy model 1, 701–713 và ghi được 704 `[FACT]` | Bộ sinh ảnh SunSpec gắn với mô hình sống (cập nhật 701/713 theo thời gian) |
| BESS/PV/công tơ "có hành vi" | **dertwin (MIT, alpha)** chạy được trong Docker: BESS phản hồi setpoint, công tơ cân bằng theo BESS `[FACT]` | Hoặc fork + nâng cấp dertwin, hoặc viết riêng; cả hai đều cần tiêm lỗi và map của ta |
| Thiết bị Huawei / Sungrow / tủ BESS Trung Quốc | **Không có emulator nào** (tìm lại lần hai, vẫn không thấy) | Viết map từ tài liệu hãng; đối chiếu với thư viện cộng đồng giấy phép mở (§4) |
| Sạc EV (OCPP) | **SAP simulator (Apache-2.0)**: OCPP 1.6 đủ luồng (ATG, SetChargingProfile Accepted), 2.0.1 boot/transaction — nhưng **2.0.1 không có SetChargingProfile** `[FACT]`. **`ocpp` (MIT)** viết CSMS/CP nhỏ trong ~120 dòng. **CitrineOS** chạy làm CSMS đối chứng 1.6 + 2.0.1 `[FACT]` | CP ảo 2.0.1 có smart charging + quirk (dùng `ocpp`); nối công suất EV vào cân bằng POC |
| IEC 104 | **c104 (GPL-3.0)** chạy server/client, interrogation và setpoint `C_SE_NC_1` `[FACT]` | Kịch bản master điều độ; chỉ dùng trong công cụ test |
| Profile PV | **pvlib (BSD-3)** sinh ngày 1 phút cho TP.HCM offline `[FACT]` | Mô hình mây; dữ liệu PVGIS cần mạng (bị chặn trong lab) |
| Mô hình EMS tham chiếu | **OpenEMS Edge** chạy trong Docker với `Simulator.*`, REST và Modbus API `[FACT]` | Chỉ dùng nếu ADR-07 chọn OpenEMS; **không** thay được simulator thiết bị |

Kết luận `[PROPOSAL]`: viết **"virtual site" riêng bằng Python trên pymodbus 3.15 `SimDevice`** (không dùng simulator JSON/REST cũ của pymodbus), dùng pysunspec2 cho phần SunSpec, pvlib sinh profile, SAP simulator + CP tự viết bằng `ocpp` cho EV, c104 cho 104. dertwin là ứng viên fork; quyết định sau một spike 2 ngày (§6).

## 2. Bảng đánh giá

Cột "Trung thực": **R** = chỉ register map, **B** = có hành vi (phản ứng lệnh/ràng buộc), **P** = mô hình vật lý. "Chạy được?": ✅ chạy và nói giao thức thật · ⚠️ chạy nhưng có lỗi/giới hạn chặn · 📖 chỉ đọc code · ❌ không chạy được. Giấy phép đọc từ file LICENSE/COPYING trong repo (hoặc `dist-info/licenses` của gói PyPI). Công sức chỉnh sửa là `[INFERENCE]`.

| Công cụ | Repo | Giấy phép | Commit cuối | Ngôn ngữ | Giao thức | Mô phỏng gì | Trung thực | Chạy được? | Công sức chỉnh | Kết luận |
|---|---|---|---|---|---|---|---|---|---|---|
| pymodbus 3.15 `SimDevice` + server | https://github.com/pymodbus-dev/pymodbus | BSD-3-Clause | 2026-10-09 (dev 4.0.0dev14; PyPI 3.15.0) | Python | Modbus TCP/RTU/TLS | Server + datastore + hook | R → B (tự viết hook) | ✅ | Trung bình (lớp map + mô hình) | **ADOPT** (nền virtual site) |
| pymodbus simulator cũ (JSON + REST, `pymodbus.simulator`) | như trên | BSD-3-Clause | như trên | Python | Modbus TCP + HTTP | Datastore phẳng, action increment/random | R | ⚠️ 3 lỗi: ghi FC16 vào kiểu 32-bit bị từ chối; tham số `min/max` sai tên; REST tiêm lỗi không tác dụng; đã báo deprecated | — | **REJECT** (bị bỏ ở v4) |
| pymodbus client | như trên | BSD-3-Clause | như trên | Python | Modbus | Client kiểm tra | — | ✅ | Thấp | **ADOPT** (công cụ test) |
| dertwin 0.1.12 | https://github.com/AlexSpivak/dertwin | MIT | 2026-06-11 | Python | Modbus TCP/RTU | BESS, PV, CHP, công tơ, lưới; YAML map | B/P | ✅ (Docker) | Trung bình–cao: nâng pymodbus `<3.13` → 3.15/4, thêm tiêm lỗi, map của ta, int64 Wh | **ADAPT** (ứng viên fork) |
| sdm630-emulator-pymodbus | https://github.com/aloishockenschlohe/sdm630-emulator-pymodbus | **Không có LICENSE** | 2025-05-17 | Python | Modbus RTU | Công tơ SDM630 | R | 📖 | — | **REJECT** (không có quyền dùng) |
| modbus-simulator-cli | https://github.com/paulorb/modbus-simulator-cli | **Không có LICENSE** | 2026-03-09 | Kotlin | Modbus TCP | Server có script | R/B | 📖 | — | **REJECT** |
| ModbusSim | https://github.com/emdem/ModbusSim | GPL-3.0 | 2016-10-27 | Python | Modbus TCP/RTU + REST | Server chung | R | 📖 | — | **REJECT** (bỏ hoang) |
| digitalpetri modbus 2.1.6 | https://github.com/digitalpetri/modbus | EPL-2.0 | 2026-10-05 | Java 17 | Modbus TCP/TLS/RTU | Client + server `ProcessImage` | R (tự viết) | ✅ | Trung bình | **ADOPT** cho driver edge (Java); phương án B cho simulator |
| j2mod 3.4.0 | https://github.com/steveohara/j2mod | Apache-2.0 | 2026-09-06 | Java | Modbus TCP/RTU | Master/slave | R | 📖 | Trung bình | **REFERENCE** |
| pysunspec2 1.3.6 | https://github.com/sunspec/pysunspec2 | Apache-2.0 | 2026-09-16 | Python | SunSpec/Modbus | Client + ảnh thiết bị JSON; `get_mb()` tuần tự hóa | — (client) / R (ảnh) | ✅ (kết hợp pymodbus) | Thấp | **ADOPT** (sinh ảnh + kiểm tra) |
| SunSpec models | https://github.com/sunspec/models | Apache-2.0 | 2026-08-20 | JSON | — | 114 model JSON (theo gói pysunspec2) | — | ✅ (qua pysunspec2) | Thấp | **ADOPT** (nguồn định nghĩa) |
| emdem/sunspec-sim | https://github.com/emdem/sunspec-sim | MIT | **2016-06-23** | Python | SunSpec/Modbus | Slave SunSpec | R | 📖 | — | **REJECT** (cũ 10 năm, không có model 7xx) |
| sunspec-device | https://github.com/nielsbasjes/sunspec-device | Apache-2.0 | 2026-10-08 | Java | SunSpec | Sinh schema từ model | — | 📖 | — | **REFERENCE** (nếu làm SunSpec phía Java) |
| OpenEMS Edge (`Simulator.*`, REST, Modbus API) | https://github.com/OpenEMS/openems | EPL-2.0 (Edge/Backend), AGPL-3.0 (UI) | 2026-10-06 | Java/OSGi | REST/JSON-RPC, Modbus TCP API riêng | ESS, công tơ, PV, EVCS ảo **trong** Edge | B | ✅ (Docker Hub) | Cao nếu dùng làm simulator | **REFERENCE** (ADOPT chỉ khi ADR-07 chọn OpenEMS) |
| venus-docker | https://github.com/victronenergy/venus-docker | MIT | 2026-05-04 | Python/shell | D-Bus playback + MQTT | Hệ Victron ghi sẵn | R (phát lại) | 📖 | — | **REFERENCE** (chỉ khi làm Victron) |
| SAP e-mobility-charging-stations-simulator 4.12.0 | https://github.com/SAP/e-mobility-charging-stations-simulator | Apache-2.0 | 2026-10-09 | Node.js/TS | OCPP-J 1.6, 2.0.1 | Nhiều trạm, ATG, meter values | B | ✅ | Thấp (1.6); 2.0.1 thiếu smart charging | **ADOPT** (tải OCPP, CI) |
| `ocpp` 2.1.0 (Mobility House) | https://github.com/mobilityhouse/ocpp | MIT | 2026-10-04 | Python | OCPP 1.6, 2.0.1, 2.1 | Thư viện CP/CSMS | — | ✅ | Thấp | **ADOPT** (CSMS stub, CP có quirk) |
| CitrineOS 2.0.1 | https://github.com/citrineos/citrineos-core | Apache-2.0 | 2026-10-06 | TypeScript | OCPP 1.6, 2.0.1, 2.1 | CSMS đầy đủ (Postgres + RabbitMQ) | — | ✅ (build từ nguồn) | Trung bình (stack nặng) | **REFERENCE** (CSMS đối chứng lab) |
| SteVe | https://github.com/steve-community/steve | GPL-3.0 | 2026-09-28 | Java | OCPP 1.2–1.6 (gồm 1.6J Security Extensions) | CSMS | — | 📖 | — | **REFERENCE** (lab 1.6) |
| EVerest everest-core | https://github.com/EVerest/everest-core | Apache-2.0 | 2026-10-09 | C++ | OCPP 1.6/2.0.1, ISO 15118 | Firmware trạm sạc + SIL | B/P | 📖 (không build) | Cao | **REFERENCE** (HIL P2) |
| Monta ocpp-emulator | https://github.com/monta-app/ocpp-emulator | Apache-2.0 | 2026-09-30 | Kotlin | OCPP | Emulator desktop | B | 📖 | — | **REFERENCE** (test tay) |
| MicroOcpp | https://github.com/matth-x/MicroOcpp | MIT | 2025-12-04 | C++ | OCPP | Thư viện firmware | — | 📖 | — | **REFERENCE** |
| scriptable-ocpp-chargepoint-simulator | https://github.com/oglimmer/scriptable-ocpp-chargepoint-simulator | Apache-2.0 | **2021-07-24** | Node.js | OCPP 1.6 | CP có script | B | 📖 | — | **REJECT** (bỏ hoang) |
| c104 2.2.1 | https://github.com/Fraunhofer-FIT-DIEN/iec104-python | GPL-3.0 | 2026-08-06 | Python (C++ lib60870) | IEC 104 | Server/client 104 | B (callback) | ✅ | Thấp | **ADOPT — chỉ công cụ test** |
| lib60870 | https://github.com/mz-automation/lib60870 | GPL-3.0 (hoặc thương mại) | 2026-07-15 | C | IEC 104/101 | Thư viện | — | 📖 | — | **REFERENCE** (license thương mại nếu nhúng edge) |
| pvlib 0.16.1 | https://github.com/pvlib/pvlib-python | BSD-3-Clause | 2026-10-08 | Python | — | Bức xạ, công suất PV | P | ✅ | Thấp | **ADOPT** (sinh profile) |
| pandapower 3.5.6 | (PyPI) | BSD-3-Clause | — | Python | — | Power flow | P | ✅ | — | **REJECT cho MVP** (thừa với một POC) |
| PyBaMM 26.10.0 | (PyPI) | BSD-3-Clause | — | Python | — | Điện hóa cell | P | ✅ | — | **REJECT cho virtual site** (bucket model đủ) |
| huawei-solar-lib | https://github.com/wlcrs/huawei-solar-lib | **AGPL-3.0** | 2026-08-21 | Python | Modbus (client) | Map Huawei (~800 định nghĩa) | — | 📖 | — | **REFERENCE** (không chép mã) |
| sun2000_modbus | https://github.com/olivergregorius/sun2000_modbus | MIT | 2026-01-04 | Python | Modbus (client) | ~340 thanh ghi Huawei | — | 📖 | — | **REFERENCE** (đối chiếu map, dùng được) |
| Sungrow-SHx HA YAML | https://github.com/mkaiser/Sungrow-SHx-Inverter-Modbus-Home-Assistant | MIT | 2026-09-06 | YAML | Modbus (client) | ~230 thanh ghi Sungrow SHx | — | 📖 | — | **REFERENCE** (đối chiếu map) |
| SunGather | https://github.com/bohdan-s/SunGather | GPL-3.0 | 2025-06-24 | Python/YAML | Modbus (client) | ~270 thanh ghi Sungrow | — | 📖 | — | **REFERENCE** (không chép) |

Không kiểm được: `energywebfoundation/ew_der_modbus_sim_py` (không clone được; snippet ghi GPLv3) và `openmuc/j60870` (không có trên GitHub dưới tên này) → `[UNKNOWN]`. `virtual-ems` (Gitee, Go, PCS + BMS) chỉ thấy qua tìm kiếm → `[UNKNOWN]`.

## 3. Ghi chú theo công cụ

### 3.1 pymodbus — dùng API mới, bỏ simulator cũ

- `[FACT]` Simulator JSON/REST (`pymodbus.simulator`, `ModbusSimulatorContext`) in cảnh báo *"deprecated and will be removed in v4"*. Nhánh dev đã là `4.0.0dev14`.
- `[FACT]` Ba lỗi khi chạy 3.15.0: (1) ghi FC16 vào `float32`/`uint32` bị exception 02 khi `"type exception": true` (code gọi `validate` từng thanh ghi với `count=1`); (2) tài liệu ghi `"parameters": {"min","max"}` nhưng hàm nhận `minval/maxval` → client nhận exception 04; (3) REST `restapi/calls → Simulate` (lỗi, trễ, rác) trả "ACTIVE" nhưng **không ảnh hưởng phản hồi**. Simulator cũ chỉ có kiểu không dấu, word order cố định ABCD.
- `[FACT]` API mới `SimDevice(id, simdata=[SimData(...)], action=hook)` được `ModbusTcpServer` nhận trực tiếp; có INT16…FLOAT64, STRING, BITS, `readonly`. Hook được gọi trước mỗi request, sửa thanh ghi tại chỗ, nhận giá trị ghi, trả `ExcCodes` → **đủ cho mô hình động và tiêm exception**. Module vẫn ghi "experimental". Không có tùy chọn word order → lớp mã hóa của ta tự đảo CDAB và ghi qua `DataType.REGISTERS`.
- `[FACT]` PoC virtual site (E3 §3): ghi `ess p_set = +200 kW` → 3 s thật (180 s mô phỏng) sau `ess.p = 200 kW`, SOC 50,0 → 47,8 %, `meter.p` từ +18 kW sang −187 kW, `e_export` tăng; ghi `p_limit_pct = 50` → PV giảm một nửa; sạc 250 kW → `meter.p = +405 kW`; ghi vào thanh ghi chỉ đọc → exception 02; `fault=1` → exception 06; `fault=2` → giá trị đóng băng.
- `[FACT]` pymodbus trả **exception 04** cho unit ID không tồn tại; digitalpetri **im lặng** (client timeout). Thiết bị/gateway thật khác nhau `[INFERENCE]` → virtual site phải cấu hình được hành vi này (để kiểm `BAD_COMM` và `BAD_CONFIG` ở 07 §5.1.5).
- Rủi ro: R-15-07 (đổi API trước v4) **đã xảy ra** với simulator cũ; API mới còn "experimental" → khóa `pymodbus==3.15.*`, bọc sau một lớp adapter mỏng, có test nâng cấp `[PROPOSAL]`.

### 3.2 dertwin — ứng viên fork

- `[FACT]` MIT, 0.1.12 "Alpha", một tác giả, ~15.000 dòng. Register map YAML có `address/func/type/count/scale/unit/direction/endian` — rất gần schema 07 §6.2. Có BESS (battery + inverter + controller, ramp), PV theo irradiance, CHP, công tơ, mô hình tần số/điện áp có seed, RTU qua socat, Dockerfile, sinh docker-compose.
- `[FACT]` Chạy `full_site_config.json` trong `python:3.12-slim`: bật nguồn (10055 = 1), remote (10057 = 1), setpoint −30 kW (10126, int32, scale 0,1 kW) → `active_power = −30`, SOC 60,0 → 60,1, công tơ tăng 10 kW/pha.
- `[FACT]` Hạn chế: ghim `pymodbus>=3.8,<3.13`, dùng `ModbusServerContext` (bị bỏ ở v4); không có tiêm lỗi; map không gắn với hãng thật nào; không thấy watchdog setpoint hay bộ đếm int64.
- Kết luận `[PROPOSAL]`: spike 2 ngày — fork dertwin, thay tầng server bằng `SimDevice`, nạp map YAML của ta. Nếu spike vướng, giữ PoC tự viết (E3 §3) và chỉ lấy ý tưởng mô hình từ dertwin (MIT cho phép chép có ghi công).

### 3.3 SunSpec

- `[FACT]` pysunspec2 **không có server**, nhưng `Device.get_mb()` tuần tự hóa model → ghép `"SunS"` + model + `0xFFFF 0` → pymodbus phục vụ. pysunspec2 scan lại: base 40000, model 1, 701–713; đọc `701.W` raw 12346 × 10^1; ghi `704.WMaxLimPctEna=1, WMaxLimPct=50` (FC16 tại 40310).
- `[FACT]` Bẫy: W là int16 → giá trị > 32,7 kW cần SF ≥ 1 (lượng tử hóa 123456 → 123460); thiếu model kết thúc làm scan lỗi; SF `None` trong ảnh mẫu làm ghi `cvalue` lỗi.
- `[PROPOSAL]` Dùng pysunspec2 theo hai vai: (a) **sinh ảnh** thanh ghi SunSpec cho thiết bị ảo; (b) **bộ kiểm tra độc lập** — driver SunSpec của edge (Java) và pysunspec2 phải đọc ra cùng giá trị trên cùng ảnh. Vai (b) giảm một phần rủi ro "cùng lỗi hai phía" (R-15-01) cho phần SunSpec.

### 3.4 OpenEMS Edge

- `[FACT]` `openems/edge:latest` chạy được; cấu hình bằng POST tới Felix configMgr. REST (8084) đọc/ghi channel; ghi `ess0/SetActivePowerEquals = 3000` → `_sum/GridActivePower = −3000`. Quy ước dấu của OpenEMS trùng 05.
- `[FACT]` Modbus TCP API của OpenEMS chỉ xuất `_meta` và `_sum` theo **bảng của OpenEMS** (ví dụ `_sum/GridActivePower` ref 315 float32). Component `Simulator.*` không có trong bảng. Profile dựng sẵn chỉ là 5 CSV hộ gia đình H0.
- `[INFERENCE]` Xác nhận F2-06: simulator OpenEMS kiểm được **controller** (nếu ta chạy controller trong OpenEMS), **không** đóng vai thiết bị Huawei/Sungrow/BESS cho driver của ta.

### 3.5 OCPP

- `[FACT]` SAP simulator (build bằng pnpm trong `node:22-alpine`): OCPP 1.6 chạy đủ Boot → Status → Authorize → StartTransaction → MeterValues → StopTransaction với ATG; `SetChargingProfile` 16 A được **Accepted**. OCPP 2.0.1: Boot, StatusNotification, `RequestStartTransaction` Accepted, `TransactionEvent` Started/Updated có `Power.Active.Import`; `SetChargingProfile` → **CALLERROR NotImplemented**. README liệt kê khối 2.0.x A–P nhưng **không có K (SmartCharging)**.
- `[FACT]` Bẫy: `supervisionUrls` trong station template đè cấu hình chung.
- `[FACT]` `ocpp` 2.1.0 có `v16`, `v201`, `v21`. CSMS mini (~120 dòng) phục vụ cả 1.6 và 2.0.1 bằng chọn subprotocol. Bẫy: không đặt tên handler trùng phương thức của `ChargePoint` (ví dụ `start`).
- `[FACT]` CitrineOS: image ghcr không tải được trong lab; build từ nguồn cần **Node ≥ 24.16**; chạy với PostGIS 16 + RabbitMQ 3 (Hasura tùy chọn); cổng OCPP 8081 khai báo `ocpp2.1, ocpp2.0.1, ocpp1.6`. Hai trạm SAP (1.6, 2.0.1) Boot **Accepted**; tag chưa đăng ký → Authorize `Invalid`. Image build 2,37 GB.
- `[FACT]` SteVe README nay ghi hỗ trợ 1.6J **gồm Security Extensions** (không chạy thử).
- `[PROPOSAL]` Smart charging 2.0.1 (giới hạn công suất theo POC) — đúng phần EMS cần — **không có simulator mã mở nào đã kiểm chạy được** → viết CP ảo 2.0.1 bằng `ocpp` (hỗ trợ `SetChargingProfile`, báo công suất vào virtual site, có hồ sơ quirk).

### 3.6 IEC 104

- `[FACT]` c104 2.2.1 có wheel Python 3.13; server CA 47 + client: interrogation trả −123,4; setpoint `C_SE_NC_1` 800 tới server. Callback cần chú thích kiểu đúng chữ ký.
- GPL-3.0 → chỉ trong container test, không vào image edge (R-15-05).

### 3.7 Profile PV, lưới, pin

- `[FACT]` pvlib: ngày 2026-03-15, 500 kWp, tilt 10°, DC/AC 1,2, clear-sky → đỉnh 400 kW (kẹp), 3.000 kWh (6,0 kWh/kWp — trần không mây). PVGIS bị chặn trong lab → **sinh profile một lần, commit CSV** (như 15 đã đề xuất).
- `[FACT]` pandapower runpp 52 ms, PyBaMM SPM 0,2 s: chạy được nhưng không cần cho virtual site một POC. Lưu ý pandapower: `storage.p_mw > 0` = sạc — **ngược dấu** ESS của ta.

## 4. Khoảng trống: register map theo hãng

**Không có emulator nào cho Huawei SUN2000/SmartLogger, Sungrow, hay bộ điều khiển BESS/PCS Trung Quốc** (tìm lại: "huawei sun2000 modbus emulator", "sungrow modbus simulator", "battery storage modbus simulator", "SDM630 emulator"). Nguồn map hiện có đều là **client** cộng đồng:

| Hãng/thiết bị | Nguồn | Giấy phép (từ LICENSE) | Kích thước | Được dùng thế nào |
|---|---|---|---|---|
| Huawei SUN2000 + LUNA2000 + công tơ qua inverter | wlcrs/huawei-solar-lib | **AGPL-3.0** | ~800 định nghĩa (`registers.py`) | **Chỉ đọc tham khảo**; không chép mã/bảng vào repo của ta |
| Huawei SUN2000 | olivergregorius/sun2000_modbus | MIT | ~340 `Register(...)` (có 32080 `ActivePower` INT32_BE W, 37113 công tơ, 47075, 47100 điều khiển pin) | Đối chiếu được; ghi `evidence: COMMUNITY` |
| Sungrow SHx (hybrid) | mkaiser/Sungrow-SHx… (YAML Home Assistant) | MIT | ~230 khối `address:` | Đối chiếu được; `COMMUNITY` |
| Sungrow | bohdan-s/SunGather | GPL-3.0 | ~270 địa chỉ | Chỉ tham khảo |
| Eastron SDM630 | sdm630-emulator-pymodbus | Không có giấy phép | — | Không dùng; viết từ tài liệu Eastron |
| BESS/PCS (tủ Trung Quốc) | Không có (virtual-ems trên Gitee chưa kiểm) | — | — | Viết từ tài liệu hãng khi có NDA/tài liệu |
| Giao thức chuẩn | SunSpec models | Apache-2.0 | 114 model | **Dùng trực tiếp** (sinh ảnh + kiểm tra) |

`[INFERENCE]` Địa chỉ thanh ghi là dữ kiện lấy từ tài liệu hãng; giấy phép của thư viện cộng đồng chi phối việc **chép mã/văn bản**, không biến địa chỉ thành của họ. Tuy vậy, map của ta phải được viết **từ tài liệu hãng** (`evidence: VENDOR_DOC`), thư viện cộng đồng chỉ để đối chiếu (`COMMUNITY`), và không được chép cấu trúc/chú thích từ nguồn AGPL/GPL. Cần ý kiến pháp lý một lần cho nguyên tắc này (Q-16-03).

## 5. Stack simulator đề xuất

`[PROPOSAL]` — cập nhật 15 §2.1 bằng thứ đã chạy được.

| Môi trường | Thiết bị Modbus/SunSpec | EV/OCPP | Điều độ | Mạng/khác |
|---|---|---|---|---|
| **(a) Laptop** | 1–3 container `vsite` (Python 3.13, pymodbus 3.15 `SimDevice`, mô hình §6, profile CSV pvlib); pymodbus REPL/client để thử tay | SAP simulator (1.6, nhiều trạm) **hoặc** `vsite-evse` (CP 2.0.1 tự viết bằng `ocpp`) trỏ vào CSMS của edge | — | Mosquitto 2.x; Toxiproxy |
| **(b) CI** | `vsite` với seed + đồng hồ ×60; pysunspec2 kiểm chéo ảnh SunSpec; ma trận lỗi đêm | SAP (1.6, smart charging) + `vsite-evse` (2.0.1); CSMS stub bằng `ocpp` để kiểm CP | c104 master (P1) | Testcontainers; Toxiproxy |
| **(c) HIL lab** | Thiết bị thật + `vsite` bù phần thiếu trên OT LAN; RTU qua USB-RS485 (pymodbus serial) | Charger thật + CitrineOS (2.0.1) hoặc SteVe (1.6) làm CSMS đối chứng; EVerest SIL tùy chọn (P2) | c104 / lib60870 | netem/Toxiproxy cho 4G |
| **(d) Demo** | `vsite` phát lại ngày điển hình, đồng hồ thật, reset đêm | `vsite-evse` | — | Nhãn "Mô phỏng"; không route tới edge thật |

Không đưa vào stack: simulator JSON/REST cũ của pymodbus, OpenEMS (trừ khi ADR-07 chọn), các repo không có giấy phép, repo bỏ hoang.

## 6. Phần phải tự viết cho "virtual site"

Ước lượng là `[INFERENCE]` cho một kỹ sư quen Python/Modbus.

| # | Thành phần | Nội dung | Dựa trên | Ước lượng |
|---|---|---|---|---|
| V1 | `vsite-core` (đồng hồ + mô hình) | Đồng hồ kịch bản (seed, ×1/×10/×60, Asia/Ho_Chi_Minh); PV (CSV pvlib × `p_limit_pct`, ramp, mây); tải (profile + bước); BESS (SOC có η, CCL/DCL taper, τ, ramp, watchdog có/không); công tơ POC `P_grid = P_load − P_pv − P_bess + P_evse`; bộ đếm int64 Wh có `R_wrap` | PoC E3 §3; ý tưởng dertwin | 4–6 ngày |
| V2 | Lớp mã hóa register map | Nạp **chính YAML driver** (07 §6.2): `type`, `word_order` (CDAB), `scale` hằng hoặc SF, `sign_transform` ngược, `na_values`, `access`, `fc`; sinh `SimData` + hook; chế độ "map lệch" cố ý | pymodbus `SimDevice` | 3–4 ngày |
| V3 | Hồ sơ thiết bị | (a) SunSpec inverter 1 + 701 + 704 (+ 713 nếu có pin) qua pysunspec2, cập nhật động; (b) "Huawei-like" và "Sungrow-like" viết từ tài liệu hãng; (c) BESS PCS/BMS chung (setpoint, mode, SOC, CCL/DCL, alarm word); (d) công tơ POC kiểu SDM/SunSpec 20x | pysunspec2, tài liệu hãng | 1–2 ngày mỗi hồ sơ |
| V4 | Tiêm lỗi + REST điều khiển | Exception 01/02/03/04/06 theo thanh ghi; đóng băng; ngắt TCP; **một client duy nhất**; unit lạ im lặng/exception; reset bộ đếm; CT ngược; "ghi chấp nhận nhưng không tác dụng"; kẹp BMS; lệch đồng hồ thiết bị; REST/JSON để CI điều khiển | hook `action` | 3 ngày |
| V5 | `vsite-evse` (CP ảo OCPP) | CP 2.0.1 (và 1.6) bằng `ocpp`: Boot, Status, TransactionEvent, **SetChargingProfile/ClearChargingProfile tác động thật vào công suất**, báo `P_evse` cho V1; hồ sơ quirk (bỏ qua profile, chỉ nhận A, `min_a`) | `ocpp` 2.1.0 | 3–4 ngày |
| V6 | Kịch bản + vector vàng | File kịch bản (ngày nắng/mây, vượt trần nhập, mất mạng); vector vàng từ thiết bị thật làm điều kiện để map được dùng | — | liên tục |
| V7 | Đóng gói | Dockerfile, healthcheck, metrics; mỗi site một container, mỗi thiết bị một cổng hoặc unit ID theo cấu hình | — | 1 ngày |

Ngoài virtual site (để bước hạ tầng khỏi quên): edge bridge Modbus → MQTT 5 theo 07 §7; CSMS cục bộ ở edge nếu edge điều khiển charger trực tiếp (chưa quyết, 07 §5.9); "edge ảo" phát payload cho test tải (15 §4); master 104 giả (c104, P1).

## 7. Hệ quả giấy phép

| Nhóm | Giấy phép | Được nhúng vào sản phẩm (edge/cloud)? | Dùng trong công cụ test/demo? |
|---|---|---|---|
| pymodbus, pvlib, pandapower, PyBaMM | BSD-3-Clause | Có (giữ thông báo) | Có |
| pysunspec2, SunSpec models, SAP simulator, CitrineOS, j2mod, EVerest, Monta | Apache-2.0 | Có (giữ NOTICE) | Có |
| `ocpp`, dertwin, sun2000_modbus, Sungrow-SHx YAML, venus-docker, MicroOcpp | MIT | Có | Có |
| digitalpetri modbus, OpenEMS Edge/Backend | EPL-2.0 | Có, nhưng sửa file EPL phải công bố file đó `[INFERENCE]` | Có |
| c104, lib60870, SteVe, SunGather, ModbusSim | GPL-3.0 | **Không** nếu edge/cloud đóng (hoặc mua license thương mại lib60870) | Có, trong container riêng, không phân phối kèm sản phẩm |
| huawei-solar-lib, OpenEMS UI | AGPL-3.0 | **Không** | Chỉ đọc tham khảo |
| sdm630-emulator, modbus-simulator-cli | Không có giấy phép | **Không** | **Không** |

`[PROPOSAL]` Virtual site là công cụ test nhưng **demo bán hàng chạy trên cloud của ta** → chỉ dùng thành phần BSD/Apache/MIT/EPL trong image `vsite`; GPL (c104) chỉ trong image CI riêng. Thêm quét SBOM/giấy phép trong CI (R-15-05).

## 8. Mô phỏng không chứng minh được gì

Giữ nguyên 15 §4.3, bổ sung từ lab:

| Không chứng minh | Bằng chứng từ lab |
|---|---|
| Register map đúng với thiết bị thật | Mọi map đã chạy (dertwin, PoC, OpenEMS) là map **tự đặt**; không có emulator hãng `[FACT]` |
| Hành vi lỗi của thiết bị thật | Hai stack chỉ khác nhau đã cho hai hành vi unit lạ (exception 04 vs im lặng) `[FACT]`; thiết bị thật có thể khác cả hai |
| Smart charging 2.0.1 trên charger thật | Simulator mã mở phổ biến nhất không cài SetChargingProfile 2.0.1 `[FACT]`; CP tự viết chỉ chứng minh logic của ta |
| Sản lượng/kinh tế | Profile pvlib là clear-sky (6,0 kWh/kWp) `[FACT]`; không có dữ liệu mây/tải VN |
| Thời gian đáp ứng, RTU, 4G | Lab chỉ chạy TCP loopback |
| Đúng tiêu chuẩn | Không công cụ nào trong lab là test tool chứng nhận (OCA, SunSpec) |

## 9. Sửa so với 15/E2 và câu hỏi mở

Dữ kiện mới trái hoặc bổ sung 15/E2 (người viết 15 quyết định cập nhật; tài liệu này không sửa file khác):

| Chỗ trong 15/E2 | Ghi cũ | Quan sát E3 |
|---|---|---|
| 15 §2.2 dòng pymodbus | "Dùng server API, khóa phiên bản"; 3.14.0 | Đúng hướng; PyPI 3.15.0; simulator cũ **đã báo deprecated + có lỗi**; API `SimDevice` dùng được ngay `[FACT]` |
| 15 §2.2 SAP | "Hỗ trợ 2.0.1 chưa xác minh" | 2.0.1 chạy được, **thiếu SmartCharging** `[FACT]` |
| 15 §2.2 `ocpp` | "Không thấy 2.1" | Gói 2.1.0 có `ocpp/v21` `[FACT]` |
| 15 §2.2 CitrineOS | Giấy phép `[UNKNOWN]` | Apache-2.0; OCPP 1.6/2.0.1/2.1; cần Node ≥ 24.16 `[FACT]` |
| 15 §2.2 SteVe | "Chưa hỗ trợ Security Whitepaper" | README hiện ghi 1.6J gồm Security Extensions `[FACT]` |
| E2 §3.1 c104 | "Python < 3.13" | Wheel 2.2.1 chạy trên Python 3.13 `[FACT]` |
| 15 §2.2 emdem/sunspec-sim | "Simulator SunSpec mã mở duy nhất" | Commit cuối 2016 → loại; thay bằng pysunspec2 `get_mb()` + pymodbus `[FACT]` |
| 15 §2.2 digitalpetri | EPL-2.0 (thứ cấp) | EPL-2.0 xác nhận từ `LICENSE.md` `[FACT]` |
| 15 §2.2 pvlib | BSD-3 `[INFERENCE]` | BSD-3-Clause từ `LICENSE` `[FACT]` |
| Mới | — | dertwin (MIT) là simulator DER mã mở có hành vi, dùng được làm điểm xuất phát `[FACT]` |

Câu hỏi mở:

| ID | Câu hỏi | Chặn |
|---|---|---|
| Q-16-01 | Fork dertwin hay giữ virtual site tự viết? (spike 2 ngày) | V1–V2 |
| Q-16-02 | Edge có làm CSMS cục bộ cho charger không? Nếu có, CP ảo 2.0.1 (V5) là bắt buộc trước Gate tương ứng | V5, 07 §5.9 |
| Q-16-03 | Ý kiến pháp lý: viết map từ tài liệu hãng và đối chiếu với thư viện MIT/AGPL có an toàn không? | V3 |
| Q-16-04 | Lấy được tài liệu Modbus của tủ BESS/PCS mục tiêu (NDA) khi nào? | V3(c) |
| Q-16-05 | Nguồn profile mây và tải C&I VN (PVGIS bị chặn trong lab; cần chạy từ máy có mạng) | V1, demo |
| Q-16-06 | CitrineOS hay SteVe làm CSMS đối chứng ở HIL (2.0.1 vs 1.6 Security)? | HIL lab |

---

Liên kết PoC: hạ tầng chạy được (virtual site pymodbus `SimDevice` + pysunspec2, SAP simulator + CSMS `ocpp`, edge bridge PoC, Mosquitto MQTT 5, TimescaleDB) và kết quả chạy thử — [infra/README.md](../../../infra/README.md).
