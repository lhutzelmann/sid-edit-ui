from pathlib import Path

from sid_edit_ui.repositories.sid_repository import SIDFileRepository
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
    filename: str,
    repo: SIDFileRepository,
    upload_dir: Path,
) -> None:
    file_path = upload_dir / filename
    file_path.write_bytes(content)

    suffix = Path(filename).suffix.lower()

    if suffix == ".sid":
        repo.load(file_path)
    else:
        repo.init()
        if suffix == ".prg":
            data = _make_prg_update(content, filename)
        elif suffix == ".data":
            data = _make_data_update(content, filename)
        else:
            data = {}
        repo.update(data)
        repo.file_name = filename
        repo.file_path = file_path
