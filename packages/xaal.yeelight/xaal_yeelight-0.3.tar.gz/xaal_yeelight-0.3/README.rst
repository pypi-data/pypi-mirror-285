xaal.yeelight
=============
This package provides a xAAL gateway for Yeelight lights. It support most of the Yeelight lights and bulbs.
You have to enable local control on your Yeelight device to use this package. You can do this by enabling
the "LAN Control" option in the Yeelight app.

The gateway detects the Yeelight devices on the network and creates a xAAL device for each of them. Check
*yeelight.ini* after the first run to see the devices created.


Notes
-----
This gateway doesn't use the asyncio API provides by the Yeelight library. Instead, it use gevent. This code
is a bit old, and need some refactoring to use the asyncio API. But it works well for now.
