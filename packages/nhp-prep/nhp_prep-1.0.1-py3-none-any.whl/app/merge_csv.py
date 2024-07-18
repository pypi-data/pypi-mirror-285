import pandas as pd
import glob
import os
import datetime
from datetime import datetime as dt

from app.main_logger import logger


def merge_csv_files(csv_files: list):
     # Initialize an empty list to store the DataFrames
    dfs = []

    # Initialize counter 
    _files_to_process = 0
    _error_files = 0

    for file_path in csv_files:
        _files_to_process += 1
        try:
            # get file name
            file_name = os.path.basename(file_path)
            # the file name should expectedly end in `csv`
            if file_name.endswith('.csv'):
                # Read the current CSV file into a DataFrame
                data = pd.read_csv(file_path)
                # Append the DataFrame to the list
                dfs.append(data)
        # handle exceptions
        except Exception as e:
            logger.error(
                f'An error has been detected while processing the file: {file_name}. \n Please check the following error: {e}')
            _error_files += 1
    
    return dfs, _files_to_process, _error_files