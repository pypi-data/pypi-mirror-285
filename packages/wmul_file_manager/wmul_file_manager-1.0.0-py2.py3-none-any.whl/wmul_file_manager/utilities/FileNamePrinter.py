"""
@Author = 'Mike Stanley'

Methods to print filenames that may have weird non-unicode character that python hates.

============ Change Log ============
2018-Apr-23 = Imported from Titanium_Monticello repo to this project.

2017-Sep-25 = Revert text_cleaner back to previous version.

2017-Aug-10 = Add object_cleaner to wrap an object in a str call before passing to text_cleaner.

2017-Jul-19 = Replaced text_cleaner with the bad_filename function from Python Cookbook.

2017-Jun-30 = text_cleaner now returns str instead of bytes.

2015-Jun-27 = Created.

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

_junk_bytes = bytes([num for num in range(128, 256)])
_question_marks = bytes([63 for num in range(128, 256)])
_bytes_translator = bytes.maketrans(_junk_bytes, _question_marks)


def clean_print(incoming_string):
    item_text = text_cleaner(incoming_string)
    print(item_text)


def text_cleaner(incoming_string):
    item_text = str(incoming_string).encode(encoding='cp1252', errors="replace")
    item_text = item_text.translate(_bytes_translator)
    return item_text.decode()


def object_cleaner(incoming_object):
    return text_cleaner(incoming_object)
