from pathlib import Path
from typing import Any

from fastapi import Request
from holm.modules._layout import without_layout
from htmy import Component, html
from sid_file_format.sidfile import SIDFile

from sid_edit_ui.components import (
    field_block,
    hex_display,
    hex_field,
    input_field,
    number_field,
    select_field,
)
from sid_edit_ui.repositories.sid_repository import DependsSidFileRepo, UpdateResult
from sid_edit_ui.settings import settings


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


def _field_error(errors: dict[str, str] | None, key: str) -> str | None:
    if errors:
        return errors.get(key)
    return None


def page_content(
    sid_file: SIDFile,
    file_name: str | None,
    errors: dict[str, str] | None = None,
    data: dict[str, Any] | None = None,
) -> Component:
    if not data:
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
                style="margin-bottom:0.5rem;",
            ),
            html.form(
                field_block(
                    "Format & Version",
                    select_field(
                        "format_type",
                        flat,
                        "Format Type",
                        [("PSID", "PSID"), ("RSID", "RSID")],
                        error=_field_error(errors, "format_type"),
                    ),
                    select_field(
                        "version",
                        flat,
                        "Version",
                        [(1, "1"), (2, "2"), (3, "3"), (4, "4")],
                        error=_field_error(errors, "version"),
                    ),
                    select_field(
                        "flags_mus_player",
                        flat,
                        "Mus Player",
                        [(0, "Built-in"), (1, "Compute Sidplayer")],
                        style_="min-width:200px",
                        error=_field_error(errors, "mus_player"),
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
                        style_="min-width:200px",
                        error=_field_error(errors, "psid_specific"),
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
                        error=_field_error(errors, "video_standard"),
                    ),
                ),
                field_block(
                    "Song Info",
                    input_field(
                        "name",
                        flat,
                        "Song Name",
                        "Enter the song's name",
                        error=_field_error(errors, "name"),
                    ),
                    input_field(
                        "author",
                        flat,
                        "Author Information",
                        "First Last (Handle)",
                        error=_field_error(errors, "author"),
                    ),
                    input_field(
                        "released",
                        flat,
                        "Release Information",
                        "2025 Organisation",
                        error=_field_error(errors, "released"),
                    ),
                    vertical=True,
                ),
                field_block(
                    "Memory Addresses",
                    hex_field(
                        "load_address",
                        flat,
                        "Load Address (hex)",
                        num_digits=4,
                        error=_field_error(errors, "load_address"),
                    ),
                    hex_field(
                        "init_address",
                        flat,
                        "Init Address (hex)",
                        num_digits=4,
                        error=_field_error(errors, "init_address"),
                    ),
                    hex_field(
                        "play_address",
                        flat,
                        "Play Address (hex)",
                        num_digits=4,
                        error=_field_error(errors, "play_address"),
                    ),
                ),
                field_block(
                    "Songs",
                    number_field(
                        "songs",
                        flat,
                        "Songs",
                        min=1,
                        max=256,
                        error=_field_error(errors, "songs"),
                    ),
                    number_field(
                        "start_song",
                        flat,
                        "Start Song",
                        min=1,
                        max=256,
                        error=_field_error(errors, "start_song"),
                    ),
                ),
                field_block(
                    "Free Memory Range",
                    hex_field(
                        "start_page",
                        flat,
                        "Start Page (hex)",
                        num_digits=2,
                        error=_field_error(errors, "start_page"),
                    ),
                    hex_field(
                        "page_length",
                        flat,
                        "Page Length (hex)",
                        num_digits=2,
                        error=_field_error(errors, "page_length"),
                    ),
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
                        style_="min-width:200px",
                        error=_field_error(errors, "sid_model"),
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
                        style_="min-width:200px",
                        error=_field_error(errors, "sid_model_2nd_sid"),
                    ),
                    hex_field(
                        "second_sid_address",
                        flat,
                        "Address $Dxx0",
                        num_digits=2,
                        error=_field_error(errors, "second_sid_address"),
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
                        style_="min-width:200px",
                        error=_field_error(errors, "sid_model_3rd_sid"),
                    ),
                    hex_field(
                        "third_sid_address",
                        flat,
                        "Address $Dxx0",
                        num_digits=2,
                        error=_field_error(errors, "third_sid_address"),
                    ),
                ),
                html.div(
                    html.button("Apply", type="submit", class_="btn btn-sm"),
                    style="margin-top:0.5rem;",
                ),
                hex_display(data),
                method="POST",
                hx_post=".",
                hx_target="#main",
                hx_swap="innerHTML",
            ),
        ),
    )


def _parse_hex(val: str) -> int:
    val = val.strip().lstrip("$")
    if val.startswith("0x") or val.startswith("0X"):
        val = val[2:]
    return int(val, 16) if val else 0


async def handle_submit(
    request: Request,
    repo: DependsSidFileRepo,
) -> Component:
    form = await request.form()
    raw = dict(form)

    data: dict[str, Any] = {}

    errors = {}
    for key in ("name", "author", "released"):
        data[key] = raw.get(key, "")

    data["format_type"] = raw.get("format_type", "PSID")
    data["version"] = int(raw.get("version", 2))

    for key in (
        "load_address",
        "init_address",
        "play_address",
        "second_sid_address",
        "third_sid_address",
        "start_page",
        "page_length",
    ):
        try:
            data[key] = _parse_hex(raw.get(key, ""))
        except ValueError as e:
            errors[key] = str(e)

    for key in ("songs", "start_song"):
        v = raw.get(key, "")
        try:
            data[key] = int(v) if v else 1
        except ValueError as e:
            errors[key] = str(e)

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
        try:
            flags[key] = int(v) if v else 0
        except ValueError as e:
            errors[key] = str(e)
    data["flags"] = flags

    result: UpdateResult = repo.update(data)
    if result.errors or errors:
        errors.update(result.errors if result.errors else {})
        erroneous_data: dict[str, Any] = raw.copy()
        erroneous_data["c64_data"] = repo.sid_file.c64_data
        content = page_content(
            result.sid_file, repo.file_name, errors=errors, data=erroneous_data
        )
    else:
        if repo.file_name and repo.file_name.endswith(".sid"):
            save_path = repo.file_path
        elif repo.file_name:
            save_path = settings.upload_dir / (Path(repo.file_name).stem + ".sid")
        else:
            save_path = None
        if save_path:
            repo.save(save_path)
        content = page_content(result.sid_file, repo.file_name)
    if request.headers.get("hx-request"):
        return without_layout(content)
    return content
