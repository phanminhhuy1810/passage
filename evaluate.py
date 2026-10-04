"""Compare fixed retrieval methods; final test requires a matching frozen protocol."""

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import platform
import time

from dataset import ROOT, load_dataset

METHODS = ("overlap", "tfidf", "semantic")
TOP_K = 5


def evaluate(engine, queries, method, top_k=TOP_K):
    """Count every missing gold passage as zero; timing is batch throughput."""
    if top_k != TOP_K:
        raise ValueError("This benchmark publishes Hit@5 and MRR@5; top_k must be 5.")
    if not queries:
        raise ValueError("No evaluation queries.")
    start = time.perf_counter()
    if callable(getattr(engine, "search_many", None)):
        ranked = engine.search_many([q["text"] for q in queries], method, top_k)
        timing_mode = "batch throughput"
    else:
        ranked = [engine.search(q["text"], method, top_k) for q in queries]
        timing_mode = "sequential throughput"
    elapsed = time.perf_counter() - start
    if len(ranked) != len(queries):
        raise ValueError("Search returned a different number of result lists than queries.")
    rows = []
    for query, hits in zip(queries, ranked):
        ids = [hit["document"]["id"] for hit in hits[:top_k]]
        if len(ids) != len(set(ids)):
            raise ValueError("A search result contains duplicate document IDs.")
        rank = ids.index(query["gold_id"]) + 1 if query["gold_id"] in ids else None
        rows.append({
            "query_id": query["id"], "query": query["text"], "gold_id": query["gold_id"],
            "gold_rank_at_5": rank, "retrieved_ids": ids,
        })
    n = len(rows)
    return {
        "method": method, "query_count": n, "top_k": top_k,
        "hit_at_1": sum(row["gold_rank_at_5"] == 1 for row in rows) / n,
        "hit_at_5": sum(row["gold_rank_at_5"] is not None for row in rows) / n,
        "mrr_at_5": sum(1 / row["gold_rank_at_5"] if row["gold_rank_at_5"] else 0 for row in rows) / n,
        "total_search_seconds": elapsed,
        "throughput_ms_per_query": 1000 * elapsed / n,
        "queries_per_second": n / elapsed if elapsed else None,
        "timing_mode": timing_mode, "details": rows,
    }


def paired_top1(results, left="tfidf", right="semantic"):
    """Describe paired outcomes without claiming statistical significance."""
    by_method = {result["method"]: result for result in results}
    first = {row["query_id"]: row for row in by_method[left]["details"]}
    second = {row["query_id"]: row for row in by_method[right]["details"]}
    if first.keys() != second.keys():
        raise ValueError("Paired methods were evaluated on different queries.")
    counts = {"both_correct": 0, "left_only_correct": 0, "right_only_correct": 0, "both_incorrect": 0}
    for query_id in first:
        a = first[query_id]["gold_rank_at_5"] == 1
        b = second[query_id]["gold_rank_at_5"] == 1
        category = "both_correct" if a and b else "left_only_correct" if a else "right_only_correct" if b else "both_incorrect"
        counts[category] += 1
    return {"left": left, "right": right, **counts}


def package_versions():
    versions = {}
    for package in ("numpy", "torch", "transformers", "sentence-transformers", "huggingface-hub"):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            pass
    return versions


