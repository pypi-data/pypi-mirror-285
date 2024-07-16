"""
@Author = 'Mike Stanley'

For yearly archiving. Deletes the junk files, renames equivalent files, copies everything to a separate directory,
    converts the wav files to mp3s, and does a final comparison to check for missing files.

============ Change Log ============
2018-May-29 = BUGFIX: Fix AnnualArchiver's call to BulkCopier.

2018-May-24 = Rename logger to _logger.

              Rename numerous method-local variables.

2018-May-14 = Remove old command-line interface that was housed in this file and based on argparse.

2018-May-11 = Imported from Titanium_Monticello into this package.

2017-Aug-24 = Added --verbose option.

2017-Aug-18 = Move the logger from Utilities to Logger.

2017-Aug-17 = Refactor pathlib import

2017-Aug-11 = Remove FolderContentQuantityComparer as its function has been overtaken by improvements to
                FolderComparer.

2017-Aug-09 = Add logging with daiquiri.

              Move management of the logging into Utilities.py.

              Add command-line argument for logging level.

2017-Aug-01 = Refactor to use the new named tuples and methods for external access in FolderComparer and
                FolderContentQuantityComparer.

              Refactor to remove some redundant arguments from run_script.

              Refactor to clean up the extraction of the command-line arguments.

              Add command-line argument for output file of FolderContentQuantityComparer.

2017-Jul-28 = Modify to make use of the new named tuples in BulkCopier and ConvertFolderToMP3 and to use each script's
                new method for external access.

2017-Jul-26 = Modify to make use of the new named tuples in DeleteJunkFiles and EquivalentFileFinder.


2017-Jul-25 = Modify the call to EquivalentFileFinder to use that script's new method for external access.

              Add command-line argument for equiv_output file and pass that argument to the
              EquivalentFileFinder script.

2017-Jul-21 = Create a method to act as an external entry point for this script.

              Modify the call to DeleteJunkFiles to use that script's new method for external access.

              Add command-line arguments for the junk_suffixes and junk_output file and pass those arguments to the
              DeleteJunkFiles script.

              Fix typo in EquivalentFileFinder.generate_equivalancy_graph name (should be equivalency with an e).

              Refactor names in EquivalentFileFinder.

2017-Jul-20 = Re-Write the names of the command-line options to be clearer as to which sub-script each option
                corresponds.

2017-Jul-19 = Add a command-line arg for the output file for when it calls FolderComparer.

2017-Jul-17 = Change the way this script calls BulkCopier to reflect changes in the API of that script.

2017-Jul-03 = Fixed a typo in one of the calls to FolderComparer.

2017-Jun-23 = Modified the way DeleteJunkFiles is called to reflect changes in that file.
              Added documentation to the top.

2014-Nov-11 = Created.

============ License ============
The MIT License (MIT)

Copyright (c) 2014-2018, 2024 Michael Stanley

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
import wmul_logger

from wmul_file_manager import BulkCopier, DeleteJunkFiles, EquivalentFileFinder, FolderComparer

_logger = wmul_logger.get_logger()


def compare_start_and_end_folders_by_names(source_directories, destination_directory, equivalent_suffixes_list,
                                           name_comparer_output_file_name):
    _logger.debug(f"Starting compare_start_and_end_folders_by_names with {locals()}")
    for this_source_dir in source_directories:
        this_dest_dir = destination_directory / this_source_dir.name
        folder_comparer_arguments = FolderComparer.FolderComparerArguments(
            first_path=this_source_dir,
            second_path=this_dest_dir,
            ignore_paths=[],
            equivalent_suffixes=equivalent_suffixes_list,
            output_path=name_comparer_output_file_name,
            name_only=False,
            name_size_only=False
        )
        _logger.debug(f"Comparing by name, {this_source_dir}")
        FolderComparer.run_script(folder_comparer_arguments)


def run_script(delete_junk_files_arguments, equivalent_file_finder_arguments, bulk_copier_arguments,
               compress_media_in_folder, name_comparer_output_file_name):
    _logger.debug(f"Starting run_script with {locals()}")
    DeleteJunkFiles.run_script(delete_junk_files_arguments)
    EquivalentFileFinder.run_script(equivalent_file_finder_arguments)
    BulkCopier.run_script(bulk_copier_arguments)
    compress_media_in_folder.archive_list_of_folders()
    compare_start_and_end_folders_by_names(
        bulk_copier_arguments.source_directories,
        bulk_copier_arguments.destination_directory,
        equivalent_file_finder_arguments.equivalent_suffixes_list,
        name_comparer_output_file_name
    )

