import copy
import json
from pathlib import Path
import tempfile
import unittest

from evaluate import evaluate, paired_top1
from freeze_protocol import SOURCE_FILES, current_snapshot, model_configuration, verify_protocol


def hits(rank):
    ids = ["a", "b", "c", "d", "e"]
    if rank is not None:
        ids[rank - 1] = "gold"
    return [{"document": {"id": doc_id}} for doc_id in ids]


class EvaluationChecks(unittest.TestCase):
    def test_batch_metrics_cover_first_second_fifth_and_miss(self):
        class BatchEngine:
            def search_many(self, queries, method, top_k):
                self.received = queries, method, top_k
                return [hits(rank) for rank in (1, 2, 5, None)]
        engine = BatchEngine()
        queries = [{"id": str(i), "text": str(i), "gold_id": "gold"} for i in range(4)]
        result = evaluate(engine, queries, "semantic")
        self.assertEqual(engine.received, (["0", "1", "2", "3"], "semantic", 5))
        self.assertEqual(result["hit_at_1"], 0.25)
        self.assertEqual(result["hit_at_5"], 0.75)
        self.assertAlmostEqual(result["mrr_at_5"], 0.425)
        self.assertEqual(result["timing_mode"], "batch throughput")

    def test_sixth_result_does_not_count_as_top_five(self):
        class Engine:
            def search(self, query, method, top_k):
                return hits(None) + [{"document": {"id": "gold"}}]
        result = evaluate(Engine(), [{"id": "q", "text": "q", "gold_id": "gold"}], "tfidf")
        self.assertEqual(result["hit_at_5"], 0)
        self.assertEqual(result["mrr_at_5"], 0)

    def test_invalid_batch_and_duplicate_results_are_rejected(self):
        class Engine:
            def __init__(self, output):
                self.output = output
            def search_many(self, queries, method, top_k):
                return self.output
        queries = [{"id": "q", "text": "q", "gold_id": "gold"}]
        with self.assertRaisesRegex(ValueError, "number"):
            evaluate(Engine([]), queries, "semantic")
        with self.assertRaisesRegex(ValueError, "duplicate"):
            evaluate(Engine([[{"document": {"id": "gold"}}] * 2]), queries, "semantic")
        with self.assertRaisesRegex(ValueError, "No evaluation"):
            evaluate(Engine([]), [], "semantic")
        with self.assertRaisesRegex(ValueError, "top_k"):
            evaluate(Engine([]), queries, "semantic", top_k=3)

    def test_paired_top_one_counts_each_outcome(self):
        results = [
            {"method": method, "details": [{"query_id": str(i), "gold_rank_at_5": rank} for i, rank in enumerate(ranks)]}
            for method, ranks in (("tfidf", (1, 1, 2, None)), ("semantic", (1, 2, 1, None)))
        ]
        self.assertEqual(paired_top1(results), {
            "left": "tfidf", "right": "semantic", "both_correct": 1,
            "left_only_correct": 1, "right_only_correct": 1, "both_incorrect": 1,
        })


class FrozenProtocolChecks(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for filename in SOURCE_FILES:
            (self.root / filename).write_text("# original source\n", encoding="utf-8")
        self.data = {"metadata": {"raw_sha256": "fixture"}, "documents": [{"id": "a", "text": "fixture"}],
                     "queries": [{"id": "q", "text": "question", "gold_id": "a", "split": "dev"}]}
        self.metadata = {"model_name": "fixture", "model_revision": "revision-1", "max_seq_length": 512,
                         "device": "cpu", "cache_hit": False, "setup_seconds": 10}
        self.protocol = {"snapshot": current_snapshot(self.data, self.root),
                         "model_configuration": model_configuration(self.metadata),
                         "methods": ["overlap", "tfidf", "semantic"], "top_k": 5}
        self.path = self.root / "protocol.json"
        self.path.write_text(json.dumps(self.protocol), encoding="utf-8")

    def test_matching_freeze_allows_runtime_changes(self):
        changed = {**self.metadata, "device": "mps", "cache_hit": True, "setup_seconds": 1}
        self.assertEqual(verify_protocol(self.data, changed, self.path, self.root), self.protocol)

    def test_source_changes_invalidate_frozen_protocol(self):
        (self.root / "retrieval.py").write_text("# changed source\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "source_sha256"):
            verify_protocol(self.data, self.metadata, self.path, self.root)

    def test_data_changes_invalidate_frozen_protocol(self):
        changed = copy.deepcopy(self.data)
        changed["queries"][0]["text"] = "edited question"
        with self.assertRaisesRegex(ValueError, "dataset_sha256"):
            verify_protocol(changed, self.metadata, self.path, self.root)

    def test_model_revision_changes_invalidate_frozen_protocol(self):
        changed = {**self.metadata, "model_revision": "revision-2"}
        with self.assertRaisesRegex(ValueError, "model configuration"):
            verify_protocol(self.data, changed, self.path, self.root)


if __name__ == "__main__":
    unittest.main()
