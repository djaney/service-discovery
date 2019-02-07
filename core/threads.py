from threading import Thread, Event


class MortalThread(Thread):
    def __init__(self, sleep_interval=1, **kwargs):
        super().__init__(**kwargs)
        self._kill = Event()
        self._interval = sleep_interval

    def run(self):
        while True:
            if self._target:
                self._target(*self._args, **self._kwargs)

            # If no kill signal is set, sleep for the interval,
            # If kill signal comes in while sleeping, immediately
            #  wake up and handle
            is_killed = self._kill.wait(self._interval)
            if is_killed:
                break

    def kill(self):
        self._kill.set()
