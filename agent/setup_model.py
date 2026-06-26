from ollama import Client

MODEL_NAME = 'qwen2.5:7b-instruct'

def download_model(host : str = "http://localhost:11434") -> bool:
    
    client = Client(host = host)

    try:
        local_models = client.list()

    except Exception as e:
        print(f"Could not reach Ollama server at {host} : {e}")
        return False

    existing_names = {m.model for m in local_models.models}

    if MODEL_NAME in existing_names:
        return True

    print(f"Downloading model '{MODEL_NAME}' via Ollama ...")

    try:
        last_status = None
        for chunk in client.pull(MODEL_NAME, stream=True):
            status = chunk.get("status") if isinstance(chunk, dict) else chunk.status
            if status != last_status:
                print(f" {status}")
                last_status = status

        print('Model download complete.')

        return True

    except Exception as e:
        print(f"Model download failed : {e}")
        return False


if __name__ == '__main__':
    download_model()