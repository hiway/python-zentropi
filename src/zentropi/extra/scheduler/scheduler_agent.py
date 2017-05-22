# coding=utf-8

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from pytz import utc
from zentropi import Agent, on_event, on_message, run_agents

jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}
executors = {
    'default': {'type': 'threadpool', 'max_workers': 20},
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}


class SchedulerAgent(Agent):
    def __init__(self, name=None):
        super().__init__(name=name)
        self.scheduler = AsyncIOScheduler()
        self.scheduler.configure(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)

    @on_event('*** started')
    def startup(self, event):
        self.scheduler.start()

    @on_event('*** stopping')
    def shutdown(self, event):
        self.scheduler.shutdown()

    @on_event('scheduler-add-cron')
    @on_event('scheduler-add-date')
    def add_job(self, event):
        print('&&&&&&&&&&7')
        from zentropi.utils import scheduler_emit
        name = event.data.event_name
        data = event.data.event_data
        space = event.data.event_space
        cron = event.data.cron
        run_date = event.data.run_date
        if not name:
            self.emit('scheduler-error', data={'text': 'Expected name in data'})
            return
        if event.name.endswith('cron'):
            if not cron:
                self.emit('scheduler-error', data={'text': 'Expected cron in data'})
                return
            trigger = CronTrigger(**cron)
            self.scheduler.add_job(func=scheduler_emit, trigger=trigger,
                                   kwargs={'name': name, 'data': data, 'space': space})
        elif event.name.endswith('date'):
            if not run_date:
                self.emit('scheduler-error', data={'text': 'Expected run_date in data'})
                return
            self.scheduler.add_job(scheduler_emit, 'date', run_date=run_date,
                                   kwargs={'name': name, 'data': data, 'space': space})
        else:
            self.emit('scheduler-error', data={'text': 'Unexpected name: {!r}'.format(event.name)})
            return
        print('*** add job: {!r}: {!r}'.format(name, data))

    @on_event('scheduler-pause')
    def pause_job(self, event):
        print('*** pause job: {!r}: {!r}'.format(event.name, event.data))

    @on_event('scheduler-resume')
    def resume_job(self, event):
        print('*** resume job: {!r}: {!r}'.format(event.name, event.data))

    @on_event('scheduler-remove')
    def remove_job(self, event):
        print('*** remove job: {!r}: {!r}'.format(event.name, event.data))

    @on_event('scheduler-jobs')
    def list_jobs(self, event):
        print('*** list jobs: {!r}: {!r}'.format(event.name, event.data))

