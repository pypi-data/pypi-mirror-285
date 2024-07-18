from bson import ObjectId
from datetime import datetime
from dataclasses import dataclass, field


@dataclass(slots=True)
class DecisionMaker:
    # Foreign key to the `company` collection
    company_id: str
    firstname: str
    lastname: str
    source: str
    # The raw string from the source, will cleaned and classified into `function_string`
    raw_function_string: str
    last_seen: datetime
    _id: ObjectId = field(default_factory=ObjectId)
    function_string: str | None = None
    email: str | None = None
    email_score: int | None = None
    phone: str | None = None
    phone_score: int | None = None
    language: str | None = None
    function_code: int | None = None
    linkedin_url: str | None = None
    cluster: str | None = None
    cluster_score: float | None = None
    cluster_best_match: str | None = None


@dataclass(slots=True)
class DecisionMakerLegacy:
    """
    Decision makers imported from the legacy SQL database.

    This is deperecated and kept for reference purpose only.
    """

    # Company ID (same _id as in company collection with leading zeros BE:012345667)
    company_id: str
    # Company ID (id in the old format (VAT without leading zeros) BE:12345667)
    legacy_entity_id: str
    name: str | None = None
    firstname: str | None = None
    # deprecated
    language: str | None = None
    # Gender (deprecated)
    sex: str | None = None
    # deprecated
    function: str | None = None
    source: str | None = None
    function_string: str | None = None
    linkedin_url: str | None = None
    email: str | None = None
    email_source: str | None = None
    email_score: int | None = None
    blacklisted: str | None = None
    # deprecated
    phone: str | None = None
    cluster: str | None = None
    cluster_score: int | None = None
    # cluster match
    best_match: str | None = None
    position_request_base: int | None = None
    position_request_ceo: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
    google_last_seen: datetime | None = None
    norbert_last_seen: datetime | None = None
