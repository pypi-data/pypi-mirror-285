from dataclasses import asdict
import json

from zeta.db.user import ZetaUserData, ZetaUserTier
from zeta.db.auth_token import ZetaAuthTokenData


class ZetaJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ZetaUserData):
            return asdict(obj)
        elif isinstance(obj, ZetaAuthTokenData):
            return asdict(obj)
        elif isinstance(obj, ZetaUserTier):
            return obj.value
        return super().default(obj)