from dataclasses import dataclass, field
from datetime import date, datetime
from typing import TypeVar

from jf_ingest.data_manifests.manifest_base import ManifestBase

IJiraDataManifest = TypeVar('IJiraDataManifest', bound='JiraDataManifest')
IJiraProjectManifest = TypeVar('IJiraProjectManifest', bound='JiraProjectManifest')


# Separating the model from the adapter behavior as a base class to make the data more transportable and reusable
@dataclass
class JiraDataManifestBase(ManifestBase):
    # Pull from date
    pull_from: date = field(default=None)

    # Counts
    users_count: int = field(default=None)
    fields_count: int = field(default=None)
    resolutions_count: int = field(default=None)
    issue_types_count: int = field(default=None)
    issue_link_types_count: int = field(default=None)
    priorities_count: int = field(default=None)
    projects_count: int = field(default=None)
    project_versions_count: int = field(default=None)
    boards_count: int = field(default=None)
    # Adheres to Pull From Date and (in remote manifests)
    # a project that we have excluded is zero'd out,
    # i.e. even if we can see issues in that project we
    # consider it to have 0 issues since we won't ingest any
    issues_count: int = field(default=None)

    # Drill down into each project with ProjectManifests
    project_manifests: list[IJiraProjectManifest] = field(default_factory=list)

    # For debug purposes. We may want to optionally exclude this when serializing
    encountered_errors_for_projects: dict = field(default_factory=dict)


# Separating the model from the adapter behavior as a base class to make the data more transportable and reusable
@dataclass
class JiraProjectManifestBase(ManifestBase):
    project_id: str = field(default=None)
    project_key: str = field(default=None)
    issues_count: int = field(default=None)
    version_count: int = field(default=None)
    # This reflects if a client has intentionally excluded
    # a project from being ingested
    excluded: bool = field(default=False)
    # Pull from date
    pull_from: date = field(default=None)
    # Latest issue updated date
    last_issue_updated_date: datetime = field(default=None)
    # Allocation Status
    classification: int = field(default=None)
    # Human readable allocation status.
    # Values pulled from JiraProjectClassification.CLASSIFICATION_CHOICES
    classification_str: str = field(default=None)
