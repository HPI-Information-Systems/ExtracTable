from fire import Fire
from csv import Sniffer
from json import dumps

class SnifferWrapper:

    @staticmethod
    def detect(file_path: str):
        with open(file_path, newline='') as file:
            dialect = Sniffer().sniff(file.read())
        print(dumps({
            'delimiter': dialect.delimiter,
            'quotechar': dialect.quotechar,
            'escapechar': dialect.quotechar if dialect.doublequote else (dialect.escapechar or '')
        }))


if __name__ == '__main__':
    Fire(SnifferWrapper)
