from Block import Block
from compact_advisors import CompactAdvisor


class BlockFactory(object):

    def __init__(
        self,
        compact_advisor: CompactAdvisor,
        min_compatibility: float = 0.5,
        max_continuous_white_spaces: float = 0.1,
        min_column_consistency: float = 0.5
    ):
        self.compact_advisor = compact_advisor
        self.min_compatibility = min_compatibility
        self.max_continuous_white_spaces = max_continuous_white_spaces
        self.min_column_consistency = min_column_consistency

    def create(self, field_count: int):
        return Block(
            field_count,
            self.compact_advisor,
            self.min_compatibility,
            self.max_continuous_white_spaces,
            self.min_column_consistency
        )
