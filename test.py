from openai import OpenAI
import httpx
client = OpenAI(http_client=httpx.Client(timeout=15.0, http2=False))

try:
    client.chat.completions.create(
        model="gpt-5",  # 刻意用不存在的
        messages=[{"role": "user", "content": "ping"}],
        max_tokens=5,
    )
except Exception as e:
    print("EXPECTED ERROR:", type(e).__name__, str(e)[:200])