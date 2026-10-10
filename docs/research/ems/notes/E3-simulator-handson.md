# E3 — Nhật ký lab: chạy thử simulator mã mở (hands-on)

[← Mục lục](../index.html) · [16 Đánh giá simulator](../16-simulator-evaluation.md) · [15 Mô phỏng](../15-simulators-and-messaging.md) · [E2](E2-simulators-messaging.md) · [07 Tích hợp](../07-device-integration.md)

- Người viết: Agent E3 (hands-on). Ngày: 2026-10-10. Trạng thái: nhật ký thô, đầu vào cho [16](../16-simulator-evaluation.md).
- Khác E2: E2 chỉ đọc snippet tìm kiếm. E3 **clone repo, đọc file LICENSE, `git log -1`, chạy và gọi giao thức thật**. Mọi `[FACT]` trong file này là quan sát trực tiếp trên máy lab (trừ khi ghi khác).
- Thư mục làm việc (tạm, sẽ mất khi hết phiên): `/tmp/claude-0/-home-user-admin/6aedd770-de72-529c-acf2-87df83aa2b49/scratchpad/simeval/` — `repos/` (mỗi repo một thư mục), `scripts/` (mã lab tự viết), `logs/`, `venv/`. Đoạn mã quan trọng được chép vào đây để không phụ thuộc thư mục tạm.
- Mã code tải về coi là **không tin cậy**: Python từ repo lạ (dertwin) chạy **trong Docker**; thư viện PyPI phổ biến (pymodbus, pysunspec2, ocpp, pvlib, c104, pandapower, pybamm) cài vào venv riêng, chạy với `python -I`.

---

## 0. Môi trường

| Thành phần | Phiên bản quan sát |
|---|---|
| Host | Linux 6.18, 4 vCPU, 15 GB RAM |
| Python / Node / Go | 3.13.16 / v22.22.0 / go1.24.7 |
| Java / Maven | có (JAVA_TOOL_OPTIONS cấu hình proxy) |
| Docker | 29.8.2 |

Sự cố môi trường [FACT]:

- Docker Hub trả **429** cho `python:3.12-slim` 3 lần liên tiếp; thử lại sau ~60 s thì được. `public.ecr.aws/docker/library/python` trả "Data limit exceeded"/403.
- **ghcr.io bị chặn ở bước tải blob** (`pkg-containers.githubusercontent.com … Forbidden`; `ghcr.io/openems/edge` trả `unauthorized`). Hệ quả: OpenEMS lấy từ Docker Hub (`openems/edge:latest`), CitrineOS phải **build từ nguồn**.
- Container gọi PyPI/npm bị proxy MITM → lỗi `CERTIFICATE_VERIFY_FAILED`. Cách chạy được: mount CA của proxy `-v /root/.ccr/ca-bundle.crt:/ca.crt:ro -e PIP_CERT=/ca.crt -e SSL_CERT_FILE=/ca.crt` (Python) hoặc `-e NODE_EXTRA_CA_CERTS=/ca.crt -e npm_config_cafile=/ca.crt` (Node).
- API PVGIS (`re.jrc.ec.europa.eu`) bị proxy chặn (`ProxyError`) → chỉ sinh profile clear-sky offline.

## 1. Clone và giấy phép (đọc từ file LICENSE trong repo)

Lệnh: `git clone --depth 1 https://github.com/<owner>/<repo>` rồi `git log -1 --format='%cs %h'` và `head` file LICENSE/COPYING.

