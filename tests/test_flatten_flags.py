from enum import IntEnum
from pathlib import Path

from sid_edit_ui.editor.page import _flatten_flags

_SID_FILE = Path(__file__).parent / "data" / "Metal_Dust_Title_Remix.sid"


class _MusPlayer(IntEnum):
    BUILT_IN = 0
    COMPUTE_SIDPLAYER = 1


class _PSIDSpecific(IntEnum):
    C64_COMPATIBLE = 0
    PLAYSID_SPECIFIC = 1
    C64_BASIC = 2


class _VideoStandard(IntEnum):
    UNKNOWN = 0
    PAL = 1
    NTSC = 2
    PAL_AND_NTSC = 3


class _SIDModel(IntEnum):
    UNKNOWN = 0
    MOS_6581 = 1
    MOS_8580 = 2
    MOS_BOTH = 3


def _make_flags(
    mus_player=0,
    psid_specific=0,
    video_standard=0,
    sid_model=0,
    sid_model_2nd_sid=0,
    sid_model_3rd_sid=0,
):
    return {
        "mus_player": _MusPlayer(mus_player),
        "psid_specific": _PSIDSpecific(psid_specific),
        "video_standard": _VideoStandard(video_standard),
        "sid_model": _SIDModel(sid_model),
        "sid_model_2nd_sid": _SIDModel(sid_model_2nd_sid),
        "sid_model_3rd_sid": _SIDModel(sid_model_3rd_sid),
    }


def test_select_field_compatibility_with_intenum():
    """Ensure str() of IntEnum matches str() of int option values.

    The select_field function compares str(data_value) with str(option_value).
    IntEnum.__str__ must return the string of the int value for this to work.
    """
    data = {
        "flags": _make_flags(
            mus_player=0,
            psid_specific=0,
            video_standard=1,
        )
    }
    flat = _flatten_flags(data)

    # select_field does: current = str(data.get(name, ""))
    # then for each option: selected = (str(v) == current)

    assert str(flat["flags_mus_player"]) == "0"
    assert str(flat["flags_psid_specific"]) == "0"
    assert str(flat["flags_video_standard"]) == "1"

    # Simulate select_field matching logic
    mus_player_options = [(0, "Built-in"), (1, "Compute Sidplayer")]
    current = str(flat["flags_mus_player"])
    matched = [str(v) == current for v, _ in mus_player_options]
    assert matched == [True, False], (
        f"Expected Built-in to be selected, got {matched} (current={current!r})"
    )

    psid_options = [
        (0, "C64 Compatible"),
        (1, "PlaySID Specific"),
        (2, "C64 Basic"),
    ]
    current = str(flat["flags_psid_specific"])
    matched = [str(v) == current for v, _ in psid_options]
    assert matched == [True, False, False], (
        f"Expected C64 Compatible to be selected, got {matched} (current={current!r})"
    )

    video_options = [
        (0, "Unknown"),
        (1, "PAL"),
        (2, "NTSC"),
        (3, "PAL & NTSC"),
    ]
    current = str(flat["flags_video_standard"])
    matched = [str(v) == current for v, _ in video_options]
    assert matched == [False, True, False, False], (
        f"Expected PAL to be selected, got {matched} (current={current!r})"
    )


def test_select_field_with_nondefault_intenum():
    """Non-default IntEnum values should match correctly in select_field logic."""
    data = {
        "flags": _make_flags(
            mus_player=1,
            psid_specific=2,
            video_standard=3,
        )
    }
    flat = _flatten_flags(data)

    mus_player_options = [(0, "Built-in"), (1, "Compute Sidplayer")]
    current = str(flat["flags_mus_player"])
    matched = [str(v) == current for v, _ in mus_player_options]
    assert matched == [False, True]

    psid_options = [
        (0, "C64 Compatible"),
        (1, "PlaySID Specific"),
        (2, "C64 Basic"),
    ]
    current = str(flat["flags_psid_specific"])
    matched = [str(v) == current for v, _ in psid_options]
    assert matched == [False, False, True]

    video_options = [
        (0, "Unknown"),
        (1, "PAL"),
        (2, "NTSC"),
        (3, "PAL & NTSC"),
    ]
    current = str(flat["flags_video_standard"])
    matched = [str(v) == current for v, _ in video_options]
    assert matched == [False, False, False, True]


def test_flatten_flags_with_none():
    """When flags is None, all flag fields should be set to 0."""
    data = {"flags": None}
    flat = _flatten_flags(data)

    assert flat["flags_mus_player"] == 0
    assert flat["flags_psid_specific"] == 0
    assert flat["flags_video_standard"] == 0
    assert flat["flags_sid_model"] == 0
    assert flat["flags_sid_model_2nd_sid"] == 0
    assert flat["flags_sid_model_3rd_sid"] == 0


def test_flatten_flags_removes_nested_flags():
    """The original nested 'flags' key should be removed so stale data isn't used."""
    data = {"flags": _make_flags(mus_player=0)}
    flat = _flatten_flags(data)

    assert "flags" not in flat, (
        "Nested 'flags' key persists alongside flattened values. "
        "This makes it possible for select_field to accidentally read from "
        "the nested dict if the flat dict is iterated or searched by key pattern."
    )


def test_flatten_flags_with_plain_ints():
    """Plain int values (as produced after form submission) should work."""
    data = {
        "flags": {
            "mus_player": 1,
            "psid_specific": 2,
            "video_standard": 3,
            "sid_model": 0,
            "sid_model_2nd_sid": 0,
            "sid_model_3rd_sid": 0,
        }
    }
    flat = _flatten_flags(data)

    assert flat["flags_mus_player"] == 1
    assert flat["flags_psid_specific"] == 2
    assert flat["flags_video_standard"] == 3


def test_flatten_flags_missing_flags_key():
    """When 'flags' key is missing, the dict is returned as-is."""
    data = {"name": "test", "version": 2}
    flat = _flatten_flags(data)

    assert flat is data
    assert "flags_mus_player" not in flat
    assert "flags" not in flat


def test_flatten_flags_preserves_other_keys():
    """Non-flags keys should be preserved."""
    data = {
        "name": "Test Song",
        "author": "Test Author",
        "version": 2,
        "flags": _make_flags(),
    }
    flat = _flatten_flags(data)

    assert flat["name"] == "Test Song"
    assert flat["author"] == "Test Author"
    assert flat["version"] == 2


def test_flatten_flags_with_live_sid_file():
    """Reproduce the exact bug scenario: load Metal_Dust, check flattened values."""
    from sid_file_format.sidfile import SIDFile

    sid = SIDFile.from_sid(_SID_FILE.read_bytes())
    data = sid.model_dump()
    flat = _flatten_flags(data)

    # Verify the intuition: these are the values we expect from this file
    assert str(flat["flags_mus_player"]) == "0"
    assert str(flat["flags_psid_specific"]) == "0"
    assert str(flat["flags_video_standard"]) == "1"
