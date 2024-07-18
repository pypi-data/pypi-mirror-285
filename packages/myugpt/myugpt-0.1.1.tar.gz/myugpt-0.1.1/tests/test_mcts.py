import pytest
from myugpt.code_env import run_code, validate_code
from myugpt.schema import (
    ProgramInputs,
    ProgramOutputs,
    ModelPrediction,
    CodingEnv,
    DatasetFrame,
    Validation,
)
from myugpt.mcts import uct_select, expand, is_terminal, simulate, mcts
from myugpt.schema import CodingEnv, ModelPrediction, Node
from myugpt.gpt import MyuGPT, GPT_SYSTEM
from unittest.mock import MagicMock


# Mock for the Testing
class MockGPT(MyuGPT):
    def step(
        self, env: CodingEnv, temperature: float = 0.5
    ) -> ModelPrediction:
        # Mocking GPT response
        return ModelPrediction(
            thought_process="Mock thought process.",
            code="output = input.strip().upper()",
        )


# Test run_code function
def test_run_code():
    code = """output = input.strip().upper()"""
    inputs = ProgramInputs(data=["  test  ", "hello ", "world "])
    expected_outputs = ProgramOutputs(data=["TEST", "HELLO", "WORLD"])

    outputs = run_code(code, inputs)

    assert (
        outputs == expected_outputs
    ), f"Expected {expected_outputs}, but got {outputs}"


# Test validate_code function
def test_validate_code():
    code = """output = input.strip().upper()"""
    model_pred = ModelPrediction(
        thought_process="Mock thought process.", code=code
    )
    inputs = ProgramInputs(data=["  test  ", "hello ", "world "])
    expected_outputs = ProgramOutputs(data=["TEST", "HELLO", "WORLD"])

    validation = validate_code(model_pred, inputs, expected_outputs)

    assert (
        validation.outputs == expected_outputs
    ), f"Expected {expected_outputs}, but got {validation.outputs}"


def test_uct_select():
    root = Node(
        state=CodingEnv(
            dataset_frame=DatasetFrame(
                problem_statement="Test Problem",
                inputs=ProgramInputs(data=["test"]),
                expected_outputs=ProgramOutputs(data=["TEST"]),
            )
        )
    )
    child1 = Node(state=root.state, parent=root, wins=10, visits=50)
    child2 = Node(state=root.state, parent=root, wins=20, visits=50)

    root.children.append(child1)
    root.children.append(child2)

    best_child = uct_select(root)

    assert best_child == child2, f"Expected {child2}, but got {best_child}"


def test_expand():
    root = Node(
        state=CodingEnv(
            dataset_frame=DatasetFrame(
                problem_statement="Test Problem",
                inputs=ProgramInputs(data=["test"]),
                expected_outputs=ProgramOutputs(data=["TEST"]),
            )
        )
    )
    gpt = MockGPT()

    expand(root, gpt, 1)

    assert len(root.children) > 0, "No children were added during expansion."


def test_is_terminal():
    inputs = ["123"]
    expected_outputs = ["456"]
    validation = Validation(outputs=ProgramOutputs(data=["789"]))
    env = CodingEnv(
        dataset_frame=DatasetFrame(
            problem_statement="Test Problem",
            inputs=ProgramInputs(data=inputs),
            expected_outputs=ProgramOutputs(data=expected_outputs),
        ),
        validation=validation,
    )
    node = Node(state=env)

    assert not is_terminal(node), "Node should not be terminal initially"


def test_simulate():
    inputs = ["test"]
    expected_outputs = ["TEST"]
    validation = Validation(outputs=ProgramOutputs(data=["estt"]))

    env = CodingEnv(
        dataset_frame=DatasetFrame(
            problem_statement="Test Problem",
            inputs=ProgramInputs(data=inputs),
            expected_outputs=ProgramOutputs(data=expected_outputs),
        ),
        validation=validation,
    )

    root = Node(state=env)
    gpt = MockGPT()

    result = simulate(root, gpt)

    assert result > 0, "Simulation result should be positive."


def test_mcts():
    env = CodingEnv(
        dataset_frame=DatasetFrame(
            problem_statement="Test Problem",
            inputs=ProgramInputs(data=["  test  ", "hello ", "world "]),
            expected_outputs=ProgramOutputs(data=["TEST", "HELLO", "WORLD"]),
        )
    )
    gpt = MockGPT()

    final_state = mcts(env, iterations=2, gpt=gpt, expand_size=2)

    assert final_state.score > 0, "Final state score should be positive."
