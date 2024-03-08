[[README DE](https://github.com/kurwjan/LanisAPI/blob/master/README-DE.md)]  [[README EN](https://github.com/kurwjan/LanisAPI/blob/master/README.md)]

# LanisAPI

> ## ⚠ Rework in Progress
> **[See issue #32](https://github.com/kurwjan/LanisAPI/issues/32)**
> 
> *For now, you can use v0.4.1*

## What is this?

It's an unofficial Python library for the Schulportal Hessen. Also available on [PyPi](https://pypi.org/project/lanisapi/).

## Features

+ Fetch homework or other tasks.
+ Fetch substitution plan.
+ Fetch calendar events.
+ Fetch conversations.
+ Fetch all schools that have Lanis.
+ Fetch all web applets with their links.

**Overview of future Features, Problems and other things [here](https://github.com/users/kurwjan/projects/2).**

## App for the Schulportal Hessen
You want an app? Use [lanis-mobile](https://github.com/alessioC42/lanis-mobile)!

[<img src="https://github.com/alessioC42/lanis-mobile/assets/84250128/19d30436-32f7-4cbe-b78e-f2fee3583c28" width="25%">](https://github.com/alessioC42/lanis-mobile)

Lanis-mobile is open for new contributors!

## How do I install it?

```sh
pip install lanisapi
```

Required is Python 3.11. *(older versions are probably not working, I didn't tested it.)*

## Example

This example gives the substitution plan.

```python
from lanisapi import LanisClient, LanisAccount, LanisCookies, School

def main():
    client = LanisClient(LanisAccount("school id", "name.lastname", "password"))
        or: client = LanisClient(LanisAccount(School("school", "city"), "name.lastname", "password"))
        or: client = LanisClient(LanisCookie("school id", "session id"))
    client.authenticate()
    print(client.get_substitution_plan())
    client.close()
    
if __name__ == "__main__":
    main()
```

More infos at the [wiki](https://lanisapi.readthedocs.io/en/latest/first_steps.html).

## How can I help?

1. You can report problems at *Issues*.
2. You can suggest ideas at *Issues*.
3. **Contributing**: You can contribute to this project either by code or improving the wiki. If you're new to contributing, look [here](https://docs.github.com/en/get-started/quickstart/contributing-to-projects) and for this project there is also some help [here](https://lanisapi.readthedocs.io/en/latest/contributing/programming_help.html).

*Also if you like this project you can give it a star.*

## Credits

The Javascript project [SPHclient](https://github.com/alessioC42/SPHclient) from [@alessioC42](https://github.com/alessioC42) helped me to understand the *Schulportal Hessen*.

The Android-App [sph-planner](https://github.com/koenidv/sph-planner) from [@koenidv](https://github.com/koenidv) helped me to understand the Level 2 encryption.

Other projects that didn't helped me but are cool:

+ **Flutter Android app [SPH-Vertretungsplan](https://github.com/alessioC42/SPH-vertretungsplan) also from [@alessioC42](https://github.com/alessioC42)**
+ TypeScript library [Maria](https://github.com/elderguardian/maria) from [Elderguardian](https://github.com/elderguardian/)
+ Javascript app [SchulportalApp](https://github.com/DerOwnerHD/SchulportalApp) from [DerOwnerHD](https://github.com/DerOwnerHD)
+ Flutter Android app [lkwslr-sphplaner](https://github.com/flutter-preview/lkwslr-sphplaner) from [flutter-preview](https://github.com/flutter-preview)

## Notice

This project isn't officially related to the Schulportal Hessen. It's only a unofficial library, supported by the community.
