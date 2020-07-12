import configparser
import logging
from ast import literal_eval
from datetime import datetime
from os import PathLike
from pathlib import Path
from typing import Optional, Union

logger = logging.getLogger(__name__)

# These match the default log levels defined in the logging package in order of severity.
# NOTSET on the root logger means that all messages will be shown.
log_levels = "critical error warning info debug notset".upper().split()

# TODO:  This is also in csv_merge.py, remove the duplication
default_header = ["Record Type", "Material Order", "Job number", "Description", "", "", "", "Record key", "", ""]
default_config_file_location = Path(Path.home(), "Documents", "csvmerge", "logmerge.cfg")
default_archive_location = Path(default_config_file_location.parent, "archive")
default_output_location = Path(default_config_file_location.parent)


class LogmergeConfig:
    # TODO: Should this just be a dataclass?
    def __init__(self, config_parser: configparser.ConfigParser):
        self.cfg = config_parser
        self.date_format_string = '%y%m%d%H%M%S'
        self.name_date_component = datetime.now().strftime(self.date_format_string)
        self.header = literal_eval(self.cfg.get("SEARCH", "Header", fallback=repr(default_header)))
        self.recursive = self.cfg.getboolean("SEARCH", "AutoRecursive", fallback=False)
        self.archive_folder = Path(self.cfg.get("ARCHIVE", "Folder", fallback=default_archive_location))
        self.archive = self.cfg.getboolean("ARCHIVE", "AutoArchive", fallback=True)
        self.output_location = Path(self.cfg.get("OUTPUT", "Folder", fallback=default_output_location))
        self.log_level = self.cfg.get("OUTPUT", "LogLevel", fallback="WARNING")
        self.input_directory = None


def get_configuration(config_file_path: Optional[Union[PathLike, Path]] = None) -> LogmergeConfig:
    cfg = load_or_create_configparser(config_file_path)
    return LogmergeConfig(cfg)


def load_or_create_configparser(config_file_path: Optional[Union[PathLike, Path]] = None) -> configparser.ConfigParser:
    if config_file_path is None:
        config_file_path = default_config_file_location
        verify_default_directories()
    if not config_file_path.exists():
        logger.info(f"Creating default config file at {config_file_path}")
        write_default_config(config_file_path)
    logger.debug(f"Loading configuration file at {config_file_path}")
    cfg = configparser.ConfigParser()
    cfg.read(config_file_path)
    return cfg


def verify_default_directories():
    # TODO: Figure out how to test this
    user_documents_directory = Path(Path.home(), "Documents")
    if not user_documents_directory.exists():
        logger.warning(f"Cannot find user documents directory at {user_documents_directory}")
    default_config_file_location.parent.mkdir(parents=True, exist_ok=True)
    default_archive_location.mkdir(parents=True, exist_ok=True)


def write_default_config(config_file_path: Union[PathLike, Path] = default_config_file_location) -> None:
    cfg = create_default_config()
    with config_file_path.open(mode="w") as configfile:
        cfg.write(configfile)


def create_default_config() -> configparser.ConfigParser:
    # TODO: Add a prefernece for no automatic header checking?
    cfg = configparser.ConfigParser()
    cfg["SEARCH"] = {"Header": repr(default_header),
                     "AutoRecursive": str(False)}
    cfg["ARCHIVE"] = {"Folder": str(default_archive_location),
                      "AutoArchive": str(True)}
    cfg["OUTPUT"] = {"Folder": str(default_output_location),
                     "LogLevel": "WARNING"}
    return cfg
