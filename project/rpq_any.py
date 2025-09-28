from networkx import MultiDiGraph
from pyformlang.finite_automaton import (
    NondeterministicFiniteAutomaton,
    State,
    Symbol,
)
from typing import Set, Iterable, Dict, Any
from scipy.sparse import (
    csr_matrix,
    kron,
    eye,
    lil_matrix,
)
from project.build_automata import graph_to_nfa, regex_to_dfa


class AdjacencyMatrixFA:
    matrices: Dict[Symbol, csr_matrix]
    n_states: int
    start_states: Set[State]
    final_states: Set[State]
    state_index_map: Dict[Any, int]

    def __init__(self, automaton: NondeterministicFiniteAutomaton):
        self.matrices: Dict[Symbol, csr_matrix] = {}
        self.start_states = automaton.start_states
        self.final_states = automaton.final_states

        idx = {s: i for i, s in enumerate(automaton.states)}
        self.state_index_map = idx
        self.n_states = len(automaton.states)

        tmp_mats: Dict[Symbol, lil_matrix] = {}
        fadict = automaton.to_dict()
        for src, trans in fadict.items():
            for lbl, dests in trans.items():
                if isinstance(dests, State):
                    dests = {dests}
                for dest in dests:
                    i, j = idx[src], idx[dest]
                    if lbl is not None:
                        if lbl not in tmp_mats:
                            tmp_mats[lbl] = lil_matrix(
                                (self.n_states, self.n_states), dtype=bool
                            )
                        tmp_mats[lbl][i, j] = True
        for lbl, M in tmp_mats.items():
            self.matrices[lbl] = M.tocsr()

    def accepts(self, word: Iterable[Symbol]) -> bool:
        cur_vec = lil_matrix((1, self.n_states), dtype=bool)
        for s in self.start_states:
            cur_vec[0, self.state_index_map[s]] = True
        cur_vec = cur_vec.tocsr()

        for symbol in word:
            A = self.matrices.get(symbol)
            if A is None:
                return False
            cur_vec = (cur_vec @ A).astype(bool)
            if cur_vec.nnz == 0:
                return False

        fin_vec = lil_matrix((self.n_states, 1), dtype=bool)
        for s in self.final_states:
            fin_vec[self.state_index_map[s], 0] = True
        fin_vec = fin_vec.tocsr()

        return (cur_vec @ fin_vec).nnz > 0

    def transitive_closure(self) -> csr_matrix:
        rclosure = csr_matrix((self.n_states, self.n_states), dtype=bool)
        for M in self.matrices.values():
            rclosure = rclosure.maximum(M.astype(bool))

        closure = rclosure.copy() + eye(self.n_states, dtype=bool, format="csr")

        changed = True
        while changed:
            new_reach = closure.maximum(closure @ rclosure)
            changed = new_reach.nnz != closure.nnz
            closure = new_reach

        return closure

    def is_empty(self) -> bool:
        closure = self.transitive_closure()

        src_vec = lil_matrix((1, self.n_states), dtype=bool)
        for s in self.start_states:
            src_vec[0, self.state_index_map[s]] = True
        src_vec = src_vec.tocsr()

        fin_vec = lil_matrix((self.n_states, 1), dtype=bool)
        for s in self.final_states:
            fin_vec[self.state_index_map[s], 0] = True
        fin_vec = fin_vec.tocsr()

        return (src_vec @ closure @ fin_vec).nnz == 0


def pair_index(i: int, j: int, n2: int) -> int:
    return i * n2 + j


def intersect_automata(
    automaton1: AdjacencyMatrixFA, automaton2: AdjacencyMatrixFA
) -> AdjacencyMatrixFA:
    common = set(automaton1.matrices) & set(automaton2.matrices)
    mats: Dict[Symbol, csr_matrix] = {}
    for lbl in common:
        mats[lbl] = kron(
            automaton1.matrices[lbl].astype(bool),
            automaton2.matrices[lbl].astype(bool),
            format="csr",
        )

    n1, n2 = automaton1.n_states, automaton2.n_states
    start_states = {
        pair_index(automaton1.state_index_map[s1], automaton2.state_index_map[s2], n2)
        for s1 in automaton1.start_states
        for s2 in automaton2.start_states
    }
    final_states = {
        pair_index(automaton1.state_index_map[s1], automaton2.state_index_map[s2], n2)
        for s1 in automaton1.final_states
        for s2 in automaton2.final_states
    }

    nfa = NondeterministicFiniteAutomaton()
    for idx in range(n1 * n2):
        nfa.add_symbol(State(idx))
    for idx in start_states:
        nfa.add_start_state(State(idx))
    for idx in final_states:
        nfa.add_final_state(State(idx))
    for lbl, M in mats.items():
        coo = M.tocoo()
        for u, v in zip(coo.row, coo.col):
            nfa.add_transition(State(u), lbl, State(v))

    return AdjacencyMatrixFA(nfa)


def tensor_based_rpq(
    regex: str, graph: MultiDiGraph, start_nodes: set[int], final_nodes: set[int]
) -> set[tuple[int, int]]:
    regex_dfa = regex_to_dfa(regex)
    adj_regex = AdjacencyMatrixFA(regex_dfa)

    graph_nfa = graph_to_nfa(graph, start_states=start_nodes, final_states=final_nodes)
    adj_graph = AdjacencyMatrixFA(graph_nfa)

    intersect_res = intersect_automata(adj_graph, adj_regex)
    closure = intersect_res.transitive_closure()

    result = set()

    n2 = adj_regex.n_states
    for g_s in graph_nfa.start_states:
        i_gs = adj_graph.state_index_map[g_s]
        for g_f in graph_nfa.final_states:
            i_gf = adj_graph.state_index_map[g_f]
            for r_s in regex_dfa.start_states:
                i_rs = adj_regex.state_index_map[r_s]
                for r_f in regex_dfa.final_states:
                    i_rf = adj_regex.state_index_map[r_f]

                    src = pair_index(i_gs, i_rs, n2)
                    dst = pair_index(i_gf, i_rf, n2)

                    if closure[src, dst]:
                        result.add((g_s.value, g_f.value))
    return result
