import eenhoorntje_llm_lib.llm
import eenhoorntje_llm_lib.language_codes
import copy

TRANSLATION_REFUSAL = "Ø"

translation_prompt_gpt4o = [
    {
        "role": "system",
        "content": "Your task is to provide a precise and idiomatic translation of the given text from {source_language} to {target_language}. Ensure that the translation maintains the original meaning, tone, and style, while also sounding natural and fluent in the target language. Write only the translation, nothing else."
    },
    {
        "role": "user",
        "content": "Please translate the following text:\n\n{source_content}"
    }
]

translation_prompt_gpt4 = [
    {
        "role": "system",
        "content": "Please provide a high-quality translation of the message from {source_language} to {target_language}, maintaining the original meaning and tone. Write only the translation, nothing else."
    },
    {
        "role": "user",
        "content": "{source_content}"
    }
]

translation_prompt_gpt35 = [
    {
        "role": "system",
        "content": "Translate the following message from {source_language} to {target_language}, ensuring the translation is accurate and fluent. Write only the translation, nothing else."
    },
    {
        "role": "user",
        "content": "{source_content}"
    }
]

translation_prompt_claude_sonnet = [
    {
        "role": "system",
        "content": "Your task is to translate the provided text from {source_language} to {target_language} with high accuracy, fluency, and contextual appropriateness. The translation should maintain the original meaning, tone, and style, while also sounding natural and idiomatic in the target language. Please ensure that any cultural nuances or contextual elements present in the source text are preserved in the translation. Write only the translation, nothing else."
    },
    {
        "role": "user",
        "content": "Here is the text to be translated:\n\n{source_content}"
    }
]

translation_prompt_claude_opus = [
    {
        "role": "system",
        "content": "As a sophisticated language model, you are tasked with translating texts between various languages with high accuracy and fluency. Ensure that your translations from {source_language} to {target_language} maintain the original's meaning, tone, and style, while also being clear and idiomatic in the target language."
    },
    {
        "role": "user",
        "content": "Translate this text from {source_language} to {target_language}: '{source_content}'. Write only the translation, nothing else."
    }
]


def create_prompt(source, source_lang, target_lang, model):
    source_language_name = eenhoorntje_llm_lib.language_codes.get_language_name(source_lang)
    target_language_name = eenhoorntje_llm_lib.language_codes.get_language_name(target_lang)

    messages = [
        {"role": "user",
         "content": f"Translate the following from {source_language_name} to {target_language_name}: '{source}'. Make the translation sound as natural as possible. Write only the translation, do not write anything else."}
    ]

    if "openai/gpt" in model:
        if model == "openai/gpt-4-turbo":
            messages = copy.deepcopy(translation_prompt_gpt4)
        if model == "openai/gpt-3.5-turbo":
            messages = copy.deepcopy(translation_prompt_gpt35)
        if model == "openai/gpt-4o":
            messages = copy.deepcopy(translation_prompt_gpt4o)

    if "anthropic/claude" in model:
        if "sonnet" in model:
            messages = copy.deepcopy(translation_prompt_claude_sonnet)
        if "opus" in model:
            messages = copy.deepcopy(translation_prompt_claude_opus)

    return messages


def translate(source, source_lang, target_lang, engine, custom_prompt=None):
    model = engine

    messages = create_prompt(source, source_lang, target_lang, model)
    if custom_prompt is not None:
        messages = copy.deepcopy(custom_prompt)

    for i in range(len(messages)):
        messages[i]["content"] = messages[i]["content"].replace("{source_content}", source)
        messages[i]["content"] = messages[i]["content"].replace("{source_language}",
                                                                eenhoorntje_llm_lib.language_codes.get_language_name(
                                                                    source_lang))
        messages[i]["content"] = messages[i]["content"].replace("{target_language}",
                                                                eenhoorntje_llm_lib.language_codes.get_language_name(
                                                                    target_lang))

    translation = eenhoorntje_llm_lib.llm.call_llm(messages, model, max_tokens=min(2048, len(source) * 4))

    if translation is None:
        return TRANSLATION_REFUSAL

    return translation
