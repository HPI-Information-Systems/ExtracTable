import math
from collections import Counter
from itertools import groupby
from operator import itemgetter
from statistics import mean
from typing import List, Dict

from DataTypes import DataType


def get_table_consistency(
        rows: List[Dict[str, any]],
        col_count: int,
        min_col_consistency: float,
        max_continuous_white_spaces: float,
        final: bool = False
) -> float:
    columns = get_cleaned_columns(rows, col_count)
    columns = [column for column in columns if sum(field['pattern'] != DataType.EMPTY.value for field in column) > 1]
    if not columns:
        return -1
    consistent_columns = get_consistent_columns(columns, min_col_consistency, max_continuous_white_spaces)
    min_required_consistent_columns = max(2, math.floor(math.log2(len(columns)))) if final or len(columns) > 1 else 1
    if consistent_columns < min_required_consistent_columns:
        return 0
    return consistent_columns / len(columns) * homogeneity(count_by(rows, 'type')) * mean(
        [get_uniformity_score(column) for column in columns]
    )


def get_consistent_columns(columns: List[List[Dict[str, any]]], min_col_consistency: float,
                           max_multi_spaces: float) -> int:
    pattern_consistent_column_indexes = get_pattern_consistent_column_indexes(columns, min_col_consistency)
    columns_without_multi_spaces_indexes = get_columns_without_multi_spaces_indexes(columns, max_multi_spaces)
    return len(set(pattern_consistent_column_indexes) & set(columns_without_multi_spaces_indexes))


def get_pattern_consistent_column_indexes(columns: List[List[Dict[str, any]]], min_col_consistency: float) -> List[int]:
    column_counters = [count_by(column, 'pattern') for column in columns]
    column_counters_without_empty = [
        {
            pattern: count
            for pattern, count in column_counter.items()
            if pattern != DataType.EMPTY.value
        }
        for i_column, column_counter in enumerate(column_counters)
    ]
    column_consistencies = [homogeneity(column_counter) for column_counter in column_counters_without_empty]
    return [i_column for i_column, consistency in enumerate(column_consistencies) if consistency >= min_col_consistency]


def get_columns_without_multi_spaces_indexes(columns: List[List[Dict[str, any]]], max_multi_spaces: float) -> List[int]:
    column_ws = [sum(field['hasContinuousWhiteSpace'] for field in column) / len(column) for column in columns]
    return [i_column for i_column, relative_ws in enumerate(column_ws) if relative_ws <= max_multi_spaces]


def get_number_consistency(number_components: List[Dict[str, any]]) -> float:
    is_float_counter = dict(Counter([
        bool(number_component['precision']['float'])
        for number_component in number_components
    ]))
    return homogeneity(is_float_counter)


def get_string_consistency(_) -> float:
    return 1.0


def get_other_consistency(other_components: List[Dict[str, any]]) -> float:
    return homogeneity(count_by(other_components, 'value'))


def get_known_consistency(_) -> float:
    return 1.0  # if it's known, it can only be all the same


def get_empty_consistency(empty_components) -> float:
    return homogeneity(count_by(empty_components, 'value'))


type_consistencies = {
    DataType.STRING: get_string_consistency,
    DataType.NUMBER: get_number_consistency,
    DataType.OTHER: get_other_consistency,
    DataType.KNOWN: get_known_consistency,
    DataType.EMPTY: get_empty_consistency
}


def get_pattern_uniformity(fields: List[Dict[str, any]]) -> float:
    pattern_component_types = [pattern_component['type'] for pattern_component in fields[0]['patternComponents']]
    return min(
        [
            type_consistencies[component_type]([field['patternComponents'][i_component] for field in fields])
            for i_component, component_type in enumerate(pattern_component_types)
        ]
    )


def get_uniformity_score(column: List[Dict[str, any]]) -> float:
    # if a column has only one field with content, it will be punished
    column_without_empty = [field for field in column if field['pattern'] != DataType.EMPTY.value]
    pattern_uniformities = [
        get_pattern_uniformity(fields) * len(fields) / len(column_without_empty)
        for pattern, fields in [(k, list(v)) for k, v in groupby(sorted(column_without_empty, key=itemgetter('pattern')), itemgetter('pattern'))]
    ]
    return max(pattern_uniformities, default=1)


def norm(counter: Dict[any, int]) -> Dict[any, float]:
    total = sum(counter.values())
    return {key: count / total for key, count in counter.items()}


def homogeneity(counter: Dict[any, int]) -> float:
    return sum([normalized_count ** 2 for normalized_count in norm(counter).values()])


def without_empty_columns(columns: List[List[Dict[str, any]]]) -> List[List[Dict[str, any]]]:
    return [
        column
        for column in columns
        if any(field['content'] for field in column)
    ]


def without_other_only_columns(columns: List[List[Dict[str, any]]]) -> List[List[Dict[str, any]]]:
    return [
        column
        for column in columns
        if (any(field['pattern'] != DataType.OTHER.value for field in column)
            or len(set(field['patternComponents'][0]['value'] for field in column)) > 1)
    ]


def get_cleaned_columns(rows: List[Dict[str, any]], col_count: int) -> List[List[Dict[str, any]]]:
    columns = [[row['fields'][i_col] for row in rows] for i_col in range(col_count)]
    columns = without_empty_columns(columns)
    columns = without_other_only_columns(columns)
    return columns


def count_by(values: List[Dict[str, any]], key: str) -> Dict[any, int]:
    return dict(Counter([d[key] for d in values]))
