from openai import OpenAI
import json
import eenhoorntje_llm_lib.llm_cache
import eenhoorntje_llm_lib.utils
import time
from PIL import Image
import base64
import io
import re


def clear_cache():
    eenhoorntje_llm_lib.llm_cache.cache.clear()


def parse_text_with_images(text):
    image_pattern = r'<image>(.*?)</image>'
    parts = re.split(image_pattern, text)

    result = []
    for part in parts:
        if part.strip():
            if part.endswith('.jpeg') or part.endswith('.jpg') or part.endswith('.png'):
                result.append({'type': 'image', 'content': part.strip()})
            else:
                result.append({'type': 'text', 'text': part.strip()})

    return result


def encode_image(image_path, crop_box=None):
    with Image.open(image_path) as img:
        if crop_box:
            img = img.crop((crop_box['left'], crop_box['top'], crop_box['right'], crop_box['bottom']))

        if img.mode != 'RGB':
            img = img.convert('RGB')

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=95)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')


def transform_message(message):
    parsed_text = parse_text_with_images(message['content'])
    has_images = False
    for part in parsed_text:
        if part['type'] == 'image':
            has_images = True
            break
    if not has_images:
        return message
    content_list = []
    for i in range(len(parsed_text)):
        if parsed_text[i]["type"] == "image":
            content_list.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{encode_image(parsed_text[i]['content'])}",
                },
            })
        else:
            content_list.append(parsed_text[i])
    res = {
        "role": message["role"],
        "content": content_list
    }
    return res


def call_llm(messages, model="anthropic/claude-3-haiku", temperature=0.0, max_tokens=500):
    api_key = eenhoorntje_llm_lib.utils.get_key("OPEN_ROUTER_API_KEY")
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    for i in range(len(messages)):
        messages[i] = transform_message(messages[i])

    cache_key = None
    if temperature == 0.0:
        cache_key = model + "\n" + json.dumps(messages, ensure_ascii=False, indent=4) + "\nMax tokens: " + str(
            max_tokens)
        output = eenhoorntje_llm_lib.llm_cache.cache.query(cache_key)
        if output:
            return output

    for i in range(8):
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
            time.sleep(2 ** i)
    return None
