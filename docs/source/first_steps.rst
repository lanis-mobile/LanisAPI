.. title:: First steps

.. _first_steps:

First steps
===========

.. important:: 
    **Very important** is also that you report not working features from your school or errors.
    This is necessary to support everyone. More info at :ref:`repo`.

Install
-------

Required is Python 3.11 *(older versions will probably work too)*.

You can install it with::

    pip install lanisapi

Better print()
~~~~~~~~~~~~~~

If you want a better formatted ``print()`` with colors install::
    
    pip install rich

To replace the normal ``print()`` import it like this:

.. code-block:: python

    from rich import print

Example code
------------

.. code-block:: python

    from lanisapi import LanisClient

    def main():
        client = LanisClient("schoolid", "name.lastname", "password")
            or: client = LanisClient(LanisClient.School("Testschule MH", "Testhausen City"), "password")
        client.authenticate()
        print(client.get_substitution_plan())
        client.close()
    
    if __name__ == "__main__":
        main()

1. First you initialise the ``LanisClient`` class with the ``schoolid`` you can find it in the url at ``?=i`` in https://start.schulportal.hessen.de/?i=SCHOOLID.
2. Or you initalise it with School(``school``, ``city``).
3. Then you log in with ``authenticate()``.
4. Then we print the current substitution plan.
5. Then we close the client. **You need to do this.**