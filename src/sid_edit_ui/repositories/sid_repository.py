from pathlib import Path
from typing import Any, Annotated

from fastapi import Depends
from pydantic import ValidationError, BaseModel

from sid_file_format.sidfile import SIDFile, Flags


class UpdateResult(BaseModel):
    sid_file: SIDFile
    errors: dict[str, str] | None





class SIDFileRepository(BaseModel):
    file_name: str|None = None
    file_path: Path | None = None
    sid_file: SIDFile = SIDFile(
            flags=Flags(),
            start_page=0,
            page_length=0,
            second_sid_address=0,
            third_sid_address=0,
        )

    def init(self):
        self.sid_file = SIDFile(
            flags=Flags(),
            start_page=0,
            page_length=0,
            second_sid_address=0,
            third_sid_address=0,
        )

    def load(self, sid_file_path: Path):
        sid_file_data: bytes = sid_file_path.read_bytes()
        self.file_path = sid_file_path
        self.file_name = sid_file_path.name
        self.sid_file = SIDFile.from_sid(sid_file_data)

    def save(self, sid_file_path: Path):
        out_file_data: bytes = self.sid_file.to_sid()
        sid_file_path.write_bytes(out_file_data)
        self.file_path = sid_file_path
        self.file_name = sid_file_path.name

    def update(self, data: dict[str, Any]) -> UpdateResult:
        errors_dict: dict[str, str] = {}
        updated_copy = self.sid_file.model_copy(update=data, deep=True)
        validated_sid_file: SIDFile | None = None
        try:
            validated_sid_file = SIDFile.model_validate(updated_copy.model_dump())
        except ValidationError as v:
            for error_details in v.errors():
                for loc in error_details["loc"]:
                    errors_dict[loc] = error_details["msg"]

        if errors_dict or validated_sid_file is None:
            return UpdateResult(sid_file=updated_copy, errors=errors_dict)
        else:
            self.sid_file = validated_sid_file
            return UpdateResult(sid_file=validated_sid_file, errors=None)


sid_file_repo: SIDFileRepository = SIDFileRepository()

def get_sid_file_repo() -> SIDFileRepository:
    return sid_file_repo

DependsSidFileRepo = Annotated[SIDFileRepository, Depends(get_sid_file_repo)]
