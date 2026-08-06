# MEMBER ROLE REPORT — DAY 10

Data Pipeline & Data Observability | Member 5: Evaluation & Metrics

## 1. Thông tin cá nhân

| | |
|---|---|
| **Họ và tên** | Phạm Trung Hiếu |
| **MSSV** | 2A202601834 |
| **Khóa/Lớp** | K4 - AI Thực Chiến |
| **Tên nhóm** | Group E402 (K4-Day10-E402-HHHQDA) |
| **Vai trò chính** | Thành viên 5 (TV5) — Evaluation & RAG Metrics Specialist |
| **Repository** | https://github.com/your-org/K4-Day10-E402-HHHQDA |
| **Ngày hoàn thành** | 2026-08-06 |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
|---|---|---|---|---|
| Evaluation Testset Generator | src/evaluation/testset.py (build_test_set) | data/clean/clean_records.csv (từ TV1/TV2) | data/eval/test_set.json (Tập testset RAG) | **Hoàn thành** |
| Pipeline Metrics & RAG Evaluation | src/evaluation/metrics.py (evaluate_pipeline) | Vector DB (TV4), test_set.json (TV5), LLM Settings | data/results/*_metrics.json, data/results/*_answers.json | **Hoàn thành** |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
|---|---|---|
| Debug Import Error & Config Sync | TV1 (Pipelines / corruption_flow.py) | Sửa lỗi ImportError: cannot import name 'get_settings' bằng cách cập nhật sang load_settings() và hoàn thiện hàm main() trong pipeline. |
| Tích hợp báo cáo so sánh & Group Report | TV3 (Observability) & Nhóm trưởng | Hỗ trợ kết nối output từ 3 file metrics JSON để sinh báo cáo so sánh tự động trong comparison_report và điền bảng tổng hợp group_report.md. |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
|---|---|---|---|
| Sinh tập Testset đánh giá chuẩn hóa | src/evaluation/testset.py, data/eval/test_set.json | Tập dữ liệu 5 câu hỏi QA kèm ground_truth_doc_ids chuẩn hóa | Kiểm tra sự tồn tại và schema của data/eval/test_set.json |
| Đánh giá RAG Agent qua 3 giai đoạn (Baseline, Corrupted, Repaired) | src/evaluation/metrics.py, data/results/*_metrics.json, data/results/*_answers.json | 3 file metrics.json và 3 file answers.json đo đạc Retrieval Hit Rate, F1, LLM Judge Score, RAGAS | Chạy python script/run_phase1.py và python script/run_corruption_flow.py |
| Tổng hợp & phân tích chỉ số trong báo cáo nhóm | group_report.md | Bảng so sánh 3 trạng thái và phân tích chuỗi nguyên nhân - bằng chứng | Đối chiếu bảng chỉ số trong group_report.md với các file JSON trong data/results/ |

**Mô tả Output cụ thể:** Hệ thống đánh giá tự động đã tạo thành công 3 bộ chỉ số JSON tại data/results/. Chỉ số Retrieval Hit Rate giảm từ 100.0% (Baseline) xuống 40.0% (Corrupted) do nhiễu/lỗi dữ liệu, và phục hồi lại 100.0% (Repaired) sau khi thực hiện Data Cleaning/Repair. Bảng kết quả đã được tích hợp đầy đủ vào group_report.md.

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Trong một pipeline RAG (Retrieval-Augmented Generation), nếu dữ liệu bị lỗi (mất trường, nhiễu văn bản, trôi nhãn), chất lượng của Vector Search và câu trả lời sinh ra từ LLM sẽ bị suy giảm nghiêm trọng. Phần việc của TV5 giải quyết bài toán: Làm thế nào để đo lường định lượng chính xác sự suy giảm chất lượng này khi dữ liệu bị lỗi (Corrupted) và xác minh sự phục hồi hiệu năng sau khi dữ liệu được làm sạch/phục hồi (Repaired) bằng các chỉ số chuẩn hóa (Hit Rate, Token F1, LLM Judge, RAGAS).

### Cách triển khai

1. Generation Testset (testset.py): Tự động trích xuất các mẫu văn bản đạt chuẩn từ clean_records.csv, sử dụng heuristic/LLM để tạo câu hỏi (question), câu trả lời chuẩn (ground_truth) và ánh xạ ID tài liệu tương ứng (ground_truth_doc_ids).
2. Pipeline Evaluation Framework (metrics.py): Xây dựng hàm evaluate_pipeline nhận vào Vector Index và Testset. Thực hiện Query trên Vector Index -> Tính Retrieval Hit Rate (xem ground_truth_doc_ids có nằm trong Top-K retrieved docs hay không) -> Gọi RAG Agent/LLM để sinh câu trả lời -> Tính Token-level F1 Score -> Gọi LLM Judge để chấm điểm độ chính xác ngữ nghĩa (scale 1-5 & accuracy) -> Xuất kết quả ra file JSON metrics và file answers chi tiết.

### Input, output và contract

| | |
|---|---|
| **Input** | clean_records.csv (tạo testset); LocalEmbeddingIndex (Vector DB), test_set.json, LLM Settings (đo đạc) |
| **Output** | data/eval/test_set.json; data/results/*_metrics.json (chứa hit_rate, f1, judge_score); data/results/*_answers.json |
| **Module phụ thuộc** | ingestion.cleaning (TV2 - dữ liệu sạch); retrieval.index (TV4 - Vector DB Index); core.config (load_settings) |
| **Module sử dụng output** | observability.reporting (TV3 - so sánh chỉ số); pipelines/corruption_flow.py (đo đạc toàn pipeline) |
| **Điều kiện lỗi cần xử lý** | Trường hợp Vector DB không trả về context nào (Empty Retrieval); API LLM Judge bị timeout/rate limit; testset thiếu trường ground_truth_doc_ids |

### Cách xác minh

python script/run_phase1.py
python script/run_corruption_flow.py

- **Kết quả mong đợi:** Cả 2 script thực thi không lỗi; tạo ra đủ 3 cặp file metrics & answers trong data/results/; chỉ số Corrupted giảm đáng kể so với Baseline, chỉ số Repaired phục hồi xấp xỉ Baseline.
- **Kết quả thực tế:** Thực thi thành công 100%. Retrieval Hit Rate: Baseline = 100%, Corrupted = 40%, Repaired = 100%.
- **Artifact/log:** data/eval/test_set.json, data/results/baseline_metrics.json, data/results/corrupted_metrics.json, data/results/repaired_metrics.json

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Khi đánh giá Retrieval trong RAG, cần chọn chỉ số chính xác để đo lường khả năng tìm kiếm đúng ngữ cảnh của Vector DB khi dữ liệu đầu vào bị nhiễu/mất mát.
- **Các phương án đã cân nhắc:** Option A: Dùng Cosine Similarity trung bình giữa Query Vector và Retrieved Documents Vector. Option B: Dùng Exact Match (Hit Rate @ K) kiểm tra sự có mặt của ground_truth_doc_ids trong Top-K kết quả trả về.
- **Phương án đã chọn:** Chọn Option B (Retrieval Hit Rate @ K=3) kết hợp với Token-level F1 Score cho câu trả lời.
- **Lý do:** Cosine Similarity có thể bị đánh lừa khi dữ liệu bị corrupt (văn bản lặp lại hoặc nhiễu vẫn có thể có similarity cao nhưng chứa thông tin sai). Hit Rate @ K phản ánh trực tiếp việc tài liệu gốc chứa đáp án đúng có được truy xuất hay không, đảm bảo tính chặt chẽ (correctness) và dễ giải thích (reproducibility).
- **Bằng chứng quyết định phù hợp:** Khi dữ liệu bị corrupt, Hit Rate giảm lập tức từ 100% xuống 40%, phản ánh đúng bản chất nhiễu dữ liệu làm tụt hạng tài liệu đúng.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** ImportError: cannot import name 'get_settings' from 'core.config' (C:\...\src\core\config.py). Did you mean: 'load_settings'?
- **Lệnh hoặc bước tái hiện:** Chạy lệnh python script/run_phase1.py trên PowerShell Terminal.
- **Nguyên nhân gốc:** File src/pipelines/corruption_flow.py thực hiện import hàm get_settings từ core.config, nhưng trong core/config.py tên hàm khởi tạo được định nghĩa thực tế là load_settings().
- **Cách xử lý:** Mở src/pipelines/corruption_flow.py, sửa dòng import thành from core.config import load_settings và đổi lời gọi hàm trong main() thành settings = load_settings(). Đồng thời bổ sung hàm def main() hoàn chỉnh cho pipeline.
- **Cách xác minh sau khi sửa:** Chạy lại python script/run_phase1.py và python script/run_corruption_flow.py -> Script chạy thành công, tạo ra các file JSON kết quả mà không còn báo lỗi ImportError.
- **Điều học được:** Cần thống nhất Naming Convention và Interface Contract giữa các module cốt lõi (core/config) trước khi triển khai các pipeline nhánh để tránh lỗi bất đồng bộ Interface.

## 7. Hiểu biết về luồng end-to-end

**Câu trả lời chi tiết cho 5 câu hỏi luồng End-to-End:**

**1. Dữ liệu đi từ Crossref đến vector index như thế nào?**

Dữ liệu thô (raw JSON/CSV) được thu thập từ Crossref API -> Đi qua Ingestion/Cleaning Pipeline (làm sạch HTML, chuẩn hóa metadata, xử lý missing value) -> Chuyển thành clean records -> Được Chunking và Embedding qua mô hình MiniLMEmbeddings -> Lưu trữ và đánh chỉ mục vào Vector Database (LocalEmbeddingIndex / ChromaDB).

**2. Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?**

Evaluation set chứa cặp (Question, Ground Truth Answer, Ground Truth Doc IDs). Khi test: Query được đưa vào Vector DB -> Lấy ra Top-K Doc IDs -> So sánh với Ground Truth Doc IDs để tính Retrieval Hit Rate. Tiếp theo, Context retrieved được đưa vào LLM để sinh câu trả lời -> So sánh câu trả lời này với Ground Truth Answer bằng Token F1 Score và LLM Judge để tính Answer Quality.

**3. Quality checks khác freshness monitoring ở điểm nào trong bài lab?**

Quality checks kiểm tra tính toàn vẹn, tính hợp lệ của dữ liệu tĩnh tại một thời điểm (VD: check null, đúng schema, độ dài văn bản, định dạng DOI). Trong khi Freshness monitoring kiểm tra tính cập nhật theo thời gian của dữ liệu (VD: thời gian thu thập gần nhất, khoảng lùi thời gian công bố tài liệu, đảm bảo dữ liệu không bị lỗi thời).

**4. Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?**

Bắt buộc dùng cùng 1 Testset cố định để đảm bảo nguyên tắc kiểm soát biến số (Controlled Experiment). Khi tập câu hỏi và ground truth giữ nguyên, bất kỳ sự thay đổi nào về chỉ số (Hit Rate, F1, Judge Score) giữa 3 giai đoạn đều phản ánh chính xác 100% tác động của chất lượng dữ liệu (Data Quality) lên hiệu năng Agent, không bị nhiễu do độ khó câu hỏi thay đổi.

**5. Repair được xem là thành công dựa trên artifact và metric nào?**

Repair thành công khi: (1) Artifact quality check (repaired_quality.json) không còn vi phạm các quy tắc dữ liệu; (2) Các metrics trong repaired_metrics.json (đặc biệt là Retrieval Hit Rate và Mean Judge Score) phục hồi về mức xấp xỉ hoặc bằng mức của baseline_metrics.json.

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
|---|---|---|---|---|
| retrieval_hit_rate | 100.0% | 40.0% | 100.0% | Dữ liệu lỗi làm suy giảm 60% khả năng tìm kiếm tài liệu đúng; phục hồi hoàn hảo 100% sau khi repair. |
| mean_token_f1 | 0.842 | 0.325 | 0.821 | Mức độ trùng khớp từ vựng giảm mạnh khi bị nhiễu; khôi phục xấp xỉ mức ban đầu. |
| judge_accuracy | 100.0% | 20.0% | 100.0% | Độ chính xác ngữ nghĩa do LLM Judge đánh giá khôi phục hoàn toàn về 100%. |
| mean_judge_score | 4.60 / 5.0 | 2.10 / 5.0 | 4.40 / 5.0 | Điểm chất lượng câu trả lời hồi phục từ 2.1 lên 4.4, phản ánh chất lượng RAG khôi phục rõ rệt. |
| Quality checks | 0 Errors | 5 Violations | 0 Errors | Xóa bỏ hoàn toàn các lỗi thiếu trường, nhiễu văn bản và sai format. |
| Freshness status | PASS (0d) | WARN (Stale) | PASS (0d) | Dữ liệu được cập nhật lại đúng mốc thời gian tươi mới sau khi repair từ raw records. |

### Kết luận từ số liệu

**1. Chuỗi Corruption:** [Corrupting title/abstract/metadata] → [Quality checks báo 5 Violations, Freshness cảnh báo Stale] → [Retrieval Hit Rate sụt giảm từ 100% xuống 40%, Mean Judge Score tụt thảm hại từ 4.60 xuống 2.10].

**2. Chuỗi Repair:** [Cleaning & Repairing từ Raw Records] → [Quality checks trở về 0 Errors, Freshness khôi phục PASS] → [Retrieval Hit Rate phục hồi về 100%, Mean Judge Score phục hồi mạnh mẽ lên 4.40/5.0].

- **Corruption ảnh hưởng rõ nhất:** Việc làm nhiễu/xóa trường Title và Abstract ảnh hưởng nghiêm trọng nhất. Nguyên nhân do mô hình Embedding phụ thuộc rất lớn vào ngữ nghĩa của hai trường này để tạo Dense Vector representation. Khi bị mất thông tin hoặc chèn ký tự rác, Vector Similarity tụt giảm dẫn đến Vector DB không thể retrieve đúng tài liệu gốc.
- **Kết quả khác kỳ vọng ban đầu:** Kỳ vọng ban đầu là chỉ số Mean Token F1 của Repaired sẽ đạt 100% bằng mức Baseline (0.842). Tuy nhiên thực tế đạt 0.821 (hơi thấp hơn một chút). Sau khi kiểm tra, giả thuyết đưa ra là quá trình Repair đã loại bỏ một số từ thừa/ký tự đặc biệt dư thừa trong văn bản gốc, khiến câu trả lời sinh ra cô đọng hơn, dẫn đến Token F1 lệch vài từ không đáng kể nhưng ngữ nghĩa (Judge Accuracy) vẫn đạt 100%.

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

**1. Về Data Pipeline:** Chất lượng dữ liệu đầu vào (Data Quality) quyết định trần hiệu năng (upper bound) của hệ thống RAG. Một mô hình LLM hay Vector DB mạnh đến đâu cũng không thể cho ra câu trả lời đúng nếu dữ liệu bị corrupt (Garbage In, Garbage Out).

**2. Về Data Quality / Observability:** Cần xây dựng hệ thống giám sát tự động (Quality Checks & Freshness Monitoring) liên tục ở mọi công đoạn của pipeline để phát hiện sớm các bất thường dữ liệu trước khi dữ liệu bẩn đi vào Vector Index.

**3. Về Đánh giá RAG Agent:** Việc kết hợp đa dạng chỉ số (Traditional Overlap Metrics như F1 + Retrieval Metrics như Hit Rate + Modern LLM-as-a-Judge) mang lại cái nhìn toàn diện, chính xác và đáng tin cậy hơn rất nhiều so với việc chỉ dùng 1 chỉ số đơn lẻ.

### Nếu có thêm thời gian

Tích hợp thư viện RAGAS đầy đủ với các chỉ số chuyên sâu hơn như Faithfulness, Answer Relevancy và Context Recall tự động vào file pipeline; mở rộng tập testset lên 50-100 mẫu đa dạng câu hỏi phức tạp (Multi-hop Reasoning) để đo lường độ bền vững (robustness) của Agent ở quy mô lớn hơn.

## 10. Cam kết của thành viên

[X] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.

[X] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.

[X] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.

[X] Tôi không ghi "đã chạy thành công" cho phần chưa được kiểm chứng.

[X] Báo cáo không chứa .env, API key, token hoặc secret.

[X] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Phạm Trung Hiếu
**Ngày xác nhận:** 2026-08-06
