from htmy import Component, html

# Static metadata for this page
metadata = {"title": "Home | My App"}


def page() -> Component:
    """Home page content."""

    return html.div(
        html.h1("Welcome to the SID Edit UI"),
        html.p("With this little web app you can edit and create SID files."),
        html.ul(
            html.li("Python powered"),
            html.li("Follows the SID file format specs."),
        ),
        html.a("Learn more about the application", href="/about"),
    )
