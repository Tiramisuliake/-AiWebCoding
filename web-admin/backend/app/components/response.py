def ok(data=None, msg="ok", status=200):
    return {"code": 0, "data": data, "msg": msg}, status


def fail(code, msg, status=400, data=None):
    return {"code": code, "data": data, "msg": msg}, status