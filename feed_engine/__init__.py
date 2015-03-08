#I am assuming that code placed here will run on startup?
from cassandra.cluster import Cluster
from cqlengine.connection import setup
from cqlengine.management import sync_table
from feed_engine.models import Photo, BlogPost, StatusUpdate, Video, User, Relationship, Comment

# print "Syncing tables ..."
#
setup(['192.168.10.200', '192.168.10.201', '192.168.10.202'], "yookore")
sync_table(Photo)
sync_table(BlogPost)
sync_table(StatusUpdate)
sync_table(Video)
# sync_table(User)
# sync_table(Relationship)
sync_table(Comment)
