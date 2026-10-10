# 13 — Câu hỏi mở, giả định, xung đột, quyết định và sổ rủi ro

[← Mục lục](index.html) · [00 Tóm tắt](00-executive-summary.html) · [02 Thị trường](02-market-and-competitor-analysis.html) · [03 Chức năng](03-functional-catalog.html) · [04 Yêu cầu](04-business-requirements.md) · [05 Domain](05-domain-model.html) · [06 Kiến trúc](06-system-architecture.html) · [07 Tích hợp](07-device-integration.md) · [08 Tối ưu](08-energy-optimization.md) · [09 UX/UI](09-ux-ui-specification.html) · [10 An toàn](10-security-and-reliability.md) · [11 Lộ trình](11-mvp-and-roadmap.html) · [12 Truy vết](12-traceability-matrix.md) · [14 Nguồn](14-source-register.md) · [K vòng 1](notes/K-review-round1.md) · [15 Mô phỏng](15-simulators-and-messaging.md)

- **Người viết:** Product/Delivery Lead (phối hợp Agent J — Kiến trúc). **Ngày:** 2026-10-10. **Phiên bản:** 1.1. **Trạng thái:** bản nháp vòng sửa, đã áp quyết định thống nhất của Evidence Judge ([K §6](notes/K-review-round1.md)). v1.1 thêm: tích hợp Huawei cần cho Phase 1 (U-29, U-30, Q-33 chặn G1), rủi ro/câu hỏi từ [15](15-simulators-and-messaging.md) (R-48…R-51, Q-59, mở rộng Q-16) và hai xung đột từ [12](12-traceability-matrix.md) (CF-39, CF-40).
- **Phạm vi:** gom và cấp mã chính thức cho mọi câu hỏi mở, giả định, xung đột, quyết định cần chốt và rủi ro đang nằm rải rác ở ghi chú `notes/`, tài liệu 02–12 và 15. Theo K §6 #38, tài liệu này là nơi duy nhất cấp `Q-NN` và `R-NN`. Mỗi mục ghi **mã tạm gốc** để [12 Truy vết](12-traceability-matrix.md) nối lại.
- **Giới hạn bằng chứng:** không có lượt tìm kiếm mới (hạn mức WebSearch chung đã hết, K mục đầu). Mọi FACT trích ở đây là FACT đã được các agent ghi nhận **qua kết quả tìm kiếm** (snippet) hoặc từ nghiên cứu FusionSolar trước; không URL nào được mở trực tiếp. Mức tin cậy tối đa là "Trung bình".

## Mục lục

