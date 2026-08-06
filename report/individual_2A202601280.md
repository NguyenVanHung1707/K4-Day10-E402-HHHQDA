# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

<<<<<<< HEAD
| Thông tin | Nội dung |
| --- | --- |
| Họ và tên | Phạm Công Đăng |
| MSSV | 2A202601280 |
| Khóa/Lớp | K4 |
| Tên nhóm | Nhóm 6 Thành Viên |
| Vai trò chính | Vector Indexing & RAG Agent Owner (TV4) |
| Repository | `DAY10_2A202601284_NguyenVanHung` |
| Ngày hoàn thành | 2026-08-06 |
=======
| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Họ và tên       | Phạm Công Đăng             |
| MSSV               | 2A202601280                |
| Khóa/Lớp         | K4                         |
| Tên nhóm         | Nhóm 6 Thành Viên          |
| Vai trò chính    | Vector Indexing & RAG Agent Owner |
| Repository         | https://github.com/NguyenVanHung1707/K4-Day10-E402-HHHQDA.git |
| Ngày hoàn thành | 2026-08-06                 |
>>>>>>> 41af95a (docs: complete group report and all 6 individual role reports with E2E metrics)

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

<<<<<<< HEAD
| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| --- | --- | --- | --- | --- |
| Embedding và Vector Store | `src/retrieval/embeddings.py`, `src/retrieval/index.py`; `MiniLMEmbeddings`, `LocalEmbeddingIndex` | `CleanPaperRecordSchema`, đặc biệt `paper_id`, `title`, `summary`, `text_for_embedding`; các dataset baseline/corrupted/repaired | Ba ChromaDB collection và ba manifest trong `data/embeddings/` | Hoàn thành |
| Đa LLM provider | `src/retrieval/llm.py`; `build_llm` | `Settings`, `LLM_PROVIDER`, `LLM_MODEL` và credential của provider được chọn | Lớp chat model tương ứng cho Gemini, OpenAI, Anthropic, OpenRouter, Ollama hoặc custom endpoint | Hoàn thành |
| RAG Agent và QA | `src/retrieval/agent.py`, `src/retrieval/qa.py`; `build_agent`, `run_agent_question`, `answer_question` | `Settings`, `LocalEmbeddingIndex`, câu hỏi và `top_k` | Semantic search, exact lookup, câu trả lời, danh sách document ID/context/title đã retrieve | Hoàn thành |
| Re-index corrupted và repaired | `LocalEmbeddingIndex.build/load` | `papers_clean_corrupted.csv`, `papers_clean_repaired.csv` | Collections `papers-corrupted`, `papers-repaired` và manifest tương ứng | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| --- | --- | --- |
| Bàn giao Agent/index cho Evaluation | TV5 — `src/evaluation/metrics.py` | Baseline, corrupted và repaired index đều load/query được để TV5 dùng cùng evaluation set đo metrics |
| Kiểm tra contract dữ liệu đầu vào | TV3 — Cleaning/Repair | Xác nhận baseline và repaired đều có 24 record đúng schema; repaired khớp baseline theo từng trường |
| Kiểm tra artifact corruption trước khi re-index | TV6 — Corruption/Observability | Xác nhận corrupted dataset có 25 dòng và đủ 6 loại corruption trong log; giữ duplicate có chủ đích khi index |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| --- | --- | --- | --- |
| Tạo embedding MiniLM và baseline index | `embeddings.py`, `index.py`, `data/embeddings/papers_embeddings.json` | Collection `papers-baseline`, đủ 24/24 document | Load manifest/collection, kiểm tra `collection.count() == 24`, semantic search trả top-k |
| Xây RAG Agent | `agent.py`, `qa.py` | Agent dùng semantic search hoặc exact lookup, trả lời có `paper_id`; xử lý câu hỏi rỗng và content blocks | Chạy câu hỏi Gemini end-to-end; kết quả có đúng title và `paper_id` |
| Re-index dữ liệu lỗi | `data/embeddings/papers_embeddings_corrupted.json` | Collection `papers-corrupted`, đủ 25 document, mỗi `record_id` duy nhất dù có duplicate `paper_id` | Load lại collection, `count() == 25`, semantic và exact lookup đều thành công |
| Re-index dữ liệu phục hồi | `data/embeddings/papers_embeddings_repaired.json` | Collection `papers-repaired`, đủ 24 document; manifest document khớp baseline | So sánh manifest baseline/repaired và kiểm tra `count() == 24` |
| Chuẩn hóa Chroma metadata | `LocalEmbeddingIndex._metadata_value` trong `index.py` | Không còn giá trị `NaN` trong corrupted/repaired manifest | Parse hai manifest và kiểm tra đệ quy `has_nan == False` |

