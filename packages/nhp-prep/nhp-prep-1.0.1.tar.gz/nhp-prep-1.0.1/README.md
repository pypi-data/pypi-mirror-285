# nhp-prep

This is a CLI Tool that has been created to pre-process historical data that has been collected
in multiple instances. This includes data collected at Seneca Zoo and Mellon Institute.

## Requirements

This package **_requires Python 3._**

## Installing

To install this CLI tool you can run the below command

```bash
pip3 install nhp-prep
```

## Updating

If you already have this tool installed, you can update it to the latest stable release by using the following command:

```bash
pip3 install -U nhp-prep
```

Alternatively, you clone this repo and then run this command from **_within_** the repository folder

```bash
python3 setup.py install
```

Another way to install this solution is by running the following command from **_within_** the repository folder:

```bash
pip install -e .
```

Both the above commands would install the package globally and `nhp-prep` will be available on your system.

## How to use

There are multiple instances in which you can use this tool.

```bash
nhp-prep COMMAND [OPTIONS]
```

There are four use-cases (commands) in which you can use this tool:

1. Mapping columns from prior to current format (`reorder-columns`)

```bash
nhp-prep reorder-columns -i <directory_with_files_to_reorder_columns_OR_unique_CSV_file> -o <output_directory> -r <file_with_reference_columns>
```

2. Rename the files to follow current standard (`rename`)

```bash
nhp-prep rename -i <directory_files_to_rename> -o <output_directory>
```

The current format for the file is: `YYYY-MM-DD_HHmmh_<experiment_name>_<Subject_name>_<Researcher_name_or_initials>_data.csv`

3. Timestamp estimation trials from historical data files based on column <X> (`timestamp-estimate`)

```bash
nhp-prep timestamp-estimate -i <directory_with_files_OR_unique_CSV_file> -o <output_directory>
```

### **Since v0.3.0**

Since the previous 3 steps are common across the different datasets collected, the dev team decided to merge them into one single command (`preparation-steps`):

```bash
nhp-prep preparation-steps -i <input_directory> -o <output_directory>
```

**_The previous command will run sequentially the steps 1 to 3. The only command left outside of the bundle is the #4 since that is only applicable for the Baboons' data and requires the additional reference file._**

4. Renaming of Subject according to logs file (needs the file) (`sub-rename`)

```bash
nhp-prep sub-rename -r <file_with_columns_and_reference_subject_names> -i <directory_with_files_OR_unique_CSV_file> -o <output_directory>
```

5. Merge multiple CSV files into a single file. The input should be a directory and so is the output

```bash
nhp-prep merge-csv -i <directory_with_files_OR_unique_CSV_file> -o <output_directory>
```

6. You can perform a data cleaning process by using the merged-csv file from step #5 based on hardcoded rules, such as the name of the Experiment, the Date or the Researcher name as well.

```bash
nhp-prep data-cleaning -i <merged_csv_file> -o <output_directory>
```

## Using the help sub-command

You could also run `nhp-prep --help` to see the available commands and their corresponding usage.

If you want to know all the options available for an specific command, run the following:

```bash
nhp-prep COMMAND --help
```

Example:

```bash
nhp-prep sub-rename --help
```

## Feedback

Please feel free to leave feedback in issues/PRs.
