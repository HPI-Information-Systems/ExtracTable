from collections import Counter
from typing import List


class Combinations:
    def __init__(self, counts: List[int]):
        self.max = counts
        self.pointer = Counter({i_count: 0 for i_count in range(len(counts))})
        self.reached_end = not all(counts)

    def __iter__(self):
        return self

    def inc(self):
        index = len(self.max) - 1
        while index > -1:
            self.pointer[index] += 1
            if self.pointer[index] == self.max[index]:
                self.pointer[index] = 0
                index -= 1
            else:
                return
        self.reached_end = True

    def __next__(self) -> List[int]:
        if self.reached_end:
            raise StopIteration
        combination = list(self.pointer.values())
        self.inc()
        return combination
