from pathlib import Path
from typing import Any, Dict

from pymongo import ASCENDING
from pymongo.database import Database
from tqdm import tqdm

from utils.utils import get_lines


def download_file(db: Database, file: Dict[str, Any]):
    lines = get_lines(db, str(file['_id']), ASCENDING, {'raw': True, '_id': False})
    with open(file['target'], mode='x') as file:
        file.writelines(line['raw'] for line in lines)


#  download all files that have been previously imported using the import_data method
def download_files(db: Database, target: Path):
    files = [
        {
            **file,
            'target': target / (file['hash'] + '.txt')
        }
        for file in db['files'].find()
    ]
    missing_files = [
        file
        for file in files
        if not file['target'].exists()
    ]
    [
        download_file(db, file)
        for file in tqdm(missing_files)
    ]
