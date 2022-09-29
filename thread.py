from listeners.tick import GameThread
import threading
from core import AutoUnload
import time
import websocket
from hooks.exceptions import except_hooks


# Thanks to Doldol from SourcePython forums for this snippet
class StoppableSPThread(GameThread, AutoUnload):
    def __init__(self, accuracy=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.accuracy = accuracy
        self._stop = threading.Event()

    def run(self):
        while not self.stopped:
            try:
                self.do()
            except Exception:
                except_hooks.print_exception()
            time.sleep(self.accuracy)

    def do(self):
        raise NotImplementedError(
            "Some exception to indicate that this should be overridden")

    def stop(self):
        self._stop.set()

    @property
    def stopped(self):
        return self._stop.is_set()

    _unload_instance = stop


class WebSocketThread(StoppableSPThread):
    def __init__(self, url, on_open, on_close, on_message, on_error, cond_run_ws, *args, **kwargs):
        self.url = url
        self.on_open = on_open
        self.on_close = on_close
        self.on_message = on_message
        self.on_error = on_error
        self.keep_running_ws = cond_run_ws
        self.WS_CONNECTED = False
        self.WS_CONNECTION = None
        super().__init__(*args, **kwargs)

    def pre_ws_close(self, ws, close_status_code, close_msg):
        self.WS_CONNECTED = False
        self.on_close(ws, close_status_code, close_msg)

    def pre_ws_error(self, ws, error):
        self.WS_CONNECTED = False
        self.on_error(ws, error)

    def get_ws_conn(self):
        return self.WS_CONNECTION

    def do(self):
        while True and self.keep_running_ws():
            try:
                self.WS_CONNECTION = websocket.WebSocketApp(
                    url=self.url,
                    on_close=self.pre_ws_close,
                    on_message=self.on_message,
                    on_error=self.pre_ws_error,
                    on_open=self.on_open
                )
                self.WS_CONNECTED = True
                self.WS_CONNECTION.run_forever(
                    skip_utf8_validation=True, ping_interval=10, ping_timeout=8)
            except Exception as e:
                WS_CONNECTED = False
                print("Websocket connection Error  : {0}".format(e))
                time.sleep(5)
