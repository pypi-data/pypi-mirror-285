import pandas as pd

from app.main_logger import logger


def map_columns(columns: list, filename: str):
    """Function generated to reorder the columns
    of a CSV file.
    It will fill with empty spaces all of those 
    columns that do not exist in the file.
    Args:
        columns (list): The list of column names as reference.
        filename (str): The file to reorder

    Returns:
        dataframe: The dataframe version of the file according 
                    to the columns order.
    """
    ordered_df = pd.DataFrame()
    try:
        file_df = pd.read_csv(filename)
        ordered_df = file_df.reindex(columns=columns)
    except Exception as e:
        logger.error(
            f'An exception has been detected while processing the file: {filename}. Please check the trace: {e}')
    return ordered_df
