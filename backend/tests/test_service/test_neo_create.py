from unittest.mock import MagicMock

from business_object.neo import Neo
from dao.neo_dao import NeoDao
from service.neo_service import NeoService



def test_create_ok():
    """Successfully create a Neo"""

    # GIVEN
    nasa_id ,name ,absolute_magnitude ,diameter_min ,diameter_max ,hazardous ,url_nasa ,origin ,date_update , neo_id = None , "caillou", 1500, 200, 600, True, "", "USER", "2005-12-25", 262543
    NeoDao().create = MagicMock(return_value=True)

    # WHEN
    neo = NeoService().create(nasa_id ,name ,absolute_magnitude ,diameter_min ,diameter_max ,hazardous ,url_nasa ,origin ,date_update , neo_id)

    # THEN
    assert isinstance(neo, Neo) and neo.name == name


def test_create_fail():
    """Fail to create a neo because NeoDao().create returns False"""

    # GIVEN
    nasa_id ,name ,absolute_magnitude ,diameter_min ,diameter_max ,hazardous ,url_nasa ,origin ,date_update , neo_id = None , "caillou", 1500, 200, 600, True, "", "USER", "2005-12-25", 262543
    NeoDao().create = MagicMock(return_value=False)

    # WHEN
    neo = NeoService().create(nasa_id ,name ,absolute_magnitude ,diameter_min ,diameter_max ,hazardous ,url_nasa ,origin ,date_update , neo_id)

    # THEN
    assert neo is None