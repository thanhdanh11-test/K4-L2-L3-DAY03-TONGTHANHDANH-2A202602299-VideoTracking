# Mini annotation guideline — Ngày 3 (tracking)

Nhóm / tên: **Tống Thành Danh — 2A202602299**  
Clip: `clip_01`, `clip_02`

---

## 1. Phạm vi: gán cái gì, không gán cái gì

Một lớp duy nhất: **`vehicle`** — xe bốn bánh (xe con, van, xe buýt, xe tải).

| Gán | Không gán |
| --- | --- |
| xe con, SUV, taxi, xe bán tải | người đi bộ |
| van, minivan | xe đạp |
| xe buýt, minibus | **xe máy / mô tô** |
| xe tải, xe đầu kéo | xe trong ảnh quảng cáo, trong gương, dưới bóng nước |

Bổ sung của nhóm:

- Chỉ bắt đầu track khi phần nhìn thấy đủ để xác định đó là xe bốn bánh; không suy đoán từ vài điểm ảnh không rõ loại.
- Xe đang đỗ vẫn được gán nếu là xe thật trong cảnh. Cảnh báo “track gần như đứng im” của validator phải được kiểm tra bằng mắt, không tự động xóa.
- Không dùng kết quả tracker hay teaching reference làm đáp án để quyết định bbox/ID.

## 2. Luật ID — phần quan trọng nhất

| Tình huống | Luật của nhóm | Vì sao |
| --- | --- | --- |
| Xe bị che một phần rồi hiện lại | Giữ nguyên ID nếu bị che dưới **25 frame** (2 giây ở 12,5 fps) và quỹ đạo/ngoại hình vẫn đủ liên tục. | Tránh tách một xe thành nhiều track chỉ vì occlusion ngắn. |
| Xe bị che lâu hơn 25 frame | So lại hướng chuyển động, màu, loại xe và vị trí xuất hiện; chỉ giữ ID khi có đủ bằng chứng liên tục, nếu không tạo ID mới. | Sau occlusion dài, nguy cơ gán nhầm sang xe giống nhau tăng mạnh. |
| Xe rời khung hình rồi quay lại | Tạo **track mới**. | Khi đã rời khung, không còn bằng chứng chuyển động liên tục trong cảnh. |
| Hai xe cắt nhau / chồng lên nhau | Theo từng xe trước và sau vùng giao cắt bằng hướng chuyển động, kích thước, màu và chi tiết đặc trưng; không đổi ID chỉ vì bbox giao nhau. | IoU tại một frame không đủ để kết luận hai xe đổi danh tính. |

## 3. Luật bbox

| Tình huống | Luật của nhóm |
| --- | --- |
| Xe bị cắt bởi rìa ảnh | Bbox chạm đúng rìa, không đoán phần ngoài ảnh. |
| Xe bị xe khác che một phần | Bbox ôm phần **nhìn thấy được**, đánh dấu `occluded`; không mở rộng qua vật che để đoán toàn thân xe. |
| Xe vừa xuất hiện, còn rất nhỏ / rất mờ | Bắt đầu ở frame đầu tiên xác định chắc là xe bốn bánh; ngưỡng thực hành là thấy được thân/biên xe, không dùng ngưỡng pixel cứng. Có thể kiểm tra thêm 1–2 frame kế tiếp rồi quay lại đặt điểm bắt đầu. |
| Xe đang đỗ, không di chuyển | Vẫn giữ một ID liên tục; bbox bám sát xe và kiểm tra cảnh báo đứng im của validator bằng ảnh gốc. |
| Keyframe đặt dày ở đâu | Đặt dày quanh lúc xe vào/ra khung, đổi hướng hoặc tỉ lệ nhanh, bị che/mở che, và khi hai xe chồng nhau. Bản cuối dùng keyframe theo từng frame để tránh nội suy trôi. |

## 4. Ít nhất ba ca mơ hồ đã gặp thật

### Ca 1

- Clip / frame / ID: `clip_01`, MOT frame 107–109 (CVAT 106–108), ID 6.
- Tình huống: minivan chỉ lộ phần trên khi đi sau xe buýt; phần thân dưới bị che.
- Quyết định: giữ ID 6, đánh dấu occluded và chỉ khoanh phần nhìn thấy.
- Lý do: quỹ đạo trước/sau liên tục; mở bbox xuống sau xe buýt sẽ đoán phần không quan sát được.

### Ca 2

- Clip / frame / ID: `clip_01`, MOT frame 125 (CVAT 124), ID 4.
- Tình huống: xe buýt lớn thay đổi tỉ lệ nhanh và có phần gương/biên xe dễ nhầm với nền.
- Quyết định: thêm keyframe, ôm biên phần xe thực sự nhìn thấy và giữ nguyên ID 4.
- Lý do: nội suy từ keyframe xa làm bbox trôi; đây là thay đổi hình học chứ không phải xe mới.

### Ca 3

- Clip / frame / ID: `clip_02`, MOT frame 8–10 (CVAT 7–9), ID 3.
- Tình huống: sedan trắng còn xuất hiện rất ít ở rìa ảnh sau điểm kết thúc cũ.
- Quyết định: kéo dài cùng ID 3 đến frame nhìn thấy cuối cùng và đặt `outside` ở MOT frame 11.
- Lý do: xe chưa rời hẳn khung; kết thúc sớm sẽ làm mất ba bbox và sai biên track.

### Ca 4

- Clip / frame / ID: `clip_01`, MOT frame 185–190 (CVAT 184–189), ID 1.
- Tình huống: xe bị che một phần ở cuối clip nhưng vẫn còn nhìn thấy.
- Quyết định: giữ cùng ID 1 đến hết clip, đánh dấu occluded ở frame cần thiết.
- Lý do: xe không rời khung và không có bằng chứng về một xe mới.

## 5. Sửa gì sau khi chấm với gold và sau khi tự kiểm

- Làm rõ quy ước **visible-only** khi occlusion: bbox chỉ ôm phần quan sát được, vì gold có thể dùng quy ước rộng hơn ở một số frame như 107–109.
- Khi quyết định frame đầu/cuối, kiểm tra ít nhất hai frame trước và sau. Evaluation còn chỉ ra các bất đồng quy ước ở ID 4, 5, 6, 7 và 8; không sửa chỉ để khớp gold nếu ảnh gốc vẫn cho thấy xe.
- Thêm quy tắc xử lý xe đứng yên để phân biệt xe thật đang đỗ với bbox treo.
- Không có vòng kiểm chéo độc lập theo yêu cầu của học viên; không tạo reviewer hay finding giả.
