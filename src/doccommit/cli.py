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
    parser = argparse.ArgumentParser(description="""This git subcommand helps to create well
    formatted git commits. They can be used to automatically create doc update sections for for SUSE
    documentation.""")

    parser.add_argument('files', metavar='files', type=str, nargs='*', help='files for the commit')
    parser.add_argument('-i', '--interactive', action='store_true', help='Start in interactive mode')
    parser.add_argument('-m', metavar='message', dest='message', type=str, help='Commit message')
    parser.add_argument('-s', metavar='subject', dest='subject', type=str, help='Commit subject')
    parser.add_argument('-x', metavar='XML IDs', dest='xml_ids', type=str, help='Comma separated list of affected XML IDs')
    parser.add_argument('-r', metavar='BSC/FATE/etc', dest='reference', type=str, help='Comma separated list of Bugzilla or FATE entries, e.g. FATE#12435 or BSC#12435')
    parser.add_argument('-c', metavar='Commit hashes', dest='merge_commits', type=str, help='Merge hashes in doc updates into one item')
    parser.add_argument('-u', metavar='Commit hash', dest='update_commit', type=str, help='Update existing commit message (uses git notes)')
    parser.add_argument('-a', '--auto-wrap', dest='update_commit', action='store_true', help='Automatic line wrap for message text')
    parser.add_argument('-e', '--editor', action='store_true', help='Final check is performed in the default editor')
    parser.set_defaults(command='commit')

    return parser.parse_args(args=args)

def parse_cli_docupdate(args=None):
    """
    Parse command line arguments with argparse
    """
    parser = argparse.ArgumentParser(description="""This git subcommand helps to create well
    formatted git commits. They can be used to automatically create doc update sections for for SUSE
    documentation.""")

    parser.add_argument('--file', type=str, help='Path to the XML file containing the doc update section')
    return parser.parse_args(args=args)


def doccommit(args=None):
    args = parse_cli_commit(args)
    if not len(sys.argv) > 1:
        print("Nothing to do. Use --help")
        quit()

    path = git.find_root(os.getcwd())
    docrepo = git.DocRepo(path)
    commit_message = git.CommitMessage(docrepo, args)
    my_gui = gui.commitGUI(commit_message, args)
    if args.interactive:
        my_gui.select_files()
    else:
        my_gui.final_check()
    commit_message.commit()

def docupdate(args=None):
    args = parse_cli_docupdate(args)
    if not len(sys.argv) > 1:
        print("Nothing to do. Use --help")
        quit()