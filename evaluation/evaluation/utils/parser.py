from enum import Enum


class Parser(Enum):
    TABLE_EXTRACTOR = 'tableExtractor'
    SNIFFER = 'sniffer'
    HYPOPARSR = 'hypoparsr'
    CLEVER = 'cleverCSV'
    RFC = 'rfc4180'
