#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""

This module provides a function to read the raw NovaPress data from the specified folder path or file and return a DataFrame containing the data.

This function imports the raw NovaPress data from the specified folder path or file and calculates the average of each measure over a selected time period. 
The default time period is 1 secong, but it can be changed by setting the `interval` parameter to a different value. 
This function is a convenient way to preprocess the data before further analysis. 
By default it combines data from the 'Basic Nova' and 'Advanced_Hemodynamics' CSV files by matching on the 'Time(sec)' column. 
This can be changed by setting the `required_files` parameter to a different list of strings specifying the names of the CSV files to be imported and processed.

Notes
-----
- The function expects the data to be stored in one or more .csv files in the specified folder.
- The function reads the data from the CSV files, performs preprocessing steps (such as dropping unnecessary columns and converting timestamps), and calculates the average of each measure over the selected time period.
- The date is extracted from the file name and used to convert the 'Time(sec)' column to a datetime object.
- If `interval` is provided, the data is resampled to the given interval using the mean value for each resampled interval, however the default interval is 1 
second because otherwise we end up with duplicate timestamps and a lot of NaN values.

Example
-------
df, id = read_raw_nova_data('/path/to/folder', interval='1T', save_csv=True)

"""

from ..dependencies import pd, pl, re, dt, Union, Tuple, Optional, List, reduce



def read_raw_nova_data(
    folder_path: Union[str, pl.Path],
    interval: Optional[str] = '1s',
    save_csv: bool = False,
    required_files: list = ['Basic Nova', 'Advanced_Hemodynamics'],
) -> Tuple[str, pd.DataFrame]:
    """
    Imports the raw NovaPress data, processes it, and calculates the average of each measure over the selected time period.

    This function imports the raw NovaPress data from the specified folder path or file and calculates the average of each measure over a selected time period. The default time period is 1 minute, but it can be changed by setting the `interval` parameter to a different value. This function is a convenient way to preprocess the data before further analysis. It combines data from the 'Basic Nova' and 'Advanced_Hemodynamics' CSV files by matching on the 'Time(sec)' column.

    Args:
        folder_path (Union[str, pathlib.Path]): The path to the folder containing the .csv files.
        file_prefix (str, optional): If provided, only files with names starting with this prefix will be considered. Defaults to None.
        interval (str, optional): The interval over which the average of each measure is calculated. Defaults to '1s'.
        save_csv (bool, optional): If True, the imported data (or the resampled data if `interval` is provided) is saved as a CSV file in the same folder as the data file. Defaults to False.
        required_files (list, optional): A list of strings specifying the names of the CSV files to be imported and processed. Defaults to ['Basic Nova', 'Advanced_Hemodynamics'].

    Raises:
        TypeError: If `folder_path` is not a pathlib.Path object or a string.
        ValueError: If `folder_path` does not exist or is not a directory, or if no matching CSV files are found.

    Returns:
        Tuple[str, pd.DataFrame]: A tuple containing the following:
            - A string representing the Participant ID of the participant whose data is being imported.
            - A pandas DataFrame with the raw NovaPress data resampled to the given interval (if provided).

    Notes:
        - The function expects the data to be stored in one or more .csv files in the specified folder.
        - If `file_prefix` is provided, only files with names starting with the specified prefix will be considered.
        - The function reads the data from the CSV files, performs preprocessing steps (such as dropping unnecessary columns and converting timestamps), and calculates the average of each measure over the selected time period.
        - If `interval` is provided, the data is resampled to the given interval using the mean value for each resampled interval.
        - If `save_csv` is True, the imported data (or the resampled data if `interval` is provided) is saved as a CSV file in the same folder as the data file.

    Example:
        df, id = read_raw_nova_data('/path/to/folder', interval='1T', save_csv=True)
    """
    
    try:
        folder_path = pl.Path(folder_path)
    except TypeError:
        raise TypeError('folder_path must be a pathlib.Path object or a string')

    if not folder_path.exists() or not folder_path.is_dir():
        raise ValueError('folder_path does not exist or is not a directory')

    files = []
    for required_file in required_files:
        matching_files = [file for file in folder_path.glob(f'*{required_file}*.csv')]
        files.extend(matching_files)

    if not files:
        raise ValueError('No matching CSV files found in the folder for the specified file prefixes')

    dfs = []

    for file in files:
        # Extract the date string from the file name
        match = re.search(r'(\d{2}-[A-Za-z]{3}-\d{2})', file.name)
        if match:
            date_str = match.group(1)
        else:
            raise ValueError(f"Date pattern not found in the file name: {file.name}")

        # Convert the date string to a datetime object
        file_date = dt.datetime.strptime(date_str, '%d-%b-%y')

        # Read the CSV file
        df = pd.read_csv(file, sep=';', skiprows=7)

        # Convert 'Time(sec)' column to datetime using the extracted date
        df['Time(sec)'] = file_date + pd.to_timedelta(df['Time(sec)'] * 1000, unit='ms')

        # resample the data to the specified interval
        if interval:
            df = df.resample(interval, on='Time(sec)').mean(numeric_only=True)
        
        dfs.append(df)

    # Merge all dataframes on the specified columns
    combined_df = reduce(lambda left, right: pd.merge(left, right, on=['Time(sec)', 'Region'], how='outer'), dfs)
    # drop any 'Unnamed: ' column
    combined_df = combined_df.loc[:, ~combined_df.columns.str.contains('^Unnamed')]

    ID = folder_path.name.split(' ')[1]

    if save_csv:
        combined_df.to_csv(folder_path / f'{ID} imported {interval} data.csv', index=True)

    return ID, combined_df