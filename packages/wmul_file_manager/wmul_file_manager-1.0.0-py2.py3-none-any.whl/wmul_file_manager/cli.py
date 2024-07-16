"""
@Author = 'Mike Stanley'

This file exposes the command-line interface to the script.

============ Change Log ============
2024-May-13 = Add compress-media-in-folder, convert-folder-to-mp4.

2024-May-03 = Made Delete Old Files timezone aware.

2023-May-05 = Added timezone argument to is_the_skimmer_working

2018-Jul-05 = Modified cli for DeleteOldFiles to permit either a specified date or a days_older_than argument.

2018-Jun-19 = Added cli for IsTheSkimmerWorking

2018-May-24 = Added cli for DidTheSkimmerCopyTheFiles

2018-May-18 = Added cli for DeleteOldFiles.

2018-May-16 = Added cli for CopyYesterdaysSkimmerFiles.

2018-May-15 = Added cli for FindOldDirectories.

              Added DateParamType, for inputting dates in YYYY-MM-DD format.

2018-May-14 = Added cli for AnnualArchiver.

2018-May-11 = Added cli for FolderComparer.

2018-May-10 = Added cli for EquivalentFileFinder.

              Added PairedParamType, a space-separated argument string.

2018-May-09 = Added cli for DeleteJunkFiles.

2018-May-07 = Added cli for ConvertFolderToMP3.

2018-Apr-30 = Created.

              Added command-line access to BulkCopier.

============ License ============
The MIT License (MIT)

Copyright (c) 2018, 2023-2024 Michael Stanley

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
from pathlib import Path
from wmul_file_manager.BulkCopier import BulkCopierArguments
from wmul_file_manager.BulkCopier import run_script as run_bulk_copier
from wmul_file_manager.CompressMediaInFolder import AudioCompressor, VideoCompressor, NullCompressor, \
    CompressMediaInFolder
from wmul_file_manager.DeleteJunkFiles import DeleteJunkFilesArguments
from wmul_file_manager.DeleteJunkFiles import run_script as run_delete_junk_files
from wmul_file_manager.EquivalentFileFinder import EquivalentFileFinderArguments
from wmul_file_manager.EquivalentFileFinder import run_script as run_equivalent_file_finder
from wmul_file_manager.FolderComparer import FolderComparerArguments
from wmul_file_manager.FolderComparer import run_script as run_folder_comparer
from wmul_file_manager.AnnualArchiver import run_script as run_annual_archiver
from wmul_file_manager.FindOldDirectories import FindOldDirectoriesArguments
from wmul_file_manager.FindOldDirectories import run_script as run_find_old_directories
from wmul_file_manager.CopyYesterdaysSkimmerFiles import run_script as run_skimmer_copy
from wmul_file_manager.DeleteOldFiles import DeleteOldFilesArguments
from wmul_file_manager.DeleteOldFiles import run_script as run_delete_old_files
from wmul_file_manager.DidTheSkimmerCopyTheFiles import DidTheSkimmerCopyTheFiles
from wmul_file_manager.IsTheSkimmerWorking import IsTheSkimmerWorking
from wmul_file_manager.CreateNewsFolders import CreateNewsFoldersArguments
from wmul_file_manager.CreateNewsFolders import run_script as run_create_news_folders
from wmul_file_manager.utilities import skimmer_calendar
import click
import wmul_emailer
import wmul_logger
from zoneinfo import ZoneInfo

_logger = wmul_logger.setup_logger()


class PairedParamType(click.ParamType):
    name = "Paired Type"

    def convert(self, value, param, ctx):
        value_casefold = value.casefold()
        value_list = value_casefold.split()
        number_of_values = len(value_list)
        if number_of_values % 2 == 0:
            return value_list
        else:
            self.fail('%s is not a valid Paired Type. The number of space-separated values must be even. '
                      'E.G. ".wav .mp3" is valid ".wav .mp3 .ogg" is not' % value, param, ctx)


PAIRED = PairedParamType()


class DateParamType(click.ParamType):
    name = "Date Type"

    def convert(self, value, param, ctx):
        try:
            return datetime.datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            self.fail("%s is not a valid Date Type. It must be in the format YYYY-MM-DD." % value, param, ctx)


DATE = DateParamType()


@click.group()
@click.option('--log_name', type=click.Path(exists=False, file_okay=True, dir_okay=False, writable=True), default=None,
              required=False, help="The path to the log file.")
@click.option('--log_level', type=click.IntRange(10,50, clamp=True), required=False, default=30,
              help="The log level: 10: Debug, 20: Info, 30: Warning, 40: Error, 50: Critical. "
                   "Intermediate values (E.G. 32) are permitted, but will essentially be rounded up (E.G. Entering 32 "
                   "is the same as entering 40. Logging messages lower than the log level will not be written to the "
                   "log. E.G. If 30 is input, then all Debug, Info, and Verbose messages will be silenced.")
def wmul_file_manager_cli(log_name, log_level):
    global _logger
    _logger = wmul_logger.setup_logger(file_name=log_name, log_level=log_level)
    _logger.warning("In command_line_interface")


@wmul_file_manager_cli.command()
@click.argument('sources', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True), nargs=-1)
@click.argument('destination', type=click.Path(exists=False, file_okay=False, dir_okay=True, writable=True), nargs=1)
@click.option('--exclude_ext', type=str, multiple=True, help="Extension to exclude from copying.")
@click.option('--ignore_folder', type=click.Path(exists=False, file_okay=False, dir_okay=True, readable=True),
              multiple=True, help="Folders inside the source folder(s) to exclude from copying.")
@click.option('--force_copy', is_flag=True, help="Force-Copy files, even if destination files are newer.")
@click.option('--delete_old', is_flag=True,
              help="Delete files in the destination folder that have no match in the source folder.")
def bulk_copy(sources, destination, exclude_ext, ignore_folder, force_copy, delete_old):
    """
    Script to copy the contents of one folder of into another. If the copy of a particular file fails for any reason,
    it continues with the remaining files (rather than quitting, like Windows). If a file already exists, compares the
    creation and modification times. If the origin file is newer, overwrites the destination file.

    SOURCES The path(s) to the folder(s) to copy.

    DESTINATION The path to the destination folder. The source folder(s) will be copied as subfolders within this
    destination folder.
    """
    _logger.debug("In cli.bulk_copy")
    _logger.info(f"with args: {locals()}")
    source_paths = [Path(item) for item in sources]
    destination_path = Path(destination)

    if exclude_ext:
        exclude_ext = [ext.casefold() for ext in exclude_ext]
    else:
        exclude_ext = []

    if ignore_folder:
        ignore_folder = [Path(folder) for folder in ignore_folder]
    else:
        ignore_folder = []

    arguments = BulkCopierArguments(
        source_directories=source_paths,
        destination_directory=destination_path,
        exclude_suffixes_list=exclude_ext,
        ignore_directories=ignore_folder,
        force_copy_flag=force_copy,
        delete_old_files_flag=delete_old
    )

    run_bulk_copier(arguments=arguments)


@wmul_file_manager_cli.command()
@click.argument('sources', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True), nargs=-1)
@click.argument('executable', type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True), nargs=1)
@click.option('--audio_source_suffixes', type=str, default=".wav",
              help="A space-separated list of the suffixes of the audio files to be compressed. (E.G. '.wav .foo'. Must include the dot ('.')")
@click.option("--audio_file_audio_codec", type=str, default="aac", help="What audio codec to use.")
@click.option("--audio_file_audio_bitrate", type=int, default=160, 
              help="What audio bitrate to use, in kilobits. E.G. 160 is 160 kilobits.")
@click.option("--audio_destination_suffix", type=str, default=".aac", help="The suffix to append to audio files after compression.")
@click.option("--ffprobe_executable", type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
              help="The path to the ffprobe executable.")
@click.option('--video_source_suffixes', type=str, default=".mov",
              help="A space-separated list of the suffixes of the video files to be compressed. (E.G. '.mov .mpeg'. Must include the dot ('.')")
@click.option("--video_file_audio_codec", type=str, default="aac", help="What audio codec to use.")
@click.option("--video_file_audio_bitrate", type=int, default=160, 
              help="What audio bitrate to use, in kilobits. E.G. 160 is 160 kilobits.")
@click.option("--video_codec", type=str, default="h264", help="What video codec to use.")
@click.option("--video_bitrate", type=int, default=10, 
              help="What video bitrate to use, in megabits. E.G. 10 is 10 megabits.")
@click.option("--video_destination_suffix", type=str, default=".mp4", help="The suffix to append to video files after compression.")
@click.option('--threads', type=int, default=3,
              help="How many threads ffmpeg can use Should be <= the number of CPU cores.")
@click.option('--delete', is_flag=True, help="Delete the original media files after compression.")
@click.option('--separate_folder', is_flag=True,
              help="Use a separate folder for the compressed files. Will be the same name as the source folder with "
                   "_cmp appended.")
@click.option('--yesterday', is_flag=True,
              help="Archive yesterday's files. Will search for a folder inside the first source folder that meets the "
                   "format YYYY-MM-DD for yesterday. E.G. If today is May 07, 2018, then it will look for a folder "
                   "named 2018-05-06.")
def compress_media_in_folder(sources, executable, audio_source_suffixes, audio_file_audio_codec, 
                             audio_file_audio_bitrate, audio_destination_suffix, ffprobe_executable, video_source_suffixes, 
                             video_file_audio_codec, video_file_audio_bitrate, video_codec, video_bitrate, 
                             video_destination_suffix, threads, delete, separate_folder, yesterday):
    """
    Script to compress all the media in a folder.
    
    SOURCES The path(s) containing the files to be compressed. All subfolders will also be compressed.

    EXECUTABLE The path to the ffmpeg executable. It does not have to actually be ffmpeg, but does need to use the
    same command-line API as ffmpeg.
    """
    _logger.info(f"With args: {locals()}")

    audio_source_suffixes = audio_source_suffixes.split()
    video_source_suffixes = video_source_suffixes.split()

    audio_compressor = AudioCompressor(
        suffixes=audio_source_suffixes,
        audio_codec=audio_file_audio_codec,
        audio_bitrate=audio_file_audio_bitrate,
        destination_suffix=audio_destination_suffix,
        ffmpeg_threads=threads,
        ffmpeg_executable=executable
    )

    video_compressor = VideoCompressor(
        suffixes=video_source_suffixes,
        video_codec=video_codec,
        video_bitrate=video_bitrate,
        audio_codec=video_file_audio_codec,
        audio_bitrate=video_file_audio_bitrate,
        destination_suffix=video_destination_suffix,
        ffmpeg_threads=threads,
        ffmpeg_executable=executable,
        ffprobe_executable=ffprobe_executable
    )
    
    source_folders = [Path(source_path) for source_path in sources]

    cmif = CompressMediaInFolder(
        source_paths=source_folders,
        audio_compressor=audio_compressor,
        video_compressor=video_compressor,
        separate_folder_flag=separate_folder,
        delete_files_flag=delete
    )

    if yesterday:
        cmif.archive_yesterdays_folders()
    else:
        cmif.archive_list_of_folders()


@wmul_file_manager_cli.command()
@click.argument('sources', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True), nargs=-1)
@click.argument('executable', type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True), nargs=1)
@click.option('--audio_source_suffixes', type=str, default=".wav",
              help="A space-separated list of the suffixes of the audio files to be compressed. (E.G. '.wav .foo'. Must include the dot ('.')")
@click.option("--audio_file_audio_codec", type=str, default="aac", help="What audio codec to use.")
@click.option("--audio_file_audio_bitrate", type=int, default=160, 
              help="What audio bitrate to use, in kilobits. E.G. 160 is 160 kilobits.")
@click.option("--audio_destination_suffix", type=str, default=".aac", help="The suffix to append to audio files after compression.")
@click.option('--threads', type=int, default=3,
              help="How many threads ffmpeg can use Should be <= the number of CPU cores.")
@click.option('--delete', is_flag=True, help="Delete the original media files after compression.")
@click.option('--separate_folder', is_flag=True,
              help="Use a separate folder for the compressed files. Will be the same name as the source folder with "
                   "_cmp appended.")
@click.option('--yesterday', is_flag=True,
              help="Archive yesterday's files. Will search for a folder inside the first source folder that meets the "
                   "format YYYY-MM-DD for yesterday. E.G. If today is May 07, 2018, then it will look for a folder "
                   "named 2018-05-06.")
def compress_audio_in_folder(sources, executable, audio_source_suffixes, audio_file_audio_codec, 
                             audio_file_audio_bitrate, audio_destination_suffix, threads, delete, separate_folder, 
                             yesterday):
    """
    Script to compress all the audio in a folder.
    
    SOURCES The path(s) containing the files to be compressed. All subfolders will also be compressed.

    EXECUTABLE The path to the ffmpeg executable. It does not have to actually be ffmpeg, but does need to use the
    same command-line API as ffmpeg.
    """
    _logger.info(f"With args: {locals()}")

    audio_source_suffixes = audio_source_suffixes.split()

    audio_compressor = AudioCompressor(
        suffixes=audio_source_suffixes,
        audio_codec=audio_file_audio_codec,
        audio_bitrate=audio_file_audio_bitrate,
        destination_suffix=audio_destination_suffix,
        ffmpeg_threads=threads,
        ffmpeg_executable=executable
    )
    
    source_folders = [Path(source_path) for source_path in sources]

    cmif = CompressMediaInFolder(
        source_paths=source_folders,
        audio_compressor=audio_compressor,
        video_compressor=NullCompressor(),
        separate_folder_flag=separate_folder,
        delete_files_flag=delete
    )

    if yesterday:
        cmif.archive_yesterdays_folders()
    else:
        cmif.archive_list_of_folders()


@wmul_file_manager_cli.command()
@click.argument('sources', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True), nargs=-1)
@click.argument('executable', type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True), nargs=1)
@click.option("--ffprobe_executable", type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
              help="The path to the ffprobe executable.")
@click.option('--video_source_suffixes', type=str, default=".mov",
              help="A space-separated list of the suffixes of the video files to be compressed. (E.G. '.mov .mpeg'. Must include the dot ('.')")
@click.option("--video_file_audio_codec", type=str, default="aac", help="What audio codec to use.")
@click.option("--video_file_audio_bitrate", type=int, default=160, 
              help="What audio bitrate to use, in kilobits. E.G. 160 is 160 kilobits.")
@click.option("--video_codec", type=str, default="h264", help="What video codec to use.")
@click.option("--video_bitrate", type=int, default=10, 
              help="What video bitrate to use, in megabits. E.G. 10 is 10 megabits.")
@click.option("--video_destination_suffix", type=str, default=".mp4", help="The suffix to append to video files after compression.")
@click.option('--threads', type=int, default=3,
              help="How many threads ffmpeg can use Should be <= the number of CPU cores.")
@click.option('--delete', is_flag=True, help="Delete the original media files after compression.")
@click.option('--separate_folder', is_flag=True,
              help="Use a separate folder for the compressed files. Will be the same name as the source folder with "
                   "_cmp appended.")
@click.option('--yesterday', is_flag=True,
              help="Archive yesterday's files. Will search for a folder inside the first source folder that meets the "
                   "format YYYY-MM-DD for yesterday. E.G. If today is May 07, 2018, then it will look for a folder "
                   "named 2018-05-06.")
def compress_video_in_folder(sources, executable, ffprobe_executable, video_source_suffixes, video_file_audio_codec, 
                             video_file_audio_bitrate, video_codec, video_bitrate, video_destination_suffix, threads, 
                             delete, separate_folder, yesterday):
    """
    Script to compress all the videos in a folder.
    
    SOURCES The path(s) containing the files to be compressed. All subfolders will also be compressed.

    EXECUTABLE The path to the ffmpeg executable. It does not have to actually be ffmpeg, but does need to use the
    same command-line API as ffmpeg.
    """
    _logger.info(f"With args: {locals()}")

    video_source_suffixes = video_source_suffixes.split()

    video_compressor = VideoCompressor(
        suffixes=video_source_suffixes,
        video_codec=video_codec,
        video_bitrate=video_bitrate,
        audio_codec=video_file_audio_codec,
        audio_bitrate=video_file_audio_bitrate,
        destination_suffix=video_destination_suffix,
        ffmpeg_threads=threads,
        ffmpeg_executable=executable,
        ffprobe_executable=ffprobe_executable
    )
    
    source_folders = [Path(source_path) for source_path in sources]

    cmif = CompressMediaInFolder(
        source_paths=source_folders,
        audio_compressor=NullCompressor(),
        video_compressor=video_compressor,
        separate_folder_flag=separate_folder,
        delete_files_flag=delete
    )

    if yesterday:
        cmif.archive_yesterdays_folders()
    else:
        cmif.archive_list_of_folders()


@wmul_file_manager_cli.command()
@click.argument('sources', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True), nargs=-1)
@click.option('--junk_ext', type=str, default='.pk .pkf .sfk .sfap0 .tmp',
              help='A space-separated list of the extensions of the junk files. Enclose in quotation marks. '
                   'E.G. ".sfk .pk"')
@click.option('--junk_name', type=str, default="Thumbs.db .DS_Store",
                 help='"A space-separated list of the names of the junk files. Enclose in quotation marks. '
                      'E.G. "Thumbs.db .DS_Store"')
@click.option('--output', type=click.Path(file_okay=True, dir_okay=False, writable=True), default=None,
              help="The path to write the results text to. Leave blank to print to standard out.")
def delete_junk_files(sources, junk_ext, junk_name, output):
    _logger.debug("In cli.delete_junk_files")
    _logger.info(f"with args: {locals()}")

    source_paths = [Path(item) for item in sources]

    junk_ext = junk_ext.casefold()
    junk_extensions = junk_ext.split()

    junk_name = junk_name.casefold()
    junk_names = junk_name.split()

    arguments = DeleteJunkFilesArguments(
        source_paths=source_paths,
        junk_suffixes=junk_extensions,
        junk_names=junk_names,
        output_path=output
    )

    run_delete_junk_files(arguments)


@wmul_file_manager_cli.command()
@click.argument('sources', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True), nargs=-1)
@click.argument('equivalent', type=PAIRED)
@click.option('--rename', is_flag=True, help="Rename the files when found.")
@click.option('--output', type=click.Path(file_okay=True, dir_okay=False, writable=True), default=None,
              help="The path to write the results text to. Leave blank to print to standard out.")
def find_equivalent_files(sources, equivalent, rename, output):
    """
    Iterates through each given folder and its subfolders. It finds files in the same folder that differ only by
    their suffix. This is to find cases where someone has created both a .wav and .mp3 version of the same file.
    E.G. foo.wav and foo.mp3.

    Optionally, the files can be renamed where the original suffix is added to the name.
    E.G. blah.wav, blah.mp3 become blah_wav.wav and blah_mp3.mp3

    This prepares folders for bulk mp3ing by ConvertFolderToMP3.py

    SOURCES  The path(s) to the root folder(s) from which to find equivalent files.

    EQUIVALENT  Pairs of equivalent extensions. List one after the other. E.G.: .wav .mp3.

    Pairs are reflective. E.G. .wav .mp3 is the same as .mp3 .wav.

    Multiple pairs are needed to indicate multiple equivalences. E.G. .wav .mp3 .wav .ogg.
    (Inputting .wav .mp3 .ogg will not work.)

    Pairs are transitive. IE .wav .mp3 .wav .ogg indicates an equivalency between .mp3 and .ogg.
    """
    _logger.debug("In cli.find_equivalent_files")
    _logger.info(f"with args: {locals()}")

    source_paths = [Path(item) for item in sources]
    if output:
        output = Path(output)

    arguments = EquivalentFileFinderArguments(
        source_paths=source_paths,
        equivalent_suffixes_list=equivalent,
        rename_flag=rename,
        output_path=output
    )

    run_equivalent_file_finder(arguments)


@wmul_file_manager_cli.command()
@click.argument('first', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True))
@click.argument('second', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True))
@click.option('--ignore', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True), multiple=True,
              help="The path[s] inside the first folder to be ignored")
@click.option('--equivalent', type=PAIRED,
              help="Pairs of equivalent extensions. List one after the other. E.G.: .wav .mp3. Pairs are reflective. "
                   "E.G. .wav .mp3 is the same as .mp3 .wav. Multiple pairs are needed to indicate multiple "
                   "equivalences. E.G. .wav .mp3 .wav .ogg. Inputting .wav .mp3 .ogg will not work.  Pairs are "
                   "transitive. E.G. .wav .mp3 .wav .ogg indicates an equivalency between .mp3 and .ogg.")
@click.option('--name_only', is_flag=True, help="Compare only by name, ignore size and timestamp.")
@click.option('--name_size_only', is_flag=True, help="Compare only by name and size, ignore timestamp.")
@click.option('--output', type=click.Path(file_okay=True, dir_okay=False, writable=True), default=None,
              help="The path to write the results text to. Leave blank to print to standard out.")
def compare_folders(first, second, ignore, equivalent, name_only, name_size_only, output):
    """
    This script compares the contents of two folders. E.G. A Folder and its backup folder.

    It does this in one of two ways. 1) By same relative path, then by modification time (mtime), then by size.
    2) By same relative path, including equivalent suffixes.

    Relative path example: original/foo/bar.txt, backup/foo/bar.txt
    Equivalent suffix example: original/foo/bar.wav, backup/foo/bar.mp3

    If prints four lists of files:
    1) Any files or directories for which the system lacks read permission.
    2) Any files in the first directory which would be duplicates with equivalent suffixes.
    E.G. original/foo/bar.wav, original/foo/bar.mp3
    3) Any files that are in the first directory but not the second.
    4) Any files that are in the second directory but not the first.

    When method 1 is used for comparison, then lists 3 and 4 would include files that are in both folders, but with
    different mtimes and/or sizes.

    FIRST   The path to the first folder.

    SECOND  The path to the second folder.
    """
    _logger.debug("Starting FolderComparer")
    _logger.info(f"with args: {locals()}")

    first = Path(first)
    second = Path(second)

    if ignore:
        ignore_paths = [Path(this_path) for this_path in ignore]
    else:
        ignore_paths = []

    if output:
        output = Path(output)

    arguments = FolderComparerArguments(
        first_path=first,
        second_path=second,
        ignore_paths=ignore_paths,
        equivalent_suffixes=equivalent,
        name_only=name_only,
        name_size_only=name_size_only,
        output_path=output
    )

    run_folder_comparer(arguments)


@wmul_file_manager_cli.command()
@click.argument('sources', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True), nargs=-1)
@click.argument('destination', type=click.Path(exists=False, file_okay=False, dir_okay=True, writable=True), nargs=1)
@click.option('--equivalent', type=PAIRED,
              help="Pairs of equivalent extensions. List one after the other. E.G.: .wav .mp3. Pairs are reflective. "
                   "E.G. .wav .mp3 is the same as .mp3 .wav. Multiple pairs are needed to indicate multiple "
                   "equivalences. E.G. .wav .mp3 .wav .ogg. Inputting .wav .mp3 .ogg will not work.  Pairs are "
                   "transitive. E.G. .wav .mp3 .wav .ogg indicates an equivalency between .mp3 and .ogg.")
@click.option('--junk_suffix', type=str, default='.pk .pkf .sfk .sfap0 .tmp',
              help='A space-separated list of the extensions of the junk files. Enclose in quotation marks. '
                   'E.G. ".sfk .pk"')
@click.option('--junk_name', type=str, default="Thumbs.db .DS_Store",
                 help='"A space-separated list of the names of the junk files. Enclose in quotation marks. '
                      'E.G. "Thumbs.db .DS_Store"')
@click.option('--equiv_rename', is_flag=True, help="Rename the files when found.")
@click.option('--audio_source_suffixes', type=str, default=".wav",
              help="A space-separated list of the suffixes of the audio files to be compressed. (E.G. '.wav .foo'. Must include the dot ('.')")
@click.option("--audio_file_audio_codec", type=str, default="aac", help="What audio codec to use.")
@click.option("--audio_file_audio_bitrate", type=int, default=160, 
              help="What audio bitrate to use, in kilobits. E.G. 160 is 160 kilobits.")
@click.option("--audio_destination_suffix", type=str, default=".aac", help="The suffix to append to audio files after compression.")
@click.option("--ffprobe_executable", type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
              help="The path to the ffprobe executable.")
@click.option('--video_source_suffixes', type=str, default=".mov",
              help="A space-separated list of the suffixes of the video files to be compressed. (E.G. '.mov .mpeg'. Must include the dot ('.')")
@click.option("--video_file_audio_codec", type=str, default="aac", help="What audio codec to use.")
@click.option("--video_file_audio_bitrate", type=int, default=160, 
              help="What audio bitrate to use, in kilobits. E.G. 160 is 160 kilobits.")
@click.option("--video_codec", type=str, default="h264", help="What video codec to use.")
@click.option("--video_bitrate", type=int, default=10, 
              help="What video bitrate to use, in megabits. E.G. 10 is 10 megabits.")
@click.option("--video_destination_suffix", type=str, default=".mp4", help="The suffix to append to video files after compression.")
@click.option('--ffmpeg_executable', type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True), 
              nargs=1, help="Path to ffmpeg executable.", required=True)
@click.option('--ffmpeg_threads', type=int, default=3,
              help="How many threads ffmpeg can use Should be <= the number of CPU cores.")
@click.option('--copy_exclude_ext', type=str, multiple=True, help="Extension to exclude from copying.")
@click.option('--output', type=click.Path(file_okay=True, dir_okay=False, writable=True), default=None,
              help="The path to write the results text to. Leave blank to print to standard out.")
def annual_archive(sources, destination, equivalent, junk_suffix, junk_name, equiv_rename, audio_source_suffixes, 
                   audio_file_audio_codec, audio_file_audio_bitrate, audio_destination_suffix, ffprobe_executable,
                   video_source_suffixes, video_file_audio_codec, video_file_audio_bitrate, video_codec, video_bitrate, 
                   video_destination_suffix, ffmpeg_executable, ffmpeg_threads, copy_exclude_ext, output):
    """
    For yearly archiving. Deletes the junk files, renames equivalent files, copies everything to a separate directory,
    compresses the audio and video files, and does a final comparison to check for missing files.

    SOURCES The path(s) to the folder(s) to copy.

    DESTINATION The path to the destination folder. The source folder(s) will be copied as subfolders within this
    destination folder.
    """
    _logger.debug("Starting AnnualArchiver")
    _logger.info(f"with args: {locals()}")

    destination = Path(destination)
    if output:
        output = Path(output)
    sources = [Path(item) for item in sources]

    junk_suffix = junk_suffix.casefold()
    junk_suffix = junk_suffix.split()

    junk_name = junk_name.casefold()
    junk_names = junk_name.split()

    if copy_exclude_ext:
        copy_exclude_ext = [ext.casefold() for ext in copy_exclude_ext]
    else:
        copy_exclude_ext = []

    delete_junk_files_arguments = DeleteJunkFilesArguments(
        source_paths=sources,
        junk_suffixes=junk_suffix,
        junk_names=junk_names,
        output_path=output
    )

    equivalent_file_finder_arguments = EquivalentFileFinderArguments(
        source_paths=sources,
        equivalent_suffixes_list=equivalent,
        rename_flag=equiv_rename,
        output_path=output
    )

    bulk_copier_arguments = BulkCopierArguments(
        source_directories=sources,
        destination_directory=destination,
        exclude_suffixes_list=copy_exclude_ext,
        ignore_directories=[],
        force_copy_flag=False,
        delete_old_files_flag=False
    )

    audio_source_suffixes = audio_source_suffixes.split()
    video_source_suffixes = video_source_suffixes.split()

    audio_compressor = AudioCompressor(
        suffixes=audio_source_suffixes,
        audio_codec=audio_file_audio_codec,
        audio_bitrate=audio_file_audio_bitrate,
        destination_suffix=audio_destination_suffix,
        ffmpeg_threads=ffmpeg_threads,
        ffmpeg_executable=ffmpeg_executable
    )

    video_compressor = VideoCompressor(
        suffixes=video_source_suffixes,
        video_codec=video_codec,
        video_bitrate=video_bitrate,
        audio_codec=video_file_audio_codec,
        audio_bitrate=video_file_audio_bitrate,
        destination_suffix=video_destination_suffix,
        ffmpeg_threads=ffmpeg_threads,
        ffmpeg_executable=ffmpeg_executable,
        ffprobe_executable=ffprobe_executable
    )
    
    source_folders = [Path(source_path) for source_path in sources]

    cmif = CompressMediaInFolder(
        source_paths=source_folders,
        audio_compressor=audio_compressor,
        video_compressor=video_compressor,
        separate_folder_flag=True,
        delete_files_flag=True
    )

    run_annual_archiver(
        delete_junk_files_arguments=delete_junk_files_arguments, 
        equivalent_file_finder_arguments=equivalent_file_finder_arguments, 
        bulk_copier_arguments=bulk_copier_arguments,
        compress_media_in_folder=cmif, 
        name_comparer_output_file_name=output
    )


@wmul_file_manager_cli.command()
@click.argument("first_path", type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True), nargs=1)
@click.argument("cutoff", type=DATE, nargs=1)
@click.option('--junk_suffix', type=str, default='',
              help='A space-separated list of the extensions of the junk files. Enclose in quotation marks. '
                   'E.G. ".sfk .pk"')
@click.option('--junk_name', type=str, default="",
                 help='"A space-separated list of the names of the junk files. Enclose in quotation marks. '
                      'E.G. "Thumbs.db .DS_Store"')
@click.option('--output', type=click.Path(file_okay=True, dir_okay=False, writable=True), default=None,
              help="The path to write the results text to. Leave blank to print to standard out.")
def find_old_directories(first_path, cutoff, junk_suffix, junk_name, output):
    """
    This script will search within a given directory and find all the top level folders that only have files
    older than the cutoff date.

    E.G.: If you pass it Z:, and Z: contains
    Z:
    | - Adam
    | - Betty
    | - Carl

    It will search each folder for new files. If Adam contains any files that are newer than the cutoff, Adam will be
    marked as new. The directory structure below the top level does not matter. Top level folders are considered new if
    they contain a new file anywhere within them. Otherwise they are old.

    FIRST_PATH The starting path.

    CUTOFF The cutoff date. Any top level folders containing only files older than or equal to this date will be
    marked as old. Format YYYY-MM-DD.
    """
    _logger.info(f"In cli.find_old_directories with: {locals()}")

    first_path = Path(first_path)
    if output:
        output = Path(output)
    cutoff = cutoff.replace(hour=23, minute=59, second=59)

    junk_suffix = junk_suffix.casefold()
    junk_suffix = junk_suffix.split()

    junk_name = junk_name.casefold()
    junk_names = junk_name.split()

    arguments = FindOldDirectoriesArguments(
        first_path=first_path,
        recent_cutoff=cutoff,
        junk_suffixes=junk_suffix,
        junk_names=junk_names,
        output_path=output
    )

    run_find_old_directories(arguments)


@wmul_file_manager_cli.command()
@click.option("--pair", type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True), multiple=True,
              nargs=2, help="A source, destination path pair.", required=True)
def copy_skimmer(pair):
    """
    Script to copy yesterday's skimmer files. For each --pair input, it looks 
    for yesterday's date directory under the source directory. The date folder 
    must be in YYYY-MM-DD format. E.G. If today is 2018-May-16 and the source
    folder is D:\\Skimmer\\, it will look for D:\\Skimmer\\2018-05-15\\.

    It copies the files in the source date folder to the destination date 
    folder. E.G. The destination is U:\\Skimmer\\, it will copy to 
    U:\\Skimmer\\2018-05-15\\.
    """
    _logger.debug(f"In copy_skimmer with {locals()}")
    source_destination_pairs = []
    for source, destination in pair:
        source = Path(source)
        destination = Path(destination)
        source_destination_pairs.append((source, destination))

    run_skimmer_copy(source_destination_path_pairs=source_destination_pairs)


@wmul_file_manager_cli.command()
@click.argument("first_path", type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True), nargs=1)
@click.option("--days_old", type=int, nargs=1,
              help="The number of days old a file must be to be deleted, rounded to the nearest day. "
                   "E.G. If today is the 12th and the user inputs '7', then all files from the 4th and older will be "
                   "deleted.")
@click.option("--cutoff_date", type=DATE, nargs=1,
              help="The cutoff date for which old files should be deleted. Any files older than this date will be "
                   "deleted, any files newer or equal to this date will be kept.")
@click.option("--remove_folders", is_flag=True,
              help="Delete any folders that are empty after the old files have been deleted.")
@click.option('--suffixes', type=str, help="The suffix(es) of the old files to be deleted. Must include the dot ('.'). "
                                           "If this is left blank, all old files will be deleted.")
def delete_old_files(first_path, days_old, cutoff_date, remove_folders, suffixes):
    """
    Deletes old files and directories off a given root directory.

    FIRST_PATH  The directory in which to begin the search for old files. All old files in this directory and its
    sub-directories will be deleted.

    Either --days_old, or --cutoff_date must be provided.
    """

    if not (days_old or cutoff_date):
        raise click.BadOptionUsage("Neither the --days_old nor --cutoff_date argument were used. "
                                   "One or the other (but not both) must be provided.")
    if days_old and cutoff_date:
        raise click.BadOptionUsage("Both --days_old and --cutoff_date were provided, you must choose one or the "
                                   "other.")

    if days_old:
        days_old = datetime.timedelta(days=days_old)
        cutoff_date = datetime.datetime.today() - days_old
        cutoff_date = cutoff_date.replace(hour=0, minute=0, second=0, microsecond=0)

    cutoff_date = cutoff_date.astimezone(tz=datetime.timezone.utc)

    _logger.info(f"In cli.delete_old_files with: {locals()}")
    arguments = DeleteOldFilesArguments(
        source_path=Path(first_path),
        remove_folders_flag=remove_folders,
        limited_suffixes_flag=bool(suffixes),
        limited_suffixes_list=suffixes,
        older_than=cutoff_date
    )

    run_delete_old_files(arguments)


@wmul_file_manager_cli.command()
@click.argument('sources', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True), nargs=-1)
@click.argument("calendar", type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
@click.option("--email", type=str, multiple=True, required=True,
              help="The e-mail address to which the results should be sent.")
@click.option("--server", type=str, required=True, help="The address of the e-mail server to use.")
@click.option("--port", type=int, default=25, help="The port of the e-mail server.")
@click.option("--username", type=str, required=True, help="The username to authenticate with the e-mail server.")
@click.option("--password", type=str, required=False, help="The password to authenticate with the e-mail server.")
def did_skimmer_copy(sources, calendar, email, server, port, username, password):
    """
    Checks the provided folders and makes certain that yesterday's skimmer files were copied to that location. If they
    were not, it sends an e-mail.

    SOURCE The path(s) to the directory(s) to be checked.

    CALENDAR The path to the calendar file.

    Calendar Format:
    Lines beginning with # are comments
    Each day must have a line dedicated to it.
    Each line should begin with the day abbreviation a comma, and then a comma-separated list of how many files there
    should be for that hour beginning with 12 AM.
    Mon, 4, 4, 5, 4, ...
    Indicates that on Monday, the 12 AM, 1 AM, and 3 AM hours should have 4 files and the 2 AM hour should have 5 files.
    Abbreviations: Mon, Tue, Wed, Thu, Fri, Sat, Sun
    """
    _logger.info(f"In cli.did_skimmer_copy with: {locals()}")

    calendar = Path(calendar)
    directories_arg = [Path(source_path) for source_path in sources]

    emailer = wmul_emailer.EmailSender(
        server_host=server,
        port=port,
        user_name=username,
        password=password,
        destination_email_addresses=email,
        from_email_address='skimmer_copy_watcher@wmul-nas-4'
    )

    _skimmer_calendar = skimmer_calendar.load_skimmer_calendar(calendar)

    did_skimmer_copy = DidTheSkimmerCopyTheFiles(
        directories=directories_arg,
        _skimmer_calendar=_skimmer_calendar,
        emailer=emailer
    )
    did_skimmer_copy.run_script()


@wmul_file_manager_cli.command()
@click.argument('sources', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True), nargs=-1)
@click.argument("calendar", type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
@click.option("--email", type=str, multiple=True, required=True,
              help="The e-mail address to which the results should be sent.")
@click.option("--server", type=str, required=True, help="The address of the e-mail server to use.")
@click.option("--port", type=int, default=25, help="The port of the e-mail server.")
@click.option("--username", type=str, required=False, help="The username to authenticate with the e-mail server.")
@click.option("--password", type=str, required=False, help="The password to authenticate with the e-mail server.")
@click.option("--timezone", type=str, required=False, help="The TimeZone to use when computing the current time. Needs to match IANA database.")
def is_skimmer_working(sources, calendar, email, server, port, username, password, timezone):
    _logger.info(f"In cli.is_skimmer_working with: {locals()}")

    calendar = Path(calendar)
    directories_arg = [Path(source_path) for source_path in sources]

    emailer = wmul_emailer.EmailSender(
        server_host=server,
        port=port,
        user_name=username,
        password=password,
        destination_email_addresses=email,
        from_email_address='skimmer_watcher@wmul-nas-4'
    )

    _skimmer_calendar = skimmer_calendar.load_skimmer_calendar(calendar)

    if timezone:
        timezone_info = ZoneInfo(timezone)
    else:
        timezone_info = None

    isw = IsTheSkimmerWorking(emailer=emailer, _skimmer_calendar=_skimmer_calendar, timezone=timezone_info)
    isw.run_script(directory_list=directories_arg)


@wmul_file_manager_cli.command()
@click.argument("start_date", type=DATE)
@click.argument("end_date", type=DATE)
@click.argument("starting_folder", type=click.Path(file_okay=False, dir_okay=True, writable=True))
def create_news_folders(start_date, end_date, starting_folder):

    starting_folder = Path(starting_folder)
    
    cnf_arguments = CreateNewsFoldersArguments(
        start_date=start_date,
        end_date=end_date,
        starting_folder=starting_folder
    )

    run_create_news_folders(cnf_arguments)
