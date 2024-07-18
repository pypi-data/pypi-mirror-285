from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List


@dataclass
class StandardizedUser:
    id: str
    name: str
    login: str
    email: str = None
    url: str = None
    account_id: str = None


@dataclass
class StandardizedTeam:
    id: str
    slug: str
    name: str
    description: str
    members: list[StandardizedUser]


@dataclass
class StandardizedBranch:
    name: str
    sha: str
    repo_id: str
    is_default: bool


@dataclass
class StandardizedOrganization:
    id: str
    name: str
    login: str
    url: str


@dataclass
class StandardizedShortRepository:
    id: int
    name: str
    url: str


@dataclass
class StandardizedRepository:
    id: str
    name: str
    full_name: str
    url: str
    is_fork: bool
    default_branch_name: str
    default_branch_sha: str
    organization: StandardizedOrganization
    commits_backpopulated_to: datetime = None
    prs_backpopulated_to: datetime = None

    def short(self):
        # return the short form of Standardized Repository
        return StandardizedShortRepository(id=self.id, name=self.name, url=self.url)


@dataclass
class StandardizedCommit:
    hash: str
    url: str
    message: str
    commit_date: datetime
    author_date: datetime
    author: StandardizedUser
    repo: StandardizedShortRepository
    is_merge: bool
    branch_name: str = None


@dataclass
class StandardizedPullRequestComment:
    user: StandardizedUser
    body: str
    created_at: str
    system_generated: bool = None


@dataclass
class StandardizedPullRequestReview:
    user: StandardizedUser
    foreign_id: int
    review_state: str


@dataclass
class StandardizedLabel:
    id: int
    name: str
    default: bool
    description: str


@dataclass
class StandardizedFileData:
    status: str
    changes: int
    additions: int
    deletions: int


@dataclass
class StandardizedPullRequest:
    id: any
    additions: int
    deletions: int
    changed_files: int
    is_closed: bool
    is_merged: bool
    created_at: str
    updated_at: datetime
    merge_date: datetime
    closed_date: datetime
    title: str
    body: str
    url: str
    base_branch: str
    head_branch: str
    author: StandardizedUser
    merged_by: StandardizedUser
    commits: List[StandardizedCommit]
    merge_commit: StandardizedCommit
    comments: List[StandardizedPullRequestComment]
    approvals: List[StandardizedPullRequestReview]
    base_repo: StandardizedShortRepository
    head_repo: StandardizedShortRepository
    labels: List[StandardizedLabel]
    files: Dict[str, StandardizedFileData]


@dataclass
class StandardizedPullRequestMetadata:
    id: any
    updated_at: datetime
    api_index: any
