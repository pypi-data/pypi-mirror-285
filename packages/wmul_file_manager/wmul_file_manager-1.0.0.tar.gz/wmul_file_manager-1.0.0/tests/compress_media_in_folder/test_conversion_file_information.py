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
import pytest
from pathlib import Path
from wmul_file_manager.CompressMediaInFolder import _CompressorFileInformation, _CompressorFileInformationType
from wmul_test_utils import make_namedtuple, generate_true_false_matrix_from_list_of_strings


conversion_file_information_params, conversion_file_information_ids = generate_true_false_matrix_from_list_of_strings (
    "conversion_file_information_options",
    [
        "return_zero"
    ]
)


@pytest.fixture(scope="function", params=conversion_file_information_params, ids=conversion_file_information_ids)
def setup_conversion_file_information(fs, mocker, request):
    params = request.param
    source_file_path = Path("/foo/bar/baz.mov")
    fs.create_file(source_file_path)
    source_root_path = Path("/foo/")
    converted_files_final_folder = Path("/converted/")
    final_suffix = ".final_suffix"

    expected_destination_path = Path("/converted/bar/baz.final_suffix")
    expected_str = "_CompressorFileInformation:\t_CompressorFileInformationType.Unchecked_File\t\\foo\\bar\\baz.mov"

    if params.return_zero:
        return_code = 0
    else:
        return_code = -1

    mock_call_ffmpeg = mocker.Mock(return_value=return_code)

    file_info_under_test = _CompressorFileInformation(
        source_file_path=source_file_path,
        source_root_path=source_root_path,
        compressed_files_folder=converted_files_final_folder
    )

    return make_namedtuple(
        "setup_conversion_file_information",
        params=params,
        source_file_path=source_file_path,
        source_root_path=source_root_path,
        converted_files_final_folder=converted_files_final_folder,
        expected_destination_path=expected_destination_path,
        expected_str=expected_str,
        final_suffix=final_suffix,
        mock_call_ffmpeg=mock_call_ffmpeg,
        file_info_under_test=file_info_under_test
    )

def test_file_info_type_set_correctly(setup_conversion_file_information):
    file_info_under_test = setup_conversion_file_information.file_info_under_test
    assert file_info_under_test.file_info_type == _CompressorFileInformationType.Unchecked_File

def test_original_file_name_set_correctly(setup_conversion_file_information):
    file_info_under_test = setup_conversion_file_information.file_info_under_test
    source_file_path = setup_conversion_file_information.source_file_path

    assert file_info_under_test.original_file_name == source_file_path

def test_str(setup_conversion_file_information):
    file_info_under_test = setup_conversion_file_information.file_info_under_test
    expected_str = setup_conversion_file_information.expected_str

    assert str(file_info_under_test) == expected_str

def test_compute_destination_path(setup_conversion_file_information):
    file_info_under_test = setup_conversion_file_information.file_info_under_test
    final_suffix = setup_conversion_file_information.final_suffix
    expected_destination_path = setup_conversion_file_information.expected_destination_path

    assert file_info_under_test.destination_path == ""
    file_info_under_test._compute_destination_path(final_suffix)
    assert file_info_under_test.destination_path == expected_destination_path

def test_set_as_media_file(setup_conversion_file_information):
    file_info_under_test = setup_conversion_file_information.file_info_under_test
    final_suffix = setup_conversion_file_information.final_suffix
    expected_destination_path = setup_conversion_file_information.expected_destination_path

    file_info_under_test.set_as_media_file(final_suffix=final_suffix)
    assert file_info_under_test.destination_path == expected_destination_path
    assert file_info_under_test.file_info_type == _CompressorFileInformationType.UnCompressed_Media_File

def test_set_as_non_media_file(setup_conversion_file_information):
    file_info_under_test = setup_conversion_file_information.file_info_under_test
    file_info_under_test.set_as_non_media_file()
    assert file_info_under_test.file_info_type == _CompressorFileInformationType.Non_Media_file

def test_convert(setup_conversion_file_information):
    params = setup_conversion_file_information.params
    file_info_under_test = setup_conversion_file_information.file_info_under_test
    source_file_path = setup_conversion_file_information.source_file_path
    expected_destination_path = setup_conversion_file_information.expected_destination_path
    mock_call_ffmpeg = setup_conversion_file_information.mock_call_ffmpeg
    final_suffix = setup_conversion_file_information.final_suffix

    file_info_under_test.set_as_media_file(final_suffix=final_suffix)

    result = file_info_under_test.compress(call_ffmpeg=mock_call_ffmpeg)

    destination_parent = expected_destination_path.parent
    assert destination_parent.exists()

    mock_call_ffmpeg.assert_called_once_with(
        input_file_path=source_file_path,
        output_file_path=expected_destination_path
    )

    if params.return_zero:
        assert result
        assert file_info_under_test.file_info_type == _CompressorFileInformationType.Compressed_Media_File
    else:
        assert not result
        assert file_info_under_test.file_info_type == _CompressorFileInformationType.UnCompressed_Media_File

def test_delete(setup_conversion_file_information):
    params = setup_conversion_file_information.params
    file_info_under_test = setup_conversion_file_information.file_info_under_test
    final_suffix = setup_conversion_file_information.final_suffix
    mock_call_ffmpeg = setup_conversion_file_information.mock_call_ffmpeg

    assert file_info_under_test.original_file_name.exists()
    file_info_under_test.set_as_media_file(final_suffix=final_suffix)
    file_info_under_test.compress(call_ffmpeg=mock_call_ffmpeg)
    assert file_info_under_test.original_file_name.exists()
    file_info_under_test.delete()
    if params.return_zero:
        assert not file_info_under_test.original_file_name.exists()
    else:
        assert file_info_under_test.original_file_name.exists()
