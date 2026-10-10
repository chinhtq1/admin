# 08 — Tối ưu năng lượng: chiến lược, tầng điều khiển, lập kế hoạch điều độ

[← Mục lục](index.html) · [00 Tóm tắt](00-executive-summary.html) · [03 Chức năng](03-functional-catalog.html) · [04 Yêu cầu](04-business-requirements.md) · [05 Domain](05-domain-model.html) · [06 Kiến trúc](06-system-architecture.html) · [07 Tích hợp](07-device-integration.md) · [09 UX/UI](09-ux-ui-specification.html) · [10 An toàn](10-security-and-reliability.md) · [11 Lộ trình](11-mvp-and-roadmap.html) · [13 Rủi ro](13-open-questions-and-risks.md) · [14 Nguồn](14-source-register.md)

| Thuộc tính | Giá trị |
|---|---|
| Tài liệu | 08 — Tối ưu năng lượng (Energy Optimization) |
| Phiên bản | 1.0 (bản phát hành nghiên cứu đầu tiên) |
| Ngày | 2026-10-10 |
| Người viết | Agent G (Energy Optimization Specialist) |
| Trạng thái | Bản nháp để duyệt. Ràng buộc bởi quyết định thống nhất của Evidence Judge ([K §6](notes/K-review-round1.md)) |
| Đầu vào | `notes/G-optimization.md`, `notes/C-energy-domain.md`, `notes/E-device-integration.md`, `notes/F-data-analytics.md`, `notes/I-security-reliability.md`, `notes/A-market-boundary.md`, `notes/B-competitors.md`, `notes/K-review-round1.md`, [03](03-functional-catalog.html), [04](04-business-requirements.md), [05](05-domain-model.html) |

**Giới hạn phương pháp (đọc trước).**

- Hạn mức WebSearch chung của lượt chạy (200 truy vấn) **đã hết** trước khi tài liệu này được viết. Truy vấn kiểm chứng duy nhất (giấy phép/binding Java của HiGHS) trả về "web search budget is used up". Tài liệu này **không** có bằng chứng web mới.
- Mọi `[FACT]` ở đây lấy lại từ bằng chứng đã được các agent ghi kèm URL trong `notes/` hoặc trong nghiên cứu FusionSolar trước (`../fusionsolar/`). Hầu hết là "(qua kết quả tìm kiếm)": nội dung được ghi nhận qua snippet, không ai mở toàn văn. Mức tin cậy tối đa vì vậy là "snippet tìm kiếm".
- Giấy phép solver, binding Java, tên controller OpenEMS ngoài `PeakShaving`/`Balancing` là **kiến thức nền chưa kiểm chứng** và được gắn `[INFERENCE]` hoặc `[UNKNOWN]`. Chúng là điều kiện chặn của ADR-OPT (§8.4).
- Các con số ví dụ (đ/kWh, kWh, kW) là phép tính trên tham số giả định, gắn nhãn "Ví dụ số" hoặc "Mô phỏng". Không phải số đo thực tế. Không có số liệu tiết kiệm độc lập nào trong nguồn hiện có.

---

## Mục lục

