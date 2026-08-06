# Hợp đồng Data Schema Chuẩn cho các Giai đoạn (Data Schema Contract)

Tài liệu này đóng vai trò là **Hợp đồng Dữ liệu (Data Contract)** chính thức do **Trưởng nhóm (TV1 - Nguyễn Văn Hưng)** chốt chuẩn hóa cho toàn bộ dự án Data Pipeline & Data Observability. 

Tất cả 6 thành viên trong nhóm phải tuân thủ nghiêm ngặt các tên trường (field names), kiểu dữ liệu (data types) và định dạng lưu trữ (formats) dưới đây để đảm bảo tích hợp hệ thống không bị lỗi.

---

## 1. Giai đoạn Ingestion — Dữ liệu Thô (Raw Data Schema)

- **Owner:** Thành viên 2 (Data Ingestion Owner)
- **Nguồn dữ liệu:** Crossref REST API (`https://api.crossref.org/works`)
- **Artifacts lưu trữ:** `data/raw/crossref_response.json`, `data/raw/crossref_records.json`

| Tên trường (Field) | Kiểu dữ liệu (Type) | Bắt buộc (Required) | Mô tả & Định dạng |
| :--- | :--- | :---: | :--- |
| `paper_id` | `string` | Có | Mã định danh duy nhất của bài báo (ví dụ: slug hóa từ DOI hoặc DOI dạng rút gọn) |
| `doi` | `string` | Có | Mã DOI chuẩn (Digital Object Identifier) |
| `title` | `string` | Có | Tiêu đề gốc của bài báo |
| `abstract` | `string` \| `null` | Không | Đoạn tóm tắt bài báo (vẫn còn ký tự HTML thô nếu có) |
| `authors` | `list[string]` | Có | Danh sách tên tác giả `["Tên Tác Giả 1", "Tên Tác Giả 2"]` |
| `categories` | `list[string]` | Có | Danh sách chủ đề/danh mục từ Crossref subject |
| `primary_category` | `string` | Có | Danh mục chính bài báo thuộc về |
| `published` | `string` | Có | Ngày xuất bản dạng ISO String (`YYYY-MM-DD`) |
| `updated` | `string` | Có | Ngày cập nhật gần nhất dạng ISO String (`YYYY-MM-DD`) |
| `abs_url` | `string` | Có | Đường dẫn URL tới trang bài báo |
| `pdf_url` | `string` | Không | Đường dẫn xem file PDF (nếu có) |
| `comment` | `string` | Không | Ghi chú hoặc thông tin bổ sung từ nguồn API |

---

## 2. Giai đoạn Cleaning & Data Modeling — Dữ liệu Sạch (Cleaned Data Schema)

- **Owner:** Thành viên 3 (Data Cleaning & Modeling Owner)
- **Input:** Raw records từ `data/raw/crossref_records.json`
- **Artifacts lưu trữ:** `data/clean/papers_clean.csv`, `data/clean/papers_clean.json`

| Tên trường (Field) | Kiểu dữ liệu (Type) | Bắt buộc (Required) | Quy tắc xử lý & Định dạng |
| :--- | :--- | :---: | :--- |
| `paper_id` | `string` | Có | Giữ nguyên định danh từ Raw Record |
| `title` | `string` | Có | Tiêu đề đã loại bỏ khoảng trắng thừa và ký tự đặc biệt |
| `summary` | `string` | Có | Abstract đã làm sạch thẻ HTML (`<p>`, `<sub>`, ...), loại bỏ nhiễu |
| `authors_joined` | `string` | Có | Tên tác giả gộp thành chuỗi cách nhau bởi dấu phẩy `", "` |
| `categories_joined` | `string` | Có | Các danh mục gộp thành chuỗi cách nhau bởi dấu phẩy `", "` |
| `primary_category` | `string` | Có | Danh mục chính của bài báo |
| `published` | `string` | Có | Định dạng ngày xuất bản chuẩn ISO `YYYY-MM-DD` |
| `updated` | `string` | Có | Định dạng ngày cập nhật chuẩn ISO `YYYY-MM-DD` |
| `age_days` | `integer` | Có | Số ngày tính từ ngày xuất bản (`published`) đến thời điểm chạy pipeline |
| `summary_chars` | `integer` | Có | Độ dài ký tự của đoạn summary đã làm sạch |
| `text_for_embedding` | `string` | Có | Đoạn văn bản hợp nhất dùng cho Vector Search: `Title: ... | Summary: ... | Authors: ... | Subject: ...` |
| `abs_url` | `string` | Có | URL trang bài báo |
| `pdf_url` | `string` | Không | URL xem trực tiếp PDF |

---

## 3. Giai đoạn Indexing & Vector Search — Vector DB Metadata Schema

