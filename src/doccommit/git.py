"""
Helper functions that make the interaction with DocBook XML repositories easer.
This is taylored towards SUSE-style repositories, usually made for daps.
They contain DC files, as well as a "xml" folder with single DocBook-XML files.
"""

import threading
from doccommit import xml
from queue import Queue

class CommitMessage():
    def __init__(self):
        self.reference = ""
        self.reference_types = []
        self.reference_ids = []
        self.subject = ""
        self.xml_ids = []
        self.merge_commits = ""
        self.input_message = ""
        self.final_message = ""
        self.xml_source_ids = {}
        self.get_xml_ids = threading.Thread(target=xml.get_source_xml_ids, args=(self.xml_source_ids, ))
        self.get_xml_ids.start()


    def parse_args(self, args):
        """
        Store arg vars in class properties
        """
        self.reference = args.reference
        self.subject = args.subject
        self.xml_ids = args.xml_ids
        self.merge_commits = args.merge_commits
        self.input_message = args.message


    def validate_reference(self, no_add=True):
        """
        Validate reference. Must contain a keyword like bsc, fate and a number.
        """
        valid_references = ['bsc', 'boo', 'fate']
        for single_reference in self.reference.split(','):
            [ref_type, ref_id] = single_reference.split('#')
            if type.lower() not in valid_references:
                return "Unknown reference type."
            try:
                ref_id = int(ref_id)
            except ValueError:
                return "ID is not a number."
            if not no_add:
                self.reference_types.append(ref_type)
                self.reference_ids.append(ref_id)

        return True


    def validate(self):
        """
        Validates if the user input is good enough for a commit.
        1) subject (first line) not more than 50 characters
        2) detailed block 72 characters per line
        3) subject must contain one of the following keywords at the beginning:
        Add, Remove, Change, Typo, Structure
        """
        if len(self.subject) > 50:
            return "Subject longer than 50 characters."

        keywords = ['Add', 'Remove', 'Change', 'Typo', 'Structure']
        if not any(keyword in 'some one long two phrase three' for keyword in keywords):
            return "No keyword found in subject."

        for line in self.input_message.splitlines():
            if len(line) > 72:
                return "Message line longer than 72 characters."

        if not self.validate_reference(self.reference):
            return "No valid reference to Bugtracker."

        return True


    def format(self):
        """
        Create a formatted commit message.
        """
        if not self.validate():
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
        pass


    def require_xml_source_ids(self):
        self.get_xml_ids.join()
        print(self.xml_source_ids)


def get_diff(file):
    """
    Get the diff for an file.
    """
    pass


def get_stage():
    """
    Return a dict of unstaged and staged files
    {'staged': ['file1'], 'unstaged': [file2]}
    """
    pass


def get_log(n=20, from_hash="", to_hash=""):
    """
    Get the last 20 commits, or alternatively from from_hash to to_hash.
    """
    pass