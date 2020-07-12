import argparse
import logging
from ast import literal_eval
from pathlib import Path

from csvlog.config_file import LogmergeConfig, get_configuration, log_levels
from csvlog.csv_merge import merge_log_files

logging.basicConfig()
logger = logging.getLogger(__name__)

# Some of the command line arguments are optional and optionally take an argument.  This leads to three situations
# *  The argument isn't present at all.  This will use the argument's "default=" value.
# * The argument is present but it doesn't have an argument.  This will use the argument's "const=" value.
# * The argument is present and the user has supplied a value, the user value will be used.

# I used constant objects here because I don't want them to be ambiguous.  If I just used a string like "DEFAULT"
# then the user could just type "DEFAULT" on the command line.
DEFAULT_OBJECT = object()


# Unfortunately, doing it this way means that I don't think I can hide the work of processing user input in custom
# type functions.  The type function is only called for user input or the default, if the default is a string.


def create_csv_merge_argument_parser() -> argparse.ArgumentParser:
    #  This is the string that shows up when the program is invoked with the -h option.
    description = "Combine CSV report"

    csv_merge_parser = argparse.ArgumentParser(description=description)
    csv_merge_parser.add_argument("--input-directory", "-i",
                                  help="The directory to scan for log files, defaults to the current working directory",
                                  default=DEFAULT_OBJECT)
    csv_merge_parser.add_argument("--output-location", "-o",
                                  help=f"Force output to the supplied location, "
                                       f"defaults to a unique time-based name in the data directory",
                                  default=DEFAULT_OBJECT)
    archive_argument = csv_merge_parser.add_mutually_exclusive_group()
    archive_argument.add_argument("-a", "--archive",
                                  help=f"Force merged files to be moved to the archive folder, "
                                       f"or the specified folder if supplied", nargs="?",
                                  default=DEFAULT_OBJECT, const=True)
    archive_argument.add_argument("--no-archive", "-A",
                                  help=f"Force no archiving.  Merged files will not be moved.",
                                  dest="archive", const=False, action="store_const")
    recursion_argument = csv_merge_parser.add_mutually_exclusive_group()
    recursion_argument.add_argument("--recursive", "-r",
                                    help=f"Force a recursive search for log files.  "
                                         f"Subdirectories of the input directory will be scanned.",
                                    default=DEFAULT_OBJECT, const=True, action="store_const")
    recursion_argument.add_argument("--no-recursive", "-R",
                                    help=f"Force a flat (non-recursive) search for log files.  "
                                         f"Subdirectories of the input directory will not be scanned",
                                    const=False, action="store_const", dest="recursive")
    header_argument = csv_merge_parser.add_mutually_exclusive_group()
    header_argument.add_argument("--header", "-t",
                                 help=f"Force header checking using the configured header, "
                                      f"or the specified header if one is supplied.", nargs="?", default=DEFAULT_OBJECT,
                                 const=True)
    header_argument.add_argument("--no-header", "-T", help=f"Force no header checking.  "
                                                           f"This will merge every .csv file found.", const=False,
                                 action="store_const", dest="header")
    verbosity_argument = csv_merge_parser.add_mutually_exclusive_group()
    verbosity_argument.add_argument("--verbose", "-v", help="Increase verbosity, repeat for even more detail.",
                                    action="count", default=0)
    verbosity_argument.add_argument("--silent", "-s", help="Decrease verbosity, repeat for even less detail.",
                                    action="count", default=0)
    return csv_merge_parser


