"""
This is the entrypoint for the CLI application.
"""

from time import time
from datetime import datetime
import sys
import os
import tempfile
import glob
import click

import pkg_resources

import pandas as pd

from app import __app_name__, __version__
from app.main_logger import logger
from app.column_mapper import map_columns
from app.subject_changer import change_sub, fill_ref_file_dates
from app.timestamp_estimator import change_timestamp
from app.rename_files import file_rename
from app.merge_csv import merge_csv_files
from app.fix_ref_file import fix_file_format
from app.cleaning import clean_data

from app.util.rough_estimate_std_files import dir_time_estimate


FILE_TYPE = ".csv"
FILE_COLUMNS_STD = "config/columns__std_format.csv"

INPUT_DIR_MSG = "Input directory: %s"
OUTPUT_DIR_MSG = "Output directory: %s"

EXECUTION_TIME_MSG = "Total execution time: %f seconds"


def print_version(ctx, _, value):
    """Printing version method

    Args:
        ctx (_type_): The context
        _ (_type_): Parameter
        value (_type_): The value
    """
    if not value or ctx.resilient_parsing:
        return
    click.echo(f"CLI: {__app_name__}")
    click.echo(f"Version: v{__version__}")
    ctx.exit()


def log_issues(issues_list: list):
    """Helper function to include in the logs
    the list of some of the issues found.

    Args:
        issues_list (list): List with empty or errors.
    """
    for err in issues_list:
        logger.error(err)


@click.group()
@click.option(
    "--version",
    "-v",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
    help="Shows current version.",
)
def main():
    """
    The main function of the CLI application.
    """
    logger.info("CLI: %s", __app_name__)
    logger.info("Version: v%s", __version__)


@click.command(name="reorder-columns", short_help="Reorders columns in files.")
@click.option(
    "--input",
    "-i",
    type=click.Path(exists=True, file_okay=True),
    required=True,
    help="The input input with the files to process OR a solo CSV file.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(exists=False),
    required=True,
    help="The output input for the reordered files.",
)
@click.option(
    "--ref-file",
    "-r",
    type=str,
    help="Reference file that contains the names of the columns.",
)
@click.pass_context
def reorder_columns(ctx, input, output, ref_file):
    """
    Processes the files from an input directory or file, and
    returns the same file(s) to a different output
    directory. If the reference file is not included
    the application will retrieve an internal standard file
    that will serve as a reference.

    OUTPUT:
    If the output path does not exist, it will be created.

    """
    logger.info(
        "-------------------------- REORDERING COLUMNS --------------------------"
    )
    logger.info(INPUT_DIR_MSG, input)
    logger.info(OUTPUT_DIR_MSG, output)
    logger.info("Columns reference file: %s", ref_file)

    reference_file = (
        ref_file
        if ref_file is not None
        else pkg_resources.resource_stream(__name__, FILE_COLUMNS_STD)
    )
    df_reference = pd.read_csv(reference_file)
    ref_columns = list(df_reference.columns)
    # Creates the output path in case that it does not exists.

    if not os.path.exists(output):
        os.makedirs(output)

    _files_to_process = 0
    _error_files = 0

    # if feed with a single csv file
    # TODO: DRY principle!!!
    if os.path.isfile(input) and input.endswith(FILE_TYPE):
        logger.info("File recognized. \n Proceeding to reorder columns of it...")
        out_filename = os.path.join(output, os.path.basename(input))
        try:
            df_reordered = map_columns(columns=ref_columns, filename=input)
            df_reordered.to_csv(out_filename, index=False)
            logger.info("File reordered successfully: %s", out_filename)
            _files_to_process += 1
        except Exception as e:
            logger.error(
                "An error has been detected while processing the file: {filename}."
            )
            logger.error("Please check the following error: %o", e)
            _error_files += 1
    # else, treat it as a folder
    else:
        for _, _, files in os.walk(input):
            for each in files:
                if each.endswith(FILE_TYPE):
                    _files_to_process += 1
                    filename = os.path.join(input, each)
                    out_filename = os.path.join(output, each)
                    try:
                        df_reordered = map_columns(
                            columns=ref_columns, filename=filename
                        )
                        df_reordered.to_csv(out_filename, index=False)
                        logger.info("File reordered successfully: %s", out_filename)
                    except Exception as e:
                        logger.error(
                            """An error has been detected while processing the file: %s. \n 
                               Please check the following error: %s""",
                            filename,
                            e,
                        )
                        _error_files += 1

    _reordered_files = _files_to_process - _error_files
    _percentage_success = (_reordered_files / _files_to_process) * 100
    logger.info(
        "Total files reordered:  %d/%d => %f %% success!",
        _reordered_files,
        _files_to_process,
        _percentage_success,
    )


