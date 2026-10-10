# 14 — Sổ đăng ký nguồn và evidence ledger

[← Mục lục](index.html) · [00 Tóm tắt](00-executive-summary.html) · [01 Phương pháp](01-research-methodology.md) · [02 Thị trường](02-market-and-competitor-analysis.html) · [04 Yêu cầu](04-business-requirements.md) · [07 Tích hợp](07-device-integration.md) · [08 Tối ưu](08-energy-optimization.md) · [10 An toàn](10-security-and-reliability.md) · [13 Rủi ro](13-open-questions-and-risks.md) · [K vòng 1](notes/K-review-round1.md) · [15 Mô phỏng](15-simulators-and-messaging.md)

- **Phiên bản:** 1.0 · **Ngày:** 2026-10-10 · **Trạng thái:** bản phát hành nội bộ, chờ lượt kiểm chứng pháp lý/tiêu chuẩn (xem §7).
- **Người viết:** Source Registrar (sở hữu duy nhất file này và [01-research-methodology.md](01-research-methodology.md)).
- **Phạm vi thu thập:** mọi URL xuất hiện trong `docs/research/ems/*.md`, `docs/research/ems/*.html` và `docs/research/ems/notes/*.md` tại ngày 2026-10-10 (tài liệu 02–11, 13 và ghi chú A, B, C, E, F, G, H, I, K). Thu bằng script quét chuỗi `http(s)://`, giải mã HTML entity, gộp trùng.
- **Kết quả:** 391 chuỗi URL thô → **387 nguồn S-001…S-387** sau khi gộp 2 biến thể và loại 3 chuỗi không phải nguồn (§4.2). Thêm **16 tệp nghiên cứu FusionSolar trước** thành S-388…S-403 (§3). Evidence ledger có **100 claim** (EL-001…EL-100, §5).
- **Giới hạn quan trọng:** không có URL nào được mở trực tiếp trong lượt nghiên cứu EMS. Fetch bị chặn. Hạn mức WebSearch dùng chung (200 lượt) đã hết trước khi Registrar bắt đầu: truy vấn spot-check duy nhất của Registrar trả về "web search budget is used up". Vì vậy sổ này **không xác minh lại nội dung** của bất kỳ URL nào. Nó chỉ ghi nhận URL, loại nguồn, cách các agent đã tiếp cận và claim mà tài liệu dựa vào. Vòng review cuối cũng không còn hạn mức WebSearch, nên **chưa reviewer nào spot-check URL nào** trong S-001…S-387 (V-14). Chi tiết về hệ quả ở [01 §6](01-research-methodology.md#6-giới-hạn-mạng-và-hệ-quả-lên-độ-tin-cậy).

---

## Mục lục

- [0. Cách đọc sổ](#0-cách-đọc-sổ)
- [1. Thống kê nhanh](#1-thống-kê-nhanh)
- [2. Bảng nguồn S-001…S-387](#2-bảng-nguồn-s-001s-387)
- [3. Tệp nghiên cứu trước S-388…S-403](#3-tệp-nghiên-cứu-trước-s-388s-403)
  - [3.1 Bảng quy đổi mã tạm L/FS sang S-ID](#31-bảng-quy-đổi-mã-tạm-lfs-sang-s-id)
- [4. URL đáng ngờ, nguồn bị loại và chuỗi không phải nguồn](#4-url-đáng-ngờ-nguồn-bị-loại-và-chuỗi-không-phải-nguồn)
- [5. Evidence ledger (100 claim quan trọng nhất)](#5-evidence-ledger-100-claim-quan-trọng-nhất)
- [6. Claims bị bác bỏ hoặc hạ cấp](#6-claims-bị-bác-bỏ-hoặc-hạ-cấp)
- [7. Hàng đợi kiểm chứng trước khi phát hành](#7-hàng-đợi-kiểm-chứng-trước-khi-phát-hành)
- [8. Quy tắc dùng và mở rộng sổ](#8-quy-tắc-dùng-và-mở-rộng-sổ)
- [9. Vấn đề gửi agent khác](#9-vấn-đề-gửi-agent-khác)

---

## 0. Cách đọc sổ

**Cột của bảng nguồn.**

| Cột | Ý nghĩa |
|---|---|
| S-ID | Mã nguồn duy nhất. Không tái sử dụng mã đã cấp, kể cả khi nguồn bị loại. |
| Tiêu đề / nhà xuất bản | Tên mô tả do Registrar đặt từ ngữ cảnh trích dẫn và đường dẫn URL. **Không phải tiêu đề trang đã kiểm chứng**, vì không trang nào được mở trong lượt này. |
| URL | Đúng chuỗi URL đã xuất hiện trong tài liệu/ghi chú (hoặc dạng đầy đủ nếu tài liệu ghi bị cắt, xem §4.2). |
| Loại nguồn | Một trong: `Vendor official` (trang/tin/blog của hãng), `Vendor press release`, `Vendor blog`, `Datasheet`, `Manual` (kể cả tài liệu API, app note, bản mirror), `Standard body` (IEC, ISO, IEEE, SunSpec, OCA, OpenADR Alliance, OPCF, DNP-UG…), `Regulator` (văn bản/cơ quan nhà nước, EVN, DSO/RTO), `News`, `Law-firm analysis`/`Advisory`, `Academic` (bài báo, phòng thí nghiệm quốc gia, đồ án), `Community` (diễn đàn, mã nguồn mở cộng đồng, wiki cá nhân), `Third-party docs` (tài liệu của bên tích hợp), `Analyst`, `Industry association`, `Distributor/Retailer page`, `AI-generated directory`. |
| Ngày xuất bản | Ngày ghi trong ghi chú agent hoặc suy ra từ đường dẫn URL ("theo URL"/"theo tên file"). `UNKNOWN` khi không có. |
| Cách tiếp cận | `Snippet tìm kiếm`: nội dung chỉ biết qua kết quả WebSearch (tiêu đề + đoạn trích/tóm tắt) trong lượt EMS. `Tệp nghiên cứu FS trước`: URL đã có trong `docs/research/fusionsolar/` (lượt 07/10/2026; một số trang được fetch ở lượt đó, một số chỉ qua snippet, xem chú thích trong tệp FS gốc). **Không có nguồn nào ở trạng thái "đã fetch trong lượt EMS".** |
| Độ tin cậy | `High` / `Med–High` / `Med` / `Low–Med` / `Low`, đánh giá cho **claim chính trong cột cuối**, theo thang ở §0.1. Đã áp mọi phán quyết hạ cấp của [K](notes/K-review-round1.md). |
| Dùng trong | Mã tài liệu: `02`…`13` = deliverable; `nA`…`nK` = ghi chú agent trong `notes/`. |
| Claim chính | Điều nguồn được dùng để hỗ trợ, diễn đạt ngắn. Không phải tóm tắt toàn bộ trang. |

### 0.1 Thang độ tin cậy

| Mức | Điều kiện |
|---|---|
| High | Tài liệu chính thức của chủ thể (hãng về sản phẩm của chính mình, tổ chức tiêu chuẩn về tiêu chuẩn của mình, cơ quan về văn bản của mình) **và** snippet nêu trực tiếp claim, hoặc nghiên cứu FS trước đã đọc tài liệu đó; hoặc hai nguồn độc lập trùng nhau. |
| Med–High | Như High nhưng chỉ một snippet, hoặc tài liệu chính thức qua bản mirror. |
| Med | Báo chí/luật sư/bên thứ ba có uy tín diễn giải; hoặc tài liệu hãng nhưng là tuyên bố tự công bố (chứng nhận, hiệu năng). |
| Low–Med | Nguồn thứ cấp, blog vendor có lợi ích thương mại, hoặc các nguồn mâu thuẫn nhau. |
| Low | Diễn đàn, blog cá nhân, nội dung marketing không có chi tiết, nguồn cũ có thể đã bị thay thế, hoặc chỉ thấy tiêu đề. |

**Trần độ tin cậy do giới hạn mạng.** Vì không trang nào được đọc toàn văn trong lượt EMS, mức "High" ở đây nghĩa là "nguồn mạnh, snippet khớp". Nó **không** tương đương "đã đọc văn bản gốc". Mọi claim pháp lý dùng để đặt yêu cầu bắt buộc phải qua §7 trước khi phát hành.

---

## 1. Thống kê nhanh

| Chỉ số | Giá trị |
|---|---|
| Nguồn URL (S-001…S-387) | 387 |
| Tệp nghiên cứu trước (S-388…S-403) | 16 |
| Cách tiếp cận: snippet tìm kiếm (lượt EMS) | 319 |
| Cách tiếp cận: URL đã có trong nghiên cứu FS trước | 68 |
| Fetch trực tiếp trong lượt EMS | 0 |
| Độ tin cậy High / Med–High / Med / Low–Med / Low | 60 / 51 / 210 / 35 / 31 |
| Nguồn bị loại khỏi vai trò bằng chứng | 2 (rfp.wiki, AI sinh) — §4.3 |
| URL bị gắn cờ cần lưu ý | 16 — §4.1 |
| Văn bản pháp lý Việt Nam đã đọc toàn văn | 0 |
| Tiêu chuẩn IEC/IEEE/ISO đã đọc toàn văn | 0 |
| URL đã được reviewer spot-check (K vòng 1 và vòng review cuối) | 0 — hết hạn mức WebSearch ở cả hai vòng; mọi FACT giữ trần độ tin cậy snippet (§0.1). Chặn phát hành ra bên ngoài tài liệu 02 (V-14, §7) |

Phân bố theo nhóm chủ đề: A. Pháp lý VN 61 · B. Quốc tế 18 · C. Ampowr/InfinitePower 24 · D. Schneider/Siemens/ABB/Wärtsilä 35 · E. SolarEdge/Huawei/Sungrow/SMA 61 · F. OpenEMS/Stem/GridBeyond/giám sát 35 · G. Giao thức 82 · H. Miền năng lượng 31 · I. Dữ liệu 26 · J. Bảo mật 12 · K. Bị loại 2.

---

## 2. Bảng nguồn S-001…S-387

Bảng được nhóm theo chủ đề. URL đặt trong `<…>` để giữ nguyên ký tự đặc biệt. Khi trích trong tài liệu khác, ghi `S-xxx` (ví dụ `[FACT] … (S-016, S-017)`).

### A. Pháp lý, biểu giá và thị trường điện Việt Nam

| S-ID | Tiêu đề / nhà xuất bản | URL | Loại nguồn | Ngày xuất bản | Cách tiếp cận | Độ tin cậy | Dùng trong | Claim chính được hỗ trợ |
|---|---|---|---|---|---|---|---|---|
| S-001 | VBHN 52: NĐ 58/2025 hợp nhất NĐ 243/2026 (cổng vnportal) | <https://storage-vnportal.vnpt.vn/gov-tnn/7350/FileQuanTriTinTuc/VBHN%2052%20Nghi%20dinh%2058%20va%20ND%20243%2030.6.pdf> | Regulator (văn bản hợp nhất) | 30/06/2026 (theo tên file) | Tệp nghiên cứu FS trước | Med (văn bản gốc nhưng chưa ai mở toàn văn) | 08, 11, 13, nA, nC | Trung áp không bán dư cần thiết bị chống phát ngược (qua tóm tắt E/G); cơ sở pháp lý zero-export; ngưỡng đăng ký/đo đếm điện dư (chưa đọc) |
| S-002 | The Investor — Insight into Decree 58 | <https://theinvestor.vn/insight-into-vietnams-decree-58-on-renewable-and-new-energy-d14912.html> | News | 2025 | Snippet tìm kiếm | Med | 02, 13, nA | NĐ 58/2025 thay NĐ 135/2024; ban hành 03/03/2025; trần 20% → 50% (theo NĐ 243) |
| S-003 | Duane Morris Vietnam blog — Decree 58 | <https://blogs.duanemorris.com/vietnam/2025/08/27/vietnam-decree-58-on-development-of-renewable-energy-power-mechanisms-and-policies-for-self-production-and-self-consumption-rooftop-solar-power-systems/> | Law-firm analysis | 27/08/2025 (theo URL) | Snippet tìm kiếm | Med | 02, 13, nA | NĐ 58 hiệu lực ngay, thay NĐ 135/2024 |
| S-004 | VTN Partners — ĐMTMN TSXTTT theo NĐ 58 | <https://vtn-partners.com/news/self-generated-and-self-consumed-rooftop-solar-power-in-vietnam-under-decree-58-2025-nd-cp.html> | Law-firm analysis | 2025 | Snippet tìm kiếm | Med | nA | Trần 20% theo "sản lượng thực phát/tháng" (mâu thuẫn cơ sở tính với ADK) |
| S-005 | ADK Lawyers — chính sách ĐMTMN tự sản tự tiêu | <https://adk-lawyers.com/en/new-policies-rooftop-solar-self-production-self-consumption-vietnam/> | Law-firm analysis | 2025 | Snippet tìm kiếm | Med | nA | Trần 20% theo "công suất lắp đặt" (mâu thuẫn với VTN) |
| S-006 | LuatVietnam — từ 26/6/2026 ĐMTMN được bán tối đa 50% | <https://luatvietnam.vn/tin-van-ban-moi/tu-26-6-2026-dien-mat-troi-mai-nha-duoc-ban-toi-da-50-san-luong-dien-du-186-109883-article.html> | News (pháp luật) | 06/2026 | Snippet tìm kiếm | Med–High | 02, 03, 11, 13, nA | NĐ 243/2026: bán dư ≤ 50% sản lượng thực phát; vượt được đến 31/12/2030 nếu lưới tiếp nhận; vùng chưa có lưới không giới hạn |
| S-007 | Reccessary — Vietnam solar grid export & DPPA | <https://www.reccessary.com/en/news/vietnam-solar-grid-export-dppa> | News | 2026 | Snippet tìm kiếm | Med | 02, 03, 04, 08, 11, 13, nA, nG | NĐ 243: trần 50%; điện xả từ BESS nối ĐMTMN tính là điện dư; mở DPPA cho DC/sạc EV |
| S-008 | Baker McKenzie — Decree 243/2026 | <https://www.bakermckenzie.com/en/insight/publications/2026/06/vietnam-decree-no-243-2026-nd-cp-enhanced-renewable-energy-dppa-framework> | Law-firm analysis | 06/2026 (theo URL) | Snippet tìm kiếm | Med–High | nA | NĐ 243 nâng trần 20% → 50%; khung DPPA |
| S-009 | Norton Rose Fulbright — Vietnam expands DPPA framework | <https://www.nortonrosefulbright.com/en/knowledge/publications/69fad1a7/vietnam-expands-its-dppa-framework> | Law-firm analysis | 2026 | Snippet tìm kiếm | Med | nA | NĐ 243 bỏ ngưỡng bên mua DPPA, bỏ trần giá DPPA vật lý, 7 → 3 bước |
| S-010 | XB Solar — NĐ 243/2026 cho bán 50% | <https://xbsolar.vn/nghi-dinh-243-2026-nd-cp-chinh-thuc-cho-ban-50-dien-mat-troi-mai-nha/> | Vendor blog (installer) | 06/2026 | Snippet tìm kiếm | Low–Med | 05, nC | Trần 50%; BESS tích từ ĐMTMN tính vào điện dư |
| S-011 | An ninh Thủ đô — cho phép bán dư tới 50% | <https://anninhthudo.vn/cho-phep-ban-dien-mat-troi-mai-nha-du-thua-len-toi-50-post657682.antd> | News | 2026 | Snippet tìm kiếm | Med | nC | Trần 50%, cơ sở "sản lượng thực phát" |
| S-012 | Công Thương — ĐMTMN được bán tới 50% sản lượng dư | <https://congthuong.vn/dien-mat-troi-mai-nha-duoc-ban-toi-50-san-luong-dien-du-463096.html> | News | 2026 | Snippet tìm kiếm | Med | nC | Trần 50% sản lượng dư |
| S-013 | VietNamNet — rooftop solar bottleneck | <https://vietnamnet.vn/en/rooftop-solar-saves-billions-of-dong-but-one-bottleneck-remains-2552186.html> | News | 2026 | Snippet tìm kiếm | Med | 02, 03, 04, 08, 11, 13, nA, nG | 28.254 hệ TSXTTT (~1.614 MWp), chỉ ~287 hệ (~16,4 MW) đăng ký bán dư; 130.811 hệ ĐMTMN |
| S-014 | EVN — Rooftop solar still holds significant potential | <https://en.evn.com.vn/d/en-US/news/Rooftop-solar-power-still-holds-significant-development-potential-60-206-501507> | Regulator/utility (EVN) | 2026 | Snippet tìm kiếm | Med–High | nA | Số liệu ĐMTMN cuối 07/2026 |
| S-015 | pv magazine — Vietnam pushes provinces (22/09/2026) | <https://www.pv-magazine.com/2026/09/22/vietnam-pushes-provinces-to-accelerate-rooftop-solar-rollout/> | News | 22/09/2026 | Snippet tìm kiếm | Med | 02, 11, 13, nA | Chưa có giao dịch bán dư nào theo NĐ 243 (08/2026); 2/34 tỉnh ban hành chính sách |
| S-016 | Thư viện Pháp luật — QĐ 963/QĐ-BCT (2026) khung giờ cao/thấp điểm | <https://thuvienphapluat.vn/van-ban/Tai-nguyen-Moi-truong/Quyet-dinh-963-QD-BCT-2026-khung-gio-cao-diem-thap-diem-cua-he-thong-dien-quoc-gia-703327.aspx> | Regulator (văn bản, cổng tra cứu) | 22/04/2026 | Snippet tìm kiếm | Med–High | 02, 03, 04, 08, 11, 13, nA, nG | Cao điểm 17h30–22h30 T2–T7; thấp điểm 0h–6h; CN không cao điểm |
| S-017 | Tuổi Trẻ — BCT đổi khung giờ, buổi tối là cao điểm | <https://tuoitre.vn/bo-cong-thuong-chinh-thuc-thay-doi-khung-gio-tinh-gia-dien-buoi-toi-la-gio-cao-diem-2026042410430101.htm> | News | 24/04/2026 (theo URL) | Snippet tìm kiếm | Med | 02, 08, 09, 13, nA, nG, nH | Xác nhận khung giờ QĐ 963 |
| S-018 | Thời báo Ngân hàng — giá điện theo giờ | <https://thoibaonganhang.vn/gia-dien-theo-gio-ai-co-the-huong-loi-187971.html> | News | 2026 | Snippet tìm kiếm | Low–Med | 03, 04, nA | Khung mới có thể chưa áp vào hóa đơn thực (07/2026) |
| S-019 | VnEconomy — đề xuất sớm áp khung giờ mới | <https://vneconomy.vn/bo-cong-thuong-de-xuat-som-ap-dung-khung-gio-gia-dien-moi.htm> | News | 2026 | Snippet tìm kiếm | Low–Med | nA | Ngày áp hóa đơn của khung mới chưa chắc |
| S-020 | Luật Minh Khuê — giờ cao điểm (khung cũ TT 16/2014) | <https://luatminhkhue.vn/quy-dinh-ve-gio-cao-diem-dien-la-luc-may-gio.aspx> | Legal advisory | UNKNOWN | Snippet tìm kiếm | Med | 03, 04, nA | Khung cũ: cao điểm 9h30–11h30 & 17h–20h; thấp điểm 22h–4h |
| S-021 | Thư viện Pháp luật — toàn văn QĐ 1279/QĐ-BCT 2025 | <https://thuvienphapluat.vn/phap-luat-nha-dat/toan-van-quyet-dinh-1279-qd-bct-2025-quy-dinh-ve-gia-ban-dien-3357.html> | Regulator (văn bản, cổng tra cứu) | 10/05/2025 (hiệu lực) | Snippet tìm kiếm | Med–High | 02, 03, 04, 08, 11, 13, nA | Bảng giá bán lẻ theo cấp điện áp; ví dụ 22–<110 kV 1.190/1.833/3.398 đ/kWh |
| S-022 | LuatVietnam — QĐ 1279/QĐ-BCT | <https://luatvietnam.vn/dien-luc/quyet-dinh-1279-qd-bct-cua-bo-cong-thuong-quy-dinh-ve-gia-ban-dien-399752-d1.html> | Regulator (văn bản, cổng tra cứu) | 05/2025 | Snippet tìm kiếm | Med–High | nA | Như trên; giá bình quân 2.204,0655 đ/kWh |
| S-023 | VietnamFinance — siết quy trình tăng giá điện | <https://vietnamfinance.vn/siet-lai-quy-trinh-tang-gia-dien-evn-khong-the-tu-dieu-chinh-tu-2-tro-len-d147425.html> | News | 07/2026 | Snippet tìm kiếm | Med | nA | NĐ 278/2026 sửa cơ chế điều chỉnh giá (ngưỡng 2%/5%) |
| S-024 | Tạp chí Công Thương — thí điểm giá hai thành phần từ 1/1/2026 | <https://tapchicongthuong.vn/thi-diem-ap-dung-gia-dien-hai-thanh-phan-tu-1-1-2026-218800.htm> | News (ngành) | 2025 | Snippet tìm kiếm | Med | 02, 03, 04, 08, 11, 13, nA, nG | Đối tượng ≥ 200.000 kWh/tháng; song song 01–06/2026; thanh toán thí điểm 07/2026–07/2027; "công suất đăng ký" (cơ sở tính UNKNOWN theo K R-16) |
| S-025 | Luật sư Việt Nam — thí điểm giá hai thành phần đầu 2026 | <https://lsvn.vn/thi-diem-gia-ban-le-dien-hai-thanh-phan-tu-dau-nam-2026-a162900.html> | News | 2025 | Snippet tìm kiếm | Med | nA | Lộ trình thí điểm |
| S-026 | Đại biểu Nhân dân — thử nghiệm giá hai thành phần từ 10/2025 | <https://daibieunhandan.vn/trien-khai-thu-nghiem-gia-ban-le-dien-hai-thanh-phan-tu-thang-10-2025-10390577.html> | News | 2025 | Snippet tìm kiếm | Med–High | 03, 04, 05, 08, 09, nC, nG, nH | Pmax = công suất trung bình chu kỳ tích phân lớn nhất tháng; "chu kỳ tích phân hiện nay đang là 30 phút" |
| S-027 | Tạp chí Công Thương — EVN xây dựng hệ thống giá hai thành phần | <https://tapchicongthuong.vn/evn-xay-dung-he-thong-gia-ban-dien-hai-thanh-phan-264219.htm> | News (ngành) | 2025 | Snippet tìm kiếm | Med | 05, nC, nG | Công tơ đo xa xác định công suất theo chu kỳ 30 phút |
| S-028 | VnExpress — đề xuất thí điểm giá hai thành phần 2026 | <https://vnexpress.net/de-xuat-thi-diem-gia-dien-hai-thanh-phan-tu-2026-4936558.html> | News | 2025 | Snippet tìm kiếm | Med | nC, nG | ≥ 200.000 kWh/tháng; có nguồn nói ≥ 22 kV |
| S-029 | Tuổi Trẻ — từ 1/1/2026 khách ≥ 200.000 kWh áp giá hai thành phần | <https://tuoitre.vn/tu-1-1-2026-khach-hang-su-dung-dien-tu-200-000-kwh-thang-tro-len-se-ap-gia-hai-thanh-phan-20250909101816204.htm> | News | 09/09/2025 (theo URL) | Snippet tìm kiếm | Med | nC | Mốc bắt đầu 1/2026 (mâu thuẫn mốc 10/2025) |
| S-030 | VnEconomy — giá điện cho trạm sạc EV | <https://vneconomy.vn/automotive/quy-dinh-moi-ve-gia-ban-dien-cho-tram-sac-xe-dien.htm> | News | 2025 | Snippet tìm kiếm | Med | 02, 03, 04, 08, 11, 13, nA, nG | Biểu giá riêng trạm sạc EV (QĐ 14/2025, TT 60/2025); trạm kinh doanh có công tơ riêng |
| S-031 | Luật sư Việt Nam — giá điện riêng cho sạc xe điện | <https://lsvn.vn/chinh-thuc-co-quy-dinh-rieng-ve-gia-dien-cho-xe-sac-dien-a166968.html> | News | 2025 | Snippet tìm kiếm | Med | nA | Như trên |
| S-032 | Tilleke & Gibbins — DPPA guidance | <https://www.tilleke.com/insights/clear-guidance-for-direct-power-purchase-agreements-in-vietnam/3/> | Law-firm analysis | 04/2025 | Snippet tìm kiếm | Med | nA | NĐ 57/2025 thay 80/2024; ngưỡng khách lớn ~200.000 kWh/tháng |
| S-033 | Conventus Law — DPPA ảo Việt Nam | <https://conventuslaw.com/featured-content/a-new-way-for-renewable-energy-developers-to-sell-their-electricity-in-vietnam-2/> | Law-firm analysis | UNKNOWN | Snippet tìm kiếm | Med | nC | DPPA ảo: giá thị trường xác định mỗi 30 phút |
| S-034 | VnEconomy EN — QHĐ8 điều chỉnh | <https://en.vneconomy.vn/government-approves-revised-power-development-plan-8.htm> | News | 04/2025 | Snippet tìm kiếm | Med–High | 02, nA | QĐ 768/QĐ-TTg: BESS 10.000–16.300 MW vào 2030 |
| S-035 | Watson Farley & Williams — PDP8 updates | <https://www.wfw.com/articles/vietnam-makes-major-updates-to-power-development-plan-viii/> | Law-firm analysis | 04/2025 | Snippet tìm kiếm | Med–High | nA | Như trên |
| S-036 | Arcus Energy Asia — Thông tư 62/2025 | <https://arcusenergyasia.com/resources/regulations/circular-62> | Advisory | 2026 | Snippet tìm kiếm | Med | 08, nA | TT 62/2025: giá hai thành phần cho BESS độc lập ≥ 10 MW, ≥ 110 kV (FTM) |
| S-037 | Lexology — TT 62/2025 | <https://www.lexology.com/library/detail.aspx?g=e4d68d39-f3ed-44bc-bab9-1187e6fbbceb> | Law-firm analysis | 2026 | Snippet tìm kiếm | Med | nA | IRR trần 12% cho BESS độc lập |
| S-038 | Norton Rose Fulbright — BESS in Vietnam | <https://www.nortonrosefulbright.com/en/knowledge/publications/7eb0008e/development-of-battery-energy-storage-systems-in-vietnam> | Law-firm analysis | 2025 | Snippet tìm kiếm | Med | nA | Mặt trời tập trung kèm BESS ≥ 10% công suất, ≥ 2 h (phạm vi chưa rõ) |
| S-039 | Energy-Storage.news — Vietnam BESS path to 2030 | <https://www.energy-storage.news/vietnams-path-from-zero-bess-deployments-to-meeting-ambitious-2030-energy-storage-targets/> | News | 2025 | Snippet tìm kiếm | Med | nA | Bối cảnh BESS VN |
| S-040 | Energy-Storage.news — EVNHANOI 100 MWh | <https://www.energy-storage.news/hanoi-power-corporation-inaugurates-the-first-100mwh-battery-storage-portfolio-in-vietnamese-capital/> | News | 07/2026 | Snippet tìm kiếm | Med–High | 02, nA | BESS lưới đầu tiên 50 MW/100 MWh (EVNHANOI) |
| S-041 | EVN — EVNNPC commissions first BESS | <https://en.evn.com.vn/d/en-US/news/EVNNPC-commissions-first-BESS-in-Ninh-Binh-60-202-501616> | Regulator/utility (EVN) | 08/2026 | Snippet tìm kiếm | Med–High | nA | EVNNPC 305 MW/610 MWh tại 47 TBA (giai đoạn đầu) |
| S-042 | Thư viện Pháp luật — TT 05/2025/TT-BCT | <https://thuvienphapluat.vn/van-ban/Thuong-mai/Thong-tu-05-2025-TT-BCT-he-thong-truyen-tai-dien-phan-phoi-dien-do-dem-dien-nang-642994.aspx> | Regulator (văn bản, cổng tra cứu) | 2025 | Snippet tìm kiếm | Med | 03, 04, 05, nC | Đ.31: cosφ ≥ 0,9 tại điểm đặt công tơ (đối tượng theo snippet); truyền tải 0,9 nhận / 0,98 phát |
| S-043 | EVN — VBHN 38 (08/2025) | <https://www.evn.com.vn/userfile/User/giangtcdl/files/2025/8/VBHN38-20250814160032345.pdf> | Regulator (văn bản hợp nhất) | 14/08/2025 (theo tên file) | Snippet tìm kiếm | Med | nC | Như trên (hai snippet mô tả đối tượng khác nhau) |
| S-044 | GKO Solar — inverter requirements VN 2026 | <https://www.gkoisolar.com/solar-inverter-requirements-in-vietnam-2026/> | Vendor blog | 2026 | Snippet tìm kiếm | Low | nC | Ride-through, PF > 0,98 cho PV hạ áp (không dùng làm NFR) |
| S-045 | VEPG — Final report technical code revision | <http://vepg.vn/wp-content/uploads/2020/03/81241566_Final-Report-of-Technical-code-revision_EN.pdf> | Technical report (dự án hỗ trợ) | 03/2020 (theo URL) | Snippet tìm kiếm | Low (có thể đã bị thay) | nC | PF 0,95/0,85 khi P > 20% (lịch sử) |
| S-046 | Advantech — QĐ 1570/QĐ-EVN: điều cần biết | <https://www.advantech.com/vi-vn/resources/industry-focus/quyet-dinh-1570qd-evn-dien-mat-troi-mai-nha-dieu-can-biet> | Vendor blog (có lợi ích thương mại) | UNKNOWN | Tệp nghiên cứu FS trước | Low (theo K) | 02, 03, 04, 07, nE, nG | Kết nối điều độ Modbus TCP + IEC 104; "≥ 64 kbps, ≤ 125 ms" (không dùng làm NFR) |
| S-047 | VJOL — bài báo khoa học về kết nối điều độ ĐMTMN | <https://vjol.info.vn/tctbgd/article/view/121843> | Academic | 2025 | Tệp nghiên cứu FS trước | Med | 07, nE | Trung áp bán dư phải kết nối điều độ |
| S-048 | LuatVietnam — Luật 77/2025/QH15 | <https://luatvietnam.vn/cong-nghiep/luat-su-dung-nang-luong-tiet-kiem-va-hieu-qua-sua-doi-2025-so-77-2025-qh15-404895-d1.html> | Regulator (văn bản, cổng tra cứu) | 2025 (hiệu lực 01/01/2026) | Snippet tìm kiếm | Med | nA | Sửa Luật SDNL TK&HQ; nghĩa vụ cơ sở trọng điểm |
| S-049 | Tạp chí Công Thương — 3.491 cơ sở trọng điểm | <https://tapchicongthuong.vn/ban-hanh-danh-sach-gan-3-500-co-so-su-dung-nang-luong-trong-diem-127249.htm> | News | 2023–2024 | Snippet tìm kiếm | Med | nA | 3.491 cơ sở; ngưỡng 1.000 TOE (công nghiệp) |
| S-050 | LuatVietnam — CV 1726/BĐKH-PTCBT (EF lưới 2023) | <https://luatvietnam.vn/dien-luc/cong-van-1726-bdkh-ptcbt-2024-cong-bo-ket-qua-he-so-phat-thai-luoi-dien-viet-nam-425131-d6.html> | Regulator (văn bản) | 2024 | Snippet tìm kiếm | High | 03, 05, nC | EF lưới VN 2023 = 0,6592 tCO2/MWh; 2022 = 0,6766 |
| S-051 | Klinova — EF lưới 2023 | <https://klinova.vn/latest-news/release-of-vietnams-2023-power-grid-emission-coefficient.html> | News/advisory | 2024 | Snippet tìm kiếm | Med–High | 05, nC | Như trên |
| S-052 | Viet Nam News — EF 2024 ước tính | <https://vietnamnews.vn/environment/1716087/study-shows-coal-power-dominant-as-viet-nam-s-grid-emissions-climbed-in-2024.html> | News | 04/2025 | Snippet tìm kiếm | Med | 05, nC | EF 2024 ước tính 0,681 (chưa chính thức) |
| S-053 | DN Kinh tế xanh — ước tính EF 2025 | <https://doanhnghiepkinhtexanh.vn/uoc-tinh-he-so-phat-thai-khi-nha-kinh-cua-luoi-dien-viet-nam-2025-a43738.html> | News | 01/2026 | Snippet tìm kiếm | Low–Med | nC | EF 2024/2025 chưa công bố; ước 2025 = 0,6235; thẩm quyền có thể chuyển BCT |
| S-054 | Tạp chí Công Thương — hội thảo tính EF lưới | <https://tapchicongthuong.vn/hoi-thao-ky-thuat-ve-tinh-toan-he-so-phat-thai-luoi-dien-va-nhiet-dien-than--buoc-tien-trong-minh-bach-hoa-du-lieu-khi-nha-kinh-142455.htm> | News | UNKNOWN | Snippet tìm kiếm | Med | nC | Bối cảnh phương pháp EF |
| S-055 | SolarBK — 227 MWp với Banpu NEXT/Amata | <https://solarbk.vn/en/article/general-news/solarbk-banpu-next-amata-sign-227-mwp-rooftop-deal-bess-becomes-core-infrastructure-as-green-industrial-parks-accelerate-in-november.html> | Vendor official (tự công bố) | 2025 | Snippet tìm kiếm | Med | 02, nA | Mô hình EPC–ESCO đa site |
| S-056 | SolarBK — a year of accelerating | <https://solarbk.vn/en/article/general-news/solarbk-a-year-of-accelerating-central-vietnams-green-transition.html> | Vendor official (tự công bố) | 2026 | Snippet tìm kiếm | Med | nA | Dự án 2,2 MWp + 2,3 MWh BESS |
| S-057 | Năng lượng Việt Nam — KCN Đồng Nai/Bắc Ninh | <https://vietnamenergy.vn/rooftop-solar-and-energy-storage-development-in-industrial-parks-field-insights-from-dong-nai-and-bac-ninh-35553.html> | News (ngành) | 2026 | Snippet tìm kiếm | Med | 02, nA | Amata Biên Hòa 18 MWp/14 nhà máy; áp lực CBAM/CSRD |
| S-058 | pv magazine — Sungrow 2 GW SG110CX Vietnam | <https://www.pv-magazine.com/press-releases/sungrow-hit-2-gw-shipment-of-sg110cx-for-vietnam-rooftops/> | Vendor press release | 12/2020 | Tệp nghiên cứu FS trước | Low–Med (tự công bố) | 02 | Sungrow tự công bố 45% phân khúc mái nhà VN (2020) |
| S-059 | Gantner — five rooftop plants in Vietnam | <https://www.gantner-environment.com/en/news/news-detail/gantner-supplies-to-five-large-rooftop-solar-power-plants-in-vietnam> | Vendor official | UNKNOWN | Tệp nghiên cứu FS trước | Med | 02 | Nền tảng giám sát quốc tế có mặt tại VN |
| S-060 | meteocontrol — reference Đông Nam Việt Packaging | <https://meteocontrol.com/en/company/references/pv-monitoring-for-dong-nam-viet-packaging> | Vendor official (reference) | UNKNOWN | Tệp nghiên cứu FS trước | Med | 02 | meteocontrol có reference tại VN |
| S-061 | meteocontrol — zero feed-in MP Pack | <https://www.meteocontrol.com/en/company/references/zero-feed-in-and-monitoring-for-the-pv-plant-mp-pack> | Vendor official (reference) | 2022 | Tệp nghiên cứu FS trước | Med | 02 | blue'Log XC PPC zero-feed-in tại Đà Nẵng |

### B. Thị trường, chính sách và chuẩn quản lý năng lượng quốc tế

| S-ID | Tiêu đề / nhà xuất bản | URL | Loại nguồn | Ngày xuất bản | Cách tiếp cận | Độ tin cậy | Dùng trong | Claim chính được hỗ trợ |
|---|---|---|---|---|---|---|---|---|
| S-062 | ISO — ISO 50001:2018 | <https://www.iso.org/standard/69426.html> | Standard body | 2018 (rà soát 2024) | Snippet tìm kiếm | High | 02, 03, nA | EnMS: PDCA, EnPI, EnB; là hệ thống quản lý, không phải hệ điều khiển |
| S-063 | ABB — Ability EnergyManager & ISO 50001 | <https://library.e.abb.com/public/97259bfd72d54220a2762fe2a9f75537/ABBAbility_EnergyManager_ISO_50001rev1.pdf> | Vendor official | UNKNOWN | Snippet tìm kiếm | Med | 02, nA | Phần mềm hỗ trợ EnPI/M&V cho ISO 50001 |
| S-064 | DNV — EU EED 2023/1791 & ISO 50001 | <https://www.dnv.com/assurance/Management-Systems/eu-directive-2023-1791-energy-efficiency-iso-50001/> | Certification body | 2023–2024 | Snippet tìm kiếm | High | 02, nA | > 85 TJ phải có EnMS (11/10/2027); > 10 TJ kiểm toán |
| S-065 | gesetze.legal — Directive 2023/1791 Art. 11 | <https://gesetze.legal/eu/rl_2023_1791_eu/11> | Regulator (văn bản EU, cổng thứ ba) | 2023 | Snippet tìm kiếm | High | nA | Như trên |
| S-066 | SEIA — Energy Storage Market Outlook | <https://seia.org/esmo> | Industry association | 2026 | Snippet tìm kiếm | Med | nA | C&I storage Mỹ Q1/2026 648 MWh |
| S-067 | SEIA — ESMO executive summary Q2/2026 | <https://seia.org/media/17746/esmo_executive_summary_q2_2026.pdf/> | Industry association | 2026 | Snippet tìm kiếm | Med | nA | C&I storage Mỹ Q2/2026 1,8 GWh |
| S-068 | Clean Energy Regulator (Úc) — Cheaper Home Batteries | <https://cer.gov.au/batteries> | Regulator | 2026 | Snippet tìm kiếm | Med–High | 02, 03, nA | Pin phải VPP-capable (không bắt buộc tham gia) |
| S-069 | Energy Magazine — 400.000 home batteries | <https://www.energymagazine.com.au/400000-home-batteries-installed-but-barely-a-vpp-in-sight/> | News | 2026 | Snippet tìm kiếm | Med | nA | ~400.000 lắp đặt nhưng ít tham gia VPP |
| S-070 | PNNL — FERC 2222 implementation report | <https://www.pnnl.gov/publications/ferc-order-2222-der-policy-and-implementation-report-january-2026> | Academic/national lab | 01/2026 | Snippet tìm kiếm | Med | nA | Lịch triển khai FERC 2222 theo RTO |
| S-071 | PJM — DER aggregator participation model | <https://www.pjm.com/-/media/DotCom/committees-groups/subcommittees/disrs/postings/updated-der-aggregator-participation-model-full-model-design.pdf> | Regulator/RTO | UNKNOWN | Snippet tìm kiếm | Med | nA | Mô hình tham gia DER aggregator |
| S-072 | EnergyToolBase — demand charge management | <https://energytoolbase.com/blog/energy-storage/mastering-demand-charge-management> | Vendor blog | UNKNOWN | Snippet tìm kiếm | Low–Med | 02, nA | Demand charge 30–70% hóa đơn C&I Mỹ, đỉnh 15 phút (không áp VN) |
| S-073 | Stromnetz Berlin — biểu phí khách đo tải 2011 | <https://www.stromnetz.berlin/files/globalassets/dokumente/entgelte/zugang/entgelte-01.01.2011/entgelte-lastgangkunden-b-2011.pdf> | Regulator/DSO tariff | 2011 | Snippet tìm kiếm | Med (cũ) | nC | Công suất tính tiền = trung bình 15 phút lớn nhất năm |
| S-074 | GridBeyond — VPP vs DERMS vs aggregation | <https://gridbeyond.com/virtual-power-plant-vs-derms-vs-aggregation-whats-the-difference/> | Vendor blog | UNKNOWN | Snippet tìm kiếm | Med | nA | DERMS hướng lưới, VPP hướng thị trường; không có định nghĩa chung |
| S-075 | Next Kraftwerke — DERMS | <https://www.next-kraftwerke.com/knowledge/derms> | Vendor blog | UNKNOWN | Snippet tìm kiếm | Med | nA | Như trên |
| S-076 | Hitachi Energy — Network Manager EMS | <https://www.hitachienergy.com/jp/ja/products-and-solutions1/grid-and-generation-management-network-manager/network-manager-energy-management-system-ems> | Vendor official | UNKNOWN | Snippet tìm kiếm | Med–High | 02, 03, nA | EMS lưới (TSO): SCADA, state estimation, OPF, AGC — ngoài phạm vi |
| S-077 | energy-solutions.co — glossary SCADA/EMS | <https://energy-solutions.co/glossary/terms/scada--ems-integration> | Vendor glossary | UNKNOWN | Snippet tìm kiếm | Low–Med | nA | Định nghĩa EMS lưới |
| S-078 | Redalyc — bài báo về IEEE 2030.7/2030.8 | <https://www.redalyc.org/journal/2913/291374362027/291374362027.pdf> | Academic | UNKNOWN | Snippet tìm kiếm | Med | 02, 03, nA | IEEE 2030.7-2017: dispatch + transition; 2030.8: thử nghiệm |
| S-079 | Nimonik — IEEE 2030.7 listing | <https://www.standards.nimonik.com/products/ieee/ieee-2030pt7/> | Standards store | UNKNOWN | Snippet tìm kiếm | Med | nA | Mô tả phạm vi IEEE 2030.7 |

### C. Đối thủ — Ampowr (seed) và HT InfinitePower (seed)

| S-ID | Tiêu đề / nhà xuất bản | URL | Loại nguồn | Ngày xuất bản | Cách tiếp cận | Độ tin cậy | Dùng trong | Claim chính được hỗ trợ |
|---|---|---|---|---|---|---|---|---|
| S-080 | Ampowr — Cosmos EMS (trang seed của người dùng) | <https://ampowr.com/energy-management-system-ems/> | Vendor official | UNKNOWN | Snippet tìm kiếm | Med | 02, 05, 06, 07, 08, 13, nA, nB | Cosmos điều khiển tài sản phát/lưu/tiêu thụ; > 3.000 datapoint; tích hợp bên thứ ba; peak shaving, self-consumption, trading |
| S-081 | Ampowr — trang chủ | <https://ampowr.com/> | Vendor official | UNKNOWN | Snippet tìm kiếm | Med | 02, nB | Local backup feature; chiến lược EMS |
| S-082 | Ampowr — Peak shaving | <https://ampowr.com/energy-management-system-ems/peak-shaving/> | Vendor official | UNKNOWN | Snippet tìm kiếm | Med | 02, 08, nB, nG | "Switch to energy from battery when grid limit is reached" |
| S-083 | Ampowr — Backup power | <https://ampowr.com/energy-management-system-ems/backup-power/> | Vendor official | UNKNOWN | Snippet tìm kiếm | Med | 02, nB | Chiến lược backup |
| S-084 | Ampowr — Generator steering | <https://ampowr.com/battery-energy-storage-systems/battery-energy-storage-system-generator-steering/> | Vendor official | UNKNOWN | Snippet tìm kiếm | Med | 02, 03, 08, nB, nG | Điều khiển máy phát theo BESS |
| S-085 | Ampowr — Utility-scale BESS | <https://ampowr.com/battery-energy-storage-systems/battery-energy-storage-solutions/utility-scale/> | Vendor official | UNKNOWN | Snippet tìm kiếm | Med | nB | Tuyên bố bảo mật/hosting EU |
| S-086 | Ampowr — imbalance trading | <https://ampowr.com/battery-energy-storage-systems-imbalance-trading/> | Vendor official | UNKNOWN | Snippet tìm kiếm | Med | 02, nB | Giao dịch imbalance (NL) |
| S-087 | Ampowr — case study Gebroeders van Pinxteren | <https://ampowr.com/case-study-gebroeders-van-pinxteren/> | Vendor case study | UNKNOWN | Snippet tìm kiếm | Med | 02, 03, 08, nB, nG | DA + imbalance + aFRR bid đồng thời |
| S-088 | Ampowr — market participation with Cosmos | <https://ampowr.com/energy-optimization-and-market-participation-through-the-use-of-ampowr-cosmos/> | Vendor official | UNKNOWN | Snippet tìm kiếm | Med | nA | Tính năng giao dịch chỉ ở thị trường Hà Lan; €100k/năm là dự báo |
| S-089 | Ampowr — case study Hoge Duin hotel | <https://ampowr.com/hoge-duin-hotel-enhances-energy-efficiency-with-ampifarm-peak-shaving/> | Vendor case study | UNKNOWN | Snippet tìm kiếm | Med | 02, 03, 04, 06, 07, 08, nB, nG | Peak shaving trần 95 kW; Partner API; local backup khi mất mạng |
| S-090 | Ampowr — AmpiHealth | <https://ampowr.com/ampihealth/> | Vendor official | UNKNOWN | Snippet tìm kiếm | Med | 02, 03, 04, nB | > 3.000 điểm giám sát; cảnh báo tới đội hỗ trợ |
| S-091 | Ampowr — NIS2 compliance | <https://ampowr.com/nis2-compliance/> | Vendor official (tự tuyên bố) | 2026 (nhắc đề xuất 3/2026) | Snippet tìm kiếm | Med (tự tuyên bố) | 02, 03, 04, 10, nB, nI | ISO 27001, NIS2, host EU — không thấy registry chứng chỉ |
| S-092 | FME (NL) — case/news nhắc Ampowr | <https://fme.nl/node/14547> | Industry association | UNKNOWN | Snippet tìm kiếm | Low–Med | nC | Ngữ cảnh Ampowr (C ledger #23; claim gốc đã bị K bác vì đi kèm rfp.wiki) |
| S-093 | Eniris — tài liệu tích hợp Ampowr hybrid | <https://manual-sofar.eniris.be/en/Controller/Devices/PV-hybrid-and-battery-inverters/Ampowr> | Third-party docs | UNKNOWN | Snippet tìm kiếm | Med | 07, nE | Unit ID Ampowr hybrid 247 (RTU)/255 (TCP) |
| S-094 | Circontrol — "Cosmos" EV charging | <https://circontrol.com/cosmos-simplifying-ev-charging-management-since-2019/> | Vendor official | UNKNOWN | Snippet tìm kiếm | Med | nB | Sản phẩm trùng tên, KHÔNG liên quan Ampowr (ghi để tránh nhầm) |
| S-095 | HT InfinitePower — What is EMS and its functions (trang seed) | <https://www.infinitepowerht.com/what-is-energy-management-system-ems-and-its-functions.html> | Vendor blog | UNKNOWN | Snippet tìm kiếm | Low (snippet một agent; B không thấy URL trong kết quả — K R-18) | 03, 04, 05, 06, 07, 08, 13, nA, nB, nC, nG | Chỉ định nghĩa chung: EMS điều phối BMS/PCS; giám sát, lập lịch, chẩn đoán (cần nguồn thứ hai: Deye) |
| S-096 | HT InfinitePower — BMS vs EMS | <https://www.infinitepowerht.com/what-is-the-difference-between-bms-and-ems.html> | Vendor blog | UNKNOWN | Snippet tìm kiếm | Low–Med | nA | Phân lớp EMS ↔ BMS |
| S-097 | HT InfinitePower — "AI-Powered EMS" | <https://www.infinitepowerht.com/ai-powered-ems-industrial-energy-storage.html> | Vendor blog (marketing) | UNKNOWN | Snippet tìm kiếm | Low | 02, 03, 04, nB, nC | Chỉ tuyên bố marketing (10–12% giảm phí đỉnh là ví dụ minh họa) — không coi là có AI |
| S-098 | HT InfinitePower — 50 kWh BESS | <https://www.infinitepowerht.com/50kwh-battery-storage-system.html> | Vendor product page | UNKNOWN | Snippet tìm kiếm | Low–Med | 02, nB | EMS: lập lịch, giám sát, truy cập từ xa; CAN/RS-485/Ethernet/Wi-Fi |
| S-099 | HT InfinitePower — C&I storage solutions | <https://www.infinitepowerht.com/commercial-energy-storage-solutions.html> | Vendor product page | UNKNOWN | Snippet tìm kiếm | Low–Med | 02, 07, nB | Như trên (snippet không rõ trang nào) |
| S-100 | HT InfinitePower — 125 kW/261 kWh | <https://www.infinitepowerht.com/125kw-261kwh-commercial-energy-storage-system.html> | Vendor product page | UNKNOWN | Snippet tìm kiếm | Med | 02, nB, nG | Custom logic peak/time-shift/backup; 832 V, 314 Ah, IP55; dải DC mâu thuẫn giữa trang |
| S-101 | HT InfinitePower — 261/522 kWh hybrid | <https://www.infinitepowerht.com/261kwh-522kwh-hybrid-energy-storage-system.html> | Vendor product page | UNKNOWN | Snippet tìm kiếm | Med | 02, 07, nB | Panel + cloud + EMS trạm; firmware từ xa; đẩy cảnh báo |
| S-102 | HT InfinitePower — container 1000 kWh | <https://www.infinitepowerht.com/1000-kwh-battery-outdoor-container-ess.html> | Vendor product page | UNKNOWN | Snippet tìm kiếm | Med | 02, 07, nB | EMS thu thập dữ liệu, điều khiển, màn hình tại chỗ, upload |
| S-103 | HT InfinitePower — container 2000 kWh | <https://www.infinitepowerht.com/2000kwh-battery-outdoor-container-ess.html/> | Vendor product page | UNKNOWN | Snippet tìm kiếm | Med (URL có dấu "/" cuối bất thường) | 02, nB | Lập lịch, peak shaving, SOC, cảnh báo |

### D. Đối thủ — Schneider, Siemens, ABB/Hitachi, Wärtsilä

| S-ID | Tiêu đề / nhà xuất bản | URL | Loại nguồn | Ngày xuất bản | Cách tiếp cận | Độ tin cậy | Dùng trong | Claim chính được hỗ trợ |
|---|---|---|---|---|---|---|---|---|
| S-104 | Schneider — EcoStruxure Microgrid Advisor handout | <https://download.schneider-electric.com/doc/998-20080341_US/EcoStruxure%20Microgrid%20Advisor%20Handout.pdf> | Vendor official (handout) | ~2017 | Snippet tìm kiếm | Low–Med (K R-23) | 02, 06, 08, 09, nA, nB, nG, nH | MPC cloud từ giá/lịch sử/thời tiết; lịch 15 phút/72 h; dự phòng 48 h (48/72 mâu thuẫn) |
| S-105 | Schneider — EcoStruxure Microgrid Advisor (product range; cũng xuất hiện không có "/" cuối) | <https://www.se.com/us/en/product-range/65896/> | Vendor official | UNKNOWN | Snippet tìm kiếm | Med | 02, 03, 08, nA, nB, nG | MPC, edge controller tại site |
| S-106 | Microsoft Marketplace — Microgrid Advisor listing | <https://marketplace.microsoft.com/en-us/product/saas/869296.microgrid_advisor?tab=overview> | Vendor listing | UNKNOWN | Snippet tìm kiếm | Med | 02, 03, 04, nB | "48-hour advance default operation schedules" |
| S-107 | Schneider — EcoStruxure Microgrid design guide (IEC) | <https://www.productinfo.schneider-electric.com/esxp_digital_apps_iec/mg/English/ESXP2GE020EN-05_Microgrid.pdf> | Vendor official (design guide) | UNKNOWN | Snippet tìm kiếm | Low–Med | 02, nB | Edge thực thi plan; cập nhật từ cloud mỗi 15 phút (một kết quả) |
| S-108 | Schneider — ECC demo (Sketchfab) | <https://clients.sketchfab.com/schneider/ecc/index.html> | Vendor demo page | UNKNOWN | Snippet tìm kiếm | Low | 02, nB | Mô tả ECC |
| S-109 | Schneider — Microgrid control solutions for buildings/campuses | <https://download.schneider-electric.com/doc/NRJED116726EN/Microgrid_control_solutions_for_commercial_buildings_and%20campuses_998-20112200_GMA-US.pdf> | Vendor brochure | UNKNOWN | Snippet tìm kiếm | Med–High | 02, 03, nB | Lệnh qua hệ quản lý con (EV, BMS tòa nhà); DR qua utility/aggregator |
| S-110 | Schneider — EcoStruxure Power cybersecurity (IEC 62443) | <https://www.productinfo.schneider-electric.com/esxp_digital_apps_iec/transverse/English/BM_ESXP_DG_Transverse_Section_IEC_0001148082.xml/$/ESXP_DG_SYSD_Cyber_ISA_IEC_0001157270> | Vendor official (design guide) | UNKNOWN | Snippet tìm kiếm | Med | 02, 10, nB, nI | Kiến trúc chứng nhận bên thứ ba theo IEC 62443-3-3; sản phẩm 4-1/4-2 |
| S-111 | Schneider — EcoStruxure Microgrid Operation | <https://www.se.com/ca/en/product-range/65897> | Vendor official | UNKNOWN | Snippet tìm kiếm | Med | 02, 03, nB | PMS on-site, islanding |
| S-112 | pv magazine USA — Schneider microgrid | <https://pv-magazine-usa.com/?p=16812> | News | UNKNOWN | Snippet tìm kiếm | Med | 02, nB | Trình tự islanding |
| S-113 | Schneider — Power Monitoring Expert | <https://www.se.com/sg/en/product-range/65404-ecostruxure-power-monitoring-expert/> | Vendor official | UNKNOWN | Snippet tìm kiếm | Med | 02, 03, nB | PQ, transient, process impact alarm, ISO 50001 |
| S-114 | Schneider — PME 2024 glossary | <https://product-help.schneider-electric.com/EcoStruxure/Power-Monitoring-Expert-2024/content/8_reference/glossary.htm> | Manual | 2024 | Snippet tìm kiếm | Med | 02, nB | Thuật ngữ PME |
| S-115 | Siemens — SICAM Microgrid Control brochure | <https://assets.new.siemens.com/siemens/assets/api/uuid:4b32eeee-ee7c-423e-94f1-ae6a4257a689/MicrogridControlBrochure.pdf> | Vendor brochure | UNKNOWN | Snippet tìm kiếm | Med–High | 02, 03, 08, nB, nG | Blackout detection, black start, SOC mgmt, dự báo, "algorithms fulfill IEC 62898-2" (edition UNKNOWN) |
| S-116 | Siemens — SICAM MGC brochure | <https://assets.new.siemens.com/siemens/assets/api/uuid:159d6566-81b2-4055-974b-7acb5ec05fc7/SICAM-MGC-Brochure.pdf> | Vendor brochure | UNKNOWN | Snippet tìm kiếm | Med–High | 02, nB | Giao thức IEC 60870-5/Modbus; genset dự phòng; thị trường |
| S-117 | Siemens — SICAM Microgrid Control (en-us) | <https://www.siemens.com/en-us/products/microgrids/sicam-microgrid-control/> | Vendor official | UNKNOWN | Snippet tìm kiếm | Med | 02, nB, nI | Tới ~2 GW; IEC 62443, IPSec, crypto chip (tự tuyên bố) |
| S-118 | Siemens — SICAM Microgrid Control (zh-cn) | <https://www.siemens.com/zh-cn/products/microgrids/sicam-microgrid-control/> | Vendor official | UNKNOWN | Snippet tìm kiếm | Med | nB | Như trên |
| S-119 | Siemens — SICAM applications MGC/PPC/DLM (partner day 2022) | <https://assets.new.siemens.com/siemens/assets/api/uuid:9c3aa6dc-3efa-4c27-9c59-ab2664a2b45c/04-var2022-hoermann-sicam-applications-mgc-ppc-dlm-pub.pdf> | Vendor slide | 2022 | Snippet tìm kiếm | Med | 02, nB | IEC 61850 GOOSE ~70 ms cho load shedding (thuộc bảo vệ, không thuộc cloud) |
| S-120 | Siemens — SICAM SCC brochure | <https://assets.new.siemens.com/siemens/assets/api/uuid:4eec54f8-04a2-48cf-9d0d-266a8dcd97e7/SICAM-SCC.pdf> | Vendor brochure | UNKNOWN | Snippet tìm kiếm | Med | 02, nB | SCADA trên WinCC, server dự phòng |
| S-121 | WinCC OA — IEC 62443 certification | <https://www.winccoa.com/documentation/WinCCOA/3.20/en_US/iec_62443/topics/iec_62443_certification.html> | Vendor official (chứng chỉ) | hiệu lực tới 2026-02-06 | Snippet tìm kiếm | Med | 02, 03, 04, 10, nB, nI | Chứng chỉ IEC 62443-4-1/4-2; chưa thấy gia hạn |
| S-122 | Microgrid Knowledge — Siemens utility microgrid whitepaper | <https://img.microgridknowledge.com/files/base/ebm/microgridknowledge/document/2022/09/1663609280032-siemens_utility_microgrid_whitepaper.pdf?dl=1663609280032-siemens_utility_microgrid_whitepaper.pdf> | Vendor whitepaper | 09/2022 | Snippet tìm kiếm | Med | 02, nB | MGMS: dự báo 7 ngày, unit commitment, load shed |
| S-123 | Renewable Energy World — Siemens MGMS | <https://www.renewableenergyworld.com/power-grid/microgrid/siemens-introduces-microgrid-management-for-distributed-power-generation/> | News | UNKNOWN (cũ) | Snippet tìm kiếm | Med | nB | Như trên |
| S-124 | ARC Advisory — Siemens Electrification X | <https://www.arcweb.com/blog/siemens-launches-electrification-x-strengthening-siemens-xcelerator-portfolio-across-buildings> | Analyst | 2024 | Snippet tìm kiếm | Med | 02, 03, nB | Load management cho sạc EV |
| S-125 | Automotive World — Siemens Electrification X | <https://www.automotiveworld.com/news/siemens-launches-electrification-x-strengthening-the-siemens-xcelerator-portfolio-across-buildings-electrification-and-grids/> | News | 2024 | Snippet tìm kiếm | Med | nB | Như trên |
| S-126 | Siemens — Gridscale X | <https://www.siemens.com/en-us/products/gridscale-x/> | Vendor official | UNKNOWN | Snippet tìm kiếm | Med | 02, nB | SaaS vận hành lưới DSO/TSO, không phải EMS C&I |
| S-127 | ABB — launches OPTIMAX | <https://new.abb.com/news/detail/10576/abb-launches-optimaxr-solutions-for-power-generation-industrial-and-commercial-companies> | Vendor news | UNKNOWN | Snippet tìm kiếm | Med | 02, nB | Lập lịch/dispatch DER cho phát điện/công nghiệp/thương mại |
| S-128 | ABB — energy management (power generation) | <https://new.abb.com/power-generation/energy-management> | Vendor official | UNKNOWN | Snippet tìm kiếm | Med | 02, nB | Như trên |
| S-129 | ABB — energy management calculator (subdomain) | <https://energymanagement-calculator.abb.com> | Vendor tool page | UNKNOWN | Snippet tìm kiếm | Low (URL bất thường, xem §4) | nB | Ngữ cảnh OPTIMAX |
| S-130 | ABB — OPTIMAX energy management news | <https://www.abb.com/global/en/company/innovation/news/optimax-energy-management> | Vendor news | 2024 | Snippet tìm kiếm | Med | 02, 03, 04, nB | OPTIMAX 6.4: dự báo tải/phát/giá "AI" (V*, tuyên bố hãng) |
| S-131 | Motion & Mechatronics — AI upgrade ABB EMS | <https://www.motionandmechatronics.ca/product-news/ai-upgrade-to-abb-energy-man/> | News | 06/2024 | Snippet tìm kiếm | Med | 02, nB | Như trên |
| S-132 | gasworld — AI upgrade ABB EMS | <https://www.gasworld.com/story/ai-upgrade-for-abb-energy-management-system/2139961.article> | News | 06/2024 | Snippet tìm kiếm | Med | nB | Như trên |
| S-133 | ABB — e-mesh unified software | <https://new.abb.com/news/detail/15680/abb-launches-unified-software-to-provide-single-view-of-microgrids-and-battery-energy-storage> | Vendor news | 2019 | Snippet tìm kiếm | Med | 02, nB | e-mesh: EMS site/fleet |
| S-134 | Hitachi Energy — grid edge portfolio 2021 | <https://www.hitachienergy.com/news/press-releases/2021/11/hitachi-energy-releases-global-updates-to-grid-edge-solutions-port-folio-including-new-services> | Vendor news | 11/2021 | Snippet tìm kiếm | Med | 02, nB | e-mesh xuất hiện dưới Hitachi Energy |
| S-135 | ABB — divestment of Power Grids to Hitachi | <https://new.abb.com/news/detail/64657/abb-completes-divestment-of-power-grids-to-hitachi> | Vendor news | 2020 | Snippet tìm kiếm | High | 02, nB | ABB bán Power Grids cho Hitachi (2020) |
| S-136 | ABB — Energy and Asset Manager for manufacturing | <https://new.abb.com/about/our-businesses/electrification/abb-ability/energy-and-asset-manager/abb-ability-energy-and-asset-manager-for-manufacturing> | Vendor official | ~2020 | Snippet tìm kiếm | Med | 02, 03, nB | Widget năng lượng, PF, PQ, Group Peak; báo cáo email |
| S-137 | Wärtsilä — GEMS for Duke Energy | <https://www.wartsila.com/media/news/31-08-2020-wartsila-s-gems-to-centrally-manage-multi-state-energy-storage-projects-for-duke-energy-2771911> | Vendor news | 31/08/2020 | Snippet tìm kiếm | Med | 02, nB | GEMS ở quy mô utility, không thấy C&I sau công tơ |
| S-138 | CARILEC — flipbook trang 21 (Wärtsilä PPC) | <https://www.carilec.org/file/flipbook/9/files/basic-html/page21.html> | Industry association | UNKNOWN | Snippet tìm kiếm | Low–Med | nB | Wärtsilä PPC tham chiếu IEC 62443 |

### E. Đối thủ — SolarEdge, Huawei, Sungrow, SMA

| S-ID | Tiêu đề / nhà xuất bản | URL | Loại nguồn | Ngày xuất bản | Cách tiếp cận | Độ tin cậy | Dùng trong | Claim chính được hỗ trợ |
|---|---|---|---|---|---|---|---|---|
| S-139 | SolarEdge — ONE for C&I | <https://www.solaredge.com/us/solaredge-one-for-commercial-and-industrial-energy-optimization-platform> | Vendor official | UNKNOWN | Snippet tìm kiếm | High (tồn tại tính năng) | 02, 03, nB, nG, nH | PV+BESS+EV+tài sản tòa nhà; tối ưu theo biểu giá + thời tiết; peak shaving; live alerts |
| S-140 | Business Wire — SolarEdge ONE for C&I launch | <https://www.businesswire.com/news/home/20241203224482/en> | Vendor press release | 12/2024 | Tệp nghiên cứu FS trước | Med–High | 02, nB, nG | Như trên |
| S-141 | North American Clean Energy — SolarEdge ONE | <https://www.nacleanenergy.com/solar/energy-optimization-solution-for-commercial-and-industrial-sites> | News | 2024 | Snippet tìm kiếm | Med | nB | Như trên |
| S-142 | SolarEdge — ONE for C&I overview | <https://knowledge-center.solaredge.com/sites/kc/files/se-one-for-c&i-overview.pdf> | Vendor official | UNKNOWN | Snippet tìm kiếm | Med–High | 02, 03, nB | Lõi miễn phí cho người mua phần cứng; gói trả phí dần |
| S-143 | SolarEdge — Site Admin in ONE for C&I user guide v1.1 | <https://knowledge-center.solaredge.com/sites/kc/files/se-site-admin-in-solaredge-one-for-c&i-user-guide.pdf> | Manual | UNKNOWN | Snippet tìm kiếm | High | 02, 03, 04, 09, nB, nH | Roles, Monitoring Access, Kiosk, Public, API Access, cảnh báo theo user |
| S-144 | SolarEdge — ONE Controller C&I datasheet | <https://knowledge-center.solaredge.com/sites/kc/files/se-one-controller-commercial-and-industrial-datasheet-eng.pdf> | Datasheet | UNKNOWN | Snippet tìm kiếm | High | 02, 03, 04, 06, 07, 13, nB | 2×RS485, CAN, 2×RJ45, Wi-Fi 6, BLE 5.3, 4DI/4DO; Modbus TCP cổng 1502 |
| S-145 | SolarEdge — ONE Controller for C&I user guide v1.6 | <https://knowledge-center.solaredge.com/sites/kc/files/se-one-controller-for-cni-user-guide-im.pdf> | Manual | 06/2026 | Snippet tìm kiếm | High | 02, nB | Như trên; register map |
| S-146 | Solarmarkt — bản sao manual ONE Controller v1.0 | <https://www.solarmarkt.ch/herstimg/50-Speichersysteme/SolarEdge/MA_EN_SolarEdge_One_Controller.pdf> | Manual (mirror nhà phân phối) | 05/2025 | Snippet tìm kiếm | Med | nB | Như trên |
| S-147 | SolarEdge — feed-in limitation application note v3.0 | <https://knowledge-center.solaredge.com/sites/kc/files/feed-in_limitation_application_note.pdf> | Manual (app note) | 08/2026 | Snippet tìm kiếm | High | 02, 03, 04, nB, nG | Export limitation cần công tơ tại điểm đấu nối; công tơ tiêu thụ không hỗ trợ |
| S-148 | pv magazine — SolarEdge acquires Wevo | <https://www.pv-magazine.com/2024/04/05/solaredge-acquires-ev-charging-optimization-and-management-startup/> | News | 05/04/2024 | Snippet tìm kiếm | Med–High | 02, 03, nB | EV đa hãng, billing, quản lý tải dự báo |
| S-149 | PV Tech — SolarEdge acquires Wevo | <https://www.pv-tech.org/solaredge-acquires-ev-charging-software-startup-wevo/> | News | 04/2024 | Snippet tìm kiếm | Med–High | nB | Như trên |
| S-150 | Huawei — C&I Smart PV Management System | <https://solar.huawei.com/fr/products/ci-smart-pv-management-system/> | Vendor official | UNKNOWN | Tệp nghiên cứu FS trước | Med–High | 02, 03, nB | SmartEMO tự chỉnh peak shaving theo lịch sử; SOC/SOH cell; I-V |
| S-151 | Huawei — SmartPVMS installer | <https://solar.huawei.com/en/products/smart-pv-management-system-installer> | Vendor official | UNKNOWN | Tệp nghiên cứu FS trước | Med | 02, 03, 04 | Installer thêm thiết bị bằng quét QR |
| S-152 | Huawei — Smart PV Plant Management (utility) | <https://solar.huawei.com/en/products/smart-pv-plant-management-system/> | Vendor official | UNKNOWN | Tệp nghiên cứu FS trước | Med | 02 | RESTful API và IEC 104 cho SCADA bên thứ ba |
| S-153 | Huawei — datasheet SmartMGC5000B (theo E) | <https://solar.huawei.com/admin/asset/v1/pro/view/bb9458d9373d4502912378db3cbc7f2d.pdf> | Datasheet | UNKNOWN | Snippet tìm kiếm | Med (số tự công bố) | 02, 03, 04, 06, 07, 08, nE, nG | "closed-loop control for zero feed-in within 2s"; peak shaving ≤ 5 s |
| S-154 | Photomate — SmartLogger5000B | <https://www.photomate.eu/smartlogger5000b> | Distributor page | UNKNOWN | Snippet tìm kiếm | Med (số tự công bố, qua nhà phân phối) | 02, 03, 04, 06, 07, 08, nA, nB, nE, nG | Zero-export ≤ 2 s, peak shaving/capacity control ≤ 5 s; hỗ trợ EMS bên thứ ba |
| S-155 | BayWa r.e. — Huawei SmartLogger5000B | <https://solar-distribution.baywa-re.de/en/commercial-storage/huawei-gs-accessories/huawei-smartlogger5000b.html> | Distributor page | UNKNOWN | Snippet tìm kiếm | Med | nA | Như trên |
| S-156 | Ahlsell — SmartLogger3000 | <https://www.ahlsell.se/products/el/energilager/tillbehor/2741919---smartlogger3000c01> | Retailer page | UNKNOWN | Snippet tìm kiếm | Med | 03, nA | ≤ 200 thiết bị; Modbus-TCP, IEC 60870-5-104 |
| S-157 | Krannich — SmartLogger3000A01EU | <https://shop.krannich-solar.com/es-es/inversores/monitorizacion/10087/smart-logger-3000a01eu?c=469> | Retailer page | UNKNOWN | Snippet tìm kiếm | Med | nA | Như trên |
| S-158 | SKE Solar — bản sao manual LUNA2000-(107-215) C&I Microgrid SmartLogger3000 V07 | <https://ske-solar.com/fileadmin/user_upload/UserManual_LUNA2000-_107-215__C_I-Microgrid-SmartLogger3000_V07_2025-11-30_EN.pdf> | Manual (mirror nhà phân phối) | 30/11/2025 (theo tên file) | Snippet tìm kiếm | Med | 02, nB, nG | Peak shaving chỉ trong kịch bản on/off-grid PQ/VSG — CHỈ trong phạm vi manual này (K R-20); ≤ 20 ESS/30 inverter |
| S-159 | SKE Solar — Quick Guide C&I On-Grid ESS 215 kWh V01 | <https://ske-solar.com/fileadmin/user_upload/QuickGuide_C_I_On-Grid_ESS__Based_on_215KWH_Series_ESS__V01_2024-08-12_EN.pdf> | Manual (mirror nhà phân phối) | 12/08/2024 (theo tên file) | Snippet tìm kiếm | Med | nB | Cấu hình ESS on-grid C&I |
| S-160 | Huawei — EMMA | <https://solar.huawei.com/en/products/EMMA> | Vendor official | UNKNOWN | Snippet tìm kiếm | High (tồn tại tính năng) | 02, 03, 08, nB, nG | Peak shaving, giới hạn feed-in, dự báo dư PV giữ SOC space reserve (hộ/thương mại nhỏ) |
| S-161 | Huawei — EMMA specs | <https://solar.huawei.com/en/professionals/all-products/EMMA/specs> | Datasheet | UNKNOWN | Snippet tìm kiếm | Med | 07, nE | "Supports Modbus-TCP and third-party VPP integration" |
| S-162 | Heima24 — bản sao datasheet EMMA-A02 | <https://www.heima24.de/shop/images/products/media/db-huawei-emma02.pdf> | Datasheet (mirror bán lẻ) | UNKNOWN | Snippet tìm kiếm | Med | 07, nA, nE | Thông số EMMA (số heat pump khác giữa bản) |
| S-163 | Huawei — Northbound control APIs (SmartPVMS 24.x) | <https://support.huawei.com/enterprise/en/doc/EDOC1100379184/7a471100/control-apis> | Manual (API) | 2024–2025 | Tệp nghiên cứu FS trước | High | 02, 03, 04, 07, nB, nE | Control API async task, chỉ OAuth Connect; không gọi lặp trước khi task xong |
| S-164 | Huawei — tài liệu SmartPVMS (EDOC1100492747) | <https://support.huawei.com/enterprise/en/doc/EDOC1100492747> | Manual (API) | UNKNOWN | Tệp nghiên cứu FS trước | High (theo FS) | 07 | Cấu hình pin qua API: task bất đồng bộ, chỉ OAuth Connect |
| S-165 | Huawei — Northbound monitoring APIs 24.2.0 | <https://support.huawei.com/enterprise/en/doc/EDOC1100358266/b9df65c2/monitoring> | Manual (API) | 2024 | Tệp nghiên cứu FS trước | High | 05, 07, nF | Lịch sử ≤ 10 thiết bị × 3 ngày ở 5 phút mỗi lần gọi |
| S-166 | Huawei — viewing and managing reports 24.2.0 | <https://support.huawei.com/enterprise/en/doc/EDOC1100331328/90b9638d/viewing-and-managing-report> | Manual | 2024 | Tệp nghiên cứu FS trước | High | 03, 04, nF | Báo cáo "subscribe and export" |
| S-167 | Huawei — enabling EMMA (SmartPVMS 24.5.0) | <https://support.huawei.com/enterprise/en/doc/EDOC1100376808/a3411c60/enabling-emma> | Manual | 2024–2025 | Tệp nghiên cứu FS trước | High | 08, nG | So sánh có/không EMMA, dự báo 24 h; tắt thì không bật lại trong tháng |
| S-168 | Huawei — SmartLogger3000 kết nối hệ quản lý | <https://support.huawei.com/enterprise/en/doc/EDOC1100108365/4fbe151e/setting-parameters-for-connecting-to-the-management-system-v300r001c00> | Manual | UNKNOWN | Tệp nghiên cứu FS trước | High | 03, 04, 06, 10, nI | Encrypted Modbus TCP outbound cổng 27250; TLS 1.2+; Modbus TCP thường tắt mặc định |
| S-169 | Huawei — SmartLogger set parameters | <https://support.huawei.com/enterprise/en/doc/EDOC1100273864/2b6a3248/set> | Manual | UNKNOWN | Tệp nghiên cứu FS trước | High | 10, nI | Như trên |
| S-170 | Huawei — setting parameters over the app (inverter) | <https://support.huawei.com/enterprise/en/doc/EDOC1100173984/6d72858a/setting-parameters-over-the-app> | Manual | UNKNOWN | Tệp nghiên cứu FS trước | Med | 03, 04, nH | Phát hiện mất liên lạc mặc định 3 s (fail-safe ở thiết bị) |
| S-171 | Huawei — Owner manual 25.2.0 "Battery Control Parameters" | <https://support.huawei.cn/enterprise/en/doc/EDOC1100488067/118cf11f/battery-control-parameters> | Manual (chỉ tiêu đề) | 2025 | Tệp nghiên cứu FS trước | Med (chỉ tiêu đề) | nH | Chủ site có mục tham số pin |
| S-172 | Huawei — installer manual "Setting String Details" | <https://support.huawei.cn/enterprise/en/doc/EDOC1100515204/2cd10883/setting-string-details> | Manual (chỉ tiêu đề) | UNKNOWN | Tệp nghiên cứu FS trước | Med (chỉ tiêu đề) | 03, 04 | Có chức năng cấu hình string |
| S-173 | Huawei — "Data Repair" | <https://support.huawei.cn/enterprise/en/doc/EDOC1100541798/ea4fbfa/data-repair> | Manual (chỉ tiêu đề) | UNKNOWN | Tệp nghiên cứu FS trước | Med (chỉ tiêu đề) | 03, 04 | FusionSolar có mục sửa dữ liệu |
| S-174 | Huawei Digital Power — EU Data Act | <https://digitalpower.huawei.com/en/eu-data-act> | Vendor official | UNKNOWN | Tệp nghiên cứu FS trước | High | 03, 04, 05, 10, nF, nI | Lưu giữ EU 15 tháng/15 tháng/5 năm/25 năm; owner cấp O&M Authorization, thu hồi được |
| S-175 | Huawei — warranty terms (PSTI) | <https://solar.huawei.com/en/service-support/tsc/warranty-terms-and-conditions> | Vendor official | 2024 | Tệp nghiên cứu FS trước | High | 10, nI | Cập nhật bảo mật tới 31/12/2029 |
| S-176 | e-solarshop — bản sao FusionSolar app manual | <https://e-solarshop.ro/wp-content/uploads/2025/07/fusionsolar-app-manual5925.pdf> | Manual (mirror bán lẻ) | 2024–2025 | Tệp nghiên cứu FS trước | High (theo FS) | 08, 10, nG, nI | 3 chế độ ESS: Max self-consumption, Fully fed to grid, TOU; Authorization Management |
| S-177 | SolisDepot — bản sao slide đào tạo FusionSolar 7.0 | <https://solisdepot.com/wp-content/uploads/2023/03/FusionSolar-Smart-PV-Management-System-7.0-After-sales-Technical-Training-Slides.pptx.pdf> | Vendor training (mirror) | ~2023 | Tệp nghiên cứu FS trước | Med | 02, 03, 04, 09, nF, nH | Lấy mẫu 5 phút; tổng hợp giờ ở phút thứ 5; khôi phục ≤ 24 h; alarm → New Ticket; kiosk |
| S-178 | GitHub (HA FusionSolar) — iMaster NetEco NBI reference V600R022C00 | <https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/imaster-neteco-v600r022c00-northbound-interface-reference-v6.pdf> | Manual (mirror cộng đồng) | UNKNOWN | Tệp nghiên cứu FS trước | Med–High | 08, nG | `ch_discharge_model` 0–4; API VPP `chargeAndDischarge` (≤ 100 plant, async) |
| S-179 | VP Solar — FusionSolar software/app/portal | <https://www.vpsolar.com/en/huawei-fusionsolar-softwares-app-and-smartpvms-portal/> | Distributor page | UNKNOWN | Tệp nghiên cứu FS trước | Med | nB | Vai trò installer/owner; dữ liệu 5 phút |
| S-180 | Solytic — set up Huawei FusionSolar API | <https://solytic.com/knowledge/set-up-api-access-huawei-fusionsolar-api/> | Third-party docs | UNKNOWN | Tệp nghiên cứu FS trước | Med | 02, nB | Quy trình cấp API Huawei |
| S-181 | meteocontrol — VCOM Huawei FusionSolar API | <https://help-center.meteocontrol.com/en/vcom-cloud/latest/huawei-fusionsolar-api-1> | Third-party docs | UNKNOWN | Tệp nghiên cứu FS trước | High (theo FS) | 02, 03, 04, 05, 07, nF | Đo 5 phút, truyền 15 phút, mỗi đêm hỏi lại 7 ngày |
| S-182 | Home Assistant forum — Fusion Solar doesn't work anymore | <https://community.home-assistant.io/t/fusion-solar-doesnt-work-anymore/927417> | Community | 09/2025 | Tệp nghiên cứu FS trước | Med | 10, nI | Huawei đổi chính sách API làm hỏng tích hợp bên thứ ba |
| S-183 | Apple App Store — FusionSolar (JP) | <https://apps.apple.com/jp/app/id1529080383> | App store listing (review người dùng) | UNKNOWN | Tệp nghiên cứu FS trước | Low–Med | 03, 04 | Người dùng phàn nàn thiếu xuất CSV |
| S-184 | PyPI — pyhfs (client FusionSolar) | <https://pypi.org/project/pyhfs/> | Community (mã nguồn) | UNKNOWN | Tệp nghiên cứu FS trước | Med | 07 | Đăng nhập thirdData; timestamp thực tế là UTC dù tài liệu ghi giờ nhà máy |
| S-185 | ioBroker forum — bản tải lên "Solar Inverter Modbus Interface Definitions v5" (Huawei) | <https://forum.iobroker.net/assets/uploads/files/1699119419919-solar-inverter-modbus-interface-definitions-v5.pdf> | Manual (mirror diễn đàn) | ~2023 | Tệp nghiên cứu FS trước | Low–Med (bản sao không chính thức) | 07 | Định nghĩa thanh ghi Modbus inverter Huawei (không dùng làm driver VERIFIED khi chưa đối chiếu bản chính thức) |
| S-186 | Sungrow — PowerStack ST255CS-2H | <https://www.sungrowpower.com/mal/en/products/c-i-energy-storage-system/st255cs-2h> | Vendor official | UNKNOWN | Snippet tìm kiếm | Med | 02, 07, nB | EMS/PCS/BMS tích hợp; VPP, demand control, backup |
| S-187 | ESS News — Sungrow integrated C&I battery | <https://www.ess-news.com/2025/04/15/sungrow-launches-fully-integrated-ci-battery/> | News | 15/04/2025 | Snippet tìm kiếm | Med | 02, 03, nB | Modbus TCP cho EMS bên thứ ba; 25/10 tủ |
| S-188 | VP Solar — Sungrow PowerStack | <https://www.vpsolar.com/en/sungrow-powerstack-bess-solutions-for-ci-solar-installations/> | Distributor page | UNKNOWN | Snippet tìm kiếm | Med | 02, nB | Như trên |
| S-189 | Vico Export — PowerStack | <https://www.vicoexport.com/en/powerstack> | Distributor page | UNKNOWN | Snippet tìm kiếm | Med | nA, nB | EMS300CP + iSolarCloud; < 20 ms (chỉ nhà phân phối) |
| S-190 | Renewable Watch — Sungrow PowerStack | <https://renewablewatch.in/2026/07/10/sungrow-unveils-solar-storage-solution-powerstack/> | News | 10/07/2026 | Snippet tìm kiếm | Med | nA, nB | Diesel sync, VSG, black start (bản On&Off-Grid) |
| S-191 | Sungrow — iSolarCloud datasheet V3 | <https://info-support.sungrowpower.com/application/pdf/2024/04/18/DS_20240417_iSolarCloud_Datasheet_V3_EN.pdf> | Datasheet | 17/04/2024 | Tệp nghiên cứu FS trước | Med–High | 02, nB | Dữ liệu 5 phút; phân quyền phân cấp; Open API keys |
| S-192 | pv magazine USA — Sungrow iSolarCloud new version | <https://pv-magazine-usa.com/press-releases/sungrow-launches-new-version-of-its-management-and-monitoring-system-isolarcloud/> | Vendor press release | 2023 | Tệp nghiên cứu FS trước | Low–Med | 02 | I-V "độ chính xác trên 90%" (tự công bố) |
| S-193 | Eniris — iSolarCloud (NL) | <https://docs.eniris.com/nl/Controller/Devices/Cloud/ISolarCloud> | Third-party docs | UNKNOWN | Tệp nghiên cứu FS trước | Med | 02, nB | Firmware cũ có thể không tôn trọng giới hạn P |
| S-194 | Eniris — iSolarCloud (DA) | <https://docs.eniris.be/da/Controller/Devices/Cloud/ISolarCloud> | Third-party docs | UNKNOWN | Snippet tìm kiếm | Med | 07, nE | Tài liệu API sau login; khuyên user chỉ đọc |
| S-195 | Home Assistant forum — iSolarCloud integration | <https://community.home-assistant.io/t/sungrow-isolarcloud-integration-custom-hacs-sensors-optional-charge-discharge-control/1017858> | Community | UNKNOWN | Snippet tìm kiếm | Low | 07, nB, nE | Cộng đồng điều khiển sạc/xả qua iSolarCloud ("tested on one system") |
| S-196 | Sungrow — ISO/IEC 27019 từ BSI | <https://dl.sungrowpower.com/en/sungrow-achieves-iso-iec-27019-and-multiple-cybersecurity-management-system-certifications-from-bsi> | Vendor press release | UNKNOWN | Tệp nghiên cứu FS trước | Med | 10, nI | Sungrow đạt ISO/IEC 27019 |
| S-197 | SMA — Data Manager M | <https://www.sma-america.com/products/energy-management/data-manager-m-10> | Vendor official | UNKNOWN | Snippet tìm kiếm | Med | 03, 04, nA | ≤ 50 thiết bị; cần công tơ POI |
| S-198 | SMA — SMA Premium manual | <https://manuals.sma.de/SMA-Premium/en-US/17048176011.html> | Manual | UNKNOWN | Snippet tìm kiếm | Med | nA | Peak load shaving qua Energy Maximizer (add-on) |
| S-199 | SMA — ennexOS manual | <https://manuals.sma.de/ennexOS/en-US/14259660939.html> | Manual | UNKNOWN | Snippet tìm kiếm | Med | 07, nE | Tham chiếu cấu hình ennexOS (07) |

### F. Đối thủ — OpenEMS, Stem/AlsoEnergy, GridBeyond, nền tảng giám sát

| S-ID | Tiêu đề / nhà xuất bản | URL | Loại nguồn | Ngày xuất bản | Cách tiếp cận | Độ tin cậy | Dùng trong | Claim chính được hỗ trợ |
|---|---|---|---|---|---|---|---|---|
| S-200 | OpenEMS docs — Edge architecture | <https://openems.github.io/openems.io/openems/latest/edge/architecture.html> | Vendor/OSS official docs | UNKNOWN (latest) | Snippet tìm kiếm | Med–High | 02, 03, 04, 06, 07, 08, 09, nB, nE, nG, nH | Cycle ~1 s, process image, scheduler, controller PeakShaving/Balancing, Power Solver |
| S-201 | OpenEMS docs — core concepts | <https://openems.github.io/openems.io/openems/latest/coreconcepts.html> | OSS official docs | UNKNOWN | Snippet tìm kiếm | Med–High | 06, 07, nE | Edge/Backend/UI; Timestamped/Aggregated/Resend notification |
| S-202 | OpenEMS docs — Edge configuration | <https://openems.github.io/openems.io/openems/latest/edge/configuration.html> | OSS official docs | UNKNOWN | Snippet tìm kiếm | Med–High | 05, nC, nH | ESS: âm = sạc, dương = xả |
| S-203 | OpenEMS docs — scheduler | <https://openems.github.io/openems.io/openems/latest/edge/scheduler.html> | OSS official docs | UNKNOWN | Snippet tìm kiếm | Med | 07, nE, nH | Thứ tự controller trong scheduler |
| S-204 | GitHub — OpenEMS repo | <https://github.com/OpenEMS/openems> | OSS repo | UNKNOWN | Snippet tìm kiếm | Med–High | 02, 03, 04, 06, nB, nG | Có file license EPL-2.0 và AGPL-3.0 (giấy phép từng module UNKNOWN — K R-21) |
| S-205 | GitHub — OpenEMS releases | <https://github.com/OpenEMS/openems/releases> | OSS repo | UNKNOWN | Snippet tìm kiếm | Med | 07, nE | Backend TimescaleDB (beta) |
| S-206 | GitHub — OpenEMS controller ess.balancing | <https://github.com/OpenEMS/openems/tree/develop/io.openems.edge.controller.ess.balancing> | OSS repo | UNKNOWN | Snippet tìm kiếm | High | 02, 03, 04, 08, nB, nG | Cân bằng PCC về `targetGridSetpoint` (mặc định 0 W) |
| S-207 | GitHub — OpenEMS issue #3972 | <https://github.com/OpenEMS/openems/issues/3972> | OSS repo | UNKNOWN | Snippet tìm kiếm | High | nC, nI | Controller ghi giá trị âm vào thanh ghi unsigned |
| S-208 | GitHub — OpenEMS PR #3973 | <https://github.com/OpenEMS/openems/pull/3973> | OSS repo | UNKNOWN | Snippet tìm kiếm | High | 08, nC, nI | Kẹp `SellToGridLimit` về 0 |
| S-209 | Uni Jena GitLab — mirror OpenEMS ToU Tibber | <https://git.rz.uni-jena.de/winner-reloaded/openems/-/tree/a45ce897d760f05fe953750744ff887f6c4947cb/io.openems.edge.timeofusetariff.tibber> | OSS repo (mirror) | UNKNOWN | Snippet tìm kiếm | Med | nB | Module ToU tariff Tibber |
| S-210 | Zenodo — OpenEMS release 2025.11.0 | <https://zenodo.org/records/17481747> | OSS release archive | 11/2025 | Snippet tìm kiếm | Med–High | 02, nB, nG | ToU Tibber chuyển QUARTER_HOURLY |
| S-211 | Zenodo — OpenEMS release 2026.4.0 | <https://zenodo.org/records/19374309> | OSS release archive | 04/2026 | Snippet tìm kiếm | Med–High | 02, nB, nG | GridOptimizedCharge; module OCPP server |
| S-212 | OpenEMS community — ConsumptionActivePower negative? | <https://community.openems.io/t/can-consumptionactivepower-be-negative/321> | Community (trích Javadoc) | UNKNOWN | Snippet tìm kiếm | Med–High | 05, nC, nH | Lưới + = mua, − = bán; Consumption = Grid + Production + Storage |
| S-213 | OpenEMS community — Edge-Backend interface | <https://community.openems.io/t/edge-backend-interface/587/2> | Community | UNKNOWN | Snippet tìm kiếm | Med | nB | JSON-RPC/WebSocket, apikey, edgeRpc |
| S-214 | OpenEMS community — ESS via Modbus TCP | <https://community.openems.io/t/ess-that-can-talk-with-openems-using-modbus-tcp/1029> | Community | UNKNOWN | Snippet tìm kiếm | Med | 02, 03, 04, 08, nB, nG | API Modbus/TCP ghi kênh không phải đường điều khiển ESS; điều khiển qua controller + Power Solver |
| S-215 | evcc docs — OpenEMS Modbus API meter | <https://docs.evcc.io/en/meters/openems-modbus-api> | Third-party docs (OSS) | UNKNOWN | Snippet tìm kiếm | Med | nE | evcc đọc OpenEMS qua Modbus TCP API |
| S-216 | Bayern Innovativ — OpenEMS §14a EnWG | <https://www.bayern-innovativ.de/en/emagazine/detail/open-source-software-is-intended-to-simplify-network-management/> | News | 06/2026 | Snippet tìm kiếm | Med | 02, nB | Reference implementation §14a với Fraunhofer ISE + FENECON |
| S-217 | FENECON — hiệu suất Industrial L/XL 2025 | <https://docs.fenecon.de/pdfs/industrial/2025/en/Wirkungsgrad_FENECON_Industrial_L_und_XL_EN.pdf> | Datasheet | 2025 | Snippet tìm kiếm | Med | nC | Hiệu suất không gồm MBA và tiêu thụ phụ trợ |
| S-218 | Business Wire — Stem launches PowerTrack EMS | <https://www.businesswire.com/news/home/20250902991311/en> | Vendor press release | 09/2025 | Snippet tìm kiếm | Med–High | 02, 03, 09, nB, nH | Portfolio + PPC + SCADA + edge UI + unit controller không phụ thuộc phần cứng |
| S-219 | Stem IR — PowerTrack EMS launch PDF | <https://s27.q4cdn.com/138752898/files/doc_news/Stem-Launches-PowerTrack-EMS-Expanding-Global-Product-Suite-for-Standalone-and-Hybrid-Energy-Storage-Control-2025.pdf> | Vendor press release | 2025 | Snippet tìm kiếm | Med–High | nB | Như trên |
| S-220 | Stem IR — Letter to Shareholders 2025 | <https://s27.q4cdn.com/138752898/files/doc_news/Stem-Inc--Letter-to-Shareholders--Reflecting-on-our-journey-of-strategic-realignment-2025.pdf> | Vendor investor doc | 2025 | Snippet tìm kiếm | Low (số tự tuyên bố) | 02, nB | −32% giờ kỹ sư; độ tin cậy controller 99,99% (tự tuyên bố) |
| S-221 | Stem — Athena | <https://www.stem.com/?p=25654> | Vendor official | UNKNOWN | Snippet tìm kiếm | Med | 02, 03, nB | Tối ưu hóa đơn, thuật toán dự đoán, EV |
| S-222 | Stem — AlsoEnergy PowerTrack | <https://www.stem.com/?p=29316> | Vendor official | UNKNOWN | Tệp nghiên cứu FS trước | Med–High | 02, nB | 8.000+ driver, Modbus TCP/RTU |
| S-223 | Stem — Solutions Overview Athena 2021 | <https://www.stem.com/wp-content/uploads/2021/05/Stem-Solutions-Overview_Athena_May-2021_v10.pdf> | Vendor brochure | 05/2021 | Snippet tìm kiếm | Low | 08, nA, nG | Tiết kiệm "lên tới 30%" (vendor claim, không dùng làm KPI) |
| S-224 | AlsoEnergy — PowerTrack flier | <https://home.alsoenergy.com/resources/flier-alsoenergy-powertrack> | Vendor brochure | UNKNOWN | Tệp nghiên cứu FS trước | Med–High | 02, 03, nB | 8.000+ driver và point map; fault detection |
| S-225 | Business Wire — GridBeyond ViewPoint Lens | <https://secure.businesswire.com/news/home/20250930978130/en/GridBeyond-Launches-ViewPoint-Lens-to-Empower-Energy-Customers-With-Greater-Visibility-and-Control> | Vendor press release | 30/09/2025 | Snippet tìm kiếm | Med | 02, 03, 09, nB, nG, nH | Tối ưu tôn trọng ràng buộc tài sản và mô hình suy hao; hồ sơ tải, DR |
| S-226 | Solar Impulse — GridBeyond profile | <https://solarimpulse.com/companies/gridbeyond> | Vendor-supplied profile | UNKNOWN | Snippet tìm kiếm | Med | 02, 03, nB | 400+ site C&I; "AI" dự báo/tối ưu (tự tuyên bố) |
| S-227 | Solar Impulse — GridBeyond solution PDF | <https://solarimpulse.com/companies_file/gridbeyond.com-1.pdf> | Vendor-supplied profile | UNKNOWN | Snippet tìm kiếm | Med | nB | Như trên |
| S-228 | Power Factors — integrated APM platform | <https://powerfactors.com/why-you-need-an-integrated-apm-platform/> | Vendor blog | UNKNOWN | Snippet tìm kiếm | Med | 03, 04, nA | Unity: APM + CMMS (tham chiếu O&M/work order) |
| S-229 | Power Factors — Unity (APM + CMMS + SCADA/PPC/EMS) | <https://powerfactors.com/?p=5335> | Vendor official | UNKNOWN | Tệp nghiên cứu FS trước | Med | 02 | Như trên |
| S-230 | Verdantix Atlas — Power Factors | <https://atlas.verdantix.com/vendors/power-factors> | Analyst | UNKNOWN | Snippet tìm kiếm | Med | nA | Gộp Drive, Greenbyte |
| S-231 | AMMP — compare Growatt | <https://ammp.io/compare/growatt> | Vendor official (so sánh) | UNKNOWN | Tệp nghiên cứu FS trước | Med | 02 | AMMP: > 30 hãng, cảnh báo, PPA, ticket |
| S-232 | Solytic — VCOM vs Solytic | <https://solytic.com/vcom-by-meteocontrol-vs-solytic/> | Vendor marketing | UNKNOWN | Tệp nghiên cứu FS trước | Low–Med | 02, 03 | Giá €100/năm + €0,20/kWp; so sánh bức xạ vệ tinh |
| S-233 | BayWa r.e. — Solar-Log Base datasheet | <https://solar-distribution.baywa-re.de/out/media/1-SL_Base_SolarLog_Datasheet_Solar-Log_Base_EN.pdf> | Datasheet (mirror nhà phân phối) | UNKNOWN | Tệp nghiên cứu FS trước | Med | 02 | Feed-in reduction, điều khiển P/Q từ xa |
| S-234 | evcc docs — Huawei SCharger 7KS | <https://docs.evcc.io/en/chargers/huawei-scharger-7ks-s0.md> | Third-party docs (OSS) | UNKNOWN | Tệp nghiên cứu FS trước | Med | 02 | SCharger điều khiển được qua OCPP (chỉ dimming) |

### G. Giao thức và tích hợp thiết bị

| S-ID | Tiêu đề / nhà xuất bản | URL | Loại nguồn | Ngày xuất bản | Cách tiếp cận | Độ tin cậy | Dùng trong | Claim chính được hỗ trợ |
|---|---|---|---|---|---|---|---|---|
| S-235 | Elipse — Modbus driver max block size | <https://docs.elipse.com.br/documents/en-us/driver/modbus/latest/modbus_appendix_max_limit_block_size.html> | Third-party docs | UNKNOWN | Snippet tìm kiếm | High | 07, nE | FC03/04 ≤ 125 thanh ghi; FC16 ≤ 123 |
| S-236 | Schneider FAQ FA252887 — Modbus limits | <https://www.se.com/be/en/faqs/FA252887/> | Vendor FAQ | UNKNOWN | Snippet tìm kiếm | High | 07, nE | Như trên |
| S-237 | Chipkin — Modbus data types & byte order | <https://docs.chipkin.com/articles/modbus-data-types-byte-order-reference/> | Third-party technical blog | UNKNOWN | Snippet tìm kiếm | Med | 03, 04, 07, nE | Word order 32 bit không chuẩn hóa; CDAB phổ biến |
| S-238 | Industrial Monitor Direct — 32-bit mapping/endianness | <https://industrialmonitordirect.com/blogs/knowledgebase/modbus-32-bit-data-register-mapping-and-endianness-guide> | Third-party technical blog | UNKNOWN | Snippet tìm kiếm | Med | 07, nE | Như trên |
| S-239 | Industrial Monitor Direct — RTU 3,5 character timeout | <https://industrialmonitordirect.com/blogs/knowledgebase/modbus-rtu-character-time-calculating-the-35-character-timeout> | Third-party technical blog | UNKNOWN | Snippet tìm kiếm | Med | 07, nE | 3,5 ký tự ≈ 4,01 ms ở 9600 baud |
| S-240 | mikrocontroller.net — Modbus RTU protocol PDF | <https://www.mikrocontroller.net/attachment/216048/Modbus_RTU_PROTOCOL.pdf> | Community (tài liệu giao thức tải lên) | UNKNOWN | Snippet tìm kiếm | Med | 07, nE | Khoảng lặng ≥ 3,5 ký tự |
| S-241 | Industrial Monitor Direct — SunSpec Modbus with inverters | <https://industrialmonitordirect.com/blogs/knowledgebase/sunspec-modbus-communication-with-solar-inverters> | Third-party technical blog | UNKNOWN | Snippet tìm kiếm | Low–Med | nE | Scale factor: 1234 với SF = −2 → 12,34 |
| S-242 | SunSpec — 700 series approved | <https://sunspec.org/sunspec-modbus-700-series-der-information-models-are-now-approved/> | Standard body (alliance) | ~2021 | Tệp nghiên cứu FS trước | High | 03, 04, 07, nE | Model 701–712 APPROVED, thay dòng 100 |
| S-243 | SMA — SunSpec Modbus TI v11 | <https://files.sma.de/downloads/SunSpecModbus-TI-en-11.pdf> | Manual (TI) | UNKNOWN | Snippet tìm kiếm | Med–High | 07, nE | Danh sách 701–714; SMA profile 2.0 bỏ 124/126 |
| S-244 | SunSpec — Energy Storage Models Draft 4 rev0-1 | <https://sunspec.org/wp-content/uploads/2025/01/SunSpec-Alliance-Specification-Energy-Storage-ModelsD4rev0-1.pdf> | Standard body (draft) | 01/2025 (theo URL) | Snippet tìm kiếm | Med | 07, nE | 802 base, 803 bank, 804 string; trạng thái TEST, không APPROVED |
| S-245 | SunSpec — Energy Storage Models Draft 4 rev0 | <https://sunspec.org/wp-content/uploads/2019/08/SunSpec-Alliance-Specification-Energy-Storage-ModelsD4rev0.pdf> | Standard body (draft) | 08/2019 (theo URL) | Snippet tìm kiếm | Med | nC | Model 802 = Battery Base Model (draft) |
| S-246 | SlideServe — SunSpec storage program slide (2014) | <https://www.slideserve.com/chaim/sunspec-alliance-overview-storage-standards-development-program> | Community (slide tải lên) | 2014 | Snippet tìm kiếm | Low | 07, nE | Đánh số model cũ khác (801 base) — mâu thuẫn phiên bản |
| S-247 | SunSpec — Modbus open source webinar deck | <https://sunspec.org/wp-content/uploads/2009/03/SunSpec-Modbus-Open-Source-Webinar-Deck-Template.pdf> | Standard body (slide) | UNKNOWN | Snippet tìm kiếm | Med | nE | Giá trị sentinel 0xFFFF |
| S-248 | SolarNetwork wiki — SunSpec model discovery | <https://github.com/SolarNetwork/solarnetwork/wiki/SunSpec-model-discovery> | Community (OSS wiki) | UNKNOWN | Snippet tìm kiếm | Med | 07, nE | Base 40000/50000/0, chuỗi "SunS" |
| S-249 | SunSpec — product certification registry | <https://sunspec.org/product-certification-registry> | Standard body | UNKNOWN | Snippet tìm kiếm | Med | 07, nE | Nơi kiểm chứng chứng nhận SunSpec của thiết bị |
| S-250 | SunSpec — interface defects in UL 1741 SB inverters | <https://sunspec.org/communication-interface-defects-revealed-inul-1741-sb-certified-inverters/> | Standard body (alliance) | 12/2023 | Snippet tìm kiếm | Med–High | 03, 04, 07, 10, nE, nI | Thiết bị có UL 1741 SB vẫn lỗi giao diện SunSpec |
| S-251 | SunSpec — 1547 initiative | <https://sunspec.org/sunspec-1547-initiative/> | Standard body (alliance) | UNKNOWN | Tệp nghiên cứu FS trước | High | 10, nI | IEEE 1547-2018: giao diện DER ≥ 1 trong 2030.5/DNP3/SunSpec |
| S-252 | NRECA — IEEE 1547-2018 (Vartanian) slide | <https://www.cooperative.com/programs-services/bts/Documents/Emerging%20Priorities%20for%20Energy%20Research%20Day%20-%20Oct%202018/IEEE%201547-2018%20-%20Vartanian%20(NRECA-APA-ResearchDay-20181031).pdf> | Industry association slide | 31/10/2018 | Snippet tìm kiếm | Med | 07, nE | Như trên |
| S-253 | Akkudoktor forum — Seplos CAN spec PDF | <https://akkudoktor.net/uploads/short-url/dwFYBPwjnfia9tSuhUopj9uGX2u.pdf> | Community (tài liệu tải lên) | UNKNOWN | Snippet tìm kiếm | Med | 03, 07, nE | CAN BMS 500 kbps, chu kỳ 1 s, ID 0x351… |
| S-254 | Akkudoktor forum — Pylontech BMS với SMA Sunny Island | <https://akkudoktor.net/t/pylontech-bms-mit-sma-sunny-island/18019> | Community | UNKNOWN | Snippet tìm kiếm | Low–Med | 07, nE | Tài liệu gốc bị gỡ; ID khác nhau giữa hãng |
| S-255 | Victron community — DIY BMS via CAN | <https://community.victronenergy.com/t/connect-diy-bms-via-can-to-cerbo-gx-eigenes-bms-via-can-mit-cerbo-gx-verbinden/37102> | Community | UNKNOWN | Snippet tìm kiếm | Low–Med | 07, nE | Thiếu 0x355 → timeout |
| S-256 | Victron community archive — DCL/CCL limits | <https://communityarchive.victronenergy.com/questions/310041/maximum-limit-of-dcl-and-ccl-numbers.html> | Community | UNKNOWN | Snippet tìm kiếm | Low–Med | nC, nH | DCL 16 bit, 0,1 A, tối đa ~3.276,7 A |
| S-257 | GitHub — BydCanProtocol | <https://github.com/dfch/BydCanProtocol> | Community (OSS reverse engineering) | UNKNOWN | Snippet tìm kiếm | Low | 07, nE | Giao thức CAN BYD (không chính thức) |
| S-258 | Orion BMS — current limit status | <https://www.orionbms.com/manuals/utility/bms_param_current_limit_status.html> | Manual | UNKNOWN | Snippet tìm kiếm | High | 03, 04, 05, nC | BMS hạ CCL/DCL theo SOC, nhiệt độ, điện áp cell; CCL có thể = 0 |
| S-259 | USPTO — patent US 11411391 (ESS) | <https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11411391> | Patent | UNKNOWN | Snippet tìm kiếm | Med (một thiết kế) | 03, 04, 06, 07, 10, nE | BMS → PCS bảo vệ qua dây cứng; EMS qua TCP/RS485/CAN |
| S-260 | EMQX — MQTT Message Expiry Interval | <https://www.emqx.com/en/blog/mqtt-message-expiry-interval> | Vendor technical blog | UNKNOWN | Snippet tìm kiếm | High | 03, 04, 06, 07, nE | MQTT 5 broker bỏ tin quá hạn |
| S-261 | Solace — MQTT 5 new features | <https://docs.solace.com/API/MQTT-v50-Prtl-Conformance-Spec/mqtt-v50-C-summary-new-features.htm> | Vendor docs | UNKNOWN | Snippet tìm kiếm | High | 06, 07, nE | Message/Session Expiry |
| S-262 | EMQX — Sparkplug 3.0 | <https://www.emqx.com/en/blog/sparkplug-3-0-advancements-and-formalization-in-mqtt-for-iiot> | Vendor technical blog | UNKNOWN | Snippet tìm kiếm | Med | 07, nE | QoS0 dữ liệu, QoS1 trạng thái; STATE JSON v3.0 |
| S-263 | Chariot docs — Sparkplug (short link) | <https://docs.chariot.io/x/S4SzBw> | Vendor docs | UNKNOWN | Snippet tìm kiếm | Med | 07, nE | Như trên |
| S-264 | HMS — Crimson Sparkplug B compliance | <https://support.hms-networks.com/hc/en-us/articles/36458732970386-Is-the-the-Crimson-Sparkplug-B-implementation-compliant-with-the-spec> | Vendor FAQ | UNKNOWN | Snippet tìm kiếm | Med | 07, nE | Will QoS cố định 0 → NDEATH có thể mất |
| S-265 | OPC Foundation — Energy Initiative | <https://opcfoundation.org/wp-content/uploads/2026/03/OPCF-Energy-Initiative.pdf> | Standard body | 03/2026 | Snippet tìm kiếm | Med | 07, nE | OPC 10040 (IEC 61850) RC; không có spec PV/BESS riêng |
| S-266 | Software Toolbox — What is IEC 61850 | <https://softwaretoolbox.com/resources/what-is-iec61850> | Vendor technical blog | UNKNOWN | Snippet tìm kiếm | Med | 07, nE | GOOSE < 3–4 ms lớp 2 |
| S-267 | SCC Canada — IEC 61850-7-420:2021 entry | <https://scc-ccn.ca/standardsdb/standards/2048725> | Standard body (danh mục) | 2021 | Snippet tìm kiếm | Med | 07, nE | 7-420:2021 gồm lưu trữ |
| S-268 | Beckhoff Infosys — IEC 60870-5-10x | <https://infosys.beckhoff.com/content/1031/tf6500_tc3_iec60870_5_10x/984040459.html> | Vendor docs | UNKNOWN | Snippet tìm kiếm | High | 03, 04, 07, nE | Port 2404; k/w/t1–t3; type 13/36/50 |
| S-269 | Elseta wiki — IEC 104 | <https://wiki.elseta.com/books/the-vinci-software/page/iec-60870-5-104> | Vendor docs | UNKNOWN | Snippet tìm kiếm | High | 07, nE | Như trên |
| S-270 | Mervis KB — IEC 104 server | <https://kb.mervis.info/doku.php/en:mervis-ide:35-help:023-server-communication-protocols:010-iec-60870-5-104-server> | Vendor docs | UNKNOWN | Snippet tìm kiếm | High | 07, nE | k=12, w=8, t1=15 s |
| S-271 | DNP Users Group — IEEE 1815.2 | <https://www.dnp.org/ieee-releases-18152-standard-for-der-communications> | Standard body (user group) | UNKNOWN | Snippet tìm kiếm | Med | 07, nE | DNP3 cho DER (1815.2); trạng thái xuất bản mâu thuẫn |
| S-272 | EPRI — DER DNP3 outstation (public download) | <https://restservice.epri.com/publicdownload/000000003002015355/0/Product> | Research institute | UNKNOWN | Snippet tìm kiếm | Med | 07, nE | Ánh xạ 7-420 sang DNP3 |
| S-273 | OCA — OCPP 2.1 available | <https://openchargealliance.org/ocpp-2-1-is-now-available/> | Standard body | 23/01/2025 | Snippet tìm kiếm | High | 03, 04, 07, nE | V2X, DER control, ISO 15118-20; tương thích logic 2.0.1 |
| S-274 | OCA — OCPP protocol page | <https://openchargealliance.org/protocols/open-charge-point-protocol> | Standard body | UNKNOWN | Snippet tìm kiếm | High | 07, nE | Như trên |
| S-275 | OCA — OCPP security whitepaper | <https://openchargealliance.org/?p=159286> | Standard body | UNKNOWN | Snippet tìm kiếm | Med–High | 03, 04, 07, 10, nE, nI | Security profile 1/2/3 (3 = TLS + client cert); Ed.3/Ed.4 |
| S-276 | Bender — OCPP smart charging | <https://www.bender.de/docs/charge-controller/OCPP/ocpp-smart-charging/> | Vendor docs | UNKNOWN | Snippet tìm kiếm | High | 03, 04, 07, 08, 10, nE, nG, nI | OCPP 1.6: 3 loại profile, stackLevel; TxDefaultProfile khi mất kết nối |
| S-277 | Easee — OCPP smart charging | <https://developer.easee.com/docs/ocpp-smart-charging> | Vendor docs | UNKNOWN | Snippet tìm kiếm | High | 03, 04, 07, 08, 10, nE, nG, nI | TxDefault 0 A đè TxProfile 20 A (quirk theo hãng) |
| S-278 | Codibly — 8 features OCPP 2.1 | <https://codibly.com/news-insights/8-features-ocpp-2_1> | Vendor blog | UNKNOWN | Snippet tìm kiếm | Low–Med | 07, nE | Tóm tắt OCPP 2.1; "80% qua gateway" chưa xác minh |
| S-279 | Midapower — OCPP 1.6J vs 2.0.1 | <https://www.midapower.com/news/strategic-comparison-of-ocpp-1-6j-vs-2-0-1-for-commercial-charging-operators/> | Vendor blog | UNKNOWN | Snippet tìm kiếm | Low–Med | 07, nE | So sánh 1.6J/2.0.1 cho CPO thương mại |
| S-280 | OpenADR Alliance — webinar 2.0 → 3.0 | <https://www.openadr.org/assets/OpenADR%20Webinar%20Nov%202023%20-%20From%202.0%20to%203.0.pdf> | Standard body (alliance) | 11/2023 | Snippet tìm kiếm | Med–High | 03, 07, 08, nE, nG | 3.0 REST/JSON; 3.1 thêm MQTT; 3.0 không thay 2.0b |
| S-281 | OpenADR Alliance — annual report 2025 | <https://www.openadr.org/assets/OpenADR%20AR25.pdf> | Standard body (alliance) | 2025 | Snippet tìm kiếm | Med | 07, nE | Tiến độ 3.x |
| S-282 | eCommerceNews — OpenADR 3.0 certification | <https://ecommercenews.co.nz/story/openadr-3-0-certification-marks-milestone-in-energy-sector> | News | 03/2025 | Snippet tìm kiếm | Med | 07, nE | Chứng nhận 3.0 bắt đầu 3/2025 |
| S-283 | IEEE SA — smart energy slides (2030.5) | <https://standards.ieee.org/content/dam/ieee-standards/standards/web/documents/presentations/smart_energy_slides.pdf> | Standard body (slide) | UNKNOWN | Snippet tìm kiếm | Med | 07, 10, nE | 2030.5 mặc định Rule 21; TLS 1.2 + chứng chỉ |
| S-284 | QualityLogic — DER workshop datasheet | <https://www.qualitylogic.com/wp-content/uploads/2021/07/Data-Sheet-DER-Workshop.pdf> | Vendor (test lab) | 07/2021 | Snippet tìm kiếm | Med | 07, nE | Chứng nhận 2030.5 bắt buộc 2020 (CA) |
| S-285 | Trialog — bài về giao thức năng lượng/EV | <https://www.trialog.com/?p=11328> | Vendor blog | UNKNOWN | Snippet tìm kiếm | Low–Med | 07, nE | Tham chiếu tích hợp (07) |
| S-286 | SMA Developer — APIs | <https://developer.sma.de/sma-apis> | Vendor official (developer portal) | UNKNOWN | Snippet tìm kiếm | Med–High | 03, 07, nE | Monitoring/GridControl/GeoForecast API; Live API không cho giám sát liên tục |
| S-287 | SMA Developer — sandbox APIs | <https://developer.sma.de/sma-sandbox-apis> | Vendor official | UNKNOWN | Snippet tìm kiếm | Med–High | 07, nE | Sandbox |
| S-288 | Solytic — set up SMA Monitoring API | <https://solytic.com/knowledge/set-up-api-access-sma-monitoring-api/> | Third-party docs | UNKNOWN | Tệp nghiên cứu FS trước | Med | 07, nE | Quy trình cấp API SMA |
| S-289 | Solis US support — API troubleshooting | <https://usservice.solisinverters.com/support/solutions/articles/73000661192-solis-api-troubleshooting> | Vendor KB | UNKNOWN | Snippet tìm kiếm | Med | 07, nE | Ký HMAC-SHA1 |
| S-290 | Ben Tasker — telegraf plugin issue (Solis) | <https://projects.bentasker.co.uk/gils_projects/issue/utilities/telegraf-plugins/9.html> | Community | 2023 | Snippet tìm kiếm | Low | 07, nE | Rate limit ~3 lần/5 s/IP |
| S-291 | GitHub — soliscloud_api | <https://github.com/hultenvp/soliscloud_api> | Community (OSS) | UNKNOWN | Snippet tìm kiếm | Low–Med | 03, 07, nE | Client SolisCloud; tên endpoint không thống nhất |
| S-292 | Home Assistant — Growatt server integration | <https://www.home-assistant.io/components/growatt_server/> | Third-party docs (OSS) | UNKNOWN | Snippet tìm kiếm | Low–Med | 03, 07, nE | Growatt V1 token, host theo vùng |
| S-293 | CPAN — DeyeCloud-Client README | <https://mirrors.edge.kernel.org/CPAN/modules/by-module/Config/KORNIX/DeyeCloud-Client-0.0.2.readme> | Community (OSS) | UNKNOWN | Snippet tìm kiếm | Low–Med | 07, nE | appId/appSecret; base URL eu1-developer; chỉ endpoint đọc pin |
| S-294 | Home Assistant forum — Deye Cloud integration | <https://community.home-assistant.io/t/deye-cloud-integration/813153> | Community | UNKNOWN | Snippet tìm kiếm | Low | 07, nE | DeyeCloud có thể chạy qua server Solarman |
| S-295 | Deye — thông báo di chuyển dữ liệu Deye Cloud | <https://deye.com/vi/deye-cloud-data-migration-announcement/> | Vendor official | UNKNOWN | Tệp nghiên cứu FS trước | Low (403, chưa đọc nội dung) | nI | Chỉ xác nhận trang tồn tại; không suy diễn |
| S-296 | GitHub — huawei_solar (wlcrs) | <https://github.com/wlcrs/huawei_solar> | Community (OSS, AGPL-3.0) | UNKNOWN | Tệp nghiên cứu FS trước | Med–High | 07, nE | Huawei chỉ một client Modbus; port 6607/502; dongle ≥ 5 s |
| S-297 | GitHub — huawei_solar services.yaml | <https://github.com/wlcrs/huawei_solar/blob/main/services.yaml> | Community (OSS) | UNKNOWN | Tệp nghiên cứu FS trước | Med–High | 03, 04, 08, nG | set_tou_periods, set_capacity_control_periods, set_maximum_feed_grid_power, forcible_charge/discharge |
| S-298 | GitHub — huawei_solar const.py | <https://github.com/wlcrs/huawei_solar/blob/main/const.py#L20-L44> | Community (OSS) | UNKNOWN | Tệp nghiên cứu FS trước | Med | nG | Hằng số dịch vụ ghi |
| S-299 | GitHub — evcc discussion #1928 (Huawei) | <https://github.com/evcc-io/evcc/discussions/1928> | Community | UNKNOWN | Tệp nghiên cứu FS trước | Med | 07, nE | "only support one connection at a time" |
| S-300 | ioBroker forum — EMMA Modbus | <https://forum.iobroker.net/post/1270320> | Community | UNKNOWN | Snippet tìm kiếm | Low | 07, nE | EMMA port 502, không chỉnh ID; installer bật Modbus TCP |
| S-301 | raspberry.tips — SUN2000/EMMA dashboard | <https://raspberry.tips/raspberrypi-tutorials/huawei-sun2000-home-assistant-emma-solar-dashboard> | Community blog | UNKNOWN | Snippet tìm kiếm | Low | 07, nE | Như trên |
| S-302 | Homey community — Huawei FusionSolar Manager | <https://community.homey.app/t/app-pro-huawei-fusionsolar-manager/153353?page=16> | Community | UNKNOWN | Snippet tìm kiếm | Low | 07, nE | Thanh ghi pin 47086=6 "Third-party Scheduling", 47100/47083/47102/47104 (cấm dùng làm driver VERIFIED) |
| S-303 | openHAB community — SveaSolar/Huawei | <https://community.openhab.org/t/sveasolar-powershifter-pv-inverter-huawei/164046> | Community | UNKNOWN | Snippet tìm kiếm | Low | 07, nE | Có người không đổi được công suất qua thanh ghi |
| S-304 | openHAB community — SUN2000 Modbus | <https://community.openhab.org/t/reading-data-from-huawei-inverter-sun-2000-3ktl-10ktl-via-modbus-tcp-and-rtu/87670?page=5> | Community | UNKNOWN | Snippet tìm kiếm | Low–Med | 07, nE | Thời gian 40000 (U32, giờ địa phương), múi giờ 43006 |
| S-305 | Homey community — Sungrow Logger1000 | <https://community.homey.app/t/modbus-register-logger-1000-sungrow/126405> | Community | UNKNOWN | Snippet tìm kiếm | Low | 07, nE | Unit ID mặc định 247 |
| S-306 | Loxforum — Sungrow SH10RT Modbus | <https://www.loxforum.com/forum/german/software-konfiguration-programm-und-visualisierung/424167-sungrow-sh10rt-wr-modbusparameter> | Community | UNKNOWN | Snippet tìm kiếm | Low | 07, nE | 13049 EMS mode; 13050/13051 mâu thuẫn |
| S-307 | ioBroker forum — Sungrow hybrid | <https://forum.iobroker.net/post/936007> | Community | UNKNOWN | Snippet tìm kiếm | Low | 07, nE | Như trên |
| S-308 | Clean Energy Reviews forum — Logger1000 as Modbus TCP server | <https://forum.cleanenergyreviews.info/t/logger1000-as-modbus-tcp-server/3181> | Community | UNKNOWN | Snippet tìm kiếm | Low | 07, nE | Sungrow không công bố tham số đọc/ghi logger |
| S-309 | Victron community — Sungrow and SunSpec | <https://community.victronenergy.com/t/sungrow-inverters-and-sunspec/57195> | Community | UNKNOWN | Snippet tìm kiếm | Low–Med | 07, nE | Sungrow dùng map riêng từ 5000 |
| S-310 | Victron community archive — MultiPlus-II ESS Mode 2/3 | <https://communityarchive.victronenergy.com/questions/95889/multipluss-ii-is-external-control-ess-mode-2-or-3%EF%B9%96childToView=102991.html> | Community | UNKNOWN | Snippet tìm kiếm | Low–Med (URL chứa ký tự "﹖" mã hóa, xem §4) | 03, 07, 08, nE, nG | `/AcPowerSetpoint` reg 2700 int16; fallback khi mất master chưa rõ |
| S-311 | mcpservers.org — victron-tcp | <https://mcpservers.org/en/servers/lubosstrejcek/victron-tcp> | Community (OSS directory) | UNKNOWN | Snippet tìm kiếm | Low | 07, nE | Victron GX Modbus/MQTT ports |
| S-312 | Autarco help — still exporting with zero export | <https://help.autarco.com/en/hardware/why-am-i-still-exporting-while-i-have-set-my-pv-system-to-zero-export-> | Vendor help center | UNKNOWN | Snippet tìm kiếm | Med | 07, 08, nE, nG | Độ trễ zero-export = chu kỳ đo + truyền + phản ứng inverter + giảm công suất |
| S-313 | meteocontrol — blue'Log XC Modbus Power Control datasheet | <https://www.meteocontrol.com/fileadmin/Daten/Dokumente/EN/Produkte/On_Site/blue_Log_XM_XC/Data_sheet/blue_Log_XM_XC_Modbus_Power_Control_license_blue_Log_XC_data_sheet_LastMod-2026-01-27_en.pdf> | Datasheet | 27/01/2026 | Snippet tìm kiếm | Med–High | 03, 04, 07, nE | Slave ID 1, port 502; 104/61850/DNP3 qua PLC chuyển đổi |
| S-314 | Solar-Log — Modbus TCP PM datasheet | <https://www.solar-log.com/fileadmin/user_upload/documents/Datenblaetter/en_GB/Komponenten/Kommunikation/SolarLog_Datasheet_Modbus_TCP_PM_EN.pdf> | Datasheet | UNKNOWN | Snippet tìm kiếm | Med–High | 07, nE | License; port 502; ID 1; FC 04/06/16; nhận lệnh P/Q |
| S-315 | Timebeat — PTP vs NTP | <https://timebeat.app/blog/ptp-vs-ntp> | Vendor technical blog | UNKNOWN | Snippet tìm kiếm | Med | 03, 07, nE | NTP 1–100 ms; PTP µs cần HW timestamping |
| S-316 | Sunplus wiki (short link) — PTP | <https://sunplus.atlassian.net/wiki/x/JQB1eQ> | Vendor wiki | UNKNOWN | Snippet tìm kiếm | Low–Med | 07, nE | PTP phần mềm ~100 µs |

### H. Miền năng lượng: dấu, đo đếm, pin, KPI

| S-ID | Tiêu đề / nhà xuất bản | URL | Loại nguồn | Ngày xuất bản | Cách tiếp cận | Độ tin cậy | Dùng trong | Claim chính được hỗ trợ |
|---|---|---|---|---|---|---|---|---|
| S-317 | OpenEnergyMonitor forum — sign convention import/export | <https://community.openenergymonitor.org/t/is-there-a-standard-for-import-export-positive-negative-power-flow/15149> | Community | UNKNOWN | Snippet tìm kiếm | Med | 03, 05, 09, nC, nH | Không có chuẩn cộng đồng thống nhất về dấu |
| S-318 | Wiener Netze — smart meter glossary | <https://www.wienernetze.at/o/document/ex129_sm_glossar_eng_v04_bf> | Regulator/DSO | UNKNOWN | Snippet tìm kiếm | High | 05, nC | OBIS 1.8.0 = A+ nhập; 2.8.0 = A− xuất |
| S-319 | Lobaro — OBIS code configuration | <https://manuals.lobaro.com/configuration/obis-code-configuration> | Vendor docs | UNKNOWN | Snippet tìm kiếm | High | 05, nC | Như trên |
| S-320 | Schneider FAQ FA239195 — ION rollover | <https://www.se.com/us/en/faqs/FA239195/> | Vendor FAQ | UNKNOWN | Snippet tìm kiếm | High | 03, 04, 05, nC, nF | Rollover ION mặc định 10.000.000 kèm bộ đếm tràn |
| S-321 | EnergyCAP — types of readings | <https://helpcenter.energycap.com/um/sa/types_of_readings> | Vendor help center | UNKNOWN | Snippet tìm kiếm | High | 05, nC, nF | Coi là tràn chỉ khi giảm > 10% giá trị cực đại |
| S-322 | PNNL-27237 — BESS performance report | <https://www.pnnl.gov/main/publications/external/technical_reports/PNNL-27237.pdf> | Academic/national lab | UNKNOWN | Snippet tìm kiếm | Med–High | 03, 05, nC | Loại aux làm RTE đo được tăng ~6–16% |
| S-323 | Sandia/PNNL — MESA-1 final test report | <https://www.sandia.gov/ess-ssl/wp-content/uploads/2019/07/PNNL-MESA-1-Final-Test-Report_Reduced.pdf> | Academic/national lab | 07/2019 (theo URL) | Snippet tìm kiếm | Med | 09, nC, nH | Aux ~30 kW trên hệ 1.000 kWh; RTE thấp nhất mùa hè |
| S-324 | RAE (Hy Lạp) — BESS installation safety & performance specs | <https://www.rae.gr/wp-content/uploads/2023/06/H1_BESS-Installation-Safety-and-Performance-Specifications.pdf> | Regulator | 06/2023 | Snippet tìm kiếm | Med | nC | RTE gồm HVAC, BMS, tổn hao MBA/PCS, đo tại điểm đấu nối |
| S-325 | Open Exam Prep — PE study guide BESS | <https://open-exam-prep.com/study-guides/pe-electrical-power/electric-power-devices-renewables/battery-storage-bess-ultracapacitors> | Educational (thứ cấp) | UNKNOWN | Snippet tìm kiếm | Low | nC | RTE AC-AC là tích hiệu suất; aux 2–4% (không dùng làm số liệu) |
| S-326 | Iowa State senior design sddec24-18 — one-line | <https://sddec24-18.sd.ece.iastate.edu/One-line.pdf> | Academic (đồ án sinh viên) | 2024 | Snippet tìm kiếm | Low | nC | Aux đỉnh 38 kVA/container (BYD) |
| S-327 | ACCURE — LFP SOC errors can exceed 15% | <https://www.accure.net/blogs/state-of-charge-soc-estimation-errors-for-lfp-batteries-can-exceed-15> | Vendor blog (có lợi ích) | UNKNOWN | Snippet tìm kiếm | Med | 03, 04, 05, nC, nG | OCV phẳng; coulomb counting trôi; lỗi SOC có thể > 15% |
| S-328 | Clarke Energy — LFP SOC challenge | <https://www.clarke-energy.com/2026/lithium-iron-phosphate-bess-the-state-of-charge-challenge/> | Vendor blog | 2026 | Snippet tìm kiếm | Med | nC | Như trên |
| S-329 | pv magazine USA — significance of SOC | <https://pv-magazine-usa.com/2024/09/25/the-significance-of-state-of-charge-in-energy-storage/> | News | 25/09/2024 | Snippet tìm kiếm | Med | nC | Như trên |
| S-330 | Deye — BMS vs EMS vs PCS | <https://deye.com/nl/blog/bms-vs-ems-vs-pcs-bess-components/> | Vendor blog | UNKNOWN | Snippet tìm kiếm | Med–High | 03, 04, 05, 06, 08, nC | BMS bảo vệ; PCS thực thi; EMS điều độ; giới hạn BMS phải được PCS và EMS tôn trọng (nguồn thứ hai cho K R-18) |
| S-331 | Power-Sonic — LFP cell datasheet | <https://cdn.power-sonic.com/documents/PSL-FP-IFP30135185EC_Data_Sheet.pdf> | Datasheet | UNKNOWN | Snippet tìm kiếm | High (cho cell đó) | nC | Cắt sạc 3,65 V; cắt xả 2,5 V; sạc 0–55 °C |
| S-332 | Sunlith Energy — battery degradation | <https://sunlithenergy.com/?p=6409> | Vendor blog | UNKNOWN | Snippet tìm kiếm | Med | nC | Lão hóa = lịch + chu kỳ (mô hình cộng) |
| S-333 | Okra Solar — battery lifetime | <https://www.okrasolar.com/blog/a-better-way-to-estimate-battery-lifetime> | Vendor blog | UNKNOWN | Snippet tìm kiếm | Med | nC | LFP chu kỳ phụ thuộc mạnh nhiệt độ |
| S-334 | RSC J. Mater. Chem. A — LFP aging 2025 | <https://pubs.rsc.org/en/content/articlehtml/2025/ta/d5ta03813h> | Academic (peer-reviewed) | 2025 | Snippet tìm kiếm | High | nC | LFP ở 55 °C, SOC cao suy giảm nhiều hơn |
| S-335 | arXiv 2605.14043 — AC vs DC coupling | <https://arxiv.org/pdf/2605.14043> | Academic (preprint) | 05/2026 (theo ID) | Snippet tìm kiếm | Med | nC | AC-coupled không cứu năng lượng clip; DC-coupled thì được |
| S-336 | Battery Power Tips — AC vs DC coupled | <https://www.batterypowertips.com/?p=4501> | News (kỹ thuật) | UNKNOWN | Snippet tìm kiếm | Med | nC | Như trên |
| S-337 | Sandia PVPMC — Performance Ratio | <https://pvpmc.sandia.gov/modeling-guide/5-ac-system-output/pv-performance-metrics/performance-ratio/> | Academic/national lab | UNKNOWN | Snippet tìm kiếm | High | 03, 04, 05, nC, nF | PR = Yf/Yr; Yr = H_POA/1 kW/m² |
| S-338 | Solargis KB — PV performance indicators | <https://kb.solargis.com/docs/pv-performance-indicators> | Vendor docs | UNKNOWN | Snippet tìm kiếm | Med–High | nC | PR và biến thể hiệu chỉnh nhiệt độ |
| S-339 | Hukseflux — IEC 61724-1:2021 what is new | <https://www.hukseflux.com/uploads/inline/iec_61724-1_2021_version-what_is_new_v2403_0.pdf> | Vendor (cảm biến) | 03/2024 (theo tên file) | Snippet tìm kiếm | Med | nC | 2021 còn Class A và B (theo Hukseflux; không dùng trong yêu cầu) |
| S-340 | IEC Webstore — IEC TS 63019:2019 | <https://webstore.iec.ch/en/publication/25466> | Standard body | 2019 | Tệp nghiên cứu FS trước | Med | 03, 05, nC | Khung availability PV; 61724-3 là đánh giá điện năng |
| S-341 | BSI Knowledge — IEC 62116 test procedure | <https://knowledge.bsigroup.com/products/test-procedure-of-islanding-prevention-measures-for-utility-interconnected-photovoltaic-inverters> | Standard body | UNKNOWN | Snippet tìm kiếm | Med–High | nC | IEC 62116 là phương pháp thử, không đặt ngưỡng ngắt |
| S-342 | Heaven Green Energy — availability glossary | <https://www.heavengreenenergy.com/glossary/availability-factor> | Vendor glossary | UNKNOWN | Snippet tìm kiếm | Low | nC | Định nghĩa giản lược (không phải chuẩn) |
| S-343 | autarc — self-consumption rate | <https://hilfe.autarc.energy/en/articles/10559274-what-is-the-self-consumption-rate> | Vendor help center | UNKNOWN | Snippet tìm kiếm | Med | 05, nC | Self-consumption dựa trên sản lượng |
| S-344 | nPro — self-sufficiency rate | <https://www.npro.energy/main/en/help/self-sufficiency-rate> | Vendor help center | UNKNOWN | Snippet tìm kiếm | Med | nC | Self-sufficiency dựa trên tiêu thụ (công thức khác nhau giữa nguồn) |
| S-345 | Aurora Solar — What is Autarky | <https://help.aurorasolar.com/hc/en-us/articles/45485868561427-What-is-Autarky> | Vendor help center | UNKNOWN | Snippet tìm kiếm | Med | nC | Autarky = PV cấp (trực tiếp/qua pin)/tiêu thụ |
| S-346 | GitHub — tesla-style-solar-power-card README | <https://github.com/reptilex/tesla-style-solar-power-card/blob/master/README.md> | Community (OSS, Apache-2.0) | 2024 | Tệp nghiên cứu FS trước | High (cho chính thẻ) | 03, 09, nH | Cạnh có hướng không âm; "all sensors need to be positive values" |
| S-347 | GitHub — tesla-style card SensorElement.ts | <https://github.com/reptilex/tesla-style-solar-power-card/blob/master/src/models/SensorElement.ts#L78-L90> | Community (OSS) | 2024 | Tệp nghiên cứu FS trước | High | 09, nH | Như trên |

### I. Dữ liệu, lưu trữ chuỗi thời gian, dự báo

| S-ID | Tiêu đề / nhà xuất bản | URL | Loại nguồn | Ngày xuất bản | Cách tiếp cận | Độ tin cậy | Dùng trong | Claim chính được hỗ trợ |
|---|---|---|---|---|---|---|---|---|
| S-348 | Tiger Data — TimescaleDB editions | <https://www.tigerdata.com/docs/about/latest/timescaledb-editions> | Vendor official | UNKNOWN | Snippet tìm kiếm | High | 03, 04, 05, 06, nF | Compression/CAGG thuộc Community (TSL); tự host miễn phí; cấm bán DBaaS |
| S-349 | Tiger Data — licenses | <https://www.tigerdata.com/legal/licenses> | Vendor official (pháp lý) | UNKNOWN | Snippet tìm kiếm | High | 06, nF | "cannot sell … Community Edition as a service" (cần pháp chế xác nhận — Q-F01) |
| S-350 | Timescale blog — continuous aggregates | <https://blog.timescale.com/continuous-aggregates-faster-queries-with-automatically-maintained-materialized-views/> | Vendor blog | UNKNOWN | Snippet tìm kiếm | High | 05, 06, nF | CAGG làm mới tăng dần |
| S-351 | Timescale docs — hypercore | <https://docs.timescale.com/use-timescale/latest/hypercore/real-time-analytics-in-hypercore> | Vendor official docs | UNKNOWN | Snippet tìm kiếm | High | 06, nF | CAGG là hypertable; columnstore segmentby/orderby |
| S-352 | Crunchy Data — mirror TimescaleDB 2.28.0 docs | <https://access.crunchydata.com/documentation/timescaledb/2.28.0/> | Third-party docs (mirror) | UNKNOWN | Snippet tìm kiếm | Med | 06, nF | "90%+ compression typical" |
| S-353 | OneUptime blog — TimescaleDB CAGG | <https://oneuptime.com/blog/post/2026-01-27-timescaledb-continuous-aggregates/view> | Third-party blog | 27/01/2026 (theo URL) | Snippet tìm kiếm | Low–Med | 06, nF | Nén 10–20× (mâu thuẫn "90%+") |
| S-354 | Tiger Data — time_weight() | <https://www.tigerdata.com/docs/api/latest/hyperfunctions/time-weighted-calculations/time_weight/> | Vendor official docs | UNKNOWN | Snippet tìm kiếm | High | 05, nF | LOCF/linear; rollup(); nội suy biên ngày |
| S-355 | Timescale forum — Toolkit 1.8.0 | <https://www.timescale.com/forum/t/toolkit-1-8-0-now-available/700> | Vendor forum | UNKNOWN | Snippet tìm kiếm | High | nF | Như trên |
| S-356 | Pigsty — timescaledb_toolkit extension | <https://pigsty.io/ext/e/timescaledb_toolkit/> | Third-party docs | UNKNOWN | Snippet tìm kiếm | Med | nF | counter_agg phát hiện reset; delta/rate/num_resets |
| S-357 | Timescale docs — analytics API | <https://docs.timescale.com/api/latest/analytics/> | Vendor official docs | UNKNOWN | Snippet tìm kiếm | Med–High | 05, nF | Như trên |
| S-358 | Timescale blog — SolarNetwork | <https://timescale.com/blog/how-solarnetwork-fuels-energy-conservation-with-timescaledb> | Vendor customer blog | 2024 | Snippet tìm kiếm | Med | 06, nF | ~300 GB; tự tổng hợp; CAGG là kế hoạch |
| S-359 | Timescale — SolarNetwork case study | <https://timescale.com/case-studies/solarnetwork> | Vendor case study | UNKNOWN | Snippet tìm kiếm | Med | 06, nF | Nói đã dùng CAGG (mâu thuẫn blog) |
| S-360 | InfluxData — InfluxDB 3 OSS alpha | <https://influxdata.com/blog/influxdb3-open-source-public-alpha> | Vendor blog | UNKNOWN (alpha) | Snippet tìm kiếm | Med | nF | InfluxDB 3 Core MIT/Apache, Parquet, LVC |
| S-361 | InfluxData — InfluxDB 3 Enterprise admin | <https://docs.influxdata.com/influxdb3/enterprise/admin/> | Vendor official docs | UNKNOWN | Snippet tìm kiếm | Med | 06, nF | HA, read replica, historical queries là Enterprise |
| S-362 | ClickHouse docs (RU) — time series | <https://clickhouse.com/docs/ru/faq/use-cases/time-series> | Vendor official docs | UNKNOWN | Snippet tìm kiếm | High | 06, nF | Codec DoubleDelta/Gorilla/T64; MV |
| S-363 | Medium (datadenys) — ClickHouse time series | <https://medium.com/datadenys/optimizing-timeseries-data-in-clickhouse-c6518a9d6da0> | Personal blog | UNKNOWN (cũ) | Snippet tìm kiếm | Low | nF | ~4× trên dữ liệu mượt, ~20% trên ngẫu nhiên |
| S-364 | QuestDB — trang chủ | <https://questdb.io> | Vendor official | UNKNOWN | Snippet tìm kiếm | Med | nF | Apache 2.0 |
| S-365 | QuestDB — release 8.1.0 | <https://questdb.io/blog/questdb-release-8-1-0> | Vendor blog | UNKNOWN | Snippet tìm kiếm | Med | 06, nF | Đọc Parquet; Parquet trên object storage là Enterprise |
| S-366 | Apache IoTDB — data model | <https://iotdb.apache.org/UserGuide/V1.3.x/Basic-Concept/Data-Model-and-Terminology.html> | OSS official docs (ASF) | UNKNOWN | Snippet tìm kiếm | High | nF | Tree model; aligned timeseries chia sẻ cột ts |
| S-367 | Solcast — rooftop sites hobbyist | <https://docs.solcast.com.au/docs/section/rooftop-sites-hobbyist> | Vendor official docs | UNKNOWN | Snippet tìm kiếm | High | 03, 04, 05, nF | PT30M, 10 lượt/ngày, ≤ 2 mảng |
| S-368 | GitHub — ha-solcast-solar | <https://github.com/BJReplay/ha-solcast-solar> | Community (OSS) | UNKNOWN | Snippet tìm kiếm | Med | nF | Tài khoản cũ 50 lượt (mâu thuẫn) |
| S-369 | EMHASS docs — forecasts | <https://emhass.readthedocs.io/en/latest/forecasts.html> | OSS docs | UNKNOWN | Snippet tìm kiếm | Med | nF | Solcast có P10/P50/P90 |
| S-370 | Open-Meteo blog — GTI MeteoFrance | <https://openmeteo.substack.com/p/global-tilted-irradiance-gti-meteofrance> | Vendor blog | UNKNOWN | Snippet tìm kiếm | Med | nF | GTI theo tilt/azimuth; AROME 15 phút chỉ Tây Âu |
| S-371 | Meltano Hub — tap-openmeteo | <https://hub.meltano.com/extractors/tap-openmeteo> | Third-party docs | UNKNOWN | Snippet tìm kiếm | Low–Med | nF | Thương mại cần API key, `customer-api` |
| S-372 | Meteomatics — MOS parameters | <https://www.meteomatics.com/en/api/available-parameters/mos-parameters/> | Vendor official docs | UNKNOWN | Snippet tìm kiếm | Med | nF | 15 ngày, 1 h, `global_rad` |
| S-373 | Meteotest API (host) | <https://api.meteotest.ch/> | Vendor API host | UNKNOWN | Snippet tìm kiếm | Low (chỉ host API) | nF | Tham số `gk` (bức xạ mặt nghiêng), `e` (kWh/kWp) |

### J. Bảo mật, sự cố và chính sách nhà cung cấp rủi ro cao

| S-ID | Tiêu đề / nhà xuất bản | URL | Loại nguồn | Ngày xuất bản | Cách tiếp cận | Độ tin cậy | Dùng trong | Claim chính được hỗ trợ |
|---|---|---|---|---|---|---|---|---|
| S-374 | Forescout — SUN:DOWN press release | <https://forescout.com/press-releases/forescout-vedere-labs-uncovers-severe-systemic-security-risks-in-global-solar-power-infrastructure> | Vendor (security research) press release | 27/03/2025 | Tệp nghiên cứu FS trước | Med–High | 03, 04, 06, 10, nI | 46 lỗ hổng Sungrow/Growatt/SMA; 80% high/critical |
| S-375 | Cybernews — China solar inverters hack | <https://cybernews.com/security/china-solar-inverters-hack/> | News | 07/2026 | Tệp nghiên cứu FS trước | Med | 10, nI | Hoymiles: cập nhật firmware/điều khiển từ xa không xác thực |
| S-376 | pv magazine — hidden devices (Reuters) | <https://www.pv-magazine.com/2025/05/14/hidden-devices-found-in-chinese-made-inverters-in-the-us-reports-reuters/> | News | 14/05/2025 | Tệp nghiên cứu FS trước | Med (đưa tin) / Low (nội dung) | 10, nI | Thiết bị liên lạc không tài liệu; không nêu hãng; "cannot verify" |
| S-377 | pv magazine India — no definitive evidence (DOE) | <https://www.pv-magazine-india.com/2026/01/29/u-s-authorities-find-no-definitive-evidence-of-hidden-devices-in-chinese-solar-inverters> | News | 29/01/2026 | Tệp nghiên cứu FS trước | Med | 10, nI | ~30 inverter; 2 trường hợp lệch tài liệu, "non-malicious" |
| S-378 | Defense News — sabotage fears in Europe | <https://www.defensenews.com/global/europe/2025/05/29/chinese-hold-on-solar-power-tech-raises-fresh-sabotage-fears-in-europe/> | News | 29/05/2025 | Tệp nghiên cứu FS trước | Med | 10, nI | 11/2024 inverter bị vô hiệu hóa từ xa do tranh chấp thương mại; không nêu hãng |
| S-379 | LRT — Lithuania blocks Chinese remote access | <https://www.lrt.lt/en/news-in-english/19/2411602/lithuania-passes-law-to-block-chinese-access-to-solar-and-wind-farm-systems> | News (đài quốc gia) | 11/2024 | Tệp nghiên cứu FS trước | High | 03, 04, 10, nI | Cấm truy cập từ xa của công ty TQ tới hệ > 100 kW; không cấm lắp đặt |
| S-380 | PV Tech — Lithuania cybersecurity legislation | <https://pv-tech.org/lithuania-to-block-chinese-inverters-with-cybersecurity-legislation> | News | 11/2024 | Tệp nghiên cứu FS trước | High | 10, nI | Như trên |
| S-381 | Solar Magazine NL — kabinet verscherpt toezicht | <https://solarmagazine.nl/nieuws-zonne-energie/i41070/kabinet-verscherpt-toezicht-op-chinese-omvormers-zonnepanelen-verbod-kill-switch-bestaat-al> | News | 07/2025 | Tệp nghiên cứu FS trước | Med | 10, nI | RED cybersecurity từ 1/8/2025; CRA từ 12/2027 |
| S-382 | pv magazine — EU high-risk vendors proposal | <http://www.pv-magazine.com/2026/01/20/eu-to-ban-chinese-inverters-commission-proposal-in-cybersecurity-mulls-high-risk-vendors-list/> | News | 20/01/2026 | Tệp nghiên cứu FS trước | Med | 10 | Đề xuất sửa Cybersecurity Act có danh sách nhà cung cấp rủi ro cao |
| S-383 | ESS News — EU funding ban high-risk inverters/BESS PCS | <https://www.ess-news.com/2026/05/04/eu-funding-ban-on-high-risk-inverters-including-chinese-suppliers-extends-to-bess-pcs/> | News | 04/05/2026 | Tệp nghiên cứu FS trước | Med | 10 | EIB/EIF chặn tài trợ inverter/BESS (gồm PCS) của nhà cung cấp rủi ro cao từ 1/5/2026 |
| S-384 | innobu — Chinese inverters high-risk list 2026 | <https://www.innobu.com/en/articles/chinese-inverters-security-risk-high-risk-list-2026.html> | Consultancy blog | 2026 | Tệp nghiên cứu FS trước | Low–Med | 10 | Quan điểm gần BSI: ưu tiên điều khiển cục bộ qua smart-meter gateway |
| S-385 | Romstal (mirror bán lẻ) — chứng chỉ RED Huawei SUN2000/SUN5000 | <https://cdn.contentspeed.ro/pimromstal.websales.ro/cs-content/cs-docs/products/35fv1635569certificateredforsun2000map0sun5000map0_78205_21_1784579986.pdf> | Certificate (mirror) | 21/08/2025 → 20/08/2030 | Tệp nghiên cứu FS trước | High (theo FS) | 10, nI | RED 3.3(d)/EN 18031-1:2024 cho inverter + dongle |

### K. Nguồn bị loại khỏi vai trò bằng chứng

| S-ID | Tiêu đề / nhà xuất bản | URL | Loại nguồn | Ngày xuất bản | Cách tiếp cận | Độ tin cậy | Dùng trong | Claim chính được hỗ trợ |
|---|---|---|---|---|---|---|---|---|
| S-386 | rfp.wiki — Ampowr vendor profile | <https://www.rfp.wiki/vendors/ampowr> | AI-generated directory | UNKNOWN | Snippet tìm kiếm | Low (tự ghi ~30%) | 02, nB, nC | KHÔNG dùng làm bằng chứng (K §4 bác bỏ) |
| S-387 | rfp.wiki — Stem vendor profile | <https://www.rfp.wiki/vendors/stem> | AI-generated directory | UNKNOWN | Snippet tìm kiếm | Low | nB | KHÔNG dùng làm bằng chứng |

---

## 3. Tệp nghiên cứu trước S-388…S-403

Nghiên cứu Huawei FusionSolar (07/10/2026) nằm ở `docs/research/fusionsolar/`. Người dùng cũng tải lên bản HTML/PDF của báo cáo, wireframe và gói zip tương ứng; lượt EMS dùng bản trong kho. Cách tiếp cận của mọi dòng dưới đây là **đọc tệp cục bộ** (Read/grep). Độ tin cậy là của *nội dung tệp*; mỗi tệp tự ghi nguồn gốc và nhãn FACT/INFERENCE/SPECULATION riêng.

| S-ID | Tệp | Nội dung | Loại | Ngày | Độ tin cậy | Dùng trong | Claim chính được hỗ trợ |
|---|---|---|---|---|---|---|---|
| S-388 | [`fusionsolar/README.md`](../fusionsolar/README.md) | Mục lục gói nghiên cứu, lưu ý giấy phép mã cộng đồng, mốc 01/12/2026 | Prior research | 07/10/2026 | High (mô tả gói) | 04, 07, 11, 13 | Hướng cũ: giám sát/O&M PV đa hãng, edge-first; UNKNOWN cần tài khoản installer; `huawei_solar` là AGPL-3.0 |
| S-389 | [`01_bao_cao/Nền tảng Huawei FusionSolar.md`](../fusionsolar/01_bao_cao/) | Báo cáo tổng quan ban đầu | Prior research | 07/10/2026 | Med–High | (nguồn gốc của URL S-185, S-382) | Bối cảnh API, bảo mật, tài liệu Modbus Huawei |
| S-390 | [`01_bao_cao/Phân rã sản phẩm FusionSolar.html`](../fusionsolar/01_bao_cao/) | Báo cáo reverse engineering 20 phần, bản đồ API web, ERD, blueprint MVP/V1/V2 | Prior research | 07/10/2026 | Med–High | nC | Quy ước dấu cũ (lưới + = xuất) đã được thay bằng K R-01; blueprint monitoring |
| S-391 | [`02_wireframe/Wireframe nền tảng giám sát PV.html`](../fusionsolar/02_wireframe/) | 15 màn hình low-fi, nhãn Observed/From manuals/Proposed | Prior research | 07/10/2026 | Med (bản vẽ đề xuất) | 09, nH | Cơ sở IA và component Angular cho 09 |
| S-392 | `04_ghi_chu_nghien_cuu/1_tong_quan/market_users_vietnam.md` | Thị trường, người dùng VN | Prior research | 07/10/2026 | Med | 02, nA | Bối cảnh installer/C&I VN; thị phần tự công bố |
| S-393 | `04_ghi_chu_nghien_cuu/1_tong_quan/api_integration.md` | Northbound, OAuth Connect, Modbus SmartLogger/SDongle/EMMA | Prior research | 07/10/2026 | High | 06, 07, nE | Northbound pull 5 phút có hạn mức; control API async; một client Modbus |
| S-394 | `04_ghi_chu_nghien_cuu/1_tong_quan/features_editions.md` | Tính năng theo phiên bản, gateway C&I | Prior research | 07/10/2026 | Med–High | 02, 03, nK | SmartLogger5000B **và** SmartMGC5000B là gateway C&I (cơ sở K R-19) |
| S-395 | `04_ghi_chu_nghien_cuu/1_tong_quan/architecture_security.md` | Kiến trúc, bảo mật, chính sách nhà cung cấp rủi ro cao | Prior research | 07/10/2026 | Med–High | 06, 07, 10, nE | Nguồn gốc S-379…S-384; Encrypted Modbus TCP outbound |
| S-396 | `04_ghi_chu_nghien_cuu/2_phan_ra_san_pham/demo_observations.md` | Quan sát trực tiếp demo + network | Prior research (quan sát trực tiếp) | 07/10/2026 | High (cho điều đã thấy) | 02, 03, 05, nC, nG, nH, nK | Release note 31/03/2026 SmartEMO demand charge theo TOU; polling ~5 s; Smart I-V 401 với guest; năm Phật lịch lọt vào UI |
| S-397 | `04_ghi_chu_nghien_cuu/2_phan_ra_san_pham/workflows_data_model.md` | Luồng nghiệp vụ, data model | Prior research | 07/10/2026 | Med–High | 03, 04, 05, 10, nC, nI | Vai trò/quyền, QR commissioning, thiếu xuất CSV |
| S-398 | `04_ghi_chu_nghien_cuu/2_phan_ra_san_pham/source_code_clients.md` | Đọc mã client cộng đồng (pyhfs, HA…) | Prior research (đọc mã) | 07/10/2026 | High (cho hành vi mã) | (nguồn gốc S-184) | thirdData login; timestamp thực tế UTC; throttling |
| S-399 | `04_ghi_chu_nghien_cuu/2_phan_ra_san_pham/source_code_clients_2.md` | Đọc mã client cộng đồng (tiếp) | Prior research (đọc mã) | 07/10/2026 | High | 05, nC, nG, nH, nI | `meterPower` + = xuất; ba quy ước dấu khác nhau giữa client; NBI VPP API |
| S-400 | `04_ghi_chu_nghien_cuu/2_phan_ra_san_pham/functions_ui_roles.md` | Chức năng, UI, vai trò từ manual | Prior research | 07/10/2026 | Med–High | 03, nH | Fail-safe 3 s; alarm → ticket; mục "Battery Control Parameters" |
| S-401 | `04_ghi_chu_nghien_cuu/2_phan_ra_san_pham/business_model_positioning.md` | Mô hình kinh doanh Huawei | Prior research | 07/10/2026 | Med | (nguồn gốc S-151, S-152) | Huawei cho dashboard miễn phí kèm phần cứng |
| S-402 | `04_ghi_chu_nghien_cuu/2_phan_ra_san_pham/competitors_rebuild.md` | Đối thủ giám sát (AMMP, Solytic, meteocontrol, Gantner, Power Factors…) | Prior research | 07/10/2026 | Med | 02, 06, 07, nB, nE, nF | Nguồn gốc FS-01…FS-14 trong 02 |
| S-403 | `03_anh_demo/01…09_*.jpg` (+ `raw/`) | 9 ảnh chụp màn hình demo thật | Prior research (ảnh gốc) | 07/10/2026 | High (cho điều hiển thị) | 03, 09, nH | Energy flow không có chữ nhập/xuất; "Công suất" đi với kWh; định dạng số lẫn lộn; trạng thái chỉ bằng màu |

Ghi chú: README nhắc thư mục `05_tai_lieu_huawei/` (NBI V500/V600) nhưng thư mục này **không có** trong kho tại 2026-10-10. Bản NBI V600R022C00 được trích qua mirror GitHub (S-178).

### 3.1 Bảng quy đổi mã tạm L/FS sang S-ID

Ma trận [02 §7](02-market-and-competitor-analysis.html#ma-tran), sổ bằng chứng [02 §13.2](02-market-and-competitor-analysis.html#bang-chung) và cột "Bằng chứng · đối thủ" của [03](03-functional-catalog.html) (dạng `B·Lnn`) dùng mã tạm L01…L49, L37b (lấy từ [ghi chú B §5](notes/B-competitors.md)) và FS-01…FS-15 (từ S-402). Bảng dưới quy đổi từng mã sang S-ID bằng cách khớp đúng chuỗi URL trong 02 §13.2 với cột URL của §2. Tất cả khớp chính xác; không có mã nào thiếu S-ID. Độ tin cậy và cách tiếp cận lấy theo dòng S-ID ở §2/§3, không theo cột "Tin cậy" của 02. Các nguồn này **chưa được reviewer spot-check** (V-14).

| Mã tạm | S-ID | Ghi chú |
|---|---|---|
| L01 | S-080, S-081 | Ampowr Cosmos, trang EMS |
| L02 | S-091, S-083 | Ampowr NIS2/ISO 27001 tự tuyên bố; backup power |
| L03 | S-087, S-086 | Ampowr case van Pinxteren; imbalance trading |
| L04 | S-089 | Ampowr case Hoge Duin (peak shaving 95 kW) — nguồn ô G1 |
| L05 | S-090 | AmpiHealth |
| L06 | S-082, S-084 | Ampowr peak shaving; generator steering |
| L07 | S-386 | rfp.wiki — **bị loại** (§4.3), không dùng làm bằng chứng |
| L08 | S-098, S-099 | HTI 50 kWh; commercial solutions |
| L09 | S-102 | HTI container 1.000 kWh |
| L10 | S-101 | HTI hybrid 261/522 kWh |
| L11 | S-100 | HTI 125 kW/261 kWh |
| L12 | S-097 | HTI "AI-Powered EMS" (EL-039) |
| L13 | S-103 | HTI container 2.000 kWh — nguồn ô G1 |
| L14 | S-105, S-104 | Schneider EMA trang sản phẩm; handout ~2017 — nguồn ô G1 |
| L15 | S-106 | Schneider EMA Microsoft Marketplace |
| L16 | S-107, S-108 | Schneider ESXP Microgrid PDF; ECC demo |
| L17 | S-109 | Schneider brochure microgrid |
| L18 | S-110 | Schneider ESXP cyber (IEC 62443) |
| L19 | S-111, S-112 | Schneider EMO; pv-magazine-usa |
| L20 | S-113, S-114 | Schneider PME; PME help |
| L21 | S-115, S-116 | Siemens SICAM MGC brochures — nguồn ô G1 |
| L22 | S-117 | Siemens SICAM MGC trang sản phẩm |
| L23 | S-119 | Siemens slide 2022 (GOOSE ~70 ms) |
| L24 | S-122 | Siemens whitepaper 2022 |
| L25 | S-124 | ARC — Electrification X |
| L26 | S-127, S-128 | ABB OPTIMAX tin; energy management |
| L27 | S-131, S-130 | ABB OPTIMAX 6.4 "AI" (Verified*) |
| L28 | S-133, S-134, S-135 | ABB e-mesh; Hitachi Energy 2021; thoái vốn Power Grids |
| L29 | S-136 | ABB Energy and Asset Manager |
| L30 | S-139, S-140 | SolarEdge ONE C&I; businesswire 12/2024 — nguồn ô G1 |
| L31 | S-142 | SolarEdge ONE C&I overview |
| L32 | S-143 | SolarEdge Site Admin user guide |
| L33 | S-148 | SolarEdge mua Wevo |
| L34 | S-144, S-145 | SolarEdge ONE Controller datasheet; user guide |
| L35 | S-147 | SolarEdge feed-in limitation app note |
| L36 | S-150 | Huawei C&I SmartPVMS |
| L37 | S-154, S-153 | Huawei ≤ 2 s/≤ 5 s tự công bố, SmartLogger5000B/SmartMGC5000B (EL-025) — nguồn ô G1. Liên kết "datasheet SmartMGC5000B theo E F-28" trong 02 là S-153 (model tranh chấp, K R-19). S-155 (BayWa) hỗ trợ cùng claim nhưng 02 không trích |
| L37b | S-158 | Manual LUNA2000-(107-215) C&I-Microgrid-SmartLogger3000 (phạm vi hẹp, K R-20) |
| L38 | S-160 | Huawei EMMA |
| L39 | S-163, S-180 | Huawei Northbound control APIs; Solytic |
| L40 | S-120, S-121 | Siemens SICAM SCC; chứng chỉ WinCC OA IEC 62443 |
| L41 | S-187, S-188, S-186 | Sungrow PowerStack 255CS — nguồn ô G1 |
| L42 | S-191, S-193 | Sungrow iSolarCloud datasheet; Eniris docs |
| L43 | S-200, S-206, S-214 | OpenEMS docs; repo balancing; forum — nguồn ô G1 (S-200) |
| L44 | S-210, S-211, S-204 | OpenEMS release notes Zenodo; repo (giấy phép UNKNOWN, K R-21) |
| L45 | S-216 | OpenEMS §14a EnWG (bayern-innovativ) |
| L46 | S-218, S-220 | Stem PowerTrack EMS; thư cổ đông (số liệu Low) |
| L47 | S-221 | Stem Athena (ô G1 chỉ Partial) |
| L48 | S-222, S-224 | Stem DAS; AlsoEnergy PowerTrack flier |
| L49 | S-225, S-226 | GridBeyond ViewPoint Lens; solarimpulse |
| FS-01 | S-060 | meteocontrol reference Đông Nam Việt Packaging |
| FS-02 | S-061 | meteocontrol reference MP Pack Đà Nẵng (zero-feed-in) |
| FS-03 | S-059 | Gantner — năm dự án mái nhà VN |
| FS-04 | S-232 | Solytic giá |
| FS-05 | S-181 | meteocontrol VCOM nhập API Huawei |
| FS-06 | S-229 | Power Factors Unity |
| FS-07 | S-151 | Huawei SmartPVMS installer |
| FS-07a | S-231 | AMMP |
| FS-08 | S-192 | Sungrow iSolarCloud I-V (pv-magazine-usa) |
| FS-09 | S-177 | FusionSolar 7.0 training slides (bản sao) |
| FS-10 | S-234 | evcc — Huawei SCharger |
| FS-11 | S-058 | Sungrow thị phần mái nhà VN tự công bố (2020) |
| FS-12 | S-233 | Solar-Log Base datasheet |
| FS-13 | S-046 | Advantech — QĐ 1570 (Low, EL-008) |
| FS-14 | S-152 | Huawei Smart PV Plant Management |
| FS-15 | S-396 | Release notes FusionSolar quan sát trực tiếp (không có URL công khai) |

---

## 4. URL đáng ngờ, nguồn bị loại và chuỗi không phải nguồn

Registrar đã thử spot-check bằng WebSearch nhưng hạn mức đã hết. Các cờ dưới đây dựa trên cấu trúc URL, đối chiếu chéo giữa ghi chú và đối chiếu với tệp FS trước. **Không phát hiện URL có dấu hiệu bịa**: 68/387 URL có trong nghiên cứu FS trước; mọi URL chỉ xuất hiện trong deliverable (23 URL) đều truy được về `docs/research/fusionsolar/`; các URL còn lại xuất hiện kèm ngữ cảnh snippet trong ghi chú A/B/C/E/F.

### 4.1 URL gắn cờ (vẫn giữ trong sổ)

| S-ID | Vấn đề | Xử lý |
|---|---|---|
| S-095 | Trang seed InfinitePower: A/C/G ghi thấy qua snippet, B **không thấy** URL trong kết quả tìm kiếm (K R-18) | Chỉ dùng cho định nghĩa chung, kèm S-330. Không gán tính năng sản phẩm. Độ tin cậy Low |
| S-103 | URL có dấu "/" sau `.html` | Có thể là biến thể do công cụ tìm kiếm trả về. Giữ, Low–Med khi trích |
| S-105 | Hai biến thể có/không "/" cuối (`…/65896` và `…/65896/`) | Gộp một S-ID |
| S-129 | `energymanagement-calculator.abb.com` không có đường dẫn, không rõ nội dung | Không dùng làm bằng chứng tính năng OPTIMAX; dùng S-127, S-130 |
| S-153 | Asset PDF dạng hash của solar.huawei.com; E gán cho SmartMGC5000B, A/B/G gán SmartLogger5000B (K R-19) | Ghi "SmartLogger5000B/SmartMGC5000B"; số là tự công bố |
| S-158 | Manual Huawei qua mirror nhà phân phối | Ràng buộc "peak shaving chỉ on/off-grid" chỉ đúng trong phạm vi manual này (K R-20) |
| S-185 | Tài liệu Modbus Huawei tải lên diễn đàn ioBroker | Bản sao không chính thức; không dùng cho driver `VERIFIED_*` khi chưa có bản từ Huawei |
| S-252 | Một số tài liệu ghi URL bị cắt trước `).pdf` | Sổ ghi dạng đầy đủ; người viết sửa trích dẫn khi chạm tới |
| S-263 | Short link `docs.chariot.io/x/…` | Không truy được tiêu đề; Med |
| S-295 | Trang Deye trả 403, nội dung chưa đọc | Chỉ xác nhận trang tồn tại; không suy diễn sự cố |
| S-310 | URL chứa `%EF%B9%96` (ký tự "﹖" toàn chiều rộng) thay cho `?` | Có thể đã bị biến đổi khi sao chép; có thể không mở được. Đối chiếu lại khi có mạng |
| S-311 | `mcpservers.org` (danh mục máy chủ MCP) làm nguồn thanh ghi Victron | Low; phải đối chiếu register list chính thức của Victron |
| S-316 | Short link `sunplus.atlassian.net/wiki/x/…` | Low–Med; chỉ dùng cho con số NTP/PTP tổng quát |
| S-335 | arXiv 2605.14043 (ID ứng với 05/2026) | Có cấu trúc hợp lệ; chưa xác minh tồn tại; claim có nguồn thứ hai S-336 |
| S-373 | `api.meteotest.ch` chỉ là host API | Low; không phải tài liệu |
| S-385 | Chứng chỉ RED của Huawei lưu trên CDN của nhà bán lẻ Romstal | Mirror; trước khi trích trong tài liệu bán hàng phải lấy bản từ tổ chức chứng nhận |

### 4.2 Chuỗi URL không phải nguồn (không cấp S-ID)

| Chuỗi | Xuất hiện ở | Lý do |
|---|---|---|
| `https://enroll` | 06 (API-INT-02) | Ví dụ endpoint enrollment của edge, không phải nguồn |
| `https://{edge-local}/` | 09 (UI-36) | Mẫu địa chỉ HMI cục bộ của edge |
| `https://eu1-developer.deyecloud.com/v1.0` | nE, 07 | Base URL API do client cộng đồng (S-293) nêu; không phải tài liệu |
| `…/65896` (không "/") và URL NRECA bị cắt | nA, nE, 07 | Biến thể của S-105 và S-252 |

### 4.3 Nguồn bị loại khỏi vai trò bằng chứng

| S-ID | Nguồn | Lý do | Hệ quả |
|---|---|---|---|
| S-386, S-387 | rfp.wiki (Ampowr, Stem) | Hồ sơ do AI sinh, tự ghi độ tin cậy ~30% (B L07; K §4) | Không trích làm FACT. Claim "Ampowr kích máy phát khi SOC thấp / API respecting safety" (C #23) chỉ giữ ở mức có S-084, S-089 |
| S-097 | InfinitePower "AI-Powered EMS" | Marketing không mô tả kỹ thuật | Chỉ dùng làm ví dụ AI-washing, không làm bằng chứng năng lực AI |
| S-223, S-220 | Số liệu tự công bố của Stem (tiết kiệm "tới 30%", 99,99%, −32% giờ kỹ sư) | Không kiểm chứng độc lập | Không dùng làm KPI hay mục tiêu bán hàng |

---

## 5. Evidence ledger (100 claim quan trọng nhất)

Chọn theo mức ảnh hưởng tới quyết định P0/MVP, yêu cầu bắt buộc, kiến trúc và tuyên bố ra bên ngoài. Nhãn đã áp phán quyết K (§2, §4 của [K](notes/K-review-round1.md)). "Excerpt" là trích ngắn hoặc diễn giải từ snippet do agent ghi, không phải trích từ văn bản gốc mà Registrar đã đọc.

### 5.1 Pháp lý, biểu giá, thị trường Việt Nam

| # | Claim | Nhãn | S-IDs | Excerpt / diễn giải | Độ tin cậy | Bằng chứng mâu thuẫn | Hệ quả thiết kế |
|---|---|---|---|---|---|---|---|
| EL-001 | NĐ 58/2025 (03/03/2025) thay NĐ 135/2024 về ĐMTMN tự sản xuất, tự tiêu thụ | FACT | S-002, S-003 | "takes effect immediately and replaces Decree 135/2024" | High | — | Cơ sở pháp lý dùng NĐ 58 + 243; bỏ tham chiếu 135 |
| EL-002 | NĐ 243/2026 (hiệu lực 26/06/2026) nâng trần bán điện dư lên 50% sản lượng thực phát; được vượt tới 31/12/2030 nếu lưới tiếp nhận | FACT | S-006, S-007, S-008, S-011, S-012 | "increases the limit… from 20% to 50%" | Med–High | Mẫu số tỷ lệ (thực phát hay khác) diễn đạt khác nhau | `export_mode = EXPORT_ENERGY_BUDGET` (P1), tham số mặc định 50% × E_pv tại `MTR_PV`, giữ `[UNKNOWN]` tới khi đọc VBHN 52 |
| EL-003 | Điện xả từ BESS nạp bằng ĐMTMN được tính vào phần điện dư | FACT | S-007, S-010 | "purchasable excess electricity includes… energy discharged from connected BESS" | Med | Chưa đọc toàn văn | Thuật toán phân bổ luồng năng lượng có `attribution_version`; quy kết kWh xuất theo nguồn |
| EL-004 | Cơ sở trần 20% của NĐ 58 bản đầu: nguồn nói "sản lượng thực phát/tháng", nguồn khác nói "công suất lắp đặt" | FACT (mâu thuẫn được ghi nhận) | S-004, S-005 | "20% of actual monthly generated output" vs "20% of installed capacity" | Med | Có | Hỗ trợ cả giới hạn theo kW và theo kWh |
| EL-005 | Cuối 07/2026: 28.254 hệ TSXTTT (~1.614 MWp), chỉ ~287 hệ (~16,4 MW) đăng ký bán dư | FACT | S-013, S-014 | Số liệu từ EVN/báo | Med | — | Zero-export/giới hạn xuất là giá trị P0 số 1 |
| EL-006 | Tới 08/2026 chưa ghi nhận giao dịch bán dư nào theo NĐ 243 | FACT | S-015 | "have not yet produced a single recorded sale" | Med | — | Không xây MVP quanh bán điện; bán dư là P1 |
| EL-007 | Hệ trung áp không bán dư phải có thiết bị chống phát ngược; hạ áp chưa rõ | FACT (trung áp, theo tóm tắt) / UNKNOWN (hạ áp) | S-001, S-046 | Tóm tắt VBHN 52 và Advantech | Low–Med | K: không được viết "bắt buộc pháp lý cho mọi site" | Rơ-le chống phát ngược là bảo vệ native; phần mềm chỉ là lớp tuân thủ thứ 4 của arbiter |
| EL-008 | QĐ 1570/QĐ-EVN yêu cầu kết nối điều độ Modbus TCP + IEC 104, "≥ 64 kbps, ≤ 125 ms" | FACT, Low (nguồn vendor có lợi ích) | S-046, S-047 | Tóm tắt của Advantech | Low | Chưa đọc QĐ 1570 | Không đưa số vào NFR; slave IEC 104 trên edge là P1 có điều kiện (K R-10) |
| EL-009 | QĐ 963/QĐ-BCT (22/04/2026): cao điểm 17h30–22h30 T2–T7, thấp điểm 0h–6h, CN không cao điểm | FACT | S-016, S-017 | Bảng khung giờ | Med–High | Ngày áp vào hóa đơn: EL-010 | Lịch TOU là dữ liệu có phiên bản, không hard-code |
| EL-010 | Khung giờ mới có thể chưa áp vào hóa đơn thực (07/2026) | UNKNOWN | S-018, S-019 | "chưa được áp dụng trên thực tế" | Low–Med | Nguồn khác nói đã/dự kiến áp từ 06/2026 | Hai lịch song song: lịch pháp lý và lịch hóa đơn |
| EL-011 | Khung giờ cũ (TT 16/2014): cao điểm 9h30–11h30 và 17h–20h; thấp điểm 22h–4h | FACT | S-020 | Bảng khung giờ cũ | Med–High | — | Giữ để tính lại dữ liệu lịch sử |
| EL-012 | Giá QĐ 1279 (hiệu lực 10/05/2025), ví dụ cấp 22–<110 kV: 1.190 / 1.833 / 3.398 đ/kWh (TĐ/BT/CĐ) | FACT | S-021, S-022 | Bảng 4 cấp điện áp | Med–High | Có thể điều chỉnh (EL-013) | Bảng giá là dữ liệu theo cấp điện áp; chênh CĐ/TĐ ~2,8× là cơ sở giá trị TOU |
| EL-013 | NĐ 278/2026 sửa cơ chế điều chỉnh giá bình quân (ngưỡng 2%/5%) | FACT | S-023 | Ngưỡng điều chỉnh | Med | — | Giá có thể đổi bất kỳ lúc nào → `TariffVersion` có hiệu lực theo ngày |
| EL-014 | Giá hai thành phần thí điểm cho khách ≥ 200.000 kWh/tháng; chạy song song 01–06/2026; thanh toán thí điểm 07/2026–07/2027 | FACT | S-024, S-025, S-028, S-029 | Lộ trình thí điểm | Med | Mốc 10/2025 vs 01/2026 | M-TAR hỗ trợ thành phần demand; peak shaving theo demand là P1 |
| EL-015 | Chu kỳ tích phân công suất hiện nay là 30 phút | FACT | S-026, S-027 | "khoảng thời gian tích phân hiện nay đang là 30 phút" | Med | Block hay trượt: UNKNOWN | Cửa sổ demand mặc định 30 phút, giả định block |
| EL-016 | Cơ sở tính thành phần công suất: công suất đăng ký hay Pmax đo | UNKNOWN | S-024, S-026 | A: "phần công suất đăng ký"; C: Pmax 30 phút | Low | Có (K R-16) | `demand_basis ∈ {MEASURED_MAX, CONTRACTED}`, mặc định tắt |
| EL-017 | Đại đa số C&I VN chưa trả phí công suất; khách thí điểm có thể đã trả từ 07/2026 | INFERENCE | S-014 | Suy từ lịch thí điểm | Med | Ghi chú A ban đầu gắn FACT (bị hạ, K R-17) | Không hiển thị demand meter khi biểu giá không có thành phần demand |
| EL-018 | Trạm sạc EV có biểu giá riêng (QĐ 14/2025, TT 60/2025); trạm kinh doanh có công tơ riêng | FACT | S-030, S-031 | Quy định giá trạm sạc | Med | Mức giá chưa đối chiếu | Nhiều biểu giá trong một site; `MTR_EV` |
| EL-019 | TT 05/2025/TT-BCT Đ.31: cosφ ≥ 0,9 tại điểm đặt công tơ cho đối tượng theo điều kiện | FACT | S-042, S-043 | Ngưỡng cosφ | Med | Hai snippet mô tả đối tượng khác nhau | KPI PF tại POC; cảnh báo PF thấp (giám sát, không điều khiển Q ở MVP) |
| EL-020 | Hệ số phát thải lưới VN 2023 = 0,6592 tCO2/MWh (CV 1726); 2024/2025 chưa công bố chính thức | FACT (2023) / UNKNOWN (2024–2025) | S-050, S-051, S-052, S-053 | 0,6592; ước 2024 0,681 | High (2023) | Ước tính khác nhau | EF là dữ liệu có phiên bản; giá trị ước tính gắn nhãn `PROVISIONAL_EF` |
| EL-021 | QHĐ8 điều chỉnh: BESS 10.000–16.300 MW vào 2030 | FACT | S-034, S-035 | Mục tiêu BESS | Med–High | — | Phần lớn là BESS phía lưới (INFERENCE); không phải thị trường mục tiêu MVP |
| EL-022 | BESS lưới đầu tiên: EVNHANOI 50 MW/100 MWh (07/2026); EVNNPC giai đoạn đầu 305 MW/610 MWh | FACT | S-040, S-041 | Số liệu dự án | Med–High | — | EVN là khách nhóm grid EMS, ngoài phạm vi 12–18 tháng |
| EL-023 | NĐ 243 mở rộng DPPA (bỏ ngưỡng bên mua, mở cho DC/sạc EV, rút gọn thủ tục) | FACT | S-007, S-009 | Như claim | Med | — | Dữ liệu đo đếm phục vụ DPPA là P2 |
| EL-024 | Phân khúc EPC–ESCO đa site có thật ở VN (SolarBK + Banpu NEXT + Amata 227 MWp) | FACT (tự công bố) | S-055, S-056, S-057 | Thông cáo doanh nghiệp | Med | Nguồn tự công bố | Persona ESCO/EPC đa site; multi-tenant |

### 5.2 Đối thủ và tham chiếu sản phẩm

| # | Claim | Nhãn | S-IDs | Excerpt / diễn giải | Độ tin cậy | Bằng chứng mâu thuẫn | Hệ quả thiết kế |
|---|---|---|---|---|---|---|---|
| EL-025 | Bộ điều khiển site C&I của Huawei (SmartLogger5000B/SmartMGC5000B) công bố zero feed-in vòng kín ≤ 2 s, peak shaving/giới hạn công suất ≤ 5 s | FACT (tự công bố) | S-153, S-154, S-155 | "closed-loop control for zero feed-in within 2s" | Med | Model chính xác (K R-19); S-394 (nghiên cứu FS trước) chỉ xác nhận SmartLogger5000B và SmartMGC5000B đều là gateway C&I, **không** hỗ trợ con số ≤ 2 s/≤ 5 s | Mục tiêu tham chiếu cho NFR vòng nhanh; ưu tiên `control_owner = NATIVE` |
| EL-026 | Huawei C&I: peak shaving chỉ hỗ trợ trong kịch bản on/off-grid (PQ/VSG) — **chỉ trong manual LUNA2000-(107-215) SmartLogger3000** | FACT (phạm vi hẹp) | S-158 | Như claim | Med | Mâu thuẫn với capacity control của SmartLogger5000B (S-154) và `set_capacity_control_periods` (S-297) | Ma trận chế độ hợp lệ theo model/firmware; không tổng quát hóa |
| EL-027 | Huawei Northbound control API là task bất đồng bộ, chỉ ở OAuth Connect, cấm gọi lặp trước khi task xong | FACT | S-163, S-164, S-393 | "available only in OAuth Connect mode" | High | — | Connector cloud hãng chỉ dùng cho giám sát/lịch chậm, không cho điều khiển |
| EL-028 | Huawei Northbound: lịch sử tối đa 10 thiết bị × 3 ngày ở 5 phút mỗi lần gọi; pull có hạn mức | FACT | S-165, S-393 | "5-minute data of a maximum of 10 devices… in three days" | High | — | Backfill theo lô; site có lệnh phải có edge của ta |
| EL-029 | FusionSolar lấy mẫu 5 phút, tổng hợp giờ trước ở phút thứ 5, khôi phục ≤ 24 h, tính lại 02:00 | FACT | S-177 | "summarized at the fifth minute of the next hour" | Med | — | Job ngày theo giờ địa phương có độ trễ; tính lại khi dữ liệu về muộn |
| EL-030 | Huawei EU giữ 15 tháng dữ liệu thiết bị, 15 tháng báo cáo giờ, 5 năm ngày/tháng, 25 năm năm | FACT | S-174 | Bảng lưu giữ | High | APAC chưa rõ | Retention của ta: raw 13 tháng, 5 phút 5 năm, giờ+ suốt vòng đời |
| EL-031 | meteocontrol đo 5 phút, truyền 15 phút, mỗi đêm hỏi lại 7 ngày | FACT | S-181 | Như claim | High | — | Cửa sổ tính lại CAGG ≥ 7 ngày; NFR không mất dữ liệu ≤ 7 ngày |
| EL-032 | Huawei đổi chính sách API (09/2025), owner phải cấp quyền, làm hỏng tích hợp bên thứ ba | FACT | S-182, S-388 | Báo cáo cộng đồng | Med | — | Phụ thuộc cloud hãng là rủi ro khả dụng; edge-first |
| EL-033 | Schneider EMA: MPC trên cloud từ giá/lịch sử/thời tiết/lịch vận hành; lịch mặc định 48 h khi mất server | FACT, Low–Med (một nguồn chính, ~2017) | S-104, S-105, S-106 | "48-hour advance default operation schedules" | Low–Med | 48 h vs 72 h (K R-23) | Lịch dự phòng ≥ 48 h tại edge là PROPOSAL độc lập |
| EL-034 | Schneider gửi lệnh qua hệ quản lý con (EV, BMS tòa nhà) thay vì thay thế chúng | FACT | S-109 | "Control orders… to existing managers" | Med–High | — | Supervisory trên controller native; không chạy hai vòng trên cùng biến |
| EL-035 | Ampowr Cosmos tuyên bố "local backup feature": mất mạng vẫn chạy chiến lược và thu dữ liệu | FACT (tuyên bố hãng) | S-089, S-081 | "continue to perform strategies… through a local backup feature" | Med | — | Edge giữ lịch và chiến lược khi mất kết nối |
| EL-036 | Ampowr tự tuyên bố ISO 27001, NIS2, host EU | FACT (tự tuyên bố) | S-091, S-085 | "ISO27001 certified and NIS2 compliant" | Med | Không thấy registry chứng chỉ | Ta không tuyên bố tuân thủ khi chưa có chứng chỉ |
| EL-037 | Ampowr bid đồng thời Day-Ahead + imbalance + aFRR (Hà Lan) | FACT | S-087, S-086, S-088 | "bid together" | Med | Chỉ thị trường NL | Giao dịch thị trường ngoài phạm vi 12–18 tháng |
| EL-038 | EMS lưu trữ điều phối BMS và PCS; giám sát, lập lịch, chẩn đoán | FACT, Low (seed, một agent) + nguồn thứ hai | S-095, S-330 | Định nghĩa chung | Low–Med | B không thấy S-095 (K R-18) | Phân lớp EMS ↔ PCS ↔ BMS; chỉ dùng như định nghĩa |
| EL-039 | [FACT] Trang "AI-Powered EMS" của InfinitePower dùng nhãn "AI-Powered", nêu ví dụ 10–12% giảm phí đỉnh, không mô tả kỹ thuật (mô hình, dữ liệu, đánh giá). [INFERENCE] Coi trang là tuyên bố marketing, chưa phải bằng chứng năng lực AI | FACT (nội dung trang) / INFERENCE (đánh giá) | S-097 | Ví dụ 10–12% giảm phí đỉnh | Low | — | Không gọi luật cố định là AI; quy tắc đặt tên AI/ML |
| EL-040 | Tủ BESS HT có EMS riêng (lập lịch, peak shaving, SOC, cảnh báo) nhưng không công bố register map/API | FACT / UNKNOWN (giao thức) | S-100, S-101, S-102, S-103 | "automated scheduling, peak shaving, SOC tracking" | Med | Dải DC mâu thuẫn giữa trang | Ta là lớp supervisory; driver cần map từ hãng |
| EL-041 | SolarEdge ONE for C&I: lõi miễn phí cho người mua phần cứng, gói trả phí đưa ra dần | FACT | S-142 | "paid software packages… introduced gradually" | Med–High | — | Không cạnh tranh bằng dashboard; định giá theo giá trị đa hãng/điều khiển |
| EL-042 | SolarEdge export limitation cần công tơ tại điểm đấu nối; công tơ tiêu thụ không được hỗ trợ | FACT | S-147 | "Consumption meters are not supported in export limitation use cases" | High | — | `MTR_POC` bắt buộc cho mọi điều khiển lưới |
| EL-043 | SMA Data Manager M cần công tơ POI; peak shaving qua add-on Energy Maximizer | FACT | S-197, S-198 | Như claim | Med | — | Như EL-042 |
| EL-044 | SolarEdge ONE Controller C&I: 2×RS485, CAN, 2×RJ45, Wi-Fi 6, BLE 5.3, 4DI/4DO; Modbus TCP cổng 1502 | FACT | S-144, S-145, S-146 | "Modbus TCP on port 1502" | High | Không thấy LTE (≠ không hỗ trợ) | Danh mục giao diện tham chiếu cho phần cứng edge |
| EL-045 | Sungrow PowerStack 255CS tích hợp EMS/PCS/BMS, mở Modbus TCP cho EMS bên thứ ba | FACT | S-186, S-187, S-188 | "Modbus TCP… with EMS300CP or a third-party EMS" | Med | — | Đường tích hợp ưu tiên với tủ BESS Sungrow |
| EL-046 | Peak shaving có tài liệu ở ≥ 8/11 sản phẩm được xét; là "table stakes" | INFERENCE | S-089 (Ampowr, L04), S-103 (HTI, L13), S-104, S-105 (Schneider, L14), S-115 (Siemens, L21), S-139 (SolarEdge, L30), S-153, S-154 (Huawei, L37), S-186 (Sungrow, L41), S-200 (OpenEMS, L43) | Tổng hợp ô G1 = Verified của ma trận [02 §7](02-market-and-competitor-analysis.html#ma-tran); Stem (L47, S-221) và GridBeyond (L49) chỉ Partial, ABB Unknown nên không tính | Med | Ghi chú B ban đầu gắn FACT "mọi sản phẩm" (bị hạ) | Peak shaving theo giới hạn nhập là P0 (vật lý); theo demand charge là P1 |
| EL-047 | Các sản phẩm có tài liệu (Schneider, Ampowr, Huawei, OpenEMS, Stem) đều đặt vòng nhanh tại site | INFERENCE | S-104, S-089, S-154, S-200, S-218 | Tổng hợp | Med | — | Cloud không ở vòng nhanh; edge bắt buộc ở site có lệnh |
| EL-048 | OpenEMS: lưới + = mua, ESS + = xả; Consumption = Grid + Production + Storage | FACT | S-212, S-202 | "positive: buy-from-grid"; "Negative values for Charge" | Med–High | Huawei `meterPower` + = xuất (S-399) | Quy ước dấu chuẩn K R-01 |
| EL-049 | OpenEMS `ess.balancing` cân bằng PCC về `targetGridSetpoint` (mặc định 0 W) | FACT | S-206, S-200 | "balanced to 0 Watt" | High | — | Mô hình setpoint lưới cho vòng edge |
| EL-050 | Repo OpenEMS có file EPL-2.0 và AGPL-3.0; giấy phép từng module chưa rõ | UNKNOWN | S-204 | Hai file license | Med | E ghi chỉ EPL-2.0 (K R-21) | Chặn ADR edge runtime tới khi pháp chế đọc LICENSE từng module; không tái dùng UI OpenEMS |
| EL-051 | OpenEMS: API Modbus/TCP ghi kênh không phải đường điều khiển ESS; điều khiển qua controller + Power Solver | FACT | S-214 | Cảnh báo trên forum | Med | — | Một bộ phân xử (arbiter) duy nhất ở edge |
| EL-052 | Stem PowerTrack EMS gồm portfolio, PPC, SCADA, edge UI, unit controller không phụ thuộc phần cứng | FACT | S-218, S-219 | "hardware-agnostic unit controllers" | Med–High | FY2025 định vị utility | Tham chiếu edge UI cục bộ (P1) |
| EL-053 | Số tiết kiệm của vendor (Stem "tới 30%") là tuyên bố chưa kiểm chứng | FACT (về việc tuyên bố) | S-223, S-220 | "up to 30%" | Low | — | Không quảng cáo % tiết kiệm; dùng shadow bill so với baseline cùng phiên bản biểu giá |
| EL-054 | GridBeyond tuyên bố tối ưu tôn trọng ràng buộc tài sản và mô hình suy hao | FACT (tuyên bố) | S-225 | "respects asset-level constraints and degradation models" | Med | — | `c_deg` trong mục tiêu tầng 3 (P1) |
| EL-055 | Power Factors Unity gộp APM + CMMS (ticket/work order) | FACT | S-228, S-229, S-230 | Như claim | Med | — | Tham chiếu cho quy trình O&M (G-01 của K) |
| EL-056 | Huawei EMMA dự báo dư PV và giữ SOC space reserve; có panel so sánh có/không EMMA | FACT | S-160, S-167 | "forecasts your surplus PV power…" | High | Nhắm hộ/thương mại nhỏ | `SOC_ceiling` có space reserve; giải thích "có/không tối ưu" |
| EL-057 | Huawei SmartEMO C&I hỗ trợ demand charge theo khung TOU (release note 31/03/2026) | FACT (quan sát trực tiếp) | S-396 | Release note trên portal demo | Med | Không có URL công khai | Đối thủ đã chuẩn bị cho giá hai thành phần |

### 5.3 Tích hợp thiết bị và giao thức

| # | Claim | Nhãn | S-IDs | Excerpt / diễn giải | Độ tin cậy | Bằng chứng mâu thuẫn | Hệ quả thiết kế |
|---|---|---|---|---|---|---|---|
| EL-058 | Modbus: đọc FC03/04 tối đa 125 thanh ghi; ghi FC16 tối đa 123 | FACT | S-235, S-236 | "125 registers… 123 registers" | High | — | Planner block đọc ≤ 125, ghi ≤ 123 |
| EL-059 | Thứ tự word cho giá trị 32/64 bit không được chuẩn hóa; CDAB phổ biến | FACT | S-237, S-238 | Spec không định nghĩa float | Med | Thuật ngữ "endian" không thống nhất | `word_order` khai báo theo từng thanh ghi |
| EL-060 | SunSpec 701–712 đã APPROVED; họ 800 (lưu trữ) mới ở trạng thái TEST | FACT | S-242, S-243, S-244 | "promoted… to APPROVED"; "from DRAFT to TEST" | Med–High | Slide 2014 đánh số khác (S-246) | Ưu tiên 70x; ghi qua 802 cần kiểm chứng từng thiết bị |
| EL-061 | Thiết bị có chứng nhận UL 1741 SB vẫn có lỗi giao diện SunSpec | FACT | S-250, S-252 | "very few vendors had completed SunSpec Modbus Certification" | Med–High | — | Readback bắt buộc; chứng nhận đấu nối ≠ an toàn điều khiển |
| EL-062 | Huawei inverter/SmartLogger chỉ nhận một client Modbus tại một thời điểm | FACT | S-296, S-299, S-393 | "only support one connection at a time" | Med–High | — | Một connection owner; edge làm proxy đọc cho bên khác |
| EL-063 | Thanh ghi lấy từ diễn đàn (Huawei 47086…, Sungrow 13049–13051, Victron 2700) có mâu thuẫn và báo cáo "ghi không tác dụng" | FACT, Low ("cộng đồng báo cáo") | S-302, S-303, S-306, S-307, S-310 | "47086… 6 = Third-party Scheduling" | Low | 13050 vs 13051 | **Cấm** dùng làm map driver `VERIFIED_*`; cần tài liệu hãng hoặc thử lab |
| EL-064 | Đồng hồ thiết bị không đáng tin: SUN2000 lưu thời gian theo giờ địa phương; client pyhfs thấy timestamp API là UTC dù tài liệu ghi giờ nhà máy | FACT, Low–Med | S-304, S-184, S-398 | "Epoch seconds, local time" | Low–Med | SmartLogger dùng thanh ghi khác | `ts` = thời điểm edge thu (UTC); `ts_src` chỉ dùng khi `SYNCED` |
| EL-065 | MQTT 5 có Message Expiry Interval; broker bỏ tin quá hạn | FACT | S-260, S-261 | Như claim | High | — | `expires_at` của lệnh ánh xạ sang MQTT expiry; lệnh hết hạn không bao giờ gửi lại |
| EL-066 | Có gateway Sparkplug thương mại đặt cứng Will QoS 0, khiến NDEATH có thể mất | FACT | S-264, S-262 | "Will Message QoS cannot be configured to 1" | Med | — | Sparkplug chỉ là đầu ra phụ; hợp đồng chính `ems/v1/{edge_id}/…` |
| EL-067 | IEC 104: port 2404; tham số k/w/t1–t3 mặc định (k=12, w=8, t1=15 s) | FACT | S-268, S-269, S-270 | Bảng tham số | High | — | Mặc định cho slave 104 (P1 có điều kiện) |
| EL-068 | OCPP 2.1 phát hành 23/01/2025 (V2X, DER control, ISO 15118-20), tương thích logic 2.0.1 | FACT | S-273, S-274 | "application logic… remains compatible" | High | — | MVP/P1 dùng OCPP 1.6J; theo dõi 2.1 |
| EL-069 | OCPP 1.6J có security profile 1/2/3 (3 = TLS + client cert) | FACT | S-275 | Security whitepaper | Med–High | — | Yêu cầu profile ≥ 2 |
| EL-070 | Hành vi profile sạc khác theo hãng (Easee: TxDefault 0 A đè TxProfile) | FACT | S-276, S-277 | "a 0A default overrides a 20A TxProfile" | High | — | Hồ sơ charger theo hãng; test tương thích trước khi bật DLM |
| EL-071 | OpenADR 3.0 dùng REST/JSON, 3.1 thêm MQTT; 3.0 không thay 2.0b | FACT | S-280, S-281, S-282 | Slide Alliance | Med–High | — | Adapter DR là P2, "VPP-capable" |
| EL-072 | IEEE 2030.5 là mặc định Rule 21, TLS 1.2 + chứng chỉ | FACT | S-283, S-284 | Slide IEEE | Med | — | P2; không ở MVP |
| EL-073 | SMA Live API không được dùng cho giám sát liên tục | FACT | S-286, S-287 | "Not allowed for constant monitoring" | Med–High | — | Connector SMA chỉ đọc theo chu kỳ cho phép |
| EL-074 | Độ trễ zero-export = chu kỳ đo + truyền + phản ứng inverter + giảm công suất | FACT | S-312 | Phân rã độ trễ | Med | — | Ngân sách độ trễ và margin cho vòng edge |
| EL-075 | Trong một thiết kế ESS, BMS gửi tín hiệu bảo vệ tới PCS qua dây cứng, EMS qua TCP/RS485/CAN | FACT (một thiết kế) | S-259 | "hard-wired line for real-time response" | Med | — | Cloud và EMS không ở vòng bảo vệ; không API đổi tham số bảo vệ (C4) |
| EL-076 | BMS hạ CCL/DCL động theo SOC, nhiệt độ, điện áp cell; CCL có thể = 0 | FACT | S-258 | Manual Orion BMS | High | — | Limit chain đọc giới hạn động trước mọi setpoint |
| EL-077 | blue'Log XC và Solar-Log cần license cho Modbus power control; IEC 104/61850/DNP3 qua bộ chuyển đổi | FACT | S-313, S-314 | "Slave ID 1; Port 502" | Med–High | — | Chi phí license trong báo giá; mẫu "PPC + converter" |
| EL-078 | NTP đạt 1–100 ms; PTP µs cần hardware timestamping | FACT | S-315, S-316 | Như claim | Med | — | chrony/NTP đủ cho MVP |
| EL-079 | OpenEMS PR #3973 kẹp `SellToGridLimit` về 0 vì giá trị âm ghi vào thanh ghi unsigned | FACT | S-207, S-208 | "clamp to 0" | High | — | Kiểm tra kiểu/kẹp ở lớp ghi driver |

### 5.4 Miền năng lượng, KPI, dữ liệu

| # | Claim | Nhãn | S-IDs | Excerpt / diễn giải | Độ tin cậy | Bằng chứng mâu thuẫn | Hệ quả thiết kế |
|---|---|---|---|---|---|---|---|
| EL-080 | OBIS 1.8.0 = A+ (nhập), 2.8.0 = A− (xuất) | FACT | S-318, S-319 | Như claim | High | Một nguồn khác ghi nhãn lỗi | Lưu nhập/xuất tách, từ thanh ghi công tơ |
| EL-081 | Không có chuẩn cộng đồng thống nhất về dấu nhập/xuất; các client FusionSolar dùng ba quy ước | FACT | S-317, S-399 | Diễn đàn + đọc mã | Med | — | Driver khai báo dấu gốc; commissioning có bước kiểm tra dấu; UI hiện số không dấu + nhãn hướng |
| EL-082 | Bộ đếm năng lượng có rollover (ION 10.000.000); EnergyCAP chỉ coi là tràn khi giảm > 10% max | FACT | S-320, S-321 | Như claim | High | — | Driver khai báo `R_wrap`; máy trạng thái thay công tơ/reset |
| EL-083 | Ranh giới đo quyết định RTE: loại aux làm RTE tăng ~6–16%; các đặc tả tính aux khác nhau | FACT | S-322, S-324, S-217 | PNNL; RAE gồm aux; FENECON loại aux | Med–High | Có (theo ranh giới) | `rte_boundary` bắt buộc trên KPI RTE |
| EL-084 | Aux BESS ~30 kW trên hệ 1.000 kWh; cao nhất mùa hè | FACT | S-323 | Báo cáo MESA-1 | Med | — | `p_bess` âm nhẹ khi đứng yên không phải đang sạc; trạng thái lấy từ PCS/BMS |
| EL-085 | SOC của LFP khó ước lượng (OCV phẳng, coulomb counting trôi), sai số có thể > 15% | FACT (nguồn vendor có lợi ích) | S-327, S-328, S-329 | Như claim | Med | — | SOC là giá trị có bất định; guard dùng giới hạn BMS; lập lại kế hoạch khi SOC nhảy |
| EL-086 | PR = Yf/Yr, Yr = H_POA/1 kW/m² | FACT | S-337, S-338 | Như claim | High | — | PR là N/A nếu không có cảm biến bức xạ mặt phẳng tấm |
| EL-087 | Availability PV có khung IEC TS 63019:2019; 61724-3 là đánh giá điện năng | FACT | S-340 | Mô tả phạm vi webstore | Med | — | Availability định nghĩa riêng, không gọi là "theo 61724" |
| EL-088 | Self-consumption dựa trên sản lượng, self-sufficiency dựa trên tiêu thụ; công thức chi tiết khác nhau giữa nguồn | FACT | S-343, S-344, S-345 | Help center | Med | Có | Hai biến thể KPI có tên rõ; tính lại từ tử số/mẫu số |
| EL-089 | AC-coupled không cứu được năng lượng bị clip; DC-coupled thì được | FACT | S-335, S-336 | Như claim | Med | — | Topology site là thuộc tính của domain model |
| EL-090 | TimescaleDB: compression/CAGG thuộc Community (TSL); tự host miễn phí; cấm bán như DBaaS | FACT | S-348, S-349 | "cannot sell… as a service" | High | Việc SaaS của ta có thuộc diện cấm: UNKNOWN | Storage TimescaleDB có điều kiện: kiểm tra pháp lý TSL; không mở SQL trực tiếp cho khách |
| EL-091 | CAGG làm mới tăng dần; CAGG có thể nén columnstore | FACT | S-350, S-351 | "only the data that has changed needs to be computed" | High | — | CAGG 5 phút/1 h, refresh 7 ngày |
| EL-092 | Tỷ lệ nén TimescaleDB: "90%+" (mirror tài liệu) vs 10–20× (blog) | FACT (mâu thuẫn) | S-352, S-353 | Như claim | Low–Med | Có | Dung lượng phải đo bằng PoC 1.000 site |
| EL-093 | Solcast gói hobbyist: 30 phút, 10 lượt/ngày, ≤ 2 mảng | FACT | S-367 | Như claim | High | HA: tài khoản cũ 50 lượt (S-368) | Dự báo cần gói thương mại; ngân sách dự báo trong định giá |

### 5.5 Bảo mật, an toàn và chính sách nhà cung cấp

| # | Claim | Nhãn | S-IDs | Excerpt / diễn giải | Độ tin cậy | Bằng chứng mâu thuẫn | Hệ quả thiết kế |
|---|---|---|---|---|---|---|---|
| EL-094 | SmartLogger3000 kết nối outbound tới hệ quản lý bằng Encrypted Modbus TCP (cổng 27250), khuyến nghị TLS 1.2+; Modbus TCP thường tắt mặc định | FACT | S-168, S-169 | "TLS1.2 or a later version is recommended" | High | — | Edge chỉ kết nối outbound, MQTT 5 + mTLS |
| EL-095 | Forescout SUN:DOWN (27/03/2025): 46 lỗ hổng mới ở Sungrow, Growatt, SMA | FACT | S-374 | "46 new vulnerabilities" | Med–High | — | Connector cloud hãng chỉ đọc; pen-test; VDP |
| EL-096 | Lithuania (12/11/2024) cấm truy cập từ xa của công ty TQ tới hệ > 100 kW; không cấm lắp đặt | FACT | S-379, S-380 | Luật sửa đổi | High | Defense News mô tả rộng hơn | Khách phải tắt được kênh cloud hãng mà vẫn vận hành qua edge |
| EL-097 | Tin "thiết bị ẩn" trong inverter TQ (Reuters) chưa kiểm chứng; DOE (01/2026) không thấy bằng chứng chức năng độc hại | FACT (về đưa tin) | S-376, S-377 | "cannot verify"; "non-malicious" | Med | Hai nguồn trái chiều | Không quy kết hãng; giám sát egress OT |
| EL-098 | 11/2024 inverter bị vô hiệu hóa từ xa do tranh chấp thương mại (không nêu hãng) | FACT | S-378 | "commercial dispute" | Med | Gán hãng cụ thể chưa kiểm chứng | Kill switch nền tảng có kiểm soát; cam kết hợp đồng "không kill vì lý do thương mại" |
| EL-099 | Chứng nhận IEC 62443 của đối thủ là tuyên bố hoặc có hạn (WinCC OA tới 2026-02-06) | FACT | S-110, S-117, S-121 | "certified by a third party according to IEC 62443-3-3" | Med | Gia hạn chưa rõ | Không tuyên bố tuân thủ khi chưa có chứng chỉ; theo dõi hạn chứng chỉ |
| EL-100 | Huawei cho owner cấp/thu hồi "O&M Authorization" và quyền API bên thứ ba; inverter có phát hiện mất liên lạc mặc định 3 s | FACT | S-174, S-176, S-170 | Revoke tại Authorization Management | High / Med | Thời gian lan truyền thu hồi ~30 phút (cộng đồng) | Quyền installer có hạn do chủ tài sản cấp; fail-safe ở thiết bị, UI chỉ hiển thị |

**Claims dựa trên ảnh demo (bổ sung cho 09, không tính trong 100):** energy flow FusionSolar không có chữ nhập/xuất; nhãn "Công suất" đi với kWh; định dạng số/ngày lẫn lộn, có năm Phật lịch; trạng thái chỉ bằng chấm màu; hai nhãn mức 2 khác nhau ("Cao"/"Nặng") — tất cả `FACT, High` từ S-403 và S-396 (H ledger #1–#7). Hệ quả: nhãn hướng không dấu, lint nhãn–đơn vị, `Intl` format, trạng thái ≥ 2 kênh, enum mức cảnh báo duy nhất (Khẩn cấp / Cao / Trung bình / Thông tin).

---

## 6. Claims bị bác bỏ hoặc hạ cấp

Ánh xạ danh sách của [K §4](notes/K-review-round1.md) sang S-ID. Người viết tài liệu không được dùng lại claim ở nhãn cũ.

| Claim gốc | Nhãn mới | S-IDs liên quan | Ledger |
|---|---|---|---|
| "C&I VN hiện chưa trả phí công suất" | INFERENCE ("đại đa số"; khách thí điểm UNKNOWN) | S-014, S-024 | EL-017 |
| Thành phần công suất tính theo công suất đăng ký / theo Pmax đo | UNKNOWN (cơ sở); giữ FACT Med cho "chu kỳ 30 phút" | S-024, S-026, S-027 | EL-015, EL-016 |
| "Peak shaving có ở mọi sản phẩm" | INFERENCE (≥ 8/11) | xem EL-046 | EL-046 |
| "Điểm khác biệt thật nằm ở (a)–(d)" | INFERENCE | S-087, S-139, S-225 | — |
| Huawei peak shaving "chỉ" on/off-grid, tổng quát hóa | FACT chỉ trong phạm vi S-158 | S-158 | EL-026 |
| "Hãng thiết bị đều có EMS với thời gian đáp ứng xác định" | INFERENCE (chỉ Huawei có số) | S-153, S-154 | EL-025 |
| "Ở mọi sản phẩm, vòng nhanh nằm tại site" | INFERENCE | xem EL-047 | EL-047 |
| "Zero-export bắt buộc pháp lý với mọi site không bán dư" | FACT chỉ trung áp (theo tóm tắt); hạ áp UNKNOWN | S-001, S-046 | EL-007 |
| ≤ 2 s / ≤ 5 s "của SmartLogger5000B" | FACT tự công bố, model "SmartLogger5000B/SmartMGC5000B" | S-153, S-154, S-155 | EL-025 |
| Ampowr kích máy phát khi SOC thấp; "API respecting safety" (nguồn rfp.wiki) | Bác nguồn; giữ mức có S-084, S-089 | S-386, S-092 | §4.3 |
| Nội dung trang seed InfinitePower | FACT Low; chỉ định nghĩa chung, cần S-330 | S-095 | EL-038 |
| Schneider "lịch 15 phút trên horizon 72 h" | FACT Low–Med (một nguồn ~2017) | S-104, S-107 | EL-033 |
| "Modbus/IEC 104 tại site không có xác thực" | INFERENCE (kiến thức nền) tới khi có URL | — | — |
| ABB OPTIMAX "AI có mô tả cụ thể" | `V*` (tuyên bố hãng qua báo ngành) | S-130, S-131, S-132 | — |
| OpenEMS giấy phép "EPL-2.0" | UNKNOWN | S-204 | EL-050 |
| QĐ 1570 "≥ 64 kbps, ≤ 125 ms" như yêu cầu | FACT Low, không làm NFR | S-046 | EL-008 |
| "Phần lớn site C&I được bên thứ ba vận hành" | INFERENCE | — | — |
| Thanh ghi Modbus từ diễn đàn | FACT Low "cộng đồng báo cáo"; cấm dùng cho driver đã kiểm chứng | S-302…S-310 | EL-063 |

---

## 7. Hàng đợi kiểm chứng trước khi phát hành

Thứ tự theo mức chặn. "Chặn" = tài liệu/ADR không được phát hành bản chính thức khi mục chưa xong. Chi tiết quy trình ở [01 §9](01-research-methodology.md#9-cách-mở-rộng-và-kiểm-chứng-nghiên-cứu).

| # | Việc cần kiểm chứng | S-IDs hiện có | Cách kiểm chứng | Chặn |
|---|---|---|---|---|
| V-01 | Toàn văn VBHN 52 (NĐ 58 + NĐ 243) và TT 29/2026: ngưỡng đăng ký, thiết bị chống phát ngược theo cấp điện áp, mẫu số trần 50%, cách tính BESS | S-001, S-006, S-007, S-010 | Đọc văn bản gốc; xác nhận với luật sư năng lượng | 00, 02, 04, 10 |
| V-02 | QĐ 963: ngày áp vào hóa đơn; xử lý ngày lễ | S-016, S-017, S-018, S-019 | Văn bản gốc + hóa đơn EVN thật của khách | 04, M-TAR |
| V-03 | Giá hai thành phần: cơ sở tính, block/rolling, đối tượng, lộ trình | S-024…S-029 | Văn bản BCT/EVN; hóa đơn thí điểm | 04, 08 |
| V-04 | QĐ 1570/QĐ-EVN toàn văn | S-046, S-047 | Văn bản gốc từ EVN/PC | 07 (IEC 104) |
| V-05 | TT 05/2025 Điều 31 (cosφ, đối tượng) | S-042, S-043 | Văn bản gốc | 04 (KPI PF) |
| V-06 | Khung luật an ninh mạng/dữ liệu VN hiện hành (Luật ANM, NĐ 53/2022, NĐ 13/2023, Luật BVDLCN 2025, thay đổi 2025–2026) | — (chưa có URL) | Tìm văn bản gốc; tư vấn pháp lý | 10 |
| V-07 | Giấy phép TimescaleDB TSL với mô hình SaaS của ta | S-348, S-349 | Pháp chế đọc TSL | ADR lưu trữ |
| V-08 | Giấy phép OpenEMS từng module (Edge/Backend/UI) | S-204 | Đọc LICENSE từng thư mục | ADR edge runtime |
| V-09 | Model và câu chữ ≤ 2 s/≤ 5 s của Huawei | S-153, S-154 | Datasheet chính thức hoặc đối tác Huawei | Dùng số trong 06/10 |
| V-10 | Register map chính thức Huawei/Sungrow/Victron/tủ BESS Trung Quốc | S-185, S-302…S-310 | Tài liệu hãng + thử lab | Driver `VERIFIED_*` |
| V-11 | Edition tiêu chuẩn: IEC 62443, IEC 61724-1, IEC TS 63019, IEC 62898-2, IEEE 2030.7, ISA-101/18.2 | S-062, S-339, S-340, S-115, S-078 | Webstore IEC/IEEE/ISA | Mọi câu nhắc tiêu chuẩn |
| V-12 | Giấy phép solver (HiGHS, CBC, OR-Tools, Timefold, SCIP) và tên controller OpenEMS | — (kiến thức nền) | Repo/LICENSE chính thức | ADR-OPT (tầng 3, P1) |
| V-13 | Trang seed InfinitePower (S-095) và các URL gắn cờ §4.1 | S-095, S-310, S-335 | Mở trang khi có mạng | Không chặn (đã hạ nhãn) |
| V-14 | Chưa URL nào được spot-check bởi reviewer, kể cả vòng review cuối (hết hạn mức WebSearch); mọi FACT giữ trần độ tin cậy snippet. Cần một lượt có mạng mở trực tiếp tối thiểu các nguồn của ô Verified trong ma trận 02 §7 (qua bảng §3.1), các nguồn EL gắn FACT và §4.1 | Toàn bộ S-001…S-387 (ưu tiên nguồn trong §3.1 và §5) | Mở trang, đối chiếu claim, ghi ngày đọc, nâng/hạ độ tin cậy theo §8 mục 3 | **Mọi phát hành ra bên ngoài của 02**; tuyên bố đối thủ trong 00 |

---

## 8. Quy tắc dùng và mở rộng sổ

1. **Trích dẫn.** Deliverable trích `S-xxx`; có thể giữ URL đầy đủ bên cạnh. Ghi chú trong `notes/` tiếp tục dùng URL đầy đủ; Registrar cấp mã khi tổng hợp.
2. **Thêm nguồn.** Cấp mã tiếp theo (S-404…). Không đánh số lại mã cũ. Ghi rõ cách tiếp cận: `Snippet tìm kiếm`, `Tệp nghiên cứu trước`, `Fetch (ngày)`, `Tài liệu khách cung cấp`, `Phỏng vấn (mã PV-xx)`, `Thử lab (mã LAB-xx)`.
3. **Nâng độ tin cậy.** Một nguồn chỉ được nâng lên mức cao hơn khi (a) đã đọc toàn văn và ghi ngày đọc, hoặc (b) có nguồn độc lập thứ hai. Ghi lịch sử thay đổi ở cột "Claim chính".
4. **Nguồn bị loại.** Giữ mã, chuyển sang nhóm K, ghi lý do. Không xóa.
5. **Nguồn vendor.** Mọi tuyên bố hiệu năng, chứng nhận, "AI", % tiết kiệm của hãng ghi là "tuyên bố hãng". "Không có tài liệu" ≠ "không hỗ trợ".
6. **Diễn đàn và mã cộng đồng.** Được dùng để định hướng câu hỏi và test case; không được làm cơ sở cho driver đã kiểm chứng hoặc yêu cầu bắt buộc.
7. **Văn bản pháp luật.** Cổng tra cứu (thuvienphapluat, luatvietnam) là bản trình bày của bên thứ ba; khi có thể, đối chiếu với Công báo hoặc cổng chính phủ.

---

## 9. Vấn đề gửi agent khác

- **Người viết 07 / ghi chú E:** URL NRECA (S-252) bị cắt trước `).pdf` ở một số chỗ do dấu ngoặc trong URL; nên bọc URL trong `<…>`. URL Victron S-310 chứa ký tự "﹖" mã hóa, nên đối chiếu lại.
- **Người viết 02:** bảng FS-01…FS-14 dùng nguồn từ S-402 (competitors_rebuild); có thể bổ sung S-ID tương ứng (S-058, S-059, S-060, S-061, S-192, S-229, S-231, S-232, S-233, S-234, S-152).
- **Người viết 06:** chuỗi `https://enroll` trong API-INT-02 dễ bị công cụ quét hiểu nhầm là URL nguồn; đề xuất viết dạng đường dẫn tương đối `/v1/edge/enroll`.
- **Người viết 12 (truy vết):** dùng EL-xxx của §5 làm cột "bằng chứng" cho FR/NFR; các yêu cầu dựa trên EL có nhãn UNKNOWN (EL-010, EL-016, EL-050) phải gắn cờ "chờ V-xx".
- **Người viết 13:** V-01…V-13 nên có R-/Q- tương ứng nếu chưa có.
- **Orchestrator:** cần một lượt có mạng/hạn mức tìm kiếm mới để chạy §7 (đặc biệt V-14) và spot-check §4.1. K vòng 1 và vòng review cuối đều không spot-check được URL nào; sổ này không thể tự nâng độ tin cậy.
- **Người viết 02:** §13.2 dùng mã tạm L01…L49, L37b, FS-01…FS-15; bảng quy đổi sang S-ID nằm ở §3.1 của sổ này. Có thể thêm cột S-ID vào §13.2. Tài liệu không được phát hành ra bên ngoài khi V-14 chưa xong.
- **Người viết 03:** cột "Bằng chứng · đối thủ" dùng `B·Lnn`; tra §3.1 để ra S-ID.
