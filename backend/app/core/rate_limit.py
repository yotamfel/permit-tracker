from slowapi import Limiter
from slowapi.util import get_remote_address

# Shared limiter instance - applied per-route via @limiter.limit(...) on the
# auth and contact endpoints (the ones worth protecting against brute-force/
# spam), not globally. Keyed by client IP; in-memory storage is fine for a
# single Railway instance - move to a Redis storage_uri if that changes.
limiter = Limiter(key_func=get_remote_address)
