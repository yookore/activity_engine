from uuid import uuid1, uuid4
import datetime

from cqlengine import Model
from cqlengine import columns

from stream_framework.activity import Activity
from feed_engine.verbs import PostVerb


class Profile(object):
    """
    Model for the user defined type of profile.
    """

    def __int__(self, birthdate, gender, title, relationshipstatus, homecountry, currentcountry, timezone,
                profilepicture, alternate_email, religion, interests, cellphone, biography):
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
    username = columns.Text(primary_key=True)
    jiveuserid = columns.Integer(primary_key=True, clustering_order='asc')
    creationdate = columns.DateTime()
    email = columns.Text(primary_key=True, clustering_order='asc')
    firstlogin = columns.Boolean()
    firstname = columns.Text()
    lastloggedin = columns.DateTime()
    lastname = columns.Text()
    lastprofileupdate = columns.DateTime()
    password = columns.Text()
    userid = columns.UUID(default=uuid4())


class Relationship(Model):
    __table_name__ = "relationships"
    user = columns.Text(primary_key=True)
    target_user = columns.Text(primary_key=True)
    relationship_id = columns.UUID(default=uuid4())
    creationdate = columns.DateTime(default=datetime.datetime.now())
    status = columns.Text()  # active, pending, retired, deleted
    type = columns.Text()  # following, friend


class Comment(Model):
    object_id       = columns.UUID(primary_key = True)
    id              = columns.TimeUUID(primary_key = True, default=uuid1, clustering_order="desc")
    author          = columns.Text(primary_key=True)
    created_at      = columns.DateTime(default=datetime.datetime.now())
    updated_at      = columns.DateTime()
    view_count      = columns.Integer(default=0)
    like_count      = columns.Integer(default=0)
    body	        = columns.Text()


class Content(Model):

    __table_name__  = 'content'
    id              = columns.TimeUUID(primary_key = True, default=uuid1)
    author          = columns.Text(primary_key=True, clustering_order='ASC')
    content_type    = columns.Text(polymorphic_key=True, index=True)
    #created_at      = columns.DateTime(default=datetime.now(), primary_key = True, clustering_order='DESC')
    created_at      = columns.DateTime(default=datetime.datetime.now())
    updated_at      = columns.DateTime()
    view_count      = columns.Integer(default=0)
    like_count      = columns.Integer(default=0)
    comment_count   = columns.Integer(default=0)
    tags            = columns.List(value_type=columns.Text(), default=[])
    images          = columns.List(value_type=columns.Bytes(), default=[]) #['url1','url2',...'urln']
    img             = columns.Bytes()

    def create(self):
        pass

    def commenting(self):
        pass

    def liking(self):
        pass

class StatusUpdate(Content):
    __polymorphic_key__ = 'statusupdate'
    body            = columns.Text(required = True)
    location        = columns.Text()
    def __unicode__(self):
        return self.body

class BlogPost(Content):
    __polymorphic_key__ = 'blogpost'
    title           = columns.Text()
    body            = columns.Text()
    location        = columns.Text()
    def __unicode__(self):
        return self.title, self.body

class PhotoAlbum(Content):
    __polymorphic_key__ = 'photoalbum'
    title		    = columns.Text(required = True)
    location		= columns.Text()
    nb_photo        = columns.Integer(default=0)


class Photo(Content):
    __polymorphic_key__ = 'photo'
    # objectid is the id of a container: photo album, blog post or status update
    object_id		= columns.TimeUUID(required = True, index=True)
    caption			= columns.Text(required = False)
    data     		= columns.Bytes(required = False)
    url_original    = columns.Text(required = True)
    url_thumbnail   = columns.Text(required=False)
    location        = columns.Text(required=False)
    image_type      = columns.Text(required=False)
    filename        = columns.Text(required=False)
    width           = columns.Integer(required=False)
    height          = columns.Integer(required=False)

class Video(Content):
    __polymorphic_key__ = 'video'
    # objectid is the id of a container: photo album, blog post or status update
    object_id       = columns.TimeUUID(required = True, index=True)
    caption         = columns.Text(required = False)
    url_original    = columns.Text(required = True)
    location        = columns.Text()

class AudioBlog(Content):
    __polymorphic_key__ = 'audioblog'
    caption         = columns.Text(required = False)
    data            = columns.Bytes(required = True)
    url_original    = columns.Text()


# class Content(Model):
#     """
#     Base class for all content types in Yookore. Content types like status updates, photos,
#     videos, blog posts, audio
#     """
#     __table_name__ = 'content'
#     author = columns.Text(primary_key=True)
#     id = columns.TimeUUID(primary_key=True, default=uuid1(), clustering_order="desc")  # content id
#     content_type = columns.Text(polymorphic_key=True, index=True)
#     created_at = columns.DateTime(default=datetime.datetime.now())
#     tags = columns.List(value_type=columns.Text())
#     view_count = columns.Integer()
#     like_count = columns.Integer()
#     comment_count = columns.Integer()
#     updated_at = columns.DateTime(default=datetime.datetime.now())
#
#
# class StatusUpdate(Content):
#     __polymorphic_key__ = "statusupdate"
#
#     body = columns.Text()
#     location = columns.Text()
#
#     def get_object_type(self):
#         return str(self.__polymorphic_key__)
#
#     def __str__(self):
#         return "StatusUpdate: { " + str(self.id) + " : " + self.author + ": " + self.body + " }"
#
#     @property
#     def create_activity(self):
#         activity = Activity(
#             actor=self.author,
#             verb=PostVerb,
#             object=self.id,
#             object_type=self.get_object_type(),
#             target=None,
#             target_type=None,
#             time=self.created_at
#         )
#
#         return activity
#
#
# class BlogPost(Content):
#     __polymorphic_key__ = "blogpost"
#
#     title = columns.Text()
#     body = columns.Text()
#
#     @property
#     def create_activity(self):
#         activity = Activity(
#             actor=self.author,
#             verb=PostVerb,
#             object=self.id,
#             object_type=self.__polymorphic_key__,
#             target=None,
#             target_type=None,
#             time=self.created_at,
#         )
#
#         return activity
#
#     def __str__(self):
#         return "Blogpost: { " + self.author + ": " + self.title + " }"
#
#
# class Photo(Content):
#     __polymorphic_key__ = "photo"
#
#     original_url = columns.Text()
#     thumbnail_url = columns.Text()
#
#     def create_activity(self):
#         pass
#
#
# class Video(Content):
#     __polymorphic_key__ = "video"
#
#     def create_activity(self):
#         pass
#
#
# class Audio(Content):
#     __polymorphic_key__ = "audio"
#
#
#     def create_activity(self):
#         pass
#

class ActivityItemModel(object):
    published = ""  # datetime.isofromat
    actor = {}  # actor dictionary object
    verb = ""  # string
    object = {}  # object dictionary
    target = {}  # dictionary
    title = ""
    img = ""     # added to get the blob (image)
    content = {}
    updated = ""


class ActivityModelJson(object):
    actor = ""
    object = ""
    object_type = ""
    verb = 0
    target = ""
    target_type = ""


class PaginationObject(object):
    nextset = uuid1()
