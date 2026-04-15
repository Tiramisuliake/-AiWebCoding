class ServiceError(Exception):
    def __init__(self, code: int, msg: str, status: int = 400, data=None):
        super().__init__(msg)
        self.code = code
        self.msg = msg
        self.status = status
        self.data = data


__all__ = ["ServiceError"]
