# C — Kiến thức miền năng lượng cho EMS: đại lượng, quy ước dấu, cân bằng năng lượng, pin, lưới, biểu giá và KPI

[← Mục lục](../index.html) · [04 Yêu cầu](../04-business-requirements.md) · [05 Domain](../05-domain-model.html) · [07 Tích hợp](../07-device-integration.md) · [08 Tối ưu](../08-energy-optimization.md) · [10 An toàn](../10-security-and-reliability.md) · [13 Rủi ro](../13-open-questions-and-risks.md) · [14 Nguồn](../14-source-register.md)

- Tác giả: Agent C (Energy Domain Expert)
- Ngày: 2026-10-10 · Trạng thái: bản nghiên cứu v1. Đầu vào cho 04 (yêu cầu), 05 (domain model), 07 (tích hợp), 08 (tối ưu), 09 (UX: hiển thị số liệu), 10 (an toàn), 12/13.
- Phương pháp: chỉ dùng WebSearch, vì fetch trực tiếp bị chặn. Mọi FACT có URL trong ghi chú này lấy **qua kết quả tìm kiếm** (snippet/tóm tắt), trừ khi ghi "nghiên cứu FusionSolar trước", tức là đã đọc trong `docs/research/fusionsolar/`. Tôi **chưa đọc toàn văn** IEC 61724-1, IEC TS 63019, IEC 62933-2-1, IEC 62116, Thông tư 05/2025/TT-BCT, Nghị định 58/2025 hay 243/2026, và cũng chưa đọc datasheet BESS cụ thể nào. Công thức chuẩn IEC dưới đây là cách hiểu phổ biến của ngành, đã đối chiếu với nguồn thứ cấp (Sandia PVPMC, Hukseflux, Solargis). Trước khi tuyên bố "tuân thủ IEC" phải đối chiếu với văn bản gốc.
- Ký hiệu: `P` công suất tác dụng (kW), `Q` công suất phản kháng (kvar), `S` công suất biểu kiến (kVA), `E` điện năng (kWh), `Δt` độ dài chu kỳ (h). Chỉ số dưới: `grid`, `pv`, `bess`, `ev`, `aux` (phụ trợ), `load` (phụ tải), `gen` (máy phát).

---

## 1. Phạm vi & câu hỏi nghiên cứu

**Phạm vi.** Phần kiến thức miền mà bất kỳ ai viết data model, driver, bộ tính KPI, bộ tối ưu hay giao diện của EMS C&I đa site (PV + BESS + lưới + phụ tải + EV tùy chọn) đều phải dùng chung. Trọng tâm là thị trường Việt Nam, nhưng mô hình phải chạy được cho tenant ở nước khác (múi giờ, biểu giá, chu kỳ đo công suất khác).

| # | Câu hỏi | Trả lời ở |
|---|---|---|
| RQ-C1 | Các đại lượng P/Q/S/E/PF khác nhau thế nào, và nên lưu chúng ra sao để không mất thông tin? | §3.1 |
| RQ-C2 | Chọn quy ước dấu nào? Giữ hay đổi khuyến nghị cũ "lưới + = xuất"? | §3.2 |
| RQ-C3 | Đặt công tơ ở đâu? Topology AC-coupled, DC-coupled và hybrid ảnh hưởng gì tới việc đo? | §3.3 |
| RQ-C4 | Phương trình cân bằng năng lượng tại site là gì? Số hạng nào đo được, số hạng nào phải tính? Phân bổ luồng (PV→tải, PV→pin…) thế nào? | §3.4 |
| RQ-C5 | Tổn hao chuyển đổi, round-trip efficiency (RTE) và tải phụ trợ (HVAC container) tính thế nào? | §3.5 |
| RQ-C6 | Kiến thức pin tối thiểu cho EMS: SOC, SOH, DoD, C-rate, dung lượng khả dụng, trôi SOC, giảm công suất theo nhiệt độ, giới hạn điện áp cell, EFC, lão hóa | §3.6 |
| RQ-C7 | BMS, PCS và EMS chịu trách nhiệm gì? Chuỗi giới hạn (limit chain) ra sao? | §3.7 |
| RQ-C8 | Ràng buộc đấu nối lưới: công suất hợp đồng, giới hạn xuất, hệ số công suất, ramp, chống tách đảo, grid code | §3.8 |
| RQ-C9 | Demand charge, chu kỳ đo công suất (Việt Nam: 15 hay 30 phút?), TOU | §3.9 |
| RQ-C10 | Định nghĩa self-consumption, self-sufficiency, PR (IEC 61724-1), availability, hệ số phát thải (Việt Nam, năm nào, bao nhiêu) | §3.10–3.13 |
| RQ-C11 | Bảng công thức KPI chuẩn kèm quy tắc chất lượng dữ liệu | §3.14 |
| RQ-C12 | Xử lý dữ liệu thiếu, reset bộ đếm, thanh ghi tích lũy và thanh ghi theo chu kỳ, lệch timestamp, múi giờ/DST | §3.15 |

---

## 2. Phát hiện chính

1. **[PROPOSAL] Đổi quy ước dấu so với nghiên cứu FusionSolar trước.** Công suất lưới **dương = nhập lưới (mua điện)**, BESS **dương = xả**, PV ≥ 0, phụ tải ≥ 0. Đây là quy ước "nguồn bơm vào thanh cái site là dương". Khi đó `P_load = P_grid + P_pv + P_bess + P_gen` và mọi số hạng nguồn cộng thẳng, không cần đảo dấu. Khuyến nghị cũ "lưới + = xuất" (theo `meterPower` của Huawei V7) được đưa ra trong bối cảnh chỉ có PV. Nó không còn tối ưu khi sản phẩm thêm BESS, giới hạn nhập (`IMPORT_CAP`), peak shaving và giá hai thành phần, vì tất cả đều là ngưỡng trên **công suất nhập**. Lý do chi tiết và cách chuyển đổi ở §3.2. Bằng chứng nền:
   - OpenEMS dùng lưới dương = mua, ESS dương = xả, và `Consumption = Grid + Production + Storage` — https://community.openems.io/t/can-consumptionactivepower-be-negative/321 ; https://openems.github.io/openems.io/openems/latest/edge/configuration.html (qua kết quả tìm kiếm).
   - Mã OBIS của công tơ: 1.8.0 = điện năng tác dụng chiều dương (A+, nhập), 2.8.0 = chiều âm (A−, xuất) — https://www.wienernetze.at/o/document/ex129_sm_glossar_eng_v04_bf ; https://manuals.lobaro.com/configuration/obis-code-configuration (qua kết quả tìm kiếm).
2. **[FACT] Các bên dùng quy ước dấu lưới khác nhau, kể cả trong cùng một hệ sinh thái.** Theo nghiên cứu FusionSolar trước (`source_code_clients_2.md`): Huawei V7 `meterPower` và client danwale coi dương = xuất; client bresden5 coi dương = nhập; thẻ Tesla-style của Home Assistant dùng − nhập/+ xuất cho lưới và + sạc/− xả cho pin. Diễn đàn OpenEnergyMonitor xác nhận cộng đồng không có chuẩn thống nhất — https://community.openenergymonitor.org/t/is-there-a-standard-for-import-export-positive-negative-power-flow/15149 (qua kết quả tìm kiếm). [INFERENCE] Mỗi driver phải khai báo quy ước dấu của nguồn, và quy trình commissioning phải có bước kiểm tra dấu bằng phép thử thực tế.
3. **[FACT] Việt Nam đang dùng chu kỳ tích phân 30 phút để xác định công suất cực đại (Pmax) trong giá điện hai thành phần.** Pmax là "công suất trung bình trong khoảng thời gian tích phân có giá trị lớn nhất của tháng, khoảng thời gian tích phân hiện nay đang là 30 phút". Hạ tầng công tơ điện tử đo xa đã xác định được công suất theo chu kỳ 30 phút — https://daibieunhandan.vn/trien-khai-thu-nghiem-gia-ban-le-dien-hai-thanh-phan-tu-thang-10-2025-10390577.html ; https://tapchicongthuong.vn/evn-xay-dung-he-thong-gia-ban-dien-hai-thanh-phan-264219.htm ; https://vnexpress.net/de-xuat-thi-diem-gia-dien-hai-thanh-phan-tu-2026-4936558.html (qua kết quả tìm kiếm). Để so sánh: lưới Berlin (Đức) tính công suất theo **trung bình 15 phút** lớn nhất trong năm — https://www.stromnetz.berlin/files/globalassets/dokumente/entgelte/zugang/entgelte-01.01.2011/entgelte-lastgangkunden-b-2011.pdf (qua kết quả tìm kiếm). [PROPOSAL] Độ dài cửa sổ demand là **tham số của biểu giá** (15/30/60 phút, kiểu block hay rolling), không hard-code.
4. **[FACT] Hệ số phát thải lưới điện Việt Nam chính thức mới nhất tìm được là năm 2023: 0,6592 tCO2/MWh.** Giá trị này được công bố bằng Công văn 1726/BĐKH-PTCBT của Cục Biến đổi khí hậu (Bộ TN&MT cũ, nay là Bộ Nông nghiệp và Môi trường). Năm 2022 là 0,6766 — https://luatvietnam.vn/dien-luc/cong-van-1726-bdkh-ptcbt-2024-cong-bo-ket-qua-he-so-phat-thai-luoi-dien-viet-nam-425131-d6.html ; https://klinova.vn/latest-news/release-of-vietnams-2023-power-grid-emission-coefficient.html (qua kết quả tìm kiếm).
   - **[FACT] Năm 2024 mới có ước tính của nhóm nghiên cứu, chưa có công bố chính thức:** 0,681 tCO2e/MWh, tăng 3,2% so với 2023 (ĐH Bách khoa Hà Nội phối hợp Bộ NN&MT). Năm 2025 có ước tính 0,6235 của một nhóm tác giả. Theo một bài viết, đến 01/2026 hệ số 2024 và 2025 vẫn chưa được công bố chính thức, và thẩm quyền công bố có thể đã chuyển sang Bộ Công Thương (chỉ một nguồn) — https://vietnamnews.vn/environment/1716087/study-shows-coal-power-dominant-as-viet-nam-s-grid-emissions-climbed-in-2024.html ; https://doanhnghiepkinhtexanh.vn/uoc-tinh-he-so-phat-thai-khi-nha-kinh-cua-luoi-dien-viet-nam-2025-a43738.html ; https://tapchicongthuong.vn/hoi-thao-ky-thuat-ve-tinh-toan-he-so-phat-thai-luoi-dien-va-nhiet-dien-than--buoc-tien-trong-minh-bach-hoa-du-lieu-khi-nha-kinh-142455.htm (qua kết quả tìm kiếm).
   - [UNKNOWN] Đến 10/2026 đã có văn bản chính thức cho năm 2024 hay chưa.
   - [PROPOSAL] Hệ số phát thải phải là dữ liệu có phiên bản: năm, giá trị, đơn vị (tCO2 hay tCO2e), cơ quan công bố, số văn bản, trạng thái "chính thức/ước tính".
5. **[FACT] Thông tư 05/2025/TT-BCT, Điều 31, quy định hệ số công suất (cosφ).** Khách hàng sản xuất, kinh doanh, dịch vụ có trạm riêng, hoặc có công suất sử dụng cực đại ≥ 40 kW, phải giữ cosφ tại điểm đặt công tơ **không nhỏ hơn 0,9** theo hợp đồng mua bán điện. Với đơn vị nhận điện từ lưới truyền tải: ≥ 0,9 khi nhận công suất phản kháng và ≥ 0,98 khi phát ngược — https://thuvienphapluat.vn/van-ban/Thuong-mai/Thong-tu-05-2025-TT-BCT-he-thong-truyen-tai-dien-phan-phoi-dien-do-dem-dien-nang-642994.aspx ; https://www.evn.com.vn/userfile/User/giangtcdl/files/2025/8/VBHN38-20250814160032345.pdf (qua kết quả tìm kiếm; hai snippet mô tả đối tượng áp dụng hơi khác nhau). [INFERENCE] EMS cần đo Q và tính PF **tại điểm đo đếm chính (POC)**. Khi PV hoặc BESS bù P cho tải, P nhập giảm còn Q nhập giữ nguyên, nên PF tại POC giảm. Đây là rủi ro thực tế với C&I có PV lớn.
6. **[FACT] Theo tóm tắt báo chí về Nghị định 243/2026, trần bán điện dư là 50%, và điện xả từ BESS tích từ ĐMTMN được tính vào phần điện dư.** Một số nguồn diễn đạt cơ sở tính là 50% "sản lượng điện thực phát" — https://xbsolar.vn/nghi-dinh-243-2026-nd-cp-chinh-thuc-cho-ban-50-dien-mat-troi-mai-nha/ ; https://anninhthudo.vn/cho-phep-ban-dien-mat-troi-mai-nha-du-thua-len-toi-50-post657682.antd ; https://congthuong.vn/dien-mat-troi-mai-nha-duoc-ban-toi-50-san-luong-dien-du-463096.html (qua kết quả tìm kiếm). [INFERENCE] Ngoài giới hạn xuất tức thời (kW), cần thêm **ngân sách xuất theo điện năng** trong kỳ (kWh/tháng ≤ 50% × điện PV đo tại đầu ra inverter), và phải quy kết được nguồn gốc điện xuất (PV trực tiếp hay BESS). [UNKNOWN] Mẫu số chính xác của tỷ lệ 50% và kỳ tính (tháng hay năm) — phải đối chiếu văn bản gốc.
7. **[FACT] Ranh giới đo quyết định giá trị RTE.** Báo cáo PNNL về một BESS quy mô lưới cho thấy RTE đo được tăng khoảng 6–16% khi loại tiêu thụ phụ trợ khỏi phép tính — https://www.pnnl.gov/main/publications/external/technical_reports/PNNL-27237.pdf (qua kết quả tìm kiếm). Một đặc tả BESS của Hy Lạp tính cả HVAC, làm mát pin, BMS, đèn sự cố và tổn hao máy biến áp/bộ biến đổi vào RTE, đo tại điểm đấu nối — https://www.rae.gr/wp-content/uploads/2023/06/H1_BESS-Installation-Safety-and-Performance-Specifications.pdf (qua kết quả tìm kiếm). Tài liệu hiệu suất của FENECON 2025 thì loại tổn hao máy biến áp và tiêu thụ phụ trợ — https://docs.fenecon.de/pdfs/industrial/2025/en/Wirkungsgrad_FENECON_Industrial_L_und_XL_EN.pdf (qua kết quả tìm kiếm). [PROPOSAL] Mọi KPI hiệu suất BESS phải ghi rõ ranh giới (DC, AC tại PCS, AC tại POC có aux).
8. **[FACT] SOC của pin LFP khó ước lượng và có thể trôi hoặc "nhảy".** Đường OCV–SOC rất phẳng, khoảng 100 mV trên 60% dải SOC. Coulomb counting tích lũy sai số. BESS chạy peak shaving/arbitrage thường ở dải 20–80%, nên hiếm khi chạm mốc 0%/100% để hiệu chỉnh — https://www.accure.net/blogs/state-of-charge-soc-estimation-errors-for-lfp-batteries-can-exceed-15 ; https://www.clarke-energy.com/2026/lithium-iron-phosphate-bess-the-state-of-charge-challenge/ ; https://pv-magazine-usa.com/2024/09/25/the-significance-of-state-of-charge-in-energy-storage/ (qua kết quả tìm kiếm; nguồn vendor, con số "lỗi >15%" là của ACCURE). [PROPOSAL] EMS coi SOC là **giá trị BMS công bố, có độ bất định**. Không ra quyết định an toàn dựa vào SOC; dùng giới hạn công suất/dòng do BMS công bố. Bước nhảy SOC được ghi thành sự kiện "hiệu chỉnh SOC", không phải bất thường năng lượng.
9. **[FACT] Phân vai BMS/PCS/EMS.**
   - BMS bảo vệ cell: giám sát điện áp, dòng, nhiệt độ cell; cân bằng cell; mở contactor khi vượt giới hạn.
   - PCS chuyển đổi DC↔AC và thực thi lệnh.
   - EMS quyết định điều độ (khi nào sạc/xả, bao nhiêu kW) theo mục tiêu kinh tế.
   - Giới hạn của BMS (ví dụ xả tối đa 220 kW) phải được cả PCS lẫn EMS tôn trọng.
   — https://deye.com/nl/blog/bms-vs-ems-vs-pcs-bess-components/ ; https://www.infinitepowerht.com/what-is-energy-management-system-ems-and-its-functions.html (qua kết quả tìm kiếm). BMS hạ CCL/DCL (giới hạn dòng sạc/xả) theo SOC, nhiệt độ, điện áp cell, điện trở cell, và có thể đặt CCL = 0 — https://www.orionbms.com/manuals/utility/bms_param_current_limit_status.html (qua kết quả tìm kiếm). [PROPOSAL] Cloud chỉ gửi **mục tiêu/lịch có thời hạn**. Edge kẹp (clamp) mọi setpoint theo giới hạn BMS/PCS/lưới mới nhất. Không lớp phần mềm nào được ghi đè bảo vệ của BMS/PCS/rơ-le.
