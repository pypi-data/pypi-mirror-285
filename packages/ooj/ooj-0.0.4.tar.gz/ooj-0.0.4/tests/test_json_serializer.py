import pytest
import json

from ooj import exceptions
from ooj.json_serializer import JsonSerializer


class Person:
    def __init__(self, name: str, age: int = None):
        self.name = name
        self.age = age


standard_serializer = JsonSerializer()

person_1 = Person("Mike", 29)
person_2 = Person("Jenny")
serialize_person_1 = standard_serializer.serialize(person_1)
serialize_person_2 = standard_serializer.serialize(person_2)

serialize_file_path = 'tests\\files\\serialize_obj.json'


def to_format(obj_str: str):
    return obj_str.replace("'", '"').replace("None", "null")

@pytest.mark.parametrize("options",
                         [{},
                          {"encoding": "utf-16le"},
                          {"ignore_errors": exceptions.NotSerializableException}])
def test_create_serializer(options: dict):
    assert JsonSerializer(options).get_serialization_options() == options


@pytest.mark.parametrize("obj", [person_1, person_2])
def test_standard_serialize(obj: object):
    serialize_str = standard_serializer.serialize(obj)
    str_obj = to_format(str(obj.__dict__))

    assert serialize_str == str_obj


@pytest.mark.parametrize("json_str, cls", [(serialize_person_1, Person),
                                           (serialize_person_2, Person)])
def test_standard_deserialize(json_str, cls):
    deserialize_obj = standard_serializer.deserialize(json_str, cls)

    assert isinstance(deserialize_obj, cls)


@pytest.mark.parametrize("obj", [person_1, person_2])
def test_serialize_to_file(obj: object):
    serialize_str = standard_serializer.serialize(obj)

    standard_serializer.serialize_to_file(obj, 'tests\\files\\serialize_obj.json')

    with open(serialize_file_path, 'r') as file:
        serialize = str(json.load(file))

    assert to_format(serialize) == serialize_str


@pytest.mark.parametrize("cls", [Person])
def test_deserialize_from_file(cls: type):
    deserialize_obj = standard_serializer\
        .deserialize_from_file(serialize_file_path, cls)
    
    assert isinstance(deserialize_obj, cls)