# Quan sát trực tiếp trên tài khoản demo FusionSolar (07/10/2026)

Nguồn: https://intl.fusionsolar.huawei.com → link "Trang minh họa" trên trang đăng nhập (không cần mật khẩu). Phiên đăng nhập tự động với user `guest_account_*` (role Guest). Giao diện tiếng Việt. Chỉ xem, không thay đổi gì. Ảnh chụp lưu trong `demo_screens/`.

Mọi mục dưới đây là **FACT (quan sát trực tiếp, 07/10/2026)** trừ khi ghi INFERENCE.

## 1. Truy cập demo & phiên
- Trang đăng nhập có 3 link: "Đăng ký đơn vị lắp đặt" (installer company registration), "Quên mật khẩu?", "Trang minh họa" (demo). Có QR tải app. Có chọn ngôn ngữ. Footer khuyến nghị Chrome 79+/Firefox ESR 68+, độ phân giải 1920×1080.
- Click "Trang minh họa" → vào thẳng portal với user `guest_account_xxxxxx` (userId số), URL: `/uniportal/pvmswebsite/assets/build/cloud.html?app-id=smartpvms&instance-id=smartpvms&zone-id=<uuid>#/home/list` → SPA hash-routing, kiến trúc "uniportal" + app-id/instance-id/zone-id (INFERENCE: micro-frontend/multi-app framework; app `smartpvms` là một app trong khung web-framework chung của Huawei Digital Power).
- Phiên guest hết hạn sau khoảng 13 phút → bị đá về trang login (redirect kèm return URL trong hash).
- Session giữ bằng `GET /rest/dpcloud/auth/v1/keep-alive` và `GET /rest/dpcloud/auth/v1/is-session-alive` gọi định kỳ.
- Menu được server cấp: `GET /rest/dpcloud/dpuniwebframeworkservice/web-framework/menu/query?applicationId=smartpvms&zoneId=...` (INFERENCE: menu lọc theo role phía server — RBAC hướng menu).

## 2. Menu thực tế của role Guest (top navigation)
- **Trang chủ** → "Xem theo danh sách" (`#/home/list`), "Chế độ xem KPI" (`#/home/kpi`)
- **Giám sát** → "Giám sát" (`#/view/station/<dn>/overview`)
- **Nhà máy** → nhóm "Thiết bị" → "Quản lý thiết bị" (`#/settings/device-management`)
- **Hệ thống** → nhóm "Giới thiệu" → Tuyên bố Quyền riêng tư, Thỏa thuận Người dùng, Chính sách cookie, Nhật ký cập nhật (`#/proUse/updateLog`), Liên hệ với chúng tôi
- Header phải: icon "Việc cần làm" (to-do panel trượt bên phải — guest: "Không dữ liệu"), Tìm kiếm, Ngôn ngữ, menu user, Giới thiệu (i), Trợ giúp (?).
- Guest KHÔNG thấy: Báo động/Bảo trì, Báo cáo, Quản lý công ty/người dùng, Northbound. Click số báo động trên Trang chủ không mở được danh sách. (FACT cho guest; INFERENCE: các menu này tồn tại cho role installer/admin — khớp manual).
- **Tab cấp nhà máy đầy đủ (role không phải guest)** thấy được trong ảnh preview của Nhật ký cập nhật 2026-06: Tổng quan | Khuynh hướng | Quản lý báo cáo | Quản lý thiết bị | Báo động | Trợ lý Quản lý Năng lượng | Bảo vệ sức khỏe thông minh | Người dùng nhà máy. Guest chỉ thấy: Tổng quan | Bố cục | Quản lý thiết bị.

