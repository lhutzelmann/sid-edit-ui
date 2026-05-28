from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from sid_edit_ui.file.handlers import (
    _make_data_update,
    _make_prg_update,
    handle_upload,
)
from sid_edit_ui.repositories.sid_repository import SIDFileRepository
from sid_edit_ui.settings import Settings

_SID_FILE = Path(__file__).parent / "data" / "Metal_Dust_Title_Remix.sid"


@pytest.fixture(autouse=True, scope="function")
def mock_settings(mocker: MockerFixture):
    mocked_settings = mocker.MagicMock(spec=Settings)
    settings = Settings()
    for key, value in settings.model_dump().items():
        mocked_settings.__setattr__(key, value)
    mocker.patch(
        "sid_edit_ui.repositories.sid_repository.get_settings",
        return_value=mocked_settings,
    )
    mocker.patch("sid_edit_ui.file.handlers.get_settings", return_value=mocked_settings)
    return mocked_settings


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


def test_handle_upload_sid_writes_file_and_loads(mock_settings, tmp_path: Path):
    mock_settings.upload_dir = tmp_path
    sid_bytes = _SID_FILE.read_bytes()
    repo = SIDFileRepository()

    handle_upload(sid_bytes, "song.sid", repo)

    file_path = tmp_path / "song.sid"
    assert file_path.exists()
    assert file_path.read_bytes() == sid_bytes
    assert repo.file_name == "song.sid"
    assert repo.file_path == file_path


def test_handle_upload_sid_repo_has_sid_data(mock_settings, tmp_path):
    mock_settings.upload_dir = tmp_path
    sid_bytes = _SID_FILE.read_bytes()
    repo = SIDFileRepository()

    handle_upload(sid_bytes, "song.sid", repo)

    assert repo.sid_file.name == "Metal Dust Title Remix"
    assert repo.sid_file.format_type == "PSID"


def test_handle_upload_prg_writes_file_and_updates_repo(mock_settings, tmp_path):
    """
    The handler should both save the original uploaded file, convert it to a SID file and save that as well.
    The repository should then refer only to the new SID file.
    """
    mock_settings.upload_dir = tmp_path
    content = b"\x00\x10\xa9\x00\x8d\x18\xd0\x60"
    repo = SIDFileRepository()

    handle_upload(content, "music.prg", repo)

    file_path = tmp_path / "music.prg"
    assert file_path.exists()
    assert file_path.read_bytes() == content
    sid_file_path = tmp_path / "music.sid"
    assert sid_file_path.exists()
    assert repo.file_name == "music.sid"
    assert repo.file_path == sid_file_path
    assert repo.sid_file.init_address == 0x1000
    assert repo.sid_file.play_address == 0x1003
    assert repo.sid_file.name == "music"


def test_handle_upload_prg_no_load_address_in_sid(mock_settings, tmp_path):
    mock_settings.upload_dir = tmp_path
    content = b"\x00\x10\xa9\x00"
    repo = SIDFileRepository()

    handle_upload(content, "tune.prg", repo)

    assert repo.sid_file.load_address == 0


def test_handle_upload_data_writes_file_and_updates_repo(mock_settings, tmp_path):
    """
    The handler should both save the original uploaded file, convert it to a SID file and save that as well.
    The repository should then refer only to the new SID file.
    """

    mock_settings.upload_dir = tmp_path
    content = b"\x34\x12\xa9\x00"
    repo = SIDFileRepository()

    handle_upload(content, "song.data", repo)

    file_path = tmp_path / "song.data"
    assert file_path.exists()
    assert file_path.read_bytes() == content
    sid_file_path = tmp_path / "song.sid"
    assert sid_file_path.exists()
    assert repo.file_name == "song.sid"
    assert repo.file_path == sid_file_path
    assert repo.sid_file.load_address == 0x1000
    assert repo.sid_file.init_address == 0x1000
    assert repo.sid_file.play_address == 0x1003
    assert repo.sid_file.name == "song"


def test_handle_upload_sid_calls_load_and_not_init(mocker, mock_settings, tmp_path):
    mock_settings.upload_dir = tmp_path
    sid_bytes = _SID_FILE.read_bytes()
    mock_load = mocker.patch(
        "sid_edit_ui.repositories.sid_repository.SIDFileRepository.load"
    )
    mock_init = mocker.patch(
        "sid_edit_ui.repositories.sid_repository.SIDFileRepository.init"
    )

    handle_upload(sid_bytes, "song.sid", SIDFileRepository())

    mock_load.assert_called_once()
    mock_init.assert_not_called()
    call_path = mock_load.call_args[0][0]
    assert call_path == tmp_path / "song.sid"


def test_handle_upload_prg_calls_init_and_not_load(mocker, mock_settings, tmp_path):
    mock_settings.upload_dir = tmp_path
    content = b"\x00\x10\xa9\x00"
    mock_init = mocker.patch(
        "sid_edit_ui.repositories.sid_repository.SIDFileRepository.init"
    )
    mock_load = mocker.patch(
        "sid_edit_ui.repositories.sid_repository.SIDFileRepository.load"
    )

    handle_upload(content, "tune.prg", SIDFileRepository())

    mock_init.assert_called_once()
    mock_load.assert_not_called()
