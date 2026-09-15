# Báo cáo Ngày 3 — Tracking Annotation

Họ tên / nhóm: **Tống Thành Danh — 2A202602299**  
Ngày: **15/09/2026**

> Báo cáo này tổng hợp evidence kỹ thuật hiện có. Các mục thời gian không có log và phần kiểm chéo đã được ghi đúng trạng thái, không suy đoán hoặc dựng dữ liệu.

---

## 1. Quá trình gán nhãn


| Mục                               | Giá trị                                                                             |
| --------------------------------- | ----------------------------------------------------------------------------------- |
| Công cụ                           | CVAT Local 2.74.1                                                                   |
| Thời gian gán `clip_02` (warm-up) | 1 hour                                                                              |
| Thời gian gán `clip_01`           | 4 hour                                                                              |
| Số track đã vẽ trong `clip_01`    | 8 track, 603 bbox nhìn thấy                                                         |
| Số keyframe trung bình mỗi track  | 76,1 shape/track nếu tính 603 bbox và 6 marker `outside`; 75,4 bbox nhìn thấy/track |


Ba tình huống khó nhất và cách xử lý:

1. `clip_01`, frame 107–109, ID 6: minivan bị xe buýt che phần thân dưới. Giữ cùng ID, bật occluded và khoanh phần nhìn thấy.
2. `clip_01`, frame 125, ID 4: xe buýt lớn đổi tỉ lệ nhanh. Thêm keyframe và siết bbox theo biên xe thay vì để nội suy trôi.
3. `clip_02`, frame 8–10, ID 3: sedan trắng còn một phần nhỏ ở rìa. Kéo dài cùng track và đặt `outside` ở frame 11.

## 2. Tự kiểm và kiểm chéo

Ba lượt tua đã thực hiện trên toàn bộ 190 frame của `clip_01` và 60 frame của `clip_02`:

- Lượt 1 — ID: kiểm tra quỹ đạo từng xe qua vùng giao cắt/occlusion; bản cuối so với gold có `IDSW = 0`, không có track gold bị bỏ sót hoặc phân mảnh.
- Lượt 2 — frame đầu/cuối: sửa điểm kết thúc sớm của `clip_02` ID 3; kiểm tra các xe chạm rìa và marker `outside`. Evaluation vẫn ghi nhận một số bất đồng quy ước với gold ở ID 4–8 và được giữ lại để giải thích bằng ảnh.
- Lượt 3 — frame giữa: thêm keyframe theo từng frame ở đoạn đổi hướng, đổi tỉ lệ và occlusion; siết bbox ở các đoạn như frame 107–109 và 125.

Kiểm chéo độc lập: **không thực hiện, bỏ qua theo yêu cầu của học viên**. Không tạo `reports/review_partner.md`, không khai reviewer hoặc finding giả. Vì vậy tiêu chí kiểm chéo 10 điểm không có evidence để chấm.

Validator cuối:

- `clip_01`: 603 bbox, 8 track, 0 lỗi, 1 cảnh báo xe đứng yên (ID 1, frame 1–15; đã kiểm tra là vật thể thật).
- `clip_02`: 239 bbox, 6 track, 0 lỗi, 2 cảnh báo xe đứng yên (ID 1–2, frame 1–15; đã kiểm tra là vật thể thật).

## 3. Pre-gold lock và chấm trước/sau rework


| Evidence                                             | Giá trị                                                            |
| ---------------------------------------------------- | ------------------------------------------------------------------ |
| SHA-256 từ `evidence/pre-gold/clip_01/manifest.json` | `274db7fc966b520b1eb40195d145fb8119f14b040df60eeaf09d460e74afed56` |
| Thời điểm khóa                                       | `2026-09-15T05:43:09.565319+00:00` (`12:43:09 +07`)                |
| Số row / frame / track trước khi mở reference        | 581 / 190 / 8                                                      |



|              | HOTA  | DetA  | AssA  | LocA  | IDF1  | MOTA  | MOTP  | FP  | FN  | IDSW |
| ------------ | -----: | -----: | -----: | -----: | -----: | -----: | -----: | ---: | ---: | ----: |
| Bản pre-gold | 0,737 | 0,703 | 0,780 | 0,812 | 0,941 | 0,881 | 0,780 | 38  | 30  | 0    |
| Sau rework   | 0,811 | 0,785 | 0,846 | 0,872 | 0,949 | 0,895 | 0,861 | 45  | 15  | 0    |


Qua cổng (`IDF1 >= 0,80`, `MOTA >= 0,75`, `MOTP >= 0,70`): **có**.

