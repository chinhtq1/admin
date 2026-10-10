# 04 — Yêu cầu nghiệp vụ EMS C&I đa site, đa hãng

[← Mục lục](index.html) · [00 Tóm tắt](00-executive-summary.html) · [03 Chức năng](03-functional-catalog.html) · [05 Domain](05-domain-model.html) · [06 Kiến trúc](06-system-architecture.html) · [07 Tích hợp](07-device-integration.md) · [08 Tối ưu](08-energy-optimization.md) · [09 UX/UI](09-ux-ui-specification.html) · [10 An toàn](10-security-and-reliability.md) · [11 Lộ trình](11-mvp-and-roadmap.html) · [12 Truy vết](12-traceability-matrix.md) · [13 Rủi ro](13-open-questions-and-risks.md) · [14 Nguồn](14-source-register.md)

| Thuộc tính | Giá trị |
|---|---|
| Tài liệu | 04 · Yêu cầu nghiệp vụ (Business Requirements) |
| Người viết | Agent D (Functional Business Analyst) |
| Phiên bản | 1.0 |
| Ngày | 2026-10-10 |
| Trạng thái | Bản nháp vòng 1. Đã áp toàn bộ "Danh sách quyết định thống nhất" của Evidence Judge ([K-review-round1 §6](notes/K-review-round1.md)). **Chưa được phát hành ra ngoài**: K §5 G-13 yêu cầu kiểm chứng pháp lý và giấy phép trước khi phát hành 04 (xem §9.3). |
| Neo mã | Mã tính năng `F-<MODULE>-NN` lấy nguyên từ [03 Danh mục chức năng](03-functional-catalog.html). Tài liệu này cấp mã chính thức `FR-<MODULE>-NNN`, `BR-<MODULE>-NN`, `NFR-<NHÓM>-NNN`. |

---

## Mục lục

- [0. Cách đọc tài liệu](#0-cách-đọc-tài-liệu)
- [1. Phạm vi và nguyên tắc ràng buộc](#1-phạm-vi-và-nguyên-tắc-ràng-buộc)
- [2. Tham số mặc định dùng trong tiêu chí chấp nhận](#2-tham-số-mặc-định-dùng-trong-tiêu-chí-chấp-nhận)
- [3. Persona, vai trò và quyền](#3-persona-vai-trò-và-quyền)
- [4. Hành trình end-to-end và luồng nghiệp vụ liên module](#4-hành-trình-end-to-end-và-luồng-nghiệp-vụ-liên-module)
- [5. Yêu cầu theo module](#5-yêu-cầu-theo-module)
  - [5.1 M-ORG](#51-m-org--tổ-chức-site-tài-sản-người-dùng) · [5.2 M-DASH](#52-m-dash--dashboard-danh-mục-và-site) · [5.3 M-MON](#53-m-mon--giám-sát-thời-gian-thực) · [5.4 M-HIST](#54-m-hist--lịch-sử-chất-lượng-dữ-liệu-phân-tích) · [5.5 M-REP](#55-m-rep--báo-cáo-xuất-dữ-liệu-bằng-chứng) · [5.6 M-TAR](#56-m-tar--biểu-giá-lịch-tou-hóa-đơn-bóng) · [5.7 M-BESS](#57-m-bess--quản-lý-bess-supervisory) · [5.8 M-PV](#58-m-pv--pv-hiệu-suất-chẩn-đoán-giới-hạn-phát) · [5.9 M-GRID](#59-m-grid--điểm-đấu-nối-công-tơ-tuân-thủ-lưới-phụ-tải) · [5.10 M-EV](#510-m-ev--sạc-xe-điện) · [5.11 M-OPT](#511-m-opt--tối-ưu-lập-lịch-điều-phối) · [5.12 M-ALM](#512-m-alm--cảnh-báo-om-ticket-work-order) · [5.13 M-INT](#513-m-int--tích-hợp-thiết-bị-edge-api-commissioning) · [5.14 M-SEC](#514-m-sec--bảo-mật-an-toàn-lệnh-tuân-thủ) · [5.15 M-ADV](#515-m-adv--nâng-cao-dự-báo-mô-phỏng-ml)
  - [5.16 Tính năng ngoài phạm vi và bị cấm](#516-tính-năng-ngoài-phạm-vi-và-bị-cấm)
- [6. Yêu cầu phi chức năng](#6-yêu-cầu-phi-chức-năng)
- [7. Truy vết mã tạm và độ phủ](#7-truy-vết-mã-tạm-và-độ-phủ)
- [8. Vấn đề gửi agent khác](#8-vấn-đề-gửi-agent-khác)
- [9. Câu hỏi mở, điều kiện phát hành và nguồn](#9-câu-hỏi-mở-điều-kiện-phát-hành-và-nguồn)

---

## 0. Cách đọc tài liệu

### 0.1 Mã định danh

| Mã | Ý nghĩa | Phạm vi |
|---|---|---|
| `F-<MODULE>-NN` | Tính năng trong [03](03-functional-catalog.html). Không đổi, không cấp mới ở đây. | Từ 03 |
| `FR-<MODULE>-NNN` | Yêu cầu chức năng chính thức. Mỗi FR trỏ về ≥ 1 `F-`. | **Cấp ở 04** |
| `BR-<MODULE>-NN` | Quy tắc nghiệp vụ (ràng buộc luôn đúng, không phải hành vi một màn hình). | **Cấp ở 04** |
| `NFR-PERF/REL/DATA/OBS/SEC-NNN` | Yêu cầu phi chức năng. Chi tiết bảo mật ở [10](10-security-and-reliability.md). | **Cấp ở 04** |
| `US-<MODULE>-NN` | User story. Mã cục bộ của 04. | Cục bộ |
| `WF-NN` | Luồng nghiệp vụ liên module (§4). Mã cục bộ của 04. | Cục bộ |
| `AC-<MODULE>-NN` | Tiêu chí chấp nhận dạng Given/When/Then. Ma trận 12 sẽ sinh `T-<FR id>` từ đây. | Cục bộ |
| `GAP-NN`, `Q-xx`, `R-xx` | `GAP-NN` là mã tạm của 03 §9. `Q-A01`, `Q-C02`… là mã tạm trong ghi chú. 13 cấp `Q-NN`/`R-NN` chính thức. | Tham chiếu |
| Mã tạm trong ghi chú | `FR-OPT-0xx` (G), `NFR-SEC-0xx` (I), `F-Pxx`, `C-Pxx`, `H-Pxx`, `PR-E-xx`, `PR-B-xx`, `D-xx` là **mã tạm** (K §6 #38). Bảng ánh xạ sang mã chính thức ở §7. **Chú ý:** `FR-OPT-004` của G **khác** `FR-OPT-004` của tài liệu này. | §7 |

### 0.2 Ưu tiên, phát hành, cổng điều khiển

- **Ưu tiên ⇔ phát hành** (theo 03 và K §6 #40): `P0` ⇔ MVP · `P1` ⇔ Later (Phase 1) · `P2` ⇔ Later (Phase 2). "CẤM" = hạng lệnh C4, không có API ở bất kỳ phiên bản nào.
- **Gate** (K §6 #27): **M1** = giám sát đa hãng + cấu hình và kiểm chứng chế độ **native** có readback. **M2** = edge của ta làm chủ vòng (`control_owner = EDGE`) và gửi setpoint/lịch. Cả M1 và M2 nằm trong MVP; M2 chỉ bật **theo từng site** khi đạt bộ an toàn P0 (FR-SEC-021).
- **Hạng lệnh** (K §6 #28): C0 thông tin · C1 thường · C2 nhạy cảm (step-up MFA + lý do) · C3 nguy hiểm (hai người duyệt) · C4 cấm (không có API). Ghi trong FR là **hạng tối thiểu**; PDP có thể nâng hạng theo ngữ cảnh (BR-SEC-03).
- Cột "Hạng·Gate" trong bảng FR: ví dụ `C1·M1`. FR không tác động vật lý ghi `—`.

### 0.3 Nhãn bằng chứng

- Mọi FR, BR, NFR là `[PROPOSAL]` cho sản phẩm của ta. Cột "Căn cứ" nêu loại căn cứ: quyết định K (`K §6 #n`), ghi chú nghiên cứu (`E §3.19`…), hoặc nguồn ngoài. Bằng chứng ngoài được trích bằng URL trong mục "Bằng chứng và độ tin cậy" của từng module với nhãn `[FACT]`, `[INFERENCE]`, `[UNKNOWN]`.
- Mọi FACT mới trong dự án được ghi nhận **qua kết quả tìm kiếm** (snippet) của các agent nghiên cứu hoặc nghiên cứu FusionSolar trước; tài liệu này không mở trực tiếp URL nào và không có lượt tìm kiếm mới (hạn mức tìm kiếm chung đã hết, K mục đầu). Do đó độ tin cậy tối đa của FACT là "Trung bình".
- Số liệu mặc định (ngưỡng, thời gian) là `[PROPOSAL]` trừ khi ghi khác. Số nào cần PoC hoặc kiểm chứng được đánh dấu ở §2.

### 0.4 Quy ước câu chữ

- "Hệ thống phải…" = bắt buộc. "Nên…" = khuyến nghị, không chặn nghiệm thu.
- "Edge" = edge gateway của ta tại site. "Cloud" = nền tảng SaaS. "Native" = controller/logger/EMS của hãng thiết bị.
- Dấu và đơn vị theo K §6 #4–#6: lưới `+` = nhập, BESS `+` = xả, PV/tải/EV/máy phát `≥ 0`; Q cùng hướng với P của từng điểm đo; raw W/Wh/var/VA (bộ đếm int64 Wh), aggregate/KPI/API kW/kWh, tên trường có hậu tố đơn vị. UI hiển thị số không dấu kèm chữ hướng (Nhập/Xuất/Sạc/Xả/Chờ).

---

## 1. Phạm vi và nguyên tắc ràng buộc

### 1.1 Định vị sản phẩm

- **Nhóm sản phẩm:** nền tảng quản lý năng lượng C&I behind-the-meter, đa site, đa hãng, xây trên lớp giám sát/O&M. Người mua chính là tổ chức vận hành (installer/O&M/ESCO). Chủ C&I là người xem báo cáo. [PROPOSAL] (K §6 #1)
- **Site chỉ có PV là công dân hạng nhất.** BESS và EV là tùy chọn. Điều khiển EV là P1. [PROPOSAL] (K §6 #2)
- **Thứ tự giá trị ở Việt Nam** dùng để xếp ưu tiên yêu cầu: (1) tuân thủ giới hạn xuất/trần nhập, (2) minh bạch chi phí theo TOU, (3) O&M đa hãng, (4) tối ưu BESS. Peak shaving theo demand charge là P1. [INFERENCE] (K §6 #3; A §3.4)
- **Ngoài phạm vi 12–18 tháng:** nền tảng ESG/carbon, SCADA/EMS cấp lưới, chuyển đảo/black start, giao dịch thị trường điện (§5.16). [PROPOSAL] (K §6 #1)

### 1.2 Thay đổi so với hướng FusionSolar trước

Nghiên cứu trước ([../fusionsolar/README.md](../fusionsolar/README.md)) đề xuất nền tảng **giám sát/O&M PV đa hãng, edge-first, chỉ đọc**. Tài liệu này giữ toàn bộ lớp đó (M-MON, M-HIST, M-ALM, M-PV) và mở rộng có chủ đích:

| Điểm | Hướng cũ | Hướng EMS | Lý do |
|---|---|---|---|
| Ghi xuống thiết bị | Không (đọc chế độ hãng) | Có, qua hai cổng M1/M2, tắt mặc định theo site | Khung cao điểm tối QĐ 963 chuyển giá trị sang BESS cần lập lịch; zero-export phổ biến (G §4 "Khác hướng cũ") |
| Tần suất dữ liệu | 1–5 phút | Edge 1 s; cloud 5 s/60 s/300 s; thanh ghi mỗi biên 5 phút | Zero-export và BESS cần dữ liệu nhanh hơn mức 5 phút của FusionSolar (K §6 #19) |
| Quy ước dấu lưới | `+` = xuất (theo FusionSolar) | `+` = nhập | Năm agent đồng thuận, khớp OBIS A+ và OpenEMS (K R-01) |
| Mô hình quyền | Company tree + Role + DataScope | Giữ nguyên cho giám sát; thêm ABAC/PDP, phê duyệt, ký lệnh cho điều khiển | Lệnh có tác động vật lý (I §4) |
| Edge | Khuyến nghị | **Bắt buộc** ở site có lệnh; site chỉ giám sát dùng connector cloud chỉ đọc | Cloud API hãng là pull 5 phút có hạn mức (K R-09) |

### 1.3 Nguyên tắc an toàn không thương lượng

Các nguyên tắc dưới đây là ràng buộc cho **mọi** FR. Vi phạm một nguyên tắc là lỗi chặn phát hành.

1. **Cloud không bao giờ nằm trong vòng bảo vệ và không ghi trực tiếp vào thiết bị.** Cloud gửi ý định/lịch có hạn; edge arbiter + limit chain quyết định setpoint (K §6 #14).
2. **Không có API sửa thông số bảo vệ** (grid code, ngưỡng BMS, rơ-le) và **không có E-stop từ xa** (C4, K §6 #14, #28).
3. **Mọi lệnh có hạn** (`expires_at` bắt buộc), có chữ ký, có readback trước khi báo "đã áp dụng" (K §6 #21).
4. **Điều khiển mặc định TẮT theo site**; bật là thao tác C3 sau commissioning và có đồng ý của chủ tài sản (K §6 #26).
5. **Một vòng trên một biến:** `control_owner ∈ {NATIVE, EDGE}`, ưu tiên native (K §6 #15).
6. **Thứ tự arbiter 12 mức cố định ở mức 1–6** (K §6 #16): (1) bảo vệ native · (2) interlock tại chỗ · (3) giám sát an toàn edge · (4) tuân thủ lưới · (5) trần nhập vật lý · (6) dự phòng backup · (7) lệnh tay · (8) DR/VPP · (9) peak shaving demand · (10) cam kết EV · (11) lịch kinh tế · (12) chiến lược mặc định.
7. **Không gọi là AI/ML** thứ không phải mô hình học đã đánh giá; số ước tính/mô phỏng luôn có nhãn (K §6 #33).
8. **Không tuyên bố tuân thủ tiêu chuẩn** khi chưa có chứng chỉ hoặc chưa đối chiếu văn bản; không quảng cáo % tiết kiệm (K §6 #34).
9. **Không gán tính năng chưa có tài liệu cho hãng**; không bao giờ ghi "tương thích mọi inverter/BESS" (K §6 #35).
10. **Không bao giờ hiển thị 0 thay cho "không có dữ liệu"** (K §6 #9).

---

## 2. Tham số mặc định dùng trong tiêu chí chấp nhận

Tiêu chí chấp nhận ở §5 tham chiếu các tham số dưới đây bằng tên. Giá trị là mặc định của sản phẩm; nhiều tham số cấu hình được theo site trong SOE hoặc cấu hình tenant. Cột "Trạng thái" ghi `PoC` khi số cần đo thực tế và `UNKNOWN` khi phụ thuộc văn bản chưa kiểm chứng.

| Nhóm | Tham số | Mặc định | Căn cứ | Trạng thái |
|---|---|---|---|---|
| Lấy mẫu | `edge_sample_period` | 1 s cho điểm điều khiển | K §6 #19 | PROPOSAL |
| Lấy mẫu | Lớp cloud C1 / C2 / C3 | 5 s / 60 s / 300 s hoặc khi đổi; thanh ghi ở mọi biên 5 phút; sự kiện tức thời | K §6 #19; F §3.1.2 | PROPOSAL |
| Độ tươi | `freshness` LIVE / DELAYED / OLD | tuổi ≤ 2× / ≤ 5× / > 5× chu kỳ mong đợi của nguồn. Ví dụ C1: ≤ 10 s / ≤ 25 s / > 25 s; C2: ≤ 120 s / ≤ 300 s / > 300 s; connector cloud 5 phút: ≤ 10 phút / ≤ 25 phút / > 25 phút | H §3.13; K R-06 | PROPOSAL |
| Độ tươi | `OFFLINE` | heartbeat edge mỗi 30 s; OFFLINE sau 3 heartbeat lỡ (≈ 90 s) | I §3.8 | PROPOSAL |
| Độ tươi | `point.max_age_s` | 3 × chu kỳ poll của điểm → `UNCERTAIN_STALE` | E §3.18 | PROPOSAL |
| Cảnh báo kết nối | `T_offline_alarm_edge` | 5 phút | I §3.9 | PROPOSAL |
| Cảnh báo kết nối | `T_offline_alarm_connector` | 30 phút (≥ 3 chu kỳ pull 5 phút + trễ hãng) | Đề xuất của 04 (khác ví dụ "10 phút" ở F §3.13 vì nguồn cloud hãng trễ tự nhiên) | PROPOSAL |
| An toàn edge | `T_stale_bms` | 5 s | I §3.7.2; C §3.7 | PROPOSAL, chỉnh trong SOE |
| An toàn edge | `T_stale_poc` | 3 s (= 3 chu kỳ 1 s) | Đề xuất của 04 (E §3.13 ghi "N giây") | PROPOSAL, chỉnh 2–5 s trong SOE |
| Đồng hồ | `clock_state` | SYNCED: \|offset\| < 100 ms; DEGRADED: < 1 s; UNSYNCED: còn lại | E §3.17 | PROPOSAL |
| Lệnh | `expires_at` setpoint | mặc định 15 phút, tối đa 1 h | K §6 #21 | Quyết định K |
| Lệnh | `expires_at` override chế độ (`SET_ESS_MODE`) | tối đa 24 h | I §3.7.5 | PROPOSAL |
| Lệnh | `expires_at` lịch (`APPLY_SCHEDULE`) | horizon ≥ 48 h, hạn tối đa 7 ngày | K §6 #17, #21 | Quyết định K |
| Lệnh | `max_latency_ms` | setpoint 10 000; chế độ 30 000; lịch 300 000; C3 sau duyệt 10 000 | I §3.7.5 | PROPOSAL |
| Lệnh | Timeout readback | setpoint 10 s; chế độ 30 s; C3 30 s; hoặc theo `capability_profile` nếu dài hơn | I §3.7.5 | PROPOSAL |
| Lệnh | Bảng `command_id` đã thấy tại edge | giữ tới `expires_at` + 24 h | E §3.19 | PROPOSAL |
| Phê duyệt | Cửa sổ duyệt C3 | ≤ 15 phút; lệnh đã duyệt phải tới edge ≤ 30 phút sau duyệt | I §3.7.4–3.7.5 | PROPOSAL |
| Xác thực | Step-up MFA | `auth_time` ≤ 5 phút trước lệnh C2/C3 | I §3.3 | PROPOSAL |
| Xác thực | Phiên web | idle 30 phút, tuyệt đối 12 h; access token 5–10 phút | I §3.3 | PROPOSAL |
| Nâng hạng | Ngưỡng C2 | setpoint > 80% giới hạn SOE; giảm `SOC_backup_reserve`; tắt tối ưu; lệnh tới > 5 site; ngoài giờ hành chính (mặc định 08:00–17:00 T2–T6 giờ site, cấu hình theo tenant) | I §3.7.4 | PROPOSAL |
| Nâng hạng | Ngưỡng C3 | `DEVICE_ON_OFF`; đổi SOE; bật/tắt `control_enabled`; `SET_REVERSE_FEED_BLOCK` thủ công; xả/sạc cưỡng bức bỏ qua tối ưu > 30 phút; lệnh tác động > 10% MW BESS của tenant; reset lỗi; cập nhật firmware edge; bật lại kill switch | I §3.7.4 | PROPOSAL |
| Tốc độ | Giới hạn lệnh | thiết bị ≤ 1 setpoint/2 s từ edge; site ≤ 6 lệnh thủ công/phút và ≤ 12 đổi chế độ/giờ; người dùng ≤ 30 lệnh/10 phút; `mode_change_min_interval` 300 s | I §3.7.2, §3.7.6 | PROPOSAL |
| Đội | Fleet Dispatch Governor | Σ\|ΔP\| được lệnh trong 5 phút ≤ 20% MW BESS của tenant; toàn nền tảng ≤ 5% tổng MW quản lý; jitter 0–300 s cho lệnh đồng loạt (trừ điều độ) | K §6 #30; I §3.7.6 | PROPOSAL, cần mô phỏng |
| Fallback | Lịch tại edge | ≥ 48 h; hết lịch → chiến lược mặc định của site | K §6 #17 | Quyết định K |
| Fallback | Watchdog thiết bị | `revert_timeout_s` 10–60 s và > 3 chu kỳ ghi của edge | I §3.9 | PROPOSAL, theo từng hãng (UNKNOWN Q-I-07) |
| Edge | Watchdog phần cứng | reset nếu vòng điều khiển treo > 10 s; khởi động `SAFE_START` ≥ 2 chu kỳ đọc trước khi ghi | I §3.8 | PROPOSAL |
| Edge | Buffer | không mất dữ liệu khi mất mạng ≤ 7 ngày (cứng); mục tiêu 30 ngày ở tần suất cloud; dữ liệu 1 s giữ vòng tròn 7 ngày | K §6 #18 | Quyết định K; 30 ngày cần PoC phần cứng |
| Edge | Chứng chỉ | X.509 hạn 90 ngày, tự gia hạn ở 2/3 hạn; gia hạn lỗi 14 ngày → cảnh báo | I §3.5 | PROPOSAL |
| Lưới | `export_violation_tol_w` | max(1.000 W; 1% công suất AC PV của site) | Đề xuất của 04 dựa trên margin của G §3.3(a) | PROPOSAL, chờ yêu cầu điện lực (UNKNOWN Q-A09) |
| Lưới | Sự kiện vi phạm xuất | P_xuất > `export_limit_w` + `export_violation_tol_w` liên tục ≥ 2 s (đo tại edge) | F §3.13 L1 | PROPOSAL |
| Lưới | Thời gian đáp ứng giới hạn xuất (test commissioning) | đạt ≤ 5 s; mục tiêu tham chiếu ≤ 2 s (số do Huawei tự công bố cho SmartLogger5000B/SmartMGC5000B) | K §6 #36; E §3.13 | PROPOSAL; không phải yêu cầu pháp lý đã kiểm chứng |
| Lưới | `T_import_alarm` | P_nhập > `import_cap_w` liên tục > 30 s | G §3.3(c) "T_alarm" | PROPOSAL |
| Biểu giá | Cửa sổ demand | 30 phút, block thẳng hàng :00/:30 | K §6 #24 | UNKNOWN (block hay rolling) |
| Biểu giá | Khung TOU mặc định | QĐ 963: cao điểm 17:30–22:30 T2–T7; thấp điểm 00:00–06:00; Chủ nhật không cao điểm; còn lại bình thường | K §6 #37 | UNKNOWN ngày áp vào hóa đơn (Q-A01) |
| Cảnh báo | Quy tắc mẫu | PV = 0 khi G_POA > 200 W/m² quá 15 phút | F §3.13 L1 | PROPOSAL |
| Cảnh báo | Tạm gác (shelve) | tối đa 8 h (cấu hình theo vai trò) | H §3.10 | PROPOSAL |
| Cảnh báo | Độ trễ thông báo | p95 sự kiện → thông báo ≤ 2 phút | I §3.14 | PROPOSAL |
| Dữ liệu | Cửa sổ tính lại | ≥ 7 ngày; dirty bucket tính lại ≤ 1 h | F §3.6; F-P24 | PROPOSAL, PoC |
| Dữ liệu | Job ngày địa phương | xong ≤ 02:00 giờ site; R1 sẵn sàng 99% trước 06:00 giờ site | F-P24; I §3.14 | PROPOSAL |
| Dữ liệu | Ngưỡng restatement | thay đổi > 0,5% kWh của KPI đã phát hành hoặc bất kỳ thay đổi Pmax nào | F §3.6 | PROPOSAL |
| Dữ liệu | Chống rung bộ đếm | ±2 LSB | F-P07 | PROPOSAL |
| Dữ liệu | Chu kỳ phân bổ luồng | ≤ 1 phút trên dữ liệu thô | K §6 #11 | Quyết định K |
| Xuất | Đồng bộ / bất đồng bộ | ≤ 100.000 hàng trả ngay; lớn hơn chạy job nền, link ký số hết hạn ≤ 7 ngày | F §3.14 | PROPOSAL |
| Lưu giữ | Raw / 5 phút / ≥ 1 h | 13 tháng / 5 năm / vòng đời dự án | K §6 #31 | Quyết định K |
| Lưu giữ | Audit lệnh, phê duyệt, SOE, kế hoạch đã chạy | trực tuyến ≥ 13 tháng; lưu trữ ≥ 5 năm (neo WORM là P1); kế hoạch bị thay trước khi chạy: tóm tắt + hash 30 ngày | K §6 #31, R-25 | Quyết định K; số tháng pháp lý UNKNOWN |
| Lưu giữ | Snapshot báo cáo đã phát hành | ≥ 5 năm | F §3.14 | PROPOSAL |
| Quyền | Grant installer | có ngày hết hạn; nhắc xem lại mỗi 90 ngày | I §3.10.2 AC-10 | PROPOSAL |
| Quyền | Phiên hỗ trợ từ xa | ≤ 2 h, chủ site cho phép (P1) | I §3.5 | PROPOSAL |
| Quyền | Client API | hạn tối đa 1 năm; mặc định chỉ đọc (P1) | I §3.3 | PROPOSAL |

---

## 3. Persona, vai trò và quyền

### 3.1 Persona nghiệp vụ

Persona là **người hoặc hệ thống với mục tiêu nghiệp vụ**. Mã P1–P7 theo A §3.3; PA, PS, PO, PK, PI, PG theo 03 §2.2. Cột "Tên gọi theo đề bài" ánh xạ các tên vai trò gợi ý của orchestrator.

| Mã | Persona | Tên gọi theo đề bài | Mục tiêu chính | Tần suất dùng | Ưu tiên MVP | Vai trò hệ thống thường gán |
|---|---|---|---|---|---|---|
| P1 | Chủ C&I / CFO / giám đốc nhà máy | Viewer/Owner | Biết hệ thống tiết kiệm/tốn bao nhiêu theo khung giờ; kiểm tra ESCO; quyết định cấp quyền cho installer | Tuần/tháng | P0 (người xem báo cáo) | `VIEWER`; chủ tài sản cấp grant |
| P2 | Energy manager (cán bộ quản lý năng lượng) | Energy Manager | Số liệu đo phụ theo phụ tải và khung giờ; Pmax 30 phút; hóa đơn bóng | Ngày/tuần | P0 cho hóa đơn bóng và R3; P1 cho phân tích tải | `ANALYST` |
| P3 | O&M contractor / NOC operator | Site Operator | Phát hiện sớm, ack, tạo ticket, đổi chiến lược khi cần, giữ SLA | Hằng ngày, ca trực | **P0 (người dùng hằng ngày)** | `OPERATOR` |
| P3t | Kỹ thuật viên O&M hiện trường | O&M Technician | Nhận ticket, cập nhật kết quả xử lý, đóng ticket có nguyên nhân | Theo sự cố | P0 (ticket), P1 (work order) | `TECHNICIAN` (vai trò mới, xem §8) |
| P4 | EPC / installer / kỹ sư commissioning | Integrator/Installer | Cấu hình nhanh, kiểm chứng giới hạn xuất, bàn giao | Theo dự án | **P0** | `SITE_ENGINEER` |
| P5 | BESS integrator | Integrator/Installer | Lớp supervisory tôn trọng giới hạn BMS, không mất bảo hành | Theo dự án + sự cố | P0/P1 | `SITE_ENGINEER` |
| P6 | IPP / chủ tài sản / ESCO | Viewer/Owner | Sản lượng tin cậy theo site và khung giờ; báo cáo cho bên cho vay | Tháng | P0 (báo cáo), P1 (PPA) | `VIEWER` hoặc `ANALYST`; chủ tài sản cấp grant |
| P7 | Aggregator / VPP | API client | Điều phối nhiều BESS | — | P2 | `API_CLIENT` (P2) |
| PA | Quản trị tổ chức (tenant) | Tenant Admin | Người dùng, vai trò, grant, gói dịch vụ | Theo nhu cầu | P0 | `ORG_ADMIN` |
| PS | Control Supervisor (người duyệt lệnh) | — | Duyệt SOE, lệnh C3, bật điều khiển | Theo sự kiện | P0 cho Gate M2 | `CONTROL_SUPERVISOR` |
| PO | Vận hành nền tảng (nội bộ) | Platform Admin | Vận hành SaaS, edge fleet, OTA, kill switch nền tảng, thư viện biểu giá EVN | Liên tục | P0 | `PLATFORM_ADMIN`; `VENDOR_SUPPORT` (break-glass) |
| PK | Khách/kiosk | — | Xem energy flow, sản lượng, CO₂ | Liên tục, thụ động | P1 | Liên kết công khai (không phải người dùng) |
| PI | Hệ thống bên thứ ba qua API | API client | Đọc dữ liệu, nhận webhook | Liên tục | P1 (đọc), P2 (lệnh) | `API_CLIENT` |
| PG | Nguồn điều độ lưới (không phải người) | — | Gửi giới hạn P / chặn phát ngược qua IEC 104 | Theo điều độ | P1 có điều kiện | Nguồn lệnh `GRID_OPERATOR` |

[INFERENCE] Mọi persona và JTBD là nghiên cứu tại bàn, chưa phỏng vấn khách (GAP-15). Thứ tự ưu tiên có thể đổi sau phỏng vấn installer/O&M/ESCO.

### 3.2 Danh mục vai trò hệ thống (RBAC)

Role binding = (principal, role, scope_node) trên cây `Organization → Portfolio (tùy chọn) → Site → Asset group → Device`; quyền kế thừa xuống cây (F-ORG-08). Quyền lệnh tách khỏi quyền xem. Bảy vai trò đầu bảng là bộ của 03 F-ORG-08; `TECHNICIAN` và `PLATFORM_ADMIN` là bổ sung của 04 (đã ghi vào `notes/_catalog-gaps.md`).

| Mã vai trò | Tên hiển thị | Mô tả ngắn | Có quyền lệnh? | Nguồn |
|---|---|---|---|---|
| `VIEWER` | Người xem (chủ đầu tư, kế toán, bên cho vay) | Xem dashboard, báo cáo đã phát hành của phạm vi được gán | Không | 03 F-ORG-08; I §3.4.1 |
| `ANALYST` | Chuyên viên năng lượng | Như Viewer + xuất dữ liệu, tạo báo cáo nháp, cấu hình biểu giá của site | Không | 03; I §3.4.1 |
| `TECHNICIAN` | Kỹ thuật viên O&M | Xem, ack cảnh báo, nhận/cập nhật/đóng ticket được giao; xem L4 chẩn đoán | Không | **Bổ sung của 04** |
| `OPERATOR` | Vận hành viên (NOC/O&M) | Xem, ack/gác cảnh báo, ticket, lệnh C1/C2 trong SOE, yêu cầu C3 | C1, C2; yêu cầu C3 | 03; I §3.4.1 |
| `SITE_ENGINEER` | Kỹ sư site / commissioning | Cấu hình tài sản, điểm đo, driver, đề xuất SOE, chạy test commissioning, lệnh C1/C2 | C1, C2 (kể cả lệnh test trong checklist); yêu cầu C3 | 03; I §3.4.1 |
| `CONTROL_SUPERVISOR` | Người duyệt điều khiển | Duyệt SOE, duyệt C3, bật điều khiển site, phát lệnh C1/C2 | C1, C2; **duyệt** C3 | 03; I §3.4.1 |
| `ORG_ADMIN` | Quản trị tổ chức | Người dùng, vai trò, grant, gói, tài liệu; tắt kill switch tenant | **Không mặc định** (K §6 #29); chỉ tắt kill switch (C1) | 03; I §3.4.1 |
| `VENDOR_SUPPORT` | Hỗ trợ của nền tảng (break-glass) | Truy cập có hạn, có phê duyệt và audit | Không | 03; I §3.4.1 |
| `PLATFORM_ADMIN` | Vận hành nền tảng | Thư viện biểu giá EVN, thư viện driver, OTA edge (C3), kill switch toàn nền tảng, sức khỏe hệ thống. **Không** đọc dữ liệu tenant nếu không qua break-glass | Kill switch nền tảng (tắt C1); OTA C3 | **Bổ sung của 04** (PO trong 03) |
| `API_CLIENT` | Tài khoản máy | OAuth2 client credentials, scope tối thiểu, mặc định chỉ đọc | Không (P2: C1 trong SOE qua F-INT-21) | 03 F-SEC-22; I §3.3 |
| `GRID_OPERATOR` | Nguồn điều độ (không phải người) | Lệnh IEC 104 tại edge tạo envelope nội bộ `source=GRID_OPERATOR` | Chỉ loại lệnh điều độ đã cấu hình | I §3.4.1; E §3.19 quy tắc 4 |

### 3.3 Danh mục quyền

| Mã quyền | Ý nghĩa | Hạng lệnh |
|---|---|---|
| `site.read` | Xem dữ liệu, dashboard, thiết bị, cảnh báo, kế hoạch trong phạm vi | C0 |
| `report.read` | Xem báo cáo đã phát hành | C0 |
| `report.draft` | Tạo/chạy báo cáo nháp, xem nháp | — |
| `report.publish` | Phát hành snapshot báo cáo cho người xem bên ngoài tenant/khách | — |
| `data.export` | Xuất CSV/XLSX/PDF (có audit) | — |
| `alarm.ack` | Xác nhận (ack), ghi chú cảnh báo | — |
| `alarm.shelve` | Tạm gác cảnh báo (có lý do, thời hạn) | — |
| `alarm.rule.configure` | Sửa quy tắc cảnh báo L1, ngưỡng theo site | — |
| `notify.subscribe` | Tự đăng ký nhận thông báo của mình | — |
| `notify.route.configure` | Cấu hình định tuyến cho người khác/NOC | — |
| `ticket.write` | Tạo, giao, cập nhật, đóng ticket | — |
| `asset.configure` | Sửa sổ tài sản, điểm đo, driver, cảm biến | — |
| `tariff.configure` | Gán/tạo biểu giá, lịch TOU, kỳ hóa đơn cho site | — (BR-TAR-05 nâng lên xác nhận khi site có điều khiển) |
| `tariff.library.manage` | Quản lý thư viện biểu giá EVN dùng chung | — |
| `commissioning.execute` | Chạy bước checklist và lệnh test commissioning | C1–C2 (theo bước) |
| `soe.propose` | Soạn/đề xuất SOE và cấu hình lưới (`export_mode`, `export_limit_w`, `import_cap_w`) | yêu cầu C3 |
| `soe.approve` | Duyệt SOE (không được duyệt bản mình đề xuất) | duyệt C3 |
| `cmd.c1` | Phát lệnh C1 | C1 |
| `cmd.c2` | Phát lệnh C2 (step-up + lý do) | C2 |
| `cmd.c3.request` | Tạo yêu cầu lệnh C3 | C3 (bước 1) |
| `cmd.c3.approve` | Duyệt lệnh C3 của người khác, khác vai trò | C3 (bước 2) |
| `control.enable` | Yêu cầu/duyệt bật `control_enabled` (đi qua C3) | C3 |
| `killswitch.engage` | Tắt kênh lệnh từ xa (site/tenant; nền tảng chỉ `PLATFORM_ADMIN`) | C1 |
| `killswitch.release` | Bật lại kênh lệnh từ xa | C3 |
| `plan.approve` | Duyệt thủ công DispatchPlan vượt guardrail | C2 (≥ C3 nếu cho phép xả dưới dự phòng ở site lớn) |
| `user.manage` | Mời, vô hiệu hóa người dùng; gán vai trò | — |
| `grant.issue` | Cấp/thu hồi grant cho tổ chức installer/O&M (chỉ tenant chủ tài sản) | — |
| `audit.read` | Xem audit của tenant mình | — |
| `tenant.configure` | Hồ sơ tổ chức, gói, cờ tính năng | — |
| `edge.manage` | Claim/gỡ edge, đẩy cấu hình edge | — (OTA là C3) |
| `edge.ota` | Cập nhật firmware edge | C3 |
| `api.client.manage` | Tạo/thu hồi client API (P1) | — |
| `breakglass` | Truy cập khẩn cấp vào tenant (có phê duyệt, có hạn, audit) | — |

### 3.4 Ma trận vai trò × quyền mặc định

Ký hiệu: ✓ có · R chỉ yêu cầu (cần người khác duyệt) · S trong phạm vi ticket/site được giao · — không. Tenant có thể **thu hẹp** nhưng không thể **mở rộng** quyền lệnh vượt bảng này (BR-SEC-01).

| Quyền | VIEWER | ANALYST | TECHNICIAN | OPERATOR | SITE_ENGINEER | CONTROL_SUPERVISOR | ORG_ADMIN | PLATFORM_ADMIN | API_CLIENT |
|---|---|---|---|---|---|---|---|---|---|
| `site.read`, `report.read` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — (chỉ metadata vận hành) | scope |
| `report.draft` | — | ✓ | — | ✓ | ✓ | ✓ | ✓ | — | — |
| `report.publish` | — | ✓ | — | ✓ | — | ✓ | ✓ | — | — |
| `data.export` | — | ✓ | — | ✓ | ✓ | ✓ | ✓ | — | scope |
| `alarm.ack` | — | — | S | ✓ | ✓ | ✓ | — | — | — |
| `alarm.shelve` | — | — | — | ✓ | ✓ | ✓ | — | — | — |
| `alarm.rule.configure` | — | — | — | — | ✓ | ✓ | ✓ | — | — |
| `notify.subscribe` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| `notify.route.configure` | — | — | — | ✓ | — | ✓ | ✓ | — | — |
| `ticket.write` | — | — | S | ✓ | ✓ | ✓ | — | — | — |
| `asset.configure`, `edge.manage` | — | — | — | — | ✓ | — | — | — | — |
| `tariff.configure` | — | ✓ | — | — | ✓ | — | ✓ | — | — |
| `tariff.library.manage` | — | — | — | — | — | — | — | ✓ | — |
| `commissioning.execute` | — | — | — | — | ✓ | — | — | — | — |
| `soe.propose` | — | — | — | — | ✓ | — | — | — | — |
| `soe.approve` | — | — | — | — | — | ✓ | — | — | — |
| `cmd.c1` | — | — | — | ✓ | ✓ | ✓ | — | — | — (P2) |
| `cmd.c2` | — | — | — | ✓ | ✓ | ✓ | — | — | — |
| `cmd.c3.request` | — | — | — | R | R | R | — | R (OTA) | — |
| `cmd.c3.approve` | — | — | — | — | — | ✓ | — | ✓ (chỉ OTA, khác người yêu cầu) | — |
| `control.enable` | — | — | — | — | R | ✓ (duyệt) | — | — | — |
| `killswitch.engage` | — | — | — | ✓ (site) | — | ✓ | ✓ (site, tenant) | ✓ (nền tảng) | — |
| `killswitch.release` | — | — | — | — | — | R/✓ (C3) | R | R/✓ (C3, nền tảng) | — |
| `plan.approve` | — | — | — | — | — | ✓ | — | — | — |
| `user.manage`, `tenant.configure` | — | — | — | — | — | — | ✓ | — | — |
| `grant.issue` | ✓ nếu là chủ tài sản được ủy quyền | — | — | — | — | — | ✓ | — | — |
| `audit.read` | — | — | — | — | — | ✓ | ✓ | — | — |
| `edge.ota` | — | — | — | — | — | — | — | R/✓ (C3) | — |
| `breakglass` | — | — | — | — | — | — | — | qua `VENDOR_SUPPORT`, có phê duyệt | — |

Ghi chú:
- **SoD** (BR-SEC-02): người đề xuất SOE ≠ người duyệt SOE; người yêu cầu C3 ≠ người duyệt C3, và hai người phải **khác vai trò**.
- `ORG_ADMIN` muốn phát lệnh phải tự gán thêm `OPERATOR`; việc gán này được audit và thông báo cho chủ tài sản (BR-ORG-04).
- Persona P1/P6 cấp grant cho tổ chức installer qua tenant chủ tài sản; installer không tự cấp quyền lệnh cho mình trên site của khách (BR-ORG-03).

---

## 4. Hành trình end-to-end và luồng nghiệp vụ liên module

### 4.1 Hành trình của một site C&I PV + BESS

Đi theo một site do đơn vị O&M vận hành, từ ký hợp đồng tới báo cáo tháng. Site PV-only đi cùng hành trình, bỏ các bước BESS và Gate M2. Bảng này mở rộng 03 §8 thành luồng có thể kiểm thử.

| Giai đoạn | Luồng | Persona | Module chính | Cổng/trạng thái site sau giai đoạn |
|---|---|---|---|---|
| 1. Thiết lập | WF-01 Onboarding site · WF-03 Thiết lập biểu giá · WF-12 Cấp quyền installer | PA, P4, P1 | M-ORG, M-TAR, M-GRID | `planned` |
| 2. Kết nối dữ liệu | WF-02 Commissioning (edge) hoặc WF-17 Site chỉ giám sát (connector cloud) | P4, P5 | M-INT, M-MON | `commissioning` |
| 3. Nghiệm thu | WF-02 bước kiểm dấu, test giới hạn xuất, biên bản | P4, PS | M-INT, M-GRID, M-REP | `active`, Gate NONE hoặc M1 |
| 4. Bật điều khiển | WF-04 Gate M1 (native) · WF-05 Gate M2 (edge làm chủ vòng) | P4, PS, P1 | M-BESS, M-GRID, M-OPT, M-SEC | `active`, Gate M1/M2 |
| 5. Vận hành hằng ngày | WF-06 Chiến lược và lịch · WF-07 Lệnh thủ công · WF-10 Cảnh báo → ticket | P3, P3t, P2 | M-DASH, M-MON, M-OPT, M-ALM | — |
| 6. Sự cố | WF-08 Mất cloud · WF-09 Mất thiết bị/POC/BMS · WF-13 Kill switch | P3, P4, P5 | M-INT, M-SEC, M-ALM | Có thể `maintenance`/`suspended` |
| 7. Báo cáo | WF-11 Báo cáo tháng · WF-14 Dữ liệu trễ và restatement | P1, P2, P6 | M-REP, M-TAR, M-HIST | — |
| 8. Thay đổi vòng đời | WF-15 Thay thiết bị/công tơ · WF-16 Ngừng site | P4, PA | M-ORG, M-HIST | `decommissioned` (cuối) |

**Trạng thái điều khiển của site** (dùng xuyên suốt): `control_gate ∈ {NONE, M1, M2}` cùng `control_enabled ∈ {false, true}`, `local_remote ∈ {LOCAL, REMOTE, MAINTENANCE, UNKNOWN}`, `kill_switch ∈ {OFF, ENGAGED}`. Lệnh từ xa chỉ hợp lệ khi `lifecycle = active` ∧ `control_enabled = true` ∧ `local_remote = REMOTE` ∧ `kill_switch = OFF` (BR-SEC-04). Tên enum chi tiết thuộc [05 Domain](05-domain-model.html).

### 4.2 WF-01 — Onboarding site

- **Mục tiêu:** tạo site đủ dữ liệu chủ để nhận dữ liệu và tính KPI. **Kích hoạt:** hợp đồng mới. **Persona:** P4 (`SITE_ENGINEER`), PA (`ORG_ADMIN`), P1.
- **Tiền điều kiện:** tenant tồn tại; người làm có `asset.configure` trên tenant hoặc portfolio.
- **Luồng chính:**
  1. Mở wizard (FR-ORG-005). Nhập thông tin site: tên, địa chỉ, tỉnh/KCN, `timezone` (mặc định `Asia/Ho_Chi_Minh`, bắt buộc), cấp điện áp đấu nối, loại khách hàng EVN, có bán điện dư hay không.
  2. Chọn topology mẫu: T1 PV-only, PV + BESS AC-coupled, hybrid DC, nhiều POC, có EV, có máy phát (FR-ORG-005).
  3. Khai báo tài sản: PV (kWp, kWac, hướng/nghiêng), inverter, BESS (`e_nominal`, `e_usable`, P định mức PCS), EV, máy phát, cảm biến (FR-ORG-003).
  4. Khai báo điểm đo chuẩn: `MTR_POC` (hoặc `MTR_POC_LV`), `MTR_PV`, `MTR_BESS`, `MTR_AUX`, `MTR_LOAD_i`, `MTR_EV_i`, `MTR_GEN`; CT/VT, cấp chính xác, `aux_inside_boundary` (FR-GRID-001, FR-GRID-002).
  5. Khai báo cấu hình lưới **dự kiến**: `export_mode`, `export_limit_w`, `import_cap_w`, `allow_grid_charge`, `allow_ess_export`. Ở bước này chỉ là dữ liệu khai báo, chưa thực thi (FR-GRID-003).
  6. Gán biểu giá và kỳ hóa đơn (WF-03), hoặc bỏ qua.
  7. Chọn đường dữ liệu: **edge của ta** (bắt buộc nếu dự kiến bật điều khiển) hoặc **connector cloud hãng chỉ đọc** (WF-17) (FR-ORG-005, FR-INT-001).
  8. Chọn gói `MONITORING` hoặc `CONTROL` (FR-ORG-011).
  9. Mời người dùng; nếu chủ tài sản là tenant khác, gửi yêu cầu grant (WF-12).
  10. Lưu. Hệ thống tạo site ở `planned`, hiện danh sách mục còn thiếu.
- **Luồng thay thế:**
  - A1 *Site PV-only chỉ giám sát*: bỏ bước BESS/EV; `MTR_POC` khuyến nghị nhưng không bắt buộc. Không có `MTR_POC` thì KPI nhập/xuất (K01/K02), hóa đơn bóng và R3 hiển thị "N/A — chưa có công tơ POC".
  - A2 *Site dự kiến có điều khiển lưới hoặc BESS*: `MTR_POC` bắt buộc; không lưu được wizard ở chế độ "sẵn sàng commissioning" nếu thiếu (BR-GRID-01).
  - A3 *Nhân bản từ mẫu site* (P1, FR-ORG-012): áp mẫu, xem diff trước khi lưu.
- **Luồng lỗi:**
  - E1 Thiếu `timezone` hoặc timezone không thuộc danh mục IANA → chặn lưu.
  - E2 Serial thiết bị đã tồn tại ở site khác cùng tenant → chặn, gợi ý WF-15 (thay thiết bị) hoặc gỡ khỏi site cũ.
  - E3 Gói `MONITORING` nhưng chọn chức năng điều khiển → chặn, yêu cầu đổi gói.
  - E4 `export_mode = ZERO_EXPORT` nhưng `export_limit_w ≠ 0` → tự đặt 0 và báo.
- **Hậu điều kiện:** site `planned`; mọi thay đổi có audit (FR-SEC-014); chưa ingest dữ liệu.

### 4.3 WF-02 — Commissioning thiết bị và xác minh map điểm (site có edge)

- **Mục tiêu:** đưa site từ `planned` → `commissioning` → `active` với dữ liệu đúng dấu, đúng đơn vị và bằng chứng nghiệm thu. **Persona:** P4/P5 (`SITE_ENGINEER`), PS. **FR chính:** FR-INT-015…020, FR-INT-002, FR-INT-005, FR-GRID-004, FR-BESS-007.
- **Tiền điều kiện:** site `planned` có `MTR_POC` khai báo (nếu cần); edge đã lắp, có Internet outbound; người làm có `commissioning.execute`.
- **Luồng chính** (mỗi bước ghi bằng chứng, người làm, thời điểm vào checklist — FR-INT-015):
  1. **Claim edge:** quét QR/nhập serial → cloud cấp chứng chỉ vận hành, gán edge vào site → site chuyển `commissioning` (FR-INT-002, FR-ORG-004). Lệnh thường bị interlock IL-10 chặn trong suốt giai đoạn này.
  2. **Kiểm tra kết nối và đồng hồ:** edge báo `uplink_state = online`, `clock_state = SYNCED` (FR-INT-010).
  3. **Khám phá thiết bị:** quét Modbus/SunSpec trên bus/OT LAN; fingerprint model/firmware → đề xuất driver và `capability_profile` (FR-INT-005).
  4. **Gán driver:** chọn `DriverProfile@version`; hệ thống hiển thị trạng thái kiểm chứng (`VERIFIED_LAB`, `VERIFIED_FIELD`, `COMMUNITY`, `UNVERIFIED`). Driver không `VERIFIED_*` chỉ được đọc (FR-INT-003, BR-INT-02).
  5. **Xác minh map điểm (point mapping verification)** — FR-INT-020: với mỗi thiết bị, so ≥ 1 giá trị đọc qua driver với giá trị tham chiếu (màn hình/HMI thiết bị, đồng hồ cầm tay, nameplate): công suất, điện áp, bộ đếm năng lượng, SOC. Kiểm hệ số scale, thứ tự word 32 bit, đơn vị, sentinel. Ghi kết quả "Khớp / Lệch (giá trị, %)". Màn L4 hiện giá trị thô, hệ số scale, mã quality (FR-MON-007).
  6. **Phép thử dấu** — FR-INT-016: tạo tình huống biết trước (ví dụ BESS sạc nhỏ, giới hạn PV) và kiểm hướng P, Q, thanh ghi nhập/xuất ở mọi điểm đo.
  7. **Cấu hình chủ vòng:** chọn `control_owner` cho từng chức năng (zero-export, import cap, SOC guard) (FR-OPT-003).
  8. **Cấu hình và kiểm chứng native** (nếu dùng Gate M1): đặt giới hạn xuất/chế độ native, readback (FR-GRID-004, FR-BESS-003).
  9. **Test giới hạn xuất** — FR-INT-017: kịch bản giảm tải/tăng PV; đo thời gian đưa xuất về ≤ giới hạn + `export_violation_tol_w` và số giây vượt.
  10. **(Chỉ cho Gate M2) Test watchdog và fail-safe** — FR-INT-018: rút cáp edge↔thiết bị, mất `MTR_POC`, chặn cloud, chuyển LOCAL; kiểm thiết bị về mặc định trong `revert_timeout_s`.
  11. **(Chỉ cho Gate M2) Đề xuất SOE** (Site Engineer) → **duyệt SOE** (Control Supervisor, khác người) → ký số, đẩy xuống edge (FR-BESS-007).
  12. **Biên bản:** sinh PDF biên bản commissioning (cấu hình, kết quả từng test, phiên bản driver/SOE, chữ ký) (FR-INT-019).
  13. **Chuyển `active`:** khi mọi bước bắt buộc theo topology đạt; người có quyền xác nhận; site vào KPI danh mục và availability.
- **Luồng thay thế:**
  - A1 *Site chỉ giám sát có edge*: bỏ bước 7–11; vẫn bắt buộc bước 5–6 cho công tơ.
  - A2 *Thiết bị không có watchdog* (bước 10 không đạt hoặc driver khai báo `watchdog_support = false`): đánh dấu `requires_native_fallback = true`; thiết bị chỉ được đổi giữa các chế độ native (FR-SEC-016). Site vẫn có thể vào M2 cho thiết bị khác.
  - A3 *Hủy commissioning*: quay về `planned`, thu hồi chứng chỉ edge nếu tháo (FR-ORG-004).
- **Luồng lỗi:**
  - E1 Khám phá không thấy thiết bị → báo lỗi bus (timeout, exception code) ở L4; không cho qua bước 4.
  - E2 Lệch map > 2% (công suất) hoặc sai đơn vị/scale → bước 5 "Không đạt"; sửa driver overlay hoặc khai báo, chạy lại.
  - E3 Phép thử dấu ngược → không tự đảo âm thầm; kỹ sư chọn "sửa đấu dây CT" hoặc "khai báo `sign_convention` đảo" (ghi lý do, audit), rồi chạy lại.
  - E4 Test giới hạn xuất vượt 5 s hoặc có vi phạm kéo dài → không cho `active` với `export_mode` đã khai; ghi kết quả vào biên bản.
  - E5 Edge `UNSYNCED` → chặn bước 6–11 (IL-06).
- **Hậu điều kiện:** site `active`; biên bản lưu ở tài liệu site; `control_gate` = NONE hoặc M1 (nếu bước 8 đạt và được bật theo WF-04).

### 4.4 WF-03 — Thiết lập biểu giá

- **Persona:** P2 (`ANALYST`), P4, PO (thư viện). **FR:** FR-TAR-001…007.
- **Luồng chính:**
  1. PO duy trì thư viện biểu giá EVN có phiên bản (nhóm khách hàng × cấp điện áp × khung giờ, đơn giá chưa VAT, `valid_from`, văn bản nguồn) và lịch TOU (QĐ 963; TT 16/2014 cho lịch sử) (FR-TAR-001, FR-TAR-002).
  2. Người dùng chọn biểu giá từ thư viện cho từng điểm đo thanh toán (POC; công tơ trạm sạc riêng) hoặc tạo bản riêng của tenant (FR-TAR-004).
  3. Chọn **lịch dùng cho hóa đơn bóng** và **lịch dùng cho tối ưu** (có thể khác nhau, FR-TAR-003).
  4. Khai báo kỳ hóa đơn: ngày chốt chỉ số (FR-TAR-005).
  5. Hệ thống kiểm hợp lệ (BR-TAR-01…04), hiển thị bản xem trước "dải TOU tuần này" theo giờ site.
  6. Lưu với ngày hiệu lực. Nếu site có `control_enabled = true` và lịch tối ưu đổi, bộ sinh lịch tầng 2 chạy lại (FR-OPT-005) sau khi người có `cmd.c2` xác nhận (BR-TAR-05).
- **Luồng thay thế:** A1 biểu giá đổi giữa kỳ → hóa đơn bóng tính theo từng `TariffVersion` (BR-TAR-03). A2 site chưa có biểu giá → KPI chi phí "N/A — chưa gán biểu giá"; bộ sinh lịch TOU không chạy.
- **Luồng lỗi:** E1 lịch TOU có khoảng hở hoặc chồng lấn trong một ngày → chặn lưu. E2 `valid_from` trong quá khứ đối với kỳ đã phát hành báo cáo → cho lưu nhưng tạo restatement (WF-14), bắt buộc lý do.
- **Hậu điều kiện:** biểu giá có phiên bản gắn điểm đo; mọi thay đổi có audit.

### 4.5 WF-04 — Kích hoạt Gate M1 (cấu hình native có readback)

- **Persona:** P4, PS, P1. **FR:** FR-SEC-005, FR-GRID-003, FR-GRID-004, FR-GRID-006, FR-BESS-003, FR-OPT-005.
- **Tiền điều kiện:** site `active`; edge của ta đã claim (K §6 #13); driver ghi của controller native `VERIFIED_*`; `MTR_POC` đã qua phép thử dấu.
- **Luồng chính:**
  1. Site Engineer đề xuất cấu hình lưới (`export_mode`, `export_limit_w`, `import_cap_w`) và `control_owner = NATIVE` cho từng chức năng mà native hỗ trợ.
  2. Chủ tài sản ghi nhận đồng ý bật điều khiển (đồng ý điện tử, lưu vào tài liệu site) (FR-SEC-005).
  3. Yêu cầu C3 "bật `control_enabled`, Gate M1" → Control Supervisor duyệt trong ≤ 15 phút (FR-SEC-007).
  4. Edge ghi tham số native (giới hạn xuất, chế độ TOU/capacity control…) qua driver, đọc lại, báo `APPLIED` hoặc `FAILED_*` (FR-INT-007).
  5. Hệ thống theo dõi kết quả tại POC (thanh nhập/trần, xuất/giới hạn, FR-GRID-007).
- **Luồng lỗi:** E1 readback lệch → `FAILED_NO_EFFECT`, cảnh báo (FR-ALM-011), `control_gate` giữ NONE. E2 Native không có chức năng đã chọn → gợi ý Gate M2 cho chức năng đó.
- **Hậu điều kiện:** `control_gate = M1`; chiến lược và lịch có thể phát qua chế độ native (WF-06).

### 4.6 WF-05 — Kích hoạt Gate M2 (edge làm chủ vòng)

- **Persona:** P4, PS, P1, PO. **FR:** FR-SEC-021 (danh sách sẵn sàng), FR-BESS-007, FR-SEC-008, FR-SEC-010, FR-SEC-012, FR-SEC-013, FR-INT-018.
- **Luồng chính:**
  1. Hệ thống hiển thị **hồ sơ sẵn sàng Gate M2** của site (FR-SEC-021) với từng điều kiện Đạt/Chưa đạt.
  2. Site Engineer hoàn tất điều kiện thiếu (test watchdog, LOCAL/REMOTE, SOE).
  3. Yêu cầu C3 "Gate M2 cho site S, chức năng X với `control_owner = EDGE`".
  4. Control Supervisor (khác người, khác vai trò) duyệt sau step-up MFA.
  5. Edge nhận cấu hình ký số, kiểm SOE, chuyển chức năng sang vòng edge; báo trạng thái trên trang trạng thái điều khiển (FR-SEC-011).
- **Luồng lỗi:** E1 Một điều kiện chuyển sang "Chưa đạt" khi đang M2 (ví dụ driver hạ trạng thái, chứng chỉ ký hết hạn, interlock không đọc được) → edge từ chối lệnh mới thuộc M2, chạy chiến lược mặc định; cảnh báo Cao; site hiển thị "M2 tạm ngưng: lý do". E2 Từ chối duyệt → yêu cầu đóng với lý do.
- **Hậu điều kiện:** `control_gate = M2` cho các chức năng đã duyệt; audit đầy đủ.

### 4.7 WF-06 — Chọn chiến lược và chạy lịch hằng ngày (tầng 2)

- **Persona:** P3 (`OPERATOR`), P2, PS. **FR:** FR-BESS-004, FR-OPT-005…011, FR-ADV-001.
- **Luồng chính:**
  1. Operator chọn `site_strategy` mặc định của site (SELF_CONSUMPTION, PEAK_SHAVING, TOU_SCHEDULE, BACKUP_HOLD, IDLE) trong danh sách `capability_profile` cho phép. Đổi chiến lược mặc định là cấu hình có phiên bản, hạng C2 (FR-BESS-004).
  2. Lúc 05:30 giờ site và khi có sự kiện (đổi biểu giá, đổi cấu hình, dự báo lệch lớn), bộ sinh lịch luật TOU tạo DispatchPlan 48 h, slot 15 phút, `slot_mode` theo G (FR-OPT-005). Dự báo tải dùng F0/F1 (FR-ADV-001).
  3. Validator kiểm mọi slot (FR-OPT-008). Không đạt → `REJECTED`, cảnh báo; edge giữ lịch cũ.
  4. Plan nằm trong guardrail → tự duyệt; vượt guardrail (ví dụ xả dưới dự phòng) → chờ người có `plan.approve` (FR-OPT-007).
  5. Gate M1: plan được chuyển thành lịch native (TOU periods…) và ghi qua driver có readback. Gate M2: đóng gói `APPLY_SCHEDULE` có ký số gửi edge.
  6. Edge báo theo slot; hệ thống tính thực tế so với kế hoạch và mã lý do (FR-OPT-010, FR-OPT-011).
- **Luồng lỗi:** E1 Thiếu biểu giá/lịch TOU → không sinh plan, cảnh báo Trung bình, edge chạy chiến lược mặc định. E2 Thiếu dữ liệu tải < 7 ngày → F0/F1 không đủ; dùng profile mặc định của topology và gắn nhãn "dự báo dự phòng". E3 Edge không xác nhận plan trong 300 s → "Chưa đồng bộ", edge tiếp tục plan cũ (FR-OPT-009).
- **Hậu điều kiện:** plan `EXECUTING`; lịch tại edge còn ≥ 48 h.

### 4.8 WF-07 — Lệnh thủ công và phê duyệt hai người

- **Persona:** P3, PS. **FR:** FR-BESS-005, FR-SEC-006…010, FR-SEC-012, FR-SEC-015.
- **Luồng chính (C1/C2):**
  1. Operator mở hộp lệnh (ví dụ `SET_ESS_P`). Hộp hiển thị "giá trị hiện tại → mới" kèm hướng, giới hạn sẽ áp, tác động dự kiến tới P lưới, thời hạn (mặc định 15 phút).
  2. PDP đánh giá: quyền, MFA, `control_enabled`, `local_remote`, driver, SOE, ngân sách đội, giờ → xác định hạng thực tế (C1/C2/C3).
  3. C2: yêu cầu step-up MFA (≤ 5 phút) và lý do.
  4. Command Signer ký envelope; gửi qua MQTT `down/cmd`.
  5. Edge kiểm chữ ký, hạn, `seq`, interlock, SOE → `ACCEPTED` hoặc `REJECTED_*`.
  6. Edge ghi xuống thiết bị, đọc lại → `APPLIED` / `APPLIED_CLAMPED` (kèm giá trị thực) / `FAILED_*`.
  7. Hết hạn → `on_expiry = REVERT_DEFAULT`; trạng thái `EXPIRED`.
- **Luồng C3:** sau bước 2, lệnh vào hàng đợi phê duyệt; Control Supervisor khác người, khác vai trò, step-up MFA, xem diff và tác động MW, duyệt trong ≤ 15 phút; chủ site được thông báo. Hết cửa sổ → `APPROVAL_EXPIRED`.
- **Luồng lỗi:** E1 Edge offline → lệnh `UNDELIVERED` khi quá `expires_at`, không gửi lại. E2 `REJECTED_INTERLOCK:IL-01` (LOCAL) → UI hiện "Site đang điều khiển tại chỗ". E3 Vượt Fleet Governor → hàng đợi + nâng C3.
- **Hậu điều kiện:** nhật ký lệnh đầy đủ; UI chỉ hiện "đã áp dụng" sau readback.

### 4.9 WF-08 — Mất liên lạc cloud ↔ edge

- **FR:** FR-INT-009, FR-OPT-006, FR-MON-008, FR-ALM-004, NFR-REL-002.
- **Luồng:**
  1. Edge mất broker. Edge **tiếp tục** vòng cục bộ (zero-export, import cap, limit chain), chạy lịch đã nhận; lệnh thủ công đang hiệu lực chạy tới `expires_at` rồi `on_expiry`.
  2. Edge ghi buffer (không mất dữ liệu ≤ 7 ngày).
  3. Cloud đánh dấu edge `OFFLINE` sau ≈ 90 s; header site hiện "Mất kết nối cloud — site vẫn đang được điều khiển cục bộ theo kế hoạch #n tới HH:MM".
  4. Sau `T_offline_alarm_edge` (5 phút): một cảnh báo kết nối mức Cao; chặn cảnh báo con (FR-ALM-004).
  5. Lệnh mới tạo trong lúc offline: `SENT` → `UNDELIVERED` khi quá hạn; không xếp hàng gửi muộn.
  6. Hết lịch → chiến lược mặc định; UI (khi có lại kết nối) hiển thị khoảng thời gian chạy lịch dự phòng.
  7. Kết nối lại: edge publish `state` (lệnh đang hiệu lực, config version, plan version) → cloud đối soát, cảnh báo nếu lệch → edge xả buffer, realtime trước, backfill giới hạn tốc độ → job tính lại dirty bucket (WF-14).
- **Hậu điều kiện:** dữ liệu đầy đủ, watermark `complete_until` cập nhật; audit cục bộ của edge đã đồng bộ lên cloud.

### 4.10 WF-09 — Mất liên lạc edge ↔ thiết bị, mất công tơ POC, dữ liệu BMS cũ

- **FR:** FR-BESS-009, FR-GRID-005, FR-SEC-010, FR-SEC-016, NFR-REL-003.
- **Luồng:**
  1. Edge phát hiện: quality `BAD_COMM` của thiết bị, hoặc dữ liệu `MTR_POC` cũ hơn `T_stale_poc`, hoặc dữ liệu BMS cũ hơn `T_stale_bms`, hoặc BMS báo lỗi.
  2. Mức 3 của arbiter (giám sát an toàn edge) áp ngay: BESS → P = 0 hoặc chế độ native; PV → giới hạn native (K §6 #17). Không giữ setpoint cũ vô hạn.
  3. Interlock IL-03/IL-04/IL-05 chặn lệnh mới tới thiết bị liên quan (`REJECTED_INTERLOCK:<code>`).
  4. Nếu edge mất kết nối thiết bị: thiết bị tự hoàn nguyên nhờ watchdog trong `revert_timeout_s`; thiết bị `requires_native_fallback` dựa vào giới hạn native đã cấu hình khi commissioning.
  5. Cảnh báo: thiết bị mất kết nối (Cao); "Edge mất `MTR_POC` — điều khiển lưới chuyển về native" (Cao, FR-ALM-009); BMS stale (Cao).
  6. Phục hồi: edge chờ ≥ 2 chu kỳ đọc hợp lệ rồi mới cho phép lại vòng của ta (giống `SAFE_START`).
- **Hậu điều kiện:** không có setpoint cưỡng bức tới thiết bị không có dữ liệu tin cậy; sự kiện ghi audit edge.

### 4.11 WF-10 — Cảnh báo → ticket (→ work order ở Phase 1)

- **Persona:** P3 (`OPERATOR`), P3t (`TECHNICIAN`). **FR:** FR-ALM-001…011, FR-ALM-010 (ticket), FR-ALM-016 (work order, P1).
- **Luồng chính:**
  1. Driver/connector hoặc quy tắc L1 sinh cảnh báo; hệ thống chuẩn hóa mã, mức (Khẩn cấp/Cao/Trung bình/Thông tin), khử trùng lặp (FR-ALM-001, FR-ALM-003).
  2. Định tuyến thông báo theo đăng ký người dùng × site × mức (in-app, e-mail ở MVP) (FR-ALM-007, FR-ALM-008).
  3. Operator mở console, xem chi tiết (biểu đồ ±2 h, lịch sử cùng mã, hành động khuyến nghị, liên hệ site) (FR-ALM-006).
  4. Operator **ack** (ghi người, thời điểm).
  5. Operator **tạo ticket** từ cảnh báo: ngữ cảnh cảnh báo, tài sản, ảnh chụp dữ liệu được gắn tự động; chọn người xử lý (`TECHNICIAN` hoặc `OPERATOR`), ưu tiên (FR-ALM-010).
  6. Kỹ thuật viên nhận thông báo, cập nhật trạng thái `Đang xử lý` → `Chờ` (vật tư/hãng) → `Đã xử lý`.
  7. Đóng ticket: bắt buộc nguyên nhân gốc (danh mục) và ghi chú; cảnh báo liên quan chuyển trạng thái xử lý `Đã xử lý` (trạng thái ack/xử lý/hết tách riêng, xem BR-ALM-02).
  8. (P1) Từ ticket tạo work order có checklist, lịch, ảnh, chữ ký; SLA theo mức (FR-ALM-016, FR-ALM-017).
- **Luồng thay thế:** A1 Cảnh báo tự hết (RTN) trước khi ack → giữ ở "Đã hết, chưa xác nhận" (mức 3–4 có thể cấu hình tự ack). A2 Tạm gác (shelve) có lý do + thời hạn ≤ 8 h; cảnh báo an toàn không được gác (BR-ALM-03). A3 Tài sản đang `maintenance` → cảnh báo vào "Ngoài dịch vụ", không thông báo.
- **Luồng lỗi:** E1 Người xử lý bị vô hiệu hóa hoặc hết grant → ticket trở về "Chưa giao", thông báo người tạo. E2 Gửi e-mail lỗi → thử lại có backoff; sau 3 lần lỗi, ghi "Không gửi được" ở cảnh báo.
- **Hậu điều kiện:** cảnh báo có `ticket_id`; nguyên nhân gốc lưu làm nhãn (FR-ALM-019, P1), là dữ liệu cho phát hiện bất thường ML có đánh giá sau này (FR-ADV-008, P2).

### 4.12 WF-11 — Báo cáo tháng (R2) và phát hành

- **Persona:** P2/P3 (tạo), P1/P6 (nhận). **FR:** FR-REP-002, FR-REP-005, FR-TAR-006, FR-REP-006.
- **Luồng chính:**
  1. Sau khi kỳ hóa đơn (hoặc tháng lịch) đóng, hệ thống chờ watermark `complete_until` ≥ cuối kỳ hoặc tối đa tới 06:00 giờ site ngày thứ 2 sau kỳ.
  2. Người có `report.draft` chạy R2: K01–K06, K10–K12, hóa đơn bóng theo khung TOU, Pmax, vi phạm xuất, availability dữ liệu, cờ chất lượng.
  3. Hệ thống ghi cờ `INCOMPLETE` và khoảng min/max nếu có chu kỳ thiếu.
  4. Người có `report.publish` xem nháp, phát hành → snapshot bất biến với `report_version`, `data_as_of`, `tariff_version`, `calc_version`, `attribution_version`.
  5. Người nhận xem/tải PDF/XLSX (MVP: theo yêu cầu; gửi theo lịch là P1, FR-REP-013).
- **Luồng thay thế:** A1 Dữ liệu trễ làm đổi số > ngưỡng restatement → bản sửa có phiên bản mới, thông báo người đã nhận (WF-14).
- **Luồng lỗi:** E1 Chưa gán biểu giá → R2 vẫn chạy phần năng lượng, phần chi phí "N/A". E2 Thiếu `MTR_POC` → phần nhập/xuất "N/A".
- **Hậu điều kiện:** snapshot lưu ≥ 5 năm; mọi lần xuất có audit.

### 4.13 WF-12 — Cấp và thu hồi quyền cho installer/O&M

- **Persona:** P1/P6 (chủ tài sản), PA. **FR:** FR-ORG-009, FR-ORG-008.
- **Luồng:** (1) Chủ tài sản (tenant chủ) chọn tổ chức installer, phạm vi site, loại quyền (xem / cấu hình / lệnh), ngày hết hạn. (2) Tổ chức installer chấp nhận; `ORG_ADMIN` của installer gán vai trò cho người của mình **trong phạm vi grant**. (3) 90 ngày một lần hệ thống nhắc chủ tài sản xem lại. (4) Hết hạn hoặc thu hồi → mọi binding dựa trên grant mất hiệu lực ngay; lệnh C3 đang chờ duyệt do người của installer tạo bị hủy; phiên đang mở mất quyền ở request kế tiếp.
- **Lỗi:** E1 Grant loại "lệnh" nhưng site chưa `control_enabled` → cho cấp, ghi chú "chưa có hiệu lực điều khiển".

### 4.14 WF-13 — Kill switch và Fleet Governor

- **FR:** FR-SEC-012, FR-SEC-013.
- **Luồng kill switch:** (1) Người có `killswitch.engage` chọn phạm vi (site/tenant; nền tảng chỉ `PLATFORM_ADMIN`), nhập lý do — thao tác C1, không cần người duyệt. (2) Cloud gửi lệnh ký `REMOTE_CONTROL_SUSPENDED` tới mọi edge trong phạm vi; edge chạy chiến lược mặc định cục bộ, từ chối mọi lệnh từ xa trừ lệnh bật lại hợp lệ. (3) Bật lại là C3 (hai người). Kill switch **không phải E-stop** và không tác động bảo vệ native.
- **Luồng Governor:** lệnh làm tổng |ΔP| của tenant trong 5 phút vượt ngưỡng → lệnh vào hàng đợi và nâng C3; lệnh đồng loạt nhiều site được trải jitter 0–300 s (trừ điều độ).

### 4.15 WF-14 — Dữ liệu trễ và restatement

- **FR:** FR-HIST-006, FR-REP-005.
- **Luồng:** (1) Dữ liệu trễ (backfill edge, connector cloud lấy lại 7 ngày, nhập tay) được ingest idempotent. (2) Bucket bị ảnh hưởng đánh dấu dirty; job tính lại ≤ 1 h; ngày/tháng địa phương ghi lại. (3) Watermark cập nhật. (4) Nếu KPI của báo cáo đã phát hành thay đổi > 0,5% kWh hoặc Pmax đổi → tạo restatement, thông báo người nhận, giữ bản cũ.

### 4.16 WF-15 — Thay thiết bị hoặc công tơ

- **FR:** FR-ORG-010 (MVP, thủ công), FR-ORG-015 (wizard P1), FR-HIST-004.
- **Luồng MVP:** (1) Site Engineer ghi sự kiện tài sản: thiết bị cũ, thiết bị mới, thời điểm, thanh ghi cuối của công tơ cũ và đầu của công tơ mới, tỷ số CT/VT mới. (2) Pipeline năng lượng dùng sự kiện này (không tự đoán), chuỗi dữ liệu giữ liên tục theo vị trí tài sản. (3) Nếu thay công tơ đo điều khiển, chạy lại phép thử dấu (FR-INT-016) trước khi edge dùng lại cho vòng lưới.
- **Lỗi:** không có sự kiện mà bộ đếm giảm → `RESET_UNEXPLAINED`, tích phân P có cờ, cảnh báo DQ.

### 4.17 WF-16 — Ngừng site (decommission)

- **FR:** FR-ORG-018. **Luồng:** `ORG_ADMIN` yêu cầu, xác nhận hai bước (gõ tên site) → hệ thống từ chối nếu `control_enabled = true` (phải tắt trước, C3) → thu hồi chứng chỉ edge, dừng ingest, đóng ticket mở hoặc chuyển → giữ dữ liệu theo chính sách lưu giữ → `decommissioned` là trạng thái cuối.

### 4.18 WF-17 — Site chỉ giám sát qua connector cloud hãng

- **FR:** FR-MON-003, FR-INT-021 (hãng khác, P1). **Luồng:** (1) Người dùng nhập credential/OAuth của hãng (Huawei Northbound ở MVP), chọn plant tương ứng. (2) Connector pull có rate limiter; quality `UNCERTAIN_VENDOR_CLOUD`; backfill ban đêm 7 ngày. (3) Site chuyển `commissioning` → `active` khi xác minh map (bước 5 của WF-02, dạng rút gọn: so tổng sản lượng ngày với màn hình hãng). (4) Mọi chức năng điều khiển bị ẩn; trang trạng thái ghi "Site chỉ giám sát — không có edge".
- **Lỗi:** credential hết hạn/hãng đổi chính sách API → cảnh báo kết nối, quality chuyển `BAD_COMM`, không hiện số cũ như số mới.

---

## 5. Yêu cầu theo module

Mỗi module theo cùng khung: mục đích → persona → user story → luồng → yêu cầu chức năng (FR) → quy tắc nghiệp vụ (BR) → tiền/hậu điều kiện → dữ liệu vào/ra → phân quyền → lỗi và trường hợp biên → tiêu chí chấp nhận (AC) → phụ thuộc → bằng chứng. Luồng dài liên module đã viết ở §4 và chỉ được tham chiếu.

### 5.1 M-ORG — Tổ chức, site, tài sản, người dùng

**Mục đích nghiệp vụ.** Cung cấp dữ liệu chủ (tenant, cây site, sổ tài sản, vòng đời) và quản lý người dùng, vai trò, grant. Mọi module khác dựa vào cây này để xác định phạm vi quyền, ngày địa phương, biểu giá và trạng thái điều khiển. Mô hình mở rộng cây Company → Plant → Device của FusionSolar bằng điểm đo có ranh giới, BESS nhiều tầng, EV, máy phát và edge (03 §4).

**Persona.** PA (chính), P4 (khai báo tài sản), P1/P6 (cấp grant), P3 (đọc).

**User story**

| ID | Là… | Tôi muốn… | Để… | FR |
|---|---|---|---|---|
| US-ORG-01 | Kỹ sư installer (P4) | tạo site mới bằng wizard theo topology mẫu | khai báo đúng ngay từ đầu và giảm thời gian commissioning | FR-ORG-005, FR-ORG-006 |
| US-ORG-02 | Quản trị tổ chức (PA) | mời người dùng và gán vai trò theo site | mỗi người chỉ thấy và làm việc trong phạm vi của mình | FR-ORG-007, FR-ORG-008 |
| US-ORG-03 | Chủ C&I (P1) | cấp quyền có hạn cho đơn vị O&M và thu hồi bất kỳ lúc nào | kiểm soát ai được điều khiển tài sản của tôi | FR-ORG-009 |
| US-ORG-04 | Kỹ sư (P4) | ghi sự kiện thay công tơ kèm chỉ số cuối/đầu | điện năng tính tiền không bị sai sau khi thay | FR-ORG-010 |
| US-ORG-05 | Quản trị tổ chức (PA) | gắn gói MONITORING hoặc CONTROL cho từng site | tách site chỉ giám sát khỏi site có điều khiển | FR-ORG-011 |
| US-ORG-06 | Kỹ sư (P4) | thấy rõ site đang ở trạng thái vòng đời nào | biết khi nào site được tính KPI và được điều khiển | FR-ORG-004 |

**Luồng chính:** WF-01 (onboarding), WF-12 (grant), WF-15 (thay thiết bị), WF-16 (ngừng site).

**Yêu cầu chức năng**

| ID | Yêu cầu | F- | Ưu tiên | Phát hành | Hạng·Gate | Căn cứ |
|---|---|---|---|---|---|---|
| FR-ORG-001 | Hệ thống phải cho tạo/sửa tổ chức (tenant) với hồ sơ pháp nhân, múi giờ mặc định, ngôn ngữ (vi/en), gói. Mọi bản ghi nghiệp vụ mang `tenant_id`. | F-ORG-01 | P0 | MVP | — | I §3.4.1 |
| FR-ORG-002 | Hệ thống phải quản lý cây Org → Portfolio/Region (tùy chọn) → Site → Asset group → Device. Site có bắt buộc: tên, `timezone` IANA, cấp điện áp, loại khách hàng EVN, `control_enabled` (mặc định `false`), `lifecycle`, topology (T1–T6), có bán dư hay không. | F-ORG-02 | P0 | MVP | — | K §6 #7, #26 |
| FR-ORG-003 | Hệ thống phải có sổ tài sản theo kiểu (GridConnection, MeteringPoint, PVPlant, Inverter, String, BatterySystem, PCS, BMS, Rack, Module, Load, EVCharger, Connector, Generator, Sensor, EdgeNode) với nameplate, hãng/model/firmware/serial, quan hệ cha–con và liên kết `DriverProfile@version`. Công suất lắp đặt (kWp) lưu theo thời gian. | F-ORG-03 | P0 | MVP | — | 03 §4.1 |
| FR-ORG-004 | Hệ thống phải thực thi vòng đời `planned → commissioning → active ⇄ maintenance / suspended → decommissioned` cho site và từng tài sản theo bảng điều kiện của 03 §4.2; mỗi chuyển trạng thái ghi người, thời điểm, lý do. | F-ORG-04 | P0 | MVP | — | 03 §4.2; I IL-10 |
| FR-ORG-005 | Hệ thống phải có wizard onboarding: thông tin site → topology mẫu → tài sản → điểm đo → cấu hình lưới dự kiến → biểu giá/kỳ hóa đơn → đường dữ liệu (edge/connector cloud) → gói → mời người dùng. Kết quả là site `planned` và danh sách mục còn thiếu. | F-ORG-05 | P0 | MVP | — | A §3.3 P4 |
| FR-ORG-006 | Wizard phải kiểm hợp lệ theo topology: `MTR_POC` bắt buộc nếu site có BESS hoặc gói CONTROL; serial không trùng trong tenant; tỷ số kWp/kWac ngoài khoảng 0,8–1,6 chỉ cảnh báo "kiểm tra lại nameplate", không chặn. | F-ORG-05, F-GRID-01 | P0 | MVP | — | K §6 #10 |
| FR-ORG-007 | Hệ thống phải cho mời người dùng qua e-mail, kích hoạt, vô hiệu hóa; người dùng chọn ngôn ngữ vi/en; danh sách người dùng theo tenant và theo site. | F-ORG-07 | P0 | MVP | — | — |
| FR-ORG-008 | Hệ thống phải lưu role binding (principal, role, scope_node) với vai trò ở §3.2, kế thừa xuống cây; quyền lệnh tách khỏi quyền xem; `ORG_ADMIN` không có quyền lệnh mặc định. | F-ORG-08 | P0 | MVP | — | K §6 #29 |
| FR-ORG-009 | Chủ tài sản phải cấp được grant cho tổ chức installer/O&M: phạm vi site, loại quyền (xem/cấu hình/lệnh), ngày hết hạn bắt buộc; thu hồi tức thời; nhắc xem lại mỗi 90 ngày; mọi grant có audit. | F-ORG-09 | P0 | MVP | — | K §6 #29; I AC-10 |
| FR-ORG-010 | Hệ thống phải ghi sự kiện tài sản có thời điểm: thay công tơ/CT/VT (thanh ghi cuối/đầu, tỷ số mới), thay inverter/PCS, đổi firmware, mở rộng công suất, sửa chữa. Pipeline năng lượng phải dùng sự kiện này. | F-ORG-11 | P0 | MVP | — | C §3.15 |
| FR-ORG-011 | Mỗi site phải có gói (`MONITORING`/`CONTROL`) và cờ tính năng (ví dụ tầng 3, EV, IEC 104); chức năng điều khiển bị ẩn và bị PDP chặn ở site gói `MONITORING`. Tính phí thuê bao không thuộc MVP. | F-ORG-15 | P0 | MVP | — | K §6 #13 |
| FR-ORG-018 | Hệ thống phải cho ngừng site với xác nhận hai bước, chặn khi `control_enabled = true`, thu hồi chứng chỉ edge, dừng ingest và giữ dữ liệu theo chính sách lưu giữ. | F-ORG-04, F-INT-02 | P0 | MVP | — | 03 §4.2 |
| FR-ORG-012 | Hệ thống nên cho lưu site làm mẫu (topology, điểm đo, quy tắc cảnh báo, chiến lược, SOE đề xuất) và áp cho site mới có xem diff. Mẫu không mang SOE đã duyệt: SOE luôn phải duyệt lại theo site. | F-ORG-06 | P1 | Phase 1 | — | B #25 |
| FR-ORG-013 | Hệ thống nên cho tạo liên kết chỉ đọc có hạn (bên cho vay, kiểm toán) và liên kết kiosk công khai; kiosk không thấy cảnh báo, cấu hình, lệnh, số tiền (nếu chủ site tắt). | F-ORG-10 | P1 | Phase 1 | — | H §3.15 |
| FR-ORG-014 | Hệ thống nên lưu tài liệu theo site/tài sản (SLD, biên bản, datasheet, bảo hành, hồ sơ đấu nối) có phiên bản, phân loại D2. | F-ORG-12 | P1 | Phase 1 | — | I §3.4.4 |
| FR-ORG-015 | Hệ thống nên có wizard thay thiết bị: chọn cũ → khai báo mới → ghi sự kiện FR-ORG-010 → giữ chuỗi dữ liệu liên tục theo vị trí tài sản. | F-ORG-13 | P1 | Phase 1 | — | C §3.15 |
| FR-ORG-016 | Hệ thống nên lưu điều khoản hợp đồng: bảo hành BESS (EFC, throughput, SOC trung bình, nhiệt độ), O&M (SLA, loại trừ availability), PPA/ESCO (giá, kỳ). | F-ORG-16 | P1 | Phase 1 | — | C-P13 |
| FR-ORG-017 | Hệ thống có thể cho white-label theo tenant (logo, màu, tên miền, người gửi e-mail). | F-ORG-14 | P2 | Phase 2 | — | UNKNOWN nhu cầu (GAP-09) |

**Quy tắc nghiệp vụ**

- **BR-ORG-01** Một site thuộc đúng một tenant sở hữu. Tổ chức khác chỉ truy cập qua grant (FR-ORG-009).
- **BR-ORG-02** `timezone` của site là bắt buộc và quyết định ngày địa phương, khung TOU và kỳ hóa đơn. Đổi `timezone` sau khi site `active` là thay đổi có lý do, kích hoạt tính lại ngày/tháng địa phương và restatement.
- **BR-ORG-03** Quyền lệnh trên site của khách chỉ tồn tại khi grant loại "lệnh" còn hạn **và** binding vai trò có quyền lệnh. Installer không tự tạo grant cho chính mình.
- **BR-ORG-04** Gán vai trò có quyền lệnh (`OPERATOR`, `SITE_ENGINEER`, `CONTROL_SUPERVISOR`) phải được audit và thông báo cho chủ tài sản của site.
- **BR-ORG-05** Site ở `planned` không ingest; ở `commissioning` ingest nhưng gắn cờ commissioning, loại khỏi KPI danh mục và availability; chỉ lệnh test trong checklist được phép (IL-10).
- **BR-ORG-06** Tài sản ở `maintenance`: lệnh tới tài sản đó bị từ chối, edge chạy mặc định/native cho tài sản đó; cảnh báo của tài sản vào trạng thái "ngoài dịch vụ".
- **BR-ORG-07** `suspended` yêu cầu lý do, bật kill switch theo site, chỉ giữ cảnh báo an toàn và kết nối.
- **BR-ORG-08** `decommissioned` là trạng thái cuối; không có chuyển ngược.

**Tiền điều kiện / hậu điều kiện.** Tiền: tenant và người dùng có `user.manage` hoặc `asset.configure`. Hậu: mọi thay đổi dữ liệu chủ có audit với giá trị trước/sau; thay đổi ảnh hưởng tính toán (kWp theo thời gian, sự kiện công tơ) tạo dirty bucket (FR-HIST-006).

**Dữ liệu vào / ra**

| Vào | Ra |
|---|---|
| Hồ sơ tổ chức, site, topology; nameplate; serial; điểm đo; grant; lời mời | Cây tài nguyên; sổ tài sản; trạng thái vòng đời; binding; danh sách mục thiếu; sự kiện tài sản cho M-HIST; audit |

**Phân quyền.** `tenant.configure`, `user.manage` (ORG_ADMIN); `asset.configure` (SITE_ENGINEER); `grant.issue` (chủ tài sản/ORG_ADMIN của tenant chủ); đọc: mọi vai trò trong phạm vi.

**Lỗi và trường hợp biên**

| Tình huống | Hành vi bắt buộc |
|---|---|
| Lời mời tới e-mail đã là người dùng tenant khác | Tạo binding mới cho cùng danh tính (một người có thể thuộc nhiều tenant), không tạo tài khoản trùng |
| Grant hết hạn khi người của installer đang mở phiên | Request kế tiếp bị từ chối 403 với lý do "grant hết hạn"; lệnh C3 họ đang chờ duyệt bị hủy |
| Đổi kWp (mở rộng) | Lưu theo thời gian; specific yield trước/sau dùng kWp tương ứng |
| Thay công tơ không khai báo | Bộ đếm giảm → `RESET_UNEXPLAINED` (FR-HIST-004), cảnh báo DQ gợi ý ghi sự kiện |
| Xóa tài sản có dữ liệu | Không xóa cứng; chuyển `decommissioned` cho tài sản |

**Tiêu chí chấp nhận**

- **AC-ORG-01** Given wizard ở bước thông tin site, When người dùng lưu mà không chọn `timezone`, Then hệ thống chặn và báo "Thiếu múi giờ (IANA)".
- **AC-ORG-02** Given site có BESS khai báo, When lưu wizard mà thiếu `MTR_POC`, Then site không thể chuyển `commissioning` và danh sách thiếu ghi "MTR_POC bắt buộc cho site có BESS/điều khiển".
- **AC-ORG-03** Given người dùng có binding `ORG_ADMIN` trên tenant và không có vai trò khác, When gọi API tạo lệnh `SET_ESS_P`, Then nhận từ chối `403 NO_COMMAND_PERMISSION` và sự kiện được audit.
- **AC-ORG-04** Given grant loại "lệnh" hết hạn lúc T, When người của installer gửi lệnh C1 lúc T + 1 s, Then lệnh bị từ chối và không có envelope nào được ký.
- **AC-ORG-05** Given grant còn 0 ngày tới mốc 90 ngày từ lần xem lại cuối, When job nhắc chạy, Then chủ tài sản nhận thông báo xem lại kèm danh sách quyền.
- **AC-ORG-06** Given site `commissioning`, When tính KPI danh mục ngày, Then site không có mặt trong tổng và availability.
- **AC-ORG-07** Given sự kiện thay công tơ với chỉ số cuối 1.000.000 Wh và chỉ số đầu 0 Wh lúc 10:00, When tính delta bucket 10:00–10:05, Then delta không âm, không bị gắn `RESET_UNEXPLAINED`.
- **AC-ORG-08** Given site `control_enabled = true`, When `ORG_ADMIN` yêu cầu decommission, Then hệ thống chặn và hướng dẫn tắt điều khiển trước.

**Phụ thuộc.** M-SEC (RBAC/PDP thực thi binding), M-HIST (sự kiện tài sản), M-INT (claim edge), [05 Domain](05-domain-model.html) (thực thể, enum vòng đời).

**Bằng chứng và độ tin cậy**

- [FACT] Huawei tách "O&M Authorization", quyền API và cho chủ sở hữu thu hồi — https://digitalpower.huawei.com/en/eu-data-act (qua kết quả tìm kiếm). Căn cứ cho FR-ORG-009. Độ tin cậy: Trung bình.
- [FACT] SolarEdge Site Admin quản lý User Role và Monitoring Access theo site — https://knowledge-center.solaredge.com/sites/kc/files/se-site-admin-in-solaredge-one-for-c&i-user-guide.pdf (qua kết quả tìm kiếm). Độ tin cậy: Trung bình.
- [FACT] FusionSolar dùng cây công ty → nhà máy → thiết bị; Company Admin/Installer/Owner (nghiên cứu trước, [workflows_data_model.md](../fusionsolar/04_ghi_chu_nghien_cuu/2_phan_ra_san_pham/workflows_data_model.md)). Độ tin cậy: Trung bình–Cao (ảnh thật + tài liệu).
- [FACT] Rollover/reset công tơ cần xử lý riêng — https://www.se.com/us/en/faqs/FA239195/ (qua kết quả tìm kiếm).
- [INFERENCE] Mô hình installer → nhiều chủ là thực tế Việt Nam (A §3.3). Chưa phỏng vấn (GAP-15).

---

### 5.2 M-DASH — Dashboard danh mục và site

**Mục đích nghiệp vụ.** Trả lời câu hỏi của operator: "site nào cần chú ý ngay, site có đang làm đúng kế hoạch và an toàn không" (H §4), và câu hỏi của chủ C&I: "hôm nay/tháng này tốn bao nhiêu, tiết kiệm bao nhiêu". Mã màn hình `UI-NN` do [09](09-ux-ui-specification.html) cấp.

**Persona.** P3 (chính, hằng ngày), P1/P6 (người xem), P2, P4.

**User story**

| ID | Là… | Tôi muốn… | Để… | FR |
|---|---|---|---|---|
| US-DASH-01 | Operator NOC (P3) | thấy danh sách site cần chú ý, sắp theo mức độ, kèm lý do bằng chữ | xử lý site nguy cấp trước | FR-DASH-001 |
| US-DASH-02 | Operator (P3) | biết site có đang chạy lịch dự phòng hay mất cloud | không hoảng khi mất kết nối và biết site vẫn được điều khiển cục bộ | FR-DASH-004 |
| US-DASH-03 | Energy manager (P2) | xem "hôm nay: thực tế và kế hoạch" có dải TOU | biết pin có xả đúng cao điểm không | FR-DASH-005 |
| US-DASH-04 | Chủ C&I (P1) có 1 site | vào thẳng dashboard site của mình | không phải đi qua danh mục | FR-DASH-007 |
| US-DASH-05 | Operator (P3) | chuyển nhanh giữa 300 site bằng tìm kiếm và deep-link từ e-mail | mở đúng site từ thông báo | FR-DASH-003 |

**Luồng chính (giám sát hằng ngày).** (1) Operator mở L1 → danh sách "cần chú ý" và bảng site. (2) Lọc theo tỉnh/KCN, trạng thái. (3) Chọn site → L2: header trạng thái, energy flow, biểu đồ hôm nay, KPI. (4) Đi tiếp L3/L4 (M-MON) hoặc console cảnh báo (M-ALM). Lỗi: dữ liệu cũ/offline hiển thị theo FR-DASH-008; không bao giờ hiện 0 thay "không có dữ liệu".

**Yêu cầu chức năng**

| ID | Yêu cầu | F- | Ưu tiên | Phát hành | Hạng·Gate | Căn cứ |
|---|---|---|---|---|---|---|
| FR-DASH-001 | L1 phải có danh sách "cần chú ý" sắp theo điểm ưu tiên: (1) cảnh báo Khẩn cấp/Cao chưa ack, (2) vượt/sắp vượt giới hạn xuất hoặc trần nhập, (3) mất kết nối > `T_offline_alarm_*`, (4) edge chạy lịch dự phòng/M2 tạm ngưng, (5) BESS lệch kế hoạch. Mỗi dòng có lý do bằng chữ. | F-DASH-01 | P0 | MVP | — | H-P01 |
| FR-DASH-002 | L1 phải có bảng site cấu hình cột: trạng thái (icon + chữ), site, khách hàng, tuổi dữ liệu, P lưới (Nhập/Xuất), thanh nhập/trần, PV kW và % kWp, BESS chế độ + SOC + P (Sạc/Xả), EV kW, đếm cảnh báo theo mức, kế hoạch đúng/lệch; lọc theo tổ chức, tỉnh/KCN, loại tài sản, trạng thái. | F-DASH-02 | P0 | MVP | — | H §3.1 |
| FR-DASH-003 | Hệ thống phải có bộ chuyển site toàn cục (breadcrumb Org ▸ Site ▸ Tài sản, tìm kiếm, phím tắt, gần đây/ghim) và URL chứa orgId/siteId/assetId để deep-link từ thông báo; đổi site giữ tab hiện tại. | F-DASH-03 | P0 | MVP | — | H-P02 |
| FR-DASH-004 | L2 phải luôn hiện header: `site_strategy` hiện hành, nguồn lệnh đang thắng (mức arbiter), trạng thái edge (trực tuyến / mất cloud – đang chạy kế hoạch #n tới HH:MM / lịch dự phòng / chế độ native), tuổi dữ liệu, dải TOU hiện tại, LOCAL/REMOTE, Gate, múi giờ site nếu khác trình duyệt. | F-DASH-04 | P0 | MVP | — | H-P03; K §6 #17 |
| FR-DASH-005 | L2 phải có biểu đồ ngày địa phương: P lưới (nhập trên/xuất dưới trục), PV, BESS, SOC, dải TOU từ biểu giá hiệu lực, trần nhập/giới hạn xuất, phần tương lai nét đứt theo kế hoạch. Site PV-only ẩn chuỗi BESS/kế hoạch. | F-DASH-05 | P0 | MVP | — | H-P04 |
| FR-DASH-006 | Hệ thống phải có thẻ KPI site và danh mục theo 03 §6 (nhập, xuất, PV, tự tiêu thụ, tự cung, hóa đơn bóng, Pmax, vi phạm xuất, availability dữ liệu); mỗi giá trị kèm nhãn chất lượng và "≈ ước tính" khi cần. | F-DASH-06 | P0 | MVP | — | C §3.14; K §6 #12 |
| FR-DASH-007 | Người dùng chỉ có 1 site phải vào thẳng L2; menu rút gọn theo vai trò. | F-DASH-07 | P0 | MVP | — | H §3.2 |
| FR-DASH-008 | Mọi màn dashboard phải áp quy tắc hiển thị: số không dấu + chữ hướng; trạng thái mã hóa ≥ 2 kênh (màu + hình/chữ); dữ liệu theo `freshness` (LIVE/DELAYED/OLD/OFFLINE/NO_DATA); "—" cho không có dữ liệu; tổng danh mục chỉ cộng đại lượng cộng được; số tiền/ngày giờ theo locale vi/en. | F-DASH-02, F-DASH-06, F-MON-04 | P0 | MVP | — | K §6 #4, #9; H §3.14, §3.16 |
| FR-DASH-009 | Hệ thống nên có chế độ NOC/màn lớn (tile, sparkline P lưới 24 h có ngưỡng) và hai mật độ Compact/Comfortable lưu theo người dùng. | F-DASH-08 | P1 | Phase 1 | — | H-P18 |
| FR-DASH-010 | Hệ thống nên có giao diện mobile: cảnh báo + ack, trạng thái site, energy flow, kế hoạch chỉ xem. Không có lệnh C2/C3 trên mobile ở Phase 1. | F-DASH-10 | P1 | Phase 1 | — | H-P19; Q-H06 |
| FR-DASH-011 | Hệ thống nên có màn kiosk công khai chữ lớn (energy flow, sản lượng, CO₂ ước tính có nguồn hệ số), tự làm mới, watermark "dữ liệu lúc…". | F-DASH-11 | P1 | Phase 1 | — | H-P18 |
| FR-DASH-012 | Hệ thống nên cho lưu view (bộ lọc, cột, khoảng thời gian) theo người dùng và chia sẻ trong tenant. | F-DASH-12 | P1 | Phase 1 | — | H §3.1 |
| FR-DASH-013 | Hệ thống có thể có chế độ bản đồ site theo tỉnh/KCN tô theo trạng thái. | F-DASH-09 | P2 | Phase 2 | — | H §3.1 |

**Quy tắc nghiệp vụ**

- **BR-DASH-01** Không bao giờ hiển thị 0 khi giá trị là không có dữ liệu; dùng "—" và tooltip nguyên nhân.
- **BR-DASH-02** Tổng danh mục chỉ gồm site `active`; mỗi tổng ghi số site có dữ liệu OLD/OFFLINE ("gồm dữ liệu cũ của 3 site").
- **BR-DASH-03** KPI tỷ số (tự tiêu thụ, tự cung) của danh mục tính lại từ tổng tử và tổng mẫu, không lấy trung bình tỷ số (K §6 #12).
- **BR-DASH-04** "Hôm nay" của danh mục = tổng các ngày địa phương của từng site cùng ngày lịch, có ghi chú khi danh mục nhiều múi giờ (F §3.9).
- **BR-DASH-05** Thông tin "điều khiển" trên dashboard là chỉ đọc; mọi thao tác lệnh đi qua hộp lệnh của M-BESS/M-GRID và PDP.

**Tiền/hậu điều kiện.** Tiền: người dùng có `site.read` trên ít nhất một site. Hậu: không thay đổi dữ liệu (trừ lưu view P1).

**Dữ liệu vào / ra.** Vào: giá trị hiện tại + `freshness` (M-MON), KPI và chất lượng (M-HIST), cảnh báo (M-ALM), kế hoạch và trạng thái arbiter (M-OPT), dải TOU (M-TAR), trạng thái điều khiển (M-SEC). Ra: màn hình; không có dữ liệu ghi.

**Phân quyền.** `site.read`; số tiền ẩn với vai trò/kiosk nếu chủ site tắt "hiển thị chi phí".

**Lỗi và trường hợp biên**

| Tình huống | Hành vi |
|---|---|
| Site chưa gán biểu giá | Thẻ chi phí "N/A — chưa gán biểu giá", không hiện 0 ₫ |
| Site không có `MTR_POC` | Thẻ nhập/xuất, thanh trần/giới hạn ẩn kèm ghi chú |
| Danh mục 500 site, 40 site OFFLINE | Danh sách cần chú ý gom thành 1 dòng mỗi site; nếu cùng nguyên nhân (cùng edge vùng) gợi ý nguyên nhân chung |
| Người dùng ở múi giờ khác site | Trục thời gian theo giờ site, nhãn hiển thị offset |

**Tiêu chí chấp nhận**

- **AC-DASH-01** Given site A có cảnh báo Cao chưa ack và site B chỉ có dữ liệu DELAYED, When mở L1, Then site A đứng trước site B và dòng của A ghi lý do "1 cảnh báo Cao chưa xác nhận".
- **AC-DASH-02** Given giá trị P lưới chưa từng nhận, When hiển thị bảng site, Then ô hiện "—", không hiện "0 kW".
- **AC-DASH-03** Given P lưới = −120 kW theo quy ước chuẩn (xuất), When hiển thị, Then UI hiện "Xuất 120 kW" (không có dấu âm).
- **AC-DASH-04** Given edge OFFLINE từ 13:40 và đang có kế hoạch #123 hạn tới 23:45 đã xác nhận trước đó, When mở L2, Then header hiện "Mất kết nối cloud từ 13:40 — site vẫn điều khiển cục bộ theo kế hoạch #123 tới 23:45".
- **AC-DASH-05** Given tổng tự tiêu thụ hai site: site 1 (PV 100 kWh, tự dùng 90) và site 2 (PV 900 kWh, tự dùng 450), When tính KPI danh mục, Then kết quả là 54,0% (540/1.000), không phải 70% (trung bình tỷ số).
- **AC-DASH-06** Given người dùng chỉ có binding trên 1 site, When đăng nhập, Then trang đầu là L2 của site đó.

**Phụ thuộc.** M-MON, M-HIST, M-ALM, M-OPT, M-TAR, M-SEC; [09 UX/UI](09-ux-ui-specification.html) cho bố cục.

**Bằng chứng và độ tin cậy**

- [FACT] FusionSolar có cột cấu hình được và lưu theo người dùng, có donut trạng thái nhưng không có thứ tự "cần chú ý", không hiện tuổi dữ liệu (ảnh thật, nghiên cứu FS trước; H #8). Độ tin cậy: Cao cho quan sát giao diện.
- [FACT] FusionSolar có dashboard màn lớn và kiosk — https://solisdepot.com/wp-content/uploads/2023/03/FusionSolar-Smart-PV-Management-System-7.0-After-sales-Technical-Training-Slides.pptx.pdf (qua kết quả tìm kiếm).
- [UNKNOWN] Không có bằng chứng giao diện của đối thủ khác ngoài FusionSolar (K §3.7, Q-H01). Mọi đề xuất bố cục là PROPOSAL.

---

### 5.3 M-MON — Giám sát thời gian thực

**Mục đích nghiệp vụ.** Thu và hiển thị trạng thái hiện tại của site và thiết bị với độ tươi trung thực, energy flow có hướng, trang thiết bị L3/L4 và trạng thái edge. Đây là nền giá trị cho mọi site, kể cả PV-only không có edge (qua connector cloud).

**Persona.** P3 (chính), P4/P5 (chẩn đoán), P1 (energy flow).

**User story**

| ID | Là… | Tôi muốn… | Để… | FR |
|---|---|---|---|---|
| US-MON-01 | Operator (P3) | biết số trên màn hình đo lúc nào và có còn tươi | không ra quyết định trên dữ liệu cũ | FR-MON-002, FR-MON-005 |
| US-MON-02 | Chủ C&I (P1) | thấy luồng năng lượng có chữ Nhập/Xuất/Sạc/Xả | hiểu ngay nhà máy đang mua hay bán điện | FR-MON-004 |
| US-MON-03 | Kỹ sư (P4) | xem giá trị thanh ghi thô, hệ số scale, mã quality | xác minh map điểm khi commissioning | FR-MON-007 |
| US-MON-04 | Operator (P3) | giám sát site PV-only không có edge qua cloud hãng | có giá trị giám sát mà không cần lắp phần cứng | FR-MON-003 |
| US-MON-05 | Kỹ sư (P4) | xem sức khỏe edge (đồng hồ, buffer, chu kỳ điều khiển) | biết chất lượng dữ liệu và an toàn của vòng điều khiển | FR-MON-008 |

**Luồng chính.** Edge lấy mẫu 1 s → tổng hợp tại nguồn 5 s/60 s/300 s → gửi lô nén qua MQTT → cloud ingest idempotent → cập nhật "giá trị hiện tại" nếu `ts` mới hơn → tính `freshness` → hiển thị. Lỗi: dữ liệu sai thứ tự không ghi đè giá trị hiện tại; dữ liệu backfill đi đường trễ (WF-14).

**Yêu cầu chức năng**

| ID | Yêu cầu | F- | Ưu tiên | Phát hành | Hạng·Gate | Căn cứ |
|---|---|---|---|---|---|---|
| FR-MON-001 | Cloud phải nhận telemetry từ edge theo lớp C1 (5 s), C2 (60 s), C3 (300 s hoặc khi đổi), thanh ghi ở mọi biên 5 phút, sự kiện tức thời; "giá trị hiện tại" chỉ cập nhật khi `ts` mới hơn `last_ts`. | F-MON-01 | P0 | MVP | — | K §6 #19; E §3.17 |
| FR-MON-002 | Mọi mẫu phải mang `ts` (edge thu, UTC ms, khóa chính), `ts_src` (tùy chọn) và `ts_ingest`. UI hiển thị "đo lúc" theo `ts`; chỉ dùng `ts_src` cho sự kiện/alarm và dữ liệu khoảng của công tơ khi `src_clock_state = SYNCED`. | F-MON-01 | P0 | MVP | — | K §6 #7, R-04 |
| FR-MON-003 | Site không có edge phải giám sát được qua connector cloud hãng chỉ đọc (MVP: Huawei Northbound), quality `UNCERTAIN_VENDOR_CLOUD`, rate limiter theo endpoint, backfill ban đêm 7 ngày. | F-MON-02 | P0 | MVP | — | K §6 #13 |
| FR-MON-004 | Hệ thống phải hiển thị energy flow với nút PV, Lưới, BESS, Tải, EV, Máy phát (ẩn nút không có); cạnh có hướng, giá trị không âm, mũi tên tĩnh + chữ Nhập/Xuất/Sạc/Xả; cạnh lấy từ thuật toán phân bổ backend (FR-HIST-009) có nhãn "ước tính" và `attribution_version`; huy hiệu lệch cân bằng; dừng hoạt ảnh khi dữ liệu OLD/OFFLINE; tôn trọng reduced-motion. | F-MON-03 | P0 | MVP | — | H-P05; K §6 #11 |
| FR-MON-005 | Hệ thống phải tính `freshness ∈ {LIVE, DELAYED, OLD, OFFLINE, NO_DATA}` theo chu kỳ mong đợi của nguồn (bảng §2) và hiển thị: DELAYED kèm "trễ N s"; OLD chữ xám nghiêng + "cập nhật HH:MM (N phút trước)"; OFFLINE giá trị cuối + "Mất kết nối từ HH:MM"; NO_DATA "—". | F-MON-04 | P0 | MVP | — | H-P14; K R-06 |
| FR-MON-006 | Hệ thống phải có danh sách thiết bị theo loại và trang chi tiết L3: giá trị chính, trạng thái, "đo lúc", nguồn dữ liệu (edge/cloud hãng), trạng thái driver; inverter có bảng MPPT/string V-I. | F-MON-05 | P0 | MVP | — | H §3.0 |
| FR-MON-007 | Hệ thống phải có trang chẩn đoán L4: điểm tín hiệu thô, giá trị thanh ghi, hệ số scale, mã quality tầng điểm (GOOD/UNCERTAIN_*/BAD_*), `driver_id@version`, nhật ký lỗi bus. | F-MON-06 | P0 | MVP | — | E §3.18 |
| FR-MON-008 | Hệ thống phải có trang trạng thái edge: online/offline, `clock_state` và offset, độ sâu và dung lượng buffer, firmware, config version, kế hoạch đang chạy hoặc fallback, thời lượng chu kỳ điều khiển (p50/p99). | F-MON-07 | P0 | MVP | — | E §3.12 G7, G13 |
| FR-MON-009 | Hệ thống phải đọc cảm biến bức xạ/thời tiết (G_POA, G_hor, T_module, T_ambient) và phát hiện cảm biến đóng băng (cờ `FROZEN`). | F-MON-08 | P0 | MVP | — | C §3.11 |
| FR-MON-010 | Hệ thống phải đọc submeter `MTR_LOAD_i` và tính "tải không đo" = tải tính toán − Σ submeter, hiển thị theo nhánh; giá trị âm của tải không đo không bị ép về 0 mà gắn cờ kiểm tra. | F-MON-09 | P0 | MVP | — | C §3.3 |
| FR-MON-011 | Hệ thống nên sinh SLD chỉ đọc từ mô hình tài sản, đánh dấu vị trí công tơ, ranh giới đo, trạng thái máy cắt bằng ký hiệu + chữ. | F-MON-10 | P1 | Phase 1 | — | H-P06 |
| FR-MON-012 | Edge nên có trang HMI cục bộ tối giản (trạng thái, energy flow, cảnh báo, chế độ, interlock, LOCAL/REMOTE) dùng khi mất Internet, có đăng nhập cục bộ không dùng mật khẩu mặc định chung. | F-MON-11 | P1 | Phase 1 | — | H-P21; K §3.7 |
| FR-MON-013 | Kỹ sư nên yêu cầu được luồng 1 s tạm thời (mặc định 15 phút, tối đa 60 phút) cho một site; edge tự dừng khi hết hạn. | F-MON-12 | P1 | Phase 1 | — | F-P04 |

**Quy tắc nghiệp vụ**

- **BR-MON-01** `freshness` (độ tươi hiển thị) tách khỏi cờ `FROZEN` của chuỗi (giá trị đóng băng bất thường) và khỏi `UNCERTAIN_STALE` của điểm (quá `max_age_s`) (K R-06).
- **BR-MON-02** Dữ liệu qua connector cloud không bao giờ dùng cho điều khiển (K R-09).
- **BR-MON-03** Trạng thái sạc/xả hiển thị lấy từ PCS/BMS, không suy từ dấu của P (K §6 #4).
- **BR-MON-04** Site OFFLINE: một cảnh báo kết nối, cảnh báo giá trị của thiết bị con bị chặn (FR-ALM-004).

**Tiền/hậu điều kiện.** Tiền: site `commissioning` hoặc `active`; edge claim hoặc connector gắn. Hậu: chuỗi thô lưu theo FR-HIST-001.

**Dữ liệu vào / ra**

| Vào | Ra |
|---|---|
| Lô telemetry `{edge_id, stream, seq, batch_ts, points[pid, ts, v, q, ts_src?]}`; dữ liệu connector cloud; trạng thái edge | Giá trị hiện tại + `freshness`; energy flow; trang L3/L4; trạng thái edge; ack theo `seq` cho edge |

**Phân quyền.** `site.read` cho L2/L3; L4 (thanh ghi thô, nhật ký bus) chỉ `TECHNICIAN`, `OPERATOR`, `SITE_ENGINEER`, `CONTROL_SUPERVISOR` (dữ liệu D2 vận hành). Burst mode: `SITE_ENGINEER`.

**Lỗi và trường hợp biên**

| Tình huống | Hành vi |
|---|---|
| Mẫu đến với `ts` cũ hơn giá trị hiện tại | Lưu vào chuỗi, không đổi giá trị hiện tại |
| Edge `UNSYNCED` | Mẫu mang `UNCERTAIN_CLOCK`; UI ghi "đồng hồ edge chưa đồng bộ" |
| Connector cloud bị hãng throttle | Giữ giá trị cuối với freshness đúng; không hiện số cũ như mới; cảnh báo sau `T_offline_alarm_connector` |
| Thiết bị trả sentinel (ví dụ 0xFFFF) | `BAD_DEVICE`, hiển thị "—" |
| Tổng PV + lưới + BESS ≠ tải đo (lệch cân bằng) | Huy hiệu "lệch cân bằng N%" trên energy flow; không tự điều chỉnh |

**Tiêu chí chấp nhận**

- **AC-MON-01** Given điểm C1 có chu kỳ mong đợi 5 s và mẫu cuối cách đây 12 s, When hiển thị, Then trạng thái là DELAYED và có chữ "trễ 12 s".
- **AC-MON-02** Given điểm C1 có mẫu cuối cách đây 26 s, When hiển thị, Then giá trị chữ xám nghiêng với "cập nhật HH:MM:SS".
- **AC-MON-03** Given edge gửi heartbeat mỗi 30 s và lỡ 3 heartbeat liên tiếp, When tới giây 90 ± 5 sau heartbeat cuối, Then edge chuyển OFFLINE trên UI.
- **AC-MON-04** Given cloud đã có giá trị P lúc 10:00:10, When nhận mẫu P có `ts` 10:00:05, Then giá trị hiện tại vẫn là mẫu 10:00:10.
- **AC-MON-05** Given BESS đang sạc 50 kW theo trạng thái PCS, When vẽ energy flow, Then cạnh vào BESS có chữ "Sạc 50 kW" và mũi tên hướng vào BESS.
- **AC-MON-06** Given site chỉ có connector Huawei, When mở trang thiết bị, Then nguồn dữ liệu ghi "Cloud hãng (≈ 5 phút)" và không có nút lệnh nào.
- **AC-MON-07** Given cảm biến G_POA không đổi giá trị trong 2 h giữa 10:00 và 14:00 giờ site, When job L0 chạy, Then chuỗi được gắn cờ `FROZEN`.

**Phụ thuộc.** M-INT (uplink, driver), M-HIST (lưu trữ, phân bổ), M-ALM (cảnh báo kết nối), [07 Tích hợp](07-device-integration.md) (định dạng payload), [06 Kiến trúc](06-system-architecture.html).

**Bằng chứng và độ tin cậy**

- [FACT] FusionSolar lấy mẫu 5 phút; Northbound pull 5 phút, có hạn mức, không webhook (nghiên cứu FS trước; F #1). Độ tin cậy: Trung bình–Cao.
- [FACT] meteocontrol hỏi lại dữ liệu Huawei 7 ngày mỗi đêm — https://help-center.meteocontrol.com/en/vcom-cloud/latest/huawei-fusionsolar-api-1 (qua kết quả tìm kiếm).
- [FACT] OpenEMS đo thời lượng cycle — https://openems.github.io/openems.io/openems/latest/edge/architecture.html (qua kết quả tìm kiếm).
- [FACT] PR cần bức xạ mặt phẳng tấm (POA) — https://pvpmc.sandia.gov/modeling-guide/5-ac-system-output/pv-performance-metrics/performance-ratio/ (qua kết quả tìm kiếm).
- [PROPOSAL] Ngưỡng độ tươi 2×/5× chu kỳ là đề xuất của H, chưa kiểm thử với người dùng.

---

### 5.4 M-HIST — Lịch sử, chất lượng dữ liệu, phân tích

**Mục đích nghiệp vụ.** Lưu chuỗi thời gian, tính điện năng **đúng để tính tiền** từ thanh ghi, tổng hợp theo ngày địa phương, xử lý dữ liệu trễ, gắn cờ chất lượng và cân bằng/phân bổ luồng năng lượng. Mọi KPI, báo cáo và hóa đơn bóng chỉ đáng tin bằng lớp này. Kiến trúc lưu trữ (TimescaleDB + Parquet) là điều kiện của 06, phụ thuộc kiểm tra giấy phép TSL và PoC 1.000 site (K §6 #25).

**Persona.** PO (vận hành dữ liệu), P3/P4 (trend, DQ), P2 (phân tích), P1 (gián tiếp qua KPI).

**User story**

| ID | Là… | Tôi muốn… | Để… | FR |
|---|---|---|---|---|
| US-HIST-01 | Energy manager (P2) | điện năng tháng khớp với chỉ số công tơ | tin được hóa đơn bóng | FR-HIST-004 |
| US-HIST-02 | Operator (P3) | biết dữ liệu đầy đủ đến thời điểm nào | không đọc nhầm số chưa đủ | FR-HIST-006 |
| US-HIST-03 | Kỹ sư (P4) | xem nhiều chuỗi trên các panel đồng bộ trục thời gian, có dải TOU và sự kiện lệnh | chẩn đoán vì sao pin không xả lúc cao điểm | FR-HIST-010 |
| US-HIST-04 | Chủ tài sản (P6) | mỗi KPI ghi rõ đo, tính hay ước tính và độ phủ | bảo vệ được số liệu trước bên cho vay | FR-HIST-007 |
| US-HIST-05 | Chủ C&I (P1) | biết điện xuất lưới đến từ PV hay từ pin | báo cáo đúng theo NĐ 243 | FR-HIST-009 |

**Luồng chính.** Ingest (FR-HIST-002) → tính delta thanh ghi (FR-HIST-004) → tổng hợp 5 phút/1 h (FR-HIST-005) → job ngày/tháng địa phương → cân bằng và phân bổ (FR-HIST-009) → KPI có cờ (FR-HIST-007). Dữ liệu trễ: WF-14.

**Yêu cầu chức năng**

| ID | Yêu cầu | F- | Ưu tiên | Phát hành | Hạng·Gate | Căn cứ |
|---|---|---|---|---|---|---|
| FR-HIST-001 | Mỗi chuỗi phải được khai báo trong catalog trước khi ingest: `kind` (gauge/register/state/event/setpoint), đơn vị, `agg_rule`, lớp tần suất, phiên bản hệ số. Gauge, register, state lưu ở ba bảng tách biệt. | F-HIST-01 | P0 | MVP | — | F-P01, F-P02 |
| FR-HIST-002 | Ingest phải idempotent theo `(series_id, ts)`; ack theo `seq` của edge; bản trùng cùng giá trị bị bỏ qua; khác giá trị thì giữ bản `rev` cao hơn và ghi audit. | F-HIST-01 | P0 | MVP | — | F-P06; E §3.17 |
| FR-HIST-003 | Raw và hợp đồng edge phải dùng W, Wh, var, VA, varh (bộ đếm int64 Wh); aggregate, KPI, báo cáo, API dùng kW/kWh; tên trường có hậu tố đơn vị (`_w`, `_wh`, `_kw`, `_kwh`). Chuyển đổi chỉ ở ranh giới raw → aggregate. | F-HIST-01 | P0 | MVP | — | K §6 #6, R-03 |
| FR-HIST-004 | Hệ thống phải tính điện năng từ thanh ghi tích lũy bằng máy trạng thái: OK / SUSPECT_SPIKE / ROLLOVER (dùng `R_wrap` của driver) / sự kiện thay công tơ (FR-ORG-010) / RESET_UNEXPLAINED → tích phân P có cờ `ESTIMATED_FROM_POWER`; chống rung ±2 LSB; luôn giữ raw để tính lại. Điện năng lưu theo cặp không âm (nhập/xuất, sạc/xả). | F-HIST-02 | P0 | MVP | — | K §6 #5; C §3.15 |
| FR-HIST-005 | Hệ thống phải tổng hợp 5 phút và 1 h khóa `bucket_start`, khoảng nửa mở `[start, start+Δ)`; aggregate ghép được (integral, covered_s, min, max, first, last, count), không avg-of-avg; bảng ngày/tháng địa phương khóa `(site, local_date)` do job có phiên bản ghi; cửa sổ 15/30 phút cho demand. Dữ liệu nhãn cuối khoảng (load profile EVN) được chuyển sang quy ước này khi ingest. | F-HIST-03 | P0 | MVP | — | K §6 #8, R-05 |
| FR-HIST-006 | Hệ thống phải xử lý dữ liệu trễ: refresh cửa sổ ≥ 7 ngày; dữ liệu trễ hơn đi `late_landing` + `dirty_bucket` + job tính lại; watermark `complete_until` theo site hiển thị trên UI; báo cáo đã phát hành được restatement có phiên bản (FR-REP-005). | F-HIST-04 | P0 | MVP | — | F-P06, F-P10 |
| FR-HIST-007 | Hệ thống phải gắn chất lượng ba tầng: tầng điểm (mã E: GOOD/UNCERTAIN_*/BAD_*), tầng chuỗi (nguồn gốc MEASURED/CALCULATED/ESTIMATED/FORECAST/MANUAL/SUBSTITUTED + bitmask INTERPOLATED/SUSPECT/OUT_OF_RANGE/FROZEN/CLOCK_SUSPECT/PARTIAL/LATE/REVISED/ROLLOVER/RESET/CURTAILED/ISLANDED/MAINTENANCE), tầng KPI (MEASURED/INTERPOLATED/ESTIMATED/PARTIAL/MISSING/SUSPECT); lan truyền "yếu nhất"; mỗi KPI có `coverage_pct`, `calc_version`. | F-HIST-05 | P0 | MVP | — | K §6 #9, R-06 |
| FR-HIST-008 | Hệ thống phải lấp khoảng trống theo bảng F §3.8: gauge ≤ 3 chu kỳ nối liền, > 3 chu kỳ đứt nét; thanh ghi có hai đầu → phân bổ theo profile, cờ `INTERPOLATED`; mất đầu/cuối → tích phân P (`ESTIMATED`) hoặc `MISSING`; không bao giờ tạo Pmax từ dữ liệu nội suy; thay thế "ngày tương tự" chỉ khi người dùng bật. | F-HIST-05, F-HIST-03 | P0 | MVP | — | F-P12 |
| FR-HIST-009 | Hệ thống phải có **một** thuật toán cân bằng và phân bổ luồng năng lượng ở backend có `attribution_version`, chạy chu kỳ ≤ 1 phút trên dữ liệu thô rồi cộng dồn: `P_cons = P_grid + P_pv + P_bess + P_gen`; cạnh PV→tải, PV→pin, PV→lưới, lưới→tải, lưới→pin, pin→tải, pin→lưới; kết quả gắn "ước tính". `attribution_version = 1` dùng thứ tự PV→tải trước, là đề xuất chờ văn bản. | F-HIST-06 | P0 | MVP | — | K §6 #11; C §3.4 |
| FR-HIST-010 | Hệ thống phải có trend explorer: nhiều panel xếp chồng đồng bộ trục thời gian, ≤ 2 đơn vị/panel, overlay dải TOU và sự kiện (lệnh, cảnh báo, đổi chế độ), khoảng trống không nối, tô nhạt ESTIMATED, legend không phân trang, so sánh nhiều ngày trên cùng trục; độ phân giải tự chọn theo khoảng (raw ≤ 7 ngày; 5 phút ≤ 93 ngày; ngày cho dài hơn). | F-HIST-07 | P0 | MVP | — | H-P09; F §3.14 |
| FR-HIST-011 | Hệ thống phải áp lưu giữ: raw nóng 13 tháng (nén sau 7 ngày), tổng hợp 5 phút 5 năm, giờ/ngày/tháng theo vòng đời dự án; gói có thể kéo dài nhưng không rút ngắn dưới mức chuẩn. | F-HIST-10 | P0 | MVP | — | K §6 #31 |
| FR-HIST-012 | Hệ thống nên so sánh chuỗi chuẩn hóa (kWh/kWp, kW/kW định mức) giữa nhiều site/thiết bị cùng loại. | F-HIST-08 | P1 | Phase 1 | — | H §3.9 |
| FR-HIST-013 | Hệ thống nên tính residual cân bằng / E_cons theo chu kỳ và cảnh báo DQ khi vượt ngưỡng (gợi ý sai CT, sai dấu, lệch pha thời gian). | F-HIST-09 | P1 | Phase 1 | — | C-P03 |
| FR-HIST-014 | Người có quyền nên nhập giá trị thủ công/thay thế cho khoảng hỏng (origin MANUAL/SUBSTITUTED, cờ REVISED), bắt buộc lý do, kích hoạt tính lại và restatement. | F-HIST-11 | P1 | Phase 1 | — | F §3.15 |
| FR-HIST-015 | Hệ thống nên có bảng điều khiển DQ: coverage theo thiết bị, độ trễ ingest p50/p95, tỷ lệ SUSPECT, số reset/rollover, lệch Σ inverter so với công tơ PV; tạo ticket DQ. | F-HIST-12 | P1 | Phase 1 | — | F-P23 |
| FR-HIST-016 | Hệ thống nên phát hiện lệch đồng hồ/lệch pha (reset `daily_yield` không gần 00:00 địa phương; tương quan chéo POC–PV) và gắn `CLOCK_SUSPECT`. | F-HIST-13 | P1 | Phase 1 | — | C §3.15 |
| FR-HIST-017 | Hệ thống nên xuất raw và 5 phút sang Parquet trên object storage, partition theo site/tháng, có cột quality. | F-HIST-14 | P1 | Phase 1 | — | F-P14 |

**Quy tắc nghiệp vụ**

- **BR-HIST-01** Lưu UTC; ngày, tháng, TOU, kỳ hóa đơn tính theo `timezone` của site. Việt Nam: ngày D = `[D−1 17:00Z, D 17:00Z)`.
- **BR-HIST-02** Không lưu điện năng net làm dữ liệu gốc; luôn cặp không âm.
- **BR-HIST-03** Có thanh ghi thì không tính kWh bằng tích phân P; tích phân chỉ là dự phòng, luôn có cờ.
- **BR-HIST-04** KPI tỷ số tính lại từ tử và mẫu; PR = N/A khi không có cảm biến POA (K §6 #12).
- **BR-HIST-05** FORECAST không bao giờ trộn vào KPI thực tế.
- **BR-HIST-06** Mọi phép tính có phiên bản (`calc_version`, `attribution_version`); đổi thuật toán không ghi đè số đã phát hành mà tạo phiên bản mới.

**Tiền/hậu điều kiện.** Tiền: chuỗi có trong catalog; site có `timezone`. Hậu: aggregate và KPI có cờ; watermark cập nhật.

**Dữ liệu vào / ra**

| Vào | Ra |
|---|---|
| Mẫu gauge/register/state/event; sự kiện tài sản; cấu hình điểm đo (`R_wrap`, `sign_convention`, ranh giới); dữ liệu trễ | Chuỗi 5 phút/1 h; bảng ngày/tháng địa phương; `interval_energy`; cân bằng và cạnh phân bổ; KPI + quality + coverage; watermark; dirty bucket |

**Phân quyền.** Đọc: `site.read`. Sửa/thay dữ liệu (P1): `SITE_ENGINEER`, `OPERATOR` với lý do; mọi sửa có audit.

**Lỗi và trường hợp biên**

| Tình huống | Hành vi |
|---|---|
| Bộ đếm giảm, không có sự kiện, giá trị trước gần `R_wrap` | ROLLOVER: delta = R_wrap − trước + sau |
| Bộ đếm giảm, không gần `R_wrap`, không có sự kiện | RESET_UNEXPLAINED; delta bucket dùng tích phân P (ESTIMATED); cảnh báo DQ |
| Delta 5 phút > định mức × 1,2 × Δt | SUSPECT_SPIKE; loại khỏi KPI cho tới khi xác nhận hoặc bucket kế tiếp hợp lý |
| Dữ liệu trễ 10 ngày (rơi vào chunk đã nén) | Đường trễ: `late_landing` → dirty bucket → tính lại; không mất |
| Site đổi `timezone` | Tính lại ngày/tháng địa phương, restatement |

**Tiêu chí chấp nhận**

- **AC-HIST-01** Given bộ đếm Wh tại 10:00:00 = 1.000.000 và tại 10:05:00 = 1.004.200, When tính bucket `[10:00, 10:05)`, Then E = 4,2 kWh, nguồn gốc MEASURED.
- **AC-HIST-02** Given bộ đếm uint32 với `R_wrap` = 4.294.967.296 Wh, giá trị trước 4.294.967.000 và sau 500, When tính delta, Then delta = 796 Wh, cờ ROLLOVER.
- **AC-HIST-03** Given bộ đếm giảm từ 50.000 xuống 100 không có sự kiện tài sản, When tính delta, Then bucket mang RESET_UNEXPLAINED, dùng tích phân P có cờ ESTIMATED và tạo cảnh báo DQ.
- **AC-HIST-04** Given edge mất mạng 6 ngày rồi xả buffer, When backfill hoàn tất, Then coverage của 6 ngày đó = 100% đối với điểm có dữ liệu ở edge, các bucket liên quan được tính lại ≤ 1 h sau khi dữ liệu tới, và watermark tiến tới thời điểm hiện tại.
- **AC-HIST-05** Given cửa sổ 30 phút có một bucket 5 phút `INTERPOLATED`, When tính Pmax tháng, Then cửa sổ đó được liệt kê `UNCERTAIN` và không được chọn làm Pmax.
- **AC-HIST-06** Given một KPI có đầu vào MEASURED và một đầu vào ESTIMATED, When tính KPI, Then quality của KPI là ESTIMATED.
- **AC-HIST-07** Given ngày địa phương 2026-10-10 ở site `Asia/Ho_Chi_Minh`, When job ngày chạy, Then nó gộp dữ liệu `[2026-10-09T17:00Z, 2026-10-10T17:00Z)` và hoàn tất trước 02:00 giờ site.
- **AC-HIST-08** Given cùng một mẫu `(series_id, ts)` gửi hai lần cùng giá trị, When ingest, Then chỉ có một bản ghi và không có cảnh báo.

**Phụ thuộc.** M-ORG (sự kiện tài sản, timezone), M-INT (`seq`, `R_wrap` trong driver), M-REP, [05 Domain](05-domain-model.html) (series, quality), [06 Kiến trúc](06-system-architecture.html) (ADR lưu trữ, PoC F-P25).

**Bằng chứng và độ tin cậy**

- [FACT] Compression, continuous aggregate, retention của TimescaleDB thuộc bản Community (TSL), không được bán như DBaaS — https://www.tigerdata.com/docs/about/latest/timescaledb-editions (qua kết quả tìm kiếm). [UNKNOWN] TSL có cho phép SaaS EMS không (Q-F01, chặn ADR lưu trữ).
- [FACT] Rollover công tơ cần xử lý — https://www.se.com/us/en/faqs/FA239195/ (qua kết quả tìm kiếm).
- [FACT] Điện xả BESS tính vào điện dư theo tóm tắt NĐ 243 — https://www.reccessary.com/en/news/vietnam-solar-grid-export-dppa (qua kết quả tìm kiếm). [INFERENCE] Phân bổ nguồn điện xuất là quy ước kế toán; thứ tự PV→tải trước là PROPOSAL chờ văn bản (Q-C04).
- [FACT] FusionSolar có mục "Data Repair" — https://support.huawei.cn/enterprise/en/doc/EDOC1100541798/ea4fbfa/data-repair (qua kết quả tìm kiếm).

---

### 5.5 M-REP — Báo cáo, xuất dữ liệu, bằng chứng

**Mục đích nghiệp vụ.** Cung cấp báo cáo định kỳ có phiên bản, minh bạch chi phí theo TOU (giá trị số 2 ở Việt Nam), bằng chứng tuân thủ giới hạn xuất (giá trị số 1) và xuất dữ liệu đầy đủ. Không quảng cáo % tiết kiệm; tiết kiệm luôn là hóa đơn bóng so với baseline phản thực cùng phiên bản biểu giá (K §6 #34).

**Persona.** P1, P6 (nhận), P2 (tạo/phân tích), P3, P4 (bằng chứng commissioning/tuân thủ).

**User story**

| ID | Là… | Tôi muốn… | Để… | FR |
|---|---|---|---|---|
| US-REP-01 | Chủ C&I (P1) | báo cáo tháng chi phí điện theo từng khung giờ | so với hóa đơn EVN và thấy tác động của PV/BESS | FR-REP-002 |
| US-REP-02 | Energy manager (P2) | top cửa sổ 30 phút có công suất cao nhất và thành phần | chuẩn bị cho giá hai thành phần và tránh quá tải MBA | FR-REP-003 |
| US-REP-03 | Installer (P4) | xuất nhật ký thay đổi giới hạn xuất và số lần vi phạm | nộp hồ sơ cho điện lực khi được hỏi | FR-REP-007 |
| US-REP-04 | ESCO (P6) | báo cáo đã gửi không bị thay đổi âm thầm | dùng làm cơ sở thanh toán | FR-REP-005 |
| US-REP-05 | Analyst (P2) | xuất CSV có cột chất lượng và giờ có offset | phân tích trong Excel không sai giờ | FR-REP-006 |

**Luồng chính.** WF-11 (báo cáo tháng), WF-14 (restatement). Báo cáo ngày R1: job ngày xong → R1 sẵn sàng trước 06:00 giờ site → người dùng xem/tải.

**Yêu cầu chức năng**

| ID | Yêu cầu | F- | Ưu tiên | Phát hành | Hạng·Gate | Căn cứ |
|---|---|---|---|---|---|---|
| FR-REP-001 | Hệ thống phải tạo R1 Báo cáo vận hành ngày: sản lượng PV, nhập/xuất, sạc/xả, SOC min/max, Pmax ngày, cảnh báo, availability dữ liệu, dòng "dữ liệu tính đến". | F-REP-01 | P0 | MVP | — | F §3.11 R1 |
| FR-REP-002 | Hệ thống phải tạo R2 Báo cáo năng lượng và hóa đơn bóng theo kỳ hóa đơn hoặc tháng lịch: K01–K06, K10–K12, chi phí theo khung TOU (K25), cờ `INCOMPLETE` và khoảng min/max khi có chu kỳ thiếu. | F-REP-02 | P0 | MVP | — | K §6 #3; C K25 |
| FR-REP-003 | Hệ thống phải tạo R3 Phân tích công suất: top-N cửa sổ 30 phút (thời điểm, kW, thành phần PV/BESS/tải), heatmap ngày × giờ, đường cong thời gian–tải, Pmax có/không BESS (ước tính); cửa sổ UNCERTAIN liệt kê riêng. | F-REP-03 | P0 | MVP | — | F §3.11 R3 |
| FR-REP-004 | Hệ thống phải tạo R8 Báo cáo chất lượng dữ liệu: coverage theo thiết bị, khoảng trống, SUSPECT, reset/rollover/thay công tơ, độ trễ ingest. | F-REP-08 | P0 | MVP | — | F §3.11 R8 |
| FR-REP-005 | Báo cáo phát hành phải là snapshot bất biến với `report_version`, `data_as_of`, `tariff_version`, `calc_version`, `ef_version` (nếu có), `attribution_version`; restatement tạo phiên bản mới và thông báo người nhận; snapshot giữ ≥ 5 năm. | F-REP-10 | P0 | MVP | — | F-P15, F-P22 |
| FR-REP-006 | Hệ thống phải xuất CSV (UTF-8 có BOM, ISO 8601 có offset + cột UTC, đơn vị trong header, cột quality), XLSX (sheet Metadata), PDF render server-side; ≤ 100.000 hàng trả ngay, lớn hơn chạy job nền với link ký số hết hạn ≤ 7 ngày; mọi lần xuất có audit và tôn trọng RBAC. | F-REP-11 | P0 | MVP | — | F-P21 |
| FR-REP-007 | Hệ thống phải xuất bằng chứng tuân thủ giới hạn xuất: nhật ký mọi thay đổi chế độ/giới hạn xuất–nhập (ai, khi nào, cũ → mới, readback), số lần và tổng thời lượng vi phạm xuất theo kỳ, kết quả test commissioning (FR-INT-017). Không ghi câu "đạt yêu cầu pháp lý". | F-REP-13 | P0 | MVP | — | A D-05 |
| FR-REP-008 | Mọi báo cáo phải ghi phương pháp và nhãn: số ước tính có "≈ ước tính"; số mô phỏng có "Mô phỏng"; không có câu % tiết kiệm quảng cáo; không tuyên bố tuân thủ IPMVP/ISO 50001/IEC 61724-1. | F-REP-02, F-REP-07 | P0 | MVP | — | K §6 #33, #34 |
| FR-REP-009 | Hệ thống nên tạo R4 Hiệu suất PV (Yf, PR chỉ khi có POA, PR hiệu chỉnh nhiệt, PR loại trừ curtail, % thời gian bị loại, K15, xếp hạng inverter). | F-REP-04 | P1 | Phase 1 | — | F §3.11 R4 |
| FR-REP-010 | Hệ thống nên tạo R5 BESS (throughput, EFC kèm `E_ref`, RTE kèm ranh giới, xu hướng SOH, aux, thời gian ở mỗi chế độ, giờ derate). | F-REP-05 | P1 | Phase 1 | — | C-P05 |
| FR-REP-011 | Hệ thống nên tạo R6 Availability (thời gian, điện năng, dữ liệu; loại trừ theo hợp đồng; mất kết nối báo riêng). | F-REP-06 | P1 | Phase 1 | — | C-P13 |
| FR-REP-012 | Hệ thống nên tạo R7 Tiết kiệm so với baseline B0 (không PV, không BESS) và B1 (có PV, không BESS) ở bucket 5 phút cùng `TariffVersion`, phân rã nguồn tiết kiệm, trừ chi phí suy hao ước tính; trang đầu ghi phương pháp; luôn "≈ ước tính". | F-REP-07 | P1 | Phase 1 | — | F §3.11; GAP-05 |
| FR-REP-013 | Hệ thống nên cho đăng ký nhận báo cáo theo lịch (giờ site), chỉ gửi khi watermark ≥ cuối kỳ hoặc sau thời gian chờ tối đa, kèm nhãn "chưa đầy đủ" khi cần. | F-REP-09 | P1 | Phase 1 | — | F-P22 |
| FR-REP-014 | Hệ thống nên xuất hàng loạt Parquet theo site/tháng cho data lake của khách. | F-REP-12 | P1 | Phase 1 | — | F §3.14 |
| FR-REP-015 | Hệ thống nên theo dõi ngân sách xuất 50%: lũy kế E_exp/E_pv theo kỳ, dự báo cuối kỳ, nguồn gốc điện xuất (PV trực tiếp/BESS xả). Tham số kỳ và mẫu số là UNKNOWN, cấu hình được. | F-REP-14 | P1 | Phase 1 | — | C K30; Q-A03 |
| FR-REP-016 | Hệ thống nên báo cáo CO₂ tránh được và Scope 2 với bảng hệ số có phiên bản (năm, giá trị, đơn vị, cơ quan, văn bản, trạng thái); nhãn `PROVISIONAL_EF` khi chưa chính thức. | F-REP-15 | P1 | Phase 1 | — | C-P14 |
| FR-REP-017 | Hệ thống nên xuất dữ liệu cho ESG/ISO 50001 (kWh theo nguồn × giờ, EnPI đơn giản khi khách nhập sản lượng); không tuyên bố tuân thủ ISO 50001. | F-REP-16 | P1 | Phase 1 | — | A D-11 |
| FR-REP-018 | Hệ thống nên tạo dữ liệu thanh toán PPA/ESCO (kWh bán theo site × khung TOU × kỳ, bảng đối soát) tham chiếu sổ hợp đồng. | F-REP-17 | P1 | Phase 1 | — | A §3.3 P6 |
| FR-REP-019 | Hệ thống nên tạo báo cáo danh mục (xếp hạng yield, chi phí, cảnh báo, availability; trọng số ghi rõ). | F-REP-18 | P1 | Phase 1 | — | H §3.1 |

**Quy tắc nghiệp vụ**

- **BR-REP-01** Tiết kiệm = `Bill_baseline_counterfactual − Bill_shadow_actual`, cùng `TariffVersion`; không bao giờ là % quảng cáo (K §6 #34).
- **BR-REP-02** Tiết kiệm demand không cộng theo ngày; chỉ tính ở cấp kỳ hóa đơn (F §3.11 bẫy a).
- **BR-REP-03** Biểu giá đổi giữa kỳ thì tính theo từng `TariffVersion` có `valid_from`.
- **BR-REP-04** Báo cáo đã phát hành không bị sửa; mọi thay đổi số là restatement có phiên bản.
- **BR-REP-05** Báo cáo chỉ dùng dữ liệu site `active` (và giai đoạn `maintenance` có ghi chú); dữ liệu `commissioning` loại ra.

**Tiền/hậu điều kiện.** Tiền: dữ liệu ngày/tháng địa phương đã tính; biểu giá gán (cho phần chi phí). Hậu: snapshot lưu; audit xuất.

**Dữ liệu vào / ra.** Vào: bảng ngày/tháng địa phương, `interval_energy` 5 phút, cảnh báo, sự kiện lệnh/cấu hình, biểu giá có phiên bản, kết quả test commissioning. Ra: R1–R8 (PDF/XLSX/CSV), snapshot, file xuất, thông báo restatement.

**Phân quyền.** Xem đã phát hành: `report.read`. Tạo nháp: `report.draft`. Phát hành: `report.publish`. Xuất: `data.export`.

**Lỗi và trường hợp biên**

| Tình huống | Hành vi |
|---|---|
| Kỳ có 2 h dữ liệu thanh ghi thiếu một đầu | R2 `INCOMPLETE`, hiện khoảng chi phí min/max |
| Đổi `calc_version` sau phát hành | Bản cũ giữ nguyên; tạo bản tính lại khi người dùng yêu cầu, ghi chú lý do |
| Xuất 2 triệu hàng | Job nền, thông báo khi xong, link hết hạn ≤ 7 ngày |
| Không có vi phạm xuất trong kỳ | Báo cáo ghi "0 lần" chỉ khi coverage `MTR_POC` ≥ 99%; nếu thấp hơn ghi "0 lần trên N% thời gian có dữ liệu" |

**Tiêu chí chấp nhận**

- **AC-REP-01** Given site `Asia/Ho_Chi_Minh`, When đến 06:00 giờ site, Then R1 của ngày hôm trước sẵn sàng (mục tiêu 99% số site) và ghi "dữ liệu tính đến HH:MM".
- **AC-REP-02** Given kỳ có 3 bucket 5 phút `MISSING` trong khung cao điểm, When tạo R2, Then báo cáo gắn `INCOMPLETE` và hiển thị khoảng chi phí min/max thay vì một số duy nhất.
- **AC-REP-03** Given R2 đã phát hành với tổng nhập 100.000 kWh, When backfill làm tổng nhập thành 100.600 kWh (+0,6%), Then hệ thống tạo restatement phiên bản 2 và thông báo người nhận; bản 1 vẫn tải được.
- **AC-REP-04** Given backfill làm tổng nhập đổi +0,3% và Pmax không đổi, When tính lại, Then không tạo restatement, nhưng số trực tuyến cập nhật và ghi "khác bản phát hành 0,3%".
- **AC-REP-05** Given xuất CSV, When mở file, Then cột thời gian có dạng `2026-10-10T17:30:00+07:00`, có cột UTC, header có hậu tố đơn vị (`p_grid_kw`) và có cột `quality`.
- **AC-REP-06** Given người dùng không có `data.export`, When gọi API xuất, Then nhận 403 và sự kiện bị từ chối được audit.
- **AC-REP-07** Given báo cáo tuân thủ giới hạn xuất cho tháng 9, When tạo, Then mỗi thay đổi `export_limit_w` có người, thời điểm, giá trị cũ, mới và kết quả readback.

**Phụ thuộc.** M-HIST, M-TAR, M-GRID (vi phạm), M-INT (kết quả test), M-ORG (hợp đồng, P1).

**Bằng chứng và độ tin cậy**

- [FACT] Khung TOU QĐ 963 — https://thuvienphapluat.vn/van-ban/Tai-nguyen-Moi-truong/Quyet-dinh-963-QD-BCT-2026-khung-gio-cao-diem-thap-diem-cua-he-thong-dien-quoc-gia-703327.aspx; giá QĐ 1279 — https://thuvienphapluat.vn/phap-luat-nha-dat/toan-van-quyet-dinh-1279-qd-bct-2025-quy-dinh-ve-gia-ban-dien-3357.html (qua kết quả tìm kiếm). Độ tin cậy: Trung bình; chi tiết thực thi UNKNOWN.
- [FACT] Chu kỳ tích phân Pmax hiện là 30 phút — https://daibieunhandan.vn/trien-khai-thu-nghiem-gia-ban-le-dien-hai-thanh-phan-tu-thang-10-2025-10390577.html (qua kết quả tìm kiếm). [UNKNOWN] Cơ sở tính tiền (đo hay đăng ký) và block/rolling (K R-16).
- [FACT] FusionSolar có báo cáo nhà máy/inverter/pin theo ngày–năm và đăng ký e-mail — https://support.huawei.com/enterprise/en/doc/EDOC1100331328/90b9638d/viewing-and-managing-report (qua kết quả tìm kiếm).
- [FACT] Người dùng FusionSolar phàn nàn thiếu xuất CSV — https://apps.apple.com/jp/app/id1529080383 (qua nghiên cứu FS trước).
- [FACT] Tuyên bố tiết kiệm của vendor không có kiểm chứng độc lập (Stem "lên tới 30%", Low — A #39). Đây là lý do BR-REP-01.
- [FACT] Xử phạt điện mặt trời mái nhà theo NĐ 133/2026 (A §3.4.1, qua kết quả tìm kiếm). [UNKNOWN] Hồ sơ cụ thể điện lực yêu cầu (Q-A09).

---

### 5.6 M-TAR — Biểu giá, lịch TOU, hóa đơn bóng

**Mục đích nghiệp vụ.** Biểu giá là **dữ liệu có phiên bản theo ngày hiệu lực**, không hard-code (K §6 #24). Một mô hình biểu giá dùng chung cho hóa đơn bóng (M-REP), bộ sinh lịch TOU (M-OPT) và dải TOU trên UI (M-DASH). Chi tiết thực thi pháp lý (ngày áp QĐ 963 vào hóa đơn, cơ sở giá hai thành phần, kiểu cửa sổ 30 phút) còn UNKNOWN nên mô hình phải chứa được nhiều phương án.

**Persona.** P2 (chính), P4, PO (thư viện EVN), P1 (đọc kết quả).

**User story**

| ID | Là… | Tôi muốn… | Để… | FR |
|---|---|---|---|---|
| US-TAR-01 | Energy manager (P2) | chọn biểu giá EVN đúng nhóm khách hàng và cấp điện áp từ thư viện | không phải nhập tay đơn giá | FR-TAR-001 |
| US-TAR-02 | Energy manager (P2) | dùng khung TOU cũ cho hóa đơn và khung mới cho tối ưu khi chưa rõ ngày áp | hóa đơn bóng khớp hóa đơn thật mà pin vẫn xả đúng khung mới | FR-TAR-003 |
| US-TAR-03 | Chủ trạm sạc (P2) | gắn biểu giá trạm sạc cho công tơ EV riêng | tính đúng chi phí từng hợp đồng | FR-TAR-004 |
| US-TAR-04 | Chủ C&I (P1) | hóa đơn bóng theo kỳ chốt chỉ số của EVN | so sánh trực tiếp với hóa đơn thật | FR-TAR-005, FR-TAR-006 |

**Luồng chính.** WF-03.

**Yêu cầu chức năng**

| ID | Yêu cầu | F- | Ưu tiên | Phát hành | Hạng·Gate | Căn cứ |
|---|---|---|---|---|---|---|
| FR-TAR-001 | Hệ thống phải có thư viện biểu giá có phiên bản: nhóm khách hàng × cấp điện áp × khung giờ, đơn giá chưa VAT (đ/kWh), `valid_from`/`valid_to`, văn bản nguồn; thư viện EVN do nền tảng quản lý; tenant chọn hoặc tạo bản riêng. | F-TAR-01 | P0 | MVP | — | A D-03 |
| FR-TAR-002 | Hệ thống phải có lịch TOU có phiên bản: khung cao điểm/bình thường/thấp điểm theo thứ trong tuần, Chủ nhật, ngày lễ (có danh mục ngày lễ theo năm); mẫu QĐ 963 và TT 16/2014 (lịch sử); tính theo giờ site; mỗi phút trong ngày thuộc đúng một khung. | F-TAR-02 | P0 | MVP | — | K §6 #24, #37 |
| FR-TAR-003 | Mỗi site phải chọn được lịch dùng cho hóa đơn bóng và lịch dùng cho tối ưu (có thể khác nhau); UI hiển thị cả hai khi khác; chuyển đổi có ngày hiệu lực và audit. | F-TAR-03 | P0 | MVP | — | A §3.4.2; Q-A01 |
| FR-TAR-004 | Mỗi điểm đo thanh toán (POC, công tơ trạm sạc riêng…) phải gắn được hợp đồng/biểu giá riêng; một site có nhiều biểu giá song song. | F-TAR-04 | P0 | MVP | — | A D-02 |
| FR-TAR-005 | Hệ thống phải quản lý kỳ hóa đơn `(site, start_local, end_local)` theo ngày chốt chỉ số; kỳ khác tháng lịch; chuyển biểu giá giữa kỳ tính theo từng `TariffVersion`. | F-TAR-05 | P0 | MVP | — | F-P13 |
| FR-TAR-006 | Hệ thống phải tính hóa đơn bóng theo kỳ: Σ E_imp(k) × giá(khung(k)) cho mọi bucket 5 phút + (khi bật) Pmax × giá công suất + (khi có) phạt PF; bucket MISSING → `INCOMPLETE` và khoảng min/max. Kết quả là ước tính, không thay hóa đơn EVN. | F-TAR-06 | P0 | MVP | — | C K25 |
| FR-TAR-007 | Hệ thống phải kiểm hợp lệ và quản lý thay đổi biểu giá: chặn lịch có khoảng hở/chồng lấn; thay đổi có `valid_from`; thay đổi hồi tố vào kỳ đã phát hành bắt buộc lý do và tạo restatement; site có điều khiển thì đổi lịch tối ưu phải được xác nhận (BR-TAR-05). | F-TAR-01, F-REP-10 | P0 | MVP | — | K §6 #24 |
| FR-TAR-008 | Hệ thống nên hỗ trợ thành phần công suất: `demand_window` (mặc định 30 phút block — UNKNOWN), `demand_basis ∈ {MEASURED_MAX, CONTRACTED}` tắt mặc định, ratchet, khung áp dụng; khi bật thì tự bật đồng hồ demand (FR-GRID-010). | F-TAR-07 | P1 | Phase 1 | — | K R-16; C-P08 |
| FR-TAR-009 | Hệ thống nên lưu giá mua điện dư theo hợp đồng và tham số ngân sách xuất theo kỳ (mặc định 50% × E_pv đo tại `MTR_PV`, theo tháng — cả hai UNKNOWN). | F-TAR-08 | P1 | Phase 1 | — | K R-27 |
| FR-TAR-010 | Hệ thống nên lưu ngưỡng cosφ theo hợp đồng (mặc định 0,9 tại điểm đặt công tơ) và cách tính phạt/mua công suất phản kháng khi có văn bản. | F-TAR-09 | P1 | Phase 1 | — | C-P10; Q-C05 |
| FR-TAR-011 | Hệ thống nên cho nhập hóa đơn EVN (tay hoặc file), so với hóa đơn bóng và với công tơ điều khiển, báo chênh lệch theo khung giờ. | F-TAR-10 | P1 | Phase 1 | — | GAP-07 |
| FR-TAR-012 | Hệ thống có thể nhận chuỗi giá 30 phút (DPPA ảo/thị trường) cho đối soát và tối ưu khi có cơ chế. | F-TAR-11 | P2 | Phase 2 | — | A D-13 |

**Quy tắc nghiệp vụ**

- **BR-TAR-01** Mỗi phút của mỗi ngày (giờ site) thuộc đúng một khung giá trong lịch TOU có hiệu lực.
- **BR-TAR-02** Đơn giá lưu chưa VAT; VAT là tham số hiển thị có phiên bản.
- **BR-TAR-03** Biểu giá áp cho bucket theo `bucket_start` giờ site; bucket 5 phút thẳng hàng biên khung giờ (17:30, 22:30) nên không cắt ngang.
- **BR-TAR-04** Thành phần công suất mặc định **tắt**; khi bật phải chọn `demand_basis` rõ ràng (K R-16).
- **BR-TAR-05** Ở site `control_enabled = true`, thay đổi lịch dùng cho tối ưu là thao tác ảnh hưởng gián tiếp tới thiết bị: yêu cầu người có `cmd.c2` xác nhận với step-up MFA và lý do, rồi mới kích hoạt sinh lịch mới.
- **BR-TAR-06** Chủ nhật theo QĐ 963 không có cao điểm; bộ sinh lịch đọc điều này từ dữ liệu lịch, không hard-code.

**Tiền/hậu điều kiện.** Tiền: site có `timezone`, điểm đo thanh toán khai báo. Hậu: hóa đơn bóng có `tariff_version`.

**Dữ liệu vào / ra.** Vào: văn bản giá (nhập bởi PO), lịch, ngày lễ, kỳ hóa đơn, `interval_energy` 5 phút, Pmax. Ra: `TariffVersion`, `TouCalendar`, `BillingPeriod`, hóa đơn bóng theo khung, dải TOU cho UI và M-OPT.

**Phân quyền.** `tariff.configure` (ANALYST, SITE_ENGINEER, ORG_ADMIN); thư viện EVN: `tariff.library.manage` (PLATFORM_ADMIN); đọc: `site.read`.

**Lỗi và trường hợp biên**

| Tình huống | Hành vi |
|---|---|
| Văn bản giá mới có hiệu lực giữa kỳ | Kỳ tách thành hai đoạn theo `valid_from` |
| Ngày lễ rơi vào ngày thường | Áp quy tắc ngày lễ của lịch (nếu văn bản có), nếu không thì như ngày thường và ghi chú UNKNOWN |
| Site có hai POC với hợp đồng khác nhau (P1) | Hóa đơn bóng riêng theo POC, không net giữa POC |
| Không có biểu giá cho cấp điện áp của site trong thư viện | Báo thiếu, cho tạo bản riêng của tenant |

**Tiêu chí chấp nhận**

- **AC-TAR-01** Given lịch QĐ 963 và một thứ Hai, When tra khung lúc 17:29 và 17:30 giờ site, Then 17:29 là "Bình thường" và 17:30 là "Cao điểm".
- **AC-TAR-02** Given một Chủ nhật, When tra khung lúc 19:00, Then không phải "Cao điểm".
- **AC-TAR-03** Given lịch có khoảng hở 22:30–22:45 chưa gán khung, When lưu, Then hệ thống chặn và chỉ ra khoảng hở.
- **AC-TAR-04** Given cấp 22–<110 kV với đơn giá mẫu 1.833 / 1.190 / 3.398 đ/kWh (bình thường/thấp điểm/cao điểm, chưa VAT) và nhập 10 kWh trong bucket 18:00–18:05 thứ Ba, When tính hóa đơn bóng, Then chi phí bucket = 33.980 đ (chưa VAT).
- **AC-TAR-05** Given site có `control_enabled = true`, When Analyst đổi lịch tối ưu từ TT 16 sang QĐ 963, Then thay đổi ở trạng thái "chờ xác nhận" cho tới khi người có `cmd.c2` xác nhận với step-up MFA.
- **AC-TAR-06** Given biểu giá thay đổi từ ngày 15 trong kỳ 01–30, When tính R2, Then bucket trước ngày 15 dùng phiên bản cũ, từ ngày 15 dùng phiên bản mới, và báo cáo liệt kê cả hai `tariff_version`.

**Phụ thuộc.** M-HIST (bucket, Pmax), M-REP, M-OPT (lịch tối ưu), M-GRID (đồng hồ demand), [05 Domain](05-domain-model.html) (TariffVersion, TouCalendar, DemandComponent, BillingPeriod — K G-03).

**Bằng chứng và độ tin cậy**

- [FACT] QĐ 963/QĐ-BCT: cao điểm 17h30–22h30 T2–T7, thấp điểm 0h–6h (URL ở §5.5). [FACT] Khung cũ TT 16/2014 — https://luatminhkhue.vn/quy-dinh-ve-gio-cao-diem-dien-la-luc-may-gio.aspx (qua kết quả tìm kiếm). [FACT] Một nguồn 07/2026 nói khung mới chưa áp thực tế — https://thoibaonganhang.vn/gia-dien-theo-gio-ai-co-the-huong-loi-187971.html; nguồn khác nói đã áp. [UNKNOWN] Ngày áp (Q-A01). Đây là lý do của FR-TAR-003.
- [FACT] Trạm sạc EV kinh doanh có biểu giá và công tơ riêng — https://vneconomy.vn/automotive/quy-dinh-moi-ve-gia-ban-dien-cho-tram-sac-xe-dien.htm (qua kết quả tìm kiếm).
- [FACT] Thí điểm giá hai thành phần — https://tapchicongthuong.vn/thi-diem-ap-dung-gia-dien-hai-thanh-phan-tu-1-1-2026-218800.htm (qua kết quả tìm kiếm). [UNKNOWN] Cơ sở tính (R-16).
- [FACT] TT 05/2025 Điều 31: cosφ ≥ 0,9 — https://thuvienphapluat.vn/van-ban/Thuong-mai/Thong-tu-05-2025-TT-BCT-he-thong-truyen-tai-dien-phan-phoi-dien-do-dem-dien-nang-642994.aspx (qua kết quả tìm kiếm).
- [UNKNOWN] Ngày chốt kỳ load profile EVN (Q-F10).

---

### 5.7 M-BESS — Quản lý BESS (supervisory)

**Mục đích nghiệp vụ.** Giám sát BESS, giữ mô hình pin, chọn chiến lược, phát lệnh supervisory trong vùng vận hành an toàn (SOE) và giải thích vì sao pin không chạy theo lệnh. EMS điều phối BMS và PCS nhưng **không** thay controller của nhà tích hợp và **không** nằm trong vòng bảo vệ: BMS bảo vệ cell và mở contactor, PCS thực thi, EMS quyết định điều độ trong giới hạn BMS/PCS công bố.

**Persona.** P3 (chiến lược, lệnh), P5 (giới hạn, bảo hành), P4 (SOE, commissioning), PS (duyệt), P1 (xem).

**User story**

| ID | Là… | Tôi muốn… | Để… | FR |
|---|---|---|---|---|
| US-BESS-01 | Operator (P3) | chọn chiến lược site trong danh sách thiết bị thực sự hỗ trợ | không gửi chế độ thiết bị không làm được | FR-BESS-004 |
| US-BESS-02 | Operator (P3) | đặt công suất xả thủ công có thời hạn và thấy khi nào lệnh đã thực sự áp dụng | thử nghiệm/vận hành an toàn, không bị UI "lạc quan" đánh lừa | FR-BESS-005 |
| US-BESS-03 | BESS integrator (P5) | thấy công suất bị kẹp bởi BMS/PCS/SOE và lý do | không bị đổ lỗi khi pin không chạy theo lệnh | FR-BESS-008 |
| US-BESS-04 | Control Supervisor (PS) | duyệt SOE do kỹ sư đề xuất trước khi edge dùng | không ai một mình nới được giới hạn an toàn | FR-BESS-007 |
| US-BESS-05 | Chủ C&I (P1) | đặt mức SOC dự phòng cho mất điện | giữ được tải quan trọng | FR-BESS-006 |

**Luồng chính.** WF-04 (Gate M1), WF-05 (Gate M2, SOE), WF-06 (chiến lược + lịch), WF-07 (lệnh thủ công), WF-09 (BMS stale/lỗi).

**Yêu cầu chức năng**

| ID | Yêu cầu | F- | Ưu tiên | Phát hành | Hạng·Gate | Căn cứ |
|---|---|---|---|---|---|---|
| FR-BESS-001 | Hệ thống phải giám sát BESS: SOC (giá trị BMS công bố, ghi có độ bất định), SOH (kèm định nghĩa của hãng), P thực tế, CCL/DCL, P sạc/xả cho phép, nhiệt độ và điện áp cell min/max, trạng thái Sạc/Xả/Chờ/Lỗi lấy từ PCS/BMS, cảnh báo BMS/PCS; tóm tắt theo rack. | F-BESS-01 | P0 | MVP | — | C §3.6; K §6 #4 |
| FR-BESS-002 | Hệ thống phải lưu mô hình pin: `e_nominal`, `e_usable_bol`, `e_usable_current`, `soc_basis`, `E_ref` cho EFC; SOC dự phòng hai tầng: giới hạn hãng (chỉ đọc) và mức khách cấu hình (có audit, không thấp hơn giới hạn hãng). | F-BESS-03 | P0 | MVP | — | C-P06 |
| FR-BESS-003 | Edge phải ánh xạ chiến lược của ta xuống chế độ native của hãng qua driver `VERIFIED_*` theo ma trận chế độ hợp lệ theo topology/kịch bản, ghi và đọc lại xác nhận; kết quả `APPLIED`/`FAILED_NO_EFFECT`. | F-BESS-04 | P0 | MVP | C1·M1 | K R-09, R-20 |
| FR-BESS-004 | Operator phải chọn được `site_strategy ∈ {SELF_CONSUMPTION, PEAK_SHAVING, TOU_SCHEDULE, BACKUP_HOLD, IDLE}`: (a) chiến lược mặc định của site là cấu hình có phiên bản, đổi là C2; (b) override tạm `SET_ESS_MODE` có hạn ≤ 24 h, C1. Chỉ hiện chế độ có trong `capability_profile`; tôn trọng `mode_change_min_interval`; hiển thị nguồn lệnh và hạn. | F-BESS-05 | P0 | MVP | C1·M1 (override), C2 (mặc định) | K R-15; E §3.19 |
| FR-BESS-005 | Operator phải gửi được `SET_ESS_P` với hạn mặc định 15 phút, tối đa 1 h, `on_expiry = REVERT_DEFAULT`; hộp xác nhận "hiện tại → mới" kèm giới hạn sẽ áp và tác động dự kiến lên P lưới; `APPLIED` chỉ sau readback; `APPLIED_CLAMPED` báo giá trị thực. Setpoint > 80% giới hạn SOE nâng C2. | F-BESS-06 | P0 | MVP | C1·M2 | K §6 #21; I §3.7.4 |
| FR-BESS-006 | Hệ thống phải cho `SET_SOC_RESERVE` trong giới hạn hãng và SOE; tăng mức là C1, giảm mức là C2 (lý do bắt buộc). | F-BESS-07 | P0 | MVP | C1·M1 / C2 | I §3.7.4 |
| FR-BESS-007 | Hệ thống phải quản lý SOE theo site có version: P sạc/xả max, SOC min/max hiệu dụng, dự phòng, `export_limit_w`, `import_cap_w`, ramp, ΔP tối đa/lệnh, `mode_change_min_interval`, chu kỳ/ngày tối đa, `T_stale_bms`, `T_stale_poc`, danh sách lệnh cho phép. Site Engineer đề xuất, Control Supervisor duyệt (khác người), ký số, đẩy xuống edge; edge từ chối lệnh ngoài SOE. | F-BESS-08 | P0 | MVP | C3·M2 | I §3.7.2 |
| FR-BESS-008 | Hệ thống phải hiển thị chuỗi giới hạn: P thực tế / setpoint / P cho phép và nguồn giới hạn (BMS, PCS, SOE, lưới, arbiter) với mã lý do (`CLAMPED_BY_BMS`…). | F-BESS-09 | P0 | MVP | — | C §3.7; G §3.11 |
| FR-BESS-009 | Edge phải giám sát an toàn BESS tự động không cần cloud: dữ liệu BMS cũ hơn `T_stale_bms` hoặc BMS báo lỗi → P = 0 hoặc chế độ native; SOC guard theo SOE (có hysteresis); thiết bị `requires_native_fallback` không nhận setpoint P cưỡng bức. | F-BESS-10 | P0 | MVP | C1·M2 (tự động) | K §6 #16, #17 |
| FR-BESS-010 | Hệ thống phải đọc tín hiệu PCCC/khí/nhiệt phòng pin (DI hoặc Modbus) khi có và kích hoạt interlock IL-08 (cấm sạc/xả theo lệnh từ xa khi có báo động). | F-BESS-18 | P0 | MVP | — | I IL-08; K G-12 |
| FR-BESS-011 | Hệ thống **không được** cung cấp API, nút hay lệnh để sửa thông số bảo vệ BMS/PCS/rơ-le hoặc E-stop từ xa; UI chỉ đọc trạng thái E-stop. | F-BESS-19, F-BESS-20 | CẤM | Mọi phiên bản | C4 | K §6 #14, #28 |
| FR-BESS-012 | Hệ thống nên có drill-down L4 rack/module/cell: heatmap điện áp/nhiệt cell, cell lệch, lịch sử cân bằng nếu BMS cung cấp. | F-BESS-02 | P1 | Phase 1 | — | H-P07 |
| FR-BESS-013 | Hệ thống nên tính KPI BESS: throughput, EFC (`E_ref` ghi rõ), RTE theo `rte_boundary` (chỉ trên cửa sổ ΔSOC ≈ 0), aux idle/active, thời gian ở mỗi chế độ, giờ derate. | F-BESS-11 | P1 | Phase 1 | — | C-P05 |
| FR-BESS-014 | Hệ thống nên hiển thị xu hướng SOH theo BMS và ước lượng dung lượng khả dụng từ chu kỳ sâu (ΔSOC ≥ 60%). | F-BESS-12 | P1 | Phase 1 | — | C K19, K20 |
| FR-BESS-015 | Hệ thống nên so EFC, throughput, SOC trung bình, nhiệt độ, chu kỳ/năm với điều khoản bảo hành (FR-ORG-016) và cảnh báo khi tiến gần giới hạn. | F-BESS-13 | P1 | Phase 1 | — | K R-25 |
| FR-BESS-016 | Edge nên chia P giữa nhiều PCS/tủ theo SOC và giới hạn từng tủ khi controller native không làm. | F-BESS-14 | P1 | Phase 1 | C1·M2 | E §3.12 G5 |
| FR-BESS-017 | Hệ thống nên theo dõi nguồn gốc năng lượng trong pin (từ PV hay lưới) để quy kết điện xuất khi BESS xả. | F-BESS-15 | P1 | Phase 1 | — | C-P04; Q-C04 |
| FR-BESS-018 | Hệ thống nên cho "Dừng/khởi động vận hành từ xa" PCS (`DEVICE_ON_OFF`, không gọi là E-stop), hai người duyệt, thông báo chủ site; không cho lịch tự động. | F-BESS-16 | P1 | Phase 1 | C3·M2 | I §3.7.7 |
| FR-BESS-019 | Hệ thống có thể cho reset lỗi từ xa chỉ khi hãng cho phép, hai người duyệt; mặc định reset tại chỗ. | F-BESS-17 | P2 | Phase 2 | C3·M2 | I §3.7.7 |

**Quy tắc nghiệp vụ**

- **BR-BESS-01** Quyết định an toàn dựa vào giới hạn P/I do BMS công bố, không dựa vào SOC (SOC có độ bất định).
- **BR-BESS-02** Hai từ vựng không trộn: `site_strategy` cho chiến lược và lệnh thủ công; `slot_mode` (PV_SURPLUS_CHARGE, GRID_CHARGE_TO_TARGET, PEAK_DISCHARGE, GRID_SETPOINT, HOLD, IDLE) chỉ trong envelope `APPLY_SCHEDULE` (K §6 #22).
- **BR-BESS-03** Lệnh thủ công nằm ở mức 7 của arbiter: luôn bị kẹp bởi mức 1–6 (bảo vệ, interlock, giám sát an toàn, tuân thủ lưới, trần nhập, dự phòng) và báo `APPLIED_CLAMPED`.
- **BR-BESS-04** SoD cho SOE: người đề xuất ≠ người duyệt; mọi thay đổi SOE thông báo chủ site.
- **BR-BESS-05** Ngoại lệ dự phòng: khi trần nhập (mức 5) bị đe dọa, edge được xả xuống dưới `SOC_backup_reserve` tới `S_res_hard` nếu SOE cho phép (`allow_reserve_dip_for_import_cap`), mã lý do `RESERVE_DIPPED_FOR_IMPORT_CAP` (G §3.8).
- **BR-BESS-06** Không có setpoint vô thời hạn từ xa; hết hạn luôn về mặc định đã định trước, không "giữ nguyên".

**Tiền/hậu điều kiện.** Tiền cho lệnh: site `active`, `control_enabled`, `REMOTE`, Gate phù hợp, thiết bị `VERIFIED_*`, SOE hiệu lực (M2). Hậu: nhật ký lệnh đầy đủ; trạng thái thực tế đọc lại.

**Dữ liệu vào / ra**

| Vào | Ra |
|---|---|
| Điểm `ess.*` (p, soc, soh, p_charge_max, p_discharge_max, e_charge, e_discharge, mode, state, cell min/max), cảnh báo BMS/PCS, SOE, `capability_profile`, tín hiệu PCCC | Lệnh `SET_ESS_MODE`, `SET_ESS_P`, `SET_SOC_RESERVE`, cấu hình native; trạng thái lệnh; chuỗi giới hạn và mã lý do; KPI BESS (P1) |

**Phân quyền.** Xem: `site.read`. Override chế độ/setpoint/dự phòng: `cmd.c1`/`cmd.c2`. Đổi chiến lược mặc định: `cmd.c2`. SOE: `soe.propose` + `soe.approve`. Dừng PCS (P1): `cmd.c3.request` + `cmd.c3.approve`.

**Lỗi và trường hợp biên**

| Tình huống | Hành vi |
|---|---|
| Lệnh `SET_ESS_P` xả 200 kW khi BMS DCL cho 120 kW | Edge kẹp 120 kW, `APPLIED_CLAMPED` + `CLAMPED_BY_BMS` |
| Readback không đổi sau timeout | `FAILED_NO_EFFECT`, cảnh báo FR-ALM-011, thiết bị bị loại khỏi pool cho tới khi kỹ sư xác nhận |
| SOC ≤ SOC_floor_eff trong khi lịch muốn xả | Không xả; mã `HOLD_BACKUP_RESERVE` |
| Đổi chế độ lần hai trong 300 s | Từ chối `REJECTED_OUT_OF_LIMIT: mode_change_min_interval` |
| Thiết bị `requires_native_fallback` nhận `SET_ESS_P` | PDP chặn trước khi ký; UI chỉ hiện các chế độ native |
| BMS báo lỗi bảo vệ | P = 0/native ngay ở edge; cảnh báo Khẩn cấp; không có nút reset từ xa ở MVP |

**Tiêu chí chấp nhận**

- **AC-BESS-01** Given site Gate M2, SOE `P_ess_dis_max` = 250 kW, When Operator gửi `SET_ESS_P` xả 180 kW với hạn mặc định, Then lệnh là C1, `expires_at` = thời điểm tạo + 15 phút, và UI chỉ hiện "Đã áp dụng" sau khi readback trong ±2% hoặc ±1 kW trong ≤ 10 s.
- **AC-BESS-02** Given cùng SOE, When gửi xả 210 kW (84% giới hạn), Then hệ thống yêu cầu step-up MFA (≤ 5 phút) và lý do (C2).
- **AC-BESS-03** Given lệnh `SET_ESS_P` hạn 15 phút được áp lúc 10:00, When tới 10:15 không có lệnh mới, Then edge về chiến lược mặc định, trạng thái `EXPIRED` có `ts` trong ±1 chu kỳ điều khiển.
- **AC-BESS-04** Given dữ liệu BMS không cập nhật trong 6 s (`T_stale_bms` = 5 s), When chu kỳ edge kế tiếp chạy, Then setpoint BESS = 0 W hoặc chế độ native trong ≤ 2 chu kỳ (≤ 2 s) và lệnh mới bị `REJECTED_INTERLOCK:IL-03`.
- **AC-BESS-05** Given SOE phiên bản 3 do người A đề xuất, When người A cố duyệt, Then hệ thống chặn "người đề xuất không được duyệt".
- **AC-BESS-06** Given nhận lệnh có tham số ngoài SOE (ví dụ ΔP > `delta_P_max_per_cmd`), When edge kiểm, Then `REJECTED_OUT_OF_LIMIT` và không có ghi nào xuống thiết bị.
- **AC-BESS-07** Given quét toàn bộ OpenAPI của cloud và edge, When tìm endpoint ghi ngưỡng BMS, grid code, rơ-le hoặc E-stop, Then không có endpoint nào (FR-BESS-011).
- **AC-BESS-08** Given Huawei capacity control không có trong `capability_profile` của site, When mở hộp chọn chiến lược, Then PEAK_SHAVING không xuất hiện.

**Phụ thuộc.** M-SEC (PDP, ký, phê duyệt, interlock), M-OPT (arbiter, lịch), M-INT (driver, readback, watchdog), M-GRID (`MTR_POC`), [08 Tối ưu](08-energy-optimization.md), [10 An toàn](10-security-and-reliability.md).

**Bằng chứng và độ tin cậy**

- [FACT] Huawei control API là task bất đồng bộ, không được gọi chồng — https://support.huawei.com/enterprise/en/doc/EDOC1100379184/7a471100/control-apis (qua kết quả tìm kiếm). [INFERENCE] Không hãng nào công bố độ trễ end-to-end cloud→thiết bị (K §6 #36).
- [FACT] BMS hạ CCL/DCL theo SOC, nhiệt, điện áp, có thể đặt 0 — https://www.orionbms.com/manuals/utility/bms_param_current_limit_status.html (qua kết quả tìm kiếm).
- [FACT] SOC LFP có thể sai lệch đáng kể (nguồn vendor) — https://www.accure.net/blogs/state-of-charge-soc-estimation-errors-for-lfp-batteries-can-exceed-15 (qua kết quả tìm kiếm). Căn cứ BR-BESS-01.
- [INFERENCE] Theo một patent ESS, BMS gửi tín hiệu bảo vệ tới PCS qua dây cứng; kênh tới EMS là TCP/IP, RS485 hoặc CAN — https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11411391 (qua kết quả tìm kiếm) → EMS phần mềm nằm ngoài vòng bảo vệ.
- [FACT, Low] Định nghĩa chung "EMS điều phối BMS và PCS" — https://deye.com/nl/blog/bms-vs-ems-vs-pcs-bess-components/ và trang hạt giống https://www.infinitepowerht.com/what-is-energy-management-system-ems-and-its-functions.html (snippet, một agent; chỉ dùng cho định nghĩa chung theo K R-18). Không gán tính năng cụ thể nào cho trang này.
- [FACT] Tên dịch vụ "capacity control periods", "TOU periods" là của thư viện cộng đồng, không phải tên chính thức của Huawei — https://github.com/wlcrs/huawei_solar/blob/main/services.yaml (qua kết quả tìm kiếm). Thanh ghi từ diễn đàn không được dùng cho driver `VERIFIED_*` (K §6 #35).
- [UNKNOWN] Watchdog/reversion và readback chế độ native của từng hãng (GAP-02, Q-I-07); ramp bắt buộc cho C&I VN (Q-C06).

---

### 5.8 M-PV — PV: hiệu suất, chẩn đoán, giới hạn phát

**Mục đích nghiệp vụ.** Giám sát nhà máy PV tới string, giới hạn phát có kiểm soát, đo điện năng bị cắt và chỉ số hiệu suất. Đây là nền giá trị cho site PV-only (K §6 #2) và tái dùng phần lớn nghiên cứu FusionSolar. Ở site zero-export, PV thường bị cắt nên PR thô thấp giả tạo; phải có điện năng bị cắt và PR loại trừ curtail.

**Persona.** P3 (chính), P6 (hiệu suất), P4 (string, giới hạn), P1.

**User story**

| ID | Là… | Tôi muốn… | Để… | FR |
|---|---|---|---|---|
| US-PV-01 | Operator (P3) | phát hiện string 0 A khi trời nắng | sửa sớm trước khi mất sản lượng nhiều | FR-PV-002 |
| US-PV-02 | Chủ tài sản (P6) | biết bao nhiêu kWh PV bị cắt do giới hạn xuất | đánh giá giá trị của việc thêm BESS | FR-PV-004 |
| US-PV-03 | Installer (P4) | đặt giới hạn công suất PV qua logger của hãng và thấy đọc lại | tuân thủ giới hạn mà không viết vòng điều khiển riêng | FR-PV-003 |
| US-PV-04 | Operator (P3) | so specific yield giữa các inverter cùng hướng | tìm inverter kém mà không cần cảm biến bức xạ | FR-PV-005 |

**Luồng chính.** Giám sát: M-MON → M-PV (FR-PV-001, 002, 005). Giới hạn: WF-04 (native) hoặc tầng 1 edge (FR-GRID-005). Điện năng bị cắt: tính khi `P_limit < 100%` hoặc vòng zero-export đang cắt.

**Yêu cầu chức năng**

| ID | Yêu cầu | F- | Ưu tiên | Phát hành | Hạng·Gate | Căn cứ |
|---|---|---|---|---|---|---|
| FR-PV-001 | Hệ thống phải giám sát nhà máy PV và inverter: P, E ngày/tháng/tổng, trạng thái, mã lỗi, nhiệt độ, MPPT V/I, P giới hạn hiện hành (%), nguồn dữ liệu. | F-PV-01 | P0 | MVP | — | H #8 |
| FR-PV-002 | Hệ thống phải cho khai báo string (số module, kWp/string, hướng/nghiêng) và giám sát V/I string; quy tắc L1 "string 0 A khi G_POA > 200 W/m² quá 15 phút" (hoặc so với string cùng inverter khi không có cảm biến). | F-PV-02 | P0 | MVP | — | K G-10 |
| FR-PV-003 | Hệ thống phải cho `SET_PV_LIMIT` (% hoặc W) qua logger/controller native hoặc edge; tôn trọng `min_write_interval`; readback; hết hạn → 100% (nếu site cho xuất) hoặc giới hạn native. Ghi vào logger thay vì từng inverter khi có logger. | F-PV-03 | P0 | MVP | C1·M1 | E §3.19; A X-03 |
| FR-PV-004 | Hệ thống phải ước lượng điện năng bị cắt `E_curt ≈ Σ max(0, P_avail − P_actual)·Δt` khi đang giới hạn, `P_avail` từ inverter tham chiếu không bị cắt, bức xạ hoặc mô hình; gắn ESTIMATED; tách khỏi tổn hao kỹ thuật. | F-PV-04 | P0 | MVP | — | G §3.3(b); C K15 |
| FR-PV-005 | Hệ thống phải tính specific yield kWh/kWp theo ngày/tháng (kWp theo thời gian) và xếp hạng inverter cùng hướng. | F-PV-05 | P0 | MVP | — | C K12 |
| FR-PV-006 | Hệ thống nên tính PR = Yf/Yr chỉ khi có G_POA; PR hiệu chỉnh nhiệt khi có T_module; PR loại trừ curtail/mất lưới/thiếu dữ liệu, báo % bị loại; `LOW_COVERAGE` khi phủ thấp. Không có POA → "N/A". | F-PV-06 | P1 | Phase 1 | — | K §6 #12; C-P12 |
| FR-PV-007 | Hệ thống nên tính availability PV theo thời gian và điện năng, loại trừ theo hợp đồng, mất kết nối báo riêng. | F-PV-07 | P1 | Phase 1 | — | C-P13 |
| FR-PV-008 | Hệ thống nên so sánh đồng cấp (yield so median cùng hướng, cờ khi lệch > k·MAD), residual so kỳ vọng, CUSUM phát hiện PR giảm dần; nhãn UI "Phân tích thống kê". | F-PV-08 | P1 | Phase 1 | — | F §3.13 L2 |
| FR-PV-009 | Hệ thống nên tính sản lượng kỳ vọng từ bức xạ đo hoặc vệ tinh (clipping, curtail) và thác tổn thất. | F-PV-09 | P1 | Phase 1 | — | F §3.12 |
| FR-PV-010 | Hệ thống nên đọc thông số grid code/bảo vệ của inverter/PCS (chỉ đọc), so với hồ sơ đã duyệt và cảnh báo khi khác. | F-PV-12 | P1 | Phase 1 | — | C-P19 |
| FR-PV-011 | Hệ thống có thể hiển thị kết quả chẩn đoán I-V của hãng và kích hoạt quét qua công cụ hãng khi có quyền. | F-PV-10 | P2 | Phase 2 | C1·M1 | K G-10 |
| FR-PV-012 | Hệ thống có thể hiển thị bố cục vật lý cấp module/optimizer tô theo hiệu suất. | F-PV-11 | P2 | Phase 2 | — | — |
| FR-PV-013 | Hệ thống có thể cho `SET_Q`/`SET_PF` cho inverter/PCS; khóa ở MVP và Phase 1. | F-PV-13 | P2 | Phase 2 | C2·M2 | Q-C06 |

**Quy tắc nghiệp vụ**

- **BR-PV-01** PR = N/A khi không có cảm biến POA; không thay bằng GHI hay vệ tinh mà vẫn gọi là PR.
- **BR-PV-02** Thông số grid code của inverter chỉ đọc (C #13; K §6 #14).
- **BR-PV-03** Điện năng bị cắt luôn là ước tính có nhãn.
- **BR-PV-04** Luật cố định (ngưỡng) gọi là "Quy tắc cảnh báo", không phải AI.
- **BR-PV-05** Khi `control_owner = NATIVE` cho zero-export, edge không ghi `SET_PV_LIMIT` theo chu kỳ (không chạy hai vòng); chỉ đặt tham số và giám sát.

**Tiền/hậu điều kiện.** Tiền: kWp/kWac khai báo; driver inverter/logger. Hậu: KPI PV có quality; lệnh giới hạn có nhật ký.

**Dữ liệu vào / ra.** Vào: điểm `pv_inverter.*` (p, q, e_total, state, p_limit_pct, dc.p, alarm_word), string V/I, cảm biến. Ra: specific yield, E_curt, xếp hạng, lệnh `SET_PV_LIMIT`, cảnh báo string.

**Phân quyền.** Xem: `site.read`. Giới hạn PV: `cmd.c1`. Cấu hình string: `asset.configure`.

**Lỗi và trường hợp biên**

| Tình huống | Hành vi |
|---|---|
| Inverter "ghi không tác dụng" | Loại khỏi pool cắt PV, `FAILED_NO_EFFECT`, cảnh báo |
| Site không có cảm biến bức xạ | Quy tắc string dùng so sánh với string cùng inverter; PR = N/A |
| Ghi giới hạn quá dày (dưới `min_write_interval`) | Edge gộp, chỉ ghi giá trị cuối khi hết khoảng |
| Inverter mất kết nối khi đang giới hạn | Inverter dùng giới hạn native/watchdog; E_curt của khoảng đó = MISSING |

**Tiêu chí chấp nhận**

- **AC-PV-01** Given G_POA = 600 W/m² trong 16 phút và một string 0 A trong khi string cùng MPPT 8 A, When quy tắc chạy, Then sinh cảnh báo string mức Trung bình với `detector_type = RULE`.
- **AC-PV-02** Given site không có cảm biến POA, When mở R4 hoặc thẻ PR, Then hiển thị "N/A — chưa có cảm biến bức xạ mặt phẳng tấm".
- **AC-PV-03** Given `SET_PV_LIMIT` 60% hạn 1 h ở site cho phép xuất, When hết hạn, Then giới hạn trở về 100% và trạng thái `EXPIRED`.
- **AC-PV-04** Given inverter tham chiếu không bị cắt cho P_avail = 100 kW và inverter bị cắt phát 70 kW trong 15 phút, When tính E_curt, Then E_curt ≈ 7,5 kWh có nhãn "≈ ước tính".
- **AC-PV-05** Given kWp tăng từ 500 lên 800 ngày 01/10, When tính specific yield tháng 9 và tháng 10, Then tháng 9 chia cho 500 kWp và tháng 10 chia cho 800 kWp.

**Phụ thuộc.** M-MON, M-HIST, M-GRID (zero-export), M-ALM, M-ADV (dự báo PV, P1).

**Bằng chứng và độ tin cậy**

- [FACT] FusionSolar hiển thị "điều chỉnh công suất P=11.5%" trên trang inverter (ảnh thật, H #8); "Setting String Details" — https://support.huawei.cn/enterprise/en/doc/EDOC1100515204/2cd10883/setting-string-details (qua kết quả tìm kiếm).
- [FACT] blue'Log/Solar-Log nhận setpoint P/Q qua Modbus có license — https://www.meteocontrol.com/fileadmin/Daten/Dokumente/EN/Produkte/On_Site/blue_Log_XM_XC/Data_sheet/blue_Log_XM_XC_Modbus_Power_Control_license_blue_Log_XC_data_sheet_LastMod-2026-01-27_en.pdf (qua kết quả tìm kiếm).
- [FACT] PR = Yf/Yr theo IEC 61724-1 — https://pvpmc.sandia.gov/modeling-guide/5-ac-system-output/pv-performance-metrics/performance-ratio/ (qua kết quả tìm kiếm). Không tuyên bố tuân thủ 61724-1 khi chưa đối chiếu văn bản.
- [INFERENCE] Zero-export + tự tiêu thụ là chiến lược phổ biến nhất ở Việt Nam vì chỉ ~287/28.254 hệ đăng ký bán dư — https://vietnamnet.vn/en/rooftop-solar-saves-billions-of-dong-but-one-bottleneck-remains-2552186.html (qua kết quả tìm kiếm).

---

### 5.9 M-GRID — Điểm đấu nối, công tơ, tuân thủ lưới, phụ tải

**Mục đích nghiệp vụ.** Giá trị số 1 ở Việt Nam: **tuân thủ giới hạn xuất và trần nhập**. Module quản lý POC và điểm đo chuẩn, cấu hình lưới của site, thực thi giới hạn qua controller native hoặc edge, ghi nhận vi phạm, và (Phase 1) demand, PF, điều độ IEC 104, phụ tải, máy phát.

**Persona.** P4 (cấu hình, test), P3 (giám sát), P1/P6 (bằng chứng tuân thủ), P2 (demand, PF), PG (điều độ, P1).

**User story**

| ID | Là… | Tôi muốn… | Để… | FR |
|---|---|---|---|---|
| US-GRID-01 | Installer (P4) | cấu hình zero-export trên logger của hãng và kiểm chứng tại POC | đạt yêu cầu đấu nối khi bàn giao | FR-GRID-004 |
| US-GRID-02 | Operator (P3) | thấy thanh "nhập hiện tại / trần" và "xuất / giới hạn" trực tiếp | can thiệp trước khi nhảy MCCB hoặc vi phạm xuất | FR-GRID-007 |
| US-GRID-03 | Chủ C&I (P1) | biết số lần và thời lượng vi phạm xuất trong tháng | trả lời điện lực khi được hỏi | FR-GRID-007, FR-REP-007 |
| US-GRID-04 | Kỹ sư (P4) | hệ thống từ chối điều khiển lưới khi không có công tơ POC đáng tin | không điều khiển mù | FR-GRID-001, BR-GRID-01 |
| US-GRID-05 | Operator (P3) | BESS tự xả khi tải vượt trần nhập | tránh quá tải MBA mà không phải ngồi canh | FR-GRID-006 |

**Luồng chính.** WF-01 bước 4–5 (khai báo), WF-02 bước 6, 8, 9 (dấu, native, test), WF-04 (Gate M1), WF-09 (mất POC).

**Yêu cầu chức năng**

| ID | Yêu cầu | F- | Ưu tiên | Phát hành | Hạng·Gate | Căn cứ |
|---|---|---|---|---|---|---|
| FR-GRID-001 | Hệ thống phải cho khai báo GridConnection và `MTR_POC` (hoặc `MTR_POC_LV` khi không đặt được CT/VT trung áp, kèm hiệu chỉnh tổn hao MBA): ranh giới, `ct_ratio`, `vt_ratio`, `accuracy_class`, quan hệ với công tơ thanh toán EVN. | F-GRID-01 | P0 | MVP | — | K §6 #10 |
| FR-GRID-002 | Hệ thống phải có danh mục điểm đo chuẩn `MTR_PV`, `MTR_BESS`, `MTR_AUX`, `MTR_LOAD_i`, `MTR_EV_i`, `MTR_GEN`, `DC_PV`/`DC_BAT`; mỗi điểm có `aux_inside_boundary`, `sign_convention` gốc, `R_wrap`, nhãn đầu/cuối chu kỳ, nguồn timestamp. | F-GRID-02 | P0 | MVP | — | K §6 #10 |
| FR-GRID-003 | Hệ thống phải lưu cấu hình lưới site: `export_mode ∈ {ZERO_EXPORT, EXPORT_LIMIT, EXPORT_ENERGY_BUDGET}` (budget là P1), `export_limit_w`, `import_cap_w`, `allow_grid_charge`, `allow_ess_export`; có version, audit; là một phần của SOE; thay đổi là C3. | F-GRID-03 | P0 | MVP | C3·M1 | K R-27 |
| FR-GRID-004 | Hệ thống phải đặt và kiểm chứng zero-export/giới hạn xuất trên logger/EMS hãng (`control_owner = NATIVE`): ghi tham số, đọc lại, giám sát kết quả tại `MTR_POC`. | F-GRID-04 | P0 | MVP | C2·M1 | K §6 #15, #36 |
| FR-GRID-005 | Khi native không có chức năng, edge phải chạy vòng giới hạn xuất 1 s (PI có anti-windup, hysteresis bất đối xứng: giảm nhanh, tăng chậm), ưu tiên sạc BESS trước khi cắt PV; mất `MTR_POC` quá `T_stale_poc` → PV về giới hạn native, BESS P = 0. | F-GRID-05 | P0 | MVP | C2·M2 | G §3.3(a)(b) |
| FR-GRID-006 | Hệ thống phải giữ P_nhập ≤ `import_cap_w` bằng BESS xả (và giảm EV khi có, P1); native trước, edge khi cần; là mức 5 của arbiter; cảnh báo khi vượt quá `T_import_alarm`. | F-GRID-06 | P0 | MVP | C2·M1 | G §3.3(c); K §6 #16 |
| FR-GRID-007 | Hệ thống phải hiện thanh live "nhập hiện tại / trần nhập" và "xuất / giới hạn xuất"; đếm số lần và tổng thời lượng vi phạm xuất theo ngày/tháng (mục tiêu = 0) theo định nghĩa sự kiện vi phạm ở §2. | F-GRID-07 | P0 | MVP | — | K R-24 |
| FR-GRID-008 | Hệ thống phải đọc trạng thái rơ-le chống phát ngược, tín hiệu cắt giảm từ lưới và máy cắt POC qua DI/Modbus khi có; dùng cho interlock và hiển thị. | F-GRID-13 | P0 | MVP | — | E §3.12 G15 |
| FR-GRID-009 | Hệ thống nên thực thi ngân sách xuất theo kỳ: E_exp_kỳ ≤ tỷ lệ × E_pv_kỳ; khi gần chạm thì ưu tiên sạc BESS, rồi hạ giới hạn xuất tức thời. | F-GRID-08 | P1 | Phase 1 | C2·M2 | C-P11; Q-A03 |
| FR-GRID-010 | Hệ thống nên có đồng hồ demand: công suất trung bình cửa sổ hiện tại (mặc định 30 phút), dự báo cuối cửa sổ, Pmax kỳ; tự bật khi biểu giá có thành phần công suất. | F-GRID-09 | P1 | Phase 1 | — | K R-24 |
| FR-GRID-011 | Hệ thống nên cảnh báo khi Pmax kỳ tiến gần công suất đăng ký hoặc ngưỡng người dùng đặt. | F-GRID-10 | P1 | Phase 1 | — | A D-12 |
| FR-GRID-012 | Hệ thống nên giám sát PF tại POC tính lại từ kWh/kvarh (không trung bình PF), cảnh báo dưới ngưỡng hợp đồng, giải thích "PV bù P làm PF tại POC giảm". | F-GRID-11 | P1 | Phase 1 | — | C-P10 |
| FR-GRID-013 | Edge nên nhận lệnh `GRID_OPERATOR` (giới hạn P, chặn phát ngược) qua slave IEC 104 (FR-INT-023), tạo envelope nội bộ, ưu tiên mức 4, audit thống nhất; DO "bật/tắt phát ngược" khi điều độ yêu cầu. Điều kiện: site trung áp bán dư hoặc PC yêu cầu. | F-GRID-12 | P1 | Phase 1 | C2·M2 | K §6 #32 |
| FR-GRID-014 | Hệ thống nên hiển thị `grid_connected`, sự kiện mất lưới, thời lượng; đổi dạng cân bằng khi đảo. | F-GRID-14 | P1 | Phase 1 | — | C §3.3 T5 |
| FR-GRID-015 | Hệ thống nên hỗ trợ nhiều POC trong một site: cân bằng và giới hạn theo từng POC, không net xuất ở POC A với nhập ở POC B. | F-GRID-15 | P1 | Phase 1 | — | C §3.3 T4 |
| FR-GRID-016 | Hệ thống nên phân tích phụ tải: tải nền, tải không đo, hồ sơ tải theo giờ/thứ, top phụ tải. | F-GRID-16 | P1 | Phase 1 | — | C K06 |
| FR-GRID-017 | Hệ thống nên giám sát máy phát (P, E, trạng thái, giờ chạy) và tách khỏi PV khi mất lưới. | F-GRID-17 | P1 | Phase 1 | — | C §3.3 |
| FR-GRID-018 | Hệ thống có thể đóng/cắt hoặc giảm phụ tải **không quan trọng** trong khung cho phép khi chạm trần nhập. | F-GRID-18 | P2 | Phase 2 | C2·M2 | A §3.6 |
| FR-GRID-019 | Hệ thống có thể bù công suất phản kháng bằng PCS để giữ PF tại POC. | F-GRID-19 | P2 | Phase 2 | C2·M2 | Q-C05, Q-C06 |

**Quy tắc nghiệp vụ**

- **BR-GRID-01** Không có `MTR_POC` hoạt động và đã qua phép thử dấu thì không có chức năng điều khiển lưới nào (zero-export, giới hạn xuất, trần nhập, demand) ở Gate M1 hay M2 (K §6 #10).
- **BR-GRID-02** Một biến một vòng: nếu `control_owner = NATIVE` cho zero-export thì edge không chạy vòng PI trên cùng biến (K §6 #15).
- **BR-GRID-03** Tuân thủ lưới (mức 4) thắng mọi lịch và lệnh tay; lệnh tay bị kẹp với mã `MANUAL_CLAMPED_BY_GRID_LIMIT`.
- **BR-GRID-04** Khi zero-export xung đột với lịch "giữ chỗ", sạc pin để hấp thụ PV trước khi cắt PV (`CHARGE_FORCED_BY_EXPORT_LIMIT`).
- **BR-GRID-05** EMS không thay thiết bị chống phát ngược đã chứng nhận; nếu điện lực yêu cầu rơ-le, rơ-le ưu tiên hơn phần mềm (mức 1–2).
- **BR-GRID-06** Zero-export bắt buộc với hệ trung áp không bán dư theo tóm tắt VBHN 52; với hạ áp là UNKNOWN (Q-A09). Sản phẩm không được ghi "bắt buộc pháp lý cho mọi site".
- **BR-GRID-07** `export_limit_w = 0` khi `export_mode = ZERO_EXPORT`.

**Tiền/hậu điều kiện.** Tiền: `MTR_POC` khai báo và qua phép thử dấu; cho thực thi: Gate M1/M2. Hậu: vi phạm được ghi và có trong bằng chứng tuân thủ.

**Dữ liệu vào / ra**

| Vào | Ra |
|---|---|
| Điểm `meter.*` tại POC (p, q, s, pf, u, i, f, e_import, e_export); DI rơ-le/máy cắt; cấu hình lưới; SOE | Thanh nhập/xuất; sự kiện vi phạm (thời điểm, thời lượng, đỉnh); tham số native; lệnh vòng edge; cảnh báo tuân thủ |

**Phân quyền.** Xem: `site.read`. Đề xuất cấu hình lưới: `soe.propose`; duyệt: `soe.approve` (C3). Lệnh native giới hạn xuất/trần nhập: `cmd.c2`. Test commissioning: `commissioning.execute`.

**Lỗi và trường hợp biên**

| Tình huống | Hành vi |
|---|---|
| `MTR_POC` quality BAD > `T_stale_poc` | Mức 3: PV về giới hạn native, BESS P = 0; cảnh báo Cao "Edge mất MTR_POC"; IL-04 chặn lệnh lưới |
| CT đấu ngược phát hiện khi chạy | Không tự đảo; cảnh báo DQ; yêu cầu chạy lại phép thử dấu |
| Tải giảm đột ngột, PV dư lớn | Vòng giảm PV ngay chu kỳ kế tiếp; sự kiện vi phạm chỉ ghi nếu vượt tol ≥ 2 s |
| Native báo đã đặt giới hạn nhưng POC vẫn xuất | Cảnh báo "giới hạn native không hiệu quả", đề xuất kiểm tra đấu nối công tơ của logger |
| Import cap không giữ được vì BESS hết SOC/khả năng | Cảnh báo Cao sau `T_import_alarm`; P1: giảm EV |

**Tiêu chí chấp nhận**

- **AC-GRID-01** Given site không có `MTR_POC` qua phép thử dấu, When yêu cầu bật Gate M1 cho zero-export, Then hệ thống chặn với lý do BR-GRID-01.
- **AC-GRID-02** Given `export_limit_w` = 0, kWac PV = 500 kW (tol = 5.000 W), When xuất 6 kW trong 3 s rồi về 0, Then ghi 1 sự kiện vi phạm thời lượng 3 s và đỉnh 6 kW; When xuất 4 kW trong 10 s, Then không ghi vi phạm (dưới tol).
- **AC-GRID-03** Given vòng edge làm chủ zero-export (M2), When tải giảm bước 200 kW làm xuất tăng, Then xuất trở về ≤ giới hạn + tol trong ≤ 5 s (mục tiêu ≤ 2 s) trong test commissioning, và kết quả lưu vào biên bản.
- **AC-GRID-04** Given dữ liệu `MTR_POC` không cập nhật 4 s (`T_stale_poc` = 3 s), When chu kỳ edge kế tiếp chạy, Then BESS setpoint = 0, PV giới hạn về giá trị native đã cấu hình, cảnh báo Cao được tạo trong ≤ 2 phút trên cloud (khi online).
- **AC-GRID-05** Given `import_cap_w` = 800 kW và tải tăng làm nhập 850 kW, BESS còn khả năng xả, When vòng trần nhập chạy, Then BESS xả thêm để nhập ≤ 800 kW trong ≤ 5 s và mã lý do ghi mức 5.
- **AC-GRID-06** Given `control_owner(zero-export) = NATIVE`, When cấu hình thêm vòng edge cho cùng chức năng, Then hệ thống từ chối "hai vòng trên cùng biến".
- **AC-GRID-07** Given đổi `export_limit_w` từ 0 sang 50.000, When người đề xuất gửi, Then thay đổi chờ duyệt C3 bởi Control Supervisor khác người và chủ site được thông báo.

**Phụ thuộc.** M-INT (driver công tơ, DI, test), M-OPT (arbiter, `control_owner`), M-BESS (SOE), M-REP (bằng chứng), M-TAR (demand, PF params), [07 Tích hợp](07-device-integration.md).

**Bằng chứng và độ tin cậy**

- [FACT] SolarEdge: giới hạn xuất cần công tơ tại điểm đấu nối; công tơ tiêu thụ không được hỗ trợ — https://knowledge-center.solaredge.com/sites/kc/files/feed-in_limitation_application_note.pdf (qua kết quả tìm kiếm). [FACT] SMA Data Manager cần công tơ POI — https://www.sma-america.com/products/energy-management/data-manager-m-10 (qua kết quả tìm kiếm).
- [FACT, tự công bố của hãng] Huawei SmartLogger5000B/SmartMGC5000B: zero feed-in ≤ 2 s, giới hạn công suất ≤ 5 s — https://solar.huawei.com/admin/asset/v1/pro/view/bb9458d9373d4502912378db3cbc7f2d.pdf và https://www.photomate.eu/smartlogger5000b (qua kết quả tìm kiếm). Chỉ là mục tiêu tham chiếu (K §6 #36).
- [FACT] OpenEMS Controller.Ess.Balancing đưa PCC về `targetGridSetpoint` — https://github.com/OpenEMS/openems/tree/develop/io.openems.edge.controller.ess.balancing (qua kết quả tìm kiếm).
- [FACT] Ampowr peak shaving theo trần lưới (ví dụ 95 kW) — https://ampowr.com/hoge-duin-hotel-enhances-energy-efficiency-with-ampifarm-peak-shaving/ (qua kết quả tìm kiếm).
- [FACT] Chỉ ~287/28.254 hệ đăng ký bán dư — https://vietnamnet.vn/en/rooftop-solar-saves-billions-of-dong-but-one-bottleneck-remains-2552186.html (qua kết quả tìm kiếm).
- [FACT, Low] Yêu cầu QĐ 1570 chỉ qua tóm tắt của vendor có lợi ích — https://www.advantech.com/vi-vn/resources/industry-focus/quyet-dinh-1570qd-evn-dien-mat-troi-mai-nha-dieu-can-biet. Không dùng làm NFR (K §3.4).
- [UNKNOWN] Yêu cầu thiết bị chống phát ngược ở hạ áp và điện lực có chấp nhận vòng phần mềm không (GAP-12, Q-A09).

---

### 5.10 M-EV — Sạc xe điện

**Mục đích nghiệp vụ.** EV là phụ tải điều khiển được, tùy chọn. MVP chỉ **đo** EV như một điểm đo để cân bằng năng lượng và tải nền đúng. Giám sát OCPP, giới hạn công suất và DLM là P1 (K §6 #2, #40). Không xây CSMS thanh toán (ngoài phạm vi).

**Persona.** P2 (chi phí, đội xe), P3 (giám sát), P4 (cấu hình), PI (CPO).

**User story**

| ID | Là… | Tôi muốn… | Để… | FR |
|---|---|---|---|---|
| US-EV-01 | Energy manager (P2) | tách điện năng sạc EV khỏi tải nhà máy | tải nền và báo cáo năng lượng không bị sai | FR-EV-001 |
| US-EV-02 | Operator (P3) | hệ thống tự giảm sạc EV khi nhà máy sắp vượt trần nhập | không nhảy MCCB vì xe điện | FR-EV-005, FR-EV-006 |
| US-EV-03 | Energy manager (P2) | sạc xe bằng PV dư ở site zero-export | dùng PV lẽ ra bị cắt | FR-EV-007 |
| US-EV-04 | Kỹ sư (P4) | tích hợp với CSMS sẵn có của nhà cung cấp trạm sạc | không có hai CSMS tranh nhau một trụ | FR-EV-004 |

**Luồng chính (P1).** (1) Kỹ sư khai báo trụ sạc, connector, công suất, số pha, `I_min`, giao thức, CSMS sở hữu. (2) Chọn đường: edge làm CSMS tối giản (OCPP 1.6J SP ≥ 2) hoặc tích hợp API CPO. (3) Cài `TxDefaultProfile` an toàn. (4) DLM tại edge phân bổ theo dư POC, ưu tiên, kWh cần. (5) Lỗi: mất kết nối trụ → trụ dùng profile mặc định an toàn.

**Yêu cầu chức năng**

| ID | Yêu cầu | F- | Ưu tiên | Phát hành | Hạng·Gate | Căn cứ |
|---|---|---|---|---|---|---|
| FR-EV-001 | Hệ thống phải hỗ trợ điểm đo `MTR_EV_i` cho từng trụ hoặc nhóm; EV tách khỏi tải nền trong cân bằng năng lượng (K32). | F-EV-01 | P0 | MVP | — | C §3.3 T6 |
| FR-EV-002 | Hệ thống nên giám sát trụ qua OCPP: trạng thái connector, phiên (bắt đầu/kết thúc, kWh từ MeterValues), lỗi; qua CSMS cục bộ trên edge hoặc API CPO. | F-EV-02 | P1 | Phase 1 | — | C K32 |
| FR-EV-003 | Edge nên làm CSMS OCPP 1.6J tối giản cho smart charging khi site không có CSMS của CPO; Security Profile ≥ 2 (TLS + Basic), mục tiêu Profile 3; credential OCPP sinh ngẫu nhiên theo site. | F-EV-03 | P1 | Phase 1 | C1·M2 | K §6 #32 |
| FR-EV-004 | Hệ thống nên nhận dữ liệu phiên và gửi giới hạn công suất qua API CPO khi khách đã có CSMS; không chạy CSMS thứ hai trên cùng trụ. | F-EV-04 | P1 | Phase 1 | C1·M2 | E PR-E-10 |
| FR-EV-005 | Hệ thống nên cho `SET_EV_LIMIT` (A hoặc W, số pha) qua ChargePointMaxProfile/TxProfile có `validTo`; giá trị ≥ `I_min` (mặc định 6 A) hoặc 0 để tạm dừng; tham gia trần nhập; hết hạn → TxDefaultProfile an toàn. | F-EV-05 | P1 | Phase 1 | C1·M2 | E §3.19; G §3.3(f) |
| FR-EV-006 | Edge nên chạy DLM: phân bổ theo dư POC, `I_min`, ưu tiên, kWh cần trước giờ đi; cập nhật ≤ 1 lần/10–30 s mỗi trụ; quirk hãng trong driver. | F-EV-06 | P1 | Phase 1 | C1·M2 | G §3.3(f) |
| FR-EV-007 | Hệ thống nên có chế độ sạc chỉ bằng PV dư (hoặc tối thiểu + PV dư). | F-EV-07 | P1 | Phase 1 | C1·M2 | G §3.1 |
| FR-EV-008 | Hệ thống nên gán biểu giá trạm sạc (FR-TAR-004) và báo cáo kWh/chi phí theo phiên, trụ, đội xe. | F-EV-08 | P1 | Phase 1 | — | A #19 |
| FR-EV-009 | Hệ thống có thể dự báo phiên sạc (số phiên, năng lượng, giờ đến/đi). | F-EV-09 | P2 | Phase 2 | — | F §3.12 |
| FR-EV-010 | Hệ thống có thể hỗ trợ OCPP 2.0.1/2.1, ISO 15118, V2X. | F-EV-10 | P2 | Phase 2 | C1·M2 | E PR-E-10 |

**Quy tắc nghiệp vụ**

- **BR-EV-01** EV ở mức 10 của arbiter: luôn nhường trần nhập (mức 5) — giảm về `I_min` rồi tạm dừng phiên ưu tiên thấp (`EV_THROTTLED_IMPORT_CAP`).
- **BR-EV-02** Import cap tức thời do ESS/vòng nhanh gánh; EV chỉ giảm tải bền vững (phản ứng chậm hơn).
- **BR-EV-03** Phiên sạc gắn người là dữ liệu cá nhân (D3) (FR-SEC-019).
- **BR-EV-04** Mỗi trụ chỉ có một CSMS điều khiển.

**Tiền/hậu điều kiện.** Tiền (P1): trụ khai báo, OCPP kết nối, Gate M2, `MTR_POC`. Hậu: phiên và năng lượng lưu; giới hạn có nhật ký.

**Dữ liệu vào / ra.** Vào: `MTR_EV_i`; OCPP StatusNotification, MeterValues, Start/StopTransaction; API CPO. Ra: phiên, kWh, chi phí; profile OCPP; mã lý do DLM.

**Phân quyền.** Xem: `site.read`; phiên gắn người chỉ hiển thị cho vai trò có quyền dữ liệu D3 (ORG_ADMIN, ANALYST theo cấu hình tenant). Giới hạn EV: `cmd.c1`.

**Lỗi và trường hợp biên**

| Tình huống | Hành vi |
|---|---|
| Profile OCPP mặc định của hãng đè TxProfile (quirk) | Driver xử lý; readback dòng thực tế; `APPLIED_CLAMPED` nếu lệch |
| Trụ mất kết nối | TxDefaultProfile an toàn có hiệu lực; năng lượng tính từ `MTR_EV_i` nếu có |
| Dư POC < `I_min` cho mọi phiên | Tạm dừng phiên ưu tiên thấp nhất trước |

**Tiêu chí chấp nhận**

- **AC-EV-01** Given site có `MTR_EV_1` đo 30 kWh trong ngày, When tính tải nền K06 (P1) và cân bằng, Then 30 kWh được tách vào EV, không cộng vào tải nhà máy.
- **AC-EV-02** (P1) Given trần nhập còn dư 10 kW và 3 phiên ưu tiên khác nhau, ba pha 230 V, When DLM chạy, Then phiên ưu tiên cao nhất nhận ≥ 6 A/pha, các phiên không đủ chỗ nhận 0 A, và tổng không vượt dư.
- **AC-EV-03** (P1) Given `SET_EV_LIMIT` hạn 30 phút, When hết hạn, Then trụ về TxDefaultProfile an toàn và trạng thái `EXPIRED`.
- **AC-EV-04** (P1) Given trụ có CSMS của CPO, When kỹ sư bật CSMS cục bộ trên edge cho cùng trụ, Then hệ thống chặn.

**Phụ thuộc.** M-GRID (trần nhập), M-OPT (arbiter mức 10), M-INT (OCPP), M-TAR (biểu giá EV), M-SEC (D3).

**Bằng chứng và độ tin cậy**

- [FACT] OCPP 1.6 có ba loại profile; stackLevel cao thắng; giới hạn hiệu lực là nhỏ nhất — https://www.bender.de/docs/charge-controller/OCPP/ocpp-smart-charging/ (qua kết quả tìm kiếm). [FACT] Easee: TxDefaultProfile có thể đè TxProfile — https://developer.easee.com/docs/ocpp-smart-charging (qua kết quả tìm kiếm).
- [FACT] OCPP 1.6J Security Whitepaper, profile 1–3 — https://openchargealliance.org/?p=159286; OCPP 2.1 công bố 23/01/2025 — https://openchargealliance.org/ocpp-2-1-is-now-available/ (qua kết quả tìm kiếm).
- [FACT] Trạm sạc kinh doanh có biểu giá và công tơ riêng — https://vneconomy.vn/automotive/quy-dinh-moi-ve-gia-ban-dien-cho-tram-sac-xe-dien.htm (qua kết quả tìm kiếm).
- [INFERENCE] `I_min` 6 A là thông lệ IEC 61851 phổ biến (E §3.19), chưa đối chiếu văn bản.
- [UNKNOWN] API CPO phổ biến ở Việt Nam.

---

### 5.11 M-OPT — Tối ưu, lập lịch, điều phối

**Mục đích nghiệp vụ.** Biến biểu giá TOU và trạng thái site thành lịch điều độ an toàn, có giải thích, và một bộ phân xử (arbiter) ở edge bảo đảm mọi nguồn lệnh tuân theo thứ tự ưu tiên cố định. MVP: tầng 1 (luật thời gian thực tại edge) và tầng 2 (bộ sinh lịch luật TOU viết bằng Java). Tầng 3 (MILP/MPC) là P1, bật theo site sau backtest thắng luật. Tầng 4 (VPP/DR) là P2 dạng "VPP-capable" (K §6 #23). Không gọi luật hay tối ưu là AI.

**Persona.** P3 (lịch, chiến lược), P2/P1 (giải thích, chi phí), P4/P5 (arbiter, chủ vòng), PS (duyệt vượt guardrail).

**User story**

| ID | Là… | Tôi muốn… | Để… | FR |
|---|---|---|---|---|
| US-OPT-01 | Operator (P3) | lịch 48 h tự sinh mỗi ngày từ biểu giá TOU | pin sạc PV dư, nạp thấp điểm phần thiếu và xả cao điểm mà tôi không phải lập tay | FR-OPT-005 |
| US-OPT-02 | Chủ C&I (P1) | thấy vì sao pin không xả lúc 15h | tin vào điều khiển | FR-OPT-011 |
| US-OPT-03 | Operator (P3) | site vẫn chạy đúng khi mất cloud | không mất an toàn và giá trị | FR-OPT-006 |
| US-OPT-04 | Kỹ sư (P4) | một chỗ duy nhất quyết định setpoint với thứ tự ưu tiên cố định | lệnh tay, lịch và điều độ không đánh nhau | FR-OPT-001 |
| US-OPT-05 | Energy manager (P2) | so sánh thực tế với kế hoạch theo slot và nguyên nhân lệch | biết nên cải thiện dự báo hay thiết bị | FR-OPT-010 |

**Luồng chính.** WF-06 (chiến lược + lịch), WF-08 (fallback), WF-07 (lệnh tay đi qua arbiter).

**Thứ tự arbiter (cố định, K §6 #16).** Tầng trên **thu hẹp khoảng cho phép** `[P_lo, P_hi]` cho P BESS (và tương tự giới hạn PV, EV); tầng dưới chọn điểm trong khoảng còn lại.

| Mức | Lớp | Ai thực thi | Cấu hình được? |
|---|---|---|---|
| 1 | Bảo vệ native (BMS/PCS/rơ-le/E-stop cứng) | Thiết bị | Không (ngoài phần mềm) |
| 2 | Interlock tại chỗ (LOCAL/REMOTE, trạng thái E-stop, PCCC) | Edge | Không |
| 3 | Giám sát an toàn edge (BMS/POC cũ, lệnh hết hạn, SOE, limit chain) | Edge | Không |
| 4 | Tuân thủ lưới (giới hạn xuất, `GRID_OPERATOR`, chặn phát ngược) | Native hoặc edge | Không |
| 5 | Trần nhập vật lý | Native hoặc edge | Không |
| 6 | Dự phòng backup (được xuống `S_res_hard` để giữ mức 5 nếu cấu hình) | Edge | Không (chỉ tham số) |
| 7 | Lệnh tay của vận hành viên (có hạn, trong SOE) | Edge | Không |
| 8 | DR/VPP (P2) | Edge | Thứ tự 8–11 cấu hình được theo site |
| 9 | Peak shaving theo demand (P1) | Edge | ″ |
| 10 | Cam kết EV (P1) | Edge | ″ |
| 11 | Lịch kinh tế (luật tầng 2 / tối ưu tầng 3) | Cloud tạo → edge | ″ |
| 12 | Chiến lược mặc định của site | Edge | — |

**Yêu cầu chức năng**

| ID | Yêu cầu | F- | Ưu tiên | Phát hành | Hạng·Gate | Căn cứ |
|---|---|---|---|---|---|---|
| FR-OPT-001 | Edge phải có **một** arbiter: mọi nguồn lệnh (điều độ, operator, lịch, optimizer, DR, API) đi qua 12 mức theo bảng trên; mức 1–6 cố định (K §6 #16), mức 7 và 12 giữ vị trí; chỉ thứ tự 8–11 cấu hình theo site; mô hình thu hẹp khoảng cho phép. | F-OPT-01 | P0 | MVP | C1·M2 | K §6 #16 |
| FR-OPT-002 | Arbiter phải báo theo chu kỳ: mức đang thắng, khoảng cho phép hiện hành, mã lý do (`EXPORT_LIMIT_ACTIVE`, `CLAMPED_BY_BMS`, `RESERVE_DIPPED_FOR_IMPORT_CAP`, `OVERRIDDEN_BY_GRID_OPERATOR`, `MANUAL_CLAMPED_BY_GRID_LIMIT`, `NATIVE_MODE_ACTIVE`…); dữ liệu này hiển thị ở header site và trend. | F-OPT-01, F-DASH-04 | P0 | MVP | — | G §3.8 |
| FR-OPT-003 | Hệ thống phải lưu `control_owner ∈ {NATIVE, EDGE}` cho từng chức năng (zero-export, import cap, SOC guard) theo site và từ chối cấu hình hai vòng trên cùng biến; đổi chủ vòng là C3. | F-OPT-02 | P0 | MVP | C3·M1 | K §6 #15 |
| FR-OPT-004 | Khi `control_owner = EDGE`, edge phải chạy tầng 1 chu kỳ 1 s: balancing về `p_grid_target` (PI, anti-windup, ramp), zero-export bằng cắt PV có hysteresis bất đối xứng, trần nhập, SOC guard, kẹp CCL/DCL; ghi Modbus chỉ khi vượt deadband hoặc hết `min_write_interval`. | F-OPT-03 | P0 | MVP | C1·M2 | G §3.3 |
| FR-OPT-005 | Cloud phải chạy bộ sinh lịch luật TOU (tầng 2) lúc 05:30 giờ site và khi có sự kiện: lịch 48 h, slot 15 phút; giữ chỗ cho PV dư; nạp lưới thấp điểm phần thiếu tới SOC đích (nếu `allow_grid_charge`); không xả cho tải giờ bình thường trừ trần nhập; xả cao điểm; Chủ nhật không arbitrage; giữ dự phòng; tôn trọng trần nhập; đọc lịch TOU có phiên bản. Gate M1 xuất ra lịch native; Gate M2 xuất `APPLY_SCHEDULE`. Nhãn UI "Quy tắc". | F-OPT-04 | P0 | MVP | C1·M1 | G §3.4; K §6 #23 |
| FR-OPT-006 | Edge phải lưu lịch ≥ 48 h; hết lịch hoặc lịch hỏng → chiến lược mặc định an toàn của site (thường self-consumption có giới hạn + zero-export, giữ dự phòng); UI báo "đang chạy lịch dự phòng" và khoảng thời gian. | F-OPT-05 | P0 | MVP | C1·M1 | K §6 #17 |
| FR-OPT-007 | DispatchPlan phải theo vòng đời DRAFT → VALIDATED → APPROVED → SCHEDULED → EXECUTING → COMPLETED (+ REJECTED, ABORTED, SUPERSEDED, EXPIRED); bất biến sau duyệt; lưu input snapshot hash (tariff, forecast, config, solver + version); tự duyệt trong guardrail đã được người có quyền phê một lần; vượt guardrail → duyệt tay (`plan.approve`). | F-OPT-06 | P0 | MVP | C1·M1 | G §3.9 |
| FR-OPT-008 | Validator phải kiểm mọi slot trước khi gửi: trong trần site; quỹ đạo SOC trong [S_min, S_max]; không vi phạm export/import; mode có trong `capability_profile`; không xung đột lệnh điều độ hiệu lực; horizon ≥ 48 h; cân bằng năng lượng hợp lý; qua PDP như lệnh C1 và qua Fleet Governor. | F-OPT-07 | P0 | MVP | — | G §3.9; I X-I-03 |
| FR-OPT-009 | Hệ thống phải hiển thị kế hoạch 48 h: dải TOU, dự báo PV/tải, kế hoạch BESS (Xả lên/Sạc xuống, có chữ), SOC dự kiến với dải min/max/dự phòng, P lưới dự kiến vs ngưỡng, giới hạn EV, khối chế độ; nguồn kế hoạch; trạng thái đồng bộ edge (Nháp → Đã gửi → Edge đã nhận #v → Đang chạy; "Chưa đồng bộ" nếu không xác nhận trong 300 s). | F-OPT-08 | P0 | MVP | — | H-P11 |
| FR-OPT-010 | Hệ thống phải lưu `plan_slot_result` theo slot: mode kế hoạch/thực tế, năng lượng BESS, SOC cuối, nhập/xuất, chi phí dự kiến/thực, `deviation_cause` (FORECAST_LOAD, FORECAST_PV, DEVICE_CLAMP, HIGHER_PRIORITY_OVERRIDE(level), COMM_LOSS, MANUAL, NATIVE_MODE), mã lý do; KPI điều độ: % slot APPLIED, lệch SOC, vi phạm xuất (= 0). | F-OPT-10 | P0 | MVP | — | G §3.10 |
| FR-OPT-011 | Hệ thống phải giải thích theo slot bằng mã lý do + câu mẫu (ví dụ "17:30–17:45: xả 180 kW vì giờ cao điểm, dự báo đủ năng lượng tới 22:30 với dự phòng 20%") và chi phí kế hoạch so với baseline "không BESS" (≈ ước tính). | F-OPT-11 | P0 | MVP | — | G §3.11 |
| FR-OPT-012 | Hệ thống nên có trình soạn lịch thủ công: kéo thả khối chế độ, nhập số theo ô, mẫu ngày, cửa sổ đóng băng 15–30 phút, kiểm tra chặn/cảnh báo, diff phiên bản, duyệt. Mobile chỉ xem. | F-OPT-09 | P1 | Phase 1 | C2·M2 | H-P11 |
| FR-OPT-013 | Hệ thống nên hiển thị giá trị biên (shadow price) của 1 kWh trong pin theo slot và của 1 kW giảm đỉnh khi tầng 3 chạy. | F-OPT-12 | P1 | Phase 1 | — | G §3.11 |
| FR-OPT-014 | Hệ thống nên có Optimization Service tầng 3: horizon 48 h, Δt 15 phút, giải lại mỗi 15 phút và theo sự kiện, LP trước MILP sau; infeasible/timeout → lịch tầng 2; bật theo site chỉ sau cổng backtest (FR-OPT-016). Python sidecar chỉ khi ADR-OPT duyệt. Nhãn "tối ưu dựa trên dự báo". | F-OPT-13 | P1 | Phase 1 | C1·M2 | K §6 #23, R-22 |
| FR-OPT-015 | Hệ thống nên cho tham số chi phí suy hao `c_deg` (đ/kWh xả) theo site, hiển thị trên UI; không tuyên bố "tối ưu tuổi thọ". | F-OPT-14 | P1 | Phase 1 | — | G §3.5.3 |
| FR-OPT-016 | Hệ thống nên có backtest: phát lại lịch sử qua code tầng 2/3 với dự báo "như đã có", mô hình edge đơn giản, so perfect foresight; cổng bật tầng 3: 90 ngày backtest rẻ hơn luật ≥ X% (X do sản phẩm quyết) và không tăng vi phạm export/dự phòng/EV; nhãn "Mô phỏng". | F-OPT-15 | P1 | Phase 1 | — | G §3.12 |
| FR-OPT-017 | Hệ thống nên có peak shaving theo demand: `P_allow_rest = (P_target·T_w − E_so_far)/(T_w − t)`, `P_target = max(plan, Pmax tháng)`, kẹp `T_w − t ≥ 60 s`; hỗ trợ `demand_basis` đo/đăng ký. | F-OPT-16 | P1 | Phase 1 | C1·M2 | C §3.9; K R-16 |
| FR-OPT-018 | Hệ thống nên đưa ngân sách xuất theo kỳ vào bộ sinh lịch, tôn trọng `allow_grid_charge`, `allow_ess_export`. | F-OPT-17 | P1 | Phase 1 | C1·M2 | Q-G09 |
| FR-OPT-019 | Hệ thống nên tăng dự phòng SOC khi có cảnh báo bão/mất điện theo lịch, sau khi người dùng xác nhận. | F-OPT-18 | P1 | Phase 1 | C1·M1 | G §3.1 |
| FR-OPT-020 | Hệ thống có thể khởi động/dừng máy phát khi SOC thấp hoặc mất lưới qua DO/controller genset. | F-OPT-19 | P2 | Phase 2 | C2·M2 | G §3.1 |
| FR-OPT-021 | Hệ thống có thể tạo FlexibilityOffer (kW lên/xuống theo slot), nhận sự kiện DR trong envelope (OpenADR 3.0 là ứng viên); không bidding. | F-OPT-20 | P2 | Phase 2 | C1·M2 | K §6 #23 |

**Quy tắc nghiệp vụ**

- **BR-OPT-01** Cloud chỉ gửi ý định có hạn (lịch, mục tiêu); edge arbiter + limit chain quyết định setpoint (K §6 #14).
- **BR-OPT-02** Tầng 2 và 3 cùng xuất DispatchPlan theo slot; đổi tầng không đổi edge.
- **BR-OPT-03** Thứ tự ưu tiên sạc ở VN: PV sắp bị cắt > lưới thấp điểm > (PV bù tải ≈ lưới giờ bình thường) (G §3.15.2, INFERENCE).
- **BR-OPT-04** Không gọi tầng 1/2 là "AI"; tầng 3 là "tối ưu dựa trên dự báo"; backtest/what-if là "Mô phỏng" (K §6 #33).
- **BR-OPT-05** Lệnh tay (mức 7) không vượt khoảng do mức 1–6 cho phép.
- **BR-OPT-06** Phát hiện bất thường không bao giờ tự sinh lệnh điều khiển (F §3.13).
- **BR-OPT-07** Kế hoạch đã APPROVED là bất biến; sửa = phiên bản mới; slot đang chạy kết thúc theo bản cũ trừ khi bản mới `preempt = true`.
- **BR-OPT-08** Lưu giữ: kế hoạch đã thực thi ≥ 1 slot giữ đầy đủ theo chính sách audit; kế hoạch bị thay trước khi chạy giữ tóm tắt + hash 30 ngày (K R-25).

**Tiền/hậu điều kiện.** Tiền: biểu giá + lịch TOU gán; mô hình pin; Gate M1/M2; dự báo F0/F1 (≥ 7 ngày dữ liệu, nếu không dùng profile mặc định). Hậu: plan EXECUTING tại edge; `plan_slot_result` ghi theo slot.

**Dữ liệu vào / ra**

| Vào | Ra |
|---|---|
| Lịch TOU/biểu giá có phiên bản, SOC, mô hình pin, SOE, cấu hình lưới, dự báo tải (F0/F1) và PV, `capability_profile`, lệnh hiện hành | DispatchPlan (version, slot_mode, SOC đích, p_grid_target, cap), envelope `APPLY_SCHEDULE`, lịch native (M1), `plan_slot_result`, mã lý do, chi phí dự kiến |

**Phân quyền.** Xem: `site.read`. Đổi chiến lược mặc định: `cmd.c2`. Duyệt kế hoạch vượt guardrail: `plan.approve`. Chủ vòng: C3. Soạn lịch tay (P1): `cmd.c2`.

**Lỗi và trường hợp biên**

| Tình huống | Hành vi |
|---|---|
| Validator phát hiện SOC dự kiến < S_min ở slot 18:00 | Plan `REJECTED`; cảnh báo Trung bình; edge giữ plan cũ |
| Lệnh điều độ (mức 4) hiệu lực 2 h | Lịch bị treo phần xung đột; slot ghi `OVERRIDDEN_BY_GRID_OPERATOR`; tầng 3 (P1) giải lại |
| Peak shaving (P1) vs TOU: đỉnh rơi giờ bình thường | Mức 9 thắng tại thời điểm vượt, chỉ xả phần cần thiết |
| Chưa đủ 7 ngày dữ liệu tải | Dùng profile mặc định của topology, gắn nhãn "dự báo dự phòng" |
| Edge offline lúc 05:30 | Plan SCHEDULED nhưng không giao; edge chạy lịch cũ (≥ 48 h) rồi mặc định; plan `EXPIRED` nếu hết horizon |

**Tiêu chí chấp nhận**

- **AC-OPT-01** Given lệnh tay xả 300 kW (mức 7) và giới hạn xuất 0 (mức 4) với tải 200 kW, PV 0, When arbiter chạy, Then setpoint xả ≤ 200 kW trừ margin zero-export (không xuất lên lưới), trạng thái `APPLIED_CLAMPED` và mã `MANUAL_CLAMPED_BY_GRID_LIMIT`.
- **AC-OPT-02** Given biểu giá QĐ 963 và một thứ Ba có dự báo PV dư 300 kWh, nhu cầu cao điểm 600 kWh, BESS 1.000 kWh, dự phòng 20%, `allow_grid_charge = true`, α = 0,7, When bộ sinh lịch chạy lúc 05:30, Then (a) không có slot `PEAK_DISCHARGE` ngoài 17:30–22:30, (b) có slot `GRID_CHARGE_TO_TARGET` chỉ trong 00:00–06:00, (c) mọi slot qua validator, (d) horizon ≥ 48 h.
- **AC-OPT-03** Given một Chủ nhật, When sinh lịch, Then không có slot `GRID_CHARGE_TO_TARGET` và không có slot `PEAK_DISCHARGE`.
- **AC-OPT-04** Given edge mất cloud lúc 10:00 với plan còn tới 10:00 ngày kia, When tới 10:00 ngày kia chưa có plan mới, Then edge chuyển chiến lược mặc định và khi online lại UI hiển thị "chạy lịch dự phòng từ … đến …".
- **AC-OPT-05** Given `control_owner(import_cap) = NATIVE`, When kỹ sư bật vòng edge cho import cap, Then hệ thống yêu cầu đổi chủ vòng qua C3 và không cho tồn tại hai vòng.
- **AC-OPT-06** Given plan APPROVED phiên bản 4, When người dùng sửa một slot, Then hệ thống tạo phiên bản 5 ở DRAFT, phiên bản 4 không đổi.
- **AC-OPT-07** Given slot 17:30–17:45 xả theo lịch, When mở giải thích, Then có mã `DISCHARGE_PEAK_TOU` và câu mẫu có giá cao điểm hiện hành và mức dự phòng.
- **AC-OPT-08** Given plan được gửi, When edge không trả `ACCEPTED` trong 300 s, Then UI hiển thị "Chưa đồng bộ" và edge vẫn chạy plan cũ.

**Phụ thuộc.** M-TAR, M-BESS (SOE, mô hình pin), M-GRID, M-ADV (dự báo F0/F1), M-SEC (PDP, ký, Governor), M-INT (envelope, ack), [08 Tối ưu](08-energy-optimization.md).

**Bằng chứng và độ tin cậy**

- [FACT] OpenEMS: điều khiển ESS đi qua Power Solver, không ghi thẳng kênh Modbus — https://community.openems.io/t/ess-that-can-talk-with-openems-using-modbus-tcp/1029; cycle ≈ 1 s — https://openems.github.io/openems.io/openems/latest/edge/architecture.html (qua kết quả tìm kiếm).
- [FACT, Low–Med] Schneider có lịch mặc định 48 h khi mất server (một nguồn, ~2017; 48/72 h mâu thuẫn) — https://marketplace.microsoft.com/en-us/product/saas/869296.microgrid_advisor?tab=overview (qua kết quả tìm kiếm). Lựa chọn 48 h/15 phút của ta là PROPOSAL độc lập (K R-23).
- [FACT] Ampowr chạy tiếp chiến lược khi mất mạng — https://ampowr.com/hoge-duin-hotel-enhances-energy-efficiency-with-ampifarm-peak-shaving/ (qua kết quả tìm kiếm).
- [FACT] Khung QĐ 963 và giá QĐ 1279 (URL ở §5.5). [INFERENCE] Chênh cao điểm/thấp điểm ~2,8× làm TOU arbitrage là giá trị BESS lớn nhất ở VN; ví dụ 3.398 − 1.190/0,9 = 2.076 đ/kWh xả (K đã tính lại).
- [INFERENCE] Không có demand charge đại trà nên lõi MVP là TOU (K R-17). [UNKNOWN] Cơ sở giá hai thành phần (R-16).
- [UNKNOWN] Độ chính xác dự báo ở VN; giá BESS ở VN cho `c_deg` (Q-G10).

---

### 5.12 M-ALM — Cảnh báo, O&M, ticket, work order

**Mục đích nghiệp vụ.** Phục vụ người dùng hằng ngày P0 (O&M/NOC): phát hiện (L0 kiểm tra dữ liệu, L1 quy tắc, L2 thống kê ở P1), vòng đời cảnh báo theo tinh thần ISA-18.2 (không tuyên bố tuân thủ), định tuyến thông báo, và cầu nối **cảnh báo → ticket** (MVP) → work order/SLA (P1). Quy trình O&M chi tiết là khoảng trống nghiên cứu (K G-01, GAP-01); phần dưới là PROPOSAL dựa trên persona P3, mô hình ticket của FusionSolar trong nghiên cứu trước và đề xuất tích hợp VOMS của báo cáo FusionSolar.

**Persona.** P3 (chính), P3t (kỹ thuật viên), P1 (nhận thông báo khi tự giám sát), P4 (quy tắc).

**User story**

| ID | Là… | Tôi muốn… | Để… | FR |
|---|---|---|---|---|
| US-ALM-01 | Operator (P3) | một cảnh báo duy nhất khi edge mất kết nối thay vì 50 cảnh báo thiết bị | không bị ngập và tìm nguyên nhân gốc | FR-ALM-004 |
| US-ALM-02 | Operator (P3) | tạo ticket ngay từ cảnh báo với dữ liệu kèm sẵn | giao việc nhanh, kỹ thuật viên có đủ ngữ cảnh | FR-ALM-010 |
| US-ALM-03 | Kỹ thuật viên (P3t) | nhận ticket được giao, cập nhật và đóng với nguyên nhân | lưu lịch sử xử lý và đo MTTR sau này | FR-ALM-010 |
| US-ALM-04 | Chủ C&I (P1) | chọn nhận cảnh báo mức Cao trở lên qua e-mail | biết sự cố ảnh hưởng sản xuất | FR-ALM-007, FR-ALM-008 |
| US-ALM-05 | Operator (P3) | cảnh báo riêng khi vượt giới hạn xuất hoặc trần nhập | ưu tiên đúng giá trị số 1 ở VN | FR-ALM-009 |
| US-ALM-06 | Operator (P3) | biết khi lệnh không có tác dụng hoặc edge đang chạy lịch dự phòng | không tưởng nhầm điều khiển đang hoạt động | FR-ALM-011 |

**Luồng chính.** WF-10 (cảnh báo → ticket → work order).

**Vòng đời cảnh báo (PROPOSAL).** Ba trục tách riêng (học từ enum gộp của FusionSolar — nghiên cứu trước [workflows_data_model.md](../fusionsolar/04_ghi_chu_nghien_cuu/2_phan_ra_san_pham/workflows_data_model.md)):

| Trục | Giá trị |
|---|---|
| Hoạt động | `ACTIVE`, `CLEARED` (hết, do thiết bị hoặc quy tắc), `CLEARED_BY_USER` (người dùng xóa khi thiết bị không tự hết, có lý do) |
| Xác nhận | `UNACKED`, `ACKED` (người, thời điểm) |
| Xử lý | `NONE`, `TICKETED` (có ticket mở), `RESOLVED` (ticket đóng) |
| Phụ | `SHELVED` (lý do + hạn), `SUPPRESSED_BY_PARENT`, `OUT_OF_SERVICE` (tài sản `maintenance`) |

**Vòng đời ticket (MVP).** `OPEN` → `IN_PROGRESS` → `WAITING` (vật tư, hãng, khách) → `RESOLVED` → `CLOSED`; `CANCELLED` có lý do. Đóng bắt buộc nguyên nhân gốc từ danh mục (thiết bị, lưới, cấu hình, truyền thông, môi trường, người, không xác định) và ghi chú.

**Yêu cầu chức năng**

| ID | Yêu cầu | F- | Ưu tiên | Phát hành | Hạng·Gate | Căn cứ |
|---|---|---|---|---|---|---|
| FR-ALM-001 | Hệ thống phải nhận mã lỗi từ driver/connector, ánh xạ sang danh mục cảnh báo chuẩn (mã, mức Khẩn cấp/Cao/Trung bình/Thông tin, loại tài sản, nguyên nhân/hậu quả/hành động), khử trùng lặp theo occurrence ID, ghi lúc kích hoạt/hết theo giờ site. | F-ALM-01 | P0 | MVP | — | K §6 #39 |
| FR-ALM-002 | Hệ thống phải chạy L0 kiểm tra dữ liệu (phạm vi vật lý, kiểu, đóng băng `FROZEN`, gai, lệch đồng hồ, rollover), gắn cờ DQ; chỉ thành cảnh báo vận hành khi kéo dài quá ngưỡng cấu hình (mặc định 30 phút). | F-ALM-02 | P0 | MVP | — | F §3.13 L0 |
| FR-ALM-003 | Hệ thống phải có quy tắc L1: ngưỡng có hysteresis và thời gian tối thiểu, mẫu theo loại tài sản, ghi đè theo site; lưu `detector_type`, `detector_version`, `evidence` (giá trị, ngưỡng, cửa sổ); nhãn UI "Quy tắc cảnh báo". Bộ mẫu MVP gồm ít nhất: PV = 0 khi G_POA > 200 W/m² quá 15 phút; string 0 A; nhiệt cell > ngưỡng BMS cảnh báo; mất kết nối thiết bị; aux/ngày > ngưỡng. | F-ALM-03 | P0 | MVP | — | F §3.13 L1 |
| FR-ALM-004 | Hệ thống phải sinh một cảnh báo kết nối cho edge/gateway/site sau `T_offline_alarm_edge` (hoặc `T_offline_alarm_connector`), chặn cảnh báo con (suppressed by design) và hiển thị số bị chặn. | F-ALM-04 | P0 | MVP | — | H §3.10 |
| FR-ALM-005 | Hệ thống phải có console cảnh báo theo vòng đời ở trên: tab Active/chưa ack, Active/đã ack, Đã hết chưa ack, Tạm gác (lý do + hạn ≤ 8 h, tự bỏ gác), Ngoài dịch vụ; cột mức (icon hình dạng + chữ), bắt đầu (giờ site), thời lượng, site, tài sản, mã, giá trị/ngưỡng, trạng thái, người ack, ticket; mặc định sắp theo mức rồi thời gian. | F-ALM-05 | P0 | MVP | — | H-P10 |
| FR-ALM-006 | Hệ thống phải có chi tiết cảnh báo: biểu đồ ±2 h quanh thời điểm kích hoạt, lịch sử cùng mã trên tài sản, nguyên nhân/hậu quả/hành động khuyến nghị, thông tin liên hệ site và người trực (nhập tay ở MVP), nút tạo ticket. | F-ALM-06 | P0 | MVP | — | H §3.10; GAP-08 |
| FR-ALM-007 | Người dùng phải đăng ký nhận thông báo theo site × mức × loại, có giờ yên lặng; tenant chọn chế độ "khách tự giám sát" hoặc "O&M giám sát hộ" (định tuyến về NOC của installer). | F-ALM-08 | P0 | MVP | — | B PR-B10 |
| FR-ALM-008 | Hệ thống phải gửi thông báo in-app và e-mail có deep-link; gộp nhiều cảnh báo thành một tin khi lũ; thử lại có backoff khi gửi lỗi. | F-ALM-09 | P0 | MVP | — | — |
| FR-ALM-009 | Hệ thống phải có cảnh báo tuân thủ lưới mức mặc định Cao: sự kiện vi phạm xuất (§2), vượt trần nhập quá `T_import_alarm`, edge mất `MTR_POC`, chế độ chống phát ngược native bị tắt/khác cấu hình. | F-ALM-13 | P0 | MVP | — | K §6 #3 |
| FR-ALM-010 | Hệ thống phải cho tạo ticket từ cảnh báo (thủ công; theo quy tắc là tùy chọn) mang ngữ cảnh cảnh báo, tài sản, ảnh chụp dữ liệu; người xử lý, ưu tiên, trạng thái theo vòng đời ticket; ghi chú, tệp đính kèm; đóng yêu cầu nguyên nhân gốc; một ticket có thể gắn nhiều cảnh báo. | F-ALM-14 | P0 | MVP | — | K G-01; FS "New Ticket" |
| FR-ALM-011 | Hệ thống phải cảnh báo về lệnh và kế hoạch: `UNDELIVERED`, `REJECTED_*`, `FAILED_NO_EFFECT`, `APPLIED_CLAMPED` kéo dài > 15 phút, kế hoạch không đồng bộ > 300 s, edge chạy lịch dự phòng, interlock đang chặn, Gate M2 tạm ngưng. | F-ALM-21 | P0 | MVP | — | E §3.19; H §3.12 |
| FR-ALM-012 | Hệ thống nên gom lũ cảnh báo (> N cảnh báo/10 phút tại một site → một dòng "Lũ cảnh báo" có nguyên nhân gốc đoán được) và khử dao động (> K lần/giờ → gom, gợi ý chỉnh deadband, không tự đổi). | F-ALM-07 | P1 | Phase 1 | — | H-P10 |
| FR-ALM-013 | Hệ thống nên gửi cảnh báo qua Zalo (OA/ZNS) theo template đã duyệt, deep-link, gộp tin, tùy chọn theo tenant. | F-ALM-10 | P1 | Phase 1 | — | GAP-06 |
| FR-ALM-014 | Hệ thống nên có push di động/web push; SMS chỉ cho mức Khẩn cấp nếu khách yêu cầu. | F-ALM-11 | P1 | Phase 1 | — | — |
| FR-ALM-015 | Hệ thống nên leo thang khi cảnh báo Khẩn cấp/Cao không được ack trong T phút và có lịch trực theo ca. | F-ALM-12 | P1 | Phase 1 | — | GAP-08 |
| FR-ALM-016 | Hệ thống nên tạo work order từ ticket: kỹ thuật viên, lịch, checklist theo loại tài sản, ảnh/biên bản, vật tư, chữ ký; mobile offline; đóng với nguyên nhân gốc và nhãn; tài sản chuyển `maintenance` trong khung công việc nếu chọn. | F-ALM-15 | P1 | Phase 1 | — | K G-01 |
| FR-ALM-017 | Hệ thống nên theo dõi SLA: thời gian phản hồi/khắc phục theo mức, MTTR, tổn thất kWh ước tính theo sự cố, availability theo hợp đồng. | F-ALM-16 | P1 | Phase 1 | — | A §3.3 P3 |
| FR-ALM-018 | Hệ thống nên có kế hoạch bảo trì định kỳ (vệ sinh tấm, chụp nhiệt, kiểm tra BESS…) tự sinh work order. | F-ALM-17 | P1 | Phase 1 | — | FS Inspection |
| FR-ALM-019 | Người dùng nên đánh dấu cảnh báo đúng/sai và nguyên nhân gốc; lưu làm nhãn cho mô hình có đánh giá sau này. | F-ALM-18 | P1 | Phase 1 | — | F §3.13 |
| FR-ALM-020 | Hệ thống nên đồng bộ hai chiều ticket/work order với CMMS của khách qua API/webhook, khóa trùng, cấu hình bên nào là nguồn sự thật. | F-ALM-19 | P1 | Phase 1 | — | GAP-01 |
| FR-ALM-021 | Hệ thống nên phát hiện bất thường thống kê L2 (peer, residual, CUSUM/EWMA cho PR, RTE, aux), nhãn "Phân tích thống kê", báo tỷ lệ cảnh báo sai. | F-ALM-20 | P1 | Phase 1 | — | F-P20 |
| FR-ALM-022 | Hệ thống nên phát hiện điều khiển ngoài: `EXTERNAL_CONTROL_DETECTED` khi chế độ/setpoint thiết bị đổi không do edge. | F-ALM-22 | P1 | Phase 1 | — | I AC-06 |

**Quy tắc nghiệp vụ**

- **BR-ALM-01** Nhãn mức duy nhất: Khẩn cấp / Cao / Trung bình / Thông tin; enum i18n, mỗi mức có icon hình dạng riêng (K §6 #39).
- **BR-ALM-02** Ack, xử lý và hết là ba trục riêng; đóng ticket không tự "xóa" cảnh báo còn đang hoạt động.
- **BR-ALM-03** Không được tạm gác cảnh báo an toàn do thiết bị phát ra: cháy/khói/khí, E-stop, BMS bảo vệ cấp cao nhất, lỗi cách điện; chỉ cho ack và ghi chú. Danh sách chốt ở [10](10-security-and-reliability.md).
- **BR-ALM-04** Luật ngưỡng cố định là "Quy tắc cảnh báo", không phải AI (K §6 #33).
- **BR-ALM-05** Phát hiện bất thường không bao giờ tự sinh lệnh điều khiển.
- **BR-ALM-06** Cảnh báo của site `commissioning` chỉ gửi cho đội commissioning; site `suspended` chỉ cảnh báo an toàn và kết nối.
- **BR-ALM-07** Kỹ thuật viên chỉ thấy và sửa ticket được giao hoặc ticket trên site có binding.

**Tiền/hậu điều kiện.** Tiền: danh mục mã cảnh báo theo driver; đăng ký thông báo. Hậu: mọi thay đổi trạng thái cảnh báo/ticket có người, thời điểm.

**Dữ liệu vào / ra**

| Vào | Ra |
|---|---|
| Mã lỗi thiết bị, sự kiện edge, kết quả L0/L1, trạng thái lệnh, trạng thái kết nối | Cảnh báo (3 trục), thông báo, ticket, nhãn nguyên nhân, số liệu cho SLA (P1) |

**Phân quyền.** Xem: `site.read`. Ack: `alarm.ack`. Gác: `alarm.shelve`. Quy tắc: `alarm.rule.configure`. Ticket: `ticket.write` (TECHNICIAN chỉ ticket được giao). Định tuyến người khác: `notify.route.configure`.

**Lỗi và trường hợp biên**

| Tình huống | Hành vi |
|---|---|
| Thiết bị gửi lại cùng occurrence | Không tạo cảnh báo mới |
| Cảnh báo dao động bật/tắt liên tục (MVP) | Hysteresis/thời gian tối thiểu của L1 chặn; gom lũ là P1 |
| Hết hạn gác | Tự bỏ gác; nếu còn ACTIVE thì hiện lại và thông báo lại |
| Người nhận không có e-mail hợp lệ | Ghi "Không gửi được" ở cảnh báo; thông báo in-app cho ORG_ADMIN |
| Ticket gắn tài sản đã thay thế | Giữ liên kết lịch sử theo vị trí tài sản |

**Tiêu chí chấp nhận**

- **AC-ALM-01** Given edge mất kết nối lúc 13:40, When tới 13:45, Then có đúng một cảnh báo kết nối mức Cao cho site và cảnh báo mất kết nối của thiết bị con bị chặn, hiển thị "N cảnh báo bị chặn".
- **AC-ALM-02** Given một cảnh báo được kích hoạt, When đo từ `ts` sự kiện tới lúc e-mail được gửi đi, Then p95 ≤ 2 phút trên tập kiểm thử 1.000 sự kiện.
- **AC-ALM-03** Given cảnh báo "BMS báo cháy/khí", When Operator chọn "Tạm gác", Then nút bị vô hiệu hóa và API trả lỗi `SHELVE_NOT_ALLOWED_SAFETY`.
- **AC-ALM-04** Given cảnh báo Trung bình, When Operator tạo ticket, giao cho Kỹ thuật viên K, Then K nhận thông báo, ticket chứa mã cảnh báo, tài sản, giá trị/ngưỡng và liên kết biểu đồ ±2 h.
- **AC-ALM-05** Given ticket `IN_PROGRESS`, When K đóng mà không chọn nguyên nhân gốc, Then hệ thống chặn.
- **AC-ALM-06** Given lệnh `SET_ESS_P` kết thúc `FAILED_NO_EFFECT`, When trạng thái được ghi, Then sinh cảnh báo Cao "Lệnh không có tác dụng" có `command_id`.
- **AC-ALM-07** Given G_POA = 500 W/m² trong 14 phút và inverter P = 0, When tới phút 15, Then sinh cảnh báo; When G_POA giảm xuống 150 W/m² ở phút 10, Then không sinh cảnh báo.
- **AC-ALM-08** Given xuất vượt `export_limit_w` + tol trong 3 s, When edge báo sự kiện, Then sinh cảnh báo tuân thủ lưới mức Cao với thời lượng và đỉnh.

**Phụ thuộc.** M-MON, M-INT (mã lỗi driver), M-HIST (L0), M-SEC (trạng thái lệnh), M-ORG (người dùng, tài sản `maintenance`), [09 UX/UI](09-ux-ui-specification.html).

**Bằng chứng và độ tin cậy**

- [FACT] FusionSolar có 4 mức cảnh báo, vòng đời 6 trạng thái gắn ticket "defect elimination", nút "New Ticket" có người xử lý và gợi ý — https://solisdepot.com/wp-content/uploads/2023/03/FusionSolar-Smart-PV-Management-System-7.0-After-sales-Technical-Training-Slides.pptx.pdf (qua kết quả tìm kiếm) và nghiên cứu FS trước ([workflows_data_model.md](../fusionsolar/04_ghi_chu_nghien_cuu/2_phan_ra_san_pham/workflows_data_model.md)). Độ tin cậy: Trung bình.
- [FACT] Ampowr AmpiHealth gửi cảnh báo tự động tới đội hỗ trợ — https://ampowr.com/ampihealth/ (qua kết quả tìm kiếm).
- [FACT] SolarEdge cho bật/tắt nhận cảnh báo theo người dùng — https://knowledge-center.solaredge.com/sites/kc/files/se-site-admin-in-solaredge-one-for-c&i-user-guide.pdf (qua kết quả tìm kiếm).
- [FACT] Power Factors gộp APM + CMMS — https://powerfactors.com/why-you-need-an-integrated-apm-platform/ (qua kết quả tìm kiếm).
- [INFERENCE] Mô hình trạng thái theo tinh thần ISA-18.2; edition chưa kiểm chứng (H #24). Ngưỡng EEMUA 191 UNKNOWN (H #25).
- [UNKNOWN] Quy trình O&M thực tế ở VN, nhu cầu Zalo (GAP-01, GAP-06). Cần phỏng vấn 5–8 đơn vị O&M trước khi chốt FR-ALM-016…020.

---

### 5.13 M-INT — Tích hợp thiết bị, edge, API, commissioning

**Mục đích nghiệp vụ.** "Đa hãng" thực chất là **thư viện driver theo model/firmware có trạng thái kiểm chứng**, cộng edge tin cậy (store-and-forward, đồng hồ, OTA) và quy trình commissioning có bằng chứng. Không bao giờ ghi "tương thích mọi inverter/BESS" (K §6 #35). Edge-first giữ nguyên hướng cũ; edge bắt buộc ở mọi site có lệnh (K §6 #13). ADR edge runtime (OpenEMS hay tự xây) bị chặn bởi kiểm tra giấy phép (K R-21).

**Persona.** P4/P5 (chính), PO (vận hành edge fleet), PI (API, P1), PG (IEC 104, P1).

**User story**

| ID | Là… | Tôi muốn… | Để… | FR |
|---|---|---|---|---|
| US-INT-01 | Installer (P4) | claim edge bằng QR và thấy thiết bị tự được phát hiện | rút ngắn thời gian commissioning | FR-INT-002, FR-INT-005 |
| US-INT-02 | Installer (P4) | checklist commissioning có bằng chứng cho từng bước và biên bản PDF | bàn giao cho chủ đầu tư và nộp hồ sơ đấu nối | FR-INT-015, FR-INT-019 |
| US-INT-03 | Kỹ sư (P4) | so giá trị đọc qua driver với màn hình thiết bị | chắc chắn map thanh ghi đúng trước khi tin số liệu | FR-INT-020 |
| US-INT-04 | Kinh doanh/installer (P4) | danh sách thiết bị được hỗ trợ kèm model, firmware, trạng thái kiểm chứng, chức năng đọc/ghi | không hứa sai với khách | FR-INT-013 |
| US-INT-05 | Vận hành nền tảng (PO) | cập nhật firmware edge theo canary có rollback | không làm hỏng cả đội edge | FR-INT-012 |

**Luồng chính.** WF-02 (commissioning), WF-08 (mất cloud), WF-17 (connector cloud).

**Yêu cầu chức năng**

| ID | Yêu cầu | F- | Ưu tiên | Phát hành | Hạng·Gate | Căn cứ |
|---|---|---|---|---|---|---|
| FR-INT-001 | Edge của ta phải bắt buộc ở mọi site mà nền tảng ghi lệnh; PDP chặn mọi lệnh tới site không có edge. Phần cứng tham chiếu: 2×RS485 cách ly, 1×CAN, 2×Ethernet (WAN/OT tách), 4 DI/4 DO, 4G tùy chọn, RTC có pin, SSD/eMMC công nghiệp, watchdog phần cứng. | F-INT-01 | P0 | MVP | — | K §6 #13; E PR-E-12 |
| FR-INT-002 | Hệ thống phải cho claim edge bằng QR/serial, cấp chứng chỉ X.509 riêng (mTLS, hạn 90 ngày, tự gia hạn ở 2/3 hạn), gán site; thu hồi khi gỡ hoặc ngừng site. Edge không có mật khẩu mặc định chung. | F-INT-02 | P0 | MVP | — | I §3.5 |
| FR-INT-003 | Hệ thống phải có framework driver khai báo: register map YAML/JSON có version (word order, scale/SF, sentinel, `sign_convention`, `R_wrap`, access, persist, `min_write_interval`, `watchdog_support`, `revert_timeout_s`) + overlay theo hãng/model/firmware; trạng thái `VERIFIED_LAB` / `VERIFIED_FIELD` / `COMMUNITY` / `UNVERIFIED` hiển thị cho installer. | F-INT-03 | P0 | MVP | — | E PR-E-02 |
| FR-INT-004 | Edge phải là Modbus master duy nhất trên mỗi bus/thiết bị; gom thanh ghi (≤ 125 thanh ghi/lần đọc, ≤ 123/lần ghi), timeout/retry cấu hình theo driver. | F-INT-04 | P0 | MVP | — | E §3.2 |
| FR-INT-005 | Edge phải khám phá SunSpec (quét "SunS" tại 40000/50000/0; đọc model 1, 101–103, 120–124, 201–214, 701–714, 802–804), fingerprint model/firmware → đề xuất driver; báo `capability_profile` lên cloud; cloud chỉ cho tạo lệnh mà profile hỗ trợ. | F-INT-05 | P0 | MVP | — | E §3.3 |
| FR-INT-006 | Thư viện driver MVP phải có, theo thứ tự: (1) công tơ PCC Modbus phổ biến; (2) Huawei SmartLogger + EMMA; (3) SunSpec chung; (4) một dòng tủ BESS có hợp đồng cung cấp register map; (5) Sungrow EMS300CP/PowerStack sau khi có map chính thức. Thứ tự có thể đổi sau đánh giá thị phần (GAP-11). | F-INT-06 | P0 | MVP | — | E PR-E-08 |
| FR-INT-007 | Edge phải ánh xạ lệnh chuẩn → chuỗi ghi theo driver, đọc lại trong dung sai và timeout, báo `APPLIED` / `APPLIED_CLAMPED` / `FAILED_{DEVICE_EXCEPTION, NO_EFFECT, TIMEOUT}`. | F-INT-07 | P0 | MVP | C1·M1 | K §6 #21 |
| FR-INT-008 | Uplink phải là MQTT 5 + mTLS, outbound-only, lô nhị phân nén (mục tiêu ≤ 15 B/mẫu), `seq` + ack, topic `ems/v1/{edge_id}/up/{state, telemetry/{stream}, event, backfill, cmd-ack}` và `ems/v1/{edge_id}/down/{cmd, config}`, lệnh không retained + Message Expiry, ACL theo `edge_id`, cấm wildcard subscribe từ edge. | F-INT-08 | P0 | MVP | — | K §6 #20, R-12 |
| FR-INT-009 | Edge phải store-and-forward: không mất dữ liệu khi mất mạng ≤ 7 ngày; mục tiêu buffer 30 ngày ở tần suất cloud; dữ liệu 1 s vòng tròn 7 ngày; xả buffer có giới hạn tốc độ, realtime trước, backfill trên topic riêng. | F-INT-09 | P0 | MVP | — | K §6 #18 |
| FR-INT-010 | Edge phải đồng bộ thời gian (chrony ≥ 2 nguồn + RTC), báo `clock_state` và offset trong telemetry; `UNSYNCED` chặn lệnh (IL-06); đặt giờ thiết bị theo lịch nếu driver hỗ trợ. | F-INT-10 | P0 | MVP | — | E PR-E-13 |
| FR-INT-011 | Hệ thống phải quản lý cấu hình edge theo mô hình desired/reported có version; config ký số (edge từ chối config không ký); sau reconnect edge báo lệnh đang hiệu lực, config version, plan version để cloud đối soát và cảnh báo khi lệch. | F-INT-11 | P0 | MVP | — | E §3.12 G11, G12 |
| FR-INT-012 | Hệ thống phải OTA firmware edge: A/B ký số, rollback tự động, anti-rollback, canary 1% → 10% → 100% có thời gian chờ; không tự cập nhật firmware thiết bị của hãng. Cập nhật là C3. | F-INT-12 | P0 | MVP | C3·M1 | I NFR-SEC-020 |
| FR-INT-013 | Hệ thống phải có trang "Thiết bị được hỗ trợ": model + firmware + trạng thái kiểm chứng + chức năng đọc/ghi; không có câu "tương thích mọi thiết bị". | F-INT-23 | P0 | MVP | — | K §6 #35 |
| FR-INT-014 | Phải có bộ mô phỏng thiết bị nội bộ (Modbus inverter/PCS/BMS/công tơ có dấu cấu hình được, OCPP charger, lỗi giao tiếp, thiết bị không có watchdog) và lab HIL; dùng trong CI và test an toàn. | F-INT-24 | P0 | MVP | — | K G-05; GAP-13 |
| FR-INT-015 | Hệ thống phải có checklist commissioning theo topology (WF-02): claim → kết nối/đồng hồ → khám phá → gán driver → xác minh map → phép thử dấu → chủ vòng → cấu hình native → test giới hạn xuất → (M2) test watchdog/LOCAL-REMOTE → (M2) SOE → biên bản; mỗi bước có bằng chứng, người làm, thời điểm; bước bắt buộc chưa đạt thì không cho `active`. | F-INT-25 | P0 | MVP | — | K G-02 |
| FR-INT-016 | Hệ thống phải có phép thử dấu cho mỗi điểm đo: tạo tình huống biết trước (BESS sạc nhỏ ≥ 5% P định mức hoặc ≥ 5 kW trong ≥ 60 s; giới hạn PV), kiểm hướng P, Q, thanh ghi nhập/xuất; ghi kết quả vào biên bản. | F-INT-26 | P0 | MVP | C1·M1 | K §6 #10 |
| FR-INT-017 | Hệ thống phải có test giới hạn xuất: kịch bản giảm tải/tăng PV; đo thời gian đưa xuất về ≤ giới hạn + tol và số giây vượt; đạt khi ≤ 5 s (mục tiêu tham chiếu ≤ 2 s); lưu làm bằng chứng (FR-REP-007). | F-INT-27 | P0 | MVP | C2·M1 | E F-28 |
| FR-INT-018 | Hệ thống phải có test watchdog và fail-safe: rút cáp edge↔thiết bị, mất `MTR_POC`, edge mất cloud, chuyển LOCAL; kiểm thiết bị về mặc định trong `revert_timeout_s` và BESS P = 0/native; thiết bị không đạt → `requires_native_fallback = true`. | F-INT-28 | P0 | MVP | C2·M2 | K §6 #17 |
| FR-INT-019 | Hệ thống phải sinh biên bản commissioning PDF: cấu hình, kết quả từng test, phiên bản driver/SOE, chữ ký người làm và người nghiệm thu; lưu vào tài liệu site. | F-INT-29 | P0 | MVP | — | K G-02 |
| FR-INT-020 | Hệ thống phải có bước xác minh map điểm: với mỗi thiết bị, so ≥ 1 giá trị công suất, 1 điện áp, 1 bộ đếm năng lượng (và SOC với BESS) với giá trị tham chiếu (màn hình thiết bị, đồng hồ cầm tay, nameplate); đạt khi lệch công suất ≤ 2% hoặc ≤ 1 kW, điện áp ≤ 1%, đơn vị/scale đúng; ghi "Khớp/Lệch". | F-INT-25, F-INT-03, F-MON-06 | P0 | MVP | — | K G-02; E §3.2 |
| FR-INT-021 | Hệ thống nên có connector cloud chỉ đọc cho Sungrow iSolarCloud, SMA, Solis, Growatt, Deye: rate limiter theo endpoint, backfill ban đêm, quality `UNCERTAIN_VENDOR_CLOUD`. | F-INT-13 | P1 | Phase 1 | — | E PR-E-11 |
| FR-INT-022 | Edge nên nghe CAN BMS ở chế độ listen-only khi không có northbound; không chen vào bus bảo vệ. | F-INT-15 | P1 | Phase 1 | — | E §3.4 |
| FR-INT-023 | Edge nên có slave IEC 60870-5-104 với bảng điểm cấu hình được, chạy độc lập cloud, trên conduit riêng; phục vụ FR-GRID-013. | F-INT-16 | P1 | Phase 1 | C2·M2 | K §6 #32 |
| FR-INT-024 | Edge nên làm Modbus TCP server xuất lại dữ liệu cho SCADA/BMS tòa nhà của khách (Sparkplug B là P2). | F-INT-17 | P1 | Phase 1 | — | E G14 |
| FR-INT-025 | Hệ thống nên có API REST đọc: OAuth2 client credentials, scope tối thiểu, mặc định chỉ đọc, hạn mức công bố theo tenant, phân trang theo thời gian, giới hạn cửa sổ theo độ phân giải, version trong đường dẫn, tài liệu công khai. | F-INT-19 | P1 | Phase 1 | — | K G-11 |
| FR-INT-026 | Hệ thống nên có webhook: cảnh báo mở/đóng, trạng thái lệnh, báo cáo sẵn sàng, ticket; ký HMAC, retry có backoff, idempotency key. | F-INT-20 | P1 | Phase 1 | — | E §3.11 |
| FR-INT-027 | Hệ thống nên cho nhập CSV lịch sử và file load profile công tơ EVN khi có, gắn origin và quality. | F-INT-22 | P1 | Phase 1 | — | GAP-14 |
| FR-INT-028 | Hệ thống có thể ghi qua cloud hãng (Huawei OAuth Connect control API, task async, không gọi chồng) chỉ cho lịch chậm, cờ riêng, C2 trở lên. | F-INT-14 | P2 | Phase 2 | C2·M1 | I NFR-SEC-018 |
| FR-INT-029 | Hệ thống có thể có adapter IEC 61850 MMS client, DNP3 outstation, OpenADR 3.x VEN, IEEE 2030.5 client. | F-INT-18 | P2 | Phase 2 | — | K §6 #32 |
| FR-INT-030 | Hệ thống có thể cho API lệnh cho bên thứ ba: scope ghi cho client máy (C1 trong SOE), qua PDP và Fleet Governor, mặc định 0 lệnh. | F-INT-21 | P2 | Phase 2 | C1·M2 | I §3.7.6 |

**Quy tắc nghiệp vụ**

- **BR-INT-01** Thanh ghi lấy từ diễn đàn không được vào driver `VERIFIED_*` khi chưa có tài liệu hãng hoặc thử lab (K §6 #35).
- **BR-INT-02** Driver không `VERIFIED_*` chỉ được đọc; IL-05 chặn lệnh ghi tới thiết bị đó.
- **BR-INT-03** Connector cloud hãng mặc định chỉ đọc; không dùng cho điều khiển nhanh (K R-09).
- **BR-INT-04** Không ghi setpoint chu kỳ vào thanh ghi `persist = NVM` trừ khi hãng xác nhận chịu được (E PR-E-15).
- **BR-INT-05** Khi edge `REMOTE`, công cụ engineering của installer không được kết nối OT LAN làm master Modbus thứ hai; phải chuyển LOCAL/MAINTENANCE.
- **BR-INT-06** Phép thử dấu không bao giờ tự đảo dấu âm thầm; đảo `sign_convention` là thay đổi có lý do và audit.

**Tiền/hậu điều kiện.** Tiền: edge có nguồn, Internet outbound 8883/443; người dùng `commissioning.execute`/`edge.manage`. Hậu: edge gắn site, driver có version, biên bản lưu.

**Dữ liệu vào / ra**

| Vào | Ra |
|---|---|
| Serial/QR edge, kết quả khám phá, register map, kết quả test, lệnh ký từ cloud, config ký | Telemetry/event/backfill/cmd-ack; `capability_profile`; trạng thái edge; biên bản; trang thiết bị được hỗ trợ |

**Phân quyền.** `edge.manage`, `asset.configure`, `commissioning.execute` (SITE_ENGINEER); OTA `edge.ota` (PLATFORM_ADMIN, C3); thư viện driver: PLATFORM_ADMIN; API client (P1): `api.client.manage`.

**Lỗi và trường hợp biên**

| Tình huống | Hành vi |
|---|---|
| Huawei SmartLogger chỉ nhận một kết nối Modbus TCP | Edge giữ kết nối duy nhất; cảnh báo nếu phát hiện client khác |
| Exception Modbus 01/02/03 | `BAD_CONFIG` ở điểm, ghi nhật ký bus |
| Buffer đầy (> 30 ngày) | Bỏ dữ liệu cũ nhất của lớp ưu tiên thấp trước (C3 rồi C2); không bao giờ bỏ thanh ghi và sự kiện trong 7 ngày gần nhất; cảnh báo trước khi đầy 80% |
| OTA lỗi khi khởi động bản mới | Rollback A/B tự động; dừng canary; cảnh báo PO |
| Chứng chỉ edge sắp hết hạn, gia hạn lỗi 14 ngày | Cảnh báo Cao; nếu hết hạn edge vẫn điều khiển cục bộ, mất uplink |

**Tiêu chí chấp nhận**

- **AC-INT-01** Given edge mới chưa claim, When kỹ sư quét QR và gán site S, Then edge nhận chứng chỉ vận hành hạn 90 ngày, kết nối được tới `ems/v1/{edge_id}/up/#` và **không** subscribe được topic của edge khác.
- **AC-INT-02** Given edge mất mạng 7 ngày với site tham chiếu 1.000 điểm, When kết nối lại, Then 100% mẫu ở tần suất cloud và 100% thanh ghi biên 5 phút của 7 ngày đó tới cloud, dữ liệu realtime vẫn được ưu tiên trong lúc backfill.
- **AC-INT-03** Given driver `COMMUNITY` cho PCS, When Operator gửi lệnh tới PCS, Then lệnh bị chặn (IL-05) và UI ghi "driver chưa kiểm chứng — chỉ đọc".
- **AC-INT-04** Given xác minh map: màn hình inverter 102,0 kW, driver đọc 10,2 kW, When kỹ sư nhập giá trị tham chiếu, Then bước ghi "Lệch — có thể sai scale ×10" và không cho qua bước.
- **AC-INT-05** Given phép thử dấu với BESS sạc 20 kW, When `MTR_BESS` đọc +20 kW (quy ước BESS + = xả), Then phép thử "Không đạt — dấu ngược" và yêu cầu kỹ sư chọn cách xử lý có lý do.
- **AC-INT-06** Given test watchdog: rút cáp RS485 tới PCS đang xả theo setpoint 100 kW, `revert_timeout_s` = 30 s, When đo, Then PCS về 0 kW hoặc chế độ native trong ≤ 30 s + 1 chu kỳ poll; nếu không, thiết bị được gắn `requires_native_fallback = true`.
- **AC-INT-07** Given edge nhận config không có chữ ký hợp lệ, When xử lý, Then edge từ chối, giữ config cũ và báo `REJECTED_SIGNATURE`.
- **AC-INT-08** Given OTA canary 1% có một edge rollback, When pipeline đánh giá, Then rollout dừng trước bước 10% và PO nhận cảnh báo.
- **AC-INT-09** Given kết nối lại sau mất cloud, When edge báo lệnh đang hiệu lực khác danh sách cloud, Then cloud sinh cảnh báo "lệch trạng thái lệnh sau kết nối lại" và không tự gửi lại lệnh đã hết hạn.

**Phụ thuộc.** M-SEC (chứng chỉ, ký, OT/IT), M-MON, M-HIST, M-GRID, M-BESS, [07 Tích hợp](07-device-integration.md) (checklist chi tiết, hợp đồng điểm/lệnh), [06 Kiến trúc](06-system-architecture.html) (ADR edge runtime).

**Bằng chứng và độ tin cậy**

- [FACT] Modbus không quy định thứ tự word 32 bit — https://docs.chipkin.com/articles/modbus-data-types-byte-order-reference/ (qua kết quả tìm kiếm).
- [FACT] SunSpec 700 series đã APPROVED — https://sunspec.org/sunspec-modbus-700-series-der-information-models-are-now-approved/; thiết bị có chứng nhận UL 1741 SB vẫn có lỗi giao diện SunSpec — https://sunspec.org/communication-interface-defects-revealed-inul-1741-sb-certified-inverters/ (qua kết quả tìm kiếm). Lý do bắt buộc xác minh map và phép thử dấu.
- [FACT] MQTT 5 Message Expiry — https://www.emqx.com/en/blog/mqtt-message-expiry-interval (qua kết quả tìm kiếm).
- [FACT] SolarEdge ONE Controller C&I: 2×RS485, CAN, 2×RJ45, 4DI/4DO, Modbus TCP 1502 — https://knowledge-center.solaredge.com/sites/kc/files/se-one-controller-commercial-and-industrial-datasheet-eng.pdf (qua kết quả tìm kiếm).
- [FACT] FusionSolar installer thêm thiết bị bằng quét QR — https://solar.huawei.com/en/products/smart-pv-management-system-installer (qua kết quả tìm kiếm).
- [FACT] Inverter Huawei phát hiện mất liên lạc mặc định 3 s — https://support.huawei.com/enterprise/en/doc/EDOC1100173984/6d72858a/setting-parameters-over-the-app (qua kết quả tìm kiếm). [UNKNOWN] Watchdog từng hãng (Q-I-07).
- [FACT] Forescout SUN:DOWN: 46 lỗ hổng ở Sungrow, Growatt, SMA — https://forescout.com/press-releases/forescout-vedere-labs-uncovers-severe-systemic-security-risks-in-global-solar-power-infrastructure (qua kết quả tìm kiếm). Lý do OTA ký số.
- [FACT] OpenEMS có ResendData — https://openems.github.io/openems.io/openems/latest/edge/architecture.html (qua kết quả tìm kiếm). [UNKNOWN] Giấy phép OpenEMS (repo có EPL-2.0 và AGPL-3.0 — https://github.com/OpenEMS/openems), chặn ADR edge runtime (K R-21).
- [FACT] Tham số IEC 104 điển hình k=12, w=8, t1=15 s — https://infosys.beckhoff.com/content/1031/tf6500_tc3_iec60870_5_10x/984040459.html (qua kết quả tìm kiếm). [UNKNOWN] Bảng điểm EVN (Q-E-01).
- [UNKNOWN] Thị phần Deye/Solarman, Growatt, Solis C&I ở VN (GAP-11); phần cứng edge và BOM (GAP-17).

---

### 5.14 M-SEC — Bảo mật, an toàn lệnh, tuân thủ

**Mục đích nghiệp vụ.** Bảo đảm rằng lệnh có tác động vật lý chỉ được phát bởi đúng người, đúng phạm vi, trong vùng an toàn, có hạn, có chữ ký, có dấu vết, và rằng một tài khoản bị chiếm không thể gây tác động hàng loạt. Cloud không nằm trong vòng bảo vệ (K §6 #14). Đặc tả kỹ thuật đầy đủ thuộc [10 An toàn](10-security-and-reliability.md); mục này là yêu cầu nghiệp vụ và tiêu chí chấp nhận.

**Persona.** PS (duyệt), PA (người dùng, kill switch), PO (nền tảng), P3/P4 (phát lệnh), P1 (đồng ý bật điều khiển, nhận thông báo).

**User story**

| ID | Là… | Tôi muốn… | Để… | FR |
|---|---|---|---|---|
| US-SEC-01 | Chủ C&I (P1) | điều khiển từ xa tắt mặc định và chỉ bật khi tôi đồng ý | không ai tác động tài sản của tôi khi tôi chưa biết | FR-SEC-005 |
| US-SEC-02 | Control Supervisor (PS) | hàng đợi duyệt lệnh nguy hiểm có diff và tác động MW | quyết định nhanh và đúng | FR-SEC-007 |
| US-SEC-03 | Quản trị tổ chức (PA) | tắt toàn bộ điều khiển từ xa của tenant bằng một thao tác | phản ứng khi nghi tài khoản bị chiếm | FR-SEC-013 |
| US-SEC-04 | Operator (P3) | một trang cho biết vì sao lệnh của tôi bị từ chối | khỏi đoán mò | FR-SEC-011 |
| US-SEC-05 | Chủ tài sản (P6) | nhật ký không sửa được của mọi lệnh và phê duyệt | giải quyết tranh chấp bảo hành và hợp đồng | FR-SEC-014 |
| US-SEC-06 | Kỹ sư (P4) | biết site còn thiếu gì để bật Gate M2 | chuẩn bị đủ trước khi xin duyệt | FR-SEC-021 |

**Luồng chính.** WF-05 (Gate M2), WF-07 (lệnh và phê duyệt), WF-13 (kill switch, Governor), WF-12 (grant).

**Trạng thái lệnh (mở rộng từ E §3.19 theo K §6 #21).** `CREATED → [PENDING_APPROVAL → APPROVED | APPROVAL_REJECTED | APPROVAL_EXPIRED] → AUTHORIZED → SENT → RECEIVED → ACCEPTED | REJECTED_{STALE, INVALID, UNSUPPORTED, OUT_OF_LIMIT, LOWER_PRIORITY, INTERLOCK:<IL>, SIGNATURE, REPLAY} → DISPATCHED → APPLIED | APPLIED_CLAMPED | FAILED_{DEVICE_EXCEPTION, NO_EFFECT, TIMEOUT} → SUPERSEDED | CANCELLED | EXPIRED → COMPLETED`; phía cloud: `SENT` quá `expires_at` không có `RECEIVED` → `UNDELIVERED`. Enum cuối cùng thuộc [05](05-domain-model.html).

**Interlock tại edge (I §3.7.3).** IL-01 LOCAL/MAINTENANCE · IL-02 E-stop đang tác động · IL-03 BMS lỗi hoặc dữ liệu BMS cũ > `T_stale_bms` · IL-04 mất `MTR_POC` · IL-05 driver chưa `VERIFIED_*` hoặc `BAD_COMM` · IL-06 đồng hồ không `SYNCED` · IL-07 lệnh `GRID_OPERATOR` xung đột · IL-08 PCCC/khí/nhiệt báo động · IL-09 cửa tủ/bảo trì (nếu có DI) · IL-10 site đang `commissioning` (trừ lệnh test trong checklist).

**Yêu cầu chức năng**

| ID | Yêu cầu | F- | Ưu tiên | Phát hành | Hạng·Gate | Căn cứ |
|---|---|---|---|---|---|---|
| FR-SEC-001 | Hệ thống phải xác thực bằng OIDC Authorization Code + PKCE; access token ngắn hạn, refresh rotation có phát hiện tái sử dụng; idle 30 phút, tuyệt đối 12 h; rate limit đăng nhập và kiểm mật khẩu lộ. SSO doanh nghiệp là P1. | F-SEC-01 | P0 | MVP | — | I §3.3 |
| FR-SEC-002 | MFA bắt buộc cho mọi vai trò có quyền ghi và admin (ưu tiên WebAuthn, TOTP phụ, không chỉ SMS); step-up ≤ 5 phút cho C2/C3. | F-SEC-02 | P0 | MVP | — | K §6 #27 |
| FR-SEC-003 | Mọi request phải qua RBAC theo cây; mọi lệnh phải qua PDP đánh giá chủ thể (vai trò, `auth_time`, loại client), tài nguyên (`lifecycle`, `control_enabled`, `local_remote`, `kill_switch`, Gate, driver, SOE), hành động (loại, hạng, ΔP, TTL), ngữ cảnh (ngân sách đội, giờ, số lệnh gần đây); kết quả PDP gồm hạng thực tế và lý do từ chối. | F-SEC-03 | P0 | MVP | — | K §6 #29 |
| FR-SEC-004 | Tenant phải cô lập bằng PostgreSQL RLS với FORCE, role ứng dụng không owner/không BYPASSRLS, `SET LOCAL` mỗi transaction, lọc lớp thứ hai trong repository; cô lập ở MQTT ACL, object storage, cache, job; test cross-tenant tự động trong CI cho mọi endpoint. | F-SEC-04 | P0 | MVP | — | K §6 #29 |
| FR-SEC-005 | Monitoring plane và control plane phải tách danh tính dịch vụ, credential, topic, quyền DB, namespace, quy trình release; `control_enabled` mặc định `false`; bật là C3 sau commissioning và chỉ khi có bản ghi đồng ý của chủ tài sản. | F-SEC-05 | P0 | MVP | C3·M1 | K §6 #26 |
| FR-SEC-006 | Hệ thống phải phân hạng mọi loại lệnh C0–C4 (bảng §2 ngưỡng nâng hạng); C4 không có API; PDP nâng hạng theo ngữ cảnh, không bao giờ hạ dưới hạng tối thiểu của loại lệnh. | F-SEC-06 | P0 | MVP | C3·M2 | K §6 #28 |
| FR-SEC-007 | Hệ thống phải có hàng đợi phê duyệt C3: người duyệt khác người yêu cầu và khác vai trò, cả hai step-up MFA; hiển thị diff trước/sau, tác động MW, site, hạn; cửa sổ duyệt ≤ 15 phút; hết hạn → `APPROVAL_EXPIRED`; thông báo chủ site. | F-SEC-06 | P0 | MVP | C3·M2 | I FR-SEC-001 (mã tạm) |
| FR-SEC-008 | Mọi lệnh phải đóng gói trong envelope: `command_id` (UUID v7, idempotency), `correlation_id`, `source` (GRID_OPERATOR/OPERATOR/SCHEDULE/OPTIMIZER/DR/API), `issued_by`, `target`, `type`, `params`, `valid_from`, `expires_at` (bắt buộc), `on_expiry` (mặc định `REVERT_DEFAULT`), `supersedes`, `max_latency_ms`, `tolerance`, `dry_run`, `seq` đơn điệu theo (site, signer), `danger_class`, `approval_ref`, `kid`, chữ ký JWS (KMS) bắt buộc; ack do edge ký. | F-SEC-07 | P0 | MVP | — | K §6 #21, R-11 |
| FR-SEC-009 | Hệ thống phải theo dõi trạng thái lệnh theo máy trạng thái ở trên; không gửi lại sau `expires_at`; retry chỉ trong hạn; UI không cập nhật lạc quan — chỉ hiện "đã áp dụng" sau `APPLIED`/`APPLIED_CLAMPED`. | F-SEC-07, F-SEC-14 | P0 | MVP | — | H §3.12 |
| FR-SEC-010 | Edge phải thực thi IL-01…IL-10 trả `REJECTED_INTERLOCK:<code>`; site Gate M2 có BESS phải có công tắc LOCAL/REMOTE phần cứng nối DI, hoặc chế độ local/remote của thiết bị native mà edge đọc được và có biên bản commissioning. | F-SEC-08 | P0 | MVP | C1·M2 | K §3.8 |
| FR-SEC-011 | Hệ thống phải có trang trạng thái điều khiển site: LOCAL/REMOTE, kill switch, Gate, SOE version, interlock đang tác động, nguồn lệnh thắng, fallback đang chạy, `control_owner` từng chức năng, thiết bị `requires_native_fallback`. | F-SEC-09 | P0 | MVP | — | I FR-SEC-002 (mã tạm) |
| FR-SEC-012 | Hệ thống phải có Fleet Dispatch Governor: Σ\|ΔP\| được lệnh trong 5 phút ≤ ngưỡng tenant (mặc định 20% MW BESS) và ngưỡng nền tảng; jitter 0–300 s cho lệnh đồng loạt (trừ điều độ); vượt → hàng đợi + C3. | F-SEC-10 | P0 | MVP | C1·M2 | K §6 #30 |
| FR-SEC-013 | Hệ thống phải có kill switch điều khiển từ xa theo site/tenant/nền tảng: edge nhận lệnh ký `REMOTE_CONTROL_SUSPENDED` và chạy chiến lược mặc định cục bộ; tắt là C1, bật lại là C3; tên hiển thị không dùng chữ "E-stop". | F-SEC-11 | P0 | MVP | C3·M2 | K §6 #30 |
| FR-SEC-014 | Hệ thống phải có audit append-only: đăng nhập/MFA, đổi quyền, grant, SOE/config/driver map, mọi chuyển trạng thái lệnh và kế hoạch, phê duyệt, kill switch, xuất dữ liệu, break-glass, OTA, lệnh điều độ; role ứng dụng chỉ INSERT; hash chain theo tenant; edge giữ audit cục bộ và đồng bộ; trực tuyến ≥ 13 tháng, lưu trữ ≥ 5 năm. | F-SEC-12 | P0 | MVP | — | K §6 #31, R-25 |
| FR-SEC-015 | Hệ thống phải có nhật ký lệnh cho người dùng: vòng đời từng lệnh (tạo → gửi → edge chấp nhận/từ chối kèm lý do → readback → hết hạn/bị thay), ai, khi nào, từ đâu, trước/sau; lọc theo site, người, loại, kết quả. | F-SEC-14 | P0 | MVP | — | H-P13 |
| FR-SEC-016 | PDP phải chặn setpoint P cưỡng bức tới thiết bị `requires_native_fallback = true`; chỉ cho đổi giữa chế độ native an toàn. | F-SEC-15 | P0 | MVP | — | K §6 #17 |
| FR-SEC-017 | Bí mật và khóa phải nằm trong Vault/KMS; khóa ký lệnh không xuất được, hỗ trợ 2 `kid` song song khi xoay; credential cloud hãng mã hóa theo tenant, chỉ control plane đọc credential có quyền ghi; quét secrets trong CI. | F-SEC-16 | P0 | MVP | — | I §3.13 |
| FR-SEC-018 | Edge phải phân vùng OT/IT: 2 NIC, không định tuyến WAN↔OT, chỉ outbound 8883/443 (+ NTP, DNS, OTA), là Modbus master duy nhất, IEC 104 trên conduit riêng; chính sách giữ/chặn kênh cloud riêng của hãng do khách chọn và ghi trong biên bản. | F-SEC-17 | P0 | MVP | — | I §3.6 |
| FR-SEC-019 | Hệ thống phải phân loại dữ liệu D0–D4 và áp quy tắc mã hóa/xuất theo lớp; hosting tại Việt Nam mặc định (chờ kiểm chứng pháp lý); DPIA và quy trình thông báo vi phạm dữ liệu cá nhân là P1. | F-SEC-18 | P0 | MVP | — | K §6 #31; Q-I-04 |
| FR-SEC-020 | Hệ thống phải áp chính sách lưu giữ ở §2 (raw 13 tháng; 5 phút 5 năm; ≥ 1 h vòng đời; audit 13 tháng trực tuyến + ≥ 5 năm; kế hoạch bị thay trước khi chạy: tóm tắt + hash 30 ngày). | F-SEC-19 | P0 | MVP | — | K §6 #31 |
| FR-SEC-021 | Hệ thống phải tính **hồ sơ sẵn sàng Gate M2** theo site và chỉ cho bật M2 khi tất cả đạt: (1) site `active`; (2) `MTR_POC` qua phép thử dấu; (3) SOE đã duyệt và ký; (4) interlock áp dụng được đã cấu hình và test; (5) LOCAL/REMOTE theo FR-SEC-010; (6) test watchdog đạt cho từng thiết bị đích hoặc `requires_native_fallback` đã xử lý; (7) driver ghi `VERIFIED_*`; (8) mọi người có quyền lệnh trên site đã đăng ký MFA; (9) khóa ký lệnh hoạt động; (10) audit append-only hoạt động; (11) Fleet Governor và kill switch hoạt động cho tenant; (12) đồng hồ edge `SYNCED`; (13) đồng ý của chủ tài sản. Điều kiện chuyển sang không đạt khi đang M2 → M2 tạm ngưng (WF-05 E1). | F-SEC-05, F-SEC-06, F-SEC-07, F-SEC-08, F-SEC-10, F-SEC-11, F-INT-28, F-BESS-08 | P0 | MVP | C3·M2 | K §6 #27; GAP (xem §8) |
| FR-SEC-022 | PDP phải áp giới hạn tốc độ: site ≤ 6 lệnh thủ công/phút và ≤ 12 đổi chế độ/giờ; người dùng ≤ 30 lệnh/10 phút; > 5 site/lệnh → C2; > 10% MW đội → C3; edge ≤ 1 setpoint/2 s tới mỗi thiết bị. | F-SEC-03, F-SEC-10 | P0 | MVP | — | I §3.7.6 |
| FR-SEC-023 | Hệ thống nên neo audit: Merkle root mỗi giờ ký KMS ghi vào object storage WORM ≥ 5 năm; xuất audit CSV/JSON kèm bằng chứng hash; công cụ kiểm chuỗi hằng ngày. | F-SEC-13 | P1 | Phase 1 | — | K §3.8; Q-I-13 |
| FR-SEC-024 | Hệ thống nên có hỗ trợ từ xa có kiểm soát: reverse tunnel theo yêu cầu, chủ site cho phép, ≤ 2 h, ghi phiên; break-glass có phê duyệt. | F-SEC-20 | P1 | Phase 1 | — | I §3.5 |
| FR-SEC-025 | Hệ thống nên có OpenTelemetry xuyên cloud → edge với `trace_id`, `command_id` và SLO tách theo dịch vụ (NFR-OBS). | F-SEC-21 | P1 | Phase 1 | — | I §3.14 |
| FR-SEC-026 | Hệ thống nên quản lý client API: OAuth2 client credentials, scope, IP allow-list tùy chọn, hạn ≤ 1 năm, mặc định chỉ đọc, thu hồi. | F-SEC-22 | P1 | Phase 1 | — | I §3.3 |
| FR-SEC-027 | Sản phẩm có thể theo lộ trình chứng nhận ISO 27001 (vận hành cloud) → IEC 62443-4-2 (edge) → đánh giá 62443-3-3; không tuyên bố trước khi có số chứng chỉ, phạm vi, hạn. | F-SEC-23 | P2 | Phase 2 | — | K §6 #34 |
| FR-SEC-028 | Sản phẩm có thể có SKU silo/on-prem (DB/cluster riêng) cho khách lớn. | F-SEC-24 | P2 | Phase 2 | — | K §6 #29 |

**Quy tắc nghiệp vụ**

- **BR-SEC-01** Tenant chỉ được thu hẹp quyền lệnh so với ma trận §3.4, không mở rộng.
- **BR-SEC-02** SoD: người đề xuất SOE ≠ người duyệt; người yêu cầu C3 ≠ người duyệt và khác vai trò; `ORG_ADMIN` không có quyền lệnh mặc định.
- **BR-SEC-03** Hạng thực tế = max(hạng tối thiểu của loại lệnh, hạng do ngữ cảnh theo §2). Không lệnh nào bị hạ hạng.
- **BR-SEC-04** Lệnh từ xa chỉ hợp lệ khi `lifecycle = active` ∧ `control_enabled` ∧ `local_remote = REMOTE` ∧ `kill_switch = OFF` ∧ Gate phù hợp với loại lệnh.
- **BR-SEC-05** Kiểm tra ở ba nơi, lớp sau không tin lớp trước: cloud (quyền, PDP, SOE, Governor) → edge (chữ ký, hạn, `seq`, interlock, SOE đã ký) → thiết bị (giới hạn native, watchdog).
- **BR-SEC-06** Không có "E-stop từ xa", không có API sửa thông số bảo vệ (C4).
- **BR-SEC-07** Không tuyên bố tuân thủ IEC 62443/ISO 27001 khi chưa có chứng chỉ; tuyên bố bảo mật của hãng ghi là "tự tuyên bố".
- **BR-SEC-08** Cam kết hợp đồng: không có "kill" thương mại; khi hết hợp đồng edge chạy chế độ mặc định cục bộ (I AC-07, chuyển 13).
- **BR-SEC-09** Edge mặc định từ chối lệnh không có `expires_at`, quá `max_latency_ms`, `command_id` đã thấy, hoặc `seq` không tăng.

**Tiền/hậu điều kiện.** Tiền: IdP, KMS, Command Signer hoạt động; người dùng có MFA. Hậu: mọi quyết định PDP và chuyển trạng thái lệnh có audit.

**Dữ liệu vào / ra**

| Vào | Ra |
|---|---|
| Danh tính, `auth_time`, binding, grant, trạng thái site/thiết bị, SOE, ngân sách đội, yêu cầu lệnh | Quyết định PDP (cho/từ chối, hạng, lý do), envelope ký, hàng đợi duyệt, trạng thái lệnh, audit, hồ sơ sẵn sàng M2 |

**Phân quyền.** Theo ma trận §3.4. Xem audit: `audit.read`. Kill switch: `killswitch.engage`/`killswitch.release`.

**Lỗi và trường hợp biên**

| Tình huống | Hành vi |
|---|---|
| KMS/Signer không sẵn sàng | Không ký → không phát lệnh mới (fail-safe); edge tiếp tục cục bộ; cảnh báo PO |
| Broker bị chiếm, phát lại lệnh cũ | Edge từ chối `REJECTED_REPLAY` (command_id/seq) hoặc `REJECTED_STALE` (hạn); cảnh báo bảo mật |
| Người duyệt C3 chính là người yêu cầu (hai vai trò) | PDP chặn |
| Lệnh tới 6 site cùng lúc | Nâng C2; nếu > 10% MW tenant → C3 |
| Đồng hồ edge UNSYNCED | IL-06 chặn mọi lệnh có hạn; vòng cục bộ vẫn chạy |
| Chủ tài sản thu hồi đồng ý | `control_enabled` về `false` (thao tác an toàn hóa, không cần duyệt), edge chạy mặc định |

**Tiêu chí chấp nhận**

- **AC-SEC-01** Given site mới tạo, When đọc `control_enabled`, Then giá trị là `false` và mọi lệnh C1+ bị PDP từ chối `CONTROL_DISABLED`.
- **AC-SEC-02** Given yêu cầu C3 lúc 10:00, When không ai duyệt tới 10:15, Then trạng thái `APPROVAL_EXPIRED` và không có envelope nào được ký.
- **AC-SEC-03** Given người A (OPERATOR) yêu cầu C3, When người B có cả OPERATOR và CONTROL_SUPERVISOR duyệt bằng vai trò CONTROL_SUPERVISOR, Then được phép; When chính A duyệt, Then bị chặn.
- **AC-SEC-04** Given lệnh hợp lệ đã thực thi, When kẻ tấn công phát lại cùng envelope sau 2 phút, Then edge trả `REJECTED_REPLAY` và cloud có cảnh báo bảo mật.
- **AC-SEC-05** Given envelope `expires_at` = T, When edge nhận lúc T + 1 s, Then `REJECTED_STALE` và không ghi xuống thiết bị.
- **AC-SEC-06** Given site ở LOCAL (DI), When gửi `SET_ESS_P`, Then `REJECTED_INTERLOCK:IL-01` và UI hiện "Đang điều khiển tại chỗ".
- **AC-SEC-07** Given tenant có 10 MW BESS, When các lệnh trong 5 phút có Σ|ΔP| = 2,1 MW, Then lệnh làm vượt 2,0 MW vào hàng đợi và cần duyệt C3.
- **AC-SEC-08** Given kill switch tenant được bật bởi ORG_ADMIN, When đo, Then mọi edge của tenant đang online báo `REMOTE_CONTROL_SUSPENDED` trong ≤ 60 s và mọi lệnh mới bị từ chối; bật lại cần C3.
- **AC-SEC-09** Given CI chạy bộ test cross-tenant, When một endpoint trả dữ liệu tenant khác, Then build thất bại.
- **AC-SEC-10** Given role DB của ứng dụng, When thực hiện `UPDATE` hoặc `DELETE` trên bảng audit, Then bị từ chối.
- **AC-SEC-11** Given site thiếu điều kiện (6) cho PCS P1, When yêu cầu Gate M2, Then hồ sơ sẵn sàng hiện "Chưa đạt: test watchdog PCS P1" và yêu cầu không gửi được.
- **AC-SEC-12** Given người dùng có quyền ghi chưa đăng ký MFA, When đăng nhập, Then bắt buộc đăng ký MFA trước khi vào trang có thao tác ghi.
- **AC-SEC-13** Given lệnh `SET_ESS_P` đã `ACCEPTED` nhưng chưa readback, When xem UI, Then giá trị hiển thị là "đang chờ xác nhận", không phải giá trị mới.

**Phụ thuộc.** Tất cả module có lệnh; M-ORG (binding, grant); M-INT (chứng chỉ, ký ack); [10 An toàn](10-security-and-reliability.md) (STRIDE, abuse case, SLO, DR); [06 Kiến trúc](06-system-architecture.html) (ADR: "Cloud gửi ý định có hạn", "Lệnh ký tầng ứng dụng", "RLS + silo", "Fleet Governor").

**Bằng chứng và độ tin cậy**

- [FACT] Inverter ở Mỹ/Anh/Pakistan bị vô hiệu hóa từ xa do tranh chấp thương mại 11/2024 (không nêu hãng — I #6). Lý do của FR-SEC-012/013 và BR-SEC-08.
- [FACT] Lithuania cấm truy cập từ xa của công ty Trung Quốc vào hệ > 100 kW — https://www.lrt.lt/en/news-in-english/19/2411602/lithuania-passes-law-to-block-chinese-access-to-solar-and-wind-farm-systems (qua kết quả tìm kiếm).
- [FACT] Huawei SmartLogger: kết nối outbound TLS; Modbus TCP không mã hóa bị tắt mặc định — https://support.huawei.com/enterprise/en/doc/EDOC1100108365/4fbe151e/setting-parameters-for-connecting-to-the-management-system-v300r001c00 (qua kết quả tìm kiếm).
- [FACT] Chứng chỉ IEC 62443 của WinCC OA có hạn tới 2026-02-06 — https://www.winccoa.com/documentation/WinCCOA/3.20/en_US/iec_62443/topics/iec_62443_certification.html; Ampowr ISO 27001/NIS2 là tự tuyên bố — https://ampowr.com/nis2-compliance/ (qua kết quả tìm kiếm).
- [INFERENCE] Modbus/IEC 104 tại site không có xác thực (kiến thức nền về giao thức, K §4) → cô lập mạng và edge là master duy nhất.
- [UNKNOWN] Luật An ninh mạng, NĐ 53/2022, Luật BVDLCN 2025 và thay đổi 2025–2026 (Q-I-04) — điều kiện chặn phát hành 10 và phần lưu trú dữ liệu của 04. [UNKNOWN] RLS trên continuous aggregate của TimescaleDB (Q-I-08).

---

### 5.15 M-ADV — Nâng cao: dự báo, mô phỏng, ML

**Mục đích nghiệp vụ.** Định nghĩa phạm vi nâng cao một cách trung thực (K G-09): dự báo thống kê cần cho bộ sinh lịch MVP; dự báo đa nguồn, what-if và ML có đánh giá ở các pha sau. Quy tắc tên gọi: luật = "Quy tắc"; tối ưu = "tối ưu dựa trên dự báo"; thống kê = "Thống kê"; chỉ mô hình học đã đánh giá trên dữ liệu có nhãn mới gọi là "ML"; mọi số mô phỏng có nhãn "Mô phỏng" (K §6 #33).

**Persona.** P3/P2 (dự báo dùng trong lịch), P5/PO (đánh giá), P4/P1 (what-if bán hàng, P1).

**User story**

| ID | Là… | Tôi muốn… | Để… | FR |
|---|---|---|---|---|
| US-ADV-01 | Operator (P3) | bộ sinh lịch dùng dự báo tải giờ cao điểm đơn giản, dễ giải thích | SOC đích sáng sớm hợp lý mà không phụ thuộc mô hình đen | FR-ADV-001 |
| US-ADV-02 | Chủ C&I (P1) | biết con số nào là mô phỏng/ước tính và phương pháp | không bị hiểu nhầm là số đo | FR-ADV-002 |
| US-ADV-03 | Integrator (P5) (P1) | đánh giá độ chính xác dự báo PV theo nhà cung cấp | chọn nguồn dự báo trước khi bật tầng 3 | FR-ADV-004 |
| US-ADV-04 | Installer (P4) (P1) | mô phỏng thêm BESS với dữ liệu đo của khách | tư vấn kích thước có căn cứ | FR-ADV-006 |

**Yêu cầu chức năng**

| ID | Yêu cầu | F- | Ưu tiên | Phát hành | Hạng·Gate | Căn cứ |
|---|---|---|---|---|---|---|
| FR-ADV-001 | Hệ thống phải có dự báo tải F0 (seasonal naive: cùng giờ tuần trước) và F1 (median theo thứ × giờ × loại ngày trên 4–8 tuần + hiệu chỉnh mức gần nhất), dùng cho SOC đích của luật TOU; nhãn "Thống kê"; lưu `(issue_time, valid_time)`, không ghi đè dự báo cũ; < 7 ngày dữ liệu → profile mặc định có nhãn "dự báo dự phòng". | F-ADV-01 | P0 | MVP | — | K §3.5; F-P18 |
| FR-ADV-002 | Mọi giá trị dự báo, ước tính, mô phỏng trên UI, báo cáo, API phải mang nhãn phương pháp ("Quy tắc", "Thống kê", "tối ưu dựa trên dự báo", "Mô phỏng", "≈ ước tính", "Mô hình học máy (thử nghiệm)") và không được trộn vào số đo. | F-ADV-01…F-ADV-11 | P0 | MVP | — | K §6 #33 |
| FR-ADV-003 | Hệ thống nên có adapter dự báo PV đa nhà cung cấp (NWP/vệ tinh, GTI) → mô hình vật lý DC/AC có clipping và curtail → hiệu chỉnh theo site sau ≥ 30 ngày (loại chu kỳ curtail); P10/P50/P90; intraday 15 phút, day-ahead 48 h. Gói dự báo cá nhân/hobbyist không dùng cho thương mại. | F-ADV-02 | P1 | Phase 1 | — | F-P17 |
| FR-ADV-004 | Hệ thống nên chạy đánh giá dự báo hằng đêm: MAE, nMAE (ghi mẫu số), nRMSE, MBE, WAPE, skill score so seasonal naive, pinball/coverage P10–P90, sai số tại đỉnh; không dùng MAPE cho PV; theo site × tầm × nhà cung cấp. | F-ADV-03 | P1 | Phase 1 | — | F-P19 |
| FR-ADV-005 | Hệ thống nên có dự báo tải F2 (gradient boosting với lịch, ngày lễ VN, Tết âm lịch, ca sản xuất, nhiệt độ, lag); chỉ gọi "ML" sau khi thắng F1 trên tập kiểm tra có phiên bản. | F-ADV-04 | P1 | Phase 1 | — | F-P18 |
| FR-ADV-006 | Hệ thống nên mô phỏng what-if định cỡ: kích thước BESS, biểu giá (TT 16 vs QĐ 963; có/không hai thành phần), chiến lược, `c_deg` → hóa đơn bóng, chu kỳ/năm, kWh PV bị cắt; dữ liệu đo ≥ 1 năm (hoặc ≥ 3 tháng + ghi mùa thiếu); nhãn "Mô phỏng". | F-ADV-06 | P1 | Phase 1 | — | G §3.12 |
| FR-ADV-007 | Hệ thống có thể nhận lịch sản xuất của khách (nhập tay ngày nghỉ/ca hoặc MES/ERP) làm đầu vào dự báo tải F3. | F-ADV-05 | P2 | Phase 2 | — | F-P18 |
| FR-ADV-008 | Hệ thống có thể chạy phát hiện bất thường ML L3 (thử nghiệm) chỉ khi có nhãn từ ticket, đo precision/recall, có phiên bản mô hình; nhãn "Mô hình học máy (thử nghiệm)". | F-ADV-07 | P2 | Phase 2 | — | F-P20 |
| FR-ADV-009 | Hệ thống có thể ước lượng xu hướng suy giảm pin theo thời gian và cách dùng. | F-ADV-08 | P2 | Phase 2 | — | — |
| FR-ADV-010 | Hệ thống có thể giám sát microgrid/backup (đảo/nối lưới, ATS, genset, thời lượng backup), chỉ đọc. | F-ADV-09 | P2 | Phase 2 | — | B PR-B12 |
| FR-ADV-011 | Hệ thống có thể phân tích chất lượng điện từ công tơ PQ có sẵn, chỉ đọc. | F-ADV-10 | P2 | Phase 2 | — | — |
| FR-ADV-012 | Hệ thống có thể đối soát DPPA (đo đếm chu kỳ 30/60 phút, giá thị trường). | F-ADV-11 | P2 | Phase 2 | — | A D-13 |

**Quy tắc nghiệp vụ**

- **BR-ADV-01** Không có tính năng nào mang nhãn "AI" chung chung; F-ADV-15 là ngoài phạm vi vĩnh viễn.
- **BR-ADV-02** Dự báo tải ròng không dự báo trực tiếp; dự báo tải và PV riêng rồi kết hợp.
- **BR-ADV-03** Số mô phỏng không xuất hiện trong báo cáo vận hành R1–R3 trừ khi tách mục và có nhãn.

**Tiền/hậu điều kiện.** Tiền F0/F1: ≥ 7 ngày dữ liệu tải (F1 đầy đủ cần ≥ 4 tuần). Hậu: dự báo lưu hai trục thời gian.

**Dữ liệu vào / ra.** Vào: tải tính toán 15 phút, lịch ngày lễ, (P1) dữ liệu thời tiết. Ra: chuỗi dự báo `(issue_time, valid_time, p10/p50/p90)`, chỉ số đánh giá (P1), kết quả mô phỏng (P1).

**Phân quyền.** Xem: `site.read`. Cấu hình nhà cung cấp dự báo (P1): `SITE_ENGINEER`, `PLATFORM_ADMIN`.

**Lỗi và trường hợp biên.** Ngày lễ/Tết chưa có trong lịch → F1 dùng ngày thường và cảnh báo Thông tin "thiếu lịch ngày lễ năm N"; dữ liệu tải có khoảng trống > 20% trong cửa sổ → loại ngày đó khỏi median.

**Tiêu chí chấp nhận**

- **AC-ADV-01** Given site có 28 ngày dữ liệu tải, When tạo dự báo F1 cho thứ Hai tới, Then mỗi slot 15 phút là median của 4 thứ Hai trước (bỏ ngày lễ), có nhãn "Thống kê" và `issue_time`.
- **AC-ADV-02** Given site có 3 ngày dữ liệu, When bộ sinh lịch chạy, Then dùng profile mặc định của topology và kế hoạch ghi "dự báo dự phòng".
- **AC-ADV-03** Given bất kỳ màn hình nào hiển thị giá trị từ mô phỏng, When kiểm tra UI, Then có nhãn "Mô phỏng"; quét chuỗi i18n không có từ "AI" gắn với tính năng nào.

**Phụ thuộc.** M-OPT (tiêu thụ dự báo), M-HIST (dữ liệu tải), M-ALM (nhãn, P1), [08 Tối ưu](08-energy-optimization.md).

**Bằng chứng và độ tin cậy**

- [FACT] Solcast gói hobbyist PT30M, 10 lượt/ngày — https://docs.solcast.com.au/docs/section/rooftop-sites-hobbyist (qua kết quả tìm kiếm). [INFERENCE] Không dùng cho sản phẩm thương mại.
- [FACT] InfinitePower "AI-powered EMS" chỉ là marketing (không có mô tả kỹ thuật) — https://www.infinitepowerht.com/ai-powered-ems-industrial-energy-storage.html (qua kết quả tìm kiếm). Lý do BR-ADV-01.
- [FACT, V* tự tuyên bố] ABB OPTIMAX 6.4 có "AI" dự báo, chỉ qua báo ngành — https://www.abb.com/global/en/company/innovation/news/optimax-energy-management (qua kết quả tìm kiếm).
- [INFERENCE] Chỉ số đánh giá dự báo và F2 là kiến thức nền chưa kiểm chứng nguồn (F #13). [UNKNOWN] Độ chính xác dự báo ở Việt Nam (Q-F06).

---

### 5.16 Tính năng ngoài phạm vi và bị cấm

Các mục dưới đây có mã trong 03 để không ai thêm lại. 04 không cấp FR "cung cấp", chỉ ràng buộc.

| F- | Tính năng | Loại | Ràng buộc | Lý do |
|---|---|---|---|---|
| F-BESS-19 | Sửa thông số bảo vệ BMS/PCS | CẤM (C4) | FR-BESS-011, BR-SEC-06 | K §6 #14 |
| F-BESS-20 | E-stop từ xa | CẤM (C4) | FR-BESS-011, BR-SEC-06 | K §6 #28 |
| F-PV-14 | Digital twin 3D | Out of scope | Không làm 12–18 tháng | 03; chi phí lớn, không phục vụ thứ tự giá trị VN |
| F-EV-11 | Thanh toán, roaming, CPO | Out of scope | Không xây CSMS thanh toán | B PR-B11 |
| F-OPT-21 | Giao dịch thị trường điện | Out of scope | Không đấu thầu | K §6 #1 |
| F-ADV-12 | Chuyển đảo, black start | Out of scope | Chỉ controller cục bộ có chứng nhận làm | K §6 #1; A §3.7 |
| F-ADV-13 | SCADA/EMS cấp lưới | Out of scope | — | K §6 #1 |
| F-ADV-14 | Nền tảng ESG/carbon | Out of scope | Chỉ xuất dữ liệu (FR-REP-016, FR-REP-017) | K §6 #1 |
| F-ADV-15 | Trợ lý "AI" chưa đánh giá | Out of scope vĩnh viễn | BR-ADV-01 | K §6 #33 |

---

## 6. Yêu cầu phi chức năng

Mọi NFR là `[PROPOSAL]`. Cột "Kiểm chứng" ghi cách nghiệm thu; "PoC" nghĩa là số phải đo trên hệ thống thử trước khi chốt. Site tham chiếu cho tải: 1.000 điểm, 10% ở 5 s và 90% ở 60 s (≈ 35 mẫu/s/site) theo F §3.1.3; site lớn 5.000 điểm (K §3.5 gợi ý cho 06).

### 6.1 NFR-PERF — Hiệu năng

| ID | Yêu cầu | Mục tiêu | Ưu tiên | Kiểm chứng | Căn cứ |
|---|---|---|---|---|---|
| NFR-PERF-001 | Thời gian tải màn hình | L1 danh mục 500 site p95 ≤ 3 s; L2 site p95 ≤ 2 s; console cảnh báo 10.000 dòng có lọc p95 ≤ 2 s | P0 | Test tải với dữ liệu giả lập | Đề xuất của 04, PoC |
| NFR-PERF-002 | Trend explorer | ≤ 8 chuỗi: raw 7 ngày p95 ≤ 3 s; 5 phút 93 ngày p95 ≤ 3 s | P0 | Test tải | F §3.14 giới hạn cửa sổ |
| NFR-PERF-003 | Độ tươi ingest | p95 từ `ts` tới truy vấn được ≤ 60 s cho C2; ≤ 10 s cho C1 khi xem live | P0 | Đo `ts_ingest − ts` | F-P24; I §3.14 |
| NFR-PERF-004 | Thông lượng ingest | Duy trì 35.000 mẫu/s (1.000 site) và chịu 5–10× trong giờ hồi phục backfill không mất dữ liệu; kiến trúc mở được tới 10.000 site | P0 | PoC F-P25 | F §3.1.3 |
| NFR-PERF-005 | Độ trễ giao lệnh | p95 CREATED→RECEIVED ≤ 5 s, p99 ≤ 15 s khi edge online; p95 RECEIVED→APPLIED ≤ 15 s (phụ thuộc thiết bị) | P0 | Đo theo trạng thái lệnh | I §3.14 |
| NFR-PERF-006 | Chu kỳ điều khiển edge | Chu kỳ 1 s; thời gian thực thi một chu kỳ p99 ≤ 200 ms; vượt chu kỳ được đếm và báo | P0 | Đo `cycle_time_ms` trên phần cứng tham chiếu | G §3.3; E §3.12 G13 |
| NFR-PERF-007 | Thông báo cảnh báo | p95 sự kiện → thông báo ≤ 2 phút | P0 | Đo end-to-end | I §3.14 |
| NFR-PERF-008 | Job ngày và báo cáo | Job ngày địa phương xong ≤ 02:00 giờ site; R1 sẵn sàng 99% trước 06:00 giờ site | P0 | Giám sát job | F-P24; I §3.14 |
| NFR-PERF-009 | Tính lại dữ liệu trễ | Dirty bucket được tính lại ≤ 1 h sau khi dữ liệu tới | P0 | Đo | F-P24 |
| NFR-PERF-010 | Bộ sinh lịch | Tầng 2: p95 ≤ 10 s/site; toàn bộ 1.000 site xong ≤ 15 phút sau 05:30 giờ site. Tầng 3 (P1): p95 ≤ 30 s/site; 500 site ≤ 5 phút mỗi chu kỳ | P0 (tầng 2), P1 (tầng 3) | Đo | G NFR-PERF-0xx (mã tạm) |
| NFR-PERF-011 | Xuất dữ liệu | ≤ 100.000 hàng trả ngay p95 ≤ 30 s; lớn hơn chạy job nền | P0 | Đo | F §3.14 |
| NFR-PERF-012 | API đọc công khai | p95 ≤ 1 s cho truy vấn ≤ 10.000 điểm dữ liệu; hạn mức công bố theo tenant | P1 | Test tải | F §3.14; K G-11 |

### 6.2 NFR-REL — Độ tin cậy và an toàn vận hành

| ID | Yêu cầu | Mục tiêu | Ưu tiên | Kiểm chứng | Căn cứ |
|---|---|---|---|---|---|
| NFR-REL-001 | Fail-safe khi mất cloud | Edge giữ vòng cục bộ (zero-export, trần nhập, limit chain), chạy lịch ≥ 48 h, rồi chiến lược mặc định; lệnh tay chạy tới `expires_at` | P0 | Game day chặn broker 4 h trên HIL | I NFR-REL-001 (mã tạm) |
| NFR-REL-002 | Fail-safe khi mất edge↔thiết bị | Thiết bị về mặc định trong `revert_timeout_s` (10–60 s); thiết bị không có watchdog chỉ đổi chế độ native | P0 | FR-INT-018 | I NFR-REL-002 (mã tạm) |
| NFR-REL-003 | Watchdog edge | Watchdog phần cứng reset khi vòng treo > 10 s; khởi động `SAFE_START`, không ghi cho tới khi ≥ 2 chu kỳ đọc hợp lệ và đồng hồ hợp lệ | P0 | Test treo tiến trình | I NFR-REL-003 (mã tạm) |
| NFR-REL-004 | Khả dụng | Điều khiển cục bộ edge ≥ 99,95%; Command API ≥ 99,9% giờ làm việc và ≥ 99,5% tổng; UI/API giám sát ≥ 99,5%; bảo toàn dữ liệu ≥ 99,9% mẫu tới cloud trong ≤ 24 h (cửa sổ 30 ngày) | P0 (mục tiêu), P1 (SLO chính thức, NFR-OBS-005) | Đo SLI | I NFR-REL-004 (mã tạm) |
| NFR-REL-005 | Sao lưu và khôi phục | Cấu hình/SOE/quyền RPO ≤ 5 phút, RTO ≤ 4 h (PITR); bảng lệnh + audit RPO ≤ 1 phút, RTO ≤ 4 h; timeseries nóng RPO ≤ 15 phút, RTO ≤ 8 h (bù bằng backfill edge) | P0 | Diễn tập khôi phục PITR hằng quý | I §3.15 |
| NFR-REL-006 | DR hai trung tâm dữ liệu tại VN | Vùng DR khác tỉnh; failover diễn tập 6 tháng/lần | P1 | Diễn tập | I NFR-REL-005 (mã tạm); K §3.8 phân pha |
| NFR-REL-007 | Phản ứng khi dữ liệu an toàn cũ | Mất `MTR_POC` quá `T_stale_poc` hoặc BMS quá `T_stale_bms` → BESS P = 0/native, PV về giới hạn native trong ≤ 2 chu kỳ điều khiển | P0 | HIL | K §6 #17 |
| NFR-REL-008 | Phát hiện edge offline | OFFLINE sau ≈ 90 s (3 heartbeat 30 s); cảnh báo sau 5 phút | P0 | Test | I §3.9 |
| NFR-REL-009 | Tuân thủ giới hạn xuất | Số sự kiện vi phạm xuất (định nghĩa §2) = 0 trong test commissioning và test hồi quy HIL; vòng edge đưa xuất về giới hạn ≤ 5 s (mục tiêu ≤ 2 s) | P0 | FR-INT-017; HIL | G NFR-REL-0xx (mã tạm) |
| NFR-REL-010 | Lan truyền kill switch | Mọi edge online trong phạm vi nhận `REMOTE_CONTROL_SUSPENDED` ≤ 60 s | P0 | Test | Đề xuất của 04 |
| NFR-REL-011 | Hạn chứng chỉ và khóa | Hết hạn chứng chỉ edge không làm dừng điều khiển cục bộ; cảnh báo trước 14 ngày khi gia hạn lỗi | P0 | Test | I §3.5 |
| NFR-REL-012 | Không thi hành lệnh cũ | Sau khi khôi phục kết nối hoặc khôi phục cloud, không lệnh nào quá `expires_at` được gửi hoặc thực thi; đối soát trạng thái lệnh trong ≤ 60 s sau kết nối lại | P0 | Test | I §3.7.5, §3.15 |

### 6.3 NFR-DATA — Dữ liệu

| ID | Yêu cầu | Mục tiêu | Ưu tiên | Kiểm chứng | Căn cứ |
|---|---|---|---|---|---|
| NFR-DATA-001 | Không mất dữ liệu khi mất mạng | Cứng: ≤ 7 ngày; mục tiêu buffer 30 ngày ở tần suất cloud; 1 s vòng tròn 7 ngày | P0 | Test rút WAN 7 ngày trên HIL | K §6 #18 |
| NFR-DATA-002 | Ingest idempotent, đúng thứ tự logic | Upsert theo `(series_id, ts)`; `seq` + ack; giá trị hiện tại chỉ tiến theo `ts` | P0 | Test gửi trùng/đảo thứ tự | F-P06 |
| NFR-DATA-003 | Quy ước dấu, đơn vị, thời gian, bucket | Theo K §6 #4–#8 cho mọi tầng (edge, DB, API, xuất) | P0 | Kiểm tra schema + test phép thử dấu | K §6 #4–#8 |
| NFR-DATA-004 | Điện năng từ thanh ghi | Bộ đếm int64 Wh; xử lý `R_wrap`, sự kiện thay công tơ; tích phân P chỉ dự phòng có cờ | P0 | AC-HIST-01…03 | K §6 #5 |
| NFR-DATA-005 | Chất lượng bắt buộc | Mọi giá trị lưu và hiển thị mang quality; mọi KPI mang `quality`, `coverage_pct`, `calc_version`; không bao giờ 0 cho thiếu dữ liệu | P0 | Kiểm tra API/UI | K §6 #9, #12 |
| NFR-DATA-006 | Tái lập được | Mọi phép tính có phiên bản (`calc_version`, `attribution_version`, `tariff_version`, input snapshot của plan); chạy lại cùng phiên bản cho cùng kết quả | P0 | Test hồi quy | G §3.9; F-P15 |
| NFR-DATA-007 | Không đổi số âm thầm | Báo cáo đã phát hành bất biến; thay đổi > 0,5% kWh hoặc Pmax → restatement | P0 | AC-REP-03 | F §3.6 |
| NFR-DATA-008 | Lưu giữ | Raw 13 tháng; 5 phút 5 năm; ≥ 1 h vòng đời dự án; snapshot báo cáo ≥ 5 năm | P0 | Kiểm tra job retention | K §6 #31 |
| NFR-DATA-009 | Lưu giữ audit | Audit lệnh, phê duyệt, SOE, kế hoạch đã chạy: trực tuyến ≥ 13 tháng, lưu trữ ≥ 5 năm (neo WORM là P1, FR-SEC-023) | P0 | Kiểm tra | K R-25 |
| NFR-DATA-010 | Lưu trú dữ liệu | Hosting tại Việt Nam là mặc định (INFERENCE, chờ kiểm chứng pháp lý Q-I-04) | P0 | Kiểm tra hạ tầng | K §6 #31 |
| NFR-DATA-011 | Định dạng xuất | CSV UTF-8 BOM, ISO 8601 có offset + UTC, đơn vị trong header, cột quality; XLSX có Metadata | P0 | AC-REP-05 | F-P21 |
| NFR-DATA-012 | Tính khả chuyển | Tenant xuất được toàn bộ dữ liệu của mình (CSV ở MVP, Parquet ở P1) khi kết thúc hợp đồng | P0 (CSV), P1 (Parquet) | Test xuất toàn tenant | I AC-07; BR-SEC-08 |
| NFR-DATA-013 | Điều kiện chọn engine | Không chốt ADR lưu trữ trước khi có kết quả kiểm tra giấy phép TimescaleDB TSL cho SaaS và PoC 1.000 site (tỷ lệ nén, ingest, độ trễ CAGG, DML trên chunk nén) | P0 (cổng quyết định) | ADR ở 06 | K §6 #25; Q-F01 |

### 6.4 NFR-OBS — Quan sát hệ thống

| ID | Yêu cầu | Mục tiêu | Ưu tiên | Căn cứ |
|---|---|---|---|---|
| NFR-OBS-001 | Bộ metric tối thiểu | Ingest lag, mẫu/s, edge online %, độ trễ lệnh theo trạng thái, tỷ lệ `FAILED_*`/`APPLIED_CLAMPED`/`REJECTED_INTERLOCK`, số lệnh/phút theo tenant, Σ\|ΔP\| đội/5 phút, số site chạy fallback, chứng chỉ sắp hết hạn, độ lệch đồng hồ edge | P0 | I §3.14 |
| NFR-OBS-002 | Telemetry sức khỏe edge | `clock_state`, `clock_offset_ms`, `buffer_fill_pct`, `uplink_state`, `cycle_time_ms`, phiên bản firmware/config | P0 | E §3.18 |
| NFR-OBS-003 | Log có cấu trúc | JSON có `trace_id`, `tenant_id`, `command_id`; không ghi dữ liệu cá nhân, token, secret | P0 | I §3.14 |
| NFR-OBS-004 | Truy vết phân tán | OpenTelemetry API → PDP → Signer → broker → edge (`traceparent` trong ack) | P1 | I NFR-OBS-001 (mã tạm) |
| NFR-OBS-005 | SLO và error budget | SLO tách theo dịch vụ (§6.2 NFR-REL-004); hết budget Command API → đóng băng release control plane | P1 | I §3.14 |
| NFR-OBS-006 | Giám sát an ninh | Đăng nhập bất thường, lệnh ngoài giờ, lệnh từ client mới, nhiều `REJECTED_STALE/REPLAY`, đứt hash chain audit (kiểm hằng ngày), thiết bị lạ trên OT LAN | P0 (bốn tín hiệu đầu + hash chain), P1 (thiết bị lạ OT) | I §3.14 |
| NFR-OBS-007 | Chất lượng dữ liệu | Coverage, độ trễ ingest p50/p95, tỷ lệ SUSPECT theo site/thiết bị, cấp cho R8 | P0 | F-P23 |

### 6.5 NFR-SEC — Tóm tắt bảo mật (chi tiết ở [10 An toàn](10-security-and-reliability.md))

Mã NFR-SEC-001…025 **giữ cùng số** với mã tạm của I vì nội dung ánh xạ một–một sau khi áp K; NFR-SEC-026 là mục `NFR-DATA-0xx` của I chuyển sang. Điều này là quyết định đánh số chính thức của 04 (K §6 #38).

| ID | Yêu cầu tóm tắt | Ưu tiên | FR liên quan |
|---|---|---|---|
| NFR-SEC-001 | Cloud và edge không ghi thông số bảo vệ; không có API cho C4 | P0 | FR-BESS-011 |
| NFR-SEC-002 | Tách monitoring plane và control plane; control tắt mặc định theo site | P0 | FR-SEC-005 |
| NFR-SEC-003 | Edge outbound-only, MQTT 5 qua TLS 1.3 (1.2 AEAD), mTLS, chứng chỉ X.509 riêng (khóa trong TPM/secure element; ngoại lệ tạm thời có ghi rủi ro khi phần cứng thiếu TPM — K §3.8), hạn 90 ngày | P0 | FR-INT-002, FR-INT-008 |
| NFR-SEC-004 | Lệnh ký JWS bởi Command Signer (KMS/HSM); edge kiểm chữ ký, `kid`, đích, hạn, `command_id`, `seq`; ack ký bằng khóa edge | P0 | FR-SEC-008 |
| NFR-SEC-005 | OIDC + PKCE; MFA cho mọi vai trò có quyền ghi/admin; step-up ≤ 5 phút cho C2/C3 | P0 | FR-SEC-001, FR-SEC-002 |
| NFR-SEC-006 | RBAC theo cây + PDP cho mọi lệnh; SoD | P0 | FR-SEC-003 |
| NFR-SEC-007 | Cô lập tenant bằng RLS FORCE + test cross-tenant trong CI | P0 | FR-SEC-004 |
| NFR-SEC-008 | Phân hạng C0–C4; hai người duyệt C3; cửa sổ ≤ 15 phút | P0 | FR-SEC-006, FR-SEC-007 |
| NFR-SEC-009 | SOE theo site, version, ký số, đề xuất/duyệt bởi hai người | P0 | FR-BESS-007 |
| NFR-SEC-010 | Interlock IL-01…IL-10 tại edge | P0 | FR-SEC-010 |
| NFR-SEC-011 | Mọi lệnh có `expires_at`; từ chối lệnh không hạn hoặc đến muộn; không gửi lại sau hạn | P0 | FR-SEC-008, FR-SEC-009 |
| NFR-SEC-012 | Fleet Dispatch Governor | P0 | FR-SEC-012 |
| NFR-SEC-013 | Kill switch điều khiển từ xa (tắt C1, bật C3) | P0 | FR-SEC-013 |
| NFR-SEC-014 | LOCAL/REMOTE phần cứng (hoặc native đọc được có biên bản) cho site Gate M2 có BESS; không có E-stop từ xa | P0 | FR-SEC-010 |
| NFR-SEC-015 | Audit append-only + hash chain theo tenant; edge audit cục bộ | P0 (neo WORM P1) | FR-SEC-014, FR-SEC-023 |
| NFR-SEC-016 | Vault/KMS; khóa ký không xuất; credential hãng mã hóa theo tenant; quét secrets CI | P0 | FR-SEC-017 |
| NFR-SEC-017 | Phân vùng OT/IT tại edge | P0 | FR-SEC-018 |
| NFR-SEC-018 | Connector cloud hãng mặc định chỉ đọc; ghi qua cloud hãng là cờ riêng, C2+ | P0 | FR-INT-021, FR-INT-028 |
| NFR-SEC-019 | Phát hiện điều khiển ngoài | P1 | FR-ALM-022 |
| NFR-SEC-020 | OTA edge ký số, A/B, anti-rollback, canary | P0 | FR-INT-012 |
| NFR-SEC-021 | OCPP Security Profile ≥ 2, mục tiêu 3; TxDefaultProfile an toàn | P1 | FR-EV-003 |
| NFR-SEC-022 | Hỗ trợ từ xa bằng reverse tunnel theo yêu cầu ≤ 2 h; không VPN thường trực | P1 | FR-SEC-024 |
| NFR-SEC-023 | Grant installer/vendor có hạn, chủ tài sản cấp/thu hồi, xem lại 90 ngày | P0 | FR-ORG-009 |
| NFR-SEC-024 | Quy trình phát triển an toàn theo tinh thần IEC 62443-4-1 (threat model, SAST/SCA/SBOM, pen-test năm, VDP, SLA vá) | P1 | — |
| NFR-SEC-025 | Lộ trình chứng nhận; không tuyên bố trước khi có chứng chỉ | P2 | FR-SEC-027 |
| NFR-SEC-026 | Phân loại dữ liệu D0–D4; hosting VN mặc định; DPIA và quy trình thông báo vi phạm dữ liệu cá nhân (P1) | P0/P1 | FR-SEC-019 |

---

## 7. Truy vết mã tạm và độ phủ

### 7.1 Độ phủ F- → FR

Mọi tính năng trong 03 có ít nhất một FR hoặc một dòng ràng buộc ở §5.16. Ma trận chi tiết F- ↔ FR- ↔ UI- ↔ T- thuộc [12 Truy vết](12-traceability-matrix.md).

| Module | Số F- trong 03 | Số FR (04) | P0 / P1 / P2 / CẤM | F- chỉ ở §5.16 |
|---|---|---|---|---|
| M-ORG | 16 | 18 | 12 / 5 / 1 / 0 | — |
| M-DASH | 12 | 13 | 8 / 4 / 1 / 0 | — |
| M-MON | 12 | 13 | 10 / 3 / 0 / 0 | — |
| M-HIST | 14 | 17 | 11 / 6 / 0 / 0 | — |
| M-REP | 18 | 19 | 8 / 11 / 0 / 0 | — |
| M-TAR | 11 | 12 | 7 / 4 / 1 / 0 | — |
| M-BESS | 20 | 19 | 10 / 7 / 1 / 1 | — |
| M-PV | 14 | 13 | 5 / 5 / 3 / 0 | F-PV-14 |
| M-GRID | 19 | 19 | 8 / 9 / 2 / 0 | — |
| M-EV | 11 | 10 | 1 / 7 / 2 / 0 | F-EV-11 |
| M-OPT | 21 | 21 | 11 / 8 / 2 / 0 | F-OPT-21 |
| M-ALM | 22 | 22 | 11 / 11 / 0 / 0 | — |
| M-INT | 29 | 30 | 20 / 7 / 3 / 0 | — |
| M-SEC | 24 | 28 | 22 / 4 / 2 / 0 | — |
| M-ADV | 15 | 12 | 2 / 4 / 6 / 0 | F-ADV-12…15 |
| **Tổng** | **258** | **266** | **146 / 95 / 24 / 1** | **7** |

Ghi chú: số FR P0 (146) lớn hơn số F- MVP (130) vì 04 tách một số tính năng MVP thành nhiều FR kiểm thử được (ví dụ FR-ORG-006, FR-DASH-008, FR-HIST-003, FR-HIST-008, FR-REP-008, FR-TAR-007, FR-OPT-002, FR-INT-020, FR-SEC-021, FR-SEC-022, FR-ADV-002) và tạo FR cho mục ngang (quy tắc hiển thị, nhãn). Bảng đếm được kiểm tra lại bằng script khi lưu tài liệu này.

### 7.2 Ánh xạ mã tạm của G (FR-OPT-0xx tạm) sang mã chính thức

| Mã tạm (G §4) | Nội dung | Mã chính thức |
|---|---|---|
| FR-OPT-001 (G) | Bốn tầng; tầng 2/3/4 xuất envelope theo slot | FR-OPT-004, FR-OPT-005, FR-OPT-014, BR-OPT-02 |
| FR-OPT-002 (G) | Arbiter một chỗ, mô hình khoảng | FR-OPT-001, FR-OPT-002 |
| FR-OPT-003 (G) | Vòng tầng 1, `control_owner` | FR-OPT-003, FR-OPT-004, FR-GRID-005 |
| FR-OPT-004 (G) | Bộ sinh lịch luật TOU | FR-OPT-005 |
| FR-OPT-005 (G) | Lịch ≥ 48 h, fallback | FR-OPT-006 |
| FR-OPT-006 (G) | Vòng đời DispatchPlan | FR-OPT-007 |
| FR-OPT-007 (G) | `plan_slot_result` | FR-OPT-010 |
| FR-OPT-008 (G) | Giải thích | FR-OPT-011, FR-OPT-013 |
| FR-OPT-009 (G) | MILP/MPC | FR-OPT-014 |
| FR-OPT-010 (G) | `c_deg` | FR-OPT-015 |
| FR-OPT-011 (G) | Backtest/what-if | FR-OPT-016, FR-ADV-006 |
| FR-OPT-012 (G) | Peak shaving demand | FR-OPT-017 |
| FR-OPT-013 (G) | Ngân sách xuất | FR-OPT-018, FR-GRID-009 |
| FR-OPT-014 (G) | Điện năng PV bị cắt | FR-PV-004 |
| FR-OPT-015 (G) | Ánh xạ chế độ native | FR-BESS-003 |
| FR-OPT-016 (G) | VPP-capable | FR-OPT-021 |
| FR-EV-0xx (G) | EV DLM | FR-EV-006 |
| NFR-PERF-0xx (G) | Thời gian giải MILP | NFR-PERF-010 |
| NFR-REL-0xx (G) | Zero-export ≤ T giây | NFR-REL-009 |

### 7.3 Ánh xạ mã tạm của I

| Mã tạm (I §4) | Mã chính thức |
|---|---|
| NFR-SEC-001…025 | NFR-SEC-001…025 (cùng số, cùng nội dung) |
| NFR-DATA-0xx (phân loại, hosting) | NFR-SEC-026, NFR-DATA-010 |
| NFR-REL-001, 002, 003 | NFR-REL-001, 002, 003 |
| NFR-REL-004 (SLO) | NFR-REL-004, NFR-OBS-005 |
| NFR-REL-005 (RPO/RTO, hai DC) | NFR-REL-005 (sao lưu, P0), NFR-REL-006 (hai DC, P1) |
| NFR-OBS-001 | NFR-OBS-004 |
| FR-SEC-001 (màn phê duyệt) | FR-SEC-007 |
| FR-SEC-002 (trạng thái điều khiển site) | FR-SEC-011 |
| FR-SEC-003 (xuất audit có bằng chứng) | FR-SEC-023 |

### 7.4 Ánh xạ mã tạm khác (chọn lọc)

| Mã tạm | Mã chính thức |
|---|---|
| E PR-E-01 (edge bắt buộc) | FR-INT-001 |
| E PR-E-02 (driver khai báo) | FR-INT-003 |
| E PR-E-03 (arbiter, expiry, readback) | FR-OPT-001, FR-INT-007, FR-SEC-008 |
| E PR-E-04 (MQTT) | FR-INT-008 |
| E PR-E-05 (store-and-forward) | FR-INT-009, NFR-DATA-001 |
| E PR-E-06 (hợp đồng điểm) | FR-HIST-003, NFR-DATA-003 |
| E PR-E-07 (hợp đồng lệnh) | FR-SEC-008, FR-SEC-009 |
| E PR-E-08 (thứ tự driver) | FR-INT-006 |
| E PR-E-09 (IEC 104, hạ P1 theo K R-10) | FR-INT-023, FR-GRID-013 |
| E PR-E-10 (OCPP) | FR-EV-003, FR-EV-004 |
| E PR-E-11 (connector cloud) | FR-MON-003, FR-INT-021 |
| E PR-E-12 (phần cứng edge) | FR-INT-001 |
| E PR-E-13 (đồng bộ thời gian) | FR-INT-010 |
| E PR-E-14 (OTA, không cập nhật firmware hãng) | FR-INT-012 |
| E PR-E-15 (NVM) | BR-INT-04 |
| E PR-E-17 (giao thức P2) | FR-INT-029 |
| E PR-E-18 (không "tương thích mọi") | FR-INT-013 |
| F-P01, F-P02 | FR-HIST-001 |
| F-P03, F-P04 | FR-MON-001, FR-MON-013 |
| F-P05 | FR-INT-009 |
| F-P06 | FR-HIST-002, FR-HIST-006 |
| F-P07 | FR-HIST-004 |
| F-P08, F-P09 | FR-HIST-005 |
| F-P10 | FR-HIST-006 |
| F-P11 | FR-HIST-007 |
| F-P12 | FR-HIST-008 |
| F-P13 | FR-HIST-005, FR-TAR-005 |
| F-P14 | FR-HIST-011, FR-HIST-017 |
| F-P15, F-P16 | FR-REP-001…005, FR-REP-009…012 |
| F-P17 | FR-ADV-003 |
| F-P18 | FR-ADV-001, FR-ADV-005, FR-ADV-007 |
| F-P19 | FR-ADV-004 |
| F-P20 | FR-ALM-002, FR-ALM-003, FR-ALM-021, FR-ADV-008 |
| F-P21 | FR-REP-006, FR-REP-014 |
| F-P22 | FR-REP-005, FR-REP-013 |
| F-P23 | FR-HIST-015, NFR-OBS-007 |
| F-P24 | NFR-PERF-003, NFR-PERF-008, NFR-PERF-009 |
| F-P25 | NFR-DATA-013 |
| H-P01…H-P04 | FR-DASH-001, FR-DASH-003, FR-DASH-004, FR-DASH-005 |
| H-P05 | FR-MON-004 |
| H-P10 | FR-ALM-005, FR-ALM-012 |
| H-P11 | FR-OPT-009, FR-OPT-012 |
| H-P13 | FR-SEC-015 |
| H-P14 | FR-MON-005 |
| C-P01, C-P02 | FR-GRID-002 |
| C-P03, C-P04 | FR-HIST-009, FR-HIST-013, FR-BESS-017 |
| C-P06 | FR-BESS-002 |
| C-P16 | FR-HIST-004 |

---

## 8. Vấn đề gửi agent khác

| Gửi | Nội dung |
|---|---|
| 03 Danh mục | Đã ghi vào [notes/_catalog-gaps.md](notes/_catalog-gaps.md): vai trò `TECHNICIAN` và `PLATFORM_ADMIN` chưa có trong F-ORG-08; "hồ sơ sẵn sàng Gate M2 theo site" (FR-SEC-021) chưa là tính năng riêng; thông tin liên hệ/trực ca trong chi tiết cảnh báo ở MVP (GAP-08); bản ghi đồng ý của chủ tài sản khi bật điều khiển. |
| 05 Domain | Enum mới cần mô hình hóa: `control_gate ∈ {NONE, M1, M2}`; trạng thái lệnh mở rộng (`PENDING_APPROVAL`, `APPROVAL_EXPIRED`, `APPROVAL_REJECTED`, `REJECTED_SIGNATURE`, `REJECTED_REPLAY`, `REJECTED_INTERLOCK:<IL>`); cảnh báo ba trục (hoạt động/xác nhận/xử lý) + `SHELVED`/`SUPPRESSED_BY_PARENT`/`OUT_OF_SERVICE`; ticket `OPEN/IN_PROGRESS/WAITING/RESOLVED/CLOSED/CANCELLED` + danh mục nguyên nhân gốc; `ConsentRecord` (đồng ý bật điều khiển); `M2ReadinessCheck`; chiến lược mặc định của site là cấu hình có version tách khỏi override `SET_ESS_MODE`. |
| 06 Kiến trúc | Cổng NFR-DATA-013 (TSL + PoC) trước ADR lưu trữ; ADR "Cloud gửi ý định có hạn", "Lệnh ký tầng ứng dụng", "RLS + silo", "Fleet Governor"; số NFR-PERF-001/002/006/010 cần PoC; site tham chiếu 1.000/5.000 điểm. |
| 07 Tích hợp | Ngưỡng xác minh map (≤ 2% hoặc ≤ 1 kW công suất, ≤ 1% điện áp) và quy trình phép thử dấu (≥ 5% P định mức hoặc ≥ 5 kW trong ≥ 60 s) ở FR-INT-016/020 là đề xuất của 04 — cần xác nhận với thực địa; chính sách bỏ dữ liệu khi buffer đầy (FR-INT-009 trường hợp biên). |
| 08 Tối ưu | AC-OPT-02/03 là tiêu chí nghiệm thu bộ sinh lịch tầng 2; xác nhận `α`, cách chọn chiến lược mặc định an toàn; tầng 2 chạy 05:30 giờ site và theo sự kiện. |
| 09 UX/UI | Màn mới cần UI-NN: hồ sơ sẵn sàng Gate M2, hàng đợi phê duyệt C3, nhật ký lệnh, ticket (danh sách + chi tiết), checklist commissioning + xác minh map, quản lý grant, kill switch; giao diện vai trò `TECHNICIAN` (chỉ ticket được giao, L4 chỉ đọc). |
| 10 An toàn | Chốt danh sách cảnh báo an toàn không được tạm gác (BR-ALM-03); lan truyền kill switch ≤ 60 s (NFR-REL-010); `T_stale_poc` = 3 s; giờ hành chính cho nâng hạng C2; xác nhận BR-TAR-05 (đổi lịch tối ưu ở site có điều khiển cần `cmd.c2`). |
| 11 Lộ trình | GAP-05 (kéo baseline B0 vào MVP?), GAP-08 (luồng sự cố MVP dừng ở ticket), thứ tự Gate M1 → M2 theo site; 146 FR P0 là phạm vi MVP lớn — cần chia mốc nội bộ. |
| 12 Truy vết | Sinh `T-<FR id>` từ AC-<MODULE>-NN; dùng bảng §7 cho mã tạm. |
| 13 Rủi ro | Câu hỏi mới ở §9.1 (Q-D-01…Q-D-08 là mã tạm của 04). |

---

## 9. Câu hỏi mở, điều kiện phát hành và nguồn

### 9.1 Câu hỏi mở mới của 04 (mã tạm, 13 cấp mã chính thức)

| Mã tạm | Câu hỏi | Ảnh hưởng | FR/NFR |
|---|---|---|---|
| Q-D-01 | Giá trị `T_stale_poc` phù hợp (2–5 s) với công tơ phổ biến và vòng 1 s? | Tần suất chuyển về native không cần thiết vs an toàn | FR-GRID-005, NFR-REL-007 |
| Q-D-02 | Định nghĩa "vi phạm xuất" mà điện lực chấp nhận (dung sai, thời lượng)? | Đếm vi phạm và bằng chứng tuân thủ | FR-GRID-007, FR-REP-007 |
| Q-D-03 | Ngưỡng đạt của test giới hạn xuất (≤ 5 s) có khớp yêu cầu nghiệm thu thực tế? | Biên bản bàn giao | FR-INT-017 |
| Q-D-04 | O&M Việt Nam dùng ticket trong nền tảng hay CMMS riêng; kỹ thuật viên có tài khoản không? | Vai trò `TECHNICIAN`, FR-ALM-016…020 | GAP-01 |
| Q-D-05 | Chủ C&I có chấp nhận đồng ý điện tử để bật điều khiển, hay cần văn bản ký? | FR-SEC-005, WF-04 | — |
| Q-D-06 | `T_offline_alarm_connector` = 30 phút có quá chậm với khách chỉ giám sát? | Cảnh báo kết nối | FR-ALM-004 |
| Q-D-07 | Phạm vi 146 FR P0 có khả thi cho một đội mới; tách MVP nội bộ thành M1 trước, M2 sau? | Lộ trình | 11 |
| Q-D-08 | Chủ tài sản có cần duyệt từng thay đổi SOE hay chỉ nhận thông báo? | SoD, thời gian bật M2 | FR-BESS-007 |

Các câu hỏi đã có trong ghi chú vẫn mở và được tham chiếu trong module: Q-A01 (ngày áp QĐ 963), Q-A03/Q-C04 (ngân sách 50%), Q-A09 (thiết bị chống phát ngược hạ áp), Q-C02 (dữ liệu công tơ EVN), Q-C05/Q-C06 (PF, ramp), Q-E-01 (bảng điểm IEC 104), Q-F01 (giấy phép TSL), Q-F06 (độ chính xác dự báo), Q-F10 (kỳ chốt), Q-G09/Q-G10, Q-H04/Q-H06, Q-I-04 (luật an ninh mạng/dữ liệu), Q-I-07 (watchdog từng hãng), Q-I-08 (RLS trên CAGG), Q-I-13 (WORM tại VN), R-16 (cơ sở giá hai thành phần).

### 9.2 Giả định chính

- [INFERENCE] Người mua chính là installer/O&M/ESCO và phần lớn site C&I được bên thứ ba vận hành (A §3.3) — chưa có số liệu, chưa phỏng vấn (GAP-15).
- [INFERENCE] Đại đa số C&I chưa trả phí công suất; khách thí điểm ≥ 200.000 kWh/tháng có thể đã trả từ 07/2026 (UNKNOWN) (K R-17).
- [PROPOSAL] Mọi số mặc định ở §2 có thể đổi sau PoC và phỏng vấn mà không đổi cấu trúc yêu cầu.

### 9.3 Điều kiện trước khi phát hành 04 ra ngoài đội

Theo K §5 G-13, các kiểm chứng sau phải xong và kết quả phản ánh vào 04:

1. NĐ 58/2025 hợp nhất NĐ 243/2026 (VBHN 52) và TT 29/2026: trần 50%, kỳ tính, mẫu số, quy kết điện xả BESS → FR-REP-015, FR-GRID-009, FR-HIST-009.
2. QĐ 963: ngày áp vào hóa đơn → FR-TAR-003, mặc định lịch hóa đơn.
3. Thí điểm giá hai thành phần: cơ sở tính, block/rolling → FR-TAR-008, FR-OPT-017.
4. QĐ 1570 (IEC 104, kênh truyền) → FR-INT-023, FR-GRID-013.
5. Yêu cầu thiết bị chống phát ngược ở hạ áp → BR-GRID-06, FR-GRID-004/005.
6. Luật An ninh mạng, NĐ 53/2022, Luật BVDLCN 2025 và thay đổi 2025–2026 → FR-SEC-019, NFR-DATA-010, NFR-SEC-026, số tháng lưu giữ audit.
7. Giấy phép TimescaleDB TSL cho SaaS và giấy phép OpenEMS (EPL-2.0/AGPL-3.0 theo module) → NFR-DATA-013, FR-INT-001 (edge runtime).

### 9.4 Nguồn trích trong tài liệu này

Mọi URL dưới đây đã xuất hiện trong ghi chú nghiên cứu hoặc trong 03; tài liệu này không mở trực tiếp URL nào. Nội dung được ghi nhận **qua kết quả tìm kiếm** (snippet). Mã S-xxx do [14 Nguồn](14-source-register.md) cấp.

- https://ampowr.com/ampihealth/
- https://ampowr.com/hoge-duin-hotel-enhances-energy-efficiency-with-ampifarm-peak-shaving/
- https://ampowr.com/nis2-compliance/
- https://apps.apple.com/jp/app/id1529080383
- https://community.openems.io/t/ess-that-can-talk-with-openems-using-modbus-tcp/1029
- https://daibieunhandan.vn/trien-khai-thu-nghiem-gia-ban-le-dien-hai-thanh-phan-tu-thang-10-2025-10390577.html
- https://developer.easee.com/docs/ocpp-smart-charging
- https://deye.com/nl/blog/bms-vs-ems-vs-pcs-bess-components/
- https://digitalpower.huawei.com/en/eu-data-act
- https://docs.chipkin.com/articles/modbus-data-types-byte-order-reference/
- https://docs.solcast.com.au/docs/section/rooftop-sites-hobbyist
- https://forescout.com/press-releases/forescout-vedere-labs-uncovers-severe-systemic-security-risks-in-global-solar-power-infrastructure
- https://github.com/OpenEMS/openems
- https://github.com/OpenEMS/openems/tree/develop/io.openems.edge.controller.ess.balancing
- https://github.com/wlcrs/huawei_solar/blob/main/services.yaml
- https://help-center.meteocontrol.com/en/vcom-cloud/latest/huawei-fusionsolar-api-1
- https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11411391
- https://infosys.beckhoff.com/content/1031/tf6500_tc3_iec60870_5_10x/984040459.html
- https://knowledge-center.solaredge.com/sites/kc/files/feed-in_limitation_application_note.pdf
- https://knowledge-center.solaredge.com/sites/kc/files/se-one-controller-commercial-and-industrial-datasheet-eng.pdf
- https://knowledge-center.solaredge.com/sites/kc/files/se-site-admin-in-solaredge-one-for-c&i-user-guide.pdf
- https://luatminhkhue.vn/quy-dinh-ve-gio-cao-diem-dien-la-luc-may-gio.aspx
- https://marketplace.microsoft.com/en-us/product/saas/869296.microgrid_advisor?tab=overview
- https://openchargealliance.org/?p=159286
- https://openchargealliance.org/ocpp-2-1-is-now-available/
- https://openems.github.io/openems.io/openems/latest/edge/architecture.html
- https://powerfactors.com/why-you-need-an-integrated-apm-platform/
- https://pvpmc.sandia.gov/modeling-guide/5-ac-system-output/pv-performance-metrics/performance-ratio/
- https://solar.huawei.com/admin/asset/v1/pro/view/bb9458d9373d4502912378db3cbc7f2d.pdf
- https://solar.huawei.com/en/products/smart-pv-management-system-installer
- https://solisdepot.com/wp-content/uploads/2023/03/FusionSolar-Smart-PV-Management-System-7.0-After-sales-Technical-Training-Slides.pptx.pdf
- https://sunspec.org/communication-interface-defects-revealed-inul-1741-sb-certified-inverters/
- https://sunspec.org/sunspec-modbus-700-series-der-information-models-are-now-approved/
- https://support.huawei.cn/enterprise/en/doc/EDOC1100515204/2cd10883/setting-string-details
- https://support.huawei.cn/enterprise/en/doc/EDOC1100541798/ea4fbfa/data-repair
- https://support.huawei.com/enterprise/en/doc/EDOC1100108365/4fbe151e/setting-parameters-for-connecting-to-the-management-system-v300r001c00
- https://support.huawei.com/enterprise/en/doc/EDOC1100173984/6d72858a/setting-parameters-over-the-app
- https://support.huawei.com/enterprise/en/doc/EDOC1100331328/90b9638d/viewing-and-managing-report
- https://support.huawei.com/enterprise/en/doc/EDOC1100379184/7a471100/control-apis
- https://tapchicongthuong.vn/thi-diem-ap-dung-gia-dien-hai-thanh-phan-tu-1-1-2026-218800.htm
- https://thoibaonganhang.vn/gia-dien-theo-gio-ai-co-the-huong-loi-187971.html
- https://thuvienphapluat.vn/phap-luat-nha-dat/toan-van-quyet-dinh-1279-qd-bct-2025-quy-dinh-ve-gia-ban-dien-3357.html
- https://thuvienphapluat.vn/van-ban/Tai-nguyen-Moi-truong/Quyet-dinh-963-QD-BCT-2026-khung-gio-cao-diem-thap-diem-cua-he-thong-dien-quoc-gia-703327.aspx
- https://thuvienphapluat.vn/van-ban/Thuong-mai/Thong-tu-05-2025-TT-BCT-he-thong-truyen-tai-dien-phan-phoi-dien-do-dem-dien-nang-642994.aspx
- https://vietnamnet.vn/en/rooftop-solar-saves-billions-of-dong-but-one-bottleneck-remains-2552186.html
- https://vneconomy.vn/automotive/quy-dinh-moi-ve-gia-ban-dien-cho-tram-sac-xe-dien.htm
- https://www.abb.com/global/en/company/innovation/news/optimax-energy-management
- https://www.accure.net/blogs/state-of-charge-soc-estimation-errors-for-lfp-batteries-can-exceed-15
- https://www.advantech.com/vi-vn/resources/industry-focus/quyet-dinh-1570qd-evn-dien-mat-troi-mai-nha-dieu-can-biet
- https://www.bender.de/docs/charge-controller/OCPP/ocpp-smart-charging/
- https://www.emqx.com/en/blog/mqtt-message-expiry-interval
- https://www.infinitepowerht.com/ai-powered-ems-industrial-energy-storage.html
- https://www.infinitepowerht.com/what-is-energy-management-system-ems-and-its-functions.html
- https://www.lrt.lt/en/news-in-english/19/2411602/lithuania-passes-law-to-block-chinese-access-to-solar-and-wind-farm-systems
- https://www.meteocontrol.com/fileadmin/Daten/Dokumente/EN/Produkte/On_Site/blue_Log_XM_XC/Data_sheet/blue_Log_XM_XC_Modbus_Power_Control_license_blue_Log_XC_data_sheet_LastMod-2026-01-27_en.pdf
- https://www.orionbms.com/manuals/utility/bms_param_current_limit_status.html
- https://www.photomate.eu/smartlogger5000b
- https://www.reccessary.com/en/news/vietnam-solar-grid-export-dppa
- https://www.se.com/us/en/faqs/FA239195/
- https://www.sma-america.com/products/energy-management/data-manager-m-10
- https://www.tigerdata.com/docs/about/latest/timescaledb-editions
- https://www.winccoa.com/documentation/WinCCOA/3.20/en_US/iec_62443/topics/iec_62443_certification.html

Nguồn nội bộ: [notes/K-review-round1.md](notes/K-review-round1.md) (ràng buộc), các ghi chú `notes/A-…`, `B-…`, `C-…`, `E-…`, `F-…`, `G-…`, `H-…`, `I-…`; nghiên cứu FusionSolar [../fusionsolar/README.md](../fusionsolar/README.md) và [../fusionsolar/04_ghi_chu_nghien_cuu/](../fusionsolar/04_ghi_chu_nghien_cuu/).

---

*04 · Yêu cầu nghiệp vụ · v1.0 · 2026-10-10 · Agent D. Mọi FR/BR/NFR là đề xuất cho sản phẩm; nhãn FACT/INFERENCE/UNKNOWN mô tả căn cứ. Quyết định ràng buộc: [K-review-round1 §6](notes/K-review-round1.md).*
