from htmy import Component, html


async def page() -> Component:
    """Async Editor page."""
    return html.div(
        html.h1("Editor"),
        html.p("Coming soon..."),
    )
