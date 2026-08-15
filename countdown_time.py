import calendar
import time
import os

def get_remaining_time(starttime : int, type : str):

    current_timestamp = calendar.timegm(time.gmtime())
    countdown_duration = 0

    match type:

        case "stop":
            countdown_duration = int(os.getenv('STOP_TIME')) * 60

        case "sleep":
            countdown_duration = int(os.getenv('SLEEP_TIME')) * 60

        case _:
            countdown_duration = 1800

    remaining_seconds = countdown_duration - (current_timestamp - starttime)

    return int((remaining_seconds-remaining_seconds%60)/60)