- **Owner:** Thành viên 4 (Vector Indexing & RAG Agent Owner)
- **Input:** `data/clean/papers_clean.json`
- **Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2`
- **ChromaDB Collections:** `papers-baseline`, `papers-corrupted`, `papers-repaired`
- **Artifacts lưu trữ:** `data/embeddings/papers_embeddings.json`, database ChromaDB tại `data/chroma/`

| Thành phần Metadata | Kiểu dữ liệu | Ý nghĩa trong ChromaDB Metadata |
| :--- | :--- | :--- |
| `document_id` | `string` | Đặt trùng với `paper_id` |
| `document_text` | `string` | Nội dung được vector hóa (`text_for_embedding`) |
| `paper_id` | `string` | Metadata truy vấn chính xác |
| `title` | `string` | Metadata hỗ trợ hiển thị/lookup câu trả lời |
| `summary` | `string` | Metadata cung cấp ngữ cảnh cho RAG Agent |
| `authors` | `string` | Metadata tác giả |
| `published` | `string` | Metadata ngày xuất bản |
| `age_days` | `integer` | Metadata tuổi của bài báo (dùng để lọc freshness) |

---

## 4. Giai đoạn RAG Evaluation — Testset & Metrics Schema

- **Owner:** Thành viên 5 (Evaluation & Metrics Owner)
- **Artifacts lưu trữ:** `data/eval/test_set.json`, `data/results/baseline_metrics.json`, `corrupted_metrics.json`, `repaired_metrics.json`

### 4.1. Schema cho Evaluation Testset (`test_set.json`)
```json
[
  {
    "sample_id": "sample_001",
    "question": "Mô hình RAG agent giải quyết vấn đề gì trong bài báo của tác giả X?",
    "ground_truth": "Mô hình giúp cải thiện độ chính xác truy vấn trên dữ liệu tri thức lớn...",
    "ground_truth_doc_ids": ["doi_10_1016_j_artint_2025_01"],
    "question_type": "factual"
  }
]
```

### 4.2. Schema cho Results Metrics (`baseline_metrics.json`)
```json
{
  "retrieval_hit_rate": 0.85,
  "mean_token_f1": 0.78,
  "judge_accuracy": 0.90,
  "mean_judge_score": 4.25,
  "total_eval_samples": 20,
  "timestamp": "2026-08-06T15:00:00Z"
}
```

---

## 5. Giai đoạn Data Observability — Quality & Freshness Schema

- **Owner:** Thành viên 6 (Data Observability Owner)
- **Artifacts lưu trữ:** `data/quality/freshness_report.json`, `data/quality/quality_report.json`

### 5.1. Schema cho Data Quality Check
```json
{
  "total_records": 24,
  "checks": [
    {
      "check_name": "completeness_check",
      "dimension": "Completeness",
      "passed": true,
      "score": 1.0,
      "details": "Không có record bị rỗng title hoặc summary."
    },
    {
      "check_name": "validity_check",
      "dimension": "Validity",
      "passed": true,
      "score": 1.0,
      "details": "Tất cả các bản ghi đều có DOI và URL hợp lệ."
    }
  ]
}
```

### 5.2. Schema cho Freshness Report
```json
{
  "evaluated_at": "2026-08-06T15:00:00Z",
  "freshness_threshold_days": 180,
  "max_age_days_found": 45,
  "latest_publication_date": "2026-06-22",
  "status": "FRESH",
  "is_fresh": true
}
```

---

## 6. Giai đoạn Corruption & Repair — Log Schema

- **Owner:** Thành viên 6 (Corruption) & Thành viên 3 (Repair)
- **Artifacts lưu trữ:** `data/results/corruption_log.json`

```json
[
  {
    "corruption_type": "blank_summary",
    "affected_records": 5,
    "affected_paper_ids": ["paper_002", "paper_007"],
    "timestamp": "2026-08-06T15:05:00Z",
    "description": "Giả lập lỗi xóa rỗng nội dung summary để đo độ suy giảm retrieval."
  },
  {
    "corruption_type": "stale_pub_date",
    "affected_records": 3,
    "affected_paper_ids": ["paper_012"],
    "timestamp": "2026-08-06T15:05:00Z",
    "description": "Làm cũ ngày xuất bản lùi về 5 năm trước để kích hoạt cảnh báo Freshness STALE."
  }
]
```

---

## 📌 Quy tắc Đổi mới & Đảm bảo Tính Tích hợp

1. **Không thay đổi tên trường:** Tất cả mã nguồn Python (`crossref.py`, `cleaning.py`, `index.py`, `metrics.py`, `quality.py`) **bắt buộc** phải truy cập tên thuộc tính khớp chính xác với Hợp đồng Schema trên.
2. **Quản lý tập trung:** Khi cần bổ sung trường mới, phải báo cáo cho **Trưởng nhóm (TV1 - Nguyễn Văn Hưng)** để cập nhật tập trung trong `src/core/config.py`.
