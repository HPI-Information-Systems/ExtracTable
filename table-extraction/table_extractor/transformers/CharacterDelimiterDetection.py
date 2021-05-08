import re
from itertools import combinations
from typing import List, Dict

from pipeline.Transformer import Transformer


class CharacterDelimiterDetection(Transformer):

    def __init__(self, max_delimiter_length: int = None, delimiter_character_blacklist: List[str] = None):
        super().__init__()
        self.non_delimiter_regex = re.compile(r'[a-zA-Z0-9' + re.escape(''.join(delimiter_character_blacklist or [])) + ']+')
        self.max_delimiter_length = max_delimiter_length

    def transform(self, line: Dict[str, any]):
        delimiter_substrings = self.get_delimiter_substrings(line['raw'])
        delimiters = get_delimiter_substring_combinations(delimiter_substrings)
        if not (self.max_delimiter_length is None):
            delimiters = [delimiter for delimiter in delimiters if len(delimiter) <= self.max_delimiter_length]
        delimiters_sorted_by_length = sorted(delimiters, key=lambda delimiter: (len(delimiter), delimiter))
        self.call_next({
            **line,
            'characterDelimiters': delimiters_sorted_by_length
        })

    def get_delimiter_substrings(self, string: str) -> List[str]:
        # in each line replace the alpha-numerical content with placeholder 's',
        # then split by s to get delimiter sequences.
        placeholder_string = self.non_delimiter_regex.sub('s', string)
        delimiter_sequences = placeholder_string.split('s')

        return list(set(seq for seq in delimiter_sequences if seq))


def get_combinations(string: str) -> List[str]:
    # get all combinations of characters
    return list(set(string[x:y] for x, y in combinations(range(len(string) + 1), r=2)))


def get_delimiter_substring_combinations(delimiter_substrings: List[str]) -> List[str]:
    delimiter_combinations = [get_combinations(delimiter) for delimiter in delimiter_substrings]
    flattened_delimiter_combinations = [combination for delimiter_combination in delimiter_combinations for combination in delimiter_combination]
    return list(set(flattened_delimiter_combinations))
