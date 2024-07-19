import json
from typing import Any, List, Dict, Union, overload
try:
    from typing import Literal
except:
    from typing_extensions import Literal

from .exceptions.exceptions import NotSerializableException, CyclicFieldError

from .json_file import JsonFile


HANDLE_CYCLES = Literal["error", "ignore", "replace"]


class JsonSerializer:
    """A class for serializing and deserializing objects."""

    def __init__(self, options: dict = None):
        """
        Initializing serialization settings.

        Parameters:
        - options (dict): Optional dictionary with settings.
        """

        self._options: Dict[str, Any] = options if options else {}

        self._encoding: str = self._options.get("encoding", "utf-8")
        self._ignore_errors: List[Exception] = self._options.get("ignore_errors", [])
        self._transform_rules: Dict[str, Any] = self._options.get("transform_rules", {})
        self._indent: int = self._options.get("indent", None)
        self._include_fields: List[Dict[str, Any]] = self._options.get("include_fields", [])
        self._exclude_fields: List[Dict[str, Any]] = self._options.get("exclude_fields", [])
        self._handle_cycles: HANDLE_CYCLES = self._options.get("handle_cycles", "error")
    
    def serialize(self, obj: object) -> str:
        """
        Converting an object to a JSON string.

        Parameters:
        - obj (object): Serializable object.

        Returns:
        - str: Serialized JSON string.
        """
        if self.is_serializable(obj):
            obj = self._include_fields_to_obj(obj)
            obj = self._apply_transform_rules(obj)
            obj = self._exclude_fields_to_obj(obj)
            obj = self._handling_cycling_fields(obj)

            return json.dumps(obj.__dict__, indent=self._indent)
        
        self._handle_error(NotSerializableException)
    
    def deserialize(self, json_str: str, cls: type) -> object:
        """
        Converts a JSON string into an object of the specified class.

        Parameters:
        - json_str (str): JSON string.
        - cls (type): Target class type.

        Returns:
        - object: Deserialized object.
        """
        if self.is_serializable(cls):
            data = json.loads(json_str)

            obj = cls.__new__(cls)
            for name, value in data.items():
                setattr(obj, name, value)

            return obj
        
        self._handle_error(NotSerializableException)
    
    @overload
    def serealize_to_file(self, obj: object, file_path: str) -> None: ...

    @overload
    def serealize_to_file(self, obj: object, json_file: JsonFile) -> None: ...

    def serialize_to_file(self, obj: object, file_path_or_json_file: Union[str, JsonFile]) -> None:
        """
        Saving a JSON representation of an object to a file.

        Parameters:
        - obj (object): Serializable object.
        - file_path (str): Path to the file.
        """
        if self.is_serializable(obj):
            obj = self._include_fields_to_obj(obj)
            obj = self._exclude_fields_to_obj(obj)
            obj = self._apply_transform_rules(obj)
            obj = self._handling_cycling_fields(obj)

            if isinstance(file_path_or_json_file, str):
                with open(file_path_or_json_file, 'w', encoding=self._encoding) as json_file:
                    json.dump(obj.__dict__, json_file, indent=self._indent)
            elif isinstance(file_path_or_json_file, JsonFile):
                file_path_or_json_file.write(obj.__dict__)
        else:
            self._handle_error(NotSerializableException)

    def deserialize_from_file(self, file_path_or_json_file: Union[str, JsonFile], cls: type) -> object:
        """
        Loading an object from a JSON file.

        Parameters:
        - file_path (str): Path to the file.
        - cls (type): Target class type.

        Returns:
        - object: Deserialized object.
        """
        if self.is_serializable(cls):
            if isinstance(file_path_or_json_file, str):
                with open(file_path_or_json_file, 'r', encoding=self._encoding) as serealize_data_file:
                    data = json.load(serealize_data_file)
            elif isinstance(file_path_or_json_file, JsonFile):
                data = file_path_or_json_file.read()

            obj = cls.__new__(cls)
            for name, value in data.items():
                setattr(obj, name, value)

            return obj
        
        self._handle_error(NotSerializableException)
    
    def is_serializable(self, obj: object) -> bool:
        """
        Checking if an object can be serialized.

        Parameters:
        - obj (object): Object to check.

        Returns:
        - bool: True if the object is serializable, False otherwise.
        """
        return hasattr(obj, '__dict__')

    def get_serialization_options(self) -> dict:
        """
        Getting current serialization and deserialization options.

        Returns:
        - dict: Dictionary of options.
        """
        return self._options
    
    def _handle_error(self, error: Exception):
        """
        Handling and logging errors that occur during serialization and deserialization.

        Parameters:
        - error (Exception): Error to be handled.
        """
        if error not in self._ignore_errors:
            raise error
        
    def _handling_cycling_fields(self, obj: object) -> object:
        if self._handle_cycles == "ignore": return

        if self.is_serializable(obj):
            data = obj.__dict__
        else:
            self._handle_error(NotSerializableException)

        for key, _ in data.items():
            if isinstance(key, dict):
                match self._handle_cycles:
                    case "error":
                        self._handle_error(CyclicFieldError)
                    case "replace":
                        obj.__dict__[key] = None

        return obj
    
    def _include_fields_to_obj(self, obj: object) -> object:
        """
        Include fields for an object and returns it.

        Parameters:
        - obj (object): Serializable object.

        Returns:
        - object: Serialized object with included fields.
        """
        for field in self._include_fields:
                for name, value in field.items():
                    setattr(obj, name, value)

        return obj
    
    def _exclude_fields_to_obj(self, obj: object) -> object:
        """
        Excludes fields for an object and returns it.

        Parameters:
        - obj (object): Serializable object.

        Returns:
        - object: Serialized object with excluded fields.
        """
        for field in self._exclude_fields:
                for name, _ in field.items():
                    delattr(obj, name)

        return obj
    
    def _apply_transform_rules(self, obj: object) -> object:
        if self.is_serializable(obj):

            for key, value in obj.__dict__.items():
                obj.__dict__[key] = self._transform_rules.get(key, value)

                return obj
        
        self._handle_error(NotSerializableException)