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
    Release
'''
import difflib
import logging
from typing import Optional, cast
import semver
from pathlib import Path
from datetime import datetime
import re
import json
from typing import Any
from typing import ClassVar

from rlabs_gitlab_release_bot import logger
from rlabs_gitlab_release_bot import gitlab
from rlabs_gitlab_release_bot import commit
from rlabs_gitlab_release_bot.error import NoVersionBump, TagFormatError
from rlabs_gitlab_release_bot import directory
from rlabs_gitlab_release_bot.error import VersionInFileUpdateRegexNotMatchedError
from rlabs_gitlab_release_bot.error import VersionInFileUpdateError
from rlabs_gitlab_release_bot.error import CommitFileError
from rlabs_gitlab_release_bot.error import FailedToLoadBotError
from rlabs_gitlab_release_bot.error import FailedToExportBotError
from rlabs_gitlab_release_bot.error import InvalidLoadedBotError
from rlabs_gitlab_release_bot.error import FailedToUpdateVersionInFileError
from rlabs_gitlab_release_bot.error import FailedToUpdateReleaseNotesFileError
from rlabs_gitlab_release_bot import validate
from rlabs_gitlab_release_bot import release_notes as module_release_notes
from rlabs_gitlab_release_bot.types import VersionAndChangelog, Changelog, ReleaseNotes
from rlabs_gitlab_release_bot.types import BumpedCommits, Version, IssuesAddressed, BumpPrefixes


SKIP_CI_TAG = "[skip ci]"

def craft_commit_message(
        tag_name: str,
        skip_ci_tag: str
    ) -> str:
    return f"chore: version bump for {tag_name} {skip_ci_tag}"

map_changelog_title_commit_prefix = {
    "breaking change": "Breaking Changes",
    "feat": "Added",
    "refactor": "Changed",
    "style": "Changed",
    "fix": "Fixed",
    "ci": "Continuous Integration",
    "chore": "Other",
    "perf": "Performance",
    "docs": "Documentation",
    "test": "Test",
    "build": "Build",
    "revert": "Revert"
}

class ReleaseBot:
    '''
        ReleaseBot
    '''
    INITIAL_VERSION: semver.Version = semver.Version.parse("0.0.1")
    DEFAULT_GITLAB_RESPONSE_LOG_DIR: Path = Path("./logs")

    logger_override: ClassVar[Optional[logging.Logger]] = None

    def __init__(
        self,
        gitlab_token: str,
        gitlab_project_id: int,
        branch: str,
        bump_prefixes: Optional[dict[str, list[str]]] = None,
        release_notes_path: Optional[Path] = None,
        log_level: Optional[int] = None,
        logger_override: Optional[logging.Logger] = None,
        response_log_dir: Path = DEFAULT_GITLAB_RESPONSE_LOG_DIR
    ) -> None:
        '''
            Init

            Args:
                gitlab_token: The Gitlab token.
                gitlab_project_id: The Gitlab project ID.
                branch: The branch to work on.
                bump_prefixes: The prefixes to bump the version with.
                log_level: The log level.
                logger_override: The logger to use.
                response_log_dir: The directory to store responses to from the Gitlab API.
        '''
        self.gitlab_token = gitlab_token
        self.gitlab_project_id = gitlab_project_id
        self.branch = branch
        self.bump_prefixes = bump_prefixes
        self.log_level = log_level
        self.response_log_dir = response_log_dir
        self.release_notes_path = release_notes_path

        self.next_version_and_changelog: VersionAndChangelog | None = None

        # Clean up response logs
        directory.remove_dir(
            self.response_log_dir
        )

        # Set up logging
        if log_level and logger_override:
            raise ValueError(
                "log_level and logger_override are mutually exclusive. "
                "Please provide one or the other."
            )

        if not log_level and not logger_override:
            raise ValueError(
                "log_level or logger_override must be provided."
            )

        if logger_override:
            self.logger = logger_override
        else:
            self.logger = logger.stdout(
                __name__,
                cast(
                    int,
                    log_level
                )
            )

        # make it available for use in class methods
        ReleaseBot.logger = self.logger

        logger.enable_pretty_tracebacks()

    @classmethod
    def export_bot(
            cls,
            bot: 'ReleaseBot',
            file_path: Path,
    ) -> None:
        '''
            Exports a Bot to a file
            to 'file_path' in JSON format.

            All fields initially passed to the bot are exported, except
            for logger override and gitlab token.
        '''
        to_export = {
            "gitlab_project_id": bot.gitlab_project_id,
            "branch": bot.branch,
            "bump_prefixes": bot.bump_prefixes,
            "release_notes_path": str(bot.release_notes_path),
            "log_level": bot.log_level,
            "response_log_dir": str(bot.response_log_dir),
            "next_version_and_changelog": bot.next_version_and_changelog
        }
        try:
            with file_path.open("w") as file:
                json.dump(
                    to_export,
                    file,
                    indent=2
                )
        except Exception as e:
            raise FailedToExportBotError(
                str(e)
            )

        if ReleaseBot.logger:
            ReleaseBot.logger.info(
                f"Exported Bot to '{file_path}'."
            )

    @classmethod
    def load_bot(
            cls,
            file_path: Path,
            gitlab_token: str,
            logger_override: Optional[logging.Logger] = None,
    ) -> 'ReleaseBot':
        '''
            Load Bot from file

            Loads a Bot from a file
            at 'file_path' in JSON format.

            Returns:
                The loaded bot
        '''
        try:
            with file_path.open("r") as file:
                bot_json = json.load(file)
        except Exception as e:
            raise FailedToLoadBotError(
                str(e)
            )

        if not isinstance(bot_json, dict):
            raise InvalidLoadedBotError(
                bot_json, "Bot must be a dictionary"
            )

        validate.loaded_bot(bot_json)

        bot = ReleaseBot(
            gitlab_token,
            bot_json["gitlab_project_id"],
            bot_json["branch"],
            bot_json["bump_prefixes"],
            bot_json["release_notes_path"],
            bot_json["log_level"],
            logger_override,
            Path(bot_json["response_log_dir"])
        )

        bot.next_version_and_changelog = bot_json["next_version_and_changelog"]

        ReleaseBot.logger.info(
            f"Loaded Bot from '{file_path}': \n"
            f"{json.dumps(bot_json, indent=2)}"
        )

        return bot

    def get_next_version_and_changelog(
            self
        ) -> None:
        '''
            Get Next Version and Changelog

            This:

            1. Finds the next version to bump to for the Gitlab project self.gitlab_project_id
            2. Creates the changelog for the next version based on the commits since the last tag.
                (commits are filtered by the prefixes in self.bump_prefixes, the default are
                the conventional commit prefixes)
            3, Loads Changelog Release Notes from the file at 'self.release_notes_path'

            On completion 'self.next_version_and_changelog' will be set to a dictionary
            with the current version, the bumped version, the changelog, and release notes.
        '''
        if self.release_notes_path:
            release_notes: ReleaseNotes = module_release_notes.load(
                cast(
                    Path,
                    self.release_notes_path
                ),
                self.logger
            )
        else:
            release_notes = {}

        last_tag = gitlab.last_tag(
            self.gitlab_token,
            self.gitlab_project_id,
            self.response_log_dir / "last_tag",
            self.logger
        )

        last_commit = gitlab.last_commit(
            self.gitlab_token,
            self.gitlab_project_id,
            self.branch,
            self.response_log_dir / "last_commit",
            self.logger
        )

        if not last_tag:
            self.logger.warning(
                f"No tags found. Setting version to {ReleaseBot.INITIAL_VERSION}"
            )
            curr_version: str = "no version"
            bumped_version: semver.Version = ReleaseBot.INITIAL_VERSION

        elif not last_commit:
            raise NoVersionBump(
                f"Failed to find last commit. Is the branch '{self.branch}' correct? "
            )

        elif last_tag["commit"]["short_id"] == last_commit["short_id"]:
            raise NoVersionBump(
                "No commits found since last tag. "
            )

        else:
            bumps: BumpedCommits = commit.bump_commits_messages(
                self.gitlab_token,
                self.gitlab_project_id,
                self.branch,
                last_tag,
                last_commit,
                cast(
                    BumpPrefixes,
                    self.bump_prefixes
                ),
                SKIP_CI_TAG,
                self.response_log_dir / "bump_commit_messages",
                self.logger
            )

            curr_version = last_tag["name"].replace("v", "")

            try:
                if bumps['major']:
                    bumped_version = semver.Version.parse(curr_version).bump_major()
                elif bumps['minor']:
                    bumped_version = semver.Version.parse(curr_version).bump_minor()
                elif bumps['patch']:
                    bumped_version = semver.Version.parse(curr_version).bump_patch()
                else:
                    all_prefixes = [
                        prefix
                        for category in bumps["bump_prefixes_used"].values()
                        for prefix in category
                    ]
                    raise NoVersionBump(
                        "Nothing to bump. No commits found since the last tag that follow either the conventional commit prefixes OR "
                        f"the provided ones: {all_prefixes}"
                    )
            except ValueError as err:
                raise TagFormatError(
                    f"Please use semantic versioning format for tags: "
                    "v{major}.{minor}.{patch} or {major}.{minor}.{patch}"
                ) from err

        self.next_version_and_changelog = {
            "version": {
                "current": curr_version,
                "bumped": str(bumped_version)
            },
            "changelog": self.__changelog_from_commits(
                bumps,
                release_notes
            )
        }

        next_version_and_changelog_pretty_json = json.dumps(
            self.next_version_and_changelog,
            indent=2
        )

        self.logger.info(
            "Next version and changelog: \n"
            f"{next_version_and_changelog_pretty_json}"
        )

    def __changelog_from_commits(
            self,
            bump_commits: BumpedCommits,
            release_notes: ReleaseNotes
    ) -> Changelog:
        '''
            Create a Changelog entry from Commits

            Creates a changelog entry from the commits in 'bump_commits' and the release notes.

            The changelog entry is not the actual changelog, but a dictionary with the
            changelog entries for each section.

            Args:
                bump_commits: The commits that were found to bump the version.
                release_notes: The release notes.

            Returns:
                A dictionary with the changelog entries.
        '''

        prefixes_in_commits =  [
            k for k in bump_commits['bump_prefixes_used']
        ]

        commits: list[str] = []
        for key in prefixes_in_commits:
            commits.extend(
                bump_commits.get(key, [])
            )

        changelog: Changelog = {
            "__release_notes__": {}
        }
        for commit in commits:
            prefix = commit.split(":")[0].strip().lower()

            try:
                title = map_changelog_title_commit_prefix[prefix]
            except KeyError:
                title = "Other"

            changelog.setdefault(title, []).append(commit)

        ## just append release notes
        changelog["__release_notes__"] = release_notes

        return changelog

    def update_changelog_string(
        self,
        changelog_string: str
    ) -> str:
        '''
            Update Changelog String

            Updates 'changelog_string' with the new version and changelog entries
            from self.next_version_and_changelog.

            Changelog format:

                # Changelog

                ## {date} (version {bumped_version})

                ### {section}
                - **{prefix}:** {entry}

                The update addresses the following issues:
                - [issue](weblink)
                - [issue](weblink)

                additional_notes

            TODO:
                This should be refactored to use a template engine. IDK what I was thinking
                For now it will have to suffice

            Args:
                changelog_string: The changelog content as a string.

            Returns:
                The updated changelog content as a string.
        '''
        self.logger.debug(
            "Updating changelog string"
        )

        if not self.next_version_and_changelog:
            raise ValueError(
                "next_version_and_changelog is empty. Please run 'get_next_version_and_changelog()' first."
            )

        version_info = self.next_version_and_changelog['version']
        bumped_version = version_info['bumped']
        changelog = self.next_version_and_changelog['changelog']

        # Create new changelog entries
        new_entries = f"## {datetime.now().strftime('%B %d, %Y')} (version {bumped_version})\n"
        for section, entries in changelog.items():
            if section == "__release_notes__":
                continue  # Skip the release notes for now

            section_title = f"### {section.capitalize()}\n"
            new_entries += section_title

            # Ensure entries are processed as a list
            if isinstance(entries, str):
                entries = [entries]

            for entry in entries:
                if ':' in entry:
                    prefix, rest_of_entry = entry.split(':', 1)
                    clean_rest_of_entry = rest_of_entry.replace("\n", " ").strip()
                    pretty_entry = f"**{prefix.strip()}:** {clean_rest_of_entry}\n"
                    new_entries += f"- {pretty_entry.strip()}\n"
                else:
                    new_entries += f"- {entry.strip()}\n"

            new_entries += "\n"

        # Process release notes if they exist
        release_notes = changelog.get("__release_notes__", {})
        issues_addressed = release_notes.get("issues_addressed", [])
        additional_notes = release_notes.get("additional_notes", [])

        if issues_addressed:
            new_entries += "The update addresses the following issues:\n"
            for issue in issues_addressed:
                issue_entry = f"- [{issue['issue']}]({issue['web_link']})"
                new_entries += f"{issue_entry}\n"
            new_entries += "\n"

        if additional_notes:
            new_entries += "\n".join(additional_notes) + "\n\n"

        # Remove any existing 'Changelog' header
        cleaned_changelog_string = changelog_string.strip()
        if cleaned_changelog_string.startswith("# Changelog"):
            cleaned_changelog_string = cleaned_changelog_string[len("# Changelog"):].strip()

        # Combine new entries with the existing changelog
        updated_changelog = f"# Changelog\n\n{new_entries.strip()}\n\n{cleaned_changelog_string}".replace("\n## ", "\n\n## ")

        return updated_changelog.strip()


    def update_changelog_file(
            self,
            changelog_path: Path
        ) -> None:
        '''
            Update Changelog File

            Updates the changelog file with the new version and changelog entries
            from self.next_version_and_changelog.

            Creates the file new if it does not exist.

            Args:
                changelog_path: The path to the changelog file.
        '''
        self.logger.info(
            f"Updating changelog file '{changelog_path}'"
        )

        if not self.next_version_and_changelog:
            raise ValueError(
                "next_version_and_changelog is empty. Please run 'get_next_version_and_changelog()' first."
            )

        try:
            changelog_string = changelog_path.read_text()
        except FileNotFoundError:
            changelog_string = ""

            #create the file
            changelog_path.touch()

        updated_changelog_string = self.update_changelog_string(
            changelog_string
        )

        changelog_path.write_text(
            updated_changelog_string
        )

        d = difflib.Differ()
        diff = d.compare(changelog_string.split(), updated_changelog_string.split())
        changes = [line for line in diff if line.startswith('+ ') or line.startswith('- ')]

        self.logger.info(
            "Diff after updating changelog:\n" + '\n'.join(changes)
        )

    def update_version_in_file(
            self,
            file_path: Path,
            regex: str
    ) -> None:
        '''
            Update Version in File

            Replaces the version in the file at 'file_path' with the next
            version from self.next_version_and_changelog.

            Searches for the version to replace using the regex 'regex'.

            Args:
                file_path: The path to the file.
                new_version: The new version to update to.
                regex: The regex to search for the current version to replace.
        '''
        self.logger.info(
            f"Updating version in file '{file_path}'"
        )

        if not self.next_version_and_changelog:
            raise ValueError(
                "next_version_and_changelog is empty. Please run 'get_next_version_and_changelog()' first."
            )

        try:
            file_content = file_path.read_text()
        except Exception as e:
            raise VersionInFileUpdateError(
                file_path,
                str(e)
            )

        # Search for the current version using the regex
        current_version_match = re.search(regex, file_content)

        if not current_version_match:
            raise VersionInFileUpdateRegexNotMatchedError(
                file_path,
                regex
            )

        try:
            current_version = current_version_match.group(0)

            # Replace only the version number within the matched string
            updated_content = re.sub(
                regex,
                lambda match: match.group(0).replace(
                    re.search(
                        r'\d+\.\d+\.\d+', match.group(0)).group(),
                        self.next_version_and_changelog['version']['bumped']
                ),
                file_content
            )
        except Exception as e:
            raise FailedToUpdateVersionInFileError(
                file_path,
                str(e)
            )

        # Write the updated content back to the file
        file_path.write_text(updated_content)

        d = difflib.Differ()
        diff = d.compare(file_content.split(), updated_content.split())
        changes = [line for line in diff if line.startswith('+ ') or line.startswith('- ')]

        self.logger.info(
            "Diff after updating version:\n" + '\n'.join(changes)
        )

    def replace_placeholder_next_version_in_release_notes_file(
            self,
            release_notes_path: Path
    ) -> None:
        '''
            Repalce Placeholder Version in Release Notes File

            Replaces the placeholder for the next version in the release notes file
            with the next version from self.next_version_and_changelog.

            The replacement is done in place.
        '''
        self.logger.info(
            f"Replacing version placeholder in release notes file '{self.release_notes_path}'"
        )

        if not self.next_version_and_changelog:
            raise ValueError(
                "next_version_and_changelog is empty. Please run 'get_next_version_and_changelog()' first."
            )

        try:
            contents = release_notes_path.read_text()
            updated_contents = contents.replace(
                module_release_notes.PLACEHOLDER_NEXT_VERSION_KEY,
                self.next_version_and_changelog['version']['bumped']
            )
            release_notes_path.write_text(updated_contents)
        except Exception as e:
            raise FailedToUpdateReleaseNotesFileError(
                release_notes_path,
                str(e)
            )

        d = difflib.Differ()
        diff = d.compare(contents.split(), updated_contents.split())
        changes = [line for line in diff if line.startswith('+ ') or line.startswith('- ')]

        self.logger.info(
            "Diff after placeholder replaced:\n" + '\n'.join(changes)
        )

    def commit_and_tag(
        self,
        files_to_commit: list[Path]
    ) -> None:
        '''
            Commit and Tag

            Refer to the __commit and __tag methods for more information
        '''
        commit_sha = self.__commit(
            files_to_commit
        )
        self.__tag(
            commit_sha
        )

    def create_release(
        self
    ) -> None:
        '''
            Create Release

            Creates a release in the Gitlab project. The release is tagged with the
            version 'bumped_version' and the changelog is included in the release description.
        '''
        self.logger.info(
            f"Creating release for project {self.gitlab_project_id}"
        )

        if not self.next_version_and_changelog:
            raise ValueError(
                "next_version_and_changelog is empty. Please run 'get_next_version_and_changelog()' first."
            )

        bumped_version: str = cast(
            str,
            self.next_version_and_changelog['version']['bumped']
        )

        updated_changelog_string: str = self.update_changelog_string(
            "",     # append current changelog to empty changelog
        )

        gitlab.create_release(
            self.gitlab_token,
            self.gitlab_project_id,
            release_name=f"Release {bumped_version}",
            tag_name=bumped_version,
            description=updated_changelog_string,
            response_log_dir=self.response_log_dir / "create_release",
            logger=self.logger
        )

    def __commit(
        self,
        files_to_commit: list[Path]
    ) -> str:
        '''
            Commit

            Commits the files in 'files_to_commit' to the Gitlab project.
            The commit message looks like:

                chore: version bump for {version} [skip ci]

            version is taken from self.next_version_and_changelog['version']['bumped']

            NOTE:
                For this to work the script must be run from the project root directory
                or from a subdirectory (NOT A PARENT DIRECTORY).

            Args:
                files_to_commit: The files to commit.

            Returns:
                The commit SHA (from the created commit).
        '''
        self.logger.info(
            f"Committing to project {self.gitlab_project_id} at branch '{self.branch}'. "
            f"Files: {[str(file) for file in files_to_commit]}"

        )

        if not self.next_version_and_changelog:
            raise ValueError(
                "next_version_and_changelog is empty. Please run 'get_next_version_and_changelog()' first."
            )

        # create actions
        actions: list[dict[str, str]] = []

        for file in files_to_commit:

            self.logger.debug(
                f"Creating actions for file '{file}'"
            )

            file_path_relative_to_project_root = self._get_path_relative_to_project_root(
                file
            )

            exists = gitlab.file_exists(
                self.gitlab_token,
                self.gitlab_project_id,
                self.branch,
                file_path_relative_to_project_root,
                self.response_log_dir / "file_exists",
                self.logger
            )

            action = "update" if exists else "create"

            # read file contents
            try:
                file_contents = file.read_text()
            except FileNotFoundError as e:
                raise CommitFileError(
                    file,
                    str(e)
                )

            actions.append(
                {
                    "action": action,
                    "file_path": file_path_relative_to_project_root,
                    "content": file_contents
                }
            )

        # print actions
        pretty_actions:list[dict[str, str]] = []

        for action in actions:                                  # type: ignore
            pretty_actions.append(
                {
                    "action": action["action"],                 # type: ignore
                    "file_path": action["file_path"],           # type: ignore
                    "content": action["content"][:20] + "..."   # type: ignore
                }
            )

        pretty_actions_json = json.dumps(
            pretty_actions,
            indent=2
        )

        self.logger.info(
            f"Actions: \n{pretty_actions_json}"
        )

        # commit actions
        commit_message = craft_commit_message(
            cast(
                str,
                self.next_version_and_changelog['version']['bumped']
            ),
            SKIP_CI_TAG
        )

        return gitlab.commit_actions(
            self.gitlab_token,
            self.gitlab_project_id,
            self.branch,
            commit_message,
            actions,
            self.response_log_dir / "commit_actions",
            self.logger
        )

    def __tag(
        self,
        commit_sha: str
    ) -> None:
        '''
            Tag

            Tags the commit 'commit_sha' with 'version' in the Gitlab project.

            'version' is taken from self.next_version_and_changelog['version']['bumped']

            Args:
                commit_sha: The commit SHA to tag.
        '''
        self.logger.info(
            f"Tagging project {self.gitlab_project_id} with "
            f"version '{self.next_version_and_changelog['version']['bumped']}'"
        )

        gitlab.tag(
            self.gitlab_token,
            self.gitlab_project_id,
            commit_sha,
            self.next_version_and_changelog['version']['bumped'],
            self.response_log_dir / "tag",
            self.logger
        )

    def _get_path_relative_to_project_root(
        self,
        file: Path
    ) -> str:
        '''
            Get Path Relative to Project Root

            Gets the path to the file relative to the project root by doinf the
            following:

                - remove trailing ./
                - remove trailing /
                - remove trailing ../

            NOTE:
                Works when the script is run from the project root or from a subdirectory.

                Examples:

                    path from root:
                        path/from/root
                    from exec dir:
                        ../path/from/root
                        ./path/from/root
                        ../../path/from/root
                    after strip:
                        path/from/root <<<-- WORKS

                    But it will not work for when exec directory is a PARENT directory.


            Args:
                file: The file path.

            Returns:
                The path to the file relative to the project root.
        '''

        return str(file).strip("./").strip("/").strip("../")
