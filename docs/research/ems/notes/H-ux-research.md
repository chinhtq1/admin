# H — Nghiên cứu UX/UI cho EMS đa site (PV + BESS + lưới + phụ tải + EV)

[← Mục lục](../index.html) · [09 UX/UI](../09-ux-ui-specification.html) · [03 Chức năng](../03-functional-catalog.html) · [05 Domain](../05-domain-model.html) · [08 Tối ưu](../08-energy-optimization.md) · [10 An toàn](../10-security-and-reliability.md) · [14 Nguồn](../14-source-register.md) · [15 Mô phỏng](../15-simulators-and-messaging.md)

- Tác giả: Agent H (UX/UI Researcher) · Ngày: 2026-10-10 · Trạng thái: ghi chú nghiên cứu v1, đầu vào chính cho người viết `09-ux-ui-specification.html`.
- Liên quan: [C-energy-domain](C-energy-domain.md) (quy ước dấu, KPI), [F-data-analytics](F-data-analytics.md) (cờ chất lượng dữ liệu), [B-competitors](B-competitors.md) (đối thủ), [E-device-integration](E-device-integration.md).

## 0. Ghi chú phương pháp (đọc trước)

**Giới hạn quan trọng:** trong phiên này công cụ WebSearch **đã hết hạn mức của toàn lượt chạy** (giới hạn 200 lượt dùng chung cho mọi agent) ngay từ truy vấn đầu tiên của tôi. Fetch trực tiếp cũng bị chặn. Vì vậy:

1. Bằng chứng **mạnh nhất** của ghi chú này là **9 ảnh chụp màn hình thật** của demo FusionSolar trong `docs/research/fusionsolar/03_anh_demo/`. Tôi đã xem từng ảnh bằng công cụ Read. Kèm theo là ghi chú quan sát trực tiếp `demo_observations.md` (07/10/2026) và wireframe cũ `02_wireframe/`. Nhãn nguồn: **[ẢNH THẬT]**.
2. Bằng chứng về hãng khác (SolarEdge ONE, Sungrow iSolarCloud, OpenEMS, Stem, GridBeyond, Schneider EMA, Huawei manual) **chỉ lấy lại từ các ghi chú đã có** (`B-competitors.md`, `C-energy-domain.md`, `fusionsolar/.../functions_ui_roles.md`, `source_code_clients_2.md`). Các agent đó lấy chúng qua kết quả tìm kiếm. Tôi ghi lại đúng URL họ đã ghi và đánh dấu "(qua kết quả tìm kiếm, theo ghi chú B/C/FS)". Tôi **không tự đọc** các trang này. Nhãn nguồn: **[TÀI LIỆU HÃNG/MARKETING]**.
3. **Victron VRM, Tesla Powerhub, Enphase Enlighten, giao diện iSolarCloud, giao diện OpenEMS UI, màn hình Schneider EMA:** phiên này **không thu được bằng chứng giao diện nào**. Tôi không gán tính năng UI nào cho các hãng này. Xem Q-H01.
4. **ISA-101, ISA-18.2, IEC 62682, EEMUA 191:** nội dung nêu dưới đây là hiểu biết ngành phổ biến, **chưa kiểm chứng bằng nguồn trong phiên này**. Vì vậy chúng được ghi là [INFERENCE] hoặc [UNKNOWN], và **edition = UNKNOWN (chưa kiểm chứng)**. Không được tuyên bố "tuân thủ ISA-101/18.2" dựa trên ghi chú này.
5. Đề xuất của ta có nhãn **[PROPOSAL]**.

---

## 1. Phạm vi & câu hỏi nghiên cứu

**Phạm vi:** giao diện web (NOC/vận hành, installer, chủ C&I) và app di động cho EMS đa site. Tài sản gồm PV, BESS, lưới/POC (điểm đấu nối), phụ tải và trạm sạc EV (tùy chọn). Ghi chú bao gồm nguyên tắc UX, mẫu thiết kế nên dùng và nên tránh, và ghi chú theo từng trang. Không viết code.

| RQ | Câu hỏi | Mục trả lời |
|---|---|---|
| RQ-H1 | Màn tổng quan fleet và bộ chọn org/site nên trình bày gì để O&M phát hiện site có vấn đề trong < 10 s? | §3.1, §3.2 |
| RQ-H2 | Sơ đồ dòng năng lượng nên dùng quy ước gì (hướng, dấu, hoạt ảnh, cân bằng) để không gây hiểu lầm? | §3.4 |
| RQ-H3 | Khi nào cần SLD (single-line diagram, sơ đồ một sợi) thay cho energy flow? Ký hiệu trạng thái máy cắt thế nào? | §3.5 |
| RQ-H4 | Trang chi tiết BESS, inverter, POC/công tơ và EV cần những trường gì? | §3.6–3.8 |
| RQ-H5 | Mẫu phân tích lịch sử: so sánh, nhiều trục, overlay TOU, độ phân giải? | §3.9 |
| RQ-H6 | Console cảnh báo: vòng đời, xác nhận (acknowledge), tạm gác (shelving), chống lũ cảnh báo (flood)? | §3.10 |
| RQ-H7 | Trình soạn lịch điều độ (dispatch schedule): timeline, dải TOU, ràng buộc, so sánh phiên bản? | §3.11 |
| RQ-H8 | Hộp xác nhận lệnh nguy hiểm và vòng đời lệnh (gửi → edge nhận → thiết bị áp dụng)? | §3.12 |
| RQ-H9 | Biểu thị dữ liệu cũ, mất kết nối, edge đang chạy lịch dự phòng? | §3.13 |
| RQ-H10 | Màu trạng thái (không chỉ đỏ/xanh), mật độ dữ liệu, di động? | §3.14–3.15 |
| RQ-H11 | Định dạng đơn vị (kW và kWh), số, ngày, tiền VND, song ngữ vi/en? | §3.16 |

---

## 2. Phát hiện chính

### 2.1 Từ ảnh thật FusionSolar (nghiên cứu trước, 07/10/2026)

1. **[FACT] [ẢNH THẬT] Energy flow của FusionSolar có 4 nút cố định (PV, Bộ lưu trữ, Lưới điện, Tải), mỗi nút một số kW, có nhãn trạng thái "Hòa lưới". Số liệu cân bằng: PV 1,746 + Lưới 4,309 + Lưu trữ 0,000 = Tải 6,055 kW.** Hướng lưới (nhập hay xuất) chỉ thể hiện bằng hoạt ảnh/đường nối, **không có chữ "nhập/xuất"**. Nút pin chỉ có "5%" SOC và kW, không có chữ "sạc/xả". Nguồn: `fusionsolar/03_anh_demo/01_plant_overview.jpg`.
   [INFERENCE] Ảnh tĩnh (in, chụp gửi Zalo, người mù màu) **mất thông tin hướng**. Đây là lỗi cần tránh.
2. **[FACT] [ẢNH THẬT] Nhãn và đơn vị bị lẫn giữa công suất và điện năng.** Trang tổng quan có thẻ "Công suất tự dùng" với đơn vị **kWh**. Trang chủ có "Công suất ESS định mức 144,00 **kWh**". Nguồn: `01_plant_overview.jpg`, `08_home_list_view.jpg`.
   [INFERENCE] Bản dịch tiếng Việt dùng "công suất" cho cả "capacity" lẫn "power". Với EMS có BESS (kW và kWh đều quan trọng), lỗi này nguy hiểm. Xem §3.16.
3. **[FACT] [ẢNH THẬT] Định dạng số không nhất quán trong cùng sản phẩm.** Trong locale vi có `9.216,58` (dấu chấm phân nghìn, phẩy thập phân) và `8,800` kWp (= 8,8 kWp, ba chữ số thập phân, người đọc theo kiểu en dễ hiểu thành 8 800). Bố cục logic lại dùng `1.67` (dấu chấm thập phân). Năm Phật lịch Thái `2565-01-29` lọt vào trường ngày. Nguồn: `08_home_list_view.jpg`, `03_logical_layout_module_level.jpg`, `demo_observations.md` §3.
4. **[FACT] [ẢNH THẬT] Trạng thái nhà máy và thiết bị chỉ mã hóa bằng chấm màu** (xanh lá/đỏ/xám), không có chữ hay hình dạng trong ô bảng. Ngược lại, **mức báo động** có icon khác hình dạng (bát giác, tia sét, dấu chấm than, chữ i) kèm màu và nhãn. Nguồn: `08_home_list_view.jpg`, `04_plant_device_list.jpg`.
5. **[FACT] [ẢNH THẬT] Nhãn mức báo động không nhất quán giữa hai trang:** trang chủ ghi "Cao", trang nhà máy ghi "Nặng" cho cùng mức thứ 2. Nguồn: `09_home_kpi_view.jpg`, `01_plant_overview.jpg`, `demo_observations.md` §5.1.
6. **[FACT] [ẢNH THẬT] Biểu đồ "Quản lý năng lượng" dùng hai trục Y** (kW bên trái, % SOC bên phải), thanh trượt zoom thời gian và **legend phân trang "1/2"** (ẩn một số chuỗi). Phía trên có hai thanh phân rã: Sản lượng PV = Đã tiêu thụ + Đã nạp vào lưới; Tiêu thụ = Từ quang điện + Từ lưới (kWh và %). Nguồn: `02_energy_revenue_charts.jpg`.
7. **[FACT] [ẢNH THẬT] Lịch sử thiết bị** gồm: chọn **một ngày** cộng chọn nhiều "điểm tín hiệu", nút Tìm kiếm, line chart trong ngày. Hai chuỗi có màu gần giống nhau (xanh ngọc và xanh dương). Nguồn: `06_device_history.jpg`. [INFERENCE] Không so sánh được nhiều ngày hoặc nhiều thiết bị trên một biểu đồ. Màu chuỗi khó phân biệt.
8. **[FACT] [ẢNH THẬT] Trang chi tiết inverter/EMMA là lưới key–value 3 cột** cộng bảng chuỗi PV1..PV3 (V, A). **Không thấy dấu thời gian "cập nhật lúc"** trên vùng realtime trong ảnh. Có trường "Trạng thái điều chỉnh công suất thuần: P=11.5%" (đang bị giới hạn công suất). Nguồn: `05_inverter_realtime_detail.jpg`, `07_smartassistant_emma_detail.jpg`, `demo_observations.md` §5.4.
9. **[FACT] Trang tổng quan polling `running-status` khoảng 5 s một lần. Không thấy WebSocket. List view (UI v7.0) tự làm mới mỗi 3 phút.** Nguồn: `demo_observations.md` §5.1; training deck 7.0 https://solisdepot.com/wp-content/uploads/2023/03/FusionSolar-Smart-PV-Management-System-7.0-After-sales-Technical-Training-Slides.pptx.pdf (theo `functions_ui_roles.md`).
10. **[FACT] Mẫu IA của FusionSolar:** cây tổ chức bên trái (Root → công ty → nhà máy → thiết bị), tab cấp nhà máy (Tổng quan | Bố cục | Quản lý thiết bị | …), trang chủ có hai chế độ List và KPI, cột bảng cấu hình được và lưu theo user (`viewcfg`). Nguồn: `01_plant_overview.jpg`, `demo_observations.md` §3, §5. Cùng nguồn cho thấy menu do server trả theo vai trò, guest không thấy Báo động/Báo cáo.
11. **[FACT] Alarm → ticket:** FusionSolar 7.0 có nút "New Ticket" trong alarm center, tạo ticket kèm mô tả, người xử lý và gợi ý xử lý. Nguồn: https://solisdepot.com/wp-content/uploads/2023/03/FusionSolar-Smart-PV-Management-System-7.0-After-sales-Technical-Training-Slides.pptx.pdf (theo `functions_ui_roles.md`). Các thao tác ack/clear/mask ở bản 25.x là **[UNKNOWN]** (trang manual bị chặn robots, theo `functions_ui_roles.md`).
12. **[FACT] FusionSolar có Kiosk:** link công khai hiển thị energy flow, sản lượng, doanh thu và lợi ích môi trường. Nguồn: training deck 7.0 (như trên). Dashboard màn lớn của UI cũ yêu cầu tối thiểu 1920×1080 (cùng nguồn).

