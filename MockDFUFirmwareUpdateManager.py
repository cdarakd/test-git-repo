#!/usr/bin/env python
import os  # To access joining directories
import re  # To access regular expression match
import syslog  # To access UNIX system log file
import time  # To access local time on Ubuntu system
import subprocess  # To launch Linux lsusb command from terminal and capture its output
import DFUShared  # To use derived data between classes
import DFUDate
import New_DFUTestCaseFileManager  # To access UNIX system log file
__author__ = 'Charles Henri Darakdjian'
__copyright__ = 'Copyright 2016, Intel Corporation'
__maintainer__ = 'Charles Henri Darakdjian'


class DFUFirmwareUpdateManager(DFUShared.DFUShared):
    """class DFUFirmwareUpdateManager
    - Can run tool from the command line and extract its output.
    - Knows command-line options of Firmware Update tool.
    - Knows how to parse/dissect output of firmware Update tool.
    """
    def __init__(self):
        """Data members of class DFUFirmwareUpdateManager

        private
        self._usbBusNumberOfDevice - USB bus number of device (for Ubuntu).
        self._usbDeviceNumberOfDevice - USB device number of device (for Ubuntu).
        self._is_mode_recovery - set to False initially. Is set if the firmware update
        completes and the system is in recovery mode.
        self._internal_alias_ubuntu_shell_manager_object - Pointer to Ubuntu shell manager object.
        self._list_greenwich_time_tool_called - List representing the greenwich time in MM-DD-YYYY HH:MM:SS
        when the DFU tool was invoked and the greenwich time of the next minute.
        self._int_dfu_time_duration - An integer representing the estimated total time-window (in seconds) that
        messages written into the UNIX system log file can take for one invocation of the DFU tool.

        public
        self.is_error_flag_set - set when an error is found.
        self.error_message - message to display when error hit.
        """
        super(DFUFirmwareUpdateManager, self).__init__('')  # Command will be set later
        self._usb_bus_number_of_device = 0
        self._usb_device_number_of_device = 0
        self._is_mode_recovery = False
        self._internal_alias_ubuntu_shell_manager_object = None
        self._list_greenwich_time_tool_called = list()
        self._int_dfu_time_duration = 90  # Assuming that DFU tool writes messages up to 90 seconds
        #                                   apart (total) for the same invocation.
        self.is_error_flag_set = False
        self.error_message = ''
        self.return_code = -1  # 0 successful. 1 firmware update not required. 2 error

    def set_bus_number_of_device(self, usb_bus_number_of_device_parameter):
        """Mutator to set the usb bus number."""
        self._usb_bus_number_of_device = usb_bus_number_of_device_parameter

    def set_device_number_of_device(self, usb_device_number_of_device_parameter):
        """Mutator to set the device bus number."""
        self._usb_device_number_of_device = usb_device_number_of_device_parameter

    def set_internal_alias_ubuntu_shell_manager_object(self, internal_alias_ubuntu_shell_manager_object_parameter):
        """Mutator. Assigning UbuntuShellManager object (aggregation link)."""
        self._internal_alias_ubuntu_shell_manager_object = internal_alias_ubuntu_shell_manager_object_parameter

    def set_command_string(self, command_string_parameter):
        """Mutator. Setting command string of parent class."""
        super(DFUFirmwareUpdateManager, self).set_command_string(command_string_parameter)

    def generate_command_for_dfu_tool(self, string_tool_name_parameter='', string_full_file_path_of_firmware=''):
        """"""
        string_parameters = str()
        string_parameters += string_tool_name_parameter + ' '
        string_parameters += "-b "
        string_parameters += str(self._usb_bus_number_of_device)
        string_parameters += " -d "
        string_parameters += str(self._usb_device_number_of_device)
        string_parameters += " -f "
        string_parameters += " -i "
        string_parameters += string_full_file_path_of_firmware
        self.set_command_string(string_parameters)


    def launch_firmware_update_tool(self):
        """Launches the firmware update tool with specified usb bus number
        and device number. If it fails, then capture error and terminate.
        If it finishes and is in recovery mode, then search for recovery mode
        product id and relaunch the firmware update until it succeeds.
        """
        self.generate_command_for_dfu_tool(string_tool_name_parameter='./FWUpdateDS5',
                                           string_full_file_path_of_firmware=os.path.join('Firmware', 'dfu_5_3_0_43_signed.bin'))
        self.launch_firmware_update_command()

        if self.is_error_flag_set:
            return -1

        shell_object = self._internal_alias_ubuntu_shell_manager_object
        while self._is_mode_recovery:
            # If in recovery mode, then search for recovery product ID
            if not self._is_mode_recovery:
                shell_object.launch_lsusb_command('search for recovery id')
            # Else in DFU mode, then search for regular product ID
            else:
                shell_object.launch_lsusb_command('search for product id')
            string_local_bus_number = shell_object.get_bus_number()
            print "\nDebug Bus number " + string_local_bus_number
            string_local_device_number = shell_object.get_device_number()
            print "\nDebug device number " + string_local_device_number
            self.set_bus_number_of_device(string_local_bus_number)
            self.set_device_number_of_device(string_local_device_number)
            string_parameters = str()
            string_parameters += "./FWUpdateDS5 "
            string_parameters += "-b "
            string_parameters += str(self._usb_bus_number_of_device)
            string_parameters += " -d "
            string_parameters += str(self._usb_device_number_of_device)
            self.set_command_string(string_parameters)
            self.launch_firmware_update_command()
        return None

    def find_errors_from_input_line(self, input_line_parameter):
        """Uses regular expressions to extract error messages (if any) and mark update as error.

        Note: This function also may set the flag _is_mode_recovery if it
        finds the recovery product ID listed on Ubuntu command shell.
        """
        # Skip lines with newlines/carriage returns only.
        if len(input_line_parameter) < 4:
            return False
        # DEBUG
        string_match_expression = '.+?Error(.+)'  # Error string can be anywhere in the search expression
        print "DEBUG matchEXP" + string_match_expression
        print "DEBUG matchLIT" + input_line_parameter
        # Attempt the match for the vendor ID and product ID representing Intel and the ASR SD5 module.
        match_object = re.match(string_match_expression, input_line_parameter)
        # If a match is not found, then return False and quit. Good path, no error found.
        if not match_object:
            return False
        # Now, need to distinguish between normal error case (in which case must stop)
        # from recovery mode (where product ID is at 0adb) where the process must continue
        # until the firmware update succeeds.
        self._internal_alias_ubuntu_shell_manager_object.is_found_product_recovery_id = False
        self._internal_alias_ubuntu_shell_manager_object.launch_lsusb_command('search for recovery id')
        if self._internal_alias_ubuntu_shell_manager_object.is_found_product_recovery_id:
            print "\nDEBUG in recovery mode, setting mode to recovery..."
            self._is_mode_recovery = True
            return False

        # Check if in recovery mode, if so then quit with success message (return False)
        if self._internal_alias_ubuntu_shell_manager_object.is_found_recovery_id:
            print "\n DFUFirmwareUpdateManager.find_errors_from_input_line() in recovery mode..."
            return False
        # Otherwise, assign error message and mark this update as failed.
        self.is_error_flag_set = True
        self.error_message = match_object.group(1)  # Grab actual error message
        return True

    def launch_firmware_update_command(self):
        """Launches lsusb Linux command and stores output for processing.

        @RETURNS 0 on success, -1 if no messages were found for the date-time given.
        """
        string_full_file_path_to_read = os.path.join(os.sep, 'var', 'log', 'syslog')
        string_dfu_tool_marker = 'PerCValidation.+?DS5_FW_Update'  # Support any characters/spaces between
        # machine name and process name.
        list_resulting_data = list()
        process_object = None  # process_object contains handle to shell command (contains return code,
        # arguments, returned string, etc)
        try:
            list_date_time_object = time.localtime()
            process_object = subprocess.check_output(self.get_command_string(), stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as called_process_error_object:
            self.return_code = called_process_error_object.returncode
            if 2 == self.return_code:
                print "\nPossible error encountered by tool (return code is 2). investigating further..."
            string_hour_minute_second_parameter = ":".join((str(list_date_time_object[3]),
                                                            str(list_date_time_object[4]),
                                                            str(list_date_time_object[5])))
            list_time_window_to_check_for_messages = \
                DFUDate.make_expression_list_match_on_current_and_next_minute(string_hour_minute_second_parameter,
                                                                              self._int_dfu_time_duration)
            # Append the current time-frame when the DFU tool was launched and the next 90 seconds time-window
            # (as regular expressions) so that the Python wrappers can capture all messages from UNIX system log file.
            for string_time_item in list_time_window_to_check_for_messages:
                self._list_greenwich_time_tool_called.append(str(list_date_time_object[1]) + '-' +
                                                               str(list_date_time_object[2]) + '-' +
                                                               str(list_date_time_object[0]) + ' ' +
                                                               string_time_item)
            New_DFUTestCaseFileManager.wrapper_read_unix_system_log_file(self._list_greenwich_time_tool_called,
                                                                         string_full_file_path_to_read,
                                                                         string_dfu_tool_marker,
                                                                         list_resulting_data)
        max_loop_index = len(list_resulting_data)
        # Check if no messages found, in which case it is an error with this Python script.
        if 0 == max_loop_index:
            print "\nERROR: DFUFirmwareUpdateManager.launch_firmware_update_command fails probably due to " \
                  "incorrect date-time searched for. Searched for date-time, " + self._list_greenwich_time_tool_called
            print "\nAborting this test-case and moving on to next one."
            return -1

        list_standard_output = list()
        index_loop_index = 0

        while True:
            line = ''  # line of data to read
            if self.return_code > 0:
                line = list_resulting_data[index_loop_index]
            else:
                break  # Get out of loop if no errors from tool reported
            # Find error message
            if self.find_errors_from_input_line(line):
                break  # In trouble, found an error during the update process.
            list_standard_output.append(line)
            print line,
            if line == '' and process_object.poll() is not None:
                # Good path. Found no errors and finished update process.
                break
            if index_loop_index < max_loop_index - 1:
                index_loop_index += 1
            else:  # Done. Traversed entire mock array
                break
        return 0

    ################################################################
    # Mock methods to simulate Ubuntu system
    ################################################################
    # FAIL CASE (NEED TO CAPTURE ERROR MESSAGE AND SET SYSTEM TO ERROR FLAG TRUE)
    def mock_write_unix_log_file(self):
        """"""
        list_of_dfu_trace_messages = DFUFirmwareUpdateManager.mock_dfu_ubuntu_command_line_tool()
        for string_item in list_of_dfu_trace_messages:
            time.sleep(2)
            syslog.syslog(string_item)


    def mock_fail_ubuntu_command_line_tool():
        """"""
        return ['DS5 busnum = 100', 'DS5 devnum = 101',
                'DS5 FW file path =./ ds5 / fw / ds5_fw.bin',
                '', 'Error: failed to open FW file, error = -2',
                'Function: FileHandle::FileHandle(std::__cxx11::string, std::__cxx11::string)',
                'File: / home / mvenka3 / repos / perc_hw_fw_update_tools - ds5_fw_updater / DFU_FW_File.cpp:37',
                'Errno: No such file or directory(-2)']
    mock_fail_ubuntu_command_line_tool = staticmethod(mock_fail_ubuntu_command_line_tool)

    # RECOVERY MODE CASE (NORMAL OPERATION, LOOK FOR CHANGED PRODUCT ID)
    def mock_recovery_ubuntu_command_line_tool():
        """"""
        return ['DS5 busnum = 2',
                'DS5 devnum = 14',
                'DS5 FW file path = ./ds5/fw/ds5_fw.bin',
                'FW version on file = 8.8.8.8',
                'FW version on device = 5.3.0.0',
                'FW update required...',
                'Error: libusb_control_transfer failed. err = Unknown error -1']
    mock_recovery_ubuntu_command_line_tool = staticmethod(mock_recovery_ubuntu_command_line_tool)

    # DFU MODE (NORMAL OPERATION)
    def mock_dfu_ubuntu_command_line_tool():
        """"""
        return ['PerCValidation DS5_FW_Update DS5 busnum = 2',
                'DS5_FW_Update DS5 devnum = 2',
                'DS5_FW_Update DS5 FW file path = Firmware / dfu_5_3_0_43_signed.bin',
                'DS5_FW_Update FW version in file = 5.3.0.43',
                'DS5_FW_Update FW version on file = 5.3.0.68',
                'DS5_FW_Update FW update not required...',
                'DS5_FW_Update Forced update requested, attempt update.',
                'DS5_FW_Update Updating FW...',
                'DS5_FW_Update DFU FW version on file = 5.3.0.43',
                'DS5_FW_Update DFU FW status = DFU_version = 54',
                'DS5_FW_Update DFU_isLocked = 0',
                'DS5_FW_Update FW_highestVersion = 5.3.0.41',
                'DS5_FW_Update FW_lastVersion = 5.3.0.41',
                'DS5_FW_Update SerialNumber = 01234567FF01',
                'DS5_FW_Update Percentage done: 99',
                'DS5_FW_Update Running post download processes...',
                'DS5_FW_Update Post download processes done.',
                'DS5_FW_Update FW update done!']
    mock_dfu_ubuntu_command_line_tool = staticmethod(mock_dfu_ubuntu_command_line_tool)

    # Mock Recovery Mode
    def mock_firmware_tool_recovery_mode(self):
        """"""
        print "\nDEBUG in recovery mode, setting mode to recovery..."
        self._is_mode_recovery = True
        self._internal_alias_ubuntu_shell_manager_object.is_found_recovery_id = True
        print "\nDEBUG in recovery, set is_found_recovery_id flag."

# Test "mock" DFU tool.
# firmware_manager_object = DFUFirmwareUpdateManager()
# firmware_manager_object.mock_write_unix_log_file()
