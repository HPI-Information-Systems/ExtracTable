import regex
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Pattern

from DataTypes import DataType
from pipeline.Transformer import Transformer

PRIMITIVES = {
    DataType.NUMBER: regex.compile(r'^([-+])?(([1-9]\d{0,2}([,]\d{3}){2,}([.]\d+)?)|([1-9]\d{0,2}[,]\d{3}[.]\d+)|([1-9]\d{0,2}([.]\d{3}){2,}([,]\d+)?)|([1-9]\d{0,2}[.]\d{3}[,]\d+)|(([1-9]\d*|0)(([.,])\d+)?))([eE]([+-])?\d+)?'),
    DataType.STRING: regex.compile(r'^[a-zA-Z]+'),
}

EMPTY = [
    regex.compile(r''),  # epsilon
    regex.compile(r'null', regex.IGNORECASE),  # null
    regex.compile(r'unknown', regex.IGNORECASE),  # unknown
    regex.compile(r'[?]+', regex.IGNORECASE),  # ???
    regex.compile(r'[-]+', regex.IGNORECASE),  # ---
    regex.compile(r'[*]+', regex.IGNORECASE),  # ***
    regex.compile(r'[#]+', regex.IGNORECASE),  # ###
    regex.compile(r'n/?a', regex.IGNORECASE),  # NA or N/A
    regex.compile(r'nan', regex.IGNORECASE)  # NaN
]

CONTINUOUS_WHITE_SPACE = regex.compile(r'\s{2,}')


class LineFeatureExtraction(Transformer):

    def __init__(self, known_patterns_file: Path = None):
        super().__init__()
        self.known_patterns = load_patterns(known_patterns_file) if known_patterns_file else []

    def transform(self, line: Dict[str, any]):
        self.call_next({
            **line,
            'solutionSpace': self.extract_line_features(line['solutionSpace'])
        })

    def get_known_pattern_match(self, field: str) -> Optional[int]:
        return next(
            (
                i_pattern
                for i_pattern, compiled_pattern in enumerate(self.known_patterns)
                if compiled_pattern.fullmatch(field)
            ),
            None
        )

    def get_field_pattern_components(self, field: str) -> List[Dict[str, any]]:
        if matches_empty(field):
            return [create_empty(field)]
        known_pattern_match = self.get_known_pattern_match(field)
        if not (known_pattern_match is None):
            return [create_known(known_pattern_match)]
        cursor_position = 0
        patterns = []
        while cursor_position < len(field):
            pattern, length = describe(field[cursor_position:])
            patterns.append(pattern)
            cursor_position += length
        return merge_other_patterns(patterns)

    def extract_field_features(self, field: str) -> Dict[str, any]:
        pattern_components = self.get_field_pattern_components(field)
        return {
            'patternComponents': pattern_components,
            'pattern': get_pattern(pattern_components),
            'hasContinuousWhiteSpace': has_continuous_white_space(field),
            'content': field
        }

    def extract_line_features(self, solution_space: List[Dict[str, any]]) -> List[Dict[str, any]]:
        return [
            {
                **possible_solution,
                'fieldCount': len(possible_solution['parsed']),
                'fields': [self.extract_field_features(field) for field in possible_solution['parsed']]
            }
            for possible_solution in solution_space
        ]


def matches_empty(field: str) -> bool:
    return any(
        compiled_pattern.fullmatch(field)
        for compiled_pattern in EMPTY
    )


def load_patterns(known_patterns_file: Path) -> List[Pattern]:
    with open(known_patterns_file, mode='r') as file:
        return [regex.compile(line.rstrip(), regex.UNICODE) for line in file if line[0] != '#']


def get_number_precision(string: str) -> Dict[str, int]:
    string = string[int(string[0] in ['-', '+']):]
    point_index = max(
        (
            string.rfind(point_candidate)
            for point_candidate in ['.', ',']
            if string.count('point_candidate') == 1
        ),
        default=-1
    )
    decimal = len(string) if (point_index == -1) else point_index
    return {
        'decimal': decimal,
        'float': len(string) - decimal - (point_index != -1)
    }


def describe(string: str) -> Tuple[Dict[str, any], int]:
    primitive_match = {
        data_type: regex.search(string)
        for data_type, regex in PRIMITIVES.items()
    }
    if not any(primitive_match.values()):
        return create_other(string[0])
    if primitive_match[DataType.NUMBER]:
        return create_number(primitive_match[DataType.NUMBER].group())
    if primitive_match[DataType.STRING]:
        return create_string(primitive_match[DataType.STRING].group())


def create_other(value: str) -> Tuple[Dict[str, any], int]:
    return {'type': DataType.OTHER, 'value': value}, len(value)


def create_number(value: str) -> Tuple[Dict[str, any], int]:
    return {
               'type': DataType.NUMBER,
               'precision': get_number_precision(value),
               'isNegative': value[0] == '-'
           }, len(value)


def create_string(value: str) -> Tuple[Dict[str, any], int]:
    return {'type': DataType.STRING, 'contentLength': len(value)}, len(value)


def create_known(value: int) -> Dict[str, any]:
    return {'type': DataType.KNOWN, 'value': value}


def create_empty(value: str) -> Dict[str, any]:
    return {'type': DataType.EMPTY, 'value': value}


def merge_other_patterns(patterns: List[Dict[str, any]]) -> List[Dict[str, any]]:
    value = ''
    merged_patterns = []
    for pattern in patterns:
        if pattern['type'] == DataType.OTHER:
            value += pattern['value']
        else:
            if value:
                merged_patterns.append(create_other(value)[0])
                value = ''
            merged_patterns.append(pattern)
    if value:
        merged_patterns.append(create_other(value)[0])
    return merged_patterns


def has_continuous_white_space(field: str) -> bool:
    return bool(CONTINUOUS_WHITE_SPACE.search(field.expandtabs()))


def get_pattern(pattern_components: List[Dict[str, any]]) -> str:
    return ','.join([
        pattern_component['type'].value + str(pattern_component['value']) if pattern_component['type'] == DataType.KNOWN else pattern_component['type'].value
        for pattern_component in pattern_components
    ])
