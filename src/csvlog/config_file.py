import configparser
import logging
from ast import literal_eval
from os import PathLike
from pathlib import Path
from typing import Optional, Union

logger = logging.getLogger(__name__)

# TODO:  This is also in csv_merge.py, remove the duplication
default_header = ["Record Type", "Material Order", "Job number", "Description", "", "", "", "Record key", "", ""]
default_config_file_location = Path(Path.home(), "Documents", "csvmerge", "logmerge.cfg")
default_archive_location = Path(default_config_file_location.parent, "archive")
default_output_location = Path(default_config_file_location.parent)


class LogmergeConfig:
    def __init__(self, config_parser: configparser.ConfigParser):
        self.cfg = config_parser

    @property
    def default_header(self):
        return literal_eval(self.cfg.get("SEARCH", "DefaultHeader", fallback=repr(default_header)))

    @property
    def auto_recursive(self):
        return self.cfg.getboolean("SEARCH", "AutoRecursive", fallback=False)

    @property
    def archive_folder(self):
        return Path(self.cfg.get("ARCHIVE", "Folder", fallback=default_archive_location))

    @property
    def auto_archive(self):
        return self.cfg.getboolean("ARCHIVE", "AutoArchive", fallback=True)

    @property
    def output_location(self):
        return Path(self.cfg.get("OUTPUT", "Folder", fallback=default_output_location))


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
    cfg = configparser.ConfigParser()
    cfg["SEARCH"] = {"DefaultHeader": repr(default_header),
                     "AutoRecursive": str(False)}
    cfg["ARCHIVE"] = {"Folder": str(default_archive_location),
                      "AutoArchive": str(True)}
    cfg["OUTPUT"] = {"Folder": str(default_output_location)}
    return cfg
