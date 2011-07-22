-- Create a schema and set it as the search path.
CREATE SCHEMA cache;
SET search_path TO cache;

-- Make UTC the timezone. This should not be changed.
SET TIME ZONE UTC;

-- TABLE active_descriptor
-- Contains descriptors published by routers in the last 20 hours.
CREATE TABLE active_descriptor (
    descriptor CHARACTER(40),
    nickname CHARACTER VARYING(19),
    fingerprint CHARACTER(40),
    published TIMESTAMP WITHOUT TIME ZONE,
    bandwidthavg BIGINT,
    bandwidthburst BIGINT,
    bandwidthobserved BIGINT,
    bandwidthkbps BIGINT,
    uptime BIGINT,
    uptimedays BIGINT,
    platform CHARACTER VARYING(256),
    contact TEXT,
    onionkey CHARACTER(188),
    signingkey CHARACTER(188),
    exitpolicy TEXT[],
    family TEXT,
    ishibernating BOOLEAN DEFAULT FALSE,
    CONSTRAINT active_descriptor_unique PRIMARY KEY (descriptor)
);

-- TABLE active_relay
-- Contains all relevant information about a relay that might be needed
-- for TorStatus.
CREATE TABLE active_relay (
    validafter TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    nickname CHARACTER VARYING(19) NOT NULL,
    fingerprint CHARACTER(40) NOT NULL,
    -- address INET NOT NULL, can't seem to cast text to inet, see below.
    address CHARACTER VARYING(15) NOT NULL,
    orport INTEGER NOT NULL,
    dirport INTEGER NOT NULL,
    isauthority BOOLEAN DEFAULT FALSE NOT NULL,
    isbadexit BOOLEAN DEFAULT FALSE NOT NULL,
    isbaddirectory BOOLEAN DEFAULT FALSE NOT NULL,
    isexit BOOLEAN DEFAULT FALSE NOT NULL,
    isfast BOOLEAN DEFAULT FALSE NOT NULL,
    isguard BOOLEAN DEFAULT FALSE NOT NULL,
    ishsdir BOOLEAN DEFAULT FALSE NOT NULL,
    isnamed BOOLEAN DEFAULT FALSE NOT NULL,
    isstable BOOLEAN DEFAULT FALSE NOT NULL,
    isrunning BOOLEAN DEFAULT FALSE NOT NULL,
    isunnamed BOOLEAN DEFAULT FALSE NOT NULL,
    isvalid BOOLEAN DEFAULT FALSE NOT NULL,
    isv2dir BOOLEAN DEFAULT FALSE NOT NULL,
    isv3dir BOOLEAN DEFAULT FALSE NOT NULL,
    descriptor CHARACTER(40),
    published TIMESTAMP WITHOUT TIME ZONE,
    bandwidthavg BIGINT,
    bandwidthburst BIGINT,
    bandwidthobserved BIGINT,
    bandwidthkbps BIGINT,
    uptime BIGINT,
    uptimedays BIGINT,
    platform CHARACTER VARYING(256),
    contact TEXT,
    onionkey CHARACTER(188),
    signingkey CHARACTER(188),
    exitpolicy TEXT[],
    family TEXT,
    ishibernating BOOLEAN,
    country CHARACTER VARYING(2),
    latitude NUMERIC(7, 4),
    longitude NUMERIC(7, 4),
    CONSTRAINT active_relay_unique PRIMARY KEY (fingerprint)
);

-- No hostname, for now. I don't think this breaks anybody's heart.
-- Later, could do lookup with socket.getfqdn (python)
-- CREATE TABLE hostname (
--    address INET NOT NULL,
--    hostname CHARACTER VARYING(255),
--    CONSTRAINT hostname_unique PRIMARY KEY (address)
--);

-- INDICES ------------------------------------------------------------
-- Create the various indexes we need for searching active relays
CREATE INDEX active_relay_fingerprint ON active_relay (fingerprint);
CREATE INDEX active_relay_nickname ON active_relay (LOWER(nickname));
CREATE INDEX active_relay_validafter ON active_relay (validafter);
CREATE INDEX active_relay_descriptor ON active_relay (descriptor);

