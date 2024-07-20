"""Loading related classes

    This module consists of classes that help display progress/loading
    to make user wait patiently and indicate a process is happening.
"""
import time
import threading
from rich.progress import Progress, SpinnerColumn, TextColumn

class Spinner:
    """
    Displays a spinner in terminal to indicate user a process is happening
    """

    def __init__(self) -> None:
        self.loading_thread = None
        self.loading_stop_event = None

    def _show_loading_spinner(self, stop_event:threading.Event, msg:str):
        """
        This function displays the loading circle and message

        :stop_event: a threading event to stop the spinner
        :msg: message to be displayed while loading.
        """
        with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
        ) as progress:
            progress.add_task(description=f"{msg}...", total=None)
            while True:
                if stop_event.is_set():
                    break
                time.sleep(0.1)

    def start(self, msg:str) -> None:
        """
        This function starts the spinner and displays the loading/progress message.

        :msg: message to be displayed while loading.
        """
        self.loading_stop_event = threading.Event()
        self.loading_thread = threading.Thread(
                                        target=self._show_loading_spinner,
                                         args=(self.loading_stop_event, msg)
                                            )
        self.loading_thread.start()

    def stop(self):
        """
        This function stops the spinner and displays the loading/progress message.
        """
        self.loading_stop_event.set()
        self.loading_thread.join()