## 3. Trang chủ — List view (`#/home/list`)
- Banner KPI toàn danh mục: Công suất hiện tại (kW), Sản lượng hôm nay (kWh), Doanh thu hôm nay (tiền tệ), Công suất định mức của bộ biến tần (kW), Công suất ESS định mức (kWh), Tổng sản lượng (MWh). Icon bánh răng cạnh "KPI nhà máy" (cấu hình KPI hiển thị).
- Donut "Trạng thái nhà máy": tổng 7 — Thường 4 / Lỗi 1 / Đã ngắt kết nối 2.
- Donut "Báo động hiện hoạt": tổng 4 — Nghiêm trọng 0 / Cao 3 / Thấp 1 / Cảnh báo 0 (4 mức severity).
- Toggle list/KPI view ở góc phải banner.
- Bộ lọc: Quốc gia/Khu vực, Loại thiết bị, SN của thiết bị, "Mở rộng" (thêm filter), Tìm kiếm, Đặt lại.
- Bảng nhà máy, cột: Trạng thái, Hình ảnh nhà máy, Tên nhà máy, Quốc gia/Khu vực, Địa chỉ (bị che `******` với guest), Ngày nối lưới, Tổng công suất chuỗi (kWp), Số lượng bộ tối ưu, Bộ lưu trữ (icon), Trạm sạc, Công suất hiện tại (kW), Năng lượng riêng (kWh/kWp), Sản lượng hôm nay (kWh), Tổng sản lượng (kWh), Tỷ lệ hiệu suất (%) (= Performance Ratio, demo toàn 0,00 vì không có cảm biến bức xạ), Bức xạ toàn cầu (kWh/m²). Cột sort được; icon bánh răng cấu hình cột; phân trang 10/trang.
- Dữ liệu demo: 7 nhà máy (Philippines, Thái Lan, Nam Phi), 4–28 kWp, phần lớn có bộ tối ưu (20–48) và ESS → demo nghiêng về Residential/small C&I.
- Lỗi dữ liệu quan sát được: một nhà máy Thái Lan có "Ngày nối lưới" = `2565-01-29` (năm Phật lịch Thái lọt vào dữ liệu) → INFERENCE: định dạng ngày nhập từ app theo locale, không chuẩn hóa.
- Network: `POST /rest/pvms/web/station/v1/station/station-list`, `GET .../station/area-list?isRegionQuery=true&locale=vi_VN`, `GET /rest/pvms/web/viewsetting/v1/viewcfg?userName=...&viewType=1|3` (lưu cấu hình view theo user), `GET /rest/dp/pvms/pvmswebservice/v1/configcenter/config-value`, `GET /rest/pvms/web/station/v1/station/total-real-kpi?queryTime=...&timeZone=7`, `GET .../station/station-status-count`, `GET /rest/pvms/fm/v1/statistic` (fm = fault management → thống kê alarm), `POST /rest/dp/pvms/organization/v1/select-station`.

## 4. Trang chủ — KPI view (`#/home/kpi`)
- Cùng banner. Thêm: "Thống kê sản lượng" (bar chart theo giờ; tab Ngày/Tháng/Năm/Tuổi thọ; date picker), "Xếp hạng nhà máy hôm nay (năng lượng riêng)" (top 5 kWh/kWp), "Lợi ích môi trường" (than tiêu chuẩn tiết kiệm (tấn), CO₂ giảm (tấn), số cây tương đương).
- Network: `POST /rest/pvms/web/report/v1/station/home-station-kpi-chart`, `GET .../station/equivalent-utilization-hours?showNum=5`, `GET .../station/social-contribution?clientTime=...&timeZone=7`.

## 5. Giám sát — cây tổ chức + trang nhà máy
- Panel trái: cây tổ chức "Root" → công ty (GoSolar Philippines, A.R.C. Siam Solar, Creovision, Pond, Solar Sunday) → nhà máy → thiết bị (gateway → thiết bị con). Ô tìm "Nhập tên thiết bị" có dropdown chọn loại đối tượng. → FACT: mô hình đa công ty lồng nhau, nhà máy thuộc công ty, thiết bị dạng cây cha-con.
- `POST /rest/dp/pvms/organization/v1/tree`, `GET /rest/dp/pvms/organization/v1/locate-tree?targetDn=NE=...&subNodeTypeIds=20801,20800,20811,...` (danh sách mã loại node 208xx/600xx) .
- Định danh: `stationDn=NE=58607856` (plant), thiết bị `NE=58607861` (inverter), `NE=58607858` (EMMA) → FACT: mọi đối tượng (plant/device) là "managed object" có DN dạng `NE=<số>` trong cùng không gian ID.

