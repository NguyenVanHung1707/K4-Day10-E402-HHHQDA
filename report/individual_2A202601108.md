# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| --- | --- |
| Họ và tên | Đặng Minh Quang |
| MSSV | 2A202601108 |
| Khóa/Lớp | K4 |
| Tên nhóm | Nhóm 6 Thành Viên (Lead: Nguyễn Văn Hùng) |
| Vai trò chính | Data Cleaning & Data Modeling Owner |
| Repository | [K4-Day10-E402-HHHQDA](https://github.com/NguyenVanHung1707/K4-Day10-E402-HHHQDA) |
| Ngày hoàn thành | 2026-08-06 |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input | Output bàn giao | Trạng thái |
| --- | --- | --- | --- | --- |
| Cleaning và data modeling Pha 1 | `src/ingestion/cleaning.py` — `build_clean_dataframe` | Raw records và `run_date` | `papers_clean.csv/json` | Hoàn thành |
| Repair Pha 2 | `src/ingestion/cleaning.py` — `clean_repaired_data` | Raw snapshot đáng tin cậy | `papers_clean_repaired.csv/json` | Hoàn thành |
| Public API | `src/ingestion/__init__.py` | Hàm cleaning/repair | Export hai hàm xử lý | Hoàn thành |

Tôi nhận raw records từ TV2. Dữ liệu sạch được TV4, TV5 và TV6 dùng cho indexing, evaluation và observability. Trong Pha 2, repaired dataset được bàn giao cho TV4 re-index và TV5 đánh giá lại trên cùng test set.

## 3. Kết quả theo vai trò

| Nhiệm vụ | File/hàm/artifact | Kết quả | Cách xác minh |
| --- | --- | --- | --- |
| Chuẩn hóa văn bản | `_clean_text`, `_clean_list` | Bỏ HTML, decode entity, chuẩn hóa Unicode NFKC/khoảng trắng, loại phần tử danh sách trùng | Kiểm tra các cột text trong clean artifacts |
| Lọc và chuẩn hóa record | `build_clean_dataframe` | Bỏ record thiếu ID, title, summary hoặc ngày hợp lệ | Kiểm tra trường bắt buộc |
| Tạo schema embedding-ready | `CLEAN_COLUMNS` | 13 cột; tạo `text_for_embedding`, `summary_chars`, `age_days` | Đọc header CSV/JSON |
| Khôi phục từ nguồn tin cậy | `clean_repaired_data` | Rebuild derived fields từ raw, không vá corrupted dataframe | So sánh clean/repaired cùng `run_date` |

Artifact thực tế gồm 24 raw records, 24 clean records và 24 repaired records. Clean và repaired đều có đúng 13 cột. Khi dùng cùng raw snapshot và `run_date`, hai DataFrame bằng nhau hoàn toàn.

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Raw metadata chưa phù hợp để embedding: văn bản có HTML/entity và khoảng trắng thừa; ngày có thể sai; authors/categories là danh sách; trường bắt buộc có thể thiếu. Khi clean data bị corruption, hệ thống phải phục hồi từ nguồn raw thay vì tiếp tục sửa dữ liệu đã hỏng.

### Cách triển khai

- `_clean_text` dùng `html.unescape`, regex loại tag, Unicode NFKC và chuẩn hóa khoảng trắng.
- `_clean_list` làm sạch từng phần tử và loại trùng theo `casefold`.
- `_parse_date` parse UTC an toàn; `updated` không hợp lệ được thay bằng `published`.
- Record thiếu `paper_id`, `title`, `summary` hoặc `published` hợp lệ bị loại.
- `age_days` là chênh lệch giữa `run_date` và `published`, chặn tối thiểu tại 0.
- `text_for_embedding` ghép title, summary, authors và subject theo định dạng ổn định.
- DataFrame loại trùng `paper_id`, sắp xếp mới nhất trước và ép hai cột số về `int64`.
- `clean_repaired_data` chạy lại cùng cleaning logic trên raw snapshot, rồi kiểm tra schema, trường bắt buộc và khóa duy nhất.

### Input, output và contract

| Thành phần | Mô tả |
| --- | --- |
| Input | `list[PaperRecord]` hoặc `list[dict]`; `run_date: datetime` |
| Output | `pandas.DataFrame` đúng 13 cột trong `CLEAN_COLUMNS` |
| Module phụ thuộc | `ingestion.crossref.PaperRecord`, pandas |
| Module sử dụng output | phase1 pipeline, retrieval, evaluation, observability và corruption flow |
| Điều kiện lỗi | `run_date` sai kiểu; record thiếu trường; ngày không parse được; repair lệch schema hoặc còn khóa trùng |

### Cách xác minh

```powershell
.\.venv\Scripts\python.exe -c "from datetime import UTC,datetime; from core.config import load_settings; from ingestion.crossref import load_raw_records; from ingestion.cleaning import build_clean_dataframe,clean_repaired_data; s=load_settings(); raw=load_raw_records(s.paths.raw_records_json); t=datetime.now(UTC); clean=build_clean_dataframe(raw,t); repaired=clean_repaired_data(raw,t); assert clean.equals(repaired); assert repaired.paper_id.is_unique; print(len(repaired), len(repaired.columns))"
```

Kết quả thực tế: `24 13`, không có assertion lỗi. Artifact nằm trong `data/clean/`.

## 5. Một quyết định kỹ thuật quan trọng

- Bối cảnh: chọn cách phục hồi sau corruption.
- Phương án A: vá trực tiếp corrupted dataframe.
- Phương án B: rebuild từ raw snapshot bằng cùng hàm cleaning của baseline.
- Phương án chọn: B.
- Lý do: tránh bỏ sót corruption, bảo toàn lineage và khả năng tái lập. Dùng chung logic ngăn schema/derived fields giữa baseline và repaired bị lệch.
- Bằng chứng: repaired có 24 dòng, 13 cột và bằng clean DataFrame khi chạy cùng input/thời điểm.

## 6. Một lỗi hoặc blocker đã xử lý

- Triệu chứng: báo cáo cá nhân ban đầu chứa thông tin và phần việc của TV2.
- Nguyên nhân gốc: file được sao chép từ báo cáo ingestion nhưng chưa thay theo ownership.
- Cách xử lý: đối chiếu workflow, group report, code và artifacts rồi viết lại theo cleaning/repair thực tế.
- Cách xác minh: kiểm tra MSSV, họ tên, module ownership và các artifact được dẫn chiếu.
- Điều học được: mỗi tuyên bố trong báo cáo phải truy ngược được tới code hoặc artifact.

## 7. Hiểu biết về luồng end-to-end

1. TV2 parse Crossref thành raw records; module của tôi chuyển raw sang clean schema và `text_for_embedding`; TV4 tạo embedding và index ChromaDB.
2. Evaluation set chứa câu hỏi, đáp án và document ID chuẩn. Retrieved IDs dùng tính hit rate; câu trả lời dùng tính F1/judge.
3. Quality checks đo tính đầy đủ, hợp lệ và duy nhất; freshness đo độ mới từ `published`/`age_days`.
4. Dùng cùng test set giúp thay đổi metrics phản ánh trạng thái dữ liệu, không phải độ khó câu hỏi.
5. Repair thành công ở data level khi schema, số dòng, khóa và derived fields phục hồi; ở agent level khi metrics repaired tiến gần baseline.

## 8. Phân tích kết quả

| Metric/signal | Baseline | Corrupted | Repaired | Nhận xét |
| --- | ---: | ---: | ---: | --- |
| `retrieval_hit_rate` | 0.90 | 0.40 | 0.90 | Phục hồi về baseline |
| `mean_token_f1` | 0.842 | 0.325 | 0.821 | Phục hồi gần baseline |
| `judge_accuracy` | 0.90 | 0.30 | 0.90 | Phục hồi về baseline |
| `mean_judge_score` | 4.50 | 2.10 | 4.40 | Phục hồi gần baseline |
| Quality checks | Chưa có artifact riêng | Có artifact corrupted | Chưa có artifact riêng | Không suy diễn phần thiếu bằng chứng |
| Freshness | Chưa có artifact riêng | Có artifact corrupted | Chưa có artifact riêng | Không suy diễn phần thiếu bằng chứng |

Số liệu lấy từ ba file metrics trong `data/results/`; việc tạo metrics thuộc TV5.

1. Corruption làm hỏng nội dung embedding → hit rate giảm 0.90 xuống 0.40 → token F1 giảm 0.842 xuống 0.325.
2. Rebuild từ raw source → schema/nội dung phục hồi → hit rate trở lại 0.90 và token F1 đạt 0.821.

Blank/noisy summary và truncated title ảnh hưởng trực tiếp nhất vì `text_for_embedding` lấy phần lớn tín hiệu từ hai trường này. Repaired metrics không khớp tuyệt đối ở mọi chỉ số; khả năng là bước sinh câu trả lời/judge có tính không xác định, trong khi retrieval hit rate đã phục hồi hoàn toàn.

## 9. Điều học được và hướng cải thiện

1. Raw snapshot bất biến là nền tảng để pipeline repair và tái lập.
2. Schema contract cần kiểm tra tên cột, khóa duy nhất và derived fields, không chỉ số dòng.
3. Lỗi title/summary lan trực tiếp sang embedding, retrieval và chất lượng RAG.

Nếu có thêm thời gian, tôi sẽ thêm pytest cho từng quy tắc cleaning và content fingerprint để so baseline/repaired nhưng loại trừ trường phụ thuộc thời gian như `age_days`.

## 10. Cam kết của thành viên

- [x] Nội dung phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end.
- [x] Kết luận có artifact hoặc metric đối chiếu.
- [x] Tôi không ghi thành công cho phần chưa kiểm chứng.
- [x] Báo cáo không chứa secret.
- [x] Báo cáo không sao chép báo cáo thành viên khác.

**Họ và tên:** Đặng Minh Quang  
**Ngày xác nhận:** 2026-08-06
