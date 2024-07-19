#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This module provides a function to create a chunk of data from a DataFrame between specified start and end times and return a new DataFrame containing the mean values for each cardiovascular measure during that chunk. 

Notes
-----
 - The DataFrame must have been created by the `read_raw_finometer_data` function. 
 - The time values must be in the format 'HH:MM:SS'. There are functions to help normalise the time values in the fino2py.times module.

Example
-------
baseline_1 = create_chunk(df, 'Participant 1', 'Baseline', '00:00:00', '00:05:00')
'''

from ..dependencies import pd, Union
from ..times.convert_timestamp_time import convert_timestamp_time


def create_chunk(df: pd.DataFrame, ID: str, tag: str, start: Union[str, None], end: Union[str, None]) -> pd.DataFrame:
    """
    Create a chunk of data from a dataframe between specified start and end times and return a new dataframe
    containing the mean values for each cardiovascular measure during that chunk.
    
    Parameters:
    -----------
    df : pandas DataFrame
        The dataframe containing the data to extract a chunk from.
    ID : str
        The participant ID to include in the output dataframe.
    tag : str
        The tag to include in the column names of the output dataframe.
    start : str or None
        The start time of the chunk in the format 'HH:MM:SS' or 'HH:MM:SS.mmm'. If None, the chunk starts at the 
        beginning of the dataframe.
    end : str or None
        The end time of the chunk in the format 'HH:MM:SS' or 'HH:MM:SS.mmm'. If None, the chunk ends at the 
        end of the dataframe.
    
    Returns:
    --------
    pandas DataFrame
        A new dataframe containing the mean values for each column in the specified chunk of the input dataframe.
        The output dataframe has a row for the specified participant ID and columns with names that include the
        specified tag.
    """
    # Convert start and end times to datetime objects if they are specified
    if start:
        try:
            start = convert_timestamp_time(start)
        except:
            raise ValueError(f"Could not convert {start} to datetime object, it must be a string in the format 'HH:MM:SS' or 'HH:MM:SS.mmm'")
    if end:
        try:
            end = convert_timestamp_time(end)
        except:
            raise ValueError(f"Could not convert {end} to datetime object, it must be a string in the format 'HH:MM:SS' or 'HH:MM:SS.mmm'")

    # Extract the chunk of data and compute the mean values for each column
    if start and end:
        chunk = df.loc[start:end].mean().to_frame().T
    elif start:
        chunk = df.loc[start:].mean().to_frame().T
    elif end:
        chunk = df.loc[:end].mean().to_frame().T
    
    # Rename the columns with the specified tag and insert the participant ID as the first column
    chunk.columns = [f"{tag} {i}" for i in chunk.columns]
    chunk.insert(0, 'Participant ID', ID)

    return chunk

