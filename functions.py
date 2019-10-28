import os, errno
import pyinotify

# class that contains methods of events
class EventHandler(pyinotify.ProcessEvent):
	def process_IN_CREATE(self, event):
		# testing purpose rn
		print("Something was created")

		# splitting path to get only name (might not need)
		name = event.pathname.split('/')
		name = name[-1]
		print("File or dir name: ", name)

		# checking if file type is .txt or if it is a dir
		if os.path.isdir(event.pathname):
			print("directory")
			# will create dir in hidden dir
			try:
				dir = event.pathname.replace(watched_dir, watched_dir_hidden)
				print("new hidden dir: ", dir)
				os.makedirs(dir)
			except:
				print("already exists")
				pass

		if os.path.isfile(event.pathname):
			print("checking if file ends in txt: ", event.pathname[-4:])
			if event.pathname[-4:] == ".txt":
				# will create a journal in the hidden dir
				print("will create journal")
				journal = event.pathname.replace(watched_dir, watched_dir_hidden)
				journal = journal.replace(".txt", "-journal.txt")
				f = open(journal, "a+")
				f.write(name + "\n")
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
	print("already exists")
	pass

# creating the notifier object
notifier = pyinotify.Notifier(wm, EventHandler())

# starting the watch
notifier.loop()
