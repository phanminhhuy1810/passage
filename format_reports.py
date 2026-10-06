"""Remove tutorial boilerplate from Markdown reports without rerunning evaluation.

Only presentation changes: JSON results, data and frozen sources are untouched.
"""

from pathlib import Path


PERSONAL_CLAIM = (
    " These measurements describe the system; "
    "they do not establish the student's independent implementation or mastery."
)
REVIEW_PROMPTS = (
    "Review prompts: Does the top passage contain the requested fact? Which query words "
    "or related meanings appear in each passage? Could an unlabeled passage also be relevant? "
    "For long passages, check whether the relevant evidence falls beyond the model's token limit."
)
REPORTS = ("dev-summary.md", "test-summary.md", "dev-error-analysis.md")


def format_markdown(text):
    """Remove only the frozen evaluator's exact nontechnical boilerplate."""
    return text.replace(PERSONAL_CLAIM, "").replace("\n" + REVIEW_PROMPTS + "\n", "")


def main():
    results = Path(__file__).resolve().parent / "results"
    for name in REPORTS:
        path = results / name
        if not path.is_file():
            continue
        before = path.read_text(encoding="utf-8")
        after = format_markdown(before)
        if after != before:
            path.write_text(after, encoding="utf-8")
            print(f"Formatted {path.relative_to(results.parent)}")


if __name__ == "__main__":
    main()
