import os
import anthropic

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def send_chat_request(prompt: str) -> str:
    try:
        completion = anthropic_client.completions.create(
            model="claude-2",
            prompt=f"{anthropic.HUMAN_PROMPT} {prompt}{anthropic.AI_PROMPT}",
            max_tokens_to_sample=300,
        )
        return completion.completion
    except Exception as e:
        raise ValueError(f"Anthropic API request failed: {str(e)}")
