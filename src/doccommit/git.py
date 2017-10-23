"""
Helper functions that make the interaction with DocBook XML repositories easer.
This is taylored towards SUSE-style repositories, usually made for daps.
They contain DC files, as well as a "xml" folder with single DocBook-XML files.
"""

class CommitMessage():
    def __init__(self):
        self.reference          = ""
        self.reference_types    = []
        self.reference_ids      = []
        self.subject            = ""
        self.xml_ids            = []
        self.merge_commits      = ""
        self.message            = ""


    def validate_reference(self, no_add = True):
        """
        Validate reference. Must contain a keyword like bsc, fate and a number.
        """
        valid_references = ['bsc', 'boo', 'fate']
        for single_reference in self.reference.split(','):
            [type, id] = single_reference.split('#')
            if type.lower() not in valid_references:
                return "Unknown reference type."
            try:
                id = int(id)
            except ValueError:
                return "ID is not a number."
            if no_add == False:
                self.reference_types.append(type)
                self.reference_ids.append(id)

        return True



def validate_input(subject, message, xml_ids, merge_commits, reference):
    """
    Validates if the user input is good enough for a commit.
    1) subject (first line) not more than 50 characters
    2) detailed block 72 characters per line
    3) subject must contain one of the following keywords at the beginning:
       Add, Remove, Change, Typo, Structure
    """
    if len(subject) > 50:
        return "Subject longer than 50 characters."

    keywords = ['Add', 'Remove', 'Change', 'Typo', 'Structure']
    if not any(keyword in 'some one long two phrase three' for keyword in keywords):
        return "No keyword found in subject."

    for line in message.splitlines():
        if len(line) > 72:
            return "Message line longer than 72 characters."

    if not validate_reference(reference):
        return "No valid reference to Bugtracker."

    return True


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


def commit(message, update=""):
    """
    Commit a message or write update to git notes if update=COMMITHASH is set.
    """
    pass


def get_log(n=20, from_hash="", to_hash=""):
    """
    Get the last 20 commits, or alternatively from from_hash to to_hash.
    """
    pass


def format_message(subject, message, xml_ids, merge_commits):
    """
    Create a formatted commit message.
    """
    if False == validate_input(subject, message, xml_ids, merge_commits):
        return False

    result = subject + "\n\n" + message + "\n\n" + "XML IDs: "
    more = False
    for xml_id in xml_ids:
        result = result + (", " if more == True else "") + "" + xml_id
        more = True

    result = result + "\n\n" + "DocUpdate Merge: "

    more = False
    for merge_commit in merge_commits:
        result = result + (", " if more == True else "") + merge_commit
        more = True

    result = result + "~~ created by git-doccommit version 0.1.1"