"""
list
----

List all runners that correspond to selection query.

.. program:: gitlabsolute runner list

.. option:: -c CFGFILE, --cfgfile CFGFILE

   Configuration file to use.

.. option:: runner

   Module positional argument.

.. option:: list

   Action positional argument.

.. option:: query

   Selection query to filter in runners

.. option:: -x, --extend

   Fetch additional data for query

Examples
--------

.. code-block:: bash

    # List all runners
    gitlabsolute runner list true

    # List all offline runners
    gitlabsolute runner list "online == false"

"""

from imxdparser import ChildParser

from .delete import action as common_action


def main(parent_parser):
    parser = ChildParser(
        parent_parser,
        "list",
        description="List all runners corresponding to selection query.",
    )
    parser.add_argument("query", help="Selection query")
    parser.add_argument("-x", "--extend", help="Use and get extended information", action="store_true", default=False)
    parser.attach()
    parser.set_defaults(func=action)


def action(cfg, args):
    args["dry_run"] = True
    common_action(cfg, args)
