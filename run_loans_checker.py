import schedule
import time
import os

def run_check_loans():
    os.system('python manage.py check_loans')

# Запускаємо раз на день о 21:00
schedule.every(1).minutes.do(run_check_loans)

while True:
    schedule.run_pending()
    time.sleep(60)
