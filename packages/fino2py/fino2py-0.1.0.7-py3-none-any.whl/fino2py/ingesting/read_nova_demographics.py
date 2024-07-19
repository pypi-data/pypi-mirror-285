#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module provides a function to read the demographics data (Participant ID, age, height, weight) from the specified folder path and return a DataFrame containing the data.
This can then be used to merge the demographics data with any of the other permutations of the cardiovascular/hemodynamic data produced by these functions.
Notes
-----
- The function expects the finometer data to be stored in a single .csv file within the specified folder.
- The function reads the data from the .csv file, performs preprocessing steps (such as dropping unnecessary columns and converting timestamps), and calculates the average of each measure over the selected time period.


Example
-------
P1_demographics = read_raw_demographics('path/to/folder')
"""

from ..dependencies import pd, pl, re, dt, Union, Tuple, Optional, List

def read_nova_demographics(folder_path: str) -> pd.DataFrame:
    """
    Reads in the demographics from the nova press .csv file and returns a DataFrame row containing the data.

    Parameters:
    file_path (str): Path to the demographics file.

    Returns:
    demographics_df (pd.DataFrame): DataFrame containing the demographics data.
    """

    try:
        folder_path = pl.Path(folder_path)
    except TypeError:
        raise TypeError('folder_path must be a pathlib.Path object or a string')

    if not folder_path.exists():
        raise ValueError('folder_path does not exist')

    if folder_path.is_dir(): # If the folder path is a directory, ask the user to specify the file

        files = [file for file in folder_path.glob('*.csv')]
        # print the files in the directory and a number for each file
        print('The following files are in the directory:')
        for i, file in enumerate(files):
            print(f'{i+1}: {file.name}')
        # ask the user to specify the file
        file_number = input('Please enter the number of the file you wish to use: ')
        # check that the input is a number
        if not file_number.isdigit():
            raise ValueError('Input must be a number')
        # check that the input is a valid number
        if int(file_number) not in range(1, len(files)+1):
            raise ValueError(f'Input must be between 1 and {len(files)}')
        # select the file
        file = files[int(file_number)-1]
    elif folder_path.is_file():
        file = folder_path

    ID = file.stem.split(' ')[1]

    detail_row = [4,5]

    # Read in the demographics data from the file
    df = pd.read_csv(
        file,
        sep=';',
        header=0,
        skiprows= lambda x: x not in detail_row,
        engine='python'
        )


    return df