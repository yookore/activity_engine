from stream_framework.feed_managers.base import Manager
from feed_engine.feeds import UserFeed, FlatFeed, NotificationFeed


class FeedManager(Manager):
    user_feed_class = UserFeed

    feed_classes = dict(
        flat=FlatFeed,
        notification=NotificationFeed,
    )

    def get_user_follower_ids(self, user_id):
        #user_id will have to be usernames
        #return a dictionary of usernames with different priorities
        #e.g, {'HIGH':[], 'LOW':[]}

        return {}

    def addactivity(self, content):
        activity = content.create_activity
        self.add_user_activity(content.author, activity)


manager = FeedManager()
