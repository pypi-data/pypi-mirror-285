import argparse
import importlib
import logging
import sys

from gql.transport.aiohttp import log as aiohttp_logger

from pypanther import testing, upload
from pypanther.custom_logging import setup_logging
from pypanther.vendor.panther_analysis_tool import util
from pypanther.vendor.panther_analysis_tool.command import standard_args
from pypanther.vendor.panther_analysis_tool.config import dynaconf_argparse_merge, setup_dynaconf


def run():
    setup_logging()

    parser = setup_parser()
    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        return

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        aiohttp_logger.setLevel(logging.WARNING)

    config_file_settings = setup_dynaconf()
    dynaconf_argparse_merge(vars(args), config_file_settings)

    try:
        return_code, out = args.func(args)
    except util.BackendNotFoundException as err:
        logging.error('Backend not found: "%s"', err)
        return 1
    except Exception as err:  # pylint: disable=broad-except
        # Catch arbitrary exceptions without printing help message
        logging.warning('Unhandled exception: "%s"', err, exc_info=err, stack_info=True)
        logging.debug("Full error traceback:", exc_info=err)
        return 1

    if return_code > 0 and out:
        logging.error(out)
    elif return_code == 0 and out:
        logging.info(out)

    sys.exit(return_code)


def setup_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Command line tool for uploading files.",
        prog="pypanther",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--debug", action="store_true", dest="debug")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Upload command
    upload_parser = subparsers.add_parser(
        "upload", help="Upload a file", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    standard_args.for_public_api(upload_parser, required=False)
    upload_parser.set_defaults(func=util.func_with_backend(upload.run))
    upload_parser.add_argument(
        "--max-retries",
        help="Retry to upload on a failure for a maximum number of times",
        default=10,
        type=int,
        required=False,
    )
    upload_parser.add_argument(
        "--skip-tests",
        help="Skip running tests and go directly to upload",
        default=False,
        required=False,
        action="store_true",
    )
    upload_parser.add_argument(
        "--confirm",
        help="Proceed with the upload without requiring user input",
        default=False,
        required=False,
        action="store_true",
    )

    # Test command
    test_parser = subparsers.add_parser(
        "test", help="run tests", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    test_parser.set_defaults(func=testing.run)

    # Version command
    version_parser = subparsers.add_parser(
        "version", help="version", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    version_parser.set_defaults(func=version)

    return parser


def version(args):
    print(importlib.metadata.version("pypanther"))
    return 0, ""


if __name__ == "__main__":
    run()
