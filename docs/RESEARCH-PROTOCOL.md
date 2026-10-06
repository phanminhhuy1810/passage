# Research protocol

## Question and scope

On a small Vietnamese passage collection, how do distinct-token overlap, TF-IDF cosine similarity and a pretrained multilingual embedding retriever differ in their ability to rank the annotated source paragraph of a question?

The experiment compares established retrieval methods and supports a working search demo. Its metrics measure source-passage ranking on an adapted XQuAD collection. E5 is used for inference without fine-tuning; the project introduces no new retrieval model, and these scores are distinct from the official XQuAD extractive-QA results.

## Dataset and split

- Source: [XQuAD](https://github.com/google-deepmind/xquad), Artetxe, Ruder & Yogatama (2019), Vietnamese version, CC BY-SA 4.0.
- Upstream revision: `7d30520c717524000f0d9d2f9c10a069acd9d285`; `dataset.py` saves and verifies the raw file hash.
- Adaptation: normalize source paragraphs to NFC and deduplicate by text hash. There are 240 candidate passages and 1,190 questions.
- Split: sort paragraph IDs by the SHA-256 of `42:<paragraph_id>`; the first 70% of paragraphs supply development questions and the remainder supply test questions. Every question about the same paragraph stays in the same split: 843 dev questions and 347 test questions.
- The **entire passage collection** is indexed for both splits. The test concerns unseen questions about a known collection, not an unseen collection. Corpus-derived IDF and passage embeddings are therefore permitted; query relevance labels are never used to fit a retriever.
- There is one annotated relevant passage per question. Other genuinely relevant passages can be counted as wrong because they lack labels.
- Dataset text and the original license are downloaded locally. Results and excerpts must retain XQuAD attribution and license information.

## Fixed methods

1. **Token overlap:** NFC-normalized lowercase Unicode tokens; score is the number of distinct query tokens also present in a passage. For Vietnamese, these tokens are mostly syllables, not linguistically segmented words.
2. **TF-IDF cosine:** raw token frequency times `log((1 + N) / (1 + df)) + 1`; L2-normalized query and passage vectors, scored by dot product. IDF is fitted to the known passage collection only.
3. **Semantic retrieval:** the pretrained `intfloat/multilingual-e5-small` model at revision `614241f622f53c4eeff9890bdc4f31cfecc418b3`. Prefix questions with `query: ` and passages with `passage: `, including Vietnamese inputs; normalize the resulting 384-dimensional embeddings and rank all passages by cosine similarity. Inputs are truncated to 512 model tokens. No task-specific fine-tuning is performed.

Model source: [multilingual-e5-small model card](https://huggingface.co/intfloat/multilingual-e5-small/tree/614241f622f53c4eeff9890bdc4f31cfecc418b3). Model configuration and the number of truncated corpus passages are recorded in evaluation artifacts. The semantic model may have seen overlapping data in pretraining; an uncontaminated benchmark cannot be asserted.

For deterministic tie handling, equal scores are ordered by stable document ID. Lexical methods return positive-score passages only; the semantic method ranks every passage without a score threshold. These choices are fixed before test. A cosine score is a similarity, not a calibrated probability of relevance.

## Measurements

With one annotated relevant passage, for each query let `r` be its rank among the first five results, if present:

- **Hit@1:** mean of `1[r = 1]`.
- **Hit@5:** mean of `1[r exists]`.
- **MRR@5:** mean of `1/r` for a hit and zero for a miss.

Every query is included in each denominator, including queries returning no lexical results. Report all three methods, including results that disagree with the initial expectation. Paired top-1 counts show how often TF-IDF and semantic retrieval each succeed on the same questions; these counts are descriptive, without a significance claim.

The evaluator also records initialization time and throughput. It warms every method using a **development** question, even during the test run. Semantic query embeddings are encoded in batches. `throughput_ms_per_query` is total search time divided by question count and is **not interactive latency**; hardware, caches and batch strategy affect it. Model/index construction and warm-up are outside the search timer and reported separately. The demo measures its own request time.

## Development, freeze and test

Run these from the repository with its environment active:

```sh
python dataset.py
python -m unittest discover -s tests -v
python evaluate.py --split dev
python format_reports.py
```

Read `results/dev-summary.md` and `results/dev-error-analysis.md`, inspect data and debug the implementation. Development examples can be used in the demo. Do not select or tune methods using test query outcomes.

After all retrieval and evaluation code is final:

```sh
python freeze_protocol.py
python evaluate.py --split test --final-test
python format_reports.py
```

`freeze_protocol.py` records the method set, cutoff, model configuration, source hashes, full processed dataset hash, upstream metadata, split counts and freeze timestamp in `results/protocol.json`. The evaluator checks that snapshot before running test and checks model configuration after constructing the engine. Different devices or cache state do not invalidate the protocol; those runtime details remain visible in the report. Numerical differences across hardware/library versions may still occur.

The freeze command refuses to replace a protocol when final-test result files already exist. `--replace` is available only while still developing and before final test. A final run can be reproduced with the same frozen inputs; it must not become a tuning loop. If the source changes after final test, the old protocol and results remain evidence only for the old implementation. Establish a new evaluation design instead of relabeling the previously inspected test as untouched.

Artifacts:

- `results/dev-metrics.json` and `results/test-metrics.json`: compact, portable metrics and provenance.
- `results/dev-summary.md` and `results/test-summary.md`: readable tables and limitations.
- `results/dev.json` and `results/test.json`: local detailed query ranks.
- `results/dev-error-analysis.md`: deterministic development casebook, up to two examples in each of three disagreement/error categories. Its rank observations do not constitute a validated causal error taxonomy.
- `results/protocol.json`: the frozen protocol used by final evaluation.

## Limits of the evidence

The corpus is small and translated from an English QA collection. Results do not establish general quality on Vietnamese web search, paraphrases, out-of-domain inputs, questions with no answer, or larger collections. Shared pretraining data cannot be ruled out. Truncation can remove evidence from long passages. No confidence intervals or statistical significance tests are reported. The benchmark evaluates passage ranking, not answer generation or hallucination reduction.

The benchmark describes the behavior of the implemented system under the configuration recorded in `results/protocol.json`.
