import os
from unittest.mock import patch, MagicMock

import psycopg2
import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialize test data"""
    with patch.dict(os.environ, {"SCHEMA": "project_test_dao"}):
        ResetDatabase().run(test_dao=True)
        yield


def test_find_un_critere(mocker):
    donnees_simulees = [{
        "neo_id": 1, "nasa_id": "2000433", "name": "Eros", 
        "absolute_magnitude": 11.16, "diameter_min": 16.84, "diameter_max": 37.65, 
        "hazardous": False, "url_nasa": "http://...", "origin": "NASA", "date_update": "2023-10-27"
    }]

    # 2. On crée nos faux objets (mocks) pour imiter psycopg2
    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchall.return_value = donnees_simulees
    
    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

    # 3. On remplace DBConnection pour qu'elle utilise notre fausse connexion
    mock_db = mocker.patch("dao.neo_dao.DBConnection")
    mock_db.return_value.connection.__enter__.return_value = mock_connection

    # 4. On exécute la fonction que l'on veut tester
    dao = NeoDao()
    resultats = dao.find({"name": "Eros", "hazardous": None})

    # 5. On vérifie que la transformation en objet a bien fonctionné
    assert len(resultats) == 1
    assert resultats[0]._name == "Eros"