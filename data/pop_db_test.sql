-- Passwords hashed : admin1234, alice1234, bob12345


INSERT INTO "user" (user_id, username, email, password_hash, role) VALUES
(997, 'admin', 'admin@neowatch.fr', '5e7a7566435ae1379da39ffbb74f49fe80dff90fe4b87caf306b91c8cd05d1d3', 'admin'),
(998, 'alice', 'alice@neowatch.fr', 'fd420a75c884e2ab5fbe119a90cd04b524e9da555bd9324b51366f1a69582b21', 'user'),
(999, 'bob',   'bob@neowatch.fr',   'c038c06dbb5ea27e2e7ee77d0d124119122aaecdbb0cd5fe76b2132067618d20', 'user');

INSERT INTO connection (user_id, connection_date) VALUES
(998, '2026-10-01 09:00:00'),
(998, '2026-10-05 18:30:00');