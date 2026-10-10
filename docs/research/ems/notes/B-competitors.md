# B — Phân tích sản phẩm đối thủ EMS (Agent B)

[← Mục lục](../index.html) · [02 Thị trường](../02-market-and-competitor-analysis.html) · [03 Chức năng](../03-functional-catalog.html) · [08 Tối ưu](../08-energy-optimization.md) · [14 Nguồn](../14-source-register.md) · [15 Mô phỏng](../15-simulators-and-messaging.md)

- Người viết: Agent B (Competitor Product Analysis). Ngày: 2026-10-10. Trạng thái: ghi chú nghiên cứu, bản 1.
- Phương pháp bằng chứng: môi trường **chặn tải trang trực tiếp** (WebFetch/curl). Toàn bộ bằng chứng mới lấy qua công cụ WebSearch. Mọi FACT mới trong file này là **"(qua kết quả tìm kiếm)"**, tức là nội dung tóm tắt/snippet do công cụ tìm kiếm trả về cho URL đó, không phải đọc toàn văn datasheet. Bằng chứng về Huawei/Sungrow/SolarEdge API lấy lại từ nghiên cứu FusionSolar trước (`docs/research/fusionsolar/04_ghi_chu_nghien_cuu/`) và được ghi rõ.
- Quy ước trạng thái trong ma trận: **V** = Verified (tài liệu của hãng nói rõ, có URL trong ledger), **P** = Partial (có nói nhưng thiếu chi tiết / chỉ ở sản phẩm anh em / chỉ qua nhà phân phối), **U** = Unknown (không tìm thấy tài liệu; *không có nghĩa là không hỗ trợ*), **NA** = Not applicable. "Verified" ở đây nghĩa là *hãng tuyên bố trong tài liệu*, **không** phải đã kiểm thử độc lập.

---

## 1. Phạm vi & câu hỏi nghiên cứu

### 1.1 Câu hỏi
- Q-B1. Các EMS thương mại cho C&I đa site (PV + BESS + lưới + tải + EV tùy chọn) thực sự làm được gì theo tài liệu công khai, ở 13 nhóm chức năng A–M?
- Q-B2. Kiến trúc triển khai phổ biến là gì (cloud-only, edge controller + cloud, on-prem SCADA)? Hành vi khi mất kết nối?
- Q-B3. Giao thức/tích hợp và mức mở API?
- Q-B4. Bảo mật/tuân thủ được tuyên bố (ISO 27001, IEC 62443, NIS2…)?
- Q-B5. Khoảng trống nào sản phẩm của chúng ta (installer/O&M C&I Việt Nam, đa hãng, edge-first) có thể chiếm?

### 1.2 Giả định ánh xạ nhóm A–M
File `_conventions.md` chỉ cho mã module, không cho tên nhóm. Ma trận dùng ánh xạ sau (cần Agent tổng hợp xác nhận, xem mục 7):

| Nhóm | Module | Nội dung dùng trong ma trận |
|---|---|---|
| A | M-ORG | Tổ chức/tenant, đa site (fleet), vai trò người dùng |
| B | M-DASH | Dashboard danh mục/site, KPI |
| C | M-MON | Giám sát thời gian thực (độ phân giải dữ liệu) |
| D | M-HIST | Lịch sử, phân tích, báo cáo |
| E | M-BESS | Quản lý BESS (SOC/SOH, chế độ, giới hạn) |
| F | M-PV | PV: chẩn đoán string/module, giới hạn phát |
| G | M-GRID | Điểm đấu nối (PCC), peak shaving, demand charge, biểu giá |
| H | M-EV | Sạc EV |
| I | M-OPT | Tối ưu hóa/lập lịch, tham gia thị trường/DR |
| J | M-ALM | Cảnh báo & bảo trì |
| K | M-INT | Giao thức, tích hợp bên thứ ba, API |
| L | M-SEC | Bảo mật & tuân thủ |
| M | M-ADV | Nâng cao: dự báo, AI, microgrid/islanding |

Thêm 3 hàng phụ: vận hành edge khi mất mạng, điều khiển máy phát (genset/CHP), mô hình triển khai.

### 1.3 Sản phẩm được chọn và lý do

| # | Sản phẩm (tên đã kiểm chứng) | Loại | Lý do chọn |
|---|---|---|---|
| P1 | **Ampowr Cosmos** (EMS) + AmpiHealth | Bắt buộc | Nguồn gốc của người dùng; EMS gắn BESS C&I châu Âu |
| P2 | **HT Infinite Power** (Shenzhen Infinite Power Technology) — EMS tích hợp trong tủ/container BESS | Bắt buộc | Nguồn gốc của người dùng; đại diện nhà tích hợp BESS Trung Quốc, giống nhiều hàng sẽ gặp ở VN |
| P3 | **Schneider EcoStruxure Microgrid Advisor (EMA)** + Microgrid Operation (EMO) + Power Monitoring Expert (PME) | Bắt buộc | EMA là EMS cloud + edge cho DER phía tải, kiến trúc gần nhất với hướng của ta |
| P4 | **Siemens SICAM Microgrid Control (MGC)** (+ Spectrum Power MGMS, Electrification X) | Bắt buộc | Chuẩn tham chiếu cho microgrid controller on-prem |
| P5 | **ABB Ability OPTIMAX** (+ e-mesh, nay nằm ở Hitachi Energy; ABB Ability Energy and Asset Manager) | Bắt buộc | Tối ưu hóa công nghiệp; kiểm tra lại tên |
| P6 | **SolarEdge ONE for C&I** + ONE Controller (CLC1) | Bắt buộc | Nền tảng OEM cho C&I PV+BESS+EV, tài liệu kỹ thuật công khai tốt |
| P7 | **Huawei FusionSolar SmartPVMS (C&I)** + SmartLogger5000B / EMMA | Chọn | Đã nghiên cứu sâu; phổ biến ở VN |
| P8 | **Sungrow PowerStack 255CS + iSolarCloud** | Chọn | OEM PV+BESS C&I phổ biến ở VN/APAC; có tích hợp EMS bên thứ ba qua Modbus TCP |
| P9 | **OpenEMS** (mã nguồn mở, FENECON/OpenEMS Association) | Chọn | Hướng edge cũ dự kiến "kiểu OpenEMS"; tham chiếu kiến trúc Edge/Backend |
| P10 | **Stem PowerTrack EMS / Athena** (gồm AlsoEnergy PowerTrack) | Chọn | Đa hãng, đa site, edge-to-cloud, PV monitoring + BESS control — rất gần mô hình kinh doanh của ta |
| P11 | **GridBeyond Point** | Chọn (phụ) | Đại diện mô hình "C&I flexibility/aggregator": tối ưu BESS + DR + thị trường |

**Loại trừ (có lý do):**
- Siemens **Gridscale X**: SaaS cho vận hành lưới điện của utility (DSO/TSO), không phải EMS phía C&I [FACT] https://www.siemens.com/en-us/products/gridscale-x/ (qua kết quả tìm kiếm).
- **Wärtsilä GEMS** (Fleet Director + Power Plant Controller): bằng chứng chỉ ở quy mô utility (Duke Energy) và nhà máy đảo; không thấy C&I sau công tơ. Giữ làm tham chiếu IEC 62443 cho PPC [FACT] https://www.wartsila.com/media/news/31-08-2020-wartsila-s-gems-to-centrally-manage-multi-state-energy-storage-projects-for-duke-energy-2771911 ; https://www.carilec.org/file/flipbook/9/files/basic-html/page21.html (qua kết quả tìm kiếm).
- **Fluence Mosaic/Nispera, Tesla Autobidder/Powerhub**: tập trung đấu thầu thị trường bán buôn utility; không tìm bằng chứng trong phiên này → không đánh giá (không suy ra gì).
- **Enphase, Victron VRM**: chủ yếu dân dụng / off-grid nhỏ. Victron VRM có thể liên quan VN cho site nhỏ — chưa tìm hiểu (Q-B12).
- **Envision EnOS, PowerSecure**: nền tảng IoT tổng quát / dịch vụ utility Mỹ; không đủ thời gian và bằng chứng.
- **rfp.wiki**: các hồ sơ vendor ở đây do AI sinh, tự ghi độ tin cậy ~30% → chỉ dùng làm gợi ý, **không** dùng làm bằng chứng Verified [FACT] https://www.rfp.wiki/vendors/ampowr (qua kết quả tìm kiếm).

---

## 2. Phát hiện chính

