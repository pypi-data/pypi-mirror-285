import asyncio
import threading

import websockets

connected = set()

loop = None

async def ws_on_message(ws, path):
    print("new client connected", ws)
    connected.add(ws)
    try:
        async for msg in ws:
            print(msg)
    except websockets.ConnectionClosed as e:
        print("有连接已断开")
        connected.remove(ws)


def start_websocket_server():
    global loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    server = loop.run_until_complete(websockets.serve(ws_on_message, "0.0.0.0", 9098))
    print("ws:server: ws://0.0.0.0:9098")

    try:
        loop.run_forever()
    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()


def run():
    server_thread = threading.Thread(target=start_websocket_server, daemon=True)
    server_thread.start()


def send_message(message):
    global loop
    for ws in list(connected):
        asyncio.run_coroutine_threadsafe(ws.send(message), loop)
