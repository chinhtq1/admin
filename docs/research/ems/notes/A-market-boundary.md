# A — Thị trường, phân khúc và ranh giới sản phẩm EMS

[← Mục lục](../index.html) · [00 Tóm tắt](../00-executive-summary.html) · [02 Thị trường](../02-market-and-competitor-analysis.html) · [04 Yêu cầu](../04-business-requirements.md) · [08 Tối ưu](../08-energy-optimization.md) · [11 Lộ trình](../11-mvp-and-roadmap.html) · [13 Rủi ro](../13-open-questions-and-risks.md) · [14 Nguồn](../14-source-register.md) · [15 Mô phỏng](../15-simulators-and-messaging.md)

- Tác giả: Agent A (Industry & Market Research + Product Boundary)
- Ngày: 2026-10-10 · Trạng thái: bản nghiên cứu v1, đầu vào cho các tài liệu 00, 02, 04, 11, 13
- Phương pháp: chỉ dùng WebSearch (fetch trực tiếp bị chặn). Mọi FACT lấy từ trang **qua kết quả tìm kiếm** (snippet/tóm tắt của công cụ tìm kiếm), trừ khi ghi "nghiên cứu FusionSolar trước" (đã đọc trong `docs/research/fusionsolar/04_ghi_chu_nghien_cuu/`). Chưa đọc toàn văn bất kỳ nghị định, thông tư hay datasheet nào. Số liệu pháp lý phải được đối chiếu văn bản gốc trước khi đưa vào yêu cầu bắt buộc.

---

## 1. Phạm vi & câu hỏi nghiên cứu

**Phạm vi.** Năm loại "EMS" mà thị trường gọi chung một tên (C&I EMS, renewable/solar management, BESS EMS, microgrid/DER EMS, utility/TSO SCADA/EMS) cộng hai loại liền kề (site monitoring & analytics; ISO 50001 enterprise energy management). Thị trường Việt Nam là trọng tâm. EU, Mỹ và Úc là bối cảnh so sánh.

**Câu hỏi nghiên cứu**

| # | Câu hỏi | Trả lời ở |
|---|---|---|
| RQ1 | Bảy nhóm sản phẩm khác nhau thế nào về định nghĩa, người mua, chức năng, độ trễ điều khiển và trách nhiệm an toàn? | §3.1, §3.2 |
| RQ2 | Ai là khách hàng/persona, và họ "thuê" sản phẩm để làm việc gì (JTBD)? | §3.3 |
| RQ3 | Động lực thị trường ở Việt Nam (Nghị định 135/2024 → 58/2025 → 243/2026, DPPA, biểu giá TOU, giá hai thành phần, BESS trong QHĐ8 điều chỉnh) và toàn cầu là gì? | §3.4, §3.5 |
| RQ4 | Giả định "bản đầu tiên là nền tảng C&I đa site: solar + BESS + lưới + phụ tải + EV tùy chọn" có đúng không? | §3.6 |
| RQ5 | Chọn **một** nhóm chính cho bản phát hành đầu. Vì sao không phải nền tảng sustainability/ESG, cũng không phải hệ điều khiển lưới cấp utility? | §3.7, §4 |

---

## 2. Phát hiện chính

1. **[FACT] Nghị định 135/2024 không còn là văn bản hiện hành.** Nghị định 58/2025/NĐ-CP (ban hành 03/03/2025) thay thế 135/2024 cho điện mặt trời mái nhà tự sản xuất, tự tiêu thụ (ĐMTMN TSXTTT). Nghị định 243/2026/NĐ-CP (26/06/2026, hiệu lực ngay) tiếp tục sửa 57/2025 và 58/2025. Trần bán điện dư tăng từ 20% lên **50% sản lượng thực phát**. Đến hết 31/12/2030 có thể bán vượt 50% nếu đơn vị vận hành lưới xác nhận lưới tiếp nhận được. Vùng chưa có lưới quốc gia không bị giới hạn. — https://theinvestor.vn/insight-into-vietnams-decree-58-on-renewable-and-new-energy-d14912.html ; https://luatvietnam.vn/tin-van-ban-moi/tu-26-6-2026-dien-mat-troi-mai-nha-duoc-ban-toi-da-50-san-luong-dien-du-186-109883-article.html ; https://www.reccessary.com/en/news/vietnam-solar-grid-export-dppa (qua kết quả tìm kiếm). Nghiên cứu FusionSolar trước (`market_users_vietnam.md` §5) dựa trên 135/2024 và mức 20% nên **đã lỗi thời**.
2. **[FACT] Điện năng xả từ BESS gắn với hệ ĐMTMN được tính vào phần điện dư được mua** theo tóm tắt Nghị định 243. — https://www.reccessary.com/en/news/vietnam-solar-grid-export-dppa (qua kết quả tìm kiếm). [INFERENCE] Hệ thống phải đo và quy kết được nguồn gốc năng lượng xuất lưới (PV trực tiếp hay BESS xả), không chỉ đo tổng P tại điểm đấu nối.
3. **[FACT] Thị trường thực tế gần như chọn "không bán điện dư".** Cuối 07/2026 có 28.254 hệ TSXTTT theo NĐ 58/243, khoảng 1.614 MWp. Chỉ khoảng 287 hệ (~16,4 MW) đăng ký bán điện dư. Toàn bộ ĐMTMN là 130.811 hệ, >11.200 MWp. — https://vietnamnet.vn/en/rooftop-solar-saves-billions-of-dong-but-one-bottleneck-remains-2552186.html (qua kết quả tìm kiếm). [INFERENCE] Với phần lớn khách C&I, bài toán vận hành chính là **giới hạn xuất lưới (zero-export / export limit)** cộng **tối đa tự tiêu thụ**, không phải bán điện.
4. **[FACT] Khung giờ TOU đã đổi theo Quyết định 963/QĐ-BCT (22/04/2026).**
   - Cao điểm: **17h30–22h30**, Thứ Hai–Thứ Bảy (5 h/ngày); Chủ nhật không có cao điểm.
   - Thấp điểm: **00h00–06h00** mọi ngày.
   - Bình thường: các giờ còn lại.
   - Khung cũ theo Thông tư 16/2014: cao điểm 9h30–11h30 và 17h–20h; thấp điểm 22h–4h.
   — https://tuoitre.vn/bo-cong-thuong-chinh-thuc-thay-doi-khung-gio-tinh-gia-dien-buoi-toi-la-gio-cao-diem-2026042410430101.htm ; https://thuvienphapluat.vn/van-ban/Tai-nguyen-Moi-truong/Quyet-dinh-963-QD-BCT-2026-khung-gio-cao-diem-thap-diem-cua-he-thong-dien-quoc-gia-703327.aspx (qua kết quả tìm kiếm). **[UNKNOWN]** Ngày khung mới thực sự áp vào hóa đơn sản xuất/kinh doanh vẫn chưa rõ. Một số nguồn tháng 7/2026 nói chưa áp dụng thực tế, nguồn khác nói đã áp dụng (xem Q-A01).
5. **[INFERENCE] Khung giờ mới làm tăng mạnh giá trị của BESS so với PV đơn thuần.** Cao điểm dời sang buổi tối, khi PV ≈ 0. PV không còn "ăn" được giờ cao điểm 9h30–11h30 như trước. Chênh lệch giá sản xuất cao điểm/thấp điểm theo QĐ 1279/QĐ-BCT là khoảng 2,8 lần, ví dụ <6 kV: 3.640 so với 1.300 đ/kWh (xem §3.4.3). Cách duy nhất để PV ban ngày "bán" vào giờ cao điểm là qua BESS.
6. **[FACT] C&I Việt Nam hiện chưa trả phí công suất (demand charge) kiểu Mỹ/EU.** Giá hai thành phần (kWh + kW công suất đăng ký) đang thí điểm cho khách sản xuất ≥200.000 kWh/tháng. Theo dự thảo: hóa đơn song song 01–06/2026, thí điểm thanh toán thật 07/2026–07/2027, mở rộng từ 08/2027. — https://tapchicongthuong.vn/thi-diem-ap-dung-gia-dien-hai-thanh-phan-tu-1-1-2026-218800.htm (qua kết quả tìm kiếm). **[UNKNOWN]** Trạng thái thực tế tháng 10/2026. [INFERENCE] "Peak shaving" ở Việt Nam hôm nay chủ yếu phục vụ: (a) giới hạn công suất máy biến áp/hợp đồng, (b) chuẩn bị cho giá hai thành phần. Chưa phải tối ưu demand charge 15 phút như ở Mỹ.
7. **[FACT] Chính sách BESS cấp lưới đã có khung.**
   - QHĐ8 điều chỉnh (QĐ 768/QĐ-TTg, 15/04/2025): BESS 10.000–16.300 MW vào 2030, so với 300 MW ở bản đầu.
   - Thông tư 62/2025/TT-BCT (hiệu lực 26/01/2026): khung giá hai thành phần cho BESS độc lập ≥10 MW, ≥110 kV.
   - Dự án mặt trời tập trung phải kèm BESS ≥10% công suất, ≥2 giờ.
   — https://en.vneconomy.vn/government-approves-revised-power-development-plan-8.htm ; https://arcusenergyasia.com/resources/regulations/circular-62 ; https://www.nortonrosefulbright.com/en/knowledge/publications/7eb0008e/development-of-battery-energy-storage-systems-in-vietnam (qua kết quả tìm kiếm). [INFERENCE] Đây là thị trường **utility/FTM**, không phải mục tiêu trực tiếp của sản phẩm C&I. Nó vẫn tạo chuỗi cung ứng, kỹ năng và chuẩn kỹ thuật BESS mà C&I hưởng lợi.
