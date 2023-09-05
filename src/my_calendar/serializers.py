import io

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers

from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from my_calendar.models import Event, UserProfile


class EventSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    start_date = serializers.DateTimeField(input_formats=['%d-%m-%Y %H:%M:%S'])
    finish_date = serializers.DateTimeField(input_formats=['%d-%m-%Y %H:%M:%S'])
    reminder = serializers.CharField(max_length=255)

    def create(self, validated_data):
        return Event.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.start_date = validated_data.get("start_date", instance.start_date)
        instance.finish_date = validated_data.get("finish_date", instance.finish_date)
        instance.reminder = validated_data.get("reminder", instance.reminder)
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email")

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "password")
        extra_kwargs = {"password": {"write_only":True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail("bad_token")







#
# class EventModel:
#     def __init__(self, title, content):
#         self.title = title
#         self.content = content
#
# class EventSerializer_TEST(serializers.Serializer):
#     title = serializers.CharField(max_length=255)
#     content = serializers.CharField()
#
# def encode():
#     event_1 = EventModel("Learn", "Learn DRF")
#     event_2 = EventModel("Clean", "Clean room")
#     model_sr = EventSerializer([event_1, event_2], many=True) # создаёт специальную коллекцию data и представляет в виде словаря
#     print(model_sr.data, type(model_sr.data), sep='\n')
#     json = JSONRenderer().render(model_sr.data) # преобразовываем словарь в байтовую строку
#     print(json)
#
# def decode():
#     stream = io.BytesIO(b'{"title":"Learn","content":"Learn DRF"}')
#     print(stream)
#     data = JSONParser().parse(stream)
#     print(data)
#     serializer = EventSerializer(data=data)
#     print(serializer)
#     serializer.is_valid()
#     print(serializer.validated_data)






