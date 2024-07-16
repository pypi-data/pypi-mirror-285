"""
@Author = 'Mike Stanley'

Script to compress all of the media in a directory or set of directories. Video files are compressed into mp4 format 
and audio files into mp3 format. 

It uses ffmpeg to do the actual work.

============ Change Log ============
2024-May-08 = Created. This is a combination of ConvertFolderToMP3 and ConvertFolderToMP4.

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
from abc import ABC
from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum, auto
from functools import partial
from pathlib import Path
import time

from wmul_file_manager.utilities import ffmpeg
from wmul_file_manager.utilities.FileNamePrinter import object_cleaner

import wmul_logger
logger = wmul_logger.get_logger()


class _CompressorFileInformationType(Enum):
    Unchecked_File = auto()
    Non_Media_file = auto()
    UnCompressed_Media_File = auto()
    Compressed_Media_File = auto()


class _CompressorFileInformation:

    def __init__(self, source_file_path: Path, source_root_path: Path, compressed_files_folder: Path):
        self.file_info_type = _CompressorFileInformationType.Unchecked_File
        self.original_file_name = source_file_path
        self.source_root_path = source_root_path
        self.compressed_files_folder = compressed_files_folder
        self.destination_path = ""

    def __str__(self):
        return f"_CompressorFileInformation:\t{str(self.file_info_type)}\t{str(self.original_file_name)}"

    def set_as_media_file(self, final_suffix: str):
        self.file_info_type = _CompressorFileInformationType.UnCompressed_Media_File
        self._compute_destination_path(final_suffix=final_suffix)

    def _compute_destination_path(self, final_suffix: str):
        relative_to_root = self.original_file_name.relative_to(self.source_root_path).parent
        final_filename = self.original_file_name.stem + final_suffix
        self.destination_path = self.compressed_files_folder / relative_to_root / final_filename

    def set_as_non_media_file(self):
        self.file_info_type = _CompressorFileInformationType.Non_Media_file

    def _create_all_needed_parents(self):
        logger.debug(f"Creating parents {self.destination_path}")
        file_parent = self.destination_path.parent
        file_parent.mkdir(parents=True, exist_ok=True)

    def compress(self, call_ffmpeg: callable) -> None:
        logger.info(f"Compressing {self.original_file_name}")
        if not self.file_info_type == _CompressorFileInformationType.UnCompressed_Media_File:
            raise RuntimeError(f"Attempting to compress a file that is not a UnCompressed_Media_File. {self.original_file_name}")
        self._create_all_needed_parents()
        return_code = call_ffmpeg(
            input_file_path=self.original_file_name,
            output_file_path=self.destination_path
        )

        if return_code == 0:
            logger.debug("Return code good.")
            self.file_info_type = _CompressorFileInformationType.Compressed_Media_File
            return True
        else:
            logger.debug("Return code bad.")
            return False
    
    def delete(self):
        if self.file_info_type == _CompressorFileInformationType.Compressed_Media_File:
            logger.debug(f"Deleting {object_cleaner(self)}")
            try:
                self.original_file_name.unlink()
            except PermissionError as pe:
                # Wait 5 seconds, retry once
                time.sleep(5)
                try:
                    self.original_file_name.unlink()
                except PermissionError as pe:
                    logger.error(f"Permission error on {self}")
        else:
            logger.warning(f"Attempted to delete a file that has not been compressed. {object_cleaner(self)}")
    
    def destination_exists(self):
        if not self.file_info_type == _CompressorFileInformationType.UnCompressed_Media_File:
            return False
        else:
            return self.destination_path.exists()

    @property
    def suffix(self):
        return self.original_file_name.suffix

    @classmethod
    def get_factory(cls, root_path, compressed_files_folder):
        def inner(source_file_path):
            return cls(source_file_path, root_path, compressed_files_folder)
        return inner


class MediaCompressor(ABC):
    call_ffmpeg: partial
    list_of_files_for_compression: list[_CompressorFileInformation]
    list_of_files_for_deletion: list[_CompressorFileInformation]
    source_suffixes: list[str]
    destination_suffix: str        

    def consider_file_for_compression(self, file_under_consideration: _CompressorFileInformation) -> bool:
        if file_under_consideration.suffix.casefold() in self.source_suffixes:
            file_under_consideration.set_as_media_file(final_suffix=self.destination_suffix)
            if file_under_consideration.destination_exists():
                logger.info(f"This file seems to have already been converted. Skipping. "
                            f"{file_under_consideration.original_file_name}")
                return True
            if self._other_factors_allow_compression(file_under_consideration):
                logger.debug("File is a desired type. Adding file to conversion queue.")
                self.list_of_files_for_compression.append(file_under_consideration)
                return True
            else:
                return True
        else:
            logger.debug(f"File is not a desired type. {file_under_consideration.suffix}\t{self.source_suffixes}")
            return False
        
    def compress_list_of_files(self):
        logger.debug(f"{self} compressing files.")
        for file_item in self.list_of_files_for_compression:
            logger.debug(f"Working on {file_item}")
            if file_item.compress(call_ffmpeg=self.call_ffmpeg):
                logger.debug("Compression successful.")
                self.list_of_files_for_deletion.append(file_item)

    def delete_list_of_files(self):
        for file_item in self.list_of_files_for_deletion:
            file_item.delete()

    def _other_factors_allow_compression(self, file_under_consideration):
        return True
    
    
class VideoCompressor(MediaCompressor):

    def __init__(self, suffixes: list[str], video_codec: str, video_bitrate: int, audio_codec: str, audio_bitrate: int,
                 destination_suffix: str, ffmpeg_threads: int, ffmpeg_executable: Path, ffprobe_executable: Path):
        self.list_of_files_for_compression = []
        self.list_of_files_for_deletion = []
        self.source_suffixes = [suffix.casefold() for suffix in suffixes]
        self.destination_suffix = destination_suffix
        self.call_ffmpeg = partial(
            ffmpeg.convert_video,
            video_codec=video_codec,
            video_bitrate=video_bitrate,
            audio_codec=audio_codec, 
            audio_bitrate=audio_bitrate,
            threads=ffmpeg_threads,
            executable_path=ffmpeg_executable
        )
        self.ffprobe_executable = ffprobe_executable
        self.set_bitrate_floor(video_bitrate)
    
    def __str__(self) -> str:
        return f"VideoCompressor: {self.source_suffixes=}"

    def set_bitrate_floor(self, video_bitrate: str):
        """This sets the video bitrate floor, below which a video file will not be re-encoded. 
        The floor is 120% of video_bitrate. 

        E.G. If this function is called with '10' (10_000_000), the floor will be set at 12_000_000. 
        Any files that are already 12_000_000 or lower will not be re-encoded.

        Args:
            video_bitrate (str): The video bitrate, below which a file will not be re-encoded.
        """
        video_bitrate = int(video_bitrate) * 1_000_000
        self.bitrate_floor = int(video_bitrate * 1.2)

    def _other_factors_allow_compression(self, file_under_consideration):
        vbr = ffmpeg.determine_video_bitrate(file_under_consideration.original_file_name, self.ffprobe_executable)
        logger.debug(f"Video Bitrate: {vbr}")
        higher_bitrate = vbr > self.bitrate_floor
        if higher_bitrate:
            logger.debug("Video bitrate is above the floor, compression allowed.")
            return True
        else:
            logger.debug("Video bitrate is below the floor, skipping.")
            return False


class AudioCompressor(MediaCompressor):

    def __init__(self, suffixes: list[str], audio_codec: str, audio_bitrate: int, destination_suffix: str, 
                 ffmpeg_threads: int, ffmpeg_executable: Path):
        self.list_of_files_for_compression = []
        self.list_of_files_for_deletion = []
        self.source_suffixes = [suffix.casefold() for suffix in suffixes]
        self.destination_suffix = destination_suffix
        self.call_ffmpeg = partial(
            ffmpeg.convert_audio,
            codec=audio_codec, 
            bitrate=audio_bitrate,
            threads=ffmpeg_threads,
            executable_path=ffmpeg_executable
        )

    def __str__(self) -> str:
        return f"AudioCompressor: {self.source_suffixes=}"


class NullCompressor(MediaCompressor):

    def consider_file_for_compression(self, file_under_consideration: _CompressorFileInformation) -> bool:
        return False

    def compress_list_of_files(self):
        return
    
    def delete_list_of_files(self):
        return

@dataclass
class CompressMediaInFolder:
    source_paths: list[Path]
    audio_compressor: AudioCompressor
    video_compressor: VideoCompressor
    separate_folder_flag: bool = False
    delete_files_flag: bool = False

    def archive_yesterdays_folders(self) -> None:
        logger.debug(f"With {locals()}")
        yesterday = date.today() - timedelta(days=1)
        yesterday_folder_name = "{yr:04d}-{mo:02d}-{da:02d}".format(yr=yesterday.year, mo=yesterday.month,
                                                                    da=yesterday.day)
        for source_path in self.source_paths:
            yesterday_raw_files_folder = source_path / yesterday_folder_name
            self._check_and_archive_folder(yesterday_raw_files_folder)

    def archive_list_of_folders(self) -> None:
        logger.debug(f"With {locals()}")
        for source_path in self.source_paths:
            self._check_and_archive_folder(source_path)

    def  _check_and_archive_folder(self, source_path: Path) -> None:
        logger.info(f"Working on: {object_cleaner(source_path)}")
        if source_path.exists():
            if self.separate_folder_flag:
                compressed_files_folder = source_path.parent / (source_path.name + "_cmp")
            else:
                compressed_files_folder = source_path
            self._archive_folder(source_path, compressed_files_folder)
        else:
            logger.warning(f"Folder does not exist. {object_cleaner(source_path)}")

    def _archive_folder(self, source_path: Path, compressed_files_folder: Path) -> None:
        logger.debug(f"With {source_path=}, {compressed_files_folder=}")
        file_info_factory = _CompressorFileInformation.get_factory(
            source_path,
            compressed_files_folder
        )

        self._populate_list_of_files_for_compression(source_path, file_info_factory)
        self._compress_list_of_files()

        if self.delete_files_flag:
            logger.info("Delete files true.")
            self._delete_files()

    def _populate_list_of_files_for_compression(self, source_path: Path, file_info_factory: callable) -> list[_CompressorFileInformation]:
        logger.debug(f"With {locals()}")
        for file_item in source_path.iterdir():
            logger.debug(f"Working on {object_cleaner(file_item)}")
            if file_item.is_file():
                logger.debug("Is File.")
                file_information = file_info_factory(file_item)
                self._consider_this_file(file_information=file_information)
            else:
                logger.debug("Is dir.")
                self._populate_list_of_files_for_compression(
                    source_path=file_item,
                    file_info_factory=file_info_factory,
                )

    def _consider_this_file(self, file_information: _CompressorFileInformation):
        logger.debug("Considering file.")
        if not self.audio_compressor.consider_file_for_compression(file_under_consideration=file_information):
            if not self.video_compressor.consider_file_for_compression(file_under_consideration=file_information):
                file_information.set_as_non_media_file()

    def _compress_list_of_files(self):
        logger.debug("Compressing files.")
        self.audio_compressor.compress_list_of_files()
        self.video_compressor.compress_list_of_files()

    def _delete_files(self) -> None:
        self.audio_compressor.delete_list_of_files()
        self.video_compressor.delete_list_of_files()
            