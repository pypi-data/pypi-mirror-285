"""
@Author = 'Mike Stanley'

============ Change Log ============
2018-May-08 = Created.

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
from wmul_file_manager import DeleteJunkFiles


def test__file_is_junk__junk_suffix():
    mock_file = pathlib.Path("foo.sfk")
    junk_extensions = [".sfk", ".sfap0"]
    junk_names = ["thumbs.db"]

    assert DeleteJunkFiles._file_is_junk(mock_file, junk_extensions, junk_names)


def test__file_is_junk__junk_suffix_mixed_case():
    mock_file = pathlib.Path("foo.sFk")
    junk_extensions = [".sfk", ".sfap0"]
    junk_names = ["thumbs.db"]

    assert DeleteJunkFiles._file_is_junk(mock_file, junk_extensions, junk_names)


def test__file_is_junk__junk_name():
    mock_file = pathlib.Path("Thumbs.db")
    junk_extensions = [".sfk", ".sfap0"]
    junk_names = ["thumbs.db"]

    assert DeleteJunkFiles._file_is_junk(mock_file, junk_extensions, junk_names)


def test__file_is_junk__junk_name_mixed_case():
    mock_file = pathlib.Path("ThuMBs.db")
    junk_extensions = [".sfk", ".sfap0"]
    junk_names = ["thumbs.db"]

    assert DeleteJunkFiles._file_is_junk(mock_file, junk_extensions, junk_names)


def test__file_is_junk__good_file():
    mock_file = pathlib.Path("foo.wav")
    junk_extensions = [".sfk", ".sfap0"]
    junk_names = ["thumbs.db"]

    assert not DeleteJunkFiles._file_is_junk(mock_file, junk_extensions, junk_names)


def test__file_is_junk__empty_extensions():
    mock_file = pathlib.Path('foo.wav')
    junk_extensions = []
    junk_names = ["thumbs.db"]

    assert not DeleteJunkFiles._file_is_junk(mock_file, junk_extensions, junk_names)


def test__file_is_junk__empty_names():
    mock_file = pathlib.Path('foo.wav')
    junk_extensions = [".sfk", ".sfap0"]
    junk_names = []

    assert not DeleteJunkFiles._file_is_junk(mock_file, junk_extensions, junk_names)


def test__file_is_junk__empty_names_and_suffixes():
    mock_file = pathlib.Path('foo.wav')
    junk_extensions = []
    junk_names = []

    assert not DeleteJunkFiles._file_is_junk(mock_file, junk_extensions, junk_names)



def test__delete_this_junk_file_success(tmpdir):
    junk_file = tmpdir.join("foo.txt")
    junk_file.write_binary(bytearray(random.randint(0, 255) for i in range(100)))
    file_size = DeleteJunkFiles._delete_this_junk_file(pathlib.Path(junk_file))
    assert not junk_file.check()
    assert file_size == 100


def test__delete_this_junk_file_failure(tmpdir, caplog):
    junk_file = tmpdir.join("foo.txt")
    file_size = DeleteJunkFiles._delete_this_junk_file(pathlib.Path(junk_file))
    assert not junk_file.check()
    assert file_size == 0
    assert "BaseException: " in caplog.text


@pytest.fixture(scope="function")
def setup__search_directory(mocker, fs):
    mock_delete_this_junk_file = mocker.patch(
        "wmul_file_manager.DeleteJunkFiles._delete_this_junk_file",
        mocker.Mock(return_value=100)
    )

    root_folder = pathlib.Path(r"test")
    directories = [
        root_folder,
        pathlib.Path(r"test\2")
    ]
    expected_good_files = [
        pathlib.Path(r"test\2016 Car Bash Promo.wav"),
        pathlib.Path(r"test\OnAir-1-2017-05-30_00-00-00-037.wav"),
        pathlib.Path(r"test\OnAir-1-2017-05-30_00-15-00-144.Wav"),
        pathlib.Path(r"test\OnAir-1-2017-05-30_00-30-00-157.waV"),
        pathlib.Path(r"test\OnAir-1-2017-05-30_00-45-00-208.wav"),
        pathlib.Path(r"test\2\OnAir-1-2017-05-30_01-00-00-017.wav"),
        pathlib.Path(r"test\2\OnAir-1-2017-05-30_01-15-00-067.wav"),
        pathlib.Path(r"test\2\OnAir-1-2017-05-30_01-30-00-127.wav"),
        pathlib.Path(r"test\2\OnAir-1-2017-05-30_01-45-00-195.wav"),
        pathlib.Path(r"test\2016 Car Bash Promo.mp3"),
        pathlib.Path(r"test\OnAir-1-2017-05-30_00-00-00-037.Mp3"),
    ]
    expected_junk_files = [
        pathlib.Path(r"test\30 Promo SBJ VO.sfk"),
        pathlib.Path(r"test\35 hiss.sfk"),
        pathlib.Path(r"test\2\foobar.sfap0"),
        pathlib.Path(r"test\2\OnAir-1-2017-05-30_01-15-00-067.SfK"),
    ]
    all_expected_files = [
        *expected_good_files,
        *expected_junk_files
    ]

    for item in directories:
        fs.create_dir(item)

    for item in all_expected_files:
        fs.create_file(item)

    junk_extensions = [".sfk", ".sfap0"]
    junk_names = ["thumbs.db", ".ds_store"]
    junk_files_list = []

    received_junk_size = DeleteJunkFiles._search_directory(root_folder, junk_extensions, junk_names, junk_files_list)

    return locals()


def test__search_directory_mock_delete_called_correctly(setup__search_directory):
    expected_junk_files = setup__search_directory["expected_junk_files"]
    mock_delete_this_junk_file = setup__search_directory["mock_delete_this_junk_file"]

    for junk_file in expected_junk_files:
        mock_delete_this_junk_file.assert_any_call(junk_file)

    assert mock_delete_this_junk_file.call_count == len(expected_junk_files)


def test__search_directory_junk_size_correct(setup__search_directory):
    expected_junk_files = setup__search_directory["expected_junk_files"]
    received_junk_size = setup__search_directory["received_junk_size"]
    assert received_junk_size == (len(expected_junk_files) * 100)


def test__search_directory_returned_junk_files_list_correct(setup__search_directory):
    expected_junk_files = setup__search_directory["expected_junk_files"]
    junk_files_list = setup__search_directory["junk_files_list"]
    assert len(expected_junk_files) == len(junk_files_list)
    for item in expected_junk_files:
        assert item in junk_files_list


@pytest.fixture(scope="function")
def setup__delete_junk_files(mocker):
    mock_search_directory = mocker.patch(
        "wmul_file_manager.DeleteJunkFiles._search_directory",
        mocker.Mock(return_value=100)
    )

    root_folder = "mock_root_folder"
    junk_extensions = "mock_junk_extensions"
    junk_names = "mock_junk_names"

    yield mock_search_directory, root_folder, junk_extensions, junk_names


def test__delete_junk_files_with_junk_extensions(setup__delete_junk_files):
    mock_search_directory, root_folder, junk_extensions, junk_names = setup__delete_junk_files
    junk_files, junk_size = DeleteJunkFiles._delete_junk_files(root_folder, junk_extensions, junk_names)
    mock_search_directory.assert_called_once_with(root_folder, junk_extensions, junk_names, junk_files)
    assert junk_size == 100


def test__delete_junk_files_with_default_junk_extensions(setup__delete_junk_files):
    mock_search_directory, root_folder, junk_extensions, junk_names = setup__delete_junk_files
    junk_files, junk_size = DeleteJunkFiles._delete_junk_files(root_folder)
    default_junk_extensions = ['.pk', '.pkf', '.sfk', '.tmp', '.sfap0']
    default_junk_names = ["Thumbs.db", ".DS_Store"]
    mock_search_directory.assert_called_once_with(root_folder, default_junk_extensions, default_junk_names, junk_files)
    assert junk_size == 100


def test__write_results(mocker):
    mock_result_writer_contents = []

    def mock_result_writer(data):
        mock_result_writer_contents.append(data)

    def mock_object_cleaner(item):
        return item
    mocker.patch("wmul_file_manager.utilities.FileNamePrinter.object_cleaner", mock_object_cleaner)

    results = [
        (["File1.txt", "File2.txt", "File3.txt"], 300),
        (["File4.txt", "File5.txt", "File6.txt", "File7.txt"], 400)
    ]

    expected_writer_contents = [
        "===========================================================================================",
        "                             ********Delete Junk Files********                             ",
        "File1.txt",
        "File2.txt",
        "File3.txt",
        "Total Size of Deleted Junk Files: 300",
        "##########################################",
        "File4.txt",
        "File5.txt",
        "File6.txt",
        "File7.txt",
        "Total Size of Deleted Junk Files: 400",
        "##########################################"
    ]

    DeleteJunkFiles._write_results(mock_result_writer, results)

    assert mock_result_writer_contents == expected_writer_contents


@pytest.fixture(scope="function")
def setup__run_script(mocker):
    mock_source_paths = ["mock_source_1", "mock_source_2"]
    mock_junk_suffixes = "mock_junk_suffixes"
    mock_junk_names = "mock_junk_names"
    mock_output_path = "mock_output_path"

    arguments = mocker.Mock(source_paths=mock_source_paths, junk_suffixes=mock_junk_suffixes,
                            junk_names=mock_junk_names, output_path=mock_output_path)

    def mock_delete_junk_files_function(source_path, junk_suffixes, junk_names):
        if source_path == "mock_source_1":
            return ["File1.txt", "File2.txt", "File3.txt"], 300
        else:
            return ["File4.txt", "File5.txt", "File6.txt", "File7.txt"], 400

    mock_delete_junk_files = mocker.patch(
        "wmul_file_manager.DeleteJunkFiles._delete_junk_files",
        mocker.Mock(side_effect=mock_delete_junk_files_function)
    )

    mock_writer = mocker.Mock()
    @contextlib.contextmanager
    def mock_writer_function(op):
        yield mock_writer

    mock_get_writer = mocker.patch(
        "wmul_file_manager.utilities.writer.get_writer",
        mocker.Mock(side_effect=mock_writer_function)
    )
    mock_write_results = mocker.patch("wmul_file_manager.DeleteJunkFiles._write_results")

    DeleteJunkFiles.run_script(arguments=arguments)

    return locals()


def test__run_script_delete_junk_files_called_correctly(setup__run_script, mocker):
    mock_junk_suffixes = setup__run_script["mock_junk_suffixes"]
    mock_junk_names = setup__run_script["mock_junk_names"]
    mock_source_paths = setup__run_script["mock_source_paths"]
    mock_delete_junk_files = setup__run_script["mock_delete_junk_files"]

    expected_calls = [mocker.call(sp, mock_junk_suffixes, mock_junk_names) for sp in mock_source_paths]
    mock_delete_junk_files.assert_has_calls(expected_calls)
    assert mock_delete_junk_files.call_count == len(mock_source_paths)


def test__run_script_get_writer_called_correctly(setup__run_script):
    mock_get_writer = setup__run_script["mock_get_writer"]
    mock_output_path = setup__run_script["mock_output_path"]

    mock_get_writer.assert_called_once_with(mock_output_path)


def test__run_script_write_results_called_correctly(setup__run_script):
    mock_write_results = setup__run_script["mock_write_results"]
    mock_writer = setup__run_script["mock_writer"]

    expected_results = [
        (["File1.txt", "File2.txt", "File3.txt"], 300),
        (["File4.txt", "File5.txt", "File6.txt", "File7.txt"], 400)
    ]

    mock_write_results.assert_called_once_with(mock_writer, expected_results)












