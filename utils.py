from subprocess import Popen
from threading import Thread
import time

class Process(Popen):
  def register_callback(self, callback, *args, **kwargs):
    Thread(target=self._poll_completion, args=(callback, args, kwargs)).start()

  def _poll_completion(self, callback, args, kwargs):
    while self.poll() is None:
      time.sleep(0.1)
    callback(*args, **kwargs)