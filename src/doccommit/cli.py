"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mdoccommit` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``doccommit.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``doccommit.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import argparse
from doccommit import git

parser = argparse.ArgumentParser(description='Command description.')
parser = argparse.ArgumentParser(description="""This git subcommand helps to create well
formatted git commits. They can be used to automatically create doc update sections for for SUSE
documentation.""")

subparsers = parser.add_subparsers(help='sub-command help')

parser_a = subparsers.add_parser('commit', help='commit help')
parser_a.add_argument('-i', '--interactive', action='store_true', help='Start in interactive mode')
parser_a.add_argument('-m', type=str, help='Commit message')
parser_a.add_argument('-s', type=str, help='Commit subject')
parser_a.add_argument('-l', type=str, help='List of affected XML IDs')

parser_b = subparsers.add_parser('docupdate', help='docupdate help')
parser_b.add_argument('--file', type=str, help='Path to the XML file containing the doc update section')


def main(args=None):
    args = parser.parse_args(args=args)
    print(args)
