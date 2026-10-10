# E — Giao thức thiết bị và kiến trúc tích hợp EMS (Agent E)

[← Mục lục](../index.html) · [05 Domain](../05-domain-model.html) · [06 Kiến trúc](../06-system-architecture.html) · [07 Tích hợp](../07-device-integration.md) · [08 Tối ưu](../08-energy-optimization.md) · [10 An toàn](../10-security-and-reliability.md) · [13 Rủi ro](../13-open-questions-and-risks.md) · [14 Nguồn](../14-source-register.md)

- Người viết: Agent E (Device & Integration Architect). Ngày: 2026-10-10. Trạng thái: ghi chú nghiên cứu bản 1. Đây là đầu vào chính cho tài liệu 07, và một phần cho 05, 06, 08, 10.
- Phương pháp bằng chứng: môi trường **chặn tải trang trực tiếp** (WebFetch/curl). Mọi FACT mới trong file này lấy qua WebSearch, tức là nội dung tóm tắt hoặc snippet do công cụ tìm kiếm trả về cho đúng URL đó. Tất cả đều mặc định là **"(qua kết quả tìm kiếm)"**. Không datasheet hay tiêu chuẩn nào được đọc toàn văn trong phiên này. Bằng chứng về Huawei (Northbound, OAuth Connect, Modbus) lấy từ nghiên cứu FusionSolar trước: `docs/research/fusionsolar/04_ghi_chu_nghien_cuu/1_tong_quan/api_integration.md`, `architecture_security.md` và `2_phan_ra_san_pham/competitors_rebuild.md`. Những chỗ đó ghi "(nghiên cứu FusionSolar trước)".
- Tiêu chuẩn (IEC/IEEE/OCPP/OpenADR): chỉ ghi edition khi kết quả tìm kiếm nêu rõ. Không tuyên bố tuân thủ bất kỳ tiêu chuẩn nào.
- Quy ước mã trong file: phát hiện `F-NN`, đề xuất `PR-E-NN`, câu hỏi mở `Q-E-NN`, vấn đề chéo `X-E-NN`, dòng ledger `E-NN`.

---

## 1. Phạm vi & câu hỏi nghiên cứu

**Phạm vi.** Phần này bàn cách EMS (Energy Management System, hệ quản lý năng lượng) cho C&I đa site đọc dữ liệu và gửi lệnh tới PV inverter, hybrid inverter, PCS (Power Conversion System, bộ biến đổi công suất của BESS), BMS (Battery Management System), công tơ PCC (Point of Common Coupling, điểm đấu nối lưới), sạc EV, logger/controller của hãng, cloud của hãng, trung tâm điều độ (EVN) và chương trình DR (Demand Response, đáp ứng phụ tải). Phần này cũng xác định nhiệm vụ của edge gateway và đề xuất một hợp đồng dữ liệu chuẩn (canonical point/command contract). Ngoài phạm vi: code ứng dụng, thuật toán tối ưu (tài liệu 08) và chi tiết bảo mật (tài liệu 10). Hai phần này chỉ được nhắc ở chỗ giao với tích hợp.

**Câu hỏi nghiên cứu**

| ID | Câu hỏi |
|---|---|
| Q-E1 | Modbus TCP/RTU có những ràng buộc cứng nào (function code, giới hạn khung, địa chỉ, word order, scale, một master) quyết định thiết kế driver và ngân sách polling? |
| Q-E2 | Số hiệu model SunSpec nào thực sự đúng và còn hiệu lực (1, 101–103, 124, 2xx, 7xx, 80x)? Bao nhiêu thiết bị thật sự hỗ trợ SunSpec? |
| Q-E3 | Uplink edge→cloud nên dùng MQTT thuần, Sparkplug B hay OPC UA? |
| Q-E4 | Khi nào cần IEC 61850, IEC 60870-5-104, DNP3? Kết nối điều độ EVN cho site trung thế cần gì? |
| Q-E5 | BMS qua CAN: có chuẩn chung không? |
| Q-E6 | Sạc EV: OCPP 1.6J, 2.0.1, 2.1 khác nhau thế nào về smart charging và bảo mật? |
| Q-E7 | DR: OpenADR 2.0b/3.x và IEEE 2030.5 có liên quan tới Việt Nam không? |
| Q-E8 | Cloud API của Huawei, Sungrow, SMA, Solis, Growatt, Deye công bố gì? Đọc hay ghi? Giới hạn ra sao? |
| Q-E9 | Edge gateway phải làm gì? Vì sao vòng điều khiển nhanh phải chạy ở edge? Tham chiếu OpenEMS và các controller thương mại. |
| Q-E10 | Hợp đồng point/command chuẩn trông thế nào: mã điểm, đơn vị, kiểu dữ liệu, quality, timestamp, lệnh có giới hạn, hạn hiệu lực, idempotency key, trạng thái ack? |

---

## 2. Phát hiện chính

**Modbus và SunSpec**

- F-01 [FACT] Một lần đọc FC03/FC04 lấy tối đa **125 thanh ghi**. Một lần ghi FC16 (Write Multiple Registers) tối đa **123 thanh ghi**. Hai giới hạn này suy ra từ PDU 253 byte. https://docs.elipse.com.br/documents/en-us/driver/modbus/latest/modbus_appendix_max_limit_block_size.html ; https://www.se.com/be/en/faqs/FA252887/ (qua kết quả tìm kiếm)
- F-02 [FACT] Đặc tả Modbus quy định byte order **big-endian trong mỗi thanh ghi**. Đặc tả **không** quy định thứ tự word cho giá trị 32/64 bit, và không định nghĩa kiểu float. Thực tế có ABCD, CDAB, BADC, DCBA, trong đó CDAB (word swap) là biến thể phổ biến nhất. https://docs.chipkin.com/articles/modbus-data-types-byte-order-reference/ ; https://industrialmonitordirect.com/blogs/knowledgebase/modbus-32-bit-data-register-mapping-and-endianness-guide (qua kết quả tìm kiếm; nguồn thứ cấp)
- F-03 [FACT] Modbus RTU phân khung bằng khoảng lặng ≥3,5 ký tự. Ở 9600 baud, ký tự 11 bit, 3,5 ký tự ≈ 4,01 ms. Khung chuẩn là 8-E-1. https://www.mikrocontroller.net/attachment/216048/Modbus_RTU_PROTOCOL.pdf ; https://industrialmonitordirect.com/blogs/knowledgebase/modbus-rtu-character-time-calculating-the-35-character-timeout (qua kết quả tìm kiếm)
- F-04 [FACT] Thiết bị Huawei (inverter, SDongle) chỉ chấp nhận **một kết nối Modbus TCP** mỗi lúc. Dongle cần chu kỳ đọc ≥5 s. Cổng là 6607 (firmware mới) hoặc 502. Modbus TCP phải được bật ("Enable (Unlimited)"). (nghiên cứu FusionSolar trước, `api_integration.md` §2)
- F-05 [FACT] Trên EMMA-A02, Modbus TCP chỉ nhận kết nối ở cổng 502 và không còn cho chỉnh Modbus ID. Chỉ tài khoản **installer** mới bật được Modbus TCP. Datasheet EMMA ghi "Supports Modbus-TCP and third-party VPP integration" và quản lý tối đa 2 sạc SCharger. https://forum.iobroker.net/post/1270320 ; https://raspberry.tips/raspberrypi-tutorials/huawei-sun2000-home-assistant-emma-solar-dashboard ; https://solar.huawei.com/en/professionals/all-products/EMMA/specs ; https://www.heima24.de/shop/images/products/media/db-huawei-emma02.pdf (qua kết quả tìm kiếm; forum = Low)
- F-06 [FACT] Thanh ghi điều khiển pin Huawei được cộng đồng ghi nhận (chưa đối chiếu tài liệu Huawei): 47086 = chế độ làm việc của pin (giá trị 6 = "Third-party Scheduling"), 47100 = kích hoạt sạc/xả cưỡng bức, 47083 = thời lượng, 47102 = công suất, 47104 = SOC đích. Có người dùng bật/tắt được nhưng không đổi được công suất. https://community.homey.app/t/app-pro-huawei-fusionsolar-manager/153353?page=16 ; https://community.openhab.org/t/sveasolar-powershifter-pv-inverter-huawei/164046 (qua kết quả tìm kiếm; Low)
- F-07 [FACT] Sungrow Logger1000: theo cộng đồng, unit ID mặc định là 247 và địa chỉ trong tài liệu phải trừ 1. Người dùng đọc được nhưng **không ghi được setpoint**. Một ý kiến khác cho rằng Sungrow không công bố tham số đọc/ghi của logger. Với hybrid SH: thanh ghi 13049 = EMS mode; lệnh sạc/xả 0xAA/0xBB/0xCC nằm ở **13050 hoặc 13051**, các nguồn mâu thuẫn và có báo cáo lệnh "không có tác dụng". https://community.homey.app/t/modbus-register-logger-1000-sungrow/126405 ; https://forum.cleanenergyreviews.info/t/logger1000-as-modbus-tcp-server/3181 ; https://www.loxforum.com/forum/german/software-konfiguration-programm-und-visualisierung/424167-sungrow-sh10rt-wr-modbusparameter ; https://forum.iobroker.net/post/936007 (qua kết quả tìm kiếm; Low)
- F-08 [FACT] SunSpec Modbus **701–712** (DER theo IEEE 1547-2018) đã lên trạng thái APPROVED và thay thế dòng 100 (101–103, 120–123). Bảng tham chiếu của SMA liệt kê 701 (AC Measurement), 702 (Capacity), 703 (Enter Service), 704 (AC Controls), 705 (Volt-Var), 706 (Volt-Watt), 707–709 (trip), 712 (Watt-Var), 713 (Storage Capacity), 714 (DC Measurement). SMA ghi rằng 124 (Storage) và 126 (Volt-Var) **không còn được hỗ trợ trong SunSpec profile 2.0 của SMA**. https://sunspec.org/sunspec-modbus-700-series-der-information-models-are-now-approved/ ; https://files.sma.de/downloads/SunSpecModbus-TI-en-11.pdf (qua kết quả tìm kiếm)
- F-09 [FACT] Dòng lưu trữ 80x: 802 = Battery Base, 803 = Lithium-Ion Battery Bank, 804 = Lithium-Ion String. Bản Draft 4 của đặc tả đưa 802–805 và 807 lên trạng thái TEST, **không phải APPROVED**. Một slide năm 2014 dùng cách đánh số khác (801 base, 802 Li-ion). Đây là mâu thuẫn do phiên bản. https://sunspec.org/wp-content/uploads/2025/01/SunSpec-Alliance-Specification-Energy-Storage-ModelsD4rev0-1.pdf ; https://www.slideserve.com/chaim/sunspec-alliance-overview-storage-standards-development-program (qua kết quả tìm kiếm)
- F-10 [FACT] SunSpec cho phép điểm bắt đầu ở thanh ghi 40000, 50000 hoặc 0, đánh dấu bằng chuỗi "SunS" (0x5375 0x6E53). Tài liệu đánh số từ 40001 (1-based), còn trên dây là 40000 (0-based). Sungrow dùng map riêng bắt đầu từ 5000 (báo cáo người dùng). https://github.com/SolarNetwork/solarnetwork/wiki/SunSpec-model-discovery ; https://community.victronenergy.com/t/sungrow-inverters-and-sunspec/57195 (qua kết quả tìm kiếm)
- F-11 [FACT] IEEE 1547-2018 yêu cầu giao diện truyền thông DER tại chỗ hỗ trợ ít nhất một trong ba giao thức: IEEE 2030.5, IEEE 1815 (DNP3) hoặc SunSpec Modbus. SunSpec (12/2023) cho biết nhiều thiết bị đã có chứng nhận UL 1741 SB vẫn **có lỗi tương tác ở giao diện SunSpec Modbus**, và tới 6/2023 rất ít hãng hoàn tất chứng nhận SunSpec 1547. https://www.cooperative.com/programs-services/bts/Documents/Emerging%20Priorities%20for%20Energy%20Research%20Day%20-%20Oct%202018/IEEE%201547-2018%20-%20Vartanian%20(NRECA-APA-ResearchDay-20181031).pdf ; https://sunspec.org/communication-interface-defects-revealed-inul-1741-sb-certified-inverters/ (qua kết quả tìm kiếm)

**MQTT, OPC UA, giao thức lưới**

- F-12 [FACT] Sparkplug B dùng NBIRTH/NDEATH/DBIRTH/DDEATH/STATE. NDEATH đi qua MQTT Last Will. Broker đạt chuẩn phải hỗ trợ QoS 0 cho dữ liệu, QoS 1 cho quản lý trạng thái, retained và LWT. Ở v3.0, STATE nằm ở `spBv1.0/STATE/<host_id>`, payload là JSON `{online, timestamp}`. Có ít nhất một gateway thương mại đặt cứng QoS 0 cho Will, khiến NDEATH có thể mất. https://www.emqx.com/en/blog/sparkplug-3-0-advancements-and-formalization-in-mqtt-for-iiot ; https://docs.chariot.io/x/S4SzBw ; https://support.hms-networks.com/hc/en-us/articles/36458732970386-Is-the-the-Crimson-Sparkplug-B-implementation-compliant-with-the-spec (qua kết quả tìm kiếm)
- F-13 [FACT] Trong MQTT 5, Message Expiry Interval cho phép broker bỏ tin đã quá hạn và giảm dần thời hạn còn lại khi tin đang chờ. Session Expiry Interval thay cho cleanSession. https://www.emqx.com/en/blog/mqtt-message-expiry-interval ; https://docs.solace.com/API/MQTT-v50-Prtl-Conformance-Spec/mqtt-v50-C-summary-new-features.htm (qua kết quả tìm kiếm)
- F-14 [FACT] Theo danh mục companion spec của OPC Foundation, OPC UA cho năng lượng mới có OPC 10040 "UA for IEC 61850" (Release Candidate) và mapping gió IEC 61400-25 (đang làm). Không thấy companion spec riêng cho PV hay BESS. https://opcfoundation.org/wp-content/uploads/2026/03/OPCF-Energy-Initiative.pdf (qua kết quả tìm kiếm)
- F-15 [FACT] IEC 61850 GOOSE chạy trực tiếp trên Ethernet lớp 2 multicast, với yêu cầu trễ <3–4 ms tùy lớp hiệu năng. IEC 61850-7-420:2021 (Ed.2) định nghĩa logical node cho DER, bao gồm lưu trữ. https://softwaretoolbox.com/resources/what-is-iec61850 ; https://scc-ccn.ca/standardsdb/standards/2048725 (qua kết quả tìm kiếm)
- F-16 [FACT] IEC 60870-5-104 dùng TCP port 2404 mặc định. Tham số điển hình là k=12, w=8, t1=15 s, t2=10 s, t3=20 s, với t2<t1 và w≤2/3·k. Kiểu ASDU: M_ME_NC_1 (13, float không tem thời gian), M_ME_TF_1 (36, float + CP56Time2a), C_SE_NC_1 (50, setpoint float). https://infosys.beckhoff.com/content/1031/tf6500_tc3_iec60870_5_10x/984040459.html ; https://kb.mervis.info/doku.php/en:mervis-ide:35-help:023-server-communication-protocols:010-iec-60870-5-104-server ; https://wiki.elseta.com/books/the-vinci-software/page/iec-60870-5-104 (qua kết quả tìm kiếm)
- F-17 [FACT] Việt Nam: theo VBHN 52 (NĐ 58/2025 + NĐ 243/2026), hệ ĐMTMN đấu nối **trung áp trở lên** có bán điện dư phải kết nối với hệ thống thu thập, giám sát, điều khiển của cấp điều độ. Hệ trung áp không bán điện dư phải có "thiết bị bật tắt phát ngược". Theo bản tóm tắt QĐ 1570/QĐ-EVN của Advantech, giao thức là Modbus TCP và IEC 60870-5-104 cho giám sát/điều khiển và IEC 62056 cho công tơ, đường truyền ≥64 kbps và trễ ≤125 ms. (nghiên cứu FusionSolar trước, `competitors_rebuild.md` Q6) ; https://www.advantech.com/vi-vn/resources/industry-focus/quyet-dinh-1570qd-evn-dien-mat-troi-mai-nha-dieu-can-biet ; https://vjol.info.vn/tctbgd/article/view/121843 (qua kết quả tìm kiếm; **chưa đọc văn bản QĐ 1570**)
- F-18 [FACT] DNP3 cho DER: IEEE 1815.2 dựa trên MESA-DER và DNP3 AN2018-001, ánh xạ đối tượng IEC 61850-7-420 sang DNP3 cho IEEE 1547/Rule 21. Trạng thái xuất bản chưa rõ (các trang DNP-UG mâu thuẫn). EPRI có outstation mã nguồn mở theo AN2018-001. https://www.dnp.org/ieee-releases-18152-standard-for-der-communications ; https://restservice.epri.com/publicdownload/000000003002015355/0/Product (qua kết quả tìm kiếm)

