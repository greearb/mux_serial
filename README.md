# mux_serial

Python3 Serial port multiplexer over TCP 


## What?

This is a set of simple utilities used to let several programs share access to a device connected to a single serial port.
Included:
* A server, which manages the serial port and shares it over TCP with any number of clients;
* a client, used to interact with the connected device (either via text terminal or via script);
* and a logger, which receives a copy of everything going through the serial port and timestamps it and echo to a terminal


## So, how?

The way I use it:

1. Launch the server:
  ```bash
user@user:~/git/mux_serial$ sudo ./mux_server.py 
MUX > Serial port: /dev/ttyUSB0 @ 115200
MUX > Server: 0.0.0.0:23200
MUX > Use ctrl+c to stop...

MUX > New connection from ('127.0.0.1', 33292)
MUX > New connection from ('192.168.0.154', 43786)
MUX > New connection from ('192.168.0.166', 39588)

  ```

2. Then connect any number of clients, will open and simple telnet interface:
  ```bash
user@user:~/git/mux_serial$ ./mux_client.py --host 'localhost' --port 23200
MUX > Connected to localhost:23200
MUX > Use ctrl+c to stop ..

pwd
/home/lanforge
[lanforge@ct523c-3ba3 ~]$ 

  ```

3. ...and the logger:
  ```bash
user@user:~/git/mux_serial$ ./mux_logger.py --host "local_host" --port 23200 --file log_file.txt
MUX > Logging output to log_file.txt
MUX > Connected to localhost:23200
MUX > format: [date time elapsed delta] line
MUX > Use ctrl+c to stop...

[2021-11-04 10:28:15 0.000 0.000] pwd
[2021-11-04 10:28:15 0.000 0.000] /home/lanforge

  ```

4. mux_test.py is a sample program using the mux_client as a module
  ```bash
user@user:~/git/mux_serial$ ./mux_test.py --host 'localhost' --port 23200 --cmd "pwd"
send cmd: pwd, adding "
" 
read wait for prompt: ]$
b'pwd\r\n/home/lanforge\r\n[lanforge@ct523c-3ba3 ~]$'
user@user:~/git/mux_serial$ 

  ```

Some useful info:
* There are defaults set if parameters not entered such as  `/dev/ttyUSB0` at `115200` served at `localhost:23200`;

* The server can accept clients from local host and remote systems

* The client is built on top of the `telnetlib` module;


## But why? - Needed Python3 version

Ability to have multiple clients and logger to a single serial device.  Also the ability to have a python3 module
to allow access to send commands


## Credits

Original code in python2 is found at https://github.com/marcelomd/mux_serial


