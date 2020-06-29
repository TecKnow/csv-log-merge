from argparse import ArgumentError
from pathlib import Path

import pytest

from csvlog.command_line import create_csv_merge_argument_parser


class TestCommandLine:
    """
    This class contains test for the command line argument parser

    One challenge in testing the _argparse_ parser is that it throws a _SystemExit_ exception if it can't make sense of
    the input, as well as an _argparse.ArgumentError_.  This means that they both need to be caught in the correct order
    for error tests to pass.
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
        assert isinstance(args.input_directory,
                          Path)
        assert args.input_directory == Path.cwd()
        assert args.log_level == "WARN"
        assert args.output_file is None

    def test_bad_log_level(self, arg_parser):
        """
        Test that invalid log levels cannot be specified on the command line

        This also demonstrates how to make a test with bad arguments pass.

        Be aware that the _argparse_ module tries to throw an _argparse.ArgumentError_ and a _SystemExit_ error
        separately.  They must be trapped separately and in the correct order for the test to pass.
        """
        with pytest.raises(SystemExit), pytest.raises(ArgumentError):
            args = arg_parser.parse_args(["--log-level", "foo"])

    def test_log_level_case_insensitive(self, arg_parser):
        """Test that the log level command line argument is case insensitive"""
        args = arg_parser.parse_args(["--log-level", "dEbUg"])
        assert args.log_level == "DEBUG"


@pytest.fixture
def arg_parser():
    """
    A fixture for supplying an argument parser object to test functions.

    I know that it only saves one line per function, but the savings do add up.  Also, it's a simple demonstration of
    declaring a new fixture.
    """
    return create_csv_merge_argument_parser()


if __name__ == '__main__':
    pytest.main()
