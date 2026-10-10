# I — Bảo mật, an toàn vận hành và độ tin cậy cho EMS điều khiển từ xa (Agent I)

[← Mục lục](../index.html) · [04 Yêu cầu](../04-business-requirements.md) · [05 Domain](../05-domain-model.html) · [06 Kiến trúc](../06-system-architecture.html) · [07 Tích hợp](../07-device-integration.md) · [08 Tối ưu](../08-energy-optimization.md) · [10 An toàn](../10-security-and-reliability.md) · [13 Rủi ro](../13-open-questions-and-risks.md) · [14 Nguồn](../14-source-register.md) · [15 Mô phỏng](../15-simulators-and-messaging.md)

- Người viết: Agent I (Security & Reliability Reviewer). Ngày: 2026-10-10. Trạng thái: ghi chú nghiên cứu bản 1. Đầu vào chính cho tài liệu **10 (An toàn)**, một phần cho 04, 05, 06, 13.
- **Giới hạn bằng chứng của lượt này (đọc trước khi dùng):**
  - Môi trường chặn tải trang trực tiếp (WebFetch/curl). Khi Agent I bắt đầu, **hạn mức WebSearch dùng chung của lượt (200 truy vấn) đã hết** — mọi truy vấn trả về "web search budget is used up". Agent I **không chạy được truy vấn mới nào**.
  - Vì vậy mọi `[FACT]` trong file này chỉ dựa trên URL **đã có sẵn** trong nghiên cứu FusionSolar trước (`docs/research/fusionsolar/…`, đã đọc ở các lượt trước) hoặc trong ghi chú của Agent A/B/C/E/F/G (phần lớn là "qua kết quả tìm kiếm"). Tôi ghi rõ nguồn gốc ở từng dòng.
  - Nội dung về tiêu chuẩn (IEC 62443, NIST SP 800-82, NISTIR 7628, IEC 62351, ETSI EN 303 645, UL 9540/9540A, IEC 62933, IEEE 1547, NIS2, CRA) và luật Việt Nam (Luật ANM 2018, NĐ 53/2022, NĐ 13/2023, Luật BVDLCN 2025) mà **không có URL** được ghi là **"kiến thức nền, chưa kiểm chứng nguồn trong lượt này"** và gắn nhãn `[INFERENCE]` hoặc `[UNKNOWN]`, **không** gắn `[FACT]`. Edition ghi `UNKNOWN` trừ khi có URL. Không tuyên bố tuân thủ bất kỳ tiêu chuẩn nào.
  - Cần một **lượt kiểm chứng bổ sung** (danh sách truy vấn đề xuất ở §6, Q-I-01…) trước khi tài liệu 10 phát hành bản chính thức.
- Quy ước mã trong file: phát hiện `I-F-NN`, đề xuất dùng mã chung `NFR-SEC-NNN`, `NFR-REL-NNN`, `NFR-OBS-NNN`, `FR-SEC-NNN`; rủi ro ứng viên `I-R-NN` (người viết 13 cấp mã `R-NN`); câu hỏi mở `Q-I-NN`; vấn đề chéo `X-I-NN`; dòng ledger `I-NN`.

---

## 1. Phạm vi & câu hỏi nghiên cứu

### 1.1 Phạm vi

