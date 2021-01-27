# SCP-079-NOFLOOD

This bot is used to prevent message-flooding.

## How to use

- See the [manual](https://telegra.ph/SCP-079-NOFLOOD-12-04)
- See [this article](https://scp-079.org/noflood/) to build a bot by yourself
- [README](https://github.com/scp-079/scp-079-readme) of the SCP-079 Project
- Discuss [group](https://t.me/SCP_079_CHAT)

## To Do List

- [x] Basic functions

## Requirements

- Python 3.6 or higher
- Debian 10: `sudo apt update && sudo apt install opencc -y`
- pip: `pip install -r requirements.txt` or `pip install -U APScheduler OpenCC pyAesCrypt pyrogram[fast]`

## Files

- plugins
    - functions
        - `channel.py` : Functions about channel
        - `etc.py` : Miscellaneous
        - `file.py` : Save files
        - `filters.py` : Some filters
        - `group.py` : Functions about group
        - `ids.py` : Modify id lists
        - `receive.py` : Receive data from exchange channel
        - `telegram.py` : Some telegram functions
        - `tests.py` : Some test functions
        - `timers.py` : Timer functions
        - `user.py` : Functions about user and channel object
    - handlers
        - `command.py` : Handle commands
        - `message.py`: Handle messages
    - `glovar.py` : Global variables
- `.gitignore` : Ignore
- `config.ini.example` -> `config.ini` : Configuration
- `LICENSE` : GPLv3
- `main.py` : Start here
- `README.md` : This file
- `requirements.txt` : Managed by pip

## Contribute

Welcome to make this project even better. You can submit merge requests, or report issues.

## Credit

This is a fork (forked on 1/26/2021 PST) of the repo from scp-079 (https://github.com/scp-079) project.


## License

Licensed under the terms of the [GNU General Public License v3](LICENSE).
