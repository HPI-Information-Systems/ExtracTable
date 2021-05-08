from collections import Counter
from pathlib import Path
from typing import Dict, Any, List

from pymongo import ASCENDING
from pymongo.cursor import Cursor
from pymongo.database import Database


def get_lines(
        db: Database,
        file_id: str,
        sort_order: int,
        projection: Dict[str, Any] = None
) -> Cursor:
    line_collection = db['lines']
    return line_collection.aggregate(
        pipeline=[
            {'$match': {'fileId': file_id}},
            {'$sort': {'index': sort_order}},
            {'$project': projection or {'_id': False, 'raw': True, 'index': True}}
        ],
        allowDiskUse=True
    )


def get_content(db: Database, file: Dict[str, Any]) -> Cursor:
    return get_lines(db, str(file['_id']), ASCENDING, {
        'isPartOfTable': True,
        'index': True,
        'parsed': True,
        'rowType': True,
        'skip': True,
        'post-processed': True,
        '_id': False
    })


def get_file_line_count(file_path: Path) -> int:
    with open(file_path, errors='replace') as file:
        return sum(1 for _ in file)


def parse_table_files(table_files: List[Path]) -> List[Dict[str, Any]]:
    parsed_table_files = []
    for table_file in table_files:
        from_index, to_index,*_ = table_file.stem.split('_')
        parsed_table_files.append({
            'path': table_file,
            'from': int(from_index) - 1,
            'to': int(to_index) - 1
        })
    return sorted(parsed_table_files, key=lambda table: table['from'])


def mean_counters(counters: List[Counter]) -> Dict[Any, float]:
    return {
        k: summed_value / len(counters)
        for k, summed_value in sum(counters, Counter()).items()
    }


def stringify_dict(value):
    if isinstance(value, dict):
        return {str(k): stringify_dict(v) for k,v in value.items()}
    elif isinstance(value, list):
        return [stringify_dict(element) for element in value]
    else:
        return value