def report_summary(report):
    split = report["split"]
    lines = [
        f"# {split.upper()} evaluation — Vietnamese passage retrieval", "",
        f"Collection: **{report['document_count']} passages**. Evaluation: **{report['query_count']} {split} questions**.", "",
        "| Method | Hit@1 | Hit@5 | MRR@5 | Batch ms/query* |", "|---|---:|---:|---:|---:|",
    ]
    for result in report["results"]:
        lines.append(f"| {result['method']} | {result['hit_at_1']:.4f} | {result['hit_at_5']:.4f} | {result['mrr_at_5']:.4f} | {result['throughput_ms_per_query']:.2f} |")
    pair = report["paired_top1"]
    lines += [
        "", "*Timing is amortized batch/sequential throughput on this machine, not per-request interactive latency. "
        "The model/index is warmed with a development query before evaluation; engine setup and warm-up are reported separately. "
        "The methods use different execution strategies, so timing is descriptive and not a controlled speed comparison.", "",
        f"TF-IDF / semantic top-1 outcomes: both correct **{pair['both_correct']}**; "
        f"TF-IDF only **{pair['left_only_correct']}**; semantic only **{pair['right_only_correct']}**; "
        f"both incorrect **{pair['both_incorrect']}**. No significance test is claimed.", "",
        "## Protocol", "",
        "This is a [XQuAD](https://github.com/google-deepmind/xquad) adaptation to **closed-corpus passage retrieval**, "
        "not the official extractive QA task. Its scores must not be compared with XQuAD QA EM/F1.", "",
        f"All {report['document_count']} passages are available to indexing. Questions are split 70/30 by source paragraph using seed 42; "
        "questions about a paragraph stay in the same split. Query labels are not used to train or fit the retrievers. "
        "This measures unseen questions about a known collection, not generalization to an unseen collection.", "",
        "Hit@1 is the fraction with the annotated passage ranked first. Hit@5 is the fraction found in the top five. "
        "MRR@5 averages reciprocal gold rank, with zero for a miss. There is one annotated relevant passage per query.", "",
        ("The protocol, source hashes, data hashes and model configuration were frozen before this final evaluation."
         if split == "test" else "These development results may be inspected to debug the pipeline; they are not untouched final evidence."), "",
        "## Model and runtime", "", "```json", json.dumps(report["engine"], ensure_ascii=False, indent=2), "```", "",
        f"Engine initialization: {report['engine_initialization_seconds']:.2f} s. Warm-up across three methods: {report['warmup_seconds']:.2f} s.", "",
        "## Limitations", "",
    ]
    lines += [f"- {item}" for item in report["limitations"]]
    lines += [
        "", "## Reproduction", "",
        f"- Dataset revision: `{report['dataset']['upstream_commit']}`.",
        f"- Raw dataset SHA-256: `{report['dataset']['raw_sha256']}`.",
        f"- Evaluation source SHA-256: `{report['code_sha256']}`.",
        f"- Python: `{report['python']}`; device and model revision are above.",
        f"- Protocol SHA-256: `{report.get('protocol_sha256') or 'not frozen (development)'}`.",
        "- Detailed per-query ranks remain local in `results/" + split + ".json`; compact metrics are in `results/" + split + "-metrics.json`.",
        "- See [the research protocol](../docs/RESEARCH-PROTOCOL.md) for freeze and final-test commands.", "",
        "Implementation and experiments were completed with AI assistance. These measurements describe the system; "
        "they do not establish the student's independent implementation or mastery.", "",
        "Dataset attribution: XQuAD — Artetxe, Ruder & Yogatama (2019), CC BY-SA 4.0. "
        "Passage grouping, retrieval adaptation and evaluation are specific to this project.",
    ]
    return "\n".join(lines) + "\n"


