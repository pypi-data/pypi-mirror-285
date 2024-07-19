from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from graphdatascience.session.aura_api_responses import SessionDetails
from graphdatascience.session.session_sizes import SessionMemoryValue


@dataclass(frozen=True)
class SessionInfo:
    """
    Represents information about a session.

    Attributes:
        name (str): The name of the session.
        memory (str): The size of the session.
    """

    name: str
    memory: SessionMemoryValue

    @classmethod
    def from_session_details(cls, details: SessionDetails) -> ExtendedSessionInfo:
        return ExtendedSessionInfo(
            details.name,
            details.memory,
            details.instance_id,
            details.status,
            details.expiry_date,
            details.created_at,
        )


@dataclass(frozen=True)
class ExtendedSessionInfo(SessionInfo):
    instance_id: str
    status: str
    expiry_date: Optional[datetime]
    created_at: datetime
