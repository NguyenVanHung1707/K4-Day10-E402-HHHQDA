# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Họ và tên       | Nguyễn Văn Hưng            |
| MSSV               | 2A202601284                |
| Khóa/Lớp         | K4                         |
| Tên nhóm         | Nhóm 6 Thành Viên (Lead: Nguyễn Văn Hưng) |
| Vai trò chính    | Trưởng nhóm (Pipeline Orchestration & Integration Lead) |
| Repository         | https://github.com/NguyenVanHung1707/K4-Day10-E402-HHHQDA.git |
| Ngày hoàn thành | 2026-08-06                 |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao  | Trạng thái |
| ------------------ | --------------------- | ---------------- | ----------------- | ---------- |
| System Config & Data Contracts | `src/core/config.py`, `src/core/__init__.py` | Env vars & Project paths | `Settings`, `Paths` và các Data Schemas chuẩn (`RawPaperRecordSchema`, `CleanPaperRecordSchema`, `EvaluationSampleSchema`, `DataQualityCheckSchema`, `CorruptionLogSchema`) | Hoàn thành |
| Baseline Pipeline Orchestration | `src/pipelines/phase1.py`, `script/run_phase1.py` | Ingestion, Cleaning, Indexing, Eval, Quality modules | Pipeline E2E Baseline, `papers_clean.json`, `papers_embeddings.json`, `baseline_metrics.json` | Hoàn thành |
| Corruption & Repair Flow Orchestration | `src/pipelines/corruption_flow.py`, `script/run_corruption_flow.py` | Baseline artifacts, Corruption, Repair, Quality, Reporting modules | Pipeline E2E Corruption Flow, `corruption_log.json`, `corruption_report.md` | Hoàn thành |
| Documentation & Workflow Contract | `report/group_report.md`, `report/data_schema_contract.md`, `report/workflow_dependencies.md` | E2E Metrics & Kiến trúc dự án | Báo cáo nhóm hoàn chỉnh, Hợp đồng Schema dữ liệu và quy trình phụ thuộc 6 thành viên | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| --------- | ----------------------------- | ------- |
| Chốt Data Contract & Workflow | Cả 6 thành viên trong nhóm | Thiết lập quy trình đợi nhau rõ ràng giữa các bước, đảm bảo các thành viên làm việc song song không bị gãy schema |
| Debug Encoding & Git Integration | Toàn bộ dự án | Sửa triệt để lỗi `UnicodeEncodeError` trên Windows Terminal; giải quyết rebase conflicts và quản lý repository GitHub |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| --------------------- | --------------------------- | ----------------- | ------------- |
| Thiết lập Config & Schemas | `src/core/config.py` | 5 Data Schemas chuẩn hóa dùng chung | `python -c "from core.config import *"` |
| Ghép nối & Thực thi Baseline Pipeline | `src/pipelines/phase1.py`, `script/run_phase1.py` | Pipeline Pha 1 chạy E2E thông suốt 24 bản ghi | `python script/run_phase1.py` |
| Ghép nối & Thực thi Corruption Flow | `src/pipelines/corruption_flow.py`, `script/run_corruption_flow.py` | Pipeline Pha 2 E2E đối chiếu 3 trạng thái | `python script/run_corruption_flow.py` |
| Hoàn thiện Báo cáo Nhóm & Docs | `report/group_report.md`, `data_schema_contract.md` | Báo cáo nhóm chuẩn hóa 100% số liệu thực tế | Kiểm tra file `report/group_report.md` |

