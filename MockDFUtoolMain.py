#!/usr/bin/env python
import sys  # System module of Python
import MockDFUtoolCommandLine  # DFU tool's command-line parser
import MockDFUFirmwareUpdateManager  # DFU tool's calls firmware tool
import MockDFUUbuntuShellManager  # DFU tool's calls 'lsusb' Linux command and finds device needed

__author__ = 'Charles Henri Darakdjian'
__copyright__ = 'Copyright 2016, Intel Corporation'
__maintainer__ = 'Charles Henri Darakdjian'
is_mock_system = False

################################################################################
#                                                                              #
# Main class and entry point for Device Firmware Upgrade (DFU) tool.           #
#                                                                              #
################################################################################


class MockDFUToolMain(object):
    """Main class and entry point for Device Firmware Upgrade (DFU) tool."""
    def __init__(self):
        """Data members of class

        _list_usb_bus_numbers A list of bus numbers (each representing a
        connected device).

        _list_usb_device_numbers A list of device numbers (each representing a
        connected device).

        _bool_is_force_firmware_update A boolean to force an upgrade on all
        connected devices.

        _bool_is_print_firmware_version A boolean to print the firmware
        version and exit.

        _string_path_firmware_file A string to represent the firmware file.

        _bool_is_print_firmware_update_tool_version A string to represent
        the firmware update tool version. This program exits afterwards.

        _bool_is_display_help_banner A string to display the help banner
        and exit.
        """
        self._list_usb_bus_numbers = []
        self._list_usb_device_numbers = []
        self._bool_is_force_firmware_update = False
        self._bool_is_print_firmware_version = False
        self._string_path_firmware_file = ''
        self._bool_is_print_firmware_update_tool_version = False
        self._bool_is_display_help_banner = False

    def set_option_values(self, tuple_of_options):
        """"""
        # Branch depending on tuple attribute provided (command-line option).
        if tuple_of_options.b is not None:
            self._list_usb_bus_numbers.append(tuple_of_options.b)

        if tuple_of_options.d is not None:
            self._list_usb_device_numbers.append(tuple_of_options.d)

        if tuple_of_options.f is not None:
            self._bool_is_force_firmware_update = True

        if tuple_of_options.p is not None:
            self._bool_is_print_firmware_version = True

        if tuple_of_options.i is not None:
            self._string_path_firmware_file = tuple_of_options.i

        if tuple_of_options.v is not None:
            self._bool_is_print_firmware_update_tool_version = True

        if tuple_of_options.v is not None:
            self._bool_is_display_help_banner = True

        if tuple_of_options.h is not None:
            self._bool_is_display_help_banner = True

    def do_firmware_upgrade(self):
        """Main method to do the full upgrade process."""
        # First, calls command-line class to extract and assign the
        # command-line parameters given. (they will be added as
        # attributes to the namespace.
        my_command_line_object = MockDFUtoolCommandLine.MockDFUToolCommandLine()
        dictionary_of_options = my_command_line_object.parse_arguments(sys.argv[1:])
        # Retrieve attributes and carry on.
        self.set_option_values(dictionary_of_options)

        # TODO: Check if some flags have been set, in which case display the appropriate data and terminate.

        self._list_usb_bus_numbers = 1

        # TODO: Otherwise, continue with upgrade process.

    def do_firmware_upgrade_with_usb_number_and_device_number(self):
        """Handles \"normal\" test-case where the tool is given a valid
        usb number and device number (retrieved from lsusb Linux command.
        """
        # This object is setup to execute 'lsusb' Linux command for vendor ID "8086" and product ID "0ad1"
        shell_object = MockDFUUbuntuShellManager.MockDFUUbuntuShellManager("lsusb", "8086", "0ad1", "0adb")
        if is_mock_system:
            string_local_bus_number = '002'
            print "\nDebug Bus number " + string_local_bus_number
            string_local_device_number = '002'
            print "\nDebug device number " + string_local_device_number
        else:
            shell_object.launch_lsusb_command('search for product id')
            string_local_bus_number = shell_object.get_bus_number()
            print "\nDebug Bus number " + string_local_bus_number
            string_local_device_number = shell_object.get_device_number()
            print "\nDebug device number " + string_local_device_number
        firmware_object = MockDFUFirmwareUpdateManager.MockDFUFirmwareUpdateManager()
        firmware_object.set_bus_number_of_device(string_local_bus_number)
        firmware_object.set_device_number_of_device(string_local_device_number)
        # Pass reference to Ubuntu shell manager and reuse it when process runs.
        firmware_object.set_internal_alias_ubuntu_shell_manager_object(shell_object)
        firmware_object.launch_firmware_update_tool()
        if firmware_object.is_error_flag_set:
            print "\nERROR flag set in DFUFirmwareUpdateManager class, specific error message follows,\n"
            print firmware_object.error_message
        else:
            print "\nFirmware tool completed successfully."

if '__main__' == __name__:
    my_main_object = MockDFUToolMain()
    my_main_object.do_firmware_upgrade_with_usb_number_and_device_number()
