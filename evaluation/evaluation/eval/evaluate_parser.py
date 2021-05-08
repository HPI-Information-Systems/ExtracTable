from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Dict, Any, List, Iterator, Set

from flatten_dict import flatten
from pymongo import MongoClient
from pymongo.database import Database

from utils.overlap import Overlap
from utils.parser import Parser
from utils.table_file_cursor import TableFileCursor
from utils.utils import parse_table_files, get_content, stringify_dict


def is_match(got: List[str], expected: Dict[str, Any]) -> bool:
    if expected['skip']:
        return not any(got)
    else:
        return got == expected['post-processed'] or got == expected['parsed']


def collect_base_metrics(returned_lines: Iterator, expected_lines: Iterator) -> List[Dict[str, Any]]:
    return [
        {
            'confusion': (bool(got), expected['isPartOfTable']),
            'isCorrectlyParsed': is_match(got, expected) if (got and expected['isPartOfTable']) else None,
            'missingType': expected['rowType'] if (not got and expected['isPartOfTable']) else None
        }
        for got, expected in zip(returned_lines, expected_lines)
    ]


def aggregate_line_metrics(metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
    correctly_classified_table_lines = [metric for metric in metrics if all(metric['confusion'])]
    return {
        'lineCount': len(metrics),
        'confusion': sum((Counter({metric['confusion']: 1}) for metric in metrics), Counter()),
        'correctlyParsed': mean(int(bool(metric['isCorrectlyParsed'])) for metric in metrics if metric['confusion'][1]),  # cannot be empty, as each file must have at least one table line
        'correctlyParsedClean': mean(int(bool(metric['isCorrectlyParsed'])) for metric in correctly_classified_table_lines) if correctly_classified_table_lines else None,
        'missingTypes': sum((Counter({metric['missingType']: 1}) for metric in metrics), Counter())
    }


def jaccard_index(set_a: Set, set_b: Set) -> float:
    return len(set_a & set_b) / len(set_a | set_b)


def expand_table_jaccard(table: Dict[str, Any], other_tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            **other_table,
            'jaccard': jaccard_index(set(range(table['from'], table['to'] + 1)), set(range(other_table['from'], other_table['to'] + 1)))
        }
        for other_table in other_tables
    ]


def get_table_coverage(table: Dict[str, Any], other_table: Dict[str, Any]) -> float:
    if other_table is None:
        return 0.0
    table_range_set = set(range(table['from'], table['to'] + 1))
    other_table_range_set = set(range(other_table['from'], other_table['to'] + 1))
    return len(table_range_set & other_table_range_set) / len(table_range_set)


def get_f1(expected_table: Dict[str, Any], got_table: Dict[str, Any]) -> float:
    expected_table_lines = set(range(expected_table['from'], expected_table['to'] + 1))
    got_table_lines = set(range(got_table['from'], got_table['to'] + 1))
    return 2 * len(expected_table_lines & got_table_lines) / (len(expected_table_lines) + len(got_table_lines))


def calculate_f1_matrix(
        expected_tables: List[Dict[str, Any]],
        got_tables: List[Dict[str, Any]]
) -> List[List[float]]:
    return [
        [
           get_f1(expected_table, got_table)
           for got_table in got_tables
        ]
        for expected_table in expected_tables
    ]


def map_score_to_overlap(f1: float) -> Overlap:
    if f1 == 1.0:
        return Overlap.LARGE
    if 0 < f1 < 1.0:
        return Overlap.MAJOR
    return Overlap.NONE


def f1_matrix_to_overlap_matrix(f1_matrix: List[List[float]]) -> List[List[Overlap]]:
    return [
        [
            map_score_to_overlap(f1)
            for f1 in expected_table
        ]
        for expected_table in f1_matrix
    ]


def get_match_type(overlap_matrix: List[List[Overlap]], expected_table: int) -> str:
    if Overlap.LARGE in overlap_matrix[expected_table]:
        return 'correct'
    if all(overlap == Overlap.NONE for overlap in overlap_matrix[expected_table]):
        return 'missed'
    if overlap_matrix[expected_table].count(Overlap.MAJOR) == 1:
        got_table = next(i_got for i_got, overlap in enumerate(overlap_matrix[expected_table]) if overlap == Overlap.MAJOR)
        if sum(overlap_matrix[i_expected][got_table] == Overlap.MAJOR for i_expected in range(len(overlap_matrix))) == 1:
            return 'partial'
        return 'underSegmented'
    else:
        return 'overSegmented'


