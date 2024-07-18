"""
GPT Coder to solve competitive programming problems
"""

from typing import List

from colorama import Fore, Style

from myugpt.llm import MODEL_NAME, openai_client
from myugpt.schema import CodingEnv, ModelPrediction

GPT_SYSTEM = """You are MyuGPT, an advanced coding chat bot that solves \
competitive programming problems. You will be provided with a problem \
statement (along with the previous list of steps taken to solve the problem, \
if applicable). You will produce the next step as python code to solve the \
problem. Remember to think step by step, you will be given multiple shots!

The input is provided as a string in the global input varriable.
The output is expected as a string in the global output varriable.

```python3
global input: str
global output: str

def main():
    # Write your code here
    pass

main()
```
"""


class MyuGPT:
    def __init__(self, max_history=10):
        self.client = openai_client
        self.previous_messages = []
        self.max_history = max_history

    def step(
        self,
        env: CodingEnv,
        temperature: float = 0.5,
    ) -> ModelPrediction:
        """Step through the coding environment to solve the problem."""
        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            temperature=temperature,
            # max_retries=5,
            stream=True,
            messages=[
                {
                    "role": "user",
                    "content": env.prompt,
                },
                {
                    "role": "system",
                    "content": GPT_SYSTEM,
                },
            ],
            max_tokens=4096,
        )

        desc = ""

        print("Response:")

        print(Fore.GREEN)

        for message in response:
            message_data = message.choices[0].delta.content
            if isinstance(message_data, str):
                desc += message_data
                print(message_data, end="")

        print(Style.RESET_ALL)
        print("=" * 20)

        gpt_prediction = self.client.chat.completions.create(
            model=MODEL_NAME,
            response_model=ModelPrediction,
            temperature=temperature,
            max_retries=2,
            messages=[
                {
                    "role": "user",
                    "content": desc,
                },
                {
                    "role": "system",
                    "content": GPT_SYSTEM,
                },
                {
                    "role": "system",
                    "content": "Generate JSON response\n" + "```json\n\n```",
                },
            ],
            # max_tokens=4096,
        )

        print(gpt_prediction)

        return gpt_prediction

    def sample(
        self,
        env: CodingEnv,
        temperature: float = 0.5,
        num_samples: int = 1,
    ) -> List[ModelPrediction]:
        """Sample the coding environment to solve the problem."""

        result = []

        for _ in range(num_samples):
            result.append(
                self.step(
                    env=env,
                    temperature=temperature,
                )
            )

        return result


if __name__ == "__main__":
    from myugpt.dataset import CodeContestsDataset

    dataset = CodeContestsDataset()
    frame = dataset[0]
    gpt = MyuGPT()

    print(type(frame))

    env = CodingEnv(
        dataset_frame=frame,
    )

    print("env.prompt", env.prompt)

    prediction = gpt.step(env)

    print("prediction", prediction)
