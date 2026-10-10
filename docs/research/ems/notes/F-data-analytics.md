# F — Dữ liệu & phân tích: telemetry, lưu trữ chuỗi thời gian, tổng hợp, KPI, dự báo, bất thường, báo cáo

[← Mục lục](../index.html) · [04 Yêu cầu](../04-business-requirements.md) · [05 Domain](../05-domain-model.html) · [06 Kiến trúc](../06-system-architecture.html) · [08 Tối ưu](../08-energy-optimization.md) · [09 UX/UI](../09-ux-ui-specification.html) · [10 An toàn](../10-security-and-reliability.md) · [13 Rủi ro](../13-open-questions-and-risks.md) · [14 Nguồn](../14-source-register.md)

- Tác giả: Agent F (Data & Analytics Architect)
- Ngày: 2026-10-10 · Trạng thái: bản nghiên cứu v1. Đầu vào cho 04 (FR/NFR), 05 (domain model), 06 (kiến trúc), 08 (dự báo/tối ưu), 09 (biểu đồ, báo cáo), 11 (lộ trình), 13 (rủi ro).
- Phương pháp và giới hạn:
  - Chỉ dùng WebSearch, vì fetch trực tiếp bị chặn. Mọi FACT có URL ở đây lấy **qua kết quả tìm kiếm** (snippet/tóm tắt), trừ khi ghi "nghiên cứu FusionSolar trước". Nhãn đó nghĩa là đã đọc trong `docs/research/fusionsolar/` hoặc trong ghi chú của agent khác.
  - **Hạn mức tìm kiếm của lượt chạy đã hết giữa chừng**, vì giới hạn chung 200 lượt cho mọi agent. Các chủ đề sau **chưa tìm được nguồn trong phiên**: chỉ số sai số dự báo (nMAE/MAPE), IPMVP/ASHRAE Guideline 14, giới hạn của Excel, `time_bucket` có tham số timezone, giá của nhà cung cấp dự báo. Những phần này ghi `[INFERENCE — kiến thức nền, chưa kiểm chứng nguồn]` hoặc `[UNKNOWN]`. Cần một lượt tìm kiếm bổ sung trước khi chốt ADR.
  - Không đọc datasheet BESS hay công tơ cụ thể nào. Số điểm đo/thiết bị là **ước lượng kỹ thuật** (INFERENCE), không phải dữ liệu hãng.
- Tôi tái sử dụng và **không lặp lại** nội dung của C-energy-domain: quy ước dấu (lưới + = nhập, BESS + = xả), bảng KPI K01–K32 (§3.14), máy trạng thái delta thanh ghi và quy tắc múi giờ (§3.15). Ghi chú này đi sâu vào phần **hạ tầng dữ liệu**: khối lượng, schema, engine, ngữ nghĩa tổng hợp có thể ghép (composable), dữ liệu trễ, cờ chất lượng, lưu giữ, dự báo, bất thường, xuất dữ liệu và báo cáo.

---

## 1. Phạm vi & câu hỏi nghiên cứu

| Mã | Câu hỏi | Mục trả lời |
|---|---|---|
| RQ-F01 | Một site C&I (PV + BESS + lưới + tải + EV tùy chọn) có bao nhiêu điểm đo (point)? Lấy mẫu ở edge và cloud nhanh đến đâu? | §3.1 |
| RQ-F02 | Khối lượng dữ liệu (mẫu/s, GB/ngày, TB/năm, băng thông 4G) cho 100 / 1.000 / 10.000 site là bao nhiêu? | §3.1 |
| RQ-F03 | Schema chuỗi thời gian nên là narrow (một hàng một giá trị), wide (một hàng một thiết bị) hay lai? | §3.2 |
| RQ-F04 | Chọn engine nào trong TimescaleDB, InfluxDB 3, ClickHouse, QuestDB, Apache IoTDB, Parquet trên object storage? Đánh đổi gì? | §3.3 |
| RQ-F05 | Ngữ nghĩa tổng hợp cho từng loại đại lượng: avg công suất, delta điện năng, last SOC, max demand, trung bình theo thời gian (time-weighted) | §3.4 |
| RQ-F06 | Lấy điện năng theo chu kỳ từ thanh ghi tích lũy thế nào khi có reset, tràn số (rollover) và thay công tơ? | §3.5 |
| RQ-F07 | Xử lý dữ liệu trễ/sai thứ tự và tính lại (recompute) ra sao? | §3.6 |
| RQ-F08 | Bộ cờ chất lượng (measured/calculated/estimated/forecast/manual/substituted) và quy tắc lan truyền? | §3.7 |
| RQ-F09 | Quy tắc lấp khoảng trống (gap filling) cho hiển thị, KPI và hóa đơn bóng? | §3.8 |
| RQ-F10 | Gộp ngày/tháng theo múi giờ nào? Danh mục đa múi giờ xử lý ra sao? | §3.9 |
| RQ-F11 | Các tầng lưu giữ (retention tier) và chi phí? | §3.10 |
| RQ-F12 | Danh mục báo cáo; phương pháp baseline cho "tiết kiệm"; tham chiếu IPMVP | §3.11 |
| RQ-F13 | Dự báo PV (Solcast, Open-Meteo, Meteomatics) và dự báo tải; chỉ số độ chính xác và bẫy | §3.12 |
| RQ-F14 | Các mức phát hiện bất thường: luật, thống kê, ML | §3.13 |
| RQ-F15 | Định dạng xuất (CSV/XLSX/PDF/Parquet), giới hạn, báo cáo định kỳ | §3.14 |
| RQ-F16 | Yêu cầu quản lý chất lượng dữ liệu (NFR-DATA) | §3.15, §4 |

---

## 2. Phát hiện chính

1. **[FACT] FusionSolar làm thế này:** lấy mẫu thống kê mỗi **5 phút**; dữ liệu giờ trước được tổng hợp ở phút thứ 5 của giờ sau; khôi phục dữ liệu sau mất kết nối trong vòng 24 h; tính lại tổng hợp ngày/tháng/năm lúc 02:00. Lưu giữ ở EU: 15 tháng dữ liệu thiết bị, 15 tháng báo cáo giờ, 5 năm báo cáo ngày/tháng, 25 năm báo cáo năm. Dữ liệu động khoảng 1–5 MB/ngày. Nguồn (nghiên cứu FusionSolar trước): https://digitalpower.huawei.com/en/eu-data-act ; https://solisdepot.com/wp-content/uploads/2023/03/FusionSolar-Smart-PV-Management-System-7.0-After-sales-Technical-Training-Slides.pptx.pdf. [INFERENCE] Mức 5 phút đủ cho giám sát PV nhưng **không đủ** cho EMS có BESS. Peak shaving với cửa sổ demand 30 phút và zero-export ≤2–5 s (theo A và B) cần dữ liệu 1 s ở edge và 5–60 s trên cloud. Đây là **thay đổi có chủ đích** so với đề xuất "raw 1–5 phút" của nghiên cứu FusionSolar trước (`competitors_rebuild.md`).

2. **[INFERENCE] Khối lượng (site tham chiếu ~1.000 điểm, §3.1):**
   - Edge 1 s: 86,4 triệu mẫu/site/ngày.
   - Cloud (10% điểm ở 5 s, 90% ở 60 s): khoảng 3,0 triệu mẫu/site/ngày, tức 35 mẫu/s/site.
   - 1.000 site: khoảng 35.000 mẫu/s; khoảng 242 GB/ngày chưa nén (80 B/mẫu, kể cả index); khoảng 15 GB/ngày nén (5 B/mẫu); **khoảng 5,5 TB/năm nén**.
   - 10.000 site: khoảng 350.000 mẫu/s và khoảng 55 TB/năm nén. Ở mức này một node PostgreSQL đơn sẽ chạm giới hạn ghi, nên cần sharding theo tenant/site hoặc engine cột.

3. **[FACT] TimescaleDB:**
   - Continuous aggregate tự làm mới tăng dần ở nền; chỉ phần dữ liệu thay đổi được tính lại — https://blog.timescale.com/continuous-aggregates-faster-queries-with-automatically-maintained-materialized-views/
   - Continuous aggregate là một hypertable đặc biệt và có thể bật columnstore với `segmentby`. Tỷ lệ nén phụ thuộc thứ tự (`orderby` theo thời gian) và cách phân đoạn — https://docs.timescale.com/use-timescale/latest/hypercore/real-time-analytics-in-hypercore
   - Tài liệu mirror ghi "90%+ compression typical"; blog bên thứ ba ghi 10–20×. Không có benchmark riêng cho energy — https://access.crunchydata.com/documentation/timescaledb/2.28.0/ ; https://oneuptime.com/blog/post/2026-01-27-timescaledb-continuous-aggregates/view (qua kết quả tìm kiếm).

4. **[FACT] Giấy phép TimescaleDB:**
   - Compression, continuous aggregate và retention policy thuộc **Community Edition (Timescale/Tiger Data License, TSL)**. Tự host thì miễn phí, nhưng **không được bán TimescaleDB như dịch vụ cơ sở dữ liệu (DBaaS)**. Bản Apache 2 không có các tính năng này — https://www.tigerdata.com/docs/about/latest/timescaledb-editions ; https://www.tigerdata.com/legal/licenses (qua kết quả tìm kiếm).
   - Việc phân chia tính năng theo thư mục `/tsl/` lấy từ nguồn thứ cấp.
   - [INFERENCE] Một SaaS EMS bán *ứng dụng* chứ không bán DB cho khách truy vấn tự do, nên có vẻ nằm trong phạm vi cho phép. **Cần pháp chế xác nhận** (Q-F01), nhất là nếu ta mở "SQL truy cập trực tiếp" cho khách.

5. **[FACT] Toolkit của TimescaleDB:**
   - Có `time_weight()` (LOCF hoặc linear/trapezoidal), ghép được bằng `rollup()`. Có accessor nội suy để tính trung bình ngày đúng ở biên ngày — https://www.tigerdata.com/docs/api/latest/hyperfunctions/time-weighted-calculations/time_weight/ ; https://www.timescale.com/forum/t/toolkit-1-8-0-now-available/700
   - Có `counter_agg()` cho bộ đếm đơn điệu, tự phát hiện reset, với các accessor `delta()`, `rate()`, `num_resets()` — https://pigsty.io/ext/e/timescaledb_toolkit/ ; https://docs.timescale.com/api/latest/analytics/ (qua kết quả tìm kiếm).
   - [INFERENCE] `counter_agg` coi mọi lần giảm là reset về 0. Nó **không** biết `R_wrap` hay sự kiện thay công tơ. Vì vậy không đủ cho điện năng tính tiền; vẫn cần máy trạng thái của C §3.15 ở tầng ingest.

6. **[FACT] SolarNetwork (nền tảng dữ liệu năng lượng tái tạo) dùng PostgreSQL/TimescaleDB.**
   - Blog của chính họ: DB khoảng 300 GB, khoảng 312 nghìn "datum" mỗi ngày, có các hàng tổng hợp giờ/ngày/tháng tính sẵn **tự làm**. Họ "muốn áp dụng" continuous aggregate và retention của Timescale.
   - Case study của Timescale lại nói họ đã dùng continuous aggregate. **Hai nguồn mâu thuẫn** — https://timescale.com/blog/how-solarnetwork-fuels-energy-conservation-with-timescaledb ; https://timescale.com/case-studies/solarnetwork (qua kết quả tìm kiếm).
   - [INFERENCE] Quy mô của SolarNetwork **nhỏ hơn khoảng 10.000 lần** so với kịch bản 1.000 site của ta (3 tỷ mẫu/ngày). Case study này chứng minh mô hình dữ liệu phù hợp, **không** chứng minh khả năng mở rộng.

7. **[FACT] Các engine thay thế:**
   - **InfluxDB 3 Core** (MIT/Apache 2) lưu Parquet trên object storage, có Last Value Cache. Truy vấn lịch sử dài, HA và read replica được tài liệu ghi là tính năng **Enterprise** (thương mại, tính theo core) — https://influxdata.com/blog/influxdb3-open-source-public-alpha ; https://docs.influxdata.com/influxdb3/enterprise/admin/
   - **ClickHouse** khuyến nghị codec DoubleDelta/Gorilla/T64 cho chuỗi thời gian. Materialized view là tùy chọn cho độ trễ/chi phí — https://clickhouse.com/docs/ru/faq/use-cases/time-series
   - **QuestDB** bản mở là Apache 2.0 và có `SAMPLE BY … FILL`. Đọc Parquet từ 8.1. Truy vấn Parquet trên object storage là tính năng Enterprise — https://questdb.io ; https://questdb.io/blog/questdb-release-8-1-0
   - **Apache IoTDB** có tree model (ví dụ chính thức là phân cấp *nhà máy điện gió → turbine → measurement*) và *aligned timeseries* dùng chung một cột thời gian — https://iotdb.apache.org/UserGuide/V1.3.x/Basic-Concept/Data-Model-and-Terminology.html
   - Tất cả lấy qua kết quả tìm kiếm.

