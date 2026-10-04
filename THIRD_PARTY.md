# Data, model and dependency notices

The [MIT license](LICENSE) covers this repository's original code and documentation. It does not replace the licenses of datasets, pretrained weights or installed libraries.

## XQuAD Vietnamese

- Authors: Mikel Artetxe, Sebastian Ruder and Dani Yogatama.
- Source: [Google DeepMind XQuAD](https://github.com/google-deepmind/xquad).
- Paper: [On the Cross-lingual Transferability of Monolingual Representations](https://arxiv.org/abs/1910.11856).
- Pinned source revision: `7d30520c717524000f0d9d2f9c10a069acd9d285`.
- License: [Creative Commons Attribution-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/).
- `dataset.py` downloads `xquad.vi.json` and the upstream `CC-BY-SA4.0.txt`. Local dataset files are excluded from Git.
- Adaptation: passage text is normalized to Unicode NFC, duplicate passages are merged by content hash, questions receive source-passage IDs, and question groups are split by paragraph with seed 42. The text is used for passage retrieval instead of extractive answer prediction.
- Dataset-derived passages and question excerpts retain the source attribution and CC BY-SA 4.0 terms, including when displayed in the local demo or quoted in an error analysis. Any distributed adapted dataset must retain those terms and identify changes.

## Multilingual E5 Small

- Model: [`intfloat/multilingual-e5-small`](https://huggingface.co/intfloat/multilingual-e5-small).
- Source revision: `614241f622f53c4eeff9890bdc4f31cfecc418b3`.
- Model card declares the MIT license; the download retains the model's source metadata. The weights are downloaded locally and are not committed to this repository.
- The pretrained model is used for inference. This project does not claim authorship of the model or train/fine-tune it.
- See the upstream [E5 project](https://github.com/microsoft/unilm/tree/master/e5) for model background and attribution.

## Python libraries

Dependencies are installed into `.venv` from `requirements-lock.txt`; their source code and weights are not vendored in this repository. Each dependency retains its own license. The lock file records the resolved versions used for the recorded run; consult the installed distribution metadata for the corresponding license notices.
