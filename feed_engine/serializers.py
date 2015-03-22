from rest_framework import serializers

class ActorSerializer(serializers.Serializer):
    id = serializers.CharField()
    displayname = serializers.CharField()
    objecttype = serializers.CharField()
    creationdate = serializers.DateTimeField()
    lastprofileupdate = serializers.DateTimeField()
    url = serializers.CharField()
    imageurl = serializers.CharField()

class LatestCommentSerializer(serializers.Serializer):
    author = serializers.CharField(allow_null=True)
    object_id = serializers.UUIDField()
    id = serializers.UUIDField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    body = serializers.CharField()


class ObjectSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    type = serializers.CharField()
    title = serializers.CharField(required=False)
    text = serializers.CharField(required=False)
    likes = serializers.IntegerField(required=False)
    views = serializers.IntegerField(required=False)
    comments = serializers.CharField()
    commentcount = serializers.IntegerField()
    publishdate = serializers.DateTimeField()
    url = serializers.CharField(required=False)
    latestcomment = serializers.DictField(required=False)
    img = serializers.CharField(required=False)
    url_original = serializers.CharField(required=False)
    # Emile - audio feature additions
    filename = serializers.CharField(required=False)
    caption = serializers.CharField(required=False)
    # END - audio feature additions

class ActivityModelSerializer(serializers.Serializer):
    published = serializers.DateTimeField()
    actor = ActorSerializer()
    verb  = serializers.CharField()
    object = ObjectSerializer()
    updated = serializers.DateTimeField()

class ActivityRequestSerializer(serializers.Serializer):
    author = serializers.CharField(required=True)
    verb_id = serializers.CharField(required=True)
    object_id = serializers.CharField(required=True)
    object_type = serializers.CharField(required=True)
    target_id = serializers.CharField(required=False, allow_blank=True)
    target_type = serializers.CharField(required=False, allow_blank=True)
    created_at = serializers.DateTimeField(required=False)

class PaginationObjectSerializer(serializers.Serializer):
    next = serializers.UUIDField()
    previous = serializers.UUIDField()

class UserProfileRequestSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
