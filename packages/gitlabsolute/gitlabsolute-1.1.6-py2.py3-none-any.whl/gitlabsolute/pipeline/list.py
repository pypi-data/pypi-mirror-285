"""
list
----

List all pipelines that correspond to selection query.

.. program:: gitlabsolute pipeline list

.. option:: -c CFGFILE, --cfgfile CFGFILE

   Configuration file to use.

.. option:: pipeline

   Module positional argument.

.. option:: list

   Action positional argument.

.. option:: project

   Project id

.. option:: query

   Selection query to filter in runners

Examples
--------

.. code-block:: bash

    # List all runners
    gitlabsolute pipeline list 123 true

    # List all failed pipelines
    gitlabsolute pipeline list 123 "status == 'failed'"

"""

from imxdparser import ChildParser

from .delete import action as common_action


def main(parent_parser):
    parser = ChildParser(
        parent_parser,
        "list",
        description="List all pipelines corresponding to selection query.",
    )
    parser.add_argument("project", help="Project id")
    parser.add_argument("query", help="Selection query")
    parser.attach()
    parser.set_defaults(func=action)


def action(cfg, args):
    args["dry_run"] = True
    common_action(cfg, args)
