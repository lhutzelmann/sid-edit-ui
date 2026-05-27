# sid-edit-ui / SEU
A simple cross-platform UI to edit C64 SID files.

The vision is to have a **minimalistic, compact local web application running on anything with modern
Python and a web browser**.

**This project is work in progress. You have been warned.**

After saying that, the sid-file-format (packages/sid-file-format) package may be of some value for somebody who wants
to have a proper, valid object representation of SID music files from Commodore 64/128 computers.

Currently only the regular specification is implemented (v1-v4) in all its variants, missing out the "SID file format+"
(v4E).

The `load_and_save_sid_file.py` script already demonstrates loss-less round-trip editing with loading and saving
SID files.

A working UI is now implemented that allows loading, editing and saving SID files.

## Features

- Supports loading of several binary files:
  - .sid: SID music files
  - .prg: C64 program files that include the load-address in the first two bytes.
  - .data: C64 program or data files without the load-address bytes.
- Guesses some values after loading, e.g. init and play addresses.
- Edit all parameters defined for SID music files of the supported versions.
- Checks for invalid values and fixes some of them automatically in the editor.
- Displays up to 4096 bytes of the loaded file as memory dump for investigating metadata.
- Saves the edited SID music file.
- Developed on Windows but should run on Linux and macOS as well.

## Set up a dev environment

For development and running you need `uv` and `Python 3.12+`.

Clone or download the repository from GitHub and create a virtual environment with uv:

```shell
cd sid-edit-ui
uv sync
```

## Run the application

```shell
uv run SEU
```

Then you can open `http://localhost:8000` in your Web browser for the user interface.
