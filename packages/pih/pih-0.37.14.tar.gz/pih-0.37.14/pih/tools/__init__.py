import re
import os
import sys
import json
import shlex
import pycron
import socket
import string
import random
import ntpath
import pathlib
import calendar
import platform
import dataclasses
from enum import Enum
from time import sleep
from os import walk, scandir
from operator import itemgetter
from contextlib import contextmanager
from inspect import isfunction, isclass
from typing import Any, Callable, Tuple, List
from datetime import date, datetime, timedelta

from pih.consts.password import RULES
from pih.consts.style import *
from pih.consts.date_time import DATE_TIME
from pih.consts.names import FieldCollectionAliases

from pih.collections import (
    R,
    T,
    User,
    Result,
    FullName,
    FieldItem,
    FieldItemList,
    PolibasePerson,
)


def if_else(
    check_value: bool | None,
    true_value: Callable[[], Any] | Any,
    false_value: Callable[[], Any] | Any = None,
    none_value: Callable[[], Any] | Any = None,
) -> Any:
    if n(check_value) and nn(none_value):
        return none_value() if callable(none_value) else none_value
    return (
        (true_value() if callable(true_value) else true_value)
        if check_value
        else (
            false_value()
            if not n(false_value) and callable(false_value)
            else false_value
        )
    )


def v(value: Any) -> Any:
    if n(value):
        if isinstance(value, tuple):
            return ()
        if isinstance(value, str):
            return ""
        if isinstance(value, list):
            return []
    return value


def one(
    value: Result[T] | Result[list[T]] | T | list[T], default_value: Any = None
) -> T | None:
    return (
        ResultTool.get_first_item(value, default_value)
        if isinstance(value, Result)
        else DataTool.get_first_item(value, default_value)
    )


def nl(
    value: str = "", count: int = 1, reversed: bool | None = False, normal: bool = True
) -> str:
    nl_text: str = ["<br>", "\n"][int(normal)] * count
    return DataTool.triple_bool(
        reversed, j((value, nl_text)), j((nl_text, value)), j((nl_text, value, nl_text))
    )


def j(value: tuple[Any, ...] | list[Any], splitter: str = "") -> str:
    return splitter.join(DataTool.map(str, DataTool.filter(nn, value)))


def nnl(value: Any) -> list:
    return value


def nna(value: Any) -> Any:
    return value


def nnd(value: Any) -> dict:
    return value


def nnt(value: T | None) -> T:
    return value


def nns(value: Any, default_value: str | None = None) -> str:
    if value == "":
        return value
    return value or default_value


def nnb(value: Any) -> bytes:
    return value


def nni(value: Any, default_value: int | None = None) -> int:
    if n(value) and nn(default_value):
        return nni(default_value)
    return value


def nndt(value: Any) -> datetime:
    return value


def nnf(value: Any) -> float:
    return value


def jnl(value: tuple[Any, ...] | list[Any]) -> str:
    return j(value, nl())


def jp(value: tuple[Any, ...] | list[Any]) -> str:
    return j(value, ".")


def js(value: tuple[Any, ...] | list[Any], aditional_splitter: str = "") -> str:
    return j(value, j((aditional_splitter or "", " ")))


class ParameterList:
    def __init__(self, value: Any):
        self.values = value if isinstance(value, (list, tuple)) else [value]
        self.index = 0

    def next(self, object: Any = None, default_value: Any = None) -> Any:
        if self.index >= len(self.values):
            return default_value
        value: Any = self.values[self.index]
        if value == "":
            value = None
        self.index = self.index + 1
        if ne(value) and ne(object):
            if isclass(object) and issubclass(object, Enum):
                value = EnumTool.get(object, value)
            else:
                value = DataTool.fill_data_from_source(object, value)
        return value

    def next_as_list(self, class_type) -> Any:
        return DataTool.fill_data_from_list_source(class_type, self.next())

    def get(
        self,
        index: int = 0,
        object: Any = None,
        default_value: Any = None,
    ) -> Any:
        temp_index: int = self.index
        self.index = index
        result: Any = self.next(object, default_value)
        self.index = temp_index
        return result

    def set(self, index: int, value: Any) -> None:
        self.values[index] = value


class EnumTool:
    @staticmethod
    def get(
        enum_class: Enum | Any,
        key: str | None = None,
        default_value: Any = None,
        return_value: bool = True,
    ) -> Any:
        if n(enum_class):
            return None
        if return_value and e(key):
            if isinstance(enum_class, Enum):
                return enum_class.value
            return enum_class
        if key not in enum_class._member_map_:
            return default_value
        return enum_class._member_map_[key]

    @staticmethod
    def get_by_value(enum_class: Enum, value: Any, default_value: Any = None) -> Any:
        if isinstance(value, Enum):
            return value
        map: Any = enum_class._value2member_map_
        return map[value] if value in map else default_value

    @staticmethod
    def get_by_value_or_key(
        enum_class: Enum, value: Any, default_value: Any = None
    ) -> Any:
        return EnumTool.get_by_value(enum_class, value, default_value) or EnumTool.get(
            enum_class, value, default_value
        )

    @staticmethod
    def get_value(enum_class: Enum | Any, default_value: str | None = None) -> Any:
        if nn(enum_class) and isinstance(enum_class, Enum):
            return enum_class.value
        return enum_class or default_value


class PIHEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, FieldItem):
            return {f"{obj.name}": obj.__dict__}
        if isinstance(obj, FieldItemList):
            return obj.list
        if isinstance(obj, Enum):
            return obj.name
        if isinstance(obj, ParameterList):
            return obj.values
        if dataclasses.is_dataclass(obj):
            return DataTool.to_data(obj)
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


