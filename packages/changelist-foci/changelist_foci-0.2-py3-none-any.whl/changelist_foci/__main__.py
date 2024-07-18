#!/usr/bin/python
from sys import argv, path


def main():
    from changelist_foci.input import validate_input
    from changelist_foci import get_changelist_foci
    input_data = validate_input(argv[1:])
    output_data = get_changelist_foci(input_data)
    print(output_data)


if __name__ == "__main__":
    from pathlib import Path
    # Get the directory of the current file (__file__ is the path to the script being executed)
    current_directory = Path(__file__).resolve().parent.parent
    # Add the directory to sys.path
    path.append(str(current_directory))
    main()

