# Quyền phụ thuộc và Trình tự làm việc giữa các thành viên (Member Dependencies & Workflow)

Tài liệu này mô tả chi tiết quy trình làm việc, điểm chặn (wait points) và sự phụ thuộc dữ liệu giữa **6 thành viên** trong dự án Data Pipeline & Data Observability.

---

## 🔄 PHA 1: Baseline Dữ Liệu Sạch (Clean Baseline Pipeline)

Trong Pha 1, dữ liệu luân chuyển theo mô hình **thác nước (Waterfall)** ở các bước thu thập/làm sạch ban đầu, sau đó **chia nhánh làm song song** ở các bước huấn luyện vector, đánh giá và giám sát chất lượng.

### 1. Bước 0 — Khởi tạo Cấu hình & Schema Contract (Trưởng nhóm TV1)
- **TV1 (Trưởng nhóm - Nguyễn Văn Hưng)** hoàn thiện `src/core/config.py` và chốt Data Schema chuẩn cho các giai đoạn.
- Tất cả các thành viên khác sử dụng thống nhất cấu hình đường dẫn (`data/raw`, `data/clean`, `data/eval`, `data/results`, `data/quality`, `data/reports`) và các biến môi trường từ `config.py`.

### 2. Bước 1 — Thu thập Dữ liệu thô (TV2)
- **TV2 (Ingestion Owner)** thực thi `src/ingestion/crossref.py` để kết nối API Crossref, lấy danh sách metadata bài báo thô và lưu vào `data/raw/`.
- ⏳ **Điểm đợi (Wait Point 1):** **TV3 phải ĐỜI TV2** hoàn thành xong việc lấy dữ liệu và tạo xong các file trong `data/raw/` mới có thể tiến hành làm sạch.

### 3. Bước 2 — Làm sạch & Chuẩn hóa Dữ liệu (TV3)
- **TV3 (Cleaning Owner)** lấy dữ liệu thô từ `data/raw/`, chạy `src/ingestion/cleaning.py` để lọc bản ghi rác, chuẩn hóa summary, tạo cột `text_for_embedding` và tính chỉ số `age_days`. Xuất kết quả ra `data/clean/`.
- ⏳ **Điểm đợi (Wait Point 2):** Sau khi TV3 hoàn thành `data/clean/`, **3 thành viên tiếp theo (TV4, TV5, TV6)** mới bắt đầu tiến hành công việc của mình:
  - **TV4** cần `data/clean/` để nạp vào ChromaDB tạo Vector Embedding.
  - **TV5** cần `data/clean/` để tạo bộ câu hỏi kiểm thử Evaluation Testset (`data/eval/`).
  - **TV6** cần `data/clean/` để thực hiện các bài kiểm tra chất lượng dữ liệu Data Quality & Freshness (`data/quality/`).

### 4. Bước 3 — Dựng Vector Index, Testset & Quality Check (Song song)
- **TV4** (Build ChromaDB Index & RAG Agent), **TV5** (Tạo Testset), **TV6** (Data Quality & Freshness) thực hiện công việc **song song**.
- ⏳ **Điểm đợi (Wait Point 3):** Để tính toán các chỉ số Baseline Metrics (`data/results/baseline_metrics.json`), **TV5 phải ĐỜI TV4** dựng xong RAG Agent (`src/retrieval/agent.py`) thì mới dùng bộ Testset vừa tạo để gửi câu hỏi query Agent và tính điểm.

### 5. Bước 4 — Báo cáo Baseline & Tích hợp Pipeline (TV6 & TV1)
- **TV6** hoàn thiện `src/observability/reporting.py`, đợi **TV5** có kết quả metrics baseline và **TV6** có kết quả quality để xuất file báo cáo `data/reports/phase1_report.md`.
- **TV1 (Trưởng nhóm)** ghép nối các module thành `src/pipelines/phase1.py` và chạy script điều phối `script/run_phase1.py` để kiểm thử toàn bộ luồng Pha 1 End-to-End.

---

## 🔄 PHA 2: Corruption, Repair & Comparison Flow

Pha 2 đòi hỏi sự phối hợp chặt chẽ giữa các thành viên để giả lập sự cố dữ liệu, đo đạc mức độ suy giảm và thực hiện phục hồi.

