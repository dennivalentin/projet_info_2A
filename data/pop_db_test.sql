-- Test seed data for NEO-Watch DAO tests

INSERT INTO "user" (user_id, username, password_hash, email, role) VALUES
(999, 'admin_test', 'c7ad44cbad762a5da0a452f9e854fdc1e0e7a52a38015f23f3eab1d80b931dd472634dfac71cd34ebc35d16ab7fb8a90c81f975113d6c7538dc69dd8de9077ec', 'admin_test@email.fr', 'admin'),
(998, 'user_test', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'user_test@email.fr', 'user')
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO neo (neo_id, nasa_id, name, absolute_magnitude, diameter_min, diameter_max, hazardous, url_nasa, origin) VALUES
(999, '9999999', 'Test Asteroid 1', 20.0, 0.1, 0.2, TRUE, 'https://ssd.jpl.nasa.gov', 'NASA'),
(998, '9999998', 'Test Asteroid 2', 22.0, 0.05, 0.1, FALSE, 'https://ssd.jpl.nasa.gov', 'NASA')
ON CONFLICT (neo_id) DO NOTHING;

INSERT INTO approach (neo_id, approach_day, approach_date, body, distance, speed) VALUES
(999, CURRENT_DATE + INTERVAL '1 day', CURRENT_TIMESTAMP + INTERVAL '1 day', 'Earth', 5000000.0, 50000.0),
(998, CURRENT_DATE + INTERVAL '2 days', CURRENT_TIMESTAMP + INTERVAL '2 days', 'Earth', 10000000.0, 30000.0)
ON CONFLICT DO NOTHING;