8. **[FACT] BESS lưới đầu tiên đã vận hành.** EVNHANOI có 50 MW/100 MWh tại 5 TBA 110 kV (07/2026). EVNNPC có 5 MW/10 MWh tại Song Khê (02/08/2026), nằm trong giai đoạn đầu 305 MW/610 MWh tại 47 TBA 110 kV. — https://www.energy-storage.news/hanoi-power-corporation-inaugurates-the-first-100mwh-battery-storage-portfolio-in-vietnamese-capital/ ; https://en.evn.com.vn/d/en-US/news/EVNNPC-commissions-first-BESS-in-Ninh-Binh-60-202-501616 (qua kết quả tìm kiếm).
9. **[FACT] DPPA được nới.** NĐ 57/2025 (03/03/2025) thay 80/2024. Ngưỡng khách hàng lớn 200.000 kWh/tháng do Bộ Công Thương quy định, có thể điều chỉnh. — https://www.tilleke.com/insights/clear-guidance-for-direct-power-purchase-agreements-in-vietnam/3/. NĐ 243/2026 có các thay đổi sau:
   - thêm trung tâm dữ liệu và doanh nghiệp sạc EV làm bên mua;
   - bỏ ngưỡng tiêu thụ/cấp điện áp cho bên mua;
   - bỏ trần giá DPPA vật lý;
   - rút thủ tục từ 7 xuống 3 bước.
   — https://www.reccessary.com/en/news/vietnam-solar-grid-export-dppa (qua kết quả tìm kiếm). [INFERENCE] DPPA là động lực **dữ liệu** (đo đếm, đối soát, chứng nhận nguồn xanh) cho bản sau. Nó chưa phải chức năng điều khiển MVP.
10. **[FACT] Sạc EV có biểu giá riêng.** QĐ 14/2025/QĐ-TTg và TT 60/2025/TT-BCT tách giá trạm sạc khỏi giá kinh doanh và sản xuất. Trạm sạc kinh doanh phải có công tơ riêng. — https://vneconomy.vn/automotive/quy-dinh-moi-ve-gia-ban-dien-cho-tram-sac-xe-dien.htm (qua kết quả tìm kiếm). [INFERENCE] Site C&I có EV phải mô hình hóa **nhiều điểm đo, nhiều biểu giá** trong cùng một site.
11. **[FACT] Phân biệt các tầng điều khiển.**
    - EMS của TSO là tầng phân tích trên SCADA: state estimation, contingency analysis, OPF/economic dispatch, AGC. — https://www.hitachienergy.com/jp/ja/products-and-solutions1/grid-and-generation-management-network-manager/network-manager-energy-management-system-ems (qua kết quả tìm kiếm).
    - Bộ điều khiển microgrid theo IEEE 2030.7-2017 có hai chức năng lõi: dispatch và transition (nối lưới ↔ tách đảo). IEEE 2030.8 quy định thử nghiệm. — https://www.redalyc.org/journal/2913/291374362027/291374362027.pdf (qua kết quả tìm kiếm).
    - ISO 50001:2018 là hệ thống **quản lý** (PDCA, EnPI, EnB), không phải hệ điều khiển. — https://www.iso.org/standard/69426.html ; https://library.e.abb.com/public/97259bfd72d54220a2762fe2a9f75537/ABBAbility_EnergyManager_ISO_50001rev1.pdf (qua kết quả tìm kiếm).
12. **[FACT] Ranh giới chức năng EMS ↔ BMS ↔ PCS.** Hai nguồn hạt giống (InfinitePower, Ampowr Cosmos) mô tả EMS lưu trữ là lớp điều phối BMS và PCS: giám sát, lập lịch tối ưu, chẩn đoán lỗi, peak shaving, tự tiêu thụ, giao dịch thị trường. — https://www.infinitepowerht.com/what-is-energy-management-system-ems-and-its-functions.html ; https://www.infinitepowerht.com/what-is-the-difference-between-bms-and-ems.html ; https://ampowr.com/energy-management-system-ems/ (qua kết quả tìm kiếm). Tính năng giao dịch của Cosmos (Day-Ahead, imbalance, aFRR) chỉ có ở thị trường Hà Lan. — https://ampowr.com/energy-optimization-and-market-participation-through-the-use-of-ampowr-cosmos/ (qua kết quả tìm kiếm).
13. **[FACT] Hãng thiết bị đều đóng gói một EMS C&I tại chỗ có thời gian đáp ứng xác định.**
    - Huawei SmartLogger5000B: zero export ≤2 s; peak shaving/capacity control ≤5 s; hỗ trợ EMS bên thứ ba.
    - Huawei EMMA-A02: peak shaving, feed-in limitation.
    - SMA Data Manager M: ≤50 thiết bị; peak load shaving qua "Energy Maximizer", là add-on SMA Premium.
    - Sungrow PowerStack: EMS300CP + iSolarCloud.
    — https://www.photomate.eu/smartlogger5000b ; https://www.heima24.de/shop/images/products/media/db-huawei-emma02.pdf ; https://www.sma-america.com/products/energy-management/data-manager-m-10 ; https://manuals.sma.de/SMA-Premium/en-US/17048176011.html ; https://www.vicoexport.com/en/powerstack (qua kết quả tìm kiếm). [INFERENCE] Mỗi hãng tối ưu **trong hệ sinh thái của mình**. Khoảng trống của chúng ta là **đa hãng + đa site + biểu giá Việt Nam + O&M**, không phải viết lại vòng điều khiển zero-export đã có sẵn trong logger của hãng.
14. **[INFERENCE → PROPOSAL] Giả định ban đầu (C&I đa site, solar + BESS + lưới + phụ tải + EV tùy chọn) về cơ bản đúng, với 4 điều chỉnh** (§3.6):
    - (a) Sản phẩm phải tạo giá trị ngay cả khi site **chỉ có PV**, vì BESS C&I ở Việt Nam còn sớm.
    - (b) EV chỉ là phụ tải điều khiển được ở P1/P2.
    - (c) Không có demand charge nên bộ tối ưu MVP xoay quanh TOU, giới hạn xuất lưới và giới hạn công suất.
    - (d) Không tham gia thị trường điện/VPP ở MVP.
15. **[PROPOSAL] Nhóm chính cho bản đầu: "C&I behind-the-meter energy management, đa site, đa hãng".** Gồm giám sát (nhóm 1) làm nền, cộng điều khiển giám sát (supervisory) BESS và giới hạn xuất lưới qua edge. Không làm: enterprise sustainability/ESG, SCADA/EMS cấp lưới, giao dịch thị trường.

---

## 3. Phân tích chi tiết

### 3.1 Bảy nhóm sản phẩm: định nghĩa, người mua, chức năng

| Nhóm | Định nghĩa làm việc | Người mua điển hình | Chức năng điển hình | Ví dụ sản phẩm (có nguồn) | Nhịp điều khiển / dữ liệu |
|---|---|---|---|---|---|
| **1. Site monitoring & analytics** | Thu thập, lưu trữ, hiển thị và phân tích dữ liệu thiết bị và công tơ của một hay nhiều site. Không ra lệnh điều khiển, hoặc chỉ điều khiển thủ công. | Installer/EPC, O&M contractor, chủ đầu tư nhỏ | Dashboard, lịch sử, báo cáo kWh/PR, cảnh báo, ticket, phân quyền theo công ty → site → chủ sở hữu | FusionSolar (nghiên cứu trước), SolisCloud, iSolarCloud; nền tảng bên thứ ba như meteocontrol VCOM (nghiên cứu FusionSolar trước) | Dữ liệu 1–5 phút (FusionSolar: 5 phút, nghiên cứu trước); không có vòng điều khiển |
| **2. C&I energy management (BTM)** | Phần mềm, thường cloud + edge, quản lý dòng năng lượng **sau công tơ** của một cơ sở: PV, BESS, lưới, phụ tải, EV. Mục tiêu: hóa đơn, tuân thủ giới hạn đấu nối, độ tin cậy. | Chủ C&I (CFO, giám đốc nhà máy), energy manager, ESCO/nhà đầu tư PPA mái nhà | Biểu giá TOU, tự tiêu thụ, peak shaving theo ngưỡng, giới hạn xuất lưới, lập lịch BESS, điều khiển phụ tải linh hoạt, báo cáo tiết kiệm | Schneider EcoStruxure Microgrid Advisor (MPC cloud, lịch 15 phút/72 h, OpenADR); Stem Athena; Wärtsilä GEMS5 (BTM, demand charge, microgrid, EV) | Lịch: 15 phút; vòng giới hạn: giây (ở edge/logger) |
| **3. Solar/renewable management (APM)** | Quản lý hiệu suất tài sản tái tạo (PV/gió) cấp danh mục: KPI kỹ thuật và thương mại, O&M, CMMS | IPP, asset manager, O&M lớn | PR, availability, phân tích tổn thất, quản lý hợp đồng, field service | Power Factors Unity (APM + CMMS; gộp Drive và Greenbyte) | Dữ liệu SCADA 1–15 phút; ít điều khiển |
| **4. BESS management & optimization** | EMS của hệ lưu trữ: điều phối BMS + PCS; chế độ vận hành, lập lịch sạc/xả, bảo vệ SOC/SOH, có thể xếp chồng doanh thu | Tích hợp BESS, chủ BESS (C&I hoặc FTM), EPC | Chế độ: peak shaving, arbitrage, tự tiêu thụ, backup, dịch vụ phụ trợ; giám sát cell/rack; chẩn đoán | Ampowr Cosmos; FENECON FEMS/OpenEMS; Sungrow EMS300CP; InfinitePower (mô tả chức năng) | Lệnh P/Q: 100 ms–giây; lịch: 5–15 phút |
| **5. Microgrid / DER coordination** | Bộ điều khiển microgrid (IEEE 2030.7: dispatch + transition, tách đảo/hòa lưới) và nền tảng phối hợp nhiều DER (DERMS do utility vận hành; VPP do aggregator vận hành, hướng thị trường) | Khu công nghiệp, campus, đảo/vùng xa; utility phân phối (DERMS); aggregator (VPP) | Tách đảo, black start, cân bằng tần số/điện áp khi đảo, xếp thứ tự sa thải phụ tải; DERMS: ràng buộc điện áp/nhiệt lưới phân phối; VPP: đấu thầu linh hoạt | Schneider Microgrid Advisor (islanding); Sungrow PowerStack On&Off-Grid (VSG, black start, VPP mode); định nghĩa DERMS/VPP theo GridBeyond, Next Kraftwerke | Transition: ms–chu kỳ (controller cục bộ); DERMS/VPP: giây–phút |
| **6. Utility/grid operational EMS (SCADA/EMS cho TSO)** | Hệ thống điều hành lưới truyền tải: SCADA + ứng dụng mạng | TSO/NSMO, utility lớn | State estimation, contingency analysis (N-1), OPF/economic dispatch, AGC, mô hình CIM/CGMES | Hitachi Energy Network Manager EMS | SCADA 2–4 s; AGC giây; quy trình vận hành 24/7 |
| **7. ISO 50001 enterprise energy management** | Hệ thống **quản lý** năng lượng của tổ chức theo PDCA: chính sách, rà soát năng lượng, SEU (hộ tiêu thụ đáng kể), EnPI, EnB, mục tiêu, hành động, đánh giá | Energy manager doanh nghiệp, bộ phận EHS/ESG; cơ sở sử dụng năng lượng trọng điểm | Đo lường phụ (sub-metering) mọi dạng năng lượng (điện, nhiệt, khí, dầu), chuẩn hóa theo sản lượng, M&V, kế hoạch hành động, bằng chứng đánh giá | ABB Ability EnergyManager (định vị hỗ trợ ISO 50001); Phoenix Contact | Ngày/tháng; không điều khiển |

