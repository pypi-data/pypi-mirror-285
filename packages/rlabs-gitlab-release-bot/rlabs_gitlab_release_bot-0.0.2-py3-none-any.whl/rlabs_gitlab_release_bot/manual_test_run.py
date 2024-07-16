#
# Copyright (C) 2024 RomanLabs, Rafael Roman Otero
# This file is part of RLabs Gitlab Release Bot.
#
# RLabs Gitlab Release Bot is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RLabs Gitlab Release Bot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with RLabs Gitlab Release Bot. If not, see <http://www.gnu.org/licenses/>.
#
'''
    Run Manual Test
    (entry point)

    For help type:
      poetry run manual-test-run --help

'''
import os
import logging
import json
from pathlib import Path
import random
import string

from rlabs_gitlab_release_bot.release import ReleaseBot
from rlabs_gitlab_release_bot import gitlab as release_gitlab


#
# There are TWO TEST PROJECTS, but here
#
#   =====  WE ONLY USE TEST_PROJECT2 here =====
#
# - Test Project 1
#    -- for testing uniquely version and changelog
#    -- has specific branches and commits for this test
#    -- used by pytest
#
# - Test Project 2
#    -- For testing the whole process (get_version_and_changelog, commit_and_tag)
#    -- commits and tags will be pushed
#
RLABS_GITLAB_RELEASE_BOT2_TEST_PROJECT_ID = 59908869
TEST_PROJECT2_ID = RLABS_GITLAB_RELEASE_BOT2_TEST_PROJECT_ID

token_test_project2 = os.environ["TOKEN_TEST_PROJECT2"]

#
# Test Files exists both in this repo (only LOCALLY) and in the test project
# In this repo they are never pushed to origin, but they are created here
# written to and then pushed to the test project, where they happen to exist
# in the same path.
#

# LOCAL paths (from current directory)
LOCAL_PATH_TO_TEST_CHANGELOG = Path("../test_files/TEST_CHANGELOG.md")
LOCAL_PATH_TO_VERSION_FILE = Path("../test_files/TEST_VERSION_FILE")
LOCAL_PATH_TO_TEST_FILE = Path("../test_files/TEST_FILE")

# TEST PROJECT 2 paths (from root)
TEST_PROJECT2_PATH_TO_TEST_CHANGELOG = Path("test_files/TEST_CHANGELOG.md")
TEST_PROJECT2_PATH_TO_VERSION_FILE = Path("test_files/TEST_VERSION_FILE")
TEST_PROJECT2_PATH_TO_TEST_FILE = Path("test_files/TEST_FILE")

def dummy_change_log():
    '''
        dummy_change_log
    '''
    return """
# Changelog

## July 11, 2024 (version 0.0.1)
### Continuous Integration
- ci: Add GitHub Actions for automated testing (#e4f5g6)
"""

def __random_string(length: int) -> str:
    '''
       Returns a random string of the specified length
    '''
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def main():
    '''
        main
    '''
    test_all_locally_and_with_test_project_2()


