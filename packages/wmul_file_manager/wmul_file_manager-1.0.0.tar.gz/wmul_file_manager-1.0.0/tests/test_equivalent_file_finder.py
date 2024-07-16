"""
@Author = 'Mike Stanley'

============ Change Log ============
2018-May-09 = Created.

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
import random
from wmul_file_manager import EquivalentFileFinder
from wmul_file_manager.utilities.graph import generate_equivalency_graph


@pytest.fixture(scope="function", params=[True, False])
def setup__file_info_with_equivalences(request):
    use_factory = request.param
    full_path_0 = "foo.wav"
    full_path_1 = "foo.mp3"
    full_path_2 = "bar.txt"
    full_path_3 = "baz.doc"
    equivalent_suffixes = [".wav", ".mp3", ".wav", ".ogg"]
    equivalency_graph = generate_equivalency_graph(equivalent_suffixes)
    empty_equivalency_graph = generate_equivalency_graph([])

    if use_factory:
        factory = EquivalentFileFinder._FileInformationWithSuffixEquivalence.get_factory(equivalency_graph)
        empty_equivalency_factory = EquivalentFileFinder._FileInformationWithSuffixEquivalence.get_factory(empty_equivalency_graph)

        path_0_info = factory(full_path_0)
        path_1_info = factory(full_path_1)
        path_2_info = factory(full_path_2)
        path_3_info = empty_equivalency_factory(full_path_3)
    else:
        path_0_info = EquivalentFileFinder._FileInformationWithSuffixEquivalence(full_path_0, equivalency_graph)
        path_1_info = EquivalentFileFinder._FileInformationWithSuffixEquivalence(full_path_1, equivalency_graph)
        path_2_info = EquivalentFileFinder._FileInformationWithSuffixEquivalence(full_path_2, equivalency_graph)
        path_3_info = EquivalentFileFinder._FileInformationWithSuffixEquivalence(full_path_3, empty_equivalency_graph)

    yield full_path_0, full_path_1, full_path_2, full_path_3, path_0_info, path_1_info, path_2_info, path_3_info


def test__file_info_with_equivalences_full_paths_correct(setup__file_info_with_equivalences):
    full_path_0, full_path_1, full_path_2, full_path_3, path_0_info, path_1_info, path_2_info, \
        path_3_info = setup__file_info_with_equivalences

    assert path_0_info.FullPath == full_path_0
    assert path_1_info.FullPath == full_path_1
    assert path_2_info.FullPath == full_path_2
    assert path_3_info.FullPath == full_path_3


def test__file_info_with_equivalences_equivalent_paths_correct(setup__file_info_with_equivalences):
    _, _, _, _, path_0_info, path_1_info, path_2_info, path_3_info = setup__file_info_with_equivalences

    expected_paths_0_and_1_equivs = {
        pathlib.Path("foo.mp3"),
        pathlib.Path("foo.wav"),
        pathlib.Path("foo.ogg")
    }
    expected_path_2_equivs = {pathlib.Path("bar.txt")}
    expected_path_3_equivs = {pathlib.Path("baz.doc")}

    assert expected_paths_0_and_1_equivs == path_0_info.EquivalentPaths
    assert expected_paths_0_and_1_equivs == path_1_info.EquivalentPaths
    assert expected_path_2_equivs == path_2_info.EquivalentPaths
    assert expected_path_3_equivs == path_3_info.EquivalentPaths


def test__file_info_with_equivalences_equality_correct(setup__file_info_with_equivalences):
    _, _, _, _, path_0_info, path_1_info, path_2_info, path_3_info = setup__file_info_with_equivalences

    assert path_0_info == path_1_info
    assert path_0_info not in [path_2_info, path_3_info]
    assert path_1_info not in [path_2_info, path_3_info]
    assert path_2_info not in [path_0_info, path_1_info, path_3_info]
    assert path_3_info not in [path_0_info, path_1_info, path_2_info]


def test__file_info_with_equivalences_hash_correct(setup__file_info_with_equivalences):
    _, _, _, _, path_0_info, path_1_info, path_2_info, path_3_info = setup__file_info_with_equivalences

    expected_paths_0_and_1_hash = hash("foo.mp3foo.oggfoo.wav")
    expected_path_2_hash = hash("bar.txt")
    expected_path_3_hash = hash("baz.doc")

    assert expected_paths_0_and_1_hash == hash(path_0_info)
    assert expected_paths_0_and_1_hash == hash(path_1_info)
    assert expected_path_2_hash == hash(path_2_info)
    assert expected_path_3_hash == hash(path_3_info)


def test__file_info_with_equivalences_str_correct(setup__file_info_with_equivalences):
    _, _, _, _, path_0_info, path_1_info, path_2_info, path_3_info = setup__file_info_with_equivalences

    expected_paths_0_and_1_str = "foo.mp3\t\tfoo.ogg\t\tfoo.wav"
    expected_path_2_str = "bar.txt"
    expected_path_3_str = "baz.doc"

    assert expected_paths_0_and_1_str == str(path_0_info)
    assert expected_paths_0_and_1_str == str(path_1_info)
    assert expected_path_2_str == str(path_2_info)
    assert expected_path_3_str == str(path_3_info)


def test__rename_this_file(tmpdir):
    random_bytes = bytearray(random.randint(0, 255) for i in range(100))

    test_file = tmpdir.join("foo.txt")
    test_file.write_binary(random_bytes)
    expected_file = tmpdir.join("foo_txt.txt")

    assert test_file.check()
    assert not expected_file.check()

    EquivalentFileFinder._rename_this_file(pathlib.Path(test_file))

    assert expected_file.check()
    assert not test_file.check()

    file_data = expected_file.read_binary()
    assert file_data == random_bytes


@pytest.fixture(scope="function")
def setup__rename_equivalent_files(mocker, fs, caplog):
    mock_rename_this_file = mocker.patch("wmul_file_manager.EquivalentFileFinder._rename_this_file")

    temp_path = pathlib.Path("foo")

    test_foo_dupes = [
        temp_path / "foo.doc",
        temp_path / "foo.docx"
    ]
    test_bar_dupes = [
        temp_path / "bar.wav",
        temp_path / "bar.mp3",
        temp_path / "bar.ogg"
    ]
    non_existent_dupe = temp_path / "baz.txt"

    all_dupes = [
        *test_foo_dupes,
        *test_bar_dupes,
        non_existent_dupe
    ]

    all_expected_dupes = [
        *test_foo_dupes,
        *test_bar_dupes,
    ]

    for dupe in all_expected_dupes:
        fs.create_file(dupe)

    EquivalentFileFinder._rename_equivalent_files(all_dupes)

    yield mock_rename_this_file, all_expected_dupes, non_existent_dupe, caplog.text


def test__rename_equivalent_files_rename_called_correctly(setup__rename_equivalent_files):
    mock_rename_this_file, all_expected_dupes, non_existent_dupe, caplog_text = setup__rename_equivalent_files

    for dupe in all_expected_dupes:
        mock_rename_this_file.assert_any_call(dupe)

    assert mock_rename_this_file.call_count == len(all_expected_dupes)


def test__rename_equivalent_files_error_logged_correctly(setup__rename_equivalent_files):
    mock_rename_this_file, all_expected_dupes, non_existent_dupe, caplog_text = setup__rename_equivalent_files

    expected_entry = f"Equiv does not exist. {str(non_existent_dupe)}"
    assert expected_entry in caplog_text


@pytest.fixture(scope="function")
def setup__walk_dir(fs):
    equivalency_graph = generate_equivalency_graph([".wav", ".mp3", ".wav", ".ogg"])
    file_info_factory = EquivalentFileFinder._FileInformationWithSuffixEquivalence.get_factory(equivalency_graph)

    root = pathlib.Path("foo")
    sub_folder = root / "2"

    folders = [
        root,
        sub_folder
    ]

    expected_dupes = [
        root / "2016 Car Bash Promo.mp3",
        root / "2016 Car Bash Promo.wav",
        sub_folder / "OnAir-1-2017-05-30_01-00-00-017.wav",
        sub_folder / "OnAir-1-2017-05-30_01-00-00-017.mp3",
        sub_folder / "OnAir-1-2017-05-30_01-45-00-195.mp3",
        sub_folder / "OnAir-1-2017-05-30_01-45-00-195.ogg"
    ]

    file_tree = [
        *expected_dupes,
        root / "02 Lean In When I Suffer.pk",
        root / "02 Lean In When I Suffer.pkf",
        root / "30 Promo SBJ VO.sfk",
        root / "35 hiss.sfk",
        root / "Gene - I appreciate that.mp3.sfap0",
        root / "OnAir-1-2017-05-30_00-00-00-037.wav",
        root / "OnAir-1-2017-05-30_00-15-00-144.wav",
        root / "OnAir-1-2017-05-30_00-30-00-157.wav",
        root / "OnAir-1-2017-05-30_00-45-00-208.wav",
        sub_folder / "OnAir-1-2017-05-30_01-15-00-067.wav",
        sub_folder / "OnAir-1-2017-05-30_01-30-00-127.wav",
    ]

    for item in folders:
        fs.create_dir(item)

    for file in file_tree:
        fs.create_file(file)

    equivalent_files = []

    EquivalentFileFinder._walk_dir(
        this_path=root,
        equivalent_files=equivalent_files,
        file_info_factory=file_info_factory,
    )

    yield expected_dupes, equivalent_files


def test__walk_dir_correct_equivs(setup__walk_dir):
    expected_dupes, equivalent_files = setup__walk_dir

    for exp_dup in expected_dupes:
        assert exp_dup in equivalent_files

    for equiv_file in equivalent_files:
        assert equiv_file in expected_dupes


@pytest.fixture(scope="function", params=[True, False])
def setup__find_equivalent_files(mocker, request):
    rename = request.param

    def mock_walk_dir_function(this_path, equivalent_files, file_info_factory):
        equivalent_files.append("Foo")
        equivalent_files.append("Bar")
        equivalent_files.append("Zulu")

    mock_walk_dir = mocker.patch(
        "wmul_file_manager.EquivalentFileFinder._walk_dir",
        mocker.Mock(side_effect=mock_walk_dir_function)
    )

    mock_rename_equivalent_files = mocker.patch("wmul_file_manager.EquivalentFileFinder._rename_equivalent_files")

    mock_folder_path = "mock_folder_path"
    mock_file_info_factory = "mock_file_info_factory"

    result_equivalent_files = EquivalentFileFinder._find_equivalent_files(
        folder_path=mock_folder_path,
        file_info_factory=mock_file_info_factory,
        rename=rename
    )

    yield mock_walk_dir, mock_rename_equivalent_files, mock_folder_path, mock_file_info_factory, \
          result_equivalent_files, rename


def test__find_equivalent_files_walk_dir_called_correctly(setup__find_equivalent_files):
    mock_walk_dir, _, mock_folder_path, mock_file_info_factory, _, _ = setup__find_equivalent_files

    mock_walk_dir.assert_called_once()
    call_args, _ = mock_walk_dir.call_args
    call_folder_path, call_equivalent_files, call_file_info_factory = call_args

    assert call_folder_path == mock_folder_path
    assert isinstance(call_equivalent_files, list)
    assert call_file_info_factory == mock_file_info_factory


def test__find_equivalent_files_list_sorted(setup__find_equivalent_files):
    _, _, _, _, result_equivalent_files, _ = setup__find_equivalent_files

    expected_list = ["Bar", "Foo", "Zulu"]
    assert expected_list == result_equivalent_files


def test__find_equivalent_files_rename_equivalent_files_called_correctly(setup__find_equivalent_files):
    _, mock_rename_equivalent_files, _, _, result_equivalent_files, rename = setup__find_equivalent_files

    if rename:
        mock_rename_equivalent_files.assert_called_once_with(result_equivalent_files)
    else:
        mock_rename_equivalent_files.assert_not_called()


def test__print_equivalent_files(mocker):
    mock_result_writer_contents = []

    def mock_result_writer(data):
        mock_result_writer_contents.append(data)

    def mock_object_cleaner(item):
        return item
    mocker.patch("wmul_file_manager.utilities.FileNamePrinter.object_cleaner", mock_object_cleaner)

    results = [
        ["File1.doc", "File1.docx"],
        ["File2.wav", "File2.mp3"],
        ["File3.wav", "File3.ogg"]
    ]

    expected_writer_contents = [
        "===========================================================================================",
        "                           ********Equivalent File Finder********                          ",
        "File1.doc",
        "File1.docx",
        "##########################################",
        "File2.wav",
        "File2.mp3",
        "##########################################",
        "File3.wav",
        "File3.ogg",
        "##########################################",
    ]

    EquivalentFileFinder._print_equivalent_files(mock_result_writer, results)

    assert mock_result_writer_contents == expected_writer_contents


@pytest.fixture(scope="function")
def setup_run_script(mocker):
    mock_source_paths = ["mock_source_1", "mock_source_2"]
    mock_equivalent_suffixes_list = "mock_equivalent_suffixes_list"
    mock_rename_flag = "mock_rename_flag"
    mock_output_path = "mock_output_path"

    arguments = mocker.Mock(
        source_paths=mock_source_paths,
        equivalent_suffixes_list=mock_equivalent_suffixes_list,
        rename_flag=mock_rename_flag,
        output_path=mock_output_path
    )

    mock_equivalency_graph = "mock_equivalency_graph"

    def mock_generate_equivalency_graph_function(equiv_suffixes):
        return mock_equivalency_graph

    mock_generate_equivalency_graph = mocker.patch(
        "wmul_file_manager.EquivalentFileFinder.generate_equivalency_graph",
        mocker.Mock(side_effect=mock_generate_equivalency_graph_function)
    )

    mock_file_info_factory = "mock_file_info_factory"

    def mock_get_factory_function(equivalency_graph):
        return mock_file_info_factory

    mock_get_factory = mocker.patch(
        "wmul_file_manager.EquivalentFileFinder._FileInformationWithSuffixEquivalence.get_factory",
        mocker.Mock(side_effect=mock_get_factory_function)
    )

    def mock_find_equivalent_files_function(source_path, file_info_factory, rename_flag):
        if source_path == "mock_source_1":
            return ["File1.doc", "File1.docx"]
        else:
            return ["File2.wav", "File2.mp3"]

    mock_find_equivalent_files = mocker.patch(
        "wmul_file_manager.EquivalentFileFinder._find_equivalent_files",
        mocker.Mock(side_effect=mock_find_equivalent_files_function)
    )

    mock_writer = mocker.Mock()
    @contextlib.contextmanager
    def mock_writer_function(file_name):
        yield mock_writer

    mock_get_writer = mocker.patch(
        "wmul_file_manager.EquivalentFileFinder.get_writer",
        mocker.Mock(side_effect=mock_writer_function)
    )
    mock_print_equivalent_files = mocker.patch("wmul_file_manager.EquivalentFileFinder._print_equivalent_files")

    EquivalentFileFinder.run_script(arguments=arguments)

    yield mock_source_paths, mock_equivalent_suffixes_list, mock_rename_flag, mock_output_path, \
          mock_equivalency_graph, mock_generate_equivalency_graph, mock_file_info_factory, mock_get_factory, \
          mock_find_equivalent_files, mock_writer, mock_get_writer, mock_print_equivalent_files


def test_run_script_generate_equivalency_graph_called_correctly(setup_run_script):
    _, mock_equivalent_suffixes_list, _, _,  _, mock_generate_equivalency_graph, _, _, _, _, _, _ = setup_run_script
    mock_generate_equivalency_graph.assert_called_once_with(mock_equivalent_suffixes_list)


def test_run_script_file_info_get_factory_called_correctly(setup_run_script):
    _, _, _, _,  mock_equivalency_graph, _, _, mock_get_factory, _, _, _, _ = setup_run_script
    mock_get_factory.assert_called_once_with(mock_equivalency_graph)


def test_run_script_find_equivalent_files_called_correctly(setup_run_script, mocker):
    mock_source_paths, _, mock_rename_flag, _,  _, _, mock_file_info_factory, _, mock_find_equivalent_files, \
        _, _, _ = setup_run_script

    expected_calls = []
    for source_path in mock_source_paths:
        expected_calls.append(mocker.call(source_path, mock_file_info_factory, mock_rename_flag))

    mock_find_equivalent_files.assert_has_calls(expected_calls, any_order=True)
    assert mock_find_equivalent_files.call_count == len(mock_source_paths)


def test_run_script_get_writer_called_correctly(setup_run_script):
    _, _, _, mock_output_path, _, _, _, _, _, _, mock_get_writer, _ = setup_run_script
    mock_get_writer.assert_called_once_with(file_name=mock_output_path)


def test_run_script__print_equivalent_files_called_correctly(setup_run_script):
    _, _, _, _,  _, _, _, _, _, mock_writer, _, mock_print_equivalent_files = setup_run_script

    expected_results = [
        ["File1.doc", "File1.docx"],
        ["File2.wav", "File2.mp3"]
    ]

    mock_print_equivalent_files.assert_called_once_with(mock_writer, expected_results)