Một output cụ thể do phần việc của tôi tạo ra là `data/embeddings/papers_embeddings_repaired.json`. Artifact chứa 24 document của collection `papers-repaired`; sau khi chuẩn hóa metadata, phần `documents` khớp hoàn toàn với baseline manifest. Repaired Agent load collection này thành công, exact lookup đưa đúng tài liệu lên hạng đầu và Gemini trả đúng title kèm `paper_id`.
=======
| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao  | Trạng thái                                 |
| ------------------ | --------------------- | ---------------- | ----------------- | -------------------------------------------- |
| Vector Indexing    | `src/retrieval/index.py`, `src/retrieval/embeddings.py` | Cleaned Dataset (`data/clean/papers_clean.json`) | ChromaDB collection (`papers-baseline`, `papers-corrupted`, `papers-repaired`) và `data/embeddings/papers_embeddings.json` | Hoàn thành |
| Multi-LLM Provider & RAG Agent | `src/retrieval/llm.py`, `src/retrieval/agent.py`, `src/retrieval/qa.py` | Query từ người dùng / Evaluation set | Câu trả lời từ RAG Agent và retrieved doc IDs | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động                         | Thành viên/module được hỗ trợ | Kết quả                    |
| ------------------------------------ | ------------------------------------ | ---------------------------- |
| Phối hợp kết nối Vector Database | TV5 (Evaluation Owner) | Đã cung cấp interface `LocalEmbeddingIndex` hỗ trợ hàm `search` và `lookup` để TV5 đo đạc metrics |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao       | Cách xác minh         |
| --------------------------- | ----------------------------- | ------------------------- | ----------------------- |
| Xây dựng Vector Embedding Index | `src/retrieval/index.py` | ChromaDB collection & manifest JSON | `python script/run_phase1.py` |
| Tích hợp Đa LLM Provider & Agent | `src/retrieval/agent.py`, `src/retrieval/llm.py` | RAG Agent truy vấn ngữ nghĩa | `python script/run_corruption_flow.py` |
>>>>>>> 41af95a (docs: complete group report and all 6 individual role reports with E2E metrics)

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
<<<<<<< HEAD

Phần TV4 chuyển cleaned dataset thành vector index có thể truy vấn và cung cấp lớp RAG Agent cho TV5 đánh giá. Index phải giữ document identity ổn định, tách riêng ba trạng thái baseline/corrupted/repaired, hỗ trợ semantic search và exact lookup, đồng thời không để dữ liệu lỗi ở một trạng thái ghi đè trạng thái khác.

### Cách triển khai

Tôi dùng `sentence-transformers/all-MiniLM-L6-v2` để mã hóa `text_for_embedding` thành vector đã normalize. Mỗi document được đưa vào ChromaDB với ID dạng `paper_id::row_index`; cách này vẫn giữ mỗi vector record duy nhất khi corrupted dataset cố ý chứa duplicate `paper_id`. Metadata gồm `paper_id`, `title`, `published`, authors, categories, summary và URL. Các ô CSV rỗng được chuẩn hóa từ `NaN` về chuỗi rỗng trước khi lưu để metadata có kiểu ổn định.

Ba đường dẫn manifest được ánh xạ sang ba collection `papers-baseline`, `papers-corrupted` và `papers-repaired`. RAG Agent có hai tool: semantic search top-k và exact lookup theo `paper_id`/title. System prompt yêu cầu Agent dùng tool, chỉ trả lời dựa trên corpus và trích dẫn `paper_id`. Lớp QA ưu tiên exact match khi câu hỏi chứa ID hoặc title trong dấu nháy, sau đó kết hợp semantic results và loại trùng.

### Input, output và contract

