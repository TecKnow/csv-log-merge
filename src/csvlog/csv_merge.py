import logging
from csv import reader, writer
from os import PathLike
from pathlib import Path, PurePath
from typing import Union, Iterator, Optional, Sequence, Callable

logger = logging.getLogger(__name__)

PathType = Union[str, bytes, PathLike, PurePath]

# Header row
# Record Type,Material Order,Job number,Description,,,,Record key,,
DEFAULT_HEADER_ROW = ["Record Type", "Material Order", "Job number", "Description", "", "", "", "Record key", "", ""]


def merge_log_files(search_directory: PathType, output_file_path: PathType, recurse: bool = False,
                    header_row: Optional[Sequence[str]] = None,
                    archive_directory: Optional[PathType] = None) -> None:
    search_directory = Path(search_directory) if search_directory is not None else None
    output_file_path = Path(output_file_path)
    archive_directory = Path(archive_directory) if archive_directory is not None else None
    if header_row and not isinstance(header_row, Sequence):
        header_row = DEFAULT_HEADER_ROW
    csv_file_iterator = get_csv_paths_in_directory(search_directory, output_file_path, recurse)
    combiner = log_file_combiner(output_file_path, header_row)
    iterator_of_merged_files = combiner(csv_file_iterator)
    for file_path in iterator_of_merged_files:
        move_file_to_archive(file_path, archive_directory, file_path)


def log_file_combiner(output_file_path: Path, header_row: Optional[Sequence[str]] = None) -> Callable[
    [Iterator[Path]], Iterator[Path]]:
    with output_file_path.open(newline='') as output_file:
        log_writer = writer(output_file)
        if header_row:
            if not isinstance(header_row, Sequence):
                header_row = DEFAULT_HEADER_ROW
            log_writer.writerow(header_row)

        def log_file_combiner_closure(input_file_paths: Iterator[Path]) -> Iterator[Path]:
            for input_file_path in input_file_paths:
                with input_file_path.open(newline='') as input_file:
                    log_reader = reader(input_file)
                    was_merged = log_record_combiner(log_writer, log_reader, header_row)
                if was_merged:
                    yield input_file_path

        return log_file_combiner_closure


def log_record_combiner(output_writer: writer, input_reader: reader,
                        header_row: Optional[Sequence[str]] = None) -> bool:
    res = False
    if not header_row or next(input_reader) == header_row:
        output_writer.writerows(input_reader)
        res = True
    return res


def get_csv_paths_in_directory(directory: PathType, ignore: Optional[PathType] = None,
                               recurse: bool = False) -> Iterator[Path]:
    # Argument conversion.  This is where we convert the arguments we receive into the form that is most useful for us.
    directory = Path(directory)
    ignore = Path(ignore) if ignore is not None else None
    glob_string = "*.csv" if not recurse else "**/*.csv"
    # This acts as a filter on the list of files.  We don't want to append our output file to itself, so we exclude it
    # from the listings.
    return (path for path in directory.glob(glob_string) if
            path.is_file() and not (ignore and path.samefile(ignore)))


def move_file_to_archive(search_directory: Path, archive_directory: Path, file_to_move: Path) -> None:
    relative_path = file_to_move.relative_to(search_directory)
    destination_path = Path(archive_directory, relative_path)
    if destination_path.exists():
        logger.error(f"Destination file {destination_path} already exists.")
        raise FileExistsError
    file_to_move.replace(destination_path)
