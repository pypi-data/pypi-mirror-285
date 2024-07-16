"""
@Author = 'Mike Stanley'

============ Change Log ============
2024-May-03 = Made Delete Old Files timezone aware. Began improving use of wmul_test_utils.

2018-Apr-30 = Created.

============ License ============
The MIT License (MIT)

Copyright (c) 2018, 2024 Michael Stanley

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
from collections import namedtuple
from wmul_file_manager import cli
from wmul_file_manager.BulkCopier import BulkCopierArguments
from wmul_file_manager.DeleteJunkFiles import DeleteJunkFilesArguments
from wmul_file_manager.EquivalentFileFinder import EquivalentFileFinderArguments
from wmul_file_manager.FolderComparer import FolderComparerArguments
from wmul_file_manager.FindOldDirectories import FindOldDirectoriesArguments
from wmul_file_manager.DeleteOldFiles import DeleteOldFilesArguments
from wmul_file_manager.DidTheSkimmerCopyTheFiles import DidTheSkimmerCopyTheFiles
from wmul_file_manager import IsTheSkimmerWorking
from wmul_test_utils import generate_true_false_matrix_from_list_of_strings, make_namedtuple
import datetime
import pathlib
import pytest
import random


def generate_binary_matrix_from_named_tuple(input_tuple):
    number_of_args = len(input_tuple._fields)
    powers_of_two = {2**i: i for i in range(number_of_args)}
    these_args = []
    for i in range(0, number_of_args):
        these_args.append(False)

    collected_test_args = []

    for i in range(1, 2**number_of_args + 1):
        this_test_arg = input_tuple._make(these_args)
        collected_test_args.append(this_test_arg)

        for this_power_of_two, corresponding_index in powers_of_two.items():
            if i % this_power_of_two == 0:
                these_args[corresponding_index] = not these_args[corresponding_index]

    return collected_test_args


def random_bytes(count=100):
    return bytearray(random.randint(0, 255) for i in range(count))


@pytest.fixture(scope="function")
def setup_bulk_copy(mocker, tmpdir):
    mock_run_bulk_copier = mocker.patch("wmul_file_manager.cli.run_bulk_copier")

    src1 = tmpdir.join("src1")
    src2 = tmpdir.join("src2")
    dst = tmpdir.join("dst")

    runner = CliRunner()
    yield mock_run_bulk_copier, src1, src2, dst, runner


def test_bulk_copy_source_and_destination(setup_bulk_copy):
    mock_run_bulk_copier, src1, src2, dst, runner = setup_bulk_copy

    src1.ensure(dir=True)

    result = runner.invoke(cli.bulk_copy, [str(src1), str(dst)])

    assert result.exit_code == 0

    expected_arguments = BulkCopierArguments(
        source_directories=[src1],
        destination_directory=dst,
        exclude_suffixes_list=[],
        ignore_directories=[],
        force_copy_flag=False,
        delete_old_files_flag=False
    )

    mock_run_bulk_copier.assert_called_once_with(arguments=expected_arguments)


def test_bulk_copy_multiple_source_and_destination(setup_bulk_copy):
    mock_run_bulk_copier, src1, src2, dst, runner = setup_bulk_copy

    src1.ensure(dir=True)
    src2.ensure(dir=True)

    result = runner.invoke(cli.bulk_copy, [str(src1), str(src2), str(dst)])

    assert result.exit_code == 0

    expected_arguments = BulkCopierArguments(
        source_directories=[src1, src2],
        destination_directory=dst,
        exclude_suffixes_list=[],
        ignore_directories=[],
        force_copy_flag=False,
        delete_old_files_flag=False
    )

    mock_run_bulk_copier.assert_called_once_with(arguments=expected_arguments)


def test_bulk_copy_non_existant_source(setup_bulk_copy):
    mock_run_bulk_copier, src1, src2, dst, runner = setup_bulk_copy

    result = runner.invoke(cli.bulk_copy, [str(src1), str(dst)])

    assert result.exit_code != 0

    mock_run_bulk_copier.assert_not_called()


def test_bulk_copy_exclude_exts(setup_bulk_copy):
    mock_run_bulk_copier, src1, src2, dst, runner = setup_bulk_copy

    src1.ensure(dir=True)

    result = runner.invoke(cli.bulk_copy, [str(src1), str(dst), "--exclude_ext", ".wav",
                                                   "--exclude_ext", ".mP3"])

    assert result.exit_code == 0

    expected_arguments = BulkCopierArguments(
        source_directories=[src1],
        destination_directory=dst,
        exclude_suffixes_list=[".wav", ".mp3"],
        ignore_directories=[],
        force_copy_flag=False,
        delete_old_files_flag=False
    )

    mock_run_bulk_copier.assert_called_once_with(arguments=expected_arguments)


def test_bulk_copy_ignore_paths(setup_bulk_copy):
    mock_run_bulk_copier, src1, src2, dst, runner = setup_bulk_copy

    src1.ensure(dir=True)
    ignore1 = src1.join("ignore1")
    ignore1.ensure(dir=True)
    ignore2 = src1.join("ignore2")
    ignore2.ensure(dir=True)

    result = runner.invoke(cli.bulk_copy, [str(src1), str(dst), "--ignore_folder", str(ignore1),
                                                   "--ignore_folder", str(ignore2)])

    assert result.exit_code == 0

    expected_arguments = BulkCopierArguments(
        source_directories=[src1],
        destination_directory=dst,
        exclude_suffixes_list=[],
        ignore_directories=[ignore1, ignore2],
        force_copy_flag=False,
        delete_old_files_flag=False
    )

    mock_run_bulk_copier.assert_called_once_with(arguments=expected_arguments)


def test_bulk_copy_force_copy(setup_bulk_copy):
    mock_run_bulk_copier, src1, src2, dst, runner = setup_bulk_copy

    src1.ensure(dir=True)

    result = runner.invoke(cli.bulk_copy, [str(src1), str(dst), "--force_copy"])

    assert result.exit_code == 0

    expected_arguments = BulkCopierArguments(
        source_directories=[src1],
        destination_directory=dst,
        exclude_suffixes_list=[],
        ignore_directories=[],
        force_copy_flag=True,
        delete_old_files_flag=False
    )

    mock_run_bulk_copier.assert_called_once_with(arguments=expected_arguments)


def test_bulk_copy_delete_old(setup_bulk_copy):
    mock_run_bulk_copier, src1, src2, dst, runner = setup_bulk_copy

    src1.ensure(dir=True)

    result = runner.invoke(cli.bulk_copy, [str(src1), str(dst), "--delete_old"])

    assert result.exit_code == 0

    expected_arguments = BulkCopierArguments(
        source_directories=[src1],
        destination_directory=dst,
        exclude_suffixes_list=[],
        ignore_directories=[],
        force_copy_flag=False,
        delete_old_files_flag=True
    )

    mock_run_bulk_copier.assert_called_once_with(arguments=expected_arguments)


@pytest.fixture(scope="function")
def setup_delete_junk_files(mocker, tmpdir):
    mock_run_delete_junk_files = mocker.patch("wmul_file_manager.cli.run_delete_junk_files")

    src1 = tmpdir.join("src1")
    src1.ensure(dir=True)
    src2 = tmpdir.join("src2")
    src2.ensure(dir=True)
    output_path = tmpdir.join("foo.txt")

    expected_junk_exts = [".pk", ".pkf", ".sfk", ".sfap0", ".tmp"]
    expected_junk_names = ["thumbs.db", ".ds_store"]

    runner = CliRunner()

    return locals()


def test_delete_junk_files_default_junk(setup_delete_junk_files):
    runner = setup_delete_junk_files["runner"]
    src1 = setup_delete_junk_files["src1"]
    src2 = setup_delete_junk_files["src2"]
    expected_junk_suffixes = setup_delete_junk_files["expected_junk_exts"]
    expected_junk_names = setup_delete_junk_files["expected_junk_names"]
    mock_run_delete_junk_files = setup_delete_junk_files["mock_run_delete_junk_files"]

    result = runner.invoke(cli.delete_junk_files, [str(src1), str(src2)])
    expected_arguments = DeleteJunkFilesArguments(
        source_paths=[pathlib.Path(src1), pathlib.Path(src2)],
        junk_suffixes=expected_junk_suffixes,
        junk_names=expected_junk_names,
        output_path=None
    )

    assert result.exit_code == 0
    mock_run_delete_junk_files.assert_called_once_with(expected_arguments)


def test_delete_junk_files_optional_junk_suffixes(setup_delete_junk_files):
    runner = setup_delete_junk_files["runner"]
    src1 = setup_delete_junk_files["src1"]
    src2 = setup_delete_junk_files["src2"]
    expected_junk_names = setup_delete_junk_files["expected_junk_names"]
    mock_run_delete_junk_files = setup_delete_junk_files["mock_run_delete_junk_files"]

    test_junk_suffixes = ".sfk .sfap0"
    expected_test_junk_suffixes = [".sfk", ".sfap0"]

    result = runner.invoke(cli.delete_junk_files, [str(src1), str(src2), "--junk_ext", test_junk_suffixes])
    expected_arguments = DeleteJunkFilesArguments(
        source_paths=[pathlib.Path(src1), pathlib.Path(src2)],
        junk_suffixes=expected_test_junk_suffixes,
        junk_names=expected_junk_names,
        output_path=None
    )

    assert result.exit_code == 0
    mock_run_delete_junk_files.assert_called_once_with(expected_arguments)


def test_delete_junk_files_optional_junk_names(setup_delete_junk_files):
    runner = setup_delete_junk_files["runner"]
    src1 = setup_delete_junk_files["src1"]
    src2 = setup_delete_junk_files["src2"]
    expected_junk_suffixes = setup_delete_junk_files["expected_junk_exts"]
    mock_run_delete_junk_files = setup_delete_junk_files["mock_run_delete_junk_files"]

    test_junk = "Thumbs.db"
    expected_test_junk = ["thumbs.db"]

    result = runner.invoke(cli.delete_junk_files, [str(src1), str(src2), "--junk_name", test_junk])
    expected_arguments = DeleteJunkFilesArguments(
        source_paths=[pathlib.Path(src1), pathlib.Path(src2)],
        junk_suffixes=expected_junk_suffixes,
        junk_names=expected_test_junk,
        output_path=None
    )

    assert result.exit_code == 0
    mock_run_delete_junk_files.assert_called_once_with(expected_arguments)


def test_delete_junk_files_output(setup_delete_junk_files):
    runner = setup_delete_junk_files["runner"]
    src1 = setup_delete_junk_files["src1"]
    src2 = setup_delete_junk_files["src2"]
    expected_junk_suffixes = setup_delete_junk_files["expected_junk_exts"]
    expected_junk_names = setup_delete_junk_files["expected_junk_names"]
    output_path = setup_delete_junk_files["output_path"]
    mock_run_delete_junk_files = setup_delete_junk_files["mock_run_delete_junk_files"]

    result = runner.invoke(cli.delete_junk_files, [str(src1), str(src2), "--output", str(output_path)])
    expected_arguments = DeleteJunkFilesArguments(
        source_paths=[pathlib.Path(src1), pathlib.Path(src2)],
        junk_suffixes=expected_junk_suffixes,
        junk_names=expected_junk_names,
        output_path=str(output_path)
    )

    assert result.exit_code == 0
    mock_run_delete_junk_files.assert_called_once_with(expected_arguments)


@pytest.fixture(scope="function")
def setup_find_equivalent_files(mocker, tmpdir):
    mock_run_equivalent_file_finder = mocker.patch("wmul_file_manager.cli.run_equivalent_file_finder")

    src1 = tmpdir.join("src1")
    src1.ensure(dir=True)
    src2 = tmpdir.join("src2")
    src2.ensure(dir=True)
    output_path = tmpdir.join("foo.txt")

    equivs = ".wav .mp3 .wav .ogg"
    expected_equivs = [".wav", ".mp3", ".wav", ".ogg"]

    runner = CliRunner()

    yield mock_run_equivalent_file_finder, src1, src2, output_path, equivs, expected_equivs, runner


def test_find_equivalent_files_good_path(setup_find_equivalent_files):
    mock_run_equivalent_file_finder, src1, src2, output_path, equivs, expected_equivs, runner = setup_find_equivalent_files

    result = runner.invoke(cli.find_equivalent_files, [str(src1), str(src2), equivs])

    assert result.exit_code == 0

    expected_args = EquivalentFileFinderArguments(
        source_paths=[pathlib.Path(src1), pathlib.Path(src2)],
        equivalent_suffixes_list=expected_equivs,
        rename_flag=False,
        output_path=None
    )

    mock_run_equivalent_file_finder.assert_called_once_with(expected_args)


def test_find_equivalent_files_wrong_equivs(setup_find_equivalent_files):
    mock_run_equivalent_file_finder, src1, src2, output_path, equivs, expected_equivs, runner = setup_find_equivalent_files

    result = runner.invoke(cli.find_equivalent_files, [str(src1), str(src2), ".wav .mp3 .ogg"])

    assert result.exit_code != 0


def test_find_equivalent_files_rename_flag(setup_find_equivalent_files):
    mock_run_equivalent_file_finder, src1, src2, output_path, equivs, expected_equivs, runner = setup_find_equivalent_files

    result = runner.invoke(cli.find_equivalent_files, [str(src1), str(src2), equivs, "--rename"])

    assert result.exit_code == 0

    expected_args = EquivalentFileFinderArguments(
        source_paths=[pathlib.Path(src1), pathlib.Path(src2)],
        equivalent_suffixes_list=expected_equivs,
        rename_flag=True,
        output_path=None
    )

    mock_run_equivalent_file_finder.assert_called_once_with(expected_args)


def test_find_equivalent_files_output_path(setup_find_equivalent_files):
    mock_run_equivalent_file_finder, src1, src2, output_path, equivs, expected_equivs, runner = setup_find_equivalent_files

    result = runner.invoke(cli.find_equivalent_files, [str(src1), str(src2), equivs, "--output", str(output_path)])

    assert result.exit_code == 0

    expected_args = EquivalentFileFinderArguments(
        source_paths=[pathlib.Path(src1), pathlib.Path(src2)],
        equivalent_suffixes_list=expected_equivs,
        rename_flag=False,
        output_path=pathlib.Path(output_path)
    )

    mock_run_equivalent_file_finder.assert_called_once_with(expected_args)


@pytest.fixture(scope="function")
def setup_compare_folders(mocker, tmpdir):
    mock_run_equivalent_file_finder = mocker.patch("wmul_file_manager.cli.run_folder_comparer")

    first_folder = tmpdir.join("first")
    first_folder.ensure(dir=True)
    second_folder = tmpdir.join("second")
    second_folder.ensure(dir=True)
    output_path = tmpdir.join("foo.txt")
    ignore_folder_1 = first_folder.join("ignore1")
    ignore_folder_1.ensure(dir=True)
    ignore_folder_2 = first_folder.join("ignore2")
    ignore_folder_2.ensure(dir=True)

    first_folder = pathlib.Path(first_folder)
    second_folder = pathlib.Path(second_folder)
    output_path = pathlib.Path(output_path)
    ignore_folder_1 = pathlib.Path(ignore_folder_1)
    ignore_folder_2 = pathlib.Path(ignore_folder_2)

    equivs = ".wav .mp3 .wav .ogg"
    expected_equivs = [".wav", ".mp3", ".wav", ".ogg"]

    runner = CliRunner()

    yield mock_run_equivalent_file_finder, first_folder, second_folder, ignore_folder_1, ignore_folder_2, output_path, \
          equivs, expected_equivs, runner


def test_compare_folders_no_options(setup_compare_folders):
    mock_run_equivalent_file_finder, first_folder, second_folder, ignore_folder_1, ignore_folder_2, output_path, \
    equivs, expected_equivs, runner = setup_compare_folders

    result = runner.invoke(cli.compare_folders, [str(first_folder), str(second_folder)])

    assert result.exit_code == 0

    expected_args = FolderComparerArguments(
        first_path=first_folder,
        second_path=second_folder,
        ignore_paths=[],
        equivalent_suffixes=None,
        name_only=False,
        name_size_only=False,
        output_path=None
    )

    mock_run_equivalent_file_finder.assert_called_once_with(expected_args)


def test_compare_folders_ignore_folders(setup_compare_folders):
    mock_run_equivalent_file_finder, first_folder, second_folder, ignore_folder_1, ignore_folder_2, output_path, \
    equivs, expected_equivs, runner = setup_compare_folders

    result = runner.invoke(
        cli.compare_folders,
        [str(first_folder), str(second_folder), "--ignore", str(ignore_folder_1), "--ignore", str(ignore_folder_2)]
    )

    assert result.exit_code == 0

    expected_args = FolderComparerArguments(
        first_path=first_folder,
        second_path=second_folder,
        ignore_paths=[ignore_folder_1, ignore_folder_2],
        equivalent_suffixes=None,
        name_only=False,
        name_size_only=False,
        output_path=None
    )

    mock_run_equivalent_file_finder.assert_called_once_with(expected_args)


def test_compare_folders_equivalents(setup_compare_folders):
    mock_run_equivalent_file_finder, first_folder, second_folder, ignore_folder_1, ignore_folder_2, output_path, \
    equivs, expected_equivs, runner = setup_compare_folders

    result = runner.invoke(cli.compare_folders, [str(first_folder), str(second_folder), "--equivalent", equivs])

    assert result.exit_code == 0

    expected_args = FolderComparerArguments(
        first_path=first_folder,
        second_path=second_folder,
        ignore_paths=[],
        equivalent_suffixes=expected_equivs,
        name_only=False,
        name_size_only=False,
        output_path=None
    )

    mock_run_equivalent_file_finder.assert_called_once_with(expected_args)


def test_compare_folders_output_path(setup_compare_folders):
    mock_run_equivalent_file_finder, first_folder, second_folder, ignore_folder_1, ignore_folder_2, output_path, \
    equivs, expected_equivs, runner = setup_compare_folders

    result = runner.invoke(cli.compare_folders, [str(first_folder), str(second_folder), "--output", str(output_path)])

    assert result.exit_code == 0

    expected_args = FolderComparerArguments(
        first_path=first_folder,
        second_path=second_folder,
        ignore_paths=[],
        equivalent_suffixes=None,
        name_only=False,
        name_size_only=False,
        output_path=output_path
    )

    mock_run_equivalent_file_finder.assert_called_once_with(expected_args)


find_old_directories_test_args = namedtuple(
    "find_old_directories_test_args",
    [
        "use_output",
        "use_junk_suffixes",
        "use_junk_names"
    ]
)


@pytest.fixture(scope="function", params=generate_binary_matrix_from_named_tuple(find_old_directories_test_args))
def setup_find_old_directories(mocker, tmpdir, request):
    parameter = request.param

    mock_run_find_old = mocker.patch("wmul_file_manager.cli.run_find_old_directories")

    first_path = tmpdir.join("foo_dir")
    first_path.ensure(dir=True)
    first_path = pathlib.Path(first_path)

    cutoff = "2018-05-15"
    expected_cutoff_date = datetime.datetime(year=2018, month=5, day=15, hour=23, minute=59, second=59)

    if parameter.use_output:
        output_path = pathlib.Path(tmpdir.join("foo.txt"))
    else:
        output_path = None

    if parameter.use_junk_suffixes:
        junk_suffixes = ".sfk .pk"
        expected_junk_suffixes = [".sfk", ".pk"]
    else:
        junk_suffixes = ""
        expected_junk_suffixes = []

    if parameter.use_junk_names:
        junk_names = "Thumbs.db"
        expected_junk_names = ["thumbs.db"]
    else:
        junk_names = ""
        expected_junk_names = []

    runner = CliRunner()

    return locals()


def test_find_old_directories(setup_find_old_directories):
    first_path = setup_find_old_directories["first_path"]
    cutoff = setup_find_old_directories["cutoff"]
    parameter = setup_find_old_directories["parameter"]
    output_path = setup_find_old_directories["output_path"]
    runner = setup_find_old_directories["runner"]
    expected_cutoff_date = setup_find_old_directories["expected_cutoff_date"]
    mock_run_find_old = setup_find_old_directories["mock_run_find_old"]
    junk_suffixes = setup_find_old_directories["junk_suffixes"]
    expected_junk_suffixes = setup_find_old_directories["expected_junk_suffixes"]
    junk_names = setup_find_old_directories["junk_names"]
    expected_junk_names = setup_find_old_directories["expected_junk_names"]

    cl_arg = [
        str(first_path),
        cutoff
    ]

    if parameter.use_output:
        cl_arg.extend(["--output", output_path])
    if parameter.use_junk_suffixes:
        cl_arg.extend(["--junk_suffix", junk_suffixes])
    if parameter.use_junk_names:
        cl_arg.extend(["--junk_name", junk_names])

    result = runner.invoke(cli.find_old_directories, cl_arg)

    assert result.exit_code == 0

    expected_arguments = FindOldDirectoriesArguments(
        first_path=first_path,
        recent_cutoff=expected_cutoff_date,
        output_path=output_path,
        junk_suffixes=expected_junk_suffixes,
        junk_names=expected_junk_names
    )

    mock_run_find_old.assert_called_once_with(expected_arguments)


@pytest.mark.skimmer_yesterday
def test_copy_skimmer_single_pair(fs, mocker):
    mock_run_skimmer_copy = mocker.patch("wmul_file_manager.cli.run_skimmer_copy")

    source = pathlib.Path("source")
    destination = pathlib.Path("destination")
    fs.create_dir(source)
    fs.create_dir(destination)

    runner = CliRunner()

    result = runner.invoke(cli.copy_skimmer, ["--pair", str(source), str(destination)])

    assert result.exit_code == 0

    mock_run_skimmer_copy.assert_called_once()

    _, call_kwargs = mock_run_skimmer_copy.call_args
    call_source_destination_pairs = call_kwargs["source_destination_path_pairs"]
    assert len(call_source_destination_pairs) == 1

    call_source, call_destination = call_source_destination_pairs[0]

    assert str(call_source) == str(source)
    assert str(call_destination) == str(destination)


@pytest.mark.skimmer_yesterday
def test_copy_skimmer_two_pair(fs, mocker):
    mock_run_skimmer_copy = mocker.patch("wmul_file_manager.cli.run_skimmer_copy")

    source_1 = pathlib.Path("source_1")
    source_2 = pathlib.Path("source_2")
    destination_1 = pathlib.Path("destination_1")
    destination_2 = pathlib.Path("destination_2")
    fs.create_dir(source_1)
    fs.create_dir(source_2)
    fs.create_dir(destination_1)
    fs.create_dir(destination_2)

    runner = CliRunner()

    result = runner.invoke(cli.copy_skimmer, ["--pair", str(source_1), str(destination_1),
                                              "--pair", str(source_2), str(destination_2)])

    assert result.exit_code == 0

    mock_run_skimmer_copy.assert_called_once()

    _, call_kwargs = mock_run_skimmer_copy.call_args
    call_source_destination_pairs = call_kwargs["source_destination_path_pairs"]
    assert len(call_source_destination_pairs) == 2

    for call_source_dest_pair in call_source_destination_pairs:
        call_source, call_destination = call_source_dest_pair

        str_call_source = str(call_source)

        if str_call_source == str(source_1):
            assert str(call_destination) == str(destination_1)
        elif str_call_source == str(source_2):
            assert str(call_destination) == str(destination_2)
        else:
            assert False


@pytest.mark.skimmer_yesterday
def test_copy_skimmer_one_item(fs, mocker):
    mock_run_skimmer_copy = mocker.patch("wmul_file_manager.cli.run_skimmer_copy")

    source_1 = pathlib.Path("source_1")
    fs.create_dir(source_1)

    runner = CliRunner()

    result = runner.invoke(cli.copy_skimmer, ["--pair", str(source_1)])

    assert not result.exit_code == 0

    mock_run_skimmer_copy.assert_not_called()


@pytest.mark.skimmer_yesterday
def test_copy_skimmer_three_items(fs, mocker):
    mock_run_skimmer_copy = mocker.patch("wmul_file_manager.cli.run_skimmer_copy")

    source_1 = pathlib.Path("source_1")
    source_2 = pathlib.Path("source_2")
    destination_1 = pathlib.Path("destination_1")
    fs.create_dir(source_1)
    fs.create_dir(source_2)
    fs.create_dir(destination_1)

    runner = CliRunner()

    result = runner.invoke(cli.copy_skimmer, ["--pair", str(source_1), str(destination_1),
                                              "--pair", str(source_2)])

    assert not result.exit_code == 0

    mock_run_skimmer_copy.assert_not_called()


@pytest.mark.skimmer_yesterday
def test_copy_skimmer_zero_pairs(fs, mocker):
    mock_run_skimmer_copy = mocker.patch("wmul_file_manager.cli.run_skimmer_copy")

    source_1 = pathlib.Path("source_1")
    fs.create_dir(source_1)

    runner = CliRunner()

    result = runner.invoke(cli.copy_skimmer)

    assert not result.exit_code == 0

    mock_run_skimmer_copy.assert_not_called()

delete_old_files_params, delete_old_files_ids = generate_true_false_matrix_from_list_of_strings(
    "delete_old_files_options",
     [
        "use_remove_folders",
        "use_suffixes",
        "use_days_old",
        "use_cutoff_date"
    ]
)

@pytest.fixture(scope="function", params=delete_old_files_params, ids=delete_old_files_ids)
def setup_delete_old_files(mocker, request, tmpdir):
    params = request.param

    mock_run_delete_old_files = mocker.patch("wmul_file_manager.cli.run_delete_old_files")

    first_path = tmpdir.join("first")
    first_path.ensure(dir=True)
    first_path = pathlib.Path(first_path)

    if params.use_days_old:
        days_old = "7"
        days_old_cutoff_date = datetime.datetime.today() - datetime.timedelta(days=int(days_old))
        days_old_cutoff_date = days_old_cutoff_date.replace(hour=0, minute=0, second=0, microsecond=0)
        days_old_cutoff_date = days_old_cutoff_date.astimezone(tz=datetime.timezone.utc)
    else:
        days_old = None
        days_old_cutoff_date = None

    if params.use_cutoff_date:
        cutoff = "2018-05-15"
        cutoff_date = datetime.datetime.strptime(cutoff, "%Y-%m-%d")
        cutoff_date = cutoff_date.astimezone(tz=datetime.timezone.utc)
    else:
        cutoff = None
        cutoff_date = None

    if params.use_suffixes:
        limited_suffixes_list = ".wav"
    else:
        limited_suffixes_list = None

    runner = CliRunner()

    yield mock_run_delete_old_files, params, first_path, days_old, days_old_cutoff_date, cutoff, cutoff_date, \
          limited_suffixes_list, runner


@pytest.mark.delete_old
def test_delete_old_files_run_delete_called_correctly(setup_delete_old_files):
    mock_run_delete_old_files, params, first_path, days_old, days_old_cutoff_date, cutoff, cutoff_date, \
        limited_suffixes_list, runner = setup_delete_old_files

    run_args = [str(first_path)]

    if params.use_cutoff_date:
        run_args.extend(["--cutoff_date", cutoff])
        expected_cutoff_date = cutoff_date

    if params.use_days_old:
        run_args.extend(["--days_old", days_old])
        expected_cutoff_date = days_old_cutoff_date


    if params.use_remove_folders:
        run_args.append("--remove_folders")

    if params.use_suffixes:
        run_args.extend(["--suffixes", limited_suffixes_list])

    result = runner.invoke(cli.delete_old_files, run_args)

    if params.use_days_old and params.use_cutoff_date:
        assert result.exit_code != 0
        mock_run_delete_old_files.assert_not_called()
    elif not (params.use_days_old or params.use_cutoff_date):
        assert result.exit_code != 0
        mock_run_delete_old_files.assert_not_called()
    else:
        assert result.exit_code == 0

        expected_args = DeleteOldFilesArguments(
            source_path=first_path,
            remove_folders_flag=params.use_remove_folders,
            limited_suffixes_flag=params.use_suffixes,
            limited_suffixes_list=limited_suffixes_list,
            older_than=expected_cutoff_date
        )

        mock_run_delete_old_files.assert_called_once_with(expected_args)


did_skimmer_copy_test_options = namedtuple(
    "did_skimmer_copy_test_options",
    [
        "use_port",
        "use_password",
        "use_multiple_email"
    ]
)


class TestDidSkimmerCopy:

    @pytest.fixture(scope="function", params=generate_binary_matrix_from_named_tuple(did_skimmer_copy_test_options))
    def setup_did_skimmer_copy(self, mocker, tmpdir, request):
        params = request.param

        mock_emailer = "mock_emailer"
        mock_email_sender = mocker.patch(
            "wmul_file_manager.cli.wmul_emailer.EmailSender",
            autospec=True
        )
        mock_email_sender.return_value = mock_emailer

        mock_calendar = "mock_calendar"
        mock_load_calendar = mocker.patch(
            "wmul_file_manager.utilities.skimmer_calendar.load_skimmer_calendar",
            autospec=True
        )
        mock_load_calendar.return_value = mock_calendar

        mock_run_did_skimmer_copy = mocker.patch(
            "wmul_file_manager.DidTheSkimmerCopyTheFiles.DidTheSkimmerCopyTheFiles.run_script",
            autospec=True
        )

        directory_1 = tmpdir.join("dir_1")
        directory_1.ensure(dir=True)
        directory_1 = pathlib.Path(directory_1)
        directory_2 = tmpdir.join("dir_2")
        directory_2.ensure(dir=True)
        directory_2 = pathlib.Path(directory_2)

        calendar_file = tmpdir.join("calendar.txt")
        calendar_file.write_binary(random_bytes())
        calendar_file = pathlib.Path(calendar_file)

        mock_email_address_1 = "mock_email_address_1"
        mock_email_address_2 = "mock_email_address_2"
        mock_server = "mock_server"
        mock_port = 10
        mock_username = "mock_username"
        mock_password = "mock_password"

        runner = CliRunner()

        yield params, mock_emailer, mock_email_sender, mock_calendar, mock_load_calendar, mock_run_did_skimmer_copy, \
              directory_1, directory_2, calendar_file, mock_email_address_1, mock_email_address_2, mock_server, \
              mock_port, mock_username, mock_password, runner

    @pytest.mark.did_skimmer_copy
    def test_did_skimmer_copy(self, setup_did_skimmer_copy):
        params, mock_emailer, mock_email_sender, mock_calendar, mock_load_calendar, mock_run_did_skimmer_copy, \
            directory_1, directory_2, calendar_file, mock_email_address_1, mock_email_address_2, mock_server, \
            mock_port, mock_username, mock_password, runner = setup_did_skimmer_copy

        invoke_args = [
            str(directory_1),
            str(directory_2),
            str(calendar_file),
            "--email",
            mock_email_address_1,
            "--server",
            mock_server,
            "--username",
            mock_username
        ]

        if params.use_port:
            invoke_args.extend(["--port", mock_port])
            expected_port = mock_port
        else:
            expected_port = 25

        if params.use_password:
            invoke_args.extend(["--password", mock_password])
            expected_password = mock_password
        else:
            expected_password = None

        if params.use_multiple_email:
            invoke_args.extend(["--email", mock_email_address_2])
            expected_email = (mock_email_address_1, mock_email_address_2)
        else:
            expected_email = (mock_email_address_1,)

        results = runner.invoke(cli.did_skimmer_copy, invoke_args)

        assert results.exit_code == 0

        mock_email_sender.assert_called_once_with(
            server_host=mock_server,
            port=expected_port,
            user_name=mock_username,
            password=expected_password,
            destination_email_addresses=expected_email,
            from_email_address="skimmer_copy_watcher@wmul-nas-4"
        )

        mock_load_calendar.assert_called_once_with(calendar_file)

        mock_run_did_skimmer_copy.assert_called_once()

        call_args, _ = mock_run_did_skimmer_copy.call_args
        dscf, = call_args
        assert isinstance(dscf, DidTheSkimmerCopyTheFiles)
        assert dscf.directories == [directory_1, directory_2]
        assert dscf._skimmer_calendar == mock_calendar
        assert dscf.emailer == mock_emailer


class TestIsSkimmerWorking:

    @pytest.fixture(scope="function", params=generate_binary_matrix_from_named_tuple(did_skimmer_copy_test_options))
    def setup_is_skimmer_working(self, mocker, tmpdir, request):
        params = request.param

        mock_emailer = "mock_emailer"
        mock_email_sender = mocker.patch(
            "wmul_file_manager.cli.wmul_emailer.EmailSender",
            autospec=True
        )
        mock_email_sender.return_value = mock_emailer

        mock_calendar = "mock_calendar"
        mock_load_calendar = mocker.patch(
            "wmul_file_manager.utilities.skimmer_calendar.load_skimmer_calendar",
            autospec=True
        )
        mock_load_calendar.return_value = mock_calendar

        mock_run_is_skimmer_working = mocker.patch(
            "wmul_file_manager.IsTheSkimmerWorking.IsTheSkimmerWorking.run_script",
            autospec=True
        )

        mock_date_directory = "mock_date_directory"
        mock_filename_regex = "mock_filename_regex"
        mock_expected_file_quantity = "mock_expected_file_quantity"
        mock_hour_info = IsTheSkimmerWorking._HourInformation(
            date_directory=mock_date_directory,
            matching_filename_regex=mock_filename_regex,
            expected_file_quantity=mock_expected_file_quantity
        )
        mocker.patch(
            "wmul_file_manager.IsTheSkimmerWorking._get_last_hour_information",
            autospec=True,
            return_value=mock_hour_info
        )

        directory_1 = tmpdir.join("dir_1")
        directory_1.ensure(dir=True)
        directory_1 = pathlib.Path(directory_1)
        directory_2 = tmpdir.join("dir_2")
        directory_2.ensure(dir=True)
        directory_2 = pathlib.Path(directory_2)

        calendar_file = tmpdir.join("calendar.txt")
        calendar_file.write_binary(random_bytes())
        calendar_file = pathlib.Path(calendar_file)

        mock_email_address_1 = "mock_email_address_1"
        mock_email_address_2 = "mock_email_address_2"
        mock_server = "mock_server"
        mock_port = 10
        mock_username = "mock_username"
        mock_password = "mock_password"

        runner = CliRunner()

        yield params, mock_emailer, mock_email_sender, mock_calendar, mock_load_calendar, mock_run_is_skimmer_working, \
              directory_1, directory_2, calendar_file, mock_email_address_1, mock_email_address_2, mock_server, \
              mock_port, mock_username, mock_password, runner, mock_date_directory, mock_filename_regex, \
              mock_expected_file_quantity

    @pytest.mark.is_skimmer_working
    def test_did_skimmer_copy(self, setup_is_skimmer_working):
        params, mock_emailer, mock_email_sender, mock_calendar, mock_load_calendar, mock_run_is_skimmer_working, \
            directory_1, directory_2, calendar_file, mock_email_address_1, mock_email_address_2, mock_server, \
            mock_port, mock_username, mock_password, runner, mock_date_directory, \
            mock_filename_regex, mock_expected_file_quantity = setup_is_skimmer_working

        invoke_args = [
            str(directory_1),
            str(directory_2),
            str(calendar_file),
            "--email",
            mock_email_address_1,
            "--server",
            mock_server,
            "--username",
            mock_username
        ]

        if params.use_port:
            invoke_args.extend(["--port", mock_port])
            expected_port = mock_port
        else:
            expected_port = 25

        if params.use_password:
            invoke_args.extend(["--password", mock_password])
            expected_password = mock_password
        else:
            expected_password = None

        if params.use_multiple_email:
            invoke_args.extend(["--email", mock_email_address_2])
            expected_email = (mock_email_address_1, mock_email_address_2)
        else:
            expected_email = (mock_email_address_1,)

        results = runner.invoke(cli.is_skimmer_working, invoke_args)

        assert results.exit_code == 0

        mock_email_sender.assert_called_once_with(
            server_host=mock_server,
            port=expected_port,
            user_name=mock_username,
            password=expected_password,
            destination_email_addresses=expected_email,
            from_email_address="skimmer_watcher@wmul-nas-4"
        )

        mock_load_calendar.assert_called_once_with(calendar_file)

        mock_run_is_skimmer_working.assert_called_once()

        call_args, call_kwargs = mock_run_is_skimmer_working.call_args
        isw, = call_args
        directory_list_arg = call_kwargs["directory_list"]
        assert isinstance(isw, IsTheSkimmerWorking.IsTheSkimmerWorking)
        assert isw.emailer == mock_emailer
        assert isinstance(isw.problems, list)
        assert isw.date_directory == mock_date_directory
        assert isw.matching_filename_regex == mock_filename_regex
        assert directory_list_arg == [directory_1, directory_2]
        assert isw.expected_file_quantity == mock_expected_file_quantity
