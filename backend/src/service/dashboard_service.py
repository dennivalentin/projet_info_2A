"""F2 - Builds the dashboard of a user."""

from datetime import date, timedelta

from dao.dashboard_dao import DashboardDao

DEFAULT_PERIOD_DAYS = 7


class DashboardService:
    """Business logic of the dashboard (F2)."""

    @staticmethod
    def check_period(start: date | None, end: date | None) -> tuple[date, date]:
        """Default period: today -> today + 7 days.

        Raises:
            ValueError: if end is before start.
        """
        start = start or date.today()
        end = end or start + timedelta(days=DEFAULT_PERIOD_DAYS)
        if end < start:
            raise ValueError("End date must be after start date")
        return start, end

    def get_dashboard(
        self, user_id: int, start: date | None = None, end: date | None = None
    ) -> dict:
        """Gathers everything the dashboard displays."""
        start, end = self.check_period(start, end)
        dao = DashboardDao()

        counts = dao.count_upcoming(start, end)
        nb_neos = counts["nb_neos"]
        hazardous_share = round(100 * counts["nb_hazardous"] / nb_neos, 1) if nb_neos else 0.0

        return {
            "period": {"start": start, "end": end},
            "nb_neos": nb_neos,
            "nb_hazardous": counts["nb_hazardous"],
            "hazardous_share_pct": hazardous_share,
            "upcoming_approaches": dao.find_upcoming_approaches(start, end),
            "closest_approach": dao.find_closest_approach(start, end),
            "favourites": dao.find_favourites(user_id),
        }
