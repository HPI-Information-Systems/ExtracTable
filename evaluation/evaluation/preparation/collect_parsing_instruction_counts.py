from json import loads
from multiprocessing import Pool
from pathlib import Path
from subprocess import run, TimeoutExpired
from typing import Dict, Optional

from pymongo.database import Database
from tqdm import tqdm

from utils.command_builder import roots, environment


def get_command(file: Path):
    return [
        'python',
        str(roots[environment] / 'table-extraction/table_extractor/Main.py'),
        'pi_count',
        '--input_file',
        str(file.resolve())
    ]


def get_pi_count(file: Path, timeout) -> Optional[Dict[str, int]]:
    try:
        completed_process = run(
            get_command(file),
            check=True,
            capture_output=True,
            timeout=timeout
        )
        return loads(completed_process.stdout)
    except TimeoutExpired:
        return None


def unpack_get_pi_count(args) -> Optional[Dict[str, int]]:
    return get_pi_count(*args)


def collect_parsing_instruction_counts(db: Database, dataset_dir: Path, cores: int, timeout: int):
    files = [*db['files'].find(
        filter={'parsing_instructions': {'$exists': False}},
        projection=['hash']
    )]
    jobs = [
        (dataset_dir / (file['hash'] + '.txt'), timeout)
        for file in files
    ]
    pool = Pool(cores)
    for file, pi_count in tqdm(zip(files, pool.imap(unpack_get_pi_count, jobs)), total=len(jobs)):
        db['files'].update_one(
            filter={'_id': file['_id']},
            update={'$set': {'parsing_instructions': pi_count}}
        )
