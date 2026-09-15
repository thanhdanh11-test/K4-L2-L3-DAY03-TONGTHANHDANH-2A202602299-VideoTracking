# Hướng dẫn sinh viên - Ngày 3

## 0. Phân bổ thời gian (4 giờ)

| Thời lượng | Hoạt động | Kết quả phải có |
| ---: | --- | --- |
| 0:00-0:15 | Đọc luật gán nhãn, mở CVAT, tạo task cho `clip_02` | task CVAT chạy được |
| 0:15-0:45 | **Warm-up**: gán `clip_02` (60 frame, 6 track), tự chấm ngay với gold có sẵn | `annotations/clip_02/gt.txt`, IDF1 >= 0.80 |
| 0:45-1:30 | **Bài chính, sprint 1**: gán `clip_01`, ưu tiên identity và lưu an toàn | task CVAT đã Save |
| 1:30-1:40 | **Nghỉ 10 phút**: reload task trước khi rời màn hình | track vẫn còn sau reload |
| 1:40-2:15 | **Bài chính, sprint 2**: hoàn tất `clip_01` (190 frame, tối thiểu 6 track hợp lệ) | `annotations/clip_01/gt.txt` |
| 2:15-2:35 | Tự kiểm ba lượt + `check_mot_labels.py` + kiểm chéo với bạn cùng nhóm | `reports/review_partner.md` |
| 2:35-2:45 | **Khóa pre-gold bằng script**, Lab Coach xác nhận hash, rồi mới nhận `gold/clip_01/` | `evidence/pre-gold/clip_01/{gt.txt,manifest.json}` |
| 2:45-3:15 | Chấm với gold, đọc danh sách lỗi, rework, chạy lại | `outputs/eval_vs_gold.json`, qua cổng |
| 3:15-3:45 | Colab: ByteTrack control + BoT-SORT-ReID | 2 file MOT + comparison JSON |
| 3:45-4:00 | Viết báo cáo, commit, push | `reports/REPORT.md` |

Mốc 2:35 là mốc cứng. Teaching reference chỉ được mở sau khi snapshot độc lập
đã tồn tại và hash đã được xác nhận.

---

## 1. Luật gán nhãn

### Gán cái gì

Một lớp duy nhất: **`vehicle`** — mọi xe bốn bánh (xe con, van, xe buýt, xe tải).

Hôm nay không phân loại xe. Ngày 2 hỏi *cái này là xe gì*; hôm nay hỏi *chiếc xe
này ở frame 30 có phải chiếc xe ở frame 10 không*. Gộp về một lớp để bạn dồn toàn
bộ sự chú ý vào `track_id`.

**Không gán**: người đi bộ, xe đạp, **xe máy / mô tô**, biển báo, xe trong ảnh
quảng cáo hay trong gương. Trong clip có xe máy và người đi bộ thật — chúng nằm
ngoài schema. Gán thêm là bbox thừa (FP), bị trừ điểm.

### Bbox đúng

- Bbox ôm sát **phần nhìn thấy được** của xe. Xe bị che một nửa thì bbox ôm nửa nhìn thấy.
- Xe bị cắt khung: bbox chạm đúng rìa ảnh, **không đoán** phần nằm ngoài.
- Mỗi xe một bbox riêng, kể cả khi hai xe chồng lên nhau.
- Xe đang đỗ vẫn là `vehicle` và vẫn cần track suốt thời gian nó trong khung.

### Ba quyết định phải nhất quán — ghi vào `GUIDELINE_MINI.md`

| Tình huống | Quyết định mặc định của lab | Ghi chú |
| --- | --- | --- |
| Xe bị che rồi hiện lại | **giữ nguyên ID cũ** nếu che dưới 2 giây (= 25 frame ở 12.5 fps) | quá 2 giây thì mở track mới |
| Xe rời khung rồi quay lại | **track mới** | đã ra khỏi khung là kết thúc track |
| Xe mới xuất hiện, còn rất nhỏ / mờ | bắt đầu track từ frame **đầu tiên xác định được đó là xe bốn bánh** | ghi lại ngưỡng bạn chọn |

Ba luật này là *mặc định của lab*. Nếu nhóm bạn chọn khác, phải viết rõ trong
`GUIDELINE_MINI.md` và áp dụng nhất quán cho cả clip.