@click.command(name="rename", short_help="Renames all the files based on standard.")
@click.option(
    "--input",
    "-i",
    type=click.Path(exists=True, file_okay=True),
    required=True,
    help="The input directory with the files to process OR a solo CSV file.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(exists=False),
    required=False,
    help="The output path for the reordered file(s) [OPTIONAL].",
)
@click.pass_context
def rename(ctx, input, output):
    """
    Processes the file(s) from an input, and
    returns the same file(s) to a different output
    input, but with the format:

    YYYY-MM-DD_HHmmh_<experiment_name>_<Subject_name>_<Researcher_name_or_initials>_data.csv

    OUTPUT:
    If the output path does not exist, it will be created.
    Also, if the Output path is not passed, nhp-prep will
    proceed to use the path of each file and rename the original
    file.
    """
    start_time = time()
    logger.info(
        "-------------------------- RENAMING FILE(S) --------------------------"
    )
    logger.info("Input: %s", input)
    logger.info("Output path: %s", output)

    # if feed with a single csv file
    # TODO: refine to follow DRY principle
    if os.path.isfile(input) and input.endswith(FILE_TYPE):
        logger.info("File recognized. \n Proceeding to rename it...")
        _result = file_rename(filepath=input, output=output)
        if _result is False:
            logger.error(
                "An error occurred during the process of renaming "
                "the file: %s. Please check the logs.",
                input,
            )
        logger.info(EXECUTION_TIME_MSG, time() - start_time)

    # else, treat it as a folder
    elif os.path.isdir(input):
        logger.info("Path recognized.")
        logger.info("Proceeding to rename all files within it...")
        num_files = 0
        num_errors = 0
        error_files = list()
        empty_files = list()

        files = [
            each for each in os.listdir(input) if each.endswith(FILE_TYPE)
        ]  # Filtering only .csv files

        for each in files:
            filepath = os.path.join(input, each)
            num_files += 1
            _result = file_rename(filepath=filepath, output=output)
            if _result is False:
                logger.error(
                    "An error occurred during the process of renaming the file: %s. "
                    "Please check the logs.",
                    each,
                )

                try:
                    file_df = pd.read_csv(filepath_or_buffer=filepath)
                    if file_df.empty:
                        logger.error(
                            "The file %s has been detected to be empty. It can be ignored!",
                            each,
                        )
                        empty_files.append(filepath)
                    else:
                        error_files.append(filepath)
                except Exception:
                    logger.error(
                        """The file %s cannot be processed.\n
                           Please check the logs: """,
                        each,
                        exc_info=True,
                    )
                    empty_files.append(filepath)
                num_errors += 1

        _renamed_files = num_files - num_errors
        _percentage_success = (_renamed_files / num_files) * 100
        logger.error("The list of files with errors is:")
        log_issues(error_files)

        logger.error("The list of empty files is:")
        log_issues(empty_files)

        logger.info("Total files with errors: %d", len(error_files))
        logger.info("Total empty files: %d", len(empty_files))

        logger.info(
            "Total files reordered successfully: %d/%d => %s %% success!",
            _renamed_files,
            num_files,
            str(_percentage_success),
        )
        logger.info(EXECUTION_TIME_MSG, time() - start_time)


