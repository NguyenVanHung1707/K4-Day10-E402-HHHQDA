# Group Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin bài nộp

| Thông tin       | Nội dung                                  |
| --------------- | ----------------------------------------- |
| Khóa/Lớp        | K4                                        |
| Tên nhóm        | Nhóm 6 Thành Viên (Lead: Nguyễn Văn Hưng) |
| Repository      | https://github.com/NguyenVanHung1707/K4-Day10-E402-HHHQDA.git |
| Ngày hoàn thành | 2026-08-06                                |

### Thành viên và phân công

| STT | Họ và tên       | MSSV        | Vai trò chính                                               | Module/deliverable sở hữu                                                                                                                            |
| --: | --------------- | ----------- | ----------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
|   1 | Nguyễn Văn Hưng | 2A202601284 | Trưởng nhóm (Pipeline Orchestration & Integration Lead)     | `src/pipelines/phase1.py`, `src/pipelines/corruption_flow.py`, `script/run_phase1.py`, `script/run_corruption_flow.py`, `src/core/config.py`         |
|   2 | Nhữ Văn Hùng    | 2A202601372 | Data Ingestion Owner (Crossref API & Raw Data)              | `src/ingestion/crossref.py`, `data/raw/`                                                                                                             |
|   3 | Đặng Minh Quang | 2A202601108 | Data Cleaning & Data Modeling Owner                         | `src/ingestion/cleaning.py`, `data/clean/`                                                                                                           |
|   4 | Phạm Công Đăng  | 2A202601280 | Vector Indexing & RAG Agent Owner                           | `src/retrieval/embeddings.py`, `src/retrieval/index.py`, `src/retrieval/llm.py`, `src/retrieval/agent.py`, `src/retrieval/qa.py`, `data/embeddings/` |
|   5 | Phạm Trung Hiếu | 2A202601834 | Evaluation & Metrics Owner                                  | `src/evaluation/testset.py`, `src/evaluation/metrics.py`, `data/eval/`, `data/results/`                                                              |
|   6 | Phạm Tuấn Anh   | 2A202601060 | Data Observability, Corruption Simulation & Reporting Owner | `src/observability/quality.py`, `src/observability/reporting.py`, `src/ingestion/corruption.py`, `data/quality/`, `data/reports/`                    |

### Chi tiết phân công công việc theo từng pha (Phase Breakdown)

#### 1. Nguyễn Văn Hưng (Trưởng nhóm - Pipeline Orchestration & Integration Lead)
- **Vai trò chính:** Điều phối toàn bộ Data Pipeline end-to-end, đảm bảo tính tích hợp, tái hiện (reproducibility) và quản lý cấu hình chung.
- **Pha 1 - Baseline với dữ liệu sạch:**
  - **Cấu hình hệ thống:** Quản lý và hoàn thiện `src/core/config.py` (đường dẫn artifacts, env vars, threshold, model configs).
  - **Điều phối Baseline Pipeline:** Xây dựng `src/pipelines/phase1.py` kết nối liền mạch các module: Ingestion -> Cleaning -> Indexing -> Evaluation -> Observability -> Reporting.
  - **Chạy & Kiểm tra E2E:** Viết `script/run_phase1.py`, trực tiếp chạy và xác minh sinh đầy đủ artifacts baseline trong `data/`.
  - **Quản lý Contract:** Đảm bảo data contract và schema nhất quán khi chuyển giao giữa các thành viên.
- **Pha 2 - Corruption, Repair và Comparison:**
  - **Điều phối Corruption Flow:** Xây dựng `src/pipelines/corruption_flow.py` thực hiện luồng: Clean Data -> Corrupt Data -> Re-index & Re-evaluate -> Quality/Freshness Check -> Repair từ Raw Source -> Re-index & Re-evaluate -> Comparison Report.
  - **Chạy script tích hợp:** Viết `script/run_corruption_flow.py`, chịu trách nhiệm chạy thực thi toàn bộ flow Pha 2.
  - **Xác minh đối chiếu:** Đảm bảo cả 3 trạng thái (Baseline, Corrupted, Repaired) đều được đánh giá trên cùng một bộ Evaluation Test Set từ Thành viên 5.

