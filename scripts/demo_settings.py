from contextlib import chdir
from pathlib import Path

from sid_edit_ui.settings import Settings

if __name__ == '__main__':
    file_path = Path(__file__)
    scripts_dir = file_path.parent
    project_dir = scripts_dir.parent
    print(project_dir)
    with chdir(project_dir):
        settings = Settings()
        print(settings.model_dump())
