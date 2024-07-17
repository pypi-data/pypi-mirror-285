
xaal.aqara
==========
This is a xAAL gateway for the Aqara Gateway (hub) from Xiaomi.
The gateway is able to discover and control most Aqara devices.



Install & Config
----------------
- Enable local network on the Aqara Gateway with the Mi Home
  Android or iOS app. You can follow this manual: `Domoticz Wiki`_.
  Search for the key and save it.
- Run the xAAL gateway with: *python -m xaal.aqara*. The gateway
  should detect all Aqara devices on your local network.
- To enable quick discovery and control devices (switches, leds..)
  edit the config file *~/.xaal/aqara.ini* and add the key
  like this:

.. code-block:: ini

    [devices]
        [[xxxxxxxxxxxx]]
        base_addr = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxx
        model = gateway
        secret = ydt5xis45x7k5x1x


Notes
-----
- xAAL gateway supports more than one Aqara Gateway (hub) on the
  network make sure to set a secret key to each hub.
- xAAL gateway supports most Aqara devices, feel free to edit (and
  submit) xaal/aqara/devices.py if you own a unsupported device.

.. _Domoticz Wiki: https://www.domoticz.com/wiki/Xiaomi_Gateway_(Aqara)
