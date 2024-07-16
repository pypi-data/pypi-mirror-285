"""
@Author = 'Mike Stanley'

This script will search within a given path and find all the top level folders that only have files older than the
    cutoff date.

E.G.: If you pass it Z:, and Z: contains
    Z:
    | - Adam
    | - Betty
    | - Carl

It will search each folder for new files. If Adam contains any files that are newer than the cutoff, Adam will be
    marked as new. The directory structure below the top level does not matter. Top level folders are considered new if
    they contain a new file anywhere within them. Otherwise they are old.

============ Change Log ============
2019-Jun-14 = Remove obsolete imports.

              Add ability to treat files with certain suffixes or names as "junk" and disregard their existence.

2018-May-15 = Renamed to FindOldDirectories.

              Add FindOldDirectoriesArguments namedtuple.

              Remove old command-line interface that was housed in this file and based on argparse.

2018-May-14 = Imported from Titanium_Monticello.PrintTopDirectoriesWithOnlyOldFiles

2017-Aug-18 = Move the logger from Utilities to Logger.

2017-Aug-17 = Replace text_cleaner(str()) calls with object_cleaner()

2017-Aug-14 = Refactor argparse.

              Re-write to use Utilities.logger.

2017-Jun-30 = Rewrite to use command-line args, a log file, and to output to a text file instead of printing to the
              console.

2017-May-10 = Imported from elsewhere.

============ License ============
The MIT License (MIT)

Copyright (c) 2017-2019, 2024 Michael Stanley

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
import datetime
from collections import namedtuple

import wmul_logger

from wmul_file_manager.DeleteJunkFiles import _file_is_junk
from wmul_file_manager.utilities.FileNamePrinter import object_cleaner
from wmul_file_manager.utilities import writer

logger = wmul_logger.get_logger()


def find_top_directories_with_only_old_files(first_path, recent_cutoff, junk_suffixes, junk_names):
    old_directories = []
    problem_directories = []
    for item_path in first_path.iterdir():
        if item_path.is_dir():
            if not directory_is_recent(item_path, problem_directories, recent_cutoff, junk_suffixes, junk_names):
                old_directories.append(item_path)

    problem_directories.sort()
    old_directories.sort()

    return problem_directories, old_directories


def directory_is_recent(this_directory, problem_directories, recent_cutoff, junk_suffixes, junk_names):
    logger.info(f"In directory_is_recent, checking: {object_cleaner(this_directory)}")
    try:
        for item in this_directory.iterdir():
            if item.is_file():
                if _file_is_junk(item, junk_suffixes, junk_names):
                    continue
                if file_is_recent(item, recent_cutoff):
                    logger.debug(f"{object_cleaner(item)} is recent.")
                    return True
            elif item.is_dir():
                if directory_is_recent(item, problem_directories, recent_cutoff, junk_suffixes, junk_names):
                    logger.debug(f"{object_cleaner(item)} is recent.")
                    return True
        return False
    except WindowsError as we:
        logger.info(str(we))
        problem_directories.append(this_directory)
        return True


def file_is_recent(this_file, recent_cutoff):
    logger.debug(f"In file_is_recent with: {object_cleaner(this_file)}")
    file_stats = this_file.stat()
    file_m_time = file_stats.st_mtime
    try:
        file_datetime = datetime.datetime.fromtimestamp(file_m_time)
        return file_datetime > recent_cutoff
    except OverflowError as OE:
        logger.info(f"Unable to parse timestamp on {object_cleaner(this_file)}")
        logger.debug((str(OE)))
        return True
    except OSError as OSE:
        logger.info(f"Unable to parse timestamp on {object_cleaner(this_file)}")
        logger.debug((str(OSE)))
        return True


def _write_results(result_writer, results):
    problem_directories, old_directories = results
    result_writer("Problem Directories")
    for directory in problem_directories:
        result_writer(str(directory))
    result_writer("========================================================================")
    result_writer("Old Directories")
    for directory in old_directories:
        result_writer(str(directory))


FindOldDirectoriesArguments = namedtuple(
    "FindOldDirectoriesArguments",
    [
        "first_path",
        "recent_cutoff",
        "junk_suffixes",
        "junk_names",
        "output_path"
    ]
)


def run_script(arguments):
    results = find_top_directories_with_only_old_files(
        arguments.first_path,
        arguments.recent_cutoff,
        arguments.junk_suffixes,
        arguments.junk_names
    )
    with writer.get_writer(arguments.output_path) as result_writer:
        _write_results(result_writer, results)
