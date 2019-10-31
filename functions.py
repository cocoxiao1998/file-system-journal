import os
import errno
import stat
import pyinotify
import time

# class that contains methods of events
class EventHandler(pyinotify.ProcessEvent):
	def process_IN_CREATE(self, event):

		# check if whatever is created is  a file, and then a text file
		if os.path.isfile(event.pathname):
			if event.pathname[-4:] == ".txt":
				# will create a journal in the hidden dir
				journal = event.pathname.replace(watched_dir, watched_dir_hidden)
				journal = journal.replace(".txt", "-journal.txt")
				f = open(journal, "a+")

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

				# writing to journal now
				f.write(str(inode) + " " + name + " " + str(permissions) + " " + timestamp + " " + change + "\n")
				f.close()

# the watched events (for now)
mask = pyinotify.IN_CREATE

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
