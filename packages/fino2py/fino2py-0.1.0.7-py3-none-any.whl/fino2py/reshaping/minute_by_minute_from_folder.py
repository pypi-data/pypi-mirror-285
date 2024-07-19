#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Reshape finometer data into a minute-by-minute format from files in a folder.

This module provides a function to read the raw finometer data from the specified folder path and reshape the data into a minute-by-minute format. 
It utilizes the `read_raw_finometer_data` function to import the data and calculate the average of each measure over the selected time interval (default is 1 minute). 
The `minute_by_minute` function is then applied to reshape the data into a single row, with each column representing the average of a particular measure over each minute of the data collection.

Notes
-----
- The `read_raw_finometer_data` function is used to import the raw finometer data and calculate the average over the selected time interval.
- The `minute_by_minute` function is applied to reshape the data into a single row for each minute.
- If `save_raw` is True, the imported raw data is saved as a CSV file in the same folder as the data files.
- If `save` is True, the minute-by-minute reshaped data is saved as a CSV file in the same folder as the data files.

Example
-------
frame, id = minute_by_minute_from_folder('/path/to/folder', int='1T', save_raw=True, save=True)
'''


from ..dependencies import pd, Tuple
from ..ingesting.read_raw_finometer_data import read_raw_finometer_data
from .minute_by_minute import minute_by_minute

def minute_by_minute_from_folder(path: str, save_raw: bool = False, save: bool = False) -> Tuple[pd.DataFrame, str]:
    '''

    This function reads the raw finometer data from the specified folder path and 'reshapes' the data into a minute-by-minute format. 
    It uses the `read_raw_finometer_data` function to import the data and calculate the average of each measure over the selected time interval (1 minute in this case). 
    Then, the `minute_by_minute` function is applied to reshape the data into a single row, with each column representing the average of a particular measure over each minute of the data collection.

    Parameters
    ----------
    path : str
        The path to the folder containing the finometer data files.
    save_raw : bool, optional
        Specifies whether to save the imported raw data as a CSV file. The default is False.
    save : bool, optional
        Specifies whether to save the minute-by-minute analysis result as a CSV file. The default is False.

    Returns
    -------
    Tuple[pd.DataFrame, str]
        A tuple containing the minute-by-minute analysis DataFrame and the Participant ID associated with the data.

    Notes
    -----
    - The `read_raw_finometer_data` function is used to import the raw finometer data and calculate the average over the selected time interval.
    - The `minute_by_minute` function is applied to reshape the data into a single row for each minute.
    - If `save_raw` is True, the imported raw data is saved as a CSV file in the same folder as the data files.
    - If `save` is True, the minute-by-minute analysis result is saved as a CSV file in the same folder as the data files.

    Example
    -------
    frame, id = minute_by_minute_from_folder('/path/to/folder', int='1T', save_raw=True, save=True)
    '''

    frame, id = read_raw_finometer_data(path, interval= '1T', save_csv=save_raw)

    minute_frame = minute_by_minute(frame, id)
    
    if save == True:
        minute_frame.to_csv(path / f'{id} minute_by_minute.csv', index = False)

    return minute_frame, id