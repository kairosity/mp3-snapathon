from apscheduler.schedulers.background import BackgroundScheduler
from app import awards, new_comp, test_function, mongo

'''
These are the scheduled functions:
1. awards() runs automatically on Sunday at 22:00PM
2. new_comp() runs automatically on Monday at 0:00AM
'''
scheduler = BackgroundScheduler()
scheduler.add_job(awards, 'cron', day_of_week='sun',
                  hour=22, minute=0, second=0,
                  start_date='2021-01-24 00:00:00')
scheduler.add_job(new_comp, 'cron', [mongo], day_of_week='mon',
                  hour=00, minute=0, second=0,
                  start_date='2021-01-24 00:00:00')
scheduler.add_job(test_function, 'cron', [mongo], day_of_week='sun',
                  hour=18, minute=11, second=0,
                  start_date='2021-01-24 00:00:00')

scheduler.start()