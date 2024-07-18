from myugpt.schema import (
    ModelPrediction,
    ProgramInputs,
    ProgramOutputs,
    Validation,
)
from myugpt.code_env import run_code, validate_code

# sample code for testing
test_code = """
output = input[::-1];  # reverse the input string
"""


def test_run_code():
    inputs = ProgramInputs(data=["hello", "world"])
    expected_outputs = ProgramOutputs(data=["olleh", "dlrow"])

    outputs = run_code(test_code, inputs)

    assert (
        outputs == expected_outputs
    ), f"Expected {expected_outputs} but got {outputs}"


def test_validate_code_correct():
    model_pred = ModelPrediction(
        thought_process="reverse input", code=test_code
    )
    inputs = ProgramInputs(data=["hello", "world"])
    expected_outputs = ProgramOutputs(data=["olleh", "dlrow"])

    validation = validate_code(model_pred, inputs, expected_outputs)

    assert (
        validation.outputs == expected_outputs
    ), f"Expected {expected_outputs} but got {validation.outputs}"


def test_validate_code_incorrect():
    incorrect_code = """
output = input  # no change to the input string
"""
    model_pred = ModelPrediction(
        thought_process="no reverse", code=incorrect_code
    )
    inputs = ProgramInputs(data=["hello", "world"])
    expected_outputs = ProgramOutputs(data=["olleh", "dlrow"])
    actual_outputs = ProgramOutputs(data=["hello", "world"])

    validation = validate_code(model_pred, inputs, expected_outputs)

    assert (
        validation.outputs == actual_outputs
    ), f"Expected {actual_outputs} but got {validation.outputs}"


if __name__ == "__main__":
    import pytest

    pytest.main()
