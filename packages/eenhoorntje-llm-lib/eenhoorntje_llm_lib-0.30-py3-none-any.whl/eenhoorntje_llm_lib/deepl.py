import json
import requests
import eenhoorntje_llm_lib.llm_cache
import eenhoorntje_llm_lib.utils

def translate_with_deepl(sentence: str, source_lang: str, target_lang: str, handle_tags=False,
                         formality="default") -> str:
    cache_key = "DeepL" + "\n"
    cache_key += "Source: " + sentence + "\n"
    cache_key += "Source lang: " + source_lang + "\n"
    cache_key += "Target lang: " + target_lang + "\n"
    cache_key += "Tags: " + str(handle_tags) + "\n"
    cache_key += "Formality: " + formality + "\n"
    output = eenhoorntje_llm_lib.llm_cache.cache.query(cache_key)
    if output:
        return output

    url = "https://api.deepl.com/v2/translate"
    auth_key = eenhoorntje_llm_lib.utils.get_key("DEEPL_API_KEY")

    headers = {
        "Authorization": f"DeepL-Auth-Key {auth_key}",
        "User-Agent": "YourApp/1.2.3",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    if handle_tags:
        data = {
            "text": sentence,
            "target_lang": target_lang,
            "source_lang": source_lang,
            "tag_handling": "html",
            "formality": formality
        }
    else:
        data = {
            "text": sentence,
            "target_lang": target_lang,
            "source_lang": source_lang,
            "formality": formality
        }

    response = requests.post(url, headers=headers, data=data)
    res = response.json()["translations"][0]["text"]
    res = res.replace("&lt;", "<").replace("&gt;", ">")
    eenhoorntje_llm_lib.llm_cache.cache.add(cache_key, res)
    return res
