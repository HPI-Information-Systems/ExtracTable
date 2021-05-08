import logging
from datetime import datetime
from pathlib import Path
from shutil import rmtree
from time import process_time
from typing import List

import fire

from BlockFactory import BlockFactory
from compact_advisors.CompactAdvisor import CompactAdvisor
from compact_advisors.CompactOnCombinationLimit import CompactOnCombinationLimit
from consumers.PICounter import ParsingInstructionsCounter
from consumers.TableSelection import TableSelection
from pipeline.Pipeline import Pipeline
from producers.FileReader import FileReader
from transformers.BuildSolutionSpace import BuildSolutionSpace
from transformers.CharacterDelimiterDetection import CharacterDelimiterDetection
from transformers.LayoutDelimiterDetection import LayoutDelimiterDetection, get_max_line_width_of_file
from transformers.LineBouncer import LineBouncer
from transformers.LineFeatureExtraction import LineFeatureExtraction
from transformers.TableFactory import TableFactory


class TableExtractor(object):
    compact_advisors = {
        'dynamic': CompactOnCombinationLimit
    }

    @staticmethod
    def __create_pipeline__(
            input_file: Path,
            output: Path,
            compact_advisor: CompactAdvisor,
            min_block_compatibility: float,
            block_min_column_consistency: float,
            final_min_column_consistency: float,
            max_character_delimiter_length: int,
            max_quotation_escape_length: int,
            delimiter_character_blacklist: List[str],
            essential_row_count: int,
            min_data_rows: int,
            min_col_count: int,
            empty_lines_delimits_tables: bool,
            min_table_consistency: float,
            known_patterns_file: Path,
            use_strict_bin_key: bool,
            enable_post_processing: bool,
            use_heuristic: bool,
            enable_ascii: bool,
            save: bool
    ):
        if save:
            if output.exists():
                rmtree(output)
            output.mkdir(exist_ok=True, parents=True)
        width = get_max_line_width_of_file(input_file)
        block_factory = BlockFactory(
            compact_advisor=compact_advisor,
            min_compatibility=min_block_compatibility,
            min_column_consistency=block_min_column_consistency
        )
        return Pipeline(
            FileReader(file_path=input_file),
            [
                LineBouncer(width=width),
                CharacterDelimiterDetection(
                    max_delimiter_length=max_character_delimiter_length,
                    delimiter_character_blacklist=delimiter_character_blacklist
                ),
                *([LayoutDelimiterDetection(
                    width,
                    min_row_count=min_data_rows,
                    min_col_count=min_col_count,
                    essential_row_count=essential_row_count,
                )] if enable_ascii else []),
                BuildSolutionSpace(
                    empty_line_delimits_table=empty_lines_delimits_tables,
                    use_strict_bin_key=use_strict_bin_key,
                    max_quotation_escape_length=max_quotation_escape_length,
                    enable_ascii=enable_ascii
                ),
                LineFeatureExtraction(known_patterns_file=known_patterns_file),
                TableFactory(
                    block_factory,
                    min_col_count=min_col_count,
                    min_data_rows=min_data_rows,
                    max_header_rows=4,
                    use_strict_bin_key=use_strict_bin_key,
                    enable_post_processing=enable_post_processing,
                    final_min_column_consistency=final_min_column_consistency
                )
            ],
            TableSelection(
                output_file_path=output,
                min_table_consistency=min_table_consistency,
                use_heuristic=use_heuristic,
                save=save
            )
        )

    def extract(
            self,
            input_file: str,
            output_dir: str = './tmp/',
            compact_advisor: str = 'dynamic',
            compact_size: int = 100,
            min_block_compatibility: float = 0.71,
            block_min_column_consistency: float = 0.31,
            final_min_column_consistency: float = 0.51,
            max_character_delimiter_length: int = 4,
            max_quotation_escape_length: int = 2,
            delimiter_character_blacklist: List[str] = None,
            essential_row_count: int = 4,
            min_data_rows: int = 2,
            min_col_count: int = 2,
            empty_lines_delimits_tables: bool = False,
            enable_datatype_recognition: bool = True,
            min_table_consistency: float = 0.51,
            use_strict_bin_key: bool = True,
            enable_post_processing: bool = False,
            use_heuristic: bool = False,
            enable_ascii: bool = True,
            debug: bool = False,
            save: bool = True
    ):
        if debug:
            logging.basicConfig(level=logging.INFO)
        logging.info('Started at: ' + str(datetime.now()))
        start = process_time()
        pipeline = self.__create_pipeline__(
            input_file=Path(input_file),
            output=Path(output_dir),
            compact_advisor=self.compact_advisors[compact_advisor](compact_size),
            min_block_compatibility=min_block_compatibility,
            block_min_column_consistency=block_min_column_consistency,
            final_min_column_consistency=final_min_column_consistency,
            max_character_delimiter_length=max_character_delimiter_length,
            max_quotation_escape_length=max_quotation_escape_length,
            delimiter_character_blacklist=['<', '>', '(', ')', '[', ']', '{', '}'] if delimiter_character_blacklist is None else delimiter_character_blacklist,
            essential_row_count=essential_row_count,
            min_data_rows=min_data_rows,
            min_col_count=min_col_count,
            empty_lines_delimits_tables=empty_lines_delimits_tables,
            known_patterns_file=Path(
                __file__).parent / 'data_type_patterns.txt' if enable_datatype_recognition else None,
            min_table_consistency=min_table_consistency,
            use_strict_bin_key=use_strict_bin_key,
            enable_post_processing=enable_post_processing,
            use_heuristic=use_heuristic,
            enable_ascii=enable_ascii,
            save=save
        )
        result = pipeline.run()
        logging.info('Finished at: ' + str(datetime.now()))
        logging.info('Elapsed time: ' + str(round(process_time() - start, 2)) + ' seconds')
        return result

    @staticmethod
    def pi_count(
            input_file: str,
            max_character_delimiter_length: int = 4,
            max_quotation_escape_length: int = 2,
            min_data_rows: int = 2,
            min_col_count: int = 2,
            empty_lines_delimits_tables: bool = False,
            use_strict_bin_key: bool = True
    ):
        width = get_max_line_width_of_file(Path(input_file))
        pipeline = Pipeline(
            FileReader(file_path=Path(input_file)),
            [
                LineBouncer(width=width),
                CharacterDelimiterDetection(
                    max_delimiter_length=max_character_delimiter_length,
                    delimiter_character_blacklist=['<', '>', '(', ')', '[', ']', '{', '}']
                ),
                LayoutDelimiterDetection(
                    width,
                    min_row_count=min_data_rows,
                    min_col_count=min_col_count,
                    essential_row_count=4
                ),
                BuildSolutionSpace(empty_line_delimits_table=empty_lines_delimits_tables,
                                   use_strict_bin_key=use_strict_bin_key, max_quotation_escape_length=max_quotation_escape_length),
            ],
            ParsingInstructionsCounter()  # prints parsing instruction count per type of whole file
        )
        pipeline.run()


if __name__ == '__main__':
    fire.Fire(TableExtractor)
