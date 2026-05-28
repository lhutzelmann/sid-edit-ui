from pathlib import Path

from fastapi import UploadFile
from fastapi.responses import Response
from holm import action

from sid_edit_ui.file.handlers import handle_upload
from sid_edit_ui.file.page import page_content
from sid_edit_ui.repositories.sid_repository import DependsSidFileRepo


@action.post()
async def upload_file(
    file: UploadFile,
    repo: DependsSidFileRepo,
):
    if file.filename is None:
        raise ValueError("No valid file name.")
    content = await file.read()
    handle_upload(content, file.filename, repo)
    return page_content(repo.file_name)


@action.get()
def download_sid_file(repo: DependsSidFileRepo):
    content = repo.sid_file.to_sid()
    raw_name = repo.file_name or "untitled.sid"
    filename = raw_name if raw_name.endswith(".sid") else Path(raw_name).stem + ".sid"
    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
