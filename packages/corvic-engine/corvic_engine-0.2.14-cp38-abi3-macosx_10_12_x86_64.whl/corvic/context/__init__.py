"""Per-request context variables.

Affect things like logging and the names of metrics.
"""

import contextvars
import uuid
from dataclasses import dataclass

# These are sentinels used only in the Requester object below rather than actual org
# ids that our query middleware uses to make query instrumentation decisions
NOBODY_ORG_ID = "org-nobody"  # an org that owns nothing
SUPERUSER_ORG_ID = "org-superuser"  # an org that can see everything


@dataclass(frozen=True)
class Requester:
    """Info about the issuer of the request, populated by middleware."""

    org_id: str


service_name = contextvars.ContextVar("service_name", default="corvic")
trace_id = contextvars.ContextVar("trace_id", default="")
requester = contextvars.ContextVar(
    "requester_identity", default=Requester(org_id=NOBODY_ORG_ID)
)


def reset_context(new_service_name: str, new_requester: Requester):
    """Reset contextvars for a new request."""
    service_name.set(new_service_name)
    trace_id.set(str(uuid.uuid4()))
    requester.set(new_requester)
