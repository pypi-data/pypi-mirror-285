import eenhoorntje_llm_lib.llm_cache
import eenhoorntje_llm_lib.utils
from google.cloud import translate_v2 as translate


def translate_with_google(sentence: str, source_lang: str, target_lang: str) -> str:
    cache_key = "GoogleTranslate" + "\n"
    cache_key += "Source: " + sentence + "\n"
    cache_key += "Source lang: " + source_lang + "\n"
    cache_key += "Target lang: " + target_lang
    output = eenhoorntje_llm_lib.llm_cache.cache.query(cache_key)
    if output:
        return output

    translate_client = translate.Client.from_service_account_json(eenhoorntje_llm_lib.utils.get_key("GOOGLE_KEY"))

    result = translate_client.translate(sentence, target_language=target_lang, source_language=source_lang, format_="text")
    res = result["translatedText"]
    res = res.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&quot;", "\"")
    eenhoorntje_llm_lib.llm_cache.cache.add(cache_key, res)
    return res
