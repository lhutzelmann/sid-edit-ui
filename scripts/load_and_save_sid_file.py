import pathlib

from sid_edit_ui.repositories.sid_repository import sid_file_repo
from sid_file_format.sidfile import SIDFile

if __name__ == "__main__":
    sid_file_path = pathlib.Path("Metal_Dust_Title_Remix.sid")
    sid_file_repo.load(sid_file_path)
    print(sid_file_repo.sid_file.model_dump_json(indent=2))

    out_file_path = pathlib.Path("out.sid")
    sid_file_repo.save(out_file_path)
    print(f"file written to {sid_file_repo.file_path}")
