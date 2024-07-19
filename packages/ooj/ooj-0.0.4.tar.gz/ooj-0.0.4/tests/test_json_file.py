import os
import pytest
from pathlib import Path
from ooj.json_file import JsonFile

# Base path from test JSON files
BASE_PATH = Path('tests/files/test_json_files')


class TestJsonFile:
    @pytest.mark.parametrize(
        "file_path",
        [
            BASE_PATH / "created_file.json",
            BASE_PATH / "not_created_file.json"
        ]
    )
    def test_create_if_not_exists(self, file_path):
        JsonFile(file_path)

        assert file_path.exists()

    @pytest.mark.parametrize(
        "keys_path, value",
        [
            ("key_1", "value_1"),
            (["key_2", "nested_key_2"], "value"),
            ("new_key", "value")
        ]
    )
    def test_set_and_get_value(self, keys_path, value):
        file = JsonFile(BASE_PATH / "set_and_get_value.json")
        file.set_value(keys_path, value)
        assert file.get_value(keys_path) == value

    @pytest.mark.parametrize(
        "keys_path",
        [
            "key",
            ["keys", "nested_key"]
        ]
    )
    def test_remove_key(self, keys_path):
        file = JsonFile(BASE_PATH / "remove_key.json")
        file.set_value(keys_path, "dummy_value")
        file.remove_key(keys_path)
        with pytest.raises(KeyError):
            file.get_value(keys_path)

    @pytest.mark.parametrize(
        "keys_path",
        [
            "key",
            ["keys", "nested_key"]
        ]
    )
    def test_remove_key(self, keys_path):
        file = JsonFile(BASE_PATH / "remove_key.json")
        file.set_value(keys_path, "dummy_value")
        file.remove_key(keys_path)
        with pytest.raises(KeyError):
            file.get_value(keys_path)

    @pytest.mark.parametrize(
        "file_or_dict, range_",
        [
            (JsonFile(BASE_PATH / 'select.json'), range(0, 10)),
            (
                {"key1": 0, "key2": 12, "key3": -8,
                "key4": 4, "key5": 2, "key6": -5,
                "key7": -3, "key8": 7, "key9": -84,
                "key10": 9},
                range(-10, 0)
            )
        ]
    )
    def test_select(self, file_or_dict, range_):
        data = JsonFile.select(file_or_dict, range_)

        keys = []
        if isinstance(data, JsonFile):
            for key, value in data.read().items():
                if value in range_:
                    keys.append(key)

            assert data.read()[keys[0]] in range_

        elif isinstance(data, dict):
            for key, value in data.items():
                if value in range_:
                    keys.append(key)

            assert data[keys[0]] in range_

    @pytest.mark.parametrize(
        "file_or_dict_1, file_or_dict_2, expected_result",
        [
            # Test union JsonFiles
            (
                JsonFile(BASE_PATH / "union/union_1.json"),
                JsonFile(BASE_PATH / "union/union_2.json"),

                JsonFile(BASE_PATH / "union/union_1.json").read() |\
                JsonFile(BASE_PATH / "union/union_2.json").read()
            ),
            # Test union JsonFile & dict 
            (
                JsonFile(BASE_PATH / "union/union_1.json"),
                {"key_1": "value_1", "key_3": "value_3", "key_8": "value_8"},

                JsonFile(BASE_PATH / "union/union_1.json").read() | {"key_1": "value_1", "key_3": "value_3", "key_8": "value_8"}
            ),
            # Test union dicts
            (
                {"key_1": "value_1", "key_2": "value_2", "key_3": "value_3"},
                {"key_1": "value_1", "key_3": "value_3", "key_8": "value_8"},

                {"key_1": "value_1", "key_2": "value_2", "key_3": "value_3"} |\
                {"key_1": "value_1", "key_3": "value_3", "key_8": "value_8"}
            )
        ]
    )
    def test_union(self, file_or_dict_1: JsonFile, file_or_dict_2, expected_result):
        assert JsonFile.union(file_or_dict_1, file_or_dict_2) == expected_result

    @pytest.mark.parametrize(
        "file_or_dict_1, file_or_dict_2, expected_result",
        [
            # Test intersect JsonFiles
            (
                JsonFile(BASE_PATH / "intersect/intersect_1.json"),
                JsonFile(BASE_PATH / "intersect/intersect_2.json"),

                dict(JsonFile(BASE_PATH / "intersect/intersect_1.json").read().items() &\
                JsonFile(BASE_PATH / "intersect/intersect_2.json").read().items())
                
            ),
            # Test intersect JsonFile & dict
            (
                JsonFile(BASE_PATH / "intersect/intersect_1.json"),
                {"key_1": "value_1", "key_3": "value_3", "key_8": "value_8"},

                dict(JsonFile(BASE_PATH / "intersect/intersect_1.json").read().items() &\
                    {"key_1": "value_1", "key_3": "value_3", "key_8": "value_8"}.items())
            ),
            # Test intersect dicts
            (
                {"key_1": "value_1", "key_2": "value_2", "key_3": "value_3"},
                {"key_1": "value_1", "key_3": "value_3", "key_8": "value_8"},

                dict({"key_1": "value_1", "key_2": "value_2", "key_3": "value_3"}.items() &\
                {"key_1": "value_1", "key_3": "value_3", "key_8": "value_8"}.items())
            )
        ]
    )
    def test_intersect(self, file_or_dict_1, file_or_dict_2, expected_result):
        print(JsonFile.intersect(file_or_dict_1, file_or_dict_2))
        assert JsonFile.intersect(file_or_dict_1, file_or_dict_2) == expected_result