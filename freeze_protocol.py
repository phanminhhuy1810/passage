"""Freeze the retrieval protocol after development and before final test."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from dataset import ROOT, load_dataset

PROTOCOL_PATH = ROOT / "results" / "protocol.json"
SOURCE_FILES = ("dataset.py", "retrieval.py", "engine.py", "semantic.py", "evaluate.py", "freeze_protocol.py")
MODEL_KEYS = ("model_name", "model_revision", "max_seq_length", "dimension", "query_prefix", "passage_prefix", "normalize_embeddings", "pooling")


def json_hash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def model_configuration(metadata):
    return {key: metadata[key] for key in MODEL_KEYS if key in metadata}


def current_snapshot(data, root=ROOT):
    root = Path(root)
    files = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in SOURCE_FILES if (root / name).exists()}
    return {
        "source_sha256": files, "dataset_sha256": json_hash(data), "dataset_metadata": data["metadata"],
        "document_count": len(data["documents"]),
        "split_query_counts": {split: sum(q["split"] == split for q in data["queries"]) for split in ("dev", "test")},
    }


def protocol_digest(path=PROTOCOL_PATH):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_protocol(data, metadata=None, path=PROTOCOL_PATH, root=ROOT):
    path = Path(path)
    if not path.exists():
        raise ValueError("No frozen protocol. Run python freeze_protocol.py before final test.")
    protocol = json.loads(path.read_text(encoding="utf-8"))
    current = current_snapshot(data, root)
    for key, value in current.items():
        if protocol["snapshot"].get(key) != value:
            raise ValueError(f"Frozen protocol mismatch: {key}. Resolve changes before opening test; do not tune on final-test results.")
    if protocol.get("methods") != ["overlap", "tfidf", "semantic"] or protocol.get("top_k") != 5:
        raise ValueError("Frozen protocol has different methods or ranking cutoff.")
    if metadata is not None and protocol.get("model_configuration") != model_configuration(metadata):
        raise ValueError("Semantic model configuration differs from frozen protocol.")
    return protocol


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replace", action="store_true", help="Replace an earlier freeze only before any final-test result exists.")
    args = parser.parse_args()
    if any((ROOT / "results" / name).exists() for name in ("test.json", "test-metrics.json")):
        parser.error("Final-test results already exist. Preserve this protocol and avoid tuning on the final test.")
    if PROTOCOL_PATH.exists() and not args.replace:
        parser.error("Protocol already exists. Use --replace only during development, before final test.")
    from engine import SearchEngine
    data = load_dataset()
    engine = SearchEngine(data["documents"])
    protocol = {
        "schema_version": 1, "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "frozen before final-test evaluation", "methods": ["overlap", "tfidf", "semantic"], "top_k": 5,
        "snapshot": current_snapshot(data), "model_configuration": model_configuration(engine.metadata),
        "reference_device": engine.metadata.get("device"),
        "metric_definitions": {
            "hit_at_1": "Fraction with the single annotated passage ranked first.",
            "hit_at_5": "Fraction with the single annotated passage in ranks 1 through 5.",
            "mrr_at_5": "Mean reciprocal annotated-passage rank through 5; zero for a miss.",
        },
        "selection_policy": "Fixed comparison of distinct-token overlap, TF-IDF cosine and a pinned pretrained multilingual embedding model; no fine-tuning.",
        "split_policy": "Paragraph-grouped questions, seed 42, 70/30 paragraph split; the full collection is known and indexed for both splits.",
        "test_policy": "Freeze after development; run the untouched test once for reporting and do not change methods in response to its scores.",
    }
    PROTOCOL_PATH.parent.mkdir(exist_ok=True)
    PROTOCOL_PATH.write_text(json.dumps(protocol, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Frozen protocol: {PROTOCOL_PATH}")
    print(f"Protocol SHA-256: {protocol_digest()}")
    print("Now run: python evaluate.py --split test --final-test")


if __name__ == "__main__":
    main()
