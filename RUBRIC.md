# Rubric Ngày 3 - Tracking Annotation (100 điểm)

## Thành phần bắt buộc và bonus

Toàn bộ tám tiêu chí trong bảng dưới là **bắt buộc** và cộng thành 100 điểm.
Lab này không có điểm bonus: phần stretch chỉ để mở rộng hiểu biết, không dùng
để bù thiếu artifact bắt buộc hoặc nâng tổng điểm vượt 100. Nội dung được chấm
là evidence trong repo và khả năng giải thích bằng frame/ID; không chấm việc
trình diễn hoặc số giờ làm thêm.

| Tiêu chí | Bằng chứng | Điểm |
| --- | --- | ---: |
| Định dạng và tính hợp lệ | `check_mot_labels.py` chạy 0 lỗi trên cả hai clip; cột `track_id` có thật (export MOT 1.1, không phải YOLO) | 10 |
| Độ bao phủ | mọi xe bốn bánh trong gold đều có track tương ứng; không gán người/xe máy/xe đạp | 15 |
| **Giữ đúng ID** | `AssA` và `IDF1`: xe bị che rồi hiện lại vẫn một ID; hai xe cắt nhau không đổi ID cho nhau; không tách một xe thành nhiều ID | 25 |
| Biên của track | `outside` bấm đúng frame xe rời khung; không bbox treo; track bắt đầu đúng lúc xe xác định được | 10 |
| Hình học bbox | `LocA` / `MOTP`: bbox sát phần nhìn thấy, keyframe đủ dày ở chỗ xe đổi hướng | 10 |
| Mini guideline | `GUIDELINE_MINI.md` nêu luật ID (che bao lâu thì giữ ID, ra khung rồi vào lại, xe quá nhỏ) và ít nhất ba ca mơ hồ có lý do | 10 |
| Kiểm chéo | `reports/review_partner.md`: mỗi lỗi ghi rõ frame / ID / lỗi gì / sửa thế nào, kèm reviewer checklist đã điền | 10 |
| Pipeline model và phân tích | notebook chạy được, có `model_run_config.json`, đủ control ByteTrack và treatment ReID, đọc IDF1/AssA/IDSW theo frame evidence, trả lời năm câu hỏi trong `reports/REPORT.md` | 10 |

## Cổng bắt buộc

- **Export sai định dạng làm mất `track_id`** (nộp nhãn YOLO, hoặc mọi dòng cùng một ID): tối đa 40 điểm — bài hôm nay chính là cột đó.
- Không chạy `check_mot_labels.py`, hoặc nộp file còn lỗi định dạng: tối đa 49 điểm.
- Không có `outputs/eval_vs_gold.json`: tối đa 69 điểm.
- Thiếu clip warm-up `clip_02`: trừ 5 điểm.
- **Sửa gold labels**, sửa `data/clips/clip_02/gt/gt.txt`, hoặc truy ngược dataset nguồn để lấy nhãn: bài không được chấm trong pilot; Lab Coach báo người thiết kế lab để xử lý theo quy định đã công bố.
- Thiếu `evidence/pre-gold/clip_01/gt.txt` hoặc manifest/hash không khớp: không có bằng chứng cho vòng annotation độc lập.
- Chạy model **trước** khi khóa pre-gold rồi sửa nhãn theo model: coi như không có phần annotation. Thứ tự tự-gán-trước là bắt buộc.

## Mức chất lượng annotation (nhãn của bạn vs gold)

| Mức | HOTA | IDF1 | MOTA | LocA/MOTP | Diễn giải |
| --- | ---: | ---: | ---: | ---: | --- |
| Xuất sắc | >= 0.80 | >= 0.90 | >= 0.90 | >= 0.80 | ID gần như không sai, bbox rất sát |
| Đạt | >= 0.65 | >= 0.80 | >= 0.75 | >= 0.70 | qua learning gate của bài lab |
| Cần rework | < 0.65 | < 0.80 | < 0.75 | < 0.70 | đọc danh sách lỗi trong JSON, sửa rồi chạy lại |

Cổng qua bài là **IDF1 >= 0.80 và MOTA >= 0.75 và MOTP >= 0.70**. HOTA là điểm tổng
để xếp mức, không phải điều kiện cổng. Đây là learning gate để kích hoạt rework,
không phải ngưỡng production hoặc chứng nhận dữ liệu sẵn sàng train.

## Cách đọc điểm cho đúng

- **Rework không bị trừ điểm.** Vòng sửa nhãn sau khi đọc báo cáo lỗi là phần
  được dạy, không phải phần bị phạt. Báo cáo nên ghi rõ: điểm trước rework, sửa
  gì, điểm sau rework. Một bài đi từ 0.71 lên 0.86 và giải thích được mình sửa
  gì thì tốt hơn một bài 0.87 không giải thích được gì.
- **Điểm model thấp không bị trừ.** `clip_01` chỉ có 190 frame và model chạy
  zero-shot trên COCO, không được train trên dữ liệu này. Việc của bạn là *giải
  thích* con số, không phải làm nó đẹp.
- **BoT-SORT + ReID không cần thắng ByteTrack để có điểm.** Điểm nằm ở thí nghiệm
  công bằng: giữ detector input cố định, đọc identity metrics, và giải thích bằng
  frame/ID treatment tốt hơn, tệ hơn hoặc không đổi. Đây không phải causal
  ablation của ReID vì hai tracker implementation khác.
- **MOTA cao mà IDF1 thấp là một phát hiện, không phải một sự cố.** Nhận ra và
  giải thích được khoảng cách đó là một phần của mục "phân tích".
- **Teaching reference có thể được challenge bằng evidence.** Finding phải có
  frame, ID, rule và ảnh/đối chiếu; Lab Coach ghi closure thay vì sửa âm thầm.