-- Create the various indexes we need for searching descriptors
CREATE INDEX active_descriptor_descriptor ON active_descriptor (descriptor);
CREATE INDEX active_descriptor_published ON active_descriptor (published);
CREATE INDEX active_descriptor_fingerprint ON active_descriptor (fingerprint);

/* Though it is likely that plpgsql has already been created, since
tordir.public should have been created, create it anyway to ensure
that the below functions and triggers can be created. */
CREATE LANGUAGE plpgsql;

-- FUNCTIONS ----------------------------------------------------------
-- TRIGGER FUNCTIONS --------------------------------------------------
CREATE OR REPLACE FUNCTION update_statusentry()
    RETURNS TRIGGER AS $add_statusentry$
    BEGIN
    IF ((SELECT COUNT(*) FROM cache.active_relay
        WHERE validafter = NEW.validafter
        AND fingerprint = NEW.fingerprint) > 0
        OR (NEW.validafter < (SELECT localtimestamp) - INTERVAL '4 hours'))
        THEN
            RETURN NULL;
    ELSE IF (SELECT COUNT(*) FROM cache.active_relay
             WHERE fingerprint = NEW.fingerprint) > 0
        THEN
        BEGIN
        UPDATE cache.active_relay
        SET
            validafter = NEW.validafter,
            nickname = NEW.nickname,
            fingerprint = NEW.fingerprint,
            -- address = NEW.address::INET, doesn't work
            address = NEW.address,
            orport = NEW.orport,
            dirport = NEW.dirport,
            isauthority = NEW.isauthority,
            isbadexit = NEW.isbadexit,
            isbaddirectory = NEW.isbaddirectory,
            isexit = NEW.isexit,
            isfast = NEW.isfast,
            isguard = NEW.isguard,
            ishsdir = NEW.ishsdir,
            isnamed = NEW.isnamed,
            isstable = NEW.isstable,
            isrunning = NEW.isrunning,
            isunnamed = NEW.isunnamed,
            isvalid = NEW.isvalid,
            isv2dir = NEW.isv2dir,
            isv3dir = NEW.isv3dir,
            country = (SELECT country FROM
                       public.geoip_lookup(NEW.address)),
            latitude = (SELECT latitude FROM
                        public.geoip_lookup(NEW.address)),
            longitude = (SELECT longitude FROM
                        public.geoip_lookup(NEW.address))
        WHERE fingerprint = NEW.fingerprint;
        END;
    ELSE
        BEGIN
        INSERT INTO cache.active_relay (validafter, nickname,
            fingerprint, address, orport, dirport, isauthority,
            isbadexit, isbaddirectory, isexit, isfast, isguard,
            ishsdir, isnamed, isstable, isrunning, isunnamed, isvalid,
            isv2dir, isv3dir, country, latitude, longitude)
        VALUES
            (NEW.validafter, NEW.nickname, NEW.fingerprint,
             NEW.address, NEW.orport, NEW.dirport,
             NEW.isauthority, NEW.isbadexit, NEW.isbaddirectory,
             NEW.isexit, NEW.isfast, NEW.isguard, NEW.ishsdir,
             NEW.isnamed, NEW.isstable, NEW.isrunning,
             NEW.isunnamed, NEW.isvalid, NEW.isv2dir,
             NEW.isv3dir,
             (SELECT country FROM
              public.geoip_lookup(NEW.address)),
             (SELECT latitude FROM
              public.geoip_lookup(NEW.address)),
             (SELECT longitude FROM
              public.geoip_lookup(NEW.address))
        );
        IF (SELECT COUNT(*) FROM cache.active_descriptor
            WHERE NEW.fingerprint = fingerprint) > 0
            THEN
                PERFORM cache.insert_descriptor_info (NEW.fingerprint);
        END IF;
        END;
    END IF;
    END IF;
    RETURN NULL;
    END;
