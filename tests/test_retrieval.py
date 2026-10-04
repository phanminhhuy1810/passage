import math
import unicodedata
import unittest

from dataset import prepare_records
from evaluate import evaluate
from retrieval import Retriever, tokenize


class RetrievalChecks(unittest.TestCase):
    def test_vietnamese_unicode_and_unknown_query(self):
        self.assertEqual(tokenize("DỮ LIỆU!"), tokenize(unicodedata.normalize("NFD", "dữ liệu")))
        engine = Retriever([{"id": "a", "title": "", "text": "dữ liệu"}])
        self.assertEqual(engine.search("zzzzunknown"), [])
        self.assertEqual(engine.search("!!!"), [])

    def test_cosine_does_not_reward_repeating_the_same_passage(self):
        engine = Retriever([
            {"id": "a", "title": "", "text": "model learns"},
            {"id": "b", "title": "", "text": "model learns model learns"},
            {"id": "c", "title": "", "text": "python runs"},
        ])
        hits = engine.search("model learns")
        self.assertEqual([hit["document"]["id"] for hit in hits], ["a", "b"])
        self.assertTrue(math.isclose(hits[0]["score"], hits[1]["score"]))

    def test_metrics_count_misses_and_rank_two(self):
        class FakeEngine:
            def search(self, query, method, top_k):
                return [] if query == "miss" else [{"document": {"id": "wrong"}}, {"document": {"id": "gold"}}]
        queries = [{"id": str(i), "text": text, "gold_id": "gold"} for i, text in enumerate(("hit", "miss"))]
        result = evaluate(FakeEngine(), queries, "tfidf")
        self.assertEqual(result["hit_at_1"], 0)
        self.assertEqual(result["hit_at_5"], .5)
        self.assertEqual(result["mrr_at_5"], .25)

    def test_duplicate_passages_stay_in_one_split(self):
        raw = {"data": [{"title": "demo", "paragraphs": [
            {"context": "same", "qas": [{"id": "q1", "question": "one"}]},
            {"context": "same", "qas": [{"id": "q2", "question": "two"}]},
            {"context": "different", "qas": [{"id": "q3", "question": "three"}]},
        ]}]}
        data = prepare_records(raw)
        self.assertEqual(len(data["documents"]), 2)
        self.assertEqual(data["queries"][0]["split"], data["queries"][1]["split"])


if __name__ == "__main__":
    unittest.main()
