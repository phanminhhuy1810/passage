"""Prepare a transparent passage-retrieval adaptation of Vietnamese XQuAD."""

import argparse
import hashlib
import json
from pathlib import Path
import ssl
import urllib.request
import unicodedata

ROOT = Path(__file__).resolve().parent
UPSTREAM_COMMIT = "7d30520c717524000f0d9d2f9c10a069acd9d285"
BASE_URL = f"https://raw.githubusercontent.com/google-deepmind/xquad/{UPSTREAM_COMMIT}"
PROCESSED = ROOT / "data" / "processed" / "dataset.json"


def prepare_records(raw, seed=42):
    documents = {}
    questions = []
    for article in raw["data"]:
        for paragraph in article["paragraphs"]:
            text = unicodedata.normalize("NFC", paragraph["context"])
            doc_id = hashlib.sha256(text.encode("utf-8")).hexdigest()
            documents.setdefault(doc_id, {"id": doc_id, "title": article["title"], "text": text})
            for qa in paragraph["qas"]:
                questions.append({"id": qa["id"], "text": qa["question"], "gold_id": doc_id})
    if len({q["id"] for q in questions}) != len(questions):
        raise ValueError("Duplicate query IDs in the source.")
    # Group by paragraph so questions about one paragraph cannot cross splits.
    ordered = sorted(documents, key=lambda key: hashlib.sha256(f"{seed}:{key}".encode()).hexdigest())
    boundary = int(len(ordered) * 0.7)
    dev_ids = set(ordered[:boundary])
    for query in questions:
        query["split"] = "dev" if query["gold_id"] in dev_ids else "test"
    return {"documents": sorted(documents.values(), key=lambda doc: doc["id"]), "queries": questions}


def prepare():
    raw_dir = ROOT / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    # Dataset and original license stay local; GitHub receives download instructions.
    for filename in ("xquad.vi.json", "CC-BY-SA4.0.txt"):
        path = raw_dir / filename
        if not path.exists():
            request = urllib.request.Request(f"{BASE_URL}/{filename}", headers={"User-Agent": "nlp-retrieval-lab"})
            # python.org macOS installs may lack their own CA bundle. Use the
            # system bundle if the default one is missing, preserving TLS checks.
            paths = ssl.get_default_verify_paths()
            system_ca = Path("/etc/ssl/cert.pem")
            context = ssl.create_default_context(
                cafile=str(system_ca) if paths.cafile is None and system_ca.exists() else None
            )
            with urllib.request.urlopen(request, timeout=30, context=context) as response:
                content = response.read()
            temporary = path.with_suffix(path.suffix + ".tmp")
            temporary.write_bytes(content)
            temporary.replace(path)
    raw_bytes = (raw_dir / "xquad.vi.json").read_bytes()
    records = prepare_records(json.loads(raw_bytes))
    records["metadata"] = {
        "source": "https://github.com/google-deepmind/xquad",
        "upstream_commit": UPSTREAM_COMMIT,
        "raw_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "license": "CC BY-SA 4.0",
        "adaptation": "Vietnamese closed-corpus passage retrieval; not official XQuAD QA evaluation",
        "split": "70/30 paragraph-grouped query split; fixed seed 42; full candidate corpus indexed",
    }
    PROCESSED.parent.mkdir(parents=True, exist_ok=True)
    PROCESSED.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Prepared {len(records['documents'])} passages and {len(records['queries'])} questions.")
    for split in ("dev", "test"):
        print(f"{split}: {sum(q['split'] == split for q in records['queries'])} questions")


def load_dataset():
    if not PROCESSED.exists():
        raise FileNotFoundError("Run python3 dataset.py first.")
    data = json.loads(PROCESSED.read_text(encoding="utf-8"))
    raw_path = ROOT / "data" / "raw" / "xquad.vi.json"
    if not raw_path.exists() or hashlib.sha256(raw_path.read_bytes()).hexdigest() != data["metadata"]["raw_sha256"]:
        raise ValueError("Source data changed or is missing. Re-run python3 dataset.py.")
    doc_ids = {doc["id"] for doc in data["documents"]}
    if len(doc_ids) != len(data["documents"]):
        raise ValueError("Duplicate document IDs.")
    if any(q["gold_id"] not in doc_ids for q in data["queries"]):
        raise ValueError("A question refers to a missing passage.")
    return data


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    prepare()
