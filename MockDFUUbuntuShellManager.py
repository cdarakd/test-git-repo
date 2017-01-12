#!/usr/bin/env python
import subprocess  # To launch Linux lsusb command from terminal and capture its output
import re  # To access regular expression match
import MockDFUShared  # To use derived data between classes
__author__ = 'Charles Henri Darakdjian'
__copyright__ = 'Copyright 2016, Intel Corporation'
__maintainer__ = 'Charles Henri Darakdjian'


class MockDFUUbuntuShellManager(MockDFUShared.MockDFUShared):
    """
    - Can run shell commands from the command line and extract its output.
    - Knows (some) command-line options of lsusb command.
    - Knows how to parse/dissect output of lsusb command.
    """
    def __init__(self, command_parameter, vendor_id_parameter, product_id_parameter, recovery_product_id_parameter):
        """Data members of DFUUbuntuShellManager

        self._vendor_id - a vendor ID alphanumeric representing the company
        self._product_id - a product ID alphanumeric representing the device
        self._recovery_product_id - a product ID alphanumeric representing the device when the
        system is in recovery mode (it is in the middle of a firmware update).
        self.is_found_product_recovery_id - sets to True if the product ID/recovery ID to search
        is found.
        """
        super(MockDFUUbuntuShellManager, self).__init__(command_parameter)
        self._vendor_id = vendor_id_parameter
        self._product_id = product_id_parameter
        self._recovery_product_id = recovery_product_id_parameter
        self.is_found_recovery_id = False

        self.is_error_flag_set = False
        self.error_message = ''

    def find_ids_from_input_line(self, input_line_parameter, string_search_target):
        """Uses regular expressions to extract the bus ID and device ID (if any).

        @PARAMETERS
        input_line_parameter - A line of input to search through.
        string_search_target - A string marking the type of product ID to use (i.e.,
        either in DFU mode or in recovery mode). If 'search for recovery id'
        then seach _product_id
        if 'search for product id' then search _recovery_product_id

        @RETURNS True if ID found. Otherwise False.
        """
        # Skip lines with newlines/carriage returns only.
        if len(input_line_parameter) < 4:
            return False
        is_in_recovery = False
        if string_search_target.__eq__('search for product id'):
            print "\nDEBUG Search for PRODUCT id"
            string_match_expression = 'Bus (\d\d\d) Device (\d\d\d): ID ' + self._vendor_id + ':' + \
                                      self._product_id + ' .+'
        elif string_search_target.__eq__('search for recovery id'):
            print "\nDEBUG Search for RECOVERY id"
            is_in_recovery = True
            string_match_expression = 'Bus (\d\d\d) Device (\d\d\d): ID ' + self._vendor_id + ':' + \
                                      self._recovery_product_id + ' .+'
        else:
            print "\nError DFUFirmwareUpdateManager.find_ids_from_input_line function fails!"
            return True
        print "DEBUG matchEXP" + string_match_expression
        print "DEBUG matchLIT" + input_line_parameter
        # Attempt the match for the vendor ID and product ID representing Intel and the ASR SD5 module.
        match_object = re.match(string_match_expression, input_line_parameter)
        # If a match is not found, then return False and quit.
        if not match_object:
            return False
        # If in recovery mode and found recovery id, then set found recovery id flag to true.
        if is_in_recovery:
            self.is_found_recovery_id = True
            print "\nDEBUG in recovery, set is_found_recovery_id flag."
        # Otherwise, remove the leading zeros and assign the appropriate data
        # to the bus number and device number.
        self.set_bus_number(str(match_object.group(1)).lstrip("0"))
        self.set_device_number(str(match_object.group(2)).lstrip("0"))
        return True

    def launch_lsusb_command(self, string_search_target):
        """Launches lsusb Linux command and stores output for processing.

        string_search_target if 'search for recovery id' then seach _product_id
        if 'search for product id' then search _recovery_product_id
        """
        local_command_string = self.get_command_string()
        print "\nMock command: " + local_command_string
        line = 'Bus 002 Device 003: ID 8086:0ad1 Intel Corp.'
        self.find_ids_from_input_line(line, string_search_target)
        return None

    def get_bus_number(self):
        """Accessor to retrieve (private) bus number"""
        return self._bus_number

    def get_device_number(self):
        """Accessor to retrieve (private) device number"""
        return self._device_number

    def get_command_string(self):
        """Accessor to retrieve command string from parent class."""
        return super(MockDFUUbuntuShellManager, self).get_command_string()
