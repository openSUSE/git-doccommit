"""
Helper functions that make the interaction with DocBook XML repositories easer.
This is taylored towards SUSE-style repositories, usually made for daps.
They contain DC files, as well as a "xml" folder with single DocBook-XML files.
"""

import os
import threading
import pygit2
from doccommit import xml
from doccommit.gui import id_info, reference_info, subject_info, message_info, commit_info

class CommitMessage():
    def __init__(self, docrepo, args=None, commit_text=None):
        self.final_message = ""
        self.docrepo = docrepo
        self.problems = []
        if args is not None:
            self.reference = args.reference if args.reference is not None else ""
            self.subject = args.subject if args.subject is not None else ""
            self.xml_ids = args.xml_ids if args.xml_ids is not None else ""
            self.merge_commits = args.merge_commits if args.merge_commits is not None else ""
            self.input_message = args.message if args.message is not None else ""
        elif commit_text is not None:
            self.parse_commit_message(commit_text)


        # Make sure to call self.require_xml_source_ids() before using the
        # xml_source_ids dict.
        self.xml_source_ids = {}
        self.get_xml_ids = threading.Thread(target=xml.get_source_xml_ids,
                                            args=(self.xml_source_ids, ))
        self.get_xml_ids.start()


    def parse_commit_message(self, text):
        """
        Parse subject, commit message, XML IDs, merge commits and references
        from git commit text or editor.
        """
        subject_parsed = False
        message_parsed = False
        xml_ids_parsed = False
        references_parsed = False
        merge_commits_parsed = False
        doccommit = False
        fallback = 0
        self.input_message = ""
        for line in text.splitlines():
            fallback = fallback + 1
            if line.startswith('#') or line == "" or line.startswith('~~'):
                continue
            if not subject_parsed:
                self.subject = line.strip()
                subject_parsed = True
            elif not line.startswith("References: ") and not message_parsed:
                self.input_message = self.input_message + line.strip()
            elif line.startswith("References: ") and not references_parsed:
                message_parsed = True
                self.reference = line.replace("References:","").strip()
                references_parsed = True
            elif line.startswith("XML IDs: ") and not xml_ids_parsed:
                self.xml_ids = line.replace("XML IDs:","").strip()
                xml_ids_parsed = True
            elif line.startswith("Update Merge: ") and not merge_commits_parsed:
                self.merge_commits = line.replace("Update Merge:","").strip()
                merge_commits_parsed = True
            elif line.startswith("~~ created by git-doccommit version"):
                doccommit = True
            if all([subject_parsed, message_parsed, xml_ids_parsed, references_parsed,
                    merge_commits_parsed, doccommit]):
                quit()
                return True
            elif fallback > 100:
                quit()
                return False

    def validate_references(self):
        """
        Validate the references string
        """
        no_problem = True
        if '#' not in self.reference and self.reference != 'MINOR':
            self.problems.append("Reference does not contain a number (#) sign.")
            return False
        if self.reference == 'MINOR':
            return True
        for single_reference in string_to_list(self.reference):
            if not self.validate_reference(single_reference):
                no_problem = False
        return no_problem


    def validate_reference(self, single_reference):
        """
        Validate if a reference is formatted as SOURCE#ID
        """
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
        return no_problem


    def validate_merge_commits(self):
        """
        Validate merge commit hashes
        """
        no_problem = True
        if self.merge_commits == "" or self.merge_commits is None:
            return True
        for commit in string_to_list(self.merge_commits):
            if not self.docrepo.commit_exists(commit):
                self.problems.append(commit + " is not a valid commit ID.")
                no_problem = False
        return no_problem


    def validate_xml_ids(self, remove_keyword=False):
        """
        Test if entered XML IDs exist in XML source
        """
        if not self.xml_ids:
            self.problems.append("No XML IDs entered.")
            return False
        if remove_keyword:
            return True
        no_problem = True
        self.require_xml_source_ids()
        for xml_id in string_to_list(self.xml_ids):
            if xml_id not in self.xml_source_ids:
                no_problem = False
                self.problems.append(xml_id + " does not exist.")
        return no_problem


    def validate_subject(self):
        """
        Validate subject
        """
        no_problem = True
        if len(self.subject) > 50:
            self.problems.append("Subject longer than 50 characters.")
            no_problem = False
        keywords = ['Add', 'Remove', 'Change']
        if not any(keyword in self.subject for keyword in keywords):
            self.problems.append("No keyword found in subject.")
            no_problem = False
        return no_problem


    def validate_message(self):
        """
        Validate main text
        """
        no_problem = True
        if len(self.input_message) < len(self.subject):
            self.problems.append("Subject is longer than description text.")
            no_problem = False
        for line in self.input_message.splitlines():
            if len(line) > 72:
                self.problems.append("Message line longer than 72 characters.")
                no_problem = False
        return no_problem

    def validate(self):
        """
        Validates if the user input is good enough for a commit.
        """
        self.problems = []
        self.validate_subject()
        self.validate_message()
        self.validate_references()
        self.validate_xml_ids()
        self.validate_merge_commits()
        return bool(not self.problems)


    def format(self, comments=False):
        """
        Create a formatted commit message.
        """
        result = ""
        no_problem = True
        if not self.validate():
            no_problem = False
        if comments:
            result = result + subject_info + "\n"
        result = result + self.subject + "\n\n"
        if comments:
            result = result + message_info
        result = result + self.input_message + "\n\n"
        if comments:
            result = result + reference_info + "\n"
        result = result + "References: " + self.reference + "\n"
        if comments:
            result = result + "\n" + id_info + "\n"
        result = result + "XML IDs: " + self.xml_ids + "\n"
        if comments:
            result = result + "\n" + commit_info + "\n"
        if comments or (self.merge_commits is not None and self.merge_commits != ""):
            result = result + "DocUpdate Merge: " + self.merge_commits

        result = result + "\n~~ created by git-doccommit version 0.3.0"
        self.final_message = result
        return no_problem


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
        result = []
        for item in csv.split(','):
            result.append(item.strip())
        return result
    else:
        return [csv.strip()]
