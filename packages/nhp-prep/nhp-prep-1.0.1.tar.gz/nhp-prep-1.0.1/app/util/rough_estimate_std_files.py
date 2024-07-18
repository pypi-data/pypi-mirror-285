import os
import re

from app.main_logger import logger

import pandas as pd

HOUR_ENDING = "h"
SEPARATOR_TAG = "_"
MS_SEPARATOR = ","
COLON = ":"
DOUBLE_ZERO = "00"

TRIAL_START_COL = "TrialStartTimestamp"
EXP_START_TS = 'ExpStartTimestamp'
HHMMSS_FORMAT = '%H:%M:%S'

# to fully comply the naming patterns of existing csv files
# see ./README.md:115
STD_FILENAME_PATTERN = r'^\d{4}-\d{2}-\d{2}_\d{4}h_(.*?_)+data.csv$'


def estimate_time(filepath, filename, output_path):
    file_data = pd.read_csv(filepath)
    # parse the file name for the month, day, year and start time
    full_time_str = filename.split(HOUR_ENDING)[0]
    _date_str = full_time_str.split(SEPARATOR_TAG)[0]
    # parse the file start time in this format: hh:mm:00
    hour_str = full_time_str.split(SEPARATOR_TAG)[1]
    hours = hour_str[:-2]
    minutes = hour_str[2:]
    start_time = hours + COLON + minutes + COLON + DOUBLE_ZERO + MS_SEPARATOR + "000"

    file_data[EXP_START_TS] = file_data[EXP_START_TS].fillna(start_time)
    file_data.to_csv(output_path, index=False)


def dir_time_estimate(input_dir: str, output_dir: str):
    """A general function that estimate the rough experiment
    start timestamp of files with standard filenames

    Args:
        input_dir (str): the directory in
        which the files (CSV) have been stored.

        output_dir (str): the output directory to
        output all modified files.
    """
    if not os.path.exists(input_dir):
        logger.error(
            f'Path {input_dir} passed does not exist. Please make sure the path is correct!')
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f'Temporary output directory {output_dir} created.')

    _std_compiled = re.compile(STD_FILENAME_PATTERN)

    files = [each for each in os.listdir(input_dir) if each.endswith('.csv')]

    for file in files:
        try:
            if not _std_compiled.fullmatch(file):
                logger.info(
                    f'The filename {file} does not match the standard filename pattern.')
                logger.info(f'Skipping this file...')
            else:
                filepath = os.path.join(input_dir, file)
                output_path = os.path.join(output_dir, file)
                estimate_time(filepath, file, output_path)
        except Exception as e:
            logger.error(
                f'There was an error in the file {filepath}. Please check the following error: {e}')
    logger.info('Process completed!')
