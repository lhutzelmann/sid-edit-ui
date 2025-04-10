from enum import StrEnum, IntEnum
from typing import Self, Any

from pydantic import (
    BaseModel,
    Field,
    conint,
    constr,
    model_validator,
    errors,
    PlainValidator,
    PlainSerializer,
)
from typing_extensions import Annotated


def as_bit(value: int) -> int:
    return 1 if value > 0 else 0


def as_byte(value: int) -> bytes:
    return value.to_bytes(length=1, byteorder="little")


def as_word(value: int) -> bytes:
    return value.to_bytes(length=2, byteorder="big")


def int_from_bytes(value: bytes) -> int:
    return int.from_bytes(value, byteorder="big")


def as_long_word(value: int) -> bytes:
    return value.to_bytes(length=4, byteorder="big")


def as_32_byte_string(value: str) -> bytes:
    filler: str = "\0" * 32
    filled_value = value + filler
    cropped = filled_value[:32]
    assert len(cropped) == 32
    return cropped.encode(encoding="cp1252")


def str_from_bytes(value: bytes) -> str:
    text = value.decode(encoding="cp1252")
    text = text.replace("\0", "")  # Remove padding 00 bytes
    return text


def as_c64_word(value: int) -> bytes:
    return value.to_bytes(length=2, byteorder="little")


def hex_bytes_validator(val: Any) -> bytes:
    if isinstance(val, bytes):
        return val
    elif isinstance(val, bytearray):
        return bytes(val)
    elif isinstance(val, str):
        return bytes.fromhex(val)
    raise errors.BytesError()


HexBytes = Annotated[
    bytes, PlainValidator(hex_bytes_validator), PlainSerializer(lambda v: v.hex())
]


class MagicId(StrEnum):
    PSID = "PSID"
    RSID = "RSID"

    def as_bytes(self) -> bytes:
        return self.encode("ascii")


class MusPlayer(IntEnum):
    BUILT_IN = 0
    COMPUTE_SIDPLAYER = 1


class PSIDSpecific(IntEnum):
    C64_COMPATIBLE = 0
    PLAYSID_SPECIFIC = 1  # PSID format, PlaySID samples
    C64_BASIC = 2  # RSID format, C64 Basic file


class VideoStandard(IntEnum):
    UNKNOWN = 0
    PAL = 1
    NTSC = 2
    PAL_AND_NTSC = 3


class SIDModel(IntEnum):
    UNKNOWN = 0
    MOS_6581 = 1
    MOS_8580 = 2
    MOS_BOTH = 3


class Flags(BaseModel):
    mus_player: MusPlayer = Field(
        default=MusPlayer.BUILT_IN,
        description="Flag indicating integrated player or Compute's Sidplayer MUS data.",
    )
    psid_specific: PSIDSpecific = Field(
        default=PSIDSpecific.C64_COMPATIBLE,
        description="Flag indicating additional environment requirements.",
    )
    video_standard: VideoStandard = Field(
        default=VideoStandard.UNKNOWN,
        description="Two bits indicating the targeted video standard. v2NG specific.",
    )
    sid_model: SIDModel = Field(
        default=SIDModel.UNKNOWN,
        description="Two bits indicating the targeted SID model. v2NG specific.",
    )
    sid_model_2nd_sid: SIDModel = Field(
        default=SIDModel.UNKNOWN,
        description="Two bits indicating the targeted SID model of a second SID. v3 specific.",
    )
    sid_model_3rd_sid: SIDModel = Field(
        default=SIDModel.UNKNOWN,
        description="Two bits indicating the targeted SID model of a third SID. v4 specific.",
    )

    def to_word(self):
        reversed_field = [
            as_bit(self.mus_player),  # 0
            as_bit(self.psid_specific),  # 1
            as_bit(self.video_standard & 1),  # 2
            as_bit(self.video_standard & 2),  # 3
            as_bit(self.sid_model & 1),  # 4
            as_bit(self.sid_model & 2),  # 5
            as_bit(self.sid_model_2nd_sid & 1),  # 6
            as_bit(self.sid_model_2nd_sid & 2),  # 7
            as_bit(self.sid_model_3rd_sid & 1),  # 8
            as_bit(self.sid_model_3rd_sid & 2),  # 9
        ]
        value = 0
        for bit in reversed(reversed_field):
            value = (value << 1) + bit
        return as_word(value)

    @classmethod
    def from_word(cls, data: bytes, is_rsid: bool) -> "Flags":
        def next_bit(v) -> (int, int):
            b = v & 1
            v = v >> 1
            return b, v

        v = int_from_bytes(data)
        b, v = next_bit(v)
        mus_player = MusPlayer(b)
        b, v = next_bit(v)
        psid_specific = (
            PSIDSpecific(b) if b == 0 or not is_rsid else PSIDSpecific.C64_BASIC
        )
        video_standard = VideoStandard(v & 3)
        v = v >> 2
        sid_model = SIDModel(v & 3)
        v = v >> 2
        sid_model_2nd_sid = SIDModel(v & 3)
        v = v >> 2
        sid_model_3rd_sid = SIDModel(v & 3)
        return cls(
            mus_player=mus_player,
            psid_specific=psid_specific,
            video_standard=video_standard,
            sid_model=sid_model,
            sid_model_2nd_sid=sid_model_2nd_sid,
            sid_model_3rd_sid=sid_model_3rd_sid,
        )


