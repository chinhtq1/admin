# 12 — Ma trận truy vết yêu cầu → tính năng → module → dữ liệu → API → UI → kiểm thử

[← Mục lục](index.html) · [00 Tóm tắt](00-executive-summary.html) · [03 Chức năng](03-functional-catalog.html) · [04 Yêu cầu](04-business-requirements.md) · [05 Domain](05-domain-model.html) · [06 Kiến trúc](06-system-architecture.html) · [07 Tích hợp](07-device-integration.md) · [08 Tối ưu](08-energy-optimization.md) · [09 UX/UI](09-ux-ui-specification.html) · [10 An toàn](10-security-and-reliability.md) · [11 Lộ trình](11-mvp-and-roadmap.html) · [13 Rủi ro](13-open-questions-and-risks.md) · [14 Nguồn](14-source-register.md) · [15 Mô phỏng](15-simulators-and-messaging.md)

| Thuộc tính | Giá trị |
|---|---|
| Tài liệu | 12 · Ma trận truy vết (Traceability Matrix) |
| Người viết | Agent Traceability Analyst |
| Phiên bản | 1.1 |
| Ngày | 2026-10-10 |
| Trạng thái | Bản nháp vòng fix. Dựng từ 03–10 (bản ngày 2026-10-10) và quyết định của Evidence Judge ([K-review-round1](notes/K-review-round1.md)). Vòng fix: thêm cột "Lộ trình (11)" lấy từ [11 §2.3, §6.3, §7.2, §8.2, §9.2](11-mvp-and-roadmap.html#s2-3); áp CF-28/CF-29/D-03 của [13](13-open-questions-and-risks.md); đồng bộ với bản 04 mới (FR-BESS-020, FR-INT-031, FR-SEC-006/007/013 ở Gate M1). Phần đối chiếu NFR mã đề xuất (§4.2, §6.4) chưa dựng lại đầy đủ theo việc 04 đã xác nhận các mã đó (§6.8). |
| Phạm vi | 268 FR (toàn bộ FR của 04), **85 NFR** của 04 (70 của bản dựng ban đầu + 15 mã 04 bản mới xác nhận, gồm 14 mã từ 10 và NFR-SEC-033), **270** tính năng của 03, 36 trang UI của 09, **111** API của 06 (thêm 13 endpoint ở vòng nhất quán 2026-10-10), các thực thể của 05. Vòng nhất quán 2026-10-10: §4.1 đủ 85 NFR, §6.6 cập nhật API cho thực thể P1 và EV, cột Test dẫn môi trường virtual site của [15](15-simulators-and-messaging.md). |

---

## Mục lục

- [0. Cách đọc tài liệu](#0-cách-đọc-tài-liệu)
- [1. Tóm tắt độ phủ](#1-tóm-tắt-độ-phủ)
- [2. Chiến lược kiểm thử và quy ước mã T-](#2-chiến-lược-kiểm-thử-và-quy-ước-mã-t-)
- [3. Ma trận FR theo module](#3-ma-trận-fr-theo-module)
- [4. Ma trận NFR](#4-ma-trận-nfr)
- [5. Truy vết API → UI (suy ra)](#5-truy-vết-api--ui-suy-ra)
- [6. Phân tích độ phủ và khoảng trống](#6-phân-tích-độ-phủ-và-khoảng-trống)
- [7. Sổ khoảng trống GAP-12](#7-sổ-khoảng-trống-gap-12)
- [8. Vấn đề gửi agent khác](#8-vấn-đề-gửi-agent-khác)
- [9. Cách duy trì ma trận](#9-cách-duy-trì-ma-trận)
- [10. Nguồn](#10-nguồn)

---

## 0. Cách đọc tài liệu

### 0.1 Chuỗi truy vết

`FR/NFR (04)` → `F- (03)` → `M- (module)` → `thực thể (05)` → `API- (06)` → `UI- (09)` → `T-<FR id> (12)` → `Hạng phát hành (04/03)` → `Phase lộ trình (11)`.

| Cột | Nguồn | Cách lấy |
|---|---|---|
| FR, ưu tiên, hạng lệnh, Gate | [04 §5](04-business-requirements.md#5-yêu-cầu-theo-module) | Chép nguyên bảng FR của 04. Phần "Yêu cầu (tóm tắt)" cắt ở khoảng 95 ký tự; nội dung đầy đủ ở 04. |
| F- | [04 §5](04-business-requirements.md#5-yêu-cầu-theo-module), cột F- | Chép nguyên. |
| Module | Tiền tố của FR và của các F- | Module đầu là module sở hữu FR. |
| Thực thể (05) | [05 §4–§14](05-domain-model.html), [05 §21](05-domain-model.html) | 12 chọn thực thể FR đọc hoặc ghi. Tên viết đúng như 05. `⚠ Tên (05 thiếu)` là thực thể FR cần nhưng 05 chưa mô hình hóa. |
| API (06) | [06 §13.2](06-system-architecture.html) | Mã không dấu: 06 ghi F- của FR trong cột "Tính năng" của API. `+API-…`: API phù hợp nhưng 06 chưa ghi F- đó. `⚠ …`: 06 chưa có endpoint. `—`: không cần REST (MQTT, edge cục bộ, hạ tầng). |
| UI (09) | [09 §13.1](09-ux-ui-specification.html) | Mã không dấu: 09 ghi FR này cho trang. `+UI-…`: trang có hoặc nên có nội dung này nhưng 09 §13.1 chưa ghi. `⚠ 09 chưa ghi`: FR chưa có trong 09 §13.1 nhưng có trang phù hợp (đi kèm `+UI-…`). `⚠ chưa có trang`: cần trang hoặc tab mới. `—`: backend, không cần UI. |
| Test | 12 (mới), dựa trên AC của 04, ca của [07 §11](07-device-integration.md), [08 §5.8](08-energy-optimization.md), [10 §19](10-security-and-reliability.md) | `T-<FR id>` · loại · kịch bản ngắn. AC và mã test có sẵn được trích trong ngoặc. |
| Hạng phát hành | 04 §0.2, 03 | `MVP/M1`, `MVP/M2`, `hạng 03: Phase 1`, `hạng 03: Phase 2`, `Không bao giờ (C4)`. Quy tắc ở §0.3. |
| Lộ trình (11) | [11 §2.3](11-mvp-and-roadmap.html#s2-3), §6.3, §7.2, §8.2, §9.2 | `Phase 1`…`Phase 4` của lộ trình, kèm track (`3A`…`4H`) và `có điều kiện`. `⚠` = 12 xếp theo quy tắc §2.3 của 11 vì 11 chưa ghi FR hoặc 11 lệch với 04 mới. |

### 0.2 Nhãn bằng chứng

- Mọi ánh xạ trong ma trận là `[INFERENCE]`: suy ra từ các tài liệu 03–10 của dự án, không từ nguồn ngoài. Nguồn gốc của từng ánh xạ là tài liệu nêu ở §0.1.
- Mọi kịch bản kiểm thử, đề xuất sửa và mã `GAP-12-NN` là `[PROPOSAL]`.
- Số liệu ngưỡng trong kịch bản (5 s, 60 s, 13 tháng…) lấy từ 04/10 và vẫn là `[PROPOSAL]` của các tài liệu đó. Một số tham số phụ thuộc pháp lý (kỳ tính ngân sách xuất 50%, cơ sở giá hai thành phần, xử lý ngày lễ trong lịch TOU) là `[UNKNOWN]` theo K §6 #37. Test của chúng phải nhận tham số, không cố định giá trị.
- Tài liệu này không trích nguồn ngoài và không có lượt tìm kiếm mới. Ngân sách tìm kiếm chung đã hết (K, mục đầu).

### 0.3 Quy tắc cột "Hạng phát hành" và "Lộ trình (11)"

Hai hệ đặt tên cùng dùng chữ "Phase" (13 CF-29). Tài liệu này luôn ghi rõ: `hạng 03: Phase n` là hạng phát hành của 03/04 ("Later (Phase 1/2)"); `Phase n` trong cột "Lộ trình (11)" là phase của [11](11-mvp-and-roadmap.html). Khi trích ở chỗ khác, viết "hạng 03: Phase 1" hoặc "lộ trình: Phase 1".

**Cột "Hạng phát hành" (theo 04/03):**

- P0 có Gate `M2` trong cột "Hạng·Gate" của 04 → `MVP/M2`: chỉ bật theo site sau khi hồ sơ sẵn sàng M2 đạt (FR-SEC-021).
- P0 khác → `MVP/M1`. Gồm FR-SEC-006, FR-SEC-007 (phân hạng C0–C4 và duyệt C3, kéo lên Gate M1 theo 13 CF-28/D-03 và 04 bản mới) và FR-SEC-013 (kill switch, 04 bản mới ghi `C1/C3·M1`).
- Một ngoại lệ 12 xếp vào `MVP/M2` dù 04 ghi `—`: FR-OPT-002 (báo trạng thái arbiter), vì chỉ có nghĩa khi edge làm chủ vòng; 11 §2.3 cũng xếp FR này vào lộ trình Phase 2. FR-SEC-016 (chặn setpoint tới thiết bị không có watchdog) nay là `MVP/M1` theo 11 §6.3: quy tắc PDP có từ Phase 1, dù ở M1 chưa có setpoint cưỡng bức nào.
- P1 → `hạng 03: Phase 1`, P2 → `hạng 03: Phase 2`, thêm `/M1` hoặc `/M2` nếu là tính năng điều khiển. CẤM → `Không bao giờ (C4)`.

**Cột "Lộ trình (11)":**

| Hạng ở 03/04 | Lộ trình (11 §2.3) | Số FR trong 12 |
|---|---|---|
| MVP, không gắn Gate M2 | Phase 1, trừ FR-OPT-002 → Phase 2; cộng FR-SEC-006/007 (CF-28) và FR-BESS-011 (ràng buộc C4) | 135 theo 11, cộng 3 FR `⚠` (dưới đây) = 138 |
| MVP, Gate M2 | Phase 2 | 10: 13 FR của 04 gốc trừ FR-SEC-006/007 (11 đã kéo lên Phase 1) và FR-SEC-013 (12 xếp Phase 1 `⚠`). Cộng FR-OPT-002 → 11 FR hạng MVP ở Phase 2 |
| hạng 03: Phase 1 (P1) | 26 FR → Phase 2; 3 FR → Phase 2 có điều kiện; 66 FR → Phase 3 (track 3A…3K) | 95. Lộ trình Phase 2 = 11 + 26 = 37, cộng 3 có điều kiện |
| hạng 03: Phase 2 (P2) | Phase 4 (track 4A…4H) | 24 |
| CẤM | Không xây chức năng; ràng buộc chặn có từ Phase 1 | 1 (FR-BESS-011) |

Ba FR mang `⚠` vì 11 (bản 07:15) chưa theo kịp 04 (bản 07:52):

- FR-BESS-020 (SOE tối thiểu Gate M1) và FR-INT-031 (lệnh `COMMISSIONING_TEST`) là FR mới của 04, 11 chưa ghi. 12 xếp Phase 1 theo quy tắc "MVP không gắn M2".
- FR-SEC-013 (kill switch): 04 nay ghi Gate M1, nhưng 11 §6.3 không có và §7.2 vẫn để ở Phase 2. 12 xếp Phase 1 vì M1 đã có lệnh ghi (cấu hình native, lịch native, OTA). Cần 11 sửa (§8).

---

## 1. Tóm tắt độ phủ

| Module | FR | P0 / P1 / P2 / CẤM | Có UI theo 09 §13.1 | Có UI sau đối chiếu của 12 | Backend, không cần UI | Chưa có trang | FR có ⚠ API | FR có ⚠ thực thể | Test U / I / S / H / E |
|---|---|---|---|---|---|---|---|---|---|
| M-ORG | 18 | 12 / 5 / 1 / 0 | 15 | 16 | 0 | 2 | 1 | 2 | 4 / 10 / 0 / 0 / 4 |
| M-DASH | 13 | 8 / 4 / 1 / 0 | 11 | 13 | 0 | 0 | 0 | 1 | 3 / 2 / 0 / 0 / 8 |
| M-MON | 13 | 10 / 3 / 0 / 0 | 11 | 11 | 2 | 0 | 1 | 0 | 4 / 2 / 4 / 1 / 2 |
| M-HIST | 17 | 11 / 6 / 0 / 0 | 6 | 11 | 5 | 1 | 0 | 0 | 7 / 6 / 2 / 0 / 2 |
| M-REP | 19 | 8 / 11 / 0 / 0 | 19 | 19 | 0 | 0 | 2 | 0 | 10 / 6 / 0 / 0 / 3 |
| M-TAR | 12 | 7 / 4 / 1 / 0 | 12 | 12 | 0 | 0 | 1 | 2 | 9 / 3 / 0 / 0 / 0 |
| M-BESS | 20 | 11 / 7 / 1 / 1 | 12 | 17 | 0 | 3 | 1 | 0 | 7 / 2 / 6 / 5 / 0 |
| M-PV | 13 | 5 / 5 / 3 / 0 | 12 | 12 | 0 | 1 | 1 | 0 | 6 / 1 / 4 / 1 / 1 |
| M-GRID | 19 | 8 / 9 / 2 / 0 | 10 | 16 | 0 | 3 | 5 | 0 | 6 / 1 / 5 / 6 / 1 |
| M-EV | 10 | 1 / 7 / 2 / 0 | 6 | 8 | 0 | 2 | 2 | 0 | 3 / 1 / 6 / 0 / 0 |
| M-OPT | 21 | 11 / 8 / 2 / 0 | 16 | 19 | 0 | 2 | 3 | 1 | 7 / 4 / 6 / 2 / 2 |
| M-ALM | 22 | 11 / 11 / 0 / 0 | 20 | 22 | 0 | 0 | 3 | 3 | 6 / 8 / 3 / 1 / 4 |
| M-INT | 31 | 21 / 7 / 3 / 0 | 19 | 25 | 3 | 3 | 0 | 3 | 1 / 11 / 12 / 5 / 2 |
| M-SEC | 28 | 22 / 4 / 2 / 0 | 21 | 21 | 6 | 1 | 0 | 1 | 4 / 14 / 5 / 2 / 3 |
| M-ADV | 12 | 2 / 4 / 6 / 0 | 2 | 3 | 0 | 9 | 10 | 3 | 8 / 3 / 0 / 1 / 0 |
| **Tổng** | **268** | **148 / 95 / 24 / 1** | **192** | **225** | **16** | **27** | **30** | **16** | **85 / 74 / 53 / 24 / 32** |

Đọc bảng:

- "Có UI sau đối chiếu" gồm trang do 09 ghi và trang 12 thêm (`+UI`). Cộng với "Backend" và "Chưa có trang" luôn bằng tổng FR.
- 76 FR (28%) không có trang trong 09 §13.1. Trong đó 16 là backend hợp lệ, 33 có chỗ trên trang có sẵn nhưng 09 chưa ghi truy vết, 11 FR P1 chưa có trang, 16 FR P2 chưa có trang (§6.1).
- 30 FR có endpoint thiếu ở 06 (41 ở bản trước; vòng nhất quán 2026-10-10 thêm API cho thực thể P1 và nhóm API-EV, §6.6). FR-ALM-008 và FR-ADV-001 (P0) đã có API-ALM-09/10 và API-FC-01.
- 16 FR cần thực thể 05 chưa có, tổng cộng 15 thực thể (§6.5).
- 1 thực thể của 05 không FR nào dùng: `AssetHealthStatus` (§6.5).
- 7 F- của 03 không có FR do nằm ngoài phạm vi (04 §5.16, chủ ý). Thêm 6 F- mới từ `_catalog-gaps` chưa có FR riêng (§6.3, 04 §7.1).
- Mọi API của 06 có ít nhất một FR dùng. API-AUD-04 không có FR riêng (§6.6).
- 21 FR điều khiển (C1–C3) thiếu NFR an toàn hoặc NFR hành vi khi lỗi riêng, không FR nào là P0. Khoảng trống P0 cũ của lệnh thử commissioning (FR-INT-016…018) đã đóng bằng FR-INT-031 và NFR-SEC-033 của 04 bản mới (§6.4).
- 11 FR Gate M1 dựa vào NFR mà bản trước của 12 (và 11 §6.3) gắn Gate M2: NFR-SEC-008, NFR-SEC-009, NFR-SEC-013. 04 bản mới đã đưa ba NFR này về M1; 11 chưa theo (§6.4.1).
- 107/107 AC của 04 đã gắn vào ít nhất một `T-`. 47 FR P0 không có AC ở 04 và không có ca test ở 07/08/10. Kịch bản của chúng chỉ có ở tài liệu này (§6.7).

**FR theo phase lộ trình (cột "Lộ trình (11)").** Phase 1 gồm 3 FR `⚠` (§0.3). "P2 đk" là Phase 2 có điều kiện; FR-INT-021 có thể sang Phase 3 (3J).

| Module | Phase 1 | Phase 2 | Phase 2 đk | Phase 3 | Phase 4 |
|---|---|---|---|---|---|
| M-ORG | 12 | 3 | 0 | 2 | 1 |
| M-DASH | 8 | 0 | 0 | 4 | 1 |
| M-MON | 10 | 1 | 0 | 2 | 0 |
| M-HIST | 11 | 3 | 0 | 3 | 0 |
| M-REP | 8 | 3 | 0 | 8 | 0 |
| M-TAR | 7 | 1 | 0 | 3 | 1 |
| M-BESS | 9 | 4 | 0 | 6 | 1 |
| M-PV | 5 | 2 | 0 | 3 | 3 |
| M-GRID | 7 | 1 | 1 | 8 | 2 |
| M-EV | 1 | 0 | 0 | 7 | 2 |
| M-OPT | 8 | 3 | 0 | 8 | 2 |
| M-ALM | 11 | 8 | 0 | 3 | 0 |
| M-INT | 20 | 2 | 2 | 4 | 3 |
| M-SEC | 19 | 6 | 0 | 1 | 2 |
| M-ADV | 2 | 0 | 0 | 4 | 6 |
| **Tổng** | **138** | **37** | **3** | **66** | **24** |

---

## 2. Chiến lược kiểm thử và quy ước mã T-

### 2.1 Loại kiểm thử

| Loại (cột Test) | Phạm vi | Tương ứng | Chạy khi | Chặn |
|---|---|---|---|---|
| Đơn vị (U) | Hàm thuần: máy trạng thái delta, TOU, KPI, PDP, validator, định dạng | 07 L1; 06 §16 "Tái lập tính toán" | Mỗi commit | Merge |
| Tích hợp (I) | Dịch vụ + DB + broker thật trong container; hợp đồng REST/MQTT; cross-tenant | 07 L2; 06 §16 "Hợp đồng", "Cross-tenant" | Mỗi commit/build | Merge, release |
| Mô phỏng (S) | Edge thật + driver + thiết bị ảo (Modbus, SunSpec, OCPP, master IEC 104), tiêm lỗi. Chạy trên **virtual site** và môi trường (b) CI của [15 §2–§3](15-simulators-and-messaging.md#2-bộ-simulator-theo-môi-trường): pymodbus server nạp register map YAML, mô hình PV/tải/BESS/POC, Toxiproxy, SAP/`ocpp` charger ảo, c104 | 07 L3–L4 (07 §11.2a); 10 §19.2 | CI hằng ngày/hằng đêm (ma trận lỗi 15 §3.4) | Release edge, release control plane |
| HIL (H) | Edge + thiết bị thật trong lab (logger, inverter, công tơ, PCS/BMS, charger, DI LOCAL/REMOTE); virtual site chỉ bổ sung phần thiếu (môi trường (c) của 15 §2.1) | 07 L5; 10 §19.3; 06 §16 "HIL / game day" | Trước mỗi release edge; trước site Gate M2 đầu tiên | Release edge, Gate M2 |
| E2E (E) | Trình duyệt → API → DB/edge mô phỏng theo luồng người dùng; gồm snapshot UI và kiểm nhãn i18n. Công cụ đề xuất cho SPA React: Playwright + axe; mức component dùng Vitest + React Testing Library + MSW (tính vào loại U) ([06 ADR-20](06-system-architecture.html#adr-20)) | 09 §6, §8.3; 04 WF | Hằng đêm trên staging | Release web |

NFR dùng thêm các loại: Tải (07 L7, 06 §16; edge ảo 1.000–10.000 kết nối của 15 §4.1), Game day/Diễn tập, Pen-test, Rà soát (tài liệu, cấu hình), PoC (06 §18), Đo SLI. Pilot hiện trường (07 L6) là bằng chứng `VERIFIED_FIELD` cho driver, không thay cho các tầng trên.

Kết quả của bộ mô phỏng luôn mang nhãn "Mô phỏng". Kết quả đó không nâng trạng thái driver lên `VERIFIED_*` (07 D-07-13; 15 §4.3; 13 R-48, R-55). Ca bổ sung của 15 §4.2 (T-E2-01…06: lệnh hết hạn ở broker, Response Topic lạ, lô quá lớn, đổi broker, 10.000 edge ảo, tenant demo không chạm edge thật) gắn vào T-NFR-SEC-011, T-NFR-SEC-003, T-NFR-PERF-004, T-NFR-REL-016 và T-FR-INT-031 (sandbox) như ca con.

### 2.2 Quy ước mã

- Mỗi FR có đúng một mã gốc `T-<FR id>`, ví dụ `T-FR-BESS-005`. Ca con: `T-<FR id>-NN`, ví dụ `T-FR-BESS-005-01` cho AC-BESS-01.
- Mỗi AC của 04 thành ít nhất một ca con của FR mà nó kiểm. Ma trận ghi AC trong ngoặc ở cột Test.
- NFR: `T-<NFR id>` và ca con `T-<NFR id>-NN` (đúng như 10 §19.3 đang dùng).
- Mã có sẵn được giữ nguyên: `T-FR-INT-003…023` và `T-FR-EV-005` của 07 §11.3; `T-NFR-…-NN` của 10 §19.3.
- Mã `T1-01…T1-07` của 08 §5.8 không theo quy ước. Ánh xạ đề xuất: T1-01 → `T-FR-GRID-005-01`; T1-02 → `T-FR-OPT-004-01`; T1-03 → `T-FR-BESS-008-01`; T1-04 → `T-FR-BESS-005-03`; T1-05 → `T-FR-GRID-006-01`; T1-06 → `T-FR-OPT-004-02`; T1-07 → `T-FR-OPT-003-01` (GAP-12-17).

### 2.3 Cổng kiểm thử theo phát hành

Cổng theo phase lộ trình của [11](11-mvp-and-roadmap.html) (G1 ở §6.6, G2a/G2b ở §7.6, G3 ở §8.5, G4 ở §9.4). "FR Phase n" nghĩa là FR có cột "Lộ trình (11)" = Phase n. `[PROPOSAL]`

| Cổng | Bắt buộc đạt |
|---|---|
| Gate MVP / G1 (Gate M1 phát hành, ra lộ trình Phase 1) | (1) Mọi `T-` của FR Phase 1 (138 FR, gồm 3 FR `⚠`) ở mọi loại test đã ghi, AC của 04 tương ứng đạt. (2) Tải L7 NFR-PERF-001…004, 007, 008 trên PoC 1.000 site. (3) T-NFR-SEC-007 (cross-tenant, chặn build); T-NFR-DATA-006 (golden snapshot); T-NFR-DATA-001 (rút WAN 7 ngày, 0 mất mẫu); diễn tập PITR (NFR-REL-005). (4) **Bộ an toàn đường lệnh M1**, vì M1 đã phát lệnh C2/C3 (cấu hình lưới, OTA, `control_enabled`, lịch native): T-FR-SEC-006, T-FR-SEC-007, T-NFR-SEC-008-01 (duyệt C3 hai người, hết hạn duyệt); T-NFR-SEC-004-01…03 (replay, sửa byte, `alg=none`/`kid` lạ); T-NFR-SEC-011-01 (đến sau `expires_at`); T-NFR-REL-012 (không thi hành lệnh cũ sau khôi phục); T-FR-SEC-013 với T-NFR-SEC-013-01 và T-NFR-SEC-013-04 (kill switch dừng lịch native, `SET_ESS_MODE`, `CONFIG_PUSH`) và T-NFR-REL-010 (≤ 60 s); T-FR-BESS-020 (SOE tối thiểu trước `control_enabled`); T-FR-INT-031 (phiên `COMMISSIONING_TEST`); T-FR-SEC-022 (giới hạn tốc độ). (5) HIL L5 cho driver ghi của M1 (NFR-SEC-030). |
| Gate M1 theo site | T-FR-INT-015, T-FR-INT-016, T-FR-INT-017, T-FR-INT-019, T-FR-INT-020 tại site, chạy qua phiên T-FR-INT-031; T-FR-GRID-004 hoặc T-FR-BESS-003 (native có readback). Trước khi bật `control_enabled`: SOE tối thiểu của site đã qua duyệt C3 hai người (T-FR-BESS-020 trên dữ liệu site, T-FR-SEC-007), engage kill switch phạm vi site một lần và xác nhận lịch native/`CONFIG_PUSH` dừng (T-NFR-SEC-013-04 tại site), gỡ bằng C3. |
| Release edge | Mọi `T-` loại S và H của FR có Gate M1/M2; toàn bộ ca 10 §19.3 áp cho gate của bản phát hành (NFR-SEC-030). |
| Gate M2 theo site (G2a của 11 §7.6) | T-FR-SEC-021 (hồ sơ sẵn sàng) với kết quả T-FR-INT-018 của chính site; T-NFR-SEC-013-02, -03 (kill switch khi edge chạy lịch rồi mất uplink, chống phát lại trạng thái cũ); T-FR-SEC-012 (Governor); game day mất cloud 4 h đã có ít nhất một lần trên HIL (NFR-REL-017); pen-test bên thứ ba trước site M2 đầu tiên, không còn lỗi Critical/High. |
| G2b (ra lộ trình Phase 2) | Mọi `T-` của FR Phase 2 (37 FR + FR có điều kiện đã kích hoạt); số đo vận hành 30 ngày theo 11 §7.6 (0 vi phạm xuất, 0 vượt SOE, 0 lệnh thi hành sau `expires_at`). |
| G3 / G4 (lộ trình Phase 3, 4) | `T-` của FR trong track được bật (cột "Lộ trình (11)"), cộng điều kiện riêng của track ở 11 §8.5, §9.4. Track chưa có trigger thì không chạy cổng. |

---

## 3. Ma trận FR theo module

Ký hiệu: xem §0.1. Loại test: Đơn vị, Tích hợp, Mô phỏng, HIL, E2E (§2.1). Cột "Ưu tiên · Hạng phát hành (04/03) · Hạng lệnh" ghi hạng lệnh tối thiểu của 04; PDP có thể nâng hạng theo ngữ cảnh. Cột "Lộ trình (11)" là phase lộ trình (§0.3); `hạng 03: Phase n` ở cột trước không phải phase lộ trình (CF-29).

### 3.1 M-ORG — Tổ chức, site, tài sản, người dùng

| FR (04) | Yêu cầu (tóm tắt) | Ưu tiên · Hạng phát hành (04/03) · Hạng lệnh | Lộ trình (11) | F- (03) | Module | Thực thể (05) | API (06) | UI (09) | Test |
|---|---|---|---|---|---|---|---|---|---|
| FR-ORG-001 | Hệ thống phải cho tạo/sửa tổ chức (tenant) với hồ sơ pháp nhân, múi giờ mặc định, ngôn ngữ … | P0 · MVP/M1 · — | Phase 1 | F-ORG-01 | M-ORG | `Organization` | API-ORG-01 | UI-32 | **T-FR-ORG-001** · Tích hợp · Tạo tenant với timezone, ngôn ngữ; mọi bản ghi tạo sau đó mang `tenant_id` của tenant; tenant B không đọc được (chạy chung bộ cross-tenant). |
| FR-ORG-002 | Hệ thống phải quản lý cây Org → Portfolio/Region (tùy chọn) → Site → Asset group → Device. … | P0 · MVP/M1 · — | Phase 1 | F-ORG-02 | M-ORG | `Site`, `Portfolio`, `GridConnection` | API-ORG-02 | UI-29 | **T-FR-ORG-002** · Tích hợp · Lưu site thiếu `timezone` → chặn (AC-ORG-01); site mới có `control_enabled=false` (AC-SEC-01); Portfolio là tùy chọn. |
| FR-ORG-003 | Hệ thống phải có sổ tài sản theo kiểu (GridConnection, MeteringPoint, PVPlant, Inverter, … | P0 · MVP/M1 · — | Phase 1 | F-ORG-03 | M-ORG | `Asset`, `Device`, `DeviceModel`, `CapabilityProfile`, `DriverVersion` | API-ORG-05 | UI-29 | **T-FR-ORG-003** · Tích hợp · Khai báo PCS gắn `DriverVersion`; đổi kWp có `valid_from` giữ lịch sử; serial trùng trong tenant bị từ chối. |
| FR-ORG-004 | Hệ thống phải thực thi vòng đời `planned → commissioning → active ⇄ maintenance / suspended →` … | P0 · MVP/M1 · — | Phase 1 | F-ORG-04 | M-ORG | `Site`, `Asset`, `AuditEvent` | API-ORG-03 | UI-29 | **T-FR-ORG-004** · Đơn vị · Bảng chuyển trạng thái hợp lệ/không hợp lệ; `decommissioned` không quay lại; site `commissioning` không vào KPI danh mục (AC-ORG-06); mỗi chuyển có audit. |
| FR-ORG-005 | Hệ thống phải có wizard onboarding: thông tin site → topology mẫu → tài sản → điểm đo → cấu … | P0 · MVP/M1 · — | Phase 1 | F-ORG-05 | M-ORG | `Site`, `Asset`, `MeteringPoint`, `TariffAssignment`, `EdgeNode`, `Integration` | API-ORG-04 | UI-29 | **T-FR-ORG-005** · E2E · Chạy wizard topology T3 (PV+BESS) tới cuối → site `planned` và danh sách mục còn thiếu đúng. |
| FR-ORG-006 | Wizard phải kiểm hợp lệ theo topology: `MTR_POC` bắt buộc nếu site có BESS hoặc gói CONTROL; … | P0 · MVP/M1 · — | Phase 1 | F-ORG-05, F-GRID-01 | M-ORG, M-GRID | `MeteringPoint`, `Asset` | API-ORG-04, API-ORG-06 | UI-29 | **T-FR-ORG-006** · Đơn vị · Site có BESS thiếu `MTR_POC` → không chuyển `commissioning` (AC-ORG-02); kWp/kWac = 1,8 chỉ cảnh báo, không chặn. |
| FR-ORG-007 | Hệ thống phải cho mời người dùng qua e-mail, kích hoạt, vô hiệu hóa; người dùng chọn ngôn ngữ … | P0 · MVP/M1 · — | Phase 1 | F-ORG-07 | M-ORG | `User`, `Organization`, `RoleAssignment` | API-ORG-07 | UI-31 | **T-FR-ORG-007** · Tích hợp · Mời e-mail đã là người dùng tenant khác → tạo binding mới, không tạo tài khoản trùng; vô hiệu hóa người dùng → phiên bị thu hồi. |
| FR-ORG-008 | Hệ thống phải lưu role binding (principal, role, scope_node) với vai trò ở §3.2, kế thừa xuống … | P0 · MVP/M1 · — | Phase 1 | F-ORG-08 | M-ORG | `Role`, `Permission`, `RolePermission`, `RoleAssignment` | API-ORG-08 | UI-31 | **T-FR-ORG-008** · Tích hợp · `ORG_ADMIN` gọi tạo `SET_ESS_P` → 403 `NO_COMMAND_PERMISSION` + audit (AC-ORG-03); binding kế thừa xuống cây. |
| FR-ORG-009 | Chủ tài sản phải cấp được grant cho tổ chức installer/O&M: phạm vi site, loại quyền (xem/cấu … | P0 · MVP/M1 · — | Phase 1 | F-ORG-09 | M-ORG | `AccessGrant`, `AuditEvent`, `Notification` | API-ORG-09 | UI-31 | **T-FR-ORG-009** · Tích hợp · Grant "lệnh" hết hạn lúc T, lệnh C1 lúc T+1 s bị từ chối, không ký envelope (AC-ORG-04); nhắc xem lại 90 ngày (AC-ORG-05); lệnh C3 đang chờ bị hủy. |
| FR-ORG-010 | Hệ thống phải ghi sự kiện tài sản có thời điểm: thay công tơ/CT/VT (thanh ghi cuối/đầu, tỷ số … | P0 · MVP/M1 · — | Phase 1 | F-ORG-11 | M-ORG | `AssetEvent`, `MeteringPointConfigVersion`, `IntervalEnergy`, `DirtyBucket` | API-ORG-10 | UI-29 | **T-FR-ORG-010** · Đơn vị · Thay công tơ 1.000.000 Wh → 0 Wh lúc 10:00: delta bucket 10:00–10:05 không âm, không `RESET_UNEXPLAINED` (AC-ORG-07); sinh DirtyBucket `ASSET_EVENT`. |
| FR-ORG-011 | Mỗi site phải có gói (`MONITORING`/`CONTROL`) và cờ tính năng (ví dụ tầng 3, EV, IEC 104); … | P0 · MVP/M1 · — | Phase 1 | F-ORG-15 | M-ORG | `Site`, `SiteControlConfig` | +API-ORG-02 (thuộc tính gói/cờ — 06 chưa ghi F-ORG-15) | UI-29, UI-32 | **T-FR-ORG-011** · Tích hợp · Site gói `MONITORING`: API-CMD-01 bị PDP từ chối, UI ẩn tab điều khiển; bật cờ tầng 3 không tự bật điều khiển. |
| FR-ORG-012 | Hệ thống nên cho lưu site làm mẫu (topology, điểm đo, quy tắc cảnh báo, chiến lược, SOE đề … | P1 · hạng 03: Phase 1 · — | Phase 2 | F-ORG-06 | M-ORG | `Site`, ⚠ `SiteTemplate` (05 thiếu) | API-ORG-13 (vòng nhất quán) | +UI-29 | **T-FR-ORG-012** · Tích hợp · Áp mẫu cho site mới có diff; SOE trong mẫu luôn về `DRAFT` và phải duyệt lại theo site. |
| FR-ORG-013 | Hệ thống nên cho tạo liên kết chỉ đọc có hạn (bên cho vay, kiểm toán) và liên kết kiosk công … | P1 · hạng 03: Phase 1 · — | Phase 3 (3K) | F-ORG-10 | M-ORG | `ShareLink` | API-ORG-12 | UI-35, +UI-31 | **T-FR-ORG-013** · E2E · Liên kết kiosk không lộ cảnh báo, cấu hình, lệnh, số tiền (khi tắt); token thu hồi → "Liên kết không còn hiệu lực". |
| FR-ORG-014 | Hệ thống nên lưu tài liệu theo site/tài sản (SLD, biên bản, datasheet, bảo hành, hồ sơ đấu … | P1 · hạng 03: Phase 1 · — | Phase 2 | F-ORG-12 | M-ORG | ⚠ `SiteDocument` (05 thiếu) | API-ORG-14 (vòng nhất quán) | ⚠ chưa có trang (đề xuất tab Tài liệu ở UI-29) | **T-FR-ORG-014** · Tích hợp · Tải SLD phiên bản 2, phiên bản 1 vẫn truy xuất được; tài liệu gắn lớp D2, người ngoài phạm vi không tải được. |
| FR-ORG-015 | Hệ thống nên có wizard thay thiết bị: chọn cũ → khai báo mới → ghi sự kiện FR-ORG-010 → giữ … | P1 · hạng 03: Phase 1 · — | Phase 2 | F-ORG-13 | M-ORG | `AssetEvent`, `Asset`, `Device`, `Series` | API-ORG-11 | UI-29 | **T-FR-ORG-015** · Tích hợp · Thay inverter qua wizard: chuỗi dữ liệu liên tục theo Asset (vị trí), Device cũ `decommissioned`, sự kiện FR-ORG-010 được ghi. |
| FR-ORG-016 | Hệ thống nên lưu điều khoản hợp đồng: bảo hành BESS (EFC, throughput, SOC trung bình, nhiệt … | P1 · hạng 03: Phase 1 · — | Phase 3 (3K) | F-ORG-16 | M-ORG | `Contract` | ⚠ thiếu endpoint hợp đồng | ⚠ chưa có trang (đề xuất tab Hợp đồng ở UI-29) | **T-FR-ORG-016** · Đơn vị · Lưu điều khoản bảo hành BESS (EFC, throughput, SOC TB, nhiệt độ) và loại trừ availability; FR-BESS-015, FR-REP-011 đọc đúng phiên bản. |
| FR-ORG-017 | Hệ thống có thể cho white-label theo tenant (logo, màu, tên miền, người gửi e-mail). | P2 · hạng 03: Phase 2 · — | Phase 4 (4E) | F-ORG-14 | M-ORG | `Organization` | +API-ORG-01 | UI-32 | **T-FR-ORG-017** · E2E · Logo/màu/tên miền riêng theo tenant; e-mail gửi từ người gửi tenant; tenant khác không bị ảnh hưởng. |
| FR-ORG-018 | Hệ thống phải cho ngừng site với xác nhận hai bước, chặn khi `control_enabled = true`, thu hồi … | P0 · MVP/M1 · — | Phase 1 | F-ORG-04, F-INT-02 | M-ORG, M-INT | `Site`, `EdgeNode`, `AuditEvent` | API-ORG-03, API-INT-01, API-INT-02 | UI-29 | **T-FR-ORG-018** · E2E · Decommission khi `control_enabled=true` bị chặn (AC-ORG-08); sau decommission: chứng chỉ edge bị thu hồi tại broker, ingest bị từ chối, dữ liệu còn theo lưu giữ. |

### 3.2 M-DASH — Dashboard

| FR (04) | Yêu cầu (tóm tắt) | Ưu tiên · Hạng phát hành (04/03) · Hạng lệnh | Lộ trình (11) | F- (03) | Module | Thực thể (05) | API (06) | UI (09) | Test |
|---|---|---|---|---|---|---|---|---|---|
| FR-DASH-001 | L1 phải có danh sách "cần chú ý" sắp theo điểm ưu tiên: (1) cảnh báo Khẩn cấp/Cao chưa ack, … | P0 · MVP/M1 · — | Phase 1 | F-DASH-01 | M-DASH | `Alarm`, `KpiValue`, `latest_value`, `Watermark` | API-TEL-09, API-LIVE-02 | UI-01 | **T-FR-DASH-001** · E2E · Site A có cảnh báo Cao chưa ack đứng trước site B chỉ DELAYED, dòng ghi lý do (AC-DASH-01); cập nhật qua SSE. |
| FR-DASH-002 | L1 phải có bảng site cấu hình cột: trạng thái (icon + chữ), site, khách hàng, tuổi dữ liệu, P … | P0 · MVP/M1 · — | Phase 1 | F-DASH-02 | M-DASH | `Site`, `latest_value`, `KpiValue` | API-TEL-09 | UI-01 | **T-FR-DASH-002** · Đơn vị · Giá trị chưa từng nhận hiển thị "—" không phải "0 kW" (AC-DASH-02); cấu hình cột lưu theo người dùng. |
| FR-DASH-003 | Hệ thống phải có bộ chuyển site toàn cục (breadcrumb Org ▸ Site ▸ Tài sản, tìm kiếm, phím tắt, … | P0 · MVP/M1 · — | Phase 1 | F-DASH-03 | M-DASH | `Site`, `RoleAssignment` | +API-ORG-02, +API-AUTH-02 | UI-02 | **T-FR-DASH-003** · E2E · Deep-link tới site ngoài phạm vi → trang 403 không lộ tên site; tìm kiếm chỉ trả site trong phạm vi. |
| FR-DASH-004 | L2 phải luôn hiện header: `site_strategy` hiện hành, nguồn lệnh đang thắng (mức arbiter), … | P0 · MVP/M1 · — | Phase 1 | F-DASH-04 | M-DASH | `SiteControlConfig`, `DispatchPlan`, `EdgeNode` | API-LIVE-01, +API-CMD-07 | UI-03 | **T-FR-DASH-004** · E2E · Edge OFFLINE 13:40 với plan #123 tới 23:45 → header "Mất kết nối cloud… đang chạy kế hoạch #123" (AC-DASH-04); hiện mức arbiter đang thắng. |
| FR-DASH-005 | L2 phải có biểu đồ ngày địa phương: P lưới (nhập trên/xuất dưới trục), PV, BESS, SOC, dải TOU … | P0 · MVP/M1 · — | Phase 1 | F-DASH-05 | M-DASH | `Aggregate`, `PlanSlot`, `TouCalendarVersion`, `ForecastValue` | +API-TEL-02, +API-OPT-03 | UI-03 | **T-FR-DASH-005** · Tích hợp · Trục ngày theo giờ site `[00:00, 24:00)`; xuất vẽ dưới trục; dải TOU đúng QĐ 963; dự báo có nhãn. |
| FR-DASH-006 | Hệ thống phải có thẻ KPI site và danh mục theo 03 §6 (nhập, xuất, PV, tự tiêu thụ, tự cung, … | P0 · MVP/M1 · — | Phase 1 | F-DASH-06 | M-DASH | `KpiDefinition`, `KpiValue` | API-TEL-06 | UI-01, UI-03 | **T-FR-DASH-006** · Đơn vị · Tự tiêu thụ danh mục tính lại từ tử số/mẫu số = 54,0% (AC-DASH-05); KPI mang `quality`, `coverage_pct`, `calc_version`. |
| FR-DASH-007 | Người dùng chỉ có 1 site phải vào thẳng L2; menu rút gọn theo vai trò. | P0 · MVP/M1 · — | Phase 1 | F-DASH-07 | M-DASH | `RoleAssignment` | +API-AUTH-02 | UI-02 | **T-FR-DASH-007** · E2E · Người dùng có binding 1 site → trang đầu là L2 site đó (AC-DASH-06); menu rút gọn theo vai trò. |
| FR-DASH-008 | Mọi màn dashboard phải áp quy tắc hiển thị: số không dấu + chữ hướng; trạng thái mã hóa ≥ 2 … | P0 · MVP/M1 · — | Phase 1 | F-DASH-02, F-DASH-06, F-MON-04 | M-DASH, M-MON | `latest_value`, `KpiValue` | API-AUTH-04, API-TEL-03, API-TEL-06, API-TEL-09 | UI-01, UI-03, +mọi trang | **T-FR-DASH-008** · Đơn vị · Snapshot UI: P lưới −120 kW hiện "Xuất 120 kW" (AC-DASH-03); thiếu dữ liệu "—" (AC-DASH-02); freshness DELAYED/OLD (AC-MON-01/02). |
| FR-DASH-009 | Hệ thống nên có chế độ NOC/màn lớn (tile, sparkline P lưới 24 h có ngưỡng) và hai mật độ … | P1 · hạng 03: Phase 1 · — | Phase 3 (3K) | F-DASH-08 | M-DASH | `latest_value`, `KpiValue` | +API-TEL-09, +API-LIVE-02 | UI-01 | **T-FR-DASH-009** · E2E · Chế độ NOC: tile + sparkline P lưới 24 h có ngưỡng; tự làm mới không cần thao tác; 500 site trong NFR-PERF-001. |
| FR-DASH-010 | Hệ thống nên có giao diện mobile: cảnh báo + ack, trạng thái site, energy flow, kế hoạch chỉ … | P1 · hạng 03: Phase 1 · — | Phase 3 (3K) | F-DASH-10 | M-DASH | `Alarm`, `latest_value` | +API-ALM-01, +API-ALM-03, +API-TEL-03 | ⚠ 09 chưa ghi FR; +UI-03, +UI-14 (responsive) | **T-FR-DASH-010** · E2E · Viewport 360 px: ack cảnh báo, xem energy flow; mobile chỉ cho C1 và engage kill switch (X-09-05). |
| FR-DASH-011 | Hệ thống nên có màn kiosk công khai chữ lớn (energy flow, sản lượng, CO₂ ước tính có nguồn hệ … | P1 · hạng 03: Phase 1 · — | Phase 3 (3K) | F-DASH-11 | M-DASH | `ShareLink`, `KpiValue`, `EmissionFactorVersion` | API-ORG-12 | UI-35 | **T-FR-DASH-011** · E2E · Kiosk: CO₂ hiện "≈" kèm phiên bản hệ số; ẩn số tiền mặc định; mất kết nối → "Dữ liệu tạm dừng lúc HH:MM". |
| FR-DASH-012 | Hệ thống nên cho lưu view (bộ lọc, cột, khoảng thời gian) theo người dùng và chia sẻ trong … | P1 · hạng 03: Phase 1 · — | Phase 3 (3K) | F-DASH-12 | M-DASH | ⚠ `SavedView` (05 thiếu) | API-ORG-15 (vòng nhất quán) | ⚠ 09 chưa ghi FR; +UI-13, +UI-01 | **T-FR-DASH-012** · Tích hợp · Lưu view (lọc, cột, khoảng) theo người dùng; người khác không thấy trừ khi chia sẻ; view trỏ site đã mất quyền bị lọc bỏ. |
| FR-DASH-013 | Hệ thống có thể có chế độ bản đồ site theo tỉnh/KCN tô theo trạng thái. | P2 · hạng 03: Phase 2 · — | Phase 4 (4E) | F-DASH-09 | M-DASH | `Site` | +API-ORG-02 | UI-01 | **T-FR-DASH-013** · E2E · Bản đồ tô theo trạng thái; site thiếu tọa độ liệt kê riêng, không đặt sai vị trí. |

### 3.3 M-MON — Giám sát thời gian thực

| FR (04) | Yêu cầu (tóm tắt) | Ưu tiên · Hạng phát hành (04/03) · Hạng lệnh | Lộ trình (11) | F- (03) | Module | Thực thể (05) | API (06) | UI (09) | Test |
|---|---|---|---|---|---|---|---|---|---|
| FR-MON-001 | Cloud phải nhận telemetry từ edge theo lớp C1 (5 s), C2 (60 s), C3 (300 s hoặc khi đổi), thanh … | P0 · MVP/M1 · — | Phase 1 | F-MON-01 | M-MON | `Series`, `ts_gauge`, `ts_register`, `ts_state`, `latest_value` | API-TEL-03, API-LIVE-01 | — (backend; hiển thị ở UI-04) | **T-FR-MON-001** · Mô phỏng · Edge ảo gửi đủ lớp C1 5 s/C2 60 s/C3 300 s/C4 biên 5 phút/C5 sự kiện; lưu tổng hợp nguồn avg/min/max/n đúng cửa sổ. |
| FR-MON-002 | Mọi mẫu phải mang `ts` (edge thu, UTC ms, khóa chính), `ts_src` (tùy chọn) và `ts_ingest`. UI … | P0 · MVP/M1 · — | Phase 1 | F-MON-01 | M-MON | `ts_gauge`, `ts_register` | API-TEL-03, API-LIVE-01 | — (backend) | **T-FR-MON-002** · Đơn vị · Mẫu thiếu `ts` bị từ chối; `ts` tương lai quá dung sai → `UNCERTAIN_CLOCK`; `ts_ingest` do cloud gán. |
| FR-MON-003 | Site không có edge phải giám sát được qua connector cloud hãng chỉ đọc (MVP: Huawei … | P0 · MVP/M1 · — | Phase 1 | F-MON-02 | M-MON | `Integration`, `ExternalRef`, `Series` | API-INT-07 | UI-04, UI-26 | **T-FR-MON-003** · Tích hợp · Connector Huawei với phản hồi ghi sẵn (mock): nguồn "Cloud hãng (≈ 5 phút)", không có nút lệnh (AC-MON-06); scope chỉ đọc. |
| FR-MON-004 | Hệ thống phải hiển thị energy flow với nút PV, Lưới, BESS, Tải, EV, Máy phát (ẩn nút không … | P0 · MVP/M1 · — | Phase 1 | F-MON-03 | M-MON | `EnergyBalance`, `FlowAttribution`, `latest_value` | API-TEL-04, API-LIVE-01 | UI-03, UI-05 | **T-FR-MON-004** · Đơn vị · BESS sạc 50 kW theo PCS → cạnh "Sạc 50 kW" hướng vào BESS (AC-MON-05); nút không có tài sản bị ẩn. |
| FR-MON-005 | Hệ thống phải tính `freshness ∈ {LIVE, DELAYED, OLD, OFFLINE, NO_DATA}` theo chu kỳ mong đợi … | P0 · MVP/M1 · — | Phase 1 | F-MON-04 | M-MON | `latest_value`, `Series` | API-AUTH-04, API-TEL-03 | UI-03, UI-04 | **T-FR-MON-005** · Đơn vị · C1 mẫu cuối cách 12 s → DELAYED "trễ 12 s" (AC-MON-01); 26 s → chữ xám "cập nhật HH:MM:SS" (AC-MON-02). |
| FR-MON-006 | Hệ thống phải có danh sách thiết bị theo loại và trang chi tiết L3: giá trị chính, trạng thái, … | P0 · MVP/M1 · — | Phase 1 | F-MON-05 | M-MON | `Asset`, `Device`, `latest_value` | +API-ORG-05, +API-TEL-03 | UI-04 | **T-FR-MON-006** · E2E · Danh sách thiết bị theo loại; L3 hiển thị đơn vị, quality, freshness; thiết bị `maintenance` có nhãn ngoài dịch vụ. |
| FR-MON-007 | Hệ thống phải có trang chẩn đoán L4: điểm tín hiệu thô, giá trị thanh ghi, hệ số scale, mã … | P0 · MVP/M1 · — | Phase 1 | F-MON-06 | M-MON | `PointDefinition`, `Series`, `ts_register` | API-TEL-08 | UI-12 | **T-FR-MON-007** · Tích hợp · L4 hiện thanh ghi thô, `scale_factor_version`, mã quality điểm; không có nút ghi. |
| FR-MON-008 | Hệ thống phải có trang trạng thái edge: online/offline, `clock_state` và offset, độ sâu và … | P0 · MVP/M1 · — | Phase 1 | F-MON-07 | M-MON | `EdgeNode`, `EdgeConfigVersion`, `Series` | API-TEL-10 | UI-26 | **T-FR-MON-008** · Mô phỏng · Lỡ 3 heartbeat 30 s → OFFLINE ở giây 90 ± 5 (AC-MON-03); hiện `clock_state`, `buffer_fill_pct`, `run_mode`. |
| FR-MON-009 | Hệ thống phải đọc cảm biến bức xạ/thời tiết (G_POA, G_hor, T_module, T_ambient) và phát hiện … | P0 · MVP/M1 · — | Phase 1 | F-MON-08 | M-MON | `Asset`, `Series` | +API-TEL-02, +API-TEL-03 | UI-04 | **T-FR-MON-009** · Mô phỏng · G_POA đứng yên 2 h giữa ngày → `FROZEN` (AC-MON-07); cảm biến thiếu → PR = N/A. |
| FR-MON-010 | Hệ thống phải đọc submeter `MTR_LOAD_i` và tính "tải không đo" = tải tính toán − Σ submeter, … | P0 · MVP/M1 · — | Phase 1 | F-MON-09 | M-MON | `MeteringPoint`, `EnergyBalance` | +API-TEL-05 | UI-04, UI-10 | **T-FR-MON-010** · Đơn vị · Tải không đo = tải tính toán − Σ submeter; giá trị âm vượt dung sai → cờ DQ, không hiển thị số âm. |
| FR-MON-011 | Hệ thống nên sinh SLD chỉ đọc từ mô hình tài sản, đánh dấu vị trí công tơ, ranh giới đo, trạng … | P1 · hạng 03: Phase 1 · — | Phase 3 (3K) | F-MON-10 | M-MON | `Asset`, `MeteringPoint`, `GridConnection` | +API-ORG-05, +API-ORG-06 (dựng SLD ở client; 06 không có endpoint SLD) | UI-06 | **T-FR-MON-011** · E2E · SLD sinh lại sau khi thêm submeter; vị trí công tơ và ranh giới đo đúng mô hình. |
| FR-MON-012 | Edge nên có trang HMI cục bộ tối giản (trạng thái, energy flow, cảnh báo, chế độ, interlock, … | P1 · hạng 03: Phase 1 · — | Phase 2 | F-MON-11 | M-MON | `EdgeNode` | — (HMI trên edge, không qua cloud) | UI-36 | **T-FR-MON-012** · HIL · Rút WAN: HMI hiện banner mất cloud, kế hoạch đang chạy, interlock; không có nút lệnh ở P1. |
| FR-MON-013 | Kỹ sư nên yêu cầu được luồng 1 s tạm thời (mặc định 15 phút, tối đa 60 phút) cho một site; … | P1 · hạng 03: Phase 1 · — | Phase 3 (3K) | F-MON-12 | M-MON | `Series` | API-LIVE-05, +⚠ thiếu endpoint yêu cầu burst (chỉ có luồng API-LIVE-05) | UI-12 | **T-FR-MON-013** · Mô phỏng · Yêu cầu burst 15 phút → luồng 1 s; tự dừng ở 60 phút tối đa; có audit người yêu cầu. |

### 3.4 M-HIST — Lịch sử, chất lượng dữ liệu

| FR (04) | Yêu cầu (tóm tắt) | Ưu tiên · Hạng phát hành (04/03) · Hạng lệnh | Lộ trình (11) | F- (03) | Module | Thực thể (05) | API (06) | UI (09) | Test |
|---|---|---|---|---|---|---|---|---|---|
| FR-HIST-001 | Mỗi chuỗi phải được khai báo trong catalog trước khi ingest: `kind` … | P0 · MVP/M1 · — | Phase 1 | F-HIST-01 | M-HIST | `PointDefinition`, `Series` | API-TEL-01 | — (backend; khai báo qua UI-28) | **T-FR-HIST-001** · Tích hợp · Mẫu của chuỗi chưa khai báo `agg_rule` → không ingest, vào hàng cách ly, cảnh báo DQ. |
| FR-HIST-002 | Ingest phải idempotent theo `(series_id, ts)`; ack theo `seq` của edge; bản trùng cùng giá trị … | P0 · MVP/M1 · — | Phase 1 | F-HIST-01 | M-HIST | `ts_gauge`, `ts_register`, `ts_state`, `latest_value` | — (MQTT `ems/v1/{edge_id}/up/…`) | — (backend) | **T-FR-HIST-002** · Tích hợp · Gửi trùng cùng giá trị → 1 bản ghi (AC-HIST-08); mẫu cũ không ghi đè giá trị hiện tại (AC-MON-04); lỗ `seq` → RESEND (T-FR-INT-008). |
| FR-HIST-003 | Raw và hợp đồng edge phải dùng W, Wh, var, VA, varh (bộ đếm int64 Wh); aggregate, KPI, báo … | P0 · MVP/M1 · — | Phase 1 | F-HIST-01 | M-HIST | `Series`, `PointDefinition` | API-TEL-01, +mọi API dữ liệu | — (quy ước) | **T-FR-HIST-003** · Đơn vị · Lint schema OpenAPI/Protobuf: mọi trường số có hậu tố đơn vị; raw W/Wh, API kW/kWh; test đối chiếu cùng mẫu qua hai tầng. |
| FR-HIST-004 | Hệ thống phải tính điện năng từ thanh ghi tích lũy bằng máy trạng thái: OK / SUSPECT_SPIKE / … | P0 · MVP/M1 · — | Phase 1 | F-HIST-02 | M-HIST | `ts_register`, `IntervalEnergy`, `AssetEvent` | +API-TEL-02 | — (backend) | **T-FR-HIST-004** · Đơn vị · Delta 4,2 kWh MEASURED (AC-HIST-01); ROLLOVER 796 Wh (AC-HIST-02); `RESET_UNEXPLAINED` dùng tích phân P có cờ ước tính (AC-HIST-03). |
| FR-HIST-005 | Hệ thống phải tổng hợp 5 phút và 1 h khóa `bucket_start`, khoảng nửa mở `[start, start+Δ)`; … | P0 · MVP/M1 · — | Phase 1 | F-HIST-03 | M-HIST | `Aggregate` | API-TEL-02 | +UI-13 | **T-FR-HIST-005** · Đơn vị · Ngày địa phương 2026-10-10 Asia/Ho_Chi_Minh gộp `[2026-10-09T17:00Z, 2026-10-10T17:00Z)` (AC-HIST-07); rollup không lấy trung bình của trung bình. |
| FR-HIST-006 | Hệ thống phải xử lý dữ liệu trễ: refresh cửa sổ ≥ 7 ngày; dữ liệu trễ hơn đi `late_landing` + … | P0 · MVP/M1 · — | Phase 1 | F-HIST-04 | M-HIST | `Watermark`, `DirtyBucket`, `LateLanding` | +API-TEL-07 | +UI-03, +UI-30 | **T-FR-HIST-006** · Tích hợp · Backfill 6 ngày → coverage 100% điểm có ở edge (AC-HIST-04); bucket bẩn tính lại ≤ 1 h; dữ liệu > 7 ngày qua LateLanding. |
| FR-HIST-007 | Hệ thống phải gắn chất lượng ba tầng: tầng điểm (mã E: GOOD/UNCERTAIN_*/BAD_*), tầng chuỗi … | P0 · MVP/M1 · — | Phase 1 | F-HIST-05 | M-HIST | `ts_gauge`, `IntervalEnergy`, `KpiValue` | API-TEL-07 | UI-13 | **T-FR-HIST-007** · Đơn vị · KPI có một đầu vào ESTIMATED → quality ESTIMATED (AC-HIST-06); `FROZEN` thay cho `STALE` (K). |
| FR-HIST-008 | Hệ thống phải lấp khoảng trống theo bảng F §3.8: gauge ≤ 3 chu kỳ nối liền, > 3 chu kỳ đứt … | P0 · MVP/M1 · — | Phase 1 | F-HIST-05, F-HIST-03 | M-HIST | `Aggregate`, `IntervalEnergy` | API-TEL-02, API-TEL-07 | UI-13 | **T-FR-HIST-008** · Đơn vị · Gauge thiếu ≤ 3 chu kỳ nội suy, > 3 để trống; cửa sổ 30 phút có bucket INTERPOLATED → `UNCERTAIN`, không chọn làm Pmax (AC-HIST-05). |
| FR-HIST-009 | Hệ thống phải có **một** thuật toán cân bằng và phân bổ luồng năng lượng ở backend có … | P0 · MVP/M1 · — | Phase 1 | F-HIST-06 | M-HIST | `EnergyBalance`, `FlowAttribution`, `CalcVersion` | API-TEL-05 | UI-05 | **T-FR-HIST-009** · Đơn vị · Bộ golden snapshot ≥ 20 site-ngày: cùng `attribution_version` → cùng `output_hash`; phân bổ gắn nhãn "ước tính". |
| FR-HIST-010 | Hệ thống phải có trend explorer: nhiều panel xếp chồng đồng bộ trục thời gian, ≤ 2 đơn … | P0 · MVP/M1 · — | Phase 1 | F-HIST-07 | M-HIST | `Aggregate`, `Series` | API-TEL-02 | UI-13 | **T-FR-HIST-010** · E2E · 8 chuỗi raw 7 ngày p95 ≤ 3 s (NFR-PERF-002); chuỗi thứ 9 bị từ chối kèm gợi ý độ phân giải. |
| FR-HIST-011 | Hệ thống phải áp lưu giữ: raw nóng 13 tháng (nén sau 7 ngày), tổng hợp 5 phút 5 năm, … | P0 · MVP/M1 · — | Phase 1 | F-HIST-10 | M-HIST | `Series`, `Aggregate`, `IntervalEnergy` | — (job nội bộ) | +UI-32 | **T-FR-HIST-011** · Tích hợp · Trên bản sao có "du hành thời gian": raw > 13 tháng bị xóa, 5 phút giữ 5 năm, ≥ 1 h giữ; nén sau 7 ngày không mất DML sửa. |
| FR-HIST-012 | Hệ thống nên so sánh chuỗi chuẩn hóa (kWh/kWp, kW/kW định mức) giữa nhiều site/thiết bị cùng … | P1 · hạng 03: Phase 1 · — | Phase 3 (3K) | F-HIST-08 | M-HIST | `Aggregate`, `Asset` | +API-TEL-02 | UI-13 | **T-FR-HIST-012** · Đơn vị · kWh/kWp dùng kWp hiệu lực theo ngày; so sánh 3 site cùng hướng cho thứ hạng đúng. |
| FR-HIST-013 | Hệ thống nên tính residual cân bằng / E_cons theo chu kỳ và cảnh báo DQ khi vượt ngưỡng (gợi ý … | P1 · hạng 03: Phase 1 · — | Phase 2 | F-HIST-09 | M-HIST | `EnergyBalance`, `Alarm` | +API-TEL-05, +API-TEL-07 | UI-05 | **T-FR-HIST-013** · Mô phỏng · Công tơ mô phỏng lệch hệ số 5% → residual vượt ngưỡng → cảnh báo DQ. |
| FR-HIST-014 | Người có quyền nên nhập giá trị thủ công/thay thế cho khoảng hỏng (origin MANUAL/SUBSTITUTED, … | P1 · hạng 03: Phase 1 · — | Phase 2 | F-HIST-11 | M-HIST | `DataCorrection`, `AuditEvent` | API-TEL-11 | ⚠ 09 chưa ghi; đề xuất thao tác trong UI-13 | **T-FR-HIST-014** · Tích hợp · Thay thế khoảng hỏng bằng MANUAL: dữ liệu gốc còn ở lớp riêng; KPI đổi quality; có người nhập/duyệt và lý do. |
| FR-HIST-015 | Hệ thống nên có bảng điều khiển DQ: coverage theo thiết bị, độ trễ ingest p50/p95, tỷ lệ … | P1 · hạng 03: Phase 1 · — | Phase 2 | F-HIST-12 | M-HIST | `Watermark`, `KpiValue` | +API-TEL-07 | ⚠ chưa có trang DQ (UI-30 chỉ có R8); đề xuất tab DQ ở UI-13 hoặc UI-26 | **T-FR-HIST-015** · E2E · Bảng DQ hiện coverage theo thiết bị, độ trễ ingest p50/p95, tỷ lệ SUSPECT; khớp với số đo NFR-OBS-007. |
| FR-HIST-016 | Hệ thống nên phát hiện lệch đồng hồ/lệch pha (reset `daily_yield` không gần 00:00 địa phương; … | P1 · hạng 03: Phase 1 · — | Phase 3 (3K) | F-HIST-13 | M-HIST | `Series`, `EdgeNode` | +API-TEL-07 | ⚠ 09 chưa ghi; đề xuất +UI-26 | **T-FR-HIST-016** · Mô phỏng · Inverter lệch đồng hồ +1 h → `daily_yield` reset lúc 01:00 giờ site → cảnh báo DQ lệch pha. |
| FR-HIST-017 | Hệ thống nên xuất raw và 5 phút sang Parquet trên object storage, partition theo site/tháng, … | P1 · hạng 03: Phase 1 · — | Phase 3 (3I) | F-HIST-14 | M-HIST | `Series`, `Aggregate`, `ExportJob` | — (nội bộ; khách dùng API-REP-07) | — (backend) | **T-FR-HIST-017** · Tích hợp · Parquet phân vùng tenant/site/tháng; số dòng và tổng kWh khớp DB. |

### 3.5 M-REP — Báo cáo, xuất dữ liệu

| FR (04) | Yêu cầu (tóm tắt) | Ưu tiên · Hạng phát hành (04/03) · Hạng lệnh | Lộ trình (11) | F- (03) | Module | Thực thể (05) | API (06) | UI (09) | Test |
|---|---|---|---|---|---|---|---|---|---|
| FR-REP-001 | Hệ thống phải tạo R1 Báo cáo vận hành ngày: sản lượng PV, nhập/xuất, sạc/xả, SOC min/max, Pmax … | P0 · MVP/M1 · — | Phase 1 | F-REP-01 | M-REP | `ReportTemplate`, `ReportSnapshot`, `KpiValue`, `Watermark` | API-REP-01, API-REP-02 | UI-30 | **T-FR-REP-001** · E2E · 06:00 giờ site R1 hôm qua sẵn sàng (≥ 99% site) và ghi "dữ liệu tính đến…" (AC-REP-01). |
| FR-REP-002 | Hệ thống phải tạo R2 Báo cáo năng lượng và hóa đơn bóng theo kỳ hóa đơn hoặc tháng lịch: … | P0 · MVP/M1 · — | Phase 1 | F-REP-02 | M-REP | `ReportTemplate`, `ReportSnapshot`, `ShadowBill`, `BillingPeriod`, `TariffVersion` | API-REP-01, API-REP-02 | UI-30 | **T-FR-REP-002** · E2E · 3 bucket MISSING ở cao điểm → R2 `INCOMPLETE` với khoảng min/max (AC-REP-02); đổi giá giữa kỳ dùng đúng phiên bản (AC-TAR-06). |
| FR-REP-003 | Hệ thống phải tạo R3 Phân tích công suất: top-N cửa sổ 30 phút (thời điểm, kW, thành phần … | P0 · MVP/M1 · — | Phase 1 | F-REP-03 | M-REP | `ReportTemplate`, `DemandWindow`, `Aggregate` | API-REP-01, API-REP-02 | UI-30 | **T-FR-REP-003** · Đơn vị · Top-N cửa sổ 30 phút theo block; cửa sổ có bucket nội suy liệt kê `UNCERTAIN` (AC-HIST-05). |
| FR-REP-004 | Hệ thống phải tạo R8 Báo cáo chất lượng dữ liệu: coverage theo thiết bị, khoảng trống, … | P0 · MVP/M1 · — | Phase 1 | F-REP-08 | M-REP | `ReportTemplate`, `Watermark`, `KpiValue` | API-TEL-07, API-REP-01, API-REP-02 | UI-30 | **T-FR-REP-004** · Tích hợp · Tiêm khoảng mất dữ liệu vào 2 thiết bị → R8 liệt kê đúng khoảng và coverage. |
| FR-REP-005 | Báo cáo phát hành phải là snapshot bất biến với `report_version`, `data_as_of`, … | P0 · MVP/M1 · — | Phase 1 | F-REP-10 | M-REP | `ReportSnapshot` | API-REP-03 | UI-30 | **T-FR-REP-005** · Tích hợp · Backfill +0,6% nhập → restatement phiên bản mới (AC-REP-03); +0,3% và Pmax không đổi → không restatement (AC-REP-04); bản cũ bất biến (`content_hash`). |
| FR-REP-006 | Hệ thống phải xuất CSV (UTF-8 có BOM, ISO 8601 có offset + cột UTC, đơn vị trong header, cột … | P0 · MVP/M1 · — | Phase 1 | F-REP-11 | M-REP | `ExportJob`, `AuditEvent` | API-REP-04 | UI-13, UI-30 | **T-FR-REP-006** · Tích hợp · CSV có `+07:00`, cột UTC, hậu tố đơn vị, cột quality (AC-REP-05); thiếu `data.export` → 403 + audit (AC-REP-06); > 100.000 dòng chạy nền. |
| FR-REP-007 | Hệ thống phải xuất bằng chứng tuân thủ giới hạn xuất: nhật ký mọi thay đổi chế độ/giới hạn … | P0 · MVP/M1 · — | Phase 1 | F-REP-13 | M-REP | `AuditEvent`, `SiteGridConfigVersion`, `Event`, `Alarm` | API-REP-05 | UI-30, +UI-10 | **T-FR-REP-007** · E2E · Báo cáo tháng 9 liệt kê mọi đổi `export_limit_w` (người, thời điểm, cũ/mới, duyệt) và mọi sự kiện vi phạm (AC-REP-07). |
| FR-REP-008 | Mọi báo cáo phải ghi phương pháp và nhãn: số ước tính có "≈ ước tính"; số mô phỏng có "Mô … | P0 · MVP/M1 · — | Phase 1 | F-REP-02, F-REP-07 | M-REP | `ReportSnapshot`, `KpiValue`, `CalcVersion` | API-REP-01, API-REP-02 | UI-30, +mọi trang báo cáo | **T-FR-REP-008** · Đơn vị · Mọi số ước tính trong PDF có "≈ ước tính", số mô phỏng có "Mô phỏng"; quét chuỗi không có "AI" (AC-ADV-03). |
| FR-REP-009 | Hệ thống nên tạo R4 Hiệu suất PV (Yf, PR chỉ khi có POA, PR hiệu chỉnh nhiệt, PR loại trừ … | P1 · hạng 03: Phase 1 · — | Phase 2 | F-REP-04 | M-REP | `ReportTemplate`, `KpiValue`, `Series` | +API-REP-01, +API-REP-02 | UI-30 | **T-FR-REP-009** · Đơn vị · Site không có cảm biến POA → PR "N/A — chưa có cảm biến bức xạ mặt phẳng tấm" (AC-PV-02). |
| FR-REP-010 | Hệ thống nên tạo R5 BESS (throughput, EFC kèm `E_ref`, RTE kèm ranh giới, xu hướng SOH, aux, … | P1 · hạng 03: Phase 1 · — | Phase 2 | F-REP-05 | M-REP | `ReportTemplate`, `KpiValue`, `BatteryEnergyLedger` | +API-REP-01, +API-REP-02 | UI-30 | **T-FR-REP-010** · Đơn vị · EFC hiển thị kèm `E_ref`; RTE kèm `rte_boundary`; không so RTE khác ranh giới. |
| FR-REP-011 | Hệ thống nên tạo R6 Availability (thời gian, điện năng, dữ liệu; loại trừ theo hợp đồng; mất … | P1 · hạng 03: Phase 1 · — | Phase 2 | F-REP-06 | M-REP | `ReportTemplate`, `KpiValue`, `MaintenanceWindow`, `Contract` | +API-REP-01, +API-REP-02 | UI-30 | **T-FR-REP-011** · Đơn vị · Availability theo thời gian và điện năng; giờ trong MaintenanceWindow loại trừ theo hợp đồng. |
| FR-REP-012 | Hệ thống nên tạo R7 Tiết kiệm so với baseline B0 (không PV, không BESS) và B1 (có PV, không … | P1 · hạng 03: Phase 1 · — | Phase 3 (3I) | F-REP-07 | M-REP | `ReportTemplate`, `ShadowBill`, `TariffVersion` | +API-REP-01, +API-REP-02 | UI-30 | **T-FR-REP-012** · Đơn vị · B0/B1 dùng cùng `tariff_version` với hóa đơn bóng; kết quả có nhãn "ước tính"; không in "% tiết kiệm" tiếp thị. |
| FR-REP-013 | Hệ thống nên cho đăng ký nhận báo cáo theo lịch (giờ site), chỉ gửi khi watermark ≥ cuối kỳ … | P1 · hạng 03: Phase 1 · — | Phase 3 (3I) | F-REP-09 | M-REP | `ReportSchedule`, `Notification` | API-REP-06 | UI-30 | **T-FR-REP-013** · Tích hợp · Chờ watermark tới `max_wait_local` 06:00 rồi gửi kèm nhãn "dữ liệu chưa đầy đủ". |
| FR-REP-014 | Hệ thống nên xuất hàng loạt Parquet theo site/tháng cho data lake của khách. | P1 · hạng 03: Phase 1 · — | Phase 3 (3I) | F-REP-12 | M-REP | `ExportJob` | API-REP-07 | UI-30 | **T-FR-REP-014** · Tích hợp · Parquet theo site/tháng đúng schema có đơn vị và quality; link hết hạn 7 ngày. |
| FR-REP-015 | Hệ thống nên theo dõi ngân sách xuất 50%: lũy kế E_exp/E_pv theo kỳ, dự báo cuối kỳ, nguồn gốc … | P1 · hạng 03: Phase 1 · — | Phase 3 (3D) | F-REP-14 | M-REP | `ExportBudgetPeriod`, `IntervalEnergy` | ⚠ thiếu endpoint ngân sách xuất | UI-30, +UI-10 | **T-FR-REP-015** · Đơn vị · Lũy kế E_exp/E_pv đúng kỳ; dự báo cuối kỳ có nhãn; kỳ tính theo NĐ 58/243 là UNKNOWN → tham số. |
| FR-REP-016 | Hệ thống nên báo cáo CO₂ tránh được và Scope 2 với bảng hệ số có phiên bản (năm, giá trị, đơn … | P1 · hạng 03: Phase 1 · — | Phase 3 (3I) | F-REP-15 | M-REP | `EmissionFactorVersion`, `KpiValue` | +API-REP-01, +API-REP-02 | UI-30 | **T-FR-REP-016** · Đơn vị · Hệ số theo năm có phiên bản; đổi hệ số sinh DirtyBucket `EF_CHANGE`; giá trị hệ số VN chưa kiểm chứng được gắn UNKNOWN. |
| FR-REP-017 | Hệ thống nên xuất dữ liệu cho ESG/ISO 50001 (kWh theo nguồn × giờ, EnPI đơn giản khi khách … | P1 · hạng 03: Phase 1 · — | Phase 3 (3I) | F-REP-16 | M-REP | `ExportJob`, `KpiValue` | +API-REP-04 | UI-30 | **T-FR-REP-017** · Tích hợp · Xuất kWh theo nguồn × giờ; file không chứa tuyên bố "tuân thủ ISO 50001". |
| FR-REP-018 | Hệ thống nên tạo dữ liệu thanh toán PPA/ESCO (kWh bán theo site × khung TOU × kỳ, bảng đối … | P1 · hạng 03: Phase 1 · — | Phase 3 (3I) | F-REP-17 | M-REP | `IntervalEnergy`, `TariffVersion`, `Contract`, `ReportSnapshot` | ⚠ thiếu mẫu báo cáo PPA trong API-REP-01 | UI-30 | **T-FR-REP-018** · Đơn vị · kWh bán theo khung TOU × kỳ khớp tổng R2; snapshot bất biến làm căn cứ thanh toán. |
| FR-REP-019 | Hệ thống nên tạo báo cáo danh mục (xếp hạng yield, chi phí, cảnh báo, availability; trọng số … | P1 · hạng 03: Phase 1 · — | Phase 3 (3I) | F-REP-18 | M-REP | `ReportTemplate`, `KpiValue` | +API-REP-01, +API-REP-02 | UI-30 | **T-FR-REP-019** · Đơn vị · Xếp hạng yield/chi phí danh mục; KPI tỷ lệ tính lại từ tử/mẫu số. |

### 3.6 M-TAR — Biểu giá, TOU, hóa đơn bóng

| FR (04) | Yêu cầu (tóm tắt) | Ưu tiên · Hạng phát hành (04/03) · Hạng lệnh | Lộ trình (11) | F- (03) | Module | Thực thể (05) | API (06) | UI (09) | Test |
|---|---|---|---|---|---|---|---|---|---|
| FR-TAR-001 | Hệ thống phải có thư viện biểu giá có phiên bản: nhóm khách hàng × cấp điện áp × khung giờ, … | P0 · MVP/M1 · — | Phase 1 | F-TAR-01 | M-TAR | `Tariff`, `TariffVersion`, `TariffComponent` | API-TAR-01, API-TAR-02 | UI-25 | **T-FR-TAR-001** · Đơn vị · Nhập 10 kWh ở bucket cao điểm cấp 22–<110 kV với giá mẫu → đúng tiền (AC-TAR-04); phiên bản đã publish không sửa được. |
| FR-TAR-002 | Hệ thống phải có lịch TOU có phiên bản: khung cao điểm/bình thường/thấp điểm theo thứ trong … | P0 · MVP/M1 · — | Phase 1 | F-TAR-02 | M-TAR | `TouCalendar`, `TouCalendarVersion`, `TouRule`, `SpecialDay` | API-TAR-03 | UI-25 | **T-FR-TAR-002** · Đơn vị · Thứ Hai 17:29 "Bình thường", 17:30 "Cao điểm" (AC-TAR-01); Chủ nhật 19:00 không phải cao điểm (AC-TAR-02). |
| FR-TAR-003 | Mỗi site phải chọn được lịch dùng cho hóa đơn bóng và lịch dùng cho tối ưu (có thể khác nhau); … | P0 · MVP/M1 · — | Phase 1 | F-TAR-03 | M-TAR | `TariffAssignment`, `TouCalendarVersion` | API-TAR-03, +API-TAR-04 | UI-25 | **T-FR-TAR-003** · Tích hợp · Site có điều khiển: đổi lịch tối ưu TT 16 → QĐ 963 ở trạng thái chờ xác nhận C2 (AC-TAR-05); lịch hóa đơn độc lập. |
| FR-TAR-004 | Mỗi điểm đo thanh toán (POC, công tơ trạm sạc riêng…) phải gắn được hợp đồng/biểu giá riêng; … | P0 · MVP/M1 · — | Phase 1 | F-TAR-04 | M-TAR | `TariffAssignment`, `MeteringPoint` | API-TAR-04 | UI-25, +UI-29 | **T-FR-TAR-004** · Đơn vị · POC và công tơ trạm sạc gắn biểu giá khác nhau; hóa đơn bóng tách theo điểm đo. |
| FR-TAR-005 | Hệ thống phải quản lý kỳ hóa đơn `(site, start_local, end_local)` theo ngày chốt chỉ số; kỳ … | P0 · MVP/M1 · — | Phase 1 | F-TAR-05 | M-TAR | `BillingPeriod` | API-TAR-05 | UI-25 | **T-FR-TAR-005** · Đơn vị · Kỳ chốt ngày 25 giờ site, biên nửa mở theo ngày địa phương; kỳ không chồng/hở. |
| FR-TAR-006 | Hệ thống phải tính hóa đơn bóng theo kỳ: Σ E_imp(k) × giá(khung(k)) cho mọi bucket 5 phút + … | P0 · MVP/M1 · — | Phase 1 | F-TAR-06 | M-TAR | `ShadowBill`, `ShadowBillLine`, `IntervalEnergy`, `TariffVersion` | API-TAR-06 | UI-25, +UI-10, +UI-30 | **T-FR-TAR-006** · Đơn vị · Σ E_imp × giá(khung) đúng; đổi giá ngày 15 (AC-TAR-06); MISSING → khoảng min/max (AC-REP-02). |
| FR-TAR-007 | Hệ thống phải kiểm hợp lệ và quản lý thay đổi biểu giá: chặn lịch có khoảng hở/chồng lấn; thay … | P0 · MVP/M1 · — | Phase 1 | F-TAR-01, F-REP-10 | M-TAR, M-REP | `TariffVersion`, `TouCalendarVersion`, `DirtyBucket` | API-TAR-01, API-TAR-02, API-REP-03 | UI-25 | **T-FR-TAR-007** · Đơn vị · Lịch hở 22:30–22:45 bị chặn (AC-TAR-03); sửa phiên bản đang áp → DirtyBucket `TARIFF_CHANGE` và restatement nếu vượt ngưỡng. |
| FR-TAR-008 | Hệ thống nên hỗ trợ thành phần công suất: `demand_window` (mặc định 30 phút block — UNKNOWN), … | P1 · hạng 03: Phase 1 · — | Phase 3 (3C) | F-TAR-07 | M-TAR | `TariffComponent`, `DemandWindow` | +API-TAR-02 | UI-25 | **T-FR-TAR-008** · Đơn vị · Cửa sổ 30 phút block; `demand_basis` mặc định tắt; cơ sở tính (đăng ký hay Pmax đo) là UNKNOWN nên tham số hóa. |
| FR-TAR-009 | Hệ thống nên lưu giá mua điện dư theo hợp đồng và tham số ngân sách xuất theo kỳ (mặc định 50% … | P1 · hạng 03: Phase 1 · — | Phase 3 (3D) | F-TAR-08 | M-TAR | `TariffComponent`, `ExportBudgetPeriod`, `Contract` | +API-TAR-02 | UI-25 | **T-FR-TAR-009** · Đơn vị · Giá mua điện dư theo hợp đồng áp cho E_exp; tham số tỷ lệ ngân sách xuất theo kỳ. |
| FR-TAR-010 | Hệ thống nên lưu ngưỡng cosφ theo hợp đồng (mặc định 0,9 tại điểm đặt công tơ) và cách tính … | P1 · hạng 03: Phase 1 · — | Phase 3 (3G) | F-TAR-09 | M-TAR | `TariffComponent`, `KpiValue` | +API-TAR-02 | UI-25 | **T-FR-TAR-010** · Đơn vị · PF tính từ kWh/kvarh tại điểm đo so ngưỡng 0,9; dưới ngưỡng → dòng phạt ước tính. |
| FR-TAR-011 | Hệ thống nên cho nhập hóa đơn EVN (tay hoặc file), so với hóa đơn bóng và với công tơ điều … | P1 · hạng 03: Phase 1 · — | Phase 2 | F-TAR-10 | M-TAR | ⚠ `UtilityBill` (05 thiếu), `ShadowBill` | API-TAR-07 | UI-25 | **T-FR-TAR-011** · Tích hợp · Nhập hóa đơn EVN, lệch > ngưỡng với hóa đơn bóng → cờ đối soát kèm thành phần lệch. |
| FR-TAR-012 | Hệ thống có thể nhận chuỗi giá 30 phút (DPPA ảo/thị trường) cho đối soát và tối ưu khi có cơ … | P2 · hạng 03: Phase 2 · — | Phase 4 (4B) | F-TAR-11 | M-TAR | ⚠ `PriceSeries` (05 thiếu) | ⚠ thiếu endpoint chuỗi giá | UI-25 | **T-FR-TAR-012** · Tích hợp · Nhận chuỗi giá 30 phút có phiên bản; dùng cho đối soát, không đổi hóa đơn bóng biểu giá EVN. |

### 3.7 M-BESS — BESS

| FR (04) | Yêu cầu (tóm tắt) | Ưu tiên · Hạng phát hành (04/03) · Hạng lệnh | Lộ trình (11) | F- (03) | Module | Thực thể (05) | API (06) | UI (09) | Test |
|---|---|---|---|---|---|---|---|---|---|
| FR-BESS-001 | Hệ thống phải giám sát BESS: SOC (giá trị BMS công bố, ghi có độ bất định), SOH (kèm định … | P0 · MVP/M1 · — | Phase 1 | F-BESS-01 | M-BESS | `Asset`, `Series`, `latest_value` | +API-TEL-02, +API-TEL-03 | UI-07 | **T-FR-BESS-001** · Mô phỏng · BMS mô phỏng: SOC hiển thị kèm độ bất định; trạng thái Sạc/Xả lấy từ PCS, không suy từ dấu. |
| FR-BESS-002 | Hệ thống phải lưu mô hình pin: `e_nominal`, `e_usable_bol`, `e_usable_current`, `soc_basis`, … | P0 · MVP/M1 · — | Phase 1 | F-BESS-03 | M-BESS | `Asset`, `SafeOperatingEnvelope` | +API-ORG-05 | UI-07 | **T-FR-BESS-002** · Đơn vị · `e_usable_current` và hai tầng dự phòng (hãng chỉ đọc, khách) tính đúng; năng lượng khả dụng không âm. |
| FR-BESS-003 | Edge phải ánh xạ chiến lược của ta xuống chế độ native của hãng qua driver `VERIFIED_*` theo … | P0 · MVP/M1 · C1 | Phase 1 | F-BESS-04 | M-BESS | `SiteControlConfig`, `CapabilityProfile`, `DriverVersion`, `DispatchCommand`, `CommandExecution` | +API-CMD-01, +API-CMD-02 (06 chưa ghi F-BESS-04) | UI-07, +UI-18, +UI-27 | **T-FR-BESS-003** · HIL · Đặt chế độ native qua SmartLogger/EMMA ở lab: readback khớp → APPLIED; ghi không tác dụng → `FAILED_NO_EFFECT` (T-FR-INT-007). Thêm T-FR-BESS-003-01…03 ([08 §6.6.4](08-energy-optimization.md): chỉ ghi khi đổi/trần ghi mỗi ngày; về `native_default_profile` khi hết hạn hoặc đổi biểu giá; validator V-N1…V-N4 khi edge offline). |
| FR-BESS-004 | Operator phải chọn được `site_strategy ∈ {SELF_CONSUMPTION, PEAK_SHAVING, TOU_SCHEDULE,` … | P0 · MVP/M1 · C1/C2 | Phase 1 | F-BESS-05 | M-BESS | `OptimizationStrategy`, `SiteControlConfig`, `CapabilityProfile` | API-CMD-01, API-OPT-01 | UI-07, UI-18, UI-21 | **T-FR-BESS-004** · Tích hợp · PEAK_SHAVING không xuất hiện khi capability thiếu (AC-BESS-08); đổi chiến lược mặc định là C2, override là C1 có hạn. |
| FR-BESS-005 | Operator phải gửi được `SET_ESS_P` với hạn mặc định 15 phút, tối đa 1 h, `on_expiry =` … | P0 · MVP/M2 · C1 | Phase 2 | F-BESS-06 | M-BESS | `DispatchCommand`, `CommandTransition`, `CommandExecution`, `SafeOperatingEnvelope` | API-CMD-01 | UI-07, UI-21 | **T-FR-BESS-005** · Mô phỏng · Xả 180 kW/SOE 250 kW → C1, hạn 15 phút (AC-BESS-01); 210 kW → step-up C2 (AC-BESS-02); hết hạn → mặc định (AC-BESS-03); UI chờ readback (AC-SEC-13). |
| FR-BESS-006 | Hệ thống phải cho `SET_SOC_RESERVE` trong giới hạn hãng và SOE; tăng mức là C1, giảm mức là C2 … | P0 · MVP/M1 · C1/C2 | Phase 1 | F-BESS-07 | M-BESS | `SafeOperatingEnvelope`, `DispatchCommand` | API-CMD-01 | UI-07, UI-21 | **T-FR-BESS-006** · Đơn vị · Tăng dự phòng là C1, giảm là C2 + step-up; ngoài giới hạn hãng → `REJECTED_OUT_OF_LIMIT`. |
| FR-BESS-007 | Hệ thống phải quản lý SOE theo site có version: P sạc/xả max, SOC min/max hiệu dụng, dự phòng, … | P0 · MVP/M2 · C3 | Phase 2 | F-BESS-08 | M-BESS | `SafeOperatingEnvelope`, `SiteGridConfigVersion`, `CommandApproval`, `AuditEvent` | API-CMD-08 | UI-07, UI-22, +UI-24 | **T-FR-BESS-007** · Mô phỏng · Người đề xuất không tự duyệt (AC-BESS-05); lệnh ngoài SOE → `REJECTED_OUT_OF_LIMIT` (AC-BESS-06); edge từ chối SOE version thấp hơn. |
| FR-BESS-008 | Hệ thống phải hiển thị chuỗi giới hạn: P thực tế / setpoint / P cho phép và nguồn giới hạn … | P0 · MVP/M1 · — | Phase 1 | F-BESS-09 | M-BESS | `CommandExecution`, `SafeOperatingEnvelope`, `Series` | API-CMD-02, +API-CMD-07 | UI-07 | **T-FR-BESS-008** · Mô phỏng · BMS hạ DCL về 0 khi đang xả → chuỗi hiện thực tế/setpoint/cho phép và nguồn "BMS" (T1-03 của 08). |
| FR-BESS-009 | Edge phải giám sát an toàn BESS tự động không cần cloud: dữ liệu BMS cũ hơn `T_stale_bms` hoặc … | P0 · MVP/M2 · C1 | Phase 2 | F-BESS-10 | M-BESS | `SafeOperatingEnvelope`, `Event`, `Alarm` | — (edge cục bộ; trạng thái qua API-CMD-07) | UI-07, +UI-24 | **T-FR-BESS-009** · HIL · BMS không cập nhật 6 s (`T_stale_bms`=5 s) → P = 0 W/native trong ≤ 2 chu kỳ (AC-BESS-04, T-NFR-REL-007-02). |
| FR-BESS-010 | Hệ thống phải đọc tín hiệu PCCC/khí/nhiệt phòng pin (DI hoặc Modbus) khi có và kích hoạt … | P0 · MVP/M1 · — | Phase 1 | F-BESS-18 | M-BESS | `Series`, `Alarm`, `AlarmDefinition` | +API-TEL-03, +API-ALM-01 | UI-07, +UI-14 | **T-FR-BESS-010** · HIL · DI báo cháy/khí → cảnh báo Khẩn cấp không tạm gác được (AC-ALM-03); IL-08 chặn lệnh; DI mất tín hiệu = tác động. |
| FR-BESS-011 | Hệ thống **không được** cung cấp API, nút hay lệnh để sửa thông số bảo vệ BMS/PCS/rơ-le hoặc … | CẤM · Không bao giờ (C4) · C4 | Ràng buộc từ Phase 1 (không xây chức năng) | F-BESS-19, F-BESS-20 | M-BESS | — (không có thực thể ghi) | Không có endpoint (kiểm bằng quét) | UI-07 (không có nút) | **T-FR-BESS-011** · Đơn vị · Quét OpenAPI cloud + tập lệnh edge: không có endpoint/command ghi ngưỡng BMS, grid code, rơ-le, E-stop (AC-BESS-07). |
| FR-BESS-012 | Hệ thống nên có drill-down L4 rack/module/cell: heatmap điện áp/nhiệt cell, cell lệch, lịch sử … | P1 · hạng 03: Phase 1 · — | Phase 3 (3F) | F-BESS-02 | M-BESS | `Asset`, `Series` | +API-TEL-02, +API-TEL-08 | UI-08 | **T-FR-BESS-012** · Mô phỏng · Heatmap 1.000 cell mô phỏng; cell min/max đánh dấu; dữ liệu cell `EDGE_ONLY` lấy theo yêu cầu. |
| FR-BESS-013 | Hệ thống nên tính KPI BESS: throughput, EFC (`E_ref` ghi rõ), RTE theo `rte_boundary` (chỉ … | P1 · hạng 03: Phase 1 · — | Phase 2 | F-BESS-11 | M-BESS | `KpiDefinition`, `KpiValue` | +API-TEL-06 | ⚠ 09 chưa ghi; +UI-07 | **T-FR-BESS-013** · Đơn vị · EFC = E_dis/`E_ref` ghi rõ; RTE theo `rte_boundary`; throughput từ thanh ghi. |
| FR-BESS-014 | Hệ thống nên hiển thị xu hướng SOH theo BMS và ước lượng dung lượng khả dụng từ chu kỳ sâu … | P1 · hạng 03: Phase 1 · — | Phase 3 (3F) | F-BESS-12 | M-BESS | `Series`, `KpiValue` | +API-TEL-02, +API-TEL-06 | ⚠ 09 chưa ghi; +UI-07 | **T-FR-BESS-014** · Đơn vị · SOH của BMS và dung lượng ước lượng hiển thị tách, ước lượng có nhãn "ước tính". |
| FR-BESS-015 | Hệ thống nên so EFC, throughput, SOC trung bình, nhiệt độ, chu kỳ/năm với điều khoản bảo hành … | P1 · hạng 03: Phase 1 · — | Phase 3 (3F) | F-BESS-13 | M-BESS | `Contract`, `KpiValue`, `Alarm` | +API-TEL-06 | ⚠ chưa có trang; đề xuất tab Bảo hành ở UI-07 | **T-FR-BESS-015** · Đơn vị · EFC lũy kế vượt 90% điều kiện bảo hành → cảnh báo Trung bình; đọc đúng phiên bản Contract. |
| FR-BESS-016 | Edge nên chia P giữa nhiều PCS/tủ theo SOC và giới hạn từng tủ khi controller native không làm. | P1 · hạng 03: Phase 1/M2 · C1 | Phase 3 (3F) | F-BESS-14 | M-BESS | `CommandExecution`, `SafeOperatingEnvelope`, `Asset` | — (edge) | ⚠ 09 chưa ghi; +UI-07 | **T-FR-BESS-016** · Mô phỏng · 2 PCS SOC khác nhau → chia P theo SOC; một tủ chạm giới hạn → phần dư chuyển tủ kia, không vượt tổng SOE. |
| FR-BESS-017 | Hệ thống nên theo dõi nguồn gốc năng lượng trong pin (từ PV hay lưới) để quy kết điện xuất khi … | P1 · hạng 03: Phase 1 · — | Phase 3 (3D) | F-BESS-15 | M-BESS | `BatteryEnergyLedger`, `FlowAttribution` | ⚠ thiếu endpoint sổ cái pin | ⚠ chưa có trang; đề xuất thẻ ở UI-07 | **T-FR-BESS-017** · Đơn vị · Sổ cái tách năng lượng nạp từ PV/lưới; kết quả gắn `attribution_version` và "ước tính". |
| FR-BESS-018 | Hệ thống nên cho "Dừng/khởi động vận hành từ xa" PCS (`DEVICE_ON_OFF`, không gọi là E-stop), … | P1 · hạng 03: Phase 1/M2 · C3 | Phase 3 (3F) | F-BESS-16 | M-BESS | `DispatchCommand`, `CommandApproval`, `AuditEvent` | +API-CMD-01 (type `DEVICE_ON_OFF`), +API-CMD-05 | ⚠ 09 chưa ghi; +UI-07, +UI-22 | **T-FR-BESS-018** · HIL · "Dừng vận hành từ xa" cần hai người duyệt; nhãn không dùng chữ E-stop; LOCAL chặn lệnh. |
| FR-BESS-019 | Hệ thống có thể cho reset lỗi từ xa chỉ khi hãng cho phép, hai người duyệt; mặc định reset tại … | P2 · hạng 03: Phase 2/M2 · C3 | Phase 4 (4H) | F-BESS-17 | M-BESS | `DispatchCommand`, `CapabilityProfile`, `CommandApproval` | +API-CMD-01, +API-CMD-05 | ⚠ chưa có trang (P2; đề xuất cạnh FR-BESS-018 ở UI-07) | **T-FR-BESS-019** · HIL · Chỉ hiện khi capability của hãng có tài liệu; mặc định tắt; hai người duyệt. |
| FR-BESS-020 | Hệ thống phải có SOE tối thiểu Gate M1 theo site, có version, ký số, duyệt C3 hai người: cấu hình lưới, SOC … | P0 · MVP/M1 · C3 | Phase 1 ⚠ (FR mới của 04; 11 chưa ghi) | F-BESS-08, F-GRID-03 | M-BESS, M-GRID | `SafeOperatingEnvelope`, `SiteGridConfigVersion`, `CommandApproval`, `AuditEvent` | +API-CMD-08 (06 chưa ghi FR-BESS-020) | ⚠ 09 chưa ghi FR; +UI-07, +UI-22, +UI-24 | **T-FR-BESS-020** · Tích hợp · Bật `control_enabled` Gate M1 khi chưa có SOE tối thiểu được duyệt → chặn; lệnh C2 đặt `export_limit_w` vượt SOE tối thiểu → PDP và edge cùng `REJECTED_OUT_OF_LIMIT`; trường SOE đầy đủ chưa có → lệnh M2 bị từ chối; người đề xuất tự duyệt bị chặn (T-NFR-SEC-008-01). |

### 3.8 M-PV — PV

| FR (04) | Yêu cầu (tóm tắt) | Ưu tiên · Hạng phát hành (04/03) · Hạng lệnh | Lộ trình (11) | F- (03) | Module | Thực thể (05) | API (06) | UI (09) | Test |
|---|---|---|---|---|---|---|---|---|---|
| FR-PV-001 | Hệ thống phải giám sát nhà máy PV và inverter: P, E ngày/tháng/tổng, trạng thái, mã lỗi, nhiệt … | P0 · MVP/M1 · — | Phase 1 | F-PV-01 | M-PV | `Asset`, `Series`, `latest_value` | +API-TEL-02, +API-TEL-03 | UI-09 | **T-FR-PV-001** · Mô phỏng · Inverter mô phỏng: P, E ngày/tổng, trạng thái; E ngày lấy từ thanh ghi, không tích phân P khi có thanh ghi. |
| FR-PV-002 | Hệ thống phải cho khai báo string (số module, kWp/string, hướng/nghiêng) và giám sát V/I … | P0 · MVP/M1 · — | Phase 1 | F-PV-02 | M-PV | `Asset`, `Series`, `AlarmRule` | +API-ORG-05 | UI-09 | **T-FR-PV-002** · Mô phỏng · G_POA 600 W/m² 16 phút, string 0 A, cùng MPPT 8 A → cảnh báo Trung bình (AC-PV-01). |
| FR-PV-003 | Hệ thống phải cho `SET_PV_LIMIT` (% hoặc W) qua logger/controller native hoặc edge; tôn trọng … | P0 · MVP/M1 · C1 | Phase 1 | F-PV-03 | M-PV | `DispatchCommand`, `CommandExecution` | API-CMD-01 | UI-09, +UI-21 | **T-FR-PV-003** · Mô phỏng · `SET_PV_LIMIT` 60% hạn 1 h → hết hạn về 100%, `EXPIRED` (AC-PV-03); site zero-export không cho nâng quá giới hạn. |
| FR-PV-004 | Hệ thống phải ước lượng điện năng bị cắt `E_curt ≈ Σ max(0, P_avail − P_actual)·Δt` khi đang … | P0 · MVP/M1 · — | Phase 1 | F-PV-04 | M-PV | `KpiValue`, `Series` | +API-TEL-06 | UI-09 | **T-FR-PV-004** · Đơn vị · P_avail 100 kW, phát 70 kW 15 phút → E_curt ≈ 7,5 kWh có nhãn ước tính (AC-PV-04). |
| FR-PV-005 | Hệ thống phải tính specific yield kWh/kWp theo ngày/tháng (kWp theo thời gian) và xếp hạng … | P0 · MVP/M1 · — | Phase 1 | F-PV-05 | M-PV | `KpiValue`, `Asset` | +API-TEL-06 | UI-09 | **T-FR-PV-005** · Đơn vị · kWp 500 → 800 từ 01/10: tháng 9 chia 500, tháng 10 chia 800 (AC-PV-05). |
| FR-PV-006 | Hệ thống nên tính PR = Yf/Yr chỉ khi có G_POA; PR hiệu chỉnh nhiệt khi có T_module; PR loại … | P1 · hạng 03: Phase 1 · — | Phase 2 | F-PV-06 | M-PV | `KpiValue`, `Series` | +API-TEL-06 | UI-09 | **T-FR-PV-006** · Đơn vị · Không có G_POA → N/A (AC-PV-02); có T_module → PR hiệu chỉnh nhiệt; không tuyên bố tuân thủ IEC 61724-1. |
| FR-PV-007 | Hệ thống nên tính availability PV theo thời gian và điện năng, loại trừ theo hợp đồng, mất kết … | P1 · hạng 03: Phase 1 · — | Phase 2 | F-PV-07 | M-PV | `KpiValue`, `MaintenanceWindow`, `Contract` | +API-TEL-06 | UI-09 | **T-FR-PV-007** · Đơn vị · Availability thời gian/điện năng; loại trừ theo hợp đồng; site `commissioning` không tính. |
| FR-PV-008 | Hệ thống nên so sánh đồng cấp (yield so median cùng hướng, cờ khi lệch > k·MAD), residual so … | P1 · hạng 03: Phase 1 · — | Phase 3 (3H) | F-PV-08 | M-PV | `KpiValue`, `AlarmRule` | +API-TEL-06 | UI-09 | **T-FR-PV-008** · Đơn vị · Inverter lệch median cùng hướng > k·MAD → cờ; nhóm < 3 inverter không so. |
| FR-PV-009 | Hệ thống nên tính sản lượng kỳ vọng từ bức xạ đo hoặc vệ tinh (clipping, curtail) và thác tổn … | P1 · hạng 03: Phase 1 · — | Phase 3 (3H) | F-PV-09 | M-PV | `ForecastValue`, `KpiValue` | +API-TEL-06 | UI-09 | **T-FR-PV-009** · Đơn vị · Sản lượng kỳ vọng từ bức xạ đo; tổn thất tách clipping/curtail; mọi số "ước tính". |
| FR-PV-010 | Hệ thống nên đọc thông số grid code/bảo vệ của inverter/PCS (chỉ đọc), so với hồ sơ đã duyệt … | P1 · hạng 03: Phase 1 · — | Phase 3 (3H) | F-PV-12 | M-PV | `Series`, `CapabilityProfile`, `Alarm` | +API-TEL-08 | UI-09 | **T-FR-PV-010** · Tích hợp · Đọc thông số grid code (chỉ đọc), lệch hồ sơ → cảnh báo; không có thao tác ghi. |
| FR-PV-011 | Hệ thống có thể hiển thị kết quả chẩn đoán I-V của hãng và kích hoạt quét qua công cụ hãng khi … | P2 · hạng 03: Phase 2/M1 · C1 | Phase 4 (4H) | F-PV-10 | M-PV | `DispatchCommand`, `CapabilityProfile` | +API-CMD-01 | UI-09 | **T-FR-PV-011** · HIL · Kích hoạt quét I-V chỉ khi capability có; hiển thị kết quả của hãng có nguồn. |
| FR-PV-012 | Hệ thống có thể hiển thị bố cục vật lý cấp module/optimizer tô theo hiệu suất. | P2 · hạng 03: Phase 2 · — | Phase 4 (4H) | F-PV-11 | M-PV | `Asset` | +API-ORG-05 | UI-09 | **T-FR-PV-012** · E2E · Bố cục module tô theo hiệu suất; module thiếu dữ liệu tô xám, không tô 0. |
| FR-PV-013 | Hệ thống có thể cho `SET_Q`/`SET_PF` cho inverter/PCS; khóa ở MVP và Phase 1. | P2 · hạng 03: Phase 2/M2 · C2 | Phase 4 (4H) | F-PV-13 | M-PV | `DispatchCommand`, `SafeOperatingEnvelope` | ⚠ chưa có type `SET_Q`/`SET_PF` ở API-CMD-01 | ⚠ chưa có trang (P2) | **T-FR-PV-013** · Mô phỏng · Q cùng hướng P tại điểm đo; PDP chặn ở MVP/Phase 1 (`NOT_PERMITTED`). |

### 3.9 M-GRID — Điểm đấu nối, tuân thủ lưới, phụ tải

| FR (04) | Yêu cầu (tóm tắt) | Ưu tiên · Hạng phát hành (04/03) · Hạng lệnh | Lộ trình (11) | F- (03) | Module | Thực thể (05) | API (06) | UI (09) | Test |
|---|---|---|---|---|---|---|---|---|---|
| FR-GRID-001 | Hệ thống phải cho khai báo GridConnection và `MTR_POC` (hoặc `MTR_POC_LV` khi không đặt được … | P0 · MVP/M1 · — | Phase 1 | F-GRID-01 | M-GRID | `GridConnection`, `MeteringPoint` | API-ORG-06 | UI-10, UI-29 | **T-FR-GRID-001** · Đơn vị · Không có `MTR_POC` qua phép thử dấu → chặn Gate M1 zero-export (AC-GRID-01); `MTR_POC_LV` chỉ khi không có MV. |
| FR-GRID-002 | Hệ thống phải có danh mục điểm đo chuẩn `MTR_PV`, `MTR_BESS`, `MTR_AUX`, `MTR_LOAD_i`, … | P0 · MVP/M1 · — | Phase 1 | F-GRID-02 | M-GRID | `MeteringPoint`, `MeteringPointConfigVersion` | API-ORG-06 | UI-10, UI-29 | **T-FR-GRID-002** · Mô phỏng · Công tơ mô phỏng khai báo `sign_convention` và `register_wrap`; edge chuẩn hóa dấu; CT ngược bị phát hiện. |
| FR-GRID-003 | Hệ thống phải lưu cấu hình lưới site: `export_mode ∈ {ZERO_EXPORT, EXPORT_LIMIT,` … | P0 · MVP/M1 · C3 | Phase 1 | F-GRID-03 | M-GRID | `SiteGridConfigVersion`, `CommandApproval`, `AuditEvent` | API-CMD-09 | UI-10, UI-29, +UI-22 | **T-FR-GRID-003** · Tích hợp · Đổi `export_limit_w` 0 → 50.000 chờ duyệt C3 người khác (AC-GRID-07); phiên bản cũ giữ nguyên. |
| FR-GRID-004 | Hệ thống phải đặt và kiểm chứng zero-export/giới hạn xuất trên logger/EMS hãng (`control_owner` … | P0 · MVP/M1 · C2 | Phase 1 | F-GRID-04 | M-GRID | `SiteGridConfigVersion`, `DispatchCommand`, `CommandExecution` | API-CMD-01 | UI-10 | **T-FR-GRID-004** · HIL · Đặt zero-export trên logger hãng ở lab, readback khớp; test bước tải (T-FR-INT-017). |
| FR-GRID-005 | Khi native không có chức năng, edge phải chạy vòng giới hạn xuất 1 s (PI có anti-windup, … | P0 · MVP/M2 · C2 | Phase 2 | F-GRID-05 | M-GRID | `SiteControlConfig`, `SiteGridConfigVersion`, `Event` | API-CMD-01, +API-CMD-09 | UI-10 | **T-FR-GRID-005** · HIL · Tải giảm bước 200 kW → xuất về ≤ giới hạn + tol ≤ 5 s (AC-GRID-03); xuất 6 kW 3 s → 1 sự kiện vi phạm (AC-GRID-02). |
| FR-GRID-006 | Hệ thống phải giữ P_nhập ≤ `import_cap_w` bằng BESS xả (và giảm EV khi có, P1); native trước, … | P0 · MVP/M1 · C2 | Phase 1 | F-GRID-06 | M-GRID | `SiteGridConfigVersion`, `SafeOperatingEnvelope` | API-CMD-01, +API-CMD-09 | UI-10 | **T-FR-GRID-006** · Mô phỏng · Nhập 850 kW > trần 800 kW → BESS xả thêm (AC-GRID-05); SOC ở dự phòng → xả tới `S_res_hard` (T1-05); `MTR_POC` cũ 4 s → BESS 0, PV về giới hạn native (AC-GRID-04). |
| FR-GRID-007 | Hệ thống phải hiện thanh live "nhập hiện tại / trần nhập" và "xuất / giới hạn xuất"; đếm số … | P0 · MVP/M1 · — | Phase 1 | F-GRID-07 | M-GRID | `latest_value`, `SiteGridConfigVersion` | +API-TEL-03, +API-LIVE-01 | UI-03, UI-10 | **T-FR-GRID-007** · E2E · Thanh live "Nhập 620/800 kW" và "Xuất 0/0 kW" có chữ hướng; mất `MTR_POC` → thanh xám. |
| FR-GRID-008 | Hệ thống phải đọc trạng thái rơ-le chống phát ngược, tín hiệu cắt giảm từ lưới và máy cắt POC … | P0 · MVP/M1 · — | Phase 1 | F-GRID-13 | M-GRID | `Series`, `Event`, `Alarm` | +API-TEL-03 | UI-10 | **T-FR-GRID-008** · HIL · Rơ-le chống phát ngược tác động (DI) → sự kiện + cảnh báo Cao; tín hiệu cắt giảm từ lưới hiển thị. |
| FR-GRID-009 | Hệ thống nên thực thi ngân sách xuất theo kỳ: E_exp_kỳ ≤ tỷ lệ × E_pv_kỳ; khi gần chạm thì ưu … | P1 · hạng 03: Phase 1/M2 · C2 | Phase 3 (3D) | F-GRID-08 | M-GRID | `ExportBudgetPeriod`, `DispatchPlan` | ⚠ thiếu endpoint ngân sách xuất | ⚠ 09 chưa ghi; +UI-10, +UI-25 | **T-FR-GRID-009** · Mô phỏng · Ngân sách gần cạn → kế hoạch giảm xuất/tăng sạc; kỳ tính UNKNOWN là tham số. |
| FR-GRID-010 | Hệ thống nên có đồng hồ demand: công suất trung bình cửa sổ hiện tại (mặc định 30 phút), dự … | P1 · hạng 03: Phase 1 · — | Phase 3 (3C) | F-GRID-09 | M-GRID | `DemandWindow`, `Aggregate` | ⚠ thiếu endpoint đồng hồ demand (đề xuất trong API-TEL-06/LIVE-01) | UI-03, UI-10 | **T-FR-GRID-010** · Đơn vị · Trung bình cửa sổ block 30 phút hiện tại và dự báo cuối cửa sổ; nhãn "dự kiến". |
| FR-GRID-011 | Hệ thống nên cảnh báo khi Pmax kỳ tiến gần công suất đăng ký hoặc ngưỡng người dùng đặt. | P1 · hạng 03: Phase 1 · — | Phase 3 (3C) | F-GRID-10 | M-GRID | `DemandWindow`, `Contract`, `Alarm` | ⚠ thiếu endpoint | ⚠ 09 chưa ghi; +UI-10 | **T-FR-GRID-011** · Đơn vị · Pmax kỳ đạt 90% công suất đăng ký → cảnh báo Trung bình. |
| FR-GRID-012 | Hệ thống nên giám sát PF tại POC tính lại từ kWh/kvarh (không trung bình PF), cảnh báo dưới … | P1 · hạng 03: Phase 1 · — | Phase 3 (3G) | F-GRID-11 | M-GRID | `Series`, `KpiValue` | +API-TEL-06 | UI-10 | **T-FR-GRID-012** · Đơn vị · PF từ kWh/kvarh theo kỳ, không trung bình PF tức thời; hai chiều nhập/xuất tách. |
| FR-GRID-013 | Edge nên nhận lệnh `GRID_OPERATOR` (giới hạn P, chặn phát ngược) qua slave IEC 104 … | P1 · hạng 03: Phase 1/M2 · C2 | Phase 2 (có điều kiện, V12) | F-GRID-12 | M-GRID | `DispatchCommand`, `CommandTransition`, `AuditEvent` | — (IEC 104 tại edge) | ⚠ 09 chưa ghi; +UI-24, +UI-26 | **T-FR-GRID-013** · Mô phỏng · Master 104 mô phỏng gửi setpoint khi cloud mất → arbiter mức 4 áp, ACT_CON sau readback (T-FR-INT-023). |
| FR-GRID-014 | Hệ thống nên hiển thị `grid_connected`, sự kiện mất lưới, thời lượng; đổi dạng cân bằng khi … | P1 · hạng 03: Phase 1 · — | Phase 3 (3G) | F-GRID-14 | M-GRID | `Series`, `Event` | +API-TEL-03 | ⚠ 09 chưa ghi; +UI-10 | **T-FR-GRID-014** · HIL · Mất lưới: sự kiện, thời lượng; energy flow đổi dạng "mất lưới". |
| FR-GRID-015 | Hệ thống nên hỗ trợ nhiều POC trong một site: cân bằng và giới hạn theo từng POC, không net … | P1 · hạng 03: Phase 1 · — | Phase 3 (3G) | F-GRID-15 | M-GRID | `GridConnection`, `MeteringPoint`, `EnergyBalance` | +API-ORG-06 | ⚠ 09 ghi F-GRID-15 ở UI-29 nhưng không ghi FR; +UI-10, +UI-29 | **T-FR-GRID-015** · Đơn vị · Cân bằng và giới hạn theo từng POC; tổng site là tổng các POC. |
| FR-GRID-016 | Hệ thống nên phân tích phụ tải: tải nền, tải không đo, hồ sơ tải theo giờ/thứ, top phụ tải. | P1 · hạng 03: Phase 1 · — | Phase 3 (3G) | F-GRID-16 | M-GRID | `EnergyBalance`, `Aggregate`, `SpecialDay` | +API-TEL-05 | ⚠ chưa có trang; đề xuất tab Phụ tải ở UI-10 | **T-FR-GRID-016** · Đơn vị · Tải nền, hồ sơ theo giờ/thứ; ngày lễ tách riêng. |
| FR-GRID-017 | Hệ thống nên giám sát máy phát (P, E, trạng thái, giờ chạy) và tách khỏi PV khi mất lưới. | P1 · hạng 03: Phase 1 · — | Phase 3 (3G) | F-GRID-17 | M-GRID | `Asset`, `Series` | +API-TEL-03 | ⚠ 09 chưa ghi; +UI-04 | **T-FR-GRID-017** · Mô phỏng · Máy phát mô phỏng: P, E, giờ chạy; không cộng vào PV trong cân bằng. |
| FR-GRID-018 | Hệ thống có thể đóng/cắt hoặc giảm phụ tải **không quan trọng** trong khung cho phép khi chạm … | P2 · hạng 03: Phase 2/M2 · C2 | Phase 4 (4H) | F-GRID-18 | M-GRID | `DispatchCommand`, `Asset` | ⚠ chưa có type lệnh phụ tải | ⚠ chưa có trang (P2) | **T-FR-GRID-018** · HIL · Chỉ phụ tải khai báo "không quan trọng"; có hạn; về trạng thái đóng khi hết hạn. |
| FR-GRID-019 | Hệ thống có thể bù công suất phản kháng bằng PCS để giữ PF tại POC. | P2 · hạng 03: Phase 2/M2 · C2 | Phase 4 (4H) | F-GRID-19 | M-GRID | `DispatchCommand`, `SafeOperatingEnvelope` | ⚠ chưa có type lệnh Q | ⚠ chưa có trang (P2) | **T-FR-GRID-019** · HIL · PCS bù Q giữ PF tại POC; không vượt S định mức; dấu Q theo quy ước. |

### 3.10 M-EV — Sạc xe điện

| FR (04) | Yêu cầu (tóm tắt) | Ưu tiên · Hạng phát hành (04/03) · Hạng lệnh | Lộ trình (11) | F- (03) | Module | Thực thể (05) | API (06) | UI (09) | Test |
|---|---|---|---|---|---|---|---|---|---|
| FR-EV-001 | Hệ thống phải hỗ trợ điểm đo `MTR_EV_i` cho từng trụ hoặc nhóm; EV tách khỏi tải nền trong cân … | P0 · MVP/M1 · — | Phase 1 | F-EV-01 | M-EV | `MeteringPoint`, `EnergyBalance` | +API-ORG-06, +API-TEL-05 | UI-11 | **T-FR-EV-001** · Đơn vị · `MTR_EV_1` 30 kWh/ngày tách khỏi tải nhà máy (AC-EV-01). |
| FR-EV-002 | Hệ thống nên giám sát trụ qua OCPP: trạng thái connector, phiên (bắt đầu/kết thúc, kWh từ … | P1 · hạng 03: Phase 1 · — | Phase 3 (3E) | F-EV-02 | M-EV | `EvSession`, `Asset`, `Series` | API-EV-01, API-EV-02 (vòng nhất quán) | UI-11 | **T-FR-EV-002** · Mô phỏng · Charger OCPP 1.6J mô phỏng: StatusNotification, Start/StopTransaction lưu thành EvSession. |
| FR-EV-003 | Edge nên làm CSMS OCPP 1.6J tối giản cho smart charging khi site không có CSMS của CPO; … | P1 · hạng 03: Phase 1/M2 · C1 | Phase 3 (3E) | F-EV-03 | M-EV | `Asset`, `EvSession`, `Integration` | API-EV-03 (vòng nhất quán) | ⚠ 09 chưa ghi; +UI-11, +UI-26 | **T-FR-EV-003** · Mô phỏng · Trụ đã có CSMS của CPO → chặn bật CSMS edge (AC-EV-04); Security Profile < 2 bị từ chối. |
| FR-EV-004 | Hệ thống nên nhận dữ liệu phiên từ CSMS của CPO (chỉ đọc); ghi giới hạn qua API CPO chỉ do edge gọi, có hạn, readback, fallback (CF-39); … | P1 · hạng 03: Phase 1/M2 · C1 | Phase 3 (3E) | F-EV-04 | M-EV | `Integration`, `EvSession` | API-EV-01, API-EV-02, API-EV-03, API-CMD-01 (`SET_EV_LIMIT`) | ⚠ 09 chưa ghi; +UI-11 | **T-FR-EV-004** · Tích hợp + Mô phỏng · API CPO mock: nhận phiên; giới hạn đi qua envelope ký → edge → CPO, TTL ≤ `expires_at`; readback lệch → `FAILED_NO_EFFECT`; CPO không trả lời → không gửi lại, `EV_CPO_LINK_LOST`; cờ ghi tắt → chỉ đọc (07 §8.10). |
| FR-EV-005 | Hệ thống nên cho `SET_EV_LIMIT` (A hoặc W, số pha) qua ChargePointMaxProfile/TxProfile có … | P1 · hạng 03: Phase 1/M2 · C1 | Phase 3 (3E) | F-EV-05 | M-EV | `DispatchCommand`, `CommandExecution` | +API-CMD-01 (type `SET_EV_LIMIT` chưa ghi ở 06) | UI-11, +UI-21 | **T-FR-EV-005** · Mô phỏng · Giới hạn có `validTo`; hết hạn hoặc mất kết nối → TxDefaultProfile an toàn, `EXPIRED` (AC-EV-03, T-FR-EV-005). |
| FR-EV-006 | Edge nên chạy DLM: phân bổ theo dư POC, `I_min`, ưu tiên, kWh cần trước giờ đi; cập nhật ≤ 1 … | P1 · hạng 03: Phase 1/M2 · C1 | Phase 3 (3E) | F-EV-06 | M-EV | `SafeOperatingEnvelope`, `EvSession` | — (edge; tham số qua API-CMD-08) | UI-11 | **T-FR-EV-006** · Mô phỏng · Dư 10 kW, 3 phiên: phiên ưu tiên cao nhận ≥ 6 A/pha (AC-EV-02); không vượt trần POC. |
| FR-EV-007 | Hệ thống nên có chế độ sạc chỉ bằng PV dư (hoặc tối thiểu + PV dư). | P1 · hạng 03: Phase 1/M2 · C1 | Phase 3 (3E) | F-EV-07 | M-EV | `SiteControlConfig`, `EvSession` | +API-OPT-01 | UI-11 | **T-FR-EV-007** · Mô phỏng · Sạc chỉ bằng PV dư: PV giảm → giới hạn giảm theo, không nhập lưới cho EV. |
| FR-EV-008 | Hệ thống nên gán biểu giá trạm sạc (FR-TAR-004) và báo cáo kWh/chi phí theo phiên, trụ, đội xe. | P1 · hạng 03: Phase 1 · — | Phase 3 (3E) | F-EV-08 | M-EV | `TariffAssignment`, `EvSession`, `ShadowBill` | API-EV-02, API-EV-04 (vòng nhất quán) | UI-11 | **T-FR-EV-008** · Đơn vị · kWh và chi phí theo phiên × khung TOU; tổng khớp `MTR_EV`. |
| FR-EV-009 | Hệ thống có thể dự báo phiên sạc (số phiên, năng lượng, giờ đến/đi). | P2 · hạng 03: Phase 2 · — | Phase 4 (4G) | F-EV-09 | M-EV | `ForecastRun`, `ForecastValue` | ⚠ thiếu API | ⚠ chưa có trang (P2) | **T-FR-EV-009** · Đơn vị · Dự báo phiên sạc có nhãn phương pháp; không gọi là AI. |
| FR-EV-010 | Hệ thống có thể hỗ trợ OCPP 2.0.1/2.1, ISO 15118, V2X. | P2 · hạng 03: Phase 2/M2 · C1 | Phase 4 (4H) | F-EV-10 | M-EV | `Asset`, `EvSession` | ⚠ thiếu API | ⚠ chưa có trang (P2) | **T-FR-EV-010** · Mô phỏng · OCPP 2.0.1 mô phỏng; ISO 15118/V2X chỉ khi có thiết bị thử. |

### 3.11 M-OPT — Tối ưu, lập lịch, điều phối

| FR (04) | Yêu cầu (tóm tắt) | Ưu tiên · Hạng phát hành (04/03) · Hạng lệnh | Lộ trình (11) | F- (03) | Module | Thực thể (05) | API (06) | UI (09) | Test |
|---|---|---|---|---|---|---|---|---|---|
| FR-OPT-001 | Edge phải có **một** arbiter: mọi nguồn lệnh (điều độ, operator, lịch, optimizer, DR, API) đi … | P0 · MVP/M2 · C1 | Phase 2 | F-OPT-01 | M-OPT | `SiteControlConfig`, `CommandExecution` | — (edge; kết quả qua API-CMD-07) | UI-18 | **T-FR-OPT-001** · Mô phỏng · Lệnh tay xả 300 kW (mức 7) + giới hạn xuất 0 (mức 4), tải 200 kW → xả ≤ 200 kW trừ margin (AC-OPT-01); test thuộc tính: mức 1–6 không đổi thứ tự. |
| FR-OPT-002 | Arbiter phải báo theo chu kỳ: mức đang thắng, khoảng cho phép hiện hành, mã lý do … | P0 · MVP/M2 · — | Phase 2 | F-OPT-01, F-DASH-04 | M-OPT, M-DASH | `SiteControlConfig`, `EdgeNode` | API-LIVE-01, +API-CMD-07 | UI-03, UI-18, UI-24 | **T-FR-OPT-002** · Mô phỏng · Mã lý do và mức thắng hiển thị khớp trạng thái arbiter trong mỗi kịch bản T1-01…T1-06. |
| FR-OPT-003 | Hệ thống phải lưu `control_owner ∈ {NATIVE, EDGE}` cho từng chức năng (zero-export, import … | P0 · MVP/M1 · C3 | Phase 1 | F-OPT-02 | M-OPT | `SiteControlConfig`, `CommandApproval` | API-CMD-07, API-CMD-09 | UI-18, UI-24 | **T-FR-OPT-003** · Tích hợp · Bật vòng edge khi `control_owner=NATIVE` → yêu cầu đổi chủ vòng C3, không cho hai vòng (AC-OPT-05, AC-GRID-06, T1-07). |
| FR-OPT-004 | Khi `control_owner = EDGE`, edge phải chạy tầng 1 chu kỳ 1 s: balancing về `p_grid_target` … | P0 · MVP/M2 · C1 | Phase 2 | F-OPT-03 | M-OPT | `SafeOperatingEnvelope`, `SiteControlConfig` | — (edge) | UI-18 | **T-FR-OPT-004** · HIL · T1-01…T1-06 của 08 §5.8 trên HIL; `cycle_time_ms` p99 ≤ 200 ms (NFR-PERF-006). |
| FR-OPT-005 | Cloud phải chạy bộ sinh lịch luật TOU (tầng 2) lúc 05:30 giờ site và khi có sự kiện: lịch 48 … | P0 · MVP/M1 · C1 | Phase 1 | F-OPT-04 | M-OPT | `OptimizationStrategyVersion`, `DispatchPlan`, `PlanSlot`, `ForecastRun`, `TariffVersion` | API-OPT-01, API-OPT-06 | UI-18, UI-19 | **T-FR-OPT-005** · Đơn vị · Thứ Ba QĐ 963 sinh lịch đúng SOC đích (AC-OPT-02); Chủ nhật không có `GRID_CHARGE_TO_TARGET`/`PEAK_DISCHARGE` (AC-OPT-03). |
| FR-OPT-006 | Edge phải lưu lịch ≥ 48 h; hết lịch hoặc lịch hỏng → chiến lược mặc định an toàn của site … | P0 · MVP/M1 · C1 | Phase 1 | F-OPT-05 | M-OPT | `DispatchPlan`, `SiteControlConfig` | API-OPT-07 | UI-18, +UI-24 | **T-FR-OPT-006** · Mô phỏng · Mất cloud, plan hết lúc 10:00 ngày kia → chiến lược mặc định (AC-OPT-04, T-NFR-REL-001-01). |
| FR-OPT-007 | DispatchPlan phải theo vòng đời DRAFT → VALIDATED → APPROVED → SCHEDULED → EXECUTING → … | P0 · MVP/M1 · C1 | Phase 1 | F-OPT-06 | M-OPT | `DispatchPlan`, `PlanSlot` | API-OPT-02, API-OPT-04 | UI-19, UI-20 | **T-FR-OPT-007** · Đơn vị · Sửa slot plan APPROVED v4 → v5 DRAFT, v4 không đổi (AC-OPT-06); không `ACCEPTED` trong 300 s → "Chưa đồng bộ" (AC-OPT-08). |
| FR-OPT-008 | Validator phải kiểm mọi slot trước khi gửi: trong trần site; quỹ đạo SOC trong [S_min, S_max]; … | P0 · MVP/M1 · — | Phase 1 | F-OPT-07 | M-OPT | `PlanSlot`, `SafeOperatingEnvelope` | API-OPT-04, +API-CMD-04 | UI-19 | **T-FR-OPT-008** · Đơn vị · Slot vượt trần site hoặc quỹ đạo SOC ngoài [min,max] → plan `REJECTED` kèm mã lý do; plan hợp lệ qua. |
| FR-OPT-009 | Hệ thống phải hiển thị kế hoạch 48 h: dải TOU, dự báo PV/tải, kế hoạch BESS (Xả lên/Sạc xuống, … | P0 · MVP/M1 · — | Phase 1 | F-OPT-08 | M-OPT | `DispatchPlan`, `PlanSlot`, `ForecastValue`, `TouCalendarVersion` | API-LIVE-04, API-OPT-02, API-OPT-03 | UI-19 | **T-FR-OPT-009** · E2E · Kế hoạch 48 h: dải TOU, dự báo có nhãn, trạng thái đồng bộ edge. |
| FR-OPT-010 | Hệ thống phải lưu `plan_slot_result` theo slot: mode kế hoạch/thực tế, năng lượng BESS, SOC … | P0 · MVP/M1 · — | Phase 1 | F-OPT-10 | M-OPT | `PlanSlotResult` | API-OPT-05 | UI-20 | **T-FR-OPT-010** · Đơn vị · `deviation_cause` đúng cho các ca OVERRIDDEN, CLAMPED_BY_BMS, OFFLINE. |
| FR-OPT-011 | Hệ thống phải giải thích theo slot bằng mã lý do + câu mẫu (ví dụ "17:30–17:45: xả 180 kW vì … | P0 · MVP/M1 · — | Phase 1 | F-OPT-11 | M-OPT | `PlanSlot` | API-OPT-03 | UI-19 | **T-FR-OPT-011** · Đơn vị · Slot 17:30–17:45 có `DISCHARGE_PEAK_TOU` và câu mẫu có giá cao điểm hiện hành (AC-OPT-07); bản en có đơn vị. |
| FR-OPT-012 | Hệ thống nên có trình soạn lịch thủ công: kéo thả khối chế độ, nhập số theo ô, mẫu ngày, cửa … | P1 · hạng 03: Phase 1/M2 · C2 | Phase 3 (3A) | F-OPT-09 | M-OPT | `DispatchPlan`, `PlanSlot`, `CommandApproval` | API-OPT-08 | UI-19 | **T-FR-OPT-012** · E2E · Kéo thả khối chế độ → validator chạy → duyệt C2/C3 theo mức nới; plan cũ giữ phiên bản. |
| FR-OPT-013 | Hệ thống nên hiển thị giá trị biên (shadow price) của 1 kWh trong pin theo slot và của 1 kW … | P1 · hạng 03: Phase 1 · — | Phase 3 (3A) | F-OPT-12 | M-OPT | `PlanSlot` | ⚠ chưa có trường shadow price trong API-OPT-03 | UI-19 | **T-FR-OPT-013** · Đơn vị · Chỉ hiện cho plan tầng 3; nhãn "Tối ưu dựa trên dự báo". |
| FR-OPT-014 | Hệ thống nên có Optimization Service tầng 3: horizon 48 h, Δt 15 phút, giải lại mỗi 15 phút và … | P1 · hạng 03: Phase 1/M2 · C1 | Phase 3 (3A) | F-OPT-13 | M-OPT | `OptimizationStrategyVersion`, `BacktestRun`, `DispatchPlan` | +API-OPT-01 | UI-18 | **T-FR-OPT-014** · Tích hợp · Solver quá thời gian → dùng plan tầng 2; tầng 3 chỉ bật khi BacktestRun đạt cổng. |
| FR-OPT-015 | Hệ thống nên cho tham số chi phí suy hao `c_deg` (đ/kWh xả) theo site, hiển thị trên UI; không … | P1 · hạng 03: Phase 1 · — | Phase 3 (3A) | F-OPT-14 | M-OPT | `OptimizationStrategyVersion` | +API-OPT-01 | UI-18 | **T-FR-OPT-015** · Đơn vị · `c_deg` thay đổi làm số chu kỳ trong plan giảm đơn điệu; hiển thị đơn vị đ/kWh. |
| FR-OPT-016 | Hệ thống nên có backtest: phát lại lịch sử qua code tầng 2/3 với dự báo "như đã có", mô hình … | P1 · hạng 03: Phase 1 · — | Phase 3 (3A) | F-OPT-15 | M-OPT | `BacktestRun`, `ForecastRun`, `TariffVersion` | API-OPT-09 | UI-18 | **T-FR-OPT-016** · Tích hợp · Phát lại 30 ngày với dự báo "như đã phát hành", cùng tariff version; kết quả nhãn "Mô phỏng". |
| FR-OPT-017 | Hệ thống nên có peak shaving theo demand: `P_allow_rest = (P_target·T_w − E_so_far)/(T_w −` … | P1 · hạng 03: Phase 1/M2 · C1 | Phase 3 (3C) | F-OPT-16 | M-OPT | `DemandWindow`, `SiteControlConfig` | +API-OPT-01 | ⚠ 09 chưa ghi; +UI-18, +UI-10 | **T-FR-OPT-017** · Mô phỏng · `P_allow_rest` theo công thức; cửa sổ block; peak giữ dưới mục tiêu khi SOC đủ. |
| FR-OPT-018 | Hệ thống nên đưa ngân sách xuất theo kỳ vào bộ sinh lịch, tôn trọng `allow_grid_charge`, … | P1 · hạng 03: Phase 1/M2 · C1 | Phase 3 (3D) | F-OPT-17 | M-OPT | `ExportBudgetPeriod`, `DispatchPlan` | +API-OPT-01 | ⚠ 09 chưa ghi; +UI-19 | **T-FR-OPT-018** · Mô phỏng · Ngân sách gần cạn → plan tăng sạc/giảm xuất; tôn trọng `allow_grid_charge`. |
| FR-OPT-019 | Hệ thống nên tăng dự phòng SOC khi có cảnh báo bão/mất điện theo lịch, sau khi người dùng xác … | P1 · hạng 03: Phase 1/M1 · C1 | Phase 3 (3A) | F-OPT-18 | M-OPT | `SafeOperatingEnvelope`, `DispatchCommand` | +API-CMD-01 | ⚠ 09 chưa ghi; +UI-18 | **T-FR-OPT-019** · Tích hợp · Cảnh báo bão → đề xuất tăng dự phòng chờ người xác nhận; nguồn cảnh báo ghi rõ. |
| FR-OPT-020 | Hệ thống có thể khởi động/dừng máy phát khi SOC thấp hoặc mất lưới qua DO/controller genset. | P2 · hạng 03: Phase 2/M2 · C2 | Phase 4 (4H) | F-OPT-19 | M-OPT | `DispatchCommand`, `Asset` | ⚠ chưa có type lệnh máy phát | ⚠ chưa có trang (P2) | **T-FR-OPT-020** · HIL · SOC thấp khi mất lưới → lệnh chạy máy phát qua DO/controller; native ATS vẫn ưu tiên. |
| FR-OPT-021 | Hệ thống có thể tạo FlexibilityOffer (kW lên/xuống theo slot), nhận sự kiện DR trong envelope … | P2 · hạng 03: Phase 2/M2 · C1 | Phase 4 (4A) | F-OPT-20 | M-OPT | ⚠ `FlexibilityOffer` (05 thiếu), `DispatchPlan` | ⚠ thiếu API DR/VPP | ⚠ chưa có trang (P2) | **T-FR-OPT-021** · Mô phỏng · Sự kiện DR mô phỏng ở mức 8 arbiter, không vượt mức 1–7; nhãn "VPP-capable". |

### 3.12 M-ALM — Cảnh báo, O&M

| FR (04) | Yêu cầu (tóm tắt) | Ưu tiên · Hạng phát hành (04/03) · Hạng lệnh | Lộ trình (11) | F- (03) | Module | Thực thể (05) | API (06) | UI (09) | Test |
|---|---|---|---|---|---|---|---|---|---|
| FR-ALM-001 | Hệ thống phải nhận mã lỗi từ driver/connector, ánh xạ sang danh mục cảnh báo chuẩn (mã, mức … | P0 · MVP/M1 · — | Phase 1 | F-ALM-01 | M-ALM | `AlarmDefinition`, `Alarm`, `Event` | +API-ALM-01 | UI-14 | **T-FR-ALM-001** · Tích hợp · Mã lỗi driver → cảnh báo chuẩn; mã lạ → cảnh báo chung kèm mã thô; mức theo bộ nhãn Khẩn cấp/Cao/Trung bình/Thông tin. |
| FR-ALM-002 | Hệ thống phải chạy L0 kiểm tra dữ liệu (phạm vi vật lý, kiểu, đóng băng `FROZEN`, gai, lệch … | P0 · MVP/M1 · — | Phase 1 | F-ALM-02 | M-ALM | `AlarmRule`, `ts_gauge` | ⚠ không có | UI-14 | **T-FR-ALM-002** · Đơn vị · G_POA đứng yên 2 h → `FROZEN` (AC-MON-07); giá trị ngoài phạm vi vật lý → `BAD_*`. |
| FR-ALM-003 | Hệ thống phải có quy tắc L1: ngưỡng có hysteresis và thời gian tối thiểu, mẫu theo loại tài … | P0 · MVP/M1 · — | Phase 1 | F-ALM-03 | M-ALM | `AlarmRule` | API-ALM-04 | UI-14, UI-32 | **T-FR-ALM-003** · Đơn vị · G_POA 500 W/m² 14 phút + P = 0 → cảnh báo phút 15; G_POA giảm ở phút 10 → không (AC-ALM-07). |
| FR-ALM-004 | Hệ thống phải sinh một cảnh báo kết nối cho edge/gateway/site sau `T_offline_alarm_edge` (hoặc … | P0 · MVP/M1 · — | Phase 1 | F-ALM-04 | M-ALM | `Alarm` | +API-ALM-01 | UI-14 | **T-FR-ALM-004** · Mô phỏng · Edge mất 13:40 → 13:45 đúng một cảnh báo Cao; cảnh báo thiết bị con `SUPPRESSED_BY_PARENT` (AC-ALM-01). |
| FR-ALM-005 | Hệ thống phải có console cảnh báo theo vòng đời ở trên: tab Active/chưa ack, Active/đã ack, Đã … | P0 · MVP/M1 · — | Phase 1 | F-ALM-05 | M-ALM | `Alarm`, `AuditEvent` | API-LIVE-03, API-ALM-01, API-ALM-03 | UI-14 | **T-FR-ALM-005** · E2E · Tạm gác cảnh báo an toàn bị vô hiệu, API `SHELVE_NOT_ALLOWED_SAFETY` (AC-ALM-03); 10.000 dòng lọc p95 ≤ 2 s. |
| FR-ALM-006 | Hệ thống phải có chi tiết cảnh báo: biểu đồ ±2 h quanh thời điểm kích hoạt, lịch sử cùng mã … | P0 · MVP/M1 · — | Phase 1 | F-ALM-06 | M-ALM | `Alarm`, `Event`, ⚠ `OnCallContact` (05 thiếu) | API-ALM-02, API-ALM-11 (vòng nhất quán) | UI-15 | **T-FR-ALM-006** · E2E · Chi tiết có biểu đồ ±2 h, lịch sử chuyển trạng thái, liên hệ trực ca (catalog gap GAP-08). |
| FR-ALM-007 | Người dùng phải đăng ký nhận thông báo theo site × mức × loại, có giờ yên lặng; tenant chọn … | P0 · MVP/M1 · — | Phase 1 | F-ALM-08 | M-ALM | `NotificationSubscription` | API-ALM-05 | UI-17 | **T-FR-ALM-007** · Tích hợp · Giờ yên lặng chặn mức Trung bình; mức Khẩn cấp vẫn gửi. |
| FR-ALM-008 | Hệ thống phải gửi thông báo in-app và e-mail có deep-link; gộp nhiều cảnh báo thành một tin … | P0 · MVP/M1 · — | Phase 1 | F-ALM-09 | M-ALM | `Notification` | ⚠ thiếu endpoint trung tâm thông báo in-app | UI-17 | **T-FR-ALM-008** · Tích hợp · p95 sự kiện → e-mail ≤ 2 phút trên 1.000 sự kiện (AC-ALM-02); gộp cảnh báo; deep-link mở đúng UI-15. |
| FR-ALM-009 | Hệ thống phải có cảnh báo tuân thủ lưới mức mặc định Cao: sự kiện vi phạm xuất (§2), vượt trần … | P0 · MVP/M1 · — | Phase 1 | F-ALM-13 | M-ALM | `Alarm`, `Event`, `SiteGridConfigVersion` | API-ALM-04 | UI-10, UI-14 | **T-FR-ALM-009** · Mô phỏng · Xuất vượt giới hạn + tol 3 s → cảnh báo tuân thủ Cao có thời lượng, đỉnh (AC-ALM-08, AC-GRID-02). |
| FR-ALM-010 | Hệ thống phải cho tạo ticket từ cảnh báo (thủ công; theo quy tắc là tùy chọn) mang ngữ cảnh … | P0 · MVP/M1 · — | Phase 1 | F-ALM-14 | M-ALM | `Ticket`, `Alarm`, `Notification` | API-ALM-06 | UI-15, UI-16 | **T-FR-ALM-010** · E2E · Tạo ticket từ cảnh báo, giao kỹ thuật viên K, K nhận thông báo (AC-ALM-04); đóng thiếu nguyên nhân gốc bị chặn (AC-ALM-05). |
| FR-ALM-011 | Hệ thống phải cảnh báo về lệnh và kế hoạch: `UNDELIVERED`, `REJECTED_*`, `FAILED_NO_EFFECT`, … | P0 · MVP/M1 · — | Phase 1 | F-ALM-21 | M-ALM | `Alarm`, `DispatchCommand`, `DispatchPlan` | +API-ALM-01 | UI-14 | **T-FR-ALM-011** · Mô phỏng · `FAILED_NO_EFFECT` → cảnh báo Cao có `command_id` (AC-ALM-06); lệch trạng thái lệnh sau kết nối lại (AC-INT-09). |
| FR-ALM-012 | Hệ thống nên gom lũ cảnh báo (> N cảnh báo/10 phút tại một site → một dòng "Lũ cảnh báo" có … | P1 · hạng 03: Phase 1 · — | Phase 2 | F-ALM-07 | M-ALM | `Alarm` | +API-ALM-01 | UI-14 | **T-FR-ALM-012** · Đơn vị · > N cảnh báo/10 phút ở một site → một dòng "Lũ cảnh báo"; khử dao động bằng hysteresis. |
| FR-ALM-013 | Hệ thống nên gửi cảnh báo qua Zalo (OA/ZNS) theo template đã duyệt, deep-link, gộp tin, tùy … | P1 · hạng 03: Phase 1 · — | Phase 2 | F-ALM-10 | M-ALM | `Notification`, `NotificationSubscription` | +API-ALM-05 | UI-17 | **T-FR-ALM-013** · Tích hợp · Gửi qua Zalo sandbox theo template; template chưa duyệt → không gửi, ghi lỗi (điều kiện Zalo UNKNOWN). |
| FR-ALM-014 | Hệ thống nên có push di động/web push; SMS chỉ cho mức Khẩn cấp nếu khách yêu cầu. | P1 · hạng 03: Phase 1 · — | Phase 3 (3K) | F-ALM-11 | M-ALM | `Notification` | +API-ALM-05 | UI-17 | **T-FR-ALM-014** · Tích hợp · Push web/di động; SMS chỉ Khẩn cấp khi khách bật. |
| FR-ALM-015 | Hệ thống nên leo thang khi cảnh báo Khẩn cấp/Cao không được ack trong T phút và có lịch trực … | P1 · hạng 03: Phase 1 · — | Phase 2 | F-ALM-12 | M-ALM | ⚠ `EscalationPolicy` (05 thiếu), `Notification` | API-ALM-11, API-ALM-12 (vòng nhất quán) | UI-17 | **T-FR-ALM-015** · Tích hợp · Cảnh báo Cao không ack trong T phút → leo thang mức 2; ack dừng leo thang. |
| FR-ALM-016 | Hệ thống nên tạo work order từ ticket: kỹ thuật viên, lịch, checklist theo loại tài sản, … | P1 · hạng 03: Phase 1 · — | Phase 2 | F-ALM-15 | M-ALM | `WorkOrder`, `Ticket` | API-ALM-07 | UI-16 | **T-FR-ALM-016** · E2E · Ticket → work order có checklist; kỹ thuật viên chỉ thấy việc được giao (vai trò TECHNICIAN). |
| FR-ALM-017 | Hệ thống nên theo dõi SLA: thời gian phản hồi/khắc phục theo mức, MTTR, tổn thất kWh ước tính … | P1 · hạng 03: Phase 1 · — | Phase 2 | F-ALM-16 | M-ALM | `Ticket`, ⚠ `SlaPolicy` (05 thiếu) | API-ALM-13 (vòng nhất quán) | UI-16 | **T-FR-ALM-017** · Đơn vị · MTTR và thời gian phản hồi theo mức; loại trừ thời gian WAITING theo hợp đồng. |
| FR-ALM-018 | Hệ thống nên có kế hoạch bảo trì định kỳ (vệ sinh tấm, chụp nhiệt, kiểm tra BESS…) tự sinh … | P1 · hạng 03: Phase 1 · — | Phase 2 | F-ALM-17 | M-ALM | `MaintenanceWindow`, `WorkOrder` | API-ALM-08 | UI-16 | **T-FR-ALM-018** · Tích hợp · Kế hoạch PM sinh work order đúng chu kỳ; cảnh báo trong cửa sổ bảo trì → `OUT_OF_SERVICE`. |
| FR-ALM-019 | Người dùng nên đánh dấu cảnh báo đúng/sai và nguyên nhân gốc; lưu làm nhãn cho mô hình có đánh … | P1 · hạng 03: Phase 1 · — | Phase 2 | F-ALM-18 | M-ALM | `Alarm`, `Ticket` | +API-ALM-03, +API-ALM-06 | UI-15 | **T-FR-ALM-019** · Đơn vị · Nhãn đúng/sai và nguyên nhân gốc lưu theo danh mục; dùng làm nhãn cho FR-ADV-008. |
| FR-ALM-020 | Hệ thống nên đồng bộ hai chiều ticket/work order với CMMS của khách qua API/webhook, khóa … | P1 · hạng 03: Phase 1 · — | Phase 3 (3K) | F-ALM-19 | M-ALM | `Ticket`, `WorkOrder` | +API-PUB-03, ⚠ thiếu API nhận cập nhật từ CMMS | UI-16 | **T-FR-ALM-020** · Tích hợp · Đồng bộ hai chiều với CMMS mock; xung đột cập nhật giải theo thời điểm và ghi audit. |
| FR-ALM-021 | Hệ thống nên phát hiện bất thường thống kê L2 (peer, residual, CUSUM/EWMA cho PR, RTE, aux), … | P1 · hạng 03: Phase 1 · — | Phase 3 (3K) | F-ALM-20 | M-ALM | `AlarmRule`, `KpiValue` | +API-ALM-04 | ⚠ 09 chưa ghi; +UI-14 | **T-FR-ALM-021** · Đơn vị · CUSUM/EWMA trên PR phát hiện suy giảm 3%; nhãn "Thống kê", không "AI". |
| FR-ALM-022 | Hệ thống nên phát hiện điều khiển ngoài: `EXTERNAL_CONTROL_DETECTED` khi chế độ/setpoint thiết … | P1 · hạng 03: Phase 1 · — | Phase 2 | F-ALM-22 | M-ALM | `Event`, `Alarm`, `SiteControlConfig` | +API-ALM-01 | ⚠ 09 chưa ghi; +UI-14, +UI-24 | **T-FR-ALM-022** · HIL · Đổi chế độ BESS qua app hãng → `EXTERNAL_CONTROL_DETECTED` trong 2 chu kỳ đọc. |

### 3.13 M-INT — Tích hợp, edge, commissioning

| FR (04) | Yêu cầu (tóm tắt) | Ưu tiên · Hạng phát hành (04/03) · Hạng lệnh | Lộ trình (11) | F- (03) | Module | Thực thể (05) | API (06) | UI (09) | Test |
|---|---|---|---|---|---|---|---|---|---|
| FR-INT-001 | Edge của ta phải bắt buộc ở mọi site mà nền tảng ghi lệnh; PDP chặn mọi lệnh tới site không có … | P0 · MVP/M1 · — | Phase 1 | F-INT-01 | M-INT | `EdgeNode`, `Site` | — (quy tắc PDP; mọi API-CMD) | UI-26 | **T-FR-INT-001** · Tích hợp · Lệnh tới site không có edge của ta → PDP từ chối; site chỉ connector chỉ đọc. |
| FR-INT-002 | Hệ thống phải cho claim edge bằng QR/serial, cấp chứng chỉ X.509 riêng (mTLS, hạn 90 ngày, tự … | P0 · MVP/M1 · — | Phase 1 | F-INT-02 | M-INT | `EdgeNode`, `AuditEvent` | API-INT-01, API-INT-02 | UI-26, +UI-27 | **T-FR-INT-002** · Tích hợp · Quét QR gán site → chứng chỉ 90 ngày, kết nối `ems/v1/{edge_id}/…` (AC-INT-01); edge đã gán site khác bị từ chối. |
| FR-INT-003 | Hệ thống phải có framework driver khai báo: register map YAML/JSON có version (word order, … | P0 · MVP/M1 · — | Phase 1 | F-INT-03 | M-INT | `DriverDefinition`, `DriverVersion`, `PointDefinition` | +API-INT-06 | UI-28 | **T-FR-INT-003** · Đơn vị · 100% vector vàng đạt (I32 CDAB, SF âm, sentinel, U32 quay vòng) (T-FR-INT-003 của 07). |
| FR-INT-004 | Edge phải là Modbus master duy nhất trên mỗi bus/thiết bị; gom thanh ghi (≤ 125 thanh ghi/lần … | P0 · MVP/M1 · — | Phase 1 | F-INT-04 | M-INT | `DeviceEndpoint`, `DriverVersion` | — (edge) | UI-28 | **T-FR-INT-004** · Mô phỏng · Edge là master duy nhất; block ≤ 125 đọc/≤ 123 ghi; không vắt lỗ địa chỉ (T-FR-INT-004). |
| FR-INT-005 | Edge phải khám phá SunSpec (quét "SunS" tại 40000/50000/0; đọc model 1, 101–103, 120–124, … | P0 · MVP/M1 · — | Phase 1 | F-INT-05 | M-INT | `CapabilityProfile`, `DeviceModel` | — (edge) | UI-28 | **T-FR-INT-005** · Mô phỏng · Khám phá SunSpec ở 40000/50000/0, dừng ở 0xFFFF, profile khớp (T-FR-INT-005). |
| FR-INT-006 | Thư viện driver MVP phải có, theo thứ tự: (1) công tơ PCC Modbus phổ biến; (2) Huawei … | P0 · MVP/M1 · — | Phase 1 | F-INT-06 | M-INT | `DriverVersion`, `DeviceModel` | +API-INT-06 | UI-28 | **T-FR-INT-006** · HIL · Mỗi driver MVP đạt `VERIFIED_LAB` trên lab L5; driver `COMMUNITY` chỉ đọc, lệnh bị IL-05 (AC-INT-03). |
| FR-INT-007 | Edge phải ánh xạ lệnh chuẩn → chuỗi ghi theo driver, đọc lại trong dung sai và timeout, báo … | P0 · MVP/M1 · C1 | Phase 1 | F-INT-07 | M-INT | `CommandExecution`, `CommandTransition` | +API-CMD-02 | UI-28, +UI-21 | **T-FR-INT-007** · Mô phỏng · APPLIED / `APPLIED_CLAMPED` / `FAILED_NO_EFFECT` / `FAILED_TIMEOUT` đúng trong timeout (T-FR-INT-007). |
| FR-INT-008 | Uplink phải là MQTT 5 + mTLS, outbound-only, lô nhị phân nén (mục tiêu ≤ 15 B/mẫu), `seq` + … | P0 · MVP/M1 · — | Phase 1 | F-INT-08 | M-INT | `EdgeNode`, `Series` | — (MQTT `ems/v1/{edge_id}/up\|down/…`) | UI-26 | **T-FR-INT-008** · Tích hợp · Gửi trùng/đảo thứ tự/lỗ `seq` → ingest idempotent, RESEND cho lỗ (T-FR-INT-008); 0 cổng inbound. |
| FR-INT-009 | Edge phải store-and-forward: không mất dữ liệu khi mất mạng ≤ 7 ngày; mục tiêu buffer 30 ngày … | P0 · MVP/M1 · — | Phase 1 | F-INT-09 | M-INT | `EdgeNode`, `Watermark` | — (edge) | UI-26 | **T-FR-INT-009** · HIL · Rút WAN 7 ngày → 0 mẫu C4/C5 mất, C1–C3 đủ (AC-INT-02, T-FR-INT-009); xả có giới hạn tốc độ. |
| FR-INT-010 | Edge phải đồng bộ thời gian (chrony ≥ 2 nguồn + RTC), báo `clock_state` và offset trong … | P0 · MVP/M1 · — | Phase 1 | F-INT-10 | M-INT | `EdgeNode`, `Series` | +API-TEL-10 | UI-26 | **T-FR-INT-010** · Mô phỏng · Lệch đồng hồ > 1 s → `UNSYNCED`, mẫu `UNCERTAIN_CLOCK`, IL-06 chặn lệnh (T-FR-INT-010). |
| FR-INT-011 | Hệ thống phải quản lý cấu hình edge theo mô hình desired/reported có version; config ký số … | P0 · MVP/M1 · — | Phase 1 | F-INT-11 | M-INT | `EdgeConfigVersion` | API-INT-03, API-INT-04 | UI-26 | **T-FR-INT-011** · Mô phỏng · Config không ký/ký sai `kid` → `REJECTED_SIGNATURE`, giữ config cũ (AC-INT-07, T-FR-INT-011). |
| FR-INT-012 | Hệ thống phải OTA firmware edge: A/B ký số, rollback tự động, anti-rollback, canary 1% → 10% → … | P0 · MVP/M1 · C3 | Phase 1 | F-INT-12 | M-INT | `EdgeNode`, `AuditEvent`, ⚠ `OtaCampaign` (05 thiếu) | API-INT-05 | UI-26 | **T-FR-INT-012** · HIL · Canary 1% có rollback → dừng trước 10% (AC-INT-08); ảnh ký sai/phiên bản thấp bị từ chối (T-NFR-SEC-020-01). |
| FR-INT-013 | Hệ thống phải có trang "Thiết bị được hỗ trợ": model + firmware + trạng thái kiểm chứng + chức … | P0 · MVP/M1 · — | Phase 1 | F-INT-23 | M-INT | `DeviceModel`, `DriverVersion` | API-INT-06 | UI-28 | **T-FR-INT-013** · E2E · Trang liệt kê model + firmware + driver@version + trạng thái kiểm chứng; không có câu "hỗ trợ mọi inverter". |
| FR-INT-014 | Phải có bộ mô phỏng thiết bị nội bộ (Modbus inverter/PCS/BMS/công tơ có dấu cấu hình được, … | P0 · MVP/M1 · — | Phase 1 | F-INT-24 | M-INT | `DriverVersion` | — (công cụ nội bộ) | — (công cụ nội bộ) | **T-FR-INT-014** · Tích hợp · Bộ mô phỏng nạp cùng register map YAML của driver; mọi kết quả nhãn "Mô phỏng", không nâng trạng thái driver. |
| FR-INT-015 | Hệ thống phải có checklist commissioning theo topology (WF-02): claim → kết nối/đồng hồ → khám … | P0 · MVP/M1 · — | Phase 1 | F-INT-25 | M-INT | `CommissioningRecord` | API-INT-08 | UI-27 | **T-FR-INT-015** · E2E · Chạy WF-02 đầy đủ trên site HIL: claim → kết nối → map → dấu → giới hạn xuất → watchdog → SOE → biên bản. |
| FR-INT-016 | Hệ thống phải có phép thử dấu cho mỗi điểm đo: tạo tình huống biết trước (BESS sạc nhỏ ≥ 5% P … | P0 · MVP/M1 · C1 | Phase 1 | F-INT-26 | M-INT | `CommissioningRecord`, `MeteringPoint` | API-INT-08 | UI-27 | **T-FR-INT-016** · Mô phỏng · BESS sạc 20 kW, `MTR_BESS` đọc +20 kW → "Không đạt — dấu ngược" (AC-INT-05, T-FR-INT-016). |
| FR-INT-017 | Hệ thống phải có test giới hạn xuất: kịch bản giảm tải/tăng PV; đo thời gian đưa xuất về ≤ … | P0 · MVP/M1 · C2 | Phase 1 | F-INT-27 | M-INT | `CommissioningRecord`, `Event` | API-INT-08 | UI-27 | **T-FR-INT-017** · HIL · Bước tải/PV làm xuất vượt → về ≤ giới hạn + tol ≤ 5 s (T-FR-INT-017); kết quả lưu vào biên bản. |
| FR-INT-018 | Hệ thống phải có test watchdog và fail-safe: rút cáp edge↔thiết bị, mất `MTR_POC`, edge mất … | P0 · MVP/M2 · C2 | Phase 2 | F-INT-28 | M-INT | `CommissioningRecord`, `CapabilityProfile` | API-INT-08 | UI-27 | **T-FR-INT-018** · HIL · Rút RS485 tới PCS xả 100 kW, `revert_timeout_s`=30 s → về 0/native trong hạn (AC-INT-06, T-FR-INT-018). |
| FR-INT-019 | Hệ thống phải sinh biên bản commissioning PDF: cấu hình, kết quả từng test, phiên bản … | P0 · MVP/M1 · — | Phase 1 | F-INT-29 | M-INT | `CommissioningRecord` | API-INT-09 | UI-27 | **T-FR-INT-019** · Tích hợp · PDF có hash cấu hình, phiên bản driver/firmware, kết quả từng test, chữ ký người thực hiện. |
| FR-INT-020 | Hệ thống phải có bước xác minh map điểm: với mỗi thiết bị, so ≥ 1 giá trị công suất, 1 điện … | P0 · MVP/M1 · — | Phase 1 | F-INT-25, F-INT-03, F-MON-06 | M-INT, M-MON | `CommissioningRecord`, `Series`, `PointDefinition` | API-TEL-08, API-INT-08 | UI-27, UI-28 | **T-FR-INT-020** · Mô phỏng · Màn hình 102,0 kW, driver 10,2 kW → "Lệch — có thể sai scale" (AC-INT-04). |
| FR-INT-021 | Hệ thống nên có connector cloud chỉ đọc cho Sungrow iSolarCloud, SMA, Solis, Growatt, Deye: … | P1 · hạng 03: Phase 1 · — | Phase 2 (có điều kiện, V13) hoặc Phase 3 (3J) | F-INT-13 | M-INT | `Integration`, `ExternalRef` | API-INT-07 | ⚠ 09 ghi F-INT-13 ở UI-26 nhưng không ghi FR; +UI-26 | **T-FR-INT-021** · Tích hợp · Connector Sungrow/SMA/Solis/Growatt mock; credential chỉ đọc; quota API hãng (UNKNOWN) được tôn trọng. |
| FR-INT-022 | Edge nên nghe CAN BMS ở chế độ listen-only khi không có northbound; không chen vào bus bảo vệ. | P1 · hạng 03: Phase 1 · — | Phase 3 (3J) | F-INT-15 | M-INT | `DeviceEndpoint` | — (edge) | ⚠ 09 chưa ghi; +UI-28 | **T-FR-INT-022** · Mô phỏng · CAN listen-only: không phát khung nào ra bus trong 24 h. |
| FR-INT-023 | Edge nên có slave IEC 60870-5-104 với bảng điểm cấu hình được, chạy độc lập cloud, trên … | P1 · hạng 03: Phase 1/M2 · C2 | Phase 2 (có điều kiện, V12) | F-INT-16 | M-INT | `EdgeConfigVersion`, `DispatchCommand` | — (IEC 104 tại edge; cấu hình qua API-INT-04) | ⚠ 09 chưa ghi; +UI-26 | **T-FR-INT-023** · Mô phỏng · Master 104 mô phỏng gửi setpoint khi cloud mất → arbiter mức 4, ACT_CON sau readback (T-FR-INT-023); type lạ bị từ chối. |
| FR-INT-024 | Edge nên làm Modbus TCP server xuất lại dữ liệu cho SCADA/BMS tòa nhà của khách (Sparkplug B … | P1 · hạng 03: Phase 1 · — | Phase 3 (3J) | F-INT-17 | M-INT | `EdgeConfigVersion` | — (edge) | ⚠ 09 chưa ghi; +UI-26 | **T-FR-INT-024** · Mô phỏng · Client SCADA đọc bảng xuất; ghi bị từ chối; fuzz không làm treo (10 §19.2). |
| FR-INT-025 | Hệ thống nên có API REST đọc: OAuth2 client credentials, scope tối thiểu, mặc định chỉ đọc, … | P1 · hạng 03: Phase 1 · — | Phase 3 (3J) | F-INT-19 | M-INT | `ApiClient` | API-PUB-02 | — (bên thứ ba; cấu hình client ở UI-32) | **T-FR-INT-025** · Tích hợp · Client credentials scope chỉ đọc; vượt hạn mức → 429 `Retry-After`; tenant khác 404. |
| FR-INT-026 | Hệ thống nên có webhook: cảnh báo mở/đóng, trạng thái lệnh, báo cáo sẵn sàng, ticket; ký HMAC, … | P1 · hạng 03: Phase 1 · — | Phase 3 (3J) | F-INT-20 | M-INT | ⚠ `WebhookSubscription` (05 thiếu), `AuditEvent` | API-PUB-03 | ⚠ chưa có trang cấu hình webhook; đề xuất trong UI-32 | **T-FR-INT-026** · Tích hợp · Webhook ký HMAC; retry lũy thừa; idempotency key; đích lỗi 24 h → tạm dừng và báo. |
| FR-INT-027 | Hệ thống nên cho nhập CSV lịch sử và file load profile công tơ EVN khi có, gắn origin và … | P1 · hạng 03: Phase 1 · — | Phase 2 | F-INT-22 | M-INT | ⚠ `ImportJob` (05 thiếu), `Series`, `IntervalEnergy` | API-INT-10 | ⚠ 09 chưa ghi; đề xuất trong UI-28 | **T-FR-INT-027** · Tích hợp · CSV lịch sử gắn origin `IMPORTED`, không ghi đè dữ liệu đo; load profile EVN dùng method `INTERVAL_NATIVE`. |
| FR-INT-028 | Hệ thống có thể ghi qua cloud hãng (Huawei OAuth Connect control API) chỉ khi đủ 6 điều kiện CF-39 (edge là client, có hạn, readback, mặc định mất liên lạc, không vòng nhanh, audit); … | P2 · hạng 03: Phase 2/M1 · C2 | Phase 4 (4D) | F-INT-14 | M-INT | `Integration`, `DispatchCommand` | API-CMD-01 (type khi track 4D bật), API-INT-07 (cờ) | ⚠ chưa có trang (P2) | **T-FR-INT-028** · Tích hợp · Ghi qua Huawei OAuth Connect (mock) chỉ khi cờ bật, C2+, qua edge; không hỗ trợ hạn → từ chối; readback không khớp → `FAILED_NO_EFFECT`; site không edge → cờ không bật được (07 §8.8). |
| FR-INT-029 | Hệ thống có thể có adapter IEC 61850 MMS client, DNP3 outstation, OpenADR 3.x VEN, IEEE 2030.5 … | P2 · hạng 03: Phase 2 · — | Phase 4 (4C; một phần 4A) | F-INT-18 | M-INT | `DeviceEndpoint`, `DriverVersion` | — (edge) | ⚠ chưa có trang (P2) | **T-FR-INT-029** · Mô phỏng · Adapter IEC 61850/DNP3/OpenADR/2030.5 với bộ thử mô phỏng; không tuyên bố tuân thủ. |
| FR-INT-030 | Hệ thống có thể cho API lệnh cho bên thứ ba: scope ghi cho client máy (C1 trong SOE), qua PDP … | P2 · hạng 03: Phase 2/M2 · C1 | Phase 4 (4D) | F-INT-21 | M-INT | `ApiClient`, `DispatchCommand` | API-PUB-04 | — (bên thứ ba) | **T-FR-INT-030** · Tích hợp · Scope `cmd.c1` mặc định 0 lệnh; lệnh qua PDP + Governor; ngoài SOE bị từ chối. |
| FR-INT-031 | Lệnh `COMMISSIONING_TEST` là đường ghi duy nhất cho phép thử dấu, test giới hạn xuất, test watchdog; chỉ … | P0 · MVP/M1 · C2 | Phase 1 ⚠ (FR mới của 04; 11 chưa ghi) | F-INT-26, F-INT-27, F-INT-28 (chờ 03 cấp F- riêng) | M-INT, M-SEC | `CommissioningRecord`, `DispatchCommand`, `AuditEvent` | API-INT-08 | ⚠ 09 chưa ghi FR; +UI-27 | **T-FR-INT-031** · Mô phỏng · Lệnh khi site `active` → `REJECTED_INTERLOCK:IL-10`; không nhấn nút vật lý trong 120 s → phiên không mở; công tắc ở LOCAL → không mở; \|P\| > min(10% P định mức, 50 kW) hoặc bước > 10 phút → từ chối; rút cáp/khởi động lại edge giữa bước → `REVERT_DEFAULT` + readback (ca HIL ở lab L5); mỗi bước có audit (NFR-SEC-033). |

### 3.14 M-SEC — Bảo mật, an toàn lệnh

| FR (04) | Yêu cầu (tóm tắt) | Ưu tiên · Hạng phát hành (04/03) · Hạng lệnh | Lộ trình (11) | F- (03) | Module | Thực thể (05) | API (06) | UI (09) | Test |
|---|---|---|---|---|---|---|---|---|---|
| FR-SEC-001 | Hệ thống phải xác thực bằng OIDC Authorization Code + PKCE; access token ngắn hạn, refresh … | P0 · MVP/M1 · — | Phase 1 | F-SEC-01 | M-SEC | `User` | API-AUTH-01, API-AUTH-05 | UI-34 | **T-FR-SEC-001** · Tích hợp · Authorization Code + PKCE; token hết hạn ngắn; thu hồi phiên qua API-AUTH-05 có hiệu lực ở request kế. |
| FR-SEC-002 | MFA bắt buộc cho mọi vai trò có quyền ghi và admin (ưu tiên WebAuthn, TOTP phụ, không chỉ … | P0 · MVP/M1 · — | Phase 1 | F-SEC-02 | M-SEC | `User`, `AuditEvent` | API-AUTH-03 | UI-31, UI-34 | **T-FR-SEC-002** · E2E · Người có quyền ghi chưa có MFA → bắt đăng ký (AC-SEC-12); C2 cần step-up ≤ 5 phút (AC-BESS-02). |
| FR-SEC-003 | Mọi request phải qua RBAC theo cây; mọi lệnh phải qua PDP đánh giá chủ thể (vai trò, … | P0 · MVP/M1 · — | Phase 1 | F-SEC-03 | M-SEC | `RoleAssignment`, `AccessGrant`, `DispatchCommand` | API-AUTH-02, +mọi API-CMD | UI-21, UI-31 | **T-FR-SEC-003** · Đơn vị · Bộ test chính sách PDP-01…15; `ORG_ADMIN` không có quyền lệnh (AC-ORG-03). |
| FR-SEC-004 | Tenant phải cô lập bằng PostgreSQL RLS với FORCE, role ứng dụng không owner/không BYPASSRLS, … | P0 · MVP/M1 · — | Phase 1 | F-SEC-04 | M-SEC | `Organization` | +mọi API | — (hạ tầng) | **T-FR-SEC-004** · Tích hợp · Bộ cross-tenant CI: token A đọc ID của B → 403/404, 0 hàng; role DB không đặt tenant → 0 hàng (AC-SEC-09). |
| FR-SEC-005 | Monitoring plane và control plane phải tách danh tính dịch vụ, credential, topic, quyền DB, … | P0 · MVP/M1 · C3 | Phase 1 | F-SEC-05 | M-SEC | `Site`, `ConsentRecord`, `SiteControlConfig` | API-CMD-10, API-CMD-11 | UI-24 | **T-FR-SEC-005** · Tích hợp · Site mới `control_enabled=false`, lệnh C1+ bị `CONTROL_DISABLED` (AC-SEC-01); test ArchUnit cấm MON import gói lệnh; ACL broker tách topic. |
| FR-SEC-006 | Hệ thống phải phân hạng mọi loại lệnh C0–C4 (bảng §2 ngưỡng nâng hạng); C4 không có API; PDP … | P0 · MVP/M1 · C3 (nâng hạng ngữ cảnh: M2) | Phase 1 | F-SEC-06 | M-SEC | `DispatchCommand`, `CommandApproval` | API-CMD-05 | UI-21, UI-22 | **T-FR-SEC-006** · Đơn vị · Quy tắc nâng hạng: > 80% SOE → C2; > 5 site/lệnh → C2; > 10% MW đội → C3; C4 không có route. |
| FR-SEC-007 | Hệ thống phải có hàng đợi phê duyệt C3: người duyệt khác người yêu cầu và khác vai trò, cả hai … | P0 · MVP/M1 · C3 | Phase 1 | F-SEC-06 | M-SEC | `CommandApproval` | API-CMD-05 | UI-21, UI-22 | **T-FR-SEC-007** · Tích hợp · Tự duyệt bị chặn; duyệt sau 15 phút → `APPROVAL_EXPIRED`, không ký envelope (AC-SEC-02, AC-SEC-03, T-NFR-SEC-008-01). |
| FR-SEC-008 | Mọi lệnh phải đóng gói trong envelope: `command_id` (UUID v7, idempotency), `correlation_id`, … | P0 · MVP/M1 · — | Phase 1 | F-SEC-07 | M-SEC | `DispatchCommand` | API-CMD-04, +API-CMD-01 | UI-21 | **T-FR-SEC-008** · Mô phỏng · Replay sau 2 phút → `REJECTED_REPLAY` + cảnh báo bảo mật (AC-SEC-04); sửa 1 byte → `REJECTED_INVALID`; `alg=none` → từ chối (T-NFR-SEC-004-01…03); vector vàng JWS. |
| FR-SEC-009 | Hệ thống phải theo dõi trạng thái lệnh theo máy trạng thái ở trên; không gửi lại sau … | P0 · MVP/M1 · — | Phase 1 | F-SEC-07, F-SEC-14 | M-SEC | `DispatchCommand`, `CommandTransition` | API-LIVE-04, API-CMD-02, API-CMD-03, API-CMD-04, API-AUD-02 | UI-21, UI-23 | **T-FR-SEC-009** · Mô phỏng · Edge offline tới quá `expires_at` → `UNDELIVERED`, không gửi lại (T-NFR-SEC-011-01); UI "đang chờ xác nhận" (AC-SEC-13). |
| FR-SEC-010 | Edge phải thực thi IL-01…IL-10 trả `REJECTED_INTERLOCK:<code>`; site Gate M2 có BESS phải có … | P0 · MVP/M2 · C1 | Phase 2 | F-SEC-08 | M-SEC | `SiteControlConfig`, `Event` | — (edge; trạng thái qua API-CMD-07) | UI-24 | **T-FR-SEC-010** · HIL · Kích IL-01…IL-10 → `REJECTED_INTERLOCK:<IL>` (T-NFR-SEC-010-01…11); LOCAL hủy lệnh tay (AC-SEC-06, T-NFR-SEC-014-01). |
| FR-SEC-011 | Hệ thống phải có trang trạng thái điều khiển site: LOCAL/REMOTE, kill switch, Gate, SOE … | P0 · MVP/M1 · — | Phase 1 | F-SEC-09 | M-SEC | `Site`, `SiteControlConfig`, `RemoteControlSuspension`, `SafeOperatingEnvelope` | API-CMD-07 | UI-24 | **T-FR-SEC-011** · E2E · Trang hiện Gate, LOCAL/REMOTE, kill switch, SOE hiệu lực, chủ vòng; mỗi trạng thái đổi có thời điểm. |
| FR-SEC-012 | Hệ thống phải có Fleet Dispatch Governor: Σ\|ΔP\| được lệnh trong 5 phút ≤ ngưỡng tenant (mặc … | P0 · MVP/M2 · C1 | Phase 2 | F-SEC-10 | M-SEC | `FleetDispatchPolicy`, `DispatchCommand` | API-CMD-12 | UI-22, UI-24 | **T-FR-SEC-012** · Mô phỏng · Tenant 10 MW, Σ\|ΔP\| 2,1 MW/5 phút → lệnh vượt 2,0 MW vào hàng đợi C3 (AC-SEC-07, T-NFR-SEC-012-01). |
| FR-SEC-013 | Hệ thống phải có kill switch điều khiển từ xa theo site/tenant/nền tảng: edge nhận lệnh ký … | P0 · MVP/M1 · C1 kích hoạt / C3 gỡ | Phase 1 ⚠ (04 nay M1; 11 §7.2 còn ghi Phase 2) | F-SEC-11 | M-SEC | `RemoteControlSuspension` | API-CMD-06 | UI-22, UI-24 | **T-FR-SEC-013** · Mô phỏng · Kill switch tenant với 50 edge mô phỏng → `REMOTE_CONTROL_SUSPENDED` ≤ 60 s, lệnh mới bị từ chối (AC-SEC-08, T-NFR-SEC-013-01); Gate M1: engage khi scheduler đang đẩy lịch native và có `CONFIG_PUSH` chờ → không lịch native, `SET_ESS_MODE`, `CONFIG_PUSH` nào được ký/gửi (T-NFR-SEC-013-04); gỡ cần C3 hai người. |
| FR-SEC-014 | Hệ thống phải có audit append-only: đăng nhập/MFA, đổi quyền, grant, SOE/config/driver map, … | P0 · MVP/M1 · — | Phase 1 | F-SEC-12 | M-SEC | `AuditEvent` | API-AUD-01, API-AUD-04 | UI-33 | **T-FR-SEC-014** · Tích hợp · Role app `UPDATE`/`DELETE` audit bị từ chối (AC-SEC-10); sửa hàng bằng superuser → kiểm chuỗi phát hiện (T-NFR-SEC-015-01). |
| FR-SEC-015 | Hệ thống phải có nhật ký lệnh cho người dùng: vòng đời từng lệnh (tạo → gửi → edge chấp … | P0 · MVP/M1 · — | Phase 1 | F-SEC-14 | M-SEC | `DispatchCommand`, `CommandTransition`, `CommandExecution` | API-LIVE-04, API-CMD-02, API-CMD-03, API-AUD-02 | UI-23 | **T-FR-SEC-015** · E2E · Nhật ký hiển thị vòng đời lệnh tạo → gửi → edge → readback, lý do kẹp, người duyệt. |
| FR-SEC-016 | PDP phải chặn setpoint P cưỡng bức tới thiết bị `requires_native_fallback = true`; chỉ cho đổi … | P0 · MVP/M1 · — | Phase 1 | F-SEC-15 | M-SEC | `CapabilityProfile`, `DispatchCommand` | +API-CMD-01, +API-CMD-04 | UI-21, UI-24 | **T-FR-SEC-016** · Mô phỏng · Thiết bị không watchdog nhận `SET_ESS_P` → PDP `DEVICE_NOT_ELIGIBLE`; edge `REJECTED_UNSUPPORTED` nếu bị gửi (T-NFR-REL-002-02). |
| FR-SEC-017 | Bí mật và khóa phải nằm trong Vault/KMS; khóa ký lệnh không xuất được, hỗ trợ 2 `kid` song … | P0 · MVP/M1 · — | Phase 1 | F-SEC-16 | M-SEC | `ApiClient`, `Integration` | — (hạ tầng) | — (hạ tầng) | **T-FR-SEC-017** · Tích hợp · Khóa ký không xuất được; xoay khóa với 2 `kid` song song; quét secret CI chặn merge. |
| FR-SEC-018 | Edge phải phân vùng OT/IT: 2 NIC, không định tuyến WAN↔OT, chỉ outbound 8883/443 (+ NTP, DNS, … | P0 · MVP/M1 · — | Phase 1 | F-SEC-17 | M-SEC | `EdgeNode` | — (hạ tầng edge) | — (checklist ở UI-27) | **T-FR-SEC-018** · HIL · Quét cổng từ WAN = 0 inbound; không route WAN↔OT; Modbus chỉ trên NIC OT. |
| FR-SEC-019 | Hệ thống phải phân loại dữ liệu D0–D4 và áp quy tắc mã hóa/xuất theo lớp; hosting tại Việt Nam … | P0 · MVP/M1 · — | Phase 1 | F-SEC-18 | M-SEC | `Organization`, `AuditEvent` | — (chính sách) | UI-32 | **T-FR-SEC-019** · Tích hợp · Trường D3 mã hóa; xuất D3 cần quyền riêng và audit; hosting VN là mặc định (chờ pháp lý). |
| FR-SEC-020 | Hệ thống phải áp chính sách lưu giữ ở §2 (raw 13 tháng; 5 phút 5 năm; ≥ 1 h vòng đời; audit 13 … | P0 · MVP/M1 · — | Phase 1 | F-SEC-19 | M-SEC | `AuditEvent`, `ReportSnapshot`, `Series` | — (job nội bộ) | UI-32 | **T-FR-SEC-020** · Tích hợp · Retention job: raw 13 tháng, 5 phút 5 năm, audit trực tuyến ≥ 13 tháng, snapshot ≥ 5 năm (bản sao "du hành thời gian"). |
| FR-SEC-021 | Hệ thống phải tính **hồ sơ sẵn sàng Gate M2** theo site và chỉ cho bật M2 khi tất cả đạt: (1) … | P0 · MVP/M2 · C3 | Phase 2 | F-SEC-05, F-SEC-06, F-SEC-07, F-SEC-08, F-SEC-10, F-SEC-11, F-INT-28, F-BESS-08 | M-SEC, M-INT, M-BESS | `M2ReadinessCheck`, `SafeOperatingEnvelope`, `CommissioningRecord` | API-CMD-04, API-CMD-05, API-CMD-06, API-CMD-08, API-CMD-10, API-CMD-11, API-CMD-12, API-INT-08 | UI-24 | **T-FR-SEC-021** · Tích hợp · Thiếu test watchdog PCS P1 → hồ sơ "Chưa đạt…" và yêu cầu bật M2 bị chặn (AC-SEC-11). |
| FR-SEC-022 | PDP phải áp giới hạn tốc độ: site ≤ 6 lệnh thủ công/phút và ≤ 12 đổi chế độ/giờ; người dùng ≤ … | P0 · MVP/M1 · — | Phase 1 | F-SEC-03, F-SEC-10 | M-SEC | `DispatchCommand` | API-AUTH-02, API-CMD-12, +API-CMD-01 | UI-21 | **T-FR-SEC-022** · Đơn vị · Lệnh tay thứ 7 trong 1 phút → `RATE_LIMITED`; đổi chế độ thứ 13 trong 1 giờ → từ chối. |
| FR-SEC-023 | Hệ thống nên neo audit: Merkle root mỗi giờ ký KMS ghi vào object storage WORM ≥ 5 năm; xuất … | P1 · hạng 03: Phase 1 · — | Phase 2 | F-SEC-13 | M-SEC | `AuditEvent` | API-AUD-03 | UI-33 | **T-FR-SEC-023** · Tích hợp · Merkle root mỗi giờ ký KMS ghi WORM; xuất audit kèm bằng chứng; sửa một hàng → bằng chứng không khớp. |
| FR-SEC-024 | Hệ thống nên có hỗ trợ từ xa có kiểm soát: reverse tunnel theo yêu cầu, chủ site cho phép, ≤ 2 … | P1 · hạng 03: Phase 1 · — | Phase 2 | F-SEC-20 | M-SEC | ⚠ `RemoteSupportSession` (05 thiếu), `AuditEvent` | API-INT-11 (vòng nhất quán) | ⚠ chưa có trang | **T-FR-SEC-024** · Tích hợp · Tunnel theo yêu cầu ≤ 2 h, chủ site duyệt, phiên ghi lại, không route sang OT. |
| FR-SEC-025 | Hệ thống nên có OpenTelemetry xuyên cloud → edge với `trace_id`, `command_id` và SLO tách theo … | P1 · hạng 03: Phase 1 · — | Phase 2 | F-SEC-21 | M-SEC | — | — (hạ tầng) | — (hạ tầng) | **T-FR-SEC-025** · Tích hợp · Trace một lệnh có span API → PDP → Signer → broker → edge với cùng `trace_id`, `command_id`. |
| FR-SEC-026 | Hệ thống nên quản lý client API: OAuth2 client credentials, scope, IP allow-list tùy chọn, hạn … | P1 · hạng 03: Phase 1 · — | Phase 3 (3J) | F-SEC-22 | M-SEC | `ApiClient` | API-PUB-01 | UI-32 | **T-FR-SEC-026** · Tích hợp · Client hạn ≤ 1 năm, mặc định chỉ đọc; IP allow-list; tạo client cần step-up. |
| FR-SEC-027 | Sản phẩm có thể theo lộ trình chứng nhận ISO 27001 (vận hành cloud) → IEC 62443-4-2 (edge) → … | P2 · hạng 03: Phase 2 · — | Phase 4 (4F) | F-SEC-23 | M-SEC | — | — (quy trình) | — (quy trình) | **T-FR-SEC-027** · Đơn vị · Rà soát tài liệu tiếp thị: không có câu "tuân thủ/chứng nhận" khi chưa có chứng chỉ (kiểm bằng quét chuỗi). |
| FR-SEC-028 | Sản phẩm có thể có SKU silo/on-prem (DB/cluster riêng) cho khách lớn. | P2 · hạng 03: Phase 2 · — | Phase 4 (4E) | F-SEC-24 | M-SEC | `Organization` | — (triển khai) | — (triển khai) | **T-FR-SEC-028** · Tích hợp · Triển khai silo; bộ cross-tenant và hồi quy vẫn đạt. |

### 3.15 M-ADV — Nâng cao

| FR (04) | Yêu cầu (tóm tắt) | Ưu tiên · Hạng phát hành (04/03) · Hạng lệnh | Lộ trình (11) | F- (03) | Module | Thực thể (05) | API (06) | UI (09) | Test |
|---|---|---|---|---|---|---|---|---|---|
| FR-ADV-001 | Hệ thống phải có dự báo tải F0 (seasonal naive: cùng giờ tuần trước) và F1 (median theo thứ × … | P0 · MVP/M1 · — | Phase 1 | F-ADV-01 | M-ADV | `ForecastModel`, `ForecastRun`, `ForecastValue`, `SpecialDay` | ⚠ thiếu API dự báo (UI-19 cần; đề xuất trường trong API-OPT-03 hoặc nhóm API-FC) | UI-19 | **T-FR-ADV-001** · Đơn vị · F1 = median 4 thứ Hai trước bỏ ngày lễ (AC-ADV-01); < 7 ngày dữ liệu → profile mặc định có nhãn "dự báo dự phòng" (AC-ADV-02). |
| FR-ADV-002 | Mọi giá trị dự báo, ước tính, mô phỏng trên UI, báo cáo, API phải mang nhãn phương pháp ("Quy … | P0 · MVP/M1 · — | Phase 1 | F-ADV-01…F-ADV-11 (11 F) | M-ADV | `ForecastModel`, `KpiValue` | +mọi API dữ liệu (`is_estimate`) | UI-19, +mọi trang | **T-FR-ADV-002** · Đơn vị · Mọi giá trị mô phỏng có nhãn "Mô phỏng"; quét i18n không có "AI" gắn với quy tắc ngưỡng (AC-ADV-03). |
| FR-ADV-003 | Hệ thống nên có adapter dự báo PV đa nhà cung cấp (NWP/vệ tinh, GTI) → mô hình vật lý DC/AC có … | P1 · hạng 03: Phase 1 · — | Phase 3 (3B) | F-ADV-02 | M-ADV | `ForecastModel`, `ForecastRun`, `ForecastValue` | ⚠ thiếu API | ⚠ 09 chưa ghi; +UI-19 | **T-FR-ADV-003** · Tích hợp · Nhà cung cấp lỗi → dùng nhà cung cấp phụ hoặc F0; giấy phép thương mại của nhà cung cấp là UNKNOWN. |
| FR-ADV-004 | Hệ thống nên chạy đánh giá dự báo hằng đêm: MAE, nMAE (ghi mẫu số), nRMSE, MBE, WAPE, skill … | P1 · hạng 03: Phase 1 · — | Phase 3 (3B) | F-ADV-03 | M-ADV | `ForecastEvaluation` | ⚠ thiếu API | ⚠ chưa có trang | **T-FR-ADV-004** · Đơn vị · nMAE ghi mẫu số; không dùng MAPE cho PV; daylight_only đúng. |
| FR-ADV-005 | Hệ thống nên có dự báo tải F2 (gradient boosting với lịch, ngày lễ VN, Tết âm lịch, ca sản … | P1 · hạng 03: Phase 1 · — | Phase 3 (3B) | F-ADV-04 | M-ADV | `ForecastModel`, `ForecastEvaluation` | ⚠ thiếu API | ⚠ chưa có trang | **T-FR-ADV-005** · Đơn vị · Nhãn `ML_EVALUATED` chỉ khi F2 thắng F1 trên tập kiểm tra; thua → không dùng. |
| FR-ADV-006 | Hệ thống nên mô phỏng what-if định cỡ: kích thước BESS, biểu giá (TT 16 vs QĐ 963; có/không … | P1 · hạng 03: Phase 1 · — | Phase 3 (3B) | F-ADV-06 | M-ADV | ⚠ `SimulationRun` (05 thiếu), `TariffVersion` | API-OPT-10 (vòng nhất quán) | ⚠ chưa có trang | **T-FR-ADV-006** · Đơn vị · What-if BESS × biểu giá cho kết quả nhãn "Mô phỏng"; cùng tariff version cho mọi phương án. |
| FR-ADV-007 | Hệ thống có thể nhận lịch sản xuất của khách (nhập tay ngày nghỉ/ca hoặc MES/ERP) làm đầu vào … | P2 · hạng 03: Phase 2 · — | Phase 4 (4G) | F-ADV-05 | M-ADV | ⚠ `ProductionSchedule` (05 thiếu), `ForecastModel` | ⚠ thiếu API | ⚠ chưa có trang (P2) | **T-FR-ADV-007** · Tích hợp · Lịch nghỉ ca nhập tay làm F3 đổi profile ngày đó. |
| FR-ADV-008 | Hệ thống có thể chạy phát hiện bất thường ML L3 (thử nghiệm) chỉ khi có nhãn từ ticket, đo … | P2 · hạng 03: Phase 2 · — | Phase 4 (4G) | F-ADV-07 | M-ADV | `ForecastModel`, `Alarm` | ⚠ thiếu API | ⚠ chưa có trang (P2) | **T-FR-ADV-008** · Đơn vị · Chỉ chạy khi đủ nhãn FR-ALM-019; nhãn "thử nghiệm"; không gửi thông báo tự động. |
| FR-ADV-009 | Hệ thống có thể ước lượng xu hướng suy giảm pin theo thời gian và cách dùng. | P2 · hạng 03: Phase 2 · — | Phase 4 (4G) | F-ADV-08 | M-ADV | `KpiValue`, `Series` | ⚠ thiếu API | ⚠ chưa có trang (P2) | **T-FR-ADV-009** · Đơn vị · Xu hướng suy giảm có khoảng tin cậy và nhãn "ước tính". |
| FR-ADV-010 | Hệ thống có thể giám sát microgrid/backup (đảo/nối lưới, ATS, genset, thời lượng backup), chỉ … | P2 · hạng 03: Phase 2 · — | Phase 4 (4G) | F-ADV-09 | M-ADV | `Series`, `Event` | ⚠ thiếu API | ⚠ chưa có trang (P2) | **T-FR-ADV-010** · HIL · Giám sát đảo/nối lưới, ATS (chỉ đọc); không có lệnh chuyển đảo. |
| FR-ADV-011 | Hệ thống có thể phân tích chất lượng điện từ công tơ PQ có sẵn, chỉ đọc. | P2 · hạng 03: Phase 2 · — | Phase 4 (4G) | F-ADV-10 | M-ADV | `Series` | ⚠ thiếu API | ⚠ chưa có trang (P2) | **T-FR-ADV-011** · Tích hợp · Đọc thông số PQ từ công tơ có sẵn, chỉ đọc; không tuyên bố tuân thủ IEC 61000-4-30. |
| FR-ADV-012 | Hệ thống có thể đối soát DPPA (đo đếm chu kỳ 30/60 phút, giá thị trường). | P2 · hạng 03: Phase 2 · — | Phase 4 (4B) | F-ADV-11 | M-ADV | `IntervalEnergy`, ⚠ `PriceSeries` (05 thiếu) | ⚠ thiếu API | ⚠ chưa có trang (P2) | **T-FR-ADV-012** · Đơn vị · Đối soát DPPA 30/60 phút khớp tổng kWh công tơ. |

---

## 4. Ma trận NFR

### 4.1 NFR chính thức của 04

Phủ toàn bộ **85 NFR** của [04 §6](04-business-requirements.md#6-yêu-cầu-phi-chức-năng): 70 của bản dựng ban đầu và 15 mã 04 bản mới xác nhận (cuối bảng, thêm ở vòng nhất quán 2026-10-10; ưu tiên/Gate theo 04). Trong cột "Hạng phát hành · Gate", `Phase n` là hạng 03 (CF-29), không phải phase lộ trình; NFR theo phase lộ trình ở [11 §6.3, §7.2](11-mvp-and-roadmap.html#s6). Ca chi tiết của nhóm SEC/REL ở [10 §19.3](10-security-and-reliability.md).

| NFR (04) | Ưu tiên (04) | FR / tính năng liên quan | Module · thành phần (06) | API · UI | Test | Loại | Kịch bản / bằng chứng | Hạng phát hành · Gate |
|---|---|---|---|---|---|---|---|---|
| NFR-PERF-001 — Thời gian tải màn hình | P0 | FR-DASH-001, FR-DASH-002, FR-DASH-004, FR-ALM-005 | M-DASH, M-ALM · mon-app | API-TEL-09, API-LIVE-02, API-ALM-01 · UI-01, UI-03, UI-14 | **T-NFR-PERF-001** | Tải | 500 site dữ liệu giả lập: L1 p95 ≤ 3 s, L2 p95 ≤ 2 s, console 10.000 dòng p95 ≤ 2 s | MVP · PoC trước Gate MVP |
| NFR-PERF-002 — Trend explorer | P0 | FR-HIST-010 | M-HIST · mon-app, TSDB | API-TEL-02 · UI-13 | **T-NFR-PERF-002** | Tải | 8 chuỗi: raw 7 ngày và 5 phút 93 ngày p95 ≤ 3 s | MVP · PoC |
| NFR-PERF-003 — Độ tươi ingest | P0 | FR-MON-001, FR-INT-008 | M-MON · ingest pipeline | API-TEL-03, API-LIVE-01 · UI-03, UI-04 | **T-NFR-PERF-003** | Tải | Đo `ts_ingest − ts`: C2 p95 ≤ 60 s, C1 p95 ≤ 10 s khi xem live | MVP |
| NFR-PERF-004 — Thông lượng ingest | P0 | FR-HIST-002, FR-INT-009 | M-HIST, M-INT · broker, ingest | MQTT · — | **T-NFR-PERF-004** | Tải | Edge ảo 1.000 site 35.000 mẫu/s + backfill 5–10×, 0 mất mẫu (07 L7; edge ảo + virtual site 15 §4.1, T-E2-05) | MVP · PoC F-P25 |
| NFR-PERF-005 — Độ trễ giao lệnh | P0 | FR-SEC-008, FR-SEC-009, FR-BESS-005 | M-SEC · ctl-app, signer, broker, edge | API-CMD-01, API-CMD-02 · UI-21 | **T-NFR-PERF-005** | Mô phỏng | 1.000 lệnh qua chuỗi tới edge mô phỏng (virtual site, 15 §3): CREATED→RECEIVED p95 ≤ 5 s, p99 ≤ 15 s | MVP · M2 |
| NFR-PERF-006 — Chu kỳ điều khiển edge | P0 | FR-OPT-004, FR-GRID-005 | M-OPT · edge runtime | — · UI-26 (`cycle_time_ms`) | **T-NFR-PERF-006** | HIL | Phần cứng tham chiếu: chu kỳ 1 s, p99 ≤ 200 ms, đếm vượt chu kỳ | MVP · M2 |
| NFR-PERF-007 — Thông báo cảnh báo | P0 | FR-ALM-008 | M-ALM · alarm engine, notifier | API-ALM-05 · UI-17 | **T-NFR-PERF-007** | Tải | 1.000 sự kiện: p95 sự kiện → e-mail ≤ 2 phút (AC-ALM-02) | MVP |
| NFR-PERF-008 — Job ngày và báo cáo | P0 | FR-REP-001, FR-HIST-005 | M-REP, M-HIST · job ngày | API-REP-02 · UI-30 | **T-NFR-PERF-008** | Tải | Job ngày xong ≤ 02:00 giờ site; R1 sẵn sàng 99% trước 06:00 (AC-REP-01) | MVP |
| NFR-PERF-009 — Tính lại dữ liệu trễ | P0 | FR-HIST-006 | M-HIST · recompute worker | API-TEL-07 · UI-03 | **T-NFR-PERF-009** | Tích hợp | Backfill 1 ngày → mọi DirtyBucket `DONE` ≤ 1 h | MVP · PoC |
| NFR-PERF-010 — Bộ sinh lịch | P0 (tầng 2), P1 (tầng 3) | FR-OPT-005, FR-OPT-014 | M-OPT · planner | API-OPT-06 · UI-19 | **T-NFR-PERF-010** | Tải | Tầng 2: p95 ≤ 10 s/site; 1.000 site xong ≤ 15 phút sau 05:30 | MVP (tầng 2), Phase 1 (tầng 3) |
| NFR-PERF-011 — Xuất dữ liệu | P0 | FR-REP-006 | M-REP · export worker | API-REP-04 · UI-30 | **T-NFR-PERF-011** | Tải | 100.000 dòng trả ngay p95 ≤ 30 s; 100.001 dòng chuyển job nền | MVP |
| NFR-PERF-012 — API đọc công khai | P1 | FR-INT-025 | M-INT · public API gateway | API-PUB-02 · — | **T-NFR-PERF-012** | Tải | ≤ 10.000 điểm/truy vấn p95 ≤ 1 s; hạn mức 429 | Phase 1 |
| NFR-REL-001 — Fail-safe khi mất cloud | P0 | FR-OPT-006, FR-GRID-005, FR-GRID-006 | M-OPT, M-INT · edge | — · UI-03, UI-24, UI-36 | **T-NFR-REL-001** | HIL / game day | T-NFR-REL-001-01: chặn broker 4 h khi đang chạy lịch → lịch, rồi mặc định; không mất dữ liệu | MVP · M1 |
| NFR-REL-002 — Fail-safe khi mất edge↔thiết bị | P0 | FR-INT-018, FR-SEC-016 | M-INT, M-SEC · edge, thiết bị | — · UI-27 | **T-NFR-REL-002** | HIL | T-NFR-REL-002-01/02: rút cáp edge↔PCS → mặc định trong `revert_timeout_s`; thiết bị không watchdog bị từ chối setpoint | MVP · M2 |
| NFR-REL-003 — Watchdog edge | P0 | FR-INT-001 | M-INT · edge | — · UI-26 | **T-NFR-REL-003** | HIL | T-NFR-REL-003-01: treo tiến trình → reset ≤ 10 s, `SAFE_START`, không ghi trước 2 chu kỳ đọc | MVP · M1 |
| NFR-REL-004 — Khả dụng | P0 (mục tiêu), P1 (SLO chính thức, NFR-OBS-005) | FR-SEC-025 | Mọi module · SLI | — | **T-NFR-REL-004** | Đo SLI | Đo khả dụng theo mặt phẳng trên pilot 30 ngày | MVP (mục tiêu), Phase 1 (SLO) |
| NFR-REL-005 — Sao lưu và khôi phục | P0 | FR-SEC-014, FR-SEC-020 | M-SEC · DB, backup | — | **T-NFR-REL-005** | Diễn tập | Khôi phục PITR hằng quý; đo RPO/RTO cấu hình, lệnh+audit, timeseries | MVP |
| NFR-REL-006 — DR hai trung tâm dữ liệu tại VN | P1 | — | Hạ tầng | — | **T-NFR-REL-006** | Diễn tập | Failover DC khác tỉnh 6 tháng/lần | Phase 1 |
| NFR-REL-007 — Phản ứng khi dữ liệu an toàn cũ | P0 | FR-BESS-009, FR-GRID-005 | M-BESS, M-GRID · edge | — · UI-07, UI-10 | **T-NFR-REL-007** | HIL | T-NFR-REL-007-01/02: ngắt `MTR_POC` / làm cũ BMS → BESS 0/native, PV về giới hạn native ≤ 2 chu kỳ | MVP · M2 |
| NFR-REL-008 — Phát hiện edge offline | P0 | FR-MON-008, FR-ALM-004 | M-MON, M-ALM | API-TEL-10 · UI-26, UI-14 | **T-NFR-REL-008** | Mô phỏng | AC-MON-03 + AC-ALM-01 | MVP · M1 |
| NFR-REL-009 — Tuân thủ giới hạn xuất | P0 | FR-GRID-004, FR-GRID-005, FR-INT-017 | M-GRID · edge, native | API-INT-08 · UI-27 | **T-NFR-REL-009** | HIL | T-FR-INT-017: 0 sự kiện vi phạm trong test commissioning và hồi quy HIL; về giới hạn ≤ 5 s | MVP · M1 |
| NFR-REL-010 — Lan truyền kill switch | P0 | FR-SEC-013 | M-SEC · ctl-app, broker, edge | API-CMD-06 · UI-24 | **T-NFR-REL-010** | Mô phỏng | T-NFR-SEC-013-01: 50 edge ảo nhận `SUSPENDED` ≤ 60 s | MVP · M1 (04 bản mới) |
| NFR-REL-011 — Hạn chứng chỉ và khóa | P0 | FR-INT-002 | M-INT · PKI, edge | API-INT-02 · UI-26 | **T-NFR-REL-011** | Mô phỏng | T-NFR-REL-011-01: chứng chỉ hết hạn, điều khiển cục bộ tiếp tục; cảnh báo trước 14 ngày | MVP · M1 |
| NFR-REL-012 — Không thi hành lệnh cũ | P0 | FR-SEC-009 | M-SEC · ctl-app, edge | API-CMD-02 · UI-23 | **T-NFR-REL-012** | Mô phỏng | Khôi phục kết nối sau 4 h: không lệnh quá hạn được gửi/thực thi; đối soát ≤ 60 s (AC-INT-09) | MVP · M1 |
| NFR-DATA-001 — Không mất dữ liệu khi mất mạng | P0 | FR-INT-009 | M-INT · edge buffer | — · UI-26 | **T-NFR-DATA-001** | HIL | T-FR-INT-009: rút WAN 7 ngày, 0 mất; 1 s vòng tròn 7 ngày | MVP · M1 |
| NFR-DATA-002 — Ingest idempotent, đúng thứ tự logic | P0 | FR-HIST-002 | M-HIST · ingest | MQTT | **T-NFR-DATA-002** | Tích hợp | Gửi trùng/đảo thứ tự (AC-HIST-08, AC-MON-04) | MVP |
| NFR-DATA-003 — Quy ước dấu, đơn vị, thời gian, bucket | P0 | FR-HIST-003, FR-MON-002, FR-INT-016 | Mọi tầng | Mọi API | **T-NFR-DATA-003** | Đơn vị + Mô phỏng | Lint schema hậu tố đơn vị; phép thử dấu trên công tơ POC của virtual site (CT ngược, 15 §3.4) | MVP |
| NFR-DATA-004 — Điện năng từ thanh ghi | P0 | FR-HIST-004, FR-ORG-010 | M-HIST | — | **T-NFR-DATA-004** | Đơn vị | AC-HIST-01…03, AC-ORG-07 | MVP |
| NFR-DATA-005 — Chất lượng bắt buộc | P0 | FR-HIST-007, FR-DASH-008 | Mọi module | Mọi API · mọi trang | **T-NFR-DATA-005** | Đơn vị + E2E | Kiểm API trả `null` không phải 0; UI hiện "—" | MVP |
| NFR-DATA-006 — Tái lập được | P0 | FR-HIST-009, FR-TAR-006, FR-OPT-005 | M-HIST, M-TAR, M-OPT | — | **T-NFR-DATA-006** | Hồi quy | Golden snapshot ≥ 20 site-ngày so `output_hash` mỗi build (06 §16) | MVP |
| NFR-DATA-007 — Không đổi số âm thầm | P0 | FR-REP-005 | M-REP | API-REP-03 · UI-30 | **T-NFR-DATA-007** | Tích hợp | AC-REP-03/04 | MVP |
| NFR-DATA-008 — Lưu giữ | P0 | FR-HIST-011, FR-SEC-020 | M-HIST, M-SEC | — · UI-32 | **T-NFR-DATA-008** | Tích hợp | Job retention trên bản sao "du hành thời gian" | MVP |
| NFR-DATA-009 — Lưu giữ audit | P0 | FR-SEC-014, FR-SEC-023 | M-SEC | API-AUD-01 · UI-33 | **T-NFR-DATA-009** | Tích hợp | Audit > 13 tháng vẫn truy vấn được từ lưu trữ; WORM P1 | MVP (WORM Phase 1) |
| NFR-DATA-010 — Lưu trú dữ liệu | P0 | FR-SEC-019 | Hạ tầng | — | **T-NFR-DATA-010** | Rà soát | Kiểm vị trí lưu trữ mọi kho dữ liệu, backup, log; chờ kiểm chứng pháp lý | MVP |
| NFR-DATA-011 — Định dạng xuất | P0 | FR-REP-006 | M-REP | API-REP-04 · UI-30 | **T-NFR-DATA-011** | Tích hợp | AC-REP-05 | MVP |
| NFR-DATA-012 — Tính khả chuyển | P0 (CSV), P1 (Parquet) | FR-REP-006, FR-REP-014 | M-REP | API-REP-04, API-REP-07 | **T-NFR-DATA-012** | Tích hợp | Xuất toàn tenant CSV (MVP), Parquet (P1); đếm dòng khớp | MVP (CSV), Phase 1 (Parquet) |
| NFR-DATA-013 — Điều kiện chọn engine | P0 (cổng quyết định) | FR-HIST-001, FR-HIST-011 | M-HIST · ADR-06 | — | **T-NFR-DATA-013** | PoC | Kiểm giấy phép TSL + PoC 1.000 site trước chốt ADR-06 | Cổng quyết định trước MVP |
| NFR-OBS-001 — Bộ metric tối thiểu | P0 | FR-SEC-025 | Mọi module | — | **T-NFR-OBS-001** | Tích hợp | Mỗi metric trong danh sách có dashboard và cảnh báo nội bộ | MVP |
| NFR-OBS-002 — Telemetry sức khỏe edge | P0 | FR-MON-008, FR-INT-010 | M-MON, M-INT | API-TEL-10 · UI-26 | **T-NFR-OBS-002** | Mô phỏng | Edge ảo báo đủ trường sức khỏe; thiếu trường → cảnh báo | MVP |
| NFR-OBS-003 — Log có cấu trúc | P0 | FR-SEC-017 | Mọi dịch vụ | — | **T-NFR-OBS-003** | Đơn vị | Quét log mẫu: có `trace_id`/`tenant_id`, không token/secret/D3 | MVP |
| NFR-OBS-004 — Truy vết phân tán | P1 | FR-SEC-025 | M-SEC | — | **T-NFR-OBS-004** | Tích hợp | Trace 100% đường lệnh | Phase 1 |
| NFR-OBS-005 — SLO và error budget | P1 | FR-SEC-025 | Mọi module | — | **T-NFR-OBS-005** | Đo SLI | Hết error budget Command API → release control plane bị chặn | Phase 1 |
| NFR-OBS-006 — Giám sát an ninh | P0 (bốn tín hiệu đầu + hash chain), P1 (thiết bị lạ OT) | FR-SEC-014, FR-ALM-022 | M-SEC | API-AUD-01 · UI-33 | **T-NFR-OBS-006** | Mô phỏng | Sinh đăng nhập bất thường, lệnh ngoài giờ, nhiều `REJECTED_REPLAY`, đứt hash chain → tín hiệu an ninh | MVP (4 tín hiệu + hash), Phase 1 (OT) |
| NFR-OBS-007 — Chất lượng dữ liệu | P0 | FR-HIST-015, FR-REP-004 | M-HIST | API-TEL-07 · UI-30 | **T-NFR-OBS-007** | Tích hợp | Coverage, độ trễ p50/p95, tỷ lệ SUSPECT khớp R8 | MVP |
| NFR-SEC-001 — Cloud và edge không ghi thông số bảo vệ; không có API cho C4 | P0 | FR-BESS-011 | M-SEC | Không endpoint C4 | **T-NFR-SEC-001** | Đơn vị | AC-BESS-07 quét OpenAPI + tập lệnh edge | MVP · M1 |
| NFR-SEC-002 — Tách monitoring plane và control plane; control tắt mặc … | P0 | FR-SEC-005 | M-SEC · mon-app/ctl-app | API-CMD-10 · UI-24 | **T-NFR-SEC-002** | Tích hợp | ArchUnit; ACL broker; quyền DB tách (AC-SEC-01) | MVP · M1 |
| NFR-SEC-003 — Edge outbound-only, MQTT 5 qua TLS 1.3 (1.2 AEAD), mTLS, … | P0 | FR-INT-002, FR-INT-008 | M-INT · PKI, broker | API-INT-02 | **T-NFR-SEC-003** | HIL | Quét cổng site 0 inbound; gia hạn/thu hồi chứng chỉ | MVP · M1 |
| NFR-SEC-004 — Lệnh ký JWS bởi Command Signer (KMS/HSM); edge kiểm chữ ký, … | P0 | FR-SEC-008 | M-SEC · signer, edge | API-CMD-01 | **T-NFR-SEC-004** | Mô phỏng | T-NFR-SEC-004-01…03 | MVP · M1 |
| NFR-SEC-005 — OIDC + PKCE; MFA cho mọi vai trò có quyền ghi/admin; … | P0 | FR-SEC-001, FR-SEC-002 | M-SEC · IdP | API-AUTH-03 · UI-34 | **T-NFR-SEC-005** | E2E | AC-SEC-12; step-up hết 5 phút → yêu cầu lại | MVP · M1 |
| NFR-SEC-006 — RBAC theo cây + PDP cho mọi lệnh; SoD | P0 | FR-SEC-003 | M-SEC · PDP | API-AUTH-02, API-CMD-* | **T-NFR-SEC-006** | Đơn vị | PDP-01…15; T-NFR-SEC-008-01 | MVP · M1 |
| NFR-SEC-007 — Cô lập tenant bằng RLS FORCE + test cross-tenant trong CI | P0 | FR-SEC-004 | Mọi module | Mọi API | **T-NFR-SEC-007** | Tích hợp | T-NFR-SEC-007-01 (AC-SEC-09) mỗi build | MVP · M1 |
| NFR-SEC-008 — Phân hạng C0–C4; hai người duyệt C3; cửa sổ ≤ 15 phút | P0 | FR-SEC-006, FR-SEC-007 | M-SEC | API-CMD-05 · UI-22 | **T-NFR-SEC-008** | Tích hợp | AC-SEC-02/03; T-NFR-SEC-008-01 | MVP · M1 (CF-28/D-03; nâng hạng ngữ cảnh PDP-04/05: M2) |
| NFR-SEC-009 — SOE theo site, version, ký số, đề xuất/duyệt bởi hai người | P0 | FR-BESS-020, FR-BESS-007, FR-GRID-003 | M-BESS, M-SEC | API-CMD-08 · UI-07, UI-22 | **T-NFR-SEC-009** | Mô phỏng | AC-BESS-05/06; T-FR-BESS-020 (SOE tối thiểu) | MVP · M1 (tối thiểu), M2 (đầy đủ) |
| NFR-SEC-010 — Interlock IL-01…IL-10 tại edge | P0 | FR-SEC-010 | M-SEC · edge | API-CMD-07 · UI-24 | **T-NFR-SEC-010** | HIL | T-NFR-SEC-010-01…11 | MVP · M2 |
| NFR-SEC-011 — Mọi lệnh có `expires_at`; từ chối lệnh không hạn hoặc đến … | P0 | FR-SEC-008, FR-SEC-009 | M-SEC | API-CMD-01 | **T-NFR-SEC-011** | Mô phỏng | T-NFR-SEC-011-01 (AC-SEC-05); T-E2-01 (Message Expiry ở broker, edge offline qua hạn) | MVP · M1 |
| NFR-SEC-012 — Fleet Dispatch Governor | P0 | FR-SEC-012 | M-SEC | API-CMD-12 · UI-22 | **T-NFR-SEC-012** | Mô phỏng | T-NFR-SEC-012-01 | MVP · M2 |
| NFR-SEC-013 — Kill switch điều khiển từ xa (tắt C1, bật C3) | P0 | FR-SEC-013 | M-SEC | API-CMD-06 · UI-24 | **T-NFR-SEC-013** | Mô phỏng | T-NFR-SEC-013-01…04 (-04 là ca Gate M1) | MVP · M1 (04 bản mới) |
| NFR-SEC-014 — LOCAL/REMOTE phần cứng (hoặc native đọc được có biên bản) … | P0 | FR-SEC-010 | M-SEC · edge DI | API-CMD-07 · UI-24, UI-36 | **T-NFR-SEC-014** | HIL | T-NFR-SEC-014-01 | MVP · M2 |
| NFR-SEC-015 — Audit append-only + hash chain theo tenant; edge audit cục … | P0 (neo WORM P1) | FR-SEC-014, FR-SEC-023 | M-SEC | API-AUD-01, API-AUD-03 · UI-33 | **T-NFR-SEC-015** | Tích hợp | T-NFR-SEC-015-01 | MVP · M1 (WORM Phase 1) |
| NFR-SEC-016 — Vault/KMS; khóa ký không xuất; credential hãng mã hóa theo … | P0 | FR-SEC-017 | M-SEC · Vault/KMS | — | **T-NFR-SEC-016** | Tích hợp | Khóa không xuất; quét secret | MVP · M1 |
| NFR-SEC-017 — Phân vùng OT/IT tại edge | P0 | FR-SEC-018 | M-INT · edge | — · UI-27 | **T-NFR-SEC-017** | HIL | Quét mạng site; checklist commissioning | MVP · M1 |
| NFR-SEC-018 — Connector cloud hãng mặc định chỉ đọc; ghi qua cloud hãng … | P0 | FR-MON-003, FR-INT-021, FR-INT-028 | M-INT · connector | API-INT-07 | **T-NFR-SEC-018** | Tích hợp | Rà soát scope credential; ghi qua cloud hãng bị chặn khi cờ tắt | MVP · M1 |
| NFR-SEC-019 — Phát hiện điều khiển ngoài | P1 | FR-ALM-022 | M-ALM | API-ALM-01 · UI-14 | **T-NFR-SEC-019** | HIL | Đổi chế độ qua app hãng → `EXTERNAL_CONTROL_DETECTED` | Phase 1 |
| NFR-SEC-020 — OTA edge ký số, A/B, anti-rollback, canary | P0 | FR-INT-012 | M-INT | API-INT-05 · UI-26 | **T-NFR-SEC-020** | HIL | T-NFR-SEC-020-01 | MVP · M1 |
| NFR-SEC-021 — OCPP Security Profile ≥ 2, mục tiêu 3; TxDefaultProfile an … | P1 | FR-EV-003, FR-EV-005 | M-EV · edge CSMS | — · UI-11 | **T-NFR-SEC-021** | Mô phỏng | Charger SP1 bị từ chối; TxDefaultProfile an toàn | Phase 1 |
| NFR-SEC-022 — Hỗ trợ từ xa bằng reverse tunnel theo yêu cầu ≤ 2 h; không … | P1 | FR-SEC-024 | M-SEC | API-INT-11 | **T-NFR-SEC-022** | Pen-test | Tunnel ≤ 2 h, không route OT | Phase 1 |
| NFR-SEC-023 — Grant installer/vendor có hạn, chủ tài sản cấp/thu hồi, xem … | P0 | FR-ORG-009 | M-ORG, M-SEC | API-ORG-09 · UI-31 | **T-NFR-SEC-023** | Tích hợp | AC-ORG-04/05; break-glass ≤ 4 h | MVP · M1 |
| NFR-SEC-024 — Quy trình phát triển an toàn theo tinh thần IEC 62443-4-1 … | P1 | — (không có FR chức năng) | Quy trình | — | **T-NFR-SEC-024** | CI | SAST/SCA/SBOM/secret mỗi build (P0); pen-test, VDP (P1) | MVP (một phần), Phase 1 |
| NFR-SEC-025 — Lộ trình chứng nhận; không tuyên bố trước khi có chứng chỉ | P2 | FR-SEC-027 | Quy trình | — | **T-NFR-SEC-025** | Rà soát | Không tuyên bố chứng nhận trước khi có chứng chỉ | Phase 2 |
| NFR-SEC-026 — Phân loại dữ liệu D0–D4; hosting VN mặc định; DPIA và quy … | P0/P1 | FR-SEC-019 | M-SEC | — · UI-32 | **T-NFR-SEC-026** | Rà soát | Phân lớp D0–D4 trên mọi bảng; DPIA (P1) | MVP · M1 (DPIA Phase 1) |
| NFR-SEC-027 — Hardening edge (secure boot, mã hóa đĩa, không mật khẩu chung, SSH tắt) | P0 · M1 (secure boot P1 nếu phần cứng MVP không hỗ trợ) | FR-INT-002, FR-SEC-018 | M-INT · edge | — · UI-26 | **T-NFR-SEC-027** | Pen-test / HIL | Pen-test phần cứng (UART/JTAG, boot, đĩa); checklist commissioning | MVP · M1 |
| NFR-SEC-028 — Toàn vẹn thời gian edge, `UNSYNCED` → IL-06 | P0 · M2 | FR-INT-010, FR-SEC-010 | M-SEC · edge | API-TEL-10 · UI-26 | **T-NFR-SEC-028** | Mô phỏng | T-NFR-SEC-028-01: lệch đồng hồ/`ts_src` sai trên virtual site (15 §3.4) → IL-06 từ chối lệnh có hạn | MVP · M2 |
| NFR-SEC-029 — Quy trình ứng phó sự cố INC-* | P0 · M2 | F-SEC-27 (chưa có FR), FR-SEC-014 | M-SEC | API-AUD-05 · — | **T-NFR-SEC-029** | Diễn tập | Diễn tập bàn 6 tháng/lần; khống chế ≤ 30 phút, thông báo tenant ≤ 4 h | MVP · M2 |
| NFR-SEC-030 — Cổng kiểm thử an toàn driver ghi và release edge | P0 · M2 | FR-INT-003, FR-INT-014, FR-SEC-021 | M-INT · CI, lab | — | **T-NFR-SEC-030** | HIL + CI | Fuzz + ca HIL trước `VERIFIED_LAB`; kết quả virtual site không đủ (15 §4.3) | MVP · M2 |
| NFR-SEC-031 — Áp hàng loạt cấu hình/driver/SOE theo đợt | P1 | FR-INT-011, FR-BESS-007 | M-INT · ctl-app | API-INT-04 · UI-26 | **T-NFR-SEC-031** | Mô phỏng | Rollout ≤ 10 site đợt đầu trên edge ảo; tự dừng khi có sự kiện an toàn | Phase 1 |
| NFR-SEC-032 — Conduit IEC 104 | P1 có điều kiện | FR-INT-023, FR-GRID-013 | M-INT · edge | — | **T-NFR-SEC-032** | Mô phỏng + fuzz | Master 104 giả (c104/j60870, chỉ công cụ test) từ IP lạ bị từ chối; fuzz 10 §19.2 | Phase 1 (điều kiện) |
| NFR-SEC-033 — An toàn lệnh `COMMISSIONING_TEST` | P0 · M1 | FR-INT-016, FR-INT-017, FR-INT-018, FR-INT-031 | M-INT, M-SEC · edge | API-INT-08 · UI-27 | **T-NFR-SEC-033** | HIL | AC-INT-10; T-FR-INT-016b; site sandbox trên virtual site cho đào tạo | MVP · M1 |
| NFR-REL-013 — `run_mode` edge theo máy trạng thái, có audit | P0 · M2 | FR-MON-008, FR-DASH-004 | M-MON · edge | API-TEL-10 · UI-03 | **T-NFR-REL-013** | Mô phỏng | Chuyển trạng thái trên edge + virtual site; mỗi chuyển có audit | MVP · M2 |
| NFR-REL-014 — Bền vững khi mất nguồn edge | P0 · M1 | FR-INT-009, FR-INT-011, FR-BESS-007 | M-INT · edge | — | **T-NFR-REL-014** | HIL | Cắt nguồn ngẫu nhiên 100 lần; không hỏng cấu hình ký, không mất `command_id`/`last_seq` | MVP · M1 |
| NFR-REL-015 — Control plane fail-closed | P0 · M1 | FR-SEC-003, FR-SEC-007, FR-SEC-008 | M-SEC · ctl-app | API-CMD-01 · UI-21 | **T-NFR-REL-015** | Tích hợp | T-NFR-REL-015-01: IdP/PDP/Signer/ctl-db lỗi → không phát lệnh mới; monitoring chạy tiếp | MVP · M1 |
| NFR-REL-016 — Ưu tiên và backpressure | P0 · M1 | FR-INT-008, FR-INT-009, FR-HIST-002 | M-INT · broker, ingest, edge | MQTT | **T-NFR-REL-016** | Tải | Edge ảo + Toxiproxy mất WAN/broker (15 §3.4); `event`/`cmd-ack`/`state` không bị bỏ; lô ≤ `max_batch_bytes` (T-E2-03) | MVP · M1 |
| NFR-REL-017 — Game day và chaos | P0/P1 · M2 | FR-OPT-006, FR-BESS-009 | Mọi mặt phẳng | — | **T-NFR-REL-017** | Game day | Mất cloud 4 h trên HIL hằng quý; chaos broker/KMS/DR (P1) | MVP · M2 |
| NFR-REL-018 — Trình tự DR | P1 | FR-SEC-013 | Hạ tầng, ctl-app | API-CMD-06 · UI-24 | **T-NFR-REL-018** | Diễn tập | Failover DR: kill switch nền tảng trước, mở lại control plane bằng C3 | Phase 1 |
| NFR-OBS-008 — Cảnh báo nền tảng, runbook, trực ca 24/7 | P0 · M2 | FR-ALM-015 (P1), FR-ALM-005 | M-ALM · vận hành | API-ALM-11, API-ALM-12 · UI-17 | **T-NFR-OBS-008** | Rà soát + diễn tập | Rà soát runbook; diễn tập gọi trực ca trước site M2 đầu tiên | MVP · M2 |
| NFR-OBS-009 — Forensic bundle, log edge ≥ 30 ngày, ghim 1 s | P0 (bundle, log) · M2; P1 (ghim) | F-SEC-26 (chưa có FR) | M-SEC · ctl-app, edge | API-AUD-04 · UI-33 | **T-NFR-OBS-009** | Mô phỏng | Tạo bundle cho sự cố mô phỏng trên virtual site; hash/ký kiểm được | MVP · M2 (ghim Phase 1) |

### 4.2 Lịch sử: NFR mã đề xuất của 10 (nay đã là NFR chính thức của 04)

10 §20 đề xuất 14 mã mới. 06 đã trích 7 trong số đó. Bản 04 mới (sau bản dựng của 12) đã xác nhận cả 14 mã với cùng số và cấp thêm NFR-SEC-033 (an toàn lệnh `COMMISSIONING_TEST`). Vòng nhất quán 2026-10-10 đã đưa cả 15 mã vào §4.1 với ưu tiên/Gate theo 04 §6. Bảng dưới chỉ giữ để truy vết nguồn gốc mã (10 §20); khi lệch, §4.1 là chuẩn.

| Mã đề xuất | Tóm tắt (10 §20) | Ưu tiên · Gate (10) | FR liên quan | Test | Ghi chú |
|---|---|---|---|---|---|
| NFR-SEC-027 | Hardening edge (secure boot, mã hóa đĩa, không mật khẩu chung, SSH tắt) | P0 · M1 | FR-SEC-018, FR-INT-001 | Pen-test phần cứng; checklist commissioning | 06 ADR-07 đã trích |
| NFR-SEC-028 | Toàn vẹn thời gian, `UNSYNCED` → IL-06 | P0 · M2 | FR-INT-010, FR-SEC-010 | T-NFR-SEC-028-01 | — |
| NFR-SEC-029 | Ứng phó sự cố INC-* | P0 · M2 | Không có FR (sổ sự cố ở _catalog-gaps) | Diễn tập bàn 6 tháng/lần | GAP-12-15 |
| NFR-SEC-030 | Cổng kiểm thử an toàn cho driver ghi và release edge | P0 · M2 | FR-INT-006, FR-INT-014 | Báo cáo test kèm release | 06 §16 đã trích |
| NFR-SEC-031 | Áp hàng loạt cấu hình/SOE theo đợt | P1 | FR-INT-011, FR-BESS-007 | Test pipeline rollout | — |
| NFR-SEC-032 | Conduit IEC 104 | P1 có điều kiện | FR-INT-023, FR-GRID-013 | Fuzz 10 §19.2; test điều độ | GAP-12-03 |
| NFR-REL-013 | `run_mode` edge theo máy trạng thái, có audit | P0 · M2 | FR-MON-008, FR-DASH-004 | Test chuyển trạng thái | — |
| NFR-REL-014 | Bền vững khi mất nguồn edge (journal, fsync, A/B cấu hình) | P0 · M1 | FR-INT-009, FR-INT-011, FR-BESS-007 | Cắt nguồn ngẫu nhiên 100 lần | — |
| NFR-REL-015 | Control plane fail-closed | P0 · M1 | FR-SEC-003, FR-SEC-007, FR-SEC-008 | T-NFR-REL-015-01 | 06 đã trích; ảnh hưởng mọi FR điều khiển |
| NFR-REL-016 | Ưu tiên và backpressure (`event`/`cmd-ack`/`state` không bị bỏ) | P0 · M1 | FR-INT-008, FR-INT-009, FR-HIST-002 | Test tải phục hồi | 06 ADR-04 đã trích |
| NFR-REL-017 | Game day mất cloud 4 h hằng quý | P0/P1 · M2 | FR-OPT-006, FR-BESS-009 | Biên bản game day | 06 đã trích |
| NFR-REL-018 | Trình tự DR (kill switch nền tảng trước, mở control plane theo C3) | P1 | FR-SEC-013 | Diễn tập DR | 06 §20 trích dạng "018" |
| NFR-OBS-008 | Danh mục cảnh báo nền tảng, runbook, trực ca 24/7 từ site M2 đầu tiên | P0 | FR-ALM-015 (P1), FR-ALM-005 | Rà soát runbook; diễn tập gọi trực ca | Điều kiện M2 (10 I-R-11) nhưng FR leo thang là P1 → GAP-12-03 |
| NFR-SEC-033 | An toàn lệnh `COMMISSIONING_TEST`: chỉ ở `commissioning` (IL-10), xác nhận có mặt bằng nút vật lý, phong bì test, `REVERT_DEFAULT` khi thoát (04 cấp) | P0 · M1 | FR-INT-031, FR-INT-016…018 | T-FR-INT-031 | Đóng phần commissioning của GAP-12-03 |
| NFR-OBS-009 | Forensic bundle, log edge ≥ 30 ngày, ghim cửa sổ 1 s | P0 (bundle, log), P1 (ghim) | Không có FR; API-AUD-04 | Tạo bundle cho sự cố mô phỏng | GAP-12-15 |

---

## 5. Truy vết API → UI (suy ra)

09 không trích mã API nào. 06 không ghi trang UI nào. Bảng dưới đây ghép hai phía qua FR (API → FR dùng nó → UI của FR) và là `[INFERENCE]` của 12. 09 nên dùng bảng này làm điểm xuất phát khi thêm cột API vào đặc tả trang (GAP-12-08).

| API (06) | Phát hành (06; `Phase n` = hạng 03) | Số FR dùng | FR dùng (rút gọn) | UI dùng (suy ra) | Ghi chú |
|---|---|---|---|---|---|
| API-AUTH-01 | MVP | 1 | FR-SEC-001 | UI-34 |  |
| API-AUTH-02 | MVP | 4 | FR-DASH-003, FR-DASH-007, FR-SEC-003, FR-SEC-022 | UI-02, UI-21, UI-31 |  |
| API-AUTH-03 | MVP | 1 | FR-SEC-002 | UI-31, UI-34 |  |
| API-AUTH-04 | MVP | 2 | FR-DASH-008, FR-MON-005 | UI-01, UI-03, UI-04 | Hạ tầng SSE; người dùng gián tiếp qua mọi trang live |
| API-AUTH-05 | MVP | 1 | FR-SEC-001 | UI-34 |  |
| API-ORG-01 | MVP | 2 | FR-ORG-001, FR-ORG-017 | UI-32 |  |
| API-ORG-02 | MVP | 4 | FR-ORG-002, FR-ORG-011, FR-DASH-003, FR-DASH-013 | UI-01, UI-02, UI-29, UI-32 |  |
| API-ORG-03 | MVP | 2 | FR-ORG-004, FR-ORG-018 | UI-29 |  |
| API-ORG-04 | MVP | 2 | FR-ORG-005, FR-ORG-006 | UI-29 |  |
| API-ORG-05 | MVP | 6 | FR-ORG-003, FR-MON-006, FR-MON-011, FR-BESS-002, FR-PV-002, FR-PV-012 | UI-04, UI-06, UI-07, UI-09, UI-29 |  |
| API-ORG-06 | MVP | 6 | FR-ORG-006, FR-MON-011, FR-GRID-001, FR-GRID-002, FR-GRID-015, FR-EV-001 | UI-06, UI-10, UI-11, UI-29 |  |
| API-ORG-07 | MVP | 1 | FR-ORG-007 | UI-31 |  |
| API-ORG-08 | MVP | 1 | FR-ORG-008 | UI-31 |  |
| API-ORG-09 | MVP | 1 | FR-ORG-009 | UI-31 |  |
| API-ORG-10 | MVP | 1 | FR-ORG-010 | UI-29 |  |
| API-ORG-11 | Phase 1 | 1 | FR-ORG-015 | UI-29 |  |
| API-ORG-12 | Phase 1 | 2 | FR-ORG-013, FR-DASH-011 | UI-31, UI-35 |  |
| API-TEL-01 | MVP | 2 | FR-HIST-001, FR-HIST-003 | UI-28 | UI-28 chỉ dùng gián tiếp khi map điểm |
| API-TEL-02 | MVP | 11 | FR-DASH-005, FR-MON-009, FR-HIST-004, FR-HIST-005, FR-HIST-008, FR-HIST-010 … (+5) | UI-03, UI-04, UI-07, UI-08, UI-09, UI-13 |  |
| API-TEL-03 | MVP | 14 | FR-DASH-008, FR-DASH-010, FR-MON-001, FR-MON-002, FR-MON-005, FR-MON-006 … (+8) | UI-01, UI-03, UI-04, UI-07, UI-09, UI-10, UI-14 |  |
| API-TEL-04 | MVP | 1 | FR-MON-004 | UI-03, UI-05 |  |
| API-TEL-05 | MVP | 5 | FR-MON-010, FR-HIST-009, FR-HIST-013, FR-GRID-016, FR-EV-001 | UI-04, UI-05, UI-10, UI-11 |  |
| API-TEL-06 | MVP | 13 | FR-DASH-006, FR-DASH-008, FR-BESS-013, FR-BESS-014, FR-BESS-015, FR-PV-004 … (+7) | UI-01, UI-03, UI-07, UI-09, UI-10 |  |
| API-TEL-07 | MVP | 7 | FR-HIST-006, FR-HIST-007, FR-HIST-008, FR-HIST-013, FR-HIST-015, FR-HIST-016 … (+1) | UI-03, UI-05, UI-13, UI-26, UI-30 |  |
| API-TEL-08 | MVP | 4 | FR-MON-007, FR-BESS-012, FR-PV-010, FR-INT-020 | UI-08, UI-09, UI-12, UI-27, UI-28 |  |
| API-TEL-09 | MVP | 4 | FR-DASH-001, FR-DASH-002, FR-DASH-008, FR-DASH-009 | UI-01, UI-03 |  |
| API-TEL-10 | MVP | 2 | FR-MON-008, FR-INT-010 | UI-26 |  |
| API-TEL-11 | Phase 1 | 1 | FR-HIST-014 | UI-13 |  |
| API-LIVE-01 | MVP | 6 | FR-DASH-004, FR-MON-001, FR-MON-002, FR-MON-004, FR-GRID-007, FR-OPT-002 | UI-03, UI-04, UI-05, UI-10, UI-18, UI-24 |  |
| API-LIVE-02 | MVP | 2 | FR-DASH-001, FR-DASH-009 | UI-01 |  |
| API-LIVE-03 | MVP | 1 | FR-ALM-005 | UI-14 |  |
| API-LIVE-04 | MVP | 3 | FR-OPT-009, FR-SEC-009, FR-SEC-015 | UI-19, UI-21, UI-23 |  |
| API-LIVE-05 | Phase 1 | 1 | FR-MON-013 | UI-12 |  |
| API-ALM-01 | MVP | 8 | FR-DASH-010, FR-BESS-010, FR-ALM-001, FR-ALM-004, FR-ALM-005, FR-ALM-011 … (+2) | UI-03, UI-07, UI-14, UI-24 |  |
| API-ALM-02 | MVP | 1 | FR-ALM-006 | UI-15 |  |
| API-ALM-03 | MVP | 3 | FR-DASH-010, FR-ALM-005, FR-ALM-019 | UI-03, UI-14, UI-15 |  |
| API-ALM-04 | MVP | 3 | FR-ALM-003, FR-ALM-009, FR-ALM-021 | UI-10, UI-14, UI-32 |  |
| API-ALM-05 | MVP | 3 | FR-ALM-007, FR-ALM-013, FR-ALM-014 | UI-17 |  |
| API-ALM-06 | MVP | 2 | FR-ALM-010, FR-ALM-019 | UI-15, UI-16 |  |
| API-ALM-07 | Phase 1 | 1 | FR-ALM-016 | UI-16 |  |
| API-ALM-08 | Phase 1 | 1 | FR-ALM-018 | UI-16 |  |
| API-CMD-01 | MVP | 17 | FR-BESS-003, FR-BESS-004, FR-BESS-005, FR-BESS-006, FR-BESS-018, FR-BESS-019 … (+11) | UI-07, UI-09, UI-10, UI-11, UI-18, UI-21, UI-22, UI-24, UI-27 | Danh sách `type` chưa phủ mọi FR dùng nó (GAP-12-07) |
| API-CMD-02 | MVP | 5 | FR-BESS-003, FR-BESS-008, FR-INT-007, FR-SEC-009, FR-SEC-015 | UI-07, UI-18, UI-21, UI-23, UI-27, UI-28 |  |
| API-CMD-03 | MVP | 2 | FR-SEC-009, FR-SEC-015 | UI-21, UI-23 |  |
| API-CMD-04 | MVP | 5 | FR-OPT-008, FR-SEC-008, FR-SEC-009, FR-SEC-016, FR-SEC-021 | UI-19, UI-21, UI-23, UI-24 |  |
| API-CMD-05 | MVP | 5 | FR-BESS-018, FR-BESS-019, FR-SEC-006, FR-SEC-007, FR-SEC-021 | UI-07, UI-21, UI-22, UI-24 |  |
| API-CMD-06 | MVP | 2 | FR-SEC-013, FR-SEC-021 | UI-22, UI-24 |  |
| API-CMD-07 | MVP | 8 | FR-DASH-004, FR-BESS-008, FR-BESS-009, FR-OPT-001, FR-OPT-002, FR-OPT-003 … (+2) | UI-03, UI-07, UI-18, UI-24 |  |
| API-CMD-08 | MVP | 3 | FR-BESS-007, FR-EV-006, FR-SEC-021 | UI-07, UI-11, UI-22, UI-24 |  |
| API-CMD-09 | MVP | 4 | FR-GRID-003, FR-GRID-005, FR-GRID-006, FR-OPT-003 | UI-10, UI-18, UI-22, UI-24, UI-29 |  |
| API-CMD-10 | MVP | 2 | FR-SEC-005, FR-SEC-021 | UI-24 |  |
| API-CMD-11 | MVP | 2 | FR-SEC-005, FR-SEC-021 | UI-24 | FR-SEC-021 có, nhưng 03 chưa có F- riêng cho hồ sơ M2 (_catalog-gaps) |
| API-CMD-12 | MVP | 3 | FR-SEC-012, FR-SEC-021, FR-SEC-022 | UI-21, UI-22, UI-24 |  |
| API-OPT-01 | MVP | 7 | FR-BESS-004, FR-EV-007, FR-OPT-005, FR-OPT-014, FR-OPT-015, FR-OPT-017 … (+1) | UI-07, UI-10, UI-11, UI-18, UI-19, UI-21 |  |
| API-OPT-02 | MVP | 2 | FR-OPT-007, FR-OPT-009 | UI-19, UI-20 |  |
| API-OPT-03 | MVP | 5 | FR-DASH-005, FR-OPT-009, FR-OPT-011, FR-OPT-013, FR-ADV-001 | UI-03, UI-19 |  |
| API-OPT-04 | MVP | 2 | FR-OPT-007, FR-OPT-008 | UI-19, UI-20 |  |
| API-OPT-05 | MVP | 1 | FR-OPT-010 | UI-20 |  |
| API-OPT-06 | MVP | 1 | FR-OPT-005 | UI-18, UI-19 |  |
| API-OPT-07 | MVP | 1 | FR-OPT-006 | UI-18, UI-24 |  |
| API-OPT-08 | Phase 1 | 1 | FR-OPT-012 | UI-19 |  |
| API-OPT-09 | Phase 1 | 1 | FR-OPT-016 | UI-18 |  |
| API-TAR-01 | MVP | 2 | FR-TAR-001, FR-TAR-007 | UI-25 |  |
| API-TAR-02 | MVP | 5 | FR-TAR-001, FR-TAR-007, FR-TAR-008, FR-TAR-009, FR-TAR-010 | UI-25 |  |
| API-TAR-03 | MVP | 2 | FR-TAR-002, FR-TAR-003 | UI-25 |  |
| API-TAR-04 | MVP | 2 | FR-TAR-003, FR-TAR-004 | UI-25, UI-29 |  |
| API-TAR-05 | MVP | 1 | FR-TAR-005 | UI-25 |  |
| API-TAR-06 | MVP | 1 | FR-TAR-006 | UI-10, UI-25, UI-30 |  |
| API-TAR-07 | Phase 1 | 1 | FR-TAR-011 | UI-25 |  |
| API-REP-01 | MVP | 12 | FR-REP-001, FR-REP-002, FR-REP-003, FR-REP-004, FR-REP-008, FR-REP-009 … (+6) | UI-30 |  |
| API-REP-02 | MVP | 11 | FR-REP-001, FR-REP-002, FR-REP-003, FR-REP-004, FR-REP-008, FR-REP-009 … (+5) | UI-30 |  |
| API-REP-03 | MVP | 2 | FR-REP-005, FR-TAR-007 | UI-25, UI-30 |  |
| API-REP-04 | MVP | 2 | FR-REP-006, FR-REP-017 | UI-13, UI-30 |  |
| API-REP-05 | MVP | 1 | FR-REP-007 | UI-10, UI-30 |  |
| API-REP-06 | Phase 1 | 1 | FR-REP-013 | UI-30 |  |
| API-REP-07 | Phase 1 | 2 | FR-HIST-017, FR-REP-014 | UI-30 |  |
| API-INT-01 | MVP | 2 | FR-ORG-018, FR-INT-002 | UI-26, UI-27, UI-29 |  |
| API-INT-02 | MVP | 2 | FR-ORG-018, FR-INT-002 | UI-26, UI-27, UI-29 | Người gọi là edge (máy); UI suy ra chỉ là trang hiển thị kết quả claim |
| API-INT-03 | MVP | 1 | FR-INT-011 | UI-26 |  |
| API-INT-04 | MVP | 2 | FR-INT-011, FR-INT-023 | UI-26 |  |
| API-INT-05 | MVP | 1 | FR-INT-012 | UI-26 |  |
| API-INT-06 | MVP | 3 | FR-INT-003, FR-INT-006, FR-INT-013 | UI-28 |  |
| API-INT-07 | MVP (Huawei), Phase 1 (hãng khác) | 2 | FR-MON-003, FR-INT-021 | UI-04, UI-26 |  |
| API-INT-08 | MVP | 6 | FR-INT-015, FR-INT-016, FR-INT-017, FR-INT-018, FR-INT-020, FR-SEC-021 | UI-24, UI-27, UI-28 |  |
| API-INT-09 | MVP | 1 | FR-INT-019 | UI-27 |  |
| API-INT-10 | Phase 1 | 1 | FR-INT-027 | UI-28 |  |
| API-AUD-01 | MVP | 1 | FR-SEC-014 | UI-33 |  |
| API-AUD-02 | MVP | 2 | FR-SEC-009, FR-SEC-015 | UI-21, UI-23 |  |
| API-AUD-03 | Phase 1 | 1 | FR-SEC-023 | UI-33 |  |
| API-AUD-04 | MVP (bundle), Phase 1 (ghim 1 s) | 1 | FR-SEC-014 | UI-33 | Không có FR riêng: gói bằng chứng sự cố mới ở _catalog-gaps (GAP-12-15) |
| API-PUB-01 | Phase 1 | 1 | FR-SEC-026 | UI-32 |  |
| API-PUB-02 | Phase 1 | 1 | FR-INT-025 | UI-32 | Người dùng là bên thứ ba; UI-32 chỉ quản lý client |
| API-PUB-03 | Phase 1 | 2 | FR-ALM-020, FR-INT-026 | UI-16, UI-32 | Người dùng là bên thứ ba/CMMS; chưa có trang cấu hình webhook (GAP-12-10) |
| API-PUB-04 | Phase 2 | 1 | FR-INT-030 | — | Phase 2; chỉ bên thứ ba, không có UI (đúng thiết kế) |

---

## 6. Phân tích độ phủ và khoảng trống

### 6.1 FR không có trang UI

76 FR không xuất hiện trong 09 §13.1. Phân loại:

**(a) Backend hoặc hạ tầng, không cần UI (16) — không phải khoảng trống:** FR-MON-001, FR-MON-002, FR-HIST-001, FR-HIST-002, FR-HIST-003, FR-HIST-004, FR-HIST-017, FR-INT-014, FR-INT-025, FR-INT-030, FR-SEC-004, FR-SEC-017, FR-SEC-018, FR-SEC-025, FR-SEC-027, FR-SEC-028. FR-INT-025 và FR-INT-030 có người dùng là bên thứ ba qua API. FR-HIST-001 được khai báo gián tiếp ở UI-28.

**(b) Có chỗ trên trang sẵn có nhưng 09 chưa ghi truy vết (33) — GAP-12-09.** 09 thêm vào §13.1. Nếu trang chưa có nội dung đó thì thêm cả nội dung.

| FR | Trang đề xuất | Ghi chú |
|---|---|---|
| FR-ORG-012 | UI-29 | UI-29 đã nhắc "mẫu site" |
| FR-DASH-010 | UI-03, UI-14 (responsive) | 09 §6.3 đã có breakpoint; FR mobile chưa trỏ |
| FR-DASH-012 | UI-13, UI-01 | UI-13 có "Lưu view" |
| FR-HIST-005 | UI-13 | Chọn độ phân giải |
| FR-HIST-006 | UI-03, UI-30 | "Dữ liệu đầy đủ đến…" |
| FR-HIST-011 | UI-32 | Hiển thị chính sách lưu giữ (cùng FR-SEC-020) |
| FR-HIST-014 | UI-13 | Thao tác sửa/thay thế có audit, P1 |
| FR-HIST-016 | UI-26 | Cảnh báo lệch đồng hồ thiết bị |
| FR-BESS-013, FR-BESS-014, FR-BESS-016 | UI-07 | UI-07 đã nhắc EFC, SOH |
| FR-BESS-020 | UI-07, UI-22, UI-24 | SOE tối thiểu Gate M1 (FR mới của 04); UI-07 đã có SOE, UI-22 là hàng đợi duyệt |
| FR-BESS-018 | UI-07, UI-22 | 09 §13.2 đã nhận "Dừng vận hành từ xa" ở UI-07 (P1) nhưng §13.1 không ghi FR |
| FR-GRID-009 | UI-10, UI-25 | UI-25 đã nhắc ngân sách xuất |
| FR-GRID-011, FR-GRID-014 | UI-10 | — |
| FR-GRID-013 | UI-24, UI-26 | Trạng thái liên kết điều độ; UI-32 đã nhắc IEC 104 |
| FR-GRID-015 | UI-10, UI-29 | 09 ghi F-GRID-15 ở UI-29 nhưng không ghi FR |
| FR-GRID-017 | UI-04 | UI-04 đã nhắc máy phát |
| FR-EV-003, FR-EV-004 | UI-11 (và UI-26 cho CSMS edge) | — |
| FR-OPT-017 | UI-18, UI-10 | — |
| FR-OPT-018 | UI-19 | — |
| FR-OPT-019 | UI-18 | — |
| FR-ALM-021 | UI-14 | Nhãn "Thống kê", không "AI" |
| FR-ALM-022 | UI-14, UI-24 | — |
| FR-INT-021 | UI-26 | 09 ghi F-INT-13 ở UI-26 nhưng không ghi FR |
| FR-INT-022 | UI-28 | — |
| FR-INT-023, FR-INT-024 | UI-26 | — |
| FR-INT-031 | UI-27 | Phiên `COMMISSIONING_TEST` (FR mới của 04); 09 đã nhắc lệnh này ở UI-27 |
| FR-INT-027 | UI-28 | UI-28 đã nhắc "nhập dữ liệu" |
| FR-ADV-003 | UI-19 | Nguồn dự báo PV |

**(c) FR P1 chưa có trang (11) — GAP-12-10.** 09 cấp trang hoặc tab mới trước phase lộ trình của FR (cột "Lộ trình (11)": FR-ORG-014, FR-HIST-015, FR-SEC-024 ở Phase 2; còn lại Phase 3):

| FR | Nội dung cần trang | Đề xuất vị trí |
|---|---|---|
| FR-ORG-014 | Tài liệu site/tài sản có phiên bản | Tab "Tài liệu" trong UI-29 |
| FR-ORG-016 | Hợp đồng, bảo hành | Tab "Hợp đồng" trong UI-29 |
| FR-HIST-015 | Bảng điều khiển chất lượng dữ liệu | Tab DQ trong UI-13 hoặc trang mới |
| FR-BESS-015 | Theo dõi điều kiện bảo hành BESS | Tab "Bảo hành" trong UI-07 |
| FR-BESS-017 | Sổ cái nguồn gốc năng lượng trong pin | Thẻ trong UI-07 |
| FR-GRID-016 | Phân tích phụ tải | Tab "Phụ tải" trong UI-10 |
| FR-INT-026 | Cấu hình webhook, xem lần gửi | UI-32 |
| FR-SEC-024 | Yêu cầu và duyệt phiên hỗ trợ từ xa | UI-26 (yêu cầu) + UI-24 (duyệt của chủ site) |
| FR-ADV-004, FR-ADV-005, FR-ADV-006 | Đánh giá dự báo, mô hình F2, what-if định cỡ | Trang mới "Dự báo và mô phỏng" (09 cấp mã) |

**(d) FR P2 chưa có trang (16) — GAP-12-19, ưu tiên thấp:** FR-BESS-019, FR-PV-013, FR-GRID-018, FR-GRID-019, FR-EV-009, FR-EV-010, FR-OPT-020, FR-OPT-021, FR-INT-028, FR-INT-029, FR-ADV-007, FR-ADV-008, FR-ADV-009, FR-ADV-010, FR-ADV-011, FR-ADV-012.

**(e) FR đã có trang, 12 thêm trang phụ (15):** FR-ORG-013 (+UI-31), FR-REP-007 (+UI-10), FR-REP-015 (+UI-10), FR-TAR-004 (+UI-29), FR-TAR-006 (+UI-10, UI-30), FR-BESS-003 (+UI-18, UI-27), FR-BESS-007 (+UI-24), FR-BESS-009 (+UI-24), FR-BESS-010 (+UI-14), FR-PV-003 (+UI-21), FR-GRID-003 (+UI-22), FR-EV-005 (+UI-21), FR-OPT-006 (+UI-24), FR-INT-002 (+UI-27), FR-INT-007 (+UI-21). Đây là bổ sung truy vết, không phải thiếu tính năng.

### 6.2 Trang UI không có FR

- **Không có trang nào trong 36 trang thiếu FR.** Mọi UI-01…UI-36 ghi ít nhất một FR trong 09 §13.1.
- **Truy vết ngược chưa khớp (GAP-12-11).** Trang ghi F- trong cột "F-" nhưng không ghi FR có F- đó làm F- chính:

| Trang | FR thiếu trong cột FR của 09 |
|---|---|
| UI-02 | FR-ORG-002 |
| UI-03 | FR-OPT-009 |
| UI-04 | FR-MON-001, FR-MON-002 (backend; chỉ cần ghi chú) |
| UI-10 | FR-TAR-006 |
| UI-19 | FR-TAR-002 |
| UI-21 | FR-PV-003, FR-GRID-003, FR-GRID-006, FR-EV-005, FR-SEC-015 |
| UI-23 | FR-SEC-008 |
| UI-24 | FR-BESS-007, FR-OPT-001 |
| UI-26 | FR-INT-021 |
| UI-27 | FR-BESS-007, FR-GRID-004, FR-OPT-003, FR-INT-002, FR-INT-005, FR-INT-007, FR-SEC-005, FR-SEC-021 |
| UI-29 | FR-ORG-012, FR-GRID-015 |
| UI-31 | FR-SEC-022 |

- **Nội dung trang không có FR (GAP-12-12):**
  - Tùy chọn hiển thị của người dùng (ngôn ngữ, sáng/tối, mật độ, trang đầu) ở UI-32. Không có F-, FR hay thực thể. Đã ghi ở [_catalog-gaps](notes/_catalog-gaps.md) (Agent H).
  - Trang phương pháp và thuật ngữ trong ứng dụng. FR-REP-008, FR-DASH-006 và nguyên tắc UXP-12 của 09 đòi "link phương pháp" cạnh số ước tính nhưng không FR nào tạo nội dung đó.
  - Mã xác nhận có mặt cho lệnh `COMMISSIONING_TEST` trên UI-36 và UI-27. Không có FR. Tính năng lệnh thử commissioning còn ở _catalog-gaps (Agent E).

### 6.3 Tính năng không có FR

- **7 F- không có FR, đều có chủ ý.** F-PV-14, F-EV-11, F-OPT-21, F-ADV-12, F-ADV-13, F-ADV-14, F-ADV-15 nằm ngoài phạm vi; ràng buộc ở 04 §5.16. Không cần sửa. Hai tính năng bị cấm F-BESS-19 và F-BESS-20 (C4) có FR dạng "không được" là FR-BESS-011, nên không nằm trong danh sách này. 251 F- còn lại đều có ít nhất một FR.
- **Cập nhật vòng nhất quán 2026-10-10:** 03 nay có 270 F- (thêm 12 F- từ `_catalog-gaps`). 6 F- mới chưa có FR riêng ở 04 (04 §7.1): F-INT-30, F-INT-32, F-INT-33, F-OPT-22, F-OPT-23, F-ORG-18 (phần MVP); F-SEC-26/27 chỉ có NFR (NFR-OBS-009, NFR-SEC-029). Bảng dưới là bản dựng ban đầu, giữ để truy vết.
- **18 tính năng trong [_catalog-gaps](notes/_catalog-gaps.md) chưa có F- trong 03 (GAP-12-15).** Hai vai trò `TECHNICIAN` và `PLATFORM_ADMIN` gộp một dòng:

| Tính năng (người ghi) | FR ở 04 | API ở 06 | UI ở 09 | Trạng thái |
|---|---|---|---|---|
| Vai trò `TECHNICIAN`, `PLATFORM_ADMIN` (D) | Có trong FR-ORG-008 qua 04 §3.2 | API-ORG-08 | UI-31, UI-16 | Thiếu F-; chỉ cần 03 cập nhật F-ORG-08 |
| Hồ sơ sẵn sàng Gate M2 (D) | FR-SEC-021 | API-CMD-11 | UI-24 | Thiếu F- riêng |
| Bản ghi đồng ý của chủ tài sản (D) | Một phần FR-SEC-005 | API-CMD-10 | UI-24 | Thiếu F-; thực thể `ConsentRecord` có |
| Liên hệ trực ca trong chi tiết cảnh báo (D) | FR-ALM-006 | API-ALM-02 | UI-15 | Thiếu thực thể (`OnCallContact`) |
| KPI sức khỏe thiết bị (F) | **Không** | Không | Không | `AssetHealthStatus` có ở 05 nhưng không ai dùng (GAP-12-14) |
| KPI SOC/năng lượng lưu trữ cấp danh mục (F) | Một phần FR-DASH-006 | API-TEL-06 | UI-01 | 03 §6 chưa có dòng KPI |
| Lịch ngày đặc biệt/ngày lễ (F) | Một phần FR-TAR-002 | API-TAR-03 | UI-25 | Có thể gộp vào F-TAR-02 |
| Quản lý phát hành và thu hồi driver (E) | Một phần FR-INT-003, FR-INT-006, FR-INT-013 | API-INT-06 (chỉ đọc) | UI-28 | Thiếu FR thu hồi/khóa driver lỗi |
| Lệnh thử `COMMISSIONING_TEST` và site sandbox (E) | **Không** (FR-INT-016…018 dùng nhưng không định nghĩa) | API-INT-08 | UI-27 | Liên quan an toàn, P0 → GAP-12-03 |
| Theo dõi đáp ứng vật lý `tracking_state` (E) | **Không** | Không | Không | FR-INT-007 chỉ có readback |
| Chạy bóng (shadow mode) chiến lược (G) | **Không** | Không | Không | Điều kiện cổng tầng 3 (08 §13.2) |
| Quản lý phiên bản chiến lược (G) | Ngầm trong FR-OPT-005 | API-OPT-01 | UI-18 | Thiếu FR và F- riêng |
| Gói bằng chứng sự cố, ghim 1 s (I) | **Không** | **API-AUD-04 (MVP)** | Không | API có trước yêu cầu |
| Sổ sự cố an toàn/bảo mật (I) | **Không** | Không | Không | NFR-SEC-029 (đề xuất) cần nó |
| Sandbox API công khai (J) | **Không** | Không | Không | hạng 03: Phase 1 cùng FR-INT-025 (lộ trình Phase 3, 3J) |
| Tùy chọn hiển thị người dùng (H) | **Không** | Không | UI-32 | GAP-12-12 |
| Trang phương pháp và thuật ngữ (H) | **Không** | Không | Không | GAP-12-12 |

### 6.4 Tính năng điều khiển thiếu NFR an toàn hoặc NFR khi lỗi

Mọi lệnh đi qua chuỗi chung của 10 §11. Chuỗi này có NFR-SEC-004 (ký), NFR-SEC-006 (PDP), NFR-SEC-008 (hạng, C3), NFR-SEC-011 (hạn), NFR-SEC-012 (Governor), NFR-SEC-013 (kill switch) và NFR-REL-001/002/012 (mất cloud, mất liên kết thiết bị, không thi hành lệnh cũ). Bảng chỉ ghi NFR **riêng** và khoảng trống. FR-BESS-011 (C4) không được liệt kê vì không có đường lệnh.

| FR | Hạng·Gate | NFR an toàn riêng | NFR khi lỗi riêng | Khoảng trống | Sửa (chủ) |
|---|---|---|---|---|---|
| FR-BESS-003 | C1·M1 | NFR-SEC-018 (native qua logger) | FR-ALM-011 (`FAILED_NO_EFFECT`) | Không | — |
| FR-BESS-004 | C1/C2·M1 | NFR-SEC-008 | NFR-REL-001 | Không | — |
| FR-BESS-005 | C1·M2 | NFR-SEC-009 | NFR-REL-002, NFR-REL-007 | Không | — |
| FR-BESS-006 | C1/C2·M1 | NFR-SEC-009 | NFR-REL-007 | Không | — |
| FR-BESS-007 | C3·M2 | NFR-SEC-009, NFR-SEC-031 | NFR-REL-014 | Không (04 đã xác nhận) | — |
| FR-BESS-020 | C3·M1 | NFR-SEC-008, NFR-SEC-009 (tối thiểu) | NFR-REL-014 | Không | — |
| FR-BESS-009 | C1·M2 | NFR-SEC-010 | NFR-REL-003, NFR-REL-007 | Không | — |
| FR-BESS-016 | C1·M2 (P1) | NFR-SEC-009 | NFR-REL-002 (chung) | Không có yêu cầu khi **một** PCS mất liên lạc trong site nhiều PCS: chia lại hay hạ tổng | 10 soạn, 04 cấp mã (GAP-12-03) |
| FR-BESS-018 | C3·M2 (P1) | NFR-SEC-008 | — | Không quy định trạng thái "đã dừng" giữ qua mất cloud/khởi động lại edge, và ai được khởi động lại (C3 từ xa hay tại chỗ) | 10, 04 (GAP-12-03) |
| FR-BESS-019 | C3·M2 (P2) | NFR-SEC-008 | — | Thiếu giới hạn số lần reset/ngày để tránh vòng reset lỗi | 10 (P2) |
| FR-PV-003 | C1·M1 | NFR-SEC-011 | NFR-REL-007 (PV về giới hạn native) | Không | — |
| FR-PV-011 | C1·M1 (P2) | NFR-SEC-006 | — | Chấp nhận được ở P2; ghi rủi ro mất sản lượng khi quét | 13 |
| FR-PV-013 | C2·M2 (P2) | — | — | Không có giới hạn Q trong SOE, không có hành vi khi mất `MTR_POC` | 10, 05 (SOE) |
| FR-GRID-003 | C3·M1 | NFR-SEC-008, NFR-SEC-009 (SOE tối thiểu, FR-BESS-020) | NFR-REL-014 | Không (04 đã xác nhận NFR-REL-014) | — |
| FR-GRID-004 | C2·M1 | NFR-SEC-018 | NFR-REL-009 | Không | — |
| FR-GRID-005 | C2·M2 | NFR-SEC-010 | NFR-REL-007, NFR-REL-009, NFR-PERF-006 | Không | — |
| FR-GRID-006 | C2·M1 | NFR-SEC-009 | NFR-REL-007 | Không | — |
| FR-GRID-009 | C2·M2 (P1) | NFR-SEC-008 | — | Không quy định hành vi khi dữ liệu lũy kế E_exp/E_pv thiếu hoặc cũ (đề xuất: giữ giới hạn bảo thủ) | 08, 10, 04 |
| FR-GRID-013 | C2·M2 (P1) | NFR-SEC-032 (đề xuất) | — (10 §13.2 có, 04 không) | NFR an toàn chưa chính thức; thiếu NFR-REL khi mất liên kết IEC 104 | 04, 10 (GAP-12-01, GAP-12-03) |
| FR-GRID-018 | C2·M2 (P2) | — | — | Không có NFR | 10 (P2) |
| FR-GRID-019 | C2·M2 (P2) | — | — | Không có NFR | 10 (P2) |
| FR-EV-003 | C1·M2 (P1) | NFR-SEC-021 | — | Không có NFR-REL khi charger/CSMS mất kết nối (chỉ có AC-EV-03) | 10, 04 |
| FR-EV-004 | C1·M2 (P1) | — | — | **Đã xử lý vòng nhất quán:** 04 FR-EV-004 + 07 §8.10 + 10 §5.4/§9.6/§13.2 buộc edge là client, envelope ký, TTL, readback, fallback (CF-39) | Đóng phần FR-EV-004 của GAP-12-02; bật ghi còn chờ ADR + driver CPO `VERIFIED_*` |
| FR-EV-005 | C1·M2 (P1) | NFR-SEC-021, NFR-SEC-011 | — | Như FR-EV-003 | 10, 04 |
| FR-EV-006 | C1·M2 (P1) | NFR-SEC-009 (`ev_site_cap_w`) | NFR-REL-007 chỉ nói BESS/PV | NFR-REL-007 cần thêm EV: mất `MTR_POC` → EV về `I_min` hoặc TxDefaultProfile | 04 |
| FR-EV-007 | C1·M2 (P1) | NFR-SEC-021 | — | Như FR-EV-006 | 04 |
| FR-EV-010 | C1·M2 (P2) | — | — | Không có NFR | 10 (P2) |
| FR-OPT-001 | C1·M2 | NFR-SEC-010 | NFR-REL-001, NFR-PERF-006 | Không | — |
| FR-OPT-003 | C3·M1 | NFR-SEC-008 | — | Không | — |
| FR-OPT-004 | C1·M2 | NFR-SEC-009 | NFR-REL-003, NFR-REL-007, NFR-PERF-006 | Không | — |
| FR-OPT-005 | C1·M1 | NFR-SEC-011 (lịch ≤ 7 ngày) | NFR-REL-001 | Không | — |
| FR-OPT-006 | C1·M1 | — | NFR-REL-001 | Không | — |
| FR-OPT-007 | C1·M1 | NFR-SEC-004, NFR-SEC-011 | NFR-REL-012 | Không | — |
| FR-OPT-012 | C2·M2 (P1) | NFR-SEC-008 | NFR-REL-001 | Không | — |
| FR-OPT-014 | C1·M2 (P1) | — | — | Không có NFR khi solver lỗi/quá thời gian (đề xuất: tự quay về plan tầng 2, cảnh báo) | 08, 04 |
| FR-OPT-017 | C1·M2 (P1) | NFR-SEC-009 | NFR-REL-007 | Thiếu hành vi khi cửa sổ demand thiếu dữ liệu (đề xuất: mục tiêu bảo thủ) | 08 |
| FR-OPT-018 | C1·M2 (P1) | NFR-SEC-008 | — | Như FR-GRID-009 | 08, 10 |
| FR-OPT-019 | C1·M1 (P1) | NFR-SEC-009 | — | Nguồn cảnh báo thời tiết bên ngoài chưa được xác thực. FR đã yêu cầu người dùng xác nhận, đủ cho P1; không tính là khoảng trống | 10 ghi nhận |
| FR-OPT-020 | C2·M2 (P2) | — | — | Không có NFR (khóa liên động với ATS/controller native) | 10 (P2) |
| FR-OPT-021 | C1·M2 (P2) | NFR-SEC-012 | — | Không có NFR xác thực và hạn của sự kiện DR | 10 (P2) |
| FR-INT-007 | C1·M1 | NFR-SEC-004 | NFR-REL-002 | Không | — |
| FR-INT-012 | C3·M1 | NFR-SEC-020, NFR-SEC-008 (duyệt C3), NFR-SEC-031 | NFR-REL-014 | Không (04 đã xác nhận) | — |
| FR-INT-016 | C1·M1 | NFR-SEC-033 (qua FR-INT-031) | NFR-SEC-033 (`REVERT_DEFAULT` khi thoát phiên) | Đã đóng ở 04 bản mới. Còn: 03 cấp F- riêng cho `COMMISSIONING_TEST` | 03 (GAP-12-15) |
| FR-INT-017 | C2·M1 | NFR-SEC-033 | NFR-REL-009, NFR-SEC-033 | Như FR-INT-016 | 03 |
| FR-INT-018 | C2·M2 | NFR-SEC-033 | NFR-REL-002, NFR-SEC-033 | Như FR-INT-016 | 03 |
| FR-INT-031 | C2·M1 | NFR-SEC-033, NFR-SEC-011 | NFR-SEC-033 | Không | — |
| FR-INT-023 | C2·M2 (P1) | NFR-SEC-032 (đề xuất) | — | Như FR-GRID-013 | GAP-12-01, GAP-12-03 |
| FR-INT-028 | C2·M1 (P2) | NFR-SEC-018 | — | **Đã xử lý vòng nhất quán:** FR-INT-028 viết lại theo 6 điều kiện CF-39; 07 §8.8 | Đóng GAP-12-02 (site không edge vẫn cấm tới khi Evidence Judge chấp nhận ngoại lệ) |
| FR-INT-030 | C1·M2 (P2) | NFR-SEC-006, NFR-SEC-012, NFR-OBS-006 | NFR-REL-015 (đề xuất) | Không | — |
| FR-SEC-005 | C3·M1 | NFR-SEC-002, NFR-SEC-008, NFR-SEC-009 (bật `control_enabled` cần SOE tối thiểu) | NFR-REL-015 | Không (04 đã xác nhận) | — |
| FR-SEC-006, FR-SEC-007 | C3·M1 (CF-28/D-03) | NFR-SEC-008 | NFR-REL-015 | Không ở 04. 11 §6.3 chưa có NFR-SEC-008 trong danh sách NFR Phase 1 (§6.4.1) | 11 |
| FR-SEC-010 | C1·M2 | NFR-SEC-010, NFR-SEC-014 | NFR-REL-003 | Không | — |
| FR-SEC-012 | C1·M2 | NFR-SEC-012 | — | Không | — |
| FR-SEC-013 | C1 kích hoạt / C3 gỡ·M1 | NFR-SEC-013 | NFR-REL-010, NFR-REL-018 | Không ở 04. 11 vẫn xếp kill switch ở Phase 2 (§6.4.1) | 11 |
| FR-SEC-021 | C3·M2 | NFR-SEC-030 (đề xuất) | NFR-REL-017 (đề xuất) | Điều kiện M2 dựa trên mã chưa chính thức | GAP-12-01 |

Tổng: 21 FR điều khiển có khoảng trống riêng: FR-BESS-016, FR-BESS-018, FR-BESS-019, FR-PV-013, FR-GRID-009, FR-GRID-013, FR-GRID-018, FR-GRID-019, FR-EV-003, FR-EV-004, FR-EV-005, FR-EV-006, FR-EV-007, FR-EV-010, FR-OPT-014, FR-OPT-017, FR-OPT-018, FR-OPT-020, FR-OPT-021, FR-INT-023, FR-INT-028. Không FR nào là P0. FR-INT-016…018 không còn là khoảng trống sau FR-INT-031 và NFR-SEC-033 của 04 bản mới. Nhãn "(đề xuất)" còn lại trong bảng là mã 10 đề xuất mà 04 bản mới đã xác nhận cùng số.

#### 6.4.1 FR Gate M1 dựa vào NFR từng gắn Gate M2

M1 đã phát lệnh C2/C3 (cấu hình lưới, OTA, cờ chủ vòng, `control_enabled`, lịch native). Các FR dưới đây là Gate M1 nhưng dựa vào NFR mà bản trước của 12 §4.1 và danh sách NFR Phase 1 của [11 §6.3](11-mvp-and-roadmap.html#s6) gắn Gate M2. 04 bản mới đã đưa NFR-SEC-008, NFR-SEC-013 về M1 và tách NFR-SEC-009 thành "tối thiểu ở M1, đầy đủ ở M2". 12 đã cập nhật §4.1 và cổng §2.3 theo 04. Khoảng trống còn lại nằm ở 11. `[INFERENCE]`

| FR (Gate M1) | Thao tác M1 | NFR cần | Gate của NFR ở 04 bản mới | 11 §6.3 (NFR Phase 1) | Khoảng trống |
|---|---|---|---|---|---|
| FR-SEC-006, FR-SEC-007 | Phân hạng, duyệt C3 | NFR-SEC-008 | M1 | Không có (NFR-SEC-008 ở §7.2, Phase 2) | 11 thêm NFR-SEC-008 vào Phase 1 |
| FR-GRID-003 | Cấu hình lưới C3 | NFR-SEC-008, NFR-SEC-009 (tối thiểu) | M1 | Không có | Như trên |
| FR-INT-012 | OTA edge C3 | NFR-SEC-008 | M1 | Không có | Như trên |
| FR-SEC-005 | Bật `control_enabled` C3 | NFR-SEC-008, NFR-SEC-009 (tối thiểu) | M1 | Không có | Như trên |
| FR-OPT-003 | Cờ chủ vòng C3 | NFR-SEC-008 | M1 | Không có | Như trên |
| FR-BESS-004 | Đổi chế độ native C1/C2 (cần phân hạng) | NFR-SEC-008 | M1 | Không có | Như trên |
| FR-BESS-006, FR-GRID-006 | Dự phòng SOC, trần nhập native | NFR-SEC-009 (tối thiểu) | M1 (tối thiểu) | Không có | 11 thêm NFR-SEC-009 (phần tối thiểu) và FR-BESS-020 vào Phase 1 |
| FR-BESS-020 | SOE tối thiểu | NFR-SEC-008, NFR-SEC-009 | M1 | FR chưa có ở 11 | Như trên |
| FR-SEC-013 | Kill switch | NFR-SEC-013, NFR-REL-010 | M1 | Không có; 11 §7.2 xếp FR-SEC-013 vào Phase 2 | 11 chuyển FR-SEC-013, NFR-SEC-013, NFR-REL-010 sang Phase 1 |

Đếm: 11 FR. Nếu 11 giữ nguyên, G1 sẽ phát hành lệnh C3 mà không có cổng kiểm thử duyệt hai người và kill switch. 12 §2.3 đã đưa các test đó vào Gate MVP/G1 bất kể 11.

### 6.5 Thực thể

**Thực thể 05 không FR nào dùng (GAP-12-14):**

| Thực thể | Lý do | Sửa | Chủ |
|---|---|---|---|
| `AssetHealthStatus` | 05 §18 định nghĩa KPI "sức khỏe thiết bị" theo quy tắc. 03 §6 và 04 chưa có F-/FR tương ứng (_catalog-gaps, Agent F) | Thêm F- (03) và FR P0 cho FR-DASH-006 hoặc FR-MON-006 (04); hoặc 05 hạ xuống P1 nếu 11 không đưa vào MVP | 03, 04 |

**Thực thể chỉ một FR dùng (để ý khi đổi mô hình, không phải lỗi):** Portfolio, Role, Permission, RolePermission, DriverDefinition, LateLanding, DataCorrection, Tariff, TouCalendar, TouRule, ShadowBillLine, OptimizationStrategy, PlanSlotResult, FleetDispatchPolicy, ConsentRecord, M2ReadinessCheck, ReportSchedule.

**Thực thể FR cần nhưng 05 chưa có (GAP-12-13).** Trường tối thiểu là `[PROPOSAL]` của 12. 05 quyết định tên và cấu trúc cuối.

| Thực thể đề xuất | FR | Trường tối thiểu đề xuất | Ưu tiên |
|---|---|---|---|
| `OnCallContact` / lịch trực | FR-ALM-006 (P0), FR-ALM-015 | `site_id`, `user_id`, `valid_from/to`, kênh, thứ tự | **P0** |
| `OtaCampaign` | FR-INT-012 (P0) | bản phát hành, ký số, nhóm canary %, trạng thái, lý do dừng, `edge_ids` | **P0** |
| `SiteTemplate` | FR-ORG-012 | `org_id`, topology, payload có phiên bản, SOE luôn `DRAFT` khi áp | P1 |
| `SiteDocument` | FR-ORG-014 | `site_id`/`asset_id`, loại, phiên bản, lớp D2, `uri`, `content_hash` | P1 |
| `SavedView` (hoặc `UserPreference`) | FR-DASH-012; tùy chọn hiển thị (GAP-12-12) | `user_id`, phạm vi, bộ lọc jsonb, cột, chia sẻ | P1 |
| `UtilityBill` | FR-TAR-011 | `site_id`, `billing_period_id`, kWh theo khung, công suất, tiền (VND), tệp gốc | P1 |
| `EscalationPolicy` | FR-ALM-015 | mức, độ trễ phút, đích theo cấp | P1 |
| `SlaPolicy` | FR-ALM-017 | mức cảnh báo, thời gian phản hồi/khắc phục, loại trừ | P1 |
| `WebhookSubscription`, `WebhookDelivery` | FR-INT-026 | đích, sự kiện, bí mật HMAC (chỉ ghi), trạng thái gửi, số lần thử | P1 |
| `ImportJob` | FR-INT-027 | nguồn, `file_hash`, số dòng, origin `IMPORTED`, trạng thái | P1 |
| `RemoteSupportSession` | FR-SEC-024 | `edge_id`, người yêu cầu, người duyệt, bắt đầu/kết thúc (≤ 2 h), bản ghi phiên | P1 |
| `SimulationRun` | FR-ADV-006 | tham số kịch bản, `tariff_version_ids`, `result_hash`, nhãn "Mô phỏng" | P1 |
| `PriceSeries` | FR-TAR-012, FR-ADV-012 | nguồn, `bucket_start`, `price_vnd_per_kwh`, phiên bản | P2 |
| `FlexibilityOffer` | FR-OPT-021 | `site_id`, slot, `up_kw`, `down_kw`, trạng thái, hạn | P2 |
| `ProductionSchedule` | FR-ADV-007 | `site_id`, ngày, ca, nguồn (tay/MES) | P2 |

Thêm từ _catalog-gaps (không có FR, cần sau khi 03/04 bổ sung): `ForensicBundle` (API-AUD-04), `Incident` (NFR-SEC-029), `CommissioningTest` envelope (FR-INT-016…018).

### 6.6 API

**API không có người dùng.** Không có. Mọi API trong 06 §13.2 được ít nhất một FR dùng (§5).

**API mới cho thực thể P1/P0 của 05 (X-05-09, vòng nhất quán 2026-10-10).** So 05 §21.1 với 06 §13.2, các thực thể sau chưa có endpoint và nay đã được 06 cấp mã:

| Thực thể (05) | API mới (06) | FR / NFR | Test |
|---|---|---|---|
| `OnCallContact` (P0) | API-ALM-11 | FR-ALM-006, FR-ALM-015 | T-FR-ALM-006 (CRUD + hiển thị ở chi tiết cảnh báo) |
| `EscalationPolicy` | API-ALM-12 | FR-ALM-015 | T-FR-ALM-015 |
| `SlaPolicy` | API-ALM-13 | FR-ALM-017 | T-FR-ALM-017 |
| `SiteTemplate` | API-ORG-13 | FR-ORG-012 | T-FR-ORG-012 (SOE từ mẫu luôn `DRAFT`) |
| `SiteDocument` | API-ORG-14 | FR-ORG-014 | T-FR-ORG-014 (URL ký ngắn hạn, cross-tenant) |
| `SavedView`, `UserPreference` | API-ORG-15 | FR-DASH-012; F-ORG-18 (chưa có FR) | T-FR-DASH-012 |
| `RemoteSupportSession` | API-INT-11 | FR-SEC-024, NFR-SEC-022 | T-FR-SEC-024, T-NFR-SEC-022 |
| `SimulationRun` | API-OPT-10 | FR-ADV-006 | T-FR-ADV-006 (nhãn "Mô phỏng") |
| `Incident` | API-AUD-05 | NFR-SEC-029; F-SEC-27 (chưa có FR) | T-NFR-SEC-029 |
| `EvSession`, trụ sạc | API-EV-01…04 | FR-EV-002, 003, 004, 008 | T-FR-EV-002, T-FR-EV-004 |

`PriceSeries`, `FlexibilityOffer`, `ProductionSchedule` (P2) vẫn chưa có API, chủ ý.

**API không có FR riêng (GAP-12-15):**

- API-AUD-04 (gói bằng chứng sự cố, MVP) và API-AUD-05 (sổ sự cố): nay có F-SEC-26/F-SEC-27 ở 03 và NFR-OBS-009/NFR-SEC-029 ở 04, nhưng chưa có FR riêng. Trước đây: ánh xạ về F-SEC-12 nhưng FR-SEC-014 (audit) không yêu cầu bundle. Hệ quả: một endpoint MVP không có yêu cầu và không có test nghiệm thu. Sửa: 03 cấp F-, 04 cấp FR. Nếu chưa làm thì 06 hạ API-AUD-04 xuống "chờ yêu cầu".
- API-CMD-11 (hồ sơ M2): có FR-SEC-021 nhưng 03 chưa có F- riêng. Chỉ cần 03 cập nhật.

**API không có trang UI dùng (đúng thiết kế):** API-PUB-04 (hạng 03: Phase 2; lộ trình Phase 4, 4D; bên thứ ba), API-INT-02 (edge gọi), API-PUB-02 và API-PUB-03 (bên thứ ba; UI-32 chỉ quản lý client), API-AUTH-04 (vé SSE, hạ tầng).

**FR thiếu endpoint (41 FR ở bản dựng ban đầu, nay còn 30; GAP-12-04…06).** Các dòng ghi "Đã có" là phần đã xử lý ở vòng nhất quán.

| Nhóm | FR | Ưu tiên | Đề xuất cho 06 |
|---|---|---|---|
| Thông báo in-app | FR-ALM-008 | **P0** | `GET /api/v1/notifications`, `POST /api/v1/notifications/{id}/read`; luồng mới qua API-LIVE-03 hoặc luồng riêng |
| Dự báo | FR-ADV-001 | **P0** | UI-19 cần dự báo PV/tải có nhãn phương pháp. Thêm trường `forecast` (p10/p50/p90, `method_label`) vào API-OPT-03 hoặc nhóm `API-FC` |
| EV | FR-EV-009, FR-EV-010 | P2 | **Đã có nhóm API-EV-01…04 (vòng nhất quán)** cho FR-EV-002, 003, 004, 008; `SET_EV_LIMIT` đã ghi ở API-CMD-01. Còn: dự báo phiên (FR-EV-009), OCPP 2.x/V2X (FR-EV-010) |
| Dự báo và mô phỏng nâng cao | FR-ADV-003…FR-ADV-012 | P1/P2 | Nhóm API-FC (dự báo, đánh giá) và API-SIM (what-if, nhãn "Mô phỏng") |
| Lưới | FR-GRID-009, FR-GRID-010, FR-GRID-011, FR-REP-015 | P1 | Endpoint ngân sách xuất và đồng hồ demand (đọc), có thể mở rộng API-TEL-06 và API-LIVE-01 |
| Lệnh P2 | FR-PV-013, FR-GRID-018, FR-GRID-019, FR-OPT-020, FR-OPT-021, FR-INT-028 | P2 | Thêm `type` vào API-CMD-01 khi track lộ trình Phase 4 tương ứng (4A, 4D, 4H) được bật; DR/VPP cần nhóm riêng |
| O&M | FR-ALM-020 | P1 | **Đã có** API-ALM-11 (trực ca), API-ALM-12 (leo thang), API-ALM-13 (SLA) cho FR-ALM-006/015/017. Còn: nhận cập nhật từ CMMS (inbound) |
| Dữ liệu chủ | FR-ORG-016 | P1 | **Đã có** API-ORG-13 (mẫu site), API-ORG-14 (tài liệu), API-ORG-15 (view đã lưu, tùy chọn) cho FR-ORG-012, FR-ORG-014, FR-DASH-012. Còn: hợp đồng (FR-ORG-016) |
| Khác | FR-MON-013 (yêu cầu burst), FR-REP-018 (mẫu báo cáo PPA trong API-REP-01), FR-TAR-012 (chuỗi giá), FR-BESS-017 (sổ cái pin), FR-OPT-013 (shadow price trong API-OPT-03), FR-SEC-024 (tunnel hỗ trợ — **đã có API-INT-11**) | P1/P2 | Như mô tả; what-if FR-ADV-006 đã có API-OPT-10 |

**Cột "Tính năng" của 06 chưa đủ (GAP-12-07).** 88 FR dùng một API mà cột "Tính năng" của API đó không ghi F- của FR (ký hiệu `+API` trong §3). Phần lớn là API đọc dùng chung (API-TEL-02/03/05/06, API-ALM-01) và không cần liệt kê hết. Những chỗ cần sửa vì ảnh hưởng đến hợp đồng lệnh:

- API-CMD-01 phải liệt kê đủ `type` và F-: `SET_ESS_MODE` (F-BESS-04), `SET_EV_LIMIT` (F-EV-05), `DEVICE_ON_OFF` (F-BESS-16), reset lỗi (F-BESS-17), quét I-V (F-PV-10), `COMMISSIONING_TEST` (catalog gap), `SET_Q`/`SET_PF` (F-PV-13, P2). Hạng tối thiểu từng `type` phải khớp 04.
- API-CMD-04 (dry run) dùng cho validator kế hoạch (FR-OPT-008) và PDP (FR-SEC-016). 06 nên ghi thêm F-OPT-07, F-SEC-15.
- API-ORG-02 mang thuộc tính gói/cờ tính năng (FR-ORG-011, F-ORG-15).

**09 không trích mã API (GAP-12-08).** Bảng §5 là bản suy ra. 09 nên thêm cột API vào §13.1 hoặc vào khối "Thông tin chính" của từng trang.

### 6.7 Kiểm thử

- **AC → T.** 107/107 AC của 04 có trong ít nhất một `T-`. Hai AC trước đây chưa có chỗ rõ ràng đã được gắn: AC-GRID-04 → T-FR-GRID-006, AC-SEC-04 → T-FR-SEC-008.
- **FR P0 không có AC và không có ca ở 07/08/10 (47):** FR-ORG-001, FR-ORG-003, FR-ORG-005, FR-ORG-007, FR-ORG-011, FR-DASH-003, FR-DASH-005, FR-MON-001, FR-MON-002, FR-MON-006, FR-MON-007, FR-MON-010, FR-HIST-001, FR-HIST-003, FR-HIST-009, FR-HIST-010, FR-HIST-011, FR-REP-004, FR-TAR-004, FR-TAR-005, FR-BESS-001, FR-BESS-002, FR-BESS-006, FR-PV-001, FR-GRID-002, FR-GRID-007, FR-GRID-008, FR-OPT-008, FR-OPT-009, FR-OPT-010, FR-ALM-001, FR-ALM-006, FR-ALM-007, FR-INT-001, FR-INT-013, FR-INT-014, FR-INT-015, FR-INT-019, FR-SEC-001, FR-SEC-006, FR-SEC-011, FR-SEC-015, FR-SEC-017, FR-SEC-018, FR-SEC-019, FR-SEC-020, FR-SEC-022. Kịch bản của chúng chỉ có ở §3, là `[PROPOSAL]` của 12. 04 nên viết AC Given/When/Then, trước hết cho 7 FR liên quan an toàn: **FR-BESS-006, FR-OPT-008, FR-SEC-006, FR-SEC-022, FR-INT-001, FR-GRID-002, FR-GRID-008** (GAP-12-16).
- **Phân bố loại test của FR:** 85 Đơn vị, 73 Tích hợp, 52 Mô phỏng, 24 HIL, 32 E2E (§1). Mỗi FR chỉ ghi loại test chính. Ca con có thể dùng loại khác, ví dụ T-FR-BESS-005 có cả Mô phỏng và HIL.
- **HIL phụ thuộc lab chưa có.** 24 FR có test HIL chính, trong đó 14 là P0. 11 đã đưa lab L5 vào Phase 0 và trước G1 ([11 §5.7, §6.8](11-mvp-and-roadmap.html#s5)). Chi phí và nguồn mua vẫn UNKNOWN (07 §11.4, Q-E-15).
- **Test phụ thuộc pháp lý UNKNOWN (GAP-12-20).** T-FR-REP-015, T-FR-GRID-009, T-FR-TAR-008, T-FR-TAR-002 (ngày lễ), T-FR-TAR-001 (giá QĐ 1279) phải nhận tham số. Bộ dữ liệu vàng ghi rõ "giá trị mẫu, chưa kiểm chứng pháp lý" cho tới khi lượt kiểm chứng G-13 xong.

### 6.8 Mã và nhất quán giữa tài liệu

| Vấn đề | Chi tiết | Sửa (chủ) |
|---|---|---|
| NFR mã đề xuất được trích như mã chính thức | 06 §20 và §16 trích NFR-REL-015/016/017/018, NFR-SEC-027/030, NFR-OBS-008/009 của 10 trước khi 04 xác nhận. 04 bản mới đã xác nhận cùng số → không còn xung đột | Đã đóng |
| Mã test của 08 | `T1-01…T1-07` không theo `T-<FR id>` | 08 đổi theo ánh xạ §2.2 (GAP-12-17) |
| Đường lệnh không qua edge | FR-EV-004 (API CPO), FR-INT-028 (cloud hãng) — đã buộc đi qua edge theo CF-39 (vòng nhất quán) | GAP-12-02 đóng |
| Trang ghi FR bị cấm | UI-07 ghi FR-BESS-011. Hợp lệ vì nghĩa là "trang không có nút". 09 nên ghi chú để người đọc không hiểu là trang cung cấp chức năng | 09 (nhỏ) |
| Phát hành API trước yêu cầu | API-AUD-04 là MVP nhưng không có FR | GAP-12-15 |
| Tài liệu tham chiếu chưa có | 11, 13, 14, 15 đã có. `00-executive-summary.html`, `index.html` và `README.md` đã được viết ở vòng hợp nhất (2026-10-10); liên kết điều hướng không còn hỏng. §4.1 nay đủ 85 NFR (vòng nhất quán) | Đã đóng |
| Số FR P0 lớn | 148 FR P0 cho MVP. 11 §6.2 đã chia Phase 1 thành milestone 1a/1b/1c; 12 chưa gắn milestone theo FR vì 11 chỉ liệt kê theo nhóm | 11 nếu cần cột milestone (GAP-12-18) |
| 11 lệch với 04 bản mới | 11 (bản 07:15) chưa có FR-BESS-020, FR-INT-031; xếp FR-SEC-013 ở Phase 2; danh sách NFR Phase 1 (§6.3) thiếu NFR-SEC-008, 009 (tối thiểu), 013, NFR-REL-010. 12 xếp theo 04 và đánh dấu `⚠` (§0.3, §6.4.1) | 11 (GAP-12-18) |
| 12 chưa đối chiếu hết 04 bản mới | **Đã xử lý vòng nhất quán:** 15 NFR 04 xác nhận đã vào §4.1 với ưu tiên/Gate của 04; §4.2 chỉ còn ghi chú lịch sử | GAP-12-01 đóng phần 12 |

---

## 7. Sổ khoảng trống GAP-12

Mã `GAP-12-NN` là mã cục bộ của tài liệu này. 13 cấp mã `R-NN`/`Q-NN` chính thức nếu cần. "Chặn" nghĩa là phải xử lý trước cổng nêu.

| Mã | Loại | Mô tả | Đề xuất sửa | Tài liệu chủ | Ưu tiên · Chặn |
|---|---|---|---|---|---|
| GAP-12-01 | NFR | 14 NFR mã đề xuất của 10 chưa được 04 xác nhận; 06 đã trích 7 mã; điều kiện M2 dựa vào NFR-REL-015, NFR-REL-017, NFR-SEC-028, NFR-SEC-030 | Đã xử lý ở 04 bản mới (xác nhận cùng số, thêm NFR-SEC-033). Còn: 12 đối chiếu lại §4.2 và cột Gate §4.1 với 04 §6 và 10 §20 (10 X-10-14 đã chuyển NFR-SEC-008, 013, 028, NFR-REL-010 về M1, tách NFR-SEC-012 thành M1 đếm / M2 ΔP; vòng này 12 mới cập nhật NFR-SEC-008, 009, 013, NFR-REL-010) | 12 | Trung bình · trước phát hành 12 |
| GAP-12-02 | An toàn/kiến trúc | FR-EV-004 và FR-INT-028 ghi lệnh không qua edge của ta | Hoặc buộc đi qua edge (edge gọi API CPO/cloud hãng với envelope ký và hạn), hoặc ghi ngoại lệ có lý do được Evidence Judge chấp nhận; nếu không thì bỏ FR | 04, 10, 07; Evidence Judge | Cao · trước lộ trình Phase 3 track 3E (EV), Phase 4 track 4D (cloud hãng) |
| GAP-12-03 | NFR điều khiển | Phần `COMMISSIONING_TEST` đã đóng (04 bản mới: FR-INT-031, NFR-SEC-033). Còn thiếu NFR riêng: một PCS mất liên lạc, trạng thái PCS đã dừng, EV khi mất kết nối/`MTR_POC`, liên kết IEC 104 mất, solver tầng 3 lỗi, dữ liệu ngân sách xuất/demand cũ, trực ca 24/7 trước M2 với FR leo thang là P1, các lệnh P2 | 10 soạn đặc tả; 04 cấp mã; 03 thêm F- riêng cho `COMMISSIONING_TEST`. FR-ALM-015 (leo thang) đã ở lộ trình Phase 2 cùng V4 trực ca (11 §7.2, §7.5); cần xác nhận có trước G2a | 10, 04, 03, 11 | Trung bình · G2a |
| GAP-12-04 | API P0 | FR-ALM-008 (thông báo in-app) và FR-ADV-001 (dự báo cho UI-19) không có endpoint | **Đã đóng vòng sửa (2026-10-10):** 06 thêm API-ALM-09/10, API-LIVE-06 (thông báo) và API-FC-01 (dự báo), `include=forecast` ở API-OPT-03 | 06 | Cao · Gate MVP |
| GAP-12-05 | API EV | Không có nhóm API-EV | Thêm nhóm API-EV | 06 | Trung bình · lộ trình Phase 3 (3E) |
| GAP-12-06 | API khác | 33 FR P1/P2 khác thiếu endpoint (§6.6) | Bổ sung theo Phase | 06 | Trung bình/Thấp |
| GAP-12-07 | Truy vết API | Cột "Tính năng" của 06 thiếu F-; danh sách `type` của API-CMD-01 chưa đủ | Sửa như §6.6 | 06 | Trung bình · Gate M1 (hợp đồng lệnh) |
| GAP-12-08 | Truy vết UI↔API | 09 không trích API | **Đã đóng vòng sửa (2026-10-10):** 09 §13.1 có cột "API (06, qua 12 §5)" cho 37 trang | 09 | Thấp |
| GAP-12-09 | Truy vết UI | 31 FR có chỗ trên trang nhưng 09 §13.1 chưa ghi | **Đã đóng vòng sửa (2026-10-10):** 09 §13.1 ghi mọi mục §6.1(b) sau dấu "+"; trang có thêm nội dung bổ sung | 09 | Trung bình |
| GAP-12-10 | Thiếu trang | 11 FR P1 không có trang | **Đã đóng vòng sửa (2026-10-10):** 09 cấp tab cho 8 FR và trang mới UI-37 "Dự báo và mô phỏng" cho FR-ADV-004/005/006 (09 nay 37 trang) | 09 | Trung bình |
| GAP-12-11 | Truy vết ngược | 12 trang ghi F- nhưng thiếu FR tương ứng | **Đã đóng vòng sửa (2026-10-10):** 09 §13.1 bổ sung FR tương ứng | 09 | Thấp |
| GAP-12-12 | Nội dung không FR | Tùy chọn hiển thị, trang phương pháp/thuật ngữ, mã xác nhận có mặt cho lệnh thử | 03 cấp F-, 04 cấp FR (MVP cho ngôn ngữ/giao diện và trang phương pháp vì FR-REP-008 cần) | 03, 04 | Trung bình · Gate MVP (trang phương pháp) |
| GAP-12-13 | Thực thể | 15 thực thể FR cần nhưng 05 chưa có; 2 phục vụ FR P0 (`OnCallContact`, `OtaCampaign`) | **Đã đóng vòng sửa (2026-10-10):** 05 thêm `OnCallContact`, `OtaCampaign`, `ForensicBundle`, `Incident` và các thực thể P1/P2, truy vết ở 05 §21.1. Còn: endpoint cho các thực thể này (X-05-09, GAP-12-06) | 05 | Cao cho 2 thực thể P0; Trung bình còn lại |
| GAP-12-14 | Thực thể thừa | `AssetHealthStatus` không có F-/FR | 03/04 thêm F-/FR hoặc 05 hạ xuống P1 | 03, 04, 05 | Thấp |
| GAP-12-15 | Tính năng chưa vào catalog | 18 mục ở _catalog-gaps chưa có F- (§6.3); API-AUD-04 phát hành MVP không có FR; NFR-SEC-029 cần sổ sự cố | 03 xử lý _catalog-gaps; 04 cấp FR | 03, 04 (06 điều chỉnh phát hành) | Cao (bundle, M2, `COMMISSIONING_TEST`); Trung bình còn lại |
| GAP-12-16 | AC | 47 FR P0 chưa có AC; 7 liên quan an toàn | 04 viết AC, ưu tiên 7 FR an toàn | 04 | Trung bình · Gate MVP |
| GAP-12-17 | Mã test | 08 dùng `T1-NN` | **Đã đóng vòng sửa (2026-10-10):** 08 §5.8 dùng mã §2.2, giữ cột mã cũ | 08 | Thấp |
| GAP-12-18 | Phát hành | Đã xử lý phần lớn: 11 có ánh xạ hạng → lộ trình (§2.3), milestone 1a/1b/1c (§6.2), lab L5 trước G1 (§5.7, §6.8); 12 thêm cột "Lộ trình (11)". Còn: 11 chưa theo 04 bản mới (FR-BESS-020, FR-INT-031, FR-SEC-013 và NFR-SEC-008/009/013, NFR-REL-010 ở M1; §6.4.1); chi phí lab HIL UNKNOWN (Q-E-15) | 11 cập nhật §2.3, §6.3, §7.2 | 11 | Cao · G1 |
| GAP-12-19 | UI P2 | 16 FR P2 không có trang | Bổ sung khi track lộ trình Phase 4 tương ứng được bật | 09 | Thấp |
| GAP-12-20 | Pháp lý trong test | Test ngân sách xuất, giá hai thành phần, ngày lễ TOU, giá QĐ 1279 dựa trên tham số UNKNOWN | Tham số hóa; nhãn "giá trị mẫu"; cập nhật sau lượt kiểm chứng G-13 | 13 (ghi rủi ro), 04 | Trung bình · trước phát hành 04 |

---

## 8. Vấn đề gửi agent khác

| Gửi | Nội dung | GAP |
|---|---|---|
| 03 Chức năng | Xử lý 18 mục _catalog-gaps chưa có F-. Ưu tiên `COMMISSIONING_TEST`, hồ sơ M2, gói bằng chứng sự cố, trang phương pháp. Quyết định F- cho KPI sức khỏe thiết bị (`AssetHealthStatus`). | 12, 14, 15 |
| 04 Yêu cầu | (Đã làm ở bản mới: xác nhận 14 NFR mã đề xuất, NFR-SEC-033 cho lệnh thử commissioning, FR-SEC-006/007/013 về M1.) Còn: thêm NFR cho EV khi mất kết nối (mở rộng NFR-REL-007), IEC 104 mất liên kết, solver tầng 3 lỗi. Viết AC cho 47 FR P0 (7 an toàn trước). Làm rõ đường lệnh FR-EV-004, FR-INT-028. | 01, 02, 03, 16 |
| 05 Domain | Thêm 15 thực thể (§6.5), trước hết `OnCallContact`, `OtaCampaign`. Thêm giới hạn Q vào SOE trước khi FR-PV-013/FR-GRID-019 được lập lịch. | 13 |
| 06 Kiến trúc | Endpoint P0 cho thông báo in-app và dự báo. Nhóm API-EV. Bổ sung `type` của API-CMD-01. Cập nhật cột "Tính năng". Chỉ trích NFR mã đề xuất sau khi 04 xác nhận. Quyết định số phận API-AUD-04 nếu chưa có FR. | 01, 04, 05, 06, 07, 15 |
| 07 Tích hợp | Đường lệnh qua API CPO (FR-EV-004) phải đi qua edge hoặc được K chấp nhận như ngoại lệ. Hành vi charger khi mất kết nối thành NFR. | 02, 03 |
| 08 Tối ưu | Đổi `T1-NN` theo §2.2. Hành vi khi solver tầng 3 lỗi và khi dữ liệu ngân sách xuất/demand cũ. | 03, 17 |
| 09 UX/UI | Cập nhật §13.1 cho 33 FR (gồm FR-BESS-020, FR-INT-031) và 12 trang lệch truy vết. Thêm trang/tab cho 11 FR P1. Thêm cột API. Ghi chú UI-07 ↔ FR-BESS-011. | 08, 09, 10, 11 |
| 10 An toàn | Soạn đặc tả cho các NFR thiếu ở §6.4. Kiểm lại đường lệnh FR-EV-004 và FR-INT-028 với nguyên tắc "cloud không ghi trực tiếp". | 02, 03 |
| 11 Lộ trình | Theo 04 bản mới: thêm FR-BESS-020, FR-INT-031 vào Phase 1 (§2.3, §6.3, tổng 135 → 137); chuyển FR-SEC-013 từ §7.2 sang Phase 1 (Phase 1 = 138, nhóm "MVP, Gate M2" = 12); thêm NFR-SEC-008, NFR-SEC-009 (tối thiểu), NFR-SEC-013, NFR-REL-010 vào danh sách NFR Phase 1 (§6.3) và bộ test duyệt C3, hạn, replay, kill switch vào G1 (§6.6) như 12 §2.3. Xác nhận FR-ALM-015 có trước G2a. | 03, 18 |
| 13 Rủi ro | Ghi rủi ro: test phụ thuộc pháp lý UNKNOWN; lab HIL chưa có; đường lệnh không qua edge. | 02, 18, 20 |

---

## 9. Cách duy trì ma trận

`[PROPOSAL]`

1. **Một nguồn sự thật cho mỗi cột.** FR, F-, ưu tiên lấy từ 04; API từ 06 §13.2; UI từ 09 §13.1; thực thể từ 05. 12 không tự cấp FR, API hay UI mới. Đề xuất mới đi vào GAP-12.
2. **Kiểm tra tự động trong CI của repo tài liệu.** Một script đọc bảng của 04/06/09 và báo lỗi khi:
   - FR không có `T-` hoặc không có dòng ở 12;
   - FR P0 không có UI và không được đánh dấu backend;
   - API không có FR dùng;
   - mã FR/NFR/UI/API được trích nhưng không tồn tại;
   - FR điều khiển (hạng C1–C3) không có NFR an toàn và NFR khi lỗi.
   Tài liệu này được dựng bằng chính quy trình đó trên bản ngày 2026-10-10.
3. **Mã test trong mã nguồn.** Tên test hoặc annotation mang `T-<FR id>-NN`. Báo cáo CI nhóm kết quả theo FR, để cột Test của ma trận đối chiếu được với kết quả thật.
4. **Cập nhật khi đổi mã.** Khi 04 đổi hoặc tách FR, 12 giữ dòng cũ với ghi chú "thay bằng …" trong một phiên bản để không mất liên kết.
5. **Cổng phát hành.** Mỗi cổng ở §2.3 xuất một bảng "FR của cổng × kết quả `T-`" làm bằng chứng nghiệm thu.

---

## 10. Nguồn

Tài liệu này chỉ dùng tài liệu nội bộ của dự án. Không trích URL ngoài; bằng chứng ngoài của từng yêu cầu nằm ở tài liệu gốc.

- [03 Danh mục chức năng](03-functional-catalog.html): 270 F- (đã gồm 12 F- từ _catalog-gaps).
- [04 Yêu cầu nghiệp vụ](04-business-requirements.md): 268 FR (bản mới, gồm FR-BESS-020, FR-INT-031), 85 NFR (70 của bản dựng ban đầu + 15 mã bản mới), 107 AC, §5.16, §7.
- [11 MVP và lộ trình](11-mvp-and-roadmap.html): ánh xạ hạng → phase §2.3, phạm vi phase §6.3, §7.2, §8.2, §9.2, cổng G1/G2 §6.6, §7.6.
- [13 Câu hỏi mở và rủi ro](13-open-questions-and-risks.md): CF-28, CF-29, D-03.
- [05 Domain](05-domain-model.html): thực thể §4–§14, ánh xạ §21.
- [06 Kiến trúc](06-system-architecture.html): API §13.2, kiểm thử §16, truy vết §20.
- [07 Tích hợp](07-device-integration.md): kiểm thử §11.
- [08 Tối ưu](08-energy-optimization.md): kiểm thử tầng 1 §5.8.
- [09 UX/UI](09-ux-ui-specification.html): trang §5.5, truy vết §13.1–§13.2.
- [10 An toàn](10-security-and-reliability.md): kiểm thử §19, NFR §20.
- [notes/K-review-round1.md](notes/K-review-round1.md): quyết định thống nhất (§6), khoảng trống G-01…G-13.
- [notes/_catalog-gaps.md](notes/_catalog-gaps.md): tính năng chưa vào catalog.
- [notes/_conventions.md](notes/_conventions.md): quy ước mã và nhãn.
