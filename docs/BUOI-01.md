# Buổi 1: từ chuỗi chữ đến điểm tìm kiếm

Mục tiêu hôm nay: chạy được một ví dụ nhỏ và hiểu chính xác cách tính điểm. Không cần học toàn bộ NLP hoặc đọc hết code dự án.

## Đọc 5–10 phút

[Jurafsky & Martin, Speech and Language Processing, chương 11](https://web.stanford.edu/~jurafsky/slp3/11.pdf#page=3), bản 19/8/2026. Mở trang 3, mục 11.1. Chỉ đọc hai đoạn định nghĩa đầu, dừng trước hình 11.1. Chưa cần phần vector, TF-IDF, BM25 hoặc dense retrieval.

- **Query:** câu người dùng gõ để tìm thông tin.
- **Document:** đơn vị văn bản được tìm; trong dự án này là một đoạn văn.

Đầu vào là câu tìm kiếm và một kho đoạn văn. Đầu ra là các đoạn được xếp hạng, không phải câu trả lời do chatbot viết.

## Cách chấm điểm đầu tiên

Tạm tách chuỗi theo khoảng trắng và bỏ chữ trùng lặp. Gọi tập mảnh chữ của câu tìm là Q, của một đoạn văn là D:

**score = |Q ∩ D|**

Đếm số phần tử của giao hai tập hợp. `set(...)` tạo tập hợp; `&` lấy giao; `len(...)` đếm số phần tử. Đây là một mô hình đơn giản để có điểm so sánh ban đầu, không phải một mô hình đã học ý nghĩa.

Tiếng Việt có từ nhiều âm tiết: “học máy” ở đây bị tách thành “học” và “máy”. Mỗi phần đang xử lý là một token theo quy tắc đơn giản, không mặc định là một từ hoàn chỉnh.

## Thực hành

Mở `lessons/01_overlap.py`, chỉ cần đọc khối từ `query_tokens` đến `score = len(shared)` trước. Các dòng còn lại lưu kết quả, sắp xếp và in ra.

Trong thư mục `nlp-retrieval-lab`, chạy:

```bash
python3 lessons/01_overlap.py
```

Với “học máy”, đoạn 1 và đoạn 2 đều được 2 điểm. Chương trình chọn đoạn 1 trước vì quy tắc giữ thứ tự khi bằng điểm; điểm số không chứng minh đoạn 1 phù hợp hơn. Nếu ý định tìm là Machine Learning, đoạn 2 mới đúng chủ đề.

Đổi `query` thành `"quy luật dữ liệu"` rồi chạy lại. Đoạn 2 sẽ được 4 điểm, hai đoạn còn lại 0 điểm. Quan sát sự khác nhau; không cần viết lại thuật toán hay trả lời một bài kiểm tra.

## Nối vào dự án thật

Phương pháp `overlap` trong `retrieval.py` cũng đếm token phân biệt trùng nhau. Bản thật còn xử lý Unicode, chữ hoa và dấu câu, và bỏ các kết quả có điểm 0. Ví dụ buổi này giữ cả điểm 0 để quan sát dễ hơn.

Sau khi bạn đã tự chạy và sửa câu tìm kiếm, mới thêm việc đó vào `docs/CONTRIBUTIONS.md`. Trợ lý đã tạo và kiểm tra ví dụ; điều đó chưa tự động thành phần thực hành độc lập của bạn.

Bước sau: xem một token có mặt ở hầu hết các đoạn thì hữu ích đến mức nào. Đó là lý do tìm hiểu trọng số TF-IDF; TF-IDF vẫn chưa tự hiểu ý nghĩa hoặc thứ tự chữ.
