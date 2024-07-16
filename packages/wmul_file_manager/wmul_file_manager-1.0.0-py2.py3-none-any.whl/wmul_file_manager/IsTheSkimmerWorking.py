"""
@Author = 'Mike Stanley'

Run once per hour. Checks the provided folders for files corresponding to the previous hour's skimmer recordings.
  Emails the provided addresses if there was a problem.

============ Change Log ============
2023-May-08 = Add timezone argument.

2018-Jul-13 = Add the skimmer_calendar as an argument.

              Add expected_file_quantity to the _HourInformation tuple.

              Add logic to check the actual file quantity against the expected quantity.

2018-Jun-19 = Modify into a class.

              Removed old command-line interface that was housed in this file and based on argparse.

2018-Jun-18 = Imported from Titanium_Monticello

2017-Aug-24 = Added --verbose option.

2017-Aug-18 = Move the logger from Utilities to Logger.

2017-Aug-14 = Refactor argparse.

              Refactor to use f-strings.

              Rewrite to use Utilities.logger.

2017-Jun-27 = Added the number and names of files that were found when there is an error.
                  Refactor to use Emailer.py

2016-Apr-21 = Add logging.

              Add ability to e-mail multiple addresses.

2016-Apr-19 = Initial Version.

============ License ============
The MIT License (MIT)

Copyright (c) 2016-2018, 2023-2024 Michael Stanley

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
from collections import namedtuple
from datetime import datetime, timedelta
import wmul_logger


logger = wmul_logger.get_logger()

_HourInformation = namedtuple(
    "_HourInformation",
    [
        "date_directory",
        "matching_filename_regex",
        "expected_file_quantity"
    ]
)


class IsTheSkimmerWorking:

    def __init__(self, emailer, _skimmer_calendar, timezone):
        self.emailer = emailer
        self.problems = []
        last_hour_information = _get_last_hour_information(_skimmer_calendar, timezone)
        self.date_directory = last_hour_information.date_directory
        self.matching_filename_regex = last_hour_information.matching_filename_regex
        self.expected_file_quantity = last_hour_information.expected_file_quantity

    def run_script(self, directory_list):
        logger.debug(f"In is_the_skimmer_working, with {directory_list}")
        for this_directory in directory_list:
            directory_of_previous_hour = this_directory / self.date_directory
            self._is_the_skimmer_working_on_this_directory(directory_of_previous_hour)
        if self.problems:
            self._send_alert_email()

    def _is_the_skimmer_working_on_this_directory(self, directory_of_previous_hour):
        logger.debug(f"Checking {directory_of_previous_hour}")
        if not self._check_existance_of_directory_of_previous_hour(directory_of_previous_hour):
            return
        files_of_previous_hour = self._collect_files_of_previous_hour(directory_of_previous_hour)
        logger.debug(f"Found files: {files_of_previous_hour}")
        self._does_previous_hour_have_correct_number_of_files(files_of_previous_hour, directory_of_previous_hour)

    def _check_existance_of_directory_of_previous_hour(self, directory_of_previous_hour):
        if directory_of_previous_hour.is_dir():
            logger.info(f"{directory_of_previous_hour} exists.")
            return True
        else:
            error_message = f"{directory_of_previous_hour} is not a folder."
            logger.warning(error_message)
            self.problems.append(error_message)
            return False

    def _does_previous_hour_have_correct_number_of_files(self, files_of_previous_hour, directory_of_previous_hour):
        number_of_files_of_previous_hour = len(files_of_previous_hour)
        if number_of_files_of_previous_hour == self.expected_file_quantity:
            logger.info(f"Folder {directory_of_previous_hour} has the correct number of files.")
        else:
            error_message = f"Folder {directory_of_previous_hour} does not have the correct number of files. " \
                            f"Should have {self.expected_file_quantity}, has {number_of_files_of_previous_hour}."
            logger.warning(error_message)
            self.problems.append(error_message)
            self.problems.extend([str(file) for file in files_of_previous_hour])

    def _collect_files_of_previous_hour(self, directory_of_previous_hour):
        return [this_file for this_file in directory_of_previous_hour.iterdir()
                if self._file_is_for_hour_under_test(this_file)]

    def _file_is_for_hour_under_test(self, filename):
        logger.debug(f"In _file_is_for_hour_under_test with: {filename}")
        return self.matching_filename_regex.search(filename.stem)

    def _send_alert_email(self):
        logger.debug(f"In _send_alert_email")
        email_subject = "[Skimmer] Skimmer failure!"
        email_body = "The skimmer failed during the previous hour.\n" + "\n".join(self.problems)

        self.emailer.send_email(
            email_body=email_body,
            email_subject=email_subject,
        )


def _get_last_hour_information(_skimmer_calendar, timezone):
    previous_hour = datetime.now(timezone) - timedelta(hours=1)
    date_directory = f"{previous_hour.year:04d}-{previous_hour.month:02d}-{previous_hour.day:02d}"
    logger.debug(f"Computed date_folder: {date_directory}")

    hour_under_test = f"{previous_hour.year:04d}-{previous_hour.month:02d}-" \
                      f"{previous_hour.day:02d}_{previous_hour.hour:02d}"
    matching_filename_regex = re.compile(hour_under_test + r"-[0-9]{2}-[0-9]{2}-[0-9]{3}")
    logger.debug(f"Computed matching_filename_regex: {matching_filename_regex}")

    the_days_expected_file_quantity = _skimmer_calendar[previous_hour.weekday()]
    previous_hours_expected_file_quantity = the_days_expected_file_quantity[previous_hour.hour]
    logger.debug(f"Previous Hour's Expected File Quantity: {previous_hours_expected_file_quantity}")
    return _HourInformation(
        date_directory=date_directory,
        matching_filename_regex=matching_filename_regex,
        expected_file_quantity=previous_hours_expected_file_quantity
    )
