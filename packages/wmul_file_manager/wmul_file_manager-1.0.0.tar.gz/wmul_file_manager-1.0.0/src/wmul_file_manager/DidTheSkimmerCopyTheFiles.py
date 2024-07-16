"""
@Author: Michael Stanley

Checks the provided folders and makes certain that yesterday's skimmer files were copied to that location.

============ Change Log ============
2018-Jul-13 = Rewrite such that the calendar is loaded externally and passed into this class. Previously a filename was
              passed in and loaded by this class.

2018-Jul-11 = Extract the skimmer calendar subsystem into its own file.

2018-Jun-13 = Add in functionality for each hour to have its own count of how many files should be created.

2018-Jun-12 = Refactor to a class.

2018-May-24 = Renamed DidTheSkimmerCopyTheFiles to DidTheSkimmerCopyTheFilesArguments.

              Removed old command-line interface that was housed in this file and based on argparse.

2018-May-18 = Imported from Titanium_Monticello.

2017-Aug-24 = Added --verbose option.

2017-Aug-18 = Move the logger from Utilities to Logger.

2017-Aug-11 = Refactor argparse.

              Add logging.

              Create a method to act as an external entry point for this script.

              Create a named tuple to encapsulate the arguments to run_script. Modify _run_from_command_line to
                use the new named tuple.

              Reformat e-mail messages to match log entries.

2017-Jun-27 = Added the directory listings of the directories that had problems.

              Modified it so that it sends only one e-mail, no matter the number of folders affected.

              Refactor to use Emailer.py

              BUGFIX: Check that folders exist using .exists() instead of .is_dir()

2016-Apr-21 = Make log filename a command-line option.

              Allow multiple destination e-mail addresses.

2016-Apr-19 = Created.

============ License ============
The MIT License (MIT)

Copyright (c) 2016-2018 Michael Stanley

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
import re
from collections import defaultdict, namedtuple
from datetime import datetime, timedelta

import wmul_logger
from wmul_file_manager.utilities.FileNamePrinter import object_cleaner
from wmul_file_manager import CopyYesterdaysSkimmerFiles

_logger = wmul_logger.get_logger()


class DidTheSkimmerCopyTheFiles:

    def __init__(self, directories, _skimmer_calendar, emailer):
        self.directories = directories
        self.emailer = emailer
        self.problems = []
        self._skimmer_calendar = _skimmer_calendar

    def __str__(self):
        return f"DidTheSkimmerCopyTheFiles: directories: {self.directories}, " \
               f"emailer: {self.emailer}, problems: {self.problems}, calendar: {self._skimmer_calendar}"

    def run_script(self):
        _logger.debug(f"In DidTheSkimmerCopyTheFiles.run_script with {self}")
        self.problems = []
        for this_directory in self.directories:
            _logger.debug(f"In run_script, working on {object_cleaner(this_directory)}")
            self._did_the_skimmer_copy_the_files_for_this_folder(this_directory)
        if self.problems:
            _logger.warning(f"There were problems, e-mailing.")
            self._send_alert_email()

    def _did_the_skimmer_copy_the_files_for_this_folder(self, base_directory):
        _logger.info(f"In did_the_skimmer_copy_the_files, with: {base_directory}")
        yesterday_information = self._get_yesterdays_information(base_directory)
        if yesterday_information.directory.exists():
            _logger.debug("Yesterday's directory does exist.")
            self._check_count_of_files_in_yesterdays_directory(yesterday_information)
        else:
            _logger.warning("Yesterday's directory does not exist.")
            self.problems.append(f"Yesterday's directory does not exist: {yesterday_information.directory}")

    def _get_yesterdays_information(self, base_directory):
        yesterday = datetime.today() - timedelta(days=1)
        _logger.info(f"Yesterday: {yesterday}")

        expected_file_quantity = self._skimmer_calendar[yesterday.weekday()]

        yesterday_directory = CopyYesterdaysSkimmerFiles.get_date_folder_name(base_directory, yesterday)
        _logger.debug(f"Yesterday's path: {yesterday_directory}")

        yesterday_information = _YesterdayInformation(
            directory=yesterday_directory,
            expected_file_quantity=expected_file_quantity
        )

        return yesterday_information

    def _check_count_of_files_in_yesterdays_directory(self, yesterday_information):
        files_in_each_hour = defaultdict(list)
        regex_pattern = r"[0-9]{4}-[0-9]{2}-[0-9]{2}_(?P<hour>[0-9]{2})-[0-9]{2}-[0-9]{2}-[0-9]{3}"
        regex_hour = re.compile(regex_pattern)
        for this_file in yesterday_information.directory.iterdir():
            regex_match = regex_hour.search(str(this_file))
            this_files_hour = int(regex_match.group("hour"))
            files_in_each_hour[this_files_hour].append(this_file)

        for this_hour, expected_quantity in enumerate(yesterday_information.expected_file_quantity):
            number_of_files_this_hour = len(files_in_each_hour[this_hour])
            if number_of_files_this_hour == expected_quantity:
                _logger.info(f"Correct number of files for hour {this_hour} in: {yesterday_information.directory}")
            else:
                error_message = f"Incorrect number of files for hour {this_hour} in: " \
                                f"{yesterday_information.directory}\n" \
                                f"Should have {expected_quantity}, " \
                                f"has {number_of_files_this_hour}"
                _logger.warning(error_message)
                self.problems.append(error_message + "\n")
                self.problems.extend([str(this_file) for this_file in files_in_each_hour[this_hour]])

    def _send_alert_email(self):
        _logger.debug(f"In _send_alert_email with {self}")
        email_subject = "[Skimmer] Skimmer copy failure!"
        email_body = "\n".join(self.problems)

        self.emailer.send_email(
            email_body=email_body,
            email_subject=email_subject,
        )


_YesterdayInformation = namedtuple(
    "_YesterdayInformation",
    [
        "directory",
        "expected_file_quantity",
    ]
)