class DataTool:

    @staticmethod
    def init_var(name: str, holder: dict[str, Any], default_value: Any = None) -> None:
        if name not in holder:
            holder[name] = default_value

    @staticmethod
    def sort(sort_function: Callable, data: list[T], reverse: bool = False) -> list[T]:
        if nn(sort_function):
            data.sort(key=sort_function, reverse=reverse)
        return data

    @staticmethod
    def every(
        action_function: Callable[[T, int], None] | Callable[[T], None],
        data: list[T],
        use_index: bool = False,
    ) -> list[T]:
        if use_index:
            for index, item in enumerate(data):
                action_function(item, index)
        else:
            for item in data:
                action_function(item)
        return data

    @staticmethod
    def fields(value: object) -> list[str]:
        if dataclasses.is_dataclass(value):
            return [field.name for field in dataclasses.fields(value)]
        return []

    @staticmethod
    def map(
        function: Callable[[Any], Any], value: list[Any] | dict[Any, Any] | Any
    ) -> list[Any] | dict[Any, Any]:
        if isinstance(value, dict):
            return (
                {} if n(value) else {key: function(data) for key, data in value.items()}
            )
        return [] if n(value) else list(map(function, DataTool.as_list(value)))

    @staticmethod
    def filter(function: Callable[[Any], bool], value: list[Any] | Any) -> list[Any]:
        return [] if n(value) else list(filter(function, DataTool.as_list(value)))

    @staticmethod
    def filter_by_string(
        string: str,
        value: list[Any] | Any,
        label_function: Callable[[Any], str] | None = None,
    ) -> list[Any]:
        string = lw(string)
        return DataTool.filter(
            lambda item: (
                lw(item if n(label_function) else label_function(item)).find(string)
            )
            != -1,
            value,
        )

    @staticmethod
    def as_value(
        function_or_value: Callable[[], str] | Callable[[Any], str] | str | None,
        parameters: Any = None,
    ) -> str:
        return (
            (function_or_value() if n(parameters) else function_or_value(parameters))
            if callable(function_or_value)
            else function_or_value
        ) or ""

    @staticmethod
    def as_bitmask_value(
        value: int | tuple[Enum, ...] | Enum | list[Enum] | list[int],
    ) -> int:
        value_list: list[Enum | int] | None = None
        if isinstance(value, (list, tuple)):
            value_list = value
        elif isinstance(value, (int, Enum)):
            value_list = [value]
        return BitMask.set(value_list)

    @staticmethod
    def by_index(data: list | None, index: int = 0, default_value: Any = None) -> Any:
        if n(data):
            return default_value
        if len(data) <= index:
            return default_value
        return data[index]

    @staticmethod
    def rpc_encode(
        data: dict[str, Any] | None, ensure_ascii: bool = True
    ) -> str | None:
        return (
            None
            if n(data)
            else json.dumps(data, cls=PIHEncoder, ensure_ascii=ensure_ascii)
        )

    @staticmethod
    def rpc_decode(value: str | None) -> dict[str, Any] | None:
        return None if e(value) else json.loads(value)

    @staticmethod
    def to_result(
        result_string: str | None,
        class_type_holder: Any | Callable[[Any], Any] | None = None,
        first_data_item: bool = False,
    ) -> Result[Any]:
        result_object: dict[str, Any] | None = DataTool.rpc_decode(result_string)
        if n(result_object):
            return Result(None, None)
        data: dict = result_object["data"]  # type: ignore
        data = DataTool.get_first_item(data) if first_data_item else data

        def fill_data_with(item: Any) -> Any:
            if e(class_type_holder):
                return item
            return (
                class_type_holder(item)
                if callable(class_type_holder) and not isclass(class_type_holder)
                else DataTool.fill_data_from_source(
                    (
                        class_type_holder()
                        if isclass(class_type_holder)
                        else class_type_holder
                    ),
                    item,
                )
            )

        def obtain_data() -> Any:
            return (
                list(map(fill_data_with, data))
                if isinstance(data, list)
                else fill_data_with(data)
            )

        if "fields_alias" in result_object:
            return Result(
                FieldItemList(
                    EnumTool.get(
                        FieldCollectionAliases, result_object["fields_alias"]
                    ).value
                ),
                obtain_data(),
            )
        else:
            fields = None if "fields" not in result_object else result_object["fields"]
        field_list: list[FieldItem] | None = None
        if nn(fields):
            field_list = []
            for field_item in fields:
                for field_name in field_item:
                    field_list.append(
                        DataTool.fill_data_from_source(
                            FieldItem(), field_item[field_name]
                        )
                    )
        return Result(FieldItemList(field_list) if field_list else None, obtain_data())

    @staticmethod
    def as_list(value: Any) -> list[Any]:
        if e(value):
            return []
        if isinstance(value, (list, tuple)):
            return value
        if isinstance(value, set):
            return list(value)
        if isinstance(value, dict):
            return list(value.values())
        try:
            if issubclass(value, Enum):
                return [EnumTool.get(item) for item in value]
        except TypeError:
            pass
        return [value]

    @staticmethod
    def to_list(value: dict | Enum, key_as_value: bool | None = False) -> list[Any]:
        if isinstance(value, dict):
            return [key if key_as_value else item for key, item in value.items()]
        result: list[Any | str] = []
        for item in value:
            result.append(
                [item.name, item.value]
                if n(key_as_value)
                else (item.name if key_as_value else item.value)
            )
        return result

    @staticmethod
    def triple_bool(
        value: bool | None, false_result: Any, true_result: Any, none_result: Any
    ) -> Any:
        if n(value):
            return none_result
        return true_result if value else false_result

    @staticmethod
    def to_result_with_fields(
        data: str, fields: FieldItemList, cls=None, first_data_item: bool = False
    ) -> Result:
        return Result(fields, DataTool.to_result(data, cls, first_data_item))

    @staticmethod
    def to_string(obj: object, join_symbol: str = "") -> str:
        return j(DataTool.to_list(DataTool.to_data(obj)), join_symbol)

    @staticmethod
    def to_data(obj: object) -> dict:
        return obj.__dict__

    @staticmethod
    def fill_data_from_source(
        destination: Any,
        source: Any,
        copy_by_index: bool = False,
        skip_not_none: bool = False,
    ) -> Any:
        if n(source):
            return None
        else:
            if dataclasses.is_dataclass(source):
                source = source.__dict__
            if copy_by_index:
                [
                    setattr(
                        destination, key.name, [source[key] for key in source][index]
                    )
                    for index, key in enumerate(dataclasses.fields(destination))
                ]
            else:
                if dataclasses.is_dataclass(source):
                    for field in destination.__dataclass_fields__:
                        if field in source:
                            if not skip_not_none or e(
                                destination.__getattribute__(field)
                            ):
                                destination.__setattr__(field, source[field])
                else:
                    is_dict: bool = isinstance(source, dict)
                    for field in destination.__dataclass_fields__:
                        if field in source if is_dict else hasattr(source, field):
                            if not skip_not_none or e(
                                destination.__getattribute__(field)
                            ):
                                destination.__setattr__(
                                    field,
                                    (
                                        source[field]
                                        if is_dict
                                        else source.__getattribute__(field)
                                    ),
                                )
        return destination

    @staticmethod
    def fill_data_from_list_source(
        class_type, source: list[Any] | dict[str, Any]
    ) -> Any:
        if n(source):
            return None
        return list(
            map(
                lambda item: DataTool.fill_data_from_source(class_type(), item),
                source if isinstance(source, list) else source.values(),
            )
        )

    @staticmethod
    def fill_data_from_rpc_str(data: T, source: str) -> T:
        return DataTool.fill_data_from_source(data, DataTool.rpc_decode(source))

    @staticmethod
    def get_first_item(
        value: list[T] | T | dict[str, Any], default_value: Any = None
    ) -> T | Any:
        if e(value):
            return default_value
        if isinstance(value, dict):
            for _, item in value.items():
                return item
        return value[0] if isinstance(value, (list, tuple)) else value

    @staticmethod
    def get_last_item(
        value: list[T] | T | dict[str, Any], default_value: Any = None
    ) -> T | Any:
        if e(value):
            return default_value
        if isinstance(value, dict):
            for _, item in reversed(value.items()):
                return item
        return value[len(value) - 1] if isinstance(value, (list, tuple)) else value

    @staticmethod
    def if_is_in(
        value: Any,
        arg_name: Any,
        default_value: Any | Callable[[], Any] | None = None,
    ) -> Any:
        return DataTool.check(
            DataTool.is_in(value, arg_name), lambda: value[arg_name], default_value
        )

    @staticmethod
    def is_in(value: Any, arg_name: Any) -> bool:
        if isinstance(value, (list, tuple)) and isinstance(arg_name, int):
            return arg_name < len(value)
        try:
            if issubclass(value, Enum):
                return arg_name in value.__members__
        except TypeError:
            pass
        return arg_name in value

    @staticmethod
    def check(
        check_value: bool | None,
        true_value: Callable[[], Any] | Any,
        false_value: Callable[[], Any] | Any = None,
        none_value: Callable[[], Any] | Any = None,
    ) -> Any:
        return if_else(check_value, true_value, false_value, none_value)

    @staticmethod
    def check_not_none(
        check_value: Any | list[Any] | tuple[Any, ...] | None,
        true_value: Callable[[], Any] | Any,
        false_value: Callable[[], Any] | Any = None,
        check_all: bool = False,
    ) -> Any:
        check: bool = False
        if isinstance(check_value, (list, tuple)):
            for item in check_value:
                check = not n(item)
                if (not check_all and check) or (check_all and not check):
                    break
        else:
            check = not n(check_value)
        return (
            (true_value() if callable(true_value) else true_value)
            if check
            else (
                false_value()
                if not n(false_value) and callable(false_value)
                else false_value
            )
        )

    @staticmethod
    def if_not_empty(
        check_value: Any,
        return_value: Callable[[Any], Any],
        default_value: Any = None,
    ) -> Any:
        return default_value if e(check_value) else return_value(check_value)

    @staticmethod
    def is_empty(value: list | str | dict | tuple | Any) -> bool:
        return n(value) or (
            isinstance(value, (list, str, dict, tuple)) and len(value) == 0
        )

    @staticmethod
    def is_not_none(value: Any) -> bool:
        return not n(value)

    @staticmethod
    def is_none(value: Any) -> bool:
        return value is None


