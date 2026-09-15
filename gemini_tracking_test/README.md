# Gemini Visual Tracking Test (`gemini_tracking_test`)

Dự án kiểm thử khả năng theo dõi đối tượng video (Multi-Object Tracking - MOT) bằng mô hình Deep Learning YOLO kết hợp thuật toán liên kết chuyển động (ByteTrack / BoT-SORT).

---

## 1. Cấu trúc dự án

```text
gemini_tracking_test/
├── configs/
│   └── tracker_config.yaml      # Tham số detector & tracker
├── data/
│   └── test_clip/               # Clip video mẫu (60 frame ảnh)
├── src/
│   ├── tracker.py               # Engine tracking YOLO + ByteTrack
│   ├── visualizer.py            # Vẽ HUD, Bounding Box, Trajectory & xuất Video
│   └── metrics.py               # Thống kê thời gian sống của track & ID
├── outputs/
│   ├── tracks_mot.txt           # File kết quả định dạng chuẩn MOT 1.1
│   ├── tracking_result.mp4      # Video kết quả tracking hoàn chỉnh
│   ├── tracking_grid.jpg        # Ảnh collage 4 thời điểm chính trong clip
│   └── metrics_summary.json     # Thống kê chi tiết
├── run_tracking.py              # Script chạy test 1-click
└── README.md                    # Tài liệu hướng dẫn
```

---

## 2. Nguyên lý hoạt động

1. **Detection (Phát hiện vật thể)**:
   - Mô hình `YOLO` quét từng frame ảnh ở độ phân giải 960px.
   - Nhận diện các lớp phương tiện 4 bánh COCO: `car`, `bus`, `truck`.
2. **Data Association (Nối track qua thời gian)**:
   - Sử dụng **ByteTrack**: Thuật toán liên kết 2 giai đoạn (Two-Stage Association).
   - Giai đoạn 1: Nối các bounding box có độ tin cậy cao với các track hiện có qua Kalman Filter và IoU matching.
   - Giai đoạn 2: Tận dụng các bounding box có độ tin cậy thấp (thường do vật thể bị che khuất hoặc mờ) để khôi phục track cũ, tránh bị đứt ID.
3. **Visualization**:
   - Vẽ khung viền Bounding Box theo bảng màu cố định riêng cho từng Track ID.
   - Vẽ dải vệt quỹ đạo chuyển động (trajectory trail) bám theo tâm xe.
   - Đánh dấu trạng thái HUD trên đầu video.

---

## 3. Cách chạy thử nghiệm

Chạy trực tiếp từ thư mục gốc của project:

```bash
python3 gemini_tracking_test/run_tracking.py
```

---

## 4. Kết quả đầu ra

Sau khi chạy, các artifact sau sẽ được tạo trong `gemini_tracking_test/outputs/`:
- **`tracking_result.mp4`**: Video hoàn chỉnh xem trực tiếp quỹ đạo và ID xe.
- **`tracking_grid.jpg`**: Ảnh tổng hợp 4 frame chính (f:1, f:20, f:40, f:60).
- **`tracks_mot.txt`**: Tệp nhãn chuẩn MOT 1.1 để đánh giá hoặc import vào CVAT.
- **`metrics_summary.json`**: Thống kê số lượng frame, thời gian sống của từng ID.
