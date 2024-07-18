import fnmatch
import logging
from abc import ABC, abstractmethod
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from enum import Enum
from itertools import chain
from typing import Any, Callable, Dict, Generator, List, NamedTuple, Optional

from jf_ingest import diagnostics, logging_helper
from jf_ingest.config import GitConfig, GitProviderInJellyfishRepo, IngestionConfig
from jf_ingest.constants import Constants
from jf_ingest.file_operations import IngestIOHelper, SubDirectory
from jf_ingest.jf_git.exceptions import GitProviderUnavailable
from jf_ingest.jf_git.standardized_models import (
    StandardizedBranch,
    StandardizedCommit,
    StandardizedOrganization,
    StandardizedPullRequest,
    StandardizedPullRequestMetadata,
    StandardizedRepository,
    StandardizedTeam,
    StandardizedUser,
)
from jf_ingest.utils import batch_iterable, batch_iterable_by_bytes_size, tqdm_to_logger

logger = logging.getLogger(__name__)

'''

    Constants

'''
# NOTE: ONLY GITHUB IS CURRENTLY SUPPORTED!!!!
BBS_PROVIDER = 'bitbucket_server'
BBC_PROVIDER = 'bitbucket_cloud'
GH_PROVIDER = 'github'
GL_PROVIDER = 'gitlab'
PROVIDERS = [GL_PROVIDER, GH_PROVIDER, BBS_PROVIDER, BBC_PROVIDER]


class BackpopulationWindow(NamedTuple):
    backpopulation_window_start: datetime
    backpopulation_window_end: datetime


def _transform_dataclass_list_to_dict(dataclass_objects: List[Any]) -> List[Dict]:
    """Helper function for taking a list of objects that inherit from Dataclass and
    transforming them to a list of dictionary objects

    Args:
        dataclass_objects (List[DataclassInstance]): A list of Dataclass Instances

    Returns:
        List[Dict]: A list of dictionaries
    """
    return [asdict(dc_object) for dc_object in dataclass_objects]


class GitObject(Enum):
    GitOrganizations = "git_data_organizations"
    GitUsers = "git_data_users"
    GitTeams = "git_data_teams"
    GitRepositories = "git_data_repos"
    GitBranches = "git_data_branches"
    GitCommits = "git_data_commits"
    GitPullRequests = "git_data_prs"


