#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING
import re
from datetime import datetime, timedelta
import base64
import plistlib
import requests  # type:ignore
import sublime  # type:ignore

from ..libs import dimensions  # type:ignore

from .stg_gitlab import StGitlab

if TYPE_CHECKING:
    from typing import Dict, Any, Optional, Tuple, List
    from ..libs.gitlab.base import RESTObject  # type:ignore
    from ..libs.gitlab.v4.objects import User as GitlabUser  # type: ignore


PROJECT_SETTINGS_PREFIX = "stgitlab"

syntaxes: Dict[str, str] = {}
filter_types: Dict[str, Any] = {
    "Author": "author_id",
    "Assignee": "assignee_id",
    "Labels": "labels",
    "Milestone": "milestone",
    "State": "state",
    "Search": "search",
    "Page number": "page",
    "Reset filters": None,
}

object_commands: Dict[str, Dict[str, Optional[str]]] = {
    "issue": {
        "char": "#",
        "screen_view": "st_gitlab_issue",
        "screen_list": "st_gitlab_issues",
        "screen_board": "st_gitlab_issues_board",
        "view": "st_gitlab_issue",
        "list": "st_gitlab_project_issues_list",
        "fetch": "st_gitlab_issue_fetcher",
    },
    "merge": {
        "char": "!",
        "screen_view": "st_gitlab_merge",
        "screen_list": "st_gitlab_merges",
        "screen_board": None,
        "view": "st_gitlab_merge",
        "list": "st_gitlab_project_merges_list",
        "fetch": "st_gitlab_merge_fetcher",
    },
    "pipeline": {
        "screen_view": "st_gitlab_pipeline",
        "screen_list": "st_gitlab_pipelines",
        "screen_board": None,
        "view": "st_gitlab_pipeline",
        "list": "st_gitlab_project_pipelines_list",
        "fetch": "st_gitlab_pipeline_fetcher",
    },
    "branch": {
        "screen_view": None,
        "screen_list": "st_gitlab_branches",
        "screen_board": None,
        "view": None,
        "list": "st_gitlab_project_branches_list",
        "fetch": None,
    },
    "snippet": {
        "screen_view": "st_gitlab_snippet",
        "screen_list": "st_gitlab_snippets",
        "screen_board": None,
        "view": "st_gitlab_snippet",
        "list": "st_gitlab_project_snippets_list",
        "fetch": "st_gitlab_snippet_fetcher",
    },
    "user": {
        "screen_view": "st_gitlab_user",
        "screen_list": "st_gitlab_users",
        "screen_board": None,
        "view": "st_gitlab_user",
        "list": "st_gitlab_users_list",
        "fetch": "st_gitlab_user_fetcher",
    },
}

gl = StGitlab()


def get_setting(key: str, default_value: Any = None) -> Any:
    settings = sublime.load_settings("StGitlab.sublime-settings")
    view = sublime.active_window().active_view()
    val = None
    if view is not None:
        val = sublime.active_window().active_view().settings().get(f"{PROJECT_SETTINGS_PREFIX}.{key}", None)
    return settings.get(key, default_value) if val is None else val


def set_setting(key: str, value: Any) -> None:
    settings = sublime.load_settings("StGitlab.sublime-settings")
    settings.set(key, value)
    sublime.save_settings("StGitlab.sublime-settings")


