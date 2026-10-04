# Development and learning log

## Development — 4 October 2026

**Phan Minh Huy:** selected NLP and passage retrieval as the exploration direction, provided the project context, reviewed the demo and requested the Passage interface revision.

**Codex assistance:** authored the retrieval implementations, dataset preparation, semantic-model integration, local server, frontend, setup workflow, tests and documentation. Codex also ran the recorded development and final-test evaluations and inspected the development error cases.

The semantic encoder is the upstream pretrained `intfloat/multilingual-e5-small` model. This project uses it for inference, without training or fine-tuning it.

The exact experiment configuration and measured results are recorded in [RESEARCH-PROTOCOL.md](RESEARCH-PROTOCOL.md), [FINDINGS.md](FINDINGS.md) and `results/`.

## Learning progress — 4 October 2026

- Phan Minh Huy reported understanding token sets, overlap scoring and deterministic ranking after the introductory explanation.
- After receiving run instructions, he reported completing the guided `lessons/01_overlap.py` example. The example was written with Codex assistance.
- Independent implementation of the full retrievers and reproduction of the full evaluation remain learning goals; they are not recorded as completed student contributions.

The next practical steps are listed in [HOC-TIEP.md](HOC-TIEP.md). Add entries when a specific reading, run, code change or experiment has actually been completed.

## Entry template

```text
Date:
What I personally read / ran / changed:
Why I did it:
Observed result or output:
AI assistance used:
What I can now explain:
Remaining question:
```
