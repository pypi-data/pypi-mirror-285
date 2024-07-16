import eenhoorntje_llm_lib.llm_cache
import eenhoorntje_llm_lib.utils
import json
import requests


def call_api(sentence: str, source_lang: str, target_lang: str) -> str:
    auth_key = eenhoorntje_llm_lib.utils.get_key("YANDEX_API_KEY")
    url = "https://translate.api.cloud.yandex.net/translate/v2/translate"
    headers = {
        "Authorization": f"Api-Key {auth_key}"
    }
    body = {
        "sourceLanguageCode": source_lang,
        "targetLanguageCode": target_lang,
        "texts": [
            sentence
        ],
        "speller": False
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code == 200:
        response_data = response.json()
        return response_data["translations"][0]["text"]
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

    return f"YandexTranslate doesn't support the language pair {source_lang} -> {target_lang}"


def translate_with_yandex(sentence: str, source_lang: str, target_lang: str) -> str:
    cache_key = "YandexTranslate" + "\n"
    cache_key += "Source: " + sentence + "\n"
    cache_key += "Source lang: " + source_lang + "\n"
    cache_key += "Target lang: " + target_lang
    output = eenhoorntje_llm_lib.llm_cache.cache.query(cache_key)
    if output:
        return output

    res = call_api(sentence, source_lang, target_lang)
    eenhoorntje_llm_lib.llm_cache.cache.add(cache_key, res)
    return res