def aggregate_table_metrics(
        metrics: List[Dict[str, Any]],
        expected_tables: List[Dict[str, Any]],
        got_tables: List[Dict[str, Any]]
) -> Dict[str, Any]:
    f1_matrix = calculate_f1_matrix(expected_tables, got_tables)
    overlap_matrix = f1_matrix_to_overlap_matrix(f1_matrix)
    metrics_per_table = []
    for i_table, table in enumerate(expected_tables):
        table_metrics = metrics[table['from']:table['to'] + 1]
        correctly_classified_table_lines = [metric for metric in table_metrics if all(metric['confusion'])]
        expanded_got_tables = expand_table_jaccard(table, got_tables)
        match = max(expanded_got_tables, key=lambda other: other['jaccard'], default=None)
        metrics_per_table.append({
            'from': table['from'],
            'to': table['to'],
            'rowCount': len(table_metrics),
            'confusion': sum((Counter({metric['confusion']: 1}) for metric in table_metrics), Counter()),
            'correctlyParsed': mean(int(bool(metric['isCorrectlyParsed'])) for metric in table_metrics if metric['confusion'][1]),
            'correctlyParsedClean': mean(int(bool(metric['isCorrectlyParsed'])) for metric in correctly_classified_table_lines) if correctly_classified_table_lines else None,
            'missingTypes': sum((Counter({metric['missingType']: 1}) for metric in table_metrics), Counter()),
            'type': table['type'],
            'jaccard': match['jaccard'] if match else 0,
            'coverage': get_table_coverage(table, match) if match else 0,
            'matchedRowCount': match['to'] - match['from'] + 1 if match else 0,
            'spanning': sum(bool(expanded_got['jaccard']) for expanded_got in expanded_got_tables),
            'matchType': get_match_type(overlap_matrix, i_table)
        })
    return {
        'tables': metrics_per_table,
        'expected': len(expected_tables),
        'got': len(got_tables),
        'eager': sum(not any(expected['jaccard'] for expected in expand_table_jaccard(table, expected_tables)) for table in got_tables),
        'falsePositive': sum(
            all(overlap_matrix[i_expected][i_got] == Overlap.NONE for i_expected in range(len(expected_tables)))
            for i_got in range(len(got_tables))
        )
    }


def get_file_type(file: Dict[str, Any]) -> str:
    if file['type'] == 'simple':
        return 'simple'
    return 'complex_' + ('single' if len(file['tables']) == 1 else 'multi')


def aggregate_file_metrics(file: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'fileType':  get_file_type(file),
        'incomplete': file.get('incomplete', False)
    }


def collect_metrics(db: Database, file: Dict[str, Any], tables_dir: Path) -> Dict[str, Any]:
    table_files = parse_table_files([*tables_dir.iterdir()]) if tables_dir.exists() else []
    base_metrics = collect_base_metrics(TableFileCursor(table_files), get_content(db, file))
    return {
        'lineMetrics': aggregate_line_metrics(base_metrics),
        'tableMetrics': aggregate_table_metrics(base_metrics, file['tables'], table_files),
        'fileMetrics': aggregate_file_metrics(file)
    }


def generate_looser_base_metrics(expected_lines: Iterator) -> List[Dict[str, Any]]:
    return [
        {
            'confusion': (bool(not expected['isPartOfTable']), expected['isPartOfTable']),
            'isCorrectlyParsed': None,
            'missingType': expected['rowType'] if expected['isPartOfTable'] else None
        }
        for expected in expected_lines
    ]


def generate_looser_metrics(db: Database, file: Dict[str, Any]) -> Dict[str, Any]:
    base_metrics = generate_looser_base_metrics(get_content(db, file))
    return {
        'lineMetrics': aggregate_line_metrics(base_metrics),
        'tableMetrics': aggregate_table_metrics(base_metrics, file['tables'], []),
        'fileMetrics': aggregate_file_metrics(file)
    }


def evaluate_parser(mongo_uri: str, database_name: str, file: Dict[str, Any], parser: Parser, tables_dir: Path):
    with MongoClient(mongo_uri) as mongo:
        db = mongo[database_name]
        metric = db['metrics'].find_one(
            filter={'fileId': str(file['_id']), 'parser': parser.value},
            projection=['status']
        )
        metrics = collect_metrics(db, file, tables_dir) if metric['status'] == 'success' else generate_looser_metrics(db, file)
        db['metrics'].update_one(
            filter={'_id': metric['_id']},
            update={'$set': stringify_dict(flatten(metrics, reducer='underscore'))}
        )


def evaluate_parser_unpack(args):
    return evaluate_parser(*args)
