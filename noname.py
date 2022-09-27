from messages import SayText2
from listeners.tick import GameThread
import enum
import websocket
import time
import json


class GameStatus(enum.Enum):
    Idle = 0
    WaitingForPlayers = 1
    Starting = 2
    KnifeRound = 3
    Live = 4
    Ending = 5


GAME_STATUS = GameStatus.Idle
WS_CONNECTED = False
WS_CONNECTION = None


def update_game_status(status: GameStatus):
    global GAME_STATUS
    GAME_STATUS = status


class WebSocketRunner():
    def start_ws(self):
        global WS_CONNECTION
        while True:
            try:
                WS_CONNECTION = websocket.WebSocketApp(
                    url="ws://192.168.0.11:1337/ws/server",
                    on_close=self.on_ws_close,
                    on_message=self.on_ws_message,
                    on_error=self.on_ws_error,
                    on_open=self.on_ws_open
                )
                WS_CONNECTED = True
                WS_CONNECTION.on_open = self.on_ws_open
                WS_CONNECTION.run_forever(
                    skip_utf8_validation=True, ping_interval=10, ping_timeout=8)
            except Exception as e:
                WS_CONNECTED = False
                print("Websocket connection Error  : {0}".format(e))
                time.sleep(5)

    def on_ws_open(self, ws):
        refresh_server_status()

    def on_ws_close(self, ws, close_status_code, close_msg):
        global WS_CONNECTED
        WS_CONNECTED = False

    def on_ws_message(self, ws, message):
        SayText2(message).send()

    def on_ws_error(self, ws, error):
        global WS_CONNECTED
        WS_CONNECTED = False
        # ws.send("Hello, server")


def send_ws_msg(action, data):
    global WS_CONNECTION
    if WS_CONNECTION is None:
        return
    WS_CONNECTION.send(json.dumps({
        "action": action,
        "data": data
    }))


def refresh_server_status():
    global GAME_STATUS
    send_ws_msg("server_2_backend_update_status", {
        "status": GAME_STATUS.name
    })


def bootstrap_websocket():
    ws_runner = WebSocketRunner()
    thread = GameThread(target=ws_runner.start_ws)
    thread.daemon = True
    thread.start()


def load():
    bootstrap_websocket()


def unload():
    pass
