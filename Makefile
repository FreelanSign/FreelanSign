# Makefile pour FreelansSign

# Variables
DOCKER_COMPOSE = docker compose
ENV_FILE = .env.docker

# Couleurs pour les messages
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

.PHONY: help setup-local setup-docker dev-local dev-docker build up down logs clean db-dump db-restore sync-db

# Aide
help:
	@echo "$(GREEN)FreelansSign - Commandes disponibles:$(NC)"
	@echo ""
	@echo "$(YELLOW)Configuration:$(NC)"
	@echo "  setup-local    - Configuration pour développement local"
	@echo "  setup-docker   - Configuration pour développement Docker"
	@echo ""
	@echo "$(YELLOW)Développement:$(NC)"
	@echo "  dev-local      - Lancer en mode développement local"
	@echo "  dev-docker     - Lancer en mode développement Docker"
	@echo "  build          - Construire les images Docker"
	@echo "  up             - Démarrer les services Docker"
	@echo "  down           - Arrêter les services Docker"
	@echo "  logs           - Voir les logs des services"
	@echo ""
	@echo "$(YELLOW)Base de données:$(NC)"
	@echo "  db-dump        - Créer un dump de la base Docker"
	@echo "  db-restore     - Restaurer un dump (usage: make db-restore DUMP=fichier.sql)"
	@echo "  sync-db        - Synchroniser les bases local <-> Docker"
	@echo ""
	@echo "$(YELLOW)Utilitaires:$(NC)"
	@echo "  clean          - Nettoyer les conteneurs et volumes"


# Configuration clean
setup-clean:
	@echo "$(GREEN)Configuration clean...$(NC)"
	@cp environment/.env.example .env 2>/dev/null || echo "Fichier .env.example non trouvé"
	@echo "$(GREEN)Configuration clean terminée!$(NC)"

# Configuration locale
setup-local:
	@echo "$(GREEN)Configuration pour développement local...$(NC)"
	@cp environment/.env.local .env 2>/dev/null || echo "Fichier .env.local non trouvé"
	@mkdir -p database/dumps database/init scripts
	@chmod +x scripts/*.sh 2>/dev/null || true
	@echo "$(GREEN)Configuration locale terminée!$(NC)"

# Configuration Docker
setup-docker:
	@echo "$(GREEN)Configuration pour développement Docker...$(NC)"
	@cp environment/.env.docker.local.example .env 2>/dev/null || echo "Fichier .env.docker.local.example non trouvé"
	@mkdir -p database/dumps database/init scripts
	@chmod +x scripts/*.sh 2>/dev/null || true
	@echo "$(GREEN)Configuration Docker terminée!$(NC)"

# Configuration Prod Docker
setup-prod:
	@echo "$(GREEN)Configuration pour production Docker...$(NC)"
	@cp environment/.env.prod.example .env 2>/dev/null || echo "Fichier .env.prod.example non trouvé"
	@mkdir -p database/dumps database/init scripts
	@chmod +x scripts/*.sh 2>/dev/null || true
	@echo "$(GREEN)Configuration Prod Docker terminée!$(NC)"

# Développement local (sans Docker)
dev-local: setup-local
	@echo "$(GREEN)Démarrage en mode développement local...$(NC)"
	@echo "$(YELLOW)Assurez-vous que PostgreSQL est démarré localement$(NC)"
	@echo "Backend: cd backend && python manage.py runserver"
	@echo "Frontend: cd frontend && npm run dev"

# Développement Docker
dev-docker: setup-docker build up
	@echo "$(GREEN)Mode développement Docker démarré!$(NC)"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"

# Production Docker
prod-build:
	@echo "$(GREEN)Construction des images Docker pour la production...$(NC)"
	@docker compose -f docker-compose.prod.yml build

prod-up:
	@echo "$(GREEN)Démarrage des services en production...$(NC)"
	@docker compose -f docker-compose.prod.yml up -d
	@echo "$(GREEN)Services de production démarrés sur http://localhost$(NC)"

prod-down:
	@echo "$(YELLOW)Arrêt des services de production...$(NC)"
	@docker compose -f docker-compose.prod.yml down

# Construction des images
build:
	@echo "$(GREEN)Construction des images Docker...$(NC)"
	@$(DOCKER_COMPOSE) --env-file $(ENV_FILE) build

# Démarrage des services
up:
	@echo "$(GREEN)Démarrage des services...$(NC)"
	@$(DOCKER_COMPOSE) --env-file $(ENV_FILE) up -d
	@echo "$(GREEN)Services démarrés!$(NC)"

# Arrêt des services
down:
	@echo "$(YELLOW)Arrêt des services...$(NC)"
	@$(DOCKER_COMPOSE) down

# Logs des services
logs:
	@$(DOCKER_COMPOSE) logs -f

# Logs d'un service spécifique
logs-backend:
	@$(DOCKER_COMPOSE) logs -f backend

logs-frontend:
	@$(DOCKER_COMPOSE) logs -f frontend

logs-postgres:
	@$(DOCKER_COMPOSE) logs -f postgres

# Dump de la base de données
db-dump:
	@echo "$(GREEN)Création du dump de la base de données...$(NC)"
	@./scripts/db-dump.sh docker

# Restauration de la base de données
db-restore:
ifndef DUMP
	@echo "$(RED)Usage: make db-restore DUMP=fichier.sql$(NC)"
	@echo "$(YELLOW)Dumps disponibles:$(NC)"
	@ls -la database/dumps/*.sql 2>/dev/null || echo "Aucun dump trouvé"
else
	@echo "$(GREEN)Restauration de la base depuis $(DUMP)...$(NC)"
	@./scripts/db-restore.sh $(DUMP) docker
endif

# Synchronisation des bases de données
sync-db:
	@echo "$(GREEN)Synchronisation des bases de données...$(NC)"
	@./scripts/sync-db.sh

# Accès au shell Django
shell:
	@$(DOCKER_COMPOSE) exec backend python manage.py shell

# Migrations Django
migrate:
	@$(DOCKER_COMPOSE) exec backend python manage.py migrate

# Collecte des fichiers statiques
collectstatic:
	@$(DOCKER_COMPOSE) exec backend python manage.py collectstatic --noinput

# Nettoyage
clean:
	@echo "$(YELLOW)Nettoyage des conteneurs et images...$(NC)"
	@$(DOCKER_COMPOSE) down -v --remove-orphans
	@docker system prune -f
	@echo "$(GREEN)Nettoyage terminé!$(NC)"

# Nettoyage complet (avec volumes)
clean-all: clean
	@echo "$(YELLOW)Suppression des volumes...$(NC)"
	@docker volume prune -f
	@echo "$(GREEN)Nettoyage complet terminé!$(NC)"

# Redémarrage des services
restart: down up

# Status des services
status:
	@$(DOCKER_COMPOSE) ps
