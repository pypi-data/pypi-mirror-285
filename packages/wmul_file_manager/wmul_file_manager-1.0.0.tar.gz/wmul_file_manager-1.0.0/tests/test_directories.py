"""
Author: Michael Stanley

============ Change Log ============
2018-May-01 = Import from Titanium_Motnicello.

              Extensive re-write to use pytest.

2015-Sep-11 = Created.

============ License ============
The MIT License (MIT)

Copyright (c) 2015 Michael Stanley

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
from pathlib import Path
from wmul_file_manager.utilities import directories


@pytest.fixture(scope="function")
def directories_setup(tmpdir):
    src = tmpdir.join("src")
    src.ensure(dir=True)

    src_path = Path(src)
    yield src, src_path


@pytest.fixture(scope="function")
def directories_setup_with_files(directories_setup):
    src, src_path = directories_setup

    file1 = src.join("file1.txt")
    file1.write_binary(bytearray(random.randint(0, 255) for i in range(100)))

    file2 = src.join("file2.txt")
    file2.write_binary(bytearray(random.randint(0, 255) for i in range(100)))

    yield src, src_path, file1, file2


def test_directory_is_empty__empty_directory(directories_setup):
    src, src_path = directories_setup
    assert directories.directory_is_empty(src_path)


def test_directory_is_empty__not_empty_directory(directories_setup_with_files):
    src, src_path, file1, file2 = directories_setup_with_files
    assert not directories.directory_is_empty(src_path)


def test_purge_directory_contents_an_empty_directory(directories_setup):
    src, src_path = directories_setup

    directories.purge_directory_contents(src_path)

    assert src_path.exists()
    assert directories.directory_is_empty(src_path)


def test_purge_directory_contents_can_empty_a_directory_with_files(directories_setup_with_files):
    src, src_path, file1, file2 = directories_setup_with_files

    assert not directories.directory_is_empty(src_path)
    directories.purge_directory_contents(src_path)
    assert directories.directory_is_empty(src_path)


def test_purge_directory_contents_can_empty_a_directory_with_subdirectories(directories_setup_with_files):
    src, src_path, file1, file2 = directories_setup_with_files

    sub1 = src.join("sub1")
    sub1.ensure(dir=True)

    assert not directories.directory_is_empty(src_path)
    directories.purge_directory_contents(src_path)
    assert directories.directory_is_empty(src_path)


def test_purge_directory_contents_with_delete_root(directories_setup_with_files):
    src, src_path, file1, file2 = directories_setup_with_files

    sub1 = src.join("sub1")
    sub1.ensure(dir=True)

    assert not directories.directory_is_empty(src_path)
    directories.purge_directory_contents(src_path, delete_root=True)
    assert not src_path.exists()