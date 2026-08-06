# Group Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin bài nộp

| Thông tin         | Nội dung                                       |
| ------------------ | ----------------------------------------------- |
| Khóa/Lớp         | K4                                              |
| Tên nhóm         | Nhóm 6 Thành Viên (Lead: Nguyễn Văn Hùng) |
| Repository         | DAY10_2A202601284_NguyenVanHung                 |
| Ngày hoàn thành | 2026-08-06                                      |

### Thành viên và phân công

| STT | Họ và tên       | MSSV        | Vai trò chính                                             | Module/deliverable sở hữu                                                                                                                                      |
| --: | ------------------ | ----------- | ----------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|   1 | Nguyễn Văn Hưng | 2A202601284 | Trưởng nhóm (Pipeline Orchestration & Integration Lead)  | `src/pipelines/phase1.py`, `src/pipelines/corruption_flow.py`, `script/run_phase1.py`, `script/run_corruption_flow.py`, `src/core/config.py`           |
|   2 | Nhữ Văn Hùng    | 2A202601372 | Data Ingestion Owner (Crossref API & Raw Data)              | `src/ingestion/crossref.py`, `data/raw/`                                                                                                                     |
|   3 | Thành viên 3     | MSSV_TV3    | Data Cleaning & Data Modeling Owner                         | `src/ingestion/cleaning.py`, `data/clean/`                                                                                                                   |
|   4 | Phạm Công Đăng | 2A202601280 | Vector Indexing & RAG Agent Owner                           | `src/retrieval/embeddings.py`, `src/retrieval/index.py`, `src/retrieval/llm.py`, `src/retrieval/agent.py`, `src/retrieval/qa.py`, `data/embeddings/` |
|   5 | Phạm Trung Hiếu  | 2A202601834 | Evaluation & Metrics Owner                                  | `src/evaluation/testset.py`, `src/evaluation/metrics.py`, `data/eval/`, `data/results/`                                                                  |
|   6 | Phạm Tuấn Anh   | 2A202601060 | Data Observability, Corruption Simulation & Reporting Owner | `src/observability/quality.py`, `src/observability/reporting.py`, `src/ingestion/corruption.py`, `data/quality/`, `data/reports/`                      |

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

#### 2. Thành viên 2 (Data Ingestion Owner)

- **Vai trò chính:** Phụ trách thu thập và chuẩn hóa dữ liệu thô từ nguồn Crossref API.
- **Pha 1 - Baseline với dữ liệu sạch:**
  - **Tích hợp API:** Hoàn thiện `src/ingestion/crossref.py` gọi tới `https://api.crossref.org/works` để lấy metadata các bài báo học thuật có DOI.
  - **Xử lý ngoại lệ:** Triển khai cơ chế retry và exponential backoff xử lý rate limit (HTTP 429) và lỗi hệ thống (HTTP 503).
  - **Parsing Raw Data:** Parse dữ liệu JSON từ API thành record schema nhất quán (`doi`, `title`, `abstract`, `authors`, `published_date`, `container_title`, `subject`, `url`).
  - **Lưu trữ Artifacts thô:** Lưu trực tiếp raw API response và raw records đã parse vào thư mục `data/raw/` phục vụ mục đích truy vết (provenance).
- **Pha 2 - Corruption, Repair và Comparison:**
  - **Hỗ trợ khôi phục dữ liệu:** Cung cấp dữ liệu gốc đáng tin cậy từ `data/raw/` hoặc fetch lại từ API Crossref để phục vụ cho hàm Repair dữ liệu.
  - **Xác minh nguồn Raw:** Đảm bảo artifact thô được lưu trữ toàn vẹn, không bị tác động bởi kịch bản corruption.

#### 3. Thành viên 3 (Data Cleaning & Data Modeling Owner)

- **Vai trò chính:** Phụ trách làm sạch, loại bỏ dữ liệu rác, thiết lập Data Schema và tính toán Freshness fields.
- **Pha 1 - Baseline với dữ liệu sạch:**
  - **Triển khai Quy tắc Làm sạch:** Hoàn thiện `src/ingestion/cleaning.py` để loại bỏ các bản ghi không hợp lệ (thiếu DOI, thiếu title), làm sạch ký tự HTML/nhiễu trong abstract/summary.
  - **Tạo cột Embedding (`text_for_embedding`):** Kết hợp các trường `title`, `summary`, `authors`, `subject` thành văn bản tối ưu cho việc tạo vector embedding.
  - **Xử lý thời gian & Freshness:** Chuẩn hóa `published` về ISO datetime và tính toán chỉ số `age_days` (số ngày tính từ ngày xuất bản đến hiện tại).
  - **Xuất Clean Dataset:** Lưu trữ dữ liệu sạch chuẩn hóa dưới dạng CSV/JSON vào `data/clean/`.
