import os
from hashlib import md5
from json import loads
from pathlib import Path

from pymongo.database import Database
from tqdm import tqdm


#  - import files from the clever csv dataset using the provided annotations-json-file and a directory
#    where all github/ukdata documents are stored
#  - each imported file will have one table that covers all lines, where each line is considered as data
#  - the annotations from the json-file will be used for all lines
#  - after the import process has finished, the files can be annotated using the annotation tool

def import_clever_csv(db: Database, input_file_path: Path, data_dir: Path, source: str):
    with open(input_file_path) as input_file:
        annotated_files = [loads(line) for line in input_file]
    valid_files = [annotated_file for annotated_file in annotated_files if annotated_file['status'] == 'OK']
    for valid_file in tqdm(valid_files):
        filename = os.path.basename(valid_file['filename'])
        absolute_path = data_dir / filename
        if not absolute_path.exists():
            continue
        line_count = 0
        with open(absolute_path, errors='replace') as source_file:
            for _ in source_file:
                line_count += 1
        file = {
            'tables': [{'from': 0, 'to': line_count - 1}],
            'absolutePath': str(absolute_path.resolve()),
            'hash': md5(str(absolute_path.resolve()).encode('utf-8')).hexdigest(),
            'source': source
        }
        file_id = str(db['files'].insert_one(file).inserted_id)
        with open(absolute_path, errors='replace') as source_file:
            lines = [{
                'delimiter': {
                    'type': 'character',
                    'sequence': [valid_file['dialect']['delimiter']],
                },
                'escape': [valid_file['dialect']['escapechar']] if valid_file['dialect']['escapechar'] else [],
                'quotation': [valid_file['dialect']['quotechar']] if valid_file['dialect']['quotechar'] else [],
                'rowType': 'data',
                'raw': line,
                'index': i_line,
                'fileId': file_id,
            } for i_line, line in enumerate(source_file)]
        db['lines'].insert_many(lines)

