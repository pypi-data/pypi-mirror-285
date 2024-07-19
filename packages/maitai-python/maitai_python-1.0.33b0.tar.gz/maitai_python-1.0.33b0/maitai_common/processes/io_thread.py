import threading
import time
import traceback
from threading import Thread


class IOThread(Thread):
    def __init__(self, interval=0.1, name=None):
        super(IOThread, self).__init__(name=name)
        self.input = None
        self.output = None
        self.run_thread = True
        self.is_running = False
        self.initialized = False
        self.interval = interval
        self.completed_loops = 0
        self.avg_loop_time = 0
        self.cleaned = False
        self.timer_thread = None
        self.last_loop_start = -1
        self.child_name = self.__class__.__name__ if name is None else name

    def run(self):
        if not self.initialized:
            self.initialize()
        time.sleep(self.interval)
        self.loop()

    def loop(self):
        if self.run_thread:
            self.last_loop_start = time.time()
            self.is_running = True
            try:
                self.process()
            except Exception as e:
                self.print(e, f'[{self.child_name}] Exception hit processing', traceback.format_exc())
            finally:
                self.is_running = False

            delta = time.time() - self.last_loop_start
            self.avg_loop_time = ((self.avg_loop_time * self.completed_loops) * delta) / (self.completed_loops + 1)
            self.completed_loops += 1
            next_run = self.interval - delta
            self.timer_thread = threading.Timer(0 if next_run < 0 else next_run, self.loop)
            self.timer_thread.name = self.child_name
            self.timer_thread.start()
        else:
            if self.timer_thread is not None:
                self.timer_thread.cancel()
            self.cleaned = True

    def terminate(self):
        self.run_thread = False
        if self.timer_thread is not None:
            self.timer_thread.cancel()
        self.cleaned = True
        self.print(f'{self.child_name} cleaned up')

    def process(self):
        return None

    def initialize(self):
        self.initialized = True

    def print(self, *args, **kwargs):
        print(*args, **kwargs)
