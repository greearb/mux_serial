#!/usr/bin/python3

import sys
import socket
import argparse
import time

'''
NAME:
mux_logger.py

PURPOSE:
a logger for a mux serial interface

EXAMPLE:
./mux_logger.py --host "local_host" --port 23200 --file log_file.txt

NOTES:
    Defaults:
        _default_host = 'localhost'
        _default_port = 23200
        _default_file = 'mux_log.txt'
 '''

_default_host = 'localhost'
_default_port = 23200
_default_file = 'mux_log.txt'


class mux_logger():
    def __init__(self,
                 host=_default_host,
                 port=_default_port,
                 log_file=_default_file):
        self.host = host
        self.port = port
        self.logname = log_file
        self.log = None
        self.socket = None

    def flush(self):
        sys.stdout.flush()

    def write_simple(self, x):
        sys.stdout.write()

    def write_log(self, x):
        sys.stdout.write(x)
        self.log.write(x)
        self.log.flush()

    def close(self):
        print('\nMUX logger > Closing...', file=sys.stderr)

        self.socket.close()
        self.log.close()

        print('MUX logger > Done! =)', file=sys.stderr)

    def start_log(self):
        # Setup log file writing
        self.log = open(self.logname, 'w')  # writing bytes
        print('MUX > Logging output to', self.logname, file=sys.stderr)

        # Setup client
        server_address = ('localhost', self.port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(server_address)

        print('MUX > Connected to %s:%d' % server_address, file=sys.stderr)
        print('MUX > format: [date time elapsed delta] line', file=sys.stderr)
        print('MUX > Use ctrl+c to stop...\n', file=sys.stderr)

        # Init line catcher
        base_t = 0
        line_t = 0
        prev_t = 0

        newline = True
        current_line = ''

        # MAIN
        try:
            while True:

                # Read 1 char
                x = self.socket.recv(1)

                # Ignore carriage returns
                if x == '\r':
                    continue

                # Set base_t to when first char is received
                if not base_t:
                    base_t = time.time()

                if newline:
                    line_t = time.time()
                    date = time.localtime(line_t)
                    elapsed = line_t - base_t
                    delta = elapsed - prev_t
                    self.write_log(
                        '[%04d-%02d-%02d %02d:%02d:%02d %4.3f %4.3f] ' %
                        (date.tm_year,
                         date.tm_mon,
                         date.tm_mday,
                         date.tm_hour,
                         date.tm_min,
                         date.tm_sec,
                         elapsed,
                         delta))
                    prev_t = elapsed
                    newline = False

                # if there is a crash will get up to crash
                self.write_log(str(x, 'utf-8'))
                current_line += str(x, 'utf-8')

                if x == b'\n':
                    newline = True
                    current_line = ''

        except Exception as e:
            print(e)

        except (KeyboardInterrupt, SystemExit):
            pass

        finally:
            self.close()


def main():

    parser = argparse.ArgumentParser(
        prog='mux_logger.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
        Useful Information:
            1. Useful Information goes here
            ''',

        description='''\
serial_mux_logger.py:
--------------------
Default port 23200

Summary :
----------
a logger for a mux serial interface


Generic command layout:
-----------------------
./mux_logger.py --host "local_host" --port 23200 --file log_file.txt

        ''')
    parser.add_argument('--host',
                        help='Host',
                        default=_default_host)

    parser.add_argument('--port',
                        help='Host port',
                        type=int,
                        default=_default_port)

    parser.add_argument('--file',
                        help='--file <log file>',
                        default=_default_file)

    args = parser.parse_args()

    logger = mux_logger(
        host=str(
            args.host), port=int(
            args.port), log_file=args.file)
    logger.start_log()


if __name__ == '__main__':
    main()
