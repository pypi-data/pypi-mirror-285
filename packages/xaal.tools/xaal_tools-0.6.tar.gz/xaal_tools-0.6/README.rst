
xaal.tools
==========
A collection of tools for working with the xAAL bus.

This package contains the following tools:
  - xaal-isalive
  - xaal-info
  - xaal-walker
  - xaal-dumper
  - xaal-log
  - xaal-querydb
  - xaal-cleandb
  - xaal-send
  - xaal-tail
  - xaal-pkgrun
  - xaal-keygen
  - xaal-uuidgen
  - xaal-shell

Usage
-----
All tools have a help option (-h) that can be used to get more information about. For example:

  .. code:: shell

    Usage: xaal-isalive [options]

    Options:
    -h, --help      show this help message and exit
    -c              disable color
    -l              Enable logging
    -a MCAST_ADDR   Multicast address
    -p MCAST_PORT   Multicast port
    -t FILTER_TYPE  only show given device type


Details
-------

xaal-isalive
~~~~~~~~~~~~
This tool is used to check if a device is alive on the xAAL bus, by sending a isAlive request to the devices

xaal-info
~~~~~~~~~
This tool is used to get information about a device, by requesting description / attributes / metadata.

xaal-walker
~~~~~~~~~~~
This tool is used to walk the xAAL bus and get information about all devices.

xaal-dumper
~~~~~~~~~~~
This tool is used to dump messages from the xAAL bus.

xaal-log
~~~~~~~~
This tool is used to log attributes changed.

xaal-querydb
~~~~~~~~~~~~
This tool is used to query the metadata database.

xaal-cleandb
~~~~~~~~~~~~
This tool is used to clean the metadata database.

xaal-send
~~~~~~~~~
This tool is used to send a message (request) on the xAAL bus.

xaal-tail
~~~~~~~~~
This tool provide a tail-like event logging.

xaal-pkgrun
~~~~~~~~~~~
This tool is used to run packages (for example a gateway). It will load the package and run it.
Example: xaal-pkgrun owm knx

xaal-keygen
~~~~~~~~~~~
This tool is used to generate a key for the xAAL bus.

xaal-uuidgen
~~~~~~~~~~~~
This tool is used to generate a UUID.

xaal-shell
~~~~~~~~~~
This tool is used to start a ipython interpreter with xAAL tools loaded.