def stg_get_datetime(datetime_str: str) -> str:
    if not datetime_str:
        return datetime_str

    dt_format_in = get_setting("datetime_format")
    dt_format_sys_1 = "%Y-%m-%dT%H:%M:%S.%fZ"
    dt_format_sys_2 = "%Y-%m-%dT%H:%M:%S.%f%z"
    dt_format_out = get_setting("datetime_format_show")

    dt_str_cnv = str(datetime_str)
    if "%z" in dt_format_in:
        # datetime_str = '2017-09-18T16:53:33.197+03:00'
        # dt_format_in = '%Y-%m-%dT%H:%M:%S.%f%z'
        # remove unsupported : in ..+03:00
        dt_str_cnv = "".join(datetime_str.rsplit(":", 1))

    # TODO: research time formats in gitlab
    try:
        datetime_obj = datetime.strptime(dt_str_cnv, dt_format_in)
        return datetime_obj.strftime(dt_format_out)
    except ValueError:
        try:
            datetime_obj = datetime.strptime(datetime_str, dt_format_sys_1)
            return datetime_obj.strftime(dt_format_out)
        except ValueError:
            try:
                dt_str_cnv = "".join(datetime_str.rsplit(":", 1))
                datetime_obj = datetime.strptime(dt_str_cnv, dt_format_sys_2)
                return datetime_obj.strftime(dt_format_out)
            except ValueError as e:
                print(f'Error converting datetime string "{dt_str_cnv}": {e} (1)')
                return datetime_str.replace("T", " ").replace("Z", "")
        except Exception as e:
            print(f'Error converting datetime string "{datetime_str}": {e} (2)')
            return datetime_str.replace("T", " ").replace("Z", "")
    except Exception as e:
        print(f'Error converting datetime string "{dt_str_cnv}": {e} (3)')
        return datetime_str.replace("T", " ").replace("Z", "")


def stg_get_seconds(seconds: int) -> str:
    try:
        return str(timedelta(seconds=int(seconds)))
    except Exception as e:
        print(f'Duration convert exception for value "{seconds}": {e}')
        return str(seconds)


def stg_cut(val: str, maxlen: int) -> str:
    if maxlen:
        if len(val) > maxlen:
            return f"{val[: maxlen - 2].strip()}.."
    return val


def stg_get_property_value(obj: RESTObject, prop: Dict[str, Any]) -> Any:
    val = ""
    label_char = get_setting("label_char")
    prop_type = prop.get("type", "string")
    attrs = obj.attributes
    try:
        if prop_type == "list":
            if prop["prop"] == "labels":
                val = " ".join([f"{label_char}{lab}{label_char}" for lab in attrs.get(prop["prop"], "")])
            else:
                val = ", ".join(attrs.get(prop["prop"], ""))
        elif prop_type == "datetime":
            val = stg_get_datetime(attrs.get(prop["prop"], ""))
        elif prop_type == "seconds":
            val = stg_get_seconds(attrs.get(prop["prop"], ""))
        elif prop_type == "bool":
            val = str(attrs.get(prop["prop"], ""))
        elif prop.get("attr", None):
            val_obj = attrs.get(prop["prop"], "")
            if val_obj:
                if isinstance(val_obj, str):
                    val = val_obj
                else:
                    val = val_obj.get(prop["attr"], "")
        else:
            val = attrs.get(prop["prop"], "")
        return stg_cut(val, prop.get("maxlen", None))
    except Exception as e:
        print(f"Exception while get {prop} value: {e}")
        return attrs.get(prop["prop"], "")


def stg_label_str(name: str) -> str:
    lbl_chr = get_setting("label_char")
    return f"{lbl_chr}{name}{lbl_chr}"


def stg_label_str_by_id(label_id: int, project_id: int) -> str:
    gitlab = gl.get()
    labels = gitlab.labels(project_id=project_id, all=True)
    for label in labels:
        if label.id != label_id:
            continue

        return stg_label_str(label.name)
    return f"~{label_id}"


def stg_msg_labels(msg: str, project_id: int) -> str:
    def get_label(matched: re.Match) -> str:
        return stg_label_str_by_id(int(matched.group(2)), project_id)

    label_pattern = r"(^|\s)\~(\d+)"
    m = re.search(label_pattern, msg)
    if not m or not m.group(2):
        return msg

    msg = re.sub(label_pattern, get_label, msg)
    return msg


