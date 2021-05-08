from hashlib import md5
from statistics import mode
from typing import Any, Dict, Optional, List

from pymongo import MongoClient, ASCENDING, DESCENDING, IndexModel
from pymongo.cursor import Cursor
from pymongo.database import Database
from tqdm import tqdm

from utils.js_parser_clone import parse_line
from utils.utils import get_lines


def get_first_non_empty_line_index(content: Cursor) -> Optional[int]:
    for line in content:
        if line['raw'].strip():
            return line['index']
    return None


def determine_file_type(db: Database, file: Dict[str, Any]) -> str:
    #  files have at least one line, and at least one table
    if len(file['tables']) == 1:
        first_non_empty_line = get_first_non_empty_line_index(get_lines(db, str(file['_id']), ASCENDING))
        last_non_empty_line = get_first_non_empty_line_index(get_lines(db, str(file['_id']), DESCENDING))
        table = file['tables'][0]
        if table['from'] == first_non_empty_line and table['to'] == last_non_empty_line:
            return 'simple'
    return 'complex'


def defer_table_type(db: Database, file_id: str, table: Dict[str, int]) -> str:
    delimiter_types = db['lines'].distinct(filter={
        'fileId': file_id,
        'skip': False,
        'index': {
            '$gte': table['from'],
            '$lte': table['to']
        }
    }, key='delimiter.type')
    return delimiter_types[0] if len(delimiter_types) == 1 else 'mixed'


def add_table_types(db: Database, file: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        {
            **table,
            'type': defer_table_type(db, str(file['_id']), table)
        }
        for table in file['tables']
    ]


def import_files(source: Database, target: Database):
    target['files'].create_indexes(indexes=[
        IndexModel('absolutePath'),
        IndexModel('hash')
    ])
    annotated_files = source['files'].find(
        filter={'status': 'annotated'},
        projection=['absolutePath', 'tables', 'source']
    )
    imported_files = [
        imported_file['absolutePath']
        for imported_file in target['files'].find(projection={'_id': False, 'absolutePath': True})
    ]
    missing_files = [
        annotated_file
        for annotated_file in annotated_files
        if not (annotated_file['absolutePath'] in imported_files)
    ]
    print('Prepare file import...')
    files = [
        {
            **missing_file,
            'tables': add_table_types(source, missing_file),
            'hash': md5(missing_file['absolutePath'].encode('utf-8')).hexdigest(),
            'type': determine_file_type(source, missing_file),
        }
        for missing_file in tqdm(missing_files)
    ]
    if files:
        print('Start import...')
        target['files'].insert_many(files)


def pad_layout_rows_to_column_count(rows: List[Dict[str, Any]], column_count: int) -> List[Dict[str, Any]]:
    return [
        {
            **row,
            'parsed': row['parsed'] if (row['delimiter']['type'] == 'delimiter' or len(
                row['parsed'])) == column_count else [
                *row['parsed'],
                *[''] * (column_count - len(row['parsed']))
            ]
        }
        for row in rows
    ]


def rows_to_columns(rows: List[Dict[str, Any]], column_count: int) -> List[List[str]]:
    return [
        [row['parsed'][i_col] for row in rows]
        for i_col in range(column_count)
    ]


def without_other_only_column(columns: List[List[str]]) -> List[List[str]]:
    return [
        column
        for column in columns
        if any(field.isalnum() for field in column) or len(set(column)) > 1
    ]


def without_empty_columns(columns: List[List[str]]) -> List[List[str]]:
    return [
        column
        for column in columns
        if any(column)
    ]


def columns_to_rows(columns: List[List[str]], row_count: int) -> List[List[str]]:
    return [[column[i_row] for column in columns] for i_row in range(row_count)]


def post_process(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    max_field_count = max(len(row['parsed']) for row in rows)
    padded_rows = pad_layout_rows_to_column_count(rows, max_field_count)
    field_counts = set(len(row['parsed']) for row in padded_rows)
    if len(field_counts) > 1:
        mode_column_count = mode(len(row['parsed']) for row in padded_rows)
        first_mismatch = next(row for row in padded_rows if len(row['parsed']) != mode_column_count)
        raise Exception('Field count mismatch detected! Line:', str(first_mismatch['index']))
    columns = rows_to_columns(padded_rows, max_field_count)
    non_empty_columns = without_empty_columns(columns)
    non_other_only_columns = without_other_only_column(non_empty_columns)
    post_processed_rows = columns_to_rows(non_other_only_columns, len(padded_rows))
    return [
        {
            **row,
            'parsed': padded_rows[i_row]['parsed'],
            'post-processed': post_processed_rows[i_row]
        }
        for i_row, row in enumerate(rows)
    ]


def parse_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    parsed_rows = []
    for row in rows:
        skip = row['rowType'] == 'other' and \
               (row['delimiter']['type'] == 'character' and not row['delimiter']['sequence'] or
                row['delimiter']['type'] == 'layout' and len(row['delimiter']['indexes']) == 1)
        try:
            parsed_rows.append({
                **row,
                'isPartOfTable': True,
                'skip': skip,
                **({'parsed': parse_line(row)} if not skip else {})
            })
        except Exception as e:
            print('Error occurred while parsing line', row['index'])
            raise e
    return sorted([
        *[row for row in parsed_rows if row['skip']],
        *post_process([row for row in parsed_rows if not row['skip']])
    ], key=lambda table_row: table_row['index'])


def import_lines(source: Database, target: Database, file: Dict[str, Any]):
    source_lines = [*get_lines(
        source,
        str(file['_id']),
        ASCENDING,
        projection={'delimiter': True, 'escape': True, 'quotation': True, 'rowType': True, 'raw': True, 'index': True,
                    'fileId': True, '_id': True}
    )]
    non_table_lines = [
        {k: v for k, v in line.items() if k in ['_id', 'fileId', 'index', 'raw']}
        for line in source_lines
        if not any(table['from'] <= line['index'] <= table['to'] for table in file['tables'])
    ]
    tables = [
        source_lines[table['from']:table['to'] + 1]
        for table in file['tables']
    ]
    try:
        parsed_tables = [
            parse_rows(table)
            for table in tables
        ]
        lines = [
            *[{**line, 'isPartOfTable': False} for line in non_table_lines],
        ]
        [
            lines.extend(parsed_table)
            for parsed_table in parsed_tables
        ]
        if lines:
            target['lines'].insert_many(lines)
    except Exception as e:
        print('Error occurred in file', file['_id'])
        print('Check your annotations! Error was:', e)
        print('Exiting...')
        exit(1)


def import_file_contents(source: Database, target: Database):
    target['lines'].create_indexes(indexes=[
        IndexModel('index'),
        IndexModel('fileId')
    ])
    files = target['files'].find(projection={'_id': True, 'tables': True})
    print('Find incomplete files...')
    incomplete_files = [
        file
        for file in files
        if target['lines'].count_documents(filter={'fileId': str(file['_id'])})
           <
           source['lines'].count_documents(filter={'fileId': str(file['_id'])})
    ]
    print('Import missing files...')
    [
        import_lines(source, target, incomplete_file)
        for incomplete_file in tqdm(incomplete_files)
    ]


#  this method will fetch all annotated files in the source database and import them into the target database
#  the file type (simple/ complex) will be automatically deferred
#  this method also import all file contents. each line will be parsed using the provided annotation.

def import_data(db: Database, target_mongo_uri: str, target_db: str):
    with MongoClient(target_mongo_uri) as target_mongo:
        target = target_mongo[target_db]
        import_files(db, target)
        import_file_contents(db, target)
