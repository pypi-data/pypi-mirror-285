"""
@Author = 'Mike Stanley'

============ Change Log ============
2018-Jun-18 = Created.

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
import re
from wmul_file_manager import IsTheSkimmerWorking
import wmul_emailer


@pytest.fixture(scope="function")
def mockout_last_hour_information(mocker):
    mock_matching_regex = "mock_matching_regex"
    mock_date_directory = "mock_date_directory"
    mock_expected_file_quantity = "mock_expected_file_quantity"

    last_hour_information = IsTheSkimmerWorking._HourInformation(
        date_directory=mock_date_directory,
        matching_filename_regex=mock_matching_regex,
        expected_file_quantity=mock_expected_file_quantity
    )
    mock_get_last_hour_information = mocker.patch(
        "wmul_file_manager.IsTheSkimmerWorking._get_last_hour_information",
        autospec=True,
        return_value=last_hour_information
    )
    yield mock_date_directory, mock_matching_regex, mock_expected_file_quantity, mock_get_last_hour_information


class TestConstruction:

    @pytest.fixture(scope="function")
    def setup_construction(self, mockout_last_hour_information):
        mock_emailer = "mock_emailer"
        mock_calendar = "mock_calendar"
        mock_timezone = "mock_timezone"
        isw = IsTheSkimmerWorking.IsTheSkimmerWorking(mock_emailer, mock_calendar, mock_timezone)

        yield mockout_last_hour_information, mock_emailer, mock_calendar, isw, mock_timezone

    @pytest.mark.is_skimmer_working
    def test_get_last_hour_information_called_correctly(self, setup_construction):
        mockout_last_hour_information, _, mock_calendar, _, mock_timezone = setup_construction
        _, _, _, mock_get_last_hour_information = mockout_last_hour_information
        mock_get_last_hour_information.assert_called_once_with(mock_calendar, mock_timezone)

    @pytest.mark.is_skimmer_working
    def test_date_directory(self, setup_construction):
        mockout_last_hour_information, _, _, isw, _ = setup_construction
        mock_date_directory, _, _, _ = mockout_last_hour_information
        assert isw.date_directory == mock_date_directory

    @pytest.mark.is_skimmer_working
    def test_matching_filename_regex(self, setup_construction):
        mockout_last_hour_information, _, _, isw, _ = setup_construction
        _, mock_matching_regex, _, _ = mockout_last_hour_information
        assert isw.matching_filename_regex == mock_matching_regex

    @pytest.mark.is_skimmer_working
    def test_emailer(self, setup_construction):
        _, mock_emailer, _, isw, _ = setup_construction
        assert isw.emailer == mock_emailer

    @pytest.mark.is_skimmer_working
    def test_expected_file_quantity(self, setup_construction):
        mockout_last_hour_information, _, _, isw, _ = setup_construction
        _, _, mock_expected_file_quantity, _ = mockout_last_hour_information
        assert isw.expected_file_quantity == mock_expected_file_quantity


class TestGetLastHourInformation:

    @pytest.fixture(scope="function")
    def setup__get_last_hour_information(self, mocker):
        expected_date_directory = "2018-05-15"

        def mock_datetime_now_function(timezone):
            return datetime.datetime(year=2018, month=5, day=15, hour=12, minute=30, second=1)

        mocker.patch(
            "wmul_file_manager.IsTheSkimmerWorking.datetime",
            autospec=True,
            now=mock_datetime_now_function
        )

        expected_quantity = 12

        mock_calendar = {
            0: [7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7],
            1: [7, 7, 7, 7, 7, 7, 7, 7, 7, 7, expected_quantity, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7],
            2: [7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7],
            3: [7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7],
            4: [7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7],
            5: [7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7],
            6: [7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7],
        }

        expected_regex_string = "2018-05-15_11-[0-9]{2}-[0-9]{2}-[0-9]{3}"
        yield expected_date_directory, expected_regex_string, mock_calendar, expected_quantity

    @pytest.mark.is_skimmer_working
    def test__get_last_hour_information(self, setup__get_last_hour_information):
        expected_date_directory, expected_regex_string, mock_calendar, expected_quantity = setup__get_last_hour_information

        results = IsTheSkimmerWorking._get_last_hour_information(mock_calendar, "mock_timezone")

        assert results.date_directory == expected_date_directory
        assert results.matching_filename_regex.pattern == expected_regex_string


class TestFileIsForHourUnderTest:

    @pytest.fixture(scope="function")
    def setup__file_is_for_hour_under_test(self, mockout_last_hour_information):
        matching_filename_regex = re.compile("2018-05-15_12-[0-9]{2}-[0-9]{2}-[0-9]{3}")
        isw = IsTheSkimmerWorking.IsTheSkimmerWorking("mock_emailer", "mock_calendar", "mock_timezone")
        isw.matching_filename_regex = matching_filename_regex
        yield isw

    @pytest.mark.is_skimmer_working
    def test_true_return(self, setup__file_is_for_hour_under_test):
        isw = setup__file_is_for_hour_under_test
        filename = pathlib.Path(r"foo\2018-05-15_12-30-03-001.wav")
        assert isw._file_is_for_hour_under_test(filename)

    @pytest.mark.is_skimmer_working
    def test_false_return(self, setup__file_is_for_hour_under_test):
        isw = setup__file_is_for_hour_under_test
        filename = pathlib.Path(r"foo\2018-05-15_11-30-03-001.wav")
        assert not isw._file_is_for_hour_under_test(filename)


class TestCollectFilesOfPreviousHour:

    @pytest.fixture(scope="function")
    def setup__collect_files_of_previous_hour(self, tmpdir, mockout_last_hour_information):
        matching_filename_regex = re.compile("2018-05-15_12-[0-9]{2}-[0-9]{2}-[0-9]{3}")

        early_file = tmpdir.join("2018-05-15_11-45-00-000.wav")
        early_file.ensure()
        early_file = pathlib.Path(early_file)
        file_1 = tmpdir.join("2018-05-15_12-00-01-001.wav")
        file_1.ensure()
        file_1 = pathlib.Path(file_1)
        file_2 = tmpdir.join("2018-05-15_12-15-02-002.wav")
        file_2.ensure()
        file_2 = pathlib.Path(file_2)
        file_3 = tmpdir.join("2018-05-15_12-30-03-003.wav")
        file_3.ensure()
        file_3 = pathlib.Path(file_3)
        file_4 = tmpdir.join("2018-05-15_12-45-04-004.wav")
        file_4.ensure()
        file_4 = pathlib.Path(file_4)
        late_file = tmpdir.join("2018-05-15_13-00-05-005.wav")
        late_file.ensure()
        late_file = pathlib.Path(late_file)

        files_of_this_hour = [file_1, file_2, file_3, file_4]
        files_of_other_hours = [early_file, late_file]

        isw = IsTheSkimmerWorking.IsTheSkimmerWorking("mock_emailer", "mock_calendar", "mock_timezone")
        isw.matching_filename_regex = matching_filename_regex
        previous_hours_files = isw._collect_files_of_previous_hour(pathlib.Path(tmpdir))

        yield previous_hours_files, files_of_this_hour, files_of_other_hours

    @pytest.mark.is_skimmer_working
    def test__collect_files_of_previous_hour_this_hour(self, setup__collect_files_of_previous_hour):
        previous_hours_files, files_of_this_hour, _ = setup__collect_files_of_previous_hour

        for this_file in files_of_this_hour:
            assert this_file in previous_hours_files

    @pytest.mark.is_skimmer_working
    def test__collect_files_of_previous_hour_other_hours(self, setup__collect_files_of_previous_hour):
        previous_hours_files, _, files_of_other_hours = setup__collect_files_of_previous_hour

        for this_file in files_of_other_hours:
            assert this_file not in previous_hours_files


class TestDoesPreviousHourHaveCorrectNumberOfFiles:

    @pytest.fixture(scope="function")
    def setup_does_previous_hour_have_correct_number_of_files(self, mockout_last_hour_information):
        isw = IsTheSkimmerWorking.IsTheSkimmerWorking("mock_emailer", "mock_calendar", "mock_timezone")
        isw.expected_file_quantity = 4
        directory_of_previous_hour = "mock_directory_of_previous_hour"
        yield directory_of_previous_hour, isw

    @pytest.mark.is_skimmer_working
    def test_it_does(self, caplog, setup_does_previous_hour_have_correct_number_of_files):
        files_of_previous_hour = ["foo1", "foo2", "foo3", "foo4"]
        directory_of_previous_hour, isw = setup_does_previous_hour_have_correct_number_of_files

        isw._does_previous_hour_have_correct_number_of_files(
            files_of_previous_hour=files_of_previous_hour,
            directory_of_previous_hour=directory_of_previous_hour
        )
        assert not isw.problems
        assert "Folder mock_directory_of_previous_hour has the correct number of files." in caplog.text

    @pytest.mark.is_skimmer_working
    def test_it_has_too_many(self, caplog, setup_does_previous_hour_have_correct_number_of_files):
        files_of_previous_hour = ["foo1", "foo2", "foo3", "foo4", "foo5"]
        directory_of_previous_hour, isw = setup_does_previous_hour_have_correct_number_of_files
        isw._does_previous_hour_have_correct_number_of_files(
            files_of_previous_hour=files_of_previous_hour,
            directory_of_previous_hour=directory_of_previous_hour
        )
        expected_error_message = "Folder mock_directory_of_previous_hour does not have the correct number of files. " \
                                 "Should have 4, has 5."
        assert isw.problems
        assert expected_error_message in isw.problems
        assert expected_error_message in caplog.text

    @pytest.mark.is_skimmer_working
    def test_it_has_too_few(self, caplog, setup_does_previous_hour_have_correct_number_of_files):
        files_of_previous_hour = ["foo1", "foo2", "foo3"]
        directory_of_previous_hour, isw = setup_does_previous_hour_have_correct_number_of_files
        isw._does_previous_hour_have_correct_number_of_files(
            files_of_previous_hour=files_of_previous_hour,
            directory_of_previous_hour=directory_of_previous_hour
        )
        expected_error_message = "Folder mock_directory_of_previous_hour does not have the correct number of files. " \
                                 "Should have 4, has 3."
        assert isw.problems
        assert expected_error_message in isw.problems
        assert expected_error_message in caplog.text


class TestCheckFolderOfPreviousHour:

    @pytest.mark.is_skimmer_working
    def test_folder_exists(self, tmpdir, caplog, mockout_last_hour_information):
        directory_of_previous_hour = tmpdir.join("foo")
        directory_of_previous_hour.ensure(dir=True)
        directory_of_previous_hour = pathlib.Path(directory_of_previous_hour)

        isw = IsTheSkimmerWorking.IsTheSkimmerWorking("mock_emailer", "mock_calendar", "mock_timezone")

        assert isw._check_existance_of_directory_of_previous_hour(directory_of_previous_hour=directory_of_previous_hour)
        assert not isw.problems
        assert f"{directory_of_previous_hour} exists." in caplog.text

    @pytest.mark.is_skimmer_working
    def test_folder_does_not_exist(self, tmpdir, caplog, mockout_last_hour_information):
        directory_of_previous_hour = tmpdir.join("foo")
        assert not directory_of_previous_hour.check()
        directory_of_previous_hour = pathlib.Path(directory_of_previous_hour)

        isw = IsTheSkimmerWorking.IsTheSkimmerWorking("mock_emailer", "mock_calendar", "mock_timezone")

        assert not isw._check_existance_of_directory_of_previous_hour(
            directory_of_previous_hour=directory_of_previous_hour
        )
        expected_error_message = f"{directory_of_previous_hour} is not a folder."
        assert isw. problems
        assert expected_error_message in isw.problems
        assert expected_error_message in caplog.text


class TestIsTheSkimmerWorkingOnThisDirectory:

    @pytest.fixture(scope="function", params=[True, False])
    def setup_is_the_skimmer_working_on_this_directory(self, mocker, request, mockout_last_hour_information):
        directory_exists = request.param
        mock_check_directory = mocker.patch(
            "wmul_file_manager.IsTheSkimmerWorking.IsTheSkimmerWorking._check_existance_of_directory_of_previous_hour",
            autospec=True,
            return_value=directory_exists
        )

        mock_files_of_previous_hour = "mock_files_of_previous_hour"

        mock_collect_files = mocker.patch(
            "wmul_file_manager.IsTheSkimmerWorking.IsTheSkimmerWorking._collect_files_of_previous_hour",
            autospec=True,
            return_value=mock_files_of_previous_hour
        )

        mock_does_previous_hour = mocker.patch(
            "wmul_file_manager.IsTheSkimmerWorking.IsTheSkimmerWorking."
            "_does_previous_hour_have_correct_number_of_files",
            autospec=True
        )

        mock_date_directory, mock_matching_regex, _, _ = mockout_last_hour_information

        mock_timezone = "mock_timezone"

        isw = IsTheSkimmerWorking.IsTheSkimmerWorking("mock_emailer", "mock_calendar", mock_timezone)
        isw._is_the_skimmer_working_on_this_directory(mock_date_directory)

        yield directory_exists, mock_check_directory, mock_files_of_previous_hour, mock_collect_files, \
              mock_does_previous_hour, mock_date_directory, mock_matching_regex, isw

    @pytest.mark.is_skimmer_working
    def test_check_directory_called_correctly(self, setup_is_the_skimmer_working_on_this_directory):
        _, mock_check_directory, _, _, _, mock_directory_of_previous_hour, _, \
            isw = setup_is_the_skimmer_working_on_this_directory

        mock_check_directory.assert_called_once_with(isw, mock_directory_of_previous_hour)

    @pytest.mark.is_skimmer_working
    def test_collect_files_called_correctly(self, setup_is_the_skimmer_working_on_this_directory):
        directory_exists, _, _, mock_collect_files, _, mock_directory_of_previous_hour, mock_matching_filename_regex, \
            isw = setup_is_the_skimmer_working_on_this_directory

        if directory_exists:
            mock_collect_files.assert_called_once_with(isw, mock_directory_of_previous_hour)
        else:
            mock_collect_files.assert_not_called()

    @pytest.mark.is_skimmer_working
    def test_does_previous_hour_called_correctly(self, setup_is_the_skimmer_working_on_this_directory):
        directory_exists, _, mock_files_of_previous_hour, _, mock_does_previous_hour, mock_directory_of_previous_hour, \
            _, isw = setup_is_the_skimmer_working_on_this_directory

        if directory_exists:
            mock_does_previous_hour.assert_called_once_with(
                isw,
                mock_files_of_previous_hour,
                mock_directory_of_previous_hour
            )
        else:
            mock_does_previous_hour.assert_not_called()


class TestIsTheSkimmerWorking:

    @pytest.fixture(scope="function", params=[True, False])
    def setup_is_this_skimmer_working(self, tmpdir, mocker, request, mockout_last_hour_information):
        has_problems = request.param
        mock_date_directory, _, _, mock_get_last_hour_information = mockout_last_hour_information

        def on_this_directory_function(self_, directory_of_previous_hour):
            if has_problems:
                self_.problems.append("Yes")

        mock_on_this_directory = mocker.patch(
            "wmul_file_manager.IsTheSkimmerWorking.IsTheSkimmerWorking._is_the_skimmer_working_on_this_directory",
            autospec=True,
        )
        mock_on_this_directory.side_effect = on_this_directory_function

        mock_send_alert_email = mocker.patch(
            "wmul_file_manager.IsTheSkimmerWorking.IsTheSkimmerWorking._send_alert_email",
            autospec=True
        )

        directory_1 = tmpdir.join("dir_1")
        directory_1.ensure(dir=True)
        directory_1 = pathlib.Path(directory_1)
        directory_2 = tmpdir.join("dir_2")
        directory_2.ensure(dir=True)
        directory_2 = pathlib.Path(directory_2)

        directory_list = [directory_1, directory_2]

        mock_calendar = "mock_calendar"
        mock_timezone = "mock_timezone"

        isw = IsTheSkimmerWorking.IsTheSkimmerWorking("mock_emailer", mock_calendar, mock_timezone)
        isw.run_script(directory_list=directory_list)

        yield has_problems, mock_date_directory, mock_get_last_hour_information, mock_on_this_directory, \
              mock_send_alert_email, directory_1, directory_2, mock_calendar, isw, mock_timezone

    @pytest.mark.is_skimmer_working
    def test_get_last_hour_called_correctly(self, setup_is_this_skimmer_working):
        _, _, mock_get_last_hour_information, _, _, _, _, mock_calendar, _, mock_timezone = setup_is_this_skimmer_working
        mock_get_last_hour_information.assert_called_once_with(mock_calendar, mock_timezone)

    @pytest.mark.is_skimmer_working
    def test_on_this_directory_called_correctly(self, setup_is_this_skimmer_working, mocker):
        _, mock_date_directory, _, mock_on_this_directory, _, directory_1, directory_2, _, \
            isw, _ = setup_is_this_skimmer_working

        expected_calls = [
            mocker.call(isw, directory_1 / mock_date_directory),
            mocker.call(isw, directory_2 / mock_date_directory)
        ]

        mock_on_this_directory.assert_has_calls(expected_calls)
        assert mock_on_this_directory.call_count == len(expected_calls)

    @pytest.mark.is_skimmer_working
    def test_send_alert_email_called_correctly(self, setup_is_this_skimmer_working):
        has_problems, _, _, _, mock_send_alert_email, _, _, _, isw, _ = setup_is_this_skimmer_working

        if has_problems:
            mock_send_alert_email.assert_called_once_with(isw)
        else:
            mock_send_alert_email.assert_not_called()


class TestSendAlertEmail:

    @pytest.mark.is_skimmer_working
    def test_send_alert_email(self, mocker, mockout_last_hour_information):
        mock_emailer = mocker.Mock()
        problems = [
            "This is problem line number 1.",
            "This is problem line number 2.",
            "This is problem line number 3."
        ]

        isw = IsTheSkimmerWorking.IsTheSkimmerWorking(mock_emailer, "mock_calendar", "mock_timezone")
        isw.problems = problems

        isw._send_alert_email()

        expected_body = "The skimmer failed during the previous hour.\nThis is problem line number 1.\n" \
                        "This is problem line number 2.\nThis is problem line number 3."
        expected_subject = "[Skimmer] Skimmer failure!"

        mock_emailer.send_email.assert_called_once_with(email_body=expected_body, email_subject=expected_subject)


integration_params = [
    {"correct_number_of_files": True, "too_many": False},
    {"correct_number_of_files": False, "too_many": False},
    {"correct_number_of_files": False, "too_many": True}
]


class TestIntegration:

    @pytest.fixture(scope="function", params=integration_params)
    def setup_integration(self, mocker, tmpdir, request):
        correct_number_of_files = request.param["correct_number_of_files"]
        too_many = request.param["too_many"]
        if correct_number_of_files:
            count_of_files = 4
        elif too_many:
            count_of_files = 5
        else:
            count_of_files = 3

        mock_emailer = mocker.create_autospec(wmul_emailer.EmailSender, spec_set=True, instance=True)
        mock_calendar = {
            0: [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
            1: [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
            2: [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
            3: [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
            4: [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
            5: [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
            6: [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
        }

        def mock_datetime_now_function(timezone):
            return datetime.datetime(year=2018, month=5, day=15, hour=12, minute=30, second=1)
        mocker.patch(
            "wmul_file_manager.IsTheSkimmerWorking.datetime",
            autospec=True,
            now=mock_datetime_now_function
        )

        from zoneinfo import ZoneInfo

        mock_timezone = ZoneInfo("America/New_York")

        base_dir = tmpdir.join("base")
        base_dir.ensure(dir=True)
        date_dir = base_dir.join("2018-05-15")
        date_dir.ensure(dir=True)
        base_dir = pathlib.Path(base_dir)
        date_dir = pathlib.Path(date_dir)
        file_name_string = f"2018-05-15_11-30-05"
        create_an_hours_files(count_of_files, file_name_string, date_dir)
        yield mock_emailer, mock_calendar, base_dir, date_dir, correct_number_of_files, too_many, mock_timezone

    def test_integration(self, setup_integration):
        mock_emailer, mock_calendar, base_dir, date_dir, correct_number_of_files, too_many, mock_timezone = setup_integration
        isw = IsTheSkimmerWorking.IsTheSkimmerWorking(mock_emailer, mock_calendar, mock_timezone)
        isw.run_script([base_dir])

        expected_subject = "[Skimmer] Skimmer failure!"

        if correct_number_of_files:
            mock_emailer.send_email.assert_not_called()
        elif too_many:
            expected_body = f"The skimmer failed during the previous hour.\nFolder {date_dir} does not have the " \
                            f"correct number of files. Should have 4, has 5.\n" \
                            f"{date_dir}\\2018-05-15_11-30-05-000.wav\n" \
                            f"{date_dir}\\2018-05-15_11-30-05-001.wav\n" \
                            f"{date_dir}\\2018-05-15_11-30-05-002.wav\n" \
                            f"{date_dir}\\2018-05-15_11-30-05-003.wav\n" \
                            f"{date_dir}\\2018-05-15_11-30-05-004.wav"
            mock_emailer.send_email.assert_called_once_with(
                email_body=expected_body,
                email_subject=expected_subject
            )
        else:
            expected_body = f"The skimmer failed during the previous hour.\nFolder {date_dir} does not have the " \
                            f"correct number of files. Should have 4, has 3.\n" \
                            f"{date_dir}\\2018-05-15_11-30-05-000.wav\n" \
                            f"{date_dir}\\2018-05-15_11-30-05-001.wav\n" \
                            f"{date_dir}\\2018-05-15_11-30-05-002.wav"
            mock_emailer.send_email.assert_called_once_with(
                email_body=expected_body,
                email_subject=expected_subject
            )


def random_bytes(count=100):
    return bytearray(random.randint(0, 255) for i in range(count))


def create_an_hours_files(count_of_files, file_name_string, base_dir):
    file_names_this_hour = (
        base_dir / f"{file_name_string}-{ix:03d}.wav"
        for ix in range(0, count_of_files)
    )
    for file_item in file_names_this_hour:
        file_item.write_bytes(random_bytes())

