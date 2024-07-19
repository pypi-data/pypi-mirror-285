"""
:authors: KiryxaTech
:license Apache License, Version 2.0, see LICENSE file

:copyright: (c) 2024 KiryxaTech
"""
import json
from typing import Any, Union, Dict, List, Optional, overload
from pathlib import Path


class JsonFile:
    def __init__(self,
                 file_path: Union[str, Path],
                 encoding: Optional[str] = "utf-8",
                 indent: Optional[int] = 4,
                 ignore_errors: Optional[List[Exception]] = None):
        
        self._file_path = Path(file_path)
        self._encoding = encoding
        self._indent = indent

        self.create_if_not_exists()

    @property
    def file_path(self):
        return self._file_path

    @property
    def exists(self) -> bool:
        return self._file_path.exists()

    def create(self):
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        self._file_path.touch()

    def create_if_not_exists(self):
        if not self._file_path.exists():
            self.create()

    def clear(self):
        self.write({})

    def delete(self):
        self._file_path.unlink(missing_ok=True)

    def write(self, data: Dict):
        with self._file_path.open('w', encoding=self._encoding) as f:
            json.dump(data, f, indent=self._indent)

    def read(self) -> Dict:
        with self._file_path.open('r', encoding=self._encoding) as f:
            return json.load(f)

    @overload
    def set_value(self, key: str, value) -> None: ...

    @overload
    def set_value(self, keys: List[str], value) -> None: ...

    def set_value(self, keys_path: Union[List[str], str], value: Any) -> None:
        keys_path = [keys_path] if isinstance(keys_path, str) else keys_path
        data = self.read()

        def recursive_set(keys, data, value):
            key = keys[0]
            if len(keys) == 1:
                data[key] = value
            else:
                if key not in data or not isinstance(data[key], dict):
                    data[key] = {}
                recursive_set(keys[1:], data[key], value)

        recursive_set(keys_path, data, value)
        self.write(data)
    
    @overload
    def get_value(self, key: str) -> Any: ...

    @overload
    def get_value(self, keys: List[str]) -> Any: ...

    def get_value(self, keys_path: Union[List[str], str]) -> Any:
        keys_path = [keys_path] if isinstance(keys_path, str) else keys_path
        data = self.read()

        for key in keys_path:
            if key in data and isinstance(data, dict):
                data = data[key]
            else:
                raise KeyError(f"Key '{key}' not found or is not a dictionary.")
                
        return data

    @overload
    def remove_key(self, key: str) -> None: ...

    @overload
    def remove_key(self, keys: List[str]) -> None: ...

    def remove_key(self, keys_path: Union[List[str], str]):
        keys_path = [keys_path] if isinstance(keys_path, str) else keys_path
        data = self.read()

        for key in keys_path[:-1]:
            if key in data and isinstance(data[key], dict):
                data = data[key]
            else:
                raise KeyError(f"Key '{key}' not found or is not a dictionary.")
            
        if keys_path[-1] in data:
            del data[keys_path[-1]]
        else:
            raise KeyError(f"Key '{keys_path[-1]}' not found.")

        self.write(data)

    @overload
    @classmethod
    def select(self, file: 'JsonFile', range_: range) ->  Dict[str, Any]: ...

    @overload
    @classmethod
    def select(self, dict_: Dict[str, Any], range_: range) -> Dict[str, Any]: ... 

    @classmethod
    def select(cls,
               file_or_dict: Union['JsonFile', Dict[str, Any]],
               range_: range
               ) -> Dict[str, Any]:
        
        data = cls._get_data(file_or_dict)

        for i in range_:
            for key, value in data.items():
                if i == data[key]:
                    data[key] = value

        return data
    
    @overload
    @classmethod
    def union(cls, dict_1: Dict[str, Any], dict_2: Dict[str, Any]) -> Dict[str, Any]: ...

    @overload
    @classmethod
    def union(cls, file_1: 'JsonFile', file_2: 'JsonFile') -> Dict[str, Any]: ...

    @overload
    @classmethod
    def union(cls, dict: Dict[str, Any], file: 'JsonFile') -> Dict[str, Any]: ...

    @overload
    @classmethod
    def union(cls, file: 'JsonFile', dict: Dict[str, Any]) -> Dict[str, Any]: ...

    @classmethod
    def union(cls,
              file_or_dict_1: Union['JsonFile', Dict[str, Any]],
              file_or_dict_2: Union['JsonFile', Dict[str, Any]],
              ) -> Dict[str, Any]:
        
        data_1 = cls._get_data(file_or_dict_1)
        data_2 = cls._get_data(file_or_dict_2)

        return data_1 | data_2
    
    @overload
    @classmethod
    def intersect(cls, dict_1: Dict[str, Any], dict_2: Dict[str, Any]) -> Dict[str, Any]: ...

    @overload
    @classmethod
    def intersect(cls, file_1: 'JsonFile', file_2: 'JsonFile') -> Dict[str, Any]: ...

    @overload
    @classmethod
    def intersect(cls, dict: Dict[str, Any], file: 'JsonFile') -> Dict[str, Any]: ...

    @overload
    @classmethod
    def intersect(cls, file: 'JsonFile', dict: Dict[str, Any]) -> Dict[str, Any]: ...

    @classmethod
    def intersect(cls,
                  file_or_dict_1: Union['JsonFile', Dict[str, Any]],
                  file_or_dict_2: Union['JsonFile', Dict[str, Any]],
                  ) -> Dict[str, Any]:
        
        data_1 = cls._get_data(file_or_dict_1)
        data_2 = cls._get_data(file_or_dict_2)

        return dict(data_1.items() & data_2.items())

    @classmethod
    def _get_data(cls, file_or_dict: Union['JsonFile', Dict[str, Any]]) -> Dict[str, Any]:
        if isinstance(file_or_dict, JsonFile):
            return file_or_dict.read()
        elif isinstance(file_or_dict, Dict):
            return file_or_dict
        else:
            raise TypeError("file_or_dict must be an instance of 'JsonFile' or a dictionary.")