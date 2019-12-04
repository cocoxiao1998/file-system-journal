import os
from Tkinter import * # Module for GUI

select = "" #Global variable to be used for both GUI and main

'''
Class to run the GUI that will take the user's selection from
the displayed journal and create another text file based on
the user's selection
'''
class JournalGui:
    def __init__(self, master):
        # function to get the selected item from GUI
        def create():
            global select
            select = journal.curselection()
            master.destroy()
        '''
        Initializes the window in class
        and give name and size to the window
        '''
        self.master = master
        master.title(journalName)
        master.geometry("500x300")

        # creates a frame
        pane = Frame(master)
        pane.pack()

        # Initializes scrollbars for right and bottom of the frame
        scrollbary = Scrollbar(pane)
        scrollbarx = Scrollbar(pane, orient = HORIZONTAL)

        # A listbox that will display the journal content
        journal = Listbox(pane, yscrollcommand = scrollbary.set,
                            xscrollcommand = scrollbarx.set,
                            width = 60, height = 15)
        for j in range (0, linesLen):
            journal.insert(j, lines[j])
        journal.pack(side = LEFT)

        # Configures and packs the scrollbar to the right place
        scrollbary.config(command = journal.yview)
        scrollbarx.config(command = journal.xview)
        scrollbary.pack(side = RIGHT, fill = Y)
        scrollbarx.pack(side = BOTTOM, fill = X)

        # Button widget to confirm the user's selection
        button = Button(master, text = "Create", command = create)
        button.pack(side = BOTTOM)

'''
process_lineNum function gets the line number the changes
were made and returns the line number without the left
parenthese
'''
def process_lineNum(ln):
    num = ln
    startL = num.find("(")
    numS = num[startL +1:]
    return numS

'''
process_changes function gets the changes that were made
and returns only the content
'''
def process_changes(ch):
    change = ch

    if (change == "\'')"):
        changeS = change[:-1]
    else:
        startC = change.find("\'")
        changeS = change[startC + 1: -2]
    return changeS

'''
process_creation function either adds or deletes the processed
changes to a list
'''
def process_creation(pln, m, pch):
    # convert processed line number to an int
    pln_int = int(pln)
    pln_int -= 1

    try:
        # add the changes to list
        if (m == '+'):
            if (pch == "\''"):
                linesA[pln_int] = None
            else:
                linesA[pln_int] = pch
        # when m == '-' change index list to none
        else:
            linesA[pln_int] = None
    except IndexError:
        # inserts the change to the list when index out of range
        if (pch == "\''"):
            linesA.insert(pln_int, None)
        else:
            linesA.insert(pln_int, pch)


if __name__ == "__main__":
    # user input file name to be read
    journalName = raw_input("Enter journal filename: ")
    ext = journalName.find('-journal.txt')

    # directory paths with "/" in order to concatenate with filenames
    home = os.path.expanduser("~")
    watched_dir = ("%s/watched_dir/" % home)
    watched_dir_hidden = ("%s/.watched_dir_hidden/" % home)

    # check to see if file exist
    # and makes sure the file extension is '-journal.txt'
    while (os.path.exists(watched_dir_hidden + journalName)
            == False or ext == -1):
        print(journalName, " invalid journal name")
        journalName = raw_input("Enter journal filename: ")
        ext = journalName.find('-journal.txt')

    # user input file name to be read
    # and new file to be written to
    jFile = open(watched_dir_hidden + journalName, 'r')
    newTxt = raw_input("Enter name for new text file: ")
    nFile = open(watched_dir + newTxt, 'a+')

    # get the joural's lines and initialize two lists
    lines = jFile.read().splitlines()
    linesLen = len(lines)
    linesA = []
    linesB = []

    # Run JournalGui
    root = Tk()
    JournalGui(root)
    root.mainloop()

    #The column number to get the line number, + or -, and changes made
    lineNum = 0
    mod = 1
    changes = 2
    # Gets the time column of original journal
    time = 6

    try:
        # From the line number user selected
        # add the entries to list linesB
        selectCh = select[0] + 1
        for x in range(selectCh):
            linesB.append(lines[x])

        # get the time from last entry from linesB
        selectedTime = linesB[-1].split()[time]

        '''
        go through the rest of the journal
        to find entries that match the time from
        linesB. Add the times that matches to linesB
        and break when they don't
        '''
        for y in range(selectCh, linesLen):
            timeCol = lines[y].split()[time]
            if (timeCol == selectedTime):
                linesB.append(lines[y])
            else:
                break

        linesBLen = len(linesB) # get length of linesB

        # Process the changes made and add to list linesA
        for x in range(linesBLen):
            startChange = linesB[x].find("(")
            newChange = linesB[x][startChange:]

            if (newChange == "(CREATED)" or newChange == "(~)"):
                continue
            else:
                ln = newChange.split()[lineNum]
                pln = process_lineNum(ln)

            m = newChange.split()[mod]

            startCh = newChange.find("\'")
            if (startCh != -1):
                ch = newChange[startCh:]
                pch = process_changes(ch)
            else:
                pch = ")"

            process_creation(pln, m, pch)

        # writes to new text file from list linesA
        for i in range(0, len(linesA)):
            if (linesA[i] == None):
                nFile.write("\n")
            else:
                nFile.write(linesA[i] + "\n")

        jFile.close()
        nFile.close()
        print("New file creation complete!")
    except:
        print("Selection was not made")
