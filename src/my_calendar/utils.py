from datetime import datetime, timedelta

import jwt
from django.contrib.auth.models import User
from rest_framework import status

from rest_framework.response import Response

from src import settings


class EventHelpMixin:
    def get_user_id(self, request):
        """
        Получает id пользователя из JWT токена
        :param request:
        :return:
        """
        jwt_token = request.headers.get('Authorization').split(' ')[1]
        try:
            payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
            return user_id

        except jwt.ExpiredSignatureError:
            return Response({'error': 'JWT token has expired'}, status=status.HTTP_401_UNAUTHORIZED)

        except jwt.DecodeError:
            return Response({'error': 'JWT token is invalid'}, status=status.HTTP_401_UNAUTHORIZED)

        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


    def auto_finish_date(self, data):
        if not data.get('finish_date'):
            start_date = datetime.strptime(data['start_date'], '%d-%m-%Y %H:%M:%S')
            finish_date = start_date.replace(hour=23, minute=59, second=59)
            data['finish_date'] = finish_date.strftime('%d-%m-%Y %H:%M:%S')
            return data

    def set_reminder(self, data):
        reminders = {
            "1": 1,
            "2": 2,
            "3": 4,
            "4": 24,
            "5": 168
        }
        start_date = datetime.strptime(data["start_date"], '%d-%m-%Y %H:%M:%S')
        reminder_time = start_date - timedelta(hours=reminders[data["reminder"]]) - timedelta(hours=3)
        return reminder_time






