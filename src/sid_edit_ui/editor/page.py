from typing import Any

from fastapi import Request
from htmy import Component, html

from sid_edit_ui.components import (
    field_block,
    hex_display,
    hex_field,
    input_field,
    number_field,
    select_field,
)
from sid_edit_ui.repositories.sid_repository import UpdateResult, DependsSidFileRepo
from sid_file_format.sidfile import SIDFile


def page(repo: DependsSidFileRepo) -> Component:
    return page_content(repo.sid_file, repo.file_name)


def _flatten_flags(data: dict) -> dict:
    if "flags" not in data:
        return data
    flat = dict(data)
    flags = flat.pop("flags")
    if isinstance(flags, dict):
        for k, v in flags.items():
            flat[f"flags_{k}"] = v
    else:
        for k in (
            "mus_player",
            "psid_specific",
            "video_standard",
            "sid_model",
            "sid_model_2nd_sid",
            "sid_model_3rd_sid",
        ):
            flat[f"flags_{k}"] = 0
    return flat


def page_content(sid_file: SIDFile, file_name: str | None) -> Component:
    data = sid_file.model_dump()
    flat = _flatten_flags(data)

    return html.div(
        html.h1("Edit SID file"),
        html.div(
            html.p(file_name if file_name else ""),
            html.button(
                "Reload .sid file",
                class_="btn btn-sm",
                hx_post="load-sid-file",
                hx_trigger="click",
                hx_target="#main",
                hx_swap="innerHTML",
            ),
            html.form(
                html.input_(type="file", name="file", accept=".sid,.prg,.data"),
                html.button("Upload file", type="submit", class_="btn btn-sm"),
                method="POST",
                enctype="multipart/form-data",
                hx_post="upload-file",
                hx_target="#main",
                hx_swap="innerHTML",
                style="margin-top:0.5rem;",
            ),
            html.form(
                field_block(
                    "Format & Version",
                    select_field(
                        "format_type",
                        flat,
                        "Format Type",
                        [("PSID", "PSID"), ("RSID", "RSID")],
                    ),
                    select_field(
                        "version",
                        flat,
                        "Version",
                        [(1, "1"), (2, "2"), (3, "3"), (4, "4")],
                    ),
                    select_field(
                        "flags_mus_player",
                        flat,
                        "Mus Player",
                        [(0, "Built-in"), (1, "Compute Sidplayer")],
                    ),
                    select_field(
                        "flags_psid_specific",
                        flat,
                        "PSID Specific",
                        [
                            (0, "C64 Compatible"),
                            (1, "PlaySID Specific"),
                            (2, "C64 Basic"),
                        ],
                    ),
                    select_field(
                        "flags_video_standard",
                        flat,
                        "Video Standard",
                        [
                            (0, "Unknown"),
                            (1, "PAL"),
                            (2, "NTSC"),
                            (3, "PAL & NTSC"),
                        ],
                    ),
                ),
                field_block(
                    "Song Info",
                    input_field("name", flat, "Song Name", "Enter the song's name"),
                    input_field(
                        "author", flat, "Author Information", "First Last (Handle)"
                    ),
                    input_field(
                        "released",
                        flat,
                        "Release Information",
                        "2025 Organisation",
                    ),
                    vertical=True,
                ),
                field_block(
                    "Memory Addresses",
                    hex_field("load_address", flat, "Load Address", num_digits=4),
                    hex_field("init_address", flat, "Init Address", num_digits=4),
                    hex_field("play_address", flat, "Play Address", num_digits=4),
                ),
                field_block(
                    "Songs",
                    number_field("songs", flat, "Songs", min=1, max=256),
                    number_field("start_song", flat, "Start Song", min=1, max=256),
                ),
                field_block(
                    "First SID",
                    select_field(
                        "flags_sid_model",
                        flat,
                        "SID Model",
                        [
                            (0, "Unknown"),
                            (1, "MOS 6581"),
                            (2, "MOS 8580"),
                            (3, "MOS Both"),
                        ],
                    ),
                    number_field("start_page", flat, "Start Page", min=0, max=255),
                    number_field(
                        "page_length", flat, "Page Length", min=0, max=255
                    ),
                ),
                field_block(
                    "Second SID",
                    select_field(
                        "flags_sid_model_2nd_sid",
                        flat,
                        "SID Model",
                        [
                            (0, "Unknown"),
                            (1, "MOS 6581"),
                            (2, "MOS 8580"),
                            (3, "MOS Both"),
                        ],
                    ),
                    number_field(
                        "second_sid_address",
                        flat,
                        "Address",
                        min=0,
                        max=255,
                    ),
                ),
                field_block(
                    "Third SID",
                    select_field(
                        "flags_sid_model_3rd_sid",
                        flat,
                        "SID Model",
                        [
                            (0, "Unknown"),
                            (1, "MOS 6581"),
                            (2, "MOS 8580"),
                            (3, "MOS Both"),
                        ],
                    ),
                    number_field(
                        "third_sid_address",
                        flat,
                        "Address",
                        min=0,
                        max=255,
                    ),
                ),
                hex_display(data),
                html.div(
                    html.button("Submit", type="submit", class_="btn btn-sm"),
                    style="margin-top:0.5rem;",
                ),
                method="POST",
                hx_post=".",
                hx_target="#main",
                hx_swap="innerHTML",
            ),
        ),
    )


def _parse_hex(val: str) -> int:
    val = val.strip().replace("$", "").replace("0x", "").replace("0X", "").replace("#", "")
    return int(val, 16) if val else 0


async def handle_submit(
    request: Request,
    repo: DependsSidFileRepo,
) -> Component:
    form = await request.form()
    raw = dict(form)

    data: dict[str, Any] = {}

    for key in ("name", "author", "released"):
        data[key] = raw.get(key, "")

    data["format_type"] = raw.get("format_type", "PSID")
    data["version"] = int(raw.get("version", 2))

    for key in ("load_address", "init_address", "play_address"):
        data[key] = _parse_hex(raw.get(key, ""))

    for key in ("songs", "start_song"):
        v = raw.get(key, "")
        data[key] = int(v) if v else 1

    flags = {}
    for key in (
        "mus_player",
        "psid_specific",
        "video_standard",
        "sid_model",
        "sid_model_2nd_sid",
        "sid_model_3rd_sid",
    ):
        v = raw.get(f"flags_{key}", "")
        flags[key] = int(v) if v else 0
    data["flags"] = flags

    for key in ("start_page", "page_length", "second_sid_address", "third_sid_address"):
        v = raw.get(key, "").strip()
        data[key] = int(v) if v else None

    result: UpdateResult = repo.update(data)
    if result.errors:
        for field, message in result.errors.items():
            print(f"{field}: {message}")
    return page_content(result.sid_file, repo.file_name)