### 5.1 Tab Tổng quan (`#/view/station/<dn>/overview`)
- Header: tên nhà máy + chấm trạng thái; widget thời tiết 3 ngày (hôm nay, T5, T6) với nhiệt độ min~max.
- Thẻ KPI: Sản lượng hôm nay, Tổng sản lượng, Mức sử dụng hôm nay (tiêu thụ), Công suất tự dùng (self-consumption).
- Sơ đồ dòng năng lượng (energy flow) 4 nút: PV (kW), Bộ lưu trữ (SOC % + kW), Lưới điện (kW), Tải (kW); nhãn trạng thái "Hòa lưới"; đường động hướng dòng.
- Lợi ích môi trường (than, CO₂, cây).
- Báo động theo 4 mức (Nghiêm trọng/Nặng/Thấp/Cảnh báo — lưu ý nhãn khác trang chủ: "Cao" vs "Nặng").
- Thông tin: Địa chỉ (che với guest), Tổng công suất chuỗi (kWp), Ngày nối lưới.
- "Quản lý năng lượng": tab Ngày/Tháng/Năm/Tuổi thọ; tách Sản lượng PV = Đã tiêu thụ + Đã nạp vào lưới (kWh, %); Tiêu thụ = Từ quang điện + Từ lưới (kWh, %); line chart 5 phút: Công suất PV, Tổng mức tiêu thụ, Trạng thái sạc pin (SOC), Đã tiêu thụ từ PV, Bộ lưu trữ… (legend phân trang 1/2); thanh zoom thời gian.
- "Doanh thu": tab Tháng/Năm/Tuổi thọ; bar chart doanh thu theo ngày; tiền tệ theo nhà máy (₱ PHP) → FACT: tiền tệ & giá điện cấu hình theo nhà máy.
- Network: polling `GET /rest/dp/pvms/station/v1/overview/running-status?stationDn=...` khoảng mỗi ~5 giây khi mở trang (quan sát 4 request trong ~20 s) → INFERENCE: energy flow "gần realtime" bằng HTTP polling (không thấy WebSocket).

### 5.2 Tab Bố cục (`#/view/station/<dn>/layout`)
- Hai chế độ: "Bố cục thực tế" (physical layout — demo trống, có link "Hướng dẫn nhanh về bố cục thực tế") và "Bố cục logic".
- Bố cục logic: inverter → 2 chuỗi × 10 tấm pin; mỗi ô tấm pin hiển thị sản lượng hôm nay (kWh, ~1,57–1,67) và mã vị trí (1.1.1 … 1.2.10) + icon trạng thái bộ tối ưu → FACT: giám sát cấp module nhờ optimizer.
- Dropdown chỉ số: "Sản lượng (kWh)" + "Hôm nay". Legend: Bộ biến tần, Mô-đun, Bộ tối ưu; trạng thái màu: Bình thường / Bị lỗi / Ngoại tuyến / Đã ngắt kết nối; "Chú giải màu sắc". Có "Mở rộng cây thiết bị", minimap "Tổng quan", nút zoom/fit.
- Network: `GET /rest/dp/pvms/station/v1/layout/buildings`, `POST /rest/pvms/web/station/v1/layout/sheet/query-sheets`, `GET .../layout/station-simple-devicedata`, `GET .../layout/disconnect-detect-menu`, `POST .../layout/device-tree-page`, `POST .../layout/device-sampling-data`, `POST .../layout/device-energy`, `GET /rest/pvms/web/station/v1/layout?stationDn=...&sheetNO=0&callerType=0&queryType=0` → INFERENCE: layout có "buildings" và "sheets" (nhiều mặt mái/trang bố cục).

