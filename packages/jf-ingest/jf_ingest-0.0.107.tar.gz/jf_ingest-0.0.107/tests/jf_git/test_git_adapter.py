from datetime import datetime, timedelta, timezone

from jf_ingest.config import GitConfig
from jf_ingest.jf_git.adapters import (
    BackpopulationWindow,
    determine_commit_backpopulation_window,
    determine_pr_backpopulation_window,
)
from jf_ingest.jf_git.standardized_models import StandardizedOrganization, StandardizedRepository

GIT_CONFIG_DEFAULTS = {
    'company_slug': 'test_company',
    'instance_slug': 'test_instance',
    'instance_file_key': 'test_FILEKEY',
    'git_provider': 'GITHUB',
    'git_auth_config': None,
}

GIT_TEST_ORG = StandardizedOrganization(id='test_org', name='Test Org', login='Test-Org', url='')
GIT_TEST_REPO = StandardizedRepository(
    id='1',
    name='test_repo',
    full_name='test_repo_full_name',
    url='',
    is_fork=False,
    default_branch_name='main',
    default_branch_sha='test',
    organization=GIT_TEST_ORG,
)


def create_git_config(*args, **kwargs):
    return GitConfig(*args, **kwargs)


def test_backpopulation_window_helper_confirm_always_none_cases():
    pull_from = datetime(2024, 1, 1)
    object_last_pulled_date = pull_from

    git_config_args = {
        'pull_from': pull_from,
        'force_full_backpopulation_pull': True,
        'backpopulation_window_days': 10,
        'repos_to_prs_backpopulated_to': {GIT_TEST_REPO.id: object_last_pulled_date},
        'repos_to_commits_backpopulated_to': {GIT_TEST_REPO.id: object_last_pulled_date},
        **GIT_CONFIG_DEFAULTS,
    }
    config = create_git_config(**git_config_args)
    repo = GIT_TEST_REPO

    prs_back_population_window = determine_pr_backpopulation_window(config=config, repo=repo)
    commits_back_population_window = determine_commit_backpopulation_window(
        config=config, repo=repo
    )
    assert commits_back_population_window == None
    assert prs_back_population_window == None

    ######################################################
    git_config_args = {
        'pull_from': pull_from,
        'force_full_backpopulation_pull': True,
        'backpopulation_window_days': 10,
        'repos_to_prs_backpopulated_to': {
            GIT_TEST_REPO.id: object_last_pulled_date - timedelta(days=1)
        },
        'repos_to_commits_backpopulated_to': {
            GIT_TEST_REPO.id: object_last_pulled_date - timedelta(days=1)
        },
        **GIT_CONFIG_DEFAULTS,
    }
    config = create_git_config(**git_config_args)
    repo = GIT_TEST_REPO

    prs_back_population_window = determine_pr_backpopulation_window(config=config, repo=repo)
    commits_back_population_window = determine_commit_backpopulation_window(
        config=config, repo=repo
    )
    assert commits_back_population_window == None
    assert prs_back_population_window == None


def test_backpopulation_window_helper_with_force_pull():
    pull_from = datetime(2024, 1, 1)
    object_last_pulled_date = datetime(2024, 2, 1)
    git_config_args = {
        'pull_from': pull_from,
        'repos_to_prs_backpopulated_to': {GIT_TEST_REPO.id: object_last_pulled_date},
        'force_full_backpopulation_pull': True,
        **GIT_CONFIG_DEFAULTS,
    }
    config = create_git_config(**git_config_args)
    repo = GIT_TEST_REPO

    prs_back_population_window = determine_pr_backpopulation_window(config=config, repo=repo)
    commits_back_population_window = determine_commit_backpopulation_window(
        config=config, repo=repo
    )
    assert prs_back_population_window == BackpopulationWindow(pull_from, object_last_pulled_date)

    #############################
    git_config_args = {
        'pull_from': pull_from,
        'repos_to_commits_backpopulated_to': {GIT_TEST_REPO.id: object_last_pulled_date},
        'force_full_backpopulation_pull': True,
        **GIT_CONFIG_DEFAULTS,
    }
    config = create_git_config(**git_config_args)
    repo = GIT_TEST_REPO

    prs_back_population_window = determine_pr_backpopulation_window(config=config, repo=repo)
    commits_back_population_window = determine_commit_backpopulation_window(
        config=config, repo=repo
    )
    assert commits_back_population_window == BackpopulationWindow(
        pull_from, object_last_pulled_date
    )


