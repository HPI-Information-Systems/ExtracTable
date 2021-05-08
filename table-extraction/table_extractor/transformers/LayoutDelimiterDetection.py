from itertools import groupby
from operator import itemgetter
from pathlib import Path
from typing import List, Dict

from pipeline.Transformer import Transformer


class LayoutDelimiterDetection(Transformer):

    def __init__(self, width: int, min_row_count: int = 1, min_col_count: int = 1, essential_row_count=None):
        super().__init__()
        self.width = width
        self.min_row_count = min_row_count
        self.min_col_count = min_col_count
        self.essential_row_count = essential_row_count
        self.buffer = []
        self.counter = initialize_counter(width)
        self.tables = []

    def transform(self, line: dict):
        self.add_line(line)
        if line['raw'].strip():
            force_start_table = self.update_tables()
            self.start_table(force_start_table)
            self.merge_tables()
            self.gc_lines()

    def reached_end(self):
        [self.close_table(table, reached_end=True) for table in list(self.tables)]
        self.gc_lines(True)

    def gc_lines(self, clear: bool = False):
        buffer_index = len(self.buffer) if clear else 0
        if not clear:
            if self.tables:
                min_from = min(table['from'] for table in self.tables)
                buffer_index = next(i_line for i_line, line in enumerate(self.buffer) if line['index'] == min_from)
            buffer_index = min(0 if len(self.buffer) < self.min_row_count else len(self.buffer) - self.get_table_start(), buffer_index)
        completed_lines = self.buffer[:buffer_index]
        [self.complete_line(line) for line in completed_lines]
        self.buffer = self.buffer[buffer_index:]

    def complete_line(self, line: Dict[str, any]):
        self.call_next({
            k: v
            for k, v in line.items()
            if not (k in ['bitmap', 'isEmpty'])
        })

    def merge_tables(self):
        tables_by_block_count = {k: list(v) for k, v in groupby(sorted(self.tables, key=block_count), block_count)}
        tables_by_block_count = sort_tables_by_row_count(tables_by_block_count)  # sorted asc
        [
            [self.merge_table(table, tables[i_table + 1:]) for i_table, table in enumerate(tables)]
            for tables in tables_by_block_count.values()
        ]

    def merge_table(self, table: Dict[str, any], longer_tables: List[Dict[str, any]]):
        mergeables = [*filter(lambda longer_table: is_mergeable(table, longer_table), longer_tables)]
        [merge_blocks(longer_table['blocks'], table['blocks']) for longer_table in mergeables]
        if any(mergeables):
            self.close_table(table, discard=True)

    def update_tables(self) -> bool:
        return any([*map(lambda table: self.update_table(table), list(self.tables))])

    def update_table(self, table: Dict[str, any]):
        white_space_indexes = get_white_space_indexes(self.buffer[-1]['bitmap'])
        continued_blocks = [block for block in table['blocks'] if has_at_least_one_intersection(block['indexes'], white_space_indexes)]
        ending_blocks = [block for block in table['blocks'] if not has_at_least_one_intersection(block['indexes'], white_space_indexes)]
        close_table = any([block['isEssential'] for block in ending_blocks]) or not continued_blocks
        if close_table:
            self.close_table(table)
        else:
            self.continue_table(table, continued_blocks, white_space_indexes)
        return close_table

    def continue_table(self, table: Dict[str, any], continued_blocks: List[Dict[str, any]], white_space_indexes: List[int]):
        block_indexes = [block['indexes'] for block in continued_blocks]  # project
        flattened_block_indexes = [index for indexes in block_indexes for index in indexes]  # flatten
        relevant_white_spaces = sorted(set(white_space_indexes) & set(flattened_block_indexes))  # intersection
        updated_blocks = vertical_lines_to_blocks(relevant_white_spaces, self.width)
        start_line_buffer_index = get_line_buffer_index(self.buffer, table['from'])
        row_count = len(self.buffer) - start_line_buffer_index
        if not (self.essential_row_count is None) and row_count >= self.essential_row_count:
            for block in updated_blocks:
                if not block['isTrailing']:
                    block['isEssential'] = True
        table['blocks'] = updated_blocks

    def close_table(self, table: Dict[str, any], discard: bool = False, reached_end: bool = False):
        if not discard:
            starting_line_buffer_index = get_line_buffer_index(self.buffer, table['from'])
            lines = self.buffer[starting_line_buffer_index:None if reached_end else -1]
            blocks = [block for block in table['blocks'] if block['isEssential']]
            split_indexes = blocks_to_split_indexes(blocks, self.width)
            for line in lines:
                line['layouts'] = [
                    *line['layouts'],
                    {
                        'indexes': split_indexes,
                        'from': table['from']
                    }
                ]
        self.tables.remove(table)

    def start_table(self, force_start_table: bool):
        detected_table_start = self.min_row_count in self.counter.values()
        if not (force_start_table or detected_table_start):
            return
        starting_vertical_lines = self.get_vertical_lines(self.min_row_count)
        blocks = vertical_lines_to_blocks(starting_vertical_lines, self.width)
        blocks_is_trailing = [block['isTrailing'] for block in blocks]
        field_count = blocks_is_trailing.count(False) + 1
        if field_count >= self.min_col_count:
            table_start = self.buffer[-self.get_table_start() if detected_table_start else -1]['index']
            self.open_table(table_start, blocks)

    def get_table_start(self):
        non_empty = 0
        for i_line, line in enumerate(reversed(self.buffer)):
            non_empty += not line['isEmpty']
            if non_empty == self.min_row_count:
                return i_line + 1
        return 0

    def open_table(self, line_index: int, blocks: List[Dict[str, any]]):
        self.tables.append(create_table(line_index, blocks))

    def get_vertical_lines(self, min_length: int) -> List[int]:
        counts = [list(pos_count_tuple) for pos_count_tuple in self.counter.items()]
        vertical_lines = {k: list(v) for k, v in groupby(sorted(counts, key=itemgetter(1)), itemgetter(1))}  # count -> List of [index, count]
        vertical_lines = {
            count: [pos_count_tuple[0] for pos_count_tuple in pos_count_tuples]
            for count, pos_count_tuples in vertical_lines.items()
        }  # count -> indexes
        vertical_lines = {count: indexes for count, indexes in vertical_lines.items() if count >= min_length}
        flattened_indexes = [index for indexes in vertical_lines.values() for index in indexes]
        return sorted(flattened_indexes)

    def add_line(self, line: Dict[str, any]):
        # add line to buffer and update counter
        expanded_raw = line['raw'].expandtabs()
        bitmap = line_to_bitmap(expanded_raw, self.width)
        self.buffer.append(expand_line(line, bitmap))
        if line['raw'].strip():  # if line is empty, don't update counter as it would stop tables
            self.update_counter(bitmap)

    def update_counter(self, bitmap: List[bool]):
        # True increments counter at position i, False resets counter to False
        self.counter = {
            pos: (count + 1) if bitmap[pos] else 0
            for pos, count in self.counter.items()
        }


