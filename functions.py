import os
import errno
import stat
import pyinotify
import time
import datetime
import difflib

# class that contains methods of events
class EventHandler(pyinotify.ProcessEvent):
	def process_IN_CREATE(self, event):
		
		# check if whatever is created is a file and if it is a .txt file
		if os.path.isfile(event.pathname):
			if event.pathname[-4:] == ".txt":

				# setting the metadata in variables first
				# inode number
				inode = os.lstat(event.pathname)[stat.ST_INO]

				# only the filename
				name = os.path.basename(event.pathname)

				# permissions
				permissions = os.stat(event.pathname)[stat.ST_MODE]
				permissions = oct(permissions)[-3:]

				#BEGIN BELOW CHANGES
				# timestamp #the below was replaced 11/23/19 to help confirm ON_CREATE wasn't calling IN_ATTRIB - PETE
				now = datetime.datetime.now()
				day = now.strftime("%d")
				if day[0] == '0':
					day = day[1]
				timestamp = now.strftime("%a %b " + day +" %H:%M:%S %Y")
				#the original timestamp is below
				#timestamp = time.ctime(os.path.getctime(event.pathname)) #previous method replaced with above to avoid CREATE and ATTRIB collisions
				#END ABOVE CHANGES

				# getting change: will set the changes to "line #, +/-, content"
				file = event.pathname
				f = open(file, "r")

				change = f.readlines()
				change = [line.rstrip("\n") for line in change]

				f.close()

				# creating hidden file and journal in hidden dir (if not created)
				# and appending changes to them
				hidden_file = event.pathname.replace(watched_dir, watched_dir_hidden)
				hidden_file = hidden_file.replace(".txt", "-hidden-file.txt")
				h = open(hidden_file, "w")

				for line in change:
					h.write(line + "\n")
				h.close()

				journal = event.pathname.replace(watched_dir, watched_dir_hidden)
				journal = journal.replace(".txt", "-journal.txt")
				j = open(journal, "a+")

				j.write(str(inode) + " " + name + " " + str(permissions) + " " + timestamp + " (CREATED)\n")
				for line in change:
					j.write(str(inode) + " " + name + " " + str(permissions) + " " + timestamp + " ('" + line + "')\n")
				j.close()
				#print(timestamp)
		#print("called")

	def process_IN_DELETE(self, event): #if any file or folder within the directory is observed being deleted

		#get name of file and extension just deleted
		name = os.path.basename(event.pathname)

		#if the filename is of the .txt extension
		if name[-4:] == ".txt":

			#indicating what the name of the hidden file should be
			hidden_file = event.pathname.replace(watched_dir, watched_dir_hidden)
			hidden_file = hidden_file.replace(".txt", "-hidden-file.txt")

			#if the file journal and file copy both exist, delete the hidden_file and edit the journal
			if os.path.isfile(hidden_file):
				os.remove(hidden_file) #remove the hidden file

				#from original ON_CREATE allowing user to open the filename-journal.txt to show changes
				journal = event.pathname.replace(watched_dir, watched_dir_hidden)
				journal = journal.replace(".txt", "-journal.txt")

				#open file journal explicitly for reading
				f = open(journal, "r")
				#since the file is deleted the below code will get the information about the file from the file journal
				contents = f.readlines()[-1] #read only the last line of the journal for information
				node = contents.split(' ',1)[0] #extracts the inode id of the file just deleted
				permissions = contents.split(' ', 3)[2] #extracts the permissions of the file just deleted
				now = datetime.datetime.now() #records current time to variable

				#formatting the day to not contain a zero if the day is a single digit
				#please watch this part of the code
				day = now.strftime("%d")
				if day[0] == '0':
					day = day[1]
				#formatting the timestamp to match the ON_CREATE situation
				timestamp = now.strftime("%a %b " + day +" %H:%M:%S %Y")

				#closing the file for read-only purposes
				f.close()

				#open file journal explicitly for appending
				f = open(journal, "a+")
				#formatting write output
				f.write(node + " " + name + " " + permissions + " " + timestamp + " (~)\n")

				#close the file
				f.close()
			else:
				print("Filename \"" + name + "\" was detected as being removed from the below watched directory: \n" + watched_dir + ".\nNo Journal or Hidden Copy was found for this file, thus no changes have been recorded.\nPlease ensure the script is running before working in your watched directory.")

# the watched events (for now), add each event as you work on it
mask = pyinotify.IN_CREATE | pyinotify.IN_DELETE | pyinotify.IN_ATTRIB | pyinotify.IN_MOVED_TO | pyinotify.IN_MOVED_FROM

# creating watch manager object
wm = pyinotify.WatchManager()

#saving the file directory names that will be watched to variables
watched_dir = os.path.abspath("Desktop/watched_dir")
watched_dir_hidden = "Desktop/.watched_dir_hidden"

#if the above directories have not yet been created, do so:
try:
	os.makedirs(watched_dir_hidden)#makedirs makes all parent directories automatically
except:
	pass

#adding the watched directory so functions can be invoked by Create, Delete, and Modify detections
wm.add_watch(watched_dir, mask)

# creating the notifier object
notifier = pyinotify.Notifier(wm, EventHandler())

# starting the watch
notifier.loop()
