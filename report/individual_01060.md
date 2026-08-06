# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Họ và tên       | Phạm Tuấn Anh             |
| MSSV               | 01060                     |
| Khóa/Lớp         | K4              |
| Tên nhóm         | HHHQDA     |
| Vai trò chính    | Data Observability, Corruption Simulation & Reporting Owner (TV6)                 |
| Repository         | https://github.com/NguyenVanHung1707/K4-Day10-E402-HHHQDA |
| Ngày hoàn thành | 2026-08-06               |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao  | Trạng thái                                 |
| ------------------ | --------------------- | ---------------- | ----------------- | -------------------------------------------- |
| Data Quality & Freshness Checks      | `src/observability/quality.py` (hàm `run_data_quality_checks`, `build_freshness_report`)           | `clean_df`, `corrupted_df`, `repaired_df`          | Báo cáo `quality.json`, `freshness.json` | Hoàn thành |
| Corruption Simulation      | `src/ingestion/corruption.py` (hàm `corrupt_clean_dataframe`)           | `clean_df`          | `corrupted_df`, `corruption_log.json` | Hoàn thành |
| Markdown Reporting      | `src/observability/reporting.py` (hàm `generate_phase1_report`, `generate_corruption_report`)           | Các file json chứa metrics, quality, freshness          | `phase1_report.md`, `corruption_report.md` | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động                         | Thành viên/module được hỗ trợ | Kết quả                    |
| ------------------------------------ | ------------------------------------ | ---------------------------- |
| Hỗ trợ sinh file dữ liệu lỗi sớm | TV4 (Re-indexing) | Giúp TV4 có file `papers_clean_corrupted.csv` để làm VectorDB không bị tắc nghẽn. |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao       | Cách xác minh         |
| --------------------------- | ----------------------------- | ------------------------- | ----------------------- |
| Xây dựng hệ thống Data Observability | `data/quality/*` | Các file `.json` chứa số liệu pass/fail và freshness. | Kiểm tra nội dung file sinh ra. |
| Giả lập lỗi dữ liệu (Data Corruption) | `data/clean/papers_clean_corrupted.csv`, `data/results/corruption_log.json` | File dữ liệu bị hỏng có chủ đích và log ghi nhận lỗi. | Load pandas kiểm tra số lượng và chất lượng. |
| Tự động hóa Báo cáo So sánh | `data/reports/corruption_report.md` | Báo cáo Markdown hiển thị bảng so sánh 3 trạng thái. | Đọc file `.md` được sinh ra tự động. |

Nêu một output cụ thể mà phần việc của bạn tạo ra hoặc giúp xác minh:

Tôi trực tiếp sinh ra file `data/reports/corruption_report.md`. Đây là báo cáo so sánh trực quan về các chỉ số Data Quality (do tôi tính toán) và Agent Metrics (do TV5 cung cấp) giữa 3 giai đoạn: Baseline, Corrupted và Repaired. Nhờ báo cáo này, cả nhóm có thể thấy rõ tác động của việc mất dữ liệu và sửa chữa dữ liệu lên hiệu suất của RAG Agent.

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Trong một pipeline dữ liệu, làm sao để biết dữ liệu hiện tại có đạt chất lượng không? Và khi dữ liệu bị hỏng (corruption), điều đó ảnh hưởng thực tế ra sao đến kết quả trả lời của LLM (RAG)? Vai trò của tôi là tạo ra công cụ để "đo lường" sự hỏng hóc đó và "giả lập" các lỗi thực tế để kiểm chứng sức mạnh của quy trình sửa lỗi.

### Cách triển khai

- **Data Quality:** Dùng `pandas` để tính toán tỷ lệ null, số dòng, độ dài chuỗi, sau đó so sánh với các Rule tĩnh.
- **Corruption:** Dùng `numpy.random` để lấy ngẫu nhiên các dòng và chèn nhiễu, làm rỗng giá trị, làm cũ ngày xuất bản (lùi về quá khứ 3 năm) để mô phỏng thực tế.
- **Reporting:** Kết hợp f-string của Python để render trực tiếp dữ liệu dạng JSON dict thành định dạng bảng Markdown trực quan.

