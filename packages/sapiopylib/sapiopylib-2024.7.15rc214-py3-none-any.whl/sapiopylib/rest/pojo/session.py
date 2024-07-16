from __future__ import annotations

from typing import Any


class SessionInfo:
    """
    Session Info data for a single session.
    """
    session_id: str
    username: str

    def __init__(self, session_id: str, username: str):
        self.session_id = session_id
        self.username = username

    @staticmethod
    def from_json(json_dct: dict[str, Any]):
        session_id = json_dct.get('sessionId')
        username = json_dct.get('userName')
        return SessionInfo(session_id, username)

    def __str__(self):
        return self.session_id + " (" + self.username + ")"

    def __repr__(self):
        return self.session_id

    def __eq__(self, other):
        if not isinstance(other, SessionInfo):
            return False
        return self.session_id == other.session_id and self.username == other.username

    def __hash__(self):
        return hash((self.session_id, self.username))
