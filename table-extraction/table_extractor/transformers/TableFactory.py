import logging
from copy import deepcopy
from itertools import groupby
from statistics import mean
from typing import Dict, List, Tuple, Any, Optional

from Block import Block
from BlockFactory import BlockFactory
from DataTypes import DataType
from Table import Table
from pipeline.Transformer import Transformer
from table_consistency import get_cleaned_columns, get_table_consistency


class TableFactory(Transformer):

    def __init__(
            self,
            block_factory: BlockFactory,
            min_col_count: int = 1,
            min_data_rows: int = 1,
            max_header_rows: int = 1,
            use_strict_bin_key: bool = False,
            enable_post_processing: bool = True,
            final_max_continuous_white_spaces: float = 0.1,
            final_min_column_consistency: float = 0.5
    ):
        super().__init__()
        self.block_factory = block_factory
        self.min_col_count = min_col_count
        self.min_data_rows = min_data_rows
        self.max_header_rows = max_header_rows
        self.use_strict_bin_key = use_strict_bin_key
        self.enable_post_processing = enable_post_processing
        self.max_continuous_white_spaces = final_max_continuous_white_spaces
        self.min_column_consistency = final_min_column_consistency
        self.tables = {}  # bin_key -> table, bin_key is either field count, or field count/type/dialect|layoutKey

    def transform(self, line: Dict[str, any]):
        logging.info('Table factory received ' + str(line['index'] + 1))
        if is_styling_line(line['raw']):
            return
        interpretations_per_bin = self.group_interpretations_per_bin(line['solutionSpace'])
        represented_bin_keys = list(interpretations_per_bin.keys())
        self.open_discovered_tables(represented_bin_keys)
        self.close_unrepresented_tables(represented_bin_keys)
        self.update_tables(interpretations_per_bin)

    def reached_end(self):
        [self.close_table(bin_key) for bin_key in [*self.tables]]

    def on_table_candidate(self, bin_key: Tuple, header: Optional[Block], data: Block):
        if not self.is_valid_data(data):
            return
        header = self.is_valid_header(header) and header
        if header:
            self.on_table_candidate(bin_key, None, data)
        header_rows = len(header.compacted) if header else 0
        rows = [*(header.compacted if header else []), *data.compacted]
        clean_columns = get_cleaned_columns(rows, bin_key[0])
        if len(clean_columns) < self.min_col_count:
            return
        store_as_cleaned = self.enable_post_processing or (self.use_strict_bin_key and bin_key[1] == 'layout')
        rows = [
            {
                **row,
                'fields': [column[i_row] for column in clean_columns]
            }
            for i_row, row in enumerate(rows)
        ] if store_as_cleaned else rows
        data_consistency = get_table_consistency(data.compacted, data.col_count, self.min_column_consistency, self.max_continuous_white_spaces, True)
        from_index = header.compacted[0]['index'] if header else data.compacted[0]['index']
        to_index = data.compacted[-1]['index']
        self.call_next({
            'from': from_index,
            'to': to_index,
            'dataRows': len(data.compacted),
            'headerRows': header_rows,
            'content': get_content(rows, not self.enable_post_processing),
            'dataConsistency': data_consistency,
            'headerConsistency': get_table_consistency(header.compacted, header.col_count, self.min_column_consistency, self.max_continuous_white_spaces, True) if header_rows > 1 else data_consistency,
            'cleanColCount': len(clean_columns),
            'storedColCount': len(clean_columns) if store_as_cleaned else bin_key[0],
            'patternComponentPerFieldNormalized': get_pattern_components_per_field(data.compacted),
            'recognizedPatternRatio': get_recognized_pattern_ratio(data.compacted),
            'hasBorderDelimiter': has_border_delimiter(header, data),
            'binKey': bin_key
        })

    def update_tables(self, interpretations_per_bin: Dict[Tuple, List[Dict[str, any]]]):
        [
            self.tables[bin_key].add_row(interpretations)
            for bin_key, interpretations in interpretations_per_bin.items()
        ]

    def open_discovered_tables(self, represented_bin_keys: List[Tuple]):
        [
            self.open_table(bin_key)
            for bin_key in represented_bin_keys
            if not(bin_key in self.tables)
        ]

    def open_table(self, bin_key: Tuple):
        fallback = self.get_fallback_bin_key(bin_key, sorted(self.tables.keys(), key=lambda t: [*map(lambda tv: not(tv is 'None'), t)]))
        blocks = deepcopy(self.tables[fallback].blocks) if fallback else None
        self.tables[bin_key] = Table(bin_key, self.block_factory, self.on_table_candidate, blocks)

    def get_fallback_bin_key(self, bin_key: Tuple, represented_bin_keys: List[Tuple]) -> Optional[Tuple]:
        if not self.use_strict_bin_key or bin_key[1] != 'character' or bin_key[3] is 'None':
            return None
        # bin key has at least quotation and maybe escape
        has_escape = not(bin_key[4] is 'None')
        fallback_match = next((
            represented_bin_key
            for represented_bin_key in represented_bin_keys
            if (*bin_key[:3 + has_escape], *(('None',)*(1 + (not has_escape)))) == represented_bin_key
        ), None)  # this magic gets a represented binary key, that has no escape/ no quotation but matches otherwise
        if fallback_match or not has_escape:
            return fallback_match
        #  we failed finding a fallback for Q, E -> Q, None. Now try Q,E -> None, None
        has_escape = False
        return next((
            represented_bin_key
            for represented_bin_key in represented_bin_keys
            if (*bin_key[:3 + has_escape], *(('None',)*(1 + (not has_escape)))) == represented_bin_key
        ), None)

    def close_unrepresented_tables(self, represented_bin_keys: List[Tuple]):
        [
            self.close_table(bin_key)
            for bin_key, table in [*self.tables.items()]
            if not (bin_key in represented_bin_keys)
        ]

    def close_table(self, bin_key: Tuple):
        self.tables[bin_key].close()
        del self.tables[bin_key]

    def group_interpretations_per_bin(self, interpretations: List[Dict[str, any]]) -> Dict[Tuple, List[Dict[str, any]]]:
        interpretations_per_bin = {
            bin_key: list(interpretations)
            for bin_key, interpretations in groupby(sorted(interpretations, key=self.get_bin_key), self.get_bin_key)
            if bin_key[0] >= self.min_col_count
        }
        for bin_key in sorted(self.tables.keys(), key=lambda t: [*map(lambda tv: not(tv is None), t)]):
            if not (bin_key in interpretations_per_bin):
                fallback = self.get_fallback_bin_key(bin_key, [*interpretations_per_bin.keys()])
                if not (fallback is None):
                    interpretations_per_bin[bin_key] = interpretations_per_bin[fallback]
        return interpretations_per_bin

    def get_bin_key(self, interpretation: Dict[str, Any]) -> Tuple:
        return (
            interpretation['fieldCount'],
            interpretation['type'],
            *(([interpretation['delimiter'], interpretation.get('quotation') or 'None', interpretation.get('escape') or 'None']) if interpretation['type'] == 'character' else (interpretation['layoutKey'],))
        ) if self.use_strict_bin_key else (interpretation['fieldCount'],)

    def is_valid_data(self, data: Block) -> bool:
        return len(data.compacted) >= self.min_data_rows

    def is_valid_header(self, header: Block) -> bool:
        if header is None:
            return True
        header_row_count = len(header.compacted)
        has_float = any(any(contains_float(field) for field in row['fields']) for row in header.compacted)
        return header_row_count <= self.max_header_rows and not has_float


