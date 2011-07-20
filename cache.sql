-- Create a schema and set it as the search path.
CREATE SCHEMA cache;
SET search_path TO cache;

-- Make UTC the timezone. This should not be changed.
SET TIME ZONE UTC;

-- TABLE active_descriptor
-- Contains descriptors published by routers in the last 20 hours.
CREATE TABLE active_descriptor (
    descriptor CHARACTER(40) NOT NULL,
    nickname CHARACTER VARYING(19) NOT NULL,
    fingerprint CHARACTER(40) NOT NULL,
    published TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    bandwidthavg BIGINT NOT NULL,
    bandwidthburst BIGINT NOT NULL,
    bandwidthobserved BIGINT NOT NULL,
    platform CHARACTER VARYING(256),
    uptime BIGINT,
    rawdesc BYTEA NOT NULL,
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
    exitpolicy TEXT,
    family TEXT,
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
CREATE OR REPLACE FUNCTION update_statusentry_relay()
    RETURNS TRIGGER AS $update_statusentry$
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
                PERFORM cache.insert_descriptor_info (
                    (SELECT descriptor FROM cache.active_descriptor
                     WHERE fingerprint = NEW.fingerprint),
                    (SELECT nickname FROM cache.active_descriptor
                     WHERE fingerprint = NEW.fingerprint),
                    (SELECT fingerprint FROM cache.active_descriptor
                     WHERE fingerprint = NEW.fingerprint),
                    (SELECT published FROM cache.active_descriptor
                     WHERE fingerprint = NEW.fingerprint),
                    (SELECT bandwidthavg FROM cache.active_descriptor
                     WHERE fingerprint = NEW.fingerprint),
                    (SELECT bandwidthburst FROM cache.active_descriptor
                     WHERE fingerprint = NEW.fingerprint),
                    (SELECT bandwidthobserved FROM cache.active_descriptor
                     WHERE fingerprint = NEW.fingerprint),
                    (SELECT platform FROM cache.active_descriptor
                     WHERE fingerprint = NEW.fingerprint),
                    (SELECT uptime FROM cache.active_descriptor
                     WHERE fingerprint = NEW.fingerprint),
                    (SELECT rawdesc FROM cache.active_descriptor
                     WHERE fingerprint = NEW.fingerprint)
                );
        END IF;
        END;
    END IF;
    END IF;
    RETURN NULL;
    END;
$update_statusentry$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION update_descriptor_relay()
    RETURNS TRIGGER AS $add_descriptor$
    BEGIN
    IF ((SELECT COUNT(*) FROM cache.active_descriptor
         WHERE (descriptor = NEW.descriptor OR published > NEW.published)) > 0
         OR (NEW.published < (SELECT localtimestamp) - INTERVAL '72 hours'))
         THEN
             RETURN NULL;
    ELSE
        BEGIN
        UPDATE cache.active_relay
        SET
            descriptor = NEW.descriptor,
            nickname = NEW.nickname,
            fingerprint = NEW.fingerprint,
            published = NEW.published,
            bandwidthavg = NEW.bandwidthavg,
            bandwidthburst = NEW.bandwidthburst,
            bandwidthobserved = NEW.bandwidthobserved,
            bandwidthkbps = (NEW.bandwidthobserved / 1024),
            platform = NEW.platform,
            uptime = NEW.uptime,
            uptimedays = (NEW.uptime / 86400),
            contact = (SELECT regexp_replace(
                       unnest(
                       regexp_matches(
                       CAST(NEW.rawdesc AS TEXT),
                       E'contact\ ([^\\\\012]*)'))::TEXT,
                       E'\\\\012', E'\n', 'g')),
            onionkey = (SELECT regexp_replace(
                        unnest(
                        regexp_matches(
                        CAST(NEW.rawdesc AS TEXT),
                        E'onion-key\\\\012-----BEGIN\ RSA\ PUBLIC\ KEY-----\\\\012(.*)-----END\ RSA\ PUBLIC\ KEY-----'))::CHARACTER(188),
                        E'\\\\012', E'\n', 'g')),
            signingkey = (SELECT regexp_replace(
                          unnest(
                          regexp_matches(
                          CAST(NEW.rawdesc AS TEXT),
                          E'signing-key\\\\012-----BEGIN\ RSA\ PUBLIC\ KEY-----\\\\012(.*)-----END\ RSA\ PUBLIC\ KEY-----'))::CHARACTER(188),
                          E'\\\\012', E'\n', 'g')),
            exitpolicy = (SELECT regexp_replace(
                          unnest(
                          regexp_matches(
                          CAST(NEW.rawdesc AS TEXT),
                          E'\\\\012([ar][ce][cj][e][pc][t]\ .*)\\\\012router-signature'))::TEXT,
                          E'\\\\012', E'\n', 'g')),
            family = (SELECT unnest(
                      regexp_matches(
                      CAST(NEW.rawdesc AS TEXT),
                      E'\\\\012family\ (.*?)\\\\012'))::TEXT)
        WHERE cache.active_relay.fingerprint = NEW.fingerprint
        AND CASE WHEN cache.active_relay.published IS NULL THEN '1980-01-01 01:00:00' ELSE cache.active_relay.published END < NEW.published;
        END;
    END IF;
    RETURN NULL;
    END;
$add_descriptor$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION update_descriptor_descriptor()
    RETURNS TRIGGER AS $cache_descriptor$
    BEGIN
    IF ((SELECT COUNT(*) FROM cache.active_descriptor
         WHERE (descriptor = NEW.descriptor OR published > NEW.published)) > 0
         OR (NEW.published < (SELECT localtimestamp) - INTERVAL '72 hours'))
         THEN
            RETURN NULL;
    ELSE
        BEGIN
        DELETE FROM cache.active_descriptor
          WHERE cache.active_descriptor.fingerprint = NEW.fingerprint
          AND cache.active_descriptor.published < NEW.published;
        INSERT INTO cache.active_descriptor (descriptor, nickname,
            fingerprint, published, bandwidthavg, bandwidthburst,
            bandwidthobserved, platform, uptime, rawdesc)
        VALUES
            (NEW.descriptor, NEW.nickname, NEW.fingerprint,
             NEW.published, NEW.bandwidthavg, NEW.bandwidthburst,
             NEW.bandwidthobserved, NEW.platform, NEW.uptime,
             NEW.rawdesc);
        END;
    END IF;
    RETURN NULL;
    END;
$cache_descriptor$ LANGUAGE plpgsql;


-- Helper functions ---------------------------------------------------
CREATE OR REPLACE FUNCTION insert_descriptor_info (
    insert_descriptor CHARACTER(40), insert_nickname CHARACTER VARYING(19),
    insert_fingerprint CHARACTER(40), insert_published TIMESTAMP WITHOUT TIME ZONE,
    insert_bandwidthavg BIGINT, insert_bandwidthburst BIGINT,
    insert_bandwidthobserved BIGINT, insert_platform CHARACTER VARYING(256),
    insert_uptime BIGINT, insert_rawdesc BYTEA)
    RETURNS INTEGER AS $$
    BEGIN
    IF (SELECT COUNT(*) FROM cache.active_relay
        WHERE descriptor = insert_descriptor) > 0
        THEN
            RETURN 0;
    ELSE
        BEGIN
        UPDATE cache.active_relay
        SET
            descriptor = insert_descriptor,
            nickname = insert_nickname,
            fingerprint = insert_fingerprint,
            published = insert_published,
            bandwidthavg = insert_bandwidthavg,
            bandwidthburst = insert_bandwidthburst,
            bandwidthobserved = insert_bandwidthobserved,
            bandwidthkbps = (insert_bandwidthobserved / 1024),
            platform = insert_platform,
            uptime = insert_uptime,
            uptimedays = (insert_uptime / 86400),
            contact = (SELECT regexp_replace(
                       unnest(
                       regexp_matches(
                       CAST(insert_rawdesc AS TEXT),
                       E'contact\ ([^\\\\012]*)'))::TEXT,
                       E'\\\\012', E'\n', 'g')),
            onionkey = (SELECT regexp_replace(
                        unnest(
                        regexp_matches(
                        CAST(insert_rawdesc AS TEXT),
                        E'onion-key\\\\012-----BEGIN\ RSA\ PUBLIC\ KEY-----\\\\012(.*)-----END\ RSA\ PUBLIC\ KEY-----'))::CHARACTER VARYING(200),
                        E'\\\\012', E'\n', 'g')),
            signingkey = (SELECT regexp_replace(
                          unnest(
                          regexp_matches(
                          CAST(insert_rawdesc AS TEXT),
                          E'signing-key\\\\012-----BEGIN\ RSA\ PUBLIC\ KEY-----\\\\012(.*)-----END\ RSA\ PUBLIC\ KEY-----'))::CHARACTER VARYING(200),
                          E'\\\\012', E'\n', 'g')),
            exitpolicy = (SELECT regexp_replace(
                          unnest(
                          regexp_matches(
                          CAST(insert_rawdesc AS TEXT),
                          E'\\\\012([ar][ce][cj][e][pc][t]\ .*)\\\\012router-signature'))::TEXT,
                          E'\\\\012', E'\n', 'g')),
            family = (SELECT unnest(
                      regexp_matches(
                      CAST(insert_rawdesc AS TEXT),
                      E'\\\\012family\ (.*?)\\\\012'))::TEXT)
        WHERE cache.active_relay.fingerprint = insert_fingerprint;
        END;
    END IF;
    RETURN 1;
    END;
$$ LANGUAGE plpgsql;


-- Purging functions --------------------------------------------------
-- Keep descriptors for no more than 36 hours
CREATE OR REPLACE FUNCTION purge_descriptor()
RETURNS TRIGGER AS $check_to_purge_descriptor$
    BEGIN
    DELETE FROM cache.active_descriptor
    WHERE published < (SELECT localtimestamp) - INTERVAL '36 hours';
RETURN NULL;
END;
$check_to_purge_descriptor$ LANGUAGE plpgsql;

-- Keep relays for no more than 4 hours
CREATE OR REPLACE FUNCTION purge_relay()
RETURNS TRIGGER AS $check_to_purge_relay$
    BEGIN
    DELETE FROM cache.active_relay
    WHERE validafter < (SELECT localtimestamp) - INTERVAL '4 hours';
RETURN NULL;
END;
$check_to_purge_relay$ LANGUAGE plpgsql;

-- TRIGGERS -----------------------------------------------------------
-- Add and purge descriptors
CREATE TRIGGER cache_descriptor
    BEFORE UPDATE OR INSERT ON public.descriptor
    FOR EACH ROW
    EXECUTE PROCEDURE update_descriptor_descriptor();

CREATE TRIGGER add_descriptor
    BEFORE UPDATE OR INSERT ON public.descriptor
    FOR EACH ROW
    EXECUTE PROCEDURE update_descriptor_relay();

CREATE TRIGGER check_to_purge_descriptor
    AFTER UPDATE OR INSERT ON active_descriptor
    FOR EACH STATEMENT
    EXECUTE PROCEDURE purge_descriptor();


-- Add and purge statusentries
CREATE TRIGGER update_statusentry
    BEFORE UPDATE OR INSERT ON public.statusentry
    FOR EACH ROW
    EXECUTE PROCEDURE update_statusentry_relay();

CREATE TRIGGER check_to_purge_relay
    AFTER UPDATE OR INSERT ON active_relay
    FOR EACH STATEMENT
    EXECUTE PROCEDURE purge_relay();

-- Set search_path back to public.
SET search_path TO public;
