#!/usr/bin/env python
# -*- coding: utf-8 -*-


from ..dependencies import pd, Union, Dict 
from .nova_minute_by_minute import nova_minute_by_minute

'''
This function allows us to concatenate the minute-by-minute data for each participant into a single DataFrame so that we can perform group-level analysis.

In future when we have a means of creating protocol 'chunk' averages, we will also be able to use this function to concatenate the chunk averages for each participant into a single DataFrame for group-level analysis. 
But for now this is just for minute-by-minute data.

Notes
-----
- The `data_dict` parameter should be a dictionary with participant IDs as keys and minute-by-minute dataframes as values.
- The `data_dict` should be created using the `read_raw_nova_data` function.
- The Participant ID column is added at the beginning of the DataFrame to allow for sample-level analysis, and to allow for easy merging of various datasets (i.e. demographics data and or survey data from qualtrics or pavlovia).

example
-------
# Import minute-by-minute data for each participant

data_dict: Dict[str, pd.DataFrame] = {}

for sub_folder in project_folder.iterdir():
    try:
        ID, df = read_raw_nova_data(sub_folder, interval='1s', save_csv=True)

        data_dict[ID] = df

    except Exception as e:
        print(f'Error processing folder {sub_folder.name}: {e}')
}

concatenated_df = nova_concat(data_dict)
'''

def nova_concat(data_dict: Dict) -> pd.DataFrame:
    '''
    Concatenate the minute-by-minute data for each participant into a single DataFrame.

    This function takes a dictionary of minute-by-minute dataframes (`data_dict`) and concatenates them into a single DataFrame. The dictionary should be created using the `read_raw_nova_data` function. The Participant ID column is added at the beginning of the DataFrame to allow for sample-level analysis.

    Parameters
    ----------
    data_dict : Dict
        A dictionary containing Participant ID as keys and minute-by-minute dataframes as values.

    Returns
    -------
    pd.DataFrame
        A concatenated DataFrame containing minute-by-minute data for all participants.

    Example
    -------
    # Import minute-by-minute data for each participant with a dictionary comprehension
    data_dict

    concatenated_df = nova_concat(data_dict)
    '''

    frames = [] 

    for df_id, df in data_dict.items():
        try:
            df = nova_minute_by_minute(df, df_id)
            frames.append(df)
        except Exception as e:
            print(f'Error processing folder {df_id}: {e}')

    # Find the widest dataframe
    widest = max(frames, key=lambda x: x.shape[1])

    # Add the missing columns to each dataframe
    frames = [df.reindex(widest.columns, axis=1) for df in frames]

    # Concatenate the dataframes on the Participant ID and Time(sec) columns
    df = pd.concat(frames)

    return df