"""
DOCUMENTATION GOES HERE

@group Custom Fields: L{BigIntegerArrayField}
@group Models: [list]
@group Custom Fields: [list]
"""

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

# We need to write our own arrays.

from django.db import models

# CUSTOM FIELDS -------------------------------------------------------
# ---------------------------------------------------------------------
class BigIntegerArrayField(models.Field):

    def db_type(self, connection):
        return 'BIGINT[]'

    def to_python(self, value):
        if isinstance(value, list):
            return value
        # Assume we can cast it as a string
        else:
            return (value.strip('[]')).split(', ')

# MODELS --------------------------------------------------------------
# ---------------------------------------------------------------------
class Descriptor(models.Model):
    """
    Model for descriptors published by routers.

    Django uses class variables to specify model fields, but these fields are
    practically used and thought of as instance variables, so this
    documentation will refer to them as such. Field types are specified as
    their Django field classes, with parentheses indicating the python type
    they are validated against and treated as. When constructing 
    a L{Descriptor} object, instance variables are specified as keyword 
    arguments in L{Descriptor} constructors.
    
    @type descriptor: CharField (str)
    @ivar descriptor: The L{Descriptor}'s unique descriptor hash.
    @type nickname: CharField (str)
    @ivar nickname: The nickname of the router that the L{Descriptor} describes.
    @type address: CharField (str)
    @ivar address: The IP address of the router that the L{Descriptor}
        describes.
    @type orport: IntegerField (int)
    @ivar orport: The ORPort of the router that the L{Descriptor} describes.
    @type dirport: IntegerField (int)
    @ivar dirport: The DirPort of the router that the L{Descriptor} describes.
    @type fingerprint: CharField (str)
    @ivar fingerprint: The fingerprint hash of the router that the L{Descriptor}
        describes.
    @type bandwidthavg: BigIntegerField (long)
    @ivar bandwidthavg: The average bandwidth of the router that the
        L{Descriptor} describes.
    @type bandwidthburst: BigIntegerField (long)
    @ivar bandwidthburst: The burst bandwidth of the router that the
        L{Descriptor} describes.
    @type bandwidthobserved: BigIntegerField (long)
    @ivar bandwidthobserved: The observed bandwidth of the router that the
        L{Descriptor} describes.
    @type platform: CharField (str)
    @ivar platform: The Tor release and the platform of the router that the
        L{Descriptor} describes.
    @type published: DateTimeField (datetime)
    @ivar published: The time that the L{Descriptor} was published.
    @type uptime: BigIntegerField (long)
    @ivar uptime: The time, in seconds, that the router that the
        L{Descriptor} describes has been continuously running.
    @type extrainfo: CharField (str)
    @ivar extrainfo: A hash that references a unique L{Extrainfo} object.
    @type rawdesc: TextField (str)
    @ivar rawdesc: Raw descriptor information that may or may not be present
        in other fields of the L{Descriptor} object
    """
    descriptorid = models.IntegerField(primary_key=True)
    descriptor = models.CharField(max_length=40, unique=True) # This field type is a guess
    nickname = models.CharField(max_length=19)
    address = models.CharField(max_length=15)
    orport = models.IntegerField()
    dirport = models.IntegerField()
    #fingerprint = models.TextField() # This field type is a guess.
    fingerprint = models.CharField(max_length=40)    
    bandwidthavg = models.BigIntegerField()
    bandwidthburst = models.BigIntegerField()
    bandwidthobserved = models.BigIntegerField()
    platform = models.CharField(max_length=256, blank=True)
    published = models.DateTimeField()
    uptime = models.BigIntegerField(blank=True)
    #extrainfo = models.TextField() # This field type is a guess.
    extrainfo= models.CharField(max_length=40, blank=True)
    rawdesc = models.TextField() # This field type is a guess.
    class Meta:
        db_table = u'descriptor'
    def __unicode__(self):
        """
        A simple string representation of the L{Descriptor} that
        consists of the L{Descriptor}'s unique hash.

        @rtype str
        @return A simple description of the L{Descriptor} object.
        """
        return self.descriptor

class Extrainfo(models.Model):
    extrainfo = models.CharField(max_length=40, primary_key=True) # This field type is a guess.
    nickname = models.CharField(max_length=19)
    fingerprint = models.CharField(max_length=40) # This field type is a guess.
    published = models.DateTimeField()
    rawdesc = models.TextField() # This field type is a guess.
    class Meta:
        verbose_name = "extra info"
        verbose_name_plural = "extra info"
        db_table = u'extrainfo'
    def __unicode__(self):
        return self.extrainfo