class SIDFile(BaseModel):
    format_type: MagicId = Field(
        default=MagicId.PSID,
        description="One of the two supported formats: PSID or RSID",
    )
    version: conint(ge=1, le=4) = Field(
        default=2, description="Version, also depends on number of SID chips"
    )
    load_address: conint(ge=0, le=0xFFFF) = Field(
        default=0,
        description="C64 memory location of the C64 data or 0 if data has load address bytes already",
    )
    init_address: conint(ge=0, le=0xFFFF) = Field(
        default=0x1000,
        description="Start address of the machine code subroutine that initializes a song",
    )
    play_address: conint(ge=0, le=0xFFFF) = Field(
        default=0x1003,
        description="Play address of the machine code subroutine that is called frequently or 0 for RSID.",
    )
    songs: conint(ge=1, le=0x0100) = Field(
        default=1,
        description="The number of songs/sfx that can be initialized by calling the init address.",
    )
    start_song: conint(ge=1, le=0x0100) = Field(
        default=1,
        description="The song number played as default.",
    )
    speed: conint(ge=0, le=0xFFFFFFFF) = Field(
        default=0,
        description="Speed flags for the songs. See sid file format description for details.",
    )
    name: constr(min_length=0, max_length=32) = Field(
        default="SONGNAME",
        description="Song name.",
    )
    author: constr(min_length=0, max_length=32) = Field(
        default="First Last (Handle)",
        description="Author information. Should be author's real name plus handle in brackets.",
    )
    released: constr(min_length=0, max_length=32) = Field(
        default="2025 Organisation",
        description="Release information. Should be year and the releasing organisation.",
    )

    # v2, v3 and v4 extensions
    flags: Flags | None = Field(
        default=None, description="Bitfield with format specific flags."
    )
    start_page: conint(ge=0, le=0xFF) | None = Field(
        default=None,
        description="Relocation start page, free to use start page, e.g. for relocation purposes. See docs for details",
    )
    page_length: conint(ge=0, le=0xFF) | None = Field(
        default=None,
        description="Amount of free to use pages after the start_page. See docs for details",
    )
    second_sid_address: conint(ge=0, le=0xFF) | None = Field(
        default=None,
        description="Low byte of second SID address for v3+ or 0 for v2NG.",
    )
    third_sid_address: conint(ge=0, le=0xFF) | None = Field(
        default=None,
        description="Low byte of third SID address for v4 or 0 for v2NG and v3.",
    )

    c64_data: HexBytes = Field(
        default=b"\0\0",
        description="C64 file data representing the SID music for the C64/128.",
    )

    def data_offset_as_bytes(self) -> bytes:
        if self.version == 1:
            return as_word(0x76)
        else:
            return as_word(0x7C)

    @model_validator(mode="after")
    def check(self) -> Self:
        if self.format_type == MagicId.RSID:
            if self.load_address > 0:
                raise ValueError("RSID format requires load_address field to be 0.")
            if (
                self.init_address == 0
                and self.flags.psid_specific != PSIDSpecific.C64_BASIC
            ):
                raise ValueError("RSID allows 0 only if C64 BASIC flag is set as well.")
            if 0xA000 <= self.init_address <= 0xBFFF:
                raise ValueError("RSID does not allow init addresses in BASIC ROM.")
            if 0xD000 <= self.init_address <= 0xFFFF:
                raise ValueError(
                    "RSID does not allow init addresses in IO or kernal ROM area."
                )
            if self.speed != 0:
                raise ValueError("RSID does not allow speed != 0.")
            if (
                self.version > 1
                and self.flags.psid_specific == PSIDSpecific.PLAYSID_SPECIFIC
            ):
                raise ValueError("RSID does not support PlaySID samples.")
        else:
            if self.version > 1 and self.flags.psid_specific == PSIDSpecific.C64_BASIC:
                raise ValueError("PSID does not support Basic files.")
        if self.version == 1:
            if (
                self.flags is not None
                or self.start_page is not None
                or self.page_length is not None
                or self.second_sid_address is not None
                or self.third_sid_address is not None
            ):
                raise ValueError("v1 does not support extended fields.")
        if self.version == 2:
            if (
                self.flags is None
                or self.start_page is None
                or self.page_length is None
            ):
                raise ValueError("PSID >= v2NG requires extended fields.")
            if self.flags.sid_model_2nd_sid != SIDModel.UNKNOWN:
                raise ValueError("v2NG must not have second SID model set.")
            if self.second_sid_address != 0:
                raise ValueError("v2NG must have second SID address == 0.")
            if self.flags.sid_model_3rd_sid != SIDModel.UNKNOWN:
                raise ValueError("v2NG must not have third SID model set.")
            if self.third_sid_address != 0:
                raise ValueError("v2NG must have third SID address == 0.")
        if self.version == 3:
            if (
                self.flags is None
                or self.start_page is None
                or self.page_length is None
                or self.second_sid_address is None
            ):
                raise ValueError("PSID >= v2NG requires extended fields.")
            if (
                not self.second_sid_address == 0
                and not (0x42 <= self.second_sid_address <= 0x7E)
                and not (0xE0 <= self.second_sid_address <= 0xFE)
                and not self.second_sid_address & 1 == 0
            ):
                raise ValueError("Invalid address for second SID.")
            if self.flags.sid_model_3rd_sid != SIDModel.UNKNOWN:
                raise ValueError("v3 must not have third SID model set.")
            if self.third_sid_address != 0:
                raise ValueError("v3 must have third SID address == 0.")
        if self.version == 4:
            if (
                self.flags is None
                or self.start_page is None
                or self.page_length is None
                or self.second_sid_address is None
                or self.third_sid_address is None
            ):
                raise ValueError("PSID >= v2NG requires extended fields.")
            if (
                not self.second_sid_address == 0
                and not (0x42 <= self.second_sid_address <= 0x7E)
                and not (0xE0 <= self.second_sid_address <= 0xFE)
                and not self.second_sid_address & 1 == 0
            ):
                raise ValueError("Invalid address for second SID.")
            if (
                not self.third_sid_address == 0
                and not (0x42 <= self.third_sid_address <= 0x7E)
                and not (0xE0 <= self.third_sid_address <= 0xFE)
                and not self.third_sid_address & 1 == 0
            ):
                raise ValueError("Invalid address for third SID.")
        return self

    def to_sid(self) -> bytes:
        common_header: list[bytes] = [
            self.format_type.as_bytes(),
            as_word(self.version),
            self.data_offset_as_bytes(),
            as_word(self.load_address),
            as_word(self.init_address),
            as_word(self.play_address),
            as_word(self.songs),
            as_word(self.start_song),
            as_long_word(self.speed),
            as_32_byte_string(self.name),
            as_32_byte_string(self.author),
            as_32_byte_string(self.released),
        ]
        additional_header: list[bytes] = []
        if self.version > 1:
            additional_header += [
                self.flags.to_word(),
                as_byte(self.start_page),
                as_byte(self.page_length),
                as_byte(self.second_sid_address),
                as_byte(self.third_sid_address),
            ]

        all_fields = common_header + additional_header + [self.c64_data]
        return b"".join(all_fields)

    @classmethod
    def from_sid(cls, sid_data: bytes):
        format_type: MagicId = MagicId(sid_data[0x0:0x4].decode("ascii"))
        version: int = int_from_bytes(sid_data[0x4:0x6])
        data_offset: int = 0x76 if version == 1 else 0x7C
        sid_file_data_offset: int = int_from_bytes(sid_data[0x6:0x8])
        if sid_file_data_offset != data_offset:
            raise ValueError(
                f"Data offset of file {sid_file_data_offset} "
                f"differs from what the version demands {data_offset}"
            )
        c64_data: bytes = sid_data[data_offset:]

        common_header = dict(
            format_type=format_type,
            version=version,
            # Skip offset
            load_address=int_from_bytes(sid_data[0x8:0xA]),
            init_address=int_from_bytes(sid_data[0xA:0xC]),
            play_address=int_from_bytes(sid_data[0xC:0xE]),
            songs=int_from_bytes(sid_data[0xE:0x10]),
            start_song=int_from_bytes(sid_data[0x10:0x12]),
            speed=int_from_bytes(sid_data[0x12:0x16]),
            name=str_from_bytes(sid_data[0x16:0x36]),
            author=str_from_bytes(sid_data[0x36:0x56]),
            released=str_from_bytes(sid_data[0x56:0x76]),
        )
        if version > 1:
            flags = Flags.from_word(
                sid_data[0x76:0x78], is_rsid=format_type == MagicId.RSID
            )

            additional_header = dict(
                flags=flags,
                start_page=sid_data[0x78],
                page_length=sid_data[0x79],
                second_sid_address=sid_data[0x7A],
                third_sid_address=sid_data[0x7B],
            )
        else:
            additional_header = {}

        data_block = dict(c64_data=c64_data)

        complete_model = common_header | additional_header | data_block

        return cls.model_validate(complete_model)
