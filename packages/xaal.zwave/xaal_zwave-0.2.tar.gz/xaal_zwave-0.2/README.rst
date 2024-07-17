
xaal.zwave
==========
This package provides a gateway to connect Zwave devices to the xAAL.
It uses the openzwave library to communicate with the Zstick.
As the openzwave library is outdated, it is recommended to use an old
version of Python (tested w/ 3.8.12) to run this gateway.


Install & Config
----------------
- Install the gateway as usual, *pip install xaal.zwave*
- Plug the Zstick
- Run the gateway w/ *python -m xaal.zwave*
- Change the serial port in the config file *zwave.ini* if needed.
- The gateway will detect all paired products with the Zstick so, no
  addtionnal config is needed

Products
--------
- Supported products are in products/, feel free to add (and submit)
  your own devices.
