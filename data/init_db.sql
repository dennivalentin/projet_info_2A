-- ============================================================================
-- NEO-Watch Database Schema
-- ============================================================================

DROP TABLE IF EXISTS import CASCADE;
DROP TABLE IF EXISTS proposal CASCADE;
DROP TABLE IF EXISTS alert CASCADE;
DROP TABLE IF EXISTS search CASCADE;
DROP TABLE IF EXISTS connection CASCADE;
DROP TABLE IF EXISTS favourite CASCADE;
DROP TABLE IF EXISTS approach CASCADE;
DROP TABLE IF EXISTS neo CASCADE;
DROP TABLE IF EXISTS "user" CASCADE;

-- ============================================================================
-- 1. USER
-- ============================================================================
CREATE TABLE "user" (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(30) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    role VARCHAR(15) NOT NULL DEFAULT 'user',
    creation_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO "user" (user_id, username, password_hash, email, role)
VALUES (1, 'admin', 'admin_password_hash', 'admin@email.fr', 'admin')
ON CONFLICT (user_id) DO NOTHING;

-- ============================================================================
-- 2. NEO
-- ============================================================================
CREATE TABLE neo (
    neo_id SERIAL PRIMARY KEY,
    nasa_id VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    absolute_magnitude NUMERIC(5, 2),
    diameter_min NUMERIC(10, 2),
    diameter_max NUMERIC(10, 2),
    hazardous BOOLEAN NOT NULL DEFAULT FALSE,
    url_nasa VARCHAR(500),
    origin VARCHAR(12) NOT NULL DEFAULT 'nasa',
    date_update TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 3. APPROACH (Closest approaches to Earth)
-- ============================================================================
CREATE TABLE approach (
    approach_id SERIAL PRIMARY KEY,
    neo_id INTEGER NOT NULL REFERENCES neo(neo_id) ON DELETE CASCADE,
    approach_day DATE NOT NULL,
    approach_date TIMESTAMP NOT NULL,
    body VARCHAR(20), 
    distance NUMERIC(15, 2) NOT NULL,
    speed NUMERIC(10, 2),
    creation_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_neo_approach_day UNIQUE (neo_id, approach_day)
);

-- ============================================================================
-- 4. CONNECTION
-- ============================================================================

CREATE TABLE connection (
    connection_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE,
    connection_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    access_token VARCHAR(64) UNIQUE  -- NULL once the user has logged out
);

-- ============================================================================
-- 5. FAVOURITE
-- ============================================================================
CREATE TABLE favourite (
    user_id INTEGER NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE,
    neo_id INTEGER NOT NULL REFERENCES neo(neo_id) ON DELETE CASCADE,
    date_added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, neo_id)
);

-- ============================================================================
-- 6. SEARCH
-- ============================================================================
CREATE TABLE search (
    search_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE,
    search_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    criteria VARCHAR(255),
    neo_id INTEGER REFERENCES neo(neo_id) ON DELETE SET NULL
);

-- ============================================================================
-- 7. PROPOSAL
-- ============================================================================
CREATE TABLE proposal (
    proposal_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE,
    neo_id INTEGER NOT NULL REFERENCES neo(neo_id) ON DELETE CASCADE,
    field_name VARCHAR(30) NOT NULL,
    proposed_value VARCHAR(255),
    justification TEXT,
    submission_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(12) NOT NULL DEFAULT 'pending' -- then 'approved' or 'rejected'
);

-- ============================================================================
-- 8. ALERT
-- ============================================================================
CREATE TABLE alert (
    alert_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE,
    label VARCHAR(100) NOT NULL,
    distance_max NUMERIC(15, 2),  
    diameter_min NUMERIC(10, 2),  
    hazardous_only BOOLEAN NOT NULL DEFAULT FALSE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    creation_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_eval_date TIMESTAMP
);

-- ============================================================================
-- 9. IMPORT 
-- ============================================================================
CREATE TABLE import (
    import_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    trigger_type VARCHAR(10),  -- 'manual' or 'auto'
    status VARCHAR(15) NOT NULL DEFAULT 'running',  -- then 'success' or 'failed'
    nb_calls INTEGER,  --number of API calls made
    nb_neo INTEGER,   -- number of NEO imported
    nb_approaches INTEGER,  
    import_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX idx_approach_neo ON approach(neo_id);
CREATE INDEX idx_approach_date ON approach(approach_day);
CREATE INDEX idx_neo_nasa_id ON neo(nasa_id);
CREATE INDEX idx_connection_user ON connection(user_id);
CREATE INDEX idx_connection_date ON connection(connection_date);
CREATE INDEX idx_favourite_user ON favourite(user_id);
CREATE INDEX idx_search_user ON search(user_id);
CREATE INDEX idx_search_neo ON search(neo_id);
CREATE INDEX idx_proposal_user ON proposal(user_id);
CREATE INDEX idx_proposal_neo ON proposal(neo_id);
CREATE INDEX idx_alert_user ON alert(user_id);
CREATE INDEX idx_alert_active ON alert(active);
CREATE INDEX idx_import_user ON import(user_id);

/*
CREATE TABLE IF NOT EXISTS app_user (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    creation_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    role VARCHAR(50) NOT NULL DEFAULT 'regular'
);


INSERT INTO app_user(user_id, username, email, password_hash, role) 
VALUES (1, 'admin', 'admin@email.fr', 'admin_password_hash', 'ADMIN')
ON CONFLICT (user_id) DO NOTHING;


CREATE TABLE IF NOT EXISTS connection (
    connection_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES app_user(user_id) ON DELETE CASCADE,
    date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS import (
    import_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES app_user(user_id) ON DELETE CASCADE,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    trigger_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    nb_calls INT DEFAULT 0,
    nb_neo INT DEFAULT 0,
    nb_approaches INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS neo (
    neo_id SERIAL PRIMARY KEY,
    nasa_id VARCHAR(50) UNIQUE,
    name VARCHAR(255) NOT NULL,
    absolute_magnitude FLOAT,
    diameter_min FLOAT,
    diameter_max FLOAT,
    hazardious BOOLEAN NOT NULL DEFAULT FALSE,
    url_nasa TEXT,
    custom BOOLEAN NOT NULL DEFAULT FALSE,
    date_update TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS approach CASCADE;

CREATE TABLE IF NOT EXISTS approach (
    approach_id SERIAL PRIMARY KEY,
    neo_id INT NOT NULL REFERENCES neo(neo_id) ON DELETE CASCADE,
    approach_date TIMESTAMP NOT NULL,
    distance FLOAT NOT NULL,
    speed FLOAT NOT NULL,
    body VARCHAR(100) NOT NULL,
    CONSTRAINT uq_approach_neo_day_body UNIQUE (neo_id, approach_date, body)
);

CREATE TABLE IF NOT EXISTS favourite (
    neo_id INT NOT NULL REFERENCES neo(neo_id) ON DELETE CASCADE,
    user_id INT NOT NULL REFERENCES app_user(user_id) ON DELETE CASCADE,
    date_added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (neo_id, user_id)
);

CREATE TABLE IF NOT EXISTS alert (
    alert_id SERIAL PRIMARY KEY,
    neo_id INT REFERENCES neo(neo_id) ON DELETE SET NULL,
    user_id INT NOT NULL REFERENCES app_user(user_id) ON DELETE CASCADE,
    min_diameter FLOAT,
    max_distance FLOAT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS proposal (
    proposal_id SERIAL PRIMARY KEY,
    neo_id INT REFERENCES neo(neo_id) ON DELETE SET NULL,
    user_id INT NOT NULL REFERENCES app_user(user_id) ON DELETE CASCADE,
    submission_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    field_name VARCHAR(100) NOT NULL,
    proposed_value TEXT NOT NULL,
    justification TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS search (
    search_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES app_user(user_id) ON DELETE CASCADE,
    search_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    criteria TEXT NOT NULL,
    neo_id INT REFERENCES neo(neo_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS apod_data (
    apod_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    date TIMESTAMP NOT NULL,
    caption TEXT,
    url TEXT NOT NULL
);
*/

