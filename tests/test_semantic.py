"""Small deterministic checks of ranking and prefix semantics; no download needed."""

import tempfile
import unittest
import numpy as np
from semantic import SemanticRetriever, corpus_fingerprint


class FakeEncoder:
    def __init__(self):
        self.calls = []

    def get_embedding_dimension(self):
        return 2

    def tokenizer(self, texts, **kwargs):
        return {"length": [len(text.split()) for text in texts]}

    def encode(self, texts, **kwargs):
        self.calls.append(texts)
        return np.asarray([[1, 0] if "toán" in text else [0, 1] for text in texts], dtype=np.float32)


class SemanticChecks(unittest.TestCase):
    def test_prefixes_ranking_empty_and_ties(self):
        docs = [{"id": "b", "text": "toán"}, {"id": "a", "text": "toán"},
                {"id": "c", "text": "sinh học"}]
        encoder = FakeEncoder()
        with tempfile.TemporaryDirectory() as folder:
            engine = SemanticRetriever(docs, model=encoder, cache_dir=folder)
            batch = engine.search_many([" toán ", "!!!", "sinh học"], top_k=2)
        self.assertEqual(encoder.calls[0], ["passage: toán", "passage: toán", "passage: sinh học"])
        self.assertEqual(encoder.calls[1], ["query: toán", "query: sinh học"])
        self.assertEqual([hit["document"]["id"] for hit in batch[0]], ["a", "b"])
        self.assertEqual(batch[1], [])
        self.assertEqual(batch[2][0]["document"]["id"], "c")
        self.assertAlmostEqual(batch[0][0]["score"], 1)

    def test_cache_identity_changes_with_content_and_order(self):
        a = [{"id": "a", "text": "one"}, {"id": "b", "text": "two"}]
        self.assertNotEqual(corpus_fingerprint(a), corpus_fingerprint(a[::-1]))
        b = [dict(a[0], text="changed"), a[1]]
        self.assertNotEqual(corpus_fingerprint(a), corpus_fingerprint(b))


if __name__ == "__main__":
    unittest.main()