#### 2. Nhữ Văn Hùng (Data Ingestion Owner)
- **Vai trò chính:** Phụ trách thu thập và chuẩn hóa dữ liệu thô từ nguồn Crossref API.
- **Pha 1 - Baseline với dữ liệu sạch:**
  - **Tích hợp API:** Hoàn thiện `src/ingestion/crossref.py` gọi tới `https://api.crossref.org/works` để lấy metadata các bài báo học thuật có DOI.
  - **Xử lý ngoại lệ:** Triển khai cơ chế retry và exponential backoff xử lý rate limit (HTTP 429) và lỗi hệ thống (HTTP 503).
  - **Parsing Raw Data:** Parse dữ liệu JSON từ API thành record schema nhất quán (`doi`, `title`, `abstract`, `authors`, `published_date`, `container_title`, `subject`, `url`).
  - **Lưu trữ Artifacts thô:** Lưu trực tiếp raw API response và raw records đã parse vào thư mục `data/raw/` phục vụ mục đích truy vết (provenance).
- **Pha 2 - Corruption, Repair và Comparison:**
  - **Hỗ trợ khôi phục dữ liệu:** Cung cấp dữ liệu gốc đáng tin cậy từ `data/raw/` hoặc fetch lại từ API Crossref để phục vụ cho hàm Repair dữ liệu.
  - **Xác minh nguồn Raw:** Đảm bảo artifact thô được lưu trữ toàn vẹn, không bị tác động bởi kịch bản corruption.

#### 3. Đặng Minh Quang (Data Cleaning & Data Modeling Owner)
- **Vai trò chính:** Phụ trách làm sạch, loại bỏ dữ liệu rác, thiết lập Data Schema và tính toán Freshness fields.
- **Pha 1 - Baseline với dữ liệu sạch:**
  - **Triển khai Quy tắc Làm sạch:** Hoàn thiện `src/ingestion/cleaning.py` để loại bỏ các bản ghi không hợp lệ (thiếu DOI, thiếu title), làm sạch ký tự HTML/nhiễu trong abstract/summary.
  - **Tạo cột Embedding (`text_for_embedding`):** Kết hợp các trường `title`, `summary`, `authors`, `subject` thành văn bản tối ưu cho việc tạo vector embedding.
  - **Xử lý thời gian & Freshness:** Chuẩn hóa `published` về ISO datetime và tính toán chỉ số `age_days` (số ngày tính từ ngày xuất bản đến hiện tại).
  - **Xuất Clean Dataset:** Lưu trữ dữ liệu sạch chuẩn hóa dưới dạng CSV/JSON vào `data/clean/`.
- **Pha 2 - Corruption, Repair và Comparison:**
  - **Triển khai Module Repair:** Viết hàm làm sạch và khôi phục dữ liệu (`clean_repaired_data`) từ nguồn raw gốc (TV2 cung cấp) khi phát hiện dữ liệu lỗi.
  - **Xác minh Schema sau Repair:** Đảm bảo dữ liệu sau repair khớp 100% về cấu trúc schema và chất lượng với Cleaned Dataset ở Pha 1.

#### 4. Phạm Công Đăng (Vector Indexing & RAG Agent Owner)
- **Vai trò chính:** Phụ trách Vector Embedding, Quản lý ChromaDB Database và Xây dựng RAG Agent.
- **Pha 1 - Baseline với dữ liệu sạch:**
  - **Tạo Embedding & Vector Store:** Hoàn thiện `src/retrieval/embeddings.py` và `src/retrieval/index.py`, sử dụng model `sentence-transformers/all-MiniLM-L6-v2` để nạp `text_for_embedding` vào ChromaDB collection kèm metadata (`paper_id`, `title`, `summary`).
  - **Đa LLM Provider Abstraction:** Cấu hình `src/retrieval/llm.py` hỗ trợ linh hoạt các LLM provider (Gemini, OpenAI, Anthropic, OpenRouter, Ollama).
  - **Xây dựng RAG Agent:** Triển khai `src/retrieval/agent.py` và `src/retrieval/qa.py` hỗ trợ Semantic Search retrieve top-k context và Lookup chính xác theo `paper_id`/title để trả lời câu hỏi.
  - **Lưu Manifest Index:** Lưu thông tin manifest indexing vào `data/embeddings/`.
