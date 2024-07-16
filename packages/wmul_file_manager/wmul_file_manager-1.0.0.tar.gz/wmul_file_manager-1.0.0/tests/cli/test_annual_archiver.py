"""
@Author = 'Mike Stanley'

============ Change Log ============
2024-May-13 = Created from test_cli.py

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
from click.testing import CliRunner
from wmul_file_manager import cli
from wmul_file_manager.BulkCopier import BulkCopierArguments
from wmul_file_manager.DeleteJunkFiles import DeleteJunkFilesArguments
from wmul_file_manager.EquivalentFileFinder import EquivalentFileFinderArguments
from wmul_test_utils import make_namedtuple
from pathlib import Path
import pytest


@pytest.fixture(scope="function")
def setup_annual_archiver(mocker, fs, request):
    mock_run_annual_archiver = mocker.patch("wmul_file_manager.cli.run_annual_archiver")

    root_folder = Path("/temp")

    source_1 = root_folder / "source_1"
    fs.create_dir(source_1)

    source_2 = root_folder / "source_2"
    fs.create_dir(source_2)
    
    destination_folder = root_folder / "destination"
    fs.create_dir(destination_folder)

    ffmpeg_executable = root_folder / "mp3_exec.txt"
    fs.create_file(ffmpeg_executable)

    ffprobe_executable = root_folder / "ffprobe.exe"
    fs.create_file(ffprobe_executable)

    equivs = ".wav .mp3 .wav .ogg"
    expected_equivs = [".wav", ".mp3", ".wav", ".ogg"]

    junk_exts = ".pk .pkf .sfk"
    expected_junk_exts = [".pk", ".pkf", ".sfk"]

    junk_names = "Thumbs.db"
    expected_junk_names = ["thumbs.db"]

    audio_source_suffixes = ".wav .aiFf"
    expected_audio_source_suffixes = [".wav", ".aiff"]

    audio_file_audio_codec = "mp3"
    expected_audio_file_audio_codec = "mp3"

    audio_file_audio_bitrate = 320
    expected_audio_file_audio_bitrate = 320

    audio_file_destination_suffix = ".mp3"
    expected_audio_file_destination_suffix = ".mp3"

    video_source_suffixes = ".mov .wMv"
    expected_video_source_suffixes = [".mov", ".wmv"]

    video_file_audio_codec = "mp3"
    expected_video_file_audio_codec = "mp3"

    video_file_audio_bitrate = 320
    expected_video_file_audio_bitrate = 320

    video_file_video_codec = "mpeg"
    expected_video_file_video_codec = "mpeg"

    video_file_video_bitrate = 20
    expected_video_file_video_bitrate = 20

    video_destination_suffix = ".m4a"
    expected_video_destination_suffix = ".m4a"

    thread_count = 12
    expected_thread_count = 12

    exclude_suffixes_list = [".docx", ".doc"]

    output_path = root_folder / "foo.txt"

    runner = CliRunner()

    return make_namedtuple(
        "setup_annual_archiver",
        mock_run_annual_archiver=mock_run_annual_archiver,
        source_1=source_1,
        source_2=source_2,
        destination_folder=destination_folder,
        ffmpeg_executable=ffmpeg_executable,
        ffprobe_executable=ffprobe_executable,
        equivs=equivs,
        expected_equivs=expected_equivs,
        junk_exts=junk_exts,
        expected_junk_exts=expected_junk_exts,
        junk_names=junk_names,
        expected_junk_names=expected_junk_names,
        audio_source_suffixes=audio_source_suffixes,
        expected_audio_source_suffixes=expected_audio_source_suffixes,
        audio_file_audio_codec=audio_file_audio_codec,
        expected_audio_file_audio_codec=expected_audio_file_audio_codec,
        audio_file_audio_bitrate=audio_file_audio_bitrate,
        expected_audio_file_audio_bitrate=expected_audio_file_audio_bitrate,
        audio_file_destination_suffix=audio_file_destination_suffix,
        expected_audio_file_destination_suffix=expected_audio_file_destination_suffix,
        video_source_suffixes=video_source_suffixes,
        expected_video_source_suffixes=expected_video_source_suffixes,
        video_file_audio_codec=video_file_audio_codec,
        expected_video_file_audio_codec=expected_video_file_audio_codec,
        video_file_audio_bitrate=video_file_audio_bitrate,
        expected_video_file_audio_bitrate=expected_video_file_audio_bitrate,
        video_file_video_codec=video_file_video_codec,
        expected_video_file_video_codec=expected_video_file_video_codec,
        video_file_video_bitrate=video_file_video_bitrate,
        expected_video_file_video_bitrate=expected_video_file_video_bitrate,
        video_destination_suffix=video_destination_suffix,
        expected_video_destination_suffix=expected_video_destination_suffix,
        thread_count=thread_count,
        expected_thread_count=expected_thread_count,
        exclude_suffixes_list=exclude_suffixes_list,
        output_path=output_path,
        runner=runner
    )



def test_annual_archiver_normal_path(setup_annual_archiver, capsys, caplog):
    mock_run_annual_archiver = setup_annual_archiver.mock_run_annual_archiver
    source_1 = setup_annual_archiver.source_1
    source_2 = setup_annual_archiver.source_2
    destination_folder = setup_annual_archiver.destination_folder
    ffmpeg_executable = setup_annual_archiver.ffmpeg_executable
    ffprobe_executable = setup_annual_archiver.ffprobe_executable
    equivs = setup_annual_archiver.equivs
    expected_equivs = setup_annual_archiver.expected_equivs
    junk_exts = setup_annual_archiver.junk_exts
    expected_junk_exts = setup_annual_archiver.expected_junk_exts
    junk_names = setup_annual_archiver.junk_names
    expected_junk_names = setup_annual_archiver.expected_junk_names
    audio_source_suffixes = setup_annual_archiver.audio_source_suffixes
    expected_audio_source_suffixes = setup_annual_archiver.expected_audio_source_suffixes
    audio_file_audio_codec = setup_annual_archiver.audio_file_audio_codec
    expected_audio_file_audio_codec = setup_annual_archiver.expected_audio_file_audio_codec
    audio_file_audio_bitrate = setup_annual_archiver.audio_file_audio_bitrate
    expected_audio_file_audio_bitrate = setup_annual_archiver.expected_audio_file_audio_bitrate
    audio_file_destination_suffix = setup_annual_archiver.audio_file_destination_suffix
    expected_audio_file_destination_suffix = setup_annual_archiver.expected_audio_file_destination_suffix
    video_source_suffixes = setup_annual_archiver.video_source_suffixes
    expected_video_source_suffixes = setup_annual_archiver.expected_video_source_suffixes
    video_file_audio_codec = setup_annual_archiver.video_file_audio_codec
    expected_video_file_audio_codec = setup_annual_archiver.expected_video_file_audio_codec
    video_file_audio_bitrate = setup_annual_archiver.video_file_audio_bitrate
    expected_video_file_audio_bitrate = setup_annual_archiver.expected_video_file_audio_bitrate
    video_file_video_codec = setup_annual_archiver.video_file_video_codec
    expected_video_file_video_codec = setup_annual_archiver.expected_video_file_video_codec
    video_file_video_bitrate = setup_annual_archiver.video_file_video_bitrate
    expected_video_file_video_bitrate = setup_annual_archiver.expected_video_file_video_bitrate
    video_destination_suffix = setup_annual_archiver.video_destination_suffix
    expected_video_destination_suffix = setup_annual_archiver.expected_video_destination_suffix
    thread_count = setup_annual_archiver.thread_count
    expected_thread_count = setup_annual_archiver.expected_thread_count
    exclude_suffixes_list = setup_annual_archiver.exclude_suffixes_list
    output_path = setup_annual_archiver.output_path
    runner = setup_annual_archiver.runner

    assert True

    invoke_args = [
        str(source_1), str(source_2), str(destination_folder),
        "--ffmpeg_executable", str(ffmpeg_executable)
    ]

    invoke_args.extend(["--equivalent", equivs])
    invoke_args.extend(["--junk_suffix", junk_exts])
    invoke_args.extend(["--junk_name", junk_names])
    invoke_args.extend(["--equiv_rename"])
    invoke_args.extend(["--audio_source_suffixes", audio_source_suffixes])
    invoke_args.extend(["--audio_file_audio_codec", audio_file_audio_codec])
    invoke_args.extend(["--audio_file_audio_bitrate", audio_file_audio_bitrate])
    invoke_args.extend(["--audio_destination_suffix", audio_file_destination_suffix])
    invoke_args.extend(["--video_source_suffixes", video_source_suffixes])
    invoke_args.extend(["--video_file_audio_codec", video_file_audio_codec])
    invoke_args.extend(["--video_file_audio_bitrate", video_file_audio_bitrate])
    invoke_args.extend(["--video_codec", video_file_video_codec])
    invoke_args.extend(["--video_bitrate", video_file_video_bitrate])
    invoke_args.extend(["--video_destination_suffix", video_destination_suffix])
    invoke_args.extend(["--ffmpeg_threads", thread_count])
    invoke_args.extend(["--ffprobe_executable", ffprobe_executable])
    for ext in exclude_suffixes_list:
        invoke_args.extend(["--copy_exclude_ext", ext])

    invoke_args.extend(["--output", str(output_path)])

    result = runner.invoke(cli.annual_archive, invoke_args)
    assert result.exit_code == 0

    expected_sources = [source_1, source_2]

    expected_djf_args = DeleteJunkFilesArguments(
        source_paths=expected_sources,
        junk_suffixes=expected_junk_exts,
        junk_names=expected_junk_names,
        output_path=output_path
    )
    
    expected_eff_args = EquivalentFileFinderArguments(
        source_paths=expected_sources,
        equivalent_suffixes_list=expected_equivs,
        rename_flag=True,
        output_path=output_path
    )

    expected_bc_args = BulkCopierArguments(
        source_directories=expected_sources,
        destination_directory=destination_folder,
        exclude_suffixes_list=exclude_suffixes_list,
        ignore_directories=[],
        force_copy_flag=False,
        delete_old_files_flag=False
    )
    mock_run_annual_archiver.assert_called_once()

    call_kwargs = mock_run_annual_archiver.call_args.kwargs
    assert call_kwargs['delete_junk_files_arguments'] == expected_djf_args
    assert call_kwargs['equivalent_file_finder_arguments'] == expected_eff_args
    assert call_kwargs['bulk_copier_arguments'] == expected_bc_args
    assert call_kwargs['name_comparer_output_file_name'] == output_path

    compress_media_in_folder = call_kwargs['compress_media_in_folder']

    assert compress_media_in_folder.source_paths == expected_sources
