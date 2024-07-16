from modernmt import ModernMT
import eenhoorntje_llm_lib.llm_cache
import eenhoorntje_llm_lib.utils


def translate_with_modern_mt(sentence: str, source_lang: str, target_lang: str) -> str:
    if target_lang == "zh":
        target_lang = "zh-CN"
    if source_lang == "zh":
        source_lang = "zh-CN"

    cache_key = "ModernMT" + "\n"
    cache_key += "Source: " + sentence + "\n"
    cache_key += "Source lang: " + source_lang + "\n"
    cache_key += "Target lang: " + target_lang
    output = eenhoorntje_llm_lib.llm_cache.cache.query(cache_key)
    if output:
        return output

    mmt = ModernMT(eenhoorntje_llm_lib.utils.get_key("MODERN_MT_API_KEY"))
    translation = mmt.translate(source_lang, target_lang, sentence)
    res = translation.translation
    eenhoorntje_llm_lib.llm_cache.cache.add(cache_key, res)
    return res