- **Pha 2 - Corruption, Repair và Comparison:**
  - **Re-indexing Corrupted Data:** Thực hiện indexing lại bộ dữ liệu nhiễu/lỗi do TV6 giả lập vào ChromaDB collection mới để phục vụ đánh giá tác động.
  - **Re-indexing Repaired Data:** Thực hiện indexing lại bộ dữ liệu sau repair từ TV3 để phục vụ đánh giá mức độ khôi phục.

#### 5. Phạm Trung Hiếu (Evaluation & Metrics Owner)
- **Vai trò chính:** Phụ trách xây dựng bộ câu hỏi kiểm thử (Evaluation Test Set) và đo đạc các chỉ số đánh giá RAG (Metrics).
- **Pha 1 - Baseline với dữ liệu sạch:**
  - **Tạo Evaluation Testset:** Hoàn thiện `src/evaluation/testset.py` tạo danh sách câu hỏi (`question`), đáp án chuẩn (`ground_truth`), danh sách ID tài liệu tham chiếu (`ground_truth_doc_ids`) và phân loại câu hỏi (`question_type`). Lưu vào `data/eval/`.
  - **Triển khai Metrics Evaluator:** Hoàn thiện `src/evaluation/metrics.py` tính toán các chỉ số: `retrieval_hit_rate`, `mean_token_f1`, `judge_accuracy`, `mean_judge_score` (dùng LLM-as-a-judge) và Ragas (nếu cấu hình).
  - **Đánh giá Baseline:** Đánh giá RAG Agent trên dữ liệu sạch, xuất file chỉ số ra `data/results/baseline_metrics.json`.
- **Pha 2 - Corruption, Repair và Comparison:**
  - **Bảo toàn Testset dùng chung:** Sử dụng lại **chính xác 100%** bộ testset từ Pha 1 để đánh giá 2 trạng thái Corrupted và Repaired (đảm bảo so sánh khách quan, công bằng).
  - **Đánh giá trạng thái Corrupted & Repaired:** Tính toán metrics cho Corrupted Pipeline (`data/results/corrupted_metrics.json`) và Repaired Pipeline (`data/results/repaired_metrics.json`).
  - **Phân tích mức độ ảnh hưởng:** Đo đạc độ sụt giảm của metrics khi dữ liệu bị hư hỏng và độ phục hồi chỉ số sau khi repair.

#### 6. Phạm Tuấn Anh (Data Observability, Corruption Simulation & Reporting Owner)
- **Vai trò chính:** Phụ trách Giám sát Chất lượng dữ liệu (Data Quality & Freshness), Giả lập lỗi Dữ liệu và Xuất Báo cáo Markdown.
- **Pha 1 - Baseline với dữ liệu sạch:**
  - **Xây dựng Data Quality Checks:** Triển khai `src/observability/quality.py` kiểm tra Completeness, Schema Validity, Duplicate và Null values trong dữ liệu.
  - **Freshness Monitoring:** Tính toán giám sát `age_days` và gán trạng thái Fresh/Stale dựa trên ngưỡng cấu hình. Lưu kết quả vào `data/quality/`.
  - **Báo cáo Baseline:** Viết `src/observability/reporting.py` tự động xuất báo cáo Markdown `data/reports/phase1_report.md`.
- **Pha 2 - Corruption, Repair và Comparison:**
  - **Giả lập Dữ liệu Lỗi (Corruption Simulation):** Hoàn thiện `src/ingestion/corruption.py` tạo dữ liệu lỗi có chủ đích: xóa bản ghi mới nhất, xóa rỗng summary, thêm nhiễu vào summary, cắt ngắn title, làm stale publication date, thêm dòng duplicate. Xuất log vào `data/results/corruption_log.json`.
  - **Giám sát tín hiệu Quality/Freshness:** Chạy Quality check trên Corrupted Data (ghi nhận tín hiệu Cảnh báo/Fail) và Repaired Data (ghi nhận tín hiệu Phục hồi/Pass).
  - **Báo cáo So sánh (Comparison Report):** Viết logic tổng hợp báo cáo Markdown `data/reports/corruption_report.md` so sánh chi tiết metrics và chất lượng dữ liệu giữa 3 trạng thái Baseline vs Corrupted vs Repaired.

