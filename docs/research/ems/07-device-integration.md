# 07 — Tích hợp thiết bị, giao thức và edge gateway

[← Mục lục](index.html) · [00 Tóm tắt](00-executive-summary.html) · [03 Chức năng](03-functional-catalog.html#m-int) · [04 Yêu cầu](04-business-requirements.md) · [05 Domain](05-domain-model.html#s6) · [06 Kiến trúc](06-system-architecture.html) · [08 Tối ưu](08-energy-optimization.md) · [10 An toàn](10-security-and-reliability.md) · [11 Lộ trình](11-mvp-and-roadmap.html) · [12 Truy vết](12-traceability-matrix.md) · [13 Rủi ro](13-open-questions-and-risks.md) · [14 Nguồn](14-source-register.md) · [15 Mô phỏng](15-simulators-and-messaging.md)

| Mục | Giá trị |
|---|---|
| Phiên bản | 1.0 (bản phát hành nghiên cứu đầu tiên) |
| Ngày | 2026-10-10 |
| Người viết | Agent E (Device & Integration Architect) |
| Trạng thái | Đầu vào cho thiết kế. Các mục pháp lý (QĐ 1570, yêu cầu điều độ) và giấy phép (OpenEMS) **chưa kiểm chứng**, xem §13 |
| Đầu vào | [`notes/E-device-integration.md`](notes/E-device-integration.md) (ghi chú gốc), [`notes/K-review-round1.md`](notes/K-review-round1.md) (phán quyết, **ràng buộc**), ghi chú C, F, G, H, I; [03](03-functional-catalog.html), [04](04-business-requirements.md), [05](05-domain-model.html); nghiên cứu FusionSolar trước tại [`../fusionsolar/`](../fusionsolar/README.md) |
| Phạm vi mã | Dùng mã tính năng `F-<MODULE>-NN` của [03](03-functional-catalog.html) và mã `FR-*`/`NFR-*` của [04](04-business-requirements.md). Mã `PR-E-xx`, `Q-E-xx` trong file này là **mã tạm**; người viết 13 cấp `Q-NN`/`R-NN`, người viết 06 cấp `ADR-NN` (K §6 #38) |

---

## Mục lục

0. [Tóm tắt quyết định](#0-tóm-tắt-quyết-định)
1. [Phạm vi, phương pháp và giới hạn bằng chứng](#1-phạm-vi-phương-pháp-và-giới-hạn-bằng-chứng)
2. [Nguyên tắc tích hợp](#2-nguyên-tắc-tích-hợp)
3. [Phân tầng tích hợp, ranh giới bảo vệ và phân xử lệnh](#3-phân-tầng-tích-hợp-ranh-giới-bảo-vệ-và-phân-xử-lệnh)
4. [Lớp thiết bị và ma trận phù hợp giao thức](#4-lớp-thiết-bị-và-ma-trận-phù-hợp-giao-thức)
5. [Giao thức](#5-giao-thức)
6. [Kiến trúc edge gateway](#6-kiến-trúc-edge-gateway)
7. [Hợp đồng telemetry chuẩn](#7-hợp-đồng-telemetry-chuẩn)
8. [Hợp đồng lệnh chuẩn](#8-hợp-đồng-lệnh-chuẩn)
9. [Onboarding và commissioning thiết bị](#9-onboarding-và-commissioning-thiết-bị)
10. [Ghi chú tích hợp theo hãng](#10-ghi-chú-tích-hợp-theo-hãng)
11. [Chiến lược kiểm thử tích hợp](#11-chiến-lược-kiểm-thử-tích-hợp)
12. [Truy vết tính năng và yêu cầu](#12-truy-vết-tính-năng-và-yêu-cầu)
13. [Câu hỏi mở và rủi ro chuyển cho 13](#13-câu-hỏi-mở-và-rủi-ro-chuyển-cho-13)
14. [Thay đổi so với ghi chú E và nghiên cứu FusionSolar](#14-thay-đổi-so-với-ghi-chú-e-và-nghiên-cứu-fusionsolar)
15. [Danh sách nguồn dùng trong tài liệu](#15-danh-sách-nguồn-dùng-trong-tài-liệu)

---

## 0. Tóm tắt quyết định

| # | Quyết định | Nhãn | Căn cứ |
|---|---|---|---|
| D-07-01 | **Tách hai đường tích hợp.** Đường đọc (monitoring plane: Modbus đọc, connector cloud hãng, import CSV) và đường ghi (control plane: edge arbiter → controller native/thiết bị) có danh tính dịch vụ, credential, topic và quy trình release riêng. Control **tắt mặc định** theo site | [PROPOSAL] | K §6 #26; I §3.4.3 |
| D-07-02 | **Không có tuyên bố "tương thích mọi thiết bị".** Hỗ trợ được công bố theo bộ ba (model, dải firmware, driver@version) kèm trạng thái kiểm chứng `VERIFIED_LAB` / `VERIFIED_FIELD` / `COMMUNITY` / `UNVERIFIED` và chức năng đọc/ghi | [PROPOSAL] | K §6 #35; F-INT-23 |
| D-07-03 | **Edge của ta bắt buộc ở mọi site mà nền tảng ghi lệnh.** Site chỉ giám sát có thể dùng connector cloud hãng (chỉ đọc) | [PROPOSAL] | K §6 #13; F-INT-01, F-MON-02 |
| D-07-04 | **Cloud không bao giờ ghi trực tiếp vào thiết bị và không nằm trong vòng bảo vệ.** Cloud gửi ý định có hạn; edge arbiter 12 mức quyết định | [PROPOSAL] | K §6 #14, #16 |
| D-07-05 | **Vòng nhanh** (zero-export, trần nhập, SOC guard) do controller native hoặc edge làm chủ theo cờ `control_owner ∈ {NATIVE, EDGE}`; ưu tiên native; không bao giờ hai vòng trên một biến | [PROPOSAL] | K §6 #15; F-OPT-02 |
| D-07-06 | **Modbus TCP/RTU là giao thức thiết bị chính** ở MVP; SunSpec dùng để khám phá năng lực, không phải bảo đảm tương thích | [INFERENCE] | §5.1–5.2 |
| D-07-07 | **Uplink MQTT 5 + mTLS**, outbound-only, lô nhị phân nén, `seq` + ack, topic `ems/v1/{edge_id}/up/…` và `…/down/…`. Sparkplug B chỉ là đầu ra tùy chọn (P2) | [PROPOSAL] | K R-12, §6 #20 |
| D-07-08 | **Hợp đồng điểm**: dấu P theo K R-01, Q theo K R-02, đơn vị SI gốc (W, Wh, var, VA; bộ đếm int64 Wh), ba timestamp `ts`/`ts_src`/`ts_ingest` (UTC, ms), quality tầng điểm | [PROPOSAL] | K §6 #4–#9 |
| D-07-09 | **Hợp đồng lệnh**: envelope ký JWS bắt buộc trước Gate M2, `expires_at` bắt buộc, idempotency theo `command_id`, readback trước khi báo `APPLIED`, không gửi lại sau hạn | [PROPOSAL] | K §6 #21, R-11 |
| D-07-10 | **IEC 60870-5-104 slave trên edge là P1 có điều kiện** (site trung áp bán dư hoặc khi điện lực yêu cầu). MVP dùng slave 104 có sẵn của logger hãng/gateway nếu cần | [PROPOSAL] | K R-10, §6 #32 |
| D-07-11 | **OCPP 1.6J (Security Profile ≥ 2) là P1**; IEC 61850, DNP3, OpenADR, IEEE 2030.5 là P2 (chỉ giữ chỗ adapter) | [PROPOSAL] | K §6 #32 |
| D-07-12 | **Commissioning có checklist bắt buộc**: khám phá → xác minh map → phép thử dấu → test giới hạn xuất → (M2) test watchdog → biên bản. Thanh ghi lấy từ diễn đàn không được vào driver `VERIFIED_*` | [PROPOSAL] | K G-02, §6 #10, #35 |
| D-07-13 | **Mọi bộ mô phỏng thiết bị là công cụ kiểm thử nội bộ**, gắn nhãn "Mô phỏng" trong mọi màn hình/báo cáo; kết quả mô phỏng không được dùng làm bằng chứng kiểm chứng driver | [PROPOSAL] | K §6 #33 |

---

## 1. Phạm vi, phương pháp và giới hạn bằng chứng

### 1.1 Phạm vi

Tài liệu này quy định cách nền tảng EMS C&I đa site, đa hãng (K §6 #1) **đọc dữ liệu và gửi lệnh** tới: công tơ (meter), PV inverter, hybrid inverter, PCS (Power Conversion System, bộ biến đổi công suất của BESS), BMS (Battery Management System), bộ điều khiển BESS/EMS tủ, sạc EV, máy phát (genset), trạm thời tiết/cảm biến bức xạ, rơ-le/I/O, controller và cloud của hãng, trung tâm điều độ, chương trình DR (Demand Response, đáp ứng phụ tải).

Ngoài phạm vi: code ứng dụng; thuật toán tối ưu ([08](08-energy-optimization.md)); chi tiết bảo mật, PKI, IAM ([10](10-security-and-reliability.md)); lưu trữ chuỗi thời gian ([05](05-domain-model.html#s7), [06](06-system-architecture.html)). Các phần này chỉ được nhắc ở chỗ giao với tích hợp.

### 1.2 Phương pháp

- Môi trường **chặn tải trang trực tiếp** (WebFetch/curl). Mọi `[FACT]` mới đến từ WebSearch, tức là nội dung tóm tắt/snippet mà công cụ tìm kiếm trả về cho đúng URL được ghi. Tất cả mặc định là **"(qua kết quả tìm kiếm)"**. Không datasheet hay tiêu chuẩn nào được đọc toàn văn.
- Khi viết tài liệu này, hạn mức WebSearch chung (200 truy vấn) **đã hết**; một truy vấn kiểm chứng bổ sung bị từ chối. Vì vậy tài liệu dựa trên các URL đã ghi trong ghi chú E và các ghi chú khác, cộng nghiên cứu FusionSolar trước. Không thêm URL mới.
- Bằng chứng Huawei Northbound/Modbus lấy từ [`../fusionsolar/04_ghi_chu_nghien_cuu/1_tong_quan/api_integration.md`](../fusionsolar/04_ghi_chu_nghien_cuu/1_tong_quan/api_integration.md), ghi "(nghiên cứu FusionSolar trước)". Nghiên cứu đó có lúc mở được trang hãng, có lúc chỉ đọc được qua mã nguồn cộng đồng; mức tin cậy ghi theo từng dòng.
- Tiêu chuẩn (IEC/IEEE/OCPP/OpenADR): chỉ ghi edition khi kết quả tìm kiếm nêu rõ. **Không tuyên bố tuân thủ** bất kỳ tiêu chuẩn nào (K §6 #34).
- Thanh ghi Modbus lấy từ diễn đàn mang nhãn `[FACT, Low — cộng đồng báo cáo]` và **không được dùng làm map driver đã kiểm chứng** (K §4, BR-INT-01 của [04](04-business-requirements.md)).

### 1.3 Mức tin cậy

| Mức | Ý nghĩa trong file này |
|---|---|
| High | Tài liệu hãng/tổ chức tiêu chuẩn, hai nguồn độc lập khớp nhau |
| Med | Một nguồn chính thức hoặc tài liệu kỹ thuật bên thứ ba có uy tín |
| Low | Diễn đàn, blog, tóm tắt của vendor có lợi ích (ví dụ tóm tắt QĐ 1570 của Advantech) |

---

## 2. Nguyên tắc tích hợp

| ID | Nguyên tắc | Hệ quả thiết kế | Nhãn |
|---|---|---|---|
| IP-01 | **Đọc và ghi là hai đường khác nhau.** Một tích hợp đọc được không có nghĩa là ghi được | `DeviceEndpoint.write_enabled = false` mặc định ([05 §6](05-domain-model.html#s6)); bật khi commissioning đạt và site có gate phù hợp | [PROPOSAL] |
| IP-02 | **Không có tương thích phổ quát.** "Đa hãng" là thư viện driver theo model/firmware, không phải một giao thức. Ngay SunSpec, chuẩn mạnh nhất, cũng có lỗi tương tác ở thiết bị đã chứng nhận | Trang "Thiết bị được hỗ trợ" (F-INT-23); trạng thái kiểm chứng theo driver | [INFERENCE] từ §5.2 (SunSpec 12/2023) |
| IP-03 | **Một thiết bị, một connection owner.** Edge (hoặc controller native) là Modbus master duy nhất trên một bus/thiết bị. Consumer khác đọc qua edge (Modbus TCP server, F-INT-17) | Huawei chỉ nhận một client Modbus TCP (§10.1); RTU chỉ có một master theo bản chất giao thức | [FACT] + [INFERENCE] |
| IP-04 | **Cloud không ghi thiết bị.** Mọi lệnh qua arbiter của edge, có hạn, có chữ ký | §3, §8 | [PROPOSAL] (K §6 #14) |
| IP-05 | **Không phần mềm nào sửa thông số bảo vệ** (grid code, ngưỡng BMS, cài đặt rơ-le). Chỉ đọc và so với hồ sơ | Lệnh hạng C4 không có API (F-BESS-19); SunSpec 705–712 chỉ đọc (§5.2) | [PROPOSAL] (K §6 #14) |
| IP-06 | **Native trước.** Nếu controller hãng (SmartLogger, EMS tủ, GX…) có chức năng, edge đặt tham số và giám sát, không chạy vòng thứ hai | `control_owner` theo chức năng (F-OPT-02) | [PROPOSAL] (K R-09) |
| IP-07 | **Không tin "đã ghi" cho đến khi đọc lại.** Có báo cáo cộng đồng về lệnh ghi "không có tác dụng" (Sungrow, Huawei) | `APPLIED` chỉ sau readback; trạng thái `FAILED_NO_EFFECT` (§8.5) | [INFERENCE] từ §10 |
| IP-08 | **Mọi lệnh có hạn và trạng thái về-mặc-định đã định trước** | `expires_at` bắt buộc; `on_expiry = REVERT_DEFAULT`; thiết bị không có watchdog không nhận setpoint P cưỡng bức | [PROPOSAL] (K §6 #17, #21) |
| IP-09 | **Chuẩn hóa tại edge.** Dấu, đơn vị, scale, word order, sentinel, múi giờ thiết bị được chuẩn hóa trong driver trước khi rời edge | Cloud chỉ nhận dữ liệu đã chuẩn hóa, có `sign_normalized = true` ([05 §7](05-domain-model.html#s7)) | [PROPOSAL] |
| IP-10 | **Driver là dữ liệu có phiên bản**, không phải code rải rác. Map thanh ghi khai báo, có hash, có bằng chứng kiểm thử | §6.2 | [PROPOSAL] |
| IP-11 | **Nguồn gốc dữ liệu luôn hiển thị**: edge hay cloud hãng, driver nào, quality nào | Quality `UNCERTAIN_VENDOR_CLOUD` cho dữ liệu qua cloud hãng; F-MON-05, F-MON-06 | [PROPOSAL] |
| IP-12 | **Không gán tính năng chưa có tài liệu cho hãng.** "Không có tài liệu" ≠ "không hỗ trợ" | §10 ghi rõ "không thấy tài liệu" thay vì "không hỗ trợ" | Quy ước |

### 2.1 Hai mặt phẳng tích hợp

| Thuộc tính | Monitoring plane (đọc) | Control plane (ghi) |
|---|---|---|
| Ví dụ | Driver Modbus ở chế độ đọc; connector cloud Huawei/Sungrow/SMA/Solis/Growatt/Deye; import CSV/load profile | Edge arbiter → controller native/PCS/inverter/charger; (ngoại lệ P2) Huawei OAuth Connect control API |
| Danh tính dịch vụ | `svc-ingest-*` | `svc-command-*` |
| Credential của hãng | Chỉ đọc nếu hãng cho phân quyền | Credential riêng, vault path riêng, chỉ control plane đọc được |
| Topic MQTT | `up/state`, `up/telemetry/*`, `up/event`, `up/backfill` | `down/cmd` (có chữ ký), `up/cmd-ack` (ký bằng khóa edge) |
| Bật/tắt | Theo site, mặc định bật | **Mặc định TẮT**; bật = lệnh C3 sau commissioning và đồng ý của chủ tài sản (F-SEC-05) |
| Gate MVP | Gate M1 phần giám sát | Gate M1 (ghi tham số native có readback), Gate M2 (edge làm chủ vòng) |

Nguồn: I §3.4.3, K §6 #26–#27. Nhãn: [PROPOSAL].

---

## 3. Phân tầng tích hợp, ranh giới bảo vệ và phân xử lệnh

### 3.1 Phân tầng

```
[Z0 Bảo vệ cứng: rơ-le, E-stop, contactor BMS, rơ-le chống phát ngược, PCCC]   ← không phần mềm nào của ta ghi
     │ dây cứng (BMS→PCS), ngoài phần mềm
[Z1 Thiết bị: inverter / PCS / BMS / công tơ / EVSE / genset / cảm biến / I/O]
     │ Modbus RTU/TCP, SunSpec, CAN (chỉ nghe), OCPP (EVSE→edge), IEC 61850 (P2)
     ▼
[Controller native của hãng (tùy chọn): SmartLogger/EMMA, Logger1000/EMS300CP, Solar-Log, blue'Log, Victron GX, EMS tủ BESS]
     │ Modbus TCP: đặt tham số/chế độ/setpoint, đọc trạng thái
     ▼
[Z2/Z3 EDGE của ta: driver, point mapping, arbiter + limit chain, buffer, (P1) IEC 104 slave, (P1) CSMS OCPP tối giản]
     │ MQTT 5 + mTLS outbound-only (telemetry/event/cmd/ack); HTTPS (OTA, file)
     ▼
[Z5/Z6 CLOUD: ingest, TSDB, bộ sinh lịch, Command API + PDP + Signer, connector cloud hãng (chỉ đọc)]
```

- [FACT, Med] Một thiết kế ESS được cấp patent cho thấy BMS gửi tín hiệu bảo vệ tới PCS qua **dây cứng** để phản ứng thời gian thực, còn kênh tới EMS là TCP/IP, RS485 hoặc CAN — https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11411391 (qua kết quả tìm kiếm). Đây là một thiết kế, không phải chuẩn.
- [INFERENCE] Từ đó: phần mềm EMS (edge và cloud) nằm **ngoài** vòng bảo vệ. Vùng Z0–Z6 theo I §3.6 và [10](10-security-and-reliability.md).

### 3.2 Thứ tự phân xử (arbiter) — chuẩn 12 mức

Thứ tự này là quyết định K R-07, thay cho thứ tự 6 mức trong ghi chú E §3.1. Mức 1–6 cố định; mức 8–11 cấu hình được theo site. Mô hình "thu hẹp khoảng cho phép" của G §3.8: mức trên tạo ràng buộc `[P_lo, P_hi]`, mức dưới chọn điểm trong khoảng còn lại ([05 §11.1](05-domain-model.html#s11-arb), F-OPT-01).

| Mức | Lớp | Nguồn trong hợp đồng tích hợp | Ai thực thi |
|---|---|---|---|
| 1 | Bảo vệ native (BMS/PCS/rơ-le/E-stop cứng) | Chỉ đọc: `ess.p_charge_max`, `ess.p_discharge_max`, trạng thái thiết bị | Thiết bị, ngoài phần mềm |
| 2 | Interlock tại chỗ (LOCAL/REMOTE, trạng thái E-stop, PCCC) | DI của edge, điểm trạng thái thiết bị; IL-01, IL-02, IL-08, IL-09 | Edge |
| 3 | Giám sát an toàn của edge (dữ liệu cũ, lệnh hết hạn, giới hạn SOE) | `T_stale_poc`, `T_stale_bms`, `expires_at`, SOE | Edge |
| 4 | Tuân thủ lưới (giới hạn xuất, lệnh `GRID_OPERATOR`, chặn phát ngược) | `export_mode`, `export_limit_w`; lệnh `source = GRID_OPERATOR` (IEC 104, P1) | Native hoặc edge |
| 5 | Trần nhập vật lý | `import_cap_w` | Native hoặc edge |
| 6 | Dự phòng backup | `soc_backup_reserve_pct` | Edge (hoặc native) |
| 7 | Lệnh tay của operator (có hạn, trong SOE) | `source = OPERATOR` | Edge |
| 8 | DR/VPP (P2) | `source = DR` | Edge |
| 9 | Peak shaving theo demand (P1) | Kế hoạch | Edge |
| 10 | Cam kết EV (P1) | Phiên sạc | Edge |
| 11 | Lịch kinh tế (luật tầng 2 / optimizer tầng 3) | `source ∈ {SCHEDULE, OPTIMIZER}` | Edge |
| 12 | Chiến lược mặc định | `default_strategy` | Edge |

### 3.3 Ai làm chủ vòng nhanh

| Chức năng | `control_owner = NATIVE` (ưu tiên) | `control_owner = EDGE` (khi native không có) | Không bao giờ |
|---|---|---|---|
| Zero-export / giới hạn xuất | Edge ghi tham số "max feed-in"/"export limit" vào logger hãng, đọc lại, giám sát tại `MTR_POC` (F-GRID-04, Gate M1) | Edge chạy vòng 1 s đọc `MTR_POC`, ưu tiên sạc BESS trước khi cắt PV (F-GRID-05, Gate M2) | Cloud chạy vòng; hai PI cùng điều khiển P xuất |
| Trần nhập | Capacity control native (nếu có, kiểm chứng theo model) | BESS xả, giảm EV (F-GRID-06) | — |
| SOC guard | BMS/PCS native luôn bảo vệ | Edge giữ SOC trong SOE (F-BESS-10) | Edge ghi ngưỡng BMS |
| Phân bổ nhiều PCS | EMS tủ/PPC của hãng | Edge chia P theo SOC (F-BESS-14, P1) | — |

[FACT, Med] Huawei tự công bố vòng kín zero feed-in ≤ 2 s và giới hạn công suất/peak shaving ≤ 5 s cho bộ điều khiển site C&I (**SmartLogger5000B/SmartMGC5000B**) — https://solar.huawei.com/admin/asset/v1/pro/view/bb9458d9373d4502912378db3cbc7f2d.pdf ; https://www.photomate.eu/smartlogger5000b (qua kết quả tìm kiếm). Đây là **số do hãng tự công bố**, dùng làm mục tiêu tham chiếu, không phải số đo độc lập (K R-19).

### 3.4 Ngân sách thời gian vòng giới hạn xuất

[FACT, Med] Autarco chia độ trễ tổng của zero-export thành chu kỳ đo của công tơ + trễ truyền + thời gian phản ứng của inverter + thời gian giảm công suất vật lý — https://help.autarco.com/en/hardware/why-am-i-still-exporting-while-i-have-set-my-pv-system-to-zero-export- (qua kết quả tìm kiếm).

| Khâu | Edge (Modbus TCP, công tơ điều khiển riêng) | Qua cloud của hãng |
|---|---|---|
| Đo tại POC | 100–1.000 ms (chu kỳ công tơ) [INFERENCE] | Dữ liệu gộp 5 phút (Huawei Northbound, §5.11) |
| Truyền tới bộ điều khiển | < 50 ms LAN [INFERENCE] | Pull 1–15 phút, có hạn mức |
| Tính toán | < 10 ms; chu kỳ edge p99 ≤ 200 ms (NFR-PERF-006) | Giây |
| Ghi lệnh | 10–300 ms (TCP nhanh, RTU chậm hơn, §5.1.4) | Task bất đồng bộ, phút |
| Thiết bị phản ứng + ramp | 0,1–2 s theo hãng [INFERENCE] | Như bên trái |
| **Tổng** | **≈ 0,5–3 s** [INFERENCE], cùng cỡ với mục tiêu tham chiếu ≤ 2 s | **Phút**: không dùng được cho zero-export |

Kết luận [INFERENCE]: vòng nhanh ở edge hoặc controller native. Cloud chỉ gửi lịch (slot 15 phút, horizon 48 h), giới hạn và chế độ, mỗi thứ có hạn.

---

## 4. Lớp thiết bị và ma trận phù hợp giao thức

### 4.1 Danh mục lớp thiết bị

`class` là giá trị của `PointDefinition.class` ([05 §7](05-domain-model.html#s7)).

| Lớp thiết bị | `class` | Đọc gì (tối thiểu) | Ghi gì (nếu có) | Kênh ưu tiên | Rủi ro chính | Ưu tiên |
|---|---|---|---|---|---|---|
| Công tơ POC / sub-meter | `meter` | P, Q, S, PF, U, I, f theo pha; thanh ghi nhập/xuất (A+/A−), vô công 4 góc phần tư | Không | Modbus TCP, hoặc Modbus RTU trên bus **riêng** | Lắp ngược CT; word order; tràn thanh ghi; công tơ EVN thường không đọc được thời gian thực nên cần công tơ điều khiển riêng (C §3.3) | P0 |
| PV inverter (string, C&I) | `pv_inverter` | P, Q, E tổng, trạng thái, mã lỗi, MPPT/string V/I, % giới hạn hiện hành | Giới hạn P (%, W); Q/PF (P2, khóa ở MVP) | Qua logger hãng (Modbus TCP); trực tiếp nếu không có logger | Map riêng theo hãng; một client; ghi NVM | P0 |
| Hybrid inverter (pin LV) | `hybrid_inverter` | Như PV + P pin, SOC, chế độ | Chế độ, sạc/xả cưỡng bức (theo hãng) | Modbus TCP qua logger/dongle/EMMA | Chế độ "third-party" khác nhau theo hãng; báo cáo ghi không tác dụng | P0 (Huawei EMMA), khác P1 |
| PCS (BESS C&I) | `pcs` | P, Q, U/I AC/DC, nhiệt độ, mode, giới hạn hiện hành, setpoint đã nhận | P/Q setpoint, mode, start/stop (C3) | Modbus TCP northbound của EMS tủ/PCS | Map lấy từ OEM; watchdog chưa rõ | P0 (một dòng tủ) |
| BMS / rack | `bms` | SOC, SOH, U/I hệ, CCL/DCL, cell V/T min/max, contactor, cảnh báo | **Không** (IP-05) | Qua northbound EMS tủ/PCS; CAN chỉ nghe khi không còn đường khác | Không có chuẩn CAN chung; bus CAN là vòng bảo vệ nội bộ | P0 đọc qua PCS/EMS; CAN P1 |
| BESS logic | `ess` | Tổng hợp PCS + BMS: P, SOC, P cho phép sạc/xả, E sạc/xả, mode, state | `SET_ESS_P`, `SET_ESS_MODE`, `SET_SOC_RESERVE` | Edge tính | Kẹp theo CCL/DCL hiện tại | P0 |
| Bộ điều khiển BESS / EMS tủ | `ess_controller` [PROPOSAL, lớp mới] | Chế độ, kế hoạch, giới hạn đang áp | Chế độ, lịch, giới hạn (theo map OEM) | Modbus TCP | Thường **không công bố** register map (§10.7) | P0 (một dòng có hợp đồng map) |
| Sạc EV AC/DC | `evse`, `ev_connector` | Trạng thái connector, P, E phiên, giới hạn đang áp | Giới hạn A/W qua charging profile | OCPP 1.6J (P1); Modbus ở một số hãng | Hành vi profile khác nhau giữa hãng | P0 đo qua `MTR_EV_i`; điều khiển P1 |
| Máy phát (genset) | `genset` | P, E, trạng thái, giờ chạy | Start/stop (P2, F-OPT-19) | Modbus qua controller genset | Giao thức theo hãng [UNKNOWN] | P1 đọc |
| Trạm thời tiết / cảm biến bức xạ | `weather` | G_POA, GHI, T_module, T_ambient, gió | Không | Modbus RTU | Cảm biến đóng băng (FROZEN); PR = N/A khi không có POA (K §6 #12) | P0 |
| Rơ-le / I/O (DI/DO) | `relay` | LOCAL/REMOTE, E-stop, PCCC, rơ-le chống phát ngược, máy cắt POC | DO chỉ cho chức năng được phép (ví dụ tín hiệu "bật tắt phát ngược" nếu điều độ yêu cầu, [UNKNOWN]) | DI/DO của edge, module I/O Modbus | Không dùng DO thay bảo vệ | P0 đọc |
| Logger/controller hãng | `vendor_controller` [PROPOSAL, lớp mới] | Tổng hợp nhà máy, trạng thái vòng native | Tham số giới hạn xuất, chế độ, lịch | Modbus TCP; cloud hãng (đọc) | License (Solar-Log, blue'Log); chồng chéo slave 104 | P0 (Huawei) |

Hai lớp đánh dấu "[PROPOSAL, lớp mới]" chưa có trong danh sách `class` của ghi chú E. Người viết 05 quyết định có thêm vào `PointDefinition.class` hay gộp vào `pcs`/`site` (X-07-01, §13).

### 4.2 Ma trận phù hợp loại thiết bị × giao thức

Ký hiệu: **●** chính (nên hỗ trợ), **◐** có điều kiện/gặp ở một số hãng, **○** hiếm/không khuyến nghị, **—** không áp dụng. Đây là **đánh giá phù hợp**, không phải tuyên bố tương thích.

Cột "Trạng thái kiểm chứng của ta": tại ngày 2026-10-10, **chưa có driver nào đạt `VERIFIED_LAB` hay `VERIFIED_FIELD`**, vì chưa có lab thiết bị. Cột này sẽ do trang F-INT-23 cập nhật.

| Loại thiết bị | Modbus RTU | Modbus TCP | SunSpec | CAN | MQTT | OPC UA | IEC 61850 | IEC 104 | DNP3 | OCPP | OpenADR / 2030.5 | Cloud API hãng | Bằng chứng | Trạng thái kiểm chứng của ta |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PV string inverter | ● | ● (qua logger/dongle) | ◐ (SMA và một số hãng; Huawei/Sungrow dùng map riêng) | — | ○ | ○ | ○ | ○ | ○ (Mỹ) | — | ◐ (Mỹ, Rule 21) | ◐ đọc | §5.1, §5.2, §10 | UNVERIFIED |
| Hybrid inverter | ● | ● | ◐ (124/713/802) | ◐ (tới BMS, nội bộ) | ◐ (Victron GX) | — | — | — | — | — | ○ | ◐ đọc; ghi hiếm | §10.1–10.4 | UNVERIFIED; thanh ghi ghi chỉ từ diễn đàn (Low) |
| PCS (BESS C&I) | ● | ● | ○ | ◐ (nội bộ với BMS) | ○ | ◐ | ◐ (MW) | ○ | ○ | — | — | ○ | §10.7 | UNVERIFIED |
| BMS / rack | ◐ | ◐ | ◐ (802–804, TEST) | ● (nội bộ) | — | ◐ | — | — | — | — | — | — | §5.3 | UNVERIFIED |
| Tủ BESS all-in-one có EMS riêng | ◐ | ● (northbound) | ○ | ○ | ◐ | ○ | ○ | ○ | — | — | — | ◐ | §10.7 (không công bố bảng thanh ghi) | UNKNOWN |
| Công tơ POC / sub-meter | ● | ● | ◐ (201–204, 211–214) | — | — | — | ◐ (trạm) | — | — | — | — | — | §5.2; IEC 62056 cho công tơ doanh thu (tóm tắt QĐ 1570, Low) | UNVERIFIED |
| Logger/controller hãng | ◐ | ● | ◐ | — | ◐ | ○ | ◐ | ◐ (SmartLogger) | ○ | — | ◐ | ● | §10 | UNVERIFIED |
| Sạc EV AC/DC | ◐ | ◐ | — | — | — | — | — | — | — | ● (1.6J; 2.0.1; 2.1) | ◐ (OCPP 2.1 DER) | ◐ | §5.9 | UNVERIFIED |
| Genset controller | ● | ● | — | ◐ (J1939, [UNKNOWN] theo hãng) | — | — | — | — | — | — | — | — | Kiến thức nền | UNKNOWN |
| Trạm thời tiết / bức xạ | ● | ◐ | ○ | — | ◐ | — | — | — | — | — | — | — | Kiến thức nền | UNVERIFIED |
| Rơ-le / máy cắt / RMU | ◐ | ◐ | — | — | — | — | ● (trạm mới) | ◐ | ◐ (Mỹ) | — | — | — | Kiến thức nền | Chỉ đọc |
| Module I/O (DI/DO) | ● | ● | — | — | — | — | — | — | — | — | — | — | Kiến thức nền | UNVERIFIED |
| Điều độ (phía trên edge) | — | ◐ (theo tóm tắt QĐ 1570) | — | — | — | — | — | ● | — | — | — | — | §5.7 (Low) | UNKNOWN |
| Aggregator/utility DR | — | — | — | — | ◐ (OpenADR 3.1) | — | — | — | ◐ | — | ● (ngoài VN) | — | §5.10 | P2 |
| SCADA/BMS tòa nhà của khách | ◐ | ● (edge là server) | — | — | ◐ (Sparkplug, P2) | ◐ | ○ | ◐ | ○ | — | — | — | §5.4 | P1 |

### 4.3 Tín hiệu an toàn và PCCC (chỉ đọc)

Đáp ứng khoảng trống K G-12. Danh sách là [INFERENCE] từ I IL-01…IL-10 và F-BESS-18; tín hiệu cụ thể phụ thuộc tủ BESS và hệ PCCC, phải liệt kê trong commissioning.

| Tín hiệu | Nguồn thường gặp | Kiểu | Dùng cho | Interlock |
|---|---|---|---|---|
| LOCAL/REMOTE/MAINTENANCE | Công tắc khóa chìa nối DI edge, hoặc chế độ native đọc được (có biên bản) | DI / Modbus | Chặn mọi lệnh từ cloud khi LOCAL | IL-01 |
| E-stop đang tác động / mạch an toàn chưa reset | Tiếp điểm phụ của mạch E-stop | DI | Hiển thị, chặn lệnh; **không** điều khiển E-stop | IL-02 |
| Báo cháy / khói / khí / nhiệt phòng pin, xả khí chữa cháy | Tủ PCCC, đầu dò của container BESS | DI / Modbus | Không sạc/xả khi có nguy cơ | IL-08 |
| Cửa tủ mở / che chắn | Công tắc cửa | DI | An toàn người | IL-09 |
| Rơ-le chống phát ngược tác động | Rơ-le bảo vệ | DI | Hiển thị, bằng chứng tuân thủ (F-GRID-13) | — |
| Trạng thái máy cắt POC, ATS | Tiếp điểm phụ | DI | `grid_connected` (F-GRID-14) | — |
| HVAC tủ pin lỗi | EMS tủ | Modbus | Cảnh báo; giảm công suất do native quyết định | — |

---

## 5. Giao thức

### 5.1 Modbus TCP/RTU

#### 5.1.1 Giới hạn cứng

| Hạng mục | Giá trị | Nhãn và nguồn |
|---|---|---|
| Đọc FC03/FC04 | ≤ 125 thanh ghi/lần | [FACT, High] https://docs.elipse.com.br/documents/en-us/driver/modbus/latest/modbus_appendix_max_limit_block_size.html ; https://www.se.com/be/en/faqs/FA252887/ (qua kết quả tìm kiếm) |
| Ghi FC16 | ≤ 123 thanh ghi/lần | Như trên |
| Thứ tự byte | Big-endian trong mỗi thanh ghi; đặc tả **không** quy định thứ tự word cho 32/64 bit và không định nghĩa float. Thực tế có ABCD, CDAB, BADC, DCBA | [FACT, Med] https://docs.chipkin.com/articles/modbus-data-types-byte-order-reference/ ; https://industrialmonitordirect.com/blogs/knowledgebase/modbus-32-bit-data-register-mapping-and-endianness-guide (qua kết quả tìm kiếm; nguồn thứ cấp) |
| Phân khung RTU | Khoảng lặng ≥ 3,5 ký tự; ở 9600 baud, ký tự 11 bit, 3,5 ký tự ≈ 4,01 ms; khung chuẩn 8-E-1 | [FACT, Med–High] https://www.mikrocontroller.net/attachment/216048/Modbus_RTU_PROTOCOL.pdf ; https://industrialmonitordirect.com/blogs/knowledgebase/modbus-rtu-character-time-calculating-the-35-character-timeout (qua kết quả tìm kiếm) |
| Xác thực | Modbus không có xác thực/mã hóa | [INFERENCE] kiến thức nền về giao thức (K §4 hạ cấp từ FACT); bù bằng cô lập mạng OT (F-SEC-17) |

#### 5.1.2 Function code

| FC | Tên | Dùng cho | Quy tắc driver [PROPOSAL] |
|---|---|---|---|
| 0x01/0x02 | Read Coils / Discrete Inputs | DI, rơ-le, module I/O | — |
| 0x03 | Read Holding Registers | Phần lớn telemetry và cấu hình (Huawei dùng 0x03, nghiên cứu FusionSolar trước) | ≤ 125 |
| 0x04 | Read Input Registers | Telemetry công tơ; Solar-Log PM dùng 04 | ≤ 125 |
| 0x05 | Write Single Coil | Bật/tắt | Chỉ khi lệnh cho phép; hạng C3 nếu là start/stop |
| 0x06 | Write Single Register | Setpoint 16 bit | **Cấm** dùng cho giá trị 32 bit (ghi nửa giá trị gây trạng thái trung gian sai) |
| 0x10 | Write Multiple Registers | Setpoint 32 bit, khối lịch | ≤ 123; một PDU cho một giá trị nhiều word |
| 0x17 | Read/Write Multiple | Hiếm | Không dựa vào |
| 0x2B/0x0E | Read Device Identification | Nhận diện | Nhiều thiết bị không hỗ trợ; fingerprint bằng thanh ghi model/firmware |

#### 5.1.3 Địa chỉ, unit ID, kiểu dữ liệu

- [FACT, Med] Tài liệu SunSpec đánh số 1-based (40001), trên dây là 0-based (40000) — https://github.com/SolarNetwork/solarnetwork/wiki/SunSpec-model-discovery (qua kết quả tìm kiếm). Cộng đồng báo Sungrow Logger1000 lệch 1 so với tài liệu (§10.2, Low).
- [PROPOSAL] Register map chỉ lưu **địa chỉ trên dây (0-based)**, kèm `doc_address` và `doc_ref` để truy vết về tài liệu hãng.
- [FACT, Low–Med] Unit ID mặc định khác nhau: Huawei 1 (0 khi qua AP của inverter, nghiên cứu FusionSolar trước), Sungrow Logger1000 247 (cộng đồng), blue'Log/Solar-Log 1, Ampowr hybrid 247 (RTU)/255 (TCP) theo tài liệu tích hợp bên thứ ba — https://manual-sofar.eniris.be/en/Controller/Devices/PV-hybrid-and-battery-inverters/Ampowr (qua kết quả tìm kiếm). [INFERENCE] Unit ID là cấu hình theo endpoint, không có mặc định toàn cục.
- Thuộc tính kiểu dữ liệu, scale, sentinel: §6.2.

#### 5.1.4 Ngân sách polling RTU (tính toán, [INFERENCE])

RTU 9600 baud, 8-E-1: 11 bit/ký tự → 1,146 ms/ký tự (K đã tính lại).

| Giao dịch | Request | Response | Thời gian dây (gồm 2 × 3,5 ký tự) | Cộng phản hồi thiết bị (giả định 20–100 ms) |
|---|---|---|---|---|
| Đọc 10 thanh ghi | 8 byte ≈ 9,2 ms | 25 byte ≈ 28,7 ms | ≈ 46 ms | ≈ 66–146 ms |
| Đọc 60 thanh ghi | 8 byte | 125 byte ≈ 143 ms | ≈ 160 ms | ≈ 180–260 ms |
| Đọc 125 thanh ghi | 8 byte | 255 byte ≈ 292 ms | ≈ 310 ms | ≈ 330–410 ms |

Hệ quả: bus 9600 baud có 10 inverter, mỗi cái 3 khối đọc (30 giao dịch × 150–300 ms) cần **4,5–9 s mỗi vòng**. Ở 19200 baud thời gian dây giảm một nửa, thời gian phản hồi thiết bị thì không.

Quy tắc [PROPOSAL]:
- Công tơ `MTR_POC` dùng cho vòng điều khiển phải ở **Modbus TCP hoặc bus RTU riêng**, không chung bus với inverter.
- Driver gom thanh ghi liền kề thành block ≤ 125, không vắt qua "lỗ" địa chỉ mà thiết bị trả exception 02.
- Chu kỳ tối thiểu theo driver: Huawei dongle ≥ 5 s (nghiên cứu FusionSolar trước); blue'Log Modbus Power Control khai báo delay 1.000 ms (§10.8).

#### 5.1.5 Xử lý lỗi

| Tình huống | Hành vi driver [PROPOSAL] | Quality điểm |
|---|---|---|
| Exception 01/02/03 | Lỗi cấu hình map; ngừng poll điểm/block đó, sinh sự kiện | `BAD_CONFIG` |
| Exception 04/06 (device failure / busy) | Backoff mũ có jitter | Giữ giá trị cũ tới `max_age_s` rồi `UNCERTAIN_STALE` |
| Timeout | Tăng bộ đếm; sau N lần (mặc định 3) đánh dấu endpoint | `BAD_COMM` |
| Socket mới tới Huawei dongle | `connect_delay_ms` 1.000–5.000 ms; giữ kết nối lâu dài, không mở/đóng theo từng lần poll ("first TX always fails", nghiên cứu FusionSolar trước, Low) | — |
| Giá trị sentinel | So với `na_values` của thanh ghi | `BAD_DEVICE` |
| Ngoài `range` vật lý | Giữ giá trị, gắn cờ | `UNCERTAIN_OUT_OF_RANGE` |

### 5.2 SunSpec Modbus

#### 5.2.1 Trạng thái các model

| Model | Nội dung | Bằng chứng | Dùng trong sản phẩm [PROPOSAL] |
|---|---|---|---|
| 1 | Common (Mn, Md, Opt, Vr, SN) | [FACT] nhiều nguồn | Bắt buộc đọc để fingerprint |
| 101/102/103 | Inverter 1 pha / split / 3 pha | [FACT, High] bị thay bởi dòng 700 — https://sunspec.org/sunspec-modbus-700-series-der-information-models-are-now-approved/ (qua kết quả tìm kiếm) | Vẫn đọc vì thiết bị cũ còn nhiều |
| 120–123 | Nameplate, settings, status, immediate controls | [FACT] khuyến nghị thay bằng dòng 700 | Đọc. Ghi 123 chỉ khi driver đã kiểm chứng |
| 124 | Storage | [FACT, Med–High] SMA ghi rằng 124 và 126 **không còn được hỗ trợ** trong SunSpec profile 2.0 của SMA — https://files.sma.de/downloads/SunSpecModbus-TI-en-11.pdf (qua kết quả tìm kiếm) | Hỗ trợ, cờ `legacy` |
| 126 | Volt-Var (cũ) | Như trên | Chỉ đọc |
| 201–204, 211–214 | Công tơ (int + SF; float) | [FACT, Med] danh sách theo tài liệu SMA — https://manuals.sma.de/ennexOS/en-US/14259660939.html (qua kết quả tìm kiếm); tên chi tiết từng model là [INFERENCE] | Hỗ trợ |
| 701–712 | DER theo IEEE 1547-2018 (701 AC Measurement, 702 Capacity, 703 Enter Service, 704 AC Controls, 705 Volt-Var, 706 Volt-Watt, 707–710 trip (LV/HV/LF/HF), 711 Freq-Droop, 712 Watt-Var) | [FACT, High] dải 701–712 APPROVED (nguồn SunSpec trên); tên từng model theo SMA TI / snippet SunSpec (qua kết quả tìm kiếm), chưa đối chiếu file định nghĩa model gốc → tên từng model [FACT, Med] | Ưu tiên đọc 701/702/704. 705–712 là chức năng lưới: **chỉ đọc**, so với hồ sơ (F-PV-12), không chỉnh (IP-05) |
| 713 | DER Storage Capacity | [FACT] SMA TI | Đọc SOC/dung lượng |
| 714 | DER DC Measurement | [FACT] SMA TI | Đọc |
| 715 | Xuất hiện trong danh sách chứng nhận của một hãng — https://sunspec.org/product-certification-registry (qua kết quả tìm kiếm) | Nội dung [UNKNOWN] | Không dùng tới khi kiểm chứng |
| 802 / 803 / 804 | Battery Base / Li-ion Bank / Li-ion String | [FACT, Med] Draft 4 đưa 802–805 và 807 lên **TEST**, chưa APPROVED; một slide 2014 đánh số khác — https://sunspec.org/wp-content/uploads/2025/01/SunSpec-Alliance-Specification-Energy-Storage-ModelsD4rev0-1.pdf ; https://www.slideserve.com/chaim/sunspec-alliance-overview-storage-standards-development-program (qua kết quả tìm kiếm) | Đọc; ghi 802 chỉ khi driver kiểm chứng |
| 805+ | Module/flow… | Mâu thuẫn số hiệu → [UNKNOWN] | Không dùng |

[FACT, Med–High] IEEE 1547-2018 yêu cầu giao diện DER hỗ trợ ít nhất một trong IEEE 2030.5, IEEE 1815 (DNP3) hoặc SunSpec Modbus; SunSpec (12/2023) cho biết nhiều thiết bị đã chứng nhận UL 1741 SB vẫn **có lỗi ở giao diện SunSpec Modbus** — https://www.cooperative.com/programs-services/bts/Documents/Emerging%20Priorities%20for%20Energy%20Research%20Day%20-%20Oct%202018/IEEE%201547-2018%20-%20Vartanian%20(NRECA-APA-ResearchDay-20181031).pdf ; https://sunspec.org/communication-interface-defects-revealed-inul-1741-sb-certified-inverters/ (qua kết quả tìm kiếm).

[INFERENCE] SunSpec có giá trị nhất ở **khám phá năng lực và chuẩn hóa tên điểm**. Ghi qua SunSpec (123, 124, 704, 802) phải kiểm chứng theo từng model/firmware.

#### 5.2.2 Thuật toán khám phá [PROPOSAL]

1. Với mỗi endpoint và unit ID đã cấu hình, đọc 2 thanh ghi tại 40000, 50000, 0 (0-based) tìm chuỗi "SunS" (0x5375 0x6E53) — [FACT, Med] nguồn SolarNetwork ở §5.1.3.
2. Duyệt chuỗi model: đọc `[ID, L]` → nhảy L thanh ghi → … cho tới ID 0xFFFF.
3. Đọc model 1 (Mn, Md, Opt, Vr, SN) để fingerprint.
4. Tra thư viện driver theo `(manufacturer, model, firmware)` để chọn **driver overlay** (sửa lỗi đã biết, bổ sung điểm ngoài SunSpec).
5. Ghi `capability_profile` (§6.4) và gửi lên cloud qua `up/event` loại `CAPABILITY_DISCOVERED`.
6. Thiết bị không có "SunS": dùng fingerprint qua thanh ghi model/firmware theo danh sách driver riêng của hãng; không có driver thì endpoint ở trạng thái `UNSUPPORTED`, chỉ cho đọc thô ở chế độ chẩn đoán (F-MON-06).

[FACT, Low] Một nguồn cộng đồng cho biết Sungrow dùng map riêng bắt đầu từ 5000 thay vì SunSpec — https://community.victronenergy.com/t/sungrow-inverters-and-sunspec/57195 (qua kết quả tìm kiếm).

### 5.3 BMS qua CAN

- [FACT, Med] Không có chuẩn CAN BMS chung. BMS "Pylontech-compatible" dùng CAN 500 kbps, khung chuẩn 11 bit, chu kỳ 1 s, với các ID 0x351/0x355/0x356/0x35A/0x35E/0x370…; tài liệu gốc từng bị gỡ; thiếu 0x355 (SOC/SOH) thì inverter báo timeout BMS — https://akkudoktor.net/uploads/short-url/dwFYBPwjnfia9tSuhUopj9uGX2u.pdf ; https://community.victronenergy.com/t/connect-diy-bms-via-can-to-cerbo-gx-eigenes-bms-via-can-mit-cerbo-gx-verbinden/37102 ; https://akkudoktor.net/t/pylontech-bms-mit-sma-sunny-island/18019 (qua kết quả tìm kiếm). BYD có protocol riêng do cộng đồng giải mã — https://github.com/dfch/BydCanProtocol (qua kết quả tìm kiếm).
- [INFERENCE] Trong C&I, BMS↔PCS qua CAN là vòng bảo vệ nội bộ của tủ. Edge đọc dữ liệu BMS (SOC, SOH, CCL/DCL, cell min/max, cảnh báo) qua Modbus TCP northbound của EMS/PCS tủ.
- [PROPOSAL] CAN trực tiếp (F-INT-15, P1) chỉ ở chế độ **listen-only**: driver dùng file mô tả kiểu DBC theo hãng/phiên bản; bộ điều khiển CAN của edge cấu hình không ACK, không phát khung. Không bao giờ phát khung lên bus BMS↔PCS.

### 5.4 MQTT 5 và Sparkplug B (uplink edge→cloud)

| Phương án | Ưu | Nhược | Kết luận |
|---|---|---|---|
| MQTT 5 + schema riêng (Protobuf + nén, envelope có `seq`) | Kiểm soát ack lệnh, hạn, seq, backfill. Message Expiry khớp hạn của lệnh | Phải tự định nghĩa | **Chọn** [PROPOSAL] |
| Sparkplug B 3.0 | Chuẩn birth/death, trạng thái online, hệ sinh thái SCADA | Chỉ có NCMD/DCMD, không có ngữ nghĩa ack/hạn/idempotency; QoS 0 cho dữ liệu; đã thấy một gateway thương mại đặt cứng Will QoS 0 làm NDEATH có thể mất | Đầu ra tùy chọn cho SCADA khách, P2 |
| OPC UA | Mô hình thông tin mạnh | Không có companion spec PV/BESS (§5.5); nặng cho 4G | Chỉ khi gặp PLC/BMS có OPC UA server hoặc khách yêu cầu |

Bằng chứng:
- [FACT, Med] Sparkplug B dùng NBIRTH/NDEATH/DBIRTH/DDEATH/STATE; NDEATH qua Last Will; broker phải hỗ trợ QoS 0 cho dữ liệu, QoS 1 cho quản lý trạng thái, retained và LWT; v3.0 đặt STATE ở `spBv1.0/STATE/<host_id>`, payload JSON — https://www.emqx.com/en/blog/sparkplug-3-0-advancements-and-formalization-in-mqtt-for-iiot ; https://docs.chariot.io/x/S4SzBw ; https://support.hms-networks.com/hc/en-us/articles/36458732970386-Is-the-the-Crimson-Sparkplug-B-implementation-compliant-with-the-spec (qua kết quả tìm kiếm).
- [FACT, High] MQTT 5 Message Expiry Interval cho phép broker bỏ tin quá hạn và giảm dần thời hạn còn lại; Session Expiry Interval thay cleanSession — https://www.emqx.com/en/blog/mqtt-message-expiry-interval ; https://docs.solace.com/API/MQTT-v50-Prtl-Conformance-Spec/mqtt-v50-C-summary-new-features.htm (qua kết quả tìm kiếm).
- [INFERENCE] QoS 1 có thể giao trùng (kiến thức chung về MQTT). Vì vậy ingest idempotent theo `(edge_id, stream, seq)` và `(series_id, ts)`; edge idempotent theo `command_id`.

Topic, payload: §7.

### 5.5 OPC UA

- [FACT, Med] Danh mục companion spec của OPC Foundation có OPC 10040 "UA for IEC 61850" (Release Candidate) và mapping IEC 61400-25 cho gió; không thấy companion spec riêng cho PV hay BESS — https://opcfoundation.org/wp-content/uploads/2026/03/OPCF-Energy-Initiative.pdf (qua kết quả tìm kiếm).
- [PROPOSAL] Không ở MVP. Adapter OPC UA client (phía dưới) chỉ làm khi một khách cụ thể có PLC/BMS công nghiệp chỉ lộ OPC UA; xếp vào nhóm "giao thức theo dự án", cần ADR.

### 5.6 IEC 61850

- [FACT, Med] GOOSE chạy trực tiếp trên Ethernet lớp 2 multicast với yêu cầu trễ < 3–4 ms tùy lớp hiệu năng; IEC 61850-7-420:2021 (Ed.2) định nghĩa logical node cho DER, gồm lưu trữ — https://softwaretoolbox.com/resources/what-is-iec61850 ; https://scc-ccn.ca/standardsdb/standards/2048725 (qua kết quả tìm kiếm).
- [INFERENCE] Với C&I behind-the-meter, 61850 chỉ cần khi: (a) site có trạm riêng với IED 61850 và chủ đầu tư yêu cầu EMS đọc/ghi qua MMS; (b) BESS quy mô MW mà PCS/PPC chỉ có giao diện 61850; (c) load shedding nhanh qua GOOSE. Trường hợp (c) thuộc hệ bảo vệ, không do edge/cloud thực hiện.
- [PROPOSAL] P2 (F-INT-18): MMS client ở edge (đọc + setpoint qua arbiter). GOOSE: không làm; nếu cần thì dùng IED/PLC chuyên dụng. Thư viện cần đánh giá giấy phép (Q-E-12).

### 5.7 IEC 60870-5-104 cho kết nối điều độ (P1 có điều kiện)

**Bối cảnh pháp lý (chưa kiểm chứng toàn văn).**
- [FACT, Med] Theo VBHN 52 (NĐ 58/2025 hợp nhất NĐ 243/2026) được tóm tắt trong nghiên cứu FusionSolar trước (`competitors_rebuild.md` Q6): hệ điện mặt trời mái nhà đấu nối **trung áp trở lên có bán điện dư** phải kết nối với hệ thống thu thập, giám sát, điều khiển của cấp điều độ; hệ trung áp không bán dư phải có "thiết bị bật tắt phát ngược".
- [FACT, Low — tóm tắt của vendor có lợi ích] Theo bản tóm tắt QĐ 1570/QĐ-EVN của Advantech: giám sát/điều khiển dùng Modbus TCP và IEC 60870-5-104, công tơ dùng IEC 62056; đường truyền ≥ 64 kbps, trễ ≤ 125 ms — https://www.advantech.com/vi-vn/resources/industry-focus/quyet-dinh-1570qd-evn-dien-mat-troi-mai-nha-dieu-can-biet ; https://vjol.info.vn/tctbgd/article/view/121843 (qua kết quả tìm kiếm). **Chưa đọc văn bản QĐ 1570**; các con số này **không được dùng làm NFR** (K §4).
- [INFERENCE] Theo A #3 (K R-10), chỉ khoảng 287/28.254 hệ đăng ký bán dư, nên phần lớn site mục tiêu ban đầu không cần kết nối điều độ. Vì vậy slave 104 trên edge là **P1 có điều kiện** (F-INT-16, F-GRID-12).

**Thông số giao thức đã thấy.**
[FACT, High] TCP port 2404 mặc định; tham số điển hình k = 12, w = 8, t1 = 15 s, t2 = 10 s, t3 = 20 s, với t2 < t1 và w ≤ 2/3·k; ASDU M_ME_NC_1 (13, float không tem thời gian), M_ME_TF_1 (36, float + CP56Time2a), C_SE_NC_1 (50, setpoint float) — https://infosys.beckhoff.com/content/1031/tf6500_tc3_iec60870_5_10x/984040459.html ; https://kb.mervis.info/doku.php/en:mervis-ide:35-help:023-server-communication-protocols:010-iec-60870-5-104-server ; https://wiki.elseta.com/books/the-vinci-software/page/iec-60870-5-104 (qua kết quả tìm kiếm).

**Cấu hình slave 104 đề xuất [PROPOSAL]** — mọi giá trị phải cấu hình được và đối chiếu yêu cầu của từng Công ty Điện lực/cấp điều độ (Q-E-01):

| Thành phần | Mặc định đề xuất | Ghi chú |
|---|---|---|
| Vai trò | Edge là controlled station (server). Điều độ là master | Port 2404 |
| Tham số | k = 12, w = 8, t0 = 30 s, t1 = 15 s, t2 = 10 s, t3 = 20 s | Giá trị phổ biến; t0 = 30 s là [INFERENCE] |
| Địa chỉ | Common Address (CA) và IOA theo bảng điểm do điều độ cấp | Không tự đặt |
| Đo lường | M_ME_TF_1 (36) cho P, Q, U, I, f, cosφ tại POC; P PV tổng; P/SOC BESS. Gửi theo deadband + chu kỳ nền | M_ME_NC_1 (13) nếu điều độ yêu cầu |
| Trạng thái | Single/double point có tem thời gian cho máy cắt, trạng thái chặn phát ngược, LOCAL/REMOTE | Số type ASDU cụ thể là [INFERENCE] kiến thức nền |
| Lệnh | C_SE_NC_1 (50) setpoint P (kW hoặc % Pđm); lệnh đơn/kép cho chặn phát ngược; select-before-operate nếu điều độ yêu cầu | Edge tạo envelope nội bộ `source = GRID_OPERATOR`, vào arbiter mức 4. ACT_CON/ACT_TERM chỉ sau readback (§8.9) |
| Đồng bộ thời gian | Nhận C_CS_NA_1 từ master; ghi nguồn thời gian | Edge vẫn chạy NTP; lệch giữa hai nguồn ghi vào event |
| Interrogation | C_IC_NA_1 trả toàn bộ ảnh điểm | — |
| Mất cloud | Slave 104 **không phụ thuộc cloud** | Bắt buộc |
| Mạng | Conduit riêng (VPN/APN của điều độ, NIC/VLAN riêng — Z4 của I §3.6) | Yêu cầu băng thông/trễ: [UNKNOWN] tới khi đọc QĐ 1570; bảo mật (IEC 62351 hay không): [UNKNOWN] |

**Phương án thay thế ở MVP**: [FACT, Med] SmartLogger có IEC 104 cho tối đa 5 kết nối bên thứ ba (nghiên cứu FusionSolar trước, `architecture_security.md` Q1); blue'Log dùng PLC chuyển đổi 104 → Modbus TCP (§10.8); Advantech ADAM-3600 được định vị cho QĐ 1570 (nghiên cứu FusionSolar trước). [PROPOSAL] Khi controller hãng đã làm slave 104, edge **không** chạy slave 104 thứ hai cho cùng điểm đấu nối; edge đọc trạng thái lệnh điều độ từ controller (nếu lộ ra) để hiển thị và audit.

### 5.8 DNP3

- [FACT, Med] IEEE 1815.2 dựa trên MESA-DER và DNP3 AN2018-001, ánh xạ đối tượng IEC 61850-7-420 sang DNP3 cho IEEE 1547/Rule 21; trạng thái xuất bản chưa rõ (các trang DNP-UG mâu thuẫn); EPRI có outstation mã nguồn mở theo AN2018-001 — https://www.dnp.org/ieee-releases-18152-standard-for-der-communications ; https://restservice.epri.com/publicdownload/000000003002015355/0/Product (qua kết quả tìm kiếm).
- [INFERENCE] Không thấy bằng chứng DNP3 dùng ở lưới phân phối Việt Nam. [PROPOSAL] P2: chỉ giữ chỗ adapter DNP3 outstation cho thị trường xuất khẩu; giấy phép thư viện cần kiểm tra.

### 5.9 OCPP cho sạc EV (P1)

| Khía cạnh | OCPP 1.6J | OCPP 2.0.1 | OCPP 2.1 |
|---|---|---|---|
| Trạng thái | Phổ biến nhất trong lắp đặt hiện có [INFERENCE] | Có chứng nhận | Công bố 23/01/2025 [FACT, High] |
| Smart charging | Ba loại profile: ChargePointMaxProfile, TxDefaultProfile, TxProfile; stackLevel cao hơn được ưu tiên; giới hạn hiệu lực là nhỏ nhất [FACT, Med–High] | Tương tự, thêm device model (SetVariables) [INFERENCE] | Thêm khối bidirectional (V2X), DER control, ISO 15118-20, giao dịch tiếp tục sau reboot [FACT, High] |
| Bảo mật | Security Whitepaper bổ sung profile 1 (HTTP Basic, không TLS), 2 (TLS + Basic), 3 (TLS + chứng chỉ client); có Ed.3 (2022), Ed.4 (02/2026) theo snippet [FACT, Low–Med, cần kiểm chứng trước khi trích dẫn chính thức] | Profile 1–3 tích hợp [INFERENCE] | Như 2.0.1 [INFERENCE] |
| Tương thích | Không tương thích với 2.x ở mức thông điệp — https://www.midapower.com/news/strategic-comparison-of-ocpp-1-6j-vs-2-0-1-for-commercial-charging-operators/ (qua kết quả tìm kiếm) | — | Logic ứng dụng 2.0.1 "vẫn tương thích" [FACT, High] |

Nguồn: https://openchargealliance.org/ocpp-2-1-is-now-available/ ; https://openchargealliance.org/protocols/open-charge-point-protocol ; https://www.bender.de/docs/charge-controller/OCPP/ocpp-smart-charging/ ; https://developer.easee.com/docs/ocpp-smart-charging ; https://openchargealliance.org/?p=159286 ; https://www.trialog.com/?p=11328 (qua kết quả tìm kiếm). Một nguồn thứ cấp nói OCPP 2.1 đã thành IEC 63584 — https://codibly.com/news-insights/8-features-ocpp-2_1 (qua kết quả tìm kiếm) — [UNKNOWN] chưa kiểm chứng.

**Kiến trúc EV [PROPOSAL]**

| Trường hợp | Giải pháp | Tính năng |
|---|---|---|
| Site không có CSMS của CPO | Edge chạy **CSMS OCPP 1.6J tối giản**, chỉ cho giám sát và smart charging; không làm thanh toán/roaming (F-EV-11 ngoài phạm vi) | F-EV-02, F-EV-03 |
| Site có CSMS của CPO | Tích hợp API của CPO (đọc phiên, gửi giới hạn); **không** chạy CSMS thứ hai trên cùng trụ | F-EV-04 |
| Đo năng lượng EV | Công tơ `MTR_EV_i` (P0) độc lập với OCPP | F-EV-01 |

Quy tắc driver OCPP [PROPOSAL]:
- Mỗi model charger có **charger profile** khai báo: đơn vị A hay W; số period tối đa; số stackLevel; có tôn trọng TxDefaultProfile khi offline không; dòng tối thiểu; quirk đã biết. [FACT, Med] Ví dụ: với Easee, TxDefaultProfile không tự xóa và có thể đè TxProfile (0 A đè 20 A) — https://developer.easee.com/docs/ocpp-smart-charging (qua kết quả tìm kiếm).
- Mọi giới hạn gửi xuống có `validTo`/`duration`; luôn cài **TxDefaultProfile an toàn** làm fallback khi mất kết nối ([FACT, Med–High] Bender: TxDefaultProfile để "keep charging controlled if connectivity is lost").
- Bảo mật tối thiểu Security Profile 2; mục tiêu Profile 3 với charger hỗ trợ; không dùng Profile 1 (K §6 #32). Credential OCPP sinh ngẫu nhiên theo site (FR-EV-003).
- Kênh EMS → CSMS bên ngoài cho giới hạn công suất site: không có chuẩn ở 1.6/2.0.1; OCPP 2.1 DER control có dùng được không là [UNKNOWN] (Q-E-08).

### 5.10 OpenADR và IEEE 2030.5 (P2)

- [FACT, Med–High] OpenADR 3.0 dùng REST/JSON (2.0b dùng XML/SOAP), có webhook; 3.0 không thay thế 2.0b; sản phẩm 3.0 đầu tiên được chứng nhận 3/2025; bản 3.1 thêm MQTT và "price clusters" — https://www.openadr.org/assets/OpenADR%20Webinar%20Nov%202023%20-%20From%202.0%20to%203.0.pdf ; https://www.openadr.org/assets/OpenADR%20AR25.pdf ; https://ecommercenews.co.nz/story/openadr-3-0-certification-marks-milestone-in-energy-sector (qua kết quả tìm kiếm).
- [FACT, Med] IEEE 2030.5 là giao thức mặc định của California Rule 21 (CSIP), dùng TLS 1.2 + chứng chỉ; chứng nhận bắt buộc từ 22/06/2020 — https://standards.ieee.org/content/dam/ieee-standards/standards/web/documents/presentations/smart_energy_slides.pdf ; https://www.qualitylogic.com/wp-content/uploads/2021/07/Data-Sheet-DER-Workshop.pdf (qua kết quả tìm kiếm).
- [INFERENCE] Không thấy chương trình DR nào ở Việt Nam dùng hai giao thức này.
- [PROPOSAL] P2 (F-OPT-20, F-INT-18): "DR adapter" ở cloud là một **nguồn lệnh** (`source = DR`, arbiter mức 8), ánh xạ sự kiện DR → `SET_IMPORT_LIMIT`/`SET_ESS_P` có cửa sổ thời gian. Nếu cần, làm VEN OpenADR 3.x trước. Không làm 2030.5 trừ khi bán vào thị trường dùng Rule 21/CSIP. Sản phẩm chỉ được gọi là "VPP-capable" (K §6 #23).

### 5.11 API cloud của hãng

#### 5.11.1 Huawei FusionSolar Northbound (nghiên cứu FusionSolar trước)

| Hạng mục | Nội dung | Nhãn |
|---|---|---|
| Kiểu API | POST/JSON dưới `https://<region-host>/thirdData/`; **pull-only**, không webhook trong các phiên bản tài liệu đã xem | [FACT, High] |
| Tài khoản | Do quản trị công ty installer tạo (System > Company Management > Northbound Management); từ khoảng 09/2025 **chủ nhà máy phải cấp quyền API** rõ ràng | [FACT, Med] |
| Xác thực | `POST /thirdData/login` với `userName` + `systemCode`; token trả về trong cookie `XSRF-TOKEN`, gửi lại làm header; failCode 305 = hết phiên | [FACT, Med] (mã nguồn pyhfs, HA) |
| Hạn mức | Giới hạn theo phút mỗi interface (failCode 407), giới hạn ngày mỗi user (20618), giới hạn số phiên (20400) | [FACT, Med] |
| Lô | Real-time: ≤ 100 nhà máy hoặc 100 thiết bị cùng loại mỗi lần; lịch sử thiết bị: 10 thiết bị × 3 ngày ở bước 5 phút — https://support.huawei.com/enterprise/en/doc/EDOC1100358266/b9df65c2/monitoring | [FACT, High] |
| Độ phân giải | Đo 5 phút, truyền 15 phút (meteocontrol); job đêm hỏi lại 7 ngày | [FACT, Med] |
| Thời gian | pyhfs ghi rằng timestamp tài liệu nói giờ nhà máy nhưng thực tế là UTC epoch ms | [FACT, Low–Med] |
| Lỗi quyền | `success: true` kèm `data: null` khi chủ chưa cấp quyền | [FACT, Med] |
| API ghi | Active power control, battery dispatch, battery mode, cấu hình pin: task **bất đồng bộ**, **chỉ ở chế độ OAuth Connect**, "không gọi lại cho cùng pin/nhà máy trước khi task hoàn tất" — https://support.huawei.com/enterprise/en/doc/EDOC1100379184/7a471100/control-apis ; https://support.huawei.com/enterprise/en/doc/EDOC1100492747 | [FACT, High] |
| Chưa biết | Endpoint OAuth, grant type, thời hạn token, con số hạn mức ở chế độ OAuth | [UNKNOWN] (Q-E-14) |

Thiết kế connector Huawei [PROPOSAL] (F-MON-02 MVP; F-INT-14 ghi P2):
- Một tài khoản API cho mỗi site hoặc mỗi khách; không dùng chung tài khoản giữa môi trường thử và thật (giới hạn phiên).
- Rate limiter theo endpoint (tối đa khoảng 1 lần/phút/interface theo quy tắc "one-minute access frequency"); 407 → chờ ≥ 60 s; 20618 → dừng tới ngày hôm sau và cảnh báo.
- Gom `stationCodes`/`devIds` tới 100; lịch sử 10 thiết bị × 3 ngày; job backfill ban đêm 7 ngày.
- Phân biệt "success nhưng data null" (mất quyền) với dữ liệu rỗng; trạng thái `AUTH_FAILED` ([05 §6](05-domain-model.html#s6) `Integration.status`).
- Mọi điểm qua connector mang quality `UNCERTAIN_VENDOR_CLOUD` và `ts` = thời điểm hãng gán (đã chuẩn hóa UTC), `ts_ingest` = lúc kéo về.
- Ghi qua OAuth Connect (P2): tuần tự hóa theo nhà máy; ánh xạ trạng thái task → `DISPATCHED`/`APPLIED`/`FAILED_*`; chỉ dùng cho **lịch chậm** (theo giờ), không cho vòng điều khiển; cờ riêng, hạng ≥ C2 (FR-INT-028).

#### 5.11.2 Hãng khác

| Hãng | Đường đọc | Đường ghi | Giới hạn/đặc điểm | Kết luận cho sản phẩm | Nguồn (qua kết quả tìm kiếm) |
|---|---|---|---|---|---|
| Sungrow iSolarCloud | Open API; tài liệu chỉ xem được sau đăng nhập portal developer | Một integration cộng đồng điều khiển được sạc/xả, SOC, lịch (thử trên 1 hệ); bên tích hợp khuyên tạo user API chỉ đọc | Firmware cũ có thể bỏ qua giới hạn công suất; bộ khóa API mô tả mâu thuẫn giữa nguồn | Đọc: P1. Ghi: [UNKNOWN] về hỗ trợ chính thức | https://docs.eniris.be/da/Controller/Devices/Cloud/ISolarCloud ; https://community.home-assistant.io/t/sungrow-isolarcloud-integration-custom-hacs-sensors-optional-charge-discharge-control/1017858 |
| SMA | Monitoring API (Sunny Portal/ennexOS), OAuth code grant, sandbox dữ liệu giả | GridControl API — phạm vi chưa rõ | "Live API" không được dùng để giám sát liên tục; hệ chuyển sang ennexOS trả HTTP 308 kèm ID mới; có thể tính phí | Đọc: P1. Ghi: [UNKNOWN] (Q-E-11) | https://developer.sma.de/sma-apis ; https://developer.sma.de/sma-sandbox-apis ; https://solytic.com/knowledge/set-up-api-access-sma-monitoring-api/ |
| Solis | SolisCloud API, ký HMAC-SHA1 trên (verb, Content-MD5, Content-Type, Date, path), header `Authorization: API <KeyId>:<Sign>` | Không thấy tài liệu ghi | "3 lần mỗi 5 giây mỗi IP" (nguồn cộng đồng 2023, Low); tên endpoint không thống nhất | Chỉ đọc, P1 | https://usservice.solisinverters.com/support/solutions/articles/73000661192-solis-api-troubleshooting ; https://projects.bentasker.co.uk/gils_projects/issue/utilities/telegraf-plugins/9.html ; https://github.com/hultenvp/soliscloud_api |
| Growatt | "Official Growatt V1 API" qua token, host theo vùng; API "classic" bằng mật khẩu có thể khóa tài khoản tới 24 h | Không thấy tài liệu ghi | Không thấy con số hạn mức chính thức cho V1 | Chỉ đọc, P1 | https://www.home-assistant.io/components/growatt_server/ |
| Deye | DeyeCloud developer API (appId/appSecret + mật khẩu băm SHA-256), base URL `https://eu1-developer.deyecloud.com/v1.0` theo client cộng đồng | Chỉ thấy endpoint đọc cấu hình pin | Có ý kiến cho rằng chạy qua server Solarman | Chỉ đọc, P1 | https://mirrors.edge.kernel.org/CPAN/modules/by-module/Config/KORNIX/DeyeCloud-Client-0.0.2.readme ; https://community.home-assistant.io/t/deye-cloud-integration/813153 |

[INFERENCE] Không hãng nào trong bảng có webhook/push trong các nguồn đã thấy. Mọi connector cloud là **pull có hạn mức**, phù hợp gói "chỉ giám sát", không phù hợp làm đường điều khiển.

Yêu cầu chung cho connector [PROPOSAL] (F-INT-13, FR-INT-021): rate limiter theo endpoint và theo tài khoản; credential mã hóa theo tenant, vault path của monitoring plane; backfill ban đêm 7 ngày; phân biệt mất quyền với dữ liệu rỗng; quality `UNCERTAIN_VENDOR_CLOUD`; cảnh báo connector sau `T_offline_alarm_connector` = 30 phút ([04 §2](04-business-requirements.md)).

---

## 6. Kiến trúc edge gateway

### 6.1 Thành phần

```
                          ┌───────────────────────────── EDGE (Z2 OT side | Z3 WAN side) ─────────────────────────────┐
 OT LAN / RS485 / CAN     │                                                                                            │   WAN (outbound only)
 ─────────────────────►   │  Protocol adapters ──► Driver runtime ──► Process image (1 s cycle) ──► Uplink publisher ─┼──► MQTT 5 + mTLS
  Modbus RTU/TCP, SunSpec │  (Modbus, CAN-listen,   (register map,     │   ▲                  │          (batch, seq,    │
  CAN (listen), OCPP WS   │   OCPP CSMS P1,          scale, sign,      ▼   │                  ▼           compress)      │
  DI/DO                   │   IEC104 slave P1)       quality)        Arbiter + limit chain   Store-and-forward  ◄──ack──┼─── down/cmd, down/config
                          │                                          (12 mức, SOE, IL-xx)   (SQLite/RocksDB, SSD)      │
                          │  Polling scheduler ── Capability discovery ── Command executor (readback, retry, expiry)   │
                          │  Clock (chrony + RTC) · Config store (desired/reported, ký số) · OTA A/B · HW watchdog     │
                          │  Local HMI (P1, F-MON-11) · Local audit log · Health metrics                               │
                          └────────────────────────────────────────────────────────────────────────────────────────────┘
```

| Thành phần | Trách nhiệm | Tính năng |
|---|---|---|
| Protocol adapters | Modbus RTU/TCP master; SunSpec discovery; CAN listen-only (P1); OCPP 1.6J CSMS tối giản (P1); IEC 104 slave (P1); Modbus TCP server xuất lại (P1); MQTT 5 client | F-INT-04, F-INT-05, F-INT-15, F-EV-03, F-INT-16, F-INT-17, F-INT-08 |
| Driver registry và runtime | Nạp `DriverVersion` (map khai báo + overlay), giải mã, chuẩn hóa dấu/đơn vị, gán quality | F-INT-03, F-INT-06 |
| Process image | Ảnh giá trị của mọi điểm cho một chu kỳ; giá trị không đổi trong chu kỳ | §6.6 |
| Arbiter + limit chain | Phân xử 12 mức, kẹp theo SOE và CCL/DCL, interlock IL-01…IL-10, fallback | F-OPT-01, F-OPT-03, F-SEC-08, F-BESS-10 |
| Command executor | Ánh xạ lệnh chuẩn → chuỗi ghi theo driver; readback; theo dõi hạn | F-INT-07 |
| Store-and-forward | Buffer bền, ack theo `seq`, backfill có giới hạn tốc độ | F-INT-09 |
| Clock | chrony ≥ 2 nguồn + RTC có pin; `clock_state` | F-INT-10 |
| Config store | Desired/reported có version, ký số | F-INT-11 |
| OTA | A/B ký số, rollback, anti-rollback | F-INT-12 |
| HMI cục bộ | Trạng thái, interlock, LOCAL/REMOTE khi mất Internet | F-MON-11 (P1) |

**Runtime edge — ứng viên ADR (người viết 06 cấp số).** [FACT, Med–High] OpenEMS Edge chạy mô hình input-process-output trong một **Cycle** khoảng 1 s; giá trị channel không đổi trong một cycle; scheduler quyết định thứ tự controller; Edge↔Backend dùng JSON-RPC qua WebSocket; dữ liệu tách thành Timestamped/Aggregated/ResendDataNotification — https://openems.github.io/openems.io/openems/latest/edge/architecture.html ; https://openems.github.io/openems.io/openems/latest/coreconcepts.html ; https://openems.github.io/openems.io/openems/latest/edge/scheduler.html ; https://github.com/OpenEMS/openems/releases (qua kết quả tìm kiếm). [UNKNOWN] Giấy phép: repo có file EPL-2.0 **và** AGPL-3.0 (B L44); cách áp theo module chưa rõ, nên **chặn** quyết định dùng OpenEMS làm nền (K R-21). [PROPOSAL] PoC hai phương án — (a) dựa trên OpenEMS Edge cho driver + controller, (b) runtime Java tự xây theo mô hình process image — với hợp đồng §7–§8 làm lớp ngoài cố định để phương án nào cũng thay được. Tiêu chí: giấy phép (ý kiến pháp lý), độ chín của driver, khả năng thêm IEC 104/OCPP, khớp stack Java của team, chi phí giữ hợp đồng §7–§8.

### 6.2 Driver registry và register map

Driver là **dữ liệu toàn cục** do nền tảng phát hành (tenant không sửa), có phiên bản và hash ([05 §6](05-domain-model.html#s6) `DriverDefinition/DriverVersion`).

**Thuộc tính của mỗi thanh ghi trong register map [PROPOSAL]** (bổ sung theo C X-C05, F X-F02, I X-I-02, H X-H04):

| Thuộc tính | Giá trị cho phép / ví dụ | Lý do |
|---|---|---|
| `address` | Địa chỉ trên dây, 0-based | §5.1.3 |
| `doc_address`, `doc_ref` | Địa chỉ trong tài liệu hãng, mã tài liệu + issue | Truy vết |
| `fc` | 1, 2, 3, 4 (đọc); 5, 6, 16 (ghi) | §5.1.2 |
| `type` | U16, I16, U32, I32, U64, I64, F32, F64, STRING(n), BITFIELD16/32, ENUM16 | Đủ cho Huawei/SunSpec/công tơ |
| `word_order` | `BIG` (ABCD), `LITTLE_WORD` (CDAB) | Đặc tả không quy định |
| `byte_order` | `BIG` (mặc định), `SWAP` | Hiếm |
| `scale` | Hằng số (ví dụ Huawei 32080 I32 gain 1000 — nghiên cứu FusionSolar trước) **hoặc** tham chiếu thanh ghi scale factor (SunSpec `*_SF`, giá trị × 10^SF; đọc SF **cùng lượt** với giá trị) | Ví dụ SunSpec: thô 1234, SF = −2 → 12,34 [FACT, Low–Med, nguồn thứ cấp] |
| `offset` | Số | Nhiệt độ một số hãng |
| `unit_src` | Đơn vị gốc của hãng (kW, W, 0,1 kWh…) | Driver đổi về `unit_raw` của điểm |
| `sign_convention` | Mô tả dấu gốc, ví dụ Huawei 37113 "> 0 feed-in, < 0 import" (nghiên cứu FusionSolar trước) → driver nhân −1 | Chuẩn hóa về K R-01/R-02 |
| `na_values` | Ví dụ 0xFFFF (U16); 0x8000 (I16) là [UNKNOWN] (Q-E-07) | Sentinel → `BAD_DEVICE` |
| `kind` | `measurement`, `counter`, `status`, `setting`, `alarm`, `nameplate` (ánh xạ sang `gauge/register/state/setpoint/event` ở [05 §7](05-domain-model.html#s7)) | Quyết định cách tổng hợp |
| `register_wrap` | Giá trị quay vòng của bộ đếm, ví dụ 2^32 Wh | F §3.5: uint32 Wh tràn sau ≈ 2,45 năm với site 1 MW (K đã tính lại) |
| `lsb` | Bước nhỏ nhất của bộ đếm | Lọc rung số âm nhỏ (F §3.5) |
| `interval_label` | `START` / `END` cho dữ liệu khoảng (load profile) | Driver chuyển về `bucket_start` (K R-05) |
| `timestamp_source` | `NONE` / `DEVICE_UTC` / `DEVICE_LOCAL` + múi giờ thiết bị | Huawei SUN2000 dùng giờ địa phương (§10.1) |
| `access` | `R`, `RW`, `W` | Cấm ghi vào thanh ghi R |
| `persist` | `VOLATILE`, `NVM`, `UNKNOWN` | Ghi setpoint chu kỳ vào NVM có thể mòn flash (PR-E-15) |
| `min_write_interval_ms` | Số | Chống ghi dồn; mặc định thiết bị ≤ 1 setpoint/2 s ([04 §2](04-business-requirements.md)) |
| `readback_ref` | Thanh ghi đọc lại tương ứng (có thể khác thanh ghi ghi) hoặc `NONE` | Thiết bị không đọc lại được → không thể báo `APPLIED` (§8.5) |
| `watchdog_support`, `revert_timeout_s` | Cơ chế hoàn nguyên của thiết bị (§8.6) | I X-I-02 |
| `evidence` | `VENDOR_DOC` / `LAB_TEST` / `FIELD_TEST` / `COMMUNITY` | Thanh ghi `COMMUNITY` không được vào driver `VERIFIED_*` |

**Ví dụ register map (cấu hình khai báo, không phải code; địa chỉ minh họa)**

Ví dụ dùng hai thanh ghi Huawei do nghiên cứu FusionSolar trước đọc từ tài liệu "Solar Inverter Modbus Interface Definitions" Issue 05 (qua bản PDF trên diễn đàn ioBroker), nên `evidence` ghi `VENDOR_DOC` nhưng trạng thái driver vẫn `UNVERIFIED` cho tới khi thử lab.

```yaml
driver_id: huawei.sun2000.inverter
version: 0.1.0
applies_to:
  manufacturer: Huawei
  models: ["SUN2000-*KTL-*"]       # dải model phải chốt khi thử lab
  firmware: ">=2023"                # [UNKNOWN] dải chính xác
verification_status: UNVERIFIED
connection:
  protocol: MODBUS_TCP
  ports: [6607, 502]
  unit_id: 1
  single_client: true
  connect_delay_ms: 2000
  min_poll_period_ms: 5000          # khi đi qua SDongle
registers:
  - point: pv_inverter.p            # W, + = phát
    address: 32080
    fc: 3
    type: I32
    word_order: BIG
    unit_src: kW
    scale: 0.001                    # gain 1000 → kW
    unit_raw: W                     # driver nhân 1000 sau scale
    kind: measurement
    access: R
    evidence: VENDOR_DOC
    doc_ref: "Solar Inverter Modbus Interface Definitions, Issue 05, 2023-02-16"
  - point: meter.p                  # công tơ qua inverter; W, + = nhập (K R-01)
    address: 37113
    fc: 3
    type: I32
    unit_src: W
    sign_convention: "+ = feed-in (export), - = import"
    sign_transform: -1
    kind: measurement
    access: R
    evidence: VENDOR_DOC
```

### 6.3 File point mapping theo site

Point mapping nối **thiết bị cụ thể ở site** với driver và với chuỗi cloud. Nó là một phần của `EdgeConfigVersion` có ký số ([05 §6](05-domain-model.html#s6)).

| Trường | Ý nghĩa |
|---|---|
| `device_id`, `asset_id`, `metering_point` | Thiết bị vật lý, vị trí chức năng, mã điểm đo chuẩn (`MTR_POC`, `MTR_PV`, …, K §6 #10) |
| `endpoint` | Giao thức, địa chỉ IP/cổng/unit ID, hoặc cổng serial/baud/parity |
| `driver` | `driver_id@version` |
| `points[]` | `code`, `pid` (mã số trên dây), `sampling_class` (C1–C5), `deadband`, `max_age_s`, `enabled` |
| `ct_ratio`, `vt_ratio` | Khi công tơ trả giá trị thứ cấp |
| `control` | `write_enabled`, `control_owner` theo chức năng, `requires_native_fallback` |

```json
{
  "config_version": 42,
  "site_id": "7a1c…",
  "edge_id": "edge-0f3e…",
  "devices": [
    {
      "device_id": "dev-poc-01",
      "metering_point": "MTR_POC",
      "endpoint": {"protocol": "MODBUS_TCP", "host": "10.10.1.21", "port": 502, "unit_id": 1},
      "driver": "generic.meter.3ph@1.2.0",
      "ct_ratio": 800, "vt_ratio": 1,
      "points": [
        {"code": "meter.p",        "pid": 1001, "sampling_class": "C1", "max_age_s": 3},
        {"code": "meter.q",        "pid": 1002, "sampling_class": "C1", "max_age_s": 3},
        {"code": "meter.e_import", "pid": 1010, "sampling_class": "C4"},
        {"code": "meter.e_export", "pid": 1011, "sampling_class": "C4"}
      ],
      "control": {"write_enabled": false}
    }
  ],
  "signature": {"alg": "ES256", "kid": "cfg-signer-2026-01", "jws": "…"}
}
```

### 6.4 Khám phá năng lực và `capability_profile`

Cloud chỉ cho tạo lệnh mà profile hỗ trợ (FR-INT-005). Profile được sinh từ: kết quả khám phá (§5.2.2), khai báo của driver, kết quả test commissioning (§9).

```json
{
  "capability_profile_id": "cap-9b2…",
  "device_id": "dev-pcs-01",
  "driver": "vendorx.pcs.500k@0.3.0",
  "fingerprint": {"manufacturer": "VendorX", "model": "PCS-500", "firmware": "V1.08", "serial": "…"},
  "discovered_sunspec_models": [1, 701, 702, 704, 713],
  "readable_points": ["pcs.p", "pcs.q", "ess.soc", "ess.p_charge_max", "ess.p_discharge_max"],
  "commands": {
    "SET_ESS_P":   {"supported": true, "unit": "W", "min_w": -500000, "max_w": 500000,
                    "readback": "REGISTER", "readback_timeout_s": 10, "min_write_interval_ms": 2000},
    "SET_ESS_MODE": {"supported": true, "modes": ["SELF_CONSUMPTION", "TOU_SCHEDULE", "IDLE"]},
    "SET_Q":       {"supported": false}
  },
  "watchdog": {"support": "HEARTBEAT_REGISTER", "revert_timeout_s": 30, "tested": false},
  "requires_native_fallback": true,
  "persist_of_setpoint_registers": "UNKNOWN",
  "verification_status": "UNVERIFIED"
}
```

Quy tắc [PROPOSAL]: `requires_native_fallback = true` cho tới khi test watchdog (F-INT-28) đạt; khi đó PDP chặn setpoint P cưỡng bức tới thiết bị (F-SEC-15).

### 6.5 Bộ lập lịch polling

Lớp tần suất theo K §6 #19 và F §3.1.2:

| Lớp | Đọc tại edge | Gửi cloud | Điểm áp dụng |
|---|---|---|---|
| C1 điều khiển nhanh | 1 s (200 ms–1 s nếu driver cho phép) | Tổng hợp 5 s (avg/min/max/last/n) | P/Q tại `MTR_POC`, P PCS, SOC, CCL/DCL, setpoint, P cho phép |
| C2 vận hành | 1–5 s | Tổng hợp 60 s | Phần lớn P/U/I/T inverter, PCS, submeter |
| C3 chậm | 10–60 s | 300 s hoặc khi đổi | Nhiệt độ tủ, SOH, cấu hình, string ít biến động |
| C4 thanh ghi | 1–60 s, **và ngay sau mỗi biên 5 phút** | Mỗi 60 s và giá trị tại hoặc ngay sau mỗi biên 5 phút | A+/A−, `total_yield`, E sạc/xả |
| C5 sự kiện | Tức thời | Tức thời (QoS 1) | Alarm, đổi trạng thái/mode, ack lệnh |
| Static | Khi kết nối và mỗi ngày | Khi đổi | Nameplate, firmware |

Quy tắc lập lịch [PROPOSAL]:
1. Lập lịch theo **endpoint** (một hàng đợi tuần tự mỗi bus RTU hoặc mỗi kết nối TCP), vì một thiết bị chỉ có một connection owner.
2. Ưu tiên: C1 > đọc biên 5 phút của C4 > C2 > C3 > static. Lệnh ghi chen trước mọi đọc trừ C1 của `MTR_POC`.
3. Tính trước ngân sách mỗi bus từ số block và thời gian giao dịch đo được (§5.1.4); nếu chu kỳ C1 không đạt thì từ chối cấu hình và cảnh báo khi commissioning, không âm thầm giãn chu kỳ.
4. Đo và báo `poll_cycle_ms` p50/p99 theo bus, số lần trễ chu kỳ.
5. Đọc biên 5 phút: lên lịch đọc C4 trong cửa sổ `[biên, biên + 5 s]`; nếu lỡ thì đánh dấu để pipeline phân bổ theo tỷ lệ thời gian (F §3.5, cờ `INTERPOLATED` khi mẫu cách biên > 30 s).

### 6.6 Vòng điều khiển cục bộ

| Hạng mục | Đặc tả [PROPOSAL] | Căn cứ |
|---|---|---|
| Chu kỳ | 1 s; thực thi p99 ≤ 200 ms (NFR-PERF-006) | F-OPT-03 |
| Process image | Đầu chu kỳ chụp giá trị + quality + tuổi của mọi điểm điều khiển; trong chu kỳ không đọc lại | Mô hình OpenEMS (§6.1) |
| Thứ tự trong chu kỳ | (1) Kiểm interlock IL-01…IL-10 → (2) tính giới hạn mức 1–6 → (3) áp lệnh tay/lịch/mặc định trong khoảng còn lại → (4) phân bổ cho thiết bị → (5) ghi (tôn trọng `min_write_interval_ms`) → (6) ghi mã lý do | K R-07 |
| Vòng giới hạn xuất (khi `control_owner = EDGE`) | PI có anti-windup, hysteresis bất đối xứng (giảm nhanh, tăng chậm), ưu tiên sạc BESS trước khi cắt PV | F-GRID-05 |
| Dữ liệu cũ | `MTR_POC` cũ hơn `T_stale_poc` (3 s) hoặc BMS cũ hơn `T_stale_bms` (5 s) → ESS P = 0 hoặc chế độ native; PV về giới hạn native trong ≤ 2 chu kỳ | K §6 #17; NFR-REL-007 |
| Thiết bị không watchdog | Không nhận setpoint P cưỡng bức; chỉ đổi giữa chế độ native an toàn | K §6 #17 |
| Khởi động lại | `SAFE_START`: không ghi gì cho tới khi ≥ 2 chu kỳ đọc hợp lệ và đồng hồ hợp lệ | NFR-REL-003 |
| Watchdog phần cứng | Reset edge nếu vòng treo > 10 s | NFR-REL-003 |
| Mã lý do | Mỗi quyết định ghi `ARBITER_REASON {level, code}`, ví dụ `CLAMPED_BY_BMS`, `OVERRIDDEN_BY_GRID_OPERATOR` | F-OPT-11, F-BESS-09 |

Logic tầng 1 chi tiết thuộc [08](08-energy-optimization.md).

### 6.7 Store-and-forward và định cỡ

**Yêu cầu** (K §6 #18, FR-INT-009): không mất dữ liệu khi mất mạng ≤ 7 ngày (cứng); mục tiêu buffer 30 ngày ở tần suất cloud; dữ liệu 1 s giữ vòng tròn 7 ngày tại edge.

**Định cỡ [INFERENCE — tính toán]** dựa trên site tham chiếu 1.000 điểm của F §3.1.3 (10% điểm ở 5 s, 90% ở 60 s → khoảng 35 mẫu/s lên cloud, 3,02 M mẫu/ngày) và site lớn 5.000 điểm (K §3.5 đề xuất cho 06). Giả định nén: lô nhị phân 10–15 B/mẫu cho dữ liệu tần suất cloud; 3–8 B/mẫu cho dữ liệu 1 s cục bộ (F §3.1.3, chưa đo — Q-E-13).

| Hạng mục | Site 1.000 điểm | Site 5.000 điểm |
|---|---|---|
| Mẫu 1 s cục bộ/ngày | 86,4 M | 432 M |
| Dữ liệu 1 s, 7 ngày (3–8 B/mẫu) | 1,8–4,8 GB | 9,1–24,2 GB |
| Mẫu tần suất cloud/ngày | 3,02 M | 15,1 M |
| Buffer tần suất cloud/ngày (15 B/mẫu) | ≈ 45 MB | ≈ 227 MB |
| Buffer 7 ngày (NFR cứng) | ≈ 0,32 GB | ≈ 1,6 GB |
| Buffer 30 ngày (mục tiêu) | ≈ 1,36 GB | ≈ 6,8 GB |
| Băng thông realtime trung bình | ≈ 4,2 kbps | ≈ 21 kbps |
| Thời gian xả 7 ngày tồn đọng ở 1 Mbps | ≈ 42 phút | ≈ 3,5 h |
| Thời gian xả 7 ngày tồn đọng ở 256 kbps | ≈ 2,7 h | ≈ 13,8 h |

Phép tính: 3,02 M × 15 B = 45,3 MB/ngày; × 8 bit / 86.400 s ≈ 4,2 kbps; 7 × 45,3 MB = 317 MB; 317 MB × 8 / 1 Mbps ≈ 2.536 s ≈ 42 phút.

[PROPOSAL] Hệ quả:
- Ổ lưu trữ edge: **≥ 32 GB** cho site tham chiếu, **≥ 64 GB** cho site lớn (để chừa chỗ cho OS A/B, log, audit cục bộ, hệ số an toàn 2×). SSD/eMMC công nghiệp, chọn theo TBW; ghi theo lô, không fsync từng mẫu.
- Hai vùng tách biệt: `ring_1s` (vòng tròn, ghi đè cũ nhất) và `uplink_queue` (không ghi đè; khi đầy 90% → cảnh báo `BUFFER_HIGH`; khi đầy 100% → bỏ dữ liệu C3 trước, rồi C2; **không bao giờ** bỏ C4 thanh ghi và C5 sự kiện/ack lệnh).
- Xả buffer: realtime trước, backfill trên topic `up/backfill` với giới hạn tốc độ cấu hình (mặc định 30% băng thông đo được, trần theo tenant) để chịu đỉnh ingest 5–10× khi nhiều site cùng hồi phục (F §3.1.3).
- Thanh ghi C4 cho phép tính lại điện năng chính xác sau mất kết nối, kể cả khi mất mẫu gauge.

### 6.8 Đồng bộ thời gian

| Hạng mục | Đặc tả | Nhãn |
|---|---|---|
| Nguồn | chrony với ≥ 2 nguồn NTP (ưu tiên NTS hoặc NTP nội bộ) + RTC có pin; GNSS tùy chọn cho site trung áp | [PROPOSAL] |
| Độ chính xác | NTP đạt cỡ 1–100 ms; PTP cỡ µs cần hardware timestamping; PTP phần mềm khoảng 100 µs — https://timebeat.app/blog/ptp-vs-ntp ; https://sunplus.atlassian.net/wiki/x/JQB1eQ (qua kết quả tìm kiếm) | [FACT, Med] |
| Trạng thái | `SYNCED` (\|offset\| < 100 ms), `DEGRADED` (< 1 s), `UNSYNCED` (RTC only hoặc ≥ 1 s) | [PROPOSAL] ([04 §2](04-business-requirements.md)) |
| Hệ quả | `UNSYNCED` → mọi mẫu gắn `UNCERTAIN_CLOCK`; mọi lệnh bị chặn (IL-06) vì không kiểm được hạn | [PROPOSAL] |
| PTP | Không ở MVP; chỉ khi có IED 61850/PMU | [PROPOSAL] |
| Đồng hồ thiết bị | Đặt giờ thiết bị theo lịch nếu driver hỗ trợ; driver chuẩn hóa `ts_src` về UTC. [FACT, Low–Med] Huawei SUN2000: thanh ghi 40000 (U32, epoch giây **theo giờ địa phương**), múi giờ 43006 (I16, phút); có người gặp exception khi ghi — https://community.openhab.org/t/reading-data-from-huawei-inverter-sun-2000-3ktl-10ktl-via-modbus-tcp-and-rtu/87670?page=5 (qua kết quả tìm kiếm) | Thanh ghi từ diễn đàn: không vào driver `VERIFIED_*` |
| Nguồn IEC 104 | Khi có clock sync từ điều độ: ghi lệch với NTP vào event; không tự đổi nguồn | [PROPOSAL] |

### 6.9 Quality tầng điểm

Bộ mã tầng điểm (tầng 1 của K R-06). Tầng chuỗi (nguồn gốc + bitmask của F, `STALE` đổi thành `FROZEN`) và tầng KPI (enum của C) thuộc [05 §7, §17](05-domain-model.html#s7).

| Nhóm | Mã | Nghĩa | Ánh xạ sang tầng chuỗi (F) |
|---|---|---|---|
| GOOD | `GOOD` | Đọc trực tiếp, trong hạn | origin `MEASURED` |
| GOOD | `GOOD_LOCAL_OVERRIDE` | Đúng nhưng thiết bị ở chế độ local/manual | `MEASURED` + ngữ cảnh `MAINTENANCE` nếu áp dụng |
| UNCERTAIN | `UNCERTAIN_STALE` | Quá `max_age_s` (mặc định 3 × chu kỳ poll) | Không ghi mẫu mới; khoảng trống |
| UNCERTAIN | `UNCERTAIN_CLOCK` | Edge `UNSYNCED` | bit `CLOCK_SUSPECT` |
| UNCERTAIN | `UNCERTAIN_OUT_OF_RANGE` | Ngoài range vật lý | bit `OUT_OF_RANGE` |
| UNCERTAIN | `UNCERTAIN_SUBSTITUTED` | Giá trị thay thế (nhập tay, ước tính tại edge) | origin `SUBSTITUTED`/`MANUAL`/`ESTIMATED` |
| UNCERTAIN | `UNCERTAIN_VENDOR_CLOUD` | Lấy qua cloud hãng (trễ, đã gộp) | `MEASURED` + bit nguồn `VENDOR_CLOUD` |
| BAD | `BAD_COMM` | Mất liên lạc với thiết bị | Khoảng trống |
| BAD | `BAD_CONFIG` | Exception 01/02/03, map sai | Khoảng trống + cảnh báo cấu hình |
| BAD | `BAD_DEVICE` | Thiết bị báo lỗi cảm biến hoặc giá trị sentinel | Khoảng trống |
| BAD | `BAD_NOT_SUPPORTED` | Thiết bị không có điểm này | Không tạo chuỗi |

Phát hiện giá trị đóng băng (`FROZEN`) là việc của tầng chuỗi ở cloud (F-ALM-02), không phải mã tầng điểm. UI dùng `freshness ∈ {LIVE, DELAYED, OLD, OFFLINE, NO_DATA}` tách riêng (F-MON-04) và **không bao giờ hiển thị 0 thay cho thiếu dữ liệu** (K §6 #9). Bộ mã lấy cảm hứng từ quality IEC 61850 / StatusCode OPC UA là [INFERENCE], không trích dẫn.

### 6.10 Trùng, sai thứ tự, đến trễ

| Tình huống | Tại edge | Tại cloud |
|---|---|---|
| Trùng do QoS 1 / gửi lại | `seq` đơn điệu theo `(edge_id, stream)`, lưu NVM theo khối, **không reset khi khởi động lại** | Bỏ bản trùng theo `(edge_id, stream, seq)`; upsert theo `(series_id, ts)`; khác giá trị → giữ bản `rev` cao hơn, ghi audit |
| Sai thứ tự | Gửi theo thứ tự `seq` trong một stream; backfill tách topic | TSDB ghi thứ tự bất kỳ; `latest_value` chỉ tiến khi `ts` > `ts` hiện có |
| Đến trễ | Backfill giữ nguyên `ts` gốc | ≤ 7 ngày: refresh continuous aggregate; > 7 ngày hoặc chunk đã nén: `late_landing` → `dirty_bucket` → job tính lại (F-HIST-04) |
| Lỗ `seq` | — | Cloud yêu cầu edge gửi lại khoảng `[seq_a, seq_b]` qua `down/config` loại `RESEND_REQUEST`; nếu edge đã mất (buffer tràn) → sự kiện `DATA_LOSS` có khoảng thời gian |
| Bộ đếm năng lượng | Gửi giá trị thô int64 | Máy trạng thái delta (F-HIST-02): `ROLLOVER` theo `register_wrap`, `RESET`, thay công tơ là `AssetEvent` |

### 6.11 Vận hành offline (mất cloud)

| Thành phần | Hành vi [PROPOSAL] |
|---|---|
| Vòng cục bộ | Tiếp tục: zero-export, trần nhập, limit chain, SOC guard (không phụ thuộc cloud) |
| Lệnh tay đang hiệu lực | Chạy tới `expires_at` rồi `on_expiry` |
| Lịch | Chạy lịch đã nhận (horizon ≥ 48 h); hết lịch → chiến lược mặc định an toàn (thường self-consumption có giới hạn + zero-export + giữ dự phòng) — `run_mode = FALLBACK_SCHEDULE` rồi `DEFAULT_STRATEGY` |
| IEC 104 slave, CSMS OCPP cục bộ (P1) | Tiếp tục chạy |
| Telemetry | Ghi buffer (§6.7) |
| Lệnh mới | Không có; HMI cục bộ (P1) chỉ cho thao tác của người tại chỗ ở chế độ LOCAL |
| Phát hiện ở cloud | Heartbeat 30 s; `OFFLINE` sau 3 heartbeat lỡ (≈ 90 s); cảnh báo người sau 5 phút (NFR-REL-008) |

### 6.12 Kết nối lại và backfill

Trình tự [PROPOSAL]:
1. Kết nối lại với backoff mũ có jitter (1 s → tối đa 5 phút); mTLS bằng chứng chỉ vận hành.
2. Publish `up/state` (retained): `online`, `firmware_version`, `config_version_reported`, `clock_state`, `run_mode`, `local_remote_state`, `maintenance_substate`, `active_commands[]` (command_id, trạng thái, `expires_at`), `active_plan_ref`, `buffer_oldest_ts`, `last_seq_by_stream`.
3. Cloud đối soát: config desired ≠ reported → đẩy lại config; lệnh cloud ghi `SENT` mà edge không có → `UNDELIVERED` nếu đã quá hạn (**không gửi lại**); lệnh còn hạn → gửi lại cùng `command_id` (edge idempotent).
4. Edge nhận `down/cmd` còn hạn (Message Expiry đã lọc lệnh quá hạn ở broker) và `down/config`.
5. Realtime C1/C5 chạy ngay; backfill xả theo giới hạn tốc độ, cũ nhất trước, trên `up/backfill`.
6. Cloud ack theo `seq`; edge xóa dữ liệu đã ack khỏi `uplink_queue`.

### 6.13 Quản lý cấu hình và firmware từ xa

| Hạng mục | Đặc tả [PROPOSAL] | Tính năng |
|---|---|---|
| Mô hình cấu hình | Desired (cloud) / reported (edge), có version; tài liệu ký số; edge từ chối config không ký | F-INT-11 |
| Nội dung config | Bảng `pid` ↔ (device, code); driver + phiên bản; lớp tần suất; SOE đang hiệu lực; chiến lược mặc định; danh sách `kid` tin cậy; `control_owner`; tham số IEC 104/OCPP | [05 §6](05-domain-model.html#s6) `EdgeConfigVersion` |
| Áp config | Kiểm chữ ký → kiểm tương thích (driver có trong ảnh firmware, bus đủ ngân sách) → áp nguyên tử → báo `APPLIED`/`REJECTED` kèm lý do | — |
| OTA edge | A/B ký số, rollback tự động nếu không lên `NORMAL` trong thời gian chờ, anti-rollback, canary 1% → 10% → 100%; hạng lệnh C3 | F-INT-12 |
| Driver | Driver mới đi kèm firmware hoặc gói driver ký số riêng; không tải code tùy ý | — |
| Firmware thiết bị của hãng | **Không** cập nhật từ nền tảng; installer làm bằng công cụ hãng | F-INT-12; rủi ro brick |
| Hỗ trợ từ xa | Reverse tunnel theo yêu cầu, chủ site cho phép, ≤ 2 h, ghi phiên (P1) | F-SEC-20 |

### 6.14 Danh tính gateway và mTLS

Tóm tắt từ I §3.5; chi tiết ở [10](10-security-and-reliability.md).

| Hạng mục | Đặc tả [PROPOSAL] |
|---|---|
| Khóa | Sinh trong TPM 2.0/secure element, không xuất được; nếu phần cứng thiếu TPM thì khóa trong file mã hóa là ngoại lệ tạm thời có ghi rủi ro (K §3.8) |
| Chứng chỉ | X.509 riêng mỗi edge do CA thiết bị của ta ký; Subject `CN=edge-<uuid>`, SAN `urn:ems:edge:<uuid>`; **không** nhúng tenant/site |
| Provisioning | Cert "birth" của xưởng chỉ gọi được `enroll` → installer claim bằng QR (F-INT-02) → cloud cấp cert vận hành hạn 90 ngày, tự gia hạn ở 2/3 hạn |
| Thu hồi | Danh sách chặn tại broker + hạn ngắn |
| Kênh | TLS 1.3 (cho phép 1.2 AEAD), mTLS, cổng 8883 hoặc 443 (WebSocket); outbound-only |
| ACL broker | Edge chỉ publish `ems/v1/{edge_id}/up/#`, chỉ subscribe `ems/v1/{edge_id}/down/#`; cấm wildcard |
| Mật khẩu | Không có mật khẩu mặc định chung; HMI cục bộ dùng mật khẩu ngẫu nhiên theo thiết bị, đổi lần đầu |

### 6.15 Phần cứng tham chiếu

Đáp ứng một phần K G-06; **chưa chọn ứng viên và chưa có giá BOM** ([UNKNOWN], Q-E-15).

| Hạng mục | Yêu cầu [PROPOSAL] | Căn cứ |
|---|---|---|
| Cổng trường | 2 × RS485 cách ly; 1 × CAN; 4 DI / 4 DO | [FACT, High] SolarEdge ONE Controller C&I có 2 × RS485, CAN, 2 × RJ45, 4DI/4DO, Modbus TCP cổng 1502 — https://knowledge-center.solaredge.com/sites/kc/files/se-one-controller-commercial-and-industrial-datasheet-eng.pdf (qua kết quả tìm kiếm; B L34). Dùng làm tham chiếu cấu hình, không phải lựa chọn |
| Mạng | 2 × Ethernet (WAN và OT LAN tách, không định tuyến giữa hai phía); 4G tùy chọn | I §3.6 |
| Lưu trữ | SSD/eMMC công nghiệp ≥ 32 GB (≥ 64 GB site lớn), chọn theo TBW | §6.7 |
| Thời gian | RTC có pin; GNSS tùy chọn | §6.8 |
| An toàn | Watchdog phần cứng; TPM 2.0/secure element | §6.6, §6.14 |
| Thao tác tại chỗ | Nút nhấn vật lý nối GPIO/DI cục bộ (xác nhận có mặt cho phiên `COMMISSIONING_TEST`); khuyến nghị LED hoặc màn hình nhỏ hiển thị mã | §9.4 |
| Môi trường | Nhiệt độ công nghiệp, gắn DIN rail | [INFERENCE] tủ điện C&I |
| CPU/RAM | [UNKNOWN] tới khi PoC runtime (§6.1) đo tải với 5.000 điểm, IEC 104 và OCPP cùng chạy | — |

### 6.16 Telemetry sức khỏe edge

Các điểm `edge.*` gửi lớp C2 (và trong `up/state`): `edge.clock_state`, `edge.clock_offset_ms`, `edge.buffer_fill_pct`, `edge.buffer_oldest_ts`, `edge.uplink_state`, `edge.cycle_time_ms` (p50/p99), `edge.poll_cycle_ms` theo bus, `edge.bus_error_count`, `edge.cpu_pct`, `edge.mem_pct`, `edge.disk_free_pct`, `edge.storage_wear_pct` (nếu ổ cho đọc), `edge.temp_c`, `edge.run_mode`, `edge.local_remote_state`. Hiển thị ở F-MON-07.

---

## 7. Hợp đồng telemetry chuẩn

### 7.1 Không gian tên topic

Theo K R-12 (thay mẫu có tenant/site trong ghi chú E §3.5). Ánh xạ edge → site/tenant nằm ở registry cloud.

| Topic | Hướng | QoS | Retained | Message Expiry | Nội dung |
|---|---|---|---|---|---|
| `ems/v1/{edge_id}/up/state` | edge → cloud | 1 | **Có** (LWT = `{"online": false}`) | — | Trạng thái edge, config/firmware version, lệnh đang hiệu lực (§6.12) |
| `ems/v1/{edge_id}/up/telemetry/{stream}` | edge → cloud | 1 | Không | — | Lô điểm; `stream ∈ {c1, c2, c3, c4}` |
| `ems/v1/{edge_id}/up/event` | edge → cloud | 1 | Không | — | Alarm/SOE, đổi chế độ, interlock, `CAPABILITY_DISCOVERED`, `ARBITER_REASON`, `DATA_LOSS` |
| `ems/v1/{edge_id}/up/backfill` | edge → cloud | 1 | Không | — | Dữ liệu tồn đọng sau mất kết nối; cùng định dạng với telemetry |
| `ems/v1/{edge_id}/up/cmd-ack` | edge → cloud | 1 | Không | — | Chuyển trạng thái lệnh, ký bằng khóa edge |
| `ems/v1/{edge_id}/down/cmd` | cloud → edge | 1 | **Không** (tránh lệnh cũ chạy lại khi reconnect) | `expires_at − now` | Envelope lệnh có chữ ký (§8) |
| `ems/v1/{edge_id}/down/config` | cloud → edge | 1 | Có (bản desired mới nhất) | — | Config ký số; yêu cầu gửi lại (`RESEND_REQUEST`); ack lô telemetry |

Ack lô telemetry: cloud gửi `{"type":"TELEMETRY_ACK","stream":"c2","ack_seq":184467}` trên `down/config` (không retained) hoặc gộp trong session; edge xóa mọi `seq ≤ ack_seq` của stream đó. [PROPOSAL] — người viết 06 có thể chọn kênh ack riêng `down/ack` nếu muốn tách; khi đó phải sửa R-12 qua ADR.

MQTT 5 user properties bắt buộc: `schema` (ví dụ `ems.telemetry.v1`), `content-type` (`application/x-protobuf+zstd` hoặc `application/json` khi debug), `edge_seq`.

### 7.2 Mã điểm, đơn vị, dấu

**Mã điểm** theo từ điển `PointDefinition` của [05 §7](05-domain-model.html#s7): `<class>.<quantity>[.<qualifier>]`, chữ thường, ổn định qua phiên bản. Ví dụ `meter.p`, `meter.p.l1`, `meter.e_import`, `pv_inverter.p`, `ess.soc`, `edge.clock_offset_ms`.

[PROPOSAL] Giải quyết yêu cầu "tên kiểu `inv.active_power`": mã điểm dùng **dạng ngắn** để thống nhất với 05; từ điển giữ thêm trường `quantity_name` dạng dài cho tài liệu và API công khai.

| `quantity` (mã) | `quantity_name` | `unit_raw` | Ghi chú dấu |
|---|---|---|---|
| `p` | active_power | W | Theo §7.2 bảng dấu |
| `q` | reactive_power | var | Cùng hướng với P của điểm (K R-02) |
| `s` | apparent_power | VA | ≥ 0 |
| `pf` | power_factor | (không đơn vị) | Tính lại từ kWh/kvarh ở cloud cho POC (F-GRID-11) |
| `u`, `i`, `f` | voltage, current, frequency | V, A, Hz | — |
| `e_import`, `e_export` | energy_import, energy_export | Wh (int64) | Cặp không âm |
| `e_charge`, `e_discharge` | energy_charge, energy_discharge | Wh (int64) | Cặp không âm |
| `e_total` | energy_total_generated | Wh (int64) | PV |
| `soc`, `soh` | state_of_charge, state_of_health | % | Giá trị BMS công bố |
| `p_charge_max`, `p_discharge_max` | allowed_charge_power, allowed_discharge_power | W | ≥ 0; từ CCL/DCL × U hoặc PCS |
| `g_poa`, `ghi` | irradiance_poa, irradiance_global_horizontal | W/m² | — |
| `t_module`, `t_ambient` | temperature_module, temperature_ambient | °C | — |

Hậu tố đơn vị trong tên trường (K R-03) áp cho **trường có kiểu cố định** (ví dụ `export_limit_w`, `clock_offset_ms`, tham số lệnh `p_w`). Giá trị điểm trong lô dùng trường chung `v`, đơn vị là `unit_raw` của mã điểm (quy ước của [05 §2.6](05-domain-model.html#s2-6)).

**Quy ước dấu (chuẩn hóa tại edge, K R-01/R-02)**

| Điểm | P > 0 | P < 0 | Q > 0 |
|---|---|---|---|
| `meter.*` tại `MTR_POC` (lưới) | Nhập từ lưới | Xuất lên lưới | Vô công đi vào site từ lưới (tải cảm, góc phần tư Q1) |
| `ess.p`, `pcs.p` | Xả | Sạc | Bơm vào thanh cái site |
| `pv_inverter.p` | Phát (≥ 0; âm nhỏ ban đêm giữ nguyên) | — | Bơm vào thanh cái site |
| `meter.p` tại `MTR_LOAD_i`, `MTR_EV_i`, `evse.p` | Tiêu thụ (≥ 0) | (V2G sau này) | Theo hướng P |
| `genset.p` | Phát (≥ 0) | — | Bơm vào thanh cái site |

UI hiển thị số không dấu kèm chữ hướng (Nhập/Xuất/Sạc/Xả/Chờ); trạng thái sạc/xả lấy từ PCS/BMS, không suy từ dấu (K §6 #4).

**Bộ điểm tối thiểu theo lớp (MVP)**

| Lớp | Điểm bắt buộc |
|---|---|
| `meter` tại `MTR_POC` | `p`, `q`, `s`, `pf`, `u.l1`–`u.l3`, `i.l1`–`i.l3`, `f`, `e_import`, `e_export`, `eq_import_q1`…`q4` (nếu công tơ có) |
| `pv_inverter` | `p`, `q`, `e_total`, `state`, `p_limit_pct` (đọc lại), `dc.p` (nếu có), `alarm_word` |
| `ess` (logic) | `p`, `soc`, `soh`, `p_charge_max`, `p_discharge_max`, `e_charge`, `e_discharge`, `mode`, `state`, `cell_v_min`/`cell_v_max`, `cell_t_min`/`cell_t_max` |
| `evse` / `ev_connector` (P1) | `p`, `i_limit_active`, `state` (trạng thái OCPP), `e_session`, `session_id` |
| `weather` | `g_poa` (nếu có), `ghi`, `t_module`, `t_ambient` |
| `relay` | `local_remote`, `estop_active`, `fire_alarm`, `reverse_power_relay`, `poc_breaker` (theo §4.3) |
| `site` (edge tính) | `p_load`, `p_export_limit_active`, `p_import_limit_active`, `control_mode`, `arbiter_level_active` |
| `edge` | §6.16 |

### 7.3 Payload

**Định dạng trên dây [PROPOSAL]:** Protobuf, gộp lô, nén zstd; mục tiêu ≤ 15 B/mẫu (FR-INT-008). JSON là **biểu diễn logic** dùng cho tài liệu, debug (`content-type: application/json`) và test hợp đồng. Hai biểu diễn ánh xạ một-một.

**Ví dụ lô C2 (JSON logic)**

```json
{
  "schema": "ems.telemetry.v1",
  "edge_id": "edge-0f3e9c2a",
  "stream": "c2",
  "seq": 184467,
  "batch_ts": 1791612060123,
  "config_version": 42,
  "points": [
    {"pid": 2001, "ts": 1791612000000, "w": 60, "avg": 412350.0, "min": 401200.0, "max": 420010.0, "last": 415800.0, "n": 60, "q": "GOOD"},
    {"pid": 2002, "ts": 1791612000000, "w": 60, "avg": -35120.0, "min": -40100.0, "max": -30050.0, "last": -36000.0, "n": 58, "q": "GOOD", "cov_ms": 58000},
    {"pid": 2050, "ts": 1791612000000, "w": 60, "q": "BAD_COMM"}
  ]
}
```

- `ts`: đầu cửa sổ nguồn (UTC, ms); khoảng `[ts, ts + w)` (K R-05). `w` tính bằng giây (5, 60, 300).
- `avg/min/max/last/n`: tổng hợp tại nguồn; `cov_ms` khi cửa sổ không đủ mẫu.
- Điểm `BAD_*` không có giá trị, **không** gửi 0.

**Ví dụ lô thanh ghi C4**

```json
{
  "schema": "ems.telemetry.v1",
  "edge_id": "edge-0f3e9c2a",
  "stream": "c4",
  "seq": 99120,
  "batch_ts": 1791612302001,
  "points": [
    {"pid": 1010, "ts": 1791612300412, "raw": 1284419375, "q": "GOOD", "boundary": true},
    {"pid": 1011, "ts": 1791612300412, "raw": 88213004, "q": "GOOD", "boundary": true}
  ]
}
```

`raw` là int64 theo `unit_raw` (Wh) sau scale; `boundary = true` khi đây là lần đọc ngay sau biên 5 phút.

**Ví dụ sự kiện**

```json
{
  "schema": "ems.event.v1",
  "edge_id": "edge-0f3e9c2a",
  "seq": 5512,
  "events": [
    {"event_id": "01HZX…", "type": "DEVICE_ALARM", "device_id": "dev-pcs-01",
     "ts": 1791612301120, "ts_src": 1791612300980, "src_clock_state": "SYNCED",
     "code_raw": "0x2104", "state": "RAISED", "q": "GOOD"},
    {"event_id": "01HZY…", "type": "INTERLOCK", "ts": 1791612302000,
     "interlock": "IL-04", "state": "ACTIVE", "detail": {"point": "meter.p", "age_ms": 3400}}
  ]
}
```

**JSON Schema rút gọn cho một mẫu gauge (tham chiếu cho test hợp đồng)**

```json
{
  "$id": "ems.telemetry.v1#/gaugeSample",
  "type": "object",
  "required": ["pid", "ts", "w", "q"],
  "properties": {
    "pid":  {"type": "integer", "minimum": 1},
    "ts":   {"type": "integer", "description": "UTC epoch ms, đầu cửa sổ"},
    "w":    {"enum": [1, 5, 60, 300]},
    "avg":  {"type": "number"}, "min": {"type": "number"},
    "max":  {"type": "number"}, "last": {"type": "number"},
    "n":    {"type": "integer", "minimum": 0},
    "cov_ms": {"type": "integer", "minimum": 0},
    "ts_src": {"type": "integer"},
    "q":    {"enum": ["GOOD", "GOOD_LOCAL_OVERRIDE", "UNCERTAIN_STALE", "UNCERTAIN_CLOCK",
                      "UNCERTAIN_OUT_OF_RANGE", "UNCERTAIN_SUBSTITUTED", "UNCERTAIN_VENDOR_CLOUD",
                      "BAD_COMM", "BAD_CONFIG", "BAD_DEVICE", "BAD_NOT_SUPPORTED"]}
  },
  "allOf": [
    {"if": {"properties": {"q": {"pattern": "^BAD_"}}},
     "then": {"not": {"anyOf": [{"required": ["avg"]}, {"required": ["last"]}]}}}
  ]
}
```

`w = 1` chỉ dùng cho burst mode (F-MON-12, P1).

### 7.4 Thời gian

| Trường | Định nghĩa | Dùng làm thời gian chuẩn khi |
|---|---|---|
| `ts` | Thời điểm edge thu giá trị (hoặc đầu cửa sổ tổng hợp), UTC, ms | Mặc định cho dữ liệu polling |
| `ts_src` | Thời điểm thiết bị cung cấp (tùy chọn), đã chuẩn hóa UTC; kèm `src_clock_state` | Chỉ SOE/alarm và dữ liệu khoảng của công tơ khi `src_clock_state = SYNCED` |
| `ts_ingest` | Thời điểm cloud ghi (cloud gán, không có trên dây) | Đo độ trễ (NFR-PERF-003), phát hiện backfill |

Nguồn: K R-04. Ngày/TOU/kỳ hóa đơn tính theo `Site.timezone` (IANA) ở cloud, không ở edge (K §6 #7).

---

## 8. Hợp đồng lệnh chuẩn

### 8.1 Kiểu lệnh

Tên lệnh giữ theo ghi chú E (K R-27). Cột "Tên tương đương" ánh xạ các tên chung chung thường gặp.

| Type | Tên tương đương | Đích | Tham số | Kiểm tra tại edge | `on_expiry` mặc định | Hạng | Gate | Tính năng |
|---|---|---|---|---|---|---|---|---|
| `SET_ESS_P` | set_active_power_setpoint (BESS) | `ess` | `p_w` (+ xả, − sạc) | Kẹp vào `[−p_charge_max, p_discharge_max]` **hiện tại**, SOE, SOC min/max, giới hạn POC; `requires_native_fallback = false` | `REVERT_DEFAULT` (P = 0 hoặc chiến lược mặc định) | C1 (C2 nếu > 80% SOE) | M2 | F-BESS-06 |
| `SET_ESS_MODE` | set_operating_mode | `ess` / site | `site_strategy ∈ {SELF_CONSUMPTION, PEAK_SHAVING, TOU_SCHEDULE, BACKUP_HOLD, IDLE}` | Mode có trong `capability_profile`; `mode_change_min_interval` 300 s | Chiến lược mặc định | C1 | M1 | F-BESS-05 |
| `SET_SOC_RESERVE` | set_soc_limits (phần cấu hình được) | `ess` | `soc_reserve_pct` | ≥ SOC min hiệu dụng của SOE; tăng = C1, giảm = C2 | Giá trị cấu hình | C1/C2 | M1 | F-BESS-07 |
| — | set_soc_limits (SOC min/max hiệu dụng) | SOE | — | **Không phải lệnh**: thay đổi SOE là quy trình C3 hai người (F-BESS-08); giới hạn của BMS là C4 (không có API) | — | C3/C4 | M2 | F-BESS-08, F-BESS-19 |
| `SET_EXPORT_LIMIT` | set_export_limit | site (POC) | `export_limit_w` | ≥ 0; ≤ giới hạn trong cấu hình lưới (F-GRID-03) | Về `export_limit_w` của cấu hình site | C2 | M1 (native) / M2 (edge) | F-GRID-04, F-GRID-05 |
| `SET_IMPORT_LIMIT` | set_import_cap | site | `import_cap_w` | ≥ tải tối thiểu không cắt được (cấu hình) | Về `import_cap_w` của cấu hình | C2 | M1/M2 | F-GRID-06 |
| `SET_PV_LIMIT` | set_active_power_setpoint (PV) | `pv_inverter` / nhóm / logger | `p_limit_pct` hoặc `p_limit_w` | 0–100%; `min_write_interval_ms` | 100% nếu site cho xuất, ngược lại giới hạn native | C1 | M1 | F-PV-03 |
| `SET_Q` / `SET_PF` | set_reactive_power | `pv_inverter` / `pcs` | `q_var` / `pf` | **Khóa ở MVP** (grid code) | Giá trị native | C2 | M2 | F-PV-13 (P2) |
| `SET_EV_LIMIT` | set_charging_limit | `evse` / `ev_connector` | `i_max_a` hoặc `p_max_w`, `phases` | ≥ `I_min` (mặc định 6 A, [INFERENCE] mức phổ biến của IEC 61851) hoặc 0 để tạm dừng | TxDefaultProfile an toàn | C1 | M2 | F-EV-05 (P1) |
| `APPLY_SCHEDULE` | apply_schedule | site / `ess` | `plan_id`, `plan_version`, `slot_minutes` = 15, `slots[]` theo `PlanSlot` của 05 (`slot_start`, `slot_mode`, `p_ess_min_w`, `p_ess_max_w`, `p_grid_target_w`, `soc_target_pct`, `import_cap_w`, `export_limit_w`, `ev_limit_w`, `reason_codes`); horizon ≥ 48 h (§8.3) | Mỗi slot kiểm như lệnh đơn; có version; F-OPT-07 | Hết lịch → chiến lược mặc định | C1 | M1 (tham số native) / M2 | F-OPT-04, F-OPT-05 |
| `SET_REVERSE_FEED_BLOCK` | — | site | `blocked: bool` | Chỉ từ `GRID_OPERATOR` hoặc thủ công C3 | Theo điều độ [UNKNOWN] | C3 (thủ công) | M2 | F-GRID-12 (P1) |
| `DEVICE_ON_OFF` | start / stop | thiết bị (PCS) | `on: bool` | Hai người duyệt; không được nằm trong lịch tự động; tên UI "Dừng vận hành từ xa", **không phải E-stop** | Không tự đảo | C3 | M2 | F-BESS-16 (P1) |
| `REMOTE_CONTROL_SUSPEND` / `RESUME` | kill switch | site / tenant / nền tảng | — | Tắt = C1, bật lại = C3 | — | C1/C3 | M2 | F-SEC-11 |
| `REVERT` | cancel / revert | site / thiết bị | `command_id` cần hủy (hoặc `all_active: true`) | Chỉ hoàn nguyên về giá trị mặc định đã cấu hình; thuộc đường an toàn hóa (§8.7 B) | — (chính nó là hoàn nguyên) | C1 | M1/M2 | F-SEC-11 |
| `CONFIG_PUSH`, `FW_UPDATE_EDGE` | — | edge | Tài liệu/ảnh ký số | Kiểm chữ ký, tương thích | Rollback | C1/C3 | M1 | F-INT-11, F-INT-12 |
| `COMMISSIONING_TEST` | test command | thiết bị | Bước test (§9.4) | Chỉ khi site `commissioning` và edge ở trạng thái con `MAINTENANCE/COMMISSIONING_TEST` có xác nhận có mặt (§9.4); biên độ trong "phong bì test" | `REVERT_DEFAULT` | C2 | — | F-INT-26–28 |

Không có kiểu lệnh nào ghi ngưỡng bảo vệ BMS, grid code PCS, cài đặt rơ-le, reset E-stop (C4, F-BESS-19, F-BESS-20).

#### 8.1.1 Thuộc tính `persist_safe` cho lệnh ghi Gate M1 [PROPOSAL]

Vấn đề: ở Gate M1, lệnh ghi tham số native (`SET_ESS_MODE`, `SET_SOC_RESERVE`, `SET_PV_LIMIT`, `SET_EXPORT_LIMIT`/`SET_IMPORT_LIMIT` tạm thời, `APPLY_SCHEDULE` tham số native) chỉ được hoàn nguyên khi **edge còn sống** thực hiện `on_expiry`. Ràng buộc `requires_native_fallback` và test watchdog F-INT-28 chỉ áp ở M2. Nếu edge mất nguồn trong lúc lệnh tạm thời còn hiệu lực, giá trị đã ghi ở lại trên thiết bị vô thời hạn.

Quy tắc: một lệnh ghi M1 chỉ được phép khi thỏa **ít nhất một** điều kiện:
- (a) **Hoàn nguyên phía thiết bị đã kiểm chứng**: driver khai báo `watchdog_support` cho đúng tham số đó và test mất nguồn edge (T-FR-INT-018b, §11.3) đã đạt trong commissioning; `revert_timeout_s` ≤ thời gian còn lại tới `expires_at`; hoặc
- (b) **`persist_safe(type, value) = true`**: giá trị ghi an toàn nếu tồn tại vô thời hạn, theo bảng dưới.

Không thỏa → PDP từ chối (`DENIED: NOT_PERSIST_SAFE`) **và** edge từ chối độc lập (`REJECTED_UNSUPPORTED`, bước 10 §8.7) — lớp sau không tin lớp trước (BR-SEC-05). Bảng `persist_safe` nằm trong config đã ký của edge, có version.

| Type | `persist_safe = true` khi | Không persist_safe (cần (a)) | Lý do |
|---|---|---|---|
| `SET_EXPORT_LIMIT` | `export_limit_w` mới ≤ `export_limit_w` của cấu hình site (chặt hơn) | Nới giới hạn xuất | Chặt hơn chỉ giảm xuất; nới tồn tại vô hạn có thể vi phạm cam kết đấu nối |
| `SET_IMPORT_LIMIT` | `import_cap_w` mới ≤ cấu hình site và ≥ tải tối thiểu không cắt được | Nới trần nhập | Như trên, theo chiều nhập |
| `SET_SOC_RESERVE` | `soc_reserve_pct` mới ≥ giá trị cấu hình (tăng dự phòng) | Giảm dự phòng | Dự phòng cao hơn chỉ giảm dải khai thác |
| `SET_ESS_MODE` | `site_strategy` mới = chiến lược mặc định đã cấu hình của site | Mọi chế độ khác (`BACKUP_HOLD`, `IDLE`, `PEAK_SHAVING`…) | Chế độ lệch mặc định tồn tại vô hạn làm site vận hành sai ý chủ tài sản (mất tiết kiệm, giữ pin đầy/rỗng) |
| `SET_PV_LIMIT` | Giá trị mới = giá trị mặc định cấu hình (thường 100% nếu được xuất, hoặc giới hạn native) | Hạ giới hạn PV tạm thời | Hạ PV vô hạn gây mất sản lượng không ai thấy |
| `APPLY_SCHEDULE` (tham số native, ví dụ lịch TOU trên logger) | Lịch là **cấu hình nền** đã duyệt (trở thành giá trị hoàn nguyên của site, lưu trong config version) | Lịch tạm/override ngắn hạn | Lịch nền lặp theo ngày là cấu hình, không phải lệnh tạm |
| Thay đổi cấu hình nền (mọi type) | Giá trị ghi = giá trị hoàn nguyên mới, đã ghi vào cấu hình site (C2, readback) | — | Hoàn nguyên về chính nó nên không có rủi ro "treo" |

Ghi chú: (b) không thay test hoàn nguyên ở M2; ở M2 vẫn áp `requires_native_fallback` (§6.4). Lệnh an toàn hóa (§8.7) luôn persist_safe theo định nghĩa (chỉ thu hẹp vận hành).

### 8.2 Envelope lệnh

Envelope = trường của ghi chú E §3.19 + trường của I (X-I-02), theo K §6 #21. Tên đối tượng lưu trữ ở cloud là `DispatchCommand` ([05 §11.2](05-domain-model.html#s11-sm1)).

| Trường | Bắt buộc | Ý nghĩa |
|---|---|---|
| `command_id` | Có | UUID v7. **Là idempotency key ở edge**: nhận trùng thì trả lại trạng thái cũ, không thực thi lại. Edge giữ bảng đã thấy tới `expires_at + 24 h` |
| `idempotency_key` | Ở API cloud | Header `Idempotency-Key` của POST tới Command API; cloud ánh xạ về một `command_id` duy nhất. Không truyền xuống edge |
| `seq` | Có | Đơn điệu theo `(site, signer)`; chống replay kể cả khi broker bị chiếm |
| `type`, `params` | Có | §8.1; tham số có hậu tố đơn vị |
| `target` | Có | `edge_id`, `site_id`, `asset_id` hoặc nhóm; edge kiểm `target.edge_id` = chính nó |
| `source` | Có | `GRID_OPERATOR` / `OPERATOR` / `SCHEDULE` / `OPTIMIZER` / `DR` / `API` / `COMMISSIONING` → mức arbiter (§3.2). **Không có trường `priority` tự do**: ưu tiên suy ra từ `source`, tránh client tự nâng ưu tiên |
| `limits` | Không | Giới hạn bổ sung chặt hơn SOE (ví dụ `ramp_w_per_s`, `p_max_w`); edge lấy giá trị chặt nhất |
| `danger_class` | Có | `C0`…`C3` (C4 không tồn tại) |
| `issued_by` | Có | user/service id |
| `approved_by` / `approval_ref` | Có với C3 | Tham chiếu `CommandApproval` (người duyệt khác người, khác vai trò) |
| `reason` | Có với C2/C3 | Lý do bắt buộc |
| `correlation_id` | Không | Liên kết kế hoạch/sự kiện DR/ticket |
| `valid_from`, `expires_at` | Có | Edge từ chối lệnh không có hạn. Setpoint: mặc định 15 phút, tối đa 1 h; đổi chế độ: tối đa 24 h; lịch: tối đa 7 ngày; C3: ≤ 30 phút sau duyệt |
| `sent_at` | Có | Thời điểm dispatcher ký và gửi (UTC, ms), nằm trong phần được ký; dùng cho `max_latency_ms` |
| `max_latency_ms` | Có | Đến edge muộn hơn → `REJECTED_STALE`. Setpoint 10.000; chế độ 30.000; lịch 300.000 |
| `on_expiry` | Có | `REVERT_DEFAULT` (mặc định) / `HOLD_LAST` (chỉ cho type được SOE cho phép) |
| `supersedes` | Không | `command_id` bị thay |
| `tolerance` | Không | Ghi đè dung sai readback mặc định (§8.5) |
| `dry_run` | Không | Chỉ kiểm tra, không ghi; trả `ACCEPTED` hoặc `REJECTED_*` rồi `COMPLETED` |
| `kid`, `signature` | Có | JWS (ES256 hoặc EdDSA) của Command Signer trên envelope chuẩn hóa. Phương pháp chuẩn hóa JSON đề xuất JCS (RFC 8785) [PROPOSAL; người viết 10 chốt] |

### 8.3 Ví dụ JSON

**Setpoint BESS thủ công**

```json
{
  "schema": "ems.command.v1",
  "command_id": "0192f3a4-6c1e-7b8a-9d10-3f2a1b4c5d6e",
  "seq": 30411,
  "type": "SET_ESS_P",
  "target": {"edge_id": "edge-0f3e9c2a", "site_id": "7a1c…", "asset_id": "ess-01"},
  "params": {"p_w": 150000},
  "limits": {"ramp_w_per_s": 25000},
  "source": "OPERATOR",
  "danger_class": "C1",
  "issued_by": "user:5d1…",
  "reason": "Thử xả trước giờ cao điểm",
  "valid_from": "2026-10-10T09:00:00.000Z",
  "expires_at": "2026-10-10T09:15:00.000Z",
  "sent_at": "2026-10-10T09:00:01.120Z",
  "max_latency_ms": 10000,
  "on_expiry": "REVERT_DEFAULT",
  "tolerance": {"abs_w": 5000, "rel": 0.02, "readback_timeout_s": 10},
  "dry_run": false,
  "kid": "cmd-signer-2026-03",
  "signature": "eyJhbGciOiJFUzI1NiIsImtpZCI6…"
}
```

**Lịch (APPLY_SCHEDULE) với slot theo G X-G02**

```json
{
  "schema": "ems.command.v1",
  "command_id": "0192f3a5-0000-7c11-8e22-aa01bb02cc03",
  "seq": 30412,
  "type": "APPLY_SCHEDULE",
  "target": {"edge_id": "edge-0f3e9c2a", "site_id": "7a1c…", "asset_id": "ess-01"},
  "source": "SCHEDULE",
  "danger_class": "C1",
  "issued_by": "svc:scheduler-tier2",
  "correlation_id": "plan:7a1c…:v118",
  "valid_from": "2026-10-10T17:00:00.000Z",
  "expires_at": "2026-10-13T17:00:00.000Z",
  "sent_at": "2026-10-10T16:55:00.000Z",
  "max_latency_ms": 300000,
  "on_expiry": "REVERT_DEFAULT",
  "params": {
    "plan_id": "plan-7a1c-118",
    "plan_version": 118,
    "slot_minutes": 15,
    "slots": [
      {"slot_start": "2026-10-10T17:00:00Z", "slot_mode": "GRID_CHARGE_TO_TARGET",
       "p_ess_min_w": -300000, "p_ess_max_w": 0, "soc_target_pct": 40.0,
       "import_cap_w": 900000, "export_limit_w": 0,
       "reason_codes": ["TOU_OFFPEAK_CHARGE"]},
      {"slot_start": "2026-10-11T10:30:00Z", "slot_mode": "PEAK_DISCHARGE",
       "p_ess_min_w": 0, "p_ess_max_w": 400000, "p_grid_target_w": 600000,
       "soc_target_pct": 30.0, "import_cap_w": 900000, "export_limit_w": 0,
       "reason_codes": ["TOU_PEAK_DISCHARGE"]}
    ]
  },
  "kid": "cmd-signer-2026-03",
  "signature": "…"
}
```

Tên trường slot là hợp đồng dây cloud↔edge và **phải trùng đúng** `PlanSlot` của [05 §e-plan](05-domain-model.html#e-plan): `slot_start`, `slot_mode`, `p_ess_min_w`, `p_ess_max_w` (dấu BESS + = xả), `p_grid_target_w` (+ = nhập), `soc_target_pct`, `soc_floor_pct` (tùy chọn), `soc_ceiling_pct` (tùy chọn), `import_cap_w`, `export_limit_w`, `ev_limit_w` (tùy chọn), `reason_codes`. Các trường dự báo của `PlanSlot` (`expected_*`) không truyền xuống edge. Edge từ chối (`REJECTED_INVALID`) slot có trường lạ hoặc thiếu trường bắt buộc theo `slot_mode`. Sàn/trần SOC theo slot (`soc_floor_pct`, `soc_ceiling_pct`) chỉ được **siết** thêm: edge dùng `max(soc_floor_pct, SOE.soc_min, dự phòng backup)` và `min(soc_ceiling_pct, SOE.soc_max)`; không bao giờ nới SOE (05 §11.5, X-07-08 đã đóng). Mã `reason_codes` trong ví dụ là minh họa; danh mục chuẩn thuộc [08](08-energy-optimization.md).

`slot_mode ∈ {PV_SURPLUS_CHARGE, GRID_CHARGE_TO_TARGET, PEAK_DISCHARGE, GRID_SETPOINT, HOLD, IDLE}` chỉ xuất hiện trong `APPLY_SCHEDULE`; `site_strategy` chỉ trong `SET_ESS_MODE` (K R-15). Giờ trong ví dụ là UTC: 10:30Z = 17:30 giờ Việt Nam (đầu cao điểm theo QĐ 963, K §6 #37).

**Ack**

```json
{
  "schema": "ems.cmd-ack.v1",
  "edge_id": "edge-0f3e9c2a",
  "command_id": "0192f3a4-6c1e-7b8a-9d10-3f2a1b4c5d6e",
  "state": "APPLIED_CLAMPED",
  "ts": 1791622806250,
  "arbiter_level": 7,
  "requested": {"p_w": 150000},
  "effective_setpoint": {"p_w": 120000},
  "clamp": {"code": "CLAMPED_BY_BMS", "limit_w": 120000, "source_point": "ess.p_discharge_max"},
  "readback": {"point": "pcs.p_setpoint", "value": 120000, "ts": 1791622806100},
  "measured": {"point": "ess.p", "value": 118400, "ts": 1791622806000},
  "edge_sig": {"kid": "edge-0f3e9c2a-2026-08", "jws": "…"}
}
```

Ack theo slot cho `APPLY_SCHEDULE`: `{"type":"SLOT","plan_version":118,"slot_start":"…","state":"SLOT_STARTED | SLOT_APPLIED | SLOT_OVERRIDDEN | SLOT_ENDED","override_level":4}` (G X-G02), làm đầu vào cho `plan_slot_result` (F-OPT-10).

### 8.4 Vòng đời lệnh

Tên trạng thái chuẩn theo [05 §11.2](05-domain-model.html#s11-sm1). Bảng dưới ánh xạ vòng đời chung "created → validated → sent → delivered → accepted/rejected → applied/failed → expired/cancelled" sang trạng thái chuẩn.

| Vòng đời chung | Trạng thái chuẩn | Ai ghi | Điều kiện |
|---|---|---|---|
| created | `CREATED` | Command API | Lưu envelope chưa ký |
| (chờ duyệt) | `PENDING_APPROVAL` → `APPROVAL_REJECTED` / `APPROVAL_EXPIRED` | PDP / người duyệt | Hạng C3 |
| validated | `AUTHORIZED` (hoặc `DENIED`) | PDP | Quyền, MFA/step-up, SOE, Fleet Dispatch Governor, kill switch, `control_enabled` |
| sent | `SENT` | Signer + dispatcher | Ký JWS, gán `seq`, publish QoS 1 không retained, Message Expiry |
| (không tới) | `UNDELIVERED` | Cloud | Không có `RECEIVED` trước `expires_at`; **không gửi lại** |
| delivered | `RECEIVED` | Edge (ack ký) | Edge nhận, ghi bảng `command_id` |
| rejected | `REJECTED_{STALE, INVALID, UNSUPPORTED, OUT_OF_LIMIT, LOWER_PRIORITY, INTERLOCK:<IL-xx>, REPLAY}` | Edge | Kết thúc; `REPLAY`/`INVALID` sinh cảnh báo bảo mật |
| accepted | `ACCEPTED` → `DISPATCHED` | Edge | Kiểm §8.7 đạt; đã ghi xuống thiết bị/controller |
| applied | `APPLIED` / `APPLIED_CLAMPED` | Edge | Readback trong dung sai (§8.5) |
| failed | `FAILED_{DEVICE_EXCEPTION, NO_EFFECT, TIMEOUT}` | Edge | Readback không khớp trong timeout |
| expired / cancelled | `EXPIRED` → `COMPLETED`; `SUPERSEDED`; `CANCELLED` | Edge / cloud | Hết hạn → thực hiện `on_expiry`, `COMPLETED` khi hoàn nguyên xong |

UI chỉ hiển thị "đã áp dụng" sau `APPLIED`/`APPLIED_CLAMPED` (H X-H04, F-SEC-14).

### 8.5 Kiểm chứng thực tế so với yêu cầu

Hai kiểm tra tách biệt [PROPOSAL]:
1. **Readback setpoint** (quyết định `APPLIED`): đọc lại thanh ghi setpoint/chế độ (`readback_ref`) sau khi ghi; khớp trong dung sai trước `readback_timeout_s`.
2. **Theo dõi đáp ứng vật lý** (không đổi trạng thái lệnh): so đại lượng đo với setpoint hiệu lực trong suốt thời gian lệnh; lệch kéo dài → `tracking_state = DEVIATING` và cảnh báo `CTRL.TRACKING_DEVIATION` có nguyên nhân (`DEVICE_CLAMP`, `HIGHER_PRIORITY_OVERRIDE`, `NATIVE_MODE`, `UNKNOWN`). Đây là bằng chứng cho `deviation_cause` của kế hoạch (G §3.10).

| Type | Readback (APPLIED) | Dung sai readback mặc định | Timeout | Theo dõi đáp ứng | Dung sai đáp ứng mặc định |
|---|---|---|---|---|---|
| `SET_ESS_P` | Thanh ghi setpoint PCS/EMS tủ | Khớp tuyệt đối sau scale (± 1 LSB) | 10 s | `ess.p` so với setpoint hiệu lực | ± max(2% P định mức, 1 kW) sau thời gian ramp; lệch > 60 s → DEVIATING |
| `SET_ESS_MODE` | Thanh ghi chế độ | Bằng nhau | 30 s | `ess.mode` | — |
| `SET_PV_LIMIT` | Thanh ghi giới hạn (%/W) | ± 1 LSB | 10 s | `pv_inverter.p` ≤ giới hạn | ≤ giới hạn + max(2% Pđm, 1 kW) |
| `SET_EXPORT_LIMIT` (native) | Tham số trên logger | Bằng nhau | 30 s | Xuất tại `MTR_POC` | ≤ giới hạn + `export_violation_tol_w` sau ≤ 5 s (mục tiêu tham chiếu ≤ 2 s, FR-INT-017) |
| `SET_SOC_RESERVE` | Tham số (native hoặc edge) | Bằng nhau | 30 s | SOC không xuống dưới mức (trừ cho phép của mức 5) | — |
| `SET_EV_LIMIT` | Phản hồi `SetChargingProfile` = Accepted; `GetCompositeSchedule` nếu charger hỗ trợ | Bằng nhau | 30 s | Dòng/công suất đo của connector | ≤ giới hạn + 1 A sau 60 s [INFERENCE] |
| `APPLY_SCHEDULE` | Edge lưu và kiểm lịch | — | — | Ack theo slot | Theo F-OPT-10 |

Các giá trị dung sai là [PROPOSAL], cấu hình theo `capability_profile`; số "2% hoặc 1 kW" lấy từ ngưỡng xác minh map của FR-INT-020.

Thiết bị **không có `readback_ref`**: lệnh không bao giờ đạt `APPLIED`; edge báo `DISPATCHED` + `readback = UNSUPPORTED`, UI ghi "Đã gửi, thiết bị không cho đọc lại". PDP chặn mọi lệnh M2 tới thiết bị loại này trừ khi có đo đáp ứng độc lập (công tơ) và kỹ sư chấp thuận trong commissioning.

`APPLIED_CLAMPED` ghi giá trị thực sau kẹp và nguồn giới hạn (BMS, PCS, SOE, lưới, arbiter) (F-BESS-09). `FAILED_NO_EFFECT`: readback khớp nhưng thiết bị phản hồi "chấp nhận" mà giá trị không đổi, hoặc thanh ghi trả lại giá trị cũ — mẫu lỗi có trong báo cáo cộng đồng (§10.2).

### 8.6 Hết hạn và hoàn nguyên

| Lớp | Cơ chế | Giá trị |
|---|---|---|
| Cloud → edge | `expires_at` + Message Expiry MQTT | Setpoint 15 phút mặc định, ≤ 1 h; lịch ≤ 7 ngày |
| Edge → thiết bị | Reversion timeout gắn với setpoint, heartbeat register, fallback cấu hình sẵn, hoặc watchdog API của controller | 10–60 s, > 3 chu kỳ ghi (I §3.9) |
| Hết hạn | Edge thực hiện `on_expiry` (mặc định `REVERT_DEFAULT`) → `EXPIRED` → `COMPLETED` | — |

Các mẫu watchdog theo hãng là [UNKNOWN] tới khi kiểm chứng (I §3.8 ghi SunSpec 123/704 có trường revert time; nhiều PCS Trung Quốc có "EMS heartbeat"; SMA có tham số fallback; Victron chưa rõ — đều là kiến thức nền chưa kiểm chứng). Driver khai báo `watchdog_support` và `revert_timeout_s`; test F-INT-28 xác nhận.

**Gate M1 khi edge chết**: `on_expiry` do edge thực hiện nên không có tác dụng nếu edge mất nguồn. Vì vậy lệnh M1 tạm thời chỉ được gửi khi thiết bị có hoàn nguyên đã kiểm chứng hoặc giá trị là `persist_safe` (§8.1.1). Sau khi edge khởi động lại (`SAFE_START`), edge đọc lại các tham số native có lệnh đã hết hạn trong lúc tắt; giá trị lệch cấu hình nền → ghi hoàn nguyên, sinh sự kiện `CTRL.REVERT_AFTER_RESTART` và audit [PROPOSAL].

### 8.7 Thứ tự kiểm tra tại edge

[PROPOSAL] Ba phần: (A) kiểm danh tính và tính toàn vẹn, áp cho **mọi** lệnh; (B) đường an toàn hóa; (C) kiểm vận hành cho lệnh thường. Tham chiếu BR-SEC-05: edge không tin rằng cloud (PDP, Signer) đã kiểm đúng.

**A. Kiểm bắt buộc cho mọi lệnh**

1. Chữ ký JWS hợp lệ; `kid` thuộc danh sách tin cậy trong config đã ký → nếu sai: `REJECTED_INVALID`.
2. `target.edge_id` = chính nó; `target.site_id`/`asset_id` thuộc edge → `REJECTED_INVALID`.
3. **Kiểm cấu trúc và hạng nguy hiểm** theo bảng `command_policy` trong config đã ký (bảng có version, khớp §8.1 và PDP của [10](10-security-and-reliability.md)) → sai bất kỳ điều nào: `REJECTED_INVALID` + cảnh báo bảo mật:
   - `type` có trong bảng; đủ trường bắt buộc; không có trường lạ trong `params` (với `APPLY_SCHEDULE`: theo `PlanSlot`, §8.3).
   - `danger_class` ≥ `min_class(type, params)`. Hạng tối thiểu tính theo cả tham số: `SET_ESS_P` > 80% SOE → C2; `SET_SOC_RESERVE` giảm → C2; `REMOTE_CONTROL_RESUME`, `DEVICE_ON_OFF`, `SET_REVERSE_FEED_BLOCK` thủ công, `FW_UPDATE_EDGE` → C3. Lệnh nhãn thấp hơn mức tối thiểu bị từ chối dù chữ ký hợp lệ (chống lỗi hoặc danh tính bị chiếm của Signer/command service).
   - C2/C3: có `reason`. C3: có `approved_by` và `approval_ref`, `approved_by` ≠ `issued_by`, và `expires_at − valid_from ≤ 30 phút`.
   - `expires_at` có mặt và `expires_at − valid_from` ≤ trần theo type (setpoint 1 h, đổi chế độ 24 h, lịch 7 ngày — §8.2).
4. `command_id` chưa thấy (nếu đã thấy: trả trạng thái cũ, không thực thi lại); `seq` > `seq` cuối của signer → `REJECTED_REPLAY`. Bước này không cần đồng hồ.

**B. Đường an toàn hóa (safe-ify)**

5. Nếu `(type, params)` thuộc danh sách an toàn hóa trong config đã ký thì **bỏ qua** bước 6–12 (đồng hồ, hạn/độ trễ, kill switch, interlock, capability, SOE, arbiter) và áp dụng ngay, vì lệnh chỉ thu hẹp vận hành. Danh sách mặc định, khớp PDP-15 của [10](10-security-and-reliability.md):
   - `REMOTE_CONTROL_SUSPEND` (bật kill switch; **không** gồm `RESUME`);
   - `SET_ESS_P` với `p_w = 0`;
   - `CONFIG_PUSH` mà thay đổi duy nhất là `control_enabled: true → false`;
   - `REVERT` (hủy lệnh/lịch đang hiệu lực và thực hiện `REVERT_DEFAULT`; tên theo PDP-15 của 10).

   Ràng buộc của đường này:
   - Không vượt bảo vệ native và interlock vật lý: nếu interlock cấm ghi xuống thiết bị (IL-01 LOCAL, IL-02 E-stop, `MAINTENANCE`), edge chỉ thực hiện phần **nội bộ** (dừng vòng điều khiển của mình, hủy lệnh/lịch đang hiệu lực, chặn lệnh mới) và không ghi thiết bị.
   - Khi `UNSYNCED`, lệnh có hạn (`SET_ESS_P = 0`) được giữ tới khi lệnh khác thay thế hoặc đồng hồ đồng bộ lại và `expires_at` đã qua; kill switch giữ tới khi có `RESUME` (C3, đi đủ phần C).
   - Audit bắt buộc với `safe_path = true` và danh sách bước kiểm đã bỏ qua kèm lý do (ví dụ `SKIPPED: IL-06 UNSYNCED`, `SKIPPED: LATENCY 42000ms > 10000ms`); cảnh báo mức Cao để người vận hành biết lệnh đã đi đường ngoại lệ.
   - Danh sách an toàn hóa chỉ đổi bằng config ký (C3). Thêm type vào danh sách phải chứng minh type đó chỉ thu hẹp vận hành.

**C. Kiểm vận hành cho lệnh thường**

6. Đồng hồ `SYNCED` (IL-06) → `REJECTED_INTERLOCK:IL-06`.
7. `valid_from ≤ now ≤ expires_at`; `now − sent_at ≤ max_latency_ms` → `REJECTED_STALE`.
8. Kill switch không bật; site `control_enabled`.
9. Interlock IL-01…IL-10 → `REJECTED_INTERLOCK:<code>`.
10. Type có trong `capability_profile`; thiết bị `VERIFIED_*`; không `requires_native_fallback` với setpoint cưỡng bức (M2); lệnh M1 thỏa (a) hoặc (b) của §8.1.1 → nếu không: `REJECTED_UNSUPPORTED`.
11. Tham số trong SOE và `limits` → `REJECTED_OUT_OF_LIMIT` (giới hạn tĩnh) hoặc chấp nhận và kẹp (giới hạn động CCL/DCL → `APPLIED_CLAMPED`).
12. Mức arbiter: lệnh mức thấp hơn lệnh đang hiệu lực mà xung đột → `REJECTED_LOWER_PRIORITY` hoặc giữ hàng đợi tới khi lệnh mức cao hết hạn (theo `type`; mặc định từ chối với lệnh tay, xếp hàng với lịch).

Vector kiểm thử vàng cho phần A và B nằm ở §11.3 (T-NFR-SEC-004b…004e, T-FR-INT-018c/d).

### 8.8 Lệnh ghi qua cloud hãng (P2)

Với API hãng dạng async (Huawei OAuth Connect), connector ở cloud control plane tuần tự hóa theo nhà máy và ánh xạ trạng thái task → `DISPATCHED`/`APPLIED`/`FAILED_*`. Không có edge arbiter trên đường này, nên chỉ cho phép: lịch chậm (theo giờ), hạng ≥ C2, site không có edge điều khiển cùng chức năng (tránh hai chủ vòng). Mặc định tắt (FR-INT-028).

### 8.9 Lệnh điều độ (IEC 104, P1)

Edge nhận lệnh từ master 104 → tạo envelope nội bộ `source = GRID_OPERATOR` (không ký JWS cloud; xác thực theo conduit 104 và cấu hình đã ký), arbiter mức 4 → ghi xuống native/thiết bị → readback → mới trả ACT_CON/ACT_TERM. Lệnh và kết quả gửi lên cloud qua `up/event` để audit thống nhất (F-GRID-12). Lệnh điều độ được giữ khi mất cloud.

---

## 9. Onboarding và commissioning thiết bị

Mục này hợp nhất quy trình rải rác ở C §3.2, E §3.12, I §3.8 thành một checklist (K G-02). Luồng nghiệp vụ WF-02 và tiêu chí chấp nhận ở [04](04-business-requirements.md); tính năng F-INT-25…F-INT-29.

### 9.1 Trạng thái và vai trò

- Site và tài sản ở trạng thái `commissioning` (F-ORG-04): interlock IL-10 chặn mọi lệnh thường; chỉ `COMMISSIONING_TEST` và `dry_run` được phép (§9.4).
- Người làm: Site Engineer (P4/P5); người nghiệm thu: Control Supervisor hoặc đại diện chủ tài sản. Mỗi bước ghi bằng chứng, người làm, thời điểm (FR-INT-015).
- Khi bước bắt buộc chưa đạt: site không được chuyển `active` với gói CONTROL; vẫn có thể `active` ở gói MONITORING.

### 9.2 Checklist theo bước

| # | Bước | Việc làm | Tiêu chí đạt [PROPOSAL] | Bằng chứng | Gate | Tính năng / FR |
|---|---|---|---|---|---|---|
| 1 | Chuẩn bị hồ sơ | SLD, danh sách thiết bị (model, firmware, serial), vị trí CT/VT, hợp đồng/biểu giá, cấu hình lưới dự kiến | Đủ trường bắt buộc của F-ORG-05 | Tài liệu site (F-ORG-12) | M1 | F-ORG-05 |
| 2 | Claim edge | Quét QR/serial; cloud cấp chứng chỉ vận hành; gán site | Edge `ONLINE`, cert hợp lệ | Event | M1 | F-INT-02 |
| 3 | Mạng và đồng hồ | Kiểm tách WAN/OT, không định tuyến; chrony | `uplink_state = ONLINE`, `clock_state = SYNCED` | Ảnh chụp trạng thái edge | M1 | F-INT-10, F-SEC-17 |
| 4 | Khám phá thiết bị | Quét Modbus/SunSpec trên OT LAN/bus; fingerprint | Mọi thiết bị trong hồ sơ được tìm thấy hoặc khai báo tay | `capability_profile` | M1 | F-INT-05 |
| 5 | Gán driver | Chọn `DriverVersion`; hiển thị trạng thái kiểm chứng | Driver tồn tại cho model/firmware; driver không `VERIFIED_*` chỉ được đọc | Ghi driver@version | M1 | F-INT-03 |
| 6 | Kiểm ngân sách polling | Đo thời gian giao dịch từng bus | Chu kỳ C1 đạt; không chung bus RTU giữa `MTR_POC` và inverter | Báo cáo bus | M1 | F-INT-04 |
| 7 | Xác minh map điểm | §9.3 | Lệch P ≤ 2% hoặc ≤ 1 kW; U ≤ 1%; đơn vị/scale đúng; bộ đếm tăng đúng hướng | Bảng "Khớp/Lệch" | M1 | FR-INT-020 |
| 8 | Phép thử dấu | §9.5 | Dấu đúng ở mọi điểm đo | Bảng kết quả | M1 | F-INT-26 |
| 9 | Khai báo chủ vòng | `control_owner` theo chức năng | Không có hai chủ vòng trên một biến | Cấu hình | M1 | F-OPT-02 |
| 10 | Tín hiệu an toàn | Kiểm DI: LOCAL/REMOTE, E-stop, PCCC, cửa tủ (§4.3) bằng thao tác thật | Mỗi tín hiệu đổi trạng thái đúng trên edge | Bảng tín hiệu | M1 (đọc), M2 (bắt buộc) | F-BESS-18, F-GRID-13 |
| 11 | Cấu hình và kiểm chứng native | Đặt giới hạn xuất/chế độ native qua driver đã kiểm chứng; đọc lại | Readback khớp | Nhật ký | M1 | F-GRID-04, F-BESS-04 |
| 12 | Test giới hạn xuất | Kịch bản giảm tải/tăng PV | Xuất về ≤ giới hạn + tol trong ≤ 5 s (mục tiêu ≤ 2 s); ghi số giây vượt | Biểu đồ 1 s, số liệu | M1 | F-INT-27 |
| 13 | Test watchdog và fail-safe (chỉ M2) | Rút cáp edge↔thiết bị; mất `MTR_POC`; chặn cloud; chuyển LOCAL; tắt nguồn edge | Thiết bị về mặc định trong `revert_timeout_s`; BESS P = 0/native trong ≤ 2 chu kỳ khi mất POC; không đạt → `requires_native_fallback = true` | Biểu đồ 1 s, nhật ký | M2 | F-INT-28 |
| 14 | SOE (chỉ M2) | Đề xuất, duyệt hai người, ký, đẩy xuống | SOE `APPLIED` trên edge | SOE version | M2 | F-BESS-08 |
| 15 | Biên bản | Sinh PDF: cấu hình, kết quả từng bước, driver/SOE version, chữ ký | Đủ chữ ký | PDF trong tài liệu site | M1 | F-INT-29 |
| 16 | Bật control | Lệnh C3 bật `control_enabled` + bản ghi đồng ý của chủ tài sản | Hai người duyệt | Audit | M1/M2 | F-SEC-05 |

### 9.3 Checklist xác minh điểm (point verification)

| Đối tượng | Kiểm | Tham chiếu | Đạt |
|---|---|---|---|
| Công suất tác dụng | `p` qua driver so với màn hình thiết bị hoặc đồng hồ kẹp | HMI/đồng hồ | Lệch ≤ 2% hoặc ≤ 1 kW |
| Điện áp | `u.l1–l3` | HMI/đồng hồ | ≤ 1% |
| Tần số | `f` | HMI | ≤ 0,05 Hz [PROPOSAL] |
| Bộ đếm năng lượng | `e_*` tăng đúng hướng trong ≥ 10 phút; ΔE so với ∫P | Tính tay | Lệch ≤ 2% [PROPOSAL] |
| SOC (BESS) | `ess.soc` so với HMI EMS tủ/BMS | HMI | Bằng nhau (± 1 điểm %) |
| Giới hạn cho phép | `p_charge_max`/`p_discharge_max` so với HMI/PCS | HMI | Bằng nhau theo scale |
| Nameplate | Model, serial, firmware | Nhãn thiết bị | Khớp |
| Hệ số CT/VT | Giá trị thứ cấp × tỷ số | Hồ sơ | Khớp |
| Đơn vị/scale | Kiểm không lệch 10×/1000× | — | Đúng |
| Sentinel | Thiết bị tắt/ban đêm không sinh giá trị giả | — | `BAD_DEVICE` hoặc giá trị hợp lý |
| Thời gian thiết bị | `ts_src` so với `ts` | — | Lệch ≤ 2 s hoặc driver chuẩn hóa đúng múi giờ |

### 9.4 Lệnh thử trong chế độ sandbox

Hai mức "sandbox" khác nhau, không được nhầm:

| Mức | Là gì | Dùng để | Nhãn |
|---|---|---|---|
| **Sandbox mô phỏng** | Site ảo chạy trên bộ mô phỏng thiết bị (§11.2), edge thật hoặc edge ảo | Thử cấu hình, driver, lịch trước khi ra hiện trường; đào tạo | Mọi màn hình và báo cáo của site ảo mang nhãn "Mô phỏng"; dữ liệu không vào KPI thật |
| **Chế độ thử tại hiện trường** | Site thật ở `commissioning`, edge ở trạng thái con `MAINTENANCE/COMMISSIONING_TEST` | Phép thử dấu, test giới hạn xuất, test watchdog | Lệnh `COMMISSIONING_TEST` |

Quy tắc `COMMISSIONING_TEST` [PROPOSAL]:
- Chỉ khi site `commissioning` **và** edge ở trạng thái con `local_remote_state = MAINTENANCE`, `maintenance_substate = COMMISSIONING_TEST` (định nghĩa dưới).
- "Phong bì test": |P| ≤ 10% P định mức hoặc ≤ 50 kW (lấy nhỏ hơn), thời gian ≤ 10 phút mỗi bước, `on_expiry = REVERT_DEFAULT`; không vượt SOE nháp hay giới hạn native.
- Hạng C2 (step-up MFA, lý do bắt buộc); mọi bước vào audit và biên bản.
- `dry_run = true` dùng trước mỗi lệnh thử để kiểm interlock/capability mà không ghi.

**Trạng thái con `MAINTENANCE/COMMISSIONING_TEST`** [PROPOSAL]

Lý do: ở `MAINTENANCE` thường, edge nhả kết nối ghi ([10 §12.2](10-security-and-reliability.md)), nên lệnh thử không ghi được; site Gate M1 không bắt buộc có công tắc LOCAL/REMOTE (FR-SEC-010 thuộc M2); HMI cục bộ (F-MON-11) chưa có ở Phase 1. Không định nghĩa trạng thái con thì phép thử dấu và test giới hạn xuất (FR-INT-016/017, bắt buộc cho G1) không thể thỏa điều kiện của chính nó.

| Khía cạnh | Quy tắc |
|---|---|
| Vào trạng thái | Site ở `commissioning` **và** (công tắc khóa chìa ở `MAINTENANCE`, **hoặc** site không có công tắc) **và** xác nhận có mặt (dưới). Site có công tắc ở `LOCAL` → không vào được |
| Xác nhận có mặt (Phase 1, không cần HMI) | Kỹ sư yêu cầu phiên test trên app; cloud gửi xuống một mã 4 chữ số; edge chỉ mở phiên khi **nút vật lý trên edge** được nhấn trong 120 s sau đó (hoặc chuỗi nhấn theo mã nếu edge có LED/màn hình 7 đoạn hiển thị mã để kỹ sư nhập lại trên app). Nút phải đi qua DI/GPIO cục bộ, không đi qua mạng. Yêu cầu phần cứng: thêm vào §6.15 |
| Phiên | Tối đa 2 h, gia hạn bằng nhấn nút lại; hết phiên hoặc rút cáp/khởi động lại edge → thoát |
| Kết nối ghi | Edge **giữ (hoặc lấy lại)** kết nối ghi **chỉ** để thực thi `COMMISSIONING_TEST` trong phong bì test; mọi type khác (kể cả lịch, lệnh tay, chiến lược mặc định) bị từ chối `REJECTED_INTERLOCK:IL-10`. Thiết bị chỉ nhận một client (Huawei, EL-062): công cụ engineering của installer phải ngắt trong phiên test |
| Thoát | Edge thực hiện `REVERT_DEFAULT` cho mọi bước test đang hiệu lực, đọc lại xác nhận, rồi về `MAINTENANCE` thường (nhả kết nối ghi) hoặc `REMOTE` theo công tắc. Không có công tắc → về trạng thái trước phiên |
| Đường an toàn hóa | Vẫn áp (§8.7 B) |
| Hiển thị và audit | `edge.local_remote_state` + `maintenance_substate` trong `up/state`; banner "Đang thử nghiệm commissioning tại chỗ"; mỗi lần vào/ra là sự kiện audit có người, mã phiên, thời gian nhấn nút |

Cần 10 §12.2 bổ sung dòng trạng thái con này (X-07-10).

### 9.5 Phép thử dấu (chi tiết)

[PROPOSAL] theo C §3.2 và FR-INT-016:

| Bước | Tình huống tạo ra | Kỳ vọng |
|---|---|---|
| 1 | PV và BESS dừng (hoặc ban đêm); bật một tải đã biết | `MTR_POC.p` tăng **dương**; `e_import` tăng |
| 2 | BESS sạc nhỏ (≥ 5% P định mức hoặc ≥ 5 kW, ≥ 60 s) | `ess.p` **âm**; `MTR_POC.p` tăng; `e_charge` tăng |
| 3 | BESS xả nhỏ (cùng biên độ) | `ess.p` **dương**; `MTR_POC.p` giảm; `e_discharge` tăng |
| 4 | Giới hạn PV xuống mức thấp | `pv_inverter.p` giảm, `MTR_POC.p` tăng tương ứng |
| 5 | (Nếu có xuất) PV vượt tải | `MTR_POC.p` **âm**; `e_export` tăng |
| 6 | Tải cảm đã biết (động cơ) | `MTR_POC.q` dương (vô công vào site, K R-02) |
| 7 | Cân bằng | `P_cons = P_grid + P_pv + P_bess` không âm và hợp lý; residual nhỏ (F-HIST-09) |

[INFERENCE] Lắp ngược CT là lỗi thực địa phổ biến; phép thử này bắt được cả lỗi lắp đặt chứ không chỉ lỗi driver (C §3.2).

---

## 10. Ghi chú tích hợp theo hãng

Quy ước: "Không thấy tài liệu" nghĩa là các nguồn đã xem không nói, **không** có nghĩa hãng không hỗ trợ (IP-12). Mọi thanh ghi từ diễn đàn chỉ để định hướng thử lab.

### 10.1 Huawei (SUN2000, SmartLogger, EMMA, SDongle, LUNA2000)

| Hạng mục | Nội dung | Nhãn |
|---|---|---|
| Tài liệu | "Solar Inverter Modbus Interface Definitions", Issue 05, 2023-02-16; FC 0x03/0x06/0x10 (bản PDF qua diễn đàn ioBroker) | [FACT, Med] nghiên cứu FusionSolar trước |
| Ví dụ thanh ghi | 32080 công suất tác dụng (I32, kW, gain 1000); 37113 công suất công tơ (I32, W; > 0 feed-in, < 0 import); 37760 SOC pin (U16, %, gain 10) | [FACT, Med] Issue 05 qua bản sao diễn đàn S-185 (https://forum.iobroker.net/assets/uploads/files/1699119419919-solar-inverter-modbus-interface-definitions-v5.pdf), như ghi trong nghiên cứu FusionSolar trước (`api_integration.md`, S-393); 37760 cũng có trong định nghĩa thanh ghi của huawei-solar-lib. Bản sao không chính thức → chưa đủ cho driver `VERIFIED_*` (V-10) |
| 47086 (chế độ làm việc pin) | Có trong nghiên cứu FusionSolar trước, nhưng giá trị/cách dùng để điều khiển chỉ đến từ cộng đồng (hàng "Điều khiển pin" bên dưới) | [FACT, Low] cộng đồng báo cáo (EL-063); **cấm** dùng cho driver `VERIFIED_*` |
| Kết nối | Modbus TCP cổng 6607 (firmware từ 12/2021) hoặc 502; unit ID 1 (0 qua AP inverter); RTU 9600 baud; phải bật "Enable (Unlimited)"/"Unrestricted Modbus TCP" — wiki huawei_solar https://github.com/wlcrs/huawei_solar/wiki/Connecting-to-the-inverter (S-296), tài liệu Eniris https://docs.eniris.com/nl/Controller/Devices/PV-hybrid-and-battery-inverters/Huawei, theo nghiên cứu FusionSolar trước (S-393). **Lưu ý**: ghi chú FS trước (`source_code_clients.md`) đính chính rằng mã huawei_solar hiện mặc định cổng 502 / unit 0 — https://github.com/wlcrs/huawei_solar/blob/main/const.py#L6-L7 | [FACT, Med] nguồn cộng đồng/bên thứ ba, không phải tài liệu Huawei; driver phải thử cả 6607/502 và unit 0/1 khi khám phá |
| Một client | "Modbus devices only support one connection at a time" (huawei_solar, S-296); proxy song song "may cause communication errors" (evcc, S-299) — EL-062 | [FACT, Med] |
| Dongle | Đọc ≥ 5 s; timeout ≥ 1.000 ms; connect delay 1–5 s; "first TX always fails"; SDongleA-05/FE gây nhiễu RS485A1/B1 | [FACT, Low–Med] cộng đồng |
| EMMA | Modbus TCP chỉ ở cổng 502, không chỉnh Modbus ID; chỉ tài khoản installer bật được; datasheet: "Supports Modbus-TCP and third-party VPP integration", quản lý tối đa 2 SCharger — https://forum.iobroker.net/post/1270320 ; https://raspberry.tips/raspberrypi-tutorials/huawei-sun2000-home-assistant-emma-solar-dashboard ; https://solar.huawei.com/en/professionals/all-products/EMMA/specs ; https://www.heima24.de/shop/images/products/media/db-huawei-emma02.pdf (qua kết quả tìm kiếm) | [FACT] datasheet Med, forum Low |
| Điều khiển pin (cộng đồng) | 47086 = 6 "Third-party Scheduling"; 47100 kích hoạt sạc/xả cưỡng bức; 47083 thời lượng; 47102 công suất; 47104 SOC đích; có người bật/tắt được nhưng không đổi được công suất — https://community.homey.app/t/app-pro-huawei-fusionsolar-manager/153353?page=16 ; https://community.openhab.org/t/sveasolar-powershifter-pv-inverter-huawei/164046 (qua kết quả tìm kiếm; S-302, S-303) | [FACT, Low] cộng đồng báo cáo (EL-063); **không dùng làm map đã kiểm chứng** |
| Thời gian | 40000 (U32, epoch giây giờ địa phương), 43006 múi giờ (I16, phút) — §6.8 | [FACT, Low–Med] |
| SmartLogger | IEC 104 cho tối đa 5 kết nối bên thứ ba; outbound TLS tới cloud Huawei (nghiên cứu FusionSolar trước, `architecture_security.md`) | [FACT, Med] |
| Controller site C&I | SmartLogger5000B/SmartMGC5000B: zero feed-in ≤ 2 s, peak shaving/giới hạn ≤ 5 s (tự công bố) | [FACT, Med] (K R-19) |
| Ràng buộc chế độ | Peak shaving chỉ ở kịch bản on/off-grid **chỉ** đúng với manual LUNA2000-(107-215) C&I-Microgrid-SmartLogger3000 được trích; không áp cho SmartLogger5000B on-grid hay SmartEMO | K R-20 |
| Cloud | Northbound đọc + OAuth Connect control async (§5.11.1) | [FACT, High] |
| Hướng tích hợp [PROPOSAL] | **C&I**: Modbus TCP tới SmartLogger (một client), ghi tham số native (giới hạn xuất, capacity control, lịch TOU) có readback — Gate M1. **SME/hộ**: EMMA cổng 502. Northbound cho site chỉ giám sát | — |
| Rủi ro | Một client nên SCADA khác của khách phải đọc qua edge; slave 104 có sẵn của SmartLogger có thể chồng chéo slave 104 của ta (§5.7); thay đổi chính sách cloud (09/2025); watchdog lệnh remote [UNKNOWN] (Q-E-04) | — |

### 10.2 Sungrow (Logger1000, EMS300CP, SH hybrid, PowerStack)

| Hạng mục | Nội dung | Nhãn |
|---|---|---|
| Logger1000 | Theo cộng đồng: unit ID mặc định 247, địa chỉ tài liệu phải trừ 1; đọc được nhưng **không ghi được setpoint**; một ý kiến cho rằng Sungrow không công bố tham số đọc/ghi của logger — https://community.homey.app/t/modbus-register-logger-1000-sungrow/126405 ; https://forum.cleanenergyreviews.info/t/logger1000-as-modbus-tcp-server/3181 (qua kết quả tìm kiếm) | [FACT, Low] |
| Hybrid SH | 13049 = EMS mode; lệnh sạc/xả 0xAA/0xBB/0xCC ở **13050 hoặc 13051** (nguồn mâu thuẫn); có báo cáo lệnh "không có tác dụng" — https://www.loxforum.com/forum/german/software-konfiguration-programm-und-visualisierung/424167-sungrow-sh10rt-wr-modbusparameter ; https://forum.iobroker.net/post/936007 (qua kết quả tìm kiếm) | [FACT, Low] **không dùng làm map** |
| PowerStack | EMS/PCS/BMS tích hợp; hỗ trợ Modbus TCP cho EMS bên thứ ba (B L41, nhiều nguồn báo chí/nhà phân phối) — ví dụ https://www.sungrowpower.com/mal/en/products/c-i-energy-storage-system/st255cs-2h (qua kết quả tìm kiếm) | [FACT, Med] |
| Cloud | iSolarCloud (§5.11.2) | — |
| Hướng tích hợp [PROPOSAL] | Driver ở vị trí (5) của thư viện MVP, **chỉ sau khi có register map chính thức** qua kênh đối tác Sungrow (Q-E-03). Trước đó: đọc qua iSolarCloud | — |
| Rủi ro | Map không công khai; báo cáo ghi không tác dụng → bắt buộc readback và `FAILED_NO_EFFECT` | — |

### 10.3 SMA

| Hạng mục | Nội dung | Nhãn |
|---|---|---|
| Local | SunSpec Modbus; danh sách model 701–714 và 201–204/211–214; profile 2.0 bỏ 124 và 126 (§5.2) | [FACT, Med–High] |
| Cloud | Monitoring API, GridControl API, GeoForecast API; sandbox; Live API không dùng giám sát liên tục; HTTP 308 khi di trú; có thể tính phí (§5.11.2) | [FACT, Med–High] |
| Hướng [PROPOSAL] | SunSpec chung (vị trí 3 của thư viện MVP) với overlay SMA; cloud chỉ đọc (P1) | — |
| Chưa biết | GridControl API cho phép P/Q setpoint không, ai được cấp (Q-E-11); tham số fallback khi mất tín hiệu điều khiển ngoài (kiến thức nền, chưa kiểm chứng) | [UNKNOWN] |

### 10.4 Victron (Cerbo GX, Venus OS)

| Hạng mục | Nội dung | Nhãn |
|---|---|---|
| Giao diện | MQTT (1883) và Modbus TCP (502, bật trong Settings → Services) | [FACT, Low–Med] |
| ESS | Theo cộng đồng, "Mode 2" dùng điểm `/AcPowerSetpoint` (thanh ghi 2700, int16) cho setpoint lưới; "Mode 3" giao cả vòng điều khiển ra ngoài; một thread nêu thanh ghi 37 — https://communityarchive.victronenergy.com/questions/95889/multipluss-ii-is-external-control-ess-mode-2-or-3%EF%B9%96childToView=102991.html ; https://mcpservers.org/en/servers/lubosstrejcek/victron-tcp (qua kết quả tìm kiếm) | [FACT, Low–Med] |
| Chưa biết | Hành vi khi master Modbus mất kết nối; setpoint ghi vào flash hay RAM (câu hỏi cộng đồng chưa có lời đáp) (Q-E-06) | [UNKNOWN] |
| Hướng [PROPOSAL] | Không trong thư viện MVP (phân khúc C&I ở VN chưa đánh giá — K G-08). Nếu làm: chỉ Mode 2, sau khi có register list chính thức và test watchdog | — |

### 10.5 Solis, Growatt, Deye/Solarman

| Hạng mục | Nội dung | Nhãn |
|---|---|---|
| Cloud | Chỉ đọc (§5.11.2) | [FACT, Low–Med] |
| Local Modbus | Map của hãng **chưa nghiên cứu** trong lượt này | [UNKNOWN] |
| Thị phần VN | Có thể phổ biến ở phân khúc hộ/SME (Deye/Solarman), chưa có số liệu (K G-08, Q-E-16) | [UNKNOWN] |
| Hướng [PROPOSAL] | Connector cloud chỉ đọc ở P1 (F-INT-13); đánh giá driver local ở lượt nghiên cứu 2 trước khi đưa vào thư viện | — |

### 10.6 Ampowr (nguồn hạt giống — đối thủ, không phải thiết bị)

- [FACT, Med] Ampowr Cosmos mô tả peak shaving theo giới hạn đấu nối, tự tiêu thụ, giao dịch thị trường ở Hà Lan; case study nêu "Partner API" và "local backup feature" để tiếp tục chiến lược khi mất mạng — https://ampowr.com/energy-management-system-ems/ ; https://ampowr.com/hoge-duin-hotel-enhances-energy-efficiency-with-ampifarm-peak-shaving/ (qua kết quả tìm kiếm; B L04, L06).
- [INFERENCE] Mô hình "chiến lược chạy cục bộ khi mất mạng" khớp nguyên tắc edge-first của ta (§6.11). Chi tiết Partner API không có tài liệu công khai trong các nguồn đã thấy.
- Nguồn rfp.wiki về Ampowr là nội dung AI sinh, **không dùng** (K R-18, §4).
- Đối với thiết bị: một tài liệu tích hợp bên thứ ba ghi unit ID hybrid Ampowr 247 (RTU)/255 (TCP) (§5.1.3). Không thuộc thư viện MVP.

### 10.7 Tủ BESS Trung Quốc all-in-one (ví dụ HT Infinite Power)

| Hạng mục | Nội dung | Nhãn |
|---|---|---|
| Đã công bố | EMS tích hợp: lập lịch, giám sát, truy cập từ xa; cổng CAN, RS-485, Ethernet, Wi-Fi; container có EMS thu thập dữ liệu, điều khiển, màn hình tại chỗ; hybrid có cập nhật firmware từ xa và đẩy cảnh báo — https://www.infinitepowerht.com/commercial-energy-storage-solutions.html ; https://www.infinitepowerht.com/1000-kwh-battery-outdoor-container-ess.html ; https://www.infinitepowerht.com/261kwh-522kwh-hybrid-energy-storage-system.html (qua kết quả tìm kiếm; B L08–L10) | [FACT, Low–Med] |
| Không thấy công bố | Bảng thanh ghi northbound, điểm điều khiển P/Q/mode, watchdog | "Không có tài liệu" |
| Trang seed | https://www.infinitepowerht.com/what-is-energy-management-system-ems-and-its-functions.html chỉ dùng cho định nghĩa chung "EMS điều phối BMS và PCS" (FACT Low, K R-18); không gán tính năng cụ thể | — |
| Trang "AI-Powered EMS" | Nội dung marketing, không phải mô tả kỹ thuật (B L12) | Không gọi là AI |
| Hướng [PROPOSAL] | Mỗi dòng tủ là một driver riêng; chỉ đưa vào thư viện MVP **một** dòng có hợp đồng cung cấp register map (dưới NDA nếu cần) và cam kết hỗ trợ khi đổi firmware (Q-E-09). EMS tủ là controller native (`control_owner = NATIVE` cho bảo vệ và phân bổ rack) | — |

### 10.8 Logger thương mại (meteocontrol, Solar-Log) và SolarEdge

| Sản phẩm | Giao diện cho bên thứ ba | Nhãn và nguồn (qua kết quả tìm kiếm) | Bài học |
|---|---|---|---|
| meteocontrol blue'Log XC | License "Modbus Power Control" (firmware ≥ 10.0.8, slave ID 1, port 502, delay 1.000 ms) nhận setpoint P/Q/cosφ; IEC 101/104, 61850, DNP3 qua bộ chuyển đổi giao thức riêng (PLC PFC200, ILC 171) rồi sang Modbus TCP | [FACT, Med–High] https://www.meteocontrol.com/fileadmin/Daten/Dokumente/EN/Produkte/On_Site/blue_Log_XM_XC/Data_sheet/blue_Log_XM_XC_Modbus_Power_Control_license_blue_Log_XC_data_sheet_LastMod-2026-01-27_en.pdf | Mô hình "PPC + protocol converter"; chi phí license vào báo giá tích hợp |
| Solar-Log "Modbus TCP PM" | License; port 502, slave ID 1, FC 04/06/16; nhận lệnh P/Q từ thiết bị ngoài | [FACT, Med–High] https://www.solar-log.com/fileadmin/user_upload/documents/Datenblaetter/en_GB/Komponenten/Kommunikation/SolarLog_Datasheet_Modbus_TCP_PM_EN.pdf | Như trên |
| SolarEdge ONE Controller C&I | Modbus TCP server cổng 1502, 2 × RS485, CAN, 4DI/4DO | [FACT, High] B L34 | Tham chiếu phần cứng edge (§6.15) |

### 10.9 Sạc EV

| Hạng mục | Nội dung | Nhãn |
|---|---|---|
| Easee | TxDefaultProfile không tự xóa, có thể đè TxProfile (0 A đè 20 A) | [FACT, Med] (§5.9) |
| Bender | Hướng dẫn smart charging OCPP 1.6: ba loại profile, stackLevel, TxDefaultProfile cho mất kết nối | [FACT, Med] (§5.9) |
| Huawei SCharger | Đọc qua EMMA (huawei-solar-lib, nghiên cứu FusionSolar trước) | [FACT, Low–Med] |
| Hướng [PROPOSAL] | Charger profile theo model; kiểm OCPP profile và quirk trong lab trước khi đưa vào danh sách hỗ trợ | — |

### 10.10 Tóm tắt thứ tự driver MVP

Theo FR-INT-006 (thứ tự có thể đổi sau đánh giá thị phần):

| Thứ tự | Driver | Đường | Ghi | Điều kiện vào `VERIFIED_LAB` |
|---|---|---|---|---|
| 1 | Công tơ PCC Modbus phổ biến (2–3 model) | Modbus TCP/RTU | Không | Tài liệu hãng + test map + phép thử dấu trên bàn thử |
| 2 | Huawei SmartLogger + EMMA | Modbus TCP | Tham số native (giới hạn xuất, chế độ pin) — Gate M1 | Tài liệu Modbus Interface Definitions bản hiện hành + lab có thiết bị thật |
| 3 | SunSpec chung (1, 101–103, 120–124, 201–214, 701–714, 802–804) | Modbus TCP | Chỉ đọc mặc định; ghi theo overlay đã kiểm chứng | Test trên ≥ 1 thiết bị thật mỗi overlay |
| 4 | Một dòng tủ BESS có hợp đồng cung cấp map | Modbus TCP northbound | P/mode — Gate M2 | Map chính thức + test watchdog |
| 5 | Sungrow EMS300CP/PowerStack | Modbus TCP | Sau khi có map chính thức | Như 4 |

---

## 11. Chiến lược kiểm thử tích hợp

Đáp ứng K G-05. Mọi bộ mô phỏng là **công cụ nội bộ**; kết quả mô phỏng gắn nhãn "Mô phỏng" và **không** dùng làm bằng chứng nâng trạng thái driver lên `VERIFIED_*` (D-07-13). Mã test theo quy ước `T-<FR id>`.

### 11.1 Các tầng kiểm thử

| Tầng | Mục tiêu | Công cụ/môi trường | Chạy khi | Bằng chứng cho |
|---|---|---|---|---|
| L1 Giải mã driver | Kiểm từng thanh ghi: word order, scale/SF, sentinel, dấu, tràn bộ đếm | "Vector vàng" (khung Modbus thô → giá trị kỳ vọng) lấy từ tài liệu hãng hoặc ghi từ thiết bị thật | Mỗi commit driver | Chất lượng driver |
| L2 Hợp đồng | Payload telemetry/lệnh/ack đúng schema §7–§8; tương thích ngược theo version | JSON Schema + Protobuf descriptor; test consumer-driven giữa edge và ingest | Mỗi commit | Ổn định hợp đồng |
| L3 Mô phỏng thiết bị | Edge + driver với thiết bị ảo | Modbus server mô phỏng (inverter, PCS/BMS, công tơ có dấu cấu hình được), SunSpec model chain, charger OCPP mô phỏng | CI hằng ngày | Logic edge, arbiter, buffer |
| L4 Tiêm lỗi | Timeout, exception, ngắt TCP, giá trị đóng băng, nhảy bộ đếm, lệch đồng hồ, mất broker, lệnh replay/hết hạn, thiết bị không watchdog, "ghi không tác dụng" | Mô phỏng + proxy mạng gây lỗi | CI hằng đêm | NFR-REL, NFR-SEC |
| L5 HIL / lab | Thiết bị thật: SmartLogger/EMMA, inverter, công tơ, 1 tủ BESS (hoặc PCS), 1 charger OCPP; tải giả lập | Lab thiết bị (X-E-06) | Trước mỗi release edge; khi thêm driver | `VERIFIED_LAB` |
| L6 Pilot hiện trường | Site thật, checklist §9 | Hiện trường | Site pilot | `VERIFIED_FIELD` |
| L7 Tải và khối lượng | Ingest 35.000 mẫu/s (1.000 site) và đỉnh backfill 5–10× | Bộ sinh tải edge ảo | Trước Gate MVP | NFR-PERF-004 |

### 11.2 Bộ mô phỏng (đều là "Mô phỏng")

| Bộ mô phỏng | Cách xây [PROPOSAL] | Ghi chú bằng chứng |
|---|---|---|
| Modbus server thiết bị | Dựng trên thư viện Modbus mã nguồn mở (ví dụ pymodbus cho Python, hoặc thư viện Java như j2mod/digitalpetri — hai thư viện Java được nghiên cứu FusionSolar trước nhắc tới); nạp **cùng register map YAML** của driver để sinh thanh ghi; mô hình vật lý đơn giản (PV theo profile bức xạ, BESS tích phân SOC, công tơ cân bằng) | Tên thư viện là kiến thức nền; khả năng cụ thể [UNKNOWN] tới khi đánh giá; chọn theo giấy phép |
| SunSpec chain | Sinh chuỗi "SunS" + model 1/103/701/704/713/802 từ định nghĩa model của SunSpec (SMDX/JSON công bố trên GitHub SunSpec — Q-E-07) | Không thay thế test thiết bị thật vì có lỗi tương tác ở thiết bị đã chứng nhận (§5.2) |
| Công tơ có dấu cấu hình được | Tham số `sign_convention`, `register_wrap`, `ct_ratio`, lỗi lắp ngược CT | Phục vụ test phép thử dấu |
| PCS/BMS | CCL/DCL thay đổi theo SOC/nhiệt độ; chế độ có/không watchdog; chế độ "ghi chấp nhận nhưng không tác dụng" | Phục vụ `APPLIED_CLAMPED`, `FAILED_NO_EFFECT`, `requires_native_fallback` |
| Charger OCPP 1.6J | Charge point mô phỏng (thư viện OCPP mã nguồn mở, cần đánh giá) có profile quirk (ví dụ hành vi Easee) và chế độ mất kết nối | Thư viện cụ thể [UNKNOWN] |
| Master IEC 104 (P1) | Master mô phỏng gửi interrogation, setpoint, clock sync | Chỉ khi làm F-INT-16 |
| Edge ảo hàng loạt | N edge gửi telemetry theo hợp đồng §7 với `seq`, mất kết nối, backfill | L7 |

### 11.3 Danh mục ca kiểm thử chính

| Mã | Ca kiểm thử | Tiêu chí đạt | Tầng |
|---|---|---|---|
| T-FR-INT-003 | Driver giải mã đúng mọi vector vàng (I32 CDAB, SF âm, sentinel 0xFFFF, U32 quay vòng) | 100% vector đạt | L1 |
| T-FR-INT-004 | Edge là master duy nhất; gom block ≤ 125 đọc/≤ 123 ghi; không vắt qua lỗ địa chỉ | Không có giao dịch vượt giới hạn | L3 |
| T-FR-INT-005 | Khám phá SunSpec ở 40000/50000/0; dừng ở 0xFFFF; profile đúng | Profile khớp mô phỏng | L3 |
| T-FR-INT-007 | Lệnh → readback: APPLIED; kẹp CCL → APPLIED_CLAMPED; ghi không tác dụng → FAILED_NO_EFFECT; thiết bị im → FAILED_TIMEOUT | Đúng trạng thái trong timeout | L3, L4 |
| T-FR-INT-008 | Gửi trùng, đảo thứ tự, lỗ `seq` | Ingest idempotent; `latest_value` chỉ tiến; RESEND_REQUEST cho lỗ | L2, L4 |
| T-FR-INT-009 | Rút WAN 7 ngày (tăng tốc thời gian hoặc chạy thật trên HIL) | 0 mẫu C4/C5 mất; C1–C3 đủ trong buffer; xả có giới hạn tốc độ | L4, L5 |
| T-FR-INT-010 | Lệch đồng hồ > 1 s | `UNSYNCED`, mẫu `UNCERTAIN_CLOCK`, lệnh bị IL-06 | L4 |
| T-FR-INT-011 | Config không ký / ký sai `kid` | Edge `REJECTED`, giữ config cũ | L4 |
| T-FR-INT-012 | OTA lỗi khởi động | Rollback tự động về slot cũ | L5 |
| T-FR-INT-016 | Phép thử dấu trên công tơ mô phỏng lắp ngược CT | Phát hiện và báo lỗi | L3, L5 |
| T-FR-INT-017 | Bước tải/PV làm xuất vượt giới hạn | Về ≤ giới hạn + tol trong ≤ 5 s | L5 |
| T-FR-INT-018 | Rút cáp edge↔PCS; mất `MTR_POC`; chặn broker; chuyển LOCAL; tắt nguồn edge | Thiết bị về mặc định trong `revert_timeout_s`; BESS P = 0/native ≤ 2 chu kỳ | L4, L5 |
| T-NFR-SEC-004 | Lệnh replay (`seq` cũ), lệnh hết hạn, chữ ký sai, `target.edge_id` sai | `REJECTED_REPLAY`/`STALE`/`INVALID`; cảnh báo bảo mật | L4 |
| T-NFR-SEC-004b | Vector vàng hạng nguy hiểm: `DEVICE_ON_OFF` và `SET_REVERSE_FEED_BLOCK` nhãn C1, chữ ký hợp lệ; `SET_SOC_RESERVE` giảm nhãn C1; `SET_ESS_P` > 80% SOE nhãn C1 | `REJECTED_INVALID`; cảnh báo bảo mật; không ghi thiết bị | L1, L4 |
| T-NFR-SEC-004c | Vector vàng C3: thiếu `approval_ref`; thiếu `reason`; `approved_by` = `issued_by`; `expires_at − valid_from` = 31 phút | `REJECTED_INVALID` cho từng vector | L1, L4 |
| T-NFR-SEC-004d | Trường lạ trong slot `APPLY_SCHEDULE` (ví dụ `p_import_cap_w`); thiếu `expires_at`; `expires_at` vượt trần theo type | `REJECTED_INVALID` | L1, L4 |
| T-NFR-SEC-004e | Lệnh an toàn hóa có `seq` cũ hoặc chữ ký sai | `REJECTED_REPLAY`/`INVALID` (đường an toàn hóa không bỏ qua phần A) | L4 |
| T-FR-INT-018b | Gate M1: gửi lệnh tạm (`SET_PV_LIMIT` 50%, `SET_ESS_MODE = IDLE`) tới thiết bị có hoàn nguyên đã khai báo; cắt nguồn edge giữa chừng; chờ qua `expires_at` | Thiết bị tự về giá trị nền trong `revert_timeout_s` sau hạn; không đạt → driver mất cờ (a), lệnh M1 không persist_safe bị PDP và edge từ chối. Sau khi edge khởi động lại: `CTRL.REVERT_AFTER_RESTART` nếu còn lệch | L5 (HIL), commissioning |
| T-FR-INT-018c | `REMOTE_CONTROL_SUSPEND` khi đồng hồ `UNSYNCED` (IL-06) | Áp dụng; vòng điều khiển dừng; audit `safe_path = true`, `SKIPPED: IL-06` | L4, L5 (HIL) |
| T-FR-INT-018d | `REMOTE_CONTROL_SUSPEND` và `SET_ESS_P = 0` đến sau `max_latency_ms`; và khi đang có lệnh mức arbiter cao hơn | Áp dụng; audit ghi bước bỏ qua; `RESUME` trong cùng điều kiện bị `REJECTED_*` | L4, L5 (HIL) |
| T-FR-INT-018e | Lệnh M1 không persist_safe (nới giới hạn xuất, hạ reserve, hạ PV) tới thiết bị không có hoàn nguyên | PDP `DENIED: NOT_PERSIST_SAFE`; gửi thẳng tới edge (bỏ qua PDP trong test) → `REJECTED_UNSUPPORTED` | L4 |
| T-FR-INT-016b | Vào phiên `MAINTENANCE/COMMISSIONING_TEST`: không nhấn nút; nhấn sau 120 s; công tắc ở `LOCAL`; nhấn đúng | Chỉ trường hợp cuối mở phiên; trong phiên lệnh khác `COMMISSIONING_TEST` bị IL-10; thoát phiên → `REVERT_DEFAULT` + readback | L4, L5 |
| T-NFR-SEC-011 | Lệnh tới edge sau `expires_at` khi edge offline | `UNDELIVERED` ở cloud; không gửi lại | L4 |
| T-FR-EV-005 (P1) | Giới hạn EV có `validTo`; mất kết nối | Charger về TxDefaultProfile an toàn | L3, L5 |
| T-FR-INT-023 (P1) | Master 104 gửi setpoint khi cloud mất | Arbiter mức 4 áp; ACT_CON sau readback | L3, L5 |

### 11.4 Lab thiết bị tối thiểu [PROPOSAL]

Huawei SmartLogger (hoặc SmartLogger5000B) + 1 inverter SUN2000; EMMA + 1 hybrid; 2 công tơ 3 pha Modbus khác hãng; 1 PCS hoặc tủ BESS nhỏ của dòng được chọn; 1 charger AC OCPP 1.6J; module DI/DO và công tắc LOCAL/REMOTE; nguồn tải giả lập. Chi phí và nguồn mua [UNKNOWN] (Q-E-15).

---

## 12. Truy vết tính năng và yêu cầu

| Mục trong 07 | Tính năng (03) | Yêu cầu (04) |
|---|---|---|
| §2 Nguyên tắc, §2.1 hai mặt phẳng | F-SEC-05, F-INT-23 | FR-INT-013, NFR-SEC-002, NFR-SEC-018 |
| §3 Arbiter, chủ vòng | F-OPT-01, F-OPT-02, F-GRID-04, F-GRID-05, F-GRID-06 | FR-GRID-004…006 |
| §4.3 Tín hiệu an toàn | F-BESS-18, F-GRID-13, F-SEC-08 | FR-GRID-008, NFR-SEC-010 |
| §5.1 Modbus | F-INT-04 | FR-INT-004 |
| §5.2 SunSpec | F-INT-05 | FR-INT-005 |
| §5.3 CAN | F-INT-15 | FR-INT-022 |
| §5.4 MQTT, §7 telemetry | F-INT-08, F-MON-01 | FR-INT-008, NFR-DATA-002, NFR-DATA-003 |
| §5.7 IEC 104 | F-INT-16, F-GRID-12 | FR-INT-023, FR-GRID-013 |
| §5.9 OCPP | F-EV-02…F-EV-06, F-EV-10 | FR-EV-002…006, FR-EV-010 |
| §5.6, §5.8, §5.10 giao thức P2 | F-INT-18, F-OPT-20 | FR-INT-029 |
| §5.11 Cloud hãng | F-MON-02, F-INT-13, F-INT-14 | FR-INT-021, FR-INT-028 |
| §6.1 Edge, §6.15 phần cứng | F-INT-01 | FR-INT-001 |
| §6.2 Driver | F-INT-03, F-INT-06 | FR-INT-003, FR-INT-006 |
| §6.6 Vòng cục bộ | F-OPT-03, F-BESS-10 | NFR-PERF-006, NFR-REL-003, NFR-REL-007 |
| §6.7 Store-and-forward | F-INT-09 | FR-INT-009, NFR-DATA-001 |
| §6.8 Đồng hồ | F-INT-10 | FR-INT-010 |
| §6.13 Config/OTA | F-INT-11, F-INT-12 | FR-INT-011, FR-INT-012 |
| §6.14 Danh tính | F-INT-02 | FR-INT-002, NFR-SEC-003 |
| §6.16 Sức khỏe edge | F-MON-07 | — |
| §8 Lệnh | F-INT-07, F-SEC-07, F-SEC-14, F-BESS-04…07, F-PV-03, F-EV-05 | FR-INT-007, NFR-SEC-004, NFR-SEC-011, NFR-PERF-005 |
| §9 Commissioning | F-INT-25…F-INT-29, F-ORG-05 | FR-INT-015…020 |
| §11 Kiểm thử | F-INT-24 | FR-INT-014 |
| §11.3 Ca kiểm thử | — | `T-<FR id>` cho 12 |

Mã đề xuất tạm của ghi chú E (`PR-E-01`…`PR-E-18`) đã được 03/04 hấp thụ thành các mã trên; ánh xạ chi tiết thuộc [12](12-traceability-matrix.md).

---

## 13. Câu hỏi mở và rủi ro chuyển cho 13

Mã `Q-E-xx` là mã tạm; người viết [13](13-open-questions-and-risks.md) cấp `Q-NN`/`R-NN`.

### 13.1 Câu hỏi mở

| Mã tạm | Câu hỏi | Ảnh hưởng | Cách kiểm chứng |
|---|---|---|---|
| Q-E-01 | Bảng điểm IEC 104, CA/IOA, cấp điều độ, ngưỡng công suất, chu kỳ, dự phòng, bảo mật theo QĐ 1570 và từng Công ty Điện lực | Phạm vi F-INT-16 | Lấy văn bản QĐ 1570; hỏi 1–2 PC; xin hồ sơ một dự án đã đấu nối (K G-13) |
| Q-E-02 | Điều độ có chấp nhận "bật tắt phát ngược" bằng logger/phần mềm, hay bắt buộc rơ-le riêng? Hạ áp có cần thiết bị chống phát ngược không? | DO của edge, trách nhiệm pháp lý | Như trên |
| Q-E-03 | Register map chính thức Sungrow Logger1000/EMS300CP/SH và cách bật EMS mode ghi được | Driver thứ 5 | Kênh đối tác Sungrow VN; lab |
| Q-E-04 | SmartLogger/EMMA: tập thanh ghi lộ ra, watchdog cho lệnh remote, số kết nối tối đa | Fallback an toàn | Tài liệu Huawei bản mới; lab |
| Q-E-05 | Thanh ghi điều khiển nào ghi vào NVM (Huawei, Sungrow, Victron, tủ BESS); giới hạn số lần ghi | `persist`, mòn flash | Hỏi hãng |
| Q-E-06 | Victron Mode 2: timeout setpoint khi mất master; register list chính thức | Driver Victron | Tài liệu Victron |
| Q-E-07 | SunSpec model 715 là gì; trạng thái hiện hành của 802–805; sentinel 0x8000 | Bảng §5.2 | Định nghĩa model trên GitHub SunSpec |
| Q-E-08 | OCPP 2.1 DER control dùng được cho kênh EMS → CSMS không | Kiến trúc EV khi có CPO | Đọc spec OCPP 2.1 |
| Q-E-09 | Tủ BESS phổ biến ở VN có Modbus TCP northbound với P/Q/mode, CCL/DCL không; có cung cấp map theo hợp đồng không | Driver thứ 4 | Phỏng vấn nhà phân phối/EPC; NDA |
| Q-E-10 | Hạn mức chính thức của Growatt V1, Deye, Solis | Định cỡ connector | Tài khoản developer |
| Q-E-11 | SMA GridControl API làm được gì, ai được cấp | Đường ghi SMA | developer.sma.de |
| Q-E-12 | Giấy phép OpenEMS (EPL-2.0 và AGPL-3.0 theo module); thư viện IEC 104/61850/OCPP/Modbus dùng trong sản phẩm đóng | ADR runtime edge (chặn) | Pháp lý; đọc LICENSE từng module (K R-21) |
| Q-E-13 | Khối lượng thực tế sau nén/deadband cho site C&I điển hình | Định cỡ buffer, băng thông 4G | PoC site thật |
| Q-E-14 | Huawei OAuth Connect: endpoint, grant, thời hạn token, hạn mức | F-INT-14 | Tài khoản installer + tài liệu |
| Q-E-15 | Ứng viên phần cứng edge, BOM, có TPM; chi phí lab thiết bị | F-INT-01, §11.4 | RFQ 2–3 nhà cung cấp |
| Q-E-16 | Thị phần thiết bị ở site C&I mục tiêu tại VN (Huawei, Sungrow, Deye/Solarman, Growatt, Solis, tủ BESS cụ thể) | Thứ tự driver | Khảo sát installer (K G-07, G-08) |
| Q-E-17 | Security Whitepaper OCPP 1.6J Ed.4 (02/2026) có đổi yêu cầu profile không | F-EV-03 | Đọc tài liệu OCA |

### 13.2 Rủi ro

| Mã tạm | Rủi ro | Hậu quả | Giảm thiểu |
|---|---|---|---|
| R-E-01 | Map Modbus không công bố hoặc đổi theo firmware | Driver sai, dữ liệu sai dấu/scale | Driver theo dải firmware; fingerprint; xác minh map khi commissioning; hợp đồng cung cấp map |
| R-E-02 | Lệnh ghi "không tác dụng" hoặc bị native âm thầm đè | Kế hoạch không thực thi, khách mất tiền | Readback bắt buộc; theo dõi đáp ứng; `FAILED_NO_EFFECT`; phát hiện điều khiển ngoài (F-ALM-22) |
| R-E-03 | Thiết bị không có watchdog setpoint | Setpoint treo khi edge chết | `requires_native_fallback`; chỉ đổi chế độ native; test F-INT-28 |
| R-E-04 | Mòn NVM do ghi setpoint chu kỳ | Hỏng thiết bị | `persist` trong driver; `min_write_interval_ms`; ghi khi đổi |
| R-E-05 | Hãng đổi chính sách cloud API (ví dụ Huawei 09/2025) | Mất dữ liệu site chỉ giám sát | Cảnh báo `AUTH_FAILED`; runbook cấp lại quyền; khuyến nghị edge |
| R-E-06 | Yêu cầu điều độ (104) chưa rõ | Không nhận được site trung áp bán dư | P1 có điều kiện; dùng slave 104 của logger/gateway trong lúc chờ |
| R-E-07 | Xung đột master Modbus với SCADA/công cụ của installer | Mất dữ liệu, lệnh lỗi | Edge là connection owner; xuất lại qua Modbus TCP server; chế độ MAINTENANCE khi installer làm việc |
| R-E-08 | Giấy phép OpenEMS/thư viện giao thức không hợp với sản phẩm đóng | Phải viết lại edge | Giữ hợp đồng §7–§8 độc lập runtime; quyết định sau ý kiến pháp lý |
| R-E-09 | Kênh cloud riêng của dongle/logger hãng vẫn hoạt động song song | Điều khiển ngoài, lộ dữ liệu | Chính sách giữ/chặn kênh cloud hãng do chủ site chọn (F-SEC-17) |
| R-E-10 | Thứ tự driver MVP sai so với thị phần thực | Không phục vụ được khách đầu | Q-E-16 trước khi chốt lab |

### 13.3 Vấn đề gửi người viết khác

| Mã | Gửi | Vấn đề |
|---|---|---|
| X-07-01 | 05 | Hai lớp `ess_controller`, `vendor_controller` (§4.1) chưa có trong `PointDefinition.class`; quyết định thêm hay gộp |
| X-07-02 | 05, 06 | Trường `sent_at` và `limits` trong envelope (§8.2); trạng thái readback `UNSUPPORTED`; `tracking_state` (§8.5) |
| X-07-03 | 06 | Kênh ack lô telemetry: dùng `down/config` hay thêm `down/ack` (§7.1) — nếu thêm phải sửa R-12 qua ADR |
| X-07-04 | 06 | ADR runtime edge (OpenEMS hay tự xây), chặn bởi Q-E-12 (§6.1) |
| X-07-05 | 10 | Chốt phương pháp chuẩn hóa JSON trước khi ký (đề xuất JCS); xác thực lệnh `GRID_OPERATOR` trên conduit 104 (§8.9) |
| X-07-06 | 09 | Hiển thị "Đã gửi, thiết bị không cho đọc lại"; nhãn "Mô phỏng" cho site sandbox; trạng thái `tracking_state` |
| X-07-07 | 11 | Lab thiết bị §11.4 và driver thứ tự §10.10 là tiền đề Gate M1/M2 |
| X-07-08 | 05, 08 | Envelope `APPLY_SCHEDULE` (§8.3) dùng đúng trường `PlanSlot` của 05. 08 (§5.5, §11) dùng `soc_floor`/`soc_ceiling`/`soc_target_end` theo slot, 05 không có. 05 quyết định: thêm `soc_floor_pct`/`soc_ceiling_pct` vào `PlanSlot` (07 sẽ thêm vào envelope) hoặc 08 đổi sang `soc_target_pct` + sàn do edge tính — **Đã đóng vòng sửa:** 05 thêm `soc_floor_pct`/`soc_ceiling_pct` (tùy chọn) vào `PlanSlot`; `soc_target_end` của 08 = `soc_target_pct`. |
| X-07-09 | 10, 04 | Đường "an toàn hóa" tại edge (§8.7) là bản đối ứng của PDP-15; danh sách type an toàn hóa phải nằm trong config ký và trùng PDP-15. Thuộc tính `persist_safe` cho lệnh M1 (§8.1, §8.6) cần một quy tắc PDP tương ứng ở 10 và tiêu chí chấp nhận ở 04 (FR-SEC-016 hiện chỉ áp M2) |
| X-07-10 | 10 | 10 §12.2 ghi `MAINTENANCE` nhả kết nối ghi; 07 §9.4 thêm trạng thái con `MAINTENANCE/COMMISSIONING_TEST` giữ kết nối ghi chỉ cho `COMMISSIONING_TEST` trong phong bì test và cách xác nhận có mặt bằng nút trên edge (Phase 1, không cần HMI). 10 §12.2 cần thêm dòng này |

---

## 14. Thay đổi so với ghi chú E và nghiên cứu FusionSolar

| Chủ đề | Trước | Nay | Lý do |
|---|---|---|---|
| Thứ tự arbiter | Ghi chú E: 6 mức (native > giới hạn site > điều độ > operator > lịch > mặc định) | 12 mức K R-07; giám sát an toàn edge đặt trên lệnh điều độ | Khi mất `MTR_POC` không thể tuân lệnh lưới; fallback an toàn hơn |
| Topic MQTT | `ems/v1/{tenant}/{site}/{edge}/…` | `ems/v1/{edge_id}/up/…` và `…/down/…` | K R-12: ACL đơn giản, không lộ tenant, edge chuyển site không đổi topic |
| Dấu Q | Q > 0 = phát (quy ước máy phát) áp chung | Q cùng hướng với P của từng điểm | K R-02 |
| Chữ ký lệnh | Tùy chọn (V1) | Bắt buộc trước Gate M2 | K R-11 |
| IEC 104 | P0 cho V1 C&I trung áp | P1 có điều kiện | K R-10 |
| Buffer | ≥ 7 ngày | Cứng 7 ngày, mục tiêu 30 ngày, 1 s vòng 7 ngày | K R-13 |
| OpenEMS | "EPL-2.0" | Giấy phép UNKNOWN, chặn ADR | K R-21 |
| Huawei cổng/unit ID | Báo cáo FS: 6607 là cổng chính, unit 1 | Thử cả 6607/502 và unit 0/1 khi khám phá; nguồn cộng đồng, FACT Med | Ghi chú FS `source_code_clients.md` đính chính mặc định hiện tại của huawei_solar là 502/unit 0 |
| Huawei 47086 | Báo cáo FS liệt kê cùng 32080/37113/37760 | FACT Low, cấm cho driver `VERIFIED_*` | Cách dùng điều khiển chỉ có từ cộng đồng (EL-063) |
| QĐ 1570 "≥ 64 kbps, ≤ 125 ms" | Nêu như tham số mạng | Chỉ là tóm tắt vendor, không dùng làm NFR | K §4 |
| Thanh ghi diễn đàn | FACT | FACT Low "cộng đồng báo cáo", cấm vào driver `VERIFIED_*` | K §4 |
| Edge (so với FusionSolar cũ) | Giám sát trước, edge tùy chọn; lấy mẫu 1–5 phút | Edge bắt buộc ở site có lệnh; lấy mẫu 1 s tại edge, cloud 5 s/60 s/300 s | Vòng ≤ 2–5 s và cloud hãng là pull 5 phút có hạn mức (§3.4, §5.11); K §6 #13, #19 |
| Dấu lưới (so với FusionSolar cũ) | Lưới + = xuất | Lưới + = nhập | K R-01; C §3.2 |

---

## 15. Danh sách nguồn dùng trong tài liệu

Mọi URL dưới đây xuất hiện trong kết quả tìm kiếm của các agent hoặc trong nghiên cứu FusionSolar trước; không URL nào được mở toàn văn trong lượt này. Người viết [14](14-source-register.md) cấp mã `S-xxx`.

**Modbus, SunSpec, CAN**
- https://docs.elipse.com.br/documents/en-us/driver/modbus/latest/modbus_appendix_max_limit_block_size.html
- https://www.se.com/be/en/faqs/FA252887/
- https://docs.chipkin.com/articles/modbus-data-types-byte-order-reference/
- https://industrialmonitordirect.com/blogs/knowledgebase/modbus-32-bit-data-register-mapping-and-endianness-guide
- https://www.mikrocontroller.net/attachment/216048/Modbus_RTU_PROTOCOL.pdf
- https://industrialmonitordirect.com/blogs/knowledgebase/modbus-rtu-character-time-calculating-the-35-character-timeout
- https://github.com/SolarNetwork/solarnetwork/wiki/SunSpec-model-discovery
- https://community.victronenergy.com/t/sungrow-inverters-and-sunspec/57195
- https://sunspec.org/sunspec-modbus-700-series-der-information-models-are-now-approved/
- https://files.sma.de/downloads/SunSpecModbus-TI-en-11.pdf
- https://manuals.sma.de/ennexOS/en-US/14259660939.html
- https://sunspec.org/wp-content/uploads/2025/01/SunSpec-Alliance-Specification-Energy-Storage-ModelsD4rev0-1.pdf
- https://www.slideserve.com/chaim/sunspec-alliance-overview-storage-standards-development-program
- https://sunspec.org/product-certification-registry
- https://www.cooperative.com/programs-services/bts/Documents/Emerging%20Priorities%20for%20Energy%20Research%20Day%20-%20Oct%202018/IEEE%201547-2018%20-%20Vartanian%20(NRECA-APA-ResearchDay-20181031).pdf
- https://sunspec.org/communication-interface-defects-revealed-inul-1741-sb-certified-inverters/
- https://akkudoktor.net/uploads/short-url/dwFYBPwjnfia9tSuhUopj9uGX2u.pdf
- https://community.victronenergy.com/t/connect-diy-bms-via-can-to-cerbo-gx-eigenes-bms-via-can-mit-cerbo-gx-verbinden/37102
- https://akkudoktor.net/t/pylontech-bms-mit-sma-sunny-island/18019
- https://github.com/dfch/BydCanProtocol
- https://manual-sofar.eniris.be/en/Controller/Devices/PV-hybrid-and-battery-inverters/Ampowr

**MQTT, OPC UA, IEC 61850, IEC 104, DNP3**
- https://www.emqx.com/en/blog/sparkplug-3-0-advancements-and-formalization-in-mqtt-for-iiot
- https://docs.chariot.io/x/S4SzBw
- https://support.hms-networks.com/hc/en-us/articles/36458732970386-Is-the-the-Crimson-Sparkplug-B-implementation-compliant-with-the-spec
- https://www.emqx.com/en/blog/mqtt-message-expiry-interval
- https://docs.solace.com/API/MQTT-v50-Prtl-Conformance-Spec/mqtt-v50-C-summary-new-features.htm
- https://opcfoundation.org/wp-content/uploads/2026/03/OPCF-Energy-Initiative.pdf
- https://softwaretoolbox.com/resources/what-is-iec61850
- https://scc-ccn.ca/standardsdb/standards/2048725
- https://infosys.beckhoff.com/content/1031/tf6500_tc3_iec60870_5_10x/984040459.html
- https://kb.mervis.info/doku.php/en:mervis-ide:35-help:023-server-communication-protocols:010-iec-60870-5-104-server
- https://wiki.elseta.com/books/the-vinci-software/page/iec-60870-5-104
- https://www.advantech.com/vi-vn/resources/industry-focus/quyet-dinh-1570qd-evn-dien-mat-troi-mai-nha-dieu-can-biet (vendor có lợi ích)
- https://vjol.info.vn/tctbgd/article/view/121843
- https://www.dnp.org/ieee-releases-18152-standard-for-der-communications
- https://restservice.epri.com/publicdownload/000000003002015355/0/Product

**OCPP, OpenADR, IEEE 2030.5**
- https://openchargealliance.org/ocpp-2-1-is-now-available/
- https://openchargealliance.org/protocols/open-charge-point-protocol
- https://openchargealliance.org/?p=159286
- https://www.trialog.com/?p=11328
- https://codibly.com/news-insights/8-features-ocpp-2_1
- https://www.bender.de/docs/charge-controller/OCPP/ocpp-smart-charging/
- https://developer.easee.com/docs/ocpp-smart-charging
- https://www.midapower.com/news/strategic-comparison-of-ocpp-1-6j-vs-2-0-1-for-commercial-charging-operators/
- https://www.openadr.org/assets/OpenADR%20Webinar%20Nov%202023%20-%20From%202.0%20to%203.0.pdf
- https://www.openadr.org/assets/OpenADR%20AR25.pdf
- https://ecommercenews.co.nz/story/openadr-3-0-certification-marks-milestone-in-energy-sector
- https://standards.ieee.org/content/dam/ieee-standards/standards/web/documents/presentations/smart_energy_slides.pdf
- https://www.qualitylogic.com/wp-content/uploads/2021/07/Data-Sheet-DER-Workshop.pdf

**Hãng, controller, cloud**
- Huawei (nghiên cứu FusionSolar trước): https://support.huawei.com/enterprise/en/doc/EDOC1100358266/b9df65c2/monitoring ; https://support.huawei.com/enterprise/en/doc/EDOC1100379184/7a471100/control-apis ; https://support.huawei.com/enterprise/en/doc/EDOC1100492747 ; https://github.com/wlcrs/huawei_solar ; https://github.com/evcc-io/evcc/discussions/1928 ; https://forum.iobroker.net/assets/uploads/files/1699119419919-solar-inverter-modbus-interface-definitions-v5.pdf ; https://pypi.org/project/pyhfs/ ; https://help-center.meteocontrol.com/en/vcom-cloud/latest/huawei-fusionsolar-api-1
- https://solar.huawei.com/admin/asset/v1/pro/view/bb9458d9373d4502912378db3cbc7f2d.pdf
- https://www.photomate.eu/smartlogger5000b
- https://help.autarco.com/en/hardware/why-am-i-still-exporting-while-i-have-set-my-pv-system-to-zero-export-
- https://forum.iobroker.net/post/1270320
- https://raspberry.tips/raspberrypi-tutorials/huawei-sun2000-home-assistant-emma-solar-dashboard
- https://solar.huawei.com/en/professionals/all-products/EMMA/specs
- https://www.heima24.de/shop/images/products/media/db-huawei-emma02.pdf
- https://community.homey.app/t/app-pro-huawei-fusionsolar-manager/153353?page=16
- https://community.openhab.org/t/sveasolar-powershifter-pv-inverter-huawei/164046
- https://community.openhab.org/t/reading-data-from-huawei-inverter-sun-2000-3ktl-10ktl-via-modbus-tcp-and-rtu/87670?page=5
- https://community.homey.app/t/modbus-register-logger-1000-sungrow/126405
- https://forum.cleanenergyreviews.info/t/logger1000-as-modbus-tcp-server/3181
- https://www.loxforum.com/forum/german/software-konfiguration-programm-und-visualisierung/424167-sungrow-sh10rt-wr-modbusparameter
- https://forum.iobroker.net/post/936007
- https://www.sungrowpower.com/mal/en/products/c-i-energy-storage-system/st255cs-2h
- https://docs.eniris.be/da/Controller/Devices/Cloud/ISolarCloud
- https://community.home-assistant.io/t/sungrow-isolarcloud-integration-custom-hacs-sensors-optional-charge-discharge-control/1017858
- https://developer.sma.de/sma-apis
- https://developer.sma.de/sma-sandbox-apis
- https://solytic.com/knowledge/set-up-api-access-sma-monitoring-api/
- https://usservice.solisinverters.com/support/solutions/articles/73000661192-solis-api-troubleshooting
- https://projects.bentasker.co.uk/gils_projects/issue/utilities/telegraf-plugins/9.html
- https://github.com/hultenvp/soliscloud_api
- https://www.home-assistant.io/components/growatt_server/
- https://mirrors.edge.kernel.org/CPAN/modules/by-module/Config/KORNIX/DeyeCloud-Client-0.0.2.readme
- https://community.home-assistant.io/t/deye-cloud-integration/813153
- https://communityarchive.victronenergy.com/questions/95889/multipluss-ii-is-external-control-ess-mode-2-or-3%EF%B9%96childToView=102991.html
- https://mcpservers.org/en/servers/lubosstrejcek/victron-tcp
- https://www.meteocontrol.com/fileadmin/Daten/Dokumente/EN/Produkte/On_Site/blue_Log_XM_XC/Data_sheet/blue_Log_XM_XC_Modbus_Power_Control_license_blue_Log_XC_data_sheet_LastMod-2026-01-27_en.pdf
- https://www.solar-log.com/fileadmin/user_upload/documents/Datenblaetter/en_GB/Komponenten/Kommunikation/SolarLog_Datasheet_Modbus_TCP_PM_EN.pdf
- https://knowledge-center.solaredge.com/sites/kc/files/se-one-controller-commercial-and-industrial-datasheet-eng.pdf
- https://ampowr.com/energy-management-system-ems/
- https://ampowr.com/hoge-duin-hotel-enhances-energy-efficiency-with-ampifarm-peak-shaving/
- https://www.infinitepowerht.com/what-is-energy-management-system-ems-and-its-functions.html (chỉ định nghĩa chung, FACT Low)
- https://www.infinitepowerht.com/commercial-energy-storage-solutions.html
- https://www.infinitepowerht.com/1000-kwh-battery-outdoor-container-ess.html
- https://www.infinitepowerht.com/261kwh-522kwh-hybrid-energy-storage-system.html

**Edge, thời gian, kiến trúc**
- https://openems.github.io/openems.io/openems/latest/edge/architecture.html
- https://openems.github.io/openems.io/openems/latest/coreconcepts.html
- https://openems.github.io/openems.io/openems/latest/edge/scheduler.html
- https://github.com/OpenEMS/openems/releases
- https://timebeat.app/blog/ptp-vs-ntp
- https://sunplus.atlassian.net/wiki/x/JQB1eQ
- https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11411391

---

*Hết tài liệu 07. Mọi số liệu tính toán trong §5.1.4 và §6.7 là ước tính ([INFERENCE]), phải đo lại trong PoC (Q-E-13).*
