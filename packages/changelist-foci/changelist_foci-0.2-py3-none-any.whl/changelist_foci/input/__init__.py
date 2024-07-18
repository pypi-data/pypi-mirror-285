"""The Input Package level methods.
"""
from pathlib import Path
from sys import exit

from changelist_foci.format_options import FormatOptions
from changelist_foci.input.argument_parser import parse_arguments
from changelist_foci.input.file_validation import validate_input_file
from changelist_foci.input.input_data import InputData


def validate_input(arguments: list[str]) -> InputData:
    """
    Given the Command Line Arguments, obtain the InputData.

    Parameters:
    - arguments (list[str]): The Command Line Arguments received by the program.
    
    Returns:
    InputData - The formatted InputData.
    """
    arg_data = parse_arguments(arguments)
    return InputData(
        workspace_xml=_find_workspace_xml() if arg_data.workspace_path is None
            else validate_input_file(arg_data.workspace_path),
        changelist_name=arg_data.changelist_name,
        format_options=FormatOptions(
            full_path=arg_data.full_path,
            no_file_ext=arg_data.no_file_ext,
            file_name=arg_data.filename,
        )
    )


def _find_workspace_xml() -> str:
    """
    Assuming that the current directory is the root project directory, try to find the workspace file.
    
    Return:
    str - The workspace.xml file contents.

    Raises:
    SystemExit - If the .idea folder or the workspace file was not found, or failed to read.
    """
    current_dir = Path('.')
    idea_dir = current_dir / '.idea'
    if not idea_dir.exists():
        exit("The Current Directory must contain the .idea folder if workspace file path is not provided.")
    workspace_path = idea_dir / 'workspace.xml'
    if not workspace_path.exists():
        exit("The workspace file was not found inside the .idea folder.")
    try:
        return workspace_path.read_text()
    except:
        exit("Failed to Read the Workspace File.")
