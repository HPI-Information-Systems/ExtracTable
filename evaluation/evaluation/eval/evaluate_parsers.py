from multiprocessing import Pool
from pathlib import Path

from pymongo.database import Database
from tqdm import tqdm

from eval.evaluate_parser import evaluate_parser_unpack
from utils.parser import Parser


def evaluate_parsers(db: Database, mongo_uri: str, database_name: str, parsed_dir: Path, cores: int):
    files = db['files'].find(
        filter={},
        projection=['hash', 'tables', 'type', 'incomplete']
    )
    pool = Pool(cores)
    jobs = [
        (mongo_uri, database_name, file, parser, parsed_dir / parser.value / file['hash'])
        for file in files
        for parser in Parser
    ]
    list(tqdm(pool.imap(evaluate_parser_unpack, jobs, chunksize=1), total=len(jobs)))
