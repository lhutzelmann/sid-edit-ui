from collections.abc import Sequence

from htmy import XBool, html

from sid_edit_ui.utils import c64_video_codes_to_unicode


def input_field(
    name: str, data: dict, label: str, placeholder: str, type_: str = "text"
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


def select_field(
    name: str,
    data: dict,
    label: str,
    options: Sequence[tuple[int | str, str]],
    class_: str = "input-sm",
):
    current = str(data.get(name, ""))
    return html.div(
        html.label(label),
        html.select(
            *(
                html.option(
                    text, value=str(v),                     selected=XBool(str(v) == current)
                )
                for v, text in options
            ),
            name=name,
            class_=class_,
        ),
    )


def hex_field(
    name: str,
    data: dict,
    label: str,
    num_digits: int = 4,
    class_: str = "input-sm",
):
    value = data.get(name)
    if value is None:
        hex_str = ""
    elif isinstance(value, int):
        hex_str = format(value, f"0{num_digits}X")
    else:
        hex_str = str(value)
    return html.div(
        html.label(label),
        html.input_(
            type="text",
            name=name,
            value=hex_str,
            class_=class_,
            placeholder="0" * num_digits,
        ),
    )


def number_field(
    name: str,
    data: dict,
    label: str,
    min: int | None = None,
    max: int | None = None,
    class_: str = "input-sm",
):
    value = data.get(name)
    str_value = "" if value is None else str(value)
    return html.div(
        html.label(label),
        html.input_(
            type="number",
            name=name,
            value=str_value,
            class_=class_,
            min=min,
            max=max,
        ),
    )


def hex_display(
    data: dict,
    label: str = "C64 Data",
    max_bytes: int = 4096,
):
    raw = data.get("c64_data", b"")
    if isinstance(raw, bytes):
        hex_str = raw.hex()
        raw_bytes = raw
    elif isinstance(raw, str):
        hex_str = raw
        raw_bytes = bytes.fromhex(raw)
    else:
        hex_str = ""
        raw_bytes = b""

    pairs = [hex_str[i : i + 2] for i in range(0, len(hex_str), 2)]
    truncated = len(pairs) > max_bytes
    if truncated:
        pairs = pairs[:max_bytes]
        raw_bytes = raw_bytes[:max_bytes]

    lines = []
    for i in range(0, len(pairs), 16):
        byte_values = " ".join(pairs[i : i + 16])
        ascii_display = c64_video_codes_to_unicode(raw_bytes[i : i + 16])
        lines.append(f"{byte_values} : {ascii_display}")
    text = "\n".join(lines)
    if truncated:
        text += "\n..."

    return html.div(
        html.label(label),
        html.pre(text, style="font-family:monospace;font-size:0.8em;line-height:1.4"),
    )


def field_block(title: str, *children, vertical: bool = False):
    flex_style = (
        "display:flex;flex-direction:column;gap:0.5rem;"
        if vertical
        else "display:flex;flex-wrap:wrap;gap:1rem;align-items:flex-end;"
    )
    return html.div(
        html.strong(title, style="display:block;margin-bottom:0.5rem;font-size:0.9rem;"),
        html.div(*children, style=flex_style),
        style=(
            "border:1px solid #d0d0d0;border-radius:8px;padding:1rem;"
            "margin-bottom:0.75rem;background:#fafafa;"
        ),
    )
