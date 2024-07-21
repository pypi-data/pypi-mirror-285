import argparse
import os
import sys

from imxdparser import ChildParser

from . import duplicate


def main(main_parser, _parser_error):
    project_badge = ChildParser(main_parser, "project-badge")
    project_badge.attach()

    duplicate.main(project_badge)
