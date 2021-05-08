from collections import Counter
from multiprocessing import Pool
from pathlib import Path
from statistics import mean, stdev
from tempfile import TemporaryDirectory
from typing import Dict, Any, List, Optional

from pymongo import ASCENDING, MongoClient
from pymongo.database import Database
from tqdm import tqdm

from eval.evaluate_parser import collect_metrics
from preparation.file_parser import unpack_parse_file
from utils.combinations import Combinations
from utils.parser import Parser


def build_configuration(
        fixed_configuration: Dict[str, Any],
        variable_configurations: Dict[str, List[Any]],
        setting: List[int]
) -> Dict[str, Any]:
    return {
        **fixed_configuration,
        **{k: v[setting[i_key]] for i_key, (k, v) in enumerate(variable_configurations.items())}
    }


def evaluate_parser(mongo_uri: str, database_name: str, file: Dict[str, Any], tables_dir: Path, status: str) -> Optional[Dict[str, Any]]:
    if status != 'success':
        return None
    with MongoClient(mongo_uri) as mongo:
        db = mongo[database_name]
        return collect_metrics(db, file, tables_dir)


def unpack_evaluate_parser(args):
    return evaluate_parser(*args)


def aggregate_metrics(metrics: List[Dict[str, Any]]):
    success_metrics = [metric for metric in metrics if metric['status'] == 'success']
    correctly_parsed_clean = [metric['lineMetrics']['correctlyParsedClean'] for metric in success_metrics if metric['lineMetrics']['correctlyParsedClean']]
    return {
        'status': sum((Counter({metric['status']: 1}) for metric in metrics), Counter()),
        'confusion': sum((metric['lineMetrics']['confusion'] for metric in success_metrics), Counter()),
        'lineCount': sum(metric['lineMetrics']['lineCount'] for metric in success_metrics),
        'correctlyParsedClean': mean(correctly_parsed_clean) if correctly_parsed_clean else 0,
        'jaccardAvg': mean(table['jaccard'] for metric in success_metrics for table in metric['tableMetrics']['tables']),
        'jaccardStdDev': stdev(table['jaccard'] for metric in success_metrics for table in metric['tableMetrics']['tables']),
        'expected': sum(metric['tableMetrics']['expected'] for metric in success_metrics),
        'got': sum(metric['tableMetrics']['got'] for metric in success_metrics),
        'expectedGotRatio': mean(metric['tableMetrics']['got'] / metric['tableMetrics']['expected'] for metric in success_metrics),
        'eager': sum(metric['tableMetrics']['eager'] for metric in success_metrics),
        'matchTypesGT': sum((Counter({table['matchType']: 1}) for metric in success_metrics for table in metric['tableMetrics']['tables']), Counter()),
        'matchTypeFalsePositive': sum(metric['tableMetrics']['falsePositive'] for metric in success_metrics)
    }


def get_parser_jobs(
        dataset_dir: Path,
        files: List[Dict[str, Any]],
        configurations: List[Dict[str, Any]],
        timeout_in_seconds: int,
        working_directories: List[TemporaryDirectory]
):
    return [
        (
            Parser.TABLE_EXTRACTOR,
            dataset_dir / (file['hash'] + '.txt'),
            Path(working_dir.name) / Parser.TABLE_EXTRACTOR.value / file['hash'],
            timeout_in_seconds,
            configuration
        )
        for configuration, working_dir in zip(configurations, working_directories)
        for file in files
    ]


def get_evaluation_jobs(
        run_times: List[Dict[str, Any]],
        files: List[Dict[str, Any]],
        mongo_uri: str,
        database_name: str,
        working_directories: List[TemporaryDirectory],
):
    return [
        (
            mongo_uri,
            database_name,
            file,
            Path(working_dir.name) / Parser.TABLE_EXTRACTOR.value / file['hash'],
            run_time['status']
        )
        for i_working_dir, working_dir in enumerate(working_directories)
        for file, run_time in zip(files, run_times[i_working_dir * len(files):][:len(files)])
    ]


def grid_search(
        db: Database,
        mongo_uri: str,
        database_name: str,
        fixed_configuration: Dict[str, Any],
        variable_configurations: Dict[str, List[Any]],
        dataset_dir: Path,
        timeout_in_seconds: int,
        cores: int
):
    files = [*db['grid_search_files'].find().sort('_id', ASCENDING)]
    configurations = [
        build_configuration(fixed_configuration, variable_configurations, setting)
        for setting in Combinations([len(setting) for setting in variable_configurations.values()])
    ]
    working_directories = [TemporaryDirectory() for _ in configurations]
    parser_jobs = get_parser_jobs(
        dataset_dir,
        files,
        configurations,
        timeout_in_seconds,
        working_directories
    )
    with Pool(cores) as pool:
        run_times = [*tqdm(pool.imap(unpack_parse_file, parser_jobs), total=len(parser_jobs))]
        evaluation_jobs = get_evaluation_jobs(run_times, files, mongo_uri, database_name, working_directories)
        metrics = [*tqdm(pool.imap(unpack_evaluate_parser, evaluation_jobs), total=len(evaluation_jobs))]
    [working_dir.cleanup() for working_dir in working_directories]
    return [
        {
            **{setting: value for setting, value in configuration.items() if setting in variable_configurations.keys()},
            **aggregate_metrics([
                {**metric, **run_time}
                for metric, run_time in zip(
                    metrics[i_configuration * len(files):][:len(files)],
                    run_times[i_configuration * len(files):][:len(files)]
                )
                if run_time['status'] == 'success'
            ])
        }
        for i_configuration, configuration in enumerate(configurations)
    ]
