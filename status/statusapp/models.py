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
    
    @type descriptorid: IntegerField (C{int})
    @ivar descriptorid: An auto-incrementing index.
    @type descriptor: CharField (C{string})
    @ivar descriptor: The L{Descriptor}'s unique descriptor hash.
    @type nickname: CharField (C{string})
    @ivar nickname: The nickname of the router that the L{Descriptor} describes.
    @type address: CharField (C{string})
    @ivar address: The IP address of the router that the L{Descriptor}
        describes.
    @type orport: IntegerField (C{int})
    @ivar orport: The ORPort of the router that the L{Descriptor} describes.
    @type dirport: IntegerField (C{int})
    @ivar dirport: The DirPort of the router that the L{Descriptor} describes.
    @type fingerprint: CharField (C{string})
    @ivar fingerprint: The fingerprint hash of the router that the L{Descriptor}
        describes.
    @type bandwidthavg: BigIntegerField (C{long})
    @ivar bandwidthavg: The average bandwidth of the router that the
        L{Descriptor} describes.
    @type bandwidthburst: BigIntegerField (C{long})
    @ivar bandwidthburst: The burst bandwidth of the router that the
        L{Descriptor} describes.
    @type bandwidthobserved: BigIntegerField (C{long})
    @ivar bandwidthobserved: The observed bandwidth of the router that the
        L{Descriptor} describes.
    @type platform: CharField (C{string})
    @ivar platform: The Tor release and the platform of the router that the
        L{Descriptor} describes.
    @type published: DateTimeField (C{datetime})
    @ivar published: The time that the L{Descriptor} was published.
    @type uptime: BigIntegerField (C{long})
    @ivar uptime: The time, in seconds, that the router that the
        L{Descriptor} describes has been continuously running.
    @type extrainfo: CharField (C{string})
    @ivar extrainfo: A hash that references a unique L{Extrainfo} object.
    @type rawdesc: TextField (C{string})
    @ivar rawdesc: Raw descriptor information that may or may not be present
        in other fields of the L{Descriptor} object
    """
    descriptorid = models.IntegerField(primary_key=True)
    descriptor = models.CharField(max_length=40, primary_key=True) # This field type is a guess
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
    """
    Model for extrainfo published by routers.

    Django uses class variables to specify model fields, but these fields are
    practically used and thought of as instance variables, so this
    documentation will refer to them as such. Field types are specified as
    their Django field classes, with parentheses indicating the python type
    they are validated against and treated as. When constructing 
    an L{Extrainfo} object, instance variables are specified as keyword 
    arguments in L{Extrainfo} constructors.

    @type extrainfo: CharField (C{string})
    @ivar extrainfo: The L{Extrainfo} object's unique extrainfo hash.
    @type nickname: Charfield (C{string})
    @ivar nickname: The nickname of the router that the L{Extrainfo} object
        describes.
    @type fingerprint: Charfield (C{string})
    @ivar fingerprint: The fingerprint hash of the router that the 
        L{Extrainfo} object describes.
    @type published: DateTimeField (C{string})
    @ivar published: The time that the L{Extrainfo} object was published.
    @type rawdesc: TextField (C{string})
    @ivar rawdesc: Raw descriptor information that may or may not be present
        in other fields of the L{Extrainfo} object or the L{Descriptor}
        object that references it.
    """
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
    """
    Model for the bandwidth history of the routers.
    
    Contains bandwidth histories reported by relays in extra-info descriptors.
    Each row contains the reported bandwidth in 15-minute intervals for
    each relay and date.

    All bandwidth values are given in bytes per second.

    Django uses class variables to specify model fields, but these fields are
    practically used and thought of as instance variables, so this
    documentation will refer to them as such. Field types are specified as
    their Django field classes, with parentheses indicating the python type
    they are validated against and treated as. When constructing 
    a L{Bwhist} object, instance variables are specified as keyword 
    arguments in L{Bwhist} constructors.

    @type fingerprint: CharField (C{string})
    @ivar fingerprint: The fingerprint hash of the router that the L{Bwhist}
        object describes.
    @type date: DateField (C{datetime})
    @ivar date: The date that the L{Bwhist} object was published.
    @type read: BigIntegerArrayField (C{list})
    @ivar read: The reported reading bandwidth as an array.
    @type read_sum: BigIntegerField (C{long})
    @ivar read_sum: The sum of the reported reading bandwidth.
    @type written: BigIntegerArrayField (C{list})
    @ivar written: The reported writing bandwidth as an array.
    @type written_sum: BigIntegerField (C{long})
    @ivar written_sum: The sum of the reported writing bandwidth.
    @type dirread: BigIntegerArrayField (C{list})
    @ivar dirread: The reported directory reading bandwidth as an array.
    @type dirread_sum: BigIntegerField (C{long})
    @ivar dirread_sum: The sum of the reported directory reading bandwidth.
    @type dirwritten: BigIntegerArrayField (C{list})
    @ivar dirwritten: The reported directory writing bandwidth as an array.
    @type dirwritten_sum: BigIntegerField (C{long})
    @ivar dirwritten_sum: The sum of the reported directory writing bandwidth.
    """
    fingerprint = models.CharField(max_length=40, primary_key=True) # This field type is a guess.
    date = models.DateField()
    read = BigIntegerArrayField()
    read_sum = models.BigIntegerField()
    written = BigIntegerArrayField()
    written_sum = models.BigIntegerField()
    dirread = BigIntegerArrayField()
    dirread_sum = models.BigIntegerField()
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
    """
    Model for the status entries of the routers.

    Contains all of the consensus entries published by the directories.
    Each statusentry references a valid descriptor, though the descriptor
    may or may not be published yet.

    Django uses class variables to specify model fields, but these fields are
    practically used and thought of as instance variables, so this
    documentation will refer to them as such. Field types are specified as
    their Django field classes, with parentheses indicating the python type
    they are validated against and treated as. When constructing 
    a L{Bwhist} object, instance variables are specified as keyword 
    arguments in L{Bwhist} constructors.

    @type validafter: DateTimeField (C{datetime})
    @ivar validafter: The time that the consensus was published.
    @type nickname: CharField (C{string})
    @ivar nickname: The nickname of the router that the L{Statusentry}
        describes.
    @type fingerprint: CharField (C{string})
    @ivar fingerprint: The unique fingerprint hash of the router that the
        L{Statusentry} describes.
    @type descriptor: CharField (C{string})
    @ivar descriptor: The unique descriptor hash of the router that the
        L{Statusentry} describes. References an entry in the L{Descriptor}
        table, but this entry may or may not be added to the table yet.
    @type descriptorid: ForeignKey
    @ivar descriptorid: References a L{Descriptor} object or is null.
    @type published: DateTimeField (C{datetime})
    @ivar published: The time that the entry was published.
    @type address: CharField (C{string})
    @ivar address: The IP address of the relay that the L{Statusentry}
        describes.
    @type orport: IntegerField (C{int})
    @ivar orport: The ORPort of the relay that the L{Statusentry} describes.
    @type dirport: IntegerField (C{int})
    @ivar dirport: The DirPort of the relay that the L{Statusentry} describes.
    @type isauthority: BooleanField (C{boolean})
    @ivar isauthority: True if the relay is an authority relay,
        False otherwise.
    @type isbadexit: BooleanField (C{boolean})
    @ivar isbadexit: True if the relay is a bad exit node, False otherwise.
    @type isbaddirectory: BooleanField (C{boolean})
    @ivar isbaddirectory: True if the relay is a bad directory node,
        False otherwise.
    @type isexit: BooleanField (C{boolean})
    @ivar isexit: True if the relay is an exit relay, False otherwise.
    @type isfast: BooleanField (C{boolean})
    @ivar isfast: True if the relay is a fast server, False otherwise.
    @type isguard: BooleanField (C{boolean})
    @ivar isguard: True if the relay is a guard server, False otherwise.
    @type ishsdir: BooleanField (C{boolean})
    @ivar ishsdir: True if the relay is a high-speed directory, 
        False otherwise.
    @type isnamed: BooleanField (C{boolean})
    @ivar isnamed: True if the relay's name has been validated,
        False otherwise.
    @type isstable: BooleanField (C{boolean})
    @ivar isstable: True if the relay is stable, False otherwise.
    @type isrunning: BooleanField (C{boolean})
    @ivar isrunning: True if the relay is running at the time that the
        L{Statusentry} is published, False otherwise.
    @type isunnamed: BooleanField (C{boolean})
    @ivar isunnamed: True if the relay is unnamed, False otherwise.
    @type isvalid: BooleanField (C{boolean})
    @ivar isvalid: True if the relay is valid, False otherwise.
    @type isv2dir: BooleanField (C{boolean})
    @ivar isv2dir: True if the relay is a v2 directory, False otherwise.
    @type isv3dir: BooleanField (C{boolean})
    @ivar isv3dir: True if the relay is a v3 directory, False otherwise.
        As of 06-20-2011, there are not yet any v3 directories.
    @type version: CharField (C{string})
    @ivar version: The version of Tor that the relay is running.
    @type bandwidth: BigIntegerField (C{long})
    @ivar bandwidth: The bandwidth of the relay in bytes per second.
    @type ports: TextField (C{string})
    @ivar ports: The ports that the relay does or does not allow exiting to.
        Includes the keywords "reject" and "accept".
    @type rawdesc: TextField (C{string})
    @ivar rawdesc: The raw descriptor information associated with the
        L{Statusentry}, which may or may not contain information published
        elsewhere.
    """
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

class Consensus(models.Model):
    """
    Model for the consensuses published by the directories.

    Django uses class variables to specify model fields, but these fields are
    practically used and thought of as instance variables, so this
    documentation will refer to them as such. Field types are specified as
    their Django field classes, with parentheses indicating the python type
    they are validated against and treated as. When constructing 
    a L{Consensus} object, instance variables are specified as keyword 
    arguments in L{Consensus} constructors.

    @type validafter: DateTimeField (C{datetime})
    @ivar validafter: The date that the L{Consensus} object was published.
    @type rawdesc: TextField (C{string})
    @ivar rawdesc: The raw descriptor of the consensus object.
    """
    validafter = models.DateTimeField(primary_key=True)
    rawdesc = models.TextField() # This field type is a guess.
    class Meta:
        verbose_name = "consensus"
        verbose_name_plural = "consensuses"
        db_table = u'consensus'
    def __unicode__(self):
        return str(self.validafter)

class Vote(models.Model):
    """
    Model for the votes published by the directories.

    Django uses class variables to specify model fields, but these fields are
    practically used and thought of as instance variables, so this
    documentation will refer to them as such. Field types are specified as
    their Django field classes, with parentheses indicating the python type
    they are validated against and treated as. When constructing 
    a L{Vote} object, instance variables are specified as keyword 
    arguments in L{Vote} constructors.

    @type validafter: DateTimeField (C{datetime})
    @ivar validafter: The validafter date that corresponds to a validafter
        date in a L{Consensus} object.
    @type dirsource: CharField (C{string})
    @ivar dirsource: The source of the directory that publishes the L{Vote}
        object.
    @type rawdesc: TextField (C{string})
    @ivar rawdesc: The raw descriptor associated with the L{Vote} object.
    """
    validafter = models.DateTimeField(primary_key=True)
    dirsource = models.CharField(max_length=40) # This field type is a guess.
    rawdesc = models.TextField() # This field type is a guess.
    class Meta:
        unique_together = ("validafter", "dirsource")
        db_table = u'vote'
    def __unicode__(self):
        return str(self.validafter) + ": " + self.dirsource

class Connbidirect(models.Model):
    #TODO: I have no idea what this does.
    """
    """
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
        return str(self.statsend) + ": " + self.source

class NetworkSize(models.Model):
    """
    Model for the size of the network.

    Django uses class variables to specify model fields, but these fields are
    practically used and thought of as instance variables, so this
    documentation will refer to them as such. Field types are specified as
    their Django field classes, with parentheses indicating the python type
    they are validated against and treated as. When constructing 
    a L{NetworkSize} object, instance variables are specified as keyword 
    arguments in L{NetworkSize} constructors.

    @type date: DateField (C{datetime})
    @ivar date: The date that corresponds to the averages given by the rest
        of the fields of the L{NetworkSize} object.
    @type avg_running: IntegerField (C{int})
    @ivar avg_running: The average number of running relays in the network.
    @type avg_exit: IntegerField (C{int})
    @ivar avg_exit: The average number of exit relays in the network.
    @type avg_guard: IntegerField (C{int})
    @ivar avg_guard: The average number of guard relays in the network.
    @type avg_fast: IntegerField (C{int})
    @ivar avg_fast: The average number of fast relays in the network.
    @type avg_stable: IntegerField (C{int})
    @ivar avg_stable: The average number of stable relays in the network.
    """
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
    """
    Model for the size of the network with respect to a certain validafter
    date that corresponds to the validafter dates found in L{Descriptor},
    L{Statusentry}, L{Consensus}, and L{Vote} objects.

    Django uses class variables to specify model fields, but these fields are
    practically used and thought of as instance variables, so this
    documentation will refer to them as such. Field types are specified as
    their Django field classes, with parentheses indicating the python type
    they are validated against and treated as. When constructing 
    a L{NetworkSizeHour} object, instance variables are specified as keyword 
    arguments in L{NetworkSizeHour} constructors.

    @type validafter: DateField (C{datetime})
    @ivar validafter: The hour that corresponds to the network size.
    @type avg_running: IntegerField (C{int})
    @ivar avg_running: The average number of running relays in the network.
    @type avg_exit: IntegerField (C{int})
    @ivar avg_exit: The average number of exit relays in the network.
    @type avg_guard: IntegerField (C{int})
    @ivar avg_guard: The average number of guard relays in the network.
    @type avg_fast: IntegerField (C{int})
    @ivar avg_fast: The average number of fast relays in the network.
    @type avg_stable: IntegerField (C{int})
    @ivar avg_stable: The average number of stable relays in the network.
    """
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
    """
    Model for the number of relays active from a given country on 
    a given date.

    Django uses class variables to specify model fields, but these fields are
    practically used and thought of as instance variables, so this
    documentation will refer to them as such. Field types are specified as
    their Django field classes, with parentheses indicating the python type
    they are validated against and treated as. When constructing 
    a L{RelayCountries} object, instance variables are specified as keyword 
    arguments in L{RelayCountries} constructors.

    @type date: DateField (C{datetime})
    @ivar date: The date that the L{RelayCountries} object refers to.
    @type country: CharField (C{datetime})
    @ivar country: The two letter country code that the L{RelayCountries}
        object refers to.
    @type relays: IntegerField (C{int})
    @ivar relays: The number of relays active from a given L{country} on 
        a given L{date}.
    """
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
    """
    Model for the number of relays active running on a given platform on 
    a given date.

    Django uses class variables to specify model fields, but these fields are
    practically used and thought of as instance variables, so this
    documentation will refer to them as such. Field types are specified as
    their Django field classes, with parentheses indicating the python type
    they are validated against and treated as. When constructing 
    a L{RelayPlatforms} object, instance variables are specified as keyword 
    arguments in L{RelayPlatforms} constructors.

    @type date: DateField (C{datetime})
    @ivar date: The date that corresponds to the L{RelayPlatforms} object.
    @type avg_linux: IntegerField (C{int})
    @ivar avg_linux: The average number of relays in the network running
        Linux.
    @type avg_darwin: IntegerField (C{int})
    @ivar avg_darwin: The average number of relays in the network running
        Darwin/OSX
    @type avg_bsd: IntegerField (C{int})
    @ivar avg_bsd: The average number of relays in the network running BSD.
    @type avg_windows: IntegerField (C{int})
    @ivar avg_windows: The average number of relays in the network running
        Windows.
    @type avg_other: IntegerField (C{int})
    @ivar avg_other: The average number of relays in the network running
        on a platform that is not Linux, Darwin/OSX, BSD, or Windows.
    """
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
        return str(self.date)

class RelayVersions(models.Model):
    """
    Model for the number of relays running a given version of Tor with
    respect to a certain date.

    Django uses class variables to specify model fields, but these fields are
    practically used and thought of as instance variables, so this
    documentation will refer to them as such. Field types are specified as
    their Django field classes, with parentheses indicating the python type
    they are validated against and treated as. When constructing 
    a L{RelayVersions} object, instance variables are specified as keyword 
    arguments in L{RelayVersions} constructors.

    @type date: DateField (C{datetime})
    @ivar date: The date that corresponds to the L{RelayVersions} object.
    @type version: CharField (C{string})
    @ivar version: The version of Tor that is being run by L{relays} on a
        given L{date}.
    @type relays: IntegerField (C{int})
    @ivar relays: The number of relays running a given version of Tor with
        respect to a given date.
    """
    date = models.DateField()
    version = models.CharField(max_length=5, primary_key=True) # This field type is a guess.
    relays = models.IntegerField()
    class Meta:
        unique_together = ("date", "version")
        verbose_name = "relay versions"
        verbose_name_plural = "relay versions"
        db_table = u'relay_versions'
    def __unicode__(self):
        return str(self.date) + ": " + self.version

class TotalBandwidth(models.Model):
    """
    Model for the whole network's total bandwidth, which is also in the
    bandwidth graphs.

    Django uses class variables to specify model fields, but these fields are
    practically used and thought of as instance variables, so this
    documentation will refer to them as such. Field types are specified as
    their Django field classes, with parentheses indicating the python type
    they are validated against and treated as. When constructing 
    a L{TotalBandwidth} object, instance variables are specified as keyword 
    arguments in L{TotalBandwidth} constructors.

    @type date: DateField (C{string})
    @ivar date: The date that corresponds to the L{TotalBandwidth} object.
    @type bwavg: BigIntegerField (C{long})
    @ivar bwavg: The average bandwidth of the network.
    @type bwburst: BigIntegerField (C{long})
    @ivar bwburst: The average burst bandwidth of the network.
    @type bwobserved: BigIntegerField (C{long})
    @ivar bwobserved: The average observed bandwidth of the network.
    @type bwadvertised: BigIntegerField (C{long})
    @ivar bwadvertised: The advertised bandwidth of the network.
    """
    date = models.DateField(primary_key=True)
    bwavg = models.BigIntegerField()
    bwburst = models.BigIntegerField()
    bwobserved = models.BigIntegerField()
    bwadvertised = models.BigIntegerField()
    class Meta:
        db_table = u'total_bandwidth'
    def __unicode__(self):
        return str(self.date)

class TotalBwhist(models.Model):
    """
    Model for the total number of read/written and the number of dir bytes
    read/written by all relays in the network on a given day. The dir bytes
    are an estimate based on the subset of relays that count dir bytes.

    Django uses class variables to specify model fields, but these fields are
    practically used and thought of as instance variables, so this
    documentation will refer to them as such. Field types are specified as
    their Django field classes, with parentheses indicating the python type
    they are validated against and treated as. When constructing 
    a L{TotalBwhist} object, instance variables are specified as keyword 
    arguments in L{TotalBwhist} constructors.

    @type date: DateField (C{datetime})
    @ivar date: The date that corresponds to the L{TotalBwhist} object.
    @type read: BigIntegerField (C{long})
    @ivar read: The total number of dir bytes that are read by all relays
        on the given date.
    @type written: BigIntegerField (C{long})
    @ivar written: The total number of dir bytes that are written by all
        relays on the given date.
    """
    date = models.DateField(primary_key=True)
    read = models.BigIntegerField()
    written = models.BigIntegerField()
    class Meta:
        verbose_name = "total bandwidth history"
        verbose_name_plural = "total bandwidth histories"
        db_table = u'total_bwhist'
    def __unicode__(self):
        return str(self.date)

class BwhistFlags(models.Model):
    #TODO: Add documentation. I don't know what this object/table means.
    """
    """
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
        return str(self.date) + ": " + self.isexit + ", " + self.isguard

class UserStats(models.Model):
    #TODO: Don't know what each field means, guessing:
    # read, directory write, directory read, d r/w, ?, ...
    # @see LINES 652- here: https://gitweb.torproject.org/metrics-web.git/
    # blob/HEAD:/db/tordir.sql
    """
    Model for the aggregate statistics on directory requests and byte 
    histories used to estimate user numbers.

    Django uses class variables to specify model fields, but these fields are
    practically used and thought of as instance variables, so this
    documentation will refer to them as such. Field types are specified as
    their Django field classes, with parentheses indicating the python type
    they are validated against and treated as. When constructing 
    a L{UserStats} object, instance variables are specified as keyword 
    arguments in L{UserStats} constructors.

    @type date: DateField (C{datetime})
    @ivar date: The date that corresponds to the L{UserStats} object.
    @type country: CharField (C{string})
    @ivar country: The country that corresponds to the L{UserStats} object.
    @type r:
    @ivar r:
    @type dw:
    @ivar dw: Dir written
    @type dr:
    @ivar dr: Dir read
    @type drw:
    @ivar drw: Directory requests written
    @type drr:
    @ivar drr: Director requests read
    @type bw:
    @ivar br: 
    @type bwd:
    @ivar bwd:
    @type brd:
    @ivar brd:
    @type bwr:
    @ivar bwr:
    @type brr:
    @ivar brr:
    @type bwdr:
    @ivar bwdr:
    @type brdr:
    @ivar brdr:
    @type bwp:
    @ivar bwp:
    @type brp:
    @ivar brp:
    @type bwn:
    @ivar bwn:
    @type brn:
    @ivar brn:
    """
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
        return str(self.date) + ": " + self.country

class RelayStatusesPerDay(models.Model):
    # TODO: What is count used for?
    """
    Model for the helper table which is used to update the other tables.

    Django uses class variables to specify model fields, but these fields are
    practically used and thought of as instance variables, so this
    documentation will refer to them as such. Field types are specified as
    their Django field classes, with parentheses indicating the python type
    they are validated against and treated as. When constructing 
    a L{RelayStatusesPerDay} object, instance variables are specified as 
    keyword arguments in L{RelayStatusesPerDay} constructors.

    @type date: DateField (C{datetime})
    @ivar date: The date that corresponds to the L{RelayStatusesPerDay}
        object.
    @type count: IntegerField (C{datetime})
    @ivar count: 
    """
    date = models.DateField(primary_key=True)
    count = models.IntegerField()
    class Meta:
        verbose_name = "relay statuses per day"
        verbose_name_plural = "relay statuses per day"
        db_table = u'relay_statuses_per_day'
    def __unicode__(self):
        return str(self.date)

class ScheduledUpdates(models.Model):
    """
    Model for the dates to be included in the next refresh run.

    Django uses class variables to specify model fields, but these fields are
    practically used and thought of as instance variables, so this
    documentation will refer to them as such. Field types are specified as
    their Django field classes, with parentheses indicating the python type
    they are validated against and treated as. When constructing 
    a L{ScheduledUpdates} object, instance variables are specified as 
    keyword arguments in L{ScheduledUpdates} constructors.

    @type id: IntegerField (C{int})
    @ivar id: The index of the L{ScheduledUpdates} object.
    @type date: DateField (C{datetime})
    @ivar date: The date that corresponds to the L{ScheduledUpdates} object.
    """
    id = models.IntegerField(primary_key=True)
    date = models.DateField()
    class Meta:
        verbose_name = "scheduled updates"
        verbose_name_plural = "scheduled updates"
        db_table = u'scheduled_updates'
    def __unicode__(self):
        return str(self.date) + ": " + self.id

class Updates(models.Model):
    """
    Model for the dates in the current refresh run.

    Django uses class variables to specify model fields, but these fields are
    practically used and thought of as instance variables, so this
    documentation will refer to them as such. Field types are specified as
    their Django field classes, with parentheses indicating the python type
    they are validated against and treated as. When constructing 
    an L{Updates} object, instance variables are specified as 
    keyword arguments in L{Updates} constructors.

    @type id: IntegerField (C{int})
    @ivar id: The index of the L{Updates} object.
    @type date: DateField (C{datetime})
    @ivar date: The date that corresponds to the L{Updates} object.
    """
    id = models.IntegerField(primary_key=True)
    date = models.DateField()
    class Meta:
        verbose_name = "updates"
        verbose_name_plural = "updates"
        db_table = u'updates'
    def __unicode__(self):
        return str(self.date) + ": " + self.id

class Geoipdb(models.Model):
    """
    Model for the GeoIP database that resolves IP addresses to country
    codes, latitudes, and longitudes.

    Django uses class variables to specify model fields, but these fields are
    practically used and thought of as instance variables, so this
    documentation will refer to them as such. Field types are specified as
    their Django field classes, with parentheses indicating the python type
    they are validated against and treated as. When constructing 
    a L{Geoipdb} object, instance variables are specified as 
    keyword arguments in L{Geoipdb} constructors.

    @type id: IntegerField (C{int})
    @ivar id: The index associated with the L{Geoipdb} object.
    @type ipstart: IPAddressField (C{string})
    @ivar ipstart: The lower bound of an IP address associated with the 
        L{Geoipdb} object.
    @type ipend: IPAddressField (C{string})
    @ivar ipend: The upper bound of an IP address associated with the
        L{Geoipdb} object.
    @type country: CharField (C{string})
    @ivar country: The two-letter country code associated with the
        L{Geoipdb} object.
    @type latitude: DecimalField (C{float})
    @ivar latitude: The latitude associated with the L{Geoipdb} object.
    @type longitude: DecimalField (C{float})
    @ivar longitude: The longitude associated with the L{Geoipdb} object.
    """
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
    """
    Model for the first known consensuses of all months in the database.

    Django uses class variables to specify model fields, but these fields are
    practically used and thought of as instance variables, so this
    documentation will refer to them as such. Field types are specified as
    their Django field classes, with parentheses indicating the python type
    they are validated against and treated as. When constructing 
    a L{RelaysMonthlySnapshots} object, instance variables are specified as 
    keyword arguments in L{RelaysMonthlySnapshots} constructors.

    @type validafter: DateTimeField (C{datetime})
    @ivar validafter: The time that the consensus was published.
    @type fingerprint: CharField (C{string})
    @ivar fingerprint: The unique fingerprint hash of the router that the
        L{Statusentry} describes.
    @type nickname: CharField (C{string})
    @ivar nickname: The nickname of the router that the L{Statusentry}
        describes.
    @type address: CharField (C{string})
    @ivar address: The IP address of the relay that the L{Statusentry}
        describes.
    @type country: CharField (C{string})
    @ivar country: The two-letter country code associated with the relay.
    @type latitude: DecimalField (C{string})
    @ivar latitude: The latitude of the relay.
    @type longitude: DecimalField (C{string})
    @ivar longitude: The longitude of the relay.
    @type isexit: BooleanField (C{boolean})
    @ivar isexit: True if the relay is an exit relay, False otherwise.
    @type isfast: BooleanField (C{boolean})
    @ivar isfast: True if the relay is a fast server, False otherwise.
    @type isguard: BooleanField (C{boolean})
    @ivar isguard: True if the relay is a guard server, False otherwise.
    @type isstable: BooleanField (C{boolean})
    @ivar isstable: True if the relay is stable, False otherwise.
    @type version: CharField (C{string})
    @ivar version: The version of Tor that the relay is running.
    @type ports: TextField (C{string})
    @ivar ports: The ports that the relay does or does not allow exiting to.
        Includes the keywords "reject" and "accept"
    @type bandwidthavg: BigIntegerField (C{long})
    @ivar bandwidthavg: The average bandwidth of the relay in bytes 
        per second.
    @type bandwidthburst: BigIntegerField (C{long})
    @ivar bandwidthburst: The burst bandwidth of the relay in bytes 
        per second.
    @type bandwidthobserved: BigIntegerField (C{long})
    @ivar bandwidthobserved: The observed bandwidth of the relay in bytes
        per second.
    """
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
        return str(self.validafter) + ": " + self.fingerprint

class BridgeNetworkSize(models.Model):
    """
    Model for the average number of running bridges.

    Django uses class variables to specify model fields, but these fields are
    practically used and thought of as instance variables, so this
    documentation will refer to them as such. Field types are specified as
    their Django field classes, with parentheses indicating the python type
    they are validated against and treated as. When constructing 
    a L{BridgeNetworkSize} object, instance variables are specified as 
    keyword arguments in L{BridgeNetworkSize} constructors.
    @type date: DateField (C{datetime})
    @ivar date: The date associated with the L{BridgeNetworkSize} object.
    @type avg_running: IntegerField (C{int})
    @ivar avg_running: The average number of running relays associated with
        the L{date}.
    """
    date = models.DateField(primary_key=True)
    avg_running = models.IntegerField()
    class Meta:
        db_table = u'bridge_network_size'
    def __unicode__(self):
        return str(self.date)

class DirreqStats(models.Model):
    #TODO: guesses in here as to what the fields are, one blank.
    """
    Model for the daily users by country.

    Django uses class variables to specify model fields, but these fields are
    practically used and thought of as instance variables, so this
    documentation will refer to them as such. Field types are specified as
    their Django field classes, with parentheses indicating the python type
    they are validated against and treated as. When constructing 
    a L{DirreqStats} object, instance variables are specified as 
    keyword arguments in L{DirreqStats} constructors.
    
    @type source: CharField (C{string})
    @ivar source: The source associated with the L{DirreqStats} object.
    @type statsend: DateTimeField (C{datetime})
    @ivar statsend: The last date that the statistics of this entry were
        gathered.
    @type seconds: IntegerField (C{int})
    @ivar seconds:
    @type country: CharField (C{string})
    @ivar country: The country associated with the L{DirreqStats} object.
    @type requests: IntegerField (C{int})
    @ivar requests: The number of requests associated with the
        L{DirreqStats} object.
    """
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
        return str(self.statsend) + ": " + self.country + ", " + self.source \
                + ", " + self.seconds

class BridgeStats(models.Model):
    """
    Model for the daily bridge users by country.

    Django uses class variables to specify model fields, but these fields are
    practically used and thought of as instance variables, so this
    documentation will refer to them as such. Field types are specified as
    their Django field classes, with parentheses indicating the python type
    they are validated against and treated as. When constructing 
    a L{BridgeStats} object, instance variables are specified as 
    keyword arguments in L{BridgeStats} constructors.

    @type date: DateField (C{datetime})
    @ivar date: The date associated with the L{BridgeStats} object.
    @type country: CharField (C{string})
    @ivar country: The country that the bridges are associated with.
    @type users: IntegerField (C{int})
    @ivar users: The number of users associated with the given L{date} and
        L{country}
    """
    date = models.DateField()
    country = models.CharField(max_length=2, primary_key=True) # This field type is a guess.
    users = models.IntegerField()
    class Meta:
        unique_together = ("date", "country")
        verbose_name = "bridge stats"
        verbose_name_plural = "bridge stats"
        db_table = u'bridge_stats'
    def __unicode__(self):
        return str(self.date) + ": " + self.country

class TorperfStats(models.Model):
    # TODO: Don't understand what the fields here are used for.
    """
    Model for the quantiles and medians of daily torperf results.

    Django uses class variables to specify model fields, but these fields are
    practically used and thought of as instance variables, so this
    documentation will refer to them as such. Field types are specified as
    their Django field classes, with parentheses indicating the python type
    they are validated against and treated as. When constructing 
    a L{TorperfStats} object, instance variables are specified as 
    keyword arguments in L{TorperfStats} constructors.
    
    @type date: DateField (C{datetime})
    @ivar date:
    @type source: CharField (C{string})
    @ivar source:
    @type q1: IntegerField (C{int})
    @ivar q1:
    @type md: IntegerField (C{int})
    @ivar md:
    @type q3: IntegerField (C{int})
    @ivar q3:
    @type timeouts: IntegerField (C{int})
    @ivar timeouts:
    @type failures: IntegerField (C{int})
    @ivar failures:
    @type requests: IntegerField (C{int})
    @ivar requests:
    """
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
        return str(self.date) + ": " + self.source

class GettorStats(models.Model):
    # TODO: Don't know what the fields here are used for, either.
    """
    Model for the packages requested from GetTor.

    Django uses class variables to specify model fields, but these fields are
    practically used and thought of as instance variables, so this
    documentation will refer to them as such. Field types are specified as
    their Django field classes, with parentheses indicating the python type
    they are validated against and treated as. When constructing 
    a L{TorperfStats} object, instance variables are specified as 
    keyword arguments in L{TorperfStats} constructors.

    @type date: DateField (C{datetime})
    @ivar date:
    @type bundle: CharField (C{string})
    @ivar bundle:
    @type downloads: IntegerField (C{int})
    @ivar downloads:
    """
    date = models.DateField()
    bundle = models.CharField(max_length=64, primary_key=True)
    downloads = models.IntegerField()
    class Meta:
        unique_together = ("date", "bundle")
        verbose_name = "get Tor statistics"
        verbose_name_plural = "get Tor statistics"
        db_table = u'gettor_stats'
    def __unicode__(self):
        return str(self.date) + ": " + self.bundle
