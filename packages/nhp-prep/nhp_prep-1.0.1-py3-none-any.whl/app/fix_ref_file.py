"""This is a module that fixes the format of the reference file."""

import pandas as pd


def fix_file_format(reference_file):
    """Function that fixes the format of the reference file.

    Args:
        reference_file (str): Path to the reference file.

    Returns:
        dataframe: The fixed reference file.
        list: A list of the problematic rows.
    """

    # Read the CSV file into a DataFrame
    df = pd.read_csv(reference_file)

    # Format the 'Start' and 'End' columns to HH:MM:SS format
    df["Start"] = pd.to_datetime(df["Start"], errors="coerce").dt.strftime("%H:%M:%S")
    df["End"] = pd.to_datetime(df["End"], errors="coerce").dt.strftime("%H:%M:%S")

    # Find rows with problematic 'Start' and 'End' format
    error_rows = df[(df["Start"].str.len() != 8) | (df["End"].str.len() != 8)]

    # Format the 'Date' column to MM/DD/YYYY format
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.strftime("%m/%d/%Y")

    # Check for rows with problematic 'Date' format
    problematic_rows = df[df["Date"].str.len() != 10]

    # Fix problematic rows that have a 'Date' format of MM/DD/YY to MM/DD/YYYY
    df.loc[problematic_rows.index, "Date"] = pd.to_datetime(
        problematic_rows["Date"], errors="coerce"
    ).dt.strftime("%m/%d/%Y")

    # Check remaining rows for problematic 'Date' format
    problematic_rows = df[df["Date"].str.len() != 10]

    # Combine error_rows and problematic_rows into a single DataFrame
    issues = pd.concat([error_rows, problematic_rows])

    # Convert the issues DataFrame to a list of strings
    issues = [f"{index} - {row}" for index, row in issues.iterrows()]

    # Return the formatted DataFrame and the issues list
    return df, issues

