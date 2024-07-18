"""Defines and Validates Argument Syntax.

Encapsulates Argument Parser.

Returns Argument Data, the args provided by the User.
"""
from argparse import ArgumentParser
from sys import exit
from typing import Optional

from .argument_data import ArgumentData
from .string_validation import validate_name


def parse_arguments(args: Optional[list[str]] = None) -> ArgumentData:
    """
    Parse command line arguments.

    Parameters:
    - args: A list of argument strings.

    Returns:
    ArgumentData : Container for Valid Argument Data.
    """
    if args is None:
        exit("No Arguments given.")
    # Initialize the Parser and Parse Immediately
    try:
        parsed_args = _define_arguments().parse_args(args)
    except SystemExit as e:
        exit("Unable to Parse Arguments.")
    return _validate_arguments(parsed_args)


def _validate_arguments(
    parsed_args,
) -> ArgumentData:
    """
    Checks the values received from the ArgParser.
        Uses Validate Name method from StringValidation.

    Parameters:
    - parsed_args : The object returned by ArgumentParser.

    Returns:
    ArgumentData - A DataClass of syntactically correct arguments.
    """
    changelist = parsed_args.changelist
    path = parsed_args.workspace
    # Validate Names
    if changelist is not None:
        if not validate_name(changelist):
            exit("The ChangeList Name was invalid.")
    if path is not None:
        if not validate_name(path):
            exit("The Workspace Path argument was invalid.")
    #
    return ArgumentData(
        changelist_name=changelist,
        workspace_path=path,
        full_path=parsed_args.full_path,
        no_file_ext=parsed_args.no_file_ext,
        filename=parsed_args.filename,
    )


def _define_arguments() -> ArgumentParser:
    """
    Initializes and Defines Argument Parser.
       - Sets Required/Optional Arguments and Flags.

    Returns:
    argparse.ArgumentParser - An instance with all supported Arguments.
    """
    parser = ArgumentParser(
        description="ChangeList FOCI Producer",
    )
    # Optional Arguments
    parser.add_argument(
        '--changelist',
        type=str,
        default=None,
        help='The Workspace File containing the ChangeList data.'
    )
    parser.add_argument(
        '--workspace',
        type=str,
        default=None,
        help='The Path to the workspace file, or none if cwd is the project root.',
    )
    parser.add_argument(
        '--full-path',
        action='store_true',
        default=False,
        help='Display the Full File Path.',
    )
    parser.add_argument(
        '--no-file-ext', '-x',
        action='store_true',
        default=False,
        help='Remove File Extension from File paths.',
    )
    parser.add_argument(
        '--filename', '-f',
        action='store_true',
        default=False,
        help='Remove Parent Directories from File paths.',
    )
    return parser
