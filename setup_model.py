"""Download one pinned model snapshot, then prepare the local passage index."""

from huggingface_hub import snapshot_download
from dataset import load_dataset
from semantic import MODEL_NAME, MODEL_REVISION, MODEL_DIR, SemanticRetriever


def main():
    print(f"Downloading {MODEL_NAME} at {MODEL_REVISION} (first setup only).", flush=True)
    snapshot_download(
        MODEL_NAME, revision=MODEL_REVISION, local_dir=MODEL_DIR,
        allow_patterns=["*.json", "model.safetensors", "sentencepiece.bpe.model", "README.md"],
        ignore_patterns=["onnx/*", "openvino/*", ".eval_results/*"],
    )
    print("Building the passage index...", flush=True)
    retriever = SemanticRetriever(load_dataset()["documents"])
    print(f"Ready: {len(retriever.documents)} passages, {retriever.dimension} dimensions.")
    print(f"Passages longer than 512 tokens: {retriever.truncated_count}")


if __name__ == "__main__":
    main()
