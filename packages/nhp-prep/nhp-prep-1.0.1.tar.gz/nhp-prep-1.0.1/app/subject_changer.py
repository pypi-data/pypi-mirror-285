"""
This module contains the functions that change the subject name to the subject name
specified in the reference file within the specified time range.
"""

import time
import datetime
import os

import pandas as pd

from app.main_logger import logger

REF_START_COL = "Start"
REF_END_COL = "End"
REF_DATE_COL = "Date"
REF_SUB_COL = "Sub"
REF_TYPE_COL = "Type"
REF_SETTINGS_COL = "Settings"

TRIAL_START_COL = "TrialStartTimestamp"
SUB_COL = "Sub"
SUB_TEST = "TEST"
SUB_AMBIGUOUS = "AMBIGUOUS"

HHMMSS_FORMAT = "%H:%M:%S"
HHMMSSFFF_FORMAT = "%H:%M:%S,%f"
STD_DATE_FORMAT = "%m/%d/%Y"
SHORT_DATE_FORMAT = "%m/%d/%y"
HOUR_ENDING = "h"
HYPHEN_CHAR = "-"
SEPARATOR_TAG = "_"
BACKSLASH = "/"
COLON = ":"
DOUBLE_ZERO = "00"


def str_date_validate(date_str: str) -> str:
    """
    Function that validates that the date string is in the correct format.
    If not, then it converts it into DD/MM/YYYY

    Args:
        date_str (str): The string date to validate

    Returns:
        str: The date string in the correct format.
    """
    res = True
    try:
        res = bool(datetime.datetime.strptime(date_str, STD_DATE_FORMAT))
    except ValueError:
        res = False

    if not res:
        try:
            parsed_time = datetime.datetime.strptime(date_str, SHORT_DATE_FORMAT)
            return parsed_time.strftime(STD_DATE_FORMAT)
        except ValueError:
            logger.debug("Error while parsing the date: %s", date_str)
    logger.debug("Date already in the correct format: %s", date_str)
    return date_str


def fill_ref_file_dates(ref_file: str):
    """Function that fills the missing start and end times within the same
    day with the same date as the previous row.

    Args:
        ref_dataframe (pd.DataFrame): The reference file DataFrame.

    Returns:
        pd.DataFrame: The modified DataFrame.
    """
    ref_dataframe = pd.read_csv(ref_file)

    # First, we transform the date column to a datetime object, and the start
    # and end columns to a time object
    ref_dataframe[REF_DATE_COL] = pd.to_datetime(
        ref_dataframe[REF_DATE_COL], format=STD_DATE_FORMAT
    )
    # Convert the 'Date' column to a string format only MM/DD/YYYY
    # ref_dataframe[REF_DATE_COL] = ref_dataframe[REF_DATE_COL].dt.strftime(
    #    STD_DATE_FORMAT
    # )

    for index, row in ref_dataframe.iterrows():
        ref_dataframe.at[index, REF_START_COL] = time.strptime(
            row[REF_START_COL], HHMMSS_FORMAT
        )
        # Now, we update the year, month and day of the time.struct_time object
        # with the year, month and day of the date object from column REF_DATE_COL
        ref_dataframe.at[index, REF_START_COL] = time.struct_time(
            (
                row[REF_DATE_COL].year,
                row[REF_DATE_COL].month,
                row[REF_DATE_COL].day,
                ref_dataframe.at[index, REF_START_COL].tm_hour,
                ref_dataframe.at[index, REF_START_COL].tm_min,
                ref_dataframe.at[index, REF_START_COL].tm_sec,
                ref_dataframe.at[index, REF_START_COL].tm_wday,
                ref_dataframe.at[index, REF_START_COL].tm_yday,
                ref_dataframe.at[index, REF_START_COL].tm_isdst,
            )
        )
        ref_dataframe.at[index, REF_END_COL] = time.strptime(
            row[REF_END_COL], HHMMSS_FORMAT
        )
        # We do the same update for the end time
        ref_dataframe.at[index, REF_END_COL] = time.struct_time(
            (
                row[REF_DATE_COL].year,
                row[REF_DATE_COL].month,
                row[REF_DATE_COL].day,
                ref_dataframe.at[index, REF_END_COL].tm_hour,
                ref_dataframe.at[index, REF_END_COL].tm_min,
                ref_dataframe.at[index, REF_END_COL].tm_sec,
                ref_dataframe.at[index, REF_END_COL].tm_wday,
                ref_dataframe.at[index, REF_END_COL].tm_yday,
                ref_dataframe.at[index, REF_END_COL].tm_isdst,
            )
        )

    # Next, we filter a unique set of dates.
    dates = ref_dataframe[REF_DATE_COL].unique()

    # Now, we iterate over the unique dates and insert the missing start and end times
    # based on the previous and next rows. I.e.: if the start time of one row
    # is more than 1 millisecond greater than the end time of the previous row,
    # we add a new row of the missing start time with the end time of the previous
    # row plus 1 millisecond, and the new missing end time with the start time
    # of the next row minus 1 millisecond.
    for date in dates:
        date_rows = ref_dataframe[ref_dataframe[REF_DATE_COL] == date]
        for i in range(1, len(date_rows)):
            prev_row = date_rows.iloc[i - 1]
            curr_row = date_rows.iloc[i]
            delta_time = datetime.timedelta(
                milliseconds=time.mktime(curr_row[REF_START_COL])
                - time.mktime(prev_row[REF_END_COL])
            )
            if delta_time > datetime.timedelta(milliseconds=1):
                converted_prev_end = datetime.datetime.fromtimestamp(
                    time.mktime(prev_row[REF_END_COL])
                )
                converted_curr_start = datetime.datetime.fromtimestamp(
                    time.mktime(curr_row[REF_START_COL])
                )
                new_start = converted_prev_end + datetime.timedelta(milliseconds=1)
                new_end = converted_curr_start - datetime.timedelta(milliseconds=1)
                new_row = pd.DataFrame(
                    [
                        [
                            new_start.timetuple(),
                            new_end.timetuple(),
                            date,
                            prev_row[REF_SUB_COL],
                            prev_row[REF_TYPE_COL],
                            prev_row[REF_SETTINGS_COL],
                        ]
                    ],
                    columns=[
                        REF_START_COL,
                        REF_END_COL,
                        REF_DATE_COL,
                        REF_SUB_COL,
                        REF_TYPE_COL,
                        REF_SETTINGS_COL,
                    ],
                )
                ref_dataframe = pd.concat([ref_dataframe, new_row], ignore_index=True)
    # Then we sort the dataframe by date and start time and reset the index
    ref_dataframe = ref_dataframe.sort_values(
        by=[REF_DATE_COL, REF_START_COL], ignore_index=True
    )
    # We transform the date column back to a string format only HH:MM:SS
    ref_dataframe[REF_DATE_COL] = ref_dataframe[REF_DATE_COL].dt.strftime(
        STD_DATE_FORMAT
    )
    ref_dataframe[REF_START_COL] = ref_dataframe[REF_START_COL].apply(
        lambda x: time.strftime(HHMMSS_FORMAT, x)
    )
    ref_dataframe[REF_END_COL] = ref_dataframe[REF_END_COL].apply(
        lambda x: time.strftime(HHMMSS_FORMAT, x)
    )
    # Save this new dataframe to a new reference file
    logger.info("Saving the new reference file...")
    # Create a filename based on date and time
    new_ref_filename = (
        datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + "_reference_file.csv"
    )
    ref_dataframe.to_csv(new_ref_filename, index=False)

    current_directory = os.getcwd()

    # Get the full path of the saved file
    full_path = os.path.join(current_directory, new_ref_filename)

    logger.info("New reference file saved: %s", full_path)
    return (ref_dataframe, full_path)


