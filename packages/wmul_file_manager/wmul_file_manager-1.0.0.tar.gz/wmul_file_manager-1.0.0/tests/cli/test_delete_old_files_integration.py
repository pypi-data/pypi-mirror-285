"""
@Author = 'Mike Stanley'

============ Change Log ============
2024-May-03 = Created.

============ License ============
The MIT License (MIT)

Copyright (c) 2024 Michael Stanley

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
from wmul_file_manager import cli

import os
import pathlib

def test_delete_old_files_integration(fs):
    root_folder = pathlib.Path("/temp")

    file_1 = root_folder / "file_1.txt"
    fs.create_file(file_1)
    file_1_expected_mtime = 1514808000.0  # 2018-January-01, Noon, UTC
    os.utime(file_1, (file_1_expected_mtime, file_1_expected_mtime))

    file_2 = root_folder / "file_2.txt"
    fs.create_file(file_2)
    file_2_expected_mtime = 1652395200.0  # 2022-May-12, 22:40, UTC
    os.utime(file_2, (file_2_expected_mtime, file_2_expected_mtime))

    file_3 = root_folder / "file_3.txt"
    fs.create_file(file_3)
    file_3_expected_mtime = 1608617700.0  # 2020-December-22, 06:15, UTC
    os.utime(file_3, (file_3_expected_mtime, file_3_expected_mtime))

    file_4 = root_folder / "file_4.txt"
    fs.create_file(file_4)
    file_4_expected_mtime = 1722855540.0  # 2024-August-05, 10:59, UTC
    os.utime(file_4, (file_4_expected_mtime, file_4_expected_mtime))

    run_args = [
        str(root_folder),
        "--cutoff_date",
        "2021-05-05",
    ]

    assert file_1.exists()
    assert file_2.exists()
    assert file_3.exists()
    assert file_4.exists()
    
    runner = CliRunner()
    result = runner.invoke(cli.delete_old_files, run_args)

    assert result.exit_code == 0

    assert not file_1.exists()
    assert file_2.exists()
    assert not file_3.exists()
    assert file_4.exists()

