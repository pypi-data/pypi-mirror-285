<div align="center">
    <picture>
        <source media="(prefers-color-scheme: dark)" srcset="doc/images/libDarkImage.png">
        <img src="./doc/images/libLightImage.png">
    </picture>

![PyPI](https://img.shields.io/pypi/v/ooj)
![PyPI - Downloads](https://img.shields.io/pypi/dm/ooj?color=green&label=downloads)
![Downloads last 6 month](https://static.pepy.tech/personalized-badge/ooj?period=total&units=international_system&left_color=grey&right_color=green&left_text=downloads%20last%206%20month)
![PyPI - License](https://img.shields.io/badge/license-Apache2.0-blue)
</div>

---

The `OOJ` library is a Python package that simplifies working with JSON files. It provides methods to read, write, add, remove, and replace elements in a JSON file.

## Installation

You can install the `OOJ` library directly from PyPI:

### On Windows:
```bash
pip install ooj
```

### On Linux/MacOS:
```bash
pip3 install ooj
```

## Usage
### Import library
```python
import ooj
```

### Working with JsonFile
#### Creating a JsonFile object
Create a `JsonFile` object:
```python
my_file = ooj.JsonFile('your/path/to/file.json')
```

#### Read and write
Read or write:
```python
data = {
 "name": "Jane",
 "age": 22,
 "is_happy": True
}

my_file.write(data)

print(my_file.read())

PS:
>>> {
>>>     "name": "Jane",
>>>     "age": 22,
>>>     "is_happy": True
>>> }
```

#### Sampling
```python
data = {
 "1": -7,
 "2": 3,
 "3": 9
}

my_file.write(data)
selected_keys_dict = my_file.select(range(0, 10))
print(selected_keys_dict)

PS:
>>> {"2": 3, "3": 9}
```

### Create serialization
You can serialize and deserialize objects.
#### Creating a serializer
```python
from ooj import JsonSerializer
from ooj.excptions import NotSerializableError

# Options for serialization
options = {
    "indent": 4,
    "ignore_errors": NotSerializableError
}

serializer = JsonSerializer(options=options)
```

#### Serialize the object
```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

serialized_person = serializer.serialize(Person("Mike", 29))
print(serialized_person)

PS:
>>> {
>>>     'name': 'Mike',
>>>     'age': 29
>>> }
```