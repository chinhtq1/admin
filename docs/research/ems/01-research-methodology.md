# 01 — Phương pháp nghiên cứu

[← Mục lục](index.html) · [00 Tóm tắt](00-executive-summary.html) · [02 Thị trường](02-market-and-competitor-analysis.html) · [03 Chức năng](03-functional-catalog.html) · [04 Yêu cầu](04-business-requirements.md) · [11 Lộ trình](11-mvp-and-roadmap.html) · [12 Truy vết](12-traceability-matrix.md) · [13 Rủi ro](13-open-questions-and-risks.md) · [14 Nguồn](14-source-register.md) · [K vòng 1](notes/K-review-round1.md) · [15 Mô phỏng](15-simulators-and-messaging.md)

- **Phiên bản:** 1.0 · **Ngày:** 2026-10-10 · **Trạng thái:** bản phát hành nội bộ.
- **Người viết:** Source Registrar (sở hữu file này và [14-source-register.md](14-source-register.md)).
- **Mục đích:** mô tả nghiên cứu EMS được làm thế nào, dựa trên bằng chứng gì, tin được đến đâu, và phải làm gì để nâng độ tin cậy trước khi xây sản phẩm. Người đọc chính: product owner, kiến trúc sư, người duyệt kỹ thuật/pháp lý, và mọi agent hay người viết tiếp bộ tài liệu.

---

## Mục lục