### 1. Bước 1 — Giả lập Dữ liệu Lỗi (TV6)
- **TV6** lấy `data/clean/` từ Pha 1, chạy `src/ingestion/corruption.py` tạo bộ dữ liệu lỗi (Corrupted Dataset) và xuất log `data/results/corruption_log.json`.
- ⏳ **Điểm đợi (Wait Point 4):**
  - **TV4 phải ĐỜI TV6** tạo xong Corrupted Dataset mới tiến hành Re-indexing (tạo Vector Database chứa dữ liệu nhiễu/lỗi).
  - **TV6 (Data Quality)** chạy lại bài test Observability trên dữ liệu lỗi để xác minh hệ thống phát hiện và đưa ra tín hiệu Cảnh báo/Fail.

### 2. Bước 2 — Đánh giá RAG Agent trên Dữ liệu Lỗi (TV4 & TV5)
- TV4 Re-index xong Vector DB lỗi -> **TV5 dùng lại ĐÚNG bộ Testset từ Pha 1** để query Corrupted Agent và xuất `data/results/corrupted_metrics.json` (đo đạc mức độ sụt giảm chỉ số).

### 3. Bước 3 — Phục hồi Dữ liệu / Repair (TV2 & TV3)
- **TV2** bàn giao lại dữ liệu thô gốc từ `data/raw/` (nguồn đáng tin cậy) -> **TV3** dùng hàm `clean_repaired_data` làm sạch lại từ đầu (loại bỏ hoàn toàn các dạng lỗi do TV6 tạo ra) -> xuất ra `Repaired Dataset`.
- ⏳ **Điểm đợi (Wait Point 5):** **TV4 phải ĐỜI TV3** làm sạch xong Repaired Dataset mới tiến hành Re-indexing lần 3 (tạo Vector Database phục hồi).

### 4. Bước 4 — Đánh giá RAG Agent trên Dữ liệu Phục hồi (TV4 & TV5)
- TV4 Re-index xong Vector DB phục hồi -> **TV5 tiếp tục dùng bộ Testset từ Pha 1** query Repaired Agent và xuất `data/results/repaired_metrics.json` (đo đạc mức độ phục hồi chỉ số).

### 5. Bước 5 — Báo cáo So sánh & Tích hợp Flow 2 (TV6 & TV1)
- ⏳ **Điểm đợi (Wait Point 6):** **TV6 phải ĐỜI TV5** bàn giao đủ cả 3 bộ chỉ số (Baseline, Corrupted, Repaired) thì mới tự động tổng hợp báo cáo so sánh `data/reports/corruption_report.md`.
- **TV1 (Trưởng nhóm)** tích hợp toàn bộ luồng Pha 2 vào `src/pipelines/corruption_flow.py`, chạy thực thi qua `script/run_corruption_flow.py` và chốt nghiệm thu dự án.

---

## 📊 Sơ đồ Tóm tắt Luồng Trình tự & Điểm Chặn (Sequence Diagram)

```text
[Trưởng nhóm TV1] -> Cấu hình config.py & Contract Schema
       │
       ▼
  [TV2 Ingestion] -> Lấy dữ liệu thô (data/raw/)
       │
       ▼ (TV3 ĐỜI TV2)
  [TV3 Cleaning] -> Làm sạch dữ liệu (data/clean/)
       │
       ├───────────────────────┬───────────────────────┐
       ▼ (TV4 ĐỜI TV3)         ▼ (TV5 ĐỜI TV3)         ▼ (TV6 ĐỜI TV3)
 [TV4 Vector DB & Agent]   [TV5 Tạo Testset]     [TV6 Quality Check]
       │                       │
       └───────────┬───────────┘
                   ▼ (TV5 ĐỜI TV4 hoàn thành Agent)
            [TV5 Đo Baseline Metrics]
                   │
                   ▼ (TV6 ĐỜI TV5 có Metrics)
            [TV6 Báo cáo Baseline] -> [TV1 Chạy Phase 1 Pipeline]
                   │
                   ▼
            [TV6 Corrupt Data] -> [TV4 Index Lỗi] -> [TV5 Đo Corrupted Metrics]
                   │
                   ▼ (TV3 Repair từ data/raw của TV2)
            [TV3 Repaired Data] -> [TV4 Index Repaired] -> [TV5 Đo Repaired Metrics]
                   │
                   ▼ (TV6 ĐỜI TV5 đủ 3 bộ Metrics)
            [TV6 Báo cáo So sánh 3 trạng thái] -> [TV1 Chạy Corruption Flow E2E]
```