**BMS, EV, DR**

- F-19 [FACT] Không có chuẩn CAN BMS chung. Các BMS kiểu "Pylontech-compatible" dùng CAN 500 kbps, khung chuẩn 11 bit, chu kỳ 1 s, với các ID 0x351/0x355/0x356/0x35A/0x35E/0x370… Tài liệu gốc của Pylontech/Victron từng bị gỡ. Thiếu 0x355 (SOC/SOH) thì inverter báo timeout BMS. Venus OS bỏ qua khung 29 bit. https://akkudoktor.net/uploads/short-url/dwFYBPwjnfia9tSuhUopj9uGX2u.pdf ; https://community.victronenergy.com/t/connect-diy-bms-via-can-to-cerbo-gx-eigenes-bms-via-can-mit-cerbo-gx-verbinden/37102 ; https://akkudoktor.net/t/pylontech-bms-mit-sma-sunny-island/18019 (qua kết quả tìm kiếm)
- F-20 [FACT] OCPP 2.1 được OCA công bố 23/01/2025. Bản này thêm khối bidirectional (V2X), DER control, hỗ trợ ISO 15118-20 và giao dịch tiếp tục sau reboot. Logic ứng dụng viết cho 2.0.1 "vẫn tương thích" với 2.1. Có nguồn thứ cấp nói 2.1 đã thành IEC 63584 (chưa kiểm chứng). https://openchargealliance.org/ocpp-2-1-is-now-available/ ; https://openchargealliance.org/protocols/open-charge-point-protocol ; https://codibly.com/news-insights/8-features-ocpp-2_1 (qua kết quả tìm kiếm)
- F-21 [FACT] OCPP 1.6 có ba loại charging profile: ChargePointMaxProfile, TxDefaultProfile và TxProfile. stackLevel cao hơn được ưu tiên, giới hạn hiệu lực là giá trị nhỏ nhất. Riêng Easee: TxDefaultProfile không tự xóa và có thể đè TxProfile (ví dụ 0 A đè 20 A). OCPP 1.6J có Security Whitepaper Ed.3 (2022) và Ed.4 (02/2026), với profile 1 (HTTP Basic, không TLS), 2 (TLS + Basic) và 3 (TLS + chứng chỉ client). https://www.bender.de/docs/charge-controller/OCPP/ocpp-smart-charging/ ; https://developer.easee.com/docs/ocpp-smart-charging ; https://openchargealliance.org/?p=159286 ; https://www.trialog.com/?p=11328 (qua kết quả tìm kiếm)
- F-22 [FACT] OpenADR 3.0 dùng REST/JSON (2.0b dùng XML/SOAP) và có webhook. 3.0 không thay thế 2.0b. Sản phẩm 3.0 đầu tiên được chứng nhận vào 3/2025. Bản 3.1 thêm MQTT và "price clusters". IEEE 2030.5 là giao thức mặc định của California Rule 21 (CSIP), dùng TLS 1.2 + chứng chỉ, và chứng nhận bắt buộc từ 22/06/2020. https://www.openadr.org/assets/OpenADR%20Webinar%20Nov%202023%20-%20From%202.0%20to%203.0.pdf ; https://www.openadr.org/assets/OpenADR%20AR25.pdf ; https://ecommercenews.co.nz/story/openadr-3-0-certification-marks-milestone-in-energy-sector ; https://standards.ieee.org/content/dam/ieee-standards/standards/web/documents/presentations/smart_energy_slides.pdf ; https://www.qualitylogic.com/wp-content/uploads/2021/07/Data-Sheet-DER-Workshop.pdf (qua kết quả tìm kiếm)

**Cloud của hãng và controller tại chỗ**

- F-23 [FACT] Huawei Northbound là API kéo (pull), giới hạn theo phút và theo ngày, dữ liệu 5 phút, không có webhook. API **ghi** (battery dispatch, chế độ pin, giới hạn công suất) là task bất đồng bộ và **chỉ có ở chế độ OAuth Connect**, kèm quy định "không gọi lại trước khi task hoàn tất". (nghiên cứu FusionSolar trước, `api_integration.md` §1)
- F-24 [FACT] Tài liệu Sungrow iSolarCloud Open API chỉ xem được sau khi đăng nhập portal developer. Bên tích hợp khuyên tạo user API chỉ đọc. Một integration cộng đồng (thử trên 1 hệ) điều khiển được sạc/xả, SOC và lịch qua OpenAPI. Firmware cũ có thể bỏ qua giới hạn công suất. https://docs.eniris.be/da/Controller/Devices/Cloud/ISolarCloud ; https://community.home-assistant.io/t/sungrow-isolarcloud-integration-custom-hacs-sensors-optional-charge-discharge-control/1017858 (qua kết quả tìm kiếm)
- F-25 [FACT] SMA có cổng developer với Monitoring API (dữ liệu Sunny Portal/ennexOS), GridControl API và GeoForecast API, sandbox dữ liệu giả, luồng OAuth code grant. "Live API" **không được dùng để giám sát liên tục**. Hệ đã chuyển sang ennexOS trả HTTP 308 kèm ID mới. Monitoring API có thể tính phí. https://developer.sma.de/sma-apis ; https://developer.sma.de/sma-sandbox-apis ; https://solytic.com/knowledge/set-up-api-access-sma-monitoring-api/ (qua kết quả tìm kiếm)
- F-26 [FACT] SolisCloud API ký HMAC-SHA1 trên (verb, Content-MD5, Content-Type, Date, path), header `Authorization: API <KeyId>:<Sign>`. Giới hạn được trích là "3 lần mỗi 5 giây mỗi IP" (nguồn cộng đồng 2023). Tên endpoint không thống nhất giữa các nguồn. https://usservice.solisinverters.com/support/solutions/articles/73000661192-solis-api-troubleshooting ; https://projects.bentasker.co.uk/gils_projects/issue/utilities/telegraf-plugins/9.html ; https://github.com/hultenvp/soliscloud_api (qua kết quả tìm kiếm)
- F-27 [FACT] Growatt: Home Assistant dùng "official Growatt V1 API" qua token với các host theo vùng (openapi.growatt.com, openapi-au, openapi-cn). API "classic" bằng mật khẩu có giới hạn chặt, có thể khóa tài khoản tới 24 h. Không thấy con số giới hạn chính thức cho V1. Deye Cloud: client cộng đồng dùng appId/appSecret + mật khẩu băm SHA-256, base URL `https://eu1-developer.deyecloud.com/v1.0`. Chỉ thấy endpoint **đọc** cấu hình pin. Có ý kiến cho rằng DeyeCloud chạy qua server Solarman. https://www.home-assistant.io/components/growatt_server/ ; https://mirrors.edge.kernel.org/CPAN/modules/by-module/Config/KORNIX/DeyeCloud-Client-0.0.2.readme ; https://community.home-assistant.io/t/deye-cloud-integration/813153 (qua kết quả tìm kiếm)
- F-28 [FACT] Theo datasheet SmartMGC5000B, Huawei công bố vòng kín zero feed-in ≤2 s và peak shaving/giới hạn công suất ≤5 s. Autarco chia độ trễ tổng thành: chu kỳ đo của công tơ + trễ truyền + thời gian phản ứng của inverter + thời gian giảm công suất vật lý. https://solar.huawei.com/admin/asset/v1/pro/view/bb9458d9373d4502912378db3cbc7f2d.pdf ; https://www.photomate.eu/smartlogger5000b ; https://help.autarco.com/en/hardware/why-am-i-still-exporting-while-i-have-set-my-pv-system-to-zero-export- (qua kết quả tìm kiếm)
- F-29 [FACT] meteocontrol blue'Log XC dùng license "Modbus Power Control" (firmware ≥10.0.8, slave ID 1, port 502, delay 1.000 ms) để nhận setpoint P/Q/cosφ. Các giao thức viễn điều khiển IEC 60870-5-101/-104, IEC 61850 và DNP3 đi qua **bộ chuyển đổi giao thức riêng** (PLC PFC200, ILC 171) rồi chuyển sang Modbus TCP. Solar-Log "Modbus TCP PM" (có license) dùng port 502, slave ID 1, FC 04/06/16 và nhận lệnh P/Q từ bên ngoài. https://www.meteocontrol.com/fileadmin/Daten/Dokumente/EN/Produkte/On_Site/blue_Log_XM_XC/Data_sheet/blue_Log_XM_XC_Modbus_Power_Control_license_blue_Log_XC_data_sheet_LastMod-2026-01-27_en.pdf ; https://www.solar-log.com/fileadmin/user_upload/documents/Datenblaetter/en_GB/Komponenten/Kommunikation/SolarLog_Datasheet_Modbus_TCP_PM_EN.pdf (qua kết quả tìm kiếm)
- F-30 [FACT] Victron Venus OS (GX): MQTT (1883) và Modbus TCP (502, bật trong Settings → Services). Theo cộng đồng, ESS "Mode 2" dùng điểm `/AcPowerSetpoint` (thanh ghi 2700, int16) cho setpoint lưới. "Mode 3" giao cả vòng điều khiển ra bên ngoài. Có câu hỏi chưa được trả lời về **fallback khi master Modbus mất kết nối** và việc ghi vào flash hay RAM. https://communityarchive.victronenergy.com/questions/95889/multipluss-ii-is-external-control-ess-mode-2-or-3%EF%B9%96childToView=102991.html ; https://mcpservers.org/en/servers/lubosstrejcek/victron-tcp (qua kết quả tìm kiếm; Low–Med)
- F-31 [FACT] OpenEMS Edge chạy mô hình input-process-output trong một **Cycle**, khoảng một lần mỗi giây. Giá trị channel không đổi trong một cycle. Scheduler quyết định thứ tự controller, và controller chạy sau không ghi đè được kết quả đã ghi. Edge↔Backend dùng JSON-RPC qua WebSocket. Dữ liệu được tách thành Timestamped/Aggregated/ResendDataNotification, với dữ liệu aggregate tính sẵn ở Edge. Backend có triển khai TimescaleDB (beta, 2022). https://openems.github.io/openems.io/openems/latest/edge/architecture.html ; https://openems.github.io/openems.io/openems/latest/coreconcepts.html ; https://openems.github.io/openems.io/openems/latest/edge/scheduler.html ; https://github.com/OpenEMS/openems/releases (qua kết quả tìm kiếm)
- F-32 [FACT] NTP đạt độ chính xác cỡ 1–100 ms. PTP (IEEE 1588) đạt cỡ µs nhưng cần hardware timestamping. PTP chỉ bằng phần mềm đạt khoảng 100 µs. https://timebeat.app/blog/ptp-vs-ntp ; https://sunplus.atlassian.net/wiki/x/JQB1eQ (qua kết quả tìm kiếm)
- F-33 [FACT] Thanh ghi thời gian hệ thống của Huawei SUN2000 là 40000 (U32, epoch giây **theo giờ địa phương**). Múi giờ là thanh ghi riêng 43006 (I16, phút). Có người dùng gặp exception khi ghi. https://community.openhab.org/t/reading-data-from-huawei-inverter-sun-2000-3ktl-10ktl-via-modbus-tcp-and-rtu/87670?page=5 (qua kết quả tìm kiếm; Low)

**Suy luận chính**

- F-34 [INFERENCE] "Tương thích đa hãng" thực chất là **thư viện driver theo model/firmware**, không phải một giao thức. Ngay cả SunSpec, "chuẩn" mạnh nhất, cũng có lỗi tương tác ở thiết bị đã chứng nhận (F-11). Hãng lớn ở Việt Nam (Huawei, Sungrow) dùng map riêng (F-04, F-07, F-10). Mọi driver phải có trạng thái kiểm chứng theo model/firmware.
- F-35 [INFERENCE] Đường **ghi** luôn khó hơn đường đọc. Cloud API: ghi chỉ có ở Huawei (OAuth Connect, async), Sungrow (cộng đồng), SMA (GridControl, chưa rõ phạm vi). Modbus: ghi phụ thuộc chế độ "third-party/remote" (Huawei 47086=6, Sungrow EMS mode, Victron Mode 2/3) và có báo cáo "ghi không tác dụng". Thiết kế phải **đọc lại để xác nhận** (readback) mọi lệnh.
- F-36 [INFERENCE] Vòng điều khiển zero-export/peak shaving cần ≤2–5 s đầu-cuối (F-28). Cloud API của hãng có độ phân giải 5 phút và giới hạn theo phút/ngày (F-23). Vì vậy **mọi điều khiển thời gian thực phải ở edge hoặc controller native**. Cloud chỉ gửi kế hoạch, giới hạn và chế độ, mỗi cái có hạn hiệu lực.
- F-37 [INFERENCE] Với C&I trung áp ở Việt Nam, IEC 60870-5-104 (slave về điều độ) là yêu cầu V1 chứ không phải tùy chọn (F-17). IEC 61850 chỉ cần khi tích hợp vào trạm biến áp hoặc BESS lớn có yêu cầu của chủ đầu tư. DNP3, IEEE 2030.5 và OpenADR **không có bằng chứng áp dụng ở Việt Nam**. Chỉ nên giữ chỗ trong kiến trúc, không đưa vào MVP.

---

## 3. Phân tích chi tiết

### 3.1 Phân tầng tích hợp và ranh giới bảo vệ

