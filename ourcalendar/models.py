from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.utils import timezone
from django.db import models
from django.conf import settings
from ourcalendar.logic.intervals import Interval
from user_accounts.models import UserProfile


class Calendar(models.Model):
    owner = models.ForeignKey(UserProfile, related_name='calendars')
    title = models.CharField(max_length=200)
    color_regex = RegexValidator(
        regex=r'^#[\dA-F]{6}',
        message="Color must be in 6-digit hex format."
    )
    color = models.CharField(max_length=7, validators=[color_regex])
    privacy = models.IntegerField(default=0)

    def __unicode__(self):
        return "%s -> %s" % (self.owner, self.title)

# TODO here to refactor to signals.py
@receiver(post_save, sender=UserProfile)
def create_calendar(sender, instance, created, **kwargs):
    if created:
        Calendar.objects.create(owner=instance, title='Default', color='#267F00')


def hour_from_now():
    return timezone.now() + timezone.timedelta(hours=1)


class Event(models.Model):
    calendar = models.ForeignKey(Calendar, related_name='events')
    title = models.CharField(max_length=200, default='New Event')
    # TODO: validate start < end
    start = models.DateTimeField(default=timezone.now)
    end = models.DateTimeField(default=hour_from_now)
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField(max_length=600, blank=True)

    DEFAULT_TIME_FMT = '%Y-%m-%dT%H:%M:%S'

    def __unicode__(self):
        return "%s -> %s -> %s" % (self.calendar.owner, self.calendar, self.title)

    # Serializes the event for the fullcalendar
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'start': self.start.strftime(getattr(settings, 'TIME_FMT',
                                                 self.DEFAULT_TIME_FMT)),
            'end': self.end.strftime(getattr(settings, 'TIME_FMT',
                                             self.DEFAULT_TIME_FMT)),
            'location': self.location,
            'description': self.description,
        }

    # Returns an Interval for comparison operations
    # TODO TEST ME
    @property
    def interval(self):
        return Interval(self.start, self.end)

    # Returns whether or not a datetime is in the range of the event
    # TODO TEST ME
    def happens_when(self, time):
        return self.start < time < self.end
