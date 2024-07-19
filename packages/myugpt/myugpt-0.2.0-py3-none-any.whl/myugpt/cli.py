"""CLI interface for myugpt project.
"""

from myugpt.dataset import CodeContestsDataset
from myugpt.gpt import MyuGPT
from myugpt.mcts import mcts
from myugpt.schema import CodingEnv
from myugpt.settings import settings


def main():  # pragma: no cover
    """
    The main function executes on commands:
    `python -m myugpt` and `$ myugpt `.
    """
    myugpt = MyuGPT()
    dataset = CodeContestsDataset()

    frame = dataset[0]

    env = CodingEnv(
        dataset_frame=frame,
    )

    print(env.prompt)

    result = mcts(env, settings.MCTS_ITERS, myugpt, settings.MCTS_EXPAND_SIZE)

    print("=" * 20)
    print("Final Result")
    print("=" * 20)
    print(result)
    print("=" * 20)
