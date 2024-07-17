xaal.tuya
=========
This package provides a gateway to control Tuya devices from xAAL network.

Tuya protocol is the common protocol used in cheap chinese outlets, smart plugs,
and RGB lamps. It use the cloud base "Smart Life" mobile application (Android/IOS).

This protocol isn't really reliable. If you can, avoid the use of Smart Life APP
when this gateway is running. This should be ok, but attributes can be out of
sync. The gateway polls devices state every 45 seconds but due to socket error,
this can be a little longuer.


The complete guide to extract keys is there:
https://github.com/codetheweb/tuyapi/blob/master/docs/SETUP.md

Notes :
The main issue is that tuya devices close every connection after 10 seconds.

Supported devices
-----------------
The gateway supports: PowerRelays (from 1 to x relais), SmartPlugs (same as relais
but with a single power-meter), lamps and RGB lamps

Configuration samples
---------------------

- Dimmer Lamp / LSC Smart filament

.. code-block::

   [[device_id]]
    ip = 192.168.1.x
    key = xxxxxxxxxxxxxxxx
    type = lamp_dimmer
    white_temp = 1800, 2700  # for LSC
    addr = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

- RGB Lamp / LSC RGB1

.. code-block::

   [[device_id]]
    ip = 192.168.1.x
    key = xxxxxxxxxxxxxxxx
    type = lamp_rgb
    white_temp = 1800, 2700  # for LSC
    white_temp = 3000, 6500  # for Utorch LE7
    addr = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

- Alphawise dumb single outlet

.. code-block::

  [[device_id]]
    ip = 192.168.1.x
    key = xxxxxxxxxxxxxxxx
    type = powerrelay

- SmartPlug (single outlet) / BW-SHP6

.. code-block::

  [[device_id]]
    ip = 192.168.1.x
    key = xxxxxxxxxxxxxxxx
    type = smartplug

- SmartPlug (dual outlet) / BW-SHP7

.. code-block::

  [[device_id]]
    ip = 192.168.1.x
    key = xxxxxxxxxxxxxxxx
    type = smartplug
    dps = 1, 2               # <= 2 outlets
    pmeter_dps = 18, 19, 20  # <= dps for current / power / voltage
