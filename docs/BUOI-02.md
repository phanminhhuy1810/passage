# Buổi 2: token hiếm giúp phân biệt chủ đề

Buổi 1 cho mỗi token trùng 1 điểm. Buổi này thay đúng một yếu tố: token khác nhau có thể đóng góp số điểm khác nhau.

## Ví dụ

Câu tìm: “học python”. Kho văn bản:

1. “tôi học toán”
2. “python là ngôn ngữ lập trình”
3. “tôi học lịch sử”

Đếm token trùng cho cả ba đoạn 1 điểm. Trong kho này, “học” có mặt trong 2 đoạn, “python” trong 1 đoạn. “python” giúp xác định chủ đề cụ thể hơn.

**Document frequency (df)** là số đoạn chứa một token. Nếu lặp “học” 10 lần trong cùng một đoạn, đoạn đó vẫn chỉ đóng góp 1 vào df của “học”. Đây là lý do vòng đếm df đi qua `set`, giống cách bỏ token trùng ở buổi 1.

## Trọng số IDF

Ví dụ dùng cùng công thức smoothed IDF như dự án chính:

`idf(token) = ln((1 + N) / (1 + df(token))) + 1`

N là tổng số đoạn. Với N = 3:

- “học”: `ln(4/3) + 1 ≈ 1.288`.
- “python”: `ln(4/2) + 1 ≈ 1.693`.

df càng nhỏ thì tỷ số càng lớn, log càng lớn, trọng số càng cao. Đây là giả định token hiếm trong kho thường giúp phân biệt tài liệu; không phải quy tắc rằng mọi token hiếm đều có ý nghĩa hoặc luôn đáng tin. Lỗi gõ chữ cũng có thể rất hiếm.

Các số 1 trong tử/mẫu là cách làm trơn; số 1 ngoài log giữ trọng số dương. [Tài liệu scikit-learn, Tf-idf term weighting](https://scikit-learn.org/stable/modules/feature_extraction.html#tfidf-term-weighting) giải thích công thức này. Chưa cần đọc hết trang.

## Cách chấm trong ví dụ

`weighted_score = sum(idf[token] for token in shared)`

Giữ nguyên phép lấy giao hai tập; thay `len(shared)` bằng tổng trọng số. Ba đoạn lần lượt được 1.288, 1.693 và 1.288 điểm, nên đoạn giới thiệu Python đứng đầu.

Đây là **IDF-weighted overlap**, chưa phải thuật toán TF-IDF + cosine trong `retrieval.py`. Chưa dùng số lần xuất hiện trong từng đoạn (TF), vector hoặc chuẩn hóa. IDF cũng không khôi phục thứ tự chữ hoặc tự hiểu đồng nghĩa; trường hợp “học” + “xe máy” ở buổi 1 chưa được giải quyết chỉ bằng việc đổi trọng số.

## Chạy và đọc code

Trong thư mục dự án:

```bash
python3 lessons/02_idf.py
```

Đọc trước vòng đếm `document_frequency`, công thức `idf`, rồi dòng `weighted_score`. Các đoạn in kết quả chỉ phục vụ quan sát.

Nếu bạn đã tự chạy và đọc code, ghi đúng phần mình làm vào contribution log. Trợ lý đã chạy ví dụ không có nghĩa bạn đã thực hiện độc lập. Đây là dữ liệu minh họa có chủ ý, chưa chứng minh chất lượng trên XQuAD.
