from dialog import Dialog

def commitGUI(commit_message):
    d = Dialog(dialog="dialog")
    d.set_background_title("Git commit for SUSE documentation")

    code, tags = d.checklist("Select the files that should be committed.",
                             choices=[(filename, "", status) for filename, status in commit_message.docrepo.stage()],
                             title="Select the files that should be committed.")


    d.scrollbox(commit_message.docrepo.diff(True), height=30, width=78,title="Diff of staged files")

    subject_info = """Insert subject. Use
 * keyword: Add, Remove or Change
 * maximum of 50 characters (length of input line)

The subject does not appear in doc update sections."""

    code, commit_message.subject = d.inputbox(subject_info, height=11, width=56,
                                              init=commit_message.subject)

    if code == 'cancel':
        quit()

    message_info = """What has changed and why? Be verbose. Do not
use more than 72 characters per line.abs

Use ## to automatically insert a list of all references and @@ for a
list of XML IDs. Single IDs can be inserted with a @ sign, for
example @sec.example.id
    
This text will be used for the doc update section. Enter text below
this line.
------------------------------------------------------------------------
"""

    code, txt = d.editbox_str(message_info+commit_message.input_message,
                                                      height=30, width=78)

    commit_message.input_message = txt.split('------------------------------------------------------------------------')[1]

    print(commit_message.input_message)
