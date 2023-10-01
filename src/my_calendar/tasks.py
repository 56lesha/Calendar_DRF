from datetime import datetime, timedelta

from celery import shared_task
from django.core.mail import send_mail



@shared_task
def send_reminder_email(data, user_email):
    send_mail(
        f"{data['name']} at {data['start_date']}",
        f"Reminder about {data['name']} \n"
        f"Start at {data['start_date']} \n"
        f"Finish at {data['finish_date']} \n",
        "56lesha@gmail.com",
        [user_email],
    )
    print("Reminder sent successfully")










