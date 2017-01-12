#!/usr/bin/env python
__author__ = 'Charles Henri Darakdjian'
__copyright__ = 'Copyright 2016, Intel Corporation'
__maintainer__ = 'Charles Henri Darakdjian'


class MockDFUShared(object):
    def __init__(self, command_string_parameter=''):
        """Data members of MockDFUShared - default constructor.

        self._command_string - a Linux command for the Ubuntu shell.
        self._bus_number - a USB bus number of the vendor ID, product ID pair.
        self._device_number - a USB device number of the vendor ID, product ID pair.
        """
        self._command_string = command_string_parameter
        self._bus_number = 0
        self._device_number = 0

    # Mutators.
    def set_command_string(self, command_parameter):
        """"""
        self._command_string = command_parameter

    def set_bus_number(self, bus_number_parameter):
        """"""
        self._bus_number = bus_number_parameter

    def set_device_number(self, device_number_parameter):
        """"""
        self._device_number = device_number_parameter

    # Accessors.
    def get_command_string(self):
        """"""
        return self._command_string

    def get_bus_number(self):
        """"""
        return self._bus_number

    def get_device_number(self):
        """"""
        return self._device_number
