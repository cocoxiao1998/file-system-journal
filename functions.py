import os
import errno
import stat
import pyinotify
import time
import datetime
from itertools import izip_longest

# class that contains methods of events
class EventHandler(pyinotify.ProcessEvent):
	def process_IN_CREATE(self, event):
		# check that it is a text file that is being created
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

				# timestamp
				timestamp = time.ctime(os.path.getctime(event.pathname))

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
				line_num = 1
				for line in change:
					j.write(str(inode) + " " + name + " " + str(permissions) + " " + timestamp + " (" + str(line_num) + " + '" + line + "')\n")
					line_num += 1
				j.close()

	def process_IN_DELETE(self, event): #if any file or folder within the directory is observed being deleted

		#get name of file and extension just deleted
		name = os.path.basename(event.pathname)

		#if the filename is of the .txt extension
		if name[-4:] == ".txt":

			#deleting the hidden file to allow proper reuse of the filename
			hidden_file = event.pathname.replace(watched_dir, watched_dir_hidden)
			hidden_file = hidden_file.replace(".txt", "-hidden-file.txt")
			#remove the hidden file
			os.remove(hidden_file)

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

	def process_IN_MODIFY(self, event):
		# check that it is a text file that is being modified
		if os.path.isfile(event.pathname):
			if event.pathname[-4:] == ".txt":
				# setting the metadata in variables first
				# inode number
				inode = os.lstat(event.pathname)[stat.ST_INO]

				# filename
				name = os.path.basename(event.pathname)

				# permissions
				permissions = os.stat(event.pathname)[stat.ST_MODE]
				permissions = oct(permissions)[-3:]

				# timestamp
				timestamp = time.ctime(os.path.getmtime(event.pathname))


				# getting changes
				file = event.pathname
				f = open(file, "r")

				hidden_file = event.pathname.replace(watched_dir, watched_dir_hidden)
				hidden_file = hidden_file.replace(".txt", "-hidden-file.txt")
				h = open(hidden_file, "r")

				journal = event.pathname.replace(watched_dir, watched_dir_hidden)
				journal = journal.replace(".txt", "-journal.txt")
				j = open(journal, "a+")

				f_text = f.read().splitlines()
				f_length = len(f_text)
				h_text = h.read().splitlines()
				h_length = len(h_text)

				# stripping the line returns
				f_text = [line.rstrip("\n") for line in f_text]
				h_text = [line.rstrip("\n") for line in h_text]

				line_num = 1
				for f_line, h_line in izip_longest(f_text, h_text):

					if f_line != h_line and line_num <= f_length and line_num <= h_length:
						# writing changes to the journal
						remove_change = "(" + str(line_num) + " - " + ")"
						j.write(str(inode) + " " + name + " " + str(permissions) + " " + timestamp + " " + remove_change + "\n")
						add_change = "(" + str(line_num) + " + '" + f_line + "')"
						j.write(str(inode) + " " + name + " " + str(permissions) + " " + timestamp + " " + add_change + "\n")

					elif line_num > f_length:
						remove_line = "(" + str(line_num) + " - " + ")"
						j.write(str(inode) + " " + name + " " + str(permissions) + " " + timestamp + " " + remove_line + "\n")

					elif line_num > h_length:
						add_change = "(" + str(line_num) + " + '" + f_line + "')"
						j.write(str(inode) + " " + name + " " + str(permissions) + " " + timestamp + " " + add_change + "\n")

					line_num += 1

				# updating hidden file
				h.close()
				h = open(hidden_file, "w")

				for line in f_text:
					h.write(line + "\n")

				# closing files
				f.close()
				h.close()
				j.close()


# the watched events (for now), add each event as you work on it
mask = pyinotify.IN_CREATE | pyinotify.IN_DELETE | pyinotify.IN_MODIFY

# creating watch manager object
wm = pyinotify.WatchManager()

try:
	# adding the directory that will be watched and the watched events
	watched_dir = os.path.abspath("home/coco/watched_dir")
	# creating hidden dir with same path as watched dir
	watched_dir_hidden = "home/coco/.watched_dir_hidden"
except:
	print("The watched directory does not exist")
	exit()

# adding the watched events
wm.add_watch(watched_dir, mask)

# creating the notifier object
notifier = pyinotify.Notifier(wm, EventHandler())

# starting the watch
notifier.loop()
