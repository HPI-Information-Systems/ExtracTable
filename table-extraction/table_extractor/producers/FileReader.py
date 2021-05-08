import logging
from pathlib import Path
from typing import Dict

from pipeline.Producer import Producer


class FileReader(Producer):

    def __init__(self, file_path: Path, limit: int = None, skip: int = 0):
        super().__init__()
        self.line_count = get_line_count(file_path)
        self.file = open(file_path, mode='r', errors='replace')
        self.index = 0
        self.next = self.file.readline()
        self.limit = min(skip + limit, self.line_count) if not (limit is None) else self.line_count
        self.skip_lines(skip)
        print_configuration(self.line_count, limit, skip)

    def has_next(self) -> bool:
        return self.index < self.limit

    def produce(self) -> Dict[str, any]:
        if not self.has_next():
            raise Exception('End of file stream reached!')
        message = self.create_message()
        self.read_next()
        return message

    def reached_end(self):
        self.file.close()

    def skip_lines(self, skip: int):
        if skip >= self.line_count:
            raise Exception('No content left after skipping!')
        [self.produce() for _ in range(skip)]

    def create_message(self) -> Dict[str, any]:
        return {
            'raw': self.next.rstrip('\n').strip('\x00'),
            'index': self.index
        }

    def read_next(self):
        self.next = self.file.readline()
        self.index += 1


def get_line_count(file_path: Path) -> int:
    with open(file_path, mode='r', errors='replace') as file:
        line_count = 0
        for _ in file:
            line_count += 1
    return line_count


def print_configuration(line_count: int, limit: int, skip: int):
    logging.info('File has ' + str(line_count) + ' lines')
    if not (limit is None):
        logging.info('Limit is set to ' + str(limit))
    if skip:
        logging.info('Skipping first ' + str(skip) + ' lines')
