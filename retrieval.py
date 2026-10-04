"""Small, inspectable lexical retrieval baselines. Python standard library only."""

import math
import re
import unicodedata
from collections import Counter


def tokenize(text):
    """Vietnamese syllable-level tokens, not linguistic word segmentation."""
    normalized = unicodedata.normalize("NFC", text).lower()
    return re.findall(r"[^\W_]+", normalized, flags=re.UNICODE)


class Retriever:
    def __init__(self, documents):
        if not documents:
            raise ValueError("The document collection must not be empty.")
        self.documents = documents
        self.counts = [Counter(tokenize(doc["text"])) for doc in documents]
        document_frequency = Counter()
        for counts in self.counts:
            document_frequency.update(counts.keys())
        n = len(documents)
        self.idf = {
            word: math.log((1 + n) / (1 + frequency)) + 1
            for word, frequency in document_frequency.items()
        }
        self.vectors = [self.vectorize(counts) for counts in self.counts]

    def vectorize(self, counts):
        # A dictionary stores only non-zero coordinates of a sparse vector.
        weights = {
            word: count * self.idf[word]
            for word, count in counts.items()
            if word in self.idf
        }
        length = math.sqrt(sum(weight ** 2 for weight in weights.values()))
        if length == 0:
            return {}
        return {word: weight / length for word, weight in weights.items()}

    def search(self, query, method="tfidf", top_k=5):
        if method not in {"overlap", "tfidf"}:
            raise ValueError("Choose overlap or tfidf.")
        if top_k < 1:
            raise ValueError("top_k must be positive.")
        words = Counter(tokenize(query))
        if not words:
            return []
        query_vector = self.vectorize(words)
        hits = []
        for doc, counts, vector in zip(self.documents, self.counts, self.vectors):
            if method == "overlap":
                score = float(len(words.keys() & counts.keys()))
            else:
                # Both vectors have unit length: dot product = cosine similarity.
                score = sum(weight * vector.get(word, 0) for word, weight in query_vector.items())
            if score > 0:
                hits.append({"document": doc, "score": score})
        # Stable tie-breaking makes repeated evaluations reproducible.
        hits.sort(key=lambda hit: (-hit["score"], hit["document"]["id"]))
        return hits[:top_k]
