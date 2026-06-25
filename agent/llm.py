from langchain_community.chat_models import ChatLlamaCpp


def get_llm():
    return ChatLlamaCpp(
        model_path="./models/qwen/qwen2.5-7b-instruct-q3_k_m.gguf",
        temperature=0.2,
        max_tokens=512,
        n_ctx=4096,
        n_gpu_layers=-1,
        verbose=True
    )