@click.command(
    name="timestamp-estimate",
    short_help="Estimates trial true timestamp based on the time of the file.",
)
@click.option(
    "--input",
    "-i",
    type=str,
    help="Directory that contains all the CSV files or a single CSV file to process.",
)
@click.option(
    "--output", "-o", type=str, help="Output directory of the processed file(s)."
)
@click.pass_context
def timestamp_estimate(ctx, input, output):
    """This command estimates the timestamp of an specific trial
    inside of each file(s). In order for this command to work
    the file must have the following columns:

      - Time \n
      - ExpStartTimestamp
      - TrialStartTimestamp

    """
    logger.info(
        "-------------------------- ESTIMATING TIMESTAMP IN output(S) --------------------------"
    )
    logger.info(INPUT_DIR_MSG, input)
    logger.info(OUTPUT_DIR_MSG, output)
    # Creates the output path in case that it does not exists.
    if not os.path.exists(output):
        os.makedirs(output)

    _files_to_process = 0
    _error_files = 0

    # if feed with a single csv file
    # TODO: refine to follow DRY principle
    if os.path.isfile(input) and input.endswith(FILE_TYPE):
        logger.info("File recognized. \n Proceeding to estimate timestamp of it...")
        out_filename = os.path.join(output, os.path.basename(input))
        try:
            df_timestamp_changed = change_timestamp(filename=input)
            df_timestamp_changed.to_csv(out_filename, index=False)
            logger.info(f"Change timestamp successfully: {out_filename}")
            _files_to_process += 1
        except Exception as e:
            logger.error(
                f"An error has been detected while processing the file: {filename}. \n Please check the following error: {e}"
            )
            _error_files += 1

    # else, treat it as a folder
    else:
        # Here, we roughly estimate the StartTimestamp of each file by creating a temporary output folder
        _tmp_intermediate_dir = tempfile.TemporaryDirectory()
        _intermediate_input = _tmp_intermediate_dir.name
        # input -> _tmp_intermediate_dir -> output
        dir_time_estimate(input, _intermediate_input)
        files = [
            each for each in os.listdir(_intermediate_input) if each.endswith(FILE_TYPE)
        ]  # Filtering only .csv files
        _files_to_process = len(files)
        for each in files:
            filename = os.path.join(_intermediate_input, each)
            out_filename = os.path.join(output, each)
            try:
                df_timestamp_changed = change_timestamp(filename=filename)
                df_timestamp_changed.to_csv(out_filename, index=False)
                logger.info("Change timestamp successfully: %s", out_filename)
            except Exception as e:
                logger.error(
                    "An error has been detected while processing the file: %s. \n Please check the following error: %s",
                    filename,
                    e,
                )
                _error_files += 1

        # clean up temporary directory
        logger.debug(
            "Cleaning up temporary directory: %s...", _tmp_intermediate_dir.name
        )
        _tmp_intermediate_dir.cleanup()

    _reordered_files = _files_to_process - _error_files
    _percentage_success = (_reordered_files / _files_to_process) * 100
    logger.info(
        "Total files reordered successfully: %d/%d => %d %% success!",
        _reordered_files,
        _files_to_process,
        _percentage_success,
    )


