from datetime import datetime


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

    def __init__(
        self,
        alert_id: int,
        user_id: int,
        label: str,
        diameter_min: float,
        distance_max: float,
        hazardous_only: bool,
        active: bool,
        creation_date: datetime,
        last_eval_date: datetime
    ):
        self._alert_id = alert_id
        self._user_id = user_id
        self._label = label
        self._diameter_min = diameter_min
        self._distance_max = distance_max
        self._hazardous_only = hazardous_only
        self._active = active
        self._creation_date = creation_date
        self._last_eval_date = last_eval_date
    
    def __repr__(self):
        beg = f"""Alert n° : {self._alert_id} from user : {self._user_id}. Criteria :
        {self._label}"""

        if self._diameter_min is not None:
            beg += f" | Minimum diameter : {self._diameter_min}"
        
        if self._distance_max is not None:
            beg += f" | Maximum distance : {self._distance_max}"
        
        if self._hazardous_only is not None:
            beg += f" | Hazardous : {self._hazardous_only}"
        
        beg += f" | Active = {self._active}"
