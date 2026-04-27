import uvicorn


def main():
    uvicorn.run("sid_edit_ui.main:app", host="localhost", port=8000, reload=True)


if __name__ == "__main__":
    main()
