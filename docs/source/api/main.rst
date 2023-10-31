.. title:: Main reference

.. _main:

Main reference
=====================

LanisClient
-----------

.. autoclass:: lanisapi.LanisClient

General functions
~~~~~~~~~~~~~~~~~

.. currentmodule:: lanisapi.LanisClient

.. autofunction:: authenticate

.. autofunction:: logout

.. autofunction:: close

Get all schools
~~~~~~~~~~~~~~~

Functions
^^^^^^^^^

.. currentmodule:: lanisapi.LanisClient
.. autofunction:: get_schools

Types
^^^^^

.. currentmodule:: lanisapi.functions.schools
.. autoclass:: School

Getting the Substitution plan
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Functions
^^^^^^^^^

.. currentmodule:: lanisapi.LanisClient
.. autofunction:: get_substitution_plan

Types
^^^^^

.. currentmodule:: lanisapi.functions.substitution
.. autoclass:: SubstitutionPlan
    :members:

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
.. autoclass:: Calendar
    :members:

Getting all tasks
~~~~~~~~~~~~~~~~~

Functions
^^^^^^^^^

.. currentmodule:: lanisapi.LanisClient
.. autofunction:: get_tasks

Types
^^^^^

.. currentmodule:: lanisapi.functions.tasks
.. autoclass:: Task

Getting conversations
~~~~~~~~~~~~~~~~~~~~~

Functions
^^^^^^^^^

.. currentmodule:: lanisapi.LanisClient
.. autofunction:: get_conversations

Types
^^^^^

.. currentmodule:: lanisapi.functions.conversations
.. autoclass:: Conversation