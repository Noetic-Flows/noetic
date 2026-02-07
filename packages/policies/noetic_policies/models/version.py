"""Policy version models."""

from pydantic import BaseModel, Field


# T012: PolicyVersion Pydantic model
class PolicyVersion(BaseModel):
    """Policy format version information."""

    major: int = Field(..., ge=0)
    minor: int = Field(..., ge=0)

    @classmethod
    def from_string(cls, version: str) -> "PolicyVersion":
        """Parse version string into PolicyVersion object."""
        major_str, minor_str = version.split(".")
        return cls(major=int(major_str), minor=int(minor_str))

    def __str__(self) -> str:
        """String representation of version."""
        return f"{self.major}.{self.minor}"

    def is_compatible(self, other: "PolicyVersion") -> bool:
        """Check if this version can parse policies from other version."""
        # Support current version and one previous
        if self.major == other.major:
            return abs(self.minor - other.minor) <= 1
        return False
