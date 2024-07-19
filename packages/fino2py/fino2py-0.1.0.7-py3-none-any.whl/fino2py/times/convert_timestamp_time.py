from ..dependencies import dt

def convert_timestamp_time(timestamp_time: str) -> str:
    """
    Convert the timestamp string in the format '09:02:12' to '%H:%M:%S' datetime format.

    Parameters:
    ----------
    timestamp_time : str
        The timestamp time in the format '09:02:12'

    Returns:
    -------
    str
        The time in the '%H:%M:%S' format.
    """
    try:
        time = dt.datetime.strptime(timestamp_time, '%H:%M:%S')
    except Exception as e:
        raise ValueError(f"Failed to convert time {timestamp_time} to datetime object. Error: {e}")

    return time.strftime('%H:%M:%S')