| Thành phần | Mô tả |
| --- | --- |
| Input | DataFrame theo `CleanPaperRecordSchema`; bắt buộc có `paper_id`, `title`, `text_for_embedding` và metadata liên quan |
| Output | `LocalEmbeddingIndex`, ChromaDB collection, embedding manifest; `AnswerResult` chứa answer, retrieved document IDs, contexts và titles |
| Module phụ thuộc | `src/core/config.py`, dữ liệu clean/repair của TV3 và corrupted dataset của TV6 |
| Module sử dụng output | `src/evaluation/metrics.py` của TV5, pipeline orchestration của TV1 và reporting của TV6 thông qua metrics |
| Điều kiện lỗi cần xử lý | Dataset/collection rỗng; câu hỏi rỗng; `top_k < 1` hoặc lớn hơn collection; metadata `NaN`; thiếu exact match; response LLM dạng text hoặc content blocks; duplicate `paper_id` trong corrupted data |

### Cách xác minh

```powershell
.\.venv\Scripts\python.exe -c "from pathlib import Path; from core.config import load_settings; from retrieval.index import LocalEmbeddingIndex; s=load_settings(Path.cwd()); i=LocalEmbeddingIndex.load(s, s.paths.repaired_embeddings_json); print(i.collection_name, i.collection.count(), len(i.search('retrieval augmented generation', top_k=4)))"
```

- **Kết quả mong đợi:** Load `papers-repaired`, có 24 document và semantic search trả 4 kết quả.
- **Kết quả thực tế:** `papers-repaired 24 4`; exact lookup và Gemini Agent cũng trả đúng title/`paper_id` trong kiểm thử end-to-end.
- **Artifact/log:** `data/embeddings/papers_embeddings.json`, `papers_embeddings_corrupted.json`, `papers_embeddings_repaired.json` và `data/chroma/`; không chứa secret.

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Corrupted dataset có ba nhóm duplicate `paper_id`. Nếu dùng trực tiếp `paper_id` làm Chroma ID, thao tác add sẽ lỗi hoặc ghi đè, làm mất chính corruption cần đo.
- **Các phương án đã cân nhắc:** (1) Deduplicate trước khi index; (2) dùng `paper_id` làm ID duy nhất và upsert; (3) tạo `record_id = paper_id::row_index` nhưng vẫn giữ `paper_id` trong metadata.
- **Phương án đã chọn:** Phương án 3.
- **Lý do:** Giữ nguyên dataset lỗi để đánh giá đúng tác động, tránh xung đột Chroma ID, đồng thời `paper_id` vẫn ổn định để đối chiếu `ground_truth_doc_ids`. Đổi lại, exact lookup theo `paper_id` đại diện cho một document trong nhóm duplicate, còn semantic index vẫn chứa đủ mọi dòng lỗi.
- **Bằng chứng quyết định phù hợp:** Collection corrupted có đủ 25/25 dòng, ba nhóm duplicate vẫn tồn tại, nhưng toàn bộ 25 `record_id` là duy nhất và collection load/query được.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** Repaired CSV khớp baseline theo từng trường nhưng phép so sánh manifest trả `documents_match_baseline=False`; khác biệt đầu tiên là `categories_joined`, baseline có `''` còn repaired có `nan` kiểu `float`.
- **Lệnh hoặc bước tái hiện:** Build repaired index từ `pd.read_csv(...)`, sau đó đọc hai manifest JSON và so sánh từng document/metadata.
- **Nguyên nhân gốc:** Pandas mặc định chuyển ô CSV rỗng thành `NaN`; `_build_documents` trước đó ghi thẳng giá trị này vào Chroma metadata và manifest.
- **Cách xử lý:** Thêm `LocalEmbeddingIndex._metadata_value` để đổi `None`/`NaN` thành chuỗi rỗng, chuyển scalar NumPy về scalar Python và stringify kiểu không được Chroma hỗ trợ. Sau đó rebuild corrupted và repaired collections.
- **Cách xác minh sau khi sửa:** Repaired manifest có `documents` bằng baseline; cả corrupted và repaired manifest đều không còn `NaN`; collection counts lần lượt là 25 và 24.
- **Điều học được:** DataFrame có thể đúng về mặt hiển thị nhưng sai kiểu ở ranh giới serialization. Contract cần kiểm tra cả giá trị lẫn kiểu trước khi ghi vào vector store.

Blocker còn lại ngoài phạm vi TV4: `baseline_metrics.json`, `corrupted_metrics.json`, `repaired_metrics.json` lần lượt ghi 10, 10 và 5 samples, trong khi `data/eval/test.json` hiện chỉ có 2 sample với `ground_truth_doc_ids` dạng `doc_001`, `doc_002` không khớp `paper_id` Crossref. Vì vậy phép so sánh metrics chưa chứng minh được ba trạng thái dùng cùng một evaluation set; TV5/TV1 cần tái tạo test set hợp lệ và chạy lại cả ba evaluation.

