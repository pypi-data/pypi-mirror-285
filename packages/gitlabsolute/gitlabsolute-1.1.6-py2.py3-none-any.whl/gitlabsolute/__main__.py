#!/usr/bin/env python3

import sys

import yaml
from imxdparser import MainParser
from torxtools import argtools, cfgtools, pathtools

from . import pipeline, project_badge, runner


def parser_error(parser, argv, *_args):
    argv += [""]
    parser.parse_args(argv)


def configure(cfgfile):
    with open(cfgfile, encoding="UTF-8") as fd:
        data = yaml.safe_load(fd)
    return data


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    cfgname = "gitlabsolute.yml"
    search_paths = cfgtools.candidates(cfgname)

    main_parser = MainParser(
        prog="gitlabsolute",
        description="Lorem ipsum sit dolor amet",
        argument_default=None,
    )
    main_parser.add_argument(
        "-c",
        "--cfgfile",
        metavar="CFGFILE",
        default=None,
        help=f"Configuration file to use. Otherwise first file found in search path is used. (default search path: {search_paths})",
        type=argtools.is_not_dir,
    )

    def error(*_args):
        parser_error(main_parser, argv)

    main_parser.attach()
    main_parser.set_defaults(func=error)

    # Enable initial positional arguments here
    pipeline.main(main_parser, error)
    project_badge.main(main_parser, error)
    runner.main(main_parser, error)

    args = vars(main_parser.parse_args(argv))
    cfg = configure(cfgtools.which(args["cfgfile"], pathtools.expandpath(search_paths)))

    args["func"](cfg, args)


if __name__ == "__main__":
    main()
