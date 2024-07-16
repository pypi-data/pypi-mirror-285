"""
@Author = 'Mike Stanley'

This script compares the contents of two folders. E.G. A Folder and its backup folder.

It does this in one of two ways.

1) By same relative path, then by modification time (mtime), then by size.

2) By same relative path, including equivalent suffixes.

Relative path example:

original/foo/bar.txt
backup/foo/bar.txt

Equivalent suffix example:

original/foo/bar.wav
backup/foo/bar.mp3

If prints four lists of files:
1) Any files or directories for which the system lacks read permission.
2) Any files in the first directory which would be duplicates with equivalent suffixes.
E.G. original/foo/bar.wav, original/foo/bar.mp3
3) Any files that are in the first directory but not the second.
4) Any files that are in the second directory but not the first.

When method 1 is used for comparison, then lists 3 and 4 would include files that are in both folders, but with
different mtimes and/or sizes.

============ Change Log ============
2019-Jun-17 =  Modify to use the str result for sorting.

2018-May-14 = Remove obsolete imports.

2018-May-11 = Remove old command-line interface that was housed in this file and based on argparse.

2018-May-10 = Imported from Titanium_Monticello.

2017-Aug-24 = Added --verbose option.

2017-Aug-18 = Move the logger from Utilities to Logger.

2017-Aug-11 = Add extensive logging.

              Change to use object_cleaner instead of text_cleaner.

2017-Aug-01 = Extract the file output to its own method.

              Refactor _write_results to take a tuple of results. This is to support a global refactoring of the
                _write_results methods.

              Extract write_to_file_or_std_out, the next step in refactoring.

2017-Jul-31 = Refactor calls to argparse.

              Remove local version of generate_equivalency_graph and import the one from Utilities instead.

              Create a named tuple to encapsulate the arguments to run_script. Modify _run_from_command_line to use
                the new named tuple. Create a method to act as an external entry point for this script.

2017-Jul-20 = Correct how this script calls text_cleaner.

2017-Jul-18 = Fix the sorting of the list of filenames that is output.

              Make the output filename a command-line option.

              When using the equivalent file extensions feature, now identifies when there are equivalent files in the
                first folder. E.G. a foo.wav and a foo.mp3.

2017-Jul-03 = Change the script so that it outputs to a file instead of printing.

2016-Jun-08 = Refactor / bugfix to fix problems with equivalent file types.

2016-Apr-15 = Added logic to handle paths for which the user does not have permission. Skips over those paths without
                crashing and prints a list of those paths.

2015-Aug-30 = Use a single class of _FileInformationWithRelativePathCreationTimeSizeEquivalence and implement total_ordering.

              Sort the file lists before printing them.

2015-Jul-14 = Updated documentation to include command-line options. Corrected help on command-line options to
                clarify that pairs are transitive.

2015-Jul-13 = Added logic to allow for files to be considered equal if they have the same name, but different
                extensions. E.G.: source/dir/subdir/blah.wav and dest/dir/subdir/blah.mp3 .

              Fixed case-folding comparisons.

2015-Jul-02 = Added MIT License and initial documentation.

2015-Jun-27 = Modify to use FileNamePrinter

2015-Jun-17 = Add exception handling for cases where the file's metadata is unavailable.

              Added ability to ignore sub-folders off the first folder.

2015-Mar-16 = Created.

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
from collections import Counter, namedtuple
from functools import total_ordering
from pathlib import Path
import networkx as nx
import wmul_logger

from wmul_file_manager.utilities.FileNamePrinter import object_cleaner
from wmul_file_manager.utilities.graph import generate_equivalency_graph
from wmul_file_manager.utilities.writer import get_writer

logger = wmul_logger.get_logger()


class _FileInformationComparer_NameOnly:

    @staticmethod
    def equals(first, second):
        return first.RelativePath == second.RelativePath

    @staticmethod
    def less_than(first, second):
        return first.RelativePath < second.RelativePath

    @staticmethod
    def hash(first):
        return hash(_FileInformationComparer_NameOnly.string(first))

    @staticmethod
    def string(first):
        return f"{str(first.RelativePath)}"


class _FileInformationComparer_NameSizeOnly:

    @staticmethod
    def equals(first, second):
        return (first.RelativePath == second.RelativePath
                and first.size == second.size)

    @staticmethod
    def less_than(first, second):
        if first.RelativePath == second.RelativePath:
            return first.size < second.size
        else:
            return first.RelativePath < second.RelativePath

    @staticmethod
    def hash(first):
        return hash(_FileInformationComparer_NameSizeOnly.string(first))

    @staticmethod
    def string(first):
        return f"{str(first.RelativePath)}\t\t{str(first.size)}"


class _FileInformationComparer_Name_mtime_size:

    @staticmethod
    def equals(first, second):
        return (first.RelativePath == second.RelativePath
                and first.mtime == second.mtime
                and first.size == second.size)

    @staticmethod
    def less_than(first, second):
        if first.RelativePath == second.RelativePath:
            if first.mtime == second.mtime:
                return first.size < second.size
            else:
                return first.mtime < second.mtime
        else:
            return first.RelativePath < second.RelativePath

    @staticmethod
    def hash(first):
        return hash(_FileInformationComparer_Name_mtime_size.string(first))

    @staticmethod
    def string(first):
        return f"{str(first.RelativePath)}\t\t{str(first.mtime)}\t{str(first.size)}"


class _FileInformationComparer_EquivalentPaths:

    @staticmethod
    def equals(first, second):
        return first.EquivalentPaths == second.EquivalentPaths

    @staticmethod
    def less_than(first, second):
        return first.EquivalentPaths < second.EquivalentPaths

    @staticmethod
    def hash(first):
        return hash(_FileInformationComparer_EquivalentPaths.string(first))

    @staticmethod
    def string(first):
        return "\t\t".join([str(eqp) for eqp in sorted(first.EquivalentPaths)])


@total_ordering
class _FileInformation:

    def __init__(self, full_path, root_path, mtime, size, equivalences, comparer):
        self.FullPath = full_path
        self.RelativePath = full_path.relative_to(root_path)
        self.mtime = mtime
        self.size = size
        self.comparer = comparer
        if equivalences:
            suffix = full_path.suffix
            if suffix in equivalences.nodes():
                equivalent_exts = nx.node_connected_component(equivalences, suffix)
                self.EquivalentPaths = {self.RelativePath.with_suffix(su) for su in equivalent_exts}
            else:
                self.EquivalentPaths = {self.RelativePath}

    def __eq__(self, other):
        return self.comparer.equals(self, other)

    def __lt__(self, other):
        return self.comparer.less_than(self, other)

    def __hash__(self):
        return self.comparer.hash(self)

    def __str__(self):
        return self.comparer.string(self)

    @classmethod
    def get_factory(cls, equivalent_exts, comparer):
        def inner(full_path, root_path, mtime, size):
            return cls(full_path, root_path, mtime, size, equivalent_exts, comparer)
        return inner


def _compare_paths(arguments, file_info_factory):
    logger.info(f"In _compare_paths with {arguments}")
    first_path_contents, second_path_contents, ignore_contents, no_permissions_list = \
        _collect_path_contents(arguments, file_info_factory)

    first_dupes = _find_duplicates(first_path_contents)

    first_minus_second, second_minus_first = _find_differences_between_paths(
        first_path_contents,
        second_path_contents,
        ignore_contents
    )

    return no_permissions_list, first_dupes, first_minus_second, second_minus_first


def _find_differences_between_paths(first_path_contents, second_path_contents, ignore_contents):
    first_path_contents = set(first_path_contents)
    second_path_contents = set(second_path_contents)
    ignore_contents = set(ignore_contents)

    first_path_contents -= ignore_contents

    first_minus_second = first_path_contents - second_path_contents
    second_minus_first = second_path_contents - first_path_contents

    return first_minus_second, second_minus_first


def _find_duplicates(path_contents):
    path_count = Counter(path_contents)
    return [item for item, count in path_count.items() if count > 1]


def _collect_path_contents(arguments, file_info_factory):
    first_path_contents = []
    second_path_contents = []
    no_permissions_list = []
    ignore_contents = []

    _walk_directory(arguments.first_path, arguments.first_path, first_path_contents, file_info_factory, no_permissions_list)
    _walk_directory(arguments.second_path, arguments.second_path, second_path_contents, file_info_factory, no_permissions_list)
    for item in arguments.ignore_paths:
        _walk_directory(item, arguments.first_path, ignore_contents, file_info_factory, no_permissions_list)

    return first_path_contents, second_path_contents, ignore_contents, no_permissions_list


def _write_results(result_writer, results):
    logger.info("Writing results.")
    no_permissions_list, first_dupes, first_minus_second, second_minus_first = results
    result_writer("Folders without permission")
    logger.debug("In _write_results, working no permission paths.")
    for file_item in sorted(no_permissions_list, key=lambda file_path: str(file_path)):
        result_writer(object_cleaner(file_item))
    result_writer("#####################################################################################")
    result_writer("#####################################################################################")
    result_writer("#####################################################################################\n\n")
    result_writer("Duplicates in First")
    logger.debug("In _write_results, working duplicates in first path.")
    for file_item in sorted(first_dupes, key=lambda file_path: str(file_path)):
        result_writer(object_cleaner(file_item))
    result_writer("#####################################################################################")
    result_writer("#####################################################################################")
    result_writer("#####################################################################################\n\n")
    result_writer("First Minus Second")
    logger.debug("In _write_results, working first minus second.")
    for file_item in sorted(first_minus_second, key=lambda file_path: str(file_path)):
        result_writer(object_cleaner(file_item))
    result_writer("#####################################################################################")
    result_writer("#####################################################################################")
    result_writer("#####################################################################################\n\n")
    result_writer("Second Minus First")
    logger.debug("In _write_results, working second minus first.")
    for file_item in sorted(second_minus_first, key=lambda file_path: str(file_path)):
        result_writer(object_cleaner(file_item))


def _walk_directory(this_path, root_path, path_contents, file_info_factory, no_permissions_list):
    logger.info(f"In _walk_directory with {object_cleaner(this_path)}")
    try:
        for item in this_path.iterdir():
            logger.debug(f"Investigating: {object_cleaner(item)}")
            try:
                if item.is_dir():
                    logger.debug("Is Dir")
                    _walk_directory(item, root_path, path_contents, file_info_factory, no_permissions_list)
                else:
                    logger.debug("Is file")
                    file_data = _get_file_data(item, root_path, file_info_factory)
                    path_contents.append(file_data)
            except PermissionError as pe:
                logger.debug("No permissions on file.")
                no_permissions_list.append(item)
                # We do not have permission for this file. Keep moving.
                continue
    except PermissionError as pe:
        logger.debug("No permission on directory.")
        no_permissions_list.append(this_path)


def _get_file_data(file_item, root_path, file_info_factory):
    logger.debug(f"In _get_file_data with {file_item} and {root_path}")
    try:
        file_stats = file_item.stat()
        mtime = file_stats.st_mtime
        size = file_stats.st_size
    except FileNotFoundError:
        mtime = 0
        size = 0

    return file_info_factory(
        full_path=Path(str(file_item).casefold()),
        root_path=Path(str(root_path).casefold()),
        mtime=mtime,
        size=size
    )


FolderComparerArguments = namedtuple(
    "FolderComparerArguments",
    [
        "first_path",
        "second_path",
        "ignore_paths",
        "equivalent_suffixes",
        "name_only",
        "name_size_only",
        "output_path"
    ]
)


def run_script(arguments):
    logger.debug(f"In run_script with {arguments}")
    if arguments.name_only:
        equivalent_exts = None
        comparer = _FileInformationComparer_NameOnly
    elif arguments.name_size_only:
        equivalent_exts = None
        comparer = _FileInformationComparer_NameSizeOnly
    elif arguments.equivalent_suffixes:
        equivalent_exts = generate_equivalency_graph(arguments.equivalent_suffixes)
        comparer = _FileInformationComparer_EquivalentPaths
    else:
        equivalent_exts = None
        comparer = _FileInformationComparer_Name_mtime_size
    file_info_factory = _FileInformation.get_factory(equivalent_exts=equivalent_exts, comparer=comparer)
    results = _compare_paths(arguments=arguments, file_info_factory=file_info_factory)

    with get_writer(file_name=arguments.output_path) as result_writer:
        _write_results(result_writer, results)
