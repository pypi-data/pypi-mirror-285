from __future__ import annotations

from copy import deepcopy
from typing import Any, Union
from urllib.parse import parse_qs, urlencode

qs_value = Union[str, list[str]]


class Query:
    __slots__ = ("_string", "_data")

    def __init__(self, _string: str = "") -> None:
        self._data = self._str_to_dict(_string)
        self._string = self._dict_to_str(self._data)

    @classmethod
    def from_dict(
        cls, dict_: dict[str, qs_value] | None = None, **kwargs: qs_value
    ) -> Query:
        dict_ = dict(dict_ or {}, **kwargs)
        return cls(cls._dict_to_str(dict_))

    def __str__(self) -> str:
        return self._string

    def __hash__(self) -> int:
        return hash(self._string)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self._string == other._string

    def __repr__(self) -> str:
        return f"Query('{self}')"

    def __bool__(self) -> bool:
        return bool(self._string)

    @property
    def string(self) -> str:
        return self._string

    @property
    def data(self) -> dict[str, list[str]]:
        return self._data

    @staticmethod
    def _str_to_dict(string: str) -> dict[str, list[str]]:
        return parse_qs(string, keep_blank_values=True)

    @staticmethod
    def _dict_to_str(data_: dict[str, Any]) -> str:
        return urlencode(data_, doseq=True)

    def get(self, key: str) -> list[str] | None:
        return self._data.get(key)

    def add(
        self, dict_: dict[str, qs_value] | None = None, **kwargs: qs_value
    ) -> Query:
        data = deepcopy(self._data)
        dict_ = dict(dict_ or {}, **kwargs)
        for key, value in dict_.items():
            data.setdefault(key, [])
            if isinstance(value, list):
                data[key].extend(value)
            else:
                data[key].append(value)
        return self.__class__(self._dict_to_str(data))

    def set(
        self, dict_: dict[str, qs_value] | None = None, **kwargs: qs_value
    ) -> Query:
        data = deepcopy(self._data)
        dict_ = dict(dict_ or {}, **kwargs)
        for key, value in dict_.items():
            data.setdefault(key, [])
            if isinstance(value, list):
                data[key] = value
            else:
                data[key] = [value]
        return self.__class__(self._dict_to_str(data))

    def replace(
        self, dict_: dict[str, tuple[str, str]] | None = None, **kwargs: tuple[str, str]
    ) -> Query:
        data = deepcopy(self._data)
        dict_ = dict(dict_ or {}, **kwargs)
        for key, (old_value, new_value) in dict_.items():
            for i, value in enumerate(data.get(key, [])):
                if value == old_value:
                    data[key][i] = new_value
        return self.__class__(self._dict_to_str(data))

    def remove(self, key: str) -> Query:
        data = deepcopy(self._data)
        del data[key]
        return self.__class__(self._dict_to_str(data))
