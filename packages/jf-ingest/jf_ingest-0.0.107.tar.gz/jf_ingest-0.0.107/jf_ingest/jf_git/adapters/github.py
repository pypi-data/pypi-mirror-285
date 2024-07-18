import logging
import traceback
from datetime import datetime
from typing import Generator, List, Optional

from dateutil import parser
from requests.exceptions import HTTPError

from jf_ingest import diagnostics, logging_helper
from jf_ingest.config import GitConfig
from jf_ingest.graphql_utils import gql_format_to_datetime
from jf_ingest.jf_git.adapters import GitAdapter
from jf_ingest.jf_git.clients.github import GithubClient
from jf_ingest.jf_git.standardized_models import (
    StandardizedBranch,
    StandardizedCommit,
    StandardizedFileData,
    StandardizedLabel,
    StandardizedOrganization,
    StandardizedPullRequest,
    StandardizedPullRequestComment,
    StandardizedPullRequestMetadata,
    StandardizedPullRequestReview,
    StandardizedRepository,
    StandardizedShortRepository,
    StandardizedTeam,
    StandardizedUser,
)
from jf_ingest.name_redactor import NameRedactor, sanitize_text

logger = logging.getLogger(__name__)

'''

    Data Fetching

'''

_branch_redactor = NameRedactor(preserve_names=['master', 'develop'])
_organization_redactor = NameRedactor()
_repo_redactor = NameRedactor()


