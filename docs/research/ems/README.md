# Nghiên cứu sản phẩm EMS (Energy Management System) C&I

[← Mục lục](index.html) · [00 Tóm tắt](00-executive-summary.html) · [01 Phương pháp](01-research-methodology.md) · [14 Nguồn](14-source-register.md) · [15 Mô phỏng](15-simulators-and-messaging.md)

Bộ tài liệu nghiên cứu và đặc tả cho một EMS behind-the-meter, đa site, đa hãng (PV, BESS, lưới, phụ tải, EV tùy chọn) cho thị trường Việt Nam. Ngày 2026-10-10, bản nội bộ v1.0. Không chứa mã ứng dụng.

## Cách mở

- Bắt đầu từ [`index.html`](index.html) (mục lục, thứ tự đọc theo vai trò, chú giải nhãn) hoặc [`00-executive-summary.html`](00-executive-summary.html).
- File `.html` mở trực tiếp bằng trình duyệt, không cần mạng. Tất cả dùng chung `assets/ems-docs.css` (có dark mode và bản in).
- File `.md` đọc trên GitHub/GitLab hoặc trình xem Markdown. Liên kết chéo giữa các file là đường dẫn tương đối.

## Cấu trúc

| Đường dẫn | Nội dung |
|---|---|
| `00`…`15` | Deliverable đánh số: tóm tắt, phương pháp, thị trường, chức năng, yêu cầu, domain, kiến trúc, tích hợp, tối ưu, UX/UI, an toàn, lộ trình, truy vết, rủi ro, sổ nguồn, mô phỏng/messaging |
| `assets/` | Stylesheet chung |
| `notes/` | Ghi chú nghiên cứu thô của từng agent (`A`…`I`, `E2`), phán quyết của Evidence Judge (`K-review-round1.md`), quy ước viết (`_conventions.md`) và khoảng trống catalog (`_catalog-gaps.md`) |
| `wireframes/` | Để trống; wireframe nằm trong `09-ux-ui-specification.html` |

## Thư mục `notes/`

- Đây là đầu vào, không phải tài liệu chính thức. Mã FR/NFR/R/Q trong `notes/` là **tạm thời**. Mã chính thức do 04, 06, 09 và 13 cấp, kèm bảng ánh xạ ngược.
- `K-review-round1.md` **ràng buộc** mọi deliverable. Khi ghi chú mâu thuẫn với "quyết định thống nhất" (K §6), K thắng.
- `_conventions.md`: ngôn ngữ (tiếng Việt + thuật ngữ kỹ thuật tiếng Anh), nhãn `FACT`/`INFERENCE`/`PROPOSAL`/`UNKNOWN`, mã định danh, quy ước HTML/Markdown, quyền sở hữu file.

## Quan hệ với `docs/research/fusionsolar`

- [`../fusionsolar/`](../fusionsolar/README.md) là nghiên cứu reverse-engineering Huawei FusionSolar trước đó (07/10/2026): báo cáo, wireframe 15 màn hình, ghi chú API/data model, ảnh demo. Hướng khi đó là nền tảng giám sát/O&M PV đa hãng, edge-first; Java/Spring Boot + Angular; TimescaleDB/PostgreSQL; MQTT. EMS giữ backend Spring Boot nhưng frontend đổi sang React + TypeScript theo quyết định product owner ngày 2026-10-10 ([06 ADR-20](06-system-architecture.html#adr-20)).
- Nghiên cứu EMS **mở rộng** hướng đó sang BESS, lưới, phụ tải và EV có điều khiển an toàn. Các điểm đổi hướng có lý do được ghi ở [00 §2.3](00-executive-summary.html#s2), [01 §1.3](01-research-methodology.md#13-kế-thừa-và-khác-biệt-so-với-hướng-cũ) và [06 §19](06-system-architecture.html#s19). Ví dụ: quy ước dấu lưới đổi sang + = nhập; dữ liệu edge 1 s; edge bắt buộc ở site có lệnh.
- Các tệp FusionSolar được trích như nguồn S-388…S-403 trong [14 §3](14-source-register.md).

## Giới hạn cần biết

- Bằng chứng mới chỉ lấy qua **snippet tìm kiếm**. Không trang nào được mở trực tiếp, chưa đọc toàn văn văn bản pháp luật hay tiêu chuẩn nào, chưa URL nào được reviewer spot-check, và chưa phỏng vấn khách hàng thật.
- **Không phát hành ra ngoài đội** trước khi xong hàng đợi kiểm chứng V-01…V-14 ([14 §7](14-source-register.md)) và các điều kiện ở [13 §8](13-open-questions-and-risks.md).
