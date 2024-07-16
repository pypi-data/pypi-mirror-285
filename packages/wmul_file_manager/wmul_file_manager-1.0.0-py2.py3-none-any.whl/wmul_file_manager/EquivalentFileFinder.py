"""
@Author = 'Mike Stanley'

Iterates through a folder and its subfolders finding files in the same folder that differ only by their suffix.
This is to find cases where someone has created both a .wav and .mp3 version of the same file.
E.G. foo.wav and foo.mp3.

Optionally, the files can be renamed where the original suffix is added to the name.
E.G. blah.wav, blah.mp3 become blah_wav.wav and blah_mp3.mp3

This prepares folders for bulk mp3ing by ConvertFolderToMP3.py

============ Change Log ============
2018-May-10 = Remove old command-line interface that was housed in this file and based on argparse.

2018-May-09 = Import from Titanium_Monticello

2017-Aug-24 = Added --verbose option.

2017-Aug-18 = Move the logger from Utilities to Logger.

2017-Aug-10 = Modify logging to use the logger provided in Utilities.

              Add additional logging.

              Modify to use Utilities.write_to_file_or_std_out.

              Modify to use object_cleaner instead of text_cleaner.

              Modify to use f-strings.

2017-Aug-09 = Refactor calls to argparse.

2017-Jul-31 = Move _generate_equivalency_graph to Utilities.

2017-Jul-26 = Create a named tuple to encapsulate the arguments to run_script. Modify _run_from_command_line to
                use the new named tuple.

              Modify to take multiple root folders.

2017-Jul-25 = Add a command-line option to output the text to a file.

2017-Jul-21 = Fix typo in generate_equivalancy_graph name (should be equivalency with an e).

              Update the documentation.

              Normalize the formatting of the calls to set the command-line arguments.

              Refactor some of the names.

              Extract the printing process into its own method.

2017-Jul-20 = Correct how this script calls clean_print.

2017-Jul-18 = The renamed files now retain their original casing.
              Re-Write to make it work under linux. Casefolding made it not work.
              Added logging and command-line path for log file.

2015-Jul-22 = Compare files casefolded.

2015-Jul-19 = Rename main method.

2015-Jul-15 = Created.

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
from collections import defaultdict, namedtuple
from pathlib import Path
import networkx as nx

import wmul_logger
from wmul_file_manager.utilities.FileNamePrinter import object_cleaner
from wmul_file_manager.utilities.writer import get_writer
from wmul_file_manager.utilities.graph import generate_equivalency_graph

_logger = wmul_logger.get_logger()


class _FileInformationWithSuffixEquivalence:

    def __init__(self, full_path, equivalences):
        self.FullPath = full_path
        casefold_path = Path(str(full_path).casefold())
        suffix = casefold_path.suffix
        if suffix in equivalences.nodes():
            equivalent_exts = nx.node_connected_component(equivalences, suffix)
            self.EquivalentPaths = {casefold_path.with_suffix(su) for su in equivalent_exts}
        else:
            self.EquivalentPaths = {casefold_path}

    def __eq__(self, other):
        return self.EquivalentPaths == other.EquivalentPaths

    def __hash__(self):
        return hash("".join([str(eqp) for eqp in sorted(self.EquivalentPaths)]))

    def __str__(self):
        return "\t\t".join([str(eqp) for eqp in sorted(self.EquivalentPaths)])

    @classmethod
    def get_factory(cls, equivalences):
        _logger.debug(f"In get_factory.")

        def inner(full_path):
            return cls(full_path, equivalences)
        return inner


def _find_equivalent_files(folder_path, file_info_factory, rename):
    _logger.info(f"In _find_equivalent_files with Path: {folder_path}, Rename: {rename}")
    equivalent_files = []
    _walk_dir(folder_path, equivalent_files, file_info_factory)
    equivalent_files.sort()
    if rename:
        _logger.debug("Rename is true.")
        _rename_equivalent_files(equivalent_files)
    return equivalent_files


def _walk_dir(this_path, equivalent_files, file_info_factory):
    files_in_dir = defaultdict(list)
    sub_dirs = []
    for item in this_path.iterdir():
        _logger.debug(f"Investigating {item}")
        if item.is_file():
            _logger.debug(f"{item} is a file.")
            this_file = file_info_factory(item)
            files_in_dir[this_file].append(this_file)
        elif item.is_dir():
            sub_dirs.append(item)

    for key, value in files_in_dir.items():
        if len(value) > 1:
            for file_item in value:
                equivalent_files.append(file_item.FullPath)

    for item in sub_dirs:
        _walk_dir(item, equivalent_files, file_info_factory)


def _rename_equivalent_files(equivalent_files):
    _logger.info("In _rename_equivalent_files")
    for equiv in equivalent_files:
        if equiv.exists():
            _logger.debug(f"Exists: Equivalent file {object_cleaner(equiv)}")
            _rename_this_file(equiv)
        else:
            _logger.debug(f"Equiv does not exist. {object_cleaner(equiv)}")


def _rename_this_file(full_path):
    suffix_without_dot = full_path.suffix[1:]
    revised_name = full_path.stem + "_" + suffix_without_dot + full_path.suffix
    revised_path = full_path.with_name(revised_name)
    _logger.debug(f"Renaming: {object_cleaner(full_path)}\t\tTo: {object_cleaner(revised_path)}")
    full_path.rename(revised_path)


def _print_equivalent_files(result_writer, results):
    result_writer("===========================================================================================")
    result_writer("                           ********Equivalent File Finder********                          ")
    for result in results:
        for item in result:
            result_writer(f"{object_cleaner(item)}")
        result_writer("##########################################")


EquivalentFileFinderArguments = namedtuple(
    "EquivalentFileFinderArguments",
    [
        "source_paths",
        "equivalent_suffixes_list",
        "rename_flag",
        "output_path"
    ]
)


def run_script(arguments):
    _logger.debug(f"Starting run_script with {arguments}")
    equivalent_exts = generate_equivalency_graph(arguments.equivalent_suffixes_list)
    file_info_factory = _FileInformationWithSuffixEquivalence.get_factory(equivalent_exts)

    results = []

    for source_path in arguments.source_paths:
        _logger.debug(f"In run_script, working on {source_path}")
        equivalent_files = _find_equivalent_files(source_path, file_info_factory, arguments.rename_flag)
        results.append(equivalent_files)

    with get_writer(file_name=arguments.output_path) as writer:
        _print_equivalent_files(writer, results)
