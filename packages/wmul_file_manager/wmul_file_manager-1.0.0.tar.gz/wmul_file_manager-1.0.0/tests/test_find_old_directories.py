"""
@Author = 'Mike Stanley'

============ Change Log ============
2018-May-14 = Created.

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
import contextlib
import datetime
import itertools
import pathlib
import pytest

from wmul_file_manager import FindOldDirectories


@pytest.fixture(scope="function")
def setup_file_is_recent(fs):
    mock_file = pathlib.Path("foo.txt")
    fs.create_file(mock_file)
    cutoff = datetime.datetime(year=2017, month=9, day=30, hour=23, minute=59, second=59)
    yield mock_file, cutoff


def test_file_is_recent_it_is(mocker, setup_file_is_recent):
    mock_file, cutoff = setup_file_is_recent

    expected_mtime = 1514826000.0  # 2018-January-01, Noon
    mock_file.stat = mocker.Mock(return_value=mocker.Mock(st_mtime=expected_mtime))

    assert FindOldDirectories.file_is_recent(mock_file, cutoff)


def test_file_is_recent_it_is_not(mocker, setup_file_is_recent):
    mock_file, cutoff = setup_file_is_recent

    expected_mtime = 1494777600.0  # 2017-May-14, Noon
    mock_file.stat = mocker.Mock(return_value=mocker.Mock(st_mtime=expected_mtime))

    assert not FindOldDirectories.file_is_recent(mock_file, cutoff)


def test_file_is_recent_value_error(mocker, caplog, setup_file_is_recent):
    mock_file, cutoff = setup_file_is_recent

    expected_mtime = 100_000_000_000  # Will trip an OSError when datetime tries to parse it.
    mock_file.stat = mocker.Mock(return_value=mocker.Mock(st_mtime=expected_mtime))

    assert FindOldDirectories.file_is_recent(mock_file, cutoff)
    assert "Unable to parse timestamp on " in caplog.text


@pytest.fixture(scope="function")
def setup__directory_is_recent(fs):
    root_dir = pathlib.Path("foo")
    fs.create_dir(root_dir)
    sub_dir = root_dir / "sub_dir"
    fs.create_dir(sub_dir)

    w_file = root_dir / "file1.txtW"
    x_file = root_dir / "file2.txtX"
    y_file = sub_dir / "file3.txtY"
    z_file = sub_dir / "file4.txtZ"

    file_tree = [
        w_file,
        x_file,
        y_file,
        z_file
    ]

    for file_item in file_tree:
        fs.create_file(file_item)

    mock_recent_cutoff = "mock_recent_cutoff"
    mock_junk_suffixes = "mock_junk_suffixes"
    mock_junk_names = "mock_junk_names"

    problem_directories = []

    return locals()


def test__directory_is_recent_subdir_is(setup__directory_is_recent, mocker):
    root_dir = setup__directory_is_recent["root_dir"]
    problem_directories = setup__directory_is_recent["problem_directories"]
    mock_recent_cutoff = setup__directory_is_recent["mock_recent_cutoff"]
    mock_junk_suffixes = setup__directory_is_recent["mock_junk_suffixes"]
    mock_junk_names = setup__directory_is_recent["mock_junk_names"]
    z_file = setup__directory_is_recent["z_file"]

    def mock_file_is_recent_function(this_file, recent_cutoff):
        file_str = str(this_file)
        return file_str[-1] == "Z"

    mock_file_is_recent = mocker.patch(
        "wmul_file_manager.FindOldDirectories.file_is_recent",
        mocker.Mock(side_effect=mock_file_is_recent_function)
    )

    def mock_file_is_junk_function(this_file, junk_suffixes, junk_names):
        return False

    mock_file_is_junk = mocker.patch(
        "wmul_file_manager.FindOldDirectories._file_is_junk",
        mocker.Mock(side_effect=mock_file_is_junk_function)
    )

    dir_is_recent = FindOldDirectories.directory_is_recent(
        root_dir,
        problem_directories,
        mock_recent_cutoff,
        mock_junk_suffixes,
        mock_junk_names
    )

    assert dir_is_recent
    mock_file_is_recent.assert_any_call(z_file, mock_recent_cutoff)
    mock_file_is_junk.assert_any_call(z_file, mock_junk_suffixes, mock_junk_names)


def test__directory_is_recent_main_dir_is(setup__directory_is_recent, mocker):
    root_dir = setup__directory_is_recent["root_dir"]
    problem_directories = setup__directory_is_recent["problem_directories"]
    mock_recent_cutoff = setup__directory_is_recent["mock_recent_cutoff"]
    mock_junk_suffixes = setup__directory_is_recent["mock_junk_suffixes"]
    mock_junk_names = setup__directory_is_recent["mock_junk_names"]
    x_file = setup__directory_is_recent["x_file"]

    def mock_file_is_recent_function(this_file, recent_cutoff):
        file_str = str(this_file)
        return file_str[-1] == "X"

    mock_file_is_recent = mocker.patch(
        "wmul_file_manager.FindOldDirectories.file_is_recent",
        mocker.Mock(side_effect=mock_file_is_recent_function)
    )

    def mock_file_is_junk_function(this_file, junk_suffixes, junk_names):
        return False

    mock_file_is_junk = mocker.patch(
        "wmul_file_manager.FindOldDirectories._file_is_junk",
        mocker.Mock(side_effect=mock_file_is_junk_function)
    )

    dir_is_recent = FindOldDirectories.directory_is_recent(
        root_dir,
        problem_directories,
        mock_recent_cutoff,
        mock_junk_suffixes,
        mock_junk_names
    )

    assert dir_is_recent
    mock_file_is_recent.assert_any_call(x_file, mock_recent_cutoff)
    mock_file_is_junk.assert_any_call(x_file, mock_junk_suffixes, mock_junk_names)


def test__directory_is_recent_it_is_not(setup__directory_is_recent, mocker):
    root_dir = setup__directory_is_recent["root_dir"]
    problem_directories = setup__directory_is_recent["problem_directories"]
    mock_recent_cutoff = setup__directory_is_recent["mock_recent_cutoff"]
    mock_junk_suffixes = setup__directory_is_recent["mock_junk_suffixes"]
    mock_junk_names = setup__directory_is_recent["mock_junk_names"]
    w_file = setup__directory_is_recent["w_file"]
    x_file = setup__directory_is_recent["x_file"]
    y_file = setup__directory_is_recent["y_file"]
    z_file = setup__directory_is_recent["z_file"]

    def mock_file_is_recent_function(this_file, recent_cutoff):
        return False

    mock_file_is_recent = mocker.patch(
        "wmul_file_manager.FindOldDirectories.file_is_recent",
        mocker.Mock(side_effect=mock_file_is_recent_function)
    )

    def mock_file_is_junk_function(this_file, junk_suffixes, junk_names):
        return False

    mock_file_is_junk = mocker.patch(
        "wmul_file_manager.FindOldDirectories._file_is_junk",
        mocker.Mock(side_effect=mock_file_is_junk_function)
    )

    dir_is_recent = FindOldDirectories.directory_is_recent(
        root_dir,
        problem_directories,
        mock_recent_cutoff,
        mock_junk_suffixes,
        mock_junk_names
    )

    assert not dir_is_recent

    expected_calls = [
        mocker.call(w_file, mock_recent_cutoff),
        mocker.call(x_file, mock_recent_cutoff),
        mocker.call(y_file, mock_recent_cutoff),
        mocker.call(z_file, mock_recent_cutoff)
    ]

    mock_file_is_recent.assert_has_calls(expected_calls, any_order=True)
    assert mock_file_is_recent.call_count == 4


def test__directory_is_recent_windows_error(setup__directory_is_recent, mocker):
    root_dir = setup__directory_is_recent["root_dir"]
    problem_directories = setup__directory_is_recent["problem_directories"]
    mock_recent_cutoff = setup__directory_is_recent["mock_recent_cutoff"]
    mock_junk_suffixes = setup__directory_is_recent["mock_junk_suffixes"]
    mock_junk_names = setup__directory_is_recent["mock_junk_names"]
    sub_dir = setup__directory_is_recent["sub_dir"]

    def mock_file_is_recent_function(this_file, recent_cutof):
        raise WindowsError("Fake Windows Error")

    mock_file_is_recent = mocker.patch(
        "wmul_file_manager.FindOldDirectories.file_is_recent",
        mocker.Mock(side_effect=mock_file_is_recent_function)
    )

    def mock_file_is_junk_function(this_file, junk_suffixes, junk_names):
        return False

    mock_file_is_junk = mocker.patch(
        "wmul_file_manager.FindOldDirectories._file_is_junk",
        mocker.Mock(side_effect=mock_file_is_junk_function)
    )

    dir_is_recent = FindOldDirectories.directory_is_recent(
        root_dir,
        problem_directories,
        mock_recent_cutoff,
        mock_junk_suffixes,
        mock_junk_names
    )

    assert dir_is_recent
    assert (root_dir in problem_directories or sub_dir in problem_directories)


@pytest.fixture(scope="function")
def setup__find_top_directories(mocker, fs):
    root_dir = pathlib.Path("foo")

    expected_old = [
        root_dir / "appleX",
        root_dir / "gingerbreadX",
        root_dir / "donutX",
        root_dir / "marshmallowX",
        root_dir / "jellybeanX"
    ]

    expected_new = [
        root_dir / "bananaY",
        root_dir / "honeycombY",
        root_dir / "nougatY",
        root_dir / "kitkatY",
        root_dir / "eclairY"
    ]

    expected_problem = [
        root_dir / "cupcakeZ",
        root_dir / "icecreamsandwichZ",
        root_dir / "oreoZ",
        root_dir / "lollypopZ",
        root_dir / "froyoZ"
    ]

    mock_junk_suffixes = "mock_junk_suffixes"
    mock_junk_names = "mock_junk_names"

    for dir_item in itertools.chain(expected_old, expected_new, expected_problem):
        fs.create_dir(dir_item)

    def mock_directory_is_recent_function(directory, problem_directories, recent_cutoff, junk_suffixes, junk_names):
        dir_str = str(directory)
        last_letter = dir_str[-1]
        if last_letter == "X":
            return False
        elif last_letter == "Y":
            return True
        else:
            problem_directories.append(directory)
            return True

    mock_directory_is_recent = mocker.patch(
        "wmul_file_manager.FindOldDirectories.directory_is_recent",
        mocker.Mock(side_effect=mock_directory_is_recent_function)
    )

    mock_recent_cutoff = "mock_recent_cutoff"

    result_problem_directories, result_old_directories = FindOldDirectories\
        .find_top_directories_with_only_old_files(root_dir, mock_recent_cutoff, mock_junk_suffixes, mock_junk_names)

    return locals()


def test_find_top_directories_directory_is_recent_called_correctly(setup__find_top_directories, mocker):
    expected_old = setup__find_top_directories["expected_old"]
    expected_new = setup__find_top_directories["expected_new"]
    expected_problem = setup__find_top_directories["expected_problem"]
    result_problem_directories = setup__find_top_directories["result_problem_directories"]
    mock_recent_cutoff = setup__find_top_directories["mock_recent_cutoff"]
    mock_directory_is_recent = setup__find_top_directories["mock_directory_is_recent"]
    mock_junk_suffixes = setup__find_top_directories["mock_junk_suffixes"]
    mock_junk_names = setup__find_top_directories["mock_junk_names"]

    expected_calls = []

    for dir_item in itertools.chain(expected_old, expected_new, expected_problem):
        expected_calls.append(mocker.call(dir_item, result_problem_directories, mock_recent_cutoff, mock_junk_suffixes, mock_junk_names))

    mock_directory_is_recent.assert_has_calls(expected_calls, any_order=True)
    assert mock_directory_is_recent.call_count == len(expected_calls)


def test_find_top_directories_correct_problem_directories(setup__find_top_directories):
    expected_problem = setup__find_top_directories["expected_problem"]
    result_problem_directories = setup__find_top_directories["result_problem_directories"]

    expected_problem_sorted = sorted(expected_problem)
    assert result_problem_directories == expected_problem_sorted


def test_find_top_directories_correct_old_directories(setup__find_top_directories):
    expected_old = setup__find_top_directories["expected_old"]
    result_old_directories = setup__find_top_directories["result_old_directories"]

    expected_old_sorted = sorted(expected_old)
    assert result_old_directories == expected_old_sorted


def test_find_top_directories_new_directories_properly_excluded(setup__find_top_directories):
    expected_new = setup__find_top_directories["expected_new"]
    result_problem_directories = setup__find_top_directories["result_problem_directories"]
    result_old_directories = setup__find_top_directories["result_old_directories"]

    for dir_item in expected_new:
        assert dir_item not in result_problem_directories
        assert dir_item not in result_old_directories


def test__write_results():
    received_writes = []

    def mock_result_writer(data):
        received_writes.append(data)

    problem_dirs = [
        "appleX",
        "gingerbreadX",
        "donutX",
        "marshmallowX",
        "jellybeanX"
    ]

    old_dirs = [
        "bananaY",
        "honeycombY",
        "nougatY",
        "kitkatY",
        "eclairY"
    ]

    expected_writes = [
        "Problem Directories",
        "appleX",
        "gingerbreadX",
        "donutX",
        "marshmallowX",
        "jellybeanX",
        "========================================================================",
        "Old Directories",
        "bananaY",
        "honeycombY",
        "nougatY",
        "kitkatY",
        "eclairY"
    ]

    results = (problem_dirs, old_dirs)

    FindOldDirectories._write_results(mock_result_writer, results)

    assert received_writes == expected_writes


@pytest.fixture(scope="function")
def setup__run_script(mocker):
    mock_results = "mock_results"
    mock_find_top = mocker.patch(
        "wmul_file_manager.FindOldDirectories.find_top_directories_with_only_old_files",
        mocker.Mock(return_value=mock_results)
    )

    mock_writer = mocker.Mock()

    @contextlib.contextmanager
    def mock_writer_function(file_name):
        yield mock_writer

    mock_get_writer = mocker.patch(
        "wmul_file_manager.utilities.writer.get_writer",
        mocker.Mock(side_effect=mock_writer_function)
    )

    mock_write_results = mocker.patch("wmul_file_manager.FindOldDirectories._write_results")

    mock_first_path = "mock_first_path"
    mock_recent_cutoff = "mock_recent_cutoff"
    mock_junk_suffixes = "mock_junk_suffixes"
    mock_junk_names = "mock_junk_names"
    mock_output_path = "mock_output_path"

    mock_arguments = mocker.Mock(
        first_path=mock_first_path,
        recent_cutoff=mock_recent_cutoff,
        junk_suffixes=mock_junk_suffixes,
        junk_names=mock_junk_names,
        output_path=mock_output_path
    )

    FindOldDirectories.run_script(mock_arguments)

    return locals()


def test_run_script_find_top_called_correctly(setup__run_script):
    mock_find_top = setup__run_script["mock_find_top"]
    mock_first_path = setup__run_script["mock_first_path"]
    mock_recent_cutoff = setup__run_script["mock_recent_cutoff"]
    mock_junk_suffixes = setup__run_script["mock_junk_suffixes"]
    mock_junk_names = setup__run_script["mock_junk_names"]

    mock_find_top.assert_called_once_with(mock_first_path, mock_recent_cutoff, mock_junk_suffixes, mock_junk_names)


def test_run_script_get_writer_called_correctly(setup__run_script):
    mock_get_writer = setup__run_script["mock_get_writer"]
    mock_output_path = setup__run_script["mock_output_path"]

    mock_get_writer.assert_called_once_with(mock_output_path)


def test_run_script_write_results_called_correctly(setup__run_script):
    mock_write_results = setup__run_script["mock_write_results"]
    mock_writer = setup__run_script["mock_writer"]
    mock_results = setup__run_script["mock_results"]

    mock_write_results.assert_called_once_with(mock_writer, mock_results)
