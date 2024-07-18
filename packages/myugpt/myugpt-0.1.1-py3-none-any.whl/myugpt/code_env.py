import sys
import traceback

from myugpt.schema import (
    ModelPrediction,
    ProgramInputs,
    ProgramOutputs,
    Validation,
)


def run_code(code: str, inputs: ProgramInputs) -> ProgramOutputs:
    """
    Run the provided Python code with the given inputs and return the output.
    """
    outputs = []
    for input in inputs.data:
        data = ""
        try:
            # Create a dictionary to serve as the local namespace for the
            # exec function
            local_namespace = {
                "input": input,
                "output": "",
            }
            exec(code, {}, local_namespace)
            data_tmp = local_namespace.get("output")
            if data_tmp is None:
                data = ""
            else:
                data = str(data_tmp)
        except Exception:
            print(
                "An error occurred while executing the code:", file=sys.stderr
            )
            data = traceback.format_exc()
        finally:
            print("Output:", data)
            assert isinstance(data, str), "Output must be a string."
            outputs.append(data)

    return ProgramOutputs(data=outputs)


def validate_code(
    model_pred: ModelPrediction,
    inputs: ProgramInputs,
    expected_outputs: ProgramOutputs,
) -> Validation:
    """Run the code with the inputs and compare the outputs"""
    # Run the code
    code = model_pred.code
    actual_outputs = run_code(code, inputs)
    print("Actual Outputs:", actual_outputs)
    print("Expected Outputs:", expected_outputs.data)

    correct_mask = [
        actual == expected
        for actual, expected in zip(actual_outputs.data, expected_outputs.data)
    ]
    all_correct = all(correct_mask)

    # Compare the actual outputs with the expected outputs
    if all_correct:
        return Validation(outputs=expected_outputs)
    else:
        print("The actual outputs do not match the expected outputs.")
        return Validation(outputs=actual_outputs)


if __name__ == "__main__":
    pass
