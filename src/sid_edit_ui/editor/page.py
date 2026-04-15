from typing import Annotated

from fastapi import Form
from htmy import Component, html

from sid_edit_ui.components import input_field
from sid_edit_ui.repositories.sid_repository import UpdateResult, DependsSidFileRepo
from sid_file_format.sidfile import SIDFile


def page(repo: DependsSidFileRepo) -> Component:
    return page_content(repo.sid_file, repo.file_name)


def page_content(sid_file: SIDFile, file_name: str|None) -> Component:
    data = sid_file.model_dump()
    return html.div(
        html.h1("Edit SID file"),
        html.div(
            html.p(file_name if file_name else ""),
            html.button("Load", class_="btn btn-sm", hx_post="load-sid-file",
                        hx_trigger="click", hx_target="#main", hx_swap="innerHTML",
                        ),
            html.button("Save", class_="btn btn-sm", hx_post="load-sid-file",
                        hx_trigger="click", hx_target="#main", hx_swap="none",
                        ),
            html.form(
                input_field("name", data, "Song Name", "Enter the song's name"),
                input_field(
                    "author", data, "Author Information", "First Last (Handle)"
                ),
                html.button("Submit", type="submit", class_="btn btn-sm"),
                method="POST",
            ),
        ),
    )



def handle_submit(
    repo: DependsSidFileRepo,
    name: Annotated[str, Form()],
    author: Annotated[str, Form()],
) -> Component:
    data = {
        "name": name,
        "author": author,
    }
    result: UpdateResult = repo.update(data)
    if result.errors:
        for field, message in result.errors.items():
            print(f"{field}: {message}")
    return page_content(result.sid_file, repo.file_name)
