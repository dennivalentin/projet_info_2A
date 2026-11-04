import pytest
from dao.neo_dao import NeoDao
from unittest.mock import MagicMock, patch

@patch("dao.neo_dao.DBConnection")
def test_find_un_critere(mock_db):
    donnees_simulees = [
        {
            "neo_id": 1,
            "nasa_id": "2000433",
            "name": "Eros",
            "absolute_magnitude": 11.16,
            "diameter_min": 16.84,
            "diameter_max": 37.65,
            "hazardous": False,
            "url_nasa": "http://example.com",
            "origin": "NASA",
            "date_update": "2023-10-27",
        }
    ]

    # Use standard MagicMock instead of mocker.MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = donnees_simulees

    mock_connection = MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

    # mock_db is passed via the @patch decorator
    mock_db.return_value.connection.__enter__.return_value = mock_connection

    dao = NeoDao()
    resultats = dao.find(
        {
            "name": "Eros",
            "hazardous": None,
        }
    )

    assert len(resultats) == 1
    assert resultats[0]._name == "Eros"

    # Vérifier la requête et les paramètres réellement envoyés
    query, params = mock_cursor.execute.call_args.args

    assert "n.name ILIKE %(name)s" in query
    assert "hazardous" not in params
    assert params == {"name": "%Eros%",
                      "limit": 100,
                      "offset": 0}


def test_find_critere_inconnu():
    dao = NeoDao()

    with pytest.raises(ValueError, match="Unknown search criterion"):
        dao.find({"color": "blue"})