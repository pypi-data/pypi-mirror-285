""" This module contains the functions to rename the files based on the
standard naming pattern: 
YYYY-MM-DD_HHmmh_<experiment_name>_<Subject_name>_<Researcher_name_or_initials>_data.csv
"""

import os
import re
import shutil

from datetime import datetime

import pandas as pd

from app.main_logger import logger

EPOCH_PATTERN = r"\d{13}"
DIGITS_REGEX = r"\D"
EMPTY_SPACE = ""
SEPARATOR = "_"
COLON = ":"
COMMA = ","
DOT = "."
DATE_ENDING_CHAR = "h"
EXP_COL = "Exp"
SUB_COL = "Sub"
RESEARCHER_COL = "Researcher"
NAME_COL = "Name"
EXP_NAME_END = "data.csv"
EXP_START_TS = "ExpStartTimestamp"

# to fully comply the naming patterns of existing csv files
# see ./README.md:115
STD_FILENAME_PATTERN = r"^\d{4}-\d{2}-\d{2}_\d{4}h_(.*?_)+data.csv$"


def find_epoch(file: str):
    """Method that finds the EPOCH
    timestamp within the file.

    Args:
        file (str): The file to evaluate.

    Returns:
        string: The digits of the epoch timestamp only.
    """
    _compiled = re.compile(EPOCH_PATTERN)
    file_elements_list = file.split(SEPARATOR)
    _epoch = EMPTY_SPACE
    try:
        _filtered = list(filter(_compiled.match, file_elements_list))
        _epoch = list(_filtered)[0]
        # Removes any non-digit character from the epoch
        _epoch = re.sub(DIGITS_REGEX, EMPTY_SPACE, _epoch)
    except Exception:
        logger.error(
            "Error detected in file: %s. Please check the error: ", file, exc_info=True
        )
    return _epoch


def get_params_from_file(filepath: str):
    """Function that retrieves the list of the
    parameters that combined will create the
    new filename for the current file.

    Args:
        filepath (str): The entire file path.

    Returns:
        list: List with the following parameters:
            - Exp -> Experiment name
            - Sub -> Subject name
            - Researcher or Name -> The name of the researcher
    """
    params_list = list()
    try:
        file_df = pd.read_csv(filepath)
    except Exception:
        logger.error(
            "Error found in the file: %s. Please check for the issues: ",
            filepath,
            exc_info=True,
        )
        return params_list

    for each in [EXP_COL, SUB_COL, RESEARCHER_COL]:
        try:
            if each in file_df.columns and pd.notnull(file_df[each].iat[0]):
                params_list.append(file_df[each].iat[0])
        except Exception:
            logger.error(
                "Error has occurred while trying to retrieve one of the column names. Check: ",
                exc_info=True,
            )
    if (
        RESEARCHER_COL not in file_df.columns
        or pd.isnull(file_df[RESEARCHER_COL].iat[0])
    ) and NAME_COL in file_df.columns:
        if pd.isnull(
            file_df[NAME_COL].iat[0]
        ):  # dealing with the case when there is no researcher name
            params_list.append("AMBIGUOUS")
        else:
            params_list.append(file_df[NAME_COL].iat[0])
    return params_list


def find_std_pattern(filename: str):
    """Function to check if the filename
    already matches the current standard pattern
    of the file.

    It uses a REGEXP to evaluate the match or not.

    Args:
        filename (str): The filename to analyze.

    Returns:
        bool: True if the filename already matches the pattern.
              False if the filename does not match.
    """
    _std_compiled = re.compile(STD_FILENAME_PATTERN)
    if _std_compiled.fullmatch(filename):
        logger.warning("The filename %s already matches the pattern.", filename)
        logger.warning("Skipping this file...")
        return True
    return False