def change_sub(file_path: str, filename: str, ref_filename: str):
    """Function that changes the subject name to the subject name
    specified in the reference file within the specified time range
    If the name is not specified, put "AMBIGUOUS" as the subject name.
    Args:
        file_path (str): the full path to the file to be changed
        filename (str): the name of the file to be changed
        ref_filename (str): the name of the reference file

    Returns:
        file_data: the modified content of the file
    """
    ref_data = pd.read_csv(ref_filename)
    file_data = pd.read_csv(file_path)

    # 1. parse the file name for the month, day and year, and change it to this format mm/dd/yyyy
    full_time_str = filename.split(HOUR_ENDING)[0]
    date_str = full_time_str.split(SEPARATOR_TAG)[0]
    dates_array = date_str.split(HYPHEN_CHAR)
    new_date_format = (
        dates_array[1] + BACKSLASH + dates_array[2] + BACKSLASH + dates_array[0]
    )
    # 2. parse the file start time in this format: hh:mm:00
    hour_str = full_time_str.split(SEPARATOR_TAG)[1]
    hours = hour_str[:-2]
    minutes = hour_str[2:]
    new_hours_format = hours + COLON + minutes + COLON + DOUBLE_ZERO
    file_start_time = time.strptime(new_hours_format, HHMMSS_FORMAT)
    # 3. search for the first row that contains the matching date and time in
    # the baboons file
    for _, trial_ref in ref_data.iterrows():
        # find the corresponding date
        if new_date_format != str_date_validate(trial_ref[REF_DATE_COL]):
            continue
        # 3_1 parse the start time to a date
        subject_start_time = time.strptime(trial_ref[REF_START_COL], HHMMSS_FORMAT)
        # 3_2 parse the end time to a date
        subject_end_time = time.strptime(trial_ref[REF_END_COL], HHMMSS_FORMAT)
        if (
            subject_end_time < file_start_time
        ):  # means the file does not include the subject
            continue
        sub = trial_ref[REF_SUB_COL]
        # 4. loop through the data file
        for index, trial in file_data.iterrows():
            # skip the lines that don't have a start time
            if pd.isnull(trial[TRIAL_START_COL]):
                continue
            # 4_1 parse TrailStartTimestamp to a date
            start_time = time.strptime(trial[TRIAL_START_COL], HHMMSSFFF_FORMAT)
            # 4_2 transform the start_time to a datetime object
            dt_start_time = datetime.datetime.fromtimestamp(time.mktime(start_time))
            # 4_3 transform the subject_start_time to a datetime object
            dt_subject_start_time = datetime.datetime.fromtimestamp(
                time.mktime(subject_start_time)
            )
            # 4_4 transform the subject_end_time to a datetime object and
            # add 999 milliseconds
            dt_subject_end_time = datetime.datetime.fromtimestamp(
                time.mktime(subject_end_time)
            )
            dt_subject_end_time = dt_subject_end_time + datetime.timedelta(
                milliseconds=999
            )
            # 4_5 test if the trial start time stamp is greater than the start
            # time and less than the end time
            if (
                dt_start_time >= dt_subject_start_time
                and dt_start_time < dt_subject_end_time
            ):
                # 4_3 if yes, then change the subject to the corresponding
                # subject in the baboons file
                file_data.at[index, SUB_COL] = sub

    # 5 change the subjects without a name to "AMBIGUOUS"
    for index, trial in file_data.iterrows():
        if trial[SUB_COL] == SUB_TEST:
            file_data.at[index, SUB_COL] = SUB_AMBIGUOUS

    # 6 Sort the data by the TrialStartTimestamp
    file_data = file_data.sort_values(by=[TRIAL_START_COL], ignore_index=True)
    # 7 Save the modified file
    return file_data
