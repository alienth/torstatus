# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models

class Consensus(models.Model):
    validafter = models.DateTimeField(primary_key=True)
    rawdesc = models.TextField()
    class Meta:
        db_table = u'consensus'

class Statusentry(models.Model):
    validafter = models.DateTimeField()
    nickname = models.CharField(max_length=57)
    fingerprint = models.CharField(max_length=120, primary_key=True)
    descriptor = models.CharField(max_length=120)
    published = models.DateTimeField()
    address = models.CharField(max_length=45)
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
    version = models.CharField(max_length=150, blank=True)
    bandwidth = models.BigIntegerField(null=True, blank=True)
    ports = models.TextField(blank=True)
    rawdesc = models.TextField()

    class Meta:
        db_table = u'statusentry'
        unique_together = ("validafter", "fingerprint") # May or may not be necessary
    def __unicode__(self):
        return self.fingerprint

class Descriptor(models.Model):
    #statusentry = models.ForeignKey('Statusentry', related_name="statusapp_statusentry_related") # A guess
    descriptor = models.CharField(max_length=120, primary_key=True)
    nickname = models.CharField(max_length=57)
    address = models.CharField(max_length=45)
    orport = models.IntegerField()
    dirport = models.IntegerField()
    fingerprint = models.CharField(max_length=120)
    bandwidthavg = models.BigIntegerField()
    bandwidthburst = models.BigIntegerField()
    bandwidthobserved = models.BigIntegerField()
    platform = models.CharField(max_length=768, blank=True)
    published = models.DateTimeField()
    uptime = models.BigIntegerField(null=True, blank=True)
    extrainfo = models.CharField(max_length=120, blank=True)
    rawdesc = models.TextField()
    class Meta:
        db_table = u'descriptor'
    def __unicode__(self):
        return self.fingerprint

class ScheduledUpdates(models.Model): #what should this primary key be?
    id = models.IntegerField(primary_key=True)
    date = models.DateField()
    class Meta:
        db_table = u'scheduled_updates'

