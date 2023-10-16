import threading
import sys
import time

class Spinner:
    stop_spinner = False

    def __init__(self, prefix):
        self.prefix = prefix

    def _spinner_thread(self):
        spinner = ["|", "/", "-", "\\"]
        while not self.stop_spinner:
            for char in spinner:
                sys.stdout.write(f"\r{self.prefix}: {char}")
                sys.stdout.flush()
                time.sleep(0.1)

    def start(self):
        self.spinner_thread = threading.Thread(target=self._spinner_thread)
        self.spinner_thread.start()

    def stop(self, msg):
        self.stop_spinner = True
        self.spinner_thread.join()
        clear_line = "\r" + " " * (len(self.prefix) + len(msg)) + "\r"  # Clear the entire line
        print(clear_line + msg)