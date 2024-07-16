"""
@Author = 'Mike Stanley'

============ Change Log ============
2018-May-01 = Created.

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
from wmul_file_manager.utilities import ffmpeg
from wmul_test_utils import make_namedtuple
import pytest
import subprocess


@pytest.fixture(scope="function")
def setup_ffmpeg(mocker):
    mock_sub_run = mocker.patch("wmul_file_manager.utilities.ffmpeg.subprocess.run")

    input_file_path = "src"
    output_file_path = "dst"
    codec = "mp3"
    bitrate = 160
    threads = '3'
    executable_path = "foo.exe"

    return make_namedtuple(
        "setup_ffmpeg",
        mock_sub_run=mock_sub_run,
        input_file_path=input_file_path,
        output_file_path=output_file_path,
        codec=codec,
        bitrate=bitrate,
        threads=threads,
        executable_path=executable_path
    )


def test_happy_path(setup_ffmpeg):
    mock_sub_run = setup_ffmpeg.mock_sub_run
    input_file_path = setup_ffmpeg.input_file_path
    output_file_path = setup_ffmpeg.output_file_path
    codec = setup_ffmpeg.codec
    bitrate = setup_ffmpeg.bitrate
    threads = setup_ffmpeg.threads
    executable_path = setup_ffmpeg.executable_path

    ffmpeg.convert_audio(
        input_file_path=input_file_path, 
        output_file_path=output_file_path, 
        codec=codec, 
        bitrate=bitrate,
        threads=threads,
        executable_path=executable_path
    )

    expected_codec = "libmp3lame"
    expected_bitrate = "160000"

    mock_sub_run.assert_called_once_with(
        [
            executable_path, 
            "-i", input_file_path, 
            "-codec:a", expected_codec, 
            "-b:a", expected_bitrate, 
            "-threads", threads,
            output_file_path
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )


def test_non_mp3_codec(setup_ffmpeg):
    mock_sub_run = setup_ffmpeg.mock_sub_run
    input_file_path = setup_ffmpeg.input_file_path
    output_file_path = setup_ffmpeg.output_file_path
    bitrate = setup_ffmpeg.bitrate
    threads = setup_ffmpeg.threads
    executable_path = setup_ffmpeg.executable_path

    codec = "aac"

    ffmpeg.convert_audio(
        input_file_path=input_file_path, 
        output_file_path=output_file_path, 
        codec=codec, 
        bitrate=bitrate,
        threads=threads,
        executable_path=executable_path
    )

    expected_bitrate = "160000"

    mock_sub_run.assert_called_once_with(
        [
            executable_path,
            "-i", input_file_path,
            "-codec:a", codec,
            "-b:a", expected_bitrate,
            "-threads", threads,
            output_file_path
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )


def test_non_numeric_bitrate(setup_ffmpeg):
    input_file_path = setup_ffmpeg.input_file_path
    output_file_path = setup_ffmpeg.output_file_path
    codec = setup_ffmpeg.codec
    bitrate = setup_ffmpeg.bitrate
    threads = setup_ffmpeg.threads
    executable_path = setup_ffmpeg.executable_path

    bitrate = "foo"

    with pytest.raises(ValueError):
        ffmpeg.convert_audio(
            input_file_path=input_file_path, 
            output_file_path=output_file_path, 
            codec=codec, 
            bitrate=bitrate,
            threads=threads,
            executable_path=executable_path
        )

bitrates_to_try = [
    (3000, "320000"),
    (193, "320000"),
    (192, "192000"),
    (191, "192000"),
    (161, "192000"),
    (160, "160000"),
    (159, "160000"),
    (97,  "160000"),
    (96,   "96000"),
    (95,   "96000"),
    (0,    "96000"),
    (-1,   "96000")
]

bitrate_ids = [f"{number_ver} : {string_ver}" for number_ver, string_ver in bitrates_to_try]


@pytest.mark.parametrize('bitrate, expected_bitrate', bitrates_to_try, ids=bitrate_ids)
def test_bitrate(setup_ffmpeg, bitrate, expected_bitrate):
    print(f"{bitrate=}\n{expected_bitrate=}")
    mock_sub_run = setup_ffmpeg.mock_sub_run
    input_file_path = setup_ffmpeg.input_file_path
    output_file_path = setup_ffmpeg.output_file_path
    codec = setup_ffmpeg.codec
    threads = setup_ffmpeg.threads
    executable_path = setup_ffmpeg.executable_path

    ffmpeg.convert_audio(
        input_file_path=input_file_path,
        output_file_path=output_file_path, 
        codec=codec, 
        bitrate=bitrate,
        threads=threads,
        executable_path=executable_path
    )

    expected_codec = "libmp3lame"

    mock_sub_run.assert_called_once_with(
        [
            executable_path,
            "-i", input_file_path,
            "-codec:a", expected_codec,
            "-b:a", expected_bitrate,
            "-threads", threads,
            output_file_path
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
