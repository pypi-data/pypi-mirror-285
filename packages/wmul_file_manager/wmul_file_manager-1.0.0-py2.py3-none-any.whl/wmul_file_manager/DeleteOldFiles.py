"""
@Author = 'Mike Stanley'

Script that deletes old files and folders off a given root folder.

Mainly designed to be run from command-line, but can also be called from other scripts.

Command-Line Options:
-f  --folder            The folder to begin the search for old files. All old files in this folder and its
                            sub-folders will be deleted.
-o  --older_than        The number of days old a file must be to be deleted, rounded to the nearest day.
                            IE If today is the 12th and the user inputs '7', then all files from the 4th and older
                            will be deleted.
-r  --remove_folders    Delete any folders that are empty after the old files are deleted.
-s  --suffix            The suffix(es) of the old files to be deleted. Must include the dot ('.'). If this is left
                            blank, all old files will be deleted.

============ Change Log ============
2024-May-03 = Updated datetime to use UTC.

2018-May-18 = Remove old command-line interface that was housed in this file and based on argparse.

2018-May-16 = Imported from Titanium_Monticello.

              Rework the API to embed the older_than argument into DeleteOldFilesArguments

2017-Aug-24 = Added --verbose option.

2017-Aug-18 = Move the logger from Utilities to Logger.

2017-Aug-11 = Refactor argparse.

              Create a method to act as an external entry point for this script. Modify _run_from_command_line to use
                that method.

              Create a named tuple to encapsulate the arguments to run_script. Modify _run_from_command_line to
                use the new named tuple.

              Add logging.

              Refactor to use Utilities.directory_is_empty

2015-Mar-26 = Created.

============ License ============
The MIT License (MIT)

Copyright (c) 2015, 2017-2018, 2024 Michael Stanley

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from collections import namedtuple
from datetime import datetime
from datetime import timezone

import wmul_logger
from wmul_file_manager.utilities.FileNamePrinter import object_cleaner
from wmul_file_manager.utilities import directories

logger = wmul_logger.get_logger()


def delete_old_files(source_path, arguments):
    logger.debug(f"In delete_old_files with {locals()}")
    for file_item in source_path.iterdir():
        logger.debug(f"In delete_old_files, working on: {object_cleaner(file_item)}")
        if file_item.is_dir():
            _purge_old_files_from_directory(file_item, arguments)
        else:
            _check_and_delete_old_file(file_item, arguments)


def _check_and_delete_old_file(this_file, arguments):
    logger.debug("Is file.")
    if arguments.limited_suffixes_flag and (this_file.suffix not in arguments.limited_suffixes_list):
        logger.debug("Suffix is not one of the ones we want.")
        return
    if _file_is_older(older_than=arguments.older_than, this_file=this_file):
        logger.info(f"{object_cleaner(this_file)} older, deleting.")
        this_file.unlink()
    else:
        logger.debug("Is younger, continueing.")


def _file_is_older(older_than, this_file):
    this_file_stat = this_file.stat()
    this_file_mtime = this_file_stat.st_mtime
    this_file_datetime = datetime.fromtimestamp(this_file_mtime, timezone.utc)
    return this_file_datetime < older_than


def _purge_old_files_from_directory(this_directory, arguments):
    logger.debug(f"In _purge_old_files_from_directory with {locals()}")
    delete_old_files(this_directory, arguments)
    if arguments.remove_folders_flag:
        logger.debug("remove_folders is true.")
        if directories.directory_is_empty(this_directory):
            logger.debug(f"Directory is empty: {object_cleaner(this_directory)}")
            this_directory.rmdir()


def run_script(arguments):
    logger.debug(f"In run_script, with {arguments}")
    delete_old_files(arguments.source_path, arguments)


DeleteOldFilesArguments = namedtuple(
    "DeleteOldFilesArguments",
    [
        "source_path",
        "remove_folders_flag",
        "limited_suffixes_flag",
        "limited_suffixes_list",
        "older_than"
    ]
)