### 3.2 Chồng lấn và khác biệt

Ma trận chức năng × nhóm (● cốt lõi, ◐ thường có/một phần, ○ hiếm/không phải trọng tâm). Đây là [INFERENCE] tổng hợp từ các nguồn ở bảng 3.1, không phải khảo sát định lượng.

| Chức năng | 1 Monitor | 2 C&I EM | 3 RE APM | 4 BESS EMS | 5 µGrid/DER | 6 TSO EMS | 7 ISO 50001 |
|---|---|---|---|---|---|---|---|
| Thu thập đa hãng (Modbus/API) | ● | ● | ● | ◐ (thường 1 hãng PCS/BMS) | ● | ● (IEC 104/61850, ICCP) | ◐ |
| Đa site / danh mục | ● | ◐ | ● | ◐ | ◐ (VPP ●) | ○ (một lưới) | ◐ |
| Biểu giá & hóa đơn ảo | ◐ | ● | ◐ (PPA) | ● | ◐ | ○ | ◐ |
| Giới hạn xuất lưới / công suất | ○ | ● | ○ | ● | ● | ○ | ○ |
| Lập lịch BESS (forecast + tối ưu) | ○ | ● | ○ | ● | ● | ○ | ○ |
| Bảo vệ cấp cell/rack | ○ | ○ (đọc) | ○ | ◐ (đọc từ BMS; bảo vệ do BMS) | ○ | ○ | ○ |
| Tách đảo / transition | ○ | ◐ | ○ | ◐ | ● | ○ | ○ |
| Mô hình mạng điện + ràng buộc lưới | ○ | ○ | ○ | ○ | ◐ (DERMS ●) | ● | ○ |
| Thị trường/dịch vụ phụ trợ | ○ | ◐ (DR) | ◐ | ◐ | ● (VPP) | ● (AGC) | ○ |
| O&M: cảnh báo, ticket, KPI | ● | ◐ | ● | ◐ | ◐ | ◐ | ○ |
| EnPI/EnB, M&V, kiểm toán | ○ | ◐ | ○ | ○ | ○ | ○ | ● |
| Carbon / báo cáo ESG | ○ | ◐ | ○ | ○ | ○ | ○ | ◐ (năng lượng, chưa phải carbon) |

**Khác biệt quan trọng cho thiết kế**