| Repo | Commit cuối | File giấy phép → giấy phép |
|---|---|---|
| pymodbus-dev/pymodbus | 2026-10-09 e33abee (nhánh dev = `4.0.0dev14`; PyPI mới nhất 3.15.0) | `LICENSE` → BSD 3 điều khoản ("Copyright 2008-2025 Pymodbus") |
| sunspec/models | 2026-08-20 90b4a33 | `LICENSE` → Apache-2.0 |
| sunspec/pysunspec2 | 2026-09-16 8606a88 (setup.py 1.3.6) | `LICENSE` → Apache-2.0 |
| emdem/sunspec-sim | **2016-06-23** a3023db | `LICENSE` → MIT |
| nielsbasjes/sunspec-device | 2026-10-08 da58783 | `LICENSE` → Apache-2.0 |
| AlexSpivak/dertwin | 2026-06-11 59b8ab0 (pyproject 0.1.12, "Alpha") | `LICENSE` → MIT |
| aloishockenschlohe/sdm630-emulator-pymodbus | 2025-05-17 ba549c9 | **không có file giấy phép** |
| paulorb/modbus-simulator-cli | 2026-03-09 944972f | **không có file giấy phép** |
| emdem/ModbusSim | 2016-10-27 5394bd7 | `LICENSE` → GPL-3.0 |
| wlcrs/huawei-solar-lib | 2026-08-21 19dfcfb | `LICENSE.md` → **AGPL-3.0** |
| olivergregorius/sun2000_modbus | 2026-01-04 1083939 | `LICENSE` → MIT |
| mkaiser/Sungrow-SHx-Inverter-Modbus-Home-Assistant | 2026-09-06 310635c | `LICENSE` → MIT |
| bohdan-s/SunGather | 2025-06-24 2c2935d | `LICENSE` → GPL-3.0 |
| victronenergy/venus-docker | 2026-05-04 7bd3b4f | `LICENSE` → MIT |
| victronenergy/velib_python | 2026-09-22 3368c07 | `LICENSE` → MIT |
| OpenEMS/openems | 2026-10-06 3240f7b (OpenemsConstants 2026.11.0-SNAPSHOT) | `LICENSE-EPL-2.0` + `LICENSE-AGPL-3.0`; README: Edge/Backend = EPL-2.0, UI = AGPL-3.0 |
| SAP/e-mobility-charging-stations-simulator | 2026-10-09 3c5b406 (package 4.12.0) | `LICENSE` + `LICENSES/Apache-2.0.txt` → Apache-2.0 |
| mobilityhouse/ocpp | 2026-10-04 b39291d (pyproject 2.1.0) | `LICENSE` → MIT |
| steve-community/steve | 2026-09-28 b067cb5 | `LICENSE.txt` → GPL-3.0 |
| citrineos/citrineos-core | 2026-10-06 1a83638 (package 2.0.1) | `LICENSE` + `LICENSES/Apache-2.0.txt` → Apache-2.0 |
| monta-app/ocpp-emulator | 2026-09-30 3f9837e | `LICENSE` → Apache-2.0 |
| matth-x/MicroOcpp | 2025-12-04 ee1271b | `LICENSE` → MIT |
| oglimmer/scriptable-ocpp-chargepoint-simulator | **2021-07-24** 091853a | `LICENSE` → Apache-2.0 |
| EVerest/everest-core | 2026-10-09 2e710bc (shallow 110 MB) | `LICENSE` → Apache-2.0 |
| Fraunhofer-FIT-DIEN/iec104-python (c104) | 2026-08-06 5c78d42 (pyproject 2.2.2; PyPI 2.2.1) | `LICENSE` → GPL-3.0 |
| mz-automation/lib60870 | 2026-07-15 7a388e3 | `COPYING` → GPL-3.0 |
| digitalpetri/modbus | 2026-10-05 efd826e (2.1.7-SNAPSHOT; release 2.1.6) | `LICENSE.md` → EPL-2.0 |
| steveohara/j2mod | 2026-09-06 d7861c9 (pom 3.4.0) | `LICENSE.txt` → Apache-2.0 |
| pvlib/pvlib-python | 2026-10-08 88fb562 (PyPI 0.16.1) | `LICENSE` → BSD-3-Clause |

Clone thất bại: `energywebfoundation/ew_der_modbus_sim_py` (không thấy repo dưới tên này; snippet tìm kiếm ghi GPLv3 — chưa kiểm), `openmuc/j60870` (không có trên GitHub dưới tên này) → `[UNKNOWN]`.

pandapower 3.5.6 và PyBaMM 26.10.0 kiểm qua `dist-info/licenses` sau `pip install`: cả hai BSD-3-Clause.