class FullNameTool:
    SPLIT_SYMBOL: str = " "
    FULL_NAME_LENGTH: int = 3

    @staticmethod
    def format(value: str) -> str:
        return FullNameTool.fullname_to_string(FullNameTool.fullname_from_string(value))

    @staticmethod
    def fullname_to_string(full_name: FullName, join_symbol: str = SPLIT_SYMBOL) -> str:
        return DataTool.to_string(full_name, join_symbol)

    @staticmethod
    def fullname_from_string(value: str, split_symbol: str = SPLIT_SYMBOL) -> FullName:
        full_name_string_list: list[str] = ListTool.not_empty_items(
            value.split(split_symbol)
        )
        return FullName(
            full_name_string_list[0], full_name_string_list[1], full_name_string_list[2]
        )

    @staticmethod
    def is_fullname(value: str, split_symbol: str = SPLIT_SYMBOL) -> bool:
        return (
            len(ListTool.not_empty_items(value.split(split_symbol)))
            >= FullNameTool.FULL_NAME_LENGTH
        )

    @staticmethod
    def is_equal_by_fullname(fn_a: FullName, fn_b: FullName) -> bool:
        return (
            fn_a.first_name == fn_b.first_name
            and fn_a.middle_name == fn_b.middle_name
            and fn_a.last_name == fn_b.last_name
        )

    @staticmethod
    def is_intersect(fn_a: FullName, fn_b: FullName) -> bool:
        al: list[str] = [fn_a.last_name, fn_a.first_name, fn_a.middle_name]
        bl: list[str] = [fn_b.last_name, fn_b.first_name, fn_b.middle_name]
        return (
            len([value for value in al if value in bl]) == FullNameTool.FULL_NAME_LENGTH
        )

    @staticmethod
    def to_given_name(
        full_name_holder: FullName | PolibasePerson | User | str,
        join_symbol: str = SPLIT_SYMBOL,
    ) -> str:
        if isinstance(full_name_holder, PolibasePerson):
            return FullNameTool.to_given_name(full_name_holder.FullName, join_symbol)
        if isinstance(full_name_holder, User):
            return FullNameTool.to_given_name(full_name_holder.name)
        if isinstance(full_name_holder, FullName):
            return join_symbol.join(
                ListTool.not_empty_items(
                    [full_name_holder.first_name, full_name_holder.middle_name]
                )
            )
        if isinstance(full_name_holder, str):
            full_name_holder = full_name_holder.strip()
            if FullNameTool.is_fullname(full_name_holder):
                return FullNameTool.to_given_name(
                    FullNameTool.fullname_from_string(full_name_holder, join_symbol)
                )
            else:
                return full_name_holder


