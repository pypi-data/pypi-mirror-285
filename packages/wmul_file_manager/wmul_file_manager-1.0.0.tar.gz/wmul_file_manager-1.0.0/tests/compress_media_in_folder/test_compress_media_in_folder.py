"""
@Author = 'Mike Stanley'

============ Change Log ============
2024-May-09 = Created from convert_folder_to_mp4/test_file_information.py

============ License ============
The MIT License (MIT)

Copyright (c) 2024 Michael Stanley

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
import pytest
from pathlib import Path
from wmul_file_manager.CompressMediaInFolder import CompressMediaInFolder, _CompressorFileInformation
from wmul_test_utils import make_namedtuple, generate_true_false_matrix_from_list_of_strings, \
    assert_has_only_these_calls

compress_media_in_folder_params, compress_media_in_folder_ids = generate_true_false_matrix_from_list_of_strings(
    "compress_media_in_folder_options",
    [
        "separate_folder",
        "delete_files"
    ]
)

@pytest.fixture(scope="function", params=compress_media_in_folder_params, ids=compress_media_in_folder_ids)
def setup_compress_media_in_folder(request, fs, mocker):
    params = request.param

    source_path_1 = Path("/temp/folder_1")
    source_path_2 = Path("/temp/folder_2")
    source_path_3 = Path("/temp/folder_3")
    file_1 = source_path_1 / "file_1.wav"
    file_2 = source_path_1 / "file_2.wav"
    file_3 = source_path_1 / "subfolder_1" / "file_3.wav"
    file_4 = source_path_1 / "subfolder_2" / "file_4.wav"

    fs.create_dir(source_path_1)
    fs.create_dir(source_path_3)

    fs.create_file(file_1)
    fs.create_file(file_2)
    fs.create_file(file_3)
    fs.create_file(file_4)

    source_paths = [source_path_1, source_path_2, source_path_3]

    audio_compressor = mocker.Mock()
    video_compressor = mocker.Mock()

    return make_namedtuple(
        "setup_compress_media_in_folder",
        params=params,
        source_path_1=source_path_1,
        source_path_2=source_path_2,
        source_path_3=source_path_3,
        file_1=file_1,
        file_2=file_2,
        file_3=file_3,
        file_4=file_4,
        source_paths=source_paths,
        audio_compressor=audio_compressor,
        video_compressor=video_compressor
    )

def test_archive_list_of_folders(setup_compress_media_in_folder, mocker):
    params = setup_compress_media_in_folder.params
    source_path_1 = setup_compress_media_in_folder.source_path_1
    source_path_2 = setup_compress_media_in_folder.source_path_2
    source_path_3 = setup_compress_media_in_folder.source_path_3
    source_paths = setup_compress_media_in_folder.source_paths
    audio_compressor = setup_compress_media_in_folder.audio_compressor
    video_compressor = setup_compress_media_in_folder.video_compressor

    mock_check_and_archive_folder = mocker.Mock()
    mocker.patch(
        "wmul_file_manager.CompressMediaInFolder.CompressMediaInFolder._check_and_archive_folder",
        mock_check_and_archive_folder
    )

    cmif = CompressMediaInFolder(
        source_paths=source_paths,
        audio_compressor=audio_compressor,
        video_compressor=video_compressor,
        separate_folder_flag=params.separate_folder,
        delete_files_flag=params.delete_files
    )

    result = cmif.archive_list_of_folders()

    assert result is None

    expected_calls = [
        mocker.call(source_path_1),
        mocker.call(source_path_2),
        mocker.call(source_path_3)
    ]

    assert_has_only_these_calls(
        mock=mock_check_and_archive_folder,
        calls=expected_calls
    )

def test_archive_yesterdays_folders(setup_compress_media_in_folder, mocker):
    params = setup_compress_media_in_folder.params
    source_path_1 = setup_compress_media_in_folder.source_path_1
    source_path_2 = setup_compress_media_in_folder.source_path_2
    source_path_3 = setup_compress_media_in_folder.source_path_3
    source_paths = setup_compress_media_in_folder.source_paths
    audio_compressor = setup_compress_media_in_folder.audio_compressor
    video_compressor = setup_compress_media_in_folder.video_compressor

    mock_today = mocker.Mock(return_value=datetime.date(year=2018, month=5, day=4))
    mock_date = mocker.Mock(today=mock_today)
    mocker.patch("wmul_file_manager.CompressMediaInFolder.date", mock_date)

    mock_check_and_archive_folder = mocker.Mock()
    mocker.patch(
        "wmul_file_manager.CompressMediaInFolder.CompressMediaInFolder._check_and_archive_folder",
        mock_check_and_archive_folder
    )

    cmif = CompressMediaInFolder(
        source_paths=source_paths,
        audio_compressor=audio_compressor,
        video_compressor=video_compressor,
        separate_folder_flag=params.separate_folder,
        delete_files_flag=params.delete_files
    )

    result = cmif.archive_yesterdays_folders()

    assert result is None

    source_path_1_yesterday = source_path_1 / "2018-05-03"
    source_path_2_yesterday = source_path_2 / "2018-05-03"
    source_path_3_yesterday = source_path_3 / "2018-05-03"

    expected_calls = [
        mocker.call(source_path_1_yesterday),
        mocker.call(source_path_2_yesterday),
        mocker.call(source_path_3_yesterday)
    ]

    assert_has_only_these_calls(
        mock=mock_check_and_archive_folder,
        calls=expected_calls
    )

def test_check_and_archive_folder(setup_compress_media_in_folder, mocker, caplog):
    params = setup_compress_media_in_folder.params
    source_path_1 = setup_compress_media_in_folder.source_path_1
    source_path_2 = setup_compress_media_in_folder.source_path_2
    source_path_3 = setup_compress_media_in_folder.source_path_3
    source_paths = setup_compress_media_in_folder.source_paths
    audio_compressor = setup_compress_media_in_folder.audio_compressor
    video_compressor = setup_compress_media_in_folder.video_compressor

    mock_archive_folder = mocker.Mock()
    mocker.patch(
        "wmul_file_manager.CompressMediaInFolder.CompressMediaInFolder._archive_folder",
        mock_archive_folder
    )

    cmif = CompressMediaInFolder(
        source_paths=source_paths,
        audio_compressor=audio_compressor,
        video_compressor=video_compressor,
        separate_folder_flag=params.separate_folder,
        delete_files_flag=params.delete_files
    )

    result_1 = cmif._check_and_archive_folder(source_path=source_path_1)
    assert result_1 is None

    result_2 = cmif._check_and_archive_folder(source_path=source_path_2)
    assert result_2 is None

    result_3 = cmif._check_and_archive_folder(source_path=source_path_3)
    assert result_3 is None

    if params.separate_folder:
        expected_calls = [
            mocker.call(source_path_1, Path("/temp/folder_1_cmp")),
            mocker.call(source_path_3, Path("/temp/folder_3_cmp"))
        ]
    else:
        expected_calls = [
            mocker.call(source_path_1, Path("/temp/folder_1")),
            mocker.call(source_path_3, Path("/temp/folder_3"))
        ]

    assert_has_only_these_calls(
        mock=mock_archive_folder,
        calls=expected_calls
    )

    assert "Folder does not exist. \\temp\\folder_2" in caplog.text

def test_archive_folder(setup_compress_media_in_folder, mocker):
    params = setup_compress_media_in_folder.params
    source_path_1 = setup_compress_media_in_folder.source_path_1
    source_paths = setup_compress_media_in_folder.source_paths
    audio_compressor = setup_compress_media_in_folder.audio_compressor
    video_compressor = setup_compress_media_in_folder.video_compressor

    compressed_files_folder = Path("/temp/compressed_files")

    mock_factory = mocker.Mock()
    mock_get_factory = mocker.Mock(return_value=mock_factory)
    mocker.patch(
        "wmul_file_manager.CompressMediaInFolder._CompressorFileInformation.get_factory",
        mock_get_factory
    )

    mock_populate_list_of_files_for_compression = mocker.Mock()
    mocker.patch(
        "wmul_file_manager.CompressMediaInFolder.CompressMediaInFolder._populate_list_of_files_for_compression",
        mock_populate_list_of_files_for_compression
    )

    mock_compress_list_of_files = mocker.Mock()
    mocker.patch(
        "wmul_file_manager.CompressMediaInFolder.CompressMediaInFolder._compress_list_of_files",
        mock_compress_list_of_files
    )

    mock_delete_files = mocker.Mock()
    mocker.patch(
        "wmul_file_manager.CompressMediaInFolder.CompressMediaInFolder._delete_files",
        mock_delete_files
    )  

    cmif = CompressMediaInFolder(
        source_paths=source_paths,
        audio_compressor=audio_compressor,
        video_compressor=video_compressor,
        separate_folder_flag=params.separate_folder,
        delete_files_flag=params.delete_files
    )

    result = cmif._archive_folder(source_path=source_path_1, compressed_files_folder=compressed_files_folder)

    assert result is None

    mock_get_factory.assert_called_once_with(source_path_1, compressed_files_folder)
    mock_populate_list_of_files_for_compression.assert_called_once_with(
        source_path_1, 
        mock_factory
    )
    mock_compress_list_of_files.assert_called_once_with()

    if params.delete_files:
        mock_delete_files.assert_called_once_with()
    else:
        mock_delete_files.assert_not_called()

def test_populate_list_of_files_for_compression(setup_compress_media_in_folder, mocker):
    params = setup_compress_media_in_folder.params
    source_path_1 = setup_compress_media_in_folder.source_path_1
    file_1 = setup_compress_media_in_folder.file_1
    file_2 = setup_compress_media_in_folder.file_2
    file_3 = setup_compress_media_in_folder.file_3
    file_4 = setup_compress_media_in_folder.file_4
    source_paths = setup_compress_media_in_folder.source_paths
    audio_compressor = setup_compress_media_in_folder.audio_compressor
    video_compressor = setup_compress_media_in_folder.video_compressor

    mock_file_info_1 = "mock_file_info_1"
    mock_file_info_2 = "mock_file_info_2"
    mock_file_info_3 = "mock_file_info_3"
    mock_file_info_4 = "mock_file_info_4"

    def file_info_function(file_item):
        if file_item == file_1:
            return mock_file_info_1
        if file_item == file_2:
            return mock_file_info_2
        if file_item == file_3:
            return mock_file_info_3
        if file_item == file_4:
            return mock_file_info_4

    mock_file_info_factory = mocker.Mock(side_effect=file_info_function)
    
    mock_consider_this_file = mocker.Mock()
    mocker.patch(
        "wmul_file_manager.CompressMediaInFolder.CompressMediaInFolder._consider_this_file",
        mock_consider_this_file
    )

    cmif = CompressMediaInFolder(
        source_paths=source_paths,
        audio_compressor=audio_compressor,
        video_compressor=video_compressor,
        separate_folder_flag=params.separate_folder,
        delete_files_flag=params.delete_files
    )

    result = cmif._populate_list_of_files_for_compression(
        source_path=source_path_1, 
        file_info_factory=mock_file_info_factory
    )

    assert result is None

    file_info_factory_expected_calls = [
        mocker.call(file_1),
        mocker.call(file_2),
        mocker.call(file_3),
        mocker.call(file_4),
    ]

    assert_has_only_these_calls(
        mock=mock_file_info_factory,
        calls=file_info_factory_expected_calls,
        any_order=True
    )

    consider_this_file_expected_calls = [
        mocker.call(file_information=mock_file_info_1),
        mocker.call(file_information=mock_file_info_2),
        mocker.call(file_information=mock_file_info_3),
        mocker.call(file_information=mock_file_info_4),
    ]

    assert_has_only_these_calls(
        mock=mock_consider_this_file,
        calls=consider_this_file_expected_calls,
        any_order=True
    )
    
def test_consider_this_file_audio(setup_compress_media_in_folder, mocker):
    params = setup_compress_media_in_folder.params
    source_paths = setup_compress_media_in_folder.source_paths

    audio_compressor = setup_compress_media_in_folder.audio_compressor
    mock_audio_consider_this_file_for_compression = mocker.Mock(return_value=True)
    audio_compressor.configure_mock(consider_file_for_compression=mock_audio_consider_this_file_for_compression)

    video_compressor = setup_compress_media_in_folder.video_compressor
    mock_video_consider_this_file_for_compression = mocker.Mock(return_value=False)
    video_compressor.configure_mock(consider_file_for_compression=mock_video_consider_this_file_for_compression)

    cmif = CompressMediaInFolder(
        source_paths=source_paths,
        audio_compressor=audio_compressor,
        video_compressor=video_compressor,
        separate_folder_flag=params.separate_folder,
        delete_files_flag=params.delete_files
    )

    mock_set_as_non_media_file = mocker.Mock()
    mock_file_information = mocker.Mock(set_as_non_media_file=mock_set_as_non_media_file)

    result = cmif._consider_this_file(file_information=mock_file_information)

    assert result is None

    mock_audio_consider_this_file_for_compression.assert_called_once_with(
        file_under_consideration=mock_file_information
    )
    mock_video_consider_this_file_for_compression.assert_not_called()
    mock_set_as_non_media_file.assert_not_called()

def test_consider_this_file_video(setup_compress_media_in_folder, mocker):
    params = setup_compress_media_in_folder.params
    source_paths = setup_compress_media_in_folder.source_paths

    audio_compressor = setup_compress_media_in_folder.audio_compressor
    mock_audio_consider_this_file_for_compression = mocker.Mock(return_value=False)
    audio_compressor.configure_mock(consider_file_for_compression=mock_audio_consider_this_file_for_compression)

    video_compressor = setup_compress_media_in_folder.video_compressor
    mock_video_consider_this_file_for_compression = mocker.Mock(return_value=True)
    video_compressor.configure_mock(consider_file_for_compression=mock_video_consider_this_file_for_compression)


    cmif = CompressMediaInFolder(
        source_paths=source_paths,
        audio_compressor=audio_compressor,
        video_compressor=video_compressor,
        separate_folder_flag=params.separate_folder,
        delete_files_flag=params.delete_files
    )

    mock_set_as_non_media_file = mocker.Mock()
    mock_file_information = mocker.Mock(set_as_non_media_file=mock_set_as_non_media_file)

    result = cmif._consider_this_file(file_information=mock_file_information)

    assert result is None

    mock_audio_consider_this_file_for_compression.assert_called_once_with(
        file_under_consideration=mock_file_information
    )
    mock_video_consider_this_file_for_compression.assert_called_once_with(
        file_under_consideration=mock_file_information,
    )
    mock_set_as_non_media_file.assert_not_called()

def test_consider_this_file_neither(setup_compress_media_in_folder, mocker):
    params = setup_compress_media_in_folder.params
    source_paths = setup_compress_media_in_folder.source_paths

    audio_compressor = setup_compress_media_in_folder.audio_compressor
    mock_audio_consider_this_file_for_compression = mocker.Mock(return_value=False)
    audio_compressor.configure_mock(consider_file_for_compression=mock_audio_consider_this_file_for_compression)

    video_compressor = setup_compress_media_in_folder.video_compressor
    mock_video_consider_this_file_for_compression = mocker.Mock(return_value=False)
    video_compressor.configure_mock(consider_file_for_compression=mock_video_consider_this_file_for_compression)


    cmif = CompressMediaInFolder(
        source_paths=source_paths,
        audio_compressor=audio_compressor,
        video_compressor=video_compressor,
        separate_folder_flag=params.separate_folder,
        delete_files_flag=params.delete_files
    )

    mock_set_as_non_media_file = mocker.Mock()
    mock_file_information = mocker.Mock(set_as_non_media_file=mock_set_as_non_media_file)

    result = cmif._consider_this_file(file_information=mock_file_information)

    assert result is None

    mock_audio_consider_this_file_for_compression.assert_called_once_with(
        file_under_consideration=mock_file_information
    )
    mock_video_consider_this_file_for_compression.assert_called_once_with(
        file_under_consideration=mock_file_information,
    )
    mock_set_as_non_media_file.assert_called_once_with()
