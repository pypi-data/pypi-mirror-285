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
    Commit
'''
import logging
from rlabs_gitlab_release_bot import gitlab
from pathlib import Path
from rlabs_mini_box.data import Box
from typing import Optional
from typing import Any

from rlabs_gitlab_release_bot.error import InvalidBumpPrefixes
from rlabs_gitlab_release_bot.types import BumpedCommits
from rlabs_gitlab_release_bot.types import BumpPrefixes

DEFAULT_MAJOR_PREFIXES = [
    "breaking change"
]
DEFAULT_MINOR_PREFIXES = [
    "feat"
]
DEFAULT_PATCH_PREFIXES = [
    'chore',
    'fix',
    'refactor',
    'perf',
    'docs',
    'style',
    'test',
    'build',
    'ci',
    'revert'
]


def filter_commits_major(
        commit_messages: list,
        bump_prefixes: list[str]
    ) -> list:
    '''
        Finds those commits that will create a major bump
        based on the bump prefixes received
    '''
    filtered_list = []
    for msg in commit_messages:
        for prefix in bump_prefixes:
            if msg.lower().startswith(prefix.lower() + ':'):
                filtered_list.append(msg)

    return filtered_list

def filter_commits_minor(
        commit_messages: list,
        bump_prefixes: list[str]
    ) -> list:
    '''
        Finds those commits that will create a minor bump
        based on the bump prefixes received
    '''
    filtered_list = []
    for msg in commit_messages:
        for prefix in bump_prefixes:
            if msg.lower().startswith(prefix.lower() + ':'):
                filtered_list.append(msg)

    return filtered_list

def filter_commits_patch(
        commit_messages: list,
        bump_prefixes: list[str]
    ) -> list:
    '''
        Finds those commits that will create a patch bump
        based on the bump prefixes received
    '''
    filtered_list = []
    for msg in commit_messages:
        for prefix in bump_prefixes:
            if msg.lower().startswith(prefix.lower() + ':'):
                filtered_list.append(msg)

    return filtered_list

def bump_commits_messages(
        token: str,
        project_id: int,
        branch:str,
        last_tag: dict,
        last_commit: dict,
        bump_prefixes: BumpPrefixes,
        skip_ci_tag: str,
        response_log_dir: Path,
        logger: logging.Logger
    ) -> BumpedCommits:
    '''
        Bump Commit Messages

        Returns commit messages between the last tag and the last commit in the branch
        that will create a major, minor or patch bump.

        IOW all commit messages since the last tag that have valid bump prefixes,
        organized as major, minor and patch.

        The default bump prefixes can be overriden by passing a dictionary:
            {
                "major": ["breaking change"],
                "minor": ["feat"],
                "patch": [
                    'chore',
                    ...
                ]
            }


        NOTE:
            - Commit mesages with the skip ci tag (skip_ci_tag) are ignored

        Args:
            token: gitlab token
            project_id: gitlab project id
            branch: gitlab branch
            last_tag: last tag
            last_commit: last commit
            bump_prefixes: dictionary with the major, minor and patch bump prefixes

        Returns:
            A dictionary with the major, minor and patch bump commit messages
    '''
    logger.info(
        "Finding bump commit messages between last tag and last commit"
    )

    __validate_bump_prefix_dict(
        bump_prefixes
    )

    if bump_prefixes:
        # user what was passed
        bump_prefixes_to_use: BumpPrefixes = bump_prefixes
    else:
        # use defaults
        bump_prefixes_to_use = {
            "major": DEFAULT_MAJOR_PREFIXES,
            "minor": DEFAULT_MINOR_PREFIXES,
            "patch": DEFAULT_PATCH_PREFIXES
        }

    bump_prefixes_to_use_pretty_json = (Box(bump_prefixes_to_use)
        .to_json(indent=2).data()
    )
    logger.debug(
        f"Using bump prefixes: {bump_prefixes_to_use_pretty_json}"
    )

    commits = gitlab.commits_date_range(
        token=token,
        project_id=project_id,
        branch=branch,
        since=last_tag['commit']['created_at'],
        until=last_commit['created_at'],
        response_log_dir=response_log_dir,
        logger=logger
    )

    commit_messages = [
        #
        # - ignore commits that have "skip ci" in them
        # - adds the short id to the message
        #
        f"{commit["message"].rstrip("\n").rstrip(" ")} ({commit["short_id"]})" for commit in commits
        if skip_ci_tag.lower() not in commit["message"].lower()
    ]

    major_bumps = filter_commits_major(
        commit_messages,
        bump_prefixes_to_use["major"]
    )
    minor_bumps = filter_commits_minor(
        commit_messages,
        bump_prefixes_to_use["minor"]
    )
    patch_bumps = filter_commits_patch(
        commit_messages,
        bump_prefixes_to_use["patch"]
    )

    major_bumps_pretty_json = (Box(major_bumps)
        .to_json(indent=2).data()
    )
    minor_bumps_pretty_json = (Box(minor_bumps)
        .to_json(indent=2).data()
    )
    patch_bumps_pretty_json = (Box(patch_bumps)
        .to_json(indent=2).data()
    )

    logger.info(f"major bump commits: \n{major_bumps_pretty_json}")
    logger.info(f"minor bump commits: \n{minor_bumps_pretty_json}")
    logger.info(f"patch bump commits: \n{patch_bumps_pretty_json}")

    return {
        "major": major_bumps,
        "minor": minor_bumps,
        "patch": patch_bumps,
        "bump_prefixes_used":  bump_prefixes_to_use
    }

def __validate_bump_prefix_dict(
        bump_prefixes: BumpPrefixes
    ) -> None:
    '''
        Validate Bump Prefix dict

        Validates the bump prefixes dictionary

        Args:
            bump_prefixes: dictionary with the major, minor and patch bump prefixes

        Raises:
            InvalidBumpPrefixes: if the dictionary is missing any of the keys
    '''
    if bump_prefixes:
        if "major" not in bump_prefixes:
            raise InvalidBumpPrefixes(
                "Missing 'major' key/field in provided bump prefixes. "
                f"We received: \n{bump_prefixes}"
            )
        if "minor" not in bump_prefixes:
            raise InvalidBumpPrefixes(
                "Missing 'minor' key/field in provided bump prefixes. "
                f"We received: \n{bump_prefixes}"
            )
        if "patch" not in bump_prefixes:
            raise InvalidBumpPrefixes(
                "Missing 'patch' key/field in provided bump prefixes. "
                f"We received: \n{bump_prefixes}"
            )
        if not isinstance(bump_prefixes["major"], list):
            raise InvalidBumpPrefixes(
                "The 'major' field in bump prefixes should be a list. "
                f"We received: \n{bump_prefixes}"
            )
        if not isinstance(bump_prefixes["minor"], list):
            raise InvalidBumpPrefixes(
                "The 'minor' field in bump prefixes should be a list. "
                f"We received: \n{bump_prefixes}"
            )
        if not isinstance(bump_prefixes["patch"], list):
            raise InvalidBumpPrefixes(
                "The 'patch' field in bump prefixes should be a list. "
                f"We received: \n{bump_prefixes}"
            )