# Command to fix the reference file
@click.command(name="fix-ref-file", short_help="Fixes the reference file.")
@click.option(
    "--ref-file",
    "-f",
    required=True,
    help="Reference file that contains the names of subjects and timestamp start and end.",
)
@click.option(
    "--output",
    "-o",
    help="Output directory for the fixed reference file. If not provided, the output reference file will be saved in the same directory as the input reference file with the suffix '_fixed'.",
)
def fix_ref_file(ref_file, output):
    """
    Fixes the reference file by adjusting the format of the date and time columns.
    This command will create a new errors file with the name: <ref_file>_errors.csv
    that will contain the rows with errors.

    REF-FILE: The file that contains the date, and the start
    and end timestamp of each subjects.

    OUTPUT: The output directory for the fixed reference file.
    If the output path does not exist, it will be created.
    """
    logger.info(
        "-------------------------- FIXING REFERENCE FILE --------------------------"
    )
    logger.info("Reference file: %s", ref_file)
    logger.info(OUTPUT_DIR_MSG, output)

    # Creates the output path in case that it does not exists.
    if not os.path.exists(output):
        os.makedirs(output)

    if output is None:
        output = ref_file.replace(".csv", "_fixed.csv")

    # Fix the reference file
    df_fixed, issues = fix_file_format(reference_file=ref_file)

    # Save the fixed reference file
    df_fixed.to_csv(output, index=False)
    logger.info("Fixed reference file saved in: %s", output)

    # Save the errors file
    errors_file = ref_file.replace(".csv", "_errors.csv")
    with open(errors_file, "w", encoding="utf-8") as f:
        f.write("\n".join(issues))
    logger.info("Errors file saved in: %s", errors_file)


@click.command(
    name="sub-rename", short_help="Updates the subject name based trial level."
)
@click.option(
    "--ref-file",
    "-f",
    required=True,
    help="Reference file that contains the names of subjects and timestamp start and end.",
)
@click.option("--input", "-i", required=True, help="Input directory.")
@click.option("--output", "-o", help="Output directory.")
def sub_rename(input, output, ref_file):
    """
    Processes the files from a directory, and
    returns the same files to a different output
    directory. If the reference file is not included
    the application will retrieve a standard file
    that will serve as a reference.

    DIRECTORY: The input directory with the files to process.

    OUTPUT: The output directory for the reordered files.
    If the output path does not exist, it will be created.

    REF-FILE: The file that contains the date, and the start
    and end timestamp of each subjects.
    """
    logger.info(
        "-------------------------- SUBJECT RENAMING --------------------------"
    )
    logger.info(INPUT_DIR_MSG, input)
    logger.info(OUTPUT_DIR_MSG, output)
    logger.info("Columns reference file: %s", ref_file)

    reference_file = (
        ref_file
        if ref_file is not None
        else "./app/config/baboons_sessions_compiled.csv"
    )

    # Creates the output path in case that it does not exists.
    if not os.path.exists(output):
        os.makedirs(output)

    _files_to_process = 0
    _error_files = 0

    # Here we fill the missing timestamps in the reference file:
    (_, new_reference_file) = fill_ref_file_dates(reference_file)
    logger.info("New reference file for the process: %s", new_reference_file)
    for _, _, files in os.walk(input):
        for each in files:
            if each.endswith(FILE_TYPE):
                _files_to_process += 1
                filename = os.path.join(input, each)
                out_filename = os.path.join(output, each)
                try:
                    df_changed = change_sub(
                        file_path=filename,
                        filename=each,
                        ref_filename=new_reference_file,
                    )
                    df_changed.to_csv(out_filename, index=False)
                    logger.info("Subject changed successfully: %s", out_filename)
                except Exception as e:
                    logger.error(
                        """An error has been detected while processing the file: %s. \n 
                           Please check the following error: %s""",
                        filename,
                        e,
                    )
                    _error_files += 1
    _changed_files = _files_to_process - _error_files
    _percentage_success = (_changed_files / _files_to_process) * 100
    logger.info(
        "Total files reordered successfully: %d/%d => %d %% success!",
        _changed_files,
        _files_to_process,
        _percentage_success,
    )


