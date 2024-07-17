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
    Validate
'''
from rlabs_gitlab_release_bot.error import InvalidLoadedBotError

def loaded_bot(bot_json: dict) -> None:
    '''
        Validate the loaded bot json

        This function will raise an InvalidLoadedBotError if the
        bot json is invalid

        TODO:
            Use a schema validator instead of this. This is ridiculuos
            but IT's late and I'm tired I don't want to do it now
    '''
    try:
        bot_json["gitlab_project_id"]
    except KeyError as e:
        raise InvalidLoadedBotError(bot_json, "missing key 'gitlab_project_id'") from e

    try:
        bot_json["branch"]
    except KeyError as e:
        raise InvalidLoadedBotError(bot_json, "missing key 'branch'") from e

    try:
        bot_json["bump_prefixes"]
    except KeyError as e:
        raise InvalidLoadedBotError(bot_json, "missing key 'bump_prefixes'") from e

    try:
        bot_json["log_level"]
    except KeyError as e:
        raise InvalidLoadedBotError(bot_json, "missing key 'log_level'") from e

    try:
        bot_json["response_log_dir"]
    except KeyError as e:
        raise InvalidLoadedBotError(bot_json, "missing key 'response_log_dir'") from e

    try:
        bot_json["next_version_and_changelog"]
    except KeyError as e:
        raise InvalidLoadedBotError(bot_json, "missing key 'next_version_and_changelog'") from e

    try:
        bot_json["next_version_and_changelog"]["version"]
    except KeyError as e:
        raise InvalidLoadedBotError(bot_json, "missing key 'next_version_and_changelog.version'") from e

    try:
        bot_json["next_version_and_changelog"]["version"]["current"]
    except KeyError as e:
        raise InvalidLoadedBotError(bot_json, "missing key 'next_version_and_changelog.version.current'") from e

    try:
        bot_json["next_version_and_changelog"]["version"]["bumped"]
    except KeyError as e:
        raise InvalidLoadedBotError(bot_json, "missing key 'next_version_and_changelog.version.bumped'") from e

    try:
        bot_json["next_version_and_changelog"]["changelog"]
    except KeyError as e:
        raise InvalidLoadedBotError(bot_json, "missing key 'next_version_and_changelog.changelog'") from e
