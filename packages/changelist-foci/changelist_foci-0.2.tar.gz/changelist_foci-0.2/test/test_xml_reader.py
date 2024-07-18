"""Testing XML Reader Methods.
"""
from xml.etree.ElementTree import fromstring

from test import get_multi_changelist_xml, get_no_changelist_xml, get_simple_changelist_xml
from changelist_foci.xml_reader import filter_by_tag


def test_filter_by_tag_no_changelist_returns_empty():
    root_elem = fromstring(get_no_changelist_xml())
    # There are no List Elements
    assert len(list(filter_by_tag(root_elem, 'list'))) == 0
    # There are no Change Elements
    assert len(list(filter_by_tag(root_elem, 'change'))) == 0
               

def test_filter_by_tag_simple_returns_1_list_1_change():
    root_elem = fromstring(get_simple_changelist_xml())
    # There are no List Elements
    assert len(list(filter_by_tag(root_elem, 'list'))) == 1
    # There are no Change Elements
    assert len(list(filter_by_tag(root_elem, 'change'))) == 1
               

def test_filter_by_tag_multi_returns_2_list_3_changes():
    root_elem = fromstring(get_multi_changelist_xml())
    # There are no List Elements
    assert len(list(filter_by_tag(root_elem, 'list'))) == 2
    # There are no Change Elements
    assert len(list(filter_by_tag(root_elem, 'change'))) == 3
