import io
import json
import ssl
import sys
import threading
import time
from datetime import datetime

import websocket

from oxpecker import WS_URL, auth

# 有些环境中，远端poc脚本找不到依赖包，看似无效引用，务必保留
import requests # pylint: disable=unused-import

static_insecure_skip_tls_verify = False


def ws_conn(insecure_skip_tls_verify):
    """
    Establishes a WebSocket connection.

    Args:
        insecure_skip_tls_verify (bool): Flag to skip TLS verification.

    """
    global static_insecure_skip_tls_verify
    static_insecure_skip_tls_verify = insecure_skip_tls_verify
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(  # pyright: ignore [reportPrivateImportUsage]
        WS_URL,
        header=auth,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    start_heartbeat(ws)
    ws.run_forever(
        sslopt={"cert_reqs": ssl.CERT_NONE} if insecure_skip_tls_verify else {}
    )


DEBUG = False


def on_message(ws, message):
    print("### websocket on_message ###")
    sys.stdout.flush()
    thread = threading.Thread(target=handle_message, args=(ws, message))
    thread.start()


def handle_message(ws, message):
    print("Received " + message if DEBUG else "")
    biz_message = json.loads(message)
    event = biz_message.get("event")
    print("event: " + event)
    sys.stdout.flush()

    if event == "EVENT.RUN_PYTHON":
        script = biz_message.get("data")
        print("===exec script===\n\n" + script if DEBUG else "")
        if script:
            old_stdout = sys.stdout
            try:
                output = io.StringIO()
                sys.stdout = output
                exec(script)
                sys.stdout = old_stdout
                captured_output = output.getvalue()
                output.close()
                biz_message["data"] = captured_output
                print("===exec finished=== " + captured_output if DEBUG else "")
                sys.stdout.flush()
            except Exception as e:
                sys.stdout = old_stdout
                print(f"发生异常：{e}")
                biz_message["data"] = repr(e)
        else:
            biz_message["data"] = "script is empty"
        ws.send(json.dumps(biz_message))
        return
    if event == "EVENT.TASK_FINISH":
        print("TODO task finish")


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print(f"### websocket close ###, at {datetime.now()}")
    time.sleep(10)
    print("### websocket reconnect ###")
    ws_conn(static_insecure_skip_tls_verify)


def on_open(ws):
    print(f"### websocket open ###，at {datetime.now()}")


def start_heartbeat(ws):
    def run():
        count = 0
        while True:
            time.sleep(15)
            count += 1
            print(f"### heartbeat {count} ###")
            ws.send(json.dumps({"event": "EVENT.HEARTBEAT.PING"}))

    thread = threading.Thread(target=run)
    thread.start()
