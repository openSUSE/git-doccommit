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
        self.xml_ids = ""
        self.merge_commits = ""
        self.input_message = ""
        self.final_message = ""
        self.docrepo = docrepo
        self.problems = []

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


    def validate_references(self, add=False):
        """
        Validate the references string
        """
        no_problem = True
        if '#' not in self.reference:
            self.problems.append("Reference does not contain a number (#) sign.")
            return False
        for single_reference in string_to_list(self.reference):
            if not self.validate_reference(single_reference, add):
                no_problem = False
        return no_problem


    def validate_reference(self, single_reference, add):
        valid_references = ['bsc', 'bnc', 'boo', 'fate', 'doccomment', 'gh', 'trello']
        # gh ?
        # trello ? often private
        # open tracker bug for all sources that are not covered
        no_problem = True
        [ref_type, ref_id] = single_reference.split('#')
        if ref_type.lower() not in valid_references:
            self.problems.append(single_reference+": Unknown reference type.")
            no_problem = False
        try:
            ref_id = int(ref_id)
        except ValueError:
            self.problems.append(single_reference+": Reference ID is not a number.")
            no_problem = False
        if add:
            self.reference_types.append(ref_type)
            self.reference_ids.append(ref_id)
        return no_problem


    def validate_merge_commits(self):
        """
        Validate merge commit hashes
        """
        no_problem = True
        for commit in string_to_list(self.merge_commits):
            if not self.docrepo.commit_exists(commit):
                self.problems.append(commit + " is not a valid commit ID.")
                no_problem = False
        return no_problem


    def validate_xml_ids(self, remove_keyword=False):
        if not self.xml_ids:
            self.problems.append("No XML IDs entered.")
            return False
        if remove_keyword:
            return True
        self.require_xml_source_ids()
        for xml_id in string_to_list(self.xml_ids):
            if xml_id not in self.xml_source_ids:
                self.problems.append(xml_id + " does not exist.")


    def validate(self):
        """
        Validates if the user input is good enough for a commit.
        """
        self.problems = []
        if len(self.subject) > 50:
            self.problems.append("Subject longer than 50 characters.")

        keywords = ['Add', 'Remove', 'Change']
        if not any(keyword in self.subject for keyword in keywords):
            self.problems.append("No keyword found in subject.")

        if len(self.input_message) < len(self.subject):
            self.problems.append("Subject is longer than description text.")

        for line in self.input_message.splitlines():
            if len(line) > 72:
                self.problems.append("Message line longer than 72 characters.")

        validate_reference = self.validate_references(True)
        if "success" not in validate_reference:
            self.problems.append(validate_reference)

        self.validate_xml_ids()

        return bool(self.problems)


    def format(self, show_messages=True):
        """
        Create a formatted commit message.
        """
        if not self.validate():
            return False

        result = self.subject + "\n" + self.input_message + "\n" + "XML IDs: "
        result = result + self.xml_ids
        if self.merge_commits != "":
            result = result + "\n\nDocUpdate Merge: " + self.merge_commits 

        result = result + "\n~~ created by git-doccommit version 0.2.1"
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


    def log(self, max=20, from_hash=None, to_hash=None):
        pass


    def commit_exists(self, commit_hash):
        try:
            if self.repo.get(commit_hash.strip()):
                return True
            else:
                return False
        except ValueError:
            return False

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

def string_to_list(csv):
    """
    Turns a csv input string into a list
    """
    if ',' in csv:
        return csv.split(',').strip()
    else:
        return [csv.strip()]