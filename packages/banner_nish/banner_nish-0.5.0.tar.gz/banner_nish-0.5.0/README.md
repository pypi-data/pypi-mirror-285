# banner_nish
```
    _   ___      __
   / | / (_)____/ /_
  /  |/ / / ___/ __ \
 / /|  / (__  ) / / /
/_/ |_/_/____/_/ /_/
```
## Introduction
Current latest release: v0.5.0 (2024. 07. 16)

Nothing special, but a good practice on publishing python packages.

## Installation
```
pip install banner-nish
```
That's it. That's all it takes. Just make sure you have the minimum python version to run it, which is `3.9`.

## Usages
As of `v0.5.0`, banner_nish has one functionality that can be executed directly from the command line: the `show-banner` command, which prints out a slanted ASCII-based banner that says my nickname, Nish. This functionality is implemented via its dependency `pyfiglet`.

An example execution looks like this:
```
$ show-banner

    _   ___      __
   / | / (_)____/ /_
  /  |/ / / ___/ __ \
 / /|  / (__  ) / / /
/_/ |_/_/____/_/ /_/

```
