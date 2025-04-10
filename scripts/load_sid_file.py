import pathlib

from sid_edit_ui.datafields.sidfile import SIDFile

if __name__ == "__main__":
    sid_file_path = pathlib.Path("Metal_Dust_Title_Remix.sid")
    sid_file_data: bytes = sid_file_path.read_bytes()
    sid_file = SIDFile.from_sid(sid_file_data)
    print(sid_file.model_dump_json(indent=2))