## 2. Tóm tắt kết quả

Nhóm đã hoàn thành 100% vòng đời dữ liệu cho hệ thống RAG Agent từ dữ liệu bài báo học thuật Crossref. Trong Pha 1 (Baseline), pipeline đã tự động thu thập 24 bản ghi thô, làm sạch chuẩn hóa schema, tạo Vector Index trên ChromaDB bằng model `sentence-transformers/all-MiniLM-L6-v2`, sinh bộ kiểm thử 24 câu hỏi và đạt chỉ số `retrieval_hit_rate` 100% cùng 5/5 bài kiểm tra Data Quality đỗ tuyệt đối. Trong Pha 2 (Corruption & Repair), nhóm đã giả lập thành công các dạng lỗi dữ liệu thực tế (xóa rỗng summary, lùi ngày xuất bản, thêm dòng trùng lặp, inject nhiễu). Kết quả ghi nhận dữ liệu bị hỏng khiến `retrieval_hit_rate` sụt giảm xuống 87.5%, `mean_token_f1` giảm từ 27.0% xuống 21.8%, và 3/5 bài kiểm tra Data Quality thất bại (cảnh báo Freshness chuyển sang STALE). Sau khi thực hiện Repair tự động tái tạo dữ liệu từ nguồn thô gốc `data/raw/crossref_records.json`, toàn bộ chỉ số của RAG Agent đã phục hồi 100% về mức baseline ban đầu, chứng minh vai trò quyết định của Data Quality và Data Observability trong hệ thống RAG.

## 3. Kiến trúc và luồng dữ liệu

### Luồng end-to-end

```text
Crossref REST API
    -> raw response & raw records (data/raw/)
    -> cleaning & schema normalization (data/clean/)
    -> embedding & ChromaDB index (data/embeddings/ & data/chroma/)
    -> evaluation baseline (data/eval/ & data/results/)
    -> quality & freshness monitoring (data/quality/)
    -> data corruption simulation (corruption_log.json)
    -> re-index & re-evaluate (corrupted_metrics.json)
    -> repair from raw data source (papers_clean_repaired.csv)
    -> comparison report generation (data/reports/corruption_report.md)
```

### Trách nhiệm của từng khối

| Khối                        | Input                                                    | Xử lý chính                                                                               | Output/artifact                                                   | Owner                         |
| --------------------------- | -------------------------------------------------------- | ----------------------------------------------------------------------------------------- | ----------------------------------------------------------------- | ----------------------------- |
| Ingestion                   | Crossref API endpoint (`https://api.crossref.org/works`) | Fetch HTTP, retry/exponential backoff, parse JSON response                                | Raw response & parsed raw records (`data/raw/`)                   | Nhữ Văn Hùng                  |
| Cleaning & Modeling         | Raw records (`data/raw/`)                                | Loại bỏ record lỗi, làm sạch HTML/summary, tạo `text_for_embedding`, tính `age_days`     | Cleaned CSV/JSON dataset (`data/clean/`)                          | Đặng Minh Quang               |
| Embedding/Index & Agent     | Cleaned dataset (`data/clean/`)                          | MiniLM embedding, ChromaDB collection indexing, multi-LLM setup & RAG agent QA            | Embedding manifest (`data/embeddings/`), ChromaDB index           | Phạm Công Đăng                |
| Evaluation                  | Cleaned dataset (`data/clean/`)                          | Tạo testset (question, ground_truth, doc_ids), đo Hit Rate, Token F1, LLM Judge           | Evaluation testset (`data/eval/`), metrics JSON (`data/results/`) | Phạm Trung Hiếu               |
| Observability & Reporting   | Cleaned / Corrupted / Repaired data                      | Data quality checks (completeness, validity), freshness status, Markdown reports          | Quality artifacts (`data/quality/`), Reports (`data/reports/`)    | Phạm Tuấn Anh                 |
| Corruption Simulation       | Cleaned dataset (`data/clean/`)                          | Giả lập lỗi (delete latest, blank summary, noise, truncate title, stale date, duplicates) | Corruption log (`data/results/corruption_log.json`)               | Phạm Tuấn Anh                 |
| Orchestration & Integration | Source modules & Config                                  | Điều phối E2E Baseline pipeline (`phase1.py`) và Corruption flow (`corruption_flow.py`)   | Entrypoint scripts (`script/`), E2E pipeline execution            | Nguyễn Văn Hưng (Trưởng nhóm) |

