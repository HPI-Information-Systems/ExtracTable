from _csv import writer
from json import loads, JSONDecodeError
from pathlib import Path
from resource import getrusage, RUSAGE_CHILDREN
from shutil import rmtree
from subprocess import CalledProcessError, TimeoutExpired, run
from typing import Optional, List, Dict, Any

from utils.command_builder import build_command
from utils.js_parser_clone import parse_line_using_character_delimiter
from utils.parser import Parser
from utils.utils import get_file_line_count


def get_command(parser: Parser, file: Path, target_dir: Path, parameters: Optional[Dict[str, Any]] = None) -> List[str]:
    return build_command(
        parser,
        str(file.resolve()),
        **({
            **({'output_dir': str(target_dir.resolve())} if parser == Parser.TABLE_EXTRACTOR else {}),
            **(parameters or {}),
        })
    )


def parse_file_content(file: Path, dialect: Dict[str, str], target_dir: Path):
    line_count = get_file_line_count(file)
    output_file_path = target_dir / '_'.join(['1', str(line_count), dialect['delimiter'], '.csv'])
    with open(file) as input_file:
        with open(output_file_path, 'w') as file:
            csv_writer = writer(file)
            for line in input_file:
                try:
                    parsed = parse_line_using_character_delimiter(line, {
                        'delimiter': [dialect['delimiter']],
                        'quotation': [dialect['quotechar']] if dialect['quotechar'] else [],
                        'escape': [dialect['escapechar']] if dialect['escapechar'] else []
                    })
                except:
                    parsed = []
                csv_writer.writerow([field.strip() for field in parsed])


#  this function applies a parser to an input file and will store parsed tables in the target_dir
#  if timeout occurs, no data will be stored

def parse_file(
    parser: Parser,
    file: Path,
    target_dir: Path,
    timeout: Optional[int] = None,
    parameters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    try:
        start = getrusage(RUSAGE_CHILDREN).ru_utime
        completed_process = run(
            get_command(parser, file, target_dir, parameters),
            check=True,
            capture_output=True,
            timeout=timeout
        )
        if parser != Parser.TABLE_EXTRACTOR:
            target_dir.mkdir(exist_ok=True)
            dialect = loads(completed_process.stdout)
            parse_file_content(file, dialect, target_dir)
        return {'status': 'success', 'runTime': getrusage(RUSAGE_CHILDREN).ru_utime - start}
    except TimeoutExpired:
        rmtree(target_dir, ignore_errors=True)
        target_dir.mkdir()
        return {'status': 'timeout', 'runTime': None}
    except (CalledProcessError, JSONDecodeError):
        rmtree(target_dir, ignore_errors=True)
        target_dir.mkdir()
        return {'status': 'error', 'runTime': None}


def unpack_parse_file(args) -> Dict[str, Any]:
    return parse_file(*args)
