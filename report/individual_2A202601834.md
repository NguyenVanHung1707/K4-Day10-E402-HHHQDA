# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Họ và tên       | Phạm Trung Hiếu            |
| MSSV               | 2A202601834                |
| Khóa/Lớp         | K4                         |
| Tên nhóm         | Nhóm 6 Thành Viên          |
| Vai trò chính    | Evaluation & Metrics Owner |
| Repository         | https://github.com/NguyenVanHung1707/K4-Day10-E402-HHHQDA.git |
| Ngày hoàn thành | 2026-08-06                 |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao  | Trạng thái                                 |
| ------------------ | --------------------- | ---------------- | ----------------- | -------------------------------------------- |
| Evaluation Testset Generator | `src/evaluation/testset.py` | Cleaned Dataset (`data/clean/papers_clean.json`) | `data/eval/test_set.json` (24 mẫu câu hỏi) | Hoàn thành |
| Metrics Evaluator  | `src/evaluation/metrics.py` | RAG Agent index & `test_set.json` | `data/results/baseline_metrics.json`, `corrupted_metrics.json`, `repaired_metrics.json` | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động                         | Thành viên/module được hỗ trợ | Kết quả                    |
| ------------------------------------ | ------------------------------------ | ---------------------------- |
| Cung cấp dữ liệu đo đạc Metrics | TV6 (Observability & Reporting Owner) | Bàn giao đầy đủ 3 bộ metrics để TV6 xuất `corruption_report.md` |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao       | Cách xác minh         |
| --------------------------- | ----------------------------- | ------------------------- | ----------------------- |
| Xây dựng Evaluation Test Set | `src/evaluation/testset.py` | File `data/eval/test_set.json` | `python script/run_phase1.py` |
| Đo đạc chỉ số RAG Evaluation | `src/evaluation/metrics.py` | Metrics JSON tại `data/results/` | `python script/run_corruption_flow.py` |

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Tạo bộ câu hỏi và đáp án chuẩn (ground truth) tự động từ dữ liệu sạch, sau đó thực hiện chấm điểm tự động hiệu năng truy vấn của RAG Agent trên 3 trạng thái Baseline, Corrupted và Repaired.

### Cách triển khai
- Sinh 4 loại câu hỏi trong `testset.py`: `summary`, `authors`, `date`, `categories`.
- Đánh giá bằng 4 chỉ số chính trong `metrics.py`: `retrieval_hit_rate` (Hit Rate Top-k), `mean_token_f1`, `judge_accuracy`, `mean_judge_score` (dùng LLM-as-a-judge).

## 5. Phân tích kết quả Metrics

| Metric/signal          | Baseline | Corrupted | Repaired | Nhận xét cá nhân |
| ---------------------- | -------: | --------: | -------: | ------------------------- |
| `retrieval_hit_rate` |     1.00 |     0.875 |     1.00 | Hit Rate sụt giảm khi data bị hỏng và quay lại 100% sau khi repair |
| `mean_token_f1`      |   0.2705 |    0.2188 |   0.2705 | Token F1 giảm 0.0517 do nhiễu và rỗng summary, phục hồi hoàn toàn sau repair |

## 6. Cam kết của thành viên
- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.

**Họ và tên:** Phạm Trung Hiếu  
**Ngày xác nhận:** 2026-08-06