## 4. Cách tái hiện kết quả

### Cấu hình không chứa secret

| Biến/cấu hình             | Giá trị sử dụng |
| ------------------------- | --------------- |
| `LLM_PROVIDER`            | `gemini`        |
| `LLM_MODEL`               | `gemini-2.5-flash` |
| Embedding model           | `sentence-transformers/all-MiniLM-L6-v2` |
| Số lượng Crossref records | 24              |
| Retrieval `top_k`          | 4               |
| Freshness threshold       | 180 days        |
| Random seed, nếu có       | 42              |

### Lệnh cài đặt

```bash
python -m pip install -e .
```

Hoặc với `uv`:

```bash
uv sync
```

### Lệnh chạy

Baseline Pipeline:

```bash
python script/run_phase1.py
```

Corruption Flow:

```bash
python script/run_corruption_flow.py
```

### Kết quả tái hiện

| Lệnh              | Trạng thái                              | Thời điểm chạy gần nhất | Bằng chứng                        |
| ----------------- | --------------------------------------- | ----------------------- | --------------------------------- |
| Baseline pipeline | Thành công                              | 2026-08-06 16:25        | Artifacts tại `data/clean/papers_clean.json` & `data/embeddings/papers_embeddings.json` |
| Corruption flow   | Thành công                              | 2026-08-06 17:42        | Báo cáo so sánh tại `data/reports/corruption_report.md` |

## 5. Ingestion, cleaning và data contract

### Nguồn dữ liệu

| Thuộc tính            | Giá trị                             |
| --------------------- | ----------------------------------- |
| Source                | `https://api.crossref.org/works`    |
| Query/filter          | `query="agentic retrieval augmented generation large language model"`, `filter="from-pub-date:2026-02-07,has-abstract:true"` |
| Thời điểm lấy dữ liệu | `2026-08-06T15:00:00Z`              |
| Số record nhận được   | 24 bài báo khoa học thô             |
| Cơ chế retry/backoff  | Exponential backoff tối đa 5 lần với hệ số 2.0 xử lý HTTP 429/503 |

### Raw và clean schema

| Trường | Kiểu dữ liệu | Bắt buộc? | Ý nghĩa | Xử lý khi thiếu/sai |
| ------ | ------------ | ---------- | ------- | ------------------- |
| `paper_id` | `string` | Có | Định danh duy nhất bài báo (slug từ DOI) | Loại bỏ record nếu thiếu |
| `title` | `string` | Có | Tiêu đề bài báo đã làm sạch khoảng trắng | Loại bỏ record nếu thiếu |
| `summary` | `string` | Có | Abstract bài báo đã bóc tách HTML | Loại bỏ record nếu rỗng |
| `authors_joined` | `string` | Có | Danh sách tác giả gộp thành chuỗi | Đặt thành chuỗi rỗng nếu thiếu |
| `categories_joined` | `string` | Có | Các chủ đề/danh mục bài báo | Đặt thành chuỗi rỗng nếu thiếu |
| `published` | `string` | Có | Ngày xuất bản chuẩn ISO YYYY-MM-DD | Loại bỏ nếu không parse được date |
| `age_days` | `integer` | Có | Số ngày từ ngày xuất bản đến hiện tại | Tính `(run_date - published).days` |
| `text_for_embedding` | `string` | Có | Chuỗi văn bản hợp nhất dùng cho Vector Indexing | Tổng hợp từ Title + Summary + Authors + Categories |

### Quy tắc cleaning

