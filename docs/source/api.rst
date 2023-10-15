.. title:: API References

.. _api:

API References
==============

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
~~~~~~~~~~~~~~~~~~~

Functions
^^^^^^^^^

.. autofunction:: get_schools

Types
^^^^^

.. autoclass:: School

Substitution plan
~~~~~~~~~~~~~~~~~

Functions
^^^^^^^^^

.. autofunction:: get_substitution_plan

Types
^^^^^

.. autoclass:: SubstitutionPlan
    :members:

Calendar
~~~~~~~~~~~~~~~~~

Functions
^^^^^^^^^

.. autofunction:: get_calendar

.. autofunction:: get_calendar_of_month

Types
^^^^^

.. autoclass:: Calendar
    :members:

Tasks
~~~~~~~~~~~~~~~~~

Functions
^^^^^^^^^

.. autofunction:: get_tasks

Types
^^^^^

.. autoclass:: TaskData