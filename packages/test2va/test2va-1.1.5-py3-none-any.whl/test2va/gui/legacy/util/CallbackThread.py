import threading


class CallbackThread(threading.Thread):
    def __init__(self, target, args=(), kwargs=None, callback=None):
        super().__init__(target=target, args=args, kwargs=kwargs if kwargs is not None else {})
        self.callback = callback
        self._stop_event = threading.Event()

    def run(self):
        if self._target:
            self._target(self._stop_event, *self._args, **self._kwargs)
        if self.callback:
            self.callback()

    def stop(self):
        if self.is_alive():
            self._stop_event.set()
            self.join()