$add_statusentry$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION update_descriptor()
    RETURNS TRIGGER AS $add_descriptor$
    BEGIN
    IF ((SELECT COUNT(*) FROM cache.active_descriptor
         WHERE (descriptor = NEW.descriptor OR published > NEW.published)) > 0
         OR (NEW.published < (SELECT localtimestamp) - INTERVAL '72 hours'))
         THEN
             RETURN NULL;
    ELSE
        DECLARE
            ndescriptor CHARACTER(40) := NEW.descriptor;
            nnickname CHARACTER VARYING(19) := NEW.nickname;
            nfingerprint CHARACTER(40) := NEW.fingerprint;
            npublished TIMESTAMP WITHOUT TIME ZONE := NEW.published;
            nbandwidthavg BIGINT := NEW.bandwidthavg;
            nbandwidthburst BIGINT := NEW.bandwidthburst;
            nbandwidthobserved BIGINT := NEW.bandwidthobserved;
            nbandwidthkbps BIGINT := (NEW.bandwidthobserved / 1024);
            nplatform CHARACTER VARYING(256) := NEW.platform;
            nuptime BIGINT := NEW.uptime;
            nuptimedays BIGINT := (NEW.uptime / 86400);
            ncontact TEXT := (SELECT unnest(
                              regexp_matches(
                              CAST(NEW.rawdesc AS TEXT),
                              E'\\\\012contact\ (.*?)\\\\012'))::TEXT);
            nonionkey CHARACTER(188) := (SELECT regexp_replace(
                                         unnest(
                                         regexp_matches(
                                         CAST(NEW.rawdesc AS TEXT),
                                         E'onion-key\\\\012-----BEGIN\ RSA\ PUBLIC\ KEY-----\\\\012(.*)-----END\ RSA\ PUBLIC\ KEY-----'))::CHARACTER(188),
                                         E'\\\\012', E'\n', 'g'));
            nsigningkey CHARACTER(188) := (SELECT regexp_replace(
                                           unnest(
                                           regexp_matches(
                                           CAST(NEW.rawdesc AS TEXT),
                                           E'signing-key\\\\012-----BEGIN\ RSA\ PUBLIC\ KEY-----\\\\012(.*)-----END\ RSA\ PUBLIC\ KEY-----'))::CHARACTER(188),
                                           E'\\\\012', E'\n', 'g'));
            nexitpolicy TEXT[] := (SELECT regexp_split_to_array(
                                   unnest(
                                   regexp_matches(
                                   CAST(NEW.rawdesc AS TEXT),
                                   E'\\\\012([ar][ce][cj][e][pc][t]\ .*)\\\\012router-signature'))::TEXT, E'\\\\012'));
            nfamily TEXT := (SELECT unnest(
                             regexp_matches(
                             CAST(NEW.rawdesc AS TEXT),
                             E'\\\\012family\ (.*?)\\\\012'))::TEXT);
            nishibernating BOOLEAN := (SELECT CASE
                                       WHEN position('opt hibernating 1'
                                       in NEW.rawdesc::text) > 0 THEN TRUE
                                       ELSE FALSE END);
        BEGIN
        UPDATE cache.active_relay
        SET
            descriptor = ndescriptor,
            nickname = nnickname,
            fingerprint = nfingerprint,
            published = npublished,
            bandwidthavg = nbandwidthavg,
            bandwidthburst = nbandwidthburst,
            bandwidthobserved = nbandwidthobserved,
            bandwidthkbps = nbandwidthkbps,
            platform = nplatform,
            uptime = nuptime,
            uptimedays = nuptimedays,
            contact = ncontact,
            onionkey = nonionkey,
            signingkey = nsigningkey,
            exitpolicy = nexitpolicy,
            family = nfamily,
            ishibernating = nishibernating
        WHERE cache.active_relay.fingerprint = NEW.fingerprint
        AND CASE WHEN cache.active_relay.published IS NULL THEN '1980-01-01 01:00:00' ELSE cache.active_relay.published END < NEW.published;
        IF ((SELECT COUNT(*) FROM cache.active_descriptor
             WHERE (descriptor = ndescriptor OR published > npublished)) > 0
             OR (npublished < (SELECT localtimestamp) - INTERVAL '72 hours'))
         THEN
            RETURN NULL;
        ELSE
            DELETE FROM cache.active_descriptor
              WHERE cache.active_descriptor.fingerprint = nfingerprint
              AND cache.active_descriptor.published < npublished;
            INSERT INTO cache.active_descriptor (descriptor, nickname,
                fingerprint, published, bandwidthavg, bandwidthburst,
                bandwidthobserved, bandwidthkbps, platform, uptime,
                uptimedays, contact, onionkey, signingkey, exitpolicy,
                family, ishibernating)
            VALUES
                (ndescriptor, nnickname, nfingerprint, npublished,
                 nbandwidthavg, nbandwidthburst, nbandwidthobserved,
                 nbandwidthkbps, nplatform, nuptime, nuptimedays,
                 ncontact, nonionkey, nsigningkey, nexitpolicy, nfamily,
                 nishibernating);
        END IF;
        END;
    END IF;
    RETURN NULL;
    END;