| Quy tắc                             | Quality dimension liên quan | Số record bị tác động | Cách xác minh       |
| ----------------------------------- | --------------------------- | --------------------: | ------------------- |
| Loại bỏ bản ghi thiếu Title hoặc Abstract | Completeness | 0 record lỗi | Kiểm tra qua `build_clean_dataframe` |
| Strip thẻ HTML (`<p>`, `<sub>`, ...) trong summary | Validity | 24 records | Xác minh qua regex `re.sub(r"<[^>]*>", "")` |
| Chuẩn hóa ngày ISO và tính `age_days` | Timeliness | 24 records | Kiểm tra `age_days <= 180` |
| Loại bỏ trùng lặp theo `paper_id` | Uniqueness | 0 record | Kiểm tra `drop_duplicates("paper_id")` |

Giải thích cách nhóm tạo `text_for_embedding`, document ID và `age_days`:
- `text_for_embedding`: Hợp nhất thông tin theo cấu trúc `Title: {title} | Summary: {summary} | Authors: {authors_joined} | Subject: {categories_joined}` để tối ưu hóa khả năng khớp ngữ nghĩa của model embedding.
- `document_id`: Đặt trùng khớp với `paper_id` (slug hóa từ DOI) để đảm bảo tính duy nhất khi nạp vào ChromaDB.
- `age_days`: Được tính bằng hiệu số giữa ngày thực thi pipeline và ngày xuất bản của bài báo (`(run_date - published).days`), phục vụ giám sát độ tươi dữ liệu.

## 6. Evaluation setup

| Thành phần                            | Cấu hình thực tế         |
| ------------------------------------- | ------------------------ |
| Số câu hỏi                            | 24 mẫu câu hỏi kiểm thử  |
| Các `question_type`                    | `summary`, `authors`, `date`, `categories` |
| Ground-truth document ID              | `paper_id` gốc của bài báo được truy vấn |
| Embedding model                       | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector store/collection               | ChromaDB (`papers-baseline`, `papers-corrupted`, `papers-repaired`) |
| Retrieval `top_k`                      | 4                        |
| LLM provider/model                    | Gemini (`gemini-2.5-flash`) |
| Test set dùng chung cho ba trạng thái | `data/eval/test_set.json` |

Giải thích vì sao test set được giữ nguyên khi đánh giá baseline, corrupted và repaired:
- Việc giữ nguyên 100% bộ câu hỏi và đáp án chuẩn (`test_set.json`) giữa 3 trạng thái đảm bảo tính công bằng và khách quan (fair comparison). Nếu thay đổi câu hỏi giữa các lần chạy, sự thay đổi chỉ số metrics sẽ bị ảnh hưởng bởi độ khó của câu hỏi mới thay vì phản ánh chính xác tác động của dữ liệu nhiễu/lỗi lên agent.

## 7. Kết quả baseline

### Artifact checklist

| Artifact                 | Đường dẫn thực tế                    | Trạng thái | Ghi chú   |
| ------------------------ | ------------------------------------ | ---------- | --------- |
| Raw response/records     | `data/raw/crossref_records.json`     | Có         | 24 bản ghi thô từ Crossref API |
| Cleaned dataset          | `data/clean/papers_clean.csv`        | Có         | 24 bản ghi sạch chuẩn hóa |
| Embedding manifest/index | `data/embeddings/papers_embeddings.json` | Có     | Manifest ChromaDB baseline collection |
| Evaluation set           | `data/eval/test_set.json`           | Có         | 24 mẫu câu hỏi kiểm thử |
| Baseline metrics         | `data/results/baseline_metrics.json` | Có         | Metrics đánh giá baseline |
| Quality/freshness        | `data/quality/freshness_report.json` | Có         | Báo cáo giám sát độ tươi |
| Baseline report          | `data/reports/phase1_report.md`      | Có         | Báo cáo tổng hợp pha baseline |

### Baseline metrics

| Metric               |       Giá trị | Diễn giải                         |
| -------------------- | ------------: | --------------------------------- |
| `retrieval_hit_rate` |          1.00 | 100% câu hỏi tìm thấy tài liệu gốc trong Top 4 context |
| `mean_token_f1`      |        0.2705 | Độ tương đồng token giữa câu trả lời Agent và Ground Truth |
| `judge_accuracy`     |        0.0417 | Tỷ lệ LLM judge đánh giá đúng tuyệt đối |
| `mean_judge_score`   |        1.0833 | Điểm trung bình của LLM-as-a-judge trên thang điểm 1-5 |
| Ragas, nếu có        |     Skipped   | Bỏ qua pass Ragas để tối ưu tốc độ chạy |

