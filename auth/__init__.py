# Authentication package
from .AuthManager import AuthService

# Keep backward-compatible name expected elsewhere in the codebase
AuthManager = AuthService

__all__ = ["AuthService", "AuthManager"]
