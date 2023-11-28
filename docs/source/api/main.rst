.. title:: Main reference

.. _main:

Main reference
=====================

LanisClient
-----------

.. autoclass:: lanisapi.LanisClient

Properties
~~~~~~~~~~~~~~~~~

.. autoproperty:: lanisapi.LanisClient.authentication_cookies

General functions
~~~~~~~~~~~~~~~~~

.. currentmodule:: lanisapi.LanisClient
.. autofunction:: authenticate

.. autofunction:: logout

.. autofunction:: close

Authentication types
~~~~~~~~~~~~~~~~~~~~

.. currentmodule:: lanisapi.functions.authentication_types
.. autoclass:: School()

.. autoclass:: LanisAccount()

.. autoclass:: LanisCookie()

.. autoenum:: SessionType

Get all schools
~~~~~~~~~~~~~~~

Functions
^^^^^^^^^

.. currentmodule:: lanisapi.LanisClient
.. autofunction:: get_schools

Getting the Substitution plan
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Functions
^^^^^^^^^

.. currentmodule:: lanisapi.LanisClient
.. autofunction:: get_substitution_plan

Types
^^^^^

.. currentmodule:: lanisapi.functions.substitution
.. autoclass:: SubstitutionPlan()

    .. autoclass:: lanisapi.functions.substitution.SubstitutionPlan.Substitution()

Getting the Calendar
~~~~~~~~~~~~~~~~~~~~

Functions
^^^^^^^^^

.. currentmodule:: lanisapi.LanisClient
.. autofunction:: get_calendar

.. autofunction:: get_calendar_of_month

Types
^^^^^

.. currentmodule:: lanisapi.functions.calendar
.. autoclass:: Calendar()

    .. autoclass:: lanisapi.functions.calendar.Calendar.Event()

Getting all tasks
~~~~~~~~~~~~~~~~~

Functions
^^^^^^^^^

.. currentmodule:: lanisapi.LanisClient
.. autofunction:: get_tasks

Types
^^^^^

.. currentmodule:: lanisapi.functions.tasks
.. autoclass:: Task()

Getting conversations
~~~~~~~~~~~~~~~~~~~~~

Functions
^^^^^^^^^

.. currentmodule:: lanisapi.LanisClient
.. autofunction:: get_conversations

Types
^^^^^

.. currentmodule:: lanisapi.functions.conversations
.. autoclass:: Conversation()

Getting all web applets
~~~~~~~~~~~~~~~~~~~~~~~

Functions
^^^^^^^^^

.. currentmodule:: lanisapi.LanisClient
.. autofunction:: get_apps

.. autofunction:: get_folders

.. autofunction:: get_available_apps

.. autofunction:: get_app_availability

Types
^^^^^

.. currentmodule:: lanisapi.functions.apps
.. autoclass:: Folder()

.. autoclass:: App()