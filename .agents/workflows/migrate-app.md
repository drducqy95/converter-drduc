---
description: 🚚 Di dời ứng dụng Windows từ ổ C sang phân vùng thứ cấp sử dụng NTFS Directory Junctions
---

# 🚚 Workflow: Di Dời Ứng Dụng Hệ Thống Windows (App State Relocation)

> **Mục đích:** Di chuyển vật lý toàn bộ ứng dụng Windows (tệp thực thi, ProgramData, AppData) từ ổ đĩa hệ thống (C:\) sang phân vùng thứ cấp, sử dụng **Robocopy** để nhân bản toàn vẹn và **NTFS Directory Junctions** (`mklink /J`) để tạo lớp trừu tượng hóa hệ thống tệp. Đảm bảo mọi bản cập nhật và dữ liệu phát sinh trong tương lai tự động định tuyến sang ổ đĩa mới.

---

## ⚠️ CÁC RÀNG BUỘC KHÔNG THỂ THƯƠNG LƯỢNG

> [!CAUTION]
> Đây là các quy tắc BẮT BUỘC. Vi phạm bất kỳ điều nào dưới đây có thể gây hỏng hệ thống hoặc phá vỡ ứng dụng.

1. **CẤM sử dụng lệnh `copy`, `xcopy`, hoặc sao chép qua GUI.** Chỉ được dùng `robocopy` với đầy đủ cờ bảo toàn ACL.
2. **CẤM sử dụng Symbolic Links (`mklink /D`).** Chỉ được tạo **Directory Junctions** (`mklink /J`) để đảm bảo:
   - Tương thích với MSI installer & Windows Update
   - Không cần Developer Mode hoặc quyền Admin đặc biệt
   - Giảm thiểu rủi ro bảo mật (chỉ đường dẫn cục bộ tuyệt đối)
3. **CẤM can thiệp trực tiếp vào Windows Registry** trong quá trình di dời.
4. **PHẢI dừng ngay và rollback** nếu robocopy báo lỗi nghiêm trọng hoặc không thể giải phóng file handles.

---

## 📋 THÔNG TIN CẦN THU THẬP TỪ USER

Trước khi bắt đầu, hỏi user các thông tin sau:

| Thông tin | Ví dụ | Bắt buộc |
|-----------|-------|----------|
| Tên ứng dụng cần di dời | `RaiDrive`, `Docker`, `Discord` | ✅ |
| Đường dẫn đích (phân vùng thứ cấp) | `D:\APP\RaiDrive` | ✅ |
| Tên vendor/publisher (nếu biết) | `OpenBoxLab` | ⬜ Tự phát hiện |
| Có đang chạy dịch vụ nền không? | Có/Không | ⬜ Tự phát hiện |

---

## GIAI ĐOẠN 1: Lập Bản Đồ Vết Chân Ứng Dụng (Application Footprint Discovery)

> Mục tiêu: Xác định TẤT CẢ các vị trí lưu trữ của ứng dụng trên ổ C:\

### Bước 1.1: Quét dịch vụ và tiến trình

```powershell
# Tìm dịch vụ liên quan
sc.exe query state= all | findstr /i "<TÊN_ỨNG_DỤNG>"

# Tìm tiến trình đang chạy
Get-Process | Where-Object { $_.Name -match "<TÊN_ỨNG_DỤNG>" } | Format-Table Name, Id, Path -AutoSize
```

### Bước 1.2: Quét các vị trí cài đặt chuẩn

Kiểm tra lần lượt các đường dẫn sau và ghi lại những thư mục tồn tại:

```powershell
# Tệp thực thi cốt lõi
$paths = @(
    "C:\Program Files\<VENDOR>\<APP>",
    "C:\Program Files (x86)\<VENDOR>\<APP>",
    "C:\Program Files\<APP>",
    "C:\Program Files (x86)\<APP>"
)

# Dữ liệu trạng thái toàn cục (logs, cache, config)
$dataPaths = @(
    "C:\ProgramData\<VENDOR>\<APP>",
    "C:\ProgramData\<APP>",
    "$env:LOCALAPPDATA\<VENDOR>\<APP>",
    "$env:LOCALAPPDATA\<APP>",
    "$env:APPDATA\<VENDOR>\<APP>",
    "$env:APPDATA\<APP>"
)

# Kiểm tra từng đường dẫn
foreach ($p in ($paths + $dataPaths)) {
    if (Test-Path $p) {
        $size = (Get-ChildItem $p -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        Write-Host "[FOUND] $p - Size: $([math]::Round($size/1MB, 2)) MB"
    }
}
```

