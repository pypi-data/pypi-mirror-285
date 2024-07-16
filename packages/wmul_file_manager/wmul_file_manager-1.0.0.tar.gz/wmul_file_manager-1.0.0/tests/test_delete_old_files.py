"""
@Author = 'Mike Stanley'

============ Change Log ============
2024-May-03 = Updated datetimes to use UTC.

2018-May-16 = Created.

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
import datetime
import pathlib
import pytest
from collections import namedtuple
from wmul_file_manager import DeleteOldFiles


def generate_binary_matrix_from_named_tuple(input_tuple):
    number_of_args = len(input_tuple._fields)
    powers_of_two = {2**i: i for i in range(number_of_args)}
    these_args = []
    for i in range(number_of_args):
        these_args.append(False)

    collected_test_args = []

    for i in range(1, 2**number_of_args + 1):
        this_test_arg = input_tuple._make(these_args)
        collected_test_args.append(this_test_arg)

        for this_power_of_two, corresponding_index in powers_of_two.items():
            if i % this_power_of_two == 0:
                these_args[corresponding_index] = not these_args[corresponding_index]

    return collected_test_args


purge_old_files_test_options = namedtuple(
    "purge_old_files_test_options",
    [
        "use_remove_folders",
        "directory_is_empty"
    ]
)


@pytest.fixture(scope="function", params=generate_binary_matrix_from_named_tuple(purge_old_files_test_options))
def setup__purge_old_files(mocker, tmpdir, request):
    params = request.param

    mock_delete_old_files = mocker.patch("wmul_file_manager.DeleteOldFiles.delete_old_files")
    mock_directory_is_empty = mocker.patch(
        "wmul_file_manager.utilities.directories.directory_is_empty",
        mocker.Mock(return_value=params.directory_is_empty)
    )

    this_directory = tmpdir.join("this_dir")
    this_directory.ensure(dir=True)
    this_directory = pathlib.Path(this_directory)

    mock_arguments = mocker.Mock(
        remove_folders_flag=params.use_remove_folders
    )

    DeleteOldFiles._purge_old_files_from_directory(
        this_directory=this_directory,
        arguments=mock_arguments
    )

    yield params, mock_delete_old_files, mock_directory_is_empty, this_directory, mock_arguments


@pytest.mark.delete_old
def test__purge_old_files_delete_called_correctly(setup__purge_old_files):
    params, mock_delete_old_files, mock_directory_is_empty, this_directory, mock_arguments = setup__purge_old_files

    mock_delete_old_files.assert_called_once_with(this_directory, mock_arguments)


@pytest.mark.delete_old
def test__purge_old_files_directory_is_empty_called_correctly(setup__purge_old_files):
    params, mock_delete_old_files, mock_directory_is_empty, this_directory, mock_arguments = setup__purge_old_files

    if params.use_remove_folders:
        mock_directory_is_empty.assert_called_once_with(this_directory)
    else:
        mock_directory_is_empty.assert_not_called()


@pytest.mark.delete_old
def test__purge_old_files_directory_handled_correctly(setup__purge_old_files):
    params, mock_delete_old_files, mock_directory_is_empty, this_directory, mock_arguments = setup__purge_old_files

    if params.directory_is_empty and params.use_remove_folders:
        assert not this_directory.exists()
    else:
        assert this_directory.exists()


@pytest.fixture(scope="function")
def setup__file_is_older(fs, mocker):
    this_file = pathlib.Path("foo")
    fs.create_file(this_file)
    expected_mtime = 1514826000.0  # 2018-January-01, Noon
    this_file.stat = mocker.Mock(return_value=mocker.Mock(st_mtime=expected_mtime))
    yield this_file


@pytest.mark.delete_old
def test__file_is_older__is(setup__file_is_older):
    this_file = setup__file_is_older
    older_than = datetime.datetime(year=2018, month=5, day=1, hour=12, tzinfo=datetime.timezone.utc)
    assert DeleteOldFiles._file_is_older(older_than=older_than, this_file=this_file)


@pytest.mark.delete_old
def test__file_is_older__is_not(setup__file_is_older):
    this_file = setup__file_is_older
    older_than = datetime.datetime(year=2017, month=5, day=1, hour=12, tzinfo=datetime.timezone.utc)
    assert not DeleteOldFiles._file_is_older(older_than=older_than, this_file=this_file)


@pytest.mark.delete_old
def test__file_is_older__is_equal(setup__file_is_older):
    this_file = setup__file_is_older
    older_than = datetime.datetime(year=2018, month=1, day=1, hour=12, tzinfo=datetime.timezone.utc)
    assert not DeleteOldFiles._file_is_older(older_than=older_than, this_file=this_file)


check_and_delete_test_options = namedtuple(
    "check_and_delete_test_options",
    [
        "use_limited_suffixes",
        "suffix_is_in_limited_list",
        "file_is_older"
    ]
)


@pytest.fixture(scope="function", params=generate_binary_matrix_from_named_tuple(check_and_delete_test_options))
def setup__check_and_delete(fs, mocker, request, caplog):
    params = request.param
    mock_file_is_older = mocker.patch(
        "wmul_file_manager.DeleteOldFiles._file_is_older",
        mocker.Mock(return_value=params.file_is_older)
    )

    this_file = pathlib.Path("foo.txt")
    fs.create_file(this_file)

    if params.suffix_is_in_limited_list:
        limited_suffix_list = [".txt", ".wav"]
    else:
        limited_suffix_list = [".wav"]

    mock_older_than = "mock_older_than"

    mock_arguments = mocker.Mock(
        limited_suffixes_flag=params.use_limited_suffixes,
        limited_suffixes_list=limited_suffix_list,
        older_than=mock_older_than
    )

    DeleteOldFiles._check_and_delete_old_file(this_file=this_file, arguments=mock_arguments)

    yield params, mock_file_is_older, this_file, mock_arguments, mock_older_than, caplog.text


@pytest.mark.delete_old
def test__check_and_delete_file_is_older_called_correctly(setup__check_and_delete):
    params, mock_file_is_older, this_file, mock_arguments, mock_older_than, caplog_text = setup__check_and_delete

    if params.use_limited_suffixes and not params.suffix_is_in_limited_list:
        mock_file_is_older.assert_not_called()
    else:
        mock_file_is_older.assert_called_once_with(older_than=mock_older_than, this_file=this_file)


@pytest.mark.delete_old
def test__check_and_delete_file_file_existance_correct(setup__check_and_delete):
    params, mock_file_is_older, this_file, mock_arguments, mock_older_than, caplog_text = setup__check_and_delete

    if (params.use_limited_suffixes and not params.suffix_is_in_limited_list) or (not params.file_is_older):
        assert this_file.exists()
    else:
        assert not this_file.exists()


@pytest.mark.delete_old
def test__check_and_delete_file_correct_logs(setup__check_and_delete):
    params, mock_file_is_older, this_file, mock_arguments, mock_older_than, caplog_text = setup__check_and_delete

    if params.use_limited_suffixes and not params.suffix_is_in_limited_list:
        assert "Suffix is not one of the ones we want." in caplog_text
    elif not params.file_is_older:
        assert "Is younger, continueing." in caplog_text
    else:
        assert " older, deleting" in caplog_text


@pytest.fixture(scope="function")
def setup_delete_old_files(fs, mocker):
    root_dir = pathlib.Path("foo")

    sub_dirs = [
        root_dir / "sub_1",
        root_dir / "sub_2"
    ]

    files = [
        root_dir / "file1.txt",
        root_dir / "file2.txt"
    ]

    for sub_dir in sub_dirs:
        fs.create_dir(sub_dir)

    for file_item in files:
        fs.create_file(file_item)

    mock_purge_dir = mocker.patch("wmul_file_manager.DeleteOldFiles._purge_old_files_from_directory")
    mock_check_file = mocker.patch("wmul_file_manager.DeleteOldFiles._check_and_delete_old_file")

    mock_arguments = "mock_arguments"

    DeleteOldFiles.delete_old_files(source_path=root_dir, arguments=mock_arguments)

    yield sub_dirs, files, mock_purge_dir, mock_check_file, mock_arguments


def test_delete_old_files_purge_old_called_correctly(setup_delete_old_files, mocker):
    sub_dirs, _, mock_purge_dir, _, mock_arguments = setup_delete_old_files

    expected_calls = []

    for sub_dir in sub_dirs:
        expected_calls.append(mocker.call(sub_dir, mock_arguments))

    mock_purge_dir.assert_has_calls(expected_calls)
    assert mock_purge_dir.call_count == len(expected_calls)


def test_delete_old_files_check_and_delete_called_correctly(setup_delete_old_files, mocker):
    _, files, _, mock_check_file, mock_arguments = setup_delete_old_files

    expected_calls = []

    for file_item in files:
        expected_calls.append(mocker.call(file_item, mock_arguments))

    mock_check_file.assert_has_calls(expected_calls)
    assert mock_check_file.call_count == len(expected_calls)


def test_run_script(mocker):
    mock_delete_old = mocker.patch("wmul_file_manager.DeleteOldFiles.delete_old_files")
    mock_source_path = "mock_source_path"
    mock_arguments = mocker.Mock(
        source_path=mock_source_path
    )

    DeleteOldFiles.run_script(arguments=mock_arguments)

    mock_delete_old.assert_called_once_with(mock_source_path, mock_arguments)
