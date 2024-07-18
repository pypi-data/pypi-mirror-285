import os
import pytest
from myugpt.settings import Settings


def test_default_values(monkeypatch):
    # Unset environment variables
    monkeypatch.delenv("CODE_CONTESTS", raising=False)
    monkeypatch.delenv("MCTS_EXPAND_SIZE", raising=False)
    monkeypatch.delenv("MCTS_ITERS", raising=False)

    # Create settings instance and assert defaults
    settings = Settings()
    expected_default_path = os.path.join(
        os.path.expanduser("~"), "Datasets", "code_contests", "data"
    )

    assert (
        settings.CODE_CONTESTS == expected_default_path
    ), "Default CODE_CONTESTS path does not match expected"
    assert settings.MCTS_EXPAND_SIZE == 1, "Default MCTS_EXPAND_SIZE is not 1"
    assert settings.MCTS_ITERS == 3, "Default MCTS_ITERS is not 3"


def test_environment_variable_overrides(monkeypatch):
    # Set environment variables
    monkeypatch.setenv("CODE_CONTESTS", "/new/path/to/code_contests")
    monkeypatch.setenv("MCTS_EXPAND_SIZE", "5")
    monkeypatch.setenv("MCTS_ITERS", "10")

    # Create settings instance and assert values
    settings = Settings()

    assert (
        settings.CODE_CONTESTS == "/new/path/to/code_contests"
    ), "CODE_CONTESTS should be overridden by environment variable"
    assert (
        settings.MCTS_EXPAND_SIZE == 5
    ), "MCTS_EXPAND_SIZE should be overridden by environment variable"
    assert (
        settings.MCTS_ITERS == 10
    ), "MCTS_ITERS should be overridden by environment variable"


# Run the tests
if __name__ == "__main__":
    pytest.main()
