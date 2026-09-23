# Theo dõi tiến độ tái kiểm — triển khai với MariaDB

Ứng dụng gồm một giao diện `index.html`, backend Flask trong `app.py` và cơ sở dữ liệu MariaDB.
Frontend không cần build bằng npm.

## 1. Yêu cầu

- Python 3.9 trở lên
- MariaDB 10.5 trở lên
- Máy chạy ứng dụng kết nối được tới cổng MariaDB, mặc định là `3306`

Hai chức năng xuất Excel và xuất ảnh sử dụng thư viện từ CDN. Nếu mạng nội bộ chặn Internet,
các chức năng nhập liệu, tổng hợp và báo cáo vẫn hoạt động nhưng hai nút xuất file có thể không dùng được.

## 2. Tạo database và tài khoản

Mở file `mariadb_setup.sql`, thay `CHANGE_ME_WITH_A_STRONG_PASSWORD`, rồi chạy bằng tài
khoản quản trị MariaDB:

```bash
mariadb -u root -p < mariadb_setup.sql
```

Hoặc có thể tạo thủ công bằng các câu lệnh tương đương:

```sql
CREATE DATABASE jingum
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER 'jingum'@'%' IDENTIFIED BY 'thay-mat-khau-manh-tai-day';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE ON jingum.* TO 'jingum'@'%';
FLUSH PRIVILEGES;
```

Nếu ứng dụng chạy cùng máy với MariaDB, có thể thay `'jingum'@'%'` bằng
`'jingum'@'localhost'` để giới hạn truy cập.

## 3. Cấu hình ứng dụng

Sao chép `.env.example` thành `.env` và sửa thông tin thực tế:

```dotenv
PORT=8000
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=jingum
DB_USER=jingum
DB_PASSWORD=mat-khau-thuc-te
DB_CONNECT_TIMEOUT=10
```

File `.env` đã được đưa vào `.gitignore`; không commit mật khẩu lên Git.

## 4. Cài đặt

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Nếu cần chuyển một `data.db` đang sử dụng, thực hiện mục 5 **trước lần đầu chạy
`python app.py`**. Nếu không có dữ liệu SQLite cần chuyển, khởi động ứng dụng:

```powershell
python app.py
```

Ứng dụng tự tạo bảng `records` nếu chưa có. Nếu bảng đang rỗng, 70 bản ghi trong
`seed_data.json` sẽ được nạp tự động. Sau đó truy cập:

```text
http://IP_MAY_CHU:8000
```

## 5. Chuyển dữ liệu từ SQLite cũ

Trước khi chuyển, sao lưu cả `data.db` và database MariaDB.

Thực hiện bước này trước lần đầu khởi động ứng dụng để MariaDB còn trống. Sau khi đã
cấu hình `.env`, chạy:

```powershell
python migrate_sqlite_to_mariadb.py data.db
```

Script chỉ đọc SQLite và sẽ dừng nếu MariaDB đã có dữ liệu. Nếu chắc chắn muốn ghi đè
các bản ghi trùng khóa trong MariaDB:

```powershell
python migrate_sqlite_to_mariadb.py data.db --overwrite
```

Sau khi migration thành công, kiểm tra số lượng:

```sql
SELECT collection, COUNT(*) AS total
FROM jingum.records
GROUP BY collection;
```

Không xóa `data.db` cho tới khi đã kiểm tra giao diện, số liệu tổng hợp và bản sao lưu.

## 6. API và mô hình dữ liệu

- `GET /api/all`: đọc toàn bộ dữ liệu
- `POST /api/save`: thêm hoặc cập nhật một bản ghi
- `POST /api/delete`: xóa một bản ghi

Bảng `records` lưu khóa `(collection, doc_id)`, JSON nghiệp vụ trong cột `data` và thời gian
cập nhật UTC trong `updated_at`. MariaDB sử dụng InnoDB và `utf8mb4` để lưu đầy đủ tiếng
Việt và tiếng Hàn.

## 7. Chạy thường trực bằng PM2

Cấu hình PM2 chạy `serve.py` bằng Waitress, không dùng Flask development server. Cài Node.js,
PM2 và các thư viện Python:

```bash
npm install -g pm2
python -m venv .venv
```

Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
pm2 start ecosystem.config.js
pm2 status
pm2 logs Jingum_Web
```

Windows Server PowerShell, chạy bằng tài khoản sẽ vận hành ứng dụng:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\deploy_windows.ps1
```

Lần chạy đầu, script tạo `.env` rồi dừng. Sửa mật khẩu MariaDB trong `.env`, sau đó chạy
lại `deploy_windows.ps1`. Script sẽ tạo `.venv`, cài dependency, cài PM2 nếu cần, khởi động
`Jingum_Web` và chạy `pm2 save`.

Sau khi kiểm tra ứng dụng hoạt động, lưu danh sách tiến trình:

```bash
pm2 save
```

Trên Linux, chạy `pm2 startup`, sau đó sao chép và thực thi chính xác lệnh `sudo` mà PM2
in ra. Cuối cùng chạy lại `pm2 save`. Khi cập nhật mã nguồn:

```bash
pip install -r requirements.txt
pm2 restart Jingum_Web
pm2 save
```

Các lệnh vận hành thường dùng:

```bash
pm2 logs Jingum_Web --lines 100
pm2 monit
pm2 restart Jingum_Web
pm2 stop Jingum_Web
pm2 delete Jingum_Web
```

### Tự khởi động trên Windows Server

PM2 không cung cấp startup hook Windows gốc, vì vậy dùng Task Scheduler:

1. Mở **Task Scheduler** → **Create Task**.
2. Tên task: `Jingum PM2 Startup`.
3. Chọn **Run whether user is logged on or not** và **Run with highest privileges**.
4. Chọn đúng tài khoản Windows đã chạy `deploy_windows.ps1`/`pm2 save`.
5. Trigger: **At startup**, nên đặt delay 30 giây để MariaDB khởi động trước.
6. Action → Program: `powershell.exe`.
7. Arguments:

```text
-NoProfile -ExecutionPolicy Bypass -File "C:\duong-dan\jingum-server-app\pm2_resurrect_windows.ps1"
```

8. Start in: `C:\duong-dan\jingum-server-app`.

Khởi động lại Windows Server rồi kiểm tra bằng `pm2 status` và
`Invoke-WebRequest http://127.0.0.1:8000/api/all`. Nếu cần cho máy khác trong mạng truy cập,
mở PowerShell bằng quyền Administrator:

```powershell
New-NetFirewallRule -DisplayName "Jingum Server 8000" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

Nếu Python virtual environment nằm ở vị trí khác, đặt biến `JINGUM_PYTHON` thành đường dẫn
tuyệt đối tới Python trước khi chạy `pm2 start`.

## 8. Vận hành và sao lưu

PM2 quản lý tiến trình Waitress; nếu cần HTTPS hoặc tên miền nội bộ, đặt Nginx/IIS làm reverse
proxy phía trước. Chỉ mở cổng MariaDB cho máy chạy ứng dụng, không công khai cổng `3306` ra Internet.

Nên sao lưu MariaDB định kỳ, ví dụ:

```powershell
mariadb-dump -h 127.0.0.1 -u jingum -p --single-transaction jingum > jingum_backup.sql
```