- **Pha 2 - Corruption, Repair và Comparison:**
  - **Triển khai Module Repair:** Viết hàm làm sạch và khôi phục dữ liệu (`clean_repaired_data`) từ nguồn raw gốc (TV2 cung cấp) khi phát hiện dữ liệu lỗi.
  - **Xác minh Schema sau Repair:** Đảm bảo dữ liệu sau repair khớp 100% về cấu trúc schema và chất lượng với Cleaned Dataset ở Pha 1.

#### 4. Thành viên 4 (Vector Indexing & RAG Agent Owner)

- **Vai trò chính:** Phụ trách Vector Embedding, Quản lý ChromaDB Database và Xây dựng RAG Agent.
- **Pha 1 - Baseline với dữ liệu sạch:**
  - **Tạo Embedding & Vector Store:** Hoàn thiện `src/retrieval/embeddings.py` và `src/retrieval/index.py`, sử dụng model `sentence-transformers/all-MiniLM-L6-v2` để nạp `text_for_embedding` vào ChromaDB collection kèm metadata (`paper_id`, `title`, `summary`).
  - **Đa LLM Provider Abstraction:** Cấu hình `src/retrieval/llm.py` hỗ trợ linh hoạt các LLM provider (Gemini, OpenAI, Anthropic, OpenRouter, Ollama).
  - **Xây dựng RAG Agent:** Triển khai `src/retrieval/agent.py` và `src/retrieval/qa.py` hỗ trợ Semantic Search retrieve top-k context và Lookup chính xác theo `paper_id`/title để trả lời câu hỏi.
  - **Lưu Manifest Index:** Lưu thông tin manifest indexing vào `data/embeddings/`.
- **Pha 2 - Corruption, Repair và Comparison:**
  - **Re-indexing Corrupted Data:** Thực hiện indexing lại bộ dữ liệu nhiễu/lỗi do TV6 giả lập vào ChromaDB collection mới để phục vụ đánh giá tác động.
  - **Re-indexing Repaired Data:** Thực hiện indexing lại bộ dữ liệu sau repair từ TV3 để phục vụ đánh giá mức độ khôi phục.

#### 5. Thành viên 5 (Evaluation & Metrics Owner)

- **Vai trò chính:** Phụ trách xây dựng bộ câu hỏi kiểm thử (Evaluation Test Set) và đo đạc các chỉ số đánh giá RAG (Metrics).
- **Pha 1 - Baseline với dữ liệu sạch:**
  - **Tạo Evaluation Testset:** Hoàn thiện `src/evaluation/testset.py` tạo danh sách câu hỏi (`question`), đáp án chuẩn (`ground_truth`), danh sách ID tài liệu tham chiếu (`ground_truth_doc_ids`) và phân loại câu hỏi (`question_type`). Lưu vào `data/eval/`.
  - **Triển khai Metrics Evaluator:** Hoàn thiện `src/evaluation/metrics.py` tính toán các chỉ số: `retrieval_hit_rate`, `mean_token_f1`, `judge_accuracy`, `mean_judge_score` (dùng LLM-as-a-judge) và Ragas (nếu cấu hình).
  - **Đánh giá Baseline:** Đánh giá RAG Agent trên dữ liệu sạch, xuất file chỉ số ra `data/results/baseline_metrics.json`.
- **Pha 2 - Corruption, Repair và Comparison:**
  - **Bảo toàn Testset dùng chung:** Sử dụng lại **chính xác 100%** bộ testset từ Pha 1 để đánh giá 2 trạng thái Corrupted và Repaired (đảm bảo so sánh khách quan, công bằng).
  - **Đánh giá trạng thái Corrupted & Repaired:** Tính toán metrics cho Corrupted Pipeline (`data/results/corrupted_metrics.json`) và Repaired Pipeline (`data/results/repaired_metrics.json`).
  - **Phân tích mức độ ảnh hưởng:** Đo đạc độ sụt giảm của metrics khi dữ liệu bị hư hỏng và độ phục hồi chỉ số sau khi repair.

#### 6. Thành viên 6 (Data Observability, Corruption Simulation & Reporting Owner)

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

Viết từ 150–250 từ, trả lời ngắn gọn:

