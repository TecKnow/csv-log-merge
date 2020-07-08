import csv
import os
from io import StringIO
from pathlib import Path
from typing import Iterator, Sequence, Tuple

import pytest

from csvlog.csv_merge import (get_csv_paths_in_directory, log_record_combiner, log_file_combiner, move_file_to_archive,
                              merge_log_files)


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
    def test_default_header(self, csv_merge_test_directory):
        # It's inconvenient if the sample production file is in the normal test directory structure, so it isn't.
        # This shows how to include it.
        sample_path = Path(csv_merge_test_directory, "sample.csv")
        with sample_path.open(mode="w", newline='') as sample_file:
            csv.writer(sample_file).writerows(SAMPLE_FILE_LIST)
        output_path = Path(csv_merge_test_directory, "test_out.csv")
        input_paths = get_csv_paths_in_directory(directory=csv_merge_test_directory, ignore=output_path, recurse=False)
        log_merger = log_file_combiner(output_path, header_row=True)
        merged_file_paths = log_merger(input_paths)
        assert tuple(merged_file_paths) == (Path(csv_merge_test_directory, "sample.csv"),)
        assert tuple((*csv.reader(output_path.open(newline="")),)) == SAMPLE_FILE_LIST

    def test_custom_header(self, csv_merge_test_directory):
        output_path = Path(csv_merge_test_directory, "test_out.csv")
        input_paths = get_csv_paths_in_directory(directory=csv_merge_test_directory, ignore=output_path, recurse=False)
        log_merger = log_file_combiner(output_path, header_row=HEADER_LIST)
        merged_file_paths = log_merger(input_paths)
        assert set(merged_file_paths) == {Path(csv_merge_test_directory, "names.csv"),
                                          Path(csv_merge_test_directory, "places.csv")}
        assert tuple((*csv.reader(output_path.open(newline="")),)) == tuple([HEADER_LIST] + NAME_LIST + PLACES_LIST)

    def test_no_header(self, csv_merge_test_directory):
        output_path = Path(csv_merge_test_directory, "test_out.csv")
        input_paths = get_csv_paths_in_directory(directory=csv_merge_test_directory, ignore=output_path, recurse=False)
        log_merger = log_file_combiner(output_path, header_row=None)
        merged_file_paths = log_merger(input_paths)
        assert set(merged_file_paths) == {Path(csv_merge_test_directory, "names.csv"),
                                          Path(csv_merge_test_directory, "places.csv"),
                                          Path(csv_merge_test_directory, "animals_bad_header.csv")}
        assert tuple((*csv.reader(output_path.open(newline="")),)) == tuple(
            [BAD_HEADER_LIST] + ANIMAL_LIST + [HEADER_LIST] + NAME_LIST + [HEADER_LIST] + PLACES_LIST)


class TestMoveFilesToArchive:
    def test_file_in_top_directory(self, csv_merge_test_directory):
        archive_folder_path = Path(csv_merge_test_directory, "archive")
        original_file_path = Path(csv_merge_test_directory, "names.csv")
        archive_file_path = Path(csv_merge_test_directory, "archive", "names.csv")
        assert original_file_path.exists()
        assert not archive_file_path.exists()
        move_file_to_archive(csv_merge_test_directory, archive_folder_path, original_file_path)
        assert not original_file_path.exists()
        assert archive_file_path.exists()

    def test_file_in_sub_directory(self, csv_merge_test_directory):
        archive_folder_path = Path(csv_merge_test_directory, "archive")
        original_file_path = Path(csv_merge_test_directory, "subdirectory", "food.csv")
        archive_file_path = Path(csv_merge_test_directory, "archive", "subdirectory", "food.csv")
        assert original_file_path.exists()
        assert not archive_file_path.exists()
        move_file_to_archive(csv_merge_test_directory, archive_folder_path, original_file_path)
        assert not original_file_path.exists()
        assert archive_file_path.exists()

    def test_file_exists_in_archive(self, csv_merge_test_directory):
        """Demonstrate what the program does if a file already exists in the archive.

           Right now it will stop in the middle of a run, meaning that some files may be moved and others not.
           This could be very inconvenient.  However, it is not likely to happen often, and it isn't 100% clear what
           the program should do instead."""
        archive_folder_path = Path(csv_merge_test_directory, "archive")
        original_file_path = Path(csv_merge_test_directory, "names.csv")
        archive_file_path = Path(csv_merge_test_directory, "archive", "names.csv")
        archive_file_path.touch()
        assert original_file_path.exists()
        assert archive_file_path.exists()
        with pytest.raises(FileExistsError):
            move_file_to_archive(csv_merge_test_directory, archive_folder_path, original_file_path)
        assert original_file_path.exists()
        assert archive_file_path.exists()


class TestMergeLogFiles:

    # TODO: Find some way to test the default filename algorithm.
    # Since it is clock based, a straightforward implementation might be flaky.
    # On the other hand, alternatives like monkeypatching the time are significant steps.
    def test_basic_operation(self, csv_merge_test_directory):
        output_path = Path(csv_merge_test_directory, "output.csv")
        merge_log_files(search_directory=csv_merge_test_directory, output_file_path=output_path, header_row=HEADER_LIST,
                        archive_directory=Path(csv_merge_test_directory, "archive"))
        assert tuple((*csv.reader(output_path.open(newline="")),)) == tuple([HEADER_LIST] + NAME_LIST + PLACES_LIST)
        assert not Path(csv_merge_test_directory, "names.csv").exists()
        assert not Path(csv_merge_test_directory, "places.csv").exists()
        assert Path(csv_merge_test_directory, "archive", "names.csv").exists()
        assert Path(csv_merge_test_directory, "archive", "places.csv").exists()


