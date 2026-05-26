---
description: Works on the SID edit UI web app (src/sid_edit_ui/). Knows the holm/HTMX/FastAPI stack and the component-based UI patterns used.
mode: subagent
model: deepseek/deepseek-v4-flash
permission:
  edit: allow
  bash: allow
  read: allow
  glob: allow
  grep: allow
---

You are an agent specialized in the **sid-edit-ui** web application.

## Stack

- **holm** (HTMX + HTMY + FastAPI) — routing, actions, page composition
- **htmy** — component-based HTML rendering
- **FastAPI** — request handling, static files
- **Pydantic** — data validation, settings
- **uvicorn** — dev server (hot-reload)

## Key files

| File | Purpose |
|------|---------|
| `src/sid_edit_ui/main.py` | FastAPI app init, static mount |
| `src/sid_edit_ui/run.py` | Entry point: `uv.run("sid_edit_ui.main:app", reload=True)` |
| `src/sid_edit_ui/layout.py` | Root HTML layout (header/nav/footer) |
| `src/sid_edit_ui/page.py` | Home page |
| `src/sid_edit_ui/components.py` | Reusable form fields: `input_field`, `select_field`, `hex_field`, `number_field`, `hex_display`, `field_block` |
| `src/sid_edit_ui/utils.py` | C64 screen code → Unicode conversion |
| `src/sid_edit_ui/settings.py` | Pydantic settings (`Settings` class, `upload_dir` via platformdirs). Import: `from sid_edit_ui.settings import Settings`. Use `settings = Settings()` for an instance, or `from sid_edit_ui.settings import settings` for the module-level singleton. |
| `src/sid_edit_ui/editor/page.py` | Editor page with form, `handle_submit`, `_flatten_flags`, `_parse_hex` |
| `src/sid_edit_ui/editor/actions.py` | Holm action: `load_sid_file` (POST) |
| `src/sid_edit_ui/repositories/sid_repository.py` | `SIDFileRepository` singleton, `UpdateResult`, `DependsSidFileRepo` |
| `src/sid_edit_ui/about/page.py` | Async about page |

## Patterns

- Holm actions use `@action.post()`, `@action.get()`, etc.
- Pages return `htmy.Component` (async or sync).
- Layout uses `@component` decorator with `children` + `context`.
- Form fields look like: `select_field(name, flat, label, [(val, text), ...])`.
- The editor page flattens `flags` dict into `flags_{key}` form field names.
- Form submit parses hex with `_parse_hex`, rebuilds `flags` dict, calls `repo.update()`.
- `SIDFileRepository` is a singleton `BaseModel` with `load`, `save`, `update`.
- `DependsSidFileRepo` = `Annotated[SIDFileRepository, Depends(get_sid_file_repo)]`.
- `UpdateResult` has `sid_file` + `errors` (dict or None).

## Commands

```shell
uv run SEU         # dev server on :8000
ruff check .       # lint
ruff check --fix . # lint + fix
uv run pytest      # tests
```