8. **[FACT] Dự báo bức xạ/PV:**
   - Solcast gói hobbyist: độ phân giải 30 phút (PT30M), 10 lượt gọi/ngày, tối đa 2 mảng; có P10/P50/P90 — https://docs.solcast.com.au/docs/section/rooftop-sites-hobbyist ; https://emhass.readthedocs.io/en/latest/forecasts.html
   - Open-Meteo có GTI (bức xạ trên mặt phẳng nghiêng, theo tilt/azimuth). Bước 15 phút có cho AROME, nhưng chỉ phủ Tây Âu. Dùng thương mại cần API key và endpoint `customer-api` — https://openmeteo.substack.com/p/global-tilted-irradiance-gti-meteofrance ; https://hub.meltano.com/extractors/tap-openmeteo
   - Meteomatics MOS: tầm 15 ngày, độ phân giải 1 h, tham số `global_rad` — https://www.meteomatics.com/en/api/available-parameters/mos-parameters/
   - Tất cả qua kết quả tìm kiếm. [UNKNOWN] Giá gói thương mại, độ phân giải 5/15 phút cho Việt Nam, và độ chính xác ở Việt Nam.

9. **[FACT] Nền tảng tích hợp cloud-to-cloud thực tế chấp nhận độ trễ 15 phút–24 h và lấy lại dữ liệu 7 ngày mỗi đêm.**
   - meteocontrol: đo 5 phút, truyền 15 phút, mỗi đêm hỏi lại 7 ngày gần nhất để lấp khoảng trống — https://help-center.meteocontrol.com/en/vcom-cloud/latest/huawei-fusionsolar-api-1
   - FusionSolar Northbound: lịch sử tối đa 10 thiết bị × 3 ngày ở 5 phút mỗi lần gọi — https://support.huawei.com/enterprise/en/doc/EDOC1100358266/b9df65c2/monitoring (nghiên cứu FusionSolar trước).
   - [PROPOSAL] Pipeline của ta phải coi **"dữ liệu trễ ≤ 7 ngày" là chuyện bình thường**, không phải ngoại lệ.

10. **[PROPOSAL] Kiến trúc dữ liệu đề xuất (ứng viên ADR):**
    - **TimescaleDB** (Community/TSL, tự host) cho tầng nóng/ấm: raw 13 tháng nén + continuous aggregate 5 phút/1 h.
    - Bảng tổng hợp ngày/tháng theo **giờ địa phương site**, tính bằng job có phiên bản.
    - **Parquet trên object storage** cho lưu trữ lạnh lâu dài và xuất hàng loạt.
    - **ClickHouse** là phương án mở rộng khi vượt khoảng 3.000–5.000 site hoặc khi cần phân tích ad hoc nặng.
    - Lý do: khớp đội Java/Spring + PostgreSQL và hướng cũ; giữ SQL/JOIN với metadata; xử lý được UPDATE/upsert cho dữ liệu trễ.

11. **[PROPOSAL] Tách ba loại dữ liệu đo, không trộn vào một bảng `value double`:**
    - (a) **gauge** (P, V, T, SOC): trung bình theo thời gian.
    - (b) **register** (điện năng tích lũy, int64/numeric): delta.
    - (c) **state/enum/event** (trạng thái, mode, alarm bit): thời lượng ở trạng thái và lần chuyển.
    - Mỗi chuỗi có `agg_rule` khai báo trong catalog. Đây là điều kiện để rollup đúng và ghép được (§3.4).

12. **[PROPOSAL] Cờ chất lượng gồm hai trục:**
    - **Nguồn gốc** (một giá trị): MEASURED, CALCULATED, ESTIMATED, FORECAST, MANUAL, SUBSTITUTED.
    - **Tình trạng** (bitmask): INTERPOLATED, SUSPECT, OUT_OF_RANGE, STALE, CLOCK_SUSPECT, PARTIAL, LATE, REVISED, ROLLOVER, RESET.
    - Cộng thêm `coverage_pct` và `calc_version`. Bộ cờ này tương thích với danh sách `quality` của C (§3.14b) (§3.7).

13. **[INFERENCE — kiến thức nền, chưa kiểm chứng nguồn] Không dùng MAPE làm chỉ số chính cho dự báo PV.**
    - Ban đêm hoặc lúc bình minh, giá trị thực ≈ 0 làm MAPE vô hạn hoặc phóng đại.
    - Dùng **nMAE/nRMSE chuẩn hóa theo công suất đặt** (PV) hoặc **theo tải trung bình** (load), chỉ tính trong giờ có nắng. Dùng **skill score** so với persistence/seasonal naive. Dùng **pinball loss** cho P10/P90.
    - Riêng peak shaving cần chỉ số **sai số tại cửa sổ đỉnh** (§3.12).

14. **[PROPOSAL] "Tiết kiệm" của PV/BESS là counterfactual dựng lại từ đo đạc**, không phải hồi quy kiểu IPMVP Option C:
    - Tải site đo được (hoặc tính từ cân bằng), nên hóa đơn "không PV/không BESS" tính lại trực tiếp cùng phiên bản biểu giá.
    - Cách này gần tinh thần **cô lập ranh giới (retrofit isolation, Option B)** của IPMVP. [INFERENCE — kiến thức nền] Chưa kiểm chứng văn bản IPMVP; không tuyên bố "tuân thủ IPMVP" (§3.11).

15. **[PROPOSAL] Phân mức bất thường L0–L3:**
    - L0: kiểm tra hợp lệ dữ liệu.
    - L1: luật ngưỡng cố định.
    - L2: thống kê, gồm so sánh đồng cấp (peer), residual so với mô hình kỳ vọng và CUSUM.
    - L3: ML.
    - **Chỉ L3 đã được đánh giá trên dữ liệu có nhãn mới được gọi là "ML". Không mức nào được quảng cáo là "AI"** nếu chỉ là luật (§3.13).

---

## 3. Phân tích chi tiết

### 3.1 Điểm đo, tần suất lấy mẫu và khối lượng

#### 3.1.1 Danh mục điểm đo của site tham chiếu [INFERENCE]

Giả định: site C&I khoảng 1 MWp PV (10 inverter string 100 kW), BESS khoảng 500 kW/1 MWh (1 PCS, 1 BMS, 4 rack), 1 công tơ POC (điểm đấu nối), 5 submeter, 1 trạm khí tượng, 2 trụ sạc EV AC/DC, 1 bộ điều khiển edge.

| Lớp thiết bị | SL | Điểm/thiết bị | Tổng | Ví dụ điểm | Ghi chú |
|---|---|---|---|---|---|
| Công tơ POC | 1 | ~40 | 40 | P/Q/S theo pha và tổng (12), U pha + dây (6), I (4), PF (4), f, A+/A−/R+/R− tích lũy (4–8), THD | Thanh ghi điện năng là **register** |
| Inverter PV | 10 | ~60 | 600 | P/Q AC, U/I theo pha, U/I mỗi MPPT/string (~20), nhiệt độ, trạng thái, mã lỗi (bitfield), `total_yield`, `daily_yield`, P_avail (nếu có) | String-level chiếm phần lớn |
| PCS | 1 | ~40 | 40 | P/Q, U/I DC/AC, nhiệt độ, mode, giới hạn hiện hành, setpoint đã nhận | |
| BMS (mức hệ + rack) | 1 | ~30 + 4×10 | 70 | SOC, SOH, U/I hệ, CCL/DCL, Tmin/Tmax, Umin/Umax cell, trạng thái contactor, cảnh báo | **Mức cell (vài trăm cell × U, T) chỉ giữ ở edge** hoặc gửi min/max/vị trí |
| Trạm khí tượng | 1 | ~8 | 8 | G_POA, GHI, T_module, T_ambient, gió | Bắt buộc cho PR (C §3.11) |
| Submeter | 5 | ~20 | 100 | P, I, E tích lũy | |
| Trụ sạc EV (OCPP) | 2 | ~15 | 30 | trạng thái connector, P, E phiên, giới hạn sạc | OCPP MeterValues, chu kỳ theo cấu hình |
| Bộ điều khiển edge | 1 | ~30 | 30 | chế độ, setpoint gửi, P_allow_rest, sức khỏe link, độ trễ vòng | Bằng chứng audit cho điều khiển |
| **Tổng** | | | **≈920 → làm tròn 1.000** | | Site nhỏ (chỉ PV + meter): ~200. Site lớn (5 MWp, nhiều BESS, cell-level lên cloud): ~5.000 |

#### 3.1.2 Lớp tần suất lấy mẫu [PROPOSAL]

| Lớp | Edge (lưu cục bộ) | Cloud (gửi lên) | Áp dụng | Lý do |
|---|---|---|---|---|
| C1: điều khiển nhanh | 1 s (hoặc nhanh nhất driver cho phép, 200 ms–1 s) | 5 s (trung bình theo thời gian + min/max của 5 s) | P/Q tại POC, P PCS, SOC, CCL/DCL, setpoint, P_allow_rest | Zero-export ≤2 s và peak shaving ≤5 s chạy **ở edge** (B-competitors L37). Cloud chỉ cần đủ để kiểm tra lại và hiển thị gần thời gian thực |
| C2: vận hành | 1–5 s | 60 s (avg/min/max/last) | Phần lớn P/U/I/T của inverter, PCS, submeter | Đủ cho biểu đồ ngày và phát hiện bất thường L1/L2 |
| C3: chậm | 10–60 s | 300 s hoặc khi đổi (report-by-exception) | Nhiệt độ tủ, SOH, cấu hình, string ít biến động | Giảm băng thông |
| C4: thanh ghi | đọc mỗi 1–60 s | mỗi 60 s **và** ở mọi biên 5 phút (giá trị tại hoặc ngay sau biên) | A+/A−, `total_yield`, E sạc/xả | Delta 5 phút chính xác; bảo toàn năng lượng qua khoảng trống |
| C5: sự kiện | tức thời | tức thời (QoS 1) | Alarm, đổi trạng thái/mode, lệnh điều khiển + ack | Phải có `ts_device` + seq |
| Tổng hợp | — | 5 phút (chuẩn), 15/30 phút (demand), 1 h, ngày, tháng | Mọi chuỗi | 5 phút khớp FusionSolar/meteocontrol. 30 phút khớp Pmax ở Việt Nam (C §3.9) |

- [PROPOSAL] Edge gửi **tổng hợp tại nguồn** (avg/min/max/last/count của khoảng 5 s hoặc 60 s), không gửi mẫu tức thời thưa. Lấy mẫu tức thời thưa gây aliasing: một gai 3 s sẽ biến mất hoàn toàn trong mẫu 60 s.
- [PROPOSAL] Có cơ chế "burst mode": khi có sự cố hoặc vận hành viên mở màn hình live, cloud yêu cầu edge đẩy C1/C2 ở 1 s trong N phút (mặc định 15 phút). Edge cũng tải lên dữ liệu 1 s quanh sự cố (±5 phút) để phân tích.

#### 3.1.3 Khối lượng [INFERENCE — tính toán]

Giả định:
- Site tham chiếu 1.000 điểm. 10% điểm ở 5 s, 90% ở 60 s, nên chu kỳ trung bình hiệu dụng khoảng 28,6 s.
- Chưa nén khoảng **80 B/mẫu** trong PostgreSQL narrow: header tuple khoảng 23 B, cùng ts 8 B, series_id 4 B, value 8 B, quality 2 B, căn lề, B-tree index. Đây là kiến thức nền, chưa kiểm chứng nguồn.
- Nén cột khoảng **5 B/mẫu**: thận trọng hơn "90%+" (≈8 B) cho dữ liệu nhiễu và lạc quan hơn so với dữ liệu mượt (Gorilla khoảng 1–2 B). Phải đo trên dữ liệu thật (Q-F03).
- Tổng hợp 5 phút cho mọi điểm: ~100 B/hàng chưa nén và ~20 B/hàng nén. Mỗi hàng giữ avg, min, max, first, last, count, integral, quality.

