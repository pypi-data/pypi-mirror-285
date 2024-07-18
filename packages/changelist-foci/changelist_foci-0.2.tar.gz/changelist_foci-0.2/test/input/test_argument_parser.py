"""Testing Argument Parser Methods.
"""
from changelist_foci.input.argument_parser import parse_arguments


def test_parse_arguments_empty_list():
    result = parse_arguments('')
    assert result.changelist_name == None
    assert result.workspace_path is None
    assert not result.full_path
    assert not result.no_file_ext
    assert not result.filename


def test_parse_arguments_change_list_main():
    result = parse_arguments(['--changelist', 'Main'])
    assert result.changelist_name == 'Main'
    assert result.workspace_path is None
    assert not result.full_path
    assert not result.no_file_ext
    assert not result.filename


def test_parse_arguments_filename_plus_no_file_ext():
    result = parse_arguments(['-fx'])
    assert result.changelist_name is None
    assert result.workspace_path is None
    assert not result.full_path
    assert result.no_file_ext
    assert result.filename


def test_parse_arguments_filename():
    result = parse_arguments(['-f'])
    assert result.changelist_name is None
    assert result.workspace_path is None
    assert not result.full_path
    assert not result.no_file_ext
    assert result.filename


def test_parse_arguments_no_file_ext():
    result = parse_arguments(['-x'])
    assert result.changelist_name is None
    assert result.workspace_path is None
    assert not result.full_path
    assert result.no_file_ext
    assert not result.filename


def test_parse_arguments_full_path():
    result = parse_arguments(['--full-path'])
    assert result.changelist_name is None
    assert result.workspace_path is None
    assert result.full_path
    assert not result.no_file_ext
    assert not result.filename


def test_parse_arguments_changelist_filename():
    result = parse_arguments(['--changelist', "Main", '-f'])
    assert result.changelist_name == 'Main'
    assert result.workspace_path is None
    assert not result.full_path
    assert not result.no_file_ext
    assert result.filename
