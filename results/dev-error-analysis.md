# Development ranking casebook

Examples below come only from the development split. They are selected by query ID, not manually chosen for a favorable outcome. Rank differences are observations; they do not prove why a model succeeds or fails. Read the full passages in the demo to examine possible causes.

## Semantic top-1 correct; TF-IDF top-1 incorrect

### Query `56beb7953aeaaa14008c92ad`

Ai đã giành Super Bowl XLIX?

Gold title: **Super_Bowl_50**. Passage ID: `34d6bc0e2da46017317c9ba3d115b62df112eb815d78df309cd50aa7e23a6868`.

> Broncos đã đánh bại Pittsburgh Steelers ở vòng bảng với điểm số 23-16, bằng cách ghi 11 điểm trong ba phút cuối cùng của trận đấu. Sau đó, họ đánh bại đương kim vô địch Super Bowl XLIX New England Patriots trong AFC Championship Game với điểm số 20-18, bằng cách đoạt bóng từ đường chuyền trong nỗ lực chuyển đổi 2 điểm của New England với 17 giây còn lại trên đồng hồ. Bất chấp những vấn đề của Manning với việc đoạt bóng trong mùa giải, anh đã không ném bóng trong hai trận đấu playoff của họ.

| Method | Gold rank in top 5 | Top result title |
|---|---:|---|
| overlap | 2 | Super_Bowl_50 |
| tfidf | 2 | Super_Bowl_50 |
| semantic | 1 | Super_Bowl_50 |

Review prompts: Does the top passage contain the requested fact? Which query words or related meanings appear in each passage? Could an unlabeled passage also be relevant? For long passages, check whether the relevant evidence falls beyond the model's token limit.

### Query `56beb86b3aeaaa14008c92c0`

John Elway hiện đang có vai trò gì trong hệ thống của Broncos?

Gold title: **Super_Bowl_50**. Passage ID: `1bf4034fd4142bdeaba3f7f809a6d0f60d58d4ccc968d21b85ee860129e42612`.

> Peyton Manning trở thành thủ quân (quaterback) đầu tiên từng dẫn dắt hai đội khác nhau đến nhiều trận đấu Super Bowls. Anh ấy cũng là thủ quân lớn tuổi nhất từng chơi trong trận Super Bowl ở tuổi 39. Kỷ lục trong quá khứ do John Elway nắm giữ, người đã dẫn dắt Broncos giành chiến thắng trong trận Super Bowl XXXIII ở tuổi 38 và hiện là Phó Chủ tịch Điều hành Bóng đá và Tổng Giám đốc của Denver.

| Method | Gold rank in top 5 | Top result title |
|---|---:|---|
| overlap | Miss | Scottish_Parliament |
| tfidf | 2 | Scottish_Parliament |
| semantic | 1 | Super_Bowl_50 |

Review prompts: Does the top passage contain the requested fact? Which query words or related meanings appear in each passage? Could an unlabeled passage also be relevant? For long passages, check whether the relevant evidence falls beyond the model's token limit.

## TF-IDF top-1 correct; semantic top-1 incorrect

### Query `56beca913aeaaa14008c946f`

Hậu vệ Panther nào phạm lỗi giữ người ở lượt chơi thứ ba?

Gold title: **Super_Bowl_50**. Passage ID: `877fe0a2b4660db1c85d51f125b471205a3807d3a3eb652e8af1e1d9fd09a239`.

> Khi thời gian quy định còn lại 4:51, Carolina có bóng ở vạch 24 yard ở phần sân của mình với cơ hội để tổ chức một lượt tấn công ghi điểm, và sớm phải đối mặt với “lượt chơi thứ 3 và phải tiến 9 yard”. Ở lượt chơi tiếp theo, Miller đã tước bóng từ Newton, và sau khi nhiều cầu thủ lao vào quả bóng, quả bóng đã bị bật ngược trở lại và Ward đã lấy lại được bóng, và đã đưa bóng trở lại 5 yard đến vạch 4 yard ở phần sân của Panthers. Mặc dù một số người chơi đã lao vào để cố gắng lấy lại quả bóng, Ne…

| Method | Gold rank in top 5 | Top result title |
|---|---:|---|
| overlap | 1 | Super_Bowl_50 |
| tfidf | 1 | Super_Bowl_50 |
| semantic | 2 | Super_Bowl_50 |

Review prompts: Does the top passage contain the requested fact? Which query words or related meanings appear in each passage? Could an unlabeled passage also be relevant? For long passages, check whether the relevant evidence falls beyond the model's token limit.

