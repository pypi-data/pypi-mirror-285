import os
import time
from pathlib import Path
from xml.etree import ElementTree

import requests

from ts_cli.util.emit import emit_warning


def get_latest_version():
    try:
        r = requests.get("https://pypi.org/rss/project/ts-cli/releases.xml", timeout=5)
        root = ElementTree.fromstring(r.content)
        return root.findall("channel/item/title")[0].text
    except:
        return "0.0.0"


def check_update_required(current_version) -> None:
    try:
        latest_version_path = Path(
            os.path.join(Path.home(), ".config/tetrascience/ts-cli-latest.txt")
        )

        # refresh saved latest version once per day
        if (
            latest_version_path.is_file()
            and time.time() - latest_version_path.stat().st_mtime < 24 * 3600
        ):
            latest_version = latest_version_path.read_text()
        else:
            latest_version = get_latest_version()
            latest_version_path.write_text(latest_version)

        if latest_version and check_versions_for_update(
            current_version, latest_version
        ):
            emit_warning(
                f"\nPlease upgrade ts-cli (local: {current_version}, latest: {latest_version})"
            )
            emit_warning("Use: pip3 install ts-cli --upgrade\n")

    except Exception:
        return


def check_versions_for_update(current: str, latest: str):
    current_major, current_minor, *_rest = current.split(".")
    latest_major, latest_minor, *_rest = latest.split(".")
    if int(current_major) < int(latest_major):
        return True
    if (int(current_major) == int(latest_major)) and (
        int(current_minor) < int(latest_minor)
    ):
        return True
    return False