def block_count(table):
    return sum([1 for block in table['blocks'] if block['isTrailing'] is False])


def merge_blocks(dst_blocks: List[Dict[str, any]], src_blocks: List[Dict[str, any]]):
    if src_blocks[0]['isTrailing'] and dst_blocks[0]['isTrailing']:
        dst_blocks[0]['indexes'] = sorted(set(dst_blocks[0]['indexes']) & set(src_blocks[0]['indexes']))
    if src_blocks[-1]['isTrailing'] and dst_blocks[-1]['isTrailing']:
        dst_blocks[-1]['indexes'] = sorted(set(dst_blocks[-1]['indexes']) & set(src_blocks[-1]['indexes']))
    src_blocks_without_trailing = [block for block in src_blocks if not block['isTrailing']]
    dst_blocks_without_trailing = [block for block in dst_blocks if not block['isTrailing']]
    for i_block, dst_block in enumerate(dst_blocks_without_trailing):
        dst_block['indexes'] = sorted(set(dst_block['indexes']) & set(src_blocks_without_trailing[i_block]['indexes']))


def is_mergeable(table: Dict[str, any], longer_table: Dict[str, any]) -> bool:
    table_blocks_without_trailing = [block for block in table['blocks'] if not block['isTrailing']]
    longer_table_blocks_without_trailing = [block for block in longer_table['blocks'] if not block['isTrailing']]
    return all([
        any(set(block['indexes']) & set(table_blocks_without_trailing[i_block]['indexes']))
        for i_block, block in enumerate(longer_table_blocks_without_trailing)
    ])


