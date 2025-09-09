from networkx import MultiDiGraph
from pyformlang.finite_automaton import DeterministicFiniteAutomaton,NondeterministicFiniteAutomaton
from typing import Set

def regex_to_dfa(regex: str) -> DeterministicFiniteAutomaton:
    pass

def graph_to_nfa(
  graph: MultiDiGraph, start_states: Set[int], final_states: Set[int]
) -> NondeterministicFiniteAutomaton:
    pass