### Input, output và contract

| Thành phần                   | Mô tả                                     |
| ------------------------------ | ------------------------------------------- |
| Input                          | Dữ liệu đã làm sạch `papers_clean.csv`           |
| Output                         | `papers_clean_corrupted.csv` và các file báo cáo JSON, MD |
| Module phụ thuộc             | `core.config` (để lấy đường dẫn)                    |
| Module sử dụng output        | `retrieval.index` (TV4 dùng file lỗi của tôi), `evaluation` (TV5)                    |
| Điều kiện lỗi cần xử lý | Xử lý Unicode Encode khi in log trên Windows (đã fix).                   |

### Cách xác minh

```bash
python script/run_tv6.py
```

- **Kết quả mong đợi:** File CSV lỗi và JSON log được tạo ra. Quality checks in ra Fail thay vì Pass.
- **Kết quả thực tế:** Hệ thống cảnh báo chính xác (chỉ Pass 2/5 checks, phát hiện 2 dòng stale). Báo cáo so sánh được tự động render.
- **Artifact/log:** `data/reports/corruption_report.md`

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Render báo cáo Markdown.
- **Các phương án đã cân nhắc:** Dùng template engine (Jinja2) hoặc dùng f-string của Python.
- **Phương án đã chọn:** Dùng f-string cơ bản.
- **Lý do:** Giảm độ phức tạp và phụ thuộc thư viện ngoài, do cấu trúc báo cáo không quá phức tạp, dùng f-string kết hợp vòng lặp `for` để render bảng là đủ nhanh và hiệu quả.
- **Bằng chứng quyết định phù hợp:** File `corruption_report.md` sinh ra có format cực kỳ chuẩn xác và đẹp mắt.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** `UnicodeEncodeError: 'charmap' codec can't encode character '\u1eaf' in position 1...`
- **Lệnh hoặc bước tái hiện:** Chạy lệnh `python script/run_tv6.py` trên Terminal của Windows.
- **Nguyên nhân gốc:** Windows terminal (cp1252) không hỗ trợ render một số ký tự tiếng Việt có dấu trong hàm `print()`.
- **Cách xử lý:** Đổi các chuỗi `print` sang tiếng Việt không dấu.
- **Cách xác minh sau khi sửa:** Chạy lại script không còn bị lỗi crash.
- **Điều học được:** Khi viết các script command line chạy trên nhiều hệ điều hành, nên hạn chế in ra console các ký tự non-ASCII nếu không thiết lập sẵn encoding UTF-8 cho môi trường.

## 7. Hiểu biết về luồng end-to-end

1. **Dữ liệu đi từ Crossref đến vector index như thế nào?**
   Dữ liệu raw (JSON) được tải từ API Crossref -> Chuyển thành DataFrame, làm sạch (loại bỏ null, join mảng) và lưu ra `papers_clean.csv` -> Chuyển nội dung thành Vector (Embedding) rồi đẩy vào ChromaDB.
2. **Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?**
   Các file Test Set chứa sẵn câu hỏi và ID tài liệu chuẩn (ground truth). Khi RAG Agent trả lời, ta so sánh ID tài liệu Agent tìm được với ground-truth ID để tính Hit Rate, và dùng LLM chấm điểm câu trả lời so với ground-truth answer để lấy Accuracy.
3. **Quality checks khác freshness monitoring ở điểm nào trong bài lab?**
   Quality checks kiểm tra tính đúng đắn của schema (null, độ dài, trùng lặp). Freshness monitoring kiểm tra ý nghĩa thời gian của dữ liệu (dữ liệu có bị "cũ" hay không) so với ngưỡng ngày cấu hình.
4. **Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?**
   Để đảm bảo tính công bằng (A/B Testing). Cùng 1 tập câu hỏi, nếu dữ liệu nền tảng bị hỏng thì điểm tụt, dữ liệu được sửa thì điểm lên -> Chứng minh được Data Quality có ảnh hưởng trực tiếp đến kết quả của Agent.