def test_backpopulation_window_helper_with_custom_days_window():
    pull_from = datetime(2024, 1, 1, tzinfo=timezone.utc)
    object_last_pulled_date = datetime(2024, 2, 1, tzinfo=timezone.utc)
    backpop_window_days = 10
    target_backpopulation_start_date = object_last_pulled_date - timedelta(days=backpop_window_days)
    git_config_args = {
        'pull_from': pull_from,
        'repos_to_prs_backpopulated_to': {GIT_TEST_REPO.id: object_last_pulled_date},
        'backpopulation_window_days': backpop_window_days,
        **GIT_CONFIG_DEFAULTS,
    }
    config = create_git_config(**git_config_args)
    repo = GIT_TEST_REPO

    prs_back_population_window = determine_pr_backpopulation_window(config=config, repo=repo)
    commits_back_population_window = determine_commit_backpopulation_window(
        config=config, repo=repo
    )
    assert prs_back_population_window == BackpopulationWindow(
        target_backpopulation_start_date, object_last_pulled_date
    )

    #############################
    git_config_args = {
        'pull_from': pull_from,
        'repos_to_commits_backpopulated_to': {GIT_TEST_REPO.id: object_last_pulled_date},
        'backpopulation_window_days': backpop_window_days,
        **GIT_CONFIG_DEFAULTS,
    }
    config = create_git_config(**git_config_args)
    repo = GIT_TEST_REPO

    prs_back_population_window = determine_pr_backpopulation_window(config=config, repo=repo)
    commits_back_population_window = determine_commit_backpopulation_window(
        config=config, repo=repo
    )
    assert commits_back_population_window == BackpopulationWindow(
        target_backpopulation_start_date, object_last_pulled_date
    )

    ##############################
    git_config_args = {
        'pull_from': pull_from,
        'repos_to_prs_backpopulated_to': {GIT_TEST_REPO.id: object_last_pulled_date},
        'repos_to_commits_backpopulated_to': {GIT_TEST_REPO.id: object_last_pulled_date},
        'backpopulation_window_days': backpop_window_days,
        **GIT_CONFIG_DEFAULTS,
    }
    config = create_git_config(**git_config_args)
    repo = GIT_TEST_REPO

    prs_back_population_window = determine_pr_backpopulation_window(config=config, repo=repo)
    commits_back_population_window = determine_commit_backpopulation_window(
        config=config, repo=repo
    )
    assert commits_back_population_window == BackpopulationWindow(
        target_backpopulation_start_date, object_last_pulled_date
    )
    assert prs_back_population_window == BackpopulationWindow(
        target_backpopulation_start_date, object_last_pulled_date
    )


def test_backpopulation_window_when_there_is_no_data_in_jellyfish():
    pull_from = datetime(2024, 1, 1, tzinfo=timezone.utc)
    start_time = datetime.now().astimezone(timezone.utc)
    backpop_window_days = 10
    git_config_args = {
        'pull_from': pull_from,
        'backpopulation_window_days': backpop_window_days,
        **GIT_CONFIG_DEFAULTS,
    }
    config = create_git_config(**git_config_args)
    repo = GIT_TEST_REPO

    prs_back_population_window = determine_pr_backpopulation_window(config=config, repo=repo)
    commits_back_population_window = determine_commit_backpopulation_window(
        config=config, repo=repo
    )
    assert commits_back_population_window.backpopulation_window_end >= start_time
    assert prs_back_population_window.backpopulation_window_end >= start_time
    assert (
        prs_back_population_window.backpopulation_window_end
        - prs_back_population_window.backpopulation_window_start
    ).days == 10
    assert (
        commits_back_population_window.backpopulation_window_end
        - commits_back_population_window.backpopulation_window_start
    ).days == 10

    #####################################################
    git_config_args = {
        'pull_from': pull_from,
        'force_full_backpopulation_pull': True,
        **GIT_CONFIG_DEFAULTS,
    }
    config = create_git_config(**git_config_args)
    repo = GIT_TEST_REPO

    prs_back_population_window = determine_pr_backpopulation_window(config=config, repo=repo)
    commits_back_population_window = determine_commit_backpopulation_window(
        config=config, repo=repo
    )
    assert commits_back_population_window.backpopulation_window_end >= start_time
    assert prs_back_population_window.backpopulation_window_end >= start_time
    assert prs_back_population_window.backpopulation_window_start == pull_from
    assert commits_back_population_window.backpopulation_window_start == pull_from
