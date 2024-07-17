xaal.schemas
============

Introduction
------------
This package contains stuffs to build some code from the schemas. Right now,
it mainly contains the "devices.py" module which is generated via the builder
script.

This module contains a function that return an instance for each dev-type.
For example, if you want to use a lamp.basic, you can simply write something
like this. 

.. code-block:: python

    from xaal.schemas import devices
    from xaal.lib import tools

    lamp = devices.lamp()
    lamp.address = tools.get_random_uuid()


WARNING
-------
This package will be updated regulary (that mainly why this files isn't in 
xaal.lib package), so don't modify the files unless you really know what 
you do. 

If your device isn't in this package, please send us a email to add a schema
or use the xaal.lib.Device API directly. (don't tweak devices.py)

TODO
----
Right now xaal.lib.Attribute doesn't support type checking (You know, it's
Python anyway..) but I think we should provide some default type checking,
in devices module.
