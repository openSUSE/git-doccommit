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
import sys
import os
from doccommit import git
from doccommit import gui


def parse_cli_commit(args=None):
    """
    Parse command line arguments with argparse
    """
    parser = argparse.ArgumentParser(description='Command description.')
    parser = argparse.ArgumentParser(description="""This git subcommand helps to create well
    formatted git commits. They can be used to automatically create doc update sections for for SUSE
    documentation.""")

    subparsers = parser.add_subparsers(help='sub-command --help')

    parser_a = subparsers.add_parser('commit', help='commit --help')
    parser_a.add_argument('-i', '--interactive', action='store_true', help='Start in interactive mode')
    parser_a.add_argument('-m', metavar='message', dest='message', type=str, help='Commit message')
    parser_a.add_argument('-s', metavar='subject', dest='subject', type=str, help='Commit subject')
    parser_a.add_argument('-x', metavar='XML IDs', dest='xml_ids', type=str, help='Comma separated list of affected XML IDs')
    parser_a.add_argument('-r', metavar='BSC/FATE/etc', dest='reference', type=str, help='Comma separated list of Bugzilla or FATE entries, e.g. FATE#12435 or BSC#12435')
    parser_a.add_argument('-c', metavar='Commit hashes', dest='merge_commits', type=str, help='Merge hashes in doc updates into one item')
    parser_a.add_argument('-u', metavar='Commit hash', dest='update_commit', type=str, help='Update existing commit message (uses git notes)')
    parser_a.add_argument('-a', '--auto-wrap', dest='update_commit', action='store_true', help='Automatic line wrap for message text')
    parser_a.set_defaults(command='commit')

    parser_b = subparsers.add_parser('docupdate', help='docupdate --help')
    parser_b.add_argument('--file', type=str, help='Path to the XML file containing the doc update section')
    parser_b.set_defaults(command='docupdate')
    return parser.parse_args(args=args)

def parse_cli_docupdate(args=None):
    """
    Parse command line arguments with argparse
    """
    parser = argparse.ArgumentParser(description='Command description.')
    parser = argparse.ArgumentParser(description="""This git subcommand helps to create well
    formatted git commits. They can be used to automatically create doc update sections for for SUSE
    documentation.""")

    subparsers = parser.add_subparsers(help='sub-command --help')

    parser_a = subparsers.add_parser('commit', help='commit --help')
    parser_a.add_argument('-i', '--interactive', action='store_true', help='Start in interactive mode')
    parser_a.add_argument('-m', metavar='message', dest='message', type=str, help='Commit message')
    parser_a.add_argument('-s', metavar='subject', dest='subject', type=str, help='Commit subject')
    parser_a.add_argument('-x', metavar='XML IDs', dest='xml_ids', type=str, help='Comma separated list of affected XML IDs')
    parser_a.add_argument('-r', metavar='BSC/FATE/etc', dest='reference', type=str, help='Comma separated list of Bugzilla or FATE entries, e.g. FATE#12435 or BSC#12435')
    parser_a.add_argument('-c', metavar='Commit hashes', dest='merge_commits', type=str, help='Merge hashes in doc updates into one item')
    parser_a.add_argument('-u', metavar='Commit hash', dest='update_commit', type=str, help='Update existing commit message (uses git notes)')
    parser_a.add_argument('-a', '--auto-wrap', dest='update_commit', action='store_true', help='Automatic line wrap for message text')
    parser_a.set_defaults(command='commit')

    parser_b = subparsers.add_parser('docupdate', help='docupdate --help')
    parser_b.add_argument('--file', type=str, help='Path to the XML file containing the doc update section')
    parser_b.set_defaults(command='docupdate')
    return parser.parse_args(args=args)


def main(args=None):
    args = parse_cli_commit(args)
    if not len(sys.argv) > 1:
        print("Nothing to do. Use --help")
        quit()

    path = git.find_root(os.getcwd())
    docrepo = git.DocRepo(path)
    if args.command == "commit":
        commit_message = git.CommitMessage(docrepo)
        commit_message.parse_args(args)
        my_gui = gui.commitGUI(commit_message)
        if args.interactive:
            my_gui.select_files()
        else:
            my_gui.final_check()
        commit_message.commit()

    elif args.command == "docupdate":
        pass
