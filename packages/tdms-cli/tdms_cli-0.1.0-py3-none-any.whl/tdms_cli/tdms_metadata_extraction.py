from nptdms import TdmsFile

_MAX_GROUPS_TO_PLOT = 10


def print_properties(properties):
    for el in properties:
        print(f"{el}: {properties[el]}")


def print_file_metadata(path: str):
    tdms_file = TdmsFile.read(path)
    print_properties(tdms_file.properties)


def print_group_metadata(path: str, group_idx: int = 0):
    tdms_file = TdmsFile.read(path)

    group = tdms_file.groups()[group_idx]
    print_properties(group.properties)


def print_channel_meta(path: str, group_path: str = ""):
    tdms_file = TdmsFile.read(path)

    if group_path:
        group = tdms_file[group_path]
    else:
        group = tdms_file.groups()[0]

    for channel in group.channels():
        print(f"\n{channel}")
        print_properties(channel.properties)


def display_groups(path: str):
    tdms_file = TdmsFile.read(path)

    groups = tdms_file.groups()
    num_groups = len(groups)
    print(f"Number of groups: {num_groups}")

    if num_groups > _MAX_GROUPS_TO_PLOT:
        print(f"Number of groups over {_MAX_GROUPS_TO_PLOT}, printing head and tail")

        print("--HEAD--")
        for j in range(_MAX_GROUPS_TO_PLOT // 2):
            print(groups[j])

        print("--TAIL--")
        for j in range(-(_MAX_GROUPS_TO_PLOT // 2), 0):
            print(groups[j])
    else:
        for group in groups:
            print(group)