### Bước 1.3: Ghi nhận kết quả

Tạo danh sách các **Source Paths** cần di dời. Ví dụ:

| # | Source Path | Loại | Kích thước |
|---|-------------|------|-----------|
| 1 | `C:\Program Files\OpenBoxLab\RaiDrive` | Binaries | 150 MB |
| 2 | `C:\ProgramData\OpenBoxLab\RaiDrive` | Data/Cache/Logs | 2.5 GB |

> [!IMPORTANT]
> Nếu không tìm thấy bất kỳ thư mục nào → DỪNG và hỏi user xác nhận lại tên ứng dụng/vendor.

---

## GIAI ĐOẠN 2: Đình Chỉ Giao Dịch & Đóng Băng Tiến Trình

> Mục tiêu: Giải phóng TẤT CẢ file handles để đảm bảo dữ liệu nhất quán khi sao chép.

### Bước 2.1: Tắt giao diện người dùng (GUI)

```powershell
# Tắt tiến trình GUI (ép buộc)
taskkill /F /IM "<TÊN_ỨNG_DỤNG>.exe"
```

### Bước 2.2: Dừng dịch vụ nền (Windows Services)

```powershell
# Liệt kê dịch vụ liên quan
Get-Service | Where-Object { $_.DisplayName -match "<TÊN_ỨNG_DỤNG>" -or $_.Name -match "<TÊN_ỨNG_DỤNG>" }

# Dừng từng dịch vụ
Stop-Service -Name "<TÊN_DỊCH_VỤ>" -Force
```

### Bước 2.3: Xác nhận không còn tiến trình

```powershell
# Kiểm tra lại
Get-Process | Where-Object { $_.Name -match "<TÊN_ỨNG_DỤNG>" }
# Output mong đợi: Không có kết quả → OK
```

> [!WARNING]
> Nếu không thể dừng tiến trình/dịch vụ → **DỪNG workflow** và thông báo user. KHÔNG được tiếp tục khi file handles chưa được giải phóng.

---

## GIAI ĐOẠN 3: Khởi Tạo Không Gian & Nhân Bản Tệp Tin

> Mục tiêu: Sao chép toàn vẹn dữ liệu sang phân vùng thứ cấp với bảo toàn đầy đủ ACL, timestamps, và ownership.

### Bước 3.1: Tạo cấu trúc thư mục đích

```powershell
# Tạo thư mục đích cho từng source path
mkdir "<ĐƯỜNG_DẪN_ĐÍCH>\Program Files" -Force
mkdir "<ĐƯỜNG_DẪN_ĐÍCH>\ProgramData" -Force
# Thêm các thư mục khác nếu có AppData, v.v.
```

### Bước 3.2: Chạy Robocopy cho từng khối dữ liệu

> [!IMPORTANT]
> Cú pháp robocopy BẮT BUỘC — KHÔNG được thay đổi các cờ (flags):

```powershell
# Sao chép tệp thực thi
robocopy "<SOURCE_BINARIES>" "<ĐƯỜNG_DẪN_ĐÍCH>\Program Files" /E /COPYALL /DCOPY:DAT /ZB /R:3 /W:5

# Sao chép dữ liệu trạng thái
robocopy "<SOURCE_DATA>" "<ĐƯỜNG_DẪN_ĐÍCH>\ProgramData" /E /COPYALL /DCOPY:DAT /ZB /R:3 /W:5
```

**Giải thích các cờ:**
| Cờ | Tác dụng |
|----|----------|
| `/E` | Sao chép đệ quy kể cả thư mục rỗng (cần thiết cho staging directories) |
| `/COPYALL` | Bảo toàn Data + Attributes + Timestamps + Security/ACLs + Owner + Auditing |
| `/DCOPY:DAT` | Bảo toàn timestamps và thuộc tính ở cấp thư mục |
| `/ZB` | Chế độ Restartable + Backup mode (bypass NTFS read restrictions cho file bị khóa) |
| `/R:3` | Chỉ thử lại 3 lần (tránh treo vô hạn, mặc định 1,000,000 lần!) |
| `/W:5` | Chờ 5 giây giữa mỗi lần thử (mặc định 30 giây) |

