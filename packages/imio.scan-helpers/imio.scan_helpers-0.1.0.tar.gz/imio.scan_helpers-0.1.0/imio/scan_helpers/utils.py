# -*- coding: utf-8 -*-
#
# This file is part of the imio.scan_helpers distribution (https://github.com/IMIO/imio.scan_helpers).
# Copyright (c) 2023 IMIO
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
from config import DOWNLOAD_DIR
from config import get_bundle_dir
from config import GITHUB_REPO
from config import IS_PROD
from config import logger
from config import MAIN_EXE_NAME

import os
import requests
import subprocess
import sys
import zipfile


def copy_files(src_dir, dest_dir):
    """Will create a bat to copy files aftermain process has ended and restart the main process without upgrade"""
    exe_path = os.path.join(dest_dir, f"{MAIN_EXE_NAME}.exe")
    script_path = os.path.join(dest_dir, 'copy_files.bat')

    with open(script_path, 'w') as script:
        script.write(f'@echo off\n')
        script.write(f'echo Copying "{src_dir}" files to "{dest_dir}""\n')
        script.write(f'timeout /t 3\n')  # waits for main script to end
        script.write(f'xcopy /s /e /h /r /y /q "{src_dir}\\*" "{dest_dir}"\n')
        script.write(f'start "" "{exe_path}" -nu\n')
        script.write(f'rmdir /s /q "{src_dir}"\n')
        # script.write(f'del "{script_path}"\n')

    if IS_PROD:
        subprocess.Popen(['cmd', '/c', script_path])


def download_update(url, download_path):
    """Download github zip file"""
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(download_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)


def get_download_dir_path():
    # maybe use tempdir
    # temp_dir = tempfile.gettempdir()
    return os.path.join(get_bundle_dir(), DOWNLOAD_DIR)


def get_latest_release_version(release=None):
    """Get GitHub latest or specified release info"""
    if release:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases"
        ret = json_request(url)
        for dic in ret:
            if dic["tag_name"] == release:
                url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/{dic['id']}"
                break
        else:
            stop(f"The release with tag '{release}' cannot be found")
    else:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    latest_release = json_request(url)
    return latest_release["tag_name"], latest_release["assets"][0]["browser_download_url"]


def json_request(url):
    """Simple json request"""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def stop(msg="", intup=True):
    if msg:
        logger.warn(msg)
    if intup:
        input("Press Enter to exit...")
    sys.exit(0)


def unzip_file(zip_path, extract_to):
    """Unzip downloaded archive and delete it"""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    os.remove(zip_path)
