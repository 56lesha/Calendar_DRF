from django.core.management import BaseCommand

from my_calendar.models import Event


class Command(BaseCommand):
    help = "fast adding test data to db"
    def handle(self, *args, **options):
        Event.objects.all().delete()
        event_1 = Event(name="Event 1", start_date="2023-08-25 16:00:00", finish_date="2023-08-25 16:30:00", reminder="1")
        event_2 = Event(name="Event 2", start_date="2023-08-26 12:00:00", finish_date="2023-08-25 19:00:00", reminder="2")
        event_3 = Event(name="Event 3", start_date="2023-08-25 10:00:00", finish_date="2023-08-25 16:30:00", reminder="3")
        event_4 = Event(name="Event 4", start_date="2023-08-26 16:00:00", finish_date="2023-08-25 16:30:00", reminder="4")
        event_5 = Event(name="Event 5", start_date="2023-08-30 19:00:00", finish_date="2023-08-25 19:30:00", reminder="5")
        Event.objects.bulk_create([event_1, event_2, event_3, event_4, event_5])