class GithubAdapter(GitAdapter):
    def __init__(self, config: GitConfig):
        # Git Config options
        self.client = GithubClient(config.git_auth_config)
        self.config = config
        self.repo_id_to_name_lookup: dict = {}

    def get_api_scopes(self):
        return self.client.get_scopes_of_api_token()

    @diagnostics.capture_timing()
    @logging_helper.log_entry_exit(logger)
    def get_organizations(self) -> List[StandardizedOrganization]:
        # NOTE: For github, organization equates to a Github organization here!
        # We have the name of the organization in the config, expected to be a list of length one
        try:
            org = self.client.get_organization_by_login(self.config.git_organizations[0])
        except HTTPError as e:
            if e.response.status_code == 404:
                # give something a little nicer for 404s
                raise ValueError(
                    'Organization not found. Make sure your token has appropriate access to Github.'
                )
            raise
        return [_standardize_organization(org, self.config.git_redact_names_and_urls)]

    def get_users(
        self, standardized_organization: StandardizedOrganization, limit: int = None
    ) -> Generator[StandardizedUser, None, None]:
        for i, user in enumerate(self.client.get_users(standardized_organization.login), start=1):
            yield _standardize_user(user)
            if limit and i >= limit:
                return

    def get_teams(
        self, standardized_organization: StandardizedOrganization, limit: int = None
    ) -> Generator[StandardizedTeam, None, None]:
        for i, team in enumerate(
            self.client.get_teams(login=standardized_organization.login), start=1
        ):
            yield _standardize_team(team)
            if limit and i >= limit:
                return

    def get_repos(
        self, standardized_organization: StandardizedOrganization
    ) -> Generator[StandardizedRepository, None, None]:
        filters = []
        if self.config.excluded_repos:
            filters.append(
                lambda r: r['name'].lower() in set([r.lower() for r in self.config.included_repos])
            )
        if self.config.excluded_repos:
            filters.append(
                lambda r: r['name'].lower()
                not in set([r.lower() for r in self.config.excluded_repos])
            )

        for api_repo in self.client.get_repos(
            standardized_organization.login, repo_filters=filters
        ):
            # Enter the repo to the ID to Name look up, incase the repo name gets
            # scrubbed by our git_redact_names_and_urls logic
            repo_id = str(api_repo['id'])
            self.repo_id_to_name_lookup[repo_id] = api_repo['name']

            yield _standardize_repo(
                api_repo, standardized_organization, self.config.git_redact_names_and_urls
            )

    def get_branches_for_repo(
        self,
        standardized_repo: StandardizedRepository,
        redact_names_and_urls: bool,
        pull_branches: Optional[bool] = False,
    ) -> Generator[StandardizedBranch, None, None]:
        if pull_branches:
            repo_name = self.repo_id_to_name_lookup[standardized_repo.id]
            for branch in self.client.get_branches(
                login=standardized_repo.organization.login, repo_name=repo_name
            ):
                yield _standardize_branch(
                    branch,
                    repo_id=standardized_repo.id,
                    redact_names_and_urls=redact_names_and_urls,
                    is_default_branch=standardized_repo.default_branch_sha
                    == branch['target']['sha'],
                )
        else:
            # Above, if we're pulling all branches, it's safe to assume that the default branch
            # will be included in that
            # When we don't pull all branches, always return default branch
            if standardized_repo.default_branch_name:
                yield StandardizedBranch(
                    repo_id=standardized_repo.id,
                    name=standardized_repo.default_branch_name,
                    sha=standardized_repo.default_branch_sha,
                    is_default=True,
                )

    def get_commits_for_branches(
        self,
        standardized_repo: StandardizedRepository,
        branches: List[StandardizedBranch],
        pull_since: datetime = None,
        pull_until: datetime = None,
    ) -> Generator[StandardizedCommit, None, None]:
        for branch_name in self.get_filtered_branches(standardized_repo, branches):
            try:
                login = standardized_repo.organization.login
                repo_name = self.repo_id_to_name_lookup[standardized_repo.id]
                for api_commit in self.client.get_commits(
                    login=login,
                    repo_name=repo_name,
                    branch_name=branch_name,
                    since=pull_since,
                    until=pull_until,
                ):
                    yield _standardize_commit(
                        api_commit,
                        standardized_repo,
                        branch_name,
                        self.config.git_strip_text_content,
                        self.config.git_redact_names_and_urls,
                    )

            except Exception as e:
                logging_helper.send_to_agent_log_file(traceback.format_exc(), level=logging.ERROR)
                logger.warning(f':WARN: Got exception for branch {branch_name}: {e}. Skipping...')

    def get_commits_for_default_branch(
        self,
        standardized_repo: StandardizedRepository,
        limit: int = None,
        pull_since: datetime = None,
        pull_until: datetime = None,
    ) -> Generator[StandardizedCommit, None, None]:
        try:
            login = standardized_repo.organization.login
            repo_name = self.repo_id_to_name_lookup[standardized_repo.id]
            branch_name = standardized_repo.default_branch_name
            for j, api_commit in enumerate(
                self.client.get_commits(
                    login=login,
                    repo_name=repo_name,
                    branch_name=branch_name,
                    since=pull_since,
                    until=pull_until,
                ),
                start=1,
            ):
                yield _standardize_commit(
                    api_commit,
                    standardized_repo,
                    standardized_repo.default_branch_name,
                    self.config.git_strip_text_content,
                    self.config.git_redact_names_and_urls,
                )
                if limit and j >= limit:
                    return

        except Exception as e:
            logging_helper.send_to_agent_log_file(traceback.format_exc(), level=logging.ERROR)
            logger.warning(
                f':WARN: Got exception for branch {standardized_repo.default_branch_name}: {e}. Skipping...'
            )

    def get_pr_metadata(
        self, standardized_repo: StandardizedRepository, limit: int = None
    ) -> Generator[StandardizedPullRequestMetadata, None, None]:
        try:
            login = standardized_repo.organization.login
            repo_id = standardized_repo.id
            repo_name = self.repo_id_to_name_lookup[repo_id]
            for api_pr_metadata in self.client.get_prs_metadata(login=login, repo_name=repo_name):
                yield StandardizedPullRequestMetadata(
                    id=api_pr_metadata['pr']['number'],
                    updated_at=gql_format_to_datetime(api_pr_metadata['pr']['updatedAt']),
                    api_index=api_pr_metadata['cursor'],
                )

        except Exception:
            # if something happens when pulling PRs for a repo, just keep going.
            logger.warning(
                f'Problem fetching PR metadata from repo {standardized_repo.name} ({standardized_repo.id}). Skipping...'
            )
            logging_helper.send_to_agent_log_file(traceback.format_exc(), level=logging.ERROR)

    def get_prs(
        self,
        standardized_repo: StandardizedRepository,
        pull_files_for_pr: bool = False,
        hash_files_for_prs: bool = False,
        limit: int = None,
        start_cursor: any = None,
    ) -> Generator[StandardizedPullRequest, None, None]:
        try:
            login = standardized_repo.organization.login
            repo_id = standardized_repo.id
            repo_name = self.repo_id_to_name_lookup[repo_id]

            try:
                labels_for_repository = self.client.get_labels_for_repository(
                    org_login=standardized_repo.organization.login, repo_name=repo_name
                )
                label_node_id_to_id = {
                    label['node_id']: label['id'] for label in labels_for_repository
                }
            except Exception as e:
                logging_helper.send_to_agent_log_file(
                    msg=f'Error when attempting to pull Labels for Repo {repo_name}. Error: {e}',
                    level=logging.ERROR,
                )
                logging_helper.send_to_agent_log_file(
                    msg=traceback.format_exc(), level=logging.ERROR
                )
                label_node_id_to_id = {}

            api_prs = self.client.get_prs(
                login=login,
                repo_name=repo_name,
                include_top_level_comments=self.config.jf_options.get(
                    'get_all_issue_comments', False
                ),
                start_cursor=start_cursor,
                pull_files_for_pr=pull_files_for_pr,
                hash_files_for_prs=hash_files_for_prs,
                repository_label_node_ids_to_id=label_node_id_to_id,
            )
            for j, api_pr in enumerate(
                api_prs,
                start=1,
            ):
                try:
                    yield _standardize_pr(
                        api_pr,
                        standardized_repo,
                        self.config.git_strip_text_content,
                        self.config.git_redact_names_and_urls,
                    )
                    if limit and j >= limit:
                        return
                except Exception:
                    # if something goes wrong with normalizing one of the prs - don't stop pulling. try
                    # the next one.
                    pr_id = f' {api_pr["id"]}' if api_pr else ''
                    logger.warning(
                        f'normalizing PR {pr_id} from repo {standardized_repo.name} ({standardized_repo.id}). Skipping...'
                    )
                    logging_helper.send_to_agent_log_file(
                        traceback.format_exc(), level=logging.ERROR
                    )

        except Exception:
            # if something happens when pulling PRs for a repo, just keep going.
            logger.warning(
                f'normalizing PRs from repo {standardized_repo.name} ({standardized_repo.id}). Skipping...'
            )
            logging_helper.send_to_agent_log_file(traceback.format_exc(), level=logging.ERROR)


