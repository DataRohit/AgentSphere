# ===== AgentSphere Docker Development Makefile =====
# Compatible with Windows Git Bash and Linux

# Colors
YELLOW := \033[1;33m
GREEN := \033[1;32m
BLUE := \033[1;34m
RED := \033[1;31m
PURPLE := \033[1;35m
CYAN := \033[1;36m
NC := \033[0m # No Color

# Help Command
.PHONY: help
help:
	@echo -e "$(YELLOW)===== AgentSphere Docker Development Commands =====$(NC)"
	@echo -e "$(GREEN)make help$(NC)              - \xF0\x9F\x94\x8D Show this help message"
	@echo -e "$(GREEN)make up$(NC)                - \xF0\x9F\x9A\x80 Start all containers"
	@echo -e "$(GREEN)make down$(NC)              - \xF0\x9F\x9B\x91 Stop all containers"
	@echo -e "$(GREEN)make infra-up$(NC)          - \xF0\x9F\x8F\x97  Start infrastructure services only"
	@echo -e "$(GREEN)make app-up$(NC)            - \xF0\x9F\x93\xB1 Start application services only"
	@echo -e "$(GREEN)make ps$(NC)                - \xF0\x9F\x93\x8B List running containers"
	@echo -e "$(GREEN)make logs$(NC)              - \xF0\x9F\x93\x9C View logs from all containers"
	@echo -e "$(GREEN)make logs-app$(NC)          - \xF0\x9F\x93\x9C View logs from application containers"
	@echo -e "$(GREEN)make logs-infra$(NC)        - \xF0\x9F\x93\x9C View logs from infrastructure containers"
	@echo -e "$(GREEN)make build$(NC)             - \xF0\x9F\x94\xA8 Build all containers"
	@echo -e "$(GREEN)make clean$(NC)             - \xF0\x9F\xA7\xB9 Remove all containers, networks, and volumes"
	@echo -e "$(GREEN)make restart$(NC)           - \xF0\x9F\x94\x84 Restart all containers"
	@echo -e "$(GREEN)make restart-app$(NC)       - \xF0\x9F\x94\x84 Restart application containers"
	@echo -e "$(GREEN)make restart-infra$(NC)     - \xF0\x9F\x94\x84 Restart infrastructure containers"

# Docker Commands
.PHONY: up down ps logs build clean restart restart-app restart-infra

# Infrastructure Services
INFRA_SERVICES := postgres-service pgadmin-service vault-service minio-service dicebear-service redis-service mailpit-service

# Application Services
APP_SERVICES := django-service nginx-service celery-worker-service celery-beat-service celery-flower-service

# Start all containers
up:
	@echo -e "$(BLUE)\xF0\x9F\x9A\x80 Starting all containers...$(NC)"
	docker-compose up -d
	@echo -e "$(GREEN)[OK] All containers started!$(NC)"

# Stop all containers
down:
	@echo -e "$(RED)\xF0\x9F\x9B\x91 Stopping all containers...$(NC)"
	docker-compose down
	@echo -e "$(GREEN)[OK] All containers stopped!$(NC)"

# Start infrastructure services only
infra-up:
	@echo -e "$(BLUE)\xF0\x9F\x8F\x97  Starting infrastructure services...$(NC)"
	docker-compose up -d $(INFRA_SERVICES)
	@echo -e "$(GREEN)[OK] Infrastructure services started!$(NC)"

# Start application services only
app-up:
	@echo -e "$(BLUE)\xF0\x9F\x93\xB1 Starting application services...$(NC)"
	docker-compose up -d $(APP_SERVICES)
	@echo -e "$(GREEN)[OK] Application services started!$(NC)"

# List running containers
ps:
	@echo -e "$(CYAN)\xF0\x9F\x93\x8B Listing running containers...$(NC)"
	docker-compose ps

# View logs from all containers
logs:
	@echo -e "$(CYAN)\xF0\x9F\x93\x9C Viewing logs from all containers...$(NC)"
	docker-compose logs -f

# View logs from application containers
logs-app:
	@echo -e "$(CYAN)\xF0\x9F\x93\x9C Viewing logs from application containers...$(NC)"
	docker-compose logs -f $(APP_SERVICES)

# View logs from infrastructure containers
logs-infra:
	@echo -e "$(CYAN)\xF0\x9F\x93\x9C Viewing logs from infrastructure containers...$(NC)"
	docker-compose logs -f $(INFRA_SERVICES)

# Build all containers
build:
	@echo -e "$(PURPLE)\xF0\x9F\x94\xA8 Building all containers...$(NC)"
	docker-compose build
	@echo -e "$(GREEN)[OK] All containers built!$(NC)"

# Remove all containers, networks, and volumes
clean:
	@echo -e "$(RED)\xF0\x9F\xA7\xB9 Removing all containers, networks, and volumes...$(NC)"
	docker-compose down -v
	@echo -e "$(GREEN)[OK] All containers, networks, and volumes removed!$(NC)"

# Restart all containers
restart:
	@echo -e "$(BLUE)\xF0\x9F\x94\x84 Restarting all containers...$(NC)"
	docker-compose restart
	@echo -e "$(GREEN)[OK] All containers restarted!$(NC)"

# Restart application containers
restart-app:
	@echo -e "$(BLUE)\xF0\x9F\x94\x84 Restarting application containers...$(NC)"
	docker-compose restart $(APP_SERVICES)
	@echo -e "$(GREEN)[OK] Application containers restarted!$(NC)"

# Restart infrastructure containers
restart-infra:
	@echo -e "$(BLUE)\xF0\x9F\x94\x84 Restarting infrastructure containers...$(NC)"
	docker-compose restart $(INFRA_SERVICES)
	@echo -e "$(GREEN)[OK] Infrastructure containers restarted!$(NC)"

