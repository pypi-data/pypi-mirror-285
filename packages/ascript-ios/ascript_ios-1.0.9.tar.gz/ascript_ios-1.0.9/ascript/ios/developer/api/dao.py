import json


def api_result_error(e: Exception):
    result = {
        "code": -1,
        "msg": str(e),
        "data": None
    }

    return result


def api_result(code: int = 1, msg: str = "success", data=None):
    result = {
        "code": code,
        "msg": msg,
        "data": data
    }

    return result


def api_result_json(code: int = 1, msg: str = "success", data=None):
    result = {
        "code": code,
        "msg": msg,
        "data": data
    }

    return json.dumps(result)
