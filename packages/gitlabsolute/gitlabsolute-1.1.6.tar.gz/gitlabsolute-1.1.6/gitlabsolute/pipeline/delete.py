"""
delete
------

Delete all pipelines that correspond to selection query.

.. program:: gitlabsolute pipeline delete

.. option:: -c CFGFILE, --cfgfile CFGFILE

   Configuration file to use.

.. option:: pipeline

   Module positional argument.

.. option:: delete

   Action positional argument.

.. option:: project

   Project id

.. option:: query

   Selection query to filter in pipelines

Examples
--------

.. code-block:: bash

    # Delete all runners
    gitlabsolute pipeline delete 123 true

    # Delete all failed pipelines
    gitlabsolute pipeline delete 123 "status == 'failed'"

"""

import json

from imxdparser import ChildParser

from ..gitlab import connect
from ..lexer import evaluate, lex2python


def main(parent_parser):
    parser = ChildParser(
        parent_parser,
        "delete",
        description="Delete pipelines corresponding to selection query.",
    )
    parser.add_argument("project", help="Project id")
    parser.add_argument("query", help="Selection query")
    parser.add_argument("--dry-run", default=False, help="Do not delete pipeline", action="store_true", dest="dry_run")
    parser.attach()
    parser.set_defaults(func=action)


def action(cfg, args, *_, gitlab=None):
    if not gitlab:
        gitlab = connect(cfg)
    query = args["query"]
    dry_run = args["dry_run"]

    expression = lex2python(query)
    pipelines = []

    project = gitlab.projects.get(args["project"])

    pipelines = []
    for pipeline in project.pipelines.list(iterator=True, all=True):
        item = pipeline
        pipeline = pipeline.asdict()
        expr = evaluate(expression, pipeline)
        if expr:
            pipelines += [pipeline]
            if not dry_run:
                item.delete()
    print(json.dumps(pipelines))