### 5.3 Tab Quản lý thiết bị (cấp nhà máy, `#/view/station/<dn>/device-manage`)
- Filter: Loại thiết bị, Tên thiết bị, SN, Mở rộng; Tìm kiếm/Đặt lại. Checkbox chọn nhiều (bulk action, guest không có nút).
- Cột: Trạng thái thiết bị, Tên thiết bị, Tên nhà máy, Loại thiết bị, Phiên bản phần mềm, SN (che một phần), Thiết bị cao cấp (parent), Thiết bị giao tiếp (communication device), Model, Số thẻ SIM, Chạy thử bởi (commissioned by). Hàng inverter có dấu "+" mở thiết bị con (optimizer).
- Thiết bị demo: SmartAssistant **EMMA-A02** (SmartHEMS V100R025C00SPC102) là gateway/cha; **SUN2000-8K-LC0** (V100R023C10SPC109); Cảm biến nguồn **DTSU666_H** (đồng hồ xuất+nhập); BackupBox **SmartGuard-63A-S0** (V100R023C10SPC107). Parent & communication device của 3 thiết bị đều là EMMA.
- Network: `GET /rest/neteco/web/config/device/v1/device-list?conditionParams.parentDn=...&conditionParams.signals=10046,10047,21001,...&conditionParams.noIncludeMocIds=20859,20860&conditionParams.maintenance=false` → FACT: danh sách thiết bị kèm "signals" (mã điểm tín hiệu số); `GET /rest/neteco/web/config/device/v1/additional-moc-type?functionItem=DataExportable`; `GET /rest/pvms/web/device/v1/get-system-config`. Tiền tố `neteco` → kế thừa nền tảng iMaster NetEco.

### 5.4 Chi tiết thiết bị — Inverter (`#/view/device/<dn>/inverter/details`)
- Tab: "Chi tiết" | "Thông tin trước đó" (lịch sử).
- "Dữ liệu thiết bị theo thời gian thực": bảng chuỗi PV1/PV2/PV3 (điện áp V, dòng A); Trạng thái bộ biến tần (Hòa lưới), Năng lượng hàng ngày, Tổng sản lượng, Công suất thuần (kW), Công suất vô công (kvar), Công suất định mức (8 kW), Hệ số công suất, Tần số lưới (60,32 Hz), Chế độ đầu ra (L1/L2), Dòng/Áp lưới, Thời gian khởi động/tắt, Nhiệt độ bên trong, Điện trở cách điện (MΩ), Trạng thái điều chỉnh công suất thuần ("P=11.5% (Tỷ lệ giảm công suất thuần)" → đang bị giới hạn công suất/derating), Trạng thái điều chỉnh vô công (PF=1.000), Cường độ WiFi.
- "Thông tin cơ bản": Tên, Loại, Số sê-ri, Lịch sử thay thiết bị, Model, Phiên bản phần mềm, Tên gói.
- Network: `GET /rest/pvms/web/device/v1/mo-details?dn=...`, `GET .../deviceExt/is-device-online`, `GET .../device-statistics-signal`, `GET .../device-real-kpi?deviceDn=...&signalIds=10095` (và một call với ~150 signalIds 10006…11119 = các điểm đo theo chuỗi), `GET .../device-realtime-data?displayAccessModel=true`, `GET .../device-signal-unit?signalIds=...` (đơn vị cho từng signal), `POST /rest/neteco/web/config/device/v2/device-status-query`, `GET /rest/neteco/web/organization/v2/check-shared-mo`, `GET /rest/neteco/web/config/device/v1/config/query-moc-config-signal`, `GET .../moc-type-name`, `GET /rest/pvms/web/sharestation/v1/config-signal`.
- **Phân quyền quan sát được:** `GET /rest/pvms/web/ivcurve/v1/devmanager/originaloptions?dnsList=...` trả **401** cho guest → FACT: Smart I-V là chức năng có kiểm soát quyền ở API; guest không có.
- `GET /rest/dp/pvms/organization/v3/users/verification/mode`, `GET /rest/dpcloud/usermgnt/er/v1/users/personalinfo` (thông tin user) gọi trên mỗi trang.

### 5.5 Lịch sử thiết bị (`.../inverter/history`)
- Chọn Ngày + "Điểm tín hiệu" (multi-select, mặc định 2: Công suất thuần, Tổng công suất đầu vào) → line chart 5 phút trong ngày.
- `GET /rest/pvms/web/device/v1/device-history-data?showDst=true&signalIds=30014&signalIds=30017&deviceDn=...&date=<ms>` → FACT: lịch sử truy vấn theo signalId + ngày; có cờ DST.

