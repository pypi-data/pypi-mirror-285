"""Workspace XML file reader methods.
"""
from xml.etree.ElementTree import Element, ParseError, fromstring

from changelist_foci.change_data import ChangeData
from changelist_foci.changelist_data import ChangelistData
from changelist_foci.xml_reader import _read_bool_from, filter_by_tag, get_attr, get_attr_or


def read_workspace_changelists(workspace_xml: str) -> list[ChangelistData]:
    """
    Parse the Workspace XML file and obtain all ChangeList Data in a list.

    Parameters:
    - workspace_xml (str): The contents of the Workspace file, in xml format.
    
    Returns:
    list[ChangelistData] - The list of Changelists in the workspace file.
    """
    if (cl_manager := _extract_changelist_manager(workspace_xml)) is None:
        exit("ChangeList Manager was not found in the workspace file.")
    if len(cl_elements := _extract_list_elements(cl_manager)) < 1:
        exit("No Changelists were found!")
    return cl_elements  


def _extract_list_elements(changelist_manager: Element) -> list[ChangelistData]:
    """
    Given the Changelist Manager Element, obtain the list of List Elements.

    Parameters:
    - changelist_manager (Element): The ChangeList Manager XML Element.

    Returns:
    list[Element] - A List containing the Lists.
    """
    return [
        ChangelistData(
            id=get_attr(cl_element, 'id'),
            name=get_attr(cl_element, 'name'),
            changes=_extract_change_data(cl_element),
            comment=get_attr_or(cl_element, 'comment', ''),
            is_default=_read_bool_from(cl_element, 'default'),
        ) for cl_element in filter_by_tag(changelist_manager, 'list')
    ]


def _extract_changelist_manager(workspace_xml: str) -> Element | None:
    """
    Given the Workspace File string, extract the ChangeList XML Element.

    Parameters:
    - workspace_xml (str): The contents of the Workspace file, in xml format.
    
    Returns:
    Element - The Changelist Manager element, or None.
    """
    try:
        xml_root = fromstring(workspace_xml)
    except ParseError:
        return None
    for elem in filter_by_tag(xml_root, 'component'):
        try:
            if elem.attrib["name"] == 'ChangeListManager':
                return elem
        except KeyError:
            pass
    return None


_PROJECT_DIR_VAR = '$PROJECT_DIR$'
_PROJECT_DIR_LEN = len(_PROJECT_DIR_VAR)

def _filter_project_dir(path_str: str | None) -> str:
    """Filter the ProjectDir string at the beginning of the path.
    """
    if path_str is None:
        return None
    if path_str.startswith(_PROJECT_DIR_VAR):
        return path_str[_PROJECT_DIR_LEN:]
    return path_str


def _extract_change_data(list_element: Element) -> list[ChangeData]:
    """
    Given a ChangeList XML Element, obtain the List of Changes.

    Parameters:
    - list_element (Element): 

    Returns:
    list[ChangeData] - The list of structured ChangeData.
    """
    return [
        ChangeData(
            before_path=_filter_project_dir(get_attr(change, 'beforePath')),
            before_dir=get_attr(change, 'beforeDir'),
            after_path=_filter_project_dir(get_attr(change, 'afterPath')),
            after_dir=get_attr(change, 'afterDir'),
        ) for change in filter(lambda x: x.tag == 'change', list_element)
    ]

