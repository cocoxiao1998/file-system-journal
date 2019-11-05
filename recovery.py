
#def process_lineNum():

#def process_mod():

'''
process_changes function gets the changes that were made 
and write into new text file
'''

def process_changes(changesA):
    length = len(changesA)
    #cResult = []

    for i in range(0, length):
        s = changesA[i]
        slen = len(s)
        start = s.find("\'")
        nS = s[start + 1:-2]
        nFile.write(nS + "\n")
        print("\nFile re-creation complete!")

if __name__ == "__main__":
    # user input file name to be read and written to
    uFile = open(raw_input("Enter filename: "), 'r')
    nFile = open(raw_input("Enter new filename: "), 'a+')
    lines = uFile.readlines()
    
    lineNum = 8
    mod = 9
    changes = 10

    lineNumA = []
    modA = []
    changesA = []

    # Get the line number column and append to array
    for x in lines:
        lineNumA.append(x.split()[lineNum])
        modA.append(x.split()[mod])
        changesA.append(x.split()[changes])

    process_changes(changesA)

    uFile.close() # Close the file