from json import dumps
from pathlib import Path
from typing import List

from utils.environment import Environment
from utils.parser import Parser

environment = Environment.DOCKER

roots = {
    Environment.MAC: Path('/Users/deeps/ownCloud/ITSE MA 4/Master Thesis/extracting-tables-from-plain-text/'),
    Environment.DOCKER: Path('/root/extracting-tables-from-plain-text/'),
    Environment.VM: Path('/home/leonardo.huebscher/extracting-tables-from-plain-text/')
}


def build_sniffer_command(file_path: str) -> List[str]:
    return [
        'python',
        str(roots[environment] / 'scripts/sniffer-cmd.py'),
        'detect',
        '--file_path',
        file_path
    ]


def build_hypoparsr_command(file_path: str) -> List[str]:
    if environment == Environment.MAC:
        return build_rfc_command(file_path)  # debug
    return ['Rscript', str(roots[environment] / 'scripts/hypoparsr.R'), file_path]


def build_clever_csv_command(file_path: str) -> List[str]:
    return ['clevercsv', 'detect', '-j', file_path]


def build_table_extractor_command(file_path: str) -> List[str]:
    return [
        'python',
        str(roots[environment] / 'table-extraction/table_extractor/Main.py'),
        'extract',
        '--input_file',
        file_path
    ]


def build_rfc_command(_) -> List[str]:
    return ['echo', dumps({'delimiter': ',', 'quotechar': '"', 'escapechar': '"'})]


command_builders = {
    Parser.TABLE_EXTRACTOR: build_table_extractor_command,
    Parser.SNIFFER: build_sniffer_command,
    Parser.CLEVER: build_clever_csv_command,
    Parser.HYPOPARSR: build_hypoparsr_command,
    Parser.RFC: build_rfc_command
}


def build_command(parser: Parser, file_path: str, **parameters) -> List[str]:
    command = command_builders[parser](file_path)
    [
        command.extend(['--' + key, str(value)])
        for key, value in parameters.items()
    ]
    return command