'''

    Massage Functions

'''


def _standardize_user(api_user) -> StandardizedUser:
    if not api_user:
        return None

    id = api_user.get('id')
    name = api_user.get('name')
    login = api_user.get('login')
    email = api_user.get('email')
    # raw user, just have email (e.g. from a commit)
    if not id:
        return StandardizedUser(
            id=email,
            login=email,
            name=name,
            email=email,
        )

    # API user, where github matched to a known account
    return StandardizedUser(id=id, login=login, name=name, email=email)


def _standardize_team(api_team: dict) -> StandardizedTeam:
    return StandardizedTeam(
        id=str(api_team.get('id')),
        name=api_team.get('name'),
        slug=api_team.get('slug'),
        description=api_team.get('description'),
        members=[_standardize_user(member) for member in api_team.get('members', [])],
    )


def _standardize_organization(
    api_org: dict, redact_names_and_urls: bool
) -> StandardizedOrganization:
    return StandardizedOrganization(
        id=api_org['id'],
        login=api_org['login'],
        name=api_org.get('name')
        if not redact_names_and_urls
        else _organization_redactor.redact_name(api_org.get('name')),
        url=api_org['url'] if not redact_names_and_urls else None,
    )


def _standardize_branch(
    api_branch, repo_id: str, is_default_branch: bool, redact_names_and_urls: bool
) -> StandardizedBranch:
    if not api_branch:
        return None
    if not api_branch['name']:
        return None
    return StandardizedBranch(
        repo_id=repo_id,
        name=api_branch['name']
        if not redact_names_and_urls
        else _branch_redactor.redact_name(api_branch['name']),
        sha=api_branch['target']['sha'],
        is_default=is_default_branch,
    )


def _standardize_repo(
    api_repo,
    standardized_organization: StandardizedOrganization,
    redact_names_and_urls: bool,
) -> StandardizedRepository:
    repo_name = (
        api_repo['name']
        if not redact_names_and_urls
        else _repo_redactor.redact_name(api_repo['name'])
    )
    url = api_repo['url'] if not redact_names_and_urls else None

    # NOTE: If a repo is completely empty, than there will be no default branch.
    # in that case, the standardized_default_branch object will be None
    standardized_default_branch = _standardize_branch(
        api_repo['defaultBranch'],
        repo_id=api_repo['id'],
        redact_names_and_urls=redact_names_and_urls,
        is_default_branch=True,
    )
    default_branch_name = standardized_default_branch.name if standardized_default_branch else None
    default_branch_sha = standardized_default_branch.sha if standardized_default_branch else None

    return StandardizedRepository(
        id=str(api_repo['id']),
        name=repo_name,
        full_name=f'{standardized_organization.login}/{repo_name}',
        url=url,
        default_branch_name=default_branch_name,
        default_branch_sha=default_branch_sha,
        is_fork=api_repo['isFork'],
        organization=standardized_organization,
    )


def _standardize_short_form_repo(
    api_repo: dict, redact_names_and_urls: dict
) -> StandardizedShortRepository:
    repo_name = (
        api_repo['name']
        if not redact_names_and_urls
        else _repo_redactor.redact_name(api_repo['name'])
    )
    url = api_repo['url'] if not redact_names_and_urls else None

    return StandardizedShortRepository(id=str(api_repo['id']), name=repo_name, url=url)


