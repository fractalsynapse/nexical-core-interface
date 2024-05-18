import json

from django_celery_beat.models import CrontabSchedule, PeriodicTask


def get_task(name):
    try:
        return PeriodicTask.objects.get(name=name)
    except PeriodicTask.DoesNotExist:
        return None


def get_crontab(task):
    if not task:
        return None

    def cronexp(field):
        return field and str(field).replace(" ", "") or "*"

    return "{} {} {} {} {}".format(
        cronexp(task.crontab.minute),
        cronexp(task.crontab.hour),
        cronexp(task.crontab.day_of_month),
        cronexp(task.crontab.month_of_year),
        cronexp(task.crontab.day_of_week),
    )


def create_task(name, crontab, timezone, task_path, **kwargs):
    crontab_elements = crontab.split(" ")

    cron_schedule, _ = CrontabSchedule.objects.get_or_create(
        minute=crontab_elements[0],
        hour=crontab_elements[1],
        day_of_month=crontab_elements[2],
        month_of_year=crontab_elements[3],
        day_of_week=crontab_elements[4],
        timezone=timezone,
    )

    PeriodicTask.objects.filter(name=name).delete()
    return PeriodicTask.objects.create(name=name, task=task_path, crontab=cron_schedule, kwargs=json.dumps(kwargs))


def delete_task(name):
    PeriodicTask.objects.filter(name=name).delete()


def delete_tasks(**filters):
    PeriodicTask.objects.filter(**filters).delete()
