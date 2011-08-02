"""
Models that correspond to the Tor Metrics database.

Django uses class variables to specify model fields, but these fields
are practically used and thought of as instance variables, so this
documentation will refer to them as such. Field types are specified as
their Django field classes, with parentheses indicating the python type
they are validated against and treated as. When constructing
an object, instance variables are specified as keyword arguments
in the object's constructors.

@see: The documentation of the class variables/instance variables here
    are only meant to provide insight as to how TorStatus can use the
    data. For more detailed descriptions, see
    U{https://gitweb.torproject.org/torspec.git/blob/HEAD:/dir-spec.txt}

@group Custom Fields: L{BigIntegerArrayField}, L{TextArrayField}
@group Models: L{Descriptor}, L{Extrainfo}, L{Bwhist}, L{Statusentry},
    L{Consensus}, L{Vote}, L{Connbidirect}, L{NetworkSize},
    L{NetworkSizeHour}, L{RelayCountries}, L{RelayPlatforms},
    L{RelayVersions}, L{TotalBandwidth}, L{TotalBwhist},
    L{BwhistFlags}, L{UserStats}, L{RelayStatusesPerDay},
    L{ScheduledUpdates}, L{Updates}, L{Geoipdb},
    L{RelaysMonthlySnapshots}, L{BridgeNetworkSize}, L{DirreqStats},
    L{BridgeStats}, L{TorperfStats}, L{GettorStats}, L{ActiveRelay},
    L{ActiveDescriptor}
"""
from django.db import models


