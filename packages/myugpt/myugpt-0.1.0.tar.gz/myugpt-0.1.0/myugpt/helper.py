from typing import List

from pydantic import validate_call
from scipy.spatial.distance import cosine

from myugpt.llm import openai_client


@validate_call
def get_embedding(
    text: str, model: str = "text-embedding-3-small"
) -> List[float]:
    text = text.replace("\n", " ")
    return (
        openai_client.embeddings.create(input=[text], model=model)
        .data[0]
        .embedding
    )


@validate_call
def text_similarity(
    text1: str,
    text2: str,
) -> float:
    """Calculate the text similarity (0 to 100)
    Use text embedding to calculate the similarity
    """

    # If the texts are the same, return 1
    if text1 == text2:
        return 100.0

    if len(text1) == 0 or len(text2) == 0:
        return 0.0

    # Compute the embeddings
    text1_embedding = get_embedding(text1)
    text2_embedding = get_embedding(text2)

    # Compute the cosine similarity
    similarity = cosine(text1_embedding, text2_embedding)

    return similarity * 100
