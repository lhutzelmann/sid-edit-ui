from holm import App

from fastapi.staticfiles import StaticFiles

app = App()


app.mount("/static", StaticFiles(directory="static"), name="static")
