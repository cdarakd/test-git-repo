#!/usr/bin/env python
import re
# import os
# from time import gmtime, strftime
import MockDFUDate
__author__ = 'Charles Henri Darakdjian'
__copyright__ = 'Copyright 2016, Intel Corporation'
__maintainer__ = 'Charles Henri Darakdjian'


def read_unix_system_log_file(string_full_file_path_to_read_parameter,
                              string_month_parameter,
                              int_day_parameter,
                              string_hour_minute_second_parameter,
                              string_dfu_tool_marker_parameter,
                              list_resulting_data_parameter):  # "out" parameter. This list will be constructed.
    """Function to read in all messages in the UNIX system log file for the given month, day, and time frame.
    This function identifies the tool by its marker and will build a list of all such messages.

    @PARAMETERS
    string_full_file_path_to_read - Full filepath of the UNIX Syslog file to read.
    string_month_parameter - 3-letter code representing a month in the calendar year.
    int_day_parameter - integer representing the date to search for.
    string_hour_minute_second_parameter - hh:mm:ss time.
    string_dfu_tool_marker - name of the tool to search for.
    list_resulting_data - resulting list created from this function.

    @RETURN CODE
    0 on successful. -1 on failure.
    """
    # Open file
    try:
        object_file = open(string_full_file_path_to_read_parameter, 'r')
    except IOError as file_error_object:
        print "\nException caught, " + file_error_object.message
        return -1
    string_line_of_data = 'not empty'
    string_local_regular_expression_hour_minute_second_parameter = \
        MockDFUDate.make_expression_match_on_hour_and_next_minute(string_hour_minute_second_parameter)
    string_match_expression_pattern = '^' + string_month_parameter + '.+?' + str(int_day_parameter) + '\s' + \
                                      string_local_regular_expression_hour_minute_second_parameter + '\s' + \
                                      string_dfu_tool_marker_parameter + '.+'
    while len(string_line_of_data) > 0:
        # Read file line by line
        string_line_of_data = object_file.readline()
        # Check if that line of input is of interest.
        result = re.match(string_match_expression_pattern, string_line_of_data)
        if result is not None:  # Skip non matches.
            # Since the regular expression matched the mask then add to list_resulting_data
            print "\nDEBUG line matched, " + string_line_of_data
            list_resulting_data_parameter.append(string_line_of_data)
    # Close file
    object_file.close()
    return 0


def wrapper_read_unix_system_log_file(string_date_time_month_day_year_hour_minute_second,
                                      string_full_file_path_to_read_parameter,
                                      string_dfu_tool_marker_parameter,
                                      list_resulting_data_parameter_out):
    """Wrapper method that formats the date time from strftime API then constructs a list of all matching messages
    in the UNIX system log file

    @PARAMETERS
    string_date_time_month_day_year_hour_minute_second - The date-time format retrieved from strftime API.

    @RETURN CODE
    0 on successful. -1 on failure.
    """
    string_month_parameter, int_day_parameter, string_hour_minute_second_parameter = \
        MockDFUDate.make_proper_date_format(string_date_time_month_day_year_hour_minute_second)
    return read_unix_system_log_file(string_full_file_path_to_read_parameter, string_month_parameter,
                                     int_day_parameter, string_hour_minute_second_parameter,
                                     string_dfu_tool_marker_parameter, list_resulting_data_parameter_out)

# string_date_time_month_day_year_hour_minute_second = strftime("%m-%d-%Y %H:%M:%S", gmtime())
# print "\nTime Now is " + str(string_date_time_month_day_year_hour_minute_second)
# string_strftime = "01-06-2017 19:39:08"
# string_full_file_path_to_read = os.path.join(os.sep, 'var', 'log', 'syslog')
# string_dfu_tool_marker = 'PerCValidation DS5_FW_Update'
# list_resulting_data = list()
# wrapper_read_unix_system_log_file(string_strftime, string_full_file_path_to_read, string_dfu_tool_marker,
#                                   list_resulting_data)
# print "\n** Resulting list **"
# for list_item in list_resulting_data:
#     print "\n" + list_item
