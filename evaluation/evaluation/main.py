from json import dumps
from multiprocessing import cpu_count
from pathlib import Path
from typing import Optional

from fire import Fire
from flatten_dict import flatten
from pymongo import MongoClient

from eval.evaluate_parsers import evaluate_parsers
from eval.evaluate_pytheas import evaluate_pytheas
from eval.grid_search import grid_search
from preparation.clever_csv_import import import_clever_csv
from preparation.collect_parsing_instruction_counts import collect_parsing_instruction_counts
from preparation.download_files import download_files
from preparation.import_data import import_data
from preparation.parse_files import parse_files
from preparation.pytheas import get_pytheas_table_ranges


class Evaluation:

    def __init__(self, mongo_uri: Optional[str] = None, db: str = 'master'):
        self.mongo_uri = mongo_uri
        self.database_name = db
        self.mongo = MongoClient(mongo_uri)
        if not (db in self.mongo.list_database_names()):
            raise Exception('Database could not be found!')
        self.db = self.mongo[db]

    # Preparation

    def import_clever_csv(self, input_file: str, data_dir: str, source: str):
        #  import clever csv files for annotation in labeling tool
        import_clever_csv(self.db, Path(input_file), Path(data_dir), source)

    def import_data(self, target_mongo_uri: str, target_db: str):
        #  import annotated files with their content from source database (that the annotation tool accesses) to a target database (used for evaluation)
        import_data(self.db, target_mongo_uri, target_db)

    def download_files(self, target: str = './data/'):
        #  persist file contents to disk
        target_path = Path(target)
        target_path.mkdir(exist_ok=True)
        download_files(self.db, target_path)

    def parse_files(self, data_dir: str = './data/', target_dir: str = './parsed/', cores: int = cpu_count(),
                    timeout: int = 900):
        #  parse all files with each parser and store results to disk
        parse_files(self.db, Path(data_dir), Path(target_dir), cores, timeout)

    def collect_parsing_instruction_counts(self, data_dir: str = './data/', cores: int = cpu_count(), timeout: int = 300):
        collect_parsing_instruction_counts(self.db, Path(data_dir), cores, timeout)

    def pytheas(self, data_dir: str = './data/', cores: int = cpu_count(), timeout: int = 600):
        get_pytheas_table_ranges(self.db, Path(data_dir), cores, timeout)

    # Evaluation

    def grid_search(self, data_dir: str = './data/', timeout: int = 300, cores: int = cpu_count()):
        #  run grid search and return aggregated metrics for each configuration
        fixed_configuration = {
            'compact_advisor': 'dynamic',
            'compact_size': 50,
            'max_character_delimiter_length': 4,
            'min_data_rows': 2,
            'min_col_count': 2,
            'empty_lines_delimits_tables': False,
            'enable_datatype_recognition': True,
            'use_strict_bin_key': True,
            'enable_post_processing': False,
            'debug': False,
            'min_block_compatibility': 0.71,
            'block_min_column_consistency': 0.31,
            'final_min_column_consistency': 0.51,
            'min_table_consistency': 0.51
        }
        variable_configuration = {
            'essential_row_count': [*range(2, 9)]
        }
        results = grid_search(
            self.db,
            self.mongo_uri,
            self.database_name,
            fixed_configuration,
            variable_configuration,
            Path(data_dir),
            timeout,
            cores
        )
        print(dumps([flatten(result, reducer='underscore') for result in results]))

    def evaluate_parsers(self, parsed_dir: str = './parsed/', cores: int = cpu_count()):
        #  evaluate each parser by looking at parsed results returned from parse_files
        evaluate_parsers(self.db, self.mongo_uri, self.database_name, Path(parsed_dir), cores)

    def min_row_count_experiment(self, data_dir: str = './data/', timeout: int = 300, cores: int = cpu_count()):
        fixed_configuration = {
            'compact_advisor': 'dynamic',
            'compact_size': 50,
            'max_character_delimiter_length': 4,
            'max_quotation_escape_length': 2,
            'min_col_count': 2,
            'empty_lines_delimits_tables': False,
            'enable_datatype_recognition': True,
            'use_strict_bin_key': True,
            'enable_post_processing': False,
            'debug': False,
            'min_block_compatibility': 0.71,
            'block_min_column_consistency': 0.31,
            'final_min_column_consistency': 0.11,
            'min_table_consistency': 0.51
        }
        variable_configuration = {
            'min_data_rows': [*range(2, 11)]
        }
        results = grid_search(
            self.db,
            self.mongo_uri,
            self.database_name,
            fixed_configuration,
            variable_configuration,
            Path(data_dir),
            timeout,
            cores
        )
        print(dumps([flatten(result, reducer='underscore') for result in results]))

    def evaluate_pytheas(self):
        evaluate_pytheas(self.db)

    def __del__(self):
        self.mongo.close()
        del self


if __name__ == '__main__':
    Fire(Evaluation)
