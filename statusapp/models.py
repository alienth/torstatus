from django.db import models

class Consensus(models.Model):
    # What are we to do with this class? Will we use it?
    validafter = models.DateTimeField(primary_key=True)
    rawdesc = models.TextField()
    class Meta:
        db_table = u'consensus'
    def __unicode__(self):
        return str(self.validafter)

class Descriptor(models.Model):
    descriptor = models.CharField(max_length=40, primary_key=True)
    nickname = models.CharField(max_length=19)
    address = models.CharField(max_length=15)
    orport = models.IntegerField()
    dirport = models.IntegerField()
    fingerprint = models.CharField(max_length=40)
    bandwidthavg = models.BigIntegerField()
    bandwidthburst = models.BigIntegerField()
    bandwidthobserved = models.BigIntegerField()
    platform = models.CharField(max_length=256, blank=True)
    published = models.DateTimeField()
    uptime = models.BigIntegerField(null=True, blank=True)
    extrainfo = models.CharField(max_length=40, blank=True)
    rawdesc = models.TextField()
    class Meta:
        db_table = u'descriptor'
    def __unicode__(self):
        return self.descriptor


class Statusentry(models.Model):
    # Not to actually be used as a primary key -- not unique. 
    # However, (validafter, fingerprint) is unique!
    validafter = models.DateTimeField(primary_key=True) 
    nickname = models.CharField(max_length=19)
    fingerprint = models.CharField(max_length=40)
    descriptor = models.CharField(max_length=40)
    published = models.DateTimeField()
    address = models.CharField(max_length=15)
    orport = models.IntegerField()
    dirport = models.IntegerField()
    isauthority = models.IntegerField()
    isbadexit = models.IntegerField()
    isbaddirectory = models.IntegerField()
    isexit = models.IntegerField()
    isfast = models.IntegerField()
    isguard = models.IntegerField()
    ishsdir = models.IntegerField()
    isnamed = models.IntegerField()
    isstable = models.IntegerField()
    isrunning = models.IntegerField()
    isunnamed = models.IntegerField()
    isvalid = models.IntegerField()
    isv2dir = models.IntegerField()
    isv3dir = models.IntegerField()
    version = models.CharField(max_length=50, blank=True)
    bandwidth = models.BigIntegerField(null=True, blank=True)
    ports = models.TextField(blank=True)
    rawdesc = models.TextField()
    # descriptor_class = models.ForeignKey(Descriptor) # Obviously won't work.
    class Meta:
        unique_together = ("validafter", "fingerprint")
        db_table = u'statusentry'
    def __unicode__(self):
        return str(self.validafter) + ": " + str(self.fingerprint)

class ScheduledUpdates(models.Model):
    # We'll use this later.
    id = models.IntegerField(primary_key=True)
    date = models.DateField()
    class Meta:
        db_table = u'scheduled_updates'
    #def __unicode__(self):
        #return something ????????????????????????????????????????????

