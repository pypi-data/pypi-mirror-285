"""
@Author = 'Mike Stanley'

Describe this file.

============ Change Log ============
7/11/2018 = Created.

============ License ============
The MIT License (MIT)

Copyright (c) 2018 Michael Stanley

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

_dow_abbrev_to_dow_number = {
    "Mon": 0,
    "Tue": 1,
    "Wed": 2,
    "Thu": 3,
    "Fri": 4,
    "Sat": 5,
    "Sun": 6
}  # Numbers correspond to those returned by date.weekday().


def load_skimmer_calendar(expected_file_quantity_file_name):
    expected_file_quantity_by_day = {}
    with open(expected_file_quantity_file_name, mode="rt") as file_handler:
        for this_line in file_handler.readlines():
            _parse_expected_file_quantity_line(this_line, expected_file_quantity_by_day)
    if len(expected_file_quantity_by_day.keys()) != 7:
        raise ValueError(f"File does not contain data for every day of the week. The days of the week that are "
                         f"present are {expected_file_quantity_by_day.keys()}")
    return expected_file_quantity_by_day


def _parse_expected_file_quantity_line(this_line, expected_file_quantity_by_day):
    this_line = this_line.strip()
    if len(this_line) < 4:
        # Functionally blank line.
        return
    if this_line[0] == "#":
        # Lines starting with # are comments
        return

    dow, *expected_files_per_hour = this_line.split(",")

    if len(expected_files_per_hour) > 24:
        raise ValueError(f"{dow} has more than 24 hours listed in the config file.")

    expected_files_per_hour = [_convert_to_number(hour) for hour in expected_files_per_hour]
    while len(expected_files_per_hour) < 24:
        expected_files_per_hour.append(0)

    try:
        dow_number = _dow_abbrev_to_dow_number[dow]
    except KeyError:
        raise ValueError(f"{dow} is not a valid day-of-week. Valid days-of-week are {_dow_abbrev_to_dow_number.keys()}")
    expected_file_quantity_by_day[dow_number] = expected_files_per_hour


def _convert_to_number(hour):
    hour = hour.strip("\t")
    try:
        hour = int(hour)
    except ValueError:
        hour = 0
    return hour
