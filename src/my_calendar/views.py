from django.forms import model_to_dict
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from my_calendar.models import Event
from my_calendar.serializers import EventSerializer


# Create your views here.
class EventAPIView(APIView):
    def get(self, request):
        events = Event.objects.all()
        print(EventSerializer(events, many=True).data)
        return Response({"events": EventSerializer(events, many=True).data})

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True) #метод is_valid автоматически создаёт словарь validated_data
        serializer.save() #метод save автоматически вызывает метод create из сериализатора

        return Response({'post': serializer.data})


    def put(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        if not pk:
            return Response({"error": "I don't know what to change"})

        try:
            instance = Event.objects.get(pk=pk)
        except:
            return Response({"error": "Don't have the instance"})

        serializer = EventSerializer(instance=instance, data=request.data)
        serializer.is_valid()
        serializer.save() #автоматически вызывает метод update
        return Response({"update_event": serializer.data})


    def delete(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        if not pk:
            return Response({"error": "Method DELETE not allowed"})

        try:
            instance = Event.objects.get(pk=pk)
        except:
            return Response({"error": "instance doesn't exist"})
        instance.delete()
        return Response({"post": "delete post " + str(pk)})

