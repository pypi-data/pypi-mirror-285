import os

DEFAULT_CODE_CONTESTS = os.path.join(
    os.path.expanduser("~"), "Datasets", "code_contests", "data"
)


class Settings:
    @property
    def CODE_CONTESTS(self) -> str:
        return os.environ.get("CODE_CONTESTS", DEFAULT_CODE_CONTESTS)

    @property
    def MCTS_EXPAND_SIZE(self) -> int:
        return int(os.environ.get("MCTS_EXPAND_SIZE", "1"))

    @property
    def MCTS_ITERS(self) -> int:
        return int(os.environ.get("MCTS_ITERS", "3"))


settings = Settings()
