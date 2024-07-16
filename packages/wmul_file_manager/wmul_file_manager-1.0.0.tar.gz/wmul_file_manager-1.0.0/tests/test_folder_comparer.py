"""
@Author = 'Mike Stanley'

============ Change Log ============
2018-May-10 = Created.

============ License ============
The MIT License (MIT)

Copyright (c) 2018 Michael Stanley

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
import contextlib
import pathlib
import pytest
from collections import namedtuple
from wmul_file_manager import FolderComparer
from wmul_file_manager.utilities import graph
import wmul_test_utils


def test_get_file_data_exists(fs, mocker):
    mock_comparer = "mock_comparer"
    mock_equivalent_exts = ""
    mock_info_factory = mocker.Mock(
        side_effect=FolderComparer._FileInformation.get_factory(
            equivalent_exts=mock_equivalent_exts,
            comparer=mock_comparer
        )
    )

    mock_mtime = 300
    mock_size = 500

    mock_root_path = pathlib.Path("src")
    file_under_test = mock_root_path / "foo.txt"

    fs.create_file(file_under_test)
    file_under_test.stat = mocker.Mock(
        return_value=mocker.Mock(st_mtime=mock_mtime, st_size=mock_size)
    )

    file_info = FolderComparer._get_file_data(file_under_test, mock_root_path, mock_info_factory)

    mock_info_factory.assert_called_once()
    _, call_kwargs = mock_info_factory.call_args
    call_file_path = call_kwargs["full_path"]
    call_root_path = call_kwargs["root_path"]
    call_mtime = call_kwargs["mtime"]
    call_size = call_kwargs["size"]

    assert str(call_file_path) == str(file_under_test)
    assert str(call_root_path) == str(mock_root_path)
    assert call_mtime == mock_mtime
    assert call_size == mock_size

    assert isinstance(file_info, FolderComparer._FileInformation)


def test_get_file_data_doesnt_exists(mocker):
    mock_comparer = "mock_comparer"
    mock_equivalent_exts = ""
    mock_info_factory = mocker.Mock(
        side_effect=FolderComparer._FileInformation.get_factory(
            equivalent_exts=mock_equivalent_exts,
            comparer=mock_comparer
        )
    )
    expected_mtime = 0
    expected_size = 0

    mock_root_path = pathlib.Path("src")
    file_under_test = mock_root_path / "foo.txt"

    file_info = FolderComparer._get_file_data(file_under_test, mock_root_path, mock_info_factory)

    mock_info_factory.assert_called_once()
    _, call_kwargs = mock_info_factory.call_args
    call_file_path = call_kwargs["full_path"]
    call_root_path = call_kwargs["root_path"]
    call_mtime = call_kwargs["mtime"]
    call_size = call_kwargs["size"]

    assert str(call_file_path) == str(file_under_test)
    assert str(call_root_path) == str(mock_root_path)
    assert call_mtime == expected_mtime
    assert call_size == expected_size

    assert isinstance(file_info, FolderComparer._FileInformation)


@pytest.fixture(scope="function")
def setup_walk_dir(fs, mocker, caplog):
    def mock_get_file_data_function(file_item, root_path, file_info_factory):
        file_str = str(file_item)
        if file_str[-1] == "Z":
            raise PermissionError("Fake Permission Error")
        else:
            return file_item
    mock_get_file_data = mocker.patch("wmul_file_manager.FolderComparer._get_file_data",
                                      mocker.Mock(side_effect=mock_get_file_data_function))

    root_folder = pathlib.Path("src")
    sub_folder = root_folder / "sub_folder"
    fs.create_dir(root_folder)
    fs.create_dir(sub_folder)

    non_permission_files = [
        root_folder / "file1.txtZ",
        sub_folder / "file10.txtZ"
    ]

    permission_files = [
        root_folder / "file2.doc",
        root_folder / "file3.mp3",
        sub_folder / "file14.wav",
        sub_folder / "file15.ogg"
    ]

    all_files = [
        *non_permission_files,
        *permission_files
    ]

    for file_item in all_files:
        fs.create_file(file_item)

    path_contents = []
    mock_file_info_factory = "mock_file_info_factory"
    no_permissions_list = []

    FolderComparer._walk_directory(root_folder, root_folder, path_contents, mock_file_info_factory, no_permissions_list)

    yield mock_get_file_data, root_folder, non_permission_files, permission_files, all_files, path_contents, \
          mock_file_info_factory, no_permissions_list, caplog.text


def test_walk_dir_get_file_data_called_correctly(setup_walk_dir, mocker):
    mock_get_file_data, root_folder, non_permission_files, permission_files, all_files, path_contents, \
    mock_file_info_factory, no_permissions_list, caplog_text = setup_walk_dir

    expected_calls = []
    for item in all_files:
        expected_calls.append(mocker.call(item, root_folder, mock_file_info_factory))

    mock_get_file_data.assert_has_calls(expected_calls, any_order=True)
    assert mock_get_file_data.call_count == len(expected_calls)


def test_walk_dir_correct_files_in_no_permissions_list(setup_walk_dir):
    mock_get_file_data, root_folder, non_permission_files, permission_files, all_files, path_contents, \
    mock_file_info_factory, no_permissions_list, caplog_text = setup_walk_dir

    for item in non_permission_files:
        assert item in no_permissions_list

    assert len(non_permission_files) == len(no_permissions_list)


def test_walk_dir_correct_files_in_path_contents(setup_walk_dir):
    mock_get_file_data, root_folder, non_permission_files, permission_files, all_files, path_contents, \
    mock_file_info_factory, no_permissions_list, caplog_text = setup_walk_dir

    for item in permission_files:
        assert item in path_contents

    assert len(permission_files) == len(path_contents)


def test_walk_dir_no_permissions_logged_correctly(setup_walk_dir):
    mock_get_file_data, root_folder, non_permission_files, permission_files, all_files, path_contents, \
    mock_file_info_factory, no_permissions_list, caplog_text = setup_walk_dir

    expected_log = "No permissions on file."
    log_text_lines = caplog_text.split("\n")
    log_lines_containing_expected = [log_line for log_line in log_text_lines if expected_log in log_line]
    assert len(log_lines_containing_expected) == 2

    unexpected_log = "No permission on directory."
    assert unexpected_log not in caplog_text


def test__collect_path_contents(mocker):
    mock_walk_dir = mocker.patch("wmul_file_manager.FolderComparer._walk_directory")

    mock_first_path = "mock_first_path"
    mock_second_path = "mock_second_path"
    mock_ignore_path_1 = "mock_ignore_path_1"
    mock_ignore_path_2 = "mock_ignore_path_2"

    arguments = mocker.Mock(
        first_path=mock_first_path,
        second_path=mock_second_path,
        ignore_paths=[mock_ignore_path_1, mock_ignore_path_2]
    )

    mock_file_info_factory = "mock_file_info_factory"

    first_path_contents, second_path_contents, ignore_contents, no_permissions_list = \
        FolderComparer._collect_path_contents(arguments=arguments, file_info_factory=mock_file_info_factory)

    expected_calls = [
        mocker.call(mock_first_path, mock_first_path, first_path_contents, mock_file_info_factory, no_permissions_list),
        mocker.call(mock_second_path, mock_second_path, second_path_contents, mock_file_info_factory,
                    no_permissions_list),
        mocker.call(mock_ignore_path_1, mock_first_path, ignore_contents, mock_file_info_factory, no_permissions_list),
        mocker.call(mock_ignore_path_2, mock_first_path, ignore_contents, mock_file_info_factory, no_permissions_list)
    ]

    mock_walk_dir.assert_has_calls(expected_calls)
    assert mock_walk_dir.call_count == len(expected_calls)


def test__find_duplicates():
    list_under_test = [
        "Foo",
        "Bar",
        "Foo",
        "Baz",
        "Apple",
        "Banana",
        "Apple",
        "Apple",
    ]

    duplicates = FolderComparer._find_duplicates(list_under_test)

    assert "Foo" in duplicates
    assert "Apple" in duplicates
    assert len(duplicates) == 2


def test__find_differences_between_paths():
    first_path_contents = [
        "Foo",
        "Bar",
        "Foo",
        "Baz",
        "Apple",
        "Banana",
        "Apple",
        "Apple",
        "Cranberry",
        "Didgeridoo",
        "Natty Narwhal",
        "Feisty Fawn"
    ]

    second_path_contents = [
        "Cupcake",
        "Donut",
        "Eclair",
        "Froyo",
        "Foo",
        "Banana",
        "Trusty Tahr"
    ]

    ignore_contents = [
        "Bar",
        "Feisty Fawn",
        "Trusty Tahr"
    ]

    expected_first_minus_second = {
        "Baz",
        "Apple",
        "Cranberry",
        "Didgeridoo",
        "Natty Narwhal",
    }

    expected_second_minus_first = {
        "Cupcake",
        "Donut",
        "Eclair",
        "Froyo",
        "Trusty Tahr"
    }

    results_first_minus_second, results_second_minus_first = FolderComparer._find_differences_between_paths(
        first_path_contents=first_path_contents,
        second_path_contents=second_path_contents,
        ignore_contents=ignore_contents
    )

    assert expected_first_minus_second == results_first_minus_second
    assert expected_second_minus_first == results_second_minus_first


@pytest.fixture(scope="function")
def setup__compare_paths(mocker):
    mock_arguments = "mock_arguments"
    mock_file_info_factory = "mock_file_info_factory"

    mock_first_path_contents = "mock_first_path_contents"
    mock_second_path_contents = "mock_second_path_contents"
    mock_ignore_contents = "mock_ignore_contents"
    mock_no_permissions_list = "mock_no_permissions_list"

    mock_collect_path_contents = mocker.patch(
        "wmul_file_manager.FolderComparer._collect_path_contents",
        mocker.Mock(
            return_value=(
                mock_first_path_contents,
                mock_second_path_contents,
                mock_ignore_contents,
                mock_no_permissions_list
            )
        )
    )

    mock_first_dupes = "mock_first_dupes"

    mock_find_duplicates = mocker.patch(
        "wmul_file_manager.FolderComparer._find_duplicates",
        mocker.Mock(return_value=mock_first_dupes)
    )

    mock_first_minus_second = "mock_first_minus_second"
    mock_second_minus_first = "mock_second_minus_first"

    mock_find_differences = mocker.patch(
        "wmul_file_manager.FolderComparer._find_differences_between_paths",
        mocker.Mock(return_value=(mock_first_minus_second, mock_second_minus_first))
    )

    result_no_permissions_list, result_first_dupes, result_first_minus_second, result_second_minus_first = \
        FolderComparer._compare_paths(arguments=mock_arguments, file_info_factory=mock_file_info_factory)

    yield mock_collect_path_contents, mock_find_duplicates, mock_find_differences, mock_arguments, \
          mock_file_info_factory, mock_first_path_contents, mock_second_path_contents, mock_ignore_contents, \
          mock_no_permissions_list, mock_first_dupes, mock_first_minus_second, mock_second_minus_first, \
          result_no_permissions_list, result_first_dupes, result_first_minus_second, result_second_minus_first


def test__compare_paths_collect_path_contents_called_correctly(setup__compare_paths):
    mock_collect_path_contents, _, _, mock_arguments, mock_file_info_factory, _, _, _, _, _, _, _, _, _, _,\
        _ = setup__compare_paths
    mock_collect_path_contents.assert_called_once_with(mock_arguments, mock_file_info_factory)


def test__compare_paths_find_duplicates_called_correctly(setup__compare_paths):
    _, mock_find_duplicates, _, _, _, mock_first_path_contents, _, _, _, _, _, _, _, _, _, _ = setup__compare_paths
    mock_find_duplicates.assert_called_once_with(mock_first_path_contents)


def test__compare_paths_find_differences_called_correctly(setup__compare_paths):
    _, _, mock_find_differences, _, _, mock_first_path_contents, mock_second_path_contents, mock_ignore_contents, \
        _, _, _, _, _, _, _, _ = setup__compare_paths
    mock_find_differences.assert_called_once_with(mock_first_path_contents, mock_second_path_contents,
                                                  mock_ignore_contents)


def test__compare_paths_returns_correct_data(setup__compare_paths):
    _, _, _, _, _, _, _, _, mock_no_permissions_list, mock_first_dupes, mock_first_minus_second, \
        mock_second_minus_first, result_no_permissions_list, result_first_dupes, result_first_minus_second, \
        result_second_minus_first = setup__compare_paths

    assert mock_no_permissions_list == result_no_permissions_list
    assert mock_first_dupes == result_first_dupes
    assert mock_first_minus_second == result_first_minus_second
    assert mock_second_minus_first == result_second_minus_first


def test__write_results(mocker):
    mock_result_writer_contents = []

    def mock_result_writer(data):
        mock_result_writer_contents.append(data)

    def mock_object_cleaner(item):
        return item

    mocker.patch("wmul_file_manager.FolderComparer.object_cleaner", mock_object_cleaner)

    mock_no_permissions_list = [
        "Apple",
        "Banana",
        "Cupcake"
    ]

    mock_first_dupes = [
        "Doughnut",
        "Eclair",
        "Froyo"
    ]

    mock_first_minus_second = [
        "Gingerbread",
        "Honeycomb",
        "Ice-Cream Sandwich"
    ]

    mock_second_minus_first = [
        "Jelly Bean",
        "KitKat",
        "Lollypop"
    ]

    mock_results = (
        mock_no_permissions_list,
        mock_first_dupes,
        mock_first_minus_second,
        mock_second_minus_first
    )

    expected_contents = [
        "Folders without permission",
        "Apple",
        "Banana",
        "Cupcake",
        "#####################################################################################",
        "#####################################################################################",
        "#####################################################################################\n\n",
        "Duplicates in First",
        "Doughnut",
        "Eclair",
        "Froyo",
        "#####################################################################################",
        "#####################################################################################",
        "#####################################################################################\n\n",
        "First Minus Second",
        "Gingerbread",
        "Honeycomb",
        "Ice-Cream Sandwich",
        "#####################################################################################",
        "#####################################################################################",
        "#####################################################################################\n\n",
        "Second Minus First",
        "Jelly Bean",
        "KitKat",
        "Lollypop"
    ]

    FolderComparer._write_results(mock_result_writer, mock_results)

    assert mock_result_writer_contents == expected_contents


_run_script_test_params = [
    "name_only",
    "name_size_only",
    "equivalent_suffixes",
    "name_time_size"
]

_run_script_test_ids = [
    "name_only",
    "name_size_only",
    "equivalent_suffixes",
    "name_time_size"
]


@pytest.fixture(scope="function",  params=_run_script_test_params, ids=_run_script_test_ids)
def setup_run_script(mocker, request):
    param = request.param

    name_only = name_size_only = False
    equivalent_suffixes = ""

    if param == "name_only":
        name_only = True
    elif param == "name_size_only":
        name_size_only = True
    elif param == "equivalent_suffixes":
        equivalent_suffixes = "equivalent_suffixes"

    mock_equivalency_graph = "mock_equivalency_graph"
    mock_generate_equivalency_graph = mocker.patch(
        "wmul_file_manager.FolderComparer.generate_equivalency_graph",
        mocker.Mock(return_value=mock_equivalency_graph)
    )

    mock_factory = "mock_factory"
    mock_get_factory = mocker.patch(
        "wmul_file_manager.FolderComparer._FileInformation.get_factory",
        mocker.Mock(return_value=mock_factory)
    )

    mock_results = "mock_results"
    mock_compare_paths = mocker.patch(
        "wmul_file_manager.FolderComparer._compare_paths",
        mocker.Mock(return_value=mock_results)
    )

    mock_result_writer = mocker.Mock()

    @contextlib.contextmanager
    def mock_writer_function(file_name):
        yield mock_result_writer

    mock_get_writer = mocker.patch(
        "wmul_file_manager.FolderComparer.get_writer",
        mocker.Mock(side_effect=mock_writer_function)
    )

    mock_write_results = mocker.patch("wmul_file_manager.FolderComparer._write_results")

    mock_output_path = "mock_output_path"

    run_script_arguments = mocker.Mock(
        name_only=name_only,
        name_size_only=name_size_only,
        equivalent_suffixes=equivalent_suffixes,
        output_path=mock_output_path
    )

    FolderComparer.run_script(arguments=run_script_arguments)

    return wmul_test_utils.make_namedtuple(
        "setup_run_script",
        param=param,
        equivalent_suffixes=equivalent_suffixes,
        mock_equivalency_graph=mock_equivalency_graph,
        mock_generate_equivalency_graph=mock_generate_equivalency_graph,
        mock_factory=mock_factory,
        mock_get_factory=mock_get_factory,
        mock_results=mock_results,
        mock_compare_paths=mock_compare_paths,
        mock_result_writer=mock_result_writer,
        mock_get_writer=mock_get_writer,
        mock_write_results=mock_write_results,
        mock_output_path=mock_output_path,
        run_script_arguments=run_script_arguments,
    )


def test_generate_equivalency_graph_called_correctly(setup_run_script):
    if setup_run_script.param == "equivalent_suffixes":
        setup_run_script.mock_generate_equivalency_graph.assert_called_once_with(setup_run_script.equivalent_suffixes)
    else:
        setup_run_script.mock_generate_equivalency_graph.assert_not_called()


def test_get_factory_called_correctly(setup_run_script):
    if setup_run_script.param == "name_only":
        setup_run_script.mock_get_factory.assert_called_once_with(
            equivalent_exts=None,
            comparer=FolderComparer._FileInformationComparer_NameOnly
        )
    elif setup_run_script.param == "name_size_only":
        setup_run_script.mock_get_factory.assert_called_once_with(
            equivalent_exts=None,
            comparer=FolderComparer._FileInformationComparer_NameSizeOnly
        )
    elif setup_run_script.param == "equivalent_suffixes":
        setup_run_script.mock_get_factory.assert_called_once_with(
            equivalent_exts=setup_run_script.mock_equivalency_graph,
            comparer=FolderComparer._FileInformationComparer_EquivalentPaths
        )
    else:
        setup_run_script.mock_get_factory.assert_called_once_with(
            equivalent_exts=None,
            comparer=FolderComparer._FileInformationComparer_Name_mtime_size
        )


def test_compare_paths_called_correctly(setup_run_script):
    setup_run_script.mock_compare_paths.assert_called_once_with(
        arguments=setup_run_script.run_script_arguments,
        file_info_factory=setup_run_script.mock_factory
    )


def test_get_writer_called_correctly(setup_run_script):
    setup_run_script.mock_get_writer.assert_called_once_with(
        file_name=setup_run_script.mock_output_path
    )


def test_write_results_called_correctly(setup_run_script):
    setup_run_script.mock_write_results.assert_called_once_with(
        setup_run_script.mock_result_writer,
        setup_run_script.mock_results
    )
