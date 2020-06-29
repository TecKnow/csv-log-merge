import os
from pathlib import Path

import pytest

from csvlog.command_line import create_csv_merge_argument_parser


class TestCommandLine:
    """
    This class contains test for the command line argument parser

    Be aware that if it can't make sense of the input, _argparse.ArgumentParser ultimately throws a SystemExit
    exception, which can interfere with any further tests.  It also throws an ArgumentError but it doesn't appear that
    this can be caught.  It seems that the ArgumentParser catches the ArgumentError internally and re-raises the
    SystemExit exception.
    """

    def test_default_arguments(self, arg_parser):
        """
        Verify the default values of command line arguments

        These types of tests can be frustrating to maintain, but they can also serve as an early warning of unintended
        changes as well as documentation of intended behavior.

        Sample args object from 28 June 2020:
        Namespace(
        backup_directory=None,
        input_directory=WindowsPath('D:/Users/teckn/PycharmProjects/cperkins/cperkins-csv-log/tests'),
        log_level='WARN',
        output_file=None)
        """
        args = arg_parser.parse_args([])
        assert args.backup_directory is None

        assert isinstance(args.output_file, Path)
        assert str(args.output_file.relative_to(Path.cwd())) == args.output_file.name
        assert args.output_file.suffix == ".csv"

        assert isinstance(args.input_directory, Path)
        assert args.input_directory == Path.cwd()

        assert args.backup_directory is None

        assert args.log_level == "WARN"

    def test_bad_log_level(self, arg_parser):
        """
        Test that invalid log levels cannot be specified on the command line

        This also demonstrates how to make a test with bad arguments pass.
        """
        with pytest.raises(SystemExit):
            arg_parser.parse_args(["--log-level", "foo"])

    def test_log_level_case_insensitive(self, arg_parser):
        """Test that the log level command line argument is case insensitive"""
        args = arg_parser.parse_args(["--log-level", "dEbUg"])
        assert args.log_level == "DEBUG"

    def test_input_directory_not_a_directory(self, arg_parser, argparse_test_dir):
        with pytest.raises(SystemExit):
            arg_parser.parse_args(["--input-directory", str(Path(argparse_test_dir, "exists.csv"))])

    def test_input_directory_does_not_exist(self, arg_parser, argparse_test_dir):
        with pytest.raises(SystemExit):
            arg_parser.parse_args(["--input-directory", str(Path(argparse_test_dir, "not_a_real_file"))])

    def test_output_file_already_exists(self, arg_parser, argparse_test_dir):
        with pytest.raises(SystemExit):
            arg_parser.parse_args(["--output-file", str(Path(argparse_test_dir, "exists.csv"))])

    def test_output_file_is_directory(self, arg_parser, argparse_test_dir):
        with pytest.raises(SystemExit):
            arg_parser.parse_args(["--output-file", str(Path(argparse_test_dir, "directory.csv"))])

    def test_backup_directory_is_file(self, arg_parser, argparse_test_dir):
        with pytest.raises(SystemExit):
            arg_parser.parse_args(["--backup-directory", str(Path(argparse_test_dir, "exists.csv"))])

    def test_backup_directory_does_not_exist(self, arg_parser, argparse_test_dir):
        with pytest.raises(SystemExit):
            arg_parser.parse_args(["--backup-directory", str(Path(argparse_test_dir, "not_a_real_file"))])


@pytest.fixture
def arg_parser():
    """
    A fixture for supplying an argument parser object to test functions.

    I know that it only saves one line per function, but the savings do add up.  Also, it's a simple demonstration of
    declaring a new fixture.
    """
    return create_csv_merge_argument_parser()


@pytest.fixture
def argparse_test_dir(tmp_path):
    previous_cwd = Path.cwd()
    # noinspection PyTypeChecker
    os.chdir(tmp_path)
    Path(tmp_path, "exists.csv").touch()
    Path(tmp_path, "directory.csv").mkdir()
    yield tmp_path
    # noinspection PyTypeChecker
    os.chdir(previous_cwd)


if __name__ == '__main__':
    pytest.main()
