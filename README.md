# Passage

A local search demo for Vietnamese passages. It compares token overlap, TF-IDF and a pretrained multilingual E5 encoder on a small retrieval benchmark adapted from XQuAD.

An NLP learning project focused on retrieval methods and evaluation. The app retrieves text from its collection; it does not generate answers or search the web.

![Search interface](docs/assets/passage.jpg)

## Quick start

Use Python 3.12 or 3.13. Python 3.12 is recommended. Initial setup needs an internet connection and several gigabytes of free disk space for dependencies and the model. Search runs locally after setup, without an API key.

On macOS:

```bash
git clone https://github.com/phanminhhuy1810/passage.git
cd passage
bash setup.sh
bash "Open Retrieval Lab.command"
```

The launcher opens [localhost:8765](http://127.0.0.1:8765). Keep its Terminal open and press Ctrl+C there to stop the server. You can also double-click `Open Retrieval Lab.command` after setup.

For terminal use on macOS or Linux:

```bash
.venv/bin/python server.py --host 127.0.0.1 --port 8765
```

To search without the browser, run one of these commands from a separate Terminal:

```bash
.venv/bin/python search.py 'Norman là ai?' --method overlap --top-k 3
.venv/bin/python search.py 'Norman là ai?' --method tfidf --top-k 3
.venv/bin/python search.py 'Norman là ai?' --method semantic --top-k 3
```

Setup creates a project-local `.venv`, downloads the dataset and prepares the pinned E5 model. To select an existing Python interpreter, use `PYTHON_BIN=/path/to/python3.12 bash setup.sh`.

For Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements-lock.txt
.venv\Scripts\python dataset.py
.venv\Scripts\python setup_model.py
.venv\Scripts\python server.py --host 127.0.0.1 --port 8765
```

The recorded setup verification was on macOS. Windows uses the same Python entry points but has not been verified here.

## Search methods

| Method | How it ranks passages |
| --- | --- |
| Token overlap | Counts distinct query tokens shared with each passage |
| TF-IDF | Weights rarer tokens more strongly and compares normalized vectors with cosine similarity |
| Multilingual E5 Small | Encodes queries and passages into normalized 384-dimensional vectors and compares them with cosine similarity |

The lexical methods use lowercase Unicode alphanumeric tokens, roughly Vietnamese syllables rather than fully segmented words. E5 uses its own tokenizer, the `query:` and `passage:` prefixes, and a 512-token input limit. The encoder is used for inference without fine-tuning.

In the browser, **Compare methods** shows the ranked lists together. **Read passage** opens the full text. Similarity scores have different scales across methods and are not probabilities.

## Dataset and results

The collection contains **240 passages** and **1,190 questions** from Vietnamese [XQuAD](https://github.com/google-deepmind/xquad). Identical passages are deduplicated. Questions are split by passage group with seed 42: **843 development questions** and **347 test questions**. All 240 passages remain candidates in both splits.

Each question's annotated source paragraph is treated as its relevant retrieval target. This is a passage-retrieval adaptation of XQuAD, not its original question-answering benchmark.

Recorded test results:

| Method | Hit@1 | Hit@5 | MRR@5 |
| --- | ---: | ---: | ---: |
| Token overlap | 77.81% | 90.20% | 0.8267 |
| TF-IDF | 83.57% | 97.98% | 0.8974 |
| Multilingual E5 Small | 93.08% | 99.14% | 0.9573 |

Hit@k measures how often the source paragraph appears in the first k results. MRR@5 averages the reciprocal rank, using zero when the source paragraph is outside the first five.

See the [test report](results/test-summary.md), [development report](results/dev-summary.md), [error analysis](results/dev-error-analysis.md) and [findings](docs/FINDINGS.md). The small, known collection limits how far these results generalize. Other relevant passages may receive no credit, and model exposure to the benchmark during pretraining cannot be ruled out.

## Reproduce the experiment

After setup:

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python evaluate.py --split dev
.venv/bin/python evaluate.py --split test --final-test
```

The dataset revision, model revision, split and frozen implementation are recorded in [the protocol](docs/RESEARCH-PROTOCOL.md) and `results/protocol.json`. The final command reproduces that recorded run. Changes made after seeing the test results need a new evaluation design; the existing test is no longer unseen.

## Code and learning notes

| Path | Purpose |
| --- | --- |
| `dataset.py` | Dataset preparation and splitting |
| `retrieval.py`, `semantic.py`, `engine.py` | Retrieval methods and shared search interface |
| `search.py`, `server.py`, `web/` | Command-line and browser demo |
| `evaluate.py`, `freeze_protocol.py`, `results/` | Evaluation and recorded evidence |
| `lessons/`, `docs/` | Small examples, Vietnamese learning notes and research documentation |
| `tests/` | Retrieval, metric, server and integrity checks |

For learning in Vietnamese, start with [PROJECT-MAP.md](docs/PROJECT-MAP.md) and [HOC-TIEP.md](docs/HOC-TIEP.md). See [CONTRIBUTIONS.md](docs/CONTRIBUTIONS.md) for the development and learning log.

## Troubleshooting

- Unsupported Python: choose Python 3.12–3.13 and rerun setup. The script does not install Python itself.
- Incomplete dataset or model download: check the setup error and rerun `bash setup.sh`.
- Port conflict: stop your existing server, or use `server.py --port 8766` and open that address manually.
- Browser did not open: keep the server running and open its printed local URL.

## Credits and license

The dataset is [XQuAD](https://github.com/google-deepmind/xquad), by Mikel Artetxe, Sebastian Ruder and Dani Yogatama ([paper](https://arxiv.org/abs/1910.11856)). The semantic encoder is [intfloat/multilingual-e5-small](https://huggingface.co/intfloat/multilingual-e5-small).

Original code and documentation use the [MIT license](LICENSE). XQuAD-derived content uses CC BY-SA 4.0. Model and library licenses are listed separately in [THIRD_PARTY.md](THIRD_PARTY.md).