### Query `56bf36b93aeaaa14008c9564`

Trận đấu còn lại bao nhiêu giây khi Broncos đoạt bóng từ đường chuyền và giành chiến thắng trong trận đấu?

Gold title: **Super_Bowl_50**. Passage ID: `34d6bc0e2da46017317c9ba3d115b62df112eb815d78df309cd50aa7e23a6868`.

> Broncos đã đánh bại Pittsburgh Steelers ở vòng bảng với điểm số 23-16, bằng cách ghi 11 điểm trong ba phút cuối cùng của trận đấu. Sau đó, họ đánh bại đương kim vô địch Super Bowl XLIX New England Patriots trong AFC Championship Game với điểm số 20-18, bằng cách đoạt bóng từ đường chuyền trong nỗ lực chuyển đổi 2 điểm của New England với 17 giây còn lại trên đồng hồ. Bất chấp những vấn đề của Manning với việc đoạt bóng trong mùa giải, anh đã không ném bóng trong hai trận đấu playoff của họ.

| Method | Gold rank in top 5 | Top result title |
|---|---:|---|
| overlap | 2 | Super_Bowl_50 |
| tfidf | 1 | Super_Bowl_50 |
| semantic | 2 | Super_Bowl_50 |

Review prompts: Does the top passage contain the requested fact? Which query words or related meanings appear in each passage? Could an unlabeled passage also be relevant? For long passages, check whether the relevant evidence falls beyond the model's token limit.

## Both top-1 incorrect

### Query `56e181d9e3433e1400422fa2`

Một thuật ngữ khác cho chuỗi của một trường hợp là gì?

Gold title: **Computational_complexity_theory**. Passage ID: `b59fb3a8c215b0a14a5119a2f156930063d6f04d0cfba8c4fc58c70fd80d2d51`.

> Khi xem xét các vấn đề tính toán, một trường hợp là một xâu ký tự trong một bảng chữ cái. Bảng chữ cái thường dùng là bảng chữ cái nhị phân (tức là tập {0,1}), và do đó xâu ký tự là dãy bit. Cũng như trong máy tính trên thực tế, các đối tượng toán học không phải dãy bit cần phải được mã hóa hợp lý. Ví dụ như một số nguyên cần phải được biểu diễn dưới dạng nhị phân, đồ thị có thể được biểu diễn dưới dạng ma trận kề, hoặc mã hóa danh sách kề dưới dạng nhị phân.

| Method | Gold rank in top 5 | Top result title |
|---|---:|---|
| overlap | Miss | European_Union_law |
| tfidf | Miss | Private_school |
| semantic | 2 | Prime_number |

Review prompts: Does the top passage contain the requested fact? Which query words or related meanings appear in each passage? Could an unlabeled passage also be relevant? For long passages, check whether the relevant evidence falls beyond the model's token limit.

### Query `56e1b62ecd28a01900c67aa4`

Lý thuyết độ phức tạp phân loại các vấn đề dựa trên thuộc tính chính nào?

Gold title: **Computational_complexity_theory**. Passage ID: `2647280002dc738dce9df95b641f8bfcafd5d184247f1ac0b850c5df85ded1cc`.

> Để có định nghĩa chính xác về ý nghĩa của việc giải quyết vấn đề bằng cách sử dụng một lượng thời gian và không gian nhất định, một mô hình tính toán như máy Turing tất định được sử dụng. Thời gian được yêu cầu bởi máy Turing tất định M với dữ liệu vào x là tổng số lần chuyển trạng thái hoặc các bước mà máy thực hiện trước khi dừng và đưa ra câu trả lời ("có" hoặc "không"). Một máy Turing M được cho là hoạt động trong khoảng thời gian f(n), nếu thời gian mà M yêu cầu trên mỗi đầu vào có độ dài n…

| Method | Gold rank in top 5 | Top result title |
|---|---:|---|
| overlap | 1 | Computational_complexity_theory |
| tfidf | 3 | Computational_complexity_theory |
| semantic | 2 | Computational_complexity_theory |

Review prompts: Does the top passage contain the requested fact? Which query words or related meanings appear in each passage? Could an unlabeled passage also be relevant? For long passages, check whether the relevant evidence falls beyond the model's token limit.

## Scope

This casebook is descriptive and has no manually validated error-category counts. It cannot establish paraphrase robustness, causality, or general superiority on Vietnamese retrieval.

Quoted source material: XQuAD, Artetxe, Ruder & Yogatama (2019), CC BY-SA 4.0. Excerpts are shortened; full text and the original license are downloaded by `dataset.py`.
