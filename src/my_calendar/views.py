from collections import defaultdict
from datetime import datetime

import jwt
from django.contrib.auth.models import User
from django.db.models.functions import TruncDay
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from my_calendar import serializers
from my_calendar.models import Event
from my_calendar.serializers import EventSerializer, UserRegistrationSerializer, TokenObtainPairSerializer
from src import settings


# Create your views here.
class EventAPIView(APIView):
    permission_classes = [IsAuthenticated,]

    def get(self, request):
        jwt_token = request.headers.get('Authorization').split(' ')[1]
        try:
            payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
            events = Event.objects.filter(user=user_id)
            return Response({"events": EventSerializer(events, many=True).data})
        except jwt.ExpiredSignatureError:
            return Response({'error': 'JWT token has expired'}, status=status.HTTP_401_UNAUTHORIZED)

        except jwt.DecodeError:
            return Response({'error': 'JWT token is invalid'}, status=status.HTTP_401_UNAUTHORIZED)

        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


    def post(self, request):
        jwt_token = request.headers.get('Authorization').split(' ')[1]

        try:
            payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']

            data = request.data
            if not data.get('finish_date'):
                start_date = datetime.strptime(data['start_date'], '%d-%m-%Y %H:%M:%S')
                finish_date = start_date.replace(hour=23, minute=59, second=59)
                data['finish_date'] = finish_date.strftime('%d-%m-%Y %H:%M:%S')

            data['user'] = user_id
            serializer = EventSerializer(data=data)
            serializer.is_valid(raise_exception=True) #метод is_valid автоматически создаёт словарь validated_data
            serializer.save() #метод save автоматически вызывает метод create из сериализатора

            return Response({'post': serializer.data})
        except jwt.ExpiredSignatureError:
            return Response({'error': 'JWT token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.DecodeError:
            return Response({'error': 'JWT token is invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)




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
