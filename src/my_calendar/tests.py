from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from my_calendar.models import Event


# Create your tests here.

def generate_jwt_token(user):
    token = AccessToken.for_user(user)
    return str(token)

class EventTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username="user1",
                            password="useruser")


        self.token = generate_jwt_token(self.user)
        Event.objects.create(name="Python",
                             start_date='2023-09-06 10:00:00',
                             finish_date='2023-09-06 12:00:00',
                             reminder="1",
                             user_id=1)

        Event.objects.create(name="Django",
                             start_date='2023-10-15 10:00:00',
                             finish_date='2023-10-15 20:00:00',
                             reminder="1",
                             user_id=1)
    def test_events_get_list(self):
        auth_header = 'Bearer ' + self.token
        headers = {'HTTP_AUTHORIZATION': auth_header}

        response = self.client.get(reverse('events_list'), **headers)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.data['events']), 2)
        self.assertTrue({'name': 'Python',
                         'start_date': '06-09-2023 10:00:00',
                         'finish_date': '06-09-2023 12:00:00',
                         'reminder': '1',
                         'user': 1} in response.json().get('events'))


    def test_add_event(self):
        auth_header = 'Bearer ' + self.token
        initial_count_data = Event.objects.count()
        headers = {'HTTP_AUTHORIZATION': auth_header}
        data = {
                "name": "Clean home",
                "start_date": "10-10-2023 10:00:00",
                "finish_date": "10-10-2023 14:00:00",
                "reminder": "1"
                }
        response = self.client.post(reverse('events_list'), data=data, format='json', **headers)
        final_count_data = Event.objects.count()
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(initial_count_data + 1, final_count_data)