- Nhóm đã hoàn thành những phần nào?
- Baseline pipeline đã tạo ra các artifact nào?
- Corruption nào ảnh hưởng rõ nhất đến data quality hoặc agent?
- Repair đã phục hồi được chỉ số nào?
- Blocker hoặc giới hạn quan trọng nhất còn lại là gì?

**Tóm tắt của nhóm:**

[Viết phần tóm tắt tại đây.]

## 3. Kiến trúc và luồng dữ liệu

### Luồng end-to-end

Điều chỉnh sơ đồ dưới đây nếu cách triển khai thực tế của nhóm khác starter:

```text
Crossref API
    -> raw response/raw records
    -> cleaning và data modeling
    -> embedding + ChromaDB index
    -> evaluation baseline
    -> quality/freshness reports
    -> corruption
    -> re-index và re-evaluate
    -> repair từ dữ liệu nguồn
    -> comparison report
```

### Trách nhiệm của từng khối

| Khối                       | Input                                                      | Xử lý chính                                                                                  | Output/artifact                                                       | Owner                               |
| --------------------------- | ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- | ----------------------------------- |
| Ingestion                   | Crossref API endpoint (`https://api.crossref.org/works`) | Fetch HTTP, retry/exponential backoff, parse JSON response                                      | Raw response & parsed raw records (`data/raw/`)                     | Thành viên 2                      |
| Cleaning & Modeling         | Raw records (`data/raw/`)                                | Loại bỏ record lỗi, làm sạch HTML/summary, tạo`text_for_embedding`, tính `age_days`  | Cleaned CSV/JSON dataset (`data/clean/`)                            | Thành viên 3                      |
| Embedding/Index & Agent     | Cleaned dataset (`data/clean/`)                          | MiniLM embedding, ChromaDB collection indexing, multi-LLM setup & RAG agent QA                  | Embedding manifest (`data/embeddings/`), ChromaDB index             | Thành viên 4                      |
| Evaluation                  | Cleaned dataset (`data/clean/`)                          | Tạo testset (question, ground_truth, doc_ids), đo Hit Rate, Token F1, LLM Judge               | Evaluation testset (`data/eval/`), metrics JSON (`data/results/`) | Thành viên 5                      |
| Observability & Reporting   | Cleaned / Corrupted / Repaired data                        | Data quality checks (completeness, validity), freshness status, Markdown reports                | Quality artifacts (`data/quality/`), Reports (`data/reports/`)    | Thành viên 6                      |
| Corruption Simulation       | Cleaned dataset (`data/clean/`)                          | Giả lập lỗi (delete latest, blank summary, noise, truncate title, stale date, duplicates)    | Corruption log (`data/results/corruption_log.json`)                 | Thành viên 6                      |
| Orchestration & Integration | Source modules & Config                                    | Điều phối E2E Baseline pipeline (`phase1.py`) và Corruption flow (`corruption_flow.py`) | Entrypoint scripts (`script/`), E2E pipeline execution              | Nguyễn Văn Hùng (Trưởng nhóm) |

## 4. Cách tái hiện kết quả

### Cấu hình không chứa secret

| Biến/cấu hình             | Giá trị sử dụng |
| ---------------------------- | ------------------- |
| `LLM_PROVIDER`             | [Giá trị]         |
| `LLM_MODEL`                | [Giá trị]         |
| Embedding model              | [Giá trị]         |
| Số lượng Crossref records | [Giá trị]         |
| Retrieval`top_k`           | [Giá trị]         |
| Freshness threshold          | [Giá trị]         |
| Random seed, nếu có        | [Giá trị]         |

Không dán nội dung API key hoặc file `.env` vào báo cáo.

### Lệnh cài đặt

Chỉ giữ lại cách nhóm đã dùng.

```bash
uv sync
```

Hoặc:

```bash
python -m pip install -e .
```

### Lệnh chạy

Baseline:

```bash
uv run python script/run_phase1.py
```

Hoặc với môi trường `pip` đã kích hoạt:

```bash
python script/run_phase1.py
```

Corruption flow:

```bash
uv run python script/run_corruption_flow.py
```

Hoặc với môi trường `pip` đã kích hoạt:

```bash
python script/run_corruption_flow.py
```

### Kết quả tái hiện

| Lệnh             | Trạng thái                                    | Thời điểm chạy gần nhất | Bằng chứng                         |
| ----------------- | ----------------------------------------------- | ----------------------------- | ------------------------------------ |
| Baseline pipeline | [Thành công/Thất bại một phần/Thất bại] | [Thời gian]                  | [Artifact hoặc log đã che secret] |
| Corruption flow   | [Thành công/Thất bại một phần/Thất bại] | [Thời gian]                  | [Artifact hoặc log đã che secret] |