class BitMask:
    @staticmethod
    def add(
        value: int | None, bit: int | tuple[Enum, ...] | Enum | list[Enum] | list[int]
    ) -> int:
        value = value or 0
        bits: list[int | Enum] = bit if isinstance(bit, (list, tuple)) else [bit]
        for bit in bits:
            if isinstance(bit, int):
                value |= bit
            elif isinstance(bit, Enum):
                value |= bit.value
        return value

    @staticmethod
    def set_index(value: int, index: int) -> int:
        return BitMask.add(value, 2**index)

    @staticmethod
    def set(bit: int | tuple[Enum, ...] | Enum | list[Enum] | list[int]) -> int:
        return BitMask.add(0, bit)

    @staticmethod
    def value(bit: int | tuple[Enum, ...] | Enum | list[Enum] | list[int]) -> int:
        return BitMask.add(0, bit)

    @staticmethod
    def has(
        value: int | tuple[Enum, ...] | Enum | list[Enum] | list[int] | None,
        bit: int | tuple[Enum, ...] | Enum | list[Enum] | list[int],
    ) -> bool:
        if n(value):
            return False
        value = BitMask.value(value)
        bits: list[int] = bit if isinstance(bit, (list, tuple)) else [bit]
        result: bool = False
        if len(bits) > 1:
            for bit in bits:
                result = BitMask.has(value, bit)
                if result:
                    break
        else:
            if isinstance(bit, int):
                result = (value & bit) == bit
            elif isinstance(bit, Enum):
                result = BitMask.has(value, bit.value)
        return result

    @staticmethod
    def has_index(value: int, index: int) -> bool:
        return BitMask.has(value, pow(2, index))

    @staticmethod
    def remove(value: int | tuple[Enum, ...], bit: int | Enum) -> int:
        if not isinstance(value, int):
            value = BitMask.value(value)
        if isinstance(bit, Enum):
            bit = bit.value
        if BitMask.has(value, bit):
            value ^= bit
        return value


class ResultTool:
    @staticmethod
    def pack(fields: Any, data: Any) -> dict[str, Any]:
        result: dict[str, Any] = {"data": data}
        if isinstance(fields, FieldCollectionAliases):
            result["fields_alias"] = fields.name
        else:
            result["fields"] = fields
        return result

    @staticmethod
    def unpack(result: dict) -> tuple[FieldItemList, Any]:
        return ResultTool.unpack_fields(result), ResultTool.unpack_data(result)

    @staticmethod
    def unpack_fields(data: dict) -> Any:
        if "fields_alias" in data:
            return (FieldCollectionAliases._member_map_[data["fields_alias"]].value,)
        return data["fields"]

    @staticmethod
    def unpack_data(result: dict) -> Any:
        return result["data"]

    @staticmethod
    def is_empty(result: Result | None) -> bool:
        return n(result) or e(result.data)

    @staticmethod
    def get_first_item(
        result: Result[list[T] | T], default_value: Any = None
    ) -> T | Any:
        return DataTool.get_first_item(result.data, default_value)

    @staticmethod
    def with_first_item(
        result: Result[list[T] | T], default_value: Any = None
    ) -> Result[T]:
        result.data = ResultTool.get_first_item(result, default_value)
        return result

    @staticmethod
    def to_string(
        result: Result[T],
        use_index: bool = True,
        item_separator: str = "\n",
        value_separator: str | None = None,
        show_caption: bool = True,
    ) -> str:
        result_string_list: list[str] = []
        data: list = DataTool.as_list(result.data)
        item_result_string_list: list[str] | None = None
        for index, data_item in enumerate(data):
            if use_index and len(data) > 1:
                result_string_list.append(f"*{str(index + 1)}*:")
            if nn(value_separator):
                item_result_string_list = []
            for field_item in result.fields.list:
                field: FieldItem = field_item
                if not field.visible:
                    continue
                data_value: str | None = None
                if isinstance(data_item, dict):
                    data_value = data_item[field.name]
                elif dataclasses.is_dataclass(data_item):
                    data_value = data_item.__getattribute__(field.name)
                data_value = data_value or "Нет"
                if n(value_separator):
                    if show_caption:
                        result_string_list.append(f"{field.caption}: {data_value}")
                    else:
                        result_string_list.append(data_value)
                else:
                    if show_caption:
                        item_result_string_list.append(f"{field.caption}: {data_value}")
                    else:
                        item_result_string_list.append(data_value)
            if nn(value_separator):
                result_string_list.append(value_separator.join(item_result_string_list))
        return item_separator.join(result_string_list)

    @staticmethod
    def as_list(result: Result[T]) -> Result[list[T]]:
        return Result(
            result.fields,
            (
                []
                if n(result.data)
                else [result.data] if not isinstance(result.data, list) else result.data
            ),
        )

    @staticmethod
    def filter(
        filter_function: Callable[[T], bool],
        result: Result[list[T]],
        as_new_result: bool = False,
    ) -> Result[list[T]]:
        try:
            data: list[T] = DataTool.filter(filter_function, result.data)
            if as_new_result:
                return Result(result.fields, data)
            result.data = data
        except StopIteration as _:
            pass
        return result

    @staticmethod
    def sort(
        sort_function: Callable, result: Result[list[T]], reverse: bool = False
    ) -> Result[list[T]]:
        if nn(sort_function):
            result.data.sort(key=sort_function, reverse=reverse)
        return result

    @staticmethod
    def every(
        action_function: Callable[[T, int], None] | Callable[[T], None],
        result: Result[list[T]],
        use_index: bool = False,
    ) -> Result[list[T]]:
        result.data = DataTool.every(action_function, result.data, use_index)
        return result

    @staticmethod
    def every_with_fields(
        action_function: Callable[[T, int, FieldItemList], None] | Callable[[T], None],
        result: Result[list[T]],
        use_index: bool = False,
    ) -> Result[list[T]]:
        return (
            ResultTool.every(
                lambda item, index: action_function(item, index, result.fields),
                result,
                use_index,
            )
            if use_index
            else ResultTool.every(
                lambda item: action_function(item, result.fields),
                result,
                use_index,
            )
        )

    @staticmethod
    def do_while(result: Result[list[T]], check_function: Callable[[T], bool]) -> Any:
        result_data: Any = None
        for item in result.data:
            if check_function(item):
                result_data = item
                break
        return result_data

    @staticmethod
    def map(
        map_function_or_class: Callable[[T], R] | R,
        result: Result[list[T]],
        map_on_each_data_item: bool = True,
        as_new_result: bool = False,
    ) -> Result[list[R]]:
        map_function: Callable[[T], R] | None = None
        if not isfunction(map_function_or_class):
            map_function = lambda item: DataTool.fill_data_from_source(
                map_function_or_class(), item
            )
        else:
            map_function = map_function_or_class
        data: list[R] = (
            list(map(map_function, result.data))
            if map_on_each_data_item
            else map_function_or_class(result.data)
        )
        if as_new_result:
            return Result(result.fields, data)
        else:
            result.data = data
        return result


