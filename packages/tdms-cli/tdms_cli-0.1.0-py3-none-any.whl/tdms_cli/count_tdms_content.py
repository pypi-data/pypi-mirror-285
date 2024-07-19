from typing import Dict

from nptdms import TdmsFile


def count_groups(path: str):
    tdms_file = TdmsFile.read(path)

    num_groups = 0
    channel_count: Dict[int, int] = {}
    for group in tdms_file.groups():
        num_groups += 1

        num_group_channels = 0
        for _ in group.channels():
            num_group_channels += 1

        if num_group_channels in channel_count:
            channel_count[num_group_channels] += 1
        else:
            channel_count[num_group_channels] = 1

    print(f"Number of groups: {num_groups}")
    print(f"Channel count (num_channels_in_group: num_groups): {channel_count}")
