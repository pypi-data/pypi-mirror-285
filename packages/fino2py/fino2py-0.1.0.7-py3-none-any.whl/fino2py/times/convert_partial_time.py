
from ..dependencies import pd, dt



def convert_partial_time(partial_time: str) -> dt.datetime.time:
    """
    Convert the partial time in the format '09:02' to a datetime.time object with 0 seconds.

    Parameters:
    ----------
    partial_time : str
        The partial time in the format '09:02'

    Returns:
    -------
    datetime.time
        The time as a `datetime.time` object with 0 seconds.
    """
    try:
        time = dt.datetime.strptime(partial_time, '%H:%M').time()
        time_str = time.strftime('%H:%M:%S')
        time_obj = dt.datetime.strptime(time_str, '%H:%M:%S').time()
    except Exception as e:
        raise ValueError(f"Failed to convert time {partial_time} to datetime object. Error: {e}")

    return time_obj