n = DataTool.is_none
nn = DataTool.is_not_none


def lw(
    value: str | list[str] | tuple[str, ...] | None
) -> str | list[str] | tuple[str, ...]:
    if n(value):
        return ""
    if isinstance(value, str):
        return lw([value])[0]
    return DataTool.map(str.lower, value)


def e(value: Any | Result[Any]) -> bool:
    return (
        ResultTool.is_empty(value)
        if isinstance(value, Result)
        else DataTool.is_empty(value)
    )


ne = lambda item: not e(item)


def ln(value: Any) -> int:
    return 0 if n(value) else len(value)


def separate_on_parts(value: Any) -> tuple[str, str, str]:
    value = str(value)
    strip_value: str = value.strip()
    index: int = value.find(strip_value)
    left: str = value[0:index]
    right: str = value[index + len(strip_value) :]
    return (left, strip_value, right)


def b(value: Any) -> str:
    if e(value):
        return ""
    return j((BOLD_BEGIN, str(value).strip(), BOLD_END))


def i(value: Any) -> str:
    if e(value):
        return ""
    return j((ITALICS_BEGIN, str(value).strip(), ITALICS_END))


def surround_text_with(text: Any, value: str) -> str:
    if ne(text):
        left, text, right = separate_on_parts(text)
        if text.find(value) == -1:
            return j((left, value, text, value, right))
    return text or ""


def lnk(value: str) -> str:
    return j(("{", value, "}"))


def esc(value: Any, single: bool = False) -> str:
    return f"'{value}'" if single else f'"{value}"'


def it(value: Any, action: Callable[[Any], None]) -> Any:
    action(value)
    return value


def escs(
    value: Any,
) -> str:
    return esc(value, True)


class ListTool:

    @staticmethod
    def diff(a: list[Any], b: list[Any]) -> list[Any]:
        return [i for i in a + b if not (i in a and i in b)]

    @staticmethod
    def list_str_diff(
        a: list[str],
        b: list[str],
    ) -> list[str]:
        def compare_function(value1: str, value2: list[str]) -> bool:
            for item in value2:
                if StringTool.contains(value1, item, True):
                    return True
            return False

        return [
            i for i in a + b if not (compare_function(i, a) and compare_function(i, b))
        ]

    @staticmethod
    def intersection(a: list[Any], b: list[Any]) -> bool:
        return len(ListTool.diff(a, b)) < (len(a) + len(b))

    @staticmethod
    def list_of_str_intersection(a: list[str], b: list[str]) -> bool:
        return ListTool.list_str_intersection_ratio(a, b) < (len(a) + len(b))

    @staticmethod
    def list_str_intersection_ratio(
        a: list[str],
        b: list[str],
    ) -> int:
        return len(ListTool.list_str_diff(a, b))

    @staticmethod
    def str_list_equal(a: list[str], b: list[str]) -> bool:
        return len(ListTool.list_str_diff(a, b)) == 0

    @staticmethod
    def to_dict_with_none_value(
        value: list[Any], modificator: Callable[[Any], Any] | None = None
    ) -> dict[Any, None]:
        return {item if n(modificator) else modificator(item): None for item in value}  # type: ignore

    @staticmethod
    def to_dict(value: list[Any], key: str) -> dict[Any, Any]:
        return {getattr(item, key): item for item in value}

    @staticmethod
    def not_empty_items(value: list[Any]) -> list[Any]:
        return list(filter(lambda item: ne(item), value))

    @staticmethod
    def not_less_length_items(value: list[Any], length: int) -> list[Any]:
        return list(filter(lambda item: ne(item) and len(item) >= length, value))


