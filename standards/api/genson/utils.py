import operator
from copy import deepcopy
from functools import reduce
import json


SCHEMA_OBJECT_VARIABLES = ('properties', 'items')
SCHEMA_VARIABLES = ('description', 'title', 'type')
ORDER_OF_SORTING_KEYS = ('$schema', '$id', 'type', 'const', 'title', 'description', 'required', 'items', 'properties')


class NestedDict(dict):
    """
    Dictionary that can use a list to get a value

    :example:
    >>> nested_dict = NestedDict({'aggs': {'aggs': {'field_I_want': 'value_I_want'}, 'None': None}})
    >>> path = ['aggs', 'aggs', 'field_I_want']
    >>> nested_dict[path]
    'value_I_want'
    >>> nested_dict[path] = 'changed'
    >>> nested_dict[path]
    'changed'
    """
    def __getitem__(self, item):
        if isinstance(item, list):
            return self.get_traverse(item)
        return super(NestedDict, self).__getitem__(item)

    def __setitem__(self, key, value):
        if isinstance(key, list):
            for _key in key[:-1]:
                if _key not in self:
                    self[_key] = {}
                self = self[_key]
            self[key[-1]] = value
            return self
        return super(NestedDict, self).__setitem__(key, value)

    def get_traverse(self, _list):
        return reduce(operator.getitem, _list, self)

    _paths = []
    _path = []

    def find(self, key, _dict=None, _main_loop=True):
        """ Find a list of paths to a key

        :param key: str, the key you want to find
        :param _dict: used for recursive searching
        :return: list with paths
        :example:
        >>> nested_dict = NestedDict({'aggs': {'aggs': {'field_I_want': 'value_I_want'}, 'None': None}})
        >>> paths = nested_dict.find('field_I_want')
        >>> paths
        [['aggs', 'aggs', 'field_I_want']]
        >>> nested_dict[paths[0]] = 'changed'
        >>> nested_dict[paths[0]]
        'changed'
        """
        if _main_loop:
            self._path, self._paths = [], []
            _dict = self

        for _key in _dict.keys():
            self._path.append(_key)

            if _key == key:
                self._paths.append(deepcopy(self._path))

            if isinstance(_dict[_key], dict):
                self.find(key, _dict[_key], _main_loop=False)

            self._path.pop()

        if _main_loop:
            return self._paths


def schema_path_id_generator(json_schema: json, nested_dict: NestedDict, id_path=[]):
    for key, value in json_schema.items():
        if isinstance(value, dict):
            id_path.append(key)
            if key != 'properties':
                nested_dict[id_path].update({'$id': f'#/{"/".join(id_path)}'})
            if all(not isinstance(item, dict) for item in value.values()):
                id_path.pop()
            schema_path_id_generator(value, nested_dict)
        if key in SCHEMA_OBJECT_VARIABLES:
            id_path.pop(-1)
        if id_path:
            if key not in SCHEMA_VARIABLES and id_path[-1] not in SCHEMA_OBJECT_VARIABLES:
                id_path.pop(-1)


def schema_sorted_first_level(data: dict) -> dict:
    result = dict(sorted(data.items(), key=lambda pair: ORDER_OF_SORTING_KEYS.index(pair[0])))
    return result


def sorted_nested_dict(data: dict):
    result = {}
    for k, v in data.items():
        if isinstance(v, dict):
            if k != 'properties':
                v = dict(sorted(v.items(), key=lambda pair: ORDER_OF_SORTING_KEYS.index(pair[0])))
                bb = 1
            result[k] = sorted_nested_dict(v)
        else:
            result[k] = v
    return result
