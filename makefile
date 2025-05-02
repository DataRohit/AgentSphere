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
	@echo -e "$(YELLOW)===== Python Code Quality Commands =====$(NC)"
	@echo -e "$(GREEN)make lint-py$(NC)           - \xF0\x9F\x94\x8E Run ruff linter on Python code"
	@echo -e "$(GREEN)make format-py$(NC)         - \xF0\x9F\x92\x85 Format Python code with ruff"
	@echo -e "$(GREEN)make fix-py$(NC)            - \xF0\x9F\x94\xA7 Fix auto-fixable issues with ruff"
	@echo -e "$(YELLOW)===== NextJS Commands =====$(NC)"
	@echo -e "$(GREEN)make nextjs-dev$(NC)        - \xF0\x9F\x9A\x80 Start NextJS development server"
	@echo -e "$(GREEN)make nextjs-build$(NC)      - \xF0\x9F\x94\xA8 Build NextJS application"
	@echo -e "$(GREEN)make nextjs-start$(NC)      - \xF0\x9F\x8F\x81 Start NextJS production server"
	@echo -e "$(GREEN)make nextjs-lint$(NC)       - \xF0\x9F\x94\x8E Run ESLint on NextJS code"

# Docker Commands
.PHONY: up down ps logs build clean restart restart-app restart-infra

# Python Code Quality Commands
.PHONY: lint-py format-py fix-py

# NextJS Commands
.PHONY: nextjs-dev nextjs-build nextjs-start nextjs-lint

# Infrastructure Services
INFRA_SERVICES := postgres-service pgadmin-service vault-service minio-service dicebear-service redis-service mailpit-service

# Application Services
APP_SERVICES := nginx-service django-service celery-worker-service celery-beat-service celery-flower-service

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

# Run ruff linter on Python code
lint-py:
	@echo -e "$(PURPLE)\xF0\x9F\x94\x8E Running ruff linter...$(NC)"
	ruff check .
	@echo -e "$(GREEN)[OK] Linting completed!$(NC)"

# Format Python code with ruff
format-py:
	@echo -e "$(PURPLE)\xF0\x9F\x92\x85 Formatting Python code...$(NC)"
	ruff format .
	@echo -e "$(GREEN)[OK] Formatting completed!$(NC)"

# Fix auto-fixable issues with ruff
fix-py:
	@echo -e "$(PURPLE)\xF0\x9F\x94\xA7 Fixing auto-fixable issues...$(NC)"
	ruff check --fix .
	@echo -e "$(GREEN)[OK] Auto-fixes applied!$(NC)"

# Start NextJS development server
nextjs-dev:
	@echo -e "$(BLUE)\xF0\x9F\x9A\x80 Starting NextJS development server...$(NC)"
	cd frontend && pnpm dev
	@echo -e "$(GREEN)[OK] NextJS development server started!$(NC)"

# Build NextJS application
nextjs-build:
	@echo -e "$(PURPLE)\xF0\x9F\x94\xA8 Building NextJS application...$(NC)"
	cd frontend && pnpm build
	@echo -e "$(GREEN)[OK] NextJS application built!$(NC)"

# Start NextJS production server
nextjs-start:
	@echo -e "$(BLUE)\xF0\x9F\x8F\x81 Starting NextJS production server...$(NC)"
	cd frontend && pnpm start
	@echo -e "$(GREEN)[OK] NextJS production server started!$(NC)"

# Run ESLint on NextJS code
nextjs-lint:
	@echo -e "$(PURPLE)\xF0\x9F\x94\x8E Running ESLint on NextJS code...$(NC)"
	cd frontend && pnpm lint
	@echo -e "$(GREEN)[OK] ESLint completed!$(NC)"
