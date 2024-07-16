"""
@Author = 'Mike Stanley'

System to write text either to a file or to standard out.

Context manager get_writer takes an optional file name and an append option.

If a name is given, it manages opening and closing the file and returns a method to write to the file.
    The file is opened in append mode by default. If `append=False`, then the file will be truncated. 
    Text sent to the file output method will have a newline appended to it with each call.

If no name is given, it returns a method that passes along to the print method.

Both the file output and the standard output method use the api method("Text").

Usage:

with get_writer(file_name="file.txt") as writer:
    writer("Output Text")

file.txt will now include the line:
Output Text\n


with get_writer() as writer:
    writer("Output Text")

The text will be sent to standard out. The print command automatically includes a newline, therefore the method will
    not add a redundant one.

============ Change Log ============
2024-May-08 = Make get_writer use the append option.

2018-May-08 = Completely re-wrote write_to_file_or_std_out into a more robust system.

2018-May-07 = Imported write_to_file_or_std_out from Titanium_Monticello.Utilities

2018-May-07 = Created.

============ License ============
The MIT License (MIT)

Copyright (c) 2018, 2024 Michael Stanley

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
import contextlib


class _WriteToFile:

    def __init__(self, file_name, append=True):
        self._file_name = file_name
        self._file_descriptor = None
        self._file_is_open = False
        if append:
            self._open_mode = "at"
        else:
            self._open_mode = "wt"

    def open_file(self):
        self._file_descriptor = open(self._file_name, self._open_mode)
        self._file_is_open = True

    def write(self, data):
        file_was_open = self._file_is_open
        if not self._file_is_open:
            self.open_file()
        self._file_descriptor.write(data + "\n")
        if not file_was_open:
            self.close_file()

    def close_file(self):
        self._file_descriptor.close()
        self._file_is_open = False


def _write_to_std_out(data):
    print(data)


@contextlib.contextmanager
def get_writer(file_name=None, append=True):
    if file_name:
        writer = _WriteToFile(file_name=file_name, append=append)
        writer.open_file()
        yield writer.write
        writer.close_file()
    else:
        yield _write_to_std_out