class GitAdapter(ABC):
    config: GitConfig
    PULL_REQUEST_BATCH_SIZE_IN_BYTES = (
        50 * Constants.MB_SIZE_IN_BYTES
    )  # PRs can be huge and of variable size. We need to limit them by batch size in bytes
    NUMBER_OF_COMMITS_PER_BATCH = (
        30000  # Commits are generally uniform in size. This is ~50 MBs per commit batch
    )

    @staticmethod
    def get_git_adapter(config: GitConfig):
        """Static function for generating a GitAdapter from a provided GitConfig object

        Args:
            config (GitConfig): A git configuration data object. The specific GitAdapter
                is returned based on the git_provider field in this object

        Raises:
            GitProviderUnavailable: If the supplied git config has an unknown git provider, this error will be thrown

        Returns:
            GitAdapter: A specific subclass of the GitAdapter, based on what git_provider we need
        """
        from jf_ingest.jf_git.adapters.github import GithubAdapter

        if config.git_provider == GitProviderInJellyfishRepo.GITHUB:
            adapter = GithubAdapter(config)
        else:
            raise GitProviderUnavailable(
                f'Git provider {config.git_provider} is not currently supported'
            )

        adapter.config = config
        return adapter

    @abstractmethod
    def get_api_scopes(self) -> str:
        """Return the list of API Scopes. This is useful for Validation

        Returns:
            str: A string of API scopes we have, given the adapters credentials
        """
        pass

    @abstractmethod
    def get_organizations(self) -> List[StandardizedOrganization]:
        """Get the list of organizations the adapter has access to

        Returns:
            List[StandardizedOrganization]: A list of standardized organizations within this Git Instance
        """
        pass

    @abstractmethod
    def get_users(
        self, standardized_organization: StandardizedOrganization, limit: int = None
    ) -> Generator[StandardizedUser, None, None]:
        """Get the list of users in a given Git Organization

        Args:
            standardized_organization (StandardizedOrganization): A standardized Git Organization Object

        Returns:
            List[StandardizedUser]: A standardized User Object
            limit (int, optional): When provided, the number of items returned is limited.
                Useful for the validation use case, where we want to just verify we can pull PRs.
                Defaults to None.
        """
        pass

    @abstractmethod
    def get_teams(
        self, standardized_organization: StandardizedOrganization, limit: int = None
    ) -> Generator[StandardizedTeam, None, None]:
        """Get the list of teams in a given Git Organization

        Args:
            standardized_organization (StandardizedOrganization): A standardized Git Organization Object

        Returns:
            List[StandardizedUser]: A standardized Team Object
            limit (int, optional): When provided, the number of items returned is limited.
                Useful for the validation use case, where we want to just verify we can pull PRs.
                Defaults to None.
        """
        pass

    @abstractmethod
    def get_repos(
        self,
        standardized_organization: StandardizedOrganization,
    ) -> Generator[StandardizedRepository, None, None]:
        """Get a list of standardized repositories within a given organization

        Args:
            standardized_organization (StandardizedOrganization): A standardized organization

        Returns:
            List[StandardizedRepository]: A list of standardized Repositories
        """
        pass

    @abstractmethod
    def get_commits_for_default_branch(
        self, standardized_repo: StandardizedRepository
    ) -> Generator[StandardizedCommit, None, None]:
        """For a given repo, get all the commits that are on the Default Branch.

        Args:
            standardized_repo (StandardizedRepository): A standard Repository object

        Returns:
            List[StandardizedCommit]: A list of standardized commits
        """
        pass

    @abstractmethod
    def get_branches_for_repo(
        self,
        standardized_repo: StandardizedRepository,
        redact_names_and_urls: bool,
        pull_branches: Optional[bool] = False,
    ) -> Generator[StandardizedBranch, None, None]:
        """Function for pulling branches for a repository. By default, pull_branches will run as False,
        so we will only process the default branch. If pull_branches is true, than we will pull all
        branches in this repository

        Args:
            standardized_repo (StandardizedRepository): A standardized repo, which hold info about the default branch.
            redact_names_and_urls (bool): boolean flag for redacting branch names
            pull_branches (bool): A boolean flag. If True, pull all branches available on Repo. If false, only process the default branch. Defaults to False.

        Yields:
            StandardizedBranch: A Standardized Branch Object
        """
        pass

    @abstractmethod
    def get_commits_for_branches(
        self,
        standardized_repo: StandardizedRepository,
        branches: List[StandardizedBranch],
        pull_since: datetime = None,
        pull_until: datetime = None,
    ) -> Generator[StandardizedCommit, None, None]:
        """For a given repo, get all the commits that are on the included branches.
        Included branches are found by crawling across the branches pulled/available
        from get_filtered_branches

        Args:
            standardized_repo (StandardizedRepository): A standard Repository object
            pull_since (datetime): A date to pull from
            pull_until (datetime): A date to pull up to

        Returns:
            List[StandardizedCommit]: A list of standardized commits
        """
        pass

    @abstractmethod
    def get_pr_metadata(
        self,
        standardized_repo: StandardizedRepository,
        limit: int = None,
        pull_since: datetime = None,
        pull_until: datetime = None,
    ) -> Generator[StandardizedPullRequestMetadata, None, None]:
        """Get all PRs, but only included the bare necesaties

        Args:
            standardized_repo (StandardizedRepository): A standardized repository
            limit (int, optional): When provided, the number of items returned is limited.
                Useful for the validation use case, where we want to just verify we can pull PRs.
                Defaults to None.
            pull_since (datetime): A date to pull from
            pull_until (datetime): A date to pull up to

        Returns:
            List[StandardizedPullRequest]: A list of standardized PRs
        """
        pass

    @abstractmethod
    def get_prs(
        self,
        standardized_repo: StandardizedRepository,
        pull_files_for_pr: bool = False,
        hash_files_for_prs: bool = False,
        limit: int = None,
        start_cursor: any = None,
    ) -> Generator[StandardizedPullRequest, None, None]:
        """Get the list of standardized Pull Requests for a Standardized Repository.

        Args:
            standardized_repo (StandardizedRepository): A standardized repository
            pull_files_for_pr (bool): When provided, we will pull file metadata for all PRs
            hash_files_for_prs (bool): When provided, all file metadata will be hashed for PRs
            limit (int, optional): When provided, the number of items returned is limited.
                Useful for the validation use case, where we want to just verify we can pull PRs.
                Defaults to None.

        Returns:
            List[StandardizedPullRequest]: A list of standardized PRs
        """
        pass

    def get_commits_for_repo(
        self, standardized_repo: StandardizedRepository, branches: List[StandardizedBranch]
    ) -> Generator[StandardizedCommit, None, None]:
        """This is a function that wraps the get_commits_for_branches function and applies the Repo
        backpopulation logic, if we need it to

        Args:
            standardized_repo (StandardizedRepository): A standardized Repository object
            branches (List[StandardizedBranches]): A list of branches to pull commits for

        Yields:
            Generator[StandardizedCommit, None, None]: A stream of commits. Potentially terminating early if we hit the pull from date
        """
        pull_from_for_commits = self.config.get_pull_from_for_commits()
        backpopulation_window = determine_commit_backpopulation_window(
            config=self.config, repo=standardized_repo
        )
        pull_until_for_commits = None

        # If backpopulating, set
        if backpopulation_window:
            backpopulation_start, backpopulation_end = backpopulation_window
            pull_from_for_commits = backpopulation_start
            pull_until_for_commits = backpopulation_end
            logging_helper.send_to_agent_log_file(
                f'Backpopulation was determeined as necessary for {standardized_repo.name}. Backpopulation will run from [{pull_from_for_commits}, {pull_until_for_commits}]'
            )
        else:
            logging_helper.send_to_agent_log_file(
                f'Backpopulation was not determined as necessary for {standardized_repo.name}. Commits will be pulled from {pull_from_for_commits}'
            )

        commit_count = 0
        commit = None
        for j, commit in enumerate(
            self.get_commits_for_branches(
                standardized_repo=standardized_repo,
                branches=branches,
                pull_since=pull_from_for_commits,
                pull_until=pull_until_for_commits,
            ),
            start=1,
        ):
            with logging_helper.log_loop_iters('branch commit inside repo', j, 100):
                # If we crawl across commits and find that we already have commits this old, stop processing
                # NOTE: THis is technically redundant, because the get_commits calls should have a pull_from/pull_until
                # scheme that should limit how many commits we pull
                if commit.commit_date and commit.commit_date < pull_from_for_commits:
                    break
                yield commit
                commit_count += 1
        if backpopulation_window:
            commits_backpopulated_to = None
            if commit:
                commits_backpopulated_to = max(
                    min(pull_from_for_commits, commit.commit_date), self.config.pull_from
                )
            else:
                commits_backpopulated_to = max(pull_from_for_commits, self.config.pull_from)
            standardized_repo.commits_backpopulated_to = commits_backpopulated_to
            logging_helper.send_to_agent_log_file(
                f'Setting commits_backpopulated_to for repo {standardized_repo.name} to {commits_backpopulated_to}'
            )
        logging_helper.send_to_agent_log_file(f'Found {commit_count} commits')

    def get_prs_for_repo(
        self,
        standardized_repo: StandardizedRepository,
        pull_files_for_pr: bool,
        hash_files_for_prs: bool,
    ) -> Generator[StandardizedPullRequest, None, None]:
        """This is a function that wraps the get_commits_for_branches function and applies the Repo
        backpopulation logic, if we need it to

        Args:
            standardized_repo (StandardizedRepository): A standardized Repository object

        Yields:
            Generator[StandardizedCommit, None, None]: A stream of commits. Potentially terminating early if we hit the pull from date
        """
        prs_start_cursor = None
        backpopulation_window = determine_pr_backpopulation_window(
            config=self.config, repo=standardized_repo
        )
        pull_from_for_pr = self.config.get_pull_from_for_prs(standardized_repo.id)

        # In the backpopulation use case, we need to find the starting mark of where to start
        # pulling PRs. To do this, we leverage the get_pr_metadata function, which should be
        # a light-weight alternative (in terms of API calls) to the get_prs function.
        # For an adapter that uses GQL, this alternative can be VERY light. For a non-GQL
        # adapter, this can be slightly lighter but likely not by much
        if backpopulation_window:
            logging_helper.send_to_agent_log_file(
                f'Backpopulation window detected for PRs in {standardized_repo.name}, attempting to walk back on all PRs to find backpopulation window end date'
            )
            backpopulation_start, backpopulation_end = backpopulation_window
            pull_from_for_pr = backpopulation_start
            prs_found = False
            for api_pr_metadata in self.get_pr_metadata(standardized_repo=standardized_repo):
                if api_pr_metadata.updated_at > backpopulation_end:
                    logging_helper.send_to_agent_log_file(
                        f'Backpopulation flow -- skipping PR (ID: {api_pr_metadata.id}) from {api_pr_metadata.updated_at} '
                        f'because backpopulation_end is {backpopulation_end.isoformat()} (Repo: {standardized_repo.name})'
                    )
                    # This is the START cursor, so it is NON-INCLUSIVE. We want it to be trailing by 1 index
                    prs_start_cursor = api_pr_metadata.api_index
                    continue
                else:
                    if api_pr_metadata.updated_at <= self.config.pull_from:
                        logging_helper.send_to_agent_log_file(
                            f'Exiting backpopulation walkback loop and NOT ingesting this PR, because PR {api_pr_metadata.id} was last updated at {api_pr_metadata.updated_at} which is less than our base pull from date: {self.config.pull_from}'
                        )
                        standardized_repo.prs_backpopulated_to = self.config.pull_from
                        return
                    elif api_pr_metadata.updated_at <= backpopulation_start:
                        # We want to ingest this one PR in this case, because it will greatly fast forward our backpopulation dates
                        logging_helper.send_to_agent_log_file(
                            f'Exiting backpopulation walkback loop, because PR {api_pr_metadata.id} was last updated at {api_pr_metadata.updated_at} which is less than our backpopulation start time ({backpopulation_start}). We WILL ingest this PR'
                        )
                        prs_found = True
                        break
                    else:
                        logging_helper.send_to_agent_log_file(
                            f'Exiting backpopulation walkback loop, because PR {api_pr_metadata.id} was last updated at {api_pr_metadata.updated_at} which is within our backpopulation window ([{backpopulation_start}, {backpopulation_end}]). We will ingest this PR and all other PRs up until {backpopulation_start}'
                        )
                        prs_found = True
                        break

            if not prs_found:
                logging_helper.send_to_agent_log_file(
                    f'No PRs found when looking in and beyond our backpopulation window, setting PRs backpopulated to to the pull from date for this git instance {self.config.pull_from}'
                )
                standardized_repo.prs_backpopulated_to = self.config.pull_from
                return
        pr = None
        pr_count_for_repo = 0
        for i, pr in enumerate(
            self.get_prs(
                standardized_repo=standardized_repo,
                start_cursor=prs_start_cursor,
                pull_files_for_pr=pull_files_for_pr,
                hash_files_for_prs=hash_files_for_prs,
            ),
            start=1,
        ):
            with logging_helper.log_loop_iters('pr inside repo', i, 10):
                # If we crawl across prs and find that we already have PR this old, stop processing
                if pr.updated_at and pr.updated_at <= pull_from_for_pr:
                    logging_helper.send_to_agent_log_file(
                        f'Stopping PR crawl for repo {standardized_repo.name} because PR {pr.id} as been identified as being older than the pull from date ({pr.updated_at} <= {pull_from_for_pr}).'
                    )
                    # If we're backpopulating, this PR represents the next oldest PR. If we ingest it, we can speed up
                    # the backpopulation window to be as old as this PR. Only ingest it if it's within the parent 'pull_from' window, though
                    if backpopulation_window and pr.updated_at >= self.config.pull_from:
                        logging_helper.send_to_agent_log_file(
                            f'This PR ({pr.id}) will be ingest by Jellyfish, because are backpopulating this repo ({standardized_repo.name})'
                        )
                        yield pr
                        pr_count_for_repo += 1
                    break
                yield pr
                pr_count_for_repo += 1
        if backpopulation_window:
            prs_back_populated_to = None
            if pr:
                prs_back_populated_to = max(
                    min(pull_from_for_pr, pr.updated_at), self.config.pull_from
                )
            else:
                prs_back_populated_to = backpopulation_start
            standardized_repo.prs_backpopulated_to = prs_back_populated_to
            logging_helper.send_to_agent_log_file(
                f'Setting prs_backpopulated_to for repo {standardized_repo.name} to {prs_back_populated_to}'
            )

        logging_helper.send_to_agent_log_file(
            f'{pr_count_for_repo} PRs found for repo {standardized_repo.name}'
        )

    def get_filtered_branches(
        self, repo: StandardizedRepository, branches: List[StandardizedBranch]
    ) -> set[str]:
        """Return branches for which we should pull commits, specified by customer in git config.
            The repo's default branch will always be included in the returned list.

        Args:
            repo (StandardizedRepository): A standardized repository

        Returns:
            set[str]: A set of branch names (as strings)
        """

        # Helper function
        def get_matching_branches(
            included_branch_patterns: List[str], repo_branch_names: List[str]
        ) -> List[str]:
            # Given a list of patterns, either literal branch names or names with wildcards (*) meant to match a set of branches in a repo,
            # return the list of branches from repo_branches that match any of the branch name patterns.
            # fnmatch is used over regex to support wildcards but avoid complicating the requirements on branch naming in a user's config.
            matching_branches = []
            for repo_branch_name in repo_branch_names:
                if self.config.pull_all_commits_and_branches:
                    matching_branches.append(repo_branch_name)
                elif any(
                    fnmatch.fnmatch(repo_branch_name, pattern)
                    for pattern in included_branch_patterns
                ):
                    matching_branches.append(repo_branch_name)
            return matching_branches

        # Always process the default branch
        branches_to_process = [repo.default_branch_name] if repo.default_branch_name else []
        # Agent use case: check for the included_branches values
        additional_branches_for_repo = self.config.included_branches_by_repo.get(repo.name, [])

        # Extend and potentially filter branches to process
        repo_branch_names = [b.name for b in branches if b]
        branches_to_process.extend(
            get_matching_branches(additional_branches_for_repo, repo_branch_names)
        )
        return set(branches_to_process)

    def discover_new_orgs(self) -> List[StandardizedOrganization]:
        """Helper function for discovering new Git organizations. Currently
        not implemented because only Github has been implement as a GitAdapter
        subclass, and Github DOES NOT support discovering new orgs. Orgs must
        be entered manually

        Raises:
            NotImplementedError: Error stating that this function is net yet to use yet

        Returns:
            List[StandardizedOrganization]: A list of standardized Org Objects
        """
        raise NotImplementedError('Discover New Orgs is not yet implemented')

    def load_and_dump_git(self, git_config: GitConfig, ingest_config: IngestionConfig):
        """This is a shared class function that can get called by
        the different types of GitAdapters that extend this class.
        This function handles fetching all the necessary data from
        Git, transforming it, and saving it to local disk and/or S3

        Args:
            ingest_config (IngestionConfig): A valid Ingestion Config
        """
        logging_helper.set_ingestion_type(ingest_config.ingest_type)
        #######################################################################
        # Init IO Helper
        #######################################################################
        ingest_io_helper = IngestIOHelper(ingest_config=ingest_config)

        # Wrapper function for writing to the IngestIOHelper
        def _write_to_s3_or_local(object_name: str, json_data: list[dict], batch_number: int = 0):
            ingest_io_helper.write_json_to_local_or_s3(
                object_name=object_name,
                json_data=json_data,
                subdirectory=SubDirectory.GIT,
                save_locally=ingest_config.save_locally,
                upload_to_s3=ingest_config.upload_to_s3,
                git_instance_key=self.config.instance_file_key,
                batch_number=batch_number,
            )

        #######################################################################
        # ORGANIZATION DATA
        #######################################################################
        logger.info('Fetching Git Organization Data...')
        standardized_organizations: List[StandardizedOrganization] = self.get_organizations()
        logger.info(
            f'Successfully pulled Git Organizations data for {len(standardized_organizations)} Organizations.'
        )
        # Upload Data
        _write_to_s3_or_local(
            object_name=GitObject.GitOrganizations.value,
            json_data=_transform_dataclass_list_to_dict(standardized_organizations),
        )

        #######################################################################
        # USER DATA
        #######################################################################
        if not git_config.skip_pulling_users:
            logger.info('Fetching Git User Data...')
            standardized_users: List[StandardizedUser] = [
                user
                for org in standardized_organizations
                for user in tqdm_to_logger(
                    self.get_users(org), desc='Processing Users', unit=' users'
                )
            ]
            logger.info(f'Successfully found {len(standardized_users)} users.')
            # Upload Data
            _write_to_s3_or_local(
                object_name=GitObject.GitUsers.value,
                json_data=_transform_dataclass_list_to_dict(standardized_users),
            )
        else:
            _write_to_s3_or_local(
                object_name=GitObject.GitUsers.value,
                json_data=[],
            )
            logger.info(
                f'Not pulling users because \'skip_pulling_users\' is set to: {git_config.skip_pulling_users}.'
            )

        #######################################################################
        # TEAM DATA
        #######################################################################
        logger.info('Fetching Git Team Data...')
        standardized_teams: List[StandardizedTeam] = [
            team
            for org in standardized_organizations
            for team in tqdm_to_logger(self.get_teams(org), desc="Processing Teams", unit=" teams")
        ]
        logger.info(f'Successfully found {len(standardized_teams)} teams.')
        # Upload Data
        _write_to_s3_or_local(
            object_name=GitObject.GitTeams.value,
            json_data=_transform_dataclass_list_to_dict(standardized_teams),
        )

        #######################################################################
        # REPO DATA, NOTE THAT WE UPLOAD LATER BECAUSE WE NEED TO SET
        # THE BACKPOPULATD DATES BELOW AFTER WE PULL PRS AND COMMITS
        #######################################################################
        if not git_config.skip_pulling_repos:
            logger.info('Fetching Git Repo Data...')
            standardized_repos: List[StandardizedRepository] = [
                repo
                for org in standardized_organizations
                for repo in tqdm_to_logger(
                    self.get_repos(
                        standardized_organization=org,
                    ),
                    unit=' repos',
                    desc=f'Pulling all available Repositories',
                )
            ]
            logger.info(f'Successfully pulled Git Repo Data for {len(standardized_repos)} Repos.')
        else:
            logger.info(
                f'Not pulling new repo data because \'skip_pulling_repos\' is set to {git_config.skip_pulling_repos}. '
                f'We will pull data for the {len(git_config.repos_in_jellyfish)} repos that already exist in Jellyfish'
            )
            standardized_repos = git_config.repos_in_jellyfish

        repos_to_process = [
            repo for repo in standardized_repos if repo.id not in git_config.quiescent_repos
        ]

        repo_count = len(repos_to_process)

        logging_helper.send_to_agent_log_file(
            f'Processing {len(repos_to_process)} ({len(git_config.quiescent_repos)} were marked as being quiescent)'
        )

        #######################################################################
        # BRANCH DATA
        # NOTE: Branches are optionally processed, depending on GitConfiguration.
        # For Direct Connect it is likely we only process the default branch,
        # for agent we process all branches
        #######################################################################
        repo_to_branches: dict[str, List[StandardizedBranch]] = {}
        all_branches = []
        with tqdm_to_logger(desc='Processing Branches', unit=' Branches') as pbar:
            for repo in repos_to_process:
                pull_branches = (
                    git_config.pull_all_commits_and_branches
                    or git_config.repo_id_to_pull_all_commits_and_branches.get(repo.id)
                )
                branch_batch = []
                # Iterate across branches and update the progress bar so we can see
                # counts and rates of branch processing
                for branch in self.get_branches_for_repo(
                    repo, git_config.git_redact_names_and_urls, pull_branches
                ):
                    pbar.update(1)
                    branch_batch.append(branch)

                repo_to_branches[repo.id] = branch_batch
                all_branches.extend(branch_batch)

        _write_to_s3_or_local(
            object_name=GitObject.GitBranches.value,
            json_data=_transform_dataclass_list_to_dict(all_branches),
        )

        #######################################################################
        # COMMIT DATA
        #
        # NOTE: Commit data can be quite large, so for better memory handling
        # we will create a chain of generators (get_commits_for_branches returns a generator)
        # and process our way through those generators, uploading data ~50 MBs at a time
        # NOTE: Commit data is pretty uniform in size (each commit is ~2KB), so we'll upload
        # in batches of 30k commits (roughly 50 MB in data)
        #
        #######################################################################
        total_commits = 0
        logger.info(f'Fetching Git Commit Data for {repo_count} Repos...')
        list_of_commit_generators: List[Generator[StandardizedCommit, None, None]] = []
        for repo in repos_to_process:
            branches = repo_to_branches[repo.id]
            commit_generator_for_repo = self.get_commits_for_repo(repo, branches=branches)
            transformed_commit_generator = map(lambda commit: commit, commit_generator_for_repo)
            list_of_commit_generators.append(transformed_commit_generator)

        # Chain together all the generators
        commits_generator = tqdm_to_logger(
            chain.from_iterable(list_of_commit_generators),
            desc=f'Processing Commits for {repo_count} repos',
            unit=' commits',
        )
        for batch_num, commit_batch in enumerate(
            batch_iterable(commits_generator, batch_size=self.NUMBER_OF_COMMITS_PER_BATCH)
        ):
            total_commits += len(commit_batch)
            commit_batch_as_dict = _transform_dataclass_list_to_dict(commit_batch)
            _write_to_s3_or_local(
                object_name=GitObject.GitCommits.value,
                json_data=commit_batch_as_dict,
                batch_number=batch_num,
            )
        if not total_commits:
            _write_to_s3_or_local(object_name=GitObject.GitCommits.value, json_data=[])
        logger.info(f'Successfully process {total_commits} total commits')

        #######################################################################
        # PULL REQUEST DATA
        #
        # NOTE: Pull Request data can be quite large, so for better memory handling
        # we will create a chain of generators (get_prs returns a generator)
        # and process our way through those generators, uploading data ~50 MBs at a time
        #
        #######################################################################
        total_prs = 0
        logger.info(f'Fetching Git Pull Request Data for {repo_count} Repos...')
        list_of_pr_generators: List[Generator[StandardizedPullRequest, None, None]] = []
        for repo in repos_to_process:
            if self.config.repos_to_skip_pull_prs_for.get(repo.id):
                logging_helper.send_to_agent_log_file(
                    f'Skipping pull PRs for {repo.name} because it was marked in Jellyfish as so'
                )
                continue
            pr_generator_for_repo = self.get_prs_for_repo(
                repo,
                pull_files_for_pr=git_config.pull_files_for_prs,
                hash_files_for_prs=git_config.hash_files_for_prs,
            )
            transformed_pr_generator = map(lambda pr: asdict(pr), pr_generator_for_repo)
            list_of_pr_generators.append(transformed_pr_generator)

        # Chain together all the generators
        prs_generator = tqdm_to_logger(
            chain.from_iterable(list_of_pr_generators),
            desc=f'Processing Pull Request Data for {repo_count} repos',
            unit=' PRs',
        )
        for batch_num, pr_batch in enumerate(
            batch_iterable_by_bytes_size(
                prs_generator, batch_byte_size=self.PULL_REQUEST_BATCH_SIZE_IN_BYTES
            )
        ):
            total_prs += len(pr_batch)
            _write_to_s3_or_local(
                object_name=GitObject.GitPullRequests.value,
                json_data=pr_batch,
                batch_number=batch_num,
            )

        if not total_prs:
            # IF we don't have any PRs, push an empty file
            _write_to_s3_or_local(
                object_name=GitObject.GitPullRequests.value,
                json_data=[],
                batch_number=0,
            )

        logger.info(f'Successfully processed {total_prs} total PRs')

        # Upload Repo Data at the very end
        _write_to_s3_or_local(
            object_name=GitObject.GitRepositories.value,
            json_data=_transform_dataclass_list_to_dict(standardized_repos)
            if standardized_repos
            else [],
        )

        logger.info(f'Done processing Git Data!')


