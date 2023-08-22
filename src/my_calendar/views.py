from collections import defaultdict
from datetime import datetime


from django.db.models.functions import TruncDay

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
            data['finish_date'] = finish_date.strftime('%d-%m-%Y %H:%M:%S')


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
    def get(self, request, year, month, day):
        events = Event.objects.filter(start_date__year=year,
                                    start_date__month=month,
                                    start_date__day=day)
        serializer = EventSerializer(events, many=True)
        data = serializer.data

        return Response({'events': data})

class AggregatedEventsByMonthView(APIView):
    def get(self, request, year, month):
        aggregated_events = Event.objects.filter(start_date__year=year, start_date__month=month) \
            .annotate(day=TruncDay('start_date')) \
            .values('day', 'name')

        day_events = defaultdict(list)

        for event in aggregated_events:
            day = event['day'].strftime('%Y-%m-%d')
            description = event['name']
            day_events[day].append(description)

        aggregated_data = [
            {"day": day, "events": events}
            for day, events in day_events.items()
        ]

        return Response({"aggregated_data": aggregated_data})