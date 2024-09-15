## StGitlab: SublimeText Gitlab manager

SublimeText 3 plugin to manage Gitlab projects:
* issues
* merge-requests
* pipelines
* branches
* snippets

### Features
* Fully customizable fields
* Create/Show/Edit issues
* Create/Show/Edit merge-requests
* Create/Show/Edit snippets
* Show/Retry/Cancel pipelines
* Shortcuts panels on every screen for fast access to commands

## Screenshots

**Project issues list**

![p1](https://raw.githubusercontent.com/wiki/tosher/StGitlab/stgl_issues.png)

**Issue**

![p2](https://raw.githubusercontent.com/wiki/tosher/StGitlab/stgl_issue.png)

**Snippet**

![p3](https://raw.githubusercontent.com/wiki/tosher/StGitlab/stgl_snippet.png)

## Install

### Package Control
The easiest way to install this is with [Package Control](http://wbond.net/sublime\_packages/package\_control).

 * If you just went and installed Package Control, you probably need to restart Sublime Text before doing this next bit.
 * Bring up the Command Palette (<kbd>Command+Shift+p</kbd> on OS X, <kbd>Control+Shift+p</kbd> on Linux/Windows).
 * Select "Package Control: Install Package" (it'll take a few seconds)
 * Select `StGitlab` when the list appears.

Package Control will automatically keep **StGitlab** up to date with the latest version.

### Configure

##### Basic
* Open plugin settings *Preferences: Package Settings > StGitlab > Settings*
* Set the *gitlab_url* and *api_token*
* Configure other options as you want
* Set the *projects_filter* for filtering data for your projects only
* Set the *users_group_filter* for filtering user groups.
* Customize columns by options like `issue_list_columns`, etc.

> For editing descriptions, notes for issues, merges, etc. in markdown, plugin MarkdownEditing is recommended.

Example:

```json
{
    "gitlab_url": "URL to your Gitlab",
    "api_token": "Set your Gitlab API token",
    "ssl_verify": true,
    "projects_filter": ["mygroup/MyProject"],
    "users_group_filter": ["mygroup"],
    "list_page_size": 40,
    "show_system_notes": true,
    "syntax_file": "Packages/StGitlab/StGitlab.sublime-syntax",
    "syntax_file_edit": "Packages/MarkdownEditing/Markdown.sublime-syntax",
}
```

## Hints
For auto-completions show, add option to syntax specific settings (markdown):

```
"auto_complete_triggers": [ {"selector": "text.html.markdown", "characters": "#!@"} ]
```

## External dependencies
* [Python Gitlab](http://python-gitlab.readthedocs.io/en/stable/index.html)
    * [Requests-Toolbelt](https://github.com/requests/toolbelt)
* [Dimensions](https://pypi.python.org/pypi/dimensions) with some fixes for Python 3
* [Tabulate](https://github.com/astanin/python-tabulate)
* [Transliterate](https://pypi.python.org/pypi/transliterate)

### Dependencies, supported by Package control
* [Requests](https://github.com/packagecontrol/requests)
    * urllib3
    * idna
    * six
    * charset_normalizer