| Đại lượng | 1 site | 100 site | 1.000 site | 10.000 site |
|---|---|---|---|---|
| Mẫu ở edge, 1 s (chỉ lưu cục bộ) | 86,4 M/ngày | — | — | — |
| Mẫu lên cloud/ngày | 3,02 M | 302 M | 3,02 B | 30,2 B |
| Tốc độ ingest trung bình | 35 mẫu/s | 3.500/s | 35.000/s | 350.000/s |
| Raw chưa nén/ngày | 0,24 GB | 24 GB | 242 GB | 2,4 TB |
| Raw nén/ngày | 15 MB | 1,5 GB | 15 GB | 151 GB |
| **Raw nén/năm** | 5,5 GB | **0,55 TB** | **5,5 TB** | **55 TB** |
| Hàng tổng hợp 5 phút/ngày | 288 k | 28,8 M | 288 M | 2,88 B |
| Tổng hợp 5 phút nén/năm | 2,1 GB | 210 GB | 2,1 TB | 21 TB |
| Hàng ngày/tháng | không đáng kể | | | |

- **Đỉnh ingest:** sau một sự cố mất mạng diện rộng, nhiều site cùng xả buffer. Phải thiết kế cho **5–10× trung bình** và có giới hạn tốc độ xả (backfill rate limit) ở edge. Ví dụ 1.000 site: 175–350 k mẫu/s trong giờ hồi phục.
- **Băng thông/site:** JSON thô khoảng 60 B/mẫu, tức khoảng 180 MB/ngày, hay khoảng 5,4 GB/tháng. Gói tin lô nhị phân (Protobuf/CBOR + zstd) khoảng 10–15 B/mẫu, tức khoảng 30–45 MB/ngày, hay khoảng 1–1,4 GB/tháng. So sánh: FusionSolar 1–5 MB/ngày ở 5 phút (Phát hiện #1). [PROPOSAL] Định dạng nhị phân có nén theo lô là **bắt buộc** cho site dùng 4G (chuyển cho kiến trúc/tích hợp).
- **Lưu trữ edge:** dữ liệu 1 s của 1.000 điểm nén khoảng 3–8 B/mẫu, tức khoảng 0,26–0,69 GB/ngày. Buffer store-and-forward ở mức cloud (5/60 s) khoảng 45 MB/ngày, nên 30 ngày khoảng 1,4 GB. [PROPOSAL] Edge giữ **1 s trong 7 ngày** (vòng tròn, khoảng 2–5 GB) và **buffer cloud-rate ≥ 30 ngày**. Chọn SSD công nghiệp và lưu ý **độ bền ghi** (TBW); ghi theo lô, không fsync từng mẫu.
- **Giới hạn engine [INFERENCE]:** 35 k mẫu/s (1.000 site) nằm trong khả năng ingest theo lô của một node PostgreSQL/TimescaleDB đủ mạnh (COPY/batch insert). 350 k mẫu/s cộng các truy vấn phân tích đồng thời là vùng nên tách theo tenant/shard hoặc dùng engine cột. Chưa có benchmark nguồn; phải PoC (Q-F03).

### 3.2 Schema chuỗi thời gian: narrow, wide hay lai

| Tiêu chí | Narrow `(series_id, ts, value, quality)` | Wide `(device_id, ts, p, q, u1, u2, …)` | Lai (đề xuất) |
|---|---|---|---|
| Đa hãng, điểm tùy biến | Rất tốt: thêm điểm = thêm hàng catalog | Kém: mỗi model thiết bị một bảng hoặc nhiều cột NULL; phải migrate khi thêm điểm | Narrow cho telemetry; wide/JSONB chỉ cho bảng "latest" và tổng hợp KPI |
| Nén | Tốt nếu `segmentby series_id`, `orderby ts` | Rất tốt (ts dùng chung, giống IoTDB aligned timeseries) | |
| Truy vấn "mọi điểm của thiết bị tại t" | Cần pivot | Tự nhiên | Bảng `latest_value` (hoặc cache) phục vụ màn hình live |
| Đơn vị, kiểu, agg_rule | Lưu trong catalog, không lặp | Gắn trong schema | Catalog |
| Dữ liệu thưa/report-by-exception | Tự nhiên | Tạo nhiều NULL | |
| Upsert dữ liệu trễ | Theo khóa `(series_id, ts)` | Theo `(device_id, ts)`; ghi đè một phần cột rất phức tạp | |

[PROPOSAL] Thiết kế bảng (logic, không phải code):
- `series` (catalog): `series_id`, `tenant_id`, `site_id`, `device_id`, `point_key` (từ điển chuẩn, ví dụ `grid.p_total`, `bess.soc`, `meter.e_imp_total`), `unit` canonical (kW, kWh, %, °C), `kind ∈ {gauge, register, state, setpoint, event}`, `agg_rule`, `sampling_class`, `sign_convention_applied`, `scale_factor_version`, `valid_from/valid_to`. **Đây là chỗ duy nhất** chứa ngữ nghĩa của một chuỗi.
- `ts_gauge(series_id int4, ts timestamptz, v_avg float8, v_min float4, v_max float4, n int2, quality int4)`: mỗi hàng là một khoảng tổng hợp tại nguồn (5 s/60 s), nhãn **cuối khoảng** (C §3.15).
- `ts_register(series_id, ts, raw int8 hoặc numeric, quality)`: giá trị thanh ghi **thô**, luôn giữ lại để tính lại.
- `interval_energy(series_id, bucket_end, kwh numeric(18,6), quality, coverage_pct, calc_version)`: delta 5 phút đã qua máy trạng thái (§3.5).
- `ts_state(series_id, ts, state int4)`: chỉ ghi khi đổi trạng thái.
- `event(…)`: alarm/lệnh/ack; do D/E thiết kế.
- `agg_5m`, `agg_1h`: continuous aggregate. `agg_day_local`, `agg_month_local`: bảng do job ghi, khóa `(site_id, series_or_kpi, local_date)` (§3.9).
- `forecast(series_or_target, issue_time, valid_time, horizon, p10, p50, p90, provider, model_version)`: **hai trục thời gian** (§3.12).
- [INFERENCE] Không dùng `float4` cho thanh ghi điện năng: chỉ có khoảng 7 chữ số có nghĩa, nên 12.345.678,9 kWh sẽ mất phần lẻ. Dùng int8 (Wh hoặc đơn vị gốc × hệ số) hoặc numeric.

### 3.3 So sánh engine lưu trữ chuỗi thời gian

| Tiêu chí | TimescaleDB (TSL) | InfluxDB 3 Core / Enterprise | ClickHouse | QuestDB | Apache IoTDB | Parquet + object storage (DuckDB/Trino/Spark) |
|---|---|---|---|---|---|---|
| Mô hình | Extension PostgreSQL; hypertable; SQL đầy đủ; JOIN với metadata | Parquet trên object storage; SQL (DataFusion) + InfluxQL [FACT #7] | DB cột MergeTree; SQL; codec DoubleDelta/Gorilla/T64 [FACT #7] | DB cột; SQL + `SAMPLE BY`, `FILL` [FACT #7] | Tree/table model; TsFile; aligned timeseries [FACT #7] | File cột; không phải DB, cần engine truy vấn |
| Tổng hợp tăng dần | Continuous aggregate, refresh tăng dần [FACT #3] | [UNKNOWN] Chưa thấy tài liệu tương đương trong kết quả tìm kiếm (có plugin/trigger xử lý?) | Materialized view tính lúc insert (không tự tính lại khi UPDATE) [FACT #7; INFERENCE về UPDATE] | `SAMPLE BY` lúc truy vấn; [UNKNOWN] view tăng dần | [UNKNOWN] | Job batch |
| Dữ liệu trễ/upsert | Upsert theo khóa; DML trên chunk nén được nhưng đắt [INFERENCE] | Ghi trùng khóa thì ghi đè (theo mô hình line protocol) [INFERENCE] | ReplacingMergeTree, dedupe bất đồng bộ; MV không tự sửa [INFERENCE] | Dedup theo khóa khi bật [UNKNOWN chi tiết] | [UNKNOWN] | Viết lại partition |
| Nén | "90%+" / 10–20× [FACT #3, nguồn trái nhau] | Parquet | ~4× dữ liệu mượt, ~20% dữ liệu ngẫu nhiên trong một benchmark cũ — https://medium.com/datadenys/optimizing-timeseries-data-in-clickhouse-c6518a9d6da0 | [UNKNOWN] | Shared ts cho aligned [FACT] | Tốt (dictionary/RLE + zstd) |
| Giấy phép | TSL: free tự host, không bán DBaaS [FACT #4] | Core MIT/Apache; Enterprise thương mại theo core [FACT #7] | Apache 2.0 [INFERENCE — kiến thức nền] | Apache 2.0; Enterprise đóng [FACT #7] | Apache 2.0 [INFERENCE — dự án ASF] | Mở |
| Khớp đội Java/Spring + Postgres | **Rất cao** (JDBC, Flyway, một DB cho metadata + telemetry) | Trung bình | Trung bình (JDBC có; ops mới) | Trung bình (wire protocol PG) | Thấp (hệ sinh thái chủ yếu ở Trung Quốc; JDBC có) | Cao cho batch (Spark/DuckDB), không cho OLTP |
| Đa tenant | RLS của PostgreSQL + schema/DB riêng | Database/bucket theo tenant | Row policy; shard theo tenant | [UNKNOWN] | Phân cấp `root.tenant.site…` | Prefix theo tenant + IAM |
| Điểm mạnh với EMS | Một DB, giao dịch, JOIN biểu giá/metadata; Toolkit `time_weight`, `counter_agg` [FACT #5]; có case năng lượng (SolarNetwork) [FACT #6] | Lưu trữ rẻ trên object storage; LVC cho màn hình live | Phân tích ad hoc rất nhanh ở quy mô 10–100 TB | Ingest nhanh, SQL thân thiện | Hợp mô hình phân cấp thiết bị | Lưu trữ lạnh rẻ; xuất cho khách; data lake |
| Điểm yếu/rủi ro | Mở rộng ghi một node; DML trên nén; khóa giấy phép TSL | Tính năng lịch sử/HA nằm ở Enterprise [FACT]; Core phiên bản mới | UPDATE/late data, MV append-only; thêm hệ thống | Tính năng cluster/HA/Parquet ở Enterprise [FACT] | Cộng đồng/tài liệu tiếng Anh hạn chế [INFERENCE] | Không cho truy vấn tương tác độ trễ thấp |

**Khuyến nghị [PROPOSAL, ứng viên ADR-F1]:**
1. **Giai đoạn MVP → 1.000 site:**
   - TimescaleDB (Community/TSL, tự host hoặc trên hạ tầng của ta; **không** dùng bản Apache-only vì mất compression/CAGG).
   - Raw nén sau 7 ngày. Continuous aggregate 5 phút và 1 h.
   - Tổng hợp ngày/tháng **theo giờ địa phương** do job ghi.
   - PostgreSQL cùng cụm cho metadata (tách DB logic).
2. **Lưu trữ lạnh:** xuất raw và 5 phút sang **Parquet** (partition `tenant/site/yyyy/mm`) trên object storage S3-compatible, theo tháng. Đây cũng là định dạng xuất hàng loạt cho khách. Cách này khớp đề xuất "raw-data ownership, Parquet export" của nghiên cứu FusionSolar trước (`competitors_rebuild.md`).
3. **Điểm chuyển:** khi ingest kéo dài > khoảng 50–100 k mẫu/s, hoặc truy vấn phân tích danh mục > vài giây trên tập > 10 TB:
   - (a) shard TimescaleDB theo tenant/region; hoặc
   - (b) thêm **ClickHouse** làm kho phân tích (đọc từ luồng ingest hoặc Parquet), giữ TimescaleDB cho dữ liệu vận hành và tính tiền.
   - Ngưỡng là INFERENCE và phải xác nhận bằng PoC (Q-F03).
4. **Không chọn** InfluxDB 3 Core hay QuestDB OSS làm kho chính. Lý do: các tính năng ta cần (lịch sử dài, HA) được tài liệu đặt ở bản Enterprise [FACT #7]. Ngoài ra đội không có kinh nghiệm. IoTDB hấp dẫn về mô hình nhưng rủi ro hệ sinh thái. "Không chọn" không có nghĩa sản phẩm đó kém.

### 3.4 Ngữ nghĩa tổng hợp

**Nguyên tắc [PROPOSAL]:**
- (1) Mỗi chuỗi có `agg_rule` trong catalog.
- (2) Tổng hợp lưu dạng **partial ghép được**: sum, count, integral, duration, first, last, min, max. Nhờ đó 5 phút → giờ → ngày được rollup **mà không lấy trung bình của trung bình**.
- (3) KPI tỷ số luôn tính lại từ tử và mẫu (C §3.14a).

| Loại (`agg_rule`) | Ví dụ | Trường lưu ở 5 phút | Rollup lên giờ/ngày | Hiển thị | Bẫy |
|---|---|---|---|---|---|
| `gauge_twa` (trung bình theo thời gian) | P (kW), Q, U, I, T | `integral` (kW·s), `covered_s`, min, max, first, last | `avg = Σintegral / Σcovered_s`; min = min; max = max | avg; dải min–max | Lấy mẫu không đều (report-by-exception, deadband) làm **trung bình mẫu ≠ trung bình thời gian**. Phải dùng LOCF hoặc trapezoid (`time_weight` [FACT #5]) |
| `register_delta` | A+, A−, E sạc/xả, `total_yield` | `delta` (kWh, qua §3.5), `r_first`, `r_last`, flags | Tổng delta | Cột kWh | Không tích phân P khi có thanh ghi (C §3.1) |
| `energy_from_power` (dự phòng) | Thiết bị không có thanh ghi | `integral/3600` (kWh) | Tổng | kWh + cờ ESTIMATED | Sai lệch theo tần suất mẫu |
| `last` | SOC, SOH, cấu hình, firmware | last, first, min, max | last của khoảng cuối; min/max | last | Trung bình SOC vô nghĩa cho báo cáo năng lượng. ΔSOC = last − first. Bước nhảy SOC là sự kiện hiệu chỉnh (C Phát hiện #8) |
| `max_window` (demand) | P_dem 15/30 phút | `E_imp(window)/T_w` ở cửa sổ đúng biên | **max** theo kỳ hóa đơn + thời điểm xảy ra | kW + timestamp | Không lấy max của P tức thời. Không lấy avg của Pmax ngày (C K07) |
| `state_duration` | Trạng thái inverter, mode BESS, curtail active | thời lượng (s) ở mỗi trạng thái, số lần chuyển, last | Tổng thời lượng | % thời gian, timeline | Thiết bị mất kết nối là trạng thái `UNKNOWN`, không phải "dừng" (C §3.12) |
| `setpoint` | P_cmd, export limit | last, số lần đổi, min, max | last/min/max | Bước (step chart) | Vẽ bậc thang, không nội suy tuyến tính |
| `counter_event` | Số alarm, số lệnh | count | Tổng | Cột | |
| `ratio_recompute` | PF, PR, SCR, RTE | Không lưu tỷ số; lưu tử và mẫu | Tính lại | % | PF bình quân = f(ΣkWh, Σkvarh) (C K09) |
| `temperature_extreme` | T cell max | max, time_of_max | max | max + thời điểm | Gửi vị trí cell ở edge |

**Ví dụ vì sao cần trung bình theo thời gian.** Trong 5 phút, một chuỗi theo kiểu report-by-exception (deadband 1 kW) gửi 0 kW tại t = 0 rồi 100 kW tại t = 280 s.
- Trung bình mẫu = 50 kW.
- Trung bình theo thời gian (LOCF) = (0 × 280 + 100 × 20)/300 = **6,7 kW**.
- Sai số gấp 7,5 lần. [INFERENCE — tính toán]

**Biên khoảng.** Integral của một khoảng phải gồm phần từ biên đầu đến mẫu đầu tiên, dùng giá trị LOCF từ khoảng trước. Toolkit gọi đây là "interpolating accessors" [FACT #5]. [PROPOSAL] Nếu khoảng trống trước mẫu đầu dài hơn `max_gap` (mặc định 3 × chu kỳ kỳ vọng) thì không LOCF. Khi đó `covered_s` giảm và coverage hạ.

### 3.5 Lấy điện năng chu kỳ từ thanh ghi tích lũy

Bổ sung cho máy trạng thái của C §3.15 (không lặp lại).

**Quy mô tràn số [INFERENCE — tính toán]:**

| Định dạng thanh ghi | Giá trị lớn nhất | Site 1 MW, CF 20% (~1.752 MWh/năm) tràn sau |
|---|---|---|
| uint16, đơn vị 0,1 kWh | 6.553,5 kWh | **~1,4 ngày** |
| uint32, Wh | 4.294.967 kWh | ~2,45 năm |
| int32 có dấu, Wh | 2.147.483 kWh | ~1,2 năm |
| uint32, 0,1 kWh hoặc kWh | ≥ 429.496.729 kWh | > 200 năm |
| uint64 | — | không thực tế |

[INFERENCE] Tràn số **không phải chuyện lý thuyết**: thanh ghi 32 bit tính bằng Wh tràn trong vòng đời dự án (20–25 năm). Driver phải khai báo `R_wrap` (C X-C05). Pipeline phải phân biệt "tràn" với "reset".

**Quy tắc bổ sung [PROPOSAL]:**
1. **Phân bổ delta vào bucket 5 phút khi mẫu không trùng biên.** Giả sử mẫu thanh ghi ở 12:03:40 và 12:06:10. Delta được chia cho bucket (12:00, 12:05] và (12:05, 12:10] theo **tỷ lệ thời gian**, hoặc theo **profile công suất** nếu có P cùng thiết bị (chính xác hơn khi tải dao động). Gắn cờ `INTERPOLATED` nếu một mẫu biên cách biên hơn `x` giây (mặc định 30 s). C4 (§3.1.2) yêu cầu edge đọc thanh ghi ngay sau biên 5 phút để giảm trường hợp này.
2. **Rung số âm nhỏ.** Một số công tơ/inverter báo giá trị giảm 1 LSB do làm tròn. Nếu `−ε ≤ Δ < 0` với ε = 2 LSB thì đặt Δ = 0, giữ `r_last` bằng giá trị lớn hơn, không ghi reset. Lớn hơn mức đó thì chạy máy trạng thái của C.
3. **Thay công tơ/CT là `AssetEvent`** (C X-C04). Giao diện bắt buộc nhập: thời điểm, chỉ số cuối của công tơ cũ, chỉ số đầu của công tơ mới, tỷ số CT/VT mới, người xác nhận. Pipeline tính lại các bucket từ thời điểm đó (đánh dấu `REVISED`).
4. **Đổi hệ số tỷ lệ** (CT ratio hoặc firmware đổi đơn vị) là một phiên bản mới của `scale_factor_version` có `valid_from`. Không áp hồi tố cho dữ liệu cũ trừ khi người dùng xác nhận đó là sửa lỗi cấu hình. Trường hợp đó cần job tính lại có audit.
5. **Thanh ghi theo ngày** (`daily_yield`): chỉ dùng khi không có thanh ghi trọn đời. Nếu reset không ở gần 00:00 giờ địa phương thì phát cảnh báo cấu hình đồng hồ (C §3.15).
6. **Đối chiếu chéo hằng ngày:**
   - `Σ delta(ngày)` phải bằng `r_last(ngày) − r_first(ngày)` (trừ tràn hoặc reset đã giải thích).
   - Σ inverter so với công tơ PV: lệch > 3% thì phát cảnh báo DQ. Ngưỡng là tham số; tổn thất cáp/biến áp làm lệch có hệ thống.

### 3.6 Dữ liệu trễ, sai thứ tự và tính lại

**Nguồn trễ:** edge mất kết nối (vài giờ–vài ngày); tích hợp cloud-to-cloud của hãng, vốn hỏi lại 7 ngày [FACT #9]; nhập tay; hiệu chỉnh công tơ; biểu giá/EF thay đổi hồi tố.

**Luồng đề xuất [PROPOSAL]:**
1. **Edge** gán `seq` tăng đơn điệu cho mỗi luồng (site, stream) và giữ buffer. Cloud ack theo `seq`. Ingest **idempotent**: upsert theo `(series_id, ts)`; bản ghi trùng với cùng `seq` thì bỏ qua.
2. **Watermark** theo site: `complete_until` = thời điểm mà trước đó mọi luồng đã đủ. Dashboard hiển thị "dữ liệu đầy đủ đến …".
3. **Continuous aggregate** có refresh policy, ví dụ `start_offset = 7 ngày`, `end_offset = 5 phút`, chạy mỗi 5 phút. Dữ liệu trễ ≤ 7 ngày tự được tính lại. [INFERENCE] Với CAGG real-time, phần chưa vật chất hóa được ghép lúc truy vấn.
4. **Dữ liệu trễ > 7 ngày**, hoặc rơi vào chunk đã nén, đi theo "đường trễ":
   - Ghi vào bảng `late_landing`.
   - Đánh dấu `dirty_bucket(site, series, bucket_start, bucket_end)`.
   - Job tính lại sẽ giải nén/ghi lại chunk liên quan (hoặc dùng DML trên chunk nén), refresh CAGG cho khoảng đó, rồi tính lại ngày/tháng địa phương.
   - [INFERENCE] Nén sau 7 ngày cân bằng giữa chi phí DML trên chunk nén và dung lượng. Có thể chỉnh theo độ trễ thực tế đo được (NFR-DATA).
5. **Đóng kỳ (period close):**
   - Báo cáo tháng hoặc hóa đơn bóng **phát hành** sẽ được chụp lại thành snapshot có `report_version`, `data_as_of` (watermark), `calc_version`, `tariff_version`, `ef_version`.
   - Dữ liệu trễ làm thay đổi KPI đã phát hành vượt ngưỡng (ví dụ > 0,5% kWh hoặc bất kỳ thay đổi Pmax nào) sẽ tạo **bản sửa (restatement)** và thông báo cho người nhận. Không ghi đè im lặng.
6. **Hai đồng hồ** (C §3.15): `ts_device`, `ts_edge_received`, `ts_ingested`. Thêm `ts_ingested` vào bảng late để đo độ trễ (SLO).

### 3.7 Cờ chất lượng dữ liệu

[PROPOSAL] Mã hóa trong `quality int4`: 4 bit nguồn gốc + bitmask tình trạng.

| Trục | Giá trị | Ý nghĩa | Ví dụ |
|---|---|---|---|
| Nguồn gốc | `MEASURED` | Đọc trực tiếp từ thiết bị | P từ công tơ |
| | `CALCULATED` | Tính tất định từ các giá trị đo | E_cons từ cân bằng (C K05); P_avg = ΔE/Δt |
| | `ESTIMATED` | Mô hình/giả định có bất định | Tích phân P thay thanh ghi; E_lost cho availability; baseline phản thực |
| | `FORECAST` | Giá trị tương lai, kèm `issue_time` | P50 PV ngày mai |
| | `MANUAL` | Người nhập, kèm `entered_by` và lý do | Chỉ số công tơ đọc tay; hóa đơn EVN |
| | `SUBSTITUTED` | Thay thế theo quy tắc VEE (validate-estimate-edit), kèm `method` | Lấp khoảng trống bằng ngày tương tự |
| Tình trạng (bitmask) | `INTERPOLATED` | Phân bổ trong khoảng trống giữa hai giá trị đo (C §3.15) | |
| | `SUSPECT` | Không qua kiểm tra hợp lý (gai, nhảy), chưa xác nhận | Δ vượt định mức × 1,2 |
| | `OUT_OF_RANGE` | Ngoài giới hạn vật lý/cấu hình | SOC 120% |
| | `STALE` | Giá trị không đổi bất thường lâu (cảm biến đóng băng) | G_POA bằng nhau 2 h giữa trưa |
| | `CLOCK_SUSPECT` | Đồng hồ thiết bị lệch > ngưỡng | |
| | `PARTIAL` | Bucket có coverage < 100% | |
| | `LATE` | Đến sau watermark/đóng kỳ | |
| | `REVISED` | Đã thay đổi sau lần tính đầu | Sau thay công tơ |
| | `ROLLOVER` / `RESET` | Bucket chứa tràn/reset đã xử lý | |
| | `CURTAILED`, `ISLANDED`, `MAINTENANCE` | Ngữ cảnh vận hành dùng để loại trừ trong KPI (C K13, §3.4) | |

- **Lan truyền:** nguồn gốc của KPI dẫn xuất lấy mức "yếu nhất" theo thứ tự MEASURED < CALCULATED < SUBSTITUTED < MANUAL < ESTIMATED. FORECAST không bao giờ trộn vào KPI thực tế. Bitmask lấy OR. `coverage_pct` lấy trung bình có trọng số thời gian.
- **Hiển thị** (chuyển cho 09): MEASURED nét liền; ESTIMATED/SUBSTITUTED nét đứt hoặc tô nhạt và có chú giải; MISSING là khoảng trống; FORECAST có dải P10–P90.
- [INFERENCE] VEE và cờ thay thế là thông lệ của ngành dữ liệu công tơ (MDM). Chưa tìm được nguồn trong phiên (Q-F08).

### 3.8 Quy tắc lấp khoảng trống

| Loại dữ liệu | Khoảng trống | Hiển thị biểu đồ | KPI năng lượng | Hóa đơn bóng / Pmax |
|---|---|---|---|---|
| Gauge (P, T…) | ≤ 3 chu kỳ kỳ vọng | Nối liền (LOCF/linear), không cờ | Không áp dụng (dùng thanh ghi) | — |
| Gauge | > 3 chu kỳ | **Đứt nét**, không nội suy | — | — |
| Thanh ghi, có giá trị hai đầu | bất kỳ | Cột kWh phân bổ theo profile, tô nhạt | Tổng chính xác. Phân bổ theo profile, cờ `INTERPOLATED` | Bucket có `INTERPOLATED` → hóa đơn `INCOMPLETE`. Cửa sổ demand chứa phần nội suy → `UNCERTAIN`, **không** dùng để tạo Pmax (C K07) |
| Thanh ghi, mất đầu hoặc cuối | bất kỳ | Khoảng trống | Tích phân P nếu có (`ESTIMATED`); không có thì `MISSING` | `INCOMPLETE` + khoảng min/max |
| Không có gì (thiết bị chết) | > 1 ngày | Khoảng trống | Tùy chọn `SUBSTITUTED` theo "ngày tương tự" (PV: tỷ lệ bức xạ; tải: cùng thứ tuần trước), **chỉ khi người dùng bật** và có ghi nhãn | Không thay thế cho hóa đơn trừ khi người dùng chấp thuận (MANUAL) |
| SOC | bất kỳ | Khoảng trống | ΔSOC không tính | — |
| Trạng thái | bất kỳ | `UNKNOWN` | Availability tính riêng phần "không xác định" (C K22) | — |

### 3.9 Múi giờ và tổng hợp ngày/tháng

- Lưu UTC; site có `timezone` IANA; ngày/tháng/TOU/kỳ hóa đơn theo giờ địa phương site (đồng ý với C §3.15).
- **Việt Nam (UTC+7, không DST):** ngày địa phương D tương ứng `[D−1 17:00Z, D 17:00Z)`. Bucket 5 phút và 1 h thẳng hàng với cả UTC lẫn giờ địa phương, vì offset là số giờ nguyên. Vì vậy CAGG 5 phút/1 h theo UTC dùng chung được, còn ngày/tháng **phải** gộp từ 1 h theo giờ địa phương.
- **Site có offset không nguyên giờ** (Ấn Độ +5:30, Nepal +5:45): bucket 1 h theo UTC **không** thẳng hàng giờ địa phương. [PROPOSAL] Từ 1 h trở lên, tổng hợp theo giờ địa phương từ bucket 5 phút (hoặc 15 phút).
- [INFERENCE — kiến thức nền, chưa kiểm chứng nguồn] `time_bucket` của TimescaleDB có tham số timezone cho bucket ngày. Nhưng một CAGG dùng chung cho nhiều site khác múi giờ thì không thể bucket theo từng site trong cùng một view. → [PROPOSAL] Bảng `agg_day_local`/`agg_month_local` do job ghi, khóa `(site_id, local_date)`. Job chạy sau nửa đêm địa phương + độ trễ (giống mốc 02:00 của FusionSolar [FACT #1]) và chạy lại khi có dirty bucket.
- **Danh mục nhiều múi giờ:** "hôm nay" của danh mục = tổng các ngày địa phương của từng site có cùng ngày lịch (không phải cùng khoảng UTC). Ghi chú điều này trên báo cáo.
- **Kỳ hóa đơn ≠ tháng lịch:** EVN ghi chỉ số theo ngày chốt của từng khách hàng [UNKNOWN chi tiết]. `billing_period` là thực thể riêng `(site, start_local, end_local)`.
- **Hiển thị:** trục thời gian theo múi giờ site, kèm offset trong tooltip. Người xem ở múi khác vẫn thấy giờ site (tùy chọn chuyển).

### 3.10 Tầng lưu giữ

| Tầng | Độ phân giải | Nơi lưu | Thời gian giữ đề xuất | So sánh FusionSolar (EU) [FACT #1] | Ghi chú |
|---|---|---|---|---|---|
| T0 Edge chi tiết | 1 s (C1/C2), cell-level BMS | Edge SSD (vòng tròn) | 7 ngày | Thiết bị ghi đè vòng tròn | Tải lên theo yêu cầu (sự cố) |
| T0b Edge buffer | Cloud-rate | Edge | ≥ 30 ngày | Khôi phục ≤ 24 h | Chống mất dữ liệu khi mất mạng dài |
| T1 Raw nóng | 5–60 s | TimescaleDB (nén sau 7 ngày) | **13 tháng** (đủ so sánh cùng kỳ năm trước) | 15 tháng | Theo gói: Pro 25 tháng |
| T2 Tổng hợp 5 phút/15 phút | 5/15 phút | TimescaleDB CAGG nén | 5 năm (mặc định), tùy gói đến vòng đời | 15 tháng (giờ) | Đủ cho hóa đơn bóng, Pmax, dự báo huấn luyện |
| T3 Giờ/ngày/tháng/năm | 1 h → năm | TimescaleDB | **Vòng đời dự án (≥ 25 năm)** | 5 năm ngày/tháng; 25 năm năm | Nhỏ, không đáng kể |
| T4 Lưu trữ lạnh | Raw + 5 phút | Parquet trên object storage | Theo hợp đồng (mặc định vòng đời; khách có thể yêu cầu xóa) | — | Khoảng 5,5 GB/site/năm nén. Truy vấn qua job/DuckDB |
| Sự kiện/alarm/lệnh/audit | sự kiện | PostgreSQL | ≥ 5 năm (audit điều khiển: chờ 10) | Charger alarm 6 tháng | Bằng chứng cho tranh chấp/bảo hành |
| Dự báo | `issue_time × valid_time` | TimescaleDB | 2 năm đầy đủ; sau đó chỉ giữ bản day-ahead 1 lần/ngày | — | Cần cho đánh giá độ chính xác |

[UNKNOWN] Quy định Việt Nam về lưu giữ dữ liệu đo đếm hoặc dữ liệu cá nhân áp dụng cho dữ liệu năng lượng C&I (chuyển cho 10/A, Q-F09).

### 3.11 KPI, báo cáo và baseline

**KPI:** dùng bảng K01–K32 của C §3.14. Ghi chú này chỉ thêm yêu cầu về **dữ liệu** của từng nhóm báo cáo.

| Báo cáo | Nội dung | Dữ liệu nguồn | Độ phân giải | Đặc thù |
|---|---|---|---|---|
| R1 Vận hành ngày | Sản lượng PV, nhập/xuất, sạc/xả, SOC min/max, Pmax ngày, alarm, data availability | agg_day_local, events | 5 phút → ngày | Gửi sáng hôm sau, sau khi job ngày chạy xong; ghi "data as of" |
| R2 Năng lượng tháng | K01–K06, K10–K12, chi phí (K25), CO2 (K28–K29) | agg_month_local, tariff | ngày → tháng | Theo **kỳ hóa đơn** hoặc tháng lịch (chọn) |
| R3 Phân tích demand | Top-N cửa sổ 30 phút (thời điểm, kW, thành phần PV/BESS/tải); heatmap ngày × giờ; load duration curve; Pmax có và không có BESS | interval_energy 5 phút → cửa sổ T_w | 5 phút | Cửa sổ `UNCERTAIN` được liệt kê riêng |
| R4 Hiệu suất PV | Yf, PR, PR_T, PR loại trừ curtail, % thời gian loại, curtailment (K15), xếp hạng inverter | G_POA, E_ac | 5 phút → ngày/tháng | Không có G_POA thì PR = N/A |
| R5 BESS | Throughput, EFC, RTE, SOH trend, aux, thời gian ở mỗi mode, giờ derate | PCS/BMS/aux meter | 5 phút → tháng | Ghi ranh giới RTE (C §3.5) |
| R6 Availability | A_t, A_E (PV/BESS), data availability | state_duration, events | 5 phút → tháng | Danh mục loại trừ theo hợp đồng |
| R7 Tiết kiệm | Hóa đơn bóng thực so với baseline; phân rã: tiết kiệm năng lượng, TOU shift, demand, phạt PF | K25–K27 | 30 phút → kỳ | Luôn ESTIMATED, kèm phương pháp |
| R8 Chất lượng dữ liệu | Coverage theo thiết bị, khoảng trống, SUSPECT, sự kiện reset/rollover/thay công tơ, độ trễ ingest | DQ tables | ngày | Báo cáo nội bộ/installer |

**Phương pháp baseline cho tiết kiệm [PROPOSAL]:**

| Mã | Baseline | Cách tính | Dùng khi | Lưu ý |
|---|---|---|---|---|
| B0 | "Không PV, không BESS" | `E_imp_base(k) = max(E_cons(k), 0)` mỗi bucket 5 phút; Pmax_base = max cửa sổ của E_imp_base/T_w; tính hóa đơn cùng `TariffVersion` | Mặc định cho báo cáo giá trị đầu tư | E_cons là CALCULATED từ cân bằng (C K05). Tải nhạy giá (DR) không phản ánh |
| B1 | "Có PV, không BESS" | `E_net_noBESS(k) = E_imp − E_exp + E_ch − E_dis` (= E_cons − E_pv), tách nhập/xuất theo dấu ở từng bucket 5 phút; tính hóa đơn | Đo giá trị riêng của BESS | Phải tính ở 5 phút (không phải ngày) vì demand và TOU phụ thuộc thời điểm. **Xuất lưới bị giới hạn**: PV dư khi không có BESS có thể bị curtail chứ không xuất. Cần mô phỏng export limit, nên đây là ESTIMATED |
| B2 | "Chiến lược tham chiếu" | Mô phỏng lại BESS chạy chiến lược đơn giản (ví dụ tự tiêu thụ thuần) trên cùng dữ liệu | Đo giá trị của tối ưu hóa (M-OPT) so với logic mặc định | Mô phỏng → ESTIMATED; mô hình BESS (RTE, giới hạn) có phiên bản |
| B3 | Hồi quy toàn site (tương tự IPMVP Option C) | Mô hình tải theo thời tiết/lịch, giai đoạn trước–sau | Chỉ cho biện pháp hiệu quả năng lượng phía tải (ngoài phạm vi MVP) | [INFERENCE — kiến thức nền] ASHRAE Guideline 14 đặt ngưỡng CV(RMSE)/NMBE cho mô hình. Chưa kiểm chứng số trong phiên |

- [INFERENCE — kiến thức nền, chưa kiểm chứng nguồn] IPMVP có 4 option: A (cô lập, đo tham số chính), B (cô lập, đo toàn bộ), C (toàn cơ sở), D (mô phỏng hiệu chỉnh). B0/B1 có đo PV/BESS/POC đầy đủ nên gần với **Option B**. Báo cáo ghi "phương pháp tham khảo nguyên tắc IPMVP", không ghi "tuân thủ IPMVP" cho đến khi đối chiếu văn bản (Q-F07).
- **Bẫy:**
  - (a) Tiết kiệm demand **không cộng được theo ngày**. Chỉ tính ở cấp kỳ hóa đơn.
  - (b) BESS sạc từ lưới làm tăng E_imp, nên tiết kiệm năng lượng có thể âm trong khi tiết kiệm TOU/demand dương. Phải hiển thị phân rã.
  - (c) Đổi biểu giá giữa kỳ thì tính theo từng `TariffVersion` có `valid_from`.

### 3.12 Dự báo

**Dự báo PV — chuỗi xử lý [PROPOSAL]:**
1. **Nguồn NWP/vệ tinh** (chọn qua adapter, một hoặc nhiều nhà cung cấp):

| Nhà cung cấp | Đã thấy trong tài liệu [FACT #8] | Chưa rõ |
|---|---|---|
| Solcast | Gói hobbyist PT30M, 10 lượt/ngày, ≤2 mảng; P10/P50/P90 | Gói thương mại: độ phân giải 5/15 phút, giá, SLA |
| Open-Meteo | GTI theo tilt/azimuth; 15 phút với AROME (Tây Âu); thương mại cần API key | Mô hình nào phủ Việt Nam ở 15 phút; giá |
| Meteomatics | MOS 15 ngày, 1 h, `global_rad` | Tham số GTI/PV và độ phân giải lưới cho Việt Nam; giá |
| Khác (Solargis, Meteotest có trong kết quả tìm kiếm) | Meteotest có tham số `gk` (bức xạ mặt nghiêng), `e` (kWh/kWp) — https://api.meteotest.ch/ | Phủ Việt Nam |

   - Gói hobbyist (giới hạn 10 lượt/ngày, mục đích cá nhân) **không** dùng được cho sản phẩm thương mại đa site [INFERENCE].
2. **Mô hình vật lý:** GTI → công suất DC (P0, hệ số nhiệt, T_module ước lượng) → AC (hiệu suất inverter, **clipping** theo kWac, **export limit/curtail**). Thư viện kiểu pvlib ở dịch vụ Python riêng là INFERENCE, quyết định ở 06.
3. **Hiệu chỉnh theo site** (MOS/hồi quy hoặc quantile regression trên sai số lịch sử), sau ≥ 30 ngày dữ liệu đo. Loại chu kỳ curtail khỏi tập huấn luyện. Nếu không, mô hình sẽ "học" curtail thành giảm bức xạ.
4. **Tầm và nhịp:** intraday 0–6 h ở bước 15 phút, cập nhật mỗi 15–60 phút. Day-ahead 48 h ở bước 15/30 phút, cập nhật ≥ 2 lần/ngày. Bước 30 phút của Solcast hobbyist khớp cửa sổ Pmax 30 phút của Việt Nam, nhưng intraday cho peak shaving cần ≤ 15 phút [INFERENCE].
5. **Đầu ra:** P10/P50/P90 (kW, kWh/bucket) cho site và từng nhóm hướng.

**Dự báo tải [PROPOSAL]:**

| Mức | Phương pháp | Dữ liệu cần | Ghi chú |
|---|---|---|---|
| F0 | Seasonal naive: cùng giờ, cùng thứ tuần trước | ≥ 1 tuần | Baseline bắt buộc để tính skill score |
| F1 | Profile trung bình/median theo (thứ, giờ, loại ngày) trên 4–8 tuần + hiệu chỉnh mức gần nhất | ≥ 4 tuần | Bền, dễ giải thích |
| F2 | Gradient boosting (LightGBM/XGBoost) với đặc trưng lịch (thứ, giờ, **ngày lễ Việt Nam, Tết âm lịch**, ca sản xuất), nhiệt độ dự báo, độ trễ (lag) tải | ≥ 3–6 tháng | [INFERENCE] Thông lệ ngành; chưa có nguồn trong phiên. Tết âm lịch cần lịch âm, và tháng Tết là ngoại lệ lớn |
| F3 | Đầu vào từ lịch sản xuất của khách (MES/ERP) hoặc nhập tay "ngày nghỉ" | Tích hợp | Thường cải thiện lớn nhất cho C&I [INFERENCE] |

- Tải ròng sau PV (net load) **không** dự báo trực tiếp. Dự báo tải và PV riêng rồi kết hợp, vì nguồn sai số khác nhau [INFERENCE].
- EV: dự báo theo phiên (số phiên, năng lượng, giờ đến/đi). P1 sau MVP.

**Chỉ số độ chính xác [INFERENCE — kiến thức nền, chưa kiểm chứng nguồn]:**

| Chỉ số | Công thức | Dùng | Bẫy |
|---|---|---|---|
| MAE | `mean|ŷ − y|` (kW hoặc kWh/bucket) | Vận hành | Không so được giữa site khác quy mô |
| nMAE | `MAE / P0` (PV, chuẩn hóa theo **công suất đặt AC hoặc DC — phải ghi rõ**) hoặc `MAE / mean(y)` (tải) | So sánh site/nhà cung cấp | Mẫu số khác nhau làm số khác 2–3 lần. Luôn ghi định nghĩa. Chỉ tính giờ có nắng (ví dụ G > 50 W/m² hoặc góc cao mặt trời > 5°) hay cả ngày cũng phải ghi |
| RMSE / nRMSE | `sqrt(mean(e²))` | Phạt sai số lớn (quan trọng cho peak) | Nhạy với outlier |
| MBE | `mean(ŷ − y)` | Phát hiện lệch hệ thống | Có thể ≈ 0 dù MAE lớn |
| MAPE | `mean|e/y|` | **Không dùng cho PV** | y ≈ 0 (đêm/bình minh) làm MAPE vô hạn; bất đối xứng. Với tải, chỉ dùng khi tải không bao giờ gần 0. Thay bằng WAPE = `Σ|e|/Σy` |
| Skill score | `1 − RMSE_model/RMSE_ref` (ref = persistence/seasonal naive) | Chứng minh giá trị của mô hình | Phải nêu tham chiếu |
| Pinball loss / coverage | Cho P10/P90: tỷ lệ y nằm trong [P10, P90] nên ≈ 80% | Dự báo xác suất | |
| Sai số tại đỉnh | `|Pmax_forecast − Pmax_actual|` theo kỳ; sai thời điểm đỉnh | Peak shaving / M-OPT | Chỉ số này quyết định chi phí, quan trọng hơn MAE cả ngày |

- [PROPOSAL] Lưu forecast **hai trục thời gian** `(issue_time, valid_time)` để đánh giá theo tầm dự báo, và không bao giờ ghi đè dự báo cũ. Mỗi đêm chạy job đánh giá: chỉ số theo site × tầm × nhà cung cấp, hiển thị cho vận hành viên.

### 3.13 Phát hiện bất thường — các mức

| Mức | Kỹ thuật | Ví dụ cụ thể cho PV+BESS | Gọi là gì trong UI | Điều kiện |
|---|---|---|---|---|
| L0 Kiểm tra dữ liệu | Phạm vi vật lý, đơn vị, kiểu; stale; gai; clock skew; rollover/reset | SOC > 100%; G_POA đóng băng; P_pv > 1,2 × kWac; tràn thanh ghi | "Kiểm tra dữ liệu" | Luôn bật, tạo cờ DQ (§3.7), không tạo alarm vận hành trừ khi kéo dài |
| L1 Luật ngưỡng | Ngưỡng cố định/có tham số, có độ trễ (hysteresis) và thời gian tối thiểu | Inverter P = 0 khi G_POA > 200 W/m² quá 15 phút; T cell max > ngưỡng; mất kết nối > 10 phút; xuất > export limit quá 2 s (edge); aux kWh/ngày > ngưỡng | "Quy tắc cảnh báo" | **Không gọi là AI/ML** |
| L2 Thống kê | So sánh đồng cấp (peer): yield inverter so với median các inverter cùng hướng, cờ khi lệch > k·MAD; residual giữa thực tế và mô hình kỳ vọng (PR kỳ vọng × bức xạ); CUSUM/EWMA phát hiện trôi (PR giảm dần, RTE giảm, aux tăng); kiểm tra cân bằng năng lượng (C K31); tương quan chéo phát hiện lệch pha thời gian giữa công tơ | String bẩn/hỏng; suy giảm dần; công tơ cấu hình sai CT/dấu | "Phân tích thống kê" | Cần ≥ 2–4 tuần dữ liệu sạch; ngưỡng k có thể chỉnh; báo cáo tỷ lệ cảnh báo sai |
| L3 ML | Isolation forest/autoencoder trên đặc trưng đa biến; phân loại lỗi có nhãn | Mẫu lỗi PCS/BMS phức tạp | "Mô hình học máy (thử nghiệm)" | Chỉ khi có dữ liệu nhãn (ticket O&M liên kết), có đo precision/recall trên tập kiểm tra và có phiên bản mô hình. Ngoài phạm vi MVP |

- [PROPOSAL] Mọi cảnh báo L1–L3 lưu `detector_type`, `detector_version`, `evidence` (giá trị, ngưỡng, cửa sổ) để giải thích được. Phản hồi của người dùng ("đúng/sai") được lưu làm nhãn cho L3 sau này.
- [PROPOSAL] Bất thường **không bao giờ** tự kích hoạt hành động điều khiển thiết bị. Bảo vệ thuộc BMS/PCS/rơ-le. Phát hiện ở cloud chỉ cảnh báo hoặc đề xuất (khớp ràng buộc của dự án và C X-C06).
- [INFERENCE] Huawei SmartEMO "tự chỉnh peak shaving theo dữ liệu lịch sử" (B-competitors) không cho biết kỹ thuật bên trong. Không suy luận đó là ML.

### 3.14 Xuất dữ liệu và báo cáo định kỳ

| Định dạng | Dùng cho | Quy ước | Giới hạn đề xuất |
|---|---|---|---|
| CSV | Dữ liệu chuỗi (long hoặc wide theo lựa chọn), KPI | UTF-8 **có BOM** (để Excel hiển thị đúng tiếng Việt [INFERENCE]); dấu thập phân `.`; phân cách `,`; thời gian ISO 8601 **có offset** (`2026-10-10T17:30:00+07:00`) và cột UTC; đơn vị trong header (`p_grid_kw`); cột `quality` dạng chữ | Đồng bộ ≤ 100.000 hàng; lớn hơn chạy job nền (async) + link tải hết hạn 7 ngày |
| XLSX | Báo cáo tháng, bảng KPI cho kế toán/khách | Mỗi sheet một bảng; sheet "Metadata" (site, tz, tariff_version, calc_version, data_as_of, định nghĩa KPI) | [INFERENCE — kiến thức nền] Excel giới hạn 1.048.576 hàng/sheet, nên 5 phút × 1 năm × 1 chuỗi = 105.120 hàng là ổn, nhưng 1.000 chuỗi thì không. Dữ liệu chi tiết dùng CSV/Parquet |
| PDF | Báo cáo định kỳ R1–R7 gửi chủ đầu tư | Render server-side từ cùng dữ liệu snapshot; trang đầu ghi phương pháp, phiên bản, cờ ESTIMATED | Khoảng ≤ 20 trang; biểu đồ tĩnh |
| Parquet | Xuất hàng loạt raw/5 phút, data lake của khách | Partition theo site/tháng; schema có `quality` | Không giới hạn hàng; theo quota dung lượng |
| API | Tích hợp | Phân trang theo thời gian; giới hạn cửa sổ theo độ phân giải (ví dụ raw ≤ 7 ngày/lần, 5 phút ≤ 93 ngày/lần, ngày ≤ 10 năm) | Rate limit theo tenant (chuyển cho 06/API) |

- So sánh: FusionSolar có "subscribe and export reports" nhưng định dạng không rõ [FACT/UNKNOWN, nghiên cứu FusionSolar trước]. Người dùng App Store phàn nàn thiếu xuất CSV (`competitors_rebuild.md`). [INFERENCE] Xuất CSV/Parquet đầy đủ là điểm khác biệt rẻ mà có giá trị.
- **Báo cáo định kỳ [PROPOSAL]:**
  - Lịch theo múi giờ site (hoặc tenant cho báo cáo danh mục).
  - Chỉ chạy khi watermark ≥ cuối kỳ, hoặc sau thời gian chờ tối đa (ví dụ 06:00 sáng hôm sau). Nếu chưa đủ thì gửi kèm nhãn "dữ liệu chưa đầy đủ".
  - Người nhận là email hoặc người dùng nội bộ; liên kết tới bản lưu trữ.
  - Có restatement khi dữ liệu trễ thay đổi số (§3.6).
  - Lưu snapshot PDF/XLSX đã gửi ít nhất 5 năm.
- **Bảo mật xuất:** xuất là hành động có audit (ai, phạm vi, thời gian); tôn trọng RBAC theo site; link có chữ ký và hết hạn (chuyển cho 10).

### 3.15 Yêu cầu quản lý chất lượng dữ liệu (tóm tắt, chi tiết ở §4)

Vòng đời DQ: **thu thập** (driver khai báo đơn vị, dấu, R_wrap, nhãn đầu/cuối chu kỳ) → **kiểm tra L0 ở edge và cloud** → **gắn cờ** → **tính delta/tổng hợp có phiên bản** → **đối chiếu** (cân bằng, Σ inverter so với công tơ, thanh ghi so với Σ delta) → **giám sát DQ** (coverage, độ trễ, SUSPECT rate theo site/thiết bị) → **xử lý** (ticket DQ cho installer: "công tơ PV lệch 5% so với Σ inverter") → **sửa có audit** (MANUAL/SUBSTITUTED, REVISED, restatement).

---

## 4. Hệ quả thiết kế cho sản phẩm

Mã `F-Pnn` sẽ được người viết 04 đổi sang `FR-…`/`NFR-DATA-…`. Gợi ý module ở cột 3.

| Mã | Đề xuất [PROPOSAL] | Module gợi ý | Ưu tiên |
|---|---|---|---|
| F-P01 | Catalog chuỗi (`series`) với `kind`, `unit` canonical, `agg_rule`, `sampling_class`, phiên bản hệ số tỷ lệ; mọi chuỗi phải có `agg_rule` trước khi ingest | M-HIST / NFR-DATA | P0 |
| F-P02 | Ba bảng tách biệt: gauge (tổng hợp tại nguồn avg/min/max/n), register (raw int8/numeric), state (khi đổi); cộng `interval_energy` 5 phút | M-HIST | P0 |
| F-P03 | Lớp lấy mẫu C1–C5: edge 1 s; cloud 5 s (C1) / 60 s (C2) / 300 s hoặc khi đổi (C3); thanh ghi ở mọi biên 5 phút; sự kiện tức thời | M-INT / M-MON | P0 |
| F-P04 | Payload nhị phân theo lô có nén (mục tiêu ≤ 15 B/mẫu) cho kênh 4G; burst mode 1 s theo yêu cầu | M-INT | P0 |
| F-P05 | Edge: 1 s giữ 7 ngày; buffer cloud-rate ≥ 30 ngày; `seq` + ack; xả buffer có giới hạn tốc độ | M-INT / NFR-REL | P0 |
| F-P06 | Ingest idempotent theo `(series_id, ts)`; watermark `complete_until` theo site hiển thị trên UI | M-HIST / NFR-DATA | P0 |
| F-P07 | Máy trạng thái delta (C §3.15) + phân bổ theo thời gian/profile + chống rung ±2 LSB + `AssetEvent` thay công tơ/CT + phiên bản hệ số tỷ lệ | M-HIST | P0 |
| F-P08 | Tổng hợp ghép được (integral, covered_s, min, max, first, last, count); `time_weight` LOCF cho gauge; không avg-of-avg | M-HIST | P0 |
| F-P09 | TimescaleDB TSL: raw nén sau 7 ngày; CAGG 5 phút và 1 h, refresh `start_offset` 7 ngày; ngày/tháng địa phương do job ghi | M-HIST (ADR-F1) | P0 |
| F-P10 | Đường dữ liệu trễ: `late_landing` + `dirty_bucket` + job tính lại; restatement báo cáo đã phát hành | M-HIST / M-REP | P0 |
| F-P11 | Cờ chất lượng hai trục (nguồn gốc + bitmask) + `coverage_pct` + `calc_version`; lan truyền "yếu nhất" | NFR-DATA | P0 |
| F-P12 | Quy tắc lấp khoảng trống theo bảng §3.8; không nội suy công suất qua khoảng > 3 chu kỳ; không tạo Pmax từ dữ liệu nội suy | M-HIST / M-REP | P0 |
| F-P13 | Bảng `agg_day_local`/`agg_month_local` khóa `(site, local_date)`; `billing_period` riêng; hỗ trợ offset không nguyên giờ | M-HIST / M-TAR | P0 |
| F-P14 | Tầng lưu giữ T0–T4 theo §3.10; Parquet lưu trữ lạnh theo tháng; retention cấu hình theo gói | M-HIST / NFR-DATA | P1 (T4 P1, còn lại P0) |
| F-P15 | Báo cáo R1–R8; snapshot có `report_version`, `data_as_of`, `tariff_version`, `calc_version`, `ef_version` | M-REP | R1, R2, R3, R8 P0; R4–R7 P1 |
| F-P16 | Baseline B0/B1 cho tiết kiệm, tính ở 5 phút, ghi phương pháp trên báo cáo; B2 (mô phỏng chiến lược) P2 | M-REP / M-OPT | P1 |
| F-P17 | Adapter dự báo PV đa nhà cung cấp; mô hình vật lý có clipping/curtail; hiệu chỉnh theo site; P10/P50/P90; lưu `(issue_time, valid_time)` | M-OPT / M-PV | P1 |
| F-P18 | Dự báo tải F0/F1 ở MVP, F2 (gradient boosting, lịch lễ Việt Nam/Tết) ở P1, F3 (lịch sản xuất) ở P2 | M-OPT | F0/F1 P0 nếu MVP có peak shaving dự báo; ngược lại P1 |
| F-P19 | Đánh giá dự báo hằng đêm: MAE, nMAE (ghi rõ mẫu số), nRMSE, MBE, WAPE, skill so với seasonal naive, sai số đỉnh; **không** dùng MAPE cho PV | M-OPT / M-REP | P1 |
| F-P20 | Bất thường L0 + L1 ở MVP; L2 (peer, residual, CUSUM) ở P1; L3 chỉ khi có nhãn. Nhãn UI trung thực ("Quy tắc", "Thống kê", "ML thử nghiệm") | M-ALM | L0/L1 P0, L2 P1, L3 P2 |
| F-P21 | Xuất CSV (UTF-8 BOM, ISO 8601 có offset, cột quality), XLSX (sheet Metadata), PDF, Parquet; đồng bộ ≤ 100 k hàng, lớn hơn chạy async; có audit | M-REP / M-SEC | P0 (CSV/XLSX/PDF), P1 (Parquet) |
| F-P22 | Báo cáo định kỳ theo múi giờ site; chờ watermark; nhãn "chưa đầy đủ"; lưu snapshot ≥ 5 năm | M-REP | P1 |
| F-P23 | Bảng điều khiển DQ: coverage, độ trễ ingest p50/p95, tỷ lệ SUSPECT, số reset/rollover, lệch Σ inverter so với công tơ; tạo ticket DQ | M-ALM / NFR-DATA | P1 |
| F-P24 | NFR-DATA ứng viên: ingest p95 ≤ 60 s từ edge đến truy vấn được (C2); ≤ 10 s cho C1 live; tính lại dirty bucket ≤ 1 h; job ngày xong ≤ 02:00 giờ địa phương; mất dữ liệu = 0 khi mất mạng ≤ 30 ngày | NFR-DATA / NFR-PERF | P0 (đặt mục tiêu; số cần PoC) |
| F-P25 | PoC hiệu năng: 1.000 site giả lập (3 B mẫu/ngày) trên TimescaleDB; đo tỷ lệ nén thật, ingest, độ trễ CAGG, chi phí DML trên chunk nén | ADR-F1 | P0 (trước khi chốt) |

---

## 5. Evidence ledger

| # | Claim | Source URL | Source type & date | Excerpt/paraphrase | Confidence | Conflicting evidence | Design implication |
|---|---|---|---|---|---|---|---|
| 1 | FusionSolar lấy mẫu 5 phút; giờ trước tổng hợp ở phút thứ 5; khôi phục ≤ 24 h; tính lại 02:00 | https://solisdepot.com/wp-content/uploads/2023/03/FusionSolar-Smart-PV-Management-System-7.0-After-sales-Technical-Training-Slides.pptx.pdf | Slide đào tạo Huawei v7.0 (bản sao nhà phân phối), ~2023; nghiên cứu FusionSolar trước | "Data of the previous hour is summarized at the fifth minute of the next hour" | Med | — | Job ngày địa phương có độ trễ; tính lại khi dữ liệu khôi phục |
| 2 | Lưu giữ EU: 15 tháng thiết bị/15 tháng giờ/5 năm ngày-tháng/25 năm năm; 1–5 MB/ngày | https://digitalpower.huawei.com/en/eu-data-act | Trang chính thức Huawei; nghiên cứu FusionSolar trước | như claim | High | Vùng APAC chưa rõ | Tầng T1–T3; ta giữ ngày/tháng trọn vòng đời |
| 3 | Northbound: lịch sử 10 thiết bị × 3 ngày ở 5 phút/lần | https://support.huawei.com/enterprise/en/doc/EDOC1100358266/b9df65c2/monitoring | Tài liệu Huawei 24.2.0; nghiên cứu FusionSolar trước | "5-minute data of a maximum of 10 devices … in three days" | High | — | Tích hợp cloud-to-cloud phải backfill theo lô, chịu trễ |
| 4 | meteocontrol: đo 5 phút, truyền 15 phút, mỗi đêm hỏi lại 7 ngày | https://help-center.meteocontrol.com/en/vcom-cloud/latest/huawei-fusionsolar-api-1 | Help center vendor; nghiên cứu FusionSolar trước | như claim | High | — | Cửa sổ tính lại tự động ≥ 7 ngày |
| 5 | CAGG làm mới tăng dần, chỉ tính phần thay đổi | https://blog.timescale.com/continuous-aggregates-faster-queries-with-automatically-maintained-materialized-views/ | Blog vendor (qua kết quả tìm kiếm) | "only the data that has changed needs to be computed" | High | — | CAGG 5 phút/1 h, refresh 7 ngày |
| 6 | CAGG là hypertable, bật columnstore với segmentby; nén phụ thuộc orderby/segmentby | https://docs.timescale.com/use-timescale/latest/hypercore/real-time-analytics-in-hypercore | Tài liệu chính thức (qua kết quả tìm kiếm) | như claim | High | — | `segmentby series_id`, `orderby ts` |
| 7 | Nén "90%+ typical" | https://access.crunchydata.com/documentation/timescaledb/2.28.0/ | Mirror tài liệu (qua kết quả tìm kiếm) | "90%+ compression typical" | Med | Blog: 10–20× (https://oneuptime.com/blog/post/2026-01-27-timescaledb-continuous-aggregates/view) | Giả định 5 B/mẫu; phải PoC |
| 8 | Compression/CAGG ở Community (TSL); free tự host; cấm bán DBaaS | https://www.tigerdata.com/docs/about/latest/timescaledb-editions ; https://www.tigerdata.com/legal/licenses | Tài liệu/pháp lý vendor (qua kết quả tìm kiếm) | "cannot sell … Community Edition as a service" | High | Phân chia `/tsl/` từ nguồn thứ cấp | Không dùng bản Apache-only; pháp chế xác nhận (Q-F01) |
| 9 | Toolkit `time_weight` LOCF/linear, `rollup()`; accessor nội suy biên ngày | https://www.tigerdata.com/docs/api/latest/hyperfunctions/time-weighted-calculations/time_weight/ ; https://www.timescale.com/forum/t/toolkit-1-8-0-now-available/700 | Tài liệu + forum vendor (qua kết quả tìm kiếm) | "each average is going to fail to correctly account for the interval before its first data point…" | High | — | Gauge dùng TWA; xử lý biên |
| 10 | `counter_agg` tự phát hiện reset; `delta`, `rate`, `num_resets` | https://pigsty.io/ext/e/timescaledb_toolkit/ ; https://docs.timescale.com/api/latest/analytics/ | Bên thứ ba + tài liệu (qua kết quả tìm kiếm) | như claim | Med | — | Không đủ cho R_wrap/thay công tơ → máy trạng thái riêng |
| 11 | SolarNetwork: ~300 GB, ~312 k datum/ngày, tổng hợp giờ/ngày/tháng tự làm; CAGG là kế hoạch | https://timescale.com/blog/how-solarnetwork-fuels-energy-conservation-with-timescaledb | Blog khách hàng, 2024 (qua kết quả tìm kiếm) | "would like to adopt more TimescaleDB features, such as data retention and continuous aggregates" | Med | Case study nói đã dùng CAGG (https://timescale.com/case-studies/solarnetwork) | Mô hình phù hợp; không chứng minh quy mô |
| 12 | InfluxDB 3 Core MIT/Apache, Parquet/object storage, LVC | https://influxdata.com/blog/influxdb3-open-source-public-alpha | Blog vendor (bản alpha) (qua kết quả tìm kiếm) | như claim | Med | Bản alpha, có thể đã đổi | Không chọn làm kho chính |
| 13 | InfluxDB 3 Enterprise: historical queries, HA, read replica | https://docs.influxdata.com/influxdb3/enterprise/admin/ | Tài liệu vendor (qua kết quả tìm kiếm) | liệt kê tính năng Enterprise | Med | — | Chi phí giấy phép nếu chọn |
| 14 | ClickHouse: codec DoubleDelta/Gorilla/T64; MV cho time series | https://clickhouse.com/docs/ru/faq/use-cases/time-series | Tài liệu chính thức (RU) (qua kết quả tìm kiếm) | như claim | High | — | Phương án mở rộng phân tích |
| 15 | Codec ClickHouse ~4× trên dữ liệu mượt, ~20% trên ngẫu nhiên | https://medium.com/datadenys/optimizing-timeseries-data-in-clickhouse-c6518a9d6da0 | Blog cá nhân, cũ (qua kết quả tìm kiếm) | như claim | Low | — | Nén phụ thuộc nhiễu; PoC dữ liệu thật |
| 16 | QuestDB Apache 2.0; SAMPLE BY FILL; đọc Parquet (8.1); Parquet trên object storage là Enterprise | https://questdb.io ; https://questdb.io/blog/questdb-release-8-1-0 | Trang/blog vendor (qua kết quả tìm kiếm) | "Open source under Apache 2.0" | Med | — | Không chọn làm kho chính |
| 17 | IoTDB tree model (ví dụ nhà máy gió), aligned timeseries chia sẻ cột ts | https://iotdb.apache.org/UserGuide/V1.3.x/Basic-Concept/Data-Model-and-Terminology.html | Tài liệu ASF (qua kết quả tìm kiếm) | "timestamp columns … stored only once" | High | — | Ý tưởng wide/aligned cho rack BMS ở edge |
| 18 | Solcast hobbyist PT30M, 10 lượt/ngày, ≤ 2 mảng | https://docs.solcast.com.au/docs/section/rooftop-sites-hobbyist | Tài liệu vendor (qua kết quả tìm kiếm) | như claim | High | HA integration: tài khoản cũ 50 lượt (https://github.com/BJReplay/ha-solcast-solar) | Cần gói thương mại; 30 phút chưa đủ intraday |
| 19 | Solcast có P10/P50/P90 | https://emhass.readthedocs.io/en/latest/forecasts.html | Tài liệu dự án mở (qua kết quả tìm kiếm) | như claim | Med | — | Schema forecast có phân vị |
| 20 | Open-Meteo GTI theo tilt/azimuth; AROME 15 phút chỉ Tây Âu | https://openmeteo.substack.com/p/global-tilted-irradiance-gti-meteofrance | Blog vendor (qua kết quả tìm kiếm) | như claim | Med | — | Kiểm tra mô hình phủ Việt Nam |
| 21 | Open-Meteo thương mại cần API key, `customer-api` | https://hub.meltano.com/extractors/tap-openmeteo | Tài liệu bên thứ ba (qua kết quả tìm kiếm) | "Optional API key for commercial use" | Low–Med | — | Ngân sách dự báo; không dùng free API cho SaaS |
| 22 | Meteomatics MOS: 15 ngày, 1 h, `global_rad` | https://www.meteomatics.com/en/api/available-parameters/mos-parameters/ | Tài liệu vendor (qua kết quả tìm kiếm) | như claim | Med | — | 1 h quá thô cho intraday; xem sản phẩm khác của hãng |
| 23 | PR = Yf/Yr | https://pvpmc.sandia.gov/modeling-guide/5-ac-system-output/pv-performance-metrics/performance-ratio/ | Sandia PVPMC (qua C-energy-domain) | như claim | High | — | R4 tính lại từ tổng |
| 24 | Báo cáo FusionSolar có "subscribe and export"; định dạng không rõ | https://support.huawei.com/enterprise/en/doc/EDOC1100331328/90b9638d/viewing-and-managing-report | Tài liệu Huawei 24.2.0; nghiên cứu FusionSolar trước | "subscribe to and export reports" | High | — | Báo cáo định kỳ là kỳ vọng tối thiểu |
| 25 | Rollover thanh ghi được Schneider/EnergyCAP xử lý tường minh | https://helpcenter.energycap.com/um/sa/types_of_readings ; https://www.se.com/us/en/faqs/FA239195/ | Help center vendor (qua C-energy-domain, qua kết quả tìm kiếm) | xem C Phát hiện #12 | Med | — | R_wrap trong driver; máy trạng thái |
| 26 | Pmax Việt Nam = trung bình 30 phút | (C-energy-domain ledger #6) | Ghi chú agent C | như claim | Med | Block hay rolling: UNKNOWN | Cửa sổ demand T_w = 30 phút; R3 |
| 27 | Tràn uint16 0,1 kWh ở 1 MW sau ~1,4 ngày; uint32 Wh ~2,45 năm | — (tính toán) | INFERENCE | 6.553,5 kWh; 4.294.967 kWh / 1.752 MWh/năm | High (số học) | — | `R_wrap` bắt buộc |
| 28 | 1.000 site ≈ 35 k mẫu/s, ≈ 5,5 TB/năm nén | — (tính toán, §3.1.3) | INFERENCE | giả định 1.000 điểm, 5 s/60 s, 5 B/mẫu | Med (phụ thuộc giả định) | — | PoC; điểm chuyển ClickHouse/shard |

---

## 6. Câu hỏi mở / UNKNOWN

| Mã | Câu hỏi | Vì sao quan trọng | Cách giải |
|---|---|---|---|
| Q-F01 | TSL có cho phép SaaS EMS dùng TimescaleDB Community khi khách **không** truy vấn DB trực tiếp không? Nếu mở "SQL access" cho khách thì sao? | Rủi ro giấy phép cho kiến trúc lõi | Pháp chế đọc toàn văn TSL; hoặc dùng Tiger Cloud |
| Q-F02 | Tỷ lệ nén thực tế với dữ liệu PV/BESS (nhiễu, nhiều chuỗi thưa) | Chi phí lưu trữ ±3× | PoC F-P25 |
| Q-F03 | Thông lượng ingest và độ trễ CAGG trên một node ở 35 k mẫu/s, đỉnh 350 k | Quyết định shard/ClickHouse | PoC tải giả lập |
| Q-F04 | Số điểm đo thật của các model BESS/PCS phổ biến ở Việt Nam (Huawei, Sungrow, …) qua Modbus | Kích thước site tham chiếu | Agent tích hợp (07) lấy register map |
| Q-F05 | Gói thương mại Solcast/Open-Meteo/Meteomatics: độ phân giải 5/15 phút ở Việt Nam, giá theo site, điều khoản phân phối lại | Chi phí đơn vị/site và khả năng intraday | Liên hệ vendor; tìm kiếm bổ sung |
| Q-F06 | Độ chính xác dự báo bức xạ ở Việt Nam (mùa mưa, mây đối lưu chiều) | Giá trị của peak shaving dựa dự báo | Thử nghiệm song song 2–3 nhà cung cấp trên site pilot ≥ 3 tháng |
| Q-F07 | Văn bản IPMVP (core concepts) và ASHRAE Guideline 14: định nghĩa option, ngưỡng CV(RMSE)/NMBE (chưa kiểm chứng trong phiên) | Cách diễn đạt "tiết kiệm" trên báo cáo; tránh tuyên bố tuân thủ sai | Tìm kiếm bổ sung / mua văn bản |
| Q-F08 | Thực hành VEE của ngành đo đếm (MDM) và quy ước cờ thay thế; EVN có quy định gì cho dữ liệu đo xa? | Tương thích cờ với dữ liệu công tơ EVN nếu nhập | Tìm kiếm bổ sung |
| Q-F09 | Quy định Việt Nam về lưu giữ dữ liệu đo đếm/dữ liệu cá nhân (Nghị định 13/2023 về dữ liệu cá nhân?) áp vào dữ liệu năng lượng C&I và vị trí lưu trữ | Retention, data residency | Agent 10/A |
| Q-F10 | Nhãn thời gian (đầu/cuối chu kỳ) và ngày chốt kỳ của load profile công tơ EVN | Khớp hóa đơn bóng với hóa đơn thật | Thu thập file công tơ thật từ khách pilot |
| Q-F11 | Ngưỡng độ chính xác dự báo tối thiểu để peak shaving dựa dự báo tốt hơn bộ điều khiển phản ứng `P_allow_rest` (C §3.9) | Quyết định có cần dự báo trong MVP | Mô phỏng trên dữ liệu pilot (cùng 08) |
| Q-F12 | `time_bucket` với timezone và CAGG theo từng site: giới hạn thực tế ở phiên bản TimescaleDB hiện hành | Thiết kế bảng ngày địa phương | Đọc tài liệu/PoC |

---

## 7. Vấn đề gửi agent khác

| Mã | Gửi | Vấn đề | Đề xuất |
|---|---|---|---|
| X-F01 | 06 (Kiến trúc), người tổng hợp ADR | Đề xuất ADR-F1: TimescaleDB TSL (nóng/ấm) + Parquet object storage (lạnh) + ClickHouse là phương án mở rộng. Thay đổi so với nghiên cứu cũ: cloud nhận **5–60 s** thay vì 1–5 phút | Ghi ADR kèm điều kiện PoC (F-P25) và Q-F01 về giấy phép |
| X-F02 | 07 (Tích hợp) | Driver phải khai báo `kind` (gauge/register/state/setpoint/event), `R_wrap`, LSB/hệ số, nhãn đầu/cuối chu kỳ; edge đọc thanh ghi ở mọi biên 5 phút; gửi tổng hợp tại nguồn (avg/min/max/n), không gửi mẫu tức thời thưa | Thêm vào template driver (bổ sung C X-C05) |
| X-F03 | 06, 07 (kênh edge–cloud) | Payload nhị phân theo lô có nén (≤ 15 B/mẫu); `seq`/ack; xả buffer có giới hạn tốc độ; burst mode 1 s; edge giữ 1 s/7 ngày và buffer 30 ngày (SSD công nghiệp, chú ý TBW) | Đưa vào thiết kế edge và NFR-REL |
| X-F04 | 05 (Domain) | Thêm thực thể: `Series` (catalog + agg_rule), `IntervalEnergy`, `DirtyBucket`, `Watermark`, `ReportSnapshot(version, data_as_of, …)`, `Forecast(issue_time, valid_time, quantile)`, `BillingPeriod`, `DetectorRun`; bổ sung `AssetEvent` của C | Mô hình hóa trong 05 |
| X-F05 | 08 (Tối ưu) | Dự báo PV/tải: chỉ số đánh giá không dùng MAPE cho PV; cần chỉ số sai số tại đỉnh; dự báo lưu hai trục thời gian; loại chu kỳ curtail khỏi huấn luyện; Solcast hobbyist không dùng được cho thương mại | Đồng bộ với thiết kế M-OPT; cùng giải Q-F11 |
| X-F06 | 09 (UX/UI) | Hiển thị theo cờ (nét đứt/tô nhạt cho ESTIMATED/SUBSTITUTED, khoảng trống cho MISSING, dải P10–P90); watermark "dữ liệu đầy đủ đến …"; trục thời gian theo múi giờ site; setpoint vẽ bậc thang; Pmax kèm thời điểm và số cửa sổ UNCERTAIN | Áp vào wireframe dashboard, lịch sử, báo cáo |
| X-F07 | 04 (Yêu cầu) | Đổi F-P01…F-P25 sang FR-HIST/FR-REP/FR-OPT/FR-ALM/NFR-DATA; F-P24 là NFR ứng viên cần số liệu PoC | Dùng bảng §4 |
| X-F08 | 10 (An toàn) | Xuất dữ liệu có audit, RBAC theo site, link ký và hết hạn; phát hiện bất thường ở cloud không bao giờ tự điều khiển; retention/data residency (Q-F09) | Đưa vào NFR-SEC |
| X-F09 | 11 (Lộ trình) | MVP: L0/L1, R1/R2/R3/R8, CSV/XLSX/PDF, CAGG 5 phút/1 h, ngày địa phương, đường dữ liệu trễ. P1: dự báo PV đa nguồn, L2, R4–R7, Parquet, báo cáo định kỳ. P2: L3 ML, baseline B2 | Đưa vào roadmap |
| X-F10 | C (Domain) | Đồng ý toàn bộ C §3.14–3.15. Bổ sung: (a) chống rung thanh ghi ±2 LSB; (b) tràn uint16 0,1 kWh ở 1 MW sau ~1,4 ngày, nên `R_wrap` là bắt buộc chứ không phải tùy chọn; (c) site có offset không nguyên giờ không dùng được bucket 1 h UTC | Không cần sửa file của C; người tổng hợp dùng cả hai |
| X-F11 | B (Đối thủ) | Khi so sánh "AI/analytics" của đối thủ, phân loại theo mức L0–L3 của §3.13; không suy ra ML từ mô tả marketing (ví dụ SmartEMO "tự chỉnh theo dữ liệu lịch sử", InfinitePower "AI-powered EMS") | Dùng thang L0–L3 trong ma trận đối thủ |
| X-F12 | Người tổng hợp / 01 (Phương pháp) | Hạn mức WebSearch đã hết giữa lượt; các mục ghi "kiến thức nền, chưa kiểm chứng nguồn" (MAPE, IPMVP, ASHRAE 14, giới hạn Excel, time_bucket timezone, giấy phép ClickHouse/IoTDB) cần một lượt tìm kiếm bổ sung | Lên lịch lượt kiểm chứng trước khi phát hành 06/08 |
