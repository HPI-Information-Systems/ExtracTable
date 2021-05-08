import logging
from typing import Dict

from pipeline.Transformer import Transformer


class LineBouncer(Transformer):

    def __init__(self, width: int):
        super().__init__()
        self.width = width

    def transform(self, line: Dict[str, any]):
        content = line['raw'].strip()
        if is_solid_styling_line(content):
            logging.info('Discard solid styling line ' + str(line['index'] + 1))
        else:
            self.call_next(line)


def is_solid_styling_line(string: str) -> bool:
    return string and not any(char.isalnum() or char.isspace() for char in string)