def blocks_to_split_indexes(blocks: List[Dict[str, any]], width: int) -> List[Dict[str, any]]:
    block_indexes = [block['indexes'] for block in blocks]  # project
    flattened_block_indexes = [index for indexes in block_indexes for index in indexes]  # flatten
    content = sorted(set(range(width)) - set(flattened_block_indexes))  # difference
    content_blocks = vertical_lines_to_blocks(content, width)
    return [
        create_split_index(block['indexes'][0], block['indexes'][-1] + 1)
        for block in content_blocks
    ]


def create_split_index(start: int, end: int) -> Dict[str, int]:
    # [start;end[
    return {
        'start': start,
        'end': end,
        'width': end-start
    }


def vertical_lines_to_blocks(vertical_lines: List[int], width: int) -> List[Dict[str, any]]:
    # detect blocks and assign vertical lines belonging to them
    blocks = []
    indexes = []
    for i_line, vertical_line in enumerate(vertical_lines):
        if not i_line or vertical_line - indexes[-1] == 1:
            indexes.append(vertical_line)
        else:
            blocks.append(create_block(indexes, width))
            indexes = [vertical_line]
    if any(indexes):
        blocks.append(create_block(indexes, width))
    return blocks


def has_at_least_one_intersection(block_a: List[int], block_b: List[int]) -> bool:
    for index in block_b:
        if index in block_a:
            return True
    return False


def get_white_space_indexes(bitmap: List[bool]) -> List[int]:
    indexes = []
    for i_position, is_white_space in enumerate(bitmap):
        if is_white_space:
            indexes.append(i_position)
    return indexes


def line_to_bitmap(line: str, width: int) -> List[bool]:
    # white space -> True, everything else -> False
    bitmap = [char.isspace() for char in line]
    padded_bitmap = [*bitmap, *([True] * (width - len(bitmap)))]
    return padded_bitmap


def create_block(indexes: List[int], width: int) -> Dict[str, any]:
    is_trailing = indexes[0] == 0 or indexes[-1] == width - 1
    return {
        'indexes': indexes,
        'isEssential': not is_trailing and len(indexes) > 1,
        'isTrailing': is_trailing,
    }


def create_table(line_index, blocks: List[Dict[str, any]]) -> Dict[str, any]:
    return {
        'from': line_index,
        'blocks': blocks
    }


def expand_line(line: Dict[str, any], bitmap: List[bool]) -> Dict[str, any]:
    return {
        **line,
        'bitmap': bitmap,
        'layouts': [],
        'isEmpty': not line['raw'].strip()
    }


def sort_tables_by_row_count(tables_by_block_count: Dict[int, List[Dict[str, any]]]) -> Dict[int, List[Dict[str, any]]]:
    return {
        field_count: sorted(tables, key=lambda table: table['from'], reverse=True)
        for field_count, tables in tables_by_block_count.items()
    }


def initialize_counter(width: int) -> Dict[int, int]:
    return {i_pos: 0 for i_pos in range(width)}


def get_line_buffer_index(lines: List[Dict[str, any]], line_index: int) -> int:
    return next((i_line for i_line, line in enumerate(lines) if line['index'] == line_index), -1)


def get_max_line_width_of_file(input_file: Path) -> int:
    max_length = 0
    with open(input_file, mode='r', errors='replace') as file:
        for line in file:
            max_length = max(max_length, len(line.expandtabs()))
    return max_length
