.. title:: LanisAPI

.. toctree::
    :hidden:
    :titlesonly:
    :maxdepth: 2
    
    first_steps
    repo
    api/index
    contributing/index

LanisAPI
========

.. attention:: 
    This project is still in a early stage so expect bugs.

.. warning:: 
    Because the Schulportal Hessen changes quickly and is very fragmented, some functions at specific schools or after a while may no longer work.

.. note:: 
    This project isn't officially related to the Schulportal Hessen. It's only a unofficial library, supported by the community.

What is this?
-------------

LanisAPi is an unofficial Python library for the Schulportal Hessen also available on `PyPi <https://pypi.org/project/lanisapi/>`__.

Features
--------

* Fetch homework or other tasks.
* Fetch substitution plan.
* Fetch calendar events.
* Fetch conversations.
* Fetch all schools that have Lanis.
* Fetch all web applets with their links.

Overview of future features, problems and other things `here <https://github.com/users/kurwjan/projects/2>`__.

Example
-------
.. code-block:: python

    from lanisapi import LanisClient, LanisAccount, LanisCookie, School

    def main():
        client = LanisClient(LanisAccount("school id", "name.lastname", "password"))
            or: client = LanisClient(LanisAccount(School("school", "city"), "name.lastname", "password"))
            or: client = LanisClient(LanisCookie("school id", "session id"))
        client.authenticate()
        print(client.get_substitution_plan())
        client.close()
    
    if __name__ == "__main__":
        main()

More infos at the :ref:`first_steps`.

How can I help?
---------------
1. You can report problems `here <https://github.com/kurwjan/LanisAPI/issues>`__.
2. You can suggest ideas `here <https://github.com/kurwjan/LanisAPI/issues>`__.
3. **Contributing:** You can contribute to this project either by code or improving the wiki. If you're new to contributing, look `here <https://docs.github.com/en/get-started/quickstart/contributing-to-projects>`__ and for this project there is also some help: :ref:`programming_help`.

*Also if you like this project you can give it a star on Github.*

Credits
-------
* `SPHclient <https://github.com/alessioC42/SPHclient>`__ helped me to understand the *Schulportal Hessen*.
* `sph-planner <https://github.com/koenidv/sph-planner>`__ helped me to understand the Level 2 encryption.