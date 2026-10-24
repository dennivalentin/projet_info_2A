from dao.alert_dao import AlertDao
from utils.log_utils import log
from utils.singleton import Singleton
import pprint


class AlertService(metaclass=Singleton):

    @log
    def create_alert(self, user_id: int, neo_id: int | None = None, min_diameter: float | None = None, max_distance: float | None = None, hazardous_only : bool | None = None) -> bool:
        """Create an alert according to what the user want to see

        Parameters
        ----------
            user_id: user who is asking
            neo_id: int | None : a possible Neo to follow
            min_diameter: float | None : A possible size of a neo to be notified about
            max_distance: float | None : Below that possible distance a notification is sent
            hazardous_only : bool | None : If the user wants to see only hazardous Neo
        
        Return
        ------
            bool, True if well created, False otherwise
        """

        if neo_id is None and min_diameter is None and max_distance is None:
            raise ValueError("At least one criterion should be submitted to create an alert")
        
        if (min_diameter is not None and min_diameter <= 0) or (max_distance is not None and max_distance <= 0):
            raise ValueError("Give a positive value")
        
        return AlertDao().create(user_id=user_id, neo_id=neo_id, min_diameter=min_diameter, max_distance=max_distance, hazardous_only = hazardous_only)
    

    def check_send_notification(self, user_id : int) -> list[str]:
        """Method to check if a notification has to be sent according to the user

        Parameters
        ----------
            user_id : user that needs to be informed
        
        Return
        ------
            list[str] : list of alert messages
        """

        matching_approaches = AlertDao.find_matching_approaches_for_user(user_id)
        list_notif = []

        for item in matching_approaches:
            neo_name = item["neo_name"]

            if item["hazardous_only"] is not None:
                notif = f"HAZARDOUS | {neo_name}"
            else:
                notif = f"{neo_name}"

            if item["diameter_min"] is not None:
                notif += f" : diameter of the neo {item["diameter_max"]}>= {item["diameter_min"]}"
            if item["distance_max"] is not None:
                notif += f" : distance from Earth is {item["distance"]} <= {item["distance_max"]}"
            
            list_notif.append(notif)
        
        return list_notif

    def list_alert_user(self, user_id) -> None:
        """find the alert by user

        Parameters
        ----------
            user_id : alert of this user

        Return
        ------
            list[str] : list of alerts
        """
        alerts = AlertDao.find_by_user(user_id)
        pprint(alerts)
    
    def trun_on_off(self, alert_id) -> None:
        

