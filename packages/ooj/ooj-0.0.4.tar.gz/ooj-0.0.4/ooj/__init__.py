"""
:authors: KiryxaTech
:license Apache License, Version 2.0, see LICENSE file

:copyright: (c) 2024 KiryxaTech
"""


READ_MODE = 'r'
WRITE_MODE = 'w'


from .json_file import JsonFile
from .json_serializer import JsonSerializer
from .exceptions.exceptions import NotSerializableException, CyclicFieldError