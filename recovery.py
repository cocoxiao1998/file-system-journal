# user input file name to be read and written to
uFile = open(raw_input("Enter filename: "), 'r')
nFile = open(raw_input("Enter new filename: "), 'a+')

# Set variables to traverse the text file
lines = uFile.readlines()
changes = 8
result = []

# Get the changes column and append to array
for x in lines:
    result.append(x.split()[changes])

uFile.close() # Close the file

# Get the changes that were made and write into new text file
length = len(result)

for i in range(0, length):
    s = result[i]
    slen = len(s)
    start = s.find("\'")
    nS = s[start + 1:-2]
    nFile.write(nS + "\n")

print("\nFile re-creation complete!")
