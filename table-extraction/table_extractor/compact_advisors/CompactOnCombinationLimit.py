from functools import reduce
from typing import List, Dict, Optional

from compact_advisors.CompactAdvisor import CompactAdvisor


class CompactOnCombinationLimit(CompactAdvisor):

    def __init__(self, max_combinations: int):
        self.max_combinations = max_combinations

    def get_compact_instructions(
            self,
            rows: List[List[Dict[str, any]]],
            line_interpretations: List[Dict[str, any]]
    ) -> Optional[List[int]]:
        line_interpretations_count = len(line_interpretations)
        if line_interpretations_count > self.max_combinations:
            raise Exception('Max combination parameter chosen too low! Single line exceeds parameter.')
        interpretations_per_row = [len(interpretations) for interpretations in rows]
        compact_required = False
        while reduce(
                lambda product, interpretations: product * interpretations,
                [*interpretations_per_row, line_interpretations_count]
        ) > self.max_combinations:
            interpretations_per_row = [max(count-1, 1) for count in interpretations_per_row]
            compact_required = True
        if not compact_required:
            return None
        return interpretations_per_row