---

## 2. Gán nhãn trong CVAT

### Tạo task

1. Vào [app.cvat.ai](https://app.cvat.ai) (hoặc CVAT tự host), **+ Create new task**.
2. **Name**: `clip_01`.
3. **Labels**: thêm đúng một label tên `vehicle`, kiểu **Rectangle**.
4. **Select files**: upload toàn bộ 190 ảnh trong `data/clips/clip_01/img1/`.
   CVAT xếp frame theo tên tệp, mà tên đã đánh số liên tục nên thứ tự luôn đúng.
5. Submit, mở job.

Làm y hệt với `clip_02` (60 ảnh) cho phần warm-up.

### Vẽ ở chế độ Track — không phải Shape

Chọn Rectangle trên thanh trái, chọn label `vehicle`, rồi bấm **Track** (không
bấm Shape). Chọn nhầm Shape là mất `track_id` và phải làm lại từ đầu.

### Quy trình cho từng xe

Làm **xong hẳn một xe rồi mới sang xe khác**. Nhảy qua nhảy lại giữa các xe là
cách nhanh nhất để tạo ra ID switch.

1. Tua đến frame chiếc xe hiện ra rõ. Vẽ bbox. CVAT cấp một `track_id`.
2. **Trước khi nhảy frame, lướt nhanh xem xe này còn trong khung bao lâu.** "20-30
   frame" chỉ là con số tham khảo cho xe đi đều — xe đi nhanh hoặc sắp ra khỏi
   khung có thể biến mất chỉ sau 8-10 frame. Nhảy 20-30 frame một cách máy móc cho
   loại xe này sẽ nhảy quá điểm nó đã rời khung, và bạn bỏ lỡ luôn track đó.
3. Nhảy về sau (ít hơn nếu xe đi nhanh), sửa bbox cho khít. CVAT tạo **keyframe**
   mới và interpolation lại toàn bộ frame ở giữa.
4. **Tua ngược về giữa hai keyframe** và kiểm tra bbox còn khít không. Đây là bước
   người mới bỏ nhiều nhất, và là chỗ lỗi trốn lâu nhất.
5. Xe rẽ, phanh, hoặc bị che → đặt keyframe dày hơn. Đi thẳng đều → thưa cũng được.
6. Đến frame xe **rời khung**, bấm **outside** (phím `O`). Quên bước này thì CVAT
   tiếp tục vẽ bbox ở chỗ trống cho đến hết clip.
7. Bấm **Save** (phím `Ctrl+S`). CVAT không tự lưu.

Xe bị che rồi hiện lại: **vẫn ID cũ**. Nếu lỡ vẽ thành hai track, bấm **Merge**
(phím `M`), chọn một bbox của track thứ nhất, một bbox của track thứ hai, rồi `M`
lần nữa để chốt.

> **Hai lỗi thao tác dễ mất trắng công sức, không có cảnh báo nào hiện lên:**
>
> - **Phải click trực tiếp lên bbox** để nó "activate" trước khi kéo chỉnh góc.
>   Chọn bbox qua danh sách bên phải (sidebar) *không* đủ để activate — nếu bạn
>   kéo lúc bbox chưa activate, CVAT **kéo trôi cả khung hình (pan)** thay vì
>   thay đổi bbox, và không báo lỗi gì. Nếu thấy cả ảnh bị trôi khi bạn tưởng
>   đang kéo bbox, đó là dấu hiệu.
> - **`Ctrl+S` không phải lúc nào cũng nhận**, nhất là khi focus đang ở một ô
>   nhập liệu hay ở sidebar chứ không phải trên canvas. Đã có trường hợp bấm
>   `Ctrl+S` nhiều lần, rời trang, quay lại thì **toàn bộ nhãn biến mất**. Bấm
>   **thẳng vào biểu tượng đĩa mềm (Save)** trên toolbar thay vì chỉ tin phím
>   tắt, và sau khi lưu, **reload trang job rồi kiểm tra số "Items"/số bbox vẫn
>   còn** trước khi coi như đã an toàn.

### Export

Quay lại **trang Task** (không phải trang Job), bấm **Actions** (góc trên bên phải)
**→ Export task dataset → định dạng `MOT 1.1`**. Sau khi bấm export, job xử lý
hiện ở trang **Requests**; đợi tới 100% rồi tải bằng nút **⋮ → Download**. Nếu
cửa sổ trình duyệt hẹp, menu `Actions` hoặc dropdown chọn định dạng có thể tràn
ra ngoài vùng nhìn thấy — phóng to cửa sổ nếu bấm mà menu như không phản hồi.

Đừng export YOLO. YOLO **bỏ mất `track_id`**, không báo lỗi, không cảnh báo, file
vẫn mở được — và toàn bộ công sức hôm nay biến mất.

Giải nén file tải về, lấy `gt/gt.txt`, đặt vào:

```text
annotations/clip_01/gt.txt
annotations/clip_02/gt.txt
```

Kiểm tra 30 giây ngay sau khi export: mở `gt.txt`, xem **cột thứ hai** — đó là
`track_id`. Số ID khác nhau phải bằng số track bạn đã vẽ.

```bash
cut -d, -f2 annotations/clip_01/gt.txt | sort -un | wc -l
```

---

## 3. Tự kiểm — ba lượt tua, mỗi lượt tìm một thứ

Làm theo thứ tự. Lượt 1 rẻ nhất và bắt được nhiều lỗi nhất.

**Lượt 1 — chỉ nhìn số ID.** Phát nhanh cả clip, mắt chỉ nhìn con số trên bbox.
Số nhấp nháy, đổi số, hiện rồi tắt → có vấn đề.

**Lượt 2 — frame đầu và frame cuối của từng track.** Frame đầu: xe đã thực sự
xuất hiện chưa? Frame cuối: đã bấm `outside` chưa, hay bbox còn treo lơ lửng?

**Lượt 3 — giữa mỗi đoạn dài.** Nhảy vào giữa hai keyframe cách nhau xa nhất.
Khít ở giữa thì phần còn lại gần như chắc chắn ổn.

Ba lượt cho clip 15 giây mất khoảng 10 phút.

### Chạy script kiểm định dạng

```bash
python3 tools/check_mot_labels.py --clip data/clips/clip_01 --tracks annotations/clip_01/gt.txt
```

Script bắt: frame ngoài khoảng, bbox lòi khỏi ảnh, **một ID xuất hiện hai lần trong
cùng một frame**, track đứng im hàng chục frame (dấu hiệu quên `outside`), track
quá ngắn. Chạy đạt **không chứng minh nhãn đúng** — chỉ chứng minh nhãn hợp lệ.

### Xem lại bằng mắt

```bash
python3 tools/visualize_tracks.py --clip data/clips/clip_01 \
    --tracks annotations/clip_01/gt.txt --out outputs/vis_clip_01
```

Ảnh có bbox và số ID được ghi vào `outputs/vis_clip_01/`. Thêm `--video out.mp4`
nếu máy bạn có OpenCV.

---

## 4. Kiểm chéo với bạn cùng nhóm

Hai người gán **cùng một clip**, độc lập, không xem nhãn của nhau. Sau đó đổi file
và chấm nhãn của nhau bằng chính công cụ chấm:

```bash
python3 tools/evaluate_tracking.py --pred annotations/clip_01/gt.txt \
    --gt ../ban-cung-nhom/annotations/clip_01/gt.txt \
    --seqinfo data/clips/clip_01/seqinfo.ini --mode peer
```

`--mode peer` bỏ phần cổng qua bài (ở đây không có ai là "đáp án") và đổi tiêu đề
phần chẩn đoán cho đúng ngữ cảnh: hai bản nhãn lệch nhau, chứ không phải ai sai.

Chỗ hai người khác nhau **thường không phải vì ai kém** — mà vì guideline chưa nói
rõ. Đó là phát hiện giá trị nhất của bước này. Ghi vào `reports/review_partner.md`:

- mỗi lỗi tìm được: **frame nào, ID nào, lỗi gì, sửa thế nào**;
- reviewer checklist đã điền;
- ca nào hai người quyết khác nhau, và luật nào trong `GUIDELINE_MINI.md` còn thiếu.

### Reviewer checklist

- [ ] Số track khớp với số xe đếm được khi xem clip bằng mắt
- [ ] Mọi track có frame đầu và frame cuối hợp lý — không treo, không cắt sớm
- [ ] Không có ID nào xuất hiện hai lần trong cùng một frame
- [ ] Xe bị che rồi hiện lại vẫn giữ nguyên ID
- [ ] Export đúng MOT 1.1; số ID khác nhau khớp với số track
- [ ] Mọi ca không rõ đều được ghi lại trong `GUIDELINE_MINI.md`

---

## 5. Khóa pre-gold, rồi chấm với teaching reference

Trước khi nhận reference, chạy:

```bash
python3 tools/lock_pre_gold.py
```

Phải thấy `ĐÃ KHÓA PRE-GOLD`. Gửi Lab Coach hash được in ra và kiểm tra hai file:

```text
evidence/pre-gold/clip_01/gt.txt
evidence/pre-gold/clip_01/manifest.json
```

Script không cho ghi đè nếu annotation hiện tại khác snapshot đã khóa. Cơ chế này
giữ được bằng chứng trước/sau rõ ràng ngay cả khi commit cuối được tạo sau giờ rework.

Lab Coach phát thư mục `gold/clip_01/` sau khi xác nhận pre-gold lock. Đặt nó vào `gold/` trong repo,
rồi ghi lại metric **trước rework** từ snapshot đã khóa:

```bash
python3 tools/evaluate_tracking.py \
    --pred evidence/pre-gold/clip_01/gt.txt \
    --gt   gold/clip_01/gt.txt \
    --seqinfo data/clips/clip_01/seqinfo.ini \
    --output outputs/eval_pre_gold.json
```

Sửa trong CVAT, export lại `annotations/clip_01/gt.txt`, rồi chạy metric **sau rework**:

```bash
python3 tools/evaluate_tracking.py \
    --pred annotations/clip_01/gt.txt \
    --gt   gold/clip_01/gt.txt \
    --seqinfo data/clips/clip_01/seqinfo.ini \
    --output outputs/eval_vs_gold.json
```

### Đọc các chỉ số

| Chỉ số | Trả lời câu hỏi | Giống gì ở Ngày 2 |
| --- | --- | --- |
| **DetA** | Có tìm ra xe không? | chính là precision/recall của detection |
| **AssA** | Có giữ đúng ID không? | **mới hoàn toàn** — phần riêng của tracking |
| **HOTA** | `sqrt(DetA x AssA)` — điểm tổng | hỏng một trong hai là tụt |
| **LocA / MOTP** | Bbox khít đến đâu | mean IoU của Ngày 2 |
| **IDF1** | Giữ đúng ID trên **toàn bộ quãng đời** của xe | — |
| **MOTA** | Tổng FP + FN + ID switch | — |

**Một điều phải để ý**: MOTA đếm mỗi ID switch đúng **một lần**, nên một track bị
cắt làm đôi chỉ tốn 1 điểm MOTA — MOTA vẫn có thể rất cao (0.95) trong khi nhãn
của bạn sai ID nghiêm trọng. IDF1 và AssA thì phạt đúng nửa quãng đời của track
đó. Nếu thấy **MOTA cao mà IDF1 thấp**, đó chính xác là dấu hiệu lỗi ID, không
phải lỗi bỏ sót. Nhận xét về khoảng cách giữa hai con số này là một câu hỏi trong
báo cáo.

### Cổng qua bài

`IDF1 >= 0.80` **và** `MOTA >= 0.75` **và** `MOTP >= 0.70`.

Chưa đạt thì script đã in sẵn danh sách việc cần làm, chia theo đúng năm loại lỗi
trong slide:

1. **ID switch** — frame nào, track nào nhảy từ ID nào sang ID nào
2. **Tách track** — xe nào bị chia cho nhiều ID → dùng `Merge`
3. **Bbox treo / bbox thừa** — ID nào còn bbox sau khi xe đã rời khung → bấm `outside`
4. **Bbox trôi** — frame nào IoU tụt → thêm keyframe quanh đó
5. **Bỏ sót** — track gold nào bạn chưa gán

Sửa trong CVAT, export lại, chạy lại. Ghi vào báo cáo: điểm trước rework, bạn sửa
gì, điểm sau rework.

---

## 6. Inference model: ByteTrack vs ReID

Chỉ làm sau khi đã qua cổng annotation — **tự gán trước, rồi mới đối chiếu với
model**. Chạy model trước rất dễ khiến bạn tin nhầm vào model.

Mở `notebooks/day3_tracking_yolo_bytetrack.ipynb` trên Google Colab. Ở cell đầu,
sửa `REPO_URL` thành **URL Git thô** của fork public, ví dụ
`https://github.com/ten-cua-ban/Day3-Lab.git` — không copy Markdown dạng
`[tên](URL)`. Notebook sẽ tự `git clone` về. Nếu repo của bạn private, Colab không
tự có quyền clone: chọn **Code → Download ZIP** trên GitHub, upload ZIP vào Colab,
giải nén thành `/content/Day3-Lab/`, giữ `REPO_URL` mặc định rồi chạy lại cell đầu.
Nếu chưa push nhãn lên GitHub thì upload tay `gt.txt` vào `annotations/clip_01/`
bằng bảng Files bên trái Colab.

Gold không nằm trong repo, nên sau khi nhận `gold/clip_01/gt.txt` từ Lab Coach,
upload nó lên Colab vào đúng đường dẫn đó. Thiếu gold thì notebook vẫn chạy, chỉ
bỏ qua các phép so cần gold. Đọc [lý thuyết ReID](docs/day3-reid-theory.md) trước
khi chạy. Notebook dùng môi trường đã pin và sẽ:

1. cài phiên bản `ultralytics` và `lap` đã khóa cho lab, rồi ghi actual version;
2. chạy **YOLO26 + ByteTrack** làm control trên `clip_01`;
3. chạy **YOLO26 + BoT-SORT-ReID** với cùng weights, frame order, confidence,
   IoU, image size và COCO classes;
4. xuất `model_bytetrack_clip_01.txt` và `model_reid_clip_01.txt` theo MOT 1.1;
5. chấm cả hai với gold, rồi vẽ frame treatment và nhãn của bạn chồng lên nhau.

BoT-SORT-ReID thêm appearance embedding vào bước association. Nó không sửa bbox
YOLO bỏ sót và không chứng minh danh tính xe ngoài đời. So **IDF1, AssA, IDSW**
trước, rồi xem DetA/FP/FN và frame sequence để mô tả treatment tốt hơn, tệ hơn
hay không đổi đáng kể. Đây là system comparison: ByteTrack và BoT-SORT khác
implementation, nên không kết luận ReID một mình là nguyên nhân.

| So sánh | Trả lời |
| --- | --- |
| bạn vs gold | nhãn của bạn tốt đến đâu |
| ByteTrack vs gold | control giữ identity tốt đến đâu |
| BoT-SORT + ReID vs gold | treatment appearance-assisted thay đổi tracking thế nào |
| ReID vs bạn | chỗ treatment và nhãn tay không đồng ý — đây là chỗ đáng soi nhất |

Cách đọc chỗ không đồng ý:

- **Model có bbox, bạn không** → có thể bạn bỏ sót xe nhỏ/rìa, hoặc model là FP. Kiểm tra frame sequence.
- **Bạn có bbox, model không** → có thể model bỏ sót xe bị che. Bạn nhiều khả năng đúng.
- **Cùng có bbox, khác ID** → soi kỹ nhất: motion, IoU và appearance cue nào hợp lý hơn?

**Model không phải đáp án.** Nó chỉ chỉ chỗ đáng ngờ. Teaching reference trong
`gold/` là bản nhãn đã review/adjudicate cho bài học nhưng vẫn có thể có finding.
Nếu nghi ngờ reference, ghi frame–ID–rule–evidence để Lab Coach đóng là `fixed`,
`needs-review` hoặc `not-a-defect`; không tự sửa reference.

---

## 7. Nộp bài

```bash
git checkout -b nop-bai-ngay3
git add annotations/ evidence/pre-gold/ outputs/ reports/ GUIDELINE_MINI.md
git commit -m "Ngày 3: nhãn tracking clip_01 + clip_02, kết quả đánh giá, báo cáo"
git push origin nop-bai-ngay3
```

Rồi mở Pull Request về repo gốc (hoặc nộp theo kênh Lab Coach đã công bố).

Đừng commit: thư mục `outputs/vis_*/` (ảnh đã vẽ bbox, rất nặng), file `.pt`, hoặc
thư mục `gold/`. Phải commit snapshot/manifest trong `evidence/pre-gold/`.
