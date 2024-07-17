import argparse
import logging
import sys

from taichu_storage.copy import copy

logger = logging.getLogger(__name__)


def cli():
    parser = argparse.ArgumentParser(description="""Taichu Storage Tools""")
    parser.add_argument('action', action="store", choices=['cp'])
    parser.add_argument('source', action="store", type=str)
    parser.add_argument('destination', action="store", type=str)
    parser.add_argument('--ak', required=False, action="store",
                        help="""Specify the access key""")
    parser.add_argument('--sk', required=False, action="store", type=str,
                        help="""Specify the secret key""")
    parser.add_argument('--endpoint', required=False, action="store", type=str,
                        help="""Specify the endpoint""")
    parser.add_argument('--retry_times', required=False, default=3, action="store", type=int,
                        help="""Specify the retry times""")

    args = parser.parse_args()

    if args.source is None or args.destination is None:
        logger.info("Please specify both source and destination")
        sys.exit(1)
    retry_times = args.retry_times
    if retry_times and retry_times <= 0:
        retry_times = 100000

    logger.info("Copying {} to {}".format(args.source, args.destination))
    copy(args.source, args.destination, retry_times=retry_times)


if __name__ == '__main__':
    cli()
