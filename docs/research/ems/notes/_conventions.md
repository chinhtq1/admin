# Quy ước viết tài liệu nghiên cứu EMS

Áp dụng cho mọi agent viết file trong `docs/research/ems/`.

## Ngôn ngữ
- Viết bằng **tiếng Việt**, giữ nguyên thuật ngữ kỹ thuật tiếng Anh khi đó là thuật ngữ chuẩn của ngành (SOC, SOH, PCS, BMS, peak shaving, setpoint, Modbus...). Lần đầu xuất hiện thì giải thích ngắn bằng tiếng Việt.
- Câu ngắn, cụ thể. Không viết lời quảng cáo, không đưa số liệu thống kê nếu không có nguồn.

## Nhãn bằng chứng (bắt buộc cho mọi nhận định quan trọng)
- `FACT`: có nguồn đáng tin hỗ trợ trực tiếp. Phải kèm URL hoặc mã nguồn `S-xxx` trong `14-source-register.md`.
- `INFERENCE`: kết luận suy ra từ bằng chứng; nêu bằng chứng gốc.
- `PROPOSAL`: đề xuất cho sản phẩm của chúng ta.
- `UNKNOWN`: chưa đủ bằng chứng.
- Trong Markdown viết dạng `[FACT]`, `[INFERENCE]`, `[PROPOSAL]`, `[UNKNOWN]`.
- Trong HTML dùng `<span class="tag fact">FACT</span>`, `tag inference`, `tag proposal`, `tag unknown`.
- Trạng thái trong ma trận đối thủ: `<span class="st verified">Verified</span>`, `st partial`, `st unknown`, `st na` (Not applicable).
- Mức ưu tiên: `<span class="prio p0">P0</span>`, `p1`, `p2`.
- **Không bao giờ** gán cho một hãng tính năng không có tài liệu nói rõ. "Không có tài liệu" ≠ "không hỗ trợ".
- **Không bịa URL.** Chỉ trích những URL đã thực sự mở được hoặc đã thấy trong kết quả tìm kiếm. Nếu chỉ thấy qua snippet tìm kiếm thì ghi rõ "(snippet tìm kiếm)".
- Tiêu chuẩn (IEC/IEEE/ISO/UL…): ghi số hiệu và edition nếu đã kiểm chứng; nếu chưa thì ghi `UNKNOWN` cho edition và không tuyên bố tuân thủ.

## Mã định danh dùng chung (tránh trùng)
- Nguồn: `S-001`… (sổ đăng ký nguồn duy nhất ở `14-source-register.md`; trong ghi chú của từng agent dùng URL đầy đủ, tổng hợp sẽ cấp mã sau).
- Module: `M-ORG, M-DASH, M-MON, M-HIST, M-BESS, M-PV, M-GRID, M-EV, M-OPT, M-ALM, M-INT, M-SEC, M-ADV` (khớp các nhóm A–M trong đề bài) và `M-REP` (báo cáo), `M-TAR` (biểu giá).
- Yêu cầu chức năng: `FR-<MODULE>-NNN` ví dụ `FR-BESS-012`. Phi chức năng: `NFR-<NHÓM>-NNN` (SEC, REL, PERF, DATA, OBS).
- Quyết định kiến trúc: `ADR-NN`. Rủi ro: `R-NN`. Câu hỏi mở: `Q-NN`. Trang UI: `UI-NN`. API: `API-<nhóm>-NN`. Test: `T-<FR id>`.