### 5.6 Chi tiết SmartAssistant/EMMA (`#/view/device/<dn>/submatrix/details`)
- Tab: Chi tiết | Quản lý thiết bị | Thông tin trước đó.
- Realtime: Năng lượng thuần chuyển tiếp (kWh, import), Năng lượng hữu công nghịch đảo (kWh, export), Công suất vô công, Công suất thuần, Hệ số công suất, Điện áp/Dòng lưới, Chế độ cổng RS485-2 (Máy master), WiFi.
- "Thiết bị thứ cấp" (con): trạng thái kết nối, loại, model, phiên bản, SN.
- "Chi tiết cổng DO" (Digital Output — điều khiển tải: DO1 "load1", loại tải "Tổng tải", Trực tuyến).
- "Chi tiết công tắc thông minh" (smart switches; số kênh).
- **"Chi tiết thiết bị hệ sinh thái"**: cột Tên, Loại, Nhà cung cấp, Mô hình, Giao thức, Trạng thái giao tiếp, Công suất hiện tại → FACT: SmartAssistant hỗ trợ thiết bị bên thứ ba (đa hãng) với trường "Giao thức".
- Network: `GET /rest/dp/pvms/device/v1/load/hems-device-detail?dn=...`, `GET /rest/neteco/web/config/device/v1/children-list?...&monitoringRelation=true&mocTypes=20822,60080,20817,20816,20861,20877,20874`.

## 6. Nhà máy → Quản lý thiết bị (toàn công ty, `#/settings/device-management`)
- Layout: sidebar trái "Thiết bị > Quản lý thiết bị", cây công ty (tìm "Nhập tên công ty"), bảng thiết bị cùng cột như 5.3. Demo trả 0 thiết bị ở Root với guest.

## 7. Nhật ký cập nhật (release notes web portal) — cadence ~quý
(Đọc trực tiếp; ngày ghi trên trang)
- **2026-06-31** (sic, ngày không hợp lệ hiển thị trên trang): Chế độ lên lịch thông minh cho nhà máy dân dụng cho phép đặt tùy chọn sử dụng "điện xanh", xem realtime trên trang "Trợ lý Quản lý Năng lượng".
- **2026-03-31**: C&I — cấu hình mẫu (template), thiết lập giá điện, phân tích doanh thu và SmartEMO hỗ trợ tính phí theo nhu cầu (demand charge) theo khung giờ (TOU).
- **2025-12-31**: (1) C&I — máy phát (generator) có thể sạc ESS; (2) với SmartAssistant, nếu kết nối inverter bên thứ ba, sơ đồ dòng năng lượng hiển thị riêng công suất inverter Huawei và bên thứ ba.
- **2025-09-30**: (1) EMMA đổi tên thành **SmartAssistant** (model EMMA-A02, SA4H-A02); (2) bật bán điện từ ESS lên lưới trong cài đặt quản lý năng lượng hộ gia đình; (3) không thể đưa nhà máy lên nền tảng nếu công suất vượt giới hạn trên theo quốc gia/khu vực; (4) installer có thể mời chủ sở hữu ngay khi tạo nhà máy.
- **2025-06-30**: (1) báo cáo xuất được thống kê theo giờ trong khoảng thời gian; xem được báo cáo cấp công ty (tab báo cáo: Báo cáo nhà máy / bộ biến tần / PCS / bộ lưu trữ); (2) thêm tab **"Người dùng nhà máy"** — chủ sở hữu có thể thêm/xóa chủ sở hữu khác; (3) **ngừng hỗ trợ**: thêm nhà máy quy mô tiện ích (utility) trên nền tảng này; installer xóa/vô hiệu hóa tài khoản chủ sở hữu; installer xóa chủ sở hữu khỏi nhà máy; xóa hàng loạt nhà máy; xóa hàng loạt thiết bị.
- **2025-03-31**: (1) hệ thống quản lý C&I hỗ trợ "bảng điều khiển" (dashboard) cho kịch bản C&I PV + ESS + bộ sạc; (2) thêm Thái Lan.
- **2024-12-30**: (1) đồ thị quản lý năng lượng hiển thị SOC của ESS; (2) thêm ngôn ngữ Romania, Séc; (3) thêm tiền tệ KZT, UZS.
- **2024-10-15**: tăng cường bảo mật, tối ưu nhiều module.

