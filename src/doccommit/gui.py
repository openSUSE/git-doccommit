"""
Classes and methods used for interactive mode
"""
import subprocess
import os
from dialog import Dialog
import npyscreen


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
        self.argument_files(args)


    def argument_files(self, args):
        """
        Parse argument files and paths
        """
        if args.files is not None:
            for file in args.files:
                if os.path.isfile(file):
                    self.commit_message.docrepo.stage_add_file(file)
                elif os.path.isdir(file) and not file == '.':
                    for root, dirs, files in os.walk(file):
                        for walkfile in files:
                            self.commit_message.docrepo.stage_add_file(root+walkfile)


    def select_files(self):
        """
        Dialog widget with file selection
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
            self.commit_message.docrepo.reset_repo()
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


    def enter_subject(self, error=False):
        """
        Dialog widget that asks for the subject
        """
        if error:
            subject_info_temp = "# Invalid subject!\n" + subject_info
        else:
            subject_info_temp = subject_info
        code, self.commit_message.subject = self.d.inputbox(subject_info_temp, height=15, width=56,
                                                            init=self.commit_message.subject)
        if code == 'cancel':
            self.commit_message.docrepo.reset_repo()
            quit()
        else:
            if self.commit_message.validate_subject():
                self.enter_message()
            else:
                self.enter_subject(True)


    def enter_message(self, problems=None):
        """
        Dialog widget that asks for the main message.
        This message is used for the docupdate section.
        """
        global message_info
        message_info_tmp = message_info
        if problems is not None:
            message_info_tmp = message_info_tmp + "\nFix the following problems:\n"
            for problem in problems:
                message_info_tmp = message_info_tmp + "* " + problem + "\n"
        message_info_tmp = message_info_tmp + "\n" + \
                       self.commit_message.input_message
        code, txt = self.d.editbox_str(message_info_tmp, height=30, width=78)
        if code == 'cancel':
            self.commit_message.docrepo.reset_repo()
            quit()
        else:
            self.commit_message.input_message = \
                "\n".join([line for line in txt.splitlines() if not line.startswith("#")])
            self.commit_message.problems = []
            if not self.commit_message.validate_message():
                self.enter_message(self.commit_message.problems)
            else:
                self.enter_xml_ids()


    def enter_xml_ids(self, unknown_ids=None):
        """
        Dialog widget that asks for the XML IDs
        """
        global id_info
        id_info_tmp = id_info
        if unknown_ids is not None:
            id_info_tmp = id_info_tmp + "\n\nThe following XML IDs are invalid:\n"
            for xml_id in unknown_ids:
                id_info_tmp = id_info_tmp + "* " + xml_id + "\n"
        code, self.commit_message.xml_ids = self.d.inputbox(id_info_tmp, height=20, width=78,
                                                            init=self.commit_message.xml_ids)
        if code == 'cancel':
            self.commit_message.docrepo.reset_repo()
            quit()
        self.commit_message.problems = []
        if not self.commit_message.validate_xml_ids():
            self.enter_xml_ids(self.commit_message.problems)
        self.enter_references()


    def enter_references(self, invalid_references=None):
        """
        Dialog widget that asks for the references (BSC, FATE, etc.)
        """
        global reference_info
        reference_info_tmp = reference_info
        if invalid_references is not None:
            reference_info_tmp = reference_info_tmp + "\n\nThe following references are invalid:\n"
            for reference in invalid_references:
                reference_info_tmp = reference_info_tmp + "* " + reference + "\n"
        code, self.commit_message.reference = \
            self.d.inputbox(reference_info_tmp, height=20, width=78,
                            init=self.commit_message.reference)
        if code == 'cancel':
            self.commit_message.docrepo.reset_repo()
            quit()
        self.commit_message.problems = []
        if not self.commit_message.validate_references():
            self.enter_references(self.commit_message.problems)
        self.enter_commits()


    def enter_commits(self, invalid_commits=None):
        """
        Dialog widget that asks for commit hashes for mergers in doc updates
        """
        global commit_info
        commit_info_tmp = commit_info
        if invalid_commits is not None:
            commit_info_tmp = commit_info_tmp + "\n\nThe following commit hashes are invalid:\n"
            for commit in invalid_commits:
                commit_info_tmp = commit_info_tmp + "* "+commit+"\n"
        code, self.commit_message.merge_commits = \
            self.d.inputbox(commit_info_tmp, height=15, width=78,
                            init=self.commit_message.merge_commits)
        if code == 'cancel':
            self.commit_message.docrepo.reset_repo()
            quit()
        self.commit_message.problems = []
        if self.commit_message.merge_commits and not self.commit_message.validate_merge_commits():
            self.enter_commits(self.commit_message.problems)
        self.final_check()


    def final_check(self):
        """
        Format commit message and display either in dialog or in editor
        """
        text = ""
        if not self.commit_message.format(self.editor or
                                          (not self.interactive and not self.editor)):
            text = """#
