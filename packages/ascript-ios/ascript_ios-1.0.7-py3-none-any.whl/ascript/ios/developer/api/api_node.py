import json
import os
import sys
import time

from flask import request, jsonify, Response, make_response
from ascript.ios.wda import Element

from ascript.ios.developer.api import dao
from ascript.ios.developer.utils import env
from ascript.ios.developer.utils.env import get_asenv
from ascript.ios.node import Selector, AsElement

current_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
module_space = os.path.join(get_asenv()["home"], 'modules')

if not os.path.exists(module_space):
    os.makedirs(module_space)


def api(app):
    @app.route("/api/node/dump", methods=['GET'])
    def api_node_dump():
        if "device_id" in request.args:

            device_id = request.args["device_id"]
            client = env.get_client(device_id)

            if 'selector' in request.args:
                selector = request.args["selector"]
                return jsonify(dao.api_result(data=api_selector(client, selector)))

            xml_info = client.source()
            # print(xml_info)
            response = make_response(xml_info)
            response.headers['Content-Type'] = 'application/xml'
            return response

        return jsonify(dao.api_result(code=-1, msg="缺少参数device_id"))

    @app.route("/api/node/attr", methods=['GET'])
    def api_node_attr():
        if "node_id" in request.args and "device_id" in request.args:
            node_id = request.args["node_id"]
            device_id = request.args["device_id"]
            client = env.get_client(device_id)
            return jsonify(dao.api_result(data=element_to_dict(AsElement(client, node_id))))

        return jsonify(dao.api_result(code=-1, msg="缺少参数device_id或node_id"))


def api_selector(client, selector: str):
    print(selector)
    sel = json.loads(selector)

    print("?-s", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    res = Selector().find_with_dict(client, sel["sels"], sel["find"])
    print("?-e", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    return elements_to_dict(res)


def elements_to_dict(element):
    res = []
    nid = 0
    for element in element:
        res.append({
            "id": element.id,
            # "name": element.name,
            "tag": element.id,
            # "value": element.value,
            # "label": element.label,
            # "displayed": element.displayed,
            # "visible": element.visible,
            # "enabled": element.enabled,
            # "accessible": element.accessible,
            # "x": element.bounds.left,
            # "y": element.bounds.top,
            # "width": element.bounds.right - element.bounds.left,
            # "height": element.bounds.bottom - element.bounds.top,
            "nodeId": nid
        })
        nid = nid + 1

    return res


def element_to_dict(element: AsElement):
    bounds = element.bounds
    return {
        "id": element.id,
        "type": element.className,
        "tag": element.id,
        "value": element.value,
        "label": element.label,
        "displayed": element.displayed,
        "visible": element.visible,
        "enabled": element.enabled,
        "index": element.index,
        "accessible": element.accessible,
        "x": bounds.left,
        "y": bounds.top,
        "width": bounds.right-bounds.left,
        "height": bounds.bottom - bounds.top,
        "nodeId": 0
    }
