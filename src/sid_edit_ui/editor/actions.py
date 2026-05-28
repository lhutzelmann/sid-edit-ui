from holm import action

from sid_edit_ui.editor.page import page_content
from sid_edit_ui.repositories.sid_repository import (
    DependsSidFileRepo,
)


@action.post()
def load_sid_file(repo: DependsSidFileRepo):
    repo.load(repo.file_path)
    print(f"Loaded {repo.file_name}.")
    return page_content(repo.sid_file, repo.file_name)
