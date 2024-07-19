#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module provides a function to read the demographics data (Participant ID, age, height, weight) from the specified folder path and return a DataFrame containing the data.
This can then be used to merge the demographics data with any of the other permutations of the cardiovascular/hemodynamic data produced by these functions.
Notes
-----
- The function expects the finometer data to be stored in a single .txt file within the specified folder.
- The function reads the data from the .txt file, performs preprocessing steps (such as dropping unnecessary columns and converting timestamps), and calculates the average of each measure over the selected time period.


Example
-------
P1_demographics = read_raw_demographics('path/to/folder')
"""

from ..dependencies import pd, pl

def read_raw_demographics(folder_path: str) -> pd.DataFrame:
    """
    Reads in the demographics from the .txt file and returns a DataFrame row containing the data.

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

    if folder_path.is_dir():
        files = [file for file in folder_path.glob('*.txt')]
        if len(files) != 1:
            raise ValueError(f'Expected one .txt file, but found {len(files)} in the folder')
        file = files[0]
    elif folder_path.is_file():
        file = folder_path

    ID = file.stem.split('_')[0]

    # Read in the demographics data from the file
    df = pd.read_csv(
        file,
        sep=';',
        header=0,
        skiprows=2,
        nrows=1,
        engine='python'
        )

    # Select the relevant columns from the DataFrame
    demographics_df = df.loc[:, ['Identification', 'Age (yrs)', 'Height (cm)', 'Weight (kg)', 'Gender']]

    # Rename the columns
    demographics_df.columns = ['Participant ID', 'Age (years)', 'Height (cm)', 'Weight (kg)', 'Gender']


    return demographics_df