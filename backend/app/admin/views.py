"""Register SQLAdmin model views. Called from main after admin is created."""
from app.models.user import User
from sqladmin import ModelView


class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    # Only list these columns (hashed_password omitted on purpose)
    column_list = [
        User.id,
        User.username,
        User.email,
        User.google_id,
        User.created_at,
        User.hashed_password,
    ]
    column_searchable_list = [User.username, User.email]
    column_sortable_list = [User.id, User.username, User.created_at]
    column_default_sort = [(User.id, False)]
    form_excluded_columns = [User.hashed_password]


def register_views(admin) -> None:
    admin.add_view(UserAdmin)
