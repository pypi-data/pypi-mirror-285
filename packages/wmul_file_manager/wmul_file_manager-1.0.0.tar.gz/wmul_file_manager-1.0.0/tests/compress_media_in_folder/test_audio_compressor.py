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
from wmul_file_manager.CompressMediaInFolder import AudioCompressor
from wmul_file_manager.utilities import ffmpeg
from wmul_test_utils import make_namedtuple, generate_combination_matrix_from_dataclass


class NumberOfSuffixes(Enum):
    Zero = 0
    One = 1
    Two = 2
    Ten = 10


@dataclass
class audio_compressor_construction_options:
    number_of_suffixes: NumberOfSuffixes


audio_compressor_construction_params, audi_compressor_construction_ids = generate_combination_matrix_from_dataclass(audio_compressor_construction_options)

@pytest.fixture(scope="function", params=audio_compressor_construction_params, ids=audi_compressor_construction_ids)
def setup_audio_compressor_construction(request, fs):
    params = request.param

    if params.number_of_suffixes == NumberOfSuffixes.Zero:
        suffixes = []
        expected_suffixes = []
    elif params.number_of_suffixes == NumberOfSuffixes.One:
        suffixes = [".wAv"]
        expected_suffixes = [".wav"]
    elif params.number_of_suffixes == NumberOfSuffixes.Two:
        suffixes = [".wAv", ".mp3"]
        expected_suffixes = [".wav", ".mp3"]
    else:
        suffixes = [".wAv", ".mp3", ".Ra", ".aiff", ".foo", 
                    ".bar", ".baZ", ".AAA", ".bbb", ".ccc"]
        expected_suffixes = [".wav", ".mp3", ".ra", ".aiff", ".foo", 
                             ".bar", ".baz", ".aaa", ".bbb", ".ccc"]
        
    audio_codec = "mp3"
    audio_bitrate = 160
    destination_suffix = ".mp3"
    ffmpeg_threads = 3
    ffmpeg_executable = Path("/ffmpeg/ffmpeg.exe")


    result = AudioCompressor(
        suffixes=suffixes,
        audio_codec=audio_codec,
        audio_bitrate=audio_bitrate,
        destination_suffix=destination_suffix,
        ffmpeg_threads=ffmpeg_threads,
        ffmpeg_executable=ffmpeg_executable
    )

    return make_namedtuple(
        "setup_audio_compressor",
        params=params,
        suffixes=suffixes,
        expected_suffixes=expected_suffixes,
        audio_codec=audio_codec,
        audio_bitrate=audio_bitrate,
        destination_suffix=destination_suffix,
        ffmpeg_threads=ffmpeg_threads,
        ffmpeg_executable=ffmpeg_executable,
        result=result
    )
    
def test_list_of_files_for_compression_created(setup_audio_compressor_construction):
    list_of_files_for_compression = setup_audio_compressor_construction.result.list_of_files_for_compression

    assert isinstance(list_of_files_for_compression, list)
    assert len(list_of_files_for_compression) == 0

def test_list_of_files_for_deletion_created(setup_audio_compressor_construction):
    list_of_files_for_deletion = setup_audio_compressor_construction.result.list_of_files_for_deletion

    assert isinstance(list_of_files_for_deletion, list)
    assert len(list_of_files_for_deletion) == 0

def test_suffixes_recorded_correctly(setup_audio_compressor_construction):
    result = setup_audio_compressor_construction.result
    expected_suffixes = setup_audio_compressor_construction.expected_suffixes

    assert result.source_suffixes == expected_suffixes

def test_destination_suffix_set_correctly(setup_audio_compressor_construction):
    result = setup_audio_compressor_construction.result
    destination_suffix = setup_audio_compressor_construction.destination_suffix

    assert result.destination_suffix == destination_suffix

def test_call_ffmpeg_created_correctly(setup_audio_compressor_construction):
    call_ffmpeg = setup_audio_compressor_construction.result.call_ffmpeg
    call_ffmpeg_kwargs = call_ffmpeg.keywords
    print(call_ffmpeg_kwargs)
    audio_codec = setup_audio_compressor_construction.audio_codec
    audio_bitrate = setup_audio_compressor_construction.audio_bitrate
    threads = setup_audio_compressor_construction.ffmpeg_threads
    executable_path = setup_audio_compressor_construction.ffmpeg_executable


    assert call_ffmpeg.func == ffmpeg.convert_audio

    assert call_ffmpeg_kwargs['codec'] == audio_codec
    assert call_ffmpeg_kwargs['bitrate'] == audio_bitrate
    assert call_ffmpeg_kwargs['threads'] == threads
    assert call_ffmpeg_kwargs['executable_path'] == executable_path
