from htmy import html


def input_field(
    name: str, data: dict[str, str], label: str, placeholder: str, type_: str = "text"
):
    return html.div(
        html.label(label),
        html.input_(
            type=type_,
            name=name,
            value=data.get(name, ""),
            placeholder=placeholder,
            class_="input-sm",
        ),
    )
