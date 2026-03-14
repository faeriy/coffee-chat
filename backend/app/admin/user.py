# UserAdmin is defined in views.py and registered via register_views(admin).
# This file kept for backwards compatibility; can be removed if unused.
from app.admin.views import UserAdmin

__all__ = ["UserAdmin"]