Rework hình học và biên track đã hoàn tất trong vòng tự kiểm trước khi nhận gold; sau khi có gold không sửa nhãn chỉ để tối ưu metric.


| Loại lỗi                | Frame          | ID  | Đã xử lý thế nào                                              |
| ----------------------- | -------------- | --- | ------------------------------------------------------------- |
| Bbox trôi/occlusion     | 107–109        | 6   | Siết bbox theo phần minivan nhìn thấy, giữ ID và cờ occluded. |
| Bbox đổi tỉ lệ nhanh    | 125            | 4   | Thêm keyframe, căn lại biên xe buýt.                          |
| Kết thúc track sớm      | `clip_02` 8–10 | 3   | Kéo dài track đến frame nhìn thấy cuối; `outside` ở frame 11. |
| Xe còn thấy ở cuối clip | 185–190        | 1   | Giữ cùng ID đến frame cuối, không kết thúc ở frame 184.       |


Sau khi chấm, diagnostic còn chỉ ra 7 đoạn khác quy ước biên track (ID 4–8) và 7 bbox có IoU 0,50–0,59. Hai ví dụ đã soi ảnh là frame 107, nơi gold mở bbox xuống vùng bị che, và frame 125, nơi biên trái/gương xe được xử lý khác nhau. Đây được ghi nhận thay vì sửa mù theo reference.

**Cảnh báo provenance:** thời gian ghi của hai output model cũ (`12:42:23` và `12:42:37 +07`) sớm hơn manifest pre-gold (`12:43:09 +07`) khoảng 46 và 32 giây. Các file cũ được giữ nguyên làm evidence; lượt notebook Google Colab mô tả ở mục 4 được chạy lại sau khi annotation đã khóa. Không dùng mốc chạy lại để viết lại lịch sử.

## 4. Kết quả model: ByteTrack control vs ReID treatment

Notebook gốc `notebooks/day3_tracking_yolo_bytetrack.ipynb` đã được upload lên Google Colab, chạy tuần tự trên **GPU T4**, `RUN_EXPERIMENT=False`.


| Mục                                | Giá trị                                                                |
| ---------------------------------- | ---------------------------------------------------------------------- |
| Python / ultralytics / torch / lap | `3.13.15 / 8.4.145 / 2.11.0+cu128 / 0.5.13`                            |
| weights / hai tracker              | `yolo26n.pt` / `bytetrack.yaml` / `configs/trackers/botsort-reid.yaml` |
| conf / IoU / imgsz / classes       | `0.25 / 0.70 / 960 / [2, 5, 7]`                                        |
| device                             | Google Colab `GPU T4`, cấu hình `device="0"`                           |
| Output                             | ByteTrack: 607 bbox/16 track; BoT-SORT + ReID: 638 bbox/16 track       |



| So sánh                   | HOTA  | DetA  | AssA  | LocA  | IDF1  | MOTA  | MOTP  | FP  | FN  | IDSW |
| ------------------------- | -----: | -----: | -----: | -----: | -----: | -----: | -----: | ---: | ---: | ----: |
| bạn vs gold               | 0,811 | 0,785 | 0,846 | 0,872 | 0,949 | 0,895 | 0,861 | 45  | 15  | 0    |
| ByteTrack control vs gold | 0,709 | 0,649 | 0,776 | 0,846 | 0,875 | 0,749 | 0,823 | 88  | 54  | 2    |
| BoT-SORT + ReID vs gold   | 0,763 | 0,711 | 0,820 | 0,872 | 0,900 | 0,792 | 0,860 | 91  | 26  | 2    |
| ReID vs bạn               | 0,770 | 0,718 | 0,827 | 0,893 | 0,891 | 0,781 | 0,883 | 82  | 47  | 3    |


## 5. Phân tích — năm câu hỏi

**1. MOTA của bạn cao hơn hay thấp hơn IDF1? Nếu MOTA cao mà IDF1 thấp thì điều đó nói gì, và vì sao MOTA không phạt nặng lỗi ID?**

MOTA của bản cuối (0,895) **thấp hơn** IDF1 (0,949). Bản cuối không có ID switch; phần chênh chủ yếu đến từ 45 FP và 15 FN. Nếu một bài có MOTA cao nhưng IDF1 thấp, detector có thể vẫn bao phủ tốt nhưng association/ID sai. MOTA tính theo `(FN + FP + IDSW) / GT`, nên một lần đổi ID chỉ cộng một lỗi tại điểm switch; IDF1 đo tính nhất quán định danh trên toàn quãng đời nên nhạy hơn với track bị tách hoặc gán sai kéo dài.

