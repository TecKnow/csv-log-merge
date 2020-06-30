import logging
from os import PathLike
from pathlib import Path, PurePath
from typing import Union, Iterator, Optional

logger = logging.getLogger(__name__)

PathType = Union[str, bytes, PathLike, PurePath]

# Header row
# Record Type,Material Order,Job number,Description,,,,Record key,,
DEFAULT_HEADER_ROW = ["Record Type", "Material Order", "Job number", "Description", "", "", "", "Record key", "", ""]


def get_csv_paths_in_directory(directory: PathType, ignore: Optional[PathType] = None,
                               recurse: bool = False) -> Iterator[Path]:
    directory = Path(directory)
    ignore = Path(ignore) if ignore is not None else None
    glob_string = "*.csv" if not recurse else "**/*.csv"
    return (path for path in directory.glob(glob_string) if
            path.is_file() and not (ignore and path.samefile(ignore)))

# def folder_name():
#     today = datetime.now()
#     return (str("Uploaded " + today.strftime('%y%m%d%H%M')))
#
#
# def write_merged_csv(source_dir, sourcefiles, dest_dir):
#     """
#     Function makes one output csv file from all csv files in a source directory.
#     """
#
#     if len(csvfiles) == 0:
#         pass
#     else:
#         foldername = str(folder_name())
#         fullfoldername = dest_csv_backup + '/' + foldername
#         os.makedirs(fullfoldername)
#         os.chdir(dest_dir)
#
#         with open('dest.csv', 'w') as destcsv:
#             csv_writer = csv.writer(destcsv, lineterminator='\n')
#             os.chdir(csv_dir)
#             for csvfile in csvfiles:
#                 with open(csvfile, 'r') as csvsource:
#                     csv_reader = csv.reader(csvsource)
#                     for line in csv_reader:
#                         csv_writer.writerow(line)
#                 shutil.move(csvfile, fullfoldername)

# csv_dir = 'C:\\Users\\CPerkins\\Desktop\\python_work\\CSVs\\In'
# dest_csv_dir = 'C:\\Users\\CPerkins\\Desktop\\python_work\\CSVs\\Out\\'
# dest_csv_backup = 'C:\\Users\\CPerkins\\Desktop\\python_work\\CSVs\\Backups\\'
# csvfiles = get_csv_files(csv_dir)
# write_merged_csv(csv_dir, csvfiles, dest_csv_dir)


# To Do - Compare first row of csv to headerrow to make sure it is a file we are looking for
