from apscheduler.schedulers.background import BlockingScheduler
from app import awards, test_function, mongo
from helpers import new_comp


'''
These are the scheduled functions:
1. awards() runs automatically on Sunday at 22:00PM
2. new_comp() runs automatically on Monday at 0:00AM
'''
scheduler = BlockingScheduler()
scheduler.add_job(awards, 'cron', day_of_week='sun',
                  hour=22, minute=0, second=0,
                  start_date='2021-02-24')
scheduler.add_job(new_comp, 'cron', [mongo], day_of_week='mon',
                  hour=00, minute=0, second=0,
                  start_date='2021-02-24')
scheduler.add_job(test_function, 'cron', day_of_week='sun',
                  hour=20, minute=32, second=0,
                  start_date='2021-02-24')

scheduler.start()
