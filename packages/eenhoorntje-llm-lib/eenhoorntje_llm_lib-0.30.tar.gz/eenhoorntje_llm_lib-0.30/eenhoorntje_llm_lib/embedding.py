from openai import OpenAI
import json
import eenhoorntje_llm_lib.llm_cache
import eenhoorntje_llm_lib.utils
import time


def embed(text, model="text-embedding-3-large", precision=None, n=None):
    models = ["text-embedding-3-large", "text-embedding-3-small"]
    if model not in models:
        raise ValueError(
            f"Invalid model: it should be either 'text-embedding-3-large' or 'text-embedding-3-small' but got '{model}'")

    api_key = eenhoorntje_llm_lib.utils.get_key("OPEN_AI_API_KEY")
    client = OpenAI(api_key=api_key)

    cache_key = model + "\n" + text
    if n is not None:
        cache_key += "\nN: " + str(n)
    output = eenhoorntje_llm_lib.llm_cache.cache.query(cache_key)
    if output:
        output = json.loads(output)
        return output

    response = None
    for i in range(10):
        try:
            if n is None:
                response = client.embeddings.create(
                    input=text,
                    model=model
                )
            else:
                response = client.embeddings.create(
                    input=text,
                    model=model,
                    dimensions=n
                )
            break
        except Exception as e:
            print(e)
            print(f"Retrying in {2 ** i} seconds...")
            time.sleep(2 ** i)
            continue

    if response is None:
        return None
    res = response.data[0].embedding

    if precision is not None:
        res = [round(x, precision) for x in res]

    string_to_cache = json.dumps(res)
    eenhoorntje_llm_lib.llm_cache.cache.add(cache_key, string_to_cache)
    return res


def dot_product(embedding1, embedding2):
    return sum([a * b for a, b in zip(embedding1, embedding2)])


def norm(embedding):
    return sum([a ** 2 for a in embedding]) ** 0.5


def cosine_similarity(embedding1, embedding2):
    embedding_dot_product = dot_product(embedding1, embedding2)
    norm1 = norm(embedding1)
    norm2 = norm(embedding2)
    res = embedding_dot_product / (norm1 * norm2)
    return res


def text_similarity(text1, text2, model="text-embedding-3-large", precision=None, n=None, metric="cosine"):
    embedding1 = embed(text1, model, precision, n)
    embedding2 = embed(text2, model, precision, n)
    if embedding1 is None or embedding2 is None:
        return None
    if metric == "cosine":
        return cosine_similarity(embedding1, embedding2)
    if metric == "dot":
        return dot_product(embedding1, embedding2)
    raise ValueError(f"Invalid metric: it should be either 'cosine' or 'dot' but got '{metric}'")
