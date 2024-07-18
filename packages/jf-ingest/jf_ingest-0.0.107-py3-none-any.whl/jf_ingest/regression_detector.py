import sys

if __name__ == "__main__":
    """
    This is a developer utility to detect possible regressions in changes that have been made. To use, first
    run the harness twice. One with an older copy of this repo containing a known-good state and another that
    includes your changes.

    Make note of the output folder locations for each run.

    Then run: pdm run regression_detector <path_to_old_harness_output> <path_to_new_harness_output> [--git, --jira]

    This will compare the two outputs and detect notable differences.
    """
    include_git = '--git' in sys.argv
    include_jira = '--jira' in sys.argv
    orig_dir = sys.argv[1]
    changes_dir = sys.argv[2]

    if include_jira:
        orig_jira_ids = set()
        new_jira_ids = set()
        # Right now this only does one check: compare the issue count of downloaded jira ids and ensure they're close.
        with open(f"{orig_dir}/jira/jira_issue_ids_downloaded.json", "r") as f:
            id_lines = f.readlines()
            for id in id_lines:
                orig_jira_ids.add(id.strip('\n \t ,'))

        with open(f"{changes_dir}/jira/jira_issue_ids_downloaded.json", "r") as f:
            id_lines = f.readlines()
            for id in id_lines:
                new_jira_ids.add(id.strip('\n \t ,'))

        # We expect a few tickets to have been added or removed between runs,
        # but let's say 10 is the threshold which warrants investigation.
        if abs(len(orig_jira_ids) - len(new_jira_ids)) > 10:
            print(f"Jira issue count mismatch: {len(orig_jira_ids)} vs {len(new_jira_ids)}")
            print(f"Issues in original that appear gone: {orig_jira_ids - new_jira_ids}")
            print(f"Issues in new that did not exist before: {new_jira_ids - orig_jira_ids}")

            exit(1)

    print("No issues detected.")
