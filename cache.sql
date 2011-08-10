-- Create a schema and set it as the search path.
CREATE SCHEMA cache;
SET search_path TO cache;

-- TABLES -------------------------------------------------------------
-- TABLE active_descriptor
-- Contains descriptors published by routers in the last 48 hours.
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
    CONSTRAINT active_descriptor_unique PRIMARY KEY (fingerprint)
);


-- TABLE active_statusentry
-- Contains statusentries published in the last 4 hours.
CREATE TABLE active_statusentry (
    validafter TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    nickname CHARACTER VARYING(19) NOT NULL,
    fingerprint CHARACTER(40) NOT NULL,
    address INET NOT NULL,
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
    country CHARACTER VARYING(2),
    latitude NUMERIC(7, 4),
    longitude NUMERIC(7, 4),
    CONSTRAINT active_statusentry_unique PRIMARY KEY (fingerprint)
);


-- TABLE active_relay
-- Contains all relevant information about a relay that might be needed
-- for TorStatus.
CREATE TABLE active_relay (
    validafter TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    nickname CHARACTER VARYING(19) NOT NULL,
    fingerprint CHARACTER(40) NOT NULL,
    address INET NOT NULL,
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
-- Later, could do lookup with socket.getfqdn (plpythonu)
-- CREATE TABLE hostname (
--    address INET NOT NULL,
--    hostname CHARACTER VARYING(255),
--    CONSTRAINT hostname_unique PRIMARY KEY (address)
--);


-- INDICES ------------------------------------------------------------
-- Create the various indexes we need for searching descriptors
CREATE INDEX active_descriptor_published ON active_descriptor (published);
CREATE INDEX active_descriptor_fingerprint ON active_descriptor (fingerprint);

-- Create the various indexes we need for searching active relays
CREATE INDEX active_statusentry_fingerprint ON active_statusentry (fingerprint);
CREATE INDEX active_statusentry_validafter ON active_statusentry (validafter);

-- Create the lookups necessary for a functioning all-purpose relay
-- table.
CREATE INDEX active_relay_fingerprint ON active_relay (fingerprint);
CREATE INDEX active_relay_nickname ON active_relay (LOWER(nickname));
CREATE INDEX active_relay_validafter ON active_relay (validafter);
CREATE INDEX active_relay_descriptor ON active_relay (descriptor);


/* Though it is likely that plpgsql has already been created, since
tordir.public should have been created, create it anyway to ensure
that the below functions and triggers can be created. */
CREATE LANGUAGE plpgsql;


-- FUNCTIONS ----------------------------------------------------------
-- TRIGGER FUNCTIONS --------------------------------------------------
CREATE OR REPLACE FUNCTION update_descriptor()
    RETURNS TRIGGER AS $add_descriptor$
    BEGIN
        IF (SELECT COUNT(*) FROM cache.active_descriptor
            WHERE cache.active_descriptor.fingerprint = NEW.fingerprint
            AND cache.active_descriptor.published > NEW.published
            AND NEW.published > (SELECT localtimestamp at time zone 'UTC'
                                 - INTERVAL '48 hours')) > 0
            THEN
                RETURN NULL;
        ELSE
            BEGIN
                DELETE FROM cache.active_descriptor
                WHERE cache.active_descriptor.fingerprint = NEW.fingerprint;
                INSERT INTO cache.active_descriptor (descriptor,
                    nickname, fingerprint, published, bandwidthavg,
                    bandwidthburst, bandwidthobserved, bandwidthkbps,
                    platform, uptime, uptimedays, contact, onionkey,
                    signingkey, exitpolicy, family, ishibernating)
                VALUES (NEW.descriptor, NEW.nickname, NEW.fingerprint,
                    NEW.published, NEW.bandwidthavg,
                    NEW.bandwidthburst, NEW.bandwidthobserved,
                    (NEW.bandwidthobserved / 1024), NEW.platform,
                    NEW.uptime, (NEW.uptime / 86400),
                    (SELECT unnest(
                                regexp_matches(
                                    CAST(NEW.rawdesc AS TEXT),
                                    E'\\\\012contact\ (.*?)\\\\012'))::TEXT),
                    (SELECT regexp_replace(
                                unnest(
                                    regexp_matches(
                                        CAST(NEW.rawdesc AS TEXT),
                                        E'onion-key\\\\012-----BEGIN\ RSA\ PUBLIC\ KEY-----\\\\012(.*)-----END\ RSA\ PUBLIC\ KEY-----'))::CHARACTER(188),
                                E'\\\\012', E'\n', 'g')),
                    (SELECT regexp_replace(
                                unnest(
                                    regexp_matches(
                                        CAST(NEW.rawdesc AS TEXT),
                                        E'signing-key\\\\012-----BEGIN\ RSA\ PUBLIC\ KEY-----\\\\012(.*)-----END\ RSA\ PUBLIC\ KEY-----'))::CHARACTER(188),
                                E'\\\\012', E'\n', 'g')),
                    (SELECT regexp_split_to_array(
                                unnest(
                                    regexp_matches(
                                        CAST(NEW.rawdesc AS TEXT),
                                        E'\\\\012([ar][ce][cj][e][pc][t]\ .*)\\\\012router-signature'))::TEXT,
                                E'\\\\012')),
                    (SELECT unnest(
                                regexp_matches(
                                    CAST(NEW.rawdesc AS TEXT),
                                    E'\\\\012family\ (.*?)\\\\012'))::TEXT),
                    (SELECT CASE WHEN position('opt hibernating 1'
                                 IN NEW.rawdesc::text) > 0 THEN TRUE
                                 ELSE FALSE END));
            END;
        END IF;
    RETURN NULL;
    END;
$add_descriptor$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION update_statusentry()
    RETURNS TRIGGER AS $add_statusentry$
    BEGIN
        IF (SELECT COUNT(*) FROM cache.active_statusentry
            WHERE validafter >= NEW.validafter
            AND fingerprint = NEW.fingerprint
            AND NEW.validafter > (SELECT localtimestamp AT TIME ZONE 'UTC'
                                  - INTERVAL '4 hours')) > 0
            THEN
                RETURN NULL;
        ELSE
            BEGIN
                DELETE FROM cache.active_statusentry
                WHERE cache.active_statusentry.fingerprint = NEW.fingerprint;
                INSERT INTO cache.active_statusentry (validafter,
                    nickname, fingerprint, address, orport, dirport,
                    isauthority, isbadexit, isbaddirectory, isexit,
                    isfast, isguard, ishsdir, isnamed, isstable,
                    isrunning, isunnamed, isvalid, isv2dir, isv3dir,
                    country, latitude, longitude)
                VALUES (NEW.validafter, NEW.nickname, NEW.fingerprint,
                    INET(NEW.address::varchar), NEW.orport,
                    NEW.dirport, NEW.isauthority, NEW.isbadexit,
                    NEW.isbaddirectory, NEW.isexit, NEW.isfast,
                    NEW.isguard, NEW.ishsdir, NEW.isnamed, NEW.isstable,
                    NEW.isrunning, NEW.isunnamed, NEW.isvalid,
                    NEW.isv2dir, NEW.isv3dir,
                    (SELECT country FROM
                     public.geoip_lookup(NEW.address)),
                    (SELECT latitude FROM
                     public.geoip_lookup(NEW.address)),
                    (SELECT longitude FROM
                     public.geoip_lookup(NEW.address)));
            END;
        END IF;
    RETURN NULL;
    END;
$add_statusentry$ LANGUAGE plpgsql;


-- PURGING FUNCTIONS --------------------------------------------------
-- Keep descriptors for no more than 48 hours.
CREATE OR REPLACE FUNCTION purge_descriptor()
RETURNS INTEGER AS $$
    BEGIN
        DELETE FROM cache.active_descriptor
        WHERE published < (SELECT localtimestamp AT TIME ZONE 'UTC')
                          - INTERVAL '48 hours';
    RETURN 1;
    END;
$$ LANGUAGE plpgsql;


-- Keep statusentries for no more than 4 hours.
CREATE OR REPLACE FUNCTION purge_statusentry()
RETURNS INTEGER AS $$
    BEGIN
        DELETE FROM cache.active_statusentry
        WHERE validafter < (SELECT localtimestamp AT TIME ZONE 'UTC')
                            - INTERVAL '4 hours';
    RETURN 1;
    END;
$$ LANGUAGE plpgsql;


-- NOTE: ADD A CRONTAB FOR THIS FUNCTION, MAYBE 25 * * * *.
CREATE OR REPLACE FUNCTION purge()
RETURNS INTEGER AS $$
    BEGIN
        PERFORM cache.purge_descriptor();
        PERFORM cache.purge_statusentry();
    RETURN 1;
    END;
$$ LANGUAGE plpgsql;


-- JOINING FUNCTION ---------------------------------------------------
-- This function actually updates the table that is used for TorStatus.
-- NOTE: ADD A CRONTAB FOR THIS FUNCTION, MAYBE 20 * * * *.
CREATE OR REPLACE FUNCTION update_relay_table()
RETURNS INTEGER AS $$
    BEGIN
        TRUNCATE TABLE cache.active_relay;
        INSERT INTO cache.active_relay (validafter, nickname,
            fingerprint, address, orport, dirport, isauthority,
            isbadexit, isbaddirectory, isexit, isfast, isguard,
            ishsdir, isnamed, isstable, isrunning, isunnamed,
            isvalid, isv2dir, isv3dir, descriptor, published,
            bandwidthavg, bandwidthburst, bandwidthobserved,
            bandwidthkbps, uptime, uptimedays, platform,
            contact, onionkey, signingkey, exitpolicy, family,
            ishibernating, country, latitude, longitude)
        SELECT s.validafter, s.nickname, s.fingerprint, s.address,
            s.orport, s.dirport, s.isauthority, s.isbadexit,
            s.isbaddirectory, s.isexit, s.isfast, s.isguard,
            s.ishsdir, s.isnamed, s.isstable, s.isrunning, s.isunnamed,
            s.isvalid, s.isv2dir, s.isv3dir, d.descriptor, d.published,
            d.bandwidthavg, d.bandwidthburst, d.bandwidthobserved,
            d.bandwidthkbps, d.uptime, d.uptimedays, d.platform,
            d.contact, d.onionkey, d.signingkey, d.exitpolicy, d.family,
            d.ishibernating, s.country, s.latitude, s.longitude
            FROM
                cache.active_statusentry AS s
                LEFT JOIN cache.active_descriptor as d
                ON s.fingerprint=d.fingerprint;
    RETURN 1;
    END;
$$ LANGUAGE plpgsql;


-- TRIGGERS -----------------------------------------------------------
-- Add descriptors
CREATE TRIGGER add_descriptor
    AFTER UPDATE OR INSERT ON public.descriptor
    FOR EACH ROW
    EXECUTE PROCEDURE update_descriptor();


-- Add statusentries
CREATE TRIGGER add_statusentry
    AFTER UPDATE OR INSERT ON public.statusentry
    FOR EACH ROW
    EXECUTE PROCEDURE update_statusentry();


-- Set search_path back to public.
SET search_path TO public;