## 7. Hiểu biết về luồng end-to-end

**1. Dữ liệu đi từ Crossref đến vector index như thế nào?**

TV2 gọi Crossref API, parse metadata và lưu raw response/raw records trong `data/raw/`. TV3 loại record không hợp lệ, chuẩn hóa text/date, tạo `paper_id`, `age_days` và `text_for_embedding`, rồi lưu CSV/JSON trong `data/clean/`. TV4 đọc cleaned dataset, dùng MiniLM tạo vector, nạp vector cùng metadata vào ChromaDB và lưu manifest trong `data/embeddings/`.

**2. Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?**

Mỗi sample có câu hỏi, đáp án chuẩn và `ground_truth_doc_ids`. Agent trả answer cùng `retrieved_doc_ids`. Nếu ít nhất một ID retrieve nằm trong ground truth thì sample là retrieval hit; tỷ lệ trên toàn test set tạo `retrieval_hit_rate`. Answer được so với ground truth bằng token F1 và LLM judge. ID phải cùng quy ước với `paper_id` trong index thì kết quả mới có ý nghĩa.

**3. Quality checks khác freshness monitoring ở điểm nào trong bài lab?**

Quality checks kiểm tra nhiều chiều như completeness, validity và uniqueness: thiếu title/summary, null, duplicate ID hoặc sai schema. Freshness monitoring tập trung vào thời gian xuất bản, so `age_days`/published date với ngưỡng 180 ngày để xác định Fresh/Stale. Freshness là một chiều chất lượng cụ thể nhưng cần artifact và tín hiệu riêng để phát hiện dữ liệu cũ.

**4. Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?**

Giữ nguyên câu hỏi, đáp án chuẩn và ground-truth IDs giúp biến độc lập chính chỉ còn trạng thái dữ liệu/index. Nếu đổi test set hoặc số sample, chênh lệch metric có thể do độ khó câu hỏi thay vì corruption/repair, nên không thể kết luận quan hệ nhân quả công bằng.

**5. Repair được xem là thành công dựa trên artifact và metric nào?**

Ở tầng TV4, repaired CSV/manifest phải phục hồi document/schema so với baseline, collection phải load/query được và retrieval của tài liệu mục tiêu phải trở lại. Ở mức end-to-end còn cần repaired quality/freshness trở lại Pass/Fresh và các metric `retrieval_hit_rate`, `mean_token_f1`, `judge_accuracy`, `mean_judge_score` tiến gần baseline trên đúng cùng test set. Hiện artifact index đã phục hồi, nhưng evaluation cần chạy lại do số sample chưa đồng nhất.

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| --- | ---: | ---: | ---: | --- |
| `retrieval_hit_rate` | 0.90 | 0.40 | 0.90 | File metrics cho thấy giảm 0.50 rồi phục hồi về baseline, nhưng repaired chỉ ghi 5 samples nên cần chạy lại cùng test set |
| `mean_token_f1` | 0.842 | 0.325 | 0.821 | Giảm 0.517 khi corrupted và phục hồi gần baseline; chưa đủ so sánh công bằng do số sample khác nhau |
| `judge_accuracy` | 0.90 | 0.30 | 0.90 | Artifact ghi nhận giảm mạnh và phục hồi hoàn toàn, nhưng cần xác minh lại trên cùng test set |
| `mean_judge_score` | 4.50 | 2.10 | 4.40 | Gần phục hồi baseline; vẫn chịu cùng blocker về evaluation set |
| Quality checks | 5/5 Pass | 2/5 Pass | Chưa có artifact riêng | Corrupted fail ở uniqueness, summary validity và freshness; repaired dataset khớp baseline nhưng TV6 chưa xuất repaired quality artifact |
| Freshness status | Fresh, 0/24 stale | Stale, 2/25 stale | Chưa có artifact riêng | Baseline/corrupted có bằng chứng; không tự kết luận repaired Fresh khi thiếu report của TV6 |

### Kết luận từ số liệu

