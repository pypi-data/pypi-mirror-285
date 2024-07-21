import itertools
import sys
import threading


class Spinner:
    spinner_cycle = itertools.cycle([
        "⠋",
        "⠙",
        "⠹",
        "⠸",
        "⠼",
        "⠴",
        "⠦",
        "⠧",
        "⠇",
        "⠏"
    ])

    def __init__(self, text, beep=False, disable=False, force=False, stream=sys.stdout):
        self.text = text
        self.disable = disable
        self.beep = beep
        self.force = force
        self.stream = stream
        self.stop_running = None
        self.spin_thread = None

    def start(self):
        if self.disable:
            return
        if self.stream.isatty() or self.force:
            self.stop_running = threading.Event()
            self.spin_thread = threading.Thread(target=self.init_spin)
            self.spin_thread.start()

    def stop(self):
        if self.spin_thread:
            self.stop_running.set()
            self.spin_thread.join()

    def init_spin(self):
        while not self.stop_running.is_set():
            spin = f"{next(self.spinner_cycle)} {self.text}"
            self.stream.write(spin)
            self.stream.flush()
            self.stop_running.wait(0.2)
            self.stream.write('\b' * len(spin))
            self.stream.flush()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.disable:
            return False
        self.stop()
        if self.beep:
            self.stream.write('\7')
            self.stream.flush()
        return False
