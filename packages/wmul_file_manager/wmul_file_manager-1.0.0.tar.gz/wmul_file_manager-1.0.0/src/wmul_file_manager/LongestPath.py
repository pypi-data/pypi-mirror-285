"""
@Author = 'Mike Stanley'

Describe this file.

============ Change Log ============
6/13/2019 = Created.

============ License ============
The MIT License (MIT)

Copyright (c) 2019 Michael Stanley

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
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LongestPathAttrib:
    longest_length: int
    longest_files: list


def find_longest_path(path_under_test, lpa):
    for file_item in path_under_test.iterdir():
        if file_item.is_file():
            file_path_str = str(file_item)
            this_item_length = len(file_path_str)
            if this_item_length > lpa.longest_length:
                lpa.longest_length = this_item_length
                lpa.longest_files = [file_path_str]
            elif this_item_length == lpa.longest_length:
                lpa.longest_files.append(file_path_str)
        else:
            find_longest_path(file_item, lpa)


start_path = Path(r"Y:\Y Archive 2018-19")
attrib = LongestPathAttrib(0, [])
find_longest_path(start_path, attrib)
print(attrib.longest_length)
print(*attrib.longest_files, sep="\n")

