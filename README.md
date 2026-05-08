# Nhận diện ngón tay và hiển thị LED 7 thanh

Project này gồm 2 phần:

- Code C chạy trên STM32F429 để nhận dữ liệu serial và hiển thị số lên LED 7 thanh.
- Code Python chạy trên PC để nhận diện số ngón tay bằng webcam và gửi số `1..5` sang STM32.

## Luồng hoạt động

1. Webcam nhận diện số ngón tay.
2. Python ổn định kết quả trong vài frame.
3. Python gửi ký tự `1..5` qua serial.
4. STM32 nhận ký tự đó và hiển thị lên LED 7 thanh.

## Có phải chạy cả C và Python không?

Có, nếu bạn muốn chạy đúng bài toán hoàn chỉnh.

- Phần C chỉ chạy trên STM32 để điều khiển LED 7 thanh.
- Phần Python chạy trên máy tính để lấy ảnh từ webcam và gửi số sang STM32.

Nếu bạn chỉ muốn:

- test riêng STM32
- hoặc hiện số thủ công từ UART

thì không cần chạy Python.

## Chuẩn bị

- Board STM32F429
- LED 7 thanh
- Webcam trên PC
- Kết nối serial giữa PC và STM32
- Python environment trong `my_env`

## Nối dây

### Serial

Firmware hiện tại dùng `USART3`:

- `PD8 = TX`
- `PD9 = RX`
- `GND = GND`

Nếu dùng USB-UART:

- `TX USB-UART -> PD9`
- `RX USB-UART -> PD8`
- `GND USB-UART -> GND STM32`

### LED 7 thanh

Code hiện tại map như sau:

- `PE8 -> a`
- `PE9 -> b`
- `PE10 -> c`
- `PE11 -> d`
- `PE12 -> e`
- `PE13 -> f`
- `PE14 -> g`
- `PE15 -> dp`

Chân chọn digit:

- `PG2 -> digit trái`
- `PG3 -> digit phải`

Nếu bạn chỉ dùng `1 LED 7 thanh 1 số`, có thể:

- nối `a..g,dp` vào `PE8..PE15`
- dùng `PG3` cho chân `COM` qua transistor
- bỏ qua `PG2`

Lưu ý:

- Mỗi segment nên qua điện trở `220R` đến `330R`
- Code đang viết cho LED `common cathode`

## Nạp firmware STM32

Nạp file:
- `Debug/TEST_NE.elf`

hoặc build lại trong STM32CubeIDE.

## Cài Python

Từ thư mục project:

```powershell
.\my_env\Scripts\pip.exe install -r .\Recognizer\requirements.txt
```

## Tìm cổng COM

```powershell
.\my_env\Scripts\python.exe .\Recognizer\main.py --list-ports
```

Ví dụ kết quả:

```text
COM5 - USB Serial Device
```

## Chạy chương trình

### Chỉ nhận diện bằng webcam

```powershell
.\my_env\Scripts\python.exe .\Recognizer\main.py
```

Hoặc chọn camera:

```powershell
.\my_env\Scripts\python.exe .\Recognizer\main.py --camera-index 0
```

### Nhận diện và gửi số sang STM32

```powershell
.\my_env\Scripts\python.exe .\Recognizer\main.py --serial-port COM5
```

Có thể thêm tham số:

```powershell
.\my_env\Scripts\python.exe .\Recognizer\main.py --serial-port COM5 --camera-index 0 --baudrate 115200 --stable-frames 4
```

## Ý nghĩa các tham số

- `--serial-port COM5`: cổng COM nối với STM32
- `--camera-index 0`: chọn webcam
- `--baudrate 115200`: tốc độ serial, phải khớp với firmware
- `--stable-frames 4`: số frame liên tiếp cần ổn định trước khi gửi

## Hành vi hiện tại

- Python chỉ gửi các giá trị hợp lệ `1..5`
- Nếu nhận diện không ổn định, chương trình sẽ chờ thêm frame
- STM32 giữ lại số cuối cùng đã nhận và hiển thị trên LED

## File chính

### Firmware C

- [Core/Src/main.c](/D:/AI/Embedded_AI/Embedded_Prj/Core/Src/main.c)
- [Core/Src/7seg.c](/D:/AI/Embedded_AI/Embedded_Prj/Core/Src/7seg.c)

### Python

- [Recognizer/main.py](/D:/AI/Embedded_AI/Embedded_Prj/Recognizer/main.py)
- [Recognizer/recognizer/apps.py](/D:/AI/Embedded_AI/Embedded_Prj/Recognizer/recognizer/apps.py)
- [Recognizer/recognizer/serial_sender.py](/D:/AI/Embedded_AI/Embedded_Prj/Recognizer/recognizer/serial_sender.py)

## Lỗi thường gặp

- `No serial ports found`
  - Chưa cắm board hoặc USB-UART, hoặc driver chưa đúng

- Webcam không mở được
  - Thử `--camera-index 0`, `1`, `2`

- LED không sáng
  - Kiểm tra dây `PE8..PE15`, `PG3`, nguồn chung, transistor và loại LED

- STM32 không nhận số
  - Kiểm tra baudrate `115200`
  - Kiểm tra nối chéo `TX -> RX`, `RX -> TX`
  - Kiểm tra đúng `USART3` trên `PD8/PD9`
