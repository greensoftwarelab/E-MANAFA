from abc import ABC, abstractmethod
import os
from manafa.utils.Utils import execute_shell_command, get_results_dir

RESULTS_DIR = get_results_dir()


class Service(ABC):
    """Reference class for managing the lifecycle of a task need during the profiling session.

	This class is responsible by starting and stopping the perfetto service at the start and stop of the profiiling session.

    Attributes:
        results_dir (str): folder where the logs will be stored after each profiling session.
    """

    def __init__(self, results_dir=""):
        self.results_dir = os.path.join(RESULTS_DIR, results_dir)

    @abstractmethod
    def config(self, **kwargs):
        print(kwargs)

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self, run_id):
        pass

    def clean(self):
        """wipes results from previous runs."""
        execute_shell_command("find %s -type f | xargs rm " % self.results_dir)

    def save_results(self, output_dir=""):
        pass
