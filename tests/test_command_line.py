import os
from argparse import ArgumentTypeError
from pathlib import Path

import pytest

from csvlog.command_line import (create_csv_merge_argument_parser, DEFAULT_OBJECT as CMD_DEFAULT,
                                 update_configuration_from_args)
from csvlog.config_file import create_default_config, LogmergeConfig, default_header


class TestArgumentParser:
    """
    This class tests the behavior of the configured argument parser.
    """

    def test_defaults(self, arg_parser):
        all_args = set("archive header input_directory output_location recursive silent verbose".split())

        args = arg_parser.parse_args([])
        # This assertion is made using set.symmetric_difference so that the output, if it fails, is more readable.
        assert all_args.symmetric_difference(set((vars(args).keys()))) == set()
        assert args.archive is CMD_DEFAULT
        assert args.header is CMD_DEFAULT
        assert args.input_directory is CMD_DEFAULT
        assert args.output_location is CMD_DEFAULT
        assert args.recursive == CMD_DEFAULT
        assert args.silent == 0
        assert args.verbose == 0

    def test_verbosity_mutual_exclusion(self, arg_parser):
        with pytest.raises(SystemExit):
            arg_parser.parse_args(["-vvv", "-ss"])

    def test_verbosity_count(self, arg_parser):
        args = arg_parser.parse_args(["-vvv"])
        assert args.verbose == 3
        assert args.silent == 0

    def test_silent_count(self, arg_parser):
        args = arg_parser.parse_args(["--silent", "--silent", "--silent", "--silent", "--silent"])
        assert args.verbose == 0
        assert args.silent == 5

    def test_archive_flag(self, arg_parser):
        args = arg_parser.parse_args(["--archive"])
        assert args.archive is True

    def test_archive_value(self, arg_parser):
        args = arg_parser.parse_args(["--archive", "file_location"])
        assert args.archive == "file_location"

    def test_no_archive_flag(self, arg_parser):
        args = arg_parser.parse_args(["-A"])
        assert args.archive is False

    def test_no_archive_long_name(self, arg_parser):
        args = arg_parser.parse_args(["--no-archive"])
        assert args.archive is False

    def test_no_archive_takes_no_argument(self, arg_parser):
        with pytest.raises(SystemExit):
            args = arg_parser.parse_args(["-A", "file_location"])


