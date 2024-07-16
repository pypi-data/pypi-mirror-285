import io
import os
import shutil
import sys
import time

from flask import request, jsonify, Response

from ascript.ios import file_utils, system
from ascript.ios.developer.api import dao
from ascript.ios.developer.utils.env import get_asenv


current_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
# print(current_dir)
module_space = os.path.join(get_asenv()["home"], 'modules')

if not os.path.exists(module_space):
    os.makedirs(module_space)


def api(app):
    @app.route("/api/screen/capture", methods=['GET'])
    def api_screen_capture():
        if "device_id" in request.args:
            device_id = os.path.join(module_space, request.args["device_id"])
        image = system.client.screenshot()
        byte_arr = io.BytesIO()
        image.save(byte_arr, format='PNG')
        byte_arr = byte_arr.getvalue()

        return Response(byte_arr, mimetype='image/png')

