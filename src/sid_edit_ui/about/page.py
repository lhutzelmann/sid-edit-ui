from htmy import Component, html


async def page() -> Component:
    """Async about page."""
    return html.div(
        html.h1("About SID Edit UI"),
        html.p(
            "I created this little app as I could not find one that fully supported the full set of specifications."
        ),
        html.h2("Info"),
        html.p("Version: V1.0"),
        html.p("Programmed by Lars Hutzelmann (The Blue Ninja)"),
        html.h2("Thanks for the SID file formats go to"),
        html.p("Michael Schwendt (PSID v1 and v2)"),
        html.p("Simon White (PSID v2NG, RSID)"),
        html.p("Dag Lem (PSID v2NG)"),
        html.p("Wilfred Bos (PSID v3, RSID v3, PSID v4, RSID v4)"),
        html.p("LaLa (SID FILE FORMAT DESCRIPTION document)"),
        html.p("Jürgen Wothke (v4E)"),
    )
