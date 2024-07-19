#!/usr/bin/env python3

from orsm import cli
from orsm.variables import variable_names_and_objects
from orsm.logger import log
from time import sleep


def main(**kwargs):
    for name, logger in variable_names_and_objects(log.trace, log.debug, log.info, log.print, log.warning, log.error, log.critical, vars_only=True):
        sleep(0.01)  # So we can see the timestamp increments more clearly.
        logger(f"A message from {name}")


if __name__ == "__main__":
    parser = cli.setup_standard_parser()
    kwargs = vars(parser.parse_args())
    main(**kwargs)
