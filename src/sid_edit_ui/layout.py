from holm import Metadata
from htmy import Component, ComponentType, Context, component, html


@component
def layout(children: ComponentType, context: Context) -> Component:
    """Root layout wrapping all pages."""
    metadata = Metadata.from_context(context)

    return (
        html.DOCTYPE.html,
        html.html(
            html.head(
                html.title(metadata.get("title", "SID Edit UI")),
                html.meta(charset="utf-8"),
                html.meta(
                    name="viewport", content="width=device-width, initial-scale=1"
                ),
                html.link(  # Use mu css in blue
                    rel="stylesheet",
                    href="/static/mu.blue.css",
                ),
                html.script(src="https://unpkg.com/htmx.org@2.0.7"),
            ),
            html.body(
                html.header(
                    html.nav(
                        html.ul(
                            html.li(html.a("Home", href="/")),
                            html.li(html.a("Edit", href="/editor")),
                            html.li(html.a("About", href="/about")),
                        ),
                        hx_boost="true",
                        class_="container",
                    ),
                ),
                html.main(children, class_="container", id_="main"),
                html.footer(html.p("V1.0 by The Blue Ninja"), class_="container"),
            ),
        ),
    )