## 2. pymodbus 3.15.0 — simulator cũ (JSON + REST)

```bash
python3 -m venv venv/main
venv/main/bin/pip install "pymodbus[simulator]==3.15.0" pysunspec2==1.3.6 ocpp==2.1.0 websockets pvlib==0.16.1
venv/main/bin/pymodbus.simulator --json_file meter_sim.json --modbus_server server \
  --modbus_device meter --http_host 127.0.0.1 --http_port 8081 --log debug
```

`meter_sim.json` (rút gọn): server TCP `127.0.0.1:5020`; device có `float32` tại 0–1 (35120.5), `float32` 2–3 action `random`, `uint32` 20–21 action `increment`, 22–23 `uptime`, `uint16` 10, `string` 100–104, vùng ghi `"write": [[40, 41]]`.

Kết quả [FACT]:

1. Khởi động in cảnh báo: `ModbusSimulatorContext is deprecated and will be removed in v4. Please convert to SimData/SimDevice.` và tương tự cho `ModbusServerContext`.
2. Đọc `float32`/`uint32`/`string` bằng `ModbusTcpClient` đúng; `increment` tăng mỗi lần đọc (1001, 1002); `uptime` chạy.
3. **Lỗi 1 — tham số action:** docstring hướng dẫn `"parameters": {"min": …, "max": …}` nhưng hàm `action_random(…, minval, maxval)` → server log `TypeError: … unexpected keyword argument 'min'`, client nhận **exception 04**. Sửa: dùng `"minval"/"maxval"`.
4. **Lỗi 2 — ghi FC16 vào `float32`/`uint32` luôn bị từ chối (exception 02) khi `"type exception": true`.** Nguyên nhân đọc code: `async_OLD_setValues` gọi `validate(func_code, address)` với `count=1` cho từng thanh ghi; `loop_validate` trả False với kiểu 2 thanh ghi khi `i + 1 >= end_address`. Gọi `validate(16, 40, 2)` trực tiếp thì True. Cách tránh: `"type exception": false` → ghi `-150000.0` và đọc lại đúng.
5. REST `POST /restapi/registers` với `{"submit":"Set","register":"10","value":"2411",…}` → client đọc được 2411. Thiếu khóa `submit` → `{"result": "error", "error": "Unhandled error Error: 'submit'"}`.
6. **Lỗi 3 — REST tiêm lỗi không có tác dụng:** `POST /restapi/calls` `{"submit":"Simulate","response_type":"1","response_error":"6",…}` trả `"simulation_action": "ACTIVE"` nhưng 5 lần đọc sau vẫn trả dữ liệu bình thường. `grep call_response` cho thấy biến chỉ dùng để vẽ HTML; API_changes ghi "removed response_manipulator, request_tracer from server".
7. Kiểu dữ liệu simulator cũ chỉ có `bits/uint16/uint32/float32/string`, word order cố định big-endian (`int.to_bytes(…, "big")`), **không có int16/int32 có dấu**.

## 3. pymodbus 3.15.0 — API mới `SimData`/`SimDevice` và PoC "virtual site"

Đọc `pymodbus/simulator/*.py` [FACT]: module ghi "experimental"; `ModbusTcpServer(context=SimDevice | list[SimDevice])` đã nhận trực tiếp; `DataType` có INT16/UINT16/INT32/UINT32/INT64/UINT64/FLOAT32/FLOAT64/STRING/BITS/REGISTERS; `SimData(readonly=True)`; `SimDevice(action=…)` gọi hook `async (function_code, start_address, address, count, current_registers, set_values) -> ExcCodes | None` **trước** mỗi request, hook sửa được thanh ghi tại chỗ hoặc trả mã exception. Không có tùy chọn word order (chuyển đổi luôn big-endian).

