from messages import SayText2
from .thread import WebSocketThread
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
WS_THREAD = None
PLUGIN_RUNNING = True


def plugin_running():
    global PLUGIN_RUNNING
    return PLUGIN_RUNNING


def update_game_status(status: GameStatus):
    global GAME_STATUS
    GAME_STATUS = status


def on_ws_open(ws):
    refresh_server_status()


def on_ws_close(ws, close_status_code, close_msg):
    pass


def on_ws_message(ws, message):
    SayText2(message).send()


def on_ws_error(ws, error):
    pass


def send_ws_msg(action, data):
    conn = WS_THREAD.get_ws_conn()
    if conn is None:
        print("Trying to send a message but the websocket connection is not open")
        return
    conn.send(json.dumps({
        "action": action,
        "data": data
    }))


def refresh_server_status():
    send_ws_msg("server_2_backend_update_status", {
        "status": GAME_STATUS.name
    })


def bootstrap_websocket():
    global WS_THREAD
    WS_THREAD = WebSocketThread(url="ws://192.168.0.11:1337/ws/server", on_open=on_ws_open, on_close=on_ws_close,
                                on_message=on_ws_message, on_error=on_ws_error, cond_run_ws=plugin_running)
    WS_THREAD.start()


def stop_websocket():
    global WS_THREAD
    global PLUGIN_RUNNING
    PLUGIN_RUNNING = False

    conn = WS_THREAD.get_ws_conn()
    if conn:
        conn.close()

    WS_THREAD.stop()
    WS_THREAD = None


def load():
    bootstrap_websocket()


def unload():
    stop_websocket()
