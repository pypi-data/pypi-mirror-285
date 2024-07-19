from pathlib import Path

import pandas as pd
from nptdms import TdmsFile, TdmsGroup


def extract_group(path: Path, group_idx: int):
    tdms_file = TdmsFile.read(path)

    group = tdms_file.groups()[group_idx]
    filename = f"{path.stem}_group_{group_idx}.csv"
    save_tdms_group_as_csv(group=group, filename=filename)


def save_tdms_group_as_csv(group: TdmsGroup, filename: str):
    group_data = {f"{channel.name}": channel[:] for channel in group.channels()}
    group_data_df = pd.DataFrame(group_data)
    group_data_df.to_csv(filename, index=False)
