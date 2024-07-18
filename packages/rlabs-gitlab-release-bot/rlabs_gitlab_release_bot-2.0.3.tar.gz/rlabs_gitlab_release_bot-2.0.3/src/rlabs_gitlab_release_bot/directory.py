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
    Directory
'''
import shutil
from pathlib import Path

def remove_dir(dir: Path, recreate: bool = False):
    '''
        Remove directory. If recreate is True, create the directory
    '''
    if dir.exists():
        shutil.rmtree(dir)

    if recreate:
        dir.mkdir(
            parents=True,
            exist_ok=True
        )

def remove_file(file: Path, recreate: bool = False):
    '''
        Remove file. If recreate is True, create the file
    '''
    if file.exists():
        file.unlink()

    if recreate:
        file.touch()
