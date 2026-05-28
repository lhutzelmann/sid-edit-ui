from pathlib import Path

from sid_edit_ui.repositories.sid_repository import SIDFileRepository
from sid_edit_ui.config import get_settings
from sid_edit_ui.utils import int_from_c64_bytes


def _make_prg_update(content: bytes, filename: str) -> dict:
    file_address = int_from_c64_bytes(content[:2])
    return {
        "c64_data": content,
        "name": Path(filename).stem,
        "init_address": file_address,
        "play_address": file_address + 3,
    }


def _make_data_update(content: bytes, filename: str) -> dict:
    file_address = 0x1000
    return {
        "c64_data": content,
        "name": Path(filename).stem,
        "load_address": file_address,
        "init_address": file_address,
        "play_address": file_address + 3,
    }


def handle_upload(
    content: bytes,
    file_name: str,
    repo: SIDFileRepository,
) -> None:
    settings = get_settings()
    # First save the original uploaded file to the upload folder (== cache)
    file_path = settings.upload_dir / file_name
    file_path.write_bytes(content)

    suffix = file_path.suffix.lower()

    if suffix == ".sid":
        repo.load(file_path)
    else:
        # Convert to SID file and save it
        repo.init()  # initialize SID file data
        if suffix == ".prg":
            data = _make_prg_update(content, file_name)
        elif suffix == ".data":
            data = _make_data_update(content, file_name)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
        sid_file_path = repo.get_cached_sid_file_path(file_name)
        # Now change the repo file data for the new SID file
        repo.file_name = sid_file_path.name
        repo.file_path = sid_file_path
        repo.update(data)  # Writes the SID file to the cache folder