HEADER_LIST = "ALPHA BRAVO CHARLIE DELTA ECHO".split()
HEADER_ROW = ",".join(HEADER_LIST)
BAD_HEADER_LIST = "ALPHA BETA GAMMA DELTA EPSILON".split()
BAD_HEADER_ROW = ",".join(BAD_HEADER_LIST)
NAME_LIST = ["Alice Betty Christine Diana Erica".split(),
             "Adam Bob Christopher Daniel Eugene".split(),
             "Adams Bowers Cooper Davies Erickson".split()]
NAME_ROWS = [",".join(row) for row in NAME_LIST]

PLACES_LIST = ["Alabama Alaska Arizona Arkansas California".split(),
               "Atlanta Boston Chicago Davenport Evanston".split()]
PLACES_ROWS = [",".join(row) for row in PLACES_LIST]

FOOD_LIST = ["apples bananas cherries dates, figs".split(),
             "asparagus beets cabbage daikon edamame".split()]
FOOD_ROWS = [",".join(row) for row in FOOD_LIST]

ANIMAL_LIST = ["anteaters badgers cockatoos deer elk".split(),
               "aardvarks, beavers, cats, dog, elephants".split()]
ANIMAL_ROWS = [",".join(row) for row in ANIMAL_LIST]

SAMPLE_FILE_LIST = (['Record Type', 'Material Order', 'Job number', 'Description', '', '', '', 'Record key', '', ''],
                    ['INMB', 'yy-1234501', 'yy-12345', 'export test 6.4.2020 v1', '', '', '', '1', '', ''],
                    ['Record Type', 'Item', 'Job Number', 'Location', 'Cost Type', 'Material Number', 'Ordered Units',
                     'Record Key', 'Tax Code', 'Phase'],
                    ['INIB', '1', 'yy-12345', '', '2', '1-4DC26', '9', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '2', 'yy-12345', '', '2', '1-31239', '100', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '3', 'yy-12345', '', '2', '1-60104', '9', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '4', 'yy-12345', '', '2', '1-4CB81', '10', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '5', 'yy-12345', '', '2', '1-30621', '100', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '6', 'yy-12345', '', '2', '1-60175', '45', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '7', 'yy-12345', '', '2', '1-60174', '90', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '8', 'yy-12345', '', '2', '1-60184', '45', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '9', 'yy-12345', '', '2', '1-60151', '9', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '10', 'yy-12345', '', '2', '1-70061', '24', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '11', 'yy-12345', '', '2', '1-70219', '24', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '12', 'yy-12345', '', '2', '1-4DD26', '1', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '13', 'yy-12345', '', '2', '1-60207', '2', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '14', 'yy-12345', '', '2', '1-60263', '5', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '15', 'yy-12345', '', '2', '1-60239', '15', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '16', 'yy-12345', '', '2', '1-60225', '9', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '17', 'yy-12345', '', '2', '1-60254', '14', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '18', 'yy-12345', '', '2', '1-70020', '40', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '19', 'yy-12345', '', '2', '1-70212', '40', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '20', 'yy-12345', '', '2', '1-4DE26', '2', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '21', 'yy-12345', '', '2', '1-60208', '2', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '22', 'yy-12345', '', '2', '1-60240', '10', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '23', 'yy-12345', '', '2', '1-60226', '6', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '24', 'yy-12345', '', '2', '1-4DD26', '1', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '25', 'yy-12345', '', '2', '1-8CD23', '1', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '26', 'yy-12345', '', '2', '1-60305', '2', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '27', 'yy-12345', '', '2', '1-60343', '1', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '28', 'yy-12345', '', '2', '1-8GD53', '1', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '29', 'yy-12345', '', '2', '1-60347NT', '2', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '30', 'yy-12345', '', '2', '1-60347NB', '2', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '31', 'yy-12345', '', '2', '1-60584', '1', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '32', 'yy-12345', '', '2', '1-60351', '2', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '33', 'yy-12345', '', '2', '1-60228', '4', '1', 'WI-ADA', '01.01.01'],
                    ['INIB', '34', 'yy-12345', '', '2', '1-60154', '1', '1', 'WI-ADA', '01.01.01'])

SAMPLE_FILE_ROWS = [",".join(row) for row in SAMPLE_FILE_LIST]


@pytest.fixture
def csv_merge_test_directory(tmp_path):
    subdirectory_path = Path(tmp_path, "subdirectory")
    subdirectory_path.mkdir()
    archive_path = Path(tmp_path, "archive")
    archive_path.mkdir()
    names_path = Path(tmp_path, "names.csv")
    with names_path.open(mode='w', newline='') as names_file:
        csv.writer(names_file).writerows([HEADER_LIST] + NAME_LIST)
    places_path = Path(tmp_path, "places.csv")
    with places_path.open(mode='w', newline='') as places_file:
        csv.writer(places_file).writerows([HEADER_LIST] + PLACES_LIST)
    animal_path = Path(tmp_path, "animals_bad_header.csv")
    with animal_path.open(mode="w", newline='') as animal_file:
        csv.writer(animal_file).writerows(([BAD_HEADER_LIST] + ANIMAL_LIST))
    food_path = Path(subdirectory_path, "food.csv")
    with food_path.open(mode='w', newline='') as food_file:
        csv.writer(food_file).writerows(([HEADER_LIST] + FOOD_LIST))
    return tmp_path


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
