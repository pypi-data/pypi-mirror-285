import eenhoorntje_llm_lib.language_codes
import eenhoorntje_llm_lib
import eenhoorntje_llm_lib.deepl
import eenhoorntje_llm_lib.translate_llm
import eenhoorntje_llm_lib.gemini
import eenhoorntje_llm_lib.google
import eenhoorntje_llm_lib.yandex
import eenhoorntje_llm_lib.modern_mt
import eenhoorntje_llm_lib.microsoft
import eenhoorntje_llm_lib.amazon

TRANSLATION_REFUSAL = "Ø"


def translate(source, source_lang, target_lang, engine="anthropic/claude-3-opus", custom_prompt=None, tags=False, formality="default"):
    if source_lang == target_lang:
        return source

    if engine is None:
        engine = "anthropic/claude-3.5-sonnet"
        if target_lang in ["fr", "pt", "pt-BR", "pt-PT", "ja", "ar", "th"]:
            engine = "openai/gpt-4o"

    if source_lang == target_lang:
        return source
    if engine == "DeepL":
        return eenhoorntje_llm_lib.deepl.translate_with_deepl(source, source_lang, target_lang, tags, formality)
    if engine == "Google":
        return eenhoorntje_llm_lib.google.translate_with_google(source, source_lang, target_lang)
    if engine == "Yandex":
        return eenhoorntje_llm_lib.yandex.translate_with_yandex(source, source_lang, target_lang)
    if engine == "ModernMT":
        return eenhoorntje_llm_lib.modern_mt.translate_with_modern_mt(source, source_lang, target_lang)
    if engine == "Microsoft":
        return eenhoorntje_llm_lib.microsoft.translate_with_microsoft(source, source_lang, target_lang)
    if engine == "Amazon":
        return eenhoorntje_llm_lib.amazon.translate_with_amazon(source, source_lang, target_lang)
    if "Gemini" in engine:
        return eenhoorntje_llm_lib.gemini.translate_with_gemini(source, source_lang, target_lang, engine, custom_prompt)
    return eenhoorntje_llm_lib.translate_llm.translate(source, source_lang, target_lang, engine, custom_prompt)


if __name__ == "__main__":
    res = translate("hoi goe gaat het met jouw?", "ru", "en")
    print(res)
    # translate_corpus()
