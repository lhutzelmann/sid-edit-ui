from fastapi import UploadFile
from holm import action

from sid_edit_ui.file.handlers import handle_upload
from sid_edit_ui.file.page import page_content
from sid_edit_ui.repositories.sid_repository import DependsSidFileRepo
from sid_edit_ui.settings import settings


@action.post()
async def upload_file(
    file: UploadFile,
    repo: DependsSidFileRepo,
):
    if file.filename is None:
        raise ValueError("No valid file name.")
    content = await file.read()
    handle_upload(content, file.filename, repo, settings.upload_dir)
    return page_content(repo.file_name)
