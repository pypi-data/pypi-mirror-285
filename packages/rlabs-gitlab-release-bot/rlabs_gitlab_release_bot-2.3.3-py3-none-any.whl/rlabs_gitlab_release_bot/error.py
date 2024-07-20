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
    error.py
'''
import json

class PrettyError(Exception):
    '''
        Custom Base Error

        This is the base class for all custom errors.

        Pretty Logs error to stdout and exits with -1
    '''
    pass

class NoVersionBump(PrettyError):
    '''
        Custom NoVersionBump Error
    '''
    pass

class TagFormatError(PrettyError):
    '''
        Custom TagFormat Error
    '''
    pass

class InvalidBumpPrefixes(PrettyError):
    '''
        Custom InvalidBumpPrefixes Error
    '''
    pass

class VersionInFileUpdateRegexNotMatchedError(PrettyError):
    '''
        Custom VersionNotFound Error
    '''
    def __init__(self, file_path, regex):
        super().__init__(
            f"Failed to find version to replace in file '{file_path}'. "
            f" Regex '{regex}' has no matches."
        )

class VersionInFileUpdateError(PrettyError):
    '''
        Custom VersionUpdateInFileError Error
    '''
    def __init__(self, file_path, reason):
        super().__init__(
            f"Failed to update version in file '{file_path}'. Reason: {reason} "
        )

class CommitFileError(PrettyError):
    '''
        Custom CommitFileError Error
    '''
    def __init__(self, file, reason):
        super().__init__(
            f"Failed to commit file {file}. Reason: {reason}"
        )

class LikelyTagAlreadyExistsError(PrettyError):
    '''
        Custom LikelyTagAlreadyExistsError Error
    '''
    def __init__(self, tag_name, project_id):
        super().__init__(
            f"The Gitlab API returned 400. Could be a few things, BUT MOST LIKELY "
            f"the tag '{tag_name}' already exists for project '{project_id}'.\n\n"
            "Was the version bumped prior to running 'commit and tag'?"
        )

class FailedToLoadBotError(PrettyError):
    '''
        Custom FailedToLoadBotError Error
    '''
    def __init__(self, reason):
        super().__init__(
            f"Failed to load Bot. Reason: {reason}"
        )

class FailedToExportBotError(PrettyError):
    '''
        Custom FailedToExportBotError Error
    '''
    def __init__(self, reason):
        super().__init__(
            f"Failed to export Bot. Reason: {reason}. "
            "Does the path to the file exist?"
        )

class InvalidLoadedBotError(PrettyError):
    '''
        Custom InvalidLoadedBotError Error
    '''
    def __init__(self, loaded_bot: dict, reason: str):
        super().__init__(
            f"Invalid loaded bot file. Reason: {reason}. "
            f"Loaded bot: \n{json.dumps(loaded_bot, indent=2)}."
        )
class FailedToLoadReleaseNotesError(PrettyError):
    '''
        Custom FailedToLoadReleaseNotesError Error
    '''
    def __init__(self, reason):
        super().__init__(
            f"Failed to load release notes. Reason: {reason}"
        )

class InvalidReleaseNotesError(PrettyError):
    '''
        Custom InvalidReleaseNotesError Error
    '''
    def __init__(self, release_notes: str, reason: str):
        super().__init__(
            f"Invalid release notes. Reason: {reason}. "
            f"Release notes: \n{json.dumps(release_notes, indent=2)}."
        )

class FailedToUpdateVersionInFileError(PrettyError):
    '''
        Custom FailedToUpdateVersionInFileError Error
    '''
    def __init__(self, file_path, reason):
        super().__init__(
            f"Failed to update version in file '{file_path}'. Reason: {reason} "
        )

class FailedToUpdateReleaseNotesFileError(PrettyError):
    '''
        Custom FailedToUpdateReleaseNotesFileError Error
    '''
    def __init__(self, file_path, reason):
        super().__init__(
            f"Failed to update release notes file '{file_path}'. Reason: {reason} "
        )
