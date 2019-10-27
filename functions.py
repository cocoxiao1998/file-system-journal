import os
import pyinotify

wm = pyinotify.WatchManager()

# the watched events
mask = pyinotify.IN_CREATE

# class that contains methods of events
class EventHandler(pyinotify.ProcessEvent):
	def process_IN_CREATE(self, event):
		print("testing ...")

# creating the notifier object
notifier = pyinotify.Notifier(wm, EventHandler())

# adding the directory that will be watched and the watched events
watch_this = os.path.abspath("/home/coco/watched_dir")
wm.add_watch(watch_this, mask)

# starting the watch
notifier.loop()

