class MVPError(Exception):
    """Base error for expected prototype failures."""


class PackValidationError(MVPError):
    """Raised when a Builder Pack does not match the prototype profile."""


class RunStateError(MVPError):
    """Raised when a Runtime transition is not allowed."""


class IntegrityError(MVPError):
    """Raised when a persisted artifact or hash chain does not verify."""


class SignatureError(MVPError):
    """Raised when an optional external identity signature is invalid."""


class TrustPolicyError(MVPError):
    """Raised when a Reviewer trust registry or policy is invalid."""
