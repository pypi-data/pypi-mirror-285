from pih import strdict, isolate, delay
from pih.tools import *
from pih.collections import *
from pih.consts.errors import NotFound
from pih.consts.events import *
from pih import A, PIH, OutputStub

from typing import Any

output_stub: OutputStub = OutputStub()


class Stub(PIH):

    def arg(self, index: int = 0) -> Any | None:
        return self.session.arg(index)

    @property
    def arg_list(self) -> list[str] | None:
        return self.session.arg_list

    def __init__(self):
        self.is_force: bool = False

    def write_line(self, value: str) -> None:
        self.output.write_line(value)


if not A.SE.is_mobile:
    self: Stub = Stub()
#b = output_stub.b
#i = output_stub.i


def execute(file_search_request: str, parameters: strdict | None = None) -> None:
    with A.ER.detect_interruption():
        A.R_F.execute(
            file_search_request,
            parameters={"self": self} | A.D.map(A.D.as_value, (parameters or {})),
            stdout_redirect=False,
            catch_exceptions=True,
        )


def execute_file(
    use_authentification: bool,
    title: str | None,
    file_search_request: str,
    show_loading_delay: float | None = None,
    loading_text: str | None = None,
    done_text: str | None = "Выполнено!",
    parameters: strdict | None = None,
) -> None:
    A.O.init()
    if ne(title):
        A.O.head(title)  # type: ignore
    if not use_authentification or A.SE.authenticate():
        if not use_authentification:
            A.SE.fill_access_groups()
        A.O.clear_screen()
        A.O.pih_title()
        if ne(title):
            A.O.head1(title)  # type: ignore
        if n(show_loading_delay):
            execute(file_search_request, parameters)
        else:
            with A.O.make_loading(
                show_loading_delay, loading_text or "Идёт выполнение файла"
            ):
                execute(file_search_request, parameters)
        if nn(done_text):
            A.O.good(done_text)
        A.SE.exit(0)
    A.SE.exit(0, "Выход")


def include(
    value: str, class_name: str | None = None, global_dict: dict[str, Any] | None = None
) -> Any | dict[str, Any] | None:
    dictionary: dict[str, Any] = A.R_F.execute(value, stdout_redirect=False)
    if n(class_name):
        return dictionary
    import_data: Any = dictionary[class_name]
    if n(global_dict):
        global_dict[class_name] = import_data
        return
    else:
        return import_data