### Bước 3.3: Kiểm định toàn vẹn dữ liệu

```powershell
# So sánh kích thước và số lượng tệp giữa nguồn và đích
function Compare-Directories {
    param($Source, $Destination)
    
    $srcInfo = Get-ChildItem $Source -Recurse -ErrorAction SilentlyContinue
    $dstInfo = Get-ChildItem $Destination -Recurse -ErrorAction SilentlyContinue
    
    $srcSize = ($srcInfo | Measure-Object -Property Length -Sum).Sum
    $dstSize = ($dstInfo | Measure-Object -Property Length -Sum).Sum
    $srcCount = ($srcInfo | Measure-Object).Count
    $dstCount = ($dstInfo | Measure-Object).Count
    
    Write-Host "Source:      Files=$srcCount, Size=$([math]::Round($srcSize/1MB, 2)) MB"
    Write-Host "Destination: Files=$dstCount, Size=$([math]::Round($dstSize/1MB, 2)) MB"
    
    if ($srcSize -eq $dstSize -and $srcCount -eq $dstCount) {
        Write-Host "[✅ PASS] Dữ liệu toàn vẹn!" -ForegroundColor Green
        return $true
    } else {
        Write-Host "[❌ FAIL] Không khớp! Kiểm tra lại." -ForegroundColor Red
        return $false
    }
}

# Chạy kiểm tra cho từng cặp source-destination
Compare-Directories "<SOURCE_BINARIES>" "<ĐƯỜNG_DẪN_ĐÍCH>\Program Files"
Compare-Directories "<SOURCE_DATA>" "<ĐƯỜNG_DẪN_ĐÍCH>\ProgramData"
```

> [!CAUTION]
> Nếu kiểm định FAIL → **DỪNG workflow**. KHÔNG được tiếp tục sang Giai đoạn 4. Kiểm tra lỗi robocopy và thử lại.

---

## GIAI ĐOẠN 4: Chuyển Tiếp Trừu Tượng Hóa & Thiết Lập Directory Junctions

> Mục tiêu: Đổi tên thư mục gốc (backup) và tạo Directory Junctions để hệ thống "nhìn thấy" đường dẫn cũ nhưng thực chất đọc/ghi vào ổ đĩa mới.

### Bước 4.1: Đổi tên thư mục gốc (backup an toàn)

> [!TIP]
> Đổi tên thay vì xóa vĩnh viễn — cho phép rollback nhanh nếu xảy ra sự cố.

```powershell
# Đổi tên thư mục gốc thành backup
Rename-Item "<SOURCE_BINARIES>" "<SOURCE_BINARIES>_backup"
Rename-Item "<SOURCE_DATA>" "<SOURCE_DATA>_backup"
```

### Bước 4.2: Tạo Directory Junctions

```powershell
# Tạo Junction Points
# ⚠️ BẮT BUỘC dùng cmd.exe /c mklink /J — KHÔNG dùng /D
cmd.exe /c mklink /J "<SOURCE_BINARIES>" "<ĐƯỜNG_DẪN_ĐÍCH>\Program Files"
cmd.exe /c mklink /J "<SOURCE_DATA>" "<ĐƯỜNG_DẪN_ĐÍCH>\ProgramData"
```

### Bước 4.3: Xác nhận Junction Points đã tạo thành công

```powershell
# Kiểm tra junction points
Get-Item "<SOURCE_BINARIES>" | Select-Object Name, LinkType, Target
Get-Item "<SOURCE_DATA>" | Select-Object Name, LinkType, Target
# LinkType phải là "Junction" và Target phải trỏ đúng đường dẫn đích
```

> [!WARNING]
> Nếu Junction không tạo được → Chạy lệnh rollback ngay:
> ```powershell
> Rename-Item "<SOURCE_BINARIES>_backup" "<SOURCE_BINARIES>"
> Rename-Item "<SOURCE_DATA>_backup" "<SOURCE_DATA>"
> ```

---

## GIAI ĐOẠN 5: Tái Kích Hoạt & Kiểm Chứng Bền Vững

> Mục tiêu: Khởi động lại ứng dụng, xác nhận hoạt động bình thường, và lên lịch dọn dẹp backup.

### Bước 5.1: Khởi động lại dịch vụ