#          !!!  WARNING  !!!
#
# The following problems have been found:\n"""
            for item in self.commit_message.problems:
                text = text + "# * "+item+"\n"
            text = text + '\n'
            commit = False
        else:
            commit = True
        # If neither interactive mode nor editor is selected, use editor
        if not self.interactive or self.editor:
            with open('/tmp/.doccommit', 'w') as tmpfile:
                tmpfile.write(text + self.commit_message.final_message)
            subprocess.call(['vim', '/tmp/.doccommit'])
            self.commit_message.parse_commit_message(open('/tmp/.doccommit', 'r').read())
            self.commit_message.problems = []
            if self.commit_message.validate():
                asdf = input("Do you want to commit? [Y|n] ")
                if asdf.lower() != 'y' and asdf != '':
                    quit()
                    self.commit_message.docrepo.reset_repo()
                else:
                    self.commit_message.commit(True)
                    quit()
            else:
                asdf = input("Your input does not validate. Retry? [Y|n] ")
                if asdf.lower() == 'n':
                    self.commit_message.docrepo.reset_repo()
                    quit()
                else:
                    self.final_check()
        # if interactive mode is used
        else:
            if commit:
                title = "Final check"
                text = self.commit_message.final_message + "\n\n# ---\n# Do you want to commit?"
            else:
                title = "Linting result"
                text = text + self.commit_message.final_message + "\n\n\n# Return to beginning?"
            code = self.d.yesno(text, height=30, width=78, title=title)
            if code == "ok" and commit:
                self.commit_message.commit(True)
                quit()
            elif code == "ok" and not commit:
                self.enter_subject()
            else:
                self.commit_message.docrepo.reset_repo()
                quit()

class commitGUInpyscreen(npyscreen.NPSAppManaged):
    def __init__(self, commit_message, args): 
        self._FORM_VISIT_LIST = []
        self.NEXT_ACTIVE_FORM = self.__class__.STARTING_FORM
        self._LAST_NEXT_ACTIVE_FORM = None
        self._Forms = {}
        self.commit_message = commit_message
        self.args = args
        self.interactive = True if args.interactive is True else False
        self.editor = True if args.editor is True else False
        self.selected_files = []

    def onStart(self):
        #self.addForm("MAIN", TestForm)
        self.addForm("MAIN", SelectFiles)
        self.addForm("WRITE", WriteCommit)
        

class SelectFiles(npyscreen.Form):
    def create(self):
        self.createLists()
        files = self.add(npyscreen.TitleMultiSelect,
                    max_height =-2,
                    name="Select files for commit:",
                    value = self.selected_files,
                    values = self.all_files,
                    scroll_exit=True)
        self.edit()
        if(isinstance(files.get_selected_objects(), list)):
            self.parentApp.selected_files = files.get_selected_objects()
            #npyscreen.notify_wait(' '.join(self.parentApp.selected_files), title='Popup Title')

    def beforeEditing(self):
        self.name = "git doccommit"
        self.parentApp.setNextForm("WRITE")

    def createLists(self):
        self.all_files = []
        n = 0
        self.selected_files = []
        for filename, status in self.parentApp.commit_message.docrepo.stage():
            self.all_files.append(filename)
            if(status):
                self.selected_files.append(n)
            n = n + 1
        if not self.all_files:
            print("No changed files in repository. Exiting ...")
            self.parentApp.commit_message.docrepo.reset_repo()
            quit()

class WriteCommit(npyscreen.Form):
    def create(self):
        self.add_widget(npyscreen.Pager, value="Blabbergast", max_height=5)
        usrn_box = self.add_widget(npyscreen.TitleText, name="Subject:", color="STANDOUT")
        internet = self.add_widget(npyscreen.TitleText, name="XML ID:")
        reference = self.add_widget(npyscreen.TitleText, name="Reference:")
        commits = self.add_widget(npyscreen.TitleText, name="Commits:")
        self.add_widget(npyscreen.TitleFixedText, name="Message", editable=False)
        message = self.add_widget(npyscreen.MultiLineEdit, name="Message", value="# Enter message here\n")
        self.edit()       
        quit() 

    def beforeEditing(self):
        self.name = "git doccommit"
        self.parentApp.setNextForm(None)

class TestForm(npyscreen.Form):
    def create(self):
        npyscreen.notify_wait('TestForm', title='Popup Title')

    def afterEditing(self):
        #self.parentApp.setNextForm('SELECTFILES')
        self.parentApp.setNextForm(None)
        #quit()