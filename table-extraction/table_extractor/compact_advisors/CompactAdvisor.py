from typing import Dict, List, Optional


class CompactAdvisor(object):

    def get_compact_instructions(
            self,
            rows: List[List[Dict[str, any]]],
            interpretations: List[Dict[str, any]]
    ) -> Optional[List[int]]:
        pass