@diagnostics.capture_timing()
@logging_helper.log_entry_exit()
def load_and_push_git_to_s3(ingest_config: IngestionConfig):
    """Handler function for the end to end processing of Git Data.
    This function is responsible for taking in an ingest config,
    creating a git adapter, and then running the Git Adapter function
    for uploading data to S3 (or saving it locally). The function for
    handling that logic is part of the GitAdapter class (see load_and_dump_git)

    Args:
        ingest_config (IngestionConfig): A fully formed IngestionConfig class, with
        valid Git Configuration in it.
    """
    for git_config in ingest_config.git_configs:
        try:
            git_adapter: GitAdapter = GitAdapter.get_git_adapter(git_config)
            git_adapter.load_and_dump_git(git_config=git_config, ingest_config=ingest_config)
        except GitProviderUnavailable:
            logger.warning(
                f'Git Config for provider {git_config.git_provider} is currently NOT supported!'
            )
            continue


def determine_commit_backpopulation_window(
    config: GitConfig, repo: StandardizedRepository
) -> BackpopulationWindow:
    """Get the backpopulation window for Commits

    Args:
        config (GitConfig): A valid Git Config
        repo (StandardizedRepository): A valid standardized repository

    Returns:
        BackpopulationWindow: A Backpopulation window object
    """
    commits_backpopulated_to = config.get_backpopulated_date_for_commits(repo.id)
    return _get_backpopulation_helper(
        repo=repo,
        git_config=config,
        objects_back_populated_to=commits_backpopulated_to,
        object_name='commits',
    )


