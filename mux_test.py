#!/usr/bin/python3

'''
NAME:
mux_test.py

PURPOSE:
a test for the mux_client module

'''

import sys
if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()

import mux_client
import argparse

_default_host = 'localhost'
_default_port = 23200


def main():

    parser = argparse.ArgumentParser(
        prog='mux_test.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
        mux_test.py:

            ''',

        description='''\
NAME:
mux_test.py

PURPOSE:
a test program to test mux_client

EXAMPLE:
./mux_test.py --host "local_host" --port 23200 --cmd "pwd"

NOTES:
    Defaults:
        _default_host = 'localhost'
        _default_port = 23200

        ''')
    parser.add_argument('--host',
                        help='Host',
                        default=_default_host)

    parser.add_argument('--port',
                        help='Host port',
                        type=int,
                        default=_default_port)

    parser.add_argument('--cmd',
                        help='--cmd "pwd"',
                        default="pwd")

    parser.add_argument('--prompt',
                        help='--prompt "]$"',
                        default="]$")

    args = parser.parse_args()

    client = mux_client.mux_client(host=str(args.host), port=int(args.port))
    client.start_telnet()
    print('send cmd: {cmd}, adding "\r\n" '.format(cmd=args.cmd))
    command = args.cmd + "\r\n"
    client.write_str(command)
    print("read wait for prompt: {prompt}".format(prompt=args.prompt))
    info = client.read_until(args.prompt)
    print(info)

    client.close_silent()


if __name__ == '__main__':
    main()
