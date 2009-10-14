"""
This unit test checks for the most common functionality:
sending scheduled sms to a registered reporter

"""
import time
import logging
from datetime import datetime, timedelta, MINYEAR
from rapidsms.tests.scripted import TestScript
import scheduler.app as scheduler_app
from scheduler.models import EventSchedule, ALL

start = datetime(MINYEAR, 1, 1, 0, 0, 0, 0 , tzinfo=None)
sec = timedelta(seconds=1)
min = timedelta(minutes=1)
hour = timedelta(hours=1)
day = timedelta(days=1)
week = timedelta(weeks=1)

class TestApp (TestScript):
    apps = ([scheduler_app.App])
    
    def setUp(self):
        TestScript.setUp(self)
        EventSchedule.objects.all().delete()

    def test_all(self):
        schedule = EventSchedule(callback="foo", \
                                 minutes=ALL)
        self.assertTrue(schedule.should_fire(start))
        self.assertTrue(schedule.should_fire(start+sec))
        self.assertTrue(schedule.should_fire(start+min))
        self.assertTrue(schedule.should_fire(start+hour))
        self.assertTrue(schedule.should_fire(start+day))
        self.assertTrue(schedule.should_fire(start+week))

    def test_minutes(self):
        schedule = EventSchedule(callback="foo", \
                                 minutes=set([1,3,5]), 
                                 count=1)
        self.assertFalse(schedule.should_fire(start))
        self.assertFalse(schedule.should_fire(start+sec))
        self.assertTrue(schedule.should_fire(start+1*min))
        self.assertFalse(schedule.should_fire(start+2*min))
        self.assertTrue(schedule.should_fire(start+3*min))
        self.assertFalse(schedule.should_fire(start+4*min))
        self.assertTrue(schedule.should_fire(start+5*min))        
        self.assertFalse(schedule.should_fire(start+hour))
        self.assertFalse(schedule.should_fire(start+day))
        self.assertFalse(schedule.should_fire(start+week))

    def test_hours(self):
        schedule = EventSchedule(callback="foo", hours=set([3,5,23]), \
                                 minutes='*')
        self.assertFalse(schedule.should_fire(start))
        self.assertTrue(schedule.should_fire(start+3*hour))
        self.assertFalse(schedule.should_fire(start+4*hour))
        self.assertTrue(schedule.should_fire(start+5*hour))
        self.assertFalse(schedule.should_fire(start+6*hour))
        self.assertTrue(schedule.should_fire(start+23*hour))

    def test_days_of_week(self):
        """ days of week are indexed starting '0' """
        """ fire monday, friday, and sunday, at 8:15 am and 5:15 pm """
        schedule = EventSchedule(callback="foo", days_of_week=set([0,4,6]),
                                 hours=set([8,17]), \
                                 minutes=set([15]))
        self.assertFalse(schedule.should_fire(start))
        self.assertFalse(schedule.should_fire(start+5*day))
        self.assertFalse(schedule.should_fire(start+7*day))
        self.assertFalse(schedule.should_fire(start+3*hour))
        self.assertFalse(schedule.should_fire(start+5*day+7*hour))
        self.assertFalse(schedule.should_fire(start+7*day+16*hour))
        self.assertFalse(schedule.should_fire(start+8*hour+13*min))
        self.assertFalse(schedule.should_fire(start+5*day+8*hour+16*min))
        self.assertFalse(schedule.should_fire(start+7*day+8*hour+25*min))
        self.assertTrue(schedule.should_fire(start+8*hour+15*min))
        self.assertTrue(schedule.should_fire(start+17*hour+15*min))
        self.assertTrue(schedule.should_fire(start+4*day+8*hour+15*min))
        self.assertTrue(schedule.should_fire(start+6*day+17*hour+15*min))
        
    def test_days_of_month(self):
        """ days of month are indexed starting '1' """
        schedule = EventSchedule(callback="foo", days_of_month=set([1,15,30]),
                                 hours=set([10]), \
                                 minutes=set([0]))
        self.assertFalse(schedule.should_fire(start))
        self.assertTrue(schedule.should_fire(start+10*hour))
        self.assertFalse(schedule.should_fire(start+10*hour+min))
        self.assertFalse(schedule.should_fire(start+10*min))
        self.assertTrue(schedule.should_fire(start+14*day+10*hour))
        self.assertFalse(schedule.should_fire(start+14*day+9*hour))
        self.assertFalse(schedule.should_fire(start+14*day+11*hour))
        self.assertTrue(schedule.should_fire(start+29*day+10*hour))
        self.assertFalse(schedule.should_fire(start+29*day+1*min))
        self.assertFalse(schedule.should_fire(start+29*day-1*min))
    
    def test_month(self):
        """ months are indexed from '1' """
        schedule = EventSchedule(callback="foo", months=set([2]), \
                                 days_of_month='*',
                                 hours='*', \
                                 minutes='*')
        self.assertFalse(schedule.should_fire(start))
        self.assertTrue(schedule.should_fire(start+31*day))
        self.assertTrue(schedule.should_fire(start+31*day+sec))
        self.assertTrue(schedule.should_fire(start+31*day+min))
        self.assertTrue(schedule.should_fire(start+31*day+hour))
        self.assertTrue(schedule.should_fire(start+31*day+day))
        self.assertTrue(schedule.should_fire(start+31*day+sec+min+hour+day))
            
    def tearDown(self):
        pass
