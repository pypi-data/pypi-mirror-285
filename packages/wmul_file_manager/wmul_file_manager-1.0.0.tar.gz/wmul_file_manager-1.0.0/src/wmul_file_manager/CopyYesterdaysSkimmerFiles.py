"""
@Author = 'Mike Stanley'

Script to copy yesterday's skimmer files. For each pair input, it looks for 
    yesterday's date directory under the source directory. The date folder must
     be in YYYY-MM-DD format. E.G. If today is 2018-May-16 and the source 
    folder is D:\\Skimmer\\, it will look for D:\\Skimmer\\2018-05-15.

It copies the files in the source date folder to the destination date folder. 
    E.G. The destination is U:\\Skimmer\\, it will copy to 
    U:\\Skimmer\\2018-05-15\\.

============ Change Log ============
2018-Jul-05 = Remove redundant trailing path separator from get_date_folder_name

2018-May-16 = Remove old command-line interface that was housed in this file and based on argparse.

2018-May-15 = Imported from Titanium_Monticello

2017-Aug-23 = Add --verbose option.

2017-Aug-18 = Move the logger from Utilities to Logger.

2017-Aug-11 = Add logging.

2017-Aug-08 = Imported into this package.

              Re-Write to use command-line arguments.

============ License ============
The MIT License (MIT)

Copyright (c) 2017-2018 Michael Stanley

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
from datetime import date, timedelta

from wmul_file_manager import BulkCopier
import wmul_logger

logger = wmul_logger.get_logger()


def _copy_folder(source_path, destination_path):
    if not source_path.exists():
        logger.debug(f"{source_path} does not exist, returning.")
        return
    arguments = BulkCopier.BulkCopierArguments(
        source_directories=[source_path],
        destination_directory=destination_path,
        exclude_suffixes_list=[],
        ignore_directories=[],
        force_copy_flag=False,
        delete_old_files_flag=False
    )
    logger.debug(f"Calling BulkCopier with {arguments}")
    BulkCopier.run_script(arguments=arguments)


def get_date_folder_name(source_base, relevant_date):
    path_date_stem = "{year:04d}-{month_Num:02d}-{day_num:02d}".format(
        year=relevant_date.year,
        month_Num=relevant_date.month,
        day_num=relevant_date.day
    )
    return source_base / path_date_stem


def run_script(source_destination_path_pairs):
    logger.debug("In run_script")
    logger.debug(f"with {source_destination_path_pairs}")
    relevant_date = date.today() - timedelta(days=1)

    for source_path, destination_path in source_destination_path_pairs:
        logger.debug(f"In run_script, working on {source_path} and {destination_path}")
        dated_source_path = get_date_folder_name(source_base=source_path, relevant_date=relevant_date)
        _copy_folder(source_path=dated_source_path, destination_path=destination_path)
