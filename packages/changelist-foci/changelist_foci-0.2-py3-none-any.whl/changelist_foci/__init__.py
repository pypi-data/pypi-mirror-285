""" Package Methods.
"""
from changelist_foci.changelist_data import ChangelistData
from .input.input_data import InputData
from .workspace_reader import read_workspace_changelists


def get_changelist_foci(
    input_data: InputData,
) -> str:
    """
    Processes InputData, returning the FOCI.

    Parameters:
    - input_data (InputData): The program input data.

    Returns:
    str - The FOCI formatted output.
    """
    return _get_change_list(input_data).get_foci(input_data.format_options)


def _get_change_list(input_data: InputData) -> ChangelistData:
    """
    Obtain the given Changelist by name, or the Active Changelist if no name was given.

    Parameters:
    - input_data (InputData): The program Input.

    Returns:
    ChangelistData - The Changelist requested by the Input Data.
    """
    cl_list = read_workspace_changelists(input_data.workspace_xml)
    if (cl_name := input_data.changelist_name) not in ["None", None]:
        # Operate on the given Changelist
        filtered_list = list(filter(lambda x: x.name == cl_name, cl_list))
    else:
        # Active Changelist
        if len(cl_list) == 1:
            filtered_list = [cl_list[0]]
        else:
            filtered_list = list(filter(lambda x: x.is_default, cl_list))
    # Ensure that there is only one match
    if (match_length := len(filtered_list)) < 1:
        exit(f"Specified Changelist {cl_name} not present.")
    elif match_length > 1:
        exit("More than one Changelist found.")
    return filtered_list[0]