PoC `scripts/vsite/vsite_poc.py` (127 dòng, Python): một cổng `127.0.0.1:5502`, unit 1 = PV, 2 = BESS, 3 = công tơ POC, 247 = điều khiển lab. Mô hình: PV từ CSV pvlib × `p_limit_pct`; tải 180 kW + 120 kW giờ hành chính; BESS 500 kWh/250 kW, η = 0,95, trễ bậc 1 τ = 2 s, CCL/DCL giảm tuyến tính 10 % gần SOC 5/95 %, watchdog 60 s; `P_grid = P_load − P_pv − P_bess`; bộ đếm Wh U64. Đồng hồ ×60.

Đoạn cốt lõi:

```python
async def action(unit, fc, start, address, count, regs, values):
    if unit == 2:
        if values is not None and address == 20:          # ghi setpoint I32 (W, + = xả)
            site.p_set = s32(values[0:2]); site.last_write = time.monotonic()
        regs[0:2] = i32(site.p_bess); regs[2] = int(site.soc * 1000) ...
    elif unit == 3:
        if site.fault == 1: return ExcCodes.DEVICE_BUSY     # tiêm lỗi
        if site.fault != 2: regs[0:2] = i32(site.p_grid) ...  # 2 = đóng băng
devices = [SimDevice(id=2, simdata=[SimData(0, count=15, datatype=DataType.REGISTERS, readonly=True),
                                    SimData(20, values=0, datatype=DataType.INT32)],
                     action=functools.partial(action, 2)), ...]
server = ModbusTcpServer(devices, address=("127.0.0.1", 5502))
```

Chạy: `python -I vsite_poc.py pv_day_hcmc_500kwp.csv 60` rồi `python -I edge_probe.py`. Kết quả [FACT]:

```
t0: pv.p=287646 W | ess.p=0 W soc=50.0% pch=250000 pdis=250000 | meter.p=18123 W e_imp=569 Wh e_exp=0 Wh
write ess p_set=+200000 W (discharge): True
t+3s(=180s sim): pv.p=292236 W | ess.p=200000 W soc=47.8% | meter.p=-187166 W e_exp=9264 Wh
write pv p_limit_pct=50: True
after curtail: pv.p=146874 W | ess.p=200000 W soc=47.1% | meter.p=-42040 W
write ess p_set=-250000 W (charge): True
charging: pv.p=149117 W | ess.p=-250000 W soc=49.5% | meter.p=405000 W e_imp=20870 Wh
write to readonly ess.p reg0: ExceptionResponse(dev_id=2, function_code=144, exception_code=2)
unknown unit 9: ExceptionResponse(dev_id=9, function_code=131, exception_code=4)
fault=1 meter read: ExceptionResponse(dev_id=3, function_code=131, exception_code=6)
fault=2 frozen: [6, 11784] [6, 11784] True
```

Dấu đúng quy ước 05/07 (meter + = nhập, ESS + = xả). Lưu ý: unit không tồn tại → pymodbus trả **exception 04**, không im lặng (khác thiết bị thật/gateway, xem §9).

## 4. SunSpec: pysunspec2 1.3.6 + pymodbus

`pysunspec2` cài từ PyPI kèm 114 file `models/json/model_*.json` [FACT]. Không có server/simulator trong gói (chỉ client RTU/TCP và `FileClientDevice` đọc ảnh thiết bị JSON); nhưng `Device.get_mb()` **tuần tự hóa** model thành byte Modbus.

`scripts/sunspec/sunspec_server.py`: nạp `sunspec2/tests/test_data/device_1547.json` (model 1, 701–713), đặt `701.W_SF = 1`, `701.W.cvalue = 123456.0`, lấy `get_mb()`, thêm `"SunS"` ở 40000 và model kết thúc `0xFFFF, 0`, phục vụ bằng `SimDevice(SimData(40000, count=614, datatype=REGISTERS))`.

`scripts/sunspec/sunspec_scan.py`: `SunSpecModbusClientDeviceTCP(slave_id=1, ipaddr="127.0.0.1", ipport=5503).scan()`.

Kết quả [FACT]:

```
base addr 40000 models found: [1, 701, 702, …, 713]
Mn SunSpecTest Md Test-1547-1 SN sn-123456789
701.W raw 12346 SF 1 cvalue 123460.0 Hz 60.01
after write: WMaxLimPctEna 1 WMaxLimPct 50          # server log: WRITE fc 16 addr 40310 values [1, 50]
```

