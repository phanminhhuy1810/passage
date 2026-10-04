# TEST evaluation — Vietnamese passage retrieval

Collection: **240 passages**. Evaluation: **347 test questions**.

| Method | Hit@1 | Hit@5 | MRR@5 | Batch ms/query* |
|---|---:|---:|---:|---:|
| overlap | 0.7781 | 0.9020 | 0.8267 | 0.19 |
| tfidf | 0.8357 | 0.9798 | 0.8974 | 0.30 |
| semantic | 0.9308 | 0.9914 | 0.9573 | 1.77 |

*Timing is amortized batch/sequential throughput on this machine, not per-request interactive latency. The model/index is warmed with a development query before evaluation; engine setup and warm-up are reported separately. The methods use different execution strategies, so timing is descriptive and not a controlled speed comparison.

TF-IDF / semantic top-1 outcomes: both correct **275**; TF-IDF only **15**; semantic only **48**; both incorrect **9**. No significance test is claimed.

## Protocol

This is a [XQuAD](https://github.com/google-deepmind/xquad) adaptation to **closed-corpus passage retrieval**, not the official extractive QA task. Its scores must not be compared with XQuAD QA EM/F1.

All 240 passages are available to indexing. Questions are split 70/30 by source paragraph using seed 42; questions about a paragraph stay in the same split. Query labels are not used to train or fit the retrievers. This measures unseen questions about a known collection, not generalization to an unseen collection.

Hit@1 is the fraction with the annotated passage ranked first. Hit@5 is the fraction found in the top five. MRR@5 averages reciprocal gold rank, with zero for a miss. There is one annotated relevant passage per query.

The protocol, source hashes, data hashes and model configuration were frozen before this final evaluation.

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
  "setup_seconds": 3.7779630000004545
}
```

Engine initialization: 3.82 s. Warm-up across three methods: 0.02 s.

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
- Protocol SHA-256: `a9c3c2bcd4e0791c138f9193bd444848814377fc5d0a494ea836620ca754d203`.
- Detailed per-query ranks remain local in `results/test.json`; compact metrics are in `results/test-metrics.json`.
- See [the research protocol](../docs/RESEARCH-PROTOCOL.md) for freeze and final-test commands.

Implementation and experiments were completed with AI assistance. These measurements describe the system; they do not establish the student's independent implementation or mastery.

Dataset attribution: XQuAD — Artetxe, Ruder & Yogatama (2019), CC BY-SA 4.0. Passage grouping, retrieval adaptation and evaluation are specific to this project.