```
[Thiết bị: inverter / PCS / BMS / công tơ / EVSE / rơ-le]
     │ Modbus RTU/TCP, SunSpec, CAN (qua PCS/BMS gateway), OCPP (EVSE→edge), IEC 61850 (nếu có)
     ▼
[Controller native của hãng (tùy chọn): SmartLogger/EMMA, Logger1000/EMS300CP, Solar-Log, blue'Log, GX, EMS tủ BESS]
     │ Modbus TCP (setpoint/chế độ), đọc trạng thái
     ▼
[EDGE của ta: driver, point mapping, local control loop, buffer, IEC 104 slave về EVN, OCPP CSMS cục bộ (tùy chọn)]
     │ MQTT 5 + TLS (telemetry/event/command/ack), HTTPS (OTA, file)
     ▼
[CLOUD: ingest, TSDB, lập lịch/tối ưu, quản lý lệnh, connector cloud API của hãng (chỉ đọc + lệnh chậm)]
```

Thứ tự ưu tiên khi có xung đột (cao xuống thấp):

1. Bảo vệ phần cứng native: rơ-le, BMS (CCL/DCL, SOC cứng), PCS (quá dòng, anti-islanding), rơ-le chống phát ngược nếu điện lực yêu cầu.
2. Giới hạn cứng của site do edge áp dụng: giới hạn xuất/nhập ở PCC, giới hạn hợp đồng.
3. Lệnh điều độ (EVN IEC 104).
4. Lệnh vận hành viên có quyền.
5. Lịch/kế hoạch tối ưu từ cloud.
6. Chiến lược mặc định của edge.

[PROPOSAL] Cloud **không bao giờ** ghi trực tiếp vào thiết bị. Mọi lệnh đi qua bộ phân xử (arbiter) ở edge (PR-E-03). Đây là cùng nguyên tắc với PR-B03 của Agent B. Theo một patent ESS (https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11411391, qua kết quả tìm kiếm), BMS gửi tín hiệu bảo vệ tới PCS qua **dây cứng** để phản ứng thời gian thực, còn kênh tới EMS chỉ là TCP/IP, RS485 hoặc CAN. Đây là [INFERENCE] ủng hộ việc phần mềm EMS nằm ngoài vòng bảo vệ.

### 3.2 Modbus TCP/RTU: ràng buộc cho driver

**Function code dùng thực tế**

| FC | Tên | Dùng cho | Ghi chú thiết kế |
|---|---|---|---|
| 0x01/0x02 | Read Coils / Discrete Inputs | Trạng thái DI, rơ-le | Ít gặp ở inverter. Hay gặp ở I/O module, rơ-le |
| 0x03 | Read Holding Registers | Phần lớn telemetry và cấu hình (Huawei dùng 0x03) | ≤125 thanh ghi/lần (F-01) |
| 0x04 | Read Input Registers | Telemetry (Solar-Log PM dùng 04, F-29; nhiều công tơ) | ≤125 thanh ghi/lần |
| 0x05 | Write Single Coil | Bật/tắt | Cần chính sách xác nhận |
| 0x06 | Write Single Register | Setpoint 16 bit | **Không** dùng cho giá trị 32 bit (ghi nửa giá trị sẽ có trạng thái trung gian sai) |
| 0x10 | Write Multiple Registers | Setpoint 32 bit, khối lịch | ≤123 thanh ghi/lần. Ghi nguyên tử trong một PDU |
| 0x17 | Read/Write Multiple | Hiếm | Không dựa vào |
| 0x2B/0x0E | Read Device Identification | Nhận diện | Nhiều thiết bị không hỗ trợ. Fingerprint bằng thanh ghi model/firmware |

**Địa chỉ và unit ID**
- [FACT] Tài liệu SunSpec đánh số 1-based (40001), trên dây là 0-based (40000) (F-10). Sungrow Logger1000 có báo cáo lệch 1 (F-07).
- [PROPOSAL] Trong register map của driver chỉ lưu **địa chỉ trên dây, 0-based**, kèm trường `doc_address` và `doc_offset` để truy vết về tài liệu hãng.
- [FACT] Unit ID mặc định khác nhau tùy thiết bị: Huawei 1 (0 khi đi qua AP của inverter, theo nghiên cứu trước), Sungrow Logger1000 247 (cộng đồng), blue'Log/Solar-Log 1 (F-29), Ampowr hybrid 247 (RTU)/255 (TCP) (https://manual-sofar.eniris.be/en/Controller/Devices/PV-hybrid-and-battery-inverters/Ampowr, qua kết quả tìm kiếm). [INFERENCE] Unit ID phải là cấu hình theo từng thiết bị, không được mặc định toàn cục.

**Kiểu dữ liệu, word order, scale và giá trị "không có"**

