# Tons

[![PyPI](https://img.shields.io/pypi/v/tons?color=blue)](https://pypi.org/project/tons/)
[![Downloads](https://static.pepy.tech/badge/tons)](https://pepy.tech/project/tons)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tons)](https://pypi.org/project/tons/)


# Documentation

You can find [installation guide](https://tonfactory.github.io/tons-docs/installation) 
and all available features in our [docs](https://tonfactory.github.io/tons-docs/).



# Introduction

**tons** is a cross-platform wallet application that maintains wallets in the TON network
for both desktops and servers. Works with Windows/Mac/Linux.

**tons** has different UIs:

- [tons-gui](#tons-gui)
- [tons-interactive](#tons-interactive)
- [tons-cli](#tons-cli)


**tons** uses specific filesystem architecture that is maintained by the application.
```
.tons
├── config.yaml
├── whitelist.json
├── keystores
│   ├── *.keystore
```


## User interfaces

### tons-gui

Graphic user interface is the most intuitive and convenient way to work with your assets.

![tons-gui](https://tonfactory.github.io/tons-docs/assets/images/introduction-b9e3fe5662fd3fbff8996ca607800448.png)




### tons-interactive

*tons-interactive* is a convenient interface to control your assets through terminal.

```bash
$ tons-interactive
[✓] Pick command: Keystores
[✓] Pick command: Open keystore
[✓] Choose keystore to use: 🔒 personal.keystore
[?] Pick command [personal.keystore]: List wallets
 > List wallets
   Transfer
   Advanced Transfer
   Whitelist
   Tonconnect v2
   DNS
   Jetton
   ...
```


### tons-cli

*tons* has a batch mode interface that allows you to write automatic scripts.

To get all available subcommands and flags run a command with an '-h' flag
```bash
$ tons -h
Usage: tons [OPTIONS] COMMAND [ARGS]...

Options:
  --version      Show the version and exit.
  -c, --config   Use specific config.yaml file
  -h, --help     Show this message and exit.

Commands:
  config      Control config parameters (check README.md for all fields...
  contract    Operate with contracts
  dev         Development tools
  dns         Operate with DNS
  init        Initialize .tons workdir in a current directory
  keystore    Operate with keystores
  tonconnect  Operate with TonConnect
  wallet      Operate with wallets
  whitelist   Operate with whitelist contacts
```

Example: get list of all wallets from a keystore
```bash
$ tons wallet list -v
| Name  | Version | WC |                     Address                      | Comment | State  | Balance |
|:------|:-------:|:--:|:------------------------------------------------:|:--------|:------:|--------:|
| dev   |   v3r2  | 0  | EQBxWbjry61lk0dU_8viG9M_e5x9VGOJaI9ZhOrn6vcIp7Sm | None    | Active |    13.1 |
| prod  |   v4r2  | 0  | EQCkNipaz2C3Md-tXVBcD3E4yv8EKqMzZ41QQtsM4IdFnKP5 | None    | Uninit |     0.0 |
| Total |         |    |                                                  |         |        |    13.1 |
```
# License

The code and data files in this distribution are licensed under the terms of the GNU General Public License version 3 
as published by the Free Software Foundation. See https://www.gnu.org/licenses/ for a copy of this license.
