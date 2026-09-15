# Ngày 3 — Dữ liệu Video Tracking

**Đối tượng:** học viên Giai đoạn 1, lộ trình chung **Level 2 → Level 3**.
**Thời lượng:** 240 phút. **Repo đề bài:** `K4-L2-L3-DAY03-VideoTracking`.

**Hình thức:** làm cá nhân hoặc phối hợp theo nhóm. Dù chọn cách nào, mỗi học
viên vẫn nộp **một repo cá nhân** để Lab Coach xác minh phần việc và evidence
độc lập. **Nơi nộp:** VLearn (dán link repo cá nhân). **Hạn nộp mặc định:**
23:59, múi giờ `Asia/Ho_Chi_Minh`, ngày diễn ra lab; chỉ thông báo ngoại lệ của
Key Coach mới thay thế mốc này.

Ngày 2 bạn gán nhãn từng ảnh. Hôm nay, một chiếc xe phải giữ được **cùng một
`track_id` qua nhiều frame**. Trong bốn giờ, bạn sẽ gán nhãn bằng CVAT Track
Mode, tự kiểm ba lượt, kiểm chéo, export MOT 1.1, đối chiếu với teaching
reference sau khi khóa bài độc lập, rồi chạy ByteTrack và BoT-SORT + ReID trên
chính clip đó.

> Làm nhãn độc lập trước; chỉ xem teaching reference hoặc model sau mốc khóa
> pre-gold. Model là công cụ chẩn đoán, không phải đáp án.

## Làm cá nhân hoặc theo nhóm

Bạn có thể chọn một trong hai cách sau, với cùng rubric và cùng chuẩn đầu ra:

- **Cá nhân:** tự làm toàn bộ annotation, review, report và nộp repo của mình.
- **Nhóm:** được thảo luận quy tắc, hỗ trợ thao tác và review chéo. Tuy nhiên,
  mỗi người phải tự tạo annotation/evidence pre-gold của mình, tự hoàn thiện
  report và nộp repo mang tên/MSSV của mình. Mỗi repo của thành viên nhóm phải
  có [TEAM.md](TEAM.md) đã điền để công khai phần việc và phần học được của từng
  người.

Quy định đầy đủ về cách nộp, checkpoint và liêm chính học thuật lần lượt ở
[SUBMISSION.md](SUBMISSION.md), [CHECKPOINTS.md](CHECKPOINTS.md) và
[RULES.md](RULES.md).

## Sau bài thực hành, bạn có thể

1. Tạo Rectangle **Track** trong CVAT, dùng keyframe và interpolation đúng chỗ.
2. Giữ identity nhất quán khi xe bị che, vào/ra khung, hoặc cắt nhau.
3. Export đúng **MOT 1.1** để không mất `track_id`.
4. Dùng HOTA, IDF1, MOTA và MOTP để tìm lỗi cần sửa trong nhãn của mình.
5. Giải thích ReID là appearance cue và đọc một so sánh ByteTrack với
   BoT-SORT + ReID bằng frame/ID evidence.
6. Ghi lại quy tắc, lỗi peer review và lần sửa để người khác tái hiện được.

## Dữ liệu và quy ước

| Thành phần | Quy ước của bài |
| --- | --- |
| `clip_02` | warm-up: 60 frame, 4.8 giây, có reference để tự kiểm ngay |
| `clip_01` | bài chính: 190 frame, 15.2 giây; reference chỉ phát sau pre-gold lock |
| Label | duy nhất `vehicle`: xe bốn bánh |
| Không gán | người, xe đạp, xe máy/mô tô, biển báo, xe xuất hiện trong quảng cáo |
| Bbox | chỉ ôm phần vật thể đang nhìn thấy; không đoán phần bị che hoặc ngoài khung |

Không đổi tên/thứ tự frame, không sửa nhãn warm-up có sẵn, không sửa file gold
sau khi nhận, và không dùng model để gợi ý box trước khi hoàn thành annotation.
Xem nguồn dữ liệu tại [data/README.md](data/README.md) và schema chi tiết tại
[CVAT_TASK_SPEC.md](CVAT_TASK_SPEC.md).

## Lịch thực hành 240 phút

| Phút | Hoạt động | Minh chứng |
| ---: | --- | --- |
| 0–15 | Preflight, đọc rule, tạo task warm-up | đúng label `vehicle`, Track Mode |
| 15–45 | Gán `clip_02`, export MOT 1.1, tự kiểm | file MOT hợp lệ |
| 45–90 | Gán `clip_01` độc lập, sprint 1 | giữ identity, Save trước khi nghỉ |
| 90–100 | Nghỉ 10 phút | reload task; chưa mở reference/model |
| 100–135 | Hoàn tất `clip_01`, sprint 2 | tối thiểu 6 track hợp lệ |
| 135–155 | Tự kiểm ba lượt và peer review | frame–ID–lỗi–cách sửa trong checklist |
| 155–165 | Export cuối, khóa pre-gold | snapshot và manifest SHA-256 |
| 165–195 | Nhận reference, evaluate, rework | metric trước/sau và change log |
| 195–225 | Notebook: ByteTrack và BoT-SORT + ReID | hai model MOT và comparison evidence |
| 225–237 | Hoàn tất report, kiểm submission | đủ artifact, không còn placeholder |
| 237–240 | Commit/push và nộp link | commit cuối tạo được |

