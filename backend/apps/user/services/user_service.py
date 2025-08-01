# Applicative logic for user management
from apps.user.infrastructure.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def list_users(self):
        # Logic to list all users
        return self.user_repository.get_all()

    def register_user(self, full_name, email, phone, password):
        # Logic to register a new user
        user_data = {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "password": password,
        }
        return self.user_repository.create(**user_data)

    def get_user(self, user_id):
        # Logic to retrieve a user by ID
        return self.user_repository.get(user_id)

    def update_user(self, user_id, user_data):
        # Logic to update an existing user
        return self.user_repository.update(user_id, user_data)

    def delete_user(self, user_id):
        # Logic to delete a user
        return self.user_repository.delete(user_id)
