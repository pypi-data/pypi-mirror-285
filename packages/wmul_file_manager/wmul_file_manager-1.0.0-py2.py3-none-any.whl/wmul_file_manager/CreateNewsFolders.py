"""
@Author = 'Mike Stanley'
This script will create the news folders between two given dates and under the given folder.

E.G.
Start Date - 2023-01-23 
End Date - 2023-04-28
Folder - Z:/News/Packages, Sports & Weather/Spring 2023

It will create:
Z:/News/Packages, Sports & Weather/Spring 2023/01 - Monday/01-23
Z:/News/Packages, Sports & Weather/Spring 2023/02 - Tuesday/01-24
Z:/News/Packages, Sports & Weather/Spring 2023/03 - Wendesday/01-25
Z:/News/Packages, Sports & Weather/Spring 2023/04 - Thursday/01-26
Z:/News/Packages, Sports & Weather/Spring 2023/05 - Friday/01-27
...

Z:/News/Packages, Sports & Weather/Spring 2023/01 - Monday/04-24
Z:/News/Packages, Sports & Weather/Spring 2023/02 - Tuesday/04-25
Z:/News/Packages, Sports & Weather/Spring 2023/03 - Wendesday/04-26
Z:/News/Packages, Sports & Weather/Spring 2023/04 - Thursday/04-27
Z:/News/Packages, Sports & Weather/Spring 2023/05 - Friday/04-28

============ Change Log ============
2023-01-09 - Created

============ License ============
The MIT License (MIT)

Copyright (c) 2023-2024 Michael Stanley

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
from datetime import timedelta

import wmul_logger

logger = wmul_logger.get_logger()

CreateNewsFoldersArguments = namedtuple(
    "CreateNewsFoldersArguments",
    [
        "start_date",
        "end_date",
        "starting_folder"
    ]
)

def create_news_folders(start_date, end_date, starting_folder):
    if end_date < start_date:
        raise ValueError("End Date is before start date.")
    current_date = start_date
    one_day = timedelta(days=1)

    while current_date <= end_date:
        if current_date.isoweekday() < 6:
            this_dates_path = starting_folder / current_date.strftime("%w - %A/%m-%d")
            logger.info(f"Trying to creat {this_dates_path}")
            this_dates_path.mkdir(parents=True, exist_ok=True)
        current_date += one_day


def run_script(arguments):
    logger.info(f"In run_script with {arguments}")
    create_news_folders(arguments.start_date, arguments.end_date, arguments.starting_folder)
