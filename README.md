## WIP:StGitlab: SublimeText 3 Gitlab manager

SublimeText 3 plugin to manage Gitlab issues, merge-requests, pipelines. 

* Fully customizable issue fields
* Show/edit issues
* Show/edit merge-requests
* Show pipelines

## Screenshots

<!--
Project issues list:
![Redlime - project issues](https://github.com/tosher/Redlime/wiki/redlime_issues.png)

Issue:
![Redlime - project issue](https://github.com/tosher/Redlime/wiki/redlime_issue.png)
-->

## Install

### Package Control
The easiest way to install this is with [Package Control](http://wbond.net/sublime\_packages/package\_control).

 * If you just went and installed Package Control, you probably need to restart Sublime Text before doing this next bit.
 * Bring up the Command Palette (<kbd>Command+Shift+p</kbd> on OS X, <kbd>Control+Shift+p</kbd> on Linux/Windows).
 * Select "Package Control: Install Package" (it'll take a few seconds)
 * Select Redlime when the list appears.

Package Control will automatically keep **StGitlab** up to date with the latest version.

### Configure

##### Basic
 * Open plugin settings *Preferences: Package Settings > StGitlab > Settings – User*.
 * Set the *gitlab_url* and *api_token*.
 * Configure the *issue_list_columns* and *issue_view_columns* for showing issues as you want.
 * Set the *projects_filter* for filtering data for your projects only.

Example:

```json
{
    "redmine_url" : "URL to your Gitlab",
    "api_token": "Set your Gitlab API token",
    "projects_filter": [],
    "list_page_size": 40,
    "syntax_file": "Packages/StGitlab/StGitlab.sublime-syntax",
     "issue_list_columns": [
        { "prop": "iid", "colname": "#", "align": "right" },
        { "prop": "title", "colname": "Title", "maxlen": 50},
        { "prop": "author", "colname": "Author", "attr": "name"},
        { "prop": "assignee", "colname": "Assigned", "attr": "name"},
        { "prop": "milestone", "colname": "Milestone", "attr": "title"},
        { "prop": "state", "colname": "State"},
        { "prop": "labels", "colname": "Labels", "type": "list"}
    ],
    "merge_requests_list_columns": [
        { "prop": "iid", "colname": "#", "align": "right" },
        { "prop": "title", "colname": "Title", "maxlen": 50},
        { "prop": "author", "colname": "Author", "attr": "name"},
        { "prop": "assignee", "colname": "Assigned", "attr": "name"},
        { "prop": "milestone", "colname": "Milestone", "attr": "title"},
        { "prop": "state", "colname": "State"},
        { "prop": "labels", "colname": "Labels", "type": "list"},
        { "prop": "work_in_progress", "colname": "WIP"}
    ],
    "pipelines_list_columns": [
        { "prop": "id", "colname": "#", "align": "right" },
        { "prop": "ref", "colname": "Branch"},
        { "prop": "status", "colname": "Status"}
    ],
    "issue_view_columns": [
        { "prop": "iid", "colname": "ID"},
        { "prop": "title", "colname": "Title"},
        { "prop": "state", "colname": "State"},
        { "prop": "author", "colname": "Author", "attr": "name"},
        { "prop": "assignee", "colname": "Assigned to", "attr": "name"},
        { "prop": "created_at", "colname": "Creation date", "type": "datetime"},
        { "prop": "milestone", "colname": "Milestone", "attr": "title"},
        { "prop": "labels", "colname": "Labels", "type": "list"}
    ],
    "merge_view_columns": [
        { "prop": "iid", "colname": "ID"},
        { "prop": "title", "colname": "Title"},
        { "prop": "source_branch", "colname": "Source branch"},
        { "prop": "work_in_progress", "colname": "WIP"},
        { "prop": "state", "colname": "State"},
        { "prop": "author", "colname": "Author", "attr": "name"},
        { "prop": "assignee", "colname": "Assigned to", "attr": "name"},
        { "prop": "created_at", "colname": "Creation date", "type": "datetime"},
        { "prop": "milestone", "colname": "Milestone", "attr": "title"},
        { "prop": "labels", "colname": "Labels", "type": "list"},
        { "prop": "merge_status", "colname": "Merge status"}
    ],
    "pipeline_view_columns": [
        { "prop": "id", "colname": "ID"},
        { "prop": "ref", "colname": "Branch"},
        { "prop": "status", "colname": "Status"},
        { "prop": "user", "colname": "User", "attr": "name"},
        { "prop": "created_at", "colname": "Created", "type": "datetime" },
        { "prop": "started_at", "colname": "Started", "type": "datetime" },
        { "prop": "updated_at", "colname": "Updated", "type": "datetime" },
        { "prop": "finished_at", "colname": "Finished", "type": "datetime" },
        { "prop": "duration", "colname": "Duration" }
    ]
}
```

### Plugin commands:

#### Project objects (issues/merge-requests/pipelines) list commands
* <kbd>r</kbd> Gitlab: Refresh
* <kbd>f</kbd> Gitlab: Filter - various filters
* <kbd>Shift+&#8592;</kbd> Gitlab: Previous page
* <kbd>Shift+&#8594;</kbd> Gitlab: Next page
* <kbd>Enter</kbd> Gitlab: View

#### Issue/merge-request/pipeline view/edit commands
* <kbd>F2</kbd> Gitlab: Change title
* <kbd>c</kbd> Gitlab: Add note
* <kbd>s</kbd> Gitlab: Change state
* <kbd>v</kbd> Gitlab: Set milestone
* <kbd>a</kbd> Gitlab: Assign to
* <kbd>m</kbd> Gitlab: Change project
* <kbd>r</kbd> Gitlab: Refresh
* <kbd>g</kbd> Gitlab: Open in browser
* <kbd>d</kbd> Gitlab: Change description
* <kbd>u</kbd> Gitlab: Toggle select mode - toggle full-line selection mode for possibility to copy any selected text.
* <kbd>j</kbd> Gitlab: Label add
* <kbd>k</kbd> Gitlab: Label remove
* <kbd>Enter</kbd> Gitlab: Change property
