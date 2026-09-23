# Theo dõi tiến độ tái kiểm — Bản triển khai trên máy chủ nội bộ

## Đây là gì (tóm tắt dành cho quản trị viên máy chủ)

- **Ứng dụng web**: chỉ có một file `index.html`. Máy chủ Flask sẽ phục vụ file này trực tiếp. Không cần build riêng (npm, v.v.).
- **CSDL**: `data.db` — chỉ là một file SQLite duy nhất. Không cần cài đặt máy chủ CSDL riêng như MySQL/MSSQL.
  Bản thân file này chính là cơ sở dữ liệu. **Đối tượng cần sao lưu định kỳ chỉ là file này.**
- **Máy chủ**: `app.py` — một web server rất nhỏ được viết bằng Python (Flask).
  - `/` : màn hình ứng dụng web
  - `/api/all` `/api/save` `/api/delete` : các API đọc/ghi dữ liệu
- Nếu muốn kết nối với CSDL khác đang dùng (ví dụ MSSQL, MySQL), chỉ cần chỉnh sửa hàm
  `get_conn()` và 3 hàm SQL (`api_all`, `api_save`, `api_delete`) trong `app.py` cho phù hợp
  với CSDL đó. Vì mô hình dữ liệu chỉ có một dạng bảng duy nhất `(phân loại, ID tài liệu,
  dữ liệu JSON)`, nên dù chuyển sang CSDL nào thì cấu trúc vẫn giống nhau.

## Yêu cầu hệ thống

- Python 3.9 trở lên (kiểm tra xem máy chủ nội bộ đã có sẵn chưa bằng lệnh `python3 --version`)
- Ngoài ra không cần kết nối Internet bên ngoài (toàn bộ logic của ứng dụng chạy hoàn toàn
  ở local. Tuy nhiên, khi nhấn nút xuất ảnh/Excel trên trình duyệt, ứng dụng sẽ tải 2 thư viện
  (xlsx, html2canvas) từ `cdnjs.cloudflare.com` — nếu mạng nội bộ chặn Internet bên ngoài thì
  chỉ hai nút này không hoạt động, các chức năng còn lại vẫn hoạt động bình thường. Nếu cần,
  tôi có thể tải các file này về và đổi sang đường dẫn local, cứ cho tôi biết nếu cần.)

## Cách chạy

```bash
cd jingum-server-app
pip install -r requirements.txt
python app.py
```

Cổng mặc định là **8000**. Nếu muốn dùng cổng khác:

```bash
PORT=9000 python app.py
```

Sau khi chạy, truy cập `http://IP_máy_chủ:8000` từ mạng nội bộ là được. Giống như các dự án
nội bộ khác (ví dụ kiểm tra PQC), nếu quản trị viên máy chủ gắn một địa chỉ truy cập chính thức
(tên miền/reverse proxy) thì mọi người có thể dùng chung địa chỉ đó.

Nếu cần **chạy liên tục 24/7** (để mọi người có thể nhập dữ liệu bất cứ lúc nào), hãy nhờ
quản trị viên máy chủ đăng ký theo một trong các cách sau:
- Linux: đăng ký dịch vụ `systemd`, hoặc chạy thường trực bằng `pm2`/`supervisor`
- Windows Server: dùng "Task Scheduler" để tự khởi động khi boot máy, hoặc kết hợp IIS + wfastcgi

## Dữ liệu ban đầu

File `seed_data.json` chứa dữ liệu được lấy từ file Excel hiện có (재검_진행사항 / tiến độ tái kiểm).
Khi chạy lần đầu mà chưa có file `data.db`, dữ liệu này sẽ tự động được nạp vào một lần duy nhất.
Nếu `data.db` đã tồn tại rồi thì sẽ không bị đụng đến, nên có thể yên tâm khởi động lại.

## Đăng nhập / Phân quyền

Theo yêu cầu, bất kỳ ai cũng có thể truy cập và nhập dữ liệu mà không cần đăng nhập riêng.
Nếu chỉ để địa chỉ này truy cập được trong mạng nội bộ thì bản thân điều đó đã là một hình thức
kiểm soát truy cập. (Nếu có kế hoạch mở cho truy cập từ bên ngoài, nên thêm ít nhất một lớp bảo
vệ bằng mật khẩu — nếu cần, tôi có thể bổ sung thêm.)

## Cách màn hình được cập nhật

Để nhiều người có thể thấy dữ liệu người khác nhập cùng lúc mà không cần tải lại trang,
**cứ mỗi 20 giây ứng dụng sẽ tự động lấy lại dữ liệu mới nhất từ máy chủ** (không phải là
thông báo thời gian thực, nhưng về cơ bản hoạt động gần như thời gian thực). Nếu muốn thay đổi
nhanh hơn/chậm hơn, chỉnh giá trị 20000 (đơn vị ms) trong đoạn
`setInterval(refreshFromServer, 20000)` bên trong file `index.html`.

## Khi có thắc mắc

- Nếu thấy cảnh báo màu đỏ ở đầu màn hình ("Không thể kết nối đến máy chủ…") → có nghĩa là
  `app.py` đang tắt, hoặc địa chỉ/cổng không đúng.
- Nếu dữ liệu có vẻ bất thường → hãy mở file `data.db` để kiểm tra (dùng công cụ xem SQLite,
  ví dụ DB Browser for SQLite), hoặc gửi lại file cho tôi để tôi kiểm tra giúp.
