-- Initial seed data for NEO-Watch
-- Passwords:
-- admin: admin (hash with salt admin = d82494f05d6917ba02f7aaa29689ccb444bb73f20380876cb05d1f37537b7892)
-- observateur: observateur (hash with salt observateur = 4ad7a99ce3b84d1ef4458541d8251ab1965f29f72abcaa470e63a918d857f674)

INSERT INTO "user" (username, password_hash, email, role) VALUES
('admin', 'd82494f05d6917ba02f7aaa29689ccb444bb73f20380876cb05d1f37537b7892', 'admin@email.fr', 'admin'),
('observateur', '4ad7a99ce3b84d1ef4458541d8251ab1965f29f72abcaa470e63a918d857f674', 'obs@ensai.fr', 'user')
ON CONFLICT (username) DO NOTHING;

SELECT setval('user_user_id_seq', (SELECT COALESCE(MAX(user_id), 1) FROM "user"));


INSERT INTO neo (nasa_id, name, absolute_magnitude, diameter_min, diameter_max, hazardous, url_nasa, origin) VALUES
('3542519', '(2010 PK9)', 21.8, 0.116, 0.259, TRUE, 'https://ssd.jpl.nasa.gov', 'NASA'),
('2099942', '99942 Apophis (2004 MN4)', 19.7, 0.34, 0.37, TRUE, 'https://ssd.jpl.nasa.gov', 'NASA'),
('3727712', '(2015 TD144)', 24.3, 0.036, 0.081, FALSE, 'https://ssd.jpl.nasa.gov', 'NASA'),
('3727713', '(2015 TE144)', 25.1, 0.025, 0.056, FALSE, 'https://ssd.jpl.nasa.gov', 'NASA'),
('3727714', '(2015 TF144)', 23.9, 0.044, 0.098, FALSE, 'https://ssd.jpl.nasa.gov', 'NASA')
ON CONFLICT (nasa_id) DO NOTHING;

INSERT INTO approach (neo_id, approach_day, approach_date, body, distance, speed) VALUES
(1, CURRENT_DATE + INTERVAL '1 day', CURRENT_TIMESTAMP + INTERVAL '1 day', 'Earth', 4985600.0, 54200.0),
(1, CURRENT_DATE + INTERVAL '15 days', CURRENT_TIMESTAMP + INTERVAL '15 days', 'Earth', 7400000.0, 48000.0),
(2, CURRENT_DATE + INTERVAL '5 days', CURRENT_TIMESTAMP + INTERVAL '5 days', 'Earth', 31000.0, 110000.0),
(3, CURRENT_DATE + INTERVAL '2 days', CURRENT_TIMESTAMP + INTERVAL '2 days', 'Earth', 12500000.0, 32000.0)
ON CONFLICT DO NOTHING;