$add_descriptor$ LANGUAGE plpgsql;

-- Helper functions ---------------------------------------------------
CREATE OR REPLACE FUNCTION insert_descriptor_info (
    given_fingerprint CHARACTER(40))
    RETURNS INTEGER AS $$
    DECLARE
        ndescriptor CHARACTER(40);
        nnickname CHARACTER VARYING(19);
        nfingerprint CHARACTER(40);
        npublished TIMESTAMP WITHOUT TIME ZONE;
        nbandwidthavg BIGINT;
        nbandwidthburst BIGINT;
        nbandwidthobserved BIGINT;
        nbandwidthkbps BIGINT;
        nplatform CHARACTER VARYING(256);
        nuptime BIGINT;
        nuptimedays BIGINT;
        ncontact TEXT;
        nonionkey CHARACTER(188);
        nsigningkey CHARACTER(188);
        nexitpolicy TEXT[];
        nfamily TEXT;
        nishibernating BOOLEAN;
    BEGIN
      SELECT INTO ndescriptor, nnickname, nfingerprint, npublished,
                  nbandwidthavg, nbandwidthburst, nbandwidthobserved,
                  nbandwidthkbps, nplatform, nuptime, nuptimedays,
                  ncontact, nonionkey, nsigningkey, nexitpolicy, nfamily,
                  nishibernating

                  descriptor, nickname, fingerprint, published,
                  bandwidthavg, bandwidthburst, bandwidthobserved,
                  bandwidthkbps, platform, uptime, uptimedays,
                  contact, onionkey, signingkey, exitpolicy, family,
                  nishibernating
                  FROM cache.active_descriptor
                  WHERE fingerprint = given_fingerprint;
    UPDATE cache.active_relay
    SET
        descriptor = ndescriptor,
        nickname = nnickname,
        fingerprint = nfingerprint,
        published = npublished,
        bandwidthavg = nbandwidthavg,
        bandwidthburst = nbandwidthburst,
        bandwidthobserved = nbandwidthobserved,
        bandwidthkbps = nbandwidthkbps,
        platform = nplatform,
        uptime = nuptime,
        uptimedays = nuptimedays,
        contact = ncontact,
        onionkey = nonionkey,
        signingkey = nsigningkey,
        exitpolicy = nexitpolicy,
        family = nfamily,
        ishibernating = nishibernating
    WHERE cache.active_relay.fingerprint = given_fingerprint;
    RETURN 1;
    END;
$$ LANGUAGE plpgsql;


-- Purging functions --------------------------------------------------
-- Keep descriptors for no more than 36 hours
CREATE OR REPLACE FUNCTION purge_descriptor()
RETURNS INTEGER AS $$
    BEGIN
    DELETE FROM cache.active_descriptor
    WHERE published < (SELECT localtimestamp) - INTERVAL '36 hours';
RETURN 1;
END;
$$ LANGUAGE plpgsql;

-- Keep relays for no more than 4 hours
CREATE OR REPLACE FUNCTION purge_relay()
RETURNS INTEGER AS $$
    BEGIN
    DELETE FROM cache.active_relay
    WHERE validafter < (SELECT localtimestamp) - INTERVAL '4 hours';
RETURN 1;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION purge()
RETURNS INTEGER AS $$
    BEGIN
    PERFORM purge_descriptor();
    PERFORM purge_relay();
RETURN 1;
END;
$$ LANGUAGE plpgsql;

-- TRIGGERS -----------------------------------------------------------
-- Add descriptors
CREATE TRIGGER add_descriptor
    BEFORE UPDATE OR INSERT ON public.descriptor
    FOR EACH ROW
    EXECUTE PROCEDURE update_descriptor();

-- Add statusentries
CREATE TRIGGER add_statusentry
    BEFORE UPDATE OR INSERT ON public.statusentry
    FOR EACH ROW
    EXECUTE PROCEDURE update_statusentry();

-- Set search_path back to public.
SET search_path TO public;
