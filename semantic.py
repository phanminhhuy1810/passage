"""Pinned multilingual E5 embeddings and exact cosine retrieval.

Model weights are downloaded explicitly by setup_model.py. Normal search is local.
"""

import hashlib
import json
import os
from pathlib import Path
import time
import unicodedata

import numpy as np

ROOT = Path(__file__).resolve().parent
MODEL_NAME = "intfloat/multilingual-e5-small"
MODEL_REVISION = "614241f622f53c4eeff9890bdc4f31cfecc418b3"
MODEL_DIR = ROOT / ".cache" / "models" / MODEL_REVISION
MAX_SEQ_LENGTH = 512
DIMENSION = 384
BATCH_SIZE = 16


def normalize_text(text):
    return unicodedata.normalize("NFC", text).strip()


def corpus_fingerprint(documents):
    # Order matters: vector row i must always refer to document i.
    payload = [(d["id"], normalize_text(d["text"])) for d in documents]
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False).encode()).hexdigest()


class SemanticRetriever:
    def __init__(self, documents, *, model=None, cache_dir=None, device=None):
        if not documents:
            raise ValueError("The document collection must not be empty.")
        if len({d["id"] for d in documents}) != len(documents):
            raise ValueError("Document IDs must be unique.")
        started = time.perf_counter()
        self.documents = documents
        self.device = device or os.environ.get("RETRIEVAL_DEVICE", "cpu")
        supplied_model = model is not None
        if model is None:
            if not (MODEL_DIR / "model.safetensors").exists():
                raise FileNotFoundError("Model not installed. Run .venv/bin/python setup_model.py first.")
            import torch
            from sentence_transformers import SentenceTransformer
            torch.set_num_threads(min(4, os.cpu_count() or 1))
            model = SentenceTransformer(str(MODEL_DIR), device=self.device,
                                        local_files_only=True, trust_remote_code=False)
        self.model = model
        self.model.max_seq_length = MAX_SEQ_LENGTH
        self.dimension = model.get_embedding_dimension()
        self.corpus_sha256 = corpus_fingerprint(documents)
        passages = ["passage: " + normalize_text(d["text"]) for d in documents]
        lengths = self.model.tokenizer(passages, truncation=False, padding=False,
                                       return_length=True, verbose=False)["length"]
        self.truncated_count = sum(n > MAX_SEQ_LENGTH for n in lengths)
        # Custom injected encoders are for unit tests; never share production cache.
        from importlib.metadata import version
        self.cache_config = {
            "model": MODEL_NAME, "revision": MODEL_REVISION,
            "corpus": self.corpus_sha256, "max_seq_length": MAX_SEQ_LENGTH,
            "prefix": "passage: ", "normalize": True, "dimension": self.dimension,
            "device": self.device, "sentence_transformers": version("sentence-transformers"),
            "torch": version("torch"), "custom_encoder": supplied_model,
        }
        key = hashlib.sha256(json.dumps(self.cache_config, sort_keys=True).encode()).hexdigest()
        cache_root = Path(cache_dir) if cache_dir else ROOT / ".cache" / "index"
        cache_root.mkdir(parents=True, exist_ok=True)
        cache_path = cache_root / f"{key}.npz"
        self.cache_hit = False
        if cache_path.exists() and not supplied_model:
            try:
                with np.load(cache_path, allow_pickle=False) as saved:
                    vectors = saved["vectors"]
                    config = json.loads(str(saved["config"]))
                valid = (config == self.cache_config and
                         vectors.shape == (len(documents), self.dimension) and
                         np.isfinite(vectors).all() and
                         np.allclose(np.linalg.norm(vectors, axis=1), 1, atol=1e-4))
                if valid:
                    self.vectors = vectors
                    self.cache_hit = True
            except (OSError, ValueError, KeyError, EOFError):
                pass  # A partial/stale cache can be rebuilt from the pinned model.
        if not self.cache_hit:
            self.vectors = self._encode(passages)
            if not supplied_model:
                temporary = cache_path.with_suffix(".tmp.npz")
                np.savez_compressed(temporary, vectors=self.vectors,
                                    config=json.dumps(self.cache_config, sort_keys=True))
                temporary.replace(cache_path)
        self.setup_seconds = time.perf_counter() - started

    @property
    def metadata(self):
        return {
            "model_name": MODEL_NAME, "model_revision": MODEL_REVISION,
            "dimension": self.dimension, "max_seq_length": MAX_SEQ_LENGTH,
            "query_prefix": "query: ", "passage_prefix": "passage: ",
            "normalize_embeddings": True, "batch_size": BATCH_SIZE,
            "device": self.device, "corpus_sha256": self.corpus_sha256,
            "corpus_truncated_count": self.truncated_count,
            "cache_hit": self.cache_hit, "setup_seconds": self.setup_seconds,
        }

    def _encode(self, texts):
        values = self.model.encode(texts, batch_size=BATCH_SIZE,
                                   normalize_embeddings=True,
                                   convert_to_numpy=True, show_progress_bar=False)
        vectors = np.asarray(values, dtype=np.float32)
        if vectors.shape != (len(texts), self.dimension) or not np.isfinite(vectors).all():
            raise ValueError("The embedding model returned invalid vectors.")
        if not np.allclose(np.linalg.norm(vectors, axis=1), 1, atol=1e-4):
            raise ValueError("Expected unit-length embeddings for cosine similarity.")
        return vectors

    def search_many(self, queries, top_k=5):
        if top_k < 1:
            raise ValueError("top_k must be positive.")
        outputs = [[] for _ in queries]
        active = [(i, normalize_text(q)) for i, q in enumerate(queries)
                  if any(c.isalnum() for c in normalize_text(q))]
        if not active:
            return outputs
        embeddings = self._encode(["query: " + text for _, text in active])
        scores = embeddings @ self.vectors.T
        for (output_index, _), row in zip(active, scores):
            order = sorted(range(len(self.documents)),
                           key=lambda j: (-float(row[j]), self.documents[j]["id"]))
            outputs[output_index] = [
                {"document": self.documents[j], "score": float(row[j])}
                for j in order[:top_k]
            ]
        return outputs

    def search(self, query, top_k=5):
        return self.search_many([query], top_k)[0]
