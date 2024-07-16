"""
@Author = 'Mike Stanley'

============ Change Log ============
2018-May-07 = Created.

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
from wmul_file_manager.utilities.writer import _WriteToFile, _write_to_std_out, get_writer
import io
import pytest


@pytest.fixture(scope="function")
def setup__write_to_file(tmpdir):
    output_file = tmpdir.join("tempfile.txt")
    writer = _WriteToFile(output_file)

    yield output_file, writer


def test__write_to_file_constructed_correctly(setup__write_to_file):
    output_file, writer = setup__write_to_file
    assert writer._file_name == output_file
    assert writer._file_descriptor is None
    assert not writer._file_is_open


def test__write_to_file_opens_file_correctly(setup__write_to_file):
    _, writer = setup__write_to_file
    writer.open_file()
    assert isinstance(writer._file_descriptor, io.TextIOBase)
    assert not writer._file_descriptor.closed
    assert writer._file_is_open


def test__write_to_file_closes_file_correctly(setup__write_to_file):
    _, writer = setup__write_to_file
    writer.open_file()
    assert writer._file_is_open
    writer.close_file()
    assert writer._file_descriptor.closed


def test__write_to_file_writes_one_line_correctly_already_open(setup__write_to_file):
    output_file, writer = setup__write_to_file
    test_text = "This is a test line of text"
    expected_text = "This is a test line of text\n"

    writer.open_file()
    writer.write(test_text)
    writer.close_file()

    file_text = output_file.read()
    assert file_text == expected_text


def test__write_to_file_writes_multiple_lines_correctly_already_open(setup__write_to_file):
    output_file, writer = setup__write_to_file
    test_text = [
        "1 This is a test line of text",
        "2 This is a test line of text",
        "3 This is a test line of text",
        "4 This is a test line of text"
    ]
    expected_text = "1 This is a test line of text\n2 This is a test line of text\n" \
                    "3 This is a test line of text\n4 This is a test line of text\n"

    writer.open_file()
    for line_of_text in test_text:
        writer.write(line_of_text)
    writer.close_file()

    file_text = output_file.read()
    assert file_text == expected_text


def test__write_to_file_writes_one_line_correctly_closed(setup__write_to_file):
    output_file, writer = setup__write_to_file
    test_text = "This is a test line of text"
    expected_text = "This is a test line of text\n"

    writer.write(test_text)

    file_text = output_file.read()
    assert file_text == expected_text
    assert not writer._file_is_open


def test__write_to_file_writes_multiple_lines_correctly_closed(setup__write_to_file):
    output_file, writer = setup__write_to_file
    test_text = [
        "1 This is a test line of text",
        "2 This is a test line of text",
        "3 This is a test line of text",
        "4 This is a test line of text"
    ]
    expected_text = "1 This is a test line of text\n2 This is a test line of text\n" \
                    "3 This is a test line of text\n4 This is a test line of text\n"

    for line_of_text in test_text:
        writer.write(line_of_text)

    file_text = output_file.read()
    assert file_text == expected_text
    assert not writer._file_is_open


def test__write_to_std_out_writes_one_line_correctly(capsys):
    test_text = "This is a test line of text"
    expected_text = "This is a test line of text\n"

    _write_to_std_out(test_text)

    stdout, err = capsys.readouterr()
    assert stdout == expected_text


def test__write_to_std_out_writes_multiple_lines_correctly(capsys):
    test_text = [
        "1 This is a test line of text",
        "2 This is a test line of text",
        "3 This is a test line of text",
        "4 This is a test line of text"
    ]
    expected_text = "1 This is a test line of text\n2 This is a test line of text\n" \
                    "3 This is a test line of text\n4 This is a test line of text\n"

    for line_of_text in test_text:
        _write_to_std_out(line_of_text)

    stdout, err = capsys.readouterr()
    assert stdout == expected_text


@pytest.fixture(scope="function", params=[True, False])
def setup_get_writer(tmpdir, request, capsys):
    using_file = request.param
    if using_file:
        output_file = tmpdir.join("tempfile.txt")
    else:
        output_file = None

    def get_file_text():
        return output_file.read()

    def get_stdout_text():
        stdout, err = capsys.readouterr()
        return stdout

    if using_file:
        get_text = get_file_text
    else:
        get_text = get_stdout_text

    single_test_text = "This is a test line of text"
    single_expected_text = "This is a test line of text\n"
    multiple_test_text = [
        "1 This is a test line of text",
        "2 This is a test line of text",
        "3 This is a test line of text",
        "4 This is a test line of text"
    ]
    multiple_expected_text = "1 This is a test line of text\n2 This is a test line of text\n" \
                             "3 This is a test line of text\n4 This is a test line of text\n"

    yield output_file, single_test_text, single_expected_text, multiple_test_text, multiple_expected_text, get_text


def test_get_writer_writes_one_line(setup_get_writer):
    output_file, single_test_text, single_expected_text, _, _, get_text = setup_get_writer

    with get_writer(file_name=output_file) as writer:
        writer(single_test_text)
    actual_text = get_text()
    assert actual_text == single_expected_text


def test_get_writer_writes_multiple_lines(setup_get_writer):
    output_file, _, _, multiple_test_text, multiple_expected_text, get_text = setup_get_writer

    with get_writer(file_name=output_file) as writer:
        for line_of_text in multiple_test_text:
            writer(line_of_text)
    actual_text = get_text()
    assert actual_text == multiple_expected_text


def test_get_writer_writes_multiple_lines_over_multiple_sessions(setup_get_writer):
    output_file, _, _, multiple_test_text, multiple_expected_text, get_text = setup_get_writer

    for line_of_text in multiple_test_text:
        with get_writer(file_name=output_file) as writer:
            writer(line_of_text)

    actual_text = get_text()
    assert actual_text == multiple_expected_text
