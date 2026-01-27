import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from pydantic import ValidationError

from noetic_lang.core.security import AgenticIntentContract, IdentityContext, ACL

class TestProtocolSecurity:
    
    def test_identity_context_immutability(self):
        """Verify IdentityContext is frozen (immutable)."""
        ctx = IdentityContext(user_id="test_user", roles=["admin"])
        with pytest.raises(ValidationError):
            ctx.user_id = "hacked_user"

    def test_aic_validity(self):
        """Verify AgenticIntentContract validation logic."""
        # Future expiration
        valid_contract = AgenticIntentContract(
            contract_id=uuid4(),
            source_agent="agent_a",
            target_agent="agent_b",
            intent="execute_task",
            expires_at=datetime.utcnow() + timedelta(hours=1),
            signature="valid_sig"
        )
        assert valid_contract.is_valid()

        # Past expiration
        expired_contract = AgenticIntentContract(
            contract_id=uuid4(),
            source_agent="agent_a",
            target_agent="agent_b",
            intent="execute_task",
            expires_at=datetime.utcnow() - timedelta(hours=1),
            signature="valid_sig"
        )
        assert not expired_contract.is_valid()
    
    def test_aic_strict_types(self):
        """Verify strict typing enforcement."""
        with pytest.raises(ValidationError):
            AgenticIntentContract(
                contract_id="not-a-uuid", # Should fail
                source_agent="agent_a",
                target_agent="agent_b",
                intent="execute_task",
                expires_at=datetime.utcnow(),
                signature="sig"
            )

    def test_acl_strictness(self):
        """Verify ACL forbids extra fields."""
        with pytest.raises(ValidationError):
            ACL(
                role="editor", 
                resource_pattern="*", 
                extra_field="malicious_payload" # Should fail
            )
