# sid-edit-ui / SEI
A simple cross-platform UI to edit C64 SID files.

**This project is work in progress, unfinished and currently not suitable for anything. You have been warned.**

After saying that, the sid-file-format (packages/sid-file-format) package may be of some value for somebody who wants
to have a proper, valid object representation of SID music files from Commodore 64/128 computers.

Currently only the regular specification is implemented (v1-v4) in all its variants, missing out the "SID file format+"
(v4E).

The `load_and_save_sid_file.py` script already demonstrates loss-less round-trip editing with loading and saving
SID files.

The goal of this project is to create a cross-platform UI. I am currently experimenting with different web
frameworks to achieve that.
The vision is to have a **minimalistic, compact local web application running on anything with modern
Python and a web browser**.

## Set up a dev environment

For development and running you need `uv` and `Python 3.12+`.

Clone or download the repository from GitHub and create a virtual environment with uv:

```shell
cd sid-edit-ui
uv sync
```

## Run the application

```shell
uv run SEI
```

Then you can open `http://localhost:8000` in your Web browser and see what is already implemented and what is still
missing.
