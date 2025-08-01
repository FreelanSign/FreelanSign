# adapter to Django's ORM
from ..models.models import User


class UserRepository:
    def get_all(self):
        """Retrieve all users."""
        return User.objects.all()

    def create(self, **data):
        """Create a new user."""
        user = User(**data)
        user.set_password(data["password"])
        user.save()
        return user
