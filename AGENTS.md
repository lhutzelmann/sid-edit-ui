# AGENTS.md

## Project

**sid-edit-ui / SEU** — Cross-platform UI for editing C64 SID files.

Stack: Python >=3.12, [holm](https://holm.bow) (HTMX + HTMY + FastAPI), uvicorn, Pydantic, ruff.

## Dev setup

```shell
uv sync          # install dependencies
uv run SEU       # run dev server at http://localhost:8000
```

## Commands

| Command              | What                        |
|----------------------|-----------------------------|
| `uv run SEU`         | Run dev server (hot-reload) |
| `ruff check .`       | Lint all files              |
| `ruff check --fix .` | Lint + auto-fix             |
| `uv run pytest`      | Run tests                   |

## Project structure

```
sid-edit-ui/
├── src/sid_edit_ui/         # Main web app (holm/htmx)
│   ├── main.py              # FastAPI app setup
│   ├── run.py               # Entry point (uvicorn)
│   ├── layout.py            # Root HTML layout
│   ├── page.py              # Home page
│   ├── components.py        # Shared form field components (input/select/hex/number + field_block)
│   ├── utils.py             # C64 screen code conversion, int_from_c64_bytes, validated_update
│   ├── file/                # File management page
│   │   ├── page.py
│   │   ├── actions.py
│   │   └── handlers.py
│   ├── editor/              # SID editor pages
│   │   ├── page.py
│   │   └── actions.py
│   ├── repositories/        # Data access layer
│   │   └── sid_repository.py
│   ├── settings.py          # Pydantic-settings (Settings, upload_dir)
│   └── about/               # About page
│       └── page.py
├── packages/sid-file-format # SID file format library
│   └── src/sid_file_format/
├── tests/                   # Pytest tests
├── static/                  # CSS assets
├── docs/                    # SID format docs
├── scripts/                 # Utility scripts
├── pyproject.toml           # Root package config
└── uv.lock                  # Lockfile
```

## Conventions

- Format + lint: ruff (no mypy/pyright configured yet)
- Tests: pytest, in `tests/`
- No type checker is configured
