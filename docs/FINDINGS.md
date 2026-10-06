# Evaluation report

Final test recorded on 4 October 2026. The experiment compares established retrieval methods on a Vietnamese passage-retrieval adaptation of XQuAD; E5 is used without fine-tuning.

## Main result

On 347 held-out questions against the same 240 known Vietnamese passages, multilingual E5 Small retrieved the annotated passage first for **323 questions (93.08%)**, compared with **290 (83.57%)** for TF-IDF and **270 (77.81%)** for token overlap. E5's MRR@5 was **0.9573**, compared with TF-IDF's **0.8974**.

The top-1 difference between E5 and TF-IDF is **9.51 percentage points**. On the paired queries, both succeeded on 275; E5 alone succeeded on 48; TF-IDF alone succeeded on 15; both missed top-1 on 9. Thus E5's higher aggregate result does not mean it wins every query. No significance test or broad Vietnamese retrieval claim is made.

| Method | Test Hit@1 | Test Hit@5 | Test MRR@5 | Dev Hit@1 |
| --- | ---: | ---: | ---: | ---: |
| Token overlap | 77.81% | 90.20% | 0.8267 | 76.63% |
| TF-IDF | 83.57% | 97.98% | 0.8974 | 83.87% |
| Multilingual E5 Small | 93.08% | 99.14% | 0.9573 | 89.32% |

The development results show the same aggregate order on 843 questions. The protocol and source hashes were frozen before opening test. All methods search the same 240 passages; each question has one annotated source-passage target. Hit@k counts targets found in the first k results, and MRR@5 averages reciprocal target rank with zero for a miss. See the [full test report](../results/test-summary.md), [development report](../results/dev-summary.md) and [evaluation protocol](RESEARCH-PROTOCOL.md).

## Three inspected development cases

These cases were inspected after the automatically generated [development casebook](../results/dev-error-analysis.md). They provide concrete observations and hypotheses, not a validated taxonomy of all errors.

### 1. Generic wording can outweigh the entity being asked about

Query `56beb86b3aeaaa14008c92c0`: **“John Elway hiện đang có vai trò gì trong hệ thống của Broncos?”**

TF-IDF ranks a passage about Scottish parliamentary committees first and the annotated Broncos passage second. E5 ranks the Broncos passage first. The correct passage names John Elway and states his executive/general-manager roles.

Inspection of this implementation's cosine contributions explains the lexical ranking: the Scottish passage scores approximately **0.1768**, with `trò` and `vai` contributing about **0.1097** together. The annotated passage scores approximately **0.1635**, with `elway`, `broncos` and `john` contributing about **0.1436** together. The vector weighting still rewards generic “role/system” wording enough to put the wrong topic first.

This is evidence of one lexical scoring failure. E5's successful ranking is observed; its internal causal reason has not been established.

### 2. The right topic and entity can still be the wrong fact

Query `56beca913aeaaa14008c946f`: **“Hậu vệ Panther nào phạm lỗi giữ người ở lượt chơi thứ ba?”**

TF-IDF ranks the annotated passage first. E5 puts it second, behind a passage describing Panthers defenders and season statistics. Both passages mention Josh Norman, but the annotated passage describes the specific holding penalty and the sequence of plays; the first semantic result discusses his general performance.

The observed error is **fact-level discrimination within the same topic**, rather than a completely unrelated subject. A hypothesis is that one pooled passage vector does not sufficiently distinguish this event from general player information. This explanation is unvalidated; no reranker or controlled ablation was evaluated.

### 3. A single gold label can penalize a plausible relevant passage

Query `56e1b62ecd28a01900c67aa4`: **“Lý thuyết độ phức tạp phân loại các vấn đề dựa trên thuộc tính chính nào?”**

TF-IDF and E5 both rank an introductory complexity-theory passage first. That passage explicitly says computational problems are classified by their intrinsic difficulty. The annotated source passage also discusses classification by difficulty, but appears at rank 3 for TF-IDF and rank 2 for E5.

By this project's one-gold metric, both top-1 results count as wrong. Manual reading suggests their first result is also relevant. This is a **label-coverage limitation**, not proof that both retrievers misunderstood the question. A broader relevance assessment would require additional human judgments and a revised evaluation design.

## Engineering and evidence limits

- E5 is an existing pretrained model, used without fine-tuning. The experiment compares representations; it does not introduce a new model.
- Three of the 240 passages exceed 512 model tokens and are truncated. No chunking or truncation ablation was performed.
- Data comes from a small translated question-answering collection. The adapted task retrieves source passages rather than extracting answer spans.
- Test questions are unseen during development, but the full passage collection is known to every index. This does not measure a new corpus or an open-domain search engine.
- Model pretraining overlap cannot be ruled out. Similarity scores are not confidence estimates, and the demo can return irrelevant text for out-of-corpus questions.
- Batch throughput and live request time are different measurements. Runtime information is recorded in the generated reports; no portable speed superiority is claimed.

Dataset attribution: XQuAD, Mikel Artetxe, Sebastian Ruder and Dani Yogatama (2019), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). The questions and described source passages above are dataset-derived material; the passage-retrieval adaptation and analysis are specific to this project.
