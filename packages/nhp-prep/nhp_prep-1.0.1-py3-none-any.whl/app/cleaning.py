""" This is a module that contains the functions to clean the data based on the
parameters that are passed to the function. The cleaning process is done by
removing the rows that contain a 'Researcher' name that is in the list of not 
allowed researchers. The rows that contain certain `Date` values that are in 
the list of not allowed dates are also removed. In addition, the rows that
contain certain `Experiment` values that are in the list of not allowed are
also removed. 
"""

from app.main_logger import logger
import pandas as pd

NOT_ALLOWED_RESEARCHERS = ["HA", "TESTER", "Tester", "tester"]
NOT_ALLOWED_DATES = [
    "2021-11-21",
    "2021-12-08",
    "2022-01-19",
    "2022-03-01",
    "2022-07-13",
    "2022-10-01",
    "2022-10-09",
    "2023-01-18",
    "2023-01-19",
    "2023-01-26",
    "2023-01-27",
    "2023-02-12",
    "2023-02-16",
    "2023-02-22",
    "2023-02-28",
    "2023-03-03",
    "2023-03-07",
    "2023-03-15",
    "2023-03-19",
    "2023-03-30",
    "2023-04-26",
    "2023-04-27",
    "2023-05-24",
]
NOT_ALLOWED_EXP = ["butterfly-exp", "endless", "Children_Scratch"]


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """This function takes a DataFrame and removes the rows that contain a
    'Researcher' name that is in the list of not allowed researchers. The rows
    that contain certain `Date` values that are in the list of not allowed dates
    are also removed. In addition, the rows that contain certain `Experiment`
    values that are in the list of not allowed are also removed.

    Args:
        df (pd.DataFrame): The DataFrame to be cleaned.

    Returns:
        pd.DataFrame: The cleaned DataFrame.
    """
    logger.info("Cleaning the data")
    df = df[~df["Researcher"].isin(NOT_ALLOWED_RESEARCHERS)]
    df = df[~df["Date"].str.contains("|".join(NOT_ALLOWED_DATES))]
    df = df[~df["Exp"].isin(NOT_ALLOWED_EXP)]
    return df
