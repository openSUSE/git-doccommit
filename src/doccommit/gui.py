"""
Classes and methods used for interactive mode
"""
import subprocess
from dialog import Dialog


subject_info = """# Insert subject. Use
# * keyword: Add, Remove or Change
# * maximum of 50 characters (length of input line)
#
# The subject does not appear in doc update
# sections."""

message_info = """# What has changed and why? Be verbose. Do not
# use more than 72 characters per line.abs
#
# Use ## to automatically insert a list of all references and @@ for a
# list of XML IDs. Single IDs can be inserted with a @ sign, for
# example @sec.example.id
#
# This text will be used for the doc update section. Enter text below
# the line."""

id_info = """# Enter a comma separated list of section or chapter XML IDs
# that were changed."""

reference_info = """# Enter a comma separated list of issues (references), for example
# BSC#12435 or FATE#12345. If this is a minor update that does not belong
# into the doc update section, enter the word MINOR."""

commit_info = """# Optional, enter a commit hash if this change is directly related to
# another commit. The commits will be merged in the doc update section."""


class commitGUI():
    """
    Class that steps through a dialog and asks the user for the required input.
    The input will be validated immediatly.
    """
    def __init__(self, commit_message, args):
        self.commit_message = commit_message
        self.d = Dialog(dialog="dialog")
        self.d.set_background_title("Git commit for SUSE documentation")
        self.interactive = True if args.interactive is True else False
        self.editor = True if args.editor is True else False


    def select_files(self):
        """
        Stage and unstage files
        """
        all_files = []
        for filename, status in self.commit_message.docrepo.stage():
            all_files.append(filename)
        if not all_files:
            print("No changed files in repository. Exiting ...")
            self.commit_message.docrepo.reset_repo()
            quit()
        code, filenames = self.d.checklist("Select files",
                                      choices=[(filename, "", status) for filename,
                                               status in self.commit_message.docrepo.stage()],
                                      title="Select the files that should be committed.")
        if code == "cancel":
            self.commit_message.docrepo.reset_repo()
            quit()
        else:
            self.commit_message.docrepo.stage_remove()
            got_file = False
            for filename in filenames:
                self.commit_message.docrepo.stage_add_file(filename)
                got_file = True
            if got_file:
                self.show_diff()
            else:
                print("No files selected.")
                quit()


    def show_diff(self):
        """
        Show the diff of staged files
        """
        self.d.scrollbox(self.commit_message.docrepo.diff(True), height=30, width=78, \
                         title="Diff of staged files")
        self.enter_subject()


    def enter_subject(self):
        code, self.commit_message.subject = self.d.inputbox(subject_info, height=15, width=56,
                                                            init=self.commit_message.subject)
        if code == 'cancel':
            self.commit_message.docrepo.reset_repo()
            quit()
        else:
            if self.commit_message.validate_subject():
                self.enter_message()
            else:
                self.enter_subject()


    def enter_message(self, problems=None):
        global message_info
        if problems is not None:
            message_info = message_info + "\nFix the following problems:\n"
            for problem in problems:
                message_info = message_info + "* " + problem + "\n"
        message_info = message_info + "\n" + \
                       self.commit_message.input_message
        code, txt = self.d.editbox_str(message_info, height=30, width=78)
        if code == 'cancel':
            self.commit_message.docrepo.reset_repo()
            quit()
        else:
            self.commit_message.input_message = "\n".join([line for line in txt.splitlines() if not line.startswith("#") ])
            self.commit_message.problems = []
            if not self.commit_message.validate_message():
                self.enter_message(self.commit_message.problems)
            else:
                self.enter_xml_ids()


    def enter_xml_ids(self, unknown_ids=None):
        global id_info
        if unknown_ids is not None:
            id_info = id_info + "\n\nThe following XML IDs are invalid:\n"
            for xml_id in unknown_ids:
                id_info = id_info + "* " + xml_id + "\n"
        code, self.commit_message.xml_ids = self.d.inputbox(id_info, height=20, width=78,
                                                            init=self.commit_message.xml_ids)
        if code == 'cancel':
            self.commit_message.docrepo.reset_repo()
            quit()
        self.commit_message.problems = []
        if not self.commit_message.validate_xml_ids():
            self.enter_xml_ids(self.commit_message.problems)
        self.enter_references()


    def enter_references(self, invalid_references=None):
        global reference_info
        if invalid_references is not None:
            reference_info = reference_info + "\n\nThe following references are invalid:\n"
            for reference in invalid_references:
                reference_info = reference_info + "* "+reference+"\n"
        code, self.commit_message.reference = self.d.inputbox(reference_info, height=20, width=78,
                                                              init=self.commit_message.reference)
        if code == 'cancel':
            quit()
        self.commit_message.problems = []
        if not self.commit_message.validate_references():
            self.enter_references(self.commit_message.problems)
        self.enter_commits()


    def enter_commits(self, invalid_commits=None):
        global commit_info
        if invalid_commits is not None:
            commit_info = commit_info + "\n\nThe following commit hashes are invalid:\n"
            for commit in invalid_commits:
                commit_info = commit_info + "* "+commit+"\n"
        code, self.commit_message.merge_commits = self.d.inputbox(commit_info, height=15, width=78,
                                                                  init=self.commit_message.merge_commits)
        if code == 'cancel':
            quit()
        self.commit_message.problems = []
        if self.commit_message.merge_commits and not self.commit_message.validate_merge_commits():
            self.enter_commits(self.commit_message.problems)
        self.final_check()


    def final_check(self):
        """
        Format commit message and display
        """
        text = ""
        if not self.commit_message.format(self.editor):
            text = "# The following problems have been found:\n"
            for item in self.commit_message.problems:
                text = text + "# * "+item+"\n"
            text = text + '\n'
            commit = False
        else:
            commit = True
        if self.editor:
            with open('/tmp/.doccommit', 'w') as f:
                f.write(text + self.commit_message.final_message)
            subprocess.call(['vim', '/tmp/.doccommit'])
            self.commit_message.parse_commit_message(open('/tmp/.doccommit', 'r').read())
            self.commit_message.problems = []
            if self.commit_message.validate():
                asdf = input("Do you want to commit? [Y|n]")
                if asdf.lower() != 'y' and asdf != '':
                    quit()
                    self.commit_message.docrepo.reset_repo()
                else:
                    self.commit_message.commit()
                    quit()
            else:
                asdf = input("Your input does not validate. Retry? [Y|n]")
                if asdf.lower() == 'n':
                    self.commit_message.docrepo.reset_repo()
                    quit()
                else:
                    self.final_check()
        else:
            if commit:
                title = "Final check"
                text = self.commit_message.final_message + "\n\n# ---\n# Continue?"
            else:
                title = "Linting result"
                text = text + self.commit_message.final_message + "\n\n\n# Return to beginning?"
            code = self.d.yesno(text, height=30, width=78, title=title)
            if code == "ok" and commit:
                print("Committing (interactive)")
                self.commit_message.commit()
                quit()
            elif code == "ok" and not commit:
                self.enter_subject()
            else:
                self.commit_message.docrepo.reset_repo()
                quit()