10. **[FACT] IEC 61724-1 định nghĩa PR = Yf/Yr.** `Yf = E_AC/P0` và `Yr = H_POA/G_ref` (G_ref = 1 kW/m²). Có biến thể PR hiệu chỉnh nhiệt độ — https://pvpmc.sandia.gov/modeling-guide/5-ac-system-output/pv-performance-metrics/performance-ratio/ ; https://kb.solargis.com/docs/pv-performance-indicators (qua kết quả tìm kiếm). Bản 2021 chỉ còn **hai cấp chính xác Class A và Class B** (Class C cũ thành Class B) — https://www.hukseflux.com/uploads/inline/iec_61724-1_2021_version-what_is_new_v2403_0.pdf (qua kết quả tìm kiếm). [INFERENCE] Ở site zero-export hoặc giới hạn xuất của Việt Nam, PV thường bị cắt công suất (curtail), nên PR thô sẽ thấp giả tạo. Phải tính thêm PR loại trừ chu kỳ bị curtail, hoặc "điện năng tiềm năng".
11. **[FACT] Availability của nhà máy PV có khung chuẩn riêng là IEC TS 63019:2019**, không nằm trong IEC TS 61724-3 (61724-3 là phương pháp đánh giá điện năng) — https://webstore.iec.ch/en/publication/25466 (qua kết quả tìm kiếm, mô tả phạm vi). [PROPOSAL] Cung cấp cả availability theo thời gian và theo điện năng, có danh mục loại trừ (lưới mất điện, chủ đầu tư yêu cầu, bất khả kháng) cấu hình theo hợp đồng.
12. **[FACT] Thanh ghi điện năng tích lũy của công tơ có thể tràn (rollover).** Ví dụ ngưỡng mặc định của Schneider ION là 10.000.000, kèm bộ đếm số lần tràn. EnergyCAP chỉ coi một lần giảm số là tràn khi mức giảm > 10% giá trị cực đại của kênh, để tránh nhầm với thay công tơ hay reset — https://www.se.com/us/en/faqs/FA239195/ ; https://helpcenter.energycap.com/um/sa/types_of_readings (qua kết quả tìm kiếm). [PROPOSAL] Pipeline tính delta điện năng có máy trạng thái riêng (§3.15).
13. **[FACT] Grid code Việt Nam mới.** Thông tư 05/2025/TT-BCT (01/02/2025) quy định hệ thống truyền tải, phân phối và đo đếm điện năng, và đã có văn bản hợp nhất ngày 14/08/2025 — https://thuvienphapluat.vn/van-ban/Thuong-mai/Thong-tu-05-2025-TT-BCT-he-thong-truyen-tai-dien-phan-phoi-dien-do-dem-dien-nang-642994.aspx ; https://www.evn.com.vn/userfile/User/giangtcdl/files/2025/8/VBHN38-20250814160032345.pdf (qua kết quả tìm kiếm). Một blog vendor tóm tắt yêu cầu ride-through (điện áp 50–85% trong 2 s; tần số 48–49 Hz ≥ 30 phút; 49–51 Hz liên tục) và PV hạ áp không được phát Q, PF > 0,98 — https://www.gkoisolar.com/solar-inverter-requirements-in-vietnam-2026/ (qua kết quả tìm kiếm; độ tin thấp). [INFERENCE] Đây là chức năng **của inverter/PCS** đã được chứng nhận. EMS chỉ đọc và giám sát, không cấu hình lại tùy tiện.
14. **[INFERENCE] Phân bổ luồng năng lượng (PV→tải, PV→pin, lưới→pin, pin→lưới…) là quy ước kế toán, không phải phép đo vật lý.** Electron không mang nhãn nguồn. Kết quả phụ thuộc thứ tự ưu tiên và độ dài chu kỳ tính: tính theo ngày sẽ "netting" mất luồng thực. Bằng chứng: các client cộng đồng của FusionSolar tự phân bổ bằng các luật min/max khác nhau (nghiên cứu FusionSolar trước, `source_code_clients_2.md`, thẻ tesla-style-solar-power-card). [PROPOSAL] Công bố một thuật toán phân bổ duy nhất, tính ở chu kỳ ≤ 1 phút (mặc định là chu kỳ lưu trữ thô), rồi cộng dồn.
15. **[UNKNOWN] Chi tiết trong văn bản gốc chưa kiểm chứng được:** ramp-rate bắt buộc với C&I ở Việt Nam; thời gian ngắt chống tách đảo (IEC 62116 chỉ là phương pháp thử, ngưỡng do grid code đặt — https://knowledge.bsigroup.com/products/test-procedure-of-islanding-prevention-measures-for-utility-interconnected-photovoltaic-inverters, qua kết quả tìm kiếm); cơ chế phạt mua công suất phản kháng hiện hành; đặc tả kỹ thuật thiết bị chống phát ngược theo NĐ 58.

---

## 3. Phân tích chi tiết

### 3.1 Đại lượng, đơn vị và cách lưu

| Đại lượng | Ký hiệu | Đơn vị lưu (canonical) | Ý nghĩa | Lưu ý cho implementer |
|---|---|---|---|---|
| Công suất tác dụng | P | kW (float64; driver đổi từ W/MW) | Tốc độ truyền năng lượng thực | Giá trị tức thời hoặc trung bình chu kỳ. Phải ghi rõ là `instant`, `avg` hay `max` |
| Công suất phản kháng | Q | kvar | Năng lượng dao động giữa nguồn và tải cảm/dung | Dấu theo quy ước 4 góc phần tư (dưới đây). Cần cho PF tại POC |
| Công suất biểu kiến | S | kVA | `S = √(P² + Q²)` (sóng sin cân bằng) | Định mức inverter/PCS/máy biến áp thường tính theo kVA. Giới hạn: `P² + Q² ≤ S_max²` |
| Hệ số công suất | PF | không thứ nguyên, −1…1 | `PF = P/S` | **Không lưu PF làm dữ liệu gốc.** Lưu P và Q, tính PF khi cần. Nếu thiết bị chỉ cho PF thì lưu kèm cờ `lead/lag` và quy ước của hãng (IEC và IEEE khác nhau về dấu PF) |
| Điện năng tác dụng | E | kWh (float64 hoặc decimal; bộ đếm tích lũy có thể là int64 Wh) | `E = ∫P dt` | Có hai loại: **thanh ghi tích lũy** (monotonic, ví dụ OBIS 1.8.0/2.8.0) và **điện năng theo chu kỳ** (delta). Lưu tách nhập/xuất, không lưu "net" duy nhất |
| Điện năng phản kháng | Eq | kvarh | `∫Q dt` theo góc phần tư | Công tơ 4 góc phần tư: Q1 (nhập P, cảm), Q2, Q3, Q4. Cần cho PF bình quân kỳ và phạt phản kháng (nếu có) |
| Công suất đặt PV | P0 | kWp (DC, STC) | Tổng công suất danh định tấm pin | Khác với kWac của inverter. Tỷ lệ DC/AC (ILR) quyết định clipping |
| Dung lượng pin | E_nom, E_usable | kWh | Danh định so với khả dụng | §3.6. Ghi rõ đo ở DC hay AC, ở công suất nào |
| Công suất cửa sổ demand | P_dem | kW | `E_import(cửa sổ)/T_w` | §3.9. Là **công suất trung bình**, không phải đỉnh tức thời |

**Quy tắc cốt lõi.**
- [PROPOSAL] **Điện năng tính từ thanh ghi điện năng, không tích phân công suất lấy mẫu**, khi thiết bị có thanh ghi. Mẫu P mỗi 5–60 s bỏ sót dao động và lệch pha lấy mẫu. Tích phân P chỉ là phương án dự phòng, và phải gắn cờ `ESTIMATED_FROM_POWER`.
- [PROPOSAL] Công suất trung bình chu kỳ `P_avg(k) = ΔE(k)/Δt` là cách duy nhất để khớp với cách công tơ tính Pmax (§3.9).
- [INFERENCE] Hệ ba pha không cân bằng: P tổng = ΣP pha. Giới hạn xuất "theo pha" (Huawei có chế độ "single-phase power" — nghiên cứu FusionSolar trước, `workflows_data_model.md`) cần dữ liệu từng pha, nên data model phải có kênh `p_l1/p_l2/p_l3`.

### 3.2 Quy ước dấu — quyết định

**Các phương án**

| Phương án | Lưới | BESS | PV | Ai dùng | Ưu | Nhược |
|---|---|---|---|---|---|---|
| A. "Nguồn bơm vào thanh cái site là dương" | + nhập | + xả | ≥ 0 | OpenEMS (lưới + = mua, ESS + = xả) [FACT, xem Phát hiện #1]; OBIS A+ = nhập | `P_load = P_grid + P_pv + P_bess`: cộng thẳng. Ngưỡng `IMPORT_CAP`, Pmax, peak shaving đều là số dương. Khớp hướng edge kiểu OpenEMS của dự án | Xuất lưới là số âm, báo cáo PV-only phải đổi dấu khi hiển thị |
| B. "Lưới + = xuất" (khuyến nghị cũ) | + xuất | thường + sạc hoặc + xả tùy hãng | ≥ 0 | Huawei V7 `meterPower`, danwale (nghiên cứu FusionSolar trước) | Trực quan cho PV-only/feed-in | `P_load = P_pv − P_grid + …`. Mọi ngưỡng nhập thành số âm. Dễ sai khi thêm BESS |
| C. Không dùng dấu, chỉ dùng cặp không âm | `import ≥ 0`, `export ≥ 0` | `charge ≥ 0`, `discharge ≥ 0` | ≥ 0 | Thanh ghi công tơ, hóa đơn | Không bao giờ sai dấu khi đọc | Tức thời cần hai trường; điều khiển cần một biến có dấu |

**Quyết định [PROPOSAL]**
1. **Lưu trữ và tính toán nội bộ dùng phương án A.**
   - `p_grid_kw`: + nhập, − xuất.
   - `p_bess_kw`: + xả, − sạc. Đo tại cực AC của BESS nếu là AC-coupled.
   - `p_pv_kw ≥ 0`. Giá trị âm nhỏ ban đêm là tự tiêu thụ của inverter; giữ nguyên, không ép về 0.
   - `p_ev_kw ≥ 0` là tiêu thụ. V2G sau này sẽ âm.
   - `p_load_kw ≥ 0`.
   - `p_gen_kw ≥ 0` cho máy phát.
2. **Tên trường mang hướng.** API và schema dùng tên như `grid_net_import_kw`, `bess_net_discharge_kw` để dấu tự giải thích. Tên trơn như `grid_power` dễ hiểu sai.
3. **Điện năng luôn lưu theo cặp không âm (phương án C):** `e_grid_import_kwh`, `e_grid_export_kwh`, `e_bess_charge_kwh`, `e_bess_discharge_kwh`. Không lưu net làm dữ liệu gốc, vì net theo ngày làm mất thông tin hóa đơn và mất luồng (Phát hiện #14).
4. **Lớp hiển thị được đổi dấu hoặc nhãn** (ví dụ thẻ "Xuất lưới 120 kW" hiển thị số dương), nhưng không đổi dữ liệu.
5. **Driver khai báo `sign_convention` của nguồn** (ví dụ Huawei `meterPower`: + = xuất → driver nhân −1). Commissioning bắt buộc chạy "phép thử dấu":
   - Bật một tải đã biết khi PV/BESS dừng. P lưới phải tăng dương.
   - Lệnh BESS xả nhỏ. `p_bess` phải dương và `p_grid` phải giảm.
   - Kết quả ghi vào hồ sơ commissioning.
   - [INFERENCE] Lắp ngược CT (biến dòng) là lỗi thực địa phổ biến, nên phép thử này cũng bắt được lỗi lắp đặt chứ không chỉ lỗi phần mềm.

**Lý do đổi so với nghiên cứu FusionSolar.** Khuyến nghị cũ ("Lưu công suất nút có dấu theo một quy ước công bố (lưới + = xuất)" — `01_bao_cao/Phân rã sản phẩm FusionSolar.html`) có mục đích là **một quy ước duy nhất, công bố rõ**. Mục đích đó vẫn giữ. Chỉ chiều dấu đổi, vì 4 lý do:
- (i) Sản phẩm mới điều khiển theo ngưỡng nhập (`IMPORT_CAP`, Pmax 30 phút, peak shaving).
- (ii) Edge tham chiếu OpenEMS dùng nhập dương. Theo cùng chiều thì bớt một lớp chuyển đổi và bớt lỗi.
- (iii) Thanh ghi công tơ thương mại lấy nhập làm chiều dương (A+).
- (iv) Với site Việt Nam đa số không bán điện dư (A-market-boundary Phát hiện #3), nhập là chiều "bình thường".

Rủi ro: tài liệu và wireframe FusionSolar cũ dùng "+ = xuất" phải được đánh dấu là lỗi thời (xem §7 X-C01).

### 3.3 Ranh giới đo và topology công tơ

**Điểm đo (đặt tên chuẩn) [PROPOSAL]**

| Mã | Vị trí | Mục đích | Bắt buộc? | Ghi chú |
|---|---|---|---|---|
| `MTR_POC` | Điểm đấu nối chung (POC/PCC) với lưới, phía công tơ thanh toán | Điều khiển xuất/nhập, peak shaving, PF tại POC, hóa đơn bóng | **Bắt buộc** cho mọi chức năng điều khiển lưới | Công tơ EVN thường **không** đọc được thời gian thực. EMS cần **công tơ điều khiển riêng** (control meter) đặt cạnh. Sai lệch giữa hai công tơ phải đối soát hằng tháng |
| `MTR_POC_LV` | Phía hạ áp máy biến áp khách hàng, nếu POC ở trung áp (22 kV) | Thay `MTR_POC` khi không đặt được CT/VT trung áp | Tùy | Chênh lệch với công tơ trung áp ≈ tổn hao MBA (không tải + có tải). Phải hiệu chỉnh khi tính Pmax/ngân sách xuất |
| `MTR_PV` | Đầu ra AC của nhóm inverter PV | Sản lượng PV, PR, cơ sở tính 50% điện dư (NĐ 243) | Khuyến nghị; có thể dùng tổng thanh ghi inverter | Thanh ghi inverter có sai số lớn hơn công tơ chuẩn. Ghi `accuracy_class` |
| `MTR_BESS` | Cực AC của BESS (sau PCS, trước hoặc sau MBA của BESS) | Năng lượng sạc/xả, RTE, EFC (AC) | Bắt buộc nếu có BESS AC-coupled | Ghi rõ **aux có nằm sau công tơ này không** (§3.5) |
| `MTR_AUX` | Nguồn phụ trợ BESS (HVAC, BMS, chữa cháy, chiếu sáng) | Tách tiêu thụ phụ trợ | Khuyến nghị | Không có thì aux lẫn vào tải hoặc vào sạc BESS, tùy sơ đồ |
| `MTR_LOAD_i` | Từng nhánh phụ tải (submeter) | Phân bổ, phụ tải linh hoạt, cân bằng chéo | Tùy | Tổng submeter thường < tải tính toán, phần còn lại là "tải không đo" |
| `MTR_EV_i` | Từng trụ sạc EV hoặc nhóm | Năng lượng sạc, điều khiển công suất | Nếu có EV | Trụ AC thường có công tơ tích hợp (MID/OCPP `MeterValues`) |
| `MTR_GEN` | Máy phát diesel/gas | Tránh nhầm với PV khi mất lưới | Nếu có | — |
| `DC_PV`, `DC_BAT` | Phía DC (MPPT, cổng pin của hybrid inverter) | Chỉ có ở DC-coupled/hybrid | Đọc từ inverter | Không phải công tơ, độ chính xác theo hãng |

**So sánh topology**

| Topology | Mô tả | Đo được trực tiếp | Phải tính | Hệ quả |
|---|---|---|---|---|
| T1 PV-only | Inverter PV + công tơ POC | P_grid, P_pv | P_load = P_grid + P_pv | Nền tảng FusionSolar cũ |
| T2 AC-coupled BESS | PCS riêng nối thanh cái AC | P_grid, P_pv, P_bess (AC) | P_load | Retrofit dễ, giữ inverter cũ. PV bị clip ở inverter thì không cứu được: không có đường DC từ PV sang pin — https://arxiv.org/pdf/2605.14043 (qua kết quả tìm kiếm) |
| T3 DC-coupled / hybrid | PV và pin chung DC bus, một bộ biến đổi ra AC | P_grid, P_inv_ac (tổng), DC_PV, DC_BAT | Tách "PV phần AC" và "BESS phần AC" là **ước lượng** (phân bổ tổn hao inverter theo tỷ lệ) | KPI PV (PR) và KPI BESS (RTE) không còn ranh giới AC riêng. Phải ghi `boundary = DC` hoặc `allocated`. Thu được năng lượng clip vào pin — https://www.batterypowertips.com/?p=4501 (qua kết quả tìm kiếm) |
| T4 Nhiều POC / nhiều MBA | Site có nhiều điểm đấu nối hoặc nhiều hợp đồng | Mỗi POC một công tơ | Cân bằng **theo từng POC** | Không được cộng gộp xuất ở POC A với nhập ở POC B để "net" (hợp đồng riêng) |
| T5 Có máy phát / microgrid | Máy phát, chuyển mạch ATS | + P_gen, trạng thái ATS | — | Khi đảo (island), P_grid = 0, nên cân bằng đổi dạng. Cờ `grid_connected` |
| T6 EV | Trụ sạc sau POC | P_ev | — | EV là tải đặc biệt có thể điều khiển. Tách khỏi P_load để tính KPI tải nền |

**Sơ đồ nguyên lý (AC-coupled, khách trung áp)**

```
Lưới 22 kV ──[MTR_EVN (thanh toán)]──[MTR_POC (điều khiển)]── MBA khách 22/0,4 kV ──┬── Thanh cái 0,4 kV
                                                                                  ├─[MTR_PV]── Inverter PV ── dàn PV
                                                                                  ├─[MTR_BESS]── MBA BESS? ── PCS ── Pin (BMS)
                                                                                  │                └─[MTR_AUX]── HVAC/BMS/PCCC (nếu lấy nguồn sau MTR_BESS)
                                                                                  ├─[MTR_EV_i]── Trụ sạc
                                                                                  └─[MTR_LOAD_i]── Phụ tải (có phần không đo)
```

### 3.4 Phương trình cân bằng năng lượng tại site

**Dẫn xuất (quy ước A, một POC, chế độ nối lưới).** Lấy nút là thanh cái site, phía sau `MTR_POC`. Định luật bảo toàn năng lượng (Kirchhoff cho công suất tác dụng) cho:

> Tổng công suất vào nút = tổng công suất ra khỏi nút

- Vào: `P_grid_import`, `P_pv`, `P_bess_discharge`, `P_gen`
- Ra: `P_grid_export`, `P_bess_charge`, `P_load_base`, `P_ev`, `P_aux_unmetered`, `P_loss` (cáp, MBA nằm giữa POC và các công tơ con)

Với biến có dấu `P_grid = P_grid_import − P_grid_export` và `P_bess = P_bess_discharge − P_bess_charge`:

```
(1)  P_grid + P_pv + P_bess + P_gen = P_load_base + P_ev + P_aux + P_loss
```

Định nghĩa "tiêu thụ site" `P_cons` là tất cả những gì không phải nguồn hay lưu trữ:

```
(2)  P_cons = P_load_base + P_ev + P_aux + P_loss = P_grid + P_pv + P_bess + P_gen
```

Dạng mà đề bài nêu ra là (2) viết tách hướng:

```
(3)  P_cons = P_grid_import − P_grid_export + P_pv + P_bess_discharge − P_bess_charge + P_gen
```

Khi tách tổn hao khỏi tải thực:

```
(4)  P_load_base = P_grid_import − P_grid_export + P_pv + P_bess_discharge − P_bess_charge + P_gen − P_ev − P_aux − P_loss
```

**Lưu ý về `P_aux` và `P_loss`:**
- Nếu `MTR_BESS` đo **sau** điểm lấy nguồn aux (aux nằm trong ranh giới BESS), `P_bess` đã là net (xả − sạc − aux). Khi đó **không trừ `P_aux` lần nữa** trong (4).
- Tổn hao biến đổi của PV và PCS đã nằm trong số đo AC của chúng. `P_loss` chỉ gồm tổn hao giữa các công tơ AC và POC (cáp, MBA khách nếu `MTR_POC` ở trung áp). Thực tế `P_loss` gần như không bao giờ đo riêng, nên nó nằm lẫn trong `P_load_base` tính toán.

**Dạng điện năng theo chu kỳ k** (độ dài Δt; dùng delta từ thanh ghi):

```
(5)  E_cons(k) = E_imp(k) − E_exp(k) + E_pv(k) + E_dis(k) − E_ch(k) + E_gen(k)
```

Cảnh báo:
- (5) chỉ đúng khi mọi chu kỳ thẳng hàng thời gian (§3.15).
- `E_imp` và `E_exp` lấy từ hai thanh ghi riêng. Không tính bằng `max(0, ΣP)`.

**Đo và tính [PROPOSAL]**

| Số hạng | Nguồn dữ liệu | Loại |
|---|---|---|
| P_grid, E_imp, E_exp, Q_grid | `MTR_POC` | Đo |
| P_pv, E_pv | `MTR_PV` hoặc tổng inverter | Đo (độ chính xác theo nguồn) |
| P_bess, E_ch, E_dis | `MTR_BESS` hoặc PCS | Đo |
| P_ev, E_ev | Trụ sạc / `MTR_EV` | Đo |
| P_aux | `MTR_AUX` hoặc ước lượng | Đo hoặc ước lượng |
| P_cons, P_load_base | (2), (4) | **Tính** |
| P_loss | Chỉ có trong (6) dưới đây khi có đủ submeter | **Tính** (residual) |
| Luồng phân bổ (PV→tải…) | Thuật toán phân bổ | **Tính theo quy ước** |

**Kiểm tra nhất quán (residual).** Khi có submeter phủ đủ tải:

```
(6)  R(k) = [E_imp − E_exp + E_pv + E_dis − E_ch + E_gen](k) − [Σ E_load_i + E_ev + E_aux](k)
```

- `R` = tổn hao + tải không đo + sai số đo.
- [PROPOSAL] Theo dõi `R/E_cons` theo ngày. Khi vượt ngưỡng cấu hình (ví dụ lệch so với trung bình 30 ngày quá 3σ), sinh cảnh báo chất lượng dữ liệu `DQ_BALANCE_RESIDUAL`. Nguyên nhân thường gặp: CT ngược, sai tỷ số CT/VT, một nhánh mất dữ liệu, thay công tơ.
- `R` âm kéo dài gần như chắc chắn là lỗi đo hoặc dấu.
- Ví dụ của OpenEMS: consumption tính ra bị âm khi xuất lớn — https://community.openems.io/t/can-consumptionactivepower-be-negative/321 (qua kết quả tìm kiếm). [PROPOSAL] Không ép `P_cons` về 0. Giữ giá trị âm và gắn cờ `SUSPECT_NEGATIVE_CONSUMPTION`, vì ép về 0 sẽ che lỗi.

**Phân bổ luồng (flow attribution) [PROPOSAL]** — tính ở **từng chu kỳ thô** (≤ 1 phút, hoặc chu kỳ lưu trữ thô của thiết bị), sau đó mới cộng dồn. Thứ tự ưu tiên mặc định, có công bố và có phiên bản thuật toán (`attribution_version`):

```
Đầu vào chu kỳ (kWh, đều ≥ 0): pv, imp, exp, ch, dis, gen; cons = imp − exp + pv + dis − ch + gen
1. pv_to_load   = min(pv, cons)
2. pv_rest      = pv − pv_to_load
3. pv_to_bess   = min(pv_rest, ch)
4. pv_to_grid   = pv_rest − pv_to_bess           (≈ phần đóng góp PV trong exp)
5. grid_to_bess = ch − pv_to_bess                (≥ 0; sạc từ lưới)
6. load_rest    = cons − pv_to_load
7. bess_to_load = min(dis, load_rest)
8. bess_to_grid = dis − bess_to_load
9. grid_to_load = load_rest − bess_to_load (− gen_to_load nếu có máy phát, xếp sau BESS)
Kiểm tra: pv_to_grid + bess_to_grid (+ gen_to_grid) = exp ; grid_to_load + grid_to_bess = imp  (sai lệch ≤ ε do làm tròn)
```

- Một chu kỳ vừa sạc vừa xả (ch > 0 và dis > 0) có thể xảy ra khi chu kỳ dài hoặc có nhiều PCS. Thuật toán trên vẫn đóng, nhưng nên gắn cờ.
- Đẳng thức kiểm tra chỉ đúng khi `cons ≥ 0`. Nếu không thì gắn cờ và bỏ qua phân bổ cho chu kỳ đó.
- Đẳng thức cũng không đúng khi trong **cùng một chu kỳ** có cả nhập lẫn xuất (`imp > 0` và `exp > 0`, ví dụ mây bay qua trong chu kỳ 15 phút). Thuật toán khi đó tự "net" và bỏ sót luồng. [PROPOSAL] Phải chạy ở chu kỳ đủ ngắn để hiếm khi có cả hai. Phần lệch `min(imp, exp)` được ghi thành chỉ số `netting_kwh` để đo sai số do chu kỳ.
- [INFERENCE] Thứ tự này quyết định số liệu "điện BESS xuất lưới" và "BESS sạc từ lưới". Cả hai liên quan trực tiếp NĐ 243 (điện xả BESS tích từ ĐMTMN được tính vào điện dư) và câu hỏi pháp lý: BESS sạc từ lưới rồi xả ra lưới có được tính là điện dư không [UNKNOWN]. Để quy kết nguồn gốc năng lượng trong pin, cần thêm **sổ cái năng lượng trong pin** ("solar-origin share" của năng lượng đang lưu, cập nhật theo kiểu FIFO hoặc bình quân gia quyền). [PROPOSAL] P1, dùng bình quân gia quyền:

```
stored_solar_kwh += pv_to_bess·η_ch ; stored_grid_kwh += grid_to_bess·η_ch
share_solar = stored_solar / (stored_solar + stored_grid)
bess_to_grid_solar = bess_to_grid · share_solar ; khi xả trừ hai kho theo tỷ lệ
```

**Ví dụ kiểm tra (một chu kỳ 1 h, số minh họa).** PV 300 kWh, nhập 200, xả 100, sạc 0, xuất 0. Khi đó cons = 600, pv_to_load = 300, bess_to_load = 100, grid_to_load = 200. Đẳng thức đúng.

Đổi lại: PV 500, cons 300, sạc 150, nhập 0, xuất 50. Khi đó pv_to_load = 300, pv_to_bess = 150, pv_to_grid = 50 = exp. Đẳng thức đúng.

**Chế độ đảo (off-grid/backup).** `P_grid = 0`. Nếu có ATS thì nút cân bằng là thanh cái được cấp bởi BESS/máy phát. Các KPI dựa trên lưới (PF tại POC, Pmax) không tính cho chu kỳ đảo (gắn cờ `ISLANDED`).

### 3.5 Tổn hao chuyển đổi, RTE và tải phụ trợ

**Chuỗi tổn hao (AC-coupled):**

```
PV DC ─η_inv_pv→ AC ─η_cable/MBA→ POC
Lưới/PV AC ─η_pcs(sạc)→ DC ─η_pin(coulomb, nhiệt)→ lưu ─η_pin→ DC ─η_pcs(xả)→ AC ─η_MBA_BESS→ thanh cái
                                                      + tự xả, + tải phụ trợ (HVAC, BMS, PCCC, chiếu sáng, PCS standby)
```

**Ba ranh giới RTE [PROPOSAL] — luôn ghi `rte_boundary`:**

| Mã | Ranh giới | Công thức | Dùng cho |
|---|---|---|---|
| `RTE_DC` | Cực DC của pin (BMS) | `E_dis_DC/E_ch_DC` | So sánh cell/pack, kiểm tra BMS |
| `RTE_AC_PCS` | Cực AC của PCS, không gồm aux | `E_dis_AC/E_ch_AC` | So với datasheet hãng (thường là ranh giới này) |
| `RTE_SYS` | Tại `MTR_BESS` có cả aux, hoặc tại POC | `E_dis/(E_ch + E_aux)` nếu aux đo riêng | Kinh tế thực, hợp đồng hiệu suất. PNNL: loại aux làm RTE cao hơn khoảng 6–16% [FACT, Phát hiện #7] |

**Điều kiện tính RTE.**
- RTE chỉ có nghĩa khi năng lượng lưu đầu và cuối kỳ bằng nhau. [PROPOSAL] Có hai cách:
  - (a) Chỉ tính trên các cửa sổ mà `|SOC_end − SOC_start| ≤ 1%`.
  - (b) Hiệu chỉnh gần đúng: `RTE ≈ E_dis/(E_ch − ΔSOC·E_usable/η_ch,est)`. Gắn cờ `APPROX_SOC_CORRECTED`, vì SOC có sai số (§3.6).
- Theo tháng, sai số do ΔSOC thường nhỏ so với tổng throughput. [INFERENCE]
- Một tài liệu ôn thi PE viết RTE AC-AC = η_MBA × η_inverter × η_pin_DC × (hệ số tổn hao phụ trợ) và ước aux khoảng 2–4% — https://open-exam-prep.com/study-guides/pe-electrical-power/electric-power-devices-renewables/battery-storage-bess-ultracapacitors (qua kết quả tìm kiếm; nguồn thứ cấp, độ tin thấp). Không dùng con số này làm mặc định sản phẩm.

**Tải phụ trợ (aux).**
- [FACT] Trong thử nghiệm PNNL MESA-1, aux khoảng 30 kW trên hệ 1.000 kWh khi chạy. RTE thấp nhất vào mùa hè do aux cao, tức là HVAC phụ thuộc mùa/nhiệt độ — https://www.sandia.gov/ess-ssl/wp-content/uploads/2019/07/PNNL-MESA-1-Final-Test-Report_Reduced.pdf (qua kết quả tìm kiếm).
- Một thiết kế đại học trích định mức aux đỉnh 38 kVA/container (BYD), cấp cho HVAC, thông tin liên lạc, báo cháy — https://sddec24-18.sd.ece.iastate.edu/One-line.pdf (qua kết quả tìm kiếm).
- [INFERENCE] Ở khí hậu Việt Nam (nóng ẩm), aux của container BESS là đáng kể kể cả khi pin đứng yên. Vì vậy:
  - Tiêu thụ standby phải là một KPI riêng (`E_aux_idle` kWh/ngày).
  - Bộ tối ưu phải tính chi phí giữ pin "sẵn sàng".
  - Nếu aux lấy nguồn sau `MTR_BESS`, ban đêm `p_bess` hơi âm khi pin đứng yên. Đây không phải "đang sạc"; trạng thái phải lấy từ PCS/BMS, không suy từ dấu P.
- [UNKNOWN] Giá trị aux điển hình của BESS C&I 100 kWh–5 MWh tại Việt Nam: cần datasheet hoặc số đo thực địa.

**Tổn hao PV.** PR (§3.11) gom mọi tổn hao (nhiệt, bụi, mismatch, inverter, clipping, curtailment). EMS nên tách **curtailment do điều khiển** (export limit) ra khỏi tổn hao kỹ thuật, vì đây là quyết định vận hành chứ không phải lỗi thiết bị.

### 3.6 Kiến thức pin tối thiểu cho EMS

| Khái niệm | Định nghĩa vận hành | Nguồn giá trị | Ghi chú cho EMS |
|---|---|---|---|
| **SOC** (State of Charge) | % năng lượng/điện tích còn lại so với dung lượng hiện tại (hoặc khả dụng, tùy hãng) | BMS | Phải biết SOC hãng báo là "SOC tuyệt đối" hay "SOC trong cửa sổ khả dụng" (0% có thể = 5% thật). Lưu `soc_basis` trong mô hình thiết bị |
| **SOH** (State of Health) | Thường là dung lượng hiện tại/dung lượng danh định (%). Có hãng dùng điện trở trong | BMS; hoặc EMS ước lượng | Không chuẩn hóa giữa các hãng. Không so SOH giữa hai hãng như cùng thước đo [INFERENCE] |
| **DoD** (Depth of Discharge) | `1 − SOC` hoặc độ sâu một chu kỳ = `SOC_max − SOC_min` của chu kỳ đó | Tính | Đếm chu kỳ cần thuật toán (ví dụ rainflow) nếu muốn mô hình lão hóa theo DoD |
| **C-rate / P-rate** | Dòng (A) / dung lượng (Ah); với BESS thường dùng `P/E` (kW/kWh), ví dụ 0,5C = xả hết trong 2 h | Datasheet | Giới hạn công suất liên tục và đỉnh. Phụ thuộc nhiệt độ và SOC |
| **Danh định và khả dụng** | `E_nom` = Ah × V danh định. `E_usable` = năng lượng lấy ra được trong cửa sổ SOC cho phép, ở công suất và nhiệt độ quy định | Datasheet + nghiệm thu | Lưu cả `e_nominal_kwh`, `e_usable_kwh_bol` (đầu đời), `e_usable_kwh_current` (ước lượng). Tối ưu và báo cáo dùng **khả dụng hiện tại** |
| **EFC** (Equivalent Full Cycles) | `EFC = Σ E_dis / E_ref` | Tính | **Phải ghi `E_ref`**: dung lượng danh định, khả dụng đầu đời hay khả dụng hiện tại; đo DC hay AC. Bảo hành thường giới hạn theo chu kỳ hoặc throughput [UNKNOWN điều khoản cụ thể từng hãng] |
| **Throughput** | `Σ E_dis` (hoặc `Σ (E_ch + E_dis)/2`) MWh | Tính | Cơ sở chi phí lão hóa trong tối ưu (VND/kWh throughput) |
| **Lão hóa lịch** (calendar) | Mất dung lượng theo thời gian, phụ thuộc nhiệt độ và SOC lưu trữ | Mô hình | Mô hình thường cộng tách lịch + chu kỳ — https://sunlithenergy.com/?p=6409 (qua kết quả tìm kiếm). LFP ở 55 °C, SOC cao thì suy giảm mạnh hơn — https://pubs.rsc.org/en/content/articlehtml/2025/ta/d5ta03813h (qua kết quả tìm kiếm) |
| **Lão hóa chu kỳ** (cycle) | Mất dung lượng theo throughput | Mô hình | Với LFP, phụ thuộc yếu vào DoD và C-rate, mạnh vào nhiệt độ (theo tổng quan tài liệu trích bởi Okra) — https://www.okrasolar.com/blog/a-better-way-to-estimate-battery-lifetime (qua kết quả tìm kiếm; độ tin trung bình) |
| **Giới hạn điện áp cell LFP** | Ví dụ 2,5–3,65 V/cell; sạc 0–55 °C, xả −20 °C… (một datasheet cell) | Datasheet cell | Power-Sonic LFP: cắt sạc 3,65 V, cắt xả khuyến nghị 2,5 V, sạc 0–55 °C — https://cdn.power-sonic.com/documents/PSL-FP-IFP30135185EC_Data_Sheet.pdf (qua kết quả tìm kiếm). **Đây là việc của BMS.** EMS chỉ hiển thị và cảnh báo xu hướng (chênh lệch cell, max/min cell V) |
| **Giảm công suất theo nhiệt độ** (derating) | BMS/PCS hạ giới hạn khi nhiệt độ cell/môi trường ra ngoài dải | BMS (CCL/DCL), PCS | EMS phải đọc giới hạn **động**. Không dùng giới hạn tĩnh trong datasheet để lập lịch ngắn hạn |
| **Trôi SOC / hiệu chỉnh** | Sai số coulomb counting tích lũy. BMS hiệu chỉnh ở đầu/cuối dải hoặc khi nghỉ đủ lâu (OCV đáng tin sau 30–60 phút nghỉ) | BMS | Phát hiện #8. [PROPOSAL] Lịch "sạc đầy cân bằng/hiệu chỉnh" định kỳ là chức năng của bộ lập lịch (do hãng khuyến nghị), có chi phí trong tối ưu |

**Hệ quả.**
- [PROPOSAL] Năng lượng khả dụng cho lập lịch: `E_avail_dis = (SOC − SOC_min_eff)·E_usable_current·η_dis` và `E_avail_ch = (SOC_max_eff − SOC)·E_usable_current/η_ch`. Trong đó `SOC_min_eff = max(SOC_min_vendor, SOC_backup_reserve, SOC_min_user)`.
- [PROPOSAL] Có hai mức SOC dự phòng tách biệt:
  - (1) giới hạn bảo vệ của hãng (bất khả xâm phạm, chỉ đọc);
  - (2) dự phòng vận hành của khách (ví dụ giữ 30% cho mất điện), cấu hình được, có audit.

### 3.7 Phân vai BMS / PCS / EMS (và PPC, edge, cloud)

| Lớp | Trách nhiệm | Thời gian đáp ứng (bậc độ lớn) [INFERENCE] | EMS được làm gì |
|---|---|---|---|
| **BMS** | Đo cell V/T/I; ước lượng SOC/SOH; cân bằng cell; tính và công bố giới hạn (CCL/DCL, CVL, max P sạc/xả); mở contactor; cảnh báo/lỗi | ms–s | **Chỉ đọc** giới hạn và trạng thái; reset lỗi chỉ khi hãng cho phép và qua quy trình có người xác nhận |
| **PCS / inverter** | Chuyển đổi DC↔AC; thực thi setpoint P/Q; bảo vệ lưới (chống tách đảo, ride-through, quá/thiếu áp-tần); tôn trọng giới hạn BMS (qua CAN/RS485 trực tiếp với BMS) | ms–100 ms | Gửi setpoint P/Q và chế độ trong giới hạn; **không** đổi thông số bảo vệ grid code |
| **Bộ điều khiển site (edge EMS / PPC)** | Vòng kín theo `MTR_POC`: zero-export, export limit, import cap, PF; kẹp setpoint; fallback khi mất kết nối cloud | 100 ms–vài s | Đây là "EMS thời gian thực" của sản phẩm |
| **Cloud EMS** | Dự báo, tối ưu lịch (15–30 phút), biểu giá, KPI, báo cáo, cảnh báo, đa site | phút–giờ | Gửi **lịch/mục tiêu có thời hạn** xuống edge; không gửi lệnh trực tiếp tới PCS bỏ qua edge |

**Chuỗi giới hạn (limit chain) tại edge [PROPOSAL]** — tính mỗi chu kỳ điều khiển:

```
P_dis_max = min( BMS_max_discharge_kW (hoặc DCL·V_bat),
                 PCS_rated_kW · derate_temp_pcs,
                 √(S_pcs² − Q_cmd²),
                 export_headroom = P_load_now + EXPORT_LIMIT − P_pv_now  [nếu cấm BESS xuất],
                 user/contract limit )
P_ch_max  = min( BMS_max_charge_kW (CCL·V_bat), PCS limits, import_headroom = IMPORT_CAP − (P_load_now − P_pv_now), … )
P_cmd = clamp(P_request_from_schedule, −P_ch_max, +P_dis_max)
Nếu SOC ≤ SOC_min_eff → P_cmd = min(P_cmd, 0); nếu SOC ≥ SOC_max_eff → P_cmd = max(P_cmd, 0)
Nếu dữ liệu BMS cũ hơn T_stale (ví dụ 5 s) hoặc BMS báo lỗi → P_cmd = 0 (hoặc chế độ an toàn hãng khuyến nghị)
Nếu lịch cloud hết hạn (expiry) → chế độ fallback cấu hình sẵn (ví dụ self-consumption + export limit)
```

- [FACT] Tham khảo OpenEMS: PR #3973 kẹp setpoint `SellToGridLimit` về 0 vì controller sinh giá trị âm ghi vào thanh ghi unsigned — https://github.com/OpenEMS/openems/pull/3973 ; https://github.com/OpenEMS/openems/issues/3972 (qua kết quả tìm kiếm). [INFERENCE] Đây là bằng chứng rằng kẹp và kiểm tra kiểu dữ liệu phải có ở **lớp ghi thanh ghi** của driver, không chỉ ở bộ điều khiển.
- [FACT] SunSpec có họ model 800 cho lưu trữ, model 802 là Battery Base Model (bản draft) — https://sunspec.org/wp-content/uploads/2019/08/SunSpec-Alliance-Specification-Energy-Storage-ModelsD4rev0.pdf (qua kết quả tìm kiếm). [UNKNOWN] Tên và offset thanh ghi cụ thể: chưa đọc spec.
- [FACT] Giao thức CAN BMS–inverter kiểu Pylontech mã hóa DCL 16 bit, độ phân giải 0,1 A, tối đa khoảng 3.276,7 A. Spec CAN của Victron không công bố công khai — https://communityarchive.victronenergy.com/questions/310041/maximum-limit-of-dcl-and-ccl-numbers.html (qua kết quả tìm kiếm). [INFERENCE] Driver phải kiểm tra tràn số và hệ số tỷ lệ của giới hạn.

### 3.8 Ràng buộc đấu nối lưới

| Ràng buộc | Đại lượng / đơn vị | Đo ở đâu | Cách EMS xử lý | Bằng chứng |
|---|---|---|---|---|
| Công suất hợp đồng / định mức MBA | kW hoặc kVA | `MTR_POC` | `IMPORT_CAP` mềm (cảnh báo) và cứng (cắt giảm sạc BESS/EV, xả BESS) | A-market-boundary D-12 |
| Giới hạn xuất tức thời | kW (0 = zero export) | `MTR_POC`, vòng kín ở edge/inverter | Hãng inverter có sẵn: Huawei cần smart meter, controller là inverter hoặc SmartLogger (nghiên cứu FusionSolar trước). EMS **không** thay thế chức năng chống phát ngược đã chứng nhận; chỉ đặt tham số hoặc bổ sung | NĐ 58 yêu cầu thiết bị chống phát ngược nếu không bán điện (tóm tắt thứ cấp) — https://storage-vnportal.vnpt.vn/gov-tnn/7350/FileQuanTriTinTuc/VBHN%2052%20Nghi%20dinh%2058%20va%20ND%20243%2030.6.pdf (qua kết quả tìm kiếm) |
| Ngân sách xuất theo điện năng | kWh/kỳ ≤ 50% × E_pv (NĐ 243, theo báo chí) | `MTR_POC` (xuất), `MTR_PV` | Theo dõi lũy kế trong kỳ; khi gần chạm thì hạ giới hạn xuất tức thời | Phát hiện #6 |
| Hệ số công suất | cosφ ≥ 0,9 tại điểm đo đếm (TT 05/2025 Đ.31) | `MTR_POC` (P, Q) | Tính PF bình quân theo kỳ: `PF = E_P/√(E_P² + E_Q²)` theo kvarh nhập; cảnh báo; P2: điều khiển Q bằng PCS (PCS có dư kVA) | Phát hiện #5 |
| Ramp rate | kW/phút hoặc %/phút | POC | [UNKNOWN] cho C&I Việt Nam. Thiết kế tham số `ramp_limit` cho mọi setpoint | — |
| Chống tách đảo (anti-islanding) | Thời gian ngắt (s) | Inverter/PCS | **Chức năng bảo vệ của thiết bị.** IEC 62116 là phương pháp thử, không đặt ngưỡng; ngưỡng do grid code | Phát hiện #15 |
| Ride-through điện áp/tần số | Dải V, Hz và thời gian | Inverter/PCS | Chỉ đọc cấu hình grid code của thiết bị, so với hồ sơ; cảnh báo khi khác | Phát hiện #13 |
| Hệ thống cũ / tham chiếu | Trước 2025, báo cáo kỹ thuật 2020 cho gió/PV: PF 0,95 (thiếu kích thích)/0,85 (quá kích thích) khi P > 20% | — | Chỉ dùng tham chiếu lịch sử | http://vepg.vn/wp-content/uploads/2020/03/81241566_Final-Report-of-Technical-code-revision_EN.pdf (qua kết quả tìm kiếm) |

**Vì sao PF tại POC giảm khi có PV/BESS [INFERENCE, vật lý cơ bản].**
- Ví dụ: tải 1.000 kW, 600 kvar (PF 0,857, chưa tính tụ bù).
- PV cấp 700 kW ở PF = 1. Khi đó P_grid = 300 kW, Q_grid = 600 kvar, nên PF tại POC = 300/√(300² + 600²) ≈ 0,447.
- Như vậy, dù tải không đổi, PF đo tại POC xuống dưới 0,9.
- EMS phải cảnh báo, và (P2) dùng khả năng phát Q của PCS/inverter nếu hợp đồng cho phép.

### 3.9 Biểu giá: TOU, demand và chu kỳ đo

**TOU.** Theo A-market-boundary (Phát hiện #4): khung QĐ 963/QĐ-BCT có cao điểm 17h30–22h30 T2–T7 và thấp điểm 0h–6h. Ngày áp vào hóa đơn chưa rõ. [PROPOSAL, chuyển cho M-TAR]
- Mỗi chu kỳ đo được gán một "bậc giá" theo **giờ địa phương của site** (wall-clock).
- Chu kỳ nào cắt ngang ranh giới khung giờ thì tách theo phút (nếu có dữ liệu 1 phút) hoặc gán theo quy ước công tơ. [UNKNOWN] Công tơ EVN gán chu kỳ 30 phút cắt ngang 17h30 thế nào. Với cửa sổ 30 phút thẳng hàng :00/:30 thì 17h30 là biên, nên không cắt ngang.

**Demand (Việt Nam, giá hai thành phần).**
- `Pmax_tháng = max_k [E_imp(k)/0,5 h]` trên các cửa sổ 30 phút [FACT, Phát hiện #3].
- [INFERENCE] Cửa sổ có lẽ là block cố định thẳng hàng đồng hồ (:00–:30, :30–:00), vì công tơ lưu load profile theo chu kỳ. [UNKNOWN] Xác nhận block hay rolling; Pmax tính theo mọi giờ hay chỉ một số khung; và có tính trên nhập lưới (không trừ xuất) hay không. [INFERENCE] Phải tính trên **nhập**, không phải net.
- Nước khác: Đức dùng trung bình 15 phút lớn nhất năm (Berlin) [FACT]; Mỹ thường 15 phút theo nguồn vendor (A-market-boundary #35). [PROPOSAL] Tham số `demand_window_min ∈ {5, 15, 30, 60}`, `demand_window_type ∈ {block, rolling(sub_interval)}`, `demand_ratchet` (lấy max nhiều tháng) cho tenant ngoài Việt Nam.

**Bộ điều khiển cửa sổ demand (thuật toán cho edge) [PROPOSAL].**
- Gọi `T_w` là độ dài cửa sổ, `t` là thời gian đã trôi trong cửa sổ, `E_so_far` là điện năng nhập đã dùng, `P_target` là mục tiêu Pmax.
- Công suất nhập trung bình còn được phép trong phần còn lại của cửa sổ:

```
P_allow_rest = (P_target · T_w − E_so_far) / (T_w − t)
```

- Ví dụ: T_w = 30 phút, P_target = 1.000 kW. Sau 20 phút đã nhập 360 kWh (trung bình 1.080 kW), nên 10 phút còn lại được phép (500 − 360)/(1/6 h) = **840 kW**.
- BESS xả bù phần `P_import_now − P_allow_rest`.
- Cách này tận dụng được việc vượt ngắn hạn mà không làm tăng Pmax. Nó tốt hơn ngưỡng tức thời cố định, vốn xả BESS nhiều hơn mức cần thiết.
- [INFERENCE] Đồng hồ edge phải đồng bộ với ranh giới cửa sổ của công tơ thanh toán (NTP; sai lệch vài giây chấp nhận được, sai lệch vài phút thì không).

**Tiết kiệm (savings).**
- [PROPOSAL] "Tiết kiệm" luôn là chênh lệch giữa **hóa đơn thực tế (bóng)** và **hóa đơn baseline phản thực** (không PV/không BESS, hoặc không điều khiển), cùng một phiên bản biểu giá.
- Baseline phản thực dùng `E_cons` tính từ (5). Đây là INFERENCE/mô hình, không phải đo, và phải ghi rõ trên báo cáo.

### 3.10 Self-consumption, self-sufficiency

Các nguồn không thống nhất công thức chi tiết. Ví dụ, nPro dùng nhập/sản lượng; Aurora định nghĩa autarky = điện PV cấp (trực tiếp hoặc qua pin)/tiêu thụ — https://www.npro.energy/main/en/help/self-sufficiency-rate ; https://help.aurorasolar.com/hc/en-us/articles/45485868561427-What-is-Autarky (qua kết quả tìm kiếm). Điểm chung đã kiểm chứng [FACT]: self-consumption dựa trên **sản lượng**, self-sufficiency (autarky) dựa trên **tiêu thụ** — https://hilfe.autarc.energy/en/articles/10559274-what-is-the-self-consumption-rate (qua kết quả tìm kiếm).

**Định nghĩa của sản phẩm [PROPOSAL]**, mỗi KPI có hai biến thể, gắn tên rõ:

| KPI | Công thức "đơn giản" (không cần phân bổ) | Công thức "phân bổ" (cần §3.4) | Ghi chú |
|---|---|---|---|
| Tỷ lệ tự tiêu thụ PV (SCR) | `1 − E_exp/E_pv` | `(pv_to_load + pv_to_bess)/E_pv` | Bản đơn giản sai khi BESS xả ra lưới (xuất không phải PV) → chỉ dùng cho site không có BESS xuất lưới |
| Tỷ lệ tự cung (SSR, autarky) | `1 − E_imp/E_cons` | `(pv_to_load + bess_to_load_solar)/E_cons` | Bản đơn giản đúng cả khi BESS sạc từ lưới, vì năng lượng lưới đã nằm trong `E_imp`. Nếu `E_cons ≤ 0` → N/A |
| Tỷ lệ năng lượng tái tạo trong tiêu thụ | — | như SSR phân bổ | Dùng cho báo cáo ESG |

### 3.11 PV: specific yield, PR (IEC 61724-1)

- **Specific yield** `Yf = E_ac/P0` (kWh/kWp).
- **Reference yield** `Yr = H_POA/G_ref` (h), với `G_ref = 1 kW/m²` và `H_POA` (kWh/m²) là bức xạ tích lũy trên mặt phẳng tấm.
- **PR** `= Yf/Yr` [FACT, Sandia].
- **PR hiệu chỉnh nhiệt độ** (dạng phổ biến; hệ số cụ thể phải đối chiếu IEC 61724-1:2021 [UNKNOWN văn bản gốc]):

```
PR_T = Σ_k E_ac(k) / Σ_k [ P0 · (G_POA(k)/G_ref) · (1 + γ·(T_mod(k) − 25 °C)) · Δt ]
γ: hệ số nhiệt công suất của module (ví dụ −0,0035/°C, lấy theo datasheet module)
```

**Quy tắc thực thi [PROPOSAL].**
- PR **bắt buộc** cần cảm biến bức xạ POA. Không có cảm biến thì hiển thị "N/A", không hiển thị 0 (FusionSolar demo hiển thị 0,00 khi không có cảm biến — nghiên cứu FusionSolar trước, `demo_observations.md`).
- Nếu dùng bức xạ vệ tinh hoặc GHI chuyển đổi thì đặt tên khác (`PR_sat`) và ghi "không theo IEC 61724-1".
- Loại khỏi tử số và mẫu số các chu kỳ: inverter bị curtail (export limit active, P_cmd < P_avail), lưới mất điện, dữ liệu thiếu. Báo cáo cả PR thô và PR loại trừ, kèm % thời gian bị loại.
- Lọc ngưỡng bức xạ thấp (ví dụ G < 50 W/m²) cho PR theo chu kỳ ngắn. Ngưỡng là tham số.
- Cấp giám sát: Class A cho utility/C&I lớn, Class B cho mái nhà/C&I nhỏ–vừa [FACT, Hukseflux]. [UNKNOWN] Yêu cầu chu kỳ lấy mẫu/ghi theo bản 2021: chưa kiểm chứng. Không tuyên bố "Class A/B" cho sản phẩm.

### 3.12 Availability

Theo IEC TS 63019:2019 (khung, công thức chuẩn hóa) — chưa đọc văn bản gốc [UNKNOWN chi tiết]. Đề xuất cấu trúc [PROPOSAL]:

| KPI | Công thức | Lưu ý |
|---|---|---|
| Availability theo thời gian (PV) | `A_t = T_available/(T_period − T_excluded)`, chỉ tính giờ có bức xạ > ngưỡng | "Available" = thiết bị không lỗi, sẵn sàng phát. Loại trừ: lưới mất điện, chủ đầu tư yêu cầu dừng, bất khả kháng (danh mục cấu hình theo hợp đồng) |
| Availability theo điện năng (PV) | `A_E = E_actual/(E_actual + E_lost_unavailable)` | `E_lost` ước lượng từ mô hình (bức xạ × P0 × PR kỳ vọng). Đánh dấu ESTIMATED |
| Availability BESS | `A_bess = T(BESS sẵn sàng ≥ x% P_rated và ≥ y% E_usable)/T_period` | x, y theo hợp đồng. Giới hạn do derate nhiệt độ có tính là "không sẵn sàng" không thì hợp đồng quyết định |
| Availability truyền thông (data availability) | `số mẫu nhận/số mẫu kỳ vọng` | **Khác** availability thiết bị. Mất kết nối không có nghĩa thiết bị dừng |

Để tham khảo, một glossary vendor viết: "Availability = giờ vận hành ban ngày/tổng giờ ban ngày" (giản lược; không phải chuẩn) — https://www.heavengreenenergy.com/glossary/availability-factor (qua kết quả tìm kiếm).

### 3.13 Phát thải carbon

- **Hệ số** (§2 Phát hiện #4): 2022 = 0,6766; 2023 = 0,6592 tCO2/MWh (chính thức); 2024 ≈ 0,681 tCO2e/MWh (nghiên cứu, chưa chính thức); 2025 ≈ 0,6235 (ước tính).
- **[UNKNOWN] Bản chất hệ số** (biên vận hành OM, biên xây dựng BM hay biên kết hợp CM theo phương pháp tín chỉ, hay hệ số trung bình lưới) và **phạm vi** (CO2 hay CO2e; có gồm tổn thất truyền tải không). Công văn 1726 yêu cầu áp dụng thống nhất cho các chương trình, dự án tín chỉ carbon và giảm nhẹ phát thải (snippet luatvietnam) → [INFERENCE] đây là hệ số dùng cho tính giảm phát thải dự án. Còn Scope 2 location-based theo GHG Protocol có thể cần hệ số trung bình. Phải đối chiếu văn bản gốc.
- **Công thức [PROPOSAL]:**
  - Phát thải tránh được (PV) = `(E_pv − tổn hao nội bộ không đo) × EF` ≈ `E_pv × EF`. Phần xuất lưới vẫn thay thế điện lưới. Tách hai số "tự dùng" và "xuất" để tránh đếm trùng với bên mua.
  - Phát thải Scope 2 (location-based) = `E_imp × EF_năm`.
  - BESS sạc từ lưới rồi xả: không tạo "tránh phát thải". Tổn hao RTE làm tăng `E_imp`, nên tự động tăng Scope 2. [INFERENCE]
  - Năm áp hệ số: dùng hệ số của năm dữ liệu nếu đã công bố; nếu chưa thì dùng hệ số chính thức mới nhất, gắn cờ `PROVISIONAL_EF` và tính lại khi có hệ số mới (báo cáo có phiên bản).

### 3.14 Bảng công thức KPI

Ký hiệu chu kỳ: dữ liệu thô (raw, 1 s–5 phút) → chu kỳ chuẩn 5 phút (`k5`) → 15/30 phút → giờ → ngày (theo **giờ địa phương site**) → tháng/kỳ hóa đơn → năm. "Aggregation" là cách gộp từ chu kỳ nhỏ lên lớn. "DQ" là quy tắc chất lượng dữ liệu.

| # | KPI | Công thức | Đơn vị | Aggregation | Đầu vào bắt buộc | DQ (khi thiếu/không hợp lệ) |
|---|---|---|---|---|---|---|
| K01 | Điện nhập lưới | `Σ ΔE_imp` từ thanh ghi A+ | kWh | Tổng | `MTR_POC` thanh ghi nhập | Nếu có thanh ghi trước/sau khoảng trống: tổng khoảng trống **đúng bằng** chênh thanh ghi; phân bổ trong khoảng theo profile (cờ `INTERPOLATED`). Nếu mất thanh ghi đầu/cuối: tích phân P (cờ `ESTIMATED_FROM_POWER`); không có gì thì `MISSING` |
| K02 | Điện xuất lưới | `Σ ΔE_exp` từ thanh ghi A− | kWh | Tổng | `MTR_POC` | Như K01 |
| K03 | Sản lượng PV | `Σ ΔE_pv` (AC) | kWh | Tổng | `MTR_PV` hoặc Σ inverter | Như K01. Nếu một inverter thiếu: tổng = Σ inverter có dữ liệu + ước lượng (tỷ lệ kWp × yield inverter cùng hướng), cờ `PARTIAL_ESTIMATED` |
| K04 | BESS sạc / xả | `Σ ΔE_ch`, `Σ ΔE_dis` | kWh | Tổng | `MTR_BESS`/PCS | Như K01. Ghi `boundary` |
| K05 | Tiêu thụ site | (5): `E_imp − E_exp + E_pv + E_dis − E_ch + E_gen` | kWh | Tổng (tính ở chu kỳ chuẩn rồi cộng) | K01–K04 | **Chỉ tính khi mọi đầu vào cùng chu kỳ đủ chất lượng.** Đầu vào nào ESTIMATED thì kết quả ESTIMATED; MISSING thì MISSING. Không ép âm về 0 |
| K06 | Tải nền | `E_cons − E_ev − E_aux` (nếu aux ngoài ranh giới BESS) | kWh | Tổng | K05, EV, aux | Như K05 |
| K07 | Công suất cửa sổ demand | `E_imp(window)/T_w` | kW | **Max** theo kỳ hóa đơn (không phải tổng/trung bình) | K01 ở độ phân giải ≤ T_w, thẳng hàng cửa sổ | Cửa sổ thiếu > x% dữ liệu → `UNCERTAIN`. Báo cáo Pmax kèm "số cửa sổ không chắc chắn". Không nội suy để tạo Pmax |
| K08 | Pmax theo khung giờ | K07 lọc theo khung TOU | kW | Max | K07, lịch TOU | Như K07 |
| K09 | Hệ số công suất bình quân | `E_P/√(E_P² + E_Q²)` với E_P = nhập, E_Q = kvarh nhập (Q1) | — | Tính lại từ tổng kWh/kvarh (**không lấy trung bình PF**) | Thanh ghi kvarh 4 góc phần tư | Không có kvarh thì tính từ P, Q lấy mẫu (cờ `ESTIMATED_FROM_POWER`) |
| K10 | Tỷ lệ tự tiêu thụ PV | `(pv_to_load + pv_to_bess)/E_pv` (hoặc bản đơn giản) | % | Tính lại từ tổng các thành phần, không lấy trung bình % | Phân bổ §3.4 | E_pv = 0 → N/A |
| K11 | Tỷ lệ tự cung | `1 − E_imp/E_cons` | % | Tính lại từ tổng | K01, K05 | E_cons ≤ 0 → N/A |
| K12 | Specific yield | `E_pv/P0` | kWh/kWp | Tổng E rồi chia | K03, P0 | P0 thay đổi trong kỳ (mở rộng) → dùng P0 theo thời gian (Σ E_k/P0_k) |
| K13 | PR (IEC 61724-1) | `Yf/Yr` | % | Tính lại từ ΣE_ac và ΣH_POA (không trung bình PR ngày) | E_ac, G_POA, P0 | Không có G_POA → N/A. Loại chu kỳ curtail/lưới mất/thiếu dữ liệu (cả tử và mẫu); báo cáo % bị loại. Coverage < ngưỡng (ví dụ 90%) → `LOW_COVERAGE` |
| K14 | PR hiệu chỉnh nhiệt độ | §3.11 | % | Như K13 | + T_mod, γ | Thiếu T_mod → không tính (không dùng T môi trường thay thế trừ khi có mô hình, cờ `MODELLED_TMOD`) |
| K15 | Điện năng bị curtail | `Σ (P_avail − P_actual)·Δt` khi đang giới hạn | kWh | Tổng | P_avail (từ inverter hoặc mô hình bức xạ) | P_avail từ mô hình → ESTIMATED |
| K16 | RTE (ranh giới X) | `E_dis/E_ch` (+aux) với ΔSOC ≈ 0 | % | Tính lại từ tổng | K04, SOC, aux | Cửa sổ ΔSOC > 1% → hiệu chỉnh gần đúng (cờ) hoặc loại. E_ch < ngưỡng tối thiểu → N/A |
| K17 | EFC | `Σ E_dis/E_ref` | chu kỳ | Tổng | K04, E_ref | Ghi E_ref và ranh giới. Thiếu dữ liệu xả → ước lượng từ ΔSOC × E_usable (cờ) |
| K18 | Throughput | `Σ E_dis` | MWh | Tổng | K04 | Như K04 |
| K19 | SOH (theo BMS) | giá trị BMS | % | Lấy giá trị cuối kỳ (last), không trung bình | BMS | Ghi `vendor_definition` |
| K20 | Dung lượng khả dụng ước lượng | Năng lượng xả từ SOC_max đến SOC_min trong chu kỳ kiểm tra / (ΔSOC) | kWh | Theo lần kiểm tra | K04, SOC | Chỉ tính khi chu kỳ đủ sâu (ΔSOC ≥ 60%, tham số) |
| K21 | Tiêu thụ phụ trợ | `Σ ΔE_aux`; chia idle/active | kWh, kWh/ngày | Tổng | `MTR_AUX` | Không có công tơ → N/A (không ước lượng mặc định) |
| K22 | Availability thời gian (PV/BESS) | §3.12 | % | Tính lại từ tổng thời gian | Trạng thái thiết bị, bức xạ | Thời gian mất kết nối: "không xác định", **không** tính là không sẵn sàng; báo riêng |
| K23 | Availability theo điện năng | §3.12 | % | Tính lại | + mô hình E_expected | ESTIMATED |
| K24 | Data availability | mẫu nhận/mẫu kỳ vọng | % | Tính lại | Metadata chu kỳ | — |
| K25 | Chi phí điện (hóa đơn bóng) | `Σ_k E_imp(k)·giá(bậc(k)) + Pmax·giá_cs + phạt PF (nếu có)` | VND | Tổng theo kỳ hóa đơn | K01, K07, K09, TariffVersion | Có chu kỳ MISSING → hóa đơn `INCOMPLETE`, hiển thị khoảng (min/max) |
| K26 | Doanh thu bán điện dư | `Σ E_exp(k)·giá_mua` (trong ngân sách 50% nếu áp dụng) | VND | Tổng | K02, hợp đồng | Như K25 |
| K27 | Tiết kiệm | `Hóa đơn_baseline − Hóa đơn_thực` | VND | Tổng | K05, biểu giá, baseline | Luôn ESTIMATED (baseline phản thực) |
| K28 | Phát thải tránh được | `E_pv·EF_năm` | tCO2(e) | Tổng | K03, EF | EF chưa chính thức → `PROVISIONAL_EF` |
| K29 | Phát thải Scope 2 | `E_imp·EF_năm` | tCO2(e) | Tổng | K01, EF | Như K28 |
| K30 | Tỷ lệ xuất so với PV (NĐ 243) | `E_exp_kỳ/E_pv_kỳ` | % | Tính lại theo kỳ | K02, K03 | [UNKNOWN mẫu số chính xác]. Hiển thị "lũy kế đến nay" và "dự báo cuối kỳ" |
| K31 | Residual cân bằng | (6) / E_cons | % | Tính lại | Đủ submeter | Dùng làm cảnh báo DQ, không phải KPI kinh doanh |
| K32 | Năng lượng EV | `Σ ΔE_ev` | kWh | Tổng | Trụ sạc/OCPP | OCPP MeterValues thiếu giữa phiên → nội suy theo thanh ghi đầu/cuối phiên |

**Quy tắc chung cho bảng [PROPOSAL].**
- (a) KPI dạng tỷ số luôn **tính lại từ tổng tử và mẫu**, không lấy trung bình các tỷ số.
- (b) Mỗi giá trị KPI mang `quality ∈ {MEASURED, INTERPOLATED, ESTIMATED, PARTIAL, MISSING, SUSPECT}`, `coverage_pct` và `calc_version`.
- (c) Chất lượng của KPI dẫn xuất bằng mức kém nhất của các đầu vào.
- (d) Tính lại hồi tố (backfill) khi dữ liệu trễ đến hoặc biểu giá/EF được cập nhật. Giữ lịch sử phiên bản báo cáo đã phát hành.

### 3.15 Chất lượng dữ liệu: thanh ghi, reset, khoảng trống, thời gian

**Thanh ghi tích lũy và chu kỳ.**

| Loại | Ví dụ | Cách lấy delta | Rủi ro |
|---|---|---|---|
| Tích lũy trọn đời (lifetime) | OBIS 1.8.0; inverter `total_yield` | `Δ = R(t) − R(t−1)` | Tràn số, reset khi thay công tơ hay cập nhật firmware, đổi hệ số CT |
| Tích lũy theo ngày | inverter `daily_yield` reset 00:00 **theo đồng hồ thiết bị** | Δ trong ngày; tại reset `Δ = R(t)` (nếu reset đúng 0) | Đồng hồ thiết bị lệch hoặc sai múi giờ khiến reset sai lúc; mất mẫu cuối ngày làm mất phần cuối |
| Chu kỳ (interval) | Load profile 30 phút của công tơ; API "5-min energy" | Dùng trực tiếp | Phải biết nhãn thời gian là **đầu hay cuối chu kỳ** |
| Công suất tức thời | P | Tích phân (dự phòng) | Aliasing; sai số lớn với tải dao động |

**Máy trạng thái tính delta cho thanh ghi tích lũy [PROPOSAL].**

```
Δ = R(t) − R(t_prev)
if Δ ≥ 0:
    if Δ ≤ P_max_plausible·(t − t_prev)·1,2 → OK
    else → SUSPECT_SPIKE (giữ lại, không dùng cho KPI cho đến khi xác nhận)
elif R(t_prev) > 0,9·R_wrap và R(t) < 0,1·R_wrap (R_wrap lấy từ cấu hình thiết bị) → ROLLOVER: Δ = R_wrap − R(t_prev) + R(t)
elif có sự kiện thay công tơ/reset đã ghi (asset event) → Δ = R(t) − R_new_start (ghi offset mới)
else → RESET_UNEXPLAINED: Δ không xác định; dùng tích phân P nếu có (cờ ESTIMATED_FROM_POWER) và sinh cảnh báo DQ
Luôn lưu cả giá trị thanh ghi thô (raw) để có thể tính lại.
```

- Cơ sở: cách xử lý rollover của Schneider và EnergyCAP [FACT, Phát hiện #12]. `P_max_plausible` lấy từ định mức thiết bị (kVA × hệ số).
- Thay công tơ hoặc thay CT là **sự kiện tài sản** có ngày giờ, thanh ghi cuối/đầu và tỷ số CT/VT mới. Không để pipeline tự "đoán".

**Khoảng trống dữ liệu.**
- Nhờ tính bảo toàn của thanh ghi tích lũy, khi edge mất kết nối nhưng thiết bị vẫn đếm, tổng năng lượng của khoảng trống vẫn **chính xác**. Chỉ phân bố trong khoảng là không biết.
- [PROPOSAL] Phân bố phần năng lượng đó theo profile tham chiếu (ví dụ bức xạ hoặc profile PV/tải cùng giờ của ngày tương tự), cờ `INTERPOLATED`. Điều này quan trọng cho TOU và demand: năng lượng phân bố sai khung giờ sẽ làm sai hóa đơn bóng. Vì vậy hóa đơn bóng của kỳ có khoảng trống được gắn `INCOMPLETE`.
- **Edge buffer:** edge lưu tạm (store-and-forward) dữ liệu thô tối thiểu N ngày (A/agent kiến trúc quyết định N) để giảm khoảng trống ngay từ nguồn.
- Không nội suy tuyến tính **công suất** qua khoảng trống dài hơn vài chu kỳ để tạo dữ liệu hiển thị như thật. Biểu đồ phải hiện khoảng trống.

**Timestamp và lệch thời gian.**
- [PROPOSAL] Mỗi mẫu có `ts_device` (nếu thiết bị cung cấp), `ts_edge_received` và `ts_ingested`. Thời gian chuẩn là `ts_device` nếu đồng hồ thiết bị được giám sát lệch ≤ ngưỡng (ví dụ 5 s); nếu không thì dùng `ts_edge_received`.
- Theo nghiên cứu FusionSolar trước: nên tách `measuredAt` khỏi `serverTime` (`source_code_clients_2.md`).
- **Căn chu kỳ:** quy mọi dữ liệu về lưới thời gian chuẩn (5 phút, nhãn = **cuối chu kỳ**, khoảng `(t−5', t]`). Mỗi driver khai báo nhãn gốc là đầu hay cuối chu kỳ. [UNKNOWN] Quy ước nhãn load profile công tơ EVN.
- **Đồng bộ giữa các thiết bị:** cân bằng (5) cộng dữ liệu của nhiều thiết bị. Lệch 1 chu kỳ giữa `MTR_POC` và `MTR_PV` sẽ sinh tải ảo dao động. Pipeline phải kiểm tra lệch pha bằng tương quan chéo trong ngày nắng (P_grid giảm khi P_pv tăng) và cảnh báo.

**Múi giờ / DST.**
- Lưu mọi thời điểm ở **UTC**. Site có thuộc tính `timezone` theo IANA (Việt Nam: `Asia/Ho_Chi_Minh`, UTC+7, không có DST).
- Ngày, tháng, khung TOU và kỳ hóa đơn tính theo **giờ địa phương của site**, không theo giờ server, giờ người xem hay giờ tenant.
- Với tenant có site ở vùng có DST: ngày chuyển giờ có 23 hoặc 25 giờ. Chu kỳ 01:00–02:00 có thể lặp hoặc biến mất. Lịch TOU định nghĩa theo wall-clock, nên giờ lặp được tính hai lần theo đúng giá của nó. Báo cáo theo giờ dùng nhãn có offset (`2026-10-25T02:00+01:00`).
- FusionSolar có cờ `showDst` trong API lịch sử (nghiên cứu FusionSolar trước) → [INFERENCE] đây là vấn đề thực tế với nền tảng đa quốc gia.
- Thiết bị có reset "theo ngày" bằng đồng hồ nội bộ sai múi giờ (ví dụ cài UTC) sẽ reset lúc 07:00 giờ Việt Nam. Driver phải phát hiện: reset `daily_yield` không gần 00:00 địa phương → cảnh báo cấu hình thời gian.

---

## 4. Hệ quả thiết kế cho sản phẩm

| Mã | PROPOSAL | Module | Ưu tiên đề xuất | Cơ sở |
|---|---|---|---|---|
| C-P01 | Quy ước dấu phương án A (lưới + = nhập, BESS + = xả); tên trường mang hướng; điện năng lưu theo cặp không âm; driver khai báo `sign_convention`; phép thử dấu khi commissioning | M-INT, M-MON, M-BESS, M-GRID | P0 | §3.2 |
| C-P02 | Danh mục điểm đo chuẩn (`MTR_POC`, `MTR_POC_LV`, `MTR_PV`, `MTR_BESS`, `MTR_AUX`, `MTR_LOAD_i`, `MTR_EV_i`, `MTR_GEN`) với thuộc tính `boundary`, `accuracy_class`, `ct_ratio`, `vt_ratio`, `aux_inside_boundary` | M-ORG (asset), M-INT | P0 | §3.3 |
| C-P03 | Bộ tính cân bằng năng lượng (5) ở chu kỳ chuẩn và kiểm tra residual (6) làm cảnh báo DQ | M-HIST, M-ALM | P0 (cân bằng), P1 (residual) | §3.4 |
| C-P04 | Thuật toán phân bổ luồng có phiên bản, tính ở chu kỳ thô; P1 thêm sổ cái nguồn gốc năng lượng trong pin (solar/grid share) | M-HIST, M-REP | P0 (phân bổ), P1 (sổ cái) | §3.4, NĐ 243 |
| C-P05 | RTE với `rte_boundary` (DC/AC_PCS/SYS), chỉ tính trên cửa sổ ΔSOC ≈ 0 | M-BESS | P1 | §3.5 |
| C-P06 | Mô hình pin: `e_nominal`, `e_usable_bol`, `e_usable_current`, `soc_basis`, SOC dự phòng hai tầng (hãng chỉ đọc / khách cấu hình có audit), EFC có `E_ref` | M-BESS | P0 | §3.6 |
| C-P07 | Limit chain tại edge (§3.7): kẹp theo BMS/PCS/lưới/SOC; dữ liệu BMS cũ thì P = 0; lịch cloud có hạn → fallback. Cloud không gửi lệnh trực tiếp tới thiết bị | M-OPT, M-BESS, M-SEC | P0 | §3.7 |
| C-P08 | Biểu giá có `demand_window_min`, `demand_window_type`, ratchet; mặc định Việt Nam 30 phút block (chờ xác nhận) | M-TAR | P0 (TOU), P1 (demand) | §3.9 |
| C-P09 | Bộ điều khiển cửa sổ demand theo `P_allow_rest` | M-OPT (edge) | P1 | §3.9 |
| C-P10 | Giám sát PF tại POC từ kvarh 4 góc phần tư; cảnh báo PF < 0,9; P2: điều khiển Q bằng PCS | M-GRID, M-ALM | P1 (giám sát), P2 (điều khiển) | §3.8 |
| C-P11 | Ngân sách xuất theo điện năng (lũy kế kỳ/50% PV) bên cạnh export limit tức thời | M-GRID, M-OPT | P1 (chờ văn bản gốc) | Phát hiện #6 |
| C-P12 | PR theo IEC 61724-1 chỉ khi có POA; PR loại trừ curtailment; K15 điện năng bị curtail | M-PV | P1 | §3.11 |
| C-P13 | Availability: thời gian, điện năng, BESS, data — tách bạch; danh mục loại trừ theo hợp đồng | M-PV, M-BESS, M-REP | P1 | §3.12 |
| C-P14 | Bảng hệ số phát thải có phiên bản (năm, giá trị, đơn vị, cơ quan, văn bản, trạng thái); tính lại khi có hệ số chính thức | M-REP | P1 | §3.13 |
| C-P15 | KPI engine: tỷ số tính lại từ tổng; mỗi giá trị mang `quality`, `coverage_pct`, `calc_version`; backfill có phiên bản báo cáo | M-HIST, M-REP | P0 | §3.14 |
| C-P16 | Máy trạng thái delta cho thanh ghi tích lũy (rollover/reset/spike), sự kiện thay công tơ là asset event; lưu raw | M-INT, M-HIST | P0 | §3.15 |
| C-P17 | Thời gian: UTC + IANA timezone của site; ngày/TOU/kỳ hóa đơn theo giờ site; ba timestamp; nhãn cuối chu kỳ; phát hiện lệch đồng hồ thiết bị | M-INT, M-HIST, M-TAR | P0 | §3.15 |
| C-P18 | Không hiển thị 0 khi không đo được (N/A); biểu đồ hiện khoảng trống; số ước lượng có nhãn | M-DASH | P0 | §3.11, §3.15 |
| C-P19 | Không lớp phần mềm nào sửa thông số bảo vệ grid code/BMS; chỉ đọc, so với hồ sơ, cảnh báo khác biệt | M-SEC, M-GRID | P0 | §3.7, §3.8 |
| C-P20 | Aux BESS là KPI riêng (idle/active); bộ tối ưu tính chi phí standby | M-BESS, M-OPT | P1 | §3.5 |

---

## 5. Evidence ledger

| # | Claim | Source URL | Source type & date | Excerpt/paraphrase | Confidence | Conflicting evidence | Design implication |
|---|---|---|---|---|---|---|---|
| 1 | OpenEMS: lưới + = mua, − = bán; Consumption = Grid + Production + Storage | https://community.openems.io/t/can-consumptionactivepower-be-negative/321 | Diễn đàn cộng đồng (trích Javadoc), không rõ ngày (qua kết quả tìm kiếm) | "positive: buy-from-grid; negative: feed-to-grid" | Med–High | — | C-P01 |
| 2 | OpenEMS ESS: âm = sạc, dương = xả | https://openems.github.io/openems.io/openems/latest/edge/configuration.html | Tài liệu chính thức OpenEMS (qua kết quả tìm kiếm) | "Negative values for Charge; positive for Discharge" | Med–High | — | C-P01 |
| 3 | OBIS 1.8.0 = A+ nhập; 2.8.0 = A− xuất | https://www.wienernetze.at/o/document/ex129_sm_glossar_eng_v04_bf ; https://manuals.lobaro.com/configuration/obis-code-configuration | Tài liệu DSO/vendor (qua kết quả tìm kiếm) | như claim | High | Promotic ghi nhãn 2.8.0 là "(A+)", có lẽ lỗi | Lưu nhập/xuất tách; mapping OBIS |
| 4 | Không có chuẩn cộng đồng thống nhất về dấu nhập/xuất | https://community.openenergymonitor.org/t/is-there-a-standard-for-import-export-positive-negative-power-flow/15149 | Diễn đàn (qua kết quả tìm kiếm) | cộng đồng dùng nhập +, có dự án dùng xuất + | Med | — | Driver khai báo dấu |
| 5 | Huawei V7 `meterPower` + = xuất; client cộng đồng dùng 3 quy ước khác nhau | `docs/research/fusionsolar/04_ghi_chu_nghien_cuu/2_phan_ra_san_pham/source_code_clients_2.md` | Nghiên cứu FusionSolar trước (đọc mã nguồn) | như claim | High | — | Adapter Huawei nhân −1 |
| 6 | Pmax giá hai thành phần = công suất trung bình chu kỳ tích phân lớn nhất trong tháng; chu kỳ hiện là 30 phút | https://daibieunhandan.vn/trien-khai-thu-nghiem-gia-ban-le-dien-hai-thanh-phan-tu-thang-10-2025-10390577.html ; https://tapchicongthuong.vn/evn-xay-dung-he-thong-gia-ban-dien-hai-thanh-phan-264219.htm | Báo, 2025 (qua kết quả tìm kiếm) | "khoảng thời gian tích phân hiện nay đang là 30 phút" | Med–High | Lộ trình thí điểm khác nhau giữa các nguồn | C-P08, C-P09 |
| 7 | Thí điểm hai thành phần: khách ≥ 200.000 kWh/tháng; có nguồn nói ≥ 22 kV; mở rộng 8/2027 | https://vnexpress.net/de-xuat-thi-diem-gia-dien-hai-thanh-phan-tu-2026-4936558.html ; https://tuoitre.vn/tu-1-1-2026-khach-hang-su-dung-dien-tu-200-000-kwh-thang-tro-len-se-ap-gia-hai-thanh-phan-20250909101816204.htm | Báo, 2025 (qua kết quả tìm kiếm) | như claim | Med | Mốc bắt đầu 10/2025 vs 1/2026 | M-TAR P1 |
| 8 | Đức (Berlin): công suất tính tiền = trung bình 15 phút lớn nhất trong năm | https://www.stromnetz.berlin/files/globalassets/dokumente/entgelte/zugang/entgelte-01.01.2011/entgelte-lastgangkunden-b-2011.pdf | Biểu giá DSO, 2011 (qua kết quả tìm kiếm) | "highest quarter-hour average" | Med (cũ) | — | Tham số cửa sổ demand |
| 9 | EF lưới Việt Nam 2023 = 0,6592 tCO2/MWh (CV 1726/BĐKH-PTCBT); 2022 = 0,6766 | https://luatvietnam.vn/dien-luc/cong-van-1726-bdkh-ptcbt-2024-cong-bo-ket-qua-he-so-phat-thai-luoi-dien-viet-nam-425131-d6.html ; https://klinova.vn/latest-news/release-of-vietnams-2023-power-grid-emission-coefficient.html | Văn bản/tin, 2024 (qua kết quả tìm kiếm) | như claim | High | — | C-P14 |
| 10 | EF 2024 ước tính 0,681 tCO2e/MWh (HUST + Bộ NN&MT), chưa chính thức | https://vietnamnews.vn/environment/1716087/study-shows-coal-power-dominant-as-viet-nam-s-grid-emissions-climbed-in-2024.html | Báo, 04/2025 (qua kết quả tìm kiếm) | +3,2% so với 2023; than 49,5% | Med | Một nguồn ghi 0,6811 tCO2/MWh | `PROVISIONAL_EF` |
| 11 | Đến 01/2026 chưa công bố EF 2024, 2025; ước tính 2025 = 0,6235; thẩm quyền có thể chuyển sang BCT | https://doanhnghiepkinhtexanh.vn/uoc-tinh-he-so-phat-thai-khi-nha-kinh-cua-luoi-dien-viet-nam-2025-a43738.html | Báo, 01/2026 (qua kết quả tìm kiếm) | như claim | Low–Med | — | Q-C03 |
| 12 | TT 05/2025/TT-BCT Đ.31: cosφ ≥ 0,9 tại điểm đặt công tơ (khách SX-KD có trạm riêng hoặc ≥ 40 kW); truyền tải: 0,9 nhận / 0,98 phát | https://thuvienphapluat.vn/van-ban/Thuong-mai/Thong-tu-05-2025-TT-BCT-he-thong-truyen-tai-dien-phan-phoi-dien-do-dem-dien-nang-642994.aspx ; https://www.evn.com.vn/userfile/User/giangtcdl/files/2025/8/VBHN38-20250814160032345.pdf | Văn bản pháp luật/VBHN 08/2025 (qua kết quả tìm kiếm) | như claim | Med–High | Hai snippet mô tả đối tượng khác nhau | C-P10 |
| 13 | Ride-through và PF > 0,98 cho PV hạ áp theo TT 05/2025/QCVN 26:2025 | https://www.gkoisolar.com/solar-inverter-requirements-in-vietnam-2026/ | Blog vendor, 2026 (qua kết quả tìm kiếm) | 50–85% V trong 2 s; 48–49 Hz ≥ 30 phút | Low | Báo cáo 2020: PF 0,95/0,85 | Chỉ đọc/so sánh cấu hình |
| 14 | NĐ 243/2026: trần 50% điện dư; BESS tích từ ĐMTMN được tính; cơ sở "sản lượng thực phát" | https://xbsolar.vn/nghi-dinh-243-2026-nd-cp-chinh-thuc-cho-ban-50-dien-mat-troi-mai-nha/ ; https://anninhthudo.vn/cho-phep-ban-dien-mat-troi-mai-nha-du-thua-len-toi-50-post657682.antd | Báo/đơn vị tư vấn, 06/2026 (qua kết quả tìm kiếm) | như claim | Med | Mẫu số tỷ lệ chưa rõ | C-P11, C-P04 |
| 15 | Loại aux làm RTE đo được tăng khoảng 6–16% (PNNL) | https://www.pnnl.gov/main/publications/external/technical_reports/PNNL-27237.pdf | Báo cáo phòng thí nghiệm quốc gia Mỹ (qua kết quả tìm kiếm) | như claim | Med–High | — | C-P05 |
| 16 | Đặc tả Hy Lạp: RTE gồm HVAC, làm mát, BMS, tổn hao MBA/PCS, đo tại điểm đấu nối | https://www.rae.gr/wp-content/uploads/2023/06/H1_BESS-Installation-Safety-and-Performance-Specifications.pdf | Đặc tả cơ quan quản lý, 2023 (qua kết quả tìm kiếm) | như claim | Med | FENECON loại aux/MBA | `rte_boundary` |
| 17 | FENECON 2025: hiệu suất trung bình không gồm MBA và tiêu thụ phụ trợ | https://docs.fenecon.de/pdfs/industrial/2025/en/Wirkungsgrad_FENECON_Industrial_L_und_XL_EN.pdf | Tài liệu vendor 2025 (qua kết quả tìm kiếm) | như claim | Med | #16 | So datasheet ở ranh giới AC_PCS |
| 18 | MESA-1: aux ~30 kW trên hệ 1.000 kWh; RTE thấp nhất mùa hè do aux | https://www.sandia.gov/ess-ssl/wp-content/uploads/2019/07/PNNL-MESA-1-Final-Test-Report_Reduced.pdf | Báo cáo thử nghiệm PNNL (qua kết quả tìm kiếm) | như claim | Med | — | C-P20 |
| 19 | SOC LFP: OCV phẳng (~100 mV/60% SOC); coulomb counting trôi; ít chạm 0/100% trong vận hành 20–80% | https://www.accure.net/blogs/state-of-charge-soc-estimation-errors-for-lfp-batteries-can-exceed-15 ; https://www.clarke-energy.com/2026/lithium-iron-phosphate-bess-the-state-of-charge-challenge/ | Blog vendor 2024–2026 (qua kết quả tìm kiếm) | như claim | Med (vendor có lợi ích) | — | SOC là giá trị có bất định |
| 20 | BMS hạ CCL/DCL theo SOC, nhiệt độ, điện áp cell, điện trở; CCL có thể = 0 | https://www.orionbms.com/manuals/utility/bms_param_current_limit_status.html | Manual BMS (qua kết quả tìm kiếm) | như claim | High | — | Limit chain đọc giới hạn động |
| 21 | BMS bảo vệ/cân bằng; PCS chuyển đổi và thực thi; EMS quyết định điều độ; giới hạn BMS phải được PCS và EMS tôn trọng | https://deye.com/nl/blog/bms-vs-ems-vs-pcs-bess-components/ | Blog vendor (qua kết quả tìm kiếm) | ví dụ cap xả 220 kW | Med–High | — | §3.7 |
| 22 | InfinitePower: EMS quản lý BMS, PCS; điều khiển sạc/xả, giám sát, chẩn đoán lỗi, đánh giá hiệu suất | https://www.infinitepowerht.com/what-is-energy-management-system-ems-and-its-functions.html | Trang vendor (nguồn hạt giống) (qua kết quả tìm kiếm) | như claim | Med | — | Phạm vi EMS lưu trữ |
| 23 | Ampowr Cosmos: peak shaving theo giới hạn lưới, giám sát SOC, kích máy phát gas khi SOC thấp; chiến lược curtailment, self-consumption, trading; API đối tác "respecting safety and site constraints" | https://www.rfp.wiki/vendors/ampowr ; https://fme.nl/node/14547 | Aggregator/case study (qua kết quả tìm kiếm) | như claim | Low–Med | Không có tài liệu kỹ thuật gốc | Chuyển agent B; khẳng định mô hình "API ngoài trong ràng buộc an toàn" |
| 24 | LFP cell: cắt sạc 3,65 V, cắt xả 2,5 V, sạc 0–55 °C | https://cdn.power-sonic.com/documents/PSL-FP-IFP30135185EC_Data_Sheet.pdf | Datasheet cell (qua kết quả tìm kiếm) | như claim | High (cho cell đó) | Trina 587Ah: 2,0 V khi T ≤ 0 °C (snippet lỗi) | Ví dụ minh họa; giới hạn thực lấy từ BMS |
| 25 | Lão hóa = lịch + chu kỳ (mô hình cộng); LFP chu kỳ phụ thuộc mạnh nhiệt độ | https://sunlithenergy.com/?p=6409 ; https://www.okrasolar.com/blog/a-better-way-to-estimate-battery-lifetime | Blog (qua kết quả tìm kiếm) | như claim | Med | — | Chi phí lão hóa trong M-OPT |
| 26 | LFP 55 °C SOC cao suy giảm nhiều hơn | https://pubs.rsc.org/en/content/articlehtml/2025/ta/d5ta03813h | Bài báo khoa học 2025 (qua kết quả tìm kiếm) | như claim | High | Bessler 2022: không thấy pattern SOC rõ ở 180 Ah | Tránh giữ SOC cao lâu khi nóng (P2) |
| 27 | PR = Yf/Yr; Yr = H_POA/1 kW/m²; định nghĩa rating chưa xác định trong IEC 61724 (theo Sandia) | https://pvpmc.sandia.gov/modeling-guide/5-ac-system-output/pv-performance-metrics/performance-ratio/ | Sandia PVPMC (qua kết quả tìm kiếm) | như claim | High | — | K13 |
| 28 | IEC 61724-1:2021 còn Class A và B (C cũ → B) | https://www.hukseflux.com/uploads/inline/iec_61724-1_2021_version-what_is_new_v2403_0.pdf | Vendor cảm biến (qua kết quả tìm kiếm) | như claim | Med–High | — | Không tuyên bố class |
| 29 | Availability PV: khung IEC TS 63019:2019; 61724-3 là đánh giá điện năng | https://webstore.iec.ch/en/publication/25466 | IEC webstore (qua kết quả tìm kiếm) | như claim | Med | — | §3.12 |
| 30 | IEC 62116 là phương pháp thử chống tách đảo, không đặt ngưỡng ngắt | https://knowledge.bsigroup.com/products/test-procedure-of-islanding-prevention-measures-for-utility-interconnected-photovoltaic-inverters | Mô tả tiêu chuẩn BSI (qua kết quả tìm kiếm) | như claim | Med–High | infralens: "2 s" | Không tuyên bố thời gian ngắt |
| 31 | Rollover: ION mặc định 10.000.000 kèm bộ đếm; EnergyCAP chỉ coi là tràn khi giảm > 10% max | https://www.se.com/us/en/faqs/FA239195/ ; https://helpcenter.energycap.com/um/sa/types_of_readings | Vendor FAQ/help (qua kết quả tìm kiếm) | như claim | High | — | C-P16 |
| 32 | AC-coupled không cứu được năng lượng clip; DC-coupled thì được | https://arxiv.org/pdf/2605.14043 ; https://www.batterypowertips.com/?p=4501 | Bài báo/tin ngành (qua kết quả tìm kiếm) | như claim | Med–High | — | Topology T2/T3 |
| 33 | OpenEMS sửa lỗi controller ghi setpoint âm vào thanh ghi unsigned | https://github.com/OpenEMS/openems/issues/3972 ; https://github.com/OpenEMS/openems/pull/3973 | GitHub issue/PR (qua kết quả tìm kiếm) | clamp về 0 | High | — | Kẹp ở lớp driver |
| 34 | SunSpec model 802 = Battery Base Model (họ 800) | https://sunspec.org/wp-content/uploads/2019/08/SunSpec-Alliance-Specification-Energy-Storage-ModelsD4rev0.pdf | Spec draft SunSpec (qua kết quả tìm kiếm) | như claim | Med (draft) | — | Chuyển agent tích hợp |
| 35 | Self-consumption dựa trên sản lượng; self-sufficiency dựa trên tiêu thụ; công thức khác nhau giữa nguồn | https://hilfe.autarc.energy/en/articles/10559274-what-is-the-self-consumption-rate ; https://www.npro.energy/main/en/help/self-sufficiency-rate ; https://help.aurorasolar.com/hc/en-us/articles/45485868561427-What-is-Autarky | Help center vendor (qua kết quả tìm kiếm) | như claim | Med | Khác biệt công thức | Hai biến thể có tên rõ |
| 36 | DPPA ảo: giá thị trường xác định mỗi 30 phút | https://conventuslaw.com/featured-content/a-new-way-for-renewable-energy-developers-to-sell-their-electricity-in-vietnam-2/ | Luật sư (qua kết quả tìm kiếm) | như claim | Med | — | Chu kỳ chuẩn 30 phút cho dữ liệu đối soát |
| 37 | PV hạ áp/gió-PV (2020): PF 0,95 thiếu kích thích/0,85 quá kích thích khi P > 20% | http://vepg.vn/wp-content/uploads/2020/03/81241566_Final-Report-of-Technical-code-revision_EN.pdf | Báo cáo kỹ thuật 2020 (qua kết quả tìm kiếm) | như claim | Low (có thể đã bị thay) | TT 05/2025 | Chỉ tham chiếu |

---

## 6. Câu hỏi mở / UNKNOWN

| Mã | Câu hỏi | Vì sao quan trọng | Cách giải |
|---|---|---|---|
| Q-C01 | Cửa sổ 30 phút của Pmax là block thẳng hàng đồng hồ hay rolling? Tính trên nhập hay net? Áp mọi giờ hay theo khung? | Thuật toán peak shaving và tính hóa đơn bóng | Đọc quyết định/hướng dẫn thí điểm của BCT/EVN; xin mẫu hóa đơn song song từ khách thí điểm |
| Q-C02 | Load profile công tơ EVN: nhãn thời gian đầu hay cuối chu kỳ; có đọc được dữ liệu (DLMS/IEC 62056, cổng quang) cho EMS không | Đối soát công tơ điều khiển với công tơ thanh toán | Hỏi Điện lực; thử thực địa |
| Q-C03 | Hệ số phát thải 2024/2025 đã có văn bản chính thức chưa (đến 10/2026)? Cơ quan nào công bố? Là OM/BM/CM hay trung bình? | KPI ESG | Tra Cổng TTĐT Bộ Công Thương, Bộ NN&MT, Công báo |
| Q-C04 | NĐ 243: mẫu số "50%" là sản lượng PV đo ở đâu (đầu ra inverter hay công tơ riêng), kỳ tính tháng hay năm; BESS sạc từ lưới rồi xả ra có được tính không | C-P11, C-P04 | Đọc NĐ 243 và VBHN 52 gốc |
| Q-C05 | Phạt hoặc mua công suất phản kháng hiện hành (sau TT 05/2025) cho khách C&I: cách tính, kỳ, ngưỡng | K09, K25 | Đọc thông tư về mua bán công suất phản kháng hiện hành |
| Q-C06 | Ramp rate và yêu cầu điều khiển Q/PF cho hệ PV + BESS C&I (hạ áp, trung áp) theo TT 05/2025 và QCVN 26:2025 | Tham số `ramp_limit`, chế độ Q | Đọc văn bản gốc, hỏi Điện lực |
| Q-C07 | Đặc tả kỹ thuật thiết bị chống phát ngược theo NĐ 58 (thời gian đáp ứng, vị trí cảm biến, chứng nhận) | Ranh giới trách nhiệm EMS và thiết bị đã chứng nhận | Đọc NĐ 58, hướng dẫn của BCT/EVN |
| Q-C08 | Điều khoản bảo hành BESS phổ biến (EFC, throughput, SOC trung bình, nhiệt độ, chu kỳ/năm) của các hãng có mặt ở Việt Nam | Dữ liệu cần lưu để chứng minh tuân thủ bảo hành | Xin hợp đồng mẫu từ nhà phân phối |
| Q-C09 | Aux điển hình (idle/active, theo mùa) của BESS C&I 100 kWh–5 MWh ở khí hậu Việt Nam | Kinh tế BESS, bộ tối ưu | Datasheet và đo thực địa pilot |
| Q-C10 | Công thức chuẩn IEC 61724-1:2021 (PR hiệu chỉnh nhiệt độ, yêu cầu lấy mẫu) và IEC TS 63019 (availability) | Tuyên bố tuân thủ | Mua/đọc tiêu chuẩn |
| Q-C11 | Định nghĩa SOC/SOH của từng hãng BESS mục tiêu (tuyệt đối hay trong cửa sổ khả dụng; SOH dung lượng hay điện trở) | Hiển thị và tối ưu đúng | Đọc manual Modbus từng hãng (agent tích hợp) |

---

## 7. Vấn đề gửi agent khác

| Mã | Gửi | Vấn đề | Đề xuất |
|---|---|---|---|
| X-C01 | Người viết 05 (Domain), 07 (Tích hợp), 09 (UX); người tổng hợp | Nghiên cứu FusionSolar khuyến nghị "lưới + = xuất". Ghi chú này đổi thành **lưới + = nhập, BESS + = xả** (§3.2) | Dùng thống nhất trong data model, API, wireframe; ghi rõ là thay đổi có chủ đích. Trong UI dùng nhãn hướng ("Nhập lưới", "Xuất lưới") thay vì số có dấu |
| X-C02 | 08 (Tối ưu), M-OPT | Pmax Việt Nam là trung bình 30 phút; dùng bộ điều khiển `P_allow_rest` thay ngưỡng tức thời; chi phí aux standby và chi phí lão hóa theo throughput | Đưa vào mô hình tối ưu và edge controller |
| X-C03 | 08, M-GRID | Cần thêm **ngân sách xuất theo điện năng** (NĐ 243) ngoài export limit tức thời; điện xả BESS có thể tính vào điện dư | Thiết kế ràng buộc kỳ (tháng) trong tối ưu, chờ Q-C04 |
| X-C04 | 05 (Domain) | Cần thực thể: `MeasurementPoint` (boundary, ct/vt ratio, accuracy, aux_inside), `RegisterReading` (raw) + `IntervalEnergy` (delta, quality), `AssetEvent` (thay công tơ/CT), `TariffVersion` có tham số demand, `EmissionFactorVersion`, `AttributionRun(version)` | Mô hình hóa theo §3.3, §3.14, §3.15 |
| X-C05 | 07 (Tích hợp) | Mỗi driver khai báo `sign_convention`, đơn vị, nhãn đầu/cuối chu kỳ, `R_wrap`, nguồn timestamp; kiểm tra tràn số/hệ số tỷ lệ khi ghi setpoint (bài học OpenEMS #3972, Pylontech DCL 16 bit) | Thêm vào template driver và checklist commissioning (phép thử dấu) |
| X-C06 | 10 (An toàn) | Limit chain §3.7: dữ liệu BMS cũ thì P = 0; lịch cloud có hạn và fallback; cấm sửa thông số bảo vệ grid code/BMS từ cloud | Đưa thành NFR an toàn và test |
| X-C07 | 09 (UX/UI), wireframe | Hiển thị N/A (không phải 0) khi thiếu cảm biến/dữ liệu; hiện khoảng trống; nhãn "ước lượng"; PR thô so với PR loại trừ curtail; sơ đồ luồng dùng kết quả phân bổ có phiên bản | Áp vào dashboard và báo cáo |
| X-C08 | A (Thị trường) | Đồng ý với A về TOU (QĐ 963) và giá hai thành phần. Bổ sung: chu kỳ tích phân Pmax là 30 phút (nguồn ở ledger #6); cosφ ≥ 0,9 theo TT 05/2025 là ràng buộc thực tế với site PV lớn | Cập nhật D-12 thành "Pmax 30 phút" |
| X-C09 | B (Đối thủ) | Ampowr Cosmos và InfinitePower: chỉ có tài liệu marketing hoặc aggregator; không gán thuật toán hay tính năng chưa có tài liệu; InfinitePower có trang "AI-powered EMS" — https://www.infinitepowerht.com/ai-powered-ems-industrial-energy-storage.html (qua kết quả tìm kiếm). Chưa kiểm chứng đó là ML thật hay luật | Đánh giá "AI" thận trọng |
| X-C10 | Người viết 04 (Yêu cầu) | Các C-P01…C-P20 cần đổi sang mã `FR-<MODULE>-NNN`/`NFR-DATA-NNN` | Dùng bảng §4 làm nguồn |
