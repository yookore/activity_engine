from rest_framework import serializers

class ActorSerializer(serializers.Serializer):
    id = serializers.CharField()
    displayname = serializers.CharField()
    objecttype = serializers.CharField()
    creationdate = serializers.DateTimeField()
    lastprofileupdate = serializers.DateTimeField()
    url = serializers.CharField()

class ObjectSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    type = serializers.CharField()
    title = serializers.CharField(required=False)
    text = serializers.CharField(required=False)
    likes = serializers.IntegerField(required=False)
    views = serializers.IntegerField(required=False)
    comments = serializers.IntegerField(required=False)
    publishdate = serializers.DateTimeField()
    url = serializers.CharField(required=False)

class ActivityModelSerializer(serializers.Serializer):
    published = serializers.DateTimeField()
    actor = ActorSerializer()
    verb  = serializers.CharField()
    object = ObjectSerializer()
    updated = serializers.DateTimeField()

class PaginationObjectSerializer(serializers.Serializer):
    next = serializers.UUIDField()
    previous = serializers.UUIDField()