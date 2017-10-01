#!/usr/bin/env python3

import os
import subprocess
import re
import datetime
import pygsheets
import speedtest

try:
    from argparse import ArgumentParser as ArgParser
    from argparse import SUPPRESS as ARG_SUPPRESS
    PARSER_TYPE_INT = int
    PARSER_TYPE_STR = str
except ImportError:
    from optparse import OptionParser as ArgParser
    from optparse import SUPPRESS_HELP as ARG_SUPPRESS
    PARSER_TYPE_INT = 'int'
    PARSER_TYPE_STR = 'string'

# Set constants
DATE = datetime.datetime.utcnow().strftime("%m/%d/%y %H:%M:%S")

def get_credentials():
    """Function to check for valid OAuth access tokens."""
    gc = pygsheets.authorize(outh_file="credentials.json")
    return gc

def submit_into_spreadsheet(download, upload, ping):
    """Function to submit speedtest result."""
    gc = get_credentials()

    speedtest = gc.open(os.getenv('SPREADSHEET', 'Speedtest'))
    sheet = speedtest.sheet1

    data = [DATE, download, upload, ping]

    sheet.append_table(values=data)

def main():
    args = parse_args()
    if args.quiet:
        quiet = True
    else:
        quiet = False

    # Check for proper credentials
    printer("Checking OAuth validity...", quiet)
    credentials = get_credentials()

    # Run speedtest and store output
    printer("Starting speed test to RidgeWireless...", quiet)
    servers = [12818] # RidgeWireless id hardwired for now

    spdtest = speedtest.Speedtest()
    spdtest.get_servers(servers)
    spdtest.get_best_server()
    download = spdtest.download()
    upload = spdtest.upload()
    ping = spdtest.results.ping
    printer("Starting speed finished!", quiet)

    # Write to spreadsheet
    printer("Writing to spreadsheet...", quiet)
    submit_into_spreadsheet(download, upload, ping)
    printer("Successfuly written to spreadsheet!", quiet)

def printer(string, quiet=False, debug=False, **kwargs):
    """Helper function to print a string only when not quiet"""

    if debug and not DEBUG:
        return

    if debug:
        out = '\033[1;30mDEBUG: %s\033[0m' % string
    else:
        out = string

    if not quiet:
        print(out)


def parse_args():
    """Function to handle building and parsing of command line arguments"""
    description = (
        'Simple Python script to push speedtest results (using speedtest-cli) '
        'to a Google Docs spreadsheet\n'
        '-------------------------------------------------------------------\n')


    parser = ArgParser(description=description)
    # Give optparse.OptionParser an `add_argument` method for
    # compatibility with argparse.ArgumentParser
    try:
        parser.add_argument = parser.add_option
    except AttributeError:
        pass
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Do not output normal status messages')

    options = parser.parse_args()
    if isinstance(options, tuple):
        args = options[0]
    else:
        args = options
    return args


if __name__ == "__main__":
    main()
