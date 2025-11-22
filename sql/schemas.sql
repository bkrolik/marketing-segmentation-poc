CREATE SCHEMA IF NOT EXISTS residents;

CREATE TABLE IF NOT EXISTS residents.resident_core (
    pseudonymous_id VARCHAR,
    age INT,
    income_band INT,
    kids_flag BOOLEAN,
    distance_miles FLOAT
);