## 5. Ingestion, cleaning và data contract

### Nguồn dữ liệu

| Thuộc tính                | Giá trị                             |
| --------------------------- | ------------------------------------- |
| Source                      | [Crossref endpoint/dataset thực tế] |
| Query/filter                | [Query hoặc filter]                  |
| Thời điểm lấy dữ liệu | [Timestamp]                           |
| Số record nhận được    | [Số lượng]                         |
| Cơ chế retry/backoff      | [Mô tả ngắn]                       |

### Raw và clean schema

| Trường        | Kiểu dữ liệu | Bắt buộc?  | Ý nghĩa   | Xử lý khi thiếu/sai |
| --------------- | --------------- | ------------ | ----------- | ---------------------- |
| [Tên trường] | [Kiểu]         | [Có/Không] | [Ý nghĩa] | [Cách xử lý]        |
| [Tên trường] | [Kiểu]         | [Có/Không] | [Ý nghĩa] | [Cách xử lý]        |

### Quy tắc cleaning

| Quy tắc                                 | Quality dimension liên quan | Số record bị tác động | Cách xác minh      |
| ---------------------------------------- | ---------------------------- | -------------------------: | -------------------- |
| [Ví dụ: loại record không có title] | [Completeness/Validity/...]  |              [Số lượng] | [Artifact/kiểm tra] |
| [Quy tắc thực tế]                     | [Dimension]                  |              [Số lượng] | [Artifact/kiểm tra] |

Giải thích cách nhóm tạo `text_for_embedding`, document ID và `age_days`:

[Mô tả tại đây.]

## 6. Evaluation setup

| Thành phần                             | Cấu hình thực tế          |
| ---------------------------------------- | ----------------------------- |
| Số câu hỏi                            | [Số lượng]                 |
| Các`question_type`                    | [Danh sách]                  |
| Ground-truth document ID                 | [Cách tạo/đối chiếu]     |
| Embedding model                          | [Tên model]                  |
| Vector store/collection                  | [Tên/config]                 |
| Retrieval`top_k`                       | [Giá trị]                   |
| LLM provider/model                       | [Giá trị]                   |
| Test set dùng chung cho ba trạng thái | [Đường dẫn hoặc ID/hash] |

Giải thích vì sao test set được giữ nguyên khi đánh giá baseline, corrupted và repaired:

[Giải thích tại đây.]

## 7. Kết quả baseline

### Artifact checklist

| Artifact                 | Đường dẫn thực tế                | Trạng thái | Ghi chú   |
| ------------------------ | -------------------------------------- | ------------ | ---------- |
| Raw response/records     | `data/raw/`                          | [Có/Thiếu] | [Ghi chú] |
| Cleaned dataset          | `data/clean/`                        | [Có/Thiếu] | [Ghi chú] |
| Embedding manifest/index | `data/embeddings/`                   | [Có/Thiếu] | [Ghi chú] |
| Evaluation set           | `data/eval/`                         | [Có/Thiếu] | [Ghi chú] |
| Baseline metrics         | `data/results/baseline_metrics.json` | [Có/Thiếu] | [Ghi chú] |
| Quality/freshness        | `data/quality/`                      | [Có/Thiếu] | [Ghi chú] |
| Baseline report          | `data/reports/phase1_report.md`      | [Có/Thiếu] | [Ghi chú] |

### Baseline metrics

| Metric                 |       Giá trị | Diễn giải                             |
| ---------------------- | --------------: | --------------------------------------- |
| `retrieval_hit_rate` |     [Giá trị] | [Ý nghĩa trong kết quả của nhóm]  |
| `mean_token_f1`      |     [Giá trị] | [Diễn giải]                           |
| `judge_accuracy`     |     [Giá trị] | [Diễn giải]                           |
| `mean_judge_score`   |     [Giá trị] | [Diễn giải]                           |
| Ragas, nếu có        | [Giá trị/N/A] | [Diễn giải hoặc lý do không chạy] |

## 8. Data quality và freshness

### Quality checks

| Check        | Quality dimension | Ngưỡng/kỳ vọng | Kết quả baseline      | Bằng chứng |
| ------------ | ----------------- | ------------------ | ----------------------- | ------------ |
| [Tên check] | [Dimension]       | [Ngưỡng]         | [Pass/Fail + giá trị] | [Artifact]   |
| [Tên check] | [Dimension]       | [Ngưỡng]         | [Pass/Fail + giá trị] | [Artifact]   |