@click.command(
    name="preparation-steps",
    short_help="This command comprises Reorder Columns, Renaming and Trials Timestamps Estimation in one command.",
)
@click.option("--input", "-i", required=True, help="Input directory.")
@click.option("--output", "-o", help="Output directory.")
@click.pass_context
def preparation_steps(ctx, input, output):
    """Pre-processes the files in a single directory for one subject.

    This is a command that replaces Steps 1 to 3:\n

     - reorder-columns\n

     - rename\n

     - timestamp-estimate

    Arguments:

    input (str): The Input folder of the subject. \n

    output (str): The output folder of the subject after pre-processing all the files.\n
    \b
    [WARNING] The 'sub-rename' command (Subject Renaming) has not been included in this
    command, so you will need to run it separately.
    """
    logger.info(
        "-------------------------- PREPARATION STEPS --------------------------"
    )
    logger.info(INPUT_DIR_MSG, input)
    logger.info(OUTPUT_DIR_MSG, output)

    start_time = time()

    # Temporary directories for the pre-processing steps
    _tmp_dir_step1 = tempfile.TemporaryDirectory()
    _tmp_dir_step2 = tempfile.TemporaryDirectory()

    _interim_dir_step1_step2 = _tmp_dir_step1.name
    _interim_dir_step2_step3 = _tmp_dir_step2.name

    logger.info("[STEP 1] Proceeding with - Reorder File Columns...")
    # Step 1 - Reorder Columns
    ctx.invoke(reorder_columns, input=input, output=_interim_dir_step1_step2)

    logger.info("[STEP 2] Proceeding with - Files Renaming...")
    # Step 2 - Rename files
    ctx.invoke(rename, input=_interim_dir_step1_step2, output=_interim_dir_step2_step3)

    logger.info("[STEP 3] Proceeding with - Estimating Trial Start time...")
    # Step 3 - Estimating trials Start Time
    ctx.invoke(timestamp_estimate, input=_interim_dir_step2_step3, output=output)

    logger.warning(
        "Process finished. Please take a look at the results in the path: %s", output
    )

    logger.debug(
        "Cleaning up temporary directory for Steps 1 - 2: %s...", _tmp_dir_step1.name
    )
    _tmp_dir_step1.cleanup()
    logger.debug(
        "Cleaning up temporary directory for Steps 2 - 3: %s...", _tmp_dir_step2.name
    )
    _tmp_dir_step2.cleanup()
    logger.info(
        "[EXECUTION-TIME] Elapse time to execute all the preparation steps: "
        "%f seconds!",
        time() - start_time,
    )


@click.command(
    name="merge-csv", short_help="Merge multiple CSV files into a single file."
)
@click.option("--input", "-i", required=True, help="Input directory.")
@click.option("--output", "-o", help="Output directory.")
@click.pass_context
def merge_csv(ctx, input, output):
    """
    Processes the file(s) from an input, and
    returns the same file(s) to a different output
    input, but with the format:

    YYYY-MM-DD_HHmmh_<experiment_name>_<Subject_name>_<Researcher_name_or_initials>_data.csv

    OUTPUT:
    If the output path does not exist, it will be created.
    Also, if the Output path is not passed, nhp-prep will
    proceed to use the path of each file and rename the original
    file.
    """
    start_time = time()
    logger.info("-------------------------- MERGE CSV(S) --------------------------")
    logger.info("Input path: %s", input)
    logger.info("Output path: %s", output)

    # Check directories existence
    if not os.path.isdir(input):
        logger.error(
            "%s is not a path. Please make sure the input is a directory!", input
        )
        sys.exit(1)

    if not os.path.exists(input):
        logger.error(
            "Path %s does not exist. Please make sure the path is correct!", input
        )
        sys.exit(1)

    if not os.path.exists(output):
        os.makedirs(output)

    # Get all csv files recursively
    csv_files = glob.glob(os.path.join(input, "**/*.csv"), recursive=True)

    try:
        # Get all appended dataframes, and file amount to be logged
        dfs, _files_to_process, _error_files = merge_csv_files(csv_files)
        # Concatenate all DataFrames into a single DataFrame
        merged_data = pd.concat(dfs, ignore_index=True)
        # Path and filename for the merged CSV file
        now = datetime.now()
        formatted_time = now.strftime("%Y-%m-%d_%H%Mh")

        output_file = os.path.join(output, f"./{formatted_time}_merged.csv")
        # Save the merged_data DataFrame to a CSV file
        merged_data.to_csv(output_file, index=False)

        _reordered_files = _files_to_process - _error_files
        _percentage_success = (_reordered_files / _files_to_process) * 100

        # logs
        logger.info("Successfully merged csv files")
        logger.info(
            "Total files merged: %d/%d => %d %% success!",
            _reordered_files,
            _files_to_process,
            _percentage_success,
        )

        logger.info(EXECUTION_TIME_MSG, time() - start_time)

    except Exception as e:
        logger.error(
            """An error has been detected while finalizing merged csv.\n 
               Please check the following error: %s""",
            e,
        )
        sys.exit(1)


