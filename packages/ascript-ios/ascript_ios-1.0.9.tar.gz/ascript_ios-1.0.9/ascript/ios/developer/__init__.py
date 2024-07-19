import sys
import time
import webbrowser

from ascript.ios.developer import server

from ascript.ios.developer import ws

ws.run()

server.run()

while server.web_server_thread.isAlive() and not server.stop:
    time.sleep(0.5)


