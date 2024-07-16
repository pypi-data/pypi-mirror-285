from openai import OpenAI
import json
import eenhoorntje_llm_lib.llm_cache

def clear_cache():
    eenhoorntje_llm_lib.llm_cache.cache.clear()

def call_llm(messages, model="anthropic/claude-3-haiku", temperature=0.0, max_tokens=500, json_output=False):
    api_key = json.load(open("keys.json", "r", encoding="utf-8"))["OPEN_ROUTER_API_KEY"]
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    cache_key = None
    if temperature == 0.0:
        cache_key = model + "\n" + json.dumps(messages, ensure_ascii=False, indent=4) + "\nMax tokens: " + str(
            max_tokens)
        output = eenhoorntje_llm_lib.llm_cache.cache.query(cache_key)
        if output:
            return output

    for i in range(10):
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            if completion.choices is None:
                return None

            res = completion.choices[0].message.content

            if cache_key:
                eenhoorntje_llm_lib.llm_cache.cache.add(cache_key, res)
            return res
        except Exception as e:
            print(e)
            print(f"Retrying in {2 ** i} seconds...")

    return ""
