# K — Phản biện bằng chứng, vòng 1 (Evidence Judge / Red Team)

[← Mục lục](../index.html) · [00 Tóm tắt](../00-executive-summary.html) · [04 Yêu cầu](../04-business-requirements.md) · [05 Domain](../05-domain-model.html) · [06 Kiến trúc](../06-system-architecture.html) · [07 Tích hợp](../07-device-integration.md) · [08 Tối ưu](../08-energy-optimization.md) · [10 An toàn](../10-security-and-reliability.md) · [11 Lộ trình](../11-mvp-and-roadmap.html) · [13 Rủi ro](../13-open-questions-and-risks.md) · [14 Nguồn](../14-source-register.md) · [15 Mô phỏng](../15-simulators-and-messaging.md)

- Người viết: Agent K (Evidence Judge / Red Team). Ngày: 2026-10-10. Trạng thái: vòng 1. File này **ràng buộc** mọi người viết tài liệu 00–14: khi ghi chú của agent mâu thuẫn với "Danh sách quyết định thống nhất" (§6), §6 thắng.
- Phạm vi đã đọc toàn văn: `A-market-boundary.md`, `B-competitors.md`, `C-energy-domain.md`, `E-device-integration.md`, `F-data-analytics.md`, `G-optimization.md`, `H-ux-research.md`, `I-security-reliability.md`, `_conventions.md`. Không có ghi chú D trong thư mục `notes/`.
- **Giới hạn phương pháp.** Hạn mức WebSearch chung của lượt chạy (200 truy vấn) **đã hết** trước khi Agent K bắt đầu. Truy vấn kiểm chứng đầu tiên trả về "web search budget is used up". Vì vậy K **không chạy lại được** 15–25 truy vấn kiểm tra chéo như kế hoạch. K đã làm ba việc thay thế:
  1. Đối chiếu chéo giữa các ghi chú (cùng URL, cùng con số, cùng nhãn).
  2. Đối chiếu với nghiên cứu FusionSolar trước (`docs/research/fusionsolar/`) bằng grep. Ví dụ: đã xác nhận `demo_observations.md` dòng 93 có release note 2026-03-31 "SmartEMO hỗ trợ demand charge theo TOU" (claim G #32). Đã xác nhận `features_editions.md` nêu **cả** SmartLogger5000B **và** SmartMGC5000B là gateway C&I (liên quan X-E-08).
  3. Tính lại mọi phép tính số học trong ghi chú (§3, cột "Đã tính lại").
- Hệ quả: các phán quyết bên dưới dựa trên **tính nhất quán, chất lượng nguồn đã ghi và logic**. K không xác nhận được nội dung URL nào. Các claim pháp lý và tiêu chuẩn quan trọng vẫn cần một **lượt kiểm chứng riêng** (§5, mục "Kiểm chứng bắt buộc").

---

## 1. Tổng quan

**Đánh giá chung.** Tám ghi chú đều theo đúng quy ước nhãn. Hầu hết FACT có URL và ghi "(qua kết quả tìm kiếm)". Các agent hết hạn mức tìm kiếm (F một phần; G, H, I toàn bộ) đã tự hạ nhãn cho phần kiến thức nền. Chất lượng như vậy là tốt. Không thấy URL có dấu hiệu bịa: URL đều có cấu trúc thật của các domain đã biết, và nhiều URL được hai agent tìm thấy độc lập. Tuy vậy, **không URL nào được K mở**, nên mức tin cậy tối đa của mọi FACT mới vẫn là "snippet tìm kiếm".

**Vấn đề hệ thống (theo mức nghiêm trọng).**

1. **High — Mâu thuẫn hợp đồng dữ liệu giữa các ghi chú.** Các điểm chưa thống nhất: đơn vị lưu trữ (C/F dùng kW/kWh, E dùng W/Wh); tên và vai trò timestamp (C/F/H dùng `ts_device` làm thời gian chuẩn, E dùng `ts` của edge); nhãn khoảng tổng hợp (C/F dùng nhãn cuối khoảng `(t−5′, t]`, còn TimescaleDB mặc định nhãn đầu khoảng); bộ mã quality (E, F, C mỗi agent một bộ, `STALE` mang hai nghĩa); dấu của Q; cấu trúc topic MQTT (E có tenant/site trong topic, I chỉ có edge-id). Nếu không chốt, tài liệu 05/06/07 sẽ mâu thuẫn. Phán quyết ở §2.
2. **High — Thứ tự ưu tiên của arbiter có ba phiên bản** (E §3.1, G §3.8, I §3.7.7). Phán quyết ở §2.
3. **High — Phạm vi MVP về điều khiển chưa thống nhất.** A, G và E coi điều khiển BESS là P0. I đề xuất MVP chỉ giám sát cộng lịch native trước, và chỉ bật setpoint khi đủ bộ an toàn lệnh P0. Phán quyết ở §2.
4. **Med — Cơ sở tính giá hai thành phần.** A ghi "công suất đăng ký", C ghi "Pmax đo 30 phút". G đã nêu mâu thuẫn này nhưng chưa ai giải. Không kiểm chứng được trong lượt này, nên phán quyết là mô hình hóa cả hai và hạ nhãn.
5. **Med — Nhãn FACT cho câu tổng quát hóa.** Ví dụ: "mọi sản phẩm", "mọi hãng", "thống trị", "bắt buộc pháp lý cho mọi site". Đây là suy luận từ một mẫu nhỏ. Danh sách hạ cấp ở §4.
6. **Med — Mã định danh.** G dùng `FR-OPT-001…`, I dùng `NFR-SEC-001…` ngay trong ghi chú. Các mã này có thể trùng với mã do người viết 04 cấp. Phán quyết: mọi mã FR/NFR trong `notes/` là **tạm thời**, và người viết 04 sẽ đánh số lại.
7. **Med — Thiếu chủ đề.** Quy trình O&M/ticket/work order cho persona P3 (người dùng hằng ngày P0) gần như chưa được nghiên cứu. Ngoài ra còn thiếu commissioning end-to-end, mô hình kinh doanh/giá, chiến lược kiểm thử (simulator/HIL), và mô hình biểu giá M-TAR hợp nhất. Chi tiết ở §5.
8. **Low — Rủi ro AI-washing.** Không agent nào gọi luật cố định là AI. Một vài ô trong ma trận B ghi "V" cho "AI có mô tả cụ thể" dựa trên báo chí/tuyên bố của hãng. Các ô đó phải đổi thành `V*` (tuyên bố của hãng).

**Kiểm tra số học (đã tính lại, đều đúng):**
- A arbitrage: 3.398 − 1.190/0,9 = 2.076 đ/kWh; ×1.000 × 312 ≈ 648 triệu đ.
- G bảng §3.15.2: 3.058 / 1.868 / 1.225 / 460 / 511.
- G `c_deg` ≈ 556 đ/kWh xả.
- C ví dụ PF: 0,447. C `P_allow_rest` = 840 kW.
- F khối lượng: 35 mẫu/s/site; 3,02 M mẫu/ngày; 5,5 GB/site/năm nén. F tràn uint16 0,1 kWh sau ≈ 1,37 ngày; uint32 Wh sau ≈ 2,45 năm.
- E Modbus RTU: 1,146 ms/ký tự; khung 255 byte ≈ 292 ms. E buffer: 553 MB/ngày.

---

## 2. Phán quyết các mâu thuẫn

| # | Chủ đề | Các lập trường | Phán quyết | Lý do |
|---|---|---|---|---|
| R-01 | Quy ước dấu P | Nghiên cứu FS cũ: lưới + = xuất. C/E/F/G/H: lưới + = nhập, BESS + = xả | **Lưới + = nhập (mua), BESS + = xả, PV ≥ 0, tải/EV ≥ 0, máy phát ≥ 0.** `P_cons = P_grid + P_pv + P_bess + P_gen` | Năm agent đồng thuận. Khớp OpenEMS và OBIS A+. Mọi ngưỡng điều khiển (import cap, Pmax) thành số dương. Thay đổi so với hướng FS cũ đã được C giải thích (§3.2) |
| R-02 | Dấu Q | C: theo 4 góc phần tư công tơ (nhập cảm = Q1, dương). E: Q > 0 = phát vô công (quy ước máy phát), áp chung | **Q theo cùng hướng với P của từng điểm đo.** Lưới: Q > 0 = vô công **đi vào site từ lưới** (tải cảm, góc phần tư Q1). PV/PCS/máy phát: Q > 0 = **bơm vào thanh cái site**. Mỗi driver khai báo quy ước gốc | Nếu dùng quy ước máy phát cho công tơ POC trong khi P_grid dùng quy ước tải, PF tại POC sẽ sai dấu. Phán quyết này giữ nguyên tắc "dương = đi vào thanh cái site" của R-01 |
| R-03 | Đơn vị lưu trữ | C/F: kW, kWh (float64/numeric). E: W, Wh (int64 cho bộ đếm). H: hiển thị kW/kWh | **Telemetry thô và hợp đồng edge (point/command contract) dùng đơn vị SI gốc: W, Wh, var, VA, varh, kèm hậu tố đơn vị trong tên trường (`_w`, `_wh`). Bộ đếm năng lượng là int64 Wh. Tổng hợp, KPI, báo cáo và API công khai dùng kW/kWh với hậu tố `_kw`/`_kwh`. UI hiển thị theo bảng đơn vị của H §3.16** | Bộ đếm Wh nguyên tránh lỗi float (F §3.2). Lớp KPI dùng kW/kWh để khớp hóa đơn và người dùng. Hậu tố trong tên trường loại bỏ nhập nhằng. Đây là chuyển đổi duy nhất, chỉ xảy ra ở ranh giới raw→aggregate |
| R-04 | Timestamp | C/F/H: `ts_device`, `ts_edge_received`, `ts_ingested`; thời gian chuẩn = `ts_device` nếu đồng hồ thiết bị đáng tin. E: `ts` (edge, UTC ms, khóa chính), `ts_src`, `ts_ingest` | **Tên chuẩn: `ts` = thời điểm edge thu giá trị (UTC, ms), là khóa thời gian của dữ liệu polling. `ts_src` = thời điểm thiết bị cung cấp (tùy chọn), dùng làm thời gian chuẩn **chỉ** cho SOE/alarm và dữ liệu khoảng của công tơ khi `src_clock_state = SYNCED`. `ts_ingest` = thời điểm cloud ghi.** UI hiển thị "đo lúc" theo thời gian chuẩn đó | Đồng hồ thiết bị không đáng tin: Huawei dùng giờ địa phương (E F-33), Northbound lệch UTC. Với dữ liệu polling, thời điểm edge thu là thời điểm đo thực tế (sai số bằng độ trễ poll). Phán quyết này hợp nhất tên trường của C/F/H vào bộ tên của E |
| R-05 | Nhãn khoảng tổng hợp | C/F: nhãn **cuối khoảng**, `(t−5′, t]`. TimescaleDB `time_bucket`: nhãn đầu khoảng, `[start, end)` | **Khóa lưu trữ là `bucket_start` với khoảng nửa mở `[start, start+Δ)`, đúng mặc định của TimescaleDB. Delta năng lượng của bucket = R(mẫu tại hoặc ngay sau biên cuối) − R(mẫu tại hoặc ngay sau biên đầu). Export và UI luôn ghi cả đầu–cuối khoảng.** Driver chuyển dữ liệu nhãn cuối khoảng (load profile EVN) sang quy ước này khi ingest | Tránh tự viết bucketing trong CAGG và lỗi lệch một khoảng. Ý định của C/F (không mập mờ về biên) vẫn đạt được vì khoảng nửa mở được khai báo tường minh. **Thay đổi so với C §3.15 và F §3.2** (`ts_gauge` nhãn cuối, `interval_energy.bucket_end`) |
| R-06 | Bộ mã chất lượng | E: GOOD / UNCERTAIN_* / BAD_* (theo điểm). F: nguồn gốc + bitmask. C: MEASURED / INTERPOLATED / ESTIMATED / PARTIAL / MISSING / SUSPECT (KPI). H: F `STALE` (giá trị đóng băng) trùng nghĩa với UI "stale" (dữ liệu cũ) | **Ba tầng.** (1) Điểm thô tại edge và realtime: bộ mã của E. (2) Chuỗi lưu trữ và tổng hợp: hai trục của F (nguồn gốc + bitmask). (3) KPI: enum của C, ánh xạ từ nguồn gốc của F (CALCULATED → MEASURED nếu mọi đầu vào MEASURED). **Đổi tên `STALE` của F thành `FROZEN`.** `UNCERTAIN_STALE` của E giữ nghĩa "quá tuổi". UI dùng khái niệm riêng `freshness ∈ {LIVE, DELAYED, OLD, OFFLINE, NO_DATA}` (H §3.13) | Mỗi tầng giải một bài toán khác nhau. Cần bảng ánh xạ, không phải một bộ mã duy nhất. Đổi tên `STALE` loại bỏ trùng nghĩa |
| R-07 | Thứ tự ưu tiên của arbiter | E: native > giới hạn cứng site > điều độ > vận hành viên > lịch > mặc định. G: L0 an toàn > L1 watchdog > L2 tuân thủ lưới > L3 import cap > L4 backup > L5 DR > L6 peak > L7 EV > L8 kinh tế; lệnh tay chỉ trong L0–L4. I: native > E-stop > LOCAL > GRID_OPERATOR > watchdog > lệnh tay > DR > optimizer > mặc định | **Thứ tự chuẩn:** (1) bảo vệ native (BMS/PCS/rơ-le/E-stop cứng, ngoài phần mềm); (2) interlock tại chỗ (LOCAL/REMOTE, trạng thái E-stop, PCCC); (3) giám sát an toàn của edge (dữ liệu BMS/POC cũ, lệnh hết hạn, SOE, limit chain → trạng thái an toàn); (4) tuân thủ lưới (zero-export/giới hạn xuất, lệnh `GRID_OPERATOR`, chặn phát ngược); (5) trần nhập vật lý (MBA/hợp đồng); (6) dự phòng backup (cho phép xuống dưới mức khi cần giữ trần nhập, theo cấu hình của G); (7) lệnh tay của vận hành viên (có hạn, trong SOE); (8) cam kết DR/VPP (P2); (9) peak shaving theo demand; (10) cam kết EV; (11) lịch kinh tế (luật/optimizer); (12) chiến lược mặc định. Mức 1–6 cố định. Mức 8–11 cấu hình được theo site | Watchdog đặt **trên** lệnh điều độ, vì fallback của nó luôn an toàn hơn (P = 0 hoặc về giới hạn native), và khi mất công tơ POC thì không thể tuân thủ lệnh lưới. Lệnh tay đặt trên DR/kinh tế (cả E, G, I đều đồng ý ở điểm này). Phán quyết dùng mô hình "thu hẹp khoảng cho phép" của G §3.8 |
| R-08 | MVP có điều khiển không? | A D-09, G FR-OPT-003/004, E PR-E-01: điều khiển BESS P0. I X-I-07: phát hành giám sát + lịch native trước | **MVP gồm hai cổng (gate).** **Gate M1:** giám sát đa hãng; cấu hình và kiểm chứng chế độ **native** (giới hạn xuất, lịch TOU, capacity control của logger hãng) qua driver đã kiểm chứng, có readback. **Gate M2 (vẫn trong MVP):** edge của ta làm chủ vòng (`control_owner = EDGE`) và gửi setpoint/lịch envelope. M2 chỉ bật cho một site khi đã có đủ các NFR an toàn P0: lệnh có hạn, SOE, interlock, audit, MFA, ký lệnh, watchdog thiết bị hoặc `requires_native_fallback` đã xử lý | Giữ được giá trị của A/G (BESS cần lập lịch) mà vẫn tôn trọng điều kiện an toàn của I. Không site nào nhận setpoint từ xa khi chưa đủ điều kiện |
| R-09 | Ai chạy vòng nhanh (zero-export/import cap) | A: logger hãng **hoặc** edge của ta. E: edge bắt buộc ở site có điều khiển. G: `control_owner ∈ {NATIVE, EDGE}`, không chạy hai PI trên cùng biến | **Edge của ta bắt buộc ở mọi site mà nền tảng ghi lệnh. Vòng nhanh ưu tiên dùng controller native đã chứng nhận (SmartLogger, EMS tủ…); edge chỉ đặt tham số và giám sát. Edge chỉ tự chạy vòng khi native không có chức năng đó.** Site chỉ giám sát có thể dùng connector cloud của hãng, không cần edge | Ba lập trường tương thích nhau khi có cờ `control_owner`. Cloud API của hãng là pull 5 phút có hạn mức, nên không dùng được cho điều khiển (E F-23, F-36) |
| R-10 | IEC 60870-5-104 | A: P2 ("nếu cần"). E PR-E-09: P0 cho V1 C&I trung thế | **Điều kiện, P1:** bắt buộc trước khi nhận site trung áp **có bán điện dư** hoặc khi PC địa phương yêu cầu. MVP dùng slave 104 có sẵn của logger hãng (SmartLogger) hoặc gateway (Advantech) nếu có. Slave 104 trên edge của ta là P1 | Theo A #3, chỉ khoảng 287/28.254 hệ đăng ký bán dư, nên phần lớn site mục tiêu ban đầu không cần kết nối điều độ. Yêu cầu theo QĐ 1570 chưa đọc toàn văn (UNKNOWN) |
| R-11 | Ký lệnh tầng ứng dụng | E: `signature` tùy chọn (V1). I: P0 (JWS, `seq` đơn điệu, KMS) | **Bắt buộc (P0) trước khi bật Gate M2 cho bất kỳ site nào.** Gate M1 (ghi tham số native) cũng phải ký nếu đi qua edge | Lệnh có tác động vật lý. Broker có thể bị chiếm (I AC-03). Mức chi phí chấp nhận được |
| R-12 | Topic MQTT | E: `ems/v1/{tenant}/{site}/{edge}/…`. I: `ems/v1/<edge-id>/up/#` và `…/down/#`, ánh xạ tenant/site ở cloud | **Dùng mẫu của I:** `ems/v1/{edge_id}/up/{state\|telemetry/{stream}\|event\|backfill\|cmd-ack}` và `ems/v1/{edge_id}/down/{cmd\|config}`. QoS và retained theo bảng của E §3.5 | ACL đơn giản, chống wildcard. Edge chuyển site không phải đổi topic. Không lộ tenant trong topic. Nội dung từng topic vẫn theo E |
| R-13 | Store-and-forward tại edge | E: ≥ 7 ngày. F: 1 s giữ 7 ngày + buffer theo tần suất cloud ≥ 30 ngày. I: ≥ 7 ngày (có nhắc F 30) | **Buffer theo tần suất cloud ≥ 30 ngày (mục tiêu). NFR cứng: không mất dữ liệu khi mất mạng ≤ 7 ngày. Dữ liệu 1 s giữ vòng tròn 7 ngày tại edge** | Buffer theo tần suất cloud chỉ khoảng 45 MB/ngày (F), nên 30 ngày rẻ. NFR cứng 7 ngày khớp cửa sổ tính lại của CAGG |
| R-14 | Phân hạng lệnh | H: A/B/C/D. I: C0–C4 | **Dùng C0–C4 của I.** Ánh xạ: H-A → C0; H-B → C1; H-C → C2/C3 theo bảng I §3.7.4; H-D → C4 (không có API) | I chi tiết hơn và đã gắn với phê duyệt hai người |
| R-15 | Chế độ BESS | E `SET_ESS_MODE`: SELF_CONSUMPTION, PEAK_SHAVING, TOU_SCHEDULE, BACKUP_HOLD, IDLE. G slot mode: PV_SURPLUS_CHARGE, GRID_CHARGE_TO_TARGET, PEAK_DISCHARGE, GRID_SETPOINT, HOLD, IDLE | **Hai từ vựng, hai tầng.** `site_strategy` (bộ của E, chọn chiến lược chung của site). `slot_mode` (bộ của G, chỉ xuất hiện trong envelope của `APPLY_SCHEDULE`). Không trộn hai bộ | Tầng 2/3 phát lịch theo slot. Lệnh thủ công chọn chiến lược |
| R-16 | Giá hai thành phần | A §3.4.4: tính theo **công suất đăng ký**, trả cả khi không dùng. C #3 và G #10: **Pmax đo** theo chu kỳ tích phân 30 phút | **Chưa quyết.** Hạ cơ sở tính xuống `[UNKNOWN]` ở cả A và C. Giữ `[FACT, Med]` cho câu "chu kỳ tích phân hiện nay là 30 phút" (có trích nguyên văn). M-TAR hỗ trợ `demand_basis ∈ {MEASURED_MAX, CONTRACTED}`, mặc định tắt. Peak shaving theo demand là P1 | Hai nguồn báo chí khác nhau. K không kiểm chứng được (hết hạn mức). Cách hiểu hợp lý: công suất đăng ký và Pmax đo có thể cùng xuất hiện (đăng ký + phạt vượt), nhưng đây là INFERENCE |
| R-17 | Tình trạng demand charge ở VN | A #6 `[FACT]`: "C&I VN hiện chưa trả phí công suất". Cũng A: thí điểm thanh toán thật từ 07/2026 | **Hạ xuống `[INFERENCE]`:** "đại đa số C&I chưa trả; khách thí điểm ≥ 200.000 kWh/tháng **có thể** đã trả từ 07/2026 (UNKNOWN)" | Câu FACT mâu thuẫn với lịch thí điểm do chính A trích |
| R-18 | Trang hạt giống InfinitePower | A #12, C #22, G #13 trích URL `what-is-energy-management-system-ems-and-its-functions.html` là FACT (qua kết quả tìm kiếm). B #20: URL **không xuất hiện** trong kết quả tìm kiếm của B | **Chỉ dùng URL này cho định nghĩa chung** ("EMS điều phối BMS và PCS; giám sát, lập lịch, chẩn đoán"), và chỉ khi có nguồn thứ hai đồng ý (Deye blog, C #21). Nhãn: `FACT, Low (snippet, một agent)`. **Không** gán tính năng cụ thể nào của InfinitePower cho trang này. Tính năng sản phẩm HT lấy từ trang sản phẩm (B L08–L13) | Hai agent thấy kết quả khác nhau. Không ai đọc toàn văn. Nguồn thứ hai giảm rủi ro |
| R-19 | Model Huawei công bố ≤ 2 s / ≤ 5 s | A, B, G: SmartLogger5000B (nhà phân phối Photomate). E: câu chữ nằm trên datasheet **SmartMGC5000B** (URL solar.huawei.com) | **Ghi "bộ điều khiển site C&I của Huawei (SmartLogger5000B/SmartMGC5000B)", kèm cả hai URL.** Đây là **số do hãng tự công bố**, dùng làm mục tiêu tham chiếu, không phải số đo độc lập | Nghiên cứu FS trước (`features_editions.md`) xác nhận cả hai model đều là gateway C&I. Model chính xác có câu chữ này chưa kiểm chứng |
| R-20 | Huawei "peak shaving chỉ ở kịch bản on/off-grid" | B #17 `[FACT]` + suy luận "phổ biến". G dùng làm ma trận chế độ | **Thu hẹp phạm vi:** ràng buộc này chỉ đúng với **manual LUNA2000-(107-215) C&I-Microgrid-SmartLogger3000** được trích. Không áp cho SmartLogger5000B on-grid hay SmartEMO | Mâu thuẫn với các claim khác cùng ghi chú: SmartLogger5000B có capacity control ≤ 5 s; thư viện `huawei_solar` có `set_capacity_control_periods` |
| R-21 | Giấy phép OpenEMS | B L44: repo có file EPL-2.0 **và** AGPL-3.0. E §3.14 và PR-E-16: "EPL-2.0" | **UNKNOWN, chặn ADR edge runtime.** Kiến thức nền của K (chưa kiểm chứng): Edge/Backend dùng EPL-2.0, UI dùng AGPL-3.0. ADR phải đọc file LICENSE từng module trước khi chốt. Không tái dùng UI OpenEMS khi chưa có ý kiến pháp lý | AGPL ở UI ảnh hưởng SaaS. E mới chỉ ghi một giấy phép |
| R-22 | Ngôn ngữ của Optimization Service | G: Python sidecar cho P1. Hướng cũ: Java/Spring | **Tầng 1 (edge) và tầng 2 (bộ sinh lịch luật, MVP) viết bằng Java. Tầng 3 (MILP/MPC, P1) được phép là sidecar Python sau hợp đồng JSON có version, *nếu* ADR-OPT chấp thuận.** Đây là ngoại lệ có chủ đích so với stack cũ, phải ghi rõ trong 06 | Không thêm runtime ở MVP. Sidecar chỉ có lý khi cần backtest/hệ sinh thái tối ưu |
| R-23 | Lịch cloud: "15 phút / 72 h" | A, G, H: FACT (handout Schneider). B L16: câu "cập nhật mỗi 15 phút" chỉ thấy ở một kết quả (Low–Med); 48 h so với 72 h mâu thuẫn | Nhãn `FACT, Low–Med, một nguồn, tài liệu ~2017`. Lựa chọn của ta (slot 15 phút, horizon 48 h, lịch dự phòng ≥ 48 h) là `[PROPOSAL]` độc lập, không phụ thuộc Schneider | Nguồn cũ, có mâu thuẫn nội bộ |
| R-24 | Ưu tiên của widget demand 30 phút | H-P08: P0. A D-12, C-P08, G FR-OPT-012: P1 | **Thanh "nhập hiện tại / trần nhập" và "xuất / giới hạn xuất" là P0. Đồng hồ demand theo cửa sổ biểu giá là P1**, tự bật khi biểu giá có thành phần demand | Khớp R-16. Không hiển thị chỉ số không áp cho phần lớn khách |
| R-25 | Lưu giữ audit lệnh và kế hoạch | F: audit ≥ 5 năm (audit điều khiển chờ 10). I: ≥ 12 tháng trực tuyến + 5 năm lưu lạnh. G: audit kế hoạch ≥ 2 năm | **Audit lệnh, phê duyệt, SOE và các phiên bản kế hoạch đã thực thi: trực tuyến ≥ 13 tháng, lưu trữ (WORM) ≥ 5 năm, hợp đồng có thể kéo dài tới 10 năm. Kế hoạch bị thay thế trước khi chạy: chỉ giữ tóm tắt + hash 30 ngày** | Tiết kiệm là cơ sở thanh toán ESCO/PPA. Bảo hành pin kéo dài nhiều năm. 13 tháng đủ so sánh cùng kỳ |
| R-26 | Nhãn mức cảnh báo | FS cũ: S1 Nghiêm trọng … S4 Cảnh báo. H: Khẩn cấp / Cao / Trung bình / Thông tin | **Dùng bộ nhãn của H**, là enum i18n duy nhất | "Cảnh báo" vừa là tên chung vừa là tên một mức (H #5, X-H07) |
| R-27 | Tên chế độ giới hạn lưới | A D-04: `ZERO_EXPORT`, `EXPORT_LIMIT_KW`, `EXPORT_ENERGY_SHARE`, `IMPORT_CAP_KW`. E: lệnh `SET_EXPORT_LIMIT` / `SET_IMPORT_LIMIT` | **Cấu hình site:** `export_mode ∈ {ZERO_EXPORT, EXPORT_LIMIT, EXPORT_ENERGY_BUDGET}` + `export_limit_w` + `import_cap_w`. `EXPORT_ENERGY_BUDGET` là P1, tham số mặc định 50% × E_pv đo tại `MTR_PV` theo kỳ tháng, cả hai đều `[UNKNOWN]` chờ văn bản gốc. **Lệnh** giữ tên của E | Cấu hình (trạng thái) tách khỏi lệnh (thay đổi tạm thời có hạn). Hậu tố đơn vị theo R-03 |

---

## 3. Vấn đề theo từng note

### 3.1 A — Thị trường & ranh giới

| Vấn đề | Mức | Sửa bắt buộc |
|---|---|---|
| Bảng chấm điểm §3.7: nhóm 1 (Monitoring) đạt 23 điểm, cao hơn nhóm 2 (19 + "kế thừa 1"), nhưng kết luận chọn nhóm 2. Thang điểm không có trọng số, và "kế thừa 1" là điểm cộng tùy ý | Med | Hoặc chấm "nhóm 1 + 2 (kết hợp)" thành một phương án, hoặc nêu trọng số (V × 2…) và giải thích vì sao V và khác biệt quan trọng hơn S/C/R. Kết luận giữ nguyên: nhóm 2 trên nền nhóm 1 |
| Phát hiện #6 gắn `[FACT]` cho "C&I VN hiện chưa trả phí công suất" trong khi lịch thí điểm cho thanh toán thật từ 07/2026 | Med | Hạ xuống INFERENCE (R-17) |
| §3.4.4 "thành phần công suất tính theo **công suất đăng ký**" mâu thuẫn với C #3 | Med | Hạ cơ sở tính xuống UNKNOWN; tham chiếu R-16 |
| Phát hiện #13: tiêu đề "**Hãng thiết bị đều** đóng gói một EMS C&I tại chỗ có thời gian đáp ứng xác định". Chỉ có số thời gian đáp ứng cho Huawei | Low | Viết lại: "Ít nhất Huawei, SMA, Sungrow có EMS/logger C&I tại chỗ. Chỉ Huawei công bố thời gian đáp ứng" |
| SmartLogger5000B ≤ 2 s/≤ 5 s gắn với một model | Low | Theo R-19 |
| §3.2 "[FACT, URL ở ledger #20–#23]" cho câu "ở **mọi** sản phẩm có nguồn, vòng nhanh nằm tại site" | Low | Đổi thành INFERENCE (4 sản phẩm) |
| X-04 / Q-A09 đúng hướng. Thiếu khẳng định rằng hệ hạ áp có thể không cần thiết bị chống phát ngược | Low | Giữ Q-A09; G không được viết "bắt buộc pháp lý cho mọi site" (xem G) |
| Ledger #29 dùng glossary vendor cho định nghĩa TSO EMS; #2 có hai cơ sở 20% | Low | Không cần sửa; đã ghi conflicting |

### 3.2 B — Đối thủ

| Vấn đề | Mức | Sửa bắt buộc |
|---|---|---|
| Phát hiện #5 `[FACT]`: "Peak shaving là chức năng chung của **mọi** sản phẩm được xét". Ma trận của chính B ghi ABB G1 = U, STM/GB = P | Med | Đổi thành "≥ 8/11 sản phẩm có tài liệu (V)". Kết luận "table stakes" là INFERENCE |
| Phát hiện #6 gắn FACT cho câu tổng hợp "điểm khác biệt thật nằm ở…" | Med | Đổi thành INFERENCE; giữ URL làm bằng chứng từng ý |
| Phát hiện #17: tổng quát hóa ràng buộc on/off-grid của Huawei | Med | Theo R-20 |
| Phát hiện #3 "**mọi** EMS nghiêm túc đều giữ vòng nhanh ở edge" | Low | "Các sản phẩm có tài liệu (Schneider, Ampowr, Huawei, OpenEMS, Stem) đều…" |
| Ma trận M3: ABB = V (L27, báo ngành) | Low | Đổi thành `V*` (tuyên bố của hãng qua báo chí). GridBeyond và Stem giữ P/`V*` |
| L16: Schneider "15 phút" là một kết quả; A/G dùng như FACT chắc chắn | Low | Theo R-23 |
| L44: hai giấy phép, mâu thuẫn với E | Med | Theo R-21 |
| Phát hiện #20 (seed InfinitePower) mâu thuẫn A/C/G | Med | Theo R-18 |
| B ghi rõ không đánh giá Victron/Deye/Solarman/Growatt C&I, là các hãng có thể phổ biến ở VN (Q-B12) | Med | Lượt sau phải bổ sung, ít nhất Deye/Solarman (thị phần hộ và SME ở VN) |
| Ánh xạ nhóm A–M (§1.2) là giả định | Low | Người viết 03 xác nhận; nếu khác thì đổi nhãn hàng |

### 3.3 C — Miền năng lượng

| Vấn đề | Mức | Sửa bắt buộc |
|---|---|---|
| Ledger #23 dùng **rfp.wiki** (B đã xác định là hồ sơ do AI sinh, độ tin ~30%) làm nguồn cho tính năng Ampowr | Med | Xóa rfp.wiki khỏi ledger. Nếu cần, giữ claim bằng URL ampowr.com của B (L04/L06) |
| Phát hiện #3: chu kỳ 30 phút được ghi là cơ sở hóa đơn, trong khi cơ sở (đo hay đăng ký) chưa rõ | Med | Giữ FACT cho "chu kỳ tích phân 30 phút". Thêm câu UNKNOWN về cơ sở tính (R-16) |
| §3.15 và K-table: nhãn cuối khoảng `(t−5′, t]` | Med | Theo R-05 |
| §3.1: đơn vị canonical kW float64 | Med | Theo R-03 (raw W/Wh; KPI kW/kWh) |
| Phát hiện #10: "Class C cũ thành Class B" trong IEC 61724-1:2021, từ nguồn vendor cảm biến | Low | Giữ Med, thêm "theo Hukseflux". Không dùng trong yêu cầu |
| Phát hiện #13: grid code từ blog vendor (gkoisolar) | Low | Đã gắn Low. Không đưa thông số ride-through vào NFR |
| Chưa định nghĩa dấu Q cho từng loại điểm | Low | Theo R-02 |
| §3.4: thuật toán phân bổ luồng chọn thứ tự PV→tải trước, BESS→tải sau. Đây là quy ước có ảnh hưởng pháp lý (NĐ 243) | Low | Ghi rõ đây là `attribution_version=1`, PROPOSAL, phải được xác nhận khi có văn bản (Q-C04) |

### 3.4 E — Tích hợp thiết bị

| Vấn đề | Mức | Sửa bắt buộc |
|---|---|---|
| PR-E-09 / F-37: IEC 104 là P0 cho "V1 C&I trung thế" | Med | Theo R-10 (P1 điều kiện) |
| §3.18: đơn vị W/Wh; `ts` khác C/F | Med | Theo R-03, R-04 (bộ tên của E là chuẩn) |
| §3.18: Q > 0 = phát (quy ước máy phát) áp chung | Med | Theo R-02 |
| §3.5: topic có tenant/site | Med | Theo R-12 |
| §3.19: `signature` tùy chọn V1 | Med | Theo R-11. Bổ sung `seq`, `danger_class`, `approval_ref`, `kid` (X-I-02) |
| §3.1: thứ tự ưu tiên khác G/I | High | Theo R-07 |
| F-06, F-07, F-30, F-33 là FACT từ diễn đàn | Low | E đã gắn Low. Quy tắc: thanh ghi từ diễn đàn **không** được vào driver `VERIFIED_*` khi chưa có tài liệu hãng hoặc thử lab |
| F-17: QĐ 1570 chỉ đọc qua bản tóm tắt của Advantech (vendor bán thiết bị cho đúng nhu cầu này) | Med | Gắn rõ "nguồn vendor có lợi ích". Không ghi "≥ 64 kbps, ≤ 125 ms" thành NFR khi chưa đọc văn bản |
| F-21: Security Whitepaper Ed.4 (02/2026) chỉ qua snippet | Low | Giữ; kiểm chứng trước khi trích trong 07 |
| §3.14: OpenEMS "EPL-2.0" | Med | Theo R-21 |
| §3.12 G6: buffer ≥ 7 ngày | Low | Theo R-13 |

### 3.5 F — Dữ liệu & phân tích

| Vấn đề | Mức | Sửa bắt buộc |
|---|---|---|
| Cờ `STALE` trùng nghĩa với UI | Med | Đổi thành `FROZEN` (R-06) |
| `series.unit` canonical kW/kWh; `ts_gauge` nhãn cuối khoảng; `interval_energy.bucket_end` | Med | Theo R-03, R-05 |
| Kiến trúc ADR-F1 dựa vào giấy phép TSL. Câu "SaaS không bán DB nên có vẻ được phép" là INFERENCE | Med | Giữ Q-F01 là **điều kiện chặn** ADR. Không mở "SQL truy cập trực tiếp" cho khách cho đến khi pháp chế duyệt |
| Phát hiện #10 đề xuất ClickHouse là điểm chuyển ở 3.000–5.000 site; ngưỡng không có benchmark | Low | Đã gắn INFERENCE; ghi rõ là giả thuyết PoC (F-P25) |
| Bảng khối lượng dùng site 1.000 điểm, còn E dùng 2.000 điểm cho buffer | Low | Người viết 06 dùng một site tham chiếu (đề xuất: 1.000 điểm mặc định, 5.000 cho site lớn) |
| Phần MAPE/IPMVP/ASHRAE là kiến thức nền | Low | Đã gắn đúng; kiểm chứng trước khi phát hành 08 |
| F-P18: F0/F1 P0 "nếu MVP có peak shaving dự báo" | Low | Theo §6: MVP không có peak shaving demand nên F0/F1 là P0 chỉ cho tính SOC đích của luật TOU (G §3.4) |

### 3.6 G — Tối ưu

| Vấn đề | Mức | Sửa bắt buộc |
|---|---|---|
| Phát hiện #11 và §3.1: "zero-export **bắt buộc pháp lý** với site không bán dư". Bằng chứng (E F-17, tóm tắt VBHN 52) chỉ nói về hệ **trung áp** không bán dư | Med | "Bắt buộc với hệ trung áp không bán dư (theo tóm tắt VBHN 52). Hạ áp: UNKNOWN (Q-A09)" |
| §3.8 thứ tự L0–L9 | High | Theo R-07 (giữ mô hình "thu hẹp khoảng", đổi thứ tự watchdog/điều độ, nêu tường minh vị trí lệnh tay) |
| FR-OPT-001…016, NFR-PERF-0xx dùng mã chính thức | Med | Mã tạm; người viết 04 cấp lại |
| §3.6: Python sidecar | Med | Theo R-22 |
| Ledger #33 (giấy phép solver) không có URL; "SCIP Apache-2.0 từ v9" | Low | Giữ UNKNOWN. K lưu ý theo kiến thức nền: SCIP chuyển sang Apache-2.0 từ khoảng bản 8.0.3, cũng chưa kiểm chứng |
| Phát hiện #10 / §3.15.3 đã nêu đúng mâu thuẫn A–C | — | Đã xử lý ở R-16 |
| §3.4: luật TOU "Chủ nhật không cao điểm" phụ thuộc QĐ 963; ngày áp hóa đơn UNKNOWN | Low | Bộ sinh lịch phải đọc lịch TOU có phiên bản, không hard-code (khớp A D-03) |
| §3.15.2 khuyến nghị BESS 4–5 h | Low | Gắn INFERENCE (đã có). Không đưa vào tài liệu bán hàng khi chưa có giá BESS ở VN |

### 3.7 H — UX

| Vấn đề | Mức | Sửa bắt buộc |
|---|---|---|
| Phân hạng lệnh A/B/C/D trùng với C0–C4 của I | Med | Theo R-14 |
| H-P08: đồng hồ demand P0 | Low | Theo R-24 |
| §3.13: hiển thị theo `ts_device` | Low | Theo R-04 |
| ISA-101/18.2, EEMUA 191, IEC 60617 không có nguồn trong phiên | Low | Đã gắn đúng. Tài liệu 09 chỉ được viết "theo tinh thần", không "tuân thủ" |
| Không có bằng chứng giao diện của bất kỳ đối thủ nào ngoài FusionSolar | Med | Ma trận UX của 02/09 chỉ so sánh với FusionSolar. Q-H01 chuyển sang lượt kiểm chứng |
| H-P21 (HMI edge cục bộ) P2, trong khi I yêu cầu công tắc LOCAL và kỹ sư tại chỗ | Low | Cân nhắc P1: tối thiểu một trang trạng thái/interlock cục bộ khi mất Internet |

### 3.8 I — Bảo mật & tin cậy

| Vấn đề | Mức | Sửa bắt buộc |
|---|---|---|
| Phát hiện #3 `[FACT]` "Modbus/IEC 104 không có xác thực", nhưng nguồn trích là ghi chú E (không phải URL) | Low | Đổi thành `INFERENCE (kiến thức nền về giao thức)` hoặc bổ sung URL ở lượt sau |
| Toàn bộ khung pháp lý VN (Luật ANM 2018, NĐ 53/2022, NĐ 13/2023, Luật BVDLCN 2025) là kiến thức nền | High (cho tài liệu 10) | Đúng nhãn. **Không** đưa số tháng lưu trữ vào NFR khi chưa kiểm chứng. K lưu ý thêm: có khả năng khung luật an ninh mạng đã thay đổi trong 2025–2026 (UNKNOWN). Q-I-04 là điều kiện chặn phát hành 10 |
| Yêu cầu P0 rất nặng cho một đội mới: TPM/secure element, CA riêng + HSM/KMS, JWS ký lệnh, hash chain + WORM theo giờ, hai DC tại VN, Fleet Governor | Med (tính khả thi) | Phân pha: ký lệnh, `expires_at`, SOE, interlock, MFA, audit append-only, outbound mTLS là P0 cho Gate M2. Neo WORM theo giờ, hai DC, chứng nhận là P1/P2. Edge thiếu TPM → khóa trong file mã hóa là ngoại lệ tạm thời có ghi rủi ro (R-xx) |
| NFR-SEC-014: công tắc LOCAL/REMOTE **phần cứng** là P0 | Med | Giữ P0 cho site có BESS do edge làm chủ (Gate M2). Cho phép thay bằng chế độ local/remote của thiết bị native **nếu** edge đọc được trạng thái đó, có biên bản commissioning |
| NFR-SEC-001…025 dùng mã chính thức | Med | Mã tạm; người viết 04 cấp lại |
| AC-07: cam kết "không kill thương mại" là đề xuất hợp đồng tốt | — | Đưa vào 13 và điều khoản dịch vụ |
| Bảng SLO: Command API ≥ 99,5% | Low | Hợp lý với edge-first. Giữ |

---

## 4. Claims bị bác bỏ hoặc hạ cấp

| Claim | Từ | Nhãn mới | Lý do |
|---|---|---|---|
| "C&I Việt Nam hiện chưa trả phí công suất (demand charge)" | A #6 | INFERENCE ("đại đa số"; khách thí điểm: UNKNOWN) | Mâu thuẫn với lịch thanh toán thí điểm 07/2026 do chính A trích |
| Thành phần công suất tính theo **công suất đăng ký** | A §3.4.4, ledger #14 | UNKNOWN | Mâu thuẫn C #3; chưa đọc văn bản |
| Pmax 30 phút là **cơ sở tính tiền** công suất | C #3 (phần suy diễn), G #10 | UNKNOWN (cơ sở). Giữ FACT Med cho "chu kỳ tích phân 30 phút" | R-16 |
| "Peak shaving là chức năng của **mọi** sản phẩm được xét" | B #5 | INFERENCE ("≥ 8/11") | Ma trận B có U/P |
| "Điểm khác biệt thật nằm ở (a)–(d)" | B #6 | INFERENCE | Câu tổng hợp, không phải tuyên bố từ một nguồn |
| Peak shaving của Huawei C&I "chỉ" ở kịch bản on/off-grid, và là mẫu phổ biến | B #17, G ledger #6 | FACT chỉ trong phạm vi manual được trích; phần tổng quát → bác bỏ | R-20 |
| "Hãng thiết bị **đều** đóng gói EMS có thời gian đáp ứng xác định" | A #13 | INFERENCE | Chỉ Huawei có số liệu |
| "Ở **mọi** sản phẩm có nguồn, vòng nhanh nằm tại site" | A §3.2 | INFERENCE | 4–5 sản phẩm |
| "Zero-export bắt buộc pháp lý với site không bán dư" (mọi cấp điện áp) | G #11, §3.1 | FACT chỉ cho trung áp (theo tóm tắt); hạ áp → UNKNOWN | E F-17 chỉ nói trung áp |
| Zero-export ≤ 2 s / peak shaving ≤ 5 s "của SmartLogger5000B" | A #13, B #4, G #2 | FACT (tự công bố của Huawei), model ghi "SmartLogger5000B/SmartMGC5000B" | R-19 |
| Ampowr: kích máy phát khi SOC thấp, "API respecting safety…" (nguồn rfp.wiki) | C ledger #23 | Bác bỏ nguồn rfp.wiki; claim chỉ giữ ở mức đã có URL ampowr.com (B L04/L06) | rfp.wiki là nội dung AI sinh, độ tin cậy tự ghi ~30% |
| Nội dung trang seed InfinitePower (EMS functions) | A #12, C #22, G #13 | FACT Low (snippet, một agent). Chỉ dùng cho định nghĩa chung khi có nguồn thứ hai | R-18 |
| Schneider "lịch 15 phút trên horizon 72 h" | A #21, G #1, H #18 | FACT Low–Med (một nguồn, ~2017, 48/72 h mâu thuẫn) | R-23 |
| "Modbus/IEC 104 tại site không có xác thực" `[FACT]` | I #3 | INFERENCE (kiến thức nền) cho đến khi có URL | Nguồn trích là ghi chú agent |
| ABB OPTIMAX "AI có mô tả cụ thể" = V | B ma trận M3 | `V*` (tuyên bố của hãng qua báo ngành) | Không có mô tả kỹ thuật độc lập |
| OpenEMS giấy phép "EPL-2.0" (một giấy phép) | E §3.14, PR-E-16 | UNKNOWN | R-21 |
| QĐ 1570: "≥ 64 kbps, ≤ 125 ms" như yêu cầu | E F-17 | FACT Low (tóm tắt của vendor có lợi ích), không dùng làm NFR | Chưa đọc văn bản |
| "Phần lớn site C&I được bên thứ ba vận hành" | A §3.3 | INFERENCE (đã gắn đúng). Không được viết thành FACT ở 00/02 | Không có số liệu |
| Mọi FACT về thanh ghi Modbus từ diễn đàn (Huawei 47086…, Sungrow 13049–13051, Victron 2700, Huawei 40000/43006) | E F-06/07/30/33, G #7 | Giữ FACT Low về "cộng đồng báo cáo"; **cấm** dùng làm map driver đã kiểm chứng | Diễn đàn, có mâu thuẫn và báo cáo "ghi không tác dụng" |

Không phát hiện URL có dấu hiệu bịa. Không phát hiện trường hợp gọi luật cố định là AI.

---

## 5. Chủ đề còn thiếu

| # | Chủ đề | Vì sao cần | Đề xuất người xử lý |
|---|---|---|---|
| G-01 | **Quy trình O&M:** ticket/work order, SLA, phân công kỹ thuật viên, lịch bảo trì định kỳ (PM), field service, liên kết cảnh báo → ticket → nguyên nhân → nhãn | P3 (O&M) là người dùng hằng ngày P0 (A §3.3), nhưng chỉ có một dòng "alarm → ticket" (H #11). Power Factors/CMMS mới chỉ được nhắc tên | Người viết 03/04 + lượt nghiên cứu bổ sung |
| G-02 | **Commissioning end-to-end:** gán edge vào site (QR), discovery, kiểm tra dấu, kiểm tra export limit, test rút cáp/watchdog, ký SOE, bàn giao | P4 là P0. Hiện nội dung nằm rải rác ở C §3.2, E G3, I §3.8 | Người viết 07 hợp nhất thành một checklist |
| G-03 | **Mô hình biểu giá M-TAR hợp nhất:** TariffVersion, TouCalendar, ngày lễ, nhiều biểu giá trong site, demand_basis/window, giá bán dư, ngân sách xuất, lịch pháp lý vs lịch hóa đơn | Có ở A/C/G/F nhưng chưa ai sở hữu | Người viết 05 |
| G-04 | **Mô hình kinh doanh và định giá** (theo site/kWp/MWh BESS, gói monitoring vs control, chi phí license thiết bị như Solar-Log/blue'Log) | Q-A10, Q-B11 bỏ ngỏ. OEM cho dashboard miễn phí (B #10) | 02/11 + phỏng vấn |
| G-05 | **Chiến lược kiểm thử:** simulator thiết bị Modbus/OCPP, HIL, lab thiết bị, test an toàn (replay, hết hạn, rút cáp), backtest | Nhiều P0 an toàn phụ thuộc test, nhưng chưa có kế hoạch | 06/10/11 |
| G-06 | **Lựa chọn phần cứng edge và chi phí BOM** (TPM, 2 NIC, CAN, 4G, SSD TBW) | E PR-E-12, I §3.5, F §3.1.3 đặt yêu cầu nhưng chưa có ứng viên và giá | 06/07 |
| G-07 | **Kiểm chứng với khách thật:** phỏng vấn installer/O&M/ESCO VN; hóa đơn EVN thật (TOU 963, hai thành phần) | Mọi giả định thị trường đều là nghiên cứu tại bàn | 01/13 |
| G-08 | **Hãng phổ biến ở VN chưa được đánh giá:** Deye/Solarman, Growatt, Solis C&I, tủ BESS Trung Quốc cụ thể | Driver thứ tự P0 có thể sai nếu thị phần khác | B/E lượt 2 |
| G-09 | **M-ADV (nâng cao):** chưa có định nghĩa phạm vi trung thực (dự báo, ML có nhãn, what-if) | Tránh M-ADV thành ngăn chứa "AI" mơ hồ | 03 |
| G-10 | **M-PV chẩn đoán:** phân tích string, so sánh peer, I-V (đã có ở FS cũ) | Chỉ F L2 và H §3.7 nhắc tới | 03, tái dùng nghiên cứu FS |
| G-11 | **API công khai (API-xx)** cho khách/đối tác: phạm vi, auth, rate limit, versioning | Rải rác ở F §3.14 và I §3.3 | 06 |
| G-12 | **Tích hợp PCCC/an toàn cháy BESS** (chỉ đọc) và liên quan UL 9540A/QCVN | I IL-08 có nhắc; chưa có danh sách tín hiệu | 07/10 |
| G-13 | **Kiểm chứng pháp lý bắt buộc** (lượt riêng, trước khi phát hành 00/02/04/10): NĐ 58 hợp nhất NĐ 243 (VBHN 52) và TT 29/2026; QĐ 963 (ngày áp hóa đơn); thí điểm giá hai thành phần; QĐ 1570; TT 05/2025 Điều 31; Luật ANM/NĐ 53/Luật BVDLCN; giấy phép TimescaleDB TSL và OpenEMS | Nhiều quyết định P0 đang dựa trên snippet | Orchestrator lên lịch |

---

## 6. Danh sách quyết định thống nhất (mọi người viết phải theo)

**Định vị và phạm vi**
1. **Nhóm sản phẩm chính:** nền tảng quản lý năng lượng **C&I behind-the-meter, đa site, đa hãng**, xây trên lớp giám sát/O&M (nhóm 1). Người mua chính là tổ chức vận hành (installer/O&M/ESCO). Chủ C&I là người xem báo cáo. Không làm ESG/carbon platform, SCADA/EMS lưới, microgrid transition/black start, hay giao dịch thị trường trong 12–18 tháng đầu (A D-14).
2. Site **chỉ có PV** là công dân hạng nhất. BESS và EV là tùy chọn. EV điều khiển là P1.
3. Thứ tự giá trị ở VN: (1) tuân thủ giới hạn xuất/trần nhập, (2) minh bạch tiết kiệm theo TOU, (3) O&M đa hãng, (4) tối ưu BESS. Demand charge chỉ là P1 (R-16, R-17).

**Quy ước dữ liệu**

4. **Dấu P:** lưới + = nhập, BESS + = xả, PV/tải/EV/máy phát ≥ 0 (R-01). **Dấu Q:** cùng hướng với P của từng điểm (R-02). UI chỉ hiển thị số không dấu kèm chữ hướng (Nhập/Xuất/Sạc/Xả/Chờ). Trạng thái sạc/xả lấy từ PCS/BMS, không suy từ dấu.
5. **Điện năng** lưu theo cặp không âm (nhập/xuất, sạc/xả), không lưu net làm dữ liệu gốc. Tính điện năng từ thanh ghi; tích phân P chỉ là dự phòng, gắn cờ `ESTIMATED_FROM_POWER`.
6. **Đơn vị:** raw/edge contract dùng W, Wh, var, VA (bộ đếm int64 Wh). Aggregate/KPI/API dùng kW/kWh. Tên trường luôn có hậu tố đơn vị (R-03).
7. **Thời gian:** lưu UTC. Site có `timezone` IANA. Ngày, tháng, TOU và kỳ hóa đơn tính theo giờ site. Timestamp gồm `ts` (edge, chính), `ts_src`, `ts_ingest` (R-04).
8. **Bucket:** khóa `bucket_start`, khoảng `[start, start+Δ)`. Lưới chuẩn 5 phút; 15/30 phút cho demand; 1 h, ngày địa phương, tháng địa phương do job ghi (R-05).
9. **Quality:** ba tầng (point E / series F / KPI C). `STALE` của F đổi thành `FROZEN`. UI dùng `freshness` riêng. Không bao giờ hiển thị 0 thay cho "không có dữ liệu" (R-06).
10. **Điểm đo chuẩn:** `MTR_POC` (bắt buộc cho mọi chức năng điều khiển lưới), `MTR_POC_LV`, `MTR_PV`, `MTR_BESS`, `MTR_AUX`, `MTR_LOAD_i`, `MTR_EV_i`, `MTR_GEN`. Mỗi điểm có `boundary`, `ct_ratio`, `vt_ratio`, `accuracy_class`, `aux_inside_boundary`. Driver khai báo `sign_convention`, `R_wrap`, nhãn đầu/cuối chu kỳ. Commissioning phải chạy **phép thử dấu**.
11. **Phân bổ luồng năng lượng** do backend tính bằng một thuật toán duy nhất có `attribution_version`, chạy ở chu kỳ ≤ 1 phút (đối với dữ liệu thô), rồi mới cộng dồn. UI chỉ hiển thị kết quả và ghi "ước tính".
12. **KPI dạng tỷ số** luôn tính lại từ tử số và mẫu số. Mỗi KPI mang `quality`, `coverage_pct`, `calc_version`. PR chỉ tính khi có cảm biến POA; không có thì hiển thị "N/A".

**Kiến trúc edge và cloud**

13. **Edge-first (giữ hướng cũ).** Edge của ta bắt buộc ở mọi site mà nền tảng ghi lệnh. Site chỉ giám sát được dùng connector cloud của hãng (chỉ đọc, quality `UNCERTAIN_VENDOR_CLOUD`).
14. **Cloud không bao giờ nằm trong vòng bảo vệ và không ghi trực tiếp vào thiết bị.** Cloud gửi ý định/lịch có hạn; edge arbiter + limit chain quyết định setpoint. Không lớp phần mềm nào sửa thông số bảo vệ (grid code, BMS, rơ-le). Nhóm lệnh C4 không có API.
15. **Vòng nhanh** (zero-export, import cap, SOC guard) chạy ở edge hoặc controller native, theo cờ `control_owner ∈ {NATIVE, EDGE}`. Ưu tiên native đã chứng nhận. Không chạy hai vòng trên cùng một biến (R-09).
16. **Thứ tự ưu tiên của arbiter:** thứ tự 12 mức của R-07. Mức 1–6 cố định.
17. **Fallback:** edge lưu lịch ≥ 48 h. Hết lịch thì chạy chiến lược mặc định an toàn của site. Mất `MTR_POC` hoặc dữ liệu BMS cũ thì ESS về P = 0 hoặc chế độ native, và PV về giới hạn native. Thiết bị không có watchdog/reversion không được nhận setpoint P cưỡng bức (`requires_native_fallback`).
18. **Store-and-forward:** NFR cứng không mất dữ liệu khi mất mạng ≤ 7 ngày; mục tiêu buffer 30 ngày theo tần suất cloud; dữ liệu 1 s giữ vòng tròn 7 ngày tại edge (R-13).
19. **Tần suất dữ liệu:** edge lấy mẫu 1 s cho điểm điều khiển. Cloud nhận tổng hợp tại nguồn 5 s (C1) / 60 s (C2) / 300 s hoặc khi đổi (C3), thanh ghi ở mọi biên 5 phút, sự kiện tức thời (F §3.1.2). Đây là thay đổi có chủ đích so với "1–5 phút" của nghiên cứu FS cũ.
20. **Uplink:** MQTT 5 + TLS (mTLS, cert riêng mỗi edge), outbound-only, payload nhị phân theo lô có nén, `seq` + ack, ingest idempotent. Topic theo R-12. Lệnh không retained và dùng Message Expiry. Sparkplug B chỉ là đầu ra tùy chọn (P2).
21. **Hợp đồng lệnh:** envelope của E §3.19 cộng các trường của I (`seq`, `danger_class`, `approval_ref`, `kid`, chữ ký JWS bắt buộc theo R-11). `expires_at` bắt buộc: setpoint mặc định 15 phút, tối đa 1 h; lịch tối đa 7 ngày. Mặc định `on_expiry = REVERT_DEFAULT`. Có readback trước khi báo `APPLIED`. Không gửi lại sau hạn. Có trạng thái `APPLIED_CLAMPED` và `FAILED_NO_EFFECT`.
22. **Từ vựng chế độ:** `site_strategy` (bộ của E) và `slot_mode` (bộ của G, chỉ trong `APPLY_SCHEDULE`). Cấu hình lưới gồm `export_mode`, `export_limit_w`, `import_cap_w` (R-15, R-27).
23. **Tầng điều khiển:** tầng 1 (edge, luật thời gian thực) và tầng 2 (bộ sinh lịch luật TOU, Java) thuộc MVP. Tầng 3 (MILP/MPC, receding horizon 48 h, slot 15 phút) là P1, chỉ bật cho site sau khi backtest chứng minh tốt hơn luật. Python sidecar chỉ dùng khi ADR-OPT chấp thuận. Tầng 4 (VPP/DR) là P2, chỉ ở dạng "VPP-capable".
24. **Biểu giá là dữ liệu có phiên bản theo ngày hiệu lực**, không hard-code. Hỗ trợ: khung QĐ 963 và TT 16/2014 (lịch sử), hai lịch song song (pháp lý/hóa đơn), nhiều biểu giá trong một site (EV), `demand_window` (mặc định 30 phút block, UNKNOWN), `demand_basis ∈ {MEASURED_MAX, CONTRACTED}` (tắt mặc định), ngân sách xuất theo kỳ (P1).
25. **Dữ liệu:** TimescaleDB (TSL, tự host) cho tầng nóng/ấm, Parquet trên object storage cho lưu lạnh. Kiến trúc này **phụ thuộc điều kiện** Q-F01 (giấy phép) và PoC F-P25. ClickHouse là phương án mở rộng, chưa dùng.

**An toàn và bảo mật**

26. **Hai mặt phẳng:** monitoring plane và control plane tách nhau về danh tính dịch vụ, credential, topic, quyền DB, quy trình release. Control mặc định **TẮT** theo site.
27. **MVP có hai cổng:** Gate M1 (giám sát + cấu hình chế độ native có readback) và Gate M2 (edge làm chủ vòng/setpoint). M2 chỉ bật cho site khi đủ P0 an toàn: SOE ký số, interlock, `expires_at`, ký lệnh, MFA + step-up, audit append-only, watchdog thiết bị, LOCAL/REMOTE (R-08).
28. **Phân hạng lệnh C0–C4** (I §3.7.4). C3 cần hai người duyệt. C4 không tồn tại trên cloud. Không có "E-stop từ xa" trên UI (R-14).
29. **Phân quyền:** RBAC theo cây Org → Site → Device, cộng ABAC/PDP cho mọi lệnh. Org Admin mặc định không có quyền lệnh. Grant installer có hạn, do chủ tài sản cấp và thu hồi. Tenant cô lập bằng PostgreSQL RLS (FORCE) + test cross-tenant trong CI. Silo/on-prem là SKU sau.
30. **Fleet Dispatch Governor** và kill switch điều khiển từ xa (tắt = C1, bật lại = C3) là P0 của Gate M2. Ngưỡng 20%/5 phút là PROPOSAL cần mô phỏng.
31. **Lưu giữ:** raw nóng 13 tháng; tổng hợp 5 phút 5 năm; giờ/ngày/tháng theo vòng đời dự án; audit lệnh và kế hoạch đã chạy: trực tuyến ≥ 13 tháng + WORM ≥ 5 năm (R-25). Hosting tại VN là mặc định (INFERENCE, chờ kiểm chứng pháp lý).
32. **IEC 104 slave** là P1 có điều kiện (site trung áp bán dư hoặc khi PC yêu cầu). IEC 61850, DNP3, OpenADR, IEEE 2030.5 là P2. OCPP 1.6J (Security Profile ≥ 2) là P1 (R-10).

**Bằng chứng và ngôn từ**

33. **Không gọi là AI/ML** bất cứ thứ gì không phải mô hình học đã đánh giá trên dữ liệu có nhãn. Luật là "Quy tắc"; tối ưu là "tối ưu dựa trên dự báo"; thống kê là "Thống kê". Mọi số ước tính hoặc mô phỏng phải có nhãn "≈ ước tính" hoặc "Mô phỏng".
34. **Không tuyên bố tuân thủ** IEC 62443, ISO 27001, ISO 50001, IEC 61724-1, IPMVP, ISA-101/18.2 khi chưa có chứng chỉ (số, phạm vi, hạn) hoặc chưa đối chiếu văn bản. Dùng cụm "thiết kế theo tinh thần". Không quảng cáo % tiết kiệm; tiết kiệm = hóa đơn bóng so với baseline phản thực, cùng phiên bản biểu giá.
35. **Không gán tính năng chưa có tài liệu cho hãng.** "Không có tài liệu" ≠ "không hỗ trợ". Tuyên bố bảo mật của hãng ghi là "tự tuyên bố". Thanh ghi lấy từ diễn đàn không được vào driver `VERIFIED_*`. Ra thị trường không bao giờ ghi "tương thích mọi inverter/BESS"; chỉ liệt kê model + firmware + trạng thái kiểm chứng.
36. **Số Huawei ≤ 2 s / ≤ 5 s** chỉ là mục tiêu tham chiếu do hãng tự công bố, ghi "SmartLogger5000B/SmartMGC5000B" (R-19). Không có sản phẩm nào công bố độ trễ end-to-end cloud→thiết bị.
37. **Pháp lý VN dùng làm cơ sở:** NĐ 58/2025 + NĐ 243/2026 (trần 50% sản lượng thực phát; điện xả BESS tính vào điện dư), không dùng NĐ 135/2024 nữa. TOU theo QĐ 963 (cao điểm 17h30–22h30 T2–T7). Giá theo QĐ 1279. Mọi chi tiết thực thi (kỳ tính 50%, ngày áp TOU, cơ sở giá hai thành phần, yêu cầu thiết bị chống phát ngược hạ áp) là UNKNOWN, phải nằm trong 13 và được kiểm chứng (§5 G-13).

**Mã định danh**

38. **Mã trong `notes/` là tạm thời.** Bao gồm D-xx, PR-B/E-xx, C-P, F-P, H-P, cũng như FR-OPT-xxx của G và NFR-SEC-xxx của I. Chỉ người viết 04 cấp `FR-<MODULE>-NNN` / `NFR-<NHÓM>-NNN`. Người viết 13 cấp `R-NN`, `Q-NN`. Người viết 06 cấp `ADR-NN`. Người viết 09 cấp `UI-NN`. Mỗi mã chính thức phải ghi mã tạm gốc để truy vết (12).
39. **Nhãn mức cảnh báo:** Khẩn cấp / Cao / Trung bình / Thông tin. Đây là enum i18n duy nhất, mỗi mức có icon hình dạng riêng (R-26).
40. **Ưu tiên P0/P1/P2 lấy từ §6 này khi mâu thuẫn với ghi chú.** P0 (MVP): giám sát đa hãng, `MTR_POC`, biểu giá TOU, zero-export/giới hạn xuất (native trước), import cap, lịch luật TOU, BESS supervisory (Gate M1/M2), cảnh báo L0/L1, báo cáo R1/R2/R3/R8, an toàn lệnh. P1: MILP/MPC, demand charge, EV DLM/OCPP, IEC 104, ngân sách xuất 50%, dự báo đa nguồn, bất thường L2, PR/availability, Parquet. P2: VPP/DR, 61850/DNP3/OpenADR, ML (L3), giám sát microgrid.