def determine_pr_backpopulation_window(
    config: GitConfig, repo: StandardizedRepository
) -> BackpopulationWindow:
    """Get the backpopulation window for PRs

    Args:
        config (GitConfig): A valid Git Config
        repo (StandardizedRepository): A valid standardized repository

    Returns:
        BackpopulationWindow: A Backpopulation window object
    """
    prs_backpopulated_to = config.get_backpopulated_date_for_prs(repo.id)
    return _get_backpopulation_helper(
        repo=repo,
        git_config=config,
        objects_back_populated_to=prs_backpopulated_to,
        object_name='PRs',
    )


def _get_backpopulation_helper(
    repo: StandardizedRepository,
    git_config: GitConfig,
    objects_back_populated_to: datetime,
    object_name: str,
) -> BackpopulationWindow:
    if objects_back_populated_to and objects_back_populated_to <= git_config.pull_from:
        # No backpopulation necessary
        return None

    # We're backpopulating objects for this repo

    if objects_back_populated_to:
        base_date = objects_back_populated_to
    else:
        base_date = datetime.now().astimezone(timezone.utc) + timedelta(days=1)

    backpopulation_window_start = (
        git_config.pull_from
        if git_config.force_full_backpopulation_pull
        else max(
            git_config.pull_from, base_date - timedelta(days=git_config.backpopulation_window_days)
        )
    )
    backpopulation_window_end = base_date

    logging_helper.send_to_agent_log_file(
        f'Backpopulation window found for {object_name} for repo {repo.name}. Window spans from {backpopulation_window_start} to {backpopulation_window_end}'
    )
    return BackpopulationWindow(backpopulation_window_start, backpopulation_window_end)
