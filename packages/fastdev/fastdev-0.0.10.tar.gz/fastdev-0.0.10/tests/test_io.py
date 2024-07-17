import os
import tempfile


from fastdev.io import load, dump


def test_handlers():
    test_dict = {"a": "abc", "b": 1, "c": {"d": [1, 2, 3], "e": "f"}}

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmpfile_path = os.path.join(tmp_dir, "test_fileio.json")
        dump(test_dict, tmpfile_path)
        assert test_dict == load(tmpfile_path)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmpfile_path = os.path.join(tmp_dir, "test_fileio.json")
        with open(tmpfile_path, "wb") as f:
            dump(test_dict, f, file_format="json")
        with open(tmpfile_path, "rb") as f:
            assert test_dict == load(f, file_format="json")

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmpfile_path = os.path.join(tmp_dir, "test_fileio.yaml")
        dump(test_dict, tmpfile_path)
        assert test_dict == load(tmpfile_path)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmpfile_path = os.path.join(tmp_dir, "test_fileio.yml")
        with open(tmpfile_path, "wb") as f:
            dump(test_dict, f, file_format="yml")
        with open(tmpfile_path, "rb") as f:
            assert test_dict == load(f, file_format="yaml")
