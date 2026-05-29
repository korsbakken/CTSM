"""Functions implementing the download_input_data command for mksurfdata"""

import argparse
import logging
import os
import re

from CIME.case import Case  # pylint: disable=import-error

from ctsm.ctsm_logging import setup_logging_pre_config, add_logging_args, process_logging_args

logger = logging.getLogger(__name__)

# ========================================================================
# Define some constants
# ========================================================================

# In surfdata.namelist, file names match this pattern:
_FILENAME = r" = '/"

# ========================================================================
# Public functions
# ========================================================================


def main():
    """Main function called when download_input_data is run from the command-line"""
    setup_logging_pre_config()
    args = _commandline_args()
    process_logging_args(args)

    download_input_data(rundir=args.rundir, dummycasedir=args.dummycasedir)


def download_input_data(rundir, dummycasedir):
    """Implementation of the download_input_data command

    Args:
    rundir: str - path to directory containing .input_data_list file
    dummycasedir: str - path to a directory with any existing valid case
    """
    _create_input_data_list(rundir)
    # TODO Remove hardwiring
    case = Case(os.path.realpath(dummycasedir))
    case.check_all_input_data(data_list_dir=rundir, download=True, chksum=False)
    os.remove(os.path.join(rundir, ".input_data_list"))


# ========================================================================
# Private functions
# ========================================================================


def _commandline_args():
    """Parse and return command-line arguments"""

    description = """
Script to download any missing input data for mksurfdata_esmf
"""

    parser = argparse.ArgumentParser(
        description=description, formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "--dummycasedir",
        required=True,
        help=(
            "Path to the directory of any existing case created for the host "
            "machine. This is temporarily required since this preliminary "
            "version of `mksurfdata_download_input_data` uses functionality "
            "from the `CIME.case.Case` class, and needs to create an instance "
            "of that class to run. The content of the case directory does not "
            "matter, as long as long as it is a valid case for the host "
            "machine."
        ),
    )
    parser.add_argument(
        "--rundir",
        default=os.getcwd(),
        help="Full path of the run directory\n"
        "(This directory should contain .input_data_list and surfdata.namelist,\n"
        "among other files.)\n"
        "(Note: it is assumed that this directory exists alongside the other\n"
        "directories created by build_ctsm: 'case' and 'inputdata'.)",
    )

    add_logging_args(parser)

    args = parser.parse_args()

    return args


def _create_input_data_list(rundir):
    with open(os.path.join(rundir, "surfdata.namelist"), encoding="utf-8") as namelist:
        with open(
            os.path.join(rundir, ".input_data_list"), "w", encoding="utf-8"
        ) as input_data_list:
            for line in namelist:
                if re.search(_FILENAME, line):
                    # Remove quotes from filename, then output this line
                    line = line.replace('"', "")
                    line = line.replace("'", "")
                    input_data_list.write(line)
