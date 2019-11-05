import os
import errno
import stat
import pyinotify
import time
import difflib

# class that contains methods of events
class EventHandler(pyinotify.ProcessEvent):
	def process_IN_CREATE(self, event):
		# check that it is a text file that is being created
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
				timestamp = time.ctime(os.path.getctime(event.pathname))

				# change: will set the changes to "line #, +/-, content"
				change = "(1 + '')"

				# will create the empty hidden file
				hidden_file = event.pathname.replace(watched_dir, watched_dir_hidden)
				hidden_file = hidden_file.replace(".txt", "-hidden-file.txt")
				h = open(hidden_file, "a+")
				h.close()

				# will create a journal in the hidden dir
				journal = event.pathname.replace(watched_dir, watched_dir_hidden)
				journal = journal.replace(".txt", "-journal.txt")
				j = open(journal, "a+")

				# writing to journal now
				j.write(str(inode) + " " + name + " " + str(permissions) + " " + timestamp + " " + change + "\n")
				j.close()

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
				print("timestamp: ", timestamp)


				# getting changes
				# opening files
				file = event.pathname
				f = open(file, "r")

				hidden_file = event.pathname.replace(watched_dir, watched_dir_hidden)
				hidden_file = hidden_file.replace(".txt", "-hidden-file.txt")
				h = open(hidden_file, "r")

				journal = event.pathname.replace(watched_dir, watched_dir_hidden)
				journal = journal.replace(".txt", "-journal.txt")
				j = open(journal, "a+")

				text1 = f.readlines()
				text2 = h.readlines()

				# comparing file text. "-" for unique to sequence 1
				d = difflib.Differ()
				diff = list(d.compare(text1, text2))
				diff = [line.rstrip("\n") for line in diff]

				line_num = 1
				for line in diff:
					operator = line[0]
					# checking if line is unique to file being modified
					if operator == "-":
						# journal entry: removing a line
						#change = "(" + str(line_num) + " - '" +

						# journal entry: adding a line
						line = line[2:]
						change = "(" + str(line_num) + " + '" + line + "')"
						j.write(str(inode) + " " + name + " " + str(permissions) + " " + timestamp + " " + change + "\n")

					line_num += 1
					print("Differences: ", line)

				# closing files
				f.close()
				h.close()
				j.close()

				# updating hidden file

# the watched events (for now)
mask = pyinotify.IN_CREATE | pyinotify.IN_MODIFY

# creating watch manager object
wm = pyinotify.WatchManager()

# adding the directory that will be watched and the watched events
watched_dir = os.path.abspath("/home/coco/watched_dir")
wm.add_watch(watched_dir, mask)

# creating hidden dir with same path as watched dir
watched_dir_hidden = "/home/coco/.watched_dir_hidden"
try:
	os.makedirs(watched_dir_hidden)
except:
	pass

# creating the notifier object
notifier = pyinotify.Notifier(wm, EventHandler())

# starting the watch
notifier.loop()
