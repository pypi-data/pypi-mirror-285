"""
@Author = 'Mike Stanley'


============ Change Log ============
2024-May-24 = Created.

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
import pytest
from click.testing import CliRunner
from pathlib import Path
from wmul_file_manager import cli
from wmul_test_utils import generate_true_false_matrix_from_list_of_strings, make_namedtuple

compress_audio_in_folder_params, compress_audio_in_folder_ids = generate_true_false_matrix_from_list_of_strings(
    "setup_compress_audio_in_folder_options",
    [
        "delete_flag",
        "separate_folder_flag",
        "yesterday_flag"
    ]
)


@pytest.fixture(scope="function", params=compress_audio_in_folder_params, ids=compress_audio_in_folder_ids)
def setup_compress_audio_in_folder(request, mocker, fs):
    params = request.param
    source_path_1 = Path("/temp/folder_1")
    fs.create_dir(source_path_1)
    source_path_2 = Path("/temp/folder_2")
    fs.create_dir(source_path_2)

    ffmpeg_executable = Path("/ffmpeg/ffmpeg.exe")
    fs.create_file(ffmpeg_executable)

    audio_source_suffixes = ".wav .AIff"
    expected_audio_source_suffixes = [".wav", ".AIff"]

    audio_file_audio_codec = "ogg"
    audio_file_audio_bitrate = 320
    audio_destination_suffix = ".ogg"

    threads = 4
    
    mock_audio_compressor_class = mocker.patch(
        "wmul_file_manager.cli.AudioCompressor",
        autospec=True
    )

    mock_null_compressor_class = mocker.patch(
        "wmul_file_manager.cli.NullCompressor",
        autospec=True
    )

    mock_compress_media_in_folder_class = mocker.patch(
        "wmul_file_manager.cli.CompressMediaInFolder",
        autospec=True
    )

    cli_args = [
        str(source_path_1),
        str(source_path_2),
        str(ffmpeg_executable),
        "--audio_source_suffixes", audio_source_suffixes,
        "--audio_file_audio_codec", audio_file_audio_codec,
        "--audio_file_audio_bitrate", audio_file_audio_bitrate,
        "--audio_destination_suffix", audio_destination_suffix,
        "--threads", threads
    ]

    if params.delete_flag:
        cli_args.append("--delete")

    if params.separate_folder_flag:
        cli_args.append("--separate_folder")

    if params.yesterday_flag:
        cli_args.append("--yesterday")

    runner = CliRunner()

    result = runner.invoke(
        cli.compress_audio_in_folder,
        cli_args
    )

    return make_namedtuple(
        "setup_compress_media_in_folder",
        params=params,
        source_path_1=source_path_1,
        source_path_2=source_path_2,
        ffmpeg_executable=ffmpeg_executable,
        expected_audio_source_suffixes=expected_audio_source_suffixes,
        audio_file_audio_codec=audio_file_audio_codec,
        audio_file_audio_bitrate=audio_file_audio_bitrate,
        audio_destination_suffix=audio_destination_suffix,
        threads=threads,
        mock_audio_compressor_class=mock_audio_compressor_class,
        mock_null_compressor_class=mock_null_compressor_class,
        mock_compress_media_in_folder_class=mock_compress_media_in_folder_class,
        result=result   
    )

def test_exit_code_zero(setup_compress_audio_in_folder):
    result = setup_compress_audio_in_folder.result
    assert result.exit_code == 0

def test_archive_yesterdays_folders_called_correctly(setup_compress_audio_in_folder):
    mock_compress_media_in_folder_class = setup_compress_audio_in_folder.mock_compress_media_in_folder_class
    params = setup_compress_audio_in_folder.params
    mock_calls = [str(mock_call) for mock_call in mock_compress_media_in_folder_class.mock_calls]

    if params.yesterday_flag:
        assert "call().archive_yesterdays_folders()" in mock_calls
    else:
        assert not "call().archive_yesterdays_folders()" in mock_calls

def test_archive_list_of_folders_called_correctly(setup_compress_audio_in_folder):
    mock_compress_media_in_folder_class = setup_compress_audio_in_folder.mock_compress_media_in_folder_class
    params = setup_compress_audio_in_folder.params
    mock_calls = [str(mock_call) for mock_call in mock_compress_media_in_folder_class.mock_calls]

    if params.yesterday_flag:
        assert not "call().archive_list_of_folders()" in mock_calls
    else:
        assert "call().archive_list_of_folders()" in mock_calls

def test_audio_compressor_constructed_correctly(setup_compress_audio_in_folder):
    expected_audio_source_suffixes = setup_compress_audio_in_folder.expected_audio_source_suffixes
    audio_file_audio_codec = setup_compress_audio_in_folder.audio_file_audio_codec
    audio_file_audio_bitrate = setup_compress_audio_in_folder.audio_file_audio_bitrate
    audio_destination_suffix = setup_compress_audio_in_folder.audio_destination_suffix
    threads = setup_compress_audio_in_folder.threads
    ffmpeg_executable = setup_compress_audio_in_folder.ffmpeg_executable
    mock_audio_compressor_class = setup_compress_audio_in_folder.mock_audio_compressor_class

    mock_audio_compressor_class.assert_called_once_with(
        suffixes=expected_audio_source_suffixes,
        audio_codec=audio_file_audio_codec,
        audio_bitrate=audio_file_audio_bitrate,
        destination_suffix=audio_destination_suffix,
        ffmpeg_threads=threads,
        ffmpeg_executable=str(ffmpeg_executable)
    )

def test_null_compressor_constructed_correctly(setup_compress_audio_in_folder):
    mock_null_compressor_class = setup_compress_audio_in_folder.mock_null_compressor_class
    mock_null_compressor_class.assert_called_once_with()

def test_compress_media_in_folder_constructed_correctly(setup_compress_audio_in_folder):
    mock_compress_media_in_folder_class = setup_compress_audio_in_folder.mock_compress_media_in_folder_class
    source_path_1 = setup_compress_audio_in_folder.source_path_1
    source_path_2 = setup_compress_audio_in_folder.source_path_2
    params = setup_compress_audio_in_folder.params
    mock_null_compressor_class = setup_compress_audio_in_folder.mock_null_compressor_class
    mock_null_compressor = mock_null_compressor_class.return_value
    mock_audio_compressor_class = setup_compress_audio_in_folder.mock_audio_compressor_class
    mock_audio_compressor = mock_audio_compressor_class.return_value

    mock_compress_media_in_folder_class.assert_called_once_with(
        source_paths=[source_path_1, source_path_2],
        audio_compressor=mock_audio_compressor,
        video_compressor=mock_null_compressor,
        separate_folder_flag=params.separate_folder_flag,
        delete_files_flag=params.delete_flag
    )