- **Trách nhiệm an toàn tăng từ trái sang phải.** Nhóm 1 và 7 không điều khiển. Nhóm 2 và 4 điều khiển tài sản của khách. Nhóm 5 phải xử lý chuyển chế độ (transition) trong thời gian ms–chu kỳ, nên chỉ controller cục bộ làm được. Nhóm 6 điều khiển hệ thống điện quốc gia. [INFERENCE]
- **Vị trí vòng điều khiển.** Ở mọi sản phẩm có nguồn, vòng nhanh (zero-export ≤2 s, peak shaving ≤5 s ở SmartLogger5000B; Energy Maximizer của SMA) nằm **tại site**. Cloud chỉ lập lịch: Schneider nói lịch 15 phút/72 h, và có lịch mặc định 48 h khi mất kết nối (một tài liệu khác nói 72 h). [FACT, URL ở ledger #20–#23]
- **Nhóm 2 và 4 chồng lấn lớn nhất.** C&I EMS **chứa** BESS EMS cấp supervisory. Nó **không thay** EMS/controller của nhà tích hợp BESS. Tương tự, Schneider tuyên bố Microgrid Advisor "không thay thế" BMS tòa nhà và các điều khiển hiện có. [FACT, ledger #21]
- **Nhóm 7 khác về bản chất.** Đây là quy trình quản lý của tổ chức (con người + tài liệu + đánh giá), đa dạng năng lượng. Phần mềm chỉ hỗ trợ dữ liệu EnPI/EnB. Nhóm 2 có thể **xuất dữ liệu** cho 50001, nhưng không được coi là "tuân thủ ISO 50001".

### 3.3 Phân khúc khách hàng, persona và JTBD

Bối cảnh Việt Nam: các hợp đồng EPC–ESCO lớn ở khu công nghiệp như SolarBK + Banpu NEXT + Amata (227 MWp mái nhà) và Hero Future Energies + VNEB (mái nhà + BESS ở KCN); Amata Biên Hòa 18 MWp trên 14 nhà máy; áp lực xuất khẩu CBAM/CSRD [FACT, ledger #27–#28]. Phần lớn site C&I được **bên thứ ba** (EPC/ESCO/O&M) vận hành, không phải chủ nhà máy tự vận hành. [INFERENCE từ các nguồn trên và nghiên cứu FusionSolar: mô hình installer → plant → owner]

| Persona | Mô tả | JTBD chính ("Khi…, tôi muốn…, để…") | Chỉ số họ quan tâm | Mức ưu tiên cho MVP |
|---|---|---|---|---|
| **P1 · Chủ C&I / CFO / giám đốc nhà máy** | Người ký hợp đồng, quan tâm hóa đơn và sản xuất không gián đoạn | Khi nhận hóa đơn EVN, tôi muốn thấy hệ PV/BESS đã tiết kiệm bao nhiêu theo từng khung giờ, để quyết định mở rộng và kiểm tra ESCO | VNĐ tiết kiệm/tháng, % tự tiêu thụ, kWh cao điểm tránh được, sự cố ảnh hưởng sản xuất | P0 (người xem, báo cáo) |
| **P2 · Energy manager (cán bộ quản lý năng lượng)** | Ở cơ sở sử dụng năng lượng trọng điểm (≥1.000 TOE/năm cho công nghiệp; cả nước 3.491 cơ sở năm 2023) | Khi lập báo cáo năng lượng hoặc kế hoạch tiết kiệm, tôi muốn có số liệu đo phụ theo phụ tải và khung giờ, để chứng minh hiệu quả | kWh/đơn vị sản phẩm, tải nền, cao điểm, phụ tải lớn | P1 (nhóm 7 chỉ ở mức xuất dữ liệu) |
| **P3 · O&M contractor** | Vận hành nhiều site của nhiều chủ, nhiều hãng inverter/BESS | Khi có báo động hoặc PR giảm ở bất kỳ site nào, tôi muốn thấy sớm và giao việc, để giữ SLA availability và không phải đi thực địa vô ích | Availability, MTTR, số ticket, tổn thất kWh | **P0 (người dùng hằng ngày)** |
| **P4 · EPC / installer** | Thiết kế, lắp, nghiệm thu, đăng ký với Sở Công Thương/điện lực; bàn giao | Khi nghiệm thu một hệ mới, tôi muốn cấu hình nhanh giới hạn xuất lưới và kiểm chứng nó hoạt động, để đạt yêu cầu đấu nối và bàn giao | Thời gian commissioning, % site đạt export-limit test, số lần quay lại site | **P0** |
| **P5 · BESS integrator** | Lắp PCS + BMS + EMS cục bộ; chịu bảo hành pin | Khi tích hợp BESS vào site có sẵn PV và nhiều phụ tải, tôi muốn một lớp supervisory đa hãng tôn trọng giới hạn của BMS, để không mất bảo hành và vẫn bán được bài toán kinh tế | Số chu kỳ, SOH, giờ vận hành ngoài giới hạn = 0, doanh thu/tiết kiệm | P0/P1 |
| **P6 · IPP / asset owner / ESCO (PPA mái nhà)** | Sở hữu danh mục mái nhà, bán điện cho chủ nhà máy (PPA, DPPA) | Khi lập hóa đơn PPA hoặc báo cáo cho bên cho vay, tôi muốn số liệu sản lượng đo đếm tin cậy theo site và khung giờ, để thu tiền và báo cáo IRR | kWh bán, kWh bị cắt do giới hạn xuất, IRR, availability | P0 (báo cáo), P1 (DPPA) |
| **P7 · Aggregator / VPP** | Gom nhiều tài sản để cung cấp linh hoạt | Khi lưới cần linh hoạt, tôi muốn điều phối nhiều BESS cùng lúc, để bán dịch vụ | MW khả dụng, tỷ lệ đáp ứng | **P2.** Việt Nam chưa có thị trường DR/linh hoạt cho C&I trong nguồn tìm được [UNKNOWN]. EU/Mỹ/Úc có. |

### 3.4 Động lực thị trường Việt Nam

#### 3.4.1 Chuỗi pháp lý ĐMTMN tự sản xuất, tự tiêu thụ

| Văn bản | Ngày | Nội dung liên quan sản phẩm | Nhãn |
|---|---|---|---|
| NĐ 135/2024/NĐ-CP | 22/10/2024 | Hộ gia đình/nhà riêng lẻ <100 kW bán dư ≤20% công suất lắp đặt; hệ có thiết bị chống phát ngược được miễn giấy phép (nghiên cứu FusionSolar trước) | FACT (đã bị thay) |
| NĐ 58/2025/NĐ-CP | 03/03/2025 | Thay 135. Mở rộng nguồn TSXTTT. Ưu tiên huy động giờ cao điểm cho dự án có lưu trữ nối lưới, **trừ nguồn TSXTTT**. Phải thông báo Sở Công Thương, điện lực, xây dựng, PCCC kể cả khi không bán dư. Định nghĩa thiết bị chống phát ngược có thể bật/tắt. Nguồn khác nhau về cơ sở tính 20% (công suất lắp đặt hay sản lượng thực phát) | FACT (qua kết quả tìm kiếm) |
| NĐ 133/2026/NĐ-CP | hiệu lực 25/05/2026 | Xử phạt vi phạm hành chính về ĐMTMN, tới 100 triệu đồng | FACT (qua kết quả tìm kiếm, luatvietnam) |
| NĐ 243/2026/NĐ-CP | 26/06/2026 | Bán dư ≤50% sản lượng thực phát; được vượt đến 31/12/2030 nếu lưới tiếp nhận được; điện xả từ BESS tính vào điện dư; đăng ký bắt buộc với hệ nối lưới trung áp trở lên **có bán dư** | FACT (qua kết quả tìm kiếm) |
| Thông tư 29/2026/TT-BCT | 2026 | Được WFW nhắc là đi kèm NĐ 243; chưa tìm thấy nội dung | UNKNOWN |
| Chỉ thị 10/CT-TTg | 30/03/2026 | Thúc đẩy ĐMTMN TSXTTT (mục tiêu ≥10% công sở/hộ gia đình); đến 22/09/2026 chỉ 2/34 tỉnh ban hành chính sách | FACT (qua kết quả tìm kiếm) |

**Hệ quả kỹ thuật [INFERENCE]**

- Chế độ "zero-export" (0 W tại điểm đấu nối) và "export-limit" (giới hạn theo kW hoặc theo % sản lượng) phải là **hai chế độ khác nhau**.
  - Giới hạn theo % **sản lượng thực phát** là ràng buộc **năng lượng tích lũy** (kWh theo kỳ). Nó không phải ràng buộc công suất tức thời, nên cần bộ đếm kWh PV và kWh xuất theo kỳ, cộng chiến lược khi tiến gần trần.
  - Chưa rõ kỳ tính (tháng? năm?) → Q-A03.
- Vì 50% tính trên sản lượng thực phát, hệ phải đo **PV phát** (inverter hoặc công tơ PV riêng), không chỉ công tơ tổng.
- Nhãn "thiết bị chống phát ngược có thể bật/tắt" cho thấy cơ quan quản lý quan tâm đến **trạng thái cấu hình**. Sản phẩm nên ghi nhật ký kiểm toán (audit log) mỗi lần đổi chế độ hoặc giới hạn.

#### 3.4.2 Khung giờ TOU

| Khung | Ngày | Thứ Hai–Thứ Bảy | Chủ nhật |
|---|---|---|---|
| Cũ (TT 16/2014) | đến 22/04/2026 | Cao điểm 9h30–11h30 & 17h00–20h00; Bình thường 4h–9h30, 11h30–17h, 20h–22h; Thấp điểm 22h–4h | Không cao điểm; BT 4h–22h; TĐ 22h–4h |
| Mới (QĐ 963/QĐ-BCT; số giờ theo TT 60/2025) | hiệu lực pháp lý 22/04/2026; ngày áp hóa đơn **chưa chắc** | Cao điểm 17h30–22h30 (5 h); Bình thường 6h–17h30 & 22h30–24h (13 h); Thấp điểm 0h–6h (6 h) | Không cao điểm; BT 6h–24h (18 h); TĐ 0h–6h |

[INFERENCE] Biểu giá phải là **dữ liệu có phiên bản theo ngày hiệu lực** (versioned calendar), có thể có hai phiên bản song song (pháp lý và hóa đơn thực). Không được hard-code. Trạm sạc EV được nêu (vnreview) là theo khung cũ, nên khung giờ có thể khác nhau theo **loại hợp đồng** trong giai đoạn chuyển tiếp [UNKNOWN].

#### 3.4.3 Giá điện C&I (QĐ 1279/QĐ-BCT, hiệu lực 10/05/2025, chưa VAT, đ/kWh)

| Sản xuất — cấp điện áp | Bình thường | Thấp điểm | Cao điểm | Cao/Thấp |
|---|---|---|---|---|
| ≥110 kV | 1.811 | 1.146 | 3.266 | 2,85× |
| 22–<110 kV | 1.833 | 1.190 | 3.398 | 2,86× |
| 6–<22 kV | 1.899 | 1.234 | 3.508 | 2,84× |
| <6 kV | 1.987 | 1.300 | 3.640 | 2,80× |

- Kinh doanh <6 kV, cao điểm: 5.422 đ/kWh. Giá bán lẻ bình quân: 2.204,0655 đ/kWh. [FACT, thuvienphapluat qua kết quả tìm kiếm]
- Nghị định 278/2026/NĐ-CP (09/07/2026) sửa cơ chế điều chỉnh giá bình quân. Chưa thấy đợt tăng giá 2026. [FACT/UNKNOWN]

**Ví dụ kinh tế arbitrage minh họa [INFERENCE, số giả định]**

- Giả định: BESS 1 MWh khả dụng, hiệu suất vòng (RTE) 90%, 1 chu kỳ/ngày, 6 ngày/tuần (~312 ngày/năm), sạc thấp điểm, xả cao điểm, cấp 22–110 kV.
- Chênh lệch ròng ≈ 3.398 − 1.190/0,9 ≈ 3.398 − 1.322 = **2.076 đ/kWh xả**.
- Tiết kiệm ≈ 2.076 × 1.000 × 312 ≈ **648 triệu đ/năm/MWh**, chưa trừ suy hao và O&M.
- Nếu sạc bằng PV dư (đặc biệt khi bị giới hạn xuất lưới), chi phí sạc gần 0 nên giá trị lên tới khoảng 3.398 đ/kWh.

Đây là ước tính thô cho mục đích định vị, **không** phải cam kết. Đơn giá CAPEX BESS ở Việt Nam là UNKNOWN.

#### 3.4.4 Giá điện hai thành phần

- Thí điểm cho khách sản xuất ≥200.000 kWh/tháng: hóa đơn song song 01–06/2026, thanh toán thật 07/2026–07/2027, mở rộng từ 08/2027 (theo dự thảo). Thành phần công suất tính theo **công suất đăng ký**, trả cả khi không dùng. [FACT, nguồn báo, qua kết quả tìm kiếm]
- [INFERENCE] Sản phẩm cần:
  - giám sát P max theo cửa sổ đo (độ dài cửa sổ: UNKNOWN, Q-A04);
  - cảnh báo khi tiến gần công suất đăng ký;
  - chế độ BESS "cap công suất mua" (import cap).
- Đây là "peak shaving kiểu Việt Nam" và là cơ hội thật từ 2027.

#### 3.4.5 BESS và lưới

- QHĐ8 điều chỉnh: 10.000–16.300 MW vào 2030, khoảng 96.000 MW vào 2050.
- TT 62/2025: giá hai thành phần cho BESS độc lập ≥10 MW/≥110 kV (capex cố định, O&M cố định, chi phí sạc biến đổi, IRR trần 12%; theo Arcus).
- TT 09/2025 và 12/2025: mặt trời kèm BESS ≥10%/2 h. Nguồn khác nhau về phạm vi: chỉ "mặt trời tập trung" hay rộng hơn.
- TT 17/2025: BESS của đơn vị EVN là tài sản lưới.
- Có tuyên bố chưa kiểm chứng rằng KCN/nhà máy lớn phải "tự cung 30%" và rằng BESS là điều kiện DPPA. Cả hai đều **UNKNOWN**.
- [INFERENCE] Tài sản BESS cấp lưới thuộc nhóm 4/6 với khách hàng là EVN. Đó **không** phải thị trường của MVP.

#### 3.4.6 EV

- Biểu giá trạm sạc riêng: khoảng 1.565–3.835 đ/kWh trung áp trở lên, 1.653–4.298 đ/kWh hạ áp (con số báo chí, chưa đối chiếu).
- V-Green: 99 trạm siêu nhanh (tối đa 100 × 150 kW/trạm) dùng PV + pin. Thế Giới Di Động + V-Green: +1.000 trạm sạc năm 2026.
- Không tìm thấy dữ liệu sạc đội xe (depot) C&I. [FACT/UNKNOWN]
- [INFERENCE] EV ở site C&I Việt Nam hiện là phụ tải phụ, nhưng có thể làm vượt công suất máy biến áp. Ở MVP chỉ cần **giám sát + giới hạn công suất tổng**. Smart charging OCPP để P1.

### 3.5 Bối cảnh toàn cầu (để so sánh, không phải thị trường mục tiêu MVP)

| Vùng | Động lực | Ý nghĩa cho định vị | Nhãn |
|---|---|---|---|
| **EU** | EED 2023/1791 Điều 11: doanh nghiệp >85 TJ/năm phải có EnMS chứng nhận (hạn 11/10/2027); >10 TJ phải kiểm toán (lần đầu trước 11/10/2026, sau đó tối thiểu mỗi 4 năm) | Nhóm 7 có động lực pháp lý ở EU. Ở Việt Nam, động lực tương tự là chế độ cơ sở trọng điểm (Luật 50/2010, sửa bởi Luật 77/2025/QH15, hiệu lực 01/01/2026; chi tiết UNKNOWN) | FACT |
| **EU (Đức)** | Lắp đặt pin đạt kỷ lục H1/2026. C&I là phân khúc nhỏ (khoảng 1,1 GWh/16 GWh giữa 2024). Tồn đọng đấu nối | C&I storage ở EU đang lên nhưng nhỏ hơn residential/utility | FACT (số liệu cũ) |
| **EU (Hà Lan)** | Ampowr Cosmos giao dịch Day-Ahead, imbalance, aFRR cho site C&I; peak shaving theo giới hạn đấu nối (tránh phạt nghẽn lưới) | "Giới hạn công suất đấu nối" là bài toán chung với Việt Nam (giới hạn MBA, công suất đăng ký) | FACT |
| **Mỹ** | Demand charge thường chiếm 30–70% hóa đơn C&I (nguồn vendor), tính theo đỉnh 15 phút. C&I storage Q2/2026: 1,8 GWh (SEIA/Benchmark). OBBBA: ITC lưu trữ được giữ lâu hơn gió/mặt trời; ràng buộc FEOC từ 2026. FERC 2222: PJM/NYISO/ISO-NE triển khai 2026–2027, MISO/SPP 2029–2030 | Phần lớn bộ tối ưu C&I Mỹ (Stem, GEMS) xây quanh demand charge, **không áp được trực tiếp** ở Việt Nam | FACT (nguồn vendor cho %); INFERENCE |
| **Úc** | Cheaper Home Batteries (mở rộng lên ~7,2 tỷ AUD, đổi mức hỗ trợ từ 05/2026); pin phải "có khả năng" tham gia VPP; khoảng 400.000 lắp đặt/11,2 GWh; ISP 2026 giả định VPP tham gia ít hơn | Yêu cầu "VPP-capable" là mẫu tốt: thiết kế sẵn khả năng điều phối, chưa bật | FACT |

### 3.6 Kiểm chứng giả định "C&I đa site: solar + BESS + lưới + phụ tải + EV tùy chọn"

| Thành phần giả định | Bằng chứng ủng hộ | Bằng chứng phản bác / rủi ro | Kết luận |
|---|---|---|---|
| **C&I** (không phải hộ gia đình, không phải utility) | Biểu giá TOU chỉ áp cho sản xuất/kinh doanh, hộ sinh hoạt vẫn bậc thang. Hợp đồng EPC–ESCO ở KCN. Hướng FusionSolar trước là installer/O&M C&I | Thị trường TSXTTT nhỏ (1.614 MWp theo NĐ 58/243). Chỉ thị 10 thúc đẩy cả hộ gia đình | **Giữ** [INFERENCE] |
| **Đa site** | O&M/EPC/ESCO quản lý danh mục. Chuỗi bán lẻ, KCN nhiều nhà máy | Chủ C&I đơn lẻ thường chỉ có 1–3 site | **Giữ**, nhưng đơn vị bán là **tổ chức vận hành** (P3/P4/P6). Chủ nhà máy là người xem [INFERENCE] |
| **Solar** | 130.811 hệ ĐMTMN >11.200 MWp; giới hạn xuất lưới là yêu cầu vận hành phổ biến | — | **Giữ, là nền** [FACT/INFERENCE] |
| **BESS** | Khung giờ mới (cao điểm tối) cộng chênh lệch ~2,8×. NĐ 243 tính điện xả BESS vào điện dư. Dự án PV + BESS C&I đã có (SolarBK 2,2 MWp + 2,3 MWh; VinFast Energy tại Nghi Sơn 2) | Tỷ lệ site C&I có BESS: UNKNOWN (có lẽ thấp). Chưa có demand charge. Giá hai thành phần còn thí điểm | **Giữ, nhưng không bắt buộc**: sản phẩm phải chạy được với site PV-only [INFERENCE] |
| **Lưới (grid connection)** | Mọi bài toán (TOU, zero-export, công suất đăng ký) đều xoay quanh điểm đấu nối | — | **Giữ, là đối tượng trung tâm** (POI meter) |
| **Phụ tải nhà máy** | Energy manager cần đo phụ; chế độ cơ sở trọng điểm | Điều khiển phụ tải sản xuất rủi ro cao (ảnh hưởng dây chuyền) | **Giám sát ở MVP**; điều khiển phụ tải chỉ với phụ tải không quan trọng, P1+ [PROPOSAL] |
| **EV tùy chọn** | Biểu giá riêng; DPPA mở cho doanh nghiệp sạc | Chưa có dữ liệu depot C&I | **P1/P2** [PROPOSAL] |

**Kết luận RQ4 [INFERENCE]:** giả định đúng về hướng, cần chỉnh 4 điểm như ở Phát hiện #14. Thêm một điểm: thứ tự giá trị ở Việt Nam là (1) tuân thủ và giới hạn xuất lưới, (2) minh bạch tiết kiệm theo TOU, (3) O&M đa hãng, (4) tối ưu BESS. Không giống Mỹ, nơi demand charge đứng đầu.

### 3.7 Chọn nhóm chính cho bản phát hành đầu

Tiêu chí: tư liệu nguồn sẵn có (S), độ phức tạp triển khai (C, thấp là tốt), giá trị cho khách Việt Nam (V), khớp năng lực đội (Java/Spring, Angular, TimescaleDB, MQTT, edge kiểu OpenEMS — giả định tại thời điểm viết; frontend nay là React, [06 ADR-20](../06-system-architecture.html#adr-20)) (T), rủi ro an toàn/pháp lý (R, thấp là tốt). Thang 1–5, [INFERENCE] chấm theo bằng chứng ở trên.

| Nhóm | S | C (5 = đơn giản) | V | T | R (5 = rủi ro thấp) | Tổng | Ghi chú |
|---|---|---|---|---|---|---|---|
| 1 Monitoring | 5 | 5 | 3 | 5 | 5 | 23 | Nền đã nghiên cứu kỹ (FusionSolar); đứng một mình thì khác biệt thấp, vì hãng cho miễn phí |
| **2 C&I EM (BTM) đa site** | 4 | 3 | **5** | 4 | 3 | **19 + kế thừa 1** | Ghép trên nhóm 1; giá trị rõ (TOU, giới hạn xuất, BESS) |
| 3 RE APM | 3 | 3 | 2 | 4 | 5 | 17 | Khách IPP lớn ít; FIT cũ |
| 4 BESS EMS (độc lập) | 3 | 2 | 3 | 3 | 2 | 13 | Cạnh tranh trực tiếp với EMS của nhà tích hợp; rủi ro bảo hành |
| 5 Microgrid/DER | 2 | 1 | 2 | 2 | 1 | 8 | Transition ms; chứng nhận IEEE 2030.7/2030.8; chưa có thị trường VPP |
| 6 TSO EMS | 2 | 1 | 1 | 1 | 1 | 6 | Khách duy nhất NSMO/EVN; vendor toàn cầu |
| 7 ISO 50001 / ESG | 3 | 3 | 2 | 3 | 5 | 16 | Người mua khác; cần đa dạng năng lượng |

**Đề xuất [PROPOSAL]: nhóm 2, "C&I behind-the-meter energy management đa site, đa hãng", với nhóm 1 làm lớp nền.** Bộ điều khiển vòng nhanh ở edge (logger của hãng hoặc edge của ta). Cloud chỉ giám sát, lập lịch và báo cáo.

**Vì sao KHÔNG làm enterprise sustainability platform (ESG/carbon)**
1. Người mua khác (CSO/ESG, tài chính) và chu kỳ bán khác. Họ cần Scope 1–3, dữ liệu phi điện (nhiên liệu, chuỗi cung ứng), khung báo cáo (GHG Protocol, CSRD) mà đội ta không có tư liệu nguồn. [INFERENCE]
2. Giá trị riêng của ta là dữ liệu thiết bị thời gian thực và điều khiển. Nền tảng ESG chỉ cần **tổng hợp tháng**, có thể lấy từ ta qua export/API. Áp lực CBAM/CSRD ở KCN là thật [FACT, ledger #28], nên ta **cung cấp dữ liệu** (kWh PV tự dùng, kWh lưới theo giờ, chứng từ đo đếm), không xây nền tảng carbon.
3. ISO 50001 là hệ quản lý con người và tài liệu. Phần mềm không thể "làm cho" doanh nghiệp tuân thủ. Tuyên bố sai rủi ro pháp lý và uy tín. [FACT về bản chất PDCA; INFERENCE về rủi ro]

**Vì sao KHÔNG làm hệ điều khiển lưới cấp utility**
1. Chức năng lõi (state estimation, contingency N-1, OPF, AGC, mô hình CIM/CGMES) cần mô hình mạng truyền tải và quy trình vận hành 24/7 của NSMO. Khách hàng gần như duy nhất là EVN/NSMO, mua từ vendor toàn cầu. [FACT về chức năng; INFERENCE về thị trường]
2. BESS lưới ở Việt Nam do EVN sở hữu, có SCADA/EMS/PPC riêng (dự án EVNHANOI dùng nhà thầu SCADA/EMS/PPC riêng). [FACT, nguồn LinkedIn của vendor: độ tin thấp]
3. Rủi ro an toàn và trách nhiệm pháp lý không phù hợp với một đội mới. Cloud **không bao giờ** được nằm trong vòng bảo vệ, kể cả ở C&I.
4. Ta vẫn **tương thích** với lưới: tôn trọng lệnh giới hạn công suất hoặc lệnh của điện lực khi có. P2: đọc lệnh qua IEC 60870-5-104 nếu cần, giống SmartLogger3000 có giao diện IEC 104 [FACT, ledger #22].

**Khác hướng cũ (FusionSolar → EMS) và lý do**

| Điểm | Hướng cũ | Hướng mới | Lý do |
|---|---|---|---|
| Phạm vi | Giám sát/O&M PV đa hãng | + supervisory BESS, giới hạn xuất/nhập, biểu giá TOU, phụ tải, EV tùy chọn | NĐ 243 tính BESS vào điện dư; cao điểm chuyển sang buổi tối; giá hai thành phần đang tới |
| Cơ sở pháp lý | NĐ 135/2024, 20% | NĐ 58/2025 + 243/2026, 50% sản lượng thực phát | Văn bản cũ đã bị thay |
| Vai trò điều khiển | Gần như chỉ đọc | Ghi setpoint/lịch qua edge, có giới hạn an toàn | Giá trị BESS cần điều khiển |
| Kiến trúc | Edge-first, MQTT, TimescaleDB | **Giữ nguyên.** Edge càng quan trọng hơn vì vòng ≤2–5 s | Nhất quán |

---

## 4. Hệ quả thiết kế cho sản phẩm

Các mục dưới đây là [PROPOSAL]. Mã FR và module theo `_conventions.md`. Mã cụ thể sẽ do người viết 04/03 cấp; mã ở đây là đề xuất.

| # | Đề xuất | Module | Ưu tiên | Căn cứ |
|---|---|---|---|---|
| D-01 | Định vị: "Nền tảng quản lý năng lượng C&I đa site, đa hãng cho installer/O&M/ESCO tại Việt Nam". Người dùng chính là tổ chức vận hành (P3/P4/P6); chủ C&I (P1) là viewer có báo cáo tiết kiệm | M-ORG, M-DASH | P0 | §3.3, §3.6 |
| D-02 | Mô hình site bắt buộc có **POI meter** (điểm đấu nối), tùy chọn công tơ PV, công tơ BESS, công tơ EV, công tơ phụ tải phụ; mỗi điểm đo gắn **hợp đồng/biểu giá** riêng | M-GRID, M-TAR | P0 | NĐ 243 (điện BESS xả = điện dư), biểu giá EV riêng |
| D-03 | Biểu giá dạng dữ liệu có phiên bản: khung giờ (TT 16/2014, QĐ 963/2026…), bảng giá theo nhóm khách hàng × cấp điện áp × khung giờ (QĐ 1279/2025…), hiệu lực theo ngày; hỗ trợ hai lịch song song (pháp lý/hóa đơn); cấu trúc hai thành phần (kWh + kW đăng ký) | M-TAR | P0 | §3.4.2–3.4.4 |
| D-04 | Chế độ lưới tách biệt: `ZERO_EXPORT` (0 W), `EXPORT_LIMIT_KW`, `EXPORT_ENERGY_SHARE` (% sản lượng thực phát theo kỳ), `IMPORT_CAP_KW` (công suất đăng ký/MBA). Vòng nhanh chạy **ở edge/logger** (mục tiêu tham chiếu: ≤2 s zero-export, ≤5 s cap như SmartLogger5000B công bố); cloud chỉ cấu hình và kiểm chứng | M-GRID, M-OPT | P0 | Phát hiện #3, #13 |
| D-05 | Mọi thay đổi chế độ hoặc giới hạn đều có audit log (ai, khi nào, giá trị cũ/mới), xuất được làm bằng chứng cho điện lực hoặc Sở Công Thương | M-SEC, M-REP | P0 | NĐ 58 định nghĩa thiết bị chống phát ngược bật/tắt được; NĐ 133/2026 xử phạt |
| D-06 | Bộ tối ưu MVP: luật minh bạch (rule-based) theo TOU: sạc từ PV dư/thấp điểm, xả cao điểm 17h30–22h30, giữ SOC dự phòng, tôn trọng `IMPORT_CAP`. **Không gọi là AI.** Tối ưu theo dự báo (MPC) để P1 | M-OPT, M-BESS | P0/P1 | §3.4.3; quy ước không gán nhãn AI |
| D-07 | Báo cáo "tiết kiệm theo khung giờ" so với baseline không có PV/BESS, kèm phương pháp tính rõ ràng; tách kWh bị cắt do giới hạn xuất lưới (curtailed) | M-REP | P0 | JTBD P1, P6 |
| D-08 | Site **PV-only** là công dân hạng nhất: mọi màn hình chạy khi không có BESS | toàn bộ | P0 | §3.6 |
| D-09 | Supervisory BESS: chỉ gửi setpoint P/lịch/chế độ tới EMS/PCS cục bộ; đọc giới hạn BMS (dòng sạc/xả cho phép, SOC min/max) và **không bao giờ** vượt; mất kết nối cloud → edge rơi về lịch mặc định an toàn | M-BESS, M-SEC | P0 | Phát hiện #12, #13; Schneider fallback 48–72 h |
| D-10 | EV: giám sát + gộp vào `IMPORT_CAP` ở P1; OCPP smart charging ở P1/P2 | M-EV | P1 | §3.4.6 |
| D-11 | Xuất dữ liệu cho ESG/ISO 50001 (CSV/API: kWh theo nguồn × giờ, EnPI đơn giản kWh/đơn vị sản phẩm nếu nhập sản lượng); **không** tuyên bố tuân thủ ISO 50001 | M-REP, M-INT | P1 | §3.7 |
| D-12 | Theo dõi P max theo cửa sổ đo và cảnh báo gần công suất đăng ký (chuẩn bị giá hai thành phần 2027) | M-GRID, M-ALM | P1 | §3.4.4 |
| D-13 | Mô hình dữ liệu sẵn cho DPPA (đo đếm theo chu kỳ 30/60 phút, đối soát) và "VPP-capable" (giống Úc), nhưng **không bật** điều phối thị trường ở MVP | M-INT | P2 | Phát hiện #9; §3.5 |
| D-14 | Không xây SCADA/EMS lưới, microgrid transition/black start hay giao dịch thị trường điện trong 12–18 tháng đầu | — | Ngoài phạm vi | §3.7 |

---

## 5. Evidence ledger

| # | Claim | Source URL | Source type & date | Excerpt/paraphrase | Confidence | Conflicting evidence | Design implication |
|---|---|---|---|---|---|---|---|
| 1 | NĐ 58/2025 thay NĐ 135/2024, ban hành 03/03/2025 | https://theinvestor.vn/insight-into-vietnams-decree-58-on-renewable-and-new-energy-d14912.html ; https://blogs.duanemorris.com/vietnam/2025/08/27/vietnam-decree-58-on-development-of-renewable-energy-power-mechanisms-and-policies-for-self-production-and-self-consumption-rooftop-solar-power-systems/ | Báo/luật sư, 2025 (qua kết quả tìm kiếm) | "takes effect immediately and replaces Decree 135/2024" | High | — | Cập nhật cơ sở pháp lý; bỏ tham chiếu 135 |
| 2 | NĐ 58: trần 20%; nguồn khác nhau về cơ sở tính (công suất lắp đặt hay sản lượng thực phát/tháng) | https://vtn-partners.com/news/self-generated-and-self-consumed-rooftop-solar-power-in-vietnam-under-decree-58-2025-nd-cp.html ; https://adk-lawyers.com/en/new-policies-rooftop-solar-self-production-self-consumption-vietnam/ | Luật sư, 2025 (qua kết quả tìm kiếm) | "up to 20% of actual monthly generated output" so với "20% of installed capacity" | Med | Có (cơ sở tính) | Hỗ trợ cả giới hạn theo kW và theo kWh |
| 3 | NĐ 243/2026 (26/06/2026): bán dư ≤50% sản lượng thực phát; vượt được đến 31/12/2030 nếu lưới tiếp nhận được; vùng chưa có lưới không giới hạn | https://luatvietnam.vn/tin-van-ban-moi/tu-26-6-2026-dien-mat-troi-mai-nha-duoc-ban-toi-da-50-san-luong-dien-du-186-109883-article.html ; https://www.reccessary.com/en/news/vietnam-solar-grid-export-dppa ; https://www.bakermckenzie.com/en/insight/publications/2026/06/vietnam-decree-no-243-2026-nd-cp-enhanced-renewable-energy-dppa-framework | Báo pháp luật/luật sư, 06–08/2026 (qua kết quả tìm kiếm) | "increases the limit… from 20% to 50%" | High | — | `EXPORT_ENERGY_SHARE` mặc định 50%, cấu hình được |
| 4 | Điện xả từ BESS nối với ĐMTMN được tính là điện dư | https://www.reccessary.com/en/news/vietnam-solar-grid-export-dppa | Tin ngành, 2026 (qua kết quả tìm kiếm) | "purchasable excess electricity includes direct RTS output and energy discharged from connected BESS" | Med | Chưa thấy toàn văn | Đo và quy kết kWh xuất theo nguồn |
| 5 | NĐ 243 mở DPPA cho trung tâm dữ liệu, doanh nghiệp sạc EV; bỏ ngưỡng bên mua; bỏ trần giá DPPA vật lý; 7 → 3 bước | https://www.reccessary.com/en/news/vietnam-solar-grid-export-dppa ; https://www.nortonrosefulbright.com/en/knowledge/publications/69fad1a7/vietnam-expands-its-dppa-framework | Tin ngành/luật sư, 2026 (qua kết quả tìm kiếm) | như claim | Med | — | DPPA ở P2 (dữ liệu đo đếm) |
| 6 | NĐ 57/2025 (03/03/2025) thay 80/2024; khách hàng lớn ~200.000 kWh/tháng (Bộ Công Thương có thể đổi) | https://www.tilleke.com/insights/clear-guidance-for-direct-power-purchase-agreements-in-vietnam/3/ | Luật sư, 04/2025 (qua kết quả tìm kiếm) | "threshold remains for now at 200,000 kWh per month" | Med | NĐ 243 bỏ ngưỡng bên mua (#5) | Không hard-code ngưỡng |
| 7 | 28.254 hệ TSXTTT theo NĐ 58/243 (~1.614 MWp), chỉ ~287 hệ (~16,4 MW) đăng ký bán dư; tổng 130.811 hệ >11.200 MWp (cuối 07/2026) | https://vietnamnet.vn/en/rooftop-solar-saves-billions-of-dong-but-one-bottleneck-remains-2552186.html ; https://en.evn.com.vn/d/en-US/news/Rooftop-solar-power-still-holds-significant-development-potential-60-206-501507 | Báo/EVN, 2026 (qua kết quả tìm kiếm) | như claim | Med | — | Zero-export là chế độ phổ biến nhất → P0 |
| 8 | Chưa có giao dịch bán dư nào theo NĐ 243 (08/2026); chỉ 2/34 tỉnh ban hành chính sách theo Chỉ thị 10 | https://www.pv-magazine.com/2026/09/22/vietnam-pushes-provinces-to-accelerate-rooftop-solar-rollout/ | Tạp chí ngành, 22/09/2026 (qua kết quả tìm kiếm) | "looser surplus-power rules have not yet produced a single recorded sale" | Med | — | Đừng xây MVP quanh bán điện |
| 9 | QĐ 963/QĐ-BCT (22/04/2026): cao điểm 17h30–22h30 T2–T7; thấp điểm 0h–6h; CN không cao điểm | https://thuvienphapluat.vn/van-ban/Tai-nguyen-Moi-truong/Quyet-dinh-963-QD-BCT-2026-khung-gio-cao-diem-thap-diem-cua-he-thong-dien-quoc-gia-703327.aspx ; https://tuoitre.vn/bo-cong-thuong-chinh-thuc-thay-doi-khung-gio-tinh-gia-dien-buoi-toi-la-gio-cao-diem-2026042410430101.htm | Văn bản/báo, 04/2026 (qua kết quả tìm kiếm) | như claim | High | Ngày áp hóa đơn: xem #10 | Lịch TOU có phiên bản |
| 10 | Khung mới có thể chưa áp vào hóa đơn thực (07/2026), phụ thuộc điều chỉnh giá bình quân theo TT 60 | https://thoibaonganhang.vn/gia-dien-theo-gio-ai-co-the-huong-loi-187971.html ; https://vneconomy.vn/bo-cong-thuong-de-xuat-som-ap-dung-khung-gio-gia-dien-moi.htm | Báo, 2026 (qua kết quả tìm kiếm) | "chưa được áp dụng trên thực tế" | Low–Med | Có: luatquanghuy/vietnamsolar nói đã/dự kiến áp từ 06/2026 | Hai lịch song song; Q-A01 |
| 11 | Khung cũ TT 16/2014: cao điểm 9h30–11h30 & 17h–20h; thấp điểm 22h–4h | https://luatminhkhue.vn/quy-dinh-ve-gio-cao-diem-dien-la-luc-may-gio.aspx | Tư vấn luật (qua kết quả tìm kiếm) | như claim | High | — | Giữ cho dữ liệu lịch sử |
| 12 | Giá sản xuất QĐ 1279/QĐ-BCT (10/05/2025): ví dụ <6 kV BT 1.987 / TĐ 1.300 / CĐ 3.640 đ/kWh; giá bình quân 2.204,0655 | https://thuvienphapluat.vn/phap-luat-nha-dat/toan-van-quyet-dinh-1279-qd-bct-2025-quy-dinh-ve-gia-ban-dien-3357.html ; https://luatvietnam.vn/dien-luc/quyet-dinh-1279-qd-bct-cua-bo-cong-thuong-quy-dinh-ve-gia-ban-dien-399752-d1.html | Văn bản/tư vấn, 05/2025 (qua kết quả tìm kiếm) | bảng 4 cấp điện áp | High | — | Bảng giá theo cấp điện áp |
| 13 | NĐ 278/2026 (09/07/2026) sửa cơ chế điều chỉnh giá bình quân; chưa thấy đợt tăng giá 2026 | https://vietnamfinance.vn/siet-lai-quy-trinh-tang-gia-dien-evn-khong-the-tu-dieu-chinh-tu-2-tro-len-d147425.html | Báo, 07/2026 (qua kết quả tìm kiếm) | ngưỡng 2%/5% | Med | — | Giá có thể đổi bất kỳ lúc nào → dữ liệu |
| 14 | Giá hai thành phần: khách sản xuất ≥200.000 kWh/tháng; song song 01–06/2026; thí điểm thanh toán 07/2026–07/2027 | https://tapchicongthuong.vn/thi-diem-ap-dung-gia-dien-hai-thanh-phan-tu-1-1-2026-218800.htm ; https://lsvn.vn/thi-diem-gia-ban-le-dien-hai-thanh-phan-tu-dau-nam-2026-a162900.html | Báo ngành, 2025 (qua kết quả tìm kiếm) | "phần công suất đăng ký" | Med | Lộ trình nhiều phiên bản | `IMPORT_CAP_KW`, P1 |
| 15 | QHĐ8 điều chỉnh (QĐ 768/QĐ-TTg, 15/04/2025): BESS 10.000–16.300 MW vào 2030 (bản đầu 300 MW) | https://en.vneconomy.vn/government-approves-revised-power-development-plan-8.htm ; https://www.wfw.com/articles/vietnam-makes-major-updates-to-power-development-plan-viii/ | Báo/luật sư, 04/2025 (qua kết quả tìm kiếm) | như claim | High | — | Thị trường BESS lớn nhưng chủ yếu FTM |
| 16 | TT 62/2025/TT-BCT (26/01/2026): giá hai thành phần cho BESS độc lập ≥10 MW, ≥110 kV; IRR trần 12% | https://arcusenergyasia.com/resources/regulations/circular-62 ; https://www.lexology.com/library/detail.aspx?g=e4d68d39-f3ed-44bc-bab9-1187e6fbbceb | Tư vấn/luật, 2026 (qua kết quả tìm kiếm) | như claim | Med | OpenPR nói chưa ban hành (cũ) | Ngoài phạm vi MVP |
| 17 | Mặt trời (tập trung) kèm BESS ≥10% công suất, ≥2 h | https://www.nortonrosefulbright.com/en/knowledge/publications/7eb0008e/development-of-battery-energy-storage-systems-in-vietnam ; https://www.energy-storage.news/vietnams-path-from-zero-bess-deployments-to-meeting-ambitious-2030-energy-storage-targets/ | Luật sư/tin ngành, 2025 (qua kết quả tìm kiếm) | "at least 10%… 2 hours" | Med | Phạm vi: CSP hay mọi utility solar | Không áp cho mái nhà C&I (chưa có bằng chứng) |
| 18 | BESS lưới đầu tiên: EVNHANOI 50 MW/100 MWh (5 × 10 MW/20 MWh, TBA 110 kV), 07/2026; EVNNPC 305 MW/610 MWh ở 47 TBA | https://www.energy-storage.news/hanoi-power-corporation-inaugurates-the-first-100mwh-battery-storage-portfolio-in-vietnamese-capital/ ; https://en.evn.com.vn/d/en-US/news/EVNNPC-commissions-first-BESS-in-Ninh-Binh-60-202-501616 | Tin ngành/EVN, 07–08/2026 (qua kết quả tìm kiếm) | như claim | High | — | EVN là khách nhóm 6; ta không nhắm |
| 19 | Biểu giá trạm sạc EV riêng (QĐ 14/2025, TT 60/2025); trạm kinh doanh phải có công tơ riêng | https://vneconomy.vn/automotive/quy-dinh-moi-ve-gia-ban-dien-cho-tram-sac-xe-dien.htm ; https://lsvn.vn/chinh-thuc-co-quy-dinh-rieng-ve-gia-dien-cho-xe-sac-dien-a166968.html | Báo, 2025 (qua kết quả tìm kiếm) | như claim | Med | Mức giá chưa đối chiếu | Nhiều biểu giá/site |
| 20 | SmartLogger5000B: zero export ≤2 s, peak shaving/capacity control ≤5 s; hỗ trợ EMS bên thứ ba | https://www.photomate.eu/smartlogger5000b ; https://solar-distribution.baywa-re.de/en/commercial-storage/huawei-gs-accessories/huawei-smartlogger5000b.html | Trang nhà phân phối (qua kết quả tìm kiếm) | như claim | Med | — | Mục tiêu tham chiếu cho NFR-PERF của edge |
| 21 | Schneider EcoStruxure Microgrid Advisor: MPC trên cloud + edge; lịch 15 phút/72 h; dự phòng 48 h; OpenADR; không thay BMS tòa nhà | https://download.schneider-electric.com/doc/998-20080341_US/EcoStruxure%20Microgrid%20Advisor%20Handout.pdf ; https://www.se.com/us/en/product-range/65896 | Tài liệu hãng (qua kết quả tìm kiếm) | như claim | Med | 48 h so với 72 h giữa các tài liệu | Cloud lập lịch, edge thực thi, lịch dự phòng |
| 22 | SmartLogger3000: ≤200 thiết bị; Modbus-TCP, IEC 60870-5-104 | https://www.ahlsell.se/products/el/energilager/tillbehor/2741919---smartlogger3000c01 ; https://shop.krannich-solar.com/es-es/inversores/monitorizacion/10087/smart-logger-3000a01eu?c=469 | Trang bán lẻ (qua kết quả tìm kiếm) | như claim | Med | — | Tích hợp qua logger, không đi thẳng tới inverter |
| 23 | SMA Data Manager M: ≤50 thiết bị; peak load shaving qua Energy Maximizer (add-on SMA Premium); cần công tơ POI | https://www.sma-america.com/products/energy-management/data-manager-m-10 ; https://manuals.sma.de/SMA-Premium/en-US/17048176011.html | Tài liệu hãng (qua kết quả tìm kiếm) | như claim | Med | Khác nhau theo vùng | POI meter bắt buộc (D-02) |
| 24 | Sungrow PowerStack: EMS300CP + iSolarCloud; peak shaving, demand control; bản On&Off-Grid có VPP, VSG, black start | https://www.vicoexport.com/en/powerstack ; https://renewablewatch.in/2026/07/10/sungrow-unveils-solar-storage-solution-powerstack/ | Nhà phân phối/tin, 2024–2026 (qua kết quả tìm kiếm) | như claim | Med | Số cabinet 10 so với 25 | Hãng có EMS riêng → ta làm supervisory |
| 25 | Ampowr Cosmos: peak shaving theo giới hạn đấu nối, tự tiêu thụ, giao dịch DA/imbalance/aFRR (NL) | https://ampowr.com/energy-management-system-ems/ ; https://ampowr.com/energy-optimization-and-market-participation-through-the-use-of-ampowr-cosmos/ | Trang hãng (qua kết quả tìm kiếm) | như claim; €100k/năm là dự báo | Med | — | Giao dịch ngoài phạm vi Việt Nam |
| 26 | InfinitePower: EMS lưu trữ = giám sát + lập lịch tối ưu + chẩn đoán lỗi, điều phối BMS/PCS; EMS dùng giá theo giờ và thời tiết | https://www.infinitepowerht.com/what-is-energy-management-system-ems-and-its-functions.html ; https://www.infinitepowerht.com/what-is-the-difference-between-bms-and-ems.html | Blog hãng (qua kết quả tìm kiếm) | như claim | Med | — | Phân lớp EMS ↔ BMS ↔ PCS |
| 27 | SolarBK + Banpu NEXT + Amata: EPC–ESCO, 227 MWp mái nhà; SolarBK 2,2 MWp + 2,3 MWh BESS | https://solarbk.vn/en/article/general-news/solarbk-banpu-next-amata-sign-227-mwp-rooftop-deal-bess-becomes-core-infrastructure-as-green-industrial-parks-accelerate-in-november.html ; https://solarbk.vn/en/article/general-news/solarbk-a-year-of-accelerating-central-vietnams-green-transition.html | Tin doanh nghiệp, 2025–2026 (qua kết quả tìm kiếm) | như claim | Med | Nguồn tự công bố | Persona ESCO/EPC đa site |
| 28 | KCN Đồng Nai/Bắc Ninh: Amata Biên Hòa 18 MWp/14 nhà máy; áp lực CBAM/CSRD | https://vietnamenergy.vn/rooftop-solar-and-energy-storage-development-in-industrial-parks-field-insights-from-dong-nai-and-bac-ninh-35553.html | Tạp chí ngành, 2026 (qua kết quả tìm kiếm) | như claim | Med | — | Export dữ liệu cho ESG (D-11) |
| 29 | TSO EMS = SCADA + state estimation + contingency + OPF + AGC; Hitachi Network Manager EMS (CIM/CGMES) | https://www.hitachienergy.com/jp/ja/products-and-solutions1/grid-and-generation-management-network-manager/network-manager-energy-management-system-ems ; https://energy-solutions.co/glossary/terms/scada--ems-integration | Trang hãng/glossary (qua kết quả tìm kiếm) | như claim | High | — | Nhóm 6 ngoài phạm vi |
| 30 | IEEE 2030.7-2017: dispatch + transition; IEEE 2030.8: thử nghiệm | https://www.redalyc.org/journal/2913/291374362027/291374362027.pdf ; https://www.standards.nimonik.com/products/ieee/ieee-2030pt7/ | Bài báo/store (qua kết quả tìm kiếm) | như claim | Med | Chưa đọc toàn văn | Không tuyên bố tuân thủ 2030.7 |
| 31 | ISO 50001:2018: PDCA, EnPI, EnB; rà soát/xác nhận lại 2024 | https://www.iso.org/standard/69426.html ; https://library.e.abb.com/public/97259bfd72d54220a2762fe2a9f75537/ABBAbility_EnergyManager_ISO_50001rev1.pdf | ISO/hãng (qua kết quả tìm kiếm) | như claim | High | — | Chỉ xuất dữ liệu EnPI |
| 32 | EU EED 2023/1791 Điều 11: >85 TJ phải có EnMS chứng nhận (11/10/2027); >10 TJ phải kiểm toán (11/10/2026, sau đó ≥4 năm/lần) | https://www.dnv.com/assurance/Management-Systems/eu-directive-2023-1791-energy-efficiency-iso-50001/ ; https://gesetze.legal/eu/rl_2023_1791_eu/11 | Tổ chức chứng nhận/văn bản, 2023–2024 (qua kết quả tìm kiếm) | như claim | High | — | Bối cảnh; không ảnh hưởng MVP Việt Nam |
| 33 | Luật 77/2025/QH15 sửa Luật SDNL TK&HQ, hiệu lực 01/01/2026; 3.491 cơ sở trọng điểm (2023); ngưỡng 1.000 TOE (công nghiệp) | https://luatvietnam.vn/cong-nghiep/luat-su-dung-nang-luong-tiet-kiem-va-hieu-qua-sua-doi-2025-so-77-2025-qh15-404895-d1.html ; https://tapchicongthuong.vn/ban-hanh-danh-sach-gan-3-500-co-so-su-dung-nang-luong-trong-diem-127249.htm | Văn bản/báo (qua kết quả tìm kiếm) | như claim | Med | Nghĩa vụ chi tiết sau sửa đổi: UNKNOWN | Persona P2 |
| 34 | DERMS hướng lưới (ràng buộc điện áp/nhiệt), VPP hướng thị trường; không có định nghĩa chung | https://gridbeyond.com/virtual-power-plant-vs-derms-vs-aggregation-whats-the-difference/ ; https://www.next-kraftwerke.com/knowledge/derms | Blog vendor (qua kết quả tìm kiếm) | như claim | Med | Vendor tự định nghĩa | Không dùng thuật ngữ DERMS cho sản phẩm |
| 35 | Demand charge thường 30–70% hóa đơn C&I Mỹ, đỉnh 15 phút | https://energytoolbase.com/blog/energy-storage/mastering-demand-charge-management | Blog vendor (qua kết quả tìm kiếm) | như claim | Low–Med | — | Không áp trực tiếp ở Việt Nam |
| 36 | C&I storage Mỹ: Q1/2026 648 MWh; Q2/2026 1,8 GWh | https://seia.org/esmo ; https://seia.org/media/17746/esmo_executive_summary_q2_2026.pdf/ | Hiệp hội ngành, 2026 (qua kết quả tìm kiếm) | như claim | Med | — | Bối cảnh toàn cầu |
| 37 | Úc: Cheaper Home Batteries, pin phải VPP-capable (không bắt buộc tham gia); khoảng 400.000 lắp đặt/11,2 GWh | https://cer.gov.au/batteries ; https://www.energymagazine.com.au/400000-home-batteries-installed-but-barely-a-vpp-in-sight/ | Cơ quan nhà nước/tạp chí, 2026 (qua kết quả tìm kiếm) | như claim | Med | Số khác nhau (454.753, CEC) | "VPP-capable" thiết kế sẵn, chưa bật |
| 38 | FERC 2222: PJM/NYISO/ISO-NE 2026–2027; MISO/SPP 2029–2030 | https://www.pnnl.gov/publications/ferc-order-2222-der-policy-and-implementation-report-january-2026 ; https://www.pjm.com/-/media/DotCom/committees-groups/subcommittees/disrs/postings/updated-der-aggregator-participation-model-full-model-design.pdf | Phòng thí nghiệm QG/RTO (qua kết quả tìm kiếm) | như claim | Med | Lịch có thể đổi | Bối cảnh |
| 39 | Stem Athena tuyên bố tiết kiệm hóa đơn "lên tới 30%" (vendor claim) | https://www.stem.com/wp-content/uploads/2021/05/Stem-Solutions-Overview_Athena_May-2021_v10.pdf | Tài liệu hãng, 2021 (qua kết quả tìm kiếm) | như claim | Low | Không kiểm chứng độc lập | Không dùng số vendor làm KPI |
| 40 | Power Factors Unity: APM + CMMS (gộp Drive, Greenbyte) | https://powerfactors.com/why-you-need-an-integrated-apm-platform/ ; https://atlas.verdantix.com/vendors/power-factors | Hãng/analyst (qua kết quả tìm kiếm) | như claim | Med | — | Nhóm 3 tham chiếu cho O&M |

---

## 6. Câu hỏi mở / UNKNOWN

| Mã | Câu hỏi | Vì sao quan trọng | Cách giải |
|---|---|---|---|
| Q-A01 | Ngày khung giờ QĐ 963 thực sự áp vào hóa đơn sản xuất/kinh doanh? Trạm sạc EV theo khung nào? | Sai khung giờ thì bộ tối ưu xả sai giờ, báo cáo tiết kiệm sai | Hỏi điện lực/khách thật; đọc hóa đơn EVN tháng 9–10/2026 |
| Q-A02 | Toàn văn NĐ 58 hợp nhất với NĐ 243 (VBHN 52) và TT 29/2026: ngưỡng thông báo/đăng ký, yêu cầu thiết bị chống phát ngược, đo đếm điện dư | Quyết định chế độ và bằng chứng tuân thủ | Đọc https://storage-vnportal.vnpt.vn/gov-tnn/7350/FileQuanTriTinTuc/VBHN%2052%20Nghi%20dinh%2058%20va%20ND%20243%2030.6.pdf (URL thấy qua kết quả tìm kiếm; chưa mở được) |
| Q-A03 | Trần 50% tính theo kỳ nào (tháng/năm) và trên công tơ nào? | Thiết kế bộ đếm `EXPORT_ENERGY_SHARE` | Như Q-A02 + hỏi PC địa phương |
| Q-A04 | Giá hai thành phần: cửa sổ đo công suất (15/30/60 phút?), cách tính vượt công suất đăng ký, trạng thái thí điểm 10/2026 | Thiết kế `IMPORT_CAP` và giá trị BESS | Văn bản Bộ Công Thương/EVN |
| Q-A05 | Tỷ lệ site C&I Việt Nam có BESS; CAPEX BESS C&I (VNĐ/kWh); thời gian hoàn vốn thực tế | Định cỡ thị trường và ưu tiên M-BESS | Phỏng vấn EPC/BESS integrator |
| Q-A06 | Có thị trường DR/dịch vụ phụ trợ cho C&I ở Việt Nam không (2026–2028)? | Quyết định P2 cho VPP | Theo dõi Bộ Công Thương/NSMO |
| Q-A07 | "Tự cung 30%" cho KCN/nhà máy lớn, và "BESS là điều kiện DPPA": có văn bản không? | Nếu có thì là động lực lớn | Tìm văn bản gốc |
| Q-A08 | Nghĩa vụ chi tiết của cơ sở trọng điểm sau Luật 77/2025 (có bắt buộc hệ thống quản lý năng lượng/đo đếm số không?) | Persona P2 và tính năng xuất dữ liệu | Nghị định hướng dẫn Luật 77/2025 |
| Q-A09 | Điện lực địa phương có chấp nhận vòng zero-export bằng phần mềm (logger + meter) làm "thiết bị chống phát ngược", hay yêu cầu rơ-le riêng? (đã là gap trong nghiên cứu FusionSolar) | Kiến trúc an toàn và thứ tự ưu tiên rơ-le | Hỏi PC; xem quy định đấu nối |
| Q-A10 | Mô hình kinh doanh: thuê bao theo site/kWp/MWh BESS? Giá chấp nhận được của O&M Việt Nam? | Đóng gói sản phẩm | Phỏng vấn khách |

---

## 7. Vấn đề gửi agent khác

| # | Gửi | Vấn đề | Đề xuất |
|---|---|---|---|
| X-01 | Người viết 08 (Tối ưu), M-OPT | Cao điểm đã chuyển sang 17h30–22h30 (QĐ 963). Không có demand charge ở Việt Nam. Thuật toán kiểu Mỹ (đỉnh 15 phút) không phải lõi | Lõi MVP: TOU + `ZERO_EXPORT`/`EXPORT_LIMIT` + `IMPORT_CAP` + SOC dự phòng; luật minh bạch, không gọi là AI |
| X-02 | Người viết M-TAR (04/05) | Biểu giá phải có phiên bản theo ngày hiệu lực, theo nhóm khách hàng × cấp điện áp, có cấu trúc hai thành phần và có thể có hai lịch song song | Mô hình `TariffVersion`, `TouCalendar`, `DemandComponent` |
| X-03 | Người viết 07 (Tích hợp) | Logger của hãng (SmartLogger3000/5000B, SMA Data Manager M, Sungrow EMS300CP) đã có vòng zero-export/peak shaving ≤2–5 s và giới hạn số thiết bị (200/50) | Ưu tiên ghi setpoint/chế độ **vào logger** thay vì điều khiển từng inverter; xác minh thanh ghi Modbus/IEC 104 tương ứng |
| X-04 | Người viết 10 (An toàn) | Cloud không ở trong vòng bảo vệ. Nếu điện lực yêu cầu rơ-le chống phát ngược thì rơ-le phải ưu tiên hơn phần mềm (Q-A09) | NFR: mất kết nối → edge giữ giới hạn cuối cùng + lịch dự phòng (tham chiếu Schneider 48–72 h) |
| X-05 | Người viết 05 (Domain) | NĐ 243 tính điện xả BESS vào điện dư; trạm EV có công tơ và biểu giá riêng | `MeteringPoint` có vai trò (POI, PV, BESS, EV, sub-load) + gán hợp đồng; quy kết kWh xuất theo nguồn |
| X-06 | Người viết 00/02/11 | Nghiên cứu FusionSolar (`market_users_vietnam.md` §5) dùng NĐ 135/2024 và 20%, nay đã lỗi thời | Trích NĐ 58/2025 + 243/2026 (50% sản lượng thực phát) |
| X-07 | Người viết 14 (Nguồn) | Tất cả URL ở §5 lấy **qua kết quả tìm kiếm**. Chưa mở toàn văn văn bản pháp luật nào | Đánh dấu loại nguồn; ưu tiên kiểm chứng #3, #4, #9, #10, #14 |
| X-08 | Người viết 13 (Rủi ro) | Rủi ro pháp lý thay đổi nhanh (4 văn bản liên quan trong 18 tháng: 135 → 58 → 133 → 243; TOU 963; NĐ 278 giá) | R: "quy định thay đổi" → biểu giá/chế độ là cấu hình, không phải code |
| X-09 | Người viết 03 (Chức năng) | Ranh giới: không có microgrid transition/black start, giao dịch thị trường, SCADA lưới, kế toán carbon ở MVP | Đánh dấu "Ngoài phạm vi" trong catalog, ghi rõ lý do (§3.7) |
