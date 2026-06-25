from huggingface_hub import hf_hub_download
from pathlib import Path


MODEL_REPO = "Qwen/Qwen2.5-7B-Instruct-GGUF"
MODEL_FILE = "qwen2.5-7b-instruct-q3_k_m.gguf"


def download_model():
    model_dir = Path("models/qwen")
    model_dir.mkdir(parents=True, exist_ok=True)

    model_path = model_dir / MODEL_FILE

    if model_path.exists():
        print("Model already exists.")
        return True

    print("Downloading model...")

    try:
        hf_hub_download(
            repo_id=MODEL_REPO,
            filename=MODEL_FILE,
            local_dir=model_dir
        )

        print("Model download complete.")
        return True

    except Exception as e:
        print(f"Model download failed: {str(e)}")
        return False