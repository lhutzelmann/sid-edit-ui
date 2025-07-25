import pathlib

from sid_file_format.sidfile import SIDFile

if __name__ == "__main__":
    sid_file_path = pathlib.Path("Metal_Dust_Title_Remix.sid")
    sid_file_data: bytes = sid_file_path.read_bytes()
    sid_file = SIDFile.from_sid(sid_file_data)
    print(sid_file.model_dump_json(indent=2))
    out_file_data: bytes = sid_file.to_sid()
    out_file_path = pathlib.Path("out.sid")
    out_file_path.write_bytes(out_file_data)
    print(f"file written to {out_file_path}")
