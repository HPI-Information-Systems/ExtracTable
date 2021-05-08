from typing import Dict, Any

from flatten_dict import flatten
from pymongo import UpdateOne
from pymongo.database import Database

from eval.evaluate_parser import expand_table_jaccard, calculate_f1_matrix, f1_matrix_to_overlap_matrix, get_match_type
from utils.overlap import Overlap
from utils.utils import stringify_dict


def get_table_metrics(pytheas_file: Dict[str, Any]) -> Dict[str, Any]:
    f1_matrix = calculate_f1_matrix(pytheas_file['GT'], pytheas_file['RT'])
    overlap_matrix = f1_matrix_to_overlap_matrix(f1_matrix)
    rt_table_lines = set(index for table in pytheas_file['RT'] for index in range(table['from'], table['to'] + 1))
    return {
        'tables': [
            {
                'from': table['from'],
                'to': table['to'],
                'type': table['type'],
                'jaccard': max(
                    expand_table_jaccard(table, pytheas_file['RT']),
                    key=lambda other: other['jaccard'],
                    default={'jaccard': 0}
                )['jaccard'],
                'coverage': len(rt_table_lines & set(range(table['from'], table['to'] + 1))) / (table['to'] - table['from'] + 1),
                'matchType': get_match_type(overlap_matrix, i_table)
            }
            for i_table, table in enumerate(pytheas_file['GT'])
        ],
        'expected': len(pytheas_file['GT']),
        'got': len(pytheas_file['RT']),
        'falsePositives': sum(
            all(overlap_matrix[i_GT][i_RT] == Overlap.NONE for i_GT in range(len(pytheas_file['GT'])))
            for i_RT in range(len(pytheas_file['RT']))
        )
    }


def get_line_metrics(pytheas_file: Dict[str, Any]) -> Dict[str, Any]:
    lines = set(range(pytheas_file['lineCount']))
    gt_table_lines = set(index for table in pytheas_file['GT'] for index in range(table['from'], table['to'] + 1))
    gt_non_table_lines = lines - gt_table_lines
    rt_table_lines = set(index for table in pytheas_file['RT'] for index in range(table['from'], table['to'] + 1))
    rt_non_table_lines = lines - rt_table_lines
    return {
        str((False, False)): len(gt_non_table_lines & rt_non_table_lines),
        str((False, True)): len(gt_non_table_lines & rt_table_lines),
        str((True, False)): len(gt_table_lines & rt_non_table_lines),
        str((True, True)): len(gt_table_lines & rt_table_lines)
    }


def get_metrics(pytheas_file: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'metrics': {
            **get_line_metrics(pytheas_file),
            **get_table_metrics(pytheas_file)
        }
    }


def evaluate_pytheas(db: Database):
    pytheas = db['pytheas'].aggregate([
        {
            '$lookup': {
                'from': 'files',
                'let': {
                    'fileId': {
                        '$toObjectId': '$fileId'
                    }
                },
                'pipeline': [
                    {
                        '$match': {
                            '$expr': {
                                '$eq': [
                                    '$_id', '$$fileId'
                                ]
                            }
                        }
                    }
                ],
                'as': 'file'
            }
        }, {
            '$unwind': {
                'path': '$file'
            }
        }, {
            '$project': {
                '_id': True,
                'RT': '$tables',
                'GT': '$file.tables',
                'lineCount': '$file.lineCount'
            }
        }
    ])
    updates = [
        UpdateOne(
            filter={'_id': pytheas_file['_id']},
            update={'$set': stringify_dict(flatten(get_metrics(pytheas_file), reducer='underscore'))}
        )
        for pytheas_file in pytheas
    ]
    db['pytheas'].bulk_write(updates)
