# G — Tối ưu năng lượng: chiến lược, tầng điều khiển, lập kế hoạch điều độ

[← Mục lục](../index.html) · [08 Tối ưu](../08-energy-optimization.md) · [04 Yêu cầu](../04-business-requirements.md) · [06 Kiến trúc](../06-system-architecture.html) · [07 Tích hợp](../07-device-integration.md) · [13 Rủi ro](../13-open-questions-and-risks.md) · [14 Nguồn](../14-source-register.md)

- Tác giả: Agent G (Energy Optimization Specialist). Ngày: 2026-10-10. Trạng thái: bản nghiên cứu v1.
- **Giới hạn phương pháp (quan trọng).** Môi trường chặn tải trang trực tiếp. Hạn mức WebSearch của lượt chạy này **đã hết** trước khi Agent G bắt đầu (công cụ trả về "web search budget is used up"). Vì vậy:
  - Mọi `[FACT]` trong file này lấy lại từ bằng chứng **đã được các agent khác hoặc nghiên cứu FusionSolar ghi kèm URL**: `notes/A-market-boundary.md`, `notes/B-competitors.md`, `notes/C-energy-domain.md`, `notes/E-device-integration.md`, `fusionsolar/04_ghi_chu_nghien_cuu/`. Nguồn gốc của mỗi FACT được ghi ở cột "Source type" trong ledger. Phần lớn là "(qua kết quả tìm kiếm)".
  - Các tên controller OpenEMS mà đề bài nêu (`ess.limittotaldischarge`, `ess.emergencycapacityreserve`…), các chế độ ESS của Victron, license của solver: **chưa kiểm chứng được trong phiên này**. Ghi `[UNKNOWN]` hoặc `[INFERENCE]` (kiến thức nền), kèm việc cần kiểm chứng ở §6.
  - Không có số liệu tiết kiệm độc lập mới. Chỉ có tuyên bố của vendor (độ tin thấp).
- Quy ước dấu theo C-energy-domain §3.2: **lưới + = nhập (mua)**, **BESS + = xả**, PV ≥ 0, tải ≥ 0. `P_load = P_grid + P_pv + P_bess`.

---

## 1. Phạm vi & câu hỏi nghiên cứu

**Phạm vi.** Phần "não" điều độ của EMS cho site C&I đa site: PV + BESS + lưới + phụ tải + (tùy chọn) sạc EV. Gồm chiến lược, cách xếp chồng ưu tiên, bốn tầng điều khiển, công thức tối ưu, vòng đời kế hoạch điều độ, giải thích quyết định, mô phỏng/backtest, và giá trị thực tế ở Việt Nam. Không gồm: bảo vệ thiết bị (thuộc BMS/PCS/relay), driver giao thức (Agent E), dự báo chi tiết (chỉ nêu giao diện đầu vào).

| ID | Câu hỏi | Trả lời ở |
|---|---|---|
| RQ-G1 | Các chiến lược (peak shaving, TOU arbitrage, self-consumption, zero-export, demand limit, DR, backup reserve, EV DLM, thị trường) cần input gì, chạy ở đâu, tạo giá trị gì? | §3.1 |
| RQ-G2 | Bốn tầng điều khiển (rule-based, lịch theo dự báo, tối ưu toán học, theo thị trường) khác nhau thế nào về input/output/độ trễ/vị trí/fallback/giải thích? | §3.2 |
| RQ-G3 | Thuật toán tầng 1 tại edge cụ thể ra sao (PI, hysteresis, cửa sổ demand)? | §3.3 |
| RQ-G4 | Công thức MILP cụ thể cho site PV+BESS+lưới+tải+EV? Kích thước, solver nào phù hợp team Java? | §3.5, §3.6 |
| RQ-G5 | Xếp chồng ưu tiên và giải xung đột giữa các chiến lược? | §3.8 |
| RQ-G6 | Vòng đời kế hoạch điều độ, thực thi, ack, actual vs planned, audit, giải thích? | §3.9–§3.11 |
| RQ-G7 | Mô phỏng what-if và backtest trên dữ liệu lịch sử? | §3.12 |
| RQ-G8 | Vendor thực sự ship những chế độ/thuật toán nào? Bằng chứng tiết kiệm? | §3.13, §3.14 |
| RQ-G9 | Ở Việt Nam (TOU QĐ 963, giá QĐ 1279, thí điểm hai thành phần, NĐ 58/243), chiến lược nào tạo tiền **hôm nay**? | §3.15 |

---

## 2. Phát hiện chính

1. **[FACT] Kiến trúc thống trị là "cloud lập kế hoạch + edge thực thi".** Schneider EcoStruxure Microgrid Advisor chạy MPC (Model Predictive Control, điều khiển dự báo theo mô hình) trên cloud từ giá, lịch sử, thời tiết, lịch vận hành. Lịch 15 phút trên horizon 72 h. Có lịch mặc định 48 h để edge chạy tiếp khi mất kết nối (một tài liệu khác ghi 72 h) — https://www.se.com/us/en/product-range/65896/ ; https://download.schneider-electric.com/doc/998-20080341_US/EcoStruxure%20Microgrid%20Advisor%20Handout.pdf (qua kết quả tìm kiếm; trích từ A #21, B L14). [INFERENCE] Đây là mẫu tham chiếu trực tiếp cho tầng 2–3 của ta.
2. **[FACT] Vòng điều khiển nhanh nằm ở site.** Huawei SmartLogger5000B công bố zero feed-in khép kín ≤ 2 s, peak shaving/giới hạn công suất ≤ 5 s — https://www.photomate.eu/smartlogger5000b ; https://solar.huawei.com/admin/asset/v1/pro/view/bb9458d9373d4502912378db3cbc7f2d.pdf (qua kết quả tìm kiếm; E F-28). Cloud API của Huawei gộp dữ liệu 5 phút (nghiên cứu FusionSolar). [INFERENCE] Tầng 1 (zero-export, import cap, demand window) **bắt buộc** ở edge hoặc controller native; cloud không bao giờ nằm trong vòng kín.
3. **[FACT] Ampowr Cosmos ship peak shaving theo trần lưới, generator steering, curtailment, self-consumption, và chạy tiếp chiến lược tại chỗ khi mất mạng ("local backup feature").** Case Hoge Duin: trần 95 kW — https://ampowr.com/hoge-duin-hotel-enhances-energy-efficiency-with-ampifarm-peak-shaving/ ; https://ampowr.com/energy-management-system-ems/peak-shaving/ (qua kết quả tìm kiếm; B L04, L06). Thị trường: bid đồng thời Day-Ahead + imbalance + aFRR ở Hà Lan — https://ampowr.com/case-study-gebroeders-van-pinxteren/ (B L03).
4. **[FACT] Huawei có ba chế độ ESS trong app: "Maximum self-consumption", "Fully fed to grid", "TOU"** (khung sạc/xả thủ công, cho phép sạc từ lưới trong khung sạc) — https://e-solarshop.ro/wp-content/uploads/2025/07/fusionsolar-app-manual5925.pdf (nghiên cứu FusionSolar). Northbound `ch_discharge_model`: 0 none, 1 forced, 2 TOU price, 3 fixed, 4 automatic — https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/imaster-neteco-v600r022c00-northbound-interface-reference-v6.pdf. Thư viện cộng đồng `huawei_solar` có các dịch vụ ghi `set_tou_periods`, `set_capacity_control_periods` (peak shaving theo khung), `set_maximum_feed_grid_power`, `set_zero_power_grid_connection`, `forcible_charge/discharge` — https://github.com/wlcrs/huawei_solar/blob/main/services.yaml. [INFERENCE] Driver Huawei nên ánh xạ chiến lược của ta xuống **chế độ native** thay vì ghi setpoint P từng giây.
5. **[FACT] Huawei EMMA/SmartAssistant dự báo dư PV và giữ "SOC space reserve"** (chừa dung lượng trống để hấp thụ PV dư) — https://solar.huawei.com/en/products/EMMA (B L38). Panel EMMA có so sánh có/không EMMA, dự báo 24 h, phân tích tiết kiệm theo giá; **tắt EMMA thì không bật lại được trong cùng tháng** — https://support.huawei.com/enterprise/en/doc/EDOC1100376808/a3411c60/enabling-emma (nghiên cứu FusionSolar). Release note 31/03/2026: SmartEMO C&I hỗ trợ demand charge theo khung TOU (đọc trực tiếp ở demo trước).
6. **[FACT] OpenEMS có controller `Controller.Ess.PeakShaving` (cắt đỉnh tại PCC) và `Controller.Ess.Balancing` (cân bằng PCC về `targetGridSetpoint`, mặc định 0 W); có ToU optimizer theo slot 15 phút (Tibber, 2025.11.0); có GridOptimizedCharge (2026.4.0); có module OCPP server.** Mọi điều khiển ESS phải đi qua "Power Solver", không ghi thẳng kênh Modbus — https://openems.github.io/openems.io/openems/latest/edge/architecture.html ; https://github.com/OpenEMS/openems/tree/develop/io.openems.edge.controller.ess.balancing ; https://zenodo.org/records/17481747 ; https://zenodo.org/records/19374309 ; https://community.openems.io/t/ess-that-can-talk-with-openems-using-modbus-tcp/1029 (B L43, L44). [UNKNOWN] Tên `ess.limittotaldischarge`, `ess.emergencycapacityreserve`, `ess.timeofusetariff` chưa kiểm chứng trong phiên này (xem Q-G01).
7. **[FACT] Victron GX: ESS "Mode 2" nhận setpoint công suất lưới (`/AcPowerSetpoint`, thanh ghi 2700, int16); "Mode 3" giao toàn bộ vòng điều khiển ra ngoài.** Hành vi fallback khi master Modbus mất kết nối chưa được trả lời — https://communityarchive.victronenergy.com/questions/95889/multipluss-ii-is-external-control-ess-mode-2-or-3%EF%B9%96childToView=102991.html (cộng đồng, Low–Med; E F-30). [INFERENCE] Kiểu "setpoint lưới" (grid setpoint) an toàn hơn kiểu "setpoint pin" khi dự báo sai, vì thiết bị tự bù sai số tải trong vòng nhanh của nó.
8. **[FACT] Việt Nam: cao điểm mới 17h30–22h30 T2–T7 (5 h), thấp điểm 0h–6h, Chủ nhật không có cao điểm (QĐ 963/QĐ-BCT, 22/04/2026).** Ngày áp vào hóa đơn còn chưa chắc — https://thuvienphapluat.vn/van-ban/Tai-nguyen-Moi-truong/Quyet-dinh-963-QD-BCT-2026-khung-gio-cao-diem-thap-diem-cua-he-thong-dien-quoc-gia-703327.aspx ; https://tuoitre.vn/bo-cong-thuong-chinh-thuc-thay-doi-khung-gio-tinh-gia-dien-buoi-toi-la-gio-cao-diem-2026042410430101.htm (A #4). Giá sản xuất 22–<110 kV: thấp điểm 1.190, bình thường 1.833, cao điểm 3.398 đ/kWh; tỷ lệ cao/thấp ≈ 2,8–2,86× (QĐ 1279/QĐ-BCT; A §3.4.3).
9. **[INFERENCE] Ở Việt Nam, cao điểm buổi tối làm PV không còn tự "ăn" giờ cao điểm; giá trị chuyển sang BESS.** Thứ tự giá trị của 1 kWh nạp vào pin (RTE 90%, cấp 22–110 kV, chưa trừ suy hao): PV dư lẽ ra bị cắt → lãi **≈3.058 đ**; lưới thấp điểm → **≈1.868 đ** (≈2.076 đ/kWh xả); PV lẽ ra bù tải giờ bình thường hoặc lưới giờ bình thường → **≈1.225 đ** (≈1.361 đ/kWh xả) (§3.15.2). Chủ nhật chỉ còn chênh lệch bình thường/thấp điểm ≈ 511 đ/kWh xả, nhiều khả năng không bù được chi phí suy hao.
10. **[FACT] Việt Nam chưa có demand charge kiểu Mỹ/EU cho C&I đại trà; giá hai thành phần đang thí điểm cho khách sản xuất ≥ 200.000 kWh/tháng** (dự thảo: hóa đơn song song 01–06/2026, thanh toán thật 07/2026–07/2027, mở rộng từ 08/2027) — https://tapchicongthuong.vn/thi-diem-ap-dung-gia-dien-hai-thanh-phan-tu-1-1-2026-218800.htm (A #6). Pmax = công suất trung bình lớn nhất trong chu kỳ tích phân **30 phút** — https://daibieunhandan.vn/trien-khai-thu-nghiem-gia-ban-le-dien-hai-thanh-phan-tu-thang-10-2025-10390577.html (C #3). **Mâu thuẫn chưa giải:** A ghi thành phần công suất tính theo **công suất đăng ký**, C ghi theo **Pmax đo 30 phút**. Hai cách cho giá trị peak shaving rất khác nhau (§3.15.3). [UNKNOWN] Trạng thái thực tế 10/2026.
11. **[FACT] Thị trường C&I Việt Nam gần như chọn không bán điện dư.** 28.254 hệ TSXTTT (~1.614 MWp), chỉ ~287 hệ (~16,4 MW) đăng ký bán dư (cuối 07/2026) — https://vietnamnet.vn/en/rooftop-solar-saves-billions-of-dong-but-one-bottleneck-remains-2552186.html (A #3). Hệ trung áp không bán dư phải có thiết bị chống phát ngược (VBHN 52; E F-17). [INFERENCE] **Zero-export + tối đa tự tiêu thụ** là chiến lược phổ biến nhất ở VN; BESS hấp thụ PV lẽ ra bị cắt là nguồn giá trị lớn nhất.
12. **[FACT] NĐ 243/2026: điện xả từ BESS gắn với ĐMTMN được tính vào phần điện dư được mua; trần bán dư 50% sản lượng thực phát** — https://www.reccessary.com/en/news/vietnam-solar-grid-export-dppa (A #1, #2). [INFERENCE] Bộ tối ưu phải mô hình hóa **ngân sách xuất lưới theo kỳ** (không chỉ giới hạn kW tức thời) cho site có bán dư, và có cờ "cấm BESS xả ra lưới" cho site không bán dư.
13. **[FACT] OCPP 1.6 có 3 loại charging profile (ChargePointMaxProfile, TxDefaultProfile, TxProfile); stackLevel cao hơn thắng; giới hạn hiệu lực là giá trị nhỏ nhất.** Easee: TxDefaultProfile không tự xóa, có thể đè TxProfile — https://www.bender.de/docs/charge-controller/OCPP/ocpp-smart-charging/ ; https://developer.easee.com/docs/ocpp-smart-charging (E F-21). [INFERENCE] EV dynamic load management (DLM, quản lý tải động) phải tính lại giới hạn trạm theo dư công suất PCC và dùng ChargePointMaxProfile/TxProfile có hạn, với quirk theo hãng.
14. **[FACT] Trạm sạc EV kinh doanh ở VN có biểu giá riêng và công tơ riêng** (QĐ 14/2025/QĐ-TTg, TT 60/2025/TT-BCT) — https://vneconomy.vn/automotive/quy-dinh-moi-ve-gia-ban-dien-cho-tram-sac-xe-dien.htm (A #10). [INFERENCE] Bộ tối ưu phải hỗ trợ **nhiều biểu giá trong một site** (giá theo công tơ con).
15. **[FACT] Huawei có API VPP trên cloud** (`vpp/chargeAndDischarge`: dispatchSwitch 0/1/2, controlType SOC/duration, targetSOC, dispatchTime 0–1440 phút, powerDispatch W, requestID duy nhất; không gọi lại trước khi task xong; timeout 24 h) — nghiên cứu FusionSolar `source_code_clients_2.md` (tài liệu NBI). [INFERENCE] Đây là đường điều độ **tầng 4 (thị trường/VPP)** với độ trễ phút; không dùng cho tầng 1.
16. **[FACT] Tuyên bố tiết kiệm là của vendor, không kiểm chứng độc lập.** Stem Athena "lên tới 30%" hóa đơn — https://www.stem.com/wp-content/uploads/2021/05/Stem-Solutions-Overview_Athena_May-2021_v10.pdf (A #39, Low). GridBeyond nói tối ưu "respects asset-level constraints and degradation models" — https://secure.businesswire.com/news/home/20250930978130/en/GridBeyond-Launches-ViewPoint-Lens-to-Empower-Energy-Customers-With-Greater-Visibility-and-Control (B L49). [PROPOSAL] Sản phẩm không quảng cáo % tiết kiệm; chỉ báo cáo tiết kiệm đo theo M&V (hóa đơn bóng vs baseline phản thực, C §3.9).
17. **[INFERENCE] Bốn tầng điều khiển không thay thế nhau mà lồng nhau:** tầng 3/4 tạo **giới hạn và mục tiêu** (SOC đích, trần nhập, trần xuất, setpoint lưới theo slot); tầng 1 bám mục tiêu và luôn tôn trọng giới hạn native. Khi tầng trên hỏng, tầng dưới chạy chiến lược mặc định an toàn. Đây là cách duy nhất giữ được hành vi đúng khi dự báo sai hoặc mất mạng.
18. **[PROPOSAL] MVP chỉ cần tầng 1 + tầng 2 (luật minh bạch theo TOU + dự báo đơn giản).** MILP/MPC (tầng 3) để P1, sau khi có ≥ 3 tháng dữ liệu site để backtest chứng minh hơn luật. Tầng 4 (thị trường/VPP) là P2 và chỉ ở dạng "VPP-capable" (đồng ý A D-06, D-13; B PR-B06, PR-B14).

