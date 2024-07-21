"""
delete
------

Delete all runners that correspond to selection query.

.. program:: gitlabsolute runner delete

.. option:: -c CFGFILE, --cfgfile CFGFILE

   Configuration file to use.

.. option:: runner

   Module positional argument.

.. option:: delete

   Action positional argument.

.. option:: query

   Selection query to filter in runners

.. option:: -x, --extend

   Fetch additional data for query

Examples
--------

.. code-block:: bash

    # delete all runners (DANGER!)
    gitlabsolute runner delete true

    # delete all offline runners
    gitlabsolute runner delete "online == false"

"""

import json

from imxdparser import ChildParser

from ..gitlab import connect, is_admin
from ..lexer import evaluate, lex2python


def main(parent_parser):
    parser = ChildParser(
        parent_parser,
        "delete",
        description="Delete runners corresponding to selection query.",
    )
    parser.add_argument("query", help="Selection query")
    parser.add_argument("-x", "--extend", help="Use and get extended information", action="store_true", default=False)
    parser.add_argument("--dry-run", default=False, help="Do not delete runner", action="store_true", dest="dry_run")
    parser.attach()
    parser.set_defaults(func=action)


def action(cfg, args, *_, gitlab=None):
    if not gitlab:
        gitlab = connect(cfg)
    query = args["query"]
    dry_run = args["dry_run"]

    expression = lex2python(query)
    runners = []

    if is_admin(gitlab):
        iterator = gitlab.runners_all.list
    else:
        iterator = gitlab.runners.list

    for runner in iterator(iterator=True, all=True):
        runner = runner.asdict()
        if args["extend"]:
            runner = gitlab.runners.get(id=runner["id"])
            runner = runner.asdict()
        expr = evaluate(expression, runner)
        if expr:
            runners += [runner]
            if not dry_run:
                gitlab.runners.delete(runner["id"])
    print(json.dumps(runners))