class StringTool:

    @staticmethod
    def bold(value: Any) -> str:
        return j((BOLD_BEGIN, str(value).strip(), BOLD_END))

    @staticmethod
    def italics(value: Any) -> str:
        return j((ITALICS_BEGIN, str(value).strip(), ITALICS_END))

    @staticmethod
    def split(value: str, delimiters: tuple[str, ...] | str) -> list[str]:
        if isinstance(delimiters, str):
            delimiters = (delimiters,)
        for delimiter in delimiters:
            value = js(value.split(delimiter))
        return StringTool.space_format(value).split(" ")

    @staticmethod
    def _comparation_ratio_by_tokens(
        a: str,
        b: str,
        token_delimiter: str | tuple[str, ...] = " ",
    ) -> tuple[int, list[str], list[str]]:
        if isinstance(token_delimiter, str):
            token_delimiter = (token_delimiter,)
        a = lw(a)
        b = lw(b)
        a_list: list[str] = StringTool.split(a, token_delimiter)
        b_list: list[str] = StringTool.split(b, token_delimiter)
        a_list = ListTool.not_empty_items(list(set(a_list)))
        b_list = ListTool.not_empty_items(list(set(b_list)))
        return (
            ListTool.list_str_intersection_ratio(a_list, b_list),
            a_list,
            b_list,
        )

    @staticmethod
    def equal_by_tokens(
        a: str,
        b: str,
        token_delimiter: str | tuple[str, ...] = " ",
    ) -> bool:
        return StringTool._comparation_ratio_by_tokens(a, b, token_delimiter)[0] == 0

    @staticmethod
    def intersection_by_tokens(
        a: str,
        b: str,
        token_delimiter: str | tuple[str, ...] = " ",
    ) -> bool:
        result: tuple[int, list[str], list[str]] = (
            StringTool._comparation_ratio_by_tokens(a, b, token_delimiter)
        )
        return result[0] < (len(result[1]) + len(result[2]))

    @staticmethod
    def full_right_intersection_by_tokens(
        a: str,
        b: str,
        token_delimiter: str | tuple[str, ...] = " ",
    ) -> bool:
        if a.find(b) != -1:
            return True
        result: tuple[int, list[str], list[str]] = (
            StringTool._comparation_ratio_by_tokens(a, b, token_delimiter)
        )
        return result[0] == (len(result[1]) - len(result[2]))

    @staticmethod
    def has_one_of(text: str, variants: list[str]) -> bool:
        def mapper(value: str) -> str:
            value = value.replace(" ", "[ ,]*")
            value_variable_list: list[str] = ListTool.not_empty_items(value.split("|"))
            if len(value_variable_list) > 1:
                value = j(
                    (
                        value_variable_list[0],
                        r"(?:\(|",
                        j(value_variable_list[1:], "|"),
                        "|$)",
                    )
                )
            return value

        return nn(
            re.search(
                j(
                    (
                        r"\b(",
                        j(
                            DataTool.map(
                                mapper,
                                variants,
                            ),
                            "|",
                        ),
                        r")\b",
                    )
                ),
                text,
                flags=re.IGNORECASE,
            )
        )

    @staticmethod
    def space_format(value: str | None) -> str | None:
        if n(value):
            return value
        return nns(value).replace("\xa0", " ")

    @staticmethod
    def split_by_space(value: str | None) -> list[str]:
        return StringTool.space_format((value or "")).split(" ")

    @staticmethod
    def contains(value1: str, value2: str, start_with: bool = False) -> bool:
        if e(value1) or e(value2):
            return False

        def eq(value1: str, value2: str) -> bool:
            return (
                value1.startswith(value2) if start_with else value1.find(value2) != -1
            )

        value1 = value1.lower()
        value2 = value2.lower()
        return eq(value2, value1) if len(value2) > len(value1) else eq(value1, value2)

    @staticmethod
    def equal(value1: str, value2: str) -> bool:
        if n(value1) or n(value2):
            return False
        value1 = value1.lower()
        value2 = value2.lower()
        return value1 == value2

    @staticmethod
    def split_with_not_empty_items(value: str, symbol: str = " ") -> list[str]:
        return ListTool.not_empty_items(value.split(symbol))

    @staticmethod
    def separate_unquoted_and_quoted(value: str) -> tuple[list[str], list[str]]:
        list_value: list[str] = shlex.split(value, posix=False)

        def is_quotes(value: str) -> bool:
            return value[0] == value[-1] and value[0] in ('"', "'")

        return (
            DataTool.filter(lambda item: not is_quotes(item), list_value),
            DataTool.map(
                lambda item: item[1:-1], DataTool.filter(is_quotes, list_value)
            ),
        )

    @staticmethod
    def list_to_string(
        value: list[str],
        escaped_string: bool = False,
        separator: str = ", ",
        start: str = "",
        end: str = "",
        filter_empty: bool = False,
    ) -> str:
        return (
            start
            + separator.join(
                list(
                    map(
                        lambda item: (
                            f"'{item}'"
                            if escaped_string
                            else str(item) if nn(item) else ""
                        ),
                        list(filter(lambda item: not filter_empty or ne(item), value)),
                    )
                )
            )
            + end
        )

    @staticmethod
    def capitalize(value: str) -> str:
        if e(value):
            return ""
        return value[0].upper() + ("" if len(value) == 1 else value[1:])

    @staticmethod
    def decapitalize(value: str) -> str:
        if e(value):
            return ""
        return value[0].lower() + ("" if len(value) == 1 else value[1:])

    @staticmethod
    def decapitalize(value: str) -> str:
        if e(value):
            return ""
        result: str = ""
        for index, char in enumerate(value):
            char_is_upper: bool = char.isupper()
            if char == " " or char_is_upper:
                char = char.lower() if char_is_upper else char
                result += char
                break
            result += char
        return result + value[index + 1 :] if index < len(value) else ""

    @staticmethod
    def from_russian_keyboard_layout(value: str) -> str:
        dictionary: dict[str, str] = {
            "Й": "Q",
            "Ц": "W",
            "У": "E",
            "К": "R",
            "Е": "T",
            "Н": "Y",
            "Г": "U",
            "Ш": "I",
            "Щ": "O",
            "З": "P",
            "Х": "{",
            "Ъ": "}",
            "Ф": "A",
            "Ы": "S",
            "В": "D",
            "А": "F",
            "П": "G",
            "Р": "H",
            "О": "J",
            "Л": "K",
            "Д": "L",
            "Ж": ":",
            "Э": '"',
            "Я": "Z",
            "Ч": "X",
            "С": "C",
            "М": "V",
            "И": "B",
            "Т": "N",
            "Ь": "M",
            "Б": "<",
            "Ю": ">",
            "Ё": "~",
            "й": "q",
            "ц": "w",
            "у": "e",
            "к": "r",
            "е": "t",
            "н": "y",
            "г": "u",
            "ш": "i",
            "щ": "o",
            "з": "p",
            "х": "[",
            "ъ": "]",
            "ф": "a",
            "ы": "s",
            "в": "d",
            "а": "f",
            "п": "g",
            "р": "h",
            "о": "j",
            "л": "k",
            "д": "l",
            "ж": ";",
            "э": "'",
            "я": "z",
            "ч": "x",
            "с": "c",
            "м": "v",
            "и": "b",
            "т": "n",
            "ь": "m",
            "б": ",",
            "ю": ".",
            "ё": "`",
        }
        result: str = ""
        for item in value:
            result += dictionary[item] if item in dictionary else item
        return result


