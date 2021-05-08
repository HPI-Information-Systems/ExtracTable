from _csv import reader, Error
from typing import List, Any, Dict


class TableFileCursor:

    def __init__(self, parsed_table_files: List[Dict[str, Any]], start_index: int = 0):
        self.line_index = 0
        self.parsed_tables = [*parsed_table_files]
        self.current = None
        for _ in range(start_index):
            self.__next__()

    def __iter__(self):
        return self

    def __next__(self):
        if self.parsed_tables and self.line_index == self.parsed_tables[0]['from']:
            if self.current:
                self.current['file_handle'].close()
            self.open_table(self.parsed_tables[0])
        if self.current:
            try:
                row = next(self.current['cursor'], None)
            except Error:
                self.current['file_handle'].close()
                self.current = None
                self.line_index += 1
                return None
            if row is None:
                self.current['file_handle'].close()
                self.current = None
                return self.__next__()
            else:
                self.line_index += 1
                return row
        else:
            self.line_index += 1
            return None

    def open_table(self, table: Dict[str, Any]):
        file_handle = open(table['path'])
        self.current = {
            'file_handle': file_handle,
            'cursor': reader(file_handle)
        }
        self.parsed_tables.remove(table)
