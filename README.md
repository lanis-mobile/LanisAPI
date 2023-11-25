[[README DE](https://github.com/kurwjan/LanisAPI/blob/master/README-DE.md)]  [[README EN](https://github.com/kurwjan/LanisAPI/blob/master/README.md)]

# LanisAPI

> ## ⚠ Notice
> **Because the Schulportal Hessen changes quickly and is very fragmented, some functions at specific schools or after a while may no longer work.**

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
If you want to have an app for Lanis, check out [SPH-vertretungsplan](https://github.com/alessioC42/SPH-vertretungsplan) by [@alessioC42](https://github.com/alessioC42). _It's still in an early phase!_

**It would be also really nice if you contribute to this project**, like bug reporting, if you know Dart and Flutter it would be nice to see your help or you could learn Dart, it's not hard.

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
