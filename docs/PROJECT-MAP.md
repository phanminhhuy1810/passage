# Passage làm gì?

**Bạn gõ một câu hỏi tiếng Việt. Chương trình tìm và xếp hạng các đoạn văn có khả năng chứa thông tin liên quan, rồi cho bạn so sánh ba cách tìm.**

Ví dụ: nhập “Norman là ai?”. Đầu ra là những đoạn có sẵn trong kho dữ liệu, kèm thứ hạng, tiêu đề và điểm tương đồng. Chương trình không tự viết câu trả lời và không tra cứu Internet khi bạn tìm kiếm.

## Sản phẩm có ba phần nối với nhau

1. **Công cụ tìm kiếm:** cùng một câu hỏi được đưa vào overlap, TF-IDF và mô hình E5 để nhận ba danh sách kết quả.
2. **Giao diện demo:** nhập câu hỏi, mở các đoạn kết quả và quan sát khác biệt giữa các phương pháp.
3. **Thực nghiệm:** dùng những câu hỏi đã có đoạn nguồn được gán nhãn để đo phương pháp nào thường xếp đúng đoạn lên cao hơn.

Vì vậy, dự án có bài toán rõ, phương pháp đối chiếu, dữ liệu có nguồn, cách kiểm tra kết quả và giới hạn cần trình bày.

## Một câu hỏi đi qua những đâu?

```text
Câu hỏi bạn nhập
      │
      ▼
Giao diện hoặc search.py
      │
      ▼
engine.py chọn phương pháp
      ├── retrieval.py → đếm token / vector TF-IDF
      └── semantic.py  → vector do E5 tạo ra
      │
      ▼
Chấm điểm từng đoạn → sắp xếp → lấy các đoạn đứng đầu
      │
      ▼
Hiển thị đoạn gốc và điểm của phương pháp đó
```

Trước khi tìm kiếm, `dataset.py` đã chuẩn bị kho **240 đoạn**. Nhánh E5 còn tạo sẵn vector của từng đoạn; mỗi lần tìm chỉ cần biến câu hỏi mới thành vector rồi so sánh với kho vector ấy.

## Ba cách tìm khác nhau ở đâu?

| Cách | Ý tưởng dễ hình dung | Giới hạn dễ thấy |
|---|---|---|
| Overlap | Đếm có bao nhiêu token khác nhau xuất hiện ở cả câu hỏi lẫn đoạn văn. | Trùng chữ chưa chắc cùng ý; nhiều kết quả có thể hòa điểm. |
| TF-IDF + cosine | Token hiếm có trọng số cao hơn; xem hai vector có cùng hướng hay không. | Không có chữ chung thì khó nối được hai cách diễn đạt. |
| E5 | Mô hình đã học trước biến văn bản thành vector để đo độ gần nhau. | Cùng chủ đề chưa chắc đúng chi tiết; vẫn có thể xếp sai. |

Điểm `0.8` của E5 không có nghĩa là “80% chắc đúng”. Điểm của các phương pháp cũng không cùng thang đo để so trực tiếp. Cần so **thứ hạng và kết quả đánh giá**.

## Tại sao có 843 câu dev và 347 câu test?

Trong XQuAD, mỗi câu hỏi đã đi cùng một đoạn chứa câu trả lời. Ta tận dụng liên kết đó để hỏi: “Chương trình có tìm lại đúng đoạn nguồn không?”.

- **Dev:** 843 câu để xem lỗi và phát triển phương pháp.
- **Test:** 347 câu dành cho lượt đánh giá sau khi cố định phương pháp.
- **Kho tìm kiếm:** cả hai lượt đều tìm trong cùng 240 đoạn.

Các câu hỏi thuộc cùng một đoạn được giữ chung một nhóm khi chia. Đó là lý do tỉ lệ câu hỏi không chính xác 70/30 dù nhóm đoạn được chia theo tỉ lệ ấy. Sau khi đã xem kết quả test, những thay đổi tiếp theo cần được gọi đúng là phát triển sau test; không thể dùng lại nó như một bài kiểm tra chưa từng thấy.

## Phần nào cần bạn thật sự hiểu?

**Ưu tiên phần lõi:** đầu vào/đầu ra; token; đếm từ; IDF; chuẩn hóa vector; cosine; embedding; thứ hạng; Hit@k và MRR. Bạn nên lần theo một ví dụ nhỏ từ đầu tới cuối, giải thích được vì sao một kết quả đứng trên kết quả khác, và sửa được một thay đổi nhỏ có chủ đích.

**Đọc sau khi cần:** mã mở cổng web, gửi JSON, CSS, đường dẫn cache và trình mở ứng dụng. Các phần này giúp sản phẩm dùng được, nhưng học chúng cùng lúc với mọi khái niệm NLP sẽ gây quá tải.

Không cần thuộc từng dòng. Tuy vậy, chỉ nhớ định nghĩa cũng chưa đủ để nhận mình đã làm chủ dự án: bạn cần chạy lại, kiểm tra đầu ra, đọc lỗi và diễn giải một lựa chọn trong code.

## Mở file theo thứ tự này

| Thứ tự | File | Cần hiểu được |
|---|---|---|
| 1 | `lessons/01_overlap.py` | Chuỗi → tập token → điểm → thứ hạng. |
| 2 | `lessons/02_idf.py` | Vì sao token hiếm được cho trọng số cao hơn. |
| 3 | `retrieval.py` | Cách biểu diễn vector thưa và tính cosine. |
| 4 | `search.py`, `engine.py` | Đưa câu hỏi vào đúng phương pháp, lấy top-k. |
| 5 | `semantic.py` | Mô hình có sẵn biến văn bản thành vector như thế nào trong chương trình; prefix, chuẩn hóa, cache và giới hạn độ dài. |
| 6 | `dataset.py`, `evaluate.py` | Nhãn đúng đến từ đâu, chia tập ra sao, điểm đánh giá được tính như thế nào. |

Bạn có thể xem demo trước khi học hết sáu bước. Lộ trình có đầu ra nhỏ để tự kiểm tra nằm trong [HOC-TIEP.md](HOC-TIEP.md).

## Liên quan gì đến hồ sơ AIoT Lab?

Repo cung cấp một sản phẩm NLP có thể mở và kiểm chứng. Bảng điểm cho thấy nền tảng học thuật; những lần bạn tự chạy, giải thích lỗi và thực hiện thay đổi có lý do sẽ bổ sung bằng chứng về khả năng học và làm dự án.

Định hướng phù hợp để ghi lúc này là **khám phá NLP và information retrieval**, đặc biệt là so sánh phương pháp từ khóa với mô hình embedding. Chưa cần tự gắn nhãn chuyên gia NLP hoặc chốt nghề nghiệp. Phần đóng góp thực tế và phần được AI hỗ trợ được ghi trong [CONTRIBUTIONS.md](CONTRIBUTIONS.md).