class DateTimeTool:

    @staticmethod
    def is_now(cron_string: str, value: datetime | None = None) -> bool:
        cron_string = cron_string.strip()
        as_time_list: list[str] = cron_string.split(":")
        if len(as_time_list) > 1:
            cron_string = js((as_time_list[1], as_time_list[0], "*", "*", "*"))
        else:
            length: int = len(cron_string.split(" "))
            need_length: int = 5
            if length < need_length:
                cron_string = j((cron_string, " *" * (need_length - length)))
        return pycron.is_now(cron_string, value)

    @staticmethod
    def day_count(date: date | datetime, month_count: int) -> int:
        result: int = 0
        year: int = date.year
        month: int = date.month
        current_month: int = month
        for _ in range(month_count):
            if current_month > 12:
                year += 1
                current_month = 1
            result += calendar.monthrange(year, current_month)[1]
            current_month += 1
        return result

    @staticmethod
    def add_months(date: date | datetime, value: int) -> date | datetime:
        return date + timedelta(days=DateTimeTool.day_count(date, value))

    @staticmethod
    def seconds_to_days(value: int) -> float:
        return value / 60 / 60 / 24

    @staticmethod
    def yesterday(as_datetime: bool = False) -> datetime | date:
        return DateTimeTool.today(-1, as_datetime=as_datetime)

    @staticmethod
    def begin_date(value: datetime | date | None = None) -> datetime | date:
        value = value or DateTimeTool.today(as_datetime=True)
        if isinstance(value, date):
            value = datetime.combine(value, datetime.min.time())
        return value.replace(hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def end_date(value: datetime | date | None = None) -> datetime | date:
        value = value or DateTimeTool.today(as_datetime=True)
        if isinstance(value, date):
            value = datetime.combine(value, datetime.min.time())
        return value.replace(hour=23, minute=59, second=59, microsecond=0)

    @staticmethod
    def timestamp() -> int:
        return int(datetime.now().timestamp())

    @staticmethod
    def date_or_today_string(value: datetime | None, format: str | None = None) -> str:
        return (
            DateTimeTool.datetime_to_string(value, format)
            if nn(value)
            else DateTimeTool.today_string(format)
        )

    @staticmethod
    def today_string(format: str | None = None, delta_days: int = 0) -> str:
        return DateTimeTool.datetime_to_string(
            DateTimeTool.today(delta_days, as_datetime=True), format
        )

    @staticmethod
    def datetime_to_string(
        date: datetime | date | None, format: str | None = None
    ) -> str | None:
        if n(date):
            return None
        return DataTool.check_not_none(
            format, lambda: date.strftime(format), lambda: date.isoformat()
        )

    @staticmethod
    def date_to_string(date: datetime | date, format: str | None = None) -> str:
        return DateTimeTool.datetime_to_string(
            date.date() if isinstance(date, datetime) else date, format
        )

    @staticmethod
    def to_date_string(isoformat_date_string: str) -> str:
        return isoformat_date_string.split(DATE_TIME.SPLITTER)[0]

    @staticmethod
    def today(delta_days: int = 0, as_datetime: bool = False) -> date | datetime:
        value: date = (datetime.today() + timedelta(days=delta_days)).date()
        if as_datetime:
            return datetime.combine(value, datetime.min.time())
        return value

    @staticmethod
    def now(
        minute: int | None = None,
        second: int | None = None,
        use_microsecond: bool = False,
    ) -> datetime:
        result: datetime = datetime.now()
        if ne(minute):
            result = result.replace(minute=minute)
        if ne(second):
            result = result.replace(second=second)
        return result if use_microsecond else result.replace(microsecond=0)

    @staticmethod
    def now_to_string(format: str | None = None) -> str:
        return DateTimeTool.datetime_to_string(DateTimeTool.now(), format)

    @staticmethod
    def now_time_to_string(format: str | None = None, delta_minutes: int = 0) -> str:
        return DateTimeTool.datetime_to_string(
            DateTimeTool.now_time(delta_minutes), format
        )

    @staticmethod
    def now_time(delta_minutes: int = 0) -> datetime:
        return datetime.combine(date.today(), datetime.now().time()) + timedelta(
            minutes=delta_minutes
        )

    @staticmethod
    def datetime_from_string(
        value: datetime | None, format: str | None = None
    ) -> datetime | None:
        if e(value):
            return None
        return DataTool.check_not_none(
            format,
            lambda: datetime.strptime(nnt(value), nnt(format)),
            lambda: datetime.fromisoformat(nnt(value)),
        )

    @staticmethod
    def datetime_or_date_from_string(
        value: str | None, format: str | None = None, as_date: bool = False
    ) -> datetime | date | None:
        if e(value):
            return None
        result: datetime = DataTool.check_not_none(
            format,
            lambda: datetime.strptime(value, format),
            lambda: datetime.fromisoformat(value),
        )
        if value.find(DATE_TIME.SPLITTER) != -1 and not as_date:
            return result
        return result.date()

    @staticmethod
    def date_from_string(value: str) -> date | None:
        return DateTimeTool.datetime_or_date_from_string(value, as_date=True)

    @staticmethod
    def is_equal_by_time(
        date: datetime, value: datetime | tuple[int, int] | list[int]
    ) -> bool | None:
        if isinstance(value, (tuple, list)):
            return date.hour == value[0] and date.minute == value[1]
        if isinstance(value, datetime):
            return date.hour == value.hour and date.minute == value.minute
        return None


class TranslateTool:
    @staticmethod
    def ru_to_en(value: str) -> str:
        return value.translate(
            dict(
                zip(
                    map(
                        ord,
                        "йцукенгшщзхъфывапролджэячсмитьбю.ё"
                        "ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё",
                    ),
                    "qwertyuiop[]asdfghjkl;'zxcvbnm,./`"
                    'QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~',
                )
            )
        )


class PathTool:

    @staticmethod
    def directory_size(path: str) -> int:
        result = 0
        dirs = [path]
        while dirs:
            next_dir = dirs.pop()
            with scandir(next_dir) as it:
                for entry in it:
                    if entry.is_dir(follow_symlinks=False):
                        dirs.append(entry.path)
                    else:
                        result += entry.stat(follow_symlinks=False).st_size
        return result

    @staticmethod
    def path(value: str) -> str:
        return value.replace("\\", "/")

    @staticmethod
    def for_windows(value: str) -> str:
        separator: str = "\\"
        value = value.replace("/", separator)
        if value.find(":") == -1 and not value.startswith(separator * 2):
            value = j((separator * 2, value))
        return value

    @staticmethod
    def exists(path: str) -> bool:
        return os.path.exists(path)

    @staticmethod
    def convert_for_unix(path: str) -> str:
        prefix: str = os.sep * 2
        path = path.replace("\\", "/").replace("\\\\", "//")
        return if_else(path.startswith(prefix), "", prefix) + path

    @staticmethod
    def get_file_list(path: str, created_after: float | None = None) -> list[str]:
        file_list: list[tuple[str, float]] = [
            (file_path, int(os.path.getctime(file_path)))
            for file_path in [
                os.path.join(path, file_path)
                for file_path in [
                    file_path for file_path in next(walk(path), (None, None, []))[2]
                ]
            ]
        ]
        if nn(created_after):
            file_list = sorted(file_list, key=itemgetter(1), reverse=True)
            return [
                file_item[0] for file_item in file_list if file_item[1] > created_after
            ]
        return [file_item[0] for file_item in file_list]

    @staticmethod
    def make_directory_if_not_exists(path: str) -> bool | None:
        try:
            is_exist = os.path.exists(path)
            if not is_exist:
                os.makedirs(path)
                return True
            return False
        except:
            return None

    @staticmethod
    def get_current_full_path(file_name: str) -> str:
        return os.path.join(sys.path[0], file_name)

    @staticmethod
    def add_extension(
        file_path: str | None = None, extension: str | None = None
    ) -> str:
        if nn(file_path):
            dot_index: int = file_path.find(".")
            if dot_index != -1:
                source_extension: str = file_path.split(".")[-1]
                if source_extension == extension:
                    file_path = file_path[0:dot_index]
        return jp((file_path, extension))

    @staticmethod
    def get_file_name(path: str, with_extension: bool = False):
        head, tail = ntpath.split(path)
        value = tail or ntpath.basename(head)
        if not with_extension:
            value = value[0 : value.rfind(".")]
        return value

    @staticmethod
    def get_file_directory(path: str):
        head, _ = ntpath.split(path)
        if head[-1] in ["\\", "/"]:
            head = head[:-1]
        return head

    @staticmethod
    def get_extension(
        file_path: str,
    ) -> str:
        dot_index: int = file_path.rfind(".")
        if dot_index != -1:
            return file_path[dot_index + 1 :].lower()
        return ""

    @staticmethod
    def replace_prohibited_symbols_from_path_with_symbol(
        path: str, replaced_symbol: str = "_"
    ) -> str:
        return (
            path.replace("\\", replaced_symbol)
            .replace("/", replaced_symbol)
            .replace("?", replaced_symbol)
            .replace("<", replaced_symbol)
            .replace(">", replaced_symbol)
            .replace("*", replaced_symbol)
            .replace(":", replaced_symbol)
            .replace('"', replaced_symbol)
        )

    @staticmethod
    def resolve(src_path: str, host_nane: str | None = None) -> str:
        src_path = str(pathlib.Path(src_path).resolve())
        if src_path[1] == ":" and nn(host_nane):
            lan_adress: str = f"\\\\{host_nane}\\"
            src_path = j((lan_adress, src_path[0], "$", src_path[2:]))
        return src_path


class NetworkTool:
    @staticmethod
    def next_free_port() -> int:
        with socket.socket() as soc:
            soc.bind(("", 0))
            return soc.getsockname()[1]


def while_not_do(
    check_action: Callable[[], bool | Any] | None = None,
    attemp_count: int | None = None,
    success_handler: Callable[[], None] | None = None,
    start_handler: Callable[[], None] | None = None,
    sleep_time: int | None = None,
    action: Callable[[], Any] | None = None,
    check_action_as_bool: bool = True,
) -> Any:
    result: Any = None
    while e(check_action) or (
        (not check_action()) if check_action_as_bool else n(result := check_action())
    ):
        if nn(start_handler):
            start_handler()
            start_handler = None
        if nn(action):
            action()
        if nn(attemp_count):
            if attemp_count == 0:
                break
            attemp_count -= 1
        if nn(sleep_time):
            sleep(sleep_time)
    if nn(success_handler):
        success_handler()
    return result


def while_excepted(
    check_action: Callable[[], Any],
    on_except: Callable[[Any], None] | None = None,
) -> Any:
    def action() -> Any:
        try:
            return check_action()
        except Exception as error:
            if nn(on_except):
                on_except(error)
            return None

    return while_not_do(action, check_action_as_bool=False)


class Clipboard:
    @staticmethod
    def copy(value: str):
        import pyperclip as pc

        pc.copy(value)


class UserTools:
    @staticmethod
    def get_given_name(user: User) -> str:
        return FullNameTool.to_given_name(user.name)


class PasswordTools:
    @staticmethod
    def check_password(value: str, length: int, special_characters: str) -> bool:
        regexp_string = (
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*["
            + special_characters
            + r"])[A-Za-z\d"
            + special_characters
            + "]{"
            + str(length)
            + ",}$"
        )
        password_checker = re.compile(regexp_string)
        return nn(re.fullmatch(password_checker, value))

    @staticmethod
    def generate_random_password(
        length: int,
        special_characters: str,
        order_list: list[str],
        special_characters_count: int,
        alphabets_lowercase_count: int,
        alphabets_uppercase_count: int,
        digits_count: int,
        shuffled: bool,
    ):
        alphabets_lowercase = list(string.ascii_lowercase)
        alphabets_uppercase = list(string.ascii_uppercase)
        digits = list(string.digits)
        characters = list(string.ascii_letters + string.digits + special_characters)
        characters_count = (
            alphabets_lowercase_count
            + alphabets_uppercase_count
            + digits_count
            + special_characters_count
        )
        if characters_count > length:
            return
        password: list[str] = []
        for order_item in order_list:
            if order_item == RULES.SPECIAL_CHARACTER:
                for i in range(special_characters_count):
                    password.append(random.choice(special_characters))
            elif order_item == RULES.LOWERCASE_ALPHABET:
                for i in range(alphabets_lowercase_count):
                    password.append(random.choice(alphabets_lowercase))
            elif order_item == RULES.UPPERCASE_ALPHABET:
                for i in range(alphabets_uppercase_count):
                    password.append(random.choice(alphabets_uppercase))
            elif order_item == RULES.DIGIT:
                for i in range(digits_count):
                    password.append(random.choice(digits))
        if characters_count < length:
            random.shuffle(characters)
            for i in range(length - characters_count):
                password.append(random.choice(characters))
        if shuffled:
            random.shuffle(password)
        return j(password)


class OSTool:
    @staticmethod
    def host() -> str:
        return platform.node()

    @staticmethod
    def pid() -> int:
        return os.getppid()


class ErrorTool:
    @contextmanager
    def detect(
        final_action: Callable[[], None] | None = None,
        error_handler: Callable[[Any], None] | None = None,
    ):
        try:
            yield True
        except Exception as error:
            if nn(error_handler):
                error_handler(error)
        finally:
            if nn(final_action):
                final_action()
