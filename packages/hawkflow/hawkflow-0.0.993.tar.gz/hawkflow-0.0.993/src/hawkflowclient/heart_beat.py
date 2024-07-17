import threading
import time
import traceback

from ._validation import _validate_api_key
from .hawkflow_api import HawkflowAPI


class Heart:
    def __init__(self, app_name, meta="heartbeat", interval=60*60, api_key=""):
        self.app_name = app_name
        self.interval = interval
        self.api_key = _validate_api_key(api_key)
        self.meta = meta
        self.keep_running = True
        self.hf_api = HawkflowAPI(api_key)
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def start_beat(self):
        self.hf_api.start(process=self.app_name)
        time.sleep(0.5)
        self.hf_api.end(process=self.app_name)

    def run(self):
        while self.keep_running:
            try:
                self.start_beat()
                time.sleep(self.interval)
            except Exception as e:
                self.hf_api.exception(self.app_name, "heartbeat", exception_text=traceback.format_exc())
                print(f"Error in Hawkflow HeartBeat: {traceback.format_exc()}")

    def stop(self):
        self.keep_running = False
        self.thread.join()

    @staticmethod
    def beat(app_name, interval, api_key):
        return Heart(app_name, interval, api_key)



