from business_object.neo import Neo


class Alert:
    """
    Class describing the alert that could be send to the user

    Attributes:
        _alert_id (int): The unique identifier of the alert.
        _neo_id (int): The ID of a specific NEO to track.
        _user_id (int): The ID of the user who created the alert.
        _object (Neo): A reference to the Neo object itself.
        _min_diameter (float): The minimum diameter threshold to trigger the alert.
        _max_distance (float): The maximum approach distance threshold.
        _is_active (bool): Indicates whether the alert is currently active or dismissed.
    """
    def __init__(self, alert_id: int, neo_id: int, user_id: int, obj_neo: Neo, min_diameter: float, max_distance: float, is_active: bool):
        self._alert_id = alert_id
        self._neo_id = neo_id
        self._user_id = user_id
        self._object = obj_neo
        self._min_diameter = min_diameter
        self._max_distance = max_distance
        self._is_active = is_active