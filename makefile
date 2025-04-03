# Colors for terminal output
BLUE := \e[1;34m
GREEN := \e[1;32m
RED := \e[1;31m
YELLOW := \e[1;33m
NC := \e[0m # No Color

# Docker Compose commands
.PHONY: up down build rebuild clean clean-all lint logs restart status help

# Start all containers
up:
	@echo -e "$(BLUE)Starting containers...$(NC)"
	@docker-compose up -d
	@echo -e "$(GREEN)Containers are up and running!$(NC)"

# Stop all containers
down:
	@echo -e "$(BLUE)Stopping containers...$(NC)"
	@docker-compose down
	@echo -e "$(GREEN)Containers stopped successfully!$(NC)"

# Build containers
build:
	@echo -e "$(BLUE)Building containers...$(NC)"
	@docker-compose build
	@echo -e "$(GREEN)Build completed successfully!$(NC)"

# Rebuild containers
rebuild:
	@echo -e "$(BLUE)Rebuilding containers...$(NC)"
	@docker-compose build --no-cache
	@echo -e "$(GREEN)Rebuild completed successfully!$(NC)"

# Clean up containers and volumes
clean:
	@echo -e "$(BLUE)Cleaning up containers and volumes...$(NC)"
	@docker-compose down -v
	@echo -e "$(GREEN)Cleanup completed successfully!$(NC)"

# Deep clean - remove all Docker resources
clean-all:
	@echo -e "$(RED)⚠️  Performing deep cleanup...$(NC)"
	@echo -e "$(YELLOW)Stopping all containers...$(NC)"
	@docker-compose down -v
	@echo -e "$(YELLOW)Removing all containers...$(NC)"
	@docker rm -f $$(docker ps -aq) 2>/dev/null || true
	@echo -e "$(YELLOW)Removing all images...$(NC)"
	@docker rmi -f $$(docker images -aq) 2>/dev/null || true
	@echo -e "$(YELLOW)Removing all volumes...$(NC)"
	@docker volume rm $$(docker volume ls -q) 2>/dev/null || true
	@echo -e "$(YELLOW)Removing all networks...$(NC)"
	@docker network prune -f
	@echo -e "$(YELLOW)Removing all build cache...$(NC)"
	@docker builder prune -f
	@echo -e "$(GREEN)Deep cleanup completed successfully!$(NC)"

# Run linting checks
lint:
	@echo -e "$(BLUE)Running linting checks...$(NC)"
	@docker-compose run --rm django-service ruff check .
	@echo -e "$(GREEN)Linting completed!$(NC)"

# Show logs
logs:
	@echo -e "$(BLUE)Showing logs...$(NC)"
	@docker-compose logs -f

# Restart all services
restart:
	@echo -e "$(BLUE)Restarting all services...$(NC)"
	@docker-compose restart
	@echo -e "$(GREEN)Services restarted successfully!$(NC)"

# Show status of containers
status:
	@echo -e "$(BLUE)Container status:$(NC)"
	@docker-compose ps

# Help command
help:
	@echo -e "$(BLUE)Available commands:$(NC)"
	@echo -e "$(GREEN)make up$(NC)         - Start all containers"
	@echo -e "$(GREEN)make down$(NC)       - Stop all containers"
	@echo -e "$(GREEN)make build$(NC)      - Build containers"
	@echo -e "$(GREEN)make rebuild$(NC)    - Rebuild containers without cache"
	@echo -e "$(GREEN)make clean$(NC)      - Clean up containers and volumes"
	@echo -e "$(GREEN)make clean-all$(NC)  - Deep clean all Docker resources"
	@echo -e "$(GREEN)make lint$(NC)       - Run linting checks"
	@echo -e "$(GREEN)make logs$(NC)       - Show container logs"
	@echo -e "$(GREEN)make restart$(NC)    - Restart all services"
	@echo -e "$(GREEN)make status$(NC)     - Show container status"
	@echo -e "$(GREEN)make help$(NC)       - Show this help message"
