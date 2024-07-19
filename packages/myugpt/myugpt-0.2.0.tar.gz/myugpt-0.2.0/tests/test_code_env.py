from myugpt.schema import (
    ModelPrediction,
    ProgramInputs,
    ProgramOutputs,
    Validation,
)
from myugpt.code_env import run_code, validate_code

# sample code for testing
test_code = """
# main function
def main(data_in: str) -> str:
    data_out = data_in[::-1]  # reverse the input string

    return data_out

# call the main function
data_out = main(data_in)
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
# main function
def main(data_in: str) -> str:
    data_out = data_in  # no change to the input string

    return data_out

# call the main function
data_out = main(data_in)
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


def test_code_example():
    code = """

def main(data_in: str) -> str:
    import math
    
    def distance(x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    data_lines = data_in.strip().split('\\n')
    index = 0
    results = []
    
    while index < len(data_lines):
        n = int(data_lines[index].strip())
        if n == 0:
            break
        index += 1
        
        stickers = []
        for _ in range(n):
            x, y = map(float, data_lines[index].strip().split(','))
            stickers.append((x, y))
            index += 1
        
        max_overlap = 0
        for i in range(n):
            overlap_count = 1  # start with the sticker itself
            for j in range(n):
                if i != j and distance(stickers[i][0], stickers[i][1], stickers[j][0], stickers[j][1]) <= 2:
                    overlap_count += 1
            max_overlap = max(max_overlap, overlap_count)
        
        results.append(str(max_overlap))
    
    return '\\n'.join(results)

# global inputs and outputs: data_in, data_out
# call the main function
data_out = main(data_in)
"""
    inputs = ProgramInputs(
        data=[
            """15
3.14979,8.51743
2.39506,3.84915
2.68432,5.39095
5.61904,9.16332
7.85653,4.75593
2.84021,5.41511
1.79500,8.59211
7.55389,8.17604
4.70665,4.66125
1.63470,4.42538
7.34959,4.61981
5.09003,8.11122
5.24373,1.30066
0.13517,1.83659
7.57313,1.58150
0"""
        ]
    )
    expected_outputs = ProgramOutputs(data=["4"])

    outputs = run_code(code, inputs)

    assert (
        outputs == expected_outputs
    ), f"Expected {expected_outputs} but got {outputs}"


if __name__ == "__main__":
    import pytest

    pytest.main()
