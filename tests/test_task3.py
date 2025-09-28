from project.build_automata import regex_to_dfa
from project.rpq_any import intersect_automata, AdjacencyMatrixFA


def test_intersection_shoul_be_empty_1():
    regex1 = "a b c"
    regex2 = "(a | c)*(a | b)*"
    dfa1 = regex_to_dfa(regex1)
    dfa2 = regex_to_dfa(regex2)
    adj1 = AdjacencyMatrixFA(dfa1)
    adj2 = AdjacencyMatrixFA(dfa2)
    inter = intersect_automata(adj1, adj2)
    assert inter.is_empty()


def test_intersection_shoul_be_empty_2():
    regex1 = "a b*"
    regex2 = "(a a)*"
    dfa1 = regex_to_dfa(regex1)
    dfa2 = regex_to_dfa(regex2)
    adj1 = AdjacencyMatrixFA(dfa1)
    adj2 = AdjacencyMatrixFA(dfa2)
    inter = intersect_automata(adj1, adj2)
    assert inter.is_empty()
