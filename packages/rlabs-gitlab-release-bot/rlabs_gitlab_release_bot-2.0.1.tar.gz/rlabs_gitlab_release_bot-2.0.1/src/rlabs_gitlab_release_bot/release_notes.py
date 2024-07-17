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
    Release Notes
'''
import logging
from pathlib import Path
import json

from rlabs_gitlab_release_bot.error import FailedToLoadReleaseNotesError
from rlabs_gitlab_release_bot.error import InvalidReleaseNotesError
from rlabs_gitlab_release_bot.types import ReleaseNotes

PLACEHOLDER_NEXT_VERSION_KEY = "__next_version__"

def load(
    path: Path,
    logger: logging.Logger
) -> ReleaseNotes:
    '''
        Load release notes from a JSON file

        Sample Release notes file:

        {
            "PLACEHOLDER_NEXT_VERSION_KEY" : {
                "issues_addressed": [
                    {
                        "issue": "1",
                        "web_link": "https://...",
                        "description": "This is a description..."
                    },
                    ...
                ],
                "additional_notes": [
                    "notes"
                    ...
                ]
            },
            ...
            "0.0.2" : {
                ...
            },
            "0.0.1" : {
                ...
            }

        }

        from the file above will select and return the single entry under
        "__next_version__"

        Returns the release notes as a dictionary

        Raises:
            FailedToLoadReleaseNotesError: If the file cannot be loaded
            InvalidReleaseNotesError: If the file is not a valid JSON file
            InvalidReleaseNotesError: If the file does not contain the PLACEHOLDER_NEXT_VERSION_KEY key
    '''
    logger.info(f"Loading release notes from {path}")

    try:
        path.read_text()
    except FileNotFoundError as e:
        raise FailedToLoadReleaseNotesError(e) from e

    try:
        parsed_notes = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        raise InvalidReleaseNotesError(
            path.read_text(),
            str(e)
        ) from e

    try:
        next_release_notes = parsed_notes[PLACEHOLDER_NEXT_VERSION_KEY]
    except KeyError as e:
        raise InvalidReleaseNotesError(
            parsed_notes,
            f"'{PLACEHOLDER_NEXT_VERSION_KEY}' key not found"
        ) from e

    return next_release_notes
