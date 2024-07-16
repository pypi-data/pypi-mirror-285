"""
@Author = 'Mike Stanley'

============ Change Log ============
2018-Jun-14 = Add autospec to the mocker.patch calls.

2018-May-18 = Created.

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
import datetime
import pathlib
import pytest
import random
from collections import defaultdict, namedtuple
from wmul_file_manager import DidTheSkimmerCopyTheFiles
from wmul_file_manager.utilities import skimmer_calendar
import wmul_emailer


class TestDidTheSkimmerCopyTheFiles_Construction:

    @pytest.mark.did_skimmer_copy
    def test_normal_path(self):
        mock_directories = "mock_directories"
        mock_calendar = "mock_calendar"
        mock_emailer = "mock_emailer"

        result = DidTheSkimmerCopyTheFiles.DidTheSkimmerCopyTheFiles(
            directories=mock_directories,
            _skimmer_calendar=mock_calendar,
            emailer=mock_emailer
        )

        assert result.directories == mock_directories
        assert result._skimmer_calendar == mock_calendar
        assert result.emailer == mock_emailer

    @pytest.mark.did_skimmer_copy
    def test_str(self):
        mock_directories = "mock_directories"
        mock_calendar = "mock_calendar"
        mock_emailer = "mock_emailer"

        result = DidTheSkimmerCopyTheFiles.DidTheSkimmerCopyTheFiles(
            directories=mock_directories,
            _skimmer_calendar=mock_calendar,
            emailer=mock_emailer
        )

        assert str(result) == "DidTheSkimmerCopyTheFiles: directories: mock_directories, " \
                              "emailer: mock_emailer, problems: [], calendar: mock_calendar"


class TestDidTheSkimmerCopyTheFiles_run_script:

    @pytest.fixture(scope="function")
    def setup_class_run_script(self, mocker):
        mock_directories = ["mock_directory_1", "mock_directory_2"]
        mock_calendar = "mock_calendar"
        mock_emailer = "mock_emailer"
        mock_send_alert_email = mocker.patch(
            "wmul_file_manager.DidTheSkimmerCopyTheFiles.DidTheSkimmerCopyTheFiles._send_alert_email",
            autospec=True
        )

        dscf = DidTheSkimmerCopyTheFiles.DidTheSkimmerCopyTheFiles(
            directories=mock_directories,
            _skimmer_calendar=mock_calendar,
            emailer=mock_emailer
        )

        mock_did_the_skimmer = mocker.patch(
            "wmul_file_manager.DidTheSkimmerCopyTheFiles.DidTheSkimmerCopyTheFiles."
            "_did_the_skimmer_copy_the_files_for_this_folder",
            autospec=True
        )

        yield mock_directories, dscf, mock_send_alert_email, mock_calendar, mock_did_the_skimmer

    @pytest.mark.did_skimmer_copy
    def test_run_script_no_problems(self, setup_class_run_script):
        mock_directories, dscf, mock_send_alert_email, mock_calendar, mock_did_the_skimmer = setup_class_run_script

        dscf.run_script()

        directories_in_call_list = []
        call_list = mock_did_the_skimmer.call_args_list

        for call_args, _ in call_list:
            _, call_directory = call_args
            assert call_directory in mock_directories
            directories_in_call_list.append(call_directory)

        for mock_dir in mock_directories:
            assert mock_dir in directories_in_call_list

        assert len(dscf.problems) == 0
        mock_send_alert_email.assert_not_called()

    @pytest.mark.did_skimmer_copy
    def test_run_script_has_problems(self, setup_class_run_script):
        mock_directories, dscf, mock_send_alert_email, mock_calendar, mock_did_the_skimmer = setup_class_run_script

        def mock_did_the_skimmer_function(self_, base_directory):
            self_.problems.append("Problem")
        mock_did_the_skimmer.side_effect = mock_did_the_skimmer_function

        dscf.run_script()

        directories_in_call_list = []
        call_list = mock_did_the_skimmer.call_args_list

        for call_args, _ in call_list:
            _, call_directory = call_args
            assert call_directory in mock_directories
            directories_in_call_list.append(call_directory)

        for mock_dir in mock_directories:
            assert mock_dir in directories_in_call_list

        assert "Problem" in dscf.problems
        assert len(dscf.problems) == 2
        mock_send_alert_email.assert_called_once()


class TestDidTheSkimmerCopyTheFiles_did_the_skimmer_copy_the_files_for_this_folder:

    @pytest.mark.did_skimmer_copy
    @pytest.mark.parametrize("yesterday_exists", [True, False])
    def test_did_the_skimmer(self, yesterday_exists, mocker, fs):
        mock_directory = pathlib.Path("mock_directory")

        if yesterday_exists:
            fs.create_dir(mock_directory)

        mock_yesterday_information = DidTheSkimmerCopyTheFiles._YesterdayInformation(
            directory=mock_directory,
            expected_file_quantity="mock_file_quantity"
        )
        mock_get_yesterday = mocker.patch(
            "wmul_file_manager.DidTheSkimmerCopyTheFiles.DidTheSkimmerCopyTheFiles._get_yesterdays_information",
            autospec=True
        )
        mock_get_yesterday.return_value = mock_yesterday_information

        mock_check_count = mocker.patch(
            "wmul_file_manager.DidTheSkimmerCopyTheFiles.DidTheSkimmerCopyTheFiles."
            "_check_count_of_files_in_yesterdays_directory",
            autospec=True
        )

        mock_base_directory = "mock_base_directory"

        dscf = DidTheSkimmerCopyTheFiles.DidTheSkimmerCopyTheFiles(
            directories="mock_directories",
            _skimmer_calendar="mock_skimmer_calendar",
            emailer="mock_emailer"
        )
        dscf._did_the_skimmer_copy_the_files_for_this_folder(mock_base_directory)

        mock_get_yesterday.assert_called_once_with(dscf, mock_base_directory)

        if yesterday_exists:
            mock_check_count.assert_called_once_with(dscf, mock_yesterday_information)
            assert not dscf.problems
        else:
            mock_check_count.assert_not_called()
            assert "Yesterday's directory does not exist: mock_directory" in dscf.problems


class TestDidTheSkimmerCopyTheFiles_get_yesterdays_information:

    @pytest.fixture(scope="function")
    def setup__get_yesterdays_directory(self, tmpdir, mocker):
        base_directory = tmpdir.join("base_dir")
        expected_date = datetime.datetime(year=2018, month=5, day=14)
        expected_yesterday_directory = base_directory.join("2018-05-14")

        def mock_date_today_function():
            return datetime.datetime(year=2018, month=5, day=15)

        mocker.patch(
            "wmul_file_manager.DidTheSkimmerCopyTheFiles.datetime",
            autospec=True,
            today=mock_date_today_function
        )

        mock_get_date_folder_name = mocker.patch(
            "wmul_file_manager.CopyYesterdaysSkimmerFiles.get_date_folder_name",
            autospec=True
        )
        mock_get_date_folder_name.return_value = expected_yesterday_directory

        dscf = DidTheSkimmerCopyTheFiles.DidTheSkimmerCopyTheFiles(
            directories="mock_directories",
            _skimmer_calendar=defaultdict(lambda: mock_file_quantity),
            emailer="mock_emailer"
        )

        mock_file_quantity = "mock_file_quantity"

        yield mock_get_date_folder_name, base_directory, expected_date, expected_yesterday_directory, \
              mock_file_quantity, dscf

    @pytest.mark.did_skimmer_copy
    def test_get_yesterdays_directory_exists(self, setup__get_yesterdays_directory):
        mock_get_date_folder_name, base_directory, expected_date, expected_yesterday_directory, mock_file_quantity, \
            dscf = setup__get_yesterdays_directory

        yesterdays_information = dscf._get_yesterdays_information(base_directory)

        mock_get_date_folder_name.assert_called_once_with(base_directory, expected_date)

        assert expected_yesterday_directory == yesterdays_information.directory
        assert mock_file_quantity == yesterdays_information.expected_file_quantity


_check_count_test_params = namedtuple(
    "_check_count_test_params",
    [
        "which_hour_is_wrong",
        "expected_count",
        "too_many"
    ]
)

_check_count_params_list = [
    _check_count_test_params(which_hour_is_wrong=4, expected_count=4, too_many=True),
    _check_count_test_params(which_hour_is_wrong=12, expected_count=4, too_many=False),
    _check_count_test_params(which_hour_is_wrong=-1, expected_count=4, too_many=False)
    # Use an out-of-bounds hour to cause all hours to be correct
]


class TestDidTheSkimmerCopyTheFiles_check_count:

    @pytest.fixture(scope="function", params=_check_count_params_list)
    def setup__check_count(self, request, fs):
        check_count_test_param = request.param
        dscf = DidTheSkimmerCopyTheFiles.DidTheSkimmerCopyTheFiles(
            directories="mock_directories",
            _skimmer_calendar="mock_expected_quantity",
            emailer="mock_emailer"
        )

        base_dir = pathlib.Path("base_dir")
        fs.create_dir(base_dir)

        file_name_string = "2018-06-14"

        def file_creation_callback(file_item):
            fs.create_file(file_item)

        wrong_hour_count = create_a_days_files(check_count_test_param, file_name_string, base_dir, file_creation_callback)
        expected_count = [check_count_test_param.expected_count for _ in range(0, 24)]

        yield dscf, base_dir, check_count_test_param, expected_count, wrong_hour_count

    @pytest.mark.did_skimmer_copy
    def test__check_count(self, setup__check_count, caplog):
        dscf, base_dir, check_count_test_param, expected_count, wrong_hour_count = setup__check_count

        mock_yesterday_information = DidTheSkimmerCopyTheFiles._YesterdayInformation(
            directory=base_dir,
            expected_file_quantity=expected_count
        )

        dscf._check_count_of_files_in_yesterdays_directory(mock_yesterday_information)

        if check_count_test_param.which_hour_is_wrong < 0:
            assert not dscf.problems
            for this_hour in range(0, 24):
                assert f"Correct number of files for hour {this_hour} in: {base_dir}" in caplog.text
        else:
            assert dscf.problems
            expected_error_message = \
                f"Incorrect number of files for hour {check_count_test_param.which_hour_is_wrong} in: " \
                f"{base_dir}\nShould have {check_count_test_param.expected_count}, has {wrong_hour_count}\n"
            assert expected_error_message in dscf.problems


class TestDidTheSkimmerCopyTheFiles_send_alert_email:

    @pytest.mark.did_skimmer_copy
    def test_send_alert_email(self, mocker):
        mock_emailer = mocker.Mock()
        problems = [
            "This is problem line number 1.",
            "This is problem line number 2.",
            "This is problem line number 3."
        ]

        dscf = DidTheSkimmerCopyTheFiles.DidTheSkimmerCopyTheFiles(
            directories="Mock Directories",
            _skimmer_calendar="Mock Expected Quantity",
            emailer=mock_emailer
        )
        dscf.problems = problems

        dscf._send_alert_email()

        expected_body = "This is problem line number 1.\nThis is problem line number 2.\nThis is problem line number 3."
        expected_subject = "[Skimmer] Skimmer copy failure!"

        mock_emailer.send_email.assert_called_once_with(email_body=expected_body, email_subject=expected_subject)


class TestIntegration:

    @pytest.fixture(scope="function", params=_check_count_params_list)
    def setup_integration_test(self, tmpdir, request, mocker):
        params = request.param
        base_dir = tmpdir.join("base_dir")
        base_dir.ensure(dir=True)

        expected_file_quantity_file_name = tmpdir.join("calendar.txt")
        expected_file_quantity_file_name.write_text(
            "#		0		1		2		3		4		5		6		7		8		9		10		11		12		13		14		15		16		17		18		19		20		21		22		23\n"
            "#Day	12 AM,	1 AM,	2 AM,	3 AM,	4 AM,	5 AM,	6 AM,	7 AM,	8 AM,	9 AM,	10 AM,	11 AM,	12 PM,	1 PM,	2 PM,	3 PM,	4 PM,	5 PM,	6 PM,	7 PM,	8 PM,	9 PM,	10 PM,	11 PM\n"
            "Mon,	4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4\n"
            "Tue,	4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4\n"
            "Wed,	4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4\n"
            "Thu,	4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4\n"
            "Fri,	4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4\n"
            "Sat,	4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4\n"
            "Sun,	4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4\n",
            "utf-8"
        )

        yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
        file_name_string = f"{yesterday.year:04d}-{yesterday.month:02d}-{yesterday.day:02d}"
        yesterday_dir = base_dir.join(file_name_string)
        yesterday_dir.ensure(dir=True)

        def file_creation_callback(file_item):
            file_item.write_binary(bytearray(random.randint(0, 255) for _ in range(100)))

        wrong_hour_count = create_a_days_files(params, file_name_string, yesterday_dir, file_creation_callback)

        mock_emailer = mocker.Mock(spec=wmul_emailer.EmailSender)

        _skimmer_calendar = skimmer_calendar.load_skimmer_calendar(expected_file_quantity_file_name)

        dscf = DidTheSkimmerCopyTheFiles.DidTheSkimmerCopyTheFiles(
            directories=[pathlib.Path(base_dir)],
            _skimmer_calendar=_skimmer_calendar,
            emailer=mock_emailer
        )

        yield dscf, params, yesterday_dir, wrong_hour_count

    @pytest.mark.did_skimmer_copy
    def test_integration_test(self, setup_integration_test, caplog):
        dscf, params, yesterday_dir, wrong_hour_count = setup_integration_test

        dscf.run_script()

        if params.which_hour_is_wrong < 0:
            assert not dscf.problems
            for this_hour in range(0, 24):
                assert f"Correct number of files for hour {this_hour} in: {yesterday_dir}" in caplog.text
        else:
            assert dscf.problems
            expected_error_message = \
                f"Incorrect number of files for hour {params.which_hour_is_wrong} in: " \
                f"{yesterday_dir}\nShould have {params.expected_count}, has {wrong_hour_count}\n"
            assert expected_error_message in dscf.problems


def create_a_days_files(params, file_name_string, base_dir, file_creation_callback):
    if params.too_many:
        wrong_hour_count = params.expected_count + 1
    else:
        wrong_hour_count = params.expected_count - 1

    for this_hour in range(0, 24):
        if this_hour == params.which_hour_is_wrong:
            actual_count = wrong_hour_count
        else:
            actual_count = params.expected_count

        file_names_this_hour = (
            base_dir / f"{file_name_string}_{this_hour:02d}-30-05-{ix:03d}.wav"
            for ix in range(0, actual_count)
        )
        for file_item in file_names_this_hour:
            file_creation_callback(file_item)

    return wrong_hour_count
