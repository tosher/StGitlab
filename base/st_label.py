import itertools

from . import utils


class StLabel:
    EDGE_LIGHT = 150

    # label font-size 0.9 to base
    html_tpl = """
    <html>
    <style>
    html {{
        --bg: {icon_color}
    }}

    div.label {{
        color: {text_color};
        background-color:var(--bg);
        font-family: Consolas, Menlo, Tahoma, Courier, monospace;
        font-size: 0.9rem;
        padding-top: 2px;
        padding-left: 6px;
        padding-right: 6px;
        padding-bottom: 0;
        border-width: 1px;
        border-radius: 3px;
        border-style: solid;
        border-color: color(white blend(var(--bg) 40%));
        margin:0;
        margin-left:4px;
    }}

    div.in_note {{
        font-size: 0.7rem;
        padding-top: 0px;
        padding-bottom: 1px;
        margin-left:0px;
    }}

    div.in_note_grayed {{
        font-size: 0.7rem;
        background-color: color(var(--bg) blend(gray 30%));
        border-color: color(var(--bg) blend(gray 30%));
        padding-top: 0px;
        padding-bottom: 1px;
        margin-left:0px;
    }}

    </style>
    <body>
        <div class="{label_class}">{text}</div>
    </body>
    </html>"""

    def __init__(self, text: str, color: str, grayed: bool = False) -> None:
        self.text = text
        self.grayed = grayed
        self.color = color

    def get(self) -> str:
        is_grayout_labels_in_notes = utils.get_setting("grayed_out_labels_in_notes")
        label_class = "label" if not self.grayed else "label in_note_grayed" if is_grayout_labels_in_notes else "label in_note"
        return self.html_tpl.format(
            text=self.text,
            icon_color=self.color,
            text_color=self._blackwhite(self.color),
            label_class=label_class,
        )

    def _blackwhite(self, hexcolor: str) -> str:
        """
        Icon text color:
        * white - for dark icons
        * black - for light icons
        """
        hexcolor = hexcolor.lstrip("#")
        rgb = (int(hexcolor[0:2], 16), int(hexcolor[2:4], 16), int(hexcolor[4:6], 16))
        pairs = list(itertools.combinations(rgb, 2))
        for pair in pairs:
            if all([x < self.EDGE_LIGHT for x in pair]):
                return "#fff"
        return "#000"

    def _complimentary_color(self, hexcolor: str) -> str:
        return "#%06X" % (int(hexcolor.lstrip("#"), 16) ^ 0xFFFFFF)
