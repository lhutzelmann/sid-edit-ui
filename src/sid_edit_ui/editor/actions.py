from pathlib import Path

from fastapi import UploadFile
from holm import action

from sid_edit_ui.editor.page import page_content
from sid_edit_ui.repositories.sid_repository import DependsSidFileRepo
from sid_edit_ui.settings import settings


@action.post()
def load_sid_file(repo: DependsSidFileRepo):
    sid_file_path = Path("Metal_Dust_Title_Remix.sid")
    repo.load(sid_file_path)
    print(f"Loaded {repo.file_name}.")
    return page_content(repo.sid_file, repo.file_name)


@action.post()
async def upload_file(
    file: UploadFile,
    repo: DependsSidFileRepo,
):
    file_path = settings.upload_dir / file.filename
    content = await file.read()
    file_path.write_bytes(content)
    return page_content(repo.sid_file, repo.file_name)
