from rest_framework import serializers


class UserProfileSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    firstname = serializers.CharField(required=True)
    lastname = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    alternate_email = serializers.CharField(required=False)
    biography = serializers.CharField(required=False)
    birthdate = serializers.DateTimeField(required=True)
    cellphone = serializers.CharField(required=False)
    currentcountry = serializers.CharField(required=False)
    gender = serializers.CharField(required=False)
    homecountry =serializers.CharField(required=False)
    imageurl = serializers.CharField(required=False)
    interests = serializers.ListField(required=False)
    lastupdated = serializers.DateTimeField(required=False)
    profilepicture = serializers.ImageField(required=False)
    relationshipstatus = serializers.CharField(required=False)
    religion = serializers.CharField(required=False)
    timezone = serializers.CharField(required=False)
    title = serializers.CharField(required=False)