def copy_or_rename_file(filepath: str, new_filename: str, output=None):
    """Function to copy or rename the file based on the input.
    If the output path is not set, then this function will rename
    the file within its original path. Otherwise, it will copy the
    original file to a new location and it will update the name
    to follow the current standard for naming.

    Args:
        filepath (str): The full filename of the file.
        new_filename (str): It is the new filename.
        output (str, optional): Output path. Defaults to None.

    Returns:
        new_full_name (str): The new fullpath name.
    """
    original_path, _file = os.path.split(filepath)
    new_full_filename = ""
    # Renaming/Copying section
    if output is not None:
        if not os.path.exists(output):
            os.makedirs(output)  # Make sure the output path exists
        new_full_filename = os.path.join(output, new_filename)
        try:
            shutil.copy(filepath, new_full_filename)
        except Exception:
            logger.error(
                "Error found in the file: %s. Please check for the issues: ",
                filepath,
                exc_info=True,
            )
            return False
    else:
        new_full_filename = os.path.join(original_path, new_filename)
        os.rename(filepath, new_full_filename)
    return new_full_filename


def file_rename(filepath: str, output=None):
    """Function that renames a data file based on the
    standard:

    YYYY-MM-DD_HHmmh_<experiment_name>_<Subject_name>_<Researcher_name_or_initials>_data.csv

    Args:
        filepath (str): The file to rename.
        output (str): The output path where the renamed
                        file is going to be saved.

    Returns:
        boolean: True if the file was successfully renamed,
                 False if the file cannot be renamed.
    """
    _, filename = os.path.split(filepath)

    # First evaluates if the file already matches the pattern or not.
    if find_std_pattern(filename=filename):
        # Here, we keep the file as is or copy to a new location.
        copy_or_rename_file(filepath=filepath, new_filename=filename, output=output)
        return True

    # First, let's find the Epoch timestamp in the filepath.
    epoch_timestamp = find_epoch(filename)
    if not epoch_timestamp.strip():
        logger.info(
            "The file %s does not have any timestamp or there is an error. Check in the logs!",
            filename,
        )
        return False

    epoch_int = int(epoch_timestamp)
    # divided by 1k to get the milliseconds.
    epoch_transformed = datetime.fromtimestamp(epoch_int / 1000.0)

    # Gets the time with milliseconds for ExpStartTimestamp column
    epoch_time = str(epoch_transformed.time())[:-3]

    epoch_time = epoch_time.replace(DOT, COMMA)

    logger.debug("Current timestamp transformed [HH:MM:SS.sss] ==> %s", epoch_time)

    # Extracting the HHMM from the epoch time.
    hours_minutes = epoch_time[:-7].replace(COLON, EMPTY_SPACE)

    date_format_list = [str(epoch_transformed.date()), hours_minutes + DATE_ENDING_CHAR]
    try:
        exp_date_time_format = SEPARATOR.join(date_format_list)  # YYYY-MM-DD_HHmmh
        logger.debug("Datetime timestamp list ==> %s", date_format_list)
        logger.debug("Datetime transformed string ==> %s", exp_date_time_format)
    except Exception:
        logger.error(
            "Error found in the file: %s. Please check for the issues: ",
            filepath,
            exc_info=True,
        )

    format_name_parts = get_params_from_file(filepath)
    if len(format_name_parts) != 3:
        logger.warning("Not enough parameters to change the filename...")
        logger.warning("Exiting now!")
        return False

    # Inserts at the beginning the datetime format
    format_name_parts.insert(0, exp_date_time_format)

    # Appends at the end the experiment ending data.csv
    format_name_parts.append(EXP_NAME_END)
    try:
        logger.debug("Format parts: %s", format_name_parts)
        new_filename = SEPARATOR.join(format_name_parts)
    except Exception:
        logger.error(
            "Error found in the file: %s. Please check for the issues: ",
            filepath,
            exc_info=True,
        )
        return False

    new_fullpath = copy_or_rename_file(
        filepath=filepath, new_filename=new_filename, output=output
    )

    # Injects the experiment timestamp start in the corresponding column in the new file.
    new_df = pd.read_csv(new_fullpath)
    new_df[EXP_START_TS] = new_df[EXP_START_TS].fillna(epoch_time)
    new_df.to_csv(new_fullpath, index=False)

    return True