---

## 3. Phân tích chi tiết

### 3.1 Danh mục chiến lược

| Chiến lược | Mục tiêu | Input tối thiểu | Tác động lên thiết bị | Tầng chính | Giá trị ở VN hôm nay | Ưu tiên |
|---|---|---|---|---|---|---|
| **Zero-export** | P_grid ≥ 0 tại POC (không phát ngược) | Công tơ POC (≤1 s), danh sách inverter, giới hạn native | Hạ `P_limit` PV; ưu tiên sạc BESS trước khi cắt PV | 1 | **Cao, bắt buộc pháp lý** với site không bán dư (E F-17) | P0 (giám sát + cấu hình native; vòng của ta chỉ khi native không có) |
| **Export limitation** (giới hạn kW hoặc % / ngân sách kỳ) | P_export ≤ P_exp_max; E_export_kỳ ≤ 50% E_pv (NĐ 243) | Như trên + bộ đếm năng lượng theo kỳ | Như trên | 1 (kW), 2/3 (ngân sách kỳ) | Trung bình, chỉ ~287 site bán dư (A #3) | P0 (kW), P1 (ngân sách) |
| **Self-consumption maximization** | Giảm nhập lưới bằng PV + BESS | POC, SOC, giới hạn BMS | ESS bám `P_grid → target` (thường 0) | 1 (balancing) + 2 (SOC đích) | Trung bình. **Không tối ưu** dưới TOU mới: xả pin ban ngày giờ bình thường (1.833) thay vì giữ đến cao điểm (3.398) là lãng phí | P0 (như chế độ có điều kiện thời gian) |
| **TOU arbitrage / load shifting** | Sạc lúc rẻ (PV dư, thấp điểm), xả cao điểm | Lịch TOU có phiên bản, SOC, dự báo tải cao điểm | Lịch sạc/xả theo khung; SOC đích trước 17h30 | 2 (luật) → 3 (MILP) | **Cao nhất với BESS**; chênh lệch ~2,8× (A §3.4.3) | P0 (luật), P1 (tối ưu) |
| **PV curtailment có điều khiển** | Cắt PV tối thiểu cần thiết khi pin đầy và không được xuất | POC, SOC, P_ch_max | `P_limit` PV | 1 | Cao ở site zero-export; cần đo **năng lượng bị cắt** (C §3.11) | P0 |
| **Import cap / demand-limit enforcement** | P_import ≤ trần (MBA, hợp đồng, cầu dao) | POC, giới hạn MBA | ESS xả; giảm EV; (P2) sa thải tải | 1 | **Cao về an toàn vận hành** (tránh nhảy MCCB/quá tải MBA), độc lập với biểu giá | P0 |
| **Peak shaving (demand charge)** | Giảm Pmax 30 phút của tháng | POC, bộ đếm cửa sổ 30 phút đồng bộ công tơ EVN, Pmax đã đạt trong tháng | ESS xả theo `P_allow_rest` (C §3.9) | 1 (thực thi) + 2/3 (chọn ngưỡng, giữ SOC) | **Phụ thuộc thí điểm hai thành phần** (Phát hiện #10). Hôm nay chủ yếu chuẩn bị | P1 |
| **Backup reserve** | Giữ SOC ≥ SOC_res để cấp tải ưu tiên khi mất lưới | Cấu hình tải ưu tiên, thời gian cần cấp, khả năng off-grid của PCS | Ràng buộc SOC dưới cho mọi chiến lược | 1 (ràng buộc) + 2 (đổi theo lịch/mùa bão) | Trung bình; chỉ có ý nghĩa nếu PCS/ATS hỗ trợ off-grid | P0 (ràng buộc), P1 (động theo cảnh báo thời tiết) |
| **EV DLM (dynamic load management)** | Sạc EV trong dư công suất POC; ưu tiên; đủ năng lượng trước giờ đi | POC, phiên OCPP (đến/đi, kWh cần), trần nhóm trụ | ChargePointMaxProfile/TxProfile (OCPP) | 1 (giới hạn) + 2/3 (lịch) | Thấp–trung bình hôm nay; tăng khi đội xe điện C&I tăng (A §3.4.6) | P1 |
| **Demand response (DR)** | Giảm/tăng tải theo sự kiện từ lưới/aggregator | Kênh sự kiện (OpenADR/API/DI/IEC 104), baseline | Mục tiêu P_import trong cửa sổ sự kiện | 2 (nhận sự kiện) + 1 (thực thi) | [UNKNOWN] Chưa thấy cơ chế DR có trả tiền cho C&I ở VN trong nguồn đã có (A Q-A06) | P2 (hook) |
| **Thị trường / dịch vụ phụ trợ / VPP** | Bán năng lượng/linh hoạt (DA, imbalance, aFRR/FCR) | Tín hiệu giá thị trường, đấu thầu, đo đếm theo chuẩn TSO | Setpoint theo kết quả trúng thầu; đáp ứng tần số tại edge | 4 (+1 cho FCR) | Không áp dụng cho C&I BTM ở VN hiện nay. BESS ≥10 MW ≥110 kV có khung giá riêng (TT 62/2025, A #7) là FTM | P2 |
| **Generator steering** (genset) | Khởi động genset khi SOC thấp/mất lưới | DI/DO genset, SOC | Lệnh start/stop | 1 | Thấp; đặc thù site có genset | P2 |

### 3.2 Bốn tầng điều khiển

| | **Tầng 1: Rule-based real-time** | **Tầng 2: Lịch theo dự báo** | **Tầng 3: Tối ưu toán học (LP/MILP/MPC)** | **Tầng 4: Điều độ theo thị trường** |
|---|---|---|---|---|
| Ví dụ | Zero-export PI, balancing về target lưới, cửa sổ demand 30 phút, kẹp SOC, EV DLM | "Sạc từ PV dư 9h–16h, nạp lưới thấp điểm tới SOC đích, xả 17h30–22h30, giữ 20% dự phòng" | MILP 96–192 bước 15 phút, nhiều mục tiêu, giải lại mỗi 15 phút (receding horizon) | Bid DA/intraday, aFRR/FCR, sự kiện VPP/DR |
| Input | Đo POC (P, Q), P_pv, P_ess, SOC, giới hạn BMS/PCS (P_ch_max, P_dis_max), cấu hình ngưỡng, lệnh hiện hành | Lịch TOU có phiên bản, dự báo PV/tải (đơn giản: profile ngày tương tự), SOC hiện tại, cấu hình chiến lược | Dự báo PV/tải theo slot (có độ bất định), giá TOU/demand, tham số BESS (η, E, giới hạn, chi phí suy hao), EV sessions, Pmax đã đạt trong tháng | Giá thị trường, kết quả đấu thầu, tín hiệu tần số (FCR), yêu cầu đo đếm |
| Output | Setpoint mỗi chu kỳ: P_ess, P_limit PV, giới hạn EV | Lịch slot: chế độ + SOC đích + trần nhập/xuất | Lịch slot (như tầng 2) + lý do + giá trị đối ngẫu (shadow price) + chi phí dự kiến | Cam kết công suất theo slot + nghĩa vụ đáp ứng |
| Độ trễ cần | 0,1–2 s (zero-export ≤ 2 s theo Huawei); demand window: vài giây | Phút; cập nhật mỗi 15–60 phút | Giải < 10–30 s cho 1 site; chu kỳ 15 phút | DA: giờ; intraday: phút; FCR: < 1 s **tại edge** |
| Chạy ở đâu | **Edge** hoặc controller native (SmartLogger, EMMA, GX, EMS tủ BESS) | Cloud tạo; edge lưu ≥ 48 h và thực thi | Cloud (đề xuất); edge chỉ nhận kết quả | Cloud (bid) + edge (đáp ứng nhanh) |
| Fallback khi lỗi | Mất công tơ POC → ESS P=0, PV về giới hạn native (E §3.13). Mất thiết bị → watchdog native | Hết lịch hoặc lịch hỏng → chiến lược mặc định của site (thường self-consumption có giới hạn thời gian + zero-export) | Solver lỗi/timeout/infeasible → dùng lịch tầng 2 (luật) cho slot tiếp; cảnh báo | Mất tín hiệu thị trường → hủy cam kết theo quy tắc thị trường; về tầng 2/3 |
| Giải thích | Mã lý do tức thời (`CLAMPED_BY_BMS`, `EXPORT_LIMIT_ACTIVE`…) | Luật nào kích hoạt, ở slot nào | Lý do theo slot + chi phí so baseline + shadow price SOC | Kết quả đấu thầu, doanh thu, phạt lệch |
| Có gọi là AI? | **Không** | **Không** (dự báo thống kê ≠ AI) | Không; là "tối ưu dựa trên dự báo" | Không |

[INFERENCE] Tầng 2 và tầng 3 cùng output (một **lịch slot**) nên dùng chung một mô hình `DispatchPlan` và cùng vòng đời (§3.9). Như vậy MVP chạy tầng 2, P1 thay bộ sinh lịch bằng MILP mà không đổi edge.

### 3.3 Tầng 1: thuật toán tại edge (đặc tả)

**Chu kỳ.** [PROPOSAL] Vòng chính 1 s (khớp OpenEMS cycle ~1 s, E §3.14). Mỗi chu kỳ chụp một "process image" (giá trị không đổi trong chu kỳ), tính, ghi. Ghi Modbus chỉ khi thay đổi vượt deadband hoặc hết `min_write_interval` (tránh mòn flash, E §3.2 `persist`).

**(a) Grid-setpoint balancing (self-consumption / zero-export bằng ESS).**
```
e(k)        = P_grid_meas(k) − P_grid_target          # target = 0 cho self-consumption; = +margin cho zero-export
P_ess_req   = P_ess_meas(k) + Kp·e(k) + Ki·Σe·Δt      # PI; ESS + = xả
P_ess_cmd   = clamp(P_ess_req, −P_ch_max_BMS, +P_dis_max_BMS)
            ∩ [ràng buộc SOC: nếu SOC ≤ SOC_floor_eff → P_ess_cmd ≤ 0; nếu SOC ≥ SOC_max → P_ess_cmd ≥ 0]
            ∩ ramp: |P_ess_cmd − P_ess_cmd_prev| ≤ R·Δt
anti-windup: dừng tích phân khi bị kẹp
```
- Biên an toàn zero-export: `P_grid_target = +margin` (ví dụ 1–3% công suất PV hoặc ≥ 2 kW) để dao động không thành phát ngược. [INFERENCE] Margin phụ thuộc độ trễ vòng và độ ồn tải; phải tinh chỉnh tại hiện trường.
- **Không dùng** cùng lúc vòng của ta và vòng native trên cùng một biến (hai PI đánh nhau). Nếu native có zero-export, của ta chỉ đặt tham số và giám sát. [PROPOSAL] Cờ `control_owner ∈ {NATIVE, EDGE}` theo từng chức năng và từng site.

**(b) Zero-export bằng cắt PV (khi ESS đầy, không có ESS, hoặc ESS đã ở P_ch_max).**
```
if P_grid_meas < margin_low  (đang xuất hoặc sát 0):
    P_pv_limit ← P_pv_meas − (margin_target − P_grid_meas)    # giảm ngay, không chờ
elif P_grid_meas > margin_high trong T_release (ví dụ 10–30 s):
    P_pv_limit ← P_pv_limit + step_up (ví dụ 2–5 %/chu kỳ)    # nới chậm
```
- Hysteresis bất đối xứng: **giảm nhanh, tăng chậm**. Lý do: phát ngược là vi phạm; cắt dư chỉ mất ít kWh.
- Phân bổ giới hạn cho nhiều inverter: tỷ lệ theo công suất danh định, hoặc ưu tiên cắt inverter có điều khiển nhanh nhất. Inverter "ghi không tác dụng" (E F-07/F-35) phải bị loại khỏi pool và báo lỗi.
- Ước lượng **năng lượng bị cắt**: `E_curt ≈ Σ max(0, P_pv_available − P_pv_meas)·Δt`, với `P_pv_available` từ inverter tham chiếu không bị cắt, bức xạ, hoặc mô hình. Gắn cờ ước lượng.

**(c) Import cap (trần MBA/hợp đồng) — giới hạn vật lý, tức thời.**
```
excess = P_grid_meas − P_import_cap_eff        # cap_eff = cap − margin
if excess > 0:
    1) ESS xả thêm: P_ess_cmd += excess (trong giới hạn BMS, kể cả xuống dưới backup reserve nếu cấu hình cho phép, xem §3.8)
    2) giảm EV: phân bổ lại giới hạn EV (d)
    3) (P2) sa thải tải theo danh sách ưu tiên qua DO
    4) nếu vẫn vượt quá T_alarm: cảnh báo P1
```

**(d) Cửa sổ demand 30 phút (peak shaving theo Pmax).** Dùng công thức của C §3.9:
```
P_allow_rest = (P_target·T_w − E_so_far) / (T_w − t)
P_ess_cmd    = max(P_ess_cmd, P_grid_meas − P_allow_rest + P_ess_meas)   # xả bù phần vượt
```
- `P_target` không cố định: lấy `max(P_target_plan, Pmax_đã_đạt_trong_tháng)`. Lý do: khi Pmax tháng đã bị đặt cao, cố giữ dưới mức đó tốn pin mà không giảm hóa đơn. [INFERENCE] Đây là lỗi thường gặp của peak shaving ngưỡng cố định.
- Đồng bộ ranh giới cửa sổ với công tơ thanh toán (NTP; C §3.9).
- Ở chu kỳ cuối cửa sổ (t → T_w), `P_allow_rest` rất nhạy. Kẹp `T_w − t ≥ 60 s`; phần còn lại dùng import cap tức thời.

**(e) SOC guard (luôn chạy, mọi chế độ).**
- `SOC_floor_eff(t) = max(SOC_min_BMS_or_config, SOC_backup_reserve(t))`. Dưới mức này cấm xả (trừ ngoại lệ import cap, §3.8).
- `SOC_ceiling_eff(t) = min(SOC_max_config, 100% − SOC_space_reserve(t))`. "Space reserve" chừa chỗ hấp thụ PV dư buổi trưa ở site zero-export (giống EMMA, Phát hiện #5).
- Hysteresis SOC (ví dụ dừng xả ở 20%, chỉ cho xả lại khi ≥ 22%) để tránh bật/tắt liên tục quanh ngưỡng.
- SOC là giá trị BMS công bố, có độ bất định (C #8). Quyết định **an toàn** dựa vào giới hạn P/I do BMS công bố, không dựa vào SOC.

**(f) EV DLM tại edge.**
```
P_ev_avail = min(P_evse_group_cap,
                 P_import_cap_eff − (P_grid_meas − P_ev_meas)          # dư công suất tại POC
                 [+ P_pv_surplus nếu chế độ "chỉ sạc bằng PV dư"])
Phân bổ: 1) mỗi phiên đang sạc nhận I_min (thường 6 A/pha; E §3.19) theo thứ tự ưu tiên; phiên không đủ chỗ → 0 A (tạm dừng)
         2) phần còn lại chia theo trọng số (ưu tiên, kWh còn thiếu / thời gian còn lại)
Gửi: TxProfile có validTo, hoặc ChargePointMaxProfile cho cả trạm; cập nhật ≤ 1 lần/10–30 s mỗi trụ (tránh spam OCPP)
```
- [INFERENCE] Chu kỳ cập nhật EV chậm hơn vòng 1 s, vì OCPP + bộ sạc + xe phản ứng mất vài giây. Import cap phải do ESS/vòng nhanh gánh; EV chỉ giảm tải bền vững.
- Quirk hãng (Easee TxDefaultProfile đè TxProfile) phải nằm trong driver (Phát hiện #13).

### 3.4 Tầng 2: lịch theo dự báo + TOU (MVP)

**Bộ sinh lịch luật (rule-based scheduler) cho TOU VN [PROPOSAL].** Chạy trên cloud lúc 05:30 hằng ngày và khi có sự kiện (đổi tariff, đổi cấu hình, dự báo lệch lớn). Output là lịch 48 h, slot 15 phút.

| Khung (QĐ 963, T2–T7) | Chế độ slot | Tham số |
|---|---|---|
| 00:00–06:00 (thấp điểm) | `GRID_CHARGE_TO_TARGET` nếu cho phép sạc lưới | `SOC_target_0600 = clamp(E_need_peak − E_pv_surplus_fc, …)` (xem dưới) |
| 06:00–17:30 (bình thường) | `PV_SURPLUS_CHARGE` + zero-export; **không xả** cho tải (giữ năng lượng cho cao điểm) trừ import cap/peak window | `SOC_ceiling` có space reserve buổi sáng nếu dự báo PV dư lớn |
| 17:30–22:30 (cao điểm) | `PEAK_DISCHARGE` (balancing về P_grid_target = 0, hoặc xả đều) | Giữ `SOC ≥ SOC_backup_reserve` |
| 22:30–24:00 (bình thường) | `IDLE` / self-consumption chỉ khi SOC > mức cần cho ngày mai | — |
| Chủ nhật | Không cao điểm: `PV_SURPLUS_CHARGE` + self-consumption; không sạc lưới | — |

- Năng lượng cần cho cao điểm: `E_need_peak = Σ_{t∈peak} min(Load_fc(t), P_dis_max)·Δt / η_d`.
- Năng lượng PV dư dự báo nạp được ngày mai: `E_pv_surplus_fc = Σ_{t∈day} min(max(0, PV_fc − Load_fc), P_ch_max)·Δt·η_c`.
- SOC đích cuối thấp điểm: `SOC_target_0600·E = min(E·SOC_max, SOC_res·E + max(0, E_need_peak − E_pv_surplus_fc·α))`, với `α ∈ [0,1]` là hệ số tin cậy dự báo PV (ví dụ 0,7). Nạp lưới thấp điểm chỉ phần PV ngày mai **không** lấp được. Đây là chỗ dự báo tạo ra tiền: nạp lưới thừa thì mất chỗ cho PV dư lẽ ra bị cắt (giá trị cao nhất, §3.15.2).
- Dự báo MVP: tải = trung bình có trọng số của N ngày cùng loại (ngày làm việc/Chủ nhật/lễ); PV = profile ngày tương tự × hiệu chỉnh từ dự báo bức xạ (nếu có nguồn thời tiết) — giao diện chi tiết thuộc agent dự báo. Không gắn nhãn AI.

### 3.5 Tầng 3: công thức MILP cụ thể

**Phạm vi bài toán.** Một site, horizon `N` bước, bước `Δt`. Giải lại theo receding horizon (MPC): mỗi 15 phút hoặc khi có sự kiện; chỉ "chốt" các slot đầu, phần sau là dự kiến.

**Tập chỉ số**
- `t ∈ T = {0,…,N−1}`; mặc định `Δt = 0,25 h`, `N = 96` (24 h) đến `192` (48 h). [PROPOSAL] 48 h để thấy được cao điểm tối mai khi giải buổi chiều.
- `w ∈ W`: cửa sổ demand (30 phút → 2 bước 15 phút; nếu dữ liệu 5 phút thì 6 bước). `T_w ⊂ T`.
- `e ∈ EV`: phiên sạc đã biết hoặc dự kiến, với `a_e` (bước đến), `d_e` (bước đi).
- `m ∈ M`: công tơ/biểu giá con (ví dụ EV có biểu giá riêng). Bản cơ sở dưới đây giả định một biểu giá tại POC; mở rộng ở cuối mục.

**Tham số (đơn vị)**

| Ký hiệu | Ý nghĩa | Đơn vị | Nguồn |
|---|---|---|---|
| `c_imp[t]` | Giá nhập theo TOU | đ/kWh | M-TAR, phiên bản theo ngày |
| `c_exp[t]` | Giá bán dư (0 nếu không bán) | đ/kWh | Hợp đồng |
| `c_dem` | Giá công suất (hai thành phần) quy về kỳ | đ/kW·tháng | M-TAR; 0 nếu không áp dụng |
| `P̂_month` | Pmax đã ghi nhận trong tháng tới thời điểm giải | kW | Bộ đếm cửa sổ 30 phút |
| `PV_f[t]`, `L_f[t]` | Dự báo PV khả dụng, tải không linh hoạt | kW | M-ADV / dự báo |
| `E_cap` | Dung lượng khả dụng | kWh | Cấu hình, cập nhật theo SOH |
| `soc_0` | Năng lượng trong pin lúc giải | kWh | BMS (có độ bất định) |
| `S_min, S_max` | Giới hạn năng lượng | kWh | max(BMS, cấu hình) |
| `S_res[t]` | Dự phòng backup theo slot | kWh | Chính sách site |
| `η_c, η_d` | Hiệu suất sạc, xả (RTE = η_c·η_d) | — | Đo thực tế (ranh giới AC tại PCS; C #7) |
| `Pc_max[t], Pd_max[t]` | Giới hạn sạc/xả dự kiến (derate theo nhiệt/SOC) | kW | BMS/PCS, cập nhật mỗi lần giải |
| `R` | Ramp tối đa | kW/h (hoặc kW/bước) | PCS / grid code |
| `Gi_max[t], Ge_max[t]` | Trần nhập (MBA/hợp đồng), trần xuất (0 = zero-export) | kW | Cấu hình site, pháp lý |
| `c_deg` | Chi phí suy hao theo throughput xả | đ/kWh | §3.5.3 |
| `c_curt` | Chi phí cắt PV (nhỏ, để ưu tiên dùng PV) | đ/kWh | Mặc định ε |
| `Pev_min_e, Pev_max_e` | Công suất EV tối thiểu khi sạc (I_min), tối đa | kW | OCPP/trụ |
| `Eev_req_e` | Năng lượng cần trước `d_e` | kWh | Người dùng/lịch đội xe |
| `Pevse_cap` | Trần nhóm trụ (feeder) | kW | Cấu hình |
| `M_res, M_ev, M_grid` | Phạt vi phạm mềm (rất lớn) | đ/kWh | ≫ mọi giá |
| `v_term` | Giá trị năng lượng còn lại cuối horizon | đ/kWh | Ước lượng = giá cao điểm kế tiếp × η_d − c_deg |
| `allow_grid_charge`, `allow_ess_export` | Cờ chính sách | bool | Pháp lý/hợp đồng (NĐ 243) |

**Biến quyết định**

| Biến | Miền | Ý nghĩa |
|---|---|---|
| `gi[t], ge[t]` | ≥ 0 | Nhập, xuất lưới (kW) |
| `pc[t], pd[t]` | ≥ 0 | Sạc, xả BESS (kW, phía AC) |
| `s[t]` | `t = 0..N` | Năng lượng trong pin (kWh) |
| `pv[t]` | `0 ≤ pv ≤ PV_f` | PV sử dụng; `PV_f − pv` = cắt |
| `pev[e,t]` | ≥ 0 | Công suất sạc EV phiên e |
| `zb[t]` | {0,1} | 1 = chế độ sạc (cấm xả) |
| `zg[t]` | {0,1} | 1 = chế độ nhập (cấm xuất) |
| `zev[e,t]` | {0,1} | 1 = phiên e đang sạc (để áp I_min) |
| `Pk` | ≥ `P̂_month` | Pmax tháng sau horizon (kW) |
| `σres[t], σev[e], σg[t]` | ≥ 0 | Slack vi phạm mềm |

**Hàm mục tiêu (cực tiểu chi phí trên horizon)**
```
min  Σ_t ( c_imp[t]·gi[t] − c_exp[t]·ge[t] ) · Δt                       # năng lượng
   + c_dem · ( Pk − P̂_month )                                           # demand: chỉ phần tăng thêm trong tháng
   + c_deg · Σ_t pd[t] · Δt                                              # suy hao (theo throughput xả)
   + c_curt · Σ_t ( PV_f[t] − pv[t] ) · Δt                              # cắt PV
   − v_term · s[N]                                                       # giá trị năng lượng còn lại
   + M_res·Σ_t σres[t] + M_ev·Σ_e σev[e] + M_grid·Σ_t σg[t]             # phạt vi phạm mềm
```
- Ghi chú demand: horizon ngắn hơn kỳ hóa đơn, nên chỉ tính **phần tăng thêm** so với `P̂_month`. Nếu dùng nguyên `c_dem·Pk` cho bài toán 1 ngày, solver sẽ "đầu tư" pin quá mức để hạ đỉnh của một ngày. Nếu biểu giá tính theo **công suất đăng ký** thay vì Pmax đo (mâu thuẫn ở Phát hiện #10), số hạng này đổi thành phạt vượt đăng ký: `c_over·max(0, Pk − P_reg)`.

**Ràng buộc**
```
(1) Cân bằng công suất (dấu: lưới + = nhập):
    gi[t] − ge[t] + pv[t] + pd[t] − pc[t] = L_f[t] + Σ_e pev[e,t]                ∀t

(2) Động học SOC:
    s[t+1] = s[t] + ( η_c·pc[t] − pd[t]/η_d ) · Δt − δ_self·Δt                   ∀t
    s[0]   = soc_0

(3) Giới hạn SOC và dự phòng:
    S_min ≤ s[t] ≤ S_max                                                          ∀t
    s[t] ≥ S_res[t] − σres[t]                                                     ∀t
    (tùy chọn) s[N] ≥ S_term_min

(4) Giới hạn công suất từ BMS/PCS + cấm sạc-xả đồng thời (binary):
    pc[t] ≤ Pc_max[t] · zb[t]
    pd[t] ≤ Pd_max[t] · (1 − zb[t])                                               ∀t

(5) Giới hạn lưới + cấm nhập-xuất đồng thời:
    gi[t] ≤ Gi_max[t] · zg[t] + σg[t]
    ge[t] ≤ Ge_max[t] · (1 − zg[t])                                               ∀t
    (zero-export: Ge_max = 0 ⇒ ge ≡ 0, zg có thể bỏ)

(6) Ramp (net ESS):
    −R·Δt ≤ (pd[t] − pc[t]) − (pd[t−1] − pc[t−1]) ≤ R·Δt                         ∀t ≥ 1 (t=0 so với đo hiện tại)

(7) Demand window (trung bình nhập trong cửa sổ):
    (1/|T_w|) · Σ_{t∈T_w} gi[t] ≤ Pk                                              ∀w ∈ W_billable
    Pk ≥ P̂_month

(8) PV:
    0 ≤ pv[t] ≤ PV_f[t]

(9) EV:
    Pev_min_e·zev[e,t] ≤ pev[e,t] ≤ Pev_max_e·zev[e,t]        với t ∈ [a_e, d_e); pev = 0 ngoài khoảng
    Σ_t pev[e,t]·Δt + σev[e] ≥ Eev_req_e                                         ∀e
    Σ_e pev[e,t] ≤ Pevse_cap                                                      ∀t

(10) Chính sách:
    nếu ¬allow_grid_charge:  pc[t] ≤ pv[t]                     (sạc chỉ từ PV; tuyến tính, hơi chặt)
                             hoặc chính xác hơn: gi[t] ≤ L_f[t] + Σ_e pev[e,t]
    nếu ¬allow_ess_export:   ge[t] ≤ pv[t]                     (xuất chỉ phần PV)
    ngân sách xuất kỳ (NĐ 243, bán dư ≤ 50% sản lượng):
        E_exp_sofar + Σ_t ge[t]·Δt ≤ 0,5·(E_pv_sofar + Σ_t pv[t]·Δt)            (phân bổ theo ngày bằng tham số)
```

**Biến thể tránh binary.** [INFERENCE] Khi `c_imp[t] > 0`, `η_c·η_d < 1` và cho phép cắt PV (biến `pv`), sạc-xả đồng thời làm tăng chi phí nên LP relaxation thường tự tránh. Ngoại lệ: khi cần "đốt" năng lượng (xuất bị cấm, PV không cắt được) hoặc giá xuất âm. Chiến lược đề xuất:
1. Giải LP (bỏ `zb`, `zg`, `zev`), thêm phạt nhỏ `ε·(pc + pd)`.
2. Kiểm tra hậu nghiệm `min(pc[t], pd[t]) > tol` hoặc `min(gi, ge) > tol` hoặc EV dưới I_min. Nếu có → giải MILP đầy đủ.
3. EV: I_min là ràng buộc semi-continuous thật (6 A). Với ít phiên (< 20) MILP vẫn nhỏ. Với bãi xe lớn: làm tròn hậu nghiệm + để tầng 1 phân bổ.

**Mở rộng nhiều biểu giá trong site (EV công tơ riêng).** [PROPOSAL] Tách `gi` thành `gi_main[t]` và `gi_ev[t]` theo topology đo; ràng buộc cân bằng tách theo nhánh. Chỉ làm khi topology điện cho phép (EV sau công tơ riêng nhưng vẫn sau MBA chung: trần MBA áp lên tổng).

#### 3.5.1 Kích thước và thời gian giải

| Cấu hình | Biến liên tục | Binary | Ràng buộc | Ghi chú |
|---|---|---|---|---|
| 96 bước, không EV | ~7×96 ≈ 670 | 2×96 = 192 (hoặc 0 nếu LP) | ~1.000 | [INFERENCE] Bài toán rất nhỏ; HiGHS/CBC thường giải trong < 1 s. Cần benchmark (Q-G05) |
| 192 bước + 10 phiên EV | ~2.300 | ~2.300 | ~4.000 | Vẫn nhỏ; đặt `time_limit` 20 s + `mip_gap` 0,5% |
| 500 site × 192 bước | 500 bài độc lập | — | — | Song song theo site; không gộp trừ khi có ràng buộc chung (VPP, trần feeder chung) |

#### 3.5.2 Receding horizon (MPC) và đầu ra cho edge

- Giải lại: định kỳ 15 phút (lệch pha ngẫu nhiên giữa các site để rải tải), và theo sự kiện: lệch SOC thực tế vs kế hoạch > 5% E_cap; dự báo PV/tải mới lệch > X%; giới hạn BMS thay đổi; đổi tariff/cấu hình; edge báo chiến lược bị ghi đè.
- **Không gửi `pd/pc` thô làm setpoint cứng.** [PROPOSAL] Mỗi slot gửi một "envelope":
  - `mode` (`PV_SURPLUS_CHARGE`, `GRID_CHARGE_TO_TARGET`, `PEAK_DISCHARGE`, `GRID_SETPOINT`, `HOLD`, `IDLE`);
  - `soc_target_end` (SOC đích cuối slot) và/hoặc `p_grid_target` (setpoint lưới);
  - `p_import_cap`, `p_export_cap`, `soc_floor`, `soc_ceiling`;
  - `p_ess_hint` (tham khảo).
  
  Tầng 1 bám `p_grid_target` hoặc tốc độ cần để đạt `soc_target_end`, luôn trong các cap. Lý do: sai số dự báo tải trong slot 15 phút được vòng nhanh hấp thụ, không biến thành nhập/xuất ngoài ý muốn. Tương tự OpenEMS Balancing (`targetGridSetpoint`) và Victron Mode 2 (`/AcPowerSetpoint`) (Phát hiện #6, #7).
- Sai số dự báo: [PROPOSAL] P1 dùng **dự báo điểm + biên an toàn** (giữ thêm SOC ≈ k × độ lệch chuẩn sai số tải cao điểm). Stochastic/robust MPC để V2+.

#### 3.5.3 Chi phí suy hao (degradation cost)

- Mô hình tuyến tính throughput [INFERENCE, công thức phổ biến]: `c_deg ≈ C_repl / (N_cycle(DoD) × E_cap × DoD × 2)` theo kWh throughput (sạc + xả), hoặc gấp đôi nếu chỉ tính trên kWh xả như trong hàm mục tiêu trên. Ví dụ **giả định** (không có nguồn giá VN, A §3.4.3): `C_repl` = 3 triệu đ/kWh, 6.000 chu kỳ ở 90% DoD → `c_deg ≈ 3.000.000 / (6.000 × 0,9) ≈ 556 đ/kWh xả`.
- Ý nghĩa: với chênh lệch arbitrage lưới ≈ 2.076 đ/kWh (§3.15.2), ví dụ này vẫn có lãi; với chênh lệch Chủ nhật (≈ 511 đ/kWh) thì **không**. Bộ tối ưu tự động không chạy arbitrage Chủ nhật nếu `c_deg` đặt đúng. [PROPOSAL] `c_deg` là tham số site, kèm giải thích trên UI; mặc định bảo thủ.
- Suy hao theo lịch (calendar aging) và theo SOC trung bình/nhiệt độ: P2 (mô hình phi tuyến, cần dữ liệu hãng pin). Không tuyên bố "tối ưu tuổi thọ pin" nếu chỉ có hệ số tuyến tính.

### 3.6 Solver: lựa chọn cho team Java

[INFERENCE — kiến thức nền, **chưa kiểm chứng license/phiên bản trong phiên này** (Q-G04)]

| Solver / thư viện | Loại | License (cần kiểm chứng) | Tích hợp Java | Phù hợp |
|---|---|---|---|---|
| **HiGHS** | LP/MIP (simplex, IPM, branch-and-cut) | MIT | Không có binding Java chính thức đã kiểm chứng; dùng qua OR-Tools MPSolver (nếu bản OR-Tools hỗ trợ backend HiGHS) hoặc JNI/sidecar | Rất phù hợp kích thước bài toán; mặc định của nhiều thư viện Python (linopy, PyPSA) |
| **CBC** (COIN-OR) | MIP | EPL-2.0 | Qua OR-Tools MPSolver | Ổn định, chậm hơn HiGHS ở nhiều benchmark công khai (cần xác nhận) |
| **Google OR-Tools** | Bộ wrapper (MPSolver: GLOP LP, SCIP, CBC, …) + CP-SAT | Apache-2.0 | **Có binding Java chính thức** (Maven) | Lựa chọn tự nhiên cho Spring Boot; CP-SAT dùng được cho MILP nhỏ chỉ có hệ số nguyên (không phù hợp số thực) |
| **SCIP** | MIP | Apache-2.0 (từ v9, cần kiểm chứng) | Qua OR-Tools | Dự phòng cho MILP khó |
| **Timefold Solver** (fork OptaPlanner) | Metaheuristic, constraint solver | Apache-2.0 (bản community) | Java native | **Không** phù hợp dispatch liên tục (cân bằng công suất, SOC). Phù hợp lập lịch rời rạc: phân ca O&M, xếp thứ tự phiên sạc khi số lượng lớn |
| **Gurobi / CPLEX** | LP/MIP thương mại | Thương mại; license cloud/SaaS tính riêng | Java API chính thức | Không cần cho bài toán kích thước này; chi phí license trên mỗi node cloud. Chỉ xem xét nếu làm tối ưu danh mục VPP lớn |

[PROPOSAL] ADR ứng viên (`ADR-OPT`): tách **Optimization Service** thành dịch vụ riêng, không nhúng vào backend chính.
- Phương án A: Java + OR-Tools MPSolver (backend HiGHS hoặc SCIP/CBC). Ưu: một ngôn ngữ. Nhược: mô hình hóa bằng API mệnh lệnh, khó đọc hơn.
- Phương án B: Python sidecar (Pyomo/linopy + HiGHS), hợp đồng JSON `OptimizationRequest/Result` có version. Ưu: hệ sinh thái tối ưu năng lượng mạnh, backtest dễ. Nhược: thêm runtime.
- Khuyến nghị: **B cho P1**, vì bài toán sẽ thay đổi nhiều và cần backtest nhanh; ranh giới JSON giữ team Java độc lập. Kết quả phải **xác định được** (deterministic: cùng input + cùng phiên bản → cùng lịch) để audit, nên pin version solver và seed.

### 3.7 Tầng 4: thị trường, DR, VPP

- Bằng chứng ship thực tế: Ampowr (DA + imbalance + aFRR, Hà Lan — Phát hiện #3); Sungrow PowerStack có chế độ VPP (B #16); Huawei có API VPP cloud và EMMA "third-party VPP integration" (Phát hiện #15; E F-05); OpenEMS có tham chiếu §14a EnWG (B L45).
- [INFERENCE] FCR/aFRR đòi đáp ứng nhanh (giây) **tại edge** theo tín hiệu tần số/AGC, cộng đo đếm và chứng nhận tiền định chất (prequalification) của TSO. Đây là sản phẩm riêng, không phải tính năng phụ.
- Việt Nam: [UNKNOWN] chưa có bằng chứng trong các nguồn đã có về thị trường dịch vụ phụ trợ/DR có trả tiền cho C&I sau công tơ (A Q-A06). DPPA ảo dùng giá thị trường 30 phút (C ledger #36): là động lực **dữ liệu đối soát**, chưa phải điều độ.
- [PROPOSAL] P2 "VPP-capable": (1) mô hình `FlexibilityOffer` (kW khả dụng lên/xuống theo slot, từ lịch + SOC headroom); (2) nguồn lệnh `DR`/`GRID_OPERATOR` đã có trong envelope lệnh (E §3.19); (3) API sự kiện DR (OpenADR 3.0 REST/JSON là ứng viên; E F-22); (4) không phát triển bidding.

### 3.8 Xếp chồng ưu tiên và giải xung đột

**Nguyên tắc.** Tầng trên **không cộng lệnh**, mà thu hẹp **khoảng cho phép** `[P_ess_lo, P_ess_hi]` (và tương tự cho PV limit, EV limit). Tầng dưới chỉ chọn điểm trong khoảng còn lại. Đây là cách OpenEMS làm với Power Solver (B #15) và là đề xuất PR-B03 của Agent B.

| Mức | Lớp | Ai thực thi | Tạo ràng buộc gì | Có thể bị ghi đè bởi |
|---|---|---|---|---|
| L0 | **An toàn thiết bị** (BMS, PCS, relay, bảo vệ inverter) | Thiết bị native | Giới hạn I/P/V/T, contactor | **Không gì cả.** EMS chỉ đọc, kẹp lệnh theo đó |
| L1 | **Giám sát edge** (watchdog, mất công tơ POC, dữ liệu stale, lệnh hết hạn) | Edge | Về trạng thái an toàn (§3.2 fallback) | L0 |
| L2 | **Tuân thủ lưới**: zero-export / export limit, lệnh điều độ (IEC 104, `SET_REVERSE_FEED_BLOCK`), PF (P2) | Native hoặc edge | `ge ≤ Ge_max`; PV limit | L0, L1 |
| L3 | **Trần nhập vật lý** (MBA, hợp đồng, CB) | Edge | `gi ≤ Gi_max` | L0–L2 |
| L4 | **Backup reserve** | Edge | `SOC ≥ S_res` | L0–L3 (xem ngoại lệ dưới) |
| L5 | **Cam kết DR/VPP đã chấp nhận** (P2) | Edge theo lịch | Mục tiêu P_grid trong cửa sổ sự kiện | L0–L4 |
| L6 | **Peak shaving (demand charge)** | Edge | Xả theo `P_allow_rest` | L0–L5 |
| L7 | **Cam kết EV** (đủ kWh trước giờ đi) | Edge + lịch | Năng lượng tối thiểu cho phiên | L0–L6 |
| L8 | **Kinh tế**: TOU arbitrage, self-consumption, giảm cắt PV | Lịch tầng 2/3 → edge | Chọn điểm trong khoảng còn lại | Tất cả ở trên |
| L9 | Lệnh tay của người vận hành (manual override) | Edge | Trong khoảng L0–L4; có hạn | L0–L4 (không bao giờ vượt) |

- Thứ tự này khớp đề bài (safety > grid compliance > backup reserve > peak shaving > economic) và chèn thêm L1 (watchdog), L3 (trần vật lý), L5 (DR), L7 (EV).
- [PROPOSAL] Thứ tự L4–L8 **cấu hình được theo site**, trong giới hạn: L0–L3 cố định, không cho người dùng đổi.

**Ma trận xung đột thường gặp**

| Xung đột | Quy tắc mặc định | Tùy chọn cấu hình | Mã lý do |
|---|---|---|---|
| Import cap (L3) vs backup reserve (L4): tải vượt trần MBA khi SOC ≈ dự phòng | L3 thắng: được xả xuống dưới `S_res` tới `S_res_hard` (ví dụ 50% của S_res), vì nhảy CB cũng làm mất điện tải | `allow_reserve_dip_for_import_cap`, `S_res_hard` | `RESERVE_DIPPED_FOR_IMPORT_CAP` |
| Zero-export (L2) vs pin đầy | Cắt PV | — | `PV_CURTAILED_EXPORT_LIMIT` |
| Zero-export vs lịch "giữ chỗ cho cao điểm" (không sạc) | L2 thắng: sạc pin để hấp thụ PV trước khi cắt PV, kể cả khi lịch nói `HOLD` | — | `CHARGE_FORCED_BY_EXPORT_LIMIT` |
| Peak shaving (L6) vs TOU (L8): đỉnh demand rơi vào giờ bình thường, lịch muốn giữ SOC cho cao điểm | L6 thắng tại thời điểm vượt, chỉ xả phần cần thiết (`P_allow_rest`); lịch tầng 3 giải lại với SOC mới | Tầng 3 nên dự kiến trước bằng ràng buộc (7) | `PEAK_SHAVING_OVERRIDE` |
| EV (L7) vs import cap (L3) | Giảm EV về I_min, rồi tạm dừng phiên ưu tiên thấp | Ưu tiên theo phiên/đội xe | `EV_THROTTLED_IMPORT_CAP` |
| Lệnh tay (L9) vs zero-export | Lệnh tay bị kẹp, báo `APPLIED_CLAMPED` | — | `MANUAL_CLAMPED_BY_GRID_LIMIT` |
| Lệnh điều độ EVN (L2) vs mọi lịch | L2 thắng, lịch bị treo đến khi lệnh hết hiệu lực; tầng 3 giải lại | — | `OVERRIDDEN_BY_GRID_OPERATOR` |
| Chế độ native của hãng vs chiến lược của ta | Không chạy song song trên cùng biến; `control_owner` quyết định | — | `NATIVE_MODE_ACTIVE` |

### 3.9 Vòng đời kế hoạch điều độ (DispatchPlan)

```
            ┌──────────── REJECTED (validation fail / người duyệt từ chối)
            │
DRAFT ──► VALIDATED ──► APPROVED ──► SCHEDULED ──► EXECUTING ──► COMPLETED
  ▲          │              │            │             │
  │          │              │            │             ├──► ABORTED (lỗi nghiêm trọng, người vận hành dừng, lệnh L2)
  │          └──► (tự động duyệt nếu trong guardrail)  │
  │                         │            ├──► SUPERSEDED (bản mới hơn được duyệt cho cùng khoảng thời gian)
  └── tạo bản mới (version+1) khi giải lại              └──► EXPIRED (hết horizon mà chưa chạy, ví dụ edge offline)
```

| Trạng thái | Ai/cái gì chuyển | Điều kiện / việc làm |
|---|---|---|
| `DRAFT` | Optimizer, bộ luật, người dùng (lịch tay), backtest | Lưu input snapshot (hash): tariff version, forecast version, site config version, giới hạn thiết bị, solver + version, tham số |
| `VALIDATED` | Validator tự động | Kiểm: mọi slot trong cap site; SOC trajectory trong [S_min, S_max]; không vi phạm export/import cap; mode có trong `capability_profile` thiết bị (E §3.19); không chồng lấn mâu thuẫn với lệnh L2 đang hiệu lực; tổng năng lượng hợp lý (cân bằng); horizon ≥ 48 h cho fallback |
| `APPROVED` | **Tự động** nếu plan do optimizer/luật sinh và nằm trong guardrail của site (chính sách đã được người có quyền duyệt một lần). **Thủ công** (2 người với site lớn) cho lịch tay hoặc vượt guardrail (ví dụ cho phép xả xuống dưới dự phòng) | Ghi `approved_by`, lý do |
| `SCHEDULED` | Dispatcher | Đóng gói thành lệnh `APPLY_SCHEDULE` (envelope E §3.19: `command_id`, `valid_from`, `expires_at`, `supersedes`), gửi edge; nhận `ACCEPTED` |
| `EXECUTING` | Edge (slot đầu tiên bắt đầu) | Edge báo theo slot: `SLOT_STARTED`, `SLOT_APPLIED`/`APPLIED_CLAMPED`/`OVERRIDDEN(reason)`, `SLOT_ENDED` + số đo |
| `COMPLETED` | Hết slot cuối | Tính actual vs planned (§3.10) |
| `ABORTED` | Người vận hành, lỗi thiết bị, lệnh L2 dài hạn | Edge về chiến lược mặc định; ghi lý do |
| `SUPERSEDED` | Plan mới (MPC giải lại) | Chỉ các slot **chưa bắt đầu** bị thay; slot đang chạy kết thúc theo bản cũ (hoặc theo bản mới nếu bản mới đánh dấu `preempt=true`) |

- **Versioning.** `plan_id` cố định cho một "dòng kế hoạch" của site; `version` tăng mỗi lần giải lại. Bản đã `APPROVED` là **bất biến** (immutable); sửa = tạo version mới. Lưu cả input snapshot để tái lập kết quả (deterministic replay).
- **Audit.** Mọi chuyển trạng thái: `who/what`, `ts`, `from→to`, `reason`. Lưu tối thiểu theo chính sách lưu trữ của agent bảo mật (đề xuất ≥ 2 năm cho site có hợp đồng ESCO/PPA, vì tiết kiệm là cơ sở thanh toán).
- **MPC tạo nhiều version.** 96 version/ngày/site × 500 site ≈ 48.000 plan/ngày. [PROPOSAL] Lưu đầy đủ version đã thực thi ít nhất 1 slot; version bị supersede trước khi chạy chỉ lưu tóm tắt + hash input trong 30 ngày.

### 3.10 Thực thi, ack, actual vs planned

- Ack theo state machine lệnh của Agent E (§3.19): `RECEIVED → ACCEPTED → DISPATCHED → APPLIED / APPLIED_CLAMPED / FAILED_*`. Plan dùng thêm ack **theo slot**.
- [PROPOSAL] Bảng `plan_slot_result` (TimescaleDB hypertable, 15 phút):

| Trường | Ý nghĩa |
|---|---|
| `plan_id, version, slot_start` | Khóa |
| `mode_planned, mode_actual` | Chế độ |
| `e_ess_planned, e_ess_actual` (kWh, + xả) | Năng lượng pin |
| `soc_end_planned, soc_end_actual` | SOC cuối slot |
| `e_import_planned/actual, e_export_planned/actual` | Lưới |
| `p_demand_window_max_actual` | Trung bình 30 phút lớn nhất chạm slot |
| `e_pv_curtailed_est` | Ước lượng cắt PV |
| `cost_planned, cost_actual` | Theo tariff version của plan |
| `deviation_cause` | `FORECAST_LOAD`, `FORECAST_PV`, `DEVICE_CLAMP`, `HIGHER_PRIORITY_OVERRIDE(level)`, `COMM_LOSS`, `MANUAL`, `NATIVE_MODE` |
| `reason_codes[]` | Mã lý do tầng 1 trong slot |

- Phân rã lệch chi phí: `Δcost = cost_actual − cost_planned` tách thành phần do dự báo (chạy lại plan với dữ liệu thực = "perfect hindsight" cùng input khác), do kẹp thiết bị, do override. [INFERENCE] Đây là bằng chứng để biết nên đầu tư vào dự báo hay vào tích hợp thiết bị.
- KPI tầng điều độ: tỷ lệ slot `APPLIED` (không bị kẹp), sai lệch SOC trung bình, MAE dự báo tải giờ cao điểm, Pmax thực tế vs mục tiêu, kWh cắt PV, số lần vi phạm export (phải = 0).

### 3.11 Giải thích quyết định (explainability)

[PROPOSAL] Ba cấp giải thích, không cần ML:
1. **Theo slot (cho người vận hành):** câu template từ mã lý do + số liệu, ví dụ "17:30–17:45: xả 180 kW vì đang giờ cao điểm (3.398 đ/kWh), dự báo đủ năng lượng tới 22:30 với dự phòng 20%". Mã lý do mẫu: `CHARGE_PV_SURPLUS`, `CHARGE_PV_WOULD_BE_CURTAILED`, `CHARGE_GRID_OFFPEAK_TO_TARGET`, `HOLD_FOR_PEAK`, `DISCHARGE_PEAK_TOU`, `DISCHARGE_PEAK_SHAVING`, `HOLD_BACKUP_RESERVE`, `IDLE_SPREAD_BELOW_DEG_COST`, `CLAMPED_BY_BMS`, `PV_CURTAILED_EXPORT_LIMIT`, `OVERRIDDEN_BY_GRID_OPERATOR`.
2. **Theo kế hoạch (cho chủ C&I):** chi phí dự kiến vs baseline (a) không BESS, (b) luật tầng 2, (c) plan tối ưu. Nêu "vì sao chọn chiến lược này": phần chênh lệch chi phí lớn nhất đến từ đâu (cao điểm tránh được, PV cứu khỏi cắt, demand giảm).
3. **Theo mô hình (cho kỹ sư):** giá trị đối ngẫu (dual/shadow price) của ràng buộc SOC theo slot = "giá trị biên của 1 kWh trong pin" (đ/kWh). Dual của ràng buộc demand = giá trị của 1 kW giảm đỉnh. Với MILP, lấy dual từ LP cố định binary. Hiển thị biểu đồ "giá trị năng lượng lưu trữ" theo giờ cùng giá TOU giúp giải thích vì sao pin không xả lúc 15h.

### 3.12 Mô phỏng what-if và backtest

- **What-if (thiết kế/bán hàng):** thay kích thước BESS (kWh/kW), tariff (khung cũ TT 16 vs QĐ 963; có/không hai thành phần), chiến lược, `c_deg`, chính sách sạc lưới → hóa đơn bóng, chu kỳ/năm, kWh cắt PV. Dùng dữ liệu đo 15 phút ≥ 1 năm (hoặc ≥ 3 tháng + ghi rõ mùa thiếu).
- **Backtest chiến lược (vận hành):** replay dữ liệu lịch sử qua đúng code tầng 2/3 **với dự báo như đã có lúc đó** (không dùng dữ liệu tương lai), cộng một mô hình edge đơn giản (tầng 1 bám envelope, pin bucket model với η, giới hạn P, SOC). So với chạy "perfect foresight" để có cận trên.
- Mô hình pin trong mô phỏng là mô hình **năng lượng**, không mô phỏng điện hóa/nhiệt. Mọi kết quả gắn nhãn "Mô phỏng" trên UI và báo cáo; không trộn vào số liệu đo (quy ước dự án: không giả vờ tính năng mô phỏng là thật).
- Giới hạn biết trước: dữ liệu 5 phút cloud của hãng làm mất đỉnh ngắn → mô phỏng peak shaving cần dữ liệu ≤ 1 phút từ edge; ghi rõ độ phân giải nguồn.
- [PROPOSAL] Cổng chất lượng trước khi bật tầng 3 cho một site: backtest 90 ngày cho thấy plan MILP rẻ hơn luật tầng 2 ≥ X% (X do sản phẩm quyết, ví dụ 3%) và **không** tăng vi phạm (export, reserve, EV).

### 3.13 Vendor thực sự ship gì (đã có bằng chứng)

| Vendor / sản phẩm | Chiến lược / chế độ có tài liệu | Tầng | Nguồn (ledger) | Ghi chú |
|---|---|---|---|---|
| Huawei app (residential/C&I nhỏ) | Maximum self-consumption; Fully fed to grid; TOU (khung tay, cho sạc lưới) | 1–2 | #4 | Ba chế độ, không phải optimizer |
| Huawei Northbound | `ch_discharge_model` 0–4 (forced, TOU price, fixed, automatic) | — | #4 | Đọc chế độ đang chạy |
| Huawei (Modbus, qua thư viện cộng đồng) | TOU periods, capacity control periods (peak shaving), fixed charge periods, max feed-grid power, zero power grid connection, forcible charge/discharge | 1–2 | #5 | Tên dịch vụ của thư viện, không phải tên Huawei chính thức |
| Huawei SmartLogger5000B / C&I | Zero feed-in ≤ 2 s, peak shaving ≤ 5 s; peak shaving chỉ hợp lệ ở kịch bản on/off-grid (PQ/VSG) theo một manual | 1 | #2, #6 | Ma trận chế độ hợp lệ theo kịch bản |
| Huawei EMMA/SmartAssistant, SmartEMO | Dự báo dư PV, giữ SOC space reserve; so sánh có/không EMMA; demand charge theo TOU (3/2026) | 2 | #7, #8 | Có thành phần dự báo |
| Huawei cloud VPP API | Forced charge/discharge theo SOC đích hoặc thời lượng, ≤ 100 plant/lệnh | 4 | #9 | Async, phút |
| Ampowr Cosmos | Peak shaving theo trần lưới, net-zero/self-consumption, curtailment, generator steering, EV/backup; DA+imbalance+aFRR; chạy tiếp tại chỗ khi mất mạng | 1–4 | #10–#12 | Thị trường chỉ Hà Lan |
| InfinitePower (BESS EMS tủ) | Lập lịch, peak shaving, time-shift, backup, SOC | 1–2 | #13 | Trang sản phẩm; không thấy register map |
| Schneider EMA | MPC cloud, lịch 15 phút/72 h, lịch mặc định 48 h, DR qua utility/aggregator | 3 (+DR) | #1 | Tài liệu cũ (~2017) |
| SolarEdge ONE for C&I | Tối ưu theo biểu giá + dự báo thời tiết, peak shaving nâng cao, EV (Wevo), export limitation cần công tơ tại điểm đấu nối | 1–3 | #14, #15 | "advanced peak shaving" chưa có mô tả thuật toán |
| OpenEMS | PeakShaving, Balancing(`targetGridSetpoint`), ToU optimizer 15 phút, GridOptimizedCharge, OCPP server; Power Solver | 1–2 | #16 | Tên controller khác: [UNKNOWN] |
| Victron GX | ESS Mode 2 (`/AcPowerSetpoint` reg 2700), Mode 3 | 1 | #17 | Tên chế độ ESS khác ("Optimized…", Dynamic ESS): [UNKNOWN] |
| Siemens SICAM MGC | Peak shaving, reserve monitoring, quản lý SOC, dự báo, DR & dynamic load control, thị trường | 1–4 | #18 | Microgrid on-prem |
| Stem Athena, GridBeyond | Tối ưu dự đoán, value stacking; GridBeyond nêu mô hình suy hao | 3–4 | #19, #20 | Tuyên bố vendor |

[INFERENCE] Mẫu chung: **mọi hãng phần cứng có sẵn tầng 1 (zero-export, peak shaving ngưỡng) và tầng 2 đơn giản (khung TOU tay)**. Khác biệt nằm ở tầng 3 (dự báo + tối ưu) và tầng 4 (thị trường). Sản phẩm đa hãng của ta không nên viết lại tầng 1 khi native có, mà làm tốt **tầng 2–3 đa hãng + biểu giá VN + giải thích + M&V**.

### 3.14 Bằng chứng tiết kiệm

- Chỉ có tuyên bố vendor (Stem "lên tới 30%", Low). Không có nghiên cứu độc lập trong nguồn hiện có. [UNKNOWN] Số liệu tiết kiệm thực tế của BESS C&I ở Việt Nam.
- [PROPOSAL] Cách báo cáo tiết kiệm (M&V) thống nhất với C §3.9: `Savings = Bill_baseline_counterfactual − Bill_shadow_actual`, cùng tariff version. Baseline phản thực: `E_cons` (đo/suy) × tariff, không PV/không BESS; và baseline "PV không BESS". Ghi rõ là ước tính mô hình.
- Tách nguồn tiết kiệm: (1) PV tự dùng trực tiếp, (2) PV cứu khỏi cắt qua BESS, (3) arbitrage lưới, (4) demand giảm (nếu áp dụng), (5) trừ chi phí suy hao ước tính. Không cộng (2) và (3) hai lần.

### 3.15 Tính áp dụng ở Việt Nam

#### 3.15.1 Tóm tắt giá trị theo chiến lược (10/2026)

| Chiến lược | Tạo tiền hôm nay? | Lý do |
|---|---|---|
| Zero-export / export limit | Gián tiếp (tuân thủ; tránh phạt/cắt đấu nối) | Bắt buộc với đa số site không bán dư (Phát hiện #11) |
| PV → BESS thay vì cắt | **Có, lớn nhất** | PV dư lẽ ra mất → bán vào cao điểm 3.398 đ/kWh |
| TOU arbitrage lưới (thấp → cao điểm) | **Có** (T2–T7) | Chênh lệch ~2,8×; cần BESS và `c_deg` hợp lý |
| Self-consumption thuần (xả ngay khi tải > PV) | Kém hơn TOU-aware | Xả giờ bình thường lãng phí năng lượng có thể bán ở cao điểm |
| Import cap | Có (tránh đầu tư nâng MBA, tránh dừng sản xuất) | Giá trị vận hành, không theo biểu giá |
| Peak shaving demand charge | **Chỉ với khách thí điểm hai thành phần**, và phụ thuộc cơ sở tính (Pmax đo vs đăng ký) | Phát hiện #10 |
| Backup reserve | Có nếu tải nhạy cảm và PCS hỗ trợ off-grid | Giá trị phi biểu giá |
| EV DLM | Có khi EV làm vượt trần MBA | Biểu giá EV riêng, khung giờ EV có thể theo khung cũ (A §3.4.2, UNKNOWN) |
| DR | [UNKNOWN] | Chưa có bằng chứng cơ chế trả tiền cho C&I |
| Thị trường/VPP | Không (C&I BTM) | Khung giá BESS chỉ cho FTM ≥ 10 MW (A #7) |

#### 3.15.2 Giá trị của 1 kWh theo nguồn sạc (cấp 22–<110 kV, QĐ 1279, chưa VAT)

[INFERENCE] Giả định RTE = 0,9 (dồn vào η_d cho đơn giản), chưa trừ `c_deg`, xả hết trong cao điểm T2–T7:

| Nguồn sạc | Chi phí cơ hội của 1 kWh sạc | Giá trị khi xả (×0,9 × 3.398) | Lãi trên 1 kWh sạc | Lãi trên 1 kWh xả |
|---|---|---|---|---|
| PV dư lẽ ra bị cắt (zero-export) | 0 | 3.058 | **3.058** | 3.398 |
| Lưới thấp điểm (1.190) | 1.190 | 3.058 | 1.868 | **2.076** |
| PV lẽ ra bù tải giờ bình thường (1.833) | 1.833 | 3.058 | 1.225 | 1.361 |
| Lưới giờ bình thường (1.833) | 1.833 | 3.058 | 1.225 | 1.361 |
| Chủ nhật: lưới thấp điểm → bình thường | 1.190 | 0,9 × 1.833 = 1.650 | 460 | 511 |

- Kết luận cho luật tầng 2: thứ tự ưu tiên sạc = **PV sắp bị cắt > lưới thấp điểm > (PV bù tải ≈ lưới bình thường)**. Vì vậy luật "giữ chỗ trống cho PV dư" + "nạp lưới thấp điểm phần thiếu" (§3.4) là đúng hướng.
- Với `c_deg ≈ 556 đ/kWh` (giả định §3.5.3): mọi dòng trừ Chủ nhật vẫn dương; Chủ nhật âm → không chạy chu kỳ.
- Với BESS thời lượng 2 h và cao điểm 5 h: không thể phủ cả cao điểm ở công suất danh định. Bộ tối ưu nên **trải xả** để cắt phần tải cao điểm có giá trị như nhau (giá phẳng trong 17h30–22h30), ưu tiên bảo đảm import cap/demand trong khung. [INFERENCE] Khung giờ mới làm BESS thời lượng 4–5 h hấp dẫn hơn 2 h (chỉ một cửa sổ cao điểm/ngày), trong khi khung cũ có hai cửa sổ ngắn (9h30–11h30, 17h–20h) phù hợp 2 h × 2 chu kỳ. Đây là đầu vào cho tư vấn kích thước (sizing) của agent thị trường.

#### 3.15.3 Demand charge ở Việt Nam: hai kịch bản

| | Kịch bản A: thành phần công suất theo **Pmax đo 30 phút** (C #3) | Kịch bản B: theo **công suất đăng ký** (A §3.4.4) |
|---|---|---|
| Giá trị peak shaving thời gian thực | Trực tiếp: mỗi kW Pmax giảm = `c_dem` | Gián tiếp: cho phép **đăng ký thấp hơn**; vận hành phải đảm bảo không vượt mức đăng ký (phạt vượt: UNKNOWN) |
| Thuật toán | Cửa sổ 30 phút §3.3(d) + `Pk` trong MILP | Import cap cứng = mức đăng ký − margin; MILP dùng phạt vượt |
| Sản phẩm cần | Bộ đếm Pmax tháng, đồng bộ cửa sổ với công tơ EVN | Công cụ "đề xuất mức đăng ký tối ưu" từ dữ liệu lịch sử + kích thước BESS (what-if) |
| Rủi ro | Một lần thất bại (mất mạng, pin lỗi) làm mất lợi ích cả tháng → cần cảnh báo sớm và fallback native | Đăng ký thấp + BESS lỗi → vượt đăng ký |

[PROPOSAL] Hỗ trợ cả hai trong M-TAR (`demand_basis ∈ {MEASURED_MAX, CONTRACTED}`), mặc định chưa bật. Ưu tiên P1, kích hoạt khi khách tham gia thí điểm.

---

## 4. Hệ quả thiết kế cho sản phẩm

Mọi mục là [PROPOSAL]. ID FR tạm, tổng hợp sẽ chuẩn hóa.

| ID | Yêu cầu | Module | Ưu tiên | Căn cứ |
|---|---|---|---|---|
| FR-OPT-001 | Bốn tầng điều khiển tách rõ; tầng 2/3/4 chỉ xuất **envelope theo slot** (mode, SOC đích, p_grid_target, import/export cap, soc floor/ceiling); tầng 1 ở edge thực thi | M-OPT, M-INT | P0 | §3.2, §3.5.2 |
| FR-OPT-002 | Bộ phân xử ưu tiên một chỗ ở edge theo mô hình khoảng cho phép (L0–L9); L0–L3 không cấu hình được | M-OPT | P0 | §3.8; B PR-B03 |
| FR-OPT-003 | Vòng tầng 1: balancing về `p_grid_target` (PI, anti-windup, ramp), zero-export bằng cắt PV với hysteresis bất đối xứng, import cap, SOC guard; chu kỳ 1 s; `control_owner ∈ {NATIVE, EDGE}` | M-OPT, M-GRID | P0 | §3.3 |
| FR-OPT-004 | Bộ sinh lịch luật TOU VN (§3.4): giữ chỗ cho PV dư, nạp lưới thấp điểm phần thiếu, xả cao điểm, Chủ nhật không arbitrage; lịch 48 h, slot 15 phút; **không gọi là AI** | M-OPT, M-TAR | P0 | §3.4, §3.15 |
| FR-OPT-005 | Lịch mặc định ≥ 48 h lưu ở edge; hết lịch → chiến lược mặc định an toàn của site | M-OPT | P0 | Phát hiện #1 |
| FR-OPT-006 | DispatchPlan có vòng đời DRAFT→VALIDATED→APPROVED→SCHEDULED→EXECUTING→COMPLETED/ABORTED (+REJECTED/SUPERSEDED/EXPIRED), bất biến sau duyệt, input snapshot hash, auto-approve trong guardrail | M-OPT | P0 | §3.9 |
| FR-OPT-007 | `plan_slot_result` actual vs planned + `deviation_cause` + mã lý do | M-OPT, M-HIST | P0 | §3.10 |
| FR-OPT-008 | Giải thích theo slot bằng mã lý do + câu template; chi phí plan vs baseline | M-OPT, M-REP | P0 (slot), P1 (shadow price) | §3.11 |
| FR-OPT-009 | Optimization Service MILP/MPC (§3.5), horizon 48 h, Δt 15 phút, giải lại 15 phút + theo sự kiện; LP trước, MILP khi cần; fallback về lịch luật khi infeasible/timeout | M-OPT | P1 | §3.5, §3.6 |
| FR-OPT-010 | Tham số suy hao `c_deg` theo site, hiển thị trên UI; không tuyên bố "tối ưu tuổi thọ" | M-OPT, M-BESS | P1 | §3.5.3 |
| FR-OPT-011 | Backtest/what-if trên dữ liệu lịch sử với dự báo "như đã có"; nhãn "Mô phỏng"; cổng chất lượng trước khi bật tầng 3 cho site | M-OPT, M-ADV | P1 | §3.12 |
| FR-OPT-012 | Peak shaving cửa sổ 30 phút đồng bộ công tơ; `P_target = max(plan, Pmax tháng)`; hỗ trợ `demand_basis` đo/đăng ký | M-OPT, M-TAR | P1 | §3.3(d), §3.15.3 |
| FR-OPT-013 | Ngân sách xuất theo kỳ (50% sản lượng, NĐ 243) và cờ `allow_grid_charge`, `allow_ess_export` theo site | M-OPT, M-GRID | P1 | Phát hiện #12 |
| FR-EV-0xx | EV DLM: phân bổ theo dư POC, I_min, ưu tiên, kWh cần trước giờ đi; OCPP profiles có hạn; quirk theo hãng | M-EV | P1 | §3.3(f), Phát hiện #13 |
| FR-OPT-014 | Ước lượng và báo cáo năng lượng PV bị cắt do điều khiển, tách khỏi tổn hao kỹ thuật | M-PV, M-REP | P0 | §3.3(b); C §3.11 |
| FR-OPT-015 | Ánh xạ chiến lược → chế độ native của hãng (Huawei TOU/capacity control/feed-grid limit; Victron Mode 2; OpenEMS controller) khi native tồn tại; ma trận chế độ hợp lệ theo kịch bản | M-INT, M-OPT | P0 | §3.13 |
| FR-OPT-016 | P2 "VPP-capable": `FlexibilityOffer`, nguồn lệnh DR, API sự kiện; không bidding | M-OPT | P2 | §3.7 |
| NFR-PERF-0xx | Giải MILP 1 site ≤ 30 s (p95); 500 site trong ≤ 5 phút mỗi chu kỳ; kết quả deterministic theo version | M-OPT | P1 | §3.5.1 |
| NFR-REL-0xx | Zero-export: không có chu kỳ xuất > margin quá T giây; mục tiêu đáp ứng ≤ 2 s khi vòng của ta là owner | M-GRID | P0 | Phát hiện #2 |

**Khác hướng cũ (FusionSolar).** Hướng cũ là giám sát/O&M PV, đọc chế độ của hãng. Hướng EMS thêm **ghi** chiến lược và lập kế hoạch. Lý do: (1) khung cao điểm tối (QĐ 963) chuyển giá trị sang BESS, cần lập lịch; (2) zero-export phổ biến làm PV bị cắt, BESS cứu được giá trị đó; (3) mọi hãng đã có tầng 1, nên giá trị đa hãng của ta nằm ở tầng 2–3 và giải thích/M&V. Hướng edge kiểu OpenEMS và Java giữ nguyên; chỉ optimizer có thể là Python sidecar (§3.6, cần ADR).

---

## 5. Evidence ledger

| # | Claim | Source URL | Source type & date | Excerpt/paraphrase | Confidence | Conflicting evidence | Design implication |
|---|---|---|---|---|---|---|---|
| 1 | Schneider EMA: MPC cloud từ giá/lịch sử/thời tiết/lịch vận hành; lịch 15 phút/72 h; lịch mặc định 48 h khi mất server | https://www.se.com/us/en/product-range/65896/ ; https://download.schneider-electric.com/doc/998-20080341_US/EcoStruxure%20Microgrid%20Advisor%20Handout.pdf | Trang + handout hãng (~2017), qua kết quả tìm kiếm (từ A #21, B L14) | "Model Predictive Control algorithms… price signals, historic data, weather forecast and operating schedule" | Med–High | 48 h vs 72 h giữa tài liệu | FR-OPT-001, FR-OPT-005 |
| 2 | SmartLogger5000B: zero feed-in ≤ 2 s, peak shaving ≤ 5 s | https://www.photomate.eu/smartlogger5000b ; https://solar.huawei.com/admin/asset/v1/pro/view/bb9458d9373d4502912378db3cbc7f2d.pdf | Nhà phân phối + datasheet Huawei, qua kết quả tìm kiếm (E F-28) | "closed-loop control for zero feed-in within 2s" | Med | Mirror nhà phân phối | Tầng 1 ở edge; NFR-REL zero-export |
| 3 | Độ trễ zero-export = chu kỳ đo + truyền + phản ứng inverter + giảm công suất | https://help.autarco.com/en/hardware/why-am-i-still-exporting-while-i-have-set-my-pv-system-to-zero-export- | Help vendor, qua kết quả tìm kiếm (E F-28) | Phân rã độ trễ | Med | — | Margin zero-export §3.3(a) |
| 4 | Huawei app ESS modes: Maximum self-consumption, Fully fed to grid, TOU; NBI `ch_discharge_model` 0–4 | https://e-solarshop.ro/wp-content/uploads/2025/07/fusionsolar-app-manual5925.pdf ; https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/imaster-neteco-v600r022c00-northbound-interface-reference-v6.pdf | App manual 2024 + NBI V6 (nghiên cứu FusionSolar) | Table 6-1; enum 0 none…4 automatic | High | — | FR-OPT-015 ánh xạ chế độ |
| 5 | Thư viện `huawei_solar`: set_tou_periods, set_capacity_control_periods, set_maximum_feed_grid_power, set_zero_power_grid_connection, forcible_charge/discharge | https://github.com/wlcrs/huawei_solar/blob/main/services.yaml ; https://github.com/wlcrs/huawei_solar/blob/main/const.py#L20-L44 | Mã nguồn cộng đồng (nghiên cứu FusionSolar) | Danh sách dịch vụ ghi | Med–High | Không phải tài liệu Huawei | Driver Huawei: peak shaving theo khung qua "capacity control" |
| 6 | Huawei C&I: peak shaving chỉ trong kịch bản on/off-grid (PQ/VSG) theo một manual | https://ske-solar.com/fileadmin/user_upload/UserManual_LUNA2000-_107-215__C_I-Microgrid-SmartLogger3000_V07_2025-11-30_EN.pdf | Bản sao manual 2025, qua kết quả tìm kiếm (B #17) | như claim | Med | Mirror | Ma trận chế độ hợp lệ (FR-OPT-015) |
| 7 | EMMA dự báo dư PV và giữ SOC space reserve | https://solar.huawei.com/en/products/EMMA | Trang hãng (B L38) | "forecasts your surplus PV power and executes… ESS SOC space reserve" | High | Nhắm hộ gia đình/thương mại nhỏ | `SOC_ceiling` có space reserve §3.3(e) |
| 8 | EMMA panel: so sánh có/không EMMA, dự báo 24 h, phân tích tiết kiệm; tắt thì không bật lại trong tháng | https://support.huawei.com/enterprise/en/doc/EDOC1100376808/a3411c60/enabling-emma | Tài liệu SmartPVMS 24.5.0 (nghiên cứu FusionSolar) | như claim | High | — | Explainability "có/không tối ưu" §3.11 |
| 9 | Huawei cloud VPP API `chargeAndDischarge` (SOC đích/thời lượng, ≤100 plant, 100/phút, async, timeout 24 h) | https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/imaster-neteco-v600r022c00-northbound-interface-reference-v6.pdf (NBI; chi tiết ở `fusionsolar/.../source_code_clients_2.md`) | Tài liệu NBI (nghiên cứu FusionSolar) | "do not invoke… repeatedly before a task is complete" | Med–High | Phiên bản NBI khác nhau | Tầng 4 qua cloud; không dùng cho tầng 1 |
| 10 | Ampowr: peak shaving trần 95 kW; local backup khi mất mạng | https://ampowr.com/hoge-duin-hotel-enhances-energy-efficiency-with-ampifarm-peak-shaving/ | Case study hãng, qua kết quả tìm kiếm (B L04) | "will continue to perform strategies and collect data through a local backup feature" | Med | — | FR-OPT-005 |
| 11 | Ampowr: chiến lược net-zero, curtailment, peak shaving khi chạm giới hạn lưới, generator steering | https://ampowr.com/energy-management-system-ems/peak-shaving/ ; https://ampowr.com/battery-energy-storage-systems/battery-energy-storage-system-generator-steering/ | Trang hãng (B L06) | "Switch to energy from battery when grid limit is reached" | Med | — | Danh mục §3.1 |
| 12 | Ampowr: DA + imbalance + aFRR bid cùng nhau | https://ampowr.com/case-study-gebroeders-van-pinxteren/ | Case study hãng (B L03) | "Day-Ahead, imbalance, and aFRR are bid together" | Med | Chỉ Hà Lan | Tầng 4 = P2 |
| 13 | InfinitePower: EMS tủ BESS có lập lịch, peak shaving, time-shift, backup, SOC; EMS điều phối BMS/PCS | https://www.infinitepowerht.com/what-is-energy-management-system-ems-and-its-functions.html ; https://www.infinitepowerht.com/125kw-261kwh-commercial-energy-storage-system.html | Trang vendor (nguồn hạt giống), qua kết quả tìm kiếm (A #12, B #19) | "automated scheduling, peak shaving, SOC tracking" | Med | Không có register map | Supervisory trên EMS tủ |
| 14 | SolarEdge ONE for C&I: tối ưu theo biểu giá + dự báo thời tiết, peak shaving nâng cao, thị trường, EV | https://www.solaredge.com/us/solaredge-one-for-commercial-and-industrial-energy-optimization-platform ; https://www.businesswire.com/news/home/20241203224482/en | Trang hãng + PR 12/2024 (B L30) | "utility rates and weather forecasts" | High | Không mô tả thuật toán | Tầng 3 là chuẩn cạnh tranh |
| 15 | SolarEdge export limitation cần công tơ tại điểm đấu nối; công tơ tiêu thụ không hỗ trợ | https://knowledge-center.solaredge.com/sites/kc/files/feed-in_limitation_application_note.pdf | App note v3.0 8/2026 (B L35) | "Consumption meters are not supported in export limitation use cases" | High | — | `pcc_meter_id` bắt buộc cho zero-export |
| 16 | OpenEMS: PeakShaving, Balancing `targetGridSetpoint`, ToU 15 phút, GridOptimizedCharge, OCPP server; điều khiển qua Power Solver | https://openems.github.io/openems.io/openems/latest/edge/architecture.html ; https://github.com/OpenEMS/openems/tree/develop/io.openems.edge.controller.ess.balancing ; https://zenodo.org/records/17481747 ; https://zenodo.org/records/19374309 ; https://community.openems.io/t/ess-that-can-talk-with-openems-using-modbus-tcp/1029 | Docs + repo + release notes + forum (B L43, L44) | "balanced to 0 Watt… targetGridSetpoint"; "switch to QUARTER_HOURLY prices" | High/Med | Tên controller khác chưa kiểm chứng | FR-OPT-002 (arbiter), envelope `p_grid_target` |
| 17 | Victron ESS Mode 2: `/AcPowerSetpoint` reg 2700; Mode 3 giao vòng điều khiển ra ngoài; fallback khi mất master chưa rõ | https://communityarchive.victronenergy.com/questions/95889/multipluss-ii-is-external-control-ess-mode-2-or-3%EF%B9%96childToView=102991.html | Cộng đồng, qua kết quả tìm kiếm (E F-30) | như claim | Low–Med | — | Ưu tiên grid-setpoint; watchdog bắt buộc |
| 18 | Siemens SICAM MGC: peak shaving, reserve monitoring, quản lý SOC, dự báo, DR, thị trường | https://assets.new.siemens.com/siemens/assets/api/uuid:4b32eeee-ee7c-423e-94f1-ae6a4257a689/MicrogridControlBrochure.pdf | Brochure hãng (B L21) | "algorithms fulfill IEC 62898-2" | Med–High | Edition UNKNOWN | Reserve là lớp riêng (L4) |
| 19 | Stem Athena "lên tới 30%" tiết kiệm | https://www.stem.com/wp-content/uploads/2021/05/Stem-Solutions-Overview_Athena_May-2021_v10.pdf | Tài liệu hãng 2021 (A #39) | như claim | Low | Không kiểm chứng độc lập | Không quảng cáo %; dùng M&V |
| 20 | GridBeyond: tối ưu tôn trọng ràng buộc tài sản và mô hình suy hao | https://secure.businesswire.com/news/home/20250930978130/en/GridBeyond-Launches-ViewPoint-Lens-to-Empower-Energy-Customers-With-Greater-Visibility-and-Control | PR 9/2025 (B L49) | "respects asset-level constraints and degradation models" | Med | — | `c_deg` trong mục tiêu |
| 21 | QĐ 963/QĐ-BCT: cao điểm 17h30–22h30 T2–T7, thấp điểm 0h–6h, CN không cao điểm | https://thuvienphapluat.vn/van-ban/Tai-nguyen-Moi-truong/Quyet-dinh-963-QD-BCT-2026-khung-gio-cao-diem-thap-diem-cua-he-thong-dien-quoc-gia-703327.aspx ; https://tuoitre.vn/bo-cong-thuong-chinh-thuc-thay-doi-khung-gio-tinh-gia-dien-buoi-toi-la-gio-cao-diem-2026042410430101.htm | Văn bản + báo 4/2026, qua kết quả tìm kiếm (A #4) | như claim | High | Ngày áp hóa đơn chưa chắc | Luật TOU §3.4; tariff có version |
| 22 | QĐ 1279: giá SX 22–<110 kV 1.190/1.833/3.398 đ/kWh; tỷ lệ ~2,8× | (A §3.4.3: thuvienphapluat, qua kết quả tìm kiếm; URL cụ thể trong A ledger) | Văn bản 5/2025 | Bảng giá | Med–High | Có thể điều chỉnh 2026 (NĐ 278) | Bảng §3.15.2 |
| 23 | Giá hai thành phần thí điểm ≥ 200.000 kWh/tháng; song song 01–06/2026; thật 07/2026–07/2027 | https://tapchicongthuong.vn/thi-diem-ap-dung-gia-dien-hai-thanh-phan-tu-1-1-2026-218800.htm ; https://vnexpress.net/de-xuat-thi-diem-gia-dien-hai-thanh-phan-tu-2026-4936558.html | Báo 2025, qua kết quả tìm kiếm (A #6, C #7) | như claim | Med | Mốc 10/2025 vs 1/2026 | FR-OPT-012 P1 |
| 24 | Pmax = công suất trung bình lớn nhất trong chu kỳ tích phân 30 phút | https://daibieunhandan.vn/trien-khai-thu-nghiem-gia-ban-le-dien-hai-thanh-phan-tu-thang-10-2025-10390577.html ; https://tapchicongthuong.vn/evn-xay-dung-he-thong-gia-ban-dien-hai-thanh-phan-264219.htm | Báo 2025, qua kết quả tìm kiếm (C #3) | "khoảng thời gian tích phân hiện nay đang là 30 phút" | Med–High | A: thành phần công suất theo **công suất đăng ký** | `demand_basis` hai kịch bản §3.15.3 |
| 25 | Chỉ ~287/28.254 hệ TSXTTT đăng ký bán dư | https://vietnamnet.vn/en/rooftop-solar-saves-billions-of-dong-but-one-bottleneck-remains-2552186.html | Báo 2026, qua kết quả tìm kiếm (A #3) | như claim | Med | — | Zero-export + PV→BESS là chiến lược chính |
| 26 | NĐ 243: trần bán dư 50% sản lượng thực phát; điện BESS xả tính vào điện dư | https://www.reccessary.com/en/news/vietnam-solar-grid-export-dppa | Báo ngành 2026, qua kết quả tìm kiếm (A #1, #2) | như claim | Med | Cơ sở 20%/50% từng khác nhau giữa nguồn | FR-OPT-013 |
| 27 | Trung áp không bán dư phải có thiết bị bật tắt phát ngược; điều độ qua Modbus TCP/IEC 104 | https://www.advantech.com/vi-vn/resources/industry-focus/quyet-dinh-1570qd-evn-dien-mat-troi-mai-nha-dieu-can-biet | Tóm tắt vendor, qua kết quả tìm kiếm (E F-17) | như claim | Med | Chưa đọc QĐ 1570 | L2 trong arbiter; `SET_REVERSE_FEED_BLOCK` |
| 28 | OCPP 1.6: 3 loại profile, stackLevel, min; quirk Easee | https://www.bender.de/docs/charge-controller/OCPP/ocpp-smart-charging/ ; https://developer.easee.com/docs/ocpp-smart-charging | Docs hãng, qua kết quả tìm kiếm (E F-21) | như claim | High | — | EV DLM §3.3(f) |
| 29 | Trạm sạc EV có biểu giá + công tơ riêng | https://vneconomy.vn/automotive/quy-dinh-moi-ve-gia-ban-dien-cho-tram-sac-xe-dien.htm | Báo 2025, qua kết quả tìm kiếm (A #10) | như claim | Med | Khung giờ EV có thể theo khung cũ | Nhiều tariff trong site (MILP mở rộng) |
| 30 | OpenADR 3.0 REST/JSON, webhook; 3.1 thêm MQTT | https://www.openadr.org/assets/OpenADR%20Webinar%20Nov%202023%20-%20From%202.0%20to%203.0.pdf | Tài liệu OpenADR Alliance (E F-22) | như claim | Med–High | Không có bằng chứng dùng ở VN | Hook DR P2 |
| 31 | SOC LFP khó ước lượng, có thể trôi/nhảy | https://www.accure.net/blogs/state-of-charge-soc-estimation-errors-for-lfp-batteries-can-exceed-15 | Blog vendor, qua kết quả tìm kiếm (C #8) | lỗi có thể >15% | Med | Con số của vendor | SOC guard dùng giới hạn BMS; replan khi SOC nhảy |
| 32 | Huawei SmartEMO C&I hỗ trợ demand charge theo khung TOU (release 31/03/2026) | (Release notes web portal FusionSolar, đọc trực tiếp trong demo trước: `fusionsolar/04_ghi_chu_nghien_cuu/2_phan_ra_san_pham/demo_observations.md` §7) | Quan sát trực tiếp, 2026 | như claim | Med | Không có URL công khai | Đối thủ ở VN đã chuẩn bị cho hai thành phần |
| 33 | Solver: HiGHS (MIT), CBC (EPL-2.0), OR-Tools (Apache-2.0, binding Java), Timefold (Apache-2.0), Gurobi/CPLEX thương mại | Không có URL trong phiên (hết hạn mức tìm kiếm) | Kiến thức nền | — | Low (chưa kiểm chứng) | — | ADR-OPT cần kiểm chứng license trước khi chốt |
| 34 | Tên controller OpenEMS `ess.limittotaldischarge`, `ess.emergencycapacityreserve`, `ess.timeofusetariff` | Không có URL trong phiên | Kiến thức nền | — | Low (UNKNOWN) | — | Kiểm chứng trong repo trước khi trích (Q-G01) |

---

## 6. Câu hỏi mở / UNKNOWN

| ID | Câu hỏi | Ảnh hưởng | Cách xác minh |
|---|---|---|---|
| Q-G01 | Tên chính xác và tham số của các controller OpenEMS: LimitTotalDischarge, EmergencyCapacityReserve, TimeOfUseTariff, GridOptimizedCharge, EVCS | Ánh xạ chiến lược khi dùng OpenEMS làm edge; tham chiếu thiết kế | Đọc `io.openems.edge.controller.*` trong https://github.com/OpenEMS/openems (lượt sau, khi có hạn mức tìm kiếm/clone) |
| Q-G02 | Chế độ ESS của Victron ("Optimized with/without BatteryLife", "Keep batteries charged", Dynamic ESS) và hành vi watchdog Mode 2/3 | Driver Victron, fallback | Tài liệu Victron ESS manual |
| Q-G03 | Huawei C&I (SmartLogger/LUNA2000-215) có chế độ TOU + capacity control cùng lúc không; thứ tự ưu tiên native | Tránh hai lớp điều khiển đánh nhau | Manual SmartLogger/LUNA C&I, test thực địa |
| Q-G04 | License và binding Java hiện tại của HiGHS, CBC, SCIP qua OR-Tools; OR-Tools có backend HiGHS chưa | ADR-OPT | Kiểm chứng tài liệu chính thức |
| Q-G05 | Thời gian giải thực tế MILP §3.5 với dữ liệu site thật (96/192 bước, 0–20 phiên EV) | NFR-PERF | Benchmark nội bộ (P1) |
| Q-G06 | Thành phần công suất giá hai thành phần tính theo Pmax đo hay công suất đăng ký; có phạt vượt đăng ký không; cửa sổ block hay rolling; áp mọi giờ hay theo khung | Thuật toán peak shaving, giá trị BESS | Văn bản thí điểm BCT/EVN; hóa đơn song song của khách thí điểm |
| Q-G07 | Ngày khung giờ QĐ 963 áp vào hóa đơn sản xuất và EV | Lịch TOU đúng | Hóa đơn thực, Điện lực (A Q-A01) |
| Q-G08 | Việt Nam có chương trình DR có trả tiền/ưu đãi cho C&I không (EVN từng có chương trình điều chỉnh phụ tải tự nguyện — **chưa có nguồn trong phiên này**) | Ưu tiên tầng 4/DR | Tìm văn bản EVN/BCT về DR |
| Q-G09 | Có được sạc BESS từ lưới rồi xả ra lưới và tính là "điện dư" không (NĐ 243) | Cờ `allow_ess_export`, `allow_grid_charge` | Văn bản hướng dẫn (C §3, UNKNOWN đã nêu) |
| Q-G10 | Đơn giá BESS C&I ở VN và cycle life thực tế để đặt `c_deg` mặc định | Quyết định arbitrage, Chủ nhật | Báo giá nhà cung cấp, datasheet cell |
| Q-G11 | Chu kỳ cập nhật OCPP tối thiểu mà các bộ sạc phổ biến ở VN chấp nhận | EV DLM | Test thiết bị |
| Q-G12 | Bằng chứng tiết kiệm độc lập cho BESS C&I dưới biểu giá TOU (VN hoặc tương tự) | Định vị, ROI | Nghiên cứu học thuật/NREL khi có hạn mức tìm kiếm |

---

## 7. Vấn đề gửi agent khác

| ID | Gửi | Vấn đề | Đề xuất |
|---|---|---|---|
| X-G01 | A (Thị trường) + C (Domain) | Mâu thuẫn cơ sở tính thành phần công suất: A §3.4.4 "công suất đăng ký, trả cả khi không dùng"; C Phát hiện #3 "Pmax đo 30 phút" | Thống nhất một mô tả; nếu chưa rõ, mô hình `demand_basis ∈ {MEASURED_MAX, CONTRACTED}` và ghi UNKNOWN (§3.15.3) |
| X-G02 | E (Tích hợp) | Hợp đồng lệnh §3.19 cần: (1) mode `GRID_SETPOINT` và `PV_SURPLUS_CHARGE`, `GRID_CHARGE_TO_TARGET`, `PEAK_DISCHARGE`, `HOLD`; (2) trong `APPLY_SCHEDULE`, slot mang envelope `{mode, soc_target_end, p_grid_target, p_import_cap, p_export_cap, soc_floor, soc_ceiling}`; (3) ack theo slot (`SLOT_STARTED/APPLIED/OVERRIDDEN/ENDED`); (4) cờ `control_owner` theo chức năng | Bổ sung vào canonical command contract |
| X-G03 | Kiến trúc (06) | Optimization Service tách riêng; chọn Java+OR-Tools hay Python sidecar (đề xuất Python cho P1); kết quả deterministic, pin version solver | Mở ADR-OPT |
| X-G04 | M-TAR / C | Tariff cần: phiên bản theo ngày hiệu lực, nhiều tariff trong một site (EV), `demand_window_min/type`, `demand_basis`, giá bán dư, ngân sách xuất theo kỳ (50%), lịch ngày lễ (không cao điểm?) | Thêm trường vào domain model |
| X-G05 | UX (09) | Màn "Kế hoạch điều độ": timeline 48 h (giá TOU, SOC kế hoạch vs thực tế, nhập/xuất), mã lý do theo slot, nút duyệt/hủy, so sánh baseline; nhãn "Mô phỏng" cho what-if | Thiết kế UI-xx |
| X-G06 | Bảo mật (10) | Quyền duyệt plan vượt guardrail (2 người cho site lớn); audit chuyển trạng thái; lệnh tay luôn có hạn; L0–L3 không cấu hình được qua UI/API | Thêm vào RBAC và NFR-SEC |
| X-G07 | Roadmap (11) | MVP: tầng 1 + tầng 2 luật TOU + actual vs planned + mã lý do. P1: MILP/MPC, backtest, peak shaving hai thành phần, EV DLM. P2: VPP-capable/DR | Đồng bộ với A D-06, B PR-B06/B11/B14 |
| X-G08 | A (sizing) | Khung cao điểm 5 h làm BESS 4–5 h hấp dẫn hơn 2 h (§3.15.2) | Đưa vào what-if/tư vấn kích thước |
| X-G09 | Dự báo (M-ADV) | Giao diện cần: dự báo PV/tải 48 h, slot 15 phút, kèm phiên bản và độ bất định (ít nhất sai số lịch sử theo giờ); dự báo "như đã có" lưu lại để backtest | Đặc tả API dự báo |
| X-G10 | Orchestrator | Hạn mức WebSearch đã hết trước khi Agent G chạy; Q-G01, Q-G02, Q-G04, Q-G08, Q-G12 cần một lượt tìm kiếm bổ sung | Chạy lượt kiểm chứng sau |
