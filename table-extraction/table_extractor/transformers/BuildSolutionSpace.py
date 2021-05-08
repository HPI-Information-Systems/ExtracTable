from typing import List, Dict

from parser.parser import parse_line
from pipeline.Transformer import Transformer


class BuildSolutionSpace(Transformer):

    def __init__(
            self,
            empty_line_delimits_table: bool = False,
            use_strict_bin_key: bool = False,
            max_quotation_escape_length: int = 2,
            enable_ascii: bool = True
    ):
        super().__init__()
        self.empty_line_delimits_table = empty_line_delimits_table
        self.use_strict_bin_key = use_strict_bin_key
        self.max_quotation_escape_length = max_quotation_escape_length
        self.enable_ascii = enable_ascii

    def transform(self, line: Dict[str, any]):
        solution_space = self.get_solution_space(line) if self.use_strict_bin_key else [*{'@@@'.join(interpretation['parsed']): interpretation for interpretation in reversed(self.get_solution_space(line))}.values()]
        solution_space = [interpretation for interpretation in solution_space if any(interpretation['parsed'])]
        if not solution_space and not self.empty_line_delimits_table:
            return
        self.call_next({
            **{
                k: v
                for k, v in line.items()
                if not (k in ['layout', 'characterDelimiters'])
            },
            'solutionSpace': solution_space
        })

    def build_character_solution_space(self, line: Dict[str, any]) -> List[Dict[str, any]]:
        parser_results = [parse_line(line['raw'], character_delimiter, self.max_quotation_escape_length) for character_delimiter in line['characterDelimiters']]
        flattened_parser_results = [result for results in parser_results for result in results]
        return flattened_parser_results

    def get_solution_space(self, line: Dict[str, any]) -> List[Dict[str, any]]:
        character_solution_space = self.build_character_solution_space(line)
        layout_solution_space = build_layout_solution_space(line) if self.enable_ascii else []
        solution_space = [*character_solution_space, *layout_solution_space]
        return [{**interpretation, 'index': line['index']} for interpretation in solution_space]


def split_string_by_indexes(string: str, indexes: List[Dict[str, int]]) -> List[str]:
    return [string[index['start']:index['end']].strip() for index in indexes]


def build_layout_solution_space(line: Dict[str, any]) -> List[Dict[str, any]]:
    expanded_raw = line['raw'].expandtabs()
    return [
        {
            'type': 'layout',
            'parsed': split_string_by_indexes(expanded_raw, layout['indexes']),
            'indexes': layout['indexes'],
            'layoutKey': layout['from']
        }
        for layout in line['layouts']
    ]