def get_content(rows: List[Dict[str, Any]], preserve_skipped_rows: bool) -> List[List[str]]:
    if preserve_skipped_rows:
        row_pointer = 0
        content = []
        column_count = len(rows[0])
        for i_row in range(rows[0]['index'], rows[-1]['index'] + 1):
            if rows[row_pointer]['index'] == i_row:
                content.append([
                    field['content'].strip()
                    for field in rows[row_pointer]['fields']
                ])
                row_pointer += 1
            else:
                content.append([''] * column_count)
        return content
    else:
        return [
            [
                field['content'].strip()
                for field in row['fields']
            ]
            for row in rows
        ]


def contains_float(field: Dict[str, any]) -> bool:
    return any(
        pattern_component['precision']['float'] > 0
        for pattern_component in field['patternComponents']
        if pattern_component['type'] == DataType.NUMBER
    )


def is_styling_line(string: str) -> bool:
    return string and all(not character.isalnum() for character in string)


def has_border_delimiter(header: Block, data: Block) -> bool:
    data_uses_border = all(row['type'] == 'character' and row['delimiter'] == '|' for row in data.compacted)
    header_uses_border = not header or all(row['type'] == 'character' and row['delimiter'] == '|' for row in header.compacted)
    return data_uses_border and header_uses_border


def get_pattern_components_per_field(rows: List[Dict[str, Any]]) -> float:
    return mean(
        mean(
            1 / len(field['patternComponents'])
            for field in row['fields']
        )
        for row in rows
    )


def get_recognized_pattern_ratio(rows: List[Dict[str, Any]]) -> float:
    return mean(
        mean(
            len(field['patternComponents']) == 1 and field['patternComponents'][0]['type'] != DataType.OTHER
            for field in row['fields']
        )
        for row in rows
    )
