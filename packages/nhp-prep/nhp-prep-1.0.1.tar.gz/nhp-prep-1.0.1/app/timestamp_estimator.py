# Timestamp Estimator
"""
  Module that estimates the trial start time from the start time epoch timestamp and the Time 
  column (which records the end time in ms since the start time) 
"""

import datetime
from datetime import datetime as dt
import pandas as pd

from app.main_logger import logger

TRIAL_START_TIME_COL = "TrialStartTimestamp"
TRIAL_START_TIME_MS = "TrialStartTime"
EXP_START_TIME_COL = "ExpStartTimestamp"
TIME_COL = "Time"


def change_timestamp(filename: str):
    """Function that creates an estimated time from the start time epoch
    timestamp and the Time column (which records the end time in ms
    since the start time)
    It will add the value in the Time column to the value in the
    ExpStartTimestamp column, and parse the format to be hh:mm:ss;ms
    Args:
        filename (str): The name of the file to be modified

    Returns:
        file_date: The modified file data
    """
    file_data = pd.read_csv(filename)
    logger.warning(
        "File %s does not have a trial start timestamp. "
        "We will proceed to calculate it...",
        filename,
    )
    # 1. read from the time column and add that to the start time
    for index, trial in file_data.iterrows():
        # 2. read timestamp of the start of the exp from col (example: 11:47:57,444)
        # if the file does not contain a start timestamp
        if pd.isnull(trial[EXP_START_TIME_COL]):
            continue
        # if the file already has "TrialStartTimestamp", no need to change it
        if not pd.isnull(trial[TRIAL_START_TIME_COL]):
            continue
        # if pd.isnull(trial[TIME_COL]):  # don't have info to check the time
        #    continue
        start_time = dt.strptime(trial[EXP_START_TIME_COL], "%X,%f")
        time_from_start = (
            trial[TIME_COL]
            if not pd.isnull(trial[TIME_COL])
            else trial[TRIAL_START_TIME_MS]
        )
        try:
            estimate_time = start_time + datetime.timedelta(
                milliseconds=time_from_start
            )
            # To trim the last three zeros
            datestr = estimate_time.strftime("%X,%f")[:-3]
            file_data.at[index, TRIAL_START_TIME_COL] = datestr
        except Exception as caught_exception:
            logger.error(
                "Error while trying to estimate the trial start time for file %s: %s",
                filename,
                caught_exception,
            )

    return file_data
