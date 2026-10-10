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


