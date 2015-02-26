from stream_framework.feeds.cassandra import CassandraFeed




class FlatFeed(CassandraFeed):
    key_format = "flat:feed:%(user_id)s"
    timeline_cf_name = "activities"

class UserFeed(FlatFeed):
    key_format = "user:feed:%(user_id)s"

class NotificationFeed(FlatFeed):
    key_format = "notification:feed:%(user_id)s"