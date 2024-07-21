import argparse
import os
import sys

from imxdparser import ChildParser

from . import delete
from . import list as list_


def main(main_parser, _parser_error):
    project_badge = ChildParser(main_parser, "pipeline")
    project_badge.attach()

    list_.main(project_badge)
    delete.main(project_badge)
