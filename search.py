"""Search the passage collection and inspect ranked results."""

import argparse
from dataset import load_dataset
from engine import SearchEngine, METHODS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="A Vietnamese question or phrase")
    parser.add_argument("--method", choices=METHODS, default="tfidf")
    parser.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args()
    if args.top_k < 1:
        parser.error("--top-k must be positive")
    engine = SearchEngine(load_dataset()["documents"], enable_semantic=args.method == "semantic")
    hits = engine.search(args.query, args.method, args.top_k)
    if not hits:
        print("Không có từ phù hợp trong kho văn bản.")
    for rank, hit in enumerate(hits, 1):
        doc = hit["document"]
        print(f"\n{rank}. {doc['title']} | score={hit['score']:.4f}")
        print(doc["text"])


if __name__ == "__main__":
    main()
