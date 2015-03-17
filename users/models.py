from uuid import uuid4
from cqlengine import Model
from cqlengine import columns

class User(Model):
    __table_name__ = "users"

    """
    Model for the User. Will be using this as the auth model.
    """
    username = columns.Text(primary_key=True)
    jiveuserid = columns.Integer(partition_key=True)
    creationdate = columns.DateTime()
    email = columns.Text(partition_key=True)
    firstlogin = columns.Boolean()
    firstname = columns.Text()
    lastloggedin = columns.DateTime()
    lastname = columns.Text()
    lastprofileupdate = columns.DateTime()
    password = columns.Text()
    userid = columns.UUID(default=uuid4())


class UserProfile(Model):
    __table_name__ = "userprofile"
    username = columns.Text(primary_key=True)
    firstname = columns.Text(required=False)
    lastname = columns.Text(required=False)
    email = columns.Text(required=False)
    alternate_email = columns.Text(required=False)
    biography = columns.Text(required=False)
    birthdate = columns.DateTime(required=True)
    cellphone = columns.Text(required=False)
    currentcountry = columns.Text(required=False)
    gender = columns.Text(required=True)
    homecountry =columns.Text(required=False)
    imageurl = columns.Text(required=False)
    interests = columns.List(value_type=columns.Text)
    lastupdated = columns.DateTime(required=False)
    profilepicture = columns.Blob(required=False)
    relationshipstatus = columns.Text(required=False)
    religion = columns.Text(required=False)
    timezone = columns.Text(required=False)
    title = columns.Text(required=False)