Mốc phút **155** là cổng cứng: không xem `gold/clip_01/gt.txt` và không chạy
model trước khi bạn khóa bản độc lập.

## Ba nguyên tắc không được đảo thứ tự

- Gán nhãn độc lập trước khi xem teaching reference hoặc model.
- Chạy `python3 tools/lock_pre_gold.py` và gửi hash cho Lab Coach trước khi nhận
  `gold/clip_01/gt.txt`.
- Model output là baseline để chẩn đoán, không phải đáp án.

## Bắt đầu

1. Mở [hướng dẫn thao tác có ảnh thật](lab-guide.html) trong browser; giữ cả thư
   mục `assets/guide/` cạnh file HTML. Nếu không mở được HTML, dùng [GUIDE.md](GUIDE.md).
2. Đọc [CVAT_SETUP.md](CVAT_SETUP.md), rồi [CVAT_TASK_SPEC.md](CVAT_TASK_SPEC.md)
   trước khi tạo task.
3. Làm `clip_02` trước để tự kiểm đường export MOT 1.1.
4. Làm `clip_01`, dùng [GUIDELINE_MINI.md](GUIDELINE_MINI.md) để ghi quy tắc và
   ba ca mơ hồ thật.
5. Chạy validator, khóa pre-gold, nhận reference từ Lab Coach, rồi mới evaluate/rework.
6. Đọc [ReID theory](docs/day3-reid-theory.md) và chạy notebook sau khi annotation core xong.

### Mở notebook trên Google Colab

1. Fork repo này sang tài khoản GitHub cá nhân nếu bạn cần commit/nộp bài từ GitHub.
2. Tải [notebook](notebooks/day3_tracking_yolo_bytetrack.ipynb) về máy.
3. Mở [Google Colab](https://colab.research.google.com/) → **File → Upload notebook**.
4. Trong Cell 1, đặt `REPO_URL` là URL Git thô của repo cá nhân, ví dụ
   `https://github.com/ten-cua-ban/K4-L2-L3-DAY03-HoVaTen-MSSV-VideoTracking.git`.
   Không dán link ở dạng `[tên](URL)`.
5. Chạy Cell 1; đúng khi in ra `ROOT = .../Day3-Lab`. Sau đó chạy các cell theo thứ tự.

Nếu bạn chưa push nhãn, clone xong rồi upload `gt.txt` vào
`annotations/clip_01/`. Nếu repo riêng tư và Colab không clone được, tải ZIP từ
GitHub, upload vào Colab, giải nén thành `/content/Day3-Lab/`, rồi chạy lại Cell 1.

## Bài nộp

Tạo repo cá nhân theo mẫu
`K4-L2-L3-DAY03-HoVaTen-MSSV-VideoTracking` (không dấu, không khoảng trắng),
push lên GitHub và dán link repo đó vào VLearn trước hạn nộp. Nếu làm nhóm, mỗi
thành viên vẫn dùng tên/MSSV của chính mình trong tên repo và điền
[TEAM.md](TEAM.md). Danh mục artifact, lệnh tự kiểm và các điều cấm nằm trong
[SUBMISSION.md](SUBMISSION.md); đây là nguồn chuẩn trước khi nộp.

## Tài liệu chính

- [Hướng dẫn từng bước](GUIDE.md)
- [Hướng dẫn CVAT và Colab bằng ảnh chụp thật](lab-guide.html)
- [Task specification](CVAT_TASK_SPEC.md)
- [Phiếu quy tắc annotation](GUIDELINE_MINI.md)
- [Rubric](RUBRIC.md)
- [Hướng dẫn nộp bài](SUBMISSION.md)
- [Checkpoint và self-check](CHECKPOINTS.md)
- [Quy tắc làm bài](RULES.md)
- [Mẫu khai báo nhóm — chỉ dùng khi làm nhóm](TEAM.md)
- [Template report](reports/REPORT_TEMPLATE.md)
- [Reviewer checklist](reports/REVIEW_PARTNER_TEMPLATE.md)
- [Lý thuyết ReID](docs/day3-reid-theory.md)

## Hỗ trợ và phần mở rộng

- Lần đầu dùng CVAT: đi lần lượt theo `lab-guide.html`; dừng kiểm sau box đầu,
  sau warm-up export và trước pre-gold lock.
- Đã có kinh nghiệm: có thể đi thẳng core path, nhưng không được bỏ QC, evidence
  hay peer review.
- Hoàn thành sớm: chỉ sau core mới làm stretch; giữ nguyên evidence và giải thích
  trade-off, không gán thêm dữ liệu để lấy lợi thế.

Khi gặp lỗi, giữ nguyên thông báo lỗi và báo Lab Coach. Không tự đổi schema,
không sửa index frame bằng tay, và không dùng output model làm nhãn tham chiếu.