| Thuộc tính trong register map | Giá trị cho phép | Lý do |
|---|---|---|
| `type` | U16, I16, U32, I32, U64, I64, F32, F64, STRING(n), BITFIELD16/32, ENUM16 | Đủ cho Huawei/SunSpec/công tơ |
| `word_order` | `BIG` (ABCD), `LITTLE_WORD` (CDAB) | Đặc tả không quy định (F-02) |
| `byte_order` | `BIG` (mặc định), `SWAP` | Hiếm, nhưng có |
| `scale` | Số cố định (ví dụ Huawei 32080 I32 gain 1000, nghiên cứu FusionSolar trước) **hoặc** tham chiếu thanh ghi scale factor (SunSpec `*_SF`, 10^SF) | SunSpec: đọc SF **cùng lượt** với giá trị |
| `offset` | Số | Nhiệt độ một số hãng |
| `sign_convention` | Mô tả dấu gốc, ví dụ Huawei 37113 ">0 feed-in, <0 import" (nghiên cứu trước) | Chuẩn hóa về quy ước chung ở §3.18 |
| `na_values` | Ví dụ 0xFFFF (U16), 0x8000 (I16), 0x7FFFFFFF… | SunSpec dùng giá trị sentinel. Chỉ kiểm chứng 0xFFFF qua slide SunSpec (https://sunspec.org/wp-content/uploads/2009/03/SunSpec-Modbus-Open-Source-Webinar-Deck-Template.pdf). 0x8000 là [UNKNOWN] |
| `access` | R, RW, W | Cấm ghi vào thanh ghi R |
| `persist` | `VOLATILE`, `NVM`, `UNKNOWN` | Ghi setpoint chu kỳ vào NVM có thể làm mòn flash. Victron chưa trả lời câu này (F-30) → [UNKNOWN] theo hãng |
| `min_write_interval_ms` | Số | Chống ghi dồn |

Ví dụ scale: SunSpec giá trị thô 1234 với SF = −2 → 12,34 (https://industrialmonitordirect.com/blogs/knowledgebase/sunspec-modbus-communication-with-solar-inverters, qua kết quả tìm kiếm, nguồn thứ cấp).

**Một master và kết nối đồng thời**
- [FACT] Huawei chỉ cho một client (F-04). Evcc cảnh báo proxy Modbus song song "may cause communication errors" (nghiên cứu trước).
- [INFERENCE] Bus RTU chỉ có **một master** theo bản chất giao thức. Nếu EMS của tủ BESS hay logger hãng đã là master trên RS485 của PCS/BMS, edge của ta không được gắn thêm master lên cùng bus. Edge phải đọc qua cổng northbound (Modbus TCP server) của controller đó.
- [PROPOSAL] Mỗi thiết bị vật lý chỉ có **một connection owner** là edge (hoặc controller native). Mọi consumer khác (HA, SCADA của khách) đọc qua Modbus TCP server/MQTT do edge xuất lại.

**Ngân sách polling (tính toán, [INFERENCE])**

RTU 9600 baud, 8-E-1 (11 bit/ký tự → 1,146 ms/ký tự):

| Giao dịch | Request | Response | Thời gian dây (gồm 2×3,5 ký tự) | + thời gian phản hồi thiết bị (giả định 20–100 ms) |
|---|---|---|---|---|
| Đọc 10 thanh ghi | 8 byte ≈ 9,2 ms | 25 byte ≈ 28,7 ms | ≈ 46 ms | ≈ 66–146 ms |
| Đọc 60 thanh ghi | 8 byte | 125 byte ≈ 143 ms | ≈ 160 ms | ≈ 180–260 ms |
| Đọc 125 thanh ghi | 8 byte | 255 byte ≈ 292 ms | ≈ 310 ms | ≈ 330–410 ms |

Hệ quả: một bus 9600 baud có 10 inverter, mỗi cái 3 khối đọc (30 giao dịch × khoảng 150–300 ms), cần **4,5–9 s mỗi vòng**. Ở 19200 baud, thời gian dây giảm một nửa, nhưng thời gian phản hồi của thiết bị thì không.

[PROPOSAL]
- Công tơ PCC dùng cho vòng điều khiển phải nằm trên **bus riêng hoặc Modbus TCP**, không chung bus RTU với inverter.
- Driver gom các thanh ghi liền kề thành block, nhưng không vượt 125 và không vắt qua "lỗ" địa chỉ mà thiết bị trả exception 02.
- Chia tầng polling:

| Tầng | Chu kỳ | Điểm |
|---|---|---|
| `fast` | 0,2–1 s | P/Q tại PCC, P của ESS, P của PV tổng (nếu controller hỗ trợ) |
| `normal` | 5–15 s | U/I/f, SOC, trạng thái |
| `slow` | 60 s | Bộ đếm năng lượng, nhiệt độ |
| `static` | Khi kết nối và mỗi ngày | Nameplate, firmware |

- Chu kỳ tối thiểu theo driver (Huawei dongle ≥5 s, F-04; blue'Log delay 1.000 ms, F-29).

**Xử lý lỗi**
- Exception 01/02/03 → lỗi cấu hình. Đánh dấu điểm `BAD_CONFIG` và ngừng poll điểm đó.
- Exception 04/06 (device failure/busy) → backoff.
- Timeout → tăng bộ đếm lỗi. Sau N lần thì `BAD_COMM`.
- Trên socket mới, Huawei dongle "first TX always fails", cần delay 1–5 s sau khi connect (nghiên cứu trước). Driver phải có `connect_delay_ms` và giữ kết nối lâu dài, không mở/đóng theo từng lần poll.

### 3.3 SunSpec: dùng để khám phá năng lực, không phải bảo đảm

**Thuật toán discovery ([PROPOSAL], dựa trên F-10)**

1. Thử đọc "SunS" ở 40000, 50000, 0 (0-based) với các unit ID đã cấu hình.
2. Đọc chuỗi model: [ID, L] → nhảy L thanh ghi → … cho tới ID 0xFFFF (kết thúc).
3. Lưu danh sách model + độ dài vào `capability_profile`. Đọc model 1 (Common: Mn, Md, Opt, Vr, SN) để fingerprint.
4. Đối chiếu với "driver overlay" theo hãng/model/firmware, để sửa lỗi đã biết (F-11) hoặc bổ sung điểm ngoài SunSpec.

**Bảng model (trạng thái kiểm chứng của chúng ta)**

| Model | Nội dung | Trạng thái bằng chứng | Dùng trong sản phẩm |
|---|---|---|---|
| 1 | Common | FACT (nhiều nguồn) | Bắt buộc đọc |
| 101/102/103 | Inverter 1 pha / split / 3 pha (dòng 100) | FACT: bị thay bởi 701/702/704 (F-08) | Vẫn hỗ trợ đọc, vì thiết bị cũ còn nhiều |
| 120–123 | Nameplate, settings, status, immediate controls | FACT: được khuyến nghị thay bởi dòng 700 (F-08) | Đọc. Ghi 123 (WMaxLimPct…) chỉ khi driver đã kiểm chứng |
| 124 | Storage (điều khiển pin, % công suất sạc) | FACT: evcc vẫn dùng; SMA profile 2.0 bỏ (F-08) | Hỗ trợ, có cờ "legacy" |
| 126 | Volt-Var (cũ) | FACT: SMA profile 2.0 bỏ | Chỉ đọc |
| 201–204 | Công tơ 1 pha / split / 3 pha wye / 3 pha delta (int + SF) | FACT danh sách 201–204, 211–214 (SMA, https://manuals.sma.de/ennexOS/en-US/14259660939.html). Tên chi tiết từng model là [INFERENCE] | Hỗ trợ 201–204 và 211–214 (float) |
| 701–712 | DER theo IEEE 1547-2018 | FACT: APPROVED (F-08) | Ưu tiên đọc 701/702/704/713/714. Chức năng lưới (705–712) chỉ đọc cấu hình, **không** chỉnh ở MVP (thuộc trách nhiệm grid code/installer) |
| 713 | DER Storage Capacity | FACT (F-08) | Đọc SOC/dung lượng |
| 714 | DER DC Measurement | FACT (F-08) | Đọc |
| 715 | Có trong danh sách chứng nhận FoxESS (https://sunspec.org/product-certification-registry) | Tên/nội dung: [UNKNOWN] | Không dùng tới khi kiểm chứng |
| 802 | Battery Base | FACT: TEST trong Draft 4 (F-09) | Đọc. Ghi chỉ khi driver kiểm chứng |
| 803/804 | Li-ion Bank / String | FACT (F-09) | Đọc (giám sát string/module) |
| 805+ | Module/flow… | Mâu thuẫn số hiệu (F-09) → [UNKNOWN] | Không dùng |

[INFERENCE] SunSpec đáng giá nhất ở bước **khám phá năng lực và chuẩn hóa tên điểm**. Ghi qua SunSpec (704, 123, 124, 802) vẫn phải kiểm chứng theo từng model, vì có lỗi tương tác ngay ở thiết bị đã chứng nhận (F-11).

### 3.4 BMS qua CAN

- [FACT] Không có chuẩn chung. "Pylontech-compatible" là chuẩn de facto ở phân khúc nhỏ (500 kbps, khung 11 bit, 1 s). ID và nội dung khác nhau giữa các hãng và tài liệu gốc đã bị gỡ (F-19). BYD có protocol riêng do cộng đồng giải mã (https://github.com/dfch/BydCanProtocol, qua kết quả tìm kiếm).
- [FACT] Tủ BESS C&I kiểu "all-in-one" (ví dụ HT Infinite Power) công bố cổng CAN, RS-485, Ethernet, Wi-Fi nhưng **không công bố bảng thanh ghi** (Agent B, L08/L11).
- [INFERENCE] Trong C&I, BMS↔PCS qua CAN là **vòng bảo vệ nội bộ của tủ**. EMS (của ta) không nên chen vào bus này. Nên đọc dữ liệu BMS (SOC, SOH, CCL/DCL, cell min/max, cảnh báo) qua Modbus TCP northbound của EMS/PCS tủ. Chỉ đọc CAN trực tiếp (chế độ nghe, listen-only) khi không còn đường nào khác, và khi đó **không bao giờ phát khung**.
- [PROPOSAL] Edge cần một cổng CAN (SolarEdge CLC1 cũng có 1×CAN, Agent B L34) để: (a) đọc BMS của hệ nhỏ không có Modbus; (b) dự phòng. Driver CAN phải dùng file mô tả kiểu DBC theo hãng/phiên bản, có cờ "listen-only" mặc định.

### 3.5 MQTT và Sparkplug B cho uplink

**Yêu cầu uplink:** đi ra (outbound-only) qua NAT/4G; store-and-forward; thứ tự trong một luồng; có ack cho lệnh; chống trùng; nén.

| Lựa chọn | Ưu | Nhược | Kết luận |
|---|---|---|---|
| MQTT 5 + schema riêng (Protobuf/CBOR, envelope có `seq`) | Kiểm soát ack lệnh, expiry, seq, batch backfill. Message Expiry khớp với hạn của lệnh (F-13) | Phải tự định nghĩa | **Chọn cho uplink chính** [PROPOSAL] |
| Sparkplug B 3.0 | Chuẩn birth/death, quản lý trạng thái online (F-12), có hệ sinh thái SCADA (Ignition…) | Chỉ có NCMD/DCMD, không có ngữ nghĩa ack/expiry/idempotency của lệnh. QoS 0 cho dữ liệu. Phụ thuộc broker "Sparkplug Aware" cho birth retained. Đã thấy lỗi triển khai Will QoS 0 (F-12) | **Xuất phụ** (northbound tùy chọn cho khách có SCADA) [PROPOSAL] |
| OPC UA (client/server, PubSub) | Mô hình thông tin mạnh | Không có companion spec cho PV/BESS (F-14). Nặng cho 4G. Không phổ biến ở thiết bị PV/BESS Việt Nam [INFERENCE] | Chỉ dùng **phía dưới** khi gặp PLC/BMS công nghiệp có OPC UA server, hoặc **phía trên** khi khách yêu cầu |

**Topic và QoS [PROPOSAL]**

| Topic | Hướng | QoS | Retained | Nội dung |
|---|---|---|---|---|
| `ems/v1/{tenant}/{site}/{edge}/state` | edge→cloud | 1 | Có (LWT = offline) | Online/offline, phiên bản firmware/config, trạng thái clock |
| `…/telemetry/{stream}` | edge→cloud | 1 | Không | Batch điểm `{seq, points[]}` |
| `…/event` | edge→cloud | 1 | Không | Alarm/SOE, thay đổi chế độ, kết quả lệnh |
| `…/backfill` | edge→cloud | 1 | Không | Dữ liệu dồn sau khi mất kết nối, tách riêng để không chặn realtime |
| `…/cmd` | cloud→edge | 1 | **Không** (tránh lệnh cũ chạy lại khi reconnect) | Envelope lệnh (§3.19) với Message Expiry = `expires_at − now` |
| `…/cmd/ack` | edge→cloud | 1 | Không | Chuyển trạng thái lệnh |
| `…/config` | cloud→edge | 1 | Có (bản config mong muốn + version) | Desired config. Edge báo reported config qua `state` |

[INFERENCE] QoS 1 có thể giao trùng. Vì thế mọi consumer phía cloud phải idempotent theo `(edge_id, stream, seq)`, và edge xử lý lệnh idempotent theo `command_id` (§3.19). Đây là kiến thức chung về MQTT, không có trích dẫn trực tiếp trong phiên này.

### 3.6 IEC 61850: khi nào đáng làm

- [FACT] GOOSE (lớp 2, <3–4 ms) dành cho tín hiệu bảo vệ/liên động. MMS dành cho giám sát/điều khiển client-server. 7-420:2021 bao gồm DER và lưu trữ (F-15). Siemens dùng GOOSE ~70 ms cho load shedding (Agent B L23).
- [INFERENCE] Trong phạm vi C&I behind-the-meter, IEC 61850 chỉ cần khi: (a) site có trạm biến áp riêng với IED 61850 và chủ đầu tư yêu cầu EMS đọc/ghi qua MMS; (b) BESS quy mô MW mà PCS/PPC chỉ có giao diện 61850; (c) load shedding nhanh qua GOOSE. Trường hợp (c) thuộc hệ bảo vệ và **không** do cloud thực hiện.
- [PROPOSAL] Không đưa vào MVP. V2: MMS client ở edge (đọc + setpoint), dựa vào thư viện có sẵn (cần đánh giá giấy phép). GOOSE: không làm. Nếu cần thì dùng IED/PLC chuyên dụng.

### 3.7 IEC 60870-5-104 cho điều độ EVN (site trung thế)

**Đã biết**: xem F-16, F-17. Các logger thương mại xử lý theo hai cách: (a) SmartLogger có sẵn IEC 104 cho tối đa 5 kết nối bên thứ ba (nghiên cứu trước, `architecture_security.md` Q1); (b) blue'Log dùng PLC chuyển đổi 104 → Modbus TCP (F-29). Advantech ADAM-3600 được định vị cho QĐ 1570, có chuyển đổi Modbus TCP ↔ IEC 104 và buffer SD (nghiên cứu trước).

**Đề xuất cấu hình slave 104 ở edge [PROPOSAL]** (cần đối chiếu yêu cầu của từng Công ty Điện lực/cấp điều độ, Q-E-01):

| Thành phần | Đề xuất mặc định | Ghi chú |
|---|---|---|
| Vai trò | Edge là **controlled station (slave/server)**. Điều độ là master | Port 2404 |
| Tham số | k=12, w=8, t0=30 s, t1=15 s, t2=10 s, t3=20 s (giá trị phổ biến, F-16) | Phải cấu hình được theo yêu cầu của điều độ |
| Địa chỉ | Common Address (CA) và IOA theo bảng điểm do điều độ cấp | Không tự đặt |
| Đo lường | M_ME_TF_1 (36, float + CP56Time2a) cho P, Q, U, I, f, cosφ tại PCC, P của PV tổng, P/SOC của BESS | Gửi theo deadband + chu kỳ nền. Dùng M_ME_NC_1 (13) nếu điều độ yêu cầu |
| Trạng thái | M_SP_TB_1 / M_DP_TB_1 (single/double point có tem thời gian) cho máy cắt, trạng thái "bật tắt phát ngược", chế độ điều khiển cục bộ/từ xa | Số type: [INFERENCE] từ kiến thức chung, chưa có trong kết quả tìm kiếm |
| Lệnh | C_SE_NC_1 (50) setpoint P (kW hoặc % Pđm); C_SC_NA_1 / C_DC_NA_1 cho bật/tắt phát ngược; select-before-operate nếu điều độ yêu cầu | Mọi lệnh 104 đi vào arbiter ở mức ưu tiên 3 (§3.1). Phản hồi ACT_CON/ACT_TERM chỉ sau khi readback xác nhận |
| Đồng bộ thời gian | Nhận C_CS_NA_1 (clock sync) từ master. Đánh dấu nguồn thời gian | Edge vẫn chạy NTP. Xung đột giữa hai nguồn ghi vào event [PROPOSAL] |
| Interrogation | C_IC_NA_1 trả toàn bộ ảnh điểm | — |
| Mất kết nối cloud | Slave 104 **không phụ thuộc cloud** | Bắt buộc |
| Mạng | VPN/APN riêng tới điều độ. ≥64 kbps, ≤125 ms (theo tóm tắt QĐ 1570) | Tài liệu 10 xử lý bảo mật (IEC 62351 là [UNKNOWN] với EVN) |

**Chưa biết**: bảng điểm chuẩn, cấp điều độ (A0/A1/A2/A3/điều độ phân phối), ngưỡng công suất, có bắt buộc redundancy hay không, yêu cầu bảo mật (Q-E-01, Q-E-02).

### 3.8 DNP3 (Mỹ)

- [FACT] F-18. [INFERENCE] Không có bằng chứng DNP3 được dùng ở lưới phân phối Việt Nam. Chỉ giữ chỗ "protocol adapter" (DNP3 outstation) cho thị trường xuất khẩu. Có thể tham khảo stack EPRI (giấy phép cần kiểm tra).

### 3.9 OCPP cho sạc EV

| Khía cạnh | OCPP 1.6J | OCPP 2.0.1 | OCPP 2.1 |
|---|---|---|---|
| Trạng thái | Phổ biến nhất trong lắp đặt hiện có [INFERENCE] | Phát hành trước 2.1, có chứng nhận | Công bố 23/01/2025 (F-20) |
| Smart charging | 3 loại profile, stackLevel, lấy giá trị nhỏ nhất (F-21) | Tương tự, cộng device model (Component/Variable, SetVariables) | + DER control, V2X, ISO 15118-20 (F-20) |
| Bảo mật | Security Whitepaper Ed.3/Ed.4 bổ sung profile 1–3 (F-21) | Profile 1–3 tích hợp sẵn | Như 2.0.1 [INFERENCE] |
| Tương thích ngược | Không tương thích với 2.x ở mức thông điệp (https://www.midapower.com/news/strategic-comparison-of-ocpp-1-6j-vs-2-0-1-for-commercial-charging-operators/) | — | Logic ứng dụng 2.0.1 dùng lại được (F-20) |

[INFERENCE] Hệ quả cho EMS:

- EMS cần quản lý công suất sạc theo PCC (giới hạn nhập, dư PV). Có hai kiến trúc:
  - (A) EMS là CSMS (OCPP server) cho sạc tại site. Phải làm cả authorize, transaction và billing, tức là chồng lấn với CPO.
  - (B) EMS gửi giới hạn công suất cho CSMS hiện có. Không có chuẩn cho kênh này ở 1.6/2.0.1. 2.1 có khối DER control nhưng chưa rõ dùng cho kênh EMS→CSMS ([UNKNOWN]).
- Cách thực dụng: edge chạy **OCPP local proxy/CSMS tối giản** chỉ cho smart charging. Chỉ dùng khi site không có CSMS khác. Nếu có CSMS (CPO) thì tích hợp API của CSMS đó.
- Charger có thể trả "NotSupported" và hành vi khác nhau giữa hãng (Easee, F-21). Driver OCPP cần "charger profile" khai báo: hỗ trợ đơn vị A hay W, số kỳ (period) tối đa, có tôn trọng TxDefaultProfile khi offline hay không.
- Lệnh tới charger phải có giới hạn hạn hiệu lực. Dùng `validTo`/`duration` của profile thay vì setpoint vô thời hạn, và có TxDefaultProfile an toàn làm fallback khi mất kết nối (F-21: TxDefaultProfile "to keep charging controlled if connectivity is lost").
- Bảo mật: tối thiểu profile 2 (TLS + Basic Auth). Profile 3 cho charger hỗ trợ. Không dùng profile 1 trên mạng không tin cậy.

### 3.10 OpenADR / IEEE 2030.5

- [FACT] F-22. [INFERENCE] Hai giao thức này gắn với chương trình DR của utility/aggregator ở Mỹ, EU và Úc. Ở Việt Nam, không thấy chương trình DR nào dùng các giao thức này. Agent A cũng ghi DR/VPP là P2 cho Việt Nam.
- [PROPOSAL] Thiết kế "DR adapter" ở cloud dưới dạng một **nguồn lệnh** (command source) vào arbiter. Ánh xạ sự kiện DR → `SET_GRID_IMPORT_LIMIT`/`SET_ESS_ACTIVE_POWER` với cửa sổ thời gian. Nếu sau này cần thì làm VEN OpenADR 3.x trước (REST/JSON, có MQTT ở 3.1, dễ hơn 2.0b XML/SOAP). Không làm 2030.5 trừ khi bán vào thị trường Rule 21/Úc.

### 3.11 Cloud API của hãng: đọc/ghi và giới hạn

| Hãng | Đường đọc công khai | Đường ghi | Giới hạn/đặc điểm | Đánh giá cho EMS |
|---|---|---|---|---|
| Huawei FusionSolar | Northbound `/thirdData/*` (pull, 5 phút, 100 trạm/thiết bị mỗi lần; lịch sử 10 thiết bị × 3 ngày) | OAuth Connect: task bất đồng bộ cho battery dispatch, battery mode, active power control. **Không gọi lại khi task chưa xong** | failCode 407/20618, giới hạn phiên, cần owner cấp quyền (từ 9/2025) | Đọc: OK cho giám sát/báo cáo. Ghi: chỉ cho **lịch chậm** (theo giờ). Không dùng cho vòng điều khiển (nghiên cứu trước) |
| Sungrow iSolarCloud | Open API (tài liệu sau đăng nhập), khóa appkey/secret (+RSA theo một nguồn) | Cộng đồng điều khiển được sạc/xả/SOC (thử trên 1 hệ) | Firmware cũ bỏ qua giới hạn P (F-24) | Đọc: OK. Ghi: [UNKNOWN] về hỗ trợ chính thức |
| SMA | Monitoring API (Sunny Portal/ennexOS), OAuth code grant, sandbox | GridControl API (phạm vi chưa rõ) | "Live API" không cho giám sát liên tục. 308 khi di trú. Có phí (F-25) | Đọc: OK. Ghi: [UNKNOWN] chi tiết |
| Solis | SolisCloud API, ký HMAC-SHA1 | Không thấy tài liệu ghi | Khoảng 3 lần / 5 s / IP (cộng đồng, F-26) | Chỉ đọc |
| Growatt | OpenAPI V1 token, host theo vùng | apis.io nhắc tới "inverter parameters", chưa rõ ghi | API cũ khóa tài khoản tới 24 h (F-27) | Chỉ đọc (mặc định) |
| Deye | DeyeCloud developer API (appId/secret), eu1 | Chỉ thấy đọc cấu hình pin | Có thể đi qua Solarman (F-27) | Chỉ đọc |

[INFERENCE] Không hãng nào trong bảng công bố webhook/push trong các nguồn đã thấy. Mọi connector cloud là **pull có hạn mức**. Connector cloud phù hợp với gói "giám sát không cần phần cứng" (tầng monitoring của hướng FusionSolar cũ), **không** phù hợp làm đường điều khiển EMS.

[PROPOSAL] Mỗi connector cần:
- Bộ giới hạn tốc độ theo endpoint và theo tài khoản.
- Một tài khoản API cho mỗi site, hoặc cho mỗi khách hàng.
- Job backfill ban đêm.
- Phân biệt "success nhưng data null" (mất quyền) với dữ liệu rỗng.
- Gắn mọi điểm lấy qua cloud quality `UNCERTAIN_VENDOR_CLOUD` với độ trễ thực.

### 3.12 Nhiệm vụ của edge gateway (đặc tả chức năng)

| # | Nhiệm vụ | Yêu cầu chi tiết [PROPOSAL] | Căn cứ |
|---|---|---|---|
| G1 | Protocol adapters | Modbus RTU/TCP master, SunSpec discovery, CAN (listen-only mặc định), OCPP 1.6J (+2.0.1 V1), IEC 104 slave (V1 cho trung thế), Modbus TCP server (xuất lại cho bên thứ ba), MQTT 5 client. Sau này: IEC 61850 MMS client, DNP3 outstation, OpenADR VEN | §3.2–3.10 |
| G2 | Point mapping | Register map khai báo (YAML/JSON), có version, gắn `driver_id@version`. Ánh xạ sang mã điểm chuẩn (§3.18). Chuẩn hóa dấu và đơn vị **tại edge** | F-02, F-04 |
| G3 | Capability discovery | SunSpec scan + fingerprint model/firmware → chọn driver overlay. Báo `capability_profile` lên cloud. Cloud chỉ cho tạo lệnh mà profile hỗ trợ | F-10, F-11 |
| G4 | Command mapping | Lệnh chuẩn → chuỗi ghi cụ thể theo driver (ví dụ Huawei: đặt 47086=6 rồi ghi công suất/thời lượng/trigger; Victron: ghi 2700). Kèm readback và timeout | F-06, F-30 |
| G5 | Arbiter / local control | Vòng 200 ms–1 s: zero-export, giới hạn nhập (peak shaving), giữ SOC dự phòng, phân bổ P giữa nhiều PCS/inverter. Ràng buộc native luôn thắng. Giống Power Solver của OpenEMS | F-28, F-31, B PR-B03 |
| G6 | Store-and-forward | Buffer bền (SQLite/RocksDB trên eMMC/SSD), ≥7 ngày ở tần suất upload. Gửi realtime trước, backfill sau với tốc độ giới hạn. Ack theo `seq` | OpenEMS ResendData (F-31); meteocontrol backfill 7 ngày (nghiên cứu trước) |
| G7 | Clock sync | chrony (NTP) với ≥2 nguồn + RTC có pin. GNSS tùy chọn cho trung thế. PTP chỉ khi có IED 61850/PMU. Báo trạng thái đồng bộ và offset ước tính. Đặt giờ thiết bị theo lịch nếu driver hỗ trợ (Huawei 40000 = giờ địa phương + 43006 múi giờ) | F-32, F-33 |
| G8 | Timestamp & quality | Mỗi mẫu có `ts` (thời điểm thu tại edge, UTC ms), `ts_src` (thời gian thiết bị nếu có) và quality code (§3.18) | — |
| G9 | Dữ liệu trùng/sai thứ tự/đến trễ | `seq` đơn điệu cho mỗi stream. Cloud upsert theo (point, ts). Dữ liệu trễ kích hoạt tính lại aggregate trong cửa sổ | §3.18 |
| G10 | Vận hành offline | Khi mất cloud: giữ giới hạn cứng, chạy kế hoạch đã nhận (≥48 h, theo Schneider 48 h ở Agent B L15), hết kế hoạch thì về chiến lược mặc định an toàn. IEC 104 và OCPP cục bộ vẫn chạy | B L15/L16 |
| G11 | Reconnect | Backoff có jitter. Khi reconnect: publish state → nhận config/cmd còn hạn → đồng bộ trạng thái lệnh → backfill | F-13 |
| G12 | Firmware/config management | OTA A/B có ký số, rollback tự động. Config theo mô hình desired/reported có version. Không tự cập nhật firmware **thiết bị** của hãng (để installer làm qua công cụ của hãng) [PROPOSAL] | Rủi ro brick |
| G13 | Watchdog & health | Watchdog phần cứng. Đo thời lượng cycle (OpenEMS CycleWorker đo execution time). Báo lỗi bus | F-31 |
| G14 | Xuất lại dữ liệu | Modbus TCP server / Sparkplug B tùy chọn cho SCADA của khách | §3.5 |
| G15 | I/O cứng | DI cho tín hiệu cắt giảm/E-stop/rơ-le chống phát ngược; DO cho "bật tắt phát ngược" nếu điều độ yêu cầu (tương tự CLC1 4DI/4DO, Agent B L34) | F-17 |

**Kích thước buffer (tính toán [INFERENCE])**: 2.000 điểm, mỗi điểm một mẫu mỗi 5 s → 400 mẫu/s → 34,6 triệu mẫu/ngày. Ở 16 byte/mẫu chưa nén, mức này là ≈ 553 MB/ngày, tức ≈ 3,9 GB cho 7 ngày. Deadband và nén delta sẽ giảm mạnh, nhưng chưa đo. Băng thông realtime ≈ 400 mẫu/s × khoảng 10 byte nén ≈ 32 kbps, vừa với 4G và dưới mức 64 kbps tham chiếu của QĐ 1570.

### 3.13 Vì sao vòng điều khiển nhanh phải ở edge

**Ngân sách thời gian zero-export ([INFERENCE] dựa trên F-28)**

| Khâu | Edge (Modbus TCP, công tơ riêng) | Qua cloud của hãng |
|---|---|---|
| Đo PCC | Chu kỳ đo của công tơ khoảng 100–1.000 ms | Dữ liệu cloud được gộp 5 phút (Huawei) |
| Truyền tới bộ điều khiển | <50 ms (LAN) | Polling 1–15 phút, cộng giới hạn hạn mức |
| Tính toán | <10 ms | Giây |
| Gửi lệnh | 10–300 ms (ghi Modbus, RTU chậm hơn) | Task bất đồng bộ, phút |
| Inverter phản ứng + ramp | 0,1–2 s (theo hãng) | Như bên trái |
| **Tổng** | **≈ 0,5–3 s**, khớp mức ≤2 s mà Huawei công bố | **Phút**: không đáp ứng zero-export |

Kết luận: zero-export, giới hạn nhập, bảo vệ SOC và phân bổ nhiều PCS phải ở **edge hoặc controller native**. Cloud làm lập lịch (15 phút đến ngày tới), giới hạn, chế độ và báo cáo.

**Fallback khi edge không thể điều khiển [PROPOSAL]**

- Mất công tơ PCC (quality BAD quá N giây): ESS về P=0 hoặc chế độ tự dùng native. Inverter PV về **giới hạn an toàn cấu hình sẵn ở inverter/logger native** (ví dụ export limit native = 0 kW với site zero-export). Không giữ setpoint cũ vô hạn.
- Mất kết nối với thiết bị: thiết bị phải có **giới hạn native hoặc watchdog** (nếu driver hỗ trợ, như timeout lệnh remote). Nếu thiết bị không có watchdog, driver đánh dấu `requires_native_fallback=true`. Installer phải cấu hình giới hạn native trước khi bật điều khiển từ xa.
- Ưu tiên ghi setpoint/chế độ **vào controller native** (SmartLogger, EMS300CP, GX, EMS tủ BESS) thay vì điều khiển từng inverter (đồng ý với X-03 của Agent A).

### 3.14 OpenEMS và controller thương mại làm tham chiếu

| Sản phẩm | Vai trò | Giao diện cho bên thứ ba (đã thấy) | Bài học cho thiết kế |
|---|---|---|---|
| OpenEMS Edge/Backend (EPL-2.0) | Edge Java/OSGi: cycle khoảng 1 s, channel, scheduler, Power Solver, controller (PeakShaving, Balancing, ToU). Backend: JSON-RPC/WebSocket, Timedata (Influx, TimescaleDB beta), resend | Modbus TCP API controller (evcc dùng: https://docs.evcc.io/en/meters/openems-modbus-api) | Mô hình process image (giá trị không đổi trong cycle) tránh race. Tách aggregate ở edge. Đúng stack Java của team. Giấy phép EPL-2.0 cần pháp lý xem (X-E-06) |
| Huawei SmartLogger3000/5000B, EMMA | Controller native: zero-export ≤2 s, peak shaving ≤5 s (F-28) | Modbus TCP (bật "Unlimited"), IEC 104 (SmartLogger, ≤5 kết nối), EMMA: Modbus TCP 502, VPP bên thứ ba (F-05) | Đọc/ghi qua controller, không qua từng inverter |
| Sungrow Logger1000 / EMS300CP | Controller native | Modbus TCP (unit 247?), map không chính thức (F-07). EMS bên thứ ba được hỗ trợ trên PowerStack (Agent B L41) | Map phải lấy từ kênh đối tác Sungrow |
| Victron Cerbo GX (Venus OS) | Controller native ESS | MQTT 1883, Modbus TCP 502, ESS Mode 2/3 (F-30) | Mode 2 = setpoint lưới, an toàn hơn Mode 3. Hỏi rõ watchdog |
| Solar-Log Base | Logger + quản lý feed-in | Modbus TCP PM (license; FC 04/06/16; 502; ID 1) (F-29) | Có license → tính vào chi phí tích hợp |
| meteocontrol blue'Log XC | Logger + PPC | Modbus Power Control (license), 104/61850/DNP3 qua PLC chuyển đổi (F-29) | Mô hình "PPC + protocol converter" để đáp ứng điều độ |
| SolarEdge ONE Controller (CLC1) | Edge C&I | Modbus TCP server 1502, 2×RS485, CAN, 4DI/4DO (Agent B L34) | Gợi ý cấu hình phần cứng edge |

### 3.15 Ma trận phù hợp: loại thiết bị × giao thức

Ký hiệu: **●** chính (nên hỗ trợ), **◐** có điều kiện/thường gặp ở một số hãng, **○** hiếm/không khuyến nghị, **—** không áp dụng. Đây là **đánh giá phù hợp**, không phải tuyên bố tương thích. Mỗi model cụ thể vẫn phải kiểm chứng.

| Loại thiết bị | Modbus RTU | Modbus TCP | SunSpec | CAN | MQTT | OPC UA | IEC 61850 | IEC 104 | DNP3 | OCPP | OpenADR/2030.5 | Cloud API hãng | Ghi chú kiểm chứng |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PV string inverter (C&I) | ● | ● (qua logger/dongle) | ◐ (SMA, Fronius, SolarEdge; Huawei/Sungrow dùng map riêng) | — | ○ | ○ | ○ | ○ | ○ (Mỹ) | — | ◐ (Mỹ, Rule 21) | ◐ đọc | F-04, F-07, F-10, F-11 |
| Hybrid inverter (pin LV) | ● | ● | ◐ (124/802/713) | ◐ (tới BMS, nội bộ) | ◐ (Victron GX) | — | — | — | — | — | ○ | ◐ đọc, ghi hiếm | F-06, F-07, F-30 |
| PCS (BESS C&I) | ● | ● | ○ | ◐ (nội bộ với BMS) | ○ | ◐ | ◐ (MW) | ○ | ○ | — | — | ○ | Thường đi kèm EMS tủ. Lấy map từ OEM |
| BMS / rack pin | ◐ | ◐ | ◐ (802–804) | ● (nội bộ) | — | ◐ | — | — | — | — | — | — | F-19. EMS không chen vào bus CAN bảo vệ |
| Tủ BESS all-in-one có EMS riêng | ◐ | ● (northbound) | ○ | ○ | ◐ | ○ | ○ | ○ | — | — | — | ◐ | Agent B L08–L11: không công bố bảng thanh ghi |
| Công tơ PCC / sub-meter | ● | ● | ◐ (201–204, 211–214) | — | — | — | ◐ (trạm) | — | — | — | — | — | IEC 62056 cho công tơ doanh thu EVN (F-17). Công tơ điều khiển là công tơ riêng |
| Logger/controller hãng | ◐ | ● | ◐ | — | ◐ | ○ | ◐ | ◐ (SmartLogger) | ○ | — | ◐ | ● | F-05, F-28, F-29 |
| Sạc EV AC/DC | ◐ (Modbus một số hãng) | ◐ | — | — | — | — | — | — | — | ● (1.6J; 2.0.1; 2.1) | ◐ (2.1 DER) | ◐ | F-20, F-21 |
| Genset controller | ● | ● | — | ◐ (J1939) | — | — | — | — | — | — | — | — | [UNKNOWN] theo hãng. Ngoài MVP |
| Trạm thời tiết / cảm biến bức xạ | ● | ◐ | ○ | — | ◐ | — | — | — | — | — | — | — | Kiến thức chung |
| Rơ-le bảo vệ / máy cắt / RMU | ◐ | ◐ | — | — | — | — | ● (trạm mới) | ◐ | ◐ (Mỹ) | — | — | — | Chỉ đọc trạng thái. Cắt bằng tay hoặc qua bảo vệ |
| Điều độ EVN (phía trên) | — | ◐ (theo QĐ 1570) | — | — | — | — | — | ● | — | — | — | — | F-17. Bảng điểm [UNKNOWN] |
| Aggregator/utility DR | — | — | — | — | ◐ (OpenADR 3.1 MQTT) | — | — | — | ◐ | — | ● (ngoài VN) | — | F-22 |
| SCADA/BMS tòa nhà của khách | ◐ | ● (edge làm server) | — | — | ◐ (Sparkplug) | ◐ | ○ | ◐ | ○ | — | — | — | Xuất lại qua edge (G14) |

### 3.16 Hướng tích hợp ưu tiên theo hãng (thị trường Việt Nam)

| Hãng/hệ | Đường điều khiển (P0) | Đường đọc dự phòng | Trạng thái bằng chứng | Rủi ro chính |
|---|---|---|---|---|
| Huawei C&I (SmartLogger) | Modbus TCP tới SmartLogger | Northbound API | FACT (nghiên cứu trước) | Bật "Unlimited". Một client. IEC 104 có sẵn trên SmartLogger, có thể chồng chéo với slave 104 của ta |
| Huawei residential/SME (EMMA) | Modbus TCP 502 tới EMMA | Northbound/OAuth | FACT forum + datasheet (F-05) | Chỉ installer bật được. EMMA chỉ lộ một tập con thanh ghi |
| Sungrow PowerStack/hybrid | Modbus TCP tới EMS300CP/inverter (EMS mode) | iSolarCloud | FACT (B L41) / Low (F-07) | Map không công khai. Lệnh ghi "không tác dụng" |
| SMA | SunSpec/Modbus (Data Manager) | SMA Monitoring API | FACT một phần (F-08, F-25) | Profile 2.0 bỏ 124 |
| Victron | Modbus TCP/MQTT tới GX (Mode 2) | VRM (chưa nghiên cứu) | Low–Med (F-30) | Watchdog setpoint [UNKNOWN] |
| Solis/Growatt/Deye | Modbus RTU/TCP local (map của hãng, chưa nghiên cứu) | Cloud API chỉ đọc | Cloud: Med/Low (F-26, F-27). Local: [UNKNOWN] | Không có ghi qua cloud |
| Tủ BESS Trung Quốc (HT, …) | Modbus TCP northbound của EMS tủ | — | UNKNOWN (B L08) | Cần hợp đồng cung cấp register map. Mỗi tủ là một driver |

### 3.17 Thời gian, chất lượng dữ liệu, dữ liệu trùng/sai thứ tự/trễ

**Ba dấu thời gian [PROPOSAL]**
- `ts`: thời điểm edge nhận giá trị (UTC, ms). Đây là khóa thời gian chính cho dữ liệu polling.
- `ts_src`: thời điểm do thiết bị cung cấp (nếu có, ví dụ SOE/alarm). Kèm `src_clock_state` (synced/unknown). Lưu ý Huawei dùng **giờ địa phương** (F-33). Pyhfs cũng ghi rằng timestamp Northbound thực ra là UTC dù tài liệu nói giờ trạm (nghiên cứu trước). Driver phải chuẩn hóa về UTC.
- `ts_ingest`: thời điểm cloud ghi nhận, dùng để đo độ trễ và phát hiện dữ liệu backfill.

**Trạng thái đồng hồ edge**: `SYNCED` (|offset| < 100 ms theo chrony), `DEGRADED` (< 1 s), `UNSYNCED` (RTC only hoặc > 1 s). Khi `UNSYNCED`, mọi mẫu mang cờ `CLOCK_UNSYNCED`. Cloud có thể hiệu chỉnh theo `ts_ingest` nếu offset đã biết. Việt Nam UTC+7, không có DST.

**Xử lý tại cloud [PROPOSAL]**
- **Trùng**: khóa duy nhất `(point_id, ts)`. Cùng giá trị thì bỏ qua. Khác giá trị (driver được sửa, cấu hình scale đổi) thì giữ bản có `rev` cao hơn và ghi audit.
- **Sai thứ tự**: TSDB chấp nhận ghi bất kỳ thứ tự. Logic realtime (giá trị "hiện tại") chỉ cập nhật khi `ts` > `last_ts`.
- **Đến trễ** (backfill): ghi vào hypertable. Đánh dấu bucket aggregate bị ảnh hưởng để tính lại (ví dụ continuous aggregate refresh window ≥ thời gian offline tối đa, 7 ngày). Báo cáo đã xuất mang phiên bản để khỏi bị âm thầm thay đổi.
- **Khoảng trống**: không nội suy trong dữ liệu thô. Khi tính aggregate thì gắn `UNCERTAIN_INTERPOLATED` và tỷ lệ phủ (coverage %).
- **Bộ đếm năng lượng**: dùng bộ đếm tích lũy (Wh, U64) làm nguồn sự thật cho kWh. Phát hiện reset hoặc quay vòng (giá trị giảm) → tạo sự kiện `COUNTER_RESET`. Không tính kWh bằng tích phân P khi có bộ đếm.

### 3.18 Hợp đồng điểm chuẩn (canonical point contract) [PROPOSAL]

**Mã điểm**: `<class>.<quantity>[.<phase|index|qualifier>]`, chữ thường, ổn định qua các phiên bản. Ví dụ `meter.p` (công suất tác dụng tổng), `meter.p.l1`, `ess.soc`, `pv.e_total`.

**Quy ước dấu (bắt buộc, chuẩn hóa tại edge)**
- Công tơ PCC/grid: `p > 0` = **nhận từ lưới (import)**, `p < 0` = **phát lên lưới (export)**. Ngược dấu với Huawei 37113, nên driver phải đảo.
- ESS: `p > 0` = **xả (discharge)**, `p < 0` = **sạc (charge)**.
- PV: `p ≥ 0` = phát.
- Tải/EV: `p ≥ 0` = tiêu thụ.
- Q: `> 0` = phát vô công (theo quy ước máy phát). Phải ghi rõ trong tài liệu 05, vì các hãng khác nhau.

**Thuộc tính của định nghĩa điểm (PointDefinition)**

| Trường | Kiểu | Ví dụ | Ghi chú |
|---|---|---|---|
| `code` | string | `ess.p` | Duy nhất trong class |
| `class` | enum | `meter`, `pv_inverter`, `hybrid_inverter`, `pcs`, `bms`, `ess` (logic), `evse`, `ev_connector`, `genset`, `weather`, `relay`, `site`, `edge` | `ess` là tài sản logic gộp PCS+BMS |
| `unit` | UCUM/SI | W, Wh, var, VA, V, A, Hz, %, °C, W/m², s | Lưu W/Wh (không lưu kW) để tránh nhầm. UI tự đổi đơn vị |
| `dtype` | enum | float64, int64, bool, enum, string, bitset | Bộ đếm Wh = int64 |
| `kind` | enum | `measurement`, `counter`, `status`, `setting`, `alarm`, `nameplate` | Quyết định cách aggregate (avg/last/delta) |
| `range` | [min,max] | `ess.soc`: [0,100] | Ngoài range → `UNCERTAIN_OUT_OF_RANGE` |
| `deadband` | số | 0,5 % Pđm | Gửi khi đổi |
| `max_age_s` | số | 3× chu kỳ poll | Quá tuổi → `UNCERTAIN_STALE` |
| `enum_ref` | id | `ess.mode` → `{IDLE, CHARGE, DISCHARGE, STANDBY, FAULT, OFFLINE}` | Trạng thái của hãng ánh xạ về enum chuẩn, kèm `raw_state` |

**Quality code** (lấy cảm hứng từ IEC 61850 quality / OPC UA StatusCode; [INFERENCE] chưa trích dẫn)

| Nhóm | Mã | Nghĩa |
|---|---|---|
| GOOD | `GOOD` | Đọc trực tiếp, trong hạn |
| GOOD | `GOOD_LOCAL_OVERRIDE` | Giá trị đúng nhưng thiết bị đang ở chế độ local/manual |
| UNCERTAIN | `UNCERTAIN_STALE` | Quá `max_age_s` |
| UNCERTAIN | `UNCERTAIN_CLOCK` | Edge `UNSYNCED` |
| UNCERTAIN | `UNCERTAIN_OUT_OF_RANGE` | Ngoài range vật lý |
| UNCERTAIN | `UNCERTAIN_SUBSTITUTED` | Giá trị thay thế (nhập tay, ước tính) |
| UNCERTAIN | `UNCERTAIN_INTERPOLATED` | Chỉ ở aggregate |
| UNCERTAIN | `UNCERTAIN_VENDOR_CLOUD` | Lấy qua cloud của hãng (trễ, đã gộp) |
| BAD | `BAD_COMM` | Mất liên lạc với thiết bị |
| BAD | `BAD_CONFIG` | Exception 01/02/03, map sai |
| BAD | `BAD_DEVICE` | Thiết bị báo lỗi cảm biến/không có giá trị (sentinel) |
| BAD | `BAD_NOT_SUPPORTED` | Thiết bị không có điểm này |

**Mẫu dữ liệu trên dây (ví dụ logic, không phải code)**

`{edge_id, stream, seq, batch_ts, points:[{pid, ts, v, q, ts_src?}]}`, trong đó `pid` là số nguyên ánh xạ từ `(device_id, code)` qua bảng do config cung cấp, để giảm băng thông. `seq` tăng đơn điệu và không reset khi khởi động lại: lưu vào NVM theo khối.

**Bộ điểm tối thiểu theo class (MVP)**

| Class | Điểm bắt buộc |
|---|---|
| `meter` (PCC) | `p`, `q`, `s`, `pf`, `u.l1-3`, `i.l1-3`, `f`, `e_import`, `e_export` |
| `pv_inverter` | `p`, `q`, `e_total`, `state`, `p_limit_pct` (đọc lại), `dc.p` (nếu có), `alarm_word` |
| `ess` (logic) | `p`, `soc`, `soh`, `p_charge_max`, `p_discharge_max` (từ CCL/DCL × U hoặc PCS), `e_charge`, `e_discharge`, `mode`, `state`, `cell_v_min/max`, `cell_t_min/max` |
| `evse`/`ev_connector` | `p`, `i_limit_active`, `state` (OCPP status), `e_session`, `session_id` |
| `site` (tính toán ở edge) | `p_load` (= grid + pv + ess, theo dấu), `p_export_limit_active`, `p_import_limit_active`, `control_mode` |
| `edge` | `clock_state`, `clock_offset_ms`, `buffer_fill_pct`, `uplink_state`, `cycle_time_ms` |

### 3.19 Hợp đồng lệnh chuẩn (canonical command contract) [PROPOSAL]

**Kiểu lệnh (MVP + V1)**

| Type | Đích | Tham số | Giới hạn kiểm tra tại edge | Mặc định khi hết hạn |
|---|---|---|---|---|
| `SET_EXPORT_LIMIT` | site (PCC) | `p_max_export_w` | ≥0. ≤ giới hạn hợp đồng/pháp lý trong config site | Về giới hạn cấu hình của site |
| `SET_IMPORT_LIMIT` | site | `p_max_import_w` | ≥ tải tối thiểu không cắt được (cấu hình) | Về giới hạn cấu hình |
| `SET_ESS_P` | ess | `p_w` (dấu theo §3.18) | Kẹp vào [−p_charge_max, p_discharge_max] **hiện tại**. Tôn trọng SOC min/max và giới hạn PCC | P=0 hoặc chiến lược mặc định |
| `SET_ESS_MODE` | ess | `mode` ∈ {SELF_CONSUMPTION, PEAK_SHAVING, TOU_SCHEDULE, BACKUP_HOLD, IDLE} | Mode phải có trong `capability_profile` | Mode mặc định |
| `SET_SOC_RESERVE` | ess | `soc_min_pct` | ≥ SOC min native/BMS | Giá trị cấu hình |
| `SET_PV_LIMIT` | pv_inverter / nhóm | `p_limit_pct` hoặc `p_limit_w` | 0–100 %. Tần suất ghi ≤ `min_write_interval` | 100 % (nếu site cho phép xuất) hoặc giới hạn native |
| `SET_Q` / `SET_PF` | pv_inverter/pcs | `q_var` / `pf` | Trong capability. Mặc định **khóa** ở MVP (grid code) | Giá trị native |
| `SET_EV_LIMIT` | evse/connector | `i_max_a` hoặc `p_max_w`, `phases` | ≥ dòng tối thiểu EV (6 A, [INFERENCE] chuẩn IEC 61851 phổ biến) hoặc 0 để tạm dừng | TxDefaultProfile an toàn |
| `APPLY_SCHEDULE` | site/ess | Danh sách khung `{start, end, type, params}` (≥48 h) | Mỗi khung kiểm tra như lệnh đơn. Có version | Hết lịch → chiến lược mặc định |
| `SET_REVERSE_FEED_BLOCK` | site | `blocked: bool` | Chỉ từ nguồn `GRID_OPERATOR` hoặc người có quyền cao | Theo yêu cầu điều độ ([UNKNOWN]) |
| `DEVICE_ON_OFF` | thiết bị | `on: bool` | Hai bước xác nhận. Quyền đặc biệt. Không cho lịch tự động | Không tự đảo |
| `CONFIG_PUSH`, `FW_UPDATE_EDGE` | edge | Bản config/firmware có ký số | Kiểm chữ ký | Rollback |

**Envelope lệnh (trường bắt buộc)**

| Trường | Ý nghĩa |
|---|---|
| `command_id` | UUID v7. **Idempotency key**: edge nhận trùng thì trả lại trạng thái cũ, không thực thi lại |
| `correlation_id` | Liên kết với kế hoạch/sự kiện DR/ticket |
| `source` | `GRID_OPERATOR`, `OPERATOR`, `SCHEDULE`, `OPTIMIZER`, `DR`, `API` → mức ưu tiên trong arbiter |
| `issued_by` | user/service id (audit) |
| `target` | `site_id`, `asset_id`/nhóm |
| `type`, `params` | Như bảng trên |
| `valid_from`, `expires_at` | **Bắt buộc**. Edge từ chối lệnh không có hạn. Hạn tối đa theo type (ví dụ setpoint đơn ≤ 1 h, lịch ≤ 7 ngày) |
| `on_expiry` | `REVERT_DEFAULT` (mặc định) / `HOLD_LAST` (chỉ cho phép với một số type, cấu hình theo site) |
| `supersedes` | `command_id` bị thay thế (tùy chọn) |
| `max_latency_ms` | Đến edge sau mức này thì `REJECTED_STALE` |
| `tolerance` | Ngưỡng readback coi là đã áp dụng (ví dụ ±2 % hoặc ±1 kW), thời gian chờ readback |
| `dry_run` | Chỉ kiểm tra, không ghi |
| `signature` | Tùy chọn (V1): chữ ký của cloud để edge kiểm |

**Trạng thái ack (state machine)**

```
CREATED → AUTHORIZED → SENT ──(edge nhận)──► RECEIVED
RECEIVED → REJECTED_{STALE|INVALID|UNSUPPORTED|OUT_OF_LIMIT|LOWER_PRIORITY}   (kết thúc)
RECEIVED → ACCEPTED → DISPATCHED (đã ghi xuống thiết bị/controller)
DISPATCHED → APPLIED (readback trong tolerance)
           → APPLIED_CLAMPED (đã kẹp do giới hạn native/BMS; báo giá trị thực)
           → FAILED_{DEVICE_EXCEPTION|NO_EFFECT|TIMEOUT}   (ví dụ "ghi không tác dụng", F-07)
APPLIED* → SUPERSEDED | CANCELLED | EXPIRED (→ thực hiện on_expiry) → COMPLETED
Cloud-side: SENT quá hạn mà không có RECEIVED → UNDELIVERED (không tự gửi lại sau expires_at)
```

Quy tắc:
- (1) Mọi chuyển trạng thái gửi qua `cmd/ack`, kèm `ts` và giá trị readback.
- (2) Edge giữ bảng `command_id` đã thấy ít nhất tới `expires_at` + 24 h.
- (3) Lệnh có hiệu lực đang chạy được báo trong `state` để cloud đối soát sau reconnect.
- (4) Lệnh từ điều độ (IEC 104) cũng được tạo envelope nội bộ ở edge với `source=GRID_OPERATOR`, để audit thống nhất.
- (5) Với API hãng dạng async (Huawei: "không gọi lại trước khi task hoàn tất"), connector tuần tự hóa theo plant và ánh xạ task status → `DISPATCHED/APPLIED/FAILED`.

---

## 4. Hệ quả thiết kế cho sản phẩm

| ID | Đề xuất [PROPOSAL] | Ưu tiên | Module | Căn cứ |
|---|---|---|---|---|
| PR-E-01 | Edge gateway là **bắt buộc** với mọi site có điều khiển (BESS, zero-export, EV). Cloud connector chỉ dành cho gói "monitoring-only". **Khác hướng FusionSolar cũ** (giám sát trước, edge tùy chọn), vì EMS cần vòng ≤2–5 s và cloud API của hãng là pull 5 phút có hạn mức | P0 | M-INT, M-BESS | F-23, F-28, F-36 |
| PR-E-02 | Driver framework khai báo (register map YAML/JSON có version, word order, scale/SF, sentinel, sign, access, persist, min_write_interval) + overlay theo hãng/model/firmware. Mỗi driver có trạng thái `VERIFIED_LAB` / `VERIFIED_FIELD` / `COMMUNITY` / `UNVERIFIED`, hiển thị cho installer | P0 | M-INT | F-02, F-07, F-11, F-34 |
| PR-E-03 | Arbiter ở edge với thứ tự ưu tiên §3.1. Ràng buộc native luôn thắng. Mọi lệnh có `expires_at` và readback | P0 | M-BESS, M-SEC | F-35, B PR-B03 |
| PR-E-04 | Uplink MQTT 5 + TLS, schema riêng (seq, batch, backfill tách topic). Lệnh không retained, có Message Expiry. Sparkplug B chỉ là đầu ra tùy chọn | P0 (MQTT), P2 (Sparkplug) | M-INT | F-12, F-13 |
| PR-E-05 | Store-and-forward ≥7 ngày. Kế hoạch offline ≥48 h. Fallback an toàn khi mất PCC/thiết bị | P0 | M-INT | G6, G10 |
| PR-E-06 | Hợp đồng điểm chuẩn §3.18 (dấu, đơn vị SI, quality, 3 timestamp) trở thành chuẩn chung giữa edge, cloud, API công khai và UI | P0 | M-INT, M-HIST | §3.17–3.18 |
| PR-E-07 | Hợp đồng lệnh chuẩn §3.19 (idempotency key, expiry bắt buộc, state machine, APPLIED_CLAMPED/NO_EFFECT) | P0 | M-BESS, M-EV, M-OPT | F-07, F-21, F-23 |
| PR-E-08 | Thứ tự driver MVP: (1) công tơ PCC phổ biến (Modbus); (2) Huawei SmartLogger + EMMA; (3) Sungrow (qua EMS300CP/PowerStack, sau khi có map chính thức); (4) SunSpec chung (1, 101–103, 120–124, 201–204/211–214, 701–714, 802–804); (5) một dòng tủ BESS Trung Quốc có hợp đồng cung cấp map | P0 | M-INT | F-04–F-11, B PR-B08 |
| PR-E-09 | IEC 60870-5-104 slave trên edge cho site trung thế: chạy độc lập với cloud, bảng điểm cấu hình được, có DO/DI cho "bật tắt phát ngược". Bắt buộc ở V1 C&I. Có thể dùng controller hãng (SmartLogger 104) khi khách đã có | P0 cho V1 C&I trung thế | M-GRID | F-16, F-17, F-37 |
| PR-E-10 | OCPP: edge chạy CSMS tối giản (1.6J, Security Profile ≥2) chỉ cho smart charging khi site không có CSMS của CPO. Nếu có CPO thì tích hợp API của CPO. Kế hoạch 2.0.1, theo dõi 2.1 | P1 | M-EV | F-20, F-21 |
| PR-E-11 | Cloud connector (Huawei, Sungrow, SMA, Solis, Growatt, Deye): mặc định chỉ đọc, rate limiter theo endpoint, backfill ban đêm, quality `UNCERTAIN_VENDOR_CLOUD`. Huawei OAuth Connect write chỉ cho lịch chậm | P1 | M-INT | F-23–F-27 |
| PR-E-12 | Phần cứng edge tham chiếu: 2×RS485 (cách ly), 1×CAN, 2×Ethernet (tách WAN/OT LAN), 4DI/4DO, 4G tùy chọn, RTC có pin, eMMC/SSD ≥32 GB, watchdog phần cứng, nhiệt độ công nghiệp | P0 | M-INT | B L34, §3.12 |
| PR-E-13 | Đồng bộ thời gian: chrony ≥2 nguồn + trạng thái đồng hồ trong telemetry. GNSS tùy chọn cho trung thế. PTP không ở MVP | P0 | M-INT | F-32 |
| PR-E-14 | Không tự cập nhật firmware thiết bị của hãng. OTA chỉ cho edge (A/B, ký số, rollback) | P0 | M-INT, M-SEC | G12 |
| PR-E-15 | Không ghi setpoint chu kỳ vào thanh ghi `persist=NVM`, trừ khi hãng xác nhận chịu được. Driver phải khai báo | P1 | M-INT | F-30 (câu hỏi flash/RAM chưa có lời đáp) |
| PR-E-16 | ADR ứng viên: **ADR-xx "Edge runtime: dựa trên OpenEMS Edge hay tự xây?"** Tiêu chí: Java/OSGi khớp team, mô hình cycle/channel đã chín, driver có sẵn, giấy phép EPL-2.0 (file-level copyleft, cần pháp lý), khả năng thêm IEC 104/OCPP. Đề xuất sơ bộ: PoC dựa trên OpenEMS Edge cho driver + controller, contract §3.18–3.19 làm lớp ngoài | P0 (quyết định trước MVP) | M-INT | F-31 |
| PR-E-17 | IEC 61850 MMS client, DNP3 outstation, OpenADR 3.x VEN, IEEE 2030.5 client: chỉ giữ chỗ ở lớp adapter, không ở MVP | P2 | M-INT | F-15, F-18, F-22, F-37 |
| PR-E-18 | Không bao giờ ghi "tương thích với mọi inverter/BESS". Trang "Thiết bị được hỗ trợ" liệt kê model + firmware + trạng thái kiểm chứng + chức năng đọc/ghi | P0 | M-INT, M-ADV | F-11, F-34 |

---

## 5. Evidence ledger

| # | Claim | Source URL | Source type & date | Excerpt/paraphrase | Confidence | Conflicting evidence | Design implication |
|---|---|---|---|---|---|---|---|
| E-01 | FC03 ≤125, FC16 ≤123 thanh ghi | https://docs.elipse.com.br/documents/en-us/driver/modbus/latest/modbus_appendix_max_limit_block_size.html ; https://www.se.com/be/en/faqs/FA252887/ | Tài liệu driver + FAQ hãng; không ngày (qua kết quả tìm kiếm) | "125 registers (250 bytes)… 123 registers (247 bytes)" | High | — | Block ≤125 khi đọc, ≤123 khi ghi |
| E-02 | Word order 32 bit không được chuẩn hóa | https://docs.chipkin.com/articles/modbus-data-types-byte-order-reference/ ; https://industrialmonitordirect.com/blogs/knowledgebase/modbus-32-bit-data-register-mapping-and-endianness-guide | Blog kỹ thuật (qua kết quả tìm kiếm) | Spec không định nghĩa float; ABCD/CDAB phổ biến | Med | Thuật ngữ "endian" dùng không thống nhất giữa các nguồn | `word_order` theo từng thanh ghi |
| E-03 | RTU 3,5 ký tự ≈ 4,01 ms ở 9600 | https://www.mikrocontroller.net/attachment/216048/Modbus_RTU_PROTOCOL.pdf ; https://industrialmonitordirect.com/blogs/knowledgebase/modbus-rtu-character-time-calculating-the-35-character-timeout | Tài liệu giao thức + blog (qua kết quả tìm kiếm) | "silent interval of at least 3.5 character times" | Med–High | Ngưỡng 1,5 ký tự giữa khung dễ bị nhầm | Ngân sách polling RTU |
| E-04 | Huawei: một client, port 6607/502, dongle ≥5 s | (nghiên cứu FusionSolar trước) https://github.com/wlcrs/huawei_solar ; https://github.com/evcc-io/evcc/discussions/1928 | README/thảo luận cộng đồng | "only support one connection at a time" | High | — | Một connection owner |
| E-05 | EMMA: port 502, không chỉnh ID, installer bật; Modbus-TCP + VPP bên thứ ba | https://forum.iobroker.net/post/1270320 ; https://raspberry.tips/raspberrypi-tutorials/huawei-sun2000-home-assistant-emma-solar-dashboard ; https://solar.huawei.com/en/professionals/all-products/EMMA/specs | Forum + blog + trang spec hãng (qua kết quả tìm kiếm) | "Supports Modbus-TCP and third-party VPP integration" | Med (hãng) / Low (forum) | Số heat pump khác nhau giữa các bản datasheet | Driver EMMA, quy trình commissioning |
| E-06 | Thanh ghi pin Huawei 47086=6, 47100/47083/47102/47104 | https://community.homey.app/t/app-pro-huawei-fusionsolar-manager/153353?page=16 ; https://community.openhab.org/t/sveasolar-powershifter-pv-inverter-huawei/164046 | Forum (qua kết quả tìm kiếm) | "47086… 6 = Third-party Scheduling" | Low | Có người không đổi được công suất | Readback + NO_EFFECT |
| E-07 | Sungrow Logger1000 unit 247, lệch 1; hybrid 13049/13050/13051 mâu thuẫn | https://community.homey.app/t/modbus-register-logger-1000-sungrow/126405 ; https://www.loxforum.com/forum/german/software-konfiguration-programm-und-visualisierung/424167-sungrow-sh10rt-wr-modbusparameter ; https://forum.iobroker.net/post/936007 | Forum (qua kết quả tìm kiếm) | "unit ID… by default, is 247" | Low | 13050 vs 13051 | Cần map chính thức từ Sungrow |
| E-08 | SunSpec 701–712 APPROVED, thay dòng 100 | https://sunspec.org/sunspec-modbus-700-series-der-information-models-are-now-approved/ | Tin SunSpec ~2021 (qua kết quả tìm kiếm) | "promoted from TEST… to APPROVED" | High | — | Ưu tiên 70x, vẫn hỗ trợ 10x |
| E-09 | Danh sách 701–714; SMA profile 2.0 bỏ 124/126 | https://files.sma.de/downloads/SunSpecModbus-TI-en-11.pdf | TI của SMA (qua kết quả tìm kiếm) | "124 (Storage) and 126 (Volt-Var) are no longer supported" | Med–High | evcc vẫn dùng 124 | 124 là legacy |
| E-10 | 802 base, 803 bank, 804 string; TEST status | https://sunspec.org/wp-content/uploads/2025/01/SunSpec-Alliance-Specification-Energy-Storage-ModelsD4rev0-1.pdf | Đặc tả Draft 4 (qua kết quả tìm kiếm) | "Promoted models 802… from DRAFT to TEST" | Med | Slide 2014 đánh số khác | Ghi qua 802 cần kiểm chứng |
| E-11 | SunSpec base 40000/50000/0, "SunS"; Sungrow map riêng 5000 | https://github.com/SolarNetwork/solarnetwork/wiki/SunSpec-model-discovery ; https://community.victronenergy.com/t/sungrow-inverters-and-sunspec/57195 | Wiki OSS + forum (qua kết quả tìm kiếm) | 0x5375 0x6E53 | Med | Lệch 40000/40001 | Thuật toán discovery |
| E-12 | IEEE 1547-2018: ít nhất một trong 2030.5/DNP3/SunSpec; thiết bị UL 1741 SB có lỗi giao diện | https://www.cooperative.com/programs-services/bts/Documents/Emerging%20Priorities%20for%20Energy%20Research%20Day%20-%20Oct%202018/IEEE%201547-2018%20-%20Vartanian%20(NRECA-APA-ResearchDay-20181031).pdf ; https://sunspec.org/communication-interface-defects-revealed-inul-1741-sb-certified-inverters/ | Slide NRECA 2018 + bài SunSpec 12/2023 (qua kết quả tìm kiếm) | "very few vendors had completed SunSpec Modbus Certification" | Med–High | — | Không tin tuyệt đối vào chứng nhận |
| E-13 | Sparkplug: QoS0 dữ liệu, QoS1 trạng thái, STATE JSON v3.0; lỗi Will QoS0 | https://www.emqx.com/en/blog/sparkplug-3-0-advancements-and-formalization-in-mqtt-for-iiot ; https://docs.chariot.io/x/S4SzBw ; https://support.hms-networks.com/hc/en-us/articles/36458732970386-Is-the-the-Crimson-Sparkplug-B-implementation-compliant-with-the-spec | Blog vendor + doc (qua kết quả tìm kiếm) | "Will Message QoS cannot be configured to 1" | Med | Retain của STATE chỉ thấy ở 1 nguồn | Sparkplug chỉ là đầu ra phụ |
| E-14 | MQTT 5 Message/Session Expiry | https://www.emqx.com/en/blog/mqtt-message-expiry-interval ; https://docs.solace.com/API/MQTT-v50-Prtl-Conformance-Spec/mqtt-v50-C-summary-new-features.htm | Blog + doc conformance (qua kết quả tìm kiếm) | Broker bỏ tin quá hạn | High | — | Expiry lệnh = MQTT expiry |
| E-15 | OPC UA: 10040 cho 61850 (RC), không có spec PV/BESS | https://opcfoundation.org/wp-content/uploads/2026/03/OPCF-Energy-Initiative.pdf | Tài liệu OPCF 3/2026 (qua kết quả tìm kiếm) | "OPC 10040 – UA for IEC 61850 (Release Candidate)" | Med | — | OPC UA không ở lõi |
| E-16 | GOOSE <3–4 ms lớp 2; 7-420:2021 bao gồm lưu trữ | https://softwaretoolbox.com/resources/what-is-iec61850 ; https://scc-ccn.ca/standardsdb/standards/2048725 | Vendor + danh mục tiêu chuẩn (qua kết quả tìm kiếm) | "<4ms (Class P1), <3ms (Class P2)" | Med | 3 vs 4 ms tùy lớp | 61850 chỉ V2, không GOOSE |
| E-17 | IEC 104 port 2404, k/w/t1–t3, type 13/36/50 | https://infosys.beckhoff.com/content/1031/tf6500_tc3_iec60870_5_10x/984040459.html ; https://wiki.elseta.com/books/the-vinci-software/page/iec-60870-5-104 ; https://kb.mervis.info/doku.php/en:mervis-ide:35-help:023-server-communication-protocols:010-iec-60870-5-104-server | Tài liệu sản phẩm (qua kết quả tìm kiếm) | k=12, w=8, t1=15 s… | High | — | Mặc định slave 104 |
| E-18 | EVN: trung áp bán dư phải kết nối điều độ; QĐ 1570: Modbus TCP + IEC 104, ≥64 kbps, ≤125 ms | https://www.advantech.com/vi-vn/resources/industry-focus/quyet-dinh-1570qd-evn-dien-mat-troi-mai-nha-dieu-can-biet ; https://vjol.info.vn/tctbgd/article/view/121843 ; (VBHN 52, nghiên cứu trước) | Tóm tắt vendor + bài báo 2025 + văn bản hợp nhất | "Modbus TCP/IP và IEC60870-5-104" | Med | Chưa đọc QĐ 1570 | PR-E-09 |
| E-19 | DNP3 IEEE 1815.2 / AN2018-001; EPRI outstation | https://www.dnp.org/ieee-releases-18152-standard-for-der-communications ; https://restservice.epri.com/publicdownload/000000003002015355/0/Product | DNP-UG + EPRI (qua kết quả tìm kiếm) | Ánh xạ 7-420 sang DNP3 | Med | Trạng thái xuất bản 1815.2 mâu thuẫn | P2 |
| E-20 | CAN BMS: 500 kbps, 1 s, ID 0x351…; tài liệu gốc bị gỡ; thiếu 0x355 → timeout | https://akkudoktor.net/uploads/short-url/dwFYBPwjnfia9tSuhUopj9uGX2u.pdf ; https://community.victronenergy.com/t/connect-diy-bms-via-can-to-cerbo-gx-eigenes-bms-via-can-mit-cerbo-gx-verbinden/37102 ; https://akkudoktor.net/t/pylontech-bms-mit-sma-sunny-island/18019 | Spec Seplos + forum (qua kết quả tìm kiếm) | "Both infos… later withdrawn" | Med | ID khác nhau giữa các hãng | CAN listen-only, DBC theo hãng |
| E-21 | OCPP 2.1 (23/01/2025): V2X, DER control, 15118-20; tương thích logic 2.0.1 | https://openchargealliance.org/ocpp-2-1-is-now-available/ ; https://openchargealliance.org/protocols/open-charge-point-protocol | Trang OCA (qua kết quả tìm kiếm) | "application logic… remains compatible" | High | IEC 63584 chỉ từ nguồn thứ cấp | Theo dõi 2.1, MVP 1.6J |
| E-22 | OCPP 1.6 profiles; Easee TxDefault đè TxProfile; Security WP Ed.3/Ed.4 | https://www.bender.de/docs/charge-controller/OCPP/ocpp-smart-charging/ ; https://developer.easee.com/docs/ocpp-smart-charging ; https://openchargealliance.org/?p=159286 | Doc hãng + OCA (qua kết quả tìm kiếm) | "a 0A default overrides a 20A TxProfile" | Med–High | — | Charger profile theo hãng |
| E-23 | OpenADR 3.0 REST/JSON, 3.1 + MQTT; 3.0 không thay 2.0b; chứng nhận 3/2025 | https://www.openadr.org/assets/OpenADR%20Webinar%20Nov%202023%20-%20From%202.0%20to%203.0.pdf ; https://www.openadr.org/assets/OpenADR%20AR25.pdf ; https://ecommercenews.co.nz/story/openadr-3-0-certification-marks-milestone-in-energy-sector | Slide + báo cáo năm Alliance + báo (qua kết quả tìm kiếm) | "3.1… MQTT support… price clusters" | Med–High | Phiên bản 3.0.1 chưa rõ | DR adapter P2 |
| E-24 | IEEE 2030.5 = mặc định Rule 21, TLS 1.2 + chứng chỉ; chứng nhận bắt buộc 2020 | https://standards.ieee.org/content/dam/ieee-standards/standards/web/documents/presentations/smart_energy_slides.pdf ; https://www.qualitylogic.com/wp-content/uploads/2021/07/Data-Sheet-DER-Workshop.pdf | Slide IEEE + datasheet QualityLogic (qua kết quả tìm kiếm) | "TLS 1.2, Certificates for authentication" | Med | Codibly "80% qua gateway" chưa xác minh | Không ở MVP |
| E-25 | Huawei NB: pull, 5 phút, hạn mức; ghi chỉ OAuth Connect async | https://support.huawei.com/enterprise/en/doc/EDOC1100379184/7a471100/control-apis (nghiên cứu FusionSolar trước) | Tài liệu hãng 24.5.0 | "available only in OAuth Connect mode" | High | — | Cloud chỉ cho lịch chậm |
| E-26 | iSolarCloud: tài liệu sau login, khuyên user chỉ đọc; cộng đồng điều khiển pin | https://docs.eniris.be/da/Controller/Devices/Cloud/ISolarCloud ; https://community.home-assistant.io/t/sungrow-isolarcloud-integration-custom-hacs-sensors-optional-charge-discharge-control/1017858 | Doc bên thứ ba + forum (qua kết quả tìm kiếm) | "tested on one system" | Low–Med | Bộ khóa (API/Access/RSA vs app/secret) mâu thuẫn | Ghi = UNKNOWN |
| E-27 | SMA Monitoring/GridControl/GeoForecast API, sandbox, Live API không cho giám sát liên tục, 308 | https://developer.sma.de/sma-apis ; https://developer.sma.de/sma-sandbox-apis ; https://solytic.com/knowledge/set-up-api-access-sma-monitoring-api/ | Cổng developer hãng + KB (qua kết quả tìm kiếm) | "Not allowed for constant monitoring" | Med–High | — | Connector SMA đọc |
| E-28 | Solis HMAC-SHA1; khoảng 3 lần/5 s/IP | https://usservice.solisinverters.com/support/solutions/articles/73000661192-solis-api-troubleshooting ; https://projects.bentasker.co.uk/gils_projects/issue/utilities/telegraf-plugins/9.html | KB hãng + issue cộng đồng 2023 (qua kết quả tìm kiếm) | "three calls every five seconds" | Med (ký) / Low (rate) | Tên endpoint không thống nhất | Rate limiter chặt |
| E-29 | Growatt V1 token, host theo vùng; Deye eu1-developer, chỉ đọc pin | https://www.home-assistant.io/components/growatt_server/ ; https://mirrors.edge.kernel.org/CPAN/modules/by-module/Config/KORNIX/DeyeCloud-Client-0.0.2.readme ; https://community.home-assistant.io/t/deye-cloud-integration/813153 | Doc HA + client OSS + forum (qua kết quả tìm kiếm) | "does not have this limitation" (V1) | Low–Med | Giới hạn V1 không có số | Chỉ đọc |
| E-30 | Huawei công bố zero feed-in ≤2 s, peak shaving ≤5 s; độ trễ tổng gồm 4 khâu | https://solar.huawei.com/admin/asset/v1/pro/view/bb9458d9373d4502912378db3cbc7f2d.pdf ; https://help.autarco.com/en/hardware/why-am-i-still-exporting-while-i-have-set-my-pv-system-to-zero-export- | Datasheet hãng + help bên thứ ba (qua kết quả tìm kiếm) | "closed-loop control for zero feed-in within 2s" | Med (số do hãng tự công bố) | Agent B L37 gán số này cho SmartLogger5000B; tôi thấy trên datasheet SmartMGC5000B | Vòng nhanh ở edge |
| E-31 | blue'Log XC Modbus Power Control; 104/61850/DNP3 qua PLC chuyển đổi | https://www.meteocontrol.com/fileadmin/Daten/Dokumente/EN/Produkte/On_Site/blue_Log_XM_XC/Data_sheet/blue_Log_XM_XC_Modbus_Power_Control_license_blue_Log_XC_data_sheet_LastMod-2026-01-27_en.pdf | Datasheet hãng 27/01/2026 (qua kết quả tìm kiếm) | "Slave ID 1; Port 502; Delay 1,000 ms" | Med–High | SCADA Interface datasheet chưa xem | Mẫu "PPC + converter" |
| E-32 | Solar-Log Modbus TCP PM: license, 502, ID 1, FC 04/06/16 | https://www.solar-log.com/fileadmin/user_upload/documents/Datenblaetter/en_GB/Komponenten/Kommunikation/SolarLog_Datasheet_Modbus_TCP_PM_EN.pdf | Datasheet hãng (qua kết quả tìm kiếm) | Lệnh P/Q từ thiết bị ngoài | Med–High | — | Chi phí license trong báo giá |
| E-33 | Victron GX MQTT 1883/Modbus 502; ESS Mode 2 thanh ghi 2700 | https://communityarchive.victronenergy.com/questions/95889/multipluss-ii-is-external-control-ess-mode-2-or-3%EF%B9%96childToView=102991.html ; https://mcpservers.org/en/servers/lubosstrejcek/victron-tcp | Forum + trang dự án OSS (qua kết quả tìm kiếm) | "/AcPowerSetpoint… 2700 int16" | Low–Med | Một thread nói thanh ghi 37 | Đối chiếu register list chính thức |
| E-34 | OpenEMS: cycle khoảng 1 s, process image, scheduler; Resend/Aggregated notification; TimescaleDB beta | https://openems.github.io/openems.io/openems/latest/edge/architecture.html ; https://openems.github.io/openems.io/openems/latest/coreconcepts.html ; https://github.com/OpenEMS/openems/releases | Doc + release notes (qua kết quả tìm kiếm) | "a channel's value will never change within a cycle" | Med–High | — | PR-E-16 |
| E-35 | NTP 1–100 ms; PTP µs cần HW timestamping | https://timebeat.app/blog/ptp-vs-ntp ; https://sunplus.atlassian.net/wiki/x/JQB1eQ | Blog vendor + wiki (qua kết quả tìm kiếm) | "software PTP ~100 µs" | Med | — | chrony đủ cho MVP |
| E-36 | Huawei SUN2000 thời gian 40000 (U32, giờ địa phương), múi giờ 43006 | https://community.openhab.org/t/reading-data-from-huawei-inverter-sun-2000-3ktl-10ktl-via-modbus-tcp-and-rtu/87670?page=5 | Forum trích bảng tài liệu Huawei (qua kết quả tìm kiếm) | "Epoch seconds, local time" | Low–Med | SmartLogger dùng 40000/40005 khác | Driver chuẩn hóa UTC |
| E-37 | BESS: BMS→PCS bảo vệ qua dây cứng, EMS qua TCP/RS485/CAN | https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11411391 | Patent USPTO (qua kết quả tìm kiếm) | "hard-wired line for real-time response" | Med (một thiết kế, không phải chuẩn) | — | Cloud/EMS ngoài vòng bảo vệ |

---

## 6. Câu hỏi mở / UNKNOWN

| ID | Câu hỏi | Vì sao quan trọng | Cách kiểm chứng |
|---|---|---|---|
| Q-E-01 | Bảng điểm IEC 104, CA/IOA, cấp điều độ, ngưỡng công suất, chu kỳ, yêu cầu dự phòng và bảo mật theo QĐ 1570/QĐ-EVN và từng PC | Quyết định phạm vi slave 104 (PR-E-09) | Lấy văn bản QĐ 1570. Hỏi 1–2 Công ty Điện lực/A2. Lấy hồ sơ một dự án đã đấu nối |
| Q-E-02 | EVN có chấp nhận điều khiển "bật tắt phát ngược" bằng phần mềm/logger, hay bắt buộc thiết bị/rơ-le riêng? | Kiến trúc DO và trách nhiệm pháp lý | Như trên |
| Q-E-03 | Register map chính thức của Sungrow Logger1000/EMS300CP/SH và cách kích hoạt EMS mode ghi được | Driver P0 thứ 3 | Kênh đối tác Sungrow Việt Nam. Thử trên lab |
| Q-E-04 | EMMA/SmartLogger: tập thanh ghi lộ ra, watchdog cho lệnh remote (có tự hủy khi master mất?), số kết nối tối đa | Fallback an toàn | Tài liệu Huawei "Modbus Interface Definitions" bản mới + thử lab |
| Q-E-05 | Thanh ghi điều khiển nào ghi vào NVM (Huawei, Sungrow, Victron, tủ BESS)? Giới hạn số lần ghi? | PR-E-15 | Hỏi hãng. Đọc ghi chú tài liệu |
| Q-E-06 | Victron Mode 2: có timeout setpoint khi mất master không? Register list chính thức (rev hiện tại) | Driver Victron | CCGX Modbus TCP register list + docs Venus OS |
| Q-E-07 | SunSpec model 715 là gì? Trạng thái hiện hành của 802–805 (TEST hay APPROVED)? Giá trị sentinel 0x8000 | Bảng model §3.3 | SMDX trên GitHub SunSpec / spec hiện hành |
| Q-E-08 | Kênh EMS→CSMS cho giới hạn công suất site (OCPP 2.1 DER control dùng được không?) | Kiến trúc EV (PR-E-10) | Đọc spec OCPP 2.1 phần DER control |
| Q-E-09 | Tủ BESS Trung Quốc phổ biến ở Việt Nam có Modbus TCP northbound với điểm điều khiển P/Q/mode và CCL/DCL không? Họ có cung cấp register map theo hợp đồng không? | Driver P0 thứ 5 | Phỏng vấn nhà phân phối/EPC. Xin tài liệu dưới NDA |
| Q-E-10 | Hạn mức chính thức của Growatt V1, Deye, Solis (bản hiện hành) | Định cỡ connector | Đăng ký tài khoản developer |
| Q-E-11 | SMA GridControl API làm được gì (P/Q setpoint?) và ai được cấp quyền | Đường ghi SMA | developer.sma.de |
| Q-E-12 | Giấy phép: dùng/sửa OpenEMS Edge (EPL-2.0) trong sản phẩm thương mại đóng; thư viện IEC 104/61850/OCPP | PR-E-16 | Pháp lý |
| Q-E-13 | Khối lượng dữ liệu thực tế sau deadband/nén cho site C&I điển hình | Định cỡ buffer/băng thông/chi phí 4G | PoC đo trên site thật |
| Q-E-14 | Huawei OAuth Connect: endpoint/grant/token lifetime, hạn mức ở chế độ OAuth | Connector ghi Huawei | Tài khoản installer + tài liệu (đã là gap từ nghiên cứu trước) |

---

## 7. Vấn đề gửi agent khác

| # | Gửi | Vấn đề | Đề xuất |
|---|---|---|---|
| X-E-01 | Người viết 05 (Domain) | Cần thực thể: `Device`, `DriverProfile@version`, `CapabilityProfile`, `PointDefinition`, `PointMapping`, `Command` (envelope §3.19) + `CommandTransition`, `ControlSource`, `EdgeNode` (clock_state, firmware, config_version) | Dùng quy ước dấu §3.18 (grid import +, ESS discharge +) làm chuẩn domain. Ghi rõ trong glossary |
| X-E-02 | Người viết 06 (Kiến trúc) | Uplink MQTT 5 schema riêng, Sparkplug là đầu ra phụ. Cloud không ghi trực tiếp thiết bị. Ingest idempotent theo `(edge, stream, seq)` và `(point, ts)`. Backfill tách topic. Refresh aggregate ≥7 ngày | Đưa vào ADR: uplink, idempotency, edge runtime (PR-E-16) |
| X-E-03 | Người viết 08 (Tối ưu) | Optimizer chỉ phát `APPLY_SCHEDULE` (khung 15 phút, ≥48 h) và giới hạn. Mọi lệnh có `expires_at`. Edge kẹp theo CCL/DCL hiện tại và báo `APPLIED_CLAMPED`. Optimizer phải đọc feedback này, không giả định setpoint đã được thực thi | Vòng nhanh (<5 s) thuộc edge. Không mô tả là "AI" |
| X-E-04 | Người viết 10 (An toàn) | Modbus/IEC 104 không có xác thực. Cần tách OT LAN, edge là master duy nhất, tường lửa. OCPP ≥ Security Profile 2. Ký số OTA. Chữ ký lệnh (V1). Dongle/logger hãng vẫn có kênh cloud riêng tới hãng (nghiên cứu trước): cần chính sách khách hàng về việc giữ hay chặn kênh này | Đưa vào NFR-SEC. Đánh giá IEC 62351 cho 104 nếu EVN yêu cầu |
| X-E-05 | Người viết 09 (UX/UI) | UI phải hiển thị trạng thái lệnh đầy đủ (SENT/RECEIVED/APPLIED/APPLIED_CLAMPED/FAILED_NO_EFFECT/EXPIRED), quality của điểm (STALE, VENDOR_CLOUD) và trạng thái kiểm chứng driver | Không hiển thị "đã áp dụng" khi chưa có readback |
| X-E-06 | Người viết 11 (Lộ trình) | MVP: edge + Modbus/SunSpec + driver Huawei + công tơ + 1 dòng BESS + MQTT. V1 C&I trung thế: IEC 104 slave (P0), OCPP 1.6J. V2: 61850 MMS, OpenADR, OCPP 2.0.1/2.1 | Kế hoạch lab thiết bị (Huawei SmartLogger/EMMA, Sungrow, 1 tủ BESS, 2 công tơ, 1 charger OCPP) |
| X-E-07 | Người viết 13 (Rủi ro) | R: map Modbus không công bố/thay đổi theo firmware. R: ghi "không tác dụng". R: hãng thay chính sách API (Huawei 9/2025). R: thiết bị không có watchdog setpoint. R: mòn NVM. R: yêu cầu 104 chưa rõ | Gắn Q-E-01…Q-E-14 |
| X-E-08 | Agent B / Người viết 14 (Nguồn) | Ledger B L37 gán "zero-export ≤2 s, peak shaving ≤5 s" cho SmartLogger5000B. Kết quả tìm kiếm của tôi cho thấy câu chữ chính xác nằm trên datasheet **SmartMGC5000B** (URL ở E-30). Photomate gán 2 s cho SmartLogger5000B | Ghi rõ model trong 02/07, hoặc ghi "theo tài liệu Huawei/nhà phân phối" |
| X-E-09 | Người viết 03/04 (Chức năng, Yêu cầu) | Thêm FR-INT về: capability discovery, driver verification status, readback, store-and-forward, clock state, Modbus TCP server xuất lại, IEC 104 slave | Lấy từ bảng G1–G15 §3.12 |
