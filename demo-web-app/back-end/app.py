import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from werkzeug.utils import secure_filename

sys.path.insert(0,
                '../../table-extraction/table_extractor')
from Main import TableExtractor

from multiprocessing import Process, Manager
from resource import getrusage, RUSAGE_CHILDREN
from typing import Dict, List

from flask import Flask, abort, request
from werkzeug.exceptions import GatewayTimeout, BadRequest

MAX_THREADS = 2
TIMEOUT_IN_SECONDS = 60
app = Flask("__main__")


def map_tables(tables: List[Dict]) -> List[Dict]:
    return [
        {
            **({
                k: v
                for k, v in table.items()
                if k in ['from', 'to', 'headerRows', 'dataRows', 'headerConsistency', 'dataConsistency', 'content']
            }),
            'columns': table['storedColCount'],
            'parsingInstruction': {
                'type': 'ASCII'
            } if table['binKey'][1] == 'layout' else {
                'type': 'CSV',
                'dialect': {
                    'delimiter': table['binKey'][2],
                    'quotation': None if table['binKey'][3] == 'None' else table['binKey'][3],
                    'escape': None if table['binKey'][4] == 'None' else table['binKey'][4]
                }
            }
        }
        for table in tables
    ]


def prepare_result(tables: List[Dict], run_time: float) -> Dict:
    return {
        'runTime': run_time,
        'tables': map_tables(tables)
    }


@app.route('/extract', methods=['POST'])
def route_extract():
    if 'inputFile' not in request.files or not request.files['inputFile'].filename:
        return abort(BadRequest.code, 'No input file found. Please provide an input file!')
    input_file = request.files['inputFile']
    with TemporaryDirectory() as working_dir:
        input_file_path = Path(working_dir) / secure_filename(input_file.filename)
        input_file.save(input_file_path)
        job = {
            'input_file': str(input_file_path.resolve()),
            'save': False,
            'enable_post_processing': True
        }
        manager = Manager()
        result = manager.list()
        process = Process(target=extractable_wrapper, args=(job, result))
        start = getrusage(RUSAGE_CHILDREN).ru_utime
        process.start()
        process.join(TIMEOUT_IN_SECONDS)
        run_time = getrusage(RUSAGE_CHILDREN).ru_utime - start
        if process.is_alive():
            process.terminate()
            process.join()
            return abort(
                GatewayTimeout.code,
                description='Could not process file within 60 seconds. Please try again locally!'
            )
        else:
            return prepare_result(result, run_time)


def extractable_wrapper(job: Dict, result: List[Dict]):
    result.extend(TableExtractor().extract(**job))


if __name__ == '__main__':
    app.run(processes=MAX_THREADS)