1. [FACT] Mô hình kiến trúc thống trị là **cloud lập kế hoạch + edge controller thực thi**. Schneider EMA: cloud chạy Model Predictive Control (MPC) từ tín hiệu giá, lịch sử, dự báo thời tiết, lịch vận hành; edge controller giao tiếp DER tại site; có **lịch mặc định 48 giờ** để chạy tiếp khi mất liên lạc server. https://www.se.com/us/en/product-range/65896/ ; https://marketplace.microsoft.com/en-us/product/saas/869296.microgrid_advisor?tab=overview (qua kết quả tìm kiếm)
2. [FACT] Ampowr Cosmos tuyên bố có "local backup feature": mất kết nối thì EMS **vẫn chạy chiến lược và thu dữ liệu** tại chỗ. https://ampowr.com/hoge-duin-hotel-enhances-energy-efficiency-with-ampifarm-peak-shaving/ (qua kết quả tìm kiếm)
3. [INFERENCE] Từ (1)(2) + OpenEMS Edge + Stem PPC + Huawei SmartLogger: mọi EMS nghiêm túc đều giữ **vòng điều khiển nhanh ở edge**, cloud chỉ gửi kế hoạch/setpoint. Điều này khớp hướng edge-first đã chọn trong nghiên cứu FusionSolar; không cần đổi hướng.
4. [FACT] Vòng điều khiển nhanh tại site có số liệu cụ thể ở Huawei SmartLogger5000B: zero-export khép kín **≤ 2 s**, peak shaving/giới hạn công suất **≤ 5 s** (datasheet qua nhà phân phối). https://www.photomate.eu/smartlogger5000b (qua kết quả tìm kiếm)
5. [FACT] Peak shaving / giới hạn công suất mua lưới là chức năng chung của **mọi** sản phẩm được xét (Ampowr, InfinitePower, Schneider, Siemens, SolarEdge, Huawei, Sungrow, OpenEMS). Đây là **table stakes**, không phải điểm khác biệt. (URL trong ledger L04, L11, L13, L14, L21, L30, L37, L41, L43.)
6. [FACT] Các điểm khác biệt thật nằm ở: (a) tham gia thị trường/DR (Ampowr bid đồng thời Day-Ahead + imbalance + aFRR, https://ampowr.com/case-study-gebroeders-van-pinxteren/; GridBeyond; Stem "value stacking"), (b) chẩn đoán PV sâu (SolarEdge module-level + digital twin; Huawei I-V), (c) quản lý EV quy mô lớn (SolarEdge/Wevo; Siemens Electrification X Load Management), (d) chức năng microgrid/islanding (Siemens MGC, Schneider EMO, Sungrow VSG/black start, Huawei on/off-grid).
7. [INFERENCE] Ở thị trường VN hiện chưa có thị trường cân bằng/aFRR cho C&I (cần Agent thị trường xác nhận — mục 7), nên (a) ít giá trị ngắn hạn; (b)(c) và peak shaving + TOU + zero-export mới là giá trị chính.
8. [FACT] SolarEdge ONE Controller C&I (CLC1) có phần cứng công khai: 2× RS485 cách ly (Modbus RTU), 1× CAN, 2× RJ45 (Modbus TCP), Wi‑Fi 802.11ax, BLE 5.3, 4 DI / 4 DO 24 V; Modbus TCP bật qua SolarEdge Go, **cổng 1502**, có bảng register. https://knowledge-center.solaredge.com/sites/kc/files/se-one-controller-commercial-and-industrial-datasheet-eng.pdf ; https://knowledge-center.solaredge.com/sites/kc/files/se-one-controller-for-cni-user-guide-im.pdf (qua kết quả tìm kiếm). Đây là "bill of interfaces" tham chiếu tốt cho gateway edge của ta.
9. [FACT] SolarEdge ONE for C&I có phân quyền theo site: Site Admin quản lý User Role, Monitoring Access, cấp quyền bên thứ ba, Public Access, Kiosk View, API Access, quyền xem biểu đồ PR, và tick "Expose to alerts notifications" theo từng user. https://knowledge-center.solaredge.com/sites/kc/files/se-site-admin-in-solaredge-one-for-c&i-user-guide.pdf (qua kết quả tìm kiếm)
10. [FACT] SolarEdge: tính năng lõi ONE for C&I **miễn phí** cho người mua phần cứng SolarEdge; gói phần mềm trả phí đưa ra dần. https://knowledge-center.solaredge.com/sites/kc/files/se-one-for-c&i-overview.pdf (qua kết quả tìm kiếm). [INFERENCE] OEM tiếp tục dùng phần mềm để bán phần cứng → sản phẩm đa hãng phải bán giá trị *đa hãng + O&M*, không cạnh tranh giá với dashboard OEM.
11. [FACT] Siemens SICAM MGC: phát hiện mất điện (blackout detection), black start, giám sát dự phòng (reserve monitoring), peak shaving, tự động chuyển chế độ lưới; thuật toán đáp ứng **IEC 62898-2**; dự báo tải/tái tạo theo lịch sử + thời tiết; quản lý SOC (giữ năng lượng tối thiểu, lịch sạc/xả); quy mô tới ~2 GW; tuyên bố chứng nhận IEC 62443, IPSec, chip mã hóa. https://assets.new.siemens.com/siemens/assets/api/uuid:4b32eeee-ee7c-423e-94f1-ae6a4257a689/MicrogridControlBrochure.pdf ; https://www.siemens.com/en-us/products/microgrids/sicam-microgrid-control/ (qua kết quả tìm kiếm)
12. [FACT] Bảo mật được tuyên bố rất khác nhau: Ampowr (ISO 27001, NIS2, host EU, pen-test bên thứ ba — tự tuyên bố); Siemens MGC (IEC 62443); Schneider (chương trình IEC 62443 cho EcoStruxure Power, kiến trúc chứng nhận 62443-3-3 — phạm vi với EMA chưa rõ); Wärtsilä PPC (IEC 62443). Huawei FusionSolar: nghiên cứu trước **không tìm thấy** chứng chỉ ISO 27001/IEC 62443 cho cloud. https://ampowr.com/nis2-compliance/ ; https://www.productinfo.schneider-electric.com/esxp_digital_apps_iec/transverse/English/BM_ESXP_DG_Transverse_Section_IEC_0001148082.xml/$/ESXP_DG_SYSD_Cyber_ISA_IEC_0001157270 (qua kết quả tìm kiếm)
13. [FACT] Một chứng chỉ IEC 62443-4-1/4-2 công khai của WinCC OA (nền HMI họ Siemens) ghi hiệu lực đến **2026-02-06**; chưa thấy gia hạn. https://www.winccoa.com/documentation/WinCCOA/3.20/en_US/iec_62443/topics/iec_62443_certification.html (qua kết quả tìm kiếm). [INFERENCE] Tuyên bố "certified" phải kèm số chứng chỉ, phạm vi, ngày hết hạn — áp dụng cho cả ta.
14. [FACT] OpenEMS: Edge (on-site, giao tiếp thiết bị, chạy thuật toán), Backend (cloud, gom nhiều Edge), UI (trình duyệt/di động). Controller `Controller.Ess.PeakShaving` (cắt đỉnh tại PCC), `Controller.Ess.Balancing` (cân bằng PCC về `targetGridSetpoint`, mặc định 0 W). Edge↔Backend: JSON-RPC qua WebSocket, xác thực `apikey` qua dịch vụ Metadata (File hoặc Odoo); Backend có thể bọc request tới một Edge bằng `edgeRpc`. https://openems.github.io/openems.io/openems/latest/edge/architecture.html ; https://github.com/OpenEMS/openems/tree/develop/io.openems.edge.controller.ess.balancing ; https://community.openems.io/t/edge-backend-interface/587/2 (qua kết quả tìm kiếm)
15. [FACT] OpenEMS cảnh báo (forum): API Modbus/TCP ghi kênh **không** phải đường điều khiển ESS thủ công; điều khiển phải đi qua Controller tham gia "Power Solver". https://community.openems.io/t/ess-that-can-talk-with-openems-using-modbus-tcp/1029 (qua kết quả tìm kiếm). [INFERENCE] Mẫu thiết kế đáng học: mọi nguồn lệnh (cloud, người vận hành, lịch) phải đi qua **một bộ phân xử công suất duy nhất** ở edge, không ghi thẳng register.
16. [FACT] Sungrow PowerStack 255CS: EMS + PCS + BMS tích hợp; chế độ VPP, demand control, VSG, backup, chuyển mạch liền mạch, black start; tích hợp EMS bên thứ ba qua **Modbus TCP**; ghép tới 25 tủ on-grid / 10 off-grid. https://www.ess-news.com/2025/04/15/sungrow-launches-fully-integrated-ci-battery/ ; https://www.vpsolar.com/en/sungrow-powerstack-bess-solutions-for-ci-solar-installations/ (qua kết quả tìm kiếm)
17. [FACT] Huawei C&I: peak shaving chỉ hỗ trợ trong kịch bản on/off-grid (PQ/VSG) theo một manual LUNA2000-(107-215); một SmartLogger tối đa 20 ESS + 30 inverter song song. https://ske-solar.com/fileadmin/user_upload/UserManual_LUNA2000-_107-215__C_I-Microgrid-SmartLogger3000_V07_2025-11-30_EN.pdf (bản sao manual ở nhà phân phối; qua kết quả tìm kiếm). [INFERENCE] Ràng buộc "chế độ chỉ hợp lệ trong kịch bản X" là phổ biến; driver của ta phải mô hình hóa ma trận tương thích chế độ.
18. [FACT] Huawei Northbound control API là **async task** (gửi task → hỏi `task-info`), chỉ có ở OAuth Connect, và cấm gọi lặp cho cùng một plant trước khi task xong (từ nghiên cứu trước). https://support.huawei.com/enterprise/en/doc/EDOC1100379184/7a471100/control-apis
19. [FACT] HT Infinite Power: EMS là một phần của tủ/container BESS; trang sản phẩm nêu lập lịch, peak shaving, theo dõi SOC, cảnh báo thời gian thực, giao diện CAN/RS‑485/Ethernet/Wi‑Fi, app + web, cập nhật firmware từ xa, đẩy cảnh báo lỗi; **không** tìm thấy bảng register Modbus, tên nền tảng cloud hay API. https://www.infinitepowerht.com/125kw-261kwh-commercial-energy-storage-system.html ; https://www.infinitepowerht.com/261kwh-522kwh-hybrid-energy-storage-system.html (qua kết quả tìm kiếm)
20. [UNKNOWN] Trang gốc người dùng đưa (https://www.infinitepowerht.com/what-is-energy-management-system-ems-and-its-functions.html) **không xuất hiện** trong kết quả tìm kiếm qua nhiều truy vấn; nội dung chưa kiểm chứng. Không trích nội dung trang này.
21. [FACT] Trang "AI-Powered EMS" của InfinitePower chỉ có tuyên bố marketing chung (ví dụ giảm 10–12% phí công suất đỉnh, là ví dụ minh họa của chính trang). https://www.infinitepowerht.com/ai-powered-ems-industrial-energy-storage.html (qua kết quả tìm kiếm). [INFERENCE] Không đủ để coi là có AI; theo quy ước, xếp "U" cho nhóm M.
22. [FACT] ABB OPTIMAX: phần mềm lập lịch/điều phối DER cho phát điện, công nghiệp, thương mại; bản 6.4 (6/2024) thêm module AI dự báo tải, phát, giá để giảm sai số nomination day-ahead/intra-day; triển khai on-prem, data center, cloud hoặc hybrid. https://new.abb.com/news/detail/10576/abb-launches-optimaxr-solutions-for-power-generation-industrial-and-commercial-companies ; https://www.motionandmechatronics.ca/product-news/ai-upgrade-to-abb-energy-man/ ; https://www.abb.com/global/en/company/innovation/news/optimax-energy-management (qua kết quả tìm kiếm)
23. [INFERENCE] "ABB Ability e-mesh" (ra mắt 2019 bởi ABB) xuất hiện năm 2021 trong thông cáo của **Hitachi Energy**; ABB đã bán mảng Power Grids cho Hitachi (hoàn tất 2020). Suy ra e-mesh nay thuộc Hitachi Energy, nhưng chưa thấy nguồn nói thẳng việc chuyển giao. https://new.abb.com/news/detail/15680/abb-launches-unified-software-to-provide-single-view-of-microgrids-and-battery-energy-storage ; https://www.hitachienergy.com/news/press-releases/2021/11/hitachi-energy-releases-global-updates-to-grid-edge-solutions-port-folio-including-new-services ; https://new.abb.com/news/detail/64657/abb-completes-divestment-of-power-grids-to-hitachi
24. [FACT] Stem PowerTrack EMS (ra mắt 2/9/2025): PowerTrack Software quản lý danh mục tập trung + Power Plant Controller + SCADA + edge UI + unit controller **không phụ thuộc phần cứng**; cho C&I và utility. Thư cổ đông tuyên bố giảm 32% giờ kỹ sư nhờ cấu hình sẵn + tinh chỉnh có AI hỗ trợ, độ tin cậy controller 99,99% (tự tuyên bố). https://www.businesswire.com/news/home/20250902991311/en ; https://s27.q4cdn.com/138752898/files/doc_news/Stem-Inc--Letter-to-Shareholders--Reflecting-on-our-journey-of-strategic-realignment-2025.pdf (qua kết quả tìm kiếm)
25. [INFERENCE] Thứ tự quan trọng của "moat" cho nền tảng đa hãng: thư viện driver (AlsoEnergy "8,000+ drivers", nghiên cứu trước) > template cấu hình site (Stem "pre-configuration") > thuật toán tối ưu. Thuật toán peak shaving/TOU là phổ thông.

---

## 3. Phân tích chi tiết theo sản phẩm

Mỗi sản phẩm theo khung 13 mục. "—" = không tìm thấy tài liệu.

### 3.1 P1 — Ampowr Cosmos (Utrecht, NL; Ampowr B.V., thành lập 2021)

| Khía cạnh | Nội dung | Nhãn |
|---|---|---|
| Thị trường & khách hàng | BESS C&I, công nghiệp, nông nghiệp/khách sạn (case Hoge Duin, Bieze Food, A‑Gas, van Pinxteren), utility-scale; "full-service" (bán BESS + EMS + dịch vụ). Văn phòng NL, UK | FACT (L01, L03, L04) |
| Tài sản | Pin, PV/tái tạo, tải cơ sở, lưới, sạc EV, máy phát (gas/diesel), backup | FACT (L01, L06) |
| Giám sát & hiển thị | Theo dõi pin, tái tạo, dùng lưới, tải; ">3,000 datapoints" (AmpiHealth) | FACT (L05) |
| Chiến lược tối ưu | Peak shaving (chuyển sang pin khi chạm giới hạn lưới, ví dụ trần 95 kW ở Hoge Duin), "Net-zero" (tự tiêu thụ), curtailment, energy trading, imbalance trading, aFRR, backup, generator steering | FACT (L03, L04, L06) |
| Điều khiển & dispatch | Bid đồng thời Day-Ahead + imbalance + aFRR; quyết định "từng thời điểm" giữ bao nhiêu công suất cho aFRR vs xuất PV | FACT (L03) |
| Dự báo & phân tích | — (không có tài liệu về phương pháp dự báo, dù bid thị trường ngụ ý cần dự báo giá) | UNKNOWN / INFERENCE |
| Cảnh báo & bảo trì | AmpiHealth: phát hiện bất thường sớm, cảnh báo tự động tới **đội hỗ trợ của Ampowr**, xử lý từ xa hoặc cử đội hiện trường; gắn với gói dịch vụ | FACT (L05) |
| Tích hợp & giao thức | "Third-party Integration", "Cosmos Partner API"; **không** có tài liệu giao thức/endpoint | FACT tên; UNKNOWN chi tiết (L04) |
| Người dùng/vai trò/fleet | — | UNKNOWN |
| Kiến trúc & edge | Cloud + local backup (tiếp tục chiến lược khi mất mạng) | FACT (L04) |
| Bảo mật & tuân thủ | Tự tuyên bố ISO 27001, NIS2 compliant, thiết kế/phát triển/host ở EU, pen-test độc lập; giải thưởng 2025 | FACT (là tuyên bố của hãng; chưa xác minh chứng chỉ) (L02) |
| Hạn chế đã ghi nhận | rfp.wiki (AI, độ tin cậy thấp) nói ít chi tiết giao thức/SCADA, giá theo yêu cầu | INFERENCE, Low (L07) |
| Chưa xác minh | Giao thức hỗ trợ, độ phân giải dữ liệu, phân quyền, chuẩn OCPP | UNKNOWN |

Ghi chú: một kết quả tìm kiếm "Cosmos" khác là sản phẩm quản lý sạc EV của **Circontrol** (https://circontrol.com/cosmos-simplifying-ev-charging-management-since-2019/) — **không liên quan** Ampowr; tránh nhầm.

### 3.2 P2 — HT Infinite Power (Shenzhen Infinite Power Technology Co., Ltd.)

| Khía cạnh | Nội dung | Nhãn |
|---|---|---|
| Thị trường | Nhà sản xuất BESS: tủ C&I (50 kW/100 kWh, 125 kW/261 kWh làm mát lỏng), container 500 kW/1000 kWh, 2000 kWh, 5000 kWh; bán qua web + Alibaba | FACT (L08–L11, L13) |
| Tài sản | Pin LFP + PCS hai chiều + EMS/BMS tích hợp; hệ hybrid có PV; giao tiếp được với BEMS, nền tảng giám sát, microgrid controller | FACT (L08, L10, L11) |
| Giám sát | Màn hình tại chỗ + cloud + EMS cấp trạm; app/web xem phát, tiêu thụ, sạc/xả theo thời gian thực | FACT (L09, L10) |
| Tối ưu | "Custom logic" cho peak shaving, time-shifting, backup; lập lịch tự động; theo dõi SOC | FACT (L11, L13) — là **luật/lịch cố định**, không phải AI |
| Điều khiển | Truy cập từ xa "qua giao diện chuẩn" | FACT, mơ hồ (L08) |
| Dự báo/AI | Trang "AI-Powered EMS" chỉ marketing | FACT là tuyên bố; INFERENCE: chưa có bằng chứng sản phẩm (L12) |
| Cảnh báo | Đẩy cảnh báo lỗi, cảnh báo thời gian thực, "autonomous anomaly detection" (container) | FACT (L10, L13) |
| Tích hợp | CAN, RS‑485, Ethernet, Wi‑Fi | FACT (L08); bảng register: UNKNOWN |
| Thông số 125/261 | 832 V danh định, cell 314 Ah LFP, 125 kW AC, 400 V 3W+N+PE 50/60 Hz, cửa sổ DC ghi khác nhau giữa 2 trang (728–936 V vs 715–923 Vdc), IP55 | FACT (L11) — mâu thuẫn nội bộ |
| Fleet/vai trò, bảo mật | — | UNKNOWN |
| OTA | Cập nhật firmware từ xa / OTA + HMI | FACT (L10) |

[INFERENCE] Đây là hình mẫu thiết bị ta sẽ gặp nhiều nhất ở VN: tủ BESS "all-in-one" với EMS nội bộ đóng, giao tiếp Modbus chưa công bố. Nhiều nhà bán tủ 125/261 gần như giống hệt (Symtech, XIHO, GSL) ghi Modbus RTU/TCP hoặc CAN, nhưng **không thể áp cho HT** (L11 conflicting).

### 3.3 P3 — Schneider Electric EcoStruxure Microgrid Advisor / Microgrid Operation / Power Monitoring Expert

| Khía cạnh | Nội dung | Nhãn |
|---|---|---|
| Thị trường | Tòa nhà thương mại, campus, công nghiệp, utility (microgrid) | FACT (L17) |
| Tài sản | PV, tải tòa nhà, sạc EV, HVAC, pin, cogeneration/CHP, máy phát gas dự phòng; "smart loads": IT, BMS, heat pump, EV, máy móc | FACT (L17) |
| Giám sát | Trending dữ liệu gần thời gian thực + dự báo, cùng lịch giá điện, nhiệt độ; CO2 tracking | FACT (L14, L17) |
| Tối ưu | MPC kết hợp tín hiệu giá, lịch sử, dự báo thời tiết, lịch vận hành; quyết định khi nào tiêu thụ/phát/lưu/bán; quản lý biểu giá theo mùa, day-ahead, hour-ahead; peak shaving | FACT (L14) |
| Điều khiển | Lệnh tới pin trực tiếp hoặc **qua hệ quản lý sẵn có** (cụm sạc EV, BMS tòa nhà cho HVAC) — EMA không thay thế chúng | FACT (L17) |
| Edge | Edge controller giao tiếp DER; kế hoạch dispatch cập nhật từ cloud **mỗi 15 phút** (một nguồn) — nguồn khác không xác nhận; ECC material: edge ra quyết định ≥1 lần/giây | FACT Med/Low, có mâu thuẫn (L16) |
| Mất mạng | Lịch vận hành mặc định trước 48 h | FACT (L15) |
| DR | Tham gia demand response qua kết nối utility hoặc nền tảng aggregator thương mại | FACT (L17) |
| Microgrid | EMO (tùy chọn): PMS on-site trong ECC/MGCC; trình tự islanding (mất lưới → đảo → phối hợp genset+PV → về lưới), quản lý công suất phản kháng DER | FACT (L19) |
| Cảnh báo | EMA: —. PME: phân tích chất lượng điện, transient capture, process impact alarms, ISO 50001 | P (L20) |
| Tích hợp | Danh sách giao thức DER cho EMA: không tìm thấy; PME kết nối relay qua Modbus TCP (luận văn) | UNKNOWN / P |
| Bảo mật | Chương trình IEC 62443 cho EcoStruxure Power (sản phẩm 4-2, một số 4-1; kiến trúc chứng nhận 62443-3-3 bởi bên thứ ba); phạm vi áp cho EMA cloud chưa rõ | FACT phạm vi chưa rõ (L18) |
| Hạn chế | Tài liệu chính 2017–2019; phiên bản hiện hành chưa rõ | INFERENCE |

### 3.4 P4 — Siemens SICAM Microgrid Control (+ MGMS, Electrification X)

| Khía cạnh | Nội dung | Nhãn |
|---|---|---|
| Thị trường | Microgrid công nghiệp (hóa chất), campus, utility; tới ~2 GW phát; tham chiếu campus Siemens Wendell, NC | FACT (L21, L22) |
| Tài sản | Tái tạo, pin, máy phát diesel (dùng chủ yếu dự phòng), tải | FACT (L21) |
| Chức năng | Blackout detection, black start, reserve monitoring, peak shaving, giảm demand charge, tối ưu OPEX, chuyển chế độ lưới tự động; quản lý SOC (lưu thừa tái tạo, giữ mức năng lượng tối thiểu, lịch sạc/xả); 5 thuật toán quản lý tải; demand response & dynamic load control; load shedding & advanced dispatch; quy trình tự động cho thị trường năng lượng/dịch vụ phụ trợ | FACT (L21, L22) |
| Dự báo | Tải và tái tạo theo lịch sử + thời tiết; nhập/import dự báo thủ công; IEC 62898-2 | FACT (L21) |
| Giao thức | IEC 61850 (GOOSE ~70 ms cho load shedding — ứng dụng SICAM, không phải MGC), IEC 60870-5, Modbus | FACT (L21, L23) |
| HMI | SICAM SCC trên nền WinCC (có server dự phòng) | P (L40 xem ledger) |
| Dự phòng | Tùy chọn "redundant live controller" (brochure) | P |
| Bảo mật | IEC 62443, IPSec, crypto chip (tuyên bố trang sản phẩm) | FACT (L22) |
| MGMS | Spectrum Power MGMS: dự báo tải/phát 7 ngày, unit commitment, load shed, chuyển đổi liền mạch; có bản hosted cho nhà vận hành nhỏ (tài liệu cũ) | FACT, tài liệu cũ (L24) |
| EV | Electrification X Load Management (cloud): giám sát trạng thái/tải mạng sạc, điều khiển từ xa, dynamic load management (Aral DE/AT) | FACT (L25) |
| Fleet đa site C&I | — (MGC là controller một site) | UNKNOWN |

[INFERENCE] SICAM MGC là chuẩn "microgrid controller" nặng (IEC 61850, black start). Quá mức cho site C&I VN thông thường, nhưng danh sách chức năng là checklist tốt cho nhóm M (microgrid) ở giai đoạn sau.

### 3.5 P5 — ABB Ability OPTIMAX (+ e-mesh / Hitachi Energy, Energy and Asset Manager)

| Khía cạnh | Nội dung | Nhãn |
|---|---|---|
| Tên đã kiểm chứng | "ABB Ability™ OPTIMAX®" (đúng); "ABB Ability e-mesh" (2019, nay xuất hiện dưới Hitachi Energy); "ABB Ability Microgrid" — **không tìm thấy** tên sản phẩm này | FACT/INFERENCE (L26, L27, L28) |
| Thị trường OPTIMAX | Phát điện, công nghiệp, thương mại, nhà máy hybrid; ngành hơi/điện, hydrogen xanh, thu hồi carbon, xử lý nước thải, district heating/cooling | FACT (L26) |
| Tối ưu | Lập lịch & điều phối DER (gió, mặt trời), quyết định lượng/thời điểm feed-in, khi nào mua lưới, so sánh chi phí nguồn; pin, máy phát, tải | FACT (L26) |
| Dự báo/AI | Bản 6.4: AI dự báo tải, phát, giá; giảm sai số nomination; AutoML | FACT (L27) |
| Triển khai | On-prem, data center, cloud, hybrid; module đặt riêng lẻ | FACT (L26, L27) |
| e-mesh EMS (Hitachi Energy 2021) | Giảm hóa đơn qua vận hành BESS + DER, quản lý tải, EV; e-mesh Monitor cloud; MicroSCADA/RTU; Skagerak Arena: dispatch theo dự báo tải, PV, xu hướng giá | FACT (L28) |
| Energy and Asset Manager | SaaS: widget Energy Monitoring, Power Factor, Power Quality, Group Peak Monitoring; báo cáo email; cảnh báo 24/7 | FACT (L29) |
| Giao thức, vai trò, bảo mật OPTIMAX | — | UNKNOWN |

### 3.6 P6 — SolarEdge ONE for C&I + ONE Controller (CLC1) + ONE Manager

| Khía cạnh | Nội dung | Nhãn |
|---|---|---|
| Thị trường | EPC, O&M, developer, doanh nghiệp C&I; ra mắt 6/2024, toàn cầu 12/2024 | FACT (L30) |
| Tài sản | PV (inverter + optimizer), lưu trữ SolarEdge (CSS-OD; giải pháp tham chiếu với Socomec SUNSYS HES L), sạc EV (đội xe), tài sản tòa nhà (HVAC, chiếu sáng), công tơ, cảm biến thời tiết bên thứ ba | FACT (L30, L31) |
| Giám sát | Phân tích hiệu suất toàn fleet tới cấp module; digital twin 3D (từ SolarEdge Designer + dữ liệu sống), phát hiện module kém qua nhiệt, sơ đồ cáp theo inverter/string | FACT (L30) |
| Tối ưu | Dùng biểu giá + dự báo thời tiết + lịch sử phát/tiêu thụ; dynamic load management, Advanced Peak Shaving, tối ưu biểu giá, tham gia thị trường/lưới | FACT (L30) |
| Điều khiển | Cấu hình & xử lý sự cố từ xa; lệnh PPC | FACT (L30) |
| EV | Mua Wevo (4/2024): phần mềm sạc nhiều cổng, đa hãng, định giá/thanh toán đa người dùng, ưu tiên theo tầng, quản lý tải dự báo | FACT (L33) |
| Cảnh báo | Live alerts; sự kiện shutdown từ ONE Controller sinh cảnh báo nêu nguồn | FACT (L32) |
| Tích hợp (L34) | CLC1: 2×RS485 (Modbus RTU), CAN, 2×RJ45 (Modbus TCP, WAN/LAN), Wi‑Fi 6, BLE 5.3, 4 DI/4 DO; Modbus TCP cổng 1502 + register map; công tơ RS485 Modbus (danh sách Appendix B; v1.0 liệt kê 4 model SE‑…‑MB); API "cho phần mềm khác truy cập" | FACT (L31, L34) |
| Giới hạn phát | Ghi chú Export Limitation v3.0 (8/2026): công tơ import/export phải đặt tại điểm đấu nối; công tơ tiêu thụ **không** hỗ trợ cho export limitation (áp dụng inverter/gateway; chưa rõ cho ONE Controller) | FACT phạm vi chưa rõ (L35) |
| Vai trò/fleet | Site Admin: User Role, Monitoring Access, quyền bên thứ ba, Public, Kiosk, API Access, PR chart, đăng ký cảnh báo theo user | FACT (L32) |
| Kiến trúc | Controller tại site + cloud; một nhà bán lẻ nói cần Internet cho giám sát/fleet/lệnh PPC (độ tin cậy thấp) | P |
| Thương mại | Lõi miễn phí cho người mua phần cứng; gói trả phí đưa dần | FACT (L31) |
| Chưa xác minh | Điều khiển pin bên thứ ba; LTE; độ phân giải dữ liệu; bảo mật/chứng chỉ; giới hạn API V2 | UNKNOWN |

### 3.7 P7 — Huawei FusionSolar SmartPVMS (C&I) + SmartLogger5000B / EMMA-A02

(Tái sử dụng nghiên cứu FusionSolar; chỉ thêm phần EMS/BESS.)

| Khía cạnh | Nội dung | Nhãn |
|---|---|---|
| Thị trường | Installer/O&M, chủ đầu tư dân dụng → utility; phổ biến VN | FACT (nghiên cứu trước) |
| BESS | LUNA2000 C&I (97–241 kWh); cell-level SOC, SOH, điện áp, nhiệt độ | FACT (L36) |
| Tối ưu | SmartEMO: tự chỉnh peak shaving theo dữ liệu lịch sử; tối đa tự tiêu thụ, TOU, peak staggering; peak shaving **chỉ** trong kịch bản on/off-grid (PQ/VSG) theo manual microgrid; "active power limit": công suất mua lưới không vượt ngưỡng đặt | FACT (L36, L37) |
| Vòng điều khiển | SmartLogger5000B: zero feed-in khép kín ≤2 s, peak shaving/capacity limit ≤5 s | FACT, nguồn nhà phân phối (L37) |
| Quy mô | 1 SmartLogger: ≤20 ESS, ≤30 inverter song song (SmartLogger3000 microgrid) | FACT (L37) |
| EMMA-A02 | Peak shaving, ưu tiên PV, giới hạn feed-in, tự khởi/dừng diesel, dự báo dư PV và giữ khoảng SOC theo thuật toán; nhắm hộ gia đình + thương mại nhỏ | FACT (L38) |
| PV | Smart I-V trên mọi string; giám sát cấp module tới 60 MW | FACT (L36) |
| API | Northbound pull-only, quota theo phút/ngày; control API async-task, chỉ OAuth Connect | FACT (L39) |
| Vai trò | Company Admin/Installer/Owner (owner chức năng hạn chế) | FACT (nghiên cứu trước, L39) |
| Bảo mật | Không thấy ISO 27001/IEC 62443 cho cloud | UNKNOWN (nghiên cứu trước) |
| Lưu trữ | Dữ liệu thiết bị lịch sử 15 tháng (EU), động 5 phút | FACT (nghiên cứu trước) |

### 3.8 P8 — Sungrow PowerStack 255CS + EMS300CP + iSolarCloud

| Khía cạnh | Nội dung | Nhãn |
|---|---|---|
| Thị trường | C&I; 125 kW/257 kWh mỗi tủ, ghép 257 kWh – 6,4 MWh | FACT (L41) |
| Chế độ | VPP, demand control, VSG, backup, chuyển mạch liền mạch (<20 ms theo nhà phân phối), black start; bản On&Off-Grid 2026: khởi động & đồng bộ diesel (AC-coupled), DC-coupled ≤250 kW không cần tủ ATS | FACT, một phần qua nhà phân phối/báo (L41) |
| Điều khiển | Thuật toán dispatch EMS; chiến lược đồng bộ on-site và cloud cho peak shaving/demand (200CS) | FACT (L41) |
| Giám sát | iSolarCloud: cảnh báo thời gian thực, phát hiện lỗi, OTA, bảo trì dự đoán (tuyên bố); chu kỳ 5 phút; thiết bị: inverter, sạc EV, trạm thời tiết, công tơ, biến áp, CB | FACT (L41, L42) |
| Tích hợp | Modbus TCP qua Ethernet với EMS300CP hoặc **EMS bên thứ ba**; Open API (API key + access key + RSA key); cộng đồng dùng Open API ghi lệnh sạc/xả, giới hạn SOC | FACT (L41, L42); community = Low |
| Hạn chế | Eniris: một số firmware cũ không tôn trọng giới hạn công suất tác dụng | FACT (L42) |
| Vai trò | Phân quyền phân cấp (blog Sungrow, nghiên cứu trước) | P |
| Bảo mật | "financial grade security" (mơ hồ) | UNKNOWN |

### 3.9 P9 — OpenEMS (mã nguồn mở)

| Khía cạnh | Nội dung | Nhãn |
|---|---|---|
| Thị trường | Nền tảng mở; FENECON là nhà sản xuất chính; OpenEMS Association e.V. | FACT (L43, L45) |
| Kiến trúc | Edge (OSGi/Java, on-site) – Backend (cloud) – UI (Angular, theo repo) | FACT (L43); "Angular/Java" là INFERENCE từ cấu trúc repo `ui/` |
| Controllers | PeakShaving tại PCC; Balancing (PCC về `targetGridSetpoint`); GridOptimizedCharge (tồn tại trong release 2026.4.0); ToU optimizer cho ESS theo slot giờ/15 phút | FACT (L43, L44) |
| Biểu giá | Module ToU Tibber chuyển sang giá 15 phút (2025.11.0) | FACT (L44) |
| EV | Có module `io.openems.edge.evcs.ocpp.server` và các module EVCS theo hãng | FACT tên module (L44) |
| Edge↔Backend | JSON-RPC/WebSocket, `apikey`, Metadata File/Odoo, Timedata; `edgeRpc` | FACT (L43) |
| API ngoài | `Controller.Api.ModbusTcp.ReadWrite`, REST/JSON, WebSocket | FACT (L43) |
| Điều hướng lưới | Triển khai tham chiếu §14a EnWG với Fraunhofer ISE + FENECON (6/2026) | FACT (L45) |
| Giấy phép | Repo có file EPL-2.0 và AGPL-3.0; cách áp dụng cụ thể chưa đọc | UNKNOWN chi tiết (L44) |
| Hạn chế | Tài liệu giao thức Edge-Backend mỏng; cộng đồng nói "chưa có tài liệu thật" | FACT (L43) |

### 3.10 P10 — Stem PowerTrack EMS / Athena (+ AlsoEnergy PowerTrack)

| Khía cạnh | Nội dung | Nhãn |
|---|---|---|
| Thị trường | Developer, EPC, integrator quốc tế; C&I và utility; khách PowerTrack sẵn có | FACT (L46) |
| Kiến trúc | Portfolio software (cloud) + PPC + SCADA + edge UI + unit controller không phụ thuộc phần cứng | FACT (L46) |
| Tối ưu | Sạc/xả pin, grid services, value stacking; Athena: tối ưu hóa đơn, thuật toán dự đoán tối đa tiết kiệm | FACT (L46, L47) |
| Giám sát PV | 200,000+ site, "8,000+ drivers and point maps", Modbus TCP/RTU, báo cáo mẫu (tài chính, nghiệm thu, capacity test) | FACT (nghiên cứu trước, L48) |
| EV | Athena tích hợp quản lý sạc EV | FACT (L47) |
| Tuyên bố | −32% giờ kỹ sư, 99,99% độ tin cậy controller | FACT là tự tuyên bố (L46) |
| Bảo mật, vai trò chi tiết | — | UNKNOWN |

### 3.11 P11 — GridBeyond Point

| Khía cạnh | Nội dung | Nhãn |
|---|---|---|
| Thị trường | 400+ site C&I (UK, IE, US, JP, AU); không cần CAPEX từ khách | FACT (L49) |
| Tài sản | Tải sản xuất, phát phân tán, pin, inverter, máy phát, sạc EV | FACT (L49) |
| Tối ưu | AI dự báo, tối ưu, dispatch tự động cho arbitrage, frequency response, capacity market; ràng buộc tài sản và mô hình suy giảm pin | FACT (vendor, qua hồ sơ Solar Impulse) (L49) |
| Hiển thị | ViewPoint Lens (9/2025): hồ sơ tải, phản ứng trong sự kiện DR, tổng hợp doanh thu | FACT (L49) |
| Còn lại | — | UNKNOWN |

---

### 3.12 Ma trận tính năng

Ký hiệu: V / P / U / NA, kèm mã ledger (Lxx). Cột: AMP = Ampowr Cosmos; HTI = HT Infinite Power; SE = Schneider EMA(+EMO/PME); SIE = Siemens SICAM MGC(+MGMS/ElecX); ABB = OPTIMAX(+e-mesh); SED = SolarEdge ONE C&I; HUA = Huawei SmartPVMS C&I; SUN = Sungrow PowerStack+iSolarCloud; OEMS = OpenEMS; STM = Stem PowerTrack EMS/Athena; GB = GridBeyond.

| Năng lực | AMP | HTI | SE | SIE | ABB | SED | HUA | SUN | OEMS | STM | GB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 Quản lý đa site / fleet | U | U | U | U | P L28 (e-mesh "fleets") | V L30 | V L39 | P L42 | P L43 | V L46 | U |
| A2 Vai trò & phân quyền chi tiết | U | U | U | U | U | V L32 | V L39 | P L42 | P L43 (Metadata/Odoo) | U | U |
| B Dashboard/KPI | P L05 | V L10 | V L14 | P L40 | P L29 (EAM) | V L30 | V L39 | V L42 | P L43 | P L48 | P L49 |
| C Giám sát thời gian thực (độ phân giải công bố) | P L05 (3.000 điểm, không rõ chu kỳ) | P L10 | P L16 | P L21 | U | P L30 | V L39 (5 phút) | V L42 (5 phút) | V L43 | U | U |
| D Lịch sử/báo cáo | U | U | P L17 (CO2) | U | P L29 | P L32 (PR) | V L39 | U | P L43 (Timedata) | V L48 | P L49 |
| E1 Giám sát BESS (SOC/SOH, cell) | V L05 | V L13 | P L17 | V L21 | P L26 | V L30 | V L36 | V L41 | V L43 | V L46 | V L49 |
| E2 Chế độ BESS tùy chỉnh (lịch/TOU/backup) | V L06 | V L11 | V L14 | V L21 | P L26 | V L30 | V L37 | V L41 | V L44 | V L46 | P L49 |
| F1 Chẩn đoán PV (string/module, I-V) | U | U | U | U | U | V L30 | V L36 | P (I-V, nghiên cứu trước) | U | V L48 | NA |
| F2 Giới hạn phát/zero-export | P L06 (curtailment) | U | U | P L23 (PPC app) | P L26 | V L35 | V L37 | P L42 | V L43 (Balancing setpoint) | V L46 (PPC) | U |
| G1 Peak shaving / giới hạn mua lưới | V L04 | V L13 | V L14 | V L21 | U | V L30 | V L37 | V L41 | V L43 | P L47 | P L49 |
| G2 Tối ưu theo biểu giá (TOU/dynamic) | P L06 | V L11 (time-shifting) | V L14 | P L21 (demand charge/OPEX) | V L26 | V L30 | V L36 | P L41 | V L44 | V L47 | V L49 |
| H Quản lý sạc EV | P L06 | U | V L17 (qua cụm quản lý EV) | V L25 (ElecX) | P L28 | V L33 | P (SCharger, nghiên cứu trước) | P L42 | P L44 (module OCPP) | P L47 | P L49 |
| I1 Lập lịch dựa trên dự báo / MPC | U | U | V L14 | V L21 | V L27 | V L30 | P L36 | U | P L44 (ToU optimizer) | P L47 | V L49 |
| I2 Thị trường/DR/value stacking | V L03 | U | V L17 | V L21 | V L27 (nomination) | P L30 | U | P L41 (chế độ VPP) | P L45 (§14a) | V L46 | V L49 |
| J1 Cảnh báo & thông báo | V L05 | V L10 | P L20 (PME) | U | P L29 (EAM) | V L32 | V L39 | V L41 | U | P L48 | U |
| J2 Quy trình bảo trì/dịch vụ | V L05 (đội hỗ trợ) | U | U | U | P L29 | P L30 (remote troubleshooting) | P L39 | P L41 (bảo trì dự đoán, tuyên bố) | U | P L48 | U |
| K1 Giao thức thiết bị công bố | U | P L08 | P L20 | V L21, L23 | U | V L34 | V L39 | V L41 | V L43 | V L48 | U |
| K2 API cho bên thứ ba | P L04 (Partner API, không tài liệu) | U | U | U | U | P L32 | V L39 | V L42 | V L43 | U | U |
| K3 Thiết bị đa hãng | V L01 | P L08 | V L17 | P L21 | P L26 | P L31 (công tơ/cảm biến) | P L38 (EMMA tải bên thứ ba) | V L41 (EMS bên thứ ba) | V L43 | V L46 | V L49 |
| L1 Chứng nhận bảo mật công bố | V* L02 (tự tuyên bố) | U | P L18 | V* L22 | U | U | U | U | NA | U | U |
| L2 Lưu trữ/hosting theo vùng | V* L02 (EU) | U | U | NA (on-prem) | V L27 (on-prem tùy chọn) | U | V L39 (EU) | U | V L43 (tự host) | U | U |
| M1 Dự báo tải/PV/giá | U | U | V L14 | V L21 | V L27 | V L30 | V L38 (EMMA) | U | P L44 | P L47 | V L49 |
| M2 Microgrid/islanding/black start | P L06 (backup) | P L11 (backup) | V L19 | V L21 | P L28 | U | V L37 | V L41 | U | U | NA |
| M3 "AI" có mô tả cụ thể | U | U (chỉ marketing) | P L14 (gọi "AI", thực chất MPC) | NA | V L27 | P L33 (Wevo "AI" phân bổ sạc) | P L38 | U | NA | P L46 | P L49 |
| X1 Edge chạy khi mất mạng | V L04 | V L09 | V L15 | V L21 (on-prem) | V L27 | U | V L37 | P L41 | V L43 | V L46 | U |
| X2 Điều khiển genset/CHP | V L06 | U | V L17 | V L21 | P L26 | U | V L38 | P L41 | U | U | P L49 |
| X3 Mô hình triển khai | Cloud+edge | Thiết bị + cloud | Cloud+edge (+on-prem EMO) | On-prem | On-prem/cloud/hybrid | Cloud+controller | Cloud+logger | Cloud+EMS tại chỗ | Tự host Edge+Backend | Cloud+PPC/edge | Cloud (+gateway, U) |

`V*` = Verified là *tuyên bố của hãng*; chưa kiểm tra chứng chỉ.

### 3.13 Phân loại năng lực (4 tầng theo yêu cầu)

| Tầng | Năng lực |
|---|---|
| **Có tài liệu rõ (explicit)** | Peak shaving/giới hạn mua lưới (≥8 sản phẩm); TOU/biểu giá; BESS SOC monitoring; edge vẫn chạy khi mất mạng (Ampowr, Schneider 48 h, Siemens, Huawei, OpenEMS, Stem); module-level PV (SolarEdge, Huawei); EV qua quản lý tải (SolarEdge/Wevo, Siemens ElecX, Schneider qua cụm EV); thị trường DA/imbalance/aFRR (Ampowr); Modbus TCP/RTU ở edge (SolarEdge, Sungrow, OpenEMS, Stem); async control task (Huawei) |
| **Suy luận (inferred)** | Ampowr cần dự báo giá để bid (không có tài liệu); SolarEdge ONE cần Internet cho lệnh PPC (chỉ nguồn bán lẻ); e-mesh thuộc Hitachi Energy; tủ BESS Trung Quốc dùng Modbus RTU/TCP |
| **Chuẩn ngành nhưng chưa kiểm chứng cho từng hãng** | OCPP 1.6J/2.0.1 cho sạc EV; SunSpec Modbus cho inverter; IEC 60870-5-104 / DNP3 cho SCADA; IEC 61850 cho trạm; SOC min/max reserve, giới hạn C-rate, ramp rate; mã hóa TLS, RBAC, audit log; lưu dữ liệu đệm ở edge (store-and-forward) |
| **Đề xuất cho ta** | Xem mục 4 |

### 3.14 Chi tiết kỹ thuật dùng được cho thiết kế

- **Hai tầng thời gian** (FACT/INFERENCE): kế hoạch cloud cỡ 15 phút (Schneider, 1 nguồn), slot giá 15 phút (OpenEMS Tibber 2025.11), dự báo 7 ngày (Siemens MGMS); vòng edge ≤1–5 s (Huawei 2 s/5 s; Schneider ≥1 Hz). → Đề xuất: plan 15 phút, horizon 24–48 h, cập nhật lại khi có dữ liệu mới; edge loop 1 s cho PCC.
- **Lịch dự phòng khi mất mạng**: Schneider giữ lịch mặc định 48 h. → Edge của ta lưu sẵn kế hoạch ≥48 h + chiến lược fallback an toàn (self-consumption/peak shaving theo ngưỡng cố định).
- **Mô hình lệnh async**: Huawei control API trả task id, cấm gửi chồng. → API điều khiển của ta: lệnh có id, trạng thái `pending/acked/applied/rejected/expired`, idempotency key, một lệnh hiệu lực/thiết bị.
- **Tham số giới hạn phát**: SolarEdge yêu cầu công tơ tại điểm đấu nối (không dùng công tơ tiêu thụ); OpenEMS dùng `targetGridSetpoint` (W, mặc định 0). → Model site cần `pcc_meter_id` bắt buộc cho chức năng G/F2.
- **Ma trận tương thích chế độ**: Huawei: peak shaving chỉ ở on/off-grid PQ/VSG; có thể kết hợp tự tiêu thụ hoặc TOU. Sungrow: 25 tủ on-grid / 10 off-grid. → Driver profile phải khai báo chế độ được phép theo topology.
- **Cổng/giao diện edge tham chiếu (SolarEdge CLC1)**: 2× RS485, 1× CAN, 2× Ethernet (WAN/LAN tách), Wi‑Fi, BLE (commissioning), 4 DI/4 DO (tín hiệu ngoài như lệnh cắt giảm của lưới, E-stop). Modbus TCP server cổng 1502 cho hệ thống bên thứ ba.
- **Phân quyền chia sẻ**: SolarEdge có Kiosk View, Public Access, API Access, quyền bên thứ ba có phạm vi. → Đáng sao chép cho installer chia sẻ với chủ đầu tư.
- **Cảnh báo theo user**: SolarEdge cho bật/tắt nhận cảnh báo theo từng user; Ampowr chuyển cảnh báo đến đội hỗ trợ trung tâm (NOC). → Hai chế độ: khách tự giám sát / O&M provider giám sát hộ.

---

## 4. Hệ quả thiết kế cho sản phẩm

- [PROPOSAL] **PR-B01 (P0)** Giữ kiến trúc edge-first: edge thực thi vòng PCC (≤1 s đo, ≤5 s đáp ứng mục tiêu cho peak shaving, ≤2 s cho zero-export, theo mức Huawei công bố), cloud lập kế hoạch 15 phút. Cơ sở: L04, L15, L16, L37. Không đổi hướng so với nghiên cứu FusionSolar.
- [PROPOSAL] **PR-B02 (P0)** Edge lưu kế hoạch ≥48 h và fallback an toàn khi mất cloud; dữ liệu store-and-forward. Hiển thị trạng thái "đang chạy lịch dự phòng" trên dashboard. Cơ sở: L15, L04.
- [PROPOSAL] **PR-B03 (P0)** Một bộ phân xử công suất duy nhất ở edge (giống OpenEMS Power Solver): mọi nguồn lệnh (lịch, người vận hành, API, DR) → arbitration theo ưu tiên → setpoint. Ràng buộc native (BMS/PCS/relay) luôn thắng; cloud không bao giờ bỏ qua bảo vệ thiết bị. Cơ sở: L43 (forum).
- [PROPOSAL] **PR-B04 (P0)** API điều khiển bất đồng bộ có task id + trạng thái + hết hạn + idempotency (học Huawei). Cơ sở: L39.
- [PROPOSAL] **PR-B05 (P0)** Gói chiến lược MVP = peak shaving/giới hạn mua lưới, TOU arbitrage (biểu giá EVN 3 khung), tự tiêu thụ, zero-export, backup reserve SOC. Đây là table stakes (≥8 sản phẩm). Gắn nhãn "luật/lịch", **không** gọi là AI.
- [PROPOSAL] **PR-B06 (P1)** Lập lịch dựa trên dự báo (PV + tải, horizon 24–48 h, slot 15 phút) bằng tối ưu hóa (LP/MILP hoặc MPC) — chỉ gọi là "tối ưu dựa trên dự báo", và chỉ dùng chữ "AI/ML" nếu thật sự có mô hình học. Cơ sở: L14, L21, L27.
- [PROPOSAL] **PR-B07 (P0)** Driver profile khai báo: chế độ được phép theo topology (on-grid/off-grid), số tủ song song tối đa, công tơ PCC bắt buộc, quirk firmware (ví dụ Sungrow firmware cũ không tôn trọng giới hạn P). Cơ sở: L37, L41, L42.
- [PROPOSAL] **PR-B08 (P0)** Thư viện driver là tài sản chính: ưu tiên Huawei (Modbus qua SmartLogger/EMMA), Sungrow (Modbus TCP – EMS bên thứ ba được hỗ trợ chính thức), SolarEdge (Modbus TCP 1502), tủ BESS Trung Quốc chung (Modbus RTU/TCP, CAN) với template ánh xạ register cấu hình được. Cơ sở: L41, L31, L48.
- [PROPOSAL] **PR-B09 (P1)** Phân quyền chia sẻ kiểu SolarEdge: Org → Site; vai trò Installer Admin / O&M Engineer / Owner Viewer / Third-party (API) / Kiosk công khai; đăng ký cảnh báo theo user × site. Cơ sở: L32.
- [PROPOSAL] **PR-B10 (P1)** Chế độ "giám sát hộ" (managed service): cảnh báo đi vào hàng đợi NOC của nhà O&M (giống AmpiHealth), có SLA, ticket. Đây là mô hình doanh thu cho installer VN. Cơ sở: L05.
- [PROPOSAL] **PR-B11 (P1)** EV: quản lý tải động cho cụm sạc qua OCPP (1.6J trước), giới hạn theo dư công suất PCC; không xây CSMS thanh toán ở MVP. Cơ sở: L25, L33, L44.
- [PROPOSAL] **PR-B12 (P2)** Microgrid/islanding/black start: **không** làm ở cloud; chỉ giám sát và phối hợp với controller native (PCS VSG, ATS, SmartLogger/EMS hãng). Checklist tham chiếu là chức năng SICAM MGC (L21).
- [PROPOSAL] **PR-B13 (P1)** Bảo mật: thiết kế theo IEC 62443 (zone/conduit, 3-3 cho hệ thống, 4-2 cho edge) và ISO 27001 cho vận hành cloud. Chỉ tuyên bố khi có chứng chỉ (số, phạm vi, hạn). Edge tách WAN/LAN như CLC1. Cơ sở: L02, L18, L22, L40.
- [PROPOSAL] **PR-B14 (P2)** Tham gia thị trường/DR: để hook (DI tín hiệu từ lưới, API sự kiện DR) nhưng không phát triển bidding cho tới khi VN có cơ chế. Cơ sở: L03, L45.
- [PROPOSAL] **PR-B15 (P1)** Báo cáo "giá trị đã tạo" theo chiến lược (kWh dịch chuyển, kW đỉnh giảm, VND tiết kiệm) — GridBeyond ViewPoint Lens và Stem Athena đều đặt trọng tâm vào đây. Cơ sở: L47, L49.
- [PROPOSAL] **PR-B16 (P2)** Cân nhắc dùng OpenEMS Edge làm nền edge thay vì tự viết: cần kiểm tra giấy phép (EPL-2.0/AGPL-3.0) và khả năng tích hợp backend Java/Spring của ta (giao thức JSON-RPC/WebSocket chưa tài liệu hóa đầy đủ). Cơ sở: L43, L44.

---

## 5. Evidence ledger

Tất cả bằng chứng mới là "(qua kết quả tìm kiếm)" trừ khi ghi "nghiên cứu trước". Ngày truy cập: 2026-10-10.

| # | Claim | Source URL | Source type & date | Excerpt/paraphrase | Confidence | Conflicting evidence | Design implication |
|---|---|---|---|---|---|---|---|
| L01 | Cosmos điều khiển tài sản phát/lưu/tiêu thụ, >3.000 datapoint, tích hợp bên thứ ba | https://ampowr.com/energy-management-system-ems/ ; https://ampowr.com/ | Trang sản phẩm hãng; không ngày | "controls assets that produce, store, or consume energy"; "Third-party Integration" (qua kết quả tìm kiếm) | Med | rfp.wiki: ít chi tiết giao thức | Đa hãng là kỳ vọng cơ bản |
| L02 | Cosmos ISO 27001, NIS2, host EU, pen-test | https://ampowr.com/nis2-compliance/ ; https://ampowr.com/battery-energy-storage-systems/battery-energy-storage-solutions/utility-scale/ ; https://ampowr.com/energy-management-system-ems/backup-power/ | Trang hãng; trang NIS2 nhắc đề xuất sửa đổi 3/2026 | "ISO27001 certified and NIS2 compliant"; "designed, developed, and hosted in EU" | Med (tự tuyên bố) | Không tìm thấy registry chứng chỉ | Tuyên bố bảo mật phải kèm bằng chứng |
| L03 | Bid đồng thời DA + imbalance + aFRR | https://ampowr.com/case-study-gebroeders-van-pinxteren/ ; https://ampowr.com/battery-energy-storage-systems-imbalance-trading/ | Case study hãng | "Day-Ahead, imbalance, and aFRR are bid together" | Med | — | Thị trường = P2 cho VN |
| L04 | Peak shaving trần 95 kW; Partner API; local backup khi mất mạng | https://ampowr.com/hoge-duin-hotel-enhances-energy-efficiency-with-ampifarm-peak-shaving/ | Case study hãng | "will continue to perform strategies and collect data through a local backup feature" | Med | — | PR-B01, PR-B02 |
| L05 | AmpiHealth >3.000 điểm, cảnh báo tới đội hỗ trợ, gói dịch vụ | https://ampowr.com/ampihealth/ | Trang hãng | "Automated alerts go straight to Ampowr's support team" | Med | — | PR-B10 |
| L06 | Chiến lược Net-zero, curtailment, peak shaving khi chạm giới hạn lưới, generator steering, EV/backup | https://ampowr.com/energy-management-system-ems/peak-shaving/ ; https://ampowr.com/battery-energy-storage-systems/battery-energy-storage-system-generator-steering/ ; https://ampowr.com/ | Trang hãng | "Switch to energy from battery when grid limit is reached" | Med | Chi tiết SOC→genset chỉ từ tóm tắt chung | Danh mục chiến lược MVP |
| L07 | Hồ sơ rfp.wiki là AI sinh, ~30% tin cậy | https://www.rfp.wiki/vendors/ampowr ; https://www.rfp.wiki/vendors/stem | Trang tổng hợp AI | Tự ghi độ tin cậy thấp | Low | — | Không dùng làm bằng chứng |
| L08 | HT EMS: lập lịch, giám sát, truy cập từ xa; CAN/RS‑485/Ethernet/Wi‑Fi | https://www.infinitepowerht.com/50kwh-battery-storage-system.html ; https://www.infinitepowerht.com/commercial-energy-storage-solutions.html | Trang sản phẩm hãng (snippet không chỉ rõ trang nào) | "remote access via standard interfaces" | Low–Med | — | Driver cần cấu hình register |
| L09 | Container 500 kW/1000 kWh: EMS thu thập dữ liệu, điều khiển, màn hình tại chỗ, upload | https://www.infinitepowerht.com/1000-kwh-battery-outdoor-container-ess.html | Trang sản phẩm | "integrated power station data communication collection and operation control" | Med | — | EMS hãng = lớp native, ta ở trên |
| L10 | Hybrid: panel + cloud + EMS trạm; app/web; firmware từ xa; đẩy cảnh báo | https://www.infinitepowerht.com/261kwh-522kwh-hybrid-energy-storage-system.html | Trang sản phẩm | "remote firmware updates and fault alarm push" | Med | Tên cloud không công bố | — |
| L11 | 125/261: custom logic peak/time-shift/backup; 832 V, 314 Ah, IP55 | https://www.infinitepowerht.com/125kw-261kwh-commercial-energy-storage-system.html | Trang sản phẩm | DC 728–936 V vs 715–923 Vdc | Med | Mâu thuẫn dải DC giữa trang; hàng tương tự (Symtech, XIHO, GSL) ghi giao thức khác | Không suy giao thức từ hàng "giống" |
| L12 | Trang "AI-Powered EMS" chỉ là marketing | https://www.infinitepowerht.com/ai-powered-ems-industrial-energy-storage.html | Blog hãng | Ví dụ 10–12% giảm phí đỉnh | Low | — | Không gọi luật cố định là AI |
| L13 | Container 2000 kWh: lập lịch, peak shaving, SOC, cảnh báo | https://www.infinitepowerht.com/2000kwh-battery-outdoor-container-ess.html/ | Trang sản phẩm | "automated scheduling, peak shaving, SOC tracking, real-time alerts" | Med | — | Table stakes |
| L14 | EMA: MPC với giá, lịch sử, thời tiết, lịch vận hành; biểu giá mùa/DA/HA | https://www.se.com/us/en/product-range/65896/ ; https://download.schneider-electric.com/doc/998-20080341_US/EcoStruxure%20Microgrid%20Advisor%20Handout.pdf | Trang + handout hãng (~2017) | "Model Predictive Control algorithms… price signals, historic data, weather forecast and operating schedule" | Med–High | Tài liệu cũ | PR-B06 |
| L15 | EMA lịch mặc định 48 h khi mất server | https://marketplace.microsoft.com/en-us/product/saas/869296.microgrid_advisor?tab=overview | Listing Microsoft Marketplace | "48-hour advance default operation schedules" | Med | — | PR-B02 |
| L16 | Edge thực thi dispatch plan; cập nhật từ cloud mỗi 15 phút; edge ≥1 quyết định/s | https://www.productinfo.schneider-electric.com/esxp_digital_apps_iec/mg/English/ESXP2GE020EN-05_Microgrid.pdf ; https://clients.sketchfab.com/schneider/ecc/index.html | Tài liệu hãng (IEC) + trang demo ECC | "plan updated from the cloud application every 15 minutes" (một kết quả) | Low–Med | Lượt tìm khác không thấy câu 15 phút | Plan 15 phút là hợp lý nhưng cần xác minh |
| L17 | EMA tài sản: PV, tải, EV, HVAC, pin, CHP, genset gas; lệnh qua quản lý EV/BMS; DR qua utility/aggregator | https://download.schneider-electric.com/doc/NRJED116726EN/Microgrid_control_solutions_for_commercial_buildings_and%20campuses_998-20112200_GMA-US.pdf | Brochure hãng | "Control orders… to existing managers… EV charging stations and building management systems" | Med–High | — | Tích hợp qua hệ quản lý con thay vì thay thế |
| L18 | IEC 62443 cho EcoStruxure Power: 4-2/4-1, kiến trúc 3-3 chứng nhận bên thứ ba | https://www.productinfo.schneider-electric.com/esxp_digital_apps_iec/transverse/English/BM_ESXP_DG_Transverse_Section_IEC_0001148082.xml/$/ESXP_DG_SYSD_Cyber_ISA_IEC_0001157270 | Tài liệu thiết kế hãng | "validated and certified by a third party according to IEC 62443-3-3" | Med | Phạm vi với EMA cloud chưa rõ | PR-B13 |
| L19 | EMO: PMS on-site trong ECC/MGCC; trình tự islanding | https://www.se.com/ca/en/product-range/65897 ; https://pv-magazine-usa.com/?p=16812 | Trang hãng + báo | islanding → phối hợp genset/PV → về lưới | Med | Grid-forming không xác nhận | PR-B12 |
| L20 | PME: chất lượng điện, transient, process impact alarm, ISO 50001; Modbus TCP với relay | https://www.se.com/sg/en/product-range/65404-ecostruxure-power-monitoring-expert/ ; https://product-help.schneider-electric.com/EcoStruxure/Power-Monitoring-Expert-2024/content/8_reference/glossary.htm | Trang + help hãng | "process impact alarms" | Med | — | PQ là module P2 |
| L21 | SICAM MGC: blackout detection, black start, SOC mgmt, dự báo, IEC 62898-2, giao thức IEC 60870-5/Modbus, genset dự phòng, thị trường | https://assets.new.siemens.com/siemens/assets/api/uuid:4b32eeee-ee7c-423e-94f1-ae6a4257a689/MicrogridControlBrochure.pdf ; https://assets.new.siemens.com/siemens/assets/api/uuid:159d6566-81b2-4055-974b-7acb5ec05fc7/SICAM-MGC-Brochure.pdf | Brochure hãng (ngày không rõ) | "algorithms fulfill IEC 62898-2" | Med–High | Edition IEC 62898-2: UNKNOWN | Checklist nhóm M |
| L22 | MGC tới ~2 GW; IEC 62443, IPSec, crypto chip; DR & dynamic load control | https://www.siemens.com/en-us/products/microgrids/sicam-microgrid-control/ ; https://www.siemens.com/zh-cn/products/microgrids/sicam-microgrid-control/ | Trang hãng | "IEC-62443 certification, IPSec encryption, and integrated crypto chip" | Med | Trang zh-tw ghi "2 MW" (lỗi gõ) | PR-B13 |
| L23 | Ứng dụng SICAM (MGC/PPC/DLM): IEC 61850 GOOSE ~70 ms cho load shedding | https://assets.new.siemens.com/siemens/assets/api/uuid:9c3aa6dc-3efa-4c27-9c59-ab2664a2b45c/04-var2022-hoermann-sicam-applications-mgc-ppc-dlm-pub.pdf | Slide partner day 2022 | GOOSE trigger 70 ms | Med | Không phải số của MGC | Load shedding nhanh thuộc protection, không thuộc cloud |
| L24 | MGMS: dự báo 7 ngày, unit commitment, load shed; bản hosted | https://img.microgridknowledge.com/files/base/ebm/microgridknowledge/document/2022/09/1663609280032-siemens_utility_microgrid_whitepaper.pdf?dl=1663609280032-siemens_utility_microgrid_whitepaper.pdf ; https://www.renewableenergyworld.com/power-grid/microgrid/siemens-introduces-microgrid-management-for-distributed-power-generation/ | Whitepaper 2022 + báo cũ | "short-term load forecasting… up to seven days" | Med | Trạng thái sản phẩm hiện hành chưa rõ | Horizon dự báo |
| L25 | Electrification X Load Management cho sạc EV (Aral) | https://www.arcweb.com/blog/siemens-launches-electrification-x-strengthening-siemens-xcelerator-portfolio-across-buildings ; https://www.automotiveworld.com/news/siemens-launches-electrification-x-strengthening-the-siemens-xcelerator-portfolio-across-buildings-electrification-and-grids/ | Báo/analyst 2024 | "remote control and dynamic load management" | Med | — | PR-B11 |
| L26 | OPTIMAX: lập lịch/dispatch DER cho phát điện/công nghiệp/thương mại; quyết định feed-in, mua lưới; pin, genset | https://new.abb.com/news/detail/10576/abb-launches-optimaxr-solutions-for-power-generation-industrial-and-commercial-companies ; https://energymanagement-calculator.abb.com ; https://new.abb.com/power-generation/energy-management | Tin hãng + trang hãng | "schedules and dispatches distributed energy resources" | Med | — | — |
| L27 | OPTIMAX 6.4 AI dự báo tải/phát/giá; triển khai on-prem/cloud/hybrid | https://www.motionandmechatronics.ca/product-news/ai-upgrade-to-abb-energy-man/ ; https://www.abb.com/global/en/company/innovation/news/optimax-energy-management ; https://www.gasworld.com/story/ai-upgrade-for-abb-energy-management-system/2139961.article | Báo ngành 6/2024 + trang hãng | "reduces day-ahead and intra-day nomination errors" | Med | — | Dự báo là module riêng có thể nâng cấp |
| L28 | e-mesh: EMS cho site/fleet, giám sát, ML, dự báo; Hitachi Energy 2021: EMS BESS + EV fleet; ABB bán Power Grids cho Hitachi 2020 | https://new.abb.com/news/detail/15680/abb-launches-unified-software-to-provide-single-view-of-microgrids-and-battery-energy-storage ; https://www.hitachienergy.com/news/press-releases/2021/11/hitachi-energy-releases-global-updates-to-grid-edge-solutions-port-folio-including-new-services ; https://new.abb.com/news/detail/64657/abb-completes-divestment-of-power-grids-to-hitachi | Tin hãng 2019/2021/2020 | "applicable for premises or for fleets" | Med | Không nguồn nói thẳng e-mesh chuyển sang Hitachi | Ghi đúng chủ sở hữu khi so sánh |
| L29 | ABB Energy and Asset Manager: widget năng lượng, PF, PQ, Group Peak; báo cáo email; cảnh báo 24/7 | https://new.abb.com/about/our-businesses/electrification/abb-ability/energy-and-asset-manager/abb-ability-energy-and-asset-manager-for-manufacturing | Trang hãng (~2020) | "Group Peak Monitoring" | Med | — | Widget so sánh nhóm site |
| L30 | ONE for C&I: PV+BESS+EV+tài sản tòa nhà; biểu giá+thời tiết; module-level, digital twin; peak shaving nâng cao; thị trường; remote troubleshooting; live alerts | https://www.solaredge.com/us/solaredge-one-for-commercial-and-industrial-energy-optimization-platform ; https://www.businesswire.com/news/home/20241203224482/en ; https://www.nacleanenergy.com/solar/energy-optimization-solution-for-commercial-and-industrial-sites | Trang hãng + PR 2024 | "utility rates and weather forecasts" | High | — | Chuẩn so sánh trực tiếp |
| L31 | ONE Overview: lõi miễn phí cho người mua phần cứng, gói trả phí dần; ONE Controller hỗ trợ công tơ/cảm biến bên thứ ba | https://knowledge-center.solaredge.com/sites/kc/files/se-one-for-c&i-overview.pdf | Tài liệu hãng | "paid software packages… introduced gradually" | Med–High | — | Định giá: không cạnh tranh dashboard miễn phí |
| L32 | Site Admin: roles, Monitoring Access, Kiosk, Public, API Access, cảnh báo theo user; shutdown alerts | https://knowledge-center.solaredge.com/sites/kc/files/se-site-admin-in-solaredge-one-for-c&i-user-guide.pdf | User guide v1.1 | "Expose to alerts notifications" | High | Có thể khác bản mới | PR-B09 |
| L33 | Wevo: EV đa hãng, billing, ưu tiên, quản lý tải dự báo | https://www.pv-magazine.com/2024/04/05/solaredge-acquires-ev-charging-optimization-and-management-startup/ ; https://www.pv-tech.org/solaredge-acquires-ev-charging-software-startup-wevo/ | Báo 4/2024 | "vendor-agnostic… predictive load management" | Med–High | — | PR-B11 |
| L34 | CLC1: 2×RS485, CAN, 2×RJ45, Wi‑Fi 6, BLE 5.3, 4DI/4DO; Modbus TCP 1502; register map; công tơ Modbus RS485 | https://knowledge-center.solaredge.com/sites/kc/files/se-one-controller-commercial-and-industrial-datasheet-eng.pdf ; https://knowledge-center.solaredge.com/sites/kc/files/se-one-controller-for-cni-user-guide-im.pdf ; https://www.solarmarkt.ch/herstimg/50-Speichersysteme/SolarEdge/MA_EN_SolarEdge_One_Controller.pdf | Datasheet + user guide v1.6 (6/2026), v1.0 (5/2025) | "Modbus TCP on port 1502" | High | Không thấy LTE (≠ không hỗ trợ) | Spec gateway edge |
| L35 | Export limitation: công tơ tại điểm đấu nối; công tơ tiêu thụ không hỗ trợ | https://knowledge-center.solaredge.com/sites/kc/files/feed-in_limitation_application_note.pdf | App note v3.0 8/2026 | "Consumption meters are not supported in export limitation use cases" | High | Phạm vi inverter/gateway, chưa rõ ONE Controller | `pcc_meter_id` bắt buộc |
| L36 | Huawei C&I SmartPVMS: SmartEMO tự chỉnh peak shaving theo lịch sử; cell-level SOC/SOH; I-V; module-level 60 MW | https://solar.huawei.com/fr/products/ci-smart-pv-management-system/ | Trang hãng (nghiên cứu trước) | "automatic peak-shaving adjustment from historical data" | Med–High | — | Đối thủ trực tiếp ở VN |
| L37 | SmartLogger5000B: zero-export ≤2 s, peak shaving ≤5 s; peak shaving chỉ on/off-grid PQ/VSG; ≤20 ESS/30 inverter | https://www.photomate.eu/smartlogger5000b ; https://ske-solar.com/fileadmin/user_upload/UserManual_LUNA2000-_107-215__C_I-Microgrid-SmartLogger3000_V07_2025-11-30_EN.pdf ; https://ske-solar.com/fileadmin/user_upload/QuickGuide_C_I_On-Grid_ESS__Based_on_215KWH_Series_ESS__V01_2024-08-12_EN.pdf | Nhà phân phối + bản sao manual Huawei 2024–2025 | "closed-loop control for zero feed-in within 2s" | Med | Mirror, không phải trang Huawei | Mục tiêu thời gian đáp ứng edge |
| L38 | EMMA-A02: peak shaving, ưu tiên PV, giới hạn feed-in, diesel, dự báo dư PV giữ SOC | https://solar.huawei.com/en/products/EMMA | Trang hãng | "forecasts your surplus PV power and executes… ESS SOC space reserve" | High | Nhắm hộ gia đình/thương mại nhỏ | — |
| L39 | Huawei NB API: async control, chỉ OAuth Connect; quota; vai trò installer/owner; dữ liệu 5 phút, 15 tháng EU | https://support.huawei.com/enterprise/en/doc/EDOC1100379184/7a471100/control-apis ; https://www.vpsolar.com/en/huawei-fusionsolar-softwares-app-and-smartpvms-portal/ ; https://solytic.com/knowledge/set-up-api-access-huawei-fusionsolar-api/ | Tài liệu hãng (nghiên cứu trước, 2024–2025) | "available only in OAuth Connect mode" | High | — | PR-B04 |
| L40 | SICAM SCC trên WinCC, server dự phòng; chứng chỉ WinCC OA IEC 62443-4-1/4-2 hiệu lực tới 2026-02-06 | https://assets.new.siemens.com/siemens/assets/api/uuid:4eec54f8-04a2-48cf-9d0d-266a8dcd97e7/SICAM-SCC.pdf ; https://www.winccoa.com/documentation/WinCCOA/3.20/en_US/iec_62443/topics/iec_62443_certification.html | Brochure + trang chứng chỉ | validity end 2026-02-06 | Med | Gia hạn chưa rõ | Theo dõi hạn chứng chỉ |
| L41 | Sungrow PowerStack 255CS: EMS/PCS/BMS tích hợp; VPP, demand control, VSG, backup, black start; Modbus TCP cho EMS bên thứ ba; 25/10 tủ; diesel sync (2026) | https://www.ess-news.com/2025/04/15/sungrow-launches-fully-integrated-ci-battery/ ; https://www.vpsolar.com/en/sungrow-powerstack-bess-solutions-for-ci-solar-installations/ ; https://www.sungrowpower.com/mal/en/products/c-i-energy-storage-system/st255cs-2h ; https://renewablewatch.in/2026/07/10/sungrow-unveils-solar-storage-solution-powerstack/ ; https://www.vicoexport.com/en/powerstack | Báo + nhà phân phối + trang hãng 2025–2026 | "Modbus TCP… with EMS300CP or a third-party EMS" | Med | <20 ms chỉ từ nhà phân phối | PR-B08 |
| L42 | iSolarCloud: 5 phút, thiết bị đa loại; Open API keys; firmware cũ bỏ qua giới hạn P; phân quyền phân cấp | https://info-support.sungrowpower.com/application/pdf/2024/04/18/DS_20240417_iSolarCloud_Datasheet_V3_EN.pdf ; https://docs.eniris.com/nl/Controller/Devices/Cloud/ISolarCloud ; https://community.home-assistant.io/t/sungrow-isolarcloud-integration-custom-hacs-sensors-optional-charge-discharge-control/1017858 | Datasheet 4/2024 + docs bên thứ ba + community (nghiên cứu trước + mới) | "some older Sungrow firmwares don't respect active power limits" | Med (community: Low) | — | PR-B07 |
| L43 | OpenEMS Edge/Backend/UI; PeakShaving, Balancing `targetGridSetpoint`; JSON-RPC/WebSocket, apikey, Metadata Odoo/File, edgeRpc; ModbusTcp API; điều khiển qua Power Solver | https://openems.github.io/openems.io/openems/latest/edge/architecture.html ; https://github.com/OpenEMS/openems/tree/develop/io.openems.edge.controller.ess.balancing ; https://community.openems.io/t/edge-backend-interface/587/2 ; https://community.openems.io/t/ess-that-can-talk-with-openems-using-modbus-tcp/1029 | Docs + repo + forum | "balanced to 0 Watt… targetGridSetpoint" | High (docs) / Med (forum) | Tài liệu Edge-Backend mỏng | PR-B03, PR-B16 |
| L44 | OpenEMS ToU Tibber 15 phút (2025.11.0); GridOptimizedCharge (2026.4.0); module OCPP server; file license EPL-2.0 + AGPL-3.0 | https://zenodo.org/records/17481747 ; https://zenodo.org/records/19374309 ; https://github.com/OpenEMS/openems ; https://git.rz.uni-jena.de/winner-reloaded/openems/-/tree/a45ce897d760f05fe953750744ff887f6c4947cb/io.openems.edge.timeofusetariff.tibber | Release notes + repo | "switch to QUARTER_HOURLY prices" | Med–High | Cách áp license chưa rõ | Slot 15 phút |
| L45 | OpenEMS §14a EnWG reference với Fraunhofer ISE + FENECON | https://www.bayern-innovativ.de/en/emagazine/detail/open-source-software-is-intended-to-simplify-network-management/ | Bài báo 6/2026 | "reference implementation… Section 14a" | Med | — | Hook tín hiệu lưới (PR-B14) |
| L46 | Stem PowerTrack EMS: portfolio + PPC + SCADA + edge UI + unit controller không phụ thuộc phần cứng; C&I+utility; −32% giờ kỹ sư, 99,99% | https://www.businesswire.com/news/home/20250902991311/en ; https://s27.q4cdn.com/138752898/files/doc_news/Stem-Launches-PowerTrack-EMS-Expanding-Global-Product-Suite-for-Standalone-and-Hybrid-Energy-Storage-Control-2025.pdf ; https://s27.q4cdn.com/138752898/files/doc_news/Stem-Inc--Letter-to-Shareholders--Reflecting-on-our-journey-of-strategic-realignment-2025.pdf | PR 9/2025 + thư cổ đông | "hardware-agnostic unit controllers" | Med–High (số liệu: Low) | FY2025: định vị chính cho utility | Template cấu hình site |
| L47 | Athena: tối ưu hóa đơn, điều chỉnh sạc/xả, thuật toán dự đoán, EV | https://www.stem.com/?p=25654 | Trang hãng | "predictively maximize savings" | Med | Demand charge chỉ từ rfp.wiki (Low) | PR-B15 |
| L48 | AlsoEnergy PowerTrack: 8.000+ driver, Modbus TCP/RTU, báo cáo mẫu, fault detection | https://www.stem.com/?p=29316 ; https://home.alsoenergy.com/resources/flier-alsoenergy-powertrack | Trang hãng (nghiên cứu trước) | "8,000+ drivers and point maps" | Med–High | — | PR-B08 |
| L49 | GridBeyond: 400+ site C&I; AI dự báo/tối ưu/dispatch, mô hình suy giảm; ViewPoint Lens | https://secure.businesswire.com/news/home/20250930978130/en/GridBeyond-Launches-ViewPoint-Lens-to-Empower-Energy-Customers-With-Greater-Visibility-and-Control ; https://solarimpulse.com/companies/gridbeyond ; https://solarimpulse.com/companies_file/gridbeyond.com-1.pdf | PR 9/2025 + hồ sơ do hãng cung cấp | "respects asset-level constraints and degradation models" | Med | — | PR-B15 |

(49 dòng; vượt mức 40 vì cần mọi ô Verified có URL.)

---

## 6. Câu hỏi mở / UNKNOWN

- Q-B1 [UNKNOWN] Nội dung trang https://www.infinitepowerht.com/what-is-energy-management-system-ems-and-its-functions.html do người dùng cung cấp — không xuất hiện trong kết quả tìm kiếm. Cần người dùng dán nội dung hoặc mở mạng.
- Q-B2 [UNKNOWN] Ampowr Cosmos: giao thức thiết bị, Partner API (endpoint, auth), độ phân giải dữ liệu, phân quyền, phương pháp dự báo.
- Q-B3 [UNKNOWN] HT Infinite Power: bảng register Modbus/CAN, tên cloud, API, chứng chỉ. Hỏi trực tiếp nếu là nhà cung cấp tiềm năng ở VN.
- Q-B4 [UNKNOWN] Schneider EMA: chu kỳ cập nhật kế hoạch thực tế (15 phút?), danh sách giao thức DER, phạm vi IEC 62443 cho cloud, hiện còn bán dưới tên nào (sau EcoStruxure Microgrid Flex?).
- Q-B5 [UNKNOWN] Siemens MGC: số chứng chỉ IEC 62443 và hạn; edition IEC 62898-2; tình trạng MGMS/DEOP hiện nay.
- Q-B6 [UNKNOWN] "ABB Ability Microgrid" không tìm thấy là tên sản phẩm. ABB hiện có EMS C&I nào ngoài OPTIMAX/EAM không?
- Q-B7 [UNKNOWN] SolarEdge ONE Controller: điều khiển pin bên thứ ba? hành vi khi mất Internet? có LTE? chứng chỉ bảo mật? giới hạn API V2 OAuth?
- Q-B8 [UNKNOWN] Sungrow: tài liệu chính thức về cấu hình chiến lược EMS trong iSolarCloud, Open API control endpoint.
- Q-B9 [UNKNOWN] OpenEMS: giấy phép áp dụng cho Edge vs UI vs Backend (EPL-2.0 vs AGPL-3.0) — ảnh hưởng quyết định dùng làm nền edge.
- Q-B10 [UNKNOWN] Không sản phẩm nào công bố số liệu độ trễ end-to-end cloud→thiết bị; chỉ Huawei công bố độ trễ vòng tại site.
- Q-B11 [UNKNOWN] Giá: không hãng nào trong phiên này công bố giá EMS (trừ "lõi miễn phí" SolarEdge).
- Q-B12 [UNKNOWN] Victron VRM, Deye/Solarman C&I EMS, Growatt C&I — chưa đánh giá, có thể phổ biến ở VN.

---

## 7. Vấn đề gửi agent khác

- → **Tổng hợp / chủ `03-functional-catalog`**: xác nhận tên 13 nhóm A–M; ma trận ở 3.12 đang dùng ánh xạ ở 1.2. Nếu khác, cần đổi nhãn hàng.
- → **Agent thị trường VN / biểu giá (M-TAR)**: VN có cơ chế DR, thị trường phụ trợ hay aFRR cho C&I không? Ảnh hưởng ưu tiên PR-B14. Biểu giá EVN 3 khung giờ + demand charge (có hay không với C&I?) cần xác nhận để định nghĩa "peak shaving" mang lại tiền gì.
- → **Agent tích hợp thiết bị (07)**: ưu tiên driver Sungrow Modbus TCP (EMS bên thứ ba được hãng hỗ trợ chính thức, L41), SolarEdge Modbus TCP 1502 (L34), Huawei qua SmartLogger/EMMA (lưu ý ràng buộc 1 Modbus client ở dongle — nghiên cứu trước), tủ BESS Trung Quốc (template register). Ghi quirk Sungrow firmware (L42).
- → **Agent tối ưu (08)**: thời gian tham chiếu — plan 15 phút, horizon 48 h fallback (Schneider), vòng PCC 2 s/5 s (Huawei). Không gọi luật/lịch cố định là AI. Mô hình suy giảm pin được GridBeyond nêu (L49) — cân nhắc đưa chi phí suy giảm vào hàm mục tiêu.
- → **Agent kiến trúc (06)**: mẫu "một bộ phân xử công suất duy nhất ở edge" (OpenEMS Power Solver, L43) và API lệnh async (Huawei, L39). Đánh giá OpenEMS Edge như nền (license, Q-B9).
- → **Agent bảo mật (10)**: chỉ tuyên bố chứng nhận khi có số chứng chỉ, phạm vi, hạn (bài học WinCC OA hết hạn 2026-02-06, L40). Tách WAN/LAN ở edge như CLC1.
- → **Agent UX (09)**: tham khảo phân quyền chia sẻ SolarEdge (Kiosk, Public, API, cảnh báo theo user — L32); báo cáo "giá trị đã tạo" (GridBeyond ViewPoint Lens, Stem Athena); hiển thị trạng thái "đang chạy lịch dự phòng".
- → **Chủ `14-source-register`**: toàn bộ URL ở mục 5 cần cấp mã S-xxx; đánh dấu nguồn "qua kết quả tìm kiếm" và nguồn rfp.wiki là Low.
- → **Ghi chú tính nhất quán**: nghiên cứu FusionSolar trước (competitors_rebuild.md) ghi SolarEdge ONE C&I là "fleet management, PV+storage+EV+building" — khớp với file này; không có mâu thuẫn. Kết luận "edge-first" của dự án cũ được củng cố, không đổi hướng.