def test_all_locally_and_with_test_project_2() -> None:
    '''
        Test all locally and with test project 2

        This tests

        - bot.get_next_version_and_changelog (TEST PROJECT 2)
        - bot.update_changelog_file (LOCALLY)
        - bot.update_version_in_file (LOCALLY)
        - bot.commit_and_tag (FROM LOCAL TO TEST_PROJECT 2)

        The distinction is made because it can be COMPLICATED
        TO UNDERSTAND what's going on. Are we changing the test
        files from this repo or the test repo? etc.
    '''
    bot2 = ReleaseBot(
        gitlab_token=token_test_project2,
        gitlab_project_id=TEST_PROJECT2_ID,
        branch="main",
        log_level=logging.DEBUG,
        response_log_dir=Path("../logs")
    )

    #
    # create a commit with a conventional commit message
    #
    __commit_file(
        bot2,
        "feat: random 12-character string",
        TEST_PROJECT2_PATH_TO_TEST_FILE
    )

    #
    # get next version and changelog
    #
    next_version_and_changelog = bot2.get_next_version_and_changelog()

    #
    # export and Load version and changelog
    #
    temp_path = Path(
        # put it in the logs for manual inspection
        bot2.response_log_dir / "manual_test_run" / "version_and_changelog.json"
    )
    temp_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    bot2.export_version_and_changelog(
        next_version_and_changelog,
        temp_path
    )

    next_version_and_changelog = bot2.load_version_and_changelog(
        temp_path
    )


    #
    # update LOCAL changelog file
    #
    #
    # It's local just so 'update_changelog_file' can be tested
    # has nothing to do with this repo (ralbs_gitlab_release_bot)
    #
    # + we'll use what the bot writes in there to commit and tag
    #   in the test project
    #
    try:
        LOCAL_PATH_TO_TEST_CHANGELOG.unlink()
    except FileNotFoundError:
        pass

    LOCAL_PATH_TO_TEST_CHANGELOG.touch()

    bot2.update_changelog_file(
        LOCAL_PATH_TO_TEST_CHANGELOG,
        next_version_and_changelog
    )

    print(
        LOCAL_PATH_TO_TEST_CHANGELOG.read_text()
    )

    #
    # update LOCAL version file
    #
    #
    # It's local just so 'update_version_in_file' can be tested
    # has nothing to do with this repo (ralbs_gitlab_release_bot)
    #
    # + we'll use what the bot writes in there to commit and tag
    #   in the test project
    #
    try:
        LOCAL_PATH_TO_VERSION_FILE.unlink()
    except FileNotFoundError:
        pass

    with open(LOCAL_PATH_TO_VERSION_FILE, "w") as version_file:
        version_file.write(
            '{"version": "0.0.0"}'
        )

    bot2.update_version_in_file(
        LOCAL_PATH_TO_VERSION_FILE,
        next_version_and_changelog["version"]['bumped'],
        regex=r'"version"\s*:\s*"\d+\.\d+\.\d+"'
    )

    print(
        LOCAL_PATH_TO_VERSION_FILE.read_text()
    )

    #
    # commit and tag
    #
    # NOTE:
    #   - We are passing the local path YES. BEcause it will read
    #    the file and commit it to the test project
    #
    #   - The test project has the same path as the local path
    #     and because the TRAILIG "../"'s ARE REMOVED
    #     this works
    bot2.commit_and_tag(
        [
            LOCAL_PATH_TO_TEST_CHANGELOG,
            LOCAL_PATH_TO_VERSION_FILE
        ],
        next_version_and_changelog["version"]['bumped'],
    )

    links_to_dummy_issues_addressed: dict[str, str] = {
        "Dummy Test Issue 1" : "https://gitlab.com/romanlabs/test-projects/test-project-rlabs-gitlab-release-bot-2/-/issues/1",
        "Dummy Test Issue 2" : "https://gitlab.com/romanlabs/test-projects/test-project-rlabs-gitlab-release-bot-2/-/issues/2"
    }

    links_to_dummy_issues_addressed_str: str = ''.join([
         f"- [{issue}]({link})\n"
         for issue, link in links_to_dummy_issues_addressed.items()
    ])

    bot2.create_release(
        next_version_and_changelog,
        f"Update {next_version_and_changelog["version"]['bumped']}. "
        f"The update address the following issues:\n\n{links_to_dummy_issues_addressed_str}"
    )


def __commit_file(
        bot: ReleaseBot,
        commit_message: str,
        test_file_path: Path
    ):
    '''
        Push Dummy Commit
    '''
    # commit test file with random content
    file_path_relative_to_project_root = bot._get_path_relative_to_project_root(
        test_file_path
    )

    actions = [
        {
            "action": "update",
            "file_path": file_path_relative_to_project_root,
            "content": __random_string(12)
        }
    ]

    bot.logger.info(
        f"actions: {json.dumps(actions, indent=2)}"
    )

    release_gitlab.commit_actions(
        bot.gitlab_token,
        bot.gitlab_project_id,
        bot.branch,
        commit_message,
        actions,
        bot.response_log_dir / "manual_test_run",
        logger=bot.logger
    )