0. [Cách đọc và mã định danh](#0-cách-đọc-và-mã-định-danh)
1. [Tóm tắt: mười điều đang chặn](#1-tóm-tắt-mười-điều-đang-chặn)
2. [Câu hỏi mở (Q-NN)](#2-câu-hỏi-mở-q-nn)
3. [Giả định (A-NN)](#3-giả-định-a-nn)
4. [Xung đột đã hòa giải (CF-NN)](#4-xung-đột-đã-hòa-giải-cf-nn)
5. [Quyết định cần chốt (D-NN)](#5-quyết-định-cần-chốt-d-nn)
6. [Sổ rủi ro (R-NN)](#6-sổ-rủi-ro-r-nn)
7. [Tích hợp không khả dụng và mục chưa kiểm chứng (U-NN)](#7-tích-hợp-không-khả-dụng-và-mục-chưa-kiểm-chứng-u-nn)
8. [Điều kiện chặn phát hành tài liệu và cổng phase](#8-điều-kiện-chặn-phát-hành-tài-liệu-và-cổng-phase)
9. [Bảng tra mã tạm → mã chính thức](#9-bảng-tra-mã-tạm--mã-chính-thức)
10. [Vấn đề gửi agent khác](#10-vấn-đề-gửi-agent-khác)
11. [Nguồn trích](#11-nguồn-trích)

---

## 0. Cách đọc và mã định danh

| Mã | Ý nghĩa | Ghi chú |
|---|---|---|
| `Q-NN` | Câu hỏi mở: chưa đủ bằng chứng để quyết | Mã chính thức (K §6 #38) |
| `A-NN` | Giả định đang dùng để lập kế hoạch | Cục bộ của 13; nếu sai thì xem cột "Ảnh hưởng nếu sai" |
| `CF-NN` | Xung đột giữa ghi chú/tài liệu và cách đã hòa giải | CF-01…CF-27 là phán quyết K R-01…R-27; CF-28 trở đi do 13 phát hiện hoặc nhận từ 11/12 (CF-39, CF-40 từ GAP-12-02/03) |
| `D-NN` | Quyết định cần chủ sản phẩm/đội chốt, có phương án và khuyến nghị | Khuyến nghị là `[PROPOSAL]` |
| `R-NN` | Rủi ro: kỹ thuật (KT), thương mại (TM), pháp lý (PL), an toàn (AT), dữ liệu (DL) | Mã chính thức (K §6 #38) |
| `U-NN` | Tích hợp không khả dụng trong nghiên cứu hoặc mục chưa kiểm chứng | Cục bộ của 13; U-29, U-30 (v1.1) được thêm vào §7.2 nên số không liên tục theo mục |

**Vai trò chủ sở hữu (owner).** PO = Product Owner · DL = Delivery Lead · ARC = Kiến trúc sư (Agent J, [06](06-system-architecture.html)) · EDGE = trưởng nhóm edge/firmware · INT = trưởng tích hợp thiết bị ([07](07-device-integration.md)) · DATA = trưởng dữ liệu ([05](05-domain-model.html)) · OPT = trưởng tối ưu ([08](08-energy-optimization.md)) · SEC = trưởng an toàn/bảo mật ([10](10-security-and-reliability.md)) · UX = trưởng UX ([09](09-ux-ui-specification.html)) · LEGAL = pháp chế/tư vấn luật bên ngoài · BIZ = kinh doanh/phát triển khách hàng. Owner là **vai trò**, không phải người cụ thể; PO phân công người khi đội hình được chốt (Q-43).

**Thang đánh giá rủi ro.** Khả năng: Thấp / Trung bình (TB) / Cao. Tác động: Thấp / TB / Cao / Rất cao. "Phase" là phase của [11 Lộ trình](11-mvp-and-roadmap.html) mà rủi ro phải được xử lý trước khi ra cổng.

**Cột "Chặn".** Ghi phase hoặc cổng bị chặn nếu câu hỏi chưa đóng: `G0`…`G4` là cổng ra của Phase 0…4 trong [11](11-mvp-and-roadmap.html#s4); `M1`/`M2` là Gate điều khiển (K §6 #27); "Phát hành 0x" là điều kiện trước khi phát hành tài liệu 0x ra ngoài đội (K §5 G-13).

---

## 1. Tóm tắt: mười điều đang chặn

| # | Điều chặn | Mã | Chặn gì |
|---|---|---|---|
| 1 | Giấy phép TimescaleDB TSL cho SaaS chưa có ý kiến pháp lý | Q-14, R-08 | ADR-06, G0 |
| 2 | Giấy phép OpenEMS theo module và thư viện giao thức | Q-15, R-09 | ADR-07 (edge runtime), G0 |
| 3 | Khung pháp lý dữ liệu/an ninh mạng VN 2026 chưa kiểm chứng | Q-08, R-05 | ADR-18 hosting, phát hành 10, G0 |
| 4 | Ngày áp khung TOU QĐ 963 vào hóa đơn | Q-01, R-01 | Mặc định lịch hóa đơn, báo cáo R2, G1 |
| 5 | Yêu cầu thiết bị chống phát ngược và chấp nhận vòng phần mềm | Q-05, R-03 | Kiến trúc S1, trách nhiệm pháp lý, G1 |
| 6 | Chưa phỏng vấn khách thật; chưa có pilot ký | Q-18, Q-20, R-42 | Thứ tự driver, ưu tiên P0/P1, G0 |
| 7 | Watchdog/reversion thực tế của thiết bị đích | Q-27, R-25 | Gate M2 theo thiết bị, G2 |
| 8 | Phần cứng edge (TPM, BOM) và lab thiết bị chưa chọn | Q-36, R-33 | PoC-03, ADR-19, G0 |
| 9 | Phạm vi MVP (148 FR P0) so với năng lực đội 6–10 kỹ sư; edge là đường găng | Q-43, R-11, R-43 | Toàn bộ lộ trình |
| 10 | Chưa có site pilot BESS có tủ cung cấp register map theo hợp đồng | Q-28, R-45 | G2 |

---

## 2. Câu hỏi mở (Q-NN)

### 2.1 Pháp lý, biểu giá, nghĩa vụ lưới

| Mã | Câu hỏi | Owner | Vì sao quan trọng | Cách giải | Chặn | Mã tạm gốc |
|---|---|---|---|---|---|---|
| Q-01 | Khung giờ TOU của QĐ 963 (cao điểm 17h30–22h30 T2–T7) áp vào hóa đơn sản xuất/kinh doanh **từ ngày nào**? Trạm sạc EV theo khung nào? | LEGAL + BIZ | Sai ngày áp → bộ sinh lịch xả sai giờ, hóa đơn bóng sai. [FACT] khung giờ có trên thuvienphapluat/tuoitre (qua kết quả tìm kiếm); ngày áp `[UNKNOWN]`, nguồn mâu thuẫn | Đọc toàn văn QĐ 963; đối chiếu hóa đơn EVN tháng 9–10/2026 của ≥ 2 khách; hỏi Điện lực | G1 (mặc định lịch hóa đơn); phát hành 00/02/04 | Q-A01, Q-G07, Q-08-07, GAP-04 |
| Q-02 | Ngày lễ/Tết trong QĐ 963 tính như ngày thường hay như Chủ nhật? | LEGAL | Lịch TOU, hóa đơn bóng, dự báo tải | Đọc văn bản; hỏi Điện lực | G1 (chỉ ảnh hưởng ngày đặc biệt) | MQ-10, `_catalog-gaps` (SpecialDay) |
| Q-03 | Giá hai thành phần: cơ sở tính thành phần công suất (`CONTRACTED` hay `MEASURED_MAX`), cửa sổ 30 phút block hay rolling, trên nhập hay net, mọi giờ hay theo khung, phạt vượt đăng ký; khách thí điểm (≥ 200.000 kWh/tháng) đã thanh toán thật từ 07/2026 chưa? | LEGAL + OPT | Quyết định giá trị và thuật toán peak shaving (S7), widget demand, hóa đơn bóng. Chu kỳ 30 phút là FACT Med; cơ sở tính `[UNKNOWN]` (K R-16, R-17) | Đọc văn bản thí điểm BCT/EVN; xin hóa đơn song song của một khách thí điểm | G3 track 3C | Q-A04, Q-C01, Q-G06, Q-08-06, MQ-06, GAP-03, Q-09-01 |
| Q-04 | NĐ 58/2025 + NĐ 243/2026 (VBHN 52) và TT 29/2026: trần 50% tính theo kỳ nào, mẫu số đo ở đâu (đầu ra inverter hay công tơ riêng), quy kết điện BESS xả, có được nạp lưới rồi xả ra lưới không | LEGAL + DATA | Bộ đếm `EXPORT_ENERGY_BUDGET`, sổ cái nguồn gốc năng lượng, `attribution_version`, cờ `allow_ess_export`/`allow_grid_charge` | Đọc VBHN 52 (URL ở [§11](#11-nguồn-trích)); hỏi PC địa phương | G3 track 3D; phát hành 04 | Q-A02, Q-A03, Q-C04, Q-G09, Q-08-09, MQ-11 |
| Q-05 | Hệ hạ áp có cần thiết bị chống phát ngược không? Điện lực có chấp nhận vòng zero-export bằng logger/phần mềm thay rơ-le riêng? Đặc tả kỹ thuật thiết bị (thời gian đáp ứng, vị trí cảm biến, chứng nhận)? | LEGAL + INT | Kiến trúc S1, DO/rơ-le của edge, trách nhiệm pháp lý khi vi phạm (NĐ 133 có chế tài). [FACT, Med] theo tóm tắt VBHN 52: hệ trung áp không bán dư phải có thiết bị bật/tắt phát ngược; hạ áp `[UNKNOWN]` | Đọc VBHN 52 Điều 10(5); hỏi 1–2 PC; xin hồ sơ đấu nối của một dự án | G1 (bằng chứng tuân thủ), G2 (vòng edge) | Q-A09, Q-E-02, Q-C07, Q-08-14, GAP-12 |
| Q-06 | QĐ 1570 và yêu cầu của từng PC cho kết nối điều độ: bảng điểm IEC 104, CA/IOA, kênh truyền, dự phòng, có bắt buộc IEC 62351, hành vi khi mất liên kết | LEGAL + INT + SEC | Phạm vi F-INT-16/F-GRID-12; chỉ FACT Low qua tóm tắt của vendor có lợi ích; con số "≥ 64 kbps, ≤ 125 ms" **không** dùng làm NFR | Lấy văn bản QĐ 1570; hỏi PC; xin hồ sơ dự án đã đấu nối | Kích hoạt track IEC 104 (Phase 2 có điều kiện) | Q-E-01, Q-I-03, Q-10-03, K R-10 |
| Q-07 | Điện lực chấp nhận định nghĩa "vi phạm xuất" nào (dung sai, thời lượng) và ngưỡng nghiệm thu test giới hạn xuất (≤ 5 s) có khớp thực tế? | INT + BIZ | Đếm vi phạm, bằng chứng tuân thủ F-REP-13, biên bản bàn giao | Hỏi PC; đối chiếu biên bản nghiệm thu của installer | G1 | Q-D-02, Q-D-03 |
| Q-08 | Hiện trạng 2026 của luật an ninh mạng, lưu trữ dữ liệu trong nước, dữ liệu cá nhân (Luật BVDLCN 2025, NĐ 13/2023, NĐ 53/2022 và thay đổi 2025–2026): thời hạn lưu trữ, chuyển dữ liệu ra nước ngoài, thời hạn thông báo vi phạm | LEGAL + SEC | Hosting tại VN (mặc định là INFERENCE), retention audit, quy trình sự cố. Toàn bộ là kiến thức nền `[UNKNOWN]` | Tư vấn luật | G0 (ADR-18); phát hành 10 | Q-I-04, Q-F09, MQ-09 |
| Q-09 | Khách là doanh nghiệp nhà nước có buộc phân loại cấp độ hệ thống thông tin không? | LEGAL | Yêu cầu bảo mật bổ sung cho một nhóm khách | Tư vấn luật; hỏi khách | Không chặn MVP | Q-I-05 |
| Q-10 | Phạt/mua công suất phản kháng và yêu cầu ramp/Q/PF cho PV + BESS C&I theo TT 05/2025, QCVN | LEGAL + OPT | KPI PF (P1), tham số `ramp_max_w_per_s` của SOE, điều khiển Q (P2) | Đọc văn bản gốc; hỏi Điện lực | G2 (giá trị ramp trong SOE), G3 | Q-C05, Q-C06, Q-I-10 |
| Q-11 | Nghĩa vụ của cơ sở sử dụng năng lượng trọng điểm sau Luật 77/2025; có văn bản về "tự cung 30%" hay "BESS là điều kiện DPPA"? | LEGAL + BIZ | Persona P2 (energy manager), tính năng xuất ESG/ISO 50001 | Tìm nghị định hướng dẫn | G3 | Q-A07, Q-A08 |
| Q-12 | Hệ số phát thải lưới VN chính thức (năm, cơ quan, loại OM/BM/CM) | DATA | Báo cáo CO₂ (P1) hợp lệ | Tra văn bản chính thức | G3 | Q-C03, MQ-08, Q-H09 |
| Q-13 | VN có chương trình DR trả tiền/ưu đãi cho C&I (2026–2028)? | BIZ + OPT | Quyết định đầu tư tầng 4 (VPP/DR) | Theo dõi BCT/EVN/NSMO | Kích hoạt Phase 4 track 4A | Q-A06, Q-G08, Q-08-08 |

### 2.2 Giấy phép phần mềm

| Mã | Câu hỏi | Owner | Vì sao quan trọng | Cách giải | Chặn | Mã tạm gốc |
|---|---|---|---|---|---|---|
| Q-14 | TimescaleDB TSL có cho phép SaaS EMS tự host khi khách **không** truy vấn DB trực tiếp? Nếu mở "SQL access" thì sao? | LEGAL + ARC | Kiến trúc lõi ADR-06; câu "SaaS không bán DB nên có vẻ được phép" chỉ là INFERENCE | Pháp chế đọc toàn văn TSL; phương án dự phòng PostgreSQL thuần/Tiger Cloud | G0 | Q-F01, NFR-DATA-013 |
| Q-15 | Giấy phép OpenEMS theo từng module (EPL-2.0 và AGPL-3.0 đều có trong repo) và giấy phép thư viện IEC 104/61850/OCPP/Modbus dùng trong sản phẩm đóng | LEGAL + EDGE | ADR-07 edge runtime; không tái dùng UI OpenEMS khi chưa có ý kiến pháp lý (K R-21) | Đọc LICENSE từng module + ý kiến pháp lý | G0 | Q-B9, Q-E-12 |
| Q-16 | Giấy phép và chi phí broker cho SaaS thương mại tự host tại VN: (a) EMQX ≥ 5.9 (BSL 1.1): SaaS của ta có thuộc ngoại lệ "integrating into a product or solution offered to third parties" của grant không, giá Enterprise theo kết nối/node; (b) giá và điều khoản HiveMQ Enterprise tự host tại VN; (c) RabbitMQ 4.x: giới hạn MQTT 5 (shared subscription, message expiry, will delay) và giấy phép hiện hành; (d) cluster có ở bản miễn phí không. VerneMQ đã bị 15 loại | LEGAL + ARC + BIZ | ADR-04 broker; chi phí license chưa có trong kế hoạch MVP (R-49). [FACT, High theo 15 E2-34] EMQX 5.9 đổi sang BSL 1.1, cluster cần license; việc SaaS của ta cần license thương mại là `[INFERENCE]` (E2 F2-22) | Đọc LICENSE trong repo + ý kiến pháp lý; xin báo giá EMQX/HiveMQ trước PoC-02 | G0 (ADR-04) | Q-06-02, Q-E2-01, Q-E2-02, Q-E2-03 |
| Q-17 | Giấy phép và binding Java của OR-Tools (và backend đóng gói), HiGHS, ojAlgo, SCIP, Timefold | LEGAL + OPT | ADR-11 (tầng 3) | Đọc LICENSE bản phát hành | G3 track 3A | Q-G04, Q-08-04 |

### 2.3 Thị trường, khách hàng, mô hình vận hành

| Mã | Câu hỏi | Owner | Vì sao quan trọng | Cách giải | Chặn | Mã tạm gốc |
|---|---|---|---|---|---|---|
| Q-18 | Installer/O&M VN vận hành thế nào: số site/người, dùng ticket trong nền tảng hay CMMS riêng, kỹ thuật viên có tài khoản không, kênh nhận cảnh báo (e-mail/Zalo), ai mua phần mềm | PO + UX | Persona P3 là người dùng hằng ngày P0 nhưng quy trình O&M chưa được nghiên cứu (K G-01); vai trò `TECHNICIAN`; ưu tiên Zalo | Phỏng vấn 5–8 đơn vị O&M/installer + 2–3 chủ C&I | G0 | GAP-01, GAP-06, GAP-15, Q-D-04, Q-H04, K G-01, G-07 |
| Q-19 | Mô hình gói và giá: theo site/kWp (giám sát) và theo site có BESS hoặc MWh BESS (điều khiển)? Mức giá chấp nhận được khi OEM cho dashboard miễn phí? | PO + BIZ | Ranh giới gói `MONITORING`/`CONTROL`; tính bền thương mại. Không hãng EMS nào trong mẫu công bố giá | Phỏng vấn; báo giá thử với pilot | G1 (giá pilot), G4 (billing) | Q-A10, Q-B11, GAP-09, K G-04 |
| Q-20 | Thị phần thiết bị ở site C&I mục tiêu (Huawei, Sungrow, Deye/Solarman, Growatt, Solis, tủ BESS cụ thể) | INT + BIZ | Thứ tự driver MVP (FR-INT-006) và connector cloud | Khảo sát installer; danh mục thiết bị của pilot | G0 | Q-E-16, GAP-11, Q-B12, RB-4, K G-08 |
| Q-21 | Tỷ lệ site C&I có BESS; CAPEX BESS C&I (đ/kWh); cycle life thực tế để đặt `c_deg` mặc định | BIZ + OPT | Định cỡ thị trường M-BESS; quyết định arbitrage (Chủ nhật lãi 511 < 556 đ/kWh với giả định minh họa) | Báo giá, datasheet, bảo hành từ nhà phân phối | G2 (`c_deg` mặc định) | Q-A05, Q-G10, Q-08-10, Q-C08 |
| Q-22 | Site do installer onboard khi chủ tài sản chưa có tài khoản: tenant là ai, ai là bên kiểm soát dữ liệu? | DATA + LEGAL | Mô hình RLS, grant, trách nhiệm pháp lý | Phỏng vấn installer; tư vấn luật | G1 | MQ-02 |
| Q-23 | Chủ C&I chấp nhận đồng ý điện tử để bật điều khiển hay cần văn bản ký? Có cần duyệt từng thay đổi SOE hay chỉ nhận thông báo? | PO + LEGAL | `ConsentRecord`, FR-SEC-005, thời gian bật M2 | Phỏng vấn chủ C&I; mẫu hợp đồng | G1 (consent M1), G2 | Q-D-05, Q-D-08 |
| Q-24 | Ai trực ca 24/7 khi site chạy Gate M2: installer/O&M hay nền tảng? Trách nhiệm khi sự cố ngoài giờ? | PO + SEC | NFR-OBS-008 là điều kiện M2; chi phí vận hành | Phỏng vấn; mô hình hợp đồng | G2 | Q-10-02 |
| Q-25 | Khách có cần luồng dữ liệu thời gian thực (MQTT out, Kafka out) trong 18 tháng? | PO + ARC | Điều kiện chuyển của ADR-05 | Phỏng vấn | G3 | Q-06-04 |
| Q-26 | Chủ C&I muốn xem kế hoạch BESS chi tiết hay chỉ "giá trị tạo ra"? Có cho lệnh C2/C3 và duyệt C3 trên mobile? | UX + SEC | Menu VIEWER; UI-21/UI-22 trên mobile (mặc định của 09: mobile chỉ C1 và engage kill switch) | Phỏng vấn; quyết định của 10 | G2 | Q-09-04, Q-H06 |

### 2.4 Thiết bị và tích hợp

| Mã | Câu hỏi | Owner | Vì sao quan trọng | Cách giải | Chặn | Mã tạm gốc |
|---|---|---|---|---|---|---|
| Q-27 | Watchdog/reversion cho lệnh remote của từng model đích (Huawei SmartLogger/EMMA, Sungrow, SMA, Victron Mode 2/3, PCS tủ phổ biến ở VN); số kết nối Modbus tối đa | INT + SEC | Thiết bị không có watchdog không được nhận setpoint P cưỡng bức (`requires_native_fallback`, K §6 #17) | Tài liệu Modbus bản hiện hành + test rút cáp ở lab (F-INT-28) | G2 (theo thiết bị) | Q-I-07, Q-E-04, Q-E-06, Q-G02, Q-08-02, GAP-02 |
| Q-28 | Tủ BESS phổ biến ở VN có Modbus TCP northbound với P/Q/mode, CCL/DCL? Có cung cấp map theo hợp đồng/NDA? SOC/SOH định nghĩa thế nào (tuyệt đối hay trong cửa sổ khả dụng)? | INT + BIZ | Driver thứ 4 (Gate M2); hiển thị và tối ưu đúng | Phỏng vấn nhà phân phối/EPC; NDA; lab | G2 | Q-E-09, Q-C11, RB-3 |
| Q-29 | Register map chính thức Sungrow Logger1000/EMS300CP/SH và cách bật EMS mode ghi được; tài liệu chiến lược EMS và endpoint điều khiển của Open API | INT | Driver thứ 5 | Kênh đối tác Sungrow VN; lab | Phase 2/3 (driver thứ 5) | Q-E-03, Q-B8 |
| Q-30 | Huawei C&I chạy TOU + capacity control đồng thời không; thứ tự ưu tiên native | INT + OPT | Tránh hai lớp điều khiển đánh nhau ở Gate M1 (R-14) | Manual + lab | G1 (milestone 1b) | Q-G03, Q-08-03 |
| Q-31 | Thanh ghi điều khiển nào ghi vào NVM; giới hạn số lần ghi | INT | Mòn flash (R-15); cờ `persist` | Hỏi hãng | G2 | Q-E-05 |
| Q-32 | Dữ liệu công tơ EVN: đọc được qua DLMS/IEC 62056 hoặc cổng quang không; nhãn đầu/cuối khoảng; ngày chốt kỳ | DATA + INT | Đối soát hóa đơn bóng với công tơ thanh toán (F-TAR-10) | Hỏi Điện lực; thu file load profile thật từ pilot | Phase 2 (F-TAR-10) | Q-C02, Q-F10, MQ-07, GAP-07 |
| Q-33 | Hạn mức và cơ chế xác thực API cloud: (a) **Huawei Northbound đọc** (OAuth Connect: endpoint, grant, hạn token, hạn mức gọi, điều kiện tài khoản installer/developer, cơ chế owner consent); (b) Growatt V1, Deye, Solis; (c) ghi qua cloud: Huawei OAuth Connect control API, SMA GridControl API cấp cho ai | INT + BIZ | (a) là connector F-MON-02 của Phase 1 (D-20, pilot (c) ở [11](11-mvp-and-roadmap.html)); (b) định cỡ connector chỉ đọc khác; (c) ghi qua cloud (P2, CF-39) | Xin tài khoản installer/developer Huawei qua pilot (c) + văn bản đồng ý của chủ site; đo hạn mức trong lab (U-29) | **G1** cho (a); Phase 3 cho (b); Phase 4 track 4D cho (c) | Q-E-10, Q-E-11, Q-E-14 |
| Q-34 | OCPP: chu kỳ cập nhật tối thiểu các bộ sạc phổ biến ở VN chấp nhận; Security Whitepaper 1.6J Ed.4 (02/2026) có đổi yêu cầu profile; OCPP 2.1 DER control dùng được cho kênh EMS → CSMS | INT + OPT | EV DLM, kiến trúc EV khi có CPO | Lab với charger thật; đọc tài liệu OCA | G3 track 3E | Q-G11, Q-08-11, Q-E-08, Q-E-17 |
| Q-35 | SunSpec: model 715 là gì; trạng thái 802–805; sentinel 0x8000 | INT | Bảng model của driver SunSpec chung | Định nghĩa model trên GitHub SunSpec | G1 (driver thứ 3) | Q-E-07 |
| Q-36 | Ứng viên phần cứng edge (CPU/RAM, TPM 2.0, secure boot, 2 NIC, CAN, 4G, SSD TBW), giá BOM; chi phí lab thiết bị | EDGE + PO | PoC-03, ADR-19, buffer 30 ngày, chi phí mỗi site | RFQ 2–3 nhà cung cấp | G0 | Q-E-15, Q-06-06, Q-10-01, GAP-17, K G-06 |
| Q-37 | Khối lượng dữ liệu thực tế sau nén/deadband cho site C&I điển hình; số điểm thật của model BESS/PCS phổ biến | DATA + INT | Định cỡ buffer, băng thông 4G, lưu trữ (±3×) | PoC-01 + đo trên pilot | G1 | Q-E-13, Q-F02, Q-F04 |

### 2.5 Dữ liệu, kiến trúc, hạ tầng

| Mã | Câu hỏi | Owner | Vì sao quan trọng | Cách giải | Chặn | Mã tạm gốc |
|---|---|---|---|---|---|---|
| Q-38 | RLS áp được trên hypertable/continuous aggregate của TimescaleDB không; nếu không thì cô lập tenant ở tầng tổng hợp thế nào? | ARC + SEC | Rò cross-tenant (R-35) | PoC-04 | G0 | MQ-01, Q-I-08 |
| Q-39 | Thông lượng ingest (35 k mẫu/s, đỉnh 350 k), độ trễ CAGG, `time_bucket` theo timezone từng site ở phiên bản hiện hành | ARC + DATA | ADR-06; điểm chuyển shard/ClickHouse (giả thuyết 3.000–5.000 site chưa có benchmark) | PoC-01 | G0 | Q-F03, Q-F12 |
| Q-40 | Lưu tổng hợp 5 phút 5 năm cho mọi chuỗi (~10,5 TB/1.000 site) hay chỉ `LONG_5M` sau 13 tháng? Lưu kế hoạch MPC: chỉ slot đã chạy + `input_hash` + snapshot content-addressed? | PO + DATA | Chi phí lưu trữ ×10; khả năng tái lập | Quyết định D-06 | G1 (5 phút), G3 (MPC) | MQ-03, MQ-04, Q-06-05 |
| Q-41 | Giá trị MANUAL (chỉ số đọc tay, hóa đơn nhập tay) ánh xạ sang KPI enum là ESTIMATED hay MEASURED? | DATA | Nhãn chất lượng trên hóa đơn bóng | Quyết định của 05 + 09 | G1 | MQ-05 |
| Q-42 | Site chỉ giám sát qua cloud hãng (5 phút): chạy phân bổ luồng ở 5 phút với cờ, chấp nhận sai số netting? | DATA | KPI tự tiêu thụ cho site monitoring-only | Đo `netting_kwh` trên pilot | G1 | MQ-12 |
| Q-43 | Quy mô và kỹ năng đội thực tế (số người, edge/embedded, vận hành PostgreSQL/Kubernetes) | PO | Năng lực MVP; edge là đường găng ([11 §11](11-mvp-and-roadmap.html#s11)); ADR-01/07/18 | Chủ dự án xác nhận | G0 | Q-06-01, Q-D-07 |
| Q-44 | Nhà cung cấp hạ tầng tại VN có managed Kubernetes, KMS/HSM, object lock (WORM), hai vùng khác tỉnh? | ARC + SEC | ADR-13, ADR-18, NFR-REL-006, neo WORM | Khảo sát nhà cung cấp | G0 (KMS), Phase 2 (WORM) | Q-06-03, Q-I-13 |
| Q-45 | Tỷ lệ người dùng mobile và mạng 4G tại site ảnh hưởng tới SSE và băng thông edge? Keepalive/Session Expiry MQTT tối ưu theo NAT timeout của nhà mạng VN (R-51)? | ARC + UX + EDGE | ADR-03, §14 của 06; ổn định uplink và chi phí dữ liệu 4G | Đo trên pilot | G1 | Q-06-07, Q-E2-09 |
| Q-59 | Mosquitto 2.1 có dùng được làm broker **pilot** (≤ ~100–200 edge, một node + standby nóng) không: shared subscription, giới hạn kết nối/tin, cấu hình cert-as-username, cơ chế ACL thay `acl_file`/`password_file` đã deprecate; tiêu chí thoát sang broker PoC-02. Đây là thay đổi so với 06 ADR-04 ("Mosquitto chỉ dev/lab") do 15 đề xuất | ARC | Nếu không chốt, Phase 1 phải chờ license broker production (Q-16) mới có pilot | PoC nhỏ theo 15 (T-E2-04 chạy trên Mosquitto và ≥ 1 ứng viên PoC-02); người viết 06 quyết | G0 (ADR-04) | Q-E2-07 |

### 2.6 An toàn, bảo mật, tiêu chuẩn

| Mã | Câu hỏi | Owner | Vì sao quan trọng | Cách giải | Chặn | Mã tạm gốc |
|---|---|---|---|---|---|---|
| Q-46 | `T_stale_poc` phù hợp (2–5 s, mặc định 3 s) với công tơ phổ biến và vòng 1 s? | SEC + INT | Chuyển về native không cần thiết vs an toàn | HIL + pilot | G2 | Q-D-01 |
| Q-47 | Ngưỡng Fleet Dispatch Governor (20% MW BESS tenant/5 phút; 5% nền tảng) và miễn trừ lệnh "về 0" có hợp lý? | SEC | NFR-SEC-012 | Mô phỏng; hỏi điện lực | G2 | Q-I-14 |
| Q-48 | Edition và câu chữ của IEC 62443 (3-2/3-3/4-1/4-2/2-4), NIST SP 800-82, CRA, UL 9540/9540A và IEC 62933-5-x về giao diện EMS ngoài | SEC | Lộ trình chứng nhận; ranh giới trách nhiệm; không tuyên bố tuân thủ khi chưa đối chiếu (K §6 #34) | Đọc tiêu chuẩn chính thức | G4 (chứng nhận) | Q-I-01, Q-I-02, Q-I-06, Q-I-11 |
| Q-49 | `T_offline_alarm_connector` = 30 phút có quá chậm cho khách chỉ giám sát? | UX + INT | Cảnh báo kết nối site monitoring-only | Đo trên pilot | G1 | Q-D-06 |

### 2.7 Tối ưu, dự báo, đo tiết kiệm

| Mã | Câu hỏi | Owner | Vì sao quan trọng | Cách giải | Chặn | Mã tạm gốc |
|---|---|---|---|---|---|---|
| Q-50 | Độ chính xác dự báo bức xạ ở VN (mùa mưa, mây đối lưu chiều); gói thương mại Solcast/Open-Meteo/Meteomatics (độ phân giải, giá, điều khoản); ngưỡng chính xác để dự báo thắng bộ điều khiển phản ứng | OPT + DATA | Giá trị tầng 3 và peak shaving dựa dự báo | Thử song song 2–3 nhà cung cấp trên pilot ≥ 3 tháng | G3 track 3A/3B | Q-F05, Q-F06, Q-F11 |
| Q-51 | Thời gian giải LP/MILP thực tế (192 slot, 0–20 phiên EV) với dữ liệu site thật | OPT | NFR-PERF-010 (tầng 3) | PoC-05 | G3 track 3A | Q-G05, Q-08-05 |
| Q-52 | Kp/Ki và margin zero-export điển hình theo loại inverter/logger | OPT + INT | Commissioning vòng edge (F-GRID-05) | Test bước tải tại hiện trường | G2 | Q-08-13 |
| Q-53 | Bằng chứng tiết kiệm độc lập cho BESS C&I dưới TOU; văn bản IPMVP/ASHRAE Guideline 14 (định nghĩa option, ngưỡng CV(RMSE)/NMBE) | OPT + PO | Định vị, cách diễn đạt "tiết kiệm"; không tuyên bố tuân thủ sai | Nghiên cứu độc lập; mua/đọc văn bản | G3 (R7 B1/B2) | Q-G12, Q-08-12, Q-F07, Q-F08 |
| Q-54 | Tên và tham số các controller OpenEMS ngoài `PeakShaving`/`Balancing` | EDGE | Chỉ cần nếu ADR-07 chọn OpenEMS | Đọc `io.openems.edge.controller.*` | Sau ADR-07 | Q-G01, Q-08-01 |

### 2.8 UX

| Mã | Câu hỏi | Owner | Vì sao quan trọng | Cách giải | Chặn | Mã tạm gốc |
|---|---|---|---|---|---|---|
| Q-55 | Ngưỡng LIVE/DELAYED/OLD theo nguồn thật (Modbus, MQTT, connector) | UX + DATA | `freshness` (04 §2 là điểm xuất phát) | Đo trong PoC/pilot | G1 | Q-H07 |
| Q-56 | Thuật ngữ tiếng Việt quen thuộc (demand, shelve, acknowledge, curtailment); ký hiệu/màu SLD và SCADA ở điện lực VN | UX | i18n; UI-06 (SLD, P1) | Phỏng vấn; tài liệu EVN | G1 (thuật ngữ), G3 (SLD) | Q-H10, Q-H05 |
| Q-57 | Bảng màu đề xuất có phân biệt được khi mù màu và đạt tương phản 3:1 trên nền tối? | UX | Toàn bộ UI | Công cụ mô phỏng + 3–5 người dùng | G1 | Q-09-03 |
| Q-58 | Mức tương tác thật của giao diện đối thủ ngoài FusionSolar (Victron VRM, Enphase, iSolarCloud, OpenEMS UI, Schneider EMA) | UX | Benchmark UI; hiện chỉ so được với FusionSolar (K §3.7) | Tài khoản demo; OpenEMS UI chỉ chạy local sau ý kiến pháp lý | Không chặn | Q-H01 |

**Đã đóng trong vòng này (không cấp Q):** cơ chế cập nhật live (Q-09-02) → ADR-03 REST + SSE ([06](06-system-architecture.html)); kênh ack telemetry (X-07-03) → ADR-16 giữ `down/config`; phương pháp chuẩn hóa JSON trước khi ký (X-07-05) → JCS + JWS ES256 ([10 D-10-10](10-security-and-reliability.md)).

---

## 3. Giả định (A-NN)

Mỗi giả định là cơ sở lập kế hoạch ở [11](11-mvp-and-roadmap.html). "Kiểm khi" là thời điểm phải xác nhận hoặc bác bỏ.

| Mã | Giả định | Nhãn | Ảnh hưởng nếu sai | Kiểm khi | Liên quan |
|---|---|---|---|---|---|
| A-01 | Người mua chính là installer/O&M/ESCO; chủ C&I là người xem báo cáo | [INFERENCE] (A §3.3, chưa có số liệu) | Đổi persona chính; đổi ưu tiên giữa O&M (M-ALM) và báo cáo tài chính (M-REP); đổi kênh bán | G0 | Q-18, R-42 |
| A-02 | Đại đa số C&I chưa trả phí công suất; chỉ khách thí điểm ≥ 200.000 kWh/tháng **có thể** đã trả từ 07/2026 | [INFERENCE] (K R-17) | Nếu demand charge áp đại trà sớm: peak shaving theo demand (F-OPT-16) phải kéo từ Phase 3 lên Phase 2 | Mỗi cổng; khi Q-03 đóng | Q-03, D-16 |
| A-03 | Zero-export/giới hạn xuất là chế độ phổ biến nhất | [INFERENCE] từ [FACT]: 28.254 hệ TSXTTT, chỉ ~287 hệ đăng ký bán dư; đến 08/2026 chưa có giao dịch bán dư theo NĐ 243 (vietnamnet, pv-magazine) | Nếu bán dư tăng nhanh: ngân sách xuất 50% và IEC 104 phải kéo lên sớm hơn | G1, G2 | Q-04, Q-06 |
| A-04 | Controller native (Huawei SmartLogger/EMMA) cho cấu hình giới hạn xuất, TOU và chế độ pin qua Modbus có readback | [INFERENCE] từ tài liệu hãng qua snippet (02 L37, L38) | Gate M1 cho BESS chậm; phải đưa vòng edge (Gate M2) lên sớm cho cả chức năng giới hạn xuất | G0 (lab), G1 | Q-30, R-13, U-30 |
| A-05 | Đội 6–10 kỹ sư trong 12–18 tháng đầu, gồm 1–2 người edge/firmware; stack Java/Spring + Angular đã quen | [INFERENCE] (06 §3.3) | Ước lượng ở 11 sai; edge thành nút cổ chai | G0 | Q-43, R-11, R-43 |
| A-06 | MVP 50–200 site; thiết kế cho 1.000 site; mở tới 10.000 site không đổi hợp đồng edge | [PROPOSAL] (06 §3.3) | Kích thước hạ tầng, PoC-01/02 | G1 | Q-39 |
| A-07 | Có nhà cung cấp hạ tầng tại VN đủ dịch vụ (Kubernetes, KMS/HSM, object storage) | [INFERENCE] | Phải dùng HSM thiết bị hoặc hosting ngoài VN (cần ý kiến pháp lý) | G0 | Q-44, R-21 |
| A-08 | Site tham chiếu 1.000 điểm; site lớn 5.000; PV-only 200 | [PROPOSAL] (K §3.5) | Định cỡ ingest/lưu trữ/edge sai | G1 | Q-37 |
| A-09 | Khách chấp nhận lắp edge của ta ở site có điều khiển (chi phí phần cứng + lắp đặt) | [INFERENCE] | Gate M1/M2 không bán được; phải dựa vào connector cloud chỉ đọc | G0 | Q-19, Q-36 |
| A-10 | Có ít nhất một khách pilot có BESS với tủ cung cấp register map theo hợp đồng | [INFERENCE] | G2 không có nơi chứng minh | G1 | Q-28, R-45 |
| A-11 | Khung QĐ 963 đã hoặc sẽ áp vào hóa đơn trước khi pilot chạy tối ưu | [INFERENCE] | Phải chạy lịch TT 16/2014 song song lâu hơn; hóa đơn bóng hai phiên bản | G1 | Q-01, R-01 |
| A-12 | Pilot cho truy cập hóa đơn EVN hằng tháng | [INFERENCE] | Không đối soát được hóa đơn bóng; giá trị số 2 (TOU) yếu | G0 | Q-32 |
| A-13 | Huawei chiếm tỷ trọng lớn ở pilot; thứ tự driver FR-INT-006 đúng | [INFERENCE] (Sungrow tự công bố 45% mái nhà 2020 là nguồn cũ, Low) | Đổi thứ tự driver; lab mua sai thiết bị | G0 | Q-20, R-41 |
| A-14 | Số tự công bố ≤ 2 s (zero feed-in) / ≤ 5 s (peak shaving) của SmartLogger5000B/SmartMGC5000B đạt được ngoài hiện trường | [FACT] chỉ là số hãng tự công bố (K R-19) | Ngưỡng test F-INT-27 (≤ 5 s) không đạt với native | G1 | Q-07 |
| A-15 | Luật tầng 2 (TOU, Java) mang phần lớn giá trị BESS dưới QĐ 963; tầng 3 có thể chờ | [INFERENCE] (08 §16: giá trị lớn nhất là PV lẽ ra bị cắt và arbitrage cao/thấp ≈ 2,86×) | Nếu tầng 3 vượt luật nhiều, Phase 3A cần sớm hơn | G3 (backtest) | Q-50, Q-51 |
| A-16 | Mất mạng tại site ≤ 7 ngày trong phần lớn trường hợp | [PROPOSAL] (K #18) | Mất dữ liệu ngoài cửa sổ buffer cứng | G1 | NFR-DATA-001 |
| A-17 | Trực ca 24/7 cho site M2 có thể do installer/O&M đảm nhận với công cụ của ta | [INFERENCE] | Nền tảng phải tự lập NOC; chi phí tăng | G2 | Q-24, R-32 |
| A-18 | Tham số mặc định ở [04 §2](04-business-requirements.md) đủ dùng tới khi có PoC/pilot | [PROPOSAL] | Điều chỉnh tham số, không đổi cấu trúc yêu cầu | G1, G2 | Q-46, Q-49, Q-55 |
| A-19 | Thuê được đơn vị pen-test bên thứ ba và dựng được HIL trước site M2 đầu tiên | [INFERENCE] | G2 trễ | G1 | R-43 |
| A-20 | Giả định `c_deg` ≈ 556 đ/kWh (C_repl 3 tr đ/kWh, 6.000 chu kỳ, 90% DoD) chỉ để minh họa | [INFERENCE] (không có nguồn giá VN) | Quyết định chạy chu kỳ Chủ nhật/giờ thường sai | G2 | Q-21 |

---

## 4. Xung đột đã hòa giải (CF-NN)

### 4.1 Phán quyết của Evidence Judge (K vòng 1)

CF-01…CF-27 tương ứng một–một với K R-01…R-27 ([K §2](notes/K-review-round1.md)). Bảng này chỉ ghi kết luận và nơi đã áp; lý do đầy đủ ở K.

| Mã | K | Chủ đề | Phán quyết (tóm tắt) | Đã áp ở |
|---|---|---|---|---|
| CF-01 | R-01 | Dấu P | Lưới + = nhập; BESS + = xả; PV/tải/EV/máy phát ≥ 0 (đổi so với FS cũ: + = xuất) | 04 §0.4, 05, 07 §7.2 |
| CF-02 | R-02 | Dấu Q | Q cùng hướng P của từng điểm đo; driver khai báo quy ước gốc | 05, 07 |
| CF-03 | R-03 | Đơn vị | Raw/edge W, Wh, var, VA (int64 Wh); aggregate/KPI/API kW/kWh; hậu tố đơn vị | FR-HIST-003 |
| CF-04 | R-04 | Timestamp | `ts` (edge, chính), `ts_src`, `ts_ingest` | FR-MON-002 |
| CF-05 | R-05 | Nhãn bucket | `bucket_start`, `[start, start+Δ)` (đổi so với C/F nhãn cuối khoảng) | FR-HIST-005, 05 §7 |
| CF-06 | R-06 | Quality | Ba tầng; `STALE` của F → `FROZEN`; `freshness` riêng ở UI | FR-HIST-007, FR-MON-005 |
| CF-07 | R-07 | Arbiter | 12 mức, mức 1–6 cố định | 04 §1.3, 07 §3.2, 08 §4.2 |
| CF-08 | R-08 | MVP có điều khiển? | Hai cổng M1/M2 trong MVP; M2 theo site khi đủ P0 an toàn | 03, 04, 10 §20.4; 11 tách thành Phase 1/Phase 2 (D-01) |
| CF-09 | R-09 | Ai chạy vòng nhanh | Edge bắt buộc ở site có lệnh; native trước; `control_owner` | FR-INT-001, FR-OPT-003 |
| CF-10 | R-10 | IEC 104 | P1 có điều kiện; MVP dùng slave 104 của logger/gateway | F-INT-16; 11 Phase 2 có điều kiện (D-07) |
| CF-11 | R-11 | Ký lệnh | JWS bắt buộc trước M2; ghi native qua edge ở M1 cũng ký | ADR-13, NFR-SEC-004 |
| CF-12 | R-12 | Topic MQTT | `ems/v1/{edge_id}/up/…`, `…/down/…` | 07 §7.1, ADR-04 |
| CF-13 | R-13 | Buffer edge | Cứng 7 ngày không mất; mục tiêu 30 ngày; 1 s giữ 7 ngày | NFR-DATA-001 |
| CF-14 | R-14 | Hạng lệnh | C0–C4 của I; ánh xạ từ A/B/C/D của H | FR-SEC-006 |
| CF-15 | R-15 | Chế độ BESS | `site_strategy` và `slot_mode` là hai từ vựng | FR-BESS-004, FR-OPT-005 |
| CF-16 | R-16 | Giá hai thành phần | Cơ sở tính UNKNOWN; `demand_basis` tắt mặc định; peak shaving demand P1 | Q-03, F-TAR-07 |
| CF-17 | R-17 | Demand charge VN | Hạ xuống INFERENCE "đại đa số" | A-02 |
| CF-18 | R-18 | Trang InfinitePower | Chỉ dùng cho định nghĩa chung, cần nguồn thứ hai | U-01 |
| CF-19 | R-19 | Số ≤ 2 s/≤ 5 s | Ghi SmartLogger5000B/SmartMGC5000B; số hãng tự công bố | A-14 |
| CF-20 | R-20 | Huawei peak shaving on/off-grid | Chỉ trong phạm vi manual LUNA2000-(107-215) C&I-Microgrid-SmartLogger3000 | 02 §13.1 |
| CF-21 | R-21 | Giấy phép OpenEMS | UNKNOWN, chặn ADR-07 | Q-15 |
| CF-22 | R-22 | Ngôn ngữ tối ưu | Tầng 1–2 Java; tầng 3 OR-Tools Java trước, Python sidecar chỉ qua ADR-11 | ADR-11 |
| CF-23 | R-23 | Lịch Schneider 15 phút/72 h | FACT Low–Med; số của ta là PROPOSAL độc lập | 02 §13.1 |
| CF-24 | R-24 | Widget demand | Thanh nhập/trần, xuất/giới hạn P0; đồng hồ demand P1 | F-GRID-07, F-GRID-09 |
| CF-25 | R-25 | Lưu giữ audit | Trực tuyến ≥ 13 tháng; WORM ≥ 5 năm | NFR-DATA-009 |
| CF-26 | R-26 | Nhãn mức cảnh báo | Khẩn cấp / Cao / Trung bình / Thông tin | 09, 05 |
| CF-27 | R-27 | Tên chế độ lưới | `export_mode` + `export_limit_w` + `import_cap_w`; lệnh giữ tên của E | FR-GRID-003 |

### 4.2 Xung đột mới do 13/11/12 phát hiện

| Mã | Xung đột | Các lập trường | Hòa giải | Trạng thái |
|---|---|---|---|---|
| CF-28 | Phê duyệt hai người C3 được đánh dấu Gate M2 ở 04 (FR-SEC-006, FR-SEC-007 = `C3·M2`), nhưng nhiều thao tác Gate M1 là C3: cấu hình lưới site (F-GRID-03 `C3·M1`), cờ chủ vòng (F-OPT-02 `C3·M1`), OTA edge (F-INT-12 `C3·M1`), tách mặt phẳng/bật điều khiển (F-SEC-05 `C3·M1`) | 04 bảng FR vs 03 cột "Điều khiển?" | **Phân hạng C0–C4 và hàng đợi duyệt C3 phải có trong Phase 1** (trước Gate M1). Phần nâng hạng theo ngữ cảnh M2 (> 10% MW BESS, xả cưỡng bức > 30 phút) bật cùng M2 | Đề xuất; gửi 04 sửa cột Hạng·Gate (D-03) |
| CF-29 | Tên phase: 03/04 dùng "Later (Phase 1/2)" làm hạng phát hành, trong khi 11 dùng Phase 0–4 cho lộ trình | Hai hệ đặt tên trùng chữ "Phase" | 11 §2.3 có bảng ánh xạ: hạng "MVP" của 03/04 = Phase 1 + phần M2 của Phase 2; "Later (Phase 1)" phân vào Phase 2/3; "Later (Phase 2)" vào Phase 4. Khi trích, ghi "hạng 03: Phase 1" hoặc "lộ trình: Phase 1" | Áp ở 11 |
| CF-30 | Khả dụng Command API: 04 NFR-REL-004 "≥ 99,9% giờ làm việc" vs 10 D-10-08 "≥ 99,5% tổng" | Hai cửa sổ đo khác nhau | Không mâu thuẫn nếu ghi rõ cửa sổ; SLO chính thức (NFR-OBS-005) phải nêu cả hai cửa sổ. Không đổi số | Gửi 04/10 thống nhất câu chữ |
| CF-31 | Trạng thái phê duyệt: 07 §8.4 `APPROVAL_DENIED` vs 04/05/10 `APPROVAL_REJECTED` | X-10-04 | Dùng `APPROVAL_REJECTED` (theo 05) | 07 cần sửa |
| CF-32 | ACL topic `down/config`: 10 §9.3 chỉ cho `svc-config-*` publish; ADR-16 cho `svc-ingest-ack` publish tin ack/resend không ký | X-06-01 | Giữ ADR-16 (không đổi R-12); 10 cập nhật ACL; edge chỉ áp tin `CONFIG` có chữ ký | 10 cần sửa |
| CF-33 | HMI cục bộ: H-P21 xếp P2, 03 xếp P1 (F-MON-11), K đề nghị cân nhắc P1 vì công tắc LOCAL và kỹ sư tại chỗ | H vs K vs 03 | 11 đưa F-MON-11 vào **Phase 2, trước site M2 đầu tiên**, tối thiểu trang trạng thái/interlock (GAP-10) | Áp ở 11 |
| CF-34 | Baseline B0 (GAP-05): 03 để R7 ở P1, nhưng giá trị số 2 (minh bạch TOU) cần so sánh sớm | 03 vs 08 §15.5 | Kéo **B0** vào Phase 1 như một dòng trong R2 (không cần mô phỏng); B1/B2 và phân rã ở Phase 3 (D-02) | Áp ở 11 |
| CF-35 | `T_offline_alarm_connector`: F §3.13 ví dụ 10 phút; 04 chọn 30 phút | F vs 04 | Giữ 30 phút (04) vì nguồn cloud hãng trễ tự nhiên; đo lại trên pilot (Q-49) | Giữ 04 |
| CF-36 | Mã FR-OPT tạm của G trùng chữ với FR-OPT chính thức của 04 (ví dụ FR-OPT-004 khác nghĩa) | G vs 04 | Mã tạm G không được dùng ở tài liệu chính thức; bảng ánh xạ ở 04 §7.2 | Đã xử lý ở 04 |
| CF-37 | Tầng 3 "P1" (K #23) nhưng cổng bật cần ≥ 90 ngày dữ liệu (08 §14.4) | Ưu tiên vs điều kiện dữ liệu | Tầng 3 nằm ở Phase 3 với trigger "≥ 3 site M2 có ≥ 90 ngày dữ liệu ≤ 5 phút"; không phải mốc cố định | Áp ở 11 |
| CF-38 | Thời điểm cần TPM: 10 D-10-13 cho phép edge thiếu TPM là ngoại lệ tạm thời; K §3.8 nêu TPM là yêu cầu nặng | 10 vs yêu cầu P0 | Edge thiếu TPM được dùng ở site chỉ giám sát và Gate M1 có ngoại lệ ghi rủi ro (R-33); **không** bật Gate M2 trên edge thiếu TPM/secure element (D-12, đề xuất chặt hơn 10) | Chờ D-12 |
| CF-39 | Đường ghi không qua envelope/arbiter của edge (GAP-12-02): FR-EV-004 ghi giới hạn công suất sang API của CPO và FR-INT-028 ghi qua cloud hãng (Huawei OAuth Connect control API) đều là lời gọi tới hệ thống bên ngoài, có thể bỏ qua SOE, TTL, arbiter và Fleet Governor của ta; mâu thuẫn tiềm tàng với K §6 ("cloud không bao giờ ghi trực tiếp thiết bị; gửi ý định có hạn, edge quyết"; "edge bắt buộc ở mọi site nền tảng ghi lệnh") | 12 (GAP-12-02) vs 04 FR-EV-004 (bản mới), FR-INT-028; 07 §8.8 | **Quyết định:** mọi lệnh ghi qua CPO hoặc cloud hãng phải thỏa đủ: (1) đi qua PDP, hạng lệnh (≥ C2 cho cloud hãng), Fleet Governor và envelope ký như lệnh edge; (2) có hạn (`expires_at`, TTL phía bên ngoài ≤ hạn envelope; bên ngoài không hỗ trợ hạn → cấm ghi); (3) readback, chỉ báo `APPLIED` khi khớp, không khớp → `FAILED_NO_EFFECT`; (4) mặc định khi mất liên lạc đã kiểm khi commissioning (profile an toàn của CPO; chế độ native của hãng); (5) không dùng cho vòng điều khiển nhanh hay mức 1–6 của arbiter; (6) ở site có edge, edge là client gọi API và arbiter của edge vẫn giữ trần nhập/giới hạn xuất bằng tài nguyên khác. Không thỏa → **cấm**, tích hợp chỉ đọc. FR-EV-004 bản mới của 04 đã đạt (1)–(6). FR-INT-028 **chưa** nêu hạn, readback, mặc định mất liên lạc, Governor → phải sửa 04 trước khi bật cờ, nếu không thì bỏ FR. Site chỉ giám sát (không có edge) không được bật FR-INT-028 cho tới khi Evidence Judge chấp nhận ngoại lệ có lý do | `[PROPOSAL]`; FR-EV-004 đã áp ở 04; FR-INT-028 gửi 04/07/10 (§10); chặn G2 cho ghi EV qua CPO, G3 track 3E, G4 track 4D |
| CF-40 | `COMMISSIONING_TEST` (GAP-12-03): FR-INT-016/017/018 (phép thử dấu, test giới hạn xuất, test watchdog) ghi lệnh thật vào thiết bị khi commissioning, là P0 · M1, nhưng bản trước của 04/12 không có NFR an toàn và không có F- riêng ở 03 | 12 (GAP-12-03) vs 04 bản trước | 04 bản mới cấp FR-INT-031 (đường ghi duy nhất, xác nhận có mặt bằng nút vật lý, phong bì test \|P\| ≤ min(10% P định mức, 50 kW), `REVERT_DEFAULT` khi thoát) và NFR-SEC-033 (P0 · M1). **Vẫn chặn G1** tới khi: 03 cấp F- riêng; 07 §9.4 và 10 IL-10 dẫn đúng FR-INT-031/NFR-SEC-033; 12 thêm dòng truy vết; AC-INT-10 có trong bộ test Phase 1 ([11](11-mvp-and-roadmap.html)). Phần còn lại của GAP-12-03 (một PCS mất liên lạc, PCS đã dừng, EV mất `MTR_POC`, IEC 104 mất liên kết, trực ca 24/7) chặn G2 | Một phần đã áp ở 04; gửi 03/07/10/12 (§10) |

---

## 5. Quyết định cần chốt (D-NN)

| Mã | Quyết định | Phương án | Khuyến nghị `[PROPOSAL]` | Chốt bởi · trước | Căn cứ |
|---|---|---|---|---|---|
| D-01 | Định nghĩa MVP và thứ tự phát hành | (a) Một bản MVP gồm cả M1 và M2. (b) Phase 1 phát hành giám sát + Gate M1; Phase 2 bật Gate M2 theo site. (c) M2 trước cho khách BESS | **(b).** Giá trị số 1–3 ở VN (tuân thủ xuất, minh bạch TOU, O&M) đạt được ở Gate M1 mà không cần vòng edge; bộ an toàn P0 của M2 nặng và cần HIL, pen-test, trực ca | PO · G0 | K §6 #3, #27; 04 Q-D-07; 11 §11 |
| D-02 | Kéo baseline B0 vào Phase 1 (GAP-05)? | (a) Có, một dòng "Chi phí nếu không có PV và BESS ≈ X đ (ước tính)" trong R2. (b) Không, chờ R7 | **(a).** Chỉ cần `E_cons` từ cân bằng thanh ghi và hóa đơn bóng đã có; gắn nhãn "≈ ước tính" | PO · G0 | 08 §15.5, CF-34 |
| D-03 | Phân hạng C0–C4 và duyệt C3 vào Phase 1 | (a) Kéo FR-SEC-006/007 vào Phase 1. (b) Hạ các thao tác M1 C3 xuống C2 | **(a).** Hạ hạng làm yếu bảo vệ cho cấu hình lưới và OTA | SEC + PO · G0 | CF-28 |
| D-04 | Edge runtime (ADR-07) | (a) OpenEMS Edge. (b) Runtime Java tự xây. (c) Lai: OpenEMS cho driver, lõi an toàn tự xây | **Hợp đồng trước; quyết sau PoC-03 + Q-15.** Mặc định dự phòng (b). Nếu giấy phép cho phép, (a)/(c) có thể rút ngắn đường găng edge | ARC + EDGE · G0 | 06 ADR-07, R-11 |
| D-05 | Lưu trữ chuỗi thời gian (ADR-06) | (a) TimescaleDB TSL tự host. (b) PostgreSQL thuần + partition. (c) Dịch vụ cloud của Timescale (ngoài VN, cần Q-08) | **(a) nếu Q-14 cho phép và PoC-01 đạt**; nếu không, (b) và tách logic tổng hợp khỏi tính năng riêng của TimescaleDB | ARC · G0 | K #25, R-06-01 |
| D-06 | Lưu tổng hợp 5 phút | (a) Mọi chuỗi 5 năm (K #31). (b) Sau 13 tháng chỉ giữ `LONG_5M` | **(a) trong MVP** (≤ 200 site, chi phí nhỏ); xem lại ở 1.000 site. Đổi sang (b) cần K/PO sửa quyết định #31 | PO · G1 | Q-40, MQ-04 |
| D-07 | Slave IEC 104 trên edge | (a) Làm trong Phase 2 vô điều kiện. (b) Chỉ khi có trigger: khách trung áp bán dư hoặc PC yêu cầu | **(b).** Trong lúc chờ dùng slave 104 của logger/gateway; trigger được theo dõi ở mỗi cổng | PO · G1 | K R-10, A-03 |
| D-08 | Ticket/work order trong nền tảng hay tích hợp CMMS | (a) Tự xây đủ. (b) Ticket tối thiểu + tích hợp CMMS. (c) Ticket tối thiểu (Phase 1), work order/SLA/PM (Phase 2), CMMS hai chiều (Phase 3) | **(c),** xác nhận bằng phỏng vấn Q-18 | PO · G0 | GAP-01, 04 WF-10 |
| D-09 | Kênh Zalo | (a) Phase 2. (b) Phase 3 | **(a) nếu Q-18 xác nhận người dùng VN nhận cảnh báo qua Zalo**; nếu không, giữ e-mail + in-app | PO · G1 | GAP-06 |
| D-10 | Tiêu chí chọn site pilot | — | Phase 1: ≥ 2 site (một site PV zero-export có Huawei SmartLogger; một site đa hãng có công tơ PCC Modbus/SunSpec) + 1 site chỉ giám sát qua Huawei Northbound. Phase 2: 1 site PV + BESS có tủ cung cấp map, có công tắc LOCAL/REMOTE, chủ tài sản đồng ý, có trực ca | PO + BIZ · G0 | A-10, R-45 |
| D-11 | Mô hình gói và giá | (a) Theo site. (b) Theo kWp/MWh. (c) Hai gói: Monitoring (theo site + bậc kWp) và Control (theo site có BESS hoặc theo MWh BESS) + dịch vụ "giám sát hộ" cho installer | **(c) làm giả thuyết**, kiểm bằng phỏng vấn và báo giá pilot; engine tính phí không trước Phase 4 (FR-ORG-011: tính phí không thuộc MVP) | PO · G1 | 02 §10, Q-19 |
| D-12 | Edge thiếu TPM/secure element | (a) Cấm mọi nơi. (b) Cho phép như ngoại lệ có thời hạn (10 D-10-13). (c) Cho phép ở site chỉ giám sát và Gate M1 có ghi rủi ro; cấm ở Gate M2 | **(c)** | SEC · G1 | CF-38, R-33 |
| D-13 | Solver tầng 3 (ADR-11) | (a) OR-Tools Java sau `SolverPort`. (b) Python sidecar | **(a) trước**; (b) chỉ khi PoC-05 không đạt NFR | ARC + OPT · trước Phase 3A | K R-22 |
| D-14 | Thời điểm EV | (a) Phase 2. (b) Phase 3 có trigger | **(b):** trigger = khách pilot có trụ sạc làm vượt trần nhập/MBA. F-EV-01 (đo EV qua công tơ) vẫn ở Phase 1 | PO · G2 | K #2, 08 §16.1 |
| D-15 | Ngân sách xuất 50% | (a) Phase 2. (b) Phase 3 có trigger | **(b):** trigger = Q-04 đóng **và** có khách bán dư | PO · G2 | A-03 |
| D-16 | Peak shaving theo demand | (a) Phase 2. (b) Phase 3 có trigger | **(b):** trigger = Q-03 đóng **và** có khách đang trả phí công suất | PO · G2 | K R-16, R-17 |
| D-17 | Nhà cung cấp hosting tại VN | — | Chốt sau Q-08 và Q-44; yêu cầu tối thiểu: KMS hoặc HSM, object storage có object lock, hai vùng (P1) | ARC + SEC · G0 | ADR-18 |
| D-18 | Mô hình trực ca 24/7 cho site M2 | (a) Installer/O&M trực, nền tảng hỗ trợ cấp 2. (b) Nền tảng trực toàn bộ | **(a)** với runbook, cảnh báo nền tảng và kill switch; xác nhận bằng Q-24 | PO · G2 | NFR-OBS-008 |
| D-19 | Cam kết "không kill thương mại" trong hợp đồng: khi hết hợp đồng, edge chạy chế độ mặc định cục bộ | (a) Có. (b) Không | **(a)** | PO + LEGAL · G1 | I AC-07, 04 BR-SEC-08 |
| D-20 | Connector Huawei Northbound trong Phase 1 (F-MON-02) | (a) Giữ. (b) Lùi sang Phase 2 | **(a)** nếu trong ngân sách **và** U-29 (tài khoản + consent) có trước giữa Phase 1; là mục **đầu tiên** của danh sách cắt nếu Phase 1 trễ hoặc U-29 chưa có ([11 §11.4](11-mvp-and-roadmap.html#s11)) | PO · G1 | 04 FR-MON-003; Q-33 (a), U-29 |
| D-21 | Vai trò `TECHNICIAN` và `PLATFORM_ADMIN` | (a) Thêm vào F-ORG-08 trong Phase 1. (b) Dùng OPERATOR cho kỹ thuật viên | **(a):** ticket MVP cần người xử lý không có quyền lệnh | PO · G0 | `_catalog-gaps`, 04 §3.2 |

---

## 6. Sổ rủi ro (R-NN)

Nhóm: KT = kỹ thuật · TM = thương mại · PL = pháp lý/quy định · AT = an toàn vận hành/bảo mật · DL = dữ liệu. Mọi đánh giá khả năng/tác động là `[INFERENCE]` của nhóm viết, không phải số đo.

### 6.1 Pháp lý và quy định

| Mã | Nhóm | Rủi ro | Khả năng | Tác động | Giảm thiểu | Owner | Phase | Mã tạm gốc |
|---|---|---|---|---|---|---|---|---|
| R-01 | PL | Lịch TOU QĐ 963 sai ngày áp → xả sai giờ, hóa đơn bóng sai | TB | Cao | Hai lịch song song (pháp lý/hóa đơn, F-TAR-03); cảnh báo khi hai lịch khác nhau; đối soát hóa đơn (Phase 2); Q-01 | OPT + LEGAL | 1 | R-08-02, GAP-04 |
| R-02 | PL | Cơ sở giá hai thành phần khác giả định; một lần thất bại peak shaving mất lợi ích cả kỳ | TB | TB | `demand_basis` tắt mặc định; peak shaving demand chỉ ở Phase 3 có trigger; cảnh báo sớm; fallback capacity control native | OPT | 3 | K R-16, R-08-08, GAP-03 |
| R-03 | PL | Điện lực không chấp nhận vòng phần mềm làm thiết bị chống phát ngược, hoặc yêu cầu thiết bị chứng nhận | TB | Cao | Native trước (`control_owner = NATIVE`); đọc rơ-le chống phát ngược (F-GRID-13); không quảng cáo edge là "thiết bị chống phát ngược"; Q-05 | INT + LEGAL | 1 | Q-A09, GAP-12 |
| R-04 | PL | Quy định thay đổi nhanh (NĐ 135 → 58 → 133 → 243, QĐ 963 trong 18 tháng) làm tham số mặc định lỗi thời | Cao | TB | Biểu giá và tham số pháp lý là dữ liệu có phiên bản, không hard-code (K #24); rà soát pháp lý mỗi cổng | PO + LEGAL | 0–4 | 02 §3.5 |
| R-05 | PL | Khung pháp lý dữ liệu/an ninh mạng VN chưa kiểm chứng → hosting, retention, thông báo vi phạm sai | Cao | TB | Hosting VN mặc định; không gắn số tháng pháp định vào NFR trước Q-08; DPIA ở Phase 2 | SEC + LEGAL | 0 | I-R-06 |
| R-06 | PL | Yêu cầu điều độ IEC 104 chưa rõ → không nhận được site trung áp bán dư | TB | TB | P1 có điều kiện (D-07); dùng slave 104 của logger/gateway trong lúc chờ | INT | 2 | R-E-06 |
| R-07 | PL/AT | Vi phạm giới hạn xuất do lỗi hệ thống của ta khiến khách bị phạt (NĐ 133 có mức tới 100 triệu đ) | Thấp | Cao | Native trước; test F-INT-27 khi commissioning; bằng chứng tuân thủ F-REP-13; cảnh báo tuân thủ lưới; điều khoản trách nhiệm trong hợp đồng | INT + PO | 1 | 02 §3.3 |

### 6.2 Giấy phép và kỹ thuật

| Mã | Nhóm | Rủi ro | Khả năng | Tác động | Giảm thiểu | Owner | Phase | Mã tạm gốc |
|---|---|---|---|---|---|---|---|---|
| R-08 | PL/KT | TSL không cho phép mô hình SaaS của ta | TB | Cao | D-05 phương án (b); tách logic tổng hợp; quyết trong Phase 0 | ARC | 0 | R-06-01 |
| R-09 | PL/KT | Giấy phép OpenEMS hoặc thư viện giao thức buộc công bố mã edge | TB | TB | Hợp đồng §7–§8 của 07 độc lập runtime; mặc định tự xây | EDGE | 0 | R-06-02, R-E-08 |
| R-10 | PL/KT | Giấy phép solver phát hiện muộn | Thấp | TB | `SolverPort`; Q-17 trước Phase 3A | OPT | 3 | R-08-07 |
| R-11 | KT | Edge là đường găng: runtime không đạt chu kỳ p99 ≤ 200 ms trên phần cứng rẻ, hoặc 1–2 kỹ sư edge không đủ năng lực | Cao | Cao | PoC-03 sớm; native trước để giảm logic edge ở Phase 1; thêm kỹ sư edge (11 §11); SKU phần cứng lớn hơn | EDGE + DL | 0–2 | R-06-07 |
| R-12 | KT | Register map không công bố hoặc đổi theo firmware → dữ liệu sai dấu/scale | Cao | Cao | Driver theo dải firmware; fingerprint; xác minh map khi commissioning (FR-INT-020); phép thử dấu; hợp đồng cung cấp map; thanh ghi từ diễn đàn không vào `VERIFIED_*` | INT | 1–2 | R-E-01, RB-3 |
| R-13 | KT | Lệnh ghi "không tác dụng" hoặc bị native âm thầm đè | TB | Cao | Readback bắt buộc; `FAILED_NO_EFFECT`; `tracking_state`; phát hiện điều khiển ngoài (F-ALM-22, Phase 2) | INT | 1–2 | R-E-02 |
| R-14 | KT | Hai vòng điều khiển (native + edge) dao động | Thấp | Cao | `control_owner`; từ chối cấu hình hai chủ; Q-30 | OPT | 1–2 | R-08-03 |
| R-15 | KT | Mòn NVM do ghi setpoint chu kỳ | TB | TB | Cờ `persist` trong driver; `min_write_interval_ms`; chỉ ghi khi đổi; Q-31 | INT | 2 | R-E-04 |
| R-54 | KT/TM | Gate M1: lịch native lặp vô hạn trên thiết bị khi edge chết, nên nạp lưới/xả theo khung TOU cũ sau khi biểu giá đổi (rủi ro kinh tế/hợp đồng; bảo vệ thiết bị vẫn do BMS/PCS) | Thấp | TB | Chỉ ghi khi đổi (≤ 4 lần/ngày); `native_default_profile` khi hết hạn/đổi biểu giá/kill switch; validator V-N1…V-N4; cảnh báo `EDGE_OFFLINE_NATIVE_SCHEDULE_ACTIVE` sau 1 h, Khẩn cấp nếu biểu giá mới hiệu lực khi edge còn offline ([08 §6.6](08-energy-optimization.md)); liên quan R-15, Q-31 | OPT + INT | 1 | R-08-10 |
| R-16 | KT | Xung đột Modbus master với SCADA/công cụ installer | TB | TB | Edge là connection owner; Modbus TCP server xuất lại (Phase 3); chế độ MAINTENANCE | INT | 1 | R-E-07 |
| R-17 | TM/KT | Hãng siết hoặc đổi chính sách cloud API (ví dụ Huawei đòi owner consent) | TB | TB | Edge Modbus cục bộ là đường chính; cảnh báo `AUTH_FAILED`; runbook cấp lại quyền | INT | 1 | R-E-05, RB-2 |
| R-18 | KT/DL | RLS chậm hoặc không áp được trên CAGG | TB | Cao | PoC-04; hàm truy cập SECURITY DEFINER; cell theo tenant ở quy mô lớn | ARC | 0 | R-06-06, MQ-01 |
| R-19 | KT | Không có Kafka làm bão backfill dồn vào DB | Thấp | TB | Giới hạn tốc độ backfill tại edge; backpressure; ngưỡng chuyển ADR-05 | ARC | 1 | R-06-03 |
| R-20 | KT | Ranh giới module/mặt phẳng trong monolith bị xói mòn | TB | TB | Test kiến trúc chặn build (06 §16) | ARC | 1 | R-06-04 |
| R-21 | KT/AT | Không có KMS/HSM managed tại VN | TB | Cao | HSM thiết bị; không bật Gate M2 khi chưa có lưu khóa ký đạt yêu cầu | SEC | 0–2 | R-06-05 |
| R-22 | KT | Dự báo PV/tải sai → nạp lưới thừa hoặc thiếu năng lượng cao điểm | TB | TB | Hệ số `α`, space reserve, lần sinh lịch 16:30; Phase 3 P10/P50 | OPT | 1–3 | R-08-01 |
| R-23 | KT | Kế hoạch MPC "lật" liên tục làm mất lòng tin | TB | TB | `λ_stab`, cửa sổ đóng băng, giới hạn số lần sinh | OPT | 3 | R-08-04 |
| R-24 | KT | Thiếu lịch sử để backtest làm tầng 3 không bao giờ bật ở site mới | Cao | Thấp | Nhập CSV lịch sử (F-INT-22, Phase 2); giữ tầng 2 | OPT | 3 | R-08-09, GAP-14 |
| R-48 | KT/AT | Mô phỏng cho kết quả "xanh giả": virtual site sinh từ cùng register map mà driver dùng nên lỗi map (dấu, scale, thứ tự word) không bao giờ lộ; driver qua CI nhưng sai ở thiết bị thật | Cao | Cao | Vector vàng thu từ thiết bị thật; chế độ "map lệch" trong simulator; HIL và test lab bắt buộc trước khi gắn `VERIFIED_*` (không có driver `VERIFIED_*` chỉ dựa mô phỏng); phép thử dấu khi commissioning (FR-INT-016) | INT + EDGE | 1–2 | R-15-01 |
| R-49 | TM/PL | Chi phí license broker MQTT chưa có trong kế hoạch MVP; broker "mở" có thể đổi giấy phép (tiền lệ EMQX 5.9 sang BSL 1.1); dịch vụ IoT managed có thể bị khai tử (Google Cloud IoT Core 2023) | Cao | TB | Hợp đồng MQTT không phụ thuộc broker (07 §7); T-E2-04 chạy trên ≥ 2 broker; xin báo giá ở Phase 0 và dự trù ngân sách; phương án RabbitMQ 4.x mở; không dùng managed IoT ở MVP; Q-16, Q-59 | ARC + PO | 0 | R-15-02, R-15-03, R-15-04 |
| R-50 | PL/KT | Thư viện GPL/copyleft (lib60870, j60870, libIEC61850, c104, SteVe) lọt vào image edge hoặc bản phân phối đóng → nghĩa vụ công bố mã | TB | Cao | SBOM + kiểm giấy phép tự động trong CI chặn build; danh sách giấy phép cho phép do LEGAL duyệt; mua license thương mại nếu nhúng thư viện giao thức; công cụ test dùng GPL chỉ ở môi trường test, không đóng gói; liên quan Q-15, R-09, R-28 | EDGE + LEGAL | 0–1 | R-15-05 |
| R-51 | KT | Keepalive/NAT timeout của mạng 4G VN làm rớt kết nối MQTT liên tục hoặc tốn dữ liệu | TB | TB | Keepalive 30–60 s, Session Expiry hữu hạn, Will Delay; đo ở pilot (Q-45); buffer edge 7–30 ngày che gián đoạn | EDGE | 1 | R-15-08 |

### 6.3 An toàn vận hành và bảo mật

| Mã | Nhóm | Rủi ro | Khả năng | Tác động | Giảm thiểu | Owner | Phase | Mã tạm gốc |
|---|---|---|---|---|---|---|---|---|
| R-25 | AT | Thiết bị phổ biến không có watchdog/reversion → setpoint treo khi edge chết | Cao | Cao | `requires_native_fallback`; chỉ đổi chế độ native; test F-INT-28 cho từng model | SEC + INT | 2 | R-E-03, I-R-02 |
| R-26 | AT | Lệnh hàng loạt do tài khoản hoặc khóa bị chiếm | Thấp | Rất cao | Fleet Governor, kill switch, C3 hai người, WebAuthn, SOE kẹp tại edge | SEC | 2 | I-R-01 |
| R-27 | AT | Lộ khóa ký lệnh | Thấp | Rất cao | KMS không xuất khóa; khóa lệnh ≠ khóa cấu hình; quy trình xoay khóa | SEC | 1–2 | I-R-05 |
| R-28 | AT | Tấn công chuỗi cung ứng edge (firmware, thư viện) | Thấp | Rất cao | SBOM, ký build, OTA A/B có canary và anti-rollback | SEC + EDGE | 1 | I-R-07 |
| R-29 | AT | Đồng hồ edge sai làm hỏng kiểm hạn lệnh | TB | Cao | `clock_state`; interlock IL-06 chặn lệnh khi UNSYNCED | EDGE | 1–2 | I-R-08 |
| R-30 | AT | Kênh cloud riêng của dongle/logger hãng vẫn chạy song song → điều khiển ngoài, lộ dữ liệu | TB | Cao | Chính sách giữ/chặn kênh cloud hãng do chủ site chọn (F-SEC-17); phát hiện điều khiển ngoài | SEC + INT | 2 | I-R-03, R-E-09 |
| R-31 | AT/DL | Lỗi đơn vị hoặc dấu (W vs kW, nhập vs xuất) trong envelope/KPI | Thấp | Cao | Hậu tố đơn vị; validator V-12; phép thử dấu; golden snapshot | DATA + OPT | 1 | R-08-06 |
| R-32 | AT | Chưa có trực ca 24/7 khi bật site M2 đầu tiên | TB | Cao | NFR-OBS-008 là điều kiện G2; D-18 | PO + SEC | 2 | I-R-11 |
| R-33 | AT | Edge MVP không có TPM → khóa thiết bị lưu bằng phần mềm | TB | TB | D-12 (cấm ở M2); thay phần cứng trước Phase 2 | SEC + EDGE | 1–2 | I-R-09 |
| R-34 | AT | Operator hiểu nhầm trạng thái lệnh ("đã gửi" = "đã áp dụng"), nhầm site khi phát lệnh, hoặc hiểu site OFFLINE là "mất điều khiển" | TB | Cao | Không cập nhật lạc quan; tên site trong hộp lệnh và gõ mã site ở C3; banner "site vẫn điều khiển cục bộ theo kế hoạch #n" | UX | 1–2 | R-09-03, R-09-04, R-09-05 |
| R-35 | DL/AT | Rò dữ liệu cross-tenant do RLS/pool cấu hình sai | TB | Cao | Lớp lọc ứng dụng thứ hai; test cross-tenant trong CI chặn build | ARC + SEC | 1 | I-R-04 |
| R-52 | AT/DL | Tenant demo/mô phỏng bị nhầm là dữ liệu thật, hoặc lệnh từ tenant demo chạm tới edge thật | Thấp | Cao | Nhãn "mô phỏng" bắt buộc trên mọi màn hình và báo cáo của tenant demo; cô lập mạng; test T-E2-06 chứng minh không có route tới edge thật | SEC + ARC | 1 | R-15-06 |

### 6.4 Dữ liệu và báo cáo

| Mã | Nhóm | Rủi ro | Khả năng | Tác động | Giảm thiểu | Owner | Phase | Mã tạm gốc |
|---|---|---|---|---|---|---|---|---|
| R-36 | DL | Chi phí lưu trữ tăng mạnh (5 phút 5 năm mọi chuỗi, kế hoạch MPC WORM) | TB | TB | D-06 xem lại ở 1.000 site; MQ-03 content-addressed snapshot | DATA | 1, 3 | MQ-03, MQ-04 |
| R-37 | DL/TM | Restatement báo cáo đã dùng cho thanh toán ESCO/PPA | TB | Cao | Snapshot bất biến (F-REP-10); ngưỡng restatement > 0,5% kWh; thông báo phiên bản mới | DATA | 1 | X-05-08 |
| R-38 | TM/PL | Người dùng tin số ước tính như số đo; tiết kiệm bị hiểu thành cam kết | TB | Cao | Nhãn "≈ ước tính"; trang phương pháp; "giới hạn trung thực" in trên báo cáo (08 §15.6); không quảng cáo % | PO + UX | 1 | R-08-05, R-09-02 |
| R-39 | DL | KPI của site chỉ giám sát (cloud 5 phút) sai do netting và mất đỉnh ngắn | Cao | TB | Quality `UNCERTAIN_VENDOR_CLOUD`; không chạy peak shaving trên dữ liệu 5 phút; Q-42 | DATA | 1 | MQ-12, 08 §14.5 |

### 6.5 Thương mại và giao hàng

| Mã | Nhóm | Rủi ro | Khả năng | Tác động | Giảm thiểu | Owner | Phase | Mã tạm gốc |
|---|---|---|---|---|---|---|---|---|
| R-40 | TM | OEM (Huawei SmartEMO đã có demand charge theo TOU và phân tích doanh thu từ 03/2026; SolarEdge ONE) mở rộng, cho dashboard miễn phí, làm hẹp khoảng trống | Cao | Cao | Tập trung vào thứ OEM khó làm: đa hãng, bằng chứng tuân thủ, O&M đa hãng, hóa đơn bóng độc lập | PO | 1–3 | RB-1 |
| R-41 | TM | Thứ tự driver MVP sai so với thị phần thực | TB | Cao | Q-20 trước khi mua lab; kiến trúc driver khai báo cho phép thêm nhanh | INT + BIZ | 0 | RB-4, R-E-10 |
| R-42 | TM | Giả định người mua/persona sai do chưa phỏng vấn khách | TB | Cao | Phỏng vấn ở Phase 0; kiểm thử khả dụng với 5 operator trước khi build UI chính | PO + UX | 0 | GAP-15, R-09-06 |
| R-43 | TM/KT | Phạm vi MVP (148 FR P0) quá lớn cho đội 6–10 kỹ sư; bộ an toàn P0 làm chậm Gate M2 | Cao | Cao | Tách Phase 1/Phase 2 (D-01); milestone nội bộ 1a/1b/1c; danh sách cắt ([11 §11.4](11-mvp-and-roadmap.html#s11)); không cắt an toàn | DL | 1–2 | Q-D-07, I-R-10 |
| R-44 | TM | Mệt mỏi cảnh báo làm operator bỏ qua cảnh báo Cao | TB | TB | Chặn theo cha–con ở Phase 1; đo số cảnh báo/operator/giờ; gom lũ (F-ALM-07) ở Phase 2 | UX | 1–2 | R-09-01 |
| R-45 | TM | Không có pilot BESS có tủ cung cấp map theo hợp đồng → G2 không chứng minh được | TB | Cao | Tìm pilot từ Phase 0 (D-10); NDA với nhà phân phối; dùng PCS/tủ nhỏ ở lab | BIZ + INT | 0–2 | Q-E-09 |
| R-46 | TM | Mô hình giá không bền khi OEM cho phần mềm miễn phí | TB | TB | Hai gói tách theo mặt phẳng; dịch vụ giám sát hộ cho installer; Q-19 | PO | 1 | K G-04 |
| R-47 | TM | Định vị dựa trên bằng chứng đối thủ chỉ qua snippet → so sánh sai | TB | TB | Không đưa so sánh đối thủ ra ngoài trước lượt kiểm chứng; ghi "không có tài liệu ≠ không hỗ trợ" | PO | 0 | U-02…U-08 |
| R-53 | TM/PL | Không URL nào được reviewer spot-check (K vòng 1 và vòng rà soát cuối đều hết hạn mức WebSearch); một FACT sai lọt vào tài liệu phát hành ra ngoài (so sánh đối thủ, pháp lý) | TB | Cao | Không phát hành 02 và phần đối thủ của 00 ra ngoài trước V-14 ([14 §7](14-source-register.md)); lượt kiểm chứng có mạng theo [01 §9.1](01-research-methodology.md); trần độ tin cậy snippet | PO + Registrar | 0 | V-14 |

---

## 7. Tích hợp không khả dụng và mục chưa kiểm chứng (U-NN)

### 7.1 Giới hạn của chính nghiên cứu

| Mã | Mục | Tình trạng | Hệ quả |
|---|---|---|---|
| U-01 | Trang hạt giống InfinitePower (`https://www.infinitepowerht.com/what-is-energy-management-system-ems-and-its-functions.html`) | Không mở được; một agent thấy qua snippet, một agent không thấy (K R-18) | Chỉ dùng cho định nghĩa chung khi có nguồn thứ hai; không gán tính năng |
| U-02 | Ampowr Cosmos (`https://ampowr.com/energy-management-system-ems/`): giao thức, Partner API, phân quyền, phương pháp dự báo | Chỉ trang sản phẩm/case study qua snippet; nguồn rfp.wiki bị bác (nội dung AI sinh) | Không gán tính năng ngoài các URL ampowr.com đã ghi |
| U-03 | HT Infinite Power: bảng thanh ghi, tên cloud, API, chứng chỉ | Chưa có | Tủ BESS kiểu này ở chế độ chỉ đọc tới khi có driver kiểm chứng |
| U-04 | Schneider EMA: chu kỳ kế hoạch thực tế (15 phút/48–72 h mâu thuẫn, nguồn ~2017), phạm vi IEC 62443 cloud | FACT Low–Med | Số của ta là PROPOSAL độc lập |
| U-05 | Siemens SICAM MGC: số chứng chỉ IEC 62443 và hạn; edition IEC 62898-2 | Chưa có | Không trích chứng chỉ |
| U-06 | SolarEdge ONE Controller: điều khiển pin bên thứ ba, hành vi khi mất Internet | Chưa có | — |
| U-07 | Độ trễ end-to-end cloud → thiết bị: không hãng nào công bố | Không tồn tại nguồn | Tự đo trong PoC/pilot (NFR-PERF-005) |
| U-08 | Victron VRM, Deye/Solarman, Growatt, Solis C&I chưa được đánh giá | Chưa nghiên cứu | Q-20 |
| U-09 | Không có phỏng vấn khách thật nào | Mọi persona/JTBD là nghiên cứu tại bàn (K G-07) | Q-18, R-42 |
| U-10 | Không có lượt tìm kiếm kiểm chứng của K; mọi FACT mới chỉ qua snippet | Hạn mức đã hết | Tin cậy tối đa "Trung bình"; lượt kiểm chứng riêng trước phát hành |

### 7.2 Tích hợp chưa khả dụng cho đội

| Mã | Tích hợp | Vì sao chưa có | Cần gì | Phase cần |
|---|---|---|---|---|
| U-11 | Huawei OAuth Connect control API (ghi qua cloud) | Cần tài khoản installer và quyền; chính sách owner consent | Q-33 | 4 |
| U-12 | SMA GridControl API | Không rõ ai được cấp | Q-33 | 4 |
| U-13 | API cloud Growatt/Deye/Solis | Chưa có tài khoản developer, chưa rõ hạn mức | Q-33 | 3 |
| U-14 | Dữ liệu công tơ EVN (DLMS/IEC 62056, load profile) | Chưa rõ quyền truy cập | Q-32 | 2 |
| U-15 | Hóa đơn EVN thật (TOU QĐ 963, hai thành phần) | Chưa có khách pilot | A-12, Q-01, Q-03 | 0–1 |
| U-16 | Kênh điều độ IEC 104 với PC | Chưa có bảng điểm, chưa có dự án | Q-06 | 2 (điều kiện) |
| U-17 | Dịch vụ dự báo thương mại (Solcast, Meteomatics…) | Chưa có điều khoản/giá | Q-50 | 3 |
| U-18 | Zalo OA/ZNS | Chưa nghiên cứu điều kiện API, chi phí, mẫu tin | GAP-06, D-09 | 2 |
| U-19 | KMS/HSM và object lock tại nhà cung cấp VN | Chưa khảo sát | Q-44 | 0–2 |
| U-20 | Chương trình DR/VPP tại VN | Chưa thấy cơ chế trả tiền | Q-13 | 4 |
| U-29 | Huawei Northbound **đọc** (OAuth Connect) cho connector F-MON-02 | Chưa có tài khoản installer/developer; chưa có văn bản đồng ý của chủ site (owner consent); hạn mức gọi và hạn token chưa đo | Tài khoản qua pilot (c) của [11](11-mvp-and-roadmap.html); consent theo mẫu (Q-23); đo hạn mức trong lab; Q-33 (a). Liên quan D-20 (là mục đầu tiên của danh sách cắt nếu không có), A-04, R-17 | **1 — chặn G1** (cho F-MON-02) |
| U-30 | Bảng register **ghi** chính thức của Huawei SmartLogger/EMMA (giới hạn xuất, TOU, chế độ pin) kèm thanh ghi readback | Chỉ có tài liệu hãng qua snippet (02 L37, L38) và thanh ghi diễn đàn (U-21, không được dùng); chưa có tài liệu Modbus bản hiện hành theo firmware, chưa thử ở lab | Tài liệu Modbus chính thức theo dải firmware (kênh đối tác/pilot (a)); thử ghi + readback + watchdog ở lab (Q-27, Q-30). Kiểm A-04; liên quan D-20, R-12, R-13 | **1 (lab) — chặn G1** (giá trị số 1 tại Gate M1: cấu hình native có readback) |

### 7.3 Nội dung chưa kiểm chứng đang dùng làm căn cứ

| Mã | Nội dung | Mức hiện tại | Không được dùng để |
|---|---|---|---|
| U-21 | Thanh ghi Modbus từ diễn đàn (Huawei 47086…, 40000/43006; Sungrow 13049–13051; Victron 2700) | FACT Low "cộng đồng báo cáo" | Đưa vào driver `VERIFIED_*` |
| U-22 | QĐ 1570 "≥ 64 kbps, ≤ 125 ms" (tóm tắt Advantech, vendor có lợi ích) | FACT Low | Làm NFR |
| U-23 | Số Huawei ≤ 2 s/≤ 5 s | Hãng tự công bố | Tuyên bố hiệu năng của ta |
| U-24 | IEC 61724-1:2021, IEC 62443, ISA-101/18.2, EEMUA 191, IEC 60617, IPMVP, ASHRAE 14, UL 9540A, WCAG edition | Kiến thức nền, chưa đối chiếu văn bản | Tuyên bố tuân thủ (chỉ "theo tinh thần") |
| U-25 | OCPP 1.6J Security Whitepaper Ed.4 (02/2026) | Chỉ qua snippet | Thay đổi yêu cầu profile trước khi đọc |
| U-26 | Khung pháp lý an ninh mạng/dữ liệu VN | Kiến thức nền | Số tháng lưu trữ trong NFR |
| U-27 | "Modbus/IEC 104 tại site không có xác thực" | INFERENCE (kiến thức nền giao thức) | Trích như FACT |
| U-28 | Giá BESS VN, cycle life, `c_deg` | Không có nguồn | Tài liệu bán hàng; kết luận "BESS 4–5 h hấp dẫn hơn" |

---

## 8. Điều kiện chặn phát hành tài liệu và cổng phase

**Trước khi phát hành 00/02/04/10 ra ngoài đội** (K §5 G-13): đóng hoặc ghi rõ trạng thái Q-01, Q-03, Q-04, Q-05, Q-06, Q-08, Q-14, Q-15. Tài liệu 06 thêm Q-16, Q-44 và kết quả PoC-01/02/04 ([06 §21.4](06-system-architecture.html)).

**Theo cổng của [11](11-mvp-and-roadmap.html):**

| Cổng | Câu hỏi phải đóng | Quyết định phải chốt | Rủi ro phải có kế hoạch giảm thiểu đã chạy | Xung đột / tích hợp phải đóng |
|---|---|---|---|---|
| G0 (ra Phase 0) | Q-08, Q-14, Q-15, Q-16, Q-18, Q-20, Q-36, Q-38, Q-39, Q-43, Q-44, Q-59 | D-01, D-02, D-03, D-04, D-05, D-08, D-10, D-17, D-21 | R-05, R-08, R-09, R-11, R-18, R-41, R-42, R-49, R-50, R-53 | — |
| G1 (Gate M1, phát hành Monitoring MVP) | Q-01 (hoặc chạy hai lịch), Q-05, Q-07, Q-22, Q-23 (M1), Q-30, Q-33 (a), Q-35, Q-37, Q-41, Q-42, Q-45, Q-49, Q-55, Q-57 | D-06, D-07, D-09, D-11, D-12, D-19, D-20 | R-01, R-03, R-07, R-12, R-31, R-35, R-37, R-38, R-43, R-48, R-51, R-52, R-54 | CF-28, CF-40 (`COMMISSIONING_TEST`); U-29 (Huawei Northbound đọc, hoặc cắt F-MON-02 theo D-20); U-30 (map ghi SmartLogger/EMMA có readback, kiểm A-04) |
| G2 (site Gate M2 đầu tiên) | Q-10 (ramp), Q-21, Q-24, Q-26, Q-27, Q-28, Q-31, Q-46, Q-47, Q-52 | D-14, D-15, D-16, D-18 | R-13, R-21, R-25, R-26, R-29, R-30, R-32, R-33, R-34, R-45, R-48 (HIL) | CF-39 (nếu bật ghi EV qua API CPO); phần còn lại của GAP-12-03 (CF-40) |
| G3 (theo track) | 3A: Q-17, Q-50, Q-51 · 3C: Q-03 · 3D: Q-04 · 3E: Q-34 | D-13 | R-02, R-10, R-22, R-23, R-24 | 3E: CF-39 (FR-EV-004) |
| G4 (theo track) | 4A: Q-13 · 4F: Q-48 · 4D: Q-33 (c) | — | R-40, R-46 | 4D: CF-39 (FR-INT-028 phải được 04 sửa hoặc bỏ) |

---

## 9. Bảng tra mã tạm → mã chính thức

Dành cho [12 Truy vết](12-traceability-matrix.md). Mã tạm không có ở đây đã được 04/06 hấp thụ (ví dụ FR-OPT tạm của G ở 04 §7.2) hoặc đã đóng.

| Mã tạm | Mã 13 |
|---|---|
| Q-A01 | Q-01 |
| Q-A02, Q-A03 | Q-04 |
| Q-A04 | Q-03 |
| Q-A05 | Q-21 |
| Q-A06 | Q-13 |
| Q-A07, Q-A08 | Q-11 |
| Q-A09 | Q-05 |
| Q-A10 | Q-19 |
| Q-B1 | U-01 |
| Q-B2, Q-B3, Q-B4, Q-B5, Q-B7 | U-02, U-03, U-04, U-05, U-06 |
| Q-B8 | Q-29 |
| Q-B9 | Q-15 |
| Q-B10 | U-07 |
| Q-B11 | Q-19 |
| Q-B12 | Q-20, U-08 |
| Q-C01 | Q-03 |
| Q-C02 | Q-32 |
| Q-C03 | Q-12 |
| Q-C04 | Q-04 |
| Q-C05, Q-C06 | Q-10 |
| Q-C07 | Q-05 |
| Q-C08 | Q-21 |
| Q-C09 | Q-21 (aux BESS, cùng khảo sát) |
| Q-C10 | Q-48 (tiêu chuẩn), U-24 |
| Q-C11 | Q-28 |
| Q-D-01 | Q-46 |
| Q-D-02, Q-D-03 | Q-07 |
| Q-D-04 | Q-18 |
| Q-D-05, Q-D-08 | Q-23 |
| Q-D-06 | Q-49 |
| Q-D-07 | Q-43, R-43 |
| Q-E-01 | Q-06 |
| Q-E-02 | Q-05 |
| Q-E-03 | Q-29 |
| Q-E-04, Q-E-06 | Q-27 |
| Q-E-05 | Q-31 |
| Q-E-07 | Q-35 |
| Q-E-08, Q-E-17 | Q-34 |
| Q-E-09 | Q-28 |
| Q-E-10, Q-E-11, Q-E-14 | Q-33 |
| Q-E-12 | Q-15 |
| Q-E-13 | Q-37 |
| Q-E-15 | Q-36 |
| Q-E-16 | Q-20 |
| Q-F01 | Q-14 |
| Q-F02, Q-F04 | Q-37 |
| Q-F03, Q-F12 | Q-39 |
| Q-F05, Q-F06, Q-F11 | Q-50 |
| Q-F07, Q-F08 | Q-53 |
| Q-F09 | Q-08 |
| Q-F10 | Q-32 |
| Q-G01 | Q-54 |
| Q-G02 | Q-27 |
| Q-G03 | Q-30 |
| Q-G04 | Q-17 |
| Q-G05 | Q-51 |
| Q-G06 | Q-03 |
| Q-G07 | Q-01 |
| Q-G08 | Q-13 |
| Q-G09 | Q-04 |
| Q-G10 | Q-21 |
| Q-G11 | Q-34 |
| Q-G12 | Q-53 |
| Q-H01 | Q-58 |
| Q-H02 | Q-48 |
| Q-H04 | Q-18 |
| Q-H05, Q-H10 | Q-56 |
| Q-H06 | Q-26 |
| Q-H07 | Q-55 |
| Q-H09 | Q-12 |
| Q-I-01, Q-I-02, Q-I-06, Q-I-11 | Q-48 |
| Q-I-03 | Q-06 |
| Q-I-04 | Q-08 |
| Q-I-05 | Q-09 |
| Q-I-07 | Q-27 |
| Q-I-08 | Q-38 |
| Q-I-09 | Không cấp (sự cố Solarman/Deye: chỉ ảnh hưởng 10 §15.4, chờ tìm kiếm có nguồn) |
| Q-I-10 | Q-10 |
| Q-I-13 | Q-44 |
| Q-I-14 | Q-47 |
| Q-10-01 | Q-36 |
| Q-10-02 | Q-24 |
| Q-10-03 | Q-06 |
| Q-06-01 | Q-43 |
| Q-06-02 | Q-16 |
| Q-06-03 | Q-44 |
| Q-06-04 | Q-25 |
| Q-06-05 | Q-40 |
| Q-06-06 | Q-36 |
| Q-06-07 | Q-45 |
| Q-08-01 | Q-54 |
| Q-08-02 | Q-27 |
| Q-08-03 | Q-30 |
| Q-08-04 | Q-17 |
| Q-08-05 | Q-51 |
| Q-08-06 | Q-03 |
| Q-08-07 | Q-01 |
| Q-08-08 | Q-13 |
| Q-08-09 | Q-04 |
| Q-08-10 | Q-21 |
| Q-08-11 | Q-34 |
| Q-08-12 | Q-53 |
| Q-08-13 | Q-52 |
| Q-08-14 | Q-05 |
| Q-09-01 | Q-03 |
| Q-09-02 | Đã đóng (ADR-03) |
| Q-09-03 | Q-57 |
| Q-09-04 | Q-26 |
| MQ-01 | Q-38 |
| MQ-02 | Q-22 |
| MQ-03, MQ-04 | Q-40 |
| MQ-05 | Q-41 |
| MQ-06 | Q-03 |
| MQ-07 | Q-32 |
| MQ-08 | Q-12 |
| MQ-09 | Q-08 |
| MQ-10 | Q-02 |
| MQ-11 | Q-04 |
| MQ-12 | Q-42 |
| GAP-01, GAP-06, GAP-15 | Q-18 |
| GAP-02 | Q-27 |
| GAP-03 | Q-03 |
| GAP-04 | Q-01 |
| GAP-05 | D-02 |
| GAP-07 | Q-32 |
| GAP-08 | Xử lý ở 11 Phase 1 (liên hệ trực ca trong chi tiết cảnh báo) + Phase 2 (leo thang, work order) |
| GAP-09 | Q-19, D-11 |
| GAP-10 | CF-33 |
| GAP-11 | Q-20 |
| GAP-12 | Q-05 |
| GAP-13 | 11 §12 (chiến lược kiểm thử theo phase) |
| GAP-14 | R-24 |
| GAP-16 | §8 của 13 |
| GAP-17 | Q-36 |
| RB-1 | R-40 |
| RB-2 | R-17 |
| RB-3 | R-12 |
| RB-4 | R-41 |
| R-E-01 | R-12 |
| R-E-02 | R-13 |
| R-E-03 | R-25 |
| R-E-04 | R-15 |
| R-E-05 | R-17 |
| R-E-06 | R-06 |
| R-E-07 | R-16 |
| R-E-08 | R-09 |
| R-E-09 | R-30 |
| R-E-10 | R-41 |
| R-06-01 | R-08 |
| R-06-02 | R-09 |
| R-06-03 | R-19 |
| R-06-04 | R-20 |
| R-06-05 | R-21 |
| R-06-06 | R-18 |
| R-06-07 | R-11 |
| R-08-01 | R-22 |
| R-08-02 | R-01 |
| R-08-03 | R-14 |
| R-08-04 | R-23 |
| R-08-05 | R-38 |
| R-08-06 | R-31 |
| R-08-07 | R-10 |
| R-08-08 | R-02 |
| R-08-09 | R-24 |
| R-08-10 | R-54 |
| R-09-01 | R-44 |
| R-09-02 | R-38 |
| R-09-03, R-09-04, R-09-05 | R-34 |
| R-09-06 | R-42 |
| I-R-01 | R-26 |
| I-R-02 | R-25 |
| I-R-03 | R-30 |
| I-R-04 | R-35 |
| I-R-05 | R-27 |
| I-R-06 | R-05 |
| I-R-07 | R-28 |
| I-R-08 | R-29 |
| I-R-09 | R-33 |
| I-R-10 | R-43 |
| I-R-11 | R-32 |
| X-05-08 | R-18, R-36, R-37 |
| R-15-01 | R-48 |
| R-15-02, R-15-03, R-15-04 | R-49 |
| R-15-05 | R-50 |
| R-15-06 | R-52 |
| R-15-07 | Không cấp (rủi ro công cụ nội bộ: API simulator pymodbus; 15 tự xử lý bằng khóa phiên bản) |
| R-15-08 | R-51 |
| V-14 (14 §7) | R-53 |
| Q-E2-01, Q-E2-02, Q-E2-03 | Q-16 |
| Q-E2-04 | Q-54 (chỉ cần nếu ADR-07 chọn OpenEMS; D-04) |
| Q-E2-05 | Q-34 (công cụ EV); phần OpenLEADR theo Q-13 |
| Q-E2-06, Q-E2-08 | Không cấp (dữ liệu/giấy phép cho tenant demo và backtest; 15 tự xử lý; nếu dùng cho backtest tầng 3 thì theo R-24) |
| Q-E2-07 | Q-59 |
| Q-E2-09 | Q-45 |
| GAP-12-02 | CF-39 |
| GAP-12-03 | CF-40 |

**Lưu ý trùng chữ.** `R-01`…`R-27` trong [K](notes/K-review-round1.md) là **mã phán quyết** của K, khác với `R-NN` của sổ rủi ro này. Khi trích phán quyết, luôn ghi "K R-nn"; khi trích rủi ro, ghi "R-nn" kèm liên kết tới 13. Phán quyết K ↔ CF-NN ở [§4.1](#41-phán-quyết-của-evidence-judge-k-vòng-1).

---

## 10. Vấn đề gửi agent khác

| Gửi | Vấn đề | Đề xuất |
|---|---|---|
| 04 Yêu cầu | CF-28: FR-SEC-006/007 đang `C3·M2` nhưng thao tác M1 cần duyệt C3 | Đổi cột Hạng·Gate thành `C3·M1`; phần nâng hạng theo ngữ cảnh M2 giữ ở M2 |
| 04 Yêu cầu | CF-30: câu chữ khả dụng Command API | Ghi cả hai cửa sổ đo trong NFR-REL-004 |
| 03 Danh mục | CF-29: ánh xạ hạng phát hành → phase lộ trình ở [11 §2.3](11-mvp-and-roadmap.html#s2) | Thêm ghi chú dưới cột "Phát hành" |
| 03 Danh mục | D-21: vai trò `TECHNICIAN`, `PLATFORM_ADMIN` (đã ở `_catalog-gaps`) | Xử lý khi cập nhật catalog |
| 07 Tích hợp | CF-31 (`APPROVAL_REJECTED`) | Sửa 07 §8.4 |
| 10 An toàn | CF-32 (ACL `down/config`); CF-38/D-12 (TPM ở M2) | Cập nhật 10 §9.3, §20.4 |
| 12 Truy vết | Bảng §9; ghi chú trùng chữ K R-nn vs R-nn | Dùng bảng này cho cột "mã tạm" |
| 12 Truy vết | GAP-12-02 → CF-39, GAP-12-03 → CF-40 (v1.1). 04 (bảng gửi agent khác) đề nghị 12 đóng GAP-12-02, nhưng FR-INT-028 chưa đạt điều kiện CF-39 | Giữ GAP-12-02 mở cho FR-INT-028; dẫn CF-39/CF-40 |
| 04 Yêu cầu | CF-39: FR-INT-028 (ghi qua cloud hãng) chưa có hạn/TTL, readback, mặc định khi mất liên lạc, Governor, điều kiện edge là client | Viết lại FR-INT-028 theo 6 điều kiện của CF-39 (như FR-EV-004 bản mới), hoặc bỏ FR; NFR-SEC-018 thêm các điều kiện này |
| 07 Tích hợp | CF-39 (§8.8 ghi qua cloud hãng; đường API CPO do edge gọi cho FR-EV-004); CF-40 (§9.4 dẫn FR-INT-031/NFR-SEC-033) | Cập nhật §8.8 theo CF-39 |
| 10 An toàn | CF-39: PDP + Fleet Governor + envelope ký áp cho ghi qua CPO/cloud hãng; CF-40: IL-10 dẫn NFR-SEC-033 | Cập nhật §5.4/§11 |
| 03 Danh mục | CF-40: cấp F- riêng cho `COMMISSIONING_TEST` (FR-INT-031 đang tạm trỏ F-INT-26…28) | Thêm F- khi cập nhật catalog |
| 06 Kiến trúc | Q-59: Mosquitto 2.1 cho pilot là thay đổi so với ADR-04 ("chỉ dev/lab") do 15 đề xuất; Q-16 mở rộng (EMQX BSL, HiveMQ, RabbitMQ); R-49 | Người viết 06 quyết trong ADR-04 |
| 11 Lộ trình | U-29/U-30 chặn G1; Q-33 (a) vào G1; R-48…R-52 | Thêm vào tiêu chí ra G1 và danh sách rủi ro Phase 0–1 |
| 15 Mô phỏng | R-15-01…08 và Q-E2-01…09 đã có mã 13 (§9) | Dẫn mã 13 khi trích ra ngoài 15 |
| 14 Nguồn | URL ở §11 | Cấp S-xxx |
| 00 Tóm tắt | Mười điều chặn ở §1 | Đưa vào phần rủi ro chính |

---

## 11. Nguồn trích

Mọi URL dưới đây đã xuất hiện trong ghi chú nghiên cứu hoặc tài liệu 02–10; tài liệu này **không** mở trực tiếp URL nào. Nội dung được ghi nhận qua kết quả tìm kiếm của các agent. Mã S-xxx do [14 Nguồn](14-source-register.md) cấp.

- VBHN 52 (NĐ 58 + NĐ 243): https://storage-vnportal.vnpt.vn/gov-tnn/7350/FileQuanTriTinTuc/VBHN%2052%20Nghi%20dinh%2058%20va%20ND%20243%2030.6.pdf
- NĐ 243/2026, trần bán dư 50%: https://luatvietnam.vn/tin-van-ban-moi/tu-26-6-2026-dien-mat-troi-mai-nha-duoc-ban-toi-da-50-san-luong-dien-du-186-109883-article.html
- NĐ 243, điện BESS xả tính vào điện dư; DPPA: https://www.reccessary.com/en/news/vietnam-solar-grid-export-dppa
- NĐ 58/2025: https://blogs.duanemorris.com/vietnam/2025/08/27/vietnam-decree-58-on-development-of-renewable-energy-power-mechanisms-and-policies-for-self-production-and-self-consumption-rooftop-solar-power-systems/
- NĐ 135 bị thay: https://theinvestor.vn/insight-into-vietnams-decree-58-on-renewable-and-new-energy-d14912.html
- QĐ 963/QĐ-BCT (khung TOU): https://thuvienphapluat.vn/van-ban/Tai-nguyen-Moi-truong/Quyet-dinh-963-QD-BCT-2026-khung-gio-cao-diem-thap-diem-cua-he-thong-dien-quoc-gia-703327.aspx ; https://tuoitre.vn/bo-cong-thuong-chinh-thuc-thay-doi-khung-gio-tinh-gia-dien-buoi-toi-la-gio-cao-diem-2026042410430101.htm
- QĐ 1279/QĐ-BCT (giá điện): https://thuvienphapluat.vn/phap-luat-nha-dat/toan-van-quyet-dinh-1279-qd-bct-2025-quy-dinh-ve-gia-ban-dien-3357.html
- Thí điểm giá hai thành phần: https://tapchicongthuong.vn/thi-diem-ap-dung-gia-dien-hai-thanh-phan-tu-1-1-2026-218800.htm
- Quy mô TSXTTT và số hệ bán dư: https://vietnamnet.vn/en/rooftop-solar-saves-billions-of-dong-but-one-bottleneck-remains-2552186.html
- Chưa có giao dịch bán dư đến 08/2026: https://www.pv-magazine.com/2026/09/22/vietnam-pushes-provinces-to-accelerate-rooftop-solar-rollout/
- Biểu giá trạm sạc EV: https://vneconomy.vn/automotive/quy-dinh-moi-ve-gia-ban-dien-cho-tram-sac-xe-dien.htm
- Trang hạt giống: https://www.infinitepowerht.com/what-is-energy-management-system-ems-and-its-functions.html (U-01) ; https://ampowr.com/energy-management-system-ems/ (U-02)
- Giấy phép EMQX 5.9 (BSL 1.1, cluster cần license; Q-16, R-49, theo 15 E2-34): https://www.emqx.com/en/content/license-faq ; https://www.emqx.com/en/blog/adopting-business-source-license-to-accelerate-mqtt-and-ai-innovation ; https://docs.emqx.com/en/emqx/latest/deploy/license.md
- Cấu hình phần cứng tham chiếu (SolarEdge ONE Controller C&I, chỉ dùng làm tham chiếu): https://knowledge-center.solaredge.com/sites/kc/files/se-one-controller-commercial-and-industrial-datasheet-eng.pdf

Nguồn nội bộ: [K-review-round1](notes/K-review-round1.md), [_catalog-gaps](notes/_catalog-gaps.md), các tài liệu 02–10 và nghiên cứu FusionSolar trước ([../fusionsolar/README.md](../fusionsolar/README.md)).
