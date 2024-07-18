"""
LLM
"""

import instructor
from openai import OpenAI

# MODEL_NAME = "codellama"
MODEL_NAME = "gpt-4o"
# MODEL_NAME = "mistral:instruct"
# MODEL_NAME = "mixtral:8x7b-instruct-v0.1-q2_K"

openai_client = instructor.patch(
    OpenAI(),
    mode=instructor.Mode.JSON,
)