def stg_get_image(url: str) -> Tuple[str, float, float]:
    max_width = get_setting("image_max_width")
    response = requests.get(url, verify=get_setting("ssl_verify", False))
    dims = dimensions.get_dimensions_from_stream(response.content)
    if not dims:
        raise ValueError("Unable to get image size")
    w, h = stg_image_scale(dims[0], dims[1], max_width)
    img_base64 = (
        "data:" + response.headers["Content-Type"] + ";" + "base64," + str(base64.b64encode(response.content).decode("utf-8"))
    )
    return img_base64, w, h


def stg_show_images(view: sublime.View) -> None:
    view.erase_phantoms("image")
    img_pattern = r"!\[(.*?)(\])\((.*?)\)"
    images = view.find_all(img_pattern)
    for image_r in images:
        img_text = view.substr(image_r)
        img_url = img_text.split("(")[1][:-1]
        if not img_url.startswith("http"):
            gitlab = gl.get()
            project = gitlab.project()
            if project is None:
                return
            img_url = "/".join([project.web_url.rstrip("/"), img_url.lstrip("/")])
        img_data, w, h = stg_get_image(img_url)
        view.add_phantom(
            "image",
            sublime.Region(image_r.b + 1, image_r.b + 2),
            f'<img src="{img_data}" width="{w}" height="{h}"><br><br>',
            sublime.LAYOUT_BLOCK,
        )


def stg_image_scale(width: float, height: float, max_width: float) -> Tuple[float, float]:
    width = float(width)
    height = float(height)
    scaled = False
    if not max_width:
        return width, height

    if width > max_width:
        koeff = width / max_width
        width = max_width
        height = height / koeff
        scaled = True

    if scaled:
        return int(width), int(height)
    return width, height


def stg_generate_syntaxes() -> None:
    def get_lazy_old_scope(text: str) -> None:
        ext_found = False
        for line in f.split("\n"):
            if "<key>fileTypes</key>" in line:
                ext_found = True
                continue
            if ext_found and "</array>" in line:
                break
            if ext_found and line.strip().startswith("<string>"):
                if "<array>" in line:
                    continue
                ext = line.strip().split("<")[1].split(">")[1].strip()
                if ext:
                    ext_syn[ext] = synfile

    global syntaxes
    ext_syn = {}
    syntax_files_new = sublime.find_resources("*.sublime-syntax")
    syntax_files_old = sublime.find_resources("*.tmLanguage")
    synfiles = syntax_files_new + syntax_files_old
    for synfile in synfiles:
        try:
            f = sublime.load_resource(synfile)
            if synfile.endswith("sublime-syntax"):
                ext_found = False
                for line in f.split("\n"):
                    if "file_extensions" in line:
                        ext_found = True
                        continue
                    if ext_found and not line.strip().startswith("-"):
                        break
                    if ext_found and line.strip().startswith("-"):
                        ext = line.strip().split("-")[-1].strip().split(" ")[0]
                        if ext:
                            ext_syn[ext] = synfile
            else:
                try:
                    plist = plistlib.readPlistFromBytes(f.encode("utf-8"))
                    if "fileTypes" in plist:
                        for ext in plist["fileTypes"]:
                            ext_syn[ext] = synfile
                except Exception:
                    get_lazy_old_scope(f.encode("utf-8"))
        except Exception as e:
            print(f"Get syntax exception for {synfile}: {e} ({e.__class__})")
    syntaxes = ext_syn


def users_filtered(users_group_filter: List[str]) -> List[GitlabUser]:
    users = []
    gitlab = gl.get()

    groups_lists = []
    for group_name in users_group_filter:
        group = gitlab.group(group_name)
        if group is None:
            sublime.active_window().status_message(f'Group "{group_name}" not found in Gitlab')
            continue
        groups_lists.append(group.members.list(active=True))

    for gr_users in groups_lists:
        for user in gr_users:
            # users.append(user)
            users.append(gitlab.user(oid=user.id))
    return users


def users_all() -> List[GitlabUser]:
    gitlab = gl.get()
    return gitlab.users(all=True, active=True)


sublime.set_timeout_async(stg_generate_syntaxes, 0)
