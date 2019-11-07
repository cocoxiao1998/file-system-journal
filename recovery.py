'''
process_lineNum function gets the line number the changes 
were made and returns the line number without the left 
parenthese
'''
def process_lineNum(ln):
    num = ln
    numLen = len(num)
    startL = num.find("(")
    numS = num[startL +1:]
    return numS

'''
process_changes function gets the changes that were made 
and returns the changes without the single quotes and right
parenthese
'''
def process_changes(ch):
    change = ch
    changeLen = len(change)
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
        if (line != ""):
            if (m == '+'):
                add = pch
                newLine = line + pch
                linesA.pop(pln_int)
                linesA.insert(pln_int, newLine)
            else:
                sub = pch
                newLine = line.replace(sub, '')
                linesA.pop(pln_int)
                linesA.insert(pln_int, newLine)
    except IndexError:
        # inserts the change to the list
        linesA.insert(pln_int, pch)


if __name__ == "__main__":
    # user input file name to be read and new file to be written to
    fileName = raw_input("Enter journal filename: ")
    uFile = open(fileName, 'r')
    nFile = open(raw_input("Enter new name for file: "), 'a+')
    
    # get the journal's lines and initialize a list
    lines = uFile.readlines()
    linesLen = len(lines)
    linesA = []
    
    #The column number to get the line number, + or -, and changes made
    lineNum = 8
    mod = 9
    changes = 10
    

    # Get the line number column and calls the 3 functions
    for x in lines:
        ln = x.split()[lineNum]
        if (ln == '(CREATED)' or ln == '(~)'):
            continue
        else:
            pln = process_lineNum(ln)

        m = x.split()[mod]
        ch = x.split()[changes]
        
        if (ch == "\' " or ch == "\'," ):
            more = x.split()[changes + 1]
            ch = ch + " " + more
            pch = process_changes(ch)
        else:
            pch = process_changes(ch)

        process_creation(pln, m, pch)

    # writes to new text file
    for i in range(0, len(linesA)):
        nFile.write(linesA[i] + "\n")

    print("New file creation complete!")