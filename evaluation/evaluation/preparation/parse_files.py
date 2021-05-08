from multiprocessing import Pool
from pathlib import Path
from shutil import rmtree
from typing import Optional

from pymongo import ASCENDING
from pymongo.database import Database

from preparation.file_parser import unpack_parse_file
from utils.parser import Parser


def parse_files(
        db: Database, dataset_dir: Path, target_dir: Path, cores: int, timeout: Optional[int]
):
    if target_dir.exists():
        rmtree(target_dir)
    target_dir.mkdir()
    db['metrics'].drop()
    db['metrics'].create_index([('parser', ASCENDING), ('fileId', ASCENDING)], unique=True)
    [(target_dir / parser.value).mkdir(exist_ok=True, parents=True) for parser in Parser]
    files = db['files'].find(filter={}, projection=['hash'])
    jobs_with_file_id = [
        (str(file['_id']), (parser, dataset_dir / (file['hash'] + '.txt'), target_dir / parser.value / file['hash'], timeout))
        for file in files
        for parser in Parser
    ]
    pool = Pool(cores)
    run_times = pool.map(unpack_parse_file, [job[1] for job in jobs_with_file_id], chunksize=1)
    db['metrics'].insert_many(
        {
            'parser': job[1][0].value,
            'fileId': job[0],
            **result
        }
        for job, result in zip(jobs_with_file_id, run_times)
    )