class Bwhist(models.Model):
    fingerprint = models.CharField(max_length=40, primary_key=True) # This field type is a guess.
    date = models.DateField()
    # Have to write own read.
    #read = models.TextField() # This field type is a guess.
    read = BigIntegerArrayField()
    read_sum = models.BigIntegerField()
    # Have to write own written.
    #written = models.TextField() # This field type is a guess.
    written = BigIntegerArrayField()
    written_sum = models.BigIntegerField()
    # Have to write own dirread
    #dirread = models.TextField() # This field type is a guess.
    dirread = BigIntegerArrayField()
    dirread_sum = models.BigIntegerField()
    # Have to write own dirwritten.
    #dirwritten = models.TextField() # This field type is a guess.
    dirwritten = BigIntegerArrayField()
    dirwritten_sum = models.BigIntegerField()
    class Meta:
        unique_together = ("fingerprint", "date")
        verbose_name = "bandwidth history"
        verbose_name_plural = "bandwidth histories"
        db_table = u'bwhist'
    def __unicode__(self):
        return str(self.date) + ": " + self.fingerprint

class Statusentry(models.Model):
    validafter = models.DateTimeField(primary_key=True)
    nickname = models.CharField(max_length=19)
    fingerprint = models.CharField(max_length=40) # This field type is a guess.
    descriptor = models.CharField(max_length=40) # This field type is a guess.
    descriptorid = models.ForeignKey(Descriptor, db_column='descriptorid')
    published = models.DateTimeField()
    address = models.CharField(max_length=15)
    orport = models.IntegerField()
    dirport = models.IntegerField()
    isauthority = models.BooleanField()
    isbadexit = models.BooleanField()
    isbaddirectory = models.BooleanField()
    isexit = models.BooleanField()
    isfast = models.BooleanField()
    isguard = models.BooleanField()
    ishsdir = models.BooleanField()
    isnamed = models.BooleanField()
    isstable = models.BooleanField()
    isrunning = models.BooleanField()
    isunnamed = models.BooleanField()
    isvalid = models.BooleanField()
    isv2dir = models.BooleanField()
    isv3dir = models.BooleanField()
    version = models.CharField(max_length=50, blank=True)
    bandwidth = models.BigIntegerField(blank=True)
    ports = models.TextField(blank=True)
    rawdesc = models.TextField() # This field type is a guess.
    class Meta:
        unique_together = ("validafter", "fingerprint")
        get_latest_by = "validafter"
        verbose_name = "status entry"
        verbose_name_plural = "status entries"
        db_table = u'statusentry'
    def __unicode__(self):
        return str(self.validafter) + ": " + self.fingerprint
    def __eq__(self, other):
        return self.fingerprint == other.fingerprint
    def __hash__(self):
        return hash(self.fingerprint)

class Consensus(models.Model):
    validafter = models.DateTimeField(primary_key=True)
    rawdesc = models.TextField() # This field type is a guess.
    class Meta:
        verbose_name = "consensus"
        verbose_name_plural = "consensuses"
        db_table = u'consensus'
    def __unicode__(self):
        return str(self.validafter)

class Vote(models.Model):
    validafter = models.DateTimeField(primary_key=True)
    dirsource = models.CharField(max_length=40) # This field type is a guess.
    rawdesc = models.TextField() # This field type is a guess.
    class Meta:
        unique_together = ("validafter", "dirsource")
        db_table = u'vote'
    def __unicode__(self):
        return str(self.validafter) + ": " + self.dirsource

class Connbidirect(models.Model):
    source = models.CharField(max_length=40, primary_key=True) # This field type is a guess.
    statsend = models.DateTimeField()
    seconds = models.IntegerField()
    belownum = models.BigIntegerField()
    readnum = models.BigIntegerField()
    writenum = models.BigIntegerField()
    bothnum = models.BigIntegerField()
    class Meta:
        unique_together = ("source", "statsend")
        verbose_name = "conn-bi-direct"
        db_table = u'connbidirect'
    def __unicode__(self):
        return self.statsend + ": " + self.source

class NetworkSize(models.Model):
    date = models.DateField(primary_key=True)
    avg_running = models.IntegerField()
    avg_exit = models.IntegerField()
    avg_guard = models.IntegerField()
    avg_fast = models.IntegerField()
    avg_stable = models.IntegerField()
    class Meta:
        db_table = u'network_size'
    def __unicode__(self):
        return str(self.date)

