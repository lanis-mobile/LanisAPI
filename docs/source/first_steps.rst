.. title:: First steps

.. _first_steps:

First steps
===========

.. important:: 
    **Very important** is also that you report not working features from your school or errors.
    This is necessary to support everyone. More info at :ref:`repo` and :ref:`bug_reporting`.

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

    from lanisapi import LanisClient, LanisAccount, LanisCookie, School

    def main():
        client = LanisClient(LanisAccount("school id", "name.lastname", "password"))
            or: client = LanisClient(LanisAccount(School("school", "city"), "name.lastname", "password"))
            or: client = LanisClient(LanisCookie("school id", "session id")) # Use client.authentication_cookies in the previous session
        client.authenticate()
        print(client.get_substitution_plan())
        client.close()
    
    if __name__ == "__main__":
        main()

1. First you initialise the ``LanisClient`` class with the LanisAccount dataclass. You can find the school id in the url at ``?=i`` in https://start.schulportal.hessen.de/?i=SCHOOLID.
2. Or you initalise it with School(``school``, ``city``).
3. Or if you already initialised before you can use the previous session and provide ``LanisCookie`` with ``LanisClient.authentication_cookies``.
4. Then you log in with ``authenticate()``.
5. Then we print the current substitution plan.
6. Then we close the client. **You need to do this.**