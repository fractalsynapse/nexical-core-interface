import json
import re
from datetime import datetime

import yaml
from django.conf import settings
from django.core.management.base import BaseCommand
from django_celery_beat.models import CrontabSchedule, PeriodicTask, PeriodicTasks


class Command(BaseCommand):
    help = "Initialize schedule"

    def handle(self, *args, **options):
        with open(f"{settings.APPS_DIR}/schedule.yml") as file:
            processes = yaml.safe_load(file)

        for name, spec in processes.items():
            schedule_elements = re.split(r"\s+", spec.get("schedule", "* * * * *"))
            (schedule, created) = CrontabSchedule.objects.get_or_create(
                minute=schedule_elements[0],
                hour=schedule_elements[1] if len(schedule_elements) > 1 else "*",
                day_of_month=schedule_elements[2] if len(schedule_elements) > 2 else "*",
                month_of_year=schedule_elements[3] if len(schedule_elements) > 3 else "*",
                day_of_week=schedule_elements[4] if len(schedule_elements) > 4 else "*",
            )

            try:
                task = PeriodicTask.objects.get(name=name)
            except PeriodicTask.DoesNotExist:
                task = PeriodicTask.objects.create(name=name, crontab=schedule)

            task.enabled = spec.get("enabled", True)
            task.task = spec["task"]
            task.args = json.dumps(spec.get("args", []))
            task.kwargs = json.dumps(spec.get("kwargs", {}))
            task.priority = spec.get("priority", 10)
            task.start_time = (
                datetime.strptime(spec["start_time"], "%Y-%m-%d %H:%M") if spec.get("start_time", None) else None
            )
            task.expires = datetime.strptime(spec["expires"], "%Y-%m-%d %H:%M") if spec.get("expires", None) else None
            task.one_off = spec.get("one_off", False)
            task.save()

        PeriodicTasks.update_changed()
        self.stdout.write(self.style.SUCCESS("Successfully initialized schedule"))
