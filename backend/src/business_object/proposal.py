from datetime import datetime


class Proposal:
    """Represents a proposal submitted by a user to add or correct a NEO.
    Must be inspected and validated (or declined) by an administrator.

    Attributes:
        _proposal_id (int | None): The unique identifier of the proposal.
        _neo_id (int | None): The ID of the proposed/associated NEO.
        _user_id (int): The ID of the user submitting the proposal.
        _submission_date (datetime): The date the proposal was submitted.
        _field_name (str): The specific field or attribute being proposed/updated.
        _proposed_value (str): Value suggested by the user.
        _justification (str): The user's reasoning or source for the proposal.
        _status (str): The status of the proposal ('WAITING', 'ACCEPTED', 'REJECTED').
    """

    def __init__(
        self,
        user_id: int,
        field_name: str,
        proposed_value: str,
        justification: str,
        submission_date: datetime | None = None,
        status: str = "WAITING",
        neo_id: int | None = None,
        proposal_id: int | None = None,
    ):
        self._proposal_id = proposal_id
        self._neo_id = neo_id
        self._user_id = user_id
        self._submission_date = submission_date or datetime.now()
        self._field_name = field_name
        self._proposed_value = proposed_value
        self._justification = justification
        self._status = status

    @property
    def proposal_id(self) -> int | None:
        return self._proposal_id

    @property
    def neo_id(self) -> int | None:
        return self._neo_id

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def submission_date(self) -> datetime:
        return self._submission_date

    @property
    def field_name(self) -> str:
        return self._field_name

    @property
    def proposed_value(self) -> str:
        return self._proposed_value

    @property
    def justification(self) -> str:
        return self._justification

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str) -> None:
        self._status = value

    def to_dict(self) -> dict:
        return {
            "proposal_id": self._proposal_id,
            "neo_id": self._neo_id,
            "user_id": self._user_id,
            "submission_date": (
                self._submission_date.isoformat()
                if hasattr(self._submission_date, "isoformat")
                else str(self._submission_date)
            ),
            "field_name": self._field_name,
            "proposed_value": self._proposed_value,
            "justification": self._justification,
            "status": self._status,
        }
