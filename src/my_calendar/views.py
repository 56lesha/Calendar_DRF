from collections import defaultdict
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.db.models.functions import TruncDay
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from my_calendar.models import Event
from my_calendar.serializers import EventSerializer, UserRegistrationSerializer, TokenObtainPairSerializer
from my_calendar.tasks import send_reminder_email
from my_calendar.utils import EventHelpMixin


# Create your views here.
class EventAPIView(APIView, EventHelpMixin):
    permission_classes = [IsAuthenticated,]

    def get(self, request):
        user_id = super().get_user_id(request)
        events = Event.objects.filter(user=user_id)
        return Response({"events": EventSerializer(events, many=True).data})


    def post(self, request):
        data = request.data
        if not data.get('finish_date'):
            data = super().auto_finish_date(data)
        user_id = super().get_user_id(request)
        data['user'] = user_id
        serializer = EventSerializer(data=data)
        serializer.is_valid(raise_exception=True) #метод is_valid автоматически создаёт словарь validated_data
        serializer.save() #метод save автоматически вызывает метод create из сериализатора


        user_email = User.objects.get(id=user_id).email
        reminder_time = super().set_reminder(data)
        send_reminder_email.apply_async(args=[data, user_email], eta=reminder_time)
        print(datetime.utcnow())
        return Response({'post': serializer.data})




class EventDetailAPIView(APIView, EventHelpMixin):
    permission_classes = [IsAuthenticated,]

    def check_pk(self, *args, **kwargs):
        pk = kwargs.get("pk", None)
        if not pk:
            return Response({"error": "I don't have such pk"})
        return pk

    def get(self, request, *args, **kwargs):
        pk = self.check_pk(*args, **kwargs)
        user_id = super().get_user_id(request)
        try:
            instance = Event.objects.get(pk=pk, user_id=user_id)
            return Response({"event": EventSerializer(instance).data})
        except:
            return Response({"error":f"User with user_id {user_id} don't have event with id {pk}"})


    def put(self, request, *args, **kwargs):
        instance = self.check_pk(*args, **kwargs)
        data = request.data
        data = super().auto_finish_date(data)
        serializer = EventSerializer(instance=instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()  # автоматически вызывает метод update
            return Response({"update_event": serializer.data})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        instance = self.check_pk(*args, **kwargs)
        pk = instance.pk
        instance.delete()
        return Response({"post": "delete post " + str(pk)})



class EventDayAPIView(APIView):
    permission_classes = [IsAuthenticated, ]
    def get(self, request, year, month, day):
        events = Event.objects.filter(start_date__year=year,
                                    start_date__month=month,
                                    start_date__day=day)
        serializer = EventSerializer(events, many=True)
        data = serializer.data

        return Response({'events': data})


class AggregatedEventsByMonthView(APIView):
    permission_classes = [IsAuthenticated, ]
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


class UserRegistrationAPIVIew(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = serializer.data
        return Response(data, status=status.HTTP_201_CREATED)

class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer
