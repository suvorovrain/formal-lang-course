import pytest
from project.graph_utils import get_graph_info, save_two_cycles_graph
import os

def test_get_graph_info():
    graph_info = get_graph_info("bzip")
    assert graph_info.nodes_number == 632
    assert graph_info.edges_number == 556
    assert graph_info.labels == ['d','a']

def test_save_two_cycles_graph():
    save_two_cycles_graph(5,5,("a","d"),"tests/test_task1_result.dot")
    try:
        with open("tests/testdata/test_task1.dot", "r") as expected_graph:
            with open("tests/test_task1_result.dot", "r") as result_graph:
                assert expected_graph.read() == result_graph.read()
    finally:
        os.remove("tests/test_task1_result.dot")