def _standardize_commit(
    api_commit: dict,
    standardized_repo: StandardizedRepository,
    branch_name: str,
    strip_text_content: bool,
    redact_names_and_urls: bool,
):
    author = _standardize_user(api_commit['author'])
    commit_url = api_commit['url'] if not redact_names_and_urls else None
    return StandardizedCommit(
        hash=api_commit['sha'],
        author=author,
        url=commit_url,
        commit_date=gql_format_to_datetime(api_commit['committedDate']),
        author_date=gql_format_to_datetime(api_commit['authoredDate']),
        message=sanitize_text(api_commit['message'], strip_text_content),
        is_merge=api_commit['parents']['totalCount'] > 1,
        repo=standardized_repo.short(),  # use short form of repo
        branch_name=branch_name
        if not redact_names_and_urls
        else _branch_redactor.redact_name(branch_name),
    )


def _get_standardized_pr_comments(
    api_comments: list[dict], strip_text_content
) -> List[StandardizedPullRequestComment]:
    return [
        StandardizedPullRequestComment(
            user=_standardize_user(api_comment['author']),
            body=sanitize_text(api_comment['body'], strip_text_content),
            created_at=api_comment['createdAt'],
        )
        for api_comment in api_comments
    ]


def _get_standardized_reviews(api_reviews: list[dict]):
    return [
        StandardizedPullRequestReview(
            user=_standardize_user(api_review['author']),
            foreign_id=api_review['id'],
            review_state=api_review['state'],
        )
        for api_review in api_reviews
    ]


def _standardize_pr(
    api_pr: dict,
    standardized_repo: StandardizedRepository,
    strip_text_content: bool,
    redact_names_and_urls: bool,
):
    base_branch_name = api_pr['baseRefName']
    head_branch_name = api_pr['headRefName']
    standardized_merge_commit = (
        _standardize_commit(
            api_pr['mergeCommit'],
            standardized_repo=standardized_repo,
            branch_name=base_branch_name,
            strip_text_content=strip_text_content,
            redact_names_and_urls=redact_names_and_urls,
        )
        if api_pr['mergeCommit']
        else None
    )
    return StandardizedPullRequest(
        id=api_pr['id'],
        additions=api_pr['additions'],
        deletions=api_pr['deletions'],
        changed_files=api_pr['changedFiles'],
        created_at=gql_format_to_datetime(api_pr['createdAt']),
        updated_at=gql_format_to_datetime(api_pr['updatedAt']),
        merge_date=gql_format_to_datetime(api_pr['mergedAt']),
        closed_date=gql_format_to_datetime(api_pr['closedAt']),
        is_closed=api_pr['state'].lower() == 'closed',
        is_merged=api_pr['merged'],
        # redacted fields
        url=api_pr['url'] if not redact_names_and_urls else None,
        base_branch=(
            base_branch_name
            if not redact_names_and_urls
            else _branch_redactor.redact_name(base_branch_name)
        ),
        head_branch=(
            head_branch_name
            if not redact_names_and_urls
            else _branch_redactor.redact_name(head_branch_name)
        ),
        # sanitized fields
        title=sanitize_text(api_pr['title'], strip_text_content),
        body=sanitize_text(api_pr['body'], strip_text_content),
        # standardized fields
        commits=[
            _standardize_commit(
                api_commit=commit,
                standardized_repo=standardized_repo,
                branch_name=base_branch_name,
                strip_text_content=strip_text_content,
                redact_names_and_urls=redact_names_and_urls,
            )
            for commit in api_pr['commits']
        ],
        merge_commit=standardized_merge_commit,
        author=_standardize_user(api_user=api_pr['author']),
        merged_by=_standardize_user(api_user=api_pr['mergedBy']),
        approvals=_get_standardized_reviews(api_pr['reviews']),
        comments=_get_standardized_pr_comments(api_pr['comments'], strip_text_content),
        base_repo=_standardize_short_form_repo(api_pr['baseRepository'], redact_names_and_urls),
        head_repo=_standardize_short_form_repo(api_pr['baseRepository'], redact_names_and_urls),
        labels=[
            StandardizedLabel(
                id=label['id'],
                name=label['name'],
                default=label['default'],
                description=label['description'],
            )
            for label in api_pr.get('labels', [])
        ],
        files={
            file_name: StandardizedFileData(
                status=file_data['status'],
                changes=file_data['changes'],
                additions=file_data['additions'],
                deletions=file_data['deletions'],
            )
            for file_name, file_data in api_pr.get('files', {}).items()
        },
    )
