"""Testing ChangeList Data
"""

from fileinput import filename
from changelist_foci.change_data import ChangeData
from changelist_foci.changelist_data import ChangelistData
from changelist_foci.format_options import FormatOptions


def get_cl0():
    return ChangelistData(
        id="0",
        name="",
        changes=list(),
    )

def get_cl1():
    return ChangelistData(
        id="1212434",
        name="ChangeList",
        changes=[
            ChangeData(
                after_path="/module/file.txt",
                after_dir=False,
            )
        ],
    )


def test_get_foci_0_returns_error():
    result = get_cl0().get_foci()
    assert result == ":\n"

    
def test_get_foci_1_returns_str():
    result = get_cl1().get_foci()
    assert result == "ChangeList:\n* Create module/file.txt"


def test_get_foci_1_full_path_returns_str():
    result = get_cl1().get_foci(FormatOptions(full_path=True))
    assert result == "ChangeList:\n* Create /module/file.txt"

    
def test_get_foci_1_no_file_ext_returns_str():
    result = get_cl1().get_foci(FormatOptions(no_file_ext=True))
    assert result == "ChangeList:\n* Create module/file"


def test_get_foci_1_filename_returns_str():
    result = get_cl1().get_foci(FormatOptions(file_name=True))
    assert result == "ChangeList:\n* Create file.txt"


def test_get_foci_1_filename_plus_no_file_ext_returns_str():
    result = get_cl1().get_foci(FormatOptions(file_name=True, no_file_ext=True))
    assert result == "ChangeList:\n* Create file"