INFERENCE từ release notes:
- Nền tảng cloud intl đang thu hẹp về Residential + C&I (utility mới không còn thêm vào đây từ 6/2025) → utility dùng hệ quản lý riêng (SmartPVMS/NetEco on-prem hoặc FusionSolar 9.0).
- Chuyển quyền kiểm soát dữ liệu/tài khoản từ installer sang owner (owner tự quản lý người dùng nhà máy; installer không xóa owner được) — cùng hướng với yêu cầu owner cấp quyền API từ 9/2025.
- EMMA/SmartAssistant trở thành trung tâm HEMS, mở ra thiết bị bên thứ ba (inverter, "thiết bị hệ sinh thái").

## 8. Danh sách endpoint web nội bộ quan sát được (để đối chiếu với fusion_solar_py)
Nhóm theo tiền tố:
- `/rest/dpcloud/auth/v1/{keep-alive,is-session-alive}` — phiên
- `/rest/dpcloud/usermgnt/er/v1/users/personalinfo` — user
- `/rest/dpcloud/dpuniwebframeworkservice/web-framework/menu/query` — menu theo app/zone
- `/rest/dp/pvms/organization/v1/{tree,select-station,locate-tree}`, `/v3/users/verification/mode` — tổ chức/cây
- `/rest/dp/pvms/station/v1/overview/running-status`, `/layout/buildings` — tổng quan/bố cục
- `/rest/dp/pvms/device/v1/load/hems-device-detail` — HEMS
- `/rest/dp/pvms/pvmswebservice/v1/configcenter/config-value` — cấu hình
- `/rest/pvms/web/station/v1/station/{station-list,area-list,total-real-kpi,station-status-count,equivalent-utilization-hours,social-contribution}`
- `/rest/pvms/web/station/v1/layout/{sheet/query-sheets,station-simple-devicedata,disconnect-detect-menu,device-tree-page,device-sampling-data,device-energy}`, `/rest/pvms/web/station/v1/layout`
- `/rest/pvms/web/device/v1/{mo-details,device-real-kpi,device-realtime-data,device-signal-unit,device-statistics-signal,device-history-data,get-system-config,deviceExt/is-device-online}`
- `/rest/pvms/web/report/v1/station/home-station-kpi-chart`
- `/rest/pvms/web/viewsetting/v1/viewcfg` — cấu hình view per user
- `/rest/pvms/web/sharestation/v1/config-signal`
- `/rest/pvms/web/ivcurve/v1/devmanager/originaloptions` — Smart I-V (401 với guest)
- `/rest/pvms/fm/v1/statistic` — fault management
- `/rest/neteco/web/config/device/v1/{device-list,children-list,additional-moc-type,config/query-moc-config-signal,moc-type-name}`, `/v2/device-status-query`, `/rest/neteco/web/organization/v2/check-shared-mo`
INFERENCE: backend chia nhiều service theo tiền tố (dpcloud = nền tảng chung Digital Power cloud: auth/user/menu; dp/pvms & pvms/web = nghiệp vụ PV; neteco = lõi quản lý thiết bị/MO kế thừa iMaster NetEco; fm = fault management). Mô hình dữ liệu thiết bị dựa trên MOC (managed object class, mã 208xx/600xx) + signal ID số + đơn vị tra riêng — kiểu mô hình NMS viễn thông.

## 9. Gap còn lại (UNKNOWN)
- Màn Báo động, Báo cáo, Bảo trì/ticket, Quản lý công ty/người dùng, Northbound — guest không truy cập được.
- Physical layout không có dữ liệu trong demo.
- Không thấy trang trạm sạc trong demo (cột "Trạm sạc" trống).
