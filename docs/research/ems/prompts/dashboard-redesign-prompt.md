# Prompt thiết kế lại dashboard EMS

[← Mục lục](../index.html) · [09 UX/UI](../09-ux-ui-specification.html) · [Wireframe](../wireframes/index.html)

Dán toàn bộ khối dưới đây vào công cụ AI thiết kế (Claude, v0, Lovable, Figma Make…). Nếu công cụ cho đính kèm file, đính kèm thêm ảnh `wireframes/screenshots/UI-01-portfolio-overview-desktop.jpg` và `UI-03-site-dashboard-desktop.jpg` làm tham chiếu bố cục (nói rõ: tham chiếu nội dung, không sao chép giao diện).

---

```text
VAI TRÒ
Bạn là senior product designer chuyên giao diện vận hành công nghiệp (SCADA/HMI, NOC, fintech dashboard). Hãy thiết kế lại 2 màn hình dashboard cho một nền tảng EMS (Energy Management System) đa site cho doanh nghiệp C&I tại Việt Nam: (1) Tổng quan danh mục nhiều site, (2) Dashboard năng lượng của một site. Mục tiêu là giao diện chuyên nghiệp, dày thông tin nhưng dễ đọc, đạt chuẩn để dev dựng thật — không phải ảnh marketing.

BỐI CẢNH SẢN PHẨM
- Mỗi site có: điện mặt trời (PV, nhiều inverter), pin lưu trữ BESS (tùy chọn), công tơ tại điểm đấu nối lưới (POC), phụ tải nhà máy, trụ sạc xe điện EV (tùy chọn).
- Người dùng chính: operator đơn vị O&M theo dõi 40–300 site (màn 1), kỹ sư năng lượng/quản lý site (màn 2). Phụ: chủ doanh nghiệp xem chi phí.
- Câu hỏi màn 1 phải trả lời trong ≤ 10 giây: "Site nào cần chú ý ngay, vì sao?"
- Câu hỏi màn 2: "Site đang làm gì, có đúng kế hoạch và an toàn không?"
- Ngôn ngữ giao diện: tiếng Việt. Số theo định dạng Việt Nam (1.377,5 kWh; 1,90 triệu ₫). Múi giờ Asia/Ho_Chi_Minh.

NGUYÊN TẮC BẮT BUỘC (không được vi phạm)
1. Nhận thức tình huống trước, số liệu sau: khối "Cần chú ý" có thứ tự ưu tiên và lý do bằng chữ đứng trên cùng; không dùng donut/gauge trang trí.
2. Nền trung tính; màu bão hòa CHỈ cho bất thường (cảnh báo, vượt giới hạn). Một site bình thường không có vùng màu cảnh báo nào.
3. Mọi trạng thái mã hóa bằng 2 kênh: màu + icon/hình dạng + chữ. Phải đọc được khi in đen trắng và với người mù màu đỏ–lục.
4. Số công suất không bao giờ có dấu âm: hiển thị "Nhập 120 kW", "Xuất 35 kW", "Sạc 116 kW", "Xả 68 kW", "Chờ".
5. Công suất (kW) khác điện năng (kWh). kWh luôn kèm khoảng thời gian ("hôm nay").
6. Trung thực về độ tươi dữ liệu: mọi giá trị realtime có "đo lúc HH:MM:SS"; dữ liệu cũ hiển thị chữ xám nghiêng + chip "dữ liệu cũ 18 phút"; mất kết nối ghi "từ HH:MM"; KHÔNG BAO GIỜ hiện 0 cho giá trị không biết (dùng "—" hoặc "N/A" kèm lý do).
7. Giá trị ước tính có nhãn "≈ ước tính" (phân bổ luồng năng lượng, chi phí, tiết kiệm). Không dùng chữ "AI", "thông minh".
8. Dashboard KHÔNG có nút điều khiển thiết bị. Chỉ có nút "Điều khiển →" dẫn sang trang khác (chỉ hiện khi có quyền).
9. Mọi số liệu phải truy được nguồn: mỗi KPI có tooltip ghi công thức và nguồn (ví dụ "Δ công tơ POC, nhập").
10. Không gradient, không icon cỡ lớn, không glassmorphism, không 3D. Ưu tiên bảng, thanh giới hạn, biểu đồ đường/vùng rõ trục.

MÀN 1 — TỔNG QUAN DANH MỤC (desktop 1440 px)
- Top bar: tổ chức "O&M Sao Mai" ▸ "Tất cả site"; ô tìm kiếm (Ctrl+K); bộ đếm cảnh báo theo mức (Khẩn cấp 1, Cao 2, Trung bình 6); "Chờ duyệt 1"; thông báo; người dùng "Lan (Operator)".
- Nav trái thu gọn được: Tổng quan, Cảnh báo, Ticket, Duyệt lệnh, Nhật ký lệnh, Báo cáo, Cấu hình, Quản trị.
- Hàng KPI hôm nay (4–6 thẻ): Nhập lưới 18,42 MWh (gồm dữ liệu cũ của 3 site), PV 31,06 MWh, Xuất lưới 0,84 MWh (6 site được bán dư), Chi phí điện ≈ 41,2 triệu ₫ (ước tính), Site mất kết nối/dữ liệu cũ.
- Khối "Cần chú ý (4)", mỗi dòng: mức, mã + tên site, lý do bằng chữ, thời lượng, nút "Xác nhận"/"Mở":
  • Khẩn cấp · LA-03 Nhà máy dệt · BMS báo nhiệt độ cell vượt ngưỡng bảo vệ (rack 2) · chưa xác nhận · 3 phút · BESS đã về P = 0 tại edge
  • Cao · BD-05 Kho bao bì · Vượt giới hạn xuất 1 lần (6 s, đỉnh 14,2 kW) và INV-02 mất kết nối từ 10:02
  • Mất kết nối · DN-07 Kho lạnh · Cloud hãng chưa trả dữ liệu từ 09:41 (39 phút) · site chỉ giám sát
  • Dự phòng · TN-01 Xưởng gỗ · Edge mất cloud từ 08:15 · đang chạy kế hoạch #87 tới 23:45
  Khi 40 site mất kết nối cùng lúc vì một nguyên nhân → gộp thành 1 dòng.
- Bảng site (42), cột: Trạng thái (icon+chữ) | Site | Đo lúc | Lưới (Nhập/Xuất kW) | Nhập/trần (thanh mini, vd 310/800 kW) | PV (kW · % công suất lắp) | BESS (chế độ · SOC · Sạc/Xả kW) | EV kW | Cảnh báo (Khẩn cấp·Cao·TB·Thông tin) | Kế hoạch (Đúng/Lệch/Không đồng bộ). Cột Trạng thái và Site cố định khi cuộn ngang. Bộ lọc: tỉnh/KCN, có BESS/có EV/chỉ PV, trạng thái, gói Giám sát/Điều khiển.
  Dòng mẫu:
  • Khẩn cấp | LA-03 Nhà máy dệt | 10:20:12 | Nhập 310 kW | 310/800 | 520 kW · 65% | Chờ · 62% · về an toàn | — | 1·0·2·0 | Lệch: an toàn
  • Bình thường | BD-02 Xưởng ép nhựa | 10:20:15 | Nhập 4 kW | 4/900 | 640 kW · 80% | Lịch TOU · 46% · Sạc 116 kW | 40 kW | 0·0·1·0 | Đúng
  • Mất kết nối | DN-07 Kho lạnh | 09:40 (40 phút trước) | Nhập 85 kW | — | 212 kW · 53% | — | — | 0·1·0·0 | —
  • Dự phòng | TN-01 Xưởng gỗ | 08:14 (2 giờ trước) | Nhập 140 kW | 140/600 | 180 kW | Kế hoạch #87 · 71% | — | 0·1·0·0 | Không đồng bộ

MÀN 2 — DASHBOARD SITE BD-02 Xưởng ép nhựa (desktop 1440 px)
- Header ngữ cảnh (luôn hiện, 7 trường): trạng thái "Bình thường"; Chiến lược "Lịch TOU"; Đang áp dụng "Mức 11 · Lịch kinh tế · Sạc PV dư" (tooltip lý do); Edge "Trực tuyến · NORMAL"; Đo lúc 10:20:15; Khung giá "Bình thường đến 17:30"; REMOTE; Gate M2; Kill switch: Không; Giờ site UTC+7. Chip "Dữ liệu đầy đủ đến 10:15". Nút "Điều khiển →".
- Sơ đồ dòng năng lượng (kW, nút + cạnh có hướng, nhãn chữ): PV 640 kW → Tải nhà máy 488 kW; PV → BESS 112 kW; PV → EV 40 kW; Lưới → BESS 4 kW. Lưới: Nhập 4 kW. BESS: Sạc 116 kW, SOC 46%. EV 2 trụ: 40 kW. Ghi "≈ phân bổ ước tính". Công tắc "Hiện tại (kW) / Hôm nay (kWh)".
- Thanh giới hạn lưới: Nhập 4 / trần 900 kW; Xuất 0 kW · chế độ "Không xuất (zero-export)".
- KPI hôm nay (00:00–10:20): Nhập lưới 1.377,5 kWh; Xuất 0,0 kWh; PV 1.544,4 kWh; BESS Sạc 122,3 kWh / Xả 0,0 kWh; Tiêu thụ 2.799,5 kWh; Tự cấp 50,8 %; Chi phí ≈ 1,90 triệu ₫ (tooltip: 972,2 kWh × 1.190 ₫ + 405,3 kWh × 1.833 ₫, biểu giá 2026-05); Vi phạm xuất hôm nay: 0 lần.
  Kiểm tra cân bằng (phải khớp): 1.377,5 − 0,0 + 1.544,4 + 0,0 − 122,3 = 2.799,5 kWh.
- Biểu đồ "Hôm nay: thực tế và kế hoạch" 00:00–24:00:
  • Panel trên (kW): Lưới (nhập trên trục 0, xuất dưới), PV, BESS (xả trên, sạc dưới); đường đỏ đứt "Trần nhập 900 kW"; dải nền khung giá: Thấp điểm 00:00–06:00, Bình thường, Cao điểm 17:30–22:30; vạch dọc "Bây giờ 10:20"; phần sau 10:20 là kế hoạch nét đứt.
  • Panel dưới (SOC %, cùng trục thời gian, KHÔNG dùng trục kép): đường SOC; vạch Max 95 %, Dự phòng 20 %.
  • Chú thích kế hoạch: 09:20–12:20 Sạc PV dư tới 95 %; 12:20–17:30 Giữ (≈ 198 kWh PV bị cắt dự kiến); 17:30–22:30 Xả cao điểm ≈ 68 kW về SOC 20 %.
- Thẻ "Kế hoạch: slot hiện tại và kế tiếp" + link "Mở kế hoạch 48 h".
- Cảnh báo đang mở (1): Trung bình · INV-03 string 2.4 dòng thấp hơn trung vị 38 % từ 09:05 · đã xác nhận (Lan 09:12) · ticket T-0412.
- Thẻ tài sản: BESS 250 kW / 500 kWh · PV 7 inverter (800 kWp) · Lưới MTR_POC · EV 2 trụ (chỉ công tơ) — mỗi thẻ dẫn sang trang chi tiết.

TRẠNG THÁI PHẢI THIẾT KẾ (vẽ thành các biến thể nhỏ bên dưới mỗi màn)
- Đang tải (skeleton, header hiện trước).
- Rỗng (chưa có site; site đang commissioning; chưa gán biểu giá → chi phí "N/A — chưa gán biểu giá").
- Dữ liệu cũ (header "dữ liệu cũ 18 phút", sơ đồ năng lượng dừng hoạt ảnh, cạnh nét đứt).
- Mất kết nối (banner "Mất kết nối cloud từ 13:40 — site vẫn điều khiển cục bộ theo kế hoạch tới 05:30", giá trị cuối cùng xám).
- Edge chạy chiến lược mặc định ("Edge chạy chiến lược mặc định từ 06:12").
- Lỗi một widget (không làm hỏng phần còn lại; nút Thử lại; mã trace).
- Không đủ quyền (ẩn chi phí khi chủ site tắt hiển thị chi phí).

RESPONSIVE
- ≥1280: như mô tả. Màn 2: hàng 1 header; hàng 2 trái 5 cột sơ đồ năng lượng + thanh giới hạn, phải 7 cột KPI + thẻ kế hoạch; hàng 3 biểu đồ toàn ngang; hàng 4 cảnh báo | tài sản.
- Tablet (768–1279): 2 cột; bảng site còn 7 cột ưu tiên.
- Mobile (390 px): "Cần chú ý" lên đầu; bảng site thành thẻ; màn 2 thứ tự: header rút gọn → sơ đồ năng lượng → giới hạn → KPI dạng danh sách → biểu đồ chỉ xem. Không cuộn ngang trang.
- Có dark mode đầy đủ (không chỉ đảo màu). In được (A4 ngang).

HỆ THIẾT KẾ
- Font: Inter hoặc system-ui; số dùng tabular-nums. Cỡ chữ cơ bản 14 px, bảng 13 px.
- Màu: nền xám rất nhạt / trắng; 1 màu nhấn xanh dương trầm; trạng thái: Khẩn cấp đỏ, Cao cam, Trung bình tím/vàng đậm, Thông tin xám xanh, Bình thường dùng xám trung tính + icon ✓ viền (không tô xanh lá).
- Màu chuỗi biểu đồ cố định toàn sản phẩm: Lưới, PV, BESS, Tải, EV — 5 màu phân biệt được với người mù màu, giữ nguyên ở light/dark.
- Lưới 12 cột, khoảng cách 8 px; bo góc 6 px; viền 1 px thay cho đổ bóng.
- Đạt WCAG 2.2 AA về tương phản; focus ring rõ; bàn phím điều hướng được bảng.

ĐẦU RA MONG MUỐN
1. Bản thiết kế độ trung thực cao cho 2 màn (desktop light), kèm biến thể dark, tablet và mobile.
2. Bảng các trạng thái (loading/empty/stale/offline/error/permission) cho từng khối.
3. Danh sách component dùng lại: KPI tile (có chip độ tươi + tooltip công thức), thanh giới hạn, chip trạng thái, mini SOC, sơ đồ dòng năng lượng, biểu đồ thời gian có dải TOU và vùng kế hoạch, bảng site, dòng "Cần chú ý", header ngữ cảnh site.
4. Design tokens (màu, chữ, khoảng cách) dạng bảng hoặc CSS variables.
5. Nếu xuất code: một file HTML/CSS tĩnh (hoặc React + Tailwind nếu công cụ bắt buộc), không dùng thư viện biểu đồ nặng — vẽ biểu đồ bằng SVG. Toàn bộ dữ liệu là DỮ LIỆU MẪU, gắn nhãn "Dữ liệu mẫu" ở góc mỗi màn.

KHÔNG ĐƯỢC
- Không dùng logo, màu thương hiệu hay bố cục sao chép từ Huawei FusionSolar, SolarEdge, Tesla hay hãng nào khác.
- Không thêm KPI không có trong mô tả (ví dụ CO₂, ROI) nếu không ghi rõ "đề xuất".
- Không đặt nút điều khiển (bật/tắt, đặt công suất) trên hai màn này.
- Không bịa thêm số liệu làm lệch cân bằng năng lượng ở trên.
```

---

## Gợi ý dùng

- **Muốn từng vòng nhỏ:** chạy riêng màn 1 hoặc màn 2 bằng cách xóa phần màn còn lại trong prompt.
- **Muốn bám code Angular của team:** thay mục 5 "Đầu ra" bằng "Xuất component Angular standalone + SCSS, dùng CSS variables cho tokens, biểu đồ bằng SVG thuần".
- **Khi review kết quả của AI**, kiểm nhanh theo 10 nguyên tắc bắt buộc, đặc biệt: số không có dấu âm, có "đo lúc", không hiện 0 cho dữ liệu thiếu, cân bằng năng lượng khớp, site bình thường không có màu cảnh báo.
- Nguồn đặc tả đầy đủ: [09 §7 UI-01 và UI-03](../09-ux-ui-specification.html), nguyên tắc UX ở 09 §4, wireframe tại [wireframes/](../wireframes/index.html).
