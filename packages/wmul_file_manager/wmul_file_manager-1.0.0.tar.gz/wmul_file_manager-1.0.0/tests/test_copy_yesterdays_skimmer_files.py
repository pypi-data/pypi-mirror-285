"""
@Author = 'Mike Stanley'

============ Change Log ============
2018-May-15 = Created.

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
import datetime
import pathlib
import pytest

from wmul_file_manager import CopyYesterdaysSkimmerFiles
from wmul_file_manager.BulkCopier import BulkCopierArguments


@pytest.mark.parametrize('folder_exists', [True, False])
def test__copy_folder(mocker, folder_exists):
    mock_bulk_copier = mocker.patch("wmul_file_manager.BulkCopier.run_script")

    def exists():
        return folder_exists

    mock_source_path = mocker.Mock(exists=exists)
    mock_destination_path = "mock_destination_path"

    CopyYesterdaysSkimmerFiles._copy_folder(mock_source_path, mock_destination_path)

    expected_arguments = BulkCopierArguments(
        source_directories=[mock_source_path],
        destination_directory=mock_destination_path,
        exclude_suffixes_list=[],
        ignore_directories=[],
        force_copy_flag=False,
        delete_old_files_flag=False
    )

    if folder_exists:
        mock_bulk_copier.assert_called_once_with(arguments=expected_arguments)
    else:
        mock_bulk_copier.assert_not_called()


def test__get_date_folder_name():
    source_base = pathlib.Path("foo")

    test_date = datetime.date(year=2018, month=5, day=15)

    expected_directory = source_base / "2018-05-15"

    received_directory = CopyYesterdaysSkimmerFiles.get_date_folder_name(
        source_base=source_base,
        relevant_date=test_date
    )

    assert expected_directory == received_directory


@pytest.fixture(scope="function")
def setup_run_script(mocker):
    expected_date = datetime.date(year=2018, month=5, day=14)

    def mock_date_today_function():
        return datetime.date(year=2018, month=5, day=15)

    mock_date = mocker.patch(
        "wmul_file_manager.CopyYesterdaysSkimmerFiles.date",
        mocker.Mock(today=mock_date_today_function)
    )

    source_1 = "source_1"
    source_2 = "source_2"
    destination_1 = "destination_1"
    destination_2 = "destination_2"

    path_pair_1 = (source_1, destination_1)
    path_pair_2 = (source_2, destination_2)

    dated_path_1 = "date_1"
    dated_path_2 = "date_2"

    def mock_get_date_folder_function(source_base, relevant_date):
        if source_base[-1] == "1":
            return dated_path_1
        else:
            return dated_path_2

    mock_get_date_folder_name = mocker.patch(
        "wmul_file_manager.CopyYesterdaysSkimmerFiles.get_date_folder_name",
        mocker.Mock(side_effect=mock_get_date_folder_function)
    )

    mock_copy_folder = mocker.patch("wmul_file_manager.CopyYesterdaysSkimmerFiles._copy_folder")

    CopyYesterdaysSkimmerFiles.run_script([path_pair_1, path_pair_2])

    yield mock_get_date_folder_name, mock_copy_folder, source_1, source_2, expected_date, dated_path_1, dated_path_2, \
          destination_1, destination_2


def test_run_script_get_date_folder_called_correctly(setup_run_script, mocker):
    mock_get_date_folder_name, _, source_1, source_2, expected_date, _, _, _, _ = setup_run_script

    expected_date_folder_calls = [
        mocker.call(source_base=source_1, relevant_date=expected_date),
        mocker.call(source_base=source_2, relevant_date=expected_date)
    ]

    mock_get_date_folder_name.assert_has_calls(expected_date_folder_calls)
    assert mock_get_date_folder_name.call_count == len(expected_date_folder_calls)


def test_run_script_copy_folder_called_correctly(setup_run_script, mocker):
    _, mock_copy_folder, _, _, _, dated_path_1, dated_path_2, destination_1, destination_2 = setup_run_script
    expected_copy_folder_calls = [
        mocker.call(source_path=dated_path_1, destination_path=destination_1),
        mocker.call(source_path=dated_path_2, destination_path=destination_2),
    ]

    mock_copy_folder.assert_has_calls(expected_copy_folder_calls)
    assert mock_copy_folder.call_count == len(expected_copy_folder_calls)





