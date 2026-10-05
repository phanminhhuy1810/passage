# Học từ sản phẩm đã chạy được

Passage đã có demo và các báo cáo đánh giá. Tài liệu này hướng dẫn đọc, chạy lại và kiểm chứng từng phần của hệ thống, bắt đầu từ một câu hỏi và kết quả tìm kiếm.

Mỗi buổi có **một đầu ra quan sát được**: một phép tính tay, một lần chạy có ghi nhận hoặc một đoạn phân tích lỗi. Hoàn thành từng bước nhỏ trước khi chuyển sang phần tiếp theo.

## Bước 1 — Đi từ câu hỏi tới thứ hạng

Mở demo, dùng cùng một câu hỏi với ba phương pháp. Đọc một đoạn trả về và nói bằng lời của mình vì sao nó liên quan hoặc không liên quan. Sau đó mở lại `lessons/01_overlap.py`.

**Đầu ra:** hai câu hỏi đã thử, kết quả đứng đầu của overlap và một trường hợp điểm trùng nhau nhưng ý nghĩa khác nhau. Ghi được đầu vào, đầu ra và cách xử lý khi hòa điểm.

**Tài liệu:** [buổi 1](BUOI-01.md); [Stanford SLP, chương Information Retrieval](https://web.stanford.edu/~jurafsky/slp3/11.pdf), đọc phần mở đầu về tìm kiếm thông tin.

## Bước 2 — Từ đếm chữ tới vector TF-IDF

Chạy `lessons/02_idf.py`, tự đếm số đoạn có chứa mỗi token. Phân biệt “token xuất hiện bao nhiêu lần trong một đoạn” với “token có mặt trong bao nhiêu đoạn”. Sau đó xem `Retriever.vectorize` trong `retrieval.py`: trọng số, độ dài vector, rồi tích vô hướng.

**Đầu ra:** tính tay IDF của hai token trong ví dụ ba câu và cosine của hai vector nhỏ. Đối chiếu với kết quả Python, giải thích được một sai lệch nếu có.

**Tài liệu:** [buổi 2](BUOI-02.md); [scikit-learn: TF-IDF term weighting](https://scikit-learn.org/stable/modules/feature_extraction.html#tfidf-term-weighting). Chưa cần thay code bằng thư viện khi chưa hiểu công thức.

## Bước 3 — Hiểu mô hình E5 đang được dùng thế nào

Theo luồng trong `semantic.py`: thêm `query: ` hoặc `passage: ` → tokenizer → mô hình → vector chuẩn hóa → điểm cosine. Phân biệt **dùng mô hình đã học trước để suy luận** với **huấn luyện hoặc fine-tune mô hình**. Dự án hiện làm việc thứ nhất.

**Đầu ra:** vẽ được luồng một câu hỏi tới vector, giải thích vì sao vector đoạn được lưu lại, và chỉ ra giới hạn 512 token có thể làm mất phần nào của đoạn dài. Thử hai cách diễn đạt cùng ý và ghi kết quả, kể cả khi E5 không tốt hơn.

**Tài liệu:** [model card E5 Small](https://huggingface.co/intfloat/multilingual-e5-small), đọc Usage và các ghi chú về prefix/length; [Sentence Transformers: Semantic Search](https://www.sbert.net/examples/sentence_transformer/applications/semantic-search/README.html), xem asymmetric search.

## Bước 4 — Tự chạy lại đánh giá trên dev

Chạy `.venv/bin/python evaluate.py --split dev`. Đọc báo cáo, chọn ba câu hỏi: đoạn nguồn đứng thứ nhất, đứng thứ hai và không có trong top 5. Tự tính Hit@1, Hit@5 và MRR@5 của nhóm ba câu ấy.

**Đầu ra:** một bảng tính tay ba dòng khớp với cách tính trong `evaluate.py`; ghi rõ 843 câu dev và kho 240 đoạn là hai số khác nhau. Ghi môi trường và lệnh đã dùng. Không cần chạy lại test để học công thức.

**Tài liệu:** `evaluate.py`, [README - dataset and results](../README.md#dataset-and-results), [XQuAD gốc](https://github.com/google-deepmind/xquad).

## Bước 5 — Phân tích năm lỗi cụ thể

Chọn năm câu từ **dev** mà ít nhất một phương pháp xếp sai. Với mỗi câu, đọc đoạn nguồn và đoạn bị xếp trên nó. Ghi điều quan sát được trước, rồi mới viết giả thuyết.

**Đầu ra cho mỗi lỗi:** câu hỏi/ID; thứ hạng theo ba cách; chi tiết đúng nằm ở đâu; dấu hiệu khiến phương pháp có thể nhầm; một phép thử nhỏ giúp kiểm tra giả thuyết. Một nhận xét như “đoạn cùng chủ đề nhưng sai năm” cụ thể hơn “AI chưa hiểu ngữ nghĩa”.

Không kết luận nguyên nhân chỉ dựa vào điểm số. Nếu không đủ bằng chứng, ghi “giả thuyết chưa kiểm chứng”.

## Bước 6 — Làm một thay đổi có lý do và kể lại được

Sau khi hiểu các bước trước, chọn **một** thử nghiệm: ví dụ cách xử lý token hoặc cách kết hợp hai thứ hạng. Trước khi sửa, viết kỳ vọng và cách kiểm tra trên dev. Giữ lại bản gốc để so sánh cùng điều kiện.

**Đầu ra:** một thay đổi nhỏ do bạn review và giải thích được, một bảng trước/sau, kết luận kể cả khi không cải thiện, cùng ghi chép AI đã hỗ trợ phần nào. Vì test của bản hiện tại đã được dùng cho báo cáo cuối, không dùng nó để lựa chọn thay đổi rồi gọi kết quả mới là đánh giá độc lập.

Cuối cùng, trình bày dự án trong khoảng hai phút: bài toán → dữ liệu → ba cách làm → một kết quả → một lỗi → phần bạn đóng góp và điều muốn nghiên cứu tiếp.

## Tiếng Anh: năm thuật ngữ mỗi buổi

Ghi đúng **năm thuật ngữ** gặp trong tài liệu, kèm một câu tự viết bằng tiếng Anh và ý nghĩa bằng tiếng Việt. Với buổi đầu có thể chọn: `query`, `passage`, `retrieval`, `ranking`, `relevance`. Buổi sau thay bằng từ mới thật sự đã gặp.

Mục tiêu là đọc hiểu một đoạn và dùng lại từ trong bối cảnh dự án. Tra từ trong ngữ cảnh, rồi diễn đạt lại một ý bằng lời của mình.

## Ghi nhận để cập nhật CV

Mỗi lần hoàn thành, thêm một mục ngắn vào [CONTRIBUTIONS.md](CONTRIBUTIONS.md): ngày; việc tự đọc/chạy/sửa; kết quả quan sát; hỗ trợ từ AI; điều chưa hiểu. Những ghi nhận này giúp mô tả đóng góp chính xác và cụ thể hơn qua từng lần cập nhật CV.
