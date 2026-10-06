# DEV evaluation — Vietnamese passage retrieval

Collection: **240 passages**. Evaluation: **843 dev questions**.

| Method | Hit@1 | Hit@5 | MRR@5 | Batch ms/query* |
|---|---:|---:|---:|---:|
| overlap | 0.7663 | 0.9300 | 0.8336 | 0.19 |
| tfidf | 0.8387 | 0.9763 | 0.8981 | 0.31 |
| semantic | 0.8932 | 0.9834 | 0.9304 | 1.87 |

*Timing is amortized batch/sequential throughput on this machine, not per-request interactive latency. The model/index is warmed with a development query before evaluation; engine setup and warm-up are reported separately. The methods use different execution strategies, so timing is descriptive and not a controlled speed comparison.

TF-IDF / semantic top-1 outcomes: both correct **661**; TF-IDF only **46**; semantic only **92**; both incorrect **44**. No significance test is claimed.

## Protocol

This is a [XQuAD](https://github.com/google-deepmind/xquad) adaptation to **closed-corpus passage retrieval**, not the official extractive QA task. Its scores must not be compared with XQuAD QA EM/F1.

All 240 passages are available to indexing. Questions are split 70/30 by source paragraph using seed 42; questions about a paragraph stay in the same split. Query labels are not used to train or fit the retrievers. This measures unseen questions about a known collection, not generalization to an unseen collection.

Hit@1 is the fraction with the annotated passage ranked first. Hit@5 is the fraction found in the top five. MRR@5 averages reciprocal gold rank, with zero for a miss. There is one annotated relevant passage per query.

These development results may be inspected to debug the pipeline; they are not untouched final evidence.

## Model and runtime

```json
{
  "model_name": "intfloat/multilingual-e5-small",
  "model_revision": "614241f622f53c4eeff9890bdc4f31cfecc418b3",
  "dimension": 384,
  "max_seq_length": 512,
  "query_prefix": "query: ",
  "passage_prefix": "passage: ",
  "normalize_embeddings": true,
  "batch_size": 16,
  "device": "cpu",
  "corpus_sha256": "90d521b261c4f26d0bfcefda98f1e4c1d0cc7c2792461ed0d2c178b78bf39026",
  "corpus_truncated_count": 3,
  "cache_hit": true,
  "setup_seconds": 4.848586250001972
}
```

Engine initialization: 4.89 s. Warm-up across three methods: 0.13 s.

## Limitations

- Small, translated, QA-derived collection; not the official XQuAD QA benchmark or a broad Vietnamese search benchmark.
- Only the original source paragraph is labeled relevant; other relevant passages may be scored as wrong.
- The full candidate corpus is shared by dev and test. This is unseen-query evaluation on a known corpus.
- Lexical tokenization uses Unicode-normalized syllables, not Vietnamese word segmentation.
- The pretrained semantic model is used without task-specific fine-tuning. Pretraining overlap with this benchmark cannot be ruled out.
- The model truncates long inputs at its configured token limit; inspect corpus_truncated_count in model metadata.
- No paraphrase, out-of-domain, no-answer, large-corpus or statistical-significance experiment has been completed.
- Batch throughput depends on hardware, caches and batch strategy and is not interactive request latency.

## Reproduction

- Dataset revision: `7d30520c717524000f0d9d2f9c10a069acd9d285`.
- Raw dataset SHA-256: `f619a1eb11fb42d3ab0834259e488a65f585447ef6154437bfb7199d85161a04`.
- Evaluation source SHA-256: `73e76488987a07a18ee605fc05d01974c80ff878021449767ba18e7e45b20de5`.
- Python: `3.12.14`; device and model revision are above.
- Protocol SHA-256: `not frozen (development)`.
- Detailed per-query ranks remain local in `results/dev.json`; compact metrics are in `results/dev-metrics.json`.
- See [the research protocol](../docs/RESEARCH-PROTOCOL.md) for freeze and final-test commands.

Implementation and experiments were completed with AI assistance.

Dataset attribution: XQuAD — Artetxe, Ruder & Yogatama (2019), CC BY-SA 4.0. Passage grouping, retrieval adaptation and evaluation are specific to this project.