# CUSTOM FIELDS -------------------------------------------------------
# ---------------------------------------------------------------------
class BigIntegerArrayField(models.Field):

    description = "An array of large integers"

    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        super(BigIntegerArrayField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        return 'BIGINT[]'

    def to_python(self, value):
        return value


class TextArrayField(models.Field):

    description = "An array of text"

    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        super(TextArrayField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        return 'TEXT[]'

    def to_python(self, value):
        return value


# MODELS --------------------------------------------------------------
# ---------------------------------------------------------------------
# tordir.public -------------------------------------------------------
class Descriptor(models.Model):
    """
    Model for descriptors published by routers.

    @type descriptorid: IntegerField (C{int})
    @ivar descriptorid: An auto-incrementing index.
    @type descriptor: CharField (C{string})
    @ivar descriptor: The L{Descriptor}'s unique descriptor hash.
    @type nickname: CharField (C{string})
    @ivar nickname: The nickname of the router that the L{Descriptor}
        describes.
    @type address: CharField (C{string})
    @ivar address: The IP address of the router that the L{Descriptor}
        describes.
    @type orport: IntegerField (C{int})
    @ivar orport: The ORPort of the router that the L{Descriptor}
        describes.
    @type dirport: IntegerField (C{int})
    @ivar dirport: The DirPort of the router that the L{Descriptor}
        describes.
    @type fingerprint: CharField (C{string})
    @ivar fingerprint: The fingerprint hash of the router that the
        L{Descriptor} describes.
    @type bandwidthavg: BigIntegerField (C{long})
    @ivar bandwidthavg: The average bandwidth of the router that the
        L{Descriptor} describes.
    @type bandwidthburst: BigIntegerField (C{long})
    @ivar bandwidthburst: The burst bandwidth of the router that the
        L{Descriptor} describes.
    @type bandwidthobserved: BigIntegerField (C{long})
    @ivar bandwidthobserved: The observed bandwidth of the router that
        the L{Descriptor} describes.
    @type platform: CharField (C{string})
    @ivar platform: The Tor release and the platform of the router that
        the L{Descriptor} describes.
    @type published: DateTimeField (C{datetime})
    @ivar published: The time that the L{Descriptor} was published.

    @type uptime: BigIntegerField (C{long})
    @ivar uptime: The time, in seconds, that the router that the
        L{Descriptor} describes has been continuously running.
    @type extrainfo: CharField (C{string})
    @ivar extrainfo: A hash that references a unique L{Extrainfo}
        object.
    @type rawdesc: TextField (C{string})
    @ivar rawdesc: Raw descriptor information that may or may not be
        present in other fields of the L{Descriptor} object
    """
    descriptorid = models.IntegerField(primary_key=True)
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
    uptime = models.BigIntegerField(blank=True)
    extrainfo = models.CharField(max_length=40, blank=True)
    rawdesc = models.TextField()

    class Meta:
        db_table = u'descriptor'

    def __unicode__(self):
        return self.descriptor


class Extrainfo(models.Model):
    """
    Model for extrainfo published by routers.

    @type extrainfo: CharField (C{string})
    @ivar extrainfo: The L{Extrainfo} object's unique extrainfo hash.
    @type nickname: Charfield (C{string})
    @ivar nickname: The nickname of the router that the L{Extrainfo}
        object describes.
    @type fingerprint: Charfield (C{string})
    @ivar fingerprint: The fingerprint hash of the router that the
        L{Extrainfo} object describes.
    @type published: DateTimeField (C{string})
    @ivar published: The time that the L{Extrainfo} object was
        published.
    @type rawdesc: TextField (C{string})
    @ivar rawdesc: Raw descriptor information that may or may not be
        present in other fields of the L{Extrainfo} object or the
        L{Descriptor} object that references it.
    """
    extrainfo = models.CharField(max_length=40, primary_key=True)
    nickname = models.CharField(max_length=19)
    fingerprint = models.CharField(max_length=40)
    published = models.DateTimeField()
    rawdesc = models.TextField()

    class Meta:
        verbose_name = "extra info"
        verbose_name_plural = "extra info"
        db_table = u'extrainfo'

    def __unicode__(self):
        return self.extrainfo


class Bwhist(models.Model):
    """
    Model for the bandwidth history of the routers.

    Contains bandwidth histories reported by relays in extra-info
    descriptors. Each row contains the reported bandwidth in 15-minute
    intervals for each relay and date.

    All bandwidth values are given in bytes per second.

    @type fingerprint: CharField (C{string})
    @ivar fingerprint: The fingerprint hash of the router that the
        L{Bwhist} object describes.
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
    @ivar dirread: The reported directory reading bandwidth as an
        array.
    @type dirread_sum: BigIntegerField (C{long})
    @ivar dirread_sum: The sum of the reported directory reading
        bandwidth.
    @type dirwritten: BigIntegerArrayField (C{list})
    @ivar dirwritten: The reported directory writing bandwidth as an
        array.
    @type dirwritten_sum: BigIntegerField (C{long})
    @ivar dirwritten_sum: The sum of the reported directory writing
        bandwidth.
    """
    fingerprint = models.CharField(max_length=40, primary_key=True)
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
    Each statusentry references a valid descriptor, though the
    descriptor may or may not be published yet.

    @type validafter: DateTimeField (C{datetime})
    @ivar validafter: The time that the consensus was published.
    @type nickname: CharField (C{string})
    @ivar nickname: The nickname of the router that the L{Statusentry}
        describes.
    @type fingerprint: CharField (C{string})
    @ivar fingerprint: The unique fingerprint hash of the router that
        the L{Statusentry} describes.
    @type descriptor: CharField (C{string})
    @ivar descriptor: The unique descriptor hash of the router that the
        L{Statusentry} describes. References an entry in the
        L{Descriptor} table, but this entry may or may not be added to
        the table yet.
    @type descriptorid: ForeignKey
    @ivar descriptorid: References a L{Descriptor} object or is null.
    @type published: DateTimeField (C{datetime})
    @ivar published: The time that the entry was published.
    @type address: CharField (C{string})
    @ivar address: The IP address of the relay that the L{Statusentry}
        describes.
    @type orport: IntegerField (C{int})
    @ivar orport: The ORPort of the relay that the L{Statusentry}
        describes.
    @type dirport: IntegerField (C{int})
    @ivar dirport: The DirPort of the relay that the L{Statusentry}
        describes.
    @type isauthority: BooleanField (C{boolean})
    @ivar isauthority: True if the relay is an authority relay,
        False otherwise.
    @type isbadexit: BooleanField (C{boolean})
    @ivar isbadexit: True if the relay is a bad exit node, False
        otherwise.
    @type isbaddirectory: BooleanField (C{boolean})
    @ivar isbaddirectory: True if the relay is a bad directory node,
        False otherwise.
    @type isexit: BooleanField (C{boolean})
    @ivar isexit: True if the relay is an exit relay, False otherwise.
    @type isfast: BooleanField (C{boolean})
    @ivar isfast: True if the relay is a fast server, False otherwise.
    @type isguard: BooleanField (C{boolean})
    @ivar isguard: True if the relay is a guard server,
        False otherwise.
    @type ishsdir: BooleanField (C{boolean})
    @ivar ishsdir: True if the relay is a hidden service directory,
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
    @ivar isv2dir: True if the relay is a v2 directory,
        False otherwise.
    @type isv3dir: BooleanField (C{boolean})
    @ivar isv3dir: True if the relay is a v3 directory,
        False otherwise.
        As of 06-20-2011, there are not yet any v3 directories.
    @type version: CharField (C{string})
    @ivar version: The version of Tor that the relay is running.
    @type bandwidth: BigIntegerField (C{long})
    @ivar bandwidth: The bandwidth of the relay in bytes per second.
    @type ports: TextField (C{string})
    @ivar ports: The ports that the relay does or does not allow
        exiting to. Includes the keywords "reject" and "accept".
    @type rawdesc: TextField (C{string})
    @ivar rawdesc: The raw descriptor information associated with the
        L{Statusentry}, which may or may not contain information
        published elsewhere.
    """
    validafter = models.DateTimeField(primary_key=True)
    nickname = models.CharField(max_length=19)
    fingerprint = models.CharField(max_length=40)
    descriptor = models.CharField(max_length=40)
    descriptorid = models.ForeignKey(Descriptor,
            db_column='descriptorid')
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
    rawdesc = models.TextField()

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
    """
    Model for the consensuses published by the directories.

    @type validafter: DateTimeField (C{datetime})
    @ivar validafter: The date that the L{Consensus} object was
        published.
    @type rawdesc: TextField (C{string})
    @ivar rawdesc: The raw descriptor of the consensus object.
    """
    validafter = models.DateTimeField(primary_key=True)
    rawdesc = models.TextField()

    class Meta:
        verbose_name = "consensus"
        verbose_name_plural = "consensuses"
        db_table = u'consensus'

    def __unicode__(self):
        return str(self.validafter)


class Vote(models.Model):
    """
    Model for the votes published by the directories.

    @type validafter: DateTimeField (C{datetime})
    @ivar validafter: The validafter date that corresponds to a
        validafter date in a L{Consensus} object.
    @type dirsource: CharField (C{string})
    @ivar dirsource: The source of the directory that publishes the
        L{Vote} object.
    @type rawdesc: TextField (C{string})
    @ivar rawdesc: The raw descriptor associated with the L{Vote}
        object.
    """
    validafter = models.DateTimeField(primary_key=True)
    dirsource = models.CharField(max_length=40)
    rawdesc = models.TextField()

    class Meta:
        unique_together = ("validafter", "dirsource")
        db_table = u'vote'

    def __unicode__(self):
        return str(self.validafter) + ": " + self.dirsource


class Connbidirect(models.Model):
    # TODO: Validate documentation
    """
    Model for the number of connections, split into 10-second
    intervals, that are used uni-directionally or bi-directionally in
    a given number of seconds before a given date.

    @type source: CharField (C{string})
    @ivar source: The reporting source, such as siv, moria, torperf, or
        all.
    @type statsend: DateTimeField (C{datetime})
    @ivar statsend: The last date, specific to seconds, that the number
        of connections was calculated for.
    @type seconds: IntegerField (C{int})
    @ivar seconds: The number of seconds before C{statsend}
    @type belownum: BigIntegerField (C{long})
    @ivar belownum: The number of connections that read and wrote less
        than 20 KiB.
    @type readnum: BigIntegerField (C{long})
    @ivar readnum: The number of connections that read at least 10
        times more than they wrote.
    @type writenum: BigIntegerField (C{long})
    @ivar writenum: The number of connections that wrote at least 10
        times more than they wrote.
    @type bothnum: BigIntegerField (C{long})
    @ivar bothnum: The number of connections that do not read 10 times
        more than they write or write 10 times more than they read
        while also reading and writing more than 20 KiB.
    """
    source = models.CharField(max_length=40, primary_key=True)
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

    @type date: DateField (C{datetime})
    @ivar date: The date that corresponds to the averages given by the
        rest of the fields of the L{NetworkSize} object.
    @type avg_running: IntegerField (C{int})
    @ivar avg_running: The average number of running relays in the
        network.
    @type avg_exit: IntegerField (C{int})
    @ivar avg_exit: The average number of exit relays in the network.
    @type avg_guard: IntegerField (C{int})
    @ivar avg_guard: The average number of guard relays in the network.
    @type avg_fast: IntegerField (C{int})
    @ivar avg_fast: The average number of fast relays in the network.
    @type avg_stable: IntegerField (C{int})
    @ivar avg_stable: The average number of stable relays in the
        network.
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
    Model for the size of the network with respect to a certain
    validafter date that corresponds to the validafter dates found
    in L{Descriptor}, L{Statusentry}, L{Consensus}, and L{Vote}
    objects.

    @type validafter: DateField (C{datetime})
    @ivar validafter: The hour that corresponds to the network size.
    @type avg_running: IntegerField (C{int})
    @ivar avg_running: The average number of running relays in
        the network.
    @type avg_exit: IntegerField (C{int})
    @ivar avg_exit: The average number of exit relays in the network.
    @type avg_guard: IntegerField (C{int})
    @ivar avg_guard: The average number of guard relays in the network.
    @type avg_fast: IntegerField (C{int})
    @ivar avg_fast: The average number of fast relays in the network.
    @type avg_stable: IntegerField (C{int})
    @ivar avg_stable: The average number of stable relays in the
        network.
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

    @type date: DateField (C{datetime})
    @ivar date: The date that the L{RelayCountries} object refers to.
    @type country: CharField (C{datetime})
    @ivar country: The two letter country code that the
        L{RelayCountries} object refers to.
    @type relays: IntegerField (C{int})
    @ivar relays: The number of relays active from a given L{country}
        on a given L{date}.
    """
    date = models.DateField()
    country = models.CharField(max_length=2, primary_key=True)
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
    Model for the number of relays active running on a given platform
    on a given date.

    @type date: DateField (C{datetime})
    @ivar date: The date that corresponds to the L{RelayPlatforms}
        object.
    @type avg_linux: IntegerField (C{int})
    @ivar avg_linux: The average number of relays in the network
        running Linux.
    @type avg_darwin: IntegerField (C{int})
    @ivar avg_darwin: The average number of relays in the network
        running Darwin/OSX
    @type avg_bsd: IntegerField (C{int})
    @ivar avg_bsd: The average number of relays in the network running
        BSD.
    @type avg_windows: IntegerField (C{int})
    @ivar avg_windows: The average number of relays in the network
        running Windows.
    @type avg_other: IntegerField (C{int})
    @ivar avg_other: The average number of relays in the network
        running on a platform that is not Linux, Darwin/OSX, BSD, or
        Windows.
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

    @type date: DateField (C{datetime})
    @ivar date: The date that corresponds to the L{RelayVersions}
        object.
    @type version: CharField (C{string})
    @ivar version: The version of Tor that is being run by L{relays}
        on a given L{date}.
    @type relays: IntegerField (C{int})
    @ivar relays: The number of relays running a given version of Tor
        with respect to a given date.
    """
    date = models.DateField()
    version = models.CharField(max_length=5, primary_key=True)
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

    @type date: DateField (C{string})
    @ivar date: The date that corresponds to the L{TotalBandwidth}
        object.
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
    Model for the total number of read/written and the number of dir
    bytes read/written by all relays in the network on a given day.

    The dir bytes are an estimate based on the subset of relays that
    count dir bytes.

    @type date: DateField (C{datetime})
    @ivar date: The date that corresponds to the L{TotalBwhist} object.
    @type read: BigIntegerField (C{long})
    @ivar read: The total number of dir bytes that are read by all
        relays on the given date.
    @type written: BigIntegerField (C{long})
    @ivar written: The total number of dir bytes that are written by
        all relays on the given date.
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
    # TODO: The interpretation of this class is a guess.
    """
    Model for the total number of read/written bandwidth in the network
    by relays that are exit routers, guard routers, both, or neither.

    @type date: DateField (C{datetime})
    @ivar date: The day for which the statistics gathered apply.
    @type isexit: BooleanField (C{boolean})
    @ivar isexit: True if the statistics gathered required that routers
        be exit routers, False if the statistics gathered required that
        routers not be exit routers.
    @type isguard: BooleanField (C{boolean})
    @ivar isguard: True if the statistics gathered required that
        routers be guard routers, False if the statistics gathered
        required that routers not be guard routers.
    @type read: BooleanField (C{boolean})
    @ivar read: The total read bandwidth of routers that fit the given
        criteria on the given date.
    @type written: BooleanField (C{boolean})
    @ivar written: The total written bandwidth of routers that fit
        the given criteria on the given date.
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
        return (str(self.date) + ": " + self.isexit + ", "
               + self.isguard)


class UserStats(models.Model):
    # TODO: The interpretation of this class is nothing more than a
    # good guess.
    # see https://gitweb.torproject.org/metrics-web.git/blob/HEAD:/db/
    # tordir.sql, particularly line 652-.
    """
    Model for the aggregate statistics on directory requests and byte
    histories used to estimate user numbers.

    Request statistics exclude requests made by authorities.

    @type date: DateField (C{datetime})
    @ivar date: The date that corresponds to the L{UserStats} object.
    @type country: CharField (C{string})
    @ivar country: The country that corresponds to the L{UserStats}
        object.
    @type r: BigIntegerField (C{long})
    @ivar r: Total requests from a given country.
    @type dw: BigIntegerField (C{long})
    @ivar dw: Directory written bandwidth, in bytes.
    @type dr: BigIntegerField (C{long})
    @ivar dr: Directory read bandwidth, in bytes.
    @type drw: BigIntegerField (C{long})
    @ivar drw: Directory written bandwidth, in bytes, where directory
        requests are reported.
    @type drr: BigIntegerField (C{long})
    @ivar drr: Directory read bandwidth, in bytes, where directory
        requests are reported.
    @type bw: BigIntegerField (C{long})
    @ivar bw: Written bandwidth, in bytes.
    @type br: BigIntegerField (C{long})
    @ivar br: Read bandwidth, in bytes.
    @type bwd: BigIntegerField (C{long})
    @ivar bwd: Bandwidth written, in bytes, where directory bandwidth
        written is reported.
    @type brd: BigIntegerField (C{long})
    @ivar brd: Bandwidth read, in bytes, where directory bandwidth
        written is reported.
    @type bwr: BigIntegerField (C{long})
    @ivar bwr: Bandwidth written, in bytes, where directory requests
        are reported.
    @type brr: BigIntegerField (C{long})
    @ivar brr: Bandwidth read, in bytes, where directory requests are
        reported.
    @type bwdr: BigIntegerField (C{long})
    @ivar bwdr: Bandwidth written, in bytes, where directory bandwidth
        written and directory requests are reported.
    @type brdr: BigIntegerField (C{long})
    @ivar brdr: Bandwidth read, in bytes, where directory bandwidth
        written and directory requests are reported.
    @type bwp: BigIntegerField (C{long})
    @ivar bwp: Bandwidth written, in bytes, where the directory port
        is open.
    @type brp: BigIntegerField (C{long})
    @ivar brp: Bandwidth read, in bytes, where the directory port is
        open.
    @type bwn: BigIntegerField (C{long})
    @ivar bwn: Bandwidth written, in bytes, where the directory port is
        not open.
    @type brn: BigIntegerField (C{long})
    @ivar brn: Bandwidth read, in bytes, where the directory port is
        not open.
    """
    date = models.DateField()
    country = models.CharField(max_length=2, primary_key=True)
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
    """
    Model for the helper table which is used to update the other
    tables.

    @type date: DateField (C{datetime})
    @ivar date: The date that corresponds to the L{RelayStatusesPerDay}
        object.
    @type count: IntegerField (C{datetime})
    @ivar count: The number of relay statuses per day.
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

    @type id: IntegerField (C{int})
    @ivar id: The index of the L{ScheduledUpdates} object.
    @type date: DateField (C{datetime})
    @ivar date: The date that corresponds to the L{ScheduledUpdates}
        object.
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

    @type id: IntegerField (C{int})
    @ivar id: The index associated with the L{Geoipdb} object.
    @type ipstart: CharField (C{string})
    @ivar ipstart: The lower bound of an IP address associated with the
        L{Geoipdb} object.
    @type ipend: IPAddressField (C{string})
    @ivar ipend: The upper bound of an IP address associated with the
        L{Geoipdb} object.
    @type country: IPAddressField (C{string})
    @ivar country: The two-letter country code associated with the
        L{Geoipdb} object.
    @type latitude: DecimalField (C{float})
    @ivar latitude: The latitude associated with the L{Geoipdb} object.
    @type longitude: DecimalField (C{float})
    @ivar longitude: The longitude associated with the L{Geoipdb}
        object.
    """
    id = models.IntegerField(primary_key=True)
    ipstart = models.IPAddressField()
    ipend = models.IPAddressField()
    country = models.CharField(max_length=2)
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
    Model for the first known consensuses of all months in the
    database.

    @type validafter: DateTimeField (C{datetime})
    @ivar validafter: The time that the consensus was published.
    @type fingerprint: CharField (C{string})
    @ivar fingerprint: The unique fingerprint hash of the router that
        the L{Statusentry} describes.
    @type nickname: CharField (C{string})
    @ivar nickname: The nickname of the router that the L{Statusentry}
        describes.
    @type address: CharField (C{string})
    @ivar address: The IP address of the relay that the L{Statusentry}
        describes.
    @type country: CharField (C{string})
    @ivar country: The two-letter country code associated with the
        relay.
    @type latitude: DecimalField (C{string})
    @ivar latitude: The latitude of the relay.
    @type longitude: DecimalField (C{string})
    @ivar longitude: The longitude of the relay.
    @type isexit: BooleanField (C{boolean})
    @ivar isexit: True if the relay is an exit relay, False otherwise.
    @type isfast: BooleanField (C{boolean})
    @ivar isfast: True if the relay is a fast server, False otherwise.
    @type isguard: BooleanField (C{boolean})
    @ivar isguard: True if the relay is a guard server,
        False otherwise.
    @type isstable: BooleanField (C{boolean})
    @ivar isstable: True if the relay is stable, False otherwise.
    @type version: CharField (C{string})
    @ivar version: The version of Tor that the relay is running.
    @type ports: TextField (C{string})
    @ivar ports: The ports that the relay does or does not allow
        exiting to. Includes the keywords "reject" and "accept"
    @type bandwidthavg: BigIntegerField (C{long})
    @ivar bandwidthavg: The average bandwidth of the relay in bytes
        per second.
    @type bandwidthburst: BigIntegerField (C{long})
    @ivar bandwidthburst: The burst bandwidth of the relay in bytes
        per second.
    @type bandwidthobserved: BigIntegerField (C{long})
    @ivar bandwidthobserved: The observed bandwidth of the relay
        in bytes per second.
    """
    validafter = models.DateTimeField(primary_key=True)
    fingerprint = models.CharField(max_length=40)
    nickname = models.CharField(max_length=19)
    address = models.IPAddressField()
    country = models.CharField(max_length=2)
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

    @type date: DateField (C{datetime})
    @ivar date: The date associated with the L{BridgeNetworkSize}
        object.
    @type avg_running: IntegerField (C{int})
    @ivar avg_running: The average number of running relays associated
        with the L{date}.
    """
    date = models.DateField(primary_key=True)
    avg_running = models.IntegerField()

    class Meta:
        db_table = u'bridge_network_size'

    def __unicode__(self):
        return str(self.date)


class DirreqStats(models.Model):
    # TODO: These are guesses; someone who knows how this works should
    # document this class better.
    """
    Model for the daily users by country, or the Directory Request
    Statistics.

    @type source: CharField (C{string})
    @ivar source: The source associated with the L{DirreqStats} object,
        usually siv, moria, torperf, or all.
    @type statsend: DateTimeField (C{datetime})
    @ivar statsend: The last date (specific to seconds)
        that the statistics of this entry were gathered.
    @type seconds: IntegerField (C{int})
    @ivar seconds: The number of seconds (usually 86400) over which
        the data has been gathered.
    @type country: CharField (C{string})
    @ivar country: The country that the number of the C{requests}
        refers to.
    @type requests: IntegerField (C{int})
    @ivar requests: The number of requests from the C{country}
        over a period of C{seconds} ending with C{statsend}.
    """
    source = models.CharField(max_length=40)
    statsend = models.DateTimeField()
    seconds = models.IntegerField()
    country = models.CharField(max_length=2)
    requests = models.IntegerField()

    class Meta:
        unique_together = ("source", "statsend", "seconds", "country")
        verbose_name = "dirreq stats"
        verbose_name_plural = "dirreq stats"
        db_table = u'dirreq_stats'

    def __unicode__(self):
        return str(self.statsend) + ": " + self.country + ", " + \
               self.source + ", " + self.seconds


class BridgeStats(models.Model):
    """
    Model for the daily bridge users by country.

    @type date: DateField (C{datetime})
    @ivar date: The date associated with the L{BridgeStats} object.
    @type country: CharField (C{string})
    @ivar country: The country that the bridges are associated with.
    @type users: IntegerField (C{int})
    @ivar users: The number of users associated with the given L{date}
        and L{country}
    """
    date = models.DateField()
    country = models.CharField(max_length=2, primary_key=True)
    users = models.IntegerField()

    class Meta:
        unique_together = ("date", "country")
        verbose_name = "bridge stats"
        verbose_name_plural = "bridge stats"
        db_table = u'bridge_stats'

    def __unicode__(self):
        return str(self.date) + ": " + self.country


class TorperfStats(models.Model):
    """
    Model for the quantiles and medians of daily torperf results.

    @type date: DateField (C{datetime})
    @ivar date: The date that the requests refer to.
    @type source: CharField (C{string})
    @ivar source: The reporting source (torperf, moria, siv, or all)
        and the size (50 Kib, 1 MiB, or 5 MiB) of the request being
        tested.
    @type q1: IntegerField (C{int})
    @ivar q1: First quartile of the time, in thousandths of
        seconds, to complete a request on a given C{date}.
    @type md: IntegerField (C{int})
    @ivar md: Median of the time, in thousandths of seconds, to
        complete a request on a given C{date}.
    @type q3: IntegerField (C{int})
    @ivar q3: Third quartile of the time, in thousandths of seconds,
        to complete a request on a given C{date}.
    @type timeouts: IntegerField (C{int})
    @ivar timeouts: The number of request timeouts.
    @type failures: IntegerField (C{int})
    @ivar failures: The number of request failures.
    @type requests: IntegerField (C{int})
    @ivar requests: The total number of requests.
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
    """
    Model for the packages requested from GetTor.

    @type date: DateField (C{datetime})
    @ivar date: The date to which statistics refer.
    @type bundle: CharField (C{string})
    @ivar bundle: The GetTor bundle name to which statistics refer.
    @type downloads: IntegerField (C{int})
    @ivar downloads: Number of C{bundle} requested from GetTor
        on C{date}.
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


# tordir.cache  -------------------------------------------------------
# ---------------------------------------------------------------------
class ActiveStatusentry(models.Model):
    """
    Model for the most recent statusentries for each relay published in
    the last 4 hours.

    @type validafter: DateTimeField (C{datetime})
    @ivar validafter: The time that the consensus was published.
    @type nickname: CharField (C{string})
    @ivar nickname: The nickname of the router that the L{Statusentry}
        describes.
    @type fingerprint: CharField (C{string})
    @ivar fingerprint: The unique fingerprint hash of the router that
        the L{Statusentry} describes.
    @type address: CharField (C{string})
    @ivar address: The IP address of the relay that the L{Statusentry}
        describes.
    @type orport: IntegerField (C{int})
    @ivar orport: The ORPort of the relay that the L{Statusentry}
        describes.
    @type dirport: IntegerField (C{int})
    @ivar dirport: The DirPort of the relay that the L{Statusentry}
        describes.
    @type isauthority: BooleanField (C{boolean})
    @ivar isauthority: True if the relay is an authority relay,
        False otherwise.
    @type isbadexit: BooleanField (C{boolean})
    @ivar isbadexit: True if the relay is a bad exit node, False
        otherwise.
    @type isbaddirectory: BooleanField (C{boolean})
    @ivar isbaddirectory: True if the relay is a bad directory node,
        False otherwise.
    @type isexit: BooleanField (C{boolean})
    @ivar isexit: True if the relay is an exit relay, False otherwise.
    @type isfast: BooleanField (C{boolean})
    @ivar isfast: True if the relay is a fast server, False otherwise.
    @type isguard: BooleanField (C{boolean})
    @ivar isguard: True if the relay is a guard server,
        False otherwise.
    @type ishsdir: BooleanField (C{boolean})
    @ivar ishsdir: True if the relay is a hidden service directory,
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
    @ivar isv2dir: True if the relay is a v2 directory,
        False otherwise.
    @type isv3dir: BooleanField (C{boolean})
    @ivar isv3dir: True if the relay is a v3 directory,
        False otherwise. As of 08-01-2011, there are not yet any
        v3 directories.
    @type country: CharField (C{string})
    @ivar country: The country that the relay is located in.
    @type latitude: DecimalField (C{float})
    @ivar latitude: The latitude at which the relay is located.
    @type longitude: DecimalField (C{float})
    @ivar longitude: The longitude at which the relay is located.
    """
    validafter = models.DateTimeField()
    nickname = models.CharField(max_length=19)
    fingerprint = models.CharField(max_length=40, primary_key=True)
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
    country = models.CharField(max_length=2)
    latitude = models.DecimalField(
               max_digits=7, decimal_places=4, blank=True)
    longitude = models.DecimalField(
                max_digits=7, decimal_places=4, blank=True)

    class Meta:
        verbose_name = "active statusentry"
        verbose_name_plural = "active statusentries"
        db_table = 'cache\".\"active_statusentries'

    def __unicode__(self):
        return self.fingerprint


class ActiveDescriptor(models.Model):
    """
    Model for the most recent descriptors for each relay published in
    the last 48 hours.

    @type descriptor: CharField (C{string})
    @ivar descriptor: The unique descriptor hash of the relay.
    @type nickname: CharField (C{string})
    @ivar nickname: The nickname of the relay.
    @type fingerprint: CharField (C{string})
    @ivar fingerprint: The unique fingerprint hash of the relay.
    @type published: DateTimeField (C{datetime})
    @ivar published: The time that the descriptor associated with
        the relay was published.
    @type bandwidthavg: BigIntegerField (C{long})
    @ivar bandwidthavg: The average bandwidth of the relay, in Bps.
    @type bandwidthburst: BigIntegerField (C{long})
    @ivar bandwidthburst: The burst bandwidth of the relay, in Bps.
    @type bandwidthobserved: BigIntegerField (C{long})
    @ivar bandwidthobserved: The observed bandwidth of the relay, in
        Bps.
    @type bandwidthkbps: BigIntegerField (C{long})
    @ivar bandwidthkbps: The observed bandwidth of the relay, in KBps.
    @type uptime: BigIntegerField (C{long})
    @ivar uptime: The uptime of the relay in seconds.
    @type uptimedays: BigIntegerField (C{long})
    @ivar uptimedays: The uptime of the relay in days.
    @type platform: CharField (C{string})
    @ivar platform: The platform of the relay.
    @type contact: CharField (C{string})
    @ivar contact: The contact information of the operator of the
        relay.
    @type onionkey: CharField (C{string})
    @ivar onionkey: The unique onionkey of the relay.
    @type signingkey: CharField (C{string})
    @ivar signingkey: The unique signing key of the relay.
    @type exitpolicy: TextField (C{string})
    @ivar exitpolicy: The exitpolicy information of the relay.
    @type family: TextField (C{string})
    @ivar family: The family that the relay belongs to.
    """
    descriptor = models.CharField(max_length=40)
    nickname = models.CharField(max_length=19)
    fingerprint = models.CharField(max_length=40, primary_key=True)
    published = models.DateTimeField()
    bandwidthavg = models.BigIntegerField()
    bandwidthburst = models.BigIntegerField()
    bandwidthobserved = models.BigIntegerField()
    bandwidthkbps = models.BigIntegerField()
    uptime = models.BigIntegerField()
    uptimedays = models.BigIntegerField()
    platform = models.CharField(max_length=256)
    contact = models.TextField()
    onionkey = models.CharField(max_length=188)
    signingkey = models.CharField(max_length=188)
    exitpolicy = TextArrayField()
    family = models.TextField()

    class Meta:
        verbose_name = "active descriptor"
        db_table = 'cache\".\"active_descriptor'

    def __unicode__(self):
        return self.fingerprint


class ActiveRelay(models.Model):
    """
    Model for the relays in the four most recent consensuses, with all
    relevant and available information.

    @type validafter: DateTimeField (C{datetime})
    @ivar validafter: The publication time of the last consensus
        that the relay appeared in.
    @type nickname: CharField (C{string})
    @ivar nickname: The nickname of the relay.
    @type fingerprint: CharField (C{string})
    @ivar fingerprint: The unique fingerprint hash of the relay.
    @type address: CharField (C{string})
    @ivar address: The IP address of the relay.
    @type orport: IntegerField (C{int})
    @ivar orport: The ORPort of the relay.
    @type dirport: IntegerField (C{int})
    @ivar dirport: The DirPort of the relay.
    @type isauthority: BooleanField (C{bool})
    @ivar isauthority: True if the relay is an authority,
        False otherwise.
    @type isbadexit: BooleanField (C{bool})
    @ivar isbadexit: True if the relay is a bad exit,
        False otherwise.
    @type isbaddirectory: BooleanField (C{bool})
    @ivar isbaddirectory: True if the relay is a bad directory,
        False otherwise.
    @type isexit: BooleanField (C{bool})
    @ivar isexit: True if the relay is an exit relay,
        False otherwise.
    @type isfast: BooleanField (C{bool})
    @ivar isfast: True if the relay is considered \'fast\',
        False otherwise.
    @type isguard: BooleanField (C{bool})
    @ivar isguard: True if the relay is a guard,
        False otherwise.
    @type ishsdir: BooleanField (C{bool})
    @ivar ishsdir: True if the relay is a hidden service directory,
        False otherwise.
    @type isnamed: BooleanField (C{bool})
    @ivar isnamed: True if the relay is named,
        False otherwise.
    @type isstable: BooleanField (C{bool})
    @ivar isstable: True if the relay is stable,
        False otherwise.
    @type isrunning: BooleanField (C{bool})
    @ivar isrunning: True if the relay is running,
        False otherwise.
    @type isunnamed: BooleanField (C{bool})
    @ivar isunnamed: True if the relay is unnamed,
        False otherwise.
    @type isvalid: BooleanField (C{bool})
    @ivar isvalid: True if the relay is valid,
        False otherwise.
    @type isv2dir: BooleanField (C{bool})
    @ivar isv2dir: True if the relay is a version 2 directory,
        False otherwise.
    @type isv3dir: BooleanField (C{bool})
    @ivar isv3dir: True if the relay is a version 3 directory,
        False otherwise.
    @type descriptor: CharField (C{string})
    @ivar descriptor: The unique descriptor hash of the relay.
    @type published: DateTimeField (C{datetime})
    @ivar published: The time that the descriptor associated with
        the relay was published.
    @type bandwidthavg: BigIntegerField (C{long})
    @ivar bandwidthavg: The average bandwidth of the relay, in Bps.
    @type bandwidthburst: BigIntegerField (C{long})
    @ivar bandwidthburst: The burst bandwidth of the relay, in Bps.
    @type bandwidthobserved: BigIntegerField (C{long})
    @ivar bandwidthobserved: The observed bandwidth of the relay, in
        Bps.
    @type bandwidthkbps: BigIntegerField (C{long})
    @ivar bandwidthkbps: The observed bandwidth of the relay, in KBps.
    @type uptime: BigIntegerField (C{long})
    @ivar uptime: The uptime of the relay in seconds.
    @type uptimedays: BigIntegerField (C{long})
    @ivar uptimedays: The uptime of the relay in days.
    @type platform: CharField (C{string})
    @ivar platform: The platform of the relay.
    @type contact: CharField (C{string})
    @ivar contact: The contact information of the operator of the
        relay.
    @type onionkey: CharField (C{string})
    @ivar onionkey: The unique onionkey of the relay.
    @type signingkey: CharField (C{string})
    @ivar signingkey: The unique signing key of the relay.
    @type exitpolicy: TextField (C{string})
    @ivar exitpolicy: The exitpolicy information of the relay.
    @type family: TextField (C{string})
    @ivar family: The family that the relay belongs to.
    @type ishibernating: BooleanField (C{bool})
    @ivar ishibernating: True if the relay is hibernating, False
        otherwise.
    @type country: CharField (C{string})
    @ivar country: The country that the relay is located in.
    @type latitude: DecimalField (C{float})
    @ivar latitude: The latitude at which the relay is located.
    @type longitude: DecimalField (C{float})
    @ivar longitude: The longitude at which the relay is located.
    """
    validafter = models.DateTimeField()
    nickname = models.CharField(max_length=19)
    fingerprint = models.CharField(max_length=40, primary_key=True)
    address = models.IPAddressField()
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
    descriptor = models.CharField(max_length=40, blank=True)
    published = models.DateTimeField(blank=True)
    bandwidthavg = models.BigIntegerField(blank=True)
    bandwidthburst = models.BigIntegerField(blank=True)
    bandwidthobserved = models.BigIntegerField(blank=True)
    bandwidthkbps = models.BigIntegerField(blank=True)
    uptime = models.BigIntegerField(blank=True)
    uptimedays = models.BigIntegerField(blank=True)
    platform = models.CharField(max_length=256, blank=True)
    contact = models.TextField()
    onionkey = models.CharField(max_length=188, blank=True)
    signingkey = models.CharField(max_length=188, blank=True)
    exitpolicy = TextArrayField()
    family = models.TextField(blank=True)
    ishibernating = models.BooleanField(blank=True)
    country = models.CharField(max_length=2, blank=True)
    latitude = models.DecimalField(
               max_digits=7, decimal_places=4, blank=True)
    longitude = models.DecimalField(
                max_digits=7, decimal_places=4, blank=True)

    class Meta:
        verbose_name = 'active relay'
        db_table = 'cache\".\"active_relay'

    def __unicode__(self):
        return self.fingerprint