- [0. Tóm tắt quyết định](#0-tóm-tắt-quyết-định)
- [1. Phạm vi, nguyên tắc và quy ước](#1-phạm-vi-nguyên-tắc-và-quy-ước)
- [2. Kiến trúc điều khiển bốn tầng](#2-kiến-trúc-điều-khiển-bốn-tầng)
- [3. Danh mục chiến lược](#3-danh-mục-chiến-lược)
- [4. Xếp chồng ưu tiên và giải xung đột](#4-xếp-chồng-ưu-tiên-và-giải-xung-đột)
- [5. Tầng 1: bộ luật thời gian thực tại edge (MVP)](#5-tầng-1-bộ-luật-thời-gian-thực-tại-edge-mvp)
- [6. Tầng 2: bộ sinh lịch luật TOU (MVP)](#6-tầng-2-bộ-sinh-lịch-luật-tou-mvp)
- [7. Tầng 3: MILP và MPC (Phase 1)](#7-tầng-3-milp-và-mpc-phase-1)
- [8. Solver cho stack Java/Spring](#8-solver-cho-stack-javaspring)
- [9. Tầng 4: DR, VPP, thị trường (Phase 2 / ngoài phạm vi)](#9-tầng-4-dr-vpp-thị-trường-phase-2--ngoài-phạm-vi)
- [10. An toàn: bộ kiểm tra ràng buộc và vùng vận hành an toàn](#10-an-toàn-bộ-kiểm-tra-ràng-buộc-và-vùng-vận-hành-an-toàn)
- [11. Vòng đời kế hoạch điều độ và thực thi](#11-vòng-đời-kế-hoạch-điều-độ-và-thực-thi)
- [12. Bản ghi giải thích ("vì sao hành động này")](#12-bản-ghi-giải-thích-vì-sao-hành-động-này)
- [13. Phiên bản chiến lược và audit](#13-phiên-bản-chiến-lược-và-audit)
- [14. Mô phỏng, what-if và backtest](#14-mô-phỏng-what-if-và-backtest)
- [15. Đo tiết kiệm: baseline và giới hạn trung thực](#15-đo-tiết-kiệm-baseline-và-giới-hạn-trung-thực)
- [16. Giá trị ở Việt Nam](#16-giá-trị-ở-việt-nam)
- [17. Những gì không được gọi là AI](#17-những-gì-không-được-gọi-là-ai)
- [18. Truy vết tính năng và yêu cầu](#18-truy-vết-tính-năng-và-yêu-cầu)
- [19. Câu hỏi mở và rủi ro](#19-câu-hỏi-mở-và-rủi-ro)
- [20. Vấn đề gửi agent khác](#20-vấn-đề-gửi-agent-khác)
- [21. Nguồn](#21-nguồn)

---

## 0. Tóm tắt quyết định

| # | Quyết định | Nhãn | Chi tiết |
|---|---|---|---|
| D-08-01 | Bốn tầng điều khiển **lồng nhau**, không thay thế nhau. Tầng trên chỉ tạo **giới hạn và mục tiêu theo slot**. Tầng 1 tại edge (hoặc controller native) thực thi trong giới hạn thiết bị. | [PROPOSAL] theo K §6 #14, #23 | §2 |
| D-08-02 | MVP = tầng 1 (luật thời gian thực, edge) + tầng 2 (bộ sinh lịch luật TOU, Java, cloud). Tầng 3 (MILP/MPC 48 h, slot 15 phút) là Phase 1, chỉ bật theo site sau khi backtest thắng luật. Tầng 4 là Phase 2, chỉ "VPP-capable". Giao dịch thị trường và đáp ứng tần số: ngoài phạm vi. | Quyết định K §6 #23 | §2, §9 |
| D-08-03 | Arbiter tại edge dùng mô hình **thu hẹp khoảng cho phép** và thứ tự 12 mức của K. Mức 1–6 cố định. Chỉ thứ tự mức 8–11 cấu hình được theo site. | Quyết định K §6 #16 | §4 |
| D-08-04 | Mọi đầu ra của tầng 2/3/4 đi qua **chuỗi kiểm tra 7 lớp** trước khi chạm thiết bị: validator cloud → PDP → Fleet Governor → kiểm tra nhận lệnh tại edge (chữ ký, hạn, interlock, SOE) → arbiter → limit chain → bảo vệ native. Không lớp phần mềm nào ghi đè BMS/PCS/rơ-le. | [PROPOSAL] theo K §6 #14, #17, #21 | §10 |
| D-08-05 | Tầng 2 và tầng 3 xuất **cùng một** `DispatchPlan` (slot 15 phút, ≥ 48 h, envelope `slot_mode` + mục tiêu + cap). Thay tầng 2 bằng tầng 3 không đổi edge. | [PROPOSAL] | §6, §7, §11 |
| D-08-06 | Chế độ Gate M1: bộ sinh lịch xuất ra **lịch native** của hãng (qua driver `VERIFIED_*`, có readback). Gate M2: xuất `APPLY_SCHEDULE` cho edge của ta. | Quyết định K R-08 | §6.6 |
| D-08-07 | Thứ tự ưu tiên sạc ở Việt Nam: PV sắp bị cắt > lưới thấp điểm > (PV bù tải ≈ lưới giờ bình thường). Không arbitrage Chủ nhật khi chênh lệch < chi phí suy hao. | [INFERENCE] từ QĐ 963 + QĐ 1279 (K đã tính lại số) | §16 |
| D-08-08 | Tiết kiệm chỉ báo bằng **hóa đơn bóng so với baseline phản thực**, cùng `TariffVersion`, luôn nhãn "≈ ước tính". Không quảng cáo %. Đề xuất kéo baseline B0 (không cần mô phỏng) vào MVP để đóng GAP-05. | Quyết định K §6 #34; [PROPOSAL] cho B0 | §15 |
| D-08-09 | Luật là "Quy tắc", MILP là "tối ưu dựa trên dự báo", F0/F1 là "Thống kê", backtest/what-if là "Mô phỏng". Không gì trong tài liệu này là AI/ML. | Quyết định K §6 #33 | §17 |
| D-08-10 | Solver tầng 3: ứng viên chính là OR-Tools Java (MPSolver) với backend LP/MIP mã nguồn mở, hoặc Python sidecar (HiGHS) **chỉ khi ADR-OPT chấp thuận**. Giấy phép mọi ứng viên là UNKNOWN cho tới khi kiểm chứng. | [INFERENCE] + K R-22 | §8 |

---

## 1. Phạm vi, nguyên tắc và quy ước

### 1.1 Phạm vi

Tài liệu đặc tả "não" điều độ của EMS cho site C&I sau công tơ (behind-the-meter), đa site, đa hãng: PV + BESS + lưới + phụ tải + (tùy chọn) sạc EV và máy phát. Gồm: danh mục chiến lược, xếp chồng ưu tiên, bốn tầng điều khiển, đặc tả bộ luật MVP, công thức MILP/MPC, chọn solver, vòng đời kế hoạch, giải thích, phiên bản và audit, mô phỏng/backtest, đo tiết kiệm.

Không gồm:

- Bảo vệ thiết bị (BMS, PCS, rơ-le, E-stop). EMS chỉ đọc giới hạn và trạng thái (K §6 #14).
- Driver giao thức và hợp đồng lệnh chi tiết: [07 Tích hợp](07-device-integration.md).
- Thuật toán dự báo: [05 Domain §12](05-domain-model.html) và `notes/F-data-analytics.md` §3.12. Ở đây chỉ nêu giao diện đầu vào.
- Phân hạng lệnh, PDP, ký lệnh, kill switch: [10 An toàn](10-security-and-reliability.md).

Site **chỉ có PV** là công dân hạng nhất (K §6 #2). Với site này, "tối ưu" chỉ gồm tuân thủ giới hạn xuất, cắt PV có kiểm soát và minh bạch chi phí TOU. Mọi phần về BESS/EV là tùy chọn theo topology.

### 1.2 Nguyên tắc không thương lượng

1. **Cloud không bao giờ nằm trong vòng bảo vệ và không ghi trực tiếp vào thiết bị.** Cloud gửi ý định có hạn (lịch, mục tiêu). Edge arbiter + limit chain quyết định setpoint (K §6 #14). [PROPOSAL]
2. **Không bao giờ ghi đè BMS.** Giới hạn sạc/xả công bố bởi BMS/PCS (CCL/DCL, P cho phép) là trần cứng. Quyết định an toàn dựa vào giới hạn BMS công bố, **không** dựa vào SOC (SOC LFP có thể trôi/nhảy; C #8, nguồn vendor). [PROPOSAL]
3. **Không chạy hai vòng điều khiển trên cùng một biến.** `control_owner ∈ {NATIVE, EDGE}` theo từng chức năng, ưu tiên controller native đã chứng nhận (K §6 #15).
4. **Mọi lệnh có hạn.** Setpoint mặc định 15 phút, tối đa 1 h; lịch tối đa 7 ngày; hết hạn → `REVERT_DEFAULT`; không gửi lại sau hạn (K §6 #21).
5. **Xác định (deterministic) và tái lập được.** Cùng input snapshot + cùng phiên bản engine → cùng kế hoạch. Đây là điều kiện để audit và thanh toán ESCO/PPA. [PROPOSAL]
6. **Giải thích được.** Mọi hành động có mã lý do. Không có hộp đen. [PROPOSAL]
7. **Control mặc định TẮT** theo site. Bật điều khiển = C3 sau commissioning và đồng ý của chủ tài sản (K §6 #26; [03 F-SEC-05](03-functional-catalog.html#f-sec-05)).

### 1.3 Quy ước dữ liệu (theo K §6)

| Chủ đề | Quy ước | Căn cứ |
|---|---|---|
| Dấu P | Lưới + = nhập (mua), BESS + = xả, PV/tải/EV/máy phát ≥ 0. Cân bằng: `P_cons = P_grid + P_pv + P_bess + P_gen`, với `P_cons` gồm tải và EV; khi EV đo riêng (`MTR_EV_i`) thì `P_load = P_cons − P_ev` | K R-01 |
| Dấu Q | Cùng hướng với P của từng điểm đo | K R-02 |
| Đơn vị | Hợp đồng edge (envelope, điểm, setpoint): W, Wh, hậu tố `_w`, `_wh`. Kế hoạch hiển thị, KPI, API: kW, kWh, hậu tố `_kw`, `_kwh`. Trong công thức toán ở tài liệu này dùng kW, kWh, h cho dễ đọc; khi đóng gói envelope nhân 1.000 và làm tròn về số nguyên W | K R-03 |
| Thời gian | Lưu UTC; site có `timezone` IANA; khung TOU, ngày, slot tính theo giờ site; timestamp `ts`, `ts_src`, `ts_ingest` | K R-04 |
| Slot | Slot kế hoạch 15 phút, khóa `slot_start`, khoảng nửa mở `[slot_start, slot_start + 15′)`. Cửa sổ demand 30 phút block thẳng hàng :00/:30 (UNKNOWN block/rolling) | K R-05, §6 #24 |
| Điện năng | Năng lượng thực tế lấy từ thanh ghi công tơ, cặp không âm (nhập/xuất, sạc/xả). Tích phân P chỉ là dự phòng, gắn `ESTIMATED_FROM_POWER` | K §6 #5 |
| Từ vựng chế độ | `site_strategy ∈ {SELF_CONSUMPTION, PEAK_SHAVING, TOU_SCHEDULE, BACKUP_HOLD, IDLE}` (chọn chiến lược chung). `slot_mode ∈ {PV_SURPLUS_CHARGE, GRID_CHARGE_TO_TARGET, PEAK_DISCHARGE, GRID_SETPOINT, HOLD, IDLE}` chỉ trong envelope `APPLY_SCHEDULE`. Không trộn | K R-15 |
| Cấu hình lưới | `export_mode ∈ {ZERO_EXPORT, EXPORT_LIMIT, EXPORT_ENERGY_BUDGET}` (budget là P1), `export_limit_w`, `import_cap_w`, `allow_grid_charge`, `allow_ess_export` | K R-27; [03 F-GRID-03](03-functional-catalog.html#f-grid-03) |
| Mã | Tính năng `F-*` theo [03](03-functional-catalog.html); yêu cầu `FR-*` theo [04](04-business-requirements.md). Mã `FR-OPT-0xx` trong `notes/G-optimization.md` là mã tạm, đã được 04 cấp lại (bảng §18). Mã `D-08-xx`, `RC-*`, `TP-*` trong tài liệu này là mã cục bộ | K §6 #38 |

### 1.4 Thay đổi so với hướng FusionSolar trước

- Hướng cũ là giám sát/O&M PV, **chỉ đọc** chế độ của hãng. Hướng EMS thêm **ghi** chiến lược và lập kế hoạch. [INFERENCE] Lý do: (1) khung cao điểm tối 17h30–22h30 (QĐ 963) khiến PV không còn tự "ăn" giờ cao điểm, giá trị chuyển sang BESS và cần lập lịch; (2) zero-export phổ biến làm PV bị cắt, BESS cứu được phần đó; (3) hãng phần cứng đã có tầng 1 nên giá trị đa hãng nằm ở tầng 2–3, giải thích và đo lường.
- Giữ nguyên: edge-first kiểu OpenEMS, Java/Spring Boot, TimescaleDB/PostgreSQL, MQTT.
- Ngoại lệ có chủ đích: tầng 3 có thể là Python sidecar sau hợp đồng JSON có version, chỉ khi ADR-OPT chấp thuận (K R-22). Tầng 1 và 2 là Java.
- Dấu lưới đổi từ "+ = xuất" (FusionSolar) sang "+ = nhập" (K R-01).

---

## 2. Kiến trúc điều khiển bốn tầng

### 2.1 Sơ đồ phân lớp

```
 CLOUD (phút–giờ, không ở vòng bảo vệ)                        EDGE của ta (100 ms–s)               THIẾT BỊ (ms)
┌──────────────────────────────────────────────┐   MQTT 5   ┌───────────────────────────────┐   Modbus/   ┌─────────────────────┐
│ Tầng 4 (P2): sự kiện DR/VPP → FlexibilityOffer│  mTLS,     │ Nhận lệnh: chữ ký, hạn, seq,   │   CAN/OCPP  │ Controller native   │
│ Tầng 3 (P1): MILP/MPC 48 h × 15′              │  outbound  │ interlock IL-01…10, SOE        │ ──────────► │ (logger, EMS tủ)    │
│ Tầng 2 (MVP): bộ sinh lịch luật TOU (Java)    │ ─────────► │ Lịch ≥ 48 h + chiến lược mặc   │             │ PCS / inverter      │
│   ↓                                            │ ems/v1/    │ định                           │ ◄────────── │ BMS (bảo vệ cell)   │
│ DispatchPlan → Validator → PDP → Governor      │ {edge_id}/ │ Arbiter 12 mức (thu hẹp khoảng)│  readback   │ Rơ-le, E-stop cứng  │
│ → ký JWS → APPLY_SCHEDULE (expires_at ≤ 7 ng)  │ down/cmd   │ Tầng 1: luật 1 s               │             └─────────────────────┘
│                                                │ ◄───────── │ Limit chain (CCL/DCL, SOC, POC)│
│ plan_slot_result, giải thích, M&V              │ up/cmd-ack │ Ghi khi vượt deadband          │
└──────────────────────────────────────────────┘ up/telemetry└───────────────────────────────┘
```

[PROPOSAL] Topic theo K R-12: `ems/v1/{edge_id}/down/cmd` (QoS 1, không retained, Message Expiry = `expires_at − now`) và `ems/v1/{edge_id}/up/cmd-ack`.

### 2.2 Bảng so sánh bốn tầng

| | **Tầng 1: Luật thời gian thực** | **Tầng 2: Lịch luật theo dự báo** | **Tầng 3: Tối ưu toán học (LP/MILP/MPC)** | **Tầng 4: DR / VPP / thị trường** |
|---|---|---|---|---|
| Phát hành | MVP (chạy khi `control_owner = EDGE`, Gate M2); Gate M1 dùng vòng native | MVP | Phase 1, bật theo site sau cổng backtest | Phase 2 "VPP-capable"; bidding ngoài phạm vi |
| Tính năng ([03](03-functional-catalog.html)) | F-OPT-01, 02, 03; F-GRID-05, 06; F-BESS-10 | F-OPT-04, 05, 06, 07; F-ADV-01 | F-OPT-12, 13, 14, 15 | F-OPT-20 (P2); F-OPT-21 (Out of scope) |
| Ví dụ | Balancing về `p_grid_target`, zero-export bằng cắt PV, trần nhập, SOC guard, EV DLM (P1), cửa sổ demand (P1) | "Nạp PV dư 06:00–17:30, nạp lưới thấp điểm tới SOC đích, xả 17:30–22:30, giữ 20% dự phòng" | MILP 192 bước 15 phút, giải lại mỗi 15 phút | Sự kiện giảm tải trong cửa sổ, FlexibilityOffer |
| Input | Đo POC (P, Q), P_pv, P_ess, SOC, CCL/DCL, SOE, lệnh hiệu lực, slot hiện hành | Lịch TOU có phiên bản, dự báo F0/F1 tải, profile PV, SOC, mô hình pin, SOE, cấu hình lưới | Như tầng 2 + dự báo PV/tải 48 h có bất định, `c_deg`, Pmax tháng, phiên EV, giới hạn derate | Sự kiện DR, baseline, kết quả chấp nhận |
| Output | Setpoint mỗi chu kỳ (P_ess, PV limit, EV limit) + mã lý do | `DispatchPlan` (slot_mode + SOC đích + cap) | `DispatchPlan` cùng định dạng + chi phí dự kiến + shadow price | Mục tiêu P_grid trong cửa sổ sự kiện (đi vào arbiter mức 8) |
| Độ trễ cần | Chu kỳ 1 s. Giới hạn xuất: đạt ≤ 5 s ở test commissioning, mục tiêu tham chiếu ≤ 2 s (số Huawei tự công bố cho SmartLogger5000B/SmartMGC5000B) | Phút. Chạy 05:30 giờ site + theo sự kiện | Giải ≤ 30 s p95/site; chu kỳ 15 phút | Phút–giờ |
| Chạy ở đâu | Edge, hoặc controller native | Cloud tạo; edge lưu ≥ 48 h và thực thi | Cloud (Optimization Service); edge chỉ nhận kế hoạch | Cloud nhận sự kiện; edge thực thi |
| Fallback | Mất `MTR_POC` > `T_stale_poc` → BESS P = 0/native, PV về giới hạn native; BMS cũ > `T_stale_bms` → P = 0/native | Lịch hết/hỏng → chiến lược mặc định của site | Infeasible/timeout/vượt guardrail → lịch tầng 2 cho cùng horizon | Hủy cam kết, về tầng 2/3 |
| Giải thích | Mã lý do tức thời + mức arbiter đang thắng | Luật nào, slot nào, tham số nào | Lý do theo slot + chi phí so baseline + shadow price | Sự kiện, mục tiêu, kết quả |
| Nhãn UI | "Quy tắc" | "Quy tắc" | "Tối ưu dựa trên dự báo" | "Sự kiện DR" |
| AI? | Không | Không | Không | Không |

[FACT, Low–Med] Mẫu "cloud lập kế hoạch + edge thực thi" có tài liệu ở Schneider EcoStruxure Microgrid Advisor: MPC trên cloud từ giá, lịch sử, thời tiết, lịch vận hành; lịch mặc định 48 h khi mất kết nối (một nguồn ~2017, 48/72 h mâu thuẫn) — https://www.se.com/us/en/product-range/65896/ ; https://download.schneider-electric.com/doc/998-20080341_US/EcoStruxure%20Microgrid%20Advisor%20Handout.pdf (qua kết quả tìm kiếm; K R-23). Lựa chọn slot 15 phút / horizon 48 h của ta là [PROPOSAL] độc lập.

[FACT] Ampowr Cosmos chạy tiếp chiến lược tại chỗ khi mất mạng ("local backup feature") — https://ampowr.com/hoge-duin-hotel-enhances-energy-efficiency-with-ampifarm-peak-shaving/ (qua kết quả tìm kiếm).

[FACT] OpenEMS Edge chạy chu kỳ ≈ 1 s và mọi điều khiển ESS đi qua "Power Solver", không ghi thẳng kênh Modbus — https://openems.github.io/openems.io/openems/latest/edge/architecture.html ; https://community.openems.io/t/ess-that-can-talk-with-openems-using-modbus-tcp/1029 (qua kết quả tìm kiếm).

### 2.3 Gate M1 và Gate M2 áp vào tầng điều khiển

| | Gate M1 (MVP) | Gate M2 (MVP, bật theo site) |
|---|---|---|
| Ai chạy vòng nhanh | Controller native (`control_owner = NATIVE`) | Edge của ta (`control_owner = EDGE`) cho chức năng native không có |
| Tầng 2 xuất ra | Lịch native của hãng (khung TOU, capacity control, giới hạn xuất) qua driver `VERIFIED_*`, ghi và đọc lại | `APPLY_SCHEDULE` với envelope theo slot |
| Điều kiện | Driver đã kiểm chứng, readback | Bộ an toàn P0: SOE ký số, interlock, `expires_at`, ký lệnh JWS, MFA + step-up, audit append-only, watchdog thiết bị hoặc `requires_native_fallback` đã xử lý, LOCAL/REMOTE, Fleet Governor, kill switch (K §6 #27, #30) |
| Độ trung thực kế hoạch | Thấp hơn: native thường chỉ nhận khung giờ sạc/xả, không nhận SOC đích theo slot (§6.6) | Đầy đủ envelope |

[FACT] Huawei có ba chế độ ESS trong app ("Maximum self-consumption", "Fully fed to grid", "TOU") — https://e-solarshop.ro/wp-content/uploads/2025/07/fusionsolar-app-manual5925.pdf (nghiên cứu FusionSolar). [FACT, Med–High] Thư viện cộng đồng `huawei_solar` có các dịch vụ ghi `set_tou_periods`, `set_capacity_control_periods`, `set_maximum_feed_grid_power`, `set_zero_power_grid_connection`, `forcible_charge/discharge` — https://github.com/wlcrs/huawei_solar/blob/main/services.yaml. Đây là tên dịch vụ của thư viện, không phải tên chính thức của Huawei, và **không** được dùng làm map driver `VERIFIED_*` khi chưa có tài liệu hãng hoặc thử lab (K §4).

---

## 3. Danh mục chiến lược

### 3.1 Bảng tổng hợp

Hạng phát hành lấy từ [03 Chức năng](03-functional-catalog.html). "Mức arbiter" theo §4.

| # | Chiến lược | Mục tiêu ngắn | Tầng | Nơi chạy | Mức arbiter | Giá trị VN 10/2026 | Phát hành | Tính năng |
|---|---|---|---|---|---|---|---|---|
| S1 | Giới hạn xuất / zero-export | P_xuất ≤ `export_limit_w` tại POC | 1 | Native ưu tiên; edge khi native thiếu | 4 | Cao (tuân thủ) | MVP | F-GRID-03, 04, 05, 07 |
| S2 | Cắt PV có kiểm soát | Cắt PV tối thiểu cần thiết | 1 | Native / edge | 4 (là phương tiện của S1) | Cao ở site zero-export | MVP | F-PV-03, 04 |
| S3 | Trần nhập (demand limit vật lý) | P_nhập ≤ `import_cap_w` | 1 | Native / edge | 5 | Cao về vận hành | MVP | F-GRID-06 |
| S4 | Dự phòng backup | SOC ≥ mức dự phòng | 1 (ràng buộc) + 2 | Edge | 6 | Trung bình, nếu PCS/ATS hỗ trợ off-grid | MVP (ràng buộc); Phase 1 (động theo thời tiết) | F-BESS-03, 07; F-OPT-18 |
| S5 | TOU load shifting / arbitrage | Sạc lúc rẻ, xả cao điểm | 2 → 3 | Cloud lập lịch, edge thực thi | 11 | Cao nhất với BESS | MVP (luật); Phase 1 (MILP) | F-OPT-04, 13 |
| S6 | Tối đa tự tiêu thụ (self-consumption) | Giảm nhập bằng PV + BESS | 1 + 2 | Edge (balancing) | 11/12 | Trung bình; kém hơn TOU-aware dưới QĐ 963 | MVP | F-BESS-05; F-OPT-03, 05 |
| S7 | Peak shaving theo demand (giá hai thành phần) | Giảm Pmax 30 phút của kỳ | 1 + 2/3 | Edge thực thi, cloud chọn ngưỡng | 9 | Chỉ với khách thí điểm; cơ sở tính UNKNOWN | Phase 1 | F-OPT-16; F-TAR-07; F-GRID-09, 10 |
| S8 | Điều phối sạc EV (DLM) | Sạc EV trong dư công suất, đủ kWh trước giờ đi | 1 + 2/3 | Edge (CSMS cục bộ hoặc qua CPO) | 10 (cam kết), 5 (giảm khi chạm trần) | Thấp–trung bình hôm nay | Phase 1 | F-EV-05, 06, 07 |
| S9 | Đáp ứng nhu cầu (DR) | Giảm/tăng tải theo sự kiện | 4 + 1 | Cloud nhận, edge thực thi | 8 | UNKNOWN (chưa thấy cơ chế trả tiền cho C&I) | Phase 2 (hook) | F-OPT-20 |
| S10 | Điều độ theo thị trường | Bán năng lượng/linh hoạt | 4 | Cloud + edge | 8 | Không áp dụng cho C&I BTM | Out of scope | F-OPT-21 |
| S11 | Đáp ứng tần số (FCR/FFR) | Thay đổi P theo tần số trong giây | 1 (tại edge/PCS) | PCS/edge | — | Không áp dụng; chức năng tần số–công suất của inverter thuộc grid code (chỉ đọc) | Out of scope | F-OPT-21; F-PV-12 (đọc) |
| S12 | Điều khiển máy phát (genset) | Khởi/dừng genset khi SOC thấp/mất lưới | 1 | Edge / controller genset | 7–11 tùy nguồn | Thấp; đặc thù site | Phase 2 | F-OPT-19 |

[INFERENCE] Ít nhất 8/11 sản phẩm được Agent B xét có tài liệu về peak shaving/giới hạn mua lưới (đếm từ ma trận [02 §7](02-market-and-competitor-analysis.html) / [14](14-source-register.md) EL-046, vốn dựng từ trích đoạn kết quả tìm kiếm; ma trận B·G1). Câu "peak shaving là table stakes" là [INFERENCE] (K §4).

### 3.2 Thẻ chiến lược

Mỗi thẻ có cùng cấu trúc: mục tiêu · input · ràng buộc · tầng thuật toán · nơi chạy · độ trễ · fallback · KPI chứng minh giá trị · áp dụng ở VN · phát hành.

#### S1 — Giới hạn xuất / zero-export

| Mục | Nội dung |
|---|---|
| Mục tiêu | Giữ `P_export = max(0, −P_grid) ≤ export_limit_w` tại `MTR_POC`. `ZERO_EXPORT` là trường hợp `export_limit_w = 0`. |
| Input | `MTR_POC` (P mỗi 1 s, bắt buộc theo K §6 #10), danh sách inverter trong pool điều khiển, giới hạn native, SOC và CCL của BESS, cấu hình lưới. |
| Ràng buộc | Không vi phạm quá `export_violation_tol_w = max(1.000 W; 1% công suất AC PV)` liên tục ≥ 2 s ([04 §2](04-business-requirements.md)). Ưu tiên sạc BESS trước khi cắt PV. Không cho BESS xả ra lưới khi `allow_ess_export = false`. |
| Tầng | 1 (vòng kín). Mức kWh theo kỳ (`EXPORT_ENERGY_BUDGET`) là tầng 2/3, Phase 1. |
| Nơi chạy | Native ưu tiên (`F-GRID-04`, Gate M1). Edge chỉ khi native không có (`F-GRID-05`, Gate M2). |
| Độ trễ | Đạt ≤ 5 s ở test commissioning; mục tiêu ≤ 2 s. [FACT] Huawei tự công bố zero feed-in ≤ 2 s, giới hạn công suất ≤ 5 s cho bộ điều khiển site C&I (SmartLogger5000B/SmartMGC5000B) — https://www.photomate.eu/smartlogger5000b ; https://solar.huawei.com/admin/asset/v1/pro/view/bb9458d9373d4502912378db3cbc7f2d.pdf (qua kết quả tìm kiếm; K R-19). Số tự công bố, không phải đo độc lập. [FACT, Med] Độ trễ = chu kỳ đo + truyền + phản ứng inverter + giảm công suất — https://help.autarco.com/en/hardware/why-am-i-still-exporting-while-i-have-set-my-pv-system-to-zero-export- (qua kết quả tìm kiếm). |
| Fallback | Mất `MTR_POC` > `T_stale_poc` (mặc định 3 s) → PV về giới hạn native an toàn (với site zero-export: giới hạn native đã cấu hình cho zero-export hoặc mức dự phòng do commissioning chốt), BESS P = 0 hoặc native. Interlock IL-04. |
| KPI | Số lần và tổng thời lượng vi phạm xuất theo ngày/tháng (mục tiêu = 0; [03 F-GRID-07](03-functional-catalog.html#f-grid-07)); thời gian đáp ứng ở test bước tải; kWh PV bị cắt do giới hạn xuất (K15). |
| Áp dụng VN | [FACT, Med] Chỉ ~287/28.254 hệ TSXTTT đăng ký bán dư (cuối 07/2026) — https://vietnamnet.vn/en/rooftop-solar-saves-billions-of-dong-but-one-bottleneck-remains-2552186.html (qua kết quả tìm kiếm). [FACT, Med] Hệ **trung áp** không bán dư phải có thiết bị chống phát ngược (theo tóm tắt VBHN 52) — https://storage-vnportal.vnpt.vn/gov-tnn/7350/FileQuanTriTinTuc/VBHN%2052%20Nghi%20dinh%2058%20va%20ND%20243%2030.6.pdf (qua kết quả tìm kiếm). [UNKNOWN] Yêu cầu cho hệ hạ áp và việc điện lực có chấp nhận vòng phần mềm thay rơ-le hay không (Q-A09, GAP-12). Không viết "bắt buộc pháp lý cho mọi site" (K §4). |
| Phát hành | MVP (P0). Ngân sách xuất theo kỳ: Phase 1 (F-GRID-08, F-OPT-17). |

#### S2 — Cắt PV có kiểm soát

| Mục | Nội dung |
|---|---|
| Mục tiêu | Khi BESS đầy/không có/đang ở `P_ch_max` và không được xuất: cắt PV **tối thiểu** cần thiết. Đo được năng lượng bị cắt. |
| Input | `MTR_POC`, P_pv mỗi inverter, P_limit hiện hành, `P_pv_available` (inverter tham chiếu không bị cắt, bức xạ POA, hoặc mô hình). |
| Ràng buộc | Tôn trọng `min_write_interval` của inverter/logger. Ghi vào logger thay vì từng inverter khi có ([03 F-PV-03](03-functional-catalog.html#f-pv-03)). Loại inverter "ghi không tác dụng" khỏi pool và báo `FAILED_NO_EFFECT`. |
| Tầng | 1. |
| Nơi chạy | Native/edge như S1. |
| Độ trễ | Như S1. |
| Fallback | Hết hạn lệnh `SET_PV_LIMIT` → 100% (nếu site cho xuất) hoặc giới hạn native. |
| KPI | `E_curt ≈ Σ max(0, P_pv_available − P_pv_meas)·Δt` (luôn "≈ ước tính"); tỷ lệ cắt/PV khả dụng; phần cắt "cứu được" bởi BESS (§15). |
| Áp dụng VN | [INFERENCE] Ở site zero-export, PV bị cắt là nguồn giá trị lớn nhất cho BESS (§16.2). PR thô bị thấp giả tạo, cần PR loại trừ curtail (F-PV-06, Phase 1). |
| Phát hành | MVP (F-PV-03 C1·M1; F-PV-04 đọc). |

#### S3 — Trần nhập (demand limit vật lý)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Giữ `P_import ≤ import_cap_w` (định mức MBA, công suất hợp đồng, cầu dao) để tránh nhảy MCCB/quá tải MBA. Độc lập với biểu giá. |
| Input | `MTR_POC`, `import_cap_w`, DCL/P_dis_max của BESS, SOC, giới hạn EV hiện hành, danh sách phụ tải cắt được (P2). |
| Ràng buộc | Thứ tự phương tiện: (1) BESS xả thêm trong DCL; (2) giảm EV về `I_min` rồi tạm dừng phiên ưu tiên thấp (P1); (3) cắt phụ tải không quan trọng (P2, F-GRID-18); (4) cảnh báo khi vượt quá `T_import_alarm = 30 s`. Được xả xuống dưới dự phòng tới `S_res_hard` nếu `allow_reserve_dip_for_import_cap = true` (§4.3). |
| Tầng | 1. |
| Nơi chạy | Native trước, edge khi cần. |
| Độ trễ | Vài giây. Mục tiêu tham chiếu ≤ 5 s (số Huawei tự công bố cho giới hạn công suất). |
| Fallback | Mất `MTR_POC` → không thể thực thi bằng BESS; BESS về P = 0/native, cảnh báo Cao. Bảo vệ quá dòng vẫn do CB/rơ-le. |
| KPI | Số lần và thời lượng vượt trần; năng lượng BESS đã xả cho trần nhập; số lần xuống dưới dự phòng. |
| Áp dụng VN | [INFERENCE] Giá trị vận hành (tránh dừng sản xuất, hoãn nâng cấp MBA), có ở mọi site có BESS. [FACT] Ampowr peak shaving theo trần lưới, ví dụ 95 kW — https://ampowr.com/hoge-duin-hotel-enhances-energy-efficiency-with-ampifarm-peak-shaving/ (qua kết quả tìm kiếm). |
| Phát hành | MVP (F-GRID-06, C2·M1). |

#### S4 — Dự phòng backup

| Mục | Nội dung |
|---|---|
| Mục tiêu | Giữ `SOC ≥ SOC_floor_eff(t) = max(SOC_min_eff, SOC_backup_reserve(t))` để cấp tải ưu tiên khi mất lưới. |
| Input | Mô hình pin (`e_usable_current`), tải ưu tiên (kW), thời gian cần cấp (h), khả năng off-grid của PCS/ATS, cảnh báo thời tiết (Phase 1). |
| Ràng buộc | Mức khách cấu hình không thấp hơn giới hạn hãng (F-BESS-03). Tăng dự phòng = C1, giảm = C2 có lý do (F-BESS-07). Gợi ý tính: `SOC_backup_reserve ≈ SOC_min_eff + P_priority·T_backup/(η_d·E_usable)`. |
| Tầng | 1 (ràng buộc mọi chu kỳ) + 2 (đổi theo lịch/mùa). |
| Nơi chạy | Edge. |
| Độ trễ | Không cần nhanh (ràng buộc năng lượng). |
| Fallback | Dữ liệu SOC cũ → BMS stale → P = 0 (mức 3). |
| KPI | Thời gian SOC < dự phòng; số lần xuống dưới dự phòng vì trần nhập; thời lượng backup ước tính. |
| Áp dụng VN | Có ý nghĩa chỉ khi PCS/ATS hỗ trợ off-grid. [FACT] Siemens SICAM MGC quản lý SOC, giữ năng lượng tối thiểu (B·L21) — https://assets.new.siemens.com/siemens/assets/api/uuid:4b32eeee-ee7c-423e-94f1-ae6a4257a689/MicrogridControlBrochure.pdf (qua kết quả tìm kiếm). |
| Phát hành | MVP cho ràng buộc tĩnh; Phase 1 cho dự phòng động theo cảnh báo thời tiết (F-OPT-18). |

#### S5 — TOU load shifting / arbitrage

| Mục | Nội dung |
|---|---|
| Mục tiêu | Tối thiểu chi phí năng lượng theo TOU: nạp năng lượng rẻ (PV dư, lưới thấp điểm), xả vào cao điểm. |
| Input | Lịch TOU + bảng giá có phiên bản (F-TAR-01, 02, 03), dự báo tải F0/F1 (F-ADV-01), profile/dự báo PV, SOC, mô hình pin, `allow_grid_charge`, `c_deg` (Phase 1). |
| Ràng buộc | Mọi giới hạn mức 1–6. Lịch TOU đọc từ dữ liệu, không hard-code (K §3.6). Chủ nhật không arbitrage khi chênh lệch < `c_deg`. `cycles_per_day_max` của SOE. |
| Tầng | 2 (luật, MVP) → 3 (MILP, Phase 1). |
| Nơi chạy | Cloud tạo kế hoạch; edge thực thi bằng balancing (tầng 1) trong envelope. |
| Độ trễ | Lịch 48 h, chạy 05:30 + theo sự kiện (tầng 2); 15 phút (tầng 3). |
| Fallback | Lịch hết → chiến lược mặc định; tầng 3 lỗi → tầng 2. |
| KPI | Chi phí thực so với kế hoạch và so với baseline B1 (cùng `TariffVersion`); kWh xả trong cao điểm / kWh xả; % slot `APPLIED`; lệch SOC cuối thấp điểm so với đích. |
| Áp dụng VN | [FACT] QĐ 963/QĐ-BCT: cao điểm 17h30–22h30 T2–T7, thấp điểm 0h–6h, Chủ nhật không cao điểm — https://thuvienphapluat.vn/van-ban/Tai-nguyen-Moi-truong/Quyet-dinh-963-QD-BCT-2026-khung-gio-cao-diem-thap-diem-cua-he-thong-dien-quoc-gia-703327.aspx ; https://tuoitre.vn/bo-cong-thuong-chinh-thuc-thay-doi-khung-gio-tinh-gia-dien-buoi-toi-la-gio-cao-diem-2026042410430101.htm (qua kết quả tìm kiếm). [UNKNOWN] Ngày áp vào hóa đơn (Q-A01) → hai lịch song song (F-TAR-03). [FACT, Med–High] QĐ 1279: giá sản xuất 22–<110 kV thấp điểm 1.190, bình thường 1.833, cao điểm 3.398 đ/kWh — https://thuvienphapluat.vn/phap-luat-nha-dat/toan-van-quyet-dinh-1279-qd-bct-2025-quy-dinh-ve-gia-ban-dien-3357.html (qua kết quả tìm kiếm). Giá trị chi tiết ở §16. |
| Phát hành | MVP (F-OPT-04); Phase 1 (F-OPT-13). |

#### S6 — Tối đa tự tiêu thụ (self-consumption)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Giảm nhập lưới bằng PV và BESS: BESS bám `P_grid → p_grid_target` (thường 0 hoặc +margin). |
| Input | `MTR_POC`, SOC, CCL/DCL. |
| Ràng buộc | Dự phòng; `SOC_ceiling_eff` có "space reserve" để còn chỗ hấp thụ PV dư buổi trưa ở site zero-export. [FACT] Huawei EMMA dự báo dư PV và giữ "SOC space reserve" — https://solar.huawei.com/en/products/EMMA (B L38). |
| Tầng | 1 (balancing) + 2 (khi nào được xả). |
| Nơi chạy | Edge / native. |
| Độ trễ | Chu kỳ 1 s. |
| Fallback | Là thành phần của chiến lược mặc định an toàn (mức 12): self-consumption có giới hạn + zero-export + giữ dự phòng. |
| KPI | Tỷ lệ tự tiêu thụ PV (K10), tỷ lệ tự cung (K11) với `attribution_version`. |
| Áp dụng VN | [INFERENCE] Dưới QĐ 963, self-consumption thuần (xả ngay khi tải > PV) **kém hơn** TOU-aware: xả giờ bình thường (1.833) lãng phí năng lượng có thể bán vào cao điểm (3.398). Tầng 2 vì vậy chặn xả cho tải giờ bình thường trừ khi trần nhập/peak cần (§6). Self-consumption thuần chỉ hợp lý ở Chủ nhật hoặc site không có biểu giá TOU. |
| Phát hành | MVP (`site_strategy = SELF_CONSUMPTION`, F-BESS-05). |

#### S7 — Peak shaving theo demand (giá hai thành phần)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Giảm Pmax = công suất trung bình lớn nhất của cửa sổ 30 phút trong kỳ, khi biểu giá có thành phần công suất. |
| Input | `MTR_POC` đồng bộ cửa sổ với công tơ thanh toán, `E_so_far` trong cửa sổ, `P_target`, `P̂_month` (Pmax đã đạt), dự báo tải, SOC. |
| Ràng buộc | `P_target_eff = max(P_target_plan, P̂_month)`: khi Pmax tháng đã bị đặt cao, cố giữ thấp hơn chỉ tốn pin mà không giảm hóa đơn. Kẹp `T_w − t ≥ 60 s` ở cuối cửa sổ. |
| Tầng | 1 (thực thi cửa sổ) + 2/3 (chọn `P_target`, giữ SOC trước giờ đỉnh dự kiến). |
| Nơi chạy | Edge (hoặc native "capacity control" khi có). |
| Độ trễ | Vài giây. |
| Fallback | BESS lỗi/mất mạng giữa tháng làm mất lợi ích cả tháng → cảnh báo sớm khi dự báo cuối cửa sổ > `P_target_eff`. |
| KPI | Pmax thực tế so với mục tiêu và so với B1 (Pmax không BESS); kWh xả cho peak; số cửa sổ UNCERTAIN (dữ liệu thiếu). |
| Áp dụng VN | [FACT, Med] Thí điểm giá hai thành phần cho khách sản xuất ≥ 200.000 kWh/tháng — https://tapchicongthuong.vn/thi-diem-ap-dung-gia-dien-hai-thanh-phan-tu-1-1-2026-218800.htm (qua kết quả tìm kiếm). [FACT, Med] "Khoảng thời gian tích phân hiện nay đang là 30 phút" — https://daibieunhandan.vn/trien-khai-thu-nghiem-gia-ban-le-dien-hai-thanh-phan-tu-thang-10-2025-10390577.html (qua kết quả tìm kiếm). [UNKNOWN] Cơ sở tính (Pmax đo hay công suất đăng ký), block hay rolling, áp mọi giờ hay theo khung (K R-16). [INFERENCE] Đại đa số C&I chưa trả phí công suất; khách thí điểm có thể đã trả từ 07/2026 (UNKNOWN, K R-17). Hai kịch bản ở §16.3. |
| Phát hành | Phase 1 (F-OPT-16, F-TAR-07). |

#### S8 — Điều phối sạc EV (DLM)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Sạc EV trong dư công suất tại POC; đủ năng lượng trước giờ đi; tùy chọn chỉ sạc bằng PV dư. |
| Input | `MTR_POC`, `MTR_EV_i`, phiên OCPP (đến/đi, kWh cần, ưu tiên), trần nhóm trụ, `I_min` (mặc định 6 A). |
| Ràng buộc | Mỗi phiên đang sạc nhận ≥ `I_min` hoặc 0 (tạm dừng). Cập nhật ≤ 1 lần/10–30 s mỗi trụ. Dùng `ChargePointMaxProfile`/`TxProfile` có `validTo`. Quirk hãng trong driver. [FACT] OCPP 1.6: ba loại profile, stackLevel cao thắng, giới hạn hiệu lực là nhỏ nhất; Easee: `TxDefaultProfile` không tự xóa, có thể đè `TxProfile` — https://www.bender.de/docs/charge-controller/OCPP/ocpp-smart-charging/ ; https://developer.easee.com/docs/ocpp-smart-charging (qua kết quả tìm kiếm). |
| Tầng | 1 (phân bổ) + 2/3 (lịch theo giờ đi và giá). |
| Nơi chạy | Edge (CSMS tối giản, F-EV-03) hoặc qua API CPO (F-EV-04). |
| Độ trễ | 10–30 s. [INFERENCE] EV phản ứng chậm hơn vòng 1 s; trần nhập tức thời phải do BESS gánh, EV chỉ giảm tải bền vững. |
| Fallback | Hết hạn profile → `TxDefaultProfile` an toàn (giới hạn trạm cấu hình). Mất POC → EV về giới hạn an toàn tĩnh. |
| KPI | % phiên đủ kWh trước giờ đi; kWh EV từ PV dư; số lần EV bị giảm do trần nhập; chi phí EV theo biểu giá EV. |
| Áp dụng VN | [FACT, Med] Trạm sạc kinh doanh có biểu giá và công tơ riêng (QĐ 14/2025, TT 60/2025) — https://vneconomy.vn/automotive/quy-dinh-moi-ve-gia-ban-dien-cho-tram-sac-xe-dien.htm (qua kết quả tìm kiếm). Do đó tối ưu phải hỗ trợ nhiều biểu giá trong một site (§7.6). |
| Phát hành | Phase 1 (F-EV-05, 06, 07). MVP chỉ đo qua công tơ (F-EV-01). |

#### S9 — Đáp ứng nhu cầu (DR)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Giảm (hoặc tăng) công suất nhập trong cửa sổ sự kiện theo yêu cầu bên ngoài. |
| Input | Sự kiện (bắt đầu, kết thúc, mục tiêu kW hoặc ΔkW so baseline), baseline sự kiện, FlexibilityOffer. |
| Ràng buộc | Mức 8 của arbiter: dưới mọi giới hạn an toàn/lưới/dự phòng và dưới lệnh tay. |
| Tầng | 4 (nhận, chấp nhận) + 1 (thực thi). |
| Nơi chạy | Cloud + edge. |
| Độ trễ | Phút. |
| Fallback | Mất kênh sự kiện → hủy theo quy tắc chương trình; về tầng 2/3. |
| KPI | kW giảm thực tế so baseline sự kiện; tỷ lệ sự kiện đạt. |
| Áp dụng VN | [UNKNOWN] Chưa có bằng chứng trong nguồn đã có về chương trình DR trả tiền cho C&I (Q-A06, Q-G08). [FACT, Med–High] OpenADR 3.0 dùng REST/JSON — https://www.openadr.org/assets/OpenADR%20Webinar%20Nov%202023%20-%20From%202.0%20to%203.0.pdf (qua kết quả tìm kiếm). |
| Phát hành | Phase 2, chỉ hook (F-OPT-20). |

#### S10 — Điều độ theo thị trường

| Mục | Nội dung |
|---|---|
| Mục tiêu | Đấu thầu năng lượng/linh hoạt (day-ahead, intraday, imbalance, dịch vụ phụ trợ). |
| Input | Giá thị trường, kết quả đấu thầu, đo đếm chuẩn TSO. |
| Tầng · nơi chạy | 4; cloud (bid) + edge (đáp ứng). |
| Áp dụng VN | [FACT] Ampowr bid đồng thời Day-Ahead + imbalance + aFRR ở Hà Lan — https://ampowr.com/case-study-gebroeders-van-pinxteren/ (qua kết quả tìm kiếm). [FACT, Med] TT 62/2025 có khung giá hai thành phần cho BESS độc lập ≥ 10 MW, ≥ 110 kV (FTM) — https://arcusenergyasia.com/resources/regulations/circular-62 (qua kết quả tìm kiếm). [INFERENCE] Không có kênh thị trường cho C&I BTM ở VN; DPPA ảo dùng giá thị trường 30 phút là động lực **dữ liệu đối soát** (F-ADV-11), chưa phải điều độ. |
| Phát hành | Out of scope 12–18 tháng (F-OPT-21; K §6 #1). |

#### S11 — Đáp ứng tần số (FCR/FFR)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Thay đổi P theo độ lệch tần số trong giây, theo yêu cầu TSO. |
| Tầng · nơi chạy | Tầng 1, bắt buộc tại PCS/edge (cloud không đủ nhanh). |
| Ràng buộc | Cần tiền định chất (prequalification), đo đếm và chứng nhận của TSO. [INFERENCE] Đây là sản phẩm riêng, không phải tính năng phụ. |
| Phân biệt | Đặc tính tần số–công suất và ride-through của inverter/PCS là **chức năng grid code của thiết bị** (bảo vệ), EMS chỉ đọc và đối chiếu (F-PV-12), không sửa (F-BESS-19 cấm, C4). |
| Áp dụng VN | Không áp dụng cho C&I BTM. |
| Phát hành | Out of scope (thuộc F-OPT-21). |

#### S12 — Điều khiển máy phát

| Mục | Nội dung |
|---|---|
| Mục tiêu | Khởi/dừng genset khi SOC thấp hoặc mất lưới. |
| Tầng · nơi chạy | Tầng 1 tại edge qua DO/controller genset; C2·M2. |
| Ràng buộc | Không lịch tự động khởi động genset khi controller genset/ATS đã tự làm; tôn trọng thời gian chạy tối thiểu của genset. |
| Áp dụng VN | [FACT] Ampowr generator steering — https://ampowr.com/battery-energy-storage-systems/battery-energy-storage-system-generator-steering/ (qua kết quả tìm kiếm). |
| Phát hành | Phase 2 (F-OPT-19). |

---

## 4. Xếp chồng ưu tiên và giải xung đột

### 4.1 Mô hình "thu hẹp khoảng cho phép"

[PROPOSAL, K R-07] Mức trên **không cộng lệnh** với mức dưới. Mỗi mức chỉ được thu hẹp khoảng cho phép của mỗi biến điều khiển. Mức dưới chọn một điểm trong khoảng còn lại.

Biến điều khiển của site: `P_ess` (W, + = xả), `P_pv_limit` (W hoặc %), `P_ev_limit[i]` (W hoặc A), `P_load_shed` (P2), `genset_run` (P2).

```
khoảng[0] = [−P_ch_max_BMS_PCS, +P_dis_max_BMS_PCS]        # mức 1: bảo vệ native, chỉ đọc
for mức L = 2 … 12 (thứ tự cố định 2…7, cấu hình 8…11, 12 cuối):
    ràng_buộc_L = ràng buộc do mức L tạo trong chu kỳ này (có thể rỗng)
    khoảng_mới  = khoảng[L−1] ∩ ràng_buộc_L
    if khoảng_mới = ∅:                 # mức L đòi điều không thể trong khoảng của mức trên
        giữ khoảng[L−1]; chọn điểm gần ràng_buộc_L nhất; ghi mã CONFLICT_UNSATISFIED(L)
    else:
        khoảng[L] = khoảng_mới
    ghi mức thắng = L nếu L làm khoảng hẹp đi
P_ess_cmd = điểm do mức thấp nhất có mục tiêu chọn (thường: lịch kinh tế hoặc mặc định)
           sau đó qua limit chain (§5.3) và ramp
```

[FACT] OpenEMS dùng "Power Solver" làm điểm hội tụ mọi yêu cầu ESS (nguồn diễn đàn, B·L43) — https://community.openems.io/t/ess-that-can-talk-with-openems-using-modbus-tcp/1029 (qua kết quả tìm kiếm). Đây là tham chiếu cho thiết kế, không phải bằng chứng rằng mô hình của ta giống hệt.

### 4.2 Thứ tự 12 mức

| Mức | Lớp | Ai thực thi | Ràng buộc tạo ra | Cấu hình được? | Mã lý do khi thắng |
|---|---|---|---|---|---|
| 1 | Bảo vệ native (BMS/PCS/rơ-le/E-stop cứng) | Thiết bị | CCL/DCL, contactor; EMS chỉ đọc và kẹp theo | Không (ngoài phần mềm) | `CLAMPED_BY_BMS`, `CLAMPED_BY_PCS` |
| 2 | Interlock tại chỗ (LOCAL/REMOTE, E-stop, PCCC, IL-01…IL-10) | Edge | Khoảng = {0} hoặc chế độ native; từ chối lệnh từ xa | Không | `INTERLOCK_ACTIVE:IL-xx` |
| 3 | Giám sát an toàn edge (BMS/POC cũ, lệnh hết hạn, SOE, limit chain) | Edge | P = 0 hoặc native; kẹp theo SOE | Không | `SAFE_STATE_STALE_BMS`, `SAFE_STATE_STALE_POC`, `CLAMPED_BY_SOE`, `COMMAND_EXPIRED` |
| 4 | Tuân thủ lưới (giới hạn xuất, lệnh `GRID_OPERATOR`, chặn phát ngược) | Native hoặc edge | `P_export ≤ export_limit`; PV limit | Không | `EXPORT_LIMIT_ACTIVE`, `OVERRIDDEN_BY_GRID_OPERATOR`, `PV_CURTAILED_EXPORT_LIMIT`, `CHARGE_FORCED_BY_EXPORT_LIMIT` |
| 5 | Trần nhập vật lý | Native hoặc edge | `P_import ≤ import_cap` | Không | `IMPORT_CAP_ACTIVE`, `EV_THROTTLED_IMPORT_CAP` |
| 6 | Dự phòng backup | Edge | `SOC ≥ SOC_floor_eff` (ngoại lệ §4.3) | Không (vị trí); giá trị cấu hình | `HOLD_BACKUP_RESERVE`, `RESERVE_DIPPED_FOR_IMPORT_CAP` |
| 7 | Lệnh tay của operator (có hạn, trong SOE) | Edge | Điểm đặt trong khoảng của 1–6 | Không | `MANUAL_OVERRIDE`, `MANUAL_CLAMPED_BY_GRID_LIMIT` |
| 8 | DR/VPP (P2) | Edge | Mục tiêu P_grid trong cửa sổ sự kiện | Thứ tự 8–11 cấu hình theo site | `DR_EVENT_ACTIVE` |
| 9 | Peak shaving theo demand (P1) | Edge | `P_grid ≤ P_allow_rest` | ″ | `DISCHARGE_PEAK_SHAVING`, `PEAK_SHAVING_OVERRIDE` |
| 10 | Cam kết EV (P1) | Edge + lịch | Năng lượng tối thiểu theo phiên | ″ | `EV_COMMITMENT` |
| 11 | Lịch kinh tế (luật tầng 2 / tối ưu tầng 3) | Cloud tạo → edge | Điểm đặt theo slot envelope | ″ | `CHARGE_PV_SURPLUS`, `CHARGE_GRID_OFFPEAK_TO_TARGET`, `DISCHARGE_PEAK_TOU`, `HOLD_FOR_PEAK`… |
| 12 | Chiến lược mặc định của site | Edge | Self-consumption có giới hạn + zero-export + dự phòng | Giá trị cấu hình | `DEFAULT_STRATEGY`, `FALLBACK_SCHEDULE_EXPIRED` |

[INFERENCE, theo K R-07] Watchdog (mức 3) đứng **trên** lệnh điều độ (mức 4), vì khi mất công tơ POC thì không thể tuân thủ lệnh lưới, và fallback của watchdog luôn an toàn hơn (P = 0 hoặc giới hạn native). Lệnh tay (mức 7) đứng trên DR và kinh tế nhưng không bao giờ vượt khoảng của mức 1–6.

Ràng buộc cấu hình mức 8–11 [PROPOSAL]: cho phép hoán vị, nhưng mức 10 (EV) không được đặt dưới mức 11 khi site có cam kết giờ đi theo hợp đồng đội xe; thay đổi thứ tự là thay đổi SOE (C3).

### 4.3 Ma trận xung đột thường gặp

| # | Xung đột | Quy tắc mặc định | Tham số | Mã lý do |
|---|---|---|---|---|
| X1 | Trần nhập (5) vs dự phòng (6): tải vượt trần MBA khi SOC ≈ dự phòng | Mức 5 thắng: được xả xuống dưới `S_res` tới `S_res_hard` nếu bật, vì nhảy CB cũng làm mất điện tải. Dưới `S_res_hard` thì dừng xả và cảnh báo Cao | `allow_reserve_dip_for_import_cap` (mặc định true), `S_res_hard` (mặc định 50% của `S_res`, không thấp hơn `SOC_min_eff`) | `RESERVE_DIPPED_FOR_IMPORT_CAP` |
| X2 | Giới hạn xuất (4) vs pin đầy | Cắt PV | — | `PV_CURTAILED_EXPORT_LIMIT` |
| X3 | Giới hạn xuất (4) vs lịch `HOLD` (11) | Mức 4 thắng: sạc pin hấp thụ PV trước khi cắt PV, kể cả khi lịch nói `HOLD`; trong `SOC_ceiling_eff` | — | `CHARGE_FORCED_BY_EXPORT_LIMIT` |
| X4 | Peak shaving (9) vs TOU (11): đỉnh demand rơi vào giờ bình thường, lịch muốn giữ SOC cho cao điểm | Mức 9 thắng tại thời điểm vượt, chỉ xả phần cần (`P_allow_rest`); tầng 3 giải lại với SOC mới; tầng 2 tạo lại lịch khi lệch SOC > 5% E | — | `PEAK_SHAVING_OVERRIDE` |
| X5 | EV (10) vs trần nhập (5) | Giảm EV về `I_min`, rồi tạm dừng phiên ưu tiên thấp nhất | Ưu tiên theo phiên/đội xe | `EV_THROTTLED_IMPORT_CAP` |
| X6 | Lệnh tay (7) vs giới hạn xuất (4) | Lệnh tay bị kẹp; trạng thái lệnh `APPLIED_CLAMPED` | — | `MANUAL_CLAMPED_BY_GRID_LIMIT` |
| X7 | Lệnh điều độ (4) vs mọi lịch | Mức 4 thắng; phần lịch xung đột bị treo đến khi lệnh hết hiệu lực; tầng 3 giải lại | — | `OVERRIDDEN_BY_GRID_OPERATOR` |
| X8 | Chế độ native của hãng vs chiến lược của ta | Không chạy song song trên cùng biến; `control_owner` quyết định | — | `NATIVE_MODE_ACTIVE` |
| X9 | Hai mục tiêu kinh tế trong một slot (`p_grid_target` và `soc_target_end`) | `p_grid_target` thắng nếu có; `soc_target_end` chỉ dùng khi slot không có `p_grid_target` (§5.5) | — | `SOC_TARGET_UNREACHABLE` nếu không đạt |
| X10 | DR (8) vs dự phòng (6) | Dự phòng thắng; FlexibilityOffer phải tính headroom trên `SOC_floor_eff` | — | `DR_LIMITED_BY_RESERVE` |

Ví dụ kiểm thử (khớp [04 AC-OPT-01](04-business-requirements.md)): lệnh tay xả 300 kW (mức 7), `export_limit_w = 0` (mức 4), tải 200 kW, PV 0 → khoảng mức 4 cho `P_ess ≤ 200 kW − margin`; setpoint ≤ 200 kW − margin, lệnh `APPLIED_CLAMPED`, mã `MANUAL_CLAMPED_BY_GRID_LIMIT`.

---

## 5. Tầng 1: bộ luật thời gian thực tại edge (MVP)

Tầng 1 chỉ chạy cho chức năng có `control_owner = EDGE` (Gate M2). Với `NATIVE`, edge chỉ đặt tham số, đọc lại và giám sát. [PROPOSAL] Đặc tả dưới đây là đầu vào cho FR-OPT-004, FR-GRID-005, FR-GRID-006, FR-BESS-009 trong [04](04-business-requirements.md).

### 5.1 Yêu cầu tính chất

| Tính chất | Yêu cầu |
|---|---|
| Xác định | Thứ tự đánh giá cố định (§5.2). Cùng process image + cùng cấu hình → cùng setpoint. Không dùng số ngẫu nhiên, không phụ thuộc thứ tự đến của tin nhắn trong chu kỳ. |
| Giải thích được | Mỗi chu kỳ sinh tập mã lý do; edge ghi Event `ARBITER_REASON` khi mức thắng hoặc mã lý do đổi, và một bản tóm tắt mỗi 60 s (mức thắng, khoảng cho phép, setpoint, mã lý do). |
| An toàn trước tiên | Chuyển trạng thái do mức 1–5 kích hoạt **bỏ qua** min dwell và ramp-up chậm; chỉ ramp-down (giảm tác động) được phép tức thời. |
| Không mòn thiết bị | Ghi Modbus chỉ khi vượt deadband hoặc hết `min_write_interval`; tôn trọng `mode_change_min_interval`. |
| Không giả định đã thực thi | Đọc lại P thực tế mỗi chu kỳ. Vòng PI dùng giá trị đo, không dùng giá trị đã ghi. |
| Khởi động an toàn | `SAFE_START`: ≥ 2 chu kỳ đọc đủ dữ liệu trước khi ghi lần đầu ([04 §2](04-business-requirements.md)). |

### 5.2 Chu kỳ 1 s

```
mỗi chu kỳ k (1 s, đồng hồ edge):
  1. Chụp process image: P_grid (MTR_POC), P_pv[i], P_ess, SOC, CCL/DCL, trạng thái BMS/PCS,
     DI interlock, lệnh hiệu lực, slot envelope hiện hành, tuổi từng điểm (age_s), quality.
  2. Kiểm tuổi dữ liệu: age(MTR_POC) > T_stale_poc → cờ POC_STALE; age(BMS) > T_stale_bms → BMS_STALE.
  3. Hết hạn lệnh: lệnh có expires_at ≤ now → EXPIRED, thực hiện on_expiry (REVERT_DEFAULT).
  4. Arbiter (§4.1) tính khoảng cho phép cho P_ess, P_pv_limit, P_ev_limit[i].
  5. Bộ điều khiển (§5.4): chọn điểm trong khoảng theo mục tiêu đang thắng.
  6. Limit chain (§5.3) + ramp.
  7. Deadband & min_write_interval: chỉ ghi khi |Δ| ≥ deadband hoặc đã qua refresh_interval (để watchdog thiết bị không hết hạn).
  8. Ghi qua driver (kiểm kiểu dữ liệu, dấu, tràn số tại lớp thanh ghi).
  9. Ghi mã lý do, cập nhật bộ đếm slot (năng lượng, SOC đầu/cuối, vi phạm).
```

[FACT] OpenEMS PR #3973 kẹp setpoint `SellToGridLimit` về 0 vì controller sinh giá trị âm ghi vào thanh ghi unsigned — https://github.com/OpenEMS/openems/pull/3973 (qua kết quả tìm kiếm). [INFERENCE] Kẹp và kiểm kiểu dữ liệu phải có ở **lớp ghi thanh ghi** của driver, không chỉ ở bộ điều khiển.

### 5.3 Limit chain

[PROPOSAL, theo C §3.7] Tính mỗi chu kỳ, sau arbiter:

```
P_dis_max = min( BMS_P_dis_max (hoặc DCL·V_bat), PCS_rated·derate_temp, √(S_pcs² − Q_cmd²),
                 SOE.P_ess_dis_max,
                 export_headroom   = P_load_now + export_limit − P_pv_now   [nếu ¬allow_ess_export] )
P_ch_max  = min( BMS_P_ch_max (CCL·V_bat), PCS_rated·derate_temp, SOE.P_ess_ch_max,
                 import_headroom   = import_cap − (P_load_now − P_pv_now)   [nếu sạc từ lưới] )
P_cmd     = clamp(P_request, −P_ch_max, +P_dis_max)
SOC ≤ SOC_floor_eff  → P_cmd ≤ 0  (ngoại lệ X1)
SOC ≥ SOC_ceiling_eff→ P_cmd ≥ 0
BMS_STALE hoặc BMS lỗi → P_cmd = 0 hoặc chế độ native (mức 3)
ramp: |P_cmd − P_cmd_prev| ≤ SOE.ramp_max·Δt   (giảm tác động về 0 được bỏ qua ramp khi do mức 1–5)
|P_cmd − P_cmd_prev| ≤ SOE.delta_P_max_per_cmd (cho lệnh từ xa)
```

`P_load_now` là ước lượng tức thời `P_grid + P_pv + P_ess` (dấu K R-01), không phải số đo trực tiếp.

### 5.4 Các bộ điều khiển

**(a) Balancing về `p_grid_target`** (self-consumption, bám envelope `GRID_SETPOINT`/`PEAK_DISCHARGE`/`PV_SURPLUS_CHARGE`):

```
e(k)      = P_grid_meas(k) − p_grid_target
P_req     = P_ess_meas(k) + Kp·e(k) + Ki·Σe·Δt          # ESS + = xả; P_grid > target → xả thêm
anti-windup: dừng cộng Σe khi P_req bị kẹp ở bất kỳ biên nào
```

`p_grid_target` theo chế độ: self-consumption = 0 W + `margin_import`; zero-export bằng ESS = `+margin_export` (dương, giữ nhập nhẹ).

**(b) Zero-export bằng cắt PV** (khi ESS đầy, không có ESS, hoặc đã ở `P_ch_max`):

```
nếu P_grid_meas < margin_low:                                  # đang xuất hoặc sát 0
    P_pv_limit ← max(0, P_pv_meas − (margin_target − P_grid_meas))   # giảm ngay, không chờ
nếu P_grid_meas > margin_high liên tục T_release:
    P_pv_limit ← min(P_pv_rated, P_pv_limit + step_up)         # nới chậm
```

Hysteresis bất đối xứng: **giảm nhanh, tăng chậm**. Lý do: phát ngược là vi phạm, còn cắt dư chỉ mất ít kWh. Phân bổ giới hạn cho nhiều inverter theo tỷ lệ công suất danh định, hoặc ưu tiên inverter phản hồi nhanh; inverter `FAILED_NO_EFFECT` bị loại khỏi pool.

**(c) Trần nhập**:

```
excess = P_grid_meas − (import_cap − margin_import_cap)
nếu excess > 0:
   1) P_ess thêm xả = min(excess, P_dis_max còn lại)          # có thể xuống tới S_res_hard (X1)
   2) phần còn lại: giảm EV (P1) theo §5.4(f)
   3) (P2) cắt phụ tải không quan trọng
   4) vượt liên tục > T_import_alarm → cảnh báo Cao
```

**(d) Cửa sổ demand (Phase 1)**, theo C §3.9:

```
P_allow_rest = (P_target_eff·T_w − E_so_far) / max(T_w − t, 60 s)
P_target_eff = max(P_target_plan, P̂_month)
nếu P_grid_meas > P_allow_rest: P_req ≥ P_ess_meas + (P_grid_meas − P_allow_rest)
```

[INFERENCE, C §3.9] Ví dụ: T_w = 30 phút, P_target = 1.000 kW, sau 20 phút đã nhập 360 kWh → 10 phút còn lại được phép (500 − 360)/(1/6 h) = 840 kW (K đã tính lại). Biên cửa sổ đồng bộ với công tơ thanh toán qua NTP (`clock_state = SYNCED`).

**(e) SOC guard** (luôn chạy):

- `SOC_floor_eff(t) = max(SOC_min_eff, SOC_backup_reserve(t), soc_floor_slot)`.
- `SOC_ceiling_eff(t) = min(SOC_max_eff, 100% − SOC_space_reserve(t), soc_ceiling_slot)`.
- Hysteresis: dừng xả ở `SOC_floor_eff`, chỉ cho xả lại khi `SOC ≥ SOC_floor_eff + h_soc` (mặc định 2 điểm %). Tương tự ở trần.

**(f) EV DLM (Phase 1)**:

```
P_ev_avail = min(P_evse_group_cap,
                 import_cap_eff − (P_grid_meas − P_ev_meas),
                 [P_pv_surplus nếu chế độ "chỉ PV dư"])
Phân bổ: (1) mỗi phiên đang sạc nhận I_min theo thứ tự ưu tiên; phiên không đủ chỗ → 0 A (tạm dừng)
         (2) phần còn lại chia theo trọng số w_e = ưu tiên_e · (kWh còn thiếu_e / giờ còn lại_e)
Gửi: TxProfile có validTo hoặc ChargePointMaxProfile; ≤ 1 lần/10–30 s mỗi trụ
```

### 5.5 Bám envelope của slot

| `slot_mode` | Hành vi tầng 1 | Biến mục tiêu |
|---|---|---|
| `PV_SURPLUS_CHARGE` | Chỉ sạc phần PV dư (`p_grid_target = +margin`, cấm xả cho tải trừ mức 4/5/9) | `p_grid_target_w`, `soc_ceiling` |
| `GRID_CHARGE_TO_TARGET` | Sạc với `P_ch = (soc_target·E − E_now)/(t_end − t)/η_c`, kẹp theo `import_cap` | `soc_target_pct` cuối slot |
| `PEAK_DISCHARGE` | Balancing về `p_grid_target` (thường 0), hoặc xả đều theo `p_ess_max_w`; dừng ở `soc_floor` | `p_grid_target_w`, `soc_floor` |
| `GRID_SETPOINT` | Balancing về `p_grid_target_w` tùy ý (tầng 3) | `p_grid_target_w` |
| `HOLD` | P_ess = 0 trừ mức 4/5/9 | — |
| `IDLE` | P_ess = 0, cho phép standby của PCS nếu hãng hỗ trợ | — |

[INFERENCE] Envelope "setpoint lưới" an toàn hơn "setpoint pin" khi dự báo sai, vì vòng nhanh tự bù sai số tải trong slot 15 phút. [FACT, Low–Med] Victron GX ESS Mode 2 nhận setpoint lưới `/AcPowerSetpoint` (diễn đàn cộng đồng; cấm dùng làm map driver VERIFIED) — https://communityarchive.victronenergy.com/questions/95889/multipluss-ii-is-external-control-ess-mode-2-or-3%EF%B9%96childToView=102991.html (qua kết quả tìm kiếm). [FACT] OpenEMS `Controller.Ess.Balancing` đưa PCC về `targetGridSetpoint` (mặc định 0 W) — https://github.com/OpenEMS/openems/tree/develop/io.openems.edge.controller.ess.balancing (qua kết quả tìm kiếm).

### 5.6 Tham số mặc định (deadband, hysteresis, dwell)

Mọi tham số là [PROPOSAL], cấu hình trong SOE và phải tinh chỉnh tại commissioning.

| Mã | Tham số | Mặc định | Ghi chú |
|---|---|---|---|
| TP-01 | `cycle_s` | 1 | Khớp `edge_sample_period` (K §6 #19) |
| TP-02 | `T_stale_poc` | 3 s | [04 §2], chỉnh 2–5 s |
| TP-03 | `T_stale_bms` | 5 s | I §3.7.2 |
| TP-04 | `write_deadband` | max(1% P_rated, 2 kW) cho ESS; 1% cho PV limit | Chống ghi liên tục |
| TP-05 | `min_write_interval` | 2 s mỗi thiết bị | [04 §2] "thiết bị ≤ 1 setpoint/2 s" |
| TP-06 | `refresh_interval` | ≤ ½ `revert_timeout_s` của thiết bị | Giữ watchdog thiết bị không hết hạn |
| TP-07 | `margin_export` (zero-export) | max(2 kW, 1–3% công suất AC PV) | Phụ thuộc độ trễ vòng và độ ồn tải |
| TP-08 | `margin_low` / `margin_high` (cắt PV) | 0,5× / 2× `margin_export` | Vùng chết giữa hai ngưỡng |
| TP-09 | `T_release` | 30 s | Thời gian P_grid ổn định trên `margin_high` trước khi nới PV |
| TP-10 | `step_up` | 2% P_pv_rated mỗi chu kỳ | Nới chậm |
| TP-11 | `margin_import_cap` | 2% `import_cap` | |
| TP-12 | `h_soc` | 2 điểm % | Hysteresis SOC |
| TP-13 | `dir_change_min_dwell_s` | 30 s | Đổi chiều sạc↔xả do mức 7–12; mức 1–5 bỏ qua |
| TP-14 | `mode_change_min_interval` | 300 s | Đổi `site_strategy`/chế độ native; I §3.7.2 |
| TP-15 | `Kp`, `Ki` | Theo commissioning (test bước tải) | Không có giá trị chung; ghi biên bản |
| TP-16 | `ramp_max` | Theo SOE (ví dụ 10% P_rated/s) | [UNKNOWN] grid code ramp cho C&I VN (Q-C06) |
| TP-17 | `cycles_per_day_max` | 1,5 EFC | Bảo hành pin; vượt → chỉ cho mức 1–6 xả |

### 5.7 Máy trạng thái ESS tại edge

```
          ┌──────────── mức 1–3 bất kỳ lúc nào ────────────┐
          ▼                                                │
     SAFE_ZERO ◄── BMS_STALE | POC_STALE | interlock       │
          │ (điều kiện hết + SAFE_START 2 chu kỳ)          │
          ▼                                                │
        IDLE ◄────────► CHARGING          DISCHARGING ◄──┘
          ▲   dwell ≥ TP-13   ▲              ▲
          └───────────────────┴── dwell ≥ TP-13 (mức 7–12) ┘
     NATIVE_MODE (control_owner = NATIVE hoặc requires_native_fallback): edge chỉ giám sát
```

### 5.8 Kiểm thử tối thiểu cho tầng 1

Mã test theo quy ước `T-<FR id>-NN` ([12 §2.2](12-traceability-matrix.md)); cột "Mã cũ" giữ để truy vết (GAP-12-17).

| Test | Mã cũ | Kịch bản | Kỳ vọng |
|---|---|---|---|
| T-FR-GRID-005-01 | T1-01 | Bước tải −30% khi PV cao, zero-export | Không có sự kiện vi phạm xuất (P_xuất > tol liên tục ≥ 2 s); đạt ≤ 5 s |
| T-FR-OPT-004-01 | T1-02 | Rút cáp `MTR_POC` | Sau `T_stale_poc`: BESS P = 0/native, PV về giới hạn native, IL-04, cảnh báo |
| T-FR-BESS-008-01 | T1-03 | BMS đặt DCL = 0 khi đang xả | Setpoint về 0 trong 1 chu kỳ, `CLAMPED_BY_BMS` |
| T-FR-BESS-005-03 | T1-04 | Lệnh tay hết hạn | `EXPIRED` → `REVERT_DEFAULT`, không có ghi lặp lại sau hạn |
| T-FR-GRID-006-01 | T1-05 | Tải vượt trần với SOC = dự phòng | Xả tới `S_res_hard`, `RESERVE_DIPPED_FOR_IMPORT_CAP` |
| T-FR-OPT-004-02 | T1-06 | Dao động quanh SOC sàn | Không quá 1 lần đổi chiều trong `dir_change_min_dwell_s` |
| T-FR-OPT-003-01 | T1-07 | Hai vòng trên cùng biến | Cấu hình bị từ chối (AC-OPT-05) |

Các test này thuộc chiến lược kiểm thử chung (simulator Modbus/OCPP, HIL) mà K G-05 nêu thiếu; chủ sở hữu là [06](06-system-architecture.html)/[10](10-security-and-reliability.md)/[11](11-mvp-and-roadmap.html).

---

## 6. Tầng 2: bộ sinh lịch luật TOU (MVP)

[PROPOSAL] Viết bằng Java (K R-22). Đầu ra là `DispatchPlan` 48 h, slot 15 phút, `origin = TIER2_RULES`. Nhãn UI "Quy tắc". Đầu vào cho [04 FR-OPT-005](04-business-requirements.md).

### 6.1 Lịch chạy và kích hoạt

| Kích hoạt | Khi nào |
|---|---|
| Định kỳ | 05:30 giờ site hằng ngày (trước khi kết thúc thấp điểm để còn điều chỉnh SOC đích); 16:30 giờ site (cập nhật trước cao điểm theo SOC thực tế) |
| Sự kiện | Đổi `TariffVersion`/lịch TOU áp cho tối ưu; đổi SOE/cấu hình lưới/strategy version; lệch SOC thực tế vs kế hoạch > 5% E_usable; dự báo tải cao điểm mới lệch > 15% so với bản đang dùng; edge báo `OVERRIDDEN` > 2 slot liên tiếp; edge online lại sau khi lịch đã hết |
| Giới hạn | ≤ 12 lần sinh/ngày/site (tránh dao động kế hoạch); cửa sổ đóng băng: slot đang chạy và slot kế tiếp không đổi trừ khi `preempt = true` |

### 6.2 Đầu vào

| Đầu vào | Nguồn | Nếu thiếu |
|---|---|---|
| Lịch TOU + giá, theo lịch "tối ưu" của site | F-TAR-01, 02, 03 | Không sinh kế hoạch; giữ kế hoạch cũ; cảnh báo Trung bình |
| Dự báo tải F1 (median theo thứ × giờ × loại ngày, 4–8 tuần) hoặc F0 | F-ADV-01 | < 7 ngày dữ liệu: profile mặc định theo topology, nhãn "dự báo dự phòng" ([04](04-business-requirements.md) lỗi biên) |
| Profile PV (ngày tương tự 7–14 ngày gần nhất, loại ngày bị cắt) hoặc dự báo PV P50 (Phase 1) | F-ADV-01/02 | Dùng PV = 0 cho SOC đích (bảo thủ: nạp lưới nhiều hơn) |
| SOC hiện tại, `e_usable_current` | F-BESS-01, 03 | Không sinh kế hoạch mới |
| SOE, cấu hình lưới, `allow_grid_charge` | F-BESS-08, F-GRID-03 | Không sinh |
| Tham số strategy version (`pv_forecast_trust_alpha`, `space_reserve`, `soc_target_rule`…) | `OptimizationStrategyVersion.params` ([05](05-domain-model.html)) | Không sinh |

### 6.3 Thuật toán (xác định, theo bước)

```
Input: ngày D (giờ site), horizon [now, now+48 h], slot 15′
1. Gán mỗi slot một băng giá (OFFPEAK | NORMAL | PEAK) từ TouCalendarVersion áp dụng cho tối ưu.
   Ngày không có PEAK (Chủ nhật, lễ theo lịch) → "ngày không cao điểm".
2. Với mỗi khối cao điểm liên tục B (ví dụ 17:30–22:30):
     E_need(B) = Σ_{t∈B} min(L_f[t], P_dis_max_eff) · Δt / η_d          # năng lượng trong pin cần cho B
3. Năng lượng PV dư nạp được trước B (trong cùng ngày, từ 06:00 tới đầu B):
     E_pvs(B)  = Σ_t min( max(0, PV_f[t] − L_f[t]), P_ch_max_eff ) · Δt · η_c
4. SOC đích cuối thấp điểm trước B (nếu allow_grid_charge):
     S_tgt = min( E·SOC_max_eff − E_space,
                  E·SOC_floor_eff + max(0, E_need(B) − α·E_pvs(B)) )
     với E_space = min(E_pvs(B), E·SOC_max_eff − E·SOC_floor_eff)  # chừa chỗ cho PV dư (space reserve)
   Nếu ¬allow_grid_charge: S_tgt không áp dụng; thấp điểm = HOLD.
5. Kiểm tra kinh tế từng nguồn sạc (§16.2): chỉ nạp lưới thấp điểm cho B nếu
     price_peak·η_c·η_d − price_offpeak − c_deg_eff > 0        # c_deg_eff mặc định = c_deg nếu có, ngược lại 0
6. Gán slot_mode:
   OFFPEAK trước B  : GRID_CHARGE_TO_TARGET (soc_target = S_tgt, trải đều trên các slot thấp điểm còn lại)
                       hoặc HOLD nếu SOC ≥ S_tgt
   NORMAL ban ngày  : PV_SURPLUS_CHARGE (p_grid_target = +margin_export), soc_ceiling = SOC_max_eff;
                       không xả cho tải trừ mức 4/5/9
   PEAK             : PEAK_DISCHARGE (p_grid_target = 0 W; p_ess_max_w = E_avail/T_B·η_d nếu E_avail < E_need,
                       để trải đều xả trên cả khối thay vì cạn pin giữa khối)
   NORMAL sau B     : IDLE; hoặc PV_SURPLUS_CHARGE nếu còn PV
   Ngày không cao điểm: PV_SURPLUS_CHARGE ban ngày + SELF-CONSUMPTION theo GRID_SETPOINT 0 W chỉ khi
                       SOC > S_tgt của ngày kế tiếp; không GRID_CHARGE_TO_TARGET; không PEAK_DISCHARGE
7. Mọi slot: soc_floor = SOC_floor_eff(t), import_cap_w, export_limit_w theo cấu hình lưới.
8. Sinh reason_codes cho từng slot (§12) và chi phí dự kiến theo TariffVersion.
9. Gửi Validator (§10). Thất bại → REJECTED, giữ kế hoạch cũ, cảnh báo.
```

Bước 6 dùng `p_ess_max_w` để trải xả: [INFERENCE] với BESS 2 h và cao điểm 5 h, giá phẳng trong 17:30–22:30 nên mọi kWh xả trong khối có giá trị như nhau; trải đều giữ được dư địa cho trần nhập cuối khối.

Hệ số `α ∈ [0, 1]` (mặc định 0,7) là mức tin dự báo PV. [INFERENCE] Đây là chỗ dự báo tạo ra tiền: nạp lưới quá nhiều làm mất chỗ cho PV dư lẽ ra bị cắt (nguồn có giá trị cao nhất); nạp quá ít làm thiếu năng lượng cao điểm. Phase 1 thay `α` cố định bằng P10/P50 từ F-ADV-02.

### 6.4 Ví dụ số (khớp [04 AC-OPT-02](04-business-requirements.md))

Giả định (Ví dụ số, không phải đo): thứ Ba; BESS `E_usable = 1.000 kWh`, `P_dis_max = P_ch_max = 250 kW`; `η_c = η_d = 0,95` (RTE ≈ 0,90); `SOC_floor_eff = 20%`, `SOC_max_eff = 95%`; SOC lúc 00:00 = 20%; dự báo nhu cầu cao điểm `E_need = 600 kWh` (trong pin); PV dư dự báo 300 kWh AC; `α = 0,7`; `allow_grid_charge = true`.

| Bước | Phép tính | Kết quả |
|---|---|---|
| PV dư nạp được | 300 × 0,95 | 285 kWh |
| Phần tin cậy | 0,7 × 285 | 199,5 kWh |
| Năng lượng cần từ lưới (trong pin) | 600 − 199,5 | 400,5 kWh |
| SOC đích 06:00 | 200 + 400,5 = 600,5 kWh | ≈ 60,05% |
| Kiểm space reserve | 950 − 600,5 = 349,5 ≥ 285 | Đủ chỗ cho PV dư |
| Năng lượng AC nạp thấp điểm | 400,5 / 0,95 | ≈ 421,6 kWh, trung bình ≈ 70,3 kW trong 6 h |
| Lịch | 00:00–06:00 `GRID_CHARGE_TO_TARGET`; 06:00–17:30 `PV_SURPLUS_CHARGE`; 17:30–22:30 `PEAK_DISCHARGE`; 22:30–24:00 `IDLE` | Không có `PEAK_DISCHARGE` ngoài 17:30–22:30 |

### 6.5 Hành vi khi lệch thực tế

- PV thực tế thấp hơn dự báo: lần sinh 16:30 thấy SOC thấp hơn kế hoạch; không nạp lưới giờ bình thường (bước 5 cho thấy lãi thấp hơn: 1.361 đ/kWh xả ở biểu giá ví dụ, §16.2) trừ khi strategy version bật `allow_normal_hour_grid_charge`. Cao điểm xả hết phần có, `soc_floor` vẫn giữ.
- Tải cao điểm cao hơn dự báo: balancing về `p_grid_target = 0` xả nhanh hơn; `p_ess_max_w` giới hạn để trải đều; nếu pin chạm sàn trước 22:30 → nhập lưới phần còn lại (ghi `deviation_cause = FORECAST_LOAD`).

### 6.6 Gate M1: ánh xạ xuống lịch native

[PROPOSAL] Khi `control_owner = NATIVE` và site ở Gate M1, bộ sinh lịch dịch `DispatchPlan` thành lịch native qua driver (F-BESS-04):

| Kế hoạch | Lịch native điển hình | Mất mát độ trung thực |
|---|---|---|
| `GRID_CHARGE_TO_TARGET` 00:00–06:00, đích 60% | Khung "charge from grid" 00:00–06:00 + giới hạn SOC cuối nếu hãng có tham số; nếu không có: khung sạc ngắn hơn tính từ `(S_tgt − SOC_now)/P_ch` | Không đạt SOC đích chính xác |
| `PV_SURPLUS_CHARGE` ban ngày | Khung không xả / self-consumption tắt xả | Phụ thuộc chế độ native |
| `PEAK_DISCHARGE` 17:30–22:30 | Khung "discharge" | Không trải đều |
| `import_cap_w` | Capacity control / peak shaving native | Theo hãng |

[INFERENCE] Ánh xạ chỉ được dùng cho chế độ có trong `capability_profile` và ma trận chế độ hợp lệ theo topology. [FACT] Ràng buộc "peak shaving chỉ ở kịch bản on/off-grid" chỉ đúng với manual LUNA2000-(107-215) C&I-Microgrid-SmartLogger3000 được trích, không áp cho SmartLogger5000B on-grid hay SmartEMO (K R-20). Readback lịch native phải khớp trước khi kế hoạch được coi là `EXECUTING`; không khớp → `FAILED_NO_EFFECT`.

[INFERENCE] Lịch native (khung TOU sạc/xả trên logger/EMS tủ) thường lặp lại hằng ngày trên thiết bị và không có thời hạn. Nếu không có quy tắc bổ sung, một lịch ghi ở Gate M1 sẽ tiếp tục chạy khi cloud hoặc edge mất liên lạc quá `plan_expiry_fallback_h` = 48 h ([10](10-security-and-reliability.md)), hoặc khi `TariffVersion`/khung QĐ 963 đã đổi. Khi đó BESS vẫn nạp lưới hoặc xả trong khung giờ cũ, trái với fallback của K §6 #17 và NFR-REL-001 ([04](04-business-requirements.md)). Ba quy tắc dưới đây khép lỗ hổng này. Cả ba áp cho mọi site có `control_owner = NATIVE` ở Gate M1. Cloud không ghi thẳng xuống thiết bị: edge ghi qua driver `VERIFIED_*`.

#### 6.6.1 Chỉ ghi khi lịch thay đổi (giảm mòn NVM)

[PROPOSAL]
1. Edge chuẩn hóa lịch native đích thành dạng chính tắc `native_schedule_canonical`: danh sách khung đã sắp xếp, đơn vị W/%, làm tròn theo bước của thanh ghi. Edge đọc lịch đang có trên thiết bị và chuẩn hóa theo cùng cách.
2. Hai bản trùng nhau: không ghi, kế hoạch chuyển `EXECUTING`, ghi lý do `NATIVE_SCHEDULE_UNCHANGED`. Hai bản khác nhau: chỉ ghi những thanh ghi khác, rồi đọc lại toàn bộ để xác nhận.
3. Lần sinh lịch định kỳ (05:30, 16:30, §6.1) **không** tự nó tạo ra lần ghi. Bản dịch native của một kế hoạch mới thường trùng bản cũ: native chỉ nhận khung giờ, còn SOC đích theo slot bị làm tròn hoặc bỏ. Khi đó không ghi gì.
4. Giới hạn `native_schedule_max_writes_per_day` (mặc định 4, theo site). Vượt mức thì edge giữ lịch hiện hành và phát cảnh báo Trung bình `NATIVE_WRITE_BUDGET_EXCEEDED`. Ngoại lệ: lần ghi về hồ sơ mặc định an toàn ở §6.6.2 luôn được phép.
5. Driver khai báo cờ `persist` và `min_write_interval_ms` cho từng thanh ghi lịch. Thanh ghi nào ghi vào NVM và giới hạn số lần ghi là bao nhiêu vẫn [UNKNOWN] ([13 Q-31](13-open-questions-and-risks.md); rủi ro mòn flash [13 R-15](13-open-questions-and-risks.md)). Khi chưa rõ, driver coi mọi thanh ghi lịch là NVM.
6. Edge đọc lại lịch native mỗi 15 phút. Lệch so với bản đã xác nhận (ví dụ có người sửa tại chỗ) thì edge không tự ghi đè: nó phát cảnh báo Cao `NATIVE_SCHEDULE_DRIFT` và kế hoạch chuyển `OVERRIDDEN`. Lý do: thao tác tại chỗ có thể là chủ ý của người vận hành, gần với tinh thần mức 2 (interlock cục bộ, §4.2); người có quyền quyết định ghi lại hay giữ.

#### 6.6.2 Hết hạn kế hoạch hoặc đổi biểu giá → hồ sơ native mặc định

[PROPOSAL] Mỗi site M1 có một `native_default_profile`. Đây là bản dịch native của chiến lược mặc định (mức 12, §4.2), được validator chấp nhận và ký cùng cấu hình site. Hồ sơ phải thỏa điều kiện **an toàn khi lặp vô hạn**:

| Điều kiện | Nội dung |
|---|---|
| N-01 | Không có khung "charge from grid". Chỉ cho phép self-consumption/sạc PV dư. Nếu hãng không có chế độ "không nạp lưới" thì đặt công suất nạp lưới = 0 |
| N-02 | Không xả ra lưới. Giới hạn xuất native (S1) bật độc lập với lịch |
| N-03 | SOC sàn native ≥ dự phòng backup của site |
| N-04 | Không phụ thuộc khung TOU. Hồ sơ đúng với mọi `TouCalendarVersion` |

Hồ sơ này được kích hoạt trong các trường hợp sau. Mọi trường hợp đều do edge thực hiện, không cần cloud:

| Sự kiện | Hành động của edge | Mã lý do |
|---|---|---|
| Kế hoạch hiện hành hết hạn (`valid_until` của `DispatchPlan`, ≤ `plan_expiry_fallback_h`) mà chưa có kế hoạch mới | Ghi `native_default_profile` (kèm readback) tại thời điểm hết hạn | `FALLBACK_SCHEDULE_EXPIRED` |
| Tới `valid_from` của một `TariffVersion`/`TouCalendarVersion` mới mà kế hoạch đang chạy còn tham chiếu bản cũ | Ghi `native_default_profile` tại `valid_from`, giữ tới khi nhận kế hoạch sinh theo bản mới | `TARIFF_VERSION_CHANGED` |
| Lệnh đổi `site_strategy`, tắt control site (`control_enabled = false`) hoặc kill switch | Ghi `native_default_profile` | `DEFAULT_STRATEGY` |

Để làm được hàng thứ hai, mỗi `DispatchPlan` M1 mang `tariff_version_id`, `tou_calendar_version_id` và `valid_until = min(plan_end, tariff_version.valid_to)`. Cloud gửi trước cho edge các phiên bản biểu giá đã công bố có `valid_from` trong tương lai ([05](05-domain-model.html)).

#### 6.6.3 Edge cũng mất: lịch đang chạy phải an toàn khi lặp vô hạn

[INFERENCE] Khi chính edge hỏng, mất nguồn hoặc mất liên lạc với logger, không thành phần nào của ta còn ghi được hồ sơ mặc định. Lịch native cuối cùng sẽ lặp mãi. Vì vậy validator (§10.2) áp thêm quy tắc cho **mọi** lịch native M1, không chỉ cho hồ sơ mặc định:

| Quy tắc | Nội dung | Mức |
|---|---|---|
| V-N1 | Mọi khung nạp lưới phải có công suất nạp ≤ `import_cap_w` − `P_load_offpeak_p95` của site, **hoặc** thiết bị đang chạy capacity control/peak shaving native với ngưỡng ≤ `import_cap_w` (đã có readback). Thiếu cả hai: không cho khung nạp lưới ở M1. Kế hoạch còn `PV_SURPLUS_CHARGE` + `PEAK_DISCHARGE` | Chặn |
| V-N2 | Khung nạp lưới chỉ nằm trong băng thấp điểm của **mọi** `TouCalendarVersion` đã công bố còn hiệu lực trong 48 h tới | Chặn |
| V-N3 | Có SOC đích/giới hạn SOC cuối khung nạp, **hoặc** độ dài khung ≤ `(S_tgt − SOC_floor)·E/P_ch` | Chặn |
| V-N4 | SOC sàn native ≥ dự phòng backup; giới hạn xuất native bật | Chặn |

[INFERENCE] Bảo vệ thiết bị vẫn do BMS/PCS/rơ-le native đảm nhiệm; lịch lặp không vượt qua được bảo vệ đó. Rủi ro còn lại chỉ là kinh tế và hợp đồng: nạp lưới hoặc xả sai khung TOU sau khi lịch giờ đổi mà edge đã chết trước `valid_from`. Giảm thiểu: cloud phát hiện edge offline (heartbeat) và phát cảnh báo Cao `EDGE_OFFLINE_NATIVE_SCHEDULE_ACTIVE` sau 1 h, nâng lên Khẩn cấp nếu còn offline khi tới `valid_from` của biểu giá mới. Runbook yêu cầu O&M tới hiện trường để chuyển hệ thống sang LOCAL hoặc tắt lịch tại chỗ. Ghi là R-08-10 (§19.2), gửi [13](13-open-questions-and-risks.md) cấp mã chính thức.

#### 6.6.4 Kiểm thử chấp nhận cho ánh xạ native

| Test | Kịch bản | Kỳ vọng |
|---|---|---|
| T-FR-BESS-003-01 | Sinh lại kế hoạch 05:30 và 16:30 trong 7 ngày, bản dịch native không đổi; sau đó một kế hoạch có khung khác | 0 lần ghi thanh ghi lịch khi không đổi (đếm từ log Modbus của simulator); khi đổi, chỉ thanh ghi khác được ghi; readback khớp → `EXECUTING` |
| T-FR-BESS-003-02 | (a) Chặn broker > `plan_expiry_fallback_h`; (b) công bố `TouCalendarVersion` mới có `valid_from` trong 24 h rồi chặn broker | (a) Tại `valid_until`: edge ghi `native_default_profile`, readback khớp, `FALLBACK_SCHEDULE_EXPIRED`. (b) Tại `valid_from`: tương tự với `TARIFF_VERSION_CHANGED`. Không có khung nạp lưới sau thời điểm đó |
| T-FR-BESS-003-03 | Gửi lịch native có khung nạp lưới vượt `import_cap_w` − tải p95 trên thiết bị không có capacity control native; rồi tắt nguồn edge khi đang chạy một lịch hợp lệ trong 72 h (HIL) | Validator chặn (V-N1). Với lịch hợp lệ: P nhập tại `MTR_POC` không vượt `import_cap_w` trong 72 h; cloud phát `EDGE_OFFLINE_NATIVE_SCHEDULE_ACTIVE` sau 1 h |

---

## 7. Tầng 3: MILP và MPC (Phase 1)

[PROPOSAL] Optimization Service, `origin = TIER3_OPTIMIZER`, nhãn "tối ưu dựa trên dự báo". Bật theo site chỉ sau cổng backtest (§14.4). Đầu vào cho [04 FR-OPT-014](04-business-requirements.md).

### 7.1 Tập chỉ số

| Ký hiệu | Ý nghĩa |
|---|---|
| `T = {0, …, N−1}` | Slot; `Δt = 0,25 h`; `N = 192` (48 h). Slot 0 bắt đầu ở biên 15′ kế tiếp sau thời điểm giải + cửa sổ đóng băng |
| `W` | Cửa sổ demand có tính tiền trong horizon; với cửa sổ 30′ block và slot 15′, mỗi `w` gồm 2 slot thẳng hàng :00/:30; `T_w ⊂ T` |
| `B ⊂ T` | Slot thuộc khung có tính demand (nếu biểu giá chỉ tính Pmax trong một số khung; UNKNOWN, mặc định mọi slot) |
| `E` | Phiên EV đã biết hoặc dự kiến; phiên `e` có bước đến `a_e`, bước đi `d_e` |
| `M` | Điểm đo thanh toán (POC chính, công tơ EV riêng…) với biểu giá riêng |
| `D` | Ngày địa phương trong horizon (cho giới hạn chu kỳ/ngày và ngân sách xuất) |

### 7.2 Tham số

| Ký hiệu | Ý nghĩa | Đơn vị | Nguồn |
|---|---|---|---|
| `c_imp[m,t]` | Giá nhập theo TOU của điểm đo m | đ/kWh | M-TAR, theo TariffVersion |
| `c_exp[t]` | Giá bán dư (0 nếu không bán) | đ/kWh | F-TAR-08 |
| `c_dem` | Giá công suất quy về kỳ | đ/kW·kỳ | F-TAR-07; 0 nếu tắt |
| `P̂_month` | Pmax đã ghi nhận trong kỳ tới lúc giải | kW | Bộ đếm cửa sổ (F-GRID-09) |
| `P_reg`, `c_over` | Công suất đăng ký và giá phạt vượt (kịch bản `CONTRACTED`) | kW, đ/kW | UNKNOWN (R-16) |
| `PV_f[t]`, `L_f[t]` | Dự báo PV khả dụng (P50), tải không linh hoạt (không gồm EV) | kW | F-ADV-01/02 |
| `PV_lo[t]`, `L_hi[t]` | Dự báo bảo thủ (P10 PV, P90 tải) cho ràng buộc an toàn năng lượng | kW | F-ADV-02 (Phase 1) |
| `E_cap` | Dung lượng khả dụng hiện tại | kWh | `e_usable_current` |
| `s_0` | Năng lượng trong pin lúc giải | kWh | SOC BMS × E_cap (bất định) |
| `S_min`, `S_max` | `SOC_min_eff·E_cap`, `SOC_max_eff·E_cap` | kWh | SOE |
| `S_res[t]`, `S_res_hard` | Dự phòng theo slot, mức tối thiểu khi giữ trần nhập | kWh | Chính sách site |
| `η_c`, `η_d` | Hiệu suất sạc, xả tại ranh giới AC của PCS | — | Đo (C #7), mặc định 0,95/0,95 |
| `δ` | Tự xả + tiêu thụ phụ trợ quy về pin | kW | MTR_AUX hoặc cấu hình |
| `Pc_max[t]`, `Pd_max[t]` | Giới hạn sạc/xả dự kiến (derate theo nhiệt/SOC), ≤ SOE | kW | BMS/PCS + SOE |
| `R` | Ramp tối đa giữa hai slot | kW/slot | SOE |
| `Gi_max[t]`, `Ge_max[t]` | `import_cap`, `export_limit` (kW) | kW | Cấu hình lưới |
| `c_deg` | Chi phí suy hao theo kWh xả | đ/kWh | F-OPT-14 |
| `c_curt` | Chi phí cắt PV (nhỏ, ưu tiên dùng PV) | đ/kWh | ε, mặc định 1 |
| `ε_t` | Hệ số ưu tiên thời gian để phá suy biến | đ/kWh | 10⁻³·t |
| `λ_stab` | Phạt lệch so với kế hoạch đang chạy (ổn định kế hoạch) | đ/kW | Mặc định 1 |
| `p_prev[t]` | `pd − pc` của kế hoạch đang chạy ở slot t | kW | Plan version hiện hành |
| `Pev_min_e`, `Pev_max_e` | Công suất EV tối thiểu khi sạc (`I_min`), tối đa | kW | OCPP/trụ |
| `Eev_req_e` | Năng lượng cần trước `d_e` | kWh | Phiên/đội xe |
| `Pevse_cap` | Trần nhóm trụ | kW | Cấu hình |
| `N_cyc` | Chu kỳ tương đương tối đa/ngày | — | SOE `cycles_per_day_max` |
| `ρ`, `E_exp_sofar`, `E_pv_sofar`, `B_exp_day[d]` | Tỷ lệ ngân sách xuất, lũy kế kỳ, ngân sách ngày phân bổ | —, kWh | F-TAR-08 (UNKNOWN) |
| `v_term` | Giá trị kWh còn lại cuối horizon | đ/kWh | ≈ `c_imp` cao điểm kế tiếp × η_d − c_deg |
| `M_res`, `M_ev`, `M_g` | Phạt vi phạm mềm | đ/kWh | ≫ mọi giá (ví dụ 10⁶) |
| `allow_grid_charge`, `allow_ess_export` | Cờ chính sách | bool | F-GRID-03 |

### 7.3 Biến quyết định (dạng phân rã dòng)

[PROPOSAL] Dùng biến dòng giữa các nút (PV, lưới, pin, tải, EV). Cách này biểu diễn chính xác `allow_grid_charge`, `allow_ess_export`, quy kết nguồn điện xuất (NĐ 243) và phân bổ nguồn tiết kiệm, mà không cần binary.

| Biến | Miền | Ý nghĩa (kW, trung bình slot) |
|---|---|---|
| `f_pl[t]`, `f_pb[t]`, `f_pg[t]`, `f_pe[t]` | ≥ 0 | PV → tải, PV → pin, PV → lưới, PV → EV |
| `f_gl[t]`, `f_gb[t]`, `f_ge[t]` | ≥ 0 | Lưới → tải, lưới → pin, lưới → EV |
| `f_bl[t]`, `f_bg[t]`, `f_be[t]` | ≥ 0 | Pin → tải, pin → lưới, pin → EV |
| `pev[e,t]` | ≥ 0 | Công suất sạc phiên e |
| `s[t]`, t = 0…N | `S_min ≤ s ≤ S_max` | Năng lượng trong pin (kWh) |
| `Pk` | ≥ `P̂_month` | Pmax kỳ sau horizon (kịch bản `MEASURED_MAX`) |
| `u_over[w]` | ≥ 0 | Phần vượt `P_reg` (kịch bản `CONTRACTED`) |
| `zb[t]` | {0,1} | 1 = slot sạc (cấm xả); chỉ thêm khi cần (§7.5) |
| `zev[e,t]` | {0,1} | 1 = phiên e đang sạc (áp `I_min`) |
| `dpos[t]`, `dneg[t]` | ≥ 0 | Lệch dương/âm so với `p_prev` |
| `σres[t]`, `σev[e]`, `σg[t]` | ≥ 0 | Slack vi phạm mềm |

Biểu thức dẫn xuất:

```
gi[t] = f_gl[t] + f_gb[t] + f_ge[t]          # nhập
ge[t] = f_pg[t] + f_bg[t]                    # xuất
pc[t] = f_pb[t] + f_gb[t]                    # sạc (AC)
pd[t] = f_bl[t] + f_bg[t] + f_be[t]          # xả (AC)
pv[t] = f_pl[t] + f_pb[t] + f_pg[t] + f_pe[t] # PV dùng; PV_f − pv = cắt
```

### 7.4 Hàm mục tiêu

```
min  Σ_t Σ_m c_imp[m,t]·gi_m[t]·Δt  −  Σ_t c_exp[t]·ge[t]·Δt                  (1) năng lượng
   + c_dem·(Pk − P̂_month)                                                    (2a) demand, MEASURED_MAX
   + c_over·Σ_w u_over[w]                                                     (2b) demand, CONTRACTED
   + c_deg·Σ_t pd[t]·Δt                                                       (3) suy hao
   + c_curt·Σ_t (PV_f[t] − pv[t])·Δt                                          (4) cắt PV
   − v_term·s[N]                                                              (5) giá trị cuối horizon
   + λ_stab·Σ_t (dpos[t] + dneg[t])                                           (6) ổn định kế hoạch
   + Σ_t ε_t·(pc[t] + pd[t])                                                  (7) phá suy biến
   + M_res·Σ_t σres[t] + M_ev·Σ_e σev[e] + M_g·Σ_t σg[t]                     (8) vi phạm mềm
```

Ghi chú:

- (2a): horizon 48 h ngắn hơn kỳ hóa đơn, nên chỉ tính **phần tăng thêm** so với `P̂_month`. Dùng nguyên `c_dem·Pk` sẽ làm solver xả pin quá mức để hạ đỉnh của một ngày. Chỉ bật (2a) **hoặc** (2b) theo `demand_basis` của TariffVersion; cả hai tắt mặc định (K R-16).
- (5): `v_term` chống "xả cạn cuối horizon". Phương án thay thế: ràng buộc `s[N] ≥ S_term` = SOC đích tầng 2 cho ngày N+1.
- (6): làm kế hoạch MPC không "lật" giữa các lần giải khi chi phí gần bằng nhau; cần thiết để người vận hành tin kế hoạch và để `plan_slot_result` có ý nghĩa.
- (7): LP suy biến (nhiều nghiệm cùng chi phí) làm kết quả phụ thuộc thứ tự nội bộ của solver. `ε_t` tăng theo t buộc ưu tiên sớm/muộn một cách xác định.

### 7.5 Ràng buộc

```
(C1) Cân bằng nút tải:     f_pl[t] + f_gl[t] + f_bl[t] = L_f[t]                                  ∀t
(C2) Cân bằng nút EV:      f_pe[t] + f_ge[t] + f_be[t] = Σ_e pev[e,t]                           ∀t
(C3) PV:                   pv[t] ≤ PV_f[t]                                                       ∀t
(C4) Động học pin:         s[t+1] = s[t] + (η_c·pc[t] − pd[t]/η_d − δ)·Δt                        ∀t
                           s[0] = s_0
(C5) Giới hạn năng lượng:  S_min ≤ s[t] ≤ S_max                                                  ∀t
(C6) Dự phòng mềm:         s[t] ≥ S_res[t] − σres[t];   s[t] ≥ S_res_hard                        ∀t
(C7) Giới hạn công suất:   pc[t] ≤ Pc_max[t];   pd[t] ≤ Pd_max[t]                                 ∀t
(C8) Lưới:                 gi[t] ≤ Gi_max[t] + σg[t];   ge[t] ≤ Ge_max[t]                         ∀t
                           (ZERO_EXPORT: Ge_max = 0 ⇒ f_pg = f_bg = 0; biên vi phạm xuất là cứng)
(C9) Ramp (net ESS):       −R ≤ (pd[t] − pc[t]) − (pd[t−1] − pc[t−1]) ≤ R                         ∀t ≥ 1
                           t = 0 so với P_ess đo hiện tại
(C10) Demand MEASURED_MAX: (1/|T_w|)·Σ_{t∈T_w} gi[t] ≤ Pk                                        ∀w ∈ W, T_w ⊂ B
                           Pk ≥ P̂_month
(C10') Demand CONTRACTED:  (1/|T_w|)·Σ_{t∈T_w} gi[t] − P_reg ≤ u_over[w]                         ∀w
(C11) EV:                  Pev_min_e·zev[e,t] ≤ pev[e,t] ≤ Pev_max_e·zev[e,t]   t ∈ [a_e, d_e)
                           pev[e,t] = 0 ngoài [a_e, d_e)
                           Σ_t pev[e,t]·Δt + σev[e] ≥ Eev_req_e                                  ∀e
                           Σ_e pev[e,t] ≤ Pevse_cap                                              ∀t
(C12) Chính sách:          ¬allow_grid_charge ⇒ f_gb[t] = 0                                      ∀t
                           ¬allow_ess_export  ⇒ f_bg[t] = 0                                      ∀t
                           EV chỉ PV dư       ⇒ f_ge[t] = f_be[t] = 0                            ∀t
(C13) Chu kỳ/ngày:         Σ_{t∈d} pd[t]·Δt ≤ N_cyc·E_cap                                        ∀d ∈ D
(C14) Ngân sách xuất (P1): E_exp_sofar + Σ_{t∈d≤D} ge[t]·Δt ≤ Σ_{d} B_exp_day[d]                 (phân bổ theo ngày)
                           với B_exp_day do tầng kỳ tính từ ρ·(E_pv_sofar + E_pv_dự_báo_còn_lại) − E_exp_sofar
(C15) Ổn định kế hoạch:    (pd[t] − pc[t]) − p_prev[t] = dpos[t] − dneg[t]                        ∀t có p_prev
(C16) An toàn năng lượng (P1, tùy chọn): kịch bản bảo thủ PV_lo/L_hi phải giữ s[t] ≥ S_res[t]
                           (thêm bản sao (C1)–(C5) cho kịch bản bảo thủ với cùng quyết định lưới–pin của slot 0)
(C17) Cấm sạc–xả đồng thời (chỉ khi cần, §7.6): pc[t] ≤ Pc_max[t]·zb[t];  pd[t] ≤ Pd_max[t]·(1 − zb[t])
```

Không thêm ràng buộc cấm nhập–xuất đồng thời: với phân rã dòng, nhập và xuất đồng thời chỉ xảy ra khi có lợi về toán (giá xuất > giá nhập), khi đó chặn bằng `c_exp[t] ≤ c_imp[t]` hoặc bằng binary tương tự (C17) cho lưới.

### 7.6 LP trước, MILP khi cần

[INFERENCE] Khi `c_imp > 0`, `η_c·η_d < 1` và cho phép cắt PV, sạc–xả đồng thời làm tăng chi phí nên LP relaxation thường tự tránh. Ngoại lệ: cần "đốt" năng lượng (xuất bị cấm, PV không cắt được), hoặc giá xuất âm.

```
1. Giải LP (bỏ zb, zev; EV coi như liên tục 0…Pev_max).
2. Kiểm hậu nghiệm:  min(pc[t], pd[t]) > tol ?   EV có 0 < pev < Pev_min ?
3. Nếu có: thêm (C17) cho slot vi phạm và zev cho phiên vi phạm, giải MILP (time_limit 20 s, mip_gap 0,5%).
4. MILP không xong trong time_limit: lấy nghiệm khả thi tốt nhất nếu gap ≤ 2%; nếu không → fallback tầng 2.
5. Bãi xe lớn (> 20 phiên): giữ LP cho EV, làm tròn hậu nghiệm, để tầng 1 phân bổ I_min (§5.4f).
```

### 7.7 Nhiều biểu giá trong site

[PROPOSAL] Khi EV có công tơ thanh toán riêng nhưng vẫn sau MBA chung: tách nhập lưới thành `gi_main[t]` (cho tải + pin) và `gi_ev[t]` (cho EV), mỗi phần nhân giá của điểm đo đó; ràng buộc trần MBA áp lên tổng `gi_main + gi_ev ≤ Gi_max`. Dòng pin → EV (`f_be`) chỉ cho phép nếu topology điện cho phép (pin nằm trước công tơ EV). Chỉ dùng khi F-TAR-04 khai báo rõ topology đo.

### 7.8 Kích thước và thời gian giải

| Cấu hình | Biến liên tục | Binary | Ràng buộc | Ước lượng |
|---|---|---|---|---|
| 192 slot, không EV, LP | ≈ 11×192 + 193 ≈ 2.300 | 0 | ≈ 2.500 | [INFERENCE] Rất nhỏ; LP mã nguồn mở thường dưới 1 s. Cần benchmark (Q-08-05) |
| 192 slot + 10 phiên EV, MILP | ≈ 4.200 | ≤ 192 + 10×(slot hiện diện) | ≈ 5.000 | Vẫn nhỏ; `time_limit` 20 s |
| 500 site | 500 bài độc lập | — | — | Song song theo site; rải lệch pha giải trong 15 phút |
| 2.000 site × 96 lần/ngày | ≈ 192.000 lần giải/ngày | — | — | [INFERENCE] Khả thi với vài worker nếu p95 < 1 s cho LP; NFR do 04 cấp |

[PROPOSAL] NFR ứng viên cho 04: giải 1 site ≤ 30 s p95 (MILP), toàn bộ site trong ≤ 5 phút mỗi chu kỳ 15 phút, kết quả xác định theo version.

### 7.9 Vòng MPC (receding horizon)

```
mỗi 15′ (lệch pha theo hash(site_id) mod 900 s) hoặc khi có sự kiện tái lập kế hoạch:
  1. Snapshot trạng thái: SOC (edge, tuổi ≤ 60 s), P̂_month, kế hoạch đang chạy, slot đang chạy,
     Pc_max/Pd_max hiện hành, phiên EV, lệnh hiệu lực (GRID_OPERATOR, tay), SOE version.
     SOC cũ hơn 60 s hoặc edge OFFLINE → bỏ lần giải này (không lập kế hoạch trên dữ liệu cũ).
  2. Lấy ForecastRun mới nhất (issue_time ≤ now); ghi forecast_run_id vào input_snapshot.
  3. Dựng mô hình từ TariffVersion áp cho tối ưu; slot 0 = biên 15′ sau cửa sổ đóng băng.
  4. Giải LP → (MILP nếu cần) với tham số solver cố định: threads = 1, seed cố định, presolve cố định.
  5. Hậu xử lý thành envelope (§7.10); làm tròn W nguyên.
  6. Validator (§10). Fail → REJECTED, dùng kế hoạch tầng 2 cùng horizon nếu kế hoạch đang chạy còn < 24 h.
  7. Guardrail → AUTO_GUARDRAIL hoặc chờ duyệt.
  8. Dispatch APPLY_SCHEDULE (supersedes = command trước, preempt = false).
  9. Lưu input_snapshot + input_hash + output + dual (shadow price) để giải thích và tái lập.
```

Sự kiện tái lập kế hoạch: lệch SOC thực tế vs kế hoạch > 5% E_cap; dự báo mới lệch > X% (tham số); giới hạn BMS thay đổi > 10%; đổi tariff/cấu hình; edge báo `OVERRIDDEN` hoặc kết thúc lệnh `GRID_OPERATOR`; phiên EV mới.

Xử lý bất định [PROPOSAL]: Phase 1 dùng dự báo điểm (P50) cho mục tiêu, cộng ràng buộc an toàn (C16) với kịch bản bảo thủ cho dự phòng/năng lượng cao điểm, cộng vòng nhanh tầng 1 hấp thụ sai số trong slot. Stochastic/robust MPC để sau, chỉ khi backtest cho thấy lợi ích.

### 7.10 Từ nghiệm MILP sang envelope

Không gửi `pc/pd` thô làm setpoint cứng. [PROPOSAL] Mỗi slot:

| Trường envelope | Từ nghiệm |
|---|---|
| `slot_mode` | `GRID_SETPOINT` nếu nghiệm xả/sạc theo nhu cầu tải; `GRID_CHARGE_TO_TARGET` nếu `f_gb > 0`; `PV_SURPLUS_CHARGE` nếu chỉ `f_pb > 0`; `HOLD` nếu `pc = pd = 0`; `IDLE` khi PCS có thể standby |
| `p_grid_target_w` | `(gi[t] − ge[t])·1.000` |
| `soc_target_pct` | `s[t+1]/E_cap·100` |
| `p_ess_min_w`, `p_ess_max_w` | Nới quanh nghiệm: `[(pd − pc) − Δ, (pd − pc) + Δ]` với Δ = 20% P_rated, cắt theo SOE |
| `import_cap_w`, `export_limit_w` | Cấu hình lưới (không nới) |
| `soc_floor`, `soc_ceiling` | `S_res[t]`, `S_max` (và space reserve nếu có) |
| `ev_limit_w` | `Σ_e pev[e,t]·1.000` |
| `reason_codes` | Từ quy tắc dịch nghiệm (§12.2) |
| `expected_cost`, `shadow_soc_vnd_per_kwh` | Đóng góp mục tiêu của slot; dual của (C4) |

---

## 8. Solver cho stack Java/Spring

### 8.1 Tiêu chí

| Tiêu chí | Yêu cầu |
|---|---|
| Lớp bài toán | LP và MILP nhỏ (≤ 10⁴ biến), hệ số thực |
| Tích hợp | Chạy trong JVM (Spring Boot) hoặc sidecar có hợp đồng JSON version |
| Giấy phép | Cho phép dùng trong SaaS thương mại, không copyleft lan sang mã của ta |
| Xác định | Cho phép cố định threads, seed; cùng input → cùng output |
| Dual | Lấy được giá trị đối ngẫu của LP (cho shadow price, F-OPT-12) |
| Vận hành | Không có server license; build cho Linux x86_64/ARM64 |

### 8.2 Đánh giá

Toàn bộ cột "Giấy phép" và "Binding Java" là **kiến thức nền chưa kiểm chứng trong phiên này** (hết hạn mức tìm kiếm). Không chốt ADR trên bảng này khi chưa đọc file LICENSE và tài liệu chính thức (Q-08-04).

| Ứng viên | Loại | Giấy phép (cần kiểm chứng) | Tích hợp Java | Dual LP | Phù hợp | Nhãn |
|---|---|---|---|---|---|---|
| **HiGHS** | LP (simplex, IPM), MIP | MIT | Không có binding Java chính thức được biết; dùng qua OR-Tools (nếu bản OR-Tools có backend HiGHS), JNI tự viết, hoặc sidecar Python (`highspy`) | Có | Rất phù hợp kích thước bài toán | [INFERENCE] |
| **Google OR-Tools** (MPSolver) | Wrapper: GLOP (LP), SCIP, CBC, có thể HiGHS; CP-SAT | Apache-2.0 | **Binding Java chính thức** (Maven, có native lib) | Có (GLOP và backend LP) | Lựa chọn tự nhiên cho Spring Boot; CP-SAT không phù hợp cho hệ số thực liên tục | [INFERENCE] |
| **ojAlgo** | LP, QP, MIP thuần Java | MIT | Java thuần, không native lib | Có (LP) | Đủ cho LP nhỏ; MIP yếu hơn solver chuyên dụng; dễ triển khai nhất | [INFERENCE] |
| **CBC** (COIN-OR) | MIP | EPL-2.0 | Qua OR-Tools | Qua LP | Ổn định; dùng làm dự phòng | [INFERENCE] |
| **SCIP** | MIP | Apache-2.0 từ khoảng bản 8.0.3 (K ghi chú, chưa kiểm chứng) | Qua OR-Tools | Qua LP | Dự phòng cho MILP khó | [UNKNOWN] |
| **Timefold Solver** (fork OptaPlanner) | Metaheuristic, constraint solver | Apache-2.0 (community) | Java native | Không | **Không phù hợp** dispatch liên tục (cân bằng công suất, động học SOC): không đảm bảo tối ưu, không có dual, khó xác định. Phù hợp lập lịch rời rạc khác: phân ca O&M, work order (M-ALM), xếp thứ tự hàng chục–trăm phiên EV | [INFERENCE] |
| **Gurobi / CPLEX** | LP/MIP thương mại | Thương mại, license theo node/cloud | API Java chính thức | Có | Không cần cho kích thước này; chỉ xem xét cho tối ưu danh mục VPP lớn (P2+) | [INFERENCE] |

### 8.3 Phương án kiến trúc

| Phương án | Mô tả | Ưu | Nhược |
|---|---|---|---|
| A. Java + OR-Tools MPSolver | Optimization Service (Spring Boot) dựng mô hình bằng API MPSolver; backend GLOP cho LP, SCIP/CBC (hoặc HiGHS nếu có) cho MILP | Một ngôn ngữ, một pipeline build, không thêm runtime; khớp K R-22 | API mệnh lệnh khó đọc; native lib cần quản lý theo kiến trúc CPU |
| A'. Java + ojAlgo | Như A nhưng thuần Java | Không native lib; triển khai đơn giản | Hiệu năng MIP cần benchmark |
| B. Python sidecar (linopy/Pyomo + HiGHS) | Dịch vụ riêng, hợp đồng JSON `OptimizationRequest/Result` có version | Hệ sinh thái tối ưu năng lượng và backtest mạnh; mô hình đọc như toán | Thêm runtime, CI, bảo mật cho một ngôn ngữ; cần ADR (K R-22) |

### 8.4 Khuyến nghị cho ADR-OPT (do [06](06-system-architecture.html) cấp số)

[PROPOSAL]

1. Tầng 1 (edge) và tầng 2 (luật) bằng Java, không solver.
2. Tầng 3: bắt đầu bằng **phương án A** (OR-Tools Java, backend LP mã nguồn mở) với một lớp trừu tượng `SolverPort` (dựng mô hình độc lập solver). Benchmark A và A' trên dữ liệu site thật (Q-08-05) trước khi Phase 1 bắt đầu.
3. Chỉ chuyển sang B nếu (a) benchmark A không đạt NFR, hoặc (b) chi phí phát triển mô hình/backtest bằng Java vượt ngưỡng do 06 định. Khi đó ADR phải ghi rõ ngoại lệ so với stack cũ.
4. Pin phiên bản solver và native lib; `engine_ref` trong strategy version ghi `solver@version + model@version`.
5. Điều kiện chặn: kiểm chứng giấy phép (HiGHS, OR-Tools và các backend đóng gói kèm, ojAlgo, SCIP) bằng file LICENSE của bản phát hành sẽ dùng.

---

## 9. Tầng 4: DR, VPP, thị trường (Phase 2 / ngoài phạm vi)

[PROPOSAL] "VPP-capable" ở Phase 2 (F-OPT-20) gồm đúng bốn phần, **không** gồm bidding:

1. `FlexibilityOffer` theo slot: `up_kw[t]` = khả năng tăng xả/giảm sạc trong giới hạn SOE, `SOC_floor_eff` và trần nhập; `down_kw[t]` tương tự chiều ngược. Tính từ kế hoạch đang chạy + headroom SOC.
2. Nguồn lệnh `DR` trong envelope (đã có trong hợp đồng lệnh của E §3.19) → mức 8 của arbiter.
3. API sự kiện DR; OpenADR 3.0 (REST/JSON) là ứng viên (E F-22).
4. Báo cáo kết quả sự kiện so baseline sự kiện (riêng với baseline tiết kiệm §15).

[FACT, Med–High] Huawei có API VPP trên cloud (`vpp/chargeAndDischarge`: dispatchSwitch, controlType SOC/duration, targetSOC, dispatchTime, powerDispatch W, requestID duy nhất; không gọi lại trước khi task xong; timeout 24 h) — https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/imaster-neteco-v600r022c00-northbound-interface-reference-v6.pdf (nghiên cứu FusionSolar). [INFERENCE] Đường này có độ trễ phút, chỉ dùng cho tầng 4 khi site ở chế độ connector cloud; không dùng cho tầng 1.

[FACT] Úc yêu cầu pin "VPP-capable" (A #37, theo 03 F-OPT-20). [UNKNOWN] Tương đương ở Việt Nam.

Giao dịch thị trường (DA/intraday/aFRR/FCR) và đáp ứng tần số: ngoài phạm vi 12–18 tháng (F-OPT-21; K §6 #1).

---

## 10. An toàn: bộ kiểm tra ràng buộc và vùng vận hành an toàn

### 10.1 Chuỗi 7 lớp

Mọi đầu ra của tầng 2/3/4, lịch tay và lệnh tay đi qua đủ các lớp sau. Một lớp không được bỏ qua vì lớp khác "chắc đã kiểm".

| Lớp | Ở đâu | Kiểm gì | Thất bại thì |
|---|---|---|---|
| L1 Validator kế hoạch | Cloud | §10.2 | `REJECTED`; giữ kế hoạch cũ; cảnh báo Trung bình |
| L2 PDP | Cloud | Quyền, hạng lệnh (C1 cho kế hoạch trong guardrail), `control_enabled`, Gate của site, kill switch, LOCAL/REMOTE đã biết | `DENIED` |
| L3 Fleet Dispatch Governor | Cloud | Σ\|ΔP\| được lệnh trong 5 phút ≤ 20% MW BESS của tenant (PROPOSAL, cần mô phỏng); jitter 0–300 s | Hàng đợi + nâng C3 |
| L4 Kiểm nhận lệnh | Edge | Chữ ký JWS, `kid`, `seq`, hạn (`clock_state = SYNCED`), `max_latency_ms`, interlock IL-01…IL-10, SOE, `capability_profile` | `REJECTED_*` |
| L5 Arbiter | Edge | 12 mức (§4) | Kẹp; mã lý do |
| L6 Limit chain | Edge | CCL/DCL, SOC, POC headroom, ramp, ΔP (§5.3) | Kẹp; `APPLIED_CLAMPED` |
| L7 Bảo vệ native | Thiết bị | BMS/PCS/rơ-le | Thiết bị tự bảo vệ; EMS chỉ đọc |

[INFERENCE] Theo một patent ESS, BMS gửi tín hiệu bảo vệ tới PCS qua dây cứng, kênh tới EMS chỉ là TCP/IP, RS485 hoặc CAN (E §3.1, theo [03 F-BESS-10](03-functional-catalog.html#f-bess-10)) → phần mềm EMS nằm ngoài vòng bảo vệ. [FACT, Med–High] BMS bảo vệ/cân bằng; PCS chuyển đổi và thực thi; EMS quyết định điều độ; giới hạn BMS phải được PCS và EMS tôn trọng — https://deye.com/nl/blog/bms-vs-ems-vs-pcs-bess-components/ (qua kết quả tìm kiếm). [FACT, Low] Trang hạt giống InfinitePower mô tả EMS điều phối BMS và PCS — https://www.infinitepowerht.com/what-is-energy-management-system-ems-and-its-functions.html (snippet, một agent; chỉ dùng cho định nghĩa chung, có nguồn thứ hai là Deye, theo K R-18).

### 10.2 Validator kế hoạch (F-OPT-07)

| Mã | Kiểm tra | Mức |
|---|---|---|
| V-01 | Horizon liên tục, ≥ 48 h, slot 15′ thẳng hàng, không chồng lấn | Chặn |
| V-02 | Mọi `slot_mode` có trong `capability_profile` của thiết bị đích; Gate M1 chỉ chế độ native | Chặn |
| V-03 | `p_ess_min_w ≥ −SOE.P_ess_ch_max`, `p_ess_max_w ≤ SOE.P_ess_dis_max` | Chặn |
| V-04 | `import_cap_w`, `export_limit_w` của slot **không nới** hơn cấu hình lưới hiệu lực | Chặn |
| V-05 | Mô phỏng quỹ đạo SOC (mô hình pin §14.2) với dự báo P50: `SOC ∈ [SOC_min_eff, SOC_max_eff]`, không dưới `soc_floor` | Chặn |
| V-06 | Không xung đột lệnh `GRID_OPERATOR` hiệu lực | Chặn |
| V-07 | Cân bằng hợp lý: \|Σ(pc·η_c − pd/η_d)·Δt − (s_N − s_0)\| ≤ 1% E_cap | Chặn |
| V-08 | Chu kỳ/ngày ≤ `cycles_per_day_max` | Chặn |
| V-09 | `GRID_CHARGE_TO_TARGET` chỉ khi `allow_grid_charge`; không có dòng pin → lưới khi `¬allow_ess_export` | Chặn |
| V-10 | Guardrail: không dưới dự phòng; năng lượng xả thay đổi ≤ 30% so với bản trước (I §3.7.6); không slot nào > 80% giới hạn SOE (nếu có → duyệt tay, C2) | Vượt → duyệt tay |
| V-11 | `input_hash` khớp snapshot; `engine_ref` khớp strategy version ACTIVE | Chặn |
| V-12 | Đầu ra số học hợp lệ: không NaN, W là số nguyên, đơn vị đúng hậu tố | Chặn |
| V-N1…V-N4 | Chỉ cho Gate M1 (lịch native): lịch phải an toàn khi lặp vô hạn (trần nhập, khung thấp điểm của mọi lịch TOU đã công bố, giới hạn SOC cuối khung, SOC sàn và giới hạn xuất native), chi tiết §6.6.3 | Chặn |

### 10.3 Những điều optimizer không bao giờ làm

- Không ghi thông số bảo vệ BMS/PCS/rơ-le/grid code (C4, không có API; F-BESS-19).
- Không gửi setpoint P cưỡng bức tới thiết bị `requires_native_fallback`; với thiết bị đó chỉ được đổi giữa chế độ native (F-SEC-15).
- Không nới `import_cap_w`, `export_limit_w`, `SOC_min_eff` hay dự phòng. Các giá trị này đến từ SOE/cấu hình lưới (C3) và chỉ người có quyền đổi.
- Không gửi lại lệnh sau `expires_at`.
- Không ra lệnh khi dữ liệu trạng thái cũ hơn ngưỡng (§7.9 bước 1).
- Không tạo lệnh điều khiển từ kết quả phát hiện bất thường ([04 BR-OPT-06](04-business-requirements.md)).

---

## 11. Vòng đời kế hoạch điều độ và thực thi

### 11.1 Máy trạng thái DispatchPlan

Theo [05 §11.4](05-domain-model.html) và [04 FR-OPT-007](04-business-requirements.md):

```
            ┌──── REJECTED (validator fail / người duyệt từ chối)
            │
DRAFT ──► VALIDATED ──► APPROVED ──► SCHEDULED ──► EXECUTING ──► COMPLETED
  ▲                      ▲  (AUTO_GUARDRAIL         │              │
  │                      │   hoặc MANUAL/           │              ├──► ABORTED (operator, lỗi thiết bị nặng,
  │                      │   TWO_PERSON)            │              │             lệnh GRID_OPERATOR dài, kill switch)
  │                                                 ├──► EXPIRED (hết horizon chưa giao, edge offline)
  └── version+1 khi giải lại / sinh lại             └──► SUPERSEDED (version mới cho cùng khoảng; chỉ slot chưa bắt đầu)
```

| Chuyển | Ai | Điều kiện / việc làm |
|---|---|---|
| → DRAFT | Tầng 2, tầng 3, người (lịch tay, P1), backtest | Lưu `input_snapshot` (TariffVersion, TouCalendarVersion, ForecastRun, SOE version, SiteGridConfigVersion, strategy version, giới hạn thiết bị, `engine_ref`) + `input_hash` |
| DRAFT → VALIDATED | Validator | §10.2 |
| VALIDATED → APPROVED | Tự động trong guardrail (`AUTO_GUARDRAIL`); người có `plan.approve` khi vượt (`MANUAL`); hai người khi lịch tay vượt guardrail ở site lớn (`TWO_PERSON`) | Bất biến từ đây |
| APPROVED → SCHEDULED | Dispatcher | PDP (C1) + Governor; đóng gói `APPLY_SCHEDULE` (`expires_at` ≤ 7 ngày, `supersedes`), ký JWS, publish |
| SCHEDULED → EXECUTING | Edge | Edge `ACCEPTED` và slot đầu bắt đầu; Gate M1: readback lịch native khớp |
| EXECUTING → COMPLETED | Edge/cloud | Hết slot cuối; tổng hợp `PlanSlotResult` |
| → SUPERSEDED | Version mới được APPROVED cho cùng khoảng | Chỉ slot chưa bắt đầu bị thay; slot đang chạy kết thúc theo bản cũ trừ khi `preempt = true` |
| → EXPIRED | Cloud | Hết horizon mà chưa từng EXECUTING |
| → ABORTED | Operator (C1), lỗi thiết bị, lệnh `GRID_OPERATOR` > 2 h, kill switch | Edge về chiến lược mặc định; ghi lý do |

### 11.2 Trình tự thực thi và xác nhận

```
Planner     Validator/PDP/Governor     Dispatcher (cloud)        Edge                         Thiết bị
  │ DRAFT v7       │                         │                      │                             │
  │──────────────► │ VALIDATED, APPROVED     │                      │                             │
  │                │───────────────────────► │ ký JWS, APPLY_SCHEDULE (cmd_id, supersedes v6)     │
  │                │                         │────── down/cmd ────► │ kiểm chữ ký/hạn/IL/SOE      │
  │                │                         │ ◄──── RECEIVED ───── │                             │
  │                │                         │ ◄──── ACCEPTED ───── │ lưu lịch (≥ 48 h, có ký)    │
  │ SCHEDULED      │                         │                      │                             │
  │                │                         │ ◄─ SLOT_STARTED ──── │ arbiter + tầng 1 ─────────► │ ghi setpoint
  │                │                         │                      │ ◄──────── readback ──────── │
  │                │                         │ ◄─ SLOT_APPLIED │ APPLIED_CLAMPED │ OVERRIDDEN(level, reason)
  │ EXECUTING      │                         │ ◄─ SLOT_ENDED + bộ đếm năng lượng slot             │
  │                │                         │   → PlanSlotResult                                 │
```

- Ack lệnh theo state machine của E §3.19 / [05 §11.2](05-domain-model.html): `SENT → RECEIVED → ACCEPTED → DISPATCHED → APPLIED | APPLIED_CLAMPED | FAILED_*`. Kế hoạch thêm ack **theo slot**: `SLOT_STARTED`, `SLOT_APPLIED`, `SLOT_APPLIED_CLAMPED`, `SLOT_OVERRIDDEN(level, reason)`, `SLOT_ENDED`.
- Không có `ACCEPTED` trong 300 s → UI "Chưa đồng bộ"; edge vẫn chạy kế hoạch cũ ([04 AC-OPT-08](04-business-requirements.md)).
- Edge offline: kế hoạch cũ (≥ 48 h) chạy tiếp; hết → chiến lược mặc định; khi online lại, edge gửi `SLOT_*` đã đệm (store-and-forward ≥ 7 ngày, K §6 #18) và cloud tính lại `PlanSlotResult`.
- `slot_status` tổng hợp: `APPLIED` nếu ≥ 90% thời gian slot không bị kẹp/ghi đè; `APPLIED_CLAMPED` nếu bị kẹp bởi mức 1/3/6 (limit chain); `OVERRIDDEN` nếu mức 4/5/7–10 thắng ≥ 10% thời gian slot. Ngưỡng 90%/10% là [PROPOSAL].

### 11.3 Thực tế so với kế hoạch (F-OPT-10)

`PlanSlotResult` (hypertable 15 phút) theo [05](05-domain-model.html): `mode_planned/actual`, `e_ess_planned_kwh/actual_kwh` (+ = xả), `soc_end_planned/actual_pct`, `e_import/export_planned/actual_kwh`, `p_demand_window_max_actual_kw`, `e_pv_curtailed_est_kwh`, `cost_planned/actual`, `slot_status`, `deviation_cause`, `reason_codes[]`. Năng lượng thực tế lấy từ delta thanh ghi tại biên slot (K §6 #5).

Phân loại `deviation_cause` (thứ tự gán, lấy nguyên nhân đầu tiên đúng):

| Thứ tự | Nguyên nhân | Quy tắc |
|---|---|---|
| 1 | `COMM_LOSS` | Edge hoặc thiết bị mất liên lạc > 10% slot |
| 2 | `HIGHER_PRIORITY_OVERRIDE(level)` | Mức 2–10 thắng ≥ 10% slot |
| 3 | `MANUAL` | Lệnh tay hiệu lực |
| 4 | `NATIVE_MODE` | Controller native không theo lịch (Gate M1) |
| 5 | `DEVICE_CLAMP` | Kẹp bởi BMS/PCS/limit chain ≥ 10% slot |
| 6 | `FORECAST_LOAD` / `FORECAST_PV` | \|tải thực − dự báo\| hoặc \|PV thực − dự báo\| lớn hơn; chọn cái có đóng góp lớn hơn vào lệch P_grid |

Phân rã lệch chi phí [PROPOSAL]: `Δcost = cost_actual − cost_planned` = phần do dự báo (giải lại cùng engine với tải/PV thực đo = "perfect hindsight") + phần do kẹp/ghi đè (phần còn lại khi các slot `APPLIED`) + phần do thiết bị/liên lạc. [INFERENCE] Đây là bằng chứng để biết nên đầu tư vào dự báo hay vào tích hợp thiết bị.

KPI điều độ: % slot `APPLIED`; MAE lệch SOC cuối slot; MAE dự báo tải trong cao điểm; số lần vi phạm xuất (= 0); kWh PV bị cắt; Pmax thực tế vs mục tiêu (P1).

---

## 12. Bản ghi giải thích ("vì sao hành động này")

### 12.1 Ba cấp giải thích

| Cấp | Người đọc | Nội dung | Phát hành |
|---|---|---|---|
| 1. Theo slot / theo quyết định | Operator (P3) | Mã lý do + câu mẫu có số liệu: "17:30–17:45: xả 180 kW vì đang giờ cao điểm (3.398 đ/kWh); dự báo đủ năng lượng tới 22:30 với dự phòng 20%." Tại edge: mức arbiter đang thắng + mã lý do | MVP (F-OPT-11, FR-OPT-002/011) |
| 2. Theo kế hoạch | Chủ C&I (P1), energy manager (P2) | Chi phí dự kiến so với baseline (a) không BESS, (b) luật tầng 2, (c) kế hoạch đang chạy; nguồn chênh lệch lớn nhất (cao điểm tránh được, PV cứu khỏi cắt, demand giảm). Luôn "≈ ước tính" | MVP cho (a) và (c); (b) khi tầng 3 chạy |
| 3. Theo mô hình | Kỹ sư (P4, P5) | Shadow price của (C4) = giá trị biên của 1 kWh trong pin theo slot (đ/kWh); dual của (C10) = giá trị của 1 kW giảm đỉnh. Với MILP: dual từ LP cố định binary | Phase 1 (F-OPT-12) |

[FACT] Huawei EMMA có panel so sánh có/không EMMA và phân tích tiết kiệm theo giá — https://support.huawei.com/enterprise/en/doc/EDOC1100376808/a3411c60/enabling-emma (nghiên cứu FusionSolar). Đây là chuẩn cạnh tranh cho cấp 2.

### 12.2 Danh mục mã lý do

| Mã | Nghĩa | Sinh bởi | Tham số trong câu mẫu |
|---|---|---|---|
| `CHARGE_PV_SURPLUS` | Sạc từ PV dư | Tầng 2/3, tầng 1 | kW, kWh PV dư dự báo |
| `CHARGE_PV_WOULD_BE_CURTAILED` | Sạc vì PV sẽ bị cắt do giới hạn xuất | Tầng 3 (`f_pb > 0` khi `Ge_max = 0` và PV > tải) | kWh cứu |
| `CHARGE_FORCED_BY_EXPORT_LIMIT` | Sạc bắt buộc để không xuất | Tầng 1 (mức 4) | P_export tránh được |
| `CHARGE_GRID_OFFPEAK_TO_TARGET` | Nạp lưới thấp điểm tới SOC đích | Tầng 2/3 | giá thấp điểm, SOC đích, phần PV ngày mai không lấp được |
| `HOLD_FOR_PEAK` | Không xả, giữ năng lượng cho cao điểm | Tầng 2/3 | giá hiện tại vs giá cao điểm |
| `DISCHARGE_PEAK_TOU` | Xả giờ cao điểm | Tầng 2/3 | giá cao điểm, giờ kết thúc, dự phòng |
| `DISCHARGE_PEAK_SHAVING` | Xả để giữ Pmax cửa sổ | Tầng 1 (mức 9) | P_allow_rest, P_target_eff |
| `IMPORT_CAP_ACTIVE` | Xả/giảm EV để giữ trần nhập | Tầng 1 (mức 5) | import_cap, P_import |
| `HOLD_BACKUP_RESERVE` | Dừng xả vì chạm dự phòng | Tầng 1 (mức 6) | SOC, dự phòng |
| `RESERVE_DIPPED_FOR_IMPORT_CAP` | Xả dưới dự phòng để giữ trần nhập | Tầng 1 (X1) | SOC, S_res_hard |
| `IDLE_SPREAD_BELOW_DEG_COST` | Không chạy chu kỳ vì chênh lệch < chi phí suy hao | Tầng 2/3 | chênh lệch, c_deg |
| `CLAMPED_BY_BMS` / `CLAMPED_BY_SOE` / `RAMP_LIMITED` | Bị kẹp | Limit chain | yêu cầu, áp dụng, giới hạn |
| `PV_CURTAILED_EXPORT_LIMIT` | Cắt PV vì giới hạn xuất | Tầng 1 | kW cắt |
| `OVERRIDDEN_BY_GRID_OPERATOR` | Lệnh điều độ ghi đè | Arbiter | nguồn, hạn |
| `MANUAL_OVERRIDE` / `MANUAL_CLAMPED_BY_GRID_LIMIT` | Lệnh tay | Arbiter | người, hạn |
| `NATIVE_MODE_ACTIVE` | Controller native đang làm chủ | Arbiter | chế độ |
| `SAFE_STATE_STALE_BMS` / `SAFE_STATE_STALE_POC` | Về trạng thái an toàn | Mức 3 | tuổi dữ liệu |
| `FALLBACK_SCHEDULE_EXPIRED` / `DEFAULT_STRATEGY` | Chạy mặc định | Mức 12 | thời điểm hết lịch |
| `TARIFF_VERSION_CHANGED` | Về hồ sơ mặc định vì biểu giá/lịch TOU mới có hiệu lực trước khi có kế hoạch mới | Edge (M1, §6.6.2) | phiên bản cũ, phiên bản mới, `valid_from` |
| `NATIVE_SCHEDULE_UNCHANGED` / `NATIVE_SCHEDULE_DRIFT` / `NATIVE_WRITE_BUDGET_EXCEEDED` | Lịch native không ghi vì trùng / bị sửa tại chỗ / hết hạn mức ghi | Edge (M1, §6.6.1) | số lần ghi trong ngày, thanh ghi lệch |
| `SOC_TARGET_UNREACHABLE` | Không đạt SOC đích | Tầng 1 | SOC đích, SOC thực |
| `EV_THROTTLED_IMPORT_CAP` / `EV_COMMITMENT` | EV bị giảm / được ưu tiên | Tầng 1 (P1) | phiên, kW |

Mã lý do là enum có version; câu mẫu tiếng Việt là dữ liệu i18n, render lúc đọc từ `reason_codes` + `explain_params`.

### 12.3 Lưu trữ

[PROPOSAL] Không tạo thực thể mới ngoài [05](05-domain-model.html):

- Cấp kế hoạch: `PlanSlot.reason_codes[]` + trường đề xuất `PlanSlot.explain_params jsonb` (giá băng, SOC đích, dự báo, shadow price) — gửi 05 (§20).
- Cấp edge: Event `ARBITER_REASON` (mức, khoảng cho phép, setpoint, mã lý do) khi thay đổi + tóm tắt 60 s.
- Cấp kết quả: `PlanSlotResult.reason_codes[]`, `deviation_cause`.
- Mọi giải thích tham chiếu `plan_id/version` và `input_hash`, nên tái lập được.

Quy tắc ngôn từ: câu mẫu không dùng "AI", "thông minh", "tự học"; số ước tính có "≈"; số mô phỏng có "Mô phỏng".

---

## 13. Phiên bản chiến lược và audit

### 13.1 Cái gì có phiên bản

| Đối tượng | Thực thể ([05](05-domain-model.html)) | Ai đổi | Hạng |
|---|---|---|---|
| Chiến lược và tham số planner | `OptimizationStrategyVersion` (DRAFT → VALIDATED → [BACKTESTED cho tầng 3] → APPROVED → ACTIVE → SUPERSEDED/RETIRED; REJECTED) | Site Engineer/Operator soạn, Control Supervisor duyệt | Nới guardrail = C3; khác = C2 |
| Biểu giá và lịch TOU | `TariffVersion`, `TouCalendarVersion` | PA/PO | Ghi cấu hình |
| Vùng vận hành an toàn | SOE | Site Engineer đề xuất, Control Supervisor duyệt, ký số | C3 |
| Cấu hình lưới | `SiteGridConfigVersion` | PS | C3 |
| Engine | `engine_ref` = `rules@x.y.z` hoặc `milp-model@x.y.z + solver@version` | Phát hành phần mềm | Quy trình release control plane |
| Kế hoạch | `DispatchPlan(plan_id, version)` | Planner | C1 trong guardrail |

Tối đa một strategy version ACTIVE cho mỗi chiến lược. Version đã APPROVED bất biến. Tầng 3 (`planner_tier = TIER3_MILP`) bắt buộc có `backtest_run_id` PASS trước APPROVED.

### 13.2 Chạy bóng (shadow mode) trước khi kích hoạt

[PROPOSAL] Strategy version mới có thể chạy ở chế độ `SHADOW` ≥ 7 ngày: planner sinh `DispatchPlan` với `origin` tương ứng nhưng **không** dispatch; so chi phí dự kiến với version ACTIVE trên cùng dữ liệu thực. Nhãn "Mô phỏng". Không có tính năng tương ứng trong 03 → ghi vào `_catalog-gaps.md`.

### 13.3 Tái lập xác định (deterministic replay)

Yêu cầu: với `input_snapshot` đã lưu và `engine_ref`, chạy lại phải cho kế hoạch giống hệt (cùng `output_hash`). Điều kiện:

- Tầng 2: không phụ thuộc giờ hệ thống ngoài `now` trong snapshot; làm tròn W cố định (half-even).
- Tầng 3: threads = 1, seed cố định, presolve cố định, phá suy biến bằng `ε_t` (§7.4). Nếu solver không cho bảo đảm bit-exact, so sánh theo dung sai (chi phí ±0,01%, mọi giá trị W ±1 W) và ghi `replay_tolerance`.
- Test CI: bộ "golden snapshot" ≥ 20 site/ngày mẫu chạy lại mỗi build.

### 13.4 Audit và lưu giữ

Theo K R-25 và [03 F-SEC-12, F-SEC-19](03-functional-catalog.html#f-sec-19):

| Bản ghi | Trực tuyến | Lưu trữ |
|---|---|---|
| Chuyển trạng thái kế hoạch, phê duyệt, lệnh `APPLY_SCHEDULE` và ack | ≥ 13 tháng | WORM ≥ 5 năm (neo WORM là P1); hợp đồng ESCO/PPA có thể tới 10 năm |
| Kế hoạch đã thực thi ≥ 1 slot (đầy đủ slot + input_snapshot) | ≥ 13 tháng | ≥ 5 năm |
| Kế hoạch bị thay trước khi chạy | Tóm tắt + `input_hash` 30 ngày | Không |
| Strategy version, SOE, cấu hình lưới (mọi version) | Vòng đời site | ≥ 5 năm |
| Event `ARBITER_REASON` | Như raw (13 tháng) | Không |
| BacktestRun | Vòng đời strategy version | — |

[INFERENCE, theo 05] Tầng 3 MPC tạo ~96 phiên bản/ngày/site ≈ 2,8 MB/ngày/site; vì thế quy tắc "bị thay trước khi chạy chỉ giữ tóm tắt" là cần thiết.

---

## 14. Mô phỏng, what-if và backtest

### 14.1 Ba loại, ba mục đích

| Loại | Câu hỏi | Người dùng | Tính năng | Phát hành |
|---|---|---|---|---|
| Backtest chiến lược | "Strategy version mới có tốt hơn version đang chạy/luật tầng 2 trên lịch sử của site này không?" | P5, P3 | F-OPT-15 | Phase 1 |
| What-if vận hành | "Nếu tăng dự phòng lên 30% / bật nạp lưới / đổi `c_deg`, chi phí tháng trước thay đổi thế nào?" | P2, P3 | F-OPT-15 (cùng engine) | Phase 1 |
| What-if định cỡ | "BESS 500 hay 1.000 kWh, 2 h hay 4 h, khung TT 16 vs QĐ 963, có/không hai thành phần?" | P4, P5, P1 | F-ADV-06 | Phase 1 |

Mọi kết quả mang nhãn "Mô phỏng", không trộn vào số đo (K §6 #33; [04 FR-ADV-002](04-business-requirements.md)).

### 14.2 Mô hình mô phỏng

[PROPOSAL] Mô hình **năng lượng**, không mô phỏng điện hóa/nhiệt:

- Pin: bucket `s[t+1] = s[t] + (η_c·pc − pd/η_d − δ)·Δt`; giới hạn P theo SOE; derate tĩnh tùy chọn theo SOC (ví dụ giảm `Pc_max` khi SOC > 90%).
- Edge: tầng 1 bám envelope với bước 1 phút (hoặc 5 phút nếu chỉ có dữ liệu 5 phút, ghi rõ); áp đầy đủ arbiter mức 4–6 và limit chain.
- Lưới: giới hạn xuất cứng; PV vượt → cắt.
- Dữ liệu vào: đo thực của site (tải dựng lại từ cân bằng `P_load = P_grid + P_pv + P_ess`, PV khả dụng ước tính khi đã bị cắt).

### 14.3 Quy tắc chống nhìn trước (no look-ahead)

- Backtest dùng **dự báo như đã có lúc đó**: `ForecastRun` có `issue_time ≤ t_plan` (dự báo lưu hai trục thời gian, không ghi đè; F-ADV-02). Site chưa có dự báo lưu: tái tạo F0/F1 chỉ từ dữ liệu trước `t_plan`.
- Chạy kèm "perfect foresight" (dữ liệu thực làm dự báo) để có **cận trên**; báo khoảng cách thực tế ↔ cận trên.
- Lịch TOU/giá theo `TariffVersion` hiệu lực tại thời điểm lịch sử, trừ khi what-if đổi biểu giá có chủ đích.

### 14.4 Cổng bật tầng 3 cho site (F-OPT-15)

[PROPOSAL] Tất cả điều kiện phải đạt:

1. Backtest ≥ 90 ngày dữ liệu đo, độ phân giải ≤ 5 phút (≤ 1 phút nếu có peak shaving).
2. Chi phí năng lượng (+ demand nếu bật) của tầng 3 thấp hơn luật tầng 2 ≥ X% (X do sản phẩm quyết, đề xuất 3%), sau khi trừ `c_deg` cho throughput tăng thêm.
3. Không tăng vi phạm: giới hạn xuất (= 0 ở cả hai), thời gian dưới dự phòng, phiên EV thiếu kWh, chu kỳ/ngày.
4. Không có lần giải nào infeasible không có fallback; p95 thời gian giải đạt NFR.
5. Chạy bóng ≥ 7 ngày trên dữ liệu thực (§13.2) không lệch hướng so với backtest.

Kết quả lưu `BacktestRun` ([05](05-domain-model.html)) với `result ∈ {PASS, FAIL}`. GAP-14: site mới không có 90 ngày lịch sử → dùng CSV lịch sử của khách nếu có, nếu không giữ tầng 2.

### 14.5 Giới hạn biết trước

- Dữ liệu 5 phút của cloud hãng làm mất đỉnh ngắn → mô phỏng peak shaving cần dữ liệu ≤ 1 phút từ edge; báo độ phân giải nguồn.
- PV khả dụng trong giờ bị cắt là **ước tính**; backtest nhạy với ước tính này ở site zero-export.
- Mô hình pin bỏ qua suy giảm theo thời gian trong kỳ backtest, nhiệt, và cân bằng cell.
- What-if định cỡ không thay thế thiết kế kỹ thuật; [INFERENCE] kết luận "BESS 4–5 h hấp dẫn hơn 2 h dưới QĐ 963" không đưa vào tài liệu bán hàng khi chưa có giá BESS VN (K §3.6).

---

## 15. Đo tiết kiệm: baseline và giới hạn trung thực

### 15.1 Định nghĩa

[PROPOSAL, K §6 #34] `Tiết kiệm = Hóa đơn_baseline_phản_thực − Hóa đơn_bóng_thực`, cả hai tính cùng `TariffVersion` (theo từng version khi đổi biểu giá giữa kỳ), ở bucket 5 phút rồi cộng lên kỳ hóa đơn. Luôn nhãn "≈ ước tính". Không hiển thị câu "% tiết kiệm" kiểu quảng cáo; chỉ hiển thị số tiền ước tính kèm phương pháp và khoảng bất định.

### 15.2 Các baseline

Theo F §3.11 (mã B0–B3 là mã tạm của F):

| Mã | Baseline | Cách tính | Cần mô phỏng? | Dùng cho |
|---|---|---|---|---|
| B0 | Không PV, không BESS | `E_imp_B0(k) = max(E_cons(k), 0)`, `E_cons = E_imp − E_exp + E_pv + E_dis − E_ch` (từ thanh ghi); Pmax_B0 từ `E_imp_B0` theo cửa sổ | **Không** | Giá trị đầu tư tổng (PV + BESS) |
| B1 | Có PV, không BESS | `E_net(k) = E_imp − E_exp + E_ch − E_dis`; tách nhập/xuất theo dấu ở 5 phút; **áp giới hạn xuất**: phần xuất vượt giới hạn coi là cắt (giá trị 0) | Có (giới hạn xuất) | Giá trị riêng của BESS |
| B2 | Chiến lược tham chiếu | Mô phỏng BESS chạy chiến lược đơn giản (self-consumption thuần hoặc luật tầng 2) trên cùng dữ liệu | Có | Giá trị của tối ưu (tầng 3 so với luật) |
| B3 | Hồi quy toàn site | Mô hình tải theo thời tiết/lịch trước–sau | Có | Ngoài phạm vi (biện pháp phía tải) |

[INFERENCE — kiến thức nền, chưa kiểm chứng] B0/B1 có đo PV/BESS/POC đầy đủ nên gần tinh thần "cô lập ranh giới" (Option B) của IPMVP. Báo cáo ghi "phương pháp tham khảo nguyên tắc IPMVP", **không** ghi "tuân thủ IPMVP" (Q-F07; K §6 #34).

### 15.3 Phân rã nguồn tiết kiệm (cho B1 → thực tế)

Dùng phân rã dòng của `attribution_version` hiện hành (backend, K §6 #11):

| Nguồn | Công thức (mỗi bucket, cộng lên kỳ) |
|---|---|
| (a) PV tự dùng trực tiếp | Có trong B1 → không tính cho BESS |
| (b) PV cứu khỏi cắt qua BESS | `E_bess_from_pv_curtail_avoided × giá(khung lúc xả)·η_d` |
| (c) Dịch chuyển TOU từ lưới | `E_dis_from_grid × giá(khung lúc xả) − E_ch_grid × giá(khung lúc sạc)` |
| (d) Dịch chuyển PV ban ngày sang cao điểm | `E_dis_from_pv_normal × (giá cao điểm) − E_pv_normal_charged × (giá bình thường)` |
| (e) Demand giảm (nếu bật) | `c_dem × (Pmax_B1 − Pmax_thực)` **chỉ ở cấp kỳ hóa đơn** |
| (f) Trừ chi phí suy hao ước tính | `− c_deg × E_dis` |

Quy tắc: không cộng (b) và (c) hai lần (năng lượng trong pin được quy kết theo sổ cái nguồn gốc, F-BESS-15, Phase 1; trước khi có sổ cái, dùng FIFO và ghi "≈ ước tính"). Tiết kiệm năng lượng có thể âm khi sạc lưới làm tăng E_imp trong khi tiết kiệm TOU dương → luôn hiển thị phân rã (F §3.11 bẫy b).

### 15.4 Ví dụ số (một ngày thứ Ba, tiếp ví dụ §6.4)

Giả định thêm: PV dư 300 kWh AC lẽ ra bị cắt (site zero-export); tải cao điểm luôn ≥ công suất xả; giá 22–<110 kV QĐ 1279; `c_deg = 556 đ/kWh` xả (giả định §16.2). **Ví dụ số, không phải kết quả đo.**

| Thành phần | Phép tính | đ/ngày |
|---|---|---|
| (b) PV cứu khỏi cắt | 285 kWh trong pin × 0,95 = 270,75 kWh xả × 3.398 | ≈ 920.009 |
| (c) TOU từ lưới | 380,48 kWh xả × 3.398 − 421,58 kWh nạp × 1.190 | ≈ 791.175 |
| Tổng trước suy hao | | ≈ 1.711.184 |
| (f) Suy hao | (270,75 + 380,48) kWh × 556 | ≈ −362.081 |
| Tiết kiệm ước tính so với B1 | | **≈ 1.349.102** |

Ý nghĩa: phần lớn giá trị đến từ PV lẽ ra bị cắt; nếu site được phép xuất PV dư với giá bán > 0, (b) giảm tương ứng.

### 15.5 Đề xuất cho GAP-05 (B0 trong MVP)

[PROPOSAL] Kéo **B0** vào MVP như một dòng trong R2 ([03 F-REP-02](03-functional-catalog.html#f-rep-02)): "Chi phí nếu không có PV và BESS ≈ X đ (ước tính)". B0 không cần mô phỏng (chỉ cần `E_cons` từ cân bằng thanh ghi và hóa đơn bóng đã có ở F-TAR-06), nên chi phí thấp và minh bạch được giá trị số 2 (TOU) ngay. B1, B2 và phân rã giữ ở Phase 1 (F-REP-07). Quyết định cuối thuộc [11 Lộ trình](11-mvp-and-roadmap.html).

### 15.6 Giới hạn trung thực (in trên trang đầu báo cáo)

1. Baseline là phản thực: không ai đo được hóa đơn "nếu không có BESS". Đây là ước tính mô hình.
2. Hóa đơn bóng không thay hóa đơn EVN; chênh lệch công tơ điều khiển vs công tơ thanh toán chưa đối soát (F-TAR-10, Phase 1).
3. Bucket có dữ liệu thiếu → `INCOMPLETE` + khoảng min/max; không nội suy Pmax.
4. B1 phụ thuộc giả định giới hạn xuất và PV khả dụng khi bị cắt (ước tính).
5. Tiết kiệm demand không cộng theo ngày; chỉ ở kỳ hóa đơn.
6. Cơ sở tính giá hai thành phần và ngày áp khung QĐ 963 vào hóa đơn là UNKNOWN; báo cáo ghi rõ lịch/biểu giá đã dùng.
7. Chi phí suy hao là tham số tuyến tính, không phải mô hình tuổi thọ pin. Không tuyên bố "tối ưu tuổi thọ pin".
8. [FACT, Low] Tuyên bố tiết kiệm của vendor (ví dụ Stem Athena "lên tới 30%") không có kiểm chứng độc lập — https://www.stem.com/wp-content/uploads/2021/05/Stem-Solutions-Overview_Athena_May-2021_v10.pdf. Sản phẩm của ta không đưa ra con số tương tự.

---

## 16. Giá trị ở Việt Nam

### 16.1 Tóm tắt (10/2026)

| Chiến lược | Tạo tiền hôm nay? | Lý do |
|---|---|---|
| Giới hạn xuất / zero-export | Gián tiếp (tuân thủ) | Đa số site không bán dư; bắt buộc với hệ trung áp không bán dư (theo tóm tắt), hạ áp UNKNOWN |
| PV → BESS thay vì cắt | **Có, lớn nhất** | PV dư lẽ ra mất → bán vào cao điểm |
| TOU arbitrage lưới (T2–T7) | **Có** | Chênh lệch cao/thấp ≈ 2,86×; cần BESS và `c_deg` hợp lý |
| Self-consumption thuần | Kém hơn TOU-aware | Xả giờ bình thường lãng phí |
| Trần nhập | Có (vận hành) | Tránh dừng sản xuất, hoãn nâng MBA |
| Peak shaving demand | Chỉ với khách thí điểm; cơ sở tính UNKNOWN | K R-16, R-17 |
| Backup reserve | Có nếu tải nhạy cảm và PCS hỗ trợ off-grid | Giá trị phi biểu giá |
| EV DLM | Có khi EV làm vượt trần MBA | Biểu giá EV riêng; khung giờ EV UNKNOWN |
| DR | UNKNOWN | Chưa thấy cơ chế trả tiền |
| Thị trường / tần số | Không (C&I BTM) | Khung giá BESS chỉ cho FTM ≥ 10 MW |

### 16.2 Giá trị của 1 kWh theo nguồn sạc

[INFERENCE] Cấp 22–<110 kV, QĐ 1279, chưa VAT; RTE = 0,9 dồn vào khâu xả; chưa trừ `c_deg`; xả trong cao điểm T2–T7. K đã tính lại các số này (K §1).

| Nguồn sạc | Chi phí cơ hội 1 kWh sạc | Giá trị khi xả (0,9 × 3.398) | Lãi / kWh sạc | Lãi / kWh xả |
|---|---|---|---|---|
| PV dư lẽ ra bị cắt | 0 | 3.058 | **3.058** | 3.398 |
| Lưới thấp điểm (1.190) | 1.190 | 3.058 | 1.868 | **2.076** |
| PV lẽ ra bù tải giờ bình thường (1.833) | 1.833 | 3.058 | 1.225 | 1.361 |
| Lưới giờ bình thường (1.833) | 1.833 | 3.058 | 1.225 | 1.361 |
| Chủ nhật: lưới thấp điểm → giờ bình thường | 1.190 | 0,9 × 1.833 = 1.650 | 460 | 511 |

Chi phí suy hao ví dụ [INFERENCE, công thức throughput tuyến tính]: `c_deg ≈ C_repl / (N_cycle × DoD)` theo kWh xả. Giả định (không có nguồn giá VN): `C_repl` = 3 triệu đ/kWh, 6.000 chu kỳ ở 90% DoD → `c_deg ≈ 3.000.000 / (6.000 × 0,9) ≈ 556 đ/kWh` xả. Với giả định này, mọi dòng trừ Chủ nhật vẫn có lãi; Chủ nhật (511 < 556) không chạy chu kỳ → mã `IDLE_SPREAD_BELOW_DEG_COST`. `c_deg` thực phải lấy từ báo giá và bảo hành của khách (Q-08-10).

Kết luận cho bộ luật: thứ tự ưu tiên sạc = **PV sắp bị cắt > lưới thấp điểm > (PV bù tải ≈ lưới giờ bình thường)** ([04 BR-OPT-03](04-business-requirements.md)).

### 16.3 Giá hai thành phần: hai kịch bản

| | Kịch bản A: `demand_basis = MEASURED_MAX` | Kịch bản B: `demand_basis = CONTRACTED` |
|---|---|---|
| Giá trị peak shaving | Trực tiếp: mỗi kW Pmax giảm = `c_dem` | Gián tiếp: cho phép đăng ký thấp hơn; vận hành phải không vượt mức đăng ký (phạt vượt UNKNOWN) |
| Thuật toán | Cửa sổ 30′ (§5.4d) + `Pk` trong MILP (2a)/(C10) | Trần nhập cứng = `P_reg − margin`; MILP dùng (2b)/(C10') |
| Sản phẩm cần | Bộ đếm Pmax kỳ đồng bộ công tơ EVN (F-GRID-09) | Công cụ đề xuất mức đăng ký từ lịch sử + định cỡ BESS (F-ADV-06) |
| Rủi ro | Một lần thất bại (mất mạng, pin lỗi) mất lợi ích cả kỳ → cảnh báo sớm khi dự báo cuối cửa sổ > mục tiêu | Đăng ký thấp + BESS lỗi → vượt đăng ký |
| Trạng thái | UNKNOWN (K R-16) | UNKNOWN (K R-16) |

[INFERENCE, K R-16] Công suất đăng ký và Pmax đo có thể cùng xuất hiện (đăng ký + phạt vượt). M-TAR hỗ trợ cả hai, tắt mặc định; peak shaving demand là Phase 1.

### 16.4 Ràng buộc pháp lý dùng trong mô hình

| Ràng buộc | Mô hình | Trạng thái |
|---|---|---|
| Trần bán dư 50% sản lượng thực phát; điện BESS xả tính vào điện dư (NĐ 58/2025 + NĐ 243/2026) | (C14) + cờ `allow_ess_export` + sổ cái nguồn gốc | [FACT, Med] theo báo ngành — https://www.reccessary.com/en/news/vietnam-solar-grid-export-dppa (qua kết quả tìm kiếm). Kỳ tính và mẫu số UNKNOWN (Q-A03) |
| Được nạp lưới rồi xả ra lưới không | `allow_grid_charge` ∧ `allow_ess_export` | UNKNOWN (Q-G09) |
| Khung TOU QĐ 963 | Lịch TOU có phiên bản | Ngày áp hóa đơn UNKNOWN (Q-A01) |
| Lịch ngày lễ (có cao điểm không) | `TouCalendarVersion` ngày đặc biệt | UNKNOWN; đã ghi trong `_catalog-gaps.md` bởi Agent F |

---

## 17. Những gì không được gọi là AI

Quy tắc dự án (K §6 #33): chỉ mô hình học đã đánh giá trên dữ liệu có nhãn mới được gọi là "ML". Không thành phần nào trong tài liệu này là AI/ML.

| Thành phần | Thực chất | Nhãn đúng trên UI/tài liệu | Cấm dùng |
|---|---|---|---|
| Tầng 1 (PI, hysteresis, cửa sổ demand, SOC guard) | Luật điều khiển xác định | "Quy tắc", "điều khiển tự động tại chỗ" | "AI", "thông minh", "tự học" |
| Arbiter 12 mức | Bảng ưu tiên cố định | "Thứ tự ưu tiên" | "AI quyết định" |
| Tầng 2 bộ sinh lịch TOU | Luật có tham số | "Quy tắc" | "AI lập lịch" |
| Dự báo F0/F1 | Thống kê (seasonal naive, median) | "Thống kê" | "AI dự báo" |
| Tầng 3 MILP/MPC | Tối ưu toán học trên dự báo | "Tối ưu dựa trên dự báo" | "AI tối ưu", "machine learning" |
| Shadow price | Đối ngẫu của LP | "Giá trị biên" | — |
| Backtest, what-if, chạy bóng | Mô phỏng | "Mô phỏng" | "dự đoán AI" |
| Chi phí suy hao tuyến tính | Tham số | "Chi phí suy hao (tham số)" | "tối ưu tuổi thọ pin" |
| Dự báo F2 gradient boosting (F-ADV-04, Phase 1) | Mô hình học | "ML" **chỉ sau** khi thắng F1 trên tập kiểm tra có phiên bản | "ML" trước khi đánh giá |

[FACT] InfinitePower dùng cụm "AI-powered EMS" mà B đánh giá là marketing (B·L12, theo [03 F-ADV-07](03-functional-catalog.html#f-adv-07)). Đây là ví dụ cần tránh.

---

## 18. Truy vết tính năng và yêu cầu

| Mục tài liệu này | Tính năng [03](03-functional-catalog.html) | Yêu cầu [04](04-business-requirements.md) | Mã tạm trong `notes/G-optimization.md` |
|---|---|---|---|
| §4 Arbiter | F-OPT-01 | FR-OPT-001, FR-OPT-002 | FR-OPT-002 (tạm) |
| §2.3, §5 Chủ vòng | F-OPT-02 | FR-OPT-003 | FR-OPT-003 (tạm) phần `control_owner` |
| §5 Tầng 1 | F-OPT-03; F-GRID-05, 06; F-BESS-10 | FR-OPT-004; FR-GRID-005, 006; FR-BESS-009 | FR-OPT-003 (tạm) |
| §6 Tầng 2 | F-OPT-04 | FR-OPT-005 | FR-OPT-004 (tạm) |
| §6, §11 Lịch dự phòng | F-OPT-05 | FR-OPT-006 | FR-OPT-005 (tạm) |
| §11 Vòng đời kế hoạch | F-OPT-06 | FR-OPT-007 | FR-OPT-006 (tạm) |
| §10.2 Validator | F-OPT-07 | FR-OPT-008 | — |
| §11 Xem kế hoạch | F-OPT-08 | FR-OPT-009 | X-G05 |
| §11.3 Thực tế vs kế hoạch | F-OPT-10 | FR-OPT-010 | FR-OPT-007 (tạm) |
| §12 Giải thích | F-OPT-11, F-OPT-12 | FR-OPT-011, FR-OPT-013 | FR-OPT-008 (tạm) |
| §7–§8 Tầng 3 | F-OPT-13 | FR-OPT-014 | FR-OPT-009 (tạm) |
| §7.2, §16.2 `c_deg` | F-OPT-14 | FR-OPT-015 | FR-OPT-010 (tạm) |
| §14 Backtest | F-OPT-15; F-ADV-06 | FR-OPT-016; FR-ADV-006 | FR-OPT-011 (tạm) |
| §3 S7, §5.4d Peak shaving | F-OPT-16; F-TAR-07; F-GRID-09, 10 | FR-OPT-017; FR-TAR-008; FR-GRID-010, 011 | FR-OPT-012 (tạm) |
| §7.5 (C14) Ngân sách xuất | F-OPT-17; F-GRID-08 | FR-OPT-018; FR-GRID-009 | FR-OPT-013 (tạm) |
| §3 S4 Dự phòng động | F-OPT-18; F-BESS-07 | FR-OPT-019; FR-BESS-006 | — |
| §3 S12 Genset | F-OPT-19 | FR-OPT-020 | — |
| §9 VPP-capable | F-OPT-20 | FR-OPT-021 | FR-OPT-016 (tạm) |
| §3 S10, S11 | F-OPT-21 (Out of scope) | — | — |
| §3 S2 Cắt PV | F-PV-03, F-PV-04 | FR-PV-003, FR-PV-004 | FR-OPT-014 (tạm) |
| §6.6 Ánh xạ native | F-BESS-04, F-GRID-04 | FR-BESS-003, FR-GRID-004 | FR-OPT-015 (tạm) |
| §3 S8 EV | F-EV-05, 06, 07 | FR-EV-005, 006, 007 | FR-EV-0xx (tạm) |
| §15 Tiết kiệm | F-REP-02, F-REP-07, F-TAR-06 | FR-REP-002, FR-REP-008, FR-REP-012; FR-TAR-006 | — |
| §6.2 Dự báo | F-ADV-01, 02, 03 | FR-ADV-001, 003, 004 | X-G09 |
| §17 Ngôn từ | F-ADV-15 (Out of scope) | FR-ADV-002; BR-OPT-04 | — |

Chi tiết FR-PV và ma trận F ↔ FR ↔ UI ↔ T đầy đủ ở [12 Truy vết](12-traceability-matrix.md).

---

## 19. Câu hỏi mở và rủi ro

Mã `Q-08-xx`/`R-08-xx` là mã cục bộ; [13](13-open-questions-and-risks.md) cấp `Q-NN`/`R-NN` chính thức.

### 19.1 Câu hỏi mở

| Mã | Câu hỏi | Ảnh hưởng | Cách xác minh | Gốc |
|---|---|---|---|---|
| Q-08-01 | Tên và tham số chính xác các controller OpenEMS ngoài `PeakShaving`/`Balancing` (giới hạn xả, dự phòng khẩn cấp, ToU, GridOptimizedCharge, EVCS) | Ánh xạ chiến lược khi edge dựa trên OpenEMS | Đọc `io.openems.edge.controller.*` trong repo | Q-G01 |
| Q-08-02 | Chế độ ESS Victron và hành vi watchdog Mode 2/3 khi mất master | Driver Victron, fallback | Tài liệu ESS Victron + lab | Q-G02, GAP-02 |
| Q-08-03 | Huawei C&I có chạy TOU + capacity control đồng thời không; thứ tự ưu tiên native | Tránh hai lớp điều khiển đánh nhau ở Gate M1 | Manual + lab | Q-G03 |
| Q-08-04 | Giấy phép và binding Java của HiGHS, OR-Tools (và backend đóng gói kèm), ojAlgo, SCIP, Timefold | Chặn ADR-OPT | File LICENSE của bản phát hành | Q-G04 |
| Q-08-05 | Thời gian giải thực tế (LP/MILP, 192 slot, 0–20 phiên EV) với dữ liệu site thật | NFR hiệu năng | Benchmark Phase 1 | Q-G05 |
| Q-08-06 | Cơ sở tính giá hai thành phần; block/rolling; khung áp dụng; phạt vượt đăng ký | Thuật toán S7, giá trị BESS | Văn bản thí điểm; hóa đơn song song | Q-G06, GAP-03 |
| Q-08-07 | Ngày khung QĐ 963 áp vào hóa đơn sản xuất và EV | Lịch đúng | Hóa đơn thực | Q-A01, GAP-04 |
| Q-08-08 | Chương trình DR có trả tiền cho C&I ở VN | Ưu tiên tầng 4 | Văn bản EVN/BCT | Q-G08 |
| Q-08-09 | Được nạp lưới rồi xả ra lưới không; cách quy kết điện BESS xả (NĐ 243) | Cờ chính sách, sổ cái nguồn gốc | Văn bản hướng dẫn | Q-G09 |
| Q-08-10 | Giá BESS C&I ở VN và cycle life thực tế để đặt `c_deg` mặc định | Quyết định arbitrage, Chủ nhật | Báo giá, datasheet, bảo hành | Q-G10 |
| Q-08-11 | Chu kỳ cập nhật OCPP tối thiểu các bộ sạc phổ biến ở VN chấp nhận | EV DLM | Lab | Q-G11 |
| Q-08-12 | Bằng chứng tiết kiệm độc lập cho BESS C&I dưới TOU | Định vị, ROI | Nghiên cứu độc lập | Q-G12 |
| Q-08-13 | Kp/Ki và margin zero-export điển hình theo loại inverter/logger | Commissioning | Test bước tải tại hiện trường | Mới |
| Q-08-14 | Điện lực có chấp nhận vòng zero-export phần mềm thay rơ-le ở hạ áp | Kiến trúc S1 | Hỏi PC; VBHN 52 | Q-A09, GAP-12 |

### 19.2 Rủi ro

| Mã | Rủi ro | Khả năng · Tác động | Giảm thiểu |
|---|---|---|---|
| R-08-01 | Dự báo PV sai làm nạp lưới thừa → mất chỗ cho PV dư, hoặc thiếu năng lượng cao điểm | Trung bình · Trung bình | `α`, space reserve, lần sinh 16:30, `deviation_cause`, Phase 1 P10/P50 |
| R-08-02 | Lịch TOU sai ngày áp → xả sai giờ, hóa đơn bóng sai | Trung bình · Cao | Hai lịch song song; cảnh báo khi khác; đối soát hóa đơn |
| R-08-03 | Hai vòng điều khiển (native + edge) dao động | Thấp · Cao | `control_owner`, từ chối cấu hình (AC-OPT-05), Q-08-03 |
| R-08-04 | Kế hoạch MPC "lật" liên tục làm mất lòng tin | Trung bình · Trung bình | `λ_stab`, `ε_t`, cửa sổ đóng băng, giới hạn số lần sinh |
| R-08-05 | Quảng cáo tiết kiệm bị hiểu thành cam kết | Trung bình · Cao (pháp lý, uy tín) | Chỉ M&V có nhãn; không % quảng cáo; trang phương pháp |
| R-08-06 | Lỗi đơn vị/dấu (W vs kW, nhập vs xuất) trong envelope | Thấp · Cao | Hậu tố đơn vị, V-12, phép thử dấu commissioning, golden snapshot |
| R-08-07 | Solver/giấy phép không phù hợp phát hiện muộn | Thấp · Trung bình | `SolverPort`, kiểm chứng Q-08-04 trước Phase 1 |
| R-08-08 | Một lần thất bại peak shaving mất lợi ích cả tháng | Trung bình · Trung bình (chỉ khách thí điểm) | Cảnh báo sớm; fallback native capacity control |
| R-08-09 | Thiếu lịch sử để backtest (site mới) làm tầng 3 không bao giờ bật | Cao · Thấp | Nhập CSV lịch sử; giữ tầng 2 (GAP-14) |
| R-08-10 | Gate M1: lịch native lặp vô hạn trên thiết bị khi edge chết, nên nạp lưới/xả theo khung TOU cũ sau khi biểu giá đổi (rủi ro kinh tế/hợp đồng, không phải bảo vệ) | Thấp · Trung bình | Chỉ ghi khi đổi; hồ sơ native mặc định khi hết hạn/đổi biểu giá; V-N1…V-N4; cảnh báo `EDGE_OFFLINE_NATIVE_SCHEDULE_ACTIVE`; runbook tới hiện trường (§6.6); liên quan [13 R-15](13-open-questions-and-risks.md)/Q-31 (mòn NVM) |

---

## 20. Vấn đề gửi agent khác

| Mã | Gửi | Vấn đề | Đề xuất |
|---|---|---|---|
| X-08-01 | 05 Domain | Câu mẫu giải thích cần tham số | Thêm `PlanSlot.explain_params jsonb` và `PlanSlot.shadow_soc_vnd_per_kwh` (P1); thêm giá trị `SHADOW` cho chế độ chạy của `OptimizationStrategyVersion` hoặc một cờ `run_mode ∈ {ACTIVE, SHADOW}` |
| X-08-02 | 05 Domain / 07 Tích hợp | Ack theo slot của `APPLY_SCHEDULE` | Thống nhất tên sự kiện `SLOT_STARTED`, `SLOT_APPLIED`, `SLOT_APPLIED_CLAMPED`, `SLOT_OVERRIDDEN(level, reason)`, `SLOT_ENDED` và quy tắc `slot_status` 90%/10% (§11.2) |
| X-08-03 | 06 Kiến trúc | ADR-OPT | Phương án A (OR-Tools Java + `SolverPort`) trước; B (Python sidecar) chỉ khi benchmark không đạt; điều kiện chặn Q-08-04 (§8.4) |
| X-08-04 | 04 Yêu cầu | NFR ứng viên | Giải 1 site ≤ 30 s p95; toàn bộ site ≤ 5 phút/chu kỳ 15′; tái lập xác định theo `engine_ref` (§7.8, §13.3) |
| X-08-05 | 09 UX/UI | Màn kế hoạch 48 h | Hiển thị mã lý do và câu mẫu theo slot, mức arbiter đang thắng, nhãn "Quy tắc"/"Tối ưu dựa trên dự báo"/"Mô phỏng"; so sánh baseline B0 |
| X-08-06 | 10 An toàn | Chuỗi 7 lớp (§10.1) và danh sách "optimizer không bao giờ làm" (§10.3) | Đưa vào test an toàn; thêm bảy ca §5.8 (T-FR-GRID-005-01 … T-FR-OPT-003-01, mã cũ T1-01…T1-07) và ba ca §6.6.4 (T-FR-BESS-003-01…03) vào chiến lược kiểm thử |
| X-08-07 | 11 Lộ trình | GAP-05 | Đề xuất B0 vào MVP trong R2 (§15.5); tầng 3 Phase 1 có cổng backtest (§14.4) |
| X-08-08 | 13 Rủi ro | Q-08-01…14, R-08-01…10 | Cấp mã chính thức; R-08-10 (lịch native lặp vô hạn ở M1) là rủi ro tồn dư mới. **Đã đóng vòng sửa:** 13 cấp R-54; 05 §11.5 thêm `native_default_profile`, `native_schedule_max_writes_per_day`, `DispatchPlan.tariff_version_id`/`tou_calendar_version_id`/`valid_until`; tên trường slot theo 05: `soc_floor` → `soc_floor_pct`, `soc_ceiling` → `soc_ceiling_pct`, `soc_target_end` → `soc_target_pct` |
| X-08-09 | 14 Nguồn | URL ở §21 | Cấp S-id |
| X-08-10 | Orchestrator | Hạn mức WebSearch hết | Lượt kiểm chứng: Q-08-01, 02, 04, 06, 08, 12 |

---

## 21. Nguồn

Mọi URL dưới đây đã xuất hiện trong ghi chú nghiên cứu (`notes/`) hoặc nghiên cứu FusionSolar trước. Tài liệu này không mở trực tiếp URL nào; nội dung được ghi nhận "(qua kết quả tìm kiếm)" trừ khi ghi khác. [14 Nguồn](14-source-register.md) sẽ cấp S-id.

**Vendor, sản phẩm và tham chiếu kỹ thuật**

- Schneider EcoStruxure Microgrid Advisor — https://www.se.com/us/en/product-range/65896/ ; https://download.schneider-electric.com/doc/998-20080341_US/EcoStruxure%20Microgrid%20Advisor%20Handout.pdf
- Huawei SmartLogger5000B/SmartMGC5000B (≤ 2 s / ≤ 5 s, tự công bố) — https://www.photomate.eu/smartlogger5000b ; https://solar.huawei.com/admin/asset/v1/pro/view/bb9458d9373d4502912378db3cbc7f2d.pdf
- Độ trễ zero-export — https://help.autarco.com/en/hardware/why-am-i-still-exporting-while-i-have-set-my-pv-system-to-zero-export-
- Huawei FusionSolar app manual (chế độ ESS) — https://e-solarshop.ro/wp-content/uploads/2025/07/fusionsolar-app-manual5925.pdf (nghiên cứu FusionSolar)
- Huawei Northbound V6 (`ch_discharge_model`, VPP API) — https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/imaster-neteco-v600r022c00-northbound-interface-reference-v6.pdf (nghiên cứu FusionSolar)
- Thư viện cộng đồng `huawei_solar` — https://github.com/wlcrs/huawei_solar/blob/main/services.yaml (mã nguồn cộng đồng)
- Huawei EMMA — https://solar.huawei.com/en/products/EMMA ; https://support.huawei.com/enterprise/en/doc/EDOC1100376808/a3411c60/enabling-emma
- Ampowr Cosmos (nguồn hạt giống) — https://ampowr.com/energy-management-system-ems/ ; https://ampowr.com/hoge-duin-hotel-enhances-energy-efficiency-with-ampifarm-peak-shaving/ ; https://ampowr.com/energy-management-system-ems/peak-shaving/ ; https://ampowr.com/battery-energy-storage-systems/battery-energy-storage-system-generator-steering/ ; https://ampowr.com/case-study-gebroeders-van-pinxteren/
- InfinitePower (nguồn hạt giống; FACT Low, chỉ định nghĩa chung, K R-18) — https://www.infinitepowerht.com/what-is-energy-management-system-ems-and-its-functions.html
- Deye: phân vai BMS/EMS/PCS — https://deye.com/nl/blog/bms-vs-ems-vs-pcs-bess-components/
- OpenEMS — https://openems.github.io/openems.io/openems/latest/edge/architecture.html ; https://github.com/OpenEMS/openems/tree/develop/io.openems.edge.controller.ess.balancing ; https://community.openems.io/t/ess-that-can-talk-with-openems-using-modbus-tcp/1029 ; https://github.com/OpenEMS/openems/pull/3973
- Victron ESS Mode 2/3 (diễn đàn, Low–Med) — https://communityarchive.victronenergy.com/questions/95889/multipluss-ii-is-external-control-ess-mode-2-or-3%EF%B9%96childToView=102991.html
- Siemens SICAM MGC — https://assets.new.siemens.com/siemens/assets/api/uuid:4b32eeee-ee7c-423e-94f1-ae6a4257a689/MicrogridControlBrochure.pdf
- OCPP smart charging — https://www.bender.de/docs/charge-controller/OCPP/ocpp-smart-charging/ ; https://developer.easee.com/docs/ocpp-smart-charging
- OpenADR 3.0 — https://www.openadr.org/assets/OpenADR%20Webinar%20Nov%202023%20-%20From%202.0%20to%203.0.pdf
- Stem Athena (tuyên bố vendor, Low) — https://www.stem.com/wp-content/uploads/2021/05/Stem-Solutions-Overview_Athena_May-2021_v10.pdf

**Việt Nam: pháp lý, biểu giá, thị trường**

- QĐ 963/QĐ-BCT (khung TOU) — https://thuvienphapluat.vn/van-ban/Tai-nguyen-Moi-truong/Quyet-dinh-963-QD-BCT-2026-khung-gio-cao-diem-thap-diem-cua-he-thong-dien-quoc-gia-703327.aspx ; https://tuoitre.vn/bo-cong-thuong-chinh-thuc-thay-doi-khung-gio-tinh-gia-dien-buoi-toi-la-gio-cao-diem-2026042410430101.htm
- QĐ 1279/QĐ-BCT (giá điện) — https://thuvienphapluat.vn/phap-luat-nha-dat/toan-van-quyet-dinh-1279-qd-bct-2025-quy-dinh-ve-gia-ban-dien-3357.html
- Giá hai thành phần (thí điểm, chu kỳ tích phân 30 phút) — https://tapchicongthuong.vn/thi-diem-ap-dung-gia-dien-hai-thanh-phan-tu-1-1-2026-218800.htm ; https://daibieunhandan.vn/trien-khai-thu-nghiem-gia-ban-le-dien-hai-thanh-phan-tu-thang-10-2025-10390577.html
- Số hệ đăng ký bán dư — https://vietnamnet.vn/en/rooftop-solar-saves-billions-of-dong-but-one-bottleneck-remains-2552186.html
- NĐ 243 (trần 50%, BESS xả) — https://www.reccessary.com/en/news/vietnam-solar-grid-export-dppa
- VBHN 52 (NĐ 58 + NĐ 243) — https://storage-vnportal.vnpt.vn/gov-tnn/7350/FileQuanTriTinTuc/VBHN%2052%20Nghi%20dinh%2058%20va%20ND%20243%2030.6.pdf
- Biểu giá trạm sạc EV — https://vneconomy.vn/automotive/quy-dinh-moi-ve-gia-ban-dien-cho-tram-sac-xe-dien.htm
- TT 62/2025 (BESS độc lập FTM) — https://arcusenergyasia.com/resources/regulations/circular-62

**Không có URL (kiến thức nền, chưa kiểm chứng):** giấy phép và binding Java của HiGHS, OR-Tools, ojAlgo, CBC, SCIP, Timefold, Gurobi/CPLEX; nguyên tắc IPMVP; công thức chi phí suy hao tuyến tính.
