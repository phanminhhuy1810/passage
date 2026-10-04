"""One interface for all three retrieval methods."""

from retrieval import Retriever

METHODS = ("overlap", "tfidf", "semantic")


class SearchEngine:
    def __init__(self, documents, *, enable_semantic=True):
        self.lexical = Retriever(documents)
        self.semantic = None
        if enable_semantic:
            from semantic import SemanticRetriever
            self.semantic = SemanticRetriever(documents)

    @property
    def metadata(self):
        return self.semantic.metadata if self.semantic else {"semantic_enabled": False}

    def search(self, query, method="tfidf", top_k=5):
        if method not in METHODS:
            raise ValueError("Choose overlap, tfidf or semantic.")
        if method == "semantic":
            if self.semantic is None:
                raise RuntimeError("The semantic model has not been loaded.")
            return self.semantic.search(query, top_k)
        return self.lexical.search(query, method, top_k)

    def search_many(self, queries, method="tfidf", top_k=5):
        if method == "semantic":
            if self.semantic is None:
                raise RuntimeError("The semantic model has not been loaded.")
            return self.semantic.search_many(queries, top_k)
        return [self.search(query, method, top_k) for query in queries]