### 2.2 Từ tài liệu hãng khác (lấy lại từ ghi chú B/C/FS, qua kết quả tìm kiếm)

13. **[FACT] SolarEdge ONE for C&I:** Site Admin quản lý User Role, Monitoring Access, Public Access, **Kiosk View**, API Access, quyền xem biểu đồ PR và ô tick **"Expose to alerts notifications" theo từng user**. https://knowledge-center.solaredge.com/sites/kc/files/se-site-admin-in-solaredge-one-for-c&i-user-guide.pdf (qua kết quả tìm kiếm, theo B L32).
14. **[FACT] SolarEdge ONE for C&I:** phân tích fleet tới cấp module, digital twin 3D, live alerts, PV + BESS + EV + tài sản tòa nhà. https://www.solaredge.com/us/solaredge-one-for-commercial-and-industrial-energy-optimization-platform (qua kết quả tìm kiếm, theo B L30). Đây là mô tả marketing, không phải ảnh giao diện.
15. **[FACT] OpenEMS gồm Edge, Backend và UI (trình duyệt/di động).** Quy ước: lưới dương = mua, ESS dương = xả, ESS âm = sạc. https://openems.github.io/openems.io/openems/latest/edge/architecture.html ; https://openems.github.io/openems.io/openems/latest/edge/configuration.html ; https://community.openems.io/t/can-consumptionactivepower-be-negative/321 (qua kết quả tìm kiếm, theo B L43 và C #2).
16. **[FACT] GridBeyond ViewPoint Lens (9/2025):** hiển thị hồ sơ tải, phản ứng trong sự kiện DR và tổng hợp doanh thu cho khách C&I. https://secure.businesswire.com/news/home/20250930978130/en/GridBeyond-Launches-ViewPoint-Lens-to-Empower-Energy-Customers-With-Greater-Visibility-and-Control (qua kết quả tìm kiếm, theo B L49).
17. **[FACT] Stem PowerTrack EMS có "edge UI"** tách khỏi phần mềm danh mục trên cloud. https://www.businesswire.com/news/home/20250902991311/en (qua kết quả tìm kiếm, theo B L46). [INFERENCE] Đối thủ lớn có hai lớp UI: cloud cho danh mục và HMI tại site cho kỹ sư. Ta cần ít nhất một trang "local" tối giản trên edge (xem §4).
18. **[FACT] Schneider EMA:** lịch 15 phút trên horizon 72 h, có lịch mặc định 48 h khi mất kết nối (tài liệu khác nói 72 h). https://download.schneider-electric.com/doc/998-20080341_US/EcoStruxure%20Microgrid%20Advisor%20Handout.pdf (qua kết quả tìm kiếm, theo A #21). [INFERENCE] UI phải cho thấy **lịch nào đang chạy** (lịch cloud mới nhất hay lịch dự phòng ở edge).
19. **[FACT] Thẻ "tesla-style-solar-power-card" mã nguồn mở** mô hình hóa energy flow bằng **7 cạnh có hướng, giá trị không âm** giữa 4 nút. Giá trị nút suy ra từ tổng các cạnh. Tốc độ chấm hoạt ảnh tỉ lệ với công suất (`speed = speedFactor × value / 1000`). Có chế độ độ dày nét tỉ lệ công suất, tùy chọn ẩn cạnh không hoạt động, và tô màu nút nhà theo nguồn chiếm ưu thế. README nói "all sensors need to be positive values". https://github.com/reptilex/tesla-style-solar-power-card/blob/master/README.md ; https://github.com/reptilex/tesla-style-solar-power-card/blob/master/src/models/SensorElement.ts#L78-L90 (theo `source_code_clients_2.md`, đã đọc mã nguồn trong nghiên cứu trước). Đây là thẻ cộng đồng, **không phải sản phẩm Tesla**.
20. **[FACT] Quy ước dấu không thống nhất giữa các hãng/cộng đồng.** Huawei `meterPower` coi dương = xuất; thẻ Tesla-style coi lưới − nhập/+ xuất, pin + sạc/− xả; OpenEMS coi lưới + mua, ESS + xả. https://community.openenergymonitor.org/t/is-there-a-standard-for-import-export-positive-negative-power-flow/15149 (qua kết quả tìm kiếm, theo C #2). Agent C đã chọn: **lưới + = nhập, BESS + = xả** và khuyến nghị UI dùng **nhãn hướng** thay vì số có dấu (C, X-C01).
21. **[FACT] Việt Nam xác định Pmax theo chu kỳ tích phân 30 phút** trong thí điểm giá điện hai thành phần. https://daibieunhandan.vn/trien-khai-thu-nghiem-gia-ban-le-dien-hai-thanh-phan-tu-thang-10-2025-10390577.html (qua kết quả tìm kiếm, theo C #3). Khung giờ cao điểm buổi tối đã được điều chỉnh năm 2026: https://tuoitre.vn/bo-cong-thuong-chinh-thuc-thay-doi-khung-gio-tinh-gia-dien-buoi-toi-la-gio-cao-diem-2026042410430101.htm (theo danh sách nguồn của A). [INFERENCE] UI phải có widget "demand 30 phút hiện tại so với ngưỡng", và dải TOU phải lấy từ dữ liệu biểu giá có hiệu lực theo ngày, không vẽ cứng.
22. **[FACT] BESS ở khí hậu nóng có aux đáng kể. Ban đêm `p_bess` có thể hơi âm khi pin đứng yên (aux lấy nguồn sau công tơ BESS), "không phải đang sạc".** Theo C §3.5 (dẫn PNNL MESA-1 https://www.sandia.gov/ess-ssl/wp-content/uploads/2019/07/PNNL-MESA-1-Final-Test-Report_Reduced.pdf). [INFERENCE] UI không được suy ra chữ "Đang sạc" từ dấu P. Trạng thái phải lấy từ PCS/BMS.

### 2.3 Thực hành HMI/cảnh báo công nghiệp (chưa kiểm chứng nguồn trong phiên)

23. **[INFERENCE] ISA-101 (HMI hiệu năng cao):** nền trung tính (xám nhạt), màu bão hòa chỉ dành cho trạng thái bất thường, phân cấp màn hình 4 mức (L1 tổng quan khu vực → L2 điều khiển đơn vị → L3 chi tiết thiết bị → L4 chẩn đoán), dùng xu hướng và đại lượng tương đối thay vì số rời. Edition: **UNKNOWN (chưa kiểm chứng; thường được trích là ANSI/ISA-101.01-2015)**.
24. **[INFERENCE] ISA-18.2 / IEC 62682 (quản lý cảnh báo):** vòng đời có các trạng thái Normal, Unacknowledged, Acknowledged, Return-to-normal chưa ack, **Shelved** (người vận hành tạm gác, có thời hạn), **Suppressed by design** (logic tự chặn, ví dụ thiết bị cha mất kết nối), **Out of service** (bảo trì). Mỗi cảnh báo phải có nguyên nhân, hậu quả, hành động và thời gian phản hồi (rationalization). Edition: **UNKNOWN** (thường trích ANSI/ISA-18.2-2016 và IEC 62682 bản 2014 hoặc mới hơn, chưa kiểm chứng).
25. **[UNKNOWN] Ngưỡng tham chiếu EEMUA 191** (khoảng ≤ 1 cảnh báo / 10 phút / người vận hành ở trạng thái ổn định; "flood" khi > 10 cảnh báo / 10 phút) cần kiểm chứng trước khi dùng làm NFR.
26. **[INFERENCE] Quy ước màu máy cắt khác nhau theo vùng.** Ở Bắc Mỹ thường đỏ = đóng/có điện, xanh lá = mở. Ở nhiều nơi khác thì ngược lại. Do đó SLD **không được** dùng màu làm kênh duy nhất cho trạng thái máy cắt. Cần kiểm chứng tập quán SCADA của EVN/điện lực Việt Nam (Q-H05).

---

## 3. Phân tích chi tiết theo chủ đề

### 3.0 Persona và mức màn hình (khung dùng cho mọi trang)

| Persona | Bối cảnh | Nhu cầu chính | Mật độ | Thiết bị |
|---|---|---|---|---|
| NOC / O&M operator (installer, đơn vị O&M) | Theo dõi 20–500 site, ca trực | Phát hiện bất thường, ack cảnh báo, tạo ticket, đổi chế độ khi cần | Cao (compact) | Desktop 1920×1080, màn lớn |
| Kỹ sư vận hành site / commissioning | Tại site, trên laptop/điện thoại | Xem SLD, chi tiết thiết bị, kiểm tra dấu, ra lệnh có kiểm soát | Cao | Laptop, mobile, HMI edge local |
| Energy manager / chủ C&I | Hằng ngày hoặc hằng tuần | Hóa đơn, đỉnh 30 phút, tiết kiệm, báo cáo | Trung bình (comfortable) | Desktop, mobile |
| Lãnh đạo / CFO / ESG | Hằng tháng | Giá trị tạo ra (VND), CO₂, so sánh site | Thấp | Mobile, PDF |
| Khách/kiosk | Sảnh nhà máy | Energy flow, sản lượng, CO₂ | Thấp, chữ lớn | Màn hình công cộng |

[PROPOSAL] Phân cấp màn hình theo tinh thần ISA-101 (INFERENCE #23), ánh xạ sang EMS:

| Mức | EMS tương ứng | Câu hỏi trả lời |
|---|---|---|
| L1 | Fleet overview (danh mục) | Site nào cần chú ý ngay? |
| L2 | Site dashboard (energy flow + KPI + kế hoạch) | Site đang làm gì, có đúng kế hoạch không? |
| L3 | Trang tài sản: BESS, PV/inverter, POC/công tơ, EV, SLD | Thiết bị nào lệch, lệch bao nhiêu? |
| L4 | Chẩn đoán: điểm tín hiệu thô, register, log lệnh, cell-level | Tại sao? |

### 3.1 Fleet overview (L1)

Quan sát FusionSolar [ẢNH THẬT, `08_home_list_view.jpg`, `09_home_kpi_view.jpg`]: banner KPI tổng (kW hiện tại, kWh hôm nay, doanh thu, kW định mức inverter, kWh ESS, MWh tổng), donut trạng thái nhà máy (Thường/Lỗi/Ngắt kết nối), donut báo động 4 mức. Bên dưới là bảng 16 cột có header bị cắt chữ ("Tổng côn…", "Năng lượ…").

Đánh giá:
- Tốt: số đếm trạng thái và báo động bấm được (dù guest không mở được); cột cấu hình được và lưu theo user; có kWh/kWp để so sánh site khác cỡ.
- Kém: header bị cắt chữ; donut chiếm nhiều diện tích mà chỉ chứa 3–4 số; trạng thái chỉ bằng màu; bảng sắp theo cột chứ không có thứ tự "cần chú ý trước"; không có cột BESS (SOC, chế độ) hoặc đỉnh 30 phút; không thấy tuổi dữ liệu.

[PROPOSAL] Nội dung fleet overview cho EMS:
- **Hàng "cần chú ý"** đặt đầu trang: danh sách site sắp theo **điểm ưu tiên** = mức cảnh báo cao nhất chưa ack, site mất kết nối > N phút, site vượt hoặc sắp vượt ngưỡng nhập (demand), BESS ngoài kế hoạch, edge đang chạy lịch dự phòng. Mỗi dòng nêu **lý do bằng chữ**.
- **Bảng site** (mặc định), cột gợi ý: Trạng thái (icon + chữ) · Site · Org/khách hàng · Tuổi dữ liệu · P lưới (nhãn Nhập/Xuất) · Demand 30 phút hiện tại / ngưỡng (thanh %) · PV kW (và % của kWp) · BESS: chế độ + SOC % + P (Sạc/Xả) · EV kW · Cảnh báo (đếm theo mức) · Kế hoạch: đúng/lệch · Tiết kiệm hôm nay (VND).
- **Chế độ bản đồ** (tùy chọn P2) và **chế độ lưới thẻ (tile)** cho màn lớn. Tile 1 site gồm tên, chấm trạng thái có hình dạng, sparkline P lưới 24 h có ngưỡng.
- Bộ lọc nhanh: Org, tỉnh/khu công nghiệp, loại tài sản (có BESS / có EV), trạng thái, "chỉ site có cảnh báo chưa ack".
- KPI tổng chỉ cộng những gì **cộng được có nghĩa** (kW, kWh, VND). Không cộng PR hay SOC; dùng trung bình có trọng số và ghi rõ trọng số.

### 3.2 Bộ chọn org/site và điều hướng

Quan sát [ẢNH THẬT, `01_plant_overview.jpg`]: FusionSolar dùng **cây trái cố định** Root → công ty → nhà máy → thiết bị, có ô tìm kiếm với dropdown loại đối tượng, thu gọn được. Ưu điểm: thấy ngữ cảnh tổ chức. Nhược điểm: chiếm khoảng 250 px ngang trên mọi trang, kém trên mobile, và với 500 site thì cây dài.

[PROPOSAL]
- **Breadcrumb ngữ cảnh** ở header: `Org ▸ Site ▸ Tài sản`. Mỗi đoạn là một **combobox tìm kiếm** (gõ tên, mã site, tỉnh, SN thiết bị). Phím tắt `/` hoặc `Ctrl+K` mở bộ chuyển site toàn cục, có danh sách "gần đây" và "ghim".
- Cây trái là **tùy chọn** (bật/tắt, nhớ theo user bằng localStorage), mặc định tắt ở màn < 1280 px.
- URL chứa `orgId/siteId/assetId` để deep-link từ e-mail/Zalo cảnh báo mở đúng trang.
- Khi user chỉ có 1 site (chủ C&I nhỏ): bỏ qua L1, vào thẳng site dashboard.
- Đổi site phải **giữ tab hiện tại** (đang ở "BESS" thì sang site khác vẫn ở "BESS" nếu site đó có BESS).
- Mỗi trang site hiện **múi giờ site** (Asia/Ho_Chi_Minh, UTC+7) khi khác múi giờ trình duyệt của user.

### 3.3 Site energy dashboard (L2)

Quan sát [ẢNH THẬT, `01_plant_overview.jpg`, `02_energy_revenue_charts.jpg`]: header tên + chấm trạng thái + thời tiết 3 ngày; 4 thẻ KPI; energy flow; lợi ích môi trường; báo động theo mức; thông tin site; biểu đồ năng lượng ngày/tháng/năm/tuổi thọ; doanh thu.

Đánh giá: "lợi ích môi trường" chiếm vị trí trung tâm ngang energy flow, có giá trị với owner/kiosk nhưng không với vận hành. Không có kế hoạch BESS hoặc TOU. Không có giới hạn nhập/xuất.

[PROPOSAL] Bố cục site dashboard (desktop, 12 cột):

| Vùng | Nội dung | Ghi chú |
|---|---|---|
| Header (toàn chiều ngang) | Tên site · trạng thái (icon + chữ) · **chế độ vận hành hiện tại** (vd "Peak shaving + TOU", "Lịch dự phòng edge", "Thủ công") · tuổi dữ liệu · giờ site · dải TOU hiện tại ("Cao điểm đến 20:00") | Chế độ và nguồn lệnh là thông tin quan trọng nhất của EMS, phải luôn thấy |
| Trái (5 cột) | Energy flow (§3.4) | Có số và chữ hướng |
| Phải (7 cột) | KPI hôm nay: Nhập lưới kWh · Xuất lưới kWh · PV kWh · BESS sạc/xả kWh · Demand 30 phút cao nhất tháng (kW) so với ngưỡng · Tiết kiệm VND (ước tính, có nhãn phương pháp) | Mỗi thẻ có đơn vị rõ, tooltip định nghĩa (khớp K-ID của C) |
| Giữa (toàn ngang) | **Biểu đồ "Hôm nay: thực tế và kế hoạch"**: P lưới, P PV, P BESS, P tải (kW), SOC % (trục phải), đường ngưỡng nhập, dải nền TOU, vùng tương lai là kế hoạch/dự báo (nét đứt) | Mẫu then chốt của EMS, FusionSolar không có |
| Dưới trái | Cảnh báo đang hoạt động (top 5, theo mức) + link console | |
| Dưới phải | Tài sản: thẻ tóm tắt BESS / PV / EV / công tơ, mỗi thẻ dẫn sang L3 | |

### 3.4 Quy ước sơ đồ dòng năng lượng

Bằng chứng: #1 (FusionSolar, ảnh thật), #19 (thẻ Tesla-style, mã nguồn), #20 (dấu không thống nhất), #22 (aux BESS).

[PROPOSAL] Quy tắc:
1. **Nút:** Lưới (POC), PV, BESS, Tải (tòa nhà/nhà máy), EV (nếu có), Máy phát (nếu có). Nút tải có thể tách tải nền và tải điều khiển được. EV và máy phát là nút hạng nhất, không gộp vào tải (khớp gợi ý `source_code_clients_2.md` §7).
2. **Cạnh có hướng, giá trị không âm.** Mỗi cạnh mang **mũi tên tĩnh** chỉ hướng (không chỉ dựa vào hoạt ảnh). Nút hiện **số không dấu + chữ hướng**: "Nhập 4,31 kW" / "Xuất 1,20 kW"; BESS: "Xả 50,0 kW" / "Sạc 50,0 kW" / "Chờ" (trạng thái từ PCS/BMS, không suy từ dấu, xem #22). Dữ liệu nội bộ vẫn theo quy ước dấu của C (lưới + = nhập, BESS + = xả); UI chỉ hiển thị nhãn.
3. **Phân bổ cạnh** (PV→tải, PV→BESS, lưới→BESS…) là quy ước kế toán (C #14). UI hiển thị cạnh **do backend tính** theo một thuật toán duy nhất. Tooltip ghi "phân bổ ước tính". Không tự tính ở frontend.
4. **Hoạt ảnh:** tốc độ hoặc độ dày tỉ lệ công suất, có ngưỡng tối thiểu để cạnh nhỏ vẫn thấy. Cạnh dưới ngưỡng (vd < 1% công suất định mức site) thì ẩn hoặc hiện mờ. **Dừng hoạt ảnh khi dữ liệu cũ** (§3.13). Tôn trọng `prefers-reduced-motion`: thay hoạt ảnh bằng mũi tên tĩnh.
5. **Kiểm tra cân bằng:** nếu Σ nguồn − Σ tải lệch quá ngưỡng (vd 3% hoặc 2 kW) thì hiện huy hiệu "Cân bằng lệch X kW". Nguyên nhân thường là thiếu công tơ, sai dấu hoặc lệch thời điểm mẫu. Nó giúp phát hiện lỗi commissioning (C: phép thử dấu).
6. **Dấu thời gian chung:** mọi số trên sơ đồ phải cùng một lát thời gian. Hiện "Lúc 14:32:05". Nếu các nguồn lệch nhau > 2 chu kỳ thì cảnh báo.
7. **Ranh giới đo:** nút BESS ghi rõ đo ở đâu (AC tại PCS hay tại công tơ BESS có aux), khớp `rte_boundary` của C.
8. **Màu nút theo loại năng lượng, không theo trạng thái** (§3.14). FusionSolar dùng viền vàng (PV), xanh lá (pin), tím (lưới), xanh dương (tải) [ẢNH THẬT]. Ta không sao chép màu Huawei, nhưng giữ nguyên tắc "một loại năng lượng = một màu cố định trên toàn sản phẩm".
9. **Đơn vị trên sơ đồ luôn là kW** (công suất tức thời). Không đặt kWh lên sơ đồ live. Chế độ "Hôm nay" (tùy chọn) đổi toàn bộ sang kWh và đổi tiêu đề thành "Điện năng hôm nay (kWh)".

### 3.5 SLD (single-line diagram)

Bằng chứng ta có: C mô tả các điểm đo chuẩn `MTR_POC`, `MTR_PV`, `MTR_BESS`, `MTR_AUX`… và sơ đồ ASCII (C §3.3). FusionSolar chỉ có "bố cục logic" (inverter → chuỗi → module) [ẢNH THẬT, `03_logical_layout_module_level.jpg`], **không thấy SLD điện**. Không có bằng chứng giao diện SLD của các đối thủ trong phiên này [UNKNOWN].

Phân biệt: energy flow trả lời "năng lượng đi đâu". SLD trả lời "điện đi qua thiết bị nào, máy cắt nào đang đóng, công tơ đặt ở đâu".

[PROPOSAL]
- SLD là trang L3 cho kỹ sư và O&M. Nó được sinh từ **mô hình tài sản** (topology trong domain model của agent 05), không vẽ tay bằng ảnh.
- Ký hiệu theo IEC 60617 (edition UNKNOWN). Trạng thái máy cắt/contactor dùng **hình dạng** (ký hiệu đóng/mở) **kèm chữ** "ĐÓNG"/"MỞ"/"KHÔNG RÕ". Không dựa màu (INFERENCE #26).
- Đặt **vị trí công tơ** lên SLD (biểu tượng công tơ với mã `MTR_POC`…), hiện P và hướng ngay tại công tơ. Đây là công cụ commissioning: kiểm tra công tơ đặt đúng chỗ và đúng dấu.
- Thanh cái có điện / mất điện: nét đậm và liền khi có điện, nét đứt khi không điện; trạng thái **không rõ** (mất dữ liệu) dùng hoa văn gạch chéo, không dùng màu "bình thường".
- MVP: SLD **chỉ đọc**. Thao tác đóng/cắt từ cloud **không làm** (cloud không được bỏ qua bảo vệ thiết bị; thao tác đóng/cắt thuộc HMI tại chỗ hoặc relay).

### 3.6 Trang BESS (L3/L4)

Quan sát [ẢNH THẬT]: FusionSolar demo chỉ có SOC trên energy flow và trong biểu đồ; không có trang BESS chi tiết trong demo guest [UNKNOWN cho bản đầy đủ]. Huawei Owner manual 25.2.0 có mục "Battery Control Parameters" (theo `functions_ui_roles.md`). Giới hạn dòng sạc/xả do BMS cấp (CCL/DCL) là khái niệm phổ biến trong cộng đồng Victron: https://communityarchive.victronenergy.com/questions/310041/maximum-limit-of-dcl-and-ccl-numbers.html (URL trong ghi chú trước; tôi chưa đọc nội dung).

[PROPOSAL] Cấu trúc trang BESS:

| Khối | Trường | Đơn vị / ghi chú |
|---|---|---|
| Trạng thái | Chế độ PCS (Chờ/Sạc/Xả/Lỗi/Dừng khẩn), trạng thái BMS, contactor DC (ĐÓNG/MỞ), on-grid/off-grid, nguồn lệnh hiện tại (Lịch/Thủ công/Dự phòng/Bảo vệ) | Chữ + icon |
| Công suất | P thực tế, P setpoint, **P cho phép** (giới hạn hiện tại = min của rating, CCL/DCL × V, giới hạn của EMS), Q | kW, kvar. Hiện "bị giới hạn bởi BMS" khi P_setpoint > P_cho_phép |
| Năng lượng | SOC (%), năng lượng khả dụng (kWh) tới SOC_min và SOC_max, SOC dự trữ backup | Hiển thị **cả % và kWh**; dải SOC_min…SOC_max trên thanh SOC |
| Sức khỏe | SOH (%), EFC (chu kỳ tương đương), throughput (MWh), RTE (có **ranh giới đo**, theo C K16), aux (kWh/ngày) | Nguồn SOH ghi rõ: BMS báo hay ước tính |
| Rack/cluster | Bảng rack: SOC, V, I, T min/max, ΔV cell (mV), ΔT (°C), cảnh báo | **Heatmap** cell V/T (L4), sắp theo độ lệch |
| Môi trường | Nhiệt độ/độ ẩm container, HVAC, PCCC (trạng thái **chỉ đọc**) | PCCC/E-stop: chỉ hiển thị |
| Biểu đồ | P và SOC 24 h hoặc 7 ngày, đường P cho phép, dải TOU | |

Ràng buộc an toàn trên UI: không có nút nào trên cloud ghi đè giới hạn BMS/PCS. Mọi giá trị nhập (SOC_min, công suất tối đa) được **clamp ở edge**. UI hiển thị giới hạn cứng của thiết bị ở dạng chỉ đọc bên cạnh ô nhập.

### 3.7 Trang PV / inverter

Quan sát [ẢNH THẬT, `05_inverter_realtime_detail.jpg`]: hình minh họa PV → inverter bên trái; bảng chuỗi (V, A); 3 cột key–value; tab Lịch sử. Có trường derating "P=11.5%".

[PROPOSAL]
- Giữ bảng chuỗi (MPPT/string) nhưng thêm **cột so sánh tương đối** (dòng chuỗi / trung vị cùng inverter, %). Chuỗi lệch hơn ngưỡng thì tô nền bất thường. Chuỗi 0 A ban ngày phải nổi bật, kể cả khi đó là chuỗi không dùng; cần cấu hình "chuỗi không đấu" để tránh báo sai (PV3 = 0 trong ảnh là ví dụ).
- Hiển thị **giới hạn công suất** rõ: "Đang bị giới hạn 11,5% (lệnh từ EMS / từ lưới / từ inverter tự bảo vệ)". Nguồn giới hạn quan trọng ở site zero-export Việt Nam (C #10: PR thô thấp giả tạo khi bị curtail).
- Tách "điện năng tiềm năng bị cắt" thành KPI nếu agent C/F có (K-ID).
- Key–value grid: nhóm theo AC / DC / nhiệt / cách điện / thông tin; **mỗi nhóm có dấu thời gian**.

### 3.8 POC / công tơ / demand; EV

[PROPOSAL] Trang Lưới/POC:
- **Đồng hồ demand 30 phút:** trung bình đã tích lũy của chu kỳ hiện tại, **dự báo cuối chu kỳ** (nếu giữ P hiện tại), ngưỡng đặt, Pmax của tháng (kW, lúc nào). Chu kỳ là tham số biểu giá (15/30/60 phút, theo C #3), không hard-code 30.
- Thanh "nhập hiện tại / giới hạn nhập" và "xuất / giới hạn xuất (zero-export)".
- Thông số điện: U, I theo pha, PF, f, Q. Nếu có công tơ đo chất lượng điện năng thì thêm THD; nếu không thì ẩn mục, không hiện 0.
- Bảng điện năng theo dải TOU hôm nay/tháng (kWh × đơn giá VND = tiền), ghi rõ "ước tính, không phải hóa đơn".

[PROPOSAL] Trang EV (tùy chọn): danh sách trụ (trạng thái OCPP dạng chữ: Available/Charging/SuspendedEV/SuspendedEVSE/Faulted kèm nhãn tiếng Việt), kW hiện tại, **giới hạn do EMS áp** (kW) và lý do ("giảm do peak shaving"), phiên sạc. FusionSolar demo có cột "Trạm sạc" nhưng trống [ẢNH THẬT]. Trạng thái OCPP cần agent E xác nhận theo phiên bản OCPP.

### 3.9 Phân tích lịch sử (L3/L4)

Quan sát [ẢNH THẬT, `06_device_history.jpg`, `02_energy_revenue_charts.jpg`]: chọn 1 ngày + nhiều điểm tín hiệu; tab Ngày/Tháng/Năm/Tuổi thọ; dataZoom; legend phân trang; trục kép kW/%.

[PROPOSAL] "Trend explorer":
- Chọn khoảng thời gian tự do, có preset (Hôm nay, Hôm qua, 7 ngày, Tháng này, Kỳ hóa đơn). **Độ phân giải tự chọn theo khoảng** (raw ≤ 1 ngày, 5 phút ≤ 31 ngày, 1 h ≤ 1 năm, ngày > 1 năm) và hiện rõ "Độ phân giải: 5 phút, trung bình".
- **Nhiều trục nhưng tối đa 2 đơn vị trên một panel.** Thêm đơn vị thứ 3 thì tự tách thành panel xếp chồng, đồng bộ trục thời gian và con trỏ (kiểu small multiples). Tránh trục kép mơ hồ.
- Hai loại đại lượng không trộn: **công suất (kW) = đường**; **điện năng (kWh) = cột theo bucket**. Tiêu đề trục luôn có đơn vị.
- **Overlay:** dải TOU (nền), đường ngưỡng, sự kiện (cảnh báo, lệnh, thay đổi chế độ) dạng marker trên trục thời gian; bấm marker mở chi tiết.
- **So sánh:** cùng điểm của nhiều thiết bị; cùng site giữa hai khoảng (tuần này / tuần trước); thực tế với kế hoạch/dự báo.
- **Khoảng trống dữ liệu** vẽ là khoảng hở (không nối đường). Giá trị nội suy/ước tính dùng nét khác và có tooltip theo cờ chất lượng của F (MEASURED/ESTIMATED/SUBSTITUTED…).
- Legend không phân trang. Quá 8 chuỗi thì dùng danh sách chọn có ô tìm kiếm.
- Xuất CSV/XLSX có đơn vị trong header, múi giờ trong header, timestamp ISO 8601 có offset `+07:00`.
- Lưu "view" (bộ điểm, khoảng, overlay) theo user và chia sẻ bằng link (FusionSolar có `viewcfg` lưu cấu hình theo user [FACT, demo_observations §3]).

### 3.10 Console cảnh báo

Bằng chứng: FusionSolar có 4 mức (Nghiêm trọng/Cao(Nặng)/Thấp/Cảnh báo), donut đếm theo mức, alarm → ticket (#11); không thấy ack/shelve trong demo [UNKNOWN]. SolarEdge cho bật/tắt nhận cảnh báo theo từng user (#13). Ampowr chuyển cảnh báo về đội hỗ trợ trung tâm (B: AmpiHealth). Thực hành công nghiệp: #24, #25 (chưa kiểm chứng).

[PROPOSAL] Mô hình trạng thái cảnh báo (đối chiếu ISA-18.2, chưa tuyên bố tuân thủ):

| Trạng thái hoạt động | Trạng thái ack | Hiển thị | Ghi chú |
|---|---|---|---|
| Active | Chưa ack | Icon mức + **nhấp nháy chỉ icon** (không nhấp cả dòng), in đậm | Âm thanh tùy chọn cho NOC, chỉ mức 1–2 |
| Active | Đã ack | Icon mức, không nhấp, chữ thường | Ghi người ack và thời điểm |
| Đã hết (RTN) | Chưa ack | Icon rỗng + "Đã hết, chưa xác nhận" | Có thể cấu hình tự ack khi RTN cho mức 3–4 |
| Shelved | — | Chuyển sang tab "Tạm gác", đếm riêng ở header | Bắt buộc **lý do + thời hạn** (tối đa vd 8 h, theo vai trò); tự bỏ gác khi hết hạn; ghi audit |
| Suppressed by design | — | Ẩn khỏi danh sách chính, đếm "N cảnh báo bị chặn do thiết bị cha" | Vd: gateway mất kết nối → chặn cảnh báo "mất kết nối" của mọi thiết bị con; site offline → chặn cảnh báo giá trị |
| Out of service | — | Tab "Bảo trì" | Gắn với lệnh công tác/ticket bảo trì, có giờ bắt đầu và kết thúc |

Quy tắc:
- **Không được shelve** các cảnh báo an toàn do thiết bị phát ra (cháy/khói, E-stop, BMS bảo vệ cấp cao nhất, lỗi cách điện). Với các cảnh báo này, UI chỉ cho ack và ghi chú. [PROPOSAL; danh sách cụ thể cần agent 10 và E chốt.]
- **Chống lũ cảnh báo (flood):** khi một site phát > N cảnh báo mới trong 10 phút (N cấu hình được; giá trị tham khảo EEMUA còn UNKNOWN #25), console **gom thành một dòng "Lũ cảnh báo tại Site X (37)"** có nguyên nhân gốc đoán được (thiết bị cha chung, thời điểm mất kết nối) và nút mở rộng. Thông báo đẩy (push/e-mail/Zalo) **gộp thành 1**.
- **Khử dao động (chattering):** cảnh báo lặp > K lần/giờ được gom với bộ đếm; gợi ý chỉnh deadband/delay cho người quản trị (không tự đổi).
- Cột console: Mức (icon+chữ) · Thời điểm bắt đầu (giờ site) · Thời lượng · Site · Tài sản · Mã + mô tả · Giá trị lúc kích hoạt / ngưỡng · Trạng thái · Người ack · Ticket. Lọc theo mức, site, loại tài sản, trạng thái; **mặc định sắp mức trước, thời gian sau**.
- Chi tiết cảnh báo: nguyên nhân có thể, **hậu quả nếu bỏ qua**, hành động khuyến nghị, thời gian phản hồi mục tiêu, biểu đồ ±2 h quanh thời điểm kích hoạt, lịch sử cùng mã trên cùng tài sản, nút "Tạo ticket".
- **Nhãn mức thống nhất** (bài học #5): định nghĩa 4 mức một lần trong i18n, dùng chung mọi trang. Đề xuất: Khẩn cấp / Cao / Trung bình / Thông tin. Mỗi mức có icon hình dạng riêng.
- Định tuyến: đăng ký theo user × site × mức (kiểu SolarEdge #13). Hai chế độ: khách tự giám sát và O&M giám sát hộ (B).
- **Không gọi luật ngưỡng cố định là "AI".** Phát hiện bất thường thống kê/ML (nếu có) phải ghi nhãn phương pháp và độ tin cậy.

### 3.11 Trình soạn lịch điều độ (dispatch schedule)

Bằng chứng: Schneider EMA lập lịch 15 phút/72 h, có lịch dự phòng (#18). OpenEMS có scheduler (https://openems.github.io/openems.io/openems/latest/edge/scheduler.html, URL trong ghi chú trước; chưa đọc). Việt Nam: demand 30 phút (#21), TOU thay đổi theo văn bản (#21). Ảnh giao diện của trình soạn lịch đối thủ: **không có** [UNKNOWN].

[PROPOSAL] Thiết kế:
- **Timeline ngang 48 h** (mặc định hôm nay + mai), ô thời gian 15 phút (đơn vị lập lịch; cấu hình được), con trỏ "bây giờ".
- **Hàng (swimlane):**
  1. Dải TOU (nền màu + nhãn chữ "Cao điểm"/"Bình thường"/"Thấp điểm" + đơn giá VND/kWh), lấy từ biểu giá có hiệu lực.
  2. Dự báo PV và tải (kW, P50, dải P10–P90 nếu có).
  3. **Kế hoạch BESS** (kW, cột trên/dưới trục: Xả lên trên, Sạc xuống dưới, kèm chữ).
  4. **SOC dự kiến** (%) với dải SOC_min/SOC_max/dự trữ backup; vi phạm thì tô vùng và báo lỗi.
  5. P lưới dự kiến so với ngưỡng nhập/xuất.
  6. Giới hạn EV (nếu có).
  7. Chế độ theo khối (Tự tiêu thụ / Peak shaving / Arbitrage / Dự phòng / Thủ công).
- **Chỉnh sửa:** kéo thả khối chế độ; nhập số cho ô hoặc khoảng; "áp mẫu ngày" (template theo ngày trong tuần/ngày lễ). Có **cửa sổ đóng băng** (vd 15–30 phút tới không sửa được) để edge không nhận lệnh sát giờ.
- **Kiểm tra trước khi gửi** (chạy ở backend, hiện tại chỗ): vượt công suất định mức PCS, SOC ra ngoài giới hạn, vượt ngưỡng nhập dự kiến, sạc từ lưới trong giờ cao điểm (cảnh báo mềm), xung đột với sự kiện DR. Phân biệt **lỗi chặn** và **cảnh báo**.
- **So sánh phiên bản (diff):** kế hoạch đang chạy và bản nháp chồng lên nhau; bảng tóm tắt thay đổi (kWh dịch chuyển, chi phí dự kiến VND trước/sau, đỉnh dự kiến).
- **Nguồn gốc kế hoạch** ghi rõ: "Bộ tối ưu (rule-based / MPC / …)", "Thủ công bởi X", "Lịch dự phòng edge". Không ghi "AI" nếu thuật toán là luật cố định.
- **Giải thích:** mỗi khối từ bộ tối ưu có lý do ngắn (mã lý do: "sạc vì giá thấp điểm", "giữ SOC cho cắt đỉnh 17–20 h"). Agent 08 cần cung cấp `reason_code`.
- **Trạng thái đồng bộ với edge:** Nháp → Đã gửi → Edge đã nhận (phiên bản #) → Đang chạy. Nếu edge không xác nhận trong T giây thì hiện "Chưa đồng bộ" và edge **tiếp tục kế hoạch cũ**.
- Mobile: chỉ xem kế hoạch, không soạn (MVP).

### 3.12 Lệnh nguy hiểm: xác nhận và vòng đời

Bằng chứng: FusionSolar có Smart I-V bị kiểm soát quyền ở API (401 với guest) [FACT, demo_observations §5.4]. Huawei có fail-safe "communication disconnection detection default 3 s" (theo `functions_ui_roles.md`, https://support.huawei.com/enterprise/en/doc/EDOC1100173984/6d72858a/setting-parameters-over-the-app). Thông số đấu nối lưới và bảo vệ là chức năng của inverter/PCS đã chứng nhận; EMS chỉ đọc (C #13).

Phân loại lệnh [PROPOSAL]:

| Mức | Ví dụ | Xác nhận | Quyền |
|---|---|---|---|
| A — thường | Đổi khoảng xem, ack cảnh báo, lưu view | Không | Viewer+ |
| B — vận hành | Áp lịch mới, đổi chế độ chiến lược, đổi giới hạn EV | Hộp xác nhận có tóm tắt tác động | Operator |
| C — nguy hiểm | Đặt P BESS thủ công, đổi giới hạn nhập/xuất, đổi SOC_min, dừng/khởi động PCS, tắt điều khiển EMS (chuyển về chế độ hãng) | Hộp xác nhận + **gõ tên site** + xác thực lại (step-up/MFA) + thời hạn lệnh | Operator có quyền "control" theo site |
| D — cấm trên cloud | Ghi đè bảo vệ BMS/PCS, đóng/cắt máy cắt, đổi thông số grid code, reset khóa bảo vệ | Không có trên UI cloud | Chỉ tại chỗ |

Nội dung hộp xác nhận (mức B/C):
- Tiêu đề động từ rõ: "Đặt công suất BESS tại **Site Bình Dương 2**", không dùng "Bạn có chắc?".
- Bảng **Giá trị hiện tại → Giá trị mới** kèm đơn vị và hướng ("Xả 0 kW → Xả 200 kW").
- **Giới hạn sẽ áp:** "Edge sẽ giới hạn trong [−250; +250] kW và SOC 10–95%. Nếu BMS giới hạn thấp hơn, giá trị thấp hơn được dùng."
- **Tác động dự kiến:** P lưới dự kiến, có vượt ngưỡng nhập không.
- **Thời hạn:** lệnh thủ công luôn có hết hạn (mặc định 1 h, tối đa theo vai trò), sau đó trở về lịch. Hiện giờ hết hạn.
- Nút hành động mang động từ ("Gửi lệnh"); nút hủy là mặc định khi nhấn Enter với mức C.
- Với thao tác hàng loạt nhiều site: liệt kê site, tổng số, và yêu cầu gõ số lượng site.

Vòng đời lệnh (hiển thị trong toast và trang "Nhật ký lệnh"):

`Đã tạo → Đã gửi tới edge → Edge chấp nhận (hoặc Từ chối: lý do) → Thiết bị áp dụng (đọc lại khớp ± dung sai) → Hết hạn / Bị thay thế`

- **Không cập nhật UI lạc quan** (optimistic). Giá trị chỉ hiển thị "đã áp dụng" sau khi edge xác nhận và giá trị đọc lại khớp.
- Nếu edge mất kết nối: "Lệnh chưa tới site; edge đang chạy theo kế hoạch hiện có". Lệnh có TTL, quá hạn thì hủy, **không xếp hàng gửi muộn**.
- Mọi lệnh có audit: ai, lúc nào, từ IP/thiết bị nào, giá trị trước/sau, kết quả.

### 3.13 Dữ liệu cũ, offline, lịch dự phòng

Quan sát: FusionSolar có trạng thái "Đã ngắt kết nối"/"Ngoại tuyến" ở cấp nhà máy và thiết bị [ẢNH THẬT], nhưng **không thấy tuổi dữ liệu** trên số realtime (#8). Cloud-to-cloud thực tế chấp nhận trễ 15 phút–24 h (F #9, meteocontrol). Đề xuất của B: hiển thị "đang chạy lịch dự phòng" (PR-B02).

[PROPOSAL] Mô hình độ tươi dữ liệu (**khác** cờ `STALE` của F, vốn nghĩa là "giá trị đóng băng bất thường", xem §7):

| Mức | Điều kiện (mặc định, cấu hình theo nguồn) | Hiển thị số | Hiển thị khác |
|---|---|---|---|
| Live | tuổi ≤ 2 × chu kỳ mong đợi (vd ≤ 10 s với edge MQTT; ≤ 10 phút với cloud-to-cloud 5 phút) | Bình thường | Hoạt ảnh energy flow chạy |
| Trễ | ≤ 5 × chu kỳ | Bình thường + icon đồng hồ nhỏ + "trễ 45 s" | |
| Cũ | > 5 × chu kỳ | **Chữ xám nghiêng**, kèm "cập nhật 14:02 (18 phút trước)" | Hoạt ảnh dừng; cạnh nét đứt; KPI tổng ghi "gồm dữ liệu cũ" |
| Mất kết nối | heartbeat edge/gateway mất > T | Giá trị cuối + nhãn "Mất kết nối từ 13:40" | Tile site có hoa văn gạch chéo + icon; cảnh báo kết nối (một cảnh báo, chặn cảnh báo con) |
| Không có dữ liệu | chưa từng có | "—" (không bao giờ hiện 0) | Tooltip "chưa cấu hình điểm đo" |

- **Hai đồng hồ:** hiện thời điểm đo tại thiết bị (`ts_device`), không dùng thời điểm nhận ở cloud (F §3.6 có `ts_device`, `ts_edge_received`, `ts_ingested`). Lệch đồng hồ thiết bị > ngưỡng thì gắn cờ CLOCK_SUSPECT (F).
- **Trạng thái edge** ở header site: "Edge: trực tuyến / Mất kết nối cloud – đang chạy kế hoạch #123 tới 23:45 / Đang chạy lịch dự phòng / Chế độ an toàn hãng". Edge vẫn điều khiển khi cloud mất kết nối, nên UI phải nói rõ "**site vẫn đang được điều khiển cục bộ**" để operator không hoảng.
- Không bao giờ hiện **0** thay cho "không có dữ liệu" (0 kW và "không biết" khác nhau về vận hành).

### 3.14 Màu, trạng thái và khả năng tiếp cận

Quan sát [ẢNH THẬT]: trạng thái dùng chấm đỏ/xanh lá/xám (#4); cảnh báo có hình dạng riêng; nền trắng với banner xanh đậm; biểu đồ hai chuỗi màu gần nhau (#7).

[PROPOSAL] Hệ màu tách 3 họ, không dùng chung:

| Họ | Dùng cho | Quy tắc |
|---|---|---|
| Trung tính | Nền, chữ, thiết bị bình thường | Theo ISA-101 (#23): trạng thái bình thường **không cần màu nổi**; nền xám nhạt/trắng ngà; dark mode nền xám đậm, không đen tuyệt đối |
| Cảnh báo (4 mức) | Chỉ cảnh báo và bất thường | 4 màu phân biệt được với người mù màu đỏ–lục (vd đỏ thẫm / cam / vàng đậm / xanh dương) **luôn kèm icon hình dạng + chữ**. Không dùng màu cảnh báo cho mục đích trang trí |
| Loại năng lượng | PV, Lưới nhập, Lưới xuất, BESS sạc/xả, Tải, EV, Máy phát | Cố định toàn sản phẩm; không trùng sắc độ với họ cảnh báo; nhập/xuất dùng cùng sắc với độ đậm khác hoặc hoa văn khác |

- Trạng thái "Bình thường" dùng **icon dấu tích viền + chữ**, không dùng chấm xanh lá to.
- Mọi mã hóa trạng thái có ≥ 2 kênh (màu + hình dạng/chữ). Kiểm tương phản WCAG 2.x AA cho chữ (4.5:1) và đồ họa (3:1) (WCAG là chuẩn W3C; phiên bản áp dụng do agent 09 chốt).
- Nhấp nháy chỉ dành cho cảnh báo mức cao chưa ack, ≤ 3 lần/giây, và tắt được (`prefers-reduced-motion`).
- Biểu đồ: tối đa khoảng 6–8 màu phân biệt mỗi biểu đồ; chuỗi thứ 2 cùng đơn vị dùng nét đứt; nhãn trực tiếp ở cuối đường khi có thể.

### 3.15 Mật độ dữ liệu và di động

[PROPOSAL]
- **Hai mật độ:** Compact (NOC: dòng bảng 28–32 px, cỡ chữ 13 px, bảng nhiều cột) và Comfortable (owner: 40–48 px, thẻ). Lưu theo user.
- **Chữ số đều (tabular numerals)** cho cột số, căn phải, cùng số chữ số thập phân trong một cột.
- Header bảng không cắt chữ (FusionSolar cắt, #3/ảnh 08). Dùng tên ngắn + tooltip định nghĩa + đơn vị ở dòng phụ của header.
- **Di động (≥ 360 px, gutter 16 px):** ưu tiên (1) danh sách cảnh báo + ack, (2) trạng thái site và energy flow, (3) KPI hôm nay, (4) kế hoạch hôm nay (chỉ xem). Bảng chuyển thành thẻ. SLD và trend explorer ở mobile là chỉ xem, có cuộn/zoom. **Lệnh mức C không làm trên mobile ở MVP**, hoặc chỉ khi có step-up auth (quyết định thuộc agent 10).
- FusionSolar web khuyến nghị 1920×1080 (demo_observations §1). Ta thiết kế desktop chuẩn 1440 px, hỗ trợ 1280 px, màn lớn 1920+ (chế độ wall/NOC).
- Kiosk/wall display: chữ lớn, không có thao tác, tự làm mới, có watermark "dữ liệu lúc …", ẩn số tiền nếu chủ site không cho phép (SolarEdge có Kiosk/Public tách quyền, #13).

### 3.16 Đơn vị, số, ngày, tiền, song ngữ

Bài học [ẢNH THẬT]: #2 (lẫn công suất/điện năng), #3 (định dạng số, năm Phật lịch).

[PROPOSAL] Bảng quy tắc đơn vị:

| Đại lượng | Tên vi | Tên en | Đơn vị | Tự đổi cấp | Số thập phân hiển thị |
|---|---|---|---|---|---|
| Công suất tác dụng tức thời | Công suất | Power | kW | ≥ 1.000 kW → MW | < 10: 2; 10–999: 1; MW: 2 |
| Điện năng | Điện năng / Sản lượng | Energy | kWh | ≥ 10.000 kWh → MWh | kWh: 1 (< 100: 2); MWh: 2 |
| Dung lượng BESS định mức | Dung lượng | Energy capacity | kWh / MWh | như trên | 0–1 |
| Công suất BESS/PCS định mức | Công suất định mức | Power rating | kW / MW | như trên | 0 |
| Công suất PV DC | Công suất lắp đặt (DC) | DC capacity | kWp / MWp | như trên | 1–2 |
| Công suất phản kháng | Công suất phản kháng | Reactive power | kvar | | 1 |
| Công suất biểu kiến | Công suất biểu kiến | Apparent power | kVA | | 1 |
| Demand | Công suất cực đại (Pmax 30 phút) | Demand (30-min) | kW | | 1 |
| SOC, SOH, PR | | | % | | 0–1 |
| Năng suất riêng | | Specific yield | kWh/kWp | | 2 |
| Giá điện | Đơn giá | Tariff | đ/kWh | | 0 |
| Tiền | | | ₫ (VND) | ≥ 1 triệu → "triệu ₫", ≥ 1 tỷ → "tỷ ₫" trong thẻ KPI; bảng/báo cáo dùng số đầy đủ | 0 (VND không có số lẻ) |
| Nhiệt độ | | | °C | | 1 |
| Chênh áp cell | | | mV | | 0 |

- **Quy tắc vàng:** chữ "Công suất" **chỉ** đi với kW/MW/kVA/kvar; "Điện năng/Sản lượng/Dung lượng" **chỉ** đi với kWh/MWh. Lint i18n: kiểm tra tự động cặp nhãn–đơn vị.
- **Định dạng theo locale:** vi = `1.234,5 kW`, en = `1,234.5 kW`. Dùng `Intl` + ICU message format (ghi chú gốc nói Intl/ICU của Angular; frontend nay là React, dùng react-i18next theo [06 ADR-20](../06-system-architecture.html#adr-20)), **không ghép chuỗi tay**. Khoảng trắng không ngắt giữa số và đơn vị. **Không bao giờ hiện 3 chữ số thập phân** sau dấu phẩy với số < 10 (tránh `8,800` bị đọc thành 8800, xem #3).
- Đơn vị kWh luôn đi với **khoảng thời gian** ("kWh hôm nay", "kWh tháng 10").
- Ký hiệu SI: `kW` (k thường, W hoa), `kWh`, `MWh`, `kvar`; không viết `KW`, `Kwh`.
- **Ngày giờ:** vi hiển thị `dd/MM/yyyy HH:mm` (24 h), en hiển thị `yyyy-MM-dd HH:mm` hoặc theo locale; **luôn lịch Gregory** (chặn năm Phật lịch/âm lịch ở input, #3); xuất dữ liệu ISO 8601 có `+07:00`. Việt Nam không có DST, nhưng hệ thống vẫn lưu UTC.
- **Tiền:** VND, ký hiệu `₫` sau số ở vi (`1.250.000 ₫`); en `VND 1,250,000`. Tiền tệ cấu hình theo site/org (FusionSolar cấu hình tiền tệ theo nhà máy [FACT, demo ₱]).
- **Song ngữ:** thuật ngữ chuẩn giữ tiếng Anh trong ngoặc ở lần đầu/tooltip (SOC, SOH, PCS, peak shaving). Bảng thuật ngữ i18n do một người sở hữu. Nhãn mức cảnh báo, trạng thái thiết bị và tên chế độ là **enum có bản dịch**, không phải chuỗi tự do (bài học "Cao" và "Nặng", #5).
- **Ước tính và đo:** số ước tính (tiết kiệm, phân bổ dòng, CO₂) có dấu "≈" hoặc nhãn "ước tính" và link phương pháp.

### 3.17 Báo cáo "giá trị tạo ra"

Bằng chứng: GridBeyond ViewPoint Lens (#16), Stem Athena (B L47), FusionSolar có Doanh thu và Lợi ích môi trường [ẢNH THẬT].

[PROPOSAL] Trang "Giá trị" theo tháng: tiết kiệm theo chiến lược (cắt đỉnh: kW giảm × đơn giá công suất nếu có giá hai thành phần; dịch chuyển TOU: kWh × chênh giá; tự tiêu thụ PV), **so với kịch bản cơ sở có nêu rõ** ("nếu không có BESS"), độ tin cậy, và kWh thông lượng BESS đã dùng (chi phí suy giảm). CO₂ dùng hệ số phát thải lưới Việt Nam có nguồn và năm (agent C/F cung cấp).

---

## 4. Hệ quả thiết kế cho sản phẩm (PROPOSAL)

| ID | Đề xuất | Module | Ưu tiên | Cơ sở |
|---|---|---|---|---|
| H-P01 | Phân cấp màn hình L1–L4 (fleet → site → tài sản → chẩn đoán); trang L1 sắp "cần chú ý" theo điểm ưu tiên có lý do bằng chữ | M-DASH | P0 | #10, #23, §3.1 |
| H-P02 | Bộ chuyển site toàn cục (Ctrl+K), breadcrumb Org ▸ Site ▸ Tài sản, deep-link URL; cây trái là tùy chọn | M-ORG, M-DASH | P0 | §3.2 |
| H-P03 | Header site luôn hiện: chế độ vận hành, nguồn lệnh, trạng thái edge, tuổi dữ liệu, dải TOU hiện tại | M-DASH, M-OPT | P0 | #18, §3.3, §3.13 |
| H-P04 | Biểu đồ "Hôm nay: thực tế và kế hoạch" có dải TOU, ngưỡng nhập, SOC, vùng tương lai nét đứt | M-DASH, M-OPT | P0 | §3.3 |
| H-P05 | Energy flow: cạnh có hướng không âm, mũi tên tĩnh + chữ Nhập/Xuất/Sạc/Xả, phân bổ cạnh tính ở backend, huy hiệu lệch cân bằng, dừng hoạt ảnh khi dữ liệu cũ, reduced-motion | M-MON | P0 | #1, #19, #20, #22 |
| H-P06 | SLD sinh từ mô hình tài sản, đánh dấu vị trí công tơ, trạng thái máy cắt bằng ký hiệu + chữ; chỉ đọc trên cloud | M-MON, M-GRID | P1 | #26, C §3.3 |
| H-P07 | Trang BESS: P thực tế / setpoint / **P cho phép** và nguồn giới hạn; SOC % + kWh khả dụng; ranh giới RTE; heatmap cell (L4) | M-BESS | P0 (heatmap P1) | #22, C K16 |
| H-P08 | Trang POC: đồng hồ demand theo chu kỳ biểu giá (mặc định 30 phút) có dự báo cuối chu kỳ | M-GRID, M-TAR | P0 | #21 |
| H-P09 | Trend explorer: ≤ 2 đơn vị/panel, panel xếp chồng đồng bộ, overlay TOU + sự kiện, khoảng trống không nối, cờ chất lượng, legend không phân trang, lưu/chia sẻ view | M-HIST | P0 | #6, #7 |
| H-P10 | Console cảnh báo theo vòng đời kiểu ISA-18.2 (ack, shelve có lý do + thời hạn, suppressed-by-design theo quan hệ cha–con, out-of-service); cấm shelve cảnh báo an toàn; gom lũ cảnh báo và gộp thông báo | M-ALM | P0 (flood P1) | #11, #13, #24, #25 |
| H-P11 | Trình soạn lịch 48 h, ô 15 phút, swimlane TOU/dự báo/BESS/SOC/lưới/EV/chế độ; cửa sổ đóng băng; kiểm tra chặn/cảnh báo; diff phiên bản; nguồn gốc + mã lý do; trạng thái đồng bộ edge | M-OPT | P0 (xem), P1 (soạn kéo thả) | #18, #21 |
| H-P12 | Phân loại lệnh A/B/C/D; hộp xác nhận hiện hiện tại → mới, giới hạn sẽ áp, tác động, thời hạn; mức C gõ tên site + step-up; mức D không có trên cloud | M-BESS, M-SEC | P0 | C #13, §3.12 |
| H-P13 | Vòng đời lệnh hiển thị được, không optimistic UI, TTL, không gửi muộn, nhật ký lệnh | M-BESS, M-SEC | P0 | §3.12 |
| H-P14 | Mô hình độ tươi Live/Trễ/Cũ/Mất kết nối/Không có dữ liệu; không bao giờ hiện 0 thay "không biết"; thời điểm đo theo `ts_device` | M-MON | P0 | #8, F §3.6 |
| H-P15 | Ba họ màu tách biệt (trung tính / cảnh báo 4 mức / loại năng lượng); ≥ 2 kênh mã hóa; nền trung tính kiểu ISA-101; WCAG AA | Toàn bộ | P0 | #4, #23 |
| H-P16 | Bảng quy tắc đơn vị + lint i18n cặp nhãn–đơn vị; Intl format; lịch Gregory; VND 0 số lẻ | Toàn bộ | P0 | #2, #3 |
| H-P17 | Enum i18n cho mức cảnh báo/trạng thái/chế độ; bảng thuật ngữ vi/en | Toàn bộ | P0 | #5 |
| H-P18 | Hai mật độ Compact/Comfortable; chế độ wall/NOC; kiosk tách quyền | M-DASH, M-SEC | P1 | #12, #13 |
| H-P19 | Mobile: cảnh báo + ack, trạng thái, energy flow, kế hoạch chỉ xem; không lệnh mức C ở MVP | M-ALM, M-DASH | P1 | §3.15 |
| H-P20 | Trang "Giá trị tạo ra" so với kịch bản cơ sở, ghi nhãn ước tính | M-REP | P1 | #16 |
| H-P21 | HMI cục bộ tối giản trên edge (chỉ trạng thái, energy flow, cảnh báo, chế độ hiện tại) để dùng khi mất Internet | M-MON (edge) | P2 | #17 |
| H-P22 | Mọi số ước tính/phân bổ có nhãn "≈ ước tính" + link phương pháp; không ghi "AI" cho luật cố định | Toàn bộ | P0 | Quy ước dự án |

**Khác biệt so với wireframe FusionSolar cũ (và lý do):**
- Wireframe cũ mô phỏng IA của FusionSolar (cây trái, trang chủ List/KPI, lợi ích môi trường ở trung tâm). Đề xuất mới chuyển trọng tâm sang **chế độ vận hành, kế hoạch so với thực tế, giới hạn và lệnh**. EMS có điều khiển, nên câu hỏi chính của operator là "site có đang làm đúng kế hoạch và an toàn không", không chỉ "sản lượng bao nhiêu".
- Wireframe cũ dùng "Mức báo động S1 Nghiêm trọng → S4 Cảnh báo". Ta giữ 4 mức nhưng đổi nhãn tránh "Cảnh báo" vừa là tên chung vừa là tên một mức.
- Quy ước dấu đổi theo agent C (lưới + = nhập). UI không hiện số có dấu nên người dùng không thấy khác biệt; chỉ API/export bị ảnh hưởng.

---

## 5. Evidence ledger

| # | Claim | Source URL | Source type & date | Excerpt/paraphrase | Confidence | Conflicting evidence | Design implication |
|---|---|---|---|---|---|---|---|
| 1 | Energy flow FusionSolar 4 nút, số kW cân bằng, không có chữ nhập/xuất | `docs/research/fusionsolar/03_anh_demo/01_plant_overview.jpg` | Ảnh chụp demo thật, 07/10/2026 | PV 1,746; Lưới 4,309; Lưu trữ 0,000 (5%); Tải 6,055 kW; nhãn "Hòa lưới" | High | — | H-P05 chữ hướng + mũi tên tĩnh |
| 2 | Nhãn "Công suất" đi với kWh | `01_plant_overview.jpg`; `08_home_list_view.jpg` | Ảnh thật, 07/10/2026 | "Công suất tự dùng 30,86 kWh"; "Công suất ESS định mức 144,00 kWh" | High | — | H-P16 lint nhãn–đơn vị |
| 3 | Định dạng số/ngày không nhất quán; năm Phật lịch lọt vào | `08_home_list_view.jpg`; `03_logical_layout_module_level.jpg`; `fusionsolar/.../demo_observations.md` §3 | Ảnh thật + ghi chú quan sát, 07/10/2026 | `8,800` kWp; `9.216,58`; `1.67`; `2565-01-29` | High | — | H-P16 Intl format, lịch Gregory |
| 4 | Trạng thái site/thiết bị chỉ bằng chấm màu; mức báo động có icon hình dạng | `08_home_list_view.jpg`; `04_plant_device_list.jpg` | Ảnh thật, 07/10/2026 | Chấm xanh/đỏ/xám; icon bát giác/tia sét/!/i | High | — | H-P15 ≥ 2 kênh |
| 5 | Nhãn mức 2 khác nhau: "Cao" và "Nặng" | `09_home_kpi_view.jpg`; `01_plant_overview.jpg` | Ảnh thật, 07/10/2026 | như claim | High | — | H-P17 enum i18n |
| 6 | Biểu đồ trục kép kW/% SOC, legend phân trang, dataZoom, thanh phân rã PV/tiêu thụ | `02_energy_revenue_charts.jpg` | Ảnh thật, 07/10/2026 | "1/2" legend; "100,00% / 0,00%"; "88,91% / 11,09%" | High | — | H-P09 |
| 7 | Lịch sử thiết bị: 1 ngày + nhiều điểm tín hiệu, màu chuỗi gần nhau | `06_device_history.jpg`; `demo_observations.md` §5.5 | Ảnh thật, 07/10/2026 | "Ngày: 2026-10-07 · Điểm tín hiệu: Đã chọn 2" | High | — | H-P09 so sánh nhiều khoảng |
| 8 | Chi tiết thiết bị không có dấu thời gian cập nhật; có trường giới hạn công suất P=11.5% | `05_inverter_realtime_detail.jpg`; `07_smartassistant_emma_detail.jpg`; `demo_observations.md` §5.4 | Ảnh thật, 07/10/2026 | Lưới key–value 3 cột | Med (có thể nằm ngoài vùng chụp) | — | H-P14 |
| 9 | Polling running-status ~5 s; list view v7.0 làm mới 3 phút | `demo_observations.md` §5.1; https://solisdepot.com/wp-content/uploads/2023/03/FusionSolar-Smart-PV-Management-System-7.0-After-sales-Technical-Training-Slides.pptx.pdf | Quan sát network 07/10/2026; slide đào tạo hãng (theo ghi chú FS) | "refreshes every 3 min" | Med–High | — | Ngưỡng Live/Trễ theo chu kỳ nguồn |
| 10 | IA: cây tổ chức trái, tab nhà máy, menu theo vai trò, cấu hình view theo user | `01_plant_overview.jpg`; `demo_observations.md` §2–5 | Ảnh thật + network | `viewcfg?userName=…` | High | — | H-P02 |
| 11 | Alarm → ticket "New Ticket" có người xử lý và gợi ý | https://solisdepot.com/wp-content/uploads/2023/03/FusionSolar-Smart-PV-Management-System-7.0-After-sales-Technical-Training-Slides.pptx.pdf | Slide đào tạo hãng v7.0 (theo `functions_ui_roles.md`) | "Click the New Ticket button" | Med (UI cũ) | Thao tác 25.x chưa rõ | H-P10 nút tạo ticket |
| 12 | Kiosk công khai: energy flow, sản lượng, doanh thu, CO₂; dashboard màn lớn ≥ 1920×1080 | như #11 | Slide hãng v7.0 | như claim | Med | — | H-P18 |
| 13 | SolarEdge ONE C&I: Kiosk, Public, API Access, cảnh báo theo user | https://knowledge-center.solaredge.com/sites/kc/files/se-site-admin-in-solaredge-one-for-c&i-user-guide.pdf | User guide hãng (qua kết quả tìm kiếm, theo B L32) | "Expose to alerts notifications" | Med–High | Có thể khác bản mới | H-P10 định tuyến; H-P18 |
| 14 | SolarEdge ONE C&I: fleet tới module, digital twin, live alerts, PV+BESS+EV | https://www.solaredge.com/us/solaredge-one-for-commercial-and-industrial-energy-optimization-platform | Trang marketing hãng (qua kết quả tìm kiếm, theo B L30) | "utility rates and weather forecasts" | Med | Không phải ảnh UI | Phạm vi trang tài sản |
| 15 | OpenEMS: Edge/Backend/UI; lưới + mua, ESS + xả | https://openems.github.io/openems.io/openems/latest/edge/architecture.html ; https://openems.github.io/openems.io/openems/latest/edge/configuration.html | Docs chính thức (qua kết quả tìm kiếm, theo B/C) | "Negative values for Charge; positive for Discharge" | Med–High | Huawei: + = xuất | H-P05 nhãn hướng |
| 16 | Quy ước dấu không có chuẩn chung | https://community.openenergymonitor.org/t/is-there-a-standard-for-import-export-positive-negative-power-flow/15149 | Diễn đàn (qua kết quả tìm kiếm, theo C #2) | như claim | Med | — | Không hiện số có dấu trên UI |
| 17 | Thẻ Tesla-style: 7 cạnh có hướng không âm, tốc độ tỉ lệ công suất, ẩn cạnh không hoạt động | https://github.com/reptilex/tesla-style-solar-power-card/blob/master/README.md ; https://github.com/reptilex/tesla-style-solar-power-card/blob/master/src/models/SensorElement.ts#L78-L90 | Mã nguồn mở Apache-2.0, 2024 (đọc trong nghiên cứu FS trước) | "all sensors need to be positive values" | High | Thẻ cộng đồng, không phải Tesla | H-P05 |
| 18 | GridBeyond ViewPoint Lens: hồ sơ tải, phản ứng DR, doanh thu | https://secure.businesswire.com/news/home/20250930978130/en/GridBeyond-Launches-ViewPoint-Lens-to-Empower-Energy-Customers-With-Greater-Visibility-and-Control | Thông cáo báo chí 9/2025 (qua kết quả tìm kiếm, theo B L49) | như claim | Med | — | H-P20 |
| 19 | Stem PowerTrack EMS có edge UI tách khỏi phần mềm danh mục | https://www.businesswire.com/news/home/20250902991311/en | Thông cáo báo chí 9/2025 (qua kết quả tìm kiếm, theo B L46) | "edge UI" | Med | — | H-P21 |
| 20 | Schneider EMA: lịch 15 phút/72 h, dự phòng 48 h | https://download.schneider-electric.com/doc/998-20080341_US/EcoStruxure%20Microgrid%20Advisor%20Handout.pdf | Handout hãng (~2017) (qua kết quả tìm kiếm, theo A #21) | như claim | Med | 48 h và 72 h giữa các tài liệu | H-P03, H-P11 |
| 21 | Pmax Việt Nam tính theo chu kỳ 30 phút | https://daibieunhandan.vn/trien-khai-thu-nghiem-gia-ban-le-dien-hai-thanh-phan-tu-thang-10-2025-10390577.html | Báo, 2025 (qua kết quả tìm kiếm, theo C #3) | "khoảng thời gian tích phân hiện nay đang là 30 phút" | Med–High | Berlin dùng 15 phút | H-P08 chu kỳ là tham số |
| 22 | Khung giờ cao điểm tối thay đổi 2026 | https://tuoitre.vn/bo-cong-thuong-chinh-thuc-thay-doi-khung-gio-tinh-gia-dien-buoi-toi-la-gio-cao-diem-2026042410430101.htm | Báo, 4/2026 (URL trong ghi chú A; tôi chưa đọc) | tiêu đề bài | Low–Med | — | Dải TOU theo dữ liệu có hiệu lực, không vẽ cứng |
| 23 | Aux BESS làm p_bess âm nhẹ khi đứng yên; không phải đang sạc | https://www.sandia.gov/ess-ssl/wp-content/uploads/2019/07/PNNL-MESA-1-Final-Test-Report_Reduced.pdf ; `C-energy-domain.md` §3.5 | Báo cáo thử nghiệm PNNL (qua kết quả tìm kiếm, theo C) + suy luận C | aux ~30 kW / 1.000 kWh | Med | — | Trạng thái sạc/xả lấy từ PCS/BMS |
| 24 | Fail-safe mất liên lạc mặc định 3 s ở inverter Huawei | https://support.huawei.com/enterprise/en/doc/EDOC1100173984/6d72858a/setting-parameters-over-the-app | Manual hãng (theo `functions_ui_roles.md`) | "communication disconnection detection default 3 s" | Med | — | Bảo vệ ở thiết bị; UI hiện trạng thái fail-safe, không thay thế |
| 25 | Smart I-V bị kiểm soát quyền ở API (401 với guest) | `demo_observations.md` §5.4 | Quan sát network, 07/10/2026 | `ivcurve/.../originaloptions` → 401 | High | — | Chức năng chẩn đoán/điều khiển cần quyền phía server, không chỉ ẩn nút |
| 26 | Cờ chất lượng: nguồn gốc + bitmask, có STALE nghĩa "giá trị đóng băng"; ba đồng hồ ts | `F-data-analytics.md` §3.6–3.7 | Ghi chú agent F, 2026-10-10 | MEASURED/ESTIMATED…; STALE | Med | Nghĩa STALE khác "dữ liệu cũ" của UI | H-P14 tách khái niệm |
| 27 | ISA-101: nền trung tính, màu cho bất thường, phân cấp L1–L4 | — (chưa kiểm chứng trong phiên) | Hiểu biết ngành | — | Low (chưa có nguồn) | — | H-P01, H-P15; cần kiểm chứng edition |
| 28 | ISA-18.2/IEC 62682: shelved, suppressed by design, out of service, rationalization | — (chưa kiểm chứng trong phiên) | Hiểu biết ngành | — | Low (chưa có nguồn) | — | H-P10; không tuyên bố tuân thủ |
| 29 | EEMUA 191: ngưỡng tải cảnh báo/flood | — | Hiểu biết ngành | ≈ 1/10 phút; flood > 10/10 phút | Low | — | Ngưỡng flood cấu hình được, không hard-code |
| 30 | Màu máy cắt đỏ/xanh ngược nhau theo vùng | — | Hiểu biết ngành | — | Low | — | H-P06 ký hiệu + chữ |
| 31 | Huawei Owner manual 25.2.0 có mục "Battery Control Parameters" | https://support.huawei.cn/enterprise/en/doc/EDOC1100488067/118cf11f/battery-control-parameters | Tiêu đề kết quả tìm kiếm (theo `functions_ui_roles.md`) | tiêu đề mục | Med (chỉ tiêu đề) | — | Chủ site cũng có tham số pin → phân quyền theo vai trò |

---

## 6. Câu hỏi mở / UNKNOWN

| ID | Câu hỏi | Ảnh hưởng | Cách đóng |
|---|---|---|---|
| Q-H01 | Giao diện thực của Victron VRM, Tesla Powerhub, Enphase Enlighten, Sungrow iSolarCloud, OpenEMS UI, Schneider EMA (energy flow, alarm, schedule editor) | Benchmark pattern | Lượt tìm kiếm mới hoặc demo/tài khoản thử; OpenEMS UI có thể chạy local từ repo (cần quyết định riêng) |
| Q-H02 | Edition và điều khoản chính xác của ISA-101, ISA-18.2, IEC 62682, EEMUA 191 | Có tuyên bố "theo tinh thần" hay "tuân thủ" | Tìm kiếm nguồn ISA/IEC/EEMUA; mua tiêu chuẩn nếu cần |
| Q-H03 | Thao tác cảnh báo thật trong FusionSolar 25.x (ack/clear/mask/export) | So sánh đối thủ | Tài khoản installer |
| Q-H04 | Persona thật ở Việt Nam: NOC của installer có bao nhiêu site/người? dùng Zalo hay e-mail để nhận cảnh báo? | Định tuyến thông báo, mật độ | Phỏng vấn 5–8 đơn vị O&M |
| Q-H05 | Tập quán màu/ký hiệu SLD và SCADA ở EVN/điện lực Việt Nam | Quy ước SLD | Hỏi kỹ sư điện lực, tài liệu EVN |
| Q-H06 | Có cần cho phép lệnh mức C trên mobile không (kỹ sư tại site)? | Bảo mật/UX | Agent 10 + phỏng vấn |
| Q-H07 | Ngưỡng Live/Trễ/Cũ theo từng loại nguồn (edge MQTT, Modbus, cloud-to-cloud) | Hiển thị độ tươi | Agent E/F cung cấp chu kỳ thực tế |
| Q-H08 | Ô lập lịch 15 phút hay 30 phút làm mặc định khi demand Việt Nam tính 30 phút? | Trình soạn lịch | Agent 08 |
| Q-H09 | Hệ số phát thải lưới Việt Nam dùng cho CO₂ (năm, nguồn) | Báo cáo giá trị | Agent C/F |
| Q-H10 | Thuật ngữ tiếng Việt chuẩn cho "demand", "shelve", "acknowledge" mà khách hàng Việt Nam quen dùng | i18n | Phỏng vấn, tài liệu EVN |

---

## 7. Vấn đề gửi agent khác

| ID | Gửi | Vấn đề | Đề nghị |
|---|---|---|---|
| X-H01 | Agent F (dữ liệu), người viết 05/09 | Cờ `STALE` của F nghĩa là "giá trị đóng băng bất thường", nhưng trong UI "stale" thường hiểu là "dữ liệu cũ, không cập nhật". Hai khái niệm dễ lẫn. | Đổi tên cờ của F thành `FROZEN` (hoặc giữ nhưng định nghĩa rõ). UI dùng khái niệm riêng "độ tươi" (`freshness`: LIVE/DELAYED/OLD/OFFLINE/NO_DATA) tính từ `ts_device` và chu kỳ mong đợi. |
| X-H02 | Agent C, người viết 05/07 | UI theo X-C01 (nhãn hướng). Cần backend cung cấp **cạnh dòng năng lượng đã phân bổ** (không âm) và **trạng thái sạc/xả/chờ từ PCS/BMS**, không suy từ dấu P. | Thêm vào domain model: `energy_flow_edges` theo lát thời gian; `bess_operating_state` enum. |
| X-H03 | Agent 08 (tối ưu) | Trình soạn lịch cần `plan_version`, `source` (optimizer/manual/fallback), `algorithm_type` (rule/MPC…), `reason_code` cho mỗi khối, SOC dự kiến, P lưới dự kiến, chi phí dự kiến VND. | Đưa các trường này vào hợp đồng API kế hoạch. Không gắn nhãn "AI" cho luật cố định. |
| X-H04 | Agent E (tích hợp) | Vòng đời lệnh cần edge trả: ack/nack kèm lý do, giá trị **đọc lại** sau khi ghi, giới hạn hiện tại (CCL/DCL, rating), nguồn giới hạn (BMS/PCS/EMS/lưới). Cần `ts_device` cho từng điểm. | Đặc tả trong 07; ghi rõ thiết bị nào không đọc lại được setpoint. |
| X-H05 | Agent 10 (bảo mật & an toàn) | Phân loại lệnh A/B/C/D (§3.12); danh sách cảnh báo an toàn **không được shelve**; step-up auth cho mức C; quyết định lệnh trên mobile; quy tắc hai người cho thao tác hàng loạt nhiều site (P2?). | Chốt danh sách và đưa vào NFR-SEC. |
| X-H06 | Agent B / người tổng hợp | B ghi Victron VRM/Enphase "chưa tìm hiểu" (Q-B12). Tôi cũng không thu được bằng chứng UI do hết hạn mức tìm kiếm. | Ma trận đối thủ không gán tính năng UI cho các hãng này; cần lượt tìm kiếm bổ sung (Q-H01). |
| X-H07 | Người viết 09 (UX spec) | Wireframe FusionSolar cũ dùng nhãn mức "S4 Cảnh báo", trùng với tên chung "cảnh báo". | Dùng bộ nhãn mới (Khẩn cấp/Cao/Trung bình/Thông tin) hoặc chốt bộ khác, nhưng một nguồn duy nhất. Mã trang UI-NN do người viết 09 cấp; H-P01…H-P22 ở đây là mã đề xuất tạm. |
| X-H08 | Người tổng hợp / orchestrator | Hạn mức WebSearch đã hết trước khi agent H tìm được nguồn nào. Mọi FACT về hãng khác trong ghi chú này là tái sử dụng từ ghi chú B/C/FS. Các claim tiêu chuẩn (ISA/IEC/EEMUA) ở mức Low. | Lên lịch một lượt tìm kiếm bổ sung riêng cho Q-H01, Q-H02 trước khi xuất bản 09. |
