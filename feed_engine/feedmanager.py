from stream_framework.feed_managers.base import Manager, FanoutPriority
from feed_engine import Relationship
from feed_engine.feeds import UserFeed, FlatFeed, NotificationFeed, YookoreAggregatedFeed


class FeedManager(Manager):
    user_feed_class = UserFeed

    feed_classes = dict(
        flat=FlatFeed,
        notification=NotificationFeed,
        #aggregated=YookoreAggregatedFeed,
    )

    def get_user_follower_ids(self, user_id):
        rels = Relationship.objects.filter(user=user_id)
        ids_high = []
        ids_low = []
        for rel in rels:
            ids_high.append(rel.target_user)

        #user_id will have to be usernames
        #return a dictionary of usernames with different priorities
        #e.g, {'HIGH':[], 'LOW':[]}

        return {FanoutPriority.HIGH:ids_high}

    def addactivity(self, content):
        activity = content.create_activity
        self.add_user_activity(content.author, activity)

    def addactivity_rest(self, actor, activity):
        print ("Adding activity...")
        self.add_user_activity(actor, activity)

manager = FeedManager()
