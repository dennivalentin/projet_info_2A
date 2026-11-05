from datetime import date, datetime

from business_object.alert import Alert
from business_object.apod import ApodData
from business_object.approach import Approach
from business_object.connection import Connection
from business_object.favourite import Favourite
from business_object.import_bo import Import
from business_object.neo import Neo
from business_object.proposal import Proposal
from business_object.search import Search
from business_object.user import User


def test_neo_getters_and_setters():
    """Verify Neo properties, getters, setters, and to_dict."""
    now = datetime(2026, 10, 25, 12, 0)
    neo = Neo(
        neo_id=1,
        nasa_id="3542519",
        name="Apophis",
        absolute_magnitude=19.7,
        diameter_min=0.34,
        diameter_max=0.45,
        hazardous=True,
        url_nasa="https://nasa.gov/apophis",
        origin="NASA",
        date_update=now,
    )

    # Initial getters
    assert neo.neo_id == 1
    assert neo.nasa_id == "3542519"
    assert neo.name == "Apophis"
    assert neo.absolute_magnitude == 19.7
    assert neo.diameter_min == 0.34
    assert neo.diameter_max == 0.45
    assert neo.hazardous is True
    assert neo.url_nasa == "https://nasa.gov/apophis"
    assert neo.origin == "NASA"
    assert neo.date_update == now

    # Setters
    neo.neo_id = 2
    neo.name = "Bennu"
    neo.hazardous = False
    neo.diameter_min = 0.49
    neo.diameter_max = 0.51
    neo.origin = "USER"

    assert neo.neo_id == 2
    assert neo.name == "Bennu"
    assert neo.hazardous is False
    assert neo.diameter_min == 0.49
    assert neo.diameter_max == 0.51
    assert neo.origin == "USER"

    d = neo.to_dict()
    assert d["name"] == "Bennu"
    assert d["origin"] == "USER"


def test_approach_getters_and_setters():
    """Verify Approach properties, getters, setters, AU conversion, and to_dict."""
    app_date = datetime(2029, 4, 13, 21, 46)
    approach = Approach(
        approach_id=10,
        neo_id=1,
        approach_date=app_date,
        distance=38000.0,
        speed=74300.0,
        body="Earth",
    )

    assert approach.approach_id == 10
    assert approach.neo_id == 1
    assert approach.approach_day == approach.approach_date.date()
    assert approach.approach_date == app_date
    assert approach.distance == 38000.0
    assert approach.speed == 74300.0
    assert approach.body == "Earth"
    assert approach.distance_au > 0

    # Setters
    approach.distance = 50000.0
    approach.speed = 80000.0
    approach.body = "Moon"

    assert approach.distance == 50000.0
    assert approach.speed == 80000.0
    assert approach.body == "Moon"

    d = approach.to_dict()
    assert d["distance_km"] == 50000.0
    assert "distance_au" in d


def test_alert_getters_and_setters():
    """Verify Alert properties, getters, setters, and to_dict."""
    day = date(2020, 8, 29)
    alert = Alert(
        alert_id=1,
        user_id=42,
        label="Huge Asteroids",
        distance_max=1000000.0,
        diameter_min=1.0,
        hazardous_only=True,
        active=True,
        creation_date=day,
    )

    assert alert.alert_id == 1
    assert alert.user_id == 42
    assert alert.label == "Huge Asteroids"
    assert alert.distance_max == 1000000.0
    assert alert.diameter_min == 1.0
    assert alert.hazardous_only is True
    assert alert.active is True
    assert alert.creation_date == date(2020, 8, 29)

    # Setters
    alert.label = "Close Approaches"
    alert.active = False
    alert.diameter_min = 0.5

    assert alert.label == "Close Approaches"
    assert alert.active is False
    assert alert.diameter_min == 0.5
    assert alert.to_dict()["label"] == "Close Approaches"


def test_user_getters_and_setters():
    """Verify User properties, getters, setters, and to_dict."""
    day = date(2001, 9, 11)
    user = User(
        user_id=1,
        username="astronomer",
        email="astro@ensai.fr",
        password_hash="secret_hash",
        role="user",
        creation_date=day,
    )

    assert user.user_id == 1
    assert user.username == "astronomer"
    assert user.email == "astro@ensai.fr"
    assert user.role == "user"
    assert user.creation_date == date(2001, 9, 11)

    user.role = "admin"
    user.username = "head_astronomer"
    assert user.role == "admin"
    assert user.username == "head_astronomer"

    d = user.to_dict(include_sensitive=False)
    assert "password_hash" not in d
    assert d["username"] == "head_astronomer"


def test_proposal_getters_and_setters():
    """Verify Proposal properties, getters, setters, and to_dict."""
    subd = date(2005, 7, 29)

    proposal = Proposal(
        proposal_id=5,
        user_id=12,
        neo_id=34,
        field_name="diameter_min",
        proposed_value="0.45",
        justification="New observation from Paris observatory",
        status="WAITING",
        submission_date=subd,
    )

    assert proposal.proposal_id == 5
    assert proposal.user_id == 12
    assert proposal.neo_id == 34
    assert proposal.field_name == "diameter_min"
    assert proposal.proposed_value == "0.45"
    assert proposal.status == "WAITING"
    assert proposal.submission_date == subd

    proposal.status = "ACCEPTED"
    assert proposal.status == "ACCEPTED"


def test_other_bos_getters_and_setters():
    """Verify ApodData, Connection, Favourite, Import"""
    now = datetime(2026, 10, 25, 12, 0)

    # ApodData
    apod = ApodData(
        "Pillars of Creation", now, "Hubble picture", "https://nasa.gov/img.jpg"
    )
    assert apod.title == "Pillars of Creation"
    apod.title = "James Webb Deep Field"
    assert apod.title == "James Webb Deep Field"

    # Connection
    conn = Connection(1, 42, now)
    assert conn.user_id == 42
    conn.user_id = 99
    assert conn.user_id == 99

    # Favourite
    fav = Favourite(neo_id=10, user_id=20, date_added=now)
    assert fav.neo_id == 10
    assert fav.user_id == 20
    fav.neo_id = 15
    assert fav.neo_id == 15

    # Import
    imp = Import(start_date=now, end_date=now, user_id=1, nb_calls=5, nb_neo=30)
    assert imp.nb_calls == 5
    assert imp.nb_neo == 30
    imp.status = "DONE"
    assert imp.status == "DONE"

    def test_search_getters_and_setters():
        sch = Search(
            search_id=123856,
            user_id=456892,
            search_date=datetime.now(),
            criteria="EROS",
            neo_id=4586333,
        )
        assert sch.search_id == 123856
        assert sch.user_id == 456892
        assert sch.search_date == datetime.now()
        assert sch.criteria == "EROS"
        sch.neo_id = 475823
        assert sch.neo_id == 475823