- [1. Bối cảnh và phạm vi](#1-bối-cảnh-và-phạm-vi)
- [2. Câu hỏi nghiên cứu](#2-câu-hỏi-nghiên-cứu)
- [3. Cấu trúc nhóm và quyền sở hữu](#3-cấu-trúc-nhóm-và-quyền-sở-hữu)
- [4. Quy trình](#4-quy-trình)
- [5. Phương pháp bằng chứng](#5-phương-pháp-bằng-chứng)
- [6. Giới hạn mạng và hệ quả lên độ tin cậy](#6-giới-hạn-mạng-và-hệ-quả-lên-độ-tin-cậy)
- [7. Cách xử lý tuyên bố của hãng](#7-cách-xử-lý-tuyên-bố-của-hãng)
- [8. Giới hạn và mối đe dọa tới tính hợp lệ](#8-giới-hạn-và-mối-đe-dọa-tới-tính-hợp-lệ)
- [9. Cách mở rộng và kiểm chứng nghiên cứu](#9-cách-mở-rộng-và-kiểm-chứng-nghiên-cứu)
- [10. Vấn đề gửi agent khác](#10-vấn-đề-gửi-agent-khác)

---

## 1. Bối cảnh và phạm vi

### 1.1 Điểm xuất phát

- [FACT] Dự án đã reverse-engineer Huawei FusionSolar ngày 07/10/2026. Kết quả ở `docs/research/fusionsolar/`: báo cáo, wireframe 15 màn hình, 11 ghi chú nghiên cứu, 9 ảnh demo thật (S-388…S-403 trong [14 §3](14-source-register.md#3-tệp-nghiên-cứu-trước-s-388s-403)).
- [FACT] Hướng trước đó: nền tảng giám sát/O&M PV đa hãng, edge-first, cho installer và đơn vị O&M C&I tại Việt Nam; Java/Spring Boot + Angular; TimescaleDB/PostgreSQL; MQTT; edge kiểu OpenEMS (S-388). (Cập nhật 2026-10-10: frontend EMS là React + TypeScript theo quyết định product owner, [06 ADR-20](06-system-architecture.html#adr-20); backend Spring Boot giữ nguyên.)
- Người dùng giao hai trang hạt giống: Ampowr Cosmos (S-080) và trang "What is EMS" của HT InfinitePower (S-095). Trang InfinitePower chỉ được dùng cho định nghĩa chung, có nguồn thứ hai đi kèm (S-330), theo phán quyết K R-18.

### 1.2 Phạm vi nghiên cứu EMS

**Trong phạm vi.** EMS phía sau công tơ (behind-the-meter) cho C&I đa site, đa hãng: PV, BESS, lưới, phụ tải, EV tùy chọn. Nền là lớp giám sát/O&M. Site chỉ có PV là công dân hạng nhất. BESS và EV là tùy chọn; điều khiển EV là P1. Nguồn: phán quyết thống nhất của [K §6](notes/K-review-round1.md).

**Ngoài phạm vi 12–18 tháng.** Nền tảng ESG, SCADA/EMS lưới (TSO/DSO), chuyển đổi microgrid (islanding, black start), giao dịch thị trường điện. Các chủ đề này vẫn được nghiên cứu ở mức đủ để vạch ranh giới sản phẩm ([02](02-market-and-competitor-analysis.html)).

**Thị trường chính.** Việt Nam. Bối cảnh EU/Mỹ/Úc chỉ dùng để so sánh (EL-030, EL-037, EL-096 trong [14 §5](14-source-register.md#5-evidence-ledger-100-claim-quan-trọng-nhất)).

### 1.3 Kế thừa và khác biệt so với hướng cũ

| Chủ đề | Hướng FusionSolar trước | Quyết định EMS | Lý do |
|---|---|---|---|
| Phạm vi | Giám sát/O&M PV | Giám sát/O&M + điều khiển BESS/lưới/EV theo hai cổng M1/M2 | Mở rộng có chủ đích; giám sát vẫn là nền (K R-08) |
| Quy ước dấu | Lưới + = xuất (theo Huawei `meterPower`) | Lưới + = nhập, BESS + = xả | Khớp OpenEMS và OBIS A+; mọi trần thành số dương (K R-01; EL-048, EL-080) |
| Edge | Edge kiểu OpenEMS cho thu thập | Edge bắt buộc ở site có lệnh; cloud không bao giờ ghi thẳng thiết bị | An toàn lệnh; cloud hãng là pull có hạn mức (K R-09; EL-027, EL-028) |
| Ngôn ngữ tối ưu | Java | Java cho tầng 1–2; sidecar Python cho tầng 3 chỉ qua ADR | Ngoại lệ có chủ đích (K R-22) |
| Lưu trữ | TimescaleDB | TimescaleDB + Parquet, **có điều kiện** kiểm tra giấy phép TSL và PoC 1.000 site | EL-090, EL-092 |
| Nhãn mức cảnh báo | S1 Nghiêm trọng … S4 Cảnh báo | Khẩn cấp / Cao / Trung bình / Thông tin | "Cảnh báo" vừa là tên chung vừa là tên mức (K R-26) |

---

## 2. Câu hỏi nghiên cứu

| Mã | Câu hỏi | Chủ trì | Trả lời ở | Trạng thái 2026-10-10 |
|---|---|---|---|---|
| RQ-01 | EMS gồm những nhóm sản phẩm nào, khác nhau ở đâu, ta nên đứng ở nhóm nào? | A | [02](02-market-and-competitor-analysis.html), nA §3.1–3.7 | Đã chốt (K §6); điểm chấm cần trọng số rõ |
| RQ-02 | Động lực pháp lý và biểu giá ở Việt Nam tạo giá trị gì cho EMS C&I? | A, C | 02, [04](04-business-requirements.md), [08](08-energy-optimization.md) §giá trị | Có hướng; chi tiết văn bản **chưa kiểm chứng** (V-01…V-05) |
| RQ-03 | Đối thủ thật sự cung cấp gì (có tài liệu), và khác biệt nằm ở đâu? | B | 02 | 11 sản phẩm có ma trận; thiếu Deye/Solarman, Growatt, Solis C&I (K G-08) |
| RQ-04 | Đại lượng, quy ước dấu, cân bằng năng lượng, KPI và cách tính đúng? | C | [05](05-domain-model.html), 04 | Đã chốt hợp đồng dữ liệu (K R-01…K R-06) |
| RQ-05 | Tích hợp thiết bị bằng giao thức nào, giới hạn gì, vòng nhanh đặt ở đâu? | E | [07](07-device-integration.md) | Có kiến trúc; register map hãng **chưa kiểm chứng** (V-10) |
| RQ-06 | Lưu trữ, tổng hợp, chất lượng dữ liệu, dự báo cho 1.000+ site? | F | 05, [06](06-system-architecture.html) | Có thiết kế; cần PoC và kiểm tra giấy phép (V-07) |
| RQ-07 | Chiến lược tối ưu nào, tầng điều khiển nào, giải xung đột ưu tiên ra sao? | G | 08 | Đã chốt arbiter 12 mức (K R-07); tầng 3 là P1 |
| RQ-08 | UX cho fleet đa site, lệnh nguy hiểm, dữ liệu cũ, song ngữ? | H | [09](09-ux-ui-specification.html) | Có đặc tả; bằng chứng UI đối thủ chỉ có FusionSolar |
| RQ-09 | Điều khiển từ xa an toàn thế nào: phân quyền, lệnh có hạn, fail-safe, audit? | I | [10](10-security-and-reliability.md) | Có bộ P0 cho Gate M2; khung luật VN **chưa kiểm chứng** (V-06) |
| RQ-10 | Kiến trúc hệ thống và stack? | J | 06 | Có; phụ thuộc ADR giấy phép (V-07, V-08) |
| RQ-11 | Chức năng và yêu cầu nghiệp vụ nào ở MVP? | D | [03](03-functional-catalog.html), 04 | Có; mã FR/NFR chính thức do 04 cấp |
| RQ-12 | MVP, lộ trình, rủi ro, câu hỏi mở? | Lead + J | [11](11-mvp-and-roadmap.html), [13](13-open-questions-and-risks.md) | Có bản vòng 1 |
| RQ-13 | Bằng chứng nào mạnh, nào yếu, nào mâu thuẫn? | K, Registrar | [K](notes/K-review-round1.md), [14](14-source-register.md) | Vòng 1 xong; spot-check online **không làm được** |
| RQ-14 | Khách hàng Việt Nam thật sự cần gì và trả tiền cho gì? | — | — | **Chưa làm.** Toàn bộ là nghiên cứu tại bàn (K G-07) |

---

## 3. Cấu trúc nhóm và quyền sở hữu

Mỗi file chỉ có một người viết tại một thời điểm. Ghi chú nghiên cứu nằm ở `notes/<agent>-<chủ-đề>.md`, chỉ agent đó ghi. Agent phát hiện lỗi ở file của người khác thì ghi vào mục "Vấn đề gửi agent khác" trong file của mình ([_conventions](notes/_conventions.md)).

| Agent / vai trò | Trọng tâm | Ghi chú nghiên cứu | Deliverable sở hữu | Tìm kiếm web trong lượt |
|---|---|---|---|---|
| A — Industry & Market Research + Product Boundary | Nhóm sản phẩm, phân khúc, pháp lý/biểu giá VN | [A-market-boundary.md](notes/A-market-boundary.md) | (đầu vào 00, 02, 04, 11, 13) | Có |
| B — Competitor Product Analyst | 11 sản phẩm đối thủ, ma trận tính năng | [B-competitors.md](notes/B-competitors.md) | [02](02-market-and-competitor-analysis.html) | Có |
| C — Energy Domain Expert | Đại lượng, dấu, cân bằng, pin, lưới, KPI | [C-energy-domain.md](notes/C-energy-domain.md) | (đầu vào 04, 05, 07, 08, 09, 10) | Có |
| D — Functional Business Analyst | Danh mục chức năng, yêu cầu nghiệp vụ | (không có ghi chú riêng) | [03](03-functional-catalog.html), [04](04-business-requirements.md) | Không rõ; dùng ghi chú |
| E — Device & Integration Architect | Giao thức, edge, hợp đồng điểm/lệnh | [E-device-integration.md](notes/E-device-integration.md) | [07](07-device-integration.md) | Có |
| F — Data & Analytics Architect | Telemetry, lưu trữ, tổng hợp, chất lượng, dự báo | [F-data-analytics.md](notes/F-data-analytics.md) | [05](05-domain-model.html) | Một phần (hết hạn mức giữa chừng) |
| G — Energy Optimization Specialist | Chiến lược, tầng điều khiển, MILP, arbiter | [G-optimization.md](notes/G-optimization.md) | [08](08-energy-optimization.md) | Không (hạn mức đã hết) |
| H — UX/UI Researcher | IA, trang, lệnh nguy hiểm, trạng thái dữ liệu | [H-ux-research.md](notes/H-ux-research.md) | [09](09-ux-ui-specification.html) | Không |
| I — Security & Reliability Reviewer | RBAC/ABAC, an toàn lệnh, fail-safe, audit, SLO | [I-security-reliability.md](notes/I-security-reliability.md) | [10](10-security-and-reliability.md) | Không |
| J — System Architect | Kiến trúc, stack, ADR | — | [06](06-system-architecture.html); phối hợp 11, 13 | Không (truy vấn bị từ chối) |
| K — Evidence Judge / Red Team | Phản biện, phán quyết mâu thuẫn, quyết định thống nhất | [K-review-round1.md](notes/K-review-round1.md) | (ràng buộc mọi tài liệu) | Không (hạn mức đã hết) |
| Product/Delivery Lead | MVP, lộ trình, rủi ro | — | [11](11-mvp-and-roadmap.html), [13](13-open-questions-and-risks.md) | Không |
| Source Registrar | Sổ nguồn, phương pháp | — | [01](01-research-methodology.md), [14](14-source-register.md) | Không (1 truy vấn bị từ chối) |
| Người viết 00 và 12 | Tóm tắt điều hành, ma trận truy vết | — | 00, 12 (chưa có tại thời điểm viết file này) | — |

**Tệp dùng chung.** [_conventions.md](notes/_conventions.md) (ngôn ngữ, nhãn, mã, HTML/Markdown) và [_catalog-gaps.md](notes/_catalog-gaps.md) (khoảng trống của 03 do các agent ghi thêm, người viết 03 xử lý).

**Quy tắc mã định danh.** Mã FR/NFR trong `notes/` là tạm thời. Chỉ người viết 04 (FR/NFR), 06 (ADR), 09 (UI) và 13 (R/Q) cấp mã chính thức, và giữ dấu vết về mã tạm. Mã nguồn `S-xxx` chỉ do 14 cấp; mã claim `EL-xxx` và việc kiểm chứng `V-xx` cũng do 14 cấp.

---

## 4. Quy trình

Quy trình có chín bước. Bước 1–4 đã xong ở vòng 1. Bước 5–6 đã có bản 1.0. Bước 7–9 đang chạy.

| Bước | Tên | Đầu vào | Đầu ra | Ai |
|---|---|---|---|---|
| 1 | **Research** | Đề bài, trang seed, nghiên cứu FS trước, WebSearch | 8 ghi chú `notes/A…I` có evidence ledger | A, B, C, E, F, G, H, I |
| 2 | **Challenge** | 8 ghi chú | Mâu thuẫn, claim bị bác/hạ cấp, chủ đề thiếu, kiểm tra số học | K ([K §1–§5](notes/K-review-round1.md)) |
| 3 | **Anchor** | Kết quả bước 2 | 27 phán quyết K R-01…K R-27 và danh sách quyết định thống nhất (K §6), ràng buộc mọi người viết | K |
| 4 | **Specify** | Ghi chú + K | Danh mục chức năng, yêu cầu nghiệp vụ, mô hình miền | D (03, 04), F (05) |
| 5 | **Architect** | 03–05 + ghi chú | Kiến trúc, tích hợp, tối ưu, UX, an toàn | J (06), E (07), G (08), H (09), I (10) |
| 6 | **Plan** | 02–10 | MVP hai cổng M1/M2, lộ trình, rủi ro, câu hỏi mở | Lead + J (11, 13) |
| 7 | **Review** | 02–13 | Rà soát chéo vòng 2 (kế hoạch); khoảng trống ghi ở `_catalog-gaps.md` | K / người duyệt |
| 8 | **Fix** | Kết quả rà soát | Bản sửa của từng deliverable bởi chủ sở hữu | Chủ sở hữu từng file |
| 9 | **Summarize** | Toàn bộ | 00 tóm tắt, 01 phương pháp, 12 truy vết, 14 sổ nguồn | Người viết 00/12, Registrar |

**Kiểm tra trong quy trình.**

- Mỗi ghi chú bắt buộc có bảy mục: phạm vi/câu hỏi, phát hiện chính, phân tích, hệ quả thiết kế, evidence ledger, UNKNOWN, vấn đề gửi agent khác.
- K tính lại mọi phép tính trong ghi chú (ví dụ arbitrage 2.076 đ/kWh; tràn uint16 0,1 kWh sau ≈ 1,37 ngày; khung RTU 255 byte ≈ 292 ms). Tất cả đúng.
- Registrar quét toàn bộ URL bằng script, gộp trùng, đối chiếu với nghiên cứu FS trước và cấp S-ID ([14 §1](14-source-register.md#1-thống-kê-nhanh)).

---

## 5. Phương pháp bằng chứng

### 5.1 Nhãn bằng chứng

| Nhãn | Định nghĩa | Điều kiện tối thiểu | Ví dụ |
|---|---|---|---|
| `FACT` | Có nguồn đáng tin hỗ trợ **trực tiếp** | URL hoặc S-ID; ghi cách tiếp cận ("qua kết quả tìm kiếm", "nghiên cứu FS trước"); phạm vi của claim không rộng hơn nguồn | EL-009 khung giờ QĐ 963 |
| `INFERENCE` | Kết luận suy ra từ bằng chứng | Nêu bằng chứng gốc; được dùng cho câu tổng quát hóa ("đa số", "các sản phẩm có tài liệu…") | EL-046 peak shaving là table stakes |
| `PROPOSAL` | Đề xuất cho sản phẩm của ta | Không cần nguồn; phải nhất quán với K §6 | Lịch dự phòng ≥ 48 h tại edge |
| `UNKNOWN` | Chưa đủ bằng chứng hoặc nguồn mâu thuẫn chưa giải | Nêu cần kiểm chứng gì | EL-016 cơ sở tính giá công suất |

Trong Markdown viết `[FACT]`; trong HTML dùng `<span class="tag fact">FACT</span>`. Ma trận đối thủ dùng thêm `Verified / Partial / Unknown / NA`, trong đó `Verified` nghĩa là **hãng tuyên bố trong tài liệu**, không phải đã kiểm thử độc lập. Ô dựa trên tuyên bố qua báo chí ghi `V*`.

**Bổ nhãn độ tin cậy.** FACT có thêm mức High/Med/Low theo thang ở [14 §0.1](14-source-register.md#01-thang-độ-tin-cậy). Ví dụ `[FACT, Med]`.

**Quy tắc hạ nhãn (do K áp dụng).**

1. Câu có "mọi", "tất cả", "thống trị", "bắt buộc cho mọi site" mà dựa trên mẫu nhỏ → `INFERENCE`.
2. Hai nguồn mâu thuẫn chưa giải → `UNKNOWN` cho phần mâu thuẫn, giữ `FACT` cho phần các nguồn đồng ý (ví dụ K R-16).
3. Nguồn do AI sinh (rfp.wiki) → loại khỏi vai trò bằng chứng.
4. Nguồn vendor có lợi ích thương mại trực tiếp với claim (Advantech về QĐ 1570) → `FACT, Low`, không làm NFR.
5. Thanh ghi từ diễn đàn → `FACT, Low` "cộng đồng báo cáo"; cấm dùng cho driver đã kiểm chứng.
6. Kiến thức nền không có URL trong phiên (IEC 62443, ISA-101/18.2, NĐ 53/2022…) → `INFERENCE` hoặc `UNKNOWN`, edition `UNKNOWN`, không tuyên bố tuân thủ.

### 5.2 Thứ tự ưu tiên nguồn

| Bậc | Loại nguồn | Dùng cho | Ghi chú |
|---|---|---|---|
| 1 | Văn bản pháp luật gốc, tiêu chuẩn gốc, tài liệu kỹ thuật chính thức của hãng (manual, datasheet, API doc) về sản phẩm của chính hãng | Yêu cầu bắt buộc, driver, NFR | Chưa đọc toàn văn bản nào trong lượt EMS (§6) |
| 2 | Quan sát trực tiếp (ảnh demo, network trace, đọc mã nguồn) | UX, hành vi API, quy ước dữ liệu | Có cho FusionSolar (S-396…S-403) |
| 3 | Mô tả của tổ chức tiêu chuẩn/cơ quan (webstore IEC, trang OCA, cổng tra cứu văn bản) | Phạm vi tiêu chuẩn, ngày hiệu lực | Cổng tra cứu VN là bên thứ ba |
| 4 | Phân tích của luật sư, phòng thí nghiệm quốc gia, bài báo khoa học | Diễn giải pháp lý, số liệu kỹ thuật | Cần nguồn bậc 1 trước khi thành yêu cầu |
| 5 | Báo chí ngành, thông cáo báo chí, trang marketing của hãng | Bối cảnh thị trường, sự tồn tại của tính năng | Tuyên bố hiệu năng/chứng nhận ghi "tự công bố" |
| 6 | Tài liệu bên thứ ba, nhà phân phối, mirror | Bổ sung chi tiết khi bậc 1 không truy cập được | Ghi rõ "mirror" |
| 7 | Diễn đàn, mã cộng đồng, blog cá nhân | Định hướng câu hỏi, test case, rủi ro tương thích | Không làm cơ sở yêu cầu |
| — | Nội dung AI sinh | Không dùng | rfp.wiki bị loại |

### 5.3 Evidence ledger

Mỗi ghi chú có ledger riêng (claim, URL, loại/ngày, trích, độ tin cậy, mâu thuẫn, hệ quả). Registrar hợp nhất 100 claim quan trọng nhất vào [14 §5](14-source-register.md#5-evidence-ledger-100-claim-quan-trọng-nhất) với mã EL-001…EL-100, tiêu chí chọn: ảnh hưởng tới quyết định P0/MVP, yêu cầu bắt buộc, kiến trúc, hoặc tuyên bố ra bên ngoài.

### 5.4 Quy tắc chống sai lệch có chủ đích

- Không gán cho hãng tính năng không có tài liệu. "Không có tài liệu" ≠ "không hỗ trợ".
- Không gọi luật cố định là AI. Chỉ gọi AI/ML khi là mô hình học đã được đánh giá.
- Không trình bày tính năng mô phỏng như tính năng thật; số ước tính/mô phỏng mang nhãn.
- Không tuyên bố tuân thủ khi chưa có chứng chỉ hoặc chưa đọc tiêu chuẩn.
- Không quảng cáo % tiết kiệm; tiết kiệm luôn là shadow bill so với baseline đối chứng trên cùng phiên bản biểu giá.
- Không bịa URL. Registrar xác nhận: mọi URL trong bộ tài liệu hoặc xuất hiện kèm ngữ cảnh snippet trong ghi chú, hoặc truy được về nghiên cứu FS trước ([14 §4](14-source-register.md#4-url-đáng-ngờ-nguồn-bị-loại-và-chuỗi-không-phải-nguồn)).

---

## 6. Giới hạn mạng và hệ quả lên độ tin cậy

### 6.1 Điều kiện thực tế

- [FACT] Môi trường chặn fetch trực tiếp (WebFetch/curl). Chỉ WebSearch hoạt động.
- [FACT] WebSearch có hạn mức **200 truy vấn dùng chung** cho mọi agent trong lượt chạy. Hạn mức hết khi F đang làm. G, H, I, J, K và Registrar không chạy được truy vấn mới; K không spot-check được claim nào; truy vấn spot-check duy nhất của Registrar cũng bị từ chối.
- [FACT] Bằng chứng mới của lượt EMS vì vậy chỉ gồm **tiêu đề + đoạn trích/tóm tắt do công cụ tìm kiếm trả về** cho từng URL. Agent ghi "(qua kết quả tìm kiếm)".
- [FACT] Thống kê ([14 §1](14-source-register.md#1-thống-kê-nhanh)): 387 nguồn URL; 319 chỉ qua snippet; 68 đã có trong nghiên cứu FS trước; 0 được fetch trong lượt EMS; 0 văn bản pháp luật hay tiêu chuẩn được đọc toàn văn.

### 6.2 Hệ quả

| Hệ quả | Mức ảnh hưởng | Cách đã xử lý |
|---|---|---|
| Không biết ngữ cảnh đầy đủ của câu trích (điều kiện, ngoại lệ, phiên bản) | Cao với pháp lý và tiêu chuẩn | Trần độ tin cậy: "High" chỉ nghĩa là nguồn mạnh + snippet khớp. Mọi yêu cầu bắt buộc dựa trên pháp lý chờ V-01…V-06 |
| Snippet có thể là tóm tắt của công cụ tìm kiếm, không phải câu nguyên văn | Trung bình | Chỉ trích ngắn; claim quan trọng cần hai nguồn |
| Không kiểm chứng được URL có còn tồn tại, đúng nội dung | Thấp–trung bình | Đối chiếu chéo giữa agent; 16 URL gắn cờ |
| Agent khác nhau thấy kết quả khác nhau (InfinitePower seed) | Trung bình | Hạ nhãn, cần nguồn thứ hai (K R-18) |
| Agent sau không tìm được nguồn mới, phải dựa vào ghi chú trước | Cao với G, H, I | Họ ghi rõ nguồn gốc lấy lại; kiến thức nền gắn `INFERENCE`/`UNKNOWN` |
| Hạn mức hết trước K: không có lượt kiểm chứng độc lập | Cao | Phán quyết K dựa trên nhất quán, chất lượng nguồn và logic; hàng đợi V-01…V-14 |
| Vòng rà soát cuối (review + fix các deliverable 02–14) cũng không có hạn mức WebSearch: **chưa reviewer nào spot-check bất kỳ URL nào** | Cao | V-14 ở [14 §7](14-source-register.md) chặn phát hành ra ngoài 02 và phần so sánh đối thủ của 00; rủi ro R-53 ở [13](13-open-questions-and-risks.md) |

### 6.3 Diễn giải cho người đọc

- Một câu `[FACT]` trong bộ tài liệu nghĩa là: **có ít nhất một nguồn có tên, có URL, và snippet của nó nói điều đó**. Không có nghĩa là ai đó đã đọc toàn văn.
- Một câu `[FACT, High]` về luật Việt Nam vẫn **không đủ** để làm yêu cầu tuân thủ bắt buộc khi chưa qua [14 §7](14-source-register.md#7-hàng-đợi-kiểm-chứng-trước-khi-phát-hành).
- Các phần dựa trên quan sát trực tiếp FusionSolar (ảnh, network, mã nguồn) là bằng chứng mạnh nhất của bộ tài liệu, nhưng chỉ cho Huawei và chỉ với tài khoản demo/guest.

---

## 7. Cách xử lý tuyên bố của hãng

| Loại tuyên bố | Cách ghi | Ví dụ | Hệ quả |
|---|---|---|---|
| Tính năng có trong tài liệu hãng | `FACT` + "theo tài liệu hãng"; ma trận `V` | SolarEdge export limitation cần công tơ POC (EL-042) | Dùng làm tham chiếu chức năng |
| Tính năng chỉ ở sản phẩm anh em, qua nhà phân phối, hoặc thiếu chi tiết | Ma trận `P` | Sungrow "< 20 ms" chỉ từ nhà phân phối | Không dùng số |
| Không tìm thấy tài liệu | Ma trận `U`; **không** viết "không hỗ trợ" | ABB peak shaving G1 = U | Hỏi hãng/đối tác |
| Hiệu năng tự công bố | `FACT (tự công bố)`; dùng làm mục tiêu tham chiếu | Huawei ≤ 2 s/≤ 5 s, ghi "SmartLogger5000B/SmartMGC5000B" (EL-025) | Không coi là số đo độc lập |
| Chứng nhận tự công bố | `FACT (tự tuyên bố)` + "không thấy registry" | Ampowr ISO 27001/NIS2 (EL-036) | Ta chỉ tuyên bố khi có chứng chỉ |
| "AI", "ML" trong marketing | `V*` hoặc `FACT` về việc tuyên bố; không suy ra năng lực | InfinitePower "AI-Powered EMS" (EL-039); ABB OPTIMAX "AI" | Quy tắc đặt tên AI/ML của ta |
| % tiết kiệm, độ tin cậy, giờ kỹ sư | `FACT, Low` về việc tuyên bố | Stem "tới 30%", 99,99% (EL-053) | Không làm KPI hay câu bán hàng |
| Thanh ghi/hành vi từ cộng đồng | `FACT, Low` "cộng đồng báo cáo" | Huawei 47086, Sungrow 13049–13051 (EL-063) | Test case, không làm driver `VERIFIED_*` |
| Ràng buộc trong một manual cụ thể | `FACT` giới hạn đúng phạm vi manual | Huawei peak shaving on/off-grid (EL-026) | Không tổng quát hóa cho dòng sản phẩm |

Nguyên tắc chung: claim về hãng được viết **hẹp nhất có thể**: đúng model, đúng phiên bản tài liệu, đúng kịch bản. Câu so sánh giữa nhiều hãng luôn là `INFERENCE`.

---

## 8. Giới hạn và mối đe dọa tới tính hợp lệ

| # | Mối đe dọa | Loại | Mô tả | Giảm thiểu hiện có | Cần làm |
|---|---|---|---|---|---|
| T-01 | Chỉ có snippet | Construct / measurement | Không đọc toàn văn nguồn nào trong lượt EMS | Trần độ tin cậy; nhãn rõ | V-01…V-13 |
| T-02 | Nghiên cứu tại bàn, không có khách thật | External validity | Chưa phỏng vấn installer, O&M, ESCO, chủ C&I; chưa xem hóa đơn EVN thật | Persona và JTBD gắn `INFERENCE` | Phỏng vấn (§9.2) |
| T-03 | Thiên lệch về Huawei | Selection | Bằng chứng sâu nhất (ảnh, API, mã) chỉ có cho FusionSolar | Ma trận UX chỉ so với FusionSolar (K) | Tài khoản/demo của hãng khác |
| T-04 | Thiếu hãng phổ biến ở VN | Selection | Deye/Solarman, Growatt, Solis C&I, tủ BESS Trung Quốc chưa được đánh giá đầy đủ | Ghi rõ ở K G-08 | Lượt B/E thứ 2 |
| T-05 | Nguồn vendor có lợi ích | Source bias | Nhiều số liệu (SOC LFP, QĐ 1570, % tiết kiệm) từ bên bán hàng | Hạ nhãn; cần nguồn độc lập | Nguồn học thuật/văn bản gốc |
| T-06 | Thời điểm | History | Pháp lý VN thay đổi nhanh (NĐ 243 06/2026, QĐ 963 04/2026, NĐ 278 07/2026, thí điểm giá hai thành phần 07/2026) | Biểu giá và lịch TOU là dữ liệu có phiên bản | Theo dõi định kỳ văn bản |
| T-07 | Mâu thuẫn giữa agent do chạy song song | Internal consistency | Đơn vị, timestamp, dấu Q, arbiter, topic MQTT từng khác nhau | phán quyết K R-01…K R-27 | Rà soát vòng 2 |
| T-08 | Hạn mức tìm kiếm phân bổ không đều | Coverage | A/B/C/E dùng gần hết; G/H/I/J/K không có | Agent sau ghi nguồn gốc lấy lại | Lượt tìm kiếm riêng cho F, G, H, I |
| T-09 | Kiến thức nền của mô hình | Construct | Nội dung tiêu chuẩn (IEC 62443, ISA-101/18.2, EEMUA 191), luật VN về dữ liệu, giấy phép solver | Gắn `INFERENCE`/`UNKNOWN`, edition `UNKNOWN` | V-06, V-11, V-12 |
| T-10 | Con số ước tính kỹ thuật | Measurement | Khối lượng dữ liệu, số điểm đo/site, dung lượng nén | Gắn `INFERENCE`; K tính lại số học | PoC 1.000 site |
| T-11 | Không có thử nghiệm thiết bị | Ecological validity | Mọi hành vi driver/fallback là theo tài liệu hoặc cộng đồng | Readback, `requires_native_fallback`, cấm map diễn đàn | Lab + HIL + pilot (§9.3) |
| T-12 | Rủi ro pháp lý của mã/giấy phép | Legal | TimescaleDB TSL, OpenEMS EPL/AGPL, `huawei_solar` AGPL-3.0 | Không chép code AGPL; ADR có điều kiện | V-07, V-08 |

**Điều chưa được nghiên cứu (theo K §5).** Quy trình O&M ticket/work order chi tiết; commissioning end-to-end; mô hình kinh doanh/định giá; chiến lược kiểm thử (simulator/HIL); phần cứng edge và BOM; tín hiệu PCCC BESS. Một số đã được các deliverable xử lý ở mức PROPOSAL; xem [13](13-open-questions-and-risks.md) cho trạng thái hiện tại.

---

## 9. Cách mở rộng và kiểm chứng nghiên cứu

### 9.1 Lượt kiểm chứng tài liệu (có mạng)

1. Chạy hàng đợi [14 §7](14-source-register.md#7-hàng-đợi-kiểm-chứng-trước-khi-phát-hành) theo thứ tự chặn: V-01…V-06 (pháp lý), V-07…V-08 (giấy phép), V-09…V-11 (hãng, tiêu chuẩn).
2. Mỗi văn bản pháp luật: lấy bản gốc (Công báo, cổng chính phủ, EVN), ghi số hiệu, ngày ban hành, ngày hiệu lực, điều khoản liên quan; cập nhật nhãn trong deliverable.
3. Spot-check 16 URL gắn cờ ở [14 §4.1](14-source-register.md#41-url-gắn-cờ-vẫn-giữ-trong-sổ).
4. Ngân sách tìm kiếm phân bổ trước cho từng agent; giữ 20% cho người phản biện.
5. Mọi nguồn mới vào sổ với mã S-404 trở đi và cách tiếp cận `Fetch (ngày)`.

### 9.2 Kiểm chứng với khách hàng (Việt Nam)

| Hoạt động | Đối tượng | Câu hỏi chính | Đầu ra |
|---|---|---|---|
| Phỏng vấn bán cấu trúc (8–12 buổi) | Installer/EPC, đơn vị O&M C&I, ESCO, chủ nhà máy | Công việc hằng ngày; công cụ đang dùng; nỗi đau đa hãng; zero-export vận hành thế nào; sẵn sàng trả tiền cho gì | Persona/JTBD có bằng chứng (`PV-xx`), thứ tự giá trị đã kiểm |
| Thu hóa đơn EVN thật | 5–10 khách C&I khác cấp điện áp | Khung TOU áp thực tế; có thành phần công suất không; cơ sở tính | Trả lời EL-010, EL-016; dữ liệu test cho M-TAR |
| Quan sát ca trực O&M | 1–2 đơn vị O&M | Luồng cảnh báo → ticket → xử lý | Đặc tả O&M (K G-01) |

### 9.3 Kiểm chứng kỹ thuật

| Hoạt động | Mục tiêu | Tiêu chí |
|---|---|---|
| **Tài khoản installer thật** (FusionSolar, iSolarCloud, SolarEdge ONE, Deye/Solarman) | Thấy màn hình cảnh báo, ticket, quản trị công ty, Northbound — các mục còn UNKNOWN với tài khoản guest (S-388) | Ảnh + ghi chú quan sát cho từng mục UNKNOWN |
| **Datasheet và register map chính thức** từ hãng/đối tác | Thay map diễn đàn; xác nhận ≤ 2 s/≤ 5 s và model (V-09, V-10) | Driver đạt `VERIFIED_LAB` |
| **Lab thiết bị + simulator** | Thử Modbus/OCPP, readback, `NO_EFFECT`, word order, wrap, dấu | Bộ test vector vàng cho từng driver |
| **HIL / thử an toàn** | Rút cáp, mất POC, BMS stale, lệnh hết hạn, replay, watchdog | Đạt bộ P0 an toàn của Gate M2 ([10](10-security-and-reliability.md)) |
| **PoC lưu trữ 1.000 site** | Dung lượng, nén, độ trễ truy vấn, refresh CAGG | Số đo thay giả định 5 B/mẫu (EL-092) |
| **Site pilot** (1–3 site C&I, ưu tiên một site PV-only và một site PV+BESS) | Gate M1 trước (giám sát + chế độ native có readback); Gate M2 chỉ khi đủ bộ P0 | Báo cáo pilot: dữ liệu mất, sai dấu, readback, tiết kiệm shadow bill so với baseline |
| **Backtest tối ưu** | Bật tầng 3 cho site chỉ khi backtest thắng luật tầng 2 | Báo cáo backtest có nhãn "Mô phỏng" |

### 9.4 Quản trị nghiên cứu tiếp theo

- Mỗi lượt mới tạo ghi chú `notes/<agent>-<chủ-đề>-r2.md`, không ghi đè vòng 1.
- K (hoặc người phản biện) chạy vòng 2 trên ghi chú mới và deliverable, cập nhật quyết định thống nhất.
- Registrar cập nhật 14: S-ID mới, nâng/hạ độ tin cậy có ghi lý do, đóng mục V-xx.
- Deliverable chỉ đổi nhãn `UNKNOWN` → `FACT` khi có S-ID với cách tiếp cận `Fetch`/văn bản gốc/quan sát trực tiếp.

---

## 10. Vấn đề gửi agent khác

- **Người viết 00:** dùng §6.3 để diễn đạt mức tin cậy trong tóm tắt điều hành; không viết "đã kiểm chứng pháp lý".
- **Người viết 12:** cột bằng chứng của ma trận truy vết nên trỏ EL-xxx và V-xx trong [14](14-source-register.md).
- **Người viết 13:** T-01…T-12 ở §8 có thể ánh xạ sang R-xx; RQ-14 (khách hàng thật) nên là rủi ro mức cao nếu chưa có.
- **Orchestrator:** cần phân bổ hạn mức tìm kiếm theo agent ở lượt sau; vòng này agent G, H, I, J, K và Registrar không có truy vấn nào.
