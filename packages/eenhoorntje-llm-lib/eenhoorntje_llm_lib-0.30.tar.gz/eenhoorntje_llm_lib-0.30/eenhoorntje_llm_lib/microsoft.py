from azure.ai.translation.text import TranslatorCredential, TextTranslationClient
from azure.ai.translation.text.models import InputTextItem

import eenhoorntje_llm_lib.llm_cache
import eenhoorntje_llm_lib.utils


def translate_with_microsoft(sentence: str, source_lang: str, target_lang: str) -> str:
    if target_lang == "zh":
        target_lang = "zh-CN"
    if source_lang == "zh":
        source_lang = "zh-CN"

    cache_key = "Microsoft" + "\n"
    cache_key += "Source: " + sentence + "\n"
    cache_key += "Source lang: " + source_lang + "\n"
    cache_key += "Target lang: " + target_lang
    output = eenhoorntje_llm_lib.llm_cache.cache.query(cache_key)
    if output:
        return output

    key = eenhoorntje_llm_lib.utils.get_key("MICROSOFT_MT_API_KEY")
    endpoint = "https://api.cognitive.microsofttranslator.com/"
    region = "global"

    credential = TranslatorCredential(key, region)
    text_translator = TextTranslationClient(endpoint=endpoint, credential=credential)
    source_language = source_lang
    target_languages = [target_lang]
    input_text_elements = [InputTextItem(text=sentence)]
    response = text_translator.translate(content=input_text_elements, to=target_languages, from_parameter=source_language)
    translation = response[0] if response else None
    res = translation.translations[0].text
    eenhoorntje_llm_lib.llm_cache.cache.add(cache_key, res)
    return res
