# first_repo

## Giới thiệu
Viết code để tạo phần mềm worktime trong vscode bằng python   

## Mục đích
- Lấy file giờ công excel 
- đọc file 
- chuyển đổi dữ liệu thành các dashboard tương ứng
- phù hợp báo cáo tuần và tháng 
## Code python
worktime_view.py (Giao diện app worktime )
  - tiếp nhận file
  - Chọn worker
  - xuất Dashboard nhiều loại khác nhau
worktime_model.py 
  - Hàm số
  - Xử lý các tham số trước khi thực hiện các thao tác trên view
worktime_controller.py
  - hàm kết nối worktime_model và worktime_view để thực hiện mục đích chương trình
main.py
  - tổng hợp tất cả và run app 
## Trạng thái
Đã hoàn thành 
