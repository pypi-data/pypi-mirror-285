import eenhoorntje_llm_lib.llm_cache
import eenhoorntje_llm_lib.utils
import boto3


def call_api(sentence, source_lang, target_lang):
    translate_client = boto3.client(
        'translate',
        aws_access_key_id=eenhoorntje_llm_lib.utils.get_key("AMAZON_API_KEY"),
        aws_secret_access_key=eenhoorntje_llm_lib.utils.get_key("AMAZON_SECRET_KEY"),
        region_name='us-west-2'
    )

    text = sentence

    try:
        response = translate_client.translate_text(
            Text=text,
            SourceLanguageCode=source_lang,
            TargetLanguageCode=target_lang
        )

        translated_text = response['TranslatedText']
        return translated_text
    except Exception as e:
        print(f"Error: {e}")


def translate_with_amazon(sentence: str, source_lang: str, target_lang: str) -> str:
    if target_lang == "zh":
        target_lang = "zh-CN"
    if source_lang == "zh":
        source_lang = "zh-CN"

    cache_key = "Amazon" + "\n"
    cache_key += "Source: " + sentence + "\n"
    cache_key += "Source lang: " + source_lang + "\n"
    cache_key += "Target lang: " + target_lang
    output = eenhoorntje_llm_lib.llm_cache.cache.query(cache_key)
    if output:
        return output

    res = call_api(sentence, source_lang, target_lang)
    eenhoorntje_llm_lib.llm_cache.cache.add(cache_key, res)
    return res
