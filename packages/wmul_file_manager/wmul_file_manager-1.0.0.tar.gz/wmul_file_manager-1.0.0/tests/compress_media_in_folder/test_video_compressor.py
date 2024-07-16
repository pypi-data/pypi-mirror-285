"""
@Author = 'Mike Stanley'

============ Change Log ============
2024-May-10 = Created.

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
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from wmul_file_manager.CompressMediaInFolder import VideoCompressor, _CompressorFileInformation, \
    _CompressorFileInformationType
from wmul_file_manager.utilities import ffmpeg
from wmul_test_utils import make_namedtuple, generate_combination_matrix_from_dataclass


class NumberOfSuffixes(Enum):
    Zero = 0
    One = 1
    Two = 2
    Ten = 10


@dataclass
class video_compressor_construction_options:
    number_of_suffixes: NumberOfSuffixes


video_compressor_construction_params, video_compressor_construction_ids = generate_combination_matrix_from_dataclass(video_compressor_construction_options)

@pytest.fixture(scope="function", params=video_compressor_construction_params, ids=video_compressor_construction_ids)
def setup_video_compressor_construction(request, fs):
    params = request.param

    if params.number_of_suffixes == NumberOfSuffixes.Zero:
        suffixes = []
        expected_suffixes = []
    elif params.number_of_suffixes == NumberOfSuffixes.One:
        suffixes = [".mOv"]
        expected_suffixes = [".mov"]
    elif params.number_of_suffixes == NumberOfSuffixes.Two:
        suffixes = [".mOv", ".mp4"]
        expected_suffixes = [".mov", ".mp4"]
    else:
        suffixes = [".mOv", ".mp4", ".mPeg", ".avi", ".foo", 
                    ".bar", ".baZ", ".AAA", ".bbb", ".ccc"]
        expected_suffixes = [".mov", ".mp4", ".mpeg", ".avi", ".foo", 
                             ".bar", ".baz", ".aaa", ".bbb", ".ccc"]
        
    video_codec = "h264"
    video_bitrate = 10
    expected_bitrate_floor = 12_000_000
    audio_codec = "aac"
    audio_bitrate = 160
    destination_suffix = ".mp4"
    ffmpeg_threads = 3
    ffmpeg_executable = Path("/ffmpeg/ffmpeg.exe")
    ffprobe_executable = Path("/ffmpeg/ffprobe.exe")

    result = VideoCompressor(
        suffixes=suffixes,
        video_codec=video_codec,
        video_bitrate=video_bitrate,
        audio_codec=audio_codec,
        audio_bitrate=audio_bitrate,
        destination_suffix=destination_suffix,
        ffmpeg_threads=ffmpeg_threads,
        ffmpeg_executable=ffmpeg_executable,
        ffprobe_executable=ffprobe_executable
    )

    return make_namedtuple(
        "setup_video_compressor",
        params=params,
        suffixes=suffixes,
        expected_suffixes=expected_suffixes,
        video_codec=video_codec,
        video_bitrate=video_bitrate,
        expected_bitrate_floor=expected_bitrate_floor,
        audio_codec=audio_codec,
        audio_bitrate=audio_bitrate,
        destination_suffix=destination_suffix,
        ffmpeg_threads=ffmpeg_threads,
        ffmpeg_executable=ffmpeg_executable,
        ffprobe_executable=ffprobe_executable,
        result=result
    )

def test_list_of_files_for_compression_created(setup_video_compressor_construction):
    list_of_files_for_compression = setup_video_compressor_construction.result.list_of_files_for_compression

    assert isinstance(list_of_files_for_compression, list)
    assert len(list_of_files_for_compression) == 0

def test_list_of_files_for_deletion_created(setup_video_compressor_construction):
    list_of_files_for_deletion = setup_video_compressor_construction.result.list_of_files_for_deletion

    assert isinstance(list_of_files_for_deletion, list)
    assert len(list_of_files_for_deletion) == 0

def test_suffixes_recorded_correctly(setup_video_compressor_construction):
    result = setup_video_compressor_construction.result
    expected_suffixes = setup_video_compressor_construction.expected_suffixes

    assert result.source_suffixes == expected_suffixes

def test_destination_suffix_set_correctly(setup_video_compressor_construction):
    result = setup_video_compressor_construction.result
    destination_suffix = setup_video_compressor_construction.destination_suffix

    assert result.destination_suffix == destination_suffix

def test_call_ffmpeg_created_correctly(setup_video_compressor_construction):
    call_ffmpeg = setup_video_compressor_construction.result.call_ffmpeg
    call_ffmpeg_kwargs = call_ffmpeg.keywords
    video_codec = setup_video_compressor_construction.video_codec
    video_bitrate = setup_video_compressor_construction.video_bitrate
    audio_codec = setup_video_compressor_construction.audio_codec
    audio_bitrate = setup_video_compressor_construction.audio_bitrate
    threads = setup_video_compressor_construction.ffmpeg_threads
    executable_path = setup_video_compressor_construction.ffmpeg_executable

    assert call_ffmpeg.func == ffmpeg.convert_video

    assert call_ffmpeg_kwargs['video_codec'] == video_codec
    assert call_ffmpeg_kwargs['video_bitrate'] == video_bitrate
    assert call_ffmpeg_kwargs['audio_codec'] == audio_codec
    assert call_ffmpeg_kwargs['audio_bitrate'] == audio_bitrate
    assert call_ffmpeg_kwargs['threads'] == threads
    assert call_ffmpeg_kwargs['executable_path'] == executable_path

def test_set_bitrate_computed_correctly(setup_video_compressor_construction):
    result = setup_video_compressor_construction.result
    expected_bitrate_floor = setup_video_compressor_construction.expected_bitrate_floor

    assert result.bitrate_floor == expected_bitrate_floor

@pytest.fixture
def setup_consider_file_for_compression(fs):
    suffixes = [".mOv", ".mp4"]
    video_codec = "h264"
    video_bitrate = 10
    audio_codec = "aac"
    audio_bitrate = 160
    destination_suffix = ".mp4"
    ffmpeg_threads = 3
    ffmpeg_executable = Path("/ffmpeg/ffmpeg.exe")
    ffprobe_executable = Path("/ffmpeg/ffprobe.exe")

    file_info_factory = _CompressorFileInformation.get_factory(
        root_path=Path("/foo/bar"),
        compressed_files_folder=Path("/finished")
    )

    video_compressor = VideoCompressor(
        suffixes=suffixes,
        video_codec=video_codec,
        video_bitrate=video_bitrate,
        audio_codec=audio_codec,
        audio_bitrate=audio_bitrate,
        destination_suffix=destination_suffix,
        ffmpeg_threads=ffmpeg_threads,
        ffmpeg_executable=ffmpeg_executable,
        ffprobe_executable=ffprobe_executable
    )

    return make_namedtuple(
        "setup_consider_file_for_compression",
        video_compressor=video_compressor,
        file_info_factory=file_info_factory
    )

def test_consider_file__is_wanted(setup_consider_file_for_compression, mocker):
    video_compressor = setup_consider_file_for_compression.video_compressor
    file_info_factory = setup_consider_file_for_compression.file_info_factory

    mock_determine_video_bitrate = mocker.Mock(return_value = 20_000_000)
    mocker.patch("wmul_file_manager.utilities.ffmpeg.determine_video_bitrate", mock_determine_video_bitrate)

    assert len(video_compressor.list_of_files_for_compression) == 0

    file_under_consideration = Path("/foo/bar/test1.mp4")
    file_information = file_info_factory(file_under_consideration)
    result = video_compressor.consider_file_for_compression(file_under_consideration=file_information)

    assert result
    assert len(video_compressor.list_of_files_for_compression) == 1

    file_in_list = video_compressor.list_of_files_for_compression[0]
    assert file_in_list.original_file_name == file_under_consideration

    assert file_information.file_info_type == _CompressorFileInformationType.UnCompressed_Media_File

def test_consider_file__is_not_wanted(setup_consider_file_for_compression):
    video_compressor = setup_consider_file_for_compression.video_compressor
    file_info_factory = setup_consider_file_for_compression.file_info_factory

    assert len(video_compressor.list_of_files_for_compression) == 0

    file_under_consideration = Path("/foo/bar/test1.docx")
    file_information = file_info_factory(file_under_consideration)
    result = video_compressor.consider_file_for_compression(file_under_consideration=file_information)

    assert not result
    assert len(video_compressor.list_of_files_for_compression) == 0

    assert file_information.file_info_type == _CompressorFileInformationType.Unchecked_File

def test_consider_file__is_wanted_mangled_suffix(setup_consider_file_for_compression, mocker):
    video_compressor = setup_consider_file_for_compression.video_compressor
    file_info_factory = setup_consider_file_for_compression.file_info_factory

    mock_determine_video_bitrate = mocker.Mock(return_value = 20_000_000)
    mocker.patch("wmul_file_manager.utilities.ffmpeg.determine_video_bitrate", mock_determine_video_bitrate)

    assert len(video_compressor.list_of_files_for_compression) == 0

    file_under_consideration = Path("/foo/bar/test1.Mp4")
    file_information = file_info_factory(file_under_consideration)
    result = video_compressor.consider_file_for_compression(file_under_consideration=file_information)

    assert result
    assert len(video_compressor.list_of_files_for_compression) == 1

    file_in_list = video_compressor.list_of_files_for_compression[0]
    assert file_in_list.original_file_name == file_under_consideration

    assert file_information.file_info_type == _CompressorFileInformationType.UnCompressed_Media_File

def test_consider_file__several(setup_consider_file_for_compression, mocker):
    video_compressor = setup_consider_file_for_compression.video_compressor
    file_info_factory = setup_consider_file_for_compression.file_info_factory

    mock_determine_video_bitrate = mocker.Mock(return_value = 20_000_000)
    mocker.patch("wmul_file_manager.utilities.ffmpeg.determine_video_bitrate", mock_determine_video_bitrate)

    list_of_files_for_compression = video_compressor.list_of_files_for_compression
    assert len(list_of_files_for_compression) == 0

    file_under_consideration_1 = Path("/foo/bar/test1.mp4")
    file_information_1 = file_info_factory(file_under_consideration_1)
    result_1 = video_compressor.consider_file_for_compression(file_under_consideration=file_information_1)

    assert result_1
    assert len(list_of_files_for_compression) == 1

    matching_files_1 = [file_item for file_item in list_of_files_for_compression
                      if file_item.original_file_name == file_under_consideration_1]
    assert len(matching_files_1) == 1

    assert file_information_1.file_info_type == _CompressorFileInformationType.UnCompressed_Media_File

    file_under_consideration_2 = Path("/foo/bar/test2.docx")
    file_information_2 = file_info_factory(file_under_consideration_2)
    result_2 = video_compressor.consider_file_for_compression(file_under_consideration=file_information_2)

    assert not result_2
    assert len(list_of_files_for_compression) == 1

    matching_files_2 = [file_item for file_item in list_of_files_for_compression
                      if file_item.original_file_name == file_under_consideration_2]
    assert len(matching_files_2) == 0

    assert file_information_2.file_info_type == _CompressorFileInformationType.Unchecked_File

    file_under_consideration_3 = Path("/foo/bar/test3.mov")
    file_information_3 = file_info_factory(file_under_consideration_3)
    result_3 = video_compressor.consider_file_for_compression(file_under_consideration=file_information_3)

    assert result_3
    assert len(list_of_files_for_compression) == 2

    matching_files_3 = [file_item for file_item in list_of_files_for_compression
                      if file_item.original_file_name == file_under_consideration_3]
    assert len(matching_files_3) == 1

    assert file_information_3.file_info_type == _CompressorFileInformationType.UnCompressed_Media_File

def test_consider_file__other_factors(setup_consider_file_for_compression, mocker):
    video_compressor = setup_consider_file_for_compression.video_compressor
    file_info_factory = setup_consider_file_for_compression.file_info_factory

    file_under_consideration_1 = Path("/foo/bar/test1.mp4")
    file_under_consideration_2 = Path("/foo/bar/test2.docx")
    file_under_consideration_3 = Path("/foo/bar/test3.mov")

    def determine_video_bitrate_func(file_name, ffprobe_executable):
        if file_name == file_under_consideration_1:
            return 20_000_000
        else:
            return 12_000_000

    mock_determine_video_bitrate = mocker.Mock(side_effect = determine_video_bitrate_func)
    mocker.patch("wmul_file_manager.utilities.ffmpeg.determine_video_bitrate", mock_determine_video_bitrate)

    list_of_files_for_compression = video_compressor.list_of_files_for_compression
    assert len(list_of_files_for_compression) == 0

    file_information_1 = file_info_factory(file_under_consideration_1)
    result_1 = video_compressor.consider_file_for_compression(file_under_consideration=file_information_1)

    assert result_1
    assert len(list_of_files_for_compression) == 1

    matching_files_1 = [file_item for file_item in list_of_files_for_compression
                      if file_item.original_file_name == file_under_consideration_1]
    assert len(matching_files_1) == 1

    assert file_information_1.file_info_type == _CompressorFileInformationType.UnCompressed_Media_File

    
    file_information_2 = file_info_factory(file_under_consideration_2)
    result_2 = video_compressor.consider_file_for_compression(file_under_consideration=file_information_2)

    assert not result_2
    assert len(list_of_files_for_compression) == 1

    matching_files_2 = [file_item for file_item in list_of_files_for_compression
                      if file_item.original_file_name == file_under_consideration_2]
    assert len(matching_files_2) == 0

    assert file_information_2.file_info_type == _CompressorFileInformationType.Unchecked_File

    
    file_information_3 = file_info_factory(file_under_consideration_3)
    result_3 = video_compressor.consider_file_for_compression(file_under_consideration=file_information_3)

    assert result_3
    assert len(list_of_files_for_compression) == 1

    matching_files_3 = [file_item for file_item in list_of_files_for_compression
                      if file_item.original_file_name == file_under_consideration_3]
    assert len(matching_files_3) == 0

    assert file_information_3.file_info_type == _CompressorFileInformationType.UnCompressed_Media_File
