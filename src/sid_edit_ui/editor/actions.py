from pathlib import Path

from fastapi import UploadFile
from holm import action

from sid_edit_ui.editor.page import page_content
from sid_edit_ui.repositories.sid_repository import DependsSidFileRepo
from sid_edit_ui.settings import settings
from sid_file_format.sidfile import int_from_bytes


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
    if file.filename is None:
        raise ValueError("No valid file name.")
    file_path = settings.upload_dir / file.filename
    content = await file.read()
    file_path.write_bytes(content)

    suffix = Path(file.filename).suffix.lower()

    if suffix == ".sid":
        repo.load(file_path)
    else:
        repo.init()
        data: dict = {}
        file_address = int_from_bytes(content[:2])
        data["c64_data"] = content
        data["name"] = Path(file.filename).stem

        if suffix == ".prg":
            data["init_address"] = file_address
            data["play_address"] = file_address + 3
        elif suffix == ".data":
            data["load_address"] = file_address
            data["init_address"] = file_address
            data["play_address"] = file_address + 3

        repo.update(data)
        repo.file_name = file.filename
        repo.file_path = file_path

    return page_content(repo.sid_file, repo.file_name)