Lỗi gặp và nguyên nhân [FACT]:

- `W.cvalue = 123456` với `W_SF = 0` → `ModelError: 'h' format requires -32768 <= number <= 32767` (W là int16 → phải chọn SF; giá trị bị lượng tử hóa 123456 → 123460).
- Thiếu model kết thúc `0xFFFF` → `scan()` đi quá vùng và lỗi `struct.error: 'H' format requires 0 <= number <= 65535`.
- Ảnh mẫu có `WMaxLimPct_SF = None` → ghi `cvalue` báo `SF field … not initialized`; ghi giá trị thô thì được.

## 5. dertwin 0.1.12 (MIT) — chạy trong Docker

Đọc code [FACT]: ~15.000 dòng Python; thiết bị BESS (battery + inverter + controller), PV, CHP, công tơ, mô hình ngoài (irradiance, nhiệt độ, tần số/điện áp lưới có nhiễu seed); register map YAML theo thiết bị có `address`, `func` (3/4/6/16), `type`, `count`, `scale`, `unit`, `direction`, `endian` theo từng thanh ghi; Modbus TCP và RTU (socat). Phụ thuộc `pymodbus>=3.8,<3.13` và dùng `ModbusServerContext` (API sẽ bị bỏ ở v4). Không tìm thấy cơ chế tiêm lỗi Modbus (grep `inject|ExcCodes|exception_code` không có kết quả).

```bash
docker run -d --name dertwin -v $REPO:/src:ro -v /root/.ccr/ca-bundle.crt:/ca.crt:ro \
  -e PIP_CERT=/ca.crt -e SSL_CERT_FILE=/ca.crt -p 127.0.0.1:55001-55005:55001-55005 python:3.12-slim \
  sh -c "cp -r /src /app && cd /app && pip install -q . && dertwin -c configs/full_site_config.json"
```

Log: 5 server Modbus TCP (55001–55005), "Simulation engine started | step=0.100s". Probe `scripts/dertwin_probe.py` đọc YAML của chính repo [FACT]:

```
t0 {'system_soc': 60.0, 'active_power': 0.0, 'max_charge_power': 50.0, 'working_status': 0} | meter {phase_active_power_a: 8.455, …} | pv {total_active_power: 24.6}
power on (10055=1), remote (10057=1), setpoint 10126 = −30 kW (int32, scale 0.1)
t+8s {'system_soc': 60.1, 'active_power': -30.0, 'working_status': 1} | meter {phase_active_power_a: 18.455, …}
```

Công tơ phản ứng theo BESS (+10 kW/pha khi sạc 30 kW) → có cân bằng site.

## 6. OpenEMS Edge (Docker Hub `openems/edge:latest`, tạo 2026-10-01)

```bash
docker run -d --name oems -p 127.0.0.1:8080:8080 -p 127.0.0.1:8084:8084 -p 127.0.0.1:15502:502 openems/edge:latest
```

Cấu hình bằng Felix Web Console (admin/admin), mỗi component một POST:

```bash
curl -u admin:admin -X POST "http://127.0.0.1:8080/system/console/configMgr/%5BTemporary%20PID%5D" \
  --data "apply=true&factoryPid=Simulator.EssSymmetric.Reacting&action=ajaxConfigManager&propertylist=id,enabled,capacity,...&id=ess0&enabled=true&capacity=10000&..."
```

Đã tạo: `Simulator.Datasource.CSV.Predefined` (datasource0 tải H0, datasource1 PV), `Simulator.NRCMeter.Acting`, `Simulator.ProductionMeter.Acting`, `Simulator.EssSymmetric.Reacting` (ess0 5 kW/10 kWh), `Simulator.GridMeter.Reacting`, `Controller.Api.Rest.ReadWrite` (8084), `Controller.Api.ModbusTcp.ReadWrite` (502). Tất cả HTTP 302, file `.config` xuất hiện dưới `/var/opt/openems/config/…`.

