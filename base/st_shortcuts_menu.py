from __future__ import annotations
from typing import TYPE_CHECKING
import math

import sublime  # type:ignore

if TYPE_CHECKING:
    from typing import List, Union, Dict


class StShortcutsMenu(object):
    # keys font size is fixed
    html_tpl = """
    <html>
        <style>
            div.keyline {{
                margin-bottom: 0.6rem;
            }}

            span.kbd {{
                color: #444446;
                background-color: #F3F3F4;
                font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
                font-size: 8pt;
                padding: 2px;
                padding-left: 6px;
                padding-right: 6px;
                margin-right: 40px;
                border: 2px solid #DCDCDC;
                border-radius: 4px;
            }}

            span.kbd2 {{
                padding-left: 3px;
                padding-right: 3px;
            }}

            span.kbdplus {{
                color: #DCDCDC;
                font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
                font-size: 8pt;
                border-radius: 2px;
                padding: 2px;
                padding-left: 4px;
                padding-right: 4px;
            }}

            span.keyname {{
                color: #c0c0c0;
                font-size: 8pt;
                font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
                padding: 0.2rem;
                padding-left: 0.5rem;
                padding-right: 0;
            }}

            li {{
                margin-left: -40px;
                padding: 0.2rem;
            }}
        </style>
        <body id="gitlab" style="padding:0;margin:0;padding-top:-1rem;">
        {shortcuts}
        </body>
    </html>
    """

    html_col_tpl = '<div style="display: block;padding:0;margin:0;"><ul>{list}</ul></div>'
    html_shortcut_tpl = '<li>{keyname}<span class="keyname">{cmdname}</span></li>'
    html_key_tpl = '<span class="{kbdclass}">{key}</span>'
    html_key_plus = '<span class="kbdplus">+</span>'

    def __init__(self, view: sublime.View, shortcuts: Dict[str, List[str]], cols: Union[None, int, List[List[str]]] = 5) -> None:
        if not shortcuts:
            return
        if isinstance(cols, int):
            cols_cnt = cols
            cols = [[] for _ in range(cols_cnt)]
            for idx, k in enumerate(shortcuts.keys()):
                cols[self.key_col(cols_cnt, idx)].append(k)
        elif cols is None:
            cols = [[k for k in shortcuts.keys()]]

        cols_html = []
        for col in cols:
            keys = []
            for k in col:
                line = self.html_shortcut_tpl.format(keyname=self.show_key(shortcuts[k][0]), cmdname=shortcuts[k][1])
                keys.append(line)
            col_html = self.html_col_tpl.format(list="".join(keys))
            cols_html.append(col_html)

        view.erase_phantoms("shortcuts")
        for idx, block in enumerate(cols_html):
            shortcuts_menu_html = self.html_tpl.format(shortcuts=block)
            view.add_phantom("shortcuts", sublime.Region(0, 0), shortcuts_menu_html, sublime.LAYOUT_INLINE)

    def key_col(self, cols: int, keyidx: int) -> int:
        return keyidx - math.floor(keyidx / cols) * cols

    def key_class(self, key: str) -> str:
        if len(key) == 2:
            return "kbd kbd2"
        return "kbd"

    def show_key(self, keyname: str) -> str:
        keys = keyname.split("+")
        return self.html_key_plus.join([self.html_key_tpl.format(kbdclass=self.key_class(k), key=k) for k in keys])
