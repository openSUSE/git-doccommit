"""
Helper functions that make the interaction with DocBook XML repositories easer.
This is taylored towards SUSE-style repositories, usually made for daps.
They contain DC files, as well as a "xml" folder with single DocBook-XML files.
"""

import threading
from doccommit import xml
import textwrap
import pygit2
import subprocess
import os

class CommitMessage():
    def __init__(self, docrepo):
        self.reference = ""
        self.reference_types = []
        self.reference_ids = []
        self.subject = ""
        self.xml_ids = []
        self.merge_commits = ""
        self.input_message = ""
        self.final_message = ""
        self.docrepo = docrepo

        # Make sure to call self.require_xml_source_ids() before using the
        # xml_source_ids dict.
        self.xml_source_ids = {}
        self.get_xml_ids = threading.Thread(target=xml.get_source_xml_ids,
                                            args=(self.xml_source_ids, ))
        self.get_xml_ids.start()


    def parse_args(self, args):
        """
        Store arg vars in class properties
        """
        self.reference = args.reference if args.reference is not None else ""
        self.subject = args.subject if args.subject is not None else ""
        self.xml_ids = args.xml_ids if args.xml_ids is not None else ""
        self.merge_commits = args.merge_commits if args.merge_commits is not None else ""
        self.input_message = args.message if args.message is not None else ""


    def validate_reference(self, no_add=True):
        """
        Validate reference. Must contain a keyword like bsc, fate and a number.
        """
        valid_references = ['bsc', 'bnc', 'boo', 'fate', 'doccomment', 'gh', 'trello']
        # gh ?
        # trello ? often private
        # open tracker bug for all sources that are not covered
        if '#' not in self.reference:
            return "Reference does not contain a number (#) sign."
        for single_reference in self.reference.split(','):
            [ref_type, ref_id] = single_reference.split('#')
            if type.lower() not in valid_references:
                return "Unknown reference type."
            try:
                ref_id = int(ref_id)
            except ValueError:
                return "Reference ID is not a number."
            if not no_add:
                self.reference_types.append(ref_type)
                self.reference_ids.append(ref_id)

        return "success"


    def validate(self):
        """
        Validates if the user input is good enough for a commit.
        """
        problems = []
        if len(self.subject) > 50:
            problems.append("Subject longer than 50 characters.")

        keywords = ['Add', 'Remove', 'Change']
        if not any(keyword in 'some one long two phrase three' for keyword in keywords):
            problems.append("No keyword found in subject.")

        if len(self.input_message) < len(self.subject):
            problems.append("Subject is longer than description text.")

        for line in self.input_message.splitlines():
            if len(line) > 72:
                problems.append("Message line longer than 72 characters.")

        validate_reference = self.validate_reference()
        if "success" not in validate_reference:
            problems.append(validate_reference)

        if problems:
            return problems
        else:
            return ["success"]


    def format(self, show_messages=True):
        """
        Create a formatted commit message.
        """
        validation = self.validate()
        if "success" not in validation:
            if show_messages:
                print("Your commit message does not yet meet the requirements:")
                for item in validation:
                    print("- "+item)
            return False

        result = self.subject + "\n\n" + self.input_message + "\n\n" + "XML IDs: "
        more = False
        for xml_id in self.xml_ids:
            result = result + (", " if more else "") + "" + xml_id
            more = True

        result = result + "\n\n" + "DocUpdate Merge: "

        more = False
        for merge_commit in self.merge_commits:
            result = result + (", " if more else "") + merge_commit
            more = True

        result = result + "~~ created by git-doccommit version 0.1.1"
        self.final_message = result


    def commit(self, update=False):
        """
        Commit a message or write update to git notes if update=COMMITHASH is set.
        """

        if self.format():
            print("committing...")
        else:
            return False


    def require_xml_source_ids(self):
        """
        This function makes sure that the thread that is supposed to deliver the XML IDs
        has finished it's work.
        """
        self.get_xml_ids.join()


class DocRepo():
    def __init__(self, path):
        self.repo = pygit2.Repository(path)


    def diff(self, cached=True):
        return str(self.repo.diff(cached=cached).patch)

    def stage(self):
        """
        Returns staged files as tuple (string filename, boolean staged)
        """
        for filename, code in self.repo.status().items():
            print(filename, code)
            if code == 2:
                yield (filename, True)
            elif code == 128 or code == 256:
                yield (filename, False)


    def commit(self, message):
        pass

    def log(max=20, from_hash=None, to_hash=None):
        pass


def find_root(path=os.getcwd()):
    """
    Find the root directory of the git repository.
    """
    try:
        path = pygit2.discover_repository(os.getcwd())
    except KeyError:
        return None
    else:
        return path


def get_log(n=20, from_hash="", to_hash=""):
    """
    Get the last 20 commits, or alternatively from from_hash to to_hash.
    """
    pass