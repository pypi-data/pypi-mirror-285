import sys

from gitlab import Gitlab
from gitlab.exceptions import GitlabListError


def connect(cfg):
    try:
        host = cfg.get("gitlab", {}).get("host")
        apikey = cfg.get("gitlab", {}).get("apikey")
        gitlab = Gitlab(host, private_token=apikey)
        gitlab.auth()
    except Exception as err:
        sys.exit(f"error: failed to connect to gitlab: {err}")
    return gitlab


def is_admin(gitlab):
    # The user api doesn't return an admin or not status,
    # so try a admin only api
    try:
        gitlab.runners_all.list(iterator=True)
        return True
    except GitlabListError:
        return False
