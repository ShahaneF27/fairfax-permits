-- rebuild from scratch each run (child table first)
DROP TABLE IF EXISTS permit;
DROP TABLE IF EXISTS record_types;
DROP TABLE IF EXISTS districts;
DROP TABLE IF EXISTS growth_centers;

CREATE TABLE record_types (
    record_type_id INTEGER PRIMARY KEY,
    record_type    TEXT NOT NULL UNIQUE,
    category       TEXT NOT NULL
        CHECK (category IN ('Construction', 'Business Occupancy', 'Certificate of Occupancy')),
    sector         TEXT NOT NULL
        CHECK (sector IN ('Residential', 'Commercial', 'Unspecified'))
);

CREATE TABLE districts (
    district_id    INTEGER PRIMARY KEY,
    district_name  TEXT NOT NULL UNIQUE
);

CREATE TABLE growth_centers (
    growth_center_id   INTEGER PRIMARY KEY,
    growth_center_name TEXT NOT NULL UNIQUE
);

CREATE TABLE permits (
        record_id        TEXT PRIMARY KEY,
    record_type_id   INTEGER NOT NULL REFERENCES record_types (record_type_id),
    district_id      INTEGER NOT NULL REFERENCES districts (district_id),
    growth_center_id INTEGER REFERENCES growth_centers (growth_center_id),
    project_name     TEXT,
    parcel_id        TEXT,
    address          TEXT,
    city             TEXT,
    zip5             TEXT,
    record_status    TEXT NOT NULL,
    status_date      TEXT,
    submitted_date   TEXT,
    accepted_date    TEXT,
    issued_date      TEXT,
    approved_date    TEXT,
    closed_date      TEXT,
    days_to_decision INTEGER CHECK (days_to_decision IS NULL OR days_to_decision >= 0),
    is_open          INTEGER NOT NULL CHECK (is_open IN (0, 1))
);