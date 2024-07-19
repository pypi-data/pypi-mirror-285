#!/usr/bin/env python
# -*- coding: utf-8 -*-



from ..dependencies import pl, pd, Union, Tuple, Optional, dt

def read_raw_finometer_data(folder_path: Union[str, pl.Path], interval: Optional[str] = None, save_csv: bool = False) -> Tuple[pd.DataFrame, str]:
    """Imports the raw finometer data and calculates the average of each measure over the selected time period.

    This function imports the raw finometer data from the specified folder path or file and calculates the average of each measure over a selected time period. The default time period is 1 minute, but it can be changed by setting the `interval` parameter to a different value. This function is a convenient way to preprocess the data before further analysis.

    Args:
        folder_path (Union[str, pathlib.Path]): The path to the folder containing the .txt file.
        interval (str, optional): If provided, the data is resampled to the given interval. Defaults to None.
        save_csv (bool, optional): If True, the imported data (or the resampled data if `interval` is provided) is saved as a CSV file in the same folder as the data file. Defaults to False.

    Raises:
        TypeError: If `folder_path` is not a pathlib.Path object or a string.
        ValueError: If `folder_path` does not exist or is not a directory.
                    If there is not exactly one .txt file in the folder.

    Returns:
        Tuple[pd.DataFrame, str]: A tuple containing the following:
            - A DataFrame with the raw finometer data resampled to the given interval.
            - The Participant ID of the participant whose data is being imported.

    Notes:
        - The function expects the finometer data to be stored in a single .txt file within the specified folder.
        - The function reads the data from the .txt file, performs preprocessing steps (such as dropping unnecessary columns and converting timestamps), and calculates the average of each measure over the selected time period.
        - If `interval` is provided, the data is resampled to the given interval using the mean value for each resampled interval.
        - If `save_csv` is True, the imported data (or the resampled data if `interval` is provided) is saved as a CSV file in the same folder as the data file.

    Example:
        df, id = read_raw_finometer_data('/path/to/folder', interval='1T', save_csv=True)
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



    df = pd.read_csv(
        file,
        sep=';',
        header=0,
        skiprows=8,
        skipfooter=1,
        engine='python',
    )

    df = df.drop(df.columns[13], axis=1)

    df['Time (s)'] = pd.to_datetime(df['Time (s)'], format='%H:%M:%S.%f').dt.floor('ms')



    if interval:

        csv_path = folder_path / file.with_stem(f'imported {interval} data for {ID}').with_suffix('.csv')
        try:
            df_resampled = df.set_index(pd.to_datetime(df['Time (s)'], format='%H:%M:%S.%f')).resample(f'{interval}').mean(numeric_only=True)
            df_resampled.index = df_resampled.index.strftime('%H:%M:%S.%f').str[:-3]
        except ValueError:
            raise ValueError(f'{interval} is not a valid time period, valid time periods are: 1s, 1T, 1H, 1D, 1W, 1M, 1Q, 1A')
    else:
        csv_path = folder_path / file.with_stem(f'imported data for {ID}').with_suffix('.csv')
        df = df.set_index(pd.to_datetime(df['Time (s)'], format='%H:%M:%S.%f').dt.strftime('%H:%M:%S.%f').str[:-3])
        df = df.drop('Time (s)', axis=1)


    if save_csv:
        df.to_csv(csv_path, index=True)

    return (df_resampled, ID) if interval else (df, ID)