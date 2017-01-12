#!/usr/bin/env python
import datetime
__author__ = 'Charles Henri Darakdjian'
__copyright__ = 'Copyright 2016, Intel Corporation'
__maintainer__ = 'Charles Henri Darakdjian'


def make_left_padded_character_string(string_to_pad_parameter,
                                      int_length_of_string_to_return,
                                      string_character_to_pad_with):
    """Creates a string padded with a characters/strings equal to 3rd parameter if the length of the 1st parameter
    is less than the int_length_of_string_to_return.

    @PARAMETERS
    string_to_pad_parameter - The string to use as the basic for the new string to pad.
    int_length_of_string_to_return - The integer determining the resulting length of the string to pad.
    string_character_to_pad_with - The character/string to use for padding.

    @RETURNS
    A new string of two characters padded on the left with the character/string given as the 2nd parameter.
    """
    if len(string_to_pad_parameter) < int_length_of_string_to_return:
        return string_character_to_pad_with + string_to_pad_parameter
    return string_to_pad_parameter


def make_proper_date_format(string_date_time_parameter):
    """Arranges date time data in suitable format used by Ubuntu system.

    @PARAMETERS
    string_date_time_parameter - Date-time object retrieved from strftime API.
    """
    string_local_date, string_hour_minute_second_parameter = string_date_time_parameter.split(" ")
    string_local_month, string_local_day, string_local_year = string_local_date.split("-")
    dictionary_calendar_month = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
                                 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}
    string_month_parameter = dictionary_calendar_month[int(string_local_month.lstrip('0'))]
    int_day_parameter = int(string_local_day.lstrip('0'))
    return string_month_parameter, int_day_parameter, string_hour_minute_second_parameter


def make_expression_list_match_on_current_and_next_minute(string_hour_minute_second_parameter, int_dfu_tool_duration):
    """Creates a string representing the hour and minute that will match for at least the
    current minute and the next minute. This function assumes that the DFU tool's timestamps in the UNIX
    system log file are spaced out by a maximum of 90 seconds apart (the DFU tool will probably take shorter
    time to execute, but we must account for multiple processes writing to that system log file.

    @PARAMETERS
    string_hour_minute_second_parameter - A string in the format HH:MM:DD.
    int_dfu_tool_duration - An integer estimating the maximum time window where messages can be apart in the UNIX
    system log file for one run of the DFU tool.

    @EXAMPLES
    Given "19:59:30". This tool returns a list of the following two minutes, "19:59:\d\d" and "20:01:\d\d".
    Given "13:59:30". This tool returns a list of the following two minutes, "13:59:\d\d" and "14:01:\d\d".
    Given "14:29:30". This tool returns a list of the following two minutes, "14:29:\d\d" and "14:31:\d\d".
    Given "02:28:14". This tool returns a list of the following two minutes, "02:28:\d\d" and "02:29:\d\d".
    Given "09:09:30". This tool returns a list of the following two minutes, "09:09:\d\d" and "09:11:\d\d".
    Given "09:59:01". This tool returns a list of the following two minutes, "09:59:\d\d" and "10:00:\d\d".

    @RETURNS
    A list of expression matches that will cover the minute the tool has been ran and the following minute.

    Note: This tool assumes that the process will take at most two minutes in duration (worst case).
    """
    list_string_of_two_minutes = list()
    string_local_hour_time_dfu_tool_launched, string_local_minute_time_dfu_tool_launched, \
    string_local_second_time_dfu_tool_launched = string_hour_minute_second_parameter.split(":")
    date_time_dfu_tool_ran_minute_object = datetime.datetime(100, 1, 1,
                                                             int(string_local_hour_time_dfu_tool_launched),
                                                             int(string_local_minute_time_dfu_tool_launched),
                                                             int(string_local_second_time_dfu_tool_launched))
    date_time_next_minute = date_time_dfu_tool_ran_minute_object + datetime.timedelta(0, int_dfu_tool_duration)  # Adding 90 seconds

    # Add current minute (minute when DFU tool was ran) as regular expression to list.
    string_padded_hour_dfu_time_launched = \
        make_left_padded_character_string(string_local_hour_time_dfu_tool_launched, 2, '0')
    string_padded_minute_dfu_time_launched = \
        make_left_padded_character_string(string_local_minute_time_dfu_tool_launched, 2, '0')
    string_padded_dfu_tool_launched = ":".join((string_padded_hour_dfu_time_launched,
                                                string_padded_minute_dfu_time_launched,
                                                '\d\d'))
    list_string_of_two_minutes.append(string_padded_dfu_tool_launched)

    # Add the next minute (minute after the DFU tool was ran) as regular expression to list.
    string_padded_hour_next_time_segment = \
        make_left_padded_character_string(str(date_time_next_minute.hour), 2, '0')
    string_padded_minute_next_time_segment = \
        make_left_padded_character_string(str(date_time_next_minute.minute), 2, '0')

    string_padded_next_minute_dfu_tool_runs = ":".join((string_padded_hour_next_time_segment,
                                                        string_padded_minute_next_time_segment,
                                                        '\d\d'))
    list_string_of_two_minutes.append(string_padded_next_minute_dfu_tool_runs)

    # Return that list.
    return list_string_of_two_minutes

# string_test_case_1 = "19:59:30"
# print "\nFOR TEST CASE 1 at " + string_test_case_1
# make_expression_list_match_on_current_and_next_minute(string_test_case_1)

# string_test_case_2 = "13:59:30"
# print "\nFOR TEST CASE 2 at " + string_test_case_2
# make_expression_list_match_on_current_and_next_minute(string_test_case_2)

# string_test_case_3 = "14:29:30"
# print "\nFOR TEST CASE 3 at " + string_test_case_3
# make_expression_list_match_on_current_and_next_minute(string_test_case_3)

# string_test_case_4 = "02:28:14"
# print "\nFOR TEST CASE 4 at " + string_test_case_4
# make_expression_list_match_on_current_and_next_minute(string_test_case_4)

# string_test_case_5 = "09:09:30"
# print "\nFOR TEST CASE 5 at " + string_test_case_5
# make_expression_list_match_on_current_and_next_minute(string_test_case_5)

# string_test_case_6 = "09:59:01"
# print "\nFOR TEST CASE 6 at " + string_test_case_6
# make_expression_list_match_on_current_and_next_minute(string_test_case_6)
