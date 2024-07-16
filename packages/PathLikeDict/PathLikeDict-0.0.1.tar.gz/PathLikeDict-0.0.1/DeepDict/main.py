from typing import overload, Any


class DeepDict:
    def __init__(self, dict: dict):
        self.__dict = dict

    @property
    def origin(self) -> dict:
        return self.__dict

    def __str__(self) -> str:
        return str(self.__dict)

    def __truediv__(self, path: str | list) -> 'DeepDict':
        return self.path(path)

    def __getattr__(self, name: str) -> 'DeepDict':
        return self.path(name)

    def path(self, path: list | str) -> 'DeepDict':
        if isinstance(path, str):
            path = path.split('.')
        for key in path:
            if key not in self.__dict:
                self.__dict[key] = dict()
            elif key in self.__dict and not isinstance(self.__dict[key], dict):
                raise ValueError(f'{self}, {path} is not dict path')
            self.__dict = self.__dict[key]
        return DeepDict(self.__dict)

    def hook_before_set(self, value: Any) -> Any:
        return value

    @overload
    def set(self, keys: str, values: Any) -> 'DeepDict': ...

    @overload
    def set(self, keys: list, values: list) -> 'DeepDict': ...

    def set(self, keys: list, values: list | Any) -> 'DeepDict':
        if isinstance(values, list):
            values = list(map(self.hook_before_set, values))
        else:
            values = self.hook_before_set(values)
        if isinstance(keys, str):
            self.__dict[keys] = values
            return self
        if len(keys) != len(values):
            raise ValueError('keys and values must have same length')
        for key, value in zip(keys, values):
            if not value:
                continue
            self.__dict[key] = value
        return self

    def alist(self, list_property: str) -> list:
        if list_property not in self.__dict:
            self.__dict[list_property] = []
        return self.__dict[list_property]


if __name__ == '__main__':
    adict = {}
    bdict = DeepDict(adict).path('a.b.c').set('d', 1).path(['e', 'f']).set('g', 2)
    print(adict)
    print(bdict)
    # {'a': {'b': {'c': {'d': 1, 'e': {'f': {'g': 2}}}}}}
    # {'g': 2}

    bdict.path('wow').set(['a', 'b', 'c'], [3, 4, 5])
    print(adict)
    print(bdict)
    # {'a': {'b': {'c': {'d': 1, 'e': {'f': {'g': 2, 'wow': {'a': 3, 'b': 4, 'c': 5}}}}}}}       
    # {'a': 3, 'b': 4, 'c': 5}
