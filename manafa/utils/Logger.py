
import time
from enum import Enum

from termcolor import colored
import datetime

DUMP_TO_FILE = False


class LogSeverity(Enum):
    SUCCESS = "Success"
    WARNING = "Warning"
    INFO = "Info"
    ERROR = "Error"
    FATAL = "Fatal"


def getColor(sev):
    return {
        'Success': 'green',
        'Warning': 'yellow',
        'Info': 'blue',
        'Error': 'magenta',
        'Fatal': 'red'
    }.get(sev, 'green')


def log(message, log_sev=LogSeverity.INFO, log_time=None):
    the_time = time.time() if log_time is None else log_time
    color = getColor(log_sev.value)
    adapted_time = datetime.datetime.fromtimestamp(the_time)
    str_to_print = colored("[E-MANAFA %s] %s: %s" % (log_sev.value, adapted_time, message), color)
    print(str_to_print)
    if DUMP_TO_FILE:
        filename = "%d-%d-%d.log" % (adapted_time.year, adapted_time.month, adapted_time.day)
        f = open(filename, "a+")
        f.write(str_to_print+"\n")
        f.close()