Kết quả [FACT]:

- REST `GET /rest/channel/_sum/(GridActivePower|…)` (user `x`, mật khẩu `admin`) trả JSON có mô tả dấu: "Grid exchange power. Negative values for sell-to-grid; positive for buy-from-grid"; ESS "Negative values for charge; positive for discharge" — **trùng quy ước 05**.
- `POST /rest/channel/ess0/SetActivePowerEquals {"value":3000}` → sau 3 s: `ess0/ActivePower 3000`, `meter0/ActivePower -3000`, `_sum/GridActivePower -3000`.
- JSON-RPC `componentJsonApi → getModbusProtocol` của `ctrlApiModbusTcp0`: bảng 70 dòng, **chỉ `_meta` và `_sum`** (ví dụ `_sum/EssSoc` ref 302 uint16, `_sum/GridActivePower` ref 315 float32). Các component `Simulator.*` không xuất hiện (không cài `ModbusSlave`). pymodbus đọc `302 → [50]`, `315 → 0.0`.
- Bảng nguồn CSV dựng sẵn chỉ có 5 profile hộ gia đình H0 (Đức) + `zero.csv`.

## 7. OCPP

### 7.1 SAP e-mobility-charging-stations-simulator 4.12.0

Build trong `node:22-alpine` (pnpm 12.10 qua corepack):

```bash
docker run --name sapbuild -v $REPO:/src:ro -v /root/.ccr/ca-bundle.crt:/ca.crt:ro -e NODE_EXTRA_CA_CERTS=/ca.crt \
  -e npm_config_cafile=/ca.crt node:22-alpine sh -c "cp -r /src /app && cd /app && npm i -g --ignore-scripts corepack \
  && corepack enable && pnpm install --ignore-scripts --frozen-lockfile && pnpm build"
docker commit sapbuild sapsim:local     # 1,19 GB (gồm devDependencies; image chính thức nhỏ hơn)
docker run -d --name sapsim --network host -v $PWD/sap_config.json:/app/dist/assets/config.json:ro \
  -v $PWD/idtags.json:/app/dist/assets/idtags.json:ro -w /app sapsim:local sh -c "NODE_ENV=production node dist/start.js"
```

`sap_config.json`: `supervisionUrls: ["ws://127.0.0.1:9000"]`, hai template `virtual-simple-atg` (OCPP 1.6, 3 connector, ATG bật) và `keba-ocpp2` (2.0.1).

### 7.2 CSMS mini bằng `ocpp` 2.1.0 (MIT)

`scripts/ocpp/mini_csms.py` (~120 dòng): `websockets.serve(…, subprotocols=["ocpp1.6","ocpp2.0.1"])`, chọn lớp `ocpp.v16.ChargePoint` hoặc `ocpp.v201.ChargePoint` theo subprotocol. Gói `ocpp` 2.1.0 có `ocpp/v16`, `ocpp/v201`, **`ocpp/v21`** [FACT].

Lỗi của chính lab: đặt tên handler là `start` → che `ChargePoint.start()` → `TypeError: CS16.start() missing 4 required positional arguments`. Đổi tên `on_start_tx`.

Kết quả SAP ↔ mini CSMS [FACT]:

```
[1.6 CS-BASIC-00001] Boot vendor=Ovomaltin model=Simulator simple
[1.6] Status c1=Available, c2=Preparing, c3=Faulted ...
[1.6] StartTransaction c3 meter_start=0 Wh
[1.6] SetChargingProfile 16A -> Accepted
[1.6] MeterValues c1 {'SoC': '81', 'Energy.Active.Import.Register': '159.49'} ...
[1.6] StopTransaction tx=1180 meter_stop=335 Wh
[2.0.1 CS-KEBA-OCPP2-00001] Boot {'model': 'KC-P30-ESS400C2-E0R', 'vendor_name': 'Keba AG', ...}
[2.0.1] RequestStartTransaction -> Accepted
[2.0.1] TransactionEvent Started trigger=RemoteStart seq=0 meter=[('Energy.Active.Import.Register', 0), ('Voltage', 239.24), ...]
[2.0.1] TransactionEvent Updated trigger=MeterValuePeriodic seq=1 meter=[('Voltage', 224.15), ('Power.Active.Import', 13…)]
CALLError: error_code=NotImplemented, error_description=SetChargingProfile is not implemented   # 2.0.1
```

