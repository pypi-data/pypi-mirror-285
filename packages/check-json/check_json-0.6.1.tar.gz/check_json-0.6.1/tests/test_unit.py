"""
Unit tests for check_json
"""
import os
import tempfile

import nagiosplugin  # type:ignore
import pytest  # type:ignore

import check_json.__main__ as check_json  # type:ignore

# pylint: disable=redefined-outer-name
# pylint: disable=too-few-public-methods


def test_file_to_string():
    """Test"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tfile:
        test_string = "This is a string\nand another string"
        filename = tfile.name
        tfile.write(test_string)
    file_contents = check_json.file_to_string(tfile.name)
    os.remove(filename)
    assert file_contents == test_string


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("w@10:20,c@21:30", check_json.Thresholds("@10:20", "@21:30")),
        ("w10,c20", check_json.Thresholds("10", "20")),
        ("w~:10,c~:20", check_json.Thresholds("~:10", "~:20")),
        ("w10:,c20", check_json.Thresholds("10:", "20")),
        ("c1:", check_json.Thresholds(None, "1:")),
        ("w~:0,c10", check_json.Thresholds("~:0", "10")),
        ("c5:6", check_json.Thresholds(None, "5:6")),
        ("c@10:20", check_json.Thresholds(None, "@10:20")),
    ],
)
def test_thresholds_parse(test_input, expected):
    """Test"""

    assert check_json.thresholds_parse(test_input) == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (
            # One filter
            [
                "--filter",
                "LABEL",
                "FILTER",
                "c@0",
                "somefile.json",
            ],
            {
                "filters": [
                    [
                        "LABEL",
                        "FILTER",
                        "c@0",
                    ],
                ],
                "jsonsrc": "somefile.json",
                "verbosity": 0,
            },
        ),
        (
            # Or multiple filters
            [
                "--filter",
                "LABEL1",
                "FILTER1",
                "w@5:9,c@10:20",
                "--filter",
                "LABEL2",
                "FILTER2",
                "w@5:9,c@10:20",
                "somefile.json",
            ],
            {
                "filters": [
                    [
                        "LABEL1",
                        "FILTER1",
                        "w@5:9,c@10:20",
                    ],
                    [
                        "LABEL2",
                        "FILTER2",
                        "w@5:9,c@10:20",
                    ],
                ],
                "jsonsrc": "somefile.json",
                "verbosity": 0,
            },
        ),
    ],
)
def test_parse_args(test_input, expected):
    """Test"""
    assert vars(check_json.parse_args(test_input)) == expected


def test_parse_args_fail():
    """Test"""
    argv = [
        "--filter",
    ]
    with pytest.raises(SystemExit):
        check_json.parse_args(argv)

    argv = []
    with pytest.raises(SystemExit):
        check_json.parse_args(argv)

    argv = [
        "somefile.json",
    ]
    with pytest.raises(SystemExit):
        check_json.parse_args(argv)


class JsonfileManager:
    """Holds a JsonFile object and its inputs for testing"""

    def __init__(self):
        self.filters = [
            check_json.Filter(*x)
            for x in [
                ["LABEL1", ".key1", "c@0"],
                ["LABEL2", ".key3 ", "c@0"],
            ]
        ]
        self.jsonstr = '{"key1": "value1", "key2": 1}\n{"key1": "value2", "key2": 2}'
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as jsonfile:
            jsonfile.write(self.jsonstr)
        self.obj = check_json.JsonFile(filters=self.filters, filepath=jsonfile.name)
        jsonfile.close()


@pytest.fixture
def jsonfile_manager():
    """Create a JsonFile object and save its inputs"""
    return JsonfileManager()


class TestJsonFile:
    """Test"""

    def test_init(self, jsonfile_manager):
        """Test that the JsonFile object is constructed as expected"""
        assert jsonfile_manager.obj.json == jsonfile_manager.jsonstr
        for filt, obj_filt in zip(
            jsonfile_manager.filters, jsonfile_manager.obj.filters
        ):
            assert filt.label == obj_filt.label
            assert filt.test_filter == obj_filt.test_filter
            assert filt.thresholds == obj_filt.thresholds

    def test_probe(self, jsonfile_manager):
        """Test that probe returns all Metric objects"""
        for metric in jsonfile_manager.obj.probe():
            assert isinstance(metric, nagiosplugin.Metric)
