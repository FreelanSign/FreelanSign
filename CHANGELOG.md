## backend/v0.1.0 — 2025-08-15

### Added
- **POST** `/api/auth/login` : connexion avec email + mot de passe → access + refresh tokens
- **POST** `/api/auth/refresh` : régénération d’un access token à partir d’un refresh token
- **POST** `/api/user/logout` : déconnexion avec invalidation (blacklist) du refresh token, 204/400

### Changed
- Swagger : ajout des tags **Auth** et **Users**
- Documentation des endpoints sur [Swagger UI](http://localhost:8000/api/docs/#/)

### Notes
- Aucun breaking change
- Aucune migration de base de données
