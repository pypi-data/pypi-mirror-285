"""
Description
-----------

UUIDExtension provides the capability to generate UUID version 4 (UUID4) strings directly within your templates.


.. autoclass: UUIDExtension

Example
-------

.. code-block:: jinja

  Generated UUID: {{ uuid() }}

"""

import uuid as m_uuid

from jinja2.ext import Extension


# pylint: disable=abstract-method
class UUIDExtension(Extension):
    """
    Jinja2 Extension to generate uuid4 string.
    """

    def __init__(self, environment):
        """
        Jinja2 Extension constructor.
        """
        super().__init__(environment)

        def uuid():
            """
            Generate UUID4.
            """
            return str(m_uuid.uuid4())

        environment.globals.update(uuid=uuid)
