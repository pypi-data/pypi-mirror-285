"""
@Author = 'Mike Stanley'

Interface to call ffmpeg from within Python. Note that the executable called need not actually be ffmpeg, it just
needs to obey the same command-line options.

============ Change Log ============
2024-May-08 = Added .convert_video method for compressing video files.
              Change .call to .convert_audio .
              Add threads option to .convert_audio .

2018-May-01 = Imported from Titanium_Monticello to this project.

              Change bitrate comparisons from equality to greater-than / less-than.

              E.G.
              if bitrate == 320:
                    bitrate = "320000"

              became

              if bitrate > 192:
                    bitrate = "320000"

2017-Aug-11 = Modify to use python 3.5's .run method and to capture stderr and stdout instead of dumping to
                    console.

2015-Feb-25 = Created.

============ License ============
The MIT License (MIT)

Copyright (c) 2015, 2017-2018, 2024 Michael Stanley

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
import subprocess
import wmul_logger

logger = wmul_logger.get_logger()

def convert_audio(input_file_path, output_file_path, codec, bitrate, threads, executable_path):
    bitrate = int(bitrate)

    if codec == "mp3":
        codec = "libmp3lame"

    if bitrate > 192:
        bitrate_as_string = "320000"
    elif bitrate > 160:
        bitrate_as_string = "192000"
    elif bitrate > 96:
        bitrate_as_string = "160000"
    elif bitrate <= 96:
        bitrate_as_string = "96000"

    subprocess_args = [
        str(executable_path), 
        "-i", str(input_file_path), 
        "-codec:a", codec,  
        "-b:a", bitrate_as_string, 
        "-threads", str(threads), 
        str(output_file_path)
    ]

    logger.info(f"subprocess_args: {subprocess_args}")

    subprocess_result = subprocess.run(
        subprocess_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    if subprocess_result.returncode != 0:
        logger.debug(f"{subprocess_result}")

    return subprocess_result.returncode

def convert_video(input_file_path, output_file_path, video_codec, video_bitrate, audio_codec, audio_bitrate, threads, executable_path):
    audio_bitrate = int(audio_bitrate)
    video_bitrate = int(video_bitrate)

    if audio_codec == "mp3":
        audio_codec = "libmp3lame"

    if audio_bitrate > 192:
        audio_bitrate_as_string = "320k"
    elif audio_bitrate > 160:
        audio_bitrate_as_string = "192k"
    elif audio_bitrate > 96:
        audio_bitrate_as_string = "160k"
    elif audio_bitrate <= 96:
        audio_bitrate_as_string = "96k"

    if video_bitrate > 19:
        video_bitrate_as_string = "20000k"
    elif video_bitrate > 14: 
        video_bitrate_as_string = "15000k"
    elif video_bitrate > 9:
        video_bitrate_as_string = "10000k"
    elif video_bitrate > 4:
        video_bitrate_as_string = "5000k"
    else:
        video_bitrate_as_string = "1000k"

    subprocess_args = [
        str(executable_path), 
        "-i", str(input_file_path),
        "-c:a", audio_codec,  
        "-b:a", audio_bitrate_as_string, 
        "-c:v", video_codec, 
        "-b:v", video_bitrate_as_string, 
        "-threads", str(threads), 
        str(output_file_path)
    ]

    logger.info(f"subprocess_args: {subprocess_args}")

    subprocess_result = subprocess.run(
        subprocess_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    return subprocess_result.returncode

def determine_video_bitrate(input_file_path, ffprope_executable_path):
    subprocess_args = [
        str(ffprope_executable_path),
        '-v', 'quiet',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=bit_rate',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        str(input_file_path)
    ]

    subprocess_result = subprocess.run(
        subprocess_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    stdout = subprocess_result.stdout

    try:
        bitrate = int(stdout)
    except ValueError:
        logger.info(f"ffprobe could not determine the bitrate, setting it to zero. {input_file_path}")
        bitrate = 0
    return bitrate
