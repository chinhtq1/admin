# 10 — An toàn vận hành, bảo mật và độ tin cậy

[← Mục lục](index.html) · [00 Tóm tắt](00-executive-summary.html) · [03 Chức năng](03-functional-catalog.html) · [04 Yêu cầu](04-business-requirements.md) · [05 Domain](05-domain-model.html) · [06 Kiến trúc](06-system-architecture.html) · [07 Tích hợp](07-device-integration.md) · [08 Tối ưu](08-energy-optimization.md) · [09 UX/UI](09-ux-ui-specification.html) · [11 Lộ trình](11-mvp-and-roadmap.html) · [12 Truy vết](12-traceability-matrix.md) · [13 Rủi ro](13-open-questions-and-risks.md) · [14 Nguồn](14-source-register.md) · [15 Mô phỏng](15-simulators-and-messaging.md)

| Thuộc tính | Giá trị |
|---|---|
| Tài liệu | 10 · An toàn vận hành, bảo mật và độ tin cậy (Security & Reliability) |
| Người viết | Agent I (Security & Reliability Reviewer) |
| Phiên bản | 1.0 |
| Ngày | 2026-10-10 |
| Trạng thái | Bản nháp vòng 1. Đã áp "Danh sách quyết định thống nhất" của Evidence Judge ([K-review-round1 §6](notes/K-review-round1.md)). **Chưa được phát hành ra ngoài đội**: phần pháp lý Việt Nam và edition tiêu chuẩn chưa kiểm chứng (K §5 G-13, §3.8). Xem [§21](#s21). |
| Đầu vào | [notes/I-security-reliability.md](notes/I-security-reliability.md) (ghi chú gốc), [notes/K-review-round1.md](notes/K-review-round1.md), [03](03-functional-catalog.html), [04](04-business-requirements.md), [05](05-domain-model.html), [07](07-device-integration.md), các ghi chú A/B/C/E/F/G/H, nghiên cứu FusionSolar trước ([../fusionsolar/04_ghi_chu_nghien_cuu/1_tong_quan/architecture_security.md](../fusionsolar/04_ghi_chu_nghien_cuu/1_tong_quan/architecture_security.md)) |

---

## Mục lục

- [0. Cách đọc tài liệu](#s0)
- [1. Tóm tắt quyết định](#s1)
- [2. Ranh giới an toàn: EMS làm gì, không làm gì](#s2)
- [3. Tiêu chuẩn và quy định](#s3)
- [4. Danh tính và xác thực người dùng](#s4)
- [5. Phân quyền: RBAC + phạm vi + PDP cho lệnh](#s5)
- [6. Cô lập tenant](#s6)
- [7. Nhật ký kiểm toán (audit trail)](#s7)
- [8. Quản lý bí mật, khóa và credential](#s8)
- [9. Danh tính thiết bị và kênh truyền an toàn](#s9)
- [10. Phân vùng OT/IT: zone và conduit](#s10)
- [11. Chuỗi an toàn lệnh](#s11)
- [12. Ưu tiên điều khiển tại chỗ và E-stop](#s12)
- [13. Hành vi khi mất liên lạc](#s13)
- [14. Giới hạn bán kính tác động ở cấp đội](#s14)
- [15. Mô hình mối đe dọa và ca lạm dụng](#s15)
- [16. Độ tin cậy: khả dụng, RPO/RTO, sao lưu/DR, chế độ suy giảm](#s16)
- [17. Quan sát hệ thống (observability) của chính nền tảng](#s17)
- [18. Quy trình điều tra sự cố](#s18)
- [19. Kế hoạch kiểm thử bảo mật và an toàn](#s19)
- [20. Danh mục yêu cầu NFR-SEC / NFR-REL / NFR-OBS](#s20)
- [21. Điều kiện phát hành, câu hỏi mở, rủi ro](#s21)
- [22. Vấn đề gửi agent khác](#s22)
- [23. Nguồn](#s23)

---

<a id="s0"></a>
## 0. Cách đọc tài liệu

### 0.1 Phạm vi

Tài liệu này đặc tả các yêu cầu an toàn vận hành, bảo mật và độ tin cậy cho nền tảng EMS C&I behind-the-meter, đa site, đa hãng (K §6 #1). Nền tảng gồm ba phần: **cloud** (Java/Spring Boot, Angular, PostgreSQL/TimescaleDB, MQTT broker), **edge gateway** đặt tại site (kiểu OpenEMS) và các **connector cloud của hãng** (chỉ đọc). Site chỉ có PV là công dân hạng nhất. BESS và sạc EV là tùy chọn (K §6 #2).

Khác với nền tảng giám sát PV trong nghiên cứu FusionSolar trước (chỉ đọc), EMS **ghi lệnh** xuống PCS, inverter, logger hãng và charger. Rủi ro chính vì thế chuyển từ "lộ dữ liệu" sang **"tác động vật lý"**: xả/sạc sai, phát ngược trái phép, quá tải MBA, hỏng pin, mất dự phòng cho tải quan trọng, và ở quy mô đội là tác động đồng thời lên lưới. [INFERENCE]

**Ngoài phạm vi:** an toàn điện/cháy nổ ở mức thiết bị (BMS, PCS, rơ-le, thiết kế lắp đặt, hệ PCCC), chứng nhận đấu nối của inverter/PCS, SCADA lưới của EVN, và code ứng dụng.

### 0.2 Mã định danh

| Mã | Ý nghĩa | Ghi chú |
|---|---|---|
| `NFR-SEC-001…026`, `NFR-REL-001…012`, `NFR-OBS-001…007` | Mã chính thức do [04 §6](04-business-requirements.md) cấp | Tài liệu này **dùng nguyên số** và đặc tả chi tiết. Không đổi nghĩa |
| `NFR-SEC-027…`, `NFR-REL-013…`, `NFR-OBS-008…` | Yêu cầu mới phát sinh khi đặc tả chi tiết | **Mã đề xuất của 10**, đánh số tiếp theo dãy của 04 để tránh trùng. Người viết 04 xác nhận hoặc đánh số lại (K §6 #38). Danh sách ở [§20](#s20), vấn đề gửi 04 ở [§22](#s22) |
| `FR-SEC-0NN`, `BR-SEC-0N`, `AC-SEC-NN` | Yêu cầu chức năng, quy tắc nghiệp vụ, tiêu chí chấp nhận của [04 §5.14](04-business-requirements.md) | Tham chiếu, không cấp mới |
| `F-<MODULE>-NN` | Tính năng trong [03](03-functional-catalog.html) | Dùng đúng mã của 03 |
| `C0…C4` | Hạng lệnh (K §6 #28) | C4 không có API |
| `IL-01…IL-10` | Interlock tại edge | Theo [04 §5.14](04-business-requirements.md), [07 §4.3](07-device-integration.md) |
| `Z0…Z8`, `CD-NN` | Zone và conduit ([§10](#s10)) | Cục bộ của 10 |
| `ABU-NN` | Ca lạm dụng (abuse case) ([§15.3](#s15)) | Cục bộ của 10. Ghi chú I dùng `AC-01…AC-10`; đổi sang `ABU-` để không trùng với tiêu chí chấp nhận `AC-<MODULE>-NN` của 04. Bảng ánh xạ ở §15.3 |
| `INC-` | Loại sự cố ([§18](#s18)) | Cục bộ |
| `T-NFR-…` | Ca kiểm thử ([§19](#s19)) | Theo quy ước `T-<id>`; ma trận ở [12](12-traceability-matrix.md) |
| `Q-I-NN`, `Q-10-NN`, `I-R-NN` | Câu hỏi mở, rủi ro ứng viên (mã tạm) | [13](13-open-questions-and-risks.md) cấp `Q-NN`, `R-NN` |

### 0.3 Nhãn bằng chứng và giới hạn

- `[FACT]` có URL; `[INFERENCE]` suy luận, nêu căn cứ; `[PROPOSAL]` đề xuất cho sản phẩm; `[UNKNOWN]` chưa đủ bằng chứng (quy ước [notes/_conventions.md](notes/_conventions.md)).
- **Giới hạn bằng chứng của lượt này.** Môi trường chặn tải trang trực tiếp. Hạn mức WebSearch chung của lượt chạy **đã hết** trước khi tài liệu này được viết; một truy vấn kiểm chứng (edition IEC 62443-3-3) bị từ chối. Vì vậy:
  - Mọi `[FACT]` dựa trên URL đã ghi trong ghi chú của các agent (phần lớn "qua kết quả tìm kiếm") hoặc nghiên cứu FusionSolar trước (ghi "(nghiên cứu FusionSolar trước)"). Không thêm URL mới.
  - Nội dung tiêu chuẩn (IEC 62443, NIST SP 800-82, IEC 62351, UL 9540…) và luật Việt Nam không có URL được ghi là **kiến thức nền chưa kiểm chứng**, nhãn `[INFERENCE]` hoặc `[UNKNOWN]`, edition `UNKNOWN`.
  - **Không tuyên bố tuân thủ** bất kỳ tiêu chuẩn nào (K §6 #34). Cụm từ dùng: "thiết kế theo tinh thần".
- Mọi số mặc định (ngưỡng, thời gian, tỷ lệ) là `[PROPOSAL]` trừ khi ghi khác. Số giống [04 §2](04-business-requirements.md) thì 04 là nguồn chuẩn.

### 0.4 Quy ước câu chữ

- "Phải" = bắt buộc, chặn nghiệm thu. "Nên" = khuyến nghị.
- "Edge" = gateway của ta tại site. "Native" = controller/logger/EMS/BMS/PCS của hãng thiết bị. "Cloud" = nền tảng SaaS của ta. "Cloud hãng" = cloud của nhà sản xuất thiết bị (FusionSolar, iSolarCloud…).
- Dấu và đơn vị theo K §6 #4–#6: lưới `+` = nhập, BESS `+` = xả; raw W/Wh, KPI/API kW/kWh; tên trường có hậu tố đơn vị.
- Nhãn mức cảnh báo: **Khẩn cấp / Cao / Trung bình / Thông tin** (K §6 #39).

---

<a id="s1"></a>
## 1. Tóm tắt quyết định

| # | Quyết định | Nhãn | Căn cứ | Yêu cầu |
|---|---|---|---|---|
| D-10-01 | **Cloud không nằm trong vòng bảo vệ và không ghi trực tiếp vào thiết bị.** Bảo vệ thiết bị (BMS, PCS, rơ-le, E-stop cứng) phải đúng **kể cả khi cloud và edge đều bị chiếm quyền**. Phần mềm chỉ đặt setpoint bên trong giới hạn native | [PROPOSAL] | K §6 #14 | NFR-SEC-001 |
| D-10-02 | **Cloud gửi ý định có hạn, edge quyết định.** Mọi lệnh có `expires_at`, chữ ký JWS, `seq` đơn điệu; edge kiểm lại toàn bộ, không tin cloud | [PROPOSAL] | K §6 #14, #21, R-11 | NFR-SEC-004, NFR-SEC-011 |
| D-10-03 | **Hai mặt phẳng** (monitoring/control) tách danh tính dịch vụ, credential, topic, quyền DB, namespace, quy trình release. Điều khiển **tắt mặc định** theo site | [PROPOSAL] | K §6 #26 | NFR-SEC-002 |
| D-10-04 | **Kiểm tra ở ba nơi**: cloud (quyền, PDP, SOE, Governor) → edge (chữ ký, hạn, `seq`, interlock, SOE đã ký) → thiết bị (giới hạn native, watchdog). Lớp sau không tin lớp trước | [PROPOSAL] | BR-SEC-05 | NFR-SEC-004, 009, 010 |
| D-10-05 | **Hạng lệnh C0–C4**, C3 hai người duyệt khác vai trò; C4 (thông số bảo vệ, E-stop, bỏ qua interlock) không có API | [PROPOSAL] | K §6 #28 | NFR-SEC-008 |
| D-10-06 | **Kill switch, C3 hai người, Governor biến thể đếm (trần site/5 phút, trần site mỗi lần chạy bộ sinh lịch), toàn vẹn thời gian edge và giới hạn tĩnh `M1StaticLimits` là P0 từ Gate M1** (site có `control_enabled`), vì M1 đã ghi tới nhiều site; Governor ΔP (20% MW BESS tenant / 5 phút, đề xuất cần mô phỏng) thêm ở Gate M2 | [PROPOSAL] | K §6 #30; 13 CF-28/D-03 | NFR-SEC-008, 009, 012, 013, 028 |
| D-10-07 | **Fail-safe về trạng thái định trước**, không "giữ nguyên": hết hạn → `REVERT_DEFAULT`; mất `MTR_POC`/BMS cũ → BESS P = 0 hoặc native, PV về giới hạn native; thiết bị không có watchdog không nhận setpoint P cưỡng bức | [PROPOSAL] | K §6 #17 | NFR-REL-001, 002, 007 |
| D-10-08 | **Mục tiêu khả dụng tách theo mặt phẳng**: điều khiển cục bộ edge cao nhất (≥ 99,95%); Command API ≥ 99,5% tổng; giám sát ≥ 99,5%. Cloud sập không làm mất an toàn, chỉ mất tối ưu/giám sát từ xa | [PROPOSAL] | I §3.14; K §3.8 | NFR-REL-004 |
| D-10-09 | **Fail-closed cho control plane**: IdP, PDP, KMS/Signer hoặc DB lệnh không sẵn sàng → không phát lệnh mới; monitoring plane vẫn chạy | [PROPOSAL] | 04 §5.14 "Lỗi và trường hợp biên" | NFR-REL-015 (mới) |
| D-10-10 | **Ký lệnh bằng JWS ES256 trên JSON chuẩn hóa JCS (RFC 8785)**; chốt câu hỏi mở của [07 §8.2](07-device-integration.md) | [PROPOSAL] | 07 §8.2 | NFR-SEC-004 |
| D-10-11 | **Không tuyên bố tuân thủ.** Lộ trình: ISO/IEC 27001 cho vận hành cloud → IEC 62443-4-2 cho edge → đánh giá kiến trúc theo 62443-3-3. Tuyên bố bảo mật của hãng ghi là "tự tuyên bố" | [PROPOSAL] | K §6 #34 | NFR-SEC-025 |
| D-10-12 | **Hosting tại Việt Nam là mặc định** cho khách Việt Nam, chờ kiểm chứng pháp lý (Q-I-04 là điều kiện chặn phát hành) | [INFERENCE] | K §6 #31 | NFR-SEC-026, NFR-DATA-010 |
| D-10-13 | **Phân pha nặng nhẹ** (K §3.8): ký lệnh, `expires_at`, SOE, interlock, MFA + step-up, audit append-only, outbound mTLS là P0 cho Gate M2. Neo WORM theo giờ, hai DC, chứng nhận là P1/P2. Edge thiếu TPM/secure element: khóa trong file mã hóa chỉ được phép ở site chỉ giám sát và Gate M1, có ghi rủi ro (13 R-33); **không** bật Gate M2 trên edge thiếu TPM/SE (13 D-12, CF-38) | [PROPOSAL] | K §3.8; 13 D-12 | [§20.4](#s20-gate) |

**Thay đổi so với hướng FusionSolar trước.** Hướng cũ là giám sát/O&M chỉ đọc với mô hình quyền Company tree + Role + DataScope (nghiên cứu FusionSolar trước, `workflows_data_model.md`). Tài liệu này **giữ nguyên** mô hình đó cho monitoring plane và **thêm** control plane: PDP, phê duyệt, ký lệnh, SOE, Governor, kill switch. Đây là phần mở rộng có chủ đích vì nền tảng bắt đầu ghi lệnh vật lý, không phải mâu thuẫn. [PROPOSAL]

---

<a id="s2"></a>
## 2. Ranh giới an toàn: EMS làm gì, không làm gì

### 2.1 Tuyên bố ranh giới

> **[PROPOSAL] Tuyên bố ranh giới an toàn (dùng nguyên văn trong tài liệu bán hàng, hợp đồng và biên bản commissioning).**
> EMS (cloud và edge) là lớp **giám sát và điều phối (supervisory)**. EMS **không** phải hệ thống bảo vệ. Bảo vệ con người, thiết bị và lưới do thiết bị native và mạch cứng đảm nhận: BMS (ngắt contactor, giới hạn CCL/DCL), PCS/inverter (bảo vệ lưới, chống tách đảo, ride-through theo chứng nhận của thiết bị), rơ-le bảo vệ và rơ-le chống phát ngược, mạch E-stop, hệ PCCC. EMS chỉ đặt chế độ, giới hạn và setpoint **nằm trong** giới hạn mà các hệ trên cho phép. Mọi chức năng bảo vệ phải hoạt động đúng khi EMS mất kết nối, bị lỗi hoặc bị chiếm quyền. EMS không sửa thông số bảo vệ, không điều khiển E-stop và không bỏ qua interlock.

Cơ sở:
- [FACT, Med] Một thiết kế ESS được cấp patent cho thấy BMS gửi tín hiệu bảo vệ tới PCS qua **dây cứng** để phản ứng thời gian thực, còn kênh tới EMS là TCP/IP, RS485 hoặc CAN — https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11411391 (qua kết quả tìm kiếm, ghi chú E; [07 §3.1](07-device-integration.md)). Đây là một thiết kế, không phải chuẩn.
- [FACT, Med–High] Inverter đã có chứng nhận UL 1741 SB vẫn có lỗi tương tác ở giao diện SunSpec Modbus — https://sunspec.org/communication-interface-defects-revealed-inul-1741-sb-certified-inverters/ (qua kết quả tìm kiếm, ghi chú E). [INFERENCE] Chứng nhận đấu nối của thiết bị **không** chứng minh rằng điều khiển từ xa an toàn; EMS phải kiểm readback và fail-safe riêng.
- [INFERENCE] Phân vai BMS/PCS/edge/cloud theo C §3.7 và A X-04, cùng nguyên tắc "defense in depth" của IEC 62443 và NIST SP 800-82 (kiến thức nền, chưa kiểm chứng câu chữ).

### 2.2 Phân vai theo lớp

| Lớp | Thành phần | Trách nhiệm an toàn | EMS được làm | EMS **không** được làm |
|---|---|---|---|---|
| L-P (bảo vệ cứng, Z0) | Rơ-le bảo vệ, rơ-le chống phát ngược, MCCB/contactor, mạch E-stop, PCCC | Bảo vệ người, thiết bị, lưới; độc lập phần mềm | Đọc trạng thái (DI/Modbus) để hiển thị, interlock, bằng chứng | Ghi, reset, bỏ qua, mô phỏng tín hiệu |
| L-N (native, Z1) | BMS, PCS, inverter, charger, controller/logger hãng đã chứng nhận | Giới hạn vận hành, SOC/nhiệt/điện áp, grid code, vòng nhanh native | Đặt chế độ, giới hạn, setpoint trong biên native; đọc lại | Sửa grid code, ngưỡng BMS, cài đặt bảo vệ; cập nhật firmware hãng (07 PR-E-14) |
| L-E (edge, Z2/Z3) | Edge của ta: driver, arbiter 12 mức, limit chain, interlock, watchdog | Kẹp theo SOE, interlock, fail-safe khi mất dữ liệu/lệnh hết hạn; một chủ vòng mỗi biến | Chạy vòng nhanh khi native không có chức năng (`control_owner = EDGE`); ghi setpoint có hạn | Ghi ngoài SOE; ghi khi interlock tác động; ghi tới thiết bị chưa `VERIFIED_*`; ghi thông số C4 |
| L-C (cloud, Z5/Z6) | Command API, PDP, Signer, bộ sinh lịch, Governor, giám sát | Kiểm quyền, SOE, ngân sách đội; ký lệnh; audit | Gửi lịch/chế độ/setpoint **có hạn** tới edge | Ghi trực tiếp thiết bị; giữ lệnh vô thời hạn; điều khiển vòng nhanh; nằm trong vòng bảo vệ |
| L-V (cloud hãng, Z8) | FusionSolar, iSolarCloud… | Ngoài kiểm soát của ta | Đọc dữ liệu (connector chỉ đọc) | Ghi mặc định; ghi qua cloud hãng chỉ là ngoại lệ P2 có cờ (F-INT-14) |

### 2.3 Cloud được làm và không được làm

| Cloud ĐƯỢC | Cloud KHÔNG ĐƯỢC |
|---|---|
| Gửi `APPLY_SCHEDULE` (slot 15 phút, horizon ≥ 48 h, hạn ≤ 7 ngày) | Gửi lệnh không có `expires_at` |
| Gửi setpoint/chế độ thủ công có hạn (setpoint mặc định 15 phút, tối đa 1 h) | Ghi Modbus/OCPP trực tiếp tới thiết bị; mở kết nối inbound tới site |
| Đề xuất SOE (đi qua quy trình C3, ký, edge kiểm) | Sửa grid code, ngưỡng BMS, cài đặt rơ-le, firmware thiết bị của hãng |
| Bật kill switch (tắt kênh lệnh từ xa) | Có nút "E-stop từ xa"; reset E-stop |
| Đẩy cấu hình edge đã ký, OTA edge đã ký (C3) | Bỏ qua interlock, LOCAL/REMOTE, Governor |
| Đọc toàn bộ trạng thái, audit, kết quả readback | Hiển thị "đã áp dụng" trước khi edge xác nhận readback |
| Ghi qua cloud hãng (P2, cờ riêng, ≥ C2, chỉ lịch chậm) | Dùng cloud hãng cho zero-export/peak shaving thời gian thực (độ trễ phút, [07 §3.4](07-device-integration.md)) |

### 2.4 Phân định trách nhiệm (RACI rút gọn)

| Việc | Hãng thiết bị | Installer/EPC (P4/P5) | O&M (P3) | Chủ tài sản (P1/P6) | Nền tảng (ta) |
|---|---|---|---|---|---|
| Bảo vệ thiết bị, chứng nhận đấu nối, UL/IEC an toàn BESS | R/A | C (lắp đúng) | I | I | I |
| Mạch E-stop, rơ-le chống phát ngược, PCCC | C | R | C | A | I (chỉ đọc) |
| Công tắc LOCAL/REMOTE nối DI edge (site M2 có BESS) | — | R | C | A | C (yêu cầu, kiểm) |
| SOE: đề xuất / duyệt | C (datasheet) | R (đề xuất) | C | A (đồng ý) | R (cơ chế ký, kiểm, Governor) |
| Commissioning, phép thử dấu, test watchdog | C | R | C | A (ký biên bản) | R (checklist, công cụ) |
| Bật điều khiển từ xa (`control_enabled`) | — | R (yêu cầu) | C | **A (ConsentRecord)** | R (C3, M2ReadinessCheck) |
| Bảo mật cloud/edge, vá lỗ hổng, audit | — | — | — | I | R/A |
| Kênh cloud riêng của hãng (giữ hay chặn) | C | R (cấu hình) | C | A (quyết định, ghi biên bản) | C (khuyến nghị, phát hiện điều khiển ngoài) |

R = thực hiện, A = chịu trách nhiệm cuối, C = tham vấn, I = được thông báo. [PROPOSAL]

### 2.5 Tác động hợp đồng

- **BR-SEC-08 (04):** không có "kill" thương mại. Khi hết hợp đồng hoặc tranh chấp, edge chạy chiến lược mặc định cục bộ vĩnh viễn; khách xuất được dữ liệu (NFR-DATA-012). Căn cứ: [FACT] tháng 11/2024 inverter ở Mỹ, Anh, Pakistan bị vô hiệu hóa từ xa; điều tra cho thấy là **tranh chấp thương mại**, nguồn không nêu hãng — https://www.defensenews.com/global/europe/2025/05/29/chinese-hold-on-solar-power-tech-raises-fresh-sabotage-fears-in-europe/ (nghiên cứu FusionSolar trước). [UNKNOWN] Việc gán sự cố cho một hãng cụ thể chưa được kiểm chứng.
- Điều khoản dịch vụ phải ghi tuyên bố ranh giới §2.1, cam kết thời hạn cập nhật bảo mật edge (NFR-SEC-024) và quyền thu hồi đồng ý của chủ tài sản (ConsentRecord, [05 §11](05-domain-model.html#s11)). [PROPOSAL]

---

<a id="s3"></a>
## 3. Tiêu chuẩn và quy định

### 3.1 Nguyên tắc

1. **Không tuyên bố tuân thủ** khi chưa có chứng chỉ (số, phạm vi, hạn) hoặc chưa đối chiếu văn bản (K §6 #34, BR-SEC-07).
2. Edition chỉ ghi khi có URL hoặc chứng chỉ thấy được; còn lại `UNKNOWN`.
3. Tách rõ ba loại: **áp dụng cho ta** (phần mềm EMS, edge, vận hành SaaS), **áp dụng cho hãng thiết bị** (ta chỉ dùng kết quả), **tham chiếu** (dùng làm khung thiết kế, không có nghĩa vụ).

### 3.2 Bảng tiêu chuẩn

Cột "Bằng chứng": **K** = kiến thức nền, chưa kiểm chứng URL; **U** = có URL trong nghiên cứu hiện có.

| Tiêu chuẩn / văn bản | Edition (đã kiểm chứng?) | Đối tượng | Áp dụng cho ta? | Cách dùng | Bằng chứng |
|---|---|---|---|---|---|
| IEC 62443-3-2 (đánh giá rủi ro, zone & conduit) | UNKNOWN | Hệ thống IACS | Có — khung phương pháp | Phân vùng Z0–Z8, conduit, SL-T theo zone ([§10](#s10)) | K |
| IEC 62443-3-3 (yêu cầu bảo mật hệ thống, SR/RE theo 7 FR, SL 1–4) | UNKNOWN | Hệ thống | Có — "thiết kế theo tinh thần" | Mục tiêu SL-T 2 cho zone điều khiển; dùng 7 FR làm checklist [§20](#s20) | K; [FACT] Schneider công bố kiến trúc "certified by a third party according to IEC 62443-3-3" (phạm vi với EMA cloud chưa rõ) — https://www.productinfo.schneider-electric.com/esxp_digital_apps_iec/transverse/English/BM_ESXP_DG_Transverse_Section_IEC_0001148082.xml/$/ESXP_DG_SYSD_Cyber_ISA_IEC_0001157270 (qua kết quả tìm kiếm) |
| IEC 62443-4-1 (quy trình phát triển an toàn) | UNKNOWN | Nhà cung cấp sản phẩm | Có (ta là nhà sản xuất phần mềm/edge) | SDL: threat model, secure coding, SAST/DAST, quản lý lỗ hổng ([§19](#s19), NFR-SEC-024) | K |
| IEC 62443-4-2 (yêu cầu kỹ thuật thành phần) | UNKNOWN | Thành phần (edge, ứng dụng) | Có cho edge | Mục tiêu chứng nhận SL 2 cho edge ở Phase 2 (NFR-SEC-025) | K; [FACT] chứng chỉ IEC 62443-4-1/4-2 của WinCC OA có hạn tới 2026-02-06 — https://www.winccoa.com/documentation/WinCCOA/3.20/en_US/iec_62443/topics/iec_62443_certification.html (qua kết quả tìm kiếm) |
| IEC 62443-2-4 (yêu cầu với nhà cung cấp dịch vụ tích hợp/bảo trì) | UNKNOWN | Integrator, O&M | Có cho đội triển khai và installer đối tác | Checklist commissioning bảo mật, quản lý tài khoản, truy cập từ xa có giám sát | K |
| ISO/IEC 27001 (+ 27017/27018 cloud, 27019 năng lượng) | UNKNOWN | Tổ chức vận hành SaaS | Có | Mục tiêu chứng nhận 27001 khi có khách lớn; 27019 là điểm cộng | K; [FACT] Sungrow công bố đạt ISO/IEC 27019 từ BSI (tự công bố) — https://dl.sungrowpower.com/en/sungrow-achieves-iso-iec-27019-and-multiple-cybersecurity-management-system-certifications-from-bsi |
| NIST SP 800-82 (OT security) | UNKNOWN (kiến thức nền: Rev. 3, 2023 — chưa kiểm chứng) | Hướng dẫn | Tham chiếu | Kiến trúc phân vùng, biện pháp OT | K |
| NISTIR 7628 (smart grid) | UNKNOWN | Hướng dẫn | Tham chiếu | Danh mục giao diện logic DER/EMS | K |
| IEC 62351 (bảo mật giao thức hệ thống điện) | UNKNOWN | Kênh SCADA (IEC 104, 61850) | Có điều kiện — chỉ khi điện lực yêu cầu bảo mật kênh IEC 104 | Không áp ở MVP; theo dõi yêu cầu QĐ 1570 ([§10](#s10) CD-05) | K; Q-I-03 |
| IEEE 2030.5 / CSIP; IEEE 1547.3 | UNKNOWN | DER ở Mỹ | Tham chiếu | Mẫu PKI thiết bị, TLS bắt buộc | [FACT] IEEE 2030.5 dùng TLS 1.2 + chứng chỉ — https://standards.ieee.org/content/dam/ieee-standards/standards/web/documents/presentations/smart_energy_slides.pdf (qua kết quả tìm kiếm, ghi chú E). 1547.3: K |
| IEEE 1547-2018 | 2018 (theo URL) | Inverter/PCS đấu nối | **Không** (không phải chứng nhận EMS) | Chỉ đọc cấu hình grid code; cấm sửa (C4) | [FACT] IEEE 1547-2018 yêu cầu giao diện DER hỗ trợ ít nhất một trong IEEE 2030.5, IEEE 1815, SunSpec Modbus — https://sunspec.org/sunspec-1547-initiative/ (nghiên cứu FusionSolar trước) |
| UL 1741 SB | UNKNOWN | Inverter | **Không** | Như trên | [FACT] URL SunSpec ở §2.1 |
| UL 9540 / UL 9540A / IEC 62933-5-x | UNKNOWN | Hệ BESS (an toàn điện, cháy, lan truyền thermal runaway) | **Không** cho cloud. EMS không thay thế BMS/PCCC | Đọc trạng thái BMS/PCCC; không lệnh nào ảnh hưởng bảo vệ (IL-08) | K; Q-I-11 |
| ETSI EN 303 645 (IoT tiêu dùng) | UNKNOWN | Thiết bị tiêu dùng | Không trực tiếp (C&I) | Checklist tối thiểu cho edge: không mật khẩu mặc định chung, công bố lỗ hổng, cập nhật an toàn | K |
| EN 18031-1 (RED, thiết bị vô tuyến EU) | 2024 (theo chứng chỉ Huawei) | Thiết bị vô tuyến bán ở EU | Không ở VN; có nếu edge có 4G/Wi-Fi bán ở EU | P2 | [FACT] Chứng chỉ TÜV SÜD TPS-RED500957 i02 cho inverter + dongle Huawei theo RED 3.3(d), EN 18031-1:2024, hiệu lực 2025-08-21 → 2030-08-20 — https://cdn.contentspeed.ro/pimromstal.websales.ro/cs-content/cs-docs/products/35fv1635569certificateredforsun2000map0sun5000map0_78205_21_1784579986.pdf (nghiên cứu FusionSolar trước). [INFERENCE] Chứng nhận thiết bị ≠ chứng nhận EMS |
| OCPP 1.6J Security Whitepaper (Profile 1/2/3) | Ed.3 (2022), Ed.4 (02/2026) — chỉ qua snippet | Sạc EV ↔ CSMS | Có khi edge làm CSMS tối giản (P1) | Security Profile ≥ 2, mục tiêu 3 (NFR-SEC-021) | [FACT, Med] https://openchargealliance.org/?p=159286 (qua kết quả tìm kiếm, ghi chú E). Edition cần kiểm chứng trước khi trích trong 07 |
| MQTT 5, TLS 1.3/1.2, JWS (RFC 7515), JCS (RFC 8785), OIDC, OAuth 2.x, WebAuthn | Theo phiên bản ghi | Giao thức | Có | Dùng làm hợp đồng kỹ thuật | K (đặc tả công khai phổ biến; edition RFC cần ghi khi chốt ADR) |
| EU NIS2 (Directive 2022/2555) | Số hiệu theo kiến thức nền | Thực thể thiết yếu ở EU | Không ở VN; nếu có khách EU thì ta là nhà cung cấp trong chuỗi | P2 | K; [FACT] Ampowr **tự tuyên bố** "ISO27001 certified and NIS2 compliant" — https://ampowr.com/nis2-compliance/ (qua kết quả tìm kiếm) |
| EU CRA (Regulation 2024/2847) | Số hiệu theo kiến thức nền | Sản phẩm có phần tử số bán ở EU | Edge + phần mềm cài đặt **có thể** thuộc phạm vi nếu bán ở EU | P2; mốc áp dụng 12/2027 | [FACT] Chính phủ Hà Lan: yêu cầu an ninh mạng của RED áp dụng từ 1/8/2025, CRA từ 12/2027 — https://solarmagazine.nl/nieuws-zonne-energie/i41070/kabinet-verscherpt-toezicht-op-chinese-omvormers-zonnepanelen-verbod-kill-switch-bestaat-al (nghiên cứu FusionSolar trước). Q-I-06 |

**Mục tiêu Security Level** [INFERENCE, kiến thức nền chưa kiểm chứng câu chữ]: SL1 chống vi phạm ngẫu nhiên; SL2 chống tấn công cố ý bằng phương tiện đơn giản; SL3 phương tiện tinh vi, kỹ năng IACS; SL4 tài nguyên cấp quốc gia. Bảy FR của 62443: IAC, UC, SI, DC, RDF, TRE, RA. **[PROPOSAL]** SL-T 2 cho zone điều khiển (edge, OT LAN, control plane cloud); SL-T 1–2 cho monitoring. Cân nhắc SL-T 3 ở Phase 2 cho site lớn có kết nối điều độ.

### 3.3 Khung pháp lý Việt Nam

**Toàn bộ mục này chưa được kiểm chứng trong dự án** (K §3.8, mức High cho tài liệu 10). K lưu ý thêm: khung luật an ninh mạng có khả năng đã thay đổi trong 2025–2026 [UNKNOWN]. Không đưa số tháng lưu trữ pháp định vào NFR khi chưa kiểm chứng.

| Văn bản (theo kiến thức nền) | Nội dung có thể liên quan | Nhãn | Hệ quả thiết kế tạm thời |
|---|---|---|---|
| Luật An ninh mạng 2018 (24/2018/QH14) và khả năng có văn bản thay thế/hợp nhất 2025–2026 | Lưu trữ dữ liệu người dùng Việt Nam trong nước theo quy định Chính phủ | [UNKNOWN] | Hosting tại VN mặc định (NFR-SEC-026, NFR-DATA-010) |
| Nghị định 53/2022/NĐ-CP | Hướng dẫn lưu trữ dữ liệu; thời hạn lưu trữ dữ liệu và nhật ký hệ thống | [UNKNOWN] (số tháng chưa kiểm chứng) | Retention audit theo quyết định sản phẩm (13 tháng trực tuyến + ≥ 5 năm lưu trữ, K R-25), **không** gắn vào luật cho tới khi kiểm chứng |
| Nghị định 13/2023/NĐ-CP và Luật Bảo vệ dữ liệu cá nhân 2025 (số hiệu, hiệu lực, nghị định hướng dẫn chưa kiểm chứng) | Đồng ý của chủ thể, đánh giá tác động, chuyển dữ liệu ra nước ngoài, thông báo vi phạm | [UNKNOWN] | DPIA (P1); quy trình thông báo vi phạm trong [§18.6](#s18); phân loại D3 |
| Luật An toàn thông tin mạng 2015 + NĐ 85/2016 (phân loại cấp độ hệ thống) | Có thể áp khi khách là doanh nghiệp nhà nước / liên quan EVN | [UNKNOWN] | Hỏi khách; Q-I-05 |
| QĐ 1570/QĐ-EVN (kết nối giám sát/điều khiển với cấp điều độ) | Kênh IEC 104/Modbus TCP qua đường truyền riêng | [FACT, Low] chỉ qua tóm tắt của vendor có lợi ích (ghi chú E F-17); **không** dùng làm NFR | Conduit điều độ riêng CD-05 (P1 có điều kiện) |

**Dữ liệu EMS có phải dữ liệu cá nhân?** [INFERENCE] Phần lớn telemetry C&I là dữ liệu doanh nghiệp. Các phần là dữ liệu cá nhân: tài khoản người dùng (tên, email, số điện thoại), audit gắn người, vị trí site của hộ kinh doanh cá thể, phiên sạc EV gắn người lái/thẻ. Hồ sơ phụ tải theo thời gian có thể suy ra hành vi → phân loại D1/D3 ([§6.4](#s6)).

### 3.4 Bối cảnh quản lý quốc tế (tham khảo, không phải nghĩa vụ ở VN)

| Sự kiện | Bằng chứng | Hệ quả cho thiết kế |
|---|---|---|
| Lithuania sửa Luật Điện 12/11/2024: cấm **truy cập từ xa** của công ty Trung Quốc tới hệ mặt trời/gió/lưu trữ > 100 kW; không cấm lắp thiết bị; hạn 1/5/2025 (mới), 1/5/2026 (hiện hữu) | [FACT] https://www.lrt.lt/en/news-in-english/19/2411602/lithuania-passes-law-to-block-chinese-access-to-solar-and-wind-farm-systems ; https://pv-tech.org/lithuania-to-block-chinese-inverters-with-cybersecurity-legislation (nghiên cứu FusionSolar trước) | Khách phải **tắt được hoàn toàn kênh cloud hãng** và vẫn vận hành qua edge (NFR-SEC-017) |
| EU: đề xuất sửa Cybersecurity Act có cơ chế "danh sách nhà cung cấp rủi ro cao", nêu inverter làm ví dụ (20/1/2026) | [FACT] http://www.pv-magazine.com/2026/01/20/eu-to-ban-chinese-inverters-commission-proposal-in-cybersecurity-mulls-high-risk-vendors-list/ (nghiên cứu FusionSolar trước) | Trang "Thiết bị được hỗ trợ" (F-INT-23) cần ghi xuất xứ hãng để khách tự đánh giá; không đưa nhận định chính trị vào sản phẩm |
| EU chặn tài trợ (EIB/EIF) cho inverter và BESS (gồm PCS) của nhà cung cấp rủi ro cao từ 1/5/2026 | [FACT] https://www.ess-news.com/2026/05/04/eu-funding-ban-on-high-risk-inverters-including-chinese-suppliers-extends-to-bess-pcs/ (nghiên cứu FusionSolar trước) | Tương tự |
| Đức: quan điểm gần BSI ưu tiên điều khiển cục bộ qua smart-meter gateway thay cho đường điều khiển qua cloud hãng | [FACT, Low–Med] bài phân tích https://www.innobu.com/en/articles/chinese-inverters-security-risk-high-risk-list-2026.html (nghiên cứu FusionSolar trước) | Củng cố hướng edge-first: điều khiển đi qua edge cục bộ, không qua cloud hãng |
| Reuters 5/2025: thiết bị liên lạc không có trong tài liệu ở một số inverter/pin Trung Quốc, không nêu hãng; pv magazine "cannot verify". DOE 1/2026 (~30 inverter): 2 trường hợp lệch tài liệu, đánh giá "non-malicious" | [FACT] https://www.pv-magazine.com/2025/05/14/hidden-devices-found-in-chinese-made-inverters-in-the-us-reports-reuters/ ; https://www.pv-magazine-india.com/2026/01/29/u-s-authorities-find-no-definitive-evidence-of-hidden-devices-in-chinese-solar-inverters (nghiên cứu FusionSolar trước) | **Không** viết "inverter X có backdoor". Coi kênh cloud riêng của hãng là đường điều khiển song song ngoài kiểm soát của EMS; giám sát egress OT LAN (P1) |

---

<a id="s4"></a>
## 4. Danh tính và xác thực người dùng

Đặc tả chi tiết cho FR-SEC-001, FR-SEC-002, FR-SEC-026, NFR-SEC-005, NFR-SEC-023 ([04 §5.14](04-business-requirements.md)); tính năng F-SEC-01, F-SEC-02, F-SEC-22, F-ORG-09.

### 4.1 Giao thức và IdP

| Hạng mục | Đặc tả | Nhãn |
|---|---|---|
| Giao thức | OIDC Authorization Code + PKCE cho SPA Angular và app di động. Access token JWT ký bất đối xứng, hạn 5–10 phút; refresh token xoay vòng (rotation) có phát hiện tái sử dụng (dùng lại refresh token cũ → thu hồi cả họ token, cảnh báo bảo mật) | [PROPOSAL] |
| IdP | Tự host IdP chuẩn OIDC (ví dụ Keycloak, hợp stack Java và chạy được tại DC Việt Nam) hoặc IdP managed có vùng tại VN. Dịch vụ ứng dụng **không** lưu mật khẩu; chỉ lưu `idp_subject` ([05 §4](05-domain-model.html#s4)) | [PROPOSAL] |
| Claim bắt buộc trong token | `sub`, `org` (home org), `auth_time`, `amr`, `acr`, `sid`; không nhúng danh sách quyền theo site (quyền tính ở PDP theo thời gian thực để thu hồi có hiệu lực ngay) | [PROPOSAL] |
| Kiểm token tại API | Chữ ký, `iss`, `aud`, `exp`, `nbf`; allow-list thuật toán (chỉ RS256/ES256); từ chối `alg=none` và HS* với khóa công khai | [PROPOSAL] |
| SSO doanh nghiệp (P1) | Federation OIDC/SAML theo tenant (Entra ID, Google Workspace). Tenant bật SSO có thể bắt buộc SSO cho mọi user của tenant; MFA vẫn bắt buộc theo §4.2 (chấp nhận MFA của IdP khách nếu `amr` chứng minh được, ngược lại step-up tại IdP của ta) | [PROPOSAL] |
| Mật khẩu (khi không SSO) | ≥ 12 ký tự, kiểm danh sách mật khẩu đã lộ, không ép đổi định kỳ trừ khi nghi lộ; rate limit theo user + IP, khóa mềm 15 phút sau 10 lần sai, cảnh báo chủ tài khoản | [PROPOSAL] |

### 4.2 MFA và step-up

| Quy tắc | Giá trị | Căn cứ |
|---|---|---|
| MFA bắt buộc | Mọi vai trò có ít nhất một quyền ghi hoặc quản trị: `TECHNICIAN` trở lên trong [04 §3.2](04-business-requirements.md) (ticket là thao tác ghi dữ liệu), `OPERATOR`, `SITE_ENGINEER`, `CONTROL_SUPERVISOR`, `ORG_ADMIN`, `PLATFORM_ADMIN`, `VENDOR_SUPPORT`. Khuyến nghị cho `VIEWER`/`ANALYST` | FR-SEC-002; AC-SEC-12 |
| Phương thức | Ưu tiên WebAuthn/passkey; TOTP là phụ; **không** dùng SMS OTP làm yếu tố duy nhất | FR-SEC-002 |
| Step-up | Lệnh C2/C3, duyệt C3, duyệt SOE, `control.enable`, `killswitch.release`, `grant.issue`, `user.manage` đổi vai trò có quyền lệnh, tạo client API, break-glass: yêu cầu `auth_time` ≤ 5 phút. Với `PLATFORM_ADMIN` và duyệt C3: chỉ chấp nhận WebAuthn (`amr` chứa `hwk`/`swk`) | [04 §2](04-business-requirements.md); [PROPOSAL] cho WebAuthn bắt buộc |
| Kill switch *engage* | **Không** yêu cầu step-up (thao tác an toàn hóa phải nhanh), chỉ cần phiên MFA hợp lệ | [PROPOSAL]; NFR-SEC-013 |
| Khôi phục MFA | Qua ORG_ADMIN của tenant + xác minh ngoài băng (gọi điện số đã đăng ký); ghi audit; 24 h sau khôi phục không được duyệt C3 | [PROPOSAL] |

### 4.3 Phiên

- Web: idle 30 phút, tuyệt đối 12 h (04 §2). App di động: refresh token tối đa 30 ngày, nhưng lệnh C2/C3 luôn cần step-up. [PROPOSAL]
- Thu hồi phiên tức thì khi: user bị vô hiệu hóa, vai trò có quyền lệnh bị gỡ, grant hết hạn/thu hồi, phát hiện tái sử dụng refresh token. PDP kiểm `sid` còn hiệu lực ở mỗi lệnh. [PROPOSAL]
- Cookie phiên (nếu dùng BFF): `Secure`, `HttpOnly`, `SameSite=Strict`; chống CSRF bằng token đồng bộ cho mọi POST thay đổi trạng thái. CSP chặt (không inline script), `frame-ancestors 'none'` trừ liên kết kiosk. [PROPOSAL]

### 4.4 Danh tính máy và truy cập của bên thứ ba

| Loại | Cơ chế | Giới hạn | Mức |
|---|---|---|---|
| API client của khách (F-SEC-22, FR-SEC-026) | OAuth2 client credentials; ưu tiên `private_key_jwt` thay cho client secret | Scope tối thiểu; **mặc định chỉ đọc, 0 lệnh**; hạn ≤ 1 năm; IP allow-list tùy chọn; gắn một tenant; rate limit theo client | P1 |
| API lệnh cho bên thứ ba (F-INT-21) | Như trên + scope `cmd.c1` theo site | Chỉ C1 trong SOE; qua PDP + Governor như người; không được C2/C3 | P2 |
| Dịch vụ nội bộ | Workload identity (mTLS nội bộ hoặc token ngắn hạn do nền tảng cấp), không dùng tài khoản người | Mỗi dịch vụ một danh tính; tách `svc-ingest-*` / `svc-command-*` (NFR-SEC-002) | P0 |
| Edge | Chứng chỉ X.509 riêng ([§9](#s9)) | Chỉ topic của chính nó | P0 |
| Liên kết chia sẻ / kiosk (F-ORG-10) | Token ngẫu nhiên ≥ 128 bit trong URL, hạn ≤ 1 năm, chỉ đọc tập trường được chọn, thu hồi được | Không lộ D2/D3 | P1 |

### 4.5 Truy cập của installer, O&M và nhân viên nền tảng

- **Grant có hạn do chủ tài sản cấp** (F-ORG-09, NFR-SEC-023): `AccessGrant(max_role, valid_to bắt buộc)` ([05 §4](05-domain-model.html#s4)). Người của tổ chức dịch vụ chỉ có `RoleAssignment` kiểu DELEGATED trong grant còn hiệu lực. Nhắc xem lại mỗi 90 ngày; tài khoản không đăng nhập 90 ngày bị khóa quyền lệnh. Căn cứ: [FACT] Huawei tách đồng ý của chủ hệ thống cho installer ("O&M Authorization", quyền thông số, quyền API), bên thứ ba qua OAuth, chủ thu hồi được — https://digitalpower.huawei.com/en/eu-data-act ; https://e-solarshop.ro/wp-content/uploads/2025/07/fusionsolar-app-manual5925.pdf (nghiên cứu FusionSolar trước).
- **Quyền lệnh là grant riêng** (loại "lệnh"), tách khỏi "xem" và "cấu hình". Installer không tự cấp quyền lệnh cho mình trên site của khách (BR-ORG-03 của 04). [PROPOSAL]
- **Break-glass** (`VENDOR_SUPPORT`, F-SEC-20): yêu cầu có lý do và ticket → ORG_ADMIN của tenant duyệt → quyền đọc + cấu hình (không lệnh) tối đa 4 h → mọi thao tác audit với cờ `breakglass=true` → tenant nhận thông báo khi bắt đầu và kết thúc. Khẩn cấp khi không liên lạc được tenant (ví dụ sự cố bảo mật toàn nền tảng): hai người của nền tảng (một là trưởng bảo mật) duyệt, thông báo tenant ≤ 24 h. [PROPOSAL]
- `PLATFORM_ADMIN` **không đọc dữ liệu tenant** nếu không qua break-glass ([04 §3.2](04-business-requirements.md)).

---

<a id="s5"></a>
## 5. Phân quyền: RBAC + phạm vi + PDP cho lệnh

Đặc tả chi tiết cho FR-SEC-003, FR-SEC-006, FR-SEC-007, FR-SEC-022, NFR-SEC-006, NFR-SEC-008, BR-SEC-01…04. **Danh mục vai trò, mã quyền và ma trận mặc định do [04 §3.2–§3.4](04-business-requirements.md) sở hữu.** Mục này dùng đúng các mã đó và bổ sung chi tiết theo **hành động điều khiển**.

### 5.1 Mô hình ba lớp

1. **RBAC theo cây** (F-ORG-08, F-SEC-03): `RoleAssignment = (principal, role, scope_node)` trên cây `Organization → Portfolio (tùy chọn) → Site → Asset group → Device`; quyền kế thừa xuống cây. Mỗi request đọc/ghi dữ liệu đi qua kiểm tra RBAC ở lớp ứng dụng **và** RLS ở DB ([§6](#s6)). [PROPOSAL]
2. **Phạm vi (scope)**: grant DELEGATED không vượt `AccessGrant.max_role`; API client bị giới hạn bởi scope OAuth; liên kết chia sẻ bị giới hạn bởi tập trường. [PROPOSAL]
3. **PDP cho mọi lệnh** (Policy Decision Point): đánh giá thuộc tính và trả `{decision, effective_class, reasons[], obligations[]}`. Chính sách viết dạng khai báo, có version, có test đơn vị (ví dụ OPA/Rego, Cedar, hoặc engine nội bộ; chọn ở ADR của [06](06-system-architecture.html)). Quyết định PDP được lưu (`pdp_decision_id`) và audit. [PROPOSAL]

### 5.2 Thuộc tính đầu vào của PDP

| Nhóm | Thuộc tính | Nguồn |
|---|---|---|
| Chủ thể | `principal_type` (USER/API_CLIENT/SERVICE), vai trò hiệu lực trên scope, `auth_time`, `amr`, `sid` còn hiệu lực, grant còn hạn, số lệnh của chủ thể trong 10 phút, IP/thiết bị mới | IdP, RoleAssignment, AccessGrant |
| Tài nguyên | `site.lifecycle`, `site.control_enabled`, `site.control_gate ∈ {NONE, M1, M2}`, `edge.local_remote_state`, `remote_control_suspended` (site/tenant/nền tảng), `edge.uplink_state`, `edge.clock_state`, `device.verification_status`, `device.requires_native_fallback`, `control_owner` của chức năng, SOE version `ACTIVE_ON_EDGE`, `ConsentRecord` hiệu lực | [05 §6, §11](05-domain-model.html#s11) |
| Hành động | `type`, hạng tối thiểu của type, `params` (ΔP so với setpoint hiệu lực, % so với giới hạn SOE), `expires_at − now`, số site đích, tổng MW đích | Envelope |
| Ngữ cảnh | Ngân sách Governor còn lại (tenant/nền tảng), giờ địa phương site (giờ hành chính mặc định 08:00–17:00 T2–T6, cấu hình theo tenant), sự cố bảo mật đang mở ở tenant, cửa sổ đóng băng release | Governor ledger, lịch tenant, sổ sự cố |

### 5.3 Quy tắc chính sách (bắt buộc)

| Mã | Quy tắc | Kết quả khi vi phạm |
|---|---|---|
| PDP-01 | Chủ thể có quyền tương ứng hạng (`cmd.c1`, `cmd.c2`, `cmd.c3.request`) trên site đích hoặc tổ tiên | `DENIED: NO_PERMISSION` |
| PDP-02 | BR-SEC-04: `lifecycle = active` ∧ `control_enabled` ∧ `local_remote = REMOTE` ∧ không kill switch ∧ Gate phù hợp type ([07 §8.1](07-device-integration.md) cột Gate) | `DENIED: CONTROL_DISABLED` / `LOCAL_MODE` / `SUSPENDED` / `GATE` |
| PDP-03 | Hạng hiệu lực = max(hạng tối thiểu của type, hạng ngữ cảnh) (BR-SEC-03); không bao giờ hạ | Nâng hạng |
| PDP-04 | Nâng **C2** khi: setpoint > 80% giới hạn SOE tương ứng; giảm `soc_backup_reserve`; tắt tối ưu; > 5 site/lệnh; ngoài giờ hành chính | Yêu cầu step-up + lý do |
| PDP-05 | Nâng **C3** khi: Σ\|ΔP\| của lệnh > 10% MW BESS tenant; vượt ngân sách Governor; xả/sạc cưỡng bức bỏ qua tối ưu > 30 phút; mọi type C3 ([04 §2](04-business-requirements.md)) | Tạo `CommandApproval` |
| PDP-06 | Step-up: C2/C3 cần `auth_time` ≤ 5 phút | `DENIED: STEP_UP_REQUIRED` (UI mở step-up) |
| PDP-07 | `expires_at` có, ≤ hạn tối đa của type ([§11.6](#s11)) | `DENIED: TTL` |
| PDP-08 | Tham số trong giới hạn **đang hiệu lực trên edge** (không phải bản nháp): `M1StaticLimits` cho site `control_gate = M1` ([§11.3a](#s11-m1)), SOE đầy đủ cho site M2; site `control_enabled` mà chưa có bản `ACTIVE_ON_EDGE` → từ chối mọi ghi | `DENIED: OUT_OF_SOE` (không kẹp im lặng ở cloud) |
| PDP-09 | Thiết bị đích `VERIFIED_*`; nếu `requires_native_fallback` thì chỉ `SET_ESS_MODE` giữa các chế độ native an toàn (FR-SEC-016) | `DENIED: DEVICE_NOT_ELIGIBLE` |
| PDP-10 | Edge `ONLINE` và `clock_state = SYNCED` lần báo gần nhất (lệnh tay); lịch có thể xếp hàng khi edge offline nhưng hết hạn theo `expires_at` | `DENIED: EDGE_UNAVAILABLE` |
| PDP-11 | Rate limit: site ≤ 6 lệnh tay/phút, ≤ 12 đổi chế độ/giờ; user ≤ 30 lệnh/10 phút; `mode_change_min_interval` 300 s (FR-SEC-022) | `DENIED: RATE_LIMIT` |
| PDP-12 | SoD: người duyệt C3 ≠ người yêu cầu và khác vai trò dùng để yêu cầu; người duyệt SOE ≠ người đề xuất (BR-SEC-02) | `DENIED: SOD` |
| PDP-13 | Sự cố bảo mật mức Khẩn cấp đang mở ở tenant → mọi lệnh C1+ trừ kill switch engage bị nâng C3 | Nâng hạng |
| PDP-14 | API client: chỉ C1 trong SOE, không C2/C3 (P2) | `DENIED` |
| PDP-15 | Lệnh "an toàn hóa" (kill switch engage, `SET_ESS_P` về 0, thu hồi đồng ý, `control_enabled=false`) **không** bị chặn bởi PDP-11, PDP-04 và Governor; vẫn cần quyền và audit | Cho phép |

Ví dụ chính sách (diễn đạt): *"OPERATOR được `SET_ESS_P` trên site S nếu có binding OPERATOR trên S hoặc tổ tiên; S.control_gate = M2; S.control_enabled; REMOTE; không kill switch; phiên MFA hợp lệ; |p_w| ≤ SOE.p_ess_discharge_max_w hoặc ≤ SOE.p_ess_charge_max_w; TTL ≤ 1 h; ngân sách Governor còn đủ; nếu |p_w| > 0,8 × giới hạn → C2."*

### 5.4 Ma trận vai trò × hành động điều khiển

Bổ sung cho ma trận quyền của [04 §3.4](04-business-requirements.md) theo từng **type lệnh** ([07 §8.1](07-device-integration.md)). Ký hiệu: ✓ được phát; ✓² được phát, cần step-up + lý do (C2); R chỉ yêu cầu (C3, người khác duyệt); A được duyệt C3; — không. Tenant chỉ được thu hẹp (BR-SEC-01). "Hạng" là hạng tối thiểu; PDP có thể nâng.

| Hành động (type / thao tác) | Hạng | Gate | VIEWER | ANALYST | TECHNICIAN | OPERATOR | SITE_ENGINEER | CONTROL_SUPERVISOR | ORG_ADMIN | PLATFORM_ADMIN | API_CLIENT |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Đọc trạng thái, `dry_run` | C0 | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | metadata | scope |
| `SET_ESS_MODE` (override `site_strategy` ≤ 24 h) | C1 | M1 | — | — | — | ✓ | ✓ | ✓ | — | — | — (P2: ✓ trong SOE) |
| Đổi chiến lược mặc định (`SiteControlConfig.default_strategy`, cấu hình có version, FR-BESS-004) | C2 | M1 | — | — | — | — | ✓² | ✓² | — | — | — |
| `SET_ESS_P` (≤ 80% SOE, TTL ≤ 1 h) | C1 | M2 | — | — | — | ✓ | ✓ | ✓ | — | — | — (P2) |
| `SET_ESS_P` (> 80% SOE) | C2 | M2 | — | — | — | ✓² | ✓² | ✓² | — | — | — |
| `SET_SOC_RESERVE` tăng / giảm | C1 / C2 | M1 | — | — | — | ✓ / ✓² | ✓ / ✓² | ✓ / ✓² | — | — | — |
| `SET_PV_LIMIT` | C1 | M1 | — | — | — | ✓ | ✓ | ✓ | — | — | — |
| `SET_EXPORT_LIMIT`, `SET_IMPORT_LIMIT` (tạm thời, chặt hơn cấu hình) | C2 | M1/M2 | — | — | — | ✓² | ✓² | ✓² | — | — | — |
| Đổi cấu hình lưới site (`export_mode`, `export_limit_w`, `import_cap_w`) | C3 | M1 | — | — | — | — | R | A | — | — | — |
| `APPLY_SCHEDULE` thủ công / duyệt kế hoạch vượt guardrail | C1 / C2 | M1/M2 | — | — | — | ✓ / — | ✓ / — | ✓ / ✓² | — | — | — |
| `SET_EV_LIMIT` (P1) — edge làm CSMS hoặc edge gọi API CPO ([07 §8.10](07-device-integration.md#810-lệnh-ev-qua-api-của-cpocsms-bên-ngoài-p1-fr-ev-004-proposal)) | C1 | M2 | — | — | — | ✓ | ✓ | ✓ | — | — | — |
| Bật/tắt ghi qua API CPO (`cpo_write_enabled`, API-EV-03) / ghi qua cloud hãng (FR-INT-028) | C3 bật / C1 tắt | M2 / M1 | — | — | — | — | R | A | — | — | — |
| Đề xuất / duyệt `M1StaticLimits` (M1) / SOE đầy đủ (M2) | C3 | M1/M2 | — | — | — | — | R | A (không duyệt bản mình) | — | — | — |
| Bật `control_enabled` / Gate M2 | C3 | M1/M2 | — | — | — | — | R | A | — | — | — |
| Tắt `control_enabled` (an toàn hóa) | C1 | — | — | — | — | ✓ | ✓ | ✓ | ✓ | — | — |
| `DEVICE_ON_OFF` "Dừng vận hành từ xa" (P1) | C3 | M2 | — | — | — | R | R | R/A (khác người) | — | — | — |
| Reset lỗi từ xa (P2, chỉ khi hãng cho phép) | C3 | M2 | — | — | — | — | R | A | — | — | — |
| `SET_REVERSE_FEED_BLOCK` thủ công (P1) | C3 | M2 | — | — | — | R | R | A | — | — | — |
| Kill switch engage: site / tenant / nền tảng | C1 | — | — | — | — | ✓ site | — | ✓ site, tenant | ✓ site, tenant | ✓ nền tảng | — |
| Kill switch release | C3 | — | — | — | — | — | — | R/A | R | R/A (nền tảng, khác người) | — |
| `COMMISSIONING_TEST` (site `commissioning`, MAINTENANCE) | C2 | — | — | — | — | — | ✓² | — | — | — | — |
| `CONFIG_PUSH` edge (driver map, point mapping) | C1 | M1 | — | — | — | — | ✓ | — | — | — | — |
| `FW_UPDATE_EDGE` (OTA) | C3 | M1 | — | — | — | — | — | — | — | R/A (khác người) | — |
| Cấp/thu hồi grant; đổi vai trò có quyền lệnh | — (step-up) | — | ✓ nếu là chủ tài sản được ủy quyền | — | — | — | — | — | ✓ | — | — |
| Sửa grid code, ngưỡng BMS, rơ-le; E-stop; bỏ interlock | **C4** | — | — | — | — | — | — | — | — | — | — |

Ghi chú:
- `ORG_ADMIN` không có quyền lệnh mặc định (K §6 #29); muốn phát lệnh phải tự gán `OPERATOR`, có audit và thông báo chủ tài sản.
- `GRID_OPERATOR` không phải người dùng: lệnh IEC 104 tạo envelope nội bộ tại edge, mức arbiter 4, không qua PDP cloud ([07 §8.9](07-device-integration.md)); xác thực bằng conduit CD-05 ([§10](#s10)).
- **Đường ghi qua hệ thống bên ngoài (CF-39)**: `SET_EV_LIMIT` tới CSMS của CPO và lệnh ghi qua cloud hãng (FR-INT-028) đi **cùng chuỗi** PDP → Fleet Governor → envelope ký → edge như mọi lệnh; edge của site là client gọi API bên ngoài, cloud không gọi API ghi của CPO/hãng (không có đường cloud → cloud). TTL phía bên ngoài ≤ `expires_at`; bên ngoài không hỗ trợ hạn hoặc không đọc lại được → chỉ đọc. Site không có edge không được bật. [PROPOSAL]
- Bộ sinh lịch tầng 2/tầng 3 (`svc:scheduler-*`) phát `APPLY_SCHEDULE` như một principal dịch vụ có quyền C1, chịu PDP và Governor như người (X-I-03). [PROPOSAL]

### 5.5 Phê duyệt hai người (C3)

| Bước | Đặc tả |
|---|---|
| 1. Yêu cầu | Người yêu cầu (step-up) tạo lệnh; PDP trả `effective_class = C3`; lệnh `PENDING_APPROVAL`; tạo `CommandApproval` với `window_expires_at = now + 15 phút` |
| 2. Thông báo | Người có `cmd.c3.approve` trên site nhận thông báo in-app + e-mail; chủ tài sản nhận thông báo (không cần duyệt, trừ khi tenant cấu hình — Q-D-08 của 04) |
| 3. Màn duyệt | Diff trước/sau, tác động MW (site, tenant, % ngân sách Governor), danh sách site, hạn, lý do, kết quả `dry_run` tại edge nếu có (FR-SEC-007; [09](09-ux-ui-specification.html)) |
| 4. Duyệt | Người duyệt khác người, khác vai trò dùng để yêu cầu, step-up WebAuthn; quyết định `APPROVED`/`REJECTED` kèm lý do |
| 5. Ký và gửi | Chỉ sau `APPROVED`; `expires_at ≤ approved_at + 30 phút`; `approval_ref` vào envelope |
| 6. Hết cửa sổ | Không duyệt trong 15 phút → `APPROVAL_EXPIRED`; không envelope nào được ký (AC-SEC-02) |
| 7. Thu hồi | Người yêu cầu hoặc người duyệt có thể hủy trước khi edge `ACCEPTED` → `CANCELLED` |

---

<a id="s6"></a>
## 6. Cô lập tenant

Đặc tả chi tiết cho FR-SEC-004, NFR-SEC-007, FR-SEC-028 (silo, P2).

### 6.1 So sánh phương án

| Phương án | Cách làm | Ưu | Nhược | Quyết định |
|---|---|---|---|---|
| A. Shared schema + PostgreSQL Row-Level Security | Mọi bảng có `tenant_id`; policy RLS; `FORCE ROW LEVEL SECURITY`; role ứng dụng không owner, không `BYPASSRLS`; `SET LOCAL app.tenant_id` mỗi transaction | Rẻ, một lần migrate, hợp nhiều tenant nhỏ (installer VN) | Lỗi cấu hình pool → rò; [UNKNOWN] hạn chế RLS trên continuous aggregate của TimescaleDB (Q-I-08) | **Mặc định MVP** [PROPOSAL] |
| B. Schema per tenant | `search_path` theo tenant | Cô lập logic rõ hơn | Migration N lần; hypertable nhân bản; khó ở > 500 tenant | Không dùng |
| C. DB/cluster per tenant (silo, on-prem) | Instance riêng, có thể DC riêng | Cô lập mạnh, lưu trú/hợp đồng riêng | Đắt, vận hành nặng | SKU P2 (F-SEC-24) |

### 6.2 Đặc tả cô lập nhiều lớp (defense in depth)

| Lớp | Biện pháp | Mức |
|---|---|---|
| DB — RLS | Policy `USING (tenant_id = current_setting('app.tenant_id')::uuid)` và `WITH CHECK` tương tự trên mọi bảng có dữ liệu tenant; `FORCE ROW LEVEL SECURITY`; thiếu `app.tenant_id` → policy trả rỗng (không lỗi mở) | P0 |
| DB — role | Tách role: `migrator` (owner, chỉ dùng trong pipeline migrate), `app_rw` (không owner, không BYPASSRLS), `app_ro`, `audit_writer` (chỉ INSERT vào audit), `job_runner` (đặt tenant theo từng job). Không dịch vụ nào chạy bằng superuser | P0 |
| DB — kết nối | `SET LOCAL` trong transaction, không `SET` cấp phiên; interceptor từ chối truy vấn ngoài transaction có tenant; pool reset khi trả kết nối | P0 |
| Ứng dụng | Repository luôn thêm điều kiện `tenant_id` (lớp thứ hai); ID tài nguyên là UUID không đoán được; kiểm sở hữu trước mọi truy cập theo ID (chống IDOR) | P0 |
| Truy vấn tổng hợp TSDB | Nếu RLS không áp được cho continuous aggregate (Q-I-08): truy cập aggregate chỉ qua view/hàm có điều kiện tenant và không cấp quyền trực tiếp lên CAGG cho `app_*`; test cross-tenant phủ đường này | P0 (điều kiện PoC) |
| MQTT | ACL theo `edge_id`; ánh xạ edge→tenant/site chỉ ở registry cloud; ingest gắn `tenant_id` từ registry, **không** tin trường tenant trong payload | P0 |
| Object storage | Prefix theo tenant + policy; link tải ký số, hạn ≤ 7 ngày | P0 |
| Cache, hàng đợi, search | Khóa cache có tenant; message/job mang `tenant_id` và job runner đặt `app.tenant_id` trước khi chạy; index tìm kiếm có filter tenant bắt buộc ở lớp truy vấn | P0 |
| Log, trace | Có `tenant_id`; người xem log của nền tảng không xem payload D2/D3 | P0 |
| Mã hóa | Secrets và credential của tenant mã hóa bằng khóa riêng theo tenant (envelope encryption, KMS) ([§8](#s8)) | P0 |
| Tài nguyên | Rate limit và quota theo tenant (API, ingest, xuất dữ liệu, job) chống noisy neighbour | P0 |
| Kiểm thử | Bộ test cross-tenant tự động trong CI cho **mọi** endpoint và mọi job: tạo 2 tenant, dùng token tenant A truy cập ID của B, kỳ vọng 404/403 và không rò trong danh sách; build thất bại nếu rò (AC-SEC-09). Thêm test DB trực tiếp: role `app_rw` không đặt tenant → 0 hàng | P0 |

### 6.3 Dữ liệu dùng chung có kiểm soát

- Thư viện biểu giá EVN, thư viện driver, danh mục mã cảnh báo: bảng **toàn cục** chỉ đọc với `app_*`, ghi bởi `PLATFORM_ADMIN` qua quy trình publish có audit. Không chứa dữ liệu tenant. [PROPOSAL]
- So sánh peer giữa site (F-ALM-20) chỉ trong phạm vi tenant; so sánh liên tenant (benchmark) chỉ trên dữ liệu ẩn danh tổng hợp, cần đồng ý trong điều khoản (P2). [PROPOSAL]

### 6.4 Phân loại dữ liệu

| Lớp | Ví dụ | Mã hóa khi lưu | Lưu trú | Xuất / truy cập |
|---|---|---|---|---|
| D0 Công khai | Tài liệu sản phẩm | — | — | Tự do |
| D1 Nội bộ tenant | Telemetry, KPI, cảnh báo, báo cáo | Có (đĩa/DB) | VN mặc định | Theo RBAC; xuất có audit |
| D2 Nhạy cảm vận hành | Cấu hình site, SOE, sơ đồ một sợi, IP OT, register map riêng của OEM, credential hãng | Có + khóa theo tenant cho secrets | VN | `SITE_ENGINEER`+; audit; watermark khi xuất |
| D3 Dữ liệu cá nhân | User, audit gắn người, phiên sạc EV gắn người (`id_tag_hash`, không lưu thô) | Có | VN; chuyển ra ngoài cần hồ sơ ([UNKNOWN] theo luật) | Quyền riêng; theo yêu cầu chủ thể |
| D4 Bí mật hệ thống | Khóa CA, khóa ký lệnh/OTA/config/audit | HSM/KMS, không xuất | — | Không bao giờ |

Quyết định: NFR-SEC-026 (P0 phân loại + hosting VN; P1 DPIA và thông báo vi phạm). Dữ liệu phân tích bất thường **không bao giờ** tự sinh lệnh C1+ mà không qua PDP (X-I-11).

---

<a id="s7"></a>
## 7. Nhật ký kiểm toán (audit trail)

Đặc tả chi tiết cho FR-SEC-014, FR-SEC-015, FR-SEC-023, NFR-SEC-015, NFR-DATA-009; thực thể `AuditEvent` ở [05 §14](05-domain-model.html#s14).

### 7.1 Phạm vi ghi (bắt buộc)

| Nhóm | Sự kiện |
|---|---|
| Danh tính | Đăng nhập thành công/thất bại, MFA đăng ký/khôi phục, step-up, đăng xuất, khóa tài khoản, tái sử dụng refresh token |
| Quyền | Gán/gỡ vai trò, tạo/thu hồi grant, tạo/thu hồi client API, break-glass bắt đầu/kết thúc, phiên tunnel hỗ trợ |
| Cấu hình an toàn | SOE (đề xuất, duyệt, ký, `ACTIVE_ON_EDGE`), cấu hình lưới site, `control_enabled`, Gate, ConsentRecord, driver map, point mapping, `EdgeConfigVersion` |
| Lệnh | **Mọi chuyển trạng thái** của `DispatchCommand` (cloud và edge), quyết định PDP, `CommandApproval`, Governor từ chối/xếp hàng, kill switch, lệnh `GRID_OPERATOR` (envelope nội bộ, [07 §8.9](07-device-integration.md)) |
| Edge | Interlock bật/tắt, LOCAL/REMOTE/MAINTENANCE, E-stop, chuyển `run_mode`, reboot watchdog, `REJECTED_INVALID/REPLAY/STALE`, đổi `clock_state`, OTA |
| Dữ liệu | Xuất dữ liệu, phát hành báo cáo, restatement, công bố biểu giá, sửa dữ liệu thủ công |
| Tích hợp | Thay đổi credential connector, bật ghi qua cloud hãng (F-INT-14) |
| Nền tảng | Deploy control plane, thay đổi chính sách PDP, xoay khóa, kết quả kiểm chuỗi hash |

### 7.2 Lược đồ

Theo [05 §14](05-domain-model.html#s14): `event_id` (UUID v7), `ts` (UTC), `tenant_id`, `actor_type ∈ {USER, API_CLIENT, SERVICE, EDGE, GRID_OPERATOR}`, `actor_id`, `auth_time`, `amr`, `ip`, `user_agent`, `action`, `resource_type`, `resource_id`, `before`/`after` (hoặc hash nếu lớn), `reason`, `correlation_id`, `command_id`, `result`, `prev_hash`, `hash`. Bổ sung [PROPOSAL]: `pdp_decision_id`, `breakglass` (bool), `edge_clock_state` (cho sự kiện từ edge), `source_seq` (thứ tự từ edge).

**Dữ liệu cá nhân trong audit**: audit chỉ lưu `actor_id` (UUID); tên/email lấy từ bảng `User` khi hiển thị. Khi chủ thể yêu cầu xóa, ẩn danh hóa bảng `User`, **không** sửa audit (giữ chuỗi hash). Cần kiểm chứng tính hợp lệ của cách làm này theo luật dữ liệu cá nhân VN [UNKNOWN]. Không ghi secret, token, mật khẩu vào `before`/`after` (mask theo danh sách trường). [PROPOSAL]

### 7.3 Bất biến và chống sửa

1. **Append-only**: bảng `audit_event` partition theo tháng; `audit_writer` chỉ có `INSERT`; `REVOKE UPDATE, DELETE, TRUNCATE` cho mọi role ứng dụng; trigger từ chối UPDATE/DELETE (AC-SEC-10). Xóa partition hết hạn chỉ bằng job retention chạy bằng role riêng, có audit. [PROPOSAL, P0]
2. **Hash chain theo tenant**: `hash_i = SHA-256(hash_{i−1} ‖ JCS(event_i không gồm hash))`. Ghi tuần tự theo tenant (advisory lock theo tenant hoặc writer đơn theo partition key) để chuỗi không phân nhánh. Sự kiện nền tảng dùng chuỗi `tenant_id = PLATFORM`. [PROPOSAL, P0]
3. **Kiểm chuỗi hằng ngày**: job tính lại chuỗi; đứt chuỗi → sự cố bảo mật mức Khẩn cấp (NFR-OBS-006). [P0]
4. **Neo WORM mỗi giờ** (P1, FR-SEC-023): Merkle root các sự kiện trong giờ, ký bằng khóa KMS riêng, ghi vào object storage có object lock chế độ compliance ở tài khoản/vùng khác; tùy chọn gửi root cho khách. [UNKNOWN] nhà cung cấp tại VN có object lock/WORM không (Q-I-13). [P1]
5. **Audit tại edge**: edge giữ audit cục bộ có hash chain riêng (`edge_id`), ký lô bằng khóa edge khi đồng bộ lên cloud qua `up/event`; cloud kiểm liên tục chuỗi edge (phát hiện mất đoạn). Edge giữ audit ≥ 30 ngày cục bộ. [PROPOSAL, P0]

### 7.4 Lưu giữ và truy cập

- Lưu giữ: trực tuyến ≥ 13 tháng; lưu trữ ≥ 5 năm (WORM là P1); hợp đồng có thể kéo dài tới 10 năm (K R-25). Kế hoạch bị thay trước khi chạy: tóm tắt + hash 30 ngày. Thời hạn pháp định: [UNKNOWN] (Q-I-04). [PROPOSAL]
- Truy cập: `audit.read` (CONTROL_SUPERVISOR, ORG_ADMIN) chỉ trong tenant; nhân viên nền tảng xem audit tenant chỉ qua break-glass. Truy vấn audit cũng được audit.
- Xuất (P1): CSV/JSON kèm `prev_hash`/`hash` và bằng chứng Merkle để khách tự kiểm (FR-SEC-023).
- Nhật ký lệnh cho người dùng (FR-SEC-015): view dựng từ audit + `CommandStateTransition` ([05 §11.2](05-domain-model.html#s11-sm1)).

---

<a id="s8"></a>
## 8. Quản lý bí mật, khóa và credential

Đặc tả chi tiết cho FR-SEC-017, NFR-SEC-016.

### 8.1 Danh mục khóa và bí mật

| Bí mật | Mục đích | Nơi lưu | Thuật toán | Xoay vòng | Ai dùng |
|---|---|---|---|---|---|
| Khóa CA gốc thiết bị | Ký CA trung gian | Offline (HSM/thẻ trong két), hai người giữ | ECDSA P-384 | 10–20 năm; nghi lộ → quy trình tái phát hành toàn đội | Nghi thức ký (ceremony) |
| Khóa CA trung gian (cấp chứng chỉ edge) | Ký chứng chỉ vận hành edge | KMS/HSM không xuất | ECDSA P-256 | 2 năm, chồng lấn ≥ 6 tháng | Dịch vụ enroll |
| Khóa ký lệnh (Command Signer) | JWS ES256 trên envelope | KMS/HSM không xuất | ECDSA P-256 | 1 năm; 2 `kid` song song ≥ 30 ngày | Chỉ `svc-command-signer` |
| Khóa ký cấu hình edge | Ký `EdgeConfigVersion` (SOE, driver map, danh sách `kid` tin cậy) | KMS/HSM | ECDSA P-256 | 1 năm | `svc-config-signer` |
| Khóa OTA (root/targets/snapshot/timestamp kiểu TUF) | Ký metadata và ảnh firmware edge | Root offline; targets trong KMS | Ed25519 hoặc ECDSA | Root 5 năm; targets 1 năm; timestamp ngắn | Pipeline phát hành |
| Khóa neo audit | Ký Merkle root | KMS | ECDSA P-256 | 1 năm | Job neo |
| Khóa mã hóa dữ liệu theo tenant (KEK) | Bọc DEK cho secrets/credential tenant | KMS | AES-256-GCM | 1 năm (re-wrap) | Dịch vụ secrets |
| Khóa edge (IDevID/LDevID) | mTLS, ký ack, ký lô audit edge | TPM 2.0/secure element, không xuất (ngoại lệ tạm: file mã hóa) | ECDSA P-256 | Theo chứng chỉ 90 ngày | Edge |
| Credential cloud hãng (OAuth token, appSecret, tài khoản Northbound) | Connector | Vault/secret store, mã hóa theo tenant | — | Theo hãng; refresh tự động | Connector của tenant đó; credential có quyền ghi chỉ control plane đọc được |
| Mật khẩu DB, broker, dịch vụ | Kết nối nội bộ | Vault dynamic secrets hoặc workload identity | — | ≤ 30 ngày hoặc động | Dịch vụ |
| Bí mật webhook (HMAC) | Ký webhook gửi khách (F-INT-20) | Vault theo tenant | HMAC-SHA256 | Khách xoay; 2 bí mật song song | Dịch vụ webhook |
| Credential OT tại edge (OCPP Basic Auth, mật khẩu UI cục bộ) | OCPP Profile 2, HMI cục bộ | Kho bí mật của edge (TPM-sealed) | — | Sinh ngẫu nhiên theo thiết bị/site; xoay khi bàn giao | Edge |

### 8.2 Quy tắc

- Không secret trong repo, image, biến môi trường dạng file `.env` của production, log, trace, audit. Quét secret ở pre-commit và phía server CI; phát hiện → chặn merge và xoay ngay. [PROPOSAL, P0]
- Khóa ký không bao giờ rời KMS/HSM; dịch vụ gửi digest để ký. Giới hạn tốc độ ký theo signer (chống lạm dụng khi dịch vụ bị chiếm): mặc định ≤ 50 chữ ký/giây toàn nền tảng, cảnh báo khi vượt p99 lịch sử × 3. [PROPOSAL]
- **KMS/Signer không sẵn sàng → không phát lệnh mới** (fail-closed); edge tiếp tục cục bộ; cảnh báo PO ([04 §5.14](04-business-requirements.md)).
- **Lộ khóa ký lệnh**: (1) kill switch nền tảng; (2) đẩy cấu hình ký bằng khóa cấu hình loại bỏ `kid` bị lộ khỏi danh sách tin cậy; (3) phát hành `kid` mới; (4) tăng `seq` sàn; (5) tháo kill switch theo C3 từng tenant. Khóa cấu hình và khóa lệnh là **hai khóa khác nhau** để một khóa lộ không tự hợp thức hóa khóa còn lại. [PROPOSAL]
- Credential CPO (FR-EV-004) và cloud hãng: tách credential đọc (connector, monitoring plane) và credential ghi (chỉ edge của site dùng, control plane); không lưu credential có quyền ghi nếu cờ ghi tắt (FR-EV-004, FR-INT-028 theo CF-39); ưu tiên token có phạm vi chỉ đọc nếu hãng hỗ trợ. [FACT] Huawei 9/2025 thêm bước chủ hệ thống phải cấp quyền API cho installer, làm các tích hợp bên thứ ba ngừng chạy cho tới khi được cấp — https://community.home-assistant.io/t/fusion-solar-doesnt-work-anymore/927417 (nghiên cứu FusionSolar trước). [INFERENCE] Connector cần trạng thái `AUTH_REVOKED` riêng và cảnh báo, không coi là lỗi mạng.

---

<a id="s9"></a>
## 9. Danh tính thiết bị và kênh truyền an toàn

Đặc tả chi tiết cho NFR-SEC-003, NFR-SEC-004, NFR-SEC-020, NFR-SEC-022, NFR-REL-011; tính năng F-INT-02, F-INT-08, F-INT-10, F-INT-11, F-INT-12, F-SEC-20.

### 9.1 Phân cấp PKI

```
Root CA thiết bị (offline, P-384)
 ├── Issuing CA "edge-ops" (KMS/HSM)   → chứng chỉ vận hành edge (LDevID, 90 ngày)
 └── Issuing CA "edge-birth" (KMS/HSM) → chứng chỉ xuất xưởng (IDevID, theo vòng đời phần cứng; chỉ gọi được /enroll)
Broker/endpoint server: chứng chỉ TLS riêng (CA công khai hoặc CA nội bộ); edge pin CA phát hành cho endpoint
Khóa ký lệnh / cấu hình / OTA / audit: JWK set có kid, không phải X.509; khóa công khai phân phối qua EdgeConfigVersion đã ký và ảnh firmware
```

- Subject chứng chỉ edge: `CN=edge-<uuid>`, SAN URI `urn:ems:edge:<uuid>`. **Không** nhúng tenant/site (edge có thể chuyển site); ánh xạ edge→site ở `EdgeSiteBinding` ([05 §6](05-domain-model.html#s6)). [PROPOSAL]
- Edge thiếu TPM/secure element: khóa lưu trong file mã hóa bằng khóa dẫn xuất từ phần cứng; ghi cờ `key_storage = SOFTWARE` và rủi ro ứng viên I-R-09; không đủ điều kiện mục tiêu chứng nhận 62443-4-2 (K §3.8). Chỉ dùng ở site chỉ giám sát và Gate M1; **không bật Gate M2** trên edge này (13 D-12, CF-38). [PROPOSAL]

### 9.2 Vòng đời danh tính edge

| Bước | Đặc tả | Mã |
|---|---|---|
| 1. Xuất xưởng | Sinh cặp khóa trong TPM; nạp IDevID; ghi `serial_no`, mã QR (serial + vân tay khóa công khai); edge `MANUFACTURED`. Không mật khẩu mặc định chung: mật khẩu UI cục bộ ngẫu nhiên theo thiết bị in trên nhãn, bắt đổi lần đầu | F-INT-01 |
| 2. Claim | `SITE_ENGINEER` quét QR trong app, chọn site; cloud ghi `EdgeSiteBinding`, edge `CLAIMED` | F-INT-02 |
| 3. Enroll | Edge gọi `/enroll` bằng IDevID (mTLS), gửi CSR khóa vận hành; cloud kiểm edge đã claim → cấp LDevID 90 ngày; edge `ACTIVE` | F-INT-02 |
| 4. Gia hạn | Tự gia hạn ở 2/3 hạn (ngày 60); thất bại liên tục 14 ngày → cảnh báo mức Cao. **Hết hạn chứng chỉ không dừng điều khiển cục bộ** (NFR-REL-011): edge mất uplink, chạy lịch/mặc định; `/enroll` chấp nhận gia hạn bằng IDevID còn hiệu lực trong 30 ngày sau hết hạn | NFR-SEC-003 |
| 5. Gỡ/chuyển site | Thu hồi LDevID; xóa binding; edge xóa cấu hình site, buffer đã đồng bộ, khóa OT; enroll lại cho site mới | F-INT-02 |
| 6. Thu hồi | Danh sách chặn tại broker và `/enroll` (tra mỗi lần kết nối) + hạn ngắn; không dựa vào CRL/OCSP phía edge | NFR-SEC-003 |
| 7. RMA / hủy | `REVOKED`; xóa khóa bằng lệnh TPM clear khi thu hồi phần cứng | — |

### 9.3 Kênh edge ↔ cloud

| Thuộc tính | Đặc tả | Căn cứ |
|---|---|---|
| Hướng | **Chỉ outbound** từ edge; không mở cổng inbound tại site; không cần IP tĩnh | [FACT] Huawei SmartLogger3000 dùng kênh outbound "Encrypted Modbus TCP" tới hệ quản lý, SSL bật mặc định, "TLS1.2 or a later version is recommended"; Modbus TCP không mã hóa tắt mặc định — https://support.huawei.com/enterprise/en/doc/EDOC1100108365/4fbe151e/setting-parameters-for-connecting-to-the-management-system-v300r001c00 (nghiên cứu FusionSolar trước). [INFERENCE] Đây là mẫu chuẩn cho gateway |
| Giao thức | MQTT 5 qua TLS 1.3 (cho phép 1.2 chỉ với cipher AEAD + ECDHE); mTLS; cổng 8883, dự phòng 443 (MQTT qua WebSocket) khi tường lửa khách chặn | K §6 #20 |
| Topic | `ems/v1/{edge_id}/up/{state \| telemetry/{stream} \| event \| backfill \| cmd-ack}`, `ems/v1/{edge_id}/down/{cmd \| config}` | K R-12; [07 §7.1](07-device-integration.md) |
| ACL broker | Edge X chỉ publish `ems/v1/X/up/#`, chỉ subscribe `ems/v1/X/down/#`; cấm wildcard ngoài phạm vi; client cloud `svc-ingest-*` chỉ subscribe `up/{state,telemetry,event,backfill}`; chỉ `svc-command-dispatcher` publish `down/cmd`; trên `down/config` chỉ hai client được publish: `svc-config-*` (tin `CONFIG` và trạng thái tạm ngưng, đã ký) và `svc-ingest-ack` (**chỉ** tin `TELEMETRY_ACK`, `RESEND_REQUEST`, không ký, không retained — theo [06 ADR-16](06-system-architecture.html), 13 CF-32; [07 §7.1](07-device-integration.md)). **Edge chỉ áp tin `CONFIG`/trạng thái có chữ ký khóa cấu hình hợp lệ** ([§9.4](#s9), [§11.8](#s11)); tin không ký trên `down/config` chỉ được hiểu là ack/resend, tối đa làm edge xóa buffer đã ack hoặc gửi lại dữ liệu, không bao giờ đổi cấu hình hay điều khiển. Rủi ro còn lại: ack giả từ broker bị chiếm có thể làm edge xóa buffer chưa ingest (mất dữ liệu, không mất an toàn) — giảm bằng ACL và kiểm `ack_seq` ≤ `seq` đã gửi | NFR-SEC-002 |
| Lệnh | QoS 1, **không retained**, Message Expiry = `expires_at − now` | K §6 #20 |
| Toàn vẹn ứng dụng | Lệnh và cấu hình **ký ở tầng ứng dụng** (không chỉ dựa vào TLS): broker bị chiếm vẫn không giả được lệnh; ack ký bằng khóa edge (chống giả "APPLIED") | K R-11; [§11.8](#s11) |
| Telemetry | Không ký từng message (mTLS đủ cho nguồn gốc); lô sự kiện an toàn (interlock, LOCAL/REMOTE, audit edge) có hash chain và chữ ký lô | [PROPOSAL] |
| Quota | Giới hạn kết nối/giây và byte/giây theo edge tại broker; edge lỗi vòng lặp không làm sập broker | NFR-REL-016 |
| Phát hiện offline | Keepalive MQTT 30–60 s + `up/state` mỗi 30 s có `seq`; `OFFLINE` sau 3 heartbeat lỡ (≈ 90 s); cảnh báo người sau 5 phút | NFR-REL-008 |

### 9.4 Cấu hình, OTA và thời gian

- **Cấu hình edge** (F-INT-11): `EdgeConfigVersion` có version, `content_hash`, chữ ký khóa cấu hình; edge từ chối cấu hình không ký, ký bằng `kid` lạ, hoặc version thấp hơn bản đang áp (chống rollback cấu hình). Cùng cơ chế ký/version áp cho `M1StaticLimits`/SOE ([§11.3a](#s11-m1)) và tin trạng thái tạm ngưng `REMOTE_CONTROL_STATE` (retained, [§14.4](#s14)); tin không ký trên `down/config` chỉ có thể là `TELEMETRY_ACK`/`RESEND_REQUEST` ([§9.3](#s9)). Danh sách `kid` tin cậy cho lệnh nằm trong cấu hình đã ký; `kid` gốc của khóa cấu hình nằm trong ảnh firmware. [PROPOSAL]
- **OTA edge** (F-INT-12, NFR-SEC-020): metadata kiểu TUF (root offline, targets/snapshot/timestamp), ảnh ký số; cài A/B có rollback tự động nếu health check thất bại trong 10 phút; bộ đếm anti-rollback; triển khai theo đợt canary ([§14.4](#s14)); OTA là C3. **Không** cập nhật firmware thiết bị của hãng. [FACT] CCC (2026) phát hiện cập nhật firmware và điều khiển từ xa không xác thực ở microinverter Hoymiles — https://cybernews.com/security/china-solar-inverters-hack/ (nghiên cứu FusionSolar trước): cơ chế cập nhật là bề mặt tấn công thật.
- **Thời gian** (F-INT-10): chrony với ≥ 2 nguồn (ưu tiên NTS khi có, hoặc NTP nội bộ của khách) + RTC có pin. Edge từ chối bước nhảy đồng hồ > 1 s khi đang `SYNCED` mà không có ≥ 2 nguồn đồng ý; `clock_state = UNSYNCED` → IL-06 chặn mọi lệnh có hạn, vòng cục bộ vẫn chạy. Mục đích: chống làm lệnh hết hạn thành hợp lệ bằng cách giả thời gian (ABU-12). [PROPOSAL, NFR-SEC-028 mới]

### 9.5 Truy cập hỗ trợ từ xa

- Không VPN thường trực tới mạng OT của khách. Hỗ trợ (SSH/UI edge) qua **reverse tunnel theo yêu cầu**: lệnh ký (C2) + chủ site cho phép trong app → edge mở tunnel outbound tới bastion, tự đóng sau ≤ 2 h, phiên được ghi (lệnh shell, thời gian), tunnel không định tuyến tới OT LAN (chỉ tới tiến trình edge). [PROPOSAL, P1, NFR-SEC-022]
- [INFERENCE, kiến thức nền chưa kiểm chứng URL] Các sự cố lưới Ukraine 2015/2016 được mô tả rộng rãi là khai thác truy cập từ xa thường trực và giao thức SCADA không xác thực; dùng làm lý do thiết kế, không trích làm FACT.

### 9.6 Kênh khác

| Kênh | Đặc tả | Mức |
|---|---|---|
| HTTPS edge → cloud (OTA, file lớn) | TLS + mTLS bằng LDevID; chỉ tới endpoint đã pin | P0 |
| OCPP charger → edge (edge làm CSMS tối giản) | OCPP 1.6J Security Profile ≥ 2 (TLS + Basic Auth với mật khẩu ngẫu nhiên theo charger), mục tiêu Profile 3 (chứng chỉ client); charger chỉ thấy cổng OCPP của edge trên OT LAN | P1, NFR-SEC-021 |
| IEC 104 master điều độ → edge | Conduit CD-05: NIC/VLAN riêng, chỉ chấp nhận IP master đã cấu hình (trong cấu hình đã ký), chỉ type lệnh đã cấu hình; IEC 62351 [UNKNOWN] theo yêu cầu điện lực | P1 có điều kiện, NFR-SEC-032 (mới) |
| Modbus TCP server của edge cho SCADA khách (F-INT-17) | Cổng riêng trên OT LAN hoặc VLAN khách; **chỉ đọc** mặc định; allow-list IP | P1 |
| Edge → API CSMS của CPO (ghi giới hạn EV, FR-EV-004) | HTTPS TLS ≥ 1.2, chỉ tới endpoint CPO đã cấu hình trong cấu hình ký (allow-list); credential **ghi** riêng với credential **đọc** của connector, lưu trong vault theo §8, không đọc lại qua API; hạn mức gọi theo hợp đồng CPO; mọi lời gọi audit | P1, NFR-SEC-018 (mở rộng), cờ mặc định tắt |
| Webhook ra ngoài (F-INT-20) | HTTPS, ký HMAC, chống SSRF (chặn IP nội bộ/metadata), retry có backoff | P1 |

---

<a id="s10"></a>
## 10. Phân vùng OT/IT: zone và conduit

Đặc tả chi tiết cho FR-SEC-018, NFR-SEC-017; khung theo tinh thần IEC 62443-3-2 (kiến thức nền) và mô hình Purdue (kiến thức nền).

### 10.1 Mô tả sơ đồ zone và conduit

Sơ đồ dưới đây là mô tả văn bản để người viết [06](06-system-architecture.html) vẽ SVG (class `zone`, `box ot`, `box ext`, `edge ctl`). Mũi tên chỉ hướng **khởi tạo kết nối**.

```
 ┌──────────────── Z7 NGƯỜI DÙNG (Internet) ─────────────────┐
 │  Web/Mobile (OIDC+MFA)          API client (OAuth2)        │
 └──────────────┬──────────────────────────┬─────────────────┘
                │ CD-08 HTTPS              │ CD-08 HTTPS
 ┌──────────────▼──── CLOUD (VN, hai mặt phẳng) ─────────────────────────────────┐
 │ ┌─ Z6 MONITORING PLANE ─────────────┐   ┌─ Z5 CONTROL PLANE (namespace riêng) ─┐│
 │ │ Ingest · TSDB · Dashboard · Báo cáo │   │ Command API · PDP · Approval ·       ││
 │ │ Cảnh báo · Connector cloud hãng     │   │ Governor · Signer(→KMS) · Dispatcher ││
 │ │ (chỉ đọc)                           │   │ Config signer · OTA                  ││
 │ └──────┬─────────────────────▲───────┘   └──────────┬───────────────────────────┘│
 │        │CD-07 (đọc)          │ up/#                 │ down/cmd, down/config (ký) │
 │        ▼                     │      ┌───────────────▼──────┐                     │
 │   Z8 CLOUD HÃNG (ngoài)      └──────┤   MQTT broker (mTLS)  │                     │
 └─────────────────────────────────────┴───────────▲──────────┴─────────────────────┘
        ▲ (kênh riêng của hãng, nếu khách giữ)        │ CD-04 MQTT 5/TLS, OUTBOUND từ edge
        │ CD-06 (VLAN riêng, không qua edge)          │
 ┌──────┼──────────────── SITE KHÁCH ─────────────────┼──────────────────────────────┐
 │      │                ┌─ Z3 DMZ SITE: edge NIC WAN ─┴─┐   ┌─ Z4 KÊNH ĐIỀU ĐỘ ──┐   │
 │      │                │  (không route/NAT WAN↔OT)     │◄──┤ IEC 104 master     │   │
 │      │                ├─ Z2 CONTROLLER SITE: edge ────┤CD-05 (VPN/APN riêng)  │   │
 │      │                │  NIC OT · arbiter · interlock │   └────────────────────┘   │
 │      │                └──────┬────────────────────────┘                            │
 │      │                       │ CD-02 Modbus TCP/RTU, CAN (nghe), OCPP (charger→edge)│
 │ ┌────┴───────────── Z1 THIẾT BỊ (OT LAN) ──────────────────────────────────────┐  │
 │ │ Logger/EMS hãng · PCS · inverter · BMS · công tơ POC · charger · I/O          │  │
 │ └───────────────────────┬──────────────────────────────────────────────────────┘  │
 │                         │ CD-01 dây cứng (không phần mềm)                          │
 │ ┌───────────── Z0 BẢO VỆ CỨNG ─────────────────────────────────────────────────┐  │
 │ │ Rơ-le bảo vệ · rơ-le chống phát ngược · E-stop · contactor BMS · PCCC          │  │
 │ └──────────────────────────────────────────────────────────────────────────────┘  │
 │  CD-03 DI của edge ← tiếp điểm phụ Z0 (LOCAL/REMOTE, E-stop, PCCC): CHỈ ĐỌC         │
 └────────────────────────────────────────────────────────────────────────────────────┘
```

### 10.2 Zone

| Zone | Thành phần | Purdue (kiến thức nền) | SL-T đề xuất | Chính sách |
|---|---|---|---|---|
| Z0 Bảo vệ cứng | Rơ-le, E-stop, contactor BMS, rơ-le chống phát ngược, PCCC | L0–L1 | Ngoài phạm vi phần mềm | Không phần mềm nào của ta ghi; chỉ đọc qua tiếp điểm phụ (CD-03) |
| Z1 Thiết bị | PCS, inverter, BMS, công tơ, charger, logger hãng, I/O | L1 | Theo thiết bị (thường thấp vì Modbus không xác thực — [INFERENCE] kiến thức nền giao thức) | Bù bằng cô lập mạng; edge là master duy nhất |
| Z2 Controller site | Edge (phía OT): driver, arbiter, interlock, buffer | L2 | **SL2** | Tiến trình điều khiển tách tiến trình kết nối cloud; quyền tối thiểu |
| Z3 DMZ site | Edge (phía WAN) | L3.5 | SL2 | Hai NIC; **không** route/NAT/bridge giữa WAN và OT |
| Z4 Kênh điều độ | IEC 104 slave của edge ↔ master điều độ | Conduit riêng | Theo yêu cầu điện lực [UNKNOWN] | NIC/VLAN riêng; P1 có điều kiện |
| Z5 Cloud control plane | Command API, PDP, Approval, Governor, Signer, Dispatcher, Config/OTA | L4 | SL2 | Namespace/tài khoản riêng; egress hạn chế; release có review bảo mật |
| Z6 Cloud monitoring plane | Ingest, TSDB, dashboard, báo cáo, cảnh báo, connector | L4 | SL1–2 | Không đọc bảng lệnh; không publish `down/#` |
| Z7 Người dùng | Web, mobile, API client | L5 | — | MFA, step-up |
| Z8 Cloud hãng | Dongle/logger → cloud hãng | Ngoài | — | Chính sách giữ/chặn do khách chọn |

### 10.3 Conduit và luật tối thiểu

| Conduit | Giữa | Giao thức / cổng | Hướng khởi tạo | Luật |
|---|---|---|---|---|
| CD-01 | Z0 ↔ Z1 | Dây cứng | — | Ngoài phần mềm |
| CD-02 | Z2 ↔ Z1 | Modbus TCP 502 / cổng hãng; Modbus RTU; CAN chỉ nghe; OCPP WS (charger → edge) | Edge → thiết bị (Modbus); charger → edge (OCPP) | Edge là master Modbus duy nhất mỗi bus/thiết bị; chặn thiết bị Z1 ra Internet (trừ CD-06); allow-list IP/unit ID trong cấu hình đã ký; CAN không bao giờ phát |
| CD-03 | Z0 → Z2 | DI (tiếp điểm khô) | — | Chỉ đọc; DO của edge không nối vào mạch bảo vệ |
| CD-04 | Z3 → Z5/Z6 | MQTT 5/TLS 8883 (443 dự phòng), HTTPS OTA, NTP/NTS, DNS | **Chỉ outbound** | Không inbound; allow-list FQDN; DNS tới resolver đã cấu hình |
| CD-05 | Z4 → Z2 | IEC 104 qua VPN/APN riêng | Master điều độ → edge | NIC/VLAN riêng; allow-list IP master; chỉ type lệnh đã cấu hình; không route sang WAN/OT |
| CD-06 | Z1 → Z8 | Kênh riêng của hãng (dongle/logger) | Thiết bị → cloud hãng | Khách chọn: (a) **chặn** (khuyến nghị cho site M2); (b) giữ qua VLAN riêng, không qua edge, ghi biên bản; phát hiện điều khiển ngoài (NFR-SEC-019) |
| CD-07 | Z6 → Z8 | HTTPS API cloud hãng | Connector → cloud hãng | Credential chỉ đọc; rate limiter theo endpoint |
| CD-08 | Z7 → Z5/Z6 | HTTPS 443 | Người dùng → cloud | WAF, rate limit, OIDC |
| CD-09 | Bastion → Z2 (qua tunnel do edge mở) | SSH/HTTPS trong tunnel | **Edge mở outbound** | Theo yêu cầu, ≤ 2 h, chủ site cho phép, ghi phiên (P1) |

Quy tắc thêm [PROPOSAL]:
- Công cụ engineering của installer chỉ được nối OT LAN khi edge ở `MAINTENANCE` ([§12](#s12)); nếu edge phát hiện master Modbus khác (phản hồi lệch, thiết bị báo bận) khi đang `REMOTE` → cảnh báo Cao `OT.SECOND_MASTER_SUSPECTED` và chặn ghi (ABU-16).
- Phát hiện thiết bị lạ trên OT LAN bằng giám sát thụ động (ARP/DHCP) là P1 (NFR-OBS-006).

---

<a id="s11"></a>
## 11. Chuỗi an toàn lệnh

Đặc tả chi tiết cho FR-SEC-003…FR-SEC-016, FR-SEC-021, FR-SEC-022, NFR-SEC-004, 008–013, NFR-REL-012. Hợp đồng lệnh (type, envelope, vòng đời) thuộc [07 §8](07-device-integration.md); máy trạng thái `DispatchCommand` thuộc [05 §11.2](05-domain-model.html#s11-sm1). Mục này quy định **các bước kiểm soát** và yêu cầu cho từng bước.

### 11.1 Tổng quan chuỗi

```
[Người/dịch vụ] ─S1 xác thực─► [Command API] ─S2 RBAC+PDP─► ─S3 kiểm SOE/trạng thái site─► ─S4 phân hạng/duyệt─►
 ─S5 Governor/rate─► ─S6 TTL─► ─S7 idempotency─► [Signer/KMS] ─S8 ký JWS + seq─► [Dispatcher] ─S9 giao MQTT─►
 [Edge] ─S10 kiểm envelope─► ─S11 arbiter + limit chain─► ─S12 ghi thiết bị + làm mới watchdog─►
 ─S13 ack/timeout─► ─S14 readback + theo dõi đáp ứng─► ─S15 hết hạn/hoàn nguyên─► ─S16 audit + đối soát─►
```

Nguyên tắc: **lớp sau không tin lớp trước** (BR-SEC-05). Bước nào lỗi thì dừng ở trạng thái an toàn và ghi lý do; không có đường tắt bỏ qua bước (kể cả cho `PLATFORM_ADMIN`). [PROPOSAL]

### 11.2 Bảng các bước

| Bước | Nơi | Kiểm soát | Lỗi → trạng thái | Yêu cầu |
|---|---|---|---|---|
| S1 Xác thực | Cloud | Token OIDC hợp lệ; phiên MFA; step-up cho C2/C3 | `DENIED: AUTH` / `STEP_UP_REQUIRED` | NFR-SEC-005 |
| S2 Phân quyền | Cloud (PDP) | RBAC theo cây + PDP-01…PDP-15 ([§5.3](#s5)); lưu `pdp_decision_id` | `DENIED: <lý do>` | NFR-SEC-006 |
| S3 Kiểm vùng an toàn | Cloud | Tham số so với `M1StaticLimits` (site M1, [§11.3a](#s11-m1)) hoặc SOE (site M2) **đang hiệu lực trên edge**; type có trong `capability_profile`; thiết bị `VERIFIED_*`; `requires_native_fallback`; Gate | `DENIED: OUT_OF_SOE` / `DEVICE_NOT_ELIGIBLE` / `GATE` | NFR-SEC-009 |
| S4 Phân hạng & duyệt | Cloud | Hạng hiệu lực = max(tối thiểu, ngữ cảnh); C2 lý do; C3 hai người ([§5.5](#s5)) | `PENDING_APPROVAL` → `APPROVAL_REJECTED` / `APPROVAL_EXPIRED` | NFR-SEC-008 |
| S5 Ngân sách đội | Cloud (Governor) | M1: số site thay đổi mỗi 5 phút và trần site mỗi lần chạy bộ sinh lịch; M2: thêm Σ\|ΔP\| cửa sổ 5 phút theo tenant và nền tảng; rate limit site/user ([§14](#s14)) | Xếp hàng + nâng C3, hoặc `DENIED: RATE_LIMIT` | NFR-SEC-012 |
| S6 Hạn | Cloud | `valid_from`, `expires_at` bắt buộc ≤ hạn tối đa type; `max_latency_ms` | `DENIED: TTL` | NFR-SEC-011 |
| S7 Idempotency | Cloud | `Idempotency-Key` trên POST → một `command_id` (UUID v7) duy nhất; gửi lại cùng key trả lệnh cũ | Trả trạng thái lệnh cũ | NFR-SEC-011 |
| S8 Ký | Signer (KMS) | Signer chỉ ký lệnh ở `AUTHORIZED` có `pdp_decision_id` (và `approval_ref` nếu C3) đọc lại từ DB; gán `seq`; JWS ES256 trên JCS | Không ký → không gửi; KMS lỗi → fail-closed | NFR-SEC-004 |
| S9 Giao | Dispatcher, broker | QoS 1, không retained, Message Expiry; retry chỉ khi còn hạn, backoff mũ; không gửi lại sau `expires_at` | `UNDELIVERED` | NFR-SEC-011, NFR-REL-012 |
| S10 Kiểm tại edge | Edge | Thứ tự 10 bước của [07 §8.7](07-device-integration.md): chữ ký/`kid` → đích → đồng hồ → hạn/độ trễ → `command_id`/`seq` → kill switch/`control_enabled` → interlock → capability/verified/fallback → SOE/limits (site M1: `M1StaticLimits`, [§11.3a](#s11-m1)) → mức arbiter | `REJECTED_{INVALID, STALE, REPLAY, INTERLOCK:<IL>, UNSUPPORTED, OUT_OF_LIMIT, LOWER_PRIORITY}` | NFR-SEC-004, 010, 011 |
| S11 Phân xử | Edge | Arbiter 12 mức, mô hình "thu hẹp khoảng"; kẹp theo CCL/DCL hiện tại, SOE, POC, ramp; ghi `ARBITER_REASON` | `APPLIED_CLAMPED` (khi kẹp động) | K §6 #16 |
| S12 Ghi thiết bị | Edge driver | Chuỗi ghi theo driver (ví dụ chế độ remote rồi setpoint); `min_write_interval`; ghi reversion timeout/heartbeat cùng setpoint | `FAILED_DEVICE_EXCEPTION` | NFR-REL-002 |
| S13 Ack/timeout | Edge → cloud | Ack ký bằng khóa edge cho mỗi chuyển trạng thái; cloud chờ `RECEIVED` trong `max_latency_ms`; readback timeout theo type | Cloud: `UNDELIVERED`; edge: `FAILED_TIMEOUT` | NFR-SEC-004 |
| S14 Kiểm chứng | Edge | Readback trong dung sai → `APPLIED`; theo dõi đáp ứng vật lý suốt hiệu lực → `tracking_state` ([07 §8.5](07-device-integration.md)) | `FAILED_NO_EFFECT`; cảnh báo `CTRL.TRACKING_DEVIATION` | FR-SEC-009 |
| S15 Hết hạn | Edge | Tại `expires_at`: thực hiện `on_expiry` (mặc định `REVERT_DEFAULT`) → `EXPIRED` → `COMPLETED` | — | NFR-SEC-011 |
| S16 Audit & đối soát | Cloud + edge | Mọi chuyển trạng thái vào audit (hash chain); sau reconnect edge báo lệnh đang hiệu lực + config version + `remote_control_suspended`/`remote_control_state_version` (+ phiên bản giới hạn tĩnh M1/SOE); cloud đối soát ≤ 60 s; edge chưa nối lại lịch cloud trước khi khớp trạng thái tạm ngưng ([§14.4](#s14)) | Cảnh báo `CTRL.STATE_MISMATCH` | NFR-SEC-015, NFR-REL-012 |

### 11.3 Vùng vận hành an toàn (SOE)

SOE (`SafeOperatingEnvelope@version`, F-BESS-08, FR-BESS-007) là tài liệu cấu hình theo site: `SITE_ENGINEER` đề xuất → `CONTROL_SUPERVISOR` (khác người) duyệt C3 → ký bằng khóa cấu hình → đẩy xuống edge → edge báo `ACTIVE_ON_EDGE`. Lệnh ngoài SOE tĩnh bị từ chối, không kẹp im lặng ở cloud; edge kẹp và báo `APPLIED_CLAMPED` chỉ cho giới hạn động (CCL/DCL, POC). [PROPOSAL]

| Tham số SOE | Đơn vị (hợp đồng edge) | Ví dụ mặc định | Nguồn giá trị |
|---|---|---|---|
| `p_ess_discharge_max_w`, `p_ess_charge_max_w` | W | ≤ công suất định mức PCS × hệ số thiết kế | Datasheet PCS + thiết kế |
| `soc_min_eff_pct`, `soc_max_eff_pct` | % | 10 / 95 | Hãng pin, điều kiện bảo hành |
| `soc_backup_reserve_pct` | % | 30 (site có tải ưu tiên) | Chủ site |
| `export_limit_w`, `import_cap_w` (trần cứng của SOE; cấu hình lưới site phải ≤) | W | 0 / ≤ công suất MBA, hợp đồng | Hợp đồng đấu nối, thiết kế |
| `ramp_max_w_per_s` | W/s | 10% P định mức/s | [UNKNOWN] grid code VN cho C&I (Q-I-10) |
| `delta_p_max_per_cmd_w` | W | 50% P định mức | Chống bước nhảy lớn |
| `mode_change_min_interval_s` | s | 300 | Chống dao động, mòn contactor |
| `cycles_per_day_max` | EFC | 1,5 | Bảo hành pin |
| `ev_site_cap_w`, `ev_min_a` | W, A | — / 6 A | Thiết kế; [INFERENCE] mức phổ biến IEC 61851 |
| `allowed_command_types` | danh sách | Theo `capability_profile` | Driver |
| `t_stale_bms_s`, `t_stale_poc_s` | s | 5 / 3 | [04 §2](04-business-requirements.md) |
| `plan_expiry_fallback_h` | h | 48 | K §6 #17 |
| `hold_last_allowed_types` | danh sách | rỗng (mặc định chỉ `REVERT_DEFAULT`) | — |

Mọi thay đổi SOE được thông báo cho chủ site; edge so SOE nhận được với chữ ký và từ chối nếu `version` thấp hơn bản đang áp (ABU-02). Tên trường SOE dùng đúng tên của [05 §11](05-domain-model.html#s11) (`p_ess_discharge_max_w`, `p_ess_charge_max_w`, …) vì chúng được kiểm trong cấu hình ký và trong quy tắc PDP; đổi tên là thay đổi hợp đồng có version.

<a id="s11-m1"></a>
#### 11.3a Giới hạn tĩnh Gate M1 (`M1StaticLimits`) — tập con bắt buộc của SOE

**Vấn đề**: ở Gate M1 chưa có SOE đầy đủ (commissioning SOE là bước của M2), nhưng M1 đã ghi tham số xuống thiết bị (`SET_PV_LIMIT`, `SET_SOC_RESERVE`, `SET_EXPORT_LIMIT`/`SET_IMPORT_LIMIT` tạm thời, `SET_ESS_MODE`, lịch native, cấu hình lưới C3). Không có trần cứng thì hoặc PDP-08 từ chối mọi ghi M1, hoặc ghi M1 không được kiểm theo giới hạn vật lý/hợp đồng. **Quyết định** [PROPOSAL]: mỗi site có `control_enabled = true` ở M1 phải có tài liệu `M1StaticLimits@version` — chính là **tập con bắt buộc của SOE**, cùng lược đồ, cùng tên trường, cùng cơ chế ký/version/chống rollback; khi lên M2, SOE đầy đủ là phiên bản sau của cùng tài liệu (không phải tài liệu thứ hai), nên không có hai nguồn giới hạn song song.

| Trường (tên như SOE) | Bắt buộc ở M1 | Nguồn giá trị |
|---|---|---|
| `export_limit_w` (trần cứng xuất) | Có | Hợp đồng đấu nối/thỏa thuận với điện lực; site zero-export = 0 |
| `import_cap_w` (trần cứng nhập) | Có | min(công suất MBA × hệ số thiết kế, công suất hợp đồng) |
| `soc_backup_reserve_pct` (sàn), `soc_min_eff_pct`, `soc_max_eff_pct` | Có nếu site có BESS | Chủ site; hãng pin |
| `pv_limit_min_w`, `pv_limit_max_w` | Có nếu M1 ghi `SET_PV_LIMIT` | Định mức inverter; giới hạn xuất |
| `allowed_command_types` | Có | `capability_profile` ∩ danh sách type Gate M1 ([07 §8.1](07-device-integration.md)); type M2 (`SET_ESS_P`, `SET_EV_LIMIT`…) không được có |
| `mode_change_min_interval_s` | Có | Mặc định 300 |
| `p_ess_discharge_max_w`, `p_ess_charge_max_w`, `ramp_max_w_per_s`, `delta_p_max_per_cmd_w` | Không (bắt buộc từ M2) | — |

- **Phê duyệt**: lập trong commissioning M1 bởi `SITE_ENGINEER`, duyệt C3 bởi `CONTROL_SUPERVISOR` khác người (PDP-12), đính kèm bằng chứng (trang hợp đồng đấu nối, nhãn MBA); ký bằng khóa cấu hình; edge báo `ACTIVE_ON_EDGE`. Bật `control_enabled` (C3) bị chặn nếu chưa có bản `ACTIVE_ON_EDGE`.
- **Kiểm**: PDP-08 và S3 ở cloud, bước 9 "SOE/limits" của chuỗi kiểm edge ([07 §8.7](07-device-integration.md)) dùng `M1StaticLimits` cho site `control_gate = M1` và SOE đầy đủ cho site M2. Cấu hình lưới site (`export_limit_w`, `import_cap_w` trong `SiteGridConfig`) phải ≤ trần cứng tương ứng; ghi tham số native (ví dụ giới hạn xuất của logger) ngoài trần → `DENIED: OUT_OF_SOE` ở cloud, `REJECTED_OUT_OF_LIMIT` ở edge.
- **Không thay bảo vệ**: trần này là kiểm tra phần mềm của ta; bảo vệ native (rơ-le chống phát ngược, BMS) vẫn là lớp 1.
- Kiểm thử: T-NFR-SEC-009-01 (dưới §19.3).

### 11.4 Interlock tại edge

| Mã | Điều kiện | Nguồn tín hiệu | Hành động khi tác động |
|---|---|---|---|
| IL-01 | LOCAL hoặc MAINTENANCE | DI công tắc khóa chìa, hoặc chế độ native đọc được (có biên bản) | Từ chối lệnh cloud; [§12](#s12) |
| IL-02 | E-stop đang tác động / mạch an toàn chưa reset | DI tiếp điểm phụ | Từ chối; hủy lệnh đang hiệu lực; cảnh báo Khẩn cấp |
| IL-03 | BMS lỗi mức bảo vệ hoặc dữ liệu BMS cũ > `t_stale_bms_s` | Modbus/CAN | BESS P = 0 hoặc native |
| IL-04 | Mất `MTR_POC` > `t_stale_poc_s` | Công tơ | BESS P = 0/native; PV về giới hạn native |
| IL-05 | Driver chưa `VERIFIED_*` hoặc `BAD_COMM` | Registry | Từ chối ghi tới thiết bị đó |
| IL-06 | Đồng hồ không `SYNCED` | chrony | Từ chối lệnh có hạn |
| IL-07 | Lệnh `GRID_OPERATOR` hiệu lực xung đột | IEC 104 (P1) | Từ chối lệnh mức thấp hơn |
| IL-08 | PCCC/khói/khí/nhiệt phòng pin báo động | DI/Modbus | Không sạc/xả (P = 0), cảnh báo Khẩn cấp; không tự bỏ khi tín hiệu hết — cần xác nhận tại chỗ |
| IL-09 | Cửa tủ mở / bảo trì | DI | Từ chối; BESS P = 0 |
| IL-10 | Site đang `commissioning` | Registry | Từ chối trừ `COMMISSIONING_TEST` |

Tín hiệu interlock không đọc được (mất DI module, giá trị không hợp lệ) được coi là **đang tác động** (fail-safe). Interlock nào áp dụng cho site được ghi trong biên bản commissioning; site không có tín hiệu PCCC thì IL-08 ghi "không áp dụng" có lý do. [PROPOSAL]

### 11.5 Hạng lệnh

| Hạng | Ví dụ | Yêu cầu |
|---|---|---|
| C0 Thông tin | Đọc, refresh, `dry_run` | Quyền đọc |
| C1 Thường | Áp lịch trong SOE (hoặc giới hạn tĩnh M1, §11.3a); override `SET_ESS_MODE` (`site_strategy`) ≤ 24 h; setpoint ≤ 80% SOE, TTL ≤ 1 h; `SET_EV_LIMIT`; kill switch engage; tắt `control_enabled` | Quyền + phiên MFA |
| C2 Nhạy cảm | Đổi chiến lược mặc định của site (`SiteControlConfig.default_strategy`, cấu hình có version — [04 FR-BESS-004](04-business-requirements.md)); setpoint > 80% SOE; giảm dự phòng SOC; tắt tối ưu; > 5 site/lệnh; ngoài giờ hành chính; `SET_EXPORT_LIMIT`/`SET_IMPORT_LIMIT` tạm thời; `COMMISSIONING_TEST`; mở tunnel hỗ trợ | Step-up ≤ 5 phút + lý do |
| C3 Nguy hiểm | `DEVICE_ON_OFF`; đổi SOE; đổi cấu hình lưới; bật `control_enabled`/Gate M2; `SET_REVERSE_FEED_BLOCK` thủ công; xả/sạc cưỡng bức bỏ qua tối ưu > 30 phút; > 10% MW BESS tenant; reset lỗi từ xa; OTA edge; kill switch release | Hai người khác vai trò, cả hai step-up; cửa sổ duyệt ≤ 15 phút; thông báo chủ site |
| C4 Cấm | Đổi grid code, ngưỡng bảo vệ, cấu hình BMS; bỏ qua interlock; điều khiển/reset E-stop | **Không có API**; chỉ làm tại chỗ bằng công cụ hãng |

Ánh xạ với phân hạng A/B/C/D của H: A → C0, B → C1, C → C2/C3, D → C4 (K R-14).

### 11.6 Hạn, độ trễ và timeout

| Type | `expires_at` tối đa (mặc định) | `max_latency_ms` | Timeout readback | Sau hạn |
|---|---|---|---|---|
| `SET_ESS_P`, `SET_PV_LIMIT`, `SET_EXPORT_LIMIT`/`SET_IMPORT_LIMIT` tạm thời | 1 h (15 phút) | 10 000 | 10 s (hoặc theo `capability_profile`) | `REVERT_DEFAULT` |
| `SET_ESS_MODE` | 24 h | 30 000 | 30 s | Chiến lược mặc định |
| `SET_SOC_RESERVE` | 24 h (về giá trị cấu hình) | 30 000 | 30 s | Giá trị cấu hình |
| `APPLY_SCHEDULE` | 7 ngày (horizon ≥ 48 h) | 300 000 | — (ack theo slot) | Chiến lược mặc định |
| `SET_EV_LIMIT` (P1) | 1 h (15 phút) | 10 000 | 30 s | TxDefaultProfile an toàn |
| Lệnh C3 sau duyệt | ≤ 30 phút sau duyệt | 10 000 | 30 s | Hủy |
| `REMOTE_CONTROL_SUSPEND` | Không hết hạn (trạng thái) — gỡ bằng `RESUME` C3. Nguồn sự thật là tin trạng thái ký, retained trên `down/config` ([§14.4](#s14)); lệnh trên `down/cmd` chỉ là đường nhanh | 60 000 | — | — |
| `GRID_OPERATOR` (IEC 104, P1) | Theo điều độ [UNKNOWN] | Cục bộ | Theo QĐ 1570 [UNKNOWN] | Theo điều độ |

Nguồn số: [04 §2](04-business-requirements.md), [07 §8.2](07-device-integration.md); K §6 #21.

### 11.7 Idempotency, thứ tự và chống phát lại

- `command_id` (UUID v7) là khóa idempotency ở edge: nhận trùng → trả trạng thái cũ, không thực thi lại; bảng đã thấy giữ tới `expires_at + 24 h` trong lưu trữ bền của edge. [PROPOSAL]
- `seq` đơn điệu theo `(site, signer kid)`: Signer cấp `seq` từ sequence DB bền; edge lưu `last_seq` bền (fsync) **trước** khi chấp nhận; `seq ≤ last_seq` → `REJECTED_REPLAY` + cảnh báo bảo mật. Khoảng trống `seq` được phép (lệnh bị hủy trước khi gửi). Khi thay edge hoặc xoay khóa: cấu hình đã ký mang `seq_floor` theo `kid`. [PROPOSAL]
- Không tự gửi lại sau `expires_at`; sau reconnect cloud **không** gửi lại lệnh tay đã hết hạn; lịch còn hạn được gửi lại một lần nếu edge báo chưa có (NFR-REL-012). [PROPOSAL]

### 11.8 Định dạng chữ ký (chốt câu hỏi mở của 07 §8.2)

| Hạng mục | Quyết định | Nhãn |
|---|---|---|
| Chuẩn hóa | JCS (RFC 8785) trên envelope **trừ** trường `signature`; `kid` nằm trong phần được ký | [PROPOSAL] |
| Chữ ký | JWS compact, `alg = ES256` (P-256); header chỉ gồm `alg`, `kid`, `typ = "ems-cmd+jws"`; payload là chuỗi JCS (base64url) | [PROPOSAL] |
| Allow-list | Edge chỉ chấp nhận `ES256` (và `EdDSA` nếu ADR chọn); từ chối `none`, HS*, RS* | [PROPOSAL] |
| Trường bắt buộc trong phần ký | `command_id`, `seq`, `type`, `params`, `target`, `source`, `danger_class`, `approval_ref` (C3), `valid_from`, `expires_at`, `sent_at`, `max_latency_ms`, `on_expiry`, `kid` | [PROPOSAL] |
| Ack | `edge_sig` JWS ES256 bằng khóa edge trên JCS của ack; cloud kiểm trước khi chuyển trạng thái | [PROPOSAL] |
| Cấu hình | Cùng cách, khóa cấu hình riêng, `typ = "ems-config+jws"` | [PROPOSAL] |
| Kiểm thử tương tác | Bộ "test vector vàng" (envelope mẫu + chữ ký + kết quả mong đợi, gồm các ca hỏng) dùng chung cho Signer (Java) và edge | [PROPOSAL] |

[INFERENCE] JCS và JWS là đặc tả công khai phổ biến (kiến thức nền); số RFC và edition cần ghi lại khi chốt ADR ở [06](06-system-architecture.html).

### 11.9 Trạng thái lệnh trên UI

UI không cập nhật lạc quan: chỉ hiện "Đã áp dụng" sau `APPLIED`/`APPLIED_CLAMPED`; trước đó hiện "Đang chờ xác nhận" (AC-SEC-13). Từ chối hiện mã lý do dễ hiểu và hướng xử lý (FR-SEC-011). `UNDELIVERED` hiện "Không tới được edge trước khi hết hạn — lệnh không được thực thi". [PROPOSAL; chi tiết ở [09](09-ux-ui-specification.html)]

---

<a id="s12"></a>
## 12. Ưu tiên điều khiển tại chỗ và E-stop

### 12.1 Thứ tự ưu tiên tại edge

Thứ tự 12 mức của K R-07 (mức 1–6 cố định): (1) bảo vệ native · (2) interlock tại chỗ (LOCAL/REMOTE, E-stop, PCCC) · (3) giám sát an toàn edge (dữ liệu cũ, lệnh hết hạn, SOE) · (4) tuân thủ lưới (giới hạn xuất, `GRID_OPERATOR`) · (5) trần nhập vật lý · (6) dự phòng backup · (7) lệnh tay operator · (8) DR/VPP (P2) · (9) peak shaving demand (P1) · (10) cam kết EV (P1) · (11) lịch kinh tế · (12) chiến lược mặc định. Chi tiết dữ liệu ở [07 §3.2](07-device-integration.md), [05 §11.1](05-domain-model.html#s11-arb). Thứ tự này **thay** thứ tự trong ghi chú I §3.7.7.

### 12.2 LOCAL / REMOTE / MAINTENANCE

| Trạng thái | Ý nghĩa | Edge làm | Cloud/UI |
|---|---|---|---|
| `REMOTE` | Cho phép lệnh từ cloud theo PDP | Bình thường | Bình thường |
| `LOCAL` | Người tại chỗ điều khiển (qua HMI hãng hoặc chế độ native) | Từ chối mọi lệnh cloud (IL-01); hủy lệnh tay đang hiệu lực (`CANCELLED`); **không ghi bất kỳ gì xuống thiết bị** kể từ lúc phát hiện LOCAL (kể cả "ghi một lần chế độ an toàn" — người tại chỗ đã nắm quyền, edge không được đè cài đặt của kỹ thuật viên); thiết bị tự về chế độ native qua cơ chế mất-master/watchdog của chính nó (cấu hình sẵn trong commissioning: `revert_timeout_s`, fallback loss-of-master). Thiết bị không có cơ chế này thì phải mang `requires_native_fallback = true` và không bao giờ nhận setpoint cưỡng bức (PDP-09, FR-SEC-016), nên khi LOCAL không có setpoint cưỡng bức nào "treo" lại; vẫn đọc và gửi telemetry; vẫn giám sát an toàn (mức 3) và cảnh báo | Banner "Đang điều khiển tại chỗ"; nút lệnh vô hiệu |
| `MAINTENANCE` | Bảo trì; công cụ engineering có thể cần làm master Modbus | Như LOCAL + **nhả kết nối ghi**; nếu thiết bị chỉ nhận một client (ví dụ Huawei chỉ một client Modbus TCP, [07 IP-03](07-device-integration.md)) thì nhả cả kết nối đọc; telemetry gắn quality `BAD_COMM` (enum tầng 1 của [05 §16](05-domain-model.html)) và khoảng trống có lý do `MAINTENANCE`; không ghi số 0 thay dữ liệu thiếu | Banner "Bảo trì tại chỗ"; cảnh báo kết nối bị chặn theo cha–con |

- **Phần cứng**: site Gate M2 có BESS phải có công tắc khóa chìa nối DI edge, **hoặc** chế độ local/remote của thiết bị native mà edge đọc được, có biên bản commissioning (K §3.8, FR-SEC-010, NFR-SEC-014).
- **Quay lại `REMOTE`**: chỉ bằng thao tác tại chỗ. Edge vào trạng thái khởi động lại kiểu `SAFE_START` (đọc đủ ≥ 2 chu kỳ, đồng hồ hợp lệ) rồi chạy chiến lược mặc định; lịch `APPLY_SCHEDULE` còn hạn được nối lại từ slot hiện tại; lệnh tay đã hủy **không** tự khôi phục. [PROPOSAL]
- Đọc trạng thái công tắc lỗi → coi là `LOCAL` (fail-safe).

### 12.3 E-stop

- E-stop thuộc mạch an toàn cứng của BESS/PCS (cắt contactor/MCCB), **không** đi qua edge hay cloud. EMS chỉ **đọc** trạng thái (IL-02). [PROPOSAL]
- **Không có nút "E-stop từ xa"** trên bất kỳ UI hay API nào (F-BESS-20, C4). Nếu khách cần "dừng từ xa" thì đó là `DEVICE_ON_OFF` (C3, P1) với tên hiển thị "Dừng vận hành từ xa", hoặc `SET_ESS_P = 0` (C1) — không được gọi là E-stop.
- Khi E-stop tác động: edge hủy mọi lệnh đang hiệu lực (`CANCELLED`, lý do `ESTOP`), ghi audit, cảnh báo Khẩn cấp, không ghi gì xuống thiết bị liên quan. Sau khi reset tại chỗ: edge `SAFE_START`, chạy chiến lược mặc định; không tự khôi phục lệnh tay; lịch còn hạn nối lại sau khi BMS/PCS báo sẵn sàng.
- **Reset lỗi/E-stop**: tại chỗ (C4 trên cloud). Reset **lỗi** từ xa (không phải E-stop) chỉ khi hãng cho phép, C3, P2 (F-BESS-17).

### 12.4 HMI cục bộ

Trang trạng thái cục bộ của edge (F-MON-11, P1): LOCAL/REMOTE, interlock đang tác động, `run_mode`, lệnh/lịch đang hiệu lực, cảnh báo, đồng hồ. Đăng nhập bằng tài khoản cục bộ (mật khẩu ngẫu nhiên theo thiết bị, bắt đổi) hoặc token ngắn hạn do cloud cấp khi còn mạng; **chỉ đọc** ở P1 (không phát lệnh từ HMI cục bộ). [PROPOSAL]

---

<a id="s13"></a>
## 13. Hành vi khi mất liên lạc

Đặc tả chi tiết cho NFR-REL-001, 002, 003, 007, 008, 011, 012; F-INT-09, F-INT-28, F-BESS-10, F-SEC-15.

### 13.1 Heartbeat và watchdog

| Đoạn | Cơ chế | Tham số mặc định | Phát hiện | Ghi chú |
|---|---|---|---|---|
| Thiết bị ← edge | Reversion timeout gắn setpoint, heartbeat register, fallback cấu hình sẵn, hoặc watchdog API của controller | `revert_timeout_s` 10–60 s và > 3 chu kỳ ghi của edge; edge làm mới ≤ T/3 | Thiết bị tự hoàn nguyên | Theo từng hãng: [UNKNOWN] (Q-I-07); driver khai báo `watchdog_support`, `revert_timeout_s`; test F-INT-28 |
| Edge (nội bộ) | Watchdog phần cứng | Reset nếu vòng điều khiển treo > 10 s | Reboot → `SAFE_START` | NFR-REL-003 |
| Edge → cloud | MQTT keepalive + `up/state` | 30 s; `OFFLINE` sau 3 lỡ (≈ 90 s); cảnh báo người sau 5 phút | Cloud | NFR-REL-008 |
| Cloud → edge (lệnh) | `expires_at` | Setpoint 15 phút mặc định, ≤ 1 h | Edge | NFR-SEC-011 |
| Cloud → edge (lịch) | Horizon | ≥ 48 h | Edge | NFR-REL-001 |
| Điều độ → edge (P1) | Giám sát liên kết IEC 104 | Theo QĐ 1570 [UNKNOWN] | Edge | NFR-SEC-032 |
| Charger ↔ edge (P1) | Heartbeat OCPP + WebSocket ping | Theo cấu hình charger | Cả hai phía | NFR-SEC-021 |

Mẫu watchdog thường gặp [INFERENCE, kiến thức nền chưa kiểm chứng theo hãng]: SunSpec model 123 có trường thời gian hoàn nguyên (`*_RvrtTms`) và model 704 có trường tương ứng; nhiều PCS có "EMS heartbeat/communication timeout"; SMA có tham số fallback cho giới hạn P từ bên ngoài; OpenEMS Controller Api có `apiTimeout`. Victron ESS Mode 2/3: fallback khi mất master chưa rõ (ghi chú G #17, nguồn cộng đồng, Low–Med). **Không** coi bất kỳ mẫu nào là có trên một model cho tới khi test F-INT-28 đạt.

### 13.2 Bảng chế độ dự phòng theo lớp thiết bị

| Lớp / tình huống | Phát hiện | Hành vi bắt buộc ở thiết bị/native | Hành vi edge | Cloud / UI | Điều kiện Gate M2 |
|---|---|---|---|---|---|
| PCS / `ess_controller` — mất edge (edge treo, mất nguồn, đứt cáp) | Watchdog thiết bị | Về chế độ mặc định đã cấu hình trong commissioning: P = 0 hoặc tự dùng native trong giới hạn | (Edge không chạy) Khi phục hồi: `SAFE_START` | `OFFLINE` sau ≈ 90 s; cảnh báo Cao "Site chạy chế độ dự phòng của thiết bị" | Test rút cáp đạt trong `revert_timeout_s`; nếu không có watchdog → `requires_native_fallback = true`, cấm setpoint P cưỡng bức (FR-SEC-016) |
| BMS — dữ liệu cũ > `t_stale_bms_s` hoặc lỗi | Edge | BMS tự bảo vệ (luôn) | IL-03: BESS P = 0 hoặc native ≤ 2 chu kỳ (NFR-REL-007) | Cảnh báo Cao | Test làm cũ dữ liệu BMS |
| Công tơ POC — mất > `t_stale_poc_s` | Edge | Rơ-le chống phát ngược (nếu có) vẫn bảo vệ | IL-04: BESS P = 0/native; PV về giới hạn native (giới hạn xuất của logger hoặc mức an toàn cấu hình) ≤ 2 chu kỳ | Cảnh báo tuân thủ lưới mức Cao (F-ALM-13) | Test ngắt công tơ POC |
| PV inverter ghi trực tiếp | Watchdog/reversion inverter | Về `WMaxLim` mặc định hoặc giới hạn native an toàn đã cấu hình (với site zero-export: giới hạn native = 0 xuất ở logger/công tơ hãng) | Không ghi giới hạn cưỡng bức nếu không có reversion; khi đó dùng logger/native làm chủ vòng | Cảnh báo | Như PCS |
| PV qua logger hãng (`control_owner = NATIVE`) | Logger | Logger tiếp tục vòng zero-export/giới hạn xuất native | Chỉ đặt tham số và giám sát; mất edge không ảnh hưởng vòng native | — | Readback tham số; test giới hạn xuất (F-INT-27) |
| Hybrid inverter (pin LV) | Theo hãng | Chế độ "third-party/remote" có timeout [UNKNOWN theo hãng] | Chỉ đổi giữa chế độ native an toàn nếu không có timeout | Cảnh báo | Như PCS |
| Charger EV — mất edge (edge là CSMS, P1) | Charger | Áp TxDefaultProfile/ChargePointMaxProfile an toàn đã cài sẵn (ví dụ giới hạn site/số charger) | Luôn cài profile mặc định an toàn trước khi điều khiển động | Cảnh báo | Test ngắt WebSocket. [FACT] OCPP 1.6 có ChargePointMaxProfile, TxDefaultProfile, TxProfile; với Easee, TxDefaultProfile 0 A có thể đè TxProfile 20 A — https://developer.easee.com/docs/ocpp-smart-charging ; https://www.bender.de/docs/charge-controller/OCPP/ocpp-smart-charging/ (qua kết quả tìm kiếm, ghi chú E): hành vi khác nhau theo hãng, phải test từng model |
| Charger EV qua CSMS của CPO (edge gọi API CPO, P1) | Edge (lỗi API/timeout) / cloud (90 s) | CSMS của CPO áp profile mặc định an toàn đã ghi nhận khi commissioning khi giới hạn hết hạn | Không gửi lại giới hạn cũ; giới hạn đã gửi tự hết hạn (TTL ≤ `expires_at`); giữ trần nhập bằng BESS/PV theo arbiter | Cảnh báo Cao `EV_CPO_LINK_LOST` | Test mock CPO: CPO không trả lời, trả sai, mất edge↔CPO (T-FR-EV-004) |
| Genset | — | Controller genset tự quản | Chỉ đọc ở MVP; start/stop là P2 | — | — |
| Rơ-le / DO của edge | Edge reboot | DO về trạng thái mất điện (de-energized) phải là trạng thái an toàn — thiết kế đấu dây quy định | Không dùng DO thay bảo vệ | — | Kiểm tra sơ đồ đấu DO trong commissioning |
| Cảm biến bức xạ/thời tiết | Edge | — | Không ảnh hưởng điều khiển; PR = N/A khi thiếu POA; quality `FROZEN`/`BAD_*` | Cảnh báo Trung bình | — |
| Liên kết IEC 104 (P1) | Edge | — | Giữ giới hạn `GRID_OPERATOR` gần nhất đang hiệu lực; khi hết hạn theo quy định điều độ → [UNKNOWN]. Đề xuất tạm: giữ giá trị **chặt nhất** cho tới khi có lệnh gỡ hoặc kỹ sư xác nhận | Cảnh báo Cao | Theo yêu cầu điện lực (Q-I-03) |
| Edge ↔ cloud | Cloud (90 s) / edge (keepalive) | — | Tiếp tục vòng cục bộ; lệnh tay chạy tới `expires_at` rồi `on_expiry`; lịch đã nhận (≥ 48 h); hết lịch → chiến lược mặc định; store-and-forward (≥ 7 ngày cứng, mục tiêu 30 ngày) | `OFFLINE`; cảnh báo sau 5 phút; UI hiện "dữ liệu tới …" | Game day chặn broker |
| Edge mất đồng hồ (`UNSYNCED`) | Edge | — | IL-06 từ chối lệnh có hạn; lịch đang chạy tiếp theo RTC nếu `DEGRADED` (< 1 s), dừng lịch và chạy mặc định nếu `UNSYNCED` | Cảnh báo Cao | Test lệch đồng hồ |
| Chứng chỉ edge hết hạn | Edge/broker | — | Như mất cloud; gia hạn qua IDevID (§9.2) | Cảnh báo trước 14 ngày | Test |
| Cloud sập toàn phần / DR | Ngoài | — | Như mất cloud | Sau khôi phục: không thi hành lại lệnh hết hạn; đối soát; mở lại control plane là C3 ([§16.4](#s16)) | Diễn tập |

### 13.3 Chiến lược mặc định của site

Chiến lược mặc định (`default_strategy`, mức 12) là cấu hình có version tách khỏi override `SET_ESS_MODE` ([04 §8](04-business-requirements.md)). Ràng buộc [PROPOSAL]:
- Không phụ thuộc cloud và dự báo.
- Ví dụ an toàn: tự dùng (self-consumption) + giới hạn xuất + giữ `soc_backup_reserve_pct`; không sạc từ lưới trừ khi cấu hình cho phép và nằm trong trần nhập.
- Được test trong commissioning (F-INT-28) như một trạng thái thực, không chỉ trên giấy.

### 13.4 Chế độ chạy của edge

`run_mode ∈ {SAFE_START, NORMAL, FALLBACK_SCHEDULE, DEFAULT_STRATEGY, NATIVE_SAFE}` ([05 §6](05-domain-model.html#s6)). Chuyển trạng thái là sự kiện audit và hiển thị ở header site.

| Từ → tới | Điều kiện |
|---|---|
| (khởi động) → `SAFE_START` | Mọi lần khởi động/reboot/quay lại REMOTE/sau E-stop |
| `SAFE_START` → `NORMAL` | ≥ 2 chu kỳ đọc hợp lệ của điểm điều khiển, đồng hồ `SYNCED`/`DEGRADED`, cấu hình ký hợp lệ, interlock không tác động |
| `NORMAL` → `FALLBACK_SCHEDULE` | Mất cloud, còn lịch hợp lệ |
| `FALLBACK_SCHEDULE` → `DEFAULT_STRATEGY` | Hết lịch hoặc lịch không hợp lệ |
| bất kỳ → `NATIVE_SAFE` | IL-03/IL-04/IL-08/IL-09, mất `MTR_POC`, BMS cũ, kill switch, LOCAL/MAINTENANCE (với LOCAL/MAINTENANCE: edge không ghi gì xuống thiết bị, §12.2) |
| `NATIVE_SAFE` → `SAFE_START` | Điều kiện gây ra đã hết (với IL-08: cần xác nhận tại chỗ) |

---

<a id="s14"></a>
## 14. Giới hạn bán kính tác động ở cấp đội

Đặc tả chi tiết cho FR-SEC-012, FR-SEC-013, FR-SEC-022, NFR-SEC-012, NFR-SEC-013, NFR-SEC-020, NFR-REL-010.

### 14.1 Vì sao

**Phạm vi Gate**: giới hạn bán kính tác động áp dụng **từ Gate M1**, không đợi M2 — ở M1 cloud đã ghi tới nhiều site cùng lúc (bộ sinh lịch tầng 2 đẩy lịch native như principal dịch vụ, `SET_ESS_MODE`, `SET_PV_LIMIT`, `SET_SOC_RESERVE`, cấu hình lưới, OTA, `CONFIG_PUSH`). Ở M1 bắt buộc: C3 hai người (NFR-SEC-008), kill switch (NFR-SEC-013), Governor biến thể đếm (NFR-SEC-012 M1), toàn vẹn thời gian edge (NFR-SEC-028, vì kiểm hạn tại edge phụ thuộc đồng hồ). Phần chỉ có nghĩa khi edge làm chủ vòng (Governor ΔP, nâng hạng PDP-04/05 theo MW) bật ở M2 (13 CF-28/D-03).

[FACT] Sự cố 11/2024 (inverter ở nhiều nước bị vô hiệu hóa từ xa do tranh chấp thương mại, nguồn không nêu hãng — Defense News, §2.5) và [FACT] Forescout "SUN:DOWN" (27/3/2025): 46 lỗ hổng mới ở sản phẩm Sungrow, Growatt, SMA (đã vá); 80% lỗ hổng hệ mặt trời công bố trong 3 năm trước là high/critical — https://forescout.com/press-releases/forescout-vedere-labs-uncovers-severe-systemic-security-risks-in-global-solar-power-infrastructure (nghiên cứu FusionSolar trước). [INFERENCE] Mẫu nguy hiểm nhất là "một tài khoản/khóa/đường cập nhật có quyền ghi → tác động đồng thời nhiều site". EMS của ta tạo đúng loại bề mặt này, nên phải giới hạn tác động ở nhiều tầng.

### 14.2 Các tầng giới hạn

| Tầng | Giới hạn mặc định [PROPOSAL] | Cơ chế | Mã |
|---|---|---|---|
| Thiết bị | ≤ 1 setpoint/2 s từ edge; `min_write_interval`; ghi NVM theo khuyến cáo hãng | Driver | FR-SEC-022, BR-INT-04 |
| Lệnh | `delta_p_max_per_cmd_w`; `ramp_max_w_per_s` | SOE tại edge | NFR-SEC-009 |
| Site | ≤ 6 lệnh tay/phút; ≤ 12 đổi chế độ/giờ; `mode_change_min_interval_s` 300 | PDP + edge | FR-SEC-022 |
| Người dùng | ≤ 30 lệnh/10 phút; > 5 site/lệnh → C2; > 10% MW BESS tenant → C3 | PDP | FR-SEC-022 |
| API client | Mặc định 0 lệnh; P2: C1 trong SOE, chịu Governor | OAuth scope + PDP | FR-SEC-026 |
| Tenant / nền tảng — **biến thể M1** (đếm, không cần mô hình ΔP) | Mỗi cửa sổ 5 phút: ≤ 10 site/tenant và ≤ 50 site/nền tảng nhận thay đổi ghi (lệnh native, lịch native, `CONFIG_PUSH`, cấu hình lưới); **mỗi lần chạy bộ sinh lịch** đổi lịch của ≤ 20 site (hoặc ≤ 20% số site của tenant, lấy số nhỏ hơn), phần còn lại xếp đợt sau và trải jitter 0–300 s; vượt → dừng đợt, cảnh báo Cao, cần `plan.approve` (người) để tiếp tục; lệnh an toàn hóa miễn trừ (PDP-15). Áp dụng từ Gate M1 cho mọi principal (người, `svc:scheduler-*`, `svc-config-*`) | Governor (chế độ đếm) dùng chung sổ cái | NFR-SEC-012 (M1) |
| Tenant | Σ\|ΔP\| được lệnh trong 5 phút ≤ 20% MW BESS của tenant (hoặc trần tuyệt đối `max_delta_p_w`); vượt → xếp hàng + C3 | **Fleet Dispatch Governor** | NFR-SEC-012 |
| Nền tảng | Σ\|ΔP\| mọi tenant trong 5 phút ≤ 5% tổng MW BESS quản lý; lệnh đồng loạt trải jitter 0–300 s (trừ điều độ và lệnh an toàn hóa) | Governor toàn cục | NFR-SEC-012 |
| Bộ sinh lịch | Lịch mới không đổi quá 30% tổng năng lượng xả của tenant trong một slot so với lịch trước, nếu không có sự kiện giải thích (biểu giá mới, sự cố) → cần `plan.approve` | Validator kế hoạch ([08](08-energy-optimization.md)) | X-I-03 |
| Cấu hình / driver | Thay đổi driver map, SOE, cấu hình lưới áp theo đợt (≤ 10 site đợt đầu, chờ 24 h) khi áp hàng loạt | Config rollout | NFR-SEC-031 (mới) |
| OTA edge | Canary 1% → 10% → 100%, chờ ≥ 24 h mỗi đợt, tự dừng khi tỷ lệ lỗi health check > 2% hoặc bất kỳ sự kiện an toàn mới | Pipeline OTA | NFR-SEC-020 |
| Kill switch | Site / tenant / nền tảng; engage C1, release C3; lan truyền ≤ 60 s tới mọi edge online | `RemoteControlSuspension` | NFR-SEC-013, NFR-REL-010 |

### 14.3 Thuật toán Governor

- **Định nghĩa ΔP của một lệnh** [PROPOSAL]: `|P_new − P_effective_now|` tại thiết bị đích, cộng trên các thiết bị đích. Với `APPLY_SCHEDULE`: max theo slot của Σ\|P_slot_new − P_slot_prev\| trong 5 phút đầu tiên của mỗi slot bị đổi (lịch thay đổi slot tương lai được tính khi slot tới gần, cửa sổ trượt). Với `SET_ESS_MODE`: ΔP ước tính = công suất định mức PCS × hệ số theo bảng chuyển chế độ (cấu hình; mặc định 1,0 — thận trọng).
- **Sổ cái**: `FleetDispatchLedger(scope, window_start, sum_abs_delta_p_w)` cửa sổ trượt 300 s ([05 §11](05-domain-model.html#s11)). Kiểm và ghi trong cùng transaction với `AUTHORIZED` để tránh đua.
- **Miễn trừ**: lệnh an toàn hóa (về P = 0, kill switch, tắt điều khiển, `REVERT`) và lệnh `GRID_OPERATOR` không tiêu ngân sách (PDP-15). [PROPOSAL; cần mô phỏng vì "về 0" đồng loạt cũng là bước nhảy lớn — Q-I-14]
- **Vượt ngân sách**: lệnh vào hàng đợi `PENDING_APPROVAL` (C3) kèm thông tin "vượt ngân sách đội X kW"; bộ sinh lịch tự trải slot (jitter) thay vì xin duyệt nếu cách trải đủ đưa về trong ngân sách.
- **Biến thể M1**: sổ cái thêm `site_count` theo `(scope, window_start)`; mỗi lần chạy bộ sinh lịch có `run_id` và trần `max_sites_per_run`; Signer từ chối ký lệnh/lịch/cấu hình mang `run_id` đã vượt trần (lớp sau không tin lớp trước). Ngưỡng 10/50/20 là đề xuất, chỉnh sau mô phỏng (Q-I-14). Biến thể ΔP được bật thêm khi site đầu tiên lên M2; biến thể đếm vẫn giữ.
- Ngưỡng 20%/5% là **đề xuất cần mô phỏng** (K §6 #30, Q-I-14). Ở quy mô MVP (vài MW), ngân sách tuyệt đối có thể quan trọng hơn %.

### 14.4 Kill switch

| Thuộc tính | Đặc tả |
|---|---|
| Phạm vi | `SITE`, `TENANT`, `PLATFORM` (`RemoteControlSuspension`, [05 §11](05-domain-model.html#s11)) |
| Engage | C1, không cần step-up, quyền theo [§5.4](#s5); có lý do (tự do) |
| Gate | **Bắt buộc từ Gate M1** (13 CF-28/D-03): ở M1 cloud đã ghi xuống nhiều site (lịch native tầng 2, `SET_ESS_MODE`, `SET_PV_LIMIT`, `SET_SOC_RESERVE`, cấu hình lưới, `CONFIG_PUSH`, OTA) |
| Hiệu lực | Cloud: PDP chặn mọi lệnh mới trong phạm vi ngay lập tức; Dispatcher hủy lệnh chưa gửi; **bộ sinh lịch dừng đẩy lịch native và lịch edge**, pipeline `CONFIG_PUSH`/rollout cấu hình và OTA tạm dừng trong phạm vi (trừ tin trạng thái tạm ngưng và cấu hình "an toàn hóa" do C3 duyệt). Edge: nhận lệnh ký `REMOTE_CONTROL_SUSPEND` (C1, không hết hạn), đặt `remote_control_suspended = true`, hủy lệnh tay, **dừng lịch cloud** và chạy chiến lược mặc định cục bộ; vòng an toàn và tuân thủ lưới vẫn chạy |
| Mang trạng thái (không phải lệnh có hạn) | Trạng thái tạm ngưng là **tin trạng thái ký, có version, retained** trên `down/config` (`type = REMOTE_CONTROL_STATE`, `{scope, suspended, suspension_id, state_version, issued_at}`, ký bằng khóa cấu hình, `typ = "ems-config+jws"`), đồng thời được đưa vào `EdgeConfigVersion` đã ký kế tiếp. Không có `expires_at`: trạng thái chỉ đổi khi có bản `state_version` cao hơn (engage hoặc `RESUME` C3). Edge lưu bền (fsync) và từ chối bản có `state_version` thấp hơn (chống rollback, tương tự ABU-02). Lệnh `REMOTE_CONTROL_SUSPEND` trên `down/cmd` chỉ là đường nhanh cho edge online, không thay trạng thái retained |
| Edge offline lúc engage | Cloud chặn lệnh mới ngay; trạng thái retained chờ sẵn ở broker **không hết hạn**. Khi reconnect (dù offline bao lâu): edge **trước khi chạy bất kỳ slot lịch cloud nào** phải nhận và so trạng thái tạm ngưng retained với bản lưu bền; trong lúc chưa nhận được (timeout 60 s sau khi kết nối), edge giữ `DEFAULT_STRATEGY` thay vì nối lại `APPLY_SCHEDULE`. Nếu `suspended = true` → hủy lịch cloud đã lưu, chạy chiến lược mặc định. Trong thời gian offline, edge không biết về engage nên tiếp tục lịch đã nhận (≤ 7 ngày) — đây là giới hạn vốn có, được ghi rõ ở rủi ro §21.3 và giảm bằng hạn lịch ngắn nhất có thể |
| Đối soát | S16: sau reconnect edge báo `remote_control_state_version` + `suspended`; cloud so với `RemoteControlSuspension` hiện hành; lệch → gửi lại tin trạng thái, cảnh báo Cao `CTRL.STATE_MISMATCH`, và PDP coi site là `SUSPENDED` cho tới khi khớp |
| Release | C3 hai người; theo phạm vi: site/tenant do CONTROL_SUPERVISOR (+ ORG_ADMIN yêu cầu), nền tảng do hai `PLATFORM_ADMIN`; edge `RESUME` → `SAFE_START` → mặc định cho tới khi có lịch mới |
| Tên hiển thị | "Tạm ngưng điều khiển từ xa"; không dùng chữ "E-stop" |
| Kiểm thử | AC-SEC-08: mọi edge online trong phạm vi báo `REMOTE_CONTROL_SUSPENDED` ≤ 60 s |
| Tự động | Kill switch nền tảng tự engage khi: lộ khóa ký nghi ngờ; failover DR ([§16.4](#s16)); phát hiện số lệnh/ΔP bất thường vượt 5× đường cơ sở trong 5 phút (cảnh báo Khẩn cấp, người xác nhận trong 15 phút hoặc giữ) [PROPOSAL] |

---

<a id="s15"></a>
## 15. Mô hình mối đe dọa và ca lạm dụng

### 15.1 Tài sản cần bảo vệ và tác nhân

| Tài sản | Vì sao quan trọng |
|---|---|
| A1 Khả năng ghi lệnh vật lý (Command API, Signer, khóa ký, kênh `down/cmd`) | Tác động thiết bị, lưới, an toàn người |
| A2 SOE và cấu hình lưới | Nới giới hạn = mở đường cho tác động sai |
| A3 Tính toàn vẹn telemetry (`MTR_POC`, BMS) | Điều khiển sai dựa trên số liệu giả |
| A4 Audit | Bằng chứng tranh chấp bảo hành, hợp đồng, sự cố |
| A5 Dữ liệu tenant (D1–D3) | Bí mật kinh doanh, dữ liệu cá nhân |
| A6 Khả dụng giám sát và cảnh báo | O&M phụ thuộc hằng ngày |
| A7 Chuỗi cung ứng (code, image edge, driver) | Một lần chèn → toàn đội |

| Tác nhân | Năng lực giả định |
|---|---|
| T1 Kẻ tấn công từ Internet | Phishing, dò mật khẩu, khai thác lỗ hổng web/API |
| T2 Insider nền tảng | Quyền vận hành; có thể lạm quyền hoặc bị ép |
| T3 Installer/O&M (cũ hoặc hiện tại) | Quyền hợp lệ trong grant; có mặt tại site |
| T4 Kẻ có truy cập mạng OT/site | Cắm thiết bị vào OT LAN, giả Modbus, chiếm edge vật lý |
| T5 Bên cung cấp (thư viện, image, hãng thiết bị) | Chèn mã; kênh cloud riêng của hãng |
| T6 Tranh chấp thương mại | Bên có quyền hợp lệ cố ý vô hiệu hóa (mẫu sự cố 11/2024) |

### 15.2 STRIDE theo thành phần

| Thành phần | S (giả mạo) | T (sửa đổi) | R (chối bỏ) | I (lộ thông tin) | D (từ chối dịch vụ) | E (leo thang quyền) | Biện pháp chính (yêu cầu) |
|---|---|---|---|---|---|---|---|
| Web/mobile | Phishing tài khoản Operator; giả thông báo có deep-link | XSS/CSRF đổi tham số lệnh | "Không phải tôi ra lệnh" | IDOR xem site tenant khác | Brute force đăng nhập | Viewer gọi API lệnh | WebAuthn/step-up (NFR-SEC-005); CSP, SameSite, CSRF token; audit có `auth_time`/`amr` (NFR-SEC-015); kiểm sở hữu theo ID (NFR-SEC-007); PDP (NFR-SEC-006) |
| IdP | Đánh cắp phiên; khôi phục MFA giả | Sửa cấu hình client OIDC | — | Lộ danh bạ user | IdP sập → không đăng nhập | Admin IdP tự cấp vai trò | Khôi phục MFA ngoài băng; cấu hình IdP dưới IaC có review; vai trò ở DB ứng dụng, không ở IdP; fail-closed cho lệnh (NFR-REL-015) |
| Command API / PDP | Token bị đánh cắp | Sửa `params` giữa đường; sửa chính sách PDP | — | Lộ danh sách site/MW | Flood lệnh | Bỏ qua phê duyệt; client tự nâng ưu tiên | mTLS nội bộ; chính sách PDP có version + review 2 người; không có trường `priority` tự do ([07 §8.2](07-device-integration.md)); rate limit; máy trạng thái duyệt phía server (NFR-SEC-008) |
| Approval | Người yêu cầu tự duyệt bằng tài khoản thứ hai | Sửa nội dung lệnh sau khi duyệt | Chối đã duyệt | — | — | — | SoD theo người + vai trò; hash nội dung lệnh gắn vào `CommandApproval`; Signer so hash trước khi ký; WebAuthn cho người duyệt |
| Command Signer / KMS | Khóa ký bị lộ → lệnh giả hợp lệ | — | — | — | KMS sập → không ra lệnh | Dịch vụ khác gọi Signer | Khóa không xuất; Signer kiểm `AUTHORIZED` + `pdp_decision_id` từ DB; chỉ `svc-command-signer` có quyền KMS; giới hạn tốc độ ký; quy trình lộ khóa ([§8.2](#s8)) |
| MQTT broker | Edge giả | Chèn/sửa message | — | Nghe lén topic | DoS kết nối | Edge subscribe `#` | mTLS + ACL theo `edge_id`; lệnh/cấu hình ký tầng ứng dụng; ack ký; quota (NFR-SEC-003, 004) |
| Ingest / TSDB | Edge gửi dữ liệu cho site khác | Sửa dữ liệu lịch sử | — | Cross-tenant | Bão backfill | Owner bypass RLS | Tenant lấy từ registry, không từ payload; idempotent upsert; RLS FORCE; role tách; backpressure (NFR-REL-016) |
| Audit store | — | Sửa/xóa audit | Xóa dấu vết | Lộ D3 | — | Role app có UPDATE | Append-only, hash chain, neo WORM (P1), kiểm hằng ngày (NFR-SEC-015) |
| Connector cloud hãng | Credential hãng lộ | — | — | Lộ dữ liệu khách | Bị hãng throttle/khóa; đổi chính sách API | Token đọc dùng để ghi | Vault + khóa theo tenant; chỉ đọc mặc định; rate limiter; trạng thái `AUTH_REVOKED` (NFR-SEC-016, 018) |
| Edge (OS, runtime) | Cloud giả (DNS spoof) | Firmware/container độc; sửa cấu hình cục bộ | Ack giả | Lộ credential OT, register map OEM | Treo vòng điều khiển | Root qua UI cục bộ/SSH | Pin CA endpoint; secure boot + OTA ký (NFR-SEC-020); cấu hình ký; ack ký; watchdog HW (NFR-REL-003); không mật khẩu mặc định chung (NFR-SEC-027); disk mã hóa; SSH tắt mặc định, chỉ qua tunnel (NFR-SEC-022) |
| OT LAN (Modbus/CAN) | Master Modbus thứ hai; công tơ giả | Ghi thanh ghi trực tiếp; giả phản hồi đọc | — | Sniff | Bão gói, chiếm kết nối duy nhất | — | Edge là master duy nhất; cô lập mạng (NFR-SEC-017); kiểm chéo cân bằng năng lượng; phát hiện master thứ hai; thiết bị lạ (P1) |
| Kênh IEC 104 (P1) | Master giả | Lệnh giả | — | — | Flood | — | Conduit riêng, allow-list IP, chỉ type đã cấu hình; IEC 62351 nếu điện lực yêu cầu (NFR-SEC-032) |
| Charger OCPP (P1) | Charger giả | Sửa MeterValues | — | Lộ idTag | DoS | — | Security Profile ≥ 2, mục tiêu 3; idTag băm (NFR-SEC-021) |
| CI/CD, chuỗi cung ứng | Package độc (typosquat) | Build bị chèn | — | Lộ secret CI | — | Pipeline tự deploy control plane | Pin dependency + lockfile; SBOM; ký artifact; review 2 người cho control plane và driver; secret CI ngắn hạn (NFR-SEC-024) |
| Bộ sinh lịch / optimizer | — | Đầu độc dự báo/biểu giá → lịch xấu | — | — | Optimizer sập | — | Validator kế hoạch; SOE; Governor; lịch cũ còn hạn ở edge; biểu giá publish có audit ([08](08-energy-optimization.md)) |
| Tunnel hỗ trợ (P1) | Kỹ sư giả | — | Chối thao tác | Lộ OT | — | Leo từ edge sang OT LAN | Chủ site cho phép; ghi phiên; tunnel không route OT (NFR-SEC-022) |
| Kênh thông báo (e-mail, Zalo) | Giả thông báo để phishing | — | — | Lộ thông tin site trong nội dung | Nhà cung cấp kênh sập | — | Nội dung tối thiểu, không chứa D2; deep-link luôn qua đăng nhập; hướng dẫn người dùng; kênh dự phòng ([§16.5](#s16)) |

### 15.3 Ca lạm dụng

| ID | Kịch bản (mã gốc ở ghi chú I) | Tác động | Phòng ngừa | Phát hiện | Phản ứng |
|---|---|---|---|---|---|
| ABU-01 (I AC-01) | Tài khoản cloud có quyền rộng bị chiếm, ra lệnh xả 100% mọi BESS cùng lúc | Vượt giới hạn xuất hàng loạt, dao động lưới cục bộ, hao pin, mất dự phòng | Governor; C3 cho > 10% MW; SOE kẹp tại edge; giới hạn xuất tại edge/native vẫn giữ (mức 4 trên mức 7); jitter | Bất thường số lệnh/ΔP; lệnh từ IP/thiết bị mới | Kill switch tenant/nền tảng; thu hồi phiên/token; edge `REVERT_DEFAULT` |
| ABU-02 (I AC-02) | Insider sửa SOE để nới giới hạn | Hỏng pin, vi phạm hợp đồng | SoD đề xuất ≠ duyệt; SOE ký; thông báo chủ site; edge từ chối version thấp hơn | Audit, diff SOE | Rollback SOE (C3) |
| ABU-03 (I AC-03) | Phát lại lệnh hợp lệ cũ | Tác động lặp | `expires_at`, `seq`, `command_id`, đồng hồ `SYNCED` | Edge `REJECTED_REPLAY/STALE` | Cảnh báo bảo mật Cao |
| ABU-04 (I AC-04) | Chèn mã vào thư viện/firmware edge | Toàn đội bị chiếm | SBOM, ký build, review, canary, anti-rollback | Egress lạ của edge; health check | Dừng rollout; rollback A/B; kill switch |
| ABU-05 (I AC-05) | Credential cloud hãng có quyền ghi bị lộ từ DB | Điều khiển trực tiếp qua cloud hãng, **bỏ qua edge** | Không lưu credential ghi nếu không cần; vault + khóa theo tenant | — | Chủ hệ thống thu hồi tại hãng |
| ABU-06 (I AC-06) | Kênh cloud hãng song song đổi chế độ pin khi edge đang điều khiển | Xung đột điều khiển, "ghi không tác dụng" | Chính sách CD-06 (chặn với site M2); đặt thiết bị ở chế độ điều khiển ngoài | Readback lệch; chế độ đổi không do ta | Cảnh báo `EXTERNAL_CONTROL_DETECTED` (NFR-SEC-019) |
| ABU-07 (I AC-07) | Nhà cung cấp (kể cả ta) vô hiệu hóa hệ thống khách vì tranh chấp | Mất vận hành | Cam kết hợp đồng không có kill thương mại (BR-SEC-08); edge chạy mặc định cục bộ vĩnh viễn khi hết hợp đồng; xuất dữ liệu | — | — |
| ABU-08 (I AC-08) | Giả telemetry công tơ POC để edge xả/sạc sai | Vi phạm giới hạn xuất/trần nhập | Kiểm chéo cân bằng (POC ≈ tải − PV − BESS trong dung sai), giới hạn tốc độ thay đổi, công tơ trên OT LAN cô lập | Mất cân bằng > ngưỡng kéo dài | Chuyển `NATIVE_SAFE`; cảnh báo Cao |
| ABU-09 (I AC-09) | DoS broker/cloud giờ cao điểm để phá peak shaving | Mất lợi ích kinh tế | Lịch ≥ 48 h tại edge | — | Không cần can thiệp điều khiển |
| ABU-10 (I AC-10) | Installer cũ còn quyền sau hết hợp đồng | Truy cập trái phép | Grant có hạn; xem lại 90 ngày; khóa quyền lệnh sau 90 ngày không đăng nhập | Đăng nhập từ tài khoản ngủ đông | Thu hồi |
| ABU-11 (mới) | Installer cố ý đặt `export_limit_w` cao hơn hợp đồng đấu nối để tăng sản lượng | Vi phạm quy định đấu nối | Đổi cấu hình lưới là C3; trần cứng trong SOE; tài liệu hợp đồng đính kèm (F-ORG-12) | Diff cấu hình vs hồ sơ | Rollback; báo chủ tài sản |
| ABU-12 (mới) | Giả NTP để lệnh hết hạn thành hợp lệ hoặc lệnh tương lai có hiệu lực sớm | Lệnh cũ/sai thời điểm | ≥ 2 nguồn thời gian; NTS khi có; từ chối bước nhảy; IL-06 | `clock_state` đổi; offset bất thường | Chặn lệnh; cảnh báo |
| ABU-13 (mới) | API client của bên thứ ba bị lộ | Đọc dữ liệu hàng loạt; (P2) lệnh C1 | Chỉ đọc mặc định; IP allow-list; scope; hạn ≤ 1 năm; Governor | Khối lượng truy vấn bất thường | Thu hồi client |
| ABU-14 (mới) | Phishing qua thông báo giả (e-mail/Zalo) dẫn tới trang đăng nhập giả | Chiếm tài khoản | WebAuthn chống phishing; nội dung thông báo không có link đăng nhập trực tiếp ngoài tên miền chính | Đăng nhập từ thiết bị mới + lệnh ngay sau đó | Thu hồi phiên |
| ABU-15 (mới) | Ransomware/xóa dữ liệu ở cloud | Mất giám sát, mất audit | Backup bất biến ở tài khoản khác; WORM audit (P1); edge giữ buffer và audit cục bộ | Giám sát xóa hàng loạt | DR; kill switch nền tảng trong lúc khôi phục |
| ABU-16 (mới) | Công cụ engineering cắm vào OT LAN làm master thứ hai khi edge `REMOTE` | Ghi xung đột, mất ghi của edge | Quy trình `MAINTENANCE`; phát hiện master thứ hai | `OT.SECOND_MASTER_SUSPECTED` | Chặn ghi; cảnh báo Cao |
| ABU-17 (mới) | Lạm dụng break-glass của nhân viên nền tảng | Lộ dữ liệu tenant | Duyệt bởi tenant; hạn 4 h; không quyền lệnh; thông báo | Audit `breakglass=true` | Thu hồi; điều tra |

### 15.4 Sự cố thực tế đã ghi nhận (trạng thái kiểm chứng)

| Sự cố | Bằng chứng | Bài học |
|---|---|---|
| 11/2024: inverter ở Mỹ/Anh/Pakistan bị vô hiệu hóa từ xa, điều tra cho thấy tranh chấp thương mại | [FACT] Defense News (§2.5); gán hãng: [UNKNOWN] | Một tài khoản cloud có quyền ghi = kill switch toàn đội → Governor, kill switch có kiểm soát, cam kết hợp đồng |
| 5/2025: "rogue communication devices" (Reuters); DOE 1/2026 không thấy bằng chứng độc hại | [FACT] bài báo tồn tại; nội dung chưa xác nhận (§3.4) | Không quy kết; chính sách kênh cloud hãng; giám sát egress OT (P1) |
| Lithuania cấm truy cập từ xa của công ty Trung Quốc > 100 kW | [FACT] (§3.4) | Khách phải tắt được kênh cloud hãng mà vẫn vận hành |
| Forescout SUN:DOWN 3/2025; CCC/Hoymiles 2026 | [FACT] (§14.1, §9.4) | Cloud API và cơ chế cập nhật là bề mặt chính → pen-test, VDP, OTA ký |
| Huawei 9/2025 đổi chính sách cấp quyền API làm hỏng tích hợp bên thứ ba | [FACT] (§8.2) | Phụ thuộc cloud hãng là rủi ro khả dụng; connector không dùng cho điều khiển |
| Ukraine 2015/2016 | [INFERENCE] kiến thức nền, chưa kiểm chứng URL | Không VPN thường trực; conduit SCADA cô lập |
| "Sự cố Solarman/Deye cloud" | [UNKNOWN] — không có bằng chứng trong nguồn hiện có; không ghi là sự cố (Q-I-09) | — |

---

<a id="s16"></a>
## 16. Độ tin cậy: khả dụng, RPO/RTO, sao lưu/DR, chế độ suy giảm

Đặc tả chi tiết cho NFR-REL-004, 005, 006, 008…012; NFR-OBS-005.

### 16.1 Mục tiêu khả dụng tách theo mặt phẳng

[INFERENCE] Với edge-first, mất cloud chỉ làm mất tối ưu và giám sát từ xa, không làm mất an toàn — **nếu** edge có lịch ≥ 48 h và fallback. Vì vậy mục tiêu của cloud có thể thấp hơn của edge, và mỗi dịch vụ có SLO riêng. Cửa sổ đo 30 ngày. [PROPOSAL]

| Dịch vụ | SLI | SLO | Mặt phẳng | Ghi chú |
|---|---|---|---|---|
| Điều khiển cục bộ edge | Tỷ lệ chu kỳ điều khiển hoàn thành đúng hạn (không treo, không vượt chu kỳ 1 s) trên số chu kỳ kỳ vọng, cho site `control_gate ≠ NONE` | ≥ 99,95% | Edge | Lớp an toàn chính; watchdog HW; NFR-PERF-006 (p99 ≤ 200 ms) |
| Tuân thủ giới hạn xuất | Số sự kiện vi phạm xuất (định nghĩa 04 §2) | 0 trong test; vận hành: báo cáo, không SLO % | Edge/native | NFR-REL-009 |
| Command API | Request hợp lệ trả 2xx/4xx đúng nghĩa / tổng (không tính từ chối PDP) | ≥ 99,9% giờ hành chính; ≥ 99,5% tổng | Control | Edge có fallback nên không cần 99,99% |
| Giao lệnh | p95 `CREATED→RECEIVED` khi edge online | ≤ 5 s; p99 ≤ 15 s | Control | NFR-PERF-005 |
| Áp dụng lệnh | p95 `RECEIVED→APPLIED` | ≤ 15 s (phụ thuộc thiết bị) | Edge | NFR-PERF-005 |
| Kill switch | Thời gian tới khi mọi edge online trong phạm vi báo `SUSPENDED` | ≤ 60 s (100% lần thử trong test) | Control | NFR-REL-010 |
| UI/API giám sát | Request thành công / tổng | ≥ 99,5% | Monitoring | — |
| Độ tươi ingest | p95 `ts_ingest − ts` cho lớp C2 | ≤ 60 s; C1 khi xem live ≤ 10 s | Monitoring | NFR-PERF-003 |
| Bảo toàn dữ liệu | Mẫu tới cloud trong ≤ 24 h (kể cả backfill) / mẫu kỳ vọng | ≥ 99,9% | Monitoring | NFR-DATA-001 |
| Cảnh báo | p95 sự kiện → thông báo | ≤ 2 phút | Monitoring | NFR-PERF-007 |
| Báo cáo ngày | R1 sẵn sàng trước 06:00 giờ site | 99% | Monitoring | NFR-PERF-008 |

**Error budget** [PROPOSAL]: hết budget Command API hoặc giao lệnh → đóng băng release control plane (trừ bản vá an toàn/bảo mật) cho tới khi phục hồi; hết budget giám sát → ưu tiên sửa ổn định trong sprint kế tiếp. Vi phạm "Tuân thủ giới hạn xuất" trong vận hành luôn mở điều tra INC-SAF ([§18](#s18)).

### 16.2 RPO / RTO

| Dữ liệu / dịch vụ | RPO | RTO | Cơ chế | Mức |
|---|---|---|---|---|
| Danh mục, cấu hình, SOE, quyền (PostgreSQL) | ≤ 5 phút | ≤ 4 h | WAL archiving + PITR; replica đồng bộ trong vùng | P0 |
| Bảng lệnh + audit | ≤ 1 phút (mục tiêu ≈ 0) | ≤ 4 h | Replica đồng bộ; edge giữ bản sao lệnh/audit cục bộ; neo WORM (P1) | P0 |
| Timeseries nóng (TimescaleDB) | ≤ 15 phút | ≤ 8 h (khôi phục dữ liệu mới trước) | Backup + **backfill từ buffer edge** (≥ 7 ngày) → RPO thực tế ≈ 0 cho dữ liệu trong buffer | P0 |
| Timeseries lạnh (Parquet, P1) | ≤ 24 h | ≤ 72 h | Sao chép sang vùng khác | P1 |
| Secrets/KMS | Theo nhà cung cấp | ≤ 4 h | Bản sao khóa trong HSM dự phòng; quy trình khôi phục CA | P0 |
| Dữ liệu connector cloud hãng | Theo khả năng backfill của hãng | — | Backfill ban đêm theo hạn mức hãng | P0 |

Nguồn: [04 NFR-REL-005](04-business-requirements.md); điều kiện ADR lưu trữ: NFR-DATA-013 (giấy phép TSL + PoC).

### 16.3 Sao lưu

- Backup mã hóa (khóa KMS riêng cho backup), lưu ở tài khoản/dự án tách biệt với production, không thể xóa bằng credential production (ABU-15). [PROPOSAL]
- Lịch: base backup hằng ngày + WAL liên tục; giữ 35 ngày PITR; bản hằng tháng giữ 13 tháng. [PROPOSAL]
- **Diễn tập khôi phục PITR hằng quý** trên môi trường tách; đo RTO thực tế; kiểm tính toàn vẹn chuỗi audit sau khôi phục. [PROPOSAL, NFR-REL-005]
- Cấu hình edge (`EdgeConfigVersion` đã áp) giữ ≥ 5 năm làm bằng chứng ([05 §6](05-domain-model.html#s6)).

### 16.4 DR và khôi phục control plane

- **Hai trung tâm dữ liệu tại Việt Nam** (vùng chính + vùng DR khác tỉnh) là P1 (NFR-REL-006); nhà cung cấp chưa đánh giá (Q-I-13). [PROPOSAL]
- **Trình tự failover** [PROPOSAL]:
  1. Tự động engage kill switch nền tảng (cloud phía DR khởi động ở trạng thái "control suspended").
  2. Khôi phục monitoring plane trước (ingest, cảnh báo, dashboard); edge backfill.
  3. Kiểm tra: chuỗi audit liên tục, `seq` sàn của Signer ≥ giá trị cuối đã biết (lấy từ edge đối soát), khóa KMS khả dụng, PDP phiên bản đúng.
  4. Release kill switch theo tenant là C3 (hai `PLATFORM_ADMIN`), có thông báo tenant.
- Sau khôi phục: không thi hành lại lệnh hết hạn; edge báo trạng thái; bộ sinh lịch phát lịch mới (NFR-REL-012).
- Diễn tập failover 6 tháng/lần (P1); **game day mất cloud 4 h** hằng quý trên site thử/HIL để xác nhận fallback edge (P0 cho Gate M2 đầu tiên).

### 16.5 Chế độ suy giảm của cloud

| Thành phần lỗi | Ảnh hưởng | Hành vi bắt buộc | Mức cảnh báo nền tảng |
|---|---|---|---|
| IdP | Không đăng nhập mới | Phiên đang có tiếp tục đọc; **lệnh C1+ bị chặn** (không xác minh được `sid`/step-up) | Khẩn cấp |
| PDP / DB lệnh | Không quyết định lệnh | Fail-closed: không lệnh mới; monitoring chạy | Khẩn cấp |
| KMS / Signer | Không ký | Fail-closed; edge chạy lịch/mặc định | Khẩn cấp |
| Broker | Không giao lệnh, không nhận telemetry | Edge buffer; cloud đánh dấu nguồn `DELAYED/OFFLINE`; không hiển thị 0 | Khẩn cấp |
| Ingest chậm/backlog | Dữ liệu trễ | Ưu tiên `event`, `cmd-ack`, `state` hơn `telemetry`/`backfill`; backpressure tới edge (edge giữ buffer) | Cao |
| TSDB | Không truy vấn lịch sử | Dashboard hiện trạng thái lỗi rõ ràng; giá trị live từ cache `state` | Cao |
| Bộ sinh lịch / optimizer | Không có lịch mới | Edge chạy lịch cũ còn hạn → mặc định; tầng 3 lỗi → tầng 2 | Cao |
| Biểu giá thiếu/hết hiệu lực | Lịch kinh tế sai | Không phát lịch kinh tế; dùng chiến lược mặc định; cảnh báo cấu hình | Trung bình |
| Connector cloud hãng (throttle, `AUTH_REVOKED`) | Site chỉ giám sát mất dữ liệu | Trạng thái nguồn rõ; backfill khi phục hồi | Trung bình (Cao nếu > 30 phút) |
| Kênh thông báo (e-mail/Zalo/push) | Cảnh báo không tới | Chuyển kênh dự phòng (in-app + kênh khác đã đăng ký); cảnh báo Khẩn cấp leo thang theo lịch trực | Cao |

### 16.6 Năng lực và backpressure

- Broker và ingest có quota theo edge và tenant; khi quá tải, giảm ưu tiên `backfill` trước, không bao giờ bỏ `event`/`cmd-ack`. [PROPOSAL, NFR-REL-016]
- Sau sự cố mất cloud diện rộng, edge xả buffer có giới hạn tốc độ và jitter để tránh "bão backfill" (F-INT-09); ingest chịu 5–10× tải thường (NFR-PERF-004).
- Bảo trì có kế hoạch: thông báo trước ≥ 72 h; không bảo trì control plane trong khung cao điểm 17:30–22:30 giờ site (QĐ 963, K §6 #37). [PROPOSAL]

---

<a id="s17"></a>
## 17. Quan sát hệ thống (observability) của chính nền tảng

Đặc tả chi tiết cho NFR-OBS-001…007, FR-SEC-025, F-SEC-21.

### 17.1 Metric

| Nhóm | Metric tối thiểu | Nhãn (label) |
|---|---|---|
| Golden signals mỗi dịch vụ | Tốc độ request, tỷ lệ lỗi, độ trễ p50/p95/p99, bão hòa (CPU, bộ nhớ, pool kết nối, hàng đợi) | `service`, `endpoint` (không `tenant_id` ở metric độ phân giải cao để tránh bùng cardinality; dùng log/trace cho tenant) |
| Ingest | Mẫu/s, độ trễ `ts_ingest − ts` p50/p95 theo lớp, backlog, tỷ lệ trùng, tỷ lệ quality `BAD_*`/`FROZEN` | `class` |
| Edge fleet (NFR-OBS-002) | Edge online %, `clock_state`, `clock_offset_ms`, `buffer_fill_pct`, `uplink_state`, `cycle_time_ms` p99, `run_mode` phân bố, phiên bản firmware/config, chứng chỉ sắp hết hạn | `firmware`, `run_mode` |
| Lệnh (NFR-OBS-001) | Số lệnh theo trạng thái, độ trễ giữa các trạng thái, tỷ lệ `REJECTED_*` theo lý do, `FAILED_*`, `APPLIED_CLAMPED`, `UNDELIVERED`; lệnh/phút; Σ\|ΔP\| tenant/nền tảng 5 phút; số site đang fallback; kill switch đang bật | `type`, `reason` |
| An ninh (NFR-OBS-006) | Đăng nhập thất bại, step-up thất bại, `REJECTED_REPLAY/INVALID/SIGNATURE`, tốc độ ký Signer, kết quả kiểm chuỗi audit, break-glass đang mở | — |
| Dữ liệu (NFR-OBS-007) | Coverage, tỷ lệ SUSPECT, độ trễ job ngày, dirty bucket chờ tính lại | — |

### 17.2 Log và trace

- Log JSON có cấu trúc: `ts` (UTC, ms), `service`, `level`, `trace_id`, `span_id`, `tenant_id`, `site_id`, `command_id`, `edge_id`, `event_code`; không ghi D3 thô, token, secret (lọc theo danh sách trường) (NFR-OBS-003). [PROPOSAL]
- Lưu log ứng dụng: 30 ngày nóng; log bảo mật (xác thực, PDP, Signer, broker ACL từ chối) 13 tháng — số pháp định [UNKNOWN] (Q-I-04). [PROPOSAL]
- Edge: log cục bộ vòng tròn ≥ 30 ngày (nén), cùng định dạng, kèm `clock_state` ở mỗi bản ghi; tải lên theo yêu cầu cho điều tra (NFR-OBS-009 mới).
- Trace OpenTelemetry (P1, NFR-OBS-004): API → PDP → Approval → Signer → Dispatcher → broker → edge; edge gắn `traceparent` vào ack. Lấy mẫu **100%** cho đường lệnh; 1–10% cho đường đọc.

### 17.3 Danh mục cảnh báo của nền tảng

Mức theo bộ nhãn chung (K §6 #39). Mỗi cảnh báo có runbook; cảnh báo Khẩn cấp gọi trực ca (on-call) 24/7 từ khi có site Gate M2 đầu tiên. [PROPOSAL, NFR-OBS-008 mới]

| Mã | Điều kiện | Mức | Runbook (tóm tắt) |
|---|---|---|---|
| PLT.KMS_UNAVAILABLE | Signer không ký được > 1 phút | Khẩn cấp | Xác minh KMS; edge đang fallback; thông báo khách nếu > 30 phút |
| PLT.PDP_DOWN | PDP lỗi > 1 phút | Khẩn cấp | Fail-closed đang hoạt động? Khôi phục |
| PLT.BROKER_DOWN | > 20% edge mất kết nối cùng lúc trong 2 phút | Khẩn cấp | Phân biệt broker vs mạng nhà mạng; theo dõi buffer |
| SEC.AUDIT_CHAIN_BROKEN | Kiểm chuỗi hằng ngày thất bại | Khẩn cấp | Mở INC-SEC; đóng băng thay đổi; so với WORM |
| SEC.REPLAY_DETECTED | Bất kỳ `REJECTED_REPLAY`/`REJECTED_INVALID` | Cao (Khẩn cấp nếu ≥ 3 edge/1 h) | Kiểm broker, khóa ký; cân nhắc kill switch |
| SEC.CMD_ANOMALY | Lệnh/ΔP > 5× đường cơ sở 5 phút | Khẩn cấp | Kill switch tự động engage; xác minh với người phát |
| SEC.SIGN_RATE | Tốc độ ký > 3× p99 lịch sử | Cao | Kiểm dịch vụ gọi Signer |
| SEC.LOGIN_ANOMALY | Nhiều đăng nhập thất bại / thiết bị mới + lệnh C2/C3 trong 10 phút | Cao | Liên hệ người dùng; thu hồi phiên |
| SEC.BREAKGLASS_OPEN | Break-glass đang mở | Thông tin | Theo dõi hết hạn |
| CTRL.GOVERNOR_SATURATED | Ngân sách tenant > 80% trong 3 cửa sổ liên tiếp | Trung bình | Xem bộ sinh lịch, jitter |
| CTRL.UNDELIVERED_RATE | > 5% lệnh `UNDELIVERED` trong 1 h | Cao | Kiểm broker, độ trễ |
| CTRL.STATE_MISMATCH | Đối soát sau reconnect lệch | Cao | Xem lệnh hiệu lực tại edge vs cloud |
| EDGE.CERT_RENEW_FAIL | Gia hạn lỗi 14 ngày | Cao | Kiểm enroll, đồng hồ, mạng |
| EDGE.WATCHDOG_REBOOT | Edge reboot do watchdog ≥ 2 lần/24 h | Cao | Thu forensic bundle |
| EDGE.CLOCK_UNSYNCED | `UNSYNCED` > 10 phút | Cao | Kiểm nguồn thời gian |
| EDGE.BUFFER_HIGH | `buffer_fill_pct` > 70% | Cao (Khẩn cấp > 90%) | Mất mạng dài; cân nhắc can thiệp tại chỗ |
| ING.LAG | p95 độ trễ ingest > 5 phút trong 10 phút | Cao | Mở rộng ingest, xem backlog |
| DATA.JOB_LATE | Job ngày chưa xong 02:00 giờ site | Trung bình | — |
| NOTIF.CHANNEL_DOWN | Kênh thông báo lỗi > 10 phút | Cao | Chuyển kênh dự phòng |
| OT.SECOND_MASTER_SUSPECTED | Dấu hiệu master Modbus thứ hai khi REMOTE | Cao | Liên hệ site; xác minh MAINTENANCE |

Cảnh báo an toàn **không được tạm gác (shelve)** — trả lời yêu cầu của 04 về BR-ALM-03 [PROPOSAL]: E-stop tác động (IL-02); PCCC/khói/khí/nhiệt phòng pin (IL-08); BMS lỗi mức bảo vệ (IL-03); mất `MTR_POC` ở site có điều khiển (IL-04); vi phạm giới hạn xuất đang diễn ra; `SEC.REPLAY_DETECTED`; `SEC.AUDIT_CHAIN_BROKEN`; `SEC.CMD_ANOMALY`; `EDGE.WATCHDOG_REBOOT` lặp. Các cảnh báo này chỉ được ack (xác nhận), không được gác; được đặt "ngoài dịch vụ" chỉ khi tài sản ở trạng thái `maintenance` có work order.

### 17.4 Dashboard vận hành

| Dashboard | Người xem | Nội dung |
|---|---|---|
| Sức khỏe nền tảng | PO, trực ca | SLO/burn rate, golden signals, broker, ingest lag |
| Đội edge | PO | Online %, phiên bản, `run_mode`, chứng chỉ, đồng hồ, buffer |
| Đường lệnh | PO, PS | Phễu trạng thái lệnh, lý do từ chối, Governor, kill switch |
| An ninh | PO bảo mật | Tín hiệu §17.1, break-glass, audit chain |
| Theo tenant (cho khách, P1) | ORG_ADMIN | Khả dụng của site mình, độ tươi dữ liệu, sự cố đang mở |

---

<a id="s18"></a>
## 18. Quy trình điều tra sự cố

Đặc tả cho NFR-SEC-029 (mới), NFR-OBS-009 (mới). [PROPOSAL] cho toàn mục.

### 18.1 Phân loại

| Loại | Ví dụ | Mức khởi điểm |
|---|---|---|
| INC-SAF (an toàn/vật lý) | Thiết bị không về mặc định khi mất liên lạc; lệnh tác động sai; vi phạm giới hạn xuất do điều khiển; interlock không chặn | Khẩn cấp |
| INC-SEC (bảo mật) | Replay/chữ ký sai; nghi chiếm tài khoản; đứt chuỗi audit; rò cross-tenant; lộ khóa/credential | Khẩn cấp/Cao |
| INC-REL (khả dụng) | Cloud/broker sập; mất giám sát diện rộng; trễ cảnh báo | Theo SLO |
| INC-DAT (toàn vẹn dữ liệu) | Sai dấu/đơn vị, KPI sai đã phát hành, mất dữ liệu > NFR | Cao/Trung bình |
| INC-CMP (tuân thủ) | Vi phạm giới hạn xuất/trần nhập được điện lực hoặc khách nêu | Cao |

### 18.2 Vai trò

Chỉ huy sự cố (IC) của nền tảng; kỹ sư trực ca; trưởng bảo mật (cho INC-SEC); đầu mối tenant (ORG_ADMIN hoặc người được chỉ định); kỹ sư hiện trường của installer/O&M (cho INC-SAF). Mỗi sự cố có một kênh trao đổi và một bản ghi thời gian (timeline) duy nhất.

### 18.3 Các bước

| Bước | Thời hạn mục tiêu | Việc làm |
|---|---|---|
| 1. Phát hiện | — | Từ cảnh báo §17.3, cảnh báo thiết bị, báo cáo khách, điện lực |
| 2. Phân loại | ≤ 15 phút (Khẩn cấp) | Loại, mức, phạm vi (site/tenant/nền tảng), có tác động vật lý không |
| 3. Khống chế | ≤ 30 phút (Khẩn cấp) | Chọn biện pháp nhỏ nhất đủ an toàn: kill switch site/tenant/nền tảng; tắt `control_enabled`; thu hồi phiên/token/client; chặn chứng chỉ edge; tắt connector; dừng rollout OTA/config; yêu cầu site chuyển LOCAL. **Không** tác động bảo vệ native |
| 4. Bảo toàn bằng chứng | Ngay sau khống chế, trước khi dữ liệu edge bị ghi đè (dữ liệu 1 s chỉ giữ 7 ngày) | Thu **forensic bundle** (§18.4); khóa partition audit liên quan khỏi job retention; chụp cấu hình |
| 5. Phân tích | Theo mức | Dựng timeline ([§18.5](#s18)); xác định nguyên nhân gốc và yếu tố góp phần |
| 6. Thông báo | Khẩn cấp: tenant bị ảnh hưởng ≤ 4 h kể từ xác nhận; cập nhật định kỳ | Tenant, chủ tài sản; cơ quan quản lý/chủ thể dữ liệu theo luật [UNKNOWN] (Q-I-04: thời hạn thông báo vi phạm dữ liệu cá nhân chưa kiểm chứng; không ghi "72 h" làm cam kết) |
| 7. Khôi phục | — | Gỡ khống chế theo C3; theo dõi tăng cường 24–72 h |
| 8. Hậu kiểm (postmortem) | ≤ 5 ngày làm việc | Không đổ lỗi cá nhân; hành động khắc phục có người chịu trách nhiệm và hạn; cập nhật threat model, test hồi quy (T-…), runbook |

### 18.4 Forensic bundle

Gói bằng chứng theo (site, khoảng thời gian), tạo bằng một thao tác C0 có audit; lưu ở object storage với object lock trong thời gian điều tra:

| Thành phần | Nguồn |
|---|---|
| Audit cloud + edge của site/tenant, kèm `prev_hash`/`hash` và kết quả kiểm chuỗi | `AuditEvent`, audit edge |
| Vòng đời các lệnh/kế hoạch liên quan (envelope đã ký, quyết định PDP, phê duyệt, ack ký) | `DispatchCommand`, `CommandApproval`, `CommandStateTransition` |
| Lý do arbiter theo chu kỳ (`ARBITER_REASON`), `run_mode`, interlock | Event edge |
| Telemetry 1 s quanh sự cố (từ vòng tròn 7 ngày của edge) + dữ liệu cloud | Edge (lệnh **ghim cửa sổ dữ liệu** để không bị ghi đè — đề xuất mới, xem [§22](#s22)), TSDB |
| Log edge, trạng thái đồng hồ, lịch sử OTA/config | Edge |
| Phiên bản SOE, cấu hình lưới, driver map, `capability_profile` | Registry |
| Log IdP, PDP, Signer, broker ACL | Cloud |

### 18.5 Câu hỏi bắt buộc khi điều tra INC-SAF

1. Ở thời điểm sự cố, lệnh/kế hoạch nào hiệu lực tại edge, nguồn nào, mức arbiter nào thắng, có kẹp không?
2. Interlock nào tác động hoặc lẽ ra phải tác động? Tín hiệu đọc được không?
3. Readback và đáp ứng vật lý có khớp setpoint không (`tracking_state`)?
4. Bảo vệ native có tác động không (BMS, PCS, rơ-le)? Thứ tự thời gian so với lệnh?
5. Đồng hồ edge và thiết bị có đồng bộ không (`clock_state`, `ts` vs `ts_src`)?
6. Có kênh điều khiển ngoài (cloud hãng, HMI tại chỗ, master Modbus thứ hai) không?
7. Thiết bị có watchdog đã test không; `revert_timeout_s` thực tế bao nhiêu?
8. Có thay đổi gần đây (OTA, driver, SOE, cấu hình lưới, chính sách PDP) không?

---

<a id="s19"></a>
## 19. Kế hoạch kiểm thử bảo mật và an toàn

Đặc tả cho NFR-SEC-024, NFR-SEC-030 (mới), NFR-REL-017 (mới). Đáp ứng khoảng trống K G-05 về chiến lược kiểm thử ở phần an toàn/bảo mật; chiến lược kiểm thử chức năng chung thuộc [06](06-system-architecture.html)/[11](11-mvp-and-roadmap.html). Công cụ nêu tên là ví dụ [PROPOSAL], không phải lựa chọn đã chốt.

### 19.1 Tổng quan hoạt động

| Hoạt động | Phạm vi | Tần suất | Cổng chặn | Mức |
|---|---|---|---|---|
| Threat model | Control plane, edge, driver ghi | Mỗi thay đổi lớn ở Command API, PDP, Signer, arbiter, driver ghi; rà soát mỗi quý | Review thiết kế | P0 |
| SAST | Mã Java, Angular, edge | Mỗi PR | Không có phát hiện High/Critical mới chưa xử lý | P0 |
| SCA + SBOM | Dependency cloud, edge, image | Mỗi build; SBOM (CycloneDX hoặc SPDX) đính kèm release | CVE Critical có bản vá → chặn release | P0 |
| Quét secret | Repo, image, log mẫu | Pre-commit + CI | Chặn merge | P0 |
| Quét IaC/container | Terraform/Helm, image | Mỗi PR | Cấu hình nguy hiểm (privileged, public bucket) chặn | P0 |
| Test cross-tenant | Mọi endpoint và job | Mỗi build | Build thất bại nếu rò (AC-SEC-09) | P0 |
| Test chuỗi lệnh (đơn vị + tích hợp) | PDP, Signer, edge verifier, test vector vàng JWS | Mỗi build | 100% ca bắt buộc §19.3 | P0 |
| DAST | API công khai, web | Hằng tuần trên staging; trước release | High chặn release | P1 |
| Fuzzing adapter giao thức | §19.2 | Liên tục trong lab (nightly) + trước khi driver đạt `VERIFIED_LAB` | Không crash/treo/ghi ngoài ý muốn | P0 cho driver ghi; P1 cho driver đọc |
| HIL an toàn | §19.3 | Trước mỗi release edge; ca áp dụng cho M1 (chữ ký, hạn, đồng hồ, LOCAL, kill switch, `M1StaticLimits`) trước site M1 có điều khiển đầu tiên; toàn bộ trước Gate M2 site đầu tiên | Mọi ca áp dụng đạt | P0 |
| Pen-test bên thứ ba | (a) Web, API, broker ACL, đường lệnh ký (gồm lịch native, `CONFIG_PUSH`), multi-tenant, edge phần cứng (UART/JTAG, boot, disk, cổng mạng), OTA, kịch bản ca lạm dụng ABU-01/03/04/08/12/16; (b) lặp lại tập trung đường setpoint, arbiter, Governor ΔP, interlock | (a) trước site production đầu tiên có `control_enabled = true` (Gate M1); (b) trước site Gate M2 đầu tiên; sau đó hằng năm và sau thay đổi lớn control plane | Critical/High đóng trước khi bật điều khiển ở Gate tương ứng | P0 (a, b), P1 (định kỳ) |
| Red team theo ca lạm dụng | ABU-01, 03, 04, 08, 12, 16 | Lần đầu nằm trong pen-test (a) trước site M1 có điều khiển; sau đó hằng năm | Báo cáo + hành động | P0 (lần đầu), P1 (định kỳ) |
| Game day / chaos | Mất cloud 4 h, mất broker, KMS lỗi, DR | Hằng quý (game day mất cloud: P0 trước Gate M2) | Fallback đúng bảng §13.2 | P0/P1 |
| Chương trình công bố lỗ hổng (VDP) | `security.txt`, e-mail có PGP | Liên tục | SLA vá: Critical cloud ≤ 72 h, Critical edge ≤ 14 ngày, High ≤ 30 ngày | P1 |

### 19.2 Fuzzing adapter Modbus và giao thức trong lab

**Mục tiêu** [PROPOSAL]:

| Đối tượng | Ai gửi dữ liệu xấu | Rủi ro cần loại trừ |
|---|---|---|
| Driver Modbus master của edge (phân tích **phản hồi**) | Slave giả/lỗi (công tơ giả, PCS lỗi firmware, kẻ tấn công trên OT LAN) | Crash/treo tiến trình điều khiển; giá trị sai không bị gắn quality; tràn số khi scale/word order; đọc sai sinh **lệnh ghi** |
| Modbus TCP server của edge (F-INT-17, P1) | Client SCADA khách hoặc kẻ trên mạng | Crash; đọc được thanh ghi ngoài bảng xuất; ghi được khi chỉ đọc |
| IEC 104 slave (F-INT-16, P1) | Master giả | Crash; chấp nhận type lệnh không cấu hình |
| OCPP CSMS tối giản (P1) | Charger giả | Crash; chấp nhận charger chưa đăng ký |
| Bộ giải mã payload uplink ở cloud | Edge bị chiếm | Crash ingest; ghi dữ liệu cho site khác; tràn bộ nhớ khi giải nén |
| Bộ kiểm envelope tại edge | Broker bị chiếm | Chấp nhận envelope hỏng/chữ ký sai/JCS lệch |

**Phương pháp:**
1. Harness chạy driver thật với **bộ mô phỏng thiết bị** (F-INT-24) làm slave; fuzzer sinh phản hồi theo ngữ pháp PDU Modbus (function code hợp lệ/không hợp lệ, độ dài byte count sai, exception code, khung RTU CRC sai, khung TCP MBAP length sai, transaction id lệch, phản hồi trễ/ngắt giữa chừng) và đột biến từ bản ghi lưu lượng thật đã ẩn danh.
2. Với SunSpec: bảng model giả (độ dài model sai, `SunS` ở địa chỉ lạ, scale factor cực trị, sentinel) để kiểm thuật toán khám phá ([07 §5.2](07-device-integration.md)).
3. **Oracle**: không crash; vòng điều khiển không vượt chu kỳ quá 3 lần liên tiếp; giá trị bất thường gắn quality `BAD_*`/`UNCERTAIN_*`; **không có lệnh ghi nào phát ra từ đường đọc**; watchdog phần cứng không phải can thiệp; bộ nhớ ổn định sau 24 h.
4. Coverage-guided fuzz cho bộ phân tích (parser) ở mức hàm; fuzz end-to-end qua socket cho hành vi thời gian.
5. **Không bao giờ fuzz thiết bị đang vận hành của khách.** Fuzz thiết bị thật chỉ trên bàn lab cô lập, có đồng ý của hãng/chủ thiết bị, thiết bị coi như có thể hỏng; kết quả lỗi thiết bị báo cho hãng theo quy trình công bố có trách nhiệm.
6. Lỗi tìm được → test hồi quy cố định trong CI.

Kết quả mô phỏng không được dùng làm bằng chứng kiểm chứng driver (07 D-07-13).

### 19.3 Ca kiểm thử an toàn bắt buộc (HIL và tích hợp)

| ID | Ca | Kỳ vọng | Yêu cầu |
|---|---|---|---|
| T-NFR-REL-001-01 | Chặn broker 4 h khi đang chạy lịch | Edge chạy lịch; hết lịch → mặc định; không mất dữ liệu; sau nối lại không thi hành lệnh hết hạn | NFR-REL-001, 012 |
| T-NFR-REL-002-01 | Rút cáp edge↔PCS khi đang xả theo setpoint | PCS về mặc định trong `revert_timeout_s` | NFR-REL-002 |
| T-NFR-REL-002-02 | Thiết bị không có watchdog nhận `SET_ESS_P` | PDP từ chối `DEVICE_NOT_ELIGIBLE`; edge `REJECTED_UNSUPPORTED` nếu bị gửi | FR-SEC-016 |
| T-NFR-REL-003-01 | Treo tiến trình điều khiển | Watchdog HW reset ≤ 10 s; `SAFE_START`; không ghi trước 2 chu kỳ đọc | NFR-REL-003 |
| T-NFR-REL-007-01 | Ngắt `MTR_POC` | BESS P = 0/native, PV về giới hạn native ≤ 2 chu kỳ; cảnh báo Cao | NFR-REL-007 |
| T-NFR-REL-007-02 | Làm cũ dữ liệu BMS | IL-03, P = 0/native | NFR-REL-007 |
| T-NFR-SEC-004-01 | Phát lại envelope hợp lệ sau 2 phút | `REJECTED_REPLAY`; cảnh báo bảo mật | AC-SEC-04 |
| T-NFR-SEC-004-02 | Envelope sửa 1 byte trong `params` | `REJECTED_INVALID` | NFR-SEC-004 |
| T-NFR-SEC-004-03 | `alg=none`, `kid` lạ, `kid` đã gỡ | `REJECTED_INVALID` | NFR-SEC-004 |
| T-NFR-SEC-011-01 | Envelope tới sau `expires_at` 1 s / sau `max_latency_ms` | `REJECTED_STALE`; không ghi | AC-SEC-05 |
| T-NFR-SEC-009-01 | Site M1 có `M1StaticLimits` (`export_limit_w` = 0, `import_cap_w` = 800 000): gửi cấu hình lưới xuất 50 kW; `SET_IMPORT_LIMIT` 1 MW; `SET_ESS_P` (type M2); site `control_enabled` chưa có bản `ACTIVE_ON_EDGE` | `DENIED: OUT_OF_SOE` / `OUT_OF_SOE` / `GATE`; edge `REJECTED_OUT_OF_LIMIT` nếu bị gửi; bật `control_enabled` bị chặn | NFR-SEC-009 |
| T-NFR-SEC-012-02 | Gate M1: bộ sinh lịch đổi lịch native của 60 site trong một lần chạy | Chỉ ≤ trần site/lần chạy được ký; phần còn lại xếp đợt; cảnh báo Cao; Signer từ chối `run_id` vượt trần | NFR-SEC-012 (M1) |
| T-NFR-SEC-028-01 | Lệch đồng hồ edge 10 phút bằng NTP giả | `UNSYNCED`/từ chối bước nhảy; IL-06 chặn lệnh | NFR-SEC-028 |
| T-NFR-SEC-010-01…10 | Kích từng interlock IL-01…IL-10 | `REJECTED_INTERLOCK:<IL>`; hành động theo §11.4 | NFR-SEC-010 |
| T-NFR-SEC-010-11 | Mất module DI | Interlock coi như tác động | NFR-SEC-010 |
| T-NFR-SEC-012-01 | Lệnh làm Σ\|ΔP\| vượt 20% MW tenant | Xếp hàng + C3 | AC-SEC-07 |
| T-NFR-SEC-013-01 | Engage kill switch tenant 50 edge mô phỏng | Mọi edge online `SUSPENDED` ≤ 60 s; lệnh mới bị từ chối | AC-SEC-08 |
| T-NFR-SEC-013-02 | Edge đang chạy `APPLY_SCHEDULE` 7 ngày; cắt uplink; engage kill switch tenant; giữ offline > 24 h (ví dụ 30 h); nối lại | Edge nhận trạng thái retained, vào `suspended`, hủy lịch cloud cũ, chạy mặc định; **không** chạy slot lịch cũ nào sau reconnect (kể cả trong 60 s đầu); S16 báo khớp | NFR-SEC-013 |
| T-NFR-SEC-013-03 | Phát lại tin trạng thái `suspended = false` cũ (version thấp) sau engage | Edge từ chối (version thấp); vẫn tạm ngưng | NFR-SEC-013 |
| T-NFR-SEC-013-04 | Gate M1: engage kill switch site/tenant/nền tảng khi scheduler đang đẩy lịch native và có `CONFIG_PUSH` chờ | Không lịch native/`SET_ESS_MODE`/`CONFIG_PUSH` nào được ký/gửi trong phạm vi; edge không áp lịch native mới | NFR-SEC-013 |
| T-NFR-SEC-008-01 | Người yêu cầu tự duyệt C3 / duyệt sau 15 phút | Bị chặn / `APPROVAL_EXPIRED` | AC-SEC-02, 03 |
| T-NFR-SEC-007-01 | Bộ cross-tenant | 0 rò | AC-SEC-09 |
| T-NFR-SEC-015-01 | `UPDATE`/`DELETE` audit bằng role app; sửa một hàng bằng superuser rồi chạy kiểm chuỗi | Bị từ chối; kiểm chuỗi phát hiện | AC-SEC-10 |
| T-NFR-SEC-014-01 | Chuyển LOCAL (và MAINTENANCE) khi đang có lệnh tay và lịch | Lệnh `CANCELLED`; từ chối lệnh mới; bắt gói bus Modbus/CAN cho thấy **0 lệnh ghi** từ edge kể từ thời điểm phát hiện LOCAL tới khi quay REMOTE; thiết bị về native bằng cơ chế mất-master của chính nó; quay REMOTE không khôi phục lệnh tay | NFR-SEC-014 |
| T-NFR-SEC-020-01 | OTA ảnh ký sai / phiên bản thấp hơn / health check lỗi | Từ chối / từ chối / rollback A/B | NFR-SEC-020 |
| T-NFR-REL-015-01 | Tắt KMS, PDP, IdP lần lượt | Không lệnh mới; monitoring chạy; cảnh báo Khẩn cấp | NFR-REL-015 |
| T-NFR-REL-011-01 | Chứng chỉ edge hết hạn | Điều khiển cục bộ tiếp tục; gia hạn qua IDevID | NFR-REL-011 |

---

<a id="s20"></a>
## 20. Danh mục yêu cầu NFR-SEC / NFR-REL / NFR-OBS

Mọi yêu cầu là `[PROPOSAL]`. Mã 001–026 (SEC), 001–012 (REL), 001–007 (OBS) là **mã chính thức của [04 §6](04-business-requirements.md)**; cột "Đặc tả ở 10" trỏ tới phần chi tiết. Mã từ NFR-SEC-027, NFR-REL-013, NFR-OBS-008 trở đi là **mã đề xuất của 10**, chờ 04 xác nhận (K §6 #38). Cột "Gate" ghi cổng đầu tiên mà yêu cầu phải đạt.

### 20.1 NFR-SEC

| ID | Yêu cầu (tóm tắt; nội dung đầy đủ ở mục được trỏ) | Ưu tiên | Gate | Đặc tả ở 10 | Kiểm chứng |
|---|---|---|---|---|---|
| NFR-SEC-001 | Cloud và edge không ghi thông số bảo vệ; không có API cho C4; không E-stop từ xa | P0 | M1 | §2, §11.5, §12.3 | Rà soát API (không endpoint C4); pen-test |
| NFR-SEC-002 | Tách monitoring/control plane (danh tính dịch vụ, credential, topic, quyền DB, namespace, release); control tắt mặc định | P0 | M1 | §2.3, §9.3, §10 | Test ACL broker; kiểm quyền DB; AC-SEC-01 |
| NFR-SEC-003 | Edge outbound-only, MQTT 5/TLS 1.3 (1.2 AEAD), mTLS, X.509 riêng, khóa trong TPM/SE (ngoại lệ có ghi rủi ro), hạn 90 ngày, tự gia hạn, thu hồi tại broker | P0 | M1 | §9.1–§9.3 | Quét cổng site (0 inbound); test gia hạn/thu hồi |
| NFR-SEC-004 | Lệnh và cấu hình ký JWS ES256 trên JCS bởi Signer (KMS); edge kiểm chữ ký, `kid`, đích, hạn, `command_id`, `seq`; ack ký bằng khóa edge | P0 | M1 (lệnh qua edge, K R-11) | §11.7, §11.8 | T-NFR-SEC-004-01…03; test vector vàng |
| NFR-SEC-005 | OIDC + PKCE; MFA cho mọi vai trò có quyền ghi/admin (WebAuthn ưu tiên); step-up ≤ 5 phút cho C2/C3; WebAuthn bắt buộc cho duyệt C3 và PLATFORM_ADMIN | P0 | M1 | §4 | AC-SEC-12; test step-up |
| NFR-SEC-006 | RBAC theo cây + PDP cho mọi lệnh (PDP-01…15); SoD; quyết định PDP lưu và audit | P0 | M1 | §5 | Test chính sách đơn vị; T-NFR-SEC-008-01 |
| NFR-SEC-007 | Cô lập tenant: RLS FORCE, role tách, `SET LOCAL`, lớp lọc thứ hai, cô lập MQTT/object/cache/job, test cross-tenant CI | P0 | M1 | §6 | T-NFR-SEC-007-01 |
| NFR-SEC-008 | Hạng C0–C4; C3 hai người khác vai trò, cửa sổ ≤ 15 phút; hash nội dung lệnh gắn vào phê duyệt (nâng hạng theo ngữ cảnh MW của PDP-04/05 bật ở M2) | P0 | M1 (13 CF-28/D-03) | §5.5, §11.5 | AC-SEC-02, 03 |
| NFR-SEC-009 | SOE theo site, version, ký, đề xuất/duyệt khác người; edge từ chối lệnh ngoài SOE và SOE version thấp hơn. Ở M1: tập con bắt buộc `M1StaticLimits` (trần xuất/nhập, sàn SOC, `allowed_command_types`) duyệt C3 trước khi bật `control_enabled` | P0 | M1 (`M1StaticLimits`); M2 (SOE đầy đủ) | §11.3, §11.3a | T-NFR-SEC-009-01; test SOE |
| NFR-SEC-010 | Interlock IL-01…IL-10 tại edge; tín hiệu không đọc được = tác động | P0 | M2 | §11.4 | T-NFR-SEC-010-01…11 |
| NFR-SEC-011 | Mọi lệnh có `expires_at` ≤ hạn tối đa type; từ chối lệnh không hạn/đến muộn; không gửi lại sau hạn | P0 | M1 | §11.6, §11.7 | T-NFR-SEC-011-01 |
| NFR-SEC-012 | Fleet Dispatch Governor. M1: biến thể đếm (site/tenant/nền tảng mỗi 5 phút, trần site mỗi lần chạy bộ sinh lịch, Signer kiểm `run_id`). M2: thêm biến thể ΔP (tenant 20%/5 phút, nền tảng 5%/5 phút, jitter); vượt → C3 | P0 | M1 (đếm); M2 (ΔP) | §14.2, §14.3 | T-NFR-SEC-012-01, 02; mô phỏng ngưỡng (Q-I-14) |
| NFR-SEC-013 | Kill switch site/tenant/nền tảng: engage C1, release C3; dừng cả lịch native, lịch edge, `CONFIG_PUSH`, OTA trong phạm vi; trạng thái tạm ngưng là tin ký, có version, retained, không hết hạn; edge đối chiếu trước khi chạy lịch cloud sau reconnect; tự engage khi DR/lộ khóa/bất thường | P0 | M1 | §14.4 | T-NFR-SEC-013-01…04 |
| NFR-SEC-014 | LOCAL/REMOTE/MAINTENANCE phần cứng (hoặc native đọc được, có biên bản) cho site M2 có BESS; quay lại REMOTE chỉ tại chỗ; không E-stop từ xa | P0 | M2 | §12 | T-NFR-SEC-014-01 |
| NFR-SEC-015 | Audit append-only, hash chain theo tenant, kiểm hằng ngày, audit edge có chuỗi riêng; neo WORM P1 | P0 (WORM P1) | M1 | §7 | T-NFR-SEC-015-01 |
| NFR-SEC-016 | Vault/KMS; khóa ký không xuất; khóa lệnh ≠ khóa cấu hình; credential hãng mã hóa theo tenant; quét secret CI; giới hạn tốc độ ký | P0 | M1 | §8 | Kiểm cấu hình KMS; quét secret |
| NFR-SEC-017 | Phân vùng OT/IT: hai NIC, không route WAN↔OT, edge master Modbus duy nhất, conduit CD-01…CD-09; chính sách kênh cloud hãng ghi trong biên bản | P0 | M1 | §10 | Checklist commissioning; quét mạng site |
| NFR-SEC-018 | Connector cloud hãng chỉ đọc mặc định; ghi qua cloud hãng là cờ riêng, ≥ C2, chỉ lịch chậm (P2) | P0 | M1 | §2.3, §8.2 | Rà soát scope credential |
| NFR-SEC-019 | Phát hiện điều khiển ngoài (`EXTERNAL_CONTROL_DETECTED`) | P1 | — | §15.3 ABU-06 | Test đổi chế độ qua app hãng |
| NFR-SEC-020 | OTA edge ký (TUF-style), A/B + rollback, anti-rollback, canary 1/10/100% có tự dừng | P0 | M1 | §9.4, §14.2 | T-NFR-SEC-020-01 |
| NFR-SEC-021 | OCPP Security Profile ≥ 2, mục tiêu 3; TxDefaultProfile an toàn; idTag băm | P1 | — | §9.6, §13.2 | Test theo model charger |
| NFR-SEC-022 | Hỗ trợ từ xa bằng reverse tunnel theo yêu cầu ≤ 2 h, chủ site cho phép, ghi phiên, không route OT; không VPN thường trực | P1 | — | §9.5 | Pen-test tunnel |
| NFR-SEC-023 | Grant installer/vendor có hạn, chủ tài sản cấp/thu hồi, xem lại 90 ngày; break-glass có duyệt, ≤ 4 h | P0 | M1 | §4.5 | Test hết hạn grant |
| NFR-SEC-024 | SDL theo tinh thần IEC 62443-4-1: threat model, SAST/SCA/SBOM/secret/IaC scan, pen-test, VDP, SLA vá; cam kết cập nhật bảo mật edge ≥ 5 năm | P1 (SAST/SCA/secret/SBOM: P0) | M1 | §19.1 | Báo cáo CI; pen-test |
| NFR-SEC-025 | Lộ trình chứng nhận ISO 27001 → IEC 62443-4-2 (edge) → đánh giá 62443-3-3; không tuyên bố trước khi có chứng chỉ | P2 | — | §3 | Rà soát tài liệu marketing |
| NFR-SEC-026 | Phân loại D0–D4; hosting VN mặc định (chờ pháp lý); DPIA và quy trình thông báo vi phạm DLCN (P1) | P0/P1 | M1 | §6.4, §3.3, §18.3 | Kiểm hạ tầng |
| **NFR-SEC-027** (mới) | Hardening edge: secure boot; mã hóa đĩa; không mật khẩu mặc định chung (mật khẩu ngẫu nhiên theo thiết bị, bắt đổi); SSH/cổng debug tắt mặc định, chỉ mở qua tunnel; tiến trình điều khiển chạy quyền tối thiểu, tách tiến trình kết nối cloud; tường lửa host theo §10.3 | P0 (secure boot: P1 nếu phần cứng MVP không hỗ trợ, ghi rủi ro) | M1 | §9.1, §9.2, §10 | Pen-test phần cứng; checklist |
| **NFR-SEC-028** (mới) | Toàn vẹn thời gian: ≥ 2 nguồn, NTS khi có, từ chối bước nhảy > 1 s khi không đồng thuận, `UNSYNCED` → IL-06 (kiểm hạn lệnh/lịch tại edge ở M1 phụ thuộc đồng hồ) | P0 | M1 | §9.4 | T-NFR-SEC-028-01 |
| **NFR-SEC-029** (mới) | Quy trình ứng phó sự cố: phân loại INC-*, khống chế ≤ 30 phút (Khẩn cấp), thông báo tenant ≤ 4 h, postmortem ≤ 5 ngày làm việc; thời hạn thông báo pháp định theo kết quả kiểm chứng Q-I-04 | P0 | M2 | §18 | Diễn tập bàn (tabletop) mỗi 6 tháng |
| **NFR-SEC-030** (mới) | Cổng kiểm thử an toàn: driver ghi chỉ đạt `VERIFIED_LAB` sau fuzz §19.2 và ca HIL liên quan §19.3; release edge cần toàn bộ ca §19.3 áp dụng cho Gate của nó đạt. Pen-test bên thứ ba **(a)** web/API/broker ACL/đường lệnh ký/multi-tenant/edge phần cứng (UART/JTAG, boot, disk)/OTA trước site production đầu tiên có `control_enabled = true` (Gate M1); **(b)** lặp lại, tập trung đường setpoint/arbiter/Governor ΔP, trước site Gate M2 đầu tiên; Critical/High đóng trước khi bật | P0 | M1 (a); M2 (b) | §19 | Báo cáo kiểm thử đính kèm release |
| **NFR-SEC-031** (mới) | Áp hàng loạt cấu hình/driver/SOE theo đợt (≤ 10 site đợt đầu, chờ 24 h), tự dừng khi có sự kiện an toàn mới | P1 | — | §14.2 | Test pipeline rollout |
| **NFR-SEC-032** (mới) | Conduit IEC 104: NIC/VLAN riêng, allow-list IP master trong cấu hình ký, chỉ type lệnh đã cấu hình, xử lý mất liên kết theo §13.2; IEC 62351 khi điện lực yêu cầu | P1 có điều kiện | — | §9.6, §10.3 | Fuzz §19.2; test điều độ |

### 20.2 NFR-REL

| ID | Yêu cầu | Ưu tiên | Gate | Đặc tả ở 10 | Kiểm chứng |
|---|---|---|---|---|---|
| NFR-REL-001 | Fail-safe mất cloud: vòng cục bộ, lịch ≥ 48 h, mặc định, lệnh tay tới hạn | P0 | M1 | §13.2 | T-NFR-REL-001-01 |
| NFR-REL-002 | Fail-safe mất edge↔thiết bị: `revert_timeout_s` 10–60 s; thiết bị không watchdog chỉ đổi chế độ native | P0 | M2 | §13.1, §13.2 | T-NFR-REL-002-01, 02 |
| NFR-REL-003 | Watchdog HW edge ≤ 10 s + `SAFE_START` | P0 | M1 | §13.4 | T-NFR-REL-003-01 |
| NFR-REL-004 | Khả dụng tách theo mặt phẳng (edge ≥ 99,95%; Command API ≥ 99,9% giờ HC / 99,5% tổng; giám sát ≥ 99,5%; bảo toàn dữ liệu ≥ 99,9%) | P0 mục tiêu; P1 SLO chính thức | M1 | §16.1 | Đo SLI |
| NFR-REL-005 | Sao lưu/khôi phục: RPO/RTO §16.2; PITR; diễn tập quý | P0 | M1 | §16.2, §16.3 | Diễn tập |
| NFR-REL-006 | Hai DC tại VN; failover 6 tháng/lần | P1 | — | §16.4 | Diễn tập |
| NFR-REL-007 | Mất `MTR_POC`/BMS cũ → BESS P = 0/native, PV giới hạn native ≤ 2 chu kỳ | P0 | M2 | §11.4, §13.2 | T-NFR-REL-007-01, 02 |
| NFR-REL-008 | Edge OFFLINE sau ≈ 90 s; cảnh báo sau 5 phút | P0 | M1 | §9.3 | Test |
| NFR-REL-009 | Tuân thủ giới hạn xuất: 0 vi phạm trong test; đưa về giới hạn ≤ 5 s (mục tiêu ≤ 2 s) | P0 | M1 | §16.1 | F-INT-27; HIL |
| NFR-REL-010 | Kill switch lan truyền ≤ 60 s | P0 | M1 | §14.4 | T-NFR-SEC-013-01 |
| NFR-REL-011 | Hết hạn chứng chỉ không dừng điều khiển cục bộ; cảnh báo trước 14 ngày | P0 | M1 | §9.2 | T-NFR-REL-011-01 |
| NFR-REL-012 | Không thi hành lệnh quá hạn sau khôi phục; đối soát ≤ 60 s | P0 | M1 | §11.7, §16.4 | T-NFR-REL-001-01 |
| **NFR-REL-013** (mới) | `run_mode` của edge theo máy trạng thái §13.4; mọi chuyển là sự kiện audit, hiển thị ở header site | P0 | M2 | §13.4 | Test chuyển trạng thái |
| **NFR-REL-014** (mới) | Bền vững khi mất nguồn edge: buffer có journal, bảng `command_id` và `last_seq` ghi bền (fsync) trước khi chấp nhận lệnh; mất nguồn đột ngột không làm hỏng cấu hình đã ký (A/B cấu hình) | P0 | M1 | §11.7 | Test cắt nguồn 100 lần ngẫu nhiên |
| **NFR-REL-015** (mới) | Control plane fail-closed: IdP/PDP/KMS/DB lệnh lỗi → không lệnh mới; monitoring độc lập | P0 | M1 | §16.5 | T-NFR-REL-015-01 |
| **NFR-REL-016** (mới) | Ưu tiên và backpressure: `event`/`cmd-ack`/`state` không bao giờ bị bỏ; quota theo edge/tenant; xả buffer có giới hạn và jitter | P0 | M1 | §9.3, §16.6 | Test tải phục hồi |
| **NFR-REL-017** (mới) | Game day mất cloud 4 h hằng quý (P0 trước Gate M2 đầu tiên); chaos KMS/broker/DR theo lịch | P0/P1 | M2 | §16.4, §19.1 | Biên bản game day |
| **NFR-REL-018** (mới) | Trình tự DR: tự engage kill switch nền tảng, khôi phục monitoring trước, kiểm chuỗi audit và `seq` sàn, mở control plane theo C3 | P1 | — | §16.4 | Diễn tập DR |

### 20.3 NFR-OBS

| ID | Yêu cầu | Ưu tiên | Đặc tả ở 10 |
|---|---|---|---|
| NFR-OBS-001 | Bộ metric tối thiểu (ingest, edge, lệnh, Governor, fallback, chứng chỉ, đồng hồ) | P0 | §17.1 |
| NFR-OBS-002 | Telemetry sức khỏe edge | P0 | §17.1 |
| NFR-OBS-003 | Log có cấu trúc, không D3/secret | P0 | §17.2 |
| NFR-OBS-004 | Trace OpenTelemetry đường lệnh 100% | P1 | §17.2 |
| NFR-OBS-005 | SLO và error budget; đóng băng release control plane khi hết budget | P1 | §16.1 |
| NFR-OBS-006 | Giám sát an ninh (đăng nhập bất thường, lệnh ngoài giờ, client mới, replay, chuỗi audit; thiết bị lạ OT ở P1) | P0/P1 | §17.1, §17.3 |
| NFR-OBS-007 | Chất lượng dữ liệu cho R8 | P0 | §17.1 |
| **NFR-OBS-008** (mới) | Danh mục cảnh báo nền tảng có mức, runbook, trực ca 24/7 từ site Gate M2 đầu tiên; danh sách cảnh báo an toàn không được gác | P0 | §17.3 |
| **NFR-OBS-009** (mới) | Forensic bundle theo (site, khoảng thời gian); log edge vòng tròn ≥ 30 ngày có `clock_state`; ghim được cửa sổ dữ liệu 1 s | P0 (bundle, log), P1 (ghim dữ liệu) | §18.4 |

<a id="s20-gate"></a>
### 20.4 Điều kiện theo Gate

Theo K §6 #27 và K §3.8 (phân pha), đã điều chỉnh theo 13 CF-28/D-03 (C3 vào Phase 1), D-12/CF-38 (TPM ở M2) và CF-32 (ACL `down/config`). Nguyên tắc: kiểm soát giới hạn bán kính tác động (C3, kill switch, Governor đếm, toàn vẹn thời gian, giới hạn tĩnh, pen-test) phải có **trước khi cloud ghi xuống site đầu tiên** (Gate M1 có `control_enabled`), vì M1 đã ghi tới nhiều site; cột M2 chỉ thêm những gì gắn với việc edge làm chủ vòng. FR-SEC-021 (hồ sơ sẵn sàng Gate M2) kiểm các mục cột M2.

| Nhóm | Gate M1 (giám sát + cấu hình native có readback) | Gate M2 (edge làm chủ vòng, setpoint) | Phase 1/2 |
|---|---|---|---|
| Xác thực, phân quyền | NFR-SEC-005, 006, 023; NFR-SEC-008 (C0–C4 + hàng đợi duyệt C3 hai người — 13 CF-28/D-03) | + PDP-04/05 nâng hạng theo ngữ cảnh MW/% SOE | SSO (P1) |
| Cô lập, dữ liệu | NFR-SEC-007, 026 (phân loại + hosting) | — | DPIA (P1); silo (P2) |
| Kênh, danh tính | NFR-SEC-002, 003 (edge thiếu TPM/SE được phép như ngoại lệ ghi rủi ro R-33), 017, 018, 027, 028 | + **edge có TPM/secure element** (không bật M2 trên edge thiếu TPM/SE — 13 D-12, CF-38) | NFR-SEC-021, 022, 032 (P1) |
| Lệnh | NFR-SEC-001, 004, 011 (mọi ghi tham số native qua edge đều ký và có hạn); NFR-SEC-009 phần `M1StaticLimits` ký, duyệt C3 hai người trong commissioning ([§11.3a](#s11-m1)); NFR-SEC-012 biến thể đếm; NFR-SEC-013 kill switch (dừng cả lịch native và `CONFIG_PUSH`) | + NFR-SEC-009 SOE đầy đủ, 010, 012 biến thể ΔP, 014 | NFR-SEC-019 (P1) |
| Audit, secrets | NFR-SEC-015 (append-only + chuỗi), 016 | — | Neo WORM (P1) |
| Độ tin cậy | NFR-REL-001, 003, 004 (mục tiêu), 005, 008, 009, 010, 011, 012, 014, 015, 016 | + NFR-REL-002, 007, 013, 017 (game day) | NFR-REL-006, 018 (P1) |
| Quan sát | NFR-OBS-001, 002, 003, 006 (phần P0), 007 | + NFR-OBS-008 (trực ca 24/7), 009 | NFR-OBS-004, 005 (P1) |
| Quy trình | NFR-SEC-024 phần P0 (SAST/SCA/secret/SBOM); NFR-SEC-030 (a): pen-test bên thứ ba web/API/broker/đường lệnh/edge phần cứng/OTA + ca lạm dụng, trước site production đầu tiên có `control_enabled = true` | + NFR-SEC-029, NFR-SEC-030 (b): pen-test lặp lại trước site M2 đầu tiên | NFR-SEC-024 đầy đủ, 025, 031 |

### 20.5 Đối chiếu với 7 nhóm yêu cầu nền tảng của IEC 62443 (kiến thức nền, chỉ để kiểm tra độ phủ)

| Nhóm (FR của 62443, kiến thức nền) | Yêu cầu của ta |
|---|---|
| Định danh và xác thực | NFR-SEC-003, 005, 023, 027 |
| Kiểm soát sử dụng | NFR-SEC-006, 008, 009, 010, 014 |
| Toàn vẹn hệ thống | NFR-SEC-004, 015, 020, 028, 030 |
| Bảo mật dữ liệu | NFR-SEC-007, 016, 026 |
| Hạn chế luồng dữ liệu | NFR-SEC-002, 017, 018, 032 |
| Phản ứng kịp thời với sự kiện | NFR-OBS-006, 008, 009; NFR-SEC-029 |
| Khả dụng tài nguyên | NFR-REL-001…018; NFR-SEC-012, 013 |

Bảng này **không** phải tuyên bố tuân thủ (K §6 #34).

---

<a id="s21"></a>
## 21. Điều kiện phát hành, câu hỏi mở, rủi ro

### 21.1 Điều kiện trước khi phát hành 10 ra ngoài đội

1. Kiểm chứng khung pháp lý Việt Nam về an ninh mạng, lưu trữ dữ liệu, dữ liệu cá nhân và thay đổi 2025–2026 (Q-I-04) → §3.3, NFR-SEC-026, NFR-SEC-029 (thời hạn thông báo), thời hạn lưu log/audit. **Điều kiện chặn** (K §3.8).
2. Kiểm chứng edition và câu chữ SL của IEC 62443-3-2/3-3/4-1/4-2/2-4 (Q-I-01) → §3.2, §20.5.
3. QĐ 1570 và yêu cầu bảo mật kênh điều độ (Q-I-03) → NFR-SEC-032.
4. Giấy phép TimescaleDB TSL (ảnh hưởng RLS/CAGG, Q-I-08) và OpenEMS (edge runtime) theo K G-13.
5. Watchdog/reversion thực tế của các model driver MVP (Q-I-07) → NFR-REL-002, bảng §13.2.

### 21.2 Câu hỏi mở (mã tạm; [13](13-open-questions-and-risks.md) cấp mã chính thức)

| ID | Câu hỏi | Ảnh hưởng | Cách giải |
|---|---|---|---|
| Q-I-01 | Edition, câu chữ SL của IEC 62443 các phần | §3, lộ trình chứng nhận | Trang IEC/ISA, ISASecure |
| Q-I-02 | NIST SP 800-82 bản hiện hành; NISTIR 7628 | Tham chiếu | csrc.nist.gov |
| Q-I-03 | IEC 62351 có bắt buộc cho IEC 104 theo QĐ 1570 không | NFR-SEC-032 | Hỏi EVN/điều độ; đọc văn bản |
| Q-I-04 | Hiện trạng luật an ninh mạng, lưu trữ dữ liệu, dữ liệu cá nhân VN 2026; thời hạn lưu trữ; thời hạn thông báo vi phạm | Hosting, retention, §18 | Tư vấn luật |
| Q-I-05 | EMS cho khách DN nhà nước có phải phân loại cấp độ hệ thống thông tin không | Yêu cầu bổ sung | Tư vấn luật |
| Q-I-06 | CRA áp cho SaaS hay chỉ edge/phần mềm cài đặt | Mở rộng EU | Đọc văn bản |
| Q-I-07 | Watchdog/reversion theo hãng (Huawei SmartLogger/EMMA, Sungrow, SMA, PCS tủ phổ biến ở VN, Victron) | NFR-REL-002 | Tài liệu Modbus + lab |
| Q-I-08 | RLS trên hypertable/CAGG của TimescaleDB | NFR-SEC-007 | PoC |
| Q-I-09 | Sự cố đã xác nhận của Solarman/Deye cloud; gán hãng cho sự cố 11/2024 | §15.4 | Tìm kiếm có nguồn |
| Q-I-10 | Grid code VN cho C&I: ramp rate, thời gian đáp ứng lệnh điều độ | SOE `ramp_max_w_per_s` | TT 05/2025, QĐ 1570 |
| Q-I-11 | UL 9540/9540A/IEC 62933-5-x có điều khoản về giao diện EMS ngoài | Ranh giới | Đọc tiêu chuẩn, tài liệu hãng BESS |
| Q-I-13 | Nhà cung cấp cloud/DC tại VN có KMS/HSM managed, object lock WORM | NFR-SEC-015/016, NFR-REL-006 | Khảo sát nhà cung cấp |
| Q-I-14 | Ngưỡng Governor 20%/5% và miễn trừ lệnh "về 0" có hợp lý | NFR-SEC-012 | Mô phỏng; hỏi điện lực |
| Q-10-01 | Phần cứng edge MVP có TPM 2.0 và secure boot không (K G-06) | NFR-SEC-003, 027 | Chọn BOM ở [06](06-system-architecture.html)/[07](07-device-integration.md) |
| Q-10-02 | Chủ C&I có chấp nhận trực ca 24/7 do installer/O&M hay do nền tảng; mô hình trách nhiệm khi sự cố ngoài giờ | NFR-OBS-008, §18.2 | Phỏng vấn (K G-07) |
| Q-10-03 | Hành vi khi mất liên kết IEC 104: giữ giới hạn chặt nhất bao lâu | §13.2 | Văn bản điều độ |

### 21.3 Rủi ro ứng viên (mã tạm; 13 cấp `R-NN`)

| ID | Rủi ro | Khả năng / Tác động | Giảm thiểu |
|---|---|---|---|
| I-R-01 | Lệnh hàng loạt do tài khoản/khóa bị chiếm | Thấp / Rất cao | Governor, kill switch, C3, WebAuthn, SOE kẹp tại edge |
| I-R-02 | Thiết bị phổ biến không có watchdog/reversion | Cao / Cao | `requires_native_fallback`; ưu tiên native; chỉ đổi chế độ |
| I-R-03 | Kênh cloud hãng song song gây xung đột điều khiển | Trung bình / Cao | Chính sách CD-06; phát hiện điều khiển ngoài |
| I-R-04 | Rò cross-tenant do cấu hình RLS/pool sai | Trung bình / Cao | Lớp lọc thứ hai; test CI |
| I-R-05 | Lộ khóa ký lệnh | Thấp / Rất cao | KMS không xuất; khóa lệnh ≠ khóa cấu hình; quy trình xoay |
| I-R-06 | Pháp lý VN (lưu trữ, dữ liệu cá nhân, thông báo) chưa kiểm chứng | Cao / Trung bình | Hosting VN mặc định; kiểm chứng trước phát hành |
| I-R-07 | Chuỗi cung ứng edge | Thấp / Rất cao | SBOM, ký build, canary |
| I-R-08 | Đồng hồ edge sai làm hỏng kiểm hạn | Trung bình / Cao | NFR-SEC-028, IL-06 |
| I-R-09 (mới) | Edge MVP không có TPM → khóa thiết bị lưu phần mềm (13 R-33) | Trung bình / Trung bình | Chỉ cho phép ở site chỉ giám sát và Gate M1 có ghi rủi ro; **không** bật Gate M2 trên edge thiếu TPM/SE (13 D-12); thay phần cứng trước Phase 2 |
| I-R-12 (mới) | Edge offline khi kill switch engage tiếp tục lịch cloud đã nhận (≤ 7 ngày) cho tới khi nối lại | Thấp / Cao | Trạng thái tạm ngưng retained, không hết hạn, đối chiếu trước khi chạy lịch sau reconnect (§14.4); cloud không gửi lịch mới; giữ horizon lịch ở mức cần thiết (≥ 48 h) thay vì tối đa 7 ngày khi không cần |
| I-R-10 (mới) | Bộ P0 an toàn quá nặng cho đội mới làm chậm Gate M2 | Cao / Trung bình | Phân pha §20.4; M1 trước, M2 theo site |
| I-R-11 (mới) | Trực ca 24/7 chưa có khi bật site M2 đầu tiên | Trung bình / Cao | NFR-OBS-008 là điều kiện M2 |

---

<a id="s22"></a>
## 22. Vấn đề gửi agent khác

| ID | Gửi | Vấn đề | Đề xuất |
|---|---|---|---|
| X-10-01 | 04 (Yêu cầu) | 10 đề xuất mã mới NFR-SEC-027…032, NFR-REL-013…018, NFR-OBS-008…009 (§20) | **Đã đóng (vòng sửa, 2026-10-10):** 04 đã thêm cả 14 mã với số giữ nguyên, có ưu tiên và gate, và thêm NFR-SEC-033 (commissioning) |
| X-10-02 | 04 | Trả lời các mục 04 §8 gửi 10: (a) danh sách cảnh báo không được gác cho BR-ALM-03 ở §17.3; (b) xác nhận lan truyền kill switch ≤ 60 s (NFR-REL-010); (c) xác nhận `T_stale_poc` 3 s làm mặc định, chỉnh 2–5 s trong SOE (Q-D-01 vẫn mở); (d) giờ hành chính mặc định 08:00–17:00 T2–T6 giờ site, cấu hình theo tenant — xác nhận; (e) BR-TAR-05: đồng ý — thay đổi làm đổi lịch tối ưu ở site có điều khiển cần `cmd.c2` | Cập nhật 04 |
| X-10-03 | 04 | Ma trận §5.4 bổ sung: tắt `control_enabled` (an toàn hóa, C1) cho OPERATOR/SITE_ENGINEER/CONTROL_SUPERVISOR/ORG_ADMIN; MFA bắt buộc cho `TECHNICIAN` (ticket là thao tác ghi) | Xác nhận hoặc điều chỉnh ma trận 04 §3.4 |
| X-10-04 | 05 / 07 | Tên trạng thái phê duyệt lệch: 04 và 05 dùng `APPROVAL_REJECTED`, 07 §8.4 dùng `APPROVAL_DENIED`. 10 dùng `APPROVAL_REJECTED` theo 05 | 07 sửa theo 05 |
| X-10-05 | 05 | Trường audit bổ sung: `pdp_decision_id`, `breakglass`, `edge_clock_state`, `source_seq`; `CommandApproval.content_hash` (hash nội dung lệnh được duyệt); `RemoteControlSuspension.auto_reason` | Thêm vào §11, §14 của 05 |
| X-10-06 | 07 (Tích hợp) | Chốt chữ ký: JCS (RFC 8785) + JWS ES256, header `typ`; `seq` theo `(site, signer kid)` + `seq_floor` trong cấu hình ký; `REMOTE_CONTROL_SUSPEND` không hết hạn; đề xuất lệnh C0 "ghim cửa sổ dữ liệu 1 s" cho điều tra (NFR-OBS-009) | Cập nhật §8.1–§8.2 của 07 |
| X-10-07 | 06 (Kiến trúc) | ADR: cloud gửi ý định có hạn; ký tầng ứng dụng (JCS+JWS); hai mặt phẳng; RLS + silo; Fleet Governor; PDP engine; khóa lệnh ≠ khóa cấu hình; DR có kill switch tự động. Vẽ SVG zone/conduit theo mô tả §10.1 | Viết ADR, sơ đồ |
| X-10-08 | 08 (Tối ưu) | Bộ sinh lịch là principal dịch vụ chịu PDP + Governor; validator giới hạn thay đổi 30%/slot; tự trải jitter khi vượt ngân sách | Thêm ràng buộc vào validator |
| X-10-09 | 09 (UX/UI) | Màn: hàng đợi duyệt C3 (diff, MW, % ngân sách Governor, hạn); trạng thái điều khiển site (LOCAL/REMOTE, kill switch, Gate, SOE, interlock, `run_mode`); "Tạm ngưng điều khiển từ xa"; "Dừng vận hành từ xa"; không nút E-stop; trạng thái lệnh không lạc quan; mã lý do từ chối PDP dễ hiểu | Cấp UI-NN |
| X-10-10 | 11 (Lộ trình) | Site M1 có điều khiển đầu tiên cần: pen-test bên thứ ba (a), C3 hai người, kill switch, Governor đếm, `M1StaticLimits`, toàn vẹn thời gian, HIL §19.3 phần M1. Gate M2 cho site đầu tiên cần thêm: pen-test (b), game day mất cloud, trực ca 24/7, HIL §19.3 đầy đủ, edge có TPM/SE (13 D-12). Chứng nhận: ISO 27001 (Phase 1–2), IEC 62443-4-2 cho edge (Phase 2) | Đưa vào lộ trình |
| X-10-11 | 13 (Rủi ro) | Rủi ro I-R-01…11, câu hỏi Q-I-01…14, Q-10-01…03 | Cấp `R-NN`, `Q-NN` |
| X-10-12 | 14 (Nguồn) | Danh sách URL ở §23; nội dung tiêu chuẩn/luật không URL là kiến thức nền | Cấp S-xxx; đánh dấu Low/Med |
| X-10-13 | 03 (Danh mục) | Đã ghi vào [notes/_catalog-gaps.md](notes/_catalog-gaps.md): gói bằng chứng sự cố (forensic bundle) và sổ sự cố bảo mật/an toàn | Người viết 03 xử lý |
| X-10-14 | 04 (Yêu cầu) | Cột Gate: NFR-SEC-008, 013, 028, NFR-REL-010 chuyển M1; NFR-SEC-012 tách M1 (đếm)/M2 (ΔP); NFR-SEC-009 thêm phần M1 `M1StaticLimits`; NFR-SEC-030 tách (a) M1 / (b) M2 (13 CF-28/D-03). Ma trận §3.4: vai trò được đổi `SiteControlConfig.default_strategy` (C2) — 10 đề xuất SITE_ENGINEER, CONTROL_SUPERVISOR | Cập nhật §6 và ma trận |
| X-10-15 | 05 (Mô hình miền) | Thêm `M1StaticLimits` (tập con SOE, cùng lược đồ; trường mới `pv_limit_min_w`, `pv_limit_max_w`) và `RemoteControlSuspension.state_version`; trạng thái báo cáo edge thêm `remote_control_state_version`. Tin trạng thái MAINTENANCE dùng `BAD_COMM` + lý do khoảng trống `MAINTENANCE` (10 không cần mã `BAD_NOT_CONNECTED`) | Thêm vào §6, §11 |
| X-10-16 | 07 (Tích hợp) / 06 (Kiến trúc) | Tin `REMOTE_CONTROL_STATE` ký, retained trên `down/config`; edge đối chiếu trước khi nối lại lịch cloud sau reconnect; S16 báo `remote_control_state_version`. Bước 9 chuỗi kiểm edge §8.7 dùng `M1StaticLimits` cho site M1. ACL `svc-ingest-ack` chỉ `TELEMETRY_ACK`/`RESEND_REQUEST` (ADR-16, CF-32) | Cập nhật 07 §7.1, §8.7; ADR ở 06 |
| X-10-17 | 08 (Tối ưu) | Bộ sinh lịch tầng 2 có `run_id` và trần `max_sites_per_run` từ Gate M1; dừng khi kill switch engage | Thêm vào validator/scheduler |

---

<a id="s23"></a>
## 23. Nguồn

Mọi URL dưới đây đã xuất hiện trong ghi chú nghiên cứu của dự án hoặc nghiên cứu FusionSolar trước; tài liệu này **không mở trực tiếp** URL nào và không có lượt tìm kiếm mới (hạn mức đã hết). Nội dung được ghi nhận qua kết quả tìm kiếm (snippet) hoặc qua ghi chú nghiên cứu trước. Mã S-xxx do [14 Nguồn](14-source-register.md) cấp.

**Thiết bị, giao thức**
- https://support.huawei.com/enterprise/en/doc/EDOC1100108365/4fbe151e/setting-parameters-for-connecting-to-the-management-system-v300r001c00 — SmartLogger3000: kết nối outbound mã hóa (nghiên cứu FusionSolar trước)
- https://support.huawei.com/enterprise/en/doc/EDOC1100273864/2b6a3248/set — Hướng dẫn commissioning, cổng 27250 (nghiên cứu FusionSolar trước)
- https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11411391 — Patent ESS, tín hiệu bảo vệ BMS→PCS qua dây cứng (ghi chú E)
- https://sunspec.org/communication-interface-defects-revealed-inul-1741-sb-certified-inverters/ — Lỗi giao diện SunSpec ở inverter có UL 1741 SB (ghi chú E)
- https://sunspec.org/sunspec-1547-initiative/ — IEEE 1547-2018 và giao diện truyền thông (nghiên cứu FusionSolar trước)
- https://openchargealliance.org/?p=159286 — OCPP 1.6J Security Whitepaper (ghi chú E)
- https://developer.easee.com/docs/ocpp-smart-charging ; https://www.bender.de/docs/charge-controller/OCPP/ocpp-smart-charging/ — Charging profile OCPP theo hãng (ghi chú E)
- https://standards.ieee.org/content/dam/ieee-standards/standards/web/documents/presentations/smart_energy_slides.pdf — IEEE 2030.5, TLS + chứng chỉ (ghi chú E)

**Chứng nhận, tuyên bố của hãng**
- https://cdn.contentspeed.ro/pimromstal.websales.ro/cs-content/cs-docs/products/35fv1635569certificateredforsun2000map0sun5000map0_78205_21_1784579986.pdf — Chứng chỉ RED/EN 18031-1:2024 cho inverter + dongle Huawei (nghiên cứu FusionSolar trước)
- https://solar.huawei.com/en/service-support/tsc/warranty-terms-and-conditions — Huawei PSTI: cập nhật bảo mật tới 31/12/2029 (nghiên cứu FusionSolar trước)
- https://www.productinfo.schneider-electric.com/esxp_digital_apps_iec/transverse/English/BM_ESXP_DG_Transverse_Section_IEC_0001148082.xml/$/ESXP_DG_SYSD_Cyber_ISA_IEC_0001157270 — Schneider, kiến trúc IEC 62443-3-3 (ghi chú B)
- https://www.winccoa.com/documentation/WinCCOA/3.20/en_US/iec_62443/topics/iec_62443_certification.html — WinCC OA, chứng chỉ IEC 62443-4-1/4-2 (ghi chú B)
- https://dl.sungrowpower.com/en/sungrow-achieves-iso-iec-27019-and-multiple-cybersecurity-management-system-certifications-from-bsi — Sungrow ISO/IEC 27019 (nghiên cứu FusionSolar trước)
- https://ampowr.com/nis2-compliance/ — Ampowr tự tuyên bố ISO 27001/NIS2 (ghi chú B)
- https://digitalpower.huawei.com/en/eu-data-act ; https://e-solarshop.ro/wp-content/uploads/2025/07/fusionsolar-app-manual5925.pdf — Huawei: ủy quyền của chủ hệ thống cho installer/bên thứ ba (nghiên cứu FusionSolar trước)
- https://community.home-assistant.io/t/fusion-solar-doesnt-work-anymore/927417 — Huawei 9/2025 đổi chính sách cấp quyền API (nghiên cứu FusionSolar trước)

**Sự cố, an ninh mạng, quản lý**
- https://www.defensenews.com/global/europe/2025/05/29/chinese-hold-on-solar-power-tech-raises-fresh-sabotage-fears-in-europe/ — Vô hiệu hóa từ xa 11/2024 do tranh chấp thương mại (nghiên cứu FusionSolar trước)
- https://forescout.com/press-releases/forescout-vedere-labs-uncovers-severe-systemic-security-risks-in-global-solar-power-infrastructure — Forescout SUN:DOWN (nghiên cứu FusionSolar trước)
- https://cybernews.com/security/china-solar-inverters-hack/ — CCC/Hoymiles (nghiên cứu FusionSolar trước)
- https://www.pv-magazine.com/2025/05/14/hidden-devices-found-in-chinese-made-inverters-in-the-us-reports-reuters/ — Reuters qua pv magazine (nghiên cứu FusionSolar trước)
- https://www.pv-magazine-india.com/2026/01/29/u-s-authorities-find-no-definitive-evidence-of-hidden-devices-in-chinese-solar-inverters — Đánh giá của DOE 1/2026 (nghiên cứu FusionSolar trước)
- https://www.lrt.lt/en/news-in-english/19/2411602/lithuania-passes-law-to-block-chinese-access-to-solar-and-wind-farm-systems ; https://pv-tech.org/lithuania-to-block-chinese-inverters-with-cybersecurity-legislation — Luật Lithuania (nghiên cứu FusionSolar trước)
- https://solarmagazine.nl/nieuws-zonne-energie/i41070/kabinet-verscherpt-toezicht-op-chinese-omvormers-zonnepanelen-verbod-kill-switch-bestaat-al — Hà Lan: RED từ 1/8/2025, CRA từ 12/2027 (nghiên cứu FusionSolar trước)
- http://www.pv-magazine.com/2026/01/20/eu-to-ban-chinese-inverters-commission-proposal-in-cybersecurity-mulls-high-risk-vendors-list/ — Đề xuất danh sách nhà cung cấp rủi ro cao của EU (nghiên cứu FusionSolar trước)
- https://www.ess-news.com/2026/05/04/eu-funding-ban-on-high-risk-inverters-including-chinese-suppliers-extends-to-bess-pcs/ — EU chặn tài trợ cho inverter/BESS của nhà cung cấp rủi ro cao (nghiên cứu FusionSolar trước)
- https://www.innobu.com/en/articles/chinese-inverters-security-risk-high-risk-list-2026.html — Phân tích: ưu tiên điều khiển cục bộ qua smart-meter gateway ở Đức (nghiên cứu FusionSolar trước)

**Tài liệu nội bộ dự án**
- [notes/I-security-reliability.md](notes/I-security-reliability.md), [notes/K-review-round1.md](notes/K-review-round1.md), [notes/E-device-integration.md](notes/E-device-integration.md), [notes/C-energy-domain.md](notes/C-energy-domain.md), [notes/G-optimization.md](notes/G-optimization.md), [notes/B-competitors.md](notes/B-competitors.md)
- [03 Danh mục chức năng](03-functional-catalog.html), [04 Yêu cầu](04-business-requirements.md), [05 Domain](05-domain-model.html), [07 Tích hợp](07-device-integration.md)
- [../fusionsolar/04_ghi_chu_nghien_cuu/1_tong_quan/architecture_security.md](../fusionsolar/04_ghi_chu_nghien_cuu/1_tong_quan/architecture_security.md)

**Kiến thức nền chưa kiểm chứng URL** (không dùng làm FACT): IEC 62443 (các phần, SL, 7 FR), NIST SP 800-82, NISTIR 7628, IEC 62351, UL 9540/9540A, IEC 62933-5-x, ETSI EN 303 645, IEEE 1547.3, EU NIS2/CRA (số hiệu), RFC 7515/8785, mô hình Purdue, sự cố Ukraine 2015/2016, SunSpec model 123/704 (trường reversion), tham số fallback của SMA, `apiTimeout` của OpenEMS, luật Việt Nam về an ninh mạng và dữ liệu cá nhân.
