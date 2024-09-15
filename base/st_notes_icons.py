from __future__ import annotations
from typing import TYPE_CHECKING

import sublime  # type:ignore

if TYPE_CHECKING:
    from typing import Optional


class StNotesIcons(object):
    ICON_WIDTH = 16
    ICON_HEIGHT = 16

    # https://gitlab.com/gitlab-org/gitlab-ce/issues/33503
    icon_markers = {
        "label": "lable.png",
        "marked": "pencil.png",
        "milestone": "clock.png",
        "task completed": "task-done.png",
        "task incomplete": "task-undone.png",
        "mention merge": "systemnote-mentioned-mr.png",
        "enabled merge": "icon-merge-request.png",
        "approved": "approval.png",
        "merged": "icon-merge-request.png",
        "mention issue": "icon-mention.png",
        "assigned to": "assignee.png",
        "removed assigne": "unassignee.png",
        "changed": "pencil.png",
        "create branch": "branch.png",
        "move project": "arrow-right.png",
        "commit": "systemnote-commit.png",
        "close": "systemnote-status-closed.png",
        "reopen": "systemnote-status-open.png",
        "comment": "comment.png",
        "duplicate": "duplicate.png",
        "confidential": "eye-slash.png",
        "visible": "eye.png",
    }

    def __init__(self, view: sublime.View) -> None:
        self.view = view
        self.build()

    def build(self) -> None:
        self.view.erase_phantoms("note_icon")
        pattern = r"^> \d+:(.*?)$"
        notes = self.view.find_all(pattern)
        for note in notes:
            text = " ".join(self.view.substr(note).split()[2:])
            self.show(note.a, text)

    def get_icon(self, text: str) -> Optional[str]:
        for marker in self.icon_markers.keys():
            marker_tokens = marker.split()
            if all([m in text.lower() for m in marker_tokens]):
                return self.icon_markers[marker]
        return None

    def show(self, point: int, text: str) -> None:
        icon = self.get_icon(text)
        if not icon:
            return

        self.view.add_phantom(
            "note_icon",
            sublime.Region(point, point),
            f"""
            <div style="padding:3px;">
                <img src="res://Packages/StGitlab/icons/{icon}" width="{self.ICON_WIDTH}" height="{self.ICON_HEIGHT}" style="border:0;">
            </div>""",
            sublime.LAYOUT_INLINE,
        )
