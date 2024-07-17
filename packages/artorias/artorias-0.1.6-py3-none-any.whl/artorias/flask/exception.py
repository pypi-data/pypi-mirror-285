from typing import NoReturn

from flask import jsonify
from werkzeug.exceptions import HTTPException


class APIException(Exception):
    code: str = ""
    msg: str = ""
    status_code: int = 400

    def __init__(
        self, code: str | None = None, msg: str | None = None, status_code: int | None = None, payload: dict | None = None
    ):
        if code is not None:
            self.code = code
        if msg is not None:
            self.msg = msg
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        data = dict(code=self.code, msg=self.msg)
        return data | {"payload": self.payload} if self.payload else data

    def to_response(self):
        return jsonify(self.to_dict()), self.status_code

    @classmethod
    def from_http_exception(cls, exception: HTTPException):
        return APIException(
            code=exception.name.replace(" ", "_").upper(),
            msg=exception.description or "",
            status_code=exception.code or 400,
        )

    @classmethod
    def from_exception(cls, exception: Exception):
        return APIException(code="SERVER_ERROR", msg=str(exception), status_code=500)


def abort(code: str, msg: str, status_code: int, payload: dict | None = None) -> NoReturn:
    raise APIException(code, msg, status_code, payload)
