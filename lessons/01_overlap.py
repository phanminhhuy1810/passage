"""Buổi 1: chấm điểm ba đoạn văn bằng số mảnh chữ trùng nhau.

Ví dụ cố ý dùng chữ thường, không có dấu câu để tập trung vào cách chấm điểm.
split() tách theo khoảng trắng, chưa phải tách từ tiếng Việt hoàn chỉnh.
"""

documents = [
    "tôi đi học bằng xe máy mỗi ngày",
    "học máy tìm quy luật trong dữ liệu",
    "đại số tuyến tính nghiên cứu vector và ma trận",
]

# Sau lượt đầu, đổi thành "quy luật dữ liệu" rồi chạy lại.
query = "học máy"
query_tokens = set(query.lower().split())
scores = []

print("Tìm:", query)
for doc_id, document in enumerate(documents, start=1):
    shared = query_tokens & set(document.lower().split())
    score = len(shared)
    scores.append((score, doc_id, document))
    print(f"Đoạn {doc_id}: {score} điểm | trùng: {', '.join(sorted(shared)) or '(không có)'}")
    print(" ", document)

# Điểm giảm dần; khi bằng điểm, giữ thứ tự đoạn ban đầu.
scores.sort(key=lambda row: (-row[0], row[1]))
print("\nĐoạn đứng đầu:", scores[0][1], "-", scores[0][2])