def error_analysis(data, results):
    """Write inspectable DEV examples, selected deterministically by query ID."""
    documents = {doc["id"]: doc for doc in data["documents"]}
    methods = {result["method"]: {row["query_id"]: row for row in result["details"]} for result in results}
    groups = {"Semantic top-1 correct; TF-IDF top-1 incorrect": [],
              "TF-IDF top-1 correct; semantic top-1 incorrect": [], "Both top-1 incorrect": []}
    for query_id in sorted(methods["tfidf"]):
        lexical, semantic = methods["tfidf"][query_id], methods["semantic"][query_id]
        a, b = lexical["gold_rank_at_5"] == 1, semantic["gold_rank_at_5"] == 1
        if b and not a:
            groups["Semantic top-1 correct; TF-IDF top-1 incorrect"].append(query_id)
        elif a and not b:
            groups["TF-IDF top-1 correct; semantic top-1 incorrect"].append(query_id)
        elif not a and not b:
            groups["Both top-1 incorrect"].append(query_id)
    lines = ["# Development ranking casebook", "",
             "Examples below come only from the development split. They are selected by query ID, "
             "not manually chosen for a favorable outcome. Rank differences are observations; they do not prove "
             "why a model succeeds or fails. Read the full passages in the demo to examine possible causes.", ""]
    for category, ids in groups.items():
        lines += [f"## {category}", ""]
        if not ids:
            lines += ["No development example in this category.", ""]
        for query_id in ids[:2]:
            query = methods["tfidf"][query_id]
            gold = documents[query["gold_id"]]
            lines += [f"### Query `{query_id}`", "", query["query"], "",
                      f"Gold title: **{gold['title']}**. Passage ID: `{gold['id']}`.", "",
                      "> " + gold["text"][:500].replace("\n", " ") + ("…" if len(gold["text"]) > 500 else ""), "",
                      "| Method | Gold rank in top 5 | Top result title |", "|---|---:|---|"]
            for method in METHODS:
                row = methods[method][query_id]
                top_title = documents[row["retrieved_ids"][0]]["title"] if row["retrieved_ids"] else "No positive-score result"
                lines.append(f"| {method} | {row['gold_rank_at_5'] or 'Miss'} | {top_title.replace('|', '/')} |")
            lines += ["", "Review prompts: Does the top passage contain the requested fact? Which query words "
                      "or related meanings appear in each passage? Could an unlabeled passage also be relevant? "
                      "For long passages, check whether the relevant evidence falls beyond the model's token limit.", ""]
    lines += ["## Scope", "", "This casebook is descriptive and has no manually validated error-category counts. "
              "It cannot establish paraphrase robustness, causality, or general superiority on Vietnamese retrieval.", "",
              "Quoted source material: XQuAD, Artetxe, Ruder & Yogatama (2019), CC BY-SA 4.0. "
              "Excerpts are shortened; full text and the original license are downloaded by `dataset.py`."]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=("dev", "test"), default="dev")
    parser.add_argument("--final-test", action="store_true", help="Evaluate test only after freeze_protocol.py succeeds.")
    args = parser.parse_args()
    if args.split == "test" and not args.final_test:
        parser.error("Test is reserved: freeze the protocol, then add --final-test.")
    if args.final_test and args.split != "test":
        parser.error("--final-test is only valid with --split test.")
    from freeze_protocol import current_snapshot, protocol_digest, verify_protocol
    from engine import SearchEngine
    data = load_dataset()
    protocol = verify_protocol(data) if args.split == "test" else None
    start = time.perf_counter()
    engine = SearchEngine(data["documents"])
    initialization = time.perf_counter() - start
    # Warm-up deliberately uses a DEV question, including on the final test run.
    warmup_query = next(q["text"] for q in data["queries"] if q["split"] == "dev")
    start = time.perf_counter()
    for method in METHODS:
        engine.search(warmup_query, method, TOP_K)
    warmup = time.perf_counter() - start
    if protocol:
        verify_protocol(data, engine.metadata)
    queries = [q for q in data["queries"] if q["split"] == args.split]
    results = []
    for method in METHODS:
        print(f"Evaluating {method}: {len(queries)} {args.split} queries…", flush=True)
        results.append(evaluate(engine, queries, method))
    snapshot = current_snapshot(data)
    report = {
        "split": args.split, "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "document_count": len(data["documents"]), "query_count": len(queries),
        "dataset": data["metadata"], "python": platform.python_version(), "packages": package_versions(),
        "code_sha256": hashlib.sha256(json.dumps(snapshot["source_sha256"], sort_keys=True).encode()).hexdigest(),
        "source_sha256": snapshot["source_sha256"], "protocol_sha256": protocol_digest() if protocol else None,
        "engine": engine.metadata, "engine_initialization_seconds": initialization, "warmup_seconds": warmup,
        "results": results, "paired_top1": paired_top1(results),
        "limitations": [
            "Small, translated, QA-derived collection; not the official XQuAD QA benchmark or a broad Vietnamese search benchmark.",
            "Only the original source paragraph is labeled relevant; other relevant passages may be scored as wrong.",
            "The full candidate corpus is shared by dev and test. This is unseen-query evaluation on a known corpus.",
            "Lexical tokenization uses Unicode-normalized syllables, not Vietnamese word segmentation.",
            "The pretrained semantic model is used without task-specific fine-tuning. Pretraining overlap with this benchmark cannot be ruled out.",
            "The model truncates long inputs at its configured token limit; inspect corpus_truncated_count in model metadata.",
            "No paraphrase, out-of-domain, no-answer, large-corpus or statistical-significance experiment has been completed.",
            "Batch throughput depends on hardware, caches and batch strategy and is not interactive request latency.",
        ],
    }
    output = ROOT / "results"
    output.mkdir(exist_ok=True)
    detailed = output / f"{args.split}.json"
    detailed.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    compact = {**report, "results": [{key: value for key, value in result.items() if key != "details"} for result in results]}
    (output / f"{args.split}-metrics.json").write_text(json.dumps(compact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / f"{args.split}-summary.md").write_text(report_summary(report), encoding="utf-8")
    if args.split == "dev":
        (output / "dev-error-analysis.md").write_text(error_analysis(data, results), encoding="utf-8")
    for result in results:
        print(f"{result['method']:8s} Hit@1={result['hit_at_1']:.4f} Hit@5={result['hit_at_5']:.4f} MRR@5={result['mrr_at_5']:.4f}")
    print(f"Detailed report: {detailed}")


if __name__ == "__main__":
    main()
