"""
@Author = 'Mike Stanley'

Script to copy the contents of one folder of into another. If the copy of a particular file fails for any reason,
it continues with the remaining files (rather than quitting, like Windows). If a file already exists, compares the
creation and modification times. If the origin file is newer, overwrites the destination file.

Mainly designed to be run from command-line, but can also be called from other scripts.

Access from the command-line is through cli.bulk_copy.

============ Change Log ============
2018-May-25 = Rename members of BulkCopierArguments, and some method-local variables

              Rename synchronize_paths to _synchronize_directories.

              Inline _synchronize_directory into _synchronize_directories.

2018-May-24 = Rename logger to _logger.

2018-May-01 = Remove old command-line interface that was housed in this file and based on argparse.

2018-Apr-23 = Imported from Titanium_Monticello to this project.

2017-Aug-18 = Move the logger from Utilities to Logger.

              Add --verbose command-line option.

2017-Aug-10 = Refactor calls to argparse.

              Modify logging to use the logger provided in Utilities.
              Improve logging.

              Re-work the mkdir call to make better use of the library.

2017-Jul-28 = Update documentation.

              Refactor Pathlib import.

2017-Jul-26 = Change formatting of dates in change log.

              Add back-entries to change log.

              Rename some methods to be private.

              Reformat the calls to add_argument to be uniform.

              Create a method to act as an external entry point for this script.

              Create a named tuple to encapsulate the arguments to run_script. Modify _run_from_command_line to use
                the new named tuple.

              Modify to take multiple root folders.

2017-Jan-30 = Bugfix for deleting old files.

2017-Jan-25 = Debugged the deletion routine.

2017-Jan-10 = Improve logging.

2017-Jan-04 = Added command-line option to delete old files.

2016-Dec-20 = Add Force_Copy command-line param to force all files to be copied, regardless of whether the destination
                file is newer.

2016-Dec-19 = Improve Logging by adding some info level logs and making the log file name a command-line param.

2016-Nov-18 = Add logging and ability to ignore folders.

2015-Aug-30 = Create an empty exclusion list if no extensions/suffixes are provided by the user.

2015-Jul-08 = Add logic and command-line option to exclude specified extensions.

2015-Jul-02 = Add documentation, MIT license.

              Move command-line logic to its own method.

              PEP8.

2015-Mar-17 = Make destination directory if it does not already exist.

2015-Mar-16 = Created.

============ License ============
The MIT License (MIT)

Copyright (c) 2015-2018, 2024 Michael Stanley

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
import shutil
from collections import namedtuple

import wmul_logger
from wmul_file_manager.utilities.FileNamePrinter import object_cleaner

_logger = wmul_logger.get_logger()


def _synchronize_directories(source_path, destination_path, exclude_exts, ignore_folders, force_copy):
    _logger.info(f"With {locals()}")
    destination_path.mkdir(parents=True, exist_ok=True)
    for source_item in source_path.iterdir():
        _logger.debug(f"In synchronize_paths, working on: {object_cleaner(source_item)}")
        if source_item.is_file():
            _logger.debug(f"Is File.")
            if not source_item.suffix.casefold() in exclude_exts:
                _logger.debug(f"Extension not excluded: {source_item.suffix}")
                _synchronize_file(source_item, destination_path, force_copy)
            else:
                _logger.debug(f"Extension excluded: {source_item.suffix} ")
        elif source_item.is_dir():
            _logger.info(f"Is Directory")
            if source_item not in ignore_folders:
                _logger.debug(f"Directory Not Ignored")
                destination_item = destination_path / source_item.name
                _synchronize_directories(source_item, destination_item, exclude_exts, ignore_folders, force_copy)
            else:
                _logger.debug("Directory Ignored")
        else:
            _logger.warning(f"Is neither a file nor a directory. {object_cleaner(source_item)}")


def _synchronize_file(source_item, destination_path, force_copy):
    _logger.debug(f"In _synchronize_file with {locals()}")
    destination_item = destination_path / source_item.name
    if not destination_item.exists():
        _logger.debug(f"Does not exist: {object_cleaner(destination_item)}")
        _try_copy(source_item, destination_item)
    elif force_copy:
        _logger.debug("Force Copy")
        _try_copy(source_item, destination_item)
    else:
        src_mtime = source_item.stat().st_mtime
        dst_mtime = destination_item.stat().st_mtime
        if (src_mtime - dst_mtime) > 60:
            _logger.debug(f"Destination file older. {src_mtime} : {dst_mtime}")
            _try_copy(source_item, destination_item)


def _try_copy(source_item, destination_item):
    _logger.info(f"Synchronizing {object_cleaner(source_item)}")
    done = False
    while not done:
        try:
            shutil.copy2(str(source_item), str(destination_item))
            done = True
        except IOError as ex:
            done = True
            _logger.debug(ex)


def _delete_old_files(source_path, destination_path, exclude_exts):
    _logger.debug(f"In _delete_old_files with {locals()}")
    for destination_item in destination_path.iterdir():
        _logger.debug(f"In _delete_old_files, working on: {object_cleaner(destination_item)}")
        if destination_item.is_file():
            _logger.debug("Is File")
            if not destination_item.suffix.casefold() in exclude_exts:
                _logger.debug(f"Extension not excluded: {destination_item.suffix}")
                if not _has_matching_source_file(destination_item, source_path):
                    _logger.info(f"Deleting {object_cleaner(destination_item)}")
                    destination_item.unlink()
        else:
            _logger.debug("Is not file")
            new_path = source_path / destination_item.name
            _delete_old_files(new_path, destination_item, exclude_exts)


def _has_matching_source_file(destination_item, source_path):
    _logger.debug(f"In _has_matching_source_file with {locals()}")
    source_item = source_path / destination_item.name
    return source_item.exists()


BulkCopierArguments = namedtuple(
    "BulkCopierArguments",
    [
        "source_directories",
        "destination_directory",
        "exclude_suffixes_list",
        "ignore_directories",
        "force_copy_flag",
        "delete_old_files_flag"
    ]
)


def run_script(arguments):
    _logger.info(f"Starting run_script with {arguments}")
    for this_source_dir in arguments.source_directories:
        _logger.debug(f"Working on {this_source_dir}")
        this_dest_dir = arguments.destination_directory / this_source_dir.name
        _synchronize_directories(this_source_dir, this_dest_dir, arguments.exclude_suffixes_list,
                                 arguments.ignore_directories, arguments.force_copy_flag)
        if arguments.delete_old_files_flag:
            _logger.info("Deleting Old Files.")
            _delete_old_files(this_source_dir, this_dest_dir, arguments.exclude_suffixes_list)
