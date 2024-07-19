""" I check websites
"""


import argparse
import sys


import requests


def _options() -> object:
    """ I provide the argparse option set.

        Returns
            argparse parser object.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--site',
                        required=True,
                        help='the url to check')
    parser.add_argument('--auth',
                        required=False,
                        default='',
                        help='the user:password')
    parser.add_argument('--codes',
                        required=False,
                        default='200',
                        help='a commalist of accepted return codes')
    return parser.parse_args()



def main():
    """ I am the main body of the script

        ExitCodes:
        0 - Service is OK.
        1 - Service has a WARNING.
        2 - Service is in a CRITICAL status.
        3 - Service status is UNKNOWN.
    """
    args = _options()
    kwargs = {}
    if args.auth:
        kwargs['auth'] = tuple(args.auth.split(':'))

    try:
        if kwargs:
            result = requests.get(args.site, **kwargs)
        else:
            result = requests.get(args.site, **kwargs)
    except:
        print('requests failed')
        sys.exit(2)

    print(f'exit code {result.status_code}')
    if str(result.status_code) in args.codes.split(','):
        sys.exit(0)

    sys.exit(2)


if __name__ == '__main__':
    main()