class NetworkSizeHour(models.Model):
    validafter = models.DateTimeField(primary_key=True)
    avg_running = models.IntegerField()
    avg_exit = models.IntegerField()
    avg_guard = models.IntegerField()
    avg_fast = models.IntegerField()
    avg_stable = models.IntegerField()
    class Meta:
        db_table = u'network_size_hour'
    def __unicode__(self):
        return str(self.validafter)

class RelayCountries(models.Model):
    date = models.DateField()
    country = models.CharField(max_length=2, primary_key=True) # This field type is a guess.
    relays = models.IntegerField()
    class Meta:
        verbose_name = "relay countries"
        verbose_name_plural = "relay countries"
        unique_together = ("date", "country")
        db_table = u'relay_countries'
    def __unicode__(self):
        return str(self.date) + ": " + self.country

class RelayPlatforms(models.Model):
    date = models.DateField(primary_key=True)
    avg_linux = models.IntegerField()
    avg_darwin = models.IntegerField()
    avg_bsd = models.IntegerField()
    avg_windows = models.IntegerField()
    avg_other = models.IntegerField()
    class Meta:
        verbose_name = "relay platforms"
        verbose_name_plural = "relay platforms"
        db_table = u'relay_platforms'
    def __unicode__(self):
        return (self.date)

class RelayVersions(models.Model):
    date = models.DateField()
    version = models.CharField(max_length=5, primary_key=True) # This field type is a guess.
    relays = models.IntegerField()
    class Meta:
        unique_together = ("date", "version")
        verbose_name = "relay versions"
        verbose_name_plural = "relay versions"
        db_table = u'relay_versions'
    def __unicode__(self):
        return self.date + ": " + self.version

class TotalBandwidth(models.Model):
    date = models.DateField(primary_key=True)
    bwavg = models.BigIntegerField()
    bwburst = models.BigIntegerField()
    bwobserved = models.BigIntegerField()
    bwadvertised = models.BigIntegerField()
    class Meta:
        db_table = u'total_bandwidth'
    def __unicode__(self):
        return self.date

class TotalBwhist(models.Model):
    date = models.DateField(primary_key=True)
    read = models.BigIntegerField()
    written = models.BigIntegerField()
    class Meta:
        verbose_name = "total bandwidth history"
        verbose_name_plural = "total bandwidth histories"
        db_table = u'total_bwhist'
    def __unicode__(self):
        return self.date

class BwhistFlags(models.Model):
    date = models.DateField(primary_key=True)
    isexit = models.BooleanField()
    isguard = models.BooleanField()
    read = models.BigIntegerField()
    written = models.BigIntegerField()
    class Meta:
        unique_together = ("date", "isexit", "isguard")
        verbose_name = "bandwidth history flags"
        verbose_name_plural = "bandwidth history flags"
        db_table = u'bwhist_flags'
    def __unicode__(self):
        return self.date + ": " + self.isexit + ", " + self.isguard

class UserStats(models.Model):
    date = models.DateField()
    country = models.CharField(max_length=2, primary_key=True) # This field type is a guess.
    r = models.BigIntegerField()
    dw = models.BigIntegerField()
    dr = models.BigIntegerField()
    drw = models.BigIntegerField()
    drr = models.BigIntegerField()
    bw = models.BigIntegerField()
    br = models.BigIntegerField()
    bwd = models.BigIntegerField()
    brd = models.BigIntegerField()
    bwr = models.BigIntegerField()
    brr = models.BigIntegerField()
    bwdr = models.BigIntegerField()
    brdr = models.BigIntegerField()
    bwp = models.BigIntegerField()
    brp = models.BigIntegerField()
    bwn = models.BigIntegerField()
    brn = models.BigIntegerField()
    class Meta:
        verbose_name = "user statistics"
        verbose_name_plural = "user statistics"
        unique_together = ("date", "country")
        db_table = u'user_stats'
    def __unicode__(self):
        return self.date + ": " + self.country

class RelayStatusesPerDay(models.Model):
    date = models.DateField(primary_key=True)
    count = models.IntegerField()
    class Meta:
        verbose_name = "relay statuses per day"
        verbose_name_plural = "relay statuses per day"
        db_table = u'relay_statuses_per_day'
    def __unicode__(self):
        return self.date