```powershell
# Khởi động lại dịch vụ
Start-Service -Name "<TÊN_DỊCH_VỤ>"

# Hoặc khởi động ứng dụng GUI
Start-Process "<ĐƯỜNG_DẪN_ĐÍCH>\Program Files\<TÊN_ỨNG_DỤNG>.exe"
```

### Bước 5.2: Kiểm chứng hoạt động

```powershell
# Kiểm tra dịch vụ đang chạy
Get-Service | Where-Object { $_.Name -match "<TÊN_ỨNG_DỤNG>" } | Format-Table Name, Status

# Kiểm tra tiến trình
Get-Process | Where-Object { $_.Name -match "<TÊN_ỨNG_DỤNG>" } | Format-Table Name, Id

# Kiểm tra xem dữ liệu mới có được ghi vào ổ đích không
Get-ChildItem "<ĐƯỜNG_DẪN_ĐÍCH>" -Recurse | Sort-Object LastWriteTime -Descending | Select-Object -First 5 Name, LastWriteTime, Length
```

### Bước 5.3: Báo cáo kết quả cho User

Thông báo cho user:
1. ✅ Ứng dụng đã di dời thành công
2. ✅ Junction Points đã hoạt động
3. ✅ Dữ liệu mới đang ghi vào ổ đích
4. ⏳ **Thư mục backup** (`*_backup`) vẫn còn trên ổ C:\ — khuyến nghị user giữ 3-7 ngày để theo dõi ổn định trước khi xóa
5. 📝 Ghi nhận vào `project_progress.json` nếu đang trong dự án Trinity

### Bước 5.4: Dọn dẹp backup (SAU KHI ĐÃ ỔN ĐỊNH)

> [!NOTE]
> Chỉ thực hiện khi user xác nhận ứng dụng đã hoạt động ổn định ít nhất vài ngày.

```powershell
# Xóa backup khi đã ổn định
Remove-Item "<SOURCE_BINARIES>_backup" -Recurse -Force
Remove-Item "<SOURCE_DATA>_backup" -Recurse -Force
Write-Host "[🎉 HOÀN TẤT] Không gian ổ C:\ đã được giải phóng!" -ForegroundColor Green
```

---

## 🔄 QUY TRÌNH ROLLBACK (KHI GẶP SỰ CỐ)

Nếu ứng dụng không hoạt động sau di dời:

```powershell
# 1. Dừng dịch vụ/tiến trình
Stop-Service -Name "<TÊN_DỊCH_VỤ>" -Force -ErrorAction SilentlyContinue
taskkill /F /IM "<TÊN_ỨNG_DỤNG>.exe" 2>$null

# 2. Xóa Junction Points
cmd.exe /c rmdir "<SOURCE_BINARIES>"
cmd.exe /c rmdir "<SOURCE_DATA>"

# 3. Khôi phục từ backup
Rename-Item "<SOURCE_BINARIES>_backup" "<SOURCE_BINARIES>"
Rename-Item "<SOURCE_DATA>_backup" "<SOURCE_DATA>"

# 4. Khởi động lại dịch vụ
Start-Service -Name "<TÊN_DỊCH_VỤ>"
Write-Host "[🔙 ROLLBACK] Hệ thống đã khôi phục về trạng thái ban đầu." -ForegroundColor Yellow
```

> [!IMPORTANT]
> `rmdir` trên Junction Point chỉ xóa liên kết, KHÔNG xóa dữ liệu thực tế trên ổ đích. Dữ liệu sẽ an toàn.

---

## 📊 CHECKLIST TỔNG KẾT

| # | Bước | Trạng thái |
|---|------|-----------|
| 1 | Lập bản đồ vết chân ứng dụng | ⬜ |
| 2 | Dừng tất cả tiến trình & dịch vụ | ⬜ |
| 3 | Tạo cấu trúc thư mục đích | ⬜ |
| 4 | Robocopy tệp thực thi | ⬜ |
| 5 | Robocopy dữ liệu trạng thái | ⬜ |
| 6 | Kiểm định toàn vẹn dữ liệu | ⬜ |
| 7 | Đổi tên thư mục gốc (backup) | ⬜ |
| 8 | Tạo Directory Junctions | ⬜ |
| 9 | Xác nhận Junctions hoạt động | ⬜ |
| 10 | Khởi động lại ứng dụng | ⬜ |
| 11 | Kiểm chứng hoạt động bình thường | ⬜ |
| 12 | (Sau 3-7 ngày) Dọn dẹp backup | ⬜ |
