import eenhoorntje_llm_lib.language_codes
import google.generativeai as genai
import json
import requests
import eenhoorntje_llm_lib.llm_cache
import eenhoorntje_llm_lib.utils
import eenhoorntje_llm_lib.translate
import time


def call_gemini(model_name, prompt, temperature=0.0):
    key = eenhoorntje_llm_lib.utils.get_key("GEMINI_API_KEY")
    genai.configure(api_key=key)

    model = genai.GenerativeModel(model_name)

    cache_key = None
    if temperature == 0.0:
        cache_key = model_name + "\n" + prompt
        output = eenhoorntje_llm_lib.llm_cache.cache.query(cache_key)
        if output:
            return output

    for i in range(8):
        response = None
        try:
            response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(
                temperature=temperature),
                                              safety_settings={
                                                  'HARASSMENT': 'block_none',
                                                  'HATE_SPEECH': 'block_none',
                                              })
            if cache_key:
                eenhoorntje_llm_lib.llm_cache.cache.add(cache_key, response.text)
            return response.text
        except Exception as e:
            print("Gemini Error", e)
            if hasattr(response.prompt_feedback, "block_reason"):
                if cache_key:
                    eenhoorntje_llm_lib.llm_cache.cache.add(cache_key,
                                                            eenhoorntje_llm_lib.translate.TRANSLATION_REFUSAL)
                return eenhoorntje_llm_lib.translate.TRANSLATION_REFUSAL
            print("Error", f"retrying in {2 ** i} seconds")

            time.sleep(2 ** i)
    return None


def translate_with_gemini(content, source_lang, target_lang, version, custom_prompt=None):
    source_language_name = eenhoorntje_llm_lib.language_codes.get_language_name(source_lang)
    target_language_name = eenhoorntje_llm_lib.language_codes.get_language_name(target_lang)
    model_name = "gemini-1.0-pro-latest"
    if version == "Gemini-1.5":
        model_name = "gemini-1.5-pro-latest"

    prompt = f"This is {source_language_name} to {target_language_name} translation, please provide the {target_language_name} translation for this sentence. Make the translation sound as natural as possible.\n" \
             f"{source_language_name}: {content}\n" \
             f"{target_language_name}:"

    if custom_prompt:
        prompt = custom_prompt
        prompt = prompt.replace("{source_language}", source_language_name)
        prompt = prompt.replace("{target_language}", target_language_name)
        prompt = prompt.replace("{source_content}", content)

    res = call_gemini(model_name, prompt)
    return res