class TestUpdateConfigurationFromArgs:

    def test_handle_verbosity_argument(self, arg_parser, logmerge_config_object):
        verbosity_strings = ("-sss", "-ss", "-s", "-v", "-vv", "-vvv", "-vvvv")
        level_strings = "CRITICAL CRITICAL ERROR INFO DEBUG NOTSET".split()
        verbosity_level_pairs = zip(verbosity_strings, level_strings)
        for verbosity, level in verbosity_level_pairs:
            res = update_configuration_from_args(logmerge_config_object, arg_parser.parse_args([verbosity]))
            assert res.log_level == level

    def test_handle_input_directory_argument_default(self, arg_parser, logmerge_config_object, argparse_test_dir):
        args_string_list = []
        res = update_configuration_from_args(logmerge_config_object, arg_parser.parse_args(args_string_list))
        assert res.input_directory == Path.cwd()

    def test_handle_input_directory_argument_custom(self, arg_parser, logmerge_config_object, argparse_test_dir):
        custom_path = Path(argparse_test_dir, "subdirectory")
        args_string_list = ["-i", str(custom_path)]
        res = update_configuration_from_args(logmerge_config_object, arg_parser.parse_args(args_string_list))
        assert res.input_directory == custom_path

    def test_handle_input_directory_argument_non_directory(self, arg_parser, logmerge_config_object, argparse_test_dir):
        custom_path = Path(argparse_test_dir, "exists.csv")
        args_string_list = ["-i", str(custom_path)]
        with pytest.raises(ArgumentTypeError):
            res = update_configuration_from_args(logmerge_config_object, arg_parser.parse_args(args_string_list))

    def test_handle_output_location_argument_default(self, arg_parser, logmerge_config_object, argparse_test_dir):
        configfile = create_default_config()
        configfile["OUTPUT"]["Folder"] = str(argparse_test_dir)
        configuration = LogmergeConfig(configfile)
        assert configuration is not None
        argument_list = []
        args_namespace = arg_parser.parse_args(argument_list)
        configuration = update_configuration_from_args(configuration, args_namespace)
        assert configuration.output_location.parent == argparse_test_dir
        assert configuration.output_location.name.endswith(".csv")

    def test_handle_output_location_argument_custom_file(self, arg_parser, logmerge_config_object, argparse_test_dir):
        configuration = LogmergeConfig(create_default_config())
        argument_list = ["-o", str(Path(argparse_test_dir, "output.csv"))]
        argument_namespace = arg_parser.parse_args(argument_list)
        configuration = update_configuration_from_args(configuration, argument_namespace)
        assert configuration.output_location.parent == argparse_test_dir
        assert configuration.output_location.name == "output.csv"

    def test_handle_output_location_argument_custom_file_exists(self, arg_parser, logmerge_config_object,
                                                                argparse_test_dir):
        configuration = LogmergeConfig(create_default_config())
        argument_list = ["-o", str(Path(argparse_test_dir, "exists.csv"))]
        argument_namespace = arg_parser.parse_args(argument_list)
        with pytest.raises(FileExistsError):
            configuration = update_configuration_from_args(configuration, argument_namespace)

    def test_handle_output_location_argument_custom_directory(self, arg_parser, logmerge_config_object,
                                                              argparse_test_dir):
        configuration = LogmergeConfig(create_default_config())
        argument_list = ["-o", str(argparse_test_dir)]
        args_namespace = arg_parser.parse_args(argument_list)
        configuration = update_configuration_from_args(configuration, args_namespace)
        assert configuration.output_location.parent == argparse_test_dir
        assert configuration.output_location.name.endswith(".csv")

    def test_handle_archive_argument_default(self, arg_parser, logmerge_config_object,
                                             argparse_test_dir):
        config_file = create_default_config()
        config_file["ARCHIVE"]["Folder"] = str(argparse_test_dir)
        configuration = LogmergeConfig(config_file)
        argument_list = []
        args_namespace = arg_parser.parse_args(argument_list)
        configuration = update_configuration_from_args(configuration, args_namespace)
        assert configuration.archive_folder.parent == argparse_test_dir
        assert configuration.archive is True

    def test_handle_archive_argument_true(self, arg_parser, logmerge_config_object,
                                          argparse_test_dir):
        config_file = create_default_config()
        config_file["ARCHIVE"]["Folder"] = str(argparse_test_dir)
        config_file["ARCHIVE"]["AutoArchive"] = str(False)
        configuration = LogmergeConfig(config_file)
        assert configuration.archive is False
        argument_list = ["-a"]
        args_namespace = arg_parser.parse_args(argument_list)
        configuration = update_configuration_from_args(configuration, args_namespace)
        assert configuration.archive_folder.parent == argparse_test_dir
        assert configuration.archive is True

    def test_handle_archive_argument_false(self, arg_parser, logmerge_config_object,
                                           argparse_test_dir):
        config_file = create_default_config()
        config_file["ARCHIVE"]["Folder"] = str(argparse_test_dir)
        configuration = LogmergeConfig(config_file)
        assert configuration.archive is True
        argument_list = ["-A"]
        args_namespace = arg_parser.parse_args(argument_list)
        configuration = update_configuration_from_args(configuration, args_namespace)
        assert configuration.archive_folder.parent == argparse_test_dir
        assert configuration.archive is False

    def test_handle_archive_argument_custom(self, arg_parser, logmerge_config_object,
                                            argparse_test_dir):
        config_file = create_default_config()
        config_file["ARCHIVE"]["AutoArchive"] = str(False)
        configuration = LogmergeConfig(config_file)
        assert configuration.archive is False
        argument_list = ["-a", str(Path(argparse_test_dir, "subdirectory"))]
        args_namespace = arg_parser.parse_args(argument_list)
        configuration = update_configuration_from_args(configuration, args_namespace)
        assert configuration.archive_folder.parent == Path(argparse_test_dir, "subdirectory")
        assert configuration.archive is True

    def test_handle_archive_argument_exists(self, arg_parser, logmerge_config_object,
                                            argparse_test_dir):
        config_file = create_default_config()
        config_file["ARCHIVE"]["AutoArchive"] = str(False)
        configuration = LogmergeConfig(config_file)
        assert configuration.archive is False
        argument_list = ["-a", str(Path(argparse_test_dir, "exists.csv"))]
        args_namespace = arg_parser.parse_args(argument_list)
        with pytest.raises(FileExistsError):
            configuration = update_configuration_from_args(configuration, args_namespace)

    @pytest.mark.xfail(reason="Not yet implemented")
    def test_handle_archive_argument_does_not_exist(self, arg_parser, logmerge_config_object,
                                                    argparse_test_dir):
        config_file = create_default_config()
        config_file["ARCHIVE"]["AutoArchive"] = str(False)
        configuration = LogmergeConfig(config_file)
        assert configuration.archive is False
        argument_list = ["-a", str(Path(argparse_test_dir, "nonexistentdirectory"))]
        args_namespace = arg_parser.parse_args(argument_list)
        with pytest.raises(FileNotFoundError):
            configuration = update_configuration_from_args(configuration, args_namespace)

    def test_handle_header_argument_default(self, arg_parser, logmerge_config_object,
                                            argparse_test_dir):
        config_file = create_default_config()
        configuration = LogmergeConfig(config_file)
        assert configuration.header == default_header
        argument_list = []
        args_namespace = arg_parser.parse_args(argument_list)
        configuration = update_configuration_from_args(configuration, args_namespace)
        assert configuration.header == default_header

    def test_handle_header_argument_true(self, arg_parser, logmerge_config_object,
                                         argparse_test_dir):
        # TODO:  Allow this to be false by default?
        config_file = create_default_config()
        configuration = LogmergeConfig(config_file)
        assert configuration.header == default_header
        argument_list = ["-t"]
        args_namespace = arg_parser.parse_args(argument_list)
        configuration = update_configuration_from_args(configuration, args_namespace)
        assert configuration.header == default_header

    def test_handle_header_argument_false(self, arg_parser, logmerge_config_object,
                                          argparse_test_dir):
        # TODO:  Is None how this should be expressed?
        config_file = create_default_config()
        configuration = LogmergeConfig(config_file)
        assert configuration.header == default_header
        argument_list = ["-T"]
        args_namespace = arg_parser.parse_args(argument_list)
        configuration = update_configuration_from_args(configuration, args_namespace)
        assert configuration.header is None

    def test_handle_header_argument_custom(self, arg_parser, logmerge_config_object,
                                           argparse_test_dir):
        config_file = create_default_config()
        configuration = LogmergeConfig(config_file)
        custom_header = ["one", "two", "three"]
        assert configuration.header == default_header
        argument_list = ["-t", repr(custom_header)]
        args_namespace = arg_parser.parse_args(argument_list)
        configuration = update_configuration_from_args(configuration, args_namespace)
        assert configuration.header == custom_header

    def test_handle_header_argument_bad(self, arg_parser, logmerge_config_object,
                                        argparse_test_dir):
        config_file = create_default_config()
        configuration = LogmergeConfig(config_file)
        custom_header = "[\\fnord"
        assert configuration.header == default_header
        argument_list = ["-t", repr(custom_header)]
        args_namespace = arg_parser.parse_args(argument_list)
        with pytest.raises(ArgumentTypeError):
            configuration = update_configuration_from_args(configuration, args_namespace)

    def test_handle_recursive_argument_default(self, arg_parser, logmerge_config_object,
                                               argparse_test_dir):
        config_file = create_default_config()
        configuration = LogmergeConfig(config_file)
        assert configuration.recursive is False
        argument_list = []
        args_namespace = arg_parser.parse_args(argument_list)
        configuration = update_configuration_from_args(configuration, args_namespace)
        assert configuration.recursive is False

    def test_handle_recursive_argument_true(self, arg_parser, logmerge_config_object,
                                            argparse_test_dir):
        config_file = create_default_config()
        config_file["SEARCH"]["AutoRecursive"] = str(False)
        configuration = LogmergeConfig(config_file)
        assert configuration.recursive is False
        argument_list = ["-r"]
        args_namespace = arg_parser.parse_args(argument_list)
        configuration = update_configuration_from_args(configuration, args_namespace)
        assert configuration.recursive is True

    def test_handle_recursive_argument_false(self, arg_parser, logmerge_config_object,
                                             argparse_test_dir):
        config_file = create_default_config()
        config_file["SEARCH"]["AutoRecursive"] = str(True)
        configuration = LogmergeConfig(config_file)
        assert configuration.recursive is True
        argument_list = ["-R"]
        args_namespace = arg_parser.parse_args(argument_list)
        configuration = update_configuration_from_args(configuration, args_namespace)
        assert configuration.recursive is False


@pytest.fixture
def arg_parser():
    """
    A fixture for supplying an argument parser object to test functions.

    I know that it only saves one line per function, but the savings do add up.  Also, it's a simple demonstration of
    declaring a new fixture.
    """
    return create_csv_merge_argument_parser()


@pytest.fixture
def logmerge_config_object():
    """
    A fixture for supplying a default LogmergeConfig object to test functions.
    """

    # TODO:  Update the default configuration for tests to locations in the test directories.
    config_parser = create_default_config()
    return LogmergeConfig(create_default_config())


@pytest.fixture
def argparse_test_dir(tmp_path):
    previous_cwd = Path.cwd()
    # noinspection PyTypeChecker
    os.chdir(tmp_path)
    Path(tmp_path, "exists.csv").touch()
    Path(tmp_path, "directory.csv").mkdir()
    Path(tmp_path, "subdirectory").mkdir()
    yield tmp_path
    # noinspection PyTypeChecker
    os.chdir(previous_cwd)


if __name__ == '__main__':
    pytest.main()
