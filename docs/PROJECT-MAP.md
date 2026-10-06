# System architecture

Passage ranks Vietnamese passages from a fixed local collection. The browser demo and command-line interface expose three retrieval methods through a shared search engine. Each result includes the original passage, its title and a method-specific score.

## Components

| Component | Responsibility |
| --- | --- |
| `dataset.py` | Downloads the pinned Vietnamese XQuAD data, normalizes and deduplicates passages, assigns source-passage labels and splits question groups. |
| `retrieval.py` | Implements distinct-token overlap and TF-IDF cosine retrieval. |
| `semantic.py` | Loads the pinned pretrained multilingual E5 Small model, creates normalized embeddings and caches the passage vectors. |
| `engine.py` | Routes a query to the requested retrieval method through `SearchEngine`. |
| `search.py` | Provides command-line search. |
| `server.py`, `web/` | Serve the local search interface and passage text. |
| `evaluate.py` | Measures Hit@1, Hit@5 and MRR@5, records runtime metadata and writes evaluation reports. |
| `freeze_protocol.py` | Records and verifies the source, dataset and model configuration for final-test evaluation. |
| `tests/` | Checks retrieval behavior, metric calculations, server behavior and protocol integrity. |

## Search flow

```text
Browser interface or search.py
             |
             v
      engine.py / SearchEngine
             |
             +-- retrieval.py: overlap or TF-IDF
             |
             +-- semantic.py: E5 query embedding
             |
             v
 Score candidate passages and order by score
             |
             v
     Return the first k passages
```

The dataset is prepared before search. All methods index the same 240 passages. E5 encodes passages during initialization or loads compatible cached vectors; each new query is encoded and compared with those vectors. Search runs locally after dependencies, dataset and model have been downloaded.

## Retrieval representations

| Method | Representation and scoring | Constraints |
| --- | --- | --- |
| Token overlap | Number of distinct tokens shared by query and passage. | Matches lexical form; ignores token order and frequency. |
| TF-IDF | Raw term counts multiplied by smoothed IDF, then L2-normalized; scores are vector dot products. | Depends on shared tokens and corpus-derived weights. |
| Multilingual E5 Small | Normalized 384-dimensional embeddings with `query: ` and `passage: ` prefixes; scores are cosine similarities. | Inputs are truncated at 512 model tokens; the pretrained model is used without fine-tuning. |

Lexical tokenization applies NFC normalization, lowercase conversion and Unicode alphanumeric matching. In Vietnamese, this produces mostly syllable tokens rather than linguistically segmented words. E5 uses its own tokenizer.

Equal scores are ordered by stable passage ID. Lexical methods return positive-score passages only; semantic retrieval ranks candidates without a score threshold. Similarity scores differ across methods and are not calibrated probabilities of relevance.

## Evaluation data flow

Each XQuAD question is associated with its annotated source paragraph. Passage normalization and deduplication produce 240 retrieval candidates from 1,190 questions. Question groups are split by source paragraph using seed 42: 843 development questions and 347 test questions. All 240 passages remain candidates in both splits.

`evaluate.py` ranks candidates for each question and checks the source paragraph's rank in the first five. Query labels are used for evaluation; they are not used to fit the retrievers. Corpus-derived IDF and passage embeddings use the known candidate collection.

`freeze_protocol.py` records the fixed configuration and input hashes in `results/protocol.json`. Final-test evaluation verifies that snapshot before search. The recorded test concerns unseen questions about a known collection; it does not establish generalization to a new corpus. After test outcomes have been inspected, further method selection requires a new evaluation design.

Setup and search commands are in the [README](../README.md). The [evaluation protocol](RESEARCH-PROTOCOL.md) documents the fixed methods, metrics and reproduction procedure; the [evaluation report](FINDINGS.md) interprets the recorded results and inspected development cases.
