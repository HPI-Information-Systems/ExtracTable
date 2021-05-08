from collections import Counter
from json import dumps
from typing import Dict

from pipeline.Consumer import Consumer


class ParsingInstructionsCounter(Consumer):

    def __init__(self):
        super().__init__()
        self.counter = Counter()

    def consume(self, line: Dict[str, any]):
        self.counter.update(sum((Counter({interpretation['type']: 1}) for interpretation in line['solutionSpace']), Counter()))

    def reached_end(self):
        print(dumps(self.counter))