Nêu một output cụ thể mà phần việc của bạn tạo ra hoặc giúp xác minh:
- Luồng điều phối `corruption_flow.py` đã kết nối thành công 7 bước từ Corrupting ➡️ Re-indexing ➡️ Evaluating ➡️ Quality Monitoring ➡️ Repairing từ Raw ➡️ Re-indexing ➡️ Comparison Reporting, tạo ra file báo cáo đối chiếu [data/reports/corruption_report.md](file:///e:/hung/VinAI/Lab/Lab10/DAY10_2A202601284_NguyenVanHung/data/reports/corruption_report.md).

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Kết nối các thành phần rời rạc do 6 thành viên phụ trách (Ingestion, Cleaning, Indexing, Evaluation, Quality, Reporting) thành một luồng dữ liệu thống nhất, tự động hóa toàn bộ vòng đời từ thu thập API đến xuất báo cáo so sánh, có khả năng chạy chịu lỗi (graceful fallback) và tái hiện kết quả (reproducibility).

### Cách triển khai
- Trong `phase1.py` và `corruption_flow.py`, thiết lập thứ tự thực thi nghiêm ngặt theo luồng phụ thuộc dữ liệu.
- Quản lý cấu hình tập trung qua dataclass `Settings` và `Paths` trong `src/core/config.py`.
- Tự động tạo thư mục chứa artifacts bằng helper `ensure_parent()`.
- Tích hợp kiểm tra tiền điều kiện (pre-conditions) để sinh tự động các artifact phụ thuộc nếu chưa tồn tại (ví dụ: tự động gọi `build_test_set` nếu `data/eval/test_set.json` chưa xuất hiện).

### Input, output và contract

| Thành phần | Mô tả |
| ---------- | ------ |
| Input | Raw Crossref records, cấu hình `Settings`, artifacts từ các module thành viên |
| Output | Dữ liệu sạch, Vector index, Metrics kết quả 3 trạng thái, Báo cáo Markdown `phase1_report.md` & `corruption_report.md` |
| Module phụ thuộc | `ingestion.crossref`, `ingestion.cleaning`, `retrieval.index`, `evaluation.metrics`, `observability.quality`, `observability.reporting` |
| Module sử dụng output | Entrypoint scripts `script/run_phase1.py`, `script/run_corruption_flow.py` và báo cáo nhóm |
| Điều kiện lỗi cần xử lý | Xử lý lỗi `UnicodeEncodeError` trên Windows Console, xử lý thiếu file testset, xử lý fallback khi API rate limit |

### Cách xác minh

```bash
python script/run_phase1.py
python script/run_corruption_flow.py
```

- **Kết quả mong đợi:** Cả 2 script chạy qua 7 bước không báo lỗi, sinh đầy đủ artifacts trong `data/` và báo cáo so sánh đối chiếu 3 trạng thái.
- **Kết quả thực tế:** Chạy thông suốt 100%, xuất kết quả Hit Rate phục hồi từ 87.5% lên 100% và đỗ 5/5 bài Quality checks.
- **Artifact/log:** `data/reports/corruption_report.md`, `data/results/corrupted_metrics.json`, `data/results/repaired_metrics.json`.

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Lựa chọn kiến trúc điều phối pipeline và cách quản lý Data Contract giữa 6 thành viên khi phát triển song song.
- **Các phương án đã cân nhắc:**
  - *Phương án A:* Đợi tất cả thành viên hoàn thành 100% code mới bắt đầu ghép vào script điều phối.
  - *Phương án B (Đã chọn):* Định nghĩa Hợp đồng Data Schema chuẩn ngay từ đầu trong `src/core/config.py`, sau đó áp dụng cơ chế try-except / graceful fallback trong `phase1.py` và `corruption_flow.py`.
- **Lý do:** Phương án B giúp dự án phát triển theo mô hình decoupled (độc lập hóa các module). Trưởng nhóm có thể xây dựng và kiểm thử khung điều phối E2E ngay từ sớm mà không bị nghẽn (block) bởi tiến độ riêng của từng thành viên.
- **Bằng chứng quyết định phù hợp:** Toàn bộ pipeline đã chạy E2E mượt mà, khi các thành viên push code mới lên GitHub, hệ thống tự động nhận diện và thực thi thành công mà không phát sinh lỗi gãy interface.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** `UnicodeEncodeError: 'charmap' codec can't encode character '\u1eaf' in position 13: character maps to <undefined>`
- **Lệnh hoặc bước tái hiện:** Chạy `python script/run_phase1.py` trên Windows PowerShell/CMD.
- **Nguyên nhân gốc:** Console mặc định của môi trường Windows sử dụng bảng mã `cp1252`, không thể mã hóa được các ký tự Unicode tiếng Việt có dấu trong lệnh `print()`.
- **Cách xử lý:** Bổ sung đoạn mã cấu hình lại encoding cho `sys.stdout` và `sys.stderr` ở đầu các file entrypoint:
  ```python
  if hasattr(sys.stdout, "reconfigure"):
      sys.stdout.reconfigure(encoding="utf-8")
  if hasattr(sys.stderr, "reconfigure"):
      sys.stderr.reconfigure(encoding="utf-8")
  ```
- **Cách xác minh sau khi sửa:** Chạy lại `python script/run_phase1.py`, toàn bộ log in ra tiếng Việt có dấu chuẩn xác 100% không còn bị crash.
- **Bài học kỹ thuật:** Luôn chủ động xử lý encoding tương thích đa nền tảng (Cross-platform I/O encoding) khi xây dựng các ứng dụng CLI/Pipeline trên Windows.

## 7. Hiểu biết về luồng end-to-end

1. **Dữ liệu đi từ Crossref đến vector index:** 
   - API Crossref ➡️ Raw JSON snapshot (`data/raw/`) ➡️ Cleaning & Normalization (`data/clean/`) ➡️ MiniLM Embedding (`sentence-transformers/all-MiniLM-L6-v2`) ➡️ Nạp vào ChromaDB Persistent Collection (`papers-baseline`).
2. **Evaluation set và ground-truth document IDs:** 
   - File `test_set.json` lưu tập câu hỏi, ground truth text và danh sách `ground_truth_doc_ids`. Khi RAG Agent trả lời, evaluator so sánh danh sách doc IDs được Agent retrieve với `ground_truth_doc_ids` để tính chỉ số `retrieval_hit_rate`.
3. **Quality checks khác freshness monitoring ở điểm nào:**
   - Quality checks đánh giá tính toàn vẹn dữ liệu ở cấp độ bản ghi (Completeness, Validity, Uniqueness, Null counts).
   - Freshness monitoring đánh giá tính thời sự của dữ liệu ở cấp độ toàn dataset dựa trên khoảng cách ngày công bố (`age_days <= 180`).
4. **Vì sao phải dùng cùng test set cho 3 trạng thái:**
   - Để đảm bảo tính so sánh công bằng (fair comparison). Độ biến động của chỉ số metrics giữa Baseline, Corrupted và Repaired phản ánh chính xác tác động của chất lượng dữ liệu chứ không bị nhiễu bởi độ khó của các câu hỏi khác nhau.
5. **Repair được xem là thành công khi:**
   - Số bài check Quality đỗ khôi phục tuyệt đối 5/5 PASS, trạng thái Freshness quay lại `FRESH`, và Retrieval Hit Rate của RAG Agent phục hồi 100% về mức baseline ban đầu (từ 87.5% lên 100%).

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal          | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| ---------------------- | -------: | --------: | -------: | ------------------------- |
| `retrieval_hit_rate` |     1.00 |     0.875 |     1.00 | Dữ liệu lỗi làm suy giảm Hit Rate; repair giúp phục hồi 100% |
| `mean_token_f1`      |   0.2705 |    0.2188 |   0.2705 | Token F1 bị sụt giảm do rỗng summary/nhiễu và phục hồi hoàn toàn sau repair |
| `judge_accuracy`     |   0.0417 |    0.0000 |   0.0417 | LLM judge score phục hồi hoàn toàn sau khi repair dữ liệu |
| `mean_judge_score`   |   1.0833 |    1.0000 |   1.0833 | Điểm trung bình của LLM-as-a-judge tăng trở lại mức baseline |
| Quality checks         | 5/5 PASS | 2/5 PASS  | 5/5 PASS | Corrupted làm fail 3 bài test quality; Repaired khôi phục 5/5 PASS |
| Freshness status       |    FRESH |     STALE |    FRESH | Trạng thái chuyển STALE khi date bị lùi và khôi phục FRESH sau repair |

### Kết luận từ số liệu

1. `[Dữ liệu bị xóa rỗng summary & nhân bản dòng trùng]` ➡️ `[Cảnh báo Quality fail tại summary_validity và paper_id_validity]` ➡️ `[Retrieval Hit Rate sụt giảm từ 100% xuống 87.5% và Token F1 giảm từ 27.0% xuống 21.8%]`.
2. `[Thực hiện hành động Repair tái tạo dữ liệu từ Raw Source gốc]` ➡️ `[Tín hiệu Quality & Freshness phục hồi 100% 5/5 PASS]` ➡️ `[Retrieval Hit Rate và Token F1 của RAG Agent phục hồi hoàn toàn 100% về mức baseline]`.

- **Corruption ảnh hưởng rõ nhất:** Kịch bản `blank_summary` (xóa rỗng tóm tắt) và `drop_latest_records` ảnh hưởng nặng nhất đến RAG Agent vì làm mất hoàn toàn ngữ cảnh ngữ nghĩa quan trọng phục vụ vector retrieval.

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất
1. **Về Data Pipeline:** Quản lý Data Contract và Schema chuẩn hóa là chìa khóa quyết định để một đội ngũ kỹ sư có thể phát triển tích hợp song song mà không bị xung đột.
2. **Về Data Observability:** Giám sát Data Quality & Freshness liên tục giúp phát hiện sớm các bất thường dữ liệu trước khi dữ liệu xấu đi vào Vector Store và gây ra sai lệch cho AI Agent.
3. **Về Ảnh hưởng đến RAG Agent:** Chất lượng dữ liệu đầu vào quyết định giới hạn trên (upper bound) về hiệu năng của RAG Agent; kỹ thuật Repair đúng cách từ nguồn thô gốc có thể khôi phục 100% sức mạnh của Agent.

### Nếu có thêm thời gian
Tự động hóa toàn bộ quy trình CI/CD testing trên GitHub Actions để mỗi khi có commit mới, hệ thống tự động chạy `run_phase1.py` và `run_corruption_flow.py` nhằm phát hiện sớm biến động chỉ số metrics.

## 10. Cam kết của thành viên

Đánh dấu sau khi tự kiểm tra:

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Nguyễn Văn Hưng  
**Ngày xác nhận:** 2026-08-06
