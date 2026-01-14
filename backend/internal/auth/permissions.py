from fastapi import Depends, HTTPException

from internal.auth.deps import get_current_user
from internal.config.settings import get_settings
from internal.db.models.user import User


def require_admin(user: User = Depends(get_current_user)) -> User:
    settings = get_settings()
    if user.ldap_id not in settings.admin_ldap_ids:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
