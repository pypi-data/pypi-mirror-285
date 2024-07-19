import mimetypes
import os
import shutil
import sys

from flask import request, send_file

from ascript.ios.developer.api import dao
from ascript.ios.developer.utils.env import get_asenv

current_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
module_space = os.path.join(get_asenv()["home"], 'modules')

if not os.path.exists(module_space):
    os.makedirs(module_space)


def api(app):
    @app.route("/api/file/get", methods=['GET'])
    def api_file_get():
        if "path" in request.args:
            file_path = os.path.join(module_space, request.args["path"])
            if not os.path.exists(file_path):
                return "File does not exist", 404

            mine_type, _ = mimetypes.guess_type(file_path)
            if not mine_type:
                mine_type = "application/octet-stream"

            return send_file(file_path, mimetype=mine_type)

        else:
            return "path缺少参数", 404

    @app.route("/api/file/save", methods=['POST'])
    def api_file_save():
        file_path = request.form.get("path")
        content = request.form.get("content")
        print(content)
        if file_path and content:
            if not os.path.exists(file_path):
                return "File does not exist", 404

            with open(file_path, "w",newline='\n',encoding="utf-8") as f:
                f.write(content)

            return dao.api_result()

        else:
            return "缺少参数[path,content]", 404

    @app.route("/api/file/create", methods=['POST'])
    def api_file_create():
        file_path = request.form.get("path")
        file_name = request.form.get("name")
        file_type = request.form.get("type")
        if file_path and file_name and file_type:

            new_file = os.path.join(file_path, file_name)
            print(new_file, file_type)

            if file_type == "file":
                with open(new_file, "w") as f:
                    pass
            else:
                os.makedirs(new_file)

            return dao.api_result()

        else:
            return "缺少参数 path,name,type", 404

    @app.route("/api/file/remove", methods=['POST'])
    def api_file_remove():
        file_path = request.form.get("path")
        if file_path:
            if os.path.exists(file_path):
                if os.path.isfile(file_path):
                    os.remove(file_path)
                else:
                    shutil.rmtree(file_path)
            return dao.api_result()

        else:
            return "缺少参数 path", 404

    @app.route("/api/file/finder", methods=['POST'])
    def api_file_finder():
        file_path = request.form.get("path")
        if file_path:
            if os.path.isfile(file_path):
                os.startfile(os.path.dirname(file_path))
            else:
                os.startfile(file_path)

            return dao.api_result()

        else:
            return "缺少参数 path", 404

    @app.route("/api/file/rename", methods=['POST'])
    def api_file_rename():
        src_file = request.form.get("path")
        file_rname = request.form.get("name")
        new_file = os.path.join(os.path.dirname(src_file),file_rname)
        if src_file and file_rname:
            os.rename(src_file, new_file)

            return dao.api_result()

        else:
            return "缺少参数 path", 404
