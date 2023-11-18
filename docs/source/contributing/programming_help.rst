.. title:: Programming help

.. _programming_help:

Programming help / guidelines
=============================

The main file is ``client.py`` which includes the hearth of the lib: ``LanisClient``.

Modules
-------

``functions``
~~~~~~~~~~~~~

This module includes every dataclass and function for outside (normal) use which are then referenced in the ``client.py`` file.
Fetching functions for Lanis applets and so are added here.

``helpers``
~~~~~~~~~~~

This module includes various general and helper functions and classes for scripts of the library.
Like ``cryptor.py`` which handles the encryption of Lanis, it can't be directly accessed but some functions in ``functions`` need it.

Programming
-----------

Making requests
~~~~~~~~~~~~~~~

If you want to make a request to Lanis use the ``Request`` class from ``helpers.request``.
This class wraps ``httpx.Client`` with some additional checking code.

More info about ``httpx`` here: https://www.python-httpx.org/.

Parsing
~~~~~~~

If Lanis provides no API we use the ``HTMLParser`` from ``selectolax.parser``.

More info about selectolax here: https://github.com/rushter/selectolax.

Parsing errors
^^^^^^^^^^^^^^

If a *(critical-enough)* element is ``None`` or something else use the ``HTMLLogger`` from ``helpers.html_logger``.

Logging
~~~~~~~

Try to log as much *(useful)* information you can with the ``LOGGER`` from ``constants.py``.
It's just the normal python logger: https://docs.python.org/3/library/logging.html.

Common Format
^^^^^^^^^^^^^

*(if exists)* ``Class name`` - *humanly formatted* ``Function name``: ``Message``.

Presenting data
~~~~~~~~~~~~~~~

Don't return just ``dict`` or something rather use the ``dataclass`` from the built-in ``dataclasses``.
Optionally in some cases the pure ``JSON`` can be returned.

Saving files
~~~~~~~~~~~~

If you want to add something that saves a file **it should not save it when LanisClient.save** is ``False``.