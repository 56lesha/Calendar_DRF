from collections import defaultdict
from datetime import datetime

from django.contrib.auth import get_user_model
from django.db.models.functions import TruncDay
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from my_calendar import serializers
from my_calendar.models import Event
from my_calendar.serializers import EventSerializer, UserRegistrationSerializer, LogoutSerializer


# Create your views here.
class EventAPIView(APIView):
    permission_classes = [IsAuthenticated,]

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




class EventDetailAPIView(APIView):
    permission_classes = [IsAuthenticated,]

    def check_pk(self, *args, **kwargs):
        pk = kwargs.get("pk", None)
        if not pk:
            return Response({"error": "I don't have such pk"})

        try:
            instance = Event.objects.get(pk=pk)
            return instance
        except:
            return Response({"error": "Don't have the instance"})


    def get(self, request, *args, **kwargs):
        instance = self.check_pk(*args, **kwargs)
        return Response({"event": EventSerializer(instance).data})

    def put(self, request, *args, **kwargs):
        instance = self.check_pk(*args, **kwargs)
        serializer = EventSerializer(instance=instance, data=request.data, partial=True)
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



User = get_user_model()
class UserRegistrationAPIVIew(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = serializers.UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = RefreshToken.for_user(user)
        data = serializer.data
        data['tokens'] = {"refresh": str(token), "access": str(token.access_token)}
        return Response(data, status=status.HTTP_201_CREATED)



class UserLoginAPIView(GenericAPIView):
    """
    An endpoint to authenticate existing users using their email and password.
    """

    permission_classes = (AllowAny,)
    serializer_class = serializers.UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        serializer = serializers.UserSerializer(user)
        token = RefreshToken.for_user(user)
        data = serializer.data
        data["tokens"] = {"refresh": str(token), "access": str(token.access_token)}
        return Response(data, status=status.HTTP_200_OK)


class UserLogoutAPIView(GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

