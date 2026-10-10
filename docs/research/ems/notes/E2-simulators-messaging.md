# E2 — Bộ mô phỏng thiết bị và lựa chọn messaging (Agent E2)

[← Mục lục](../index.html) · [06 Kiến trúc](../06-system-architecture.html) · [07 Tích hợp](../07-device-integration.md) · [10 An toàn](../10-security-and-reliability.md) · [11 Lộ trình](../11-mvp-and-roadmap.html) · [15 Simulator & messaging](../15-simulators-and-messaging.md) · [14 Nguồn](../14-source-register.md)

- Người viết: Agent E2 (Simulation & Messaging). Ngày: 2026-10-10. Trạng thái: ghi chú nghiên cứu bản 1. Đầu vào cho tài liệu [15](../15-simulators-and-messaging.md), và đề xuất sửa cho 06 (ADR-03/04/05, PoC-02) và 07 (§7, §11).
- Câu hỏi của người dùng: *"Nghiên cứu các source các thiết bị simulator và dùng MQTT hoặc message nào không"*. Tách thành hai phần: (1) mã nguồn/công cụ mô phỏng thiết bị EMS để phát triển và kiểm thử khi chưa có phần cứng; (2) chọn giao thức/broker cho edge↔cloud và messaging bên trong cloud.
- **Phương pháp bằng chứng.** Môi trường chặn tải trang trực tiếp (WebFetch/curl). Mọi FACT mới lấy qua WebSearch: nội dung là tóm tắt/snippet do công cụ tìm kiếm trả về cho đúng URL đó, mặc định **"(qua kết quả tìm kiếm)"**. **Không clone được repo nào**. Mô tả repo chỉ dựa trên README/trang dự án/trang đóng gói xuất hiện trong kết quả tìm kiếm. Giấy phép ghi theo nguồn đã thấy; nhiều chỗ là nguồn thứ cấp (nixpkgs, ecosyste.ms, mirror) và ghi rõ như vậy. Thông tin "kiến thức nền" (chưa có nguồn trong phiên) gắn `[INFERENCE]` hoặc `[UNKNOWN]`.
- Không lặp lại nội dung đã có ở ghi chú E (F-12 Sparkplug, F-13 MQTT 5 expiry, F-31 OpenEMS cycle) và phán quyết K (R-12 topic, §6 #20 uplink). File này **mở rộng** các điểm đó.
- Quy ước mã trong file: phát hiện `F2-NN`, đề xuất `PR-E2-NN`, câu hỏi mở `Q-E2-NN`, vấn đề chéo `X-E2-NN`, dòng ledger `E2-NN`. Mọi mã là tạm thời (K §6 #38).

---

## 1. Phạm vi & câu hỏi nghiên cứu

| ID | Câu hỏi |
|---|---|
| Q1 | Có mã nguồn/công cụ nào mô phỏng được Modbus/SunSpec inverter, PCS/BMS, công tơ, sạc EV (OCPP), DR (OpenADR/2030.5), IEC 104/61850? Giấy phép, ngôn ngữ, mức duy trì, độ trung thực? |
| Q2 | Mô hình vật lý/dữ liệu nào đủ để "site ảo" có hành vi hợp lý (PV, tải, SOC BESS, cân bằng POC) mà không quá nặng? |
| Q3 | Bộ mô phỏng nào cho laptop, CI, HIL lab, demo bán hàng? Mô phỏng **không** chứng minh được gì? |
| Q4 | Edge↔cloud: MQTT 3.1.1, MQTT 5, Sparkplug B hay giao thức khác? OpenEMS, Victron, Huawei, AWS/Azure làm thế nào? |
| Q5 | Broker nào (EMQX, HiveMQ, Mosquitto, VerneMQ, NanoMQ, RabbitMQ, managed cloud)? Giấy phép hiện hành? |
| Q6 | Trong cloud có cần Kafka ở MVP không? Ngưỡng nâng cấp ở 100 / 1.000 / 10.000 site? |
| Q7 | Frontend live update: SSE, WebSocket hay MQTT-over-WebSocket? |

---

## 2. Phát hiện chính

**Mô phỏng Modbus/SunSpec**

- F2-01 [FACT] pymodbus có bộ simulator: server Modbus + giao diện HTTP/REST, cấu hình bằng file JSON (mục `server_list` và `device_list`), datastore là một danh sách thanh ghi phẳng có thể thay đổi bằng "actions", web UI, REST API hoặc client ghi vào. REST API được mô tả là để tự động hóa test harness. **Tài liệu cảnh báo: từ v3.9.0 đến v4.0.0 simulator này sẽ bị thay bằng phiên bản mới** ("simulator3", mô hình `SimData`/`SimDevice`), và chữ ký API đã đổi giữa 3.8 và 3.11+. pymodbus BSD-3-Clause; bản 3.14.0 phát hành 2026-07-12 theo mirror piwheels (pepy ghi 3.13.0, có thể là snapshot cũ). (E2-01, E2-02)
- F2-02 [FACT] modbus-tk (Python, LGPL-2.1) có "simulator dùng ngay với giao diện RPC". diagslave (FieldTalk) là slave dòng lệnh miễn phí theo license riêng, hỗ trợ RTU/ASCII/TCP/UDP. ModbusPal (Java, GPL) mô phỏng tới 247 slave, có script và giá trị động, bản chính thức 1.6b. (E2-03, E2-04)
- F2-03 [FACT] Java: j2mod là fork của jamod 1.2.1, giấy phép Apache 2.0 (trang SourceForge cũng ghi BSD). OpenEMS phát hành artifact `io.openems:j2mod` (fork riêng). digitalpetri/modbus hỗ trợ Modbus TCP, Modbus TCP Security, RTU serial, RTU over TCP, Java 17+; giấy phép EPL-2.0 chỉ thấy qua POM của một wrapper bên thứ ba. (E2-05)
- F2-04 [FACT] SunSpec: pysunspec2 (Python, Apache 2.0 theo nixpkgs; phiên bản 1.2.1–1.3.5 tùy nguồn) là thư viện đọc định nghĩa model và giao tiếp thiết bị SunSpec. Simulator SunSpec mã mở duy nhất tìm thấy là `emdem/sunspec-sim` (MIT), tách từ `sunspec/device-webprobe`, có shell `add_slave/add_block/set_values`, cổng 502. `nielsbasjes/sunspec-device` (Apache-2.0) sinh schema Modbus từ model SunSpec chính thức; `otfabric/go-sunspec` có 112 model dựng sẵn. **Không thấy "SunSpec DER simulator" chính thức mã mở.** (E2-06, E2-07)
- F2-05 [FACT] OpenEMS có các component mô phỏng **bên trong Edge**: `Simulator.EssSymmetric.Reacting` (mô phỏng SOC, hành vi phụ thuộc controller), `Simulator.GridMeter.Reacting` (lưới phản ứng theo component khác), `Simulator.Datasource.CSV` (Predefined: profile chuẩn kèm sẵn; Direct: dán CSV). Bản 2022.10.0 thêm Simulated ESS suy ra AllowedCharge/DischargePower từ Capacity với C-rate 1. Có issue báo tutorial đã lỗi thời; forum có ý kiến rằng dữ liệu 15 phút với cycle ngắn làm phép tính năng lượng/SOC sai. (E2-08)
- F2-06 [INFERENCE] Các simulator OpenEMS là **channel ảo trong process Edge**, không phải thiết bị Modbus trên mạng. Chúng kiểm được **controller** (logic peak shaving, arbiter) nhưng **không** kiểm được **driver Modbus** của ta. Nếu ADR-07 chọn OpenEMS Edge thì dùng chúng cho test controller; driver vẫn cần Modbus server ảo bên ngoài.
- F2-07 [FACT] Không tìm thấy emulator Huawei SUN2000/SmartLogger hay Sungrow mã mở. Chỉ có thư viện client (`wlcrs/huawei-solar-lib`, `sun2000_modbus`) và proxy cache `norbim1/sun2000-modbus-cache` (giữ **một** kết nối tới inverter, phục vụ nhiều client — khớp ràng buộc một client của E F-04). Bên tích hợp thứ ba lấy dữ liệu SmartLogger qua **FTP/SFTP đẩy CSV** (khuyến nghị 300 s) hoặc Modbus TCP ("Remote Communication Scheduling" để điều khiển P). SmartLogger tải dữ liệu lên FusionSolar; danh sách giao thức gồm Modbus TCP, IEC 60870-5-104, Modbus RTU, IEC 60870-5-103, DL/T645. **Không thấy tài liệu MQTT cho SmartLogger/EMMA.** (E2-12, E2-13)
- F2-08 [FACT] Victron Venus OS dùng broker **FlashMQ** + plugin `dbus-flashmq` để ánh xạ D-Bus sang MQTT, có cơ chế keepalive (`R/<id>/keepalive`, dữ liệu dưới `N/<id>/…`) và kết nối tới máy chủ MQTT của VRM. Mô phỏng: cộng đồng dùng `velib_python` (`dbusdummyservice.py`) và dự án `venus-os_dbus-multiplus-emulator`; demo mode ESS có hạn chế (dữ liệu grid meter không hiện). (E2-10, E2-11)
- F2-09 [FACT] Công tơ Eastron SDM630: không có emulator Modbus mã mở dạng repo; có cấu hình ESPHome giả lập thanh ghi SDM630 (forum). evcc có `demo-meter`/`demo-battery` giá trị cố định và `demo.yaml` với thiết bị demo động bằng JavaScript. (E2-14)

**Sạc EV / OCPP**

- F2-10 [FACT] Simulator charge point: SAP `e-mobility-charging-stations-simulator` (Node.js, Apache-2.0, mô phỏng và **scale** nhiều trạm OCPP-J; một bài báo nói chỉ hỗ trợ 1.6 — có thể lỗi thời, tag repo có `ocpp20`); Monta `ocpp-emulator` (1.6 + 2.0.1, desktop/web, chặn/sửa message để tái hiện charger không chuẩn); MicroOcpp Simulator (WebAssembly trong trình duyệt); `oglimmer/scriptable-ocpp-chargepoint-simulator` (1.6J, REST, script JS, Apache-2.0); Solidstudio VCP (1.6 + 2.0.1, Apache-2.0). (E2-15, E2-20)
- F2-11 [FACT] Thư viện `ocpp` của Mobility House: Python, MIT (tài liệu spec trong `docs/v16`, `docs/v201` theo CC BY-ND), hỗ trợ OCPP 1.6 và 2.0.1; không thấy 2.1. (E2-16)
- F2-12 [FACT] CSMS mã mở: SteVe (Java, GPL — phiên bản GPL chỉ thấy qua bên thứ ba; OCPP 1.2/1.5/1.6 SOAP/JSON; README cảnh báo **chưa hỗ trợ OCPP 1.6 Security Whitepaper**; cần JDK 17 + MySQL/MariaDB); một bản thương mại "SteVe OCPP Pro" có chứng nhận OCA 1.6 (07/2026). CitrineOS (LF Energy, OCPP 1.6 + 2.0.1, 1.3.0 thêm smart charging 2.0.1 và OCPI 2.2.1; giấy phép chưa thấy). EVerest (LF Energy) có SIL/HIL, module là process Linux giao tiếp qua **MQTT**, OCPP 1.6/2.0.1. (E2-17, E2-18, E2-19)

**DR, IEC 104/61850**

- F2-13 [FACT] OpenLEADR: bản Python OpenADR 2.0b **hiện không còn được duy trì**; dự án tập trung `openleadr-rs` (Rust, OpenADR 3.1), chưa có bản "field-test-ready" chính thức theo Tweede Golf. Bản reference implementation OpenADR 3 của Alliance **chỉ dành cho thành viên**; spec có file OpenAPI YAML để sinh code. (E2-21, E2-22)
- F2-14 [FACT] IEEE 2030.5: EPRI có client mã mở BSD-3 (được tài trợ bởi CEC cho Rule 21); test tool chuẩn là QualityLogic (thương mại). Không thấy server/test tool 2030.5 mã mở trong GridAPPS-D. (E2-23)
- F2-15 [FACT] lib60870 và libIEC61850 (MZ Automation): GPLv3 **hoặc** giấy phép thương mại; libIEC61850 bản 1.6.x. j60870 (OpenMUC, Java): GPLv3, giấy phép độc quyền thương lượng riêng, làm được client và server. `c104` (Python, Fraunhofer, dựa trên lib60870-C, GPLv3) dùng để **mô phỏng SCADA và RTU** IEC 104. QTester104: client 104 trên Qt (giấy phép chưa thấy). (E2-24, E2-25, E2-26, E2-27)

**Lưới, đồng mô phỏng, pin, dữ liệu**

- F2-16 [FACT] pandapower (BSD, theo bài báo), HELICS (BSD-3), mosaik (LGPL-2.1, có binding pandapower), GridLAB-D (BSD-style + điều khoản Battelle), PyPSA (MIT), PyBaMM (BSD-3, mô hình điện hóa SPM/SPMe/DFN). Giấy phép OpenDSS: chưa thấy trong kết quả. (E2-28)
- F2-17 [FACT] NREL BLAST-Lite: Python/MATLAB, BSD-3 (theo metadata repo), mô hình suy giảm pin Li-ion thương mại theo nhiệt độ, SOC, DOD, C-rate, fit từ dữ liệu lão hóa công khai. (E2-29)
- F2-18 [FACT] pvlib có `iotools.get_pvgis_tmy` lấy TMY từ PVGIS (JRC); API mặc định dùng mọi năm, khác bản web (10 năm); 0.13.0 đổi giá trị trả về thành `(data, meta)`. PVGIS 5.3 (09/2024) dùng SARAH-3 (2005–2023), phủ "phần lớn châu Á"; ngoài vùng vệ tinh dùng ERA5. Giấy phép pvlib (BSD-3) **chưa thấy** trong kết quả. (E2-30)
- F2-19 [FACT] Dữ liệu tải: Pecan Street Dataport miễn phí **chỉ cho đại học, phi thương mại**, cấm bán lại/cấp phép lại; thương mại tính phí theo dataset. NREL End-Use Load Profiles (ComStock/ResStock) 15 phút; giấy phép **mâu thuẫn**: AWS Open Data ghi "ComStock License", data.gov ghi CC BY 4.0. Dữ liệu là của **Mỹ**. OPSD: không có kết quả. (E2-31, E2-32)
- F2-20 [FACT] Toxiproxy (Shopify, MIT, Go): proxy TCP có "toxic" latency, bandwidth, reset, timeout, down, slicer…, điều khiển qua HTTP API; **chỉ TCP**. (E2-33)

**Messaging edge↔cloud và broker**

- F2-21 [FACT] **EMQX từ 5.9.0 chuyển sang BSL 1.1**, gộp bản Open Source (Apache 2.0) và Enterprise thành một. Tài liệu chính thức: **clustering không được phép mặc định từ 5.9.0**; cluster cần giấy phép thương mại. Additional Use Grant cho phép chạy production **một node**, **nhưng không áp dụng nếu cung cấp phần mềm cho bên thứ ba như dịch vụ hoặc tích hợp vào sản phẩm/giải pháp bán cho bên thứ ba** (văn bản grant trong ScanCode LicenseDB). Change Date = 4 năm sau khi phát hành mỗi bản, khi đó chuyển Apache 2.0. Docker Official Image `emqx` ngừng; dùng `emqx/emqx`. (E2-34)
- F2-22 [INFERENCE] Nền tảng SaaS của ta là "sản phẩm/giải pháp cung cấp cho bên thứ ba", nên theo câu chữ grant, **EMQX ≥ 5.9 cần giấy phép thương mại cho mọi triển khai production của ta, kể cả một node**. Bản ≤ 5.8 vẫn Apache 2.0 nhưng sẽ hết vòng đời. Cần ý kiến pháp lý (Q-E2-01).
- F2-23 [FACT] HiveMQ CE: Apache 2.0, **không có clustering** (nhân viên HiveMQ xác nhận trên forum 2021–2023; cluster thuộc Professional/Enterprise). Bản CE mới nhất thấy được là 2025.5; cần Java 11+ để chạy. (E2-36)
- F2-24 [FACT] VerneMQ: mã nguồn Apache 2.0, nhưng **gói nhị phân và Docker image từ 1.10.0 theo EULA**: dùng thương mại phải trả phí subscription hằng năm. Công ty Octavo Labs; dự án tự tuyên bố "vẫn được duy trì"; không thấy lịch sử commit/release gần đây trong kết quả. (E2-37)
- F2-25 [FACT] Mosquitto 2.1.0 (01/2026): bỏ dần `acl_file`/`password_file`/`per_listener_settings` (thay bằng plugin, gỡ ở 3.0), `max_packet_size` mặc định **2.000.000 byte**, thêm PROXY protocol v1/v2, systemd watchdog, giới hạn client/kết nối toàn cục, bỏ TLS 1.1; sau đó có 2.1.1, 2.1.2. (E2-38)
- F2-26 [FACT] NanoMQ: MIT, dự án LF Edge, bridge edge→nhiều cloud qua MQTT hoặc **MQTT over QUIC** (msquic, MIT), chuyển đổi QUIC/TCP. (E2-39)
- F2-27 [FACT] RabbitMQ (tài liệu 4.1/4.2): plugin MQTT trong bản phân phối lõi hỗ trợ MQTT 3.1, 3.1.1 và **5.0**; mỗi subscriber có queue riêng gắn với topic exchange. "Native MQTT" từ 3.12: một process Erlang mỗi kết nối, vendor công bố giảm bộ nhớ tới 95%, hàng triệu kết nối. Mục "Limitations" (3.13) liệt kê QoS 2 không hỗ trợ và tiếp tục với shared subscriptions (snippet bị cắt). (E2-40)
- F2-28 [FACT] NATS chỉ hỗ trợ MQTT **3.1.1**, bắt buộc account có JetStream; QoS 2 có từ 2.10; message từ NATS tới subscriber MQTT luôn QoS 0; retained message trong cluster là best-effort. (E2-41)
- F2-29 [FACT] AWS IoT Core hỗ trợ MQTT 3.1.1 và 5 "với một số khác biệt"; shared subscriptions GA 04/2023; có message/session expiry và request/response. Azure **IoT Hub**: MQTT 3.1.1 hạn chế, topic cố định (`devices/{deviceId}/messages/events/`), không wildcard; **MQTT 5 trên IoT Hub bị đánh dấu deprecated**; Microsoft khuyên dùng **Event Grid MQTT broker** (GA, MQTT 5 + 3.1.1, topic tùy ý). Google Cloud IoT Core **đóng ngày 16/08/2023**, cầu MQTT/HTTP đóng, kết nối bị ngắt, báo trước khoảng 1 năm. (E2-43, E2-44, E2-45)
- F2-30 [FACT] OpenEMS Edge↔Backend: Backend có `EdgeWebsocketImpl` "gửi JSON-RPC request có xác thực tới Edge qua WebSocket và chờ JSON-RPC response", cổng mặc định 8081; request tới Edge cụ thể bọc trong `edgeRpc` (`edgeId`, `payload`); có B2B API JSON-RPC qua REST/WebSocket. Xác nhận E F-31. (E2-09)
- F2-31 [FACT] MQTT 5 request/response: requester đặt Response Topic và Correlation Data; broker chuyển nguyên không sửa; **bên trả lời phải tự publish phản hồi** (broker không định tuyến). HiveMQ gọi đây là mẫu "business ACK". Azure Event Grid và AWS có ví dụ lệnh tới thiết bị. (E2-46)
- F2-32 [FACT] Sparkplug 3.0 đã thành tiêu chuẩn ISO/IEC; 4.0 đang làm (đề xuất MetaBirth retained). Phê bình chính (blog vendor): QoS 0 cho dữ liệu có thể mất số liệu khi rớt mạng/khởi động lại broker; protobuf nhỏ hơn JSON 60–75% (số của vendor); 2.2 và 3.0 khác topic/payload STATE nên trộn trên cùng broker dễ lỗi. (E2-47)
- F2-33 [FACT] Lý do không nối thiết bị thẳng vào Kafka (nguồn vendor MQTT/Confluent): client Kafka phải tới từng broker trực tiếp (lộ broker ra Internet), Kafka kém với số lượng topic lớn, client nặng (nhiều kết nối TCP), cần TCP ổn định nên kém trên 4G. Mẫu chuẩn: MQTT broker ở biên, bridge sang Kafka. (E2-48)
- F2-34 [FACT] PostgreSQL `NOTIFY`: payload mặc định phải < 8.000 byte (dữ liệu lớn → lưu bảng, gửi khóa); hàng đợi ~8 GB, đầy thì `NOTIFY` làm commit thất bại. Nguồn thứ cấp: thông báo không bền, không ai nghe thì mất. (E2-49)
- F2-35 [FACT] WebSocket từ trình duyệt chỉ có TLS một chiều, không trình chứng chỉ client được, nên MQTT-over-WS cho trình duyệt phải dùng token; khuyến nghị ACL tối thiểu, không anonymous. (E2-50)
- F2-36 [FACT] Redpanda Community: BSL, không được cung cấp Redpanda như dịch vụ streaming/queuing thương mại cho người khác; mã chuyển Apache 2.0 sau 4 năm. (E2-42)
- F2-37 [FACT] EMQX↔Kafka: tài liệu 5.2/5.6 ghi Kafka integration là tính năng Enterprise; trang mới nhất mô tả là "built-in" (do gộp bản ở 5.9). Benchmark vendor 5.1: một node bridge 100.000 tin QoS 1/s sang Kafka. Bản Open Source cũ chỉ có WebHook và MQTT bridge. (E2-35)

**Suy luận chính**

- F2-38 [INFERENCE] **Không có giải pháp "cắm là chạy" cho thiết bị Việt Nam**: không có emulator Huawei/Sungrow/tủ BESS Trung Quốc. Bộ mô phỏng phải **sinh từ register map YAML của chính driver** (07 §6.2) cộng mô hình vật lý đơn giản. Đó vừa là lợi thế (một nguồn định nghĩa) vừa là rủi ro (lỗi map giống nhau ở hai phía → test "xanh" giả). Giải: vector vàng từ thiết bị thật (07 §11.1 L1) và test HIL.
- F2-39 [INFERENCE] **MQTT 5 vẫn là lựa chọn đúng cho edge↔cloud** (khớp K §6 #20). Bằng chứng mới củng cố: (a) AWS, Azure Event Grid, RabbitMQ, EMQX, HiveMQ, Mosquitto đều hỗ trợ MQTT 5 → hợp đồng di động; (b) Google IoT Core đóng và Azure IoT Hub bỏ MQTT 5 cho thấy **không được gắn hợp đồng vào topic/SDK riêng của nhà cung cấp**; (c) request/response, expiry, correlation data của MQTT 5 khớp hợp đồng lệnh 07 §8.
- F2-40 [INFERENCE] **Thị trường broker cluster mã mở đã co lại**: EMQX ≥ 5.9 (BSL, cluster trả phí, grant không áp cho sản phẩm bán cho bên thứ ba), HiveMQ CE (không cluster), VerneMQ (nhị phân trả phí; mã nguồn tự build). Lựa chọn còn lại "mở và có cluster" là RabbitMQ 4.x (MQTT 5, nhưng không QoS 2 và có thể không shared subscription) hoặc tự build VerneMQ. Vì vậy ADR-04 phải **dự trù chi phí giấy phép broker** hoặc chấp nhận đổi mẫu ingest.

---

## 3. Phân tích chi tiết

### 3.1 Bảng so sánh công cụ mô phỏng

Độ trung thực: **R** = chỉ register map (giá trị tĩnh/script), **B** = có hành vi (phản ứng với lệnh, ràng buộc), **P** = mô hình vật lý. "Phù hợp" là đánh giá của E2 [INFERENCE].

| Công cụ | URL (qua kết quả tìm kiếm) | Giấy phép | Ngôn ngữ | Duy trì | Mô phỏng gì | Giao thức | Trung thực | Phù hợp cho ta | Rủi ro |
|---|---|---|---|---|---|---|---|---|---|
| pymodbus (server API + simulator) | https://pymodbus.readthedocs.io/en/dev/source/library/simulator/config.html | BSD-3 (pepy) | Python | 3.14.0 (07/2026, piwheels) | Server Modbus, datastore, REST điều khiển | Modbus TCP/RTU/ASCII | R (simulator) / B nếu tự viết logic quanh server API | **Cao**: nền cho virtual site | Simulator app sắp thay bằng simulator3, API đổi giữa phiên bản → dùng server API, khóa phiên bản |
| modbus-tk | https://github.com/bbarcklay/modbus-tk (mirror) | LGPL-2.1 | Python | 1.1.2–1.1.5 (không rõ ngày) | Simulator + RPC | Modbus TCP/RTU | R | Thấp (pymodbus đủ) | Ít hoạt động [UNKNOWN] |
| diagslave | https://www.modbusdriver.com/index.php/diagslave.html | Freeware (license riêng) | Binary | 3.5 (site) | Slave dòng lệnh | RTU/ASCII/TCP/UDP | R | Debug nhanh tại lab | Không mã nguồn, license phải đọc |
| ModbusPal | https://modbuspal.sourceforge.net/ | GPL | Java | 1.6b (cũ) | 247 slave, script, giá trị động | TCP (serial cần RxTx) | R/B (script) | Demo/ad-hoc | Dự án cũ; GPL chỉ dùng như công cụ, không nhúng |
| Modbus Slave (Witte) | — | Thương mại | Windows | [UNKNOWN] | Slave GUI | RTU/TCP | R | Kỹ sư hiện trường | Không tìm nguồn trong phiên |
| j2mod | https://sourceforge.net/p/j2mod | Apache 2.0 (+BSD) | Java | fork OpenEMS `io.openems:j2mod` | Thư viện master/slave | TCP/RTU | R (tự viết) | Trung bình: nếu muốn simulator Java | Nhiều fork; chọn bản duy trì |
| digitalpetri modbus | https://jitpack.io/p/digitalpetri/modbus | EPL-2.0 (thứ cấp) | Java 17+ | [UNKNOWN] | Thư viện client/server Netty | TCP, TCP Security, RTU | R (tự viết) | Trung bình–cao cho driver Java của edge | Giấy phép chưa đọc từ repo |
| Node-RED modbus | — | [UNKNOWN] | Node.js | [UNKNOWN] | Flex-server | TCP | R/B (flow) | Thấp | Không có nguồn trong phiên |
| emdem/sunspec-sim | https://github.com/emdem/sunspec-sim | MIT | Python | [UNKNOWN] | Slave SunSpec, block | Modbus TCP | R | Trung bình: tham khảo cách dựng chuỗi SunSpec | Dự án cá nhân |
| pysunspec2 + model JSON | https://mynixos.com/nixpkgs/package/python313Packages.pysunspec2 | Apache 2.0 (nixpkgs) | Python | 1.3.5 | Đọc/ghi thiết bị SunSpec, nạp model | Modbus | — (client) | **Cao**: nguồn định nghĩa model để sinh chuỗi SunS | Repo models chưa kiểm giấy phép (Q-E-07) |
| OpenEMS Simulator.* | https://openems.github.io/openems.io/openems/latest/simulation/realtime.html | EPL-2.0/AGPL theo module (K R-21) | Java/OSGi | Có trong release | ESS SOC, grid meter, datasource CSV | Channel nội bộ | B | Cao **chỉ khi** ADR-07 chọn OpenEMS (test controller) | Không kiểm driver; tài liệu lỗi thời |
| Victron dbus dummy/emulator | https://communityarchive.victronenergy.com/questions/197508/simulate-multi-rs.html | [UNKNOWN] | Python | Cộng đồng | Dịch vụ D-Bus giả | D-Bus/MQTT (FlashMQ) | R/B | Thấp (chỉ khi làm driver Victron) | Không chính thức |
| evcc demo devices | https://docs.evcc.io/en/meters/demo-meter | MIT [INFERENCE] | Go | Hoạt động | Meter/pin giá trị cố định, demo JS | Nội bộ evcc | R | Thấp | Không phải Modbus |
| SAP charging-stations-simulator | https://redirect.github.com/SAP/e-mobility-charging-stations-simulator | Apache-2.0 (oosmetrics) | Node.js | Hoạt động [INFERENCE] | Nhiều trạm sạc, scale | OCPP-J 1.6 (2.0.x chưa xác minh) | B | **Cao** cho tải OCPP và CI | Hỗ trợ 2.0.1 chưa xác minh |
| Monta ocpp-emulator | https://monta.com/en/?p=30014 | Mã mở (giấy phép chưa thấy) | Kotlin/desktop/web [UNKNOWN] | Hoạt động | Charger 1.6/2.0.1, chặn message | OCPP-J | B | Cao cho test tay và quirk | Giấy phép |
| MicroOcpp Simulator | https://github.com/matth-x/MicroOcpp | [UNKNOWN] | C++/WASM | Hoạt động | Charger trong trình duyệt | OCPP 1.6 (2.0.1 [UNKNOWN]) | B | Trung bình | — |
| Mobility House `ocpp` | https://pypi.org/project/ocpp/ | MIT (docs CC BY-ND) | Python | Hoạt động | Thư viện CP/CSMS | OCPP 1.6, 2.0.1 | — (thư viện) | Cao để viết CP ảo có quirk | Không có 2.1 |
| SteVe | https://github.com/rwth-i5-idsg/steve | GPL | Java | Hoạt động (JDK 17) | CSMS | OCPP 1.2–1.6 SOAP/JSON | — | Trung bình: CSMS đối chứng ở lab | Không Security Whitepaper; GPL |
| CitrineOS | https://lfenergy.org/projects/citrineos/ | [UNKNOWN] | TypeScript [INFERENCE] | 1.3.0 (07/2024) | CSMS | OCPP 1.6, 2.0.1 | — | Trung bình: đối chứng 2.0.1 | Giấy phép chưa thấy |
| EVerest | https://www.mintlify.com/EVerest/everest-core | Apache-2.0 [INFERENCE] | C++ | LF Energy | Firmware trạm sạc + SIL | OCPP 1.6/2.0.1, ISO 15118 | B/P (EV, SLAC giả) | Trung bình: charger ảo trung thực nhất | Nặng, cấu hình chậm |
| OpenLEADR (py 2.0b / rs 3.1) | https://lfenergy.org/projects/openleadr/ | [UNKNOWN] (Apache-2.0 [INFERENCE]) | Python / Rust | py: không duy trì; rs: hoạt động | VTN/VEN | OpenADR 2.0b / 3.1 | B | P2 | 2.0b bỏ; 3.x reference chỉ cho thành viên |
| EPRI 2030.5 client | https://www.opensourceforu.com/2019/02/epri-open-source-software-accelerates-implementation-of-intelligent-distributed-energy-resources/ | BSD-3 | C [INFERENCE] | 2019 | Client 2030.5 | IEEE 2030.5 | — | P2 (ngoài VN) | Không có server mã mở |
| lib60870 / libIEC61850 | https://github.com/mz-automation/lib60870 | GPLv3 hoặc thương mại | C (C#) | 61850: 1.6.x | Client/server 104, 61850 | IEC 104, MMS, GOOSE | — | Test 104/61850; sản phẩm cần license thương mại | GPL nếu nhúng vào edge đóng |
| j60870 (OpenMUC) | https://openmuc.org/iec-60870-5-104 | GPLv3 / độc quyền | Java | 1.8.0 (Maven) | Client/server 104 | IEC 104 | — | Cao cho **master 104 giả** trong test Java | Nhúng vào edge cần license độc quyền |
| c104 | https://pypi.org/project/c104 | GPLv3 | Python (lib60870) | 2.0.x | SCADA/RTU 104 | IEC 104 | B (callback) | **Cao** cho master 104 giả trong CI | Python < 3.13 |
| QTester104 | https://qtester104.sourceforge.net | [UNKNOWN] | C++/Qt | [UNKNOWN] | Client 104 GUI | IEC 104 | — | Lab (tay) | — |
| pandapower / PyPSA / OpenDSS / GridLAB-D | xem E2-28 | BSD / MIT / ? / BSD-style | Python / Python / C++ / C++ | Hoạt động | Power flow, tối ưu | — | P | Thấp ở MVP (BTM, một POC) | Quá mức cần cho C&I sau công tơ |
| HELICS / mosaik | xem E2-28 | BSD-3 / LGPL-2.1 | C++ / Python | Hoạt động | Đồng mô phỏng | — | — | P2 (HIL lớn, nghiên cứu) | Chi phí tích hợp |
| PyBaMM | https://science.ecosyste.ms/projects/34624 | BSD-3 | Python | Hoạt động | Điện hóa SPM/DFN | — | P (chi tiết) | Thấp: quá chi tiết cho EMS | Chậm, cần tham số cell |
| BLAST-Lite | https://www.nrel.gov/research/software/blast-lite--battery-lifetime-analysis-and-simulation-tool---lite | BSD-3 | Python | PyPI | Suy giảm pin | — | P (thống kê) | Trung bình: backtest chi phí suy giảm (08) | Cell Mỹ/Âu, không phải tủ VN |
| pvlib + PVGIS | https://pvlib-python.readthedocs.io/en/latest/reference/generated/pvlib.iotools.get_pvgis_tmy.html | BSD-3 [INFERENCE] | Python | Hoạt động | Bức xạ, sản lượng PV | — | P | **Cao**: profile PV cho site VN | API PVGIS đổi phiên bản |
| Toxiproxy | https://dev.co/testing/open-source/toxiproxy | MIT | Go | v2.12.0 (2025-03) | Lỗi mạng TCP | TCP | — | **Cao**: tiêm lỗi Modbus TCP, MQTT, OCPP | Chỉ TCP (RTU dùng cách khác) |

### 3.2 Thiết kế "virtual site" [PROPOSAL]

**Mục tiêu.** Một process (container) đóng vai **toàn bộ thiết bị** của một site C&I, nói đúng giao thức mà edge thật dùng, phản ứng với lệnh, và tiêm lỗi theo kịch bản. Không phải digital twin; chỉ đủ để kiểm driver, arbiter, buffer, hợp đồng lệnh và UI.

**Thành phần**

| Khối | Mô hình | Tham số chính | Lộ ra qua |
|---|---|---|---|
| Đồng hồ kịch bản | Thời gian mô phỏng; hệ số tăng tốc (1×, 10×, 60×); seed ngẫu nhiên cố định | `speed`, `seed`, `start_ts`, `tz=Asia/Ho_Chi_Minh` | REST điều khiển |
| PV | Profile công suất AC từ pvlib + PVGIS TMY theo tọa độ VN, scale theo kWp; nhiễu mây (chuỗi Markov hoặc phát lại ngày thật); kẹp theo `p_limit_pct` ghi vào; ramp theo cấu hình | `kwp`, `tilt`, `azimuth`, `dc_ac_ratio`, `cloud_model` | Modbus (map của driver PV: Huawei-like, SunSpec 1/103/701/704) |
| Tải | Profile 15 phút (ngày làm việc/cuối tuần) + nhiễu; bước tải theo kịch bản | `p_base_w`, `shape_id`, `steps[]` | Chỉ qua cân bằng công tơ (và sub-meter nếu có) |
| BESS (PCS + BMS) | SOC tích phân có hiệu suất; giới hạn CCL/DCL giảm dần gần SOC biên và theo nhiệt độ; trễ đáp ứng bậc 1 + ramp; watchdog setpoint có/không | `e_nom_wh`, `p_rated_w`, `eta_c`, `eta_d`, `soc_min/max`, `tau_s`, `ramp_w_per_s`, `watchdog_s` | Modbus: setpoint, mode, `soc`, `p_charge_max`, `p_discharge_max`, alarm word |
| Công tơ POC | `P_grid = P_load − P_pv − P_bess` (P_bess > 0 = xả, theo K R-01); bộ đếm `e_import`/`e_export` tích lũy riêng, int64 Wh; tùy chọn quay vòng (`R_wrap`) | `sign_convention`, `ct_ratio`, `ct_reversed`, `R_wrap` | Modbus (map công tơ, ví dụ kiểu SDM/SunSpec 20x) |
| EVSE (P1) | Charge point ảo kết nối tới CSMS cục bộ của edge; phiên sạc theo kịch bản; tôn trọng/không tôn trọng profile | `quirk_profile` (ví dụ Easee TxDefault), `min_a` | OCPP 1.6J (2.0.1 sau) |
| Điều độ (P1) | Master 104 giả gửi interrogation, setpoint, clock sync | CA, IOA | IEC 104 (c104 hoặc j60870) |

**Phương trình BESS (rời rạc, bước Δt)** [PROPOSAL; mô hình "bucket" chuẩn, INFERENCE]:

- `p_cmd` = setpoint đã kẹp vào `[−p_charge_max, p_discharge_max]` hiện tại.
- `p(t+Δt) = p(t) + (p_cmd − p(t))·(1 − e^(−Δt/τ))`, sau đó giới hạn bởi `ramp_w_per_s·Δt`.
- Sạc (`p < 0`): `soc += (−p)·η_c·Δt / e_nom`. Xả (`p > 0`): `soc −= p·Δt / (η_d·e_nom)`.
- `p_charge_max = p_rated · min(1, (soc_max − soc)/taper_band)`; tương tự cho xả gần `soc_min`. Nhiệt độ > ngưỡng → nhân hệ số giảm.
- Bộ đếm `e_charge`/`e_discharge` cộng dồn |p|·Δt theo chiều, Wh nguyên.
- Mất setpoint (watchdog bật, không ghi trong `watchdog_s`) → `p_cmd = 0` hoặc chế độ native. Watchdog tắt → giữ setpoint cũ (để kiểm `requires_native_fallback`).

Mô hình suy giảm (BLAST-Lite) **không** chạy trong virtual site thời gian thực; chỉ dùng trong backtest tối ưu (08).

**Nguồn sự thật về thanh ghi.** Virtual site **nạp cùng file register map YAML** của driver (07 §6.2) để mã hóa giá trị (scale, word order, sentinel). Để tránh "cùng lỗi hai phía": (1) mỗi map có tối thiểu một bộ **vector vàng** lấy từ thiết bị thật hoặc tài liệu hãng (07 §11.1 L1); (2) có chế độ "map lệch" cố ý (word order sai, scale sai) để kiểm driver phát hiện qua range/plausibility; (3) kết quả mô phỏng **không** nâng driver lên `VERIFIED_*` (D-07-13).

**Điều khiển và tiêm lỗi (REST của virtual site, chỉ ở mạng test).**

| Lỗi | Cách tạo | Kiểm cái gì (07 §11.3) |
|---|---|---|
| Mất liên lạc thiết bị | Dừng phản hồi / đóng TCP / Toxiproxy `timeout`, `down` | `BAD_COMM`, fallback, T-FR-INT-018 |
| Exception Modbus | Trả 01/02/03/04/06 theo thanh ghi | `BAD_CONFIG`, retry/backoff |
| Một client duy nhất (kiểu Huawei) | Từ chối kết nối thứ hai | Edge là master duy nhất (T-FR-INT-004) |
| Giá trị đóng băng | Giữ nguyên giá trị nhưng vẫn trả lời | Phát hiện `FROZEN` (F, K R-06) |
| Dữ liệu cũ / trễ | Toxiproxy `latency` + jitter | `UNCERTAIN_STALE`, ngân sách vòng ≤ 5 s |
| Alarm | Bật bit trong alarm word, tắt sau N s | Ánh xạ alarm, SOE |
| Timestamp sai thứ tự | `ts_src` của SOE/alarm đảo, lệch đồng hồ thiết bị (giờ địa phương như Huawei F-33) | Chuẩn hóa UTC, `UNCERTAIN_CLOCK` |
| Reset/quay vòng bộ đếm | Đặt `e_import` về 0 hoặc qua `R_wrap` | Sự kiện `COUNTER_RESET`, không tạo kWh âm |
| CT lắp ngược | Đảo dấu P công tơ | Phép thử dấu (T-FR-INT-016) |
| Ghi không tác dụng | Chấp nhận FC16 nhưng không đổi hành vi | `FAILED_NO_EFFECT` |
| Kẹp bởi BMS | Giảm DCL đột ngột | `APPLIED_CLAMPED` |
| Mất WAN/broker | Toxiproxy giữa edge và broker; dừng broker | Store-and-forward, backfill, `seq`, T-FR-INT-009 |
| Modbus RTU timing | Bộ chuyển USB-RS485 thật + virtual site ở chế độ RTU, hoặc thiết bị thật | Ngân sách polling (E F-03); Toxiproxy không áp dụng cho serial |

### 3.3 Bộ mô phỏng theo môi trường [PROPOSAL]

| Môi trường | Thành phần | Ghi chú |
|---|---|---|
| (a) Laptop dev | `docker compose`: 1–3 virtual site (pymodbus server API + mô hình §3.2) · edge thật (build local) · broker Mosquitto 2.1 (hoặc EMQX một node — BSL cho phép môi trường không production, F2-21) · cloud stack · 1 charger ảo (Monta web emulator hoặc script `ocpp` Python) · diagslave/ModbusPal cho thử nhanh | Profile PV sinh sẵn bằng pvlib, commit dạng CSV trong repo test để không cần gọi PVGIS khi chạy |
| (b) CI | Testcontainers [INFERENCE: thư viện Java phổ biến] khởi broker + virtual site + Toxiproxy · kịch bản tất định (seed, đồng hồ tăng tốc) · test hợp đồng (JSON Schema + Protobuf) · đêm: ma trận lỗi §3.2 · tuần: tải bằng "edge ảo" (chỉ phát payload theo hợp đồng 07 §7, không mô phỏng thiết bị) tới 1.000–10.000 kết nối (PoC-02) · c104/j60870 làm master 104 (P1) · SAP simulator cho nhiều charger (P1) | CI không gọi Internet (PVGIS) |
| (c) HIL lab | **Edge phần cứng thật** (PR-E-12) + thiết bị thật tối thiểu (07 §11.4: SmartLogger/EMMA, inverter, công tơ, 1 PCS/tủ BESS, 1 charger) + virtual site cho phần không có (BESS lớn, công tơ POC thứ hai) trên OT LAN · RS-485 thật · Toxiproxy/netem cho WAN 4G giả · master 104 giả · đo thời gian vòng giới hạn xuất end-to-end | Chỉ HIL/lab mới cấp `VERIFIED_LAB` |
| (d) Demo bán hàng | Tenant riêng "Demo – Mô phỏng"; virtual site + **edge ảo chạy trong cloud** (không phần cứng); phát lại các ngày điển hình (nắng, mây, mất lưới, vượt trần nhập); tài khoản chỉ đọc + một kịch bản lệnh sandbox; reset hằng đêm | Mọi màn hình, báo cáo, export mang nhãn "Mô phỏng" (D-07-13, K §6 #33); dữ liệu không vào KPI/benchmark thật; **mặt phẳng điều khiển của tenant demo không có route tới edge thật** |

**Ngôn ngữ của virtual site.** Đề xuất Python (pymodbus + pvlib) cho **công cụ test**, cô lập trong container, giao tiếp chỉ qua Modbus/OCPP/REST. Lý do: thư viện sẵn (pvlib không có bản Java tương đương [INFERENCE]), REST điều khiển dễ, không vào sản phẩm. Phương án B (thuần Java: digitalpetri/j2mod server + profile CSV sinh trước) giữ được một stack; chọn nếu đội không muốn duy trì Python. Đây không mâu thuẫn K R-22 (R-22 nói về runtime sản phẩm), nhưng cần ghi trong 06/11 [PROPOSAL].

### 3.4 Mô phỏng không chứng minh được gì

| Không chứng minh | Vì sao | Cần gì |
|---|---|---|
| Register map đúng với thiết bị thật | Map mô phỏng sinh từ cùng YAML (F2-38); diễn đàn mâu thuẫn (E F-06/07) | Vector vàng từ thiết bị, tài liệu hãng, lab |
| Quirk firmware | Thiết bị đã chứng nhận SunSpec vẫn lỗi (E F-11); "ghi không tác dụng" (E F-07); Easee TxDefault (E F-21) | Ma trận model × firmware, `VERIFIED_LAB/FIELD` |
| Thời gian đáp ứng thật | Ramp PCS, độ trễ logger, chu kỳ đo công tơ (E F-28) | Đo HIL: zero-export ≤ mục tiêu (T-FR-INT-017) |
| Giới hạn đồng thời/tài nguyên thiết bị | Một client, chu kỳ đọc ≥ 5 s (E F-04) — mô phỏng chỉ khi đã biết | Lab |
| Mòn NVM, watchdog thật | Hành vi ghi flash/RAM chưa có tài liệu (Q-E-05) | Hỏi hãng, thử dài ngày |
| Điện (dấu CT thật, pha, PF) | Mô phỏng không có lỗi lắp đặt chưa biết | Phép thử dấu khi commissioning |
| Hành vi bảo vệ (BMS/PCS/rơ-le) | Ngoài phần mềm (K §6 #14) | Không bao giờ kiểm bằng mô phỏng; thử nghiệm của hãng |
| Mạng 4G thật, NAT, broker dưới churn thật | Toxiproxy chỉ xấp xỉ | Pilot hiện trường, PoC-02 |
| Kết quả kinh tế | Profile tải Mỹ (ComStock) ≠ C&I VN | Dữ liệu pilot VN; nhãn "Mô phỏng" |

### 3.5 Dữ liệu mẫu cho virtual site và backtest

| Nguồn | Dùng cho | Giấy phép (qua kết quả tìm kiếm) | Đánh giá |
|---|---|---|---|
| PVGIS TMY (qua pvlib) | Profile PV theo tọa độ VN | Điều khoản PVGIS chưa đọc [UNKNOWN] | **Dùng**; ghi phiên bản PVGIS/SARAH-3 |
| NREL ComStock/EULP | Hình dạng tải thương mại 15 phút | Mâu thuẫn: "ComStock License" vs CC BY 4.0 | Chỉ tham khảo hình dạng; khí hậu/biểu giá Mỹ; kiểm license trước khi đóng gói vào demo |
| Pecan Street | Tải hộ gia đình | Đại học phi thương mại; thương mại trả phí | **Không dùng** cho sản phẩm/demo |
| OPSD household | Tải/PV hộ châu Âu | Không có kết quả [UNKNOWN] | Kiểm sau |
| Dữ liệu pilot VN (đã ẩn danh, có đồng ý) | Profile thật | Hợp đồng khách | **Ưu tiên** khi có |
| Profile tổng hợp tự sinh | Demo | Của ta | Mặc định cho demo; ghi "Mô phỏng" |

### 3.6 Edge↔cloud: so sánh giao thức

| Lựa chọn | Điểm mạnh | Điểm yếu | Kết luận |
|---|---|---|---|
| **MQTT 5** (schema riêng) | Outbound-only qua NAT/4G; QoS 1; Session Expiry; Message Expiry khớp `expires_at` (E F-13); Response Topic + Correlation Data cho business ACK (F2-31); Content Type, Payload Format Indicator, User Properties; Reason Codes; shared subscription cho ingest; topic alias giảm byte; mọi broker lớn và cloud hỗ trợ (F2-29) | Phải tự định nghĩa hợp đồng; shared subscription/expiry khác nhau đôi chút giữa broker | **Chọn** (giữ K §6 #20) |
| MQTT 3.1.1 | Hỗ trợ rộng nhất (NATS chỉ có 3.1.1, F2-28) | Không expiry tin, không reason code, không correlation data → phải nhét vào payload; `cleanSession` thô | Chỉ làm tương thích ngược, không dùng |
| Sparkplug B 3.0 | Chuẩn ISO/IEC (F2-32); birth/death, hệ SCADA (Ignition) | QoS 0 dữ liệu; không ngữ nghĩa ack/expiry/idempotency cho lệnh (E); xung đột 2.2/3.0; broker "aware" | **Đầu ra phụ P2** (giữ) |
| AMQP 1.0 | Ngữ nghĩa giao nhận mạnh, link credit | Client edge nặng hơn; ít broker IoT dùng; không cần thêm | Không |
| HTTPS batch upload | Đơn giản, qua mọi proxy; tốt cho file lớn | Không có downlink đẩy; polling lệnh trễ | **Dùng bổ sung** cho OTA, gói driver, backfill rất lớn (pre-signed URL), enroll |
| gRPC streaming | Hợp đồng protobuf, hai chiều | HTTP/2 dài hạn qua 4G/NAT khó; không broker fan-out; tự làm reconnect/queue | Không cho uplink chính |
| WebSocket (JSON-RPC kiểu OpenEMS) | Hai chiều, đã chạy ở OpenEMS (F2-30) | Point-to-point tới backend có trạng thái; tự làm QoS, fan-out, cân bằng tải | Không (nhưng phải có adapter nếu dùng OpenEMS Edge) |
| CoAP | Nhẹ, UDP | Thiết bị bị hạn chế mới cần; NAT/UDP 4G phức tạp | Không |
| DDS | Realtime LAN | Không hợp WAN đa tenant | Không |
| OPC UA PubSub over MQTT | Mô hình thông tin chuẩn | Không có companion spec PV/BESS (E F-14); nặng | Không (chỉ northbound khi khách yêu cầu) |
| Kafka trực tiếp từ edge | Log bền | Lộ broker, client nặng, cần TCP ổn định, kém với nhiều topic (F2-33) | **Không** |
| MQTT over QUIC (NanoMQ/EMQX) | Kết nối lại nhanh trên mạng di động | Chưa chuẩn OASIS [INFERENCE]; ràng buộc broker | Theo dõi, không MVP |

**Hệ sinh thái tham chiếu**

| Hệ | Cách làm (đã thấy) | Bài học |
|---|---|---|
| OpenEMS | JSON-RPC qua WebSocket, Backend `Edge.Websocket` cổng 8081, `edgeRpc` (F2-30) | Nếu ADR-07 chọn OpenEMS Edge: viết bundle uplink theo hợp đồng MQTT 07, **không** chạy OpenEMS Backend làm ingest (Q-E2-04) |
| Victron | FlashMQ trên GX, cầu D-Bus→MQTT, keepalive, kết nối máy chủ MQTT của VRM (F2-08) | MQTT làm kênh đám mây cho thiết bị năng lượng là thực tiễn đã có; keepalive theo yêu cầu để giảm lưu lượng |
| Huawei SmartLogger | Dữ liệu lên FusionSolar; bên thứ ba dùng FTP CSV hoặc Modbus TCP (F2-07) | Không phụ thuộc kênh cloud của hãng; edge của ta đọc Modbus |
| EVerest | MQTT giữa các module trong trạm (F2-12) | MQTT cũng hợp làm bus nội bộ edge (tùy chọn) |
| AWS IoT Core | MQTT 3.1.1/5, shared subs, expiry, request/response (F2-29) | Hợp đồng của ta chuyển sang được nếu sau này cần |
| Azure IoT Hub / Event Grid | IoT Hub: topic cố định, MQTT 5 deprecated; Event Grid: MQTT 5 tùy topic (F2-29) | Không gắn vào topic/SDK độc quyền |
| Google Cloud IoT Core | Đóng 16/08/2023 (F2-29) | Rủi ro managed service; giữ hợp đồng broker-agnostic, có lối thoát |

### 3.7 Quyết định uplink/downlink chi tiết [PROPOSAL]

| Lớp tin | Kênh | QoS | Retained | Thuộc tính MQTT 5 | Bền vững / idempotency |
|---|---|---|---|---|---|
| Telemetry C1–C4 | `ems/v1/{edge_id}/up/telemetry/{stream}` | 1 | Không | Content Type `application/x-protobuf+zstd`; User Property `schema`; topic alias | `seq` theo stream; cloud ack **sau commit DB** (06 ADR-05); edge xóa ≤ `ack_seq` |
| Backfill | `…/up/backfill` | 1 | Không | Như trên; edge giới hạn tốc độ | Như trên; > ngưỡng (ví dụ > 24 h dữ liệu) → HTTPS upload file + tin báo trên MQTT (P1) |
| Sự kiện/alarm/SOE | `…/up/event` | 1 | Không | — | `event_id` UUIDv7 |
| Trạng thái edge | `…/up/state` | 1 | **Có**; Will = offline (retained) | Will Delay Interval vài giây để tránh nhấp nháy [INFERENCE] | Bản mới nhất thắng theo `ts` |
| Lệnh | `…/down/cmd` | 1 | **Không** | Message Expiry = `expires_at − now`; Correlation Data = `command_id`; Response Topic = `…/up/cmd-ack` (edge **chỉ** chấp nhận đúng topic này, bỏ qua giá trị khác) | `command_id` idempotency; `seq` + chữ ký chống replay (07 §8.2) |
| Ack lệnh | `…/up/cmd-ack` | 1 | Không | Correlation Data echo | State machine 07 §8.4 |
| Config mong muốn | `…/down/config` | 1 | **Có** | — | `config_version` + chữ ký; edge báo reported trong `state` |
| Firmware/gói driver | HTTPS pre-signed URL; MQTT chỉ mang con trỏ + hash + chữ ký | — | — | — | A/B, rollback (PR-E-14) |

**Phiên.** Edge kết nối với Session Expiry hữu hạn (ví dụ 1–24 h) để lệnh còn hạn được giao khi rớt mạng ngắn; lệnh hết hạn bị broker loại (Message Expiry). Cloud consumer dùng shared subscription với session bền. Keepalive 30–60 s trên 4G [INFERENCE; cần đo ở pilot].

**Kích thước lô.** Mosquitto 2.1 mặc định `max_packet_size` 2 MB (F2-25); broker khác có giới hạn riêng. Đề xuất lô ≤ 256 KB sau nén, cấu hình được.

**Bảo mật.** mTLS mỗi edge; `client_id` = CN/SAN = `edge_id`; ACL theo mẫu `ems/v1/${client_id}/up/#` (chỉ publish) và `ems/v1/${client_id}/down/#` (chỉ subscribe); cấm edge subscribe wildcard; dịch vụ cloud có danh tính riêng theo mặt phẳng (06 ADR-01/§12). Vì topic không chứa tenant (K R-12), **không có wildcard xuyên tenant** để chặn ở topic; cô lập tenant nằm ở registry edge→site→tenant của ingest + RLS (K §6 #29). Trình duyệt **không bao giờ** kết nối broker.

### 3.8 Ước lượng lưu lượng

**Giả định** [PROPOSAL, ghi rõ]: site 200–500 điểm; tổng hợp tại nguồn theo K §6 #19. Ba kịch bản mẫu/s mỗi site:
- Thấp: 200 điểm × 1/60 s = **3,3 mẫu/s**.
- Trung bình: 50 điểm C1 (5 s) + 450 điểm C2 (60 s) = 10 + 7,5 = **17,5 mẫu/s**.
- Cao: 500 điểm × 1/5 s = **100 mẫu/s**.
- Số **tin** MQTT (đã gộp lô): C1 mỗi 5 s (0,2), C2 mỗi 60 s (0,017), C3/C4 mỗi 300 s (≈ 0,007), state/event ≈ 0,01 → **≈ 0,23–0,26 tin/s/site**, gần như không đổi theo số điểm.
- Byte: mục tiêu ≤ 15 B/mẫu sau nén (07 §7.3).

| Quy mô | Mẫu/s (thấp / TB / cao) | Tin MQTT/s thường | Đỉnh backfill (×10) | Băng thông ingest (TB / cao) |
|---|---|---|---|---|
| 100 site | 333 / 1.750 / 10.000 | ≈ 25 | ≈ 250 | 26 KB/s / 150 KB/s |
| 1.000 site | 3.333 / 17.500 / 100.000 | ≈ 250 | ≈ 2.500 | 263 KB/s / 1,5 MB/s |
| 10.000 site | 33.333 / 175.000 / 1.000.000 | ≈ 2.500 | ≈ 25.000 | 2,6 MB/s / 15 MB/s |

Đối chiếu: 06 dùng 35 mẫu/s/site (≈ 35.000 mẫu/s và ≈ 260 tin/s ở 1.000 site) và PoC-02 2.600/26.000 tin/s ở 10.000 edge — **khớp** với bảng trên. Lưu lượng 4G mỗi site (TB): 17,5 × 15 B ≈ 263 B/s ≈ 23 MB/ngày ≈ 0,7 GB/tháng, chưa tính overhead TLS/MQTT (cao: ≈ 3,9 GB/tháng). [INFERENCE: số học]

**Hệ quả.** Ở mọi quy mô đến 10.000 site, số **tin** (≤ 25.000/s đỉnh) nằm trong tầm một cụm MQTT broker nhỏ; nút thắt là **ghi TSDB** (mẫu/s), không phải messaging (PoC-01 của 06).

### 3.9 Broker: so sánh [PROPOSAL dựa trên FACT F2-21…F2-29]

| Broker | Cluster | MQTT 5 | Giấy phép (2026) | Auth/ACL | Bridge/rule | Vận hành | Đánh giá |
|---|---|---|---|---|---|---|---|
| EMQX ≥ 5.9 | Có (cần license thương mại) | Có | BSL 1.1; một node miễn phí **trừ** khi tích hợp vào sản phẩm bán cho bên thứ ba (F2-21) | X.509, JWT, HTTP, SQL/NoSQL (F2-37 nguồn tổng hợp) | Rule engine SQL; Kafka "built-in" (F2-37) | Erlang | **Ứng viên thương mại #1** (nhiều tính năng nhất); bắt buộc báo giá + pháp lý |
| EMQX ≤ 5.8 (Apache 2.0) | Có | Có | Apache 2.0 | Như trên (một phần) | WebHook, MQTT bridge | Erlang | **Không**: nhánh sẽ hết hỗ trợ [INFERENCE] |
| HiveMQ Enterprise | Có | Có | Thương mại | Extension SDK **Java** | Kafka extension (kiến thức nền) | JVM — hợp đội | **Ứng viên thương mại #2**; hợp đội Java |
| HiveMQ CE | **Không** (F2-23) | Có | Apache 2.0 | Extension Java | — | JVM | Dev/CI; pilot một node |
| Mosquitto 2.1 | Không (kiến thức nền) | Có | EPL/EDL [INFERENCE] | Plugin (dynamic security), cert-as-username [INFERENCE] | Bridge MQTT | Rất nhẹ | Dev/CI/lab; **pilot ≤ ~100–200 edge** một node + dự phòng nóng (PR-E2-06) |
| VerneMQ | Có | Có | Mã Apache 2.0; nhị phân EULA trả phí (F2-24) | Plugin | Webhooks | Erlang; tự build | **Bỏ khỏi shortlist** (thay đổi so với 06 ADR-04) trừ khi mua subscription |
| RabbitMQ 4.x MQTT | Có (quorum queue) | Có (trừ QoS 2; shared subscription có thể không) (F2-27) | MPL-2.0 [INFERENCE] | Plugin auth HTTP/LDAP, cert | Consumer AMQP/streams đọc thẳng queue | Erlang; đội có thể đã quen | **Ứng viên mở #3** cho PoC-02: ingest đọc queue bằng AMQP thay shared subscription |
| NanoMQ | Không (edge) | Có | MIT (F2-26) | Cơ bản | Bridge MQTT/QUIC | Rất nhẹ | **Edge** nếu cần broker cục bộ; không làm cloud |
| NATS (MQTT gateway) | Có | **Không** (chỉ 3.1.1, F2-28) | Apache 2.0 [INFERENCE] | NATS accounts | JetStream | Go | **Không** cho biên MQTT |
| AWS IoT Core / Azure Event Grid | Managed | Có | Dịch vụ | Cert/X.509 | Rule → dịch vụ cloud | Không vận hành | Loại ở MVP (hosting VN, 06 AC-08); giữ làm phương án di chuyển |
| Azure IoT Hub | Managed | Deprecated (F2-29) | Dịch vụ | — | — | — | **Không** (topic cố định) |

### 3.10 Messaging nội bộ cloud

| Phương án | Hợp lúc nào | Không hợp | Đánh giá cho MVP |
|---|---|---|---|
| Broker → ingest trực tiếp (shared subscription hoặc queue AMQP) + ack-sau-commit | Một consumer telemetry; edge buffer 7–30 ngày là log bền (06 ADR-05) | ≥ 3 consumer cần đọc lại luồng | **Chọn** |
| PostgreSQL transactional outbox + relay polling | Sự kiện nghiệp vụ (lệnh, alarm, plan) ~ vài/s | Telemetry | **Chọn** cho sự kiện; `LISTEN/NOTIFY` chỉ làm **tín hiệu đánh thức** relay, không làm kênh dữ liệu (payload < 8.000 B, không bền — F2-34) |
| Kafka (Apache 2.0) | Nhiều consumer, phát lại, phân vùng theo khóa | Thêm cụm stateful, kỹ năng | Ngưỡng nâng cấp (dưới) |
| Redpanda | API Kafka, vận hành gọn | BSL: cấm cung cấp như dịch vụ streaming (F2-36) — ta không bán streaming nhưng cần pháp lý | Ứng viên khi nâng cấp |
| NATS JetStream | Bus nhẹ, bền | Không làm được biên MQTT 5 (F2-28); thêm runtime | Không ở MVP |
| RabbitMQ streams | Nếu RabbitMQ đã là broker MQTT | — | Có lý **chỉ** khi chọn RabbitMQ ở biên |
| Redis/Valkey Streams | Hàng đợi tạm | Cache trong 06 là không bền | Không cho sự kiện nghiệp vụ |

**Ngưỡng nâng cấp sang Kafka/Redpanda** (bổ sung cho 06 ADR-05, PROPOSAL): bất kỳ điều kiện nào sau đây kéo dài ≥ 1 tuần: (1) ≥ 3 consumer độc lập cần đọc lại telemetry; (2) > 200.000 mẫu/s duy trì (≈ kịch bản TB ở ~10.000 site) **và** ingest cần tách khỏi tốc độ ghi DB; (3) đỉnh backfill khiến backpressure giữ edge chờ > 1 h; (4) khách cần luồng xuất có phát lại; (5) relay outbox trễ p95 > 5 s. Khi đó đặt log giữa broker và ingest (bridge của broker hoặc connector), **hợp đồng edge không đổi**.

### 3.11 Live update cho frontend

| Phương án | Đánh giá |
|---|---|
| **SSE** | **Chọn** (giữ 06 ADR-03): một chiều, HTTP thường, Spring hỗ trợ; vé ngắn hạn ≤ 60 s; ghi đi qua REST có PDP/audit |
| WebSocket | Chỉ khi có nhu cầu hai chiều thật; không dùng cho lệnh |
| MQTT over WebSocket tới trình duyệt | **Loại**: trình duyệt không trình được chứng chỉ client (F2-35) → phải mở auth token trên broker của mặt phẳng điều khiển; ACL theo người dùng phức tạp; tăng bề mặt tấn công; phá tách mặt phẳng (K §6 #26). Nếu sau này cần (ví dụ khách muốn subscribe trực tiếp), dùng **broker/listener riêng** chỉ đọc, dữ liệu đã chuẩn hóa, token ngắn hạn (Q-06-04) |

---

## 4. Hệ quả thiết kế cho sản phẩm

| ID | Đề xuất [PROPOSAL] | Ưu tiên | Module | Căn cứ |
|---|---|---|---|---|
| PR-E2-01 | **Virtual site** theo §3.2 là công cụ test chuẩn: nạp register map YAML của driver, mô hình PV/tải/BESS/POC, REST tiêm lỗi; kèm vector vàng từ thiết bị thật | P0 (trước Gate M1) | M-INT | F2-01, F2-38, 07 §11 |
| PR-E2-02 | Virtual site dựng trên **pymodbus server API** (khóa phiên bản; không dùng app simulator cũ) + profile pvlib sinh sẵn; phương án B Java (digitalpetri/j2mod) nếu ADR quyết một stack | P0 | M-INT | F2-01, F2-03, F2-18 |
| PR-E2-03 | Toxiproxy trong CI cho mọi kết nối TCP (Modbus TCP, MQTT, OCPP); RTU kiểm ở HIL | P0 | M-INT | F2-20 |
| PR-E2-04 | Charger ảo: SAP simulator cho tải/scale, script `ocpp` (MIT) cho quirk; CSMS đối chứng SteVe (1.6, chỉ lab vì thiếu Security Whitepaper) và CitrineOS (2.0.1) | P1 | M-EV | F2-10–F2-12 |
| PR-E2-05 | Master IEC 104 giả: c104 (Python, GPLv3, chỉ công cụ test) hoặc j60870 (Java). Nếu edge sản phẩm nhúng thư viện 104/61850 → **mua giấy phép thương mại** (MZ Automation/OpenMUC) hoặc viết riêng | P1 | M-GRID | F2-15 |
| PR-E2-06 | Broker: hợp đồng broker-agnostic. PoC-02 so **EMQX Enterprise** (license) vs **HiveMQ Enterprise** (license) vs **RabbitMQ 4.x** (mở). VerneMQ ra khỏi shortlist. Pilot ≤ ~100–200 edge cho phép Mosquitto 2.1 một node + standby, với tiêu chí thoát rõ | P0 (quyết trước MVP) | M-INT | F2-21–F2-27 |
| PR-E2-07 | Lệnh dùng thuộc tính chuẩn MQTT 5: Message Expiry, Correlation Data = `command_id`, Response Topic cố định; Content Type/Payload Format Indicator **chuẩn** thay User Property `content-type` | P0 | M-INT, M-BESS | F2-31 |
| PR-E2-08 | Không Kafka ở MVP; outbox + relay polling; NOTIFY chỉ đánh thức; ngưỡng nâng cấp §3.10 | P0 | M-INT | F2-34, 06 ADR-05 |
| PR-E2-09 | File lớn (firmware, gói driver, backfill > 24 h) qua HTTPS pre-signed URL; MQTT chỉ mang con trỏ + hash + chữ ký | P1 | M-INT | §3.7 |
| PR-E2-10 | Tenant demo "Mô phỏng": edge ảo trong cloud, không route tới edge thật, nhãn bắt buộc, reset hằng đêm, không dùng dữ liệu Pecan Street | P1 | M-ADV, M-SEC | F2-19, D-07-13 |
| PR-E2-11 | Kế hoạch lối thoát managed: hợp đồng chạy được trên AWS IoT Core/Azure Event Grid; không dùng tính năng broker riêng cho logic nghiệp vụ | P1 | M-INT | F2-29 |

---

## 5. Evidence ledger

Mọi URL "(qua kết quả tìm kiếm)"; không trang nào được mở trực tiếp.

| # | Claim | Source URL | Source type & date | Excerpt/paraphrase | Confidence | Conflicting evidence | Design implication |
|---|---|---|---|---|---|---|---|
| E2-01 | pymodbus simulator: JSON config, datastore, REST; bị thay từ 3.9 tới 4.0 bằng simulator3 (SimData/SimDevice) | https://pymodbus.readthedocs.io/en/dev/source/library/simulator/config.html ; https://pymodbus.readthedocs.io/en/v3.8.6/source/simulator.html ; https://pymodbus.readthedocs.io/en/v3.14.0/_sources/source/simulator3.rst.txt ; https://pymodbus.readthedocs.io/en/dev/source/simulator/datamodel.html | Tài liệu dự án, nhiều phiên bản | "beginning with v3.9.0 and ending with v4.0.0, this simulator will be replaced" | High | Chữ ký SimData đổi giữa 3.8 và 3.11+ | Dùng server API, khóa phiên bản |
| E2-02 | pymodbus BSD-3; 3.14.0 ngày 2026-07-12 | https://www.piwheels.org/project/pymodbus/ ; https://pepy.tech/projects/pymodbus | Mirror PyPI / thống kê | 3.14.0 released 2026-07-12 | Med | pepy ghi 3.13.0 mới nhất | Theo dõi phiên bản |
| E2-03 | modbus-tk LGPL, có simulator + RPC | https://github.com/bbarcklay/modbus-tk ; https://depscope.dev/pkg/pypi/modbus_tk | Mirror + trang phụ thuộc | "ready-to-use simulator with RPC interface" | Med | 1.1.2 vs 1.1.5 | Không cần |
| E2-04 | diagslave freeware FieldTalk; ModbusPal GPL, 247 slave | https://www.modbusdriver.com/index.php/diagslave.html ; https://modbuspal.sourceforge.net/ | Trang hãng / dự án | "simple command line based Modbus slave simulator" | Med–High | diagslave 3.2 (OE) vs 3.5 | Công cụ tay |
| E2-05 | j2mod Apache 2.0 fork jamod; `io.openems:j2mod`; digitalpetri Java 17+, TCP Security; EPL-2.0 (thứ cấp) | https://sourceforge.net/p/j2mod ; https://central.sonatype.com/artifact/io.openems/j2mod ; https://jitpack.io/p/digitalpetri/modbus ; https://central.sonatype.com/artifact/nl.basjes.modbus/modbus-api-digitalpetri/ | Trang dự án, Maven Central | "fork of the jamod… Apache 2 license" | Med | SourceForge ghi cả BSD | Thư viện Java cho edge/sim |
| E2-06 | sunspec-sim MIT; sunspec-device Apache-2.0; go-sunspec 112 model | https://github.com/emdem/sunspec-sim ; https://github.com/nielsbasjes/sunspec-device ; https://github.com/otfabric/go-sunspec | README GitHub | "split from the rest of the sunspec tooling" | Med | — | Không có simulator SunSpec chính thức |
| E2-07 | pysunspec2 Apache 2.0, 1.2.1–1.3.5 | https://mynixos.com/nixpkgs/package/python313Packages.pysunspec2 ; https://code.ornl.gov/nix/nixpkgs/-/commit/e6c75a2a128206801aaec65b6c1568e1e1d4823a | Đóng gói nixpkgs | "Python library for interfacing with SunSpec devices" | Med (thứ cấp) | Phiên bản khác nhau | Nguồn model cho sinh chuỗi SunS |
| E2-08 | OpenEMS Simulator.EssSymmetric.Reacting / GridMeter.Reacting / Datasource.CSV; Simulated ESS C-rate 1 (2022.10) | https://openems.github.io/openems.io/openems/latest/simulation/realtime.html ; https://openems.github.io/openems.io/openems/latest/gettingstarted.html ; https://zenodo.org/records/7145189 ; https://github.com/OpenEMS/openems/issues/1507 ; https://community.openems.io/t/simulation-openems-with-my-own-data-csv-file/2444 | Tài liệu + release + issue + forum | "Simulates the State of Charge of a ess device" | Med–High | Tutorial lỗi thời; caveat 15 phút từ một bài forum (thread chính xác chưa chắc) | Chỉ test controller |
| E2-09 | OpenEMS Backend↔Edge: JSON-RPC qua WebSocket, cổng 8081, `edgeRpc` | https://openems.github.io/openems.io/javadoc/io/openems/backend/edgewebsocket/EdgeWebsocketImpl.html ; https://openems.github.io/openems.io//openems/latest/component-communication/index.html ; https://community.openems.io/t/error-when-connecting-the-edge-to-backend/787 ; https://dhub.cyberranges.com/r/openems/backend-edge | Javadoc, docs, forum, Docker page | "Send an authenticated JSON-RPC Request to an Edge via Websocket" | High | — | Cần adapter MQTT nếu dùng OpenEMS Edge |
| E2-10 | Venus OS dùng FlashMQ + dbus-flashmq; keepalive; kết nối MQTT VRM | https://github.com/victronenergy/dbus-flashmq ; https://communityarchive.victronenergy.com/questions/162746/simpler-local-mqtt-usage.html | README + forum | "FlashMQ, the MQTT Broker used on Venus OS" | Med | Hành vi keepalive đổi theo firmware 3.20 | MQTT là thực tiễn ngành |
| E2-11 | Mô phỏng Victron qua velib dbusdummyservice, multiplus emulator; demo mode hạn chế | https://communityarchive.victronenergy.com/questions/197508/simulate-multi-rs.html ; https://communityarchive.victronenergy.com/questions/80752/demo-mode-not-showing-all-tiles.html | Forum | "dbusdummyservice.py… simple service on D-Bus" | Low | — | Không ưu tiên |
| E2-12 | Không có emulator Huawei; huawei-solar-lib; proxy cache một kết nối | https://github.com/wlcrs/huawei-solar-lib ; https://github.com/norbim1/sun2000-modbus-cache ; https://github.com/topics/sun2000 | README GitHub | "one connection to the inverter, unlimited clients" | Med (vắng mặt = chưa tìm thấy) | — | Tự sinh từ map |
| E2-13 | SmartLogger: tích hợp thứ ba qua FTP CSV hoặc Modbus TCP; lên FusionSolar; giao thức 104/103/DL/T645 | https://support.spacewell.com/hc/en-001/articles/28356570657436 ; https://knowledge.ampere.cloud/en/huawei-smartlogger-1000-3000-per-passthrough-an-den-amperecloud-log-anbinden ; https://www.estg.eu/pl-pl/p/02312SCU-017 | KB bên tích hợp + nhà phân phối | "FTP/SFTP generic gateway… 300 seconds" | Med | — | Không có MQTT của hãng |
| E2-14 | SDM630 emulator chỉ qua ESPHome forum; evcc demo meter cố định, demo.yaml động | https://akkudoktor.net/t/sdm630-emulator-fuer-deye-sun-xxk-sg04-mqtt-deye-gateway/24950 ; https://docs.evcc.io/en/meters/demo-meter ; https://docs.evcc.io/en/meters/demo-battery.md | Forum + docs | "meter with a fixed set of values" | Low–Med | — | Tự dựng công tơ ảo |
| E2-15 | SAP simulator Node.js, Apache-2.0, OCPP-J; bài báo nói chỉ 1.6 | https://redirect.github.com/SAP/e-mobility-charging-stations-simulator ; https://oosmetrics.com/repo/SAP/e-mobility-charging-stations-simulator ; https://s3.eurecom.fr/docs/vehiclesec25_boussaha.pdf | README mirror, aggregator 06/2026, bài báo 2025 | "simulate and scale a set of charging stations" | Med | Tag `ocpp20` vs bài báo "only 1.6" | Xác minh 2.0.1 trước khi dùng |
| E2-16 | `ocpp` Mobility House MIT; 1.6 + 2.0.1; docs CC BY-ND | https://pypi.org/project/ocpp/ ; https://dfsg-new-queue.debian.org/reviews/python-ocpp | PyPI, Debian review | "OCPP 1.6 (errata v4), OCPP 2.0.1… supported" | High | — | Viết CP ảo có quirk |
| E2-17 | SteVe GPL, OCPP 1.2–1.6, chưa Security Whitepaper; SteVe OCPP Pro chứng nhận 1.6 (07/2026) | https://github.com/rwth-i5-idsg/steve ; https://ost.ecosyste.ms/projects/64142 ; https://openchargealliance.org/wp-content/uploads/2026/07/Certificate_OCA.0016.1261.CSMS_Powerfill.pdf | README + aggregator + chứng nhận OCA | "doesn't support the OCPP-1.6 security whitepaper yet" | Med–High | Phiên bản GPL chỉ từ bên thứ ba | Chỉ lab |
| E2-18 | CitrineOS LF Energy, 1.6/2.0.1; 1.3.0 smart charging + OCPI | https://lfenergy.org/projects/citrineos/ ; https://lfenergy.org/?p=8992 ; https://www.electronicspecifier.com/?p=33285 | Trang LF + báo (2024) | "OCPP 1.6 and 2.0.1 compliant" | Med | Giấy phép chưa thấy | CSMS đối chứng 2.0.1 |
| E2-19 | EVerest SIL/HIL; module giao tiếp qua MQTT; OCPP 1.6/2.0.1 | https://lfenergy.org/lf-energy-summit-2023-recap-revolutionizing-ev-charging-with-everest-a-breakthrough-operating-system/ ; https://www.mintlify.com/EVerest/everest-core ; https://mintlify.wiki/EVerest/everest-core/quickstart | LF recap 2023 + mirror docs | "modules communicate through MQTT brokers" | Med | — | Charger ảo trung thực |
| E2-20 | Monta emulator 1.6/2.0.1 web; MicroOcpp WASM; oglimmer Apache-2.0; Solidstudio VCP Apache-2.0 | https://monta.com/en/?p=30014 ; https://github.com/matth-x/MicroOcpp ; https://github.com/oglimmer/scriptable-ocpp-chargepoint-simulator ; https://solidstudio.io/products/virtual-charge-point/ | Blog hãng, README | "hosted web version in the browser" | Med | — | Công cụ tay/demo |
| E2-21 | OpenLEADR py 2.0b không duy trì; openleadr-rs 3.1; chưa bản field-test | https://lfenergy.org/projects/openleadr/ ; https://tweedegolf.nl/en/blog/162/rust-meets-the-grid-building-openleadr-rs-for-real-world-demand-response/ | Trang LF + blog Tweede Golf | "Python based implementation of OpenADR 2.0b is currently unmaintained" | Med–High | Trang LF 2025 cũ nói còn duy trì | DR P2 dùng 3.x |
| E2-22 | Reference implementation OpenADR 3 chỉ cho thành viên; spec OpenAPI | https://www.openadr.org/openadr-3-0 | Trang Alliance | "available to OpenADR members only" | Med–High | — | Sinh code từ OpenAPI |
| E2-23 | EPRI client 2030.5 BSD-3; QualityLogic test thương mại | https://www.opensourceforu.com/2019/02/epri-open-source-software-accelerates-implementation-of-intelligent-distributed-energy-resources/ ; https://www.energy.ca.gov/publications/2020/certified-open-source-software-support-interconnection-compliance-distributed ; https://www.qualitylogic.com/wp-content/uploads/2017/01/QL_DataSheet_IEEE-2030-5-test-tools_011617.pdf | Báo 2019, CEC 2020, datasheet 2017 | "BSD 3-clause" | Med | — | P2 |
| E2-24 | lib60870 & libIEC61850: GPLv3 hoặc thương mại; 61850 bản 1.6.x | https://github.com/mz-automation/lib60870 ; https://github.com/mz-automation/libiec61850 ; https://git.enea.com/cgit/linux/meta-openembedded.git/plain/meta-networking/recipes-connectivity/libiec61850/libiec61850_1.6.1.bb | README + recipe Yocto | "dual licensed under the GPLv3 and a commercial license" | High | Mirror ghi chỉ GPL | License thương mại nếu nhúng |
| E2-25 | j60870 GPLv3 + độc quyền; client & server; 1.8.0 | https://openmuc.org/iec-60870-5-104 ; https://central.sonatype.com/artifact/org.openmuc/j60870 | Trang dự án + Maven | "sell j60870 under proprietary licenses" | High | — | Master 104 giả (Java) |
| E2-26 | c104 Python trên lib60870-C, GPLv3, mô phỏng SCADA/RTU | https://pypi.org/project/c104/1.17.1 ; https://pypi.org/project/c104 | PyPI | "simulate scada systems and remote terminal units" | High | Bản 2.0 không trích license | Master/slave 104 giả CI |
| E2-27 | QTester104 client 104 Qt | https://qtester104.sourceforge.net | Trang dự án | "client side… using the QT UI Framework" | Med | Giấy phép chưa thấy | Lab |
| E2-28 | pandapower BSD; HELICS BSD-3; mosaik LGPL-2.1; GridLAB-D BSD-style; PyPSA MIT; PyBaMM BSD-3 | https://arxiv.org/pdf/1709.06743 ; https://docs.helics.org/en/latest/developer-guide/tests.html ; https://wiki.openmod-initiative.org/wiki/Mosaik ; https://en.wikipedia.org/wiki/GridLAB-D ; https://docs.pypsa.org/latest/home/license/ ; https://science.ecosyste.ms/projects/34624 | Bài báo, docs, wiki, aggregator | "BSD-licensed power system analysis tool" | Med | OpenDSS chưa thấy; eELib binding GPL | Không MVP |
| E2-29 | BLAST-Lite BSD-3; suy giảm theo T, SOC, DOD, C-rate | https://www.nrel.gov/research/software/blast-lite--battery-lifetime-analysis-and-simulation-tool---lite ; https://pypi.org/project/blast-lite/ ; https://ost.ecosyste.ms/projects/303832 | Trang NREL, PyPI, aggregator | "fitted from public lab aging data" | Med–High | NREL/NLR đổi tên | Backtest 08 |
| E2-30 | pvlib get_pvgis_tmy; PVGIS 5.3 SARAH-3 2005–2023 phủ phần lớn châu Á | https://pvlib-python.readthedocs.io/en/latest/reference/generated/pvlib.iotools.get_pvgis_tmy.html ; https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/getting-started-pvgis/pvgis-user-manual_en ; https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/pvgis-releases/pvgis-53_pt | Docs + JRC | "API defaults to using all available years" | High | Giấy phép pvlib chưa thấy | Profile PV VN |
| E2-31 | Pecan Street: đại học phi thương mại; thương mại trả phí | https://www.pecanstreet.org/dataport/licenses ; https://www.pecanstreet.org/access/ | Trang chính thức | "no resale and no sub-license" | High | — | Không dùng cho demo |
| E2-32 | NREL EULP 15 phút; license "ComStock License" vs CC BY 4.0 | https://registry.opendata.aws/nrel-pds-building-stock/ ; https://catalog.data.gov/dataset/end-use-load-profiles-for-the-u-s-building-stock | Registry AWS + data.gov | "ComStock License and ResStock License" | Med | Hai license khác nhau | Kiểm trước khi đóng gói |
| E2-33 | Toxiproxy MIT, TCP-only, toxics qua HTTP API | https://awesome.ecosyste.ms/projects/github.com%2FShopify%2Ftoxiproxy ; https://dev.co/testing/open-source/toxiproxy | Aggregator | "Toxiproxy is TCP-only" | Med | — | Tiêm lỗi CI |
| E2-34 | EMQX 5.9 BSL 1.1; cluster cần license; grant một node trừ sản phẩm cho bên thứ ba; Change Date 4 năm | https://www.emqx.com/en/content/license-faq ; https://www.emqx.com/en/blog/adopting-business-source-license-to-accelerate-mqtt-and-ai-innovation ; https://docs.emqx.com/en/emqx/latest/deploy/license.md ; https://scancode-licensedb.aboutcode.org/emq-use-grant-for-bsl-1.1.LICENSE | FAQ + blog + docs hãng + LicenseDB | "clustering is not permitted by default in EMQX 5.9.0+" | High | — | License thương mại cho SaaS (Q-E2-01) |
| E2-35 | Kafka integration: Enterprise ở 5.2/5.6, "built-in" ở latest; benchmark 100k QoS1/s một node (5.1) | https://docs.emqx.com/en/emqx/v5.6/data-integration/data-bridge-kafka.html ; https://docs.emqx.com/en/emqx/latest/data-integration/data-bridge-kafka.md ; https://www.emqx.com/en/blog/mqtt-performance-benchmark-testing-emqx-kafka-integration | Docs + benchmark vendor | "single node… 100,000 QoS1 messages per second" | Med (vendor) | — | Đường lên Kafka sẵn |
| E2-36 | HiveMQ CE Apache 2.0, không cluster; CE 2025.5 | https://community.hivemq.com/t/cluster-support-in-community-edition-ce/737 ; https://www.mintlify.com/hivemq/hivemq-community-edition/deployment/binary ; https://hivemq.com/blog/hivemq-ce-2024-3-released | Forum nhân viên 2021–2023 + docs mirror + blog | "community edition does not support clustering" | Med–High | Forum cũ | CE chỉ dev/pilot |
| E2-37 | VerneMQ: mã Apache; nhị phân EULA trả phí từ 1.10; tự tuyên bố duy trì | https://vernemq.com/vernemq-licenses.html ; https://vernemq.com/blog/2019/11/26/vernemq-end-user-license-agreement.html ; https://newreleases.io/project/github/vernemq/vernemq/release/2.0.1 ; https://sponsors.ecosyste.ms/accounts/vernemq | Trang hãng + release note | "yearly usage fee… if you use these packages commercially" | High (license) / Low (duy trì) | Phí "yearly" vs "subscription" | Bỏ khỏi shortlist |
| E2-38 | Mosquitto 2.1.0 (01/2026): max_packet_size 2 MB, PROXY, bỏ TLS 1.1, deprecate acl_file | https://mosquitto.org/blog/2026/01/version-2-1-0-released/ ; https://projects.eclipse.org/projects/iot.mosquitto/releases/2.1/review | Blog dự án + Eclipse | "max_packet_size now defaults to 2,000,000 bytes" | High | — | Lô ≤ 256 KB |
| E2-39 | NanoMQ MIT, LF Edge, bridge QUIC | https://lf-edge.atlassian.net/wiki/spaces/LE/pages/15865096/Project+NanoMQ ; https://nanomq.io/docs/en/latest/quic/introduction.html | LF Edge wiki + docs | "Project license | MIT License" | Med–High | — | Broker edge tùy chọn |
| E2-40 | RabbitMQ MQTT 3.1/3.1.1/5.0; queue mỗi subscriber; native MQTT 3.12; giới hạn QoS 2 (+ shared subscription, bị cắt) | https://www.rabbitmq.com/docs/4.2/mqtt ; https://rabbitmq.com/blog/2023/03/21/native-mqtt ; https://www.rabbitmq.com/docs/3.13/mqtt | Docs + blog hãng | "supports MQTT versions 3.1, 3.1.1, and 5.0" | Med–High | Forum 2023 nói chưa có MQTT 5 (cũ) | Ứng viên mở PoC-02 |
| E2-41 | NATS: MQTT 3.1.1, cần JetStream, QoS 2 từ 2.10, giao QoS 0 | https://docs.nats.io/nats-server/configuration/mqtt ; https://docs.nats.io/learn/mqtt/ | Docs | "NATS implements MQTT v3.1.1" | Med–High | Tài liệu cũ nói không QoS 2 | Không làm biên |
| E2-42 | Redpanda Community BSL, cấm cung cấp như dịch vụ streaming; Apache sau 4 năm | https://docs.redpanda.com/streaming/24.2/get-started/licenses/ | Docs hãng | "cannot provide Redpanda as a commercial streaming or queuing service" | High | — | Pháp lý khi nâng cấp |
| E2-43 | AWS IoT Core MQTT 3.1.1/5; shared subs GA 04/2023; expiry; request/response | https://aws.amazon.com/about-aws/whats-new/2023/04/aws-iot-core-mqtt5-shared-subscriptions-cloudwatch-metrics ; https://aws.amazon.com/blogs/iot/introducing-new-mqttv5-features-for-aws-iot-core-to-help-build-flexible-architecture-patterns/ ; https://amazonaws.cn/en/new/2022/amazon-iot-announces-general-availability-for-version-5-of-mqtt-message-broker | Tin/blog AWS | "Shared Subscriptions… general availability" | High | "với một số khác biệt" chưa liệt kê | Lối thoát managed |
| E2-44 | Azure IoT Hub: topic cố định, MQTT 5 deprecated; Event Grid MQTT 5 GA | https://learn.microsoft.com/en-my/azure/iot/iot-mqtt-5-preview ; https://learn.microsoft.com/en-us/answers/questions/1665609/how-to-send-different-message-to-different-topics ; https://www.hivemq.com/blog/hivemq-cloud-vs-aws-iot/ ; https://learn.microsoft.com/azure/event-grid/mqtt-request-response-messages | Docs + Q&A Microsoft + blog | "IoT Hub MQTT 5 support (deprecated)" | Med–High | GA Event Grid từ mirror | Không gắn vào topic hãng |
| E2-45 | Google Cloud IoT Core đóng 16/08/2023 | https://www.techzine.eu/news/infrastructure/86481/google-cloud-discontinues-iot-core/ ; https://itpro.com/network-internet/internet-of-things-iot/368845/google-cloud-to-retire-iot-core-service-in-2023 | Báo công nghệ 2022 | "MQTT and HTTP bridges became unavailable" | High | — | Bài học portability |
| E2-46 | MQTT 5 Response Topic + Correlation Data; broker không sửa; responder tự publish | https://www.emqx.com/en/blog/mqtt5-request-response ; https://www.hivemq.com/blog/underutilized-mqtt-5-features-enhance-iot-data-flows/ ; https://dev.classmethod.jp/articles/aws-iot-core-mqtt-v5-request-response/ | Blog vendor | "broker does not change the Response Topic or Correlation Data" | High | — | PR-E2-07 |
| E2-47 | Sparkplug 3.0 ISO/IEC; 4.0 đang làm; QoS 0 mất dữ liệu; 2.2 vs 3.0 STATE | https://newsroom.eclipse.org/node/39823 ; https://flowfuse.com/blog/2026/06/mqtt-vs-sparkplug-b ; https://www.issoh.co.jp/tech/details/16864/ | Eclipse newsroom 12/2023; blog vendor 06/2026; bài kỹ thuật | "certified as an ISO/IEC international standard" | Med | Số 60–75% của vendor | Sparkplug P2 |
| E2-48 | Không nối thiết bị thẳng Kafka | https://www.hivemq.com/blog/streaming-iot-data-and-mqtt-messages-to-apache-kafka/ ; https://www.confluent.io/fr-fr/blog/iot-with-kafka-connect-mqtt-and-rest-proxy/ | Blog vendor (có lợi ích) | "Kafka clients require a stable TCP connection" | Med | — | MQTT ở biên |
| E2-49 | NOTIFY < 8.000 byte; queue 8 GB; không bền (thứ cấp) | https://access.crunchydata.com/documentation/postgresql16/16.0/sql-notify.html ; https://chat2db.ai/resources/blog/postgres-listen-notify-guide | Docs PostgreSQL (mirror) + blog | "must be shorter than 8000 bytes" | High / Med | "truncated" chỉ ở blog | NOTIFY chỉ đánh thức |
| E2-50 | Browser WebSocket chỉ TLS một chiều; ACL tối thiểu | https://thingsboard.io/docs/mqtt-broker/user-guide/mqtt-over-ws/ ; https://lavinmq.com/resources/mqtt/mqtt-security | Docs vendor | "only support one-way TLS" | Med | — | SSE, không MQTT tới trình duyệt |

---

## 6. Câu hỏi mở / UNKNOWN

| ID | Câu hỏi | Vì sao quan trọng | Cách kiểm chứng |
|---|---|---|---|
| Q-E2-01 | EMQX ≥ 5.9: SaaS của ta có thuộc ngoại lệ "integrating into a product or solution offered to third parties" không? Giá license Enterprise theo kết nối/node? | Chi phí và hợp lệ của ADR-04 | Đọc LICENSE trong repo EMQX + pháp lý + báo giá |
| Q-E2-02 | HiveMQ Enterprise: giá, điều khoản tự host ở VN, extension Kafka/PostgreSQL | So sánh PoC-02 | Báo giá |
| Q-E2-03 | RabbitMQ 4.x: danh sách đầy đủ "Limitations" MQTT 5 (shared subscription, message expiry, will delay), giấy phép hiện hành | Ứng viên mở | Đọc rabbitmq.com/docs/mqtt bản 4.2 + PoC |
| Q-E2-04 | Nếu ADR-07 chọn OpenEMS Edge: có sẵn component uplink MQTT không, hay phải viết bundle theo hợp đồng 07? | Chi phí ADR-07 | Đọc mã OpenEMS (`io.openems.edge.controller.api.mqtt` nếu có) |
| Q-E2-05 | SAP simulator có OCPP 2.0.1 chưa? Giấy phép Monta emulator, CitrineOS, EVerest, OpenLEADR | Chọn công cụ EV/DR | Đọc README/LICENSE từng repo |
| Q-E2-06 | Giấy phép pvlib, điều khoản dùng dữ liệu PVGIS cho demo thương mại | Demo tenant | Đọc LICENSE pvlib + điều khoản JRC |
| Q-E2-07 | Mosquitto 2.1: shared subscription, giới hạn kết nối/tin cho pilot 100–200 edge, cấu hình cert-as-username | Pilot PR-E2-06 | PoC nhỏ |
| Q-E2-08 | Có profile tải C&I Việt Nam công khai (nhà máy, tòa nhà) với giấy phép dùng được? | Demo/backtest thực tế | Hỏi EVN/đại học/đối tác pilot |
| Q-E2-09 | Keepalive và Session Expiry tối ưu trên 4G Việt Nam (NAT timeout của nhà mạng) | Ổn định kết nối, chi phí dữ liệu | Đo ở pilot |

---

## 7. Vấn đề gửi agent khác

| # | Gửi | Vấn đề | Đề xuất |
|---|---|---|---|
| X-E2-01 | Người viết 06 (ADR-04) | Shortlist "EMQX + HiveMQ, VerneMQ dự phòng" giả định có bản cluster miễn phí. Bằng chứng mới: EMQX ≥ 5.9 cluster cần license và grant một node có thể không áp cho SaaS (F2-21/22); HiveMQ CE không cluster (F2-23); VerneMQ nhị phân trả phí (F2-24) | Sửa ADR-04: (1) dự trù chi phí license broker; (2) thêm RabbitMQ 4.x làm ứng viên mở trong PoC-02; (3) bỏ VerneMQ; (4) cân nhắc cho phép Mosquitto 2.1 một node ở pilot ≤ 100–200 edge với tiêu chí thoát. Q-06-02 đã đúng hướng, nay có dữ kiện |
| X-E2-02 | Người viết 06 (ADR-05) | Đồng ý không Kafka. Bổ sung: NOTIFY chỉ làm tín hiệu đánh thức relay, không mang dữ liệu (< 8.000 B, không bền); nếu chọn RabbitMQ ở biên thì ingest đọc queue bằng AMQP thay shared subscription; ngưỡng định lượng theo §3.10 | Cập nhật ADR-05 + bảng §14 với ba kịch bản mẫu/s |
| X-E2-03 | Người viết 07 (§7.1) | User property `content-type` trùng với **thuộc tính chuẩn** Content Type và Payload Format Indicator của MQTT 5 | Dùng thuộc tính chuẩn; giữ User Property cho `schema`, `edge_seq` |
| X-E2-04 | Người viết 07 (§8) | Chưa nói cách dùng Correlation Data/Response Topic | Correlation Data = `command_id`; Response Topic cố định `…/up/cmd-ack`; edge bỏ qua Response Topic khác (chống lạm dụng ACL) |
| X-E2-05 | Người viết 07 (§11.2) | "Thư viện cụ thể [UNKNOWN]" cho Modbus/OCPP | Thay bằng bảng §3.1 (pymodbus, SAP simulator, `ocpp`, c104/j60870, Toxiproxy) và lưu ý giấy phép GPL chỉ cho công cụ test |
| X-E2-06 | Người viết 07/10 | Mọi lô MQTT phải ≤ giới hạn packet của broker (Mosquitto 2.1 mặc định 2 MB) | Thêm `max_batch_bytes` (đề xuất 256 KB) vào cấu hình edge |
| X-E2-07 | Người viết 06 (ADR-07) | OpenEMS Edge↔Backend là JSON-RPC/WebSocket (xác nhận). Simulator OpenEMS chỉ test controller, không test driver | Tiêu chí ADR-07 thêm: chi phí bundle uplink MQTT theo 07; kế hoạch test driver bằng virtual site ngoài |
| X-E2-08 | Người viết 11 (Lộ trình) | Virtual site + Toxiproxy là điều kiện trước Gate M1; HIL lab trước Gate M2; tenant demo P1 | Thêm mốc "Virtual site v1" ở Phase 0 |
| X-E2-09 | Người viết 10 (An toàn) | Tenant demo không được có route tới edge thật; c104/lib60870/j60870 GPL chỉ ở công cụ test, không trong image edge | Thêm kiểm tra SBOM/giấy phép trong CI |
| X-E2-10 | Người viết 13 (Rủi ro) | R: chi phí license broker; R: broker mã mở bị đổi license (tiền lệ EMQX 5.9); R: managed IoT bị khai tử (Google 2023); R: mô phỏng cho kết quả xanh giả | Gắn Q-E2-01…09 |
| X-E2-11 | Người viết 14 (Nguồn) | Cấp mã S-xxx cho E2-01…E2-50 | — |
| X-E2-12 | Người viết index | Thêm liên kết tới `15-simulators-and-messaging.md` | — |
