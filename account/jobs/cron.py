import datetime
from apscheduler.schedulers.background import BackgroundScheduler

from account.models import Customer
from django.core.mail import send_mail


def send_email(customers, i):
    if customers[i].user.language:
        send_mail(f'Deer {customers[i].name}',
                  f'{customers[i].user.massageText}\nFor more information {customers[i].user.email}',
                  f'{customers[i].email}',
                  [f'{customers[i].email}'], fail_silently=False)
        print('English Email Sent!!!!!!')
    else:
        send_mail(f'الى {customers[i].name}',
                  f'{customers[i].user.massageText}'
                  f'\nللمزيد من المعلومات يرجى التواصل على هذا الايميل {customers[i].user.email}',
                  f'{customers[i].email}',
                  [f'{customers[i].email}'], fail_silently=False)
        print('Arabic Email Sent!!!!!!')


def test():
    print("started!!!!!!")
    customers = Customer.objects.all()
    for i in range(customers.count()):
        if customers[i].birthday.strftime('%d-%m') == datetime.date.today().strftime('%d-%m'):
            send_email(customers, i)


def start():
    s = BackgroundScheduler(timezone="Europe/Berlin")
    s.add_job(test, 'interval', seconds=10)
    s.start()
