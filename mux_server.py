#!/usr/bin/python3

'''
NAME:
mux_server.py

PURPOSE:
mux_server.py A server, which managers the serial port
and shares it over TCP socket with any number of clients

EXAMPLE:

./mux_server.py --device /dev/ttyUSB0 --baud 115200 --port 23200

NOTES:
    to clear the lock sudo minicom -S ttyUSB0 -o

    Defaults:
        _default_host = 'localhost'
        _default_port = 23200

        _default_device = '/dev/ttyUSB0'
        _default_baudrate = 115200
        _default_width = serial.EIGHTBITS
        _default_parity = serial.PARITY_NONE
        _default_stopbits = serial.STOPBITS_ONE
        _default_xon = False
        _default_rtc = False

'''


import sys
if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()

import argparse
import serial
import select
import socket

# To install PySerial: `sudo python3 -m pip install pyserial`


_default_host = 'localhost'
_default_port = 23200

_default_device = '/dev/ttyUSB0'
_default_baudrate = 115200
_default_width = serial.EIGHTBITS
_default_parity = serial.PARITY_NONE
_default_stopbits = serial.STOPBITS_ONE
_default_xon = False
_default_rtc = False
_default_broadcast = False

_READ_ONLY = select.POLLIN | select.POLLPRI


class mux_server():
    def __init__(self,
                 broadcast=_default_broadcast,
                 host=_default_host,
                 port=_default_port,
                 device=_default_device,
                 baudrate=_default_baudrate,
                 width=_default_width,
                 parity=_default_parity,
                 stopbits=_default_stopbits,
                 xon=_default_xon,
                 rtc=_default_rtc):
        self.host = host
        self.port = port
        self.device = device
        self.baudrate = baudrate
        self.width = width
        self.parity = parity
        self.stopbits = stopbits
        self.xon = xon
        self.rtc = rtc

        self.broadcast = broadcast

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setblocking(0)

        self.poller = select.poll()

        self.fd_to_socket = {}
        self.clients = []
        self.client_fileno_processing = None

    def close(self):
        print('\nMUX > Closing...', file=sys.stderr)

        for client in self.clients:
            client.close()
        self.tty.close()
        self.server.close()

        print('MUX > Done! =)', file=sys.stderr)

    def add_client(self, client):
        print(
            'MUX > New connection from',
            client.getpeername(),
            file=sys.stderr)
        client.setblocking(0)
        self.fd_to_socket[client.fileno()] = client
        self.clients.append(client)
        self.poller.register(client, _READ_ONLY)

    def remove_client(self, client, why='?'):
        try:
            name = client.getpeername()
        except BaseException:
            name = 'client %d' % client.fileno()
        print('MUX > Closing %s: %s' % (name, why), file=sys.stderr)
        self.poller.unregister(client)
        self.clients.remove(client)
        client.close()

    def run(self):
        try:
            self.tty = serial.Serial(
                port=self.device,
                baudrate=self.baudrate,
                bytesize=self.width,
                parity=self.parity,
                stopbits=self.stopbits,
                timeout=1,
                xonxoff=self.xon,
                rtscts=self.rtc)
            self.tty.flushInput()
            self.tty.flushOutput()
            self.poller.register(self.tty, _READ_ONLY)
            self.fd_to_socket[self.tty.fileno()] = self.tty
            print('MUX > Serial port: %s @ %s' %
                  (self.device, self.baudrate), file=sys.stderr)

            # self.server.bind((self.host, self.port))
            self.server.bind(('', self.port))
            self.server.listen(5)
            self.poller.register(self.server, _READ_ONLY)
            self.fd_to_socket[self.server.fileno()] = self.server
            print(
                'MUX > Server: %s:%d' %
                self.server.getsockname(),
                file=sys.stderr)

            print('MUX > Use ctrl+c to stop...\n', file=sys.stderr)

            while True:
                events = self.poller.poll(500)
                for fd, flag in events:
                    # Get socket from fd
                    socket = self.fd_to_socket[fd]

                    if flag & select.POLLHUP:
                        self.remove_client(socket, 'HUP')

                    elif flag & select.POLLERR:
                        self.remove_client(socket, 'Received error')

                    elif flag & (_READ_ONLY):
                        # A readable server socket is ready to accept a
                        # connection
                        if socket is self.server:
                            connection, client_address = socket.accept()

                            self.add_client(connection)

                        # Data from serial port
                        elif socket is self.tty:
                            # should we loging at this point
                            data = socket.read(1024)
                            # TODO check which client requested data
                            for client in self.clients:
                                # TODO add logger
                                print("client:{client}".format(client=client))
                                print("client.fd {}".format(client.fileno()))
                                # if broadcast set send to all interfaces
                                if self.broadcast:
                                    client.send(data)

                                elif self.client_fileno_processing == client.fileno():
                                    print("send data client.fd {}".format(client.fileno()))
                                    client.send(data)

                        # Data from client
                        # https://realpython.com/python-sockets/
                        # multiconn-server.py
                        else:
                            print("receive: {}".format(socket))
                            print("getpeername {}".format(socket.getpeername()))
                            print("processing fd receive {}".format(socket.fileno()))
                            self.client_fileno_processing = socket.fileno()

                            # TODO look for START_CMD , END_CMD 
                            # Timeout 
                            data = socket.recv(80)

                            # Client has data
                            if data:
                                self.tty.write(data)

                            # Interpret empty result as closed connection
                            else:
                                self.remove_client(socket, 'Got no data')

        except serial.SerialException as e:
            print(
                '\nMUX > Serial error: "%s". Closing...' %
                e, file=sys.stderr)

        except (KeyboardInterrupt, SystemExit):
            pass

        finally:
            self.close()


def main():

    parser = argparse.ArgumentParser(
        prog='mux_server.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
        Note:
            1. need to run as sudo since connecting to serial device
            ''',

        description='''\
NAME:
mux_server.py

PURPOSE:
mux_server.py A server, which managers the serial port
and shares it over TCP socket with any number of clients

EXAMPLE:

./mux_server.py --device /dev/ttyUSB0 --baud 115200 --port 23200

NOTES:
    to clear the lock sudo minicom -S ttyUSB0 -o

    Defaults:
        _default_host = 'localhost'
        _default_port = 23200

        _default_device = '/dev/ttyUSB0'
        _default_baudrate = 115200
        _default_width = serial.EIGHTBITS
        _default_parity = serial.PARITY_NONE
        _default_stopbits = serial.STOPBITS_ONE
        _default_xon = False
        _default_rtc = False
        ''')

    parser.add_argument('--device', help='Serial port device', default=_default_device)
    parser.add_argument('--baud', help='Baud rate', type=int, default=_default_baudrate)
    parser.add_argument('--port', help='Host port', type=int, default=_default_port)
    parser.add_argument('--broadcast', action='store_true',help='broadcast to all connected sockets')

    args = parser.parse_args()

    server = mux_server(broadcast=args.broadcast,port=args.port, device=args.device, baudrate=args.baud)
    server.run()


if __name__ == '__main__':
    main()
