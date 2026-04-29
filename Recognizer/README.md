# Recognizer

Project nay dem so ngon tay bang webcam va co the gui ky tu `1..5` sang STM32 qua serial.

## Cau truc

- `main.py`: entry point de chay webcam va gui du lieu serial.
- `recognizer/config.py`: cau hinh chung va khoi tao MediaPipe.
- `recognizer/detection.py`: phat hien landmarks cua ban tay.
- `recognizer/counting.py`: dem so ngon tay dang gio len.
- `recognizer/apps.py`: luong webcam va overlay trang thai serial.
- `recognizer/serial_sender.py`: loc ket qua on dinh va gui sang STM32.

## Cai dat

```bash
pip install -r requirements.txt
```

Neu can cai tung goi rieng:

```bash
pip install opencv-python mediapipe==0.10.14 numpy matplotlib pyserial
```

## Liet ke cong serial

```bash
python main.py --list-ports
```

## Chay chi de nhan dien

```bash
python main.py
python main.py --camera-index 0
```

## Chay va gui so sang STM32

```bash
python main.py --serial-port COM5
python main.py --serial-port COM5 --baudrate 115200 --stable-frames 4
```

Ung dung chi gui cac gia tri hop le `1..5`. Gia tri phai on dinh lien tiep mot vai frame truoc khi gui de tranh nhap nhay.

Nhan `Esc` de thoat cua so webcam.
