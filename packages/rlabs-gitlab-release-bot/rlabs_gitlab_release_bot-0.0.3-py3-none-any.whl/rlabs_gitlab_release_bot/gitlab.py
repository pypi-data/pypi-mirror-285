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
    Gitlab
'''
import logging
from rlabs_mini_gitlab.gitlab import Gitlab
from rlabs_mini_box.data import Box
from pathlib import Path
from typing import cast
from httpx import HTTPStatusError
from typing import Any

from rlabs_gitlab_release_bot.error import LikelyTagAlreadyExistsError

GITLAB_API_V4_URL = "https://gitlab.com/api/v4"
GITLAB_REQUESTS_GENERAL_TIMEOUT = 11.0

def last_tag(
        token: str,
        project_id: int,
        response_log_dir: Path,
        logger: logging.Logger
    ) -> dict:
    '''
        Last Tag

        Returns the last tag for a project

        Args:
            token: gitlab token
            project_id: gitlab project id

        Sample response:

        # sample last tag

        {
            "name": "0.30.0",
            "message": "",
            "commit": {
                "short_id": "928e34ec",
                "title": "chore: version bump for 0.30.0 [skip ci]",
                "message": "chore: version bump for 0.30.0 [skip ci]",
                "created_at": "2024-07-14T17:18:34.000+00:00"
            },
            "release": {
                "tag_name": "0.30.0",
                "description": "# Changelog\n\n## [0.30.0] - 2024-07-14\n### Added\n- **feat:** random 12-character
            string (55f9522a)\n\nRandom description for test release"
            }
        }

    '''
    logger.info(
        f"Reading last tag for project {project_id}"
    )

    Gitlab.config(
        gitlab_url=GITLAB_API_V4_URL,
        gitlab_token=token,
        requests_general_timeout=GITLAB_REQUESTS_GENERAL_TIMEOUT,
        logger_override=logger,
        response_log_dir=response_log_dir
    )

    databox = (Gitlab.GET
        .projects
        .project_id(project_id)
        .repository
        .tags(
            per_page=1
        )
        .exec()
    )


    tags = (databox  # type: ignore
        .select([
            "name",
            "message",
            "release",
            "commit"
        ])
        .map(
            lambda item: {
                **item,
                "commit": {
                    "short_id": item["commit"]["short_id"],
                    "title": item["commit"]["title"],
                    "message": item["commit"]["message"],
                    "created_at": item["commit"]["created_at"]
                }
            }
        )
        .data()
    )

    if tags:
        tag = tags[0]
    else:
        tag = {}

    tag_pretty_json = (Box(tag)
        .to_json(indent=2).data()
    )

    logger.debug(
        f"Last tag: \n{tag_pretty_json}"
    )

    return tag

def last_commit(
        token: str,
        project_id: int,
        branch: str,
        response_log_dir: Path,
        logger: logging.Logger
    ) -> dict:
    '''
        Last

        Returns the last commit for a project's branch

        Args:
            token: gitlab token
            project_id: gitlab project id
            branch: gitlab branch

        Sample response:

        {
           "short_id": "fcf5c9b7",
           "created_at": "2024-07-14T17:40:34.000+00:00",
           "title": "feat: random 12-character string",
           "message": "feat: random 12-character string"
         }
    '''
    logger.info(
        f"Reading last commit for project {project_id}"
    )

    Gitlab.config(
        gitlab_url=GITLAB_API_V4_URL,
        gitlab_token=token,
        requests_general_timeout=GITLAB_REQUESTS_GENERAL_TIMEOUT,
        logger_override=logger,
        response_log_dir=response_log_dir
    )

    databox = (Gitlab.GET
        .projects
        .project_id(project_id)
        .repository
        .commits(
            ref_name=branch,
            per_page=1
        )
        .exec()
    )

    commits = (databox  # type: ignore
        .select([
            "short_id",
            "title",
            "message",
            "created_at"
        ])
        .data()
    )

    if commits:
        commit = commits[0]
    else:
        commit = {}

    commit_pretty_json = (Box(commit)
        .to_json(indent=2).data()
    )

    logger.debug(
        f"Last commit: \n{commit_pretty_json}"
    )

    return commit

def commits_date_range(
        token: str,
        project_id: int,
        branch: str,
        since: str,
        until: str,
        response_log_dir: Path,
        logger: logging.Logger
    ) -> dict:
    '''
        Range

        For a project's branch, returns the commits that were made between
        the dates 'since' and 'until', inclusive.

        Args:
            token: gitlab token
            project_id: gitlab project id
            branch: gitlab branch
            since: since date [inclusive]
            until: until date [inclusive]
    '''
    logger.debug(
        f"Reading commits between dates {since} and {until} for project {project_id} at branch {branch}"
    )

    Gitlab.config(
        gitlab_url=GITLAB_API_V4_URL,
        gitlab_token=token,
        requests_general_timeout=GITLAB_REQUESTS_GENERAL_TIMEOUT,
        logger_override=logger,
        response_log_dir=response_log_dir
    )

    databox = (Gitlab.GET  # type: ignore
        .projects
        .project_id(project_id)
        .repository
        .commits(
            ref_name=branch,
            per_page=100,
            since=since,
            until=until
        )
        .exec(
            fetch_all=True
        )
    )

    commits = (databox  # type: ignore
        .select([
            "short_id",
            "title",
            "message",
            "created_at"
        ])
        .data()
    )

    commits_pretty_json = (Box(commits)
        .to_json(indent=2).data()
    )

    logger.debug(
        f"Commits: \n{commits_pretty_json}"
    )

    return commits

def file_exists(
    token: str,
    project_id: int,
    branch: str,
    file_path_relative_to_project_root: str,
    response_log_dir: Path,
    logger: logging.Logger
) -> bool:
    '''
        File Exists

        Checks if a file exists in a Gitlab's project

        Args:
         token: gitlab token
            project_id: gitlab project id
            branch: gitlab branch
            response_log_dir: response log directory
            logger: logger to use
    '''
    logger.info(
        f"Checking if file '{file_path_relative_to_project_root}' exists for project {project_id} at branch {branch}"
    )

    Gitlab.config(
        gitlab_url=GITLAB_API_V4_URL,
        gitlab_token=token,
        requests_general_timeout=GITLAB_REQUESTS_GENERAL_TIMEOUT,
        logger_override=logger,
        response_log_dir=response_log_dir
    )

    #encode in between slashes
    encoded_file_path = file_path_relative_to_project_root.replace("/", "%2F")

    try:
        (Gitlab.GET  # type: ignore
            .projects
            .project_id(project_id)
            .repository
            .files
            .file_path(
                encoded_file_path,
                ref=branch
            )
            .exec()
        )
        exists = True
    except HTTPStatusError as error:
        if "404" in str(error):
            exists = False
        else:
            raise error

    logger.debug(
        f"File '{file_path_relative_to_project_root}' exists: {exists}"
    )

    return exists

def commit_actions(
        token: str,
        project_id: int,
        branch: str,
        commit_message: str,
        actions: list[dict[str, str]],
        response_log_dir: Path,
        logger: logging.Logger
    ) -> str:
    '''
        Commit Actions

        Commits actions to a project's branch

        Args:
            token: gitlab token
            project_id: gitlab project id
            branch: gitlab branch
            commit_message: commit message
            actions: list of actions to commit
            response_log_dir: response log directory
            logger: logger to use

        Returns:
            The SHA of the commit that was created
    '''
    logger.info(
        f"Committing actions to project '{project_id}' at branch '{branch}'"
    )

    Gitlab.config(
        gitlab_url=GITLAB_API_V4_URL,
        gitlab_token=token,
        requests_general_timeout=GITLAB_REQUESTS_GENERAL_TIMEOUT,
        logger_override=logger,
        response_log_dir=response_log_dir
    )

    databox = (Gitlab     # type: ignore
        .POST(data={
            "branch": branch,
            "commit_message": commit_message,
            "actions": actions
        })
        .projects
        .project_id(project_id)
        .repository
        .commits
        .exec()
    )

    commit_sha = databox.data()["id"]

    logger.info(
        f"Commit created: '{commit_sha}'"
    )

    return commit_sha

def tag(
    token: str,
    project_id: int,
    commit_sha: str,
    tag_name: str,
    response_log_dir: Path,
    logger: logging.Logger
) -> None:
    '''
        Tag

        Tags a commit

        Args:
            token: gitlab token
            project_id: gitlab project id
            commit_sha: commit sha
            tag_name: tag name
            response_log_dir: response log directory
            logger: logger to use
    '''
    logger.info(
        f"Tagging commit '{commit_sha}' as '{tag_name}' for project '{project_id}'"
    )

    Gitlab.config(
        gitlab_url=GITLAB_API_V4_URL,
        gitlab_token=token,
        requests_general_timeout=GITLAB_REQUESTS_GENERAL_TIMEOUT,
        logger_override=logger,
        response_log_dir=response_log_dir
    )

    try:
        (Gitlab     # type: ignore
            .POST(data={
                "tag_name": tag_name,
                "ref": commit_sha
            })
            .projects
            .project_id(project_id)
            .repository
            .tags
            .exec()
        )
    except HTTPStatusError as error:
        if "400" in str(error):
            raise LikelyTagAlreadyExistsError(
                tag_name,
                project_id
            )
        else:
            raise error

def create_release(
    token: str,
    project_id: int,
    release_name: str,
    tag_name: str,
    description: str,
    response_log_dir: Path,
    logger: logging.Logger
) -> None:
    '''
        Create Release

        Creates a release

        Args:
            token: gitlab token
            project_id: gitlab project id
            release_name: release name
            tag_name: tag name
            description: description
            response_log_dir: response log directory
            logger: logger to use
    '''
    logger.info(
        f"Creating release '{release_name}' on tag '{tag_name}' for project '{project_id}'"
    )

    Gitlab.config(
        gitlab_url=GITLAB_API_V4_URL,
        gitlab_token=token,
        requests_general_timeout=GITLAB_REQUESTS_GENERAL_TIMEOUT,
        logger_override=logger,
        response_log_dir=response_log_dir
    )

    release_details ={
        "name": release_name,
        "tag_name": tag_name,
        "description": description
    }

    release_details_pretty_json = (Box(release_details)
        .to_json(indent=2).data()
    )

    logger.info(
        f"Release details: {release_details_pretty_json}"
    )

    (Gitlab     # type: ignore
        .POST(data=release_details)
        .projects
        .project_id(project_id)
        .releases
        .exec()
    )