1. Kịch bản corruption tổng hợp (drop latest, blank/noise summary, truncate title, stale date, duplicate) → quality giảm từ 5/5 xuống 2/5 Pass và freshness chuyển Fresh thành Stale → artifact metrics ghi retrieval hit rate giảm `0.90 → 0.40`, token F1 giảm `0.842 → 0.325`.
2. Repair lại từ nguồn raw và rebuild `papers-repaired` → repaired dataset/manifest khớp baseline ở tầng TV4 → artifact metrics ghi retrieval hit rate `0.90`, token F1 `0.821`; tuy nhiên chưa thể xác nhận quan hệ nhân quả cuối cùng cho đến khi TV5 chạy cùng test set và TV6 tạo repaired quality/freshness report.

**Corruption nào ảnh hưởng rõ nhất và vì sao?**

Artifacts hiện chỉ có metrics cho kịch bản tổng hợp, không có ablation metric cho từng corruption nên không thể khẳng định trung thực một loại riêng lẻ ảnh hưởng mạnh nhất. Về tín hiệu trực tiếp, duplicate làm uniqueness fail (`22/25` ID unique), blank summary làm summary validity fail (`24/25` hợp lệ), stale date làm freshness fail (`2/25` stale), còn drop/noise/truncate có khả năng ảnh hưởng retrieval. Muốn xác định loại ảnh hưởng nhất cần tạo từng corruption độc lập và đo cùng test set.

**Kết quả nào khác với kỳ vọng ban đầu?**

Repaired metrics có giá trị gần baseline như kỳ vọng, nhưng `samples=5` thay vì 10; `data/eval/test.json` lại chỉ có 2 câu hỏi không khớp corpus. Đây là khác biệt quan trọng vì report số đẹp nhưng chưa tái hiện được từ evaluation artifact hiện tại. Cách kiểm tra là đối chiếu trường `samples`, đếm test set và so `ground_truth_doc_ids` với `paper_id` trong manifest. Nhóm cần tái tạo test set từ cleaned Crossref data rồi chạy lại cả ba trạng thái.

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. Data contract ở ranh giới cleaning → vector store phải ổn định cả document ID, giá trị và kiểu dữ liệu; một ô rỗng bị đọc thành `NaN` cũng có thể làm manifest sai khác.
2. Data quality/observability giúp phát hiện nguyên nhân trước khi nhìn thấy câu trả lời Agent sai: duplicate, summary rỗng và stale date đã tạo các tín hiệu fail riêng biệt.
3. Chất lượng retrieval phụ thuộc trực tiếp vào corpus/index, nhưng muốn chứng minh tác động phải giữ nguyên evaluation set; metric từ số sample khác nhau không đủ làm bằng chứng nhân quả.

### Nếu có thêm thời gian

Tôi sẽ bổ sung automated tests cho ba collection và một evaluation test set được sinh trực tiếp từ `paper_id` Crossref. Test sẽ kiểm tra schema/metadata không có `NaN`, collection count, exact lookup, retrieval hit trên cùng sample IDs và chênh lệch baseline–corrupted–repaired. Cải thiện được đo bằng khả năng chạy lại toàn bộ test/evaluation với cùng test-set hash và kết quả artifact nhất quán.

## 10. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.
=======
Chuyển đổi dữ liệu bài báo học thuật đã làm sạch thành vector embeddings, nạp vào ChromaDB vector database và xây dựng RAG Agent có khả năng Semantic Search + Lookup để trả lời câu hỏi chính xác.

### Cách triển khai
- Dùng `sentence-transformers/all-MiniLM-L6-v2` để vector hóa chuỗi `text_for_embedding`.
- Nạp vào ChromaDB `PersistentClient` với khoảng cách Cosine Similarity.
- Hỗ trợ đa LLM Provider trong `llm.py` (Gemini, OpenAI, Anthropic, OpenRouter, Ollama).

## 5. Phân tích kết quả Metrics

| Metric/signal          | Baseline | Corrupted | Repaired | Nhận xét cá nhân |
| ---------------------- | -------: | --------: | -------: | ------------------------- |
| `retrieval_hit_rate` |     1.00 |     0.875 |     1.00 | Dữ liệu lỗi làm giảm hit rate, repair giúp phục hồi 100% |
| `mean_token_f1`      |   0.2705 |    0.2188 |   0.2705 | Độ tương đồng token phục hồi hoàn toàn sau khi repair |

## 6. Cam kết của thành viên
- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
>>>>>>> 41af95a (docs: complete group report and all 6 individual role reports with E2E metrics)

**Họ và tên:** Phạm Công Đăng  
**Ngày xác nhận:** 2026-08-06
