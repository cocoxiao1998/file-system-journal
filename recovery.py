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
    elif (change == ")"):
        changeS = change
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
        '''
        if the index of the list contains something, add or
        delete a particular change to that index
        '''
        line = linesA[pln_int]
        if (line != ''):
            if (m == '+'):
                add = pch
                newLine = line + pch
                linesA.pop(pln_int)
                linesA.insert(pln_int, newLine)
            else:
                linesA.pop(pln_int)
        else:
            linesA.insert(pln_int, pch)
    except IndexError:
        # inserts the change to the list
        if (pch == "\''"):
            linesA.insert(pln_int, "")
        else:
            linesA.insert(pln_int, pch)


if __name__ == "__main__":
    # user input file name to be read and new file to be written to
    journalName = raw_input("Enter journal filename: ")
    jFile = open("/home/coco/.watched_dir_hidden/" + journalName, 'r')
    newTxt = raw_input("Enter name for new text file: ")
    nFile = open("/home/coco/watched_dir/" + newTxt, 'a+')

    # get the journal's lines and initialize a list
    lines = jFile.read().splitlines()
    linesLen = len(lines)
    linesA = []

    # Run JournalGui
    root = Tk()
    JournalGui(root)
    root.mainloop()

    #The column number to get the line number, + or -, and changes made
    lineNum = 8
    mod = 9
    changes = 10
    s = -1 # variable use to stop creating the file

    # Get the line number column and calls the 3 functions
    for x in lines:
        s += 1
        if (s <= select[0]):
            # Ignores the two strings and continue to next line
            ln = x.split()[lineNum]
            if (ln == '(CREATED)' or ln == '(~)'):
                continue
            else:
                pln = process_lineNum(ln)

            m = x.split()[mod] # gets the + or -

            # Gets the changes made by user
            ch = x.split()[changes]
            if (ch == "\'')"):
                pch = process_changes(ch)
            elif (ch == ")"):
                pch = process_changes(ch)
            # Since the file is read by delimiting space
            # Need to make sure all changes are included
            elif ("\')" not in ch):
                nString = ch
                c = changes
                while ("\')" not in ch):
                    c += 1
                    ch = x.split()[c]
                    nString = nString + ' ' + ch
                pch = process_changes(nString)
            else:
                pch = process_changes(ch)

            process_creation(pln, m, pch)
        else:
            break

    # writes to new text file
    for i in range(0, len(linesA)):
        nFile.write(linesA[i] + "\n")

    print("New file creation complete!")
