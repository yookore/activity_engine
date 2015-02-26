from uuid import uuid1, uuid4
from cqlengine import Model
from cqlengine import columns
import datetime
from django.utils.timezone import make_naive
import pytz
from stream_framework.activity import Activity
from feed_engine.verbs import PostVerb


class Profile(object):
    """
    Model for the user defined type of profile.
    """
    def __int__(self, birthdate, gender, title, relationshipstatus, homecountry, currentcountry, timezone, profilepicture, alternate_email, religion, interests, cellphone, biography ):
        self.birthdate = birthdate
        self.gender = gender
        self.title = title
        self.relationshipstatus = relationshipstatus
        self.homecountry = homecountry
        self.currentcountry = currentcountry
        self.timezone = timezone
        self.profilepicture = profilepicture
        self.alternate_email = alternate_email
        self.religion = religion
        self.interests = interests
        self.cellphone = cellphone
        self.biography = biography


class User(Model):
    __table_name__ = "users"

    """
    Model for the User. Will be using this as the auth model.
    """
    username =columns.Text(primary_key=True)
    jiveuserid = columns.Integer(partition_key=True)
    creationdate = columns.DateTime()
    email = columns.Text()
    firstlogin = columns.Boolean()
    firstname = columns.Text()
    lastloggedin = columns.DateTime()
    lastname = columns.Text()
    lastprofileupdate =columns.DateTime()
    password = columns.Text()
    userid = columns.UUID(default=uuid4())


class Relationship(Model):
    __table_name__ = "relationships"
    relationship_id = columns.UUID(primary_key=True, default=uuid4())
    user = columns.Text(partition_key=True)
    target_user = columns.Text()
    creationdate = columns.DateTime(default=datetime.datetime.now())
    status = columns.Text()

class Content(Model):
    """
    Base class for all content types in Yookore. Content types like status updates, photos,
    videos, blog posts, audio
    """
    __table_name__ = 'content'
    author = columns.Text(primary_key=True)
    id = columns.TimeUUID(primary_key=True, default=uuid1, clustering_order="desc") #content id
    content_type = columns.Text(polymorphic_key=True, index=True)
    creationdate = columns.DateTime(default=datetime.datetime.now())
    tags = columns.List(value_type=columns.Text())
    viewcount = columns.Integer()
    likescount = columns.Integer()
    commentcount = columns.Integer()

class StatusUpdate(Content):
    __polymorphic_key__ = "statusupdate"

    text = columns.Text()
    location = columns.Text()

    @property
    def create_activity(self):
        print "Object id: ", self.id
        print "User id: ", self.author
        activity = Activity(
            actor=self.author,
            verb=PostVerb,
            object=self.id,
            #time = self.created_at
        )

        return activity

class BlogPost(Content):
    __polymorphic_key__ = "blogpost"

    text = columns.Text()

    def create_activity(self):
        pass

class Photo(Content):
    __polymorphic_key__ = "photo"

    original_url = columns.Text()
    thumbnail_url = columns.Text()

    def create_activity(self):
        pass

class Video(Content):
    __polymorphic_key__ = "video"

    def create_activity(self):
        pass

class Audio(Content):
    __polymorphic_key__ = "audio"


    def create_activity(self):
        pass


if __name__ == '__main__':
    from feed_engine.feedmanager import manager
    from feed_engine.verbs import PostVerb
    from feed_engine.models import StatusUpdate

    status = StatusUpdate()
    status.author = 'jomski2009'
    status.text = 'Trying to ensure that I can save stuff in the feeds!'
    status.location = 'Randburg'

    status.save()

    manager.addactivity(status)