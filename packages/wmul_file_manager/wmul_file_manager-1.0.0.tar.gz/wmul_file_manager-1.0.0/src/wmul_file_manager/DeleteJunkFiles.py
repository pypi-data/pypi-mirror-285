"""
@Author = 'Mike Stanley'

Iterates the contents of the given folder and deletes all of the junk files in the directory.

Junk files are the ones with one of the provided extensions. Defaults are .pk files created by Adobe Audition,
.sfk, .tmp, and .sfap0 files created by Sony Sound Forge.

Outputs, either to a file or to standard out, the deleted files' names and the total size of the deleted files.

Mainly designed to be run from command-line, but can also be called from other scripts.

============ Change Log ============
2019-Jun-10 = Add ability to consider a file to be junk based on its full name, not just its suffix.

2018-May-09 = Remove old command-line interface that was housed in this file and based on argparse.

2018-May-08 = Import from Titanium_Monticello to this package.

2017-Aug-24 = Added --verbose option.

2017-Aug-18 = Move the logger from Utilities to Logger.

2017-Aug-17 = Replace text_cleaner(str()) calls with object_cleaner()

2017-Aug-10 = Fix bug when encountering sub-folders.

2017-Aug-09 = Refactor calls to argparse.

              Re-write logging to use daiquiri.

              Eliminate the class.

              Modify to use Utilities.write_to_file_or_std_out.

              Move management of the logging into Utilities.py.

              Add command-line argument for logging level.

2017-Jul-26 = Rename ScriptArguments to DeleteJunkFilesArguments.

              Rename --folder argument to --sources

              Fix the way printing is handled so that both standard out and file output work when multiple source paths
                are provided.

2017-Jul-25 = Create a named tuple to encapsulate the arguments to run_scrupt. Modify _run_from_command_line to use
                the new named tuple.

              Modify to take multiple root folders.

              Reformat the calls to add_argument to be uniform.

2017-Jul-21 = Create a method to act as an external entry point for this script.

2017-Jul-20 = Rewrite to use the logging module instead of printing to stdout, add command-line params for log file
                and for normal results printing.

              Separate the deleting and printing actions into different methods.

2017-Jul-17 = Add .pkf as one of the default junk extensions. This seems to be used by newer versions of
              Adobe Audition.

              Fix a bug related to the calculation of the junk file sizes.

2017-Jun-23 = Make the list of junk files extensions a command-line option. Make whole thing a class.

2015-Jun-27 = Added MIT License.

2015-Jun-25 = Extracted the filename printing to a separate code file.

2015-Jun-24 = Created.

============ License ============
The MIT License (MIT)

Copyright (c) 2015-2019, 2024 Michael Stanley

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
from collections import namedtuple
import wmul_logger

from wmul_file_manager.utilities import FileNamePrinter
from wmul_file_manager.utilities import writer

_logger = wmul_logger.get_logger()


def _delete_junk_files(root_folder, junk_extensions=None, junk_names=None):
    _logger.info("Running _delete_junk_files")

    if not junk_extensions:
        junk_extensions = ['.pk', '.pkf', '.sfk', '.tmp', '.sfap0']
    if not junk_names:
        junk_names = ["Thumbs.db", ".DS_Store"]

    junk_files = []

    junk_size = _search_directory(root_folder, junk_extensions, junk_names, junk_files)

    return junk_files, junk_size


def _write_results(result_writer, results):
    _logger.info("Running _write_results")
    result_writer("===========================================================================================")
    result_writer("                             ********Delete Junk Files********                             ")
    for junk_files, junk_size in results:
        for item in junk_files:
            result_writer(f"{FileNamePrinter.object_cleaner(item)}")
        result_writer(f"Total Size of Deleted Junk Files: {junk_size}")
        result_writer("##########################################")


def _search_directory(path, junk_extensions, junk_names, junk_files_list):
    _logger.debug(f"Running _search_directory with {path}")
    junk_size = 0
    try:
        for item in path.iterdir():
            _logger.debug(f"Inspecting {item}")
            if item.is_file():
                _logger.debug(f"{item} is file")
                if _file_is_junk(item, junk_extensions, junk_names):
                    junk_files_list.append(item)
                    junk_size += _delete_this_junk_file(item)
            else:
                junk_size += _search_directory(item, junk_extensions, junk_names, junk_files_list)
    except WindowsError as we:
        _logger.error(f"Windows Error on: {path}")
        _logger.error(str(we))
    return junk_size


def _delete_this_junk_file(this_junk_file):
    _logger.info(f"{this_junk_file} is junk.")
    try:
        file_size = this_junk_file.stat().st_size
        this_junk_file.unlink()
        return file_size
    except BaseException as be:
        _logger.error(f"BaseException: {be}")
        return 0


def _file_is_junk(path, junk_extensions, junk_names):
    _logger.debug(f"Checking for junk-status of {path}. {junk_extensions}")
    extension_is_junk = path.suffix.casefold() in junk_extensions
    name_is_junk = path.name.casefold() in junk_names
    return extension_is_junk or name_is_junk


DeleteJunkFilesArguments = namedtuple(
    "DeleteJunkFilesArguments",
    [
        "source_paths",
        "junk_suffixes",
        "junk_names",
        "output_path"
    ]
)


def run_script(arguments):
    _logger.debug(f"Starting run_script with {arguments}")

    results = []

    for source_path in arguments.source_paths:
        _logger.debug(f"In run_script, working on {source_path}")
        junk_files, junk_size = _delete_junk_files(source_path, arguments.junk_suffixes, arguments.junk_names)
        results.append((junk_files, junk_size))

    with writer.get_writer(arguments.output_path) as result_writer:
        _write_results(result_writer, results)
