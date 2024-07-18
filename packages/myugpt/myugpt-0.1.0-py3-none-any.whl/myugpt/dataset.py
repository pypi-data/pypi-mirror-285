import os
from glob import glob
from typing import List, Union

import pandas as pd

from myugpt.schema import DatasetFrame, ProgramInputs, ProgramOutputs
from myugpt.settings import settings

CODE_CONTESTS_DATASETS = glob(
    os.path.join(settings.CODE_CONTESTS, "*.parquet")
)


class Dataset:
    def __init__(self):
        raise NotImplementedError()

    def __len__(self) -> int:
        raise NotImplementedError()

    def __getitem__(self, idx) -> Union[DatasetFrame, List[DatasetFrame]]:
        raise NotImplementedError()

    def __iter__(self):
        raise NotImplementedError()

    def __repr__(self):
        return f"Dataset with {len(self)} items"

    def __str__(self):
        return self.__repr__()


class CodeContestsDataset(Dataset):
    def __init__(
        self,
        dataset_path: str = CODE_CONTESTS_DATASETS[0],
    ):
        self.dataset_path = dataset_path
        self.df = pd.read_parquet(self.dataset_path, engine="pyarrow")

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx) -> DatasetFrame:
        # if idx is a slice
        # if isinstance(idx, slice):
        #     return [
        #         self[sub_idx] for sub_idx in range(*idx.indices(len(self)))
        #     ]

        frame = self.df.iloc[idx]

        program_inputs = ProgramInputs(
            data=frame["public_tests"]["input"],
        )
        program_outputs = ProgramOutputs(
            data=frame["public_tests"]["output"],
        )

        return DatasetFrame(
            problem_statement=frame["description"],
            inputs=program_inputs,
            expected_outputs=program_outputs,
        )

    def __iter__(self):
        for idx in range(len(self)):
            yield self[idx]


if __name__ == "__main__":
    dataset = CodeContestsDataset()
    print(dataset)
    frame = dataset[0]
    print(frame)