### Freshness

| Thuộc tính               | Giá trị                           |
| -------------------------- | ----------------------------------- |
| Freshness được đo tại | [Dataset/index/artifact]            |
| Timestamp mới nhất       | [Giá trị]                         |
| Ngưỡng freshness         | [Giá trị]                         |
| Trạng thái baseline      | [Fresh/Stale/Unknown]               |
| Lý do                     | [Giải thích dựa trên số liệu] |

## 9. Corruption scenarios và repair

| Corruption         | Cách tạo | Record bị tác động | Quality signal kỳ vọng | Tác động thực tế | Cách repair   |
| ------------------ | ---------- | ---------------------: | ------------------------ | --------------------- | -------------- |
| [Loại corruption] | [Mô tả]  |          [Số lượng] | [Kỳ vọng]              | [Artifact/metric]     | [Cách repair] |
| [Loại corruption] | [Mô tả]  |          [Số lượng] | [Kỳ vọng]              | [Artifact/metric]     | [Cách repair] |

Corruption log:

- Đường dẫn: `data/results/corruption_log.json`
- Trạng thái: [Có/Thiếu]
- Nhận xét: [Log có đủ loại corruption, record bị tác động và tham số hay không?]

Giải thích cách repair đảm bảo dữ liệu được phục hồi từ nguồn đáng tin cậy thay vì chỉ che kết quả lỗi:

[Giải thích tại đây.]

## 10. So sánh baseline, corrupted và repaired

| Metric/signal            | Baseline | Corrupted | Repaired | Thay đổi do corruption | Mức phục hồi | Nhận xét   |
| ------------------------ | -------: | --------: | -------: | -----------------------: | --------------: | ------------ |
| `retrieval_hit_rate`   |      [ ] |       [ ] |      [ ] |                      [ ] |             [ ] | [Nhận xét] |
| `mean_token_f1`        |      [ ] |       [ ] |      [ ] |                      [ ] |             [ ] | [Nhận xét] |
| `judge_accuracy`       |      [ ] |       [ ] |      [ ] |                      [ ] |             [ ] | [Nhận xét] |
| `mean_judge_score`     |      [ ] |       [ ] |      [ ] |                      [ ] |             [ ] | [Nhận xét] |
| Quality checks pass/fail |      [ ] |       [ ] |      [ ] |                      [ ] |             [ ] | [Nhận xét] |
| Freshness status         |      [ ] |       [ ] |      [ ] |                      [ ] |             [ ] | [Nhận xét] |

Nêu ít nhất hai kết luận có quan hệ nhân quả được hỗ trợ bởi artifacts:

1. [Corruption/data change] → [quality/freshness signal] → [retrieval/answer metric].
2. [Repair action] → [quality/freshness recovery] → [agent metric recovery hoặc lý do chưa recovery].

Không kết luận corruption “có tác động” nếu số liệu không cho thấy thay đổi. Nếu kết quả khác kỳ vọng, mô tả giả thuyết và cách nhóm đã kiểm tra.

## 11. Vấn đề tích hợp quan trọng

Mô tả một vấn đề phát sinh khi ghép các module trong pipeline và cách nhóm xử lý:

- **Triệu chứng:** [Lỗi hoặc kết quả sai.]
- **Nguyên nhân:** [Root cause.]
- **Cách xử lý:** [Thay đổi đã thực hiện.]
- **Cách xác minh:** [Lệnh và artifact.]

## 12. Giới hạn và hướng cải thiện

| Giới hạn hiện tại | Ảnh hưởng   | Hướng cải thiện có thể kiểm chứng |
| --------------------- | -------------- | ----------------------------------------- |
| [Giới hạn]          | [Ảnh hưởng] | [Đề xuất]                              |
| [Giới hạn]          | [Ảnh hưởng] | [Đề xuất]                              |

## 13. Checklist trước khi nộp

- [ ] Thông tin nhóm và repository chính xác.
- [ ] Phân công khớp với module, artifact và kết quả thực tế.
- [ ] Lệnh tái hiện đã được chạy lại trên phiên bản dùng để nộp.
- [ ] Baseline, corrupted và repaired dùng cùng evaluation set.
- [ ] Bảng metrics khớp với các file trong `data/results/`.
- [ ] Quality/freshness conclusions khớp với `data/quality/`.
- [ ] Các đường dẫn báo cáo và artifact truy cập được.
- [ ] Mỗi thành viên đã hoàn thành báo cáo vai trò riêng.
- [ ] Không có `.env`, API key, token hoặc secret trong source, report, log hay ảnh.
