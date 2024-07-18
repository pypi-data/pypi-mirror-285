"""
Models
"""

import ast
from typing import List

from pydantic import BaseModel, field_validator

from myugpt.helper import text_similarity


class ProgramInputs(BaseModel):
    """Program Input"""

    data: List[str]


class ProgramOutputs(BaseModel):
    """Program Output"""

    data: List[str]


class DatasetFrame(BaseModel):
    """Dataset Frame"""

    problem_statement: str
    inputs: ProgramInputs
    expected_outputs: ProgramOutputs

    def __str__(self):
        rep = "Problem Statement: " + self.problem_statement + "\n"
        rep += "=============\n"
        for index, (inp, out) in enumerate(
            zip(self.inputs.data, self.expected_outputs.data)
        ):
            rep += f"Input[{index}]:\n" + inp + "\n"
            rep += f"ExpectedOutputs[{index}]:\n" + out + "\n"
            rep += "=============\n"

        return rep


class ModelPrediction(BaseModel):
    """Model Prediction"""

    thought_process: str
    code: str
    # code: Annotated[
    #     str,
    #     BeforeValidator(
    #         llm_validator(
    #             "Write a valid Python code, "
    #             + "don't worry about varriable declatation or "
    #             + "logical errors, "
    #             + "don't worry about missing the necessary context and "
    #             + "structure to be considered valid Python code",
    #             openai_client,
    #         )
    #     ),
    # ]

    @field_validator("code")
    def is_valid_python(cls, v):
        try:
            ast.parse(v)
        except SyntaxError as se:
            raise ValueError(
                f"Invalid Python code:\n"
                f"SyntaxError:"
                f"{se.msg}"
                f"at line {se.lineno}"
            )
        return v

    # score: Annotated[
    #     float,
    #     BeforeValidator(
    #         llm_validator(
    #             "Score the correctness of your code (0 to 100)",
    #             openai_client,
    #         )
    #     ),
    # ]

    def __str__(self):
        rep = "ThoughtProcess:\n" + self.thought_process + "\n"
        rep += "Code:\n" + self.code + "\n"
        rep += "=============\n"
        # for index, out in enumerate(self.predicted_outputs.data):
        #     rep += f"PredictedOutputs[{index}]:\n" + out + "\n"
        #     rep += "=============\n"
        rep += "=============\n"
        # rep += "Score:\n" + str(self.score) + "\n"
        # rep += "=============\n"
        return rep


class Validation(BaseModel):
    """Validation"""

    outputs: ProgramOutputs


class CodingEnv(BaseModel):
    """Coding Environment"""

    # From Dataset
    dataset_frame: DatasetFrame

    # From Model
    model_predictions: List[ModelPrediction] = []

    # From Validation
    validation: Validation = Validation(outputs=ProgramOutputs(data=[]))

    @property
    def prompt(self):
        """Convert the code env to a prompt"""
        prompt = str(self.dataset_frame)
        prompt += "=============\n"
        for index, (model_prediction, validation) in enumerate(
            zip(self.model_predictions, self.validation.outputs.data)
        ):
            prompt += f"Code[{index}]:\n" + str(model_prediction) + "\n"
            prompt += "=============\n"
            prompt += f"Output[{index}]:\n" + str(validation) + "\n"
            prompt += "=============\n"
        return prompt

    @property
    def score(self):
        """Calculate the score"""
        res = 0
        model_prediction_list = self.dataset_frame.expected_outputs.data
        validation_list = self.validation.outputs.data

        assert len(model_prediction_list) == len(
            validation_list
        ), f"{len(model_prediction_list)} != {len(validation_list)}"

        for model_prediction, validation in zip(
            model_prediction_list, validation_list
        ):
            frame_score = text_similarity(
                model_prediction,
                validation,
            )
            assert 0 <= frame_score <= 100
            res += frame_score
        res = res / len(model_prediction_list)
        return res


# @no_type_check
class Node(BaseModel):
    """Node for MCTS"""

    state: CodingEnv  # type: ignore

    parent: "Node" = None  # type: ignore
    children: List["Node"] = []  # type: ignore
    wins: float = 0
    visits: int = 1
    untried_actions: List[ModelPrediction] = []
