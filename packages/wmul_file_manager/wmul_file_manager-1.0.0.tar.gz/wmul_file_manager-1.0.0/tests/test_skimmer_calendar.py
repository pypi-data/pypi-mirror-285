"""
@Author = 'Mike Stanley'

Describe this file.

============ Change Log ============
7/11/2018 = Created.

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
from wmul_file_manager.utilities import skimmer_calendar


class TestLoadExpectedFileQuantityByDay:

    @pytest.mark.skimmer_calendar
    def test_normal_path(self, tmpdir):
        test_file = tmpdir.join("testfile.txt")
        test_file.write(
            """
            #		0		1		2		3		4		5		6		7		8		9		10		11		12		13		14		15		16		17		18		19		20		21		22		23
            #Day	12 AM,	1 AM,	2 AM,	3 AM,	4 AM,	5 AM,	6 AM,	7 AM,	8 AM,	9 AM,	10 AM,	11 AM,	12 PM,	1 PM,	2 PM,	3 PM,	4 PM,	5 PM,	6 PM,	7 PM,	8 PM,	9 PM,	10 PM,	11 PM
            Mon,	4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4
            Tue,	4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4
            Wed,	4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4
            Thu,	4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4
            Fri,	4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4
            Sat,	4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4
            Sun,	4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4
            """
        )

        expected_value = {
            0: [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
            1: [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
            2: [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
            3: [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
            4: [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
            5: [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
            6: [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4]
        }

        received_value = skimmer_calendar.load_skimmer_calendar(str(test_file))
        assert received_value == expected_value

    @pytest.mark.skimmer_calendar
    def test_not_all_days(self, tmpdir):
        test_file = tmpdir.join("testfile.txt")
        test_file.write(
            """
            #		0		1		2		3		4		5		6		7		8		9		10		11		12		13		14		15		16		17		18		19		20		21		22		23
            #Day	12 AM,	1 AM,	2 AM,	3 AM,	4 AM,	5 AM,	6 AM,	7 AM,	8 AM,	9 AM,	10 AM,	11 AM,	12 PM,	1 PM,	2 PM,	3 PM,	4 PM,	5 PM,	6 PM,	7 PM,	8 PM,	9 PM,	10 PM,	11 PM
            Mon,	4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4
            Wed,	4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4
            Thu,	4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4
            Fri,	4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4
            Sat,	4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4
            Sun,	4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4
            """
        )

        with pytest.raises(ValueError) as exc:
            skimmer_calendar.load_skimmer_calendar(str(test_file))

        assert "File does not contain data for every day of the week. " \
               "The days of the week that are present are " in str(exc.value)


class TestParseExpectedFileQuantityLine:

    @pytest.mark.skimmer_calendar
    def test_comment_line(self):
        this_line = "# ksaljdfklsadfkljfisaojsaefj"
        expected_quantity = {}
        skimmer_calendar._parse_expected_file_quantity_line(
            this_line=this_line,
            expected_file_quantity_by_day=expected_quantity
        )

        assert len(expected_quantity) == 0

    @pytest.mark.skimmer_calendar
    def test_normal_flow(self):
        mon_line = "Mon,	1,		2,		3,		4,		3,		2,		1,		2,		3,		4,		3,		2,		1,		2,		3,		4,		3,		2,		1,		2,		3,		4,		3,		1"
        tue_line = "Tue,	4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4,		4"

        expected_quantity = {}

        skimmer_calendar._parse_expected_file_quantity_line(
            this_line=mon_line,
            expected_file_quantity_by_day=expected_quantity
        )

        assert len(expected_quantity) == 1

        mon_list = expected_quantity[0]
        assert mon_list[0] == 1
        assert mon_list[1] == 2

        skimmer_calendar._parse_expected_file_quantity_line(
            this_line=tue_line,
            expected_file_quantity_by_day=expected_quantity
        )

        assert len(expected_quantity) == 2

        tue_list = expected_quantity[1]
        assert tue_list[0] == 4
        assert tue_list[1] == 4

    @pytest.mark.skimmer_calendar
    def test_not_enough_hours(self):
        mon_line = "Mon,	1,		2,		3,		4,		3,		2,		1,		2,		3,		4,		3,		2,		1,		2,		3,		4,		3,		2,		1,		2,		3,		4"
        # 22 hours

        expected_quantity = {}

        skimmer_calendar._parse_expected_file_quantity_line(
            this_line=mon_line,
            expected_file_quantity_by_day=expected_quantity
        )

        assert len(expected_quantity) == 1

        mon_list = expected_quantity[0]
        assert mon_list[0] == 1
        assert mon_list[1] == 2
        assert mon_list[22] == 0
        assert mon_list[23] == 0

    @pytest.mark.skimmer_calendar
    def test_too_many_hours(self):
        mon_line = "Mon,	1,		2,		3,		4,		3,		2,		1,		2,		3,		4,		3,		2,		1,		2,		3,		4,		3,		2,		1,		2,		3,		4,		3,		1,      2,      3"

        expected_quantity = {}

        with pytest.raises(ValueError) as exc:
            skimmer_calendar._parse_expected_file_quantity_line(
                this_line=mon_line,
                expected_file_quantity_by_day=expected_quantity
            )

        assert "Mon has more than 24 hours listed in the config file." in str(exc.value)

    @pytest.mark.skimmer_calendar
    def test_invalid_dow(self):
        mon_line = "Blu,	1,		2,		3,		4,		3,		2,		1,		2,		3,		4,		3,		2,		1,		2,		3,		4,		3,		2"

        expected_quantity = {}

        with pytest.raises(ValueError) as exc:
            skimmer_calendar._parse_expected_file_quantity_line(
                this_line=mon_line,
                expected_file_quantity_by_day=expected_quantity
            )

        assert "Blu is not a valid day-of-week." in str(exc.value)


class TestConvertToNumber:

    @pytest.mark.skimmer_calendar
    def test_not_a_number(self):
        assert skimmer_calendar._convert_to_number("jksalfjskdl") == 0

    @pytest.mark.skimmer_calendar
    def test_one_tab_before(self):
        assert skimmer_calendar._convert_to_number("\t4") == 4

    @pytest.mark.skimmer_calendar
    def test_one_tab_after(self):
        assert skimmer_calendar._convert_to_number("4\t") == 4

    @pytest.mark.skimmer_calendar
    def test_two_tabs(self):
            assert skimmer_calendar._convert_to_number("\t\t4") == 4
