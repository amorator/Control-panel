from threading import Thread
from time import sleep


class ThreadPool:
    def __init__(self, max=4):
        self.max = max
        self.procs = []

    def add(self, target, *args):
        Thread(target=self._add, args=(target, *args)).start()

    def _add(self, target, *args):
        while len(self.procs) > self.max:
            sleep(1)
            self.refresh()
        self.procs.append(Thread(target=target, args=args))
        self.procs[-1].start()

    def refresh(self):
        for proc in self.procs:
            if not proc.is_alive():
                proc.join()
                self.procs.remove(proc)