EMS đa site C&I (PV + BESS + lưới + tải + EV charger tùy chọn), kiến trúc **edge-first** (edge kiểu OpenEMS tại site, cloud Java/Spring Boot + Angular, PostgreSQL/TimescaleDB, MQTT; *cập nhật 2026-10-10: frontend nay là React + TypeScript theo quyết định PO, xem [06 ADR-20](../06-system-architecture.html#adr-20)*). Khác với nền tảng giám sát PV trước đây (chủ yếu **chỉ đọc**), EMS này **ghi lệnh** vào PCS, inverter, charger và có thể vào logger của hãng. Rủi ro chuyển từ "lộ dữ liệu" sang **"tác động vật lý"**: xả/sạc sai, phát ngược trái phép, quá tải MBA, hỏng pin, mất điện tải quan trọng, và — ở quy mô đội (fleet) — tác động đồng thời lên lưới.

Ngoài phạm vi: an toàn điện/cháy nổ ở mức thiết bị (do BMS/PCS/rơ-le/thiết kế lắp đặt đảm nhận), chứng nhận đấu nối (thuộc inverter/PCS), SCADA lưới của EVN.

### 1.2 Câu hỏi nghiên cứu

| ID | Câu hỏi | Mục trả lời |
|---|---|---|
| RQ-I1 | Tiêu chuẩn/luật nào áp dụng cho **phần mềm EMS** (cloud + edge), cái nào chỉ áp dụng cho **thiết bị**? Ta nên "thiết kế theo" cái nào, "chứng nhận" cái nào, khi nào? | §3.1 |
| RQ-I2 | Luật Việt Nam về an ninh mạng, lưu trữ dữ liệu trong nước, dữ liệu cá nhân ràng buộc gì cho hosting, log, xuất dữ liệu? | §3.2 |
| RQ-I3 | Mô hình định danh, xác thực, phân quyền (RBAC + scope + ABAC cho lệnh), cô lập tenant? | §3.3, §3.4 |
| RQ-I4 | Định danh thiết bị, kênh edge–cloud, phân vùng OT/IT? | §3.5, §3.6 |
| RQ-I5 | **An toàn lệnh**: envelope, kiểm tra vùng vận hành an toàn, khóa liên động, hai người duyệt, TTL, idempotency, ack/timeout, rate limit, local precedence, E-stop, fail-safe khi mất liên lạc? | §3.7–§3.9 |
| RQ-I6 | Mô hình mối đe dọa (STRIDE) và các ca lạm dụng, đặc biệt **lệnh hàng loạt toàn đội**? | §3.10 |
| RQ-I7 | Sự cố thực tế nào có liên quan, đã kiểm chứng tới đâu? | §3.11 |
| RQ-I8 | Audit, secrets, observability, SLO, backup/DR, mục tiêu khả dụng tách giám sát vs điều khiển? | §3.12–§3.15 |

---

## 2. Phát hiện chính

1. **[INFERENCE]** Cloud EMS **không nằm trong vòng bảo vệ**. Bảo vệ thiết bị (BMS ngắt contactor, PCS chống tách đảo/ride-through, rơ-le chống phát ngược, E-stop cứng) phải hoạt động đúng **kể cả khi cloud và edge đều bị chiếm quyền**. Phần mềm chỉ được đặt setpoint **bên trong** giới hạn native. Cơ sở: phân vai BMS/PCS/edge/cloud trong C §3.7 (`C-energy-domain.md`), A X-04, và nguyên tắc "defense in depth" của IEC 62443/NIST SP 800-82 (kiến thức nền). Đây là nguyên tắc thiết kế số 1.
2. **[FACT]** Huawei SmartLogger3000 dùng kênh **outbound** "Encrypted Modbus TCP" tới hệ quản lý (cổng mặc định 27250), SSL bật mặc định, "TLS1.2 or a later version is recommended"; Modbus TCP không mã hóa bị tắt mặc định và có cảnh báo "data transmitted over this protocol is not encrypted". https://support.huawei.com/enterprise/en/doc/EDOC1100108365/4fbe151e/setting-parameters-for-connecting-to-the-management-system-v300r001c00 (nghiên cứu FusionSolar trước). **[INFERENCE]** Mẫu chuẩn ngành cho gateway: kết nối **từ trong ra** (outbound-only), TLS, không mở cổng inbound tại site. Ta theo mẫu này.
3. **[FACT]** Modbus/IEC 104 tại site **không có xác thực**; Agent E yêu cầu tách OT LAN, edge là master duy nhất, OCPP ≥ Security Profile 2, ký số OTA (`E-device-integration.md` X-E-04). OCPP 1.6J có Security Whitepaper với profile 1 (HTTP Basic, không TLS), 2 (TLS + Basic), 3 (TLS + chứng chỉ client). https://openchargealliance.org/?p=159286 (qua kết quả tìm kiếm, ledger E-22).
4. **[FACT]** Lithuania sửa Luật Điện ngày 12/11/2024: cấm **truy cập từ xa** của công ty Trung Quốc tới hệ mặt trời/gió/lưu trữ > 100 kW; không cấm lắp thiết bị; hiệu lực 1/5/2025 (mới), 1/5/2026 (hiện hữu). https://www.lrt.lt/en/news-in-english/19/2411602/lithuania-passes-law-to-block-chinese-access-to-solar-and-wind-farm-systems ; https://pv-tech.org/lithuania-to-block-chinese-inverters-with-cybersecurity-legislation (nghiên cứu FusionSolar trước). **[INFERENCE]** Xu hướng quản lý nhắm vào **kênh truy cập từ xa** (cloud hãng → thiết bị), không chỉ phần cứng. EMS của ta cũng là một kênh truy cập từ xa → phải chứng minh được ai, từ đâu, ra lệnh gì, giới hạn nào.
5. **[FACT]** Reuters (14–15/5/2025) đưa tin thiết bị liên lạc không có trong tài liệu trong một số inverter/pin Trung Quốc, **không nêu hãng**, dựa trên hai nguồn giấu tên; pv magazine "cannot verify". https://www.pv-magazine.com/2025/05/14/hidden-devices-found-in-chinese-made-inverters-in-the-us-reports-reuters/ . Đánh giá của DOE và các phòng thí nghiệm quốc gia (29/1/2026) trên khoảng 30 inverter: 2 trường hợp liên lạc khác tài liệu, được đánh giá "non-malicious", không có bằng chứng chức năng vô tuyến độc hại. https://www.pv-magazine-india.com/2026/01/29/u-s-authorities-find-no-definitive-evidence-of-hidden-devices-in-chinese-solar-inverters (nghiên cứu FusionSolar trước). **[INFERENCE]** Không được viết "inverter Trung Quốc có backdoor" trong tài liệu. Nhưng phải coi **kênh cloud riêng của hãng** (dongle/logger → cloud hãng) là một đường điều khiển song song nằm ngoài kiểm soát của EMS.
6. **[FACT]** Tháng 11/2024, inverter ở Mỹ, Anh, Pakistan bị vô hiệu hóa từ xa từ Trung Quốc; điều tra cho thấy là **tranh chấp thương mại**, không phải tấn công nhà nước; nguồn không nêu hãng. https://www.defensenews.com/global/europe/2025/05/29/chinese-hold-on-solar-power-tech-raises-fresh-sabotage-fears-in-europe/ (nghiên cứu FusionSolar trước). **[UNKNOWN]** Việc gán sự cố cho Deye/Sol-Ark **chưa được kiểm chứng** (nghiên cứu trước đã ghi rõ). **[INFERENCE]** Đây là ca lạm dụng thực tế của mẫu "một tài khoản cloud có quyền ghi → tác động hàng loạt thiết bị" → cần giới hạn bán kính tác động (blast radius) ở cấp đội.
7. **[FACT]** Forescout "SUN:DOWN" (27/3/2025): 46 lỗ hổng mới ở sản phẩm Sungrow, Growatt, SMA (đã vá); 80% lỗ hổng hệ mặt trời công bố trong 3 năm trước là high/critical. https://forescout.com/press-releases/forescout-vedere-labs-uncovers-severe-systemic-security-risks-in-global-solar-power-infrastructure . CCC (2026) phát hiện cập nhật firmware và điều khiển từ xa **không xác thực** ở microinverter Hoymiles. https://cybernews.com/security/china-solar-inverters-hack/ (nghiên cứu FusionSolar trước). **[INFERENCE]** Lỗ hổng phổ biến nhất nằm ở **cloud/API hãng và cơ chế cập nhật**, chính là các bề mặt EMS của ta cũng sẽ có.
8. **[FACT]** Chính phủ Hà Lan (9/7/2025): yêu cầu an ninh mạng của RED áp dụng từ 1/8/2025; CRA áp dụng từ 12/2027. https://solarmagazine.nl/nieuws-zonne-energie/i41070/kabinet-verscherpt-toezicht-op-chinese-omvormers-zonnepanelen-verbod-kill-switch-bestaat-al (nghiên cứu FusionSolar trước). **[INFERENCE]** Với khách EU (nếu sau này mở rộng), phần mềm EMS bán kèm/phân phối như sản phẩm có thể rơi vào CRA; dịch vụ SaaS thuần thì không phải "product with digital elements" theo cách hiểu phổ biến — cần tư vấn pháp lý (Q-I-06). Thị trường mục tiêu hiện tại là Việt Nam nên CRA/NIS2 là **P2**.
9. **[FACT]** Đối thủ tuyên bố bảo mật rất khác nhau: Ampowr (ISO 27001, NIS2, host EU — tự tuyên bố) https://ampowr.com/nis2-compliance/ ; Schneider có chương trình IEC 62443 cho EcoStruxure Power, kiến trúc "validated and certified by a third party according to IEC 62443-3-3" (phạm vi với EMA cloud chưa rõ) https://www.productinfo.schneider-electric.com/esxp_digital_apps_iec/transverse/English/BM_ESXP_DG_Transverse_Section_IEC_0001148082.xml/$/ESXP_DG_SYSD_Cyber_ISA_IEC_0001157270 ; chứng chỉ IEC 62443-4-1/4-2 của WinCC OA hiệu lực đến 2026-02-06. https://www.winccoa.com/documentation/WinCCOA/3.20/en_US/iec_62443/topics/iec_62443_certification.html (Agent B, qua kết quả tìm kiếm). Sungrow có ISO/IEC 27019 từ BSI. https://dl.sungrowpower.com/en/sungrow-achieves-iso-iec-27019-and-multiple-cybersecurity-management-system-certifications-from-bsi . **[INFERENCE]** Người mua C&I/EVN sẽ hỏi IEC 62443 + ISO 27001. Ta chỉ tuyên bố khi có số chứng chỉ, phạm vi, hạn.
10. **[FACT]** Huawei tách **đồng ý của chủ hệ thống** (consent) cho installer: "O&M Authorization", quyền đặt thông số, quyền API; bên thứ ba qua OAuth, chủ hệ thống thu hồi được. https://digitalpower.huawei.com/en/eu-data-act ; https://e-solarshop.ro/wp-content/uploads/2025/07/fusionsolar-app-manual5925.pdf . API điều khiển cloud của Huawei chỉ có ở "OAuth Connect mode"; API VPP async, "không gọi lại trước khi task hoàn tất", ≤10 thiết bị/thao tác với tham số (lỗi 20018) (nghiên cứu FusionSolar `workflows_data_model.md`, `source_code_clients_2.md`). **[INFERENCE]** Quyền điều khiển nên là **quyền riêng do chủ tài sản cấp**, có hạn, thu hồi được — tách khỏi quyền xem.
11. **[FACT]** SunSpec (12/2023): nhiều inverter **đã có UL 1741 SB** vẫn có lỗi tương tác ở giao diện SunSpec Modbus. https://sunspec.org/communication-interface-defects-revealed-inul-1741-sb-certified-inverters/ (Agent E, qua kết quả tìm kiếm). IEEE 1547-2018 yêu cầu giao diện DER hỗ trợ ít nhất một trong IEEE 2030.5, IEEE 1815 (DNP3), SunSpec Modbus. https://sunspec.org/sunspec-1547-initiative/ . **[INFERENCE]** UL 1741 SB / IEEE 1547 là chứng nhận **đấu nối của inverter/PCS**, không phải chứng nhận EMS và không phải chứng nhận an ninh mạng. EMS không được dùng chúng làm bằng chứng "an toàn khi điều khiển từ xa"; phải kiểm thử readback (Agent E: trạng thái `FAILED_NO_EFFECT`).
12. **[INFERENCE]** Cơ chế **watchdog / reversion timeout** ở thiết bị là bắt buộc để fail-safe khi mất liên lạc: thiết bị phải tự quay về chế độ mặc định khi master không làm mới setpoint trong T giây. Theo kiến thức nền (chưa kiểm chứng trong lượt này): SunSpec model 123 (legacy) có các trường `*_RvrtTms`; model 704 có các trường thời gian hoàn nguyên tương tự; SMA có tham số fallback khi mất tín hiệu điều khiển; OpenEMS Controller Api (Modbus/TCP, REST) có `apiTimeout`. Agent E đã đánh dấu thiết bị không có watchdog là rủi ro (`requires_native_fallback=true`). → Chi tiết §3.9.
13. **[INFERENCE]** Với kiến trúc edge-first, **mục tiêu khả dụng của cloud có thể thấp hơn của edge**: mất cloud chỉ làm mất tối ưu/giám sát từ xa, không làm mất an toàn — **nếu** edge có kế hoạch offline ≥48 h và fallback (B PR-B02, E PR-E-05). Vì vậy đặt SLO tách: edge điều khiển cục bộ (cao nhất), kênh lệnh cloud→edge (trung bình, có TTL), giám sát/UI (trung bình), báo cáo (thấp).
14. **[UNKNOWN]** Hiện trạng chính xác của khung pháp lý Việt Nam năm 2026 (Luật An ninh mạng 2018 và khả năng đã có luật thay thế/hợp nhất; NĐ 53/2022; Luật Bảo vệ dữ liệu cá nhân 2025 và nghị định hướng dẫn; NĐ 13/2023 còn hiệu lực hay bị thay thế). Chưa kiểm chứng được trong lượt này. Thiết kế phải **giả định hosting dữ liệu tại Việt Nam là lựa chọn mặc định** cho khách Việt Nam (§3.2).
15. **[PROPOSAL]** Tách kiến trúc thành **hai mặt phẳng**: *monitoring plane* (chỉ đọc, connector cloud hãng, ingest, dashboard) và *control plane* (lệnh, ký số, phê duyệt, arbiter edge). Hai mặt phẳng dùng **danh tính dịch vụ khác nhau, credential khác nhau, topic MQTT khác nhau, quyền DB khác nhau**. Connector cloud hãng mặc định **chỉ đọc**; ghi qua cloud hãng là ngoại lệ có cờ riêng (E PR-E-11).

---

## 3. Phân tích chi tiết

### 3.1 Bản đồ tiêu chuẩn: cái gì áp dụng cho EMS, cái gì cho thiết bị

Ký hiệu cột "Bằng chứng": **K** = kiến thức nền, chưa kiểm chứng URL trong lượt này; **U** = có URL trong nghiên cứu hiện có.

| Tiêu chuẩn / văn bản | Đối tượng | Áp dụng cho EMS của ta? | Cách dùng đề xuất | Bằng chứng |
|---|---|---|---|---|
| **IEC 62443-3-2** (đánh giá rủi ro, zone & conduit) | Hệ thống IACS | **Có** — phương pháp chia zone/conduit, đặt SL-T cho từng zone | Dùng làm khung phân vùng §3.6 | K |
| **IEC 62443-3-3** (yêu cầu bảo mật hệ thống, SR/RE theo 7 FR, SL 1–4) | Hệ thống (cloud + edge + mạng site) | **Có** | "Thiết kế theo": mục tiêu SL-T 2 cho zone điều khiển site và control plane cloud; SL-T 1–2 cho monitoring | K; Schneider có kiến trúc chứng nhận 3-3 (U, finding 9) |
| **IEC 62443-4-1** (quy trình phát triển an toàn, ML 1–4) | Nhà cung cấp sản phẩm | **Có** (ta là nhà sản xuất phần mềm/edge) | Áp quy trình SDL: threat model, secure coding, SAST/DAST, quản lý lỗ hổng, cập nhật, tài liệu hardening | K |
| **IEC 62443-4-2** (yêu cầu kỹ thuật thành phần: software app, embedded device, host device, network device) | Thành phần | **Có** cho **edge gateway** (embedded/host device) và ứng dụng edge | Mục tiêu chứng nhận 4-2 SL 2 cho edge ở V2 | K; WinCC OA có 4-1/4-2 (U) |
| **IEC 62443-2-4** (yêu cầu với nhà cung cấp dịch vụ tích hợp/bảo trì) | Integrator, O&M | **Có** cho đội triển khai và installer đối tác | Quy trình commissioning, quản lý tài khoản, truy cập từ xa có giám sát | K |
| **IEC 62443-2-1** (chương trình bảo mật của chủ tài sản) | Chủ site | Gián tiếp | Cung cấp tài liệu để chủ site đưa EMS vào chương trình của họ | K |
| **ISO/IEC 27001** (+27017/27018 cloud, 27019 năng lượng) | Tổ chức vận hành cloud | **Có** cho vận hành SaaS | Mục tiêu chứng nhận 27001 khi có khách lớn; 27019 là điểm cộng (Sungrow có, U) | K + U |
| **NIST SP 800-82 Rev. 3** (OT security, 2023) | Hướng dẫn OT | Tham chiếu | Dùng cho kiến trúc phân vùng, overlay biện pháp OT | K |
| **NISTIR 7628 Rev. 1** (smart grid) | Hướng dẫn smart grid | Tham chiếu | Danh mục giao diện logic và yêu cầu bảo mật cho DER/EMS | K |
| **IEC 62351** (bảo mật truyền thông hệ thống điện; phần 3 TLS cho profile TCP/IP, phần 5 cho IEC 60870-5 & DNP3, phần 6 cho 61850, phần 8 RBAC, phần 9 quản lý khóa) | Giao thức SCADA | **Có điều kiện** — chỉ khi EVN/điều độ yêu cầu bảo mật kênh IEC 104 | Chưa áp ở MVP; theo dõi yêu cầu QĐ 1570 (E: IEC 62351 với EVN là UNKNOWN) | K |
| **IEEE 2030.5 / CSIP**, **IEEE 1547.3** (hướng dẫn an ninh mạng DER) | DER ở Mỹ | Tham chiếu | Mẫu PKI thiết bị, TLS bắt buộc | K |
| **ETSI EN 303 645** (IoT tiêu dùng, 13 nhóm điều khoản) / **EN 18031** (RED) | Thiết bị tiêu dùng / thiết bị vô tuyến | Không trực tiếp (C&I, không phải consumer). EN 18031 áp cho thiết bị vô tuyến bán ở EU | Dùng như checklist tối thiểu cho edge: không mật khẩu mặc định chung, công bố lỗ hổng, cập nhật an toàn | K; Huawei có chứng nhận EN 18031-1 (U, nghiên cứu trước) |
| **UL 1741 SB / IEEE 1547-2018 / IEEE 1547.1-2020** | Inverter/PCS đấu nối | **Không** (không phải chứng nhận EMS) | Chỉ đọc cấu hình grid code; cấm sửa từ cloud (C X-C06) | U (finding 11) |
| **UL 9540 / UL 9540A / IEC 62933-5-x** | Hệ thống BESS (an toàn điện, cháy, lan truyền thermal runaway) | **Không** cho cloud. EMS **không thay thế** BMS/hệ PCCC | EMS đọc trạng thái BMS/hệ chữa cháy; không ghi lệnh nào ảnh hưởng bảo vệ | K; C đã nêu 62933-2-1 chưa đọc toàn văn |
| **EU NIS2 (Directive 2022/2555)** | Thực thể thiết yếu/quan trọng ở EU (năng lượng thuộc phụ lục) | Không áp tại VN. Nếu có khách EU là thực thể NIS2, ta là **nhà cung cấp trong chuỗi cung ứng** của họ | P2 | K; Ampowr dựa vào NIS2 (U) |
| **EU CRA (Regulation 2024/2847)** | Sản phẩm có phần tử số bán ở EU | Edge gateway + phần mềm cài đặt **có thể** thuộc phạm vi nếu bán ở EU | P2; ghi nhận mốc 12/2027 | U (Hà Lan, finding 8) + K |

**Security Level (kiến thức nền, cần kiểm chứng câu chữ):** SL1 = chống vi phạm ngẫu nhiên; SL2 = chống tấn công cố ý bằng phương tiện đơn giản, ít tài nguyên, kỹ năng chung; SL3 = phương tiện tinh vi, tài nguyên vừa, kỹ năng chuyên IACS; SL4 = tinh vi, tài nguyên lớn (cấp quốc gia). Bảy FR: IAC (định danh & xác thực), UC (kiểm soát sử dụng), SI (toàn vẹn hệ thống), DC (bảo mật dữ liệu), RDF (hạn chế luồng dữ liệu), TRE (phản ứng kịp thời với sự kiện), RA (khả dụng tài nguyên).

**[INFERENCE] Mục tiêu SL hợp lý cho C&I Việt Nam**: SL-T 2 cho zone điều khiển (edge + OT LAN + control plane cloud). SL3 đòi hỏi các biện pháp (ví dụ xác thực đa yếu tố cho mọi giao diện con người, phân tách vật lý mạnh hơn, chống giả mạo phần cứng) vượt ngân sách MVP; cân nhắc SL3 cho site lớn kết nối điều độ (QĐ 1570) ở V2.

### 3.2 Khung pháp lý Việt Nam (chưa kiểm chứng — tất cả cần lượt xác minh)

| Văn bản (theo kiến thức nền) | Nội dung liên quan EMS | Nhãn | Hệ quả |
|---|---|---|---|
| Luật An ninh mạng 2018 (số 24/2018/QH14), hiệu lực 1/1/2019 | Điều 26 khoản 3: doanh nghiệp trong/ngoài nước cung cấp dịch vụ trên mạng viễn thông/Internet tại VN có thu thập, khai thác dữ liệu người dùng VN phải lưu trữ dữ liệu tại VN theo quy định Chính phủ | [INFERENCE] (K) | Hosting VN mặc định |
| Nghị định 53/2022/NĐ-CP (hiệu lực 1/10/2022) | Hướng dẫn Luật ANM. Theo hiểu biết nền: **doanh nghiệp trong nước** phải lưu dữ liệu (dữ liệu cá nhân người dùng VN, dữ liệu do người dùng tạo ra, dữ liệu về mối quan hệ người dùng) tại VN; doanh nghiệp nước ngoài chỉ phải lưu trữ/lập chi nhánh **khi có yêu cầu** của Bộ Công an sau vi phạm. Thời hạn lưu trữ tối thiểu 24 tháng; nhật ký hệ thống tối thiểu 12 tháng | [INFERENCE] (K) — số tháng **phải kiểm chứng** | Nếu ta là doanh nghiệp VN → dữ liệu người dùng VN ở DC trong nước; audit/log ≥ 12 tháng |
| Nghị định 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân (hiệu lực 1/7/2023) | Đồng ý của chủ thể dữ liệu, hồ sơ đánh giá tác động xử lý DLCN, hồ sơ chuyển DLCN ra nước ngoài, thông báo vi phạm trong 72 h | [INFERENCE] (K) | Lập DPIA, quy trình thông báo 72 h |
| Luật Bảo vệ dữ liệu cá nhân 2025 (theo kiến thức nền: số 91/2025/QH15, thông qua 26/6/2025, hiệu lực 1/1/2026) | Nâng NĐ 13 lên luật; xử phạt theo % doanh thu cho chuyển DLCN trái phép ra nước ngoài | [UNKNOWN] — số hiệu, ngày, mức phạt cần kiểm chứng; nghị định hướng dẫn chưa xác định | Theo dõi; NĐ 13 có thể đã bị thay thế |
| Luật An toàn thông tin mạng 2015 + NĐ 85/2016 (phân loại hệ thống thông tin theo cấp độ 1–5) | Có thể áp khi khách hàng là DN nhà nước/EVN | [UNKNOWN] | Hỏi khách EVN-linked |
| QĐ 1570/QĐ-EVN (kết nối giám sát/điều khiển với cấp điều độ) | Kênh IEC 104/Modbus TCP qua VPN/APN riêng | [FACT] tóm tắt qua E/A (qua kết quả tìm kiếm) | Kênh điều độ là conduit riêng, ưu tiên cao nhất (`source=GRID_OPERATOR`) |

**Dữ liệu EMS có phải "dữ liệu cá nhân"?** [INFERENCE] Phần lớn telemetry C&I là dữ liệu doanh nghiệp. Nhưng: tài khoản người dùng (tên, email, SĐT), nhật ký thao tác gắn người, vị trí site của hộ kinh doanh cá thể, phiên sạc EV gắn người lái/biển số → là DLCN. Hồ sơ phụ tải theo thời gian có thể suy ra hành vi. → Phân loại dữ liệu (§3.4.4).

### 3.3 Định danh và xác thực (người dùng)

| Hạng mục | Đề xuất | Lý do |
|---|---|---|
| Giao thức | **OIDC** (Authorization Code + PKCE cho SPA (ghi chú gốc: Angular; nay là React, [06 ADR-20](../06-system-architecture.html#adr-20)) và app mobile), access token JWT ngắn hạn (5–10 phút), refresh token xoay vòng (rotation + phát hiện tái sử dụng) | Chuẩn, hỗ trợ SSO doanh nghiệp |
| IdP | Keycloak tự host (hợp stack Java, chạy được tại DC VN) hoặc IdP managed có vùng VN [PROPOSAL] | Lưu trú dữ liệu |
| SSO doanh nghiệp | Federation OIDC/SAML theo tenant (Azure AD/Entra, Google Workspace) — V1 | Khách C&I lớn yêu cầu |
| MFA | **Bắt buộc** cho mọi vai trò có quyền ghi (Operator trở lên) và mọi admin; khuyến nghị cho Viewer. Ưu tiên **WebAuthn/passkey**, TOTP là phương án phụ; **không** dùng SMS OTP làm yếu tố duy nhất | Lệnh vật lý |
| Step-up auth | Lệnh "nguy hiểm" (§3.7.4) yêu cầu xác thực lại MFA trong 5 phút gần nhất (`auth_time`, `acr` claim) | Chống chiếm phiên |
| Phiên | Idle timeout 30 phút (web), tuyệt đối 12 h; app mobile: refresh token 30 ngày nhưng **không** cho lệnh nguy hiểm nếu chưa step-up | Cân bằng UX |
| Tài khoản máy (API client) | OAuth2 client credentials, scope tối thiểu, **IP allow-list tùy chọn**, hạn tối đa 1 năm, mỗi client gắn tenant; client **mặc định chỉ đọc** | Học từ Huawei Northbound/OAuth Connect (finding 10) |
| Chống dò mật khẩu | Rate limit đăng nhập theo user + IP, khóa mềm, cảnh báo; kiểm mật khẩu lộ (danh sách breach) | — |
| Tài khoản installer/hỗ trợ | Truy cập vào tenant khách **chỉ qua grant có hạn** do chủ tenant cấp (kiểu "O&M Authorization"), ghi audit; nhân viên vendor dùng "break-glass" có phê duyệt | Finding 10, IEC 62443-2-4 (K) |

### 3.4 Phân quyền và cô lập tenant

#### 3.4.1 Mô hình: RBAC + phạm vi tài nguyên + ABAC cho lệnh

- **Cây tài nguyên**: `Organization (tenant) → Portfolio/Region (tùy chọn) → Site → Asset group → Device`. Học từ FusionSolar: Company tree + Role + DataScope (nghiên cứu trước `workflows_data_model.md`).
- **Role binding** = (principal, role, scope_node). Quyền kế thừa xuống cây.
- **Vai trò đề xuất**:

| Vai trò | Xem | Cấu hình site | Lệnh thường (đổi mode, lịch, setpoint trong envelope) | Lệnh nguy hiểm | Duyệt (approver) | Quản trị user |
|---|---|---|---|---|---|---|
| Viewer (chủ đầu tư, kế toán) | ✓ | – | – | – | – | – |
| Analyst | ✓ + xuất dữ liệu | – | – | – | – | – |
| Operator (O&M) | ✓ | – | ✓ | Yêu cầu (cần duyệt) | – | – |
| Site Engineer (installer đã được cấp) | ✓ | ✓ (driver, map, envelope đề xuất) | ✓ | Yêu cầu | – | – |
| Control Supervisor | ✓ | – | ✓ | Yêu cầu | ✓ | – |
| Org Admin | ✓ | ✓ | – (mặc định **không** có quyền lệnh; phải tự gán Operator) | – | – | ✓ |
| Grid Operator (nguồn hệ thống, không phải người) | – | – | `SET_REVERSE_FEED_BLOCK`, giới hạn P | Theo hợp đồng | – | – |
| Vendor Support (break-glass) | Có hạn | Có hạn | – | – | – | – |

- **Tách nhiệm vụ (SoD)**: người tạo lệnh nguy hiểm ≠ người duyệt; Org Admin không tự động có quyền lệnh; người sửa **envelope an toàn** ≠ người phê duyệt envelope.
- **ABAC cho lệnh** (Policy Decision Point — ví dụ OPA/Cedar, hoặc engine nội bộ): quyết định dựa trên thuộc tính
  - chủ thể: role, MFA gần đây (`auth_time`), loại client (người/máy), mạng nguồn;
  - tài nguyên: `site.control_enabled`, `site.local_remote_switch == REMOTE`, `device.driver_verification_status == VERIFIED`, `site.commissioning_state == IN_SERVICE`, `site.size_kW`;
  - hành động: `command.type`, `danger_class`, độ lớn thay đổi ΔP, TTL;
  - ngữ cảnh: số lệnh trong cửa sổ, tổng MW đội đang bị lệnh, giờ (ngoài giờ hành chính → cần duyệt), có sự kiện bảo mật đang mở.
- Ví dụ chính sách: *"Operator được `SET_ESS_P` trên site S nếu: có binding Operator trên S hoặc tổ tiên; S.control_enabled; MFA ≤ 12 h; |P| ≤ envelope.P_max; TTL ≤ 1 h; fleet_budget còn đủ."*

#### 3.4.2 Cô lập tenant — so sánh

| Phương án | Cách làm | Ưu | Nhược | Khi nào |
|---|---|---|---|---|
| **A. Shared schema + PostgreSQL Row-Level Security (RLS)** | Mọi bảng có `tenant_id`; `CREATE POLICY … USING (tenant_id = current_setting('app.tenant_id')::uuid)`; `ALTER TABLE … FORCE ROW LEVEL SECURITY`; ứng dụng dùng role DB **không phải owner, không BYPASSRLS**; đặt `SET LOCAL app.tenant_id` trong mỗi transaction | Rẻ, một lần migrate, hợp nhiều tenant nhỏ (installer VN) | Lỗi cấu hình pool (quên `SET LOCAL`) → rò dữ liệu; owner/superuser bỏ qua RLS nếu không FORCE; hiệu năng với policy phức tạp; **[UNKNOWN]** RLS trên continuous aggregate của TimescaleDB (theo kiến thức nền có hạn chế — cần kiểm chứng) | **Mặc định MVP** |
| B. Schema per tenant | Mỗi tenant một schema, `search_path` | Cô lập logic rõ hơn | Migration N lần; hypertable/cagg nhân bản; khó ở >500 tenant | Ít dùng |
| C. Database/cluster per tenant (silo) | DB riêng, có thể DC riêng | Cô lập mạnh, đáp ứng lưu trú/hợp đồng riêng, khôi phục riêng | Đắt, vận hành nặng | Khách lớn/EVN-linked, yêu cầu on-prem |

**[PROPOSAL] Hybrid**: A cho đa số + C (silo/on-prem) là SKU riêng. Bổ sung **lớp thứ hai** ngoài RLS: mọi repository Spring kèm `tenant_id` trong truy vấn (defense in depth), test tự động "cross-tenant" chạy trong CI cho **mọi** endpoint, khóa mã hóa dữ liệu nhạy cảm theo tenant (envelope encryption).

**Cô lập ở các lớp khác**: MQTT ACL theo `tenant/site/edge`; object storage prefix + policy theo tenant; cache key có tenant; search index có filter bắt buộc; hàng đợi job có `tenant_id`; rate limit theo tenant (chống noisy neighbour).

#### 3.4.3 Tách tích hợp đọc và tích hợp ghi

| Thuộc tính | Monitoring integration (đọc) | Control integration (ghi) |
|---|---|---|
| Ví dụ | Connector cloud Huawei/Sungrow/Solis/Deye (polling), import CSV, Modbus đọc | Edge arbiter → PCS/inverter/charger; (ngoại lệ) Huawei OAuth Connect control API |
| Service identity | `svc-ingest-*` | `svc-command-*` |
| Credential hãng | Token chỉ đọc nếu hãng cho phép phân quyền | Credential riêng, lưu riêng (vault path khác), chỉ control plane đọc được |
| Topic MQTT | `…/telemetry`, `…/events`, `…/state` (edge publish) | `…/cmd` (cloud publish, **có chữ ký**), `…/cmd/ack` (edge publish) |
| Quyền DB | Ghi bảng timeseries, không đọc bảng lệnh | Ghi bảng `command`, `approval`, `audit`; đọc envelope |
| Mạng | Có thể chạy ở cụm chung | Cụm/namespace riêng, egress hạn chế |
| Deploy | Release thường | Release có review bảo mật, canary, có thể đóng băng |
| Bật/tắt | Theo site | **Mặc định TẮT**; bật theo site sau commissioning + chủ tài sản ký đồng ý |

#### 3.4.4 Phân loại dữ liệu

| Lớp | Ví dụ | Mã hóa nghỉ | Lưu trú | Xuất |
|---|---|---|---|---|
| D0 Công khai | Tài liệu sản phẩm | – | – | Tự do |
| D1 Nội bộ tenant | Telemetry, KPI, cảnh báo | Có (đĩa/DB) | VN mặc định | Theo RBAC, audit |
| D2 Nhạy cảm vận hành | Cấu hình site, envelope, sơ đồ một sợi, IP OT, credential hãng | Có + khóa theo tenant cho secrets | VN | Chỉ Site Engineer+, audit, watermark |
| D3 Dữ liệu cá nhân | User, phiên sạc EV gắn người, audit gắn người | Có | VN; chuyển ra ngoài cần hồ sơ | Theo yêu cầu chủ thể |
| D4 Bí mật hệ thống | Khóa CA, khóa ký lệnh | HSM/KMS, không xuất | – | Không bao giờ |

### 3.5 Định danh thiết bị và kênh edge–cloud

**Định danh edge**
- Mỗi edge có cặp khóa **sinh trong secure element/TPM 2.0** (không xuất được khóa riêng), chứng chỉ **X.509 riêng** do CA thiết bị riêng của ta ký (CA gốc offline; CA trung gian online trong HSM/KMS).
- Subject: `CN=edge-<uuid>`, SAN URI `urn:ems:edge:<uuid>`; tenant/site **không** nhúng vào cert (vì edge có thể chuyển site) — ánh xạ edge→site nằm ở registry cloud, ràng buộc khi commissioning.
- **Provisioning**: (1) xưởng nạp cert "birth" (IDevID kiểu IEEE 802.1AR) chỉ đủ quyền gọi endpoint `enroll`; (2) installer quét QR trên app, gán edge vào site → cloud cấp cert vận hành (LDevID) qua CSR (EST hoặc ACME-like); (3) cert vận hành có hạn **90 ngày**, tự gia hạn ở 2/3 thời hạn; gia hạn thất bại 14 ngày → cảnh báo; (4) thu hồi: danh sách chặn tại broker (tra mỗi lần kết nối) + hạn ngắn, không dựa vào CRL/OCSP phía thiết bị.
- Edge **không có mật khẩu mặc định chung**; UI cục bộ dùng mật khẩu ngẫu nhiên theo thiết bị in trên nhãn + bắt đổi lần đầu (phù hợp tinh thần ETSI EN 303 645/EN 18031 — K).

**Kênh truyền**
- Edge **chỉ kết nối ra** (outbound) tới broker MQTT 5 qua TLS 1.3 (cho phép 1.2 với cipher AEAD), **mTLS**, cổng 8883 hoặc 443 (qua WebSocket nếu tường lửa khách chặn). Không mở cổng inbound tại site; không cần IP tĩnh. Tham chiếu: SmartLogger outbound TLS (finding 2).
- Truy cập hỗ trợ từ xa (SSH/UI edge): **reverse tunnel theo yêu cầu**, do edge mở khi nhận lệnh có ký + được chủ site cho phép, tự đóng sau 2 h, ghi phiên. Không VPN thường trực tới mạng OT của khách.
- **ACL broker**: edge X chỉ publish `ems/v1/<edge-id>/up/#`, chỉ subscribe `ems/v1/<edge-id>/down/#`. Ánh xạ tenant/site ở phía cloud. Wildcard subscribe bị cấm với client edge.
- **Lệnh có chữ ký ở tầng ứng dụng** (không chỉ dựa vào TLS): dịch vụ ký lệnh (Command Signer, khóa trong KMS/HSM, tách khỏi broker) ký JWS (ECDSA P-256 hoặc Ed25519) trên envelope chuẩn hóa (Agent E §3.19). Edge kiểm: chữ ký, `kid` thuộc danh sách tin cậy (pin trong config đã ký), `target.edge_id` = chính nó, `valid_from ≤ now ≤ expires_at` (đồng hồ edge phải `SYNCED` — E: clock_state), `command_id` chưa thấy, **`seq` tăng đơn điệu theo (site, signer)** → chống replay kể cả khi broker bị chiếm.
- **Ack** do edge ký bằng khóa thiết bị (chống giả ack "APPLIED").
- **OTA**: firmware/container edge ký số (ví dụ cosign/TUF-style metadata với khóa root offline, khóa targets có hạn), cài kiểu A/B có rollback; không cho hạ phiên bản (anti-rollback counter) trừ khi có lệnh ký đặc biệt.
- **Config push**: cấu hình driver/envelope/limit là tài liệu có version + chữ ký; edge từ chối config không ký.

### 3.6 Phân vùng OT/IT (zones & conduits, tham chiếu Purdue)

Mô hình Purdue (kiến thức nền): L0 quá trình/cảm biến, L1 điều khiển cơ bản (PLC, BMS, PCS controller), L2 giám sát khu vực (HMI, controller site), L3 vận hành site, L3.5 DMZ công nghiệp, L4–5 IT doanh nghiệp/cloud. [INFERENCE] Ánh xạ cho EMS:

| Zone | Thành phần | Purdue | SL-T đề xuất | Ghi chú |
|---|---|---|---|---|
| Z0 Bảo vệ cứng | Rơ-le bảo vệ, E-stop, contactor BMS, rơ-le chống phát ngược, hệ PCCC | L0–L1 | Không phần mềm nào của ta ghi vào | Đi dây cứng, độc lập |
| Z1 Thiết bị điều khiển | PCS, inverter, BMS, công tơ, charger, logger hãng | L1 | Theo thiết bị (thường SL0–1 vì Modbus không xác thực) | Bù bằng cô lập mạng |
| Z2 Controller site | Edge EMS (OT LAN side) | L2 | **SL2** | Edge là **Modbus master duy nhất** |
| Z3 DMZ site | Edge (WAN side) — hai NIC tách biệt; không định tuyến giữa WAN và OT LAN | L3.5 | SL2 | Edge không bridge, không NAT giữa hai phía |
| Z4 Kênh điều độ | IEC 104 slave tới điều độ qua VPN/APN riêng | Conduit riêng | Theo EVN | Interface/NIC hoặc VLAN riêng |
| Z5 Cloud control plane | Command API, Signer, Approval, Arbiter cloud | L4 | SL2 | Namespace/tài khoản cloud riêng |
| Z6 Cloud monitoring plane | Ingest, TSDB, dashboard, connector cloud hãng | L4 | SL1–2 | — |
| Z7 Người dùng | Web/mobile | L5 | — | MFA |
| Z8 Cloud hãng (ngoài kiểm soát) | Dongle/SmartLogger → cloud Huawei, … | Ngoài | — | Chính sách giữ/chặn (§3.10, X-E-04) |

**Conduit và luật tường lửa tối thiểu (edge)**:
- WAN → Internet: chỉ outbound 8883/443 tới broker và endpoint OTA, NTP (ưu tiên NTS hoặc NTP nội bộ), DNS. **Không inbound.**
- OT LAN: edge → thiết bị: Modbus TCP 502 / cổng hãng (ví dụ SolarEdge 1502 — E), OCPP WebSocket (charger → edge, Security Profile ≥2), CAN/RS485 vật lý. Chặn thiết bị OT ra Internet trừ khi chủ site chọn giữ kênh cloud hãng (khi đó đi qua VLAN riêng, không qua edge).
- Không cho phép công cụ engineering của installer kết nối OT LAN khi edge đang `REMOTE` mà không chuyển sang `LOCAL/MAINTENANCE` (xung đột master Modbus).

### 3.7 An toàn lệnh (command safety)

#### 3.7.1 Nguyên tắc

1. **Cloud gửi ý định, edge quyết định.** Cloud gửi lịch/mục tiêu có hạn; edge arbiter + limit chain (C §3.7) tính setpoint cuối. Cloud không ghi thẳng thanh ghi thiết bị (C, E X-E-02).
2. **Mọi lệnh có hạn** (`expires_at` bắt buộc; E §3.19). Không có setpoint vô thời hạn từ xa.
3. **Kiểm tra ở ba nơi**: (a) cloud — chính sách, quyền, envelope, ngân sách đội; (b) edge — chữ ký, hạn, envelope cục bộ (bản đã ký), trạng thái thiết bị, local/remote; (c) thiết bị — giới hạn native, watchdog. Lớp sau **không tin** lớp trước.
4. **Không lệnh nào được thay đổi thông số bảo vệ** (grid code, ngưỡng BMS, cài đặt rơ-le) từ cloud. Những thông số đó là "read-only, so sánh với hồ sơ" (C X-C06, E bảng SunSpec 705–712).
5. **Fail-safe về trạng thái đã định trước, không phải "giữ nguyên".** `on_expiry = REVERT_DEFAULT` là mặc định (E).

#### 3.7.2 Vùng vận hành an toàn (Safe Operating Envelope — SOE)

SOE là tài liệu cấu hình **theo site**, có version, do Site Engineer đề xuất, Control Supervisor duyệt, ký số, đẩy xuống edge. Lệnh ngoài SOE bị từ chối (không kẹp im lặng ở cloud; edge kẹp và báo `APPLIED_CLAMPED` cho các giới hạn động như CCL/DCL).

| Tham số SOE | Đơn vị | Ví dụ | Nguồn giá trị |
|---|---|---|---|
| `P_ess_dis_max`, `P_ess_ch_max` | kW | ≤ PCS rated × hệ số | Datasheet PCS + thiết kế |
| `SOC_min_eff`, `SOC_max_eff` | % | 10 / 95 | Hãng pin + chính sách bảo hành |
| `SOC_backup_reserve` | % | 30 (site có tải ưu tiên) | Chủ site |
| `export_limit_kW` | kW | 0 (zero export) | Hợp đồng/NĐ 58 (A) |
| `import_cap_kW` | kW | ≤ công suất đăng ký / MBA | A, C |
| `ramp_max` | kW/s | 10% P_rated/s | [UNKNOWN] grid code VN cho C&I; tham số |
| `delta_P_max_per_cmd` | kW | 50% P_rated | Chống bước nhảy lớn |
| `mode_change_min_interval` | s | 300 | Chống dao động/mòn contactor |
| `cycles_per_day_max` | chu kỳ tương đương | 1,5 | Bảo hành pin |
| `ev_site_cap_kW`, `ev_min_A` | kW, A | 6 A min | E |
| `allowed_command_types` | danh sách | Theo `capability_profile` | E §3.19 |
| `T_stale_bms` | s | 5 | C limit chain |
| `T_cloud_plan_expiry_fallback` | h | 48 | B PR-B02 |

#### 3.7.3 Khóa liên động (interlocks) phần mềm tại edge

Một lệnh bị chặn (`REJECTED_INTERLOCK:<code>`) nếu bất kỳ điều kiện nào sau đây đúng [PROPOSAL]:

| Mã | Điều kiện | Lý do |
|---|---|---|
| IL-01 | Công tắc **LOCAL/REMOTE** của site (DI phần cứng hoặc thiết bị) ở LOCAL hoặc MAINTENANCE | Người tại chỗ có quyền cao nhất |
| IL-02 | E-stop đang tác động / mạch an toàn chưa reset (đọc DI) | E-stop cứng |
| IL-03 | BMS báo lỗi/alarm cấp bảo vệ, hoặc dữ liệu BMS cũ > `T_stale_bms` | C limit chain |
| IL-04 | Công tơ POC mất dữ liệu (cần cho zero-export/import cap) | G fallback |
| IL-05 | Thiết bị đích `driver_verification_status ≠ VERIFIED` hoặc đang `BAD_COMM` | E |
| IL-06 | Đồng hồ edge không `SYNCED` (không kiểm được hạn lệnh) | Chống replay/lệnh cũ |
| IL-07 | Đang có lệnh `GRID_OPERATOR` hiệu lực xung đột | Ưu tiên điều độ |
| IL-08 | Hệ PCCC/phát hiện khí/nhiệt độ phòng pin báo động (nếu có tín hiệu) | Không xả/sạc khi có nguy cơ cháy |
| IL-09 | Cửa tủ/che chắn mở, chế độ bảo trì (nếu có DI) | An toàn người |
| IL-10 | Site đang trong `COMMISSIONING` | Chưa nghiệm thu |

#### 3.7.4 Phân hạng nguy hiểm và phê duyệt hai người

| Hạng | Ví dụ lệnh | Yêu cầu |
|---|---|---|
| C0 Thông tin | Đọc, refresh, `dry_run` | Viewer |
| C1 Thường | Áp lịch trong SOE, đổi mode trong danh sách cho phép, setpoint EV trong cap, TTL ≤ 1 h | Operator + MFA phiên |
| C2 Nhạy cảm | Setpoint vượt 80% giới hạn SOE; giảm `SOC_backup_reserve`; tắt tối ưu; lệnh tới > 5 site cùng lúc; ngoài giờ hành chính | Operator + **step-up MFA**; lý do bắt buộc |
| C3 Nguy hiểm | `DEVICE_ON_OFF`; thay đổi SOE; bật/tắt `control_enabled`; `SET_REVERSE_FEED_BLOCK` thủ công; xả/sạc cưỡng bức bỏ qua tối ưu > 30 phút; lệnh tới > 10% MW đội; reset lỗi (nếu hãng cho phép); cập nhật firmware edge | **Hai người** (người yêu cầu + approver khác người, khác vai trò, cả hai step-up MFA), cửa sổ duyệt ≤ 15 phút, lệnh hết hạn nếu không duyệt; thông báo chủ site |
| C4 Cấm từ cloud | Đổi grid code, ngưỡng bảo vệ, cấu hình BMS, bỏ qua interlock, điều khiển E-stop | Không tồn tại API. Chỉ làm tại chỗ bằng công cụ hãng |

#### 3.7.5 TTL, idempotency, ack/timeout

Dựa trên envelope và state machine của Agent E (§3.19, `E-device-integration.md`); bổ sung giá trị số [PROPOSAL]:

| Loại lệnh | `expires_at` tối đa | `max_latency_ms` (đến edge muộn hơn → `REJECTED_STALE`) | Timeout readback | Sau hạn |
|---|---|---|---|---|
| Setpoint thủ công (`SET_ESS_P`, `SET_EXPORT_LIMIT` tạm) | 1 h (mặc định 15 phút) | 10 000 | 10 s (tùy thiết bị, theo `capability_profile`) | `REVERT_DEFAULT` |
| Đổi mode | 24 h | 30 000 | 30 s | `REVERT_DEFAULT` |
| `APPLY_SCHEDULE` | 7 ngày (horizon ≥ 48 h) | 300 000 | — (từng khung) | Chiến lược mặc định site |
| Lệnh DR/VPP | Theo sự kiện | 5 000 | 10 s | Theo quy tắc chương trình |
| `GRID_OPERATOR` (IEC 104) | Theo điều độ | — (cục bộ) | Theo QĐ 1570 [UNKNOWN] | Theo điều độ |
| Lệnh C3 sau duyệt | ≤ 30 phút từ lúc duyệt | 10 000 | 30 s | Hủy |

- **Idempotency**: `command_id` (UUID v7) là khóa; API cloud nhận thêm header `Idempotency-Key` cho POST; edge lưu bảng đã thấy tới `expires_at + 24 h` (E). Gửi lại sau mất kết nối **không** được tạo lệnh mới.
- **Không tự gửi lại sau `expires_at`** (E: `UNDELIVERED`). Retry chỉ trong hạn, backoff mũ, tối đa N lần.
- **Readback bắt buộc** trước khi hiển thị "đã áp dụng" (E X-E-05).
- **Đối soát sau reconnect**: edge báo danh sách lệnh đang hiệu lực + config version; cloud so và cảnh báo lệch.

#### 3.7.6 Rate limiting và giới hạn bán kính tác động (blast radius)

| Cấp | Giới hạn đề xuất [PROPOSAL] | Cơ chế |
|---|---|---|
| Thiết bị | ≤ 1 setpoint mới/2 s từ edge (vòng nhanh là việc của edge); ghi NVM ≤ theo khuyến cáo hãng (E: mòn NVM) | Edge driver |
| Site (cloud → edge) | ≤ 6 lệnh thủ công/phút; ≤ 12 đổi mode/giờ; `mode_change_min_interval` | Command API + edge |
| Người dùng | ≤ 30 lệnh/10 phút; > 5 site/lệnh → C2; > 10% MW đội → C3 | PDP |
| API client (máy) | Theo scope; mặc định 0 lệnh (chỉ đọc) | OAuth scope |
| **Tenant / đội** | Tổng |ΔP| được lệnh trong 5 phút ≤ **X% công suất BESS của tenant** (đề xuất 20%) hoặc ≤ Y MW tuyệt đối; vượt → hàng đợi + duyệt C3 | **Fleet Dispatch Governor** |
| **Toàn nền tảng** | Tổng |ΔP| mọi tenant trong 5 phút ≤ Z MW (đặt theo quy mô; ví dụ 5% tổng công suất quản lý); lệnh đồng loạt được **trải ngẫu nhiên** (jitter 0–300 s) trừ lệnh điều độ | Governor toàn cục + kill switch |
| Optimizer | Lịch mới không đổi quá 30% tổng năng lượng xả của đội trong 1 khung so với lịch trước nếu không có sự kiện giải thích | Validator (G: `VALIDATED`) |

**Kill switch điều khiển** (không phải E-stop): Org Admin hoặc vận hành nền tảng có thể **tắt toàn bộ kênh lệnh từ xa** cho một site/tenant/toàn nền tảng; edge nhận lệnh ký "REMOTE_CONTROL_SUSPENDED" và chạy chiến lược mặc định cục bộ. Thao tác *tắt* là C1 (an toàn hóa nhanh), thao tác *bật lại* là C3.

#### 3.7.7 Ưu tiên điều khiển cục bộ, E-stop

- **Thứ tự ưu tiên tại edge** (khớp G L0–L7 và E `source`): bảo vệ native (ngoài phần mềm) > E-stop cứng > công tắc LOCAL > `GRID_OPERATOR` > watchdog/fallback edge > lệnh thủ công từ xa (C1–C3) > DR > optimizer > mặc định.
- **Công tắc LOCAL/REMOTE**: khuyến nghị **phần cứng** (khóa chìa hoặc công tắc trên tủ, nối DI của edge). Ở LOCAL: edge từ chối mọi lệnh từ cloud, vẫn gửi telemetry; UI cloud hiển thị "Đang điều khiển tại chỗ".
- **E-stop**: thuộc mạch an toàn cứng của BESS/PCS (thường cắt contactor/MCCB), **không** đi qua edge hay cloud. EMS chỉ **đọc** trạng thái E-stop. Không có nút "E-stop từ xa" trong UI. Nếu khách muốn "dừng từ xa" → đó là lệnh `DEVICE_ON_OFF`/`SET_ESS_P=0` hạng C3/C1, đặt tên khác ("Dừng vận hành từ xa"), không được gọi là E-stop.
- **Reset sau E-stop/lỗi**: chỉ tại chỗ (C4) hoặc theo quy trình hãng cho phép reset từ xa có hai người duyệt (C3).

### 3.8 Fail-safe khi mất liên lạc

Hai đoạn liên lạc khác nhau, hai cơ chế khác nhau:

**(a) Mất cloud ↔ edge** (Internet, broker, cloud sập)
- Edge tiếp tục vòng điều khiển cục bộ (zero-export, import cap, limit chain) — không phụ thuộc cloud.
- Lệnh thủ công từ xa đang hiệu lực: chạy tới `expires_at`, rồi `on_expiry`.
- Lịch: dùng lịch đã nhận (≥48 h). Hết lịch → chiến lược mặc định của site (ví dụ self-consumption + export limit + giữ `SOC_backup_reserve`).
- Store-and-forward telemetry ≥ 7 ngày (E PR-E-05; F đề xuất buffer 30 ngày).
- Phát hiện: heartbeat edge mỗi 30 s (MQTT keepalive 30–60 s + message `state` có `seq`); cloud đánh dấu `OFFLINE` sau 3 heartbeat lỡ (~90 s); cảnh báo sau 5 phút (tránh nhiễu).

**(b) Mất edge ↔ thiết bị** (edge treo, cáp RS485 đứt, edge mất nguồn)
- Thiết bị **phải** tự hoàn nguyên. Mẫu watchdog/heartbeat phổ biến (kiến thức nền, cần xác minh theo từng hãng):

| Mẫu | Cách hoạt động | Ví dụ (K — chưa kiểm chứng) | Yêu cầu với driver |
|---|---|---|---|
| Reversion timeout gắn với setpoint | Mỗi setpoint kèm thời gian hiệu lực; hết thời gian thiết bị về giá trị mặc định | SunSpec 123 `WMaxLim_RvrtTms`, `OutPFSet_RvrtTms`; SunSpec 704 có trường revert time tương ứng | Ghi RvrtTms = 2–5 × chu kỳ ghi của edge |
| Heartbeat register | Master ghi bộ đếm/giá trị định kỳ vào thanh ghi; thiết bị đếm thời gian từ lần ghi cuối | Nhiều PCS BESS Trung Quốc có "EMS heartbeat"/"communication timeout" [UNKNOWN theo hãng] | Ghi mỗi ≤ T/3 |
| Fallback cấu hình sẵn khi mất tín hiệu điều khiển | Thiết bị có tham số "timeout" + "giá trị fallback" (giữ / giá trị cố định) | SMA (tham số fallback cho giới hạn P từ bên ngoài) [K]; Victron ESS Mode 2/3 [UNKNOWN — Q-G02, Q-E-06] | Đặt fallback = an toàn (P_ess=0 hoặc tự dùng, PV về export limit) |
| Watchdog của API controller | Giá trị ghi qua API bị reset sau timeout nếu không được làm mới | OpenEMS Controller Api `apiTimeout` [K] | Dùng khi edge ghi vào một EMS khác (OpenEMS/logger) |
| Charger: profile mặc định | TxDefaultProfile/ChargePointMaxProfile an toàn khi mất kết nối | OCPP (E F-21: TxDefaultProfile "to keep charging controlled if connectivity is lost") | Luôn cài profile mặc định an toàn |
| Logger hãng tự giữ vòng | Logger/EMS hãng (SmartLogger, EMMA) chạy zero-export nội bộ | E X-E-04, Q-E-04 [UNKNOWN watchdog lệnh remote] | Ưu tiên ghi vào logger |

- **[PROPOSAL] Quy tắc nghiệm thu**: thiết bị không có watchdog/reversion **không được** nhận setpoint P từ xa ở chế độ "cưỡng bức xả/sạc"; chỉ được đổi mode giữa các chế độ native an toàn (ví dụ "self-consumption" ↔ "TOU" của hãng), hoặc phải có rơ-le/giới hạn native được installer cấu hình và ghi biên bản (E: `requires_native_fallback=true`).
- **Watchdog phần cứng của edge**: timer phần cứng reset edge nếu vòng điều khiển treo > 10 s; sau reboot edge khởi động ở chế độ **SAFE_START** (không ghi gì cho tới khi đọc đủ trạng thái và đồng hồ hợp lệ).
- **Kiểm thử bắt buộc** (T-…): rút cáp WAN, rút cáp RS485, tắt nguồn edge, làm lệch đồng hồ, chặn broker, gửi lệnh hết hạn, gửi lệnh replay — mỗi ca có tiêu chí "thiết bị về trạng thái X trong ≤ T s".

### 3.9 Bảng thời gian hoàn nguyên đề xuất

| Lớp | Tham số | Giá trị đề xuất | Ghi chú |
|---|---|---|---|
| Thiết bị ← edge | Reversion/heartbeat timeout | 10–60 s (theo khả năng thiết bị) | Phải > 3 chu kỳ ghi |
| Edge ← cloud (setpoint thủ công) | `expires_at` | 15 phút mặc định, tối đa 1 h | |
| Edge ← cloud (lịch) | Horizon | ≥ 48 h | B, E |
| Cloud phát hiện edge offline | 3 heartbeat lỡ | ~90 s | |
| Cảnh báo người | Offline | 5 phút | Khử nhiễu |
| Edge khởi động lại | SAFE_START | tới khi đủ dữ liệu, ≥ 2 chu kỳ đọc | |

### 3.10 Mô hình mối đe dọa (STRIDE) và ca lạm dụng

#### 3.10.1 STRIDE theo thành phần

| Thành phần | S (giả mạo) | T (sửa đổi) | R (chối bỏ) | I (lộ thông tin) | D (từ chối dịch vụ) | E (leo thang quyền) | Biện pháp chính |
|---|---|---|---|---|---|---|---|
| Web/mobile | Phishing tài khoản Operator | CSRF/XSS sửa lệnh | "Không phải tôi ra lệnh" | Xem site tenant khác (IDOR) | Brute force | Viewer gọi API lệnh | MFA/WebAuthn, CSP, SameSite, ABAC, audit có `auth_time` |
| Command API | Token bị đánh cắp | Sửa params giữa đường | — | — | Flood lệnh | Bỏ qua phê duyệt | mTLS nội bộ, chữ ký envelope, idempotency, rate limit, approval state machine phía server |
| Command Signer / KMS | Khóa ký bị lộ → lệnh giả hợp lệ | — | — | — | KMS sập → không ra lệnh (fail-safe) | — | HSM/KMS, khóa không xuất, xoay khóa, ký chỉ sau PDP + approval, giới hạn tốc độ ký |
| Broker MQTT | Edge giả | Chèn/sửa message | — | Nghe lén topic | DoS kết nối | Client edge subscribe `#` | mTLS, ACL theo edge, lệnh ký tầng ứng dụng, quota |
| Edge | Cloud giả (DNS spoof) | Firmware độc | Ack giả | Lộ credential OT | Treo vòng điều khiển | Root qua UI cục bộ | Pin CA, secure boot, OTA ký, ack ký, watchdog HW, không mật khẩu mặc định |
| OT LAN | Master Modbus thứ hai | Ghi thanh ghi trực tiếp | — | Sniff | Bão gói | — | Edge là master duy nhất, cô lập mạng, giám sát thiết bị lạ |
| Connector cloud hãng | Credential hãng lộ | — | — | Lộ dữ liệu khách | Bị hãng throttle/khóa | Token đọc dùng để ghi | Vault, scope chỉ đọc, rate limiter (E PR-E-11) |
| DB/TSDB | — | Sửa audit | Xóa dấu vết | Cross-tenant | — | Owner bypass RLS | RLS FORCE, role tách, audit hash chain + WORM |
| CI/CD, supply chain | Package độc | Build bị chèn | — | Lộ secrets CI | — | — | SBOM, ký artifact, pin dependency, review 2 người cho control plane |
| Optimizer | — | Dữ liệu dự báo bị đầu độc → lịch xấu | — | — | — | — | Validator lịch (G), giới hạn thay đổi, SOE |

#### 3.10.2 Ca lạm dụng (abuse cases)

| ID | Kịch bản | Tác động | Phòng ngừa | Phát hiện | Phản ứng |
|---|---|---|---|---|---|
| AC-01 | **Tài khoản cloud có quyền rộng bị chiếm, ra lệnh xả 100% toàn bộ BESS cùng lúc** | Vượt export limit hàng loạt, dao động lưới cục bộ, hao pin, mất dự phòng | Fleet Dispatch Governor (§3.7.6); C3 cho > 10% MW; SOE kẹp tại edge; export limit tại edge/inverter vẫn giữ; jitter | Bất thường số lệnh/ΔP; lệnh từ IP/thiết bị mới | Kill switch tenant/nền tảng; thu hồi token; edge `REVERT_DEFAULT` |
| AC-02 | Insider (nhân viên vận hành nền tảng) sửa SOE để nới giới hạn | Hỏng pin/vi phạm hợp đồng | SoD: sửa SOE ≠ duyệt SOE; SOE ký; edge so SOE với bản ký; thông báo chủ site mọi thay đổi SOE | Audit, diff SOE | Rollback SOE |
| AC-03 | **Replay** lệnh cũ hợp lệ (ví dụ "xả 500 kW") | Tác động lặp | `expires_at`, `seq` đơn điệu, `command_id` đã thấy, đồng hồ đồng bộ | Edge log `REJECTED_STALE/REPLAY` | Cảnh báo bảo mật |
| AC-04 | Supply chain: thư viện/firmware edge bị chèn mã | Toàn đội bị chiếm | SBOM, ký build, review, canary rollout 1% → 10% → 100% với thời gian chờ, anti-rollback | Hành vi edge khác chuẩn (egress lạ) | Dừng rollout, rollback A/B |
| AC-05 | Credential cloud hãng (ví dụ OAuth Connect có quyền điều khiển) bị lộ từ DB | Kẻ tấn công điều khiển trực tiếp qua cloud hãng, **bỏ qua edge của ta** | Mặc định chỉ đọc; vault + khóa theo tenant; không lưu quyền ghi cloud hãng nếu không cần | — | Thu hồi tại hãng (owner revoke) |
| AC-06 | Kênh cloud hãng song song (dongle → cloud hãng) đổi mode pin trong khi edge điều khiển | Xung đột điều khiển, "ghi không tác dụng" | Chính sách: khi edge `REMOTE`, khuyến nghị chặn/giới hạn kênh hãng hoặc đặt hãng ở chế độ "điều khiển ngoài"; phát hiện mode thay đổi không do ta | Readback lệch, mode đổi ngoài lệnh | Cảnh báo `EXTERNAL_CONTROL_DETECTED` |
| AC-07 | Tranh chấp thương mại: nhà cung cấp (kể cả ta) vô hiệu hóa hệ thống của khách từ xa (mẫu sự cố 11/2024, finding 6) | Mất vận hành | Cam kết hợp đồng: không có "kill" thương mại; khi hết hợp đồng edge chạy chế độ mặc định cục bộ vĩnh viễn; xuất dữ liệu | — | — |
| AC-08 | Giả mạo telemetry (công tơ POC giả số liệu) để edge xả/sạc sai | Vi phạm export/import | Kiểm tra chéo cân bằng năng lượng (POC ≈ PV + BESS − tải), giới hạn tốc độ thay đổi, công tơ trên OT LAN cô lập | Mất cân bằng > ngưỡng | Chuyển chế độ an toàn |
| AC-09 | DoS broker/cloud trong giờ cao điểm để làm hỏng peak shaving | Mất lợi ích kinh tế | Lịch offline 48 h tại edge | — | Không cần can thiệp |
| AC-10 | Installer cũ còn quyền sau khi hết hợp đồng | Truy cập trái phép | Grant có hạn, nhắc xem lại quyền định kỳ 90 ngày | Đăng nhập từ tài khoản ngủ đông | Thu hồi |

### 3.11 Sự cố thực tế (trạng thái kiểm chứng)

| Sự cố | Trạng thái bằng chứng | Bài học cho thiết kế |
|---|---|---|
| Ukraine 12/2015: tấn công 3 công ty phân phối, chiếm HMI từ xa qua kênh truy cập từ xa, cắt điện khoảng 225.000 khách, ghi đè firmware bộ chuyển đổi serial-Ethernet, xóa máy (KillDisk) | **[INFERENCE] kiến thức nền, chưa kiểm chứng URL trong lượt này** | Truy cập từ xa thường trực + thông tin đăng nhập VPN là cửa vào; firmware thiết bị phụ trợ không ký có thể bị "brick" → OTA ký, không VPN thường trực, MFA |
| Ukraine 12/2016: Industroyer/CrashOverride tại trạm biến áp gần Kyiv, có module IEC 60870-5-104/101, IEC 61850, OPC DA | **[INFERENCE] kiến thức nền, chưa kiểm chứng URL** | Giao thức SCADA không xác thực → kênh IEC 104 tới điều độ phải là conduit cô lập; edge chỉ nhận lệnh 104 từ IP/kênh đã định |
| 11/2024: inverter ở Mỹ/Anh/Pakistan bị vô hiệu hóa từ xa do tranh chấp thương mại | **[FACT]** Defense News (finding 6); gán hãng: **[UNKNOWN]** | Một tài khoản cloud có quyền ghi = kill switch toàn đội → blast radius, hợp đồng |
| 5/2025: "rogue communication devices" trong inverter/pin Trung Quốc (Reuters) | **[FACT]** bài báo tồn tại; nội dung **chưa xác nhận**, DOE 1/2026 không tìm thấy bằng chứng độc hại (finding 5) | Không quy kết; nhưng giám sát egress OT LAN và chính sách kênh cloud hãng |
| Lithuania: cấm truy cập từ xa của công ty Trung Quốc > 100 kW | **[FACT]** (finding 4) | Thiết kế để khách có thể **tắt hoàn toàn kênh cloud hãng** và vẫn vận hành qua edge |
| Forescout SUN:DOWN 3/2025; CCC/Hoymiles 2026 | **[FACT]** (finding 7) | Cloud API + cập nhật là bề mặt chính; chương trình công bố lỗ hổng (VDP) + vá |
| Huawei 9/2025: đổi chính sách API (owner phải cấp quyền) làm hỏng tích hợp bên thứ ba | **[FACT]** https://community.home-assistant.io/t/fusion-solar-doesnt-work-anymore/927417 (nghiên cứu trước) | Phụ thuộc cloud hãng là rủi ro khả dụng → connector đọc có trạng thái suy giảm, không dùng cho điều khiển nhanh |
| Deye Cloud "data migration announcement" | **[FACT]** trang tồn tại (403, nội dung **chưa đọc**) https://deye.com/vi/deye-cloud-data-migration-announcement/ | Không suy diễn sự cố; theo dõi |
| "Sự cố Solarman/Deye cloud" (đề bài yêu cầu kiểm chứng) | **[UNKNOWN]** — không có bằng chứng trong nguồn hiện có; không ghi là sự cố | Cần lượt tìm kiếm (Q-I-09) |

### 3.12 Nhật ký kiểm toán (audit trail)

- **Phạm vi ghi**: đăng nhập/đăng xuất/MFA, thay đổi quyền, grant installer, thay đổi SOE/config/driver map, **mọi chuyển trạng thái lệnh** (E state machine), phê duyệt/từ chối, kill switch, xuất dữ liệu (F X-F08), truy cập break-glass, phiên tunnel hỗ trợ, OTA, thay đổi credential tích hợp, lệnh `GRID_OPERATOR` (envelope nội bộ E rule 4).
- **Lược đồ sự kiện**: `event_id` (UUID v7), `ts` (UTC, nguồn đồng hồ), `tenant_id`, `actor` (user/service/edge, `auth_time`, `amr`, IP, user-agent), `action`, `resource`, `before`/`after` (hoặc hash nếu lớn), `reason`, `correlation_id`, `command_id`, `result`, `prev_hash`, `hash`.
- **Bất biến**:
  1. Bảng `audit_event` append-only: role ứng dụng chỉ có `INSERT`; `REVOKE UPDATE, DELETE, TRUNCATE`; trigger chặn sửa; partition theo tháng.
  2. **Hash chain theo tenant**: `hash_i = SHA-256(hash_{i-1} ‖ canonical_json(event_i))`; ghi tuần tự theo tenant (advisory lock hoặc sequence) để chuỗi không phân nhánh.
  3. **Neo định kỳ** (mỗi giờ): Merkle root các sự kiện trong giờ được ký bằng khóa KMS và ghi vào **object storage WORM** (object lock chế độ compliance) ở vùng/tài khoản khác; tùy chọn gửi root cho khách hàng (email/API) để họ tự lưu.
  4. Công cụ kiểm tra chuỗi chạy hằng ngày; đứt chuỗi → sự cố bảo mật P1.
  5. Edge cũng giữ audit cục bộ (lệnh nhận, interlock, LOCAL/REMOTE, E-stop) có hash chain, đồng bộ lên cloud.
- **Lưu trữ**: tối thiểu 12 tháng trực tuyến (khớp kiến thức nền về NĐ 53, cần kiểm chứng), đề xuất 5 năm lưu trữ lạnh cho audit lệnh (phục vụ tranh chấp bảo hành pin/hợp đồng điện) — [PROPOSAL], tham số theo hợp đồng.
- **Truy cập**: chủ tenant xem audit của tenant mình; nhân viên nền tảng xem cần lý do + được audit.

### 3.13 Quản lý secrets và khóa

| Secret | Nơi lưu | Xoay vòng | Ghi chú |
|---|---|---|---|
| Khóa CA gốc thiết bị | Offline (HSM/thẻ, két) | 10–20 năm | Chỉ dùng ký CA trung gian |
| Khóa CA trung gian, khóa ký lệnh, khóa ký OTA, khóa neo audit | KMS/HSM (không xuất) | 1–2 năm; ký lệnh: hỗ trợ 2 `kid` song song | Tách theo mục đích |
| Credential cloud hãng (OAuth token, appSecret) | Vault (HashiCorp Vault/OpenBao hoặc KMS-backed secret store), mã hóa khóa theo tenant | Theo hãng; refresh tự động | Chỉ connector của tenant đó đọc được |
| Mật khẩu DB, broker, dịch vụ | Vault dynamic secrets / workload identity | ≤ 30 ngày hoặc động | Không trong env file, không trong repo |
| Secrets tại edge | Secure element/TPM-sealed store | Theo cert | Credential OT (ví dụ OCPP basic auth) sinh ngẫu nhiên theo site |
- Quét secrets trong CI (pre-commit + server-side), cấm log token, mask trong audit.

### 3.14 Observability và SLO

**Tín hiệu**
- Metrics (Prometheus/OpenTelemetry): ingest lag, số điểm/giây, tỷ lệ `STALE`, edge online %, độ trễ lệnh theo trạng thái (CREATED→RECEIVED→APPLIED), tỷ lệ `FAILED_*`/`APPLIED_CLAMPED`, tỷ lệ `REJECTED_INTERLOCK`, số lệnh/phút theo tenant, ΔP đội/5 phút, tỷ lệ fallback đang chạy, cert sắp hết hạn, độ lệch đồng hồ edge.
- Logs: JSON có `trace_id`, `tenant_id`, `command_id`; không ghi DLCN/secret.
- Traces: OpenTelemetry xuyên API → PDP → Signer → broker; edge gắn `traceparent` vào ack.
- **Security monitoring**: login bất thường, lệnh ngoài giờ, lệnh từ client mới, đứt hash chain, edge egress lạ, thiết bị lạ trên OT LAN (edge passive discovery), nhiều `REJECTED_STALE/REPLAY`.

**SLO đề xuất [PROPOSAL]** (cửa sổ 30 ngày):

| Dịch vụ | SLI | SLO | Lý do |
|---|---|---|---|
| Điều khiển cục bộ tại edge | Thời gian vòng điều khiển chạy đúng hạn (không treo) | ≥ 99,95% | Lớp an toàn chính; watchdog HW |
| Bảo toàn dữ liệu (edge→cloud) | Tỷ lệ mẫu tới cloud trong ≤ 24 h (kể cả backfill) | ≥ 99,9% | Store-and-forward |
| Ingest tươi | p95 độ trễ mẫu tới khi truy vấn được | ≤ 60 s | F: cloud nhận 5–60 s |
| Giao lệnh cloud→edge | p95 CREATED→RECEIVED khi edge online | ≤ 5 s; p99 ≤ 15 s | |
| Lệnh có readback | p95 RECEIVED→APPLIED | ≤ 15 s (phụ thuộc thiết bị) | |
| Khả dụng Command API | Request thành công / tổng | ≥ 99,9% giờ làm việc; ≥ 99,5% tổng | Edge có fallback nên không cần 99,99% |
| Khả dụng UI/API giám sát | | ≥ 99,5% | |
| Cảnh báo | p95 sự kiện → thông báo | ≤ 2 phút | |
| Báo cáo | Báo cáo ngày sẵn sàng | 99% trước 06:00 giờ site | |

Error budget: hết budget của Command API → đóng băng release control plane.

### 3.15 Backup, DR, khả dụng

| Dữ liệu | RPO | RTO | Cơ chế |
|---|---|---|---|
| Danh mục/cấu hình/SOE/quyền (PostgreSQL) | ≤ 5 phút | ≤ 4 h | WAL archiving + PITR (pgBackRest/WAL-G), replica đồng bộ trong vùng |
| Bảng lệnh + audit | ≤ 1 phút (mục tiêu ~0) | ≤ 4 h | Replica đồng bộ; neo WORM mỗi giờ; edge giữ bản sao lệnh/audit cục bộ |
| Timeseries nóng (TimescaleDB) | ≤ 15 phút | ≤ 8 h (đọc dữ liệu mới trước) | Backup + **backfill từ edge** (buffer 7–30 ngày) giúp RPO thực tế gần 0 cho dữ liệu trong buffer |
| Timeseries lạnh (Parquet object storage) | ≤ 24 h | ≤ 72 h | Sao chép liên vùng |
| Secrets/KMS | Theo nhà cung cấp | ≤ 4 h | Khóa ký có bản dự phòng HSM; quy trình khôi phục CA |

- **Hai DC tại Việt Nam** (vùng chính + vùng DR khác tỉnh) để vừa lưu trú dữ liệu vừa DR [PROPOSAL; nhà cung cấp cụ thể chưa đánh giá].
- **Diễn tập**: khôi phục PITR hằng quý; failover DR 6 tháng/lần; "game day" mất cloud 4 h để xác nhận edge fallback.
- **Khi cloud khôi phục**: edge đối soát (§3.7.5), không tự thi hành lại lệnh đã hết hạn; optimizer phát lịch mới.

### 3.16 Quy trình phát triển và vận hành an toàn (tóm tắt theo tinh thần IEC 62443-4-1, K)

- Threat model cập nhật mỗi release lớn của control plane; review bảo mật bắt buộc cho thay đổi ở Command API, PDP, Signer, edge arbiter, driver ghi.
- SAST, dependency scan, container scan, SBOM (CycloneDX/SPDX) cho cloud và edge; DAST cho API.
- Pen-test bên thứ ba trước GA và hằng năm; chương trình công bố lỗ hổng (security.txt, email PGP), SLA vá: critical ≤ 14 ngày (cloud ≤ 72 h), high ≤ 30 ngày.
- Hỗ trợ bảo mật cho edge: cam kết thời hạn cập nhật bảo mật (ví dụ ≥ 5 năm — tương tự Huawei PSTI cam kết tới 31/12/2029, nghiên cứu trước).
- Tài liệu hardening cho installer (IEC 62443-2-4 tinh thần): checklist commissioning bảo mật (đổi mật khẩu, VLAN, LOCAL/REMOTE, kiểm watchdog, kiểm SOE).

---

## 4. Hệ quả thiết kế cho sản phẩm (PROPOSAL)

| ID | Đề xuất | Module | Ưu tiên | Cơ sở |
|---|---|---|---|---|
| NFR-SEC-001 | Cloud và edge **không bao giờ** ghi thông số bảo vệ (grid code, BMS, rơ-le); không có API cho nhóm C4 | M-SEC, M-BESS | P0 | Finding 1, C X-C06 |
| NFR-SEC-002 | Tách **monitoring plane** và **control plane**: service identity, credential, topic, quyền DB, namespace, quy trình release riêng; control mặc định TẮT theo site | M-SEC, M-INT | P0 | Finding 15, §3.4.3 |
| NFR-SEC-003 | Edge kết nối **outbound-only**, MQTT 5 qua TLS 1.3/1.2 AEAD, **mTLS** với cert X.509 riêng từng edge (khóa trong TPM/SE), hạn 90 ngày, tự gia hạn | M-INT, M-SEC | P0 | Finding 2, §3.5 |
| NFR-SEC-004 | Lệnh ký ở tầng ứng dụng (JWS) bởi Command Signer dùng KMS/HSM; edge kiểm chữ ký, `kid`, đích, hạn, `command_id`, `seq` đơn điệu; ack ký bằng khóa edge | M-SEC | P0 (ký), P0 (seq/expiry) | §3.5, AC-03 |
| NFR-SEC-005 | OIDC + PKCE; MFA bắt buộc cho mọi vai trò có quyền ghi/admin, ưu tiên WebAuthn; step-up MFA ≤ 5 phút cho C2/C3 | M-ORG, M-SEC | P0 | §3.3 |
| NFR-SEC-006 | RBAC theo cây Org→Site→Device + **ABAC/PDP** cho mọi lệnh; SoD (Org Admin không mặc định có quyền lệnh) | M-ORG, M-SEC | P0 | §3.4.1 |
| NFR-SEC-007 | Cô lập tenant: PostgreSQL RLS với `FORCE ROW LEVEL SECURITY`, role app không owner/không BYPASSRLS, `SET LOCAL` mỗi transaction, test cross-tenant tự động trong CI; SKU silo/on-prem cho khách lớn | M-ORG, M-SEC | P0 (RLS), P2 (silo) | §3.4.2 |
| NFR-SEC-008 | Phân hạng lệnh C0–C4; **hai người duyệt** cho C3; cửa sổ duyệt ≤ 15 phút; lý do bắt buộc từ C2 | M-SEC, M-BESS | P0 | §3.7.4, G X-G06 |
| NFR-SEC-009 | **SOE theo site** có version, ký số, đề xuất/duyệt bởi hai vai trò khác nhau; edge từ chối lệnh ngoài SOE | M-BESS, M-SEC | P0 | §3.7.2 |
| NFR-SEC-010 | Interlock IL-01…IL-10 tại edge; trả `REJECTED_INTERLOCK:<code>` | M-BESS, M-INT | P0 | §3.7.3 |
| NFR-SEC-011 | Mọi lệnh có `expires_at` theo bảng §3.7.5; edge từ chối lệnh không hạn hoặc đến muộn; không gửi lại sau hạn | M-INT | P0 | E §3.19 |
| NFR-SEC-012 | **Fleet Dispatch Governor**: giới hạn tổng ΔP theo tenant (mặc định 20% MW BESS/5 phút) và toàn nền tảng; jitter; vượt → C3 | M-OPT, M-SEC | P0 | AC-01, finding 6 |
| NFR-SEC-013 | **Kill switch điều khiển từ xa** theo site/tenant/nền tảng: tắt = C1, bật lại = C3 | M-SEC | P0 | §3.7.6 |
| NFR-SEC-014 | Công tắc **LOCAL/REMOTE** phần cứng nối DI edge là yêu cầu lắp đặt cho site bật điều khiển; E-stop cứng chỉ được đọc; UI không có "E-stop từ xa" | M-BESS, M-INT | P0 | §3.7.7 |
| NFR-REL-001 | Fail-safe mất cloud: edge giữ vòng cục bộ, lịch ≥ 48 h, fallback mặc định, store-and-forward ≥ 7 ngày | M-INT, M-OPT | P0 | §3.8, B PR-B02 |
| NFR-REL-002 | Fail-safe mất edge↔thiết bị: driver phải cấu hình watchdog/reversion (10–60 s); thiết bị không có watchdog chỉ được đổi giữa các mode native, không nhận setpoint P cưỡng bức | M-INT | P0 | §3.8 |
| NFR-REL-003 | Watchdog phần cứng edge (≤ 10 s) + SAFE_START sau reboot | M-INT | P0 | §3.8 |
| NFR-REL-004 | SLO theo bảng §3.14; Command API ≥ 99,5%, giao lệnh p95 ≤ 5 s, edge control ≥ 99,95% | M-SEC | P1 | §3.14 |
| NFR-REL-005 | RPO/RTO theo bảng §3.15; PITR; hai DC tại VN; diễn tập quý/6 tháng; game day mất cloud | M-SEC | P1 | §3.15 |
| NFR-SEC-015 | Audit append-only + hash chain theo tenant + neo hằng giờ vào WORM; kiểm chuỗi hằng ngày; edge audit cục bộ | M-SEC | P0 | §3.12 |
| NFR-SEC-016 | Secrets trong Vault/KMS; khóa ký không xuất; credential cloud hãng mã hóa theo tenant; quét secrets CI | M-SEC | P0 | §3.13 |
| NFR-SEC-017 | Phân vùng OT/IT: edge 2 NIC, không định tuyến WAN↔OT, edge là Modbus master duy nhất, IEC 104 trên conduit riêng; chặn OT ra Internet trừ khi khách chọn giữ kênh hãng | M-INT | P0 | §3.6, E X-E-04 |
| NFR-SEC-018 | Connector cloud hãng **mặc định chỉ đọc**; quyền ghi qua cloud hãng là cờ riêng, chỉ cho lịch chậm, C2 trở lên | M-INT | P0 | Finding 10, E PR-E-11 |
| NFR-SEC-019 | Phát hiện điều khiển ngoài (`EXTERNAL_CONTROL_DETECTED`) khi mode/setpoint thiết bị đổi không do edge | M-ALM | P1 | AC-06 |
| NFR-SEC-020 | OTA edge ký số, A/B + rollback, anti-rollback, canary 1%→10%→100% | M-INT, M-SEC | P0 | AC-04 |
| NFR-SEC-021 | OCPP ≥ Security Profile 2 (TLS + Basic), mục tiêu Profile 3; TxDefaultProfile an toàn | M-EV | P1 | Finding 3, E PR-E-10 |
| NFR-SEC-022 | Truy cập hỗ trợ từ xa: reverse tunnel theo yêu cầu, chủ site cho phép, ≤ 2 h, ghi phiên; không VPN thường trực | M-SEC | P1 | §3.5, Ukraine 2015 (K) |
| NFR-SEC-023 | Grant installer/vendor có hạn, chủ tài sản cấp/thu hồi; xem lại quyền mỗi 90 ngày | M-ORG | P0 | Finding 10, AC-10 |
| NFR-DATA-0xx | Phân loại dữ liệu D0–D4; hosting tại VN mặc định; DPIA; quy trình thông báo vi phạm DLCN | M-SEC | P0 (hosting VN), P1 (DPIA) | §3.2, §3.4.4 |
| NFR-OBS-001 | OpenTelemetry metrics/logs/traces xuyên cloud→edge với `trace_id`, `command_id`; dashboard an ninh (§3.14) | M-SEC | P1 | §3.14 |
| NFR-SEC-024 | SDL theo tinh thần IEC 62443-4-1: threat model, SAST/SCA/SBOM, pen-test năm, VDP, SLA vá; cam kết cập nhật bảo mật edge ≥ 5 năm | M-SEC | P1 | §3.16 |
| NFR-SEC-025 | Lộ trình chứng nhận: ISO 27001 (vận hành cloud) → IEC 62443-4-2 SL2 cho edge → đánh giá 62443-3-3 cho kiến trúc tham chiếu. **Không tuyên bố** trước khi có chứng chỉ (số, phạm vi, hạn) | M-SEC | P2 | Finding 9, B PR-B13 |
| FR-SEC-001 | Màn hình "Phê duyệt lệnh" (hàng đợi C3, diff trước/sau, tác động MW, hết hạn) | M-SEC | P0 | §3.7.4 |
| FR-SEC-002 | Màn hình "Trạng thái điều khiển site": LOCAL/REMOTE, kill switch, SOE version, interlock đang tác động, fallback đang chạy | M-SEC, M-DASH | P0 | §3.7 |
| FR-SEC-003 | Xuất audit (CSV/JSON) kèm bằng chứng hash/Merkle để khách tự kiểm | M-SEC | P1 | §3.12 |
| ADR ứng viên | ADR: "Cloud gửi ý định có hạn, edge quyết định setpoint" ; ADR: "Lệnh ký tầng ứng dụng độc lập broker" ; ADR: "RLS shared-schema + silo option" ; ADR: "Fleet Dispatch Governor" | 06 | — | §3 |

**Giải thích thay đổi so với hướng trước (FusionSolar research)**: hướng cũ là giám sát/O&M **chỉ đọc**; mô hình quyền chỉ cần Company tree + Role + DataScope. Hướng EMS **giữ nguyên** mô hình đó cho monitoring plane, và **thêm** control plane với ABAC, phê duyệt, ký lệnh, SOE, governor. Không có mâu thuẫn; đây là phần mở rộng có chủ đích.

---

## 5. Evidence ledger

| # | Claim | Source URL | Source type & date | Excerpt/paraphrase | Confidence | Conflicting evidence | Design implication |
|---|---|---|---|---|---|---|---|
| I-01 | SmartLogger3000 kết nối outbound tới NMS bằng Encrypted Modbus TCP, cổng 27250, TLS 1.2+ khuyến nghị; Modbus TCP thường tắt mặc định | https://support.huawei.com/enterprise/en/doc/EDOC1100108365/4fbe151e/setting-parameters-for-connecting-to-the-management-system-v300r001c00 ; https://support.huawei.com/enterprise/en/doc/EDOC1100273864/2b6a3248/set | Manual hãng; đọc ở nghiên cứu FusionSolar trước | "TLS1.2 or a later version is recommended" | High | — | NFR-SEC-003 outbound + TLS |
| I-02 | Lithuania cấm truy cập từ xa của công ty TQ tới hệ > 100 kW; không cấm lắp đặt | https://www.lrt.lt/en/news-in-english/19/2411602/lithuania-passes-law-to-block-chinese-access-to-solar-and-wind-farm-systems ; https://pv-tech.org/lithuania-to-block-chinese-inverters-with-cybersecurity-legislation | Báo chí 11/2024 (nghiên cứu trước) | Luật 12/11/2024; hạn 1/5/2025 và 1/5/2026 | High | Defense News mô tả rộng hơn (loại trừ inverter TQ) | Khách phải tắt được kênh cloud hãng, vẫn vận hành qua edge |
| I-03 | Reuters: thiết bị liên lạc không tài liệu trong inverter/pin TQ, không nêu hãng; chưa kiểm chứng | https://www.pv-magazine.com/2025/05/14/hidden-devices-found-in-chinese-made-inverters-in-the-us-reports-reuters/ | Báo chí 5/2025 | pv magazine "cannot verify" | Med (về việc đưa tin); Low (về nội dung) | I-04 | Không quy kết; giám sát egress OT |
| I-04 | DOE 1/2026: ~30 inverter, 2 trường hợp lệch tài liệu, "non-malicious" | https://www.pv-magazine-india.com/2026/01/29/u-s-authorities-find-no-definitive-evidence-of-hidden-devices-in-chinese-solar-inverters | Báo chí 1/2026 | no definitive evidence | Med | I-03 | Như trên |
| I-05 | 11/2024 inverter bị vô hiệu hóa từ xa do tranh chấp thương mại; không nêu hãng | https://www.defensenews.com/global/europe/2025/05/29/chinese-hold-on-solar-power-tech-raises-fresh-sabotage-fears-in-europe/ | Báo chí 5/2025 | commercial dispute | Med | Gán Deye/Sol-Ark chưa kiểm chứng | Fleet governor, cam kết hợp đồng (AC-07) |
| I-06 | Forescout SUN:DOWN: 46 lỗ hổng Sungrow/Growatt/SMA; 80% high/critical | https://forescout.com/press-releases/forescout-vedere-labs-uncovers-severe-systemic-security-risks-in-global-solar-power-infrastructure | Press release 27/3/2025 | 46 new vulnerabilities | Med–High | — | Pen-test, VDP, connector cloud chỉ đọc |
| I-07 | CCC: Hoymiles cập nhật firmware/điều khiển từ xa không xác thực | https://cybernews.com/security/china-solar-inverters-hack/ | Báo chí 7/2026 | unauthenticated firmware updates | Med | — | OTA ký (NFR-SEC-020) |
| I-08 | RED cybersecurity từ 1/8/2025; CRA từ 12/2027 (theo chính phủ NL) | https://solarmagazine.nl/nieuws-zonne-energie/i41070/kabinet-verscherpt-toezicht-op-chinese-omvormers-zonnepanelen-verbod-kill-switch-bestaat-al | Báo chuyên ngành 7/2025 | RDI có thể phạt, cấm, thu hồi | Med | — | P2 nếu bán EU |
| I-09 | Huawei có chứng nhận RED 3.3(d)/EN 18031-1 cho inverter + dongle, hiệu lực 2025-08-21 → 2030-08-20 | https://cdn.contentspeed.ro/pimromstal.websales.ro/cs-content/cs-docs/products/35fv1635569certificateredforsun2000map0sun5000map0_78205_21_1784579986.pdf | Chứng chỉ (nghiên cứu trước) | EN 18031-1:2024 | High | — | Chứng nhận thiết bị ≠ chứng nhận EMS |
| I-10 | Huawei PSTI: cập nhật bảo mật tới 31/12/2029 | https://solar.huawei.com/en/service-support/tsc/warranty-terms-and-conditions | Tuyên bố hãng 2024 | "5 years (until 31/12/2029)" | High | — | Cam kết thời hạn hỗ trợ bảo mật edge |
| I-11 | Ampowr tự tuyên bố ISO 27001, NIS2, host EU | https://ampowr.com/nis2-compliance/ | Trang hãng (Agent B, qua kết quả tìm kiếm) | "ISO27001 certified and NIS2 compliant" | Med (tự tuyên bố) | Không thấy registry | Chỉ tuyên bố khi có chứng chỉ |
| I-12 | Schneider: kiến trúc chứng nhận bên thứ ba theo IEC 62443-3-3; sản phẩm 4-2/4-1 | https://www.productinfo.schneider-electric.com/esxp_digital_apps_iec/transverse/English/BM_ESXP_DG_Transverse_Section_IEC_0001148082.xml/$/ESXP_DG_SYSD_Cyber_ISA_IEC_0001157270 | Tài liệu thiết kế hãng (Agent B) | "certified by a third party according to IEC 62443-3-3" | Med | Phạm vi với EMA cloud chưa rõ | 62443-3-3 là chuẩn mà đối thủ dùng |
| I-13 | Chứng chỉ IEC 62443-4-1/4-2 của WinCC OA hiệu lực tới 2026-02-06 | https://www.winccoa.com/documentation/WinCCOA/3.20/en_US/iec_62443/topics/iec_62443_certification.html | Trang chứng chỉ (Agent B) | validity end 2026-02-06 | Med | Gia hạn chưa rõ | Theo dõi hạn chứng chỉ |
| I-14 | Siemens SICAM MGC tuyên bố IEC 62443, IPSec, crypto chip | https://www.siemens.com/en-us/products/microgrids/sicam-microgrid-control/ | Trang hãng (Agent B) | "IEC-62443 certification, IPSec encryption, and integrated crypto chip" | Med | — | Secure element ở edge là chuẩn ngành |
| I-15 | Sungrow đạt ISO/IEC 27019 từ BSI | https://dl.sungrowpower.com/en/sungrow-achieves-iso-iec-27019-and-multiple-cybersecurity-management-system-certifications-from-bsi | Press release hãng | ISO/IEC 27019 | Med | — | 27019 là điểm cộng lộ trình |
| I-16 | OCPP 1.6J Security WP: profile 1/2/3 | https://openchargealliance.org/?p=159286 | OCA (Agent E, qua kết quả tìm kiếm) | Profile 3 = TLS + client cert | Med–High | — | NFR-SEC-021 |
| I-17 | OCPP TxDefaultProfile giữ sạc có kiểm soát khi mất kết nối; Easee: TxDefault 0 A đè TxProfile | https://www.bender.de/docs/charge-controller/OCPP/ocpp-smart-charging/ ; https://developer.easee.com/docs/ocpp-smart-charging | Doc hãng (Agent E) | "a 0A default overrides a 20A TxProfile" | Med–High | Khác nhau theo hãng | Fail-safe EV theo hãng |
| I-18 | Inverter có UL 1741 SB vẫn lỗi giao diện SunSpec | https://sunspec.org/communication-interface-defects-revealed-inul-1741-sb-certified-inverters/ | SunSpec 12/2023 (Agent E) | very few vendors completed certification | Med–High | — | Chứng nhận đấu nối ≠ an toàn điều khiển; readback |
| I-19 | IEEE 1547-2018: giao diện DER ≥ 1 trong 2030.5/DNP3/SunSpec | https://sunspec.org/sunspec-1547-initiative/ | SunSpec (nghiên cứu trước) | default communication standard | High | — | 1547 là chuẩn đấu nối, không phải EMS |
| I-20 | Huawei: owner cấp "O&M Authorization"/quyền thông số/API; bên thứ ba qua OAuth, thu hồi được | https://digitalpower.huawei.com/en/eu-data-act ; https://e-solarshop.ro/wp-content/uploads/2025/07/fusionsolar-app-manual5925.pdf | Trang hãng + manual (nghiên cứu trước) | Revoke tại Authorization Management | High | Propagation ~30 phút (issue cộng đồng) | NFR-SEC-023 grant có hạn |
| I-21 | Huawei 9/2025 đổi chính sách API làm hỏng tích hợp bên thứ ba | https://community.home-assistant.io/t/fusion-solar-doesnt-work-anymore/927417 | Diễn đàn 9/2025 (nghiên cứu trước) | Owner phải cấp quyền | Med–High | — | Connector cloud hãng không dùng cho điều khiển nhanh |
| I-22 | OpenEMS PR #3973: kẹp `SellToGridLimit` vì giá trị âm ghi vào thanh ghi unsigned | https://github.com/OpenEMS/openems/pull/3973 ; https://github.com/OpenEMS/openems/issues/3972 | GitHub (Agent C, qua kết quả tìm kiếm) | clamp to 0 | Med | — | Kiểm tra kiểu/kẹp ở lớp ghi driver (validation tầng cuối) |
| I-23 | Deye có thông báo di chuyển dữ liệu Deye Cloud (nội dung chưa đọc) | https://deye.com/vi/deye-cloud-data-migration-announcement/ | Trang hãng (403) | — | Low | — | Không suy diễn sự cố |
| I-24 | Cloud không trong vòng bảo vệ; rơ-le chống phát ngược ưu tiên hơn phần mềm | `A-market-boundary.md` X-04; `C-energy-domain.md` §3.7 | Ghi chú agent (suy luận) | — | Med | — | NFR-SEC-001 |
| I-25 | Schneider giữ lịch mặc định 48 h khi mất kết nối | Xem `B-competitors.md` L15 (URL Schneider trong ledger B) | Tài liệu hãng (Agent B) | 48–72 h | Med | — | NFR-REL-001 |
| I-26 | IEC 62443: SL1–4, 7 FR, 3-2/3-3/4-1/4-2/2-4 | — (kiến thức nền, chưa kiểm chứng URL) | — | — | Med (nội dung phổ biến) | — | Khung thiết kế; cần URL IEC/ISA |
| I-27 | NIST SP 800-82 Rev.3 (9/2023) "Guide to OT Security" | — (kiến thức nền) | — | — | Med | — | Tham chiếu |
| I-28 | Ukraine 2015/2016 (BlackEnergy3/KillDisk; Industroyer với IEC 104) | — (kiến thức nền) | — | — | Med | — | Không VPN thường trực; conduit 104 cô lập |
| I-29 | NĐ 53/2022: lưu trữ dữ liệu tại VN, ≥24 tháng dữ liệu, ≥12 tháng log | — (kiến thức nền) | — | — | Low–Med (số tháng) | — | Hosting VN, retention audit |
| I-30 | Luật BVDLCN 2025 (số 91/2025/QH15?, hiệu lực 1/1/2026?) | — (kiến thức nền) | — | — | Low | Có thể có nghị định thay NĐ 13 | Theo dõi pháp lý |
| I-31 | SunSpec 123/704 có trường reversion time; SMA fallback; OpenEMS `apiTimeout` | — (kiến thức nền) | — | — | Low–Med | Victron chưa rõ (Q-G02) | NFR-REL-002; xác minh từng driver |

---

## 6. Câu hỏi mở / UNKNOWN

| ID | Câu hỏi | Ảnh hưởng | Cách giải quyết (truy vấn đề xuất cho lượt kiểm chứng) |
|---|---|---|---|
| Q-I-01 | Edition hiện hành và câu chữ SL của IEC 62443-3-3, 4-1, 4-2, 2-4, 3-2 | Tài liệu 10, lộ trình chứng nhận | Tìm "IEC 62443-3-3 edition", trang ISA/IEC webstore, ISASecure |
| Q-I-02 | NIST SP 800-82r3 ngày xuất bản, nội dung overlay; NISTIR 7628 Rev.1 | Tham chiếu | Tìm trên csrc.nist.gov |
| Q-I-03 | IEC 62351 phần nào bắt buộc cho IEC 104 trong yêu cầu EVN/QĐ 1570; IEC 60870-5-7 | Kênh điều độ | Hỏi EVN/NLDC; tìm QĐ 1570 toàn văn |
| Q-I-04 | Hiện trạng Luật ANM (có luật hợp nhất mới 2025?), NĐ 53/2022 (điều khoản lưu trữ, thời hạn), Luật BVDLCN 2025 (số, hiệu lực, nghị định hướng dẫn), NĐ 13/2023 còn hiệu lực? | Hosting, retention, DPIA | thuvienphapluat/chinhphu.vn; tư vấn luật |
| Q-I-05 | EMS cho C&I có thuộc "hệ thống thông tin quan trọng về an ninh quốc gia" hoặc phải phân loại cấp độ theo NĐ 85/2016 khi khách là DN nhà nước? | Yêu cầu bổ sung | Tư vấn luật |
| Q-I-06 | CRA áp cho SaaS EMS hay chỉ edge/phần mềm cài đặt? Mốc báo cáo lỗ hổng (theo kiến thức nền: 9/2026) | Mở rộng EU | Tìm "Regulation (EU) 2024/2847 remote data processing solution" |
| Q-I-07 | Watchdog/reversion cụ thể theo hãng: Huawei SUN2000/SmartLogger/EMMA, Sungrow, SMA, PCS tủ BESS phổ biến ở VN, Victron Mode 2/3 | NFR-REL-002 (P0) | Tài liệu Modbus từng hãng + lab (trùng Q-E-04, Q-E-06, Q-G02) |
| Q-I-08 | TimescaleDB: RLS trên hypertable/continuous aggregate có hạn chế gì ở bản đang dùng | NFR-SEC-007 | Tài liệu Timescale + PoC |
| Q-I-09 | Có sự cố bảo mật/khả dụng đã xác nhận của Solarman/Deye cloud không? Gán sự cố 11/2024 cho hãng nào? | Ca lạm dụng, rủi ro | Tìm "Sol-Ark Deye remote disable November 2024", "Solarman breach" |
| Q-I-10 | Grid code VN cho C&I có yêu cầu ramp rate/thời gian phản hồi lệnh điều độ không | SOE `ramp_max`, timeout lệnh 104 | TT 05/2025, QĐ 1570 |
| Q-I-11 | UL 9540 (ed. 3?) / UL 9540A (ed. 5?) / IEC 62933-5-2 — có điều khoản nào về giao diện điều khiển bên ngoài (EMS) cần tuân thủ? | Ranh giới trách nhiệm | Tìm UL/IEC, tài liệu hãng BESS |
| Q-I-12 | UL 2941 / IEEE 1547.3-2023 (an ninh mạng DER) — tồn tại, phạm vi? | Tham chiếu | Tìm UL/IEEE |
| Q-I-13 | Nhà cung cấp DC/cloud tại VN có KMS/HSM managed, object lock WORM không | NFR-SEC-015/016 | Khảo sát Viettel/VNPT/FPT/CMC |
| Q-I-14 | Ngưỡng Fleet Governor (20%/5 phút) hợp lý? Có quy định điều độ về điều khiển tập trung nhiều site? | NFR-SEC-012 | Mô phỏng + hỏi EVN |

---

## 7. Vấn đề gửi agent khác

| ID | Gửi | Vấn đề | Đề xuất |
|---|---|---|---|
| X-I-01 | 06 (Kiến trúc) | Cần ADR: (1) cloud gửi ý định có hạn, edge quyết định; (2) lệnh ký tầng ứng dụng bởi Command Signer tách broker, `seq` đơn điệu; (3) monitoring/control plane tách; (4) Fleet Dispatch Governor; (5) RLS + silo | Vẽ zone/conduit Z0–Z8 trong sơ đồ kiến trúc (class `box ot`, `zone`) |
| X-I-02 | 07 (Tích hợp) / Agent E | Bổ sung vào envelope E §3.19: `seq` (đơn điệu theo site, signer), `danger_class`, `approval_ref`, `kid`; ack có chữ ký edge; trạng thái `REJECTED_INTERLOCK:<code>`, `REJECTED_REPLAY`; driver khai báo `watchdog_support` + `revert_timeout_s` | Cập nhật `capability_profile` và checklist commissioning (test rút cáp) |
| X-I-03 | 08 (Tối ưu) / Agent G | Optimizer chịu Fleet Governor: lịch đội không đổi > ngưỡng/khung nếu không có sự kiện; optimizer là `source=OPTIMIZER` hạng thấp nhất; lịch phát ra phải qua PDP như lệnh C1 | Thêm ràng buộc vào validator `VALIDATED` |
| X-I-04 | 05 (Domain) | Thực thể mới: `SafeOperatingEnvelope@version`, `CommandApproval`, `ControlGrant` (owner→installer, scope, expiry), `KillSwitchState`, `AuditEvent` (hash chain), `EdgeCertificate`, `InterlockState` | Đặt trong bounded context Security/Control |
| X-I-05 | 09 (UX/UI) | Màn hình: hàng đợi phê duyệt C3; trạng thái điều khiển site (LOCAL/REMOTE, kill switch, SOE, interlock, fallback); không có nút "E-stop từ xa"; lệnh C2/C3 hiện tác động MW và hạn; nhãn rõ "Dừng vận hành từ xa" | Dùng phân hạng §3.7.4 |
| X-I-06 | 04 (Yêu cầu) | Chuyển các NFR-SEC/REL/OBS ở §4 vào 04; NFR-SEC-001, 002, 004, 008–014, REL-001–003 là P0 cho bất kỳ release nào bật điều khiển | Gắn test T-… (rút cáp, replay, hết hạn, cross-tenant) |
| X-I-07 | 11 (Lộ trình) | Đề xuất: MVP có thể phát hành **chỉ giám sát + lịch native** trước; bật điều khiển từ xa (setpoint) chỉ khi đủ P0 an toàn lệnh. Chứng nhận: ISO 27001 (V1–V2), IEC 62443-4-2 cho edge (V2) | Đưa vào roadmap |
| X-I-08 | 13 (Rủi ro) | Rủi ro ứng viên: I-R-01 lệnh hàng loạt do tài khoản bị chiếm; I-R-02 thiết bị không có watchdog; I-R-03 kênh cloud hãng song song; I-R-04 rò cross-tenant qua RLS sai cấu hình; I-R-05 khóa ký lệnh bị lộ; I-R-06 pháp lý VN (lưu trữ, DLCN) chưa kiểm chứng; I-R-07 supply chain edge; I-R-08 đồng hồ edge sai làm hỏng kiểm hạn | Cấp mã R-NN |
| X-I-09 | 14 (Nguồn) / Orchestrator | **Hạn mức WebSearch đã hết trước khi Agent I chạy** (0 truy vấn thành công). Toàn bộ nội dung tiêu chuẩn và luật VN trong file là kiến thức nền chưa kiểm chứng (ledger I-26…I-31). Cần lượt kiểm chứng theo Q-I-01…Q-I-14 trước khi phát hành 10 | Đánh dấu nguồn "kiến thức nền" là Low/Med; không đưa vào 10 dưới dạng FACT |
| X-I-10 | B (Đối thủ) | Không viết "Ampowr tuân thủ NIS2" như sự thật — chỉ "tự tuyên bố" (B đã ghi đúng ở L02) | Giữ nguyên câu chữ |
| X-I-11 | F (Dữ liệu) | Đồng ý X-F08. Bổ sung: xuất dữ liệu là sự kiện audit; link ký hết hạn ≤ 7 ngày; xuất D3 (DLCN) cần quyền riêng; dữ liệu analytics bất thường **không bao giờ** tự sinh lệnh C1+ mà không qua PDP | Đưa vào NFR-DATA |
