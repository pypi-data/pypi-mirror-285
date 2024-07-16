"""
@Author = 'Mike Stanley'

============ Change Log ============
2018-May-11 = Created.

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
import pathlib
import pytest
from wmul_file_manager import AnnualArchiver
from wmul_test_utils import make_namedtuple

def test_compare_start_and_end_folders_by_names(mocker):
    mock_folder_comparer_run_script = mocker.patch("wmul_file_manager.FolderComparer.run_script")

    root_folder = pathlib.Path("temp")

    source_1 = root_folder / "source_1"
    source_2 = root_folder / "source_2"

    destination_path = root_folder / "destination"

    mock_equivalent = "mock_equivalent"
    mock_name_comparer_output_file = "mock_name_comparer_output_file"

    AnnualArchiver.compare_start_and_end_folders_by_names(
        source_directories=[source_1, source_2],
        destination_directory=destination_path,
        equivalent_suffixes_list=mock_equivalent,
        name_comparer_output_file_name=mock_name_comparer_output_file
    )

    expected_call_1 = mocker.call(
        AnnualArchiver.FolderComparer.FolderComparerArguments(
            first_path=source_1,
            second_path=destination_path / "source_1",
            ignore_paths=[],
            equivalent_suffixes=mock_equivalent,
            name_only=False,
            name_size_only=False,
            output_path=mock_name_comparer_output_file
        )
    )

    expected_call_2 = mocker.call(
        AnnualArchiver.FolderComparer.FolderComparerArguments(
            first_path=source_2,
            second_path=destination_path / "source_2",
            ignore_paths=[],
            equivalent_suffixes=mock_equivalent,
            name_only=False,
            name_size_only=False,
            output_path=mock_name_comparer_output_file
        )
    )

    mock_folder_comparer_run_script.assert_has_calls([expected_call_1, expected_call_2])
    assert mock_folder_comparer_run_script.call_count == 2


@pytest.fixture(scope="function")
def setup_run_script(mocker):
    mock_delete_junk_files_arguments = "mock_delete_junk_files_arguments"
    mock_equivalent_suffixes_list = "mock_equivalent_suffixes_list"
    mock_equivalent_file_finder_arguments = mocker.Mock(equivalent_suffixes_list=mock_equivalent_suffixes_list)
    mock_source_paths = "mock_source_paths"
    mock_destination_path = "mock_destination_path"
    mock_bulk_copier_arguments = mocker.Mock(
        source_directories=mock_source_paths,
        destination_directory=mock_destination_path
    )

    mock_archive_list_of_folders = mocker.Mock()
    mock_compress_media_in_folder = mocker.Mock(archive_list_of_folders=mock_archive_list_of_folders)
    mock_name_comparer_output_file = "mock_name_comparer_output_file"

    mock_delete_junk_files_run_script = mocker.patch("wmul_file_manager.DeleteJunkFiles.run_script")
    mock_equivalent_file_finder_run_script = mocker.patch("wmul_file_manager.EquivalentFileFinder.run_script")
    mock_bulk_copier_run_script = mocker.patch("wmul_file_manager.BulkCopier.run_script")
    mock_compare_start_and_end = mocker.patch("wmul_file_manager.AnnualArchiver.compare_start_and_end_folders_by_names")

    AnnualArchiver.run_script(mock_delete_junk_files_arguments, mock_equivalent_file_finder_arguments,
                              mock_bulk_copier_arguments, mock_compress_media_in_folder,
                              mock_name_comparer_output_file)

    return make_namedtuple(
        "setup_run_script",
        mock_delete_junk_files_arguments=mock_delete_junk_files_arguments,
        mock_delete_junk_files_run_script=mock_delete_junk_files_run_script,
        mock_equivalent_suffixes_list=mock_equivalent_suffixes_list,
        mock_equivalent_file_finder_arguments=mock_equivalent_file_finder_arguments,
        mock_equivalent_file_finder_run_script=mock_equivalent_file_finder_run_script,
        mock_source_paths=mock_source_paths,
        mock_destination_path=mock_destination_path,
        mock_bulk_copier_arguments=mock_bulk_copier_arguments,
        mock_bulk_copier_run_script=mock_bulk_copier_run_script,
        mock_archive_list_of_folders=mock_archive_list_of_folders,
        mock_compress_media_in_folder=mock_compress_media_in_folder,
        mock_name_comparer_output_file=mock_name_comparer_output_file,
        mock_compare_start_and_end=mock_compare_start_and_end
    )

def test_run_script_delete_junk_files_called_correctly(setup_run_script):
    mock_delete_junk_files_arguments = setup_run_script.mock_delete_junk_files_arguments
    mock_delete_junk_files_run_script = setup_run_script.mock_delete_junk_files_run_script

    mock_delete_junk_files_run_script.assert_called_once_with(mock_delete_junk_files_arguments)

def test_run_script_equivalent_file_finder_called_correctly(setup_run_script):
    mock_equivalent_file_finder_arguments = setup_run_script.mock_equivalent_file_finder_arguments
    mock_equivalent_file_finder_run_script = setup_run_script.mock_equivalent_file_finder_run_script

    mock_equivalent_file_finder_run_script.assert_called_once_with(mock_equivalent_file_finder_arguments)

def test_run_script_bulk_copier_called_correctly(setup_run_script):
    mock_bulk_copier_arguments = setup_run_script.mock_bulk_copier_arguments
    mock_bulk_copier_run_script = setup_run_script.mock_bulk_copier_run_script

    mock_bulk_copier_run_script.assert_called_once_with(mock_bulk_copier_arguments)

def test_run_script_compress_media_in_folder_called_correctly(setup_run_script):
    mock_archive_list_of_folders = setup_run_script.mock_archive_list_of_folders
    mock_archive_list_of_folders.assert_called_once_with()

def test_run_script_compare_start_and_end_called_correctly(setup_run_script):
    mock_equivalent_suffixes_list = setup_run_script.mock_equivalent_suffixes_list
    mock_source_paths = setup_run_script.mock_source_paths
    mock_destination_path = setup_run_script.mock_destination_path
    mock_name_comparer_output_file = setup_run_script.mock_name_comparer_output_file
    mock_compare_start_and_end = setup_run_script.mock_compare_start_and_end

    mock_compare_start_and_end.assert_called_once_with(
        mock_source_paths,
        mock_destination_path,
        mock_equivalent_suffixes_list,
        mock_name_comparer_output_file
    )