## 8. Data quality và freshness

### Quality checks

| Check       | Quality dimension | Ngưỡng/kỳ vọng | Kết quả baseline      | Bằng chứng |
| ----------- | ----------------- | -------------- | --------------------- | ---------- |
| `row_count` | Completeness | > 0 rows | PASS (24 rows) | `data/quality/` |
| `paper_id_validity` | Validity & Uniqueness | 100% unique & non-null | PASS (Score 1.0) | `data/quality/` |
| `title_completeness` | Completeness | 0 empty titles | PASS (Score 1.0) | `data/quality/` |
| `summary_validity` | Validity | Summary len > 10 | PASS (24/24 valid) | `data/quality/` |
| `freshness_check` | Freshness | age_days <= 180 | PASS (24/24 fresh) | `data/quality/` |

### Freshness

| Thuộc tính            | Giá trị                       |
| --------------------- | ----------------------------- |
| Freshness được đo tại | `data/clean/papers_clean.json` |
| Timestamp mới nhất    | `2026-06-22`                  |
| Ngưỡng freshness      | 180 ngày                      |
| Trạng thái baseline   | `FRESH`                       |
| Lý do                 | 100% bản ghi có `age_days` nhỏ hơn ngưỡng 180 ngày (0 stale rows) |

## 9. Corruption scenarios và repair

| Corruption        | Cách tạo | Record bị tác động | Quality signal kỳ vọng | Tác động thực tế  | Cách repair   |
| ----------------- | -------- | -----------------: | ---------------------- | ----------------- | ------------- |
| `drop_latest_records` | Xóa 10% bản ghi mới nhất | 2 records | Giảm row_count | Mất thông tin bài báo mới | Tái thu thập/load lại từ raw data gốc |
| `blank_summary` | Xóa rỗng 5% summary | 1 record | FAIL `summary_validity` | Sụt giảm Hit Rate và Token F1 | Làm sạch lại từ `data/raw/` |
| `inject_noise` | Thêm chuỗi `[NOISE]` vào summary | 1 record | Giảm điểm F1 | Làm giảm độ khớp từ vựng | Re-clean lại nội dung thô gốc |
| `truncate_title` | Cắt tiêu đề còn 10 ký tự | 1 record | Mất thông tin tiêu đề | Giảm khả năng exact lookup | Khôi phục tiêu đề gốc từ raw |
| `stale_publication_date` | Lùi ngày xuất bản 3 năm | 2 records | FAIL `freshness_check` | Chuyển trạng thái sang `STALE` | Lấy lại date gốc từ raw |
| `add_duplicates` | Nhân bản 3 dòng trùng lặp | 3 records | FAIL `paper_id_validity` | Tăng số lượng bản ghi dư thừa | Áp dụng deduplicate theo `paper_id` |

Corruption log:
- Đường dẫn: `data/results/corruption_log.json`
- Trạng thái: Có
- Nhận xét: Log ghi nhận đầy đủ 6 dạng kịch bản corruption, số bản ghi bị tác động và mô tả chi tiết.

Giải thích cách repair đảm bảo dữ liệu được phục hồi từ nguồn đáng tin cậy thay vì chỉ che kết quả lỗi:
- Nhóm thực hiện khôi phục dữ liệu triệt để bằng cách đọc lại file lưu trữ thô gốc `data/raw/crossref_records.json` (được bảo toàn tuyệt đối không bị tác động bởi kịch bản corruption). Sau đó cho chạy lại pipeline làm sạch `build_clean_dataframe` và Re-indexing lại ChromaDB collection `papers-repaired` để đảm bảo tính toàn vẹn 100%.

## 10. So sánh baseline, corrupted và repaired

