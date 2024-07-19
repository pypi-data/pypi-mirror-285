from ..dependencies import pl,pd

def import_protocol_times(times_file_path: pl.Path or str, add_seconds: bool = False, flatten_seconds: bool = False, save_csv: bool = False) -> pd.DataFrame:
    '''
    This function imports the protocol times from a .csv or excel file file and returns a cleaned pandas dataframe with the protocol times for each participant.

    Parameters
    ----------
    times_file_path : pathlib.Path or str
        The path to the .csv/.xlsx  file containing the protocol times.
    add_seconds : bool, optional
        If True, seconds will be added to the time values (if missing).
    flatten_seconds : bool, optional
        If True, seconds will be set to 00 for all time values.
    save_csv : bool, optional
        If True, the imported data will be saved as a .csv file in the same folder as the .csv file.

    Raises
    ------
    TypeError:
        If times_file_path is not a pathlib.Path object.
    ValueError:
        If times_file_path does not exist or is not a file.
        If times_file_path does not have a .csv extension.
        If add_seconds and flatten_seconds are both True.
        If the function is unable to add seconds to time values or set seconds to 00.

    Returns
    -------
    pandas.DataFrame
        A cleaned pandas dataframe with the protocol times for each participant.
    '''

    def add_seconds_to_time(time_str):
        '''This function adds seconds to the time string for in case the time string is missing seconds'''
        if len(time_str) == 5:
            time_str += ":00"
        return time_str

    def flatten_seconds(time_str):
        '''This function sets seconds to 00 for a given time string'''
        return time_str[:5] + ':00'
    
    supported_extensions = ['.csv', '.xlsx']

    if not isinstance(times_file_path, pl.Path):  # check if file_path is a pathlib.Path object
        raise TypeError('times_file_path must be a pathlib.Path object')
    elif not times_file_path.exists():  # and if it exists
        raise ValueError('times_file_path does not exist')
    elif not times_file_path.is_file():  # and is a file
        raise ValueError('times_file_path is not a file')
    elif times_file_path.suffix not in supported_extensions:  # and is a supported file extension
        raise ValueError('times_file_path is not a supported file (csv or xlsx)')
    else:
        if times_file_path.suffix == '.csv':
            df = pd.read_csv(times_file_path)
        elif times_file_path.suffix == '.xlsx':
            df = pd.read_excel(times_file_path)
        else:
            raise ValueError('Invalid file extension')
        
        if add_seconds and flatten_seconds:
            raise ValueError('Only one of add_seconds and flatten_seconds can be True')

        if add_seconds:
            try:
                df.iloc[:, 1:] = df.iloc[:, 1:].applymap(lambda x: add_seconds_to_time(x) if isinstance(x, str) else x)
                df.iloc[:, 1:] = df.iloc[:, 1:].applymap(lambda x: pd.to_datetime(x, format='%H:%M:%S', errors='coerce'))
            except:
                print('Could not add seconds to time, please check the time format')

        elif flatten_seconds:
            try:
                df.iloc[:, 1:] = df.iloc[:, 1:].applymap(lambda x: add_seconds_to_time(x) if isinstance(x, str) else x)
                df.iloc[:, 1:] = df.iloc[:, 1:].applymap(lambda x: flatten_seconds(x) if isinstance(x, str) else x)
                df.iloc[:, 1:] = df.iloc[:, 1:].applymap(lambda x: pd.to_datetime(x, format='%H:%M:%S', errors='coerce'))
            except:
                print('Could not set seconds to 00, please check the time format')
        
        if save_csv: #if you want to save the csv file (which may be useful if you want to use the data in other ways)
            try:
                df.to_csv(times_file_path.parent / f"cleaned times.csv", index=False)
                print(f"CSV saved for {times_file_path.stem}")
            except Exception as e:
                print(f"Could not save csv file, error: {e}")
            


        return df