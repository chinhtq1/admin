# Bộ tư liệu nghiên cứu Huawei FusionSolar (07/10/2026)

Gói này giữ lại toàn bộ kết quả nghiên cứu để dùng khi triển khai sau này.

## Cấu trúc

| Thư mục | Nội dung |
|---|---|
| `01_bao_cao/` | Báo cáo Product Reverse Engineering (HTML, 20 phần, có gallery ảnh demo, bản đồ API web nội bộ, ERD, blueprint MVP/V1/V2) và báo cáo tổng quan ban đầu (Markdown). |
| `02_wireframe/` | Wireframe low-fi 15 màn hình + sitemap + danh mục component Angular + design tokens. Mỗi màn hình gắn nhãn Observed (thấy trên demo) / From manuals / Proposed. |
| `03_anh_demo/` | 9 ảnh chụp chính từ tài khoản demo (Trang minh họa) đã đặt tên; `raw/` chứa toàn bộ ảnh gốc chụp trong phiên. |
| `04_ghi_chu_nghien_cuu/` | Ghi chú gốc của từng hướng nghiên cứu, có trích nguồn và nhãn FACT/INFERENCE/SPECULATION. Quan trọng nhất cho dev: `api_integration.md`, `workflows_data_model.md`, `source_code_clients.md`, `source_code_clients_2.md`, `demo_observations.md`. |
| `05_tai_lieu_huawei/` | Tài liệu Huawei công khai đi kèm các repo cộng đồng: Northbound Interface Reference (V500R007C00, V600R022C00, V600R023C00), hướng dẫn tạo tài khoản API/openAPI. |

## Lưu ý
- Ảnh demo là giao diện của Huawei, chỉ dùng tham khảo nội bộ; wireframe là bản vẽ lại độc lập, không dùng thương hiệu Huawei.
- Mã nguồn tham khảo: pjugowiec, pyhfs, HomeAssistant-FusionSolar, fusion_solar_py dùng MIT; huawei-solar-lib/huawei_solar dùng AGPL-3.0 (không chép code nếu không chấp nhận AGPL).
- Các mục còn UNKNOWN (màn hình báo động, báo cáo, ticket, quản trị công ty, Northbound không hiển thị với tài khoản guest) cần kiểm chứng bằng tài khoản installer thật.
- Mốc cần theo dõi: các kết nối kiểu cũ có thể ngừng đồng bộ từ 01/12/2026 (theo thông báo của EnergyID); Huawei đang chuyển sang cơ chế owner cấp quyền (OAuth Connect).
