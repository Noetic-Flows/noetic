from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field
import uuid
import datetime
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

class AICHeader(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    origin_device: str
    issued_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    expires_at: Optional[datetime.datetime] = None

class AICCapabilityScopes(BaseModel):
    allowed_tools: List[str] = []
    max_compute_budget: float = 1.0  # Normalized 0-1
    data_access_regex: List[str] = [".*"]  # Default to anything in local scope

class AICSafetyGuardrails(BaseModel):
    pii_filter: bool = True
    content_moderation: bool = True
    max_tokens_per_request: int = 4096

class AICUserPreferences(BaseModel):
    tone: str = "technical"
    human_in_the_loop: str = "high_stakes_only"

class AgenticIntentContract(BaseModel):
    header: AICHeader
    scopes: AICCapabilityScopes
    safety: AICSafetyGuardrails
    preferences: AICUserPreferences
    signature: Optional[str] = None

    def serialize(self) -> str:
        # Exclude signature from serialization for signing
        data = self.model_dump(exclude={"signature"})
        return json.dumps(data, sort_keys=True, default=str)

    def sign(self, private_key: rsa.RSAPrivateKey):
        serialized_data = self.serialize().encode('utf-8')
        signature = private_key.sign(
            serialized_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        self.signature = signature.hex()

    def verify(self, public_key: rsa.RSAPublicKey) -> bool:
        if not self.signature:
            return False
        try:
            serialized_data = self.serialize().encode('utf-8')
            public_key.verify(
                bytes.fromhex(self.signature),
                serialized_data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
