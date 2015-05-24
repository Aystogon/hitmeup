from django.contrib.contenttypes.models import ContentType
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.utils import timezone
from django.db import models
from django.conf import settings
import itertools
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

    def get_between(self, range_start, range_end):
        itertools.chain([e.get_between(range_start, range_end) for e in self.events.all()])

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
#TODO: How do we link event to recurring so that when we make an event, we also make a recurring?
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
    @property
    def as_interval(self):
        return Interval(self.start, self.end)

    # Returns whether or not a datetime is in the range of the event
    def happens_when(self, time):
        return self.start < time < self.end

    def get_between(self, range_start, range_end):
        return self.recurrence_type.get_between(range_start, range_end)

'''
# This is using abstract, don't really know how to implement
class RecurrenceType(models.Model):

    class Meta:
        abstract = True

    event = models.ForeignKey(Event, related_name="recurrence_type")

    ''
    Website used to let us call get_between of the respective subtype
    http://stackoverflow.com/questions/929029/how-do-i-access-the-child-classes-of-an-object-in-django-without-knowing-the-name/929982#929982
    ''
    #TODO in the comments he says we should use inheritance manager but that would mean we would have to do concrete inheritance. thoughts?
    real_type = models.ForeignKey(ContentType, editable=False)

    def _get_real_type(self):
        return ContentType.objects.get_for_model(type(self))

    def cast(self):
        return self.real_type.get_object_for_this_type(pk=self.pk)

    def get_between(self, range_start, range_end):
        raise NotImplementedError("Recurrence Type not implemented!!")
'''


class RecurrenceType(models.Model):

   # event = models.OneToOneField(Event, primary_key=True, related_name="recurrence_type")
    event = models.OneToOneField(Event, primary_key=True)
    def get_between(self, range_start, range_end):
        raise NotImplementedError("Recurrence Type not implemented!!")

    def __unicode__(self):
        return "%s -> RecurrenceType" % (self.event)


class SingleRecurrence(RecurrenceType):
    #If it's just a single event, we just have to make one check
    def get_between(self, range_start, range_end):
        if self.event.start < range_end and self.event.end > range_start:
            return self.event

    def __unicode__(self):
        return "%s -> SingleRecurrenceType" % self.event

'''
def find_last_occurrence():
    print("hi")
    return timezone.now()
'''
def find_last_occurrence(time, frequency, total_number, days_of_week):
    print(days_of_week)
    return 1

class WeeklyRecurrence(RecurrenceType):
    #TODO: Make sure that the length is only 7!
    days_of_week = models.CommaSeparatedIntegerField(default=[0,0,0,0,0,0,0], max_length=13)
    # The number of weeks between each occurrence
    frequency = models.IntegerField(default=1)
    total_number = models.IntegerField(default=1)
    end = models.DateTimeField(default=find_last_occurrence(event.end,
                        frequency, total_number, days_of_week)) #TODO: Question : why can't this be self?
    #end = models.DateTimeField(default=find_last_occurrence)

    def get_between(self, range_start, range_end):
        if self.event.start < range_end and self.event.end > range_start:
            return self.event

    def __unicode__(self):
        return "%s -> WeeklyRecurrenceType" % self.event



