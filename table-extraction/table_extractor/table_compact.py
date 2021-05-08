from statistics import mean
from typing import List, Dict

from Combinations import Combinations
from DataTypes import DataType
from table_consistency import get_table_consistency


def compact_rows(
        rows: List[List[Dict[str, any]]],
        col_count: int,
        min_col_consistency: float,
        max_continuous_white_spaces: float,
        compact_instructions: List[int]
) -> List[List[Dict[str, any]]]:
    if is_compact(rows):
        return rows
    else:
        return compact(rows, col_count, min_col_consistency, max_continuous_white_spaces, compact_instructions)


def compact(
        rows: List[List[Dict[str, any]]],
        col_count: int,
        min_col_consistency: float,
        max_continuous_white_spaces: float,
        compact_instructions: List[int]
) -> List[List[Dict[str, any]]]:
    interpretations_per_row = [len(row) for row in rows]
    for row in rows:
        for interpretation in row:
            interpretation['consistency'] = -1
    for combination in Combinations(interpretations_per_row):
        table = build_table(rows, combination)
        consistency = get_table_consistency(table, col_count, min_col_consistency, max_continuous_white_spaces)
        update_consistency(table, consistency)
    return get_best_n_interpretation_candidates(rows, compact_instructions)

def is_compact(rows: List[List[Dict[str, any]]]):
    return all(len(row) == 1 for row in rows)


def update_consistency(rows: List[Dict[str, any]], consistency: float):
    for row in rows:
        row['consistency'] = max(row['consistency'], consistency)


def get_best_n_interpretation_candidates(
        rows: List[List[Dict[str, any]]],
        compact_instructions: List[int]
) -> List[List[Dict[str, any]]]:
    return [
        sorted(
            interpretations,
            key=lambda interpretation: (
                interpretation['consistency'],
                sum(
                    field['patternComponents'][0]['type'] != DataType.OTHER
                    for field in interpretation['fields']
                    if len(field['patternComponents']) == 1 and field['patternComponents'][0]['type'] != DataType.EMPTY
                ),
                mean(1 / len(field['patternComponents']) for field in interpretation['fields'])
            ),
            reverse=True
        )[:compact_instructions[i_row]]
        for i_row, interpretations in enumerate(rows)
    ]


def build_table(rows: List[List[Dict[str, any]]], selection: List[int]) -> List[Dict[str, any]]:
    return [interpretations[selection[i_row]] for i_row, interpretations in enumerate(rows)]


def get_max_consistency(
        rows: List[List[dict]],
        col_count: int,
        min_col_consistency: float,
        max_continuous_white_spaces: float,
) -> float:
    interpretations_per_row = [len(row) for row in rows]
    return max([
        get_table_consistency(
            build_table(rows, combination),
            col_count,
            min_col_consistency,
            max_continuous_white_spaces
        )
        for combination in Combinations(interpretations_per_row)
    ])
