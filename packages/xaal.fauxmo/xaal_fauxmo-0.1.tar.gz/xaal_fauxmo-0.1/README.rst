xaal.fauxmo
===========
This is a simple implementation of a Fauxmo device for the xAAL protocol. It allows you to control xAAL devices with an Amazon Echo.
The device can be :

- a simple power relay
- a lamp
- a scenario
- anything that support on/off commands

You can group multiple devices under the same name to control them all at once.

Usage
-----

The configuration (`fauxmo.ini`) file looks like this :

  .. code:: yaml

    [devices]
    [[lampe ambiance]]
        targets = e19d5ea8-c838-11ea-82a8-9cebe88e1963,
        port = 49001

    [[luminaires séjour]]
        targets = e19d5ea8-c838-11ea-82a8-9cebe88e1963,6265eb30-8c59-11e9-98b1-b827ebe99201,
        port = 49003

    [[volet salle de bain]]
        targets = e4b05165-be5d-46d5-acd0-4da7be1158ed,
        port = 49004

Device name are the name that will be used to control the device with the Amazon Echo.
The `targets` field is a list of xAAL device UUIDs that will be controlled.
