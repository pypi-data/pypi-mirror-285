"""
@Author = 'Mike Stanley'

============ Change Log ============
4/24/2018 = Created.

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
import pytest
import random
import shutil
import time

from pathlib import Path
from wmul_file_manager import BulkCopier


def test_try_copy_normal(tmpdir):
    tmpfile1 = tmpdir.join("tmpfile1.txt")
    tmpfile1.write_binary(bytearray(random.randint(0, 255) for i in range(100)))

    tmpfile2 = tmpdir.join("tmpfile2.txt")

    assert not tmpfile2.check()

    BulkCopier._try_copy(tmpfile1, tmpfile2)

    assert tmpfile2.check()

    tmpfile1_contents = tmpfile1.read_binary()
    tmpfile2_contents = tmpfile2.read_binary()

    assert tmpfile1_contents == tmpfile2_contents


def test_try_copy_ioerror(monkeypatch, capsys):
    import wmul_logger
    import logging
    wmul_logger.setup_logger(log_level=logging.DEBUG)

    def mock_copy2(src, dst):
        raise IOError("Mock IO Error")
    monkeypatch.setattr(BulkCopier.shutil, 'copy2', mock_copy2)

    BulkCopier._try_copy("foo", "bar")

    stdout, err = capsys.readouterr()

    assert "Mock IO Error" in stdout


def test_try_copy_other_exception(monkeypatch, capsys):
    def mock_copy2(src, dst):
        raise Exception("Mock Other Exception")
    monkeypatch.setattr(BulkCopier.shutil, 'copy2', mock_copy2)

    with pytest.raises(Exception):
        BulkCopier._try_copy("foo", "bar")


def test_synchronize_file_dst_doesnt_exist(tmpdir, mocker):
    mock_try_copy = mocker.patch("wmul_file_manager.BulkCopier._try_copy")
    src_name = "foo.txt"
    src_file = tmpdir.join(src_name)
    dst_path = tmpdir.join(r"\temp2")
    dst_file = dst_path.join(src_name)

    random_bytes = bytearray(random.randint(0, 255) for i in range(100))
    src_file.write_binary(random_bytes)

    assert src_file.check()
    assert not dst_file.check()

    BulkCopier._synchronize_file(source_item=Path(src_file), destination_path=Path(dst_path), force_copy=False)
    mock_try_copy.assert_called_once_with(src_file, dst_file)


def test_synchronize_file_already_exists_force_copy(test_setup_synchronize_file):
    src_file, dst_file, dst_path, random_bytes1, random_bytes2, mock_try_copy = test_setup_synchronize_file

    src_file.write_binary(random_bytes1)

    assert src_file.check()
    assert not dst_file.check()

    shutil.copy2(src_file, dst_file)
    assert dst_file.check()

    BulkCopier._synchronize_file(source_item=Path(src_file), destination_path=Path(dst_path), force_copy=True)
    mock_try_copy.assert_called_once_with(src_file, dst_file)


@pytest.fixture(scope="function")
def test_setup_synchronize_file(tmpdir, mocker):
    mock_try_copy = mocker.patch("wmul_file_manager.BulkCopier._try_copy")
    src_name = "foo.txt"
    src_file = tmpdir.join(src_name)
    dst_path = tmpdir.join(r"\temp2")
    dst_path.ensure(dir=True)
    dst_file = dst_path.join(src_name)

    random_bytes1 = bytearray(random.randint(0, 255) for i in range(100))
    random_bytes2 = random_bytes1
    while random_bytes2 == random_bytes1:
        random_bytes2 = bytearray(random.randint(0, 255) for i in range(100))

    yield src_file, dst_file, dst_path, random_bytes1, random_bytes2, mock_try_copy


@pytest.mark.skip
@pytest.mark.LongRun
def test_synchronize_file_already_exists_source_newer(test_setup_synchronize_file):
    src_file, dst_file, dst_path, random_bytes1, random_bytes2, mock_try_copy = test_setup_synchronize_file

    dst_file.write_binary(random_bytes2)
    time.sleep(70)
    src_file.write_binary(random_bytes1)

    assert src_file.check()
    assert dst_file.check()

    BulkCopier._synchronize_file(source_item=Path(src_file), destination_path=Path(dst_path), force_copy=False)

    mock_try_copy.assert_called_once_with(src_file, dst_file)


@pytest.mark.skip
@pytest.mark.LongRun
def test_synchronize_file_already_exists_destination_newer(test_setup_synchronize_file):
    src_file, dst_file, dst_path, random_bytes1, random_bytes2, mock_try_copy = test_setup_synchronize_file

    src_file.write_binary(random_bytes1)
    time.sleep(70)
    dst_file.write_binary(random_bytes2)

    assert src_file.check()
    assert dst_file.check()

    BulkCopier._synchronize_file(source_item=Path(src_file), destination_path=Path(dst_path), force_copy=False)

    mock_try_copy.assert_not_called()


def test_synchronize_paths_two_files(tmpdir, mocker):
    mock_synchronize_file = mocker.patch("wmul_file_manager.BulkCopier._synchronize_file")

    src_dir = tmpdir.join("temp_src")
    src_dir.ensure(dir=True)

    file1 = src_dir.join("temp1.txt")
    file2 = src_dir.join("temp2.txt")
    file1.write_binary(bytearray(random.randint(0, 255) for i in range(100)))
    file2.write_binary(bytearray(random.randint(0, 255) for i in range(100)))

    dst_dir = tmpdir.join("temp_dst")

    assert not dst_dir.check()

    src_dir = Path(src_dir)
    file1 = Path(file1)
    file2 = Path(file2)
    dst_dir = Path(dst_dir)

    BulkCopier._synchronize_directories(
        source_path=src_dir,
        destination_path=dst_dir,
        exclude_exts=[],
        ignore_folders=[],
        force_copy=False
    )

    mock_synchronize_file.assert_any_call(file1, dst_dir, False)
    mock_synchronize_file.assert_any_call(file2, dst_dir, False)


@pytest.fixture(scope="function")
def setup__synchronize_directories(tmpdir, mocker):
    mock_synchronize_file = mocker.patch("wmul_file_manager.BulkCopier._synchronize_file")

    src_dir = tmpdir.join("temp_src")
    src_dir.ensure(dir=True)

    dir1 = src_dir.join("sub_dir1")
    dir1.ensure(dir=True)
    dir2 = src_dir.join("sub_dir2")
    dir2.ensure(dir=True)

    file0 = src_dir.join("temp0.txt")
    file1 = dir1.join("temp1.txt")
    file2 = dir1.join("temp2.DAT")
    file3 = dir2.join("temp3.txt")
    file0.write_binary(bytearray(random.randint(0, 255) for i in range(100)))
    file1.write_binary(bytearray(random.randint(0, 255) for i in range(100)))
    file2.write_binary(bytearray(random.randint(0, 255) for i in range(100)))
    file3.write_binary(bytearray(random.randint(0, 255) for i in range(100)))

    dst_dir = tmpdir.join("temp_dst")

    src_dir = Path(src_dir)
    dir1 = Path(dir1)
    dir2 = Path(dir2)
    dst_dir = Path(dst_dir)
    file0 = Path(file0)
    file1 = Path(file1)
    file2 = Path(file2)
    file3 = Path(file3)

    yield src_dir, dst_dir, dir1, dir2, file0, file1, file2, file3, mock_synchronize_file


def test_synchronize_paths_no_ignore_no_exclude_no_force(setup__synchronize_directories, mocker):
    src_dir, dst_dir, dir1, dir2, file0, file1, file2, file3, mock_synchronize_file = setup__synchronize_directories
    assert not dst_dir.exists()

    BulkCopier._synchronize_directories(
        source_path=src_dir,
        destination_path=dst_dir,
        exclude_exts=[],
        ignore_folders=[],
        force_copy=False
    )

    expected_synchronize_calls = [
        mocker.call(file0, dst_dir, False),
        mocker.call(file1, dst_dir / "sub_dir1", False),
        mocker.call(file2, dst_dir / "sub_dir1", False),
        mocker.call(file3, dst_dir / "sub_dir2", False),
    ]

    mock_synchronize_file.assert_has_calls(expected_synchronize_calls, any_order=True)
    assert mock_synchronize_file.call_count == len(expected_synchronize_calls)


def test_synchronize_paths_suffixes_excluded(setup__synchronize_directories, mocker):
    src_dir, dst_dir, dir1, dir2, file0, file1, file2, file3, mock_synchronize_file = setup__synchronize_directories
    assert not dst_dir.exists()

    BulkCopier._synchronize_directories(
        source_path=src_dir,
        destination_path=dst_dir,
        exclude_exts=[".dat"],
        ignore_folders=[],
        force_copy=False
    )

    expected_synchronize_calls = [
        mocker.call(file0, dst_dir, False),
        mocker.call(file1, dst_dir / "sub_dir1", False),
        mocker.call(file3, dst_dir / "sub_dir2", False),
    ]

    mock_synchronize_file.assert_has_calls(expected_synchronize_calls, any_order=True)
    assert mock_synchronize_file.call_count == len(expected_synchronize_calls)


def test_synchronize_paths_some_dirs_ignored(setup__synchronize_directories, mocker):
    src_dir, dst_dir, dir1, dir2, file0, file1, file2, file3, mock_synchronize_file = setup__synchronize_directories
    assert not dst_dir.exists()

    BulkCopier._synchronize_directories(
        source_path=src_dir,
        destination_path=dst_dir,
        exclude_exts=[],
        ignore_folders=[dir2],
        force_copy=False
    )

    expected_synchronize_calls = [
        mocker.call(file0, dst_dir, False),
        mocker.call(file1, dst_dir / "sub_dir1", False),
        mocker.call(file2, dst_dir / "sub_dir1", False),
    ]

    mock_synchronize_file.assert_has_calls(expected_synchronize_calls, any_order=True)
    assert mock_synchronize_file.call_count == len(expected_synchronize_calls)


@pytest.fixture(scope="function")
def setup_has_matching_source_file(tmpdir):
    src_dir = tmpdir.join("temp1")
    src_dir.ensure(dir=True)
    dst_dir = tmpdir.join("temp2")
    dst_dir.ensure(dir=True)

    random_bytes = bytearray(random.randint(0, 255) for i in range(100))

    dst_file = dst_dir.join("test.txt")
    dst_file.write_binary(random_bytes)
    dst_file = Path(dst_file)

    yield src_dir, dst_dir, dst_file, random_bytes


def test_has_matching_source_file_it_does(setup_has_matching_source_file):
    src_dir, dst_dir, dst_file, random_bytes = setup_has_matching_source_file

    src_file = src_dir.join("test.txt")
    src_file.write_binary(random_bytes)

    src_dir = Path(src_dir)

    assert BulkCopier._has_matching_source_file(dst_file, src_dir)


def test_has_matching_source_file_it_does_not(setup_has_matching_source_file):
    src_dir, dst_dir, dst_file, random_bytes = setup_has_matching_source_file

    src_dir = Path(src_dir)

    assert not BulkCopier._has_matching_source_file(dst_file, src_dir)


@pytest.fixture(scope="function")
def setup_delete_old_files_no_subdir(tmpdir):
    dir1 = tmpdir.join("temp1")
    dir1.ensure(dir=True)
    dir2 = tmpdir.join("temp2")
    dir2.ensure(dir=True)

    file1 = dir1.join("test1.txt")
    file1.write_binary(bytearray(random.randint(0, 255) for i in range(100)))

    file2 = dir1.join("test2.dat")
    file2.write_binary(bytearray(random.randint(0, 255) for i in range(100)))

    yield dir1, dir2, file1, file2


def test_delete_old_files_two_files(setup_delete_old_files_no_subdir, monkeypatch):
    dir1, dir2, file1, file2 = setup_delete_old_files_no_subdir

    def mock_has_matching_source_file(destination_item, source_path):
        return False
    monkeypatch.setattr(BulkCopier, '_has_matching_source_file', mock_has_matching_source_file)

    BulkCopier._delete_old_files(Path(dir2), Path(dir1), [])

    assert not file1.check()
    assert not file2.check()


def test_delete_old_files_has_matching_source(setup_delete_old_files_no_subdir, monkeypatch):
    dir1, dir2, file1, file2 = setup_delete_old_files_no_subdir
    file1_path = Path(file1)

    def mock_has_matching_source_file(destination_item, source_path):
        return destination_item == file1_path
    monkeypatch.setattr(BulkCopier, '_has_matching_source_file', mock_has_matching_source_file)

    BulkCopier._delete_old_files(Path(dir2), Path(dir1), [])

    assert file1.check()
    assert not file2.check()


@pytest.fixture(scope="function")
def setup_delete_old_files_subdir(tmpdir, monkeypatch):
    def mock_has_matching_source_file(destination_item, source_path):
        return False
    monkeypatch.setattr(BulkCopier, '_has_matching_source_file', mock_has_matching_source_file)

    dir1 = tmpdir.join("temp1")
    dir1.ensure(dir=True)
    subdir1 = dir1.join("sub_dir")
    subdir1.ensure(dir=True)
    dir2 = tmpdir.join("temp2")
    dir2.ensure(dir=True)

    file1 = subdir1.join("test1.txt")
    file1.write_binary(bytearray(random.randint(0, 255) for i in range(100)))

    file2 = subdir1.join("test2.dat")
    file2.write_binary(bytearray(random.randint(0, 255) for i in range(100)))

    yield dir1, dir2, file1, file2


def test_delete_old_files_subdir(setup_delete_old_files_subdir):
    dir1, dir2, file1, file2 = setup_delete_old_files_subdir

    BulkCopier._delete_old_files(Path(dir2), Path(dir1), [])

    assert not file1.check()
    assert not file2.check()


def test_delete_old_files_exluded_exts(setup_delete_old_files_subdir):
    dir1, dir2, file1, file2 = setup_delete_old_files_subdir

    BulkCopier._delete_old_files(Path(dir2), Path(dir1), [".dat"])

    assert not file1.check()
    assert file2.check()


@pytest.fixture(scope="function")
def setup_run_script(tmpdir, mocker):
    mock_synchronize_paths = mocker.patch("wmul_file_manager.BulkCopier._synchronize_directories")
    mock_delete_old_files = mocker.patch("wmul_file_manager.BulkCopier._delete_old_files")

    src_path = tmpdir.join("src_path")
    src_path.ensure(dir=True)

    dir1_src = src_path.join("temp1")
    dir1_src.ensure(dir=True)
    dir1_src = Path(dir1_src)
    dir2_src = src_path.join("temp2")
    dir2_src.ensure(dir=True)
    dir2_src = Path(dir2_src)

    dst_path = tmpdir.join("dst_path")
    dst_path.ensure(dir=True)
    dst_path = Path(dst_path)

    dir1_dst = dst_path / dir1_src.name
    dir2_dst = dst_path / dir2_src.name

    source_paths = [dir1_src, dir2_src]
    destination_path = dst_path

    yield mock_synchronize_paths, mock_delete_old_files, source_paths, destination_path, dir1_src, \
          dir1_dst, dir2_src, dir2_dst


def test_run_script_delete_old_false(setup_run_script):
    mock_synchronize_paths, mock_delete_old_files, source_paths, destination_path, dir1_src, dir1_dst, \
    dir2_src, dir2_dst = setup_run_script

    exclude_suffixes_list = []
    ignore_paths = []
    force_copy_flag = False
    delete_old_files_flag = False

    bca = BulkCopier.BulkCopierArguments(
        source_directories=source_paths,
        destination_directory=destination_path,
        exclude_suffixes_list=exclude_suffixes_list,
        ignore_directories=ignore_paths,
        force_copy_flag=force_copy_flag,
        delete_old_files_flag=delete_old_files_flag
    )

    BulkCopier.run_script(bca)

    mock_synchronize_paths.assert_any_call(dir1_src, dir1_dst, exclude_suffixes_list, ignore_paths, force_copy_flag)
    mock_synchronize_paths.assert_any_call(dir2_src, dir2_dst, exclude_suffixes_list, ignore_paths, force_copy_flag)
    mock_delete_old_files.assert_not_called()


def test_run_script_delete_old_true(setup_run_script):
    mock_synchronize_paths, mock_delete_old_files, source_paths, destination_path, dir1_src, dir1_dst, \
    dir2_src, dir2_dst = setup_run_script

    exclude_suffixes_list = []
    ignore_paths = []
    force_copy_flag = False
    delete_old_files_flag = True

    bca = BulkCopier.BulkCopierArguments(
        source_directories=source_paths,
        destination_directory=destination_path,
        exclude_suffixes_list=exclude_suffixes_list,
        ignore_directories=ignore_paths,
        force_copy_flag=force_copy_flag,
        delete_old_files_flag=delete_old_files_flag
    )

    BulkCopier.run_script(bca)

    mock_synchronize_paths.assert_any_call(dir1_src, dir1_dst, exclude_suffixes_list, ignore_paths, force_copy_flag)
    mock_synchronize_paths.assert_any_call(dir2_src, dir2_dst, exclude_suffixes_list, ignore_paths, force_copy_flag)
    mock_delete_old_files.assert_any_call(dir1_src, dir1_dst, exclude_suffixes_list)
    mock_delete_old_files.assert_any_call(dir2_src, dir2_dst, exclude_suffixes_list)