| Metric/signal            | Baseline | Corrupted | Repaired | Thay đổi do corruption | Mức phục hồi | Nhận xét   |
| ------------------------ | -------: | --------: | -------: | ---------------------: | -----------: | ---------- |
| `retrieval_hit_rate`     |     1.00 |     0.875 |     1.00 |                 -0.125 |       +0.125 | Phục hồi hoàn toàn 100% về mức baseline |
| `mean_token_f1`          |   0.2705 |    0.2188 |   0.2705 |                -0.0517 |      +0.0517 | Phục hồi hoàn toàn 100% về mức baseline |
| `judge_accuracy`         |   0.0417 |    0.0000 |   0.0417 |                -0.0417 |      +0.0417 | Phục hồi hoàn toàn 100% |
| `mean_judge_score`       |   1.0833 |    1.0000 |   1.0833 |                -0.0833 |      +0.0833 | Phục hồi hoàn toàn 100% |
| Quality checks pass/fail | 5/5 PASS | 2/5 PASS  | 5/5 PASS |         -3 checks FAIL | +3 checks PASS | Phục hồi đỗ 100% các bài check Quality |
| Freshness status         |    FRESH |     STALE |    FRESH |           Chuyển STALE | Phục hồi FRESH | Trạng thái freshness quay lại FRESH |

Nêu ít nhất hai kết luận có quan hệ nhân quả được hỗ trợ bởi artifacts:
1. `[Dữ liệu bị xóa rỗng summary & thêm dòng trùng lặp]` ➡️ `[Cảnh báo Quality fail tại summary_validity và paper_id_validity]` ➡️ `[Retrieval Hit Rate sụt giảm từ 100% xuống 87.5% và Token F1 sụt giảm từ 27.0% xuống 21.8%]`.
2. `[Thực hiện hành động Repair tái tạo dữ liệu từ Raw Source]` ➡️ `[Tín hiệu Quality & Freshness khôi phục hoàn toàn 5/5 PASS]` ➡️ `[Retrieval Hit Rate và Token F1 của RAG Agent phục hồi 100% về mức baseline]`.

## 11. Vấn đề tích hợp quan trọng

Mô tả một vấn đề phát sinh khi ghép các module trong pipeline và cách nhóm xử lý:
- **Triệu chứng:** Khi chạy `corruption_flow.py`, hàm `evaluate_pipeline` báo lỗi `FileNotFoundError: data/eval/test_set.json`.
- **Nguyên nhân:** Do Pha 1 trước đó chưa tự động sinh file `test_set.json` cố định vào thư mục `data/eval/`, khiến luồng Pha 2 không tìm thấy file testset dùng chung để đánh giá.
- **Cách xử lý:** Bổ sung logic kiểm tra và tự động gọi `build_test_set(clean_df, settings.paths.eval_testset)` trong `src/pipelines/corruption_flow.py` trước khi thực thi đánh giá metrics.
- **Cách xác minh:** Chạy lại `python script/run_corruption_flow.py`, cả 3 trạng thái đều đọc thành công `data/eval/test_set.json` và xuất kết quả đo đạc chính xác.

## 12. Giới hạn và hướng cải thiện

| Giới hạn hiện tại | Ảnh hưởng | Hướng cải thiện có thể kiểm chứng |
| ----------------- | ----------- | --------------------------------- |
| Context window của model embedding `MiniLM-L6-v2` bị giới hạn 256 tokens | Bài báo có summary dài bị cắt bớt thông tin khi vector hóa | Nâng cấp lên model embedding ngữ cảnh dài hơn như `text-embedding-3-small` hoặc `bge-large-en-v1.5` |
| Phụ thuộc vào API key bên ngoài khi chạy LLM Evaluator | Khi hết quota rate limit hệ thống chuyển sang heuristic fallback score | Sử dụng local LLM qua Ollama (e.g. `llama3:8b`) làm judge cố định |

## 13. Checklist trước khi nộp

- [x] Thông tin nhóm và repository chính xác.
- [x] Phân công khớp với module, artifact và kết quả thực tế.
- [x] Lệnh tái hiện đã được chạy lại trên phiên bản dùng để nộp.
- [x] Baseline, corrupted và repaired dùng cùng evaluation set.
- [x] Bảng metrics khớp với các file trong `data/results/`.
- [x] Quality/freshness conclusions khớp với `data/quality/`.
- [x] Các đường dẫn báo cáo và artifact truy cập được.
- [x] Mỗi thành viên đã hoàn thành báo cáo vai trò riêng.
- [x] Không có `.env`, API key, token hoặc secret trong source, report, log hay ảnh.
