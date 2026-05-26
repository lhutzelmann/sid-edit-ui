from htmy import Component, html

from sid_edit_ui.repositories.sid_repository import DependsSidFileRepo


def page(repo: DependsSidFileRepo) -> Component:
    return page_content(repo.file_name)


def page_content(file_name: str | None) -> Component:
    return html.div(
        html.h1("File Management"),
        html.p(f"Current file: {file_name}" if file_name else ""),
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
    )
