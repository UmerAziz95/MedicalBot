"""
Token counting utility for prompts and responses
"""

def count_tokens(text: str, model_name: str = "gpt-3.5-turbo") -> int:
    try:
        import tiktoken
        enc = tiktoken.encoding_for_model(model_name)
        return len(enc.encode(text))
    except Exception:
        # Fallback: use simple whitespace splitting
        return len(text.split())

# For output, you can also call this function with response text and model