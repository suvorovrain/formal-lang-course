from project.build_automata import regex_to_dfa


def test_regex_to_dfa_is_minimal():
    regex = "(a|aa)*"
    actual_dfa = regex_to_dfa(regex)
    min_dfa = actual_dfa.minimize()
    assert len(actual_dfa.states) == len(min_dfa.states)
