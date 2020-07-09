import configparser
from pathlib import Path

import pytest

from csvlog.config_file import (LogmergeConfig, default_header, default_archive_location, default_output_location,
                                create_default_config, load_or_create_configparser, write_default_config,
                                get_configuration)


class TestLogmergeConfig:
    def test_defaults(self):
        cfg = configparser.ConfigParser()
        lmc = LogmergeConfig(cfg)
        assert lmc.header == default_header
        assert lmc.recursive is False
        assert lmc.archive_folder == default_archive_location
        assert lmc.archive is True
        assert lmc.output_location == default_output_location
        assert lmc.log_level == "WARN"


class TestCreateDefaultConfig:

    def test_custom_location(self, tmp_path):
        configure_file_path = Path(tmp_path, "logmerge.csv")
        assert not configure_file_path.exists()
        write_default_config(configure_file_path)
        assert configure_file_path.exists()
        cfg = configparser.ConfigParser()
        cfg.read(configure_file_path)
        # TODO: Eliminate this duplication.
        assert set(cfg.sections()) == set("SEARCH ARCHIVE OUTPUT".split())
        assert cfg["SEARCH"]["Header"] == repr(default_header)
        assert cfg.getboolean("SEARCH", "AutoRecursive") is False
        assert cfg.get("ARCHIVE", "Folder") == str(default_archive_location)
        assert cfg.getboolean("ARCHIVE", "AutoArchive") is True
        assert cfg.get("OUTPUT", "Folder") == str(default_output_location)
        assert cfg.get("OUTPUT", "LogLevel") == "WARN"

    def test_custom_location_is_directory(self, tmp_path):
        directory_path = Path(tmp_path, "subfolder")
        directory_path.mkdir()
        with pytest.raises(PermissionError):
            write_default_config(directory_path)


class TestLoadOrCreateConfigparser:
    def test_create_default_config(self, tmp_path):
        config_file_path = Path(tmp_path, "config.cfg")
        assert not config_file_path.exists()
        cfg = load_or_create_configparser(config_file_path)
        assert config_file_path.exists()
        # TODO: Eliminate this duplication.
        assert set(cfg.sections()) == set("SEARCH ARCHIVE OUTPUT".split())
        assert cfg["SEARCH"]["Header"] == repr(default_header)
        assert cfg.getboolean("SEARCH", "AutoRecursive") is False
        assert cfg.get("ARCHIVE", "Folder") == str(default_archive_location)
        assert cfg.getboolean("ARCHIVE", "AutoArchive") is True
        assert cfg.get("OUTPUT", "Folder") == str(default_output_location)
        assert cfg.get("OUTPUT", "LogLevel") == "WARN"

    def test_read_custom_config(self, tmp_path):
        archive_path = Path(tmp_path, "archive")
        config_file_path = Path(tmp_path, "config.cfg")
        assert not config_file_path.exists()
        assert not archive_path.exists()
        archive_path.mkdir()
        assert archive_path.exists()
        cfg = create_default_config()
        cfg["ARCHIVE"]["Folder"] = str(archive_path)
        with config_file_path.open(mode="w") as cfg_outfile:
            cfg.write(cfg_outfile)
        assert config_file_path.exists()
        read_config = load_or_create_configparser(config_file_path)
        assert read_config.get("ARCHIVE", "Folder") == str(archive_path)


class TestGetConfiguration:
    def test_default_config(self, tmp_path):
        # TODO: Remove this duplication.
        config_file_path = Path(tmp_path, "config.cfg")
        assert not config_file_path.exists()
        lmc = get_configuration(config_file_path)
        assert config_file_path.exists()
        assert lmc.header == default_header
        assert lmc.recursive is False
        assert lmc.archive_folder == default_archive_location
        assert lmc.archive is True
        assert lmc.output_location == default_output_location

    def test_custom_config(self, tmp_path):
        # TODO: Remove this duplication.
        archive_path = Path(tmp_path, "archive")
        config_file_path = Path(tmp_path, "config.cfg")
        assert not config_file_path.exists()
        assert not archive_path.exists()
        archive_path.mkdir()
        assert archive_path.exists()
        cfg = create_default_config()
        cfg["ARCHIVE"]["Folder"] = str(archive_path)
        with config_file_path.open(mode="w") as cfg_outfile:
            cfg.write(cfg_outfile)
        assert config_file_path.exists()
        lmc = get_configuration(config_file_path)
        assert lmc.archive_folder == archive_path
