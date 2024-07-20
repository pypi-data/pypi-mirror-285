#!/usr/bin/env python3
"""
Icinga2/Nagios plugin to run any number of JQ filters on JSON data, testing the
results against provided thresholds.
"""

import argparse
import logging
import os
import re
import sys
import tempfile
from pprint import pformat
from typing import Dict, Iterable, List, NamedTuple, Optional

import jq  # type:ignore
import nagiosplugin  # type:ignore
import requests  # type:ignore


def file_to_string(filepath: str) -> str:
    """
    Given a file path, put its contents into a string
    """
    try:
        with open(filepath, encoding="utf-8", mode="r") as fileobj:
            return fileobj.read()
    except FileNotFoundError as err:
        logging.debug(pformat(err))
        print(f"File not found: `{filepath}`", file=sys.stderr)
        sys.exit(3)
    except OSError as err:
        logging.debug(pformat(err))
        print(f"OS error opening file: `{filepath}`", file=sys.stderr)
        sys.exit(3)


class Thresholds(NamedTuple):
    """
    Thresholds (warn,crit)
    """

    warning: Optional[str]
    critical: Optional[str]


def thresholds_parse(thresholds: str) -> Thresholds:
    """
    Given combined thresholds into separate warning and/or critical ranges

    E.g. `w@10:19,c@20:30` -> `@10:19", `@20:30`
    """
    thresholds = thresholds.lower()

    split = thresholds.split(",")
    if 0 < len(split) > 2:
        raise ValueError(f"Invalid threshold: `{thresholds}`")

    thresh_ranges: Dict[str, Optional[str]] = {
        "critical": None,
        "warning": None,
    }
    levels: Dict[str, str] = {
        "c": "critical",
        "w": "warning",
    }
    for thresh in split:
        level = thresh[0]
        if level not in levels:
            raise ValueError(f"Invalid threshold: `{thresholds}`")
        thresh_range = thresh[1:]
        thresh_ranges[levels[level]] = thresh_range

    if not thresh_ranges:
        raise ValueError(f"No valid thresholds in `{thresholds}`")

    return Thresholds(thresh_ranges["warning"], thresh_ranges["critical"])


def parse_args(argv=None) -> argparse.Namespace:
    """Parse args"""

    usage_examples: str = """examples of use:

        # THRESHOLDS
        #
        # `THRESHOLD` should be either one or a pair of comma-separated Nagios
        # thresholds with `{c,w}` denoting their level, (e.g. `c10:20,w~:0` or
        # only `c10:20`). These ranges will be compared against the results of
        # `FILTER` to determine success.
        #
        # For more on ranges and thresholds, see Nagios Plugin Development
        # Guidelines:
        #   https://nagios-plugins.org/doc/guidelines.html


        # Run the filter `FILTER` on the given JSON file. WARN if `FILTER` does
        # not match specified range. Use the result of `FILTER` for perfdata.

        %(prog)s --filter 'LABEL' 'FILTER' 'w@10:20' /path/to/jsonfile

        # As above, but also add a critical range

        %(prog)s --filter 'LABEL' 'FILTER' 'w@10:20,c@30:40' /path/to/jsonfile

        # Run multiple filters

        %(prog)s \\
            --filter 'LABEL1' 'FILTER1' 'w~:10,c~:20' \\
            --filter 'LABEL2' 'FILTER2' 'w~:10,c~:20' \\
            /path/to/jsonfile

        # The source can also be an HTTP/S URI

        %(prog)s --filter 'LABEL' 'FILTER' 'w@10:20' http://domain.tld/path

    """
    descr: str = """
        Icinga2/Nagios plugin to run any number of JQ filters on JSON data,
        testing the results against provided thresholds.

        Refer to the JQ Manual for for your version of libjq, for all of the
        things you can do in a filter:
        https://stedolan.github.io/jq/manual/
        """
    parser = argparse.ArgumentParser(
        description=descr,
        epilog=usage_examples,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--filter",
        "-f",
        action="append",
        dest="filters",
        help=("Defines a filter, its name, and thresholds."),
        metavar=(
            "LABEL",
            "FILTER",
            "THRESHOLDS",
        ),
        nargs=3,
        type=str,
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        dest="verbosity",
        help="Set output verbosity (-v=warning, -vv=debug)",
    )

    parser.add_argument(
        "jsonsrc",
        action="store",
        help="The path to the file to inspect",
        metavar="jsonsrc",
        type=str,
    )

    args = parser.parse_args(argv) if argv else parser.parse_args()

    if not args.filters:
        parser.error("At least one `--filter` is required.")

    if args.verbosity >= 2:
        log_level = logging.DEBUG
    elif args.verbosity >= 1:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    logging.basicConfig(level=log_level)

    return args


# pylint: enable=too-few-public-methods


class Filter(NamedTuple):
    """
    Filter
    """

    label: str
    test_filter: str
    thresholds: str


class JsonFile(nagiosplugin.Resource):
    """
    Determines if filters succeed or fail on the given JSON file
    """

    def __init__(self, *, filters: Iterable[Iterable[str]], filepath: str):
        """
        Record filters and ingest JSON file
        """
        self.json: str = file_to_string(filepath)
        self.filters: List[Filter] = []
        self.contexts: List[nagiosplugin.ScalarContext] = []
        for label, test_filter, thresholds in filters:
            self.filters.append(
                Filter(
                    label,
                    test_filter,
                    thresholds,
                )
            )
            parsed_thresholds = thresholds_parse(thresholds)
            self.contexts.append(
                nagiosplugin.ScalarContext(
                    label,
                    warning=parsed_thresholds.warning,
                    critical=parsed_thresholds.critical,
                )
            )
            logging.debug("Readied nagiosplugin context for filter: %s", label)
        logging.debug("Readied filters: %s", pformat(self.filters))

    def probe(self):
        for filt in self.filters:
            compiled_test_filt = jq.compile(filt.test_filter)
            try:
                filter_result = compiled_test_filt.input(text=self.json).first()
                logging.info(
                    "Ran test filter `%s` on JSON. Result: `%s`",
                    filt.label,
                    filter_result,
                )
                yield nagiosplugin.Metric(filt.label, filter_result, context=filt.label)
            except StopIteration:
                return


@nagiosplugin.guarded
def main():
    """Main"""
    args = parse_args(sys.argv[1:])
    logging.debug("Argparse results: %s", pformat(args))

    if os.path.isfile(args.jsonsrc):
        logging.info("Source for the JSON will be the file `%s`", args.jsonsrc)
        filepath = args.jsonsrc
    elif re.search("^https?://", args.jsonsrc.lower()):
        logging.info("Source for the JSON will be the URI `%s`", args.jsonsrc)
        with tempfile.NamedTemporaryFile(delete=False) as tfile:
            try:
                res = requests.get(args.jsonsrc, timeout=5)
                tfile.write(res.text.encode())
                filepath = tfile.name
            except requests.exceptions.RequestException as err:
                print("Failed querying JSON source URI", file=sys.stderr)
                raise err
    else:
        raise TypeError(
            f"Given JSONSRC (`{args.jsonsrc}`) is neither a file nor a URI."
        )

    jsonfile = JsonFile(filters=args.filters, filepath=filepath)
    check = nagiosplugin.Check(jsonfile, *jsonfile.contexts)
    check.main(args.verbosity)


if __name__ == "__main__":
    main()
