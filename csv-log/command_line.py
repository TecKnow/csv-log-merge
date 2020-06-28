import argparse
import logging
from pathlib import Path

logging.basicConfig()
logger = logging.getLogger(__name__)


def create_csv_merge_argument_parser():
    def path_type(path):
        return Path(path) if path is not None else None

    description = "Combine CSV report files NOT YET IMPLEMENTED"
    log_levels = "critical error warning info debug notset".upper().split()
    csv_merge_parser = argparse.ArgumentParser(description=description)
    csv_merge_parser.add_argument("--input-directory", "-i",
                                  help="Input directory, defaults to the current working directory",
                                  type=path_type, default=Path.cwd())
    csv_merge_parser.add_argument("--output-file", "-f",
                                  help="The resulting combined CSV file, defaults to standard out",
                                  type=path_type)
    csv_merge_parser.add_argument("--backup-directory", "-b",
                                  help="The backup directory, files are not moved if this argument is not present.",
                                  type=path_type)
    csv_merge_parser.add_argument("--log-level", "-l", choices=log_levels, default="WARN", type=str.upper,
                                  help="Optional logging level")
    return csv_merge_parser


if __name__ == "__main__":
    parser = create_csv_merge_argument_parser()
    args = parser.parse_args()
    logging.getLogger().setLevel(args.log_level)
    logger.info(args)
