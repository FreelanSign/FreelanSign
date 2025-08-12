# Applicative logic for user management
from apps.user.infrastructure.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def list_users(self):
        """Logic to list all users."""
        return self.user_repository.get_all()

    def register_user(self, **payload):
        """Logic to register a new user."""
        return self.user_repository.create(**payload)

    def get_user(self, user_id):
        """Logic to retrieve a user by ID."""
        return self.user_repository.get(user_id)

    def update_user(self, user_id, user_data):
        """Logic to update a user."""
        return self.user_repository.update(user_id, user_data)

    def delete_user(self, user_id):
        """Logic to delete a user."""
        return self.user_repository.delete(user_id)
