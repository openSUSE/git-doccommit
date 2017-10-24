from dialog import Dialog

class commitGUI():
    def __init__(self, commit_message):
        self.commit_message = commit_message
        self.d = Dialog(dialog="dialog")
        self.d.set_background_title("Git commit for SUSE documentation")
        self.select_files()


    def select_files(self):
        code, tags = self.d.checklist("Select files",
                                choices=[(filename, "", status) for filename, status in self.commit_message.docrepo.stage()],
                                title="Select the files that should be committed.")
        if code == "cancel":
            quit()
        else:
            self.show_diff()


    def show_diff(self):
        self.d.scrollbox(self.commit_message.docrepo.diff(True), height=30, width=78,title="Diff of staged files")
        subject_info = """Insert subject. Use
 * keyword: Add, Remove or Change
 * maximum of 50 characters (length of input line)

The subject does not appear in doc update sections."""
        code, self.commit_message.subject = self.d.inputbox(subject_info, height=11, width=56,
                                              init=self.commit_message.subject)
        if code == 'cancel':
            quit()
        else:
            self.enter_message()


    def enter_message(self):
        message_info = """What has changed and why? Be verbose. Do not
use more than 72 characters per line.abs

Use ## to automatically insert a list of all references and @@ for a
list of XML IDs. Single IDs can be inserted with a @ sign, for
example @sec.example.id
    
This text will be used for the doc update section. Enter text below
the line.
------------------------------------------------------------------------
"""
        code, txt = self.d.editbox_str(message_info+self.commit_message.input_message,
                                                      height=30, width=78)
        self.commit_message.input_message = txt.split('------------------------------------------------------------------------')[1]
        if code == 'cancel':
            quit()
        else:
            self.enter_xml_ids()


    def enter_xml_ids(self, unknown_ids=None):
        id_info = """Enter a comma separated list of section or chapter XML IDs that were changed."""
        if unknown_ids is not None:
            id_info = id_info + "\n\nThe following XML IDs are invalid:\n"
            for id in unknown_ids:
                id_info = id_info + "* "+id+"\n"
        code, self.commit_message.xml_ids = self.d.inputbox(id_info, height=20, width=78,
                                              init=self.commit_message.xml_ids)
        if code == 'cancel':
            quit()
        else:
            self.commit_message.require_xml_source_ids()
            invalid_ids = []
            for id in self.commit_message.xml_ids.split(","):
                if id.strip() not in self.commit_message.xml_source_ids:
                    invalid_ids.append(id.strip())
            if invalid_ids and "Remove" not in self.commit_message.subject:
                self.enter_xml_ids(invalid_ids)
            else:
                self.enter_references()


    def enter_references(self, invalid_references=None):
        reference_info = """Enter a comma separated list of issues (references), for example
BSC#12435 or FATE#12345"""
        if invalid_references is not None:
            reference_info = reference_info + "\n\nThe following references are invalid:\n"
            for reference in invalid_references:
                reference_info = reference_info + "* "+reference+"\n"
        code, self.commit_message.reference = self.d.inputbox(reference_info, height=20, width=78,
                                                              init=self.commit_message.reference)
        result = self.commit_message.validate_references()
        if not result == "success":
            self.enter_references(result)
        self.enter_commits()


    def enter_commits(self, invalid_commits=None):
        commit_info = """Optional, enter a commit hash if this change is directly related to
another commit. The commits will be merged in the doc update section."""
        if invalid_commits is not None:
            commit_info = commit_info + "\n\nThe following commit hashes are invalid:\n"
            for commit in invalid_commits:
                commit_info = commit_info + "* "+commit+"\n"
        code, self.commit_message.merge_commits = self.d.inputbox(commit_info, height=10, width=78,
                                                                  init=self.commit_message.merge_commits)
        result = self.commit_message.validate_merge_commits()
        if not result == "success":
            self.enter_commits(result)
        self.final_check()


    def final_check(self):
        """
        Format commit message and display
        """
        validation = self.commit_message.format()
        if "success" not in validation:
            title = "Linting result"
            text = "The following problems have been found:\n\n"
            for item in validation:
                text = text+ "* "+item+"\n"
            text = text + self.commit_message.final_message + "\n\n\nReturn to beginning?"
            commit = False
        else:
            title = "Final check"
            text = self.commit_message.final_message + "\n\n\nContinue?"
            commit = True
        code = self.d.yesno(text, height=30, width=78, title=title)
        print(code)
        if code == "ok" and commit:
            print("committing!")
        elif code == "ok" and not commit:
            self.enter_message()
        else:
            quit()