README SAP liệt kê cho 2.0.x các khối A, B, C, D, E, F, G, J, L, M, N, P — **không có K (SmartCharging)**; 1.6 có Smart Charging Profile (Set/Clear/GetCompositeSchedule) [FACT]. Theo code, giá trị đo được giới hạn bởi `getConnectorMaximumAvailablePower` có tính charging profile (`HelpersChargingProfile.ts`) — **đọc code, chưa đo** `[INFERENCE]`.

Bẫy cấu hình [FACT]: `supervisionUrls` trong **station template** (keba-ocpp2 có `ws://localhost:9000`) **đè** `supervisionUrls` trong `config.json`; phải mount template sửa.

### 7.3 CitrineOS 2.0.1 (Apache-2.0)

`ghcr.io/citrineos/citrineos-server:latest` không tải được (blob Forbidden). Build từ nguồn: `node:22-alpine` thất bại (`engines.node >=24.16.0`, "Got: v22.23.3"); `node:24-alpine` (Docker Hub, lần thử thứ nhất OK):

```bash
docker run --name citbuild ... node:24-alpine sh -c "cp -r /src /app && cd /app && npm i -g corepack@latest && corepack enable \
  && pnpm install --frozen-lockfile && pnpm --filter '@citrineos/ocpp-server...' build"     # pnpm 10.19.0, ~23 s install
docker commit citbuild citrine:local                                                          # 2,37 GB
docker network create citnet
docker run -d --name ocpp-db --network citnet -e POSTGRES_DB=citrine -e POSTGRES_USER=citrine -e POSTGRES_PASSWORD=citrine postgis/postgis:16-3.5
docker run -d --name amqp-broker --network citnet rabbitmq:3-management
docker run -d --name citrine --network citnet -p 127.0.0.1:18080:8080 -p 127.0.0.1:18081:8081 -w /app/apps/ocpp-server \
  -e APP_NAME=all -e DB_STRATEGY=migrate -e CITRINEOS_DATABASE_HOST=ocpp-db \
  -e CITRINEOS_MESSAGEBROKER_AMQP_URL=amqp://guest:guest@amqp-broker:5672 ... citrine:local sh ./entrypoint.sh
```

Kết quả [FACT]: migration chạy, "schema validation: 0 errors, 4 warnings (52 tables, 635 columns)", "Server listening at http://127.0.0.1:8080", Swagger `/docs` → 200. `websocket-servers.json` khai báo `"protocols": ["ocpp2.1", "ocpp2.0.1", "ocpp1.6"]` cho security profile 0–3. SAP: `CS-BASIC-00001` (1.6) và `CS-KEBA-OCPP2-00001` (2.0.1) đều **BootNotification Accepted**; `Authorize` của tag chưa đăng ký → `Invalid` (phải tạo tag qua API, chưa làm). Hasura (GraphQL) không chạy — server lõi vẫn lên.

### 7.4 SteVe, EVerest, Monta — chỉ đọc

- SteVe README hiện ghi hỗ trợ **OCPP 1.2S/J, 1.5S/J, 1.6S, 1.6J (gồm Security Extensions)** [FACT] — khác ghi chú E2/15 ("chưa hỗ trợ Security Whitepaper"). Không chạy: docker-compose build từ nguồn + MariaDB 10.11.
- EVerest: có `config/config-sil-ocpp.yaml`, `config-sil-ocpp201.yaml`, `config-sil-ocpp201-pnc.yaml`, `modules/Simulation/{EvseManagerSimulator, YetiSimulator, SlacSimulator, …}`, `applications/containers/{mosquitto, nodered, steve, mqtt-explorer}` [FACT]. Không build (C++/Bazel/CMake, nặng).
- Monta ocpp-emulator: Kotlin (Compose desktop + engine), Apache-2.0. Không chạy.

