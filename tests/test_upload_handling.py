from pathlib import Path

from sid_edit_ui.editor.handlers import (
    _make_prg_update,
    _make_data_update,
    handle_upload,
)
from sid_edit_ui.repositories.sid_repository import SIDFileRepository

_SID_FILE = Path(__file__).parent / "data" / "Metal_Dust_Title_Remix.sid"


# -- _make_prg_update unit tests --


def test_make_prg_update_uses_little_endian_address():
    content = b"\x00\x10\xa9\x00\x8d\x18\xd0\x60"
    result = _make_prg_update(content, "music.prg")
    assert result["init_address"] == 0x1000
    assert result["play_address"] == 0x1003


def test_make_prg_update_sets_c64_data():
    content = b"\x00\x10\xa9\x00\x8d\x18\xd0\x60"
    result = _make_prg_update(content, "music.prg")
    assert result["c64_data"] == content


def test_make_prg_update_uses_filename_stem():
    content = b"\x00\x10\xa9\x00"
    result = _make_prg_update(content, "my_tune.prg")
    assert result["name"] == "my_tune"


def test_make_prg_update_handles_different_address():
    content = b"\x01\x10\xa9\x00"
    result = _make_prg_update(content, "tune.prg")
    assert result["init_address"] == 0x1001
    assert result["play_address"] == 0x1004


def test_make_prg_update_no_load_address():
    result = _make_prg_update(b"\x00\x10\xa9\x00", "tune.prg")
    assert "load_address" not in result


# -- _make_data_update unit tests --


def test_make_data_update_uses_fixed_0x1000():
    content = b"\x00\x10\xa9\x00\x8d\x18\xd0\x60"
    result = _make_data_update(content, "music.data")
    assert result["load_address"] == 0x1000
    assert result["init_address"] == 0x1000
    assert result["play_address"] == 0x1003


def test_make_data_update_sets_c64_data():
    content = b"\x00\x10\xa9\x00\x8d\x18\xd0\x60"
    result = _make_data_update(content, "music.data")
    assert result["c64_data"] == content


def test_make_data_update_uses_filename_stem():
    content = b"\x00\x10\xa9\x00"
    result = _make_data_update(content, "my_data.data")
    assert result["name"] == "my_data"


def test_make_data_update_address_independent_of_content():
    content = b"\x34\x12\xa9\x00"
    result = _make_data_update(content, "tune.data")
    assert result["load_address"] == 0x1000
    assert result["init_address"] == 0x1000
    assert result["play_address"] == 0x1003


# -- handle_upload integration tests --


def test_handle_upload_sid_writes_file_and_loads(tmp_path):
    sid_bytes = _SID_FILE.read_bytes()
    repo = SIDFileRepository()

    handle_upload(sid_bytes, "song.sid", repo, tmp_path)

    file_path = tmp_path / "song.sid"
    assert file_path.exists()
    assert file_path.read_bytes() == sid_bytes
    assert repo.file_name == "song.sid"
    assert repo.file_path == file_path


def test_handle_upload_sid_repo_has_sid_data(tmp_path):
    sid_bytes = _SID_FILE.read_bytes()
    repo = SIDFileRepository()

    handle_upload(sid_bytes, "song.sid", repo, tmp_path)

    assert repo.sid_file.name == "Metal Dust Title Remix"
    assert repo.sid_file.format_type == "PSID"


def test_handle_upload_prg_writes_file_and_updates_repo(tmp_path):
    content = b"\x00\x10\xa9\x00\x8d\x18\xd0\x60"
    repo = SIDFileRepository()

    handle_upload(content, "music.prg", repo, tmp_path)

    file_path = tmp_path / "music.prg"
    assert file_path.exists()
    assert file_path.read_bytes() == content
    assert repo.file_name == "music.prg"
    assert repo.file_path == file_path
    assert repo.sid_file.init_address == 0x1000
    assert repo.sid_file.play_address == 0x1003
    assert repo.sid_file.name == "music"


def test_handle_upload_prg_no_load_address_in_sid(tmp_path):
    content = b"\x00\x10\xa9\x00"
    repo = SIDFileRepository()

    handle_upload(content, "tune.prg", repo, tmp_path)

    assert repo.sid_file.load_address == 0


def test_handle_upload_data_writes_file_and_updates_repo(tmp_path):
    content = b"\x34\x12\xa9\x00"
    repo = SIDFileRepository()

    handle_upload(content, "song.data", repo, tmp_path)

    file_path = tmp_path / "song.data"
    assert file_path.exists()
    assert file_path.read_bytes() == content
    assert repo.file_name == "song.data"
    assert repo.file_path == file_path
    assert repo.sid_file.load_address == 0x1000
    assert repo.sid_file.init_address == 0x1000
    assert repo.sid_file.play_address == 0x1003
    assert repo.sid_file.name == "song"


def test_handle_upload_sid_calls_load_and_not_init(mocker, tmp_path):
    sid_bytes = _SID_FILE.read_bytes()
    mock_load = mocker.patch(
        "sid_edit_ui.repositories.sid_repository.SIDFileRepository.load"
    )
    mock_init = mocker.patch(
        "sid_edit_ui.repositories.sid_repository.SIDFileRepository.init"
    )

    handle_upload(sid_bytes, "song.sid", SIDFileRepository(), tmp_path)

    mock_load.assert_called_once()
    mock_init.assert_not_called()
    call_path = mock_load.call_args[0][0]
    assert call_path == tmp_path / "song.sid"


def test_handle_upload_prg_calls_init_and_not_load(mocker, tmp_path):
    content = b"\x00\x10\xa9\x00"
    mock_init = mocker.patch(
        "sid_edit_ui.repositories.sid_repository.SIDFileRepository.init"
    )
    mock_load = mocker.patch(
        "sid_edit_ui.repositories.sid_repository.SIDFileRepository.load"
    )

    handle_upload(content, "tune.prg", SIDFileRepository(), tmp_path)

    mock_init.assert_called_once()
    mock_load.assert_not_called()
