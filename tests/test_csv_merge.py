import csv
import os
from io import StringIO
from pathlib import Path
from typing import Iterator, Sequence, Tuple

import pytest

from csvlog.csv_merge import get_csv_paths_in_directory, log_record_combiner


class TestGetCSVPathsInDirectory:
    def test_defaults(self, csv_paths_temp_dir):
        res = set(p.stem for p in get_csv_paths_in_directory(Path.cwd()))
        assert Path.cwd().samefile(csv_paths_temp_dir)
        assert res == set("one two three ignore".split())

    def test_not_in_cwd(self, csv_paths_temp_dir):
        outside_dir = Path(csv_paths_temp_dir, "other_dir")
        outside_dir.mkdir()
        os.chdir(outside_dir)
        res = set(p.stem for p in get_csv_paths_in_directory(csv_paths_temp_dir))
        assert res == set("one two three ignore".split())

    def test_defaults_recursive(self, csv_paths_temp_dir):
        res = set(p.stem for p in get_csv_paths_in_directory(csv_paths_temp_dir, recurse=True))
        assert res == set("one two three four five ignore".split())

    def test_recursive_not_in_cwd(self, csv_paths_temp_dir):
        outside_dir = Path(csv_paths_temp_dir, "other_dir")
        outside_dir.mkdir()
        os.chdir(outside_dir)
        res = set(p.stem for p in get_csv_paths_in_directory(csv_paths_temp_dir, recurse=True))
        assert res == set("one two three four five ignore".split())

    def test_with_ignore(self, csv_paths_temp_dir):
        res = set(p.stem for p in get_csv_paths_in_directory(Path.cwd(), ignore=Path(csv_paths_temp_dir, "ignore.csv")))
        assert res == set("one two three".split())

    def test_ignore_recursive(self, csv_paths_temp_dir):
        res = set(p.stem for p in
                  get_csv_paths_in_directory(Path.cwd(), recurse=True, ignore=Path(csv_paths_temp_dir, "ignore.csv")))
        assert res == set("one two three four five".split())


class TestMoveFilesToArchive:
    pass


class TestLogRecordCombiner:
    def test_no_header(self):
        readers, writer, stream = self.csv_object_setup((NAME_ROWS, PLACES_ROWS))
        function_returns = tuple(log_record_combiner(writer, reader) for reader in readers)
        assert function_returns == (True, True)
        assert tuple(csv.reader(stream.getvalue().splitlines())) == (*NAME_LIST, *PLACES_LIST)

    def test_correct_headers(self):
        names_with_headers = [HEADER_ROW] + NAME_ROWS
        places_with_headers = [HEADER_ROW] + PLACES_ROWS
        expected_results = (*NAME_LIST, *PLACES_LIST)
        readers, writer, stream = self.csv_object_setup((names_with_headers, places_with_headers))
        function_returns = tuple(log_record_combiner(writer, reader, HEADER_LIST) for reader in readers)
        assert function_returns == (True, True)
        assert tuple(csv.reader(stream.getvalue().splitlines())) == expected_results

    def test_partial_incorrect_headers(self):
        names_with_headers = [HEADER_ROW] + NAME_ROWS
        places_with_bad_headers = [BAD_HEADER_ROW] + PLACES_ROWS
        expected_results = (*NAME_LIST,)
        readers, writer, stream = self.csv_object_setup((names_with_headers, places_with_bad_headers))
        function_returns = tuple(log_record_combiner(writer, reader, HEADER_LIST) for reader in readers)
        assert function_returns == (True, False)
        assert tuple(csv.reader(stream.getvalue().splitlines())) == expected_results

    def test_total_incorrect_headers(self):
        names_with_bad_headers = [BAD_HEADER_ROW] + NAME_ROWS
        places_with_bad_headers = [BAD_HEADER_ROW] + PLACES_ROWS
        expected_results = tuple()
        readers, writer, stream = self.csv_object_setup((names_with_bad_headers, places_with_bad_headers))
        function_returns = tuple(log_record_combiner(writer, reader, HEADER_LIST) for reader in readers)
        assert function_returns == (False, False)
        assert tuple(csv.reader(stream.getvalue().splitlines())) == expected_results

    @staticmethod
    def csv_object_setup(data_sets: Iterator[Sequence[str]]) -> Tuple[Iterator[csv.reader], csv.writer, StringIO]:
        readers = (csv.reader(data) for data in data_sets)
        stream = StringIO()
        writer = csv.writer(stream)
        return readers, writer, stream


class TestLogFileCombiner:
    pass


class TestMergeLogFiles:
    pass


HEADER_LIST = "ALPHA BRAVO CHARLIE DELTA ECHO".split()
HEADER_ROW = ",".join(HEADER_LIST)
BAD_HEADER_LIST = "ALPHA, BETA, GAMMA, DELTA, EPSILON".split()
BAD_HEADER_ROW = ",".join(BAD_HEADER_LIST)
NAME_LIST = [
    "Alice Betty Christine Diana Erica".split(),
    "Adam Bob Christopher Daniel Eugene".split(),
    "Adams Bowers Cooper Davies Erickson".split()]
NAME_ROWS = [",".join(row) for row in NAME_LIST]

PLACES_LIST = [
    "Alabama Alaska Arizona Arkansas California".split(),
    "Atlanta Boston Chicago Davenport Evanston".split()]
PLACES_ROWS = [",".join(row) for row in PLACES_LIST]


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
