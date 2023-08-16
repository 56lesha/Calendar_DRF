from datetime import datetime

from django.db.models import Q, Count
from django.db.models.functions import TruncMonth
from django.forms import model_to_dict
from django.shortcuts import render
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from my_calendar.models import Event
from my_calendar.serializers import EventSerializer


# Create your views here.
class EventAPIView(APIView):
    def get(self, request):
        events = Event.objects.all()

        return Response({"events": EventSerializer(events, many=True).data})

    def post(self, request):
        data = request.data
        if not data.get('finish_date'):
            start_date = datetime.strptime(data['start_date'], '%d-%m-%Y %H:%M:%S')
            finish_date = start_date.replace(hour=23, minute=59, second=59)
            data['finish_date'] = finish_date.strftime("%d-%m-%Y %H:%M:%S")
        serializer = EventSerializer(data=data)
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

class EventDayAPIView(APIView):
    def get(self, request, *args, **kwargs):
        if kwargs:
            year = kwargs.get('year', None)
            month = kwargs.get('month', None)
            day = kwargs.get('day', None)

            if day:
                events = Event.objects.filter(Q(start_date__year=year) &
                                              Q(start_date__month=month) &
                                              Q(start_date__day=day))
                return Response({"events": EventSerializer(events, many=True).data})

            else:
                events = Event.objects.annotate(month=TruncMonth('start_date')).values('month').annotate(c=Count('id'))
                return Response({"events": EventSerializer(events, many=True).data})






