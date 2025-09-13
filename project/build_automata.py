from networkx import MultiDiGraph
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
    State,
)
from typing import Set
import pyformlang.regular_expression


def regex_to_dfa(regex: str) -> DeterministicFiniteAutomaton:
    return (
        pyformlang.regular_expression.Regex(regex).to_epsilon_nfa().to_deterministic()
    )


def graph_to_nfa(
    graph: MultiDiGraph, start_states: Set[int], final_states: Set[int]
) -> NondeterministicFiniteAutomaton:
    nfa = NondeterministicFiniteAutomaton.from_networkx(graph)
    if len(start_states) > 0:
        for s in start_states:
            nfa.add_start_state(State(s))
    else:
        for v in graph.nodes:
            nfa.add_start_state(State(v))

    if len(final_states) > 0:
        for s in final_states:
            nfa.add_final_state(State(s))
    else:
        for v in graph.nodes:
            nfa.add_final_state(State(v))
    return nfa
