from date import datetime


class Proposal:
    """
    Represents a proposal submitted by a user to add a new NEO.
    Must be inspected and validated (or declined) by an administrator.

    Attributes:
        _proposal_id (int): The unique identifier of the proposal.
        _neo_id (int): The ID of the proposed NEO.
        _user_id (int): The ID of the user submitting the proposal.
        _submission_date (datetime): The date the proposal was submitted.
        _field_name (str): The specific field or attribute being proposed/updated.
        _proposed_value (str): Values suggested by the user.
        _justification (str): The user's reasoning or source for the proposal.
        _status (str): The status of the proposal ('pending', 'accepted', 'rejected').
    """
    def __init__(self, proposal_id: int, neo_id: int, user_id: int, submission_date: datetime, field_name: str, proposed_value: str, justification: str, status: str):
        self._proposal_id = proposal_id
        self._neo_id = neo_id
        self._user_id = user_id
        self._submission_date = submission_date
        self._field_name = field_name
        self._proposed_value = proposed_value
        self._justification = justification
        self._status = status