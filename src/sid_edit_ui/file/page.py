from htmy import Component, html

from sid_edit_ui.components import field_block
from sid_edit_ui.repositories.sid_repository import DependsSidFileRepo


def page(repo: DependsSidFileRepo) -> Component:
    return page_content(repo.file_name)


def page_content(file_name: str | None) -> Component:
    return html.div(
        html.h1("File Management"),
        html.p(f"Current file: {file_name}" if file_name else ""),
        field_block(
            "Load",
            html.form(
                html.input_(
                    type="file",
                    name="file",
                    accept=".sid,.prg,.data",
                    style="flex:1;min-width:200px;",
                ),
                html.button(
                    "Load file",
                    type="submit",
                    class_="btn btn-sm",
                    style="flex-shrink:0;",
                ),
                method="POST",
                enctype="multipart/form-data",
                hx_post="upload-file",
                hx_target="#main",
                hx_swap="innerHTML",
                style="display:flex;gap:0.75rem;align-items:flex-end;flex-wrap:wrap;",
            ),
        ),
        field_block(
            "Save",
            html.button(
                "Save SID File",
                class_="btn btn-sm",
                onclick="window.location.href='/file/download-sid-file'",
            ),
        ),
    )
