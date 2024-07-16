import threading
import queue


class EventBroker:
    def __init__(self, max_threads=5):
        self.queue = queue.Queue()
        self.max_threads = max_threads
        self.lock = threading.Lock()
        self.threads = []

    def _worker(self):
        while True:
            task = self.queue.get()
            if task is None:
                break
            task()
            self.queue.task_done()

    def add_task(self, task):
        with self.lock:
            self.queue.put(task)
            if len(self.threads) < self.max_threads:
                thread = threading.Thread(target=self._worker)
                thread.start()
                self.threads.append(thread)

    def wait_for_completion(self):
        self.queue.join()
        for _ in range(len(self.threads)):
            self.queue.put(None)
        for thread in self.threads:
            thread.join()


# broker = EventBroker(max_threads=3)
#
# for n in range(10):
#     broker.add_task(lambda x=n: example_task(x))
#
# broker.wait_for_completion()
