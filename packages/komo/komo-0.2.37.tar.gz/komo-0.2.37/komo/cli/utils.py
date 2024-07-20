import os
import subprocess
import json
import sys

import click
import pkg_resources
import requests

from datetime import datetime, timedelta
from packaging import version
from komo import printing
from komo.types import ClientException


def handle_errors(fn):
    def inner(*args, **kwargs):
        try:
            fn(*args, **kwargs)
        except ClientException as e:
            printing.error(e.msg)
            exit(1)

    return inner


PACKAGE_NAME = "komo"
UPDATE_CHECK_FILE = os.path.expanduser("~/.komo/.package_update_check.json")
CHECK_INTERVAL_DAYS = 2


def _get_latest_version(package_name: str) -> str:
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
        response.raise_for_status()
        data = response.json()
        return data["info"]["version"]
    except requests.RequestException as e:
        return None


def _get_installed_version(package_name: str) -> str:
    try:
        return pkg_resources.get_distribution(package_name).version
    except pkg_resources.DistributionNotFound:
        return None


def _should_check_for_update() -> bool:
    if os.environ.get("__KOMODO_INTERNAL_AGENT__", None) == "1":
        return False
    if not os.path.exists(UPDATE_CHECK_FILE):
        return True

    with open(UPDATE_CHECK_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return True
        last_check = datetime.fromisoformat(data.get("last_check"))
        if datetime.now() - last_check > timedelta(days=CHECK_INTERVAL_DAYS):
            return True
    return False


def _update_check_time():
    if not os.path.exists(os.path.dirname(UPDATE_CHECK_FILE)):
        os.makedirs(os.path.dirname(UPDATE_CHECK_FILE))
    with open(UPDATE_CHECK_FILE, "w") as f:
        json.dump({"last_check": datetime.now().isoformat()}, f)


def prompt_update(noconfirm: bool = False):
    if noconfirm or _should_check_for_update():
        installed_version = _get_installed_version(PACKAGE_NAME)
        latest_version = _get_latest_version(PACKAGE_NAME)

        if not installed_version or not latest_version:
            return

        installed_ver = version.parse(installed_version)
        latest_ver = version.parse(latest_version)

        if installed_ver < latest_ver:
            printing.warning(
                f"A new version of {PACKAGE_NAME} is available: {latest_version} (you have {installed_version})."
            )
            if noconfirm or click.confirm("Do you want to update?"):
                try:
                    subprocess.check_call(
                        [
                            sys.executable,
                            "-m",
                            "pip",
                            "install",
                            "--upgrade",
                            PACKAGE_NAME,
                        ]
                    )
                    printing.success(
                        f"{PACKAGE_NAME} has been updated to version {latest_version}."
                    )
                except subprocess.CalledProcessError as e:
                    printing.error(f"Error during update: {e}")
            else:
                printing.info("Update skipped.")
        else:
            if noconfirm:
                printing.success(
                    f"You are using the latest version of {PACKAGE_NAME} ({installed_version})."
                )

        _update_check_time()


def _get_path_size_and_file_count(path):
    total_size = 0
    file_count = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
                file_count += 1
    return total_size, file_count


def _bytes_to_gigabytes(bytes_size):
    gigabytes = bytes_size / (1024**3)
    return round(gigabytes, 2)


def _bytes_to_megabytes(bytes_size):
    megabytes = bytes_size / (1024**2)
    return round(megabytes, 2)