5. **Repair được xem là thành công dựa trên artifact và metric nào?**
   Dựa vào `repaired_quality.json` (phải Pass 5/5) và file metrics `repaired_metrics.json` (các chỉ số F1, Accuracy phải phục hồi tiệm cận lại mức Baseline).

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal          | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| ---------------------- | -------: | --------: | -------: | ------------------------- |
| `retrieval_hit_rate` |      0.9 |       0.4 |      0.92 | RAG gặp khó khăn lớn khi tìm kiếm do title bị cắt, nội dung summary bị nhiễu. Việc sửa lỗi giúp phục hồi khả năng tìm kiếm. |
| `mean_token_f1`      |      0.842 |       0.325 |      0.821 | Tụt dốc thê thảm do dữ liệu nhiễu khiến LLM không tạo ra được câu trả lời sát với Ground Truth. Sau khi sửa, phục hồi gần như hoàn toàn. |
| `judge_accuracy`     |      0.9 |       0.3 |      0.9 | Độ chính xác của câu trả lời bị hủy diệt khi bị thiếu hụt dữ liệu (do xóa 10% bản ghi). Đã phục hồi 100% nhờ repair. |
| `mean_judge_score`   |      4.5 |       2.1 |      4.4 | Mức độ hài lòng chung giảm. |
| Quality checks         |      5/5 |       2/5 |      5/5 | Observability đã làm tốt việc cảnh báo kịp thời. |
| Freshness status       |      0 Stale |       2 Stale |      0 Stale | Giả lập lỗi đổi ngày làm dữ liệu cũ đi, và hệ thống đã bắt được thành công. |

### Kết luận từ số liệu

1. **[Data corruption (Xóa dữ liệu, làm rỗng summary)]** → **[Quality checks bị fail]** → **[Agent metric (Accuracy, Hit rate) giảm mạnh]**.
2. **[Repair action (Gọi LLM trích xuất lại từ RAW)]** → **[Quality checks Pass trở lại]** → **[Agent metric phục hồi 99%]**.

**Corruption nào ảnh hưởng rõ nhất và vì sao?**
Việc xóa ngẫu nhiên các dòng và làm rỗng cột `summary`. Vì RAG Agent phụ thuộc 100% vào ngữ cảnh được nạp vào, nếu bản ghi biến mất hoặc không còn nội dung hữu ích, Agent sẽ rơi vào tình trạng "mù thông tin" dẫn tới trả lời sai (hallucination).

**Kết quả nào khác với kỳ vọng ban đầu?**
Hit Rate của Repaired (0.92) thậm chí còn cao hơn Baseline (0.9). Giả thuyết là việc TV3 Repair dữ liệu bằng LLM đã vô tình tóm tắt lại thông tin một cách "chuẩn SEO" và sạch sẽ hơn dữ liệu gốc, giúp VectorDB dễ matching hơn.

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. Tầm quan trọng tuyệt đối của Data Quality. Garbage In = Garbage Out. Dữ liệu móng hỏng thì Agent AI xây bên trên cũng sụp đổ.
2. Việc giám sát (Observability) phải được tự động hóa. Khi dữ liệu lớn lên, không thể kiểm tra bằng mắt mà phải viết rule tự động quét và cảnh báo.
3. RAG Agent cực kỳ nhạy cảm với dữ liệu nhiễu (noise) và dữ liệu bị cũ (stale).

### Nếu có thêm thời gian

Tôi sẽ viết thêm hệ thống Alerting. Ví dụ: Nếu `run_data_quality_checks` trả về Fail, hệ thống sẽ tự động bắn tin nhắn cảnh báo qua Slack hoặc Telegram cho Team Data Engineer ngay lập tức thay vì chỉ lưu file JSON.

## 10. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Phạm Tuấn Anh
**Ngày xác nhận:** 2026-08-06
