import logging
from _csv import writer
from itertools import groupby
from operator import itemgetter
from pathlib import Path
from typing import List, Dict, Tuple

from networkx import MultiDiGraph, bellman_ford_path, path_graph

from pipeline.Consumer import Consumer

RANKING = [
    {'name': 'recognizedPatternRatio', 'ascending': False},  # prefer higher recognized pattern ratio
    {'name': 'cleanColCount', 'ascending': False},  # prefer higher clean col count
    {'name': 'patternComponentPerFieldNormalized', 'ascending': False},  # 1 -> 1 component, 0.5 -> 2 components ...
    {'name': 'storedColCount', 'ascending': True},  # prefer lower stored columns
]


class TableSelection(Consumer):

    def __init__(self, output_file_path: Path, min_table_consistency: float = 0, use_heuristic: bool = False, save: bool = True):
        super().__init__()
        self.min_table_consistency = min_table_consistency
        self.table_graph = MultiDiGraph()
        self.last_table_line = 0
        self.use_heuristic = use_heuristic
        self.output_file_path = output_file_path
        self.save = save

    def consume(self, table_candidate: Dict[str, any]):
        if table_candidate['dataConsistency'] >= self.min_table_consistency:
            self.add_table_candidate_to_graph(table_candidate)

    def add_table_candidate_to_graph(self, table_candidate: Dict[str, any]):
        self.last_table_line = max(self.last_table_line, table_candidate['to'] + 1)
        self.table_graph.add_edge(**create_edge(table_candidate))

    def reached_end(self):
        if not self.table_graph.nodes:
            logging.info('No tables found!')
            return None
        selected_tables = self.select_tables()
        if self.save:
            store_selected_tables(selected_tables, self.output_file_path)
        return selected_tables if not self.save else [
            {
                k: v
                for k, v in table.items()
                if k != 'content'
            }
            for table in selected_tables
        ]

    def prepare_graph(self):
        self.table_graph.add_node(0)
        self.connect_all_nodes()

    def select_tables(self) -> List[Dict[str, any]]:
        return self.select_tables_using_heuristic() if self.use_heuristic else self.select_tables_using_shortest_path()

    def select_tables_using_heuristic(self) -> List[Dict[str, any]]:
        table_candidates = sorted(
            (edge[2] for edge in self.table_graph.edges(data=True)),
            key=lambda candidate: (candidate['weight'], *tuple(-1 * int(not criteria['ascending']) * candidate[criteria['name']] for criteria in RANKING))
        )
        selected_tables = []
        while table_candidates:
            next_table = table_candidates[0]
            lines = range(next_table['from'], next_table['to'] + 1)
            selected_tables.append(next_table)
            table_candidates = [
                table_candidate
                for table_candidate in table_candidates
                if not any(
                    candidate_line in lines
                    for candidate_line in range(table_candidate['from'], table_candidate['to'] + 1)
                )
            ]
        return selected_tables

    def select_tables_using_shortest_path(self) -> List[Dict[str, any]]:
        self.prepare_graph()
        selected_line_nodes = bellman_ford_path(self.table_graph, 0, self.last_table_line)
        solution_graph = path_graph(selected_line_nodes, create_using=MultiDiGraph)
        edge_candidates = self.get_edge_candidates(solution_graph)
        return [pick_best_candidate(candidates) for candidates in edge_candidates]

    def get_edge_candidates(self, solution_graph: MultiDiGraph):
        path_without_zero_weight_edges = [
            [candidate for candidate in self.table_graph.get_edge_data(edge[0], edge[1]).values() if candidate['weight']]
            for edge in solution_graph.edges()
        ]
        return [
            min(((k, list(v)) for k, v in groupby(sorted(edge_candidates, key=itemgetter('weight')), itemgetter('weight'))), key=itemgetter(0))[1]
            for edge_candidates in path_without_zero_weight_edges
            if edge_candidates
        ]

    def connect_all_nodes(self):
        nodes = sorted(self.table_graph.nodes)
        for iFrom, fromNode in enumerate(nodes):
            for toNode in nodes[iFrom + 1:]:
                self.table_graph.add_edge(fromNode, toNode, weight=0)


def pick_best_candidate(candidates: List[Dict[str, any]]) -> Dict[str, any]:
    if len(candidates) == 1:
        return candidates[0]
    return sorted(
        candidates,
        key=lambda candidate: tuple(-1 * int(not criteria['ascending']) * candidate[criteria['name']] for criteria in RANKING)
    )[0]


def get_weight(table_candidate: Dict[str, any]) -> float:
    return - table_candidate['dataConsistency'] * table_candidate['dataRows']**2 \
           - table_candidate['headerConsistency'] * ((table_candidate['headerRows'] + table_candidate['dataRows'])**2 - table_candidate['dataRows']**2) \
           - 0.001 * (bool(table_candidate['headerRows'])) \
           + 0.00000001


def print_result(selected_tables: List[Dict[str, any]]):
    [logging.info(str({k: v for k, v in table.items() if not (k in ['weight', 'content'])})) for table in selected_tables]
    logging.info('Found ' + str(len(selected_tables)) + ' tables')


def create_edge(table_candidate: Dict[str, any]) -> Dict:
    return {
        **table_candidate,
        'u_for_edge': table_candidate['from'],
        'v_for_edge': table_candidate['to'] + 1,
        'weight': get_weight(table_candidate),
    }


def store_selected_tables(tables: List[Dict[str, any]], output_file_path: Path):
    [
        store_table(
            output_file_path / '_'.join([
                str(table['from'] + 1),
                str(table['to'] + 1),
                bin_key_to_str(table['binKey']),
                str(table['headerRows']),
                '.csv'
            ]),
            table['content']
        )
        for table in tables
    ]


def bin_key_to_str(bin_key: Tuple) -> str:
    return '_'.join([str(value).replace('\\', 'b_slash').replace('/', 'slash') for value in bin_key])


def store_table(target: Path, content: List[List[str]]):
    with open(target, 'w') as file:
        csv_writer = writer(file)
        [csv_writer.writerow(row) for row in content]
