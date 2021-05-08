from typing import List, Dict

from compact_advisors.CompactAdvisor import CompactAdvisor
from table_compact import get_max_consistency, compact_rows


class Block(object):

    def __init__(
            self,
            col_count: int,
            compact_advisor: CompactAdvisor,
            min_compatibility: float = 0.5,
            max_continuous_white_spaces: float = 1.0,
            min_column_consistency: float = 0.5
    ):
        self.col_count = col_count
        self.compact_advisor = compact_advisor
        self.min_compatibility = min_compatibility
        self.max_continuous_white_spaces = max_continuous_white_spaces
        self.min_column_consistency = min_column_consistency
        self.rows = []
        self.prev_row_interpretations = []
        self.compacted = []

    def is_compatible(self, interpretations: List[Dict[str, any]]) -> bool:
        return not self.prev_row_interpretations or get_max_consistency(
            [self.prev_row_interpretations, interpretations],
            self.col_count,
            self.min_column_consistency,
            1.0
        ) >= self.min_compatibility

    def add(self, interpretations: List[Dict[str, any]]):
        if len(interpretations) > 1:
            compact_instructions = self.compact_advisor.get_compact_instructions(self.rows, interpretations)
            if compact_instructions:
                self.rows = compact_rows(
                    self.rows,
                    self.col_count,
                    self.min_column_consistency,
                    self.max_continuous_white_spaces,
                    compact_instructions
                )
        self.rows.append(interpretations)
        self.prev_row_interpretations = interpretations

    def close(self):
        self.rows = compact_rows(
            self.rows,
            self.col_count,
            self.min_column_consistency,
            self.max_continuous_white_spaces,
            [1] * len(self.rows)
        )
        self.compacted = [interpretations[0] for interpretations in self.rows]
