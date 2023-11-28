.. title:: Get data as a dictionary

.. _dict:

Get data as a dictionary
========================

If you want to get data as a dictionary (or JSON) and not as a attrs dataclass, use
the ``asdict()`` function from ``attrs``.

Example
-------

.. code-block:: python

    from attrs import asdict
    from lanisapi import LanisAccount, LanisClient, SubstitutionPlan
    from rich import print


    def main(): 
        ... # Authentication

        substitutions: SubstitutionPlan = client.get_substitution_plan()
        print(asdict(substitutions))

        client.close()

    if __name__ == "__main__":
        main()