## 8. IEC 60870-5-104: c104 2.2.1 (GPL-3.0)

`pip install c104==2.2.1` cài được **wheel cho Python 3.13** (E2 ghi "Python < 3.13" — đã lỗi thời) [FACT]. `scripts/iec104/c104_test.py`: server CA 47, điểm `M_ME_NC_1` IOA 11 = −123.4, điểm lệnh `C_SE_NC_1` IOA 5001; client `Init.ALL`.

```
connected True interrogation value -123.4000015258789
setpoint transmit ok True
server received setpoint {'sp': 800.0}
```

Bẫy: callback `on_receive` phải có **chú thích kiểu** đúng chữ ký, nếu không: `ValueError: Invalid callback signature, expected: (point:c104.Point,previous_info:c104.Information,message:c104.IncomingMessage)->c104.ResponseState`.

## 9. Java Modbus: digitalpetri modbus 2.1.6 (EPL-2.0)

Maven project tối thiểu (`com.digitalpetri.modbus:modbus-tcp:2.1.6`), `ProcessImage` + `ReadWriteModbusServices`, ghi `meter.p = −36000` I32 BE vào HR 0–1, cổng 1502. pymodbus đọc [FACT]:

```
regs [65535, 29536] meter.p -36000
write 10..11 = [7, 8] → read back [7, 8]
unit 2 → pymodbus: "No response received after 0 retries"    # unit lạ: server im lặng (đúng như tài liệu repo)
```

j2mod 3.4.0 (Apache-2.0) có `com.ghgande.j2mod.modbus.slave.ModbusSlave` — chỉ đọc code, không chạy.

## 10. Profile PV: pvlib 0.16.1 (BSD-3-Clause)

`scripts/pv/pv_profile.py`: `Location(10.80, 106.65, tz="Asia/Ho_Chi_Minh")`, clear-sky Ineichen, `PVSystem` PVWatts 500 kWp, tilt 10°, azimuth 180°, inverter `pdc0 = 500/1.2` kW, `ModelChain(aoi_model="physical", spectral_model="no_loss")`, ngày 2026-03-15, bước 1 phút.

```
pvlib 0.16.1: rows=1440 peak=400.0 kW energy=3000 kWh specific=6.00 kWh/kWp
PVGIS fetch failed: ProxyError ... re.jrc.ec.europa.eu
```

6,0 kWh/kWp là **trần clear-sky** (không mây), cao hơn thực tế ở TP.HCM `[INFERENCE]`; đỉnh bị kẹp 400 kW do tỉ lệ DC/AC 1,2.

## 11. Lưới/pin (khả thi, không đào sâu)

```
pandapower 3.5.6 runpp 52 ms; P_ext_grid=-0.0465 MW; Vm bus2=1.0935 pu     # lưới 22/0,4 kV, tải 0,4 MW, PV 0,35 MW, storage -0,1 MW
pybamm 26.10.0.0 SPM 30-min 1C solve 0.2 s; V_end=3.631 V
```

pandapower: `storage.p_mw > 0` = **sạc** (quy ước tải) — ngược dấu ESS của ta (05: + = xả) [FACT, theo kết quả: p_mw = −0,1 làm P_ext_grid âm]. venv `grid` 825 MB.

## 12. Dọn dẹp

- Đã dừng toàn bộ process (pymodbus sim, vsite, SunSpec server, mini CSMS) và container (sapsim, citrine, ocpp-db, amqp-broker, oems, dertwin), xóa network `citnet`.
- Scratchpad ~1,9 GB (< 2 GB); xóa venv `grid` (825 MB) vì không cần cho bước sau.
- Image Docker để lại cho bước hạ tầng: `sapsim:local` 1,19 GB, `citrine:local` 2,37 GB, `openems/edge`, `postgis/postgis:16-3.5`, `rabbitmq:3-management`, `hasura/graphql-engine` (chưa dùng), `python:3.12-slim`, `node:22-alpine`, `node:24-alpine`. Xóa bằng `docker rmi` nếu cần chỗ.
