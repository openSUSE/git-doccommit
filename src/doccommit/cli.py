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
from doccommit import gui

parser = argparse.ArgumentParser(description='Command description.')
parser = argparse.ArgumentParser(description="""This git subcommand helps to create well
formatted git commits. They can be used to automatically create doc update sections for for SUSE
documentation.""")

subparsers = parser.add_subparsers(help='sub-command --help')

parser_a = subparsers.add_parser('commit', help='commit --help')
parser_a.add_argument('-i', '--interactive', action='store_true', help='Start in interactive mode')
parser_a.add_argument('-m', metavar='message', dest='message', type=str, help='Commit message')
parser_a.add_argument('-s', metavar='subject', dest='subject', type=str, help='Commit subject')
parser_a.add_argument('-l', metavar='XML IDs', dest='xml_ids', type=str, help='List of affected XML IDs')
parser_a.add_argument('-r', metavar='BSC/FATE/etc', dest='reference', type=str, help='Reference Bug or FATE entry')
parser_a.add_argument('-c', metavar='Commit hashes', dest='merge_commits', type=str, help='Reference Bug or FATE entry')
parser_a.set_defaults(command='commit')

parser_b = subparsers.add_parser('docupdate', help='docupdate --help')
parser_b.add_argument('--file', type=str, help='Path to the XML file containing the doc update section')
parser_b.set_defaults(command='docupdate')


def main(args=None):
    args = parser.parse_args(args=args)
    print(args)
    if args.command == "commit":
        commitMessage = git.CommitMessage()
        if args.interactive:
            commitGUI = gui.CommitGUI(commitMessage)
        else:
            print("")
        print("blaaaaaa")
        commitMessage.require_xml_source_ids()
        commitMessage.require_xml_source_ids()
        commitMessage.require_xml_source_ids()
        commitMessage.require_xml_source_ids()
        print("do something")
