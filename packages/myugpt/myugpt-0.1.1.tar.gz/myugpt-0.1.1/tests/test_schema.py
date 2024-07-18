# test_schema.py

import pytest
from pydantic import ValidationError
from myugpt.schema import (
    ProgramInputs,
    ProgramOutputs,
    DatasetFrame,
    ModelPrediction,
    Validation,
    CodingEnv,
)


def test_program_inputs():
    data = ["input1", "input2"]
    inputs = ProgramInputs(data=data)
    assert inputs.data == data


def test_program_outputs():
    data = ["output1", "output2"]
    outputs = ProgramOutputs(data=data)
    assert outputs.data == data


def test_dataset_frame():
    problem_statement = "Sample Problem"
    inputs = ProgramInputs(data=["input1", "input2"])
    outputs = ProgramOutputs(data=["output1", "output2"])
    dataset_frame = DatasetFrame(
        problem_statement=problem_statement,
        inputs=inputs,
        expected_outputs=outputs,
    )
    assert dataset_frame.problem_statement == problem_statement
    assert dataset_frame.inputs == inputs
    assert dataset_frame.expected_outputs == outputs


def test_model_prediction_valid_code():
    thought_process = "Sample thought process"
    code = "print('Hello, world!')"
    prediction = ModelPrediction(thought_process=thought_process, code=code)
    assert prediction.thought_process == thought_process
    assert prediction.code == code


def test_model_prediction_invalid_code():
    thought_process = "Sample thought process"
    code = "print('Hello, world!'"  # Missing closing parenthesis
    with pytest.raises(ValidationError):
        ModelPrediction(thought_process=thought_process, code=code)


def test_validation():
    outputs = ProgramOutputs(data=["output1", "output2"])
    validation = Validation(outputs=outputs)
    assert validation.outputs == outputs


def test_coding_env():
    problem_statement = "Sample Problem"
    inputs = ProgramInputs(data=["input1", "input2"])
    expected_outputs = ProgramOutputs(data=["output1", "output2"])
    dataset_frame = DatasetFrame(
        problem_statement=problem_statement,
        inputs=inputs,
        expected_outputs=expected_outputs,
    )
    model_predictions = [
        ModelPrediction(
            thought_process="Sample thought process",
            code="print('Hello, world!')",
        )
    ]
    validation = Validation(
        outputs=ProgramOutputs(data=["output1", "output2"])
    )
    coding_env = CodingEnv(
        dataset_frame=dataset_frame,
        model_predictions=model_predictions,
        validation=validation,
    )
    assert coding_env.dataset_frame == dataset_frame
    assert coding_env.model_predictions == model_predictions
    assert coding_env.validation == validation


def test_coding_env_prompt():
    problem_statement = "Sample Problem"
    inputs = ProgramInputs(data=["input1", "input2"])
    outputs = ProgramOutputs(data=["output1", "output2"])
    dataset_frame = DatasetFrame(
        problem_statement=problem_statement,
        inputs=inputs,
        expected_outputs=outputs,
    )
    coding_env = CodingEnv(dataset_frame=dataset_frame)
    prompt = coding_env.prompt
    assert problem_statement in prompt
    assert "input1" in prompt
    assert "output1" in prompt


def test_coding_env_score():
    problem_statement = "Sample Problem"
    inputs = ProgramInputs(data=["input1", "input2"])
    expected_outputs = ProgramOutputs(data=["output1", "output2"])
    dataset_frame = DatasetFrame(
        problem_statement=problem_statement,
        inputs=inputs,
        expected_outputs=expected_outputs,
    )
    model_predictions = [
        ModelPrediction(
            thought_process="Sample thought process", code="print('output1')"
        )
    ]
    validation = Validation(
        outputs=ProgramOutputs(data=["output1", "output2"])
    )
    coding_env = CodingEnv(
        dataset_frame=dataset_frame,
        model_predictions=model_predictions,
        validation=validation,
    )
    score = coding_env.score
    assert (
        0.0 <= score <= 100.0
    ), f"Expected score between 0 and 100, but got {score}"
