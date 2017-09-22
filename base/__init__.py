#!/usr/bin/env python\n
# -*- coding: utf-8 -*-

from .stg_issue import StGitlabIssueCommand
from .stg_issue import StGitlabIssueCreateCommand
from .stg_issue import StGitlabIssueDeleteCommand
from .stg_object_add_label import StGitlabAddLabelCommand
from .stg_object_add_label import StGitlabIssueAddLabelCommand
from .stg_object_add_label import StGitlabMergeAddLabelCommand
from .stg_object_remove_label import StGitlabRemoveLabelCommand
from .stg_object_remove_label import StGitlabIssueRemoveLabelCommand
from .stg_object_remove_label import StGitlabMergeRemoveLabelCommand
from .stg_object_change_assigned import StGitlabObjectChangeAssignedCommand
from .stg_object_change_description import StGitlabObjectChangeDescriptionCommand
from .stg_issue_change_project import StGitlabChangeProjectCommand
from .stg_object_change_title import StGitlabObjectChangeTitleCommand
from .stg_fetcher import StGitlabFetcherCommand
from .stg_fetcher import StGitlabIssueFetcherCommand
from .stg_fetcher import StGitlabMergeFetcherCommand
from .stg_fetcher import StGitlabPipelineFetcherCommand
from .stg_object_in_browser import StGitlabObjectInBrowserCommand
from .stg_object_change_any import StGitlabObjectChangeAnyCommand
from .stg_object_add_note import StGitlabObjectAddNoteCommand
from .stg_object_change_note import StGitlabObjectChangeNoteCommand
from .stg_object_refresh import StGitlabObjectRefreshCommand
from .stg_object_set_milestone import StGitlabObjectSetMilestoneCommand
from .stg_object_change_state import StGitlabObjectChangeStateCommand
from .stg_issue_toggle_selectable import StGitlabToggleSelectableCommand
from .stg_project_issues import StGitlabProjectIssuesCommand
from .stg_project_merges import StGitlabProjectMergesCommand
from .stg_project_pipelines import StGitlabProjectPipelinesCommand
from .stg_project_list_filter import StGitlabProjectListFilterCommand
from .stg_project_list_refresh import StGitlabProjectListRefreshCommand
from .stg_project_list_page import StGitlabProjectListPageCommand
from .stg_project_objects_list import StGitlabProjectObjectsListCommand
from .stg_project_objects_list import StGitlabProjectIssuesListCommand
from .stg_project_objects_list import StGitlabProjectMergesListCommand
from .stg_project_objects_list import StGitlabProjectPipelinesListCommand
from .stg_merge import StGitlabMergeCommand
from .stg_pipeline import StGitlabPipelineCommand
from .stg_pipeline import StGitlabPipelineCancelCommand
from .stg_pipeline import StGitlabPipelineRetryCommand
from .stg_view_show_labels import StGitlabViewShowLabelsCommand

__all__ = [
    'StGitlabIssueCommand',
    'StGitlabIssueFetcherCommand',
    'StGitlabIssueCreateCommand',
    'StGitlabIssueDeleteCommand',
    'StGitlabIssueAddLabelCommand',
    'StGitlabIssueRemoveLabelCommand',
    'StGitlabChangeProjectCommand',

    'StGitlabMergeCommand',
    'StGitlabMergeFetcherCommand',
    'StGitlabMergeAddLabelCommand',
    'StGitlabMergeRemoveLabelCommand',

    'StGitlabPipelineCommand',
    'StGitlabPipelineCancelCommand',
    'StGitlabPipelineRetryCommand',
    'StGitlabPipelineFetcherCommand',

    'StGitlabAddLabelCommand',
    'StGitlabRemoveLabelCommand',
    'StGitlabFetcherCommand',
    'StGitlabObjectChangeAnyCommand',
    'StGitlabObjectAddNoteCommand',
    'StGitlabObjectChangeNoteCommand',
    'StGitlabObjectRefreshCommand',
    'StGitlabObjectSetMilestoneCommand',
    'StGitlabObjectChangeTitleCommand',
    'StGitlabObjectChangeDescriptionCommand',
    'StGitlabObjectChangeAssignedCommand',
    'StGitlabObjectChangeStateCommand',
    'StGitlabObjectInBrowserCommand',
    'StGitlabToggleSelectableCommand',

    'StGitlabProjectObjectsListCommand',
    'StGitlabProjectIssuesListCommand',
    'StGitlabProjectMergesListCommand',
    'StGitlabProjectPipelinesListCommand',
    'StGitlabProjectIssuesCommand',
    'StGitlabProjectMergesCommand',
    'StGitlabProjectPipelinesCommand',
    'StGitlabProjectListFilterCommand',
    'StGitlabProjectListRefreshCommand',
    'StGitlabProjectListPageCommand',
    'StGitlabViewShowLabelsCommand'
]
