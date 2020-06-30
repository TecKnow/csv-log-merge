import os
from pathlib import Path

import pytest

from csvlog.csv_merge import get_csv_paths_in_directory


class TestCSVMerge:
    def test_get_csv_paths_in_directory_defaults(self, csv_paths_temp_dir):
        res = set(p.stem for p in get_csv_paths_in_directory(Path.cwd()))
        assert res == set("one two three ignore".split())

    def test_get_csv_paths_in_directory_not_in_cwd(self, csv_paths_temp_dir):
        outside_dir = Path(csv_paths_temp_dir, "other_dir")
        outside_dir.mkdir()
        os.chdir(outside_dir)
        res = set(p.stem for p in get_csv_paths_in_directory(csv_paths_temp_dir))
        assert res == set("one two three ignore".split())

    def test_get_csv_paths_in_directory_defaults_recursive(self, csv_paths_temp_dir):
        res = set(p.stem for p in get_csv_paths_in_directory(Path.cwd(), recurse=True))
        assert res == set("one two three four five ignore".split())

    def test_get_csv_paths_in_directory_recursive_not_in_cwd(self, csv_paths_temp_dir):
        outside_dir = Path(csv_paths_temp_dir, "other_dir")
        outside_dir.mkdir()
        os.chdir(outside_dir)
        res = set(p.stem for p in get_csv_paths_in_directory(csv_paths_temp_dir, recurse=True))
        assert res == set("one two three four five ignore".split())

    def test_get_csv_paths_in_directory_with_ignore(self, csv_paths_temp_dir):
        res = set(p.stem for p in get_csv_paths_in_directory(Path.cwd(), ignore=Path(csv_paths_temp_dir, "ignore.csv")))
        assert res == set("one two three".split())

    def test_get_csv_paths_in_directory_with_ignore_recursive(self, csv_paths_temp_dir):
        res = set(p.stem for p in
                  get_csv_paths_in_directory(Path.cwd(), recurse=True, ignore=Path(csv_paths_temp_dir, "ignore.csv")))
        assert res == set("one two three four five".split())


@pytest.fixture
def csv_paths_temp_dir(tmp_path):
    previous_cwd = Path.cwd()
    # noinspection PyTypeChecker
    os.chdir(tmp_path)
    Path(tmp_path, "one.csv").touch()
    Path(tmp_path, "two.csv").touch()
    Path(tmp_path, "three.csv").touch()
    Path(tmp_path, "ignore.csv").touch()
    dir_path = Path(tmp_path, "directory.csv")
    dir_path.mkdir()
    Path(dir_path, "four.csv").touch()
    Path(dir_path, "five.csv").touch()
    yield tmp_path
    # noinspection PyTypeChecker
    os.chdir(previous_cwd)


if __name__ == '__main__':
    pytest.main()