**2. ByteTrack control và BoT-SORT + ReID treatment khác nhau thế nào ở IDF1, AssA và IDSW?**

Treatment tăng IDF1 từ 0,875 lên 0,900 (+0,025) và AssA từ 0,776 lên 0,820 (+0,044); IDSW vẫn bằng 2. ByteTrack đổi ID ở frame 59 (gold ID 4) và 94 (gold ID 5), còn treatment đổi ở frame 87 (gold ID 5) và 113 (gold ID 6). Treatment cải thiện association tổng thể nhưng không loại bỏ phân mảnh. Đây là so sánh hai hệ thống, không cô lập causal effect của ReID vì ByteTrack và BoT-SORT khác implementation/association logic ngoài cue appearance.

**3. DetA, FP và FN đổi thế nào? Lỗi còn lại là detector hay association?**

DetA tăng từ 0,649 lên 0,711. FN giảm mạnh từ 54 xuống 26, nhưng FP tăng từ 88 lên 91. Treatment giữ được nhiều detection thật hơn nhưng cũng duy trì một số track thừa. Lỗi còn lại gồm cả detection (91 FP, 26 FN) và association (2 IDSW, ba track gold bị phân mảnh), không thể quy hết cho ReID.

**4. Một chỗ bạn đúng và ReID sai (frame, ID, vì sao):**

Ở chuỗi frame 106–121, treatment sinh track 27 không khớp track gold nào (16 frame), trong khi annotation tay không duy trì bbox đó. Ngoài ra, annotation giữ gold ID 6 liên tục qua vùng occlusion, còn treatment đổi từ ID 24 sang ID 31 tại frame 113. Evidence gold và quỹ đạo cho thấy annotation đúng ở tình huống này.

**5. Một chỗ ReID làm bạn xem lại annotation, hoặc evidence cho thấy model sai:**

Frame 107–109, ID 6 được xem lại vì treatment và annotation bất đồng. Ảnh gốc cho thấy minivan chỉ lộ phần trên sau xe buýt; annotation dùng bbox visible-only và giữ ID 6, trong khi treatment bị phân mảnh (24 → 28 → 31 khi so với annotation). Evaluation với gold cũng cho thấy treatment chỉ phủ 44/56 frame của track này. Vì vậy bất đồng này là evidence model yếu ở occlusion, không phải lý do để sửa annotation theo model.

## 6. Nếu phải gán thêm 10 clip nữa

Quy trình đề xuất là đặt keyframe dày ngay tại vùng occlusion/đổi tỉ lệ, kiểm frame đầu-cuối bằng cửa sổ ±2 frame, rồi chạy validator và tua ba lượt trước khi khóa pre-gold. `GUIDELINE_MINI.md` đã được bổ sung quy ước visible-only, ngưỡng occlusion 25 frame, xử lý xe đứng yên và quy tắc không dùng model/reference làm đáp án. Với nhiều clip, nên ghi log thời gian và finding ngay trong lúc làm để report không phải suy lại từ timestamp.

## 7. Tệp đã nộp / trạng thái artifact

- [x] `annotations/clip_01/gt.txt`
- [x] `annotations/clip_02/gt.txt`
- [x] `evidence/pre-gold/clip_01/gt.txt` và `manifest.json`
- [x] `GUIDELINE_MINI.md` đã điền
- [x] `outputs/eval_vs_gold.json`
- [x] `outputs/model_bytetrack_clip_01.txt`
- [x] `outputs/model_reid_clip_01.txt`
- [x] `outputs/model_run_config.json` (được chuẩn hóa lại theo lượt Colab)
- [x] `outputs/eval_bytetrack_vs_gold.json`, `outputs/eval_reid_vs_gold.json`, `outputs/eval_reid_vs_me.json`
- [ ] `reports/review_partner.md` — bỏ qua theo yêu cầu, không có peer review độc lập
- [x] `reports/REPORT.md`

Phạm vi hỗ trợ AI cần khai báo: trợ lý đã hỗ trợ thao tác browser/CVAT, rà soát frame, điều chỉnh bbox/ID ở giai đoạn trước, export, validator, evaluation và soạn báo cáo từ evidence. Việc hỗ trợ quyết định bbox/ID vượt quá ranh giới trợ lý được mô tả trong `RULES.md`; bài này không được trình bày là annotation hoàn toàn độc lập hay peer review độc lập.