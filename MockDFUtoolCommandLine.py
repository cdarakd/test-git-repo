#!/usr/bin/env python
import optparse  # Performs parse

__author__ = 'Charles Henri Darakdjian'
__copyright__ = 'Copyright 2016, Intel Corporation'
__maintainer__ = 'Charles Henri Darakdjian'

################################################################################
#                                                                              #
# Command-line class that inherits from Python's optparse module.              #
#                                                                              #
################################################################################


class MockDFUToolCommandLine(object):
    """Class that parses command-line parameters and adds them as attributes
    to the namespace.

    _option_parser An option parser object to be used.
    """

    def __init__(self):
        """Initialize the option parser object."""
        self._option_parser = optparse.OptionParser()

    def parse_arguments(self, list_arguments):
        """parse_arguments is a static method that uses Python's optparse module
        to parse the command-line arguments.

        @list_arguments A list of arguments (retrieved from argv commandline list.).

        RETURNS A Python tuple containing all the options as attributes of the tuple.
        Any option that was not set has its value set to None.
        """
        self._option_parser.add_option("-b", action="store")
        self._option_parser.add_option("-d", action="store")
        self._option_parser.add_option("-f", action="store_true")
        self._option_parser.add_option("-p", action="store_true")
        self._option_parser.add_option("-i", action="store")
        self._option_parser.add_option("-v", action="store_true")
        # self._option_parser.add_option("-h", action="store_true")
        tuple_options, arguments = self._option_parser.parse_args(list_arguments)
        return tuple_options  # Returns options as a Python tuple.
