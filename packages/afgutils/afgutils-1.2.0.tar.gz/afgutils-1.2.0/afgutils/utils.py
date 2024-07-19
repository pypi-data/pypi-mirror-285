# CHANGE LOG
#
# 2023-09-05
# Added:
# generate_random_token()
# parse_row_into_object()
# afg_base_object_class
# afg_freezable_object_class
# query_result_class
# type hints to function definitions
#
# get_username() removed, now it is uwtool-specific, to be replaced with a general purpose
# session handling function (to be used not only in uwtool)
#
# 2024-17-18
# docstrings added

import time
import string
import secrets
# from os import environ
# from .db import DB, sql
from pandas import DataFrame
import pyodbc
from typing import Any
from afgutils.db import DB


# session_token_cookie_name = "uwtool_session_token"


def print_log(*args, **kwargs) -> None:
    """Prints a line preceeded by a timestamp"""
    print(time.strftime('%Y-%m-%d %H:%M:%S'), *args, **kwargs)


def ci(cursor: pyodbc.Cursor, column_name: str) -> int:
    """Returns the index of a column in a cursor by its name"""
    column_index_cnt = -1
    column_index = -1
    for column in cursor.description:
        column_index_cnt = column_index_cnt + 1
        if column[0] == column_name:
            column_index = column_index_cnt
            break
    if column_index == -1:
        raise SystemExit("ERROR: Column index not found for column: " + column_name)
    return column_index


def nvl(s: Any, d: Any) -> Any:
    """Returns d if s is None, otherwise returns s"""
    if s is None:
        return d
    else:
        return s


def iif(bool_val: bool, ret_true, ret_false):
    """Returns ret_true if bool_val is True, otherwise returns ret_false"""
    if bool_val:
        aaa = ret_true
    else:
        aaa = ret_false
    return aaa


def isnullorempty(v) -> bool:
    """Returns True if v is None or an empty/whitespace-only string, otherwise returns False"""
    if v is None:
        return True
    if type(v) == str:
        v = v.strip()
        if len(v) == 0:
            return True
    return False


def clear_mfv(mfv: dict) -> dict:
    if type(mfv) == dict:
        for i in mfv.keys():
            mfv[i] = None
    return mfv


# def get_username()-> str:
#     conn_repserv = DB.get_connection('repserv')
#     cursor_repserv = conn_repserv.cursor()
#
#     username = None
#
#     if 'HTTP_COOKIE' in environ:
#         for cookie in map(str.strip, environ['HTTP_COOKIE'].split(';')):
#             key, value = cookie.split('=')
#             if key == session_token_cookie_name:
#                 uwtool_session_token = value
#                 result = DB.execute(cursor=cursor_repserv,
#                                     query=sql("find_session", 2),
#                                     fetch='one',
#                                     parameters=uwtool_session_token)
#                 if result:  # can be replaced by "if cursor_repserv.rowcount"
#                     username = result['username']
#                     DB.execute(cursor_repserv, sql("update_session", 1), None, (uwtool_session_token, username))
#                     cursor_repserv.commit()
#
#     cursor_repserv.close()
#
#     return username


