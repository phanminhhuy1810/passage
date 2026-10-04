"""Buổi 2: token hiếm trong kho văn bản có trọng số lớn hơn.

Đây là overlap có trọng số IDF để học một ý mới, chưa phải TF-IDF + cosine.
Ví dụ cố ý không có dấu câu; cách tách theo khoảng trắng giống buổi 1.
"""

from math import log

documents = [
    "tôi học toán",
    "python là ngôn ngữ lập trình",
    "tôi học lịch sử",
]
query = "học python"
token_sets = [set(document.lower().split()) for document in documents]

# Đếm SỐ ĐOẠN chứa mỗi token, không đếm tổng số lần token xuất hiện.
document_frequency = {}
for tokens in token_sets:
    for token in tokens:
        document_frequency[token] = document_frequency.get(token, 0) + 1

n = len(documents)
idf = {
    token: log((1 + n) / (1 + frequency)) + 1
    for token, frequency in document_frequency.items()
}
query_tokens = set(query.lower().split())

print("Tìm:", query)
for token in sorted(query_tokens):
    print(f"{token}: có trong {document_frequency[token]}/{n} đoạn; IDF = {idf[token]:.3f}")

scores = []
for doc_id, (document, tokens) in enumerate(zip(documents, token_sets), start=1):
    shared = query_tokens & tokens
    overlap_score = len(shared)
    weighted_score = sum(idf[token] for token in shared)
    scores.append((doc_id, overlap_score, weighted_score))
    print(f"Đoạn {doc_id}: overlap = {overlap_score}; có trọng số = {weighted_score:.3f} | {document}")

overlap_order = sorted(scores, key=lambda row: (-row[1], row[0]))
weighted_order = sorted(scores, key=lambda row: (-row[2], row[0]))
print("Đứng đầu khi đếm trùng:", overlap_order[0][0])
print("Đứng đầu khi cộng IDF:", weighted_order[0][0])
