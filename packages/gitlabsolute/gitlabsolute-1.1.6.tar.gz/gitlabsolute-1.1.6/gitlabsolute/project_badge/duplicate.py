"""
duplicate
---------

Takes all the badges from one project and replaces all the badges of another project with those from first project.

.. program:: gitlabsolute project-badge duplicate

.. option:: -c CFGFILE, --cfgfile CFGFILE

   Configuration file to use.

.. option:: project-badge

   Module positional argument.

.. option:: duplicate

   Action positional argument.

.. option:: src

   Source project to copy badges from

.. option:: dst

   Destination project to copy badges to

.. option:: --delete

   Delete badges on destination before copy (default)

Examples
--------

.. code-block:: bash

    # With path
    gitlabsolute project-badge duplicate group/project1 group/project2

    # With id
    gitlabsolute project-badge duplicate 123 789

"""

import argparse
import sys

from imxdparser import ChildParser

from ..gitlab import connect


def main(parent_parser):
    parser = ChildParser(
        parent_parser,
        "duplicate",
        description="Duplicate all badges from one project to another.",
    )
    parser.add_argument("src", help="Source project to copy badges from")
    parser.add_argument("dst", help="Destination project to copy badges to")

    parser.add_argument(
        "--delete",
        default=True,
        help="Delete badges on destination before copy (default)",
        action="store_true",
        dest="delete",
    )
    parser.add_argument(
        "--no-delete",
        help=argparse.SUPPRESS,
        action="store_false",
        dest="delete",
    )
    parser.attach()
    parser.set_defaults(func=action)


def action(cfg, args):
    gitlab = connect(cfg)
    src = args["src"]
    dst = args["dst"]

    src_prj = gitlab.projects.get(src)
    dst_prj = gitlab.projects.get(dst)

    if args["delete"]:
        print(f'Deleting project badges from "{dst_prj.web_url}"...', file=sys.stderr)
        for badge in dst_prj.badges.list(iterator=True):
            if badge.kind == "group":
                continue
            dst_prj.badges.delete(id=badge.id)

    print(f'Copying project badges from "{src_prj.web_url}" to "{dst_prj.web_url}"...', file=sys.stderr)
    for badge in src_prj.badges.list(iterator=True):
        if badge.kind == "group":
            continue
        dst_prj.badges.create(badge.asdict())
    print(f'Copied project badges from "{src_prj.web_url}" to "{dst_prj.web_url}".', file=sys.stderr)