def data_vector_to_sql_insert(data_vector: dict | DataFrame, insert_sql_tpl: str = None,
                              existing_values: list = None) -> (list, str):
    """
    Returns data tuple and an SQL INSERT statement to be used in conjunction with DB.execute() function.

    data_vector
        a pandas.DataFrame or a dictionary containing data to be inserted
    insert_sql_tpl
        a template of an SQL INSERT statement; if None then a string with comma-separated column names from
        data_vector is returned instead of a full SQL statement
    existing_values
        a list of values to be inserted at the beginning of the result data tuple, before values from
        data_vector; useful if there are already some hardcoded column names and '?' placeholders in the
        template

    dict and list values are serialized into strings in the resulting data tuple

    Template format:

    INSERT INTO table_name (col1, ..., colX, {0}) VALUES (?, ..., ?, {1})

    {0} is replaced with keys from the data_vector; {1} is replaced with a number of '?' placeholders equal
    to the number of keys in the data_vector
    """

    column_names_insert_text = ""
    item_values = []

    # convert data vector into a list
    if isinstance(data_vector, DataFrame):
        for column_name in data_vector.columns.tolist():
            column_names_insert_text = (column_names_insert_text + "," + column_name + "\r\n").replace(".",
                                                                                                       "_")
            item_values.append(data_vector.loc[0, column_name])

    elif type(data_vector) is dict:
        # TODO: implement dictionary data_vector processing
        raise NotImplementedError("data_vector_to_sql_insert: dictionary data_vector is not implemented yet")

    else:
        raise TypeError("data_vector_to_sql_insert: data_vector must be a pandas.DataFrame or a dictionary")

    # text-serialize any embedded lists or dictionaries
    item_values = [str(item_value) if type(item_value) in (list, dict) else item_value for item_value in
                   item_values]

    # combine existing values with new values
    if type(existing_values) is list:
        result_items = existing_values + item_values
    elif existing_values is None:
        result_items = item_values
    else:
        raise TypeError("data_vector_to_sql_insert: existing_values must be a list or None")

    # generate SQL
    if type(insert_sql_tpl) is str:
        result_sql = insert_sql_tpl.format(column_names_insert_text, f"{', ?' * len(item_values)}")
    elif insert_sql_tpl is None:
        result_sql = column_names_insert_text
    else:
        raise TypeError("data_vector_to_sql_insert: insert_sql_tpl must be a string or None")

    return tuple(result_items), result_sql


def generate_random_token(length: int = 16) -> str:
    """Generates a random token of the specified length from string.ascii_letters and string.digits"""

    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def parse_dict_into_object(dict_obj: dict, obj: object, strict_attributes: bool = True,
                           add_attributes: bool = False) -> None:
    """
    Pastes dict contents into an object

    strict_attributes=true
        requires all keys in the source dict to have corresponding attributes in the target object; raises an
        exception if not
    add_attributes=true
        creates attributes in the target object for given dict keys if they are not present yet
    """

    # if (result_row is None) or (not isinstance(result_row, tuple)):
    #     raise Exception("parse_row_into_object: result_row is None or not a list")

    for key in dict_obj:
        if not hasattr(obj, key) and strict_attributes:
            raise Exception("parse_row_into_object: object does not have attribute: " + key)
        if not hasattr(obj, key) and not add_attributes:
            continue
        setattr(obj, key, dict_obj[key])


parse_row_into_object = parse_dict_into_object  # added for legacy compatibility after function name change


class AfgBaseMixin:
    """
    Base class for all AFG objects; restricts operations on private and callabe attributes.

    __str__ ommits private and callable attributes

    __setattr__ prevents modification of callable attributes at runtime

    __iter__ allows for dict() conversion; returns only non-private and non-callable attributes
    """

    def __str__(self) -> str:
        result_dict = {}

        for b in dir(self):
            if not b.startswith("_") and not callable(getattr(self, b)):
                result_dict[b] = getattr(self, b)

        return str(result_dict)

    def __setattr__(self, key, value) -> None:
        if callable(getattr(self, key, None)):
            # callable attributes cannot be set/overloaded at runtime
            raise AttributeError("%r modification of callable attribute is not allowed: %s" % (self, key))
        super().__setattr__(key, value)

    def __iter__(self) -> Any:
        for b in dir(self):
            if not b.startswith("_") and not callable(getattr(self, b)):
                yield b, getattr(self, b)


class AfgBaseObject(AfgBaseMixin):
    """
    Base class for all AFG objects; restricts operations on private and callabe attributes.
    """

afg_base_object_class=AfgBaseObject  # added for legacy compatibility after class name change