@click.command(
    name="data-cleaning", short_help="Cleans the merged data file with hardcoded rules."
)
@click.option("--in-file", "-i", required=True, help="Input file.")
@click.option("--out-dir", "-o", help="Output directory.")
@click.pass_context
def data_cleaning(ctx, in_file, out_dir):
    """
    Cleans the merged data file by removing rows with not allowed researchers, dates, and experiments.

    Args:
        ctx (_type_): Context
        in_file (_type_): Input file location to be cleaned. It should be merged data file.
        out_dir (_type_): The output directory for the cleaned file.
    """
    start_time = time()
    logger.info("-------------------------- DATA CLEANING --------------------------")
    logger.info("Input file: %s", in_file)
    logger.info("Output path: %s", out_dir)

    # Check directories existence
    if not os.path.exists(in_file):
        logger.error(
            "Path %s does not exist. Please make sure the path is correct!", in_file
        )
        sys.exit(1)

    # If output directory is not provided, use the input directory
    if not out_dir:
        out_dir = os.path.dirname(in_file)
        logger.info("Output directory not provided. Using input directory: %s", out_dir)

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    try:
        # Load the data
        df = pd.read_csv(in_file, header=0, dtype="unicode")
        # Count the rows where `Sub` is 'AMBIGUOUS'
        raw_ambiguous_count = df[df["Sub"] == "AMBIGUOUS"].shape[0]
        # Clean the data
        cleaned_data = clean_data(df)
        # Count the rows where `Sub` is 'AMBIGUOUS' after cleaning
        cleaned_ambiguous_count = cleaned_data[
            cleaned_data["Sub"] == "AMBIGUOUS"
        ].shape[0]
        # Log the raw and cleaned ambiguous count
        logger.warning(
            "The number of rows with 'AMBIGUOUS' subject before cleaning: %d",
            raw_ambiguous_count,
        )
        logger.warning(
            "The number of rows with 'AMBIGUOUS' subject after cleaning: %d",
            cleaned_ambiguous_count,
        )
        # Log the total number of rows
        logger.info("Total number of rows after cleaning: %d", df.shape[0])
        # Log the percentage of `AMBIGUOUS` rows
        logger.info(
            "Percentage of 'AMBIGUOUS' rows after cleaning: %f",
            (cleaned_ambiguous_count / cleaned_data.shape[0]) * 100,
        )
        # Save the cleaned_data DataFrame to a CSV file
        output_file = os.path.join(out_dir, in_file[:-4] + "_cleaned.csv")
        cleaned_data.to_csv(output_file, index=False)

        # logs
        logger.info("Successfully cleaned the data!")
        logger.info("Cleaned data saved in: %s", output_file)
        logger.info(EXECUTION_TIME_MSG, time() - start_time)
    except Exception as e:
        logger.error(
            """An error has been detected while cleaning the data.\n 
               Please check the following error: %s""",
            e,
        )
        sys.exit(1)


main.add_command(reorder_columns)
main.add_command(rename)
main.add_command(fix_ref_file)
main.add_command(timestamp_estimate)
main.add_command(sub_rename)
main.add_command(preparation_steps)
main.add_command(merge_csv)
main.add_command(data_cleaning)

if __name__ == "__main__":
    main()
