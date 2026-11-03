"""FO3 - Statistics on NEOs, each one with its justification."""

from decimal import Decimal

from dao.statistics_dao import StatisticsDao

KM_PER_LUNAR_DISTANCE = 384_400  # average Earth-Moon distance

JUSTIFICATIONS = {
    "approaches_per_month": (
        "Shows how the number of close approaches evolves over time. An increase mostly "
        "reflects better detection by sky surveys, so it also measures monitoring progress."
    ),
    "size_distribution": (
        "Size drives the consequences of an impact. Below ~25 m an object mostly burns up in "
        "the atmosphere; 140 m is NASA's threshold for regional damage; above 1 km the "
        "consequences would be global."
    ),
    "hazardous_pct": (
        "Share of NEOs classified 'potentially hazardous' by NASA. It summarises the risk "
        "level of the catalogue."
    ),
    "mean_vs_median": (
        "Distances are very skewed: a few very far objects pull the mean up, so the median "
        "better describes a typical approach."
    ),
}


def _to_float(value):
    """Converts Decimal values from PostgreSQL to float (None stays None)."""
    return float(value) if isinstance(value, Decimal) else value


class StatisticsService:
    """Business logic of the statistics (FO3)."""

    def get_statistics(self) -> dict:
        """Gathers all the statistics, with their justification."""
        dao = StatisticsDao()

        summary = {key: _to_float(value) for key, value in dao.global_summary().items()}
        if summary.get("median_distance_km") is not None:
            summary["median_distance_ld"] = round(
                summary["median_distance_km"] / KM_PER_LUNAR_DISTANCE, 2
            )

        return {
            "summary": summary,
            "approaches_per_month": dao.approaches_per_month(),
            "size_distribution": dao.size_distribution(),
            "justifications": JUSTIFICATIONS,
        }