class AfgFreezableMixin:
    """
    Attributes modification, addition, deletion is restricted ("freezed") after object instantiation;
    mix-in class not to be instantiated.

    self.set_frozen_attrib()
        modifies/adds an attribute to the object

    self.del_frozen_attrib()
        removes an attribute from the object
    """

    __isfrozen = False

    def __init__(self) -> None:
        self._freeze()  # prevent adding new or altering existing attributes to the object after initialisation
        super().__init__()

    def __setattr__(self, key, value) -> None:
        if self.__isfrozen and (key[-10:] != "__isfrozen"):  # and not hasattr(self, key):
            raise TypeError("%r is a frozen class" % self)
        super().__setattr__(key, value)

    def __delattr__(self, item) -> None:
        if self.__isfrozen:
            raise TypeError("%r is a frozen class" % self)
        super().__delattr__(item)

    def _freeze(self) -> None:
        self.__isfrozen = True

    def _unfreeze(self) -> None:
        self.__isfrozen = False

    def set_frozen_attrib(self, key: str, value: any) -> None:
        self._unfreeze()
        setattr(self, key, value)
        self._freeze()

    def del_frozen_attrib(self, key: str) -> None:
        self._unfreeze()
        delattr(self, key)
        self._freeze()


class AfgFreezableObject(AfgFreezableMixin, AfgBaseObject):
    """
    Extends AfgBaseObject with AfgFreezableMixin:

    * restricts operations on private and callabe attributes

    * attributes modification, addition, deletion is restricted ("freezed") after object instantiation
    """


afg_freezable_object_class=AfgFreezableObject  # added for legacy compatibility after class name change


class AfgQueryResultMixin:
    """
    Executes a query via DB.execute() and pastes the resulting row (fetch='one') into the object attributes at
    instantiation; mix-in class not to be instantiated.

    self.__init__(self, db_cursor: pyodbc.Cursor = None, query_text: str = None, query_params: tuple = None,
    strict_attributes: bool = True, add_attributes: bool = False) -> None

    strict_attributes=true
        requires all keys in the source dict to have corresponding attributes in the target object; raises an
        exception if not

    add_attributes=true
        creates attributes in the instantiated object for given dict keys if they are not present yet
    """

    def __init__(self, db_cursor: pyodbc.Cursor, query_text: str, query_params: tuple = None,
                 strict_attributes: bool = True, add_attributes: bool = False) -> None:
        if not isinstance(db_cursor, pyodbc.Cursor):
            raise TypeError("%r db_cursor is not a pyodbc.Cursor" % self)
        if (type(query_text) is not str) or isnullorempty(query_text):
            raise TypeError("%r query_text is not a string or is empty" % self)
        if query_params is not None and type(query_params) is not tuple:
            raise TypeError("%r query_params is not a tuple" % self)

        result_row = DB.execute(db_cursor, query_text, parameters=query_params, fetch='one')

        if result_row is not None:
            parse_row_into_object(result_row, self, strict_attributes, add_attributes)

        super().__init__()


class AfgQueryResult(AfgQueryResultMixin, AfgFreezableObject):
    """
    Extends AfgFreezableObject with AfgQueryResultMixin:

    * restricts operations on private and callabe attributes

    * attributes modification, addition, deletion is restricted ("freezed") after object instantiation
    
    * executes a query via DB.execute() and pastes the resulting row (fetch='one') into the object
    attributes at instantiation

    self.__init__(self, db_cursor: pyodbc.Cursor = None, query_text: str = None, query_params: tuple = None,
    strict_attributes: bool = True, add_attributes: bool = False) -> None

    strict_attributes=true
        requires all keys in the source dict to have corresponding attributes in the target object; raises an
        exception if not

    add_attributes=true
        creates attributes in the instantiated object for given dict keys if they are not present yet
    """


query_result_class=AfgQueryResult  # added for legacy compatibility after class name change
