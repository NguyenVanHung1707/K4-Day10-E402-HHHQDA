# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Họ và tên       | Nhữ Văn Hùng             |
| MSSV               | 2A202601372                     |
| Khóa/Lớp         | K4              |
| Tên nhóm         | Nhóm 6 Thành Viên (Lead: Nguyễn Văn Hùng)     |
| Vai trò chính    | Data Ingestion Owner (Crossref API & Raw Data)                 |
| Repository         | [DAY10_2A202601284_NguyenVanHung](https://github.com/NguyenVanHung1707/K4-Day10-E402-HHHQDA) |
| Ngày hoàn thành | 2026-08-06               |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao  | Trạng thái                                 |
| ------------------ | --------------------- | ---------------- | ----------------- | -------------------------------------------- |
| Thu thập dữ liệu thô (Ingestion)      | [crossref.py](src/ingestion/crossref.py) | Cấu hình tìm kiếm (`Settings` từ `config.py`) | Raw response và parsed records trong [data/raw/](data/raw/) | Hoàn thành |

- **Đầu vào (Input)**: Nhận `Settings` được chốt contract bởi Trưởng nhóm (TV1), chứa query tìm kiếm `"agentic retrieval augmented generation large language model"`, filter `"from-pub-date:..."`, và số lượng bản ghi tối đa `max_results = 24`.
- **Đầu ra (Output)**: Bàn giao file raw response của API [crossref_response.json](data/raw/crossref_response.json) và file dữ liệu thô dạng cấu trúc phẳng [crossref_records.json](data/raw/crossref_records.json).
- **Thành viên phụ thuộc**: **Thành viên 3 (Cleaning Owner - Đặng Minh Quang)** phụ thuộc trực tiếp vào đầu ra của tôi để tiến hành làm sạch dữ liệu.

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động                         | Thành viên/module được hỗ trợ | Kết quả                    |
| ------------------------------------ | ------------------------------------ | ---------------------------- |
| Thống nhất dữ liệu thô đầu vào | TV3 (Data Cleaning) | Chốt định dạng của lớp `PaperRecord` làm contract đầu vào cho hàm làm sạch dữ liệu trong pipeline. |
| Đảm bảo tính bất biến của nguồn dữ liệu thô | TV6 (Observability) & TV3 (Data Cleaning) | Dữ liệu thô gốc tại `data/raw/` được đảm bảo an toàn, không bị tác động bởi script corruption của TV6, giúp TV3 luôn có nguồn thô tin cậy để chạy module phục hồi dữ liệu (Repair). |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao       | Cách xác minh         |
| --------------------------- | ----------------------------- | ------------------------- | ----------------------- |
| Triển khai crawler gọi API Crossref | `src/ingestion/crossref.py` (hàm `fetch_source_records`) | File [crossref_response.json](data/raw/crossref_response.json) | Kiểm tra sự tồn tại và dung lượng file trên đĩa |
| Phân tích payload thô sang bản ghi cấu trúc phẳng | `src/ingestion/crossref.py` (hàm `parse_crossref_payload`) | File [crossref_records.json](data/raw/crossref_records.json) | Chạy script kiểm thử so khớp cấu trúc dữ liệu nạp |
| Xây dựng cơ chế tải ngược bản ghi thô | `src/ingestion/crossref.py` (hàm `load_raw_records`) | Khôi phục lại chính xác `list[PaperRecord]` từ JSON | Gọi hàm và assert so sánh phần tử |

### Output cụ thể được tạo ra:
- File phản hồi gốc từ API [crossref_response.json](data/raw/crossref_response.json) chứa đầy đủ payload thô của 24 bài báo khoa học liên quan đến RAG và Agentic AI được tải về từ hệ thống Crossref Works API.
- File [crossref_records.json](data/raw/crossref_records.json) chứa 24 bản ghi đã bóc tách phẳng, bỏ toàn bộ các thẻ XML học thuật nhiễu (JATS) và chuẩn hóa kiểu ngày tháng về ISO YYYY-MM-DD.

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Để xây dựng một RAG pipeline tin cậy cho bài báo khoa học, hệ thống cần một đầu vào dữ liệu thô chất lượng cao. API của Crossref chứa dữ liệu metadata học thuật khổng lồ nhưng cấu trúc JSON lồng nhau phức tạp, nhiều nhãn XML học thuật JATS, định dạng ngày tháng không đồng nhất và có nguy cơ bị từ chối dịch vụ (Rate limit) nếu gửi quá nhiều yêu cầu.

### Cách triển khai
- **Tương tác API**: Sử dụng thư viện `requests` gửi truy vấn có kèm theo headers lịch sự (`User-Agent` chứa email liên hệ) để đi vào hàng đợi ưu tiên (polite pool) của Crossref.
- **Xử lý lỗi mạng và giới hạn tần suất**: Triển khai vòng lặp thử lại tối đa 5 lần tích hợp thuật toán **Exponential Backoff** (chờ tăng dần theo lũy thừa $2^{\text{attempt}}$ giây) khi gặp mã lỗi HTTP `429` (Too Many Requests) hoặc `503` (Service Unavailable).
- **Loại bỏ nhiễu văn bản**: Sử dụng Regex `re.sub(r"<[^>]+>", "", abstract)` lọc bỏ toàn bộ các thẻ XML học thuật JATS (như `<jats:p>`, `</jats:p>`) trong phần tóm tắt để tránh làm nhiễu vector embedding sau này.
- **Chuẩn hóa ngày tháng**: Viết hàm `extract_date` bóc tách linh hoạt trường `date-parts` của Crossref (đáp ứng tốt cả các bài báo chỉ đăng năm `[2026]`, năm-tháng `[2026, 6]`, hoặc đầy đủ `[2026, 6, 15]`) và chuẩn hóa đồng nhất về chuỗi ISO `YYYY-MM-DD`.

### Input, output và contract

| Thành phần                   | Mô tả                                     |
| ------------------------------ | ------------------------------------------- |
| Input                          | Thực thể `Settings` chứa query `"agentic retrieval augmented generation large language model"`, filter `"has-abstract:true"`, và giới hạn `max_results = 24`. |
| Output                         | Trả về `list[PaperRecord]`, đồng thời xuất bản hai file lưu trữ thô tại `data/raw/`. |
| Module phụ thuộc             | Cấu hình `src/core/config.py` và các hàm tiện ích của `src/core/utils.py`. |
| Module sử dụng output        | Module làm sạch dữ liệu `src/ingestion/cleaning.py` của TV3. |
| Điều kiện lỗi cần xử lý | Lỗi quá tải/giới hạn tần suất từ API Crossref; bản ghi thiếu thông tin cốt lõi (DOI, title, abstract); định dạng ngày tháng không hoàn chỉnh. |

### Cách xác minh

Chạy lệnh Python trực tiếp từ thư mục gốc dự án để kích hoạt quá trình thu thập dữ liệu:
```bash
python -c "from core.config import load_settings; from ingestion.crossref import fetch_source_records; fetch_source_records(load_settings())"
```

- **Kết quả mong đợi:** Kết nối API thành công, tải và parse chuẩn xác 24 bản ghi học thuật, ghi thành công hai file JSON vào `data/raw/`, và nạp ngược lại dữ liệu so khớp thành công mà không gặp bất kỳ lỗi định dạng nào.
- **Kết quả thực tế:**
  ```text
  Loading settings...
  Fetching source records from Crossref API...
  Fetched 24 parsed records.
  Raw API response exists: True (size: 245261 bytes)
  Raw records JSON exists: True (size: 59176 bytes)
  First record sample:
    paper_id: 10-47576-2949-1894-2026-7-7-023
    title: Снижение рисков применения LLM (Large Language Model) в сфере экономической безопасности...
    published: 2026-06-15
    updated: 2026-06-17
  Testing load_raw_records...
  Loaded 24 records from disk.
  Success! Loaded record matches fetched record.
  ```
- **Artifact/log:** Xem file [crossref_response.json](data/raw/crossref_response.json) và [crossref_records.json](data/raw/crossref_records.json).

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Lựa chọn phương pháp lưu trữ dữ liệu thô khi hoàn tất quá trình Ingestion.
- **Các phương án đã cân nhắc:**
  1. *Phương án A*: Chỉ parse trực tiếp và lưu một file bản ghi phẳng đã lọc `crossref_records.json` để tiết kiệm dung lượng lưu trữ của ổ đĩa.
  2. *Phương án B*: Lưu trữ song song cả API response nguyên bản từ máy chủ (`crossref_response.json`) và danh sách bản ghi đã parse (`crossref_records.json`).
- **Phương án đã chọn:** Phương án B.
- **Lý do:** Đây là quyết định cốt lõi giúp đảm bảo tính **Data Lineage** (truy vết dòng chảy dữ liệu) và khả năng tái lập (**Reproducibility**). File response nguyên bản đóng vai trò là "chứng cứ gốc" giúp ích cho việc sửa đổi logic phân tích (parsing rules) hoặc gỡ lỗi trong tương lai mà không cần phải thực hiện lại cuộc gọi mạng lên hệ thống Crossref (giảm phụ thuộc vào tài nguyên mạng và tránh nguy cơ bị khóa IP do rate limit). File records đã parse đóng vai trò là hợp đồng dữ liệu phẳng giúp TV3 dễ dàng thao tác trực tiếp.
- **Bằng chứng quyết định phù hợp:** Cả hai file đã được tạo ra thành công trên đĩa với kích thước cân bằng và được kiểm tra tính khớp nối trong kiểm thử.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:**
  ```text
  Traceback (most recent call last):
    File "verify_ingestion.py", line 48, in <module>
      main()
    File "verify_ingestion.py", line 29, in main
      print(f"  title: {sample.title}")
    File "...\encodings\cp1252.py", line 19, in encode
      return codecs.charmap_encode(input,self.errors,encoding_table)[0]
  UnicodeEncodeError: 'charmap' codec can't encode characters in position 9-16: character maps to <undefined>
  ```
- **Lệnh hoặc bước tái hiện:** Chạy file script xác minh thu thập dữ liệu bằng công cụ `uv run python` trên môi trường terminal Windows PowerShell mặc định.
- **Nguyên nhân gốc:** Hệ thống Crossref trả về một số bài báo nghiên cứu bằng tiếng Nga (chứa ký tự Cyrillic). Do PowerShell trên hệ điều hành Windows mặc định sử dụng bảng mã hóa luồng ra `cp1252` (không hỗ trợ các ký tự Unicode phi ASCII), hàm `print()` của Python cố gắng đẩy chuỗi này ra console dẫn đến lỗi UnicodeEncodeError.
- **Cách xử lý:** Bổ sung cấu hình `sys.stdout.reconfigure(encoding='utf-8')` ở phần đầu của các file thực thi chạy terminal trên Windows để ép kiểu xuất dữ liệu sử dụng bảng mã UTF-8.
- **Cách xác minh sau khi sửa:** Chạy lại lệnh trên terminal, màn hình in ra tiêu đề tiếng Nga hoàn toàn bình thường mà không bị crash.
- **Điều học được:** Khi xây dựng pipeline thu thập dữ liệu đa ngôn ngữ quốc tế, không nên giả định console của hệ điều hành đích luôn hỗ trợ UTF-8. Cần cấu hình tường minh encoding cho luồng xuất chuẩn `sys.stdout` trong môi trường kiểm thử.

## 7. Hiểu biết về luồng end-to-end

1. **Dữ liệu đi từ Crossref đến vector index như thế nào?**
   - **Ingestion**: `crossref.py` gọi API Crossref lấy metadata học thuật thô lưu vào `crossref_response.json` và parse thành `crossref_records.json`.
   - **Cleaning**: `cleaning.py` đọc các bản ghi thô này, lọc bỏ các bản ghi lỗi, chuẩn hóa văn bản, ghép các trường lại thành cột `text_for_embedding`, tính số ngày xuất bản `age_days` và ghi vào `data/clean/papers_clean.csv` / `.json`.
   - **Indexing**: `index.py` đọc dữ liệu sạch, dùng mô hình `MiniLM` để tạo vector embeddings cho cột `text_for_embedding`, sau đó lưu cả vector và metadata của tài liệu vào cơ sở dữ liệu vector ChromaDB và xuất file manifest JSON.

2. **Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?**
   - Bộ kiểm thử (evaluation set) chứa các mẫu câu hỏi học thuật có sẵn câu trả lời chuẩn (`ground_truth`) và danh sách các ID của tài liệu gốc chứa câu trả lời (`ground_truth_doc_ids`).
   - Khi chạy RAG Agent, Agent sẽ tìm kiếm thông tin liên quan trong ChromaDB dựa trên câu hỏi. Hệ thống so sánh xem các tài liệu mà Agent tìm được có nằm trong `ground_truth_doc_ids` hay không để tính điểm `retrieval_hit_rate` (chất lượng tìm kiếm). Đồng thời, câu trả lời do Agent sinh ra sẽ được so khớp với `ground_truth` thông qua một mô hình giám định LLM (Judge Evaluator) để chấm điểm đúng/sai và mức độ chuẩn xác (Token F1 / Judge Score).

3. **Quality checks khác freshness monitoring ở điểm nào trong bài lab?**
   - **Quality checks**: Đánh giá tính toàn vẹn và chất lượng tĩnh của dữ liệu (như kiểm tra tổng số dòng, đảm bảo khóa chính `paper_id` không rỗng và duy nhất, các trường tiêu đề không rỗng, độ dài tóm tắt tối thiểu, dữ liệu không bị trùng lặp).
   - **Freshness monitoring**: Đo lường tính cập nhật của dữ liệu theo thời gian (như tính ngày xuất bản gần nhất/xa nhất, đếm số lượng tài liệu đã quá hạn cũ - stale rows dựa trên số ngày `age_days` so với ngưỡng quy định).

4. **Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?**
   - Để đảm bảo tính nhất quán khoa học khi so sánh (A/B testing trên cùng một hệ quy chiếu). Nếu dùng các bộ câu hỏi khác nhau cho các trạng thái dữ liệu khác nhau, sự biến động của metrics hiệu năng của Agent có thể bị nhiễu do độ khó của câu hỏi chứ không phản ánh chính xác chất lượng của nguồn dữ liệu đầu vào.

5. **Repair được xem là thành công dựa trên artifact và metric nào?**
   - **Về dữ liệu (Data level)**: File dữ liệu sau khi được khôi phục phải vượt qua bài kiểm tra chất lượng (Quality check báo Passed) và các chỉ số thống kê (như số dòng) trở lại bình thường.
   - **Về mô hình (Model level)**: Các chỉ số đo đạc trên cùng bộ test set (`retrieval_hit_rate`, `mean_token_f1`, và `judge_accuracy`) của hệ thống Repaired RAG phải tăng mạnh so với khi hệ thống bị lỗi (Corrupted RAG) và tiệm cận trở lại với mức Baseline ban đầu.

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal          | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| ---------------------- | -------: | --------: | -------: | ------------------------- |
| `retrieval_hit_rate` |      [1.0] |       [0.0] |      [1.0] | Baseline thu được 100% tài liệu liên quan. Khi bị lỗi, không truy xuất được gì. Sau khi sửa đổi từ dữ liệu thô của TV2, chỉ số phục hồi hoàn toàn. |
| `mean_token_f1`      |      [0.6] |       [0.1] |      [0.6] | Độ tương đồng token giảm sâu khi dữ liệu bị lỗi và được khôi phục trở lại sau repair. |
| `judge_accuracy`     |      [1.0] |       [0.0] |      [1.0] | Độ chính xác của câu trả lời do LLM giám định đạt điểm tối đa ở trạng thái sạch và phục hồi hoàn toàn sau sửa đổi. |
| `mean_judge_score`   |      [5.0] |       [1.0] |      [5.0] | Điểm số trung bình phục hồi từ 1.0 (khi lỗi) về mức tối đa 5.0. |
| Quality checks         |   [Passed] |    [Failed] |  [Passed] | Dữ liệu baseline và repaired vượt qua kiểm tra chất lượng, dữ liệu lỗi bị phát hiện thất bại. |
| Freshness status       |    [Fresh] |    [Stale] |   [Fresh] | Dữ liệu hỏng bị đổi ngày về quá khứ nên bị đánh dấu Stale, sau repair ngày tháng được khôi phục về trạng thái Fresh. |

*Lưu ý: Các chỉ số metrics trên được ghi nhận từ chạy pipeline tích hợp của nhóm.*

### Kết luận từ số liệu

1. **Chuỗi sự cố**: [Dữ liệu bị sửa đổi ngày xuất bản về quá khứ và nhân bản trùng lặp] $\rightarrow$ [Quality checks báo lỗi trùng lặp và Freshness status chuyển sang Stale] $\rightarrow$ [LLM Agent bị nhiễu thông tin dẫn đến điểm judge_accuracy giảm mạnh về 0].
2. **Chuỗi phục hồi**: [Phục hồi dữ liệu từ nguồn thô gốc đáng tin cậy của TV2] $\rightarrow$ [Kiểm tra Quality checks và Freshness status khôi phục trạng thái Passed và Fresh] $\rightarrow$ [Các chỉ số đánh giá Agent metric phục hồi hoàn toàn về mức Baseline ban đầu].

- **Corruption nào ảnh hưởng rõ nhất và vì sao?**
  - Sự cố làm rỗng tóm tắt (abstract) và làm nhiễu tiêu đề ảnh hưởng nặng nhất. Lý do là vì embedding index phụ thuộc trực tiếp vào ngữ nghĩa của cột `text_for_embedding` (được sinh từ title và summary). Khi các thông tin này bị xóa hoặc làm nhiễu, khoảng cách cosine giữa câu hỏi và vector tài liệu tăng cao khiến retriever hoàn toàn thất bại trong việc truy xuất tài liệu đúng, kéo theo toàn bộ các chỉ số của RAG sụp đổ.

- **Kết quả nào khác với kỳ vọng ban đầu?**
  - Ban đầu tôi nghĩ LLM có khả năng suy luận tốt nên kể cả khi tiêu đề bị nhiễu nhẹ vẫn có thể đoán được ngữ cảnh. Tuy nhiên, thực tế kiểm thử cho thấy khi retriever không tìm đúng tài liệu (retrieval_hit = 0) do vector embedding bị lệch quá xa, LLM hoàn toàn không có dữ liệu để suy luận và bắt buộc phải trả lời sai. Điều này chứng minh sự phụ phục cực kỳ lớn của RAG vào chất lượng dữ liệu đầu vào.

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. **Về data pipeline**: Một data pipeline hoạt động tốt không chỉ là code chạy không lỗi mà phải đảm bảo bảo toàn dữ liệu (**Data Lineage**). Việc lưu trữ tài nguyên thô (raw artifacts) là bắt buộc để hệ thống có khả năng tự phục hồi (self-healing) khi xảy ra sự cố dữ liệu ở các pha sau.
2. **Về data quality/observability**: Cần có các bài test chất lượng tĩnh (Quality Checks) và giám sát động (Freshness Monitoring) để chủ động phát hiện sự cố dữ liệu trước khi người dùng cuối nhận được câu trả lời sai từ AI Agent.
3. **Về ảnh hưởng của data đến RAG agent**: Chất lượng của RAG Agent chịu ảnh hưởng mang tính quyết định từ chất lượng dữ liệu. "Garbage in, garbage out" - nếu dữ liệu đầu vào bị lỗi hoặc cũ, dù mô hình LLM có thông minh đến đâu cũng không thể sinh ra câu trả lời chính xác.

### Nếu có thêm thời gian
Tôi muốn xây dựng thêm một phân hệ tự động kiểm tra định kỳ (Cron scheduler) để tự động gọi API Crossref cập nhật dữ liệu mới hàng ngày, và tích hợp sâu hơn cơ chế kiểm định dữ liệu thô ngay khi tải về (Schema Validation khi Ingestion) để phát hiện sớm các bài báo bị thiếu trường dữ liệu quan trọng ngay tại cửa ngõ đầu tiên của pipeline thay vì đợi đến bước Cleaning hay Observability mới phát hiện.

## 10. Cam kết của thành viên

Đánh dấu sau khi tự kiểm tra:

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Nhữ Văn Hùng
**Ngày xác nhận:** 2026-08-06
