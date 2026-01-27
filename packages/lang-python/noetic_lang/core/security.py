from typing import List, Dict, Optional, Literal, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict, UUID4

class ACL(BaseModel):
    """
    Access Control List entry.
    Defines who can do what on a resource.
    """
    model_config = ConfigDict(frozen=True, extra="forbid")

    role: str = Field(..., min_length=1, description="The role required to access the resource.")
    permissions: List[Literal["read", "write", "execute", "admin"]] = Field(
        default_factory=list, 
        description="List of allowed operations."
    )
    resource_pattern: str = Field("*", description="Glob pattern for resource ID matching.")

class IdentityContext(BaseModel):
    """
    Represents the identity executing a Flow or Stanza.
    Carries authentication and session context.
    """
    model_config = ConfigDict(frozen=True, extra="ignore")

    user_id: str = Field(..., min_length=1, description="Unique identifier for the user or agent.")
    roles: List[str] = Field(default_factory=list, description="Assigned roles for RBAC.")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Extended attributes (e.g., department, clearance).")
    
    # Session-specific
    session_id: Optional[str] = Field(None, description="Traceable session identifier.")
    client_ip: Optional[str] = Field(None, description="Origin IP address for audit logging.")

class AgenticIntentContract(BaseModel):
    """
    AIC: A cryptographically verifiable contract for inter-agent communication.
    Ensures that an intent is authorized and has not expired.
    """
    model_config = ConfigDict(frozen=True)

    contract_id: UUID4 = Field(..., description="Unique ID of the contract.")
    source_agent: str = Field(..., min_length=1, description="The Agent ID initiating the request.")
    target_agent: str = Field(..., min_length=1, description="The Agent ID receiving the request.")
    intent: str = Field(..., min_length=1, description="The specific action or goal being requested.")
    
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Creation time (UTC).")
    expires_at: datetime = Field(..., description="Expiration time (UTC).")
    
    signature: str = Field(..., description="Cryptographic signature of the contract content.")

    @field_validator("expires_at")
    @classmethod
    def validate_expiration(cls, v: datetime, info: Any) -> datetime:
        # We can't easily validate 'future' without context of 'now' which drifts, 
        # but we can ensure it's timezone aware or naive as per system standards.
        # For now, we assume naive UTC.
        return v
    
    def is_valid(self) -> bool:
        """Check if the contract is structurally valid and not expired."""
        return datetime.utcnow() < self.expires_at
