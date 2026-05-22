import time

class Chrono:
    def __init__(self):
        self.reset()

    def __str__(self) -> str:
        return f"{self.elapsed():.4f}"

    def reset(self):
        self._start = None
        self._elapsed = None

    def start(self):
        self._start = time.perf_counter()

    def pause(self):
        if self._start is None:
            raise ValueError("Le chrono n'a pas été démarré.")
        if self._elapsed is None:
            self._elapsed = 0.
        self._elapsed += time.perf_counter() - self._start
        self._start = None

    def elapsed(self):
        if self._start is None and self._elapsed is None:
            raise ValueError("Le chrono n'a pas été démarré ou arrêté.")
        if self._elapsed is None:
            # Live value
            return time.perf_counter() - self._start
        # Final value
        return self._elapsed