class ScheduledUpdates(models.Model):
    id = models.IntegerField(primary_key=True)
    date = models.DateField()
    class Meta:
        verbose_name = "scheduled updates"
        verbose_name_plural = "scheduled updates"
        db_table = u'scheduled_updates'
    def __unicode__(self):
        return self.date + ": " + self.id

class Updates(models.Model):
    id = models.IntegerField(primary_key=True)
    date = models.DateField()
    class Meta:
        verbose_name = "updates"
        verbose_name_plural = "updates"
        db_table = u'updates'
    def __unicode__(self):
        return self.date + ": " + self.id

class Geoipdb(models.Model):
    id = models.IntegerField(primary_key=True)
    ipstart = models.IPAddressField()
    ipend = models.IPAddressField()
    country = models.CharField(max_length=2) # This field type is a guess.
    latitude = models.DecimalField(max_digits=7, decimal_places=4)
    longitude = models.DecimalField(max_digits=7, decimal_places=4)
    class Meta:
        verbose_name = "GeoIP entry"
        verbose_name_plural = "GeoIP entries"
        db_table = u'geoipdb'
    def __unicode__(self):
        return self.ipstart + ", " + self.ipend

class RelaysMonthlySnapshots(models.Model):
    validafter = models.DateTimeField(primary_key=True)
    fingerprint = models.CharField(max_length=40) # This field type is a guess.
    nickname = models.CharField(max_length=19)
    address = models.CharField(max_length=15)
    country = models.CharField(max_length=2) # This field type is a guess.
    latitude = models.DecimalField(max_digits=7, decimal_places=4)
    longitude = models.DecimalField(max_digits=7, decimal_places=4)
    isexit = models.BooleanField()
    isfast = models.BooleanField()
    isguard = models.BooleanField()
    isstable = models.BooleanField()
    version = models.CharField(max_length=50)
    ports = models.TextField()
    bandwidthavg = models.BigIntegerField()
    bandwidthburst = models.BigIntegerField()
    bandwidthobserved = models.BigIntegerField()
    class Meta:
        unique_together = ("validafter", "fingerprint")
        verbose_name = "month of relay snapshots"
        verbose_name_plural = "months of relay snapshots"
        db_table = u'relays_monthly_snapshots'
    def __unicode__(self):
        return self.validafter + ": " + self.fingerprint

class BridgeNetworkSize(models.Model):
    date = models.DateField(primary_key=True)
    avg_running = models.IntegerField()
    class Meta:
        db_table = u'bridge_network_size'
    def __unicode__(self):
        return self.date

class DirreqStats(models.Model):
    source = models.CharField(max_length=40) # This field type is a guess.
    statsend = models.DateTimeField()
    seconds = models.IntegerField()
    country = models.CharField(max_length=2) # This field type is a guess.
    requests = models.IntegerField()
    class Meta:
        unique_together = ("source", "statsend", "seconds", "country")
        verbose_name = "dirreq stats"
        verbose_name_plural = "dirreq stats"
        db_table = u'dirreq_stats'
    def __unicode__(self):
        return self.statsend + ": " + self.country + ", " + self.source \
                + ", " + self.seconds

class BridgeStats(models.Model):
    date = models.DateField()
    country = models.CharField(max_length=2, primary_key=True) # This field type is a guess.
    users = models.IntegerField()
    class Meta:
        unique_together = ("date", "country")
        verbose_name = "bridge stats"
        verbose_name_plural = "bridge stats"
        db_table = u'bridge_stats'
    def __unicode__(self):
        return self.date + ": " + self.country

class TorperfStats(models.Model):
    date = models.DateField()
    source = models.CharField(max_length=32, primary_key=True)
    q1 = models.IntegerField()
    md = models.IntegerField()
    q3 = models.IntegerField()
    timeouts = models.IntegerField()
    failures = models.IntegerField()
    requests = models.IntegerField()
    class Meta:
        unique_together = ("date", "source")
        verbose_name = "Tor performance statistics"
        verbose_name_plural = "Tor performance statistics"
        db_table = u'torperf_stats'
    def __unicode__(self):
        return self.date + ": " + self.source

class GettorStats(models.Model):
    date = models.DateField()
    bundle = models.CharField(max_length=64, primary_key=True)
    downloads = models.IntegerField()
    class Meta:
        unique_together = ("date", "bundle")
        verbose_name = "get Tor statistics"
        verbose_name_plural = "get Tor statistics"
        db_table = u'gettor_stats'
    def __unicode__(self):
        return self.date + ": " + self.bundle
