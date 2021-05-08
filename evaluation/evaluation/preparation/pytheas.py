from json import JSONDecodeError, load
from multiprocessing import Pool
from pathlib import Path
from resource import getrusage, RUSAGE_CHILDREN
from subprocess import CalledProcessError, TimeoutExpired, run, DEVNULL
from tempfile import TemporaryDirectory
from typing import Any, Dict, List

from pymongo import InsertOne
from pymongo.database import Database
from tqdm import tqdm

PYTHEAS_BIN = Path('/root/Pytheas/src/pytheas/')


def build_pytheas_command(file_path: Path, target: Path) -> List[str]:
    return [
        'python',
        str((PYTHEAS_BIN / 'pytheas.py').resolve()),
        'infer',
        '--weights',
        str((PYTHEAS_BIN / 'trained_rules.json').resolve()),
        '--output_file',
        str(target.resolve()),
        '--filepath',
        str(file_path.resolve())
    ]


def unpack_pytheas(args) -> Dict[str, Any]:
    return run_pytheas_for_file(*args)


def run_pytheas_for_file(file_path: Path, target: Path, timeout: int) -> Dict[str, Any]:
    try:
        start = getrusage(RUSAGE_CHILDREN).ru_utime
        run(
            build_pytheas_command(file_path, target),
            stdout=DEVNULL,
            stderr=DEVNULL,
            capture_output=False,
            timeout=timeout,
            check=True
        )
        with open(target) as target_file:
            result = load(target_file)
        if not result:
            return {
                'status': 'error',
                'runTime': None,
                'tables': []
            }
        tables = [
            {
                'from': min(table['data_start'], *table['header']) if table['header'] else table['data_start'],
                'to': table['data_end']
            }
            for table in result['tables']
        ]
        return {
            'status': 'success',
            'runTime': getrusage(RUSAGE_CHILDREN).ru_utime - start,
            'tables': tables
        }
    except TimeoutExpired:
        return {
            'status': 'timeout',
            'runTime': None,
            'tables': []
        }
    except (CalledProcessError, JSONDecodeError):
        return {
            'status': 'error',
            'runTime': None,
            'tables': []
        }


def get_pytheas_table_ranges(db: Database, dataset_dir: Path, cores: int, timeout: int):
    files = db['files'].find(projection=['_id', 'hash', 'incomplete'])
    existing_files = db['pytheas'].find(projection=['_id'])
    missing_files = [file for file in files if not(file['_id'] in existing_files)]
    working_dir = TemporaryDirectory()
    jobs = [
        (dataset_dir / (file['hash'] + '.txt'), Path(working_dir.name) / (file['hash'] + '.json'), timeout)
        for file in missing_files
    ]
    with Pool(cores) as pool:
        pytheas_results = list(tqdm(pool.imap(unpack_pytheas, jobs, chunksize=1), total=len(jobs)))
    working_dir.cleanup()
    operations = [
        InsertOne({
            'fileId': str(file['_id']),
            'incomplete': file.get('incomplete', False),
            **result
        })
        for file, result in zip(missing_files, pytheas_results)
    ]
    db['pytheas'].bulk_write(operations)