## Bối cảnh dự án đã có
- Dự án đã nghiên cứu Huawei FusionSolar trước đó: `docs/research/fusionsolar/` (báo cáo, wireframe 15 màn hình, ghi chú API/data model/kiến trúc, ảnh demo). Hướng đề xuất trước đó: nền tảng giám sát/O&M PV đa hãng, edge-first, thị trường Việt Nam (installer/O&M C&I), team Java/Spring Boot + Angular, TimescaleDB/PostgreSQL, MQTT, edge kiểu OpenEMS. **Cập nhật 2026-10-10:** product owner chốt Spring Boot (backend) + React (frontend) cho EMS; "Angular" ở trên chỉ là bối cảnh lịch sử ([06 ADR-20](../06-system-architecture.html#adr-20)).
- Nghiên cứu EMS mới **mở rộng** hướng đó sang BESS/EMS, không mâu thuẫn mà không giải thích. Nếu đề xuất khác hướng cũ thì ghi rõ lý do.

## HTML
- Mọi file HTML dùng stylesheet chung: `<link rel="stylesheet" href="assets/ems-docs.css">` (đường dẫn tương đối từ `docs/research/ems/`). Không thêm CSS framework, không gọi CDN, không dùng font ngoài. CSS riêng trong `<style>` chỉ khi thật cần và ngắn.
- Sơ đồ: **SVG inline** dùng các class `box`, `box alt`, `box ot`, `box ext`, `zone`, `edge`, `edge ctl`, `edge dash`, `text.small`, `text.title` (đã định nghĩa trong CSS, tự đổi màu theo dark mode). Có `<title>` trong SVG, có `viewBox`, không đặt width cố định quá 1100. Không dùng JS để vẽ.
- Bảng rộng bọc trong `<div class="table-wrap">`.
- Đầu trang: `<!doctype html>`, `<html lang="vi">`, meta charset utf-8, meta viewport, `<title>` 2–5 từ.
- Ngay sau `<body>` chèn khối điều hướng dưới đây, đặt `aria-current="page"` cho link của trang hiện tại:

```html
<nav class="docnav"><div class="inner">
  <a class="brand" href="index.html">EMS Research</a>
  <a href="00-executive-summary.html">00 Tóm tắt</a>
  <a href="01-research-methodology.md">01 Phương pháp</a>
  <a href="02-market-and-competitor-analysis.html">02 Thị trường</a>
  <a href="03-functional-catalog.html">03 Chức năng</a>
  <a href="04-business-requirements.md">04 Yêu cầu</a>
  <a href="05-domain-model.html">05 Domain</a>
  <a href="06-system-architecture.html">06 Kiến trúc</a>
  <a href="07-device-integration.md">07 Tích hợp</a>
  <a href="08-energy-optimization.md">08 Tối ưu</a>
  <a href="09-ux-ui-specification.html">09 UX/UI</a>
  <a href="10-security-and-reliability.md">10 An toàn</a>
  <a href="11-mvp-and-roadmap.html">11 Lộ trình</a>
  <a href="12-traceability-matrix.md">12 Truy vết</a>
  <a href="13-open-questions-and-risks.md">13 Rủi ro</a>
  <a href="14-source-register.md">14 Nguồn</a>
  <a href="15-simulators-and-messaging.md">15 Mô phỏng</a>
</div></nav>
```

- Sau đó: `<main>` với `<header class="doc-header">` (kicker, h1, meta: phiên bản, ngày 2026-10-10, trạng thái), tài liệu dài dùng `<div class="layout-toc"><nav class="toc">…</nav><article>…</article></div>`. Cuối trang `<footer class="docfoot">`.
- Dữ liệu mẫu trong wireframe phải gắn nhãn `<span class="sample">Dữ liệu mẫu</span>`.

## Markdown
- Dòng đầu là tiêu đề H1, ngay sau là dòng điều hướng: `[← Mục lục](index.html) · [00 Tóm tắt](00-executive-summary.html) · …` (rút gọn, chỉ các tài liệu liên quan). Từ vòng nhất quán 2026-10-10, dòng điều hướng của mọi file Markdown kết thúc bằng `[15 Mô phỏng](15-simulators-and-messaging.md)` (trong `notes/` dùng `../`).
- Liên kết chéo bằng đường dẫn tương đối tới file và anchor khi cần.

## Quyền sở hữu file
- Mỗi deliverable chỉ có **một** agent ghi tại một thời điểm. Ghi chú nghiên cứu của agent nằm ở `notes/<agent>-<chủ-đề>.md`, chỉ agent đó ghi.
- Không sửa file của agent khác; nếu thấy lỗi thì ghi vào phần "Vấn đề gửi agent khác" trong file của mình.
