from django.db import models
from apps.reporters.models import Location, Reporter, PersistantConnection


class NetDistribution(models.Model):
    reporter = models.ForeignKey(Reporter, null=True, blank=True)
    connection = models.ForeignKey(PersistantConnection, null=True, blank=True)
    location = models.ForeignKey(Location)
    time = models.DateTimeField()
    distributed = models.PositiveIntegerField()
    expected = models.PositiveIntegerField()
    actual = models.PositiveIntegerField()
    discrepancy = models.PositiveIntegerField()
    
    @staticmethod
    def get_totals(location):
        all = NetDistribution.objects.all().filter(location=location)
        distributed = 0
        expected = 0
        actual= 0
        discrepancy = 0
        for report in all:
            distributed += report.distributed
            expected += report.expected
            actual += report.actual
            discrepancy += report.discrepancy 
        return {"distributed":distributed, 
                "expected":expected,
                "actual":actual,
                "discrepancy":discrepancy }
        
    def __unicode__(self):
        return "%s reported net distribution at %s.  distributed=%s, expected=%s, actual=%s, discrepancy=%s" %(self.reporter, 
                                                                        self.location, 
                                                                        self.distributed, 
                                                                        self.expected, 
                                                                        self.actual, 
                                                                        self.discrepancy)

class CardDistribution(models.Model):
    reporter = models.ForeignKey(Reporter, null=True, blank=True)
    connection = models.ForeignKey(PersistantConnection, null=True, blank=True)
    location = models.ForeignKey(Location)
    time = models.DateTimeField()
    settlements = models.PositiveIntegerField()
    people = models.PositiveIntegerField()
    distributed = models.PositiveIntegerField()
    
    @staticmethod
    def get_totals(location):
        all = CardDistribution.objects.all().filter(location=location)
        settlements = 0
        people = 0
        distributed= 0
        for report in all:
            settlements += report.settlements
            people += report.people
            distributed += report.distributed
        return {"settlements":settlements, 
                "people":people,
                "distributed":distributed
    }
                
    
    def __unicode__(self):
        return "%s reported net card distribution at %s.  settlements=%s, people=%s, cards=%s" %(self.reporter, 
                                                                        self.location, 
                                                                        self.settlements, 
                                                                        self.people, 
                                                                        self.distributed)

# this is a signal that says that whenever a location is loaded,
# if these models have also been loaded we should try to set the 
# data for nets and net cards distributed in that location
def loc_nets_cards_post_init(sender, **kwargs):
    """Location post init signal that reads the net and net card information from the 
       models and sets it in the location object, if it is defined"""
    instance = kwargs["instance"]
    instance.net_data =  NetDistribution.get_totals(instance)
    instance.card_data =  CardDistribution.get_totals(instance)
    

# this is the magic that glues the signal to the post load call
models.signals.post_init.connect(loc_nets_cards_post_init, sender=Location)
