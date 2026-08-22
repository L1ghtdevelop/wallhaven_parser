from scheduler import Scheduler
import datetime as dt
from time import sleep

class Manager:
    def __init__(self, rating) -> None:
        self.scheduler = Scheduler()
        self.rating = rating

    def shedule(self, controller):
        self.scheduler.daily(dt.time(hour=9), controller.choose_job, kwargs={"type": "parse", "rating": self.rating})
        self.scheduler.daily(dt.time(hour=10), controller.choose_job, kwargs={"type": "send", "rating": self.rating})
        self.scheduler.daily(dt.time(hour=20), controller.choose_job, kwargs={"type": "parse", "rating": self.rating})
        self.scheduler.daily(dt.time(hour=21), controller.choose_job, kwargs={"type": "send", "rating": self.rating})

    def start_job(self):
        while True:
            self.scheduler.exec_jobs()
            sleep(1)
        