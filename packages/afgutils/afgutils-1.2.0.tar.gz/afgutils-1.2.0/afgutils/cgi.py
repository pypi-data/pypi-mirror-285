import json
import os
import sys
from typing import Any
from urllib import parse

import xmltodict


class FieldStorage:
    class Field:
        def __init__(self, value: str | list[str]):
            self.value: str | list[str] = value

        def __str__(self):
            return str(self.value)

    def __init__(self):
        self._fields: dict[str, FieldStorage.Field] = {}
        self.body_data: str = sys.stdin.read()
        self._query_string_parsed: dict[str, FieldStorage.Field] = {}
        self._body_data_parsed: dict[str, Any] = {}
        self._populate_fields()

    def __iter__(self):
        return iter(self._fields.keys())

    def __getitem__(self, key: str) -> Field:
        return self._fields[key]

    def __str__(self):
        return str(self._fields)

    def _populate_fields(self) -> None:
        request_method: str = os.getenv("REQUEST_METHOD")
        self._query_string_parsed = self._populate_fields_from_query_string(query_string=os.getenv("QUERY_STRING"))
        self._fields.update(self._query_string_parsed)
        if request_method == "POST":
            self._populate_fields_from_post()

    def _populate_fields_from_post(self):
        content_type: str = os.getenv("CONTENT_TYPE")
        if content_type == "application/x-www-form-urlencoded":
            self._body_data_parsed = self._populate_fields_from_query_string(query_string=self.body_data)
            self._fields.update(self._body_data_parsed)
        elif content_type == "application/json":
            self._body_data_parsed: dict[str, Any] = json.loads(self.body_data)
            self._fields.update({key: self.Field(value=value) for key, value in self._body_data_parsed.items()})
        elif content_type == "application/xml":
            self._body_data_parsed = xmltodict.parse(self.body_data)
            self._fields.update({key: self.Field(value=value) for key, value in self._body_data_parsed.items()})

    def _populate_fields_from_query_string(self, query_string: str) -> dict[str, Field]:
        parsed_fields: list[tuple] = parse.parse_qsl(query_string)
        fields: dict[str, FieldStorage.Field] = {}
        for field, value in parsed_fields:
            field_instance: FieldStorage.Field = fields.get(field)
            if field_instance is None:
                fields[field] = self.Field(value)
            elif isinstance(field_instance.value, list):
                field_instance.value.append(value)
            else:
                field_instance.value = [field_instance.value, value]
        return fields

    def getvalue(self, item_key: str, def_value: Any = None) -> str | list[str]:
        item_object=self._fields.get(item_key)
        if item_object is None:
            return def_value
        return item_object.value

    def keys(self):
        return self._fields.keys()