def update_configuration_from_args(configuration: LogmergeConfig, args: argparse.Namespace) -> LogmergeConfig:
    def handle_input_directory_argument(configuration: LogmergeConfig, args: argparse.Namespace) -> LogmergeConfig:
        if args.input_directory is DEFAULT_OBJECT:
            configuration.input_directory = Path.cwd()
        else:
            user_supplied_path = Path(args.input_directory)
            if not user_supplied_path.is_dir():
                raise argparse.ArgumentTypeError(f"--input-directory {user_supplied_path} is not a directory.")
            configuration.input_directory = user_supplied_path
        return configuration

    def handle_output_location_argument(configuration: LogmergeConfig, args: argparse.Namespace) -> LogmergeConfig:
        res = Path(args.output_location) if args.output_location is not DEFAULT_OBJECT else (
            configuration.output_location)
        if res.exists():
            if res.is_dir():
                res = Path(res, f"{configuration.name_date_component}.csv")
            else:
                raise (FileExistsError(f"The file {res} already exists and will not be overwritten."))
        configuration.output_location = res
        return configuration

    def handle_archive_argument(configuration: LogmergeConfig, args: argparse.Namespace) -> LogmergeConfig:
        archive_path = Path(configuration.archive_folder)
        do_archive = bool(configuration.archive)
        if isinstance(args.archive, str):
            do_archive = True
            archive_path = Path(args.archive)
        elif args.archive is True:
            do_archive = True
        elif args.archive is False:
            do_archive = False
        if archive_path.is_dir():
            archive_path = Path(archive_path, configuration.name_date_component)
        elif archive_path.exists():
            raise (FileExistsError(f"The file {archive_path} already exists and will not be overwritten."))
        # TODO: Update the tests so that this check doesn't cause them to fail.
        # The normal default is a specific user directory.  During tests, that directory might reaosnably not exist.
        # Update the testing framework to change the default configuration file during testing so the locations are
        # inside the test directories.
        # elif not archive_path.exists():
        #     raise FileNotFoundError(
        #         f"Archive folder must be a directory that exists, the directory {archive_path} does not exist.")

        configuration.archive = do_archive
        configuration.archive_folder = archive_path
        return configuration

    def handle_recursive_argument(configuration: LogmergeConfig, args: argparse.Namespace) -> LogmergeConfig:
        configuration.recursive = configuration.recursive if args.recursive is DEFAULT_OBJECT else bool(args.recursive)
        return configuration

    def handle_header_argument(configuration: LogmergeConfig, args: argparse.Namespace) -> LogmergeConfig:
        header_arg = args.header
        file_header = configuration.header
        if header_arg is False:
            file_header = None
        if isinstance(header_arg, str):
            file_header = literal_eval(header_arg)
            if not isinstance(file_header, (list, tuple)):
                raise argparse.ArgumentTypeError(f"{file_header} is not a valid header row.")
        configuration.header = file_header
        return configuration

    def handle_verbosity_argument(configuration: LogmergeConfig, args: argparse.Namespace) -> LogmergeConfig:
        idx = log_levels.index("WARNING")
        idx += args.verbose
        idx -= args.silent
        # Force idx to be a valid index into log_levels.
        # It won't be less than 0 and it won't be greater than the last valid index in log_levels
        idx = max(0, min(len(log_levels) - 1, idx))
        configuration.log_level = log_levels[idx]
        return configuration

    # The verbosity argument needs to be handled first because it should be set properly during the handling of other
    # arguments.
    configuration = handle_verbosity_argument(configuration, args)
    configuration = handle_input_directory_argument(configuration, args)
    configuration = handle_output_location_argument(configuration, args)
    configuration = handle_archive_argument(configuration, args)
    configuration = handle_header_argument(configuration, args)
    configuration = handle_recursive_argument(configuration, args)

    return configuration


def main():
    # This is loaded from the file on disk.
    configuration = get_configuration()
    logging.getLogger().setLevel(configuration.log_level)
    parser = create_csv_merge_argument_parser()
    args = parser.parse_args()
    # This is where the configuration is updated with the command line arguments.
    configuration = update_configuration_from_args(configuration, args)
    logging.getLogger().setLevel(configuration.log_level)
    logger.debug(args)
    logger.debug(configuration)
    merge_log_files(search_directory=configuration.input_directory, output_file_path=configuration.output_location,
                    recurse=configuration.recursive,
                    header_row=configuration.header,
                    archive_directory=configuration.archive_folder if configuration.archive else None)


if __name__ == "__main__":
    main()
