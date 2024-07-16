"""
Author: Michael Stanley

Utility functions dealing with directories.

============ Change Log ============
2018-May-01 = Import directory functions from Titanium_Monticello.Utilities.py
              Other parts of Titanium_Monticello.Utilities.py will be imported as other files.

2017-Aug-18 = Move the logger from Utilities to Logger.

2017-Aug-10 = Add logging to generate_equivalency_graph and empty_directory

              Re-write generate_equivalency_graph to use the zip method to convert the list into pairs.
              https://stackoverflow.com/questions/4628290/pairs-from-single-list

              Change logging format to include thread name for multi-threaded scripts.

2017-Aug-09 = Move logging management into this file.

              Make log_level an argument.

2017-Aug-01 = Move write_to_file_or_std_out from FolderComparer to Utilities.

2017-Jul-31 = Move _generate_equivalency_graph from EquivalentFileFinder to Utilities.

2015-Sep-08 = Created.

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
import wmul_logger
from wmul_file_manager.utilities.FileNamePrinter import object_cleaner

logger = wmul_logger.get_logger()


def purge_directory_contents(directory, delete_root=False):
    logger.debug(f"In purge_directory_contents with {locals()}")
    for file_item in directory.iterdir():
        logger.debug(f"In purge_directory_contents, working on {object_cleaner(file_item)}")
        if file_item.is_file():
            logger.debug("Is file")
            file_item.unlink()
        elif file_item.is_dir():
            logger.debug("Is directory")
            purge_directory_contents(file_item)
            file_item.rmdir()
    if delete_root:
        logger.debug("delete_root is true.")
        directory.rmdir()


def directory_is_empty(directory):
    return not any(directory.iterdir())
