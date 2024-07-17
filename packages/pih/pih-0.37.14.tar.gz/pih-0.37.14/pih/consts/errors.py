from dataclasses import dataclass

from typing import Any

import grpc

RPCError = grpc.RpcError

class NotImplemented(BaseException):
    pass

class OperationExit(BaseException):
    pass


class OperationCanceled(BaseException):
    pass

@dataclass
class Redirection(BaseException):
    arg: Any | None = None



class ZeroReached(BaseException):
    pass

class BarcodeNotFound(BaseException):

    def get_details(self) -> str:
        return "Штрих-код не распознан, попробуйте еще раз"


class NotFound(BaseException):

    def get_details(self) -> str:
        return self.args[0]

    def get_value(self) -> str:
        return self.args[1]


class IncorrectInputFile(BaseException):
    pass


class NotAccesable(BaseException):
    pass

@dataclass
class Error(BaseException):
    details: str | None = None
    code: